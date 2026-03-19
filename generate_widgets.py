#!/usr/bin/env python3
"""
generate_widgets.py — Génère les pages widget iframe pour toutes les destinations FR
Deux formats :
  /widget/{slug}.html         — compact 320×200
  /widget/{slug}-full.html    — tableau complet 400×520
"""

import csv, json, os
from pathlib import Path

SITE_URL = 'https://bestdateweather.com'
MOIS_ABBR = ['Jan','Fév','Mar','Avr','Mai','Jui','Jul','Aoû','Sep','Oct','Nov','Déc']
MOIS_FULL = ['janvier','février','mars','avril','mai','juin',
             'juillet','août','septembre','octobre','novembre','décembre']

def load_data():
    with open('data/climate.csv', encoding='utf-8-sig') as f:
        climate = {}
        for r in csv.DictReader(f):
            climate[(r['slug'], int(r['mois_num']))] = r
    with open('data/destinations.csv', encoding='utf-8-sig') as f:
        dests = {r['slug_fr']: r for r in csv.DictReader(f)}
    return climate, dests

def score_color(s):
    s = float(s)
    if s >= 8.5: return '#16a34a'
    if s >= 7.0: return '#d97706'
    return '#dc2626'

def score_bar_width(s):
    return max(8, int(float(s) / 10 * 100))

def gen_compact(slug, dest, months):
    """Widget compact 320×200px"""
    nom = dest.get('nom_fr', slug)
    pays = dest.get('pays', '')
    flag = dest.get('flag', '')
    flag_url = f"{SITE_URL}/flags/{flag}.png" if flag else ''

    # Trouver meilleur mois
    valid = [(i, m) for i, m in enumerate(months) if m and m.get('score')]
    if not valid: return None
    best_i, best = max(valid, key=lambda x: float(x[1]['score']))
    best_score = float(best['score'])
    best_mois = MOIS_FULL[best_i].capitalize()
    color = score_color(best_score)

    # Barres de score — 12 mois
    bars = ''
    for i, m in enumerate(months):
        if not m or not m.get('score'): continue
        s = float(m['score'])
        c = score_color(s)
        h = max(4, int(s / 10 * 48))
        active = ' style="opacity:1"' if i == best_i else ''
        bars += f'<div title="{MOIS_ABBR[i]}: {s}/10" style="flex:1;display:flex;flex-direction:column;align-items:center;justify-content:flex-end;height:48px;opacity:.55;cursor:default"{active}><div style="width:100%;background:{c};border-radius:2px 2px 0 0;height:{h}px"></div></div>'

    fiche_url = f"{SITE_URL}/meilleure-periode-{slug}.html"

    return f'''<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1.0"/>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:'DM Sans',Arial,sans-serif;background:#fff;border:1px solid #e8e0d0;border-radius:12px;overflow:hidden;width:320px;height:200px}}
.top{{background:#1a1f2e;padding:12px 14px 10px;color:white}}
.dest{{display:flex;align-items:center;gap:8px;margin-bottom:6px}}
.dest img{{border-radius:2px;flex-shrink:0}}
.dest-name{{font-size:14px;font-weight:700}}
.dest-country{{font-size:11px;opacity:.6}}
.best{{display:flex;align-items:baseline;gap:6px}}
.best-label{{font-size:11px;opacity:.6;text-transform:uppercase;letter-spacing:.4px}}
.best-month{{font-size:18px;font-weight:800;color:{color}}}
.best-score{{font-size:13px;font-weight:700;color:{color}}}
.bars{{padding:8px 14px 0;display:flex;gap:2px;align-items:flex-end}}
.footer{{padding:6px 14px;display:flex;align-items:center;justify-content:space-between}}
.footer-brand{{font-size:10px;color:#94a3b8}}
.cta{{font-size:11px;font-weight:700;color:#d97706;text-decoration:none;background:#fff8ec;border:1px solid #d97706;border-radius:6px;padding:3px 8px}}
.cta:hover{{background:#d97706;color:white}}
</style>
</head>
<body>
<div class="top">
  <div class="dest">
    {'<img src="' + flag_url + '" width="18" height="13" alt="">' if flag_url else ''}
    <div>
      <div class="dest-name">{nom}</div>
      <div class="dest-country">{pays}</div>
    </div>
  </div>
  <div class="best">
    <span class="best-label">Meilleur mois</span>
    <span class="best-month">{best_mois}</span>
    <span class="best-score">{best_score:.1f}/10</span>
  </div>
</div>
<div class="bars">{bars}</div>
<div class="footer">
  <span class="footer-brand">bestdateweather.com</span>
  <a href="{fiche_url}" target="_blank" class="cta">Voir le guide →</a>
</div>
</body>
</html>'''

def gen_full(slug, dest, months):
    """Widget tableau complet 400×520px"""
    nom = dest.get('nom_fr', slug)
    pays = dest.get('pays', '')
    flag = dest.get('flag', '')
    flag_url = f"{SITE_URL}/flags/{flag}.png" if flag else ''
    fiche_url = f"{SITE_URL}/meilleure-periode-{slug}.html"

    valid = [(i, m) for i, m in enumerate(months) if m and m.get('score')]
    if not valid: return None
    best_i, best = max(valid, key=lambda x: float(x[1]['score']))

    rows = ''
    for i, m in enumerate(months):
        if not m or not m.get('score'): continue
        s = float(m['score'])
        c = score_color(s)
        is_best = i == best_i
        bg = 'background:#fef9f0;' if is_best else ''
        fw = 'font-weight:700;' if is_best else ''
        star = '⭐' if is_best else ''
        rows += f'''<tr style="{bg}">
  <td style="padding:6px 10px;font-size:13px;{fw}color:#1a1f2e">{star}{MOIS_ABBR[i]}</td>
  <td style="padding:6px 8px;text-align:center;font-size:13px;{fw}color:{c}">{s:.1f}</td>
  <td style="padding:6px 8px;text-align:center;font-size:12px;color:#475569">{m.get("tmax","?")}°C</td>
  <td style="padding:6px 8px;text-align:center;font-size:12px;color:#475569">{m.get("rain_pct","?")}%</td>
  <td style="padding:6px 10px"><div style="height:8px;background:{c};border-radius:4px;width:{score_bar_width(s)}%"></div></td>
</tr>'''

    return f'''<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1.0"/>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:'DM Sans',Arial,sans-serif;background:#fff;border:1px solid #e8e0d0;border-radius:12px;overflow:hidden;width:400px}}
.header{{background:#1a1f2e;padding:14px 16px;color:white;display:flex;align-items:center;gap:10px}}
.header img{{border-radius:2px}}
.header-name{{font-size:16px;font-weight:700}}
.header-sub{{font-size:11px;opacity:.6;margin-top:2px}}
table{{width:100%;border-collapse:collapse}}
th{{background:#f8f6f0;padding:6px 8px;font-size:10px;font-weight:700;color:#64748b;text-transform:uppercase;letter-spacing:.4px;text-align:center}}
th:first-child{{text-align:left;padding-left:10px}}
tr:nth-child(even){{background:#fafaf8}}
.footer{{padding:10px 16px;display:flex;align-items:center;justify-content:space-between;border-top:1px solid #e8e0d0}}
.brand{{font-size:10px;color:#94a3b8}}
.cta{{font-size:12px;font-weight:700;color:white;background:#d97706;border-radius:8px;padding:6px 12px;text-decoration:none}}
.cta:hover{{background:#c69a3a}}
</style>
</head>
<body>
<div class="header">
  {'<img src="' + flag_url + '" width="22" height="16" alt="">' if flag_url else ''}
  <div>
    <div class="header-name">{nom} — Météo par mois</div>
    <div class="header-sub">{pays} · 10 ans de données ERA5</div>
  </div>
</div>
<table>
<thead><tr>
  <th>Mois</th><th>Score</th><th>T° max</th><th>Pluie</th><th style="padding-right:10px">Météo</th>
</tr></thead>
<tbody>{rows}</tbody>
</table>
<div class="footer">
  <span class="brand">bestdateweather.com</span>
  <a href="{fiche_url}" target="_blank" class="cta">Guide complet →</a>
</div>
</body>
</html>'''

def main():
    climate, dests = load_data()
    out_dir = Path('widget')
    out_dir.mkdir(exist_ok=True)

    ok_compact = ok_full = 0
    for slug, dest in dests.items():
        months = [climate.get((slug, m)) for m in range(1, 13)]

        html_compact = gen_compact(slug, dest, months)
        if html_compact:
            (out_dir / f'{slug}.html').write_text(html_compact, encoding='utf-8')
            ok_compact += 1

        html_full = gen_full(slug, dest, months)
        if html_full:
            (out_dir / f'{slug}-full.html').write_text(html_full, encoding='utf-8')
            ok_full += 1

    # Page d'embed doc
    doc = gen_embed_doc(dests)
    (out_dir / 'index.html').write_text(doc, encoding='utf-8')

    print(f"✅ {ok_compact} widgets compacts")
    print(f"✅ {ok_full} widgets complets")
    print(f"✅ widget/index.html — page de documentation")

def gen_embed_doc(dests):
    """Page de documentation pour les blogueurs"""
    sample_slugs = ['barcelone', 'bali', 'paris', 'tokyo', 'new-york']
    options = ''.join(f'<option value="{s}">{dests.get(s,{}).get("nom_fr",s)}</option>'
                      for s in sample_slugs if s in dests)

    return f'''<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1.0"/>
<title>Widgets météo voyage — BestDateWeather</title>
<style>
body{{font-family:'DM Sans',Arial,sans-serif;max-width:800px;margin:0 auto;padding:32px 16px;color:#1a1f2e}}
h1{{font-size:28px;font-weight:800;margin-bottom:8px}}
h2{{font-size:18px;font-weight:700;margin:32px 0 12px}}
.sub{{color:#64748b;margin-bottom:32px}}
.widget-row{{display:flex;gap:24px;flex-wrap:wrap;margin-bottom:24px}}
pre{{background:#f1f5f9;padding:14px;border-radius:8px;font-size:12px;overflow-x:auto;line-height:1.6}}
select{{padding:8px 12px;border:1px solid #e8e0d0;border-radius:8px;font-size:14px;margin-bottom:16px}}
.badge{{display:inline-block;background:#d97706;color:white;font-size:11px;font-weight:700;padding:2px 8px;border-radius:20px;margin-left:8px}}
</style>
</head>
<body>
<h1>Widgets météo voyage <span class="badge">Gratuit</span></h1>
<p class="sub">Ajoutez des données météo à votre blog voyage en 1 ligne de code. 696 destinations, 100% gratuit, aucune inscription.</p>

<h2>Choisir une destination</h2>
<select onchange="updateCode(this.value)">
{options}
<option value="">— Autre destination —</option>
</select>

<h2>Format compact (320×200)</h2>
<div class="widget-row">
  <iframe id="preview-compact" src="{SITE_URL}/widget/barcelone.html" width="320" height="200" frameborder="0" style="border-radius:12px;border:1px solid #e8e0d0"></iframe>
</div>
<pre id="code-compact">&lt;iframe src="{SITE_URL}/widget/barcelone.html" width="320" height="200" frameborder="0" style="border-radius:12px"&gt;&lt;/iframe&gt;</pre>

<h2>Format complet (400×auto)</h2>
<div class="widget-row">
  <iframe id="preview-full" src="{SITE_URL}/widget/barcelone-full.html" width="400" height="520" frameborder="0" style="border-radius:12px;border:1px solid #e8e0d0"></iframe>
</div>
<pre id="code-full">&lt;iframe src="{SITE_URL}/widget/barcelone-full.html" width="400" height="520" frameborder="0" style="border-radius:12px"&gt;&lt;/iframe&gt;</pre>

<script>
function updateCode(slug) {{
  if (!slug) return;
  document.getElementById('preview-compact').src = '{SITE_URL}/widget/' + slug + '.html';
  document.getElementById('preview-full').src = '{SITE_URL}/widget/' + slug + '-full.html';
  document.getElementById('code-compact').textContent = '<iframe src="{SITE_URL}/widget/' + slug + '.html" width="320" height="200" frameborder="0" style="border-radius:12px"></iframe>';
  document.getElementById('code-full').textContent = '<iframe src="{SITE_URL}/widget/' + slug + '-full.html" width="400" height="520" frameborder="0" style="border-radius:12px"></iframe>';
}}
</script>
</body>
</html>'''

if __name__ == '__main__':
    main()
