#!/usr/bin/env python3
"""
generate_pages.py — BestDateWeather unified page generator
============================================================
Generates all destination pages (annual + monthly) for FR or EN.

Usage:
  python3 generate_pages.py --lang fr              # all FR pages
  python3 generate_pages.py --lang en              # all EN pages
  python3 generate_pages.py --lang fr paris        # one destination FR
  python3 generate_pages.py --lang en --dry-run    # EN simulation
  python3 generate_pages.py --lang fr --validate-only

Replaces generate_all.py and generate_all_en.py.
"""

import csv, re, os, sys, json, glob
from datetime import date
from lib.common import (score_badge as _score_badge, best_months as _best_months,
                        budget_tier as _budget_tier, seasonal_stats as _seasonal_stats,
                        bar_chart, climate_table_html as _climate_table_html,
                        weather_emoji, LANG_FR, LANG_EN)
from lib.page_config import (build_config, dest_name, dest_name_full, dest_slug,
                              dest_country, annual_url, monthly_url,
                              annual_url_cross, monthly_url_cross, hero_sub as _hero_sub,
                              pillar_url, MONTH_URL, MONTH_URL_FR,
                              SEASON_ICONS, TODAY, YEAR)

# ── PATHS ───────────────────────────────────────────────────────────────────
DIR  = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(DIR, 'data')


def _bind_lang(cfg):
    """Bind shared functions to the selected language."""
    L = LANG_FR if cfg['is_fr'] else LANG_EN
    return {
        'score_badge': lambda s, c=None: _score_badge(s, c, L=L),
        'best_months': lambda m: _best_months(m, L=L),
        'budget_tier': lambda s, a: _budget_tier(s, a, L=L),
        'seasonal_stats': lambda m: _seasonal_stats(m, L=L),
        'climate_table_html': lambda m, n, mtn=False: _climate_table_html(m, n, mtn, L=L),
    }


# ── COMPARISON PAIRS ────────────────────────────────────────────────────────

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


def build_comparison_index(cfg, all_dests=None):
    """Build reverse index for comparison links."""
    if cfg['is_fr']:
        idx = {}
        for a, b in COMPARISON_PAIRS:
            idx.setdefault(a, []).append((b, f"{a}-ou-{b}-climat.html"))
            idx.setdefault(b, []).append((a, f"{a}-ou-{b}-climat.html"))
        return idx
    else:
        out_dir = os.path.join(DIR, 'en')
        idx = {}
        for f in glob.glob(os.path.join(out_dir, '*-vs-*-weather.html')):
            fname = os.path.basename(f)
            parts = fname.replace('-weather.html', '').split('-vs-')
            if len(parts) == 2:
                a, b = parts
                idx.setdefault(a, []).append((b, fname))
                idx.setdefault(b, []).append((a, fname))
        return idx


# ── DATA LOADING ────────────────────────────────────────────────────────────

def load_data(cfg):
    """Load destinations, climate, cards, overrides, events."""
    dests = {}
    for row in csv.DictReader(open(f'{DATA}/destinations.csv', encoding='utf-8-sig')):
        dests[row['slug_fr']] = row

    climate = {}
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

    cards_file = f'{DATA}/{cfg["cards_file"]}'
    cards = {}
    if os.path.exists(cards_file):
        for row in csv.DictReader(open(cards_file, encoding='utf-8-sig')):
            cards.setdefault(row['slug'], []).append(row)

    overrides = {}
    ov_path = f'{DATA}/overrides.csv'
    if os.path.exists(ov_path):
        for row in csv.DictReader(open(ov_path, encoding='utf-8-sig')):
            key = (row['slug'], int(row['mois_num']) - 1, row['champ'])
            overrides[key] = row['valeur']
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
                    print(f"[WARN] Invalid override: {slug}/{mi}/{champ}={val}")

    events = {}
    events_path = f'{DATA}/events.csv'
    if os.path.exists(events_path):
        for row in csv.DictReader(open(events_path, encoding='utf-8-sig')):
            events[(row['slug'], int(row['month']))] = {
                'fr': row['event_fr'], 'en': row['event_en'],
            }

    return dests, climate, cards, overrides, events


# ── VALIDATION ──────────────────────────────────────────────────────────────

def validate(cfg, dests, climate, cards=None):
    """Validate data consistency. Returns list of errors."""
    errors = []
    MONTHS = cfg['months']

    for slug, months_data in climate.items():
        if None in months_data:
            missing = [MONTHS[i] for i, m in enumerate(months_data) if m is None]
            errors.append(cfg['val_missing_months'].format(slug=slug, missing=', '.join(missing)))
            continue
        for i, m in enumerate(months_data):
            if not (0.0 <= m['score'] <= 10.0):
                errors.append(cfg['val_score_range'].format(slug=slug, month=MONTHS[i], score=m['score']))

    for slug in dests:
        if slug not in climate:
            errors.append(cfg['val_no_climate'].format(slug=slug))

    return errors


# ── SIMILARITY ──────────────────────────────────────────────────────────────

def compute_all_similarities(dests, climate):
    """Compute similarity scores between all destinations."""
    profiles = {}
    for slug in dests:
        if slug not in climate or None in climate[slug]:
            continue
        months = climate[slug]
        profiles[slug] = [m['tmax'] for m in months] + [m['rain_pct'] for m in months] + [m['sun_h'] for m in months]

    import math
    def cos_sim(a, b):
        dot = sum(x * y for x, y in zip(a, b))
        na = math.sqrt(sum(x * x for x in a))
        nb = math.sqrt(sum(x * x for x in b))
        return dot / (na * nb) if na and nb else 0

    similarities = {}
    slugs = list(profiles.keys())
    for i, s1 in enumerate(slugs):
        sims = []
        for j, s2 in enumerate(slugs):
            if i == j:
                continue
            sims.append((cos_sim(profiles[s1], profiles[s2]), s2))
        sims.sort(reverse=True)
        similarities[s1] = sims[:5]
    return similarities


# ── HTML CONSTANTS ──────────────────────────────────────────────────────────

GTAG = '''<script async src="https://www.googletagmanager.com/gtag/js?id=G-NTCJTDPSJL"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}gtag("js",new Date());gtag("config","G-NTCJTDPSJL");</script>'''

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





def head_css(cfg):
    pfx = cfg['asset_prefix']
    return f'''<link rel="preconnect" href="https://fonts.googleapis.com"/>
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin/>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700;900&family=DM+Sans:wght@300;400;500;600;700&display=swap"/>
<link rel="stylesheet" href="{pfx}style.css"/>
<link rel="icon" type="image/x-icon" href="{pfx}favicon.ico"/>
<link rel="apple-touch-icon" sizes="180x180" href="{pfx}apple-touch-icon.png"/>
<meta name="theme-color" content="#1a1f2e"/>'''


def nav_html(cfg):
    pfx = cfg['asset_prefix']
    if cfg['is_fr']:
        return f'''<nav>
 <a class="nav-brand" href="{pfx}index.html">Best<em>Date</em>Weather</a>
 <div class="nav-actions">
  <button class="nav-share" onclick="shareThis()" aria-label="Partager"><svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><path d="M8.59 13.51l6.83 3.98M15.41 6.51l-6.82 3.98"/></svg></button>
  <a class="nav-cta" href="{pfx}index.html">Tester l'application</a>
 </div>
</nav>'''
    else:
        return f'''<nav>
 <a class="nav-brand" href="app.html">Best<em>Date</em>Weather</a>
 <div class="nav-actions">
  <button class="nav-share" onclick="shareThis()" aria-label="Share"><svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><path d="M8.59 13.51l6.83 3.98M15.41 6.51l-6.82 3.98"/></svg></button>
  <a class="nav-cta" href="app.html">Try the weather app</a>
 </div>
</nav>'''


def footer_html(cfg, dest):
    """Generate footer with language toggle."""
    fc = cfg['footer']
    pfx = cfg['asset_prefix']
    slug_fr = dest['slug_fr']
    slug_en = dest['slug_en']

    if cfg['is_fr']:
        alt_link = f' · <a href="en/best-time-to-visit-{slug_en}.html" class="txt-muted"><img src="flags/gb.png" width="20" height="15" alt="" class="flag-icon-lg"> English</a>'
    else:
        alt_link = f' · <a href="../meilleure-periode-{slug_fr}.html" class="txt-muted"><img src="../flags/fr.png" width="20" height="15" alt="" class="flag-icon-lg"> Français</a>'

    meth_url, meth_label = fc['methodology']
    app_url, app_label = fc['app']
    about_url, about_label = fc['about']
    faq_url, faq_label = fc['faq']
    legal_url, legal_label = fc['legal']
    priv_url, priv_label = fc['privacy']

    return f'''<footer>
 <p class="txt-muted-label">bestdateweather.com</p>
 <p><a href="https://open-meteo.com/" rel="noopener" class="txt-muted">{fc['data_by']}</a> · {fc['sources']}</p>
 <p class="mt-8"><a href="{meth_url}" class="txt-muted">{meth_label}</a> · <a href="{about_url}" class="txt-muted">{about_label}</a> · <a href="{faq_url}" class="txt-muted">{faq_label}</a> · <a href="{app_url}" class="txt-muted">{app_label}</a>{alt_link}</p>
 <p class="f11-muted"><a href="{legal_url}" class="txt-muted">{legal_label}</a> · <a href="{priv_url}" class="txt-muted">{priv_label}</a> · <a href="contact.html" class="txt-muted">Contact</a></p>
</footer>
<script>function shareThis(){{if(navigator.share)navigator.share({{title:document.title,url:location.href}});else{{navigator.clipboard.writeText(location.href);var b=document.querySelector('.nav-share');b.style.color='#27ae60';setTimeout(function(){{b.style.color=''}},1200)}}}}</script>'''


# ── ANNUAL PAGE GENERATOR ──────────────────────────────────────────────────

def gen_annual(cfg, fn, dest, months, dest_cards, all_dests, similarities, comparison_index=None):
    C = cfg
    MONTHS = C['months']
    slug_fr = dest['slug_fr']
    slug_en = dest['slug_en']
    slug    = dest_slug(C, dest)
    nom     = dest_name(C, dest)
    nom_f   = dest_name_full(C, dest)  # "à Paris" (FR) or "Paris" (EN)
    country = dest_country(C, dest)
    flag    = dest['flag']
    lat     = float(dest['lat'])
    lon     = float(dest['lon'])
    pfx     = C['asset_prefix']
    booking_id = dest['booking_dest_id']

    bests      = fn['best_months'](months)
    best_str   = ' & '.join(bests[:2]) if len(bests) >= 2 else bests[0]
    best_score = max(m['score'] for m in months)
    best_idx   = next(i for i, m in enumerate(months) if m['score'] == best_score)
    best_m     = months[best_idx]
    seas       = fn['seasonal_stats'](months)
    all_scores = [m['score'] for m in months]
    best_rain  = best_m['rain_pct']
    best_tmax  = best_m['tmax']
    is_mountain = dest.get('mountain', 'False').strip() == 'True'
    worst_idx  = min(range(12), key=lambda i: months[i]['score'])
    worst_rain = months[worst_idx]['rain_pct']

    # ── Title & description (3 variants each) ──
    title_var = hash(slug_fr) % 3
    desc_var  = hash(slug_fr + 'desc') % 3

    if C['is_fr']:
        prep = dest.get('prep', 'à')
        nom_bare = dest.get('nom_bare', slug_fr)
        if title_var == 0:
            title = f"Meilleure période pour partir {prep} {nom_bare} [{YEAR}] — Météo & conseils"
            h1_text = f"Meilleure période pour partir<br/><em>{prep} {nom_bare}</em>"
        elif title_var == 1:
            title = f"Quand partir {prep} {nom_bare} ? Climat mois par mois [{YEAR}]"
            h1_text = f"Quand partir<br/><em>{prep} {nom_bare}</em> ?"
        else:
            title = f"{nom_bare} : meilleure saison pour voyager [{YEAR}] — Climat & météo"
            h1_text = f"<em>{nom_bare}</em><br/>quelle saison choisir ?"
        if desc_var == 0:
            desc = (f"Quelle est la meilleure période pour visiter {nom_bare} ? "
                    f"{MONTHS[best_idx]} offre {best_tmax}°C et {best_rain}% de jours pluvieux. "
                    f"Score météo : {best_score}/10. Données 10 ans Open-Meteo.")
        elif desc_var == 1:
            desc = (f"Quand partir {prep} {nom_bare} ? {MONTHS[best_idx]} est le meilleur mois "
                    f"({best_score}/10) avec {best_tmax}°C. Analyse complète des 12 mois sur 10 ans de données.")
        else:
            desc = (f"{nom_bare} en {MONTHS[best_idx].lower()} : {best_tmax}°C, {best_rain}% de pluie, "
                    f"score {best_score}/10. Découvrez le meilleur moment pour partir — données météo 10 ans.")
        og_title = f"Meilleure période {prep} {nom_bare} — météo &amp; conseils"
    else:
        if title_var == 0:
            title = f"Best Time to Visit {nom} [{YEAR}] — Weather & Tips"
            h1_text = f"Best Time to Visit<br/><em>{nom}</em>"
        elif title_var == 1:
            title = f"When to Visit {nom}? Month-by-Month Climate [{YEAR}]"
            h1_text = f"When to Visit<br/><em>{nom}</em>?"
        else:
            title = f"{nom}: Best Season to Travel [{YEAR}] — Climate & Weather"
            h1_text = f"<em>{nom}</em><br/>Which Season to Choose?"
        if desc_var == 0:
            desc = (f"When is the best time to visit {nom}? "
                    f"{MONTHS[best_idx]} offers {best_tmax}°C and {best_rain}% rainy days. "
                    f"Weather score: {best_score}/10. 10-year Open-Meteo data.")
        elif desc_var == 1:
            desc = (f"When to visit {nom}? {MONTHS[best_idx]} is the best month "
                    f"({best_score}/10) with {best_tmax}°C. Full 12-month analysis based on 10 years of data.")
        else:
            desc = (f"{nom} in {MONTHS[best_idx]}: {best_tmax}°C, {best_rain}% rain, "
                    f"score {best_score}/10. Find the best time to go — 10-year weather data.")
        og_title = f"Best time to visit {nom} — weather &amp; tips"

    # ── Climate table ──
    table_html = fn['climate_table_html'](months, nom, is_mountain)
    hsub = _hero_sub(C, dest)

    # ── Quick facts ──
    qf = f'''<section class="section">
 <div class="section-label">{C['lbl_quick_section']}</div>
 <h2 class="section-title">{C['lbl_quick_title_tpl'].format(name=nom_f)}</h2>
 <div class="quick-facts">
 <div class="quick-facts-row"><div class="qf-label">{C['lbl_best_overall']}</div><div class="qf-value"><strong>{MONTHS[best_idx]}</strong></div></div>
 <div class="quick-facts-row"><div class="qf-label">{C['lbl_optimal_temp']}</div><div class="qf-value"><strong>{best_m["tmin"]}–{best_m["tmax"]}°C</strong> {C['lbl_in']} {MONTHS[best_idx].lower() if C['is_fr'] else MONTHS[best_idx]}</div></div>
 <div class="quick-facts-row"><div class="qf-label">{C['lbl_least_rain']}</div><div class="qf-value"><strong>{best_rain}%</strong> {C['lbl_rainy_days_in']} {MONTHS[best_idx].lower() if C['is_fr'] else MONTHS[best_idx]}</div></div>
 <div class="quick-facts-row"><div class="qf-label">{C['lbl_wettest']}</div><div class="qf-value"><strong>{MONTHS[worst_idx]}</strong> ({worst_rain}%)</div></div>
 <div class="quick-facts-row"><div class="qf-label">{C['lbl_best_score']}</div><div class="qf-value"><strong>{best_score}/10</strong></div></div>
 </div>
</section>'''

    # ── Cards section ──
    tk, xk = C['card_title_key'], C['card_text_key']
    cards_html = '\n'.join(
        f'<div class="project-card"><span class="proj-icon">{c["icon"]}</span>'
        f'<span class="proj-title">{c[tk]}</span>'
        f'<span class="proj-text">{c[xk]}</span></div>'
        for c in dest_cards
    )
    cards_section = f'''<section class="section">
 <div class="section-label">{C['lbl_cards_section']}</div>
 <h2 class="section-title">{C['lbl_cards_title']}</h2>
 <div class="project-grid">{cards_html}</div>
</section>''' if dest_cards else ''

    # ── Climate table section ──
    table_section = f'''<section class="section">
 <div class="section-label">{C['lbl_table_section']}</div>
 <h2 class="section-title">{C['lbl_table_title_tpl'].format(name=nom_f)}</h2>
 {table_html}
</section>'''

    # ── Seasonal analysis ──
    season_rows = ''
    for sname in C['season_order']:
        s = seas[sname]
        icon = SEASON_ICONS[sname]
        mrange = C['season_range'][sname]
        season_rows += (f'<h3 class="sub-title">{icon} {sname} ({mrange}) — {s["verdict"]}</h3>'
                        f'<p>{C["lbl_season_temp_tpl"].format(tmax=s["tmax"], rain=s["rain_pct"], sun=s["sun_h"], score=s["score"])}</p>\n')
    seasonal_section = f'''<section class="section">
 <div class="section-label">{C['lbl_season_section']}</div>
 <h2 class="section-title">{C['lbl_season_title']}</h2>
 {season_rows}
</section>'''

    # ── Booking ──
    booking_section = ''
    if booking_id:
        booking_url = (f"https://www.booking.com/{C['booking_domain']}?ss={nom}"
                       f"&dest_id={booking_id}&dest_type=city"
                       f"&checkin={YEAR}-{best_idx+1:02d}-01&checkout={YEAR}-{best_idx+1:02d}-07"
                       f"&group_adults=2&no_rooms=1&lang={C['booking_lang']}")
        off_months = [MONTHS[i].lower() if C['is_fr'] else MONTHS[i]
                      for i in range(12) if months[i]['score'] >= 6.5 and months[i]['score'] < best_score - 1.5]
        if off_months:
            verb = C['lbl_offer_pl'] if len(off_months[:2]) > 1 else C['lbl_offer_sg']
            budget_tip = f"{C['lbl_tip_prefix']} : {C['lbl_tip_good_tpl'].format(months=', '.join(off_months[:2]), verb=verb)}"
        else:
            m1 = MONTHS[worst_idx].lower() if C['is_fr'] else MONTHS[worst_idx]
            m2 = MONTHS[(worst_idx+1)%12].lower() if C['is_fr'] else MONTHS[(worst_idx+1)%12]
            budget_tip = f"{C['lbl_tip_prefix']} : {C['lbl_tip_offpeak_tpl'].format(m1=m1, m2=m2)}"
        booking_section = f'''<section class="section">
 <div class="section-label">{C['lbl_booking_section']}</div>
 <h2 class="section-title">{C['lbl_booking_title_tpl'].format(name=nom_f)}</h2>
 <div class="affil-box">
 <strong>{C['lbl_booking_cta']}</strong>
 <p>{budget_tip}</p>
 <a href="{booking_url}" target="_blank" rel="sponsored noopener" class="affil-btn">{C['lbl_booking_btn']}</a>
 </div>
</section>'''

    # ── Monthly navigation ──
    MONTH_BTN_CLS = {'rec': 'month-btn-rec', 'mid': 'month-btn-mid', 'avoid': 'month-btn-avoid'}
    monthly_links = ''.join(
        f'<a href="{monthly_url(C, slug, i)}" class="month-btn '
        f'{MONTH_BTN_CLS.get(months[i]["classe"], "month-btn-mid")}">'
        f'<div class="fw700-f13">{MONTHS[i]}</div>'
        f'</a>'
        for i in range(12)
    )
    monthly_section = f'''<section class="section">
 <div class="section-label">{C['lbl_monthly_section']}</div>
 <h2 class="section-title">{C['lbl_monthly_title']}</h2>
 <div class="grid-months">
 {monthly_links}
 </div>
</section>'''

    # ── FAQ ──
    winter_key = 'Hiver' if C['is_fr'] else 'Winter'
    if is_mountain:
        from scoring import compute_ski_score
        best_ski_idx = max(range(12), key=lambda i: compute_ski_score(months[i]['tmax'], months[i]['rain_pct'], months[i]['sun_h']))
        best_ski_score = f"{compute_ski_score(months[best_ski_idx]['tmax'], months[best_ski_idx]['rain_pct'], months[best_ski_idx]['sun_h']):.1f}"
        winter_months_ski = [compute_ski_score(months[i]['tmax'], months[i]['rain_pct'], months[i]['sun_h']) for i in (11, 0, 1)]
        winter_ski_avg = f"{sum(winter_months_ski)/3:.1f}"
        if C['is_fr']:
            faq_items = [
                (f"Quelle est la meilleure période pour partir {dest.get('prep','à')} {dest.get('nom_bare',slug_fr)} ?",
                 f"Ça dépend de l'activité. Pour le ski : {MONTHS[best_ski_idx].lower()} "
                 f"(score ski {best_ski_score}/10). Pour la randonnée/été : {MONTHS[best_idx].lower()} "
                 f"({best_score}/10, {best_tmax}°C)."),
                (f"Peut-on skier {dest.get('prep','à')} {dest.get('nom_bare',slug_fr)} en hiver ?",
                 f"Oui, c'est la pleine saison. Score ski moyen décembre-février : {winter_ski_avg}/10. "
                 f"Températures froides ({months[0]['tmax']}°C max en janvier) et neige fréquente."),
                (f"Fait-il chaud {dest.get('prep','à')} {dest.get('nom_bare',slug_fr)} en été ?",
                 f"En {MONTHS[best_idx].lower()}, il fait {best_tmax}°C en moyenne. Idéal pour la randonnée et les activités outdoor."),
                (f"Quel est le mois le plus pluvieux {dest.get('prep','à')} {dest.get('nom_bare',slug_fr)} ?",
                 f"{MONTHS[worst_idx]} est le mois le plus pluvieux avec {worst_rain}% de jours de pluie."),
            ]
        else:
            faq_items = [
                (f"When is the best time to visit {nom}?",
                 f"It depends on the activity. For skiing: {MONTHS[best_ski_idx]} "
                 f"(ski score {best_ski_score}/10). For hiking/summer: {MONTHS[best_idx]} "
                 f"({best_score}/10, {best_tmax}°C)."),
                (f"Can you ski in {nom} in winter?",
                 f"Yes, it's peak ski season. Average ski score December–February: {winter_ski_avg}/10. "
                 f"Cold temperatures ({months[0]['tmax']}°C max in January) and frequent snowfall."),
                (f"Is it warm in {nom} in summer?",
                 f"In {MONTHS[best_idx]}, temperatures average {best_tmax}°C. Ideal for hiking and outdoor activities."),
                (f"What is the wettest month in {nom}?",
                 f"{MONTHS[worst_idx]} is the wettest month with {worst_rain}% rainy days."),
            ]
    else:
        if C['is_fr']:
            prep = dest.get('prep', 'à')
            nb = dest.get('nom_bare', slug_fr)
            faq_items = [
                (f"Quelle est la meilleure période pour partir {prep} {nb} ?",
                 f"{MONTHS[best_idx]} est idéal avec {best_rain}% de jours pluvieux et {best_tmax}°C. "
                 f"{'La période ' + ' & '.join(bests[:2]) + ' offre des conditions comparables.' if len(bests) > 1 else ''}"),
                (f"Quel est le mois le plus pluvieux {prep} {nb} ?",
                 f"{MONTHS[worst_idx]} est le mois le plus pluvieux avec {worst_rain}% de jours de pluie."),
                (f"Fait-il chaud {prep} {nb} en {MONTHS[best_idx].lower()} ?",
                 f"Oui, {MONTHS[best_idx].lower()} est le meilleur mois avec {best_tmax}°C en moyenne."),
                (f"Peut-on partir {prep} {nb} en hiver ?",
                 f"En hiver, le score moyen est {seas[winter_key]['score']}/10. "
                 f"{'Conditions acceptables pour les visites culturelles.' if seas[winter_key]['score'] >= 5.5 else 'Période difficile — préférez la haute saison.'}"),
            ]
        else:
            faq_items = [
                (f"When is the best time to visit {nom}?",
                 f"{MONTHS[best_idx]} is ideal with {best_rain}% rainy days and {best_tmax}°C. "
                 f"{'The months of ' + ' & '.join(bests[:2]) + ' offer comparable conditions.' if len(bests) > 1 else ''}"),
                (f"What is the wettest month in {nom}?",
                 f"{MONTHS[worst_idx]} is the wettest month with {worst_rain}% rainy days."),
                (f"Is it hot in {nom} in {MONTHS[best_idx]}?",
                 f"Yes, {MONTHS[best_idx]} is the best month with an average of {best_tmax}°C."),
                (f"Can you visit {nom} in winter?",
                 f"In winter, the average score is {seas[winter_key]['score']}/10. "
                 f"{'Acceptable conditions for cultural visits.' if seas[winter_key]['score'] >= 5.5 else 'Difficult period — prefer the peak season.'}"),
            ]

    faq_html = '<div class="faq-list">' + ''.join(
        f'<div class="faq-item"><button class="faq-q" onclick="toggleFaq(this)">'
        f'{q}<span class="faq-icon">+</span></button>'
        f'<div class="faq-a">{a}</div></div>'
        for q, a in faq_items
    ) + '</div>'
    faq_schema = json.dumps({
        "@context": "https://schema.org", "@type": "FAQPage",
        "mainEntity": [{"@type": "Question", "name": q,
                        "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq_items]
    }, ensure_ascii=False)
    faq_section = f'''<section class="section">
 <div class="section-label">FAQ</div>
 <h2 class="section-title">{C['lbl_faq_title']}</h2>
 {faq_html}
</section>'''

    # ── Similar destinations ──
    similar_section = ''
    sim_list = (similarities or {}).get(slug_fr, [])
    if sim_list and all_dests:
        sim_cards = ''
        for sim_score, sim_slug in sim_list[:3]:
            sd = all_dests.get(sim_slug, {})
            sn = dest_name(C, sd) if sd else sim_slug
            sc = dest_country(C, sd) if sd else ''
            sf = sd.get('flag', '')
            s_slug = dest_slug(C, sd) if sd else sim_slug
            sim_cards += (
                f'<a href="{annual_url(C, s_slug)}" class="sim-card">'
                f'<div class="f13-slate3"><img src="{pfx}flags/{sf}.png" width="16" height="12" '
                f'alt="{sf}" class="flag-icon">{sc}</div>'
                f'<div class="fw700-navy">{sn}</div>'
                f'<div class="f12-slate2">{C["lbl_similar_match"].format(pct=f"{sim_score:.0%}")}</div>'
                f'</a>')
        similar_section = f'''<section class="section">
 <div class="section-label">{C['lbl_similar_section']}</div>
 <h2 class="section-title">{C['lbl_similar_title']}</h2>
 <div class="flex-wrap-14">{sim_cards}</div>
</section>'''

    # ── Rankings ──
    rank_links = ''.join(f'<a href="{url}" class="link-card">{label}</a>' for url, label in C['rankings'])
    ranking_section = f'''<section class="section">
 <div class="section-label">{C['lbl_ranking_section']}</div>
 <h2 class="section-title">{C['lbl_ranking_title']}</h2>
 <div class="flex-wrap-14">{rank_links}</div>
</section>'''

    # ── Pillar + comparison ──
    pillar_comp_cards = []
    best_month_name = MONTHS[best_idx]
    pillar_comp_cards.append(
        f'<a href="{pillar_url(C, best_idx)}" class="link-card">'
        f'{C["lbl_pillar_tpl"].format(month=best_month_name.lower() if C["is_fr"] else best_month_name)}</a>')
    comp_slug = slug_fr if C['is_fr'] else slug_en
    if comparison_index and comp_slug in comparison_index:
        for other_slug, comp_file in comparison_index[comp_slug][:3]:
            if C['is_fr']:
                other_nom = all_dests.get(other_slug, {}).get('nom_bare', other_slug)
            else:
                other_nom = other_slug
                for d in all_dests.values():
                    if d.get('slug_en') == other_slug:
                        other_nom = d.get('nom_en', d.get('nom_bare', other_slug))
                        break
            pillar_comp_cards.append(
                f'<a href="{comp_file}" class="link-card">'
                f'{C["lbl_vs_tpl"].format(a=nom, b=other_nom)}</a>')
    pillar_comparison_section = f'''<section class="section">
 <div class="section-label">{C['lbl_guides_section']}</div>
 <h2 class="section-title">{C['lbl_guides_title']}</h2>
 <div class="flex-wrap-14">{"".join(pillar_comp_cards)}</div>
</section>'''

    # ── Schema.org ──
    canonical = f"{C['canonical_prefix']}{annual_url(C, slug)}"
    hreflang_fr = f"https://bestdateweather.com/meilleure-periode-{slug_fr}.html"
    hreflang_en = f"https://bestdateweather.com/en/best-time-to-visit-{slug_en}.html"

    if C['is_fr']:
        headline = f"Meilleure période pour partir {dest.get('prep','à')} {dest.get('nom_bare',slug_fr)}"
    else:
        headline = f"Best Time to Visit {nom}"

    article_schema = json.dumps({
        "@context": "https://schema.org", "@type": "Article",
        "headline": headline, "description": desc,
        "author": {"@type": "Organization", "name": "BestDateWeather"},
        "publisher": {"@type": "Organization", "name": "BestDateWeather"},
        "dateModified": TODAY,
        **({"inLanguage": "en"} if not C['is_fr'] else {}),
        "mainEntityOfPage": {"@type": "WebPage", "@id": canonical}
    }, ensure_ascii=False)

    breadcrumb_schema = json.dumps({
        "@context": "https://schema.org", "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": C['lbl_breadcrumb_home'], "item": C['schema_home_url']},
            {"@type": "ListItem", "position": 2, "name": nom, "item": canonical}
        ]
    }, ensure_ascii=False)

    if C['is_fr']:
        ds_name = f"Données climatiques de {nom} — moyennes mensuelles sur 10 ans"
        ds_desc = f"Températures, précipitations, ensoleillement et vent mensuels {nom_f}. Moyennes calculées sur 10 ans de données ERA5 (Open-Meteo)."
    else:
        ds_name = f"Climate data for {nom} — monthly averages over 10 years"
        ds_desc = f"Monthly temperatures, precipitation, sunshine and wind for {nom}. Averages computed from 10 years of ERA5 data (Open-Meteo)."

    dataset_schema = json.dumps({
        "@context": "https://schema.org", "@type": "Dataset",
        "name": ds_name, "description": ds_desc,
        "temporalCoverage": "2015/2024",
        "spatialCoverage": {"@type": "Place", "name": nom},
        "creator": {"@type": "Organization", "name": "BestDateWeather", "url": "https://bestdateweather.com"},
        "license": "https://creativecommons.org/licenses/by-nc/4.0/",
        **({"inLanguage": "en"} if not C['is_fr'] else {}),
        "variableMeasured": ["Temperature", "Precipitation", "Sunshine hours", "Wind speed"]
    }, ensure_ascii=False)

    # ── Hero stats ──
    if C['is_fr']:
        best_months_lbl = f"Meilleur{'s mois' if len(bests) > 1 else ' mois'}"
        updated_date = f"{MONTHS[date.today().month - 1]} {date.today().year}"
    else:
        best_months_lbl = f"Best month{'s' if len(bests) > 1 else ''}"
        updated_date = date.today().strftime("%B %Y")

    coords = f"{lat}°N {abs(lon)}°{'E' if lon >= 0 else 'W'}"
    kicker = C['lbl_updated_tpl'].format(date=updated_date, coords=coords)

    # ── HTML ASSEMBLY ──
    html = f'''<!DOCTYPE html>
<html lang="{C['html_lang']}">
<head>
<!-- SCORING: generate_pages.py | lang={C['lang']} | slug={slug_fr} | tropical={dest["tropical"]} | generated={TODAY} -->
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1.0"/>
{GTAG}
<title>{title}</title>
<meta name="description" content="{desc}"/>
<link rel="canonical" href="{canonical}"/>
<link rel="alternate" hreflang="fr" href="{hreflang_fr}"/>
<link rel="alternate" hreflang="en" href="{hreflang_en}"/>
<link rel="alternate" hreflang="x-default" href="{hreflang_en}"/>
<meta property="og:type" content="article"/>
<meta property="og:title" content="{og_title}"/>
<meta property="og:description" content="{desc}"/>
<meta property="og:url" content="{canonical}"/>
<script type="application/ld+json">{article_schema}</script>
<script type="application/ld+json">{faq_schema}</script>
<script type="application/ld+json">{breadcrumb_schema}</script>
<script type="application/ld+json">{dataset_schema}</script>
{head_css(C)}
<style>
.hero-band{{background:linear-gradient(160deg,#0d1a3a 0%,#1a2a6a 55%,#2a4a9a 100%);}}
.hero-title em{{color:#93c5fd;}}
</style>
</head>
<body><script>window.scrollTo(0,0);</script>
{nav_html(C)}
<header class="hero-band">
 <div class="dest-tag"><img src="{pfx}flags/{flag}.png" width="20" height="15" alt="{flag.upper()}" class="flag-icon"> {nom}, {country}</div>
 <h1 class="hero-title">{h1_text}</h1>
 <p class="hero-sub">{hsub}</p>
 <div class="kicker">{kicker}</div>
 <div class="hero-stats mt-22">
 <div><span class="hstat-val">{best_str}</span><span class="hstat-lbl">{best_months_lbl}</span></div>
 <div><span class="hstat-val">{best_tmax}°C</span><span class="hstat-lbl">{C['lbl_optimal_temp_stat']}</span></div>
 <div><span class="hstat-val">{best_rain}%</span><span class="hstat-lbl">{C['lbl_rainy_days_stat']}</span></div>
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
{footer_html(C, dest)}
<script>
function toggleFaq(btn){{
  const a=btn.nextElementSibling;
  const opening=a.style.display!=="block";
  a.style.display=opening?"block":"none";
  btn.querySelector(".faq-icon").textContent=opening?"-":"+";
}}
</script>
</body>
</html>'''
    return html


# ── CONTEXT PARAGRAPH ──────────────────────────────────────────────────────

def context_paragraph(cfg, nom, nom_f, m, mi, score, best_month, best_score, is_tropical, event_text=None):
    """Generate a context paragraph per destination × month."""
    C = cfg
    MONTHS = C['months']
    month = MONTHS[mi]
    season_map = C['seasons_map']
    season = season_map[mi]
    tmax, rain, sun = m['tmax'], m['rain_pct'], m['sun_h']

    parts = []
    if event_text:
        parts.append(f"<strong>🎯 {event_text}</strong>")

    if C['is_fr']:
        season_summer, season_winter = 'Été', 'Hiver'
        season_spring, season_autumn = 'Printemps', 'Automne'
        ml = month.lower()
        if is_tropical and rain >= 50:
            parts.append(f"{month} correspond à la saison humide {nom_f}. Les averses, souvent brèves mais intenses, rythment les journées.")
        elif is_tropical and rain <= 20:
            parts.append(f"{month} tombe en pleine saison sèche {nom_f}. L'air est chaud et l'humidité plus supportable qu'en saison des pluies.")
        elif season == season_summer and tmax >= 30:
            parts.append(f"En plein été, {nom} connaît des températures élevées ({tmax}°C). La chaleur est un facteur à prendre en compte pour les activités en extérieur.")
        elif season == season_summer and tmax >= 22:
            parts.append(f"L'été {nom_f} offre des températures agréables ({tmax}°C) et de longues journées ensoleillées ({sun}h de soleil).")
        elif season == season_winter and tmax <= 10:
            parts.append(f"L'hiver {nom_f} est frais ({tmax}°C en journée). Les journées sont courtes ({sun}h de soleil) mais la ville se découvre sous un autre angle.")
        elif season == season_winter and tmax >= 20:
            parts.append(f"Même en hiver, {nom} affiche {tmax}°C. Un atout pour ceux qui fuient le froid européen.")
        elif season == season_spring:
            parts.append(f"Le printemps marque le début de la bonne saison {nom_f}. Les températures remontent ({tmax}°C) et les touristes ne sont pas encore là en masse.")
        elif season == season_autumn and score >= 7:
            parts.append(f"L'automne {nom_f} est souvent sous-estimé : {tmax}°C, lumière dorée et affluence en baisse. Une fenêtre intéressante.")
        elif season == season_autumn:
            parts.append(f"L'automne marque la fin de la haute saison {nom_f}. Les températures baissent ({tmax}°C) et la pluie revient ({rain}% des jours).")
        else:
            parts.append(f"En {ml}, {nom} affiche {tmax}°C en journée avec {sun}h de soleil par jour.")
        # Rain
        if rain <= 10:
            parts.append(f"La pluie est quasi absente ({rain}% des jours) — idéal pour planifier sans plan B.")
        elif rain <= 25:
            parts.append(f"Le risque de pluie reste faible ({rain}% des jours), ce qui laisse une bonne marge pour les activités extérieures.")
        elif rain <= 45:
            parts.append(f"Comptez {rain}% de jours avec pluie — un imperméable léger dans le sac est recommandé.")
        else:
            parts.append(f"Avec {rain}% de jours pluvieux, prévoyez systématiquement des alternatives couvertes.")
        # Best month comparison
        if score >= 9:
            parts.append(f"C'est l'un des meilleurs moments de l'année pour visiter {nom}.")
        elif score >= 7.5:
            parts.append(f"Un bon compromis entre météo et affluence, même si {best_month.lower()} ({best_score:.1f}/10) reste théoriquement meilleur.")
        elif score >= 5.5:
            parts.append(f"Pas le meilleur créneau, mais acceptable pour qui a des contraintes de dates. {best_month} ({best_score:.1f}/10) est nettement préférable si possible.")
    else:
        if is_tropical and rain >= 50:
            parts.append(f"{month} falls in the wet season in {nom}. Showers are often brief but intense.")
        elif is_tropical and rain <= 20:
            parts.append(f"{month} is peak dry season in {nom}. The air is warm and humidity more bearable than in the rainy season.")
        elif season == 'Summer' and tmax >= 30:
            parts.append(f"In the height of summer, {nom} sees high temperatures ({tmax}°C). Heat is a factor for outdoor activities.")
        elif season == 'Summer' and tmax >= 22:
            parts.append(f"Summer in {nom} brings pleasant temperatures ({tmax}°C) and long sunny days ({sun}h of sunshine).")
        elif season == 'Winter' and tmax <= 10:
            parts.append(f"Winter in {nom} is cool ({tmax}°C during the day). Days are short ({sun}h of sunshine) but the city reveals a different side.")
        elif season == 'Winter' and tmax >= 20:
            parts.append(f"Even in winter, {nom} enjoys {tmax}°C. A real asset for escaping the European cold.")
        elif season == 'Spring':
            parts.append(f"Spring marks the start of the good season in {nom}. Temperatures rise ({tmax}°C) and tourists have not yet arrived en masse.")
        elif season == 'Autumn' and score >= 7:
            parts.append(f"Autumn in {nom} is often underrated: {tmax}°C, golden light and declining crowds. An interesting window.")
        elif season == 'Autumn':
            parts.append(f"Autumn marks the end of peak season in {nom}. Temperatures drop ({tmax}°C) and rain returns ({rain}% of days).")
        else:
            parts.append(f"In {month}, {nom} sees {tmax}°C during the day with {sun}h of sunshine per day.")
        if rain <= 10:
            parts.append(f"Rain is virtually absent ({rain}% of days) — ideal for planning without a backup.")
        elif rain <= 25:
            parts.append(f"Rain risk remains low ({rain}% of days), leaving good room for outdoor activities.")
        elif rain <= 45:
            parts.append(f"Expect rain on {rain}% of days — a light raincoat in the bag is recommended.")
        else:
            parts.append(f"With {rain}% of rainy days, always have indoor alternatives planned.")
        if score >= 9:
            parts.append(f"This is one of the best times of year to visit {nom}.")
        elif score >= 7.5:
            parts.append(f"A good balance between weather and crowds, even if {best_month} ({best_score:.1f}/10) remains theoretically better.")
        elif score >= 5.5:
            parts.append(f"Not the best window, but acceptable if dates are constrained. {best_month} ({best_score:.1f}/10) is significantly better if possible.")

    return ' '.join(parts)


# ── HELPER: SIM CARDS ──────────────────────────────────────────────────────

def _build_sim_cards(cfg, sim_list, all_dests, climate_for_sim, mi):
    C = cfg
    MONTHS = C['months']
    parts = []
    for _, sim_slug in sim_list:
        sd = all_dests.get(sim_slug)
        if not sd:
            continue
        if sd.get('monthly', 'True').strip().lower() not in ('true', '1', 'yes', ''):
            continue
        sc = climate_for_sim.get(sim_slug, {})
        if C['is_fr']:
            url = f"{sim_slug}-meteo-{MONTH_URL_FR[mi]}.html"
            name = sd.get('nom_bare', sim_slug)
            pfx = 'flags/'
            lbl = f"{MONTHS[mi]} : {sc.get('score','?')}/10 · {sc.get('tmax','?')}°C"
        else:
            url = f"{sd.get('slug_en', sim_slug)}-weather-{MONTH_URL[mi]}.html"
            name = sd.get('nom_en', sd.get('nom_bare', sim_slug))
            pfx = '../flags/'
            lbl = f"{MONTHS[mi]}: {sc.get('score','?')}/10 · {sc.get('tmax','?')}°C"
        parts.append(
            f'<a href="{url}" class="sim-card-sm">'
            f'<div class="fw700-navy-f14">'
            f'<img src="{pfx}{sd.get("flag","")}.png" width="16" height="12" '
            f'alt="" class="flag-icon">'
            f'{name}</div>'
            f'<div class="f12-slate2">{lbl}</div>'
            f'</a>')
    return ''.join(parts)


def _build_comp_cards_monthly(cfg, slug, nom, comparison_index, all_dests):
    if not comparison_index or slug not in comparison_index:
        return ''
    cards = []
    for other_slug, comp_file in comparison_index[slug][:2]:
        if cfg['is_fr']:
            other_nom = all_dests.get(other_slug, {}).get('nom_bare', other_slug)
            label = f'⚖️ {nom} ou {other_nom} ?'
        else:
            other_nom = all_dests.get(other_slug, {}).get('nom_en', other_slug)
            label = f'⚖️ {nom} or {other_nom}?'
        cards.append(
            f'<a href="{comp_file}" class="link-card">'
            f'{label}</a>')
    return ''.join(cards)


# ── MONTHLY PAGE GENERATOR ────────────────────────────────────────────────

SEASONS_FR = ['Hiver','Hiver','Printemps','Printemps','Printemps','Été',
              'Été','Été','Automne','Automne','Automne','Hiver']
SEASONS_EN = ['Winter','Winter','Spring','Spring','Spring','Summer',
              'Summer','Summer','Autumn','Autumn','Autumn','Winter']

MONTHLY_GRAD = [
    'linear-gradient(160deg,#0d1a3a 0%,#1a2a6a 55%,#2a4a9a 100%)',
    'linear-gradient(160deg,#0d1a3a 0%,#1a2a6a 55%,#2a4a9a 100%)',
    'linear-gradient(160deg,#0a2a1a 0%,#1a4a2a 55%,#3a8a5a 100%)',
    'linear-gradient(160deg,#0a2a1a 0%,#1a4a2a 55%,#3a8a5a 100%)',
    'linear-gradient(160deg,#0a2a1a 0%,#1a4a2a 55%,#3a8a5a 100%)',
    'linear-gradient(160deg,#2a1a0a 0%,#6a3a1a 55%,#d97706 100%)',
    'linear-gradient(160deg,#2a1a0a 0%,#6a3a1a 55%,#d97706 100%)',
    'linear-gradient(160deg,#2a1a0a 0%,#6a3a1a 55%,#d97706 100%)',
    'linear-gradient(160deg,#1a1a0a 0%,#4a3a0a 55%,#8a6a2a 100%)',
    'linear-gradient(160deg,#1a1a0a 0%,#4a3a0a 55%,#8a6a2a 100%)',
    'linear-gradient(160deg,#1a1a0a 0%,#4a3a0a 55%,#8a6a2a 100%)',
    'linear-gradient(160deg,#0d1a3a 0%,#1a2a6a 55%,#2a4a9a 100%)',
]

MONTH_ABBR_FR = ['Jan','Fév','Mar','Avr','Mai','Jun','Jul','Aoû','Sep','Oct','Nov','Déc']
MONTH_ABBR_EN = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']


def gen_monthly(cfg, fn, dest, months, mi, all_dests, similarities, all_climate, events=None, comparison_index=None):
    C = cfg
    is_fr   = C['is_fr']
    MONTHS  = C['months']
    MABBR   = MONTH_ABBR_FR if is_fr else MONTH_ABBR_EN
    slug_fr = dest['slug_fr']
    slug_en = dest['slug_en']
    slug    = dest_slug(C, dest)
    nom     = dest_name(C, dest)
    nom_f   = dest_name_full(C, dest)
    flag    = dest['flag']
    lat     = float(dest['lat'])
    lon     = float(dest['lon'])
    pfx     = C['asset_prefix']

    m        = months[mi]
    score    = m['score']
    season   = (SEASONS_FR if is_fr else SEASONS_EN)[mi]
    month    = MONTHS[mi]
    month_url = MONTH_URL_FR[mi] if is_fr else MONTH_URL[mi]
    is_mountain = dest.get('mountain', 'False').strip() == 'True'

    all_scores = [mo['score'] for mo in months]
    best_idx   = max(range(12), key=lambda i: months[i]['score'])
    best_month = MONTHS[best_idx]
    best_score = months[best_idx]['score']

    eff_classe = m['classe']
    if is_mountain:
        from scoring import compute_ski_score, best_class
        ski_sc = compute_ski_score(m['tmax'], m['rain_pct'], m['sun_h'])
        eff_classe = best_class(m['classe'], ski_sc)
    bg, txt, verdict_lbl = fn['score_badge'](score, eff_classe)
    bud = fn['budget_tier'](score, all_scores)

    prev_mi = (mi - 1) % 12
    next_mi = (mi + 1) % 12

    # Activities
    if is_fr:
        act_city  = '✅ Bon' if score >= 6.5 else '⚠️ Possible'
        act_ext   = '✅ Bon' if score >= 7.5 else ('⚠️ Possible' if score >= 6.0 else '❌ Déconseillé')
        act_beach = ('✅ Bon' if score >= 7.5 and m['tmax'] >= 25
                     else ('⚠️ Possible' if score >= 6.5 and m['tmax'] >= 20 else '❌ Déconseillé'))
    else:
        act_city  = '✅ Good' if score >= 6.5 else '⚠️ Possible'
        act_ext   = '✅ Good' if score >= 7.5 else ('⚠️ Possible' if score >= 6.0 else '❌ Not recommended')
        act_beach = ('✅ Good' if score >= 7.5 and m['tmax'] >= 25
                     else ('⚠️ Possible' if score >= 6.5 and m['tmax'] >= 20 else '❌ Not recommended'))

    # Context flags
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
    hash_var    = (hash(slug_fr + str(mi)) % 3)

    # FR-specific vars (needed in labels dict even for EN path)
    prep = dest.get('prep', 'à')
    nom_bare = dest.get('nom_bare', slug_fr)
    month_lc = month.lower() if is_fr else month  # FR lowercases months

    # ── Hero sub ──
    if is_fr:
        if score >= 8.5:
            hero_opts = [
                f"{month} est l'une des meilleures périodes {prep} {nom_bare}.",
                f"{month} {prep} {nom_bare} : conditions quasi idéales.",
                f"Partir {prep} {nom_bare} en {month_lc} ? Excellente idée.",
            ]
        elif score >= 7.0:
            hero_opts = [
                f"{month} est une bonne période. {best_month} est légèrement meilleur.",
                f"{nom_bare} en {month_lc} : solide, même si {best_month.lower()} reste le pic.",
                f"Bonne fenêtre en {month_lc} — {best_month.lower()} est un cran au-dessus.",
            ]
        else:
            hero_opts = [
                f"{month} est difficile — {best_month} offre de bien meilleures conditions.",
                f"Période compliquée en {month_lc}. Préférez {best_month.lower()} si possible.",
                f"{nom_bare} en {month_lc} ? Pas la meilleure fenêtre — visez {best_month.lower()}.",
            ]
    else:
        if score >= 8.5:
            hero_opts = [
                f"{month} is one of the best times to visit {nom}.",
                f"{nom} in {month}: near-perfect conditions.",
                f"Visiting {nom} in {month}? Excellent choice.",
            ]
        elif score >= 7.0:
            hero_opts = [
                f"{month} is a good time to visit. {best_month} is slightly better.",
                f"{nom} in {month}: solid, though {best_month} remains peak.",
                f"Good window in {month} — {best_month} is a notch above.",
            ]
        else:
            hero_opts = [
                f"{month} is a difficult time — {best_month} offers much better conditions.",
                f"Tough conditions in {month}. Consider {best_month} if possible.",
                f"{nom} in {month}? Not the best window — aim for {best_month}.",
            ]
    hero_sub = hero_opts[hash_var]

    # ── Verdict text ──
    diff = round(best_score - score, 1)
    if is_fr:
        if score >= 9.0:
            verdict_opts = [
                f"{month} est une excellente période {prep} {nom_bare}. {m['tmax']}°C, {m['sun_h']}h de soleil — conditions optimales.",
                f"Partir en {month_lc} {prep} {nom_bare} est un choix sûr : météo au top, {m['rain_pct']}% de risque de pluie seulement.",
                f"{nom_bare} en {month_lc} coche toutes les cases : chaleur, soleil, peu de pluie.",
            ]
        elif score >= 7.0:
            verdict_opts = [
                f"{month} est une bonne période {prep} {nom_bare}. {best_month} reste légèrement meilleur (+{diff} pts).",
                f"Conditions favorables en {month_lc} ({score:.1f}/10). {best_month} fait mieux mais l'écart est faible.",
                f"{nom_bare} en {month_lc} : {m['tmax']}°C et {m['sun_h']}h de soleil. Correct, sans être le pic.",
            ]
        elif score >= 5.0:
            verdict_opts = [
                f"{month} est une période moyenne {prep} {nom_bare}. {best_month} ({best_score}/10) est nettement préférable.",
                f"Pas la meilleure fenêtre : {m['rain_pct']}% de risque de pluie et {m['sun_h']}h de soleil. {best_month} est bien plus sûr.",
                f"{nom_bare} en {month_lc} reste possible mais {best_month} offre un score de {best_score}/10 contre {score:.1f}.",
            ]
        else:
            verdict_opts = [
                f"{month} est difficile {prep} {nom_bare}. {best_month} ({best_score}/10) est bien plus favorable.",
                f"Conditions défavorables en {month_lc} ({score:.1f}/10). Privilégiez {best_month.lower()} si vos dates sont flexibles.",
                f"{nom_bare} en {month_lc} : {m['rain_pct']}% de pluie, {m['sun_h']}h de soleil. Mieux vaut reporter à {best_month.lower()}.",
            ]
    else:
        if score >= 9.0:
            verdict_opts = [
                f"{month} is an excellent time to visit {nom}. {m['tmax']}°C, {m['sun_h']}h of sunshine — optimal conditions.",
                f"Visiting {nom} in {month} is a safe bet: great weather, only {m['rain_pct']}% chance of rain.",
                f"{nom} in {month} ticks all the boxes: warmth, sunshine, minimal rain.",
            ]
        elif score >= 7.0:
            verdict_opts = [
                f"{month} is a good time to visit {nom}. {best_month} remains slightly better (+{diff} pts).",
                f"Favourable conditions in {month} ({score:.1f}/10). {best_month} scores higher but the gap is small.",
                f"{nom} in {month}: {m['tmax']}°C and {m['sun_h']}h of sunshine. Decent, but not the peak.",
            ]
        elif score >= 5.0:
            verdict_opts = [
                f"{month} is an average time for {nom}. {best_month} ({best_score}/10) is clearly preferable.",
                f"Not the best window: {m['rain_pct']}% rain risk and {m['sun_h']}h of sunshine. {best_month} is much safer.",
                f"{nom} in {month} is possible but {best_month} offers a score of {best_score}/10 vs {score:.1f}.",
            ]
        else:
            verdict_opts = [
                f"{month} is a difficult time for {nom}. {best_month} ({best_score}/10) is much more favourable.",
                f"Unfavourable conditions in {month} ({score:.1f}/10). Consider {best_month} if your dates are flexible.",
                f"{nom} in {month}: {m['rain_pct']}% rain, {m['sun_h']}h of sunshine. Better to wait for {best_month}.",
            ]
    verdict_txt = verdict_opts[hash_var]

    # Bars
    rain_bar = bar_chart(m['rain_pct'])
    temp_bar = bar_chart(min(m['tmax'], 40), 40)
    sun_bar  = bar_chart(min(m['sun_h'], 14), 14)

    # ── Oui si / Yes if ──
    if is_fr:
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
                oui_si = "apprécier l'ambiance hivernale et les prix les plus bas de l'année."
                non_si = "chercher le soleil ou les activités de plein air."
            elif is_rainy:
                oui_si = "voyager hors saison avec des prix réduits et très peu de touristes."
                non_si = "éviter la pluie — plus d'un jour sur deux est pluvieux."
            else:
                oui_si = "profiter de tarifs bas et d'une fréquentation minimale."
                non_si = "rechercher un temps estival — les conditions ne s'y prêtent pas."
    else:
        if score >= 8.0:
            if is_tropical and is_dry:
                oui_si = "you want to enjoy the dry season — ideal for beaches and excursions."
                non_si = "you're on a tight budget — it's peak season with highest prices."
            elif is_hot and is_sunny:
                oui_si = f"you're looking for maximum sunshine — {m['sun_h']}h per day on average."
                non_si = "you struggle with heat — temperatures regularly exceed 30°C."
            elif is_warm and is_dry:
                oui_si = f"you want to combine beach, sightseeing and hiking — versatile weather ({m['tmax']}°C, little rain)."
                non_si = "you want to avoid tourist crowds — this is the busiest period."
            elif is_summer:
                oui_si = "you want long sunny days and outdoor activities."
                non_si = "you want to avoid summer crowds — this is peak tourist season."
            elif is_shoulder:
                oui_si = "you want good weather with lower prices than peak season."
                non_si = "you need guaranteed perfect weather — some mixed days are possible."
            else:
                oui_si = "you want great weather for all activities."
                non_si = "you're on a tight budget — prices are higher during peak season."
        elif score >= 6.0:
            if is_rainy:
                oui_si = "you're willing to accept showers in exchange for lower prices and fewer tourists."
                non_si = "you're planning 100% outdoor activities — rain is frequent."
            elif is_cold:
                oui_si = f"you prefer museums and gastronomy — it's cool at {m['tmax']}°C."
                non_si = "you're looking for beach weather — it's not the right season."
            elif is_mild:
                oui_si = "you want to explore the city on foot without suffering from heat."
                non_si = "you're looking for a beach destination — water and air are still cool."
            elif is_shoulder:
                oui_si = f"you want shoulder-season value — fewer crowds, {m['tmax']}°C."
                non_si = "you need maximum sunshine — some overcast days are possible."
            else:
                oui_si = "you want to explore cultural sites and local food."
                non_si = "you need guaranteed sunshine for photos or outdoor activities."
        else:
            if is_tropical and is_rainy:
                oui_si = "you want an off-the-beaten-path experience at bargain prices."
                non_si = "you're worried about rain — it's monsoon season with daily showers."
            elif is_cold and is_winter:
                oui_si = "you enjoy winter atmosphere and the lowest prices of the year."
                non_si = "you're looking for sunshine or outdoor activities."
            elif is_rainy:
                oui_si = "you prefer off-season travel with reduced prices and very few tourists."
                non_si = "you want to avoid rain — more than half the days are rainy."
            else:
                oui_si = "you want the lowest prices and minimal crowds."
                non_si = "you're looking for summer weather — conditions don't support it."

    # ── Month nav ──
    MNAV_CLS = {'rec': 'mnav-rec', 'mid': 'mnav-mid', 'avoid': 'mnav-avoid'}
    def _mnav_attr(i):
        if i == mi:
            return ' class="active"'
        c = MNAV_CLS.get(months[i]['classe'], '')
        return f' class="{c}"' if c else ''

    if is_fr:
        month_nav = ''.join(
            f'<a href="{slug_fr}-meteo-{MONTH_URL_FR[i]}.html"{_mnav_attr(i)}>{MABBR[i]}</a>'
            for i in range(12))
    else:
        month_nav = ''.join(
            f'<a href="{slug_en}-weather-{MONTH_URL[i]}.html"{_mnav_attr(i)}>{MABBR[i]}</a>'
            for i in range(12))

    # ── Annual table ──
    table_rows = ''
    for i, mo in enumerate(months):
        highlight = ' class="row-highlight"' if i == mi else ''
        cls = mo['classe']
        ski_col = ''
        if is_mountain:
            from scoring import compute_ski_score, best_class
            ski = compute_ski_score(mo['tmax'], mo['rain_pct'], mo['sun_h'])
            cls = best_class(mo['classe'], ski)
            ski_col = f'<td>{ski:.1f}/10</td>'
        table_rows += (f'<tr class="{cls}"{highlight}>'
                       f'<td>{weather_emoji(mo["tmax"], mo["rain_pct"], mo["sun_h"])} {MONTHS[i]}</td>'
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

    # ── FAQ ──
    if is_fr:
        faq_q1 = f"{nom_bare} en {month_lc} : est-ce une bonne période ?"
        if is_mountain:
            from scoring import compute_ski_score
            ski_this = compute_ski_score(m['tmax'], m['rain_pct'], m['sun_h'])
            if ski_this >= 6.5 and score < 5:
                faq_a1 = (f"Pour le ski, oui : score ski {ski_this}/10 en {month_lc}. "
                          f"Les températures ({m['tmax']}°C max) garantissent un bon enneigement. "
                          f"Pour la randonnée estivale, préférez {best_month.lower()} ({best_score:.1f}/10).")
            elif ski_this >= 5 and score < 5:
                faq_a1 = (f"{month} est une période correcte pour le ski (score ski {ski_this}/10). "
                          f"Les conditions ne sont pas idéales pour la randonnée ({score:.1f}/10).")
            elif score >= 9:
                faq_a1 = f"Oui, {month_lc} est l'une des meilleures périodes {prep} {nom_bare} (score {score:.1f}/10). {m['tmax']}°C, {m['sun_h']}h de soleil — idéal pour la randonnée."
            elif score >= 7:
                faq_a1 = f"Oui, {month_lc} est une bonne période ({score:.1f}/10). Idéal pour les activités outdoor et la randonnée."
            else:
                faq_a1 = (f"Période de transition avec un score été de {score:.1f}/10 et ski de {ski_this}/10. "
                          f"Ni la meilleure saison de ski ni d'été.")
        elif score >= 9:
            faq_a1 = f"Oui, {month_lc} est l'une des meilleures périodes {prep} {nom_bare} (score {score:.1f}/10). {m['tmax']}°C, {m['sun_h']}h de soleil et seulement {m['rain_pct']}% de jours pluvieux."
        elif score >= 7.5:
            faq_a1 = f"Oui, {month_lc} est une bonne période ({score:.1f}/10). Les conditions sont favorables même si {best_month.lower()} reste le mois optimal ({best_score:.1f}/10)."
        elif score >= 5.5:
            faq_a1 = f"{month} est une période correcte ({score:.1f}/10) mais pas idéale. Attendez-vous à {m['rain_pct']}% de jours pluvieux. {best_month} ({best_score:.1f}/10) offre de meilleures garanties."
        else:
            faq_a1 = f"{month} n'est pas recommandé {prep} {nom_bare} (score {score:.1f}/10). Avec {m['rain_pct']}% de jours pluvieux et {m['sun_h']}h de soleil, préférez {best_month.lower()} ({best_score:.1f}/10)."

        # Q2
        if is_mountain and is_cold:
            faq_q2 = f"Peut-on skier {prep} {nom_bare} en {month_lc} ?"
            if ski_this >= 6.5:
                faq_a2 = f"Oui, {month_lc} est une excellente période pour le ski (score {ski_this}/10). Avec {m['tmax']}°C max et {m['rain_pct']}% de précipitations, les conditions d'enneigement sont bonnes."
            elif ski_this >= 4:
                faq_a2 = f"Les conditions sont correctes (score ski {ski_this}/10) mais pas optimales. Vérifiez l'état des pistes avant de partir."
            else:
                faq_a2 = f"Le ski n'est pas recommandé en {month_lc} (score ski {ski_this}/10). Les températures ({m['tmax']}°C) limitent l'enneigement."
        elif is_hot and is_dry:
            faq_q2 = f"Fait-il trop chaud {prep} {nom_bare} en {month_lc} ?"
            _heat_fr = "C'est intense mais gérable avec de la crème solaire et de l'eau." if m['tmax'] < 38 else "La chaleur est extrême — limitez les activités aux heures fraîches."
            faq_a2 = f"Les températures atteignent {m['tmax']}°C. {_heat_fr} Ensoleillement : {m['sun_h']}h/jour."
        elif is_rainy:
            faq_q2 = f"Pleut-il beaucoup {prep} {nom_bare} en {month_lc} ?"
            faq_a2 = f"Oui, {m['rain_pct']}% des jours connaissent de la pluie en {month_lc}. {'En zone tropicale, ce sont souvent des averses courtes mais intenses.' if is_tropical else 'Prévoyez des activités couvertes en alternative.'}"
        elif is_cold:
            faq_q2 = f"Quel temps fait-il {prep} {nom_bare} en {month_lc} ?"
            faq_a2 = f"Il fait frais avec {m['tmax']}°C en journée et {m['tmin']}°C la nuit. {m['sun_h']}h de soleil par jour. Prévoyez des vêtements chauds et privilégiez les visites intérieures."
        elif score >= 8:
            faq_q2 = f"Que faire {prep} {nom_bare} en {month_lc} ?"
            faq_a2 = f"Avec {m['tmax']}°C et {m['sun_h']}h de soleil, toutes les activités extérieures sont possibles : {'plage, snorkeling et excursions en bateau.' if is_tropical else 'randonnées, visites de sites et terrasses.'}"
        else:
            faq_q2 = f"Que faire {prep} {nom_bare} en {month_lc} ?"
            faq_a2 = f"Avec {m['tmax']}°C max et {m['sun_h']}h de soleil, {'concentrez-vous sur les sites culturels, musées et gastronomie locale.' if score >= 6 else 'privilégiez les activités couvertes — musées, spas, gastronomie.'}"
    else:
        faq_q1 = f"Is {month} a good time to visit {nom}?"
        if is_mountain:
            from scoring import compute_ski_score
            ski_this = compute_ski_score(m['tmax'], m['rain_pct'], m['sun_h'])
            if ski_this >= 6.5 and score < 5:
                faq_a1 = (f"For skiing, yes: ski score {ski_this}/10 in {month}. "
                          f"Temperatures ({m['tmax']}°C max) ensure good snow cover. "
                          f"For summer hiking, prefer {best_month} ({best_score:.1f}/10).")
            elif ski_this >= 5 and score < 5:
                faq_a1 = (f"{month} is decent for skiing (ski score {ski_this}/10). "
                          f"Conditions aren't ideal for hiking ({score:.1f}/10).")
            elif score >= 9:
                faq_a1 = f"Yes, {month} is one of the best times to visit {nom} (score {score:.1f}/10). {m['tmax']}°C, {m['sun_h']}h of sunshine — perfect for hiking."
            elif score >= 7:
                faq_a1 = f"Yes, {month} is a good time ({score:.1f}/10). Great for outdoor activities and hiking."
            else:
                faq_a1 = (f"Transition period with a summer score of {score:.1f}/10 and ski score of {ski_this}/10. "
                          f"Neither the best ski nor summer season.")
        elif score >= 9:
            faq_a1 = f"Yes, {month} is one of the best times to visit {nom} (score {score:.1f}/10). {m['tmax']}°C, {m['sun_h']}h of sunshine and only {m['rain_pct']}% rainy days."
        elif score >= 7.5:
            faq_a1 = f"Yes, {month} is a good time ({score:.1f}/10). Conditions are favourable although {best_month} remains the optimal month ({best_score:.1f}/10)."
        elif score >= 5.5:
            faq_a1 = f"{month} is acceptable ({score:.1f}/10) but not ideal. Expect {m['rain_pct']}% rainy days. {best_month} ({best_score:.1f}/10) offers better guarantees."
        else:
            faq_a1 = f"{month} is not recommended for {nom} (score {score:.1f}/10). With {m['rain_pct']}% rainy days and {m['sun_h']}h of sunshine, prefer {best_month} ({best_score:.1f}/10)."

        # Q2 EN
        if is_mountain and is_cold:
            faq_q2 = f"Can you ski in {nom} in {month}?"
            if ski_this >= 6.5:
                faq_a2 = f"Yes, {month} is excellent for skiing (score {ski_this}/10). With {m['tmax']}°C max and {m['rain_pct']}% precipitation, snow conditions are good."
            elif ski_this >= 4:
                faq_a2 = f"Conditions are decent (ski score {ski_this}/10) but not optimal. Check slope conditions before going."
            else:
                faq_a2 = f"Skiing is not recommended in {month} (ski score {ski_this}/10). Temperatures ({m['tmax']}°C) limit snow cover."
        elif is_hot and is_dry:
            faq_q2 = f"Is it too hot in {nom} in {month}?"
            _heat_en = "It's intense but manageable with sunscreen and water." if m['tmax'] < 38 else "The heat is extreme — limit activities to cooler hours."
            faq_a2 = f"Temperatures reach {m['tmax']}°C. {_heat_en} Sunshine: {m['sun_h']}h/day."
        elif is_rainy:
            faq_q2 = f"Does it rain a lot in {nom} in {month}?"
            faq_a2 = f"Yes, {m['rain_pct']}% of days see rain in {month}. {'In tropical zones, these are often short but intense showers.' if is_tropical else 'Plan indoor alternatives.'}"
        elif is_cold:
            faq_q2 = f"What is the weather like in {nom} in {month}?"
            faq_a2 = f"It's cool with {m['tmax']}°C during the day and {m['tmin']}°C at night. {m['sun_h']}h of sunshine per day. Pack warm clothes and favour indoor visits."
        elif score >= 8:
            faq_q2 = f"What to do in {nom} in {month}?"
            faq_a2 = f"With {m['tmax']}°C and {m['sun_h']}h of sunshine, all outdoor activities are possible: {'beach, snorkelling and boat excursions.' if is_tropical else 'hiking, sightseeing and terraces.'}"
        else:
            faq_q2 = f"What to do in {nom} in {month}?"
            faq_a2 = f"With {m['tmax']}°C max and {m['sun_h']}h of sunshine, {'focus on cultural sites, museums and local gastronomy.' if score >= 6 else 'favour indoor activities — museums, spas, gastronomy.'}"

    # ── Schemas ──
    faq_schema = json.dumps({
        "@context": "https://schema.org", "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": faq_q1, "acceptedAnswer": {"@type": "Answer", "text": faq_a1}},
            {"@type": "Question", "name": faq_q2, "acceptedAnswer": {"@type": "Answer", "text": faq_a2}},
        ]
    }, ensure_ascii=False)

    if is_fr:
        canonical = f"https://bestdateweather.com/{slug_fr}-meteo-{month_url}.html"
        cross_url = f"https://bestdateweather.com/en/{slug_en}-weather-{MONTH_URL[mi]}.html"
        hreflang_fr = canonical
        hreflang_en = cross_url
        article_headline = f"Météo {prep} {nom_bare} en {month_lc} — Températures, pluie et conseils"
        article_desc = f"Météo {prep} {nom_bare} en {month_lc} : {m['tmax']}°C, {m['rain_pct']}% de jours pluvieux. Score {score:.1f}/10."
    else:
        canonical = f"https://bestdateweather.com/en/{slug_en}-weather-{month_url}.html"
        cross_url = f"https://bestdateweather.com/{slug_fr}-meteo-{MONTH_URL_FR[mi]}.html"
        hreflang_fr = cross_url
        hreflang_en = canonical
        article_headline = f"{nom} weather in {month} — Temperature, rain and tips"
        article_desc = f"{nom} weather in {month}: {m['tmax']}°C, {m['rain_pct']}% rainy days. Score {score:.1f}/10."

    article_schema = json.dumps({
        "@context": "https://schema.org", "@type": "Article",
        "headline": article_headline,
        "description": article_desc,
        "author": {"@type": "Organization", "name": "BestDateWeather"},
        "publisher": {"@type": "Organization", "name": "BestDateWeather"},
        "dateModified": TODAY,
        "mainEntityOfPage": {"@type": "WebPage", "@id": canonical}
    }, ensure_ascii=False)

    if is_fr:
        bc_items = [
            {"@type": "ListItem", "position": 1, "name": "Accueil", "item": "https://bestdateweather.com/"},
            {"@type": "ListItem", "position": 2, "name": nom_bare, "item": f"https://bestdateweather.com/meilleure-periode-{slug_fr}.html"},
            {"@type": "ListItem", "position": 3, "name": month, "item": canonical}
        ]
    else:
        bc_items = [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://bestdateweather.com/en/"},
            {"@type": "ListItem", "position": 2, "name": nom, "item": f"https://bestdateweather.com/en/best-time-to-visit-{slug_en}.html"},
            {"@type": "ListItem", "position": 3, "name": month, "item": canonical}
        ]
    breadcrumb_schema = json.dumps({
        "@context": "https://schema.org", "@type": "BreadcrumbList",
        "itemListElement": bc_items
    }, ensure_ascii=False)

    # ── Title / Desc / H1 (3 variants) ──
    title_var = hash(slug_fr + str(mi)) % 3
    desc_var  = hash(slug_fr + str(mi) + 'd') % 3
    h1_var    = hash(slug_fr + str(mi) + 'h1') % 3

    if is_fr:
        if title_var == 0:
            title = f"{nom_bare} en {month_lc} : météo, pluie ({m['rain_pct']}%) et faut-il partir ? [{YEAR}]"
        elif title_var == 1:
            title = f"Météo {prep} {nom_bare} en {month_lc} [{YEAR}] — {m['tmax']}°C, {m['rain_pct']}% pluie"
        else:
            title = f"Partir {prep} {nom_bare} en {month_lc} ? Score {score:.1f}/10 [{YEAR}]"

        if desc_var == 0:
            desc = f"Météo {prep} {nom_bare} en {month_lc} : {m['tmax']}°C max, {m['rain_pct']}% de jours pluvieux, {m['sun_h']}h de soleil/jour. Score {score:.1f}/10. Données 10 ans Open-Meteo."
        elif desc_var == 1:
            desc = f"{nom_bare} en {month_lc} : {m['tmax']}°C, {m['sun_h']}h de soleil, {m['rain_pct']}% de pluie. {'Période recommandée.' if score >= 7.5 else 'Période moyenne.' if score >= 5.5 else 'Période déconseillée.'} Score {score:.1f}/10."
        else:
            desc = f"Faut-il partir {prep} {nom_bare} en {month_lc} ? {m['tmax']}°C et {m['rain_pct']}% de pluie — score météo {score:.1f}/10 sur 10 ans de données."

        if h1_var == 0:
            h1_text = f"Météo {prep} {nom_bare}<br/><em>en {month_lc}</em>"
        elif h1_var == 1:
            h1_text = f"{nom_bare} en {month_lc}<br/><em>quel temps fait-il ?</em>"
        else:
            h1_text = f"Partir {prep} {nom_bare}<br/><em>en {month_lc} ?</em>"

        og_title = f"Météo {prep} {nom_bare} en {month_lc} — {m['tmax']}°C, {m['rain_pct']}% pluie"
    else:
        if title_var == 0:
            title = f"{nom} in {month}: weather, rain ({m['rain_pct']}%) and should you go? [{YEAR}]"
        elif title_var == 1:
            title = f"{nom} weather in {month} [{YEAR}] — {m['tmax']}°C, {m['rain_pct']}% rain"
        else:
            title = f"Visit {nom} in {month}? Score {score:.1f}/10 [{YEAR}]"

        if desc_var == 0:
            desc = f"{nom} weather in {month}: {m['tmax']}°C max, {m['rain_pct']}% rainy days, {m['sun_h']}h sunshine/day. Score {score:.1f}/10. Based on 10 years of Open-Meteo data."
        elif desc_var == 1:
            desc = f"{nom} in {month}: {m['tmax']}°C, {m['sun_h']}h sunshine, {m['rain_pct']}% rain. {'Recommended period.' if score >= 7.5 else 'Average period.' if score >= 5.5 else 'Not recommended.'} Score {score:.1f}/10."
        else:
            desc = f"Should you visit {nom} in {month}? {m['tmax']}°C and {m['rain_pct']}% rain — weather score {score:.1f}/10 based on 10 years of data."

        if h1_var == 0:
            h1_text = f"{nom} weather<br/><em>in {month}</em>"
        elif h1_var == 1:
            h1_text = f"{nom} in {month}<br/><em>what's the weather like?</em>"
        else:
            h1_text = f"Visit {nom}<br/><em>in {month}?</em>"

        og_title = f"{nom} in {month} — {m['tmax']}°C, {m['rain_pct']}% rain"

    # ── Cross-linking similar destinations ──
    climate_for_sim = {}
    for _, sim_slug in similarities.get(slug_fr, [])[:3]:
        if sim_slug in all_climate and all_climate[sim_slug][mi]:
            sm = all_climate[sim_slug][mi]
            climate_for_sim[sim_slug] = {'score': f"{sm['score']:.1f}", 'tmax': sm['tmax']}

    sim_cards_html = _build_sim_cards(cfg, similarities.get(slug_fr, [])[:3], all_dests, climate_for_sim, mi)

    if is_fr:
        sim_section_title = f"Destinations similaires en {month_lc}"
        sim_section_label = "Explorer aussi"
    else:
        sim_section_title = f"Similar destinations in {month}"
        sim_section_label = "Explore also"

    # Pillar + comparison links
    if is_fr:
        pillar_link = (f'<a href="ou-partir-en-{MONTH_URL_FR[mi]}.html" class="link-card">'
                       f'📅 Où partir en {month_lc} — top 25</a>')
    else:
        pillar_link = (f'<a href="where-to-go-in-{MONTH_URL[mi]}.html" class="link-card">'
                       f'📅 Where to go in {month} — top 25</a>')
    comp_links = _build_comp_cards_monthly(cfg, slug_fr, nom if not is_fr else nom_bare, comparison_index, all_dests) if comparison_index else ''

    # ── Context paragraph ──
    event_text = (events or {}).get((slug_fr, mi+1), {}).get('fr' if is_fr else 'en')
    ctx_para = context_paragraph(cfg, nom if not is_fr else nom_bare,
                                 nom_f, m, mi, score, best_month, best_score,
                                 dest.get('tropical', '0') == '1', event_text)

    # ── Labels ──
    lang = 'fr' if is_fr else 'en'
    L = {
        'fr': {
            'html_lang': 'fr',
            'hstat_tmax': 'Température max', 'hstat_rain': 'Jours pluvieux', 'hstat_sun': 'Soleil / jour',
            'sec_summary': 'Résumé du mois', 'sec_summary_title': f'Météo {prep} {nom_bare} en {month_lc}',
            'qf_tminmax': 'Température min / max', 'qf_rain': 'Jours pluvieux', 'qf_rain_unit': 'des jours',
            'qf_sun': 'Soleil', 'qf_sun_unit': 'par jour en moyenne', 'qf_season': 'Saison',
            'qf_score': 'Score météo', 'qf_best': 'Meilleur mois',
            'sec_verdict': 'Décision rapide', 'sec_verdict_title': f'Faut-il partir {prep} {nom_bare} en {month_lc} ?',
            'yes_lbl': '✅ Oui si :', 'no_lbl': '❌ Non si :',
            'bar_rain': 'Pluie', 'bar_temp': 'Température', 'bar_sun': 'Soleil',
            'verdict_intro': 'Notre avis :',
            'sec_activity': 'Selon votre projet', 'sec_activity_title': f'{nom_bare} en {month_lc} selon votre type de voyage',
            'act_city': 'City-trip / culture', 'act_ext': 'Activités extérieures', 'act_beach': 'Plage / baignade', 'act_budget': 'Budget',
            'sec_context': 'Contexte local', 'sec_context_title': f"À quoi s'attendre en {month_lc}",
            'sec_nav': 'Naviguer par mois', 'sec_nav_title': f'Tous les mois {prep} {nom_bare}',
            'sec_table': 'Tableau annuel', 'sec_table_title': 'Comparaison mois par mois',
            'th_month': 'Mois', 'th_tmin': 'T° min', 'th_tmax': 'T° max', 'th_rain': 'Pluie %',
            'th_precip': 'Précip. mm', 'th_sun': 'Soleil h/j', 'th_score': 'Score', 'th_ski': 'Score ski 🎿',
            'legend_ideal': 'Idéal', 'legend_ok': 'Acceptable', 'legend_bad': 'Défavorable',
            'legend_note': '◀ Mois consulté · Source Open-Meteo · 10 ans',
            'src_label': '📊 Source des données',
            'src_text': f'Données calculées sur <strong>10 ans de relevés ERA5</strong> via Open-Meteo, avec ajustement saisonnier ECMWF. En {month_lc}, {nom_bare} affiche en moyenne <strong>{m["tmax"]}°C</strong>, {m["rain_pct"]}% de jours pluvieux et {m["sun_h"]}h de soleil par jour. Score météo global du mois : <strong>{score:.1f}/10</strong>.',
            'src_link_text': 'Voir la méthodologie →', 'src_link': 'methodologie.html',
            'sec_compare': 'Comparaison', 'sec_compare_title': f'{month} vs {best_month} (meilleur mois)',
            'compare_intro': f'Le meilleur mois est <strong><a href="meilleure-periode-{slug_fr}.html" class="txt-inherit">{best_month}</a></strong> (score {best_score:.1f}/10). Différence :',
            'cmp_tmax': 'Température max', 'cmp_rain': 'Jours de pluie', 'cmp_sun': 'Ensoleillement',
            'sec_faq': 'Questions fréquentes', 'sec_faq_title': f'FAQ — {nom_bare} en {month_lc}',
            'prev_label': '← Mois précédent', 'next_label': 'Mois suivant →',
            'annual_label': '📅 Vue annuelle', 'annual_text': 'Tous les mois', 'annual_best': f'Meilleur : {best_month.lower()}',
            'sec_rankings': 'Classements météo', 'sec_rankings_title': 'Comparer les destinations par météo',
            'rank_links': [
                ('classement-destinations-meteo-2026.html', '🌍 Classement mondial 2026'),
                ('classement-destinations-meteo-ete-2026.html', '🌞 Meilleures destinations été'),
                ('classement-destinations-meteo-hiver-2026.html', '🌴 Destinations soleil hiver'),
            ],
            'sec_guides': 'Guides & comparatifs', 'sec_guides_title': 'Explorer ou comparer',
            'cta_title': '📅 Prévisions actualisées — 12 prochains mois',
            'cta_text': 'Données temps réel avec corrections saisonnières ECMWF · mise à jour quotidienne',
            'cta_btn': 'Tester l\'application météo', 'cta_link': 'index.html',
            'kicker': f'Open-Meteo · 10 ans · 12 mois comparés · {lat:.2f}°N {abs(lon):.2f}°{"E" if lon >= 0 else "W"}',
        },
        'en': {
            'html_lang': 'en',
            'hstat_tmax': 'Max temperature', 'hstat_rain': 'Rainy days', 'hstat_sun': 'Sunshine / day',
            'sec_summary': 'Month summary', 'sec_summary_title': f'{nom} weather in {month}',
            'qf_tminmax': 'Temperature min / max', 'qf_rain': 'Rainy days', 'qf_rain_unit': 'of days',
            'qf_sun': 'Sunshine', 'qf_sun_unit': 'per day average', 'qf_season': 'Season',
            'qf_score': 'Weather score', 'qf_best': 'Best month',
            'sec_verdict': 'Quick verdict', 'sec_verdict_title': f'Should you visit {nom} in {month}?',
            'yes_lbl': '✅ Yes if:', 'no_lbl': '❌ No if:',
            'bar_rain': 'Rain', 'bar_temp': 'Temperature', 'bar_sun': 'Sunshine',
            'verdict_intro': 'Our verdict:',
            'sec_activity': 'By trip type', 'sec_activity_title': f'{nom} in {month} by trip type',
            'act_city': 'City-trip / culture', 'act_ext': 'Outdoor activities', 'act_beach': 'Beach / swimming', 'act_budget': 'Budget',
            'sec_context': 'Local context', 'sec_context_title': f'What to expect in {month}',
            'sec_nav': 'Browse by month', 'sec_nav_title': f'All months for {nom}',
            'sec_table': 'Annual table', 'sec_table_title': 'Month-by-month comparison',
            'th_month': 'Month', 'th_tmin': 'Min °C', 'th_tmax': 'Max °C', 'th_rain': 'Rain %',
            'th_precip': 'Precip mm', 'th_sun': 'Sun h/d', 'th_score': 'Score', 'th_ski': 'Ski score 🎿',
            'legend_ideal': 'Ideal', 'legend_ok': 'Acceptable', 'legend_bad': 'Unfavourable',
            'legend_note': '◀ Current month · Source Open-Meteo · 10 years',
            'src_label': '📊 Data source',
            'src_text': f'Calculated from <strong>10 years of ERA5 records</strong> via Open-Meteo, with ECMWF seasonal adjustment. In {month}, {nom} averages <strong>{m["tmax"]}°C</strong>, {m["rain_pct"]}% rainy days and {m["sun_h"]}h sunshine per day. Overall weather score: <strong>{score:.1f}/10</strong>.',
            'src_link_text': 'See methodology →', 'src_link': 'methodology.html',
            'sec_compare': 'Comparison', 'sec_compare_title': f'{month} vs {best_month} (best month)',
            'compare_intro': f'The best month is <strong><a href="best-time-to-visit-{slug_en}.html" class="txt-inherit">{best_month}</a></strong> (score {best_score:.1f}/10). Difference:',
            'cmp_tmax': 'Max temperature', 'cmp_rain': 'Rainy days', 'cmp_sun': 'Sunshine',
            'sec_faq': 'Frequently asked', 'sec_faq_title': f'FAQ — {nom} in {month}',
            'prev_label': '← Previous month', 'next_label': 'Next month →',
            'annual_label': '📅 Annual view', 'annual_text': 'All months', 'annual_best': f'Best: {best_month}',
            'sec_rankings': 'Weather rankings', 'sec_rankings_title': 'Compare destinations by weather',
            'rank_links': [
                ('best-weather-destinations-2026.html', '🌍 World ranking 2026'),
                ('best-summer-destinations-2026.html', '🌞 Best summer destinations'),
                ('best-winter-sun-destinations-2026.html', '🌴 Winter sun destinations'),
            ],
            'sec_guides': 'Guides & comparisons', 'sec_guides_title': 'Explore or compare',
            'cta_title': '📅 Live forecast — next 12 months',
            'cta_text': 'Real-time data with ECMWF seasonal corrections · updated daily',
            'cta_btn': 'Try the weather app', 'cta_link': 'app.html',
            'kicker': f'Open-Meteo · 10 years · 12 months compared · {lat:.2f}°N {abs(lon):.2f}°{"E" if lon >= 0 else "W"}',
        }
    }[lang]

    # ── Prev/Next URLs ──
    if is_fr:
        prev_url = f"{slug_fr}-meteo-{MONTH_URL_FR[prev_mi]}.html"
        next_url = f"{slug_fr}-meteo-{MONTH_URL_FR[next_mi]}.html"
        annual_link = f"meilleure-periode-{slug_fr}.html"
    else:
        prev_url = f"{slug_en}-weather-{MONTH_URL[prev_mi]}.html"
        next_url = f"{slug_en}-weather-{MONTH_URL[next_mi]}.html"
        annual_link = f"best-time-to-visit-{slug_en}.html"

    rank_links_html = ''.join(
        f'<a href="{url}" class="link-card">{label}</a>'
        for url, label in L['rank_links'])

    # ── HEAD CSS / NAV / FOOTER from gen_annual helpers ──
    NAV      = nav_html(cfg)

    html = f'''<!DOCTYPE html>
<html lang="{L['html_lang']}">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1.0"/>
{GTAG}
<title>{title}</title>
<meta name="description" content="{desc}"/>
<link rel="canonical" href="{canonical}"/>
<link rel="alternate" hreflang="fr" href="{hreflang_fr}"/>
<link rel="alternate" hreflang="en" href="{hreflang_en}"/>
<link rel="alternate" hreflang="x-default" href="{hreflang_en}"/>
<meta property="og:type" content="article"/>
<meta property="og:title" content="{og_title}"/>
<meta property="og:description" content="{desc}"/>
<meta property="og:url" content="{canonical}"/>
<script type="application/ld+json">{article_schema}</script>
<script type="application/ld+json">{faq_schema}</script>
<script type="application/ld+json">{breadcrumb_schema}</script>
{head_css(cfg)}
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
 <div class="dest-tag"><img src="{pfx}flags/{flag}.png" width="20" height="15" alt="{flag.upper()}" class="flag-icon"> {nom} · {season}</div>
 <h1 class="hero-title">{h1_text}</h1>
 <p class="hero-sub">{hero_sub}</p>
 <div class="kicker">{L['kicker']}</div>
 <div class="hero-stats mt-22">
 <div><span class="hstat-val">{m['tmax']}°C</span><span class="hstat-lbl">{L['hstat_tmax']}</span></div>
 <div><span class="hstat-val">{m['rain_pct']}%</span><span class="hstat-lbl">{L['hstat_rain']}</span></div>
 <div><span class="hstat-val">{m['sun_h']}h</span><span class="hstat-lbl">{L['hstat_sun']}</span></div>
 </div>
</header>
<main class="page">
 <section class="section">
 <div class="section-label">{L['sec_summary']}</div>
 <h2 class="section-title">{L['sec_summary_title']}</h2>
 <div class="verdict-badge" style="background:{bg};color:{txt};border:1.5px solid {txt}">{verdict_lbl}</div>
 <div class="quick-facts">
 <div class="quick-facts-row"><div class="qf-label">🌡️ {L['qf_tminmax']}</div><div class="qf-value"><strong>{m['tmin']}°C – {m['tmax']}°C</strong></div></div>
 <div class="quick-facts-row"><div class="qf-label">🌧 {L['qf_rain']}</div><div class="qf-value"><strong>{m['rain_pct']}%</strong> {L['qf_rain_unit']}</div></div>
 <div class="quick-facts-row"><div class="qf-label">☀️ {L['qf_sun']}</div><div class="qf-value"><strong>{m['sun_h']}h</strong> {L['qf_sun_unit']}</div></div>
 <div class="quick-facts-row"><div class="qf-label">🌊 {L['qf_season']}</div><div class="qf-value"><strong>{season}</strong></div></div>
 <div class="quick-facts-row"><div class="qf-label">⭐ {L['qf_score']}</div><div class="qf-value"><strong>{score:.1f}/10</strong></div></div>
 <div class="quick-facts-row"><div class="qf-label">📅 {L['qf_best']}</div><div class="qf-value"><strong>{best_month}</strong> ({best_score:.1f}/10)</div></div>
 </div>
 </section>

 <section class="section" class="mb-28">
 <div class="section-label">{L['sec_verdict']}</div>
 <h2 class="section-title">{L['sec_verdict_title']}</h2>
 <div class="verdict-badge" style="background:{bg};color:{txt};border:1.5px solid {txt}">{verdict_lbl}</div>
 <div class="f14-body-mb">
 <p class="mb-8"><strong>{L['yes_lbl']}</strong> {oui_si}</p>
 <p><strong>{L['no_lbl']}</strong> {non_si}</p>
 </div>
 <div class="bar-wrap">
 <div>🌧 {L['bar_rain']} : {rain_bar} <span class="txt-gray">{m['rain_pct']}%</span></div>
 <div>🌡 {L['bar_temp']} : {temp_bar} <span class="txt-gray">{m['tmax']}°C</span></div>
 <div>☀️ {L['bar_sun']} : {sun_bar} <span class="txt-gray">{m['sun_h']}h/j</span></div>
 </div>
 <p class="f14-body-sep"><strong>{L['verdict_intro']}</strong> {verdict_txt}</p>
 </section>

 <section class="section" class="mb-28">
 <div class="section-label">{L['sec_activity']}</div>
 <h2 class="section-title">{L['sec_activity_title']}</h2>
 <ul class="act-list">
 <li class="act-item-odd">🏙️ {L['act_city']} : <strong>{act_city}</strong></li>
 <li class="act-item-even">🚶 {L['act_ext']} : <strong>{act_ext}</strong></li>
 <li class="act-item-odd">🏖️ {L['act_beach']} : <strong>{act_beach}</strong></li>
 <li class="act-item-last">💰 {L['act_budget']} : <strong>{bud}</strong></li>
 </ul>
 </section>

 <section class="section" class="ctx-section mb-28">
 <div class="section-label">{L['sec_context']}</div>
 <h2 class="section-title">{L['sec_context_title']}</h2>
 <p class="f14-context">{ctx_para}</p>
 </section>

 <section class="section">
 <div class="section-label">{L['sec_nav']}</div>
 <h2 class="section-title">{L['sec_nav_title']}</h2>
 <div class="month-nav">{month_nav}</div>
 </section>

 <section class="section">
 <div class="section-label">{L['sec_table']}</div>
 <h2 class="section-title">{L['sec_table_title']}</h2>
 <div class="{'climate-table-wrap mountain' if is_mountain else 'climate-table-wrap'}">
 <table class="climate-table" aria-label="{L['sec_table_title']} {nom}">
 <thead><tr><th>{L['th_month']}</th><th>{L['th_tmin']}</th><th>{L['th_tmax']}</th><th>{L['th_rain']}</th><th>{L['th_precip']}</th><th>{L['th_sun']}</th><th>{L['th_score']}</th>{'<th>' + L['th_ski'] + '</th>' if is_mountain else ''}</tr></thead>
 <tbody>{table_rows}</tbody>
 </table>
 </div>
 <div class="table-legend">
 <span><span class="legend-dot legend-rec"></span>{L['legend_ideal']}</span>
 <span><span class="legend-dot legend-mid"></span>{L['legend_ok']}</span>
 <span><span class="legend-dot legend-avoid"></span>{L['legend_bad']}</span>
 <span class="ml-auto">{L['legend_note']}</span>
 </div>
 </section>

 <div class="eeat-note" class="eeat-note">
 <strong class="txt-navy-block">{L['src_label']}</strong>
 {L['src_text']}
 <a href="{L['src_link']}" class="txt-gold">{L['src_link_text']}</a>
 </div>

 <section class="section" class="mb-28">
 <div class="section-label">{L['sec_compare']}</div>
 <h2 class="section-title">{L['sec_compare_title']}</h2>
 <p class="f14-mb12">{L['compare_intro']}</p>
 <ul class="cmp-list">
 <li class="act-item-odd">🌡️ {L['cmp_tmax']} : <strong>{'+' if diff_t >= 0 else ''}{diff_t}°C</strong></li>
 <li class="act-item-even">🌧 {L['cmp_rain']} : <strong>{'+' if diff_r >= 0 else ''}{diff_r}%</strong></li>
 <li class="act-item-last">☀️ {L['cmp_sun']} : <strong>{'+' if diff_s >= 0 else ''}{diff_s}h/jour</strong></li>
 </ul>
 </section>

 <section class="section" class="mb-28">
 <div class="section-label">{L['sec_faq']}</div>
 <h2 class="section-title">{L['sec_faq_title']}</h2>
 <div class="flex-col-12">
 <div class="faq-card">
 <div class="fw700-mb">{faq_q1}</div>
 <div class="f14-detail">{faq_a1}</div>
 </div>
 <div class="faq-card">
 <div class="fw700-mb">{faq_q2}</div>
 <div class="f14-detail">{faq_a2}</div>
 </div>
 </div>
 </section>

 <section class="section">
 <div class="section-label">{L['prev_label'].split()[0]}</div>
 <div class="flex-wrap-14">
 <a href="{prev_url}" class="nav-card">
 <div class="f11-slate3-mb">{L['prev_label']}</div>
 <div class="fw700-navy">{MONTHS[prev_mi]}</div>
 <div class="f12-slate2">{months[prev_mi]['tmax']}°C · {months[prev_mi]['rain_pct']}% {'pluie' if is_fr else 'rain'}</div>
 </a>
 <a href="{annual_link}" class="nav-card-active">
 <div class="f11-slate3-mb">{L['annual_label']}</div>
 <div class="fw700-navy">{L['annual_text']}</div>
 <div class="f12-slate2">{L['annual_best']}</div>
 </a>
 <a href="{next_url}" class="nav-card">
 <div class="f11-slate3-mb">{L['next_label']}</div>
 <div class="fw700-navy">{MONTHS[next_mi]}</div>
 <div class="f12-slate2">{months[next_mi]['tmax']}°C · {months[next_mi]['rain_pct']}% {'pluie' if is_fr else 'rain'}</div>
 </a>
 </div>
 </section>

 <section class="section">
 <div class="section-label">{sim_section_label}</div>
 <h2 class="section-title">{sim_section_title}</h2>
 <div class="flex-wrap-14">{sim_cards_html}</div>
 </section>

 <section class="section">
 <div class="section-label">{L['sec_rankings']}</div>
 <h2 class="section-title">{L['sec_rankings_title']}</h2>
 <div class="flex-wrap-14">{rank_links_html}</div>
 </section>

 <section class="section">
 <div class="section-label">{L['sec_guides']}</div>
 <h2 class="section-title">{L['sec_guides_title']}</h2>
 <div class="flex-wrap-14">{pillar_link}{comp_links}</div>
 </section>

 <section class="widget-section">
 <div class="cta-box" class="text-center">
 <strong>{L['cta_title']}</strong>
 <p>{L['cta_text']}</p>
 <a class="cta-btn" href="{L['cta_link']}">
 <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" class="icon-18"><path d="M8 6h13M8 12h13M8 18h13M3 6h.01M3 12h.01M3 18h.01"/></svg>
 {L['cta_btn']}
 </a>
 </div>
 </section>
</main>
{footer_html(cfg, dest)}
</body>
</html>'''
    return html


# ── MAIN ────────────────────────────────────────────────────────────────────

def main():
    import argparse
    parser = argparse.ArgumentParser(description='BestDateWeather unified page generator')
    parser.add_argument('--lang', required=True, choices=['fr', 'en'])
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--validate-only', action='store_true')
    parser.add_argument('target', nargs='?', default=None, help='Single destination slug')
    args = parser.parse_args()

    cfg = build_config(args.lang)
    fn  = _bind_lang(cfg)

    print(f"BestDateWeather — generate_pages.py --lang {args.lang}")
    print(f"Mode: {'validate-only' if args.validate_only else 'dry-run' if args.dry_run else 'production'}")
    print(f"Target: {args.target or 'all destinations'}\n")

    dests, climate, cards, overrides, events = load_data(cfg)

    errors = validate(cfg, dests, climate, cards)
    if errors:
        print(f"⚠️  {len(errors)} issue(s) detected:")
        for e in errors:
            print(f"   {e}")
        if any(e.startswith('[P0]') for e in errors):
            print("\n❌ P0 blocking errors. Fix data/climate.csv first.")
            if not args.dry_run:
                sys.exit(1)
    else:
        print("✅ Validation OK\n")

    if args.validate_only:
        return

    similarities = compute_all_similarities(dests, climate)
    comp_index = build_comparison_index(cfg)

    OUT = DIR if cfg['is_fr'] else os.path.join(DIR, 'en')
    os.makedirs(OUT, exist_ok=True)

    slugs = [args.target] if args.target else list(dests.keys())
    total_annual = total_monthly = 0
    errors_gen = []

    for slug_key in slugs:
        if slug_key not in dests:
            print(f"[SKIP] {slug_key}: unknown destination")
            continue
        if slug_key not in climate or None in climate[slug_key]:
            print(f"[SKIP] {slug_key}: incomplete climate data")
            continue

        dest   = dests[slug_key]
        months = climate[slug_key]
        dest_cards_list = cards.get(slug_key, [])
        slug = dest_slug(cfg, dest)

        # Annual page
        try:
            html = gen_annual(cfg, fn, dest, months, dest_cards_list, dests, similarities, comp_index)
            out  = os.path.join(OUT, annual_url(cfg, slug))
            if not args.dry_run:
                open(out, 'w', encoding='utf-8').write(html)
            total_annual += 1
        except Exception as e:
            errors_gen.append(f"{slug_key}/annual: {e}")

        # 12 monthly pages
        gen_monthly_pages = dest.get('monthly', 'True').strip().lower() in ('true', '1', 'yes', '')
        if gen_monthly_pages:
            for mi in range(12):
                try:
                    html = gen_monthly(cfg, fn, dest, months, mi, dests, similarities, climate, events, comp_index)
                    out  = os.path.join(OUT, monthly_url(cfg, slug, mi))
                    if not args.dry_run:
                        open(out, 'w', encoding='utf-8').write(html)
                    total_monthly += 1
                except Exception as e:
                    errors_gen.append(f"{slug_key}/{cfg['months'][mi]}: {e}")

        if not args.dry_run:
            monthly_msg = f"12 monthly" if gen_monthly_pages else "monthly skipped"
            print(f"✓ {slug}: 1 annual + {monthly_msg}")

    print(f"\n{'[DRY-RUN] ' if args.dry_run else ''}Generated: {total_annual} annual + {total_monthly} monthly pages")
    if errors_gen:
        print(f"Generation errors ({len(errors_gen)}):")
        for e in errors_gen:
            print(f"  {e}")
    else:
        print("✅ No generation errors")

    if overrides:
        print(f"ℹ️  {len(overrides)} override(s) applied from overrides.csv")


if __name__ == '__main__':
    main()
