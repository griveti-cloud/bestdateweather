#!/usr/bin/env python3
"""
generate_all_en.py — BestDateWeather
======================================
Source of truth: data/destinations.csv + data/climate.csv + data/cards_en.csv
Generates all EN pages (annual + monthly) into en/ folder.

Usage:
  python3 generate_all_en.py                  # regenerate all
  python3 generate_all_en.py agadir           # one destination (use slug_fr)
  python3 generate_all_en.py --validate-only  # validation only
  python3 generate_all_en.py --dry-run        # simulation
"""

import csv, re, os, sys, json
from datetime import date

# ── PATHS ───────────────────────────────────────────────────────────────────
DIR  = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(DIR, 'data')
OUT  = os.path.join(DIR, 'en')
os.makedirs(OUT, exist_ok=True)

# ── CONSTANTS ───────────────────────────────────────────────────────────────
MONTHS_EN   = ['January','February','March','April','May','June',
               'July','August','September','October','November','December']
MONTH_URL   = ['january','february','march','april','may','june',
               'july','august','september','october','november','december']
MONTH_URL_FR = ['janvier','fevrier','mars','avril','mai','juin',
                'juillet','aout','septembre','octobre','novembre','decembre']
MONTH_ABBR  = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
SEASONS     = {
    0:'Winter',1:'Winter',2:'Spring',3:'Spring',4:'Spring',
    5:'Summer',6:'Summer',7:'Summer',8:'Autumn',9:'Autumn',10:'Autumn',11:'Winter'
}
SEASON_ICONS = {'Spring':'🌸','Summer':'☀️','Autumn':'🍂','Winter':'❄️'}
TODAY = date.today().strftime('%Y-%m-%d')
YEAR  = date.today().year

# ── DATA LOADING ────────────────────────────────────────────────────────────

def load_data(target_slug=None):
    """Load and return (destinations, climate, cards, overrides)."""

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

    cards = {}
    cards_path = f'{DATA}/cards_en.csv'
    if os.path.exists(cards_path):
        for row in csv.DictReader(open(cards_path, encoding='utf-8-sig')):
            slug = row['slug']
            cards.setdefault(slug, []).append(row)

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

    # events.csv — local context per destination × month
    events = {}
    events_path = f'{DATA}/events.csv'
    if os.path.exists(events_path):
        for row in csv.DictReader(open(events_path, encoding='utf-8-sig')):
            events[(row['slug'], int(row['month']))] = {
                'fr': row['event_fr'],
                'en': row['event_en'],
            }

    return dests, climate, cards, overrides, events


# ── VALIDATION ──────────────────────────────────────────────────────────────

def validate(dests, climate):
    errors = []
    for slug, months in climate.items():
        if None in months:
            missing = [MONTHS_EN[i] for i, m in enumerate(months) if m is None]
            errors.append(f"[P0] {slug}: missing months: {missing}")
            continue
        for i, m in enumerate(months):
            if m['score'] > 10.0 or m['score'] < 0:
                errors.append(f"[P0] {slug}/{MONTHS_EN[i]}: score out of range ({m['score']})")
            if m['tmin'] > m['tmax']:
                errors.append(f"[P0] {slug}/{MONTHS_EN[i]}: tmin({m['tmin']}) > tmax({m['tmax']})")
    for slug in dests:
        if slug not in climate:
            errors.append(f"[P0] {slug}: no climate data")
    return errors


# ── DERIVED CALCULATIONS ────────────────────────────────────────────────────

def best_months(months):
    max_score = max(m['score'] for m in months)
    return [MONTHS_EN[i] for i, m in enumerate(months) if m['score'] == max_score]

def budget_tier(score, all_scores):
    sorted_scores = sorted(all_scores, reverse=True)
    n = len(sorted_scores)
    top = sorted_scores[min(3, n-1)]
    bottom = sorted_scores[max(n-5, 0)]
    if score >= top:   return '💸 Peak season'
    if score <= bottom: return '✅ Low season'
    return '🌿 Shoulder'

def score_badge(score):
    if score >= 9.0: return '#dcfce7','#16a34a','✅ Excellent'
    if score >= 7.5: return '#dcfce7','#16a34a','✅ Good'
    if score >= 6.0: return '#fef9c3','#ca8a04','⚠️ Fair'
    return '#fee2e2','#dc2626','❌ Poor'

def seasonal_stats(months):
    seasons = {'Spring':[2,3,4],'Summer':[5,6,7],'Autumn':[8,9,10],'Winter':[11,0,1]}
    result = {}
    for name, idxs in seasons.items():
        ms = [months[i] for i in idxs]
        avg_t  = round(sum(m['tmax'] for m in ms) / len(ms))
        avg_r  = round(sum(m['rain_pct'] for m in ms) / len(ms))
        avg_s  = round(sum(m['sun_h'] for m in ms) / len(ms), 1)
        avg_sc = round(sum(m['score'] for m in ms) / len(ms), 1)
        if avg_sc >= 8.5: verdict = 'Excellent time'
        elif avg_sc >= 7.0: verdict = 'Good time'
        elif avg_sc >= 5.5: verdict = 'Acceptable'
        else: verdict = 'Not recommended'
        result[name] = {'tmax': avg_t, 'rain_pct': avg_r, 'sun_h': avg_s,
                        'score': avg_sc, 'verdict': verdict}
    return result

def bar_chart(pct, max_val=100):
    filled = round((pct / max_val) * 10)
    return '█' * filled + '░' * (10 - filled)


# ── HTML TEMPLATES ──────────────────────────────────────────────────────────

COMMON_HEAD_CSS = '''<link rel="stylesheet" href="../style.css"/>
<link rel="icon" type="image/x-icon" href="../favicon.ico"/>
<link rel="apple-touch-icon" sizes="180x180" href="../apple-touch-icon.png"/>
<meta name="theme-color" content="#1a1f2e"/>'''

GTAG = '''<script async src="https://www.googletagmanager.com/gtag/js?id=G-NTCJTDPSJL"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}gtag("js",new Date());gtag("config","G-NTCJTDPSJL");</script>'''

NAV = '''<nav>
 <a class="nav-brand" href="app.html">Best<em>Date</em>Weather</a>
 <a class="nav-cta" href="app.html">Try the app</a>
</nav>'''

def footer_html(slug_fr, slug_en, nom_en):
    fr_link = f' · <a href="../meilleure-periode-{slug_fr}.html" style="color:rgba(255,255,255,.7)"><img src="../flags/fr.png" width="20" height="15" alt="" style="vertical-align:middle;border-radius:2px"> Français</a>'
    return f'''<footer>
 <p style="color:rgba(255,255,255,.7);font-size:13px;font-weight:700;margin-bottom:8px">bestdateweather.com</p>
 <p><a href="https://open-meteo.com/" rel="noopener" style="color:rgba(255,255,255,.7)">Weather data by Open-Meteo.com</a> · Sources: ECMWF, DWD, NOAA · CC BY 4.0</p>
 <p style="margin-top:8px"><a href="../methodology-en.html" style="color:rgba(255,255,255,.7)">Methodology</a> · <a href="app.html" style="color:rgba(255,255,255,.7)">Weather app</a>{fr_link}</p>
 <p style="margin-top:8px;font-size:11px;opacity:.6"><a href="../legal-en.html" style="color:rgba(255,255,255,.7)">Legal</a> · <a href="../privacy-en.html" style="color:rgba(255,255,255,.7)">Privacy</a> · <a href="../contact.html" style="color:rgba(255,255,255,.7)">Contact</a></p>
</footer>'''

def climate_table_html(months, nom_en, is_mountain=False):
    rows = ''
    for i, m in enumerate(months):
        cls = m['classe']
        ski_col = ''
        if is_mountain:
            from scoring import compute_ski_score, best_class
            ski = compute_ski_score(m['tmax'], m['rain_pct'], m['sun_h'])
            cls = best_class(m['classe'], ski)
            ski_col = f'<td>{ski:.1f}/10</td>'
        rows += (f'<tr class="{cls}" data-tmax="{m["tmax"]}" '
                 f'data-rain="{m["rain_pct"]}" data-sun="{m["sun_h"]}">'
                 f'<td>{MONTHS_EN[i]}</td>'
                 f'<td>{m["tmin"]}°C</td><td>{m["tmax"]}°C</td>'
                 f'<td>{m["rain_pct"]}%</td>'
                 f'<td>{m["precip"]:.1f}</td>'
                 f'<td>{m["sun_h"]}h</td>'
                 f'<td>{m["score"]:.1f}/10</td>{ski_col}</tr>\n')
    ski_header = '<th>Ski score 🎿</th>' if is_mountain else ''
    wrap_class = 'climate-table-wrap mountain' if is_mountain else 'climate-table-wrap'
    return f'''<div class="{wrap_class}">
 <table class="climate-table" aria-label="Monthly climate table {nom_en}">
 <thead><tr><th>Month</th><th>Min °C</th><th>Max °C</th><th>Rainy days (%)</th><th>Precip. mm/d</th><th>Sun h/d</th><th>Score</th>{ski_header}</tr></thead>
 <tbody>{rows}</tbody>
 </table>
</div>
<div class="table-legend">
 <span><span class="legend-dot" style="background:#1a7a4a"></span>Ideal</span>
 <span><span class="legend-dot" style="background:#d97706"></span>Fair</span>
 <span><span class="legend-dot" style="background:#dc2626"></span>Off season</span>
 <span style="margin-left:auto">Source: Open-Meteo · 10 years</span>
</div>'''


# ── ANNUAL PAGE GENERATOR ──────────────────────────────────────────────────

def gen_annual(dest, months, dest_cards, all_dests=None, similarities=None, comparison_index=None):
    slug_fr  = dest['slug_fr']
    slug_en  = dest['slug_en']
    nom_en   = dest.get('nom_en', dest['nom_bare'])
    country  = dest.get('country_en', dest['pays'])
    flag     = dest['flag']
    lat      = float(dest['lat'])
    lon      = float(dest['lon'])
    booking_id = dest['booking_dest_id']

    bests      = best_months(months)
    best_str   = ' & '.join(bests[:2]) if len(bests) >= 2 else bests[0]
    best_score = max(m['score'] for m in months)
    best_idx   = next(i for i, m in enumerate(months) if m['score'] == best_score)
    best_m     = months[best_idx]
    seas       = seasonal_stats(months)
    all_scores = [m['score'] for m in months]

    best_rain  = best_m['rain_pct']
    best_tmax  = best_m['tmax']

    title_var = hash(slug_fr) % 3
    if title_var == 0:
        title = f"Best Time to Visit {nom_en} [{YEAR}] — Weather & Tips"
        h1_text = f"Best Time to Visit<br/><em>{nom_en}</em>"
    elif title_var == 1:
        title = f"When to Visit {nom_en}? Month-by-Month Climate [{YEAR}]"
        h1_text = f"When to Visit<br/><em>{nom_en}</em>?"
    else:
        title = f"{nom_en}: Best Season to Travel [{YEAR}] — Climate & Weather"
        h1_text = f"<em>{nom_en}</em><br/>Which Season to Choose?"

    desc_var = hash(slug_fr + 'desc') % 3
    if desc_var == 0:
        desc = (f"When is the best time to visit {nom_en}? "
                f"{MONTHS_EN[best_idx]} offers {best_tmax}°C and {best_rain}% rainy days. "
                f"Weather score: {best_score}/10. 10-year Open-Meteo data.")
    elif desc_var == 1:
        desc = (f"When to visit {nom_en}? {MONTHS_EN[best_idx]} is the best month "
                f"({best_score}/10) with {best_tmax}°C. Full 12-month analysis based on 10 years of data.")
    else:
        desc = (f"{nom_en} in {MONTHS_EN[best_idx]}: {best_tmax}°C, {best_rain}% rain, "
                f"score {best_score}/10. Find the best time to go — 10-year weather data.")

    is_mountain = dest.get('mountain', 'False').strip() == 'True'
    table_html = climate_table_html(months, nom_en, is_mountain)

    hero_sub = dest.get('hero_sub_en') or f"{nom_en}, a destination to discover based on weather data."

    # Quick facts
    worst_idx  = min(range(12), key=lambda i: months[i]['score'])
    worst_rain = months[worst_idx]['rain_pct']
    qf = f'''<section class="section">
 <div class="section-label">Quick decision</div>
 <h2 class="section-title">When to visit {nom_en}?</h2>
 <div class="quick-facts">
 <div class="quick-facts-row"><div class="qf-label">🌞 Best time overall</div><div class="qf-value"><strong>{MONTHS_EN[best_idx]}</strong></div></div>
 <div class="quick-facts-row"><div class="qf-label">🌡️ Optimal temperature</div><div class="qf-value"><strong>{best_m["tmin"]}–{best_m["tmax"]}°C</strong> in {MONTHS_EN[best_idx]}</div></div>
 <div class="quick-facts-row"><div class="qf-label">🌧 Least rain</div><div class="qf-value"><strong>{best_rain}%</strong> rainy days in {MONTHS_EN[best_idx]}</div></div>
 <div class="quick-facts-row"><div class="qf-label">🌧 Wettest month</div><div class="qf-value"><strong>{MONTHS_EN[worst_idx]}</strong> ({worst_rain}%)</div></div>
 <div class="quick-facts-row"><div class="qf-label">📅 Best score</div><div class="qf-value"><strong>{best_score}/10</strong></div></div>
 </div>
</section>'''

    # Cards
    cards_html = '\n'.join(
        f'<div class="project-card"><span class="proj-icon">{c["icon"]}</span>'
        f'<span class="proj-title">{c["title"]}</span>'
        f'<span class="proj-text">{c["text"]}</span></div>'
        for c in dest_cards
    )
    cards_section = f'''<section class="section">
 <div class="section-label">By trip type</div>
 <h2 class="section-title">Best time by type of trip</h2>
 <div class="project-grid">{cards_html}</div>
</section>''' if dest_cards else ''

    # Climate table section
    table_section = f'''<section class="section">
 <div class="section-label">Monthly climate data</div>
 <h2 class="section-title">{nom_en} weather month by month</h2>
 {table_html}
</section>'''

    # Seasonal analysis
    season_rows = ''
    for sname in ['Spring','Summer','Autumn','Winter']:
        s = seas[sname]
        icon = SEASON_ICONS[sname]
        mrange = {'Spring':'Mar–May','Summer':'Jun–Aug','Autumn':'Sep–Nov','Winter':'Dec–Feb'}[sname]
        season_rows += (f'<h3 class="sub-title">{icon} {sname} ({mrange}) — {s["verdict"]}</h3>'
                        f'<p>Average {s["tmax"]}°C, {s["rain_pct"]}% rainy days, '
                        f'{s["sun_h"]}h sunshine/day. Score: {s["score"]}/10.</p>\n')
    seasonal_section = f'''<section class="section">
 <div class="section-label">Seasonal breakdown</div>
 <h2 class="section-title">What to expect each season</h2>
 {season_rows}
</section>'''

    # Booking
    if booking_id:
        booking_url = (f"https://www.booking.com/searchresults.en-gb.html?ss={nom_en}"
                       f"&dest_id={booking_id}&dest_type=city"
                       f"&checkin={YEAR}-{best_idx+1:02d}-01&checkout={YEAR}-{best_idx+1:02d}-07"
                       f"&group_adults=2&no_rooms=1&lang=en-gb")
        # Contextualised budget tip
        off_months = [MONTHS_EN[i] for i in range(12) if months[i]['score'] >= 6.5 and months[i]['score'] < best_score - 1.5]
        if off_months:
            budget_tip = f"Tip: {', '.join(off_months[:2])} {'offer' if len(off_months[:2]) > 1 else 'offers'} a good weather/price balance — decent score with fewer crowds."
        else:
            budget_tip = f"Tip: off-peak months ({MONTHS_EN[worst_idx]}, {MONTHS_EN[(worst_idx+1)%12]}) are cheapest but weather is significantly worse."
        booking_section = f'''<section class="section">
 <div class="section-label">Accommodation</div>
 <h2 class="section-title">Find a place to stay in {nom_en}</h2>
 <div class="affil-box">
 <strong>Check availability during the recommended period</strong>
 <p>{budget_tip}</p>
 <div style="display:flex;gap:12px;flex-wrap:wrap">
 <a class="affil-btn" href="{booking_url}" target="_blank" rel="noopener">Booking.com →</a>
 </div>
 </div>
</section>'''
    else:
        booking_section = ''

    # Monthly nav — colored by score class
    MONTH_BTN_STYLE = {
        'rec':   'background:#e8f8f0;border:1.5px solid #86efac;',
        'mid':   'background:#fffbeb;border:1.5px solid #fbbf24;',
        'avoid': 'background:#fef2f2;border:1.5px solid #fca5a5;',
    }
    has_monthly = dest.get('monthly', 'True').strip().lower() in ('true', '1', 'yes', '')
    monthly_links = ''.join(
        f'<a href="{slug_en}-weather-{MONTH_URL[i]}.html" style="display:block;padding:10px 8px;'
        f'{MONTH_BTN_STYLE.get(months[i]["classe"], MONTH_BTN_STYLE["mid"])}'
        f'border-radius:10px;text-decoration:none;text-align:center">'
        f'<div style="font-weight:700;font-size:13px;color:#1a1f2e">{MONTHS_EN[i]}</div>'
        f'</a>'
        for i in range(12)
    )
    monthly_section = f'''<section class="section">
 <div class="section-label">Monthly weather</div>
 <h2 class="section-title">Detailed weather by month</h2>
 <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(80px,1fr));gap:8px;margin-bottom:20px">
 {monthly_links}
 </div>
</section>''' if has_monthly else ''

    # FAQ
    faq_items = [
        (f"When is the best time to visit {nom_en}?",
         f"{MONTHS_EN[best_idx]} is ideal with {best_rain}% rainy days and {best_tmax}°C. "
         f"{'The months of ' + ' & '.join(bests[:2]) + ' offer comparable conditions.' if len(bests) > 1 else ''}"),
        (f"What is the wettest month in {nom_en}?",
         f"{MONTHS_EN[worst_idx]} is the wettest month with {worst_rain}% rainy days."),
        (f"Is it hot in {nom_en} in {MONTHS_EN[best_idx]}?",
         f"Yes, {MONTHS_EN[best_idx]} is the best month with an average of {best_tmax}°C."),
        (f"Can you visit {nom_en} in winter?",
         f"In winter, the average score is {seas['Winter']['score']}/10. "
         f"{'Acceptable conditions for cultural visits.' if seas['Winter']['score'] >= 5.5 else 'Difficult period — prefer the peak season.'}"),
    ]
    faq_html = '<div class="faq-list">' + ''.join(
        f'<div class="faq-item"><button class="faq-q" onclick="toggleFaq(this)">'
        f'{q}<span class="faq-icon">+</span></button>'
        f'<div class="faq-a">{a}</div></div>'
        for q, a in faq_items
    ) + '</div>'

    faq_schema = json.dumps({
        "@context": "https://schema.org", "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q,
             "acceptedAnswer": {"@type": "Answer", "text": a}}
            for q, a in faq_items
        ]
    }, ensure_ascii=False)

    faq_section = f'''<section class="section">
 <div class="section-label">FAQ</div>
 <h2 class="section-title">Frequently asked questions</h2>
 {faq_html}
</section>'''

    # Cross-linking: similar destinations
    similar_section = ''
    sim_list = (similarities or {}).get(slug_fr, [])
    if sim_list and all_dests:
        sim_cards = ''
        for sim_score, sim_slug in sim_list[:3]:
            sd = all_dests.get(sim_slug, {})
            sn = sd.get('nom_en', sd.get('nom_bare', sim_slug))
            sc = sd.get('country_en', sd.get('pays', ''))
            sf = sd.get('flag', '')
            se = sd.get('slug_en', sim_slug)
            sim_cards += (
                f'<a href="best-time-to-visit-{se}.html" style="flex:1;min-width:200px;'
                f'padding:16px;background:white;border:1.5px solid #e8e0d0;border-radius:12px;'
                f'text-decoration:none;display:flex;flex-direction:column;gap:6px">'
                f'<div style="font-size:13px;color:var(--slate3)"><img src="../flags/{sf}.png" width="16" height="12" '
                f'alt="{sf}" style="vertical-align:middle;margin-right:4px;border-radius:1px">{sc}</div>'
                f'<div style="font-weight:700;color:var(--navy)">{sn}</div>'
                f'<div style="font-size:12px;color:var(--slate2)">Similar climate · {sim_score:.0%} match</div>'
                f'</a>')
        similar_section = f'''<section class="section">
 <div class="section-label">Also explore</div>
 <h2 class="section-title">Destinations with similar climate</h2>
 <div style="display:flex;gap:14px;flex-wrap:wrap">{sim_cards}</div>
</section>'''

    # Ranking pages section
    ranking_section = '''<section class="section">
 <div class="section-label">Weather rankings</div>
 <h2 class="section-title">Compare destinations by weather</h2>
 <div style="display:flex;gap:14px;flex-wrap:wrap"><a href="best-destinations-weather-ranking-2026.html" style="flex:1;min-width:170px;padding:14px 16px;background:white;border:1.5px solid #e8e0d0;border-radius:12px;text-decoration:none;font-size:14px;font-weight:600;color:var(--navy)">🌍 World ranking 2026</a><a href="best-europe-weather-ranking-2026.html" style="flex:1;min-width:170px;padding:14px 16px;background:white;border:1.5px solid #e8e0d0;border-radius:12px;text-decoration:none;font-size:14px;font-weight:600;color:var(--navy)">🇪🇺 Best in Europe</a></div>
</section>'''

    # Pillar page + comparison links (reverse maillage)
    pillar_comp_cards_en = []
    best_month_slug_en = MONTH_URL[best_idx]
    best_month_name_en = MONTHS_EN[best_idx]
    pillar_comp_cards_en.append(
        f'<a href="where-to-go-in-{best_month_slug_en}.html" style="flex:1;min-width:180px;'
        f'padding:14px 16px;background:white;border:1.5px solid #e8e0d0;border-radius:12px;'
        f'text-decoration:none;font-size:14px;font-weight:600;color:var(--navy)">'
        f'📅 Where to go in {best_month_name_en}</a>')
    if comparison_index and slug_en in comparison_index:
        for other_slug_en, comp_file in comparison_index[slug_en][:3]:
            other_nom = other_slug_en
            if all_dests:
                for d in all_dests.values():
                    if d.get('slug_en') == other_slug_en:
                        other_nom = d.get('nom_en', d.get('nom_bare', other_slug_en))
                        break
            pillar_comp_cards_en.append(
                f'<a href="{comp_file}" style="flex:1;min-width:180px;'
                f'padding:14px 16px;background:white;border:1.5px solid #e8e0d0;border-radius:12px;'
                f'text-decoration:none;font-size:14px;font-weight:600;color:var(--navy)">'
                f'⚖️ {nom_en} vs {other_nom}</a>')
    pillar_comparison_section = f'''<section class="section">
 <div class="section-label">Guides & comparisons</div>
 <h2 class="section-title">Explore by month or compare</h2>
 <div style="display:flex;gap:14px;flex-wrap:wrap">{"".join(pillar_comp_cards_en)}</div>
</section>'''

    article_schema = json.dumps({
        "@context": "https://schema.org", "@type": "Article",
        "headline": f"Best Time to Visit {nom_en}",
        "description": desc,
        "author": {"@type": "Organization", "name": "BestDateWeather"},
        "publisher": {"@type": "Organization", "name": "BestDateWeather"},
        "dateModified": TODAY,
        "inLanguage": "en",
        "mainEntityOfPage": {
            "@type": "WebPage",
            "@id": f"https://bestdateweather.com/en/best-time-to-visit-{slug_en}.html"
        }
    }, ensure_ascii=False)

    breadcrumb_schema = json.dumps({
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://bestdateweather.com/en/app.html"},
            {"@type": "ListItem", "position": 2, "name": nom_en, "item": f"https://bestdateweather.com/en/best-time-to-visit-{slug_en}.html"}
        ]
    }, ensure_ascii=False)

    dataset_schema = json.dumps({
        "@context": "https://schema.org",
        "@type": "Dataset",
        "name": f"Climate data for {nom_en} — monthly averages over 10 years",
        "description": f"Monthly temperatures, precipitation, sunshine and wind for {nom_en}. Averages computed from 10 years of ERA5 data (Open-Meteo).",
        "temporalCoverage": "2015/2024",
        "spatialCoverage": {"@type": "Place", "name": nom_en},
        "creator": {"@type": "Organization", "name": "BestDateWeather", "url": "https://bestdateweather.com"},
        "license": "https://creativecommons.org/licenses/by-nc/4.0/",
        "inLanguage": "en",
        "variableMeasured": ["Temperature", "Precipitation", "Sunshine hours", "Wind speed"]
    }, ensure_ascii=False)

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<!-- SCORING: generate_all_en.py | slug={slug_fr} | tropical={dest["tropical"]} | generated={TODAY} -->
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1.0"/>
{GTAG}
<title>{title}</title>
<meta name="description" content="{desc}"/>
<link rel="canonical" href="https://bestdateweather.com/en/best-time-to-visit-{slug_en}.html"/>
<link rel="alternate" hreflang="fr" href="https://bestdateweather.com/meilleure-periode-{slug_fr}.html"/>
<link rel="alternate" hreflang="en" href="https://bestdateweather.com/en/best-time-to-visit-{slug_en}.html"/>
<meta property="og:type" content="article"/>
<meta property="og:title" content="Best time to visit {nom_en} — weather &amp; tips"/>
<meta property="og:description" content="{desc}"/>
<meta property="og:url" content="https://bestdateweather.com/en/best-time-to-visit-{slug_en}.html"/>
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
 <div class="dest-tag"><img src="../flags/{flag}.png" width="20" height="15" alt="{flag.upper()}" style="vertical-align:middle;margin-right:4px;border-radius:1px"> {nom_en}, {country}</div>
 <h1 class="hero-title">{h1_text}</h1>
 <p class="hero-sub">{hero_sub}</p>
 <div class="kicker">Updated: {date.today().strftime("%B %Y")} · Open-Meteo · 10 years · 12 months compared · {lat}°N {abs(lon)}°{"E" if lon >= 0 else "W"}</div>
 <div class="hero-stats" style="margin-top:22px">
 <div><span class="hstat-val">{best_str}</span><span class="hstat-lbl">Best month{"s" if len(bests) > 1 else ""}</span></div>
 <div><span class="hstat-val">{best_tmax}°C</span><span class="hstat-lbl">Optimal temperature</span></div>
 <div><span class="hstat-val">{best_rain}%</span><span class="hstat-lbl">Rainy days</span></div>
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
{footer_html(slug_fr, slug_en, nom_en)}
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


# ── MONTHLY PAGE GENERATOR ─────────────────────────────────────────────────

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

# ── SIMILARITY & CROSS-LINKING ──────────────────────────────────────────────

def build_comparison_index_en():
    """Scan existing EN comparison files to build reverse lookup: slug_en → [(other_slug_en, filename)]."""
    import glob
    index = {}
    for f in glob.glob(os.path.join(OUT, '*-vs-*-weather.html')):
        fname = os.path.basename(f)
        parts = fname.replace('-weather.html', '').split('-vs-')
        if len(parts) == 2:
            a, b = parts
            index.setdefault(a, []).append((b, fname))
            index.setdefault(b, []).append((a, fname))
    return index

def build_pillar_link_month_en(mi):
    """Build single pillar link card for an EN monthly page."""
    mname = MONTHS_EN[mi]
    return (f'<a href="where-to-go-in-{MONTH_URL[mi]}.html" style="flex:1;min-width:170px;'
            f'padding:14px 16px;background:white;border:1.5px solid #e8e0d0;border-radius:12px;'
            f'text-decoration:none;font-size:14px;font-weight:600;color:var(--navy)">'
            f'📅 Where to go in {mname} — top 25</a>')

def build_comparison_links_en(slug_en, comp_index, all_dests):
    """Build comparison link cards (HTML only, no section wrapper) for an EN page."""
    comps = comp_index.get(slug_en, [])
    if not comps:
        return ''
    # Find nom_en from slug_en
    nom = slug_en
    for d in all_dests.values():
        if d.get('slug_en') == slug_en:
            nom = d.get('nom_en', d.get('nom_bare', slug_en))
            break
    cards = ''
    for other_slug_en, filename in comps[:2]:
        other_nom = other_slug_en
        for d in all_dests.values():
            if d.get('slug_en') == other_slug_en:
                other_nom = d.get('nom_en', d.get('nom_bare', other_slug_en))
                break
        cards += (f'<a href="{filename}" style="flex:1;min-width:180px;'
                  f'padding:14px 16px;background:white;border:1.5px solid #e8e0d0;border-radius:12px;'
                  f'text-decoration:none;font-size:14px;font-weight:600;color:var(--navy)">'
                  f'⚖️ {nom} vs {other_nom}</a>')
    return cards

def compute_all_similarities(dests, climate):
    """Pre-compute 3 most similar destinations for each slug."""
    profiles = {}
    for slug, d in dests.items():
        if slug not in climate or any(m is None for m in climate[slug]):
            continue
        months = climate[slug]
        profiles[slug] = {
            'scores': [m['score'] for m in months],
            'tmaxs':  [m['tmax'] for m in months],
        }

    similarities = {}
    for slug, p in profiles.items():
        sims = []
        for other_slug, op in profiles.items():
            if other_slug == slug:
                continue
            score_diff = sum(abs(p['scores'][i] - op['scores'][i]) for i in range(12)) / 12
            temp_diff  = sum(abs(p['tmaxs'][i]  - op['tmaxs'][i])  for i in range(12)) / 12
            best_a = set(i for i in range(12) if p['scores'][i] >= max(p['scores']) - 1)
            best_b = set(i for i in range(12) if op['scores'][i] >= max(op['scores']) - 1)
            overlap = len(best_a & best_b) / max(len(best_a | best_b), 1)
            sim = (1.0 - (score_diff / 5 + temp_diff / 15) / 2) * 0.6 + overlap * 0.4
            sims.append((max(0, min(1, sim)), other_slug))
        sims.sort(reverse=True)
        similarities[slug] = sims[:3]
    return similarities


def context_paragraph_en(nom_en, m, mi, score, best_month, best_score, is_tropical, event_text=None):
    """Generate a unique context paragraph per destination × month."""
    month_en = MONTHS_EN[mi]
    season = SEASONS[mi]
    tmax, rain, sun = m['tmax'], m['rain_pct'], m['sun_h']

    parts = []

    if event_text:
        parts.append(f"<strong>🎯 {event_text}</strong>")

    if is_tropical and rain >= 50:
        parts.append(f"{month_en} falls in the wet season in {nom_en}. Showers are often brief but intense.")
    elif is_tropical and rain <= 20:
        parts.append(f"{month_en} is peak dry season in {nom_en}. The air is warm and humidity more bearable than in the rainy season.")
    elif season == 'Summer' and tmax >= 30:
        parts.append(f"In the height of summer, {nom_en} sees high temperatures ({tmax}°C). Heat is a factor for outdoor activities.")
    elif season == 'Summer' and tmax >= 22:
        parts.append(f"Summer in {nom_en} brings pleasant temperatures ({tmax}°C) and long sunny days ({sun}h of sunshine).")
    elif season == 'Winter' and tmax <= 10:
        parts.append(f"Winter in {nom_en} is cool ({tmax}°C during the day). Days are short ({sun}h of sunshine) but the city reveals a different side.")
    elif season == 'Winter' and tmax >= 20:
        parts.append(f"Even in winter, {nom_en} enjoys {tmax}°C. A real asset for escaping the European cold.")
    elif season == 'Spring':
        parts.append(f"Spring marks the start of the good season in {nom_en}. Temperatures rise ({tmax}°C) and tourists have not yet arrived en masse.")
    elif season == 'Autumn' and score >= 7:
        parts.append(f"Autumn in {nom_en} is often underrated: {tmax}°C, golden light and declining crowds. An interesting window.")
    elif season == 'Autumn':
        parts.append(f"Autumn marks the end of peak season in {nom_en}. Temperatures drop ({tmax}°C) and rain returns ({rain}% of days).")
    else:
        parts.append(f"In {month_en}, {nom_en} sees {tmax}°C during the day with {sun}h of sunshine per day.")

    if rain <= 10:
        parts.append(f"Rain is virtually absent ({rain}% of days) — ideal for planning without a backup.")
    elif rain <= 25:
        parts.append(f"Rain risk remains low ({rain}% of days), leaving good room for outdoor activities.")
    elif rain <= 45:
        parts.append(f"Expect rain on {rain}% of days — a light raincoat in the bag is recommended.")
    else:
        parts.append(f"With {rain}% of rainy days, always have indoor alternatives planned.")

    if score >= 9:
        parts.append(f"This is one of the best times of year to visit {nom_en}.")
    elif score >= 7.5:
        parts.append(f"A good balance between weather and crowds, even if {best_month} ({best_score:.1f}/10) remains theoretically better.")
    elif score >= 5.5:
        parts.append(f"Not the best window, but acceptable if dates are constrained. {best_month} ({best_score:.1f}/10) is significantly better if possible.")

    return ' '.join(parts)


def _build_sim_cards_en(sim_list, all_dests, climate_for_sim, mi):
    """Build cross-linking HTML cards for similar destinations (EN)."""
    parts = []
    for _, sim_slug in sim_list:
        sd = all_dests.get(sim_slug)
        if not sd:
            continue
        # Skip destinations without monthly pages
        if sd.get('monthly', 'True').strip().lower() not in ('true', '1', 'yes', ''):
            continue
        sc = climate_for_sim.get(sim_slug, {})
        slug_en = sd.get('slug_en', sim_slug)
        nom_en = sd.get('nom_en', sd.get('nom_bare', sim_slug))
        parts.append(
            f'<a href="{slug_en}-weather-{MONTH_URL[mi]}.html" style="flex:1;min-width:180px;'
            f'padding:14px;background:white;border:1.5px solid #e8e0d0;border-radius:12px;'
            f'text-decoration:none;display:flex;flex-direction:column;gap:4px">'
            f'<div style="font-weight:700;color:var(--navy);font-size:14px">'
            f'<img src="../flags/{sd.get("flag","")}.png" width="16" height="12" '
            f'alt="" style="vertical-align:middle;margin-right:4px;border-radius:1px">'
            f'{nom_en}</div>'
            f'<div style="font-size:12px;color:var(--slate2)">{MONTHS_EN[mi]}: {sc.get("score","?")}/10 · {sc.get("tmax","?")}°C</div>'
            f'</a>')
    return ''.join(parts)


def gen_monthly(dest, months, mi, all_dests=None, similarities=None, all_climate=None, events=None, comparison_index=None):
    slug_fr  = dest['slug_fr']
    slug_en  = dest['slug_en']
    nom_en   = dest.get('nom_en', dest['nom_bare'])
    country  = dest.get('country_en', dest['pays'])
    flag     = dest['flag']
    lat      = float(dest['lat'])
    lon      = float(dest['lon'])

    m        = months[mi]
    score    = m['score']
    season   = SEASONS[mi]
    month_en = MONTHS_EN[mi]
    month_url= MONTH_URL[mi]

    all_scores = [mo['score'] for mo in months]
    best_idx   = max(range(12), key=lambda i: months[i]['score'])
    best_month = MONTHS_EN[best_idx]
    best_score = months[best_idx]['score']
    bg, txt, verdict_lbl = score_badge(score)
    bud = budget_tier(score, all_scores)

    prev_mi = (mi - 1) % 12
    next_mi = (mi + 1) % 12

    # Activities
    act_city  = '✅ Good' if score >= 6.5 else '⚠️ Possible'
    act_ext   = '✅ Good' if score >= 7.5 else ('⚠️ Possible' if score >= 6.0 else '❌ Not recommended')
    act_beach = ('✅ Good' if score >= 7.5 and m['tmax'] >= 25
                 else ('⚠️ Possible' if score >= 6.5 and m['tmax'] >= 20 else '❌ Not recommended'))

    # ── Destination context for diversification ──
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

    # Hero sub — 9 variants
    if score >= 8.5:
        hero_opts = [
            f"{month_en} is one of the best times to visit {nom_en}.",
            f"{nom_en} in {month_en}: near-perfect conditions.",
            f"Visiting {nom_en} in {month_en}? Excellent choice.",
        ]
        hero_sub = hero_opts[hash_var]
    elif score >= 7.0:
        hero_opts = [
            f"{month_en} is a good time to visit. {best_month} is slightly better.",
            f"{nom_en} in {month_en}: solid, though {best_month} remains peak.",
            f"Good window in {month_en} — {best_month} is a notch above.",
        ]
        hero_sub = hero_opts[hash_var]
    else:
        hero_opts = [
            f"{month_en} is a difficult time — {best_month} offers much better conditions.",
            f"Tough conditions in {month_en}. Consider {best_month} if possible.",
            f"{nom_en} in {month_en}? Not the best window — aim for {best_month}.",
        ]
        hero_sub = hero_opts[hash_var]

    # Verdict text — enriched with weather context
    if score >= 9.0:
        verdict_opts = [
            f"{month_en} is an excellent time to visit {nom_en}. {m['tmax']}°C, {m['sun_h']}h of sunshine — optimal conditions.",
            f"Visiting {nom_en} in {month_en} is a safe bet: great weather, only {m['rain_pct']}% chance of rain.",
            f"{nom_en} in {month_en} ticks all the boxes: warmth, sunshine, minimal rain.",
        ]
        verdict_txt = verdict_opts[hash_var]
    elif score >= 7.0:
        diff = round(best_score - score, 1)
        verdict_opts = [
            f"{month_en} is a good time to visit {nom_en}. {best_month} remains slightly better (+{diff} pts).",
            f"Favourable conditions in {month_en} ({score:.1f}/10). {best_month} scores higher but the gap is small.",
            f"{nom_en} in {month_en}: {m['tmax']}°C and {m['sun_h']}h of sunshine. Decent, but not the peak.",
        ]
        verdict_txt = verdict_opts[hash_var]
    elif score >= 5.0:
        verdict_opts = [
            f"{month_en} is an average time for {nom_en}. {best_month} ({best_score}/10) is clearly preferable.",
            f"Not the best window: {m['rain_pct']}% rain risk and {m['sun_h']}h of sunshine. {best_month} is much safer.",
            f"{nom_en} in {month_en} is possible but {best_month} offers a score of {best_score}/10 vs {score:.1f}.",
        ]
        verdict_txt = verdict_opts[hash_var]
    else:
        verdict_opts = [
            f"{month_en} is a difficult time for {nom_en}. {best_month} ({best_score}/10) is much more favourable.",
            f"Unfavourable conditions in {month_en} ({score:.1f}/10). Consider {best_month} if your dates are flexible.",
            f"{nom_en} in {month_en}: {m['rain_pct']}% rain, {m['sun_h']}h of sunshine. Better to wait for {best_month}.",
        ]
        verdict_txt = verdict_opts[hash_var]

    rain_bar = bar_chart(m['rain_pct'])
    temp_bar = bar_chart(min(m['tmax'], 40), 40)
    sun_bar  = bar_chart(min(m['sun_h'], 14), 14)

    # Yes if / No if — 18+ variants
    if score >= 8.0:
        if is_tropical and is_dry:
            yes_if = "you want to enjoy the dry season — ideal for beaches and excursions."
            no_if  = "you're on a tight budget — it's peak season with highest prices."
        elif is_hot and is_sunny:
            yes_if = f"you're looking for maximum sunshine — {m['sun_h']}h per day on average."
            no_if  = "you struggle with heat — temperatures regularly exceed 30°C."
        elif is_warm and is_dry:
            yes_if = f"you want to combine beach, sightseeing and hiking — versatile weather ({m['tmax']}°C, little rain)."
            no_if  = "you want to avoid tourist crowds — this is the busiest period."
        elif is_summer:
            yes_if = "you want long sunny days and outdoor activities."
            no_if  = "you want to avoid summer crowds — this is peak tourist season."
        elif is_shoulder:
            yes_if = "you want good weather with lower prices than peak season."
            no_if  = "you need guaranteed perfect weather — some mixed days are possible."
        else:
            yes_if = "you want great weather for all activities."
            no_if  = "you're on a tight budget — prices are higher during peak season."
    elif score >= 6.0:
        if is_rainy:
            yes_if = "you're willing to accept showers in exchange for lower prices and fewer tourists."
            no_if  = "you're planning 100% outdoor activities — rain is frequent."
        elif is_cold:
            yes_if = f"you prefer museums and gastronomy — it's cool at {m['tmax']}°C."
            no_if  = "you're looking for beach weather — it's not the right season."
        elif is_mild:
            yes_if = "you want to explore the city on foot without suffering from heat."
            no_if  = "you're looking for a beach destination — water and air are still cool."
        elif is_shoulder:
            yes_if = f"you want shoulder-season value — fewer crowds, {m['tmax']}°C."
            no_if  = "you need maximum sunshine — some overcast days are possible."
        else:
            yes_if = "you want to explore cultural sites and local food."
            no_if  = "you need guaranteed sunshine for photos or outdoor activities."
    else:
        if is_tropical and is_rainy:
            yes_if = "you want an off-the-beaten-path experience at bargain prices."
            no_if  = "you're worried about rain — it's monsoon season with daily showers."
        elif is_cold and is_winter:
            yes_if = "you enjoy winter atmosphere and the lowest prices of the year."
            no_if  = "you're looking for sunshine or outdoor activities."
        elif is_rainy:
            yes_if = "you prefer off-season travel with reduced prices and very few tourists."
            no_if  = "you want to avoid rain — more than half the days are rainy."
        else:
            yes_if = "you want the lowest prices and minimal crowds."
            no_if  = "you're looking for summer weather — conditions don't support it."

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
        f'<a href="{slug_en}-weather-{MONTH_URL[i]}.html"{_mnav_attr(i)}>{MONTH_ABBR[i]}</a>'
        for i in range(12)
    )

    is_mountain = dest.get('mountain', 'False').strip() == 'True'
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
                       f'<td>{MONTHS_EN[i]}</td>'
                       f'<td>{mo["tmin"]}°C</td><td>{mo["tmax"]}°C</td>'
                       f'<td>{mo["rain_pct"]}%</td>'
                       f'<td>{mo["precip"]:.1f}</td>'
                       f'<td>{mo["sun_h"]}h</td>'
                       f'<td>{mo["score"]:.1f}/10</td>{ski_col}</tr>\n')

    bm = months[best_idx]
    diff_t = round(bm['tmax'] - m['tmax'])
    diff_r = round(bm['rain_pct'] - m['rain_pct'])
    diff_s = round(bm['sun_h'] - m['sun_h'], 1)

    # FAQ — varied by context
    faq_q1 = f"Is {month_en} a good time to visit {nom_en}?"
    if score >= 9:
        faq_a1 = f"Yes, {month_en} is one of the best times to visit {nom_en} (score {score:.1f}/10). {m['tmax']}°C, {m['sun_h']}h of sunshine and only {m['rain_pct']}% rainy days."
    elif score >= 7.5:
        faq_a1 = f"Yes, {month_en} is a good time ({score:.1f}/10). Conditions are favourable though {best_month} remains the peak month ({best_score:.1f}/10)."
    elif score >= 5.5:
        faq_a1 = f"{month_en} is a fair time ({score:.1f}/10) but not ideal. Expect {m['rain_pct']}% rainy days. {best_month} ({best_score:.1f}/10) offers better guarantees."
    else:
        faq_a1 = f"{month_en} is not recommended for {nom_en} (score {score:.1f}/10). With {m['rain_pct']}% rainy days and {m['sun_h']}h of sunshine, consider {best_month} ({best_score:.1f}/10) instead."

    if is_hot and is_dry:
        faq_q2 = f"Is it too hot in {nom_en} in {month_en}?"
        faq_a2 = f"Temperatures reach {m['tmax']}°C. {'Intense but manageable with sun protection.' if m['tmax'] < 38 else 'Heat is extreme — limit activities to cooler hours.'} Sunshine: {m['sun_h']}h/day."
    elif is_rainy:
        faq_q2 = f"Does it rain a lot in {nom_en} in {month_en}?"
        faq_a2 = f"Yes, {m['rain_pct']}% of days see rain in {month_en}. {'In tropical areas, these are often short but intense showers.' if is_tropical else 'Plan indoor alternatives just in case.'}"
    elif is_cold:
        faq_q2 = f"What is the weather like in {nom_en} in {month_en}?"
        faq_a2 = f"It's cool with {m['tmax']}°C daytime highs and {m['tmin']}°C at night. {m['sun_h']}h of sunshine per day. Bring warm layers and focus on indoor visits."
    elif score >= 8:
        faq_q2 = f"What to do in {nom_en} in {month_en}?"
        faq_a2 = f"With {m['tmax']}°C and {m['sun_h']}h of sunshine, all outdoor activities are possible: {'beach, snorkeling and boat trips.' if is_tropical else 'hiking, sightseeing and terrace dining.'}"
    else:
        faq_q2 = f"What to do in {nom_en} in {month_en}?"
        faq_a2 = f"With {m['tmax']}°C max and {m['sun_h']}h of sunshine, {'focus on cultural sites, museums and local cuisine.' if score >= 6 else 'prefer indoor activities — museums, spas, gastronomy.'}"

    faq_schema = json.dumps({
        "@context": "https://schema.org", "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": faq_q1, "acceptedAnswer": {"@type": "Answer", "text": faq_a1}},
            {"@type": "Question", "name": faq_q2, "acceptedAnswer": {"@type": "Answer", "text": faq_a2}},
        ]
    }, ensure_ascii=False)

    article_schema = json.dumps({
        "@context": "https://schema.org", "@type": "Article",
        "headline": f"{nom_en} Weather in {month_en} — Temperature & Rain Data",
        "description": f"{nom_en} in {month_en}: {m['tmax']}°C max, {m['rain_pct']}% rainy days. Score {score:.1f}/10.",
        "author": {"@type": "Organization", "name": "BestDateWeather"},
        "publisher": {"@type": "Organization", "name": "BestDateWeather"},
        "dateModified": TODAY,
        "inLanguage": "en",
        "mainEntityOfPage": {"@type": "WebPage",
            "@id": f"https://bestdateweather.com/en/{slug_en}-weather-{month_url}.html"}
    }, ensure_ascii=False)

    breadcrumb_schema = json.dumps({
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://bestdateweather.com/en/app.html"},
            {"@type": "ListItem", "position": 2, "name": nom_en, "item": f"https://bestdateweather.com/en/best-time-to-visit-{slug_en}.html"},
            {"@type": "ListItem", "position": 3, "name": month_en, "item": f"https://bestdateweather.com/en/{slug_en}-weather-{month_url}.html"}
        ]
    }, ensure_ascii=False)

    title_var = hash(slug_fr + str(mi)) % 3
    if title_var == 0:
        title = f"{nom_en} in {month_en}: Weather, Rain ({m['rain_pct']}%) — Is It Worth It? [{YEAR}]"
    elif title_var == 1:
        title = f"{nom_en} Weather in {month_en} [{YEAR}] — {m['tmax']}°C, {m['rain_pct']}% Rain"
    else:
        title = f"Should You Visit {nom_en} in {month_en}? Score {score:.1f}/10 [{YEAR}]"

    desc_var = hash(slug_fr + str(mi) + 'd') % 3
    if desc_var == 0:
        desc = f"{nom_en} weather in {month_en}: {m['tmax']}°C max, {m['tmin']}°C min, {m['rain_pct']}% rainy days, {m['sun_h']}h sunshine/day. Score {score:.1f}/10. 10-year Open-Meteo data."
    elif desc_var == 1:
        desc = f"{nom_en} in {month_en}: {m['tmax']}°C, {m['sun_h']}h of sunshine, {m['rain_pct']}% rain. {'Recommended period.' if score >= 7.5 else 'Average period.' if score >= 5.5 else 'Not recommended.'} Score {score:.1f}/10."
    else:
        desc = f"Is {month_en} a good time to visit {nom_en}? {m['tmax']}°C and {m['rain_pct']}% rain — weather score {score:.1f}/10 based on 10 years of data."

    h1_var = hash(slug_fr + str(mi) + 'h1') % 3
    if h1_var == 0:
        h1_text = f"<em>{nom_en}</em> Weather<br/>in {month_en}"
    elif h1_var == 1:
        h1_text = f"{nom_en} in {month_en}<br/><em>What's the Weather Like?</em>"
    else:
        h1_text = f"Visiting {nom_en}<br/><em>in {month_en}?</em>"

    # Pre-compute context paragraph and cross-linking
    _evt = (events or {}).get((slug_fr, mi+1), {}).get('en')
    _ctx_para = context_paragraph_en(nom_en, m, mi, score, best_month, best_score, is_tropical, event_text=_evt)

    _sim_climate = {}
    for _, sim_slug in (similarities or {}).get(slug_fr, [])[:3]:
        if all_climate and sim_slug in all_climate and all_climate[sim_slug][mi]:
            sm = all_climate[sim_slug][mi]
            _sim_climate[sim_slug] = {'score': f"{sm['score']:.1f}", 'tmax': sm['tmax']}
    _sim_html = _build_sim_cards_en((similarities or {}).get(slug_fr, [])[:3], all_dests or {}, _sim_climate, mi)

    # Pillar + comparison reverse links for monthly page
    pillar_link_en = build_pillar_link_month_en(mi)
    comp_links_en = build_comparison_links_en(slug_en, comparison_index or {}, all_dests or {}) if comparison_index else ''

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1.0"/>
{GTAG}
<title>{title}</title>
<meta name="description" content="{desc}"/>
<link rel="canonical" href="https://bestdateweather.com/en/{slug_en}-weather-{month_url}.html"/>
<link rel="alternate" hreflang="fr" href="https://bestdateweather.com/{slug_fr}-meteo-{MONTH_URL_FR[mi]}.html"/>
<link rel="alternate" hreflang="en" href="https://bestdateweather.com/en/{slug_en}-weather-{month_url}.html"/>
<meta property="og:type" content="article"/>
<meta property="og:title" content="{nom_en} in {month_en} — {m['tmax']}°C, {m['rain_pct']}% rain"/>
<meta property="og:description" content="{desc}"/>
<meta property="og:url" content="https://bestdateweather.com/en/{slug_en}-weather-{month_url}.html"/>
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
 <div class="dest-tag"><img src="../flags/{flag}.png" width="20" height="15" alt="{flag.upper()}" style="vertical-align:middle;margin-right:4px;border-radius:1px"> {nom_en} · {season}</div>
 <h1 class="hero-title">{h1_text}</h1>
 <p class="hero-sub">{hero_sub}</p>
 <div class="kicker">Open-Meteo · 10 years · 12 months compared · {lat:.2f}°N {abs(lon):.2f}°{"E" if lon >= 0 else "W"}</div>
 <div class="hero-stats" style="margin-top:22px">
 <div><span class="hstat-val">{m['tmax']}°C</span><span class="hstat-lbl">Max temperature</span></div>
 <div><span class="hstat-val">{m['rain_pct']}%</span><span class="hstat-lbl">Rainy days</span></div>
 <div><span class="hstat-val">{m['sun_h']}h</span><span class="hstat-lbl">Sunshine / day</span></div>
 </div>
</header>
<main class="page">
 <section class="section">
 <div class="section-label">Month summary</div>
 <h2 class="section-title">{nom_en} weather in {month_en}</h2>
 <div style="display:inline-flex;align-items:center;gap:6px;padding:6px 14px;border-radius:20px;font-size:13px;font-weight:700;background:{bg};color:{txt};border:1.5px solid {txt};margin-bottom:16px">{verdict_lbl}</div>
 <div class="quick-facts">
 <div class="quick-facts-row"><div class="qf-label">🌡️ Temperature min / max</div><div class="qf-value"><strong>{m['tmin']}°C – {m['tmax']}°C</strong></div></div>
 <div class="quick-facts-row"><div class="qf-label">🌧 Rainy days</div><div class="qf-value"><strong>{m['rain_pct']}%</strong> of days</div></div>
 <div class="quick-facts-row"><div class="qf-label">☀️ Sunshine</div><div class="qf-value"><strong>{m['sun_h']}h</strong> per day average</div></div>
 <div class="quick-facts-row"><div class="qf-label">🌊 Season</div><div class="qf-value"><strong>{season}</strong></div></div>
 <div class="quick-facts-row"><div class="qf-label">⭐ Weather score</div><div class="qf-value"><strong>{score:.1f}/10</strong></div></div>
 <div class="quick-facts-row"><div class="qf-label">📅 Best month</div><div class="qf-value"><strong>{best_month}</strong> ({best_score:.1f}/10)</div></div>
 </div>
 </section>

 <section class="section" style="margin-bottom:28px">
 <div class="section-label">Quick verdict</div>
 <h2 class="section-title">Should you visit {nom_en} in {month_en}?</h2>
 <div style="display:inline-flex;align-items:center;gap:6px;padding:6px 14px;border-radius:20px;font-size:13px;font-weight:700;background:{bg};color:{txt};border:1.5px solid {txt};margin-bottom:16px">{verdict_lbl}</div>
 <div style="margin-bottom:14px;font-size:14px;line-height:1.7">
 <p style="margin-bottom:8px"><strong>✅ Yes if:</strong> {yes_if}</p>
 <p><strong>❌ No if:</strong> {no_if}</p>
 </div>
 <div style="background:#f8f8f4;border-radius:10px;padding:14px;font-size:13px;line-height:1.9;margin-bottom:14px">
 <div>🌧 Rain: {rain_bar} <span style="color:#718096">{m['rain_pct']}%</span></div>
 <div>🌡 Temperature: {temp_bar} <span style="color:#718096">{m['tmax']}°C</span></div>
 <div>☀️ Sunshine: {sun_bar} <span style="color:#718096">{m['sun_h']}h/d</span></div>
 </div>
 <p style="font-size:14px;line-height:1.7;border-top:1px solid #e8e0d0;padding-top:14px"><strong>Our verdict:</strong> {verdict_txt}</p>
 </section>

 <section class="section" style="margin-bottom:28px">
 <div class="section-label">By trip type</div>
 <h2 class="section-title">{nom_en} in {month_en} by type of trip</h2>
 <ul style="list-style:none;padding:0;border:1.5px solid var(--cream2);border-radius:12px;overflow:hidden;font-size:14px">
 <li style="padding:10px 16px;border-bottom:1px solid var(--cream2);background:white">🏙️ City break / culture: <strong>{act_city}</strong></li>
 <li style="padding:10px 16px;border-bottom:1px solid var(--cream2)">🚶 Outdoor activities: <strong>{act_ext}</strong></li>
 <li style="padding:10px 16px;border-bottom:1px solid var(--cream2);background:white">🏖️ Beach / swimming: <strong>{act_beach}</strong></li>
 <li style="padding:10px 16px">💰 Budget: <strong>{bud}</strong></li>
 </ul>
 </section>

 <section class="section" style="border-left:3px solid var(--gold);padding-left:18px;margin-bottom:28px">
 <p style="font-size:14px;line-height:1.7"><strong>Our recommendation for {month_en}:</strong> {verdict_txt}</p>
 </section>

 <section class="section" style="border-left:3px solid var(--gold);padding-left:18px;margin-bottom:28px">
 <div class="section-label">Local context</div>
 <h2 class="section-title">What to expect in {month_en}</h2>
 <p style="font-size:14px;line-height:1.8;color:var(--slate)">{_ctx_para}</p>
 </section>

 <section class="section">
 <div class="section-label">Also explore</div>
 <h2 class="section-title">Similar destinations in {month_en}</h2>
 <div style="display:flex;gap:14px;flex-wrap:wrap">{_sim_html}</div>
 </section>

 <section class="section">
 <div class="section-label">Browse by month</div>
 <h2 class="section-title">All months in {nom_en}</h2>
 <div class="month-nav">{month_nav}</div>
 </section>

 <section class="section">
 <div class="section-label">Annual overview</div>
 <h2 class="section-title">Month-by-month comparison</h2>
 <div class="{'climate-table-wrap mountain' if is_mountain else 'climate-table-wrap'}">
 <table class="climate-table" aria-label="Monthly climate table {nom_en}">
 <thead><tr><th>Month</th><th>Min °C</th><th>Max °C</th><th>Rain %</th><th>Precip. mm</th><th>Sun h/d</th><th>Score</th>{'<th>Ski score 🎿</th>' if is_mountain else ''}</tr></thead>
 <tbody>{table_rows}</tbody>
 </table>
 </div>
 <div class="table-legend">
 <span><span class="legend-dot" style="background:#1a7a4a"></span>Ideal</span>
 <span><span class="legend-dot" style="background:#d97706"></span>Fair</span>
 <span><span class="legend-dot" style="background:#dc2626"></span>Off season</span>
 <span style="margin-left:auto">◀ Current month · Source: Open-Meteo · 10 years</span>
 </div>
 </section>

 <div class="eeat-note" style="margin:20px 0;padding:14px 18px;background:#f8f6f2;border-left:3px solid var(--gold);border-radius:0 8px 8px 0;font-size:13px;color:var(--slate2);line-height:1.7">
 <strong style="color:var(--navy);display:block;margin-bottom:4px">📊 Data source</strong>
 Computed from <strong>10 years of ERA5 records</strong> via Open-Meteo, with ECMWF seasonal adjustment.
 In {month_en.lower()}, {nom_en} averages <strong>{m['tmax']}°C</strong>, {m['rain_pct']}% rainy days and {m['sun_h']}h of sunshine per day.
 Overall weather score: <strong>{score:.1f}/10</strong>.
 <a href="../methodology-en.html" style="color:var(--gold);font-weight:600">See methodology →</a>
 </div>

 <section class="section" style="margin-bottom:28px">
 <div class="section-label">Comparison</div>
 <h2 class="section-title">{month_en} vs {best_month} (best month)</h2>
 <p style="font-size:14px;margin-bottom:12px">The best month is <strong><a href="best-time-to-visit-{slug_en}.html" style="color:inherit">{best_month}</a></strong> (score {best_score:.1f}/10). Difference:</p>
 <ul style="list-style:none;padding:0;border:1.5px solid var(--cream2);border-radius:10px;overflow:hidden;font-size:14px">
 <li style="padding:10px 16px;border-bottom:1px solid var(--cream2);background:white">🌡️ Max temperature: <strong>{'+' if diff_t >= 0 else ''}{diff_t}°C</strong></li>
 <li style="padding:10px 16px;border-bottom:1px solid var(--cream2)">🌧 Rainy days: <strong>{'+' if diff_r >= 0 else ''}{diff_r}%</strong></li>
 <li style="padding:10px 16px">☀️ Sunshine: <strong>{'+' if diff_s >= 0 else ''}{diff_s}h/day</strong></li>
 </ul>
 </section>

 <section class="section" style="margin-bottom:28px">
 <div class="section-label">FAQ</div>
 <h2 class="section-title">FAQ — {nom_en} in {month_en}</h2>
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
 <div class="section-label">Previous / next month</div>
 <div style="display:flex;gap:14px;flex-wrap:wrap">
 <a href="{slug_en}-weather-{MONTH_URL[prev_mi]}.html" style="flex:1;min-width:140px;padding:16px;background:white;border:1.5px solid #e8e0d0;border-radius:12px;text-decoration:none;text-align:center">
 <div style="font-size:11px;color:var(--slate3);margin-bottom:4px">← Previous month</div>
 <div style="font-weight:700;color:var(--navy)">{MONTHS_EN[prev_mi]}</div>
 <div style="font-size:12px;color:var(--slate2)">{months[prev_mi]['tmax']}°C · {months[prev_mi]['rain_pct']}% rain</div>
 </a>
 <a href="best-time-to-visit-{slug_en}.html" style="flex:1;min-width:140px;padding:16px;background:#fef9c3;border:1.5px solid var(--gold);border-radius:12px;text-decoration:none;text-align:center">
 <div style="font-size:11px;color:var(--slate3);margin-bottom:4px">📅 Annual overview</div>
 <div style="font-weight:700;color:var(--navy)">All months</div>
 <div style="font-size:12px;color:var(--slate2)">Best: {best_month.lower()}</div>
 </a>
 <a href="{slug_en}-weather-{MONTH_URL[next_mi]}.html" style="flex:1;min-width:140px;padding:16px;background:white;border:1.5px solid #e8e0d0;border-radius:12px;text-decoration:none;text-align:center">
 <div style="font-size:11px;color:var(--slate3);margin-bottom:4px">Next month →</div>
 <div style="font-weight:700;color:var(--navy)">{MONTHS_EN[next_mi]}</div>
 <div style="font-size:12px;color:var(--slate2)">{months[next_mi]['tmax']}°C · {months[next_mi]['rain_pct']}% rain</div>
 </a>
 </div>
 </section>

 <section class="section">
 <div class="section-label">Weather rankings</div>
 <h2 class="section-title">Compare destinations by weather</h2>
 <div style="display:flex;gap:14px;flex-wrap:wrap"><a href="best-destinations-weather-ranking-2026.html" style="flex:1;min-width:170px;padding:14px 16px;background:white;border:1.5px solid #e8e0d0;border-radius:12px;text-decoration:none;font-size:14px;font-weight:600;color:var(--navy)">🌍 World ranking 2026</a><a href="best-europe-weather-ranking-2026.html" style="flex:1;min-width:170px;padding:14px 16px;background:white;border:1.5px solid #e8e0d0;border-radius:12px;text-decoration:none;font-size:14px;font-weight:600;color:var(--navy)">🇪🇺 Best in Europe</a></div>
 </section>

 <section class="section">
 <div class="section-label">Guides & comparisons</div>
 <h2 class="section-title">Explore or compare</h2>
 <div style="display:flex;gap:14px;flex-wrap:wrap">{pillar_link_en}{comp_links_en}</div>
 </section>

 <section class="widget-section">
 <div class="cta-box" style="text-align:center">
 <strong>📅 Live forecast — next 12 months</strong>
 <p>Real-time data with ECMWF seasonal corrections · updated daily</p>
 <a class="cta-btn" href="app.html">
 <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" style="width:18px;height:18px"><path d="M8 6h13M8 12h13M8 18h13M3 6h.01M3 12h.01M3 18h.01"/></svg>
 Try the weather app
 </a>
 </div>
 </section>
</main>
{footer_html(slug_fr, slug_en, nom_en)}
</body>
</html>'''
    return html


# ── MAIN ────────────────────────────────────────────────────────────────────

def main():
    args        = sys.argv[1:]
    dry_run     = '--dry-run' in args
    validate_only = '--validate-only' in args
    target      = next((a for a in args if not a.startswith('--')), None)

    print("BestDateWeather — generate_all_en.py")
    print(f"Mode: {'validate-only' if validate_only else 'dry-run' if dry_run else 'production'}")
    print(f"Target: {target or 'all destinations'}\n")

    dests, climate, cards, overrides, events = load_data()

    errors = validate(dests, climate)
    if errors:
        print(f"⚠️  {len(errors)} issue(s) detected:")
        for e in errors:
            print(f"   {e}")
        if any(e.startswith('[P0]') for e in errors):
            print("\n❌ P0 blocking errors. Fix data/climate.csv first.")
            if not dry_run:
                sys.exit(1)
    else:
        print("✅ Validation OK\n")

    if validate_only:
        return

    similarities = compute_all_similarities(dests, climate)
    comparison_index_en = build_comparison_index_en()

    slugs = [target] if target else list(dests.keys())
    total_annual = total_monthly = 0
    errors_gen = []

    for slug in slugs:
        if slug not in dests:
            print(f"[SKIP] {slug}: unknown destination")
            continue
        if slug not in climate or None in climate[slug]:
            print(f"[SKIP] {slug}: incomplete climate data")
            continue

        dest   = dests[slug]
        months = climate[slug]
        slug_en = dest['slug_en']
        dest_cards = cards.get(slug, [])

        # Annual page
        try:
            html = gen_annual(dest, months, dest_cards, dests, similarities, comparison_index_en)
            out  = f"{OUT}/best-time-to-visit-{slug_en}.html"
            if not dry_run:
                open(out, 'w', encoding='utf-8').write(html)
            total_annual += 1
        except Exception as e:
            errors_gen.append(f"{slug}/annual: {e}")

        # 12 monthly pages (skip if monthly=False in destinations.csv)
        gen_monthly_pages = dest.get('monthly', 'True').strip().lower() in ('true', '1', 'yes', '')
        if gen_monthly_pages:
            for mi in range(12):
                try:
                    html = gen_monthly(dest, months, mi, dests, similarities, climate, events, comparison_index_en)
                    out  = f"{OUT}/{slug_en}-weather-{MONTH_URL[mi]}.html"
                    if not dry_run:
                        open(out, 'w', encoding='utf-8').write(html)
                    total_monthly += 1
                except Exception as e:
                    errors_gen.append(f"{slug}/{MONTHS_EN[mi]}: {e}")

        if not dry_run:
            monthly_msg = "12 monthly pages" if gen_monthly_pages else "monthly skipped (monthly=False)"
            print(f"✓ {slug_en}: 1 annual + {monthly_msg}")

    print(f"\n{'[DRY-RUN] ' if dry_run else ''}Generated: {total_annual} annual + {total_monthly} monthly pages")
    if errors_gen:
        print(f"Generation errors ({len(errors_gen)}):")
        for e in errors_gen:
            print(f"  {e}")
    else:
        print("✅ No generation errors")


if __name__ == '__main__':
    main()
