#!/usr/bin/env python3
"""
generate_all.py — BestDateWeather
==================================
Source de vérité : data/destinations.csv + data/climate.csv + data/cards.csv + data/overrides.csv
Génère toutes les fiches FR (annuelles + mensuelles).

Usage :
  python3 generate_all.py                  # tout régénérer
  python3 generate_all.py agadir           # une destination
  python3 generate_all.py --validate-only  # vérification sans écriture
  python3 generate_all.py --dry-run        # simulation sans écriture

Workflow de modification :
  1. Ouvrir data/climate.csv ou data/destinations.csv dans Excel
  2. Modifier → Sauvegarder
  3. python3 generate_all.py
  → Toutes les fiches concernées sont régénérées automatiquement.
"""

import csv, re, os, sys, json
from datetime import date
from lib.common import (score_badge, best_months, budget_tier,
                        seasonal_stats, bar_chart, climate_table_html,
                        weather_emoji, LANG_FR)

# ── CHEMINS ─────────────────────────────────────────────────────────────────
DIR = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(DIR, 'data')
OUT  = DIR  # fichiers HTML générés dans le même dossier

# ── CONSTANTES ───────────────────────────────────────────────────────────────
MONTHS_FR  = ['Janvier','Février','Mars','Avril','Mai','Juin',
               'Juillet','Août','Septembre','Octobre','Novembre','Décembre']
MONTH_URL  = ['janvier','fevrier','mars','avril','mai','juin',
               'juillet','aout','septembre','octobre','novembre','decembre']
MONTH_ABBR = ['Jan','Fév','Mar','Avr','Mai','Jun','Jul','Aoû','Sep','Oct','Nov','Déc']
MONTH_URL_EN = ['january','february','march','april','may','june',
                'july','august','september','october','november','december']
SEASONS    = {
    0:'Hiver',1:'Hiver',2:'Printemps',3:'Printemps',4:'Printemps',
    5:'Été',6:'Été',7:'Été',8:'Automne',9:'Automne',10:'Automne',11:'Hiver'
}
SEASON_ICONS = {'Printemps':'🌸','Été':'☀️','Automne':'🍂','Hiver':'❄️'}
TODAY = date.today().strftime('%Y-%m-%d')
YEAR  = date.today().year

# ── SIMILARITÉ & CROSS-LINKING ──────────────────────────────────────────────

COMPARISON_PAIRS = [
    ('nice','barcelone'),('algarve','canaries'),('crete','sardaigne'),
    ('sicile','crete'),('majorque','sardaigne'),('corse','sardaigne'),
    ('malte','sicile'),('dubrovnik','split'),('cote-azur','costa-brava'),
    ('mykonos','santorin'),('ibiza','majorque'),('lisbonne','porto'),
    ('barcelone','lisbonne'),('algarve','cote-azur'),('marrakech','fes'),
    ('marrakech','agadir'),('dubai','abu-dhabi'),('bali','phuket'),
    ('koh-samui','koh-lanta'),('chiang-mai','bangkok'),('bali','sri-lanka'),
    ('langkawi','phuket'),('maldives','seychelles'),('ile-maurice','reunion'),
    ('maldives','zanzibar'),('guadeloupe','martinique'),
    ('republique-dominicaine','jamaique'),('cancun','riviera-maya'),
    ('costa-rica','colombie'),('bali','republique-dominicaine'),
    ('tenerife','madere'),('canaries','madere'),('fuerteventura','gran-canaria'),
]

def build_comparison_index():
    """Build reverse index: slug → [(other_slug, filename)]."""
    idx = {}
    for a, b in COMPARISON_PAIRS:
        idx.setdefault(a, []).append((b, f"{a}-ou-{b}-climat.html"))
        idx.setdefault(b, []).append((a, f"{a}-ou-{b}-climat.html"))
    return idx

def build_pillar_link_month_fr(mi):
    """Build single pillar link card for a monthly page."""
    mname = MONTHS_FR[mi].lower()
    return (f'<a href="ou-partir-en-{MONTH_URL[mi]}.html" style="flex:1;min-width:170px;'
            f'padding:14px 16px;background:white;border:1.5px solid #e8e0d0;border-radius:12px;'
            f'text-decoration:none;font-size:14px;font-weight:600;color:var(--navy)">'
            f'📅 Où partir en {mname} — top 25</a>')

def build_comparison_links_fr(slug, comp_index, all_dests):
    """Build comparison page section for a destination."""
    comps = comp_index.get(slug, [])
    if not comps:
        return ''
    nom = all_dests.get(slug, {}).get('nom_bare', slug)
    cards = ''
    for other_slug, filename in comps[:3]:
        other_nom = all_dests.get(other_slug, {}).get('nom_bare', other_slug)
        cards += (f'<a href="{filename}" style="flex:1;min-width:180px;'
                  f'padding:14px 16px;background:white;border:1.5px solid #e8e0d0;border-radius:12px;'
                  f'text-decoration:none;font-size:14px;font-weight:600;color:var(--navy)">'
                  f'⚖️ {nom} ou {other_nom} ?</a>')
    return (f'<section class="section">\n'
            f' <div class="section-label">Comparatifs météo</div>\n'
            f' <h2 class="section-title">Comparer {nom} avec d\'autres destinations</h2>\n'
            f' <div style="display:flex;gap:14px;flex-wrap:wrap">{cards}</div>\n'
            f'</section>')

def compute_all_similarities(dests, climate):
    """Pré-calcule les 3 destinations les plus similaires pour chaque slug."""
    profiles = {}
    for slug, d in dests.items():
        if slug not in climate or any(m is None for m in climate[slug]):
            continue
        months = climate[slug]
        profiles[slug] = {
            'scores': [m['score'] for m in months],
            'tmaxs':  [m['tmax'] for m in months],
        }

    similarities = {}  # {slug: [(score, other_slug), ...]}
    for slug, p in profiles.items():
        sims = []
        for other_slug, op in profiles.items():
            if other_slug == slug:
                continue
            # Month-by-month profile similarity
            score_diff = sum(abs(p['scores'][i] - op['scores'][i]) for i in range(12)) / 12
            temp_diff  = sum(abs(p['tmaxs'][i]  - op['tmaxs'][i])  for i in range(12)) / 12
            # Best months overlap
            best_a = set(i for i in range(12) if p['scores'][i] >= max(p['scores']) - 1)
            best_b = set(i for i in range(12) if op['scores'][i] >= max(op['scores']) - 1)
            overlap = len(best_a & best_b) / max(len(best_a | best_b), 1)
            sim = (1.0 - (score_diff / 5 + temp_diff / 15) / 2) * 0.6 + overlap * 0.4
            sims.append((max(0, min(1, sim)), other_slug))
        sims.sort(reverse=True)
        similarities[slug] = sims[:3]
    return similarities

def context_paragraph_fr(nom_bare, prep, m, mi, score, best_month, best_score, is_tropical, event_text=None):
    """Génère un paragraphe contextuel unique par destination × mois."""
    month_fr = MONTHS_FR[mi]
    # Déterminer le contexte saisonnier
    season = SEASONS[mi]
    tmax, rain, sun = m['tmax'], m['rain_pct'], m['sun_h']
    
    parts = []
    
    # Événement local si disponible — phrase d'accroche unique
    if event_text:
        parts.append(f"<strong>🎯 {event_text}</strong>")
    
    # Ouverture contextuelle — basée sur la saison locale
    if is_tropical and rain >= 50:
        parts.append(f"{month_fr} correspond à la saison humide {prep} {nom_bare}. Les averses, souvent brèves mais intenses, rythment les journées.")
    elif is_tropical and rain <= 20:
        parts.append(f"{month_fr} tombe en pleine saison sèche {prep} {nom_bare}. L'air est chaud et l'humidité plus supportable qu'en saison des pluies.")
    elif season == 'Été' and tmax >= 30:
        parts.append(f"En plein été, {nom_bare} connaît des températures élevées ({tmax}°C). La chaleur est un facteur à prendre en compte pour les activités en extérieur.")
    elif season == 'Été' and tmax >= 22:
        parts.append(f"L'été {prep} {nom_bare} offre des températures agréables ({tmax}°C) et de longues journées ensoleillées ({sun}h de soleil).")
    elif season == 'Hiver' and tmax <= 10:
        parts.append(f"L'hiver {prep} {nom_bare} est frais ({tmax}°C en journée). Les journées sont courtes ({sun}h de soleil) mais la ville se découvre sous un autre angle.")
    elif season == 'Hiver' and tmax >= 20:
        parts.append(f"Même en hiver, {nom_bare} affiche {tmax}°C. Un atout pour ceux qui fuient le froid européen.")
    elif season == 'Printemps':
        parts.append(f"Le printemps marque le début de la bonne saison {prep} {nom_bare}. Les températures remontent ({tmax}°C) et les touristes ne sont pas encore là en masse.")
    elif season == 'Automne' and score >= 7:
        parts.append(f"L'automne {prep} {nom_bare} est souvent sous-estimé : {tmax}°C, lumière dorée et affluence en baisse. Une fenêtre intéressante.")
    elif season == 'Automne':
        parts.append(f"L'automne marque la fin de la haute saison {prep} {nom_bare}. Les températures baissent ({tmax}°C) et la pluie revient ({rain}% des jours).")
    else:
        parts.append(f"En {month_fr.lower()}, {nom_bare} affiche {tmax}°C en journée avec {sun}h de soleil par jour.")

    # Détail pluie
    if rain <= 10:
        parts.append(f"La pluie est quasi absente ({rain}% des jours) — idéal pour planifier sans plan B.")
    elif rain <= 25:
        parts.append(f"Le risque de pluie reste faible ({rain}% des jours), ce qui laisse une bonne marge pour les activités extérieures.")
    elif rain <= 45:
        parts.append(f"Comptez {rain}% de jours avec pluie — un imperméable léger dans le sac est recommandé.")
    else:
        parts.append(f"Avec {rain}% de jours pluvieux, prévoyez systématiquement des alternatives couvertes.")

    # Positionnement vs meilleur mois
    if score >= 9:
        parts.append(f"C'est l'un des meilleurs moments de l'année pour visiter {nom_bare}.")
    elif score >= 7.5:
        parts.append(f"Un bon compromis entre météo et affluence, même si {best_month.lower()} ({best_score:.1f}/10) reste théoriquement meilleur.")
    elif score >= 5.5:
        parts.append(f"Pas le meilleur créneau, mais acceptable pour qui a des contraintes de dates. {best_month} ({best_score:.1f}/10) est nettement préférable si possible.")
    # score < 5.5 → déjà couvert par le verdict, on n'en rajoute pas

    return ' '.join(parts)

# ── CHARGEMENT DES DONNÉES ───────────────────────────────────────────────────

def load_data(target_slug=None):
    """Charge et retourne (destinations, climate, cards, overrides)."""

    # destinations.csv
    dests = {}
    for row in csv.DictReader(open(f'{DATA}/destinations.csv', encoding='utf-8-sig')):
        dests[row['slug_fr']] = row

    # climate.csv
    climate = {}  # {slug: [month_dict × 12]}
    for row in csv.DictReader(open(f'{DATA}/climate.csv', encoding='utf-8-sig')):
        slug = row['slug']
        if slug not in climate:
            climate[slug] = [None] * 12
        mi = int(row['mois_num']) - 1
        climate[slug][mi] = {
            'mois'    : row['mois'],
            'tmin'    : int(row['tmin']),
            'tmax'    : int(row['tmax']),
            'rain_pct': int(row['rain_pct']),
            'precip'  : float(row['precip_mm']),
            'sun_h'   : float(row['sun_h']),
            'score'   : float(row['score']),
            'classe'  : row['classe'],
        }

    # cards.csv
    cards = {}  # {slug: [card_dict]}
    for row in csv.DictReader(open(f'{DATA}/cards.csv', encoding='utf-8-sig')):
        slug = row['slug']
        cards.setdefault(slug, []).append(row)

    # overrides.csv
    overrides = {}  # {(slug, mi, champ): valeur}
    for row in csv.DictReader(open(f'{DATA}/overrides.csv', encoding='utf-8-sig')):
        key = (row['slug'], int(row['mois_num']) - 1, row['champ'])
        overrides[key] = row['valeur']

    # Apply overrides
    for (slug, mi, champ), val in overrides.items():
        if slug in climate and climate[slug][mi]:
            try:
                if champ in ('tmin','tmax','rain_pct'):
                    climate[slug][mi][champ] = int(val)
                elif champ in ('precip','sun_h','score'):
                    climate[slug][mi][champ] = float(val)
                else:
                    climate[slug][mi][champ] = val
            except ValueError:
                print(f"[WARN] Override invalide: {slug}/{mi}/{champ}={val}")

    # events.csv — contexte local par destination × mois
    events = {}  # {(slug, month_num): event_text}
    events_path = f'{DATA}/events.csv'
    if os.path.exists(events_path):
        for row in csv.DictReader(open(events_path, encoding='utf-8-sig')):
            events[(row['slug'], int(row['month']))] = {
                'fr': row['event_fr'],
                'en': row['event_en'],
            }

    return dests, climate, cards, overrides, events


# ── VALIDATION (mini-SSOT checks) ────────────────────────────────────────────

def validate(dests, climate, cards):
    """Valide la cohérence des données. Retourne liste d'erreurs."""
    errors = []

    for slug, months in climate.items():
        if None in months:
            missing = [MONTHS_FR[i] for i, m in enumerate(months) if m is None]
            errors.append(f"[P0] {slug}: mois manquants: {missing}")
            continue

        scores = [m['score'] for m in months]

        # Score scale
        for i, m in enumerate(months):
            if m['score'] > 10.0 or m['score'] < 0:
                errors.append(f"[P0] {slug}/{MONTHS_FR[i]}: score hors échelle ({m['score']})")

        # tmin <= tmax
        for i, m in enumerate(months):
            if m['tmin'] > m['tmax']:
                errors.append(f"[P0] {slug}/{MONTHS_FR[i]}: tmin({m['tmin']}) > tmax({m['tmax']})")

        # rain_pct 0-100
        for i, m in enumerate(months):
            if not (0 <= m['rain_pct'] <= 100):
                errors.append(f"[P1] {slug}/{MONTHS_FR[i]}: rain_pct hors [0,100] ({m['rain_pct']})")

    for slug in dests:
        if slug not in climate:
            errors.append(f"[P0] {slug}: aucune donnée climatique")

    return errors


# ── CALCULS DÉRIVÉS ──────────────────────────────────────────────────────────

# best_months, budget_tier, score_badge, seasonal_stats, bar_chart
# → imported from lib.common (default L=LANG_FR)


# ── TEMPLATES HTML ───────────────────────────────────────────────────────────

COMMON_HEAD_CSS = '''<link rel="stylesheet" href="style.css"/>
<link rel="icon" type="image/x-icon" href="favicon.ico"/>
<link rel="apple-touch-icon" sizes="180x180" href="apple-touch-icon.png"/>
<meta name="theme-color" content="#1a1f2e"/>'''

GTAG = '''<script async src="https://www.googletagmanager.com/gtag/js?id=G-NTCJTDPSJL"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}gtag("js",new Date());gtag("config","G-NTCJTDPSJL");</script>'''

NAV = '''<nav>
 <a class="nav-brand" href="index.html">Best<em>Date</em>Weather</a>
 <div class="nav-actions">
  <button class="nav-share" onclick="shareThis()" aria-label="Partager"><svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><path d="M8.59 13.51l6.83 3.98M15.41 6.51l-6.82 3.98"/></svg></button>
  <a class="nav-cta" href="index.html">Tester l'application</a>
 </div>
</nav>'''

def footer_html(slug_fr, nom_bare, prep, slug_en=None):
    en_link = ''
    if slug_en:
        en_link = f''' · <a href="en/best-time-to-visit-{slug_en}.html" style="color:rgba(255,255,255,.7)"><img src="flags/gb.png" width="20" height="15" alt="" style="vertical-align:middle;border-radius:2px"> English</a>'''
    return f'''<footer>
 <p style="color:rgba(255,255,255,.7);font-size:13px;font-weight:700;margin-bottom:8px">bestdateweather.com</p>
 <p><a href="https://open-meteo.com/" rel="noopener" style="color:rgba(255,255,255,.7)">Données météo par Open-Meteo.com</a> · Sources ECMWF, DWD, NOAA, Météo-France · CC BY 4.0</p>
 <p style="margin-top:8px"><a href="methodologie.html" style="color:rgba(255,255,255,.7)">Méthodologie</a> · <a href="index.html" style="color:rgba(255,255,255,.7)">Application météo</a>{en_link}</p>
 <p style="margin-top:8px;font-size:11px;opacity:.6"><a href="mentions-legales.html" style="color:rgba(255,255,255,.7)">Mentions légales</a> · <a href="confidentialite.html" style="color:rgba(255,255,255,.7)">Confidentialité</a> · <a href="contact.html" style="color:rgba(255,255,255,.7)">Contact</a></p>
</footer>
<script>function shareThis(){{if(navigator.share)navigator.share({{title:document.title,url:location.href}});else{{navigator.clipboard.writeText(location.href);var b=document.querySelector('.nav-share');b.style.color='#27ae60';setTimeout(function(){{b.style.color=''}},1200)}}}}</script>'''

# climate_table_html → imported from lib.common (default L=LANG_FR)


# ── GÉNÉRATEUR FICHE ANNUELLE ────────────────────────────────────────────────

def gen_annual(dest, months, dest_cards, all_dests, similarities, comparison_index=None):
    slug       = dest['slug_fr']
    slug_en    = dest['slug_en']
    nom_fr     = dest['nom_fr']
    nom_bare   = dest['nom_bare']
    prep       = dest['prep']
    pays       = dest['pays']
    flag       = dest['flag']
    lat        = float(dest['lat'])
    lon        = float(dest['lon'])
    hero_sub   = dest['hero_sub'] or f"{nom_bare}, une destination à découvrir selon la météo."
    booking_id = dest['booking_dest_id']

    bests      = best_months(months)
    best_str   = ' & '.join(bests[:2]) if len(bests) >= 2 else bests[0]
    best_score = max(m['score'] for m in months)
    best_idx   = next(i for i, m in enumerate(months) if m['score'] == best_score)
    best_m     = months[best_idx]
    seas       = seasonal_stats(months)
    all_scores = [m['score'] for m in months]

    # best period rain/temp
    best_rain  = best_m['rain_pct']
    best_tmax  = best_m['tmax']

    # Meta — 3 patterns de title + description
    title_var = hash(slug) % 3
    if title_var == 0:
        title = f"Meilleure période pour partir {prep} {nom_bare} [{YEAR}] — Météo & conseils"
        h1_text = f"Meilleure période pour partir<br/><em>{prep} {nom_bare}</em>"
    elif title_var == 1:
        title = f"Quand partir {prep} {nom_bare} ? Climat mois par mois [{YEAR}]"
        h1_text = f"Quand partir<br/><em>{prep} {nom_bare}</em> ?"
    else:
        title = f"{nom_bare} : meilleure saison pour voyager [{YEAR}] — Climat & météo"
        h1_text = f"<em>{nom_bare}</em><br/>quelle saison choisir ?"

    desc_var = hash(slug + 'desc') % 3
    if desc_var == 0:
        desc = (f"Quelle est la meilleure période pour visiter {nom_bare} ? "
                f"{MONTHS_FR[best_idx]} offre {best_tmax}°C et {best_rain}% de jours pluvieux. "
                f"Score météo : {best_score}/10. Données 10 ans Open-Meteo.")
    elif desc_var == 1:
        desc = (f"Quand partir {prep} {nom_bare} ? {MONTHS_FR[best_idx]} est le meilleur mois "
                f"({best_score}/10) avec {best_tmax}°C. Analyse complète des 12 mois sur 10 ans de données.")
    else:
        desc = (f"{nom_bare} en {MONTHS_FR[best_idx].lower()} : {best_tmax}°C, {best_rain}% de pluie, "
                f"score {best_score}/10. Découvrez le meilleur moment pour partir — données météo 10 ans.")

    # Climate table
    is_mountain = dest.get('mountain', 'False').strip() == 'True'
    table_html = climate_table_html(months, nom_bare, is_mountain)

    # Quick facts section
    worst_idx  = min(range(12), key=lambda i: months[i]['score'])
    worst_rain = months[worst_idx]['rain_pct']
    qf = f'''<section class="section">
 <div class="section-label">Décision en 30 secondes</div>
 <h2 class="section-title">Quand partir {prep} {nom_bare} ?</h2>
 <div class="quick-facts">
 <div class="quick-facts-row"><div class="qf-label">🌞 Meilleure période générale</div><div class="qf-value"><strong>{MONTHS_FR[best_idx]}</strong></div></div>
 <div class="quick-facts-row"><div class="qf-label">🌡️ Température optimale</div><div class="qf-value"><strong>{best_m["tmin"]}–{best_m["tmax"]}°C</strong> en {MONTHS_FR[best_idx].lower()}</div></div>
 <div class="quick-facts-row"><div class="qf-label">🌧 Moins de pluie</div><div class="qf-value"><strong>{best_rain}%</strong> de jours pluvieux en {MONTHS_FR[best_idx].lower()}</div></div>
 <div class="quick-facts-row"><div class="qf-label">🌧 Mois le plus pluvieux</div><div class="qf-value"><strong>{MONTHS_FR[worst_idx]}</strong> ({worst_rain}%)</div></div>
 <div class="quick-facts-row"><div class="qf-label">📅 Meilleur score</div><div class="qf-value"><strong>{best_score}/10</strong></div></div>
 </div>
</section>'''

    # Cards section
    cards_html = '\n'.join(
        f'<div class="project-card"><span class="proj-icon">{c["icon"]}</span>'
        f'<span class="proj-title">{c["titre"]}</span>'
        f'<span class="proj-text">{c["texte"]}</span></div>'
        for c in dest_cards
    )
    cards_section = f'''<section class="section">
 <div class="section-label">Selon votre projet</div>
 <h2 class="section-title">Meilleure période selon votre type de voyage</h2>
 <div class="project-grid">{cards_html}</div>
</section>''' if dest_cards else ''

    # Climate table section
    table_section = f'''<section class="section">
 <div class="section-label">Tableau climatique mensuel</div>
 <h2 class="section-title">Météo {prep} {nom_bare} mois par mois</h2>
 {table_html}
</section>'''

    # Seasonal analysis
    season_rows = ''
    for sname in ['Printemps','Été','Automne','Hiver']:
        s = seas[sname]
        icon = SEASON_ICONS[sname]
        mois_range = {'Printemps':'mars–mai','Été':'juin–août','Automne':'sept–nov','Hiver':'déc–fév'}[sname]
        season_rows += (f'<h3 class="sub-title">{icon} {sname} ({mois_range}) — {s["verdict"]}</h3>'
                        f'<p>Températures moyennes {s["tmax"]}°C, {s["rain_pct"]}% de jours avec pluie, '
                        f'{s["sun_h"]}h de soleil par jour. Score moyen : {s["score"]}/10.</p>\n')
    seasonal_section = f'''<section class="section">
 <div class="section-label">Analyse saison par saison</div>
 <h2 class="section-title">À quoi s'attendre selon la période</h2>
 {season_rows}
</section>'''

    # Booking section
    if booking_id:
        booking_url = (f"https://www.booking.com/searchresults.fr.html?ss={nom_bare}"
                       f"&dest_id={booking_id}&dest_type=city"
                       f"&checkin={YEAR}-{best_idx+1:02d}-01&checkout={YEAR}-{best_idx+1:02d}-07"
                       f"&group_adults=2&no_rooms=1&lang=fr")
        # Conseil budget contextualisé
        off_months = [MONTHS_FR[i].lower() for i in range(12) if months[i]['score'] >= 6.5 and months[i]['score'] < best_score - 1.5]
        if off_months:
            budget_tip = f"Conseil : {', '.join(off_months[:2])} {'offrent' if len(off_months[:2]) > 1 else 'offre'} un bon compromis météo/prix — score correct avec moins d'affluence."
        else:
            budget_tip = f"Conseil : les mois hors pic ({MONTHS_FR[worst_idx].lower()}, {MONTHS_FR[(worst_idx+1)%12].lower()}) sont les moins chers mais la météo est nettement moins favorable."
        booking_section = f'''<section class="section">
 <div class="section-label">Hébergement</div>
 <h2 class="section-title">Trouver un hébergement {prep} {nom_bare}</h2>
 <div class="affil-box">
 <strong>Voir les disponibilités sur la période recommandée</strong>
 <p>{budget_tip}</p>
 <div style="display:flex;gap:12px;flex-wrap:wrap">
 <a class="affil-btn" href="{booking_url}" target="_blank" rel="noopener">Booking.com →</a>
 </div>
 </div>
</section>'''
    else:
        booking_section = ''

    # Monthly nav section — colored by score class
    MONTH_BTN_STYLE = {
        'rec':   'background:#e8f8f0;border:1.5px solid #86efac;',
        'mid':   'background:#fffbeb;border:1.5px solid #fbbf24;',
        'avoid': 'background:#fef2f2;border:1.5px solid #fca5a5;',
    }
    has_monthly = dest.get('monthly', 'True').strip().lower() in ('true', '1', 'yes', '')
    monthly_links = ''.join(
        f'<a href="{slug}-meteo-{MONTH_URL[i]}.html" style="display:block;padding:10px 8px;'
        f'{MONTH_BTN_STYLE.get(months[i]["classe"], MONTH_BTN_STYLE["mid"])}'
        f'border-radius:10px;text-decoration:none;text-align:center">'
        f'<div style="font-weight:700;font-size:13px;color:#1a1f2e">{MONTHS_FR[i]}</div>'
        f'</a>'
        for i in range(12)
    )
    monthly_section = f'''<section class="section">
 <div class="section-label">Météo par mois</div>
 <h2 class="section-title">Météo détaillée mois par mois</h2>
 <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(80px,1fr));gap:8px;margin-bottom:20px">
 {monthly_links}
 </div>
</section>''' if has_monthly else ''

    # FAQ
    if is_mountain:
        from scoring import compute_ski_score
        ski_scores = [(i, compute_ski_score(months[i]['tmax'], months[i]['rain_pct'], months[i]['sun_h'])) for i in range(12)]
        best_ski_idx = max(ski_scores, key=lambda x: x[1])[0]
        best_ski_score = ski_scores[best_ski_idx][1]
        winter_ski_avg = round(sum(ski_scores[i][1] for i in (11, 0, 1)) / 3, 1)
        faq_items = [
            (f"Quelle est la meilleure période pour partir {prep} {nom_bare} ?",
             f"Ça dépend de l'activité. Pour le ski : {MONTHS_FR[best_ski_idx].lower()} "
             f"(score ski {best_ski_score}/10). Pour la randonnée/été : {MONTHS_FR[best_idx].lower()} "
             f"({best_score}/10, {best_tmax}°C)."),
            (f"Peut-on skier {prep} {nom_bare} en hiver ?",
             f"Oui, c'est la pleine saison. Score ski moyen décembre-février : {winter_ski_avg}/10. "
             f"Températures froides ({months[0]['tmax']}°C max en janvier) et neige fréquente."),
            (f"Fait-il chaud {prep} {nom_bare} en été ?",
             f"En {MONTHS_FR[best_idx].lower()}, il fait {best_tmax}°C en moyenne. Idéal pour la randonnée et les activités outdoor."),
            (f"Quel est le mois le plus pluvieux {prep} {nom_bare} ?",
             f"{MONTHS_FR[worst_idx]} est le mois le plus pluvieux avec {worst_rain}% de jours de pluie."),
        ]
    else:
        faq_items = [
            (f"Quelle est la meilleure période pour partir {prep} {nom_bare} ?",
             f"{MONTHS_FR[best_idx]} est idéal avec {best_rain}% de jours pluvieux et {best_tmax}°C. "
             f"{'La période ' + ' & '.join(bests[:2]) + ' offre des conditions comparables.' if len(bests) > 1 else ''}"),
            (f"Quel est le mois le plus pluvieux {prep} {nom_bare} ?",
             f"{MONTHS_FR[worst_idx]} est le mois le plus pluvieux avec {worst_rain}% de jours de pluie."),
            (f"Fait-il chaud {prep} {nom_bare} en {MONTHS_FR[best_idx].lower()} ?",
             f"Oui, {MONTHS_FR[best_idx].lower()} est le meilleur mois avec {best_tmax}°C en moyenne."),
            (f"Peut-on partir {prep} {nom_bare} en hiver ?",
             f"En hiver, le score moyen est {seas['Hiver']['score']}/10. "
             f"{'Conditions acceptables pour les visites culturelles.' if seas['Hiver']['score'] >= 5.5 else 'Période difficile — préférez la haute saison.'}"),
        ]
    faq_html = '<div class="faq-list">' + ''.join(
        f'<div class="faq-item"><button class="faq-q" onclick="toggleFaq(this)">'
        f'{q}<span class="faq-icon">+</span></button>'
        f'<div class="faq-a">{a}</div></div>'
        for q, a in faq_items
    ) + '</div>'

    faq_schema = json.dumps({
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q,
             "acceptedAnswer": {"@type": "Answer", "text": a}}
            for q, a in faq_items
        ]
    }, ensure_ascii=False)

    faq_section = f'''<section class="section">
 <div class="section-label">FAQ</div>
 <h2 class="section-title">Questions fréquentes</h2>
 {faq_html}
</section>'''

    # Cross-linking: destinations similaires
    sim_list = similarities.get(slug, [])
    if sim_list:
        sim_cards = ''
        for sim_score, sim_slug in sim_list[:3]:
            sd = all_dests.get(sim_slug, {})
            sn = sd.get('nom_bare', sim_slug)
            sp = sd.get('prep', 'à')
            sf = sd.get('flag', '')
            sim_cards += (
                f'<a href="meilleure-periode-{sim_slug}.html" style="flex:1;min-width:200px;'
                f'padding:16px;background:white;border:1.5px solid #e8e0d0;border-radius:12px;'
                f'text-decoration:none;display:flex;flex-direction:column;gap:6px">'
                f'<div style="font-size:13px;color:var(--slate3)"><img src="flags/{sf}.png" width="16" height="12" '
                f'alt="{sf}" style="vertical-align:middle;margin-right:4px;border-radius:1px">{sd.get("pays","")}</div>'
                f'<div style="font-weight:700;color:var(--navy)">{sn}</div>'
                f'<div style="font-size:12px;color:var(--slate2)">Climat similaire · {sim_score:.0%} de correspondance</div>'
                f'</a>')
        similar_section = f'''<section class="section">
 <div class="section-label">Explorer aussi</div>
 <h2 class="section-title">Destinations au climat similaire</h2>
 <div style="display:flex;gap:14px;flex-wrap:wrap">{sim_cards}</div>
</section>'''
    else:
        similar_section = ''

    # Ranking pages section
    ranking_section = '''<section class="section">
 <div class="section-label">Classements météo</div>
 <h2 class="section-title">Comparer les destinations par météo</h2>
 <div style="display:flex;gap:14px;flex-wrap:wrap"><a href="classement-destinations-meteo-2026.html" style="flex:1;min-width:170px;padding:14px 16px;background:white;border:1.5px solid #e8e0d0;border-radius:12px;text-decoration:none;font-size:14px;font-weight:600;color:var(--navy)">🌍 Classement mondial 2026</a><a href="classement-destinations-meteo-ete-2026.html" style="flex:1;min-width:170px;padding:14px 16px;background:white;border:1.5px solid #e8e0d0;border-radius:12px;text-decoration:none;font-size:14px;font-weight:600;color:var(--navy)">🌞 Meilleures destinations été</a><a href="classement-destinations-meteo-hiver-2026.html" style="flex:1;min-width:170px;padding:14px 16px;background:white;border:1.5px solid #e8e0d0;border-radius:12px;text-decoration:none;font-size:14px;font-weight:600;color:var(--navy)">🌴 Destinations soleil hiver</a></div>
</section>'''

    # Pillar page + comparison links (reverse maillage)
    pillar_comp_cards = []
    # Pillar for best month
    best_month_slug = MONTH_URL[best_idx]
    best_month_name = MONTHS_FR[best_idx]
    pillar_comp_cards.append(
        f'<a href="ou-partir-en-{best_month_slug}.html" style="flex:1;min-width:180px;'
        f'padding:14px 16px;background:white;border:1.5px solid #e8e0d0;border-radius:12px;'
        f'text-decoration:none;font-size:14px;font-weight:600;color:var(--navy)">'
        f'📅 Où partir en {best_month_name.lower()}</a>')
    # Comparison pages involving this destination
    if comparison_index and slug in comparison_index:
        for other_slug, comp_file in comparison_index[slug][:3]:
            other_nom = all_dests.get(other_slug, {}).get('nom_bare', other_slug)
            pillar_comp_cards.append(
                f'<a href="{comp_file}" style="flex:1;min-width:180px;'
                f'padding:14px 16px;background:white;border:1.5px solid #e8e0d0;border-radius:12px;'
                f'text-decoration:none;font-size:14px;font-weight:600;color:var(--navy)">'
                f'⚖️ {nom_bare} ou {other_nom} ?</a>')
    pillar_comparison_section = f'''<section class="section">
 <div class="section-label">Guides & comparatifs</div>
 <h2 class="section-title">Explorer par mois ou comparer</h2>
 <div style="display:flex;gap:14px;flex-wrap:wrap">{"".join(pillar_comp_cards)}</div>
</section>'''

    # Schema.org Article
    article_schema = json.dumps({
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": f"Meilleure période pour partir {prep} {nom_bare}",
        "description": desc,
        "author": {"@type": "Organization", "name": "BestDateWeather"},
        "publisher": {"@type": "Organization", "name": "BestDateWeather"},
        "dateModified": TODAY,
        "mainEntityOfPage": {
            "@type": "WebPage",
            "@id": f"https://bestdateweather.com/meilleure-periode-{slug}.html"
        }
    }, ensure_ascii=False)

    breadcrumb_schema = json.dumps({
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Accueil", "item": "https://bestdateweather.com/"},
            {"@type": "ListItem", "position": 2, "name": nom_bare, "item": f"https://bestdateweather.com/meilleure-periode-{slug}.html"}
        ]
    }, ensure_ascii=False)

    dataset_schema = json.dumps({
        "@context": "https://schema.org",
        "@type": "Dataset",
        "name": f"Données climatiques de {nom_bare} — moyennes mensuelles sur 10 ans",
        "description": f"Températures, précipitations, ensoleillement et vent mensuels {prep} {nom_bare}. Moyennes calculées sur 10 ans de données ERA5 (Open-Meteo).",
        "temporalCoverage": "2015/2024",
        "spatialCoverage": {"@type": "Place", "name": nom_bare},
        "creator": {"@type": "Organization", "name": "BestDateWeather", "url": "https://bestdateweather.com"},
        "license": "https://creativecommons.org/licenses/by-nc/4.0/",
        "variableMeasured": ["Temperature", "Precipitation", "Sunshine hours", "Wind speed"]
    }, ensure_ascii=False)

    html = f'''<!DOCTYPE html>
<html lang="fr">
<head>
<!-- SCORING: generate_all.py | slug={slug} | tropical={dest["tropical"]} | generated={TODAY} -->
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1.0"/>
{GTAG}
<title>{title}</title>
<meta name="description" content="{desc}"/>
<link rel="canonical" href="https://bestdateweather.com/meilleure-periode-{slug}.html"/>
<link rel="alternate" hreflang="fr" href="https://bestdateweather.com/meilleure-periode-{slug}.html"/>
<link rel="alternate" hreflang="en" href="https://bestdateweather.com/en/best-time-to-visit-{slug_en}.html"/>
<link rel="alternate" hreflang="x-default" href="https://bestdateweather.com/en/best-time-to-visit-{slug_en}.html"/>
<meta property="og:type" content="article"/>
<meta property="og:title" content="Meilleure période {prep} {nom_bare} — météo &amp; conseils"/>
<meta property="og:description" content="{desc}"/>
<meta property="og:url" content="https://bestdateweather.com/meilleure-periode-{slug}.html"/>
<script type="application/ld+json">{article_schema}</script>
<script type="application/ld+json">{faq_schema}</script>
<script type="application/ld+json">{breadcrumb_schema}</script>
<script type="application/ld+json">{dataset_schema}</script>
{COMMON_HEAD_CSS}
<style>
.hero-band{{background:linear-gradient(160deg,#0d1a3a 0%,#1a2a6a 55%,#2a4a9a 100%);}}
.hero-title em{{color:#93c5fd;}}
</style>
</head>
<body><script>window.scrollTo(0,0);</script>
{NAV}
<header class="hero-band">
 <div class="dest-tag"><img src="flags/{flag}.png" width="20" height="15" alt="{flag.upper()}" style="vertical-align:middle;margin-right:4px;border-radius:1px"> {nom_bare}, {pays}</div>
 <h1 class="hero-title">{h1_text}</h1>
 <p class="hero-sub">{hero_sub}</p>
 <div class="kicker">Mis à jour : {MONTHS_FR[date.today().month - 1]} {date.today().year} · Open-Meteo · 10 ans · 12 mois comparés · {lat}°N {abs(lon)}°{"E" if lon >= 0 else "W"}</div>
 <div class="hero-stats" style="margin-top:22px">
 <div><span class="hstat-val">{best_str}</span><span class="hstat-lbl">Meilleur{'s mois' if len(bests) > 1 else ' mois'}</span></div>
 <div><span class="hstat-val">{best_tmax}°C</span><span class="hstat-lbl">Température optimale</span></div>
 <div><span class="hstat-val">{best_rain}%</span><span class="hstat-lbl">Jours pluvieux</span></div>
 </div>
</header>
<main class="page">
{qf}
{cards_section}
{table_section}
{seasonal_section}
{booking_section}
{monthly_section}
{faq_section}
{similar_section}
{ranking_section}
{pillar_comparison_section}
</main>
{footer_html(slug, nom_bare, prep, slug_en)}
<script>
function toggleFaq(btn){{
  const a=btn.nextElementSibling;
  const opening=a.style.display!=="block";
  a.style.display=opening?"block":"none";
  btn.querySelector(".faq-icon").textContent=opening?"-":"+";
  if(opening)setTimeout(function(){{btn.scrollIntoView({{behavior:'smooth',block:'start'}})}},80);
}}
</script>
</body>
</html>'''
    return html


# ── GÉNÉRATEUR FICHE MENSUELLE ───────────────────────────────────────────────

MONTHLY_GRAD = {
    0:'linear-gradient(160deg,#0d1a3a 0%,#1a2a6a 55%,#2a4a9a 100%)',
    1:'linear-gradient(160deg,#0d1a3a 0%,#1a2a6a 55%,#2a4a9a 100%)',
    2:'linear-gradient(160deg,#0a2a1a 0%,#1a4a2a 55%,#3a8a5a 100%)',
    3:'linear-gradient(160deg,#0a2a1a 0%,#1a4a2a 55%,#3a8a5a 100%)',
    4:'linear-gradient(160deg,#0a2a1a 0%,#1a4a2a 55%,#3a8a5a 100%)',
    5:'linear-gradient(160deg,#2a1a0a 0%,#6a3a1a 55%,#d97706 100%)',
    6:'linear-gradient(160deg,#2a1a0a 0%,#6a3a1a 55%,#d97706 100%)',
    7:'linear-gradient(160deg,#2a1a0a 0%,#6a3a1a 55%,#d97706 100%)',
    8:'linear-gradient(160deg,#1a1a0a 0%,#4a3a0a 55%,#8a6a2a 100%)',
    9:'linear-gradient(160deg,#1a1a0a 0%,#4a3a0a 55%,#8a6a2a 100%)',
    10:'linear-gradient(160deg,#1a1a0a 0%,#4a3a0a 55%,#8a6a2a 100%)',
    11:'linear-gradient(160deg,#0d1a3a 0%,#1a2a6a 55%,#2a4a9a 100%)',
}


def _build_sim_cards_fr(sim_list, all_dests, climate_for_sim, mi):
    """Build cross-linking HTML cards for similar destinations."""
    parts = []
    for _, sim_slug in sim_list:
        sd = all_dests.get(sim_slug)
        if not sd:
            continue
        # Skip destinations without monthly pages
        if sd.get('monthly', 'True').strip().lower() not in ('true', '1', 'yes', ''):
            continue
        sc = climate_for_sim.get(sim_slug, {})
        parts.append(
            f'<a href="{sim_slug}-meteo-{MONTH_URL[mi]}.html" style="flex:1;min-width:180px;'
            f'padding:14px;background:white;border:1.5px solid #e8e0d0;border-radius:12px;'
            f'text-decoration:none;display:flex;flex-direction:column;gap:4px">'
            f'<div style="font-weight:700;color:var(--navy);font-size:14px">'
            f'<img src="flags/{sd.get("flag","")}.png" width="16" height="12" '
            f'alt="" style="vertical-align:middle;margin-right:4px;border-radius:1px">'
            f'{sd.get("nom_bare",sim_slug)}</div>'
            f'<div style="font-size:12px;color:var(--slate2)">{MONTHS_FR[mi]} : {sc.get("score","?")}/10 · {sc.get("tmax","?")}°C</div>'
            f'</a>')
    return ''.join(parts)

def _build_comp_cards_monthly_fr(slug, nom_bare, comparison_index, all_dests):
    """Build comparison page link cards for monthly pages."""
    if not comparison_index or slug not in comparison_index:
        return ''
    cards = []
    for other_slug, comp_file in comparison_index[slug][:2]:
        other_nom = all_dests.get(other_slug, {}).get('nom_bare', other_slug)
        cards.append(
            f'<a href="{comp_file}" style="flex:1;min-width:180px;'
            f'padding:14px 16px;background:white;border:1.5px solid #e8e0d0;border-radius:12px;'
            f'text-decoration:none;font-size:14px;font-weight:600;color:var(--navy)">'
            f'⚖️ {nom_bare} ou {other_nom} ?</a>')
    return ''.join(cards)

def gen_monthly(dest, months, mi, all_dests, similarities, all_climate, events=None, comparison_index=None):
    slug     = dest['slug_fr']
    slug_en  = dest['slug_en']
    nom_bare = dest['nom_bare']
    prep     = dest['prep']
    flag     = dest['flag']
    lat      = float(dest['lat'])
    lon      = float(dest['lon'])

    m        = months[mi]
    score    = m['score']
    season   = SEASONS[mi]
    month_fr = MONTHS_FR[mi]
    month_url= MONTH_URL[mi]
    is_mountain = dest.get('mountain', 'False').strip() == 'True'

    all_scores = [mo['score'] for mo in months]
    best_idx   = max(range(12), key=lambda i: months[i]['score'])
    best_month = MONTHS_FR[best_idx]
    best_score = months[best_idx]['score']
    # Effective class: use best_class for mountain destinations
    eff_classe = m['classe']
    if is_mountain:
        from scoring import compute_ski_score, best_class
        ski_sc = compute_ski_score(m['tmax'], m['rain_pct'], m['sun_h'])
        eff_classe = best_class(m['classe'], ski_sc)
    bg, txt, verdict_lbl = score_badge(score, eff_classe)
    bud = budget_tier(score, all_scores)

    # Prev / next
    prev_mi = (mi - 1) % 12
    next_mi = (mi + 1) % 12

    # Activities
    act_city  = '✅ Bon' if score >= 6.5 else '⚠️ Possible'
    act_ext   = '✅ Bon' if score >= 7.5 else ('⚠️ Possible' if score >= 6.0 else '❌ Déconseillé')
    act_beach = ('✅ Bon' if score >= 7.5 and m['tmax'] >= 25
                 else ('⚠️ Possible' if score >= 6.5 and m['tmax'] >= 20 else '❌ Déconseillé'))

    # ── Contexte destination pour diversification ──
    is_tropical = dest.get('tropical', '0') == '1'
    is_hot      = m['tmax'] >= 30
    is_warm     = 22 <= m['tmax'] < 30
    is_mild     = 15 <= m['tmax'] < 22
    is_cold     = m['tmax'] < 15
    is_rainy    = m['rain_pct'] >= 50
    is_dry      = m['rain_pct'] <= 15
    is_sunny    = m['sun_h'] >= 10
    is_winter   = mi in (11, 0, 1)
    is_summer   = mi in (5, 6, 7)
    is_shoulder = mi in (3, 4, 8, 9)
    hash_var    = (hash(slug + str(mi)) % 3)  # pour rotation patterns

    # Hero sub — 9 variantes
    if score >= 8.5:
        hero_opts = [
            f"{month_fr} est l'une des meilleures périodes {prep} {nom_bare}.",
            f"{month_fr} {prep} {nom_bare} : conditions quasi idéales.",
            f"Partir {prep} {nom_bare} en {month_fr.lower()} ? Excellente idée.",
        ]
        hero_sub = hero_opts[hash_var]
    elif score >= 7.0:
        hero_opts = [
            f"{month_fr} est une bonne période. {best_month} est légèrement meilleur.",
            f"{nom_bare} en {month_fr.lower()} : solide, même si {best_month.lower()} reste le pic.",
            f"Bonne fenêtre en {month_fr.lower()} — {best_month.lower()} est un cran au-dessus.",
        ]
        hero_sub = hero_opts[hash_var]
    else:
        hero_opts = [
            f"{month_fr} est difficile — {best_month} offre de bien meilleures conditions.",
            f"Période compliquée en {month_fr.lower()}. Préférez {best_month.lower()} si possible.",
            f"{nom_bare} en {month_fr.lower()} ? Pas la meilleure fenêtre — visez {best_month.lower()}.",
        ]
        hero_sub = hero_opts[hash_var]

    # Verdict text — enrichi avec contexte météo
    if score >= 9.0:
        verdict_opts = [
            f"{month_fr} est une excellente période {prep} {nom_bare}. {m['tmax']}°C, {m['sun_h']}h de soleil — conditions optimales.",
            f"Partir en {month_fr.lower()} {prep} {nom_bare} est un choix sûr : météo au top, {m['rain_pct']}% de risque de pluie seulement.",
            f"{nom_bare} en {month_fr.lower()} coche toutes les cases : chaleur, soleil, peu de pluie.",
        ]
        verdict_txt = verdict_opts[hash_var]
    elif score >= 7.0:
        diff = round(best_score - score, 1)
        verdict_opts = [
            f"{month_fr} est une bonne période {prep} {nom_bare}. {best_month} reste légèrement meilleur (+{diff} pts).",
            f"Conditions favorables en {month_fr.lower()} ({score:.1f}/10). {best_month} fait mieux mais l'écart est faible.",
            f"{nom_bare} en {month_fr.lower()} : {m['tmax']}°C et {m['sun_h']}h de soleil. Correct, sans être le pic.",
        ]
        verdict_txt = verdict_opts[hash_var]
    elif score >= 5.0:
        verdict_opts = [
            f"{month_fr} est une période moyenne {prep} {nom_bare}. {best_month} ({best_score}/10) est nettement préférable.",
            f"Pas la meilleure fenêtre : {m['rain_pct']}% de risque de pluie et {m['sun_h']}h de soleil. {best_month} est bien plus sûr.",
            f"{nom_bare} en {month_fr.lower()} reste possible mais {best_month} offre un score de {best_score}/10 contre {score:.1f}.",
        ]
        verdict_txt = verdict_opts[hash_var]
    else:
        verdict_opts = [
            f"{month_fr} est difficile {prep} {nom_bare}. {best_month} ({best_score}/10) est bien plus favorable.",
            f"Conditions défavorables en {month_fr.lower()} ({score:.1f}/10). Privilégiez {best_month.lower()} si vos dates sont flexibles.",
            f"{nom_bare} en {month_fr.lower()} : {m['rain_pct']}% de pluie, {m['sun_h']}h de soleil. Mieux vaut reporter à {best_month.lower()}.",
        ]
        verdict_txt = verdict_opts[hash_var]

    # Bars
    rain_bar = bar_chart(m['rain_pct'])
    temp_bar = bar_chart(min(m['tmax'], 40), 40)
    sun_bar  = bar_chart(min(m['sun_h'], 14), 14)

    # Oui / Non si — 18+ variantes croisées (score × contexte)
    if score >= 8.0:
        if is_tropical and is_dry:
            oui_si = "profiter de la saison sèche — conditions idéales pour la plage et les excursions."
            non_si = "voyager à petit budget — c'est la haute saison, les prix sont au plus haut."
        elif is_hot and is_sunny:
            oui_si = f"chercher le plein soleil — {m['sun_h']}h par jour en moyenne."
            non_si = "mal supporter la chaleur — les températures dépassent souvent 30°C."
        elif is_warm and is_dry:
            oui_si = f"combiner plage, visites et randonnées — météo polyvalente ({m['tmax']}°C, peu de pluie)."
            non_si = "éviter l'affluence touristique — c'est la période la plus fréquentée."
        elif is_summer:
            oui_si = "profiter de longues journées ensoleillées et d'activités en plein air."
            non_si = "fuir la foule estivale — c'est le pic de fréquentation."
        elif is_shoulder:
            oui_si = "combiner bonne météo et tarifs plus doux qu'en pleine saison."
            non_si = "avoir une garantie absolue de beau temps — quelques jours mitigés possibles."
        else:
            oui_si = "profiter d'un temps agréable pour toutes les activités."
            non_si = "voyager avec un budget serré — les prix sont plus élevés en haute saison."
    elif score >= 6.0:
        if is_rainy:
            oui_si = "accepter des averses en échange de prix réduits et moins de touristes."
            non_si = "planifier des activités 100% extérieures — la pluie est fréquente."
        elif is_cold:
            oui_si = f"privilégier les musées et la gastronomie — il fait frais ({m['tmax']}°C)."
            non_si = "chercher du soleil pour bronzer ou nager — ce n'est pas la bonne saison."
        elif is_mild:
            oui_si = "explorer la ville à pied sans souffrir de la chaleur."
            non_si = "chercher une destination balnéaire — l'eau et l'air sont encore frais."
        elif is_shoulder:
            oui_si = f"profiter de l'entre-saison — moins de monde, {m['tmax']}°C agréables."
            non_si = "garantir un ensoleillement maximal — des journées grises sont possibles."
        else:
            oui_si = "visiter les sites culturels et profiter de la gastronomie locale."
            non_si = "garantir du soleil pour vos photos ou activités extérieures."
    else:
        if is_tropical and is_rainy:
            oui_si = "découvrir une facette différente hors des sentiers battus, à prix cassés."
            non_si = "craindre la pluie — c'est la mousson, les averses sont quotidiennes."
        elif is_cold and is_winter:
            oui_si = f"apprécier l'ambiance hivernale et les prix les plus bas de l'année."
            non_si = "chercher le soleil ou les activités de plein air."
        elif is_rainy:
            oui_si = "voyager hors saison avec des prix réduits et très peu de touristes."
            non_si = "éviter la pluie — plus d'un jour sur deux est pluvieux."
        else:
            oui_si = "profiter de tarifs bas et d'une fréquentation minimale."
            non_si = "rechercher un temps estival — les conditions ne s'y prêtent pas."

    # Month nav — colored by score class
    MNAV_STYLE = {
        'rec':   'background:#e8f8f0;border-color:#86efac;',
        'mid':   'background:#fffbeb;border-color:#fbbf24;',
        'avoid': 'background:#fef2f2;border-color:#fca5a5;',
    }
    def _mnav_attr(i):
        if i == mi:
            return ' class="active"'
        s = MNAV_STYLE.get(months[i]['classe'], '')
        return f' style="{s}"' if s else ''
    month_nav = ''.join(
        f'<a href="{slug}-meteo-{MONTH_URL[i]}.html"{_mnav_attr(i)}>{MONTH_ABBR[i]}</a>'
        for i in range(12)
    )

    # Annual table with current month highlighted
    table_rows = ''
    for i, mo in enumerate(months):
        highlight = ' style="background:#fef9c3;font-weight:700"' if i == mi else ''
        cls = mo['classe']
        ski_col = ''
        if is_mountain:
            from scoring import compute_ski_score, best_class
            ski = compute_ski_score(mo['tmax'], mo['rain_pct'], mo['sun_h'])
            cls = best_class(mo['classe'], ski)
            ski_col = f'<td>{ski:.1f}/10</td>'
        table_rows += (f'<tr class="{cls}"{highlight}>'
                       f'<td>{weather_emoji(mo["tmax"], mo["rain_pct"], mo["sun_h"])} {MONTHS_FR[i]}</td>'
                       f'<td>{mo["tmin"]}°C</td><td>{mo["tmax"]}°C</td>'
                       f'<td>{mo["rain_pct"]}%</td>'
                       f'<td>{mo["precip"]:.1f}</td>'
                       f'<td>{mo["sun_h"]}h</td>'
                       f'<td>{mo["score"]:.1f}/10</td>{ski_col}</tr>\n')

    # Best month diff
    bm = months[best_idx]
    diff_t = round(bm['tmax'] - m['tmax'])
    diff_r = round(bm['rain_pct'] - m['rain_pct'])
    diff_s = round(bm['sun_h'] - m['sun_h'], 1)

    # FAQ — variées selon contexte
    faq_q1 = f"{nom_bare} en {month_fr.lower()} : est-ce une bonne période ?"
    if is_mountain:
        from scoring import compute_ski_score
        ski_this = compute_ski_score(m['tmax'], m['rain_pct'], m['sun_h'])
        if ski_this >= 6.5 and score < 5:
            faq_a1 = (f"Pour le ski, oui : score ski {ski_this}/10 en {month_fr.lower()}. "
                      f"Les températures ({m['tmax']}°C max) garantissent un bon enneigement. "
                      f"Pour la randonnée estivale, préférez {best_month.lower()} ({best_score:.1f}/10).")
        elif ski_this >= 5 and score < 5:
            faq_a1 = (f"{month_fr} est une période correcte pour le ski (score ski {ski_this}/10). "
                      f"Les conditions ne sont pas idéales pour la randonnée ({score:.1f}/10).")
        elif score >= 9:
            faq_a1 = f"Oui, {month_fr.lower()} est l'une des meilleures périodes {prep} {nom_bare} (score {score:.1f}/10). {m['tmax']}°C, {m['sun_h']}h de soleil — idéal pour la randonnée."
        elif score >= 7:
            faq_a1 = f"Oui, {month_fr.lower()} est une bonne période ({score:.1f}/10). Idéal pour les activités outdoor et la randonnée."
        else:
            faq_a1 = (f"Période de transition avec un score été de {score:.1f}/10 et ski de {ski_this}/10. "
                      f"Ni la meilleure saison de ski ni d'été.")
    elif score >= 9:
        faq_a1 = f"Oui, {month_fr.lower()} est l'une des meilleures périodes {prep} {nom_bare} (score {score:.1f}/10). {m['tmax']}°C, {m['sun_h']}h de soleil et seulement {m['rain_pct']}% de jours pluvieux."
    elif score >= 7.5:
        faq_a1 = f"Oui, {month_fr.lower()} est une bonne période ({score:.1f}/10). Les conditions sont favorables même si {best_month.lower()} reste le mois optimal ({best_score:.1f}/10)."
    elif score >= 5.5:
        faq_a1 = f"{month_fr} est une période correcte ({score:.1f}/10) mais pas idéale. Attendez-vous à {m['rain_pct']}% de jours pluvieux. {best_month} ({best_score:.1f}/10) offre de meilleures garanties."
    else:
        faq_a1 = f"{month_fr} n'est pas recommandé {prep} {nom_bare} (score {score:.1f}/10). Avec {m['rain_pct']}% de jours pluvieux et {m['sun_h']}h de soleil, préférez {best_month.lower()} ({best_score:.1f}/10)."

    # Q2 — varie selon le type de météo du mois
    if is_mountain and is_cold:
        faq_q2 = f"Peut-on skier {prep} {nom_bare} en {month_fr.lower()} ?"
        if ski_this >= 6.5:
            faq_a2 = f"Oui, {month_fr.lower()} est une excellente période pour le ski (score {ski_this}/10). Avec {m['tmax']}°C max et {m['rain_pct']}% de précipitations, les conditions d'enneigement sont bonnes."
        elif ski_this >= 4:
            faq_a2 = f"Les conditions sont correctes (score ski {ski_this}/10) mais pas optimales. Vérifiez l'état des pistes avant de partir."
        else:
            faq_a2 = f"Le ski n'est pas recommandé en {month_fr.lower()} (score ski {ski_this}/10). Les températures ({m['tmax']}°C) limitent l'enneigement."
    elif is_hot and is_dry:
        faq_q2 = f"Fait-il trop chaud {prep} {nom_bare} en {month_fr.lower()} ?"
        faq_a2 = f"Les températures atteignent {m['tmax']}°C. {'C\'est intense mais gérable avec de la crème solaire et de l\'eau.' if m['tmax'] < 38 else 'La chaleur est extrême — limitez les activités aux heures fraîches.'} Ensoleillement : {m['sun_h']}h/jour."
    elif is_rainy:
        faq_q2 = f"Pleut-il beaucoup {prep} {nom_bare} en {month_fr.lower()} ?"
        faq_a2 = f"Oui, {m['rain_pct']}% des jours connaissent de la pluie en {month_fr.lower()}. {'En zone tropicale, ce sont souvent des averses courtes mais intenses.' if is_tropical else 'Prévoyez des activités couvertes en alternative.'}"
    elif is_cold:
        faq_q2 = f"Quel temps fait-il {prep} {nom_bare} en {month_fr.lower()} ?"
        faq_a2 = f"Il fait frais avec {m['tmax']}°C en journée et {m['tmin']}°C la nuit. {m['sun_h']}h de soleil par jour. Prévoyez des vêtements chauds et privilégiez les visites intérieures."
    elif score >= 8:
        faq_q2 = f"Que faire {prep} {nom_bare} en {month_fr.lower()} ?"
        faq_a2 = f"Avec {m['tmax']}°C et {m['sun_h']}h de soleil, toutes les activités extérieures sont possibles : {'plage, snorkeling et excursions en bateau.' if is_tropical else 'randonnées, visites de sites et terrasses.'}"
    else:
        faq_q2 = f"Que faire {prep} {nom_bare} en {month_fr.lower()} ?"
        faq_a2 = f"Avec {m['tmax']}°C max et {m['sun_h']}h de soleil, {'concentrez-vous sur les sites culturels, musées et gastronomie locale.' if score >= 6 else 'privilégiez les activités couvertes — musées, spas, gastronomie.'}"

    faq_schema = json.dumps({
        "@context": "https://schema.org", "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": faq_q1, "acceptedAnswer": {"@type": "Answer", "text": faq_a1}},
            {"@type": "Question", "name": faq_q2, "acceptedAnswer": {"@type": "Answer", "text": faq_a2}},
        ]
    }, ensure_ascii=False)

    article_schema = json.dumps({
        "@context": "https://schema.org", "@type": "Article",
        "headline": f"Météo {prep} {nom_bare} en {month_fr.lower()} — Températures, pluie et conseils",
        "description": f"Météo {prep} {nom_bare} en {month_fr.lower()} : {m['tmax']}°C, {m['rain_pct']}% de jours pluvieux. Score {score:.1f}/10.",
        "author": {"@type": "Organization", "name": "BestDateWeather"},
        "publisher": {"@type": "Organization", "name": "BestDateWeather"},
        "dateModified": TODAY,
        "mainEntityOfPage": {"@type": "WebPage",
            "@id": f"https://bestdateweather.com/{slug}-meteo-{month_url}.html"}
    }, ensure_ascii=False)

    breadcrumb_schema = json.dumps({
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Accueil", "item": "https://bestdateweather.com/"},
            {"@type": "ListItem", "position": 2, "name": nom_bare, "item": f"https://bestdateweather.com/meilleure-periode-{slug}.html"},
            {"@type": "ListItem", "position": 3, "name": month_fr, "item": f"https://bestdateweather.com/{slug}-meteo-{month_url}.html"}
        ]
    }, ensure_ascii=False)

    title_var = hash(slug + str(mi)) % 3
    if title_var == 0:
        title = f"{nom_bare} en {month_fr.lower()} : météo, pluie ({m['rain_pct']}%) et faut-il partir ? [{YEAR}]"
    elif title_var == 1:
        title = f"Météo {prep} {nom_bare} en {month_fr.lower()} [{YEAR}] — {m['tmax']}°C, {m['rain_pct']}% pluie"
    else:
        title = f"Partir {prep} {nom_bare} en {month_fr.lower()} ? Score {score:.1f}/10 [{YEAR}]"

    desc_var = hash(slug + str(mi) + 'd') % 3
    if desc_var == 0:
        desc = f"Météo {prep} {nom_bare} en {month_fr.lower()} : {m['tmax']}°C max, {m['rain_pct']}% de jours pluvieux, {m['sun_h']}h de soleil/jour. Score {score:.1f}/10. Données 10 ans Open-Meteo."
    elif desc_var == 1:
        desc = f"{nom_bare} en {month_fr.lower()} : {m['tmax']}°C, {m['sun_h']}h de soleil, {m['rain_pct']}% de pluie. {'Période recommandée.' if score >= 7.5 else 'Période moyenne.' if score >= 5.5 else 'Période déconseillée.'} Score {score:.1f}/10."
    else:
        desc = f"Faut-il partir {prep} {nom_bare} en {month_fr.lower()} ? {m['tmax']}°C et {m['rain_pct']}% de pluie — score météo {score:.1f}/10 sur 10 ans de données."

    h1_var = hash(slug + str(mi) + 'h1') % 3
    if h1_var == 0:
        h1_text = f"Météo {prep} {nom_bare}<br/><em>en {month_fr.lower()}</em>"
    elif h1_var == 1:
        h1_text = f"{nom_bare} en {month_fr.lower()}<br/><em>quel temps fait-il ?</em>"
    else:
        h1_text = f"Partir {prep} {nom_bare}<br/><em>en {month_fr.lower()} ?</em>"

    # Data for cross-linking similar destinations
    climate_for_sim = {}
    for _, sim_slug in similarities.get(slug, [])[:3]:
        if sim_slug in all_climate and all_climate[sim_slug][mi]:
            sm = all_climate[sim_slug][mi]
            climate_for_sim[sim_slug] = {'score': f"{sm['score']:.1f}", 'tmax': sm['tmax']}

    # Build cross-linking HTML
    sim_cards_html = ''
    for _, sim_slug in similarities.get(slug, [])[:3]:
        if sim_slug not in all_dests:
            continue
        sd = all_dests[sim_slug]
        # Skip destinations without monthly pages
        if sd.get('monthly', 'True').strip().lower() not in ('true', '1', 'yes', ''):
            continue
        sn = sd.get('nom_bare', sim_slug)
        sf = sd.get('flag', '')
        sc = climate_for_sim.get(sim_slug, {})
        sc_score = sc.get('score', '?')
        sc_tmax = sc.get('tmax', '?')
        sim_cards_html += (
            f'<a href="{sim_slug}-meteo-{MONTH_URL[mi]}.html" style="flex:1;min-width:180px;'
            f'padding:14px;background:white;border:1.5px solid #e8e0d0;border-radius:12px;'
            f'text-decoration:none;display:flex;flex-direction:column;gap:4px">'
            f'<div style="font-weight:700;color:var(--navy);font-size:14px">'
            f'<img src="flags/{sf}.png" width="16" height="12" '
            f'alt="" style="vertical-align:middle;margin-right:4px;border-radius:1px">'
            f'{sn}</div>'
            f'<div style="font-size:12px;color:var(--slate2)">{MONTHS_FR[mi]} : {sc_score}/10 · {sc_tmax}°C</div>'
            f'</a>')
    similar_section_monthly = f'''<section class="section">
 <div class="section-label">Explorer aussi</div>
 <h2 class="section-title">Destinations similaires en {MONTHS_FR[mi].lower()}</h2>
 <div style="display:flex;gap:14px;flex-wrap:wrap">{sim_cards_html}</div>
</section>''' if sim_cards_html else ''

    # Pillar + comparison reverse links for monthly page
    pillar_link = (f'<a href="ou-partir-en-{MONTH_URL[mi]}.html" style="flex:1;min-width:180px;'
                   f'padding:14px 16px;background:white;border:1.5px solid #e8e0d0;border-radius:12px;'
                   f'text-decoration:none;font-size:14px;font-weight:600;color:var(--navy)">'
                   f'📅 Où partir en {MONTHS_FR[mi].lower()} — top 25</a>')
    comp_links = _build_comp_cards_monthly_fr(slug, nom_bare, comparison_index, all_dests) if comparison_index else ''

    html = f'''<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1.0"/>
{GTAG}
<title>{title}</title>
<meta name="description" content="{desc}"/>
<link rel="canonical" href="https://bestdateweather.com/{slug}-meteo-{month_url}.html"/>
<link rel="alternate" hreflang="fr" href="https://bestdateweather.com/{slug}-meteo-{month_url}.html"/>
<link rel="alternate" hreflang="en" href="https://bestdateweather.com/en/{slug_en}-weather-{MONTH_URL_EN[mi]}.html"/>
<link rel="alternate" hreflang="x-default" href="https://bestdateweather.com/en/{slug_en}-weather-{MONTH_URL_EN[mi]}.html"/>
<meta property="og:type" content="article"/>
<meta property="og:title" content="Météo {prep} {nom_bare} en {month_fr.lower()} — {m['tmax']}°C, {m['rain_pct']}% pluie"/>
<meta property="og:description" content="{desc}"/>
<meta property="og:url" content="https://bestdateweather.com/{slug}-meteo-{month_url}.html"/>
<script type="application/ld+json">{article_schema}</script>
<script type="application/ld+json">{faq_schema}</script>
<script type="application/ld+json">{breadcrumb_schema}</script>
{COMMON_HEAD_CSS}
<style>
.hero-band{{background:{MONTHLY_GRAD[mi]};}}
.hero-title em{{color:#93c5fd;}}
.month-nav{{display:flex;gap:10px;margin-bottom:24px;flex-wrap:wrap;}}
.month-nav a{{padding:8px 14px;border-radius:8px;font-size:13px;font-weight:600;text-decoration:none;background:white;border:1.5px solid #e8e0d0;color:var(--navy);}}
.month-nav a.active{{background:var(--gold);color:white;border-color:var(--gold);}}
.month-nav a:hover{{border-color:var(--gold);}}
</style>
</head>
<body><script>window.scrollTo(0,0);</script>
{NAV}
<header class="hero-band">
 <div class="dest-tag"><img src="flags/{flag}.png" width="20" height="15" alt="{flag.upper()}" style="vertical-align:middle;margin-right:4px;border-radius:1px"> {nom_bare} · {season}</div>
 <h1 class="hero-title">{h1_text}</h1>
 <p class="hero-sub">{hero_sub}</p>
 <div class="kicker">Open-Meteo · 10 ans · 12 mois comparés · {lat:.2f}°N {abs(lon):.2f}°{"E" if lon >= 0 else "W"}</div>
 <div class="hero-stats" style="margin-top:22px">
 <div><span class="hstat-val">{m['tmax']}°C</span><span class="hstat-lbl">Température max</span></div>
 <div><span class="hstat-val">{m['rain_pct']}%</span><span class="hstat-lbl">Jours pluvieux</span></div>
 <div><span class="hstat-val">{m['sun_h']}h</span><span class="hstat-lbl">Soleil / jour</span></div>
 </div>
</header>
<main class="page">
 <section class="section">
 <div class="section-label">Résumé du mois</div>
 <h2 class="section-title">Météo {prep} {nom_bare} en {month_fr.lower()}</h2>
 <div style="display:inline-flex;align-items:center;gap:6px;padding:6px 14px;border-radius:20px;font-size:13px;font-weight:700;background:{bg};color:{txt};border:1.5px solid {txt};margin-bottom:16px">{verdict_lbl}</div>
 <div class="quick-facts">
 <div class="quick-facts-row"><div class="qf-label">🌡️ Température min / max</div><div class="qf-value"><strong>{m['tmin']}°C – {m['tmax']}°C</strong></div></div>
 <div class="quick-facts-row"><div class="qf-label">🌧 Jours pluvieux</div><div class="qf-value"><strong>{m['rain_pct']}%</strong> des jours</div></div>
 <div class="quick-facts-row"><div class="qf-label">☀️ Soleil</div><div class="qf-value"><strong>{m['sun_h']}h</strong> par jour en moyenne</div></div>
 <div class="quick-facts-row"><div class="qf-label">🌊 Saison</div><div class="qf-value"><strong>{season}</strong></div></div>
 <div class="quick-facts-row"><div class="qf-label">⭐ Score météo</div><div class="qf-value"><strong>{score:.1f}/10</strong></div></div>
 <div class="quick-facts-row"><div class="qf-label">📅 Meilleur mois</div><div class="qf-value"><strong>{best_month}</strong> ({best_score:.1f}/10)</div></div>
 </div>
 </section>

 <section class="section" style="margin-bottom:28px">
 <div class="section-label">Décision rapide</div>
 <h2 class="section-title">Faut-il partir {prep} {nom_bare} en {month_fr.lower()} ?</h2>
 <div style="display:inline-flex;align-items:center;gap:6px;padding:6px 14px;border-radius:20px;font-size:13px;font-weight:700;background:{bg};color:{txt};border:1.5px solid {txt};margin-bottom:16px">{verdict_lbl}</div>
 <div style="margin-bottom:14px;font-size:14px;line-height:1.7">
 <p style="margin-bottom:8px"><strong>✅ Oui si :</strong> {oui_si}</p>
 <p><strong>❌ Non si :</strong> {non_si}</p>
 </div>
 <div style="background:#f8f8f4;border-radius:10px;padding:14px;font-size:13px;line-height:1.9;margin-bottom:14px">
 <div>🌧 Pluie : {rain_bar} <span style="color:#718096">{m['rain_pct']}%</span></div>
 <div>🌡 Température : {temp_bar} <span style="color:#718096">{m['tmax']}°C</span></div>
 <div>☀️ Soleil : {sun_bar} <span style="color:#718096">{m['sun_h']}h/j</span></div>
 </div>
 <p style="font-size:14px;line-height:1.7;border-top:1px solid #e8e0d0;padding-top:14px"><strong>Notre avis :</strong> {verdict_txt}</p>
 </section>

 <section class="section" style="margin-bottom:28px">
 <div class="section-label">Selon votre projet</div>
 <h2 class="section-title">{nom_bare} en {month_fr.lower()} selon votre type de voyage</h2>
 <ul style="list-style:none;padding:0;border:1.5px solid var(--cream2);border-radius:12px;overflow:hidden;font-size:14px">
 <li style="padding:10px 16px;border-bottom:1px solid var(--cream2);background:white">🏙️ City-trip / culture : <strong>{act_city}</strong></li>
 <li style="padding:10px 16px;border-bottom:1px solid var(--cream2)">🚶 Activités extérieures : <strong>{act_ext}</strong></li>
 <li style="padding:10px 16px;border-bottom:1px solid var(--cream2);background:white">🏖️ Plage / baignade : <strong>{act_beach}</strong></li>
 <li style="padding:10px 16px">💰 Budget : <strong>{bud}</strong></li>
 </ul>
 </section>

 <section class="section" style="border-left:3px solid var(--gold);padding-left:18px;margin-bottom:28px">
 <div class="section-label">Contexte local</div>
 <h2 class="section-title">À quoi s'attendre en {month_fr.lower()}</h2>
 <p style="font-size:14px;line-height:1.8;color:var(--slate)">{context_paragraph_fr(nom_bare, prep, m, mi, score, best_month, best_score, is_tropical, event_text=(events or {}).get((slug, mi+1), {}).get('fr'))}</p>
 </section>

 <section class="section">
 <div class="section-label">Naviguer par mois</div>
 <h2 class="section-title">Tous les mois {prep} {nom_bare}</h2>
 <div class="month-nav">{month_nav}</div>
 </section>

 <section class="section">
 <div class="section-label">Tableau annuel</div>
 <h2 class="section-title">Comparaison mois par mois</h2>
 <div class="{'climate-table-wrap mountain' if is_mountain else 'climate-table-wrap'}">
 <table class="climate-table" aria-label="Tableau climat mensuel {nom_bare}">
 <thead><tr><th>Mois</th><th>T° min</th><th>T° max</th><th>Pluie %</th><th>Précip. mm</th><th>Soleil h/j</th><th>Score</th>{'<th>Score ski 🎿</th>' if is_mountain else ''}</tr></thead>
 <tbody>{table_rows}</tbody>
 </table>
 </div>
 <div class="table-legend">
 <span><span class="legend-dot" style="background:#1a7a4a"></span>Idéal</span>
 <span><span class="legend-dot" style="background:#d97706"></span>Acceptable</span>
 <span><span class="legend-dot" style="background:#dc2626"></span>Défavorable</span>
 <span style="margin-left:auto">◀ Mois consulté · Source Open-Meteo · 10 ans</span>
 </div>
 </section>

 <div class="eeat-note" style="margin:20px 0;padding:14px 18px;background:#f8f6f2;border-left:3px solid var(--gold);border-radius:0 8px 8px 0;font-size:13px;color:var(--slate2);line-height:1.7">
 <strong style="color:var(--navy);display:block;margin-bottom:4px">📊 Source des données</strong>
 Données calculées sur <strong>10 ans de relevés ERA5</strong> via Open-Meteo, avec ajustement saisonnier ECMWF.
 En {month_fr.lower()}, {nom_bare} affiche en moyenne <strong>{m['tmax']}°C</strong>, {m['rain_pct']}% de jours pluvieux et {m['sun_h']}h de soleil par jour.
 Score météo global du mois : <strong>{score:.1f}/10</strong>.
 <a href="methodologie.html" style="color:var(--gold);font-weight:600">Voir la méthodologie →</a>
 </div>

 <section class="section" style="margin-bottom:28px">
 <div class="section-label">Comparaison</div>
 <h2 class="section-title">{month_fr} vs {best_month} (meilleur mois)</h2>
 <p style="font-size:14px;margin-bottom:12px">Le meilleur mois est <strong><a href="meilleure-periode-{slug}.html" style="color:inherit">{best_month}</a></strong> (score {best_score:.1f}/10). Différence :</p>
 <ul style="list-style:none;padding:0;border:1.5px solid var(--cream2);border-radius:10px;overflow:hidden;font-size:14px">
 <li style="padding:10px 16px;border-bottom:1px solid var(--cream2);background:white">🌡️ Température max : <strong>{'+' if diff_t >= 0 else ''}{diff_t}°C</strong></li>
 <li style="padding:10px 16px;border-bottom:1px solid var(--cream2)">🌧 Jours de pluie : <strong>{'+' if diff_r >= 0 else ''}{diff_r}%</strong></li>
 <li style="padding:10px 16px">☀️ Ensoleillement : <strong>{'+' if diff_s >= 0 else ''}{diff_s}h/jour</strong></li>
 </ul>
 </section>

 <section class="section" style="margin-bottom:28px">
 <div class="section-label">Questions fréquentes</div>
 <h2 class="section-title">FAQ — {nom_bare} en {month_fr.lower()}</h2>
 <div style="display:flex;flex-direction:column;gap:12px">
 <div style="border:1.5px solid var(--cream2);border-radius:10px;padding:16px;background:white">
 <div style="font-weight:700;margin-bottom:8px">{faq_q1}</div>
 <div style="color:var(--slate2);font-size:14px;line-height:1.65">{faq_a1}</div>
 </div>
 <div style="border:1.5px solid var(--cream2);border-radius:10px;padding:16px;background:white">
 <div style="font-weight:700;margin-bottom:8px">{faq_q2}</div>
 <div style="color:var(--slate2);font-size:14px;line-height:1.65">{faq_a2}</div>
 </div>
 </div>
 </section>

 <section class="section">
 <div class="section-label">Mois précédent / suivant</div>
 <div style="display:flex;gap:14px;flex-wrap:wrap">
 <a href="{slug}-meteo-{MONTH_URL[prev_mi]}.html" style="flex:1;min-width:140px;padding:16px;background:white;border:1.5px solid #e8e0d0;border-radius:12px;text-decoration:none;text-align:center">
 <div style="font-size:11px;color:var(--slate3);margin-bottom:4px">← Mois précédent</div>
 <div style="font-weight:700;color:var(--navy)">{MONTHS_FR[prev_mi]}</div>
 <div style="font-size:12px;color:var(--slate2)">{months[prev_mi]['tmax']}°C · {months[prev_mi]['rain_pct']}% pluie</div>
 </a>
 <a href="meilleure-periode-{slug}.html" style="flex:1;min-width:140px;padding:16px;background:#fef9c3;border:1.5px solid var(--gold);border-radius:12px;text-decoration:none;text-align:center">
 <div style="font-size:11px;color:var(--slate3);margin-bottom:4px">📅 Vue annuelle</div>
 <div style="font-weight:700;color:var(--navy)">Tous les mois</div>
 <div style="font-size:12px;color:var(--slate2)">Meilleur : {best_month.lower()}</div>
 </a>
 <a href="{slug}-meteo-{MONTH_URL[next_mi]}.html" style="flex:1;min-width:140px;padding:16px;background:white;border:1.5px solid #e8e0d0;border-radius:12px;text-decoration:none;text-align:center">
 <div style="font-size:11px;color:var(--slate3);margin-bottom:4px">Mois suivant →</div>
 <div style="font-weight:700;color:var(--navy)">{MONTHS_FR[next_mi]}</div>
 <div style="font-size:12px;color:var(--slate2)">{months[next_mi]['tmax']}°C · {months[next_mi]['rain_pct']}% pluie</div>
 </a>
 </div>
 </section>

 <section class="section">
 <div class="section-label">Explorer aussi</div>
 <h2 class="section-title">Destinations similaires en {month_fr.lower()}</h2>
  <div style="display:flex;gap:14px;flex-wrap:wrap">''' + _build_sim_cards_fr(similarities.get(slug, [])[:3], all_dests, climate_for_sim, mi) + f'''</div>
  </section>

 <section class="section">
 <div class="section-label">Classements météo</div>
 <h2 class="section-title">Comparer les destinations par météo</h2>
 <div style="display:flex;gap:14px;flex-wrap:wrap"><a href="classement-destinations-meteo-2026.html" style="flex:1;min-width:170px;padding:14px 16px;background:white;border:1.5px solid #e8e0d0;border-radius:12px;text-decoration:none;font-size:14px;font-weight:600;color:var(--navy)">🌍 Classement mondial 2026</a><a href="classement-destinations-meteo-ete-2026.html" style="flex:1;min-width:170px;padding:14px 16px;background:white;border:1.5px solid #e8e0d0;border-radius:12px;text-decoration:none;font-size:14px;font-weight:600;color:var(--navy)">🌞 Meilleures destinations été</a><a href="classement-destinations-meteo-hiver-2026.html" style="flex:1;min-width:170px;padding:14px 16px;background:white;border:1.5px solid #e8e0d0;border-radius:12px;text-decoration:none;font-size:14px;font-weight:600;color:var(--navy)">🌴 Destinations soleil hiver</a></div>
 </section>

 <section class="section">
 <div class="section-label">Guides & comparatifs</div>
 <h2 class="section-title">Explorer ou comparer</h2>
 <div style="display:flex;gap:14px;flex-wrap:wrap">{pillar_link}{comp_links}</div>
 </section>

 <section class="widget-section">
 <div class="cta-box" style="text-align:center">
 <strong>📅 Prévisions actualisées — 12 prochains mois</strong>
 <p>Données temps réel avec corrections saisonnières ECMWF · mise à jour quotidienne</p>
 <a class="cta-btn" href="index.html">
 <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" style="width:18px;height:18px"><path d="M8 6h13M8 12h13M8 18h13M3 6h.01M3 12h.01M3 18h.01"/></svg>
 Tester l'application météo
 </a>
 </div>
 </section>
</main>
{footer_html(slug, nom_bare, prep, slug_en)}
</body>
</html>'''
    return html


# ── POINT D'ENTRÉE ───────────────────────────────────────────────────────────

def main():
    args        = sys.argv[1:]
    dry_run     = '--dry-run' in args
    validate_only = '--validate-only' in args
    target      = next((a for a in args if not a.startswith('--')), None)

    print("BestDateWeather — generate_all.py")
    print(f"Mode: {'validate-only' if validate_only else 'dry-run' if dry_run else 'production'}")
    print(f"Cible: {target or 'toutes les destinations'}\n")

    dests, climate, cards, overrides, events = load_data()

    # Validate
    errors = validate(dests, climate, cards)
    if errors:
        print(f"⚠️  {len(errors)} problème(s) détecté(s):")
        for e in errors:
            print(f"   {e}")
        if any(e.startswith('[P0]') for e in errors):
            print("\n❌ Erreurs P0 bloquantes. Corrigez data/climate.csv avant de régénérer.")
            if not dry_run:
                sys.exit(1)
    else:
        print("✅ Validation OK — aucune incohérence détectée\n")

    if validate_only:
        return

    # Pre-compute similarities for cross-linking
    similarities = compute_all_similarities(dests, climate)
    comp_index = build_comparison_index()

    # Generate
    slugs = [target] if target else list(dests.keys())
    total_annual = total_monthly = 0
    errors_gen = []

    for slug in slugs:
        if slug not in dests:
            print(f"[SKIP] {slug}: destination inconnue")
            continue
        if slug not in climate or None in climate[slug]:
            print(f"[SKIP] {slug}: données climatiques incomplètes")
            continue

        dest   = dests[slug]
        months = climate[slug]
        dest_cards = cards.get(slug, [])

        # Annual fiche
        try:
            html = gen_annual(dest, months, dest_cards, dests, similarities, comp_index)
            out  = f"{OUT}/meilleure-periode-{slug}.html"
            if not dry_run:
                open(out, 'w', encoding='utf-8').write(html)
            total_annual += 1
        except Exception as e:
            errors_gen.append(f"{slug}/annual: {e}")

        # 12 monthly fiches (skip if monthly=False in destinations.csv)
        gen_monthly_pages = dest.get('monthly', 'True').strip().lower() in ('true', '1', 'yes', '')
        if gen_monthly_pages:
            for mi in range(12):
                try:
                    html = gen_monthly(dest, months, mi, dests, similarities, climate, events, comp_index)
                    out  = f"{OUT}/{slug}-meteo-{MONTH_URL[mi]}.html"
                    if not dry_run:
                        open(out, 'w', encoding='utf-8').write(html)
                    total_monthly += 1
                except Exception as e:
                    errors_gen.append(f"{slug}/{MONTHS_FR[mi]}: {e}")

        if not dry_run:
            monthly_msg = "12 fiches mensuelles" if gen_monthly_pages else "mensuelles ignorées (monthly=False)"
            print(f"✓ {slug}: 1 fiche annuelle + {monthly_msg}")

    print(f"\n{'[DRY-RUN] ' if dry_run else ''}Généré: {total_annual} fiches annuelles + {total_monthly} fiches mensuelles")
    if errors_gen:
        print(f"Erreurs de génération ({len(errors_gen)}):")
        for e in errors_gen:
            print(f"  {e}")
    else:
        print("✅ Aucune erreur de génération")

    if overrides:
        print(f"ℹ️  {len(overrides)} override(s) appliqué(s) depuis overrides.csv")


if __name__ == '__main__':
    main()
