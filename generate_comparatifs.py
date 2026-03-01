#!/usr/bin/env python3
"""
Generate comparison pages (X vs Y) for high-search-volume destination pairs.
  FR: nice-ou-barcelone-climat.html
  EN: en/nice-vs-barcelona-weather.html

Each page shows side-by-side monthly climate, score comparison, and verdict.
Usage: python3 generate_comparatifs.py
"""

import csv, html as html_mod, json
from pathlib import Path
from datetime import date

ROOT = Path(__file__).parent
TODAY = date.today().isoformat()
YEAR = date.today().year

MONTHS_FR = ['Janvier','Février','Mars','Avril','Mai','Juin',
             'Juillet','Août','Septembre','Octobre','Novembre','Décembre']
MONTHS_EN = ['January','February','March','April','May','June',
             'July','August','September','October','November','December']
MONTH_URL_FR = ['janvier','fevrier','mars','avril','mai','juin',
                'juillet','aout','septembre','octobre','novembre','decembre']
MONTH_URL_EN = ['january','february','march','april','may','june',
                'july','august','september','october','november','december']

# ── Strategic comparison pairs ────────────────────────────────────────────────
# Format: (slug_fr_a, slug_fr_b)
# Selected for high search volume: "X ou Y", "X vs Y climat/météo"

PAIRS = [
    # Mediterranean rivals
    ('nice', 'barcelone'),
    ('algarve', 'canaries'),
    ('crete', 'sardaigne'),
    ('sicile', 'crete'),
    ('majorque', 'sardaigne'),
    ('corse', 'sardaigne'),
    ('malte', 'sicile'),
    ('dubrovnik', 'split'),
    ('cote-azur', 'costa-brava'),
    ('mykonos', 'santorin'),
    ('ibiza', 'majorque'),
    # Iberian
    ('lisbonne', 'porto'),
    ('barcelone', 'lisbonne'),
    ('algarve', 'cote-azur'),
    # North Africa / Middle East
    ('marrakech', 'fes'),
    ('marrakech', 'agadir'),
    ('dubai', 'abu-dhabi'),
    # Southeast Asia
    ('bali', 'phuket'),
    ('koh-samui', 'koh-lanta'),
    ('chiang-mai', 'bangkok'),
    ('bali', 'sri-lanka'),
    ('langkawi', 'phuket'),
    # Indian Ocean
    ('maldives', 'seychelles'),
    ('ile-maurice', 'reunion'),
    ('maldives', 'zanzibar'),
    # Caribbean / Americas
    ('guadeloupe', 'martinique'),
    ('republique-dominicaine', 'jamaique'),
    ('cancun', 'riviera-maya'),
    ('costa-rica', 'colombie'),
    # Long haul
    ('bali', 'republique-dominicaine'),
    ('tenerife', 'madere'),
    ('canaries', 'madere'),
    ('fuerteventura', 'gran-canaria'),
]

# ── Data Loading ──────────────────────────────────────────────────────────────

def load_destinations():
    dests = {}
    with open(ROOT / 'data/destinations.csv', encoding='utf-8-sig') as f:
        for r in csv.DictReader(f):
            dests[r['slug_fr']] = r
    return dests

def load_climate():
    data = {}
    with open(ROOT / 'data/climate.csv', encoding='utf-8-sig') as f:
        for r in csv.DictReader(f):
            slug = r['slug']
            if slug not in data:
                data[slug] = {}
            m = int(r['mois_num'])
            data[slug][m] = {
                'score': float(r['score']),
                'tmin': float(r['tmin']),
                'tmax': float(r['tmax']),
                'rain_pct': float(r['rain_pct']),
                'precip_mm': float(r['precip_mm']),
                'sun_h': float(r['sun_h']),
            }
    return data

def e(s):
    return html_mod.escape(str(s))

def score_color(s):
    if s >= 8: return '#16a34a'
    if s >= 6: return '#d4a853'
    return '#dc2626'

# ── CSS ───────────────────────────────────────────────────────────────────────

CSS = r"""
*{margin:0;padding:0;box-sizing:border-box}
:root{--navy:#1a2332;--gold:#d4a853;--cream:#faf6ef;--cream2:#ede4d3;--text:#2c3e50;--slate:#5a6c7d;--slate2:#8899a6;--green:#16a34a;--red:#dc2626}
body{font-family:'DM Sans',system-ui,sans-serif;background:var(--cream);color:var(--text);line-height:1.6}
.hero{background:var(--navy);color:white;padding:48px 20px 36px;text-align:center}
.hero-eyebrow{font-size:11px;text-transform:uppercase;letter-spacing:2.5px;color:var(--gold);margin-bottom:12px;font-weight:700}
.hero-title{font-family:'Playfair Display',Georgia,serif;font-size:clamp(22px,5vw,36px);margin-bottom:10px;line-height:1.2}
.hero-title em{color:var(--gold);font-style:italic}
.hero-sub{font-size:15px;opacity:.75;max-width:600px;margin:0 auto}
.page{max-width:960px;margin:0 auto;padding:28px 20px 40px}
.section{margin-bottom:36px}
.eyebrow{font-size:10px;text-transform:uppercase;letter-spacing:2px;color:var(--gold);font-weight:700;margin-bottom:6px}
.sec-title{font-family:'Playfair Display',Georgia,serif;font-size:clamp(18px,4vw,24px);margin-bottom:8px}
.sec-intro{font-size:14px;color:var(--slate);margin-bottom:18px;line-height:1.7}
.vs-grid{display:grid;grid-template-columns:1fr auto 1fr;gap:0;margin-bottom:28px}
.vs-card{background:white;border:1.5px solid var(--cream2);border-radius:14px;padding:24px;text-align:center}
.vs-card h3{font-family:'Playfair Display',Georgia,serif;font-size:18px;margin-bottom:8px}
.vs-card .big-score{font-size:36px;font-weight:700;margin:8px 0}
.vs-card .vs-stat{font-size:13px;color:var(--slate);margin:4px 0}
.vs-card .vs-stat strong{color:var(--text)}
.vs-sep{display:flex;align-items:center;justify-content:center;padding:0 16px;font-size:20px;font-weight:700;color:var(--slate2)}
.ct{width:100%;border-collapse:collapse;font-size:13px;margin-bottom:12px}
.ct th{background:var(--navy);color:white;padding:9px 10px;font-size:11px;text-transform:uppercase;letter-spacing:.5px;font-weight:700;text-align:center}
.ct th:first-child{text-align:left}
.ct td{padding:8px 10px;border-bottom:1px solid var(--cream2);text-align:center}
.ct td:first-child{text-align:left;font-weight:600}
.ct tr:hover{background:#fef9f0}
.ct .win{font-weight:700}
.verdict{background:white;border:1.5px solid var(--cream2);border-radius:14px;padding:24px;margin-bottom:24px}
.verdict h3{font-family:'Playfair Display',Georgia,serif;font-size:17px;margin-bottom:12px}
.verdict p{font-size:14px;color:var(--slate);line-height:1.7;margin-bottom:8px}
.related-pages{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:12px;margin-top:16px}
.related-card{background:white;border:1.5px solid var(--cream2);border-radius:12px;padding:16px;text-decoration:none;color:var(--text);display:block}
.related-card:hover{border-color:var(--gold);background:#fffbf0}
.related-card strong{display:block;font-size:13px;font-weight:700;margin-bottom:4px}
.related-card span{font-size:11px;color:var(--slate2)}
.cta-box{background:linear-gradient(135deg,#d4a853,#c69a3a);border-radius:14px;padding:24px;text-align:center;margin:28px 0}
.cta-box a{color:white;font-weight:700;font-size:15px;text-decoration:none}
footer{background:var(--navy);color:rgba(255,255,255,.7);text-align:center;padding:36px 20px;font-size:12px;line-height:2}
footer a{color:rgba(255,255,255,.8);text-decoration:none}
@media(max-width:640px){.vs-grid{grid-template-columns:1fr;gap:12px}.vs-sep{padding:8px 0}.ct th:nth-child(n+6),.ct td:nth-child(n+6){display:none}}
"""

FONTS = (
    '<link rel="preconnect" href="https://fonts.googleapis.com"/>'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin/>'
    '<link rel="preload" as="style" href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;1,700&family=DM+Sans:wght@400;500;700&display=swap" onload="this.onload=null;this.rel=\'stylesheet\'"/>'
    '<noscript><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;1,700&family=DM+Sans:wght@400;500;700&display=swap"/></noscript>'
)

# ── Page Builders ─────────────────────────────────────────────────────────────

def build_comparison_table(ca, cb, nom_a, nom_b, lang):
    """Build month-by-month comparison table."""
    is_fr = lang == 'fr'
    months = MONTHS_FR if is_fr else MONTHS_EN
    headers = (
        f'<tr><th>{"Mois" if is_fr else "Month"}</th>'
        f'<th colspan="2">{e(nom_a)}</th>'
        f'<th colspan="2">{e(nom_b)}</th>'
        f'<th>{"Meilleur" if is_fr else "Better"}</th></tr>'
    )
    subheaders = (
        f'<tr style="background:#f8f6f0"><td></td>'
        f'<td style="font-size:10px;text-align:center;color:var(--slate2)">Score</td>'
        f'<td style="font-size:10px;text-align:center;color:var(--slate2)">{"Temp" if is_fr else "Temp"}</td>'
        f'<td style="font-size:10px;text-align:center;color:var(--slate2)">Score</td>'
        f'<td style="font-size:10px;text-align:center;color:var(--slate2)">{"Temp" if is_fr else "Temp"}</td>'
        f'<td></td></tr>'
    )
    rows = ''
    for mi in range(1, 13):
        ma = ca.get(mi, {})
        mb = cb.get(mi, {})
        sa = ma.get('score', 0)
        sb = mb.get('score', 0)
        ta = ma.get('tmax', 0)
        tb = mb.get('tmax', 0)
        winner_name = nom_a if sa > sb else (nom_b if sb > sa else '=')
        winner_flag = '🏆' if abs(sa - sb) >= 1 else ('↑' if sa != sb else '—')
        a_cls = ' class="win"' if sa > sb else ''
        b_cls = ' class="win"' if sb > sa else ''
        rows += (
            f'<tr>'
            f'<td>{months[mi-1][:3]}</td>'
            f'<td{a_cls} style="color:{score_color(sa)}">{sa:.1f}</td>'
            f'<td>{ta:.0f}°C</td>'
            f'<td{b_cls} style="color:{score_color(sb)}">{sb:.1f}</td>'
            f'<td>{tb:.0f}°C</td>'
            f'<td style="font-size:12px">{winner_flag} {e(winner_name)}</td>'
            f'</tr>'
        )
    return f'<table class="ct"><thead>{headers}{subheaders}</thead><tbody>{rows}</tbody></table>'


def compute_verdicts(ca, cb, nom_a, nom_b, lang):
    """Generate verdicts per season and overall."""
    is_fr = lang == 'fr'
    wins_a = sum(1 for mi in range(1, 13) if ca.get(mi, {}).get('score', 0) > cb.get(mi, {}).get('score', 0))
    wins_b = sum(1 for mi in range(1, 13) if cb.get(mi, {}).get('score', 0) > ca.get(mi, {}).get('score', 0))
    ties = 12 - wins_a - wins_b

    avg_a = sum(ca.get(mi, {}).get('score', 0) for mi in range(1, 13)) / 12
    avg_b = sum(cb.get(mi, {}).get('score', 0) for mi in range(1, 13)) / 12

    # Best months per destination
    best_a = max(range(1, 13), key=lambda mi: ca.get(mi, {}).get('score', 0))
    best_b = max(range(1, 13), key=lambda mi: cb.get(mi, {}).get('score', 0))

    # Season analysis
    seasons = {
        ('hiver' if is_fr else 'winter'): [12, 1, 2],
        ('printemps' if is_fr else 'spring'): [3, 4, 5],
        ('été' if is_fr else 'summer'): [6, 7, 8],
        ('automne' if is_fr else 'autumn'): [9, 10, 11],
    }
    season_verdicts = []
    for season_name, month_list in seasons.items():
        sa_avg = sum(ca.get(mi, {}).get('score', 0) for mi in month_list) / 3
        sb_avg = sum(cb.get(mi, {}).get('score', 0) for mi in month_list) / 3
        ta_avg = sum(ca.get(mi, {}).get('tmax', 0) for mi in month_list) / 3
        tb_avg = sum(cb.get(mi, {}).get('tmax', 0) for mi in month_list) / 3
        if is_fr:
            winner = nom_a if sa_avg > sb_avg else nom_b
            detail = f"En {season_name}, <strong>{winner}</strong> l'emporte ({sa_avg:.1f} vs {sb_avg:.1f}). Températures : {nom_a} {ta_avg:.0f}°C, {nom_b} {tb_avg:.0f}°C."
        else:
            winner = nom_a if sa_avg > sb_avg else nom_b
            detail = f"In {season_name}, <strong>{winner}</strong> wins ({sa_avg:.1f} vs {sb_avg:.1f}). Temperatures: {nom_a} {ta_avg:.0f}°C, {nom_b} {tb_avg:.0f}°C."
        season_verdicts.append(detail)

    months = MONTHS_FR if is_fr else MONTHS_EN
    if is_fr:
        overall = (f"<strong>{nom_a}</strong> gagne {wins_a} mois sur 12, "
                   f"<strong>{nom_b}</strong> en gagne {wins_b}" +
                   (f" ({ties} ex-æquo)." if ties else ".") +
                   f" Score annuel moyen : {nom_a} {avg_a:.1f}/10, {nom_b} {avg_b:.1f}/10. "
                   f"Meilleur mois : {nom_a} en {months[best_a-1].lower()}, {nom_b} en {months[best_b-1].lower()}.")
    else:
        overall = (f"<strong>{nom_a}</strong> wins {wins_a} months out of 12, "
                   f"<strong>{nom_b}</strong> wins {wins_b}" +
                   (f" ({ties} ties)." if ties else ".") +
                   f" Annual average: {nom_a} {avg_a:.1f}/10, {nom_b} {avg_b:.1f}/10. "
                   f"Best month: {nom_a} in {months[best_a-1]}, {nom_b} in {months[best_b-1]}.")

    return overall, season_verdicts, avg_a, avg_b, best_a, best_b


def generate_comparison(slug_a, slug_b, dests, climate, generated_files):
    """Generate FR + EN comparison pages for a pair."""
    da = dests.get(slug_a)
    db = dests.get(slug_b)
    if not da or not db:
        print(f"  ⚠️  Missing destination: {slug_a if not da else slug_b}")
        return
    ca = climate.get(slug_a, {})
    cb = climate.get(slug_b, {})
    if not ca or not cb:
        print(f"  ⚠️  Missing climate: {slug_a if not ca else slug_b}")
        return

    for lang in ('fr', 'en'):
        is_fr = lang == 'fr'
        nom_a = da['nom_bare'] if is_fr else da.get('nom_en', da['nom_bare'])
        nom_b = db['nom_bare'] if is_fr else db.get('nom_en', db['nom_bare'])
        slug_en_a = da.get('slug_en', slug_a)
        slug_en_b = db.get('slug_en', slug_b)
        flag_a, flag_b = da.get('flag', ''), db.get('flag', '')

        if is_fr:
            filename = f"{slug_a}-ou-{slug_b}-climat.html"
            filepath = ROOT / filename
            canonical = f"https://bestdateweather.com/{filename}"
            alt_filename = f"{slug_en_a}-vs-{slug_en_b}-weather.html"
            hreflang_fr = canonical
            hreflang_en = f"https://bestdateweather.com/en/{alt_filename}"
        else:
            filename = f"{slug_en_a}-vs-{slug_en_b}-weather.html"
            filepath = ROOT / 'en' / filename
            canonical = f"https://bestdateweather.com/en/{filename}"
            alt_filename = f"{slug_a}-ou-{slug_b}-climat.html"
            hreflang_fr = f"https://bestdateweather.com/{alt_filename}"
            hreflang_en = canonical

        # Scores
        avg_a_score = sum(ca.get(mi, {}).get('score', 0) for mi in range(1, 13)) / 12
        avg_b_score = sum(cb.get(mi, {}).get('score', 0) for mi in range(1, 13)) / 12
        best_mi_a = max(range(1, 13), key=lambda mi: ca.get(mi, {}).get('score', 0))
        best_mi_b = max(range(1, 13), key=lambda mi: cb.get(mi, {}).get('score', 0))

        months = MONTHS_FR if is_fr else MONTHS_EN
        flag_prefix = '' if is_fr else '../'

        # Content
        if is_fr:
            title = f"{nom_a} ou {nom_b} ? Comparatif météo mois par mois [{YEAR}]"
            desc = (f"{nom_a} ou {nom_b} : quel climat est meilleur ? Comparaison mois par mois "
                    f"sur 10 ans. {nom_a} : {avg_a_score:.1f}/10, {nom_b} : {avg_b_score:.1f}/10.")
            h1 = f"{nom_a} <em>ou</em> {nom_b} ?"
            hero_sub = f"Comparaison climatique complète — 12 mois, 10 ans de données, score objectif"
            href_a = f"meilleure-periode-{slug_a}.html"
            href_b = f"meilleure-periode-{slug_b}.html"
        else:
            title = f"{nom_a} vs {nom_b} — Weather Comparison [{YEAR}]"
            desc = (f"{nom_a} vs {nom_b}: which has better weather? Month-by-month comparison "
                    f"over 10 years. {nom_a}: {avg_a_score:.1f}/10, {nom_b}: {avg_b_score:.1f}/10.")
            h1 = f"{nom_a} <em>vs</em> {nom_b}"
            hero_sub = f"Complete climate comparison — 12 months, 10 years of data, objective scores"
            href_a = f"best-time-to-visit-{slug_en_a}.html"
            href_b = f"best-time-to-visit-{slug_en_b}.html"

        # VS cards
        vs_cards = f"""<div class="vs-grid">
<div class="vs-card">
<img src="{flag_prefix}flags/{flag_a}.png" width="24" height="18" alt="" style="border-radius:2px;margin-bottom:8px">
<h3><a href="{href_a}" style="color:var(--navy);text-decoration:none">{e(nom_a)}</a></h3>
<div class="big-score" style="color:{score_color(avg_a_score)}">{avg_a_score:.1f}<span style="font-size:16px;color:var(--slate2)">/10</span></div>
<div class="vs-stat">{"Meilleur mois" if is_fr else "Best month"} : <strong>{months[best_mi_a-1]}</strong> ({ca[best_mi_a]['score']:.1f})</div>
<div class="vs-stat">{"Temp. max" if is_fr else "Max temp"} : <strong>{ca[best_mi_a]['tmax']:.0f}°C</strong></div>
</div>
<div class="vs-sep">VS</div>
<div class="vs-card">
<img src="{flag_prefix}flags/{flag_b}.png" width="24" height="18" alt="" style="border-radius:2px;margin-bottom:8px">
<h3><a href="{href_b}" style="color:var(--navy);text-decoration:none">{e(nom_b)}</a></h3>
<div class="big-score" style="color:{score_color(avg_b_score)}">{avg_b_score:.1f}<span style="font-size:16px;color:var(--slate2)">/10</span></div>
<div class="vs-stat">{"Meilleur mois" if is_fr else "Best month"} : <strong>{months[best_mi_b-1]}</strong> ({cb[best_mi_b]['score']:.1f})</div>
<div class="vs-stat">{"Temp. max" if is_fr else "Max temp"} : <strong>{cb[best_mi_b]['tmax']:.0f}°C</strong></div>
</div>
</div>"""

        table = build_comparison_table(ca, cb, nom_a, nom_b, lang)
        overall, season_verdicts, _, _, _, _ = compute_verdicts(ca, cb, nom_a, nom_b, lang)

        verdict_html = f"""<div class="verdict">
<h3>{"🏆 Verdict global" if is_fr else "🏆 Overall Verdict"}</h3>
<p>{overall}</p>
</div>
<div class="verdict">
<h3>{"📅 Par saison" if is_fr else "📅 By Season"}</h3>
{"".join(f'<p>{v}</p>' for v in season_verdicts)}
</div>"""

        # Schemas
        breadcrumb = json.dumps({
            "@context": "https://schema.org", "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1,
                 "name": "Accueil" if is_fr else "Home",
                 "item": "https://bestdateweather.com/" if is_fr else "https://bestdateweather.com/en/app.html"},
                {"@type": "ListItem", "position": 2,
                 "name": f"{nom_a} {'ou' if is_fr else 'vs'} {nom_b}", "item": canonical}
            ]
        }, ensure_ascii=False)

        faq_items = []
        if is_fr:
            faq_items.append({"@type": "Question",
                "name": f"{nom_a} ou {nom_b} : où fait-il meilleur ?",
                "acceptedAnswer": {"@type": "Answer", "text": overall.replace('<strong>', '').replace('</strong>', '')}})
            faq_items.append({"@type": "Question",
                "name": f"Quand partir à {nom_a} plutôt qu'à {nom_b} ?",
                "acceptedAnswer": {"@type": "Answer",
                    "text": f"{nom_a} est meilleur en {months[best_mi_a-1].lower()} ({ca[best_mi_a]['score']:.1f}/10). {nom_b} est meilleur en {months[best_mi_b-1].lower()} ({cb[best_mi_b]['score']:.1f}/10)."}})
        else:
            faq_items.append({"@type": "Question",
                "name": f"{nom_a} or {nom_b}: which has better weather?",
                "acceptedAnswer": {"@type": "Answer", "text": overall.replace('<strong>', '').replace('</strong>', '')}})
            faq_items.append({"@type": "Question",
                "name": f"When to visit {nom_a} instead of {nom_b}?",
                "acceptedAnswer": {"@type": "Answer",
                    "text": f"{nom_a} is best in {months[best_mi_a-1]} ({ca[best_mi_a]['score']:.1f}/10). {nom_b} is best in {months[best_mi_b-1]} ({cb[best_mi_b]['score']:.1f}/10)."}})

        faq_schema = json.dumps({"@context": "https://schema.org", "@type": "FAQPage",
                                  "mainEntity": faq_items}, ensure_ascii=False)

        # Related
        related_cards = []
        for slug, nom in [(slug_a, nom_a), (slug_b, nom_b)]:
            if is_fr:
                href = f"meilleure-periode-{slug}.html"
                label = f"{"Meilleure période" } {nom}"
            else:
                sle = dests[slug].get('slug_en', slug)
                href = f"best-time-to-visit-{sle}.html"
                label = f"Best time to visit {nom}"
            related_cards.append(f'<a href="{href}" class="related-card"><strong>{e(label)}</strong><span>{"Guide complet" if is_fr else "Full guide"}</span></a>')

        related_html = (f'<div class="section"><div class="eyebrow">{"Explorer" if is_fr else "Explore"}</div>'
                        f'<h2 class="sec-title">{"Guides détaillés" if is_fr else "Detailed Guides"}</h2>'
                        f'<div class="related-pages">{"".join(related_cards)}</div></div>')

        # CTA
        if is_fr:
            cta = '<div class="cta-box"><a href="index.html">🎯 Choisir une date précise pour votre voyage →</a></div>'
        else:
            cta = '<div class="cta-box"><a href="app.html">🎯 Choose a specific date for your trip →</a></div>'

        # Footer
        if is_fr:
            alt_link_file = f"en/{alt_filename}"
            footer = f"""<footer>
<p style="font-weight:700;margin-bottom:8px">bestdateweather.com</p>
<p><a href="https://open-meteo.com/" rel="noopener">Données Open-Meteo</a> · ECMWF, DWD, NOAA · CC BY 4.0</p>
<p style="margin-top:8px"><a href="index.html">Application météo</a> · <a href="{alt_link_file}"><img src="flags/gb.png" width="20" height="15" alt="" style="vertical-align:middle;border-radius:2px"> English</a></p>
<p style="margin-top:8px;font-size:11px;opacity:.6"><a href="mentions-legales.html">Mentions légales</a></p>
</footer>"""
        else:
            alt_link_file = f"../{alt_filename}"
            footer = f"""<footer>
<p style="font-weight:700;margin-bottom:8px">bestdateweather.com</p>
<p><a href="https://open-meteo.com/" rel="noopener">Data by Open-Meteo</a> · ECMWF, DWD, NOAA · CC BY 4.0</p>
<p style="margin-top:8px"><a href="app.html">Weather app</a> · <a href="{alt_link_file}"><img src="../flags/fr.png" width="20" height="15" alt="" style="vertical-align:middle;border-radius:2px"> Français</a></p>
<p style="margin-top:8px;font-size:11px;opacity:.6"><a href="../mentions-legales.html">Legal</a></p>
</footer>"""

        page_html = f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="UTF-8"/><meta name="viewport" content="width=device-width,initial-scale=1.0"/>
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}"/>
<link rel="canonical" href="{canonical}"/>
<link rel="alternate" hreflang="fr" href="{hreflang_fr}"/>
<link rel="alternate" hreflang="en" href="{hreflang_en}"/>
<link rel="alternate" hreflang="x-default" href="{hreflang_en}"/>
<meta property="og:type" content="article"/>
<meta property="og:title" content="{e(title)}"/>
<meta property="og:description" content="{e(desc)}"/>
<meta property="og:url" content="{canonical}"/>
<style>{CSS}</style>
{FONTS}
<script type="application/ld+json">{breadcrumb}</script>
<script type="application/ld+json">{faq_schema}</script>
</head>
<body>
<header class="hero">
<div class="hero-eyebrow">{"Comparatif climatique · 10 ans de données · " if is_fr else "Climate comparison · 10 years of data · "}{YEAR}</div>
<h1 class="hero-title">{h1}</h1>
<p class="hero-sub">{hero_sub}</p>
</header>
<main class="page">
{vs_cards}
<div class="section">
<div class="eyebrow">{"Mois par mois" if is_fr else "Month by month"}</div>
<h2 class="sec-title">{"Comparaison climatique détaillée" if is_fr else "Detailed Climate Comparison"}</h2>
<p class="sec-intro">{"Score météo sur 10, basé sur températures, pluie et ensoleillement. Données 10 ans Open-Meteo." if is_fr else "Weather score out of 10, based on temperature, rain and sunshine. 10-year Open-Meteo data."}</p>
<div style="overflow-x:auto">{table}</div>
</div>
{verdict_html}
{cta}
{related_html}
</main>
{footer}
</body></html>"""

        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(page_html)

        generated_files.append({
            'canonical': canonical, 'hreflang_fr': hreflang_fr, 'hreflang_en': hreflang_en,
            'lang': lang, 'filename': filename
        })


def update_sitemaps(files):
    """Append comparison pages to sitemaps."""
    fr_files = [f for f in files if f['lang'] == 'fr']
    en_files = [f for f in files if f['lang'] == 'en']

    for sitemap_file, pages in [('sitemap-fr.xml', fr_files), ('sitemap-en.xml', en_files)]:
        path = ROOT / sitemap_file
        if not path.exists():
            continue
        content = path.read_text(encoding='utf-8')
        added = 0
        for page in pages:
            if page['canonical'] in content:
                continue
            entry = f"""  <url>
    <loc>{page['canonical']}</loc>
    <lastmod>{TODAY}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.7</priority>
    <xhtml:link rel="alternate" hreflang="fr" href="{page['hreflang_fr']}"/>
    <xhtml:link rel="alternate" hreflang="en" href="{page['hreflang_en']}"/>
    <xhtml:link rel="alternate" hreflang="x-default" href="{page['hreflang_en']}"/>
  </url>"""
            content = content.replace('</urlset>', entry + '\n</urlset>')
            added += 1
        path.write_text(content, encoding='utf-8')
        if added:
            print(f"  📍 {sitemap_file}: +{added} URLs")


if __name__ == '__main__':
    print(f"generate_comparatifs.py — {len(PAIRS)} comparison pairs")
    dests = load_destinations()
    climate = load_climate()
    print(f"📦 {len(dests)} destinations\n")

    generated = []
    for slug_a, slug_b in PAIRS:
        generate_comparison(slug_a, slug_b, dests, climate, generated)
        fr_name = f"{slug_a}-ou-{slug_b}-climat.html"
        en_a = dests.get(slug_a, {}).get('slug_en', slug_a)
        en_b = dests.get(slug_b, {}).get('slug_en', slug_b)
        en_name = f"{en_a}-vs-{en_b}-weather.html"
        print(f"  ✅ {fr_name}")
        print(f"  ✅ en/{en_name}")

    fr_count = sum(1 for f in generated if f['lang'] == 'fr')
    en_count = sum(1 for f in generated if f['lang'] == 'en')
    print(f"\n📄 {fr_count} FR + {en_count} EN comparison pages")

    update_sitemaps(generated)
    print("\n✅ Done")
