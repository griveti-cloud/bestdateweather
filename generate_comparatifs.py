#!/usr/bin/env python3
"""
Generate comparison pages (X vs Y) for high-search-volume destination pairs.
  FR: nice-ou-barcelone-climat.html
  EN: en/nice-vs-barcelona-weather.html

Each page shows side-by-side monthly climate, score comparison, and verdict.
Usage: python3 generate_comparatifs.py
"""

import csv, html as html_mod, json, sys, os
from pathlib import Path
from datetime import date

sys.path.insert(0, str(Path(__file__).parent))
from lib.page_config import load_locale
from lib.common import footer_ranking_html

ROOT = Path(__file__).parent
TODAY = date.today().isoformat()
YEAR = date.today().year

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
    # Americas / US-specific
    ('miami', 'cancun'),
    ('new-york', 'miami'),
    ('new-york', 'los-angeles'),
    ('los-angeles', 'san-francisco'),
    ('hawaii', 'cancun'),
    # ES-specific
    ('barcelone', 'madrid'),
    ('tenerife', 'lanzarote'),
    ('valence', 'barcelone'),
    ('costa-rica', 'panama'),
    # Asia/Pacific
    ('tokyo', 'seoul'),
    ('sydney', 'melbourne'),
    # Europe
    ('amsterdam', 'bruxelles'),
    ('prague', 'vienne'),
    # Paires supplémentaires
    ('maldives', 'bali'),
    ('lisbonne', 'madrid'),
    ('rome', 'florence'),
    ('paris', 'amsterdam'),
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

def c_to_f(c):
    return round(c * 9 / 5 + 32)

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
.ct-mhead{display:none}
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
@media(max-width:640px){.vs-grid{grid-template-columns:1fr;gap:12px}.vs-sep{padding:8px 0}.ct-dhead{display:none}.ct-mhead{display:table-row}.ct td:nth-child(3),.ct td:nth-child(5){display:none}}
"""

FONTS = (
    '<link rel="preconnect" href="https://fonts.googleapis.com"/>'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin/>'
    '<link rel="preload" as="style" href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;1,700&family=DM+Sans:wght@400;500;700&display=swap" onload="this.onload=null;this.rel=\'stylesheet\'"/>'
    '<noscript><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;1,700&family=DM+Sans:wght@400;500;700&display=swap"/></noscript>'
)

# ── Page Builders ─────────────────────────────────────────────────────────────

def build_comparison_table(ca, cb, nom_a, nom_b, loc, use_f=False):
    """Build month-by-month comparison table."""
    months = loc['months']
    comp = loc['comp']
    unit = '°F' if use_f else '°C'
    headers = (
        f'<tr class="ct-dhead"><th>{comp["th_month"]}</th>'
        f'<th colspan="2">{e(nom_a)}</th>'
        f'<th colspan="2">{e(nom_b)}</th>'
        f'<th>{comp["th_better"]}</th></tr>'
    )
    subheaders = (
        f'<tr class="ct-dhead" style="background:#f8f6f0"><td></td>'
        f'<td style="font-size:10px;text-align:center;color:var(--slate2)">Score</td>'
        f'<td style="font-size:10px;text-align:center;color:var(--slate2)">Temp</td>'
        f'<td style="font-size:10px;text-align:center;color:var(--slate2)">Score</td>'
        f'<td style="font-size:10px;text-align:center;color:var(--slate2)">Temp</td>'
        f'<td></td></tr>'
    )
    # Header simplifié pour mobile (sans colspan)
    mobile_header = (
        f'<tr class="ct-mhead"><th>{comp["th_month"]}</th>'
        f'<th>{e(nom_a)}</th>'
        f'<th>{e(nom_b)}</th>'
        f'<th>{comp["th_better"]}</th></tr>'
    )
    rows = ''
    for mi in range(1, 13):
        ma = ca.get(mi, {})
        mb = cb.get(mi, {})
        sa = ma.get('score', 0)
        sb = mb.get('score', 0)
        ta = ma.get('tmax', 0)
        tb = mb.get('tmax', 0)
        if use_f:
            ta = c_to_f(ta)
            tb = c_to_f(tb)
        winner_name = nom_a if sa > sb else (nom_b if sb > sa else '=')
        winner_flag = '🏆' if abs(sa - sb) >= 1 else ('↑' if sa != sb else '—')
        a_cls = ' class="win"' if sa > sb else ''
        b_cls = ' class="win"' if sb > sa else ''
        rows += (
            f'<tr>'
            f'<td>{months[mi-1][:3]}</td>'
            f'<td{a_cls} style="color:{score_color(sa)}">{sa:.1f}</td>'
            f'<td>{ta:.0f}{unit}</td>'
            f'<td{b_cls} style="color:{score_color(sb)}">{sb:.1f}</td>'
            f'<td>{tb:.0f}{unit}</td>'
            f'<td style="font-size:12px">{winner_flag} {e(winner_name)}</td>'
            f'</tr>'
        )
    return f'<table class="ct"><thead>{headers}{subheaders}{mobile_header}</thead><tbody>{rows}</tbody></table>'


def compute_verdicts(ca, cb, nom_a, nom_b, loc, use_f=False):
    """Generate verdicts per season and overall."""
    is_fr = loc['meta']['html_lang'] == 'fr'
    is_es = loc['meta']['html_lang'] == 'es'
    is_de = loc['meta']['html_lang'] == 'de'
    wins_a = sum(1 for mi in range(1, 13) if ca.get(mi, {}).get('score', 0) > cb.get(mi, {}).get('score', 0))
    wins_b = sum(1 for mi in range(1, 13) if cb.get(mi, {}).get('score', 0) > ca.get(mi, {}).get('score', 0))
    ties = 12 - wins_a - wins_b

    avg_a = sum(ca.get(mi, {}).get('score', 0) for mi in range(1, 13)) / 12
    avg_b = sum(cb.get(mi, {}).get('score', 0) for mi in range(1, 13)) / 12

    # Best months per destination
    best_a = max(range(1, 13), key=lambda mi: ca.get(mi, {}).get('score', 0))
    best_b = max(range(1, 13), key=lambda mi: cb.get(mi, {}).get('score', 0))

    # Season analysis — use locale season_order for names
    season_map = {int(k): v for k, v in loc['seasons_map'].items()}
    seasons = {}
    for name in loc['season_order']:
        months_in = [mi for mi in range(1, 13) if season_map.get(mi - 1, '') == name
                     or season_map.get(mi % 12, '') == name]
        if not months_in:
            continue
        seasons[name.lower()] = months_in

    # Fallback if season_order mapping doesn't give month lists
    if not seasons:
        so = loc['season_order']
        seasons = {so[3].lower(): [12, 1, 2], so[0].lower(): [3, 4, 5],
                   so[1].lower(): [6, 7, 8], so[2].lower(): [9, 10, 11]}

    unit = '°F' if use_f else '°C'
    season_verdicts = []
    for season_name, month_list in seasons.items():
        sa_avg = sum(ca.get(mi, {}).get('score', 0) for mi in month_list) / len(month_list)
        sb_avg = sum(cb.get(mi, {}).get('score', 0) for mi in month_list) / len(month_list)
        ta_avg = sum(ca.get(mi, {}).get('tmax', 0) for mi in month_list) / len(month_list)
        tb_avg = sum(cb.get(mi, {}).get('tmax', 0) for mi in month_list) / len(month_list)
        if use_f:
            ta_avg = c_to_f(ta_avg)
            tb_avg = c_to_f(tb_avg)
        winner = nom_a if sa_avg > sb_avg else nom_b
        if is_fr:
            detail = f"En {season_name}, <strong>{winner}</strong> l'emporte ({sa_avg:.1f} vs {sb_avg:.1f}). Températures : {nom_a} {ta_avg:.0f}{unit}, {nom_b} {tb_avg:.0f}{unit}."
        elif is_es:
            detail = f"En {season_name}, <strong>{winner}</strong> gana ({sa_avg:.1f} vs {sb_avg:.1f}). Temperaturas: {nom_a} {ta_avg:.0f}{unit}, {nom_b} {tb_avg:.0f}{unit}."
        elif is_de:
            detail = f"Im {season_name}, <strong>{winner}</strong> gewinnt ({sa_avg:.1f} vs {sb_avg:.1f}). Temperaturen: {nom_a} {ta_avg:.0f}{unit}, {nom_b} {tb_avg:.0f}{unit}."
        else:
            detail = f"In {season_name}, <strong>{winner}</strong> wins ({sa_avg:.1f} vs {sb_avg:.1f}). Temperatures: {nom_a} {ta_avg:.0f}{unit}, {nom_b} {tb_avg:.0f}{unit}."
        season_verdicts.append(detail)

    months = loc['months']
    if is_fr:
        overall = (f"<strong>{nom_a}</strong> gagne {wins_a} mois sur 12, "
                   f"<strong>{nom_b}</strong> en gagne {wins_b}" +
                   (f" ({ties} ex-æquo)." if ties else ".") +
                   f" Score annuel moyen : {nom_a} {avg_a:.1f}/10, {nom_b} {avg_b:.1f}/10. "
                   f"Meilleur mois : {nom_a} en {months[best_a-1].lower()}, {nom_b} en {months[best_b-1].lower()}.")
    elif is_es:
        overall = (f"<strong>{nom_a}</strong> gana {wins_a} meses de 12, "
                   f"<strong>{nom_b}</strong> gana {wins_b}" +
                   (f" ({ties} empates)." if ties else ".") +
                   f" Puntuación anual media: {nom_a} {avg_a:.1f}/10, {nom_b} {avg_b:.1f}/10. "
                   f"Mejor mes: {nom_a} en {months[best_a-1]}, {nom_b} en {months[best_b-1]}.")
    elif is_de:
        overall = (f"<strong>{nom_a}</strong> gewinnt {wins_a} Monate von 12, "
                   f"<strong>{nom_b}</strong> gewinnt {wins_b}" +
                   (f" ({ties} Unentschieden)." if ties else ".") +
                   f" Jahres-Ø-Score: {nom_a} {avg_a:.1f}/10, {nom_b} {avg_b:.1f}/10. "
                   f"Bester Monat: {nom_a} im {months[best_a-1]}, {nom_b} im {months[best_b-1]}.")
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

    for lang in ('fr', 'en', 'en-us', 'es', 'de'):
        loc = load_locale(lang)
        gen = loc['gen']
        comp = loc['comp']
        is_fr = (lang == 'fr')
        is_us = (lang == 'en-us')
        is_es = (lang == 'es')
        is_de = (lang == 'de')
        use_f = is_us
        if is_fr:
            nom_a = da['nom_bare']
            nom_b = db['nom_bare']
        elif is_es:
            nom_a = da.get('nom_es', da['nom_bare'])
            nom_b = db.get('nom_es', db['nom_bare'])
        elif is_de:
            nom_a = da.get('nom_de', da.get('nom_en', da['nom_bare']))
            nom_b = db.get('nom_de', db.get('nom_en', db['nom_bare']))
        else:
            nom_a = da.get('nom_en', da['nom_bare'])
            nom_b = db.get('nom_en', db['nom_bare'])
        slug_en_a = da.get('slug_en', slug_a)
        slug_en_b = db.get('slug_en', slug_b)
        slug_es_a = da.get('slug_es', slug_en_a)
        slug_es_b = db.get('slug_es', slug_en_b)
        slug_de_a = da.get('slug_de', slug_en_a)
        slug_de_b = db.get('slug_de', slug_en_b)
        flag_a, flag_b = da.get('flag', ''), db.get('flag', '')

        filename = comp['file_tpl'].format(
            a=slug_a if is_fr else (slug_es_a if is_es else (slug_de_a if is_de else slug_en_a)),
            b=slug_b if is_fr else (slug_es_b if is_es else (slug_de_b if is_de else slug_en_b))
        )
        alt_fr_filename = load_locale('fr')['comp']['file_tpl'].format(a=slug_a, b=slug_b)
        alt_en_filename = load_locale('en')['comp']['file_tpl'].format(a=slug_en_a, b=slug_en_b)
        alt_us_filename = load_locale('en-us')['comp']['file_tpl'].format(a=slug_en_a, b=slug_en_b)
        alt_es_filename = load_locale('es')['comp']['file_tpl'].format(a=slug_es_a, b=slug_es_b)
        alt_de_filename = load_locale('de')['comp']['file_tpl'].format(a=slug_de_a, b=slug_de_b)
        hreflang_fr = f"https://bestdateweather.com/{alt_fr_filename}"
        hreflang_en = f"https://bestdateweather.com/en/{alt_en_filename}"
        hreflang_us = f"https://bestdateweather.com/us/{alt_us_filename}"
        hreflang_es = f"https://bestdateweather.com/es/{alt_es_filename}"
        hreflang_de = f"https://bestdateweather.com/de/{alt_de_filename}"
        if is_fr:
            filepath = ROOT / filename
            canonical = hreflang_fr
        elif is_es:
            filepath = ROOT / 'es' / filename
            canonical = hreflang_es
        elif is_us:
            filepath = ROOT / 'us' / filename
            canonical = hreflang_us
        elif is_de:
            filepath = ROOT / 'de' / filename
            canonical = hreflang_de
        else:  # en
            filepath = ROOT / 'en' / filename
            canonical = hreflang_en

        # Scores
        avg_a_score = sum(ca.get(mi, {}).get('score', 0) for mi in range(1, 13)) / 12
        avg_b_score = sum(cb.get(mi, {}).get('score', 0) for mi in range(1, 13)) / 12
        best_mi_a = max(range(1, 13), key=lambda mi: ca.get(mi, {}).get('score', 0))
        best_mi_b = max(range(1, 13), key=lambda mi: cb.get(mi, {}).get('score', 0))

        months = loc['months']
        flag_prefix = gen['asset_prefix']
        tmax_a = ca[best_mi_a]['tmax']
        tmax_b = cb[best_mi_b]['tmax']
        if use_f:
            tmax_a = c_to_f(tmax_a)
            tmax_b = c_to_f(cb[best_mi_b]['tmax'])
        temp_unit = '°F' if use_f else '°C'

        # Content
        if is_fr:
            _winner_fr = nom_a if avg_a_score >= avg_b_score else nom_b
            _winner_score_fr = max(avg_a_score, avg_b_score)
            title = f"{nom_a} ou {nom_b} ? Lequel a le meilleur climat ? [{YEAR}]"
            desc = (f"{nom_a} ou {nom_b} : comparaison météo mois par mois sur 10 ans. "
                    f"Verdict : {_winner_fr} ({_winner_score_fr:.1f}/10). Données ERA5.")
            h1 = f"{nom_a} <em>ou</em> {nom_b} ?"
            hero_sub = f"Comparaison climatique complète — 12 mois, 10 ans de données, score objectif"
            href_a = gen['annual_href_tpl'].format(slug=slug_a)
            href_b = gen['annual_href_tpl'].format(slug=slug_b)
        elif is_es:
            _winner_es = nom_a if avg_a_score >= avg_b_score else nom_b
            _winner_score_es = max(avg_a_score, avg_b_score)
            title = f"{nom_a} vs {nom_b}: ¿Cuál Tiene Mejor Clima? [{YEAR}]"
            desc = (f"{nom_a} vs {nom_b}: comparación del tiempo mes a mes en 10 años. "
                    f"Veredicto: {_winner_es} ({_winner_score_es:.1f}/10). Datos ERA5.")
            h1 = f"{nom_a} <em>vs</em> {nom_b}"
            hero_sub = f"Comparación climática completa — 12 meses, 10 años de datos, puntuación objetiva"
            href_a = gen['annual_href_tpl'].format(slug=slug_es_a)
            href_b = gen['annual_href_tpl'].format(slug=slug_es_b)
        elif is_de:
            _winner_de = nom_a if avg_a_score >= avg_b_score else nom_b
            _winner_score_de = max(avg_a_score, avg_b_score)
            title = f"{nom_a} vs {nom_b}: Wer Hat das Bessere Wetter? [{YEAR}]"
            desc = (f"{nom_a} vs {nom_b}: Klimavergleich Monat für Monat über 10 Jahre. "
                    f"Ergebnis: {_winner_de} ({_winner_score_de:.1f}/10). ERA5-Daten.")
            h1 = f"{nom_a} <em>vs</em> {nom_b}"
            hero_sub = f"Vollständiger Klimavergleich — 12 Monate, 10 Jahre Daten, objektiver Score"
            href_a = gen['annual_href_tpl'].format(slug=slug_de_a)
            href_b = gen['annual_href_tpl'].format(slug=slug_de_b)
        else:
            _winner_en = nom_a if avg_a_score >= avg_b_score else nom_b
            _winner_score_en = max(avg_a_score, avg_b_score)
            title = f"{nom_a} vs {nom_b}: Which Has Better Weather? [{YEAR}]"
            desc = (f"{nom_a} vs {nom_b}: month-by-month weather comparison over 10 years. "
                    f"Winner: {_winner_en} ({_winner_score_en:.1f}/10). Based on ERA5 data.")
            h1 = f"{nom_a} <em>vs</em> {nom_b}"
            hero_sub = f"Complete climate comparison — 12 months, 10 years of data, objective scores"
            href_a = gen['annual_href_tpl'].format(slug=slug_en_a)
            href_b = gen['annual_href_tpl'].format(slug=slug_en_b)

        # VS cards
        vs_cards = f"""<div class="vs-grid">
<div class="vs-card">
<img src="{flag_prefix}flags/{flag_a}.png" width="24" height="18" alt="" style="border-radius:2px;margin-bottom:8px">
<h3><a href="{href_a}" style="color:var(--navy);text-decoration:none">{e(nom_a)}</a></h3>
<div class="big-score" style="color:{score_color(avg_a_score)}">{avg_a_score:.1f}<span style="font-size:16px;color:var(--slate2)">/10</span></div>
<div class="vs-stat">{comp["best_month_label"]} : <strong>{months[best_mi_a-1]}</strong> ({ca[best_mi_a]['score']:.1f})</div>
<div class="vs-stat">{comp["max_temp_label"]} : <strong>{tmax_a:.0f}{temp_unit}</strong></div>
</div>
<div class="vs-sep">VS</div>
<div class="vs-card">
<img src="{flag_prefix}flags/{flag_b}.png" width="24" height="18" alt="" style="border-radius:2px;margin-bottom:8px">
<h3><a href="{href_b}" style="color:var(--navy);text-decoration:none">{e(nom_b)}</a></h3>
<div class="big-score" style="color:{score_color(avg_b_score)}">{avg_b_score:.1f}<span style="font-size:16px;color:var(--slate2)">/10</span></div>
<div class="vs-stat">{comp["best_month_label"]} : <strong>{months[best_mi_b-1]}</strong> ({cb[best_mi_b]['score']:.1f})</div>
<div class="vs-stat">{comp["max_temp_label"]} : <strong>{tmax_b:.0f}{temp_unit}</strong></div>
</div>
</div>"""

        table = build_comparison_table(ca, cb, nom_a, nom_b, loc, use_f=use_f)
        overall, season_verdicts, _, _, _, _ = compute_verdicts(ca, cb, nom_a, nom_b, loc, use_f=use_f)

        verdict_html = f"""<div class="verdict">
<h3>{comp["verdict_title"]}</h3>
<p>{overall}</p>
</div>
<div class="verdict">
<h3>{comp["season_title"]}</h3>
{"".join(f'<p>{v}</p>' for v in season_verdicts)}
</div>"""

        # Schemas
        breadcrumb = json.dumps({
            "@context": "https://schema.org", "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1,
                 "name": loc['labels']['breadcrumb_home'],
                 "item": loc['meta']['schema_home_url']},
                {"@type": "ListItem", "position": 2,
                 "name": f"{nom_a} {comp['sep']} {nom_b}", "item": canonical}
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
        elif is_es:
            faq_items.append({"@type": "Question",
                "name": f"{nom_a} o {nom_b}: ¿cuál tiene mejor clima?",
                "acceptedAnswer": {"@type": "Answer", "text": overall.replace('<strong>', '').replace('</strong>', '')}})
            faq_items.append({"@type": "Question",
                "name": f"¿Cuándo visitar {nom_a} en lugar de {nom_b}?",
                "acceptedAnswer": {"@type": "Answer",
                    "text": f"{nom_a} es mejor en {months[best_mi_a-1]} ({ca[best_mi_a]['score']:.1f}/10). {nom_b} es mejor en {months[best_mi_b-1]} ({cb[best_mi_b]['score']:.1f}/10)."}})
        elif is_de:
            faq_items.append({"@type": "Question",
                "name": f"{nom_a} oder {nom_b}: Wo ist das Wetter besser?",
                "acceptedAnswer": {"@type": "Answer", "text": overall.replace('<strong>', '').replace('</strong>', '')}})
            faq_items.append({"@type": "Question",
                "name": f"Wann {nom_a} statt {nom_b} besuchen?",
                "acceptedAnswer": {"@type": "Answer",
                    "text": f"{nom_a} ist am besten im {months[best_mi_a-1]} ({ca[best_mi_a]['score']:.1f}/10). {nom_b} ist am besten im {months[best_mi_b-1]} ({cb[best_mi_b]['score']:.1f}/10)."}})
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

        # hreflang block (5 languages)
        hreflang_block = (
            f'<link rel="alternate" hreflang="fr" href="{hreflang_fr}"/>\n'
            f'<link rel="alternate" hreflang="en" href="{hreflang_en}"/>\n'
            f'<link rel="alternate" hreflang="en-US" href="{hreflang_us}"/>\n'
            f'<link rel="alternate" hreflang="es" href="{hreflang_es}"/>\n'
            f'<link rel="alternate" hreflang="de" href="{hreflang_de}"/>\n'
            f'<link rel="alternate" hreflang="x-default" href="{hreflang_en}"/>'
        )

        # Related
        related_cards = []
        for slug, nom in [(slug_a, nom_a), (slug_b, nom_b)]:
            if is_fr:
                href = gen['annual_href_tpl'].format(slug=slug)
            elif is_es:
                sle = dests[slug].get('slug_es', slug)
                href = gen['annual_href_tpl'].format(slug=sle)
            else:
                sle = dests[slug].get('slug_en', slug)
                href = gen['annual_href_tpl'].format(slug=sle)
            label = gen['best_period_tpl'].format(nom=nom)
            related_cards.append(f'<a href="{href}" class="related-card"><strong>{e(label)}</strong><span>{gen["guide_label"]}</span></a>')

        related_html = (f'<div class="section"><div class="eyebrow">{gen["explore_label"]}</div>'
                        f'<h2 class="sec-title">{gen["guides_title"]}</h2>'
                        f'<div class="related-pages">{"".join(related_cards)}</div></div>')

        # CTA
        cta = f'<div class="cta-box"><a href="{gen["home_url"]}">{gen["cta_choose"]}</a></div>'

        # Footer — cross-lang links
        _es_fn = load_locale('es')['comp']['file_tpl'].format(a=slug_es_a, b=slug_es_b)
        _en_fn = load_locale('en')['comp']['file_tpl'].format(a=slug_en_a, b=slug_en_b)
        _us_fn = load_locale('en-us')['comp']['file_tpl'].format(a=slug_en_a, b=slug_en_b)
        _fr_fn = load_locale('fr')['comp']['file_tpl'].format(a=slug_a, b=slug_b)
        _de_fn = load_locale('de')['comp']['file_tpl'].format(a=slug_de_a, b=slug_de_b)
        if is_fr:
            _alt_links = [
                {'url': f'en/{_en_fn}', 'flag': 'flags/gb.png', 'label': 'English'},
                {'url': f'us/{_us_fn}', 'flag': 'flags/us.png', 'label': 'English (US)'},
                {'url': f'es/{_es_fn}', 'flag': 'flags/es.png', 'label': 'Español'},
                {'url': f'de/{_de_fn}', 'flag': 'flags/de.png', 'label': 'Deutsch'},
            ]
        elif is_es:
            _alt_links = [
                {'url': f'../en/{_en_fn}', 'flag': '../flags/gb.png', 'label': 'English'},
                {'url': f'../us/{_us_fn}', 'flag': '../flags/us.png', 'label': 'English (US)'},
                {'url': f'../{_fr_fn}', 'flag': '../flags/fr.png', 'label': 'Français'},
                {'url': f'../de/{_de_fn}', 'flag': '../flags/de.png', 'label': 'Deutsch'},
            ]
        elif is_de:
            _alt_links = [
                {'url': f'../en/{_en_fn}', 'flag': '../flags/gb.png', 'label': 'English'},
                {'url': f'../us/{_us_fn}', 'flag': '../flags/us.png', 'label': 'English (US)'},
                {'url': f'../{_fr_fn}', 'flag': '../flags/fr.png', 'label': 'Français'},
                {'url': f'../es/{_es_fn}', 'flag': '../flags/es.png', 'label': 'Español'},
            ]
        elif is_us:
            _alt_links = [
                {'url': f'../en/{_en_fn}', 'flag': '../flags/gb.png', 'label': 'English'},
                {'url': f'../{_fr_fn}', 'flag': '../flags/fr.png', 'label': 'Français'},
                {'url': f'../es/{_es_fn}', 'flag': '../flags/es.png', 'label': 'Español'},
                {'url': f'../de/{_de_fn}', 'flag': '../flags/de.png', 'label': 'Deutsch'},
            ]
        else:  # en
            _alt_links = [
                {'url': f'../{_fr_fn}', 'flag': '../flags/fr.png', 'label': 'Français'},
                {'url': f'../us/{_us_fn}', 'flag': '../flags/us.png', 'label': 'English (US)'},
                {'url': f'../es/{_es_fn}', 'flag': '../flags/es.png', 'label': 'Español'},
                {'url': f'../de/{_de_fn}', 'flag': '../flags/de.png', 'label': 'Deutsch'},
            ]
        footer_lang = 'en' if is_us else lang
        footer = footer_ranking_html(footer_lang, _alt_links)

        html_lang = loc['meta']['html_lang']

        page_html = f"""<!DOCTYPE html>
<html lang="{html_lang}">
<head>
<meta charset="UTF-8"/><meta name="viewport" content="width=device-width,initial-scale=1.0"/>
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}"/>
<link rel="canonical" href="{canonical}"/>
{hreflang_block}
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
<div class="hero-eyebrow">{comp["hero_eyebrow_prefix"]}{YEAR}</div>
<h1 class="hero-title">{h1}</h1>
<p class="hero-sub">{hero_sub}</p>
</header>
<main class="page">
{vs_cards}
<div class="section">
<div class="eyebrow">{comp["month_by_month"]}</div>
<h2 class="sec-title">{comp["detailed_title"]}</h2>
<p class="sec-intro">{comp["detailed_intro"]}</p>
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
            'hreflang_us': hreflang_us, 'hreflang_es': hreflang_es, 'lang': lang, 'filename': filename
        })


def update_sitemaps(files):
    """Append comparison pages to sitemaps."""
    fr_files  = [f for f in files if f['lang'] == 'fr']
    en_files  = [f for f in files if f['lang'] == 'en']
    us_files  = [f for f in files if f['lang'] == 'en-us']
    es_files  = [f for f in files if f['lang'] == 'es']
    de_files  = [f for f in files if f['lang'] == 'de']

    for sitemap_file, pages in [('sitemap-fr.xml', fr_files),
                                  ('sitemap-en.xml', en_files),
                                  ('sitemap-us.xml', us_files),
                                  ('sitemap-es.xml', es_files),
                                  ('sitemap-de.xml', de_files)]:
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
        da_tmp = dests.get(slug_a, {})
        db_tmp = dests.get(slug_b, {})
        es_a = da_tmp.get('slug_es', da_tmp.get('slug_en', slug_a))
        es_b = db_tmp.get('slug_es', db_tmp.get('slug_en', slug_b))
        print(f"  ✅ {fr_name}")
        print(f"  ✅ en/{en_name}")
        print(f"  ✅ us/{en_name}")
        print(f"  ✅ es/{es_a}-vs-{es_b}-clima.html")

    fr_count = sum(1 for f in generated if f['lang'] == 'fr')
    en_count = sum(1 for f in generated if f['lang'] == 'en')
    us_count = sum(1 for f in generated if f['lang'] == 'en-us')
    es_count = sum(1 for f in generated if f['lang'] == 'es')
    print(f"\n📄 {fr_count} FR + {en_count} EN + {us_count} US + {es_count} ES comparison pages")

    update_sitemaps(generated)
    print("\n✅ Done")
