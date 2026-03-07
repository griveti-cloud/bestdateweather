#!/usr/bin/env python3
"""
Generate 24 seasonal pillar pages (12 FR + 12 EN):
  FR: ou-partir-en-janvier.html … ou-partir-en-decembre.html
  EN: en/where-to-go-in-january.html … en/where-to-go-in-december.html

Each page ranks top 25 destinations for that month by weather score.
Usage: python3 generate_piliers.py
"""

import csv, html as html_mod, json, sys, os
from pathlib import Path
from datetime import date

sys.path.insert(0, str(Path(__file__).parent))
from lib.page_config import load_locale

ROOT = Path(__file__).parent
TODAY = date.today().isoformat()
YEAR = date.today().year

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

REGION_CHILDREN = {
    'canaries': {'lanzarote', 'fuerteventura', 'gran-canaria', 'tenerife',
                 'la-palma', 'la-gomera', 'el-hierro'},
}

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
    # Remove region parents when a child island is also ranked
    ranked = {e['slug_fr'] for e in entries}
    remove = {p for p, ch in REGION_CHILDREN.items() if p in ranked and ranked & ch}
    if remove:
        entries = [e for e in entries if e['slug_fr'] not in remove]
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
.nav-share{display:none}
@media(pointer:coarse),(max-width:768px){.nav-share{display:flex}}
@media(max-width:640px){.rt th:nth-child(5),.rt td:nth-child(5){display:none}.hero-stats{gap:20px}}
"""

FONTS = (
    '<link rel="preconnect" href="https://fonts.googleapis.com"/>'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin/>'
    '<link rel="preload" as="style" href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;1,700&family=DM+Sans:wght@400;500;700&display=swap" onload="this.onload=null;this.rel=\'stylesheet\'"/>'
    '<noscript><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;1,700&family=DM+Sans:wght@400;500;700&display=swap"/></noscript>'
)

# ── Page Builders ─────────────────────────────────────────────────────────────

def build_table(entries, loc, mi):
    """Build ranking table for a given month."""
    is_fr = loc['meta']['html_lang'] == 'fr'
    is_es = loc['meta']['html_lang'] == 'es'
    gen = loc['gen']
    pil = loc['pilier']
    month_url = loc['month_url']
    rows = ''
    for i, entry in enumerate(entries, 1):
        slug = entry['slug_fr'] if is_fr else (entry.get('slug_es') or entry['slug_en'] if is_es else entry['slug_en'])
        nom = entry['nom_bare'] if is_fr else (entry.get('nom_es') or entry['nom_bare'] if is_es else entry['nom_en'])
        href = gen['monthly_href_tpl'].format(slug=slug, month_slug=month_url[mi])
        flag_img = f'<img src="{gen["asset_prefix"]}flags/{entry["flag"]}.png" width="16" height="12" alt="" style="vertical-align:middle;margin-right:6px;border-radius:1px">'
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
    h = pil['th']
    return (
        f'<table class="rt" aria-label="{pil["ranking_label"]}">'
        f'<thead><tr>{"".join(f"<th>{c}</th>" for c in h)}</tr></thead>'
        f'<tbody>{rows}</tbody></table>'
    )

def build_month_nav(mi, loc):
    """Build month navigation bar."""
    months = loc['months']
    month_url = loc['month_url']
    pil = loc['pilier']
    prefix = pil['pillar_prefix']
    links = ''
    for i in range(12):
        active = ' class="active"' if i == mi else ''
        links += f'<a href="{prefix}{month_url[i]}.html"{active}>{months[i][:3]}</a>'
    return f'<nav class="month-nav" aria-label="{pil["months_label"]}">{links}</nav>'

def build_related(mi, loc):
    """Build related ranking cards."""
    months = loc['months']
    month_url = loc['month_url']
    pil = loc['pilier']
    prefix = pil['pillar_prefix']
    cards = []
    # Adjacent months
    for offset in [-1, 1]:
        adj = (mi + offset) % 12
        month_name = months[adj]
        label = pil['where_to_go_tpl'].format(month=month_name.lower() if loc['meta'].get('lowercase_months') else month_name)
        cards.append(f'<a href="{prefix}{month_url[adj]}.html" class="related-card"><strong>{label}</strong><span>Top {TOP_N} {pil["top_n_label"]}</span></a>')
    # General ranking
    cards.append(f'<a href="{pil["world_ranking_url"]}" class="related-card"><strong>{pil["world_ranking_label"]}</strong><span>{pil["world_ranking_sub"]}</span></a>')
    return f'<div class="section"><div class="eyebrow">{pil["also_explore"]}</div><h2 class="sec-title">{pil["other_rankings"]}</h2><div class="related-pages">{"".join(cards)}</div></div>'


def generate_page(mi, lang, dests, climate):
    """Generate one pillar page for month mi (0-indexed) in given language."""
    loc = load_locale(lang)
    gen = loc['gen']
    pil = loc['pilier']
    is_fr = (lang == 'fr')
    months = loc['months']
    month_url = loc['month_url']
    month_name = months[mi]
    month_slug = month_url[mi]
    season_map = {int(k): v for k, v in loc['seasons_map'].items()}
    season = season_map.get(mi, '')

    entries = get_rankings(climate, dests, mi + 1)  # climate.csv is 1-indexed
    if not entries:
        print(f"  ⚠️  No data for month {mi}")
        return

    top = entries[0]
    avg_score = sum(x['score'] for x in entries[:10]) / 10
    avg_temp = sum(x['tmax'] for x in entries[:10]) / 10

    # File paths
    is_es = (lang == 'es')
    if is_fr:
        cross_loc = load_locale('en')
    elif is_es:
        cross_loc = load_locale('fr')  # ES first alt = FR
    else:
        cross_loc = load_locale('fr')
    cross_month_url = cross_loc['month_url']
    cross_prefix = cross_loc['pilier']['pillar_prefix']

    filename = f'{pil["pillar_prefix"]}{month_slug}.html'
    alt_file = f'{cross_prefix}{cross_month_url[mi]}.html'
    # alt_file2 = file in the third language
    loc_fr = load_locale('fr')
    loc_en = load_locale('en')
    loc_es = load_locale('es')
    es_prefix = loc_es['pilier']['pillar_prefix']
    es_month_url = loc_es['month_url']
    alt_file2_es = f'{es_prefix}{es_month_url[mi]}.html'
    alt_file2_en = f'{loc_en["pilier"]["pillar_prefix"]}{loc_en["month_url"][mi]}.html'
    alt_file2_fr = f'{loc_fr["pilier"]["pillar_prefix"]}{loc_fr["month_url"][mi]}.html'
    if is_fr:
        filepath = ROOT / filename
        canonical = f'https://bestdateweather.com/{filename}'
        hreflang_fr = canonical
        hreflang_en = f'https://bestdateweather.com/en/{alt_file}'
        alt_file2 = alt_file2_es  # FR→EN already in alt_file, FR→ES in alt_file2
    elif is_es:
        filepath = ROOT / 'es' / filename
        canonical = f'https://bestdateweather.com/es/{filename}'
        hreflang_fr = f'https://bestdateweather.com/ou-partir-en-{loc_fr["month_url"][mi]}.html'
        hreflang_en = f'https://bestdateweather.com/en/{alt_file}'
        alt_file2 = alt_file2_en  # ES→FR already in alt_file, ES→EN in alt_file2
    else:
        filepath = ROOT / 'en' / filename
        canonical = f'https://bestdateweather.com/en/{filename}'
        hreflang_fr = f'https://bestdateweather.com/{alt_file}'
        hreflang_en = canonical
        alt_file2 = alt_file2_es  # EN→FR already in alt_file, EN→ES in alt_file2

    # Month name for display (lowercase in FR)
    mn_lc = month_name.lower() if loc['meta'].get('lowercase_months') else month_name

    # Content — keep is_fr for complex text blocks
    nom_es = lambda e: e.get('nom_es') or e.get('nom_bare', '')
    if is_es:
        title = f"Adónde ir en {month_name} {YEAR} — Top {TOP_N} destinos por clima"
        desc = (f"¿Adónde ir en {month_name} {YEAR}? Top {TOP_N} destinos por clima. "
                f"N°1: {nom_es(top)} ({top['score']:.1f}/10, {top['tmax']:.0f}°C). "
                f"Basado en 10 años de datos Open-Meteo.")
        h1 = f"¿Adónde ir en <em>{month_name}</em>?"
        hero_sub = (f"Los {TOP_N} mejores destinos por clima en {month_name} {YEAR}, "
                    f"clasificados por puntuación climática basada en 10 años de datos.")
        sec_eyebrow = f"Ranking {month_name} {YEAR}"
        sec_title = f"Top {TOP_N} destinos en {month_name}"
        sec_intro = (f"Puntuación media top 10: <strong>{avg_score:.1f}/10</strong> · "
                     f"Temperatura media: <strong>{avg_temp:.0f}°C</strong>")
        cta_text = f"🎯 Elige una fecha exacta para tu viaje en {month_name}"
    elif is_fr:
        title = f"Où partir en {mn_lc} {YEAR} ? Top {TOP_N} destinations météo"
        desc = (f"Où partir en {mn_lc} {YEAR} ? Classement des {TOP_N} meilleures destinations "
                f"par score météo. N°1 : {top['nom_bare']} ({top['score']:.1f}/10, {top['tmax']:.0f}°C). "
                f"Données 10 ans Open-Meteo.")
        h1 = f"Où partir en <em>{mn_lc}</em> ?"
        hero_sub = (f"Les {TOP_N} meilleures destinations météo pour {mn_lc} {YEAR}, "
                    f"classées par score climatique sur 10 ans de données.")
        sec_eyebrow = f"Classement {month_name} {YEAR}"
        sec_title = f"Top {TOP_N} destinations en {mn_lc}"
        sec_intro = (f"Score moyen du top 10 : <strong>{avg_score:.1f}/10</strong> · "
                     f"Température moyenne : <strong>{avg_temp:.0f}°C</strong>")
        cta_text = f"🎯 Choisir une date précise pour votre voyage en {mn_lc}"
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

    cta_href = gen['home_url']

    table = build_table(entries, loc, mi)
    month_nav = build_month_nav(mi, loc)
    related = build_related(mi, loc)

    # Schema.org
    breadcrumb_name = pil['where_to_go_tpl'].format(month=mn_lc)
    breadcrumb = json.dumps({
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1,
             "name": loc['labels']['breadcrumb_home'],
             "item": loc['meta']['schema_home_url']},
            {"@type": "ListItem", "position": 2,
             "name": breadcrumb_name, "item": canonical}
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
                "name": entry['nom_bare'] if is_fr else (entry.get('nom_es') or entry['nom_bare'] if is_es else entry['nom_en']),
                "url": loc['meta']['canonical_prefix'] + gen['monthly_href_tpl'].format(
                    slug=entry['slug_fr'] if is_fr else (entry.get('slug_es') or entry['slug_en'] if is_es else entry['slug_en']),
                    month_slug=month_url[mi])
            }
            for i, entry in enumerate(entries)
        ]
    }, ensure_ascii=False)

    # FAQ — keep is_fr for complex content
    faq_items = []
    if is_fr:
        faq_items.append({"@type": "Question",
            "name": f"Quelle est la meilleure destination en {mn_lc} ?",
            "acceptedAnswer": {"@type": "Answer",
                "text": f"{top['nom_bare']} est la destination n°1 en {mn_lc} avec un score de {top['score']:.1f}/10 et {top['tmax']:.0f}°C."}})
        faq_items.append({"@type": "Question",
            "name": f"Où partir au soleil en {mn_lc} ?",
            "acceptedAnswer": {"@type": "Answer",
                "text": f"Les destinations les plus ensoleillées en {mn_lc} sont {entries[0]['nom_bare']}, {entries[1]['nom_bare']} et {entries[2]['nom_bare']}, avec des scores de {entries[0]['score']:.1f} à {entries[2]['score']:.1f}/10."}})
    elif is_es:
        faq_items.append({"@type": "Question",
            "name": f"¿Cuál es el mejor destino en {month_name}?",
            "acceptedAnswer": {"@type": "Answer",
                "text": f"{nom_es(top)} es el destino n°1 en {month_name} con una puntuación de {top['score']:.1f}/10 y {top['tmax']:.0f}°C."}})
        faq_items.append({"@type": "Question",
            "name": f"¿Adónde ir con buen tiempo en {month_name}?",
            "acceptedAnswer": {"@type": "Answer",
                "text": f"Los destinos con mejor clima en {month_name} son {nom_es(entries[0])}, {nom_es(entries[1])} y {nom_es(entries[2])}, con puntuaciones de {entries[0]['score']:.1f} a {entries[2]['score']:.1f}/10."}})
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
    alt_link = f'{gen["alt_link_prefix"]}{alt_file}'
    alt_link2 = f'{gen["alt_link2_prefix"]}{alt_file2}' if gen.get('alt_link2_prefix') and alt_file2 else ''
    alt_link2_html = f' · <a href="{alt_link2}"><img src="{gen["alt_flag_path2"]}" width="20" height="15" alt="" style="vertical-align:middle;border-radius:2px"> {gen["alt_lang_label2"]}</a>' if alt_link2 else ''
    footer = f"""<footer>
<p style="font-weight:700;margin-bottom:8px">bestdateweather.com</p>
<p><a href="https://open-meteo.com/" rel="noopener">{gen["data_credit"]}</a> · ECMWF, DWD, NOAA · CC BY 4.0</p>
<p style="margin-top:8px"><a href="{gen["home_url"]}">{gen["home_label"]}</a> · <a href="{alt_link}"><img src="{gen["alt_flag_path"]}" width="20" height="15" alt="" style="vertical-align:middle;border-radius:2px"> {gen["alt_lang_label"]}</a>{alt_link2_html}</p>
<p style="margin-top:8px;font-size:11px;opacity:.6"><a href="{gen["legal_url"]}" style="color:rgba(255,255,255,.7)">{gen["legal_label"]}</a></p>
</footer>"""

    flag_prefix = gen['asset_prefix']

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
<link rel="alternate" hreflang="es" href="https://bestdateweather.com/es/{pil['pillar_prefix']}{month_slug}.html"/>
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
<nav style="display:flex;align-items:center;justify-content:space-between;padding:16px 20px;max-width:900px;margin:0 auto">
 <a href="{gen["home_url"]}" style="text-decoration:none;font-family:'Playfair Display',serif;font-size:20px;font-weight:700;color:#1a2332">Best<em style="color:#d4a853;font-style:italic">Date</em>Weather</a>
 <div style="display:flex;align-items:center;gap:12px">
  <button class="nav-share" onclick="shareThis()" aria-label="{gen["share_label"]}" style="background:none;border:1.5px solid #e8e0d0;border-radius:8px;padding:8px 10px;cursor:pointer;align-items:center;color:#5a6c7d"><svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><path d="M8.59 13.51l6.83 3.98M15.41 6.51l-6.82 3.98"/></svg></button>
  <a href="{gen["home_url"]}" style="display:inline-block;background:#d4a853;color:white;font-size:12px;font-weight:700;padding:10px 20px;border-radius:8px;text-decoration:none">{gen["try_app_label"]}</a>
 </div>
</nav>
<header class="hero">
<div class="hero-eyebrow">{pil["hero_eyebrow_prefix"]}{YEAR}</div>
<h1 class="hero-title">{h1}</h1>
<p class="hero-sub">{hero_sub}</p>
<div class="hero-stats">
<div class="hstat"><span class="hstat-val">{top['score']:.1f}</span><span class="hstat-lbl">{pil["score_n1"]}</span></div>
<div class="hstat"><span class="hstat-val">{TOP_N}</span><span class="hstat-lbl">Destinations</span></div>
<div class="hstat"><span class="hstat-val">{avg_temp:.0f}°C</span><span class="hstat-lbl">{pil["top10_avg"]}</span></div>
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
<script src="{gen['asset_prefix']}js/share.js"></script>
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
        updated = 0
        for page in pages:
            entry = f"""  <url>
    <loc>{page['canonical']}</loc>
    <lastmod>{TODAY}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
    <xhtml:link rel="alternate" hreflang="fr" href="{page['hreflang_fr']}"/>
    <xhtml:link rel="alternate" hreflang="en" href="{page['hreflang_en']}"/>
    <xhtml:link rel="alternate" hreflang="x-default" href="{page['hreflang_en']}"/>
  </url>"""
            if page['canonical'] in content:
                # Replace existing entry if it lacks hreflang
                import re
                pattern = (
                    r'<url>\s*'
                    + re.escape(f"<loc>{page['canonical']}</loc>") + r'\s*'
                    + r'<lastmod>[^<]*</lastmod>\s*'
                    + r'<changefreq>[^<]*</changefreq>\s*'
                    + r'<priority>[^<]*</priority>\s*'
                    + r'</url>'
                )
                if re.search(pattern, content):
                    content = re.sub(pattern, entry, content)
                    updated += 1
                continue
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

    # ES
    es_pages = []
    for mi in range(12):
        result = generate_page(mi, 'es', dests, climate)
        if result:
            filename, canonical, hreflang_fr, hreflang_en = result
            es_pages.append({'canonical': canonical})
            print(f"  ✅ es/{filename}")

    print(f"\n📄 {len(fr_pages)} FR + {len(en_pages)} EN + {len(es_pages)} ES pillar pages generated")

    update_sitemaps(fr_pages, en_pages)
    print("\n✅ Done")
