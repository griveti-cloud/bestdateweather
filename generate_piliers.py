#!/usr/bin/env python3
"""
Generate 24 seasonal pillar pages (12 FR + 12 EN):
  FR: ou-partir-en-janvier.html … ou-partir-en-decembre.html
  EN: en/where-to-go-in-january.html … en/where-to-go-in-december.html

Each page ranks top 25 destinations for that month by weather score.
Usage: python3 generate_piliers.py
"""

import csv, html as html_mod, json
from pathlib import Path
from datetime import date

ROOT = Path(__file__).parent
TODAY = date.today().isoformat()
YEAR = date.today().year

# ── Constants ─────────────────────────────────────────────────────────────────

MONTHS_FR = ['Janvier','Février','Mars','Avril','Mai','Juin',
             'Juillet','Août','Septembre','Octobre','Novembre','Décembre']
MONTHS_EN = ['January','February','March','April','May','June',
             'July','August','September','October','November','December']
MONTH_SLUG_FR = ['janvier','fevrier','mars','avril','mai','juin',
                 'juillet','aout','septembre','octobre','novembre','decembre']
MONTH_SLUG_EN = ['january','february','march','april','may','june',
                 'july','august','september','october','november','december']
MONTH_URL_FR = ['janvier','fevrier','mars','avril','mai','juin',
                'juillet','aout','septembre','octobre','novembre','decembre']
MONTH_URL_EN = ['january','february','march','april','may','june',
                'july','august','september','october','november','december']

SEASON_FR = {0:'hiver',1:'hiver',2:'printemps',3:'printemps',4:'printemps',5:'été',
             6:'été',7:'été',8:'automne',9:'automne',10:'automne',11:'hiver'}
SEASON_EN = {0:'winter',1:'winter',2:'spring',3:'spring',4:'spring',5:'summer',
             6:'summer',7:'summer',8:'autumn',9:'autumn',10:'autumn',11:'winter'}

TOP_N = 25

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

# ── Helpers ───────────────────────────────────────────────────────────────────

def e(s):
    return html_mod.escape(str(s))

def rank_icon(i):
    if i == 1: return '🥇'
    if i == 2: return '🥈'
    if i == 3: return '🥉'
    return str(i)

def score_class(s):
    if s >= 8: return '#16a34a'
    if s >= 6: return '#d4a853'
    return '#dc2626'

def get_rankings(climate, dests, month_idx):
    """Return top destinations for given month (1-indexed), sorted by score desc."""
    entries = []
    for slug, dest in dests.items():
        if slug not in climate or month_idx not in climate[slug]:
            continue
        m = climate[slug][month_idx]
        entries.append({
            'slug_fr': slug,
            'slug_en': dest.get('slug_en', slug),
            'nom_bare': dest.get('nom_bare', slug),
            'nom_en': dest.get('nom_en', dest.get('nom_bare', slug)),
            'pays': dest.get('pays', ''),
            'flag': dest.get('flag', ''),
            'score': m['score'],
            'tmin': m['tmin'],
            'tmax': m['tmax'],
            'rain_pct': m['rain_pct'],
            'sun_h': m['sun_h'],
        })
    entries.sort(key=lambda x: (-x['score'], x['nom_bare']))
    return entries[:TOP_N]

# ── CSS ───────────────────────────────────────────────────────────────────────

CSS = r"""
*{margin:0;padding:0;box-sizing:border-box}
:root{--navy:#1a2332;--gold:#d4a853;--cream:#faf6ef;--cream2:#ede4d3;--text:#2c3e50;--slate:#5a6c7d;--slate2:#8899a6}
body{font-family:'DM Sans',system-ui,sans-serif;background:var(--cream);color:var(--text);line-height:1.6}
.hero{background:var(--navy);color:white;padding:48px 20px 36px;text-align:center}
.hero-eyebrow{font-size:11px;text-transform:uppercase;letter-spacing:2.5px;color:var(--gold);margin-bottom:12px;font-weight:700}
.hero-title{font-family:'Playfair Display',Georgia,serif;font-size:clamp(24px,5vw,38px);margin-bottom:10px;line-height:1.2}
.hero-title em{color:var(--gold);font-style:italic}
.hero-sub{font-size:15px;opacity:.75;max-width:600px;margin:0 auto 20px}
.hero-stats{display:flex;justify-content:center;gap:36px;margin-top:16px}
.hstat{text-align:center}.hstat-val{display:block;font-size:22px;font-weight:700;color:var(--gold)}.hstat-lbl{font-size:11px;opacity:.6;text-transform:uppercase;letter-spacing:1px}
.page{max-width:960px;margin:0 auto;padding:28px 20px 40px}
.section{margin-bottom:36px}
.eyebrow{font-size:10px;text-transform:uppercase;letter-spacing:2px;color:var(--gold);font-weight:700;margin-bottom:6px}
.sec-title{font-family:'Playfair Display',Georgia,serif;font-size:clamp(18px,4vw,24px);margin-bottom:8px}
.sec-intro{font-size:14px;color:var(--slate);margin-bottom:18px}
.rt{width:100%;border-collapse:collapse;font-size:13px}
.rt th{background:var(--navy);color:white;padding:10px 12px;text-align:left;font-size:11px;text-transform:uppercase;letter-spacing:.5px;font-weight:700;position:sticky;top:0}
.rt td{padding:10px 12px;border-bottom:1px solid var(--cream2);vertical-align:middle}
.rt tr:hover{background:#fef9f0}
.rt .rank{font-weight:700;font-size:15px;text-align:center;width:48px}
.rt .sc{font-weight:700;color:var(--navy);font-size:14px;white-space:nowrap}
.dest-link{color:var(--text);text-decoration:none;font-weight:600}
.dest-link:hover{color:var(--gold)}
.region-tag{display:inline-block;font-size:10px;color:var(--slate2);background:var(--cream);padding:2px 8px;border-radius:10px;margin-left:8px;vertical-align:middle}
.month-nav{display:flex;gap:8px;flex-wrap:wrap;justify-content:center;margin-bottom:28px}
.month-nav a{padding:8px 14px;border-radius:8px;font-size:12px;font-weight:600;text-decoration:none;background:white;border:1.5px solid var(--cream2);color:var(--navy)}
.month-nav a.active{background:var(--gold);color:white;border-color:var(--gold)}
.month-nav a:hover{border-color:var(--gold)}
.cta-box{background:linear-gradient(135deg,#d4a853,#c69a3a);border-radius:14px;padding:24px;text-align:center;margin:28px 0}
.cta-box a{color:white;font-weight:700;font-size:15px;text-decoration:none}
.related-pages{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:12px;margin-top:16px}
.related-card{background:white;border:1.5px solid var(--cream2);border-radius:12px;padding:16px;text-decoration:none;color:var(--text);display:block}
.related-card:hover{border-color:var(--gold);background:#fffbf0}
.related-card strong{display:block;font-size:13px;font-weight:700;margin-bottom:4px}
.related-card span{font-size:11px;color:var(--slate2)}
footer{background:var(--navy);color:rgba(255,255,255,.7);text-align:center;padding:36px 20px;font-size:12px;line-height:2}
footer a{color:rgba(255,255,255,.8);text-decoration:none}
@media(max-width:640px){.rt th:nth-child(5),.rt td:nth-child(5){display:none}.hero-stats{gap:20px}}
"""

FONTS = (
    '<link rel="preconnect" href="https://fonts.googleapis.com"/>'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin/>'
    '<link rel="preload" as="style" href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;1,700&family=DM+Sans:wght@400;500;700&display=swap" onload="this.onload=null;this.rel=\'stylesheet\'"/>'
    '<noscript><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;1,700&family=DM+Sans:wght@400;500;700&display=swap"/></noscript>'
)

# ── Page Builders ─────────────────────────────────────────────────────────────

def build_table(entries, lang, mi):
    """Build ranking table for a given month."""
    is_fr = lang == 'fr'
    rows = ''
    for i, entry in enumerate(entries, 1):
        slug = entry['slug_fr'] if is_fr else entry['slug_en']
        nom = entry['nom_bare'] if is_fr else entry['nom_en']
        month_slug = MONTH_URL_FR[mi] if is_fr else MONTH_URL_EN[mi]
        href = f"{slug}-meteo-{month_slug}.html" if is_fr else f"{slug}-weather-{month_slug}.html"
        flag_img = f'<img src="{"" if is_fr else "../"}flags/{entry["flag"]}.png" width="16" height="12" alt="" style="vertical-align:middle;margin-right:6px;border-radius:1px">'
        sc = entry['score']
        sc_color = score_class(sc)
        rows += (
            f'<tr>'
            f'<td class="rank">{rank_icon(i)}</td>'
            f'<td>{flag_img}<a href="{href}" class="dest-link">{e(nom)}</a></td>'
            f'<td class="sc" style="color:{sc_color}">{sc:.1f}<span>/10</span></td>'
            f'<td>{entry["tmin"]:.0f}–{entry["tmax"]:.0f}°C</td>'
            f'<td>{entry["rain_pct"]:.0f}%</td>'
            f'<td>{entry["sun_h"]:.1f}h</td>'
            f'</tr>'
        )
    headers = {
        'fr': ('#', 'Destination', 'Score', 'Temp.', 'Pluie', 'Soleil/j'),
        'en': ('#', 'Destination', 'Score', 'Temp.', 'Rain', 'Sun/day'),
    }
    h = headers[lang]
    return (
        f'<table class="rt" aria-label="{"Classement" if is_fr else "Ranking"}">'
        f'<thead><tr>{"".join(f"<th>{c}</th>" for c in h)}</tr></thead>'
        f'<tbody>{rows}</tbody></table>'
    )

def build_month_nav(mi, lang):
    """Build month navigation bar."""
    is_fr = lang == 'fr'
    months = MONTHS_FR if is_fr else MONTHS_EN
    slugs = MONTH_SLUG_FR if is_fr else MONTH_SLUG_EN
    prefix = 'ou-partir-en-' if is_fr else 'where-to-go-in-'
    links = ''
    for i in range(12):
        active = ' class="active"' if i == mi else ''
        links += f'<a href="{prefix}{slugs[i]}.html"{active}>{months[i][:3]}</a>'
    return f'<nav class="month-nav" aria-label="{"Mois" if is_fr else "Months"}">{links}</nav>'

def build_related(mi, lang):
    """Build related ranking cards."""
    is_fr = lang == 'fr'
    cards = []
    # Adjacent months
    for offset in [-1, 1]:
        adj = (mi + offset) % 12
        month_name = MONTHS_FR[adj] if is_fr else MONTHS_EN[adj]
        slug = MONTH_SLUG_FR[adj] if is_fr else MONTH_SLUG_EN[adj]
        prefix = 'ou-partir-en-' if is_fr else 'where-to-go-in-'
        label = f'{"Où partir en" if is_fr else "Where to go in"} {month_name.lower()}'
        cards.append(f'<a href="{prefix}{slug}.html" class="related-card"><strong>{label}</strong><span>Top {TOP_N} {"destinations" if is_fr else "destinations"}</span></a>')
    # General ranking
    if is_fr:
        cards.append('<a href="classement-destinations-meteo-2026.html" class="related-card"><strong>🌍 Classement mondial 2026</strong><span>Toutes destinations</span></a>')
    else:
        cards.append('<a href="best-destinations-weather-ranking-2026.html" class="related-card"><strong>🌍 World ranking 2026</strong><span>All destinations</span></a>')
    return f'<div class="section"><div class="eyebrow">{"Explorer aussi" if is_fr else "Also explore"}</div><h2 class="sec-title">{"Autres classements" if is_fr else "Other rankings"}</h2><div class="related-pages">{"".join(cards)}</div></div>'


def generate_page(mi, lang, dests, climate):
    """Generate one pillar page for month mi (0-indexed) in given language."""
    is_fr = lang == 'fr'
    month_name = MONTHS_FR[mi] if is_fr else MONTHS_EN[mi]
    month_slug = MONTH_SLUG_FR[mi] if is_fr else MONTH_SLUG_EN[mi]
    season = SEASON_FR[mi] if is_fr else SEASON_EN[mi]

    entries = get_rankings(climate, dests, mi + 1)  # climate.csv is 1-indexed
    if not entries:
        print(f"  ⚠️  No data for month {mi}")
        return

    top = entries[0]
    avg_score = sum(x['score'] for x in entries[:10]) / 10
    avg_temp = sum(x['tmax'] for x in entries[:10]) / 10

    # File paths
    if is_fr:
        filename = f'ou-partir-en-{month_slug}.html'
        filepath = ROOT / filename
        canonical = f'https://bestdateweather.com/{filename}'
        alt_file = f'where-to-go-in-{MONTH_SLUG_EN[mi]}.html'
        hreflang_fr = canonical
        hreflang_en = f'https://bestdateweather.com/en/{alt_file}'
    else:
        filename = f'where-to-go-in-{month_slug}.html'
        filepath = ROOT / 'en' / filename
        canonical = f'https://bestdateweather.com/en/{filename}'
        alt_file = f'ou-partir-en-{MONTH_SLUG_FR[mi]}.html'
        hreflang_fr = f'https://bestdateweather.com/{alt_file}'
        hreflang_en = canonical

    # Content
    if is_fr:
        title = f"Où partir en {month_name.lower()} {YEAR} ? Top {TOP_N} destinations météo"
        desc = (f"Où partir en {month_name.lower()} {YEAR} ? Classement des {TOP_N} meilleures destinations "
                f"par score météo. N°1 : {top['nom_bare']} ({top['score']:.1f}/10, {top['tmax']:.0f}°C). "
                f"Données 10 ans Open-Meteo.")
        h1 = f"Où partir en <em>{month_name.lower()}</em> ?"
        hero_sub = (f"Les {TOP_N} meilleures destinations météo pour {month_name.lower()} {YEAR}, "
                    f"classées par score climatique sur 10 ans de données.")
        sec_eyebrow = f"Classement {month_name} {YEAR}"
        sec_title = f"Top {TOP_N} destinations en {month_name.lower()}"
        sec_intro = (f"Score moyen du top 10 : <strong>{avg_score:.1f}/10</strong> · "
                     f"Température moyenne : <strong>{avg_temp:.0f}°C</strong>")
        cta_text = f"🎯 Choisir une date précise pour votre voyage en {month_name.lower()}"
        cta_href = "index.html"
    else:
        title = f"Where to Go in {month_name} {YEAR} — Top {TOP_N} Weather Destinations"
        desc = (f"Where to go in {month_name} {YEAR}? Top {TOP_N} destinations ranked by weather score. "
                f"#1: {top['nom_en']} ({top['score']:.1f}/10, {top['tmax']:.0f}°C). "
                f"Based on 10 years of Open-Meteo data.")
        h1 = f"Where to Go in <em>{month_name}</em>"
        hero_sub = (f"The {TOP_N} best weather destinations for {month_name} {YEAR}, "
                    f"ranked by climate score based on 10 years of data.")
        sec_eyebrow = f"{month_name} {YEAR} ranking"
        sec_title = f"Top {TOP_N} destinations in {month_name}"
        sec_intro = (f"Top 10 average score: <strong>{avg_score:.1f}/10</strong> · "
                     f"Average temperature: <strong>{avg_temp:.0f}°C</strong>")
        cta_text = f"🎯 Choose a specific date for your {month_name} trip"
        cta_href = "app.html"

    table = build_table(entries, lang, mi)
    month_nav = build_month_nav(mi, lang)
    related = build_related(mi, lang)

    # Schema.org
    breadcrumb = json.dumps({
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1,
             "name": "Accueil" if is_fr else "Home",
             "item": "https://bestdateweather.com/" if is_fr else "https://bestdateweather.com/en/app.html"},
            {"@type": "ListItem", "position": 2,
             "name": f"{'Où partir en' if is_fr else 'Where to go in'} {month_name.lower() if is_fr else month_name}",
             "item": canonical}
        ]
    }, ensure_ascii=False)

    itemlist = json.dumps({
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": title,
        "numberOfItems": len(entries),
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": i + 1,
                "name": entry['nom_bare'] if is_fr else entry['nom_en'],
                "url": (f"https://bestdateweather.com/{entry['slug_fr']}-meteo-{MONTH_URL_FR[mi]}.html" if is_fr
                        else f"https://bestdateweather.com/en/{entry['slug_en']}-weather-{MONTH_URL_EN[mi]}.html")
            }
            for i, entry in enumerate(entries)
        ]
    }, ensure_ascii=False)

    faq_items = []
    if is_fr:
        faq_items.append({"@type": "Question",
            "name": f"Quelle est la meilleure destination en {month_name.lower()} ?",
            "acceptedAnswer": {"@type": "Answer",
                "text": f"{top['nom_bare']} est la destination n°1 en {month_name.lower()} avec un score de {top['score']:.1f}/10 et {top['tmax']:.0f}°C."}})
        faq_items.append({"@type": "Question",
            "name": f"Où partir au soleil en {month_name.lower()} ?",
            "acceptedAnswer": {"@type": "Answer",
                "text": f"Les destinations les plus ensoleillées en {month_name.lower()} sont {entries[0]['nom_bare']}, {entries[1]['nom_bare']} et {entries[2]['nom_bare']}, avec des scores de {entries[0]['score']:.1f} à {entries[2]['score']:.1f}/10."}})
    else:
        faq_items.append({"@type": "Question",
            "name": f"What is the best destination in {month_name}?",
            "acceptedAnswer": {"@type": "Answer",
                "text": f"{top['nom_en']} is the #1 destination in {month_name} with a score of {top['score']:.1f}/10 and {top['tmax']:.0f}°C."}})
        faq_items.append({"@type": "Question",
            "name": f"Where is it sunny in {month_name}?",
            "acceptedAnswer": {"@type": "Answer",
                "text": f"The sunniest destinations in {month_name} are {entries[0]['nom_en']}, {entries[1]['nom_en']} and {entries[2]['nom_en']}, with scores from {entries[2]['score']:.1f} to {entries[0]['score']:.1f}/10."}})

    faq_schema = json.dumps({
        "@context": "https://schema.org", "@type": "FAQPage",
        "mainEntity": faq_items
    }, ensure_ascii=False)

    # Footer
    if is_fr:
        footer = f"""<footer>
<p style="font-weight:700;margin-bottom:8px">bestdateweather.com</p>
<p><a href="https://open-meteo.com/" rel="noopener">Données Open-Meteo</a> · ECMWF, DWD, NOAA · CC BY 4.0</p>
<p style="margin-top:8px"><a href="index.html">Application météo</a> · <a href="en/{alt_file}"><img src="flags/gb.png" width="20" height="15" alt="" style="vertical-align:middle;border-radius:2px"> English</a></p>
<p style="margin-top:8px;font-size:11px;opacity:.6"><a href="mentions-legales.html">Mentions légales</a></p>
</footer>"""
    else:
        footer = f"""<footer>
<p style="font-weight:700;margin-bottom:8px">bestdateweather.com</p>
<p><a href="https://open-meteo.com/" rel="noopener">Data by Open-Meteo</a> · ECMWF, DWD, NOAA · CC BY 4.0</p>
<p style="margin-top:8px"><a href="app.html">Weather app</a> · <a href="../{alt_file}"><img src="../flags/fr.png" width="20" height="15" alt="" style="vertical-align:middle;border-radius:2px"> Français</a></p>
<p style="margin-top:8px;font-size:11px;opacity:.6"><a href="../mentions-legales.html">Legal</a></p>
</footer>"""

    flag_prefix = '' if is_fr else '../'

    page_html = f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="UTF-8"/><meta name="viewport" content="width=device-width,initial-scale=1.0"/>
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}"/>
<link rel="canonical" href="{canonical}"/>
<link rel="alternate" hreflang="fr" href="{hreflang_fr}"/>
<link rel="alternate" hreflang="en" href="{hreflang_en}"/>
<meta property="og:type" content="article"/>
<meta property="og:title" content="{e(title)}"/>
<meta property="og:description" content="{e(desc)}"/>
<meta property="og:url" content="{canonical}"/>
<style>{CSS}</style>
{FONTS}
<script type="application/ld+json">{breadcrumb}</script>
<script type="application/ld+json">{itemlist}</script>
<script type="application/ld+json">{faq_schema}</script>
</head>
<body>
<header class="hero">
<div class="hero-eyebrow">{"Étude climatique · 10 ans de données · " if is_fr else "Climate study · 10 years of data · "}{YEAR}</div>
<h1 class="hero-title">{h1}</h1>
<p class="hero-sub">{hero_sub}</p>
<div class="hero-stats">
<div class="hstat"><span class="hstat-val">{top['score']:.1f}</span><span class="hstat-lbl">{"Score n°1" if is_fr else "#1 Score"}</span></div>
<div class="hstat"><span class="hstat-val">{TOP_N}</span><span class="hstat-lbl">Destinations</span></div>
<div class="hstat"><span class="hstat-val">{avg_temp:.0f}°C</span><span class="hstat-lbl">{"Moy. top 10" if is_fr else "Top 10 avg"}</span></div>
</div>
</header>
<main class="page">
{month_nav}
<div class="section">
<div class="eyebrow">{sec_eyebrow}</div>
<h2 class="sec-title">{sec_title}</h2>
<p class="sec-intro">{sec_intro}</p>
<div style="overflow-x:auto">{table}</div>
</div>
<div class="cta-box"><a href="{cta_href}">{cta_text} →</a></div>
{related}
</main>
{footer}
</body></html>"""

    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(page_html)

    return filename, canonical, hreflang_fr, hreflang_en


# ── Sitemap Update ────────────────────────────────────────────────────────────

def update_sitemaps(fr_pages, en_pages):
    """Append new pillar pages to existing sitemaps if not already present."""
    for sitemap_file, pages in [('sitemap-fr.xml', fr_pages), ('sitemap-en.xml', en_pages)]:
        path = ROOT / sitemap_file
        if not path.exists():
            print(f"  ⚠️  {sitemap_file} not found, skipping")
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
    <priority>0.8</priority>
    <xhtml:link rel="alternate" hreflang="fr" href="{page['hreflang_fr']}"/>
    <xhtml:link rel="alternate" hreflang="en" href="{page['hreflang_en']}"/>
  </url>"""
            content = content.replace('</urlset>', entry + '\n</urlset>')
            added += 1
        path.write_text(content, encoding='utf-8')
        if added:
            print(f"  📍 {sitemap_file}: +{added} URLs")


# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    print("generate_piliers.py — seasonal pillar pages")
    dests = load_destinations()
    climate = load_climate()
    print(f"📦 {len(dests)} destinations, {len(climate)} climate entries\n")

    fr_pages = []
    en_pages = []

    for mi in range(12):
        # FR
        result = generate_page(mi, 'fr', dests, climate)
        if result:
            filename, canonical, hreflang_fr, hreflang_en = result
            fr_pages.append({'canonical': canonical, 'hreflang_fr': hreflang_fr, 'hreflang_en': hreflang_en})
            print(f"  ✅ {filename}")

        # EN
        result = generate_page(mi, 'en', dests, climate)
        if result:
            filename, canonical, hreflang_fr, hreflang_en = result
            en_pages.append({'canonical': canonical, 'hreflang_fr': hreflang_fr, 'hreflang_en': hreflang_en})
            print(f"  ✅ en/{filename}")

    print(f"\n📄 {len(fr_pages)} FR + {len(en_pages)} EN pillar pages generated")

    update_sitemaps(fr_pages, en_pages)
    print("\n✅ Done")
