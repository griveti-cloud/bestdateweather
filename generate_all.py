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
SEASONS    = {
    0:'Hiver',1:'Hiver',2:'Printemps',3:'Printemps',4:'Printemps',
    5:'Été',6:'Été',7:'Été',8:'Automne',9:'Automne',10:'Automne',11:'Hiver'
}
SEASON_ICONS = {'Printemps':'🌸','Été':'☀️','Automne':'🍂','Hiver':'❄️'}
TODAY = date.today().strftime('%Y-%m-%d')
YEAR  = date.today().year

# ── CHARGEMENT DES DONNÉES ───────────────────────────────────────────────────

def load_data(target_slug=None):
    """Charge et retourne (destinations, climate, cards, overrides)."""

    # destinations.csv
    dests = {}
    for row in csv.DictReader(open(f'{DATA}/destinations.csv', encoding='utf-8')):
        dests[row['slug_fr']] = row

    # climate.csv
    climate = {}  # {slug: [month_dict × 12]}
    for row in csv.DictReader(open(f'{DATA}/climate.csv', encoding='utf-8')):
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
    for row in csv.DictReader(open(f'{DATA}/cards.csv', encoding='utf-8')):
        slug = row['slug']
        cards.setdefault(slug, []).append(row)

    # overrides.csv
    overrides = {}  # {(slug, mi, champ): valeur}
    for row in csv.DictReader(open(f'{DATA}/overrides.csv', encoding='utf-8')):
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

    return dests, climate, cards, overrides


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

def best_months(months):
    """Retourne la liste des mois ex-aequo avec le score max."""
    max_score = max(m['score'] for m in months)
    return [MONTHS_FR[i] for i, m in enumerate(months) if m['score'] == max_score]

def budget_tier(score, all_scores):
    """Tier relatif : top 4 = Haute saison, bottom 4 = Prix bas, reste = Épaule."""
    sorted_scores = sorted(all_scores, reverse=True)
    n = len(sorted_scores)
    top = sorted_scores[min(3, n-1)]
    bottom = sorted_scores[max(n-5, 0)]
    if score >= top:   return '💸 Haute saison'
    if score <= bottom: return '✅ Prix bas'
    return '🌿 Épaule'

def score_badge(score):
    if score >= 9.0: return '#dcfce7','#16a34a','✅ Excellent'
    if score >= 7.5: return '#dcfce7','#16a34a','✅ Favorable'
    if score >= 6.0: return '#fef9c3','#ca8a04','⚠️ Acceptable'
    return '#fee2e2','#dc2626','❌ Peu favorable'

def seasonal_stats(months):
    """Calcule stats par saison (Printemps/Été/Automne/Hiver)."""
    seasons = {'Printemps':[2,3,4],'Été':[5,6,7],'Automne':[8,9,10],'Hiver':[11,0,1]}
    result = {}
    for name, idxs in seasons.items():
        ms = [months[i] for i in idxs]
        avg_t  = round(sum(m['tmax'] for m in ms) / len(ms))
        avg_r  = round(sum(m['rain_pct'] for m in ms) / len(ms))
        avg_s  = round(sum(m['sun_h'] for m in ms) / len(ms), 1)
        avg_sc = round(sum(m['score'] for m in ms) / len(ms), 1)
        if avg_sc >= 8.5: verdict = 'Excellente période'
        elif avg_sc >= 7.0: verdict = 'Bonne période'
        elif avg_sc >= 5.5: verdict = 'Période acceptable'
        else: verdict = 'Période difficile'
        result[name] = {'tmax': avg_t, 'rain_pct': avg_r, 'sun_h': avg_s,
                        'score': avg_sc, 'verdict': verdict}
    return result

def bar_chart(pct, max_val=100):
    filled = round((pct / max_val) * 10)
    return '█' * filled + '░' * (10 - filled)


# ── TEMPLATES HTML ───────────────────────────────────────────────────────────

COMMON_HEAD_CSS = '''<link rel="stylesheet" href="style.css"/>
<link rel="icon" type="image/x-icon" href="favicon.ico"/>
<link rel="apple-touch-icon" sizes="180x180" href="apple-touch-icon.png"/>
<meta name="theme-color" content="#1a1f2e"/>'''

GTAG = '''<script async src="https://www.googletagmanager.com/gtag/js?id=G-NTCJTDPSJL"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}gtag("js",new Date());gtag("config","G-NTCJTDPSJL");</script>'''

NAV = '''<nav>
 <a class="nav-brand" href="index.html">Best<em>Date</em>Weather</a>
 <a class="nav-cta" href="index.html">Tester l'application</a>
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
</footer>'''

def climate_table_html(months, nom_bare):
    rows = ''
    for i, m in enumerate(months):
        rows += (f'<tr class="{m["classe"]}" data-tmax="{m["tmax"]}" '
                 f'data-rain="{m["rain_pct"]}" data-sun="{m["sun_h"]}">'
                 f'<td>{MONTHS_FR[i]}</td>'
                 f'<td>{m["tmin"]}°C</td><td>{m["tmax"]}°C</td>'
                 f'<td>{m["rain_pct"]}%</td>'
                 f'<td>{m["precip"]:.1f}</td>'
                 f'<td>{m["sun_h"]}h</td>'
                 f'<td>{m["score"]:.1f}/10</td></tr>\n')
    return f'''<div class="climate-table-wrap">
 <table class="climate-table" aria-label="Tableau climat mensuel {nom_bare}">
 <thead><tr><th>Mois</th><th>T° min</th><th>T° max</th><th>Jours de pluie (%)</th><th>Précip. mm/j</th><th>Soleil h/j</th><th>Score</th></tr></thead>
 <tbody>{rows}</tbody>
 </table>
</div>
<div class="table-legend">
 <span><span class="legend-dot" style="background:#1a7a4a"></span>Idéal</span>
 <span><span class="legend-dot" style="background:#d97706"></span>Acceptable</span>
 <span><span class="legend-dot" style="background:#dc2626"></span>Hors saison</span>
 <span style="margin-left:auto">Source Open-Meteo · 10 ans</span>
</div>'''


# ── GÉNÉRATEUR FICHE ANNUELLE ────────────────────────────────────────────────

def gen_annual(dest, months, dest_cards):
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

    # Meta
    title = f"Meilleure période pour partir {prep} {nom_bare} [{YEAR}] — Météo & conseils"
    desc  = (f"Quelle est la meilleure période pour visiter {nom_bare} ? "
             f"{MONTHS_FR[best_idx]} offre {best_tmax}°C et {best_rain}% de jours pluvieux. "
             f"Score météo : {best_score}/10. Données 10 ans Open-Meteo.")

    # Climate table
    table_html = climate_table_html(months, nom_bare)

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
</section>'''

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
        booking_section = f'''<section class="section">
 <div class="section-label">Hébergement</div>
 <h2 class="section-title">Trouver un hébergement {prep} {nom_bare}</h2>
 <div class="affil-box">
 <strong>Voir les disponibilités sur la période recommandée</strong>
 <p>Conseil : comparez aussi le créneau hors pic — souvent 15-40% moins cher pour une météo identique.</p>
 <div style="display:flex;gap:12px;flex-wrap:wrap">
 <a class="affil-btn" href="{booking_url}" target="_blank" rel="noopener">Booking.com →</a>
 </div>
 </div>
</section>'''
    else:
        booking_section = ''

    # Monthly nav section
    monthly_links = ''.join(
        f'<a href="{slug}-meteo-{MONTH_URL[i]}.html" style="display:block;padding:10px 8px;'
        f'background:#f0fdf4;border-radius:10px;border:1.5px solid #86efac;'
        f'text-decoration:none;text-align:center">'
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
</section>'''

    # FAQ
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
<meta property="og:type" content="article"/>
<meta property="og:title" content="Meilleure période {prep} {nom_bare} — météo &amp; conseils"/>
<meta property="og:description" content="{desc}"/>
<meta property="og:url" content="https://bestdateweather.com/meilleure-periode-{slug}.html"/>
<script type="application/ld+json">{article_schema}</script>
<script type="application/ld+json">{faq_schema}</script>
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
 <h1 class="hero-title">Meilleure période pour partir<br/><em>{prep} {nom_bare}</em></h1>
 <p class="hero-sub">{hero_sub}</p>
 <div class="kicker">Mis à jour : {date.today().strftime("%B %Y")} · Open-Meteo · 10 ans · {lat}°N {abs(lon)}°{"E" if lon >= 0 else "W"}</div>
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
</main>
{footer_html(slug, nom_bare, prep, slug_en)}
<script>
function toggleFaq(btn){{
  const a=btn.nextElementSibling;
  a.style.display=a.style.display==="block"?"none":"block";
  btn.querySelector(".faq-icon").textContent=a.style.display==="block"?"-":"+";
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

def gen_monthly(dest, months, mi):
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

    all_scores = [mo['score'] for mo in months]
    best_idx   = max(range(12), key=lambda i: months[i]['score'])
    best_month = MONTHS_FR[best_idx]
    best_score = months[best_idx]['score']
    bg, txt, verdict_lbl = score_badge(score)
    bud = budget_tier(score, all_scores)

    # Prev / next
    prev_mi = (mi - 1) % 12
    next_mi = (mi + 1) % 12

    # Activities
    act_city  = '✅ Bon' if score >= 6.5 else '⚠️ Possible'
    act_ext   = '✅ Bon' if score >= 7.5 else ('⚠️ Possible' if score >= 6.0 else '❌ Déconseillé')
    act_beach = ('✅ Bon' if score >= 7.5 and m['tmax'] >= 25
                 else ('⚠️ Possible' if score >= 6.5 and m['tmax'] >= 20 else '❌ Déconseillé'))

    # Hero sub
    if score >= 8.5:
        hero_sub = f"{month_fr} est l'une des meilleures périodes {prep} {nom_bare}."
    elif score >= 7.0:
        hero_sub = f"{month_fr} est une bonne période. {best_month} est légèrement meilleur."
    else:
        hero_sub = f"{month_fr} est difficile — {best_month} offre de bien meilleures conditions."

    # Verdict text
    if score >= 8.5:
        verdict_txt = f"{month_fr} est une excellente période {prep} {nom_bare}. Conditions optimales."
    elif score >= 7.0:
        verdict_txt = f"{month_fr} est une bonne période {prep} {nom_bare}. {best_month} reste légèrement meilleur."
    else:
        verdict_txt = f"{month_fr} est difficile {prep} {nom_bare}. {best_month} ({best_score}/10) est bien plus favorable."

    # Bars
    rain_bar = bar_chart(m['rain_pct'])
    temp_bar = bar_chart(min(m['tmax'], 40), 40)
    sun_bar  = bar_chart(min(m['sun_h'], 14), 14)

    # Oui / Non si
    if score >= 8.0:
        oui_si = "profiter d'un temps agréable pour toutes les activités."
        non_si = "voyager avec un budget serré — les prix sont plus élevés."
    elif score >= 6.0:
        oui_si = "visiter les sites culturels et la gastronomie locale."
        non_si = "garantir du soleil pour vos photos ou activités extérieures."
    else:
        oui_si = "voyager hors saison avec des prix réduits."
        non_si = "éviter la pluie ou chercher un temps estival."

    # Month nav
    month_nav = ''.join(
        f'<a href="{slug}-meteo-{MONTH_URL[i]}.html'
        f'"{" class=\"active\"" if i == mi else ""}>{MONTH_ABBR[i]}</a>'
        for i in range(12)
    )

    # Annual table with current month highlighted
    table_rows = ''
    for i, mo in enumerate(months):
        highlight = ' style="background:#fef9c3;font-weight:700"' if i == mi else ''
        table_rows += (f'<tr class="{mo["classe"]}"{highlight}>'
                       f'<td>{MONTHS_FR[i]}</td>'
                       f'<td>{mo["tmin"]}°C</td><td>{mo["tmax"]}°C</td>'
                       f'<td>{mo["rain_pct"]}%</td>'
                       f'<td>{mo["precip"]:.1f}</td>'
                       f'<td>{mo["sun_h"]}h</td>'
                       f'<td>{mo["score"]:.1f}/10</td></tr>\n')

    # Best month diff
    bm = months[best_idx]
    diff_t = round(bm['tmax'] - m['tmax'])
    diff_r = round(bm['rain_pct'] - m['rain_pct'])
    diff_s = round(bm['sun_h'] - m['sun_h'], 1)

    # FAQ
    faq_q1 = f"{nom_bare} en {month_fr.lower()} : est-ce une bonne période ?"
    faq_a1 = (f"{'Oui, ' if score >= 7.5 else ''}{month_fr} est "
              f"{'une excellente période' if score >= 9 else 'une bonne période' if score >= 7.5 else 'une période correcte'} "
              f"({score:.1f}/10){'. Conditions optimales.' if score >= 9 else f'. {best_month} reste le meilleur mois ({best_score:.1f}/10).' if score < 8.5 else '.'}")
    faq_q2 = f"Que faire {prep} {nom_bare} en {month_fr.lower()} ?"
    faq_a2 = (f"Avec {m['tmax']}°C max et {m['sun_h']}h de soleil, "
              f"{'les activités de plein air sont recommandées.' if score >= 8 else 'concentrez-vous sur les sites culturels et la gastronomie locale.' if score >= 6 else 'privilégiez les musées et activités couvertes.'}")

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

    title = f"{nom_bare} en {month_fr.lower()} : météo, pluie ({m['rain_pct']}%) et faut-il partir ? [{YEAR}]"
    desc  = f"Météo {prep} {nom_bare} en {month_fr.lower()} : {m['tmax']}°C max, {m['rain_pct']}% de jours pluvieux, {m['sun_h']}h de soleil/jour. Score {score:.1f}/10. Données 10 ans Open-Meteo."

    html = f'''<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1.0"/>
{GTAG}
<title>{title}</title>
<meta name="description" content="{desc}"/>
<link rel="canonical" href="https://bestdateweather.com/{slug}-meteo-{month_url}.html"/>
<meta property="og:type" content="article"/>
<meta property="og:title" content="Météo {prep} {nom_bare} en {month_fr.lower()} — {m['tmax']}°C, {m['rain_pct']}% pluie"/>
<meta property="og:description" content="{desc}"/>
<meta property="og:url" content="https://bestdateweather.com/{slug}-meteo-{month_url}.html"/>
<script type="application/ld+json">{article_schema}</script>
<script type="application/ld+json">{faq_schema}</script>
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
 <h1 class="hero-title">Météo <em>{prep} {nom_bare}</em><br/>en {month_fr.lower()}</h1>
 <p class="hero-sub">{hero_sub}</p>
 <div class="kicker">Open-Meteo · 10 ans · {lat:.2f}°N {abs(lon):.2f}°{"E" if lon >= 0 else "W"}</div>
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
 <p style="font-size:14px;line-height:1.8;color:var(--slate)">En {month_fr.lower()}, {nom_bare} affiche {m['tmax']}°C max. {"Peu de pluie (" + str(m['rain_pct']) + "% des jours) — météo généralement favorable." if m['rain_pct'] <= 20 else "Risque modéré de pluie (" + str(m['rain_pct']) + "% des jours) — prévoir un imperméable." if m['rain_pct'] <= 40 else "Mois pluvieux (" + str(m['rain_pct']) + "% des jours) — privilégiez les activités couvertes."} Ensoleillement moyen : {m['sun_h']}h.</p>
 </section>

 <section class="section">
 <div class="section-label">Naviguer par mois</div>
 <h2 class="section-title">Tous les mois {prep} {nom_bare}</h2>
 <div class="month-nav">{month_nav}</div>
 </section>

 <section class="section">
 <div class="section-label">Tableau annuel</div>
 <h2 class="section-title">Comparaison mois par mois</h2>
 <div class="climate-table-wrap">
 <table class="climate-table" aria-label="Tableau climat mensuel {nom_bare}">
 <thead><tr><th>Mois</th><th>T° min</th><th>T° max</th><th>Pluie %</th><th>Précip. mm</th><th>Soleil h/j</th><th>Score</th></tr></thead>
 <tbody>{table_rows}</tbody>
 </table>
 </div>
 <div class="table-legend">
 <span><span class="legend-dot" style="background:#1a7a4a"></span>Idéal</span>
 <span><span class="legend-dot" style="background:#d97706"></span>Acceptable</span>
 <span><span class="legend-dot" style="background:#dc2626"></span>Hors saison</span>
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

    dests, climate, cards, overrides = load_data()

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
            html = gen_annual(dest, months, dest_cards)
            out  = f"{OUT}/meilleure-periode-{slug}.html"
            if not dry_run:
                open(out, 'w', encoding='utf-8').write(html)
            total_annual += 1
        except Exception as e:
            errors_gen.append(f"{slug}/annual: {e}")

        # 12 monthly fiches
        for mi in range(12):
            try:
                html = gen_monthly(dest, months, mi)
                out  = f"{OUT}/{slug}-meteo-{MONTH_URL[mi]}.html"
                if not dry_run:
                    open(out, 'w', encoding='utf-8').write(html)
                total_monthly += 1
            except Exception as e:
                errors_gen.append(f"{slug}/{MONTHS_FR[mi]}: {e}")

        if not dry_run:
            print(f"✓ {slug}: 1 fiche annuelle + 12 fiches mensuelles")

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
