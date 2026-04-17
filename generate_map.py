#!/usr/bin/env python3
"""Generate the interactive world climate map in 5 languages."""

import json
import csv
from pathlib import Path
from scoring import compute_ski_score, profile_score
from generate_piliers import load_destinations, load_climate, load_country_info
from generate_classements import compute_nomad

ROOT = Path('.')
SUPPORTED_LANGS = ['fr', 'en', 'en-us', 'es', 'de']

# URL config per lang
LANG_CONFIG = {
    'fr':    {'subdir': '',   'filename': 'carte.html',  'hub': 'index.html',     'flag': 'fr', 'label': 'FR', 'cookie': 'fr'},
    'en':    {'subdir': 'en', 'filename': 'map.html',    'hub': 'app.html',       'flag': 'gb', 'label': 'EN', 'cookie': 'en'},
    'en-us': {'subdir': 'us', 'filename': 'map.html',    'hub': 'app.html',       'flag': 'us', 'label': 'EN-US', 'cookie': 'en-us'},
    'es':    {'subdir': 'es', 'filename': 'mapa.html',   'hub': 'app.html',       'flag': 'es', 'label': 'ES', 'cookie': 'es'},
    'de':    {'subdir': 'de', 'filename': 'karte.html',  'hub': 'app.html',       'flag': 'de', 'label': 'DE', 'cookie': 'de'},
}

def load_locale(lang):
    with open(f'locales/{lang}.json') as f:
        return json.load(f)

def asset_prefix(lang):
    return '../' if LANG_CONFIG[lang]['subdir'] else ''

def build_map_data():
    """Build MAP_DATA JS variable with all scores."""
    dests_raw = load_destinations()
    climate_raw = load_climate()
    country_info = load_country_info()

    nomad_map = {}
    for r in compute_nomad(climate_raw, dests_raw, country_info):
        if r['nomad_score'] is not None:
            nomad_map[r['slug']] = round(r['nomad_score'], 1)

    dests = {}
    with open('data/destinations.csv') as f:
        for row in csv.DictReader(f):
            pays = row['pays']
            ci = country_info.get(pays, {})
            dests[row['slug_fr']] = {
                'n': row['nom_en'] or row['nom_bare'],
                'lat': float(row['lat']), 'lon': float(row['lon']),
                'f': row['flag'], 'slug_en': row['slug_en'],
                'rl': ci.get('risk_level', 2), 'bi': ci.get('budget_index', 3),
            }

    climate = {}
    with open('data/climate.csv') as f:
        for row in csv.DictReader(f):
            slug = row['slug']
            mi = int(row['mois_num']) - 1
            if slug not in climate: climate[slug] = [None]*12
            try:
                tmax = float(row['tmax']); rain = float(row['rain_pct']); sun = float(row['sun_h'])
                dew  = float(row['dew_point_mean']) if row.get('dew_point_mean','').strip() else None
                s    = round(float(row['score']), 1)
                b    = round(float(row['beach_score']), 1) if row.get('beach_score','').strip() else None
                k    = round(compute_ski_score(tmax, rain, sun), 1)
                sc   = round(profile_score(tmax, rain, sun, dew, 'cool') * 10, 1)
                sw   = round(profile_score(tmax, rain, sun, dew, 'warm') * 10, 1)
                sh   = round(profile_score(tmax, rain, sun, dew, 'humid') * 10, 1)
                climate[slug][mi] = [s, b, k, sc, sw, sh]
            except: climate[slug][mi] = None

    def avg(lst): return round(sum(lst)/len(lst), 1) if lst else None

    points = []
    for slug, d in dests.items():
        if slug not in climate: continue
        months = climate[slug]
        if not any(m for m in months): continue
        nd = nomad_map.get(slug)
        annual = [
            avg([m[0] for m in months if m and m[0]]),
            avg([m[1] for m in months if m and m[1]]),
            avg([m[2] for m in months if m and m[2]]),
            avg([m[3] for m in months if m and m[3]]),
            avg([m[4] for m in months if m and m[4]]),
            avg([m[5] for m in months if m and m[5]]),
            nd,
        ]
        best_mi = max(range(12), key=lambda i: (months[i] or [0])[0])
        points.append([d['slug_en'], d['n'], d['lat'], d['lon'],
                        d['f'], d['rl'], d['bi'], best_mi, months, annual])

    return f"var MAP_DATA={json.dumps(points, separators=(',',':'))};"

def build_lang_selector(lang):
    """Build language selector HTML matching hub pages."""
    cfg = LANG_CONFIG[lang]
    ap = asset_prefix(lang)
    # Current lang button
    html = f'''<button class="lang-btn" id="lang-btn" onclick="toggleLangMenu()" aria-label="Language">
          <img src="{ap}flags/{cfg['flag']}.png" width="20" height="15" alt="" style="border-radius:2px;display:block">
          <svg viewBox="0 0 24 24" width="10" height="10" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="6 9 12 15 18 9"/></svg>
        </button>
        <div class="lang-drop" id="lang-drop">'''

    for other_lang, other_cfg in LANG_CONFIG.items():
        other_ap = asset_prefix(other_lang)
        if other_lang == lang:
            html += f'\n          <a href="#" class="active" onclick="return false" style="cursor:default"><img src="{ap}flags/{other_cfg["flag"]}.png" width="20" height="14" alt=""> {other_cfg["label"]}</a>'
        else:
            # Relative path to the other map file
            if cfg['subdir'] == '' and other_cfg['subdir'] == '':
                href = other_cfg['filename']
            elif cfg['subdir'] == '':
                href = f"{other_cfg['subdir']}/{other_cfg['filename']}"
            elif other_cfg['subdir'] == '':
                href = f"../{other_cfg['filename']}"
            else:
                href = f"../{other_cfg['subdir']}/{other_cfg['filename']}"
            ocookie = other_cfg['cookie']
            oflag = other_cfg['flag']
            olabel = other_cfg['label']
            html += f'\n          <a href="{href}" onclick="document.cookie=\'bdw_lang={ocookie};path=/;max-age=31536000\'"><img src="{ap}flags/{oflag}.png" width="20" height="14" alt=""> {olabel}</a>'

    html += '\n        </div>'
    return html

def build_hreflang(lang):
    lines = []
    for l, cfg in LANG_CONFIG.items():
        base = 'https://bestdateweather.com'
        path = f"/{cfg['subdir']}/{cfg['filename']}" if cfg['subdir'] else f"/{cfg['filename']}"
        hl = 'fr' if l=='fr' else 'en-US' if l=='en-us' else 'en-GB' if l=='en' else l
        lines.append(f'<link rel="alternate" hreflang="{hl}" href="{base}{path}"/>')
    return '\n'.join(lines)

def generate_map_page(lang, map_data_js, world_json, clabels_json):
    loc = load_locale(lang)
    pil = loc['pilier']
    m   = loc['map']
    cfg = LANG_CONFIG[lang]
    ap  = asset_prefix(lang)
    months_full = loc['months']
    months_short = [mn[:3] for mn in months_full]

    # Labels localisés
    tab_gen   = pil.get('tab_meteo_annual', '☀️ General weather')
    tab_beach = pil.get('tab_beach_annual', '🏖️ Beach')
    tab_ski   = pil.get('tab_ski_annual',   '⛷️ Ski')
    tab_nomad = pil.get('tab_nomad',        '💻 Digital Nomad')
    sl = pil.get('secu_labels', {'1':'🟢','2':'🟡','3':'🟠','4':'🔴'})
    bl = pil.get('budget_labels', {'1':'💚','2':'💛','3':'🟡','4':'🟠','5':'🔴'})
    secu_all   = pil.get('secu_all', 'All destinations')
    budget_all = pil.get('budget_all', 'All budgets')
    fp_secu    = pil.get('fp_secu', 'SAFETY')
    fp_budget  = pil.get('fp_budget', 'BUDGET')

    # Balanced / Cool / Warm / Humid labels
    prof_labels_raw = {
        'fr': {'bal':'🌤️ Équilibré','cool':'❄️ Frais','warm':'🔥 Chaud','hum':'💧 Humidité'},
        'en': {'bal':'🌤️ Balanced','cool':'❄️ Prefer cool','warm':'🔥 Prefer warm','hum':'💧 Humidity sensitive'},
        'en-us': {'bal':'🌤️ Balanced','cool':'❄️ Prefer cool','warm':'🔥 Prefer warm','hum':'💧 Humidity sensitive'},
        'es': {'bal':'🌤️ Equilibrado','cool':'❄️ Prefiero frío','warm':'🔥 Prefiero calor','hum':'💧 Sensible humedad'},
        'de': {'bal':'🌤️ Ausgewogen','cool':'❄️ Kühl bevorzugt','warm':'🔥 Warm bevorzugt','hum':'💧 Feuchtigkeitssensibel'},
    }
    pl = prof_labels_raw.get(lang, prof_labels_raw['en'])

    # Hub URL (back link)
    hub_url = f"{ap}{cfg['hub']}"
    # Canonical
    canon_base = 'https://bestdateweather.com'
    canon_path = f"/{cfg['subdir']}/{cfg['filename']}" if cfg['subdir'] else f"/{cfg['filename']}"
    canonical = canon_base + canon_path
    # map-data.js path
    mapdata_src = f"{ap}map-data.js"

    # Language selector
    lang_selector_html = build_lang_selector(lang)
    hreflang = build_hreflang(lang)

    # Month items
    month_items = '\n'.join(
        f'      <div class="dd-item{" on" if i==3 else ""}" onclick="pickMonth({i})">{months_full[i]}</div>'
        for i in range(12)
    )
    month_items = f'      <div class="dd-item" onclick="pickMonth(12)">{m["map_annual"]}</div>\n' + month_items

    # Safety items
    secu_items = f'      <div class="dd-item on" onclick="pickRL(4)">{secu_all}</div>\n'
    for r in [1,2,3]:
        secu_items += f'      <div class="dd-item" onclick="pickRL({r})">≤ {sl.get(str(r), str(r))}</div>\n'

    # Budget items
    budget_items = f'      <div class="dd-item on" onclick="pickBI(5)">{budget_all}</div>\n'
    for b in [1,2,3,4]:
        budget_items += f'      <div class="dd-item" onclick="pickBI({b})">≤ {bl.get(str(b), str(b))}</div>\n'

    # Min score items
    all_scores_lbl = m['map_all_scores']
    min_items = f'      <div class="dd-item on" onclick="pickMin(0)">{all_scores_lbl}</div>\n'
    for s in [5,6,7,8,9]:
        min_items += f'      <div class="dd-item" onclick="pickMin({s})">≥ {s}.0</div>\n'

    # Secu/Budget label strings for JS
    secu_labels_js = json.dumps({str(r): sl.get(str(r),'') for r in [1,2,3]}, ensure_ascii=False)
    budget_labels_js = json.dumps({str(b): bl.get(str(b),'') for b in [1,2,3,4]}, ensure_ascii=False)

    html = f'''<!DOCTYPE html>
<html lang="{loc['meta'].get('html_lang', lang)}">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>{m['map_title']}</title>
<meta name="description" content="{m['map_desc']}"/>
<link rel="canonical" href="{canonical}"/>
{hreflang}
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css"/>
<link rel="icon" type="image/x-icon" href="{ap}favicon.ico"/>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
html,body{{height:100%;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#1a1f2e;color:white;overflow:hidden}}
.topbar{{position:fixed;top:0;left:0;right:0;z-index:1000;background:#1a1f2e;border-bottom:1px solid rgba(255,255,255,.08);display:flex;align-items:center;justify-content:space-between;padding:0 12px;height:48px;gap:8px}}
.brand{{font-size:16px;font-weight:700;color:white;text-decoration:none;white-space:nowrap;flex-shrink:0}}
.brand em{{color:#c9a84c;font-style:normal}}
.topbar-stats{{font-size:11px;color:rgba(255,255,255,.4);white-space:nowrap;flex:1;text-align:center;overflow:hidden;text-overflow:ellipsis}}
.topbar-stats b{{color:white}}
.topbar-right{{display:flex;align-items:center;gap:6px;flex-shrink:0}}
.back{{font-size:11px;color:#5a6c7d;text-decoration:none;white-space:nowrap}}
.back:hover{{color:white}}
.lang-btn{{background:none;border:1.5px solid rgba(255,255,255,.15);border-radius:8px;padding:4px 8px;cursor:pointer;color:rgba(255,255,255,.7);display:flex;align-items:center;gap:5px;font-size:11px;font-weight:600;font-family:inherit;transition:all .15s}}
.lang-btn:hover{{border-color:rgba(255,255,255,.35);color:#fff;background:rgba(255,255,255,.08)}}
.lang-btn img{{border-radius:2px;display:block}}
.lang-drop{{display:none;position:fixed;background:#1e2640;border:1px solid rgba(255,255,255,.12);border-radius:10px;box-shadow:0 8px 24px rgba(0,0,0,.6);padding:4px;z-index:9999;min-width:120px}}
.lang-drop.open{{display:block}}
.lang-drop a{{display:flex;align-items:center;gap:8px;padding:7px 10px;border-radius:7px;font-size:12px;color:rgba(255,255,255,.7);text-decoration:none;white-space:nowrap}}
.lang-drop a:hover{{background:rgba(255,255,255,.08);color:white}}
.lang-drop a.active{{color:#c9a84c;font-weight:700}}
.fbar{{position:fixed;top:48px;left:0;right:0;z-index:990;background:rgba(20,25,40,.97);border-bottom:1px solid rgba(255,255,255,.06);display:flex;align-items:center;gap:6px;padding:7px 12px;overflow-x:auto;overflow-y:visible;scrollbar-width:none}}
.fbar::-webkit-scrollbar{{display:none}}
.dd{{position:relative;display:inline-flex;flex-shrink:0}}
.dd-btn{{display:inline-flex;align-items:center;gap:4px;padding:5px 10px;border:1px solid rgba(255,255,255,.18);border-radius:16px;font-size:11px;font-weight:600;cursor:pointer;color:rgba(255,255,255,.75);background:transparent;white-space:nowrap;transition:border-color .12s;font-family:inherit}}
.dd-btn:hover{{border-color:#c9a84c;color:white}}
.dd-btn.sel{{border-color:#c9a84c;background:rgba(201,168,76,.12);color:#c9a84c}}
.dd-arr{{font-size:7px;opacity:.45}}
.dd-menu{{display:none;position:fixed;background:#1e2640;border:1px solid rgba(255,255,255,.12);border-radius:10px;box-shadow:0 8px 24px rgba(0,0,0,.6);padding:4px;z-index:9999;min-width:150px;max-height:280px;overflow-y:auto}}
.dd.open .dd-menu{{display:block}}
.dd-item{{padding:7px 12px;border-radius:7px;font-size:12px;cursor:pointer;color:rgba(255,255,255,.7);white-space:nowrap}}
.dd-item:hover{{background:rgba(255,255,255,.08);color:white}}
.dd-item.on{{color:#c9a84c;font-weight:700}}
.fsep{{width:1px;height:16px;background:rgba(255,255,255,.1);flex-shrink:0}}
#map{{position:fixed;top:88px;left:0;right:0;bottom:0}}
.leaflet-container{{background:#0d1117}}
.bdw-dot{{border-radius:50%;border:1.5px solid rgba(255,255,255,.2);cursor:pointer;transition:transform .1s}}
.bdw-dot:hover{{transform:scale(1.5)}}
.leaflet-popup-content-wrapper{{background:#1a1f2e;border:1px solid rgba(255,255,255,.12);border-radius:12px;box-shadow:0 8px 32px rgba(0,0,0,.6);padding:0;overflow:hidden}}
.leaflet-popup-tip{{background:#1a1f2e}}
.leaflet-popup-content{{margin:0;width:200px!important}}
.pi{{padding:14px}}
.pi-flag{{font-size:18px}}
.pi-name{{font-size:15px;font-weight:700;margin:5px 0 2px}}
.pi-score{{font-size:26px;font-weight:700;line-height:1;margin:6px 0 2px}}
.pi-month{{font-size:11px;color:#5a6c7d;margin-bottom:10px}}
.pi-bars{{display:flex;gap:2px;align-items:flex-end;height:28px;margin-bottom:10px}}
.pi-bar{{flex:1;border-radius:2px 2px 0 0;min-height:2px}}
.pi-bar.cur{{outline:2px solid white;outline-offset:1px}}
.pi-link{{display:block;background:#c9a84c;color:#1a1f2e;text-align:center;padding:7px;font-size:12px;font-weight:700;text-decoration:none;border-radius:7px}}
.dest-label{{background:rgba(20,25,40,.85);border:1px solid rgba(255,255,255,.1);border-radius:4px;padding:2px 5px;font-size:10px;font-weight:600;color:rgba(255,255,255,.85);white-space:nowrap;pointer-events:none}}
.dest-label::before{{display:none}}
.clbl{{background:transparent!important;border:none!important;box-shadow:none!important;color:rgba(255,255,255,.4);font-size:10px;font-weight:600;text-transform:uppercase;letter-spacing:.5px;pointer-events:none}}
.legend{{position:fixed;bottom:16px;left:16px;z-index:900;background:rgba(20,25,40,.92);border:1px solid rgba(255,255,255,.08);border-radius:10px;padding:9px 12px;font-size:11px}}
.lt{{font-weight:600;color:#5a6c7d;text-transform:uppercase;letter-spacing:.4px;margin-bottom:6px}}
.lr{{display:flex;align-items:center;gap:7px;margin-bottom:3px;color:rgba(255,255,255,.6)}}
.ld{{width:9px;height:9px;border-radius:50%;border:1px solid rgba(255,255,255,.2)}}
@media(max-width:500px){{
  .topbar-stats{{display:none}}
  .brand{{font-size:14px}}
  .back{{font-size:10px}}
  .fbar{{padding:5px 8px;gap:4px}}
  .dd-btn{{font-size:10px;padding:4px 7px;border-radius:12px}}
  .dd-arr{{display:none}}
  #map{{top:82px}}
  .legend{{display:none}}
}}
</style>
</head>
<body>
<div class="topbar">
  <a href="/" class="brand">Best<em>Date</em>Weather</a>
  <div class="topbar-stats">{m['map_showing']} <b id="sc">—</b> {m['map_destinations']} · {m['map_best']} <b id="sb">—</b>/10</div>
  <div class="topbar-right">
    <div style="position:relative">
      {lang_selector_html}
    </div>
    <a href="{hub_url}" class="back">{m['map_back']}</a>
  </div>
</div>
<div class="fbar">
  <div class="dd" id="dd-m">
    <button class="dd-btn sel" id="dd-m-btn" onclick="openDD('m')">{months_short[3]} <span class="dd-arr">▾</span></button>
    <div class="dd-menu" id="dd-m-menu">
{month_items}
    </div>
  </div>
  <div class="fsep"></div>
  <div class="dd" id="dd-mode">
    <button class="dd-btn" id="dd-mode-btn" onclick="openDD('mode')">{tab_gen} <span class="dd-arr">▾</span></button>
    <div class="dd-menu" id="dd-mode-menu">
      <div class="dd-item on" onclick="pickMode('gen',{json.dumps(tab_gen)})">{tab_gen}</div>
      <div class="dd-item" onclick="pickMode('beach',{json.dumps(tab_beach)})">{tab_beach}</div>
      <div class="dd-item" onclick="pickMode('ski',{json.dumps(tab_ski)})">{tab_ski}</div>
      <div class="dd-item" onclick="pickMode('nomad',{json.dumps(tab_nomad)})">{tab_nomad}</div>
    </div>
  </div>
  <div class="fsep"></div>
  <div class="dd" id="dd-prof">
    <button class="dd-btn" id="dd-prof-btn" onclick="openDD('prof')">{pl['bal']} <span class="dd-arr">▾</span></button>
    <div class="dd-menu" id="dd-prof-menu">
      <div class="dd-item on" onclick="pickProf('bal',{json.dumps(pl['bal'])})">{pl['bal']}</div>
      <div class="dd-item" onclick="pickProf('cool',{json.dumps(pl['cool'])})">{pl['cool']}</div>
      <div class="dd-item" onclick="pickProf('warm',{json.dumps(pl['warm'])})">{pl['warm']}</div>
      <div class="dd-item" onclick="pickProf('hum',{json.dumps(pl['hum'])})">{pl['hum']}</div>
    </div>
  </div>
  <div class="fsep"></div>
  <div class="dd" id="dd-rl">
    <button class="dd-btn" id="dd-rl-btn" onclick="openDD('rl')">{fp_secu} <span class="dd-arr">▾</span></button>
    <div class="dd-menu" id="dd-rl-menu">
{secu_items}    </div>
  </div>
  <div class="fsep"></div>
  <div class="dd" id="dd-bi">
    <button class="dd-btn" id="dd-bi-btn" onclick="openDD('bi')">{fp_budget} <span class="dd-arr">▾</span></button>
    <div class="dd-menu" id="dd-bi-menu">
{budget_items}    </div>
  </div>
  <div class="fsep"></div>
  <div class="dd" id="dd-min">
    <button class="dd-btn" id="dd-min-btn" onclick="openDD('min')">{m['map_min_score']} <span class="dd-arr">▾</span></button>
    <div class="dd-menu" id="dd-min-menu">
{min_items}    </div>
  </div>
</div>
<div id="map"></div>
<div class="legend">
  <div class="lt">Score</div>
  <div class="lr"><div class="ld" style="background:#1a7a4a"></div>8.6+ Excellent</div>
  <div class="lr"><div class="ld" style="background:#2d9e60"></div>7.6–8.5 Great</div>
  <div class="lr"><div class="ld" style="background:#84cc16"></div>6.3–7.5 Good</div>
  <div class="lr"><div class="ld" style="background:#f59e0b"></div>5.0–6.2 Fair</div>
  <div class="lr"><div class="ld" style="background:#f97316"></div>3.5–4.9 Poor</div>
  <div class="lr"><div class="ld" style="background:#ef4444"></div>0–3.4 Avoid</div>
</div>
<script src="{mapdata_src}"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js"></script>
<script>
var MN={json.dumps(months_short)};
var MF={json.dumps(months_full)};
var MF_ANNUAL={json.dumps(m['map_annual'])};
var FP_SECU={json.dumps(fp_secu)};
var FP_BUDGET={json.dumps(fp_budget)};
var SECU_LABELS={secu_labels_js};
var BUDGET_LABELS={budget_labels_js};
var CUR_M=new Date().getMonth();
var CUR_MODE='gen',CUR_PROF='bal',CUR_RL=4,CUR_BI=5,CUR_MIN=0;

document.getElementById('dd-m-btn').innerHTML=MN[CUR_M]+' <span class="dd-arr">▾</span>';
document.querySelectorAll('#dd-m-menu .dd-item').forEach(function(el,i){{el.classList.toggle('on',i===CUR_M+1);}});

function scoreColor(s){{return s>=8.6?'#1a7a4a':s>=7.6?'#2d9e60':s>=6.3?'#84cc16':s>=5?'#f59e0b':s>=3.5?'#f97316':'#ef4444';}}
function flagEmoji(c){{try{{return c.toUpperCase().split('').map(function(x){{return String.fromCodePoint(x.charCodeAt(0)+127397)}}).join('')}}catch(e){{return '🌍'}}}}

function getScore(d,mi){{
  if(CUR_MODE==='nomad'){{var nd=(d[9]||[])[6];return nd||null;}}
  var m;
  if(mi===12){{m=d[9]||null;}}else{{m=(d[8]||[])[mi];}}
  if(!m)return null;
  if(CUR_MODE==='beach')return m[1];
  if(CUR_MODE==='ski')return m[2];
  if(CUR_PROF==='cool')return m[3];
  if(CUR_PROF==='warm')return m[4];
  if(CUR_PROF==='hum')return m[5];
  return m[0];
}}

// Language selector
function toggleLangMenu(){{
  var drop=document.getElementById('lang-drop');
  var btn=document.getElementById('lang-btn');
  var isOpen=drop.classList.contains('open');
  drop.classList.toggle('open',!isOpen);
  if(!isOpen){{var r=btn.getBoundingClientRect();drop.style.top=(r.bottom+4)+'px';drop.style.right=(window.innerWidth-r.right)+'px';drop.style.left='auto';}}
}}
document.addEventListener('click',function(e){{
  if(!e.target.closest('#lang-btn')&&!e.target.closest('#lang-drop'))
    document.getElementById('lang-drop').classList.remove('open');
}});

// Dropdowns
function openDD(id){{
  var isOpen=document.getElementById('dd-'+id).classList.contains('open');
  closeDD();
  if(isOpen)return;
  var el=document.getElementById('dd-'+id);el.classList.add('open');
  var btn=document.getElementById('dd-'+id+'-btn');
  var menu=document.getElementById('dd-'+id+'-menu');
  var r=btn.getBoundingClientRect();
  menu.style.top=(r.bottom+4)+'px';
  menu.style.left=Math.max(4,Math.min(r.left,window.innerWidth-160))+'px';
}}
function closeDD(){{document.querySelectorAll('.dd').forEach(function(d){{d.classList.remove('open');}});}}
document.addEventListener('click',function(e){{if(!e.target.closest('.dd'))closeDD();}});
function setBtn(id,label,active){{var btn=document.getElementById('dd-'+id+'-btn');if(btn){{btn.innerHTML=label+' <span class="dd-arr">▾</span>';btn.classList.toggle('sel',active);}}}}

function pickMonth(mi){{CUR_M=mi;setBtn('m',mi===12?MF_ANNUAL:MN[mi],true);document.querySelectorAll('#dd-m-menu .dd-item').forEach(function(el,i){{el.classList.toggle('on',i===(mi===12?0:mi+1));}});closeDD();render();}}
function pickMode(mode,label){{
  CUR_MODE=mode;setBtn('mode',label,mode!=='gen');
  document.querySelectorAll('#dd-mode-menu .dd-item').forEach(function(el){{el.classList.toggle('on',el.textContent.trim()===label);}});
  var isNomad=mode==='nomad';
  ['dd-rl','dd-bi','dd-min','dd-prof'].forEach(function(id){{var el=document.getElementById(id);if(el){{el.style.display=isNomad?'none':'';el.style.pointerEvents=isNomad?'none':'';}}}} );
  document.querySelectorAll('.fsep').forEach(function(el,i){{if(i>=2)el.style.display=isNomad?'none':'';}} );
  closeDD();render();
}}
function pickProf(prof,label){{CUR_PROF=prof;setBtn('prof',label,prof!=='bal');document.querySelectorAll('#dd-prof-menu .dd-item').forEach(function(el){{el.classList.toggle('on',el.textContent.trim()===label);}});closeDD();render();}}
function pickRL(rl){{CUR_RL=rl;var lbl=SECU_LABELS[String(rl)];var active=rl<4;setBtn('rl',active?'🛡 ≤ '+lbl:FP_SECU,active);document.querySelectorAll('#dd-rl-menu .dd-item').forEach(function(el,i){{el.classList.toggle('on',i===(rl===4?0:rl===1?1:rl===2?2:3));}});closeDD();render();}}
function pickBI(bi){{CUR_BI=bi;var lbl=BUDGET_LABELS[String(bi)];var active=bi<5;setBtn('bi',active?'≤ '+lbl:FP_BUDGET,active);document.querySelectorAll('#dd-bi-menu .dd-item').forEach(function(el,i){{el.classList.toggle('on',i===(bi===5?0:bi===1?1:bi===2?2:bi===3?3:4));}});closeDD();render();}}
function pickMin(min){{CUR_MIN=min;setBtn('min',min>0?('≥ '+min.toFixed(1)):'{m['map_min_score']}',min>0);document.querySelectorAll('#dd-min-menu .dd-item').forEach(function(el,i){{el.classList.toggle('on',i===(min===0?0:min-4));}});closeDD();render();}}

// Map
var map=L.map('map',{{center:[20,10],zoom:2,minZoom:2,maxZoom:8,zoomControl:true,attributionControl:false}});
L.control.attribution({{position:'bottomright'}}).addTo(map);
var WORLD={world_json};
L.geoJSON(WORLD,{{style:{{fillColor:'#1e2640',fillOpacity:1,color:'#3a4a6a',weight:0.6}}}}).addTo(map);
var CLABELS={clabels_json};
CLABELS.forEach(function(c){{
  var sz=c.l===0?'11px':c.l===1?'9px':'8px';
  var op=c.l===0?0.55:c.l===1?0.4:0.3;
  var minZ=c.l===0?2:c.l===1?3:4;
  var icon=L.divIcon({{className:'clbl',html:'<span style="font-size:'+sz+';opacity:'+op+'">'+c.n+'</span>',iconSize:[c.n.length*7,14],iconAnchor:[c.n.length*3.5,7]}});
  var mk=L.marker([c.lat,c.lon],{{icon:icon,interactive:false,zIndexOffset:-1000}}).addTo(map);
  map.on('zoomend',function(){{var el=mk.getElement();if(el)el.style.display=map.getZoom()>=minZ?'':'none';}});
  map.fire('zoomend');
}});
var layer=L.layerGroup().addTo(map);
function render(){{
  layer.clearLayers();var best=0,cnt=0;
  (window.MAP_DATA||[]).forEach(function(d){{
    if(CUR_MODE!=='nomad'){{if(d[5]>CUR_RL||d[6]>CUR_BI)return;}}
    var s=getScore(d,CUR_M);if(!s||s<=0||s<CUR_MIN)return;
    cnt++;if(s>best)best=s;
    var z=map.getZoom();var sz=Math.max(4,Math.min(10,z+1));var col=scoreColor(s);
    var icon=L.divIcon({{className:'',html:'<div class="bdw-dot" style="width:'+sz+'px;height:'+sz+'px;background:'+col+';opacity:'+(0.5+s/20)+'"></div>',iconSize:[sz,sz],iconAnchor:[sz/2,sz/2]}});
    var mk=L.marker([d[2],d[3]],{{icon:icon,zIndexOffset:Math.round(s*10)}});
    mk.bindTooltip(d[1],{{permanent:false,direction:'right',offset:[sz/2+2,0],className:'dest-label',opacity:1}});
    map.on('zoomend',function(){{if(map.getZoom()>=5){{mk.bindTooltip(d[1],{{permanent:true,direction:'right',offset:[sz/2+2,0],className:'dest-label',opacity:1}});}}else{{mk.unbindTooltip();}}}});
    mk.on('click',function(){{
      var bars=(d[8]||[]).map(function(ms,i){{var h=ms?Math.round(((ms[0]||0)/10)*100):0;var c=ms?scoreColor(ms[0]):'#333';return '<div class="pi-bar'+(i===CUR_M?' cur':'')+'\" style="height:'+h+'%;background:'+c+'"></div>';}}).join('');
      L.popup({{maxWidth:200}}).setLatLng([d[2],d[3]]).setContent('<div class="pi"><div class="pi-flag">'+flagEmoji(d[4])+'</div><div class="pi-name">'+d[1]+'</div><div class="pi-score" style="color:'+col+'">'+s.toFixed(1)+'<span style="font-size:13px;color:#5a6c7d">/10</span></div><div class="pi-month">'+(CUR_M===12?MF_ANNUAL:MF[CUR_M])+'</div><div class="pi-bars">'+bars+'</div><a href="{ap}en/best-time-to-visit-'+(d[0]||'')+'.html" class="pi-link">{'→'}</a></div>').openOn(map);
    }});
    mk.addTo(layer);
  }});
  document.getElementById('sc').textContent=cnt;
  document.getElementById('sb').textContent=best>0?best.toFixed(1):'—';
}}
render();
</script>
</body>
</html>'''

    return html

def main():
    print("Building map data...")
    map_data_js = build_map_data()

    # Sauvegarder map-data.js
    with open('map-data.js', 'w') as f:
        f.write(map_data_js)
    print(f"  map-data.js: {len(map_data_js)//1024}KB")

    # Extraire WORLD et CLABELS depuis map.html existant
    with open('map.html') as f:
        existing = f.read()
    world_json = existing.split('var WORLD=')[1].split(';\nL.geoJSON')[0]
    clabels_json = existing.split('var CLABELS=')[1].split(';\nCLABELS.forEach')[0]

    # Générer les 5 pages
    for lang in SUPPORTED_LANGS:
        print(f"  Generating {lang}...")
        cfg = LANG_CONFIG[lang]
        html = generate_map_page(lang, map_data_js, world_json, clabels_json)

        if cfg['subdir']:
            filepath = ROOT / cfg['subdir'] / cfg['filename']
        else:
            filepath = ROOT / cfg['filename']

        with open(filepath, 'w') as f:
            f.write(html)
        print(f"    ✅ {filepath} ({len(html)//1024}KB)")

    print("\n✅ Done")

if __name__ == '__main__':
    main()
