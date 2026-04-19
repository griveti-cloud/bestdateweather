#!/usr/bin/env python3
"""Generate the interactive world climate map in 5 languages."""

import json
import csv
from pathlib import Path
from scoring import compute_ski_score, profile_score
from generate_piliers import load_destinations, load_climate, load_country_info
from generate_classements import compute_nomad
from lib.common import profile_translations

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
                'n': [
                row.get('nom_fr') or row['nom_bare'],
                row.get('nom_en') or row['nom_bare'],
                row.get('nom_es') or row.get('nom_en') or row['nom_bare'],
                row.get('nom_de') or row.get('nom_en') or row['nom_bare'],
            ],
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
    en_url = None
    for l, cfg in LANG_CONFIG.items():
        base = 'https://bestdateweather.com'
        path = f"/{cfg['subdir']}/{cfg['filename']}" if cfg['subdir'] else f"/{cfg['filename']}"
        hl = 'fr' if l=='fr' else 'en-US' if l=='en-us' else 'en-GB' if l=='en' else l
        lines.append(f'<link rel="alternate" hreflang="{hl}" href="{base}{path}"/>')
        if l == 'en':
            en_url = f'{base}{path}'
    if en_url:
        lines.append(f'<link rel="alternate" hreflang="x-default" href="{en_url}"/>')
    return '\n'.join(lines)

def generate_map_page(lang, map_data_js, world_json, clabels_json, clabels_by_lang=None):
    loc = load_locale(lang)
    pil = loc['pilier']
    m   = loc['map']
    # CLABELS localisés
    if clabels_by_lang and lang in clabels_by_lang:
        clabels_lang_json = json.dumps(clabels_by_lang[lang], ensure_ascii=False, separators=(',',':'))
    else:
        clabels_lang_json = clabels_json
    leg = m.get('legend', {'excellent':'Excellent','great':'Great','good':'Good','fair':'Fair','poor':'Poor','avoid':'Avoid'})
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

    # Balanced / Cool / Warm / Humid labels — source: lib.common.profile_translations
    # La map utilise les clés courtes bal/cool/warm/hum côté JS (CUR_PROF='bal'…);
    # on mappe vers les clés longues balanced/cool/warm/humid de la source partagée.
    _pt = profile_translations(lang)
    pl = {
        'bal': _pt['balanced'], 'cool': _pt['cool'],
        'warm': _pt['warm'], 'hum': _pt['humid'],
    }
    pl_sub = {
        'bal': _pt['sub_balanced'], 'cool': _pt['sub_cool'],
        'warm': _pt['sub_warm'], 'hum': _pt['sub_humid'],
    }

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
        f'      <div class="dd-item{" on" if i==3 else ""}" onclick="event.stopPropagation();pickMonth({i})">{months_full[i]}</div>'
        for i in range(12)
    )
    month_items = f'      <div class="dd-item" onclick="event.stopPropagation();pickMonth(12)">{m["map_annual"]}</div>\n' + month_items

    # Safety items
    secu_items = f'      <div class="dd-item on" onclick="event.stopPropagation();pickRL(4)">{secu_all}</div>\n'
    for r in [1,2,3]:
        secu_items += f'      <div class="dd-item" onclick="event.stopPropagation();pickRL({r})">≤ {sl.get(str(r), str(r))}</div>\n'

    # Budget items
    budget_items = f'      <div class="dd-item on" onclick="event.stopPropagation();pickBI(5)">{budget_all}</div>\n'
    for b in [1,2,3,4]:
        budget_items += f'      <div class="dd-item" onclick="event.stopPropagation();pickBI({b})">≤ {bl.get(str(b), str(b))}</div>\n'

    # Min score items
    all_scores_lbl = m['map_all_scores']
    min_items = f'      <div class="dd-item on" onclick="event.stopPropagation();pickMin(0)">{all_scores_lbl}</div>\n'
    for s in [5,6,7,8,9]:
        min_items += f'      <div class="dd-item" onclick="event.stopPropagation();pickMin({s})">≥ {s}.0</div>\n'

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
.cta-btn{{display:inline-flex;align-items:center;padding:6px 14px;background:linear-gradient(135deg,#c99438,#e8b84b);border-radius:20px;font-size:12px;font-weight:700;color:#1a1f2e;text-decoration:none;white-space:nowrap;flex-shrink:0;transition:filter .15s}}
.cta-btn:hover{{filter:brightness(1.08)}}
.share-btn{{background:none;border:1.5px solid rgba(255,255,255,.18);border-radius:50%;width:32px;height:32px;display:inline-flex;align-items:center;justify-content:center;cursor:pointer;color:rgba(255,255,255,.6);flex-shrink:0;transition:all .15s;padding:0}}
.share-btn:hover{{border-color:rgba(255,255,255,.4);color:white;background:rgba(255,255,255,.08)}}
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
.dd-menu-profile{{min-width:240px;max-width:min(280px,calc(100vw - 24px))}}
.dd-item-profile{{display:flex;flex-direction:column;align-items:flex-start;gap:2px;white-space:normal;padding:8px 12px}}
.dd-item-profile .dd-lbl{{font-size:13px;font-weight:600;line-height:1.3;color:rgba(255,255,255,.85)}}
.dd-item-profile .dd-sub{{font-size:11px;font-weight:400;line-height:1.35;color:rgba(255,255,255,.5)}}
.dd-item-profile.on .dd-lbl{{color:#c9a84c;font-weight:700}}
.dd-item-profile.on .dd-sub{{color:rgba(201,168,76,.7)}}
.fsep{{width:1px;height:16px;background:rgba(255,255,255,.1);flex-shrink:0}}
#map{{position:fixed;top:88px;left:0;right:0;bottom:0}}
.leaflet-container{{background:#0d1117}}
.bdw-dot{{border-radius:50%;border:1.5px solid rgba(255,255,255,.2);cursor:pointer;transition:transform .1s}}
.bdw-dot:hover{{transform:scale(1.5)}}
.leaflet-popup-content-wrapper{{background:#1a1f2e;border:1px solid rgba(255,255,255,.12);border-radius:12px;box-shadow:0 8px 32px rgba(0,0,0,.6);padding:0;overflow:hidden}}
.leaflet-popup-tip{{background:#1a1f2e}}
.leaflet-popup-content{{margin:0;width:200px!important}}
.pi{{padding:14px}}
.pi-flag{{font-size:14px;color:rgba(255,255,255,.45);font-weight:600;letter-spacing:.5px}}
.pi-name{{font-size:15px;font-weight:700;margin:5px 0 2px;color:white}}
.pi-score{{font-size:26px;font-weight:700;line-height:1;margin:6px 0 2px}}
.pi-month{{font-size:11px;color:rgba(255,255,255,.55);margin-bottom:10px}}
.pi-bars{{display:flex;gap:1px;align-items:stretch;margin-bottom:8px}}
.pi-col{{flex:1;display:flex;flex-direction:column;align-items:center;gap:1px}}
.pi-bar-wrap{{height:28px;width:100%;display:flex;align-items:flex-end}}
.pi-bar{{width:100%;border-radius:2px 2px 0 0;min-height:2px}}
.pi-bar.cur{{outline:2px solid white;outline-offset:1px}}
.pi-link{{display:block;background:#c9a84c;color:#1a1f2e;text-align:center;padding:7px;font-size:12px;font-weight:700;text-decoration:none;border-radius:7px}}
.dest-label{{background:rgba(20,25,40,.85);border:1px solid rgba(255,255,255,.1);border-radius:4px;padding:2px 5px;font-size:10px;font-weight:600;color:rgba(255,255,255,.85);white-space:nowrap;pointer-events:none}}
.dest-label::before{{display:none}}
.clbl{{background:transparent!important;border:none!important;box-shadow:none!important;color:rgba(255,255,255,.4);font-size:10px;font-weight:600;text-transform:uppercase;letter-spacing:.5px;pointer-events:none}}
.legend{{position:fixed;bottom:16px;left:16px;z-index:900;background:rgba(20,25,40,.92);border:1px solid rgba(255,255,255,.08);border-radius:10px;padding:9px 12px;font-size:11px}}
.lt{{font-weight:600;color:#5a6c7d;text-transform:uppercase;letter-spacing:.4px;margin-bottom:6px}}
.lr{{display:flex;align-items:center;gap:7px;margin-bottom:3px;color:rgba(255,255,255,.6)}}
.ld{{width:9px;height:9px;border-radius:50%;border:1px solid rgba(255,255,255,.2)}}
.leaflet-control-attribution{{display:none!important}}
@media(max-width:500px){{
  .topbar-stats{{display:none}}
  .brand{{font-size:14px}}
  .fbar{{padding:5px 8px;gap:4px}}
  .dd-btn{{font-size:10px;padding:4px 7px;border-radius:12px}}
  .dd-arr{{display:none}}
  #map{{top:82px}}
  .legend{{display:none}}
}}
</style>
<script type="application/ld+json">{{
  "@context": "https://schema.org",
  "@type": "WebPage",
  "name": "{m['map_title']}",
  "description": "{m['map_desc']}",
  "url": "{canonical}",
  "inLanguage": "{lang}"
}}</script>
</head>
<body>
<h1 style="position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap">{m['map_title']}</h1>
<div class="topbar">
  <a href="/" class="brand">Best<em>Date</em>Weather</a>
  <div class="topbar-stats">{m['map_showing']} <b id="sc">—</b> {m['map_destinations']} · {m['map_best']} <b id="sb">—</b>/10</div>
  <div class="topbar-right">
    <div style="position:relative">
      {lang_selector_html}
    </div>
    <button class="share-btn" onclick="bdwShareMap()" title="Share">
        <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/></svg>
      </button>
    <a href="{hub_url}" class="cta-btn">{m['cta']}</a>
  </div>
</div>
<div class="fbar">
  <div class="dd" id="dd-m">
    <button class="dd-btn sel" id="dd-m-btn" onclick="event.stopPropagation();openDD('m')">{m['map_annual']} <span class="dd-arr">▾</span></button>
    <div class="dd-menu" id="dd-m-menu">
{month_items}
    </div>
  </div>
  <div class="fsep"></div>
  <div class="dd" id="dd-mode">
    <button class="dd-btn" id="dd-mode-btn" onclick="event.stopPropagation();openDD('mode')">{tab_gen} <span class="dd-arr">▾</span></button>
    <div class="dd-menu" id="dd-mode-menu">
      <div class="dd-item on" data-mode="gen" onclick="event.stopPropagation();pickMode(this.dataset.mode,this.dataset.label)" data-label="{tab_gen}">{tab_gen}</div>
      <div class="dd-item" data-mode="beach" onclick="event.stopPropagation();pickMode(this.dataset.mode,this.dataset.label)" data-label="{tab_beach}">{tab_beach}</div>
      <div class="dd-item" data-mode="ski" onclick="event.stopPropagation();pickMode(this.dataset.mode,this.dataset.label)" data-label="{tab_ski}">{tab_ski}</div>
      <div class="dd-item" data-mode="nomad" onclick="event.stopPropagation();pickMode(this.dataset.mode,this.dataset.label)" data-label="{tab_nomad}">{tab_nomad}</div>
    </div>
  </div>
  <div class="fsep"></div>
  <div class="dd" id="dd-prof">
    <button class="dd-btn" id="dd-prof-btn" onclick="event.stopPropagation();openDD('prof')">{pl['bal']} <span class="dd-arr">▾</span></button>
    <div class="dd-menu dd-menu-profile" id="dd-prof-menu">
      <div class="dd-item dd-item-profile on" data-prof="bal" onclick="event.stopPropagation();pickProf(this.dataset.prof,this.dataset.label)" data-label="{pl['bal']}"><span class="dd-lbl">{pl['bal']}</span><span class="dd-sub">{pl_sub['bal']}</span></div>
      <div class="dd-item dd-item-profile" data-prof="cool" onclick="event.stopPropagation();pickProf(this.dataset.prof,this.dataset.label)" data-label="{pl['cool']}"><span class="dd-lbl">{pl['cool']}</span><span class="dd-sub">{pl_sub['cool']}</span></div>
      <div class="dd-item dd-item-profile" data-prof="warm" onclick="event.stopPropagation();pickProf(this.dataset.prof,this.dataset.label)" data-label="{pl['warm']}"><span class="dd-lbl">{pl['warm']}</span><span class="dd-sub">{pl_sub['warm']}</span></div>
      <div class="dd-item dd-item-profile" data-prof="hum" onclick="event.stopPropagation();pickProf(this.dataset.prof,this.dataset.label)" data-label="{pl['hum']}"><span class="dd-lbl">{pl['hum']}</span><span class="dd-sub">{pl_sub['hum']}</span></div>
    </div>
  </div>
  <div class="fsep"></div>
  <div class="dd" id="dd-rl">
    <button class="dd-btn" id="dd-rl-btn" onclick="event.stopPropagation();openDD('rl')">{fp_secu} <span class="dd-arr">▾</span></button>
    <div class="dd-menu" id="dd-rl-menu">
{secu_items}    </div>
  </div>
  <div class="fsep"></div>
  <div class="dd" id="dd-bi">
    <button class="dd-btn" id="dd-bi-btn" onclick="event.stopPropagation();openDD('bi')">{fp_budget} <span class="dd-arr">▾</span></button>
    <div class="dd-menu" id="dd-bi-menu">
{budget_items}    </div>
  </div>
  <div class="fsep"></div>
  <div class="dd" id="dd-min">
    <button class="dd-btn" id="dd-min-btn" onclick="event.stopPropagation();openDD('min')">{m['map_min_score']} <span class="dd-arr">▾</span></button>
    <div class="dd-menu" id="dd-min-menu">
{min_items}    </div>
  </div>
</div>
<div id="map"></div>
<div class="legend">
  <div class="lt">Score</div>
  <div class="lr"><div class="ld" style="background:#1a7a4a"></div>8.6+ {leg['excellent']}</div>
  <div class="lr"><div class="ld" style="background:#2d9e60"></div>7.6–8.5 {leg['great']}</div>
  <div class="lr"><div class="ld" style="background:#84cc16"></div>6.3–7.5 {leg['good']}</div>
  <div class="lr"><div class="ld" style="background:#f59e0b"></div>5.0–6.2 {leg['fair']}</div>
  <div class="lr"><div class="ld" style="background:#f97316"></div>3.5–4.9 {leg['poor']}</div>
  <div class="lr"><div class="ld" style="background:#ef4444"></div>0–3.4 {leg['avoid']}</div>
</div>
<script src="{mapdata_src}"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js"></script>
<script>
var MN={json.dumps(months_short)};
var LANG_IDX={{'fr':0,'en':1,'en-us':1,'es':2,'de':3}}[{json.dumps(lang)}]||1;
var MF={json.dumps(months_full)};
var MS={json.dumps(months_short)};
var MF_ANNUAL={json.dumps(m['map_annual'])};
var FP_SECU={json.dumps(fp_secu)};
var FP_BUDGET={json.dumps(fp_budget)};
var SECU_LABELS={secu_labels_js};
var BUDGET_LABELS={budget_labels_js};
var CUR_M=12; // Annual par défaut
var CUR_MODE='gen',CUR_PROF='bal',CUR_RL=4,CUR_BI=5,CUR_MIN=0;

document.getElementById('dd-m-btn').innerHTML=MF_ANNUAL+' <span class="dd-arr">▾</span>';document.getElementById('dd-m-btn').classList.add('sel');
document.querySelectorAll('#dd-m-menu .dd-item').forEach(function(el,i){{el.classList.toggle('on',i===CUR_M+1);}});

function getName(d){{return Array.isArray(d[1])?d[1][LANG_IDX]||d[1][1]:d[1];}}
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

function bdwShareMap(){{
  var url=window.location.href;
  var title=document.title||'BestDateWeather';
  if(navigator.share){{navigator.share({{title:title,url:url}}).catch(function(){{}});}}
  else if(navigator.clipboard){{navigator.clipboard.writeText(url).then(function(){{
    var btn=document.querySelector('.share-btn');
    if(btn){{var old=btn.innerHTML;btn.innerHTML='<svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="#c9a84c" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>';setTimeout(function(){{btn.innerHTML=old;}},1500);}}
  }}).catch(function(){{}});}}
  else{{window.open('https://wa.me/?text='+encodeURIComponent(url),'_blank');}}
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
var _openMenuId=null;
function openDD(id){{
  if(_openMenuId===id){{closeDD();return;}}
  closeDD();
  _openMenuId=id;
  var btn=document.getElementById('dd-'+id+'-btn');
  var menu=document.getElementById('dd-'+id+'-menu');
  if(!btn||!menu)return;
  btn.classList.add('_dd-open');
  var r=btn.getBoundingClientRect();
  var left=Math.max(4,Math.min(r.left,window.innerWidth-164));
  menu.style.cssText='display:block!important;position:fixed!important;top:'+(r.bottom+4)+'px;left:'+left+'px;z-index:99999;min-width:150px;max-height:280px;overflow-y:auto;background:#1e2640;border:1px solid rgba(255,255,255,.12);border-radius:10px;box-shadow:0 8px 24px rgba(0,0,0,.6);padding:4px;';
}}
function closeDD(){{
  if(_openMenuId){{
    var btn=document.getElementById('dd-'+_openMenuId+'-btn');
    var menu=document.getElementById('dd-'+_openMenuId+'-menu');
    if(btn)btn.classList.remove('_dd-open');
    if(menu)menu.style.cssText='display:none';
    _openMenuId=null;
  }}
}}
document.addEventListener('click',function(e){{
  if(_openMenuId&&!e.target.closest('#dd-'+_openMenuId+'-menu')&&!e.target.closest('#dd-'+_openMenuId+'-btn'))closeDD();
}});
// Déplacer tous les menus dans body pour échapper au overflow:auto du fbar
document.addEventListener('DOMContentLoaded',function(){{
  document.querySelectorAll('.dd-menu').forEach(function(m){{document.body.appendChild(m);}});
}});
function setBtn(id,label,active){{var btn=document.getElementById('dd-'+id+'-btn');if(btn){{btn.innerHTML=label+' <span class="dd-arr">▾</span>';btn.classList.toggle('sel',active);}}}}

function pickMonth(mi){{CUR_M=mi;setBtn('m',mi===12?MF_ANNUAL:MN[mi],true);document.querySelectorAll('#dd-m-menu .dd-item').forEach(function(el,i){{el.classList.toggle('on',i===(mi===12?0:mi+1));}});if(CUR_MODE==='nomad'){{CUR_MODE='gen';setBtn('mode','{tab_gen}',false);}}closeDD();render();}}
function pickMode(mode,label){{
  CUR_MODE=mode;setBtn('mode',label,mode!=='gen');
  if(mode==='nomad'){{CUR_M=12;setBtn('m',MF_ANNUAL,true);document.querySelectorAll('#dd-m-menu .dd-item').forEach(function(el,i){{el.classList.toggle('on',i===0);}});}}
  document.querySelectorAll('#dd-mode-menu .dd-item').forEach(function(el){{el.classList.toggle('on',el.textContent.trim()===label);}});
  var isNomad=mode==='nomad';
  var isSki=mode==='ski';
  // Nomad : score annuel par construction → masquer sélecteur mois
  var mEl=document.getElementById('dd-m');
  if(mEl){{mEl.style.display=isNomad?'none':'';mEl.style.pointerEvents=isNomad?'none':'';}}
  // Nomad : masquer Safety, Budget, MinScore (non pertinents pour score nomade)
  ['dd-rl','dd-bi','dd-min'].forEach(function(id){{var el=document.getElementById(id);if(el){{el.style.display=isNomad?'none':'';el.style.pointerEvents=isNomad?'none':'';}}}} );
  // Ski + Nomad : masquer Profil (incompatible avec scores spécialisés)
  var profEl=document.getElementById('dd-prof');
  if(profEl){{profEl.style.display=(isNomad||isSki)?'none':'';profEl.style.pointerEvents=(isNomad||isSki)?'none':'';}}
  // Séparateurs : en nomad aucun (seul dd-mode visible) ; en ski seul le 1er (entre dd-m et dd-mode) ; sinon tous
  document.querySelectorAll('.fbar .fsep').forEach(function(el,i){{
    if(isNomad) el.style.display='none';
    else if(isSki) el.style.display=(i===0)?'':'none';
    else el.style.display='';
  }} );
  closeDD();render();
}}
function pickProf(prof,label){{CUR_PROF=prof;setBtn('prof',label,prof!=='bal');document.querySelectorAll('#dd-prof-menu .dd-item').forEach(function(el){{el.classList.toggle('on',el.dataset.prof===prof);}});closeDD();render();}}
function pickRL(rl){{CUR_RL=rl;var lbl=SECU_LABELS[String(rl)];var active=rl<4;setBtn('rl',active?'🛡 ≤ '+lbl:FP_SECU,active);document.querySelectorAll('#dd-rl-menu .dd-item').forEach(function(el,i){{el.classList.toggle('on',i===(rl===4?0:rl===1?1:rl===2?2:3));}});closeDD();render();}}
function pickBI(bi){{CUR_BI=bi;var lbl=BUDGET_LABELS[String(bi)];var active=bi<5;setBtn('bi',active?'≤ '+lbl:FP_BUDGET,active);document.querySelectorAll('#dd-bi-menu .dd-item').forEach(function(el,i){{el.classList.toggle('on',i===(bi===5?0:bi===1?1:bi===2?2:bi===3?3:4));}});closeDD();render();}}
function pickMin(min){{CUR_MIN=min;setBtn('min',min>0?('≥ '+min.toFixed(1)):'{m['map_min_score']}',min>0);document.querySelectorAll('#dd-min-menu .dd-item').forEach(function(el,i){{el.classList.toggle('on',i===(min===0?0:min-4));}});closeDD();render();}}

// Map
var map=L.map('map',{{center:[20,10],zoom:2,minZoom:2,maxZoom:12,zoomControl:true,attributionControl:false}});
// Attribution hidden
L.tileLayer('https://{{s}}.basemaps.cartocdn.com/dark_nolabels/{{z}}/{{x}}/{{y}}{{r}}.png',{{maxZoom:19,subdomains:'abcd'}}).addTo(map);
var WORLD={world_json};
L.geoJSON(WORLD,{{style:{{fillColor:'#1e2640',fillOpacity:0.7,color:'#3a4a6a',weight:0.5}}}}).addTo(map);
var CLABELS={clabels_lang_json};
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
    mk.bindTooltip(getName(d),{{permanent:false,direction:'right',offset:[sz/2+2,0],className:'dest-label',opacity:1}});
    map.on('zoomend',function(){{if(map.getZoom()>=5){{mk.bindTooltip(getName(d),{{permanent:true,direction:'right',offset:[sz/2+2,0],className:'dest-label',opacity:1}});}}else{{mk.unbindTooltip();}}}});
    mk.on('click',function(){{
      var bars=(d[8]||[]).map(function(ms,i){{var h=ms?Math.round(((ms[0]||0)/10)*100):0;var c=ms?scoreColor(ms[0]):'#333';var lbl=MS[i]?MS[i][0]:'';return '<div class="pi-col"><div class="pi-bar-wrap"><div class="pi-bar'+(i===CUR_M?' cur':'')+'\" style="height:'+h+'%;background:'+c+'"></div></div><span style="font-size:6px;color:#64748b;line-height:1">'+lbl+'</span></div>';}}).join('');
      L.popup({{maxWidth:200}}).setLatLng([d[2],d[3]]).setContent('<div class="pi"><div class="pi-flag">'+flagEmoji(d[4])+'</div><div class="pi-name">'+getName(d)+'</div><div class="pi-score" style="color:'+col+'">'+s.toFixed(1)+'<span style="font-size:13px;color:#5a6c7d">/10</span></div><div class="pi-month">'+(CUR_M===12?MF_ANNUAL:MF[CUR_M])+'</div><div class="pi-bars">'+bars+'</div><a href="{ap}en/best-time-to-visit-'+(d[0]||'')+'.html" class="pi-link">{m['cta']}</a></div>').openOn(map);
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
    clabels_by_lang = {"fr":[{"n":"Fidji","lat":-18.0,"lon":178.0,"l":0},{"n":"Tanzanie","lat":-6.5,"lon":34.3,"l":1},{"n":"Sahara occidental","lat":24.8,"lon":-12.0,"l":2},{"n":"Canada","lat":56.0,"lon":-96.0,"l":0},{"n":"États-Unis","lat":39.5,"lon":-98.0,"l":0},{"n":"Kazakhstan","lat":48.0,"lon":66.0,"l":0},{"n":"Ouzbékistan","lat":41.2,"lon":65.3,"l":1},{"n":"Papouasie-Nouvelle-Guinée","lat":-7.8,"lon":146.2,"l":1},{"n":"Indonésie","lat":-2.0,"lon":118.0,"l":0},{"n":"Argentine","lat":-36.0,"lon":-65.0,"l":0},{"n":"Chili","lat":-38.1,"lon":-71.4,"l":1},{"n":"République démocratique du Congo","lat":-3.0,"lon":24.0,"l":1},{"n":"Somalie","lat":6.6,"lon":46.9,"l":1},{"n":"Kenya","lat":1.1,"lon":37.8,"l":2},{"n":"Soudan","lat":15.0,"lon":29.0,"l":1},{"n":"Tchad","lat":15.0,"lon":18.0,"l":1},{"n":"Haïti","lat":18.8,"lon":-72.7,"l":2},{"n":"République dominicaine","lat":18.7,"lon":-70.5,"l":2},{"n":"Russie","lat":61.0,"lon":90.0,"l":0},{"n":"Bahamas","lat":24.5,"lon":-77.9,"l":2},{"n":"îles Malouines","lat":-51.7,"lon":-59.6,"l":2},{"n":"Norvège","lat":65.0,"lon":14.0,"l":0},{"n":"Groenland","lat":72.0,"lon":-40.0,"l":0},{"n":"Terres australes et antarctiques françaises","lat":-49.1,"lon":69.5,"l":2},{"n":"Timor oriental","lat":-8.7,"lon":125.9,"l":2},{"n":"Afrique du Sud","lat":-28.6,"lon":24.7,"l":1},{"n":"Lesotho","lat":-29.6,"lon":28.4,"l":2},{"n":"Mexique","lat":23.5,"lon":-102.0,"l":0},{"n":"Uruguay","lat":-32.7,"lon":-56.1,"l":2},{"n":"Brésil","lat":-10.0,"lon":-53.0,"l":0},{"n":"Bolivie","lat":-16.3,"lon":-64.1,"l":1},{"n":"Pérou","lat":-7.8,"lon":-74.1,"l":1},{"n":"Colombie","lat":4.5,"lon":-72.7,"l":1},{"n":"Panama","lat":8.5,"lon":-80.3,"l":2},{"n":"Costa Rica","lat":9.8,"lon":-84.2,"l":2},{"n":"Nicaragua","lat":13.1,"lon":-85.0,"l":2},{"n":"Honduras","lat":14.7,"lon":-86.3,"l":2},{"n":"Salvador","lat":13.9,"lon":-88.9,"l":2},{"n":"Guatemala","lat":15.5,"lon":-90.3,"l":2},{"n":"Belize","lat":17.4,"lon":-88.6,"l":2},{"n":"Venezuela","lat":7.2,"lon":-66.9,"l":1},{"n":"Guyana","lat":4.5,"lon":-58.9,"l":2},{"n":"Suriname","lat":3.7,"lon":-55.9,"l":2},{"n":"France","lat":46.5,"lon":2.5,"l":0},{"n":"Équateur","lat":-1.6,"lon":-78.7,"l":2},{"n":"Porto Rico","lat":18.3,"lon":-66.4,"l":2},{"n":"Jamaïque","lat":18.2,"lon":-77.3,"l":2},{"n":"Cuba","lat":21.7,"lon":-79.7,"l":2},{"n":"Zimbabwe","lat":-18.9,"lon":29.7,"l":2},{"n":"Botswana","lat":-22.5,"lon":24.5,"l":2},{"n":"Namibie","lat":-21.6,"lon":17.9,"l":1},{"n":"Sénégal","lat":13.9,"lon":-14.6,"l":2},{"n":"Mali","lat":17.0,"lon":-2.0,"l":1},{"n":"Mauritanie","lat":18.8,"lon":-12.4,"l":1},{"n":"Bénin","lat":9.8,"lon":2.3,"l":2},{"n":"Niger","lat":17.0,"lon":8.5,"l":1},{"n":"Nigeria","lat":9.7,"lon":8.3,"l":1},{"n":"Cameroun","lat":6.9,"lon":13.2,"l":2},{"n":"Togo","lat":8.9,"lon":0.9,"l":2},{"n":"Ghana","lat":8.3,"lon":-1.0,"l":2},{"n":"Côte d'Ivoire","lat":7.9,"lon":-6.3,"l":2},{"n":"Guinée","lat":10.4,"lon":-11.0,"l":2},{"n":"Guinée-Bissau","lat":12.0,"lon":-15.2,"l":2},{"n":"Liberia","lat":6.8,"lon":-9.1,"l":2},{"n":"Sierra Leone","lat":8.6,"lon":-11.7,"l":2},{"n":"Burkina Faso","lat":12.1,"lon":-1.9,"l":2},{"n":"République centrafricaine","lat":6.3,"lon":20.7,"l":1},{"n":"République du Congo","lat":-0.9,"lon":14.9,"l":2},{"n":"Gabon","lat":-0.3,"lon":11.9,"l":2},{"n":"Guinée équatoriale","lat":1.6,"lon":10.1,"l":2},{"n":"Zambie","lat":-12.8,"lon":28.0,"l":1},{"n":"Malawi","lat":-12.9,"lon":34.1,"l":2},{"n":"Mozambique","lat":-17.7,"lon":35.0,"l":1},{"n":"Eswatini","lat":-26.4,"lon":31.4,"l":2},{"n":"Angola","lat":-12.0,"lon":18.0,"l":1},{"n":"Burundi","lat":-3.2,"lon":30.0,"l":2},{"n":"Israël","lat":32.0,"lon":35.1,"l":2},{"n":"Liban","lat":33.8,"lon":35.9,"l":2},{"n":"Madagascar","lat":-18.0,"lon":47.0,"l":2},{"n":"Palestine","lat":31.8,"lon":35.2,"l":2},{"n":"Gambie","lat":13.5,"lon":-15.3,"l":2},{"n":"Tunisie","lat":34.0,"lon":9.8,"l":2},{"n":"Algérie","lat":28.0,"lon":2.5,"l":1},{"n":"Jordanie","lat":31.1,"lon":36.7,"l":2},{"n":"Émirats arabes unis","lat":24.2,"lon":54.2,"l":2},{"n":"Qatar","lat":25.3,"lon":51.2,"l":2},{"n":"Koweït","lat":29.3,"lon":47.7,"l":2},{"n":"Irak","lat":33.4,"lon":44.4,"l":2},{"n":"Oman","lat":20.9,"lon":56.6,"l":2},{"n":"Vanuatu","lat":-15.4,"lon":166.9,"l":2},{"n":"Cambodge","lat":12.6,"lon":104.9,"l":2},{"n":"Thaïlande","lat":13.2,"lon":100.7,"l":1},{"n":"Laos","lat":18.3,"lon":103.7,"l":2},{"n":"Birmanie","lat":20.0,"lon":97.2,"l":1},{"n":"Viêt Nam","lat":16.7,"lon":105.9,"l":1},{"n":"Corée du Nord","lat":39.9,"lon":127.4,"l":2},{"n":"Corée du Sud","lat":36.7,"lon":127.5,"l":2},{"n":"Mongolie","lat":47.2,"lon":104.6,"l":1},{"n":"Inde","lat":22.0,"lon":80.0,"l":0},{"n":"Bangladesh","lat":23.4,"lon":90.6,"l":2},{"n":"Bhoutan","lat":27.5,"lon":90.6,"l":2},{"n":"Népal","lat":28.2,"lon":84.6,"l":2},{"n":"Pakistan","lat":30.8,"lon":69.4,"l":1},{"n":"Afghanistan","lat":34.8,"lon":67.8,"l":1},{"n":"Tadjikistan","lat":38.5,"lon":70.8,"l":2},{"n":"Kirghizistan","lat":41.4,"lon":74.0,"l":2},{"n":"Turkménistan","lat":39.3,"lon":58.5,"l":1},{"n":"Iran","lat":33.4,"lon":53.2,"l":1},{"n":"Syrie","lat":35.1,"lon":38.0,"l":2},{"n":"Arménie","lat":39.9,"lon":45.3,"l":2},{"n":"Suède","lat":62.7,"lon":16.6,"l":1},{"n":"Biélorussie","lat":53.3,"lon":28.3,"l":2},{"n":"Ukraine","lat":48.7,"lon":30.5,"l":1},{"n":"Pologne","lat":51.7,"lon":19.5,"l":2},{"n":"Autriche","lat":47.6,"lon":13.5,"l":2},{"n":"Hongrie","lat":47.4,"lon":19.2,"l":2},{"n":"Moldavie","lat":47.0,"lon":28.5,"l":2},{"n":"Roumanie","lat":45.9,"lon":25.2,"l":2},{"n":"Lituanie","lat":55.2,"lon":24.0,"l":2},{"n":"Lettonie","lat":56.9,"lon":24.9,"l":2},{"n":"Estonie","lat":58.7,"lon":26.1,"l":2},{"n":"Allemagne","lat":51.0,"lon":10.7,"l":2},{"n":"Bulgarie","lat":42.9,"lon":24.7,"l":2},{"n":"Grèce","lat":39.8,"lon":23.1,"l":2},{"n":"Turquie","lat":38.4,"lon":36.9,"l":1},{"n":"Albanie","lat":41.3,"lon":20.1,"l":2},{"n":"Croatie","lat":44.8,"lon":16.4,"l":2},{"n":"Suisse","lat":46.8,"lon":8.3,"l":2},{"n":"Luxembourg","lat":49.8,"lon":6.0,"l":2},{"n":"Belgique","lat":50.7,"lon":4.4,"l":2},{"n":"Pays-Bas","lat":52.1,"lon":5.5,"l":2},{"n":"Portugal","lat":39.8,"lon":-8.0,"l":2},{"n":"Espagne","lat":40.2,"lon":-4.5,"l":2},{"n":"Irlande","lat":53.5,"lon":-7.7,"l":2},{"n":"Nouvelle-Calédonie","lat":-21.2,"lon":165.5,"l":2},{"n":"Îles Salomon","lat":-7.9,"lon":159.1,"l":2},{"n":"Nouvelle-Zélande","lat":-38.2,"lon":175.5,"l":1},{"n":"Australie","lat":-25.0,"lon":134.0,"l":0},{"n":"Sri Lanka","lat":7.6,"lon":80.9,"l":2},{"n":"République populaire de Chine","lat":35.0,"lon":104.0,"l":0},{"n":"Taïwan","lat":23.9,"lon":121.1,"l":2},{"n":"Italie","lat":43.1,"lon":12.6,"l":1},{"n":"Danemark","lat":56.3,"lon":9.6,"l":2},{"n":"Royaume-Uni","lat":53.9,"lon":-3.1,"l":2},{"n":"Islande","lat":65.3,"lon":-19.3,"l":2},{"n":"Azerbaïdjan","lat":40.4,"lon":47.4,"l":2},{"n":"Géorgie","lat":42.3,"lon":43.4,"l":2},{"n":"Philippines","lat":15.4,"lon":121.8,"l":1},{"n":"Malaisie","lat":3.7,"lon":114.8,"l":1},{"n":"Brunei","lat":4.7,"lon":115.0,"l":2},{"n":"Slovénie","lat":46.1,"lon":15.0,"l":2},{"n":"Finlande","lat":65.2,"lon":25.9,"l":1},{"n":"Slovaquie","lat":48.8,"lon":19.4,"l":2},{"n":"Tchéquie","lat":49.8,"lon":15.8,"l":2},{"n":"Érythrée","lat":14.7,"lon":39.6,"l":2},{"n":"Japon","lat":35.7,"lon":136.0,"l":1},{"n":"Paraguay","lat":-23.3,"lon":-57.6,"l":2},{"n":"Yémen","lat":15.5,"lon":46.5,"l":2},{"n":"Arabie saoudite","lat":24.0,"lon":44.0,"l":1},{"n":"Antarctique","lat":-73.0,"lon":-2.7,"l":0},{"n":"Chypre du Nord","lat":35.2,"lon":33.4,"l":2},{"n":"Chypre","lat":35.0,"lon":33.2,"l":2},{"n":"Maroc","lat":28.8,"lon":-9.4,"l":1},{"n":"Égypte","lat":28.2,"lon":31.7,"l":1},{"n":"Libye","lat":28.5,"lon":16.6,"l":1},{"n":"Éthiopie","lat":9.0,"lon":39.2,"l":1},{"n":"Djibouti","lat":11.8,"lon":42.5,"l":2},{"n":"Somaliland","lat":10.5,"lon":46.4,"l":2},{"n":"Ouganda","lat":1.3,"lon":32.0,"l":2},{"n":"Rwanda","lat":-2.0,"lon":29.9,"l":2},{"n":"Bosnie-Herzégovine","lat":44.2,"lon":17.9,"l":2},{"n":"Macédoine du Nord","lat":41.7,"lon":21.6,"l":2},{"n":"Serbie","lat":43.9,"lon":20.9,"l":2},{"n":"Monténégro","lat":42.7,"lon":19.4,"l":2},{"n":"Kosovo","lat":42.5,"lon":21.0,"l":2},{"n":"Trinité-et-Tobago","lat":10.5,"lon":-61.5,"l":2},{"n":"Soudan du Sud","lat":8.0,"lon":30.1,"l":2}],"en":[{"n":"Fiji","lat":-18.0,"lon":178.0,"l":0},{"n":"Tanzania","lat":-6.5,"lon":34.3,"l":1},{"n":"Western Sahara","lat":24.8,"lon":-12.0,"l":2},{"n":"Canada","lat":56.0,"lon":-96.0,"l":0},{"n":"United States of America","lat":39.5,"lon":-98.0,"l":0},{"n":"Kazakhstan","lat":48.0,"lon":66.0,"l":0},{"n":"Uzbekistan","lat":41.2,"lon":65.3,"l":1},{"n":"Papua New Guinea","lat":-7.8,"lon":146.2,"l":1},{"n":"Indonesia","lat":-2.0,"lon":118.0,"l":0},{"n":"Argentina","lat":-36.0,"lon":-65.0,"l":0},{"n":"Chile","lat":-38.1,"lon":-71.4,"l":1},{"n":"Democratic Republic of the Congo","lat":-3.0,"lon":24.0,"l":1},{"n":"Somalia","lat":6.6,"lon":46.9,"l":1},{"n":"Kenya","lat":1.1,"lon":37.8,"l":2},{"n":"Sudan","lat":15.0,"lon":29.0,"l":1},{"n":"Chad","lat":15.0,"lon":18.0,"l":1},{"n":"Haiti","lat":18.8,"lon":-72.7,"l":2},{"n":"Dominican Republic","lat":18.7,"lon":-70.5,"l":2},{"n":"Russia","lat":61.0,"lon":90.0,"l":0},{"n":"The Bahamas","lat":24.5,"lon":-77.9,"l":2},{"n":"Falkland Islands","lat":-51.7,"lon":-59.6,"l":2},{"n":"Norway","lat":65.0,"lon":14.0,"l":0},{"n":"Greenland","lat":72.0,"lon":-40.0,"l":0},{"n":"French Southern and Antarctic Lands","lat":-49.1,"lon":69.5,"l":2},{"n":"East Timor","lat":-8.7,"lon":125.9,"l":2},{"n":"South Africa","lat":-28.6,"lon":24.7,"l":1},{"n":"Lesotho","lat":-29.6,"lon":28.4,"l":2},{"n":"Mexico","lat":23.5,"lon":-102.0,"l":0},{"n":"Uruguay","lat":-32.7,"lon":-56.1,"l":2},{"n":"Brazil","lat":-10.0,"lon":-53.0,"l":0},{"n":"Bolivia","lat":-16.3,"lon":-64.1,"l":1},{"n":"Peru","lat":-7.8,"lon":-74.1,"l":1},{"n":"Colombia","lat":4.5,"lon":-72.7,"l":1},{"n":"Panama","lat":8.5,"lon":-80.3,"l":2},{"n":"Costa Rica","lat":9.8,"lon":-84.2,"l":2},{"n":"Nicaragua","lat":13.1,"lon":-85.0,"l":2},{"n":"Honduras","lat":14.7,"lon":-86.3,"l":2},{"n":"El Salvador","lat":13.9,"lon":-88.9,"l":2},{"n":"Guatemala","lat":15.5,"lon":-90.3,"l":2},{"n":"Belize","lat":17.4,"lon":-88.6,"l":2},{"n":"Venezuela","lat":7.2,"lon":-66.9,"l":1},{"n":"Guyana","lat":4.5,"lon":-58.9,"l":2},{"n":"Suriname","lat":3.7,"lon":-55.9,"l":2},{"n":"France","lat":46.5,"lon":2.5,"l":0},{"n":"Ecuador","lat":-1.6,"lon":-78.7,"l":2},{"n":"Puerto Rico","lat":18.3,"lon":-66.4,"l":2},{"n":"Jamaica","lat":18.2,"lon":-77.3,"l":2},{"n":"Cuba","lat":21.7,"lon":-79.7,"l":2},{"n":"Zimbabwe","lat":-18.9,"lon":29.7,"l":2},{"n":"Botswana","lat":-22.5,"lon":24.5,"l":2},{"n":"Namibia","lat":-21.6,"lon":17.9,"l":1},{"n":"Senegal","lat":13.9,"lon":-14.6,"l":2},{"n":"Mali","lat":17.0,"lon":-2.0,"l":1},{"n":"Mauritania","lat":18.8,"lon":-12.4,"l":1},{"n":"Benin","lat":9.8,"lon":2.3,"l":2},{"n":"Niger","lat":17.0,"lon":8.5,"l":1},{"n":"Nigeria","lat":9.7,"lon":8.3,"l":1},{"n":"Cameroon","lat":6.9,"lon":13.2,"l":2},{"n":"Togo","lat":8.9,"lon":0.9,"l":2},{"n":"Ghana","lat":8.3,"lon":-1.0,"l":2},{"n":"Ivory Coast","lat":7.9,"lon":-6.3,"l":2},{"n":"Guinea","lat":10.4,"lon":-11.0,"l":2},{"n":"Guinea-Bissau","lat":12.0,"lon":-15.2,"l":2},{"n":"Liberia","lat":6.8,"lon":-9.1,"l":2},{"n":"Sierra Leone","lat":8.6,"lon":-11.7,"l":2},{"n":"Burkina Faso","lat":12.1,"lon":-1.9,"l":2},{"n":"Central African Republic","lat":6.3,"lon":20.7,"l":1},{"n":"Republic of the Congo","lat":-0.9,"lon":14.9,"l":2},{"n":"Gabon","lat":-0.3,"lon":11.9,"l":2},{"n":"Equatorial Guinea","lat":1.6,"lon":10.1,"l":2},{"n":"Zambia","lat":-12.8,"lon":28.0,"l":1},{"n":"Malawi","lat":-12.9,"lon":34.1,"l":2},{"n":"Mozambique","lat":-17.7,"lon":35.0,"l":1},{"n":"Eswatini","lat":-26.4,"lon":31.4,"l":2},{"n":"Angola","lat":-12.0,"lon":18.0,"l":1},{"n":"Burundi","lat":-3.2,"lon":30.0,"l":2},{"n":"Israel","lat":32.0,"lon":35.1,"l":2},{"n":"Lebanon","lat":33.8,"lon":35.9,"l":2},{"n":"Madagascar","lat":-18.0,"lon":47.0,"l":2},{"n":"Palestine","lat":31.8,"lon":35.2,"l":2},{"n":"The Gambia","lat":13.5,"lon":-15.3,"l":2},{"n":"Tunisia","lat":34.0,"lon":9.8,"l":2},{"n":"Algeria","lat":28.0,"lon":2.5,"l":1},{"n":"Jordan","lat":31.1,"lon":36.7,"l":2},{"n":"United Arab Emirates","lat":24.2,"lon":54.2,"l":2},{"n":"Qatar","lat":25.3,"lon":51.2,"l":2},{"n":"Kuwait","lat":29.3,"lon":47.7,"l":2},{"n":"Iraq","lat":33.4,"lon":44.4,"l":2},{"n":"Oman","lat":20.9,"lon":56.6,"l":2},{"n":"Vanuatu","lat":-15.4,"lon":166.9,"l":2},{"n":"Cambodia","lat":12.6,"lon":104.9,"l":2},{"n":"Thailand","lat":13.2,"lon":100.7,"l":1},{"n":"Laos","lat":18.3,"lon":103.7,"l":2},{"n":"Myanmar","lat":20.0,"lon":97.2,"l":1},{"n":"Vietnam","lat":16.7,"lon":105.9,"l":1},{"n":"North Korea","lat":39.9,"lon":127.4,"l":2},{"n":"South Korea","lat":36.7,"lon":127.5,"l":2},{"n":"Mongolia","lat":47.2,"lon":104.6,"l":1},{"n":"India","lat":22.0,"lon":80.0,"l":0},{"n":"Bangladesh","lat":23.4,"lon":90.6,"l":2},{"n":"Bhutan","lat":27.5,"lon":90.6,"l":2},{"n":"Nepal","lat":28.2,"lon":84.6,"l":2},{"n":"Pakistan","lat":30.8,"lon":69.4,"l":1},{"n":"Afghanistan","lat":34.8,"lon":67.8,"l":1},{"n":"Tajikistan","lat":38.5,"lon":70.8,"l":2},{"n":"Kyrgyzstan","lat":41.4,"lon":74.0,"l":2},{"n":"Turkmenistan","lat":39.3,"lon":58.5,"l":1},{"n":"Iran","lat":33.4,"lon":53.2,"l":1},{"n":"Syria","lat":35.1,"lon":38.0,"l":2},{"n":"Armenia","lat":39.9,"lon":45.3,"l":2},{"n":"Sweden","lat":62.7,"lon":16.6,"l":1},{"n":"Belarus","lat":53.3,"lon":28.3,"l":2},{"n":"Ukraine","lat":48.7,"lon":30.5,"l":1},{"n":"Poland","lat":51.7,"lon":19.5,"l":2},{"n":"Austria","lat":47.6,"lon":13.5,"l":2},{"n":"Hungary","lat":47.4,"lon":19.2,"l":2},{"n":"Moldova","lat":47.0,"lon":28.5,"l":2},{"n":"Romania","lat":45.9,"lon":25.2,"l":2},{"n":"Lithuania","lat":55.2,"lon":24.0,"l":2},{"n":"Latvia","lat":56.9,"lon":24.9,"l":2},{"n":"Estonia","lat":58.7,"lon":26.1,"l":2},{"n":"Germany","lat":51.0,"lon":10.7,"l":2},{"n":"Bulgaria","lat":42.9,"lon":24.7,"l":2},{"n":"Greece","lat":39.8,"lon":23.1,"l":2},{"n":"Turkey","lat":38.4,"lon":36.9,"l":1},{"n":"Albania","lat":41.3,"lon":20.1,"l":2},{"n":"Croatia","lat":44.8,"lon":16.4,"l":2},{"n":"Switzerland","lat":46.8,"lon":8.3,"l":2},{"n":"Luxembourg","lat":49.8,"lon":6.0,"l":2},{"n":"Belgium","lat":50.7,"lon":4.4,"l":2},{"n":"Netherlands","lat":52.1,"lon":5.5,"l":2},{"n":"Portugal","lat":39.8,"lon":-8.0,"l":2},{"n":"Spain","lat":40.2,"lon":-4.5,"l":2},{"n":"Ireland","lat":53.5,"lon":-7.7,"l":2},{"n":"New Caledonia","lat":-21.2,"lon":165.5,"l":2},{"n":"Solomon Islands","lat":-7.9,"lon":159.1,"l":2},{"n":"New Zealand","lat":-38.2,"lon":175.5,"l":1},{"n":"Australia","lat":-25.0,"lon":134.0,"l":0},{"n":"Sri Lanka","lat":7.6,"lon":80.9,"l":2},{"n":"People's Republic of China","lat":35.0,"lon":104.0,"l":0},{"n":"Taiwan","lat":23.9,"lon":121.1,"l":2},{"n":"Italy","lat":43.1,"lon":12.6,"l":1},{"n":"Denmark","lat":56.3,"lon":9.6,"l":2},{"n":"United Kingdom","lat":53.9,"lon":-3.1,"l":2},{"n":"Iceland","lat":65.3,"lon":-19.3,"l":2},{"n":"Azerbaijan","lat":40.4,"lon":47.4,"l":2},{"n":"Georgia","lat":42.3,"lon":43.4,"l":2},{"n":"Philippines","lat":15.4,"lon":121.8,"l":1},{"n":"Malaysia","lat":3.7,"lon":114.8,"l":1},{"n":"Brunei","lat":4.7,"lon":115.0,"l":2},{"n":"Slovenia","lat":46.1,"lon":15.0,"l":2},{"n":"Finland","lat":65.2,"lon":25.9,"l":1},{"n":"Slovakia","lat":48.8,"lon":19.4,"l":2},{"n":"Czech Republic","lat":49.8,"lon":15.8,"l":2},{"n":"Eritrea","lat":14.7,"lon":39.6,"l":2},{"n":"Japan","lat":35.7,"lon":136.0,"l":1},{"n":"Paraguay","lat":-23.3,"lon":-57.6,"l":2},{"n":"Yemen","lat":15.5,"lon":46.5,"l":2},{"n":"Saudi Arabia","lat":24.0,"lon":44.0,"l":1},{"n":"Antarctica","lat":-73.0,"lon":-2.7,"l":0},{"n":"Turkish Republic of Northern Cyprus","lat":35.2,"lon":33.4,"l":2},{"n":"Cyprus","lat":35.0,"lon":33.2,"l":2},{"n":"Morocco","lat":28.8,"lon":-9.4,"l":1},{"n":"Egypt","lat":28.2,"lon":31.7,"l":1},{"n":"Libya","lat":28.5,"lon":16.6,"l":1},{"n":"Ethiopia","lat":9.0,"lon":39.2,"l":1},{"n":"Djibouti","lat":11.8,"lon":42.5,"l":2},{"n":"Somaliland","lat":10.5,"lon":46.4,"l":2},{"n":"Uganda","lat":1.3,"lon":32.0,"l":2},{"n":"Rwanda","lat":-2.0,"lon":29.9,"l":2},{"n":"Bosnia and Herzegovina","lat":44.2,"lon":17.9,"l":2},{"n":"North Macedonia","lat":41.7,"lon":21.6,"l":2},{"n":"Serbia","lat":43.9,"lon":20.9,"l":2},{"n":"Montenegro","lat":42.7,"lon":19.4,"l":2},{"n":"Kosovo","lat":42.5,"lon":21.0,"l":2},{"n":"Trinidad and Tobago","lat":10.5,"lon":-61.5,"l":2},{"n":"South Sudan","lat":8.0,"lon":30.1,"l":2}],"en-us":[{"n":"Fiji","lat":-18.0,"lon":178.0,"l":0},{"n":"Tanzania","lat":-6.5,"lon":34.3,"l":1},{"n":"Western Sahara","lat":24.8,"lon":-12.0,"l":2},{"n":"Canada","lat":56.0,"lon":-96.0,"l":0},{"n":"United States of America","lat":39.5,"lon":-98.0,"l":0},{"n":"Kazakhstan","lat":48.0,"lon":66.0,"l":0},{"n":"Uzbekistan","lat":41.2,"lon":65.3,"l":1},{"n":"Papua New Guinea","lat":-7.8,"lon":146.2,"l":1},{"n":"Indonesia","lat":-2.0,"lon":118.0,"l":0},{"n":"Argentina","lat":-36.0,"lon":-65.0,"l":0},{"n":"Chile","lat":-38.1,"lon":-71.4,"l":1},{"n":"Democratic Republic of the Congo","lat":-3.0,"lon":24.0,"l":1},{"n":"Somalia","lat":6.6,"lon":46.9,"l":1},{"n":"Kenya","lat":1.1,"lon":37.8,"l":2},{"n":"Sudan","lat":15.0,"lon":29.0,"l":1},{"n":"Chad","lat":15.0,"lon":18.0,"l":1},{"n":"Haiti","lat":18.8,"lon":-72.7,"l":2},{"n":"Dominican Republic","lat":18.7,"lon":-70.5,"l":2},{"n":"Russia","lat":61.0,"lon":90.0,"l":0},{"n":"The Bahamas","lat":24.5,"lon":-77.9,"l":2},{"n":"Falkland Islands","lat":-51.7,"lon":-59.6,"l":2},{"n":"Norway","lat":65.0,"lon":14.0,"l":0},{"n":"Greenland","lat":72.0,"lon":-40.0,"l":0},{"n":"French Southern and Antarctic Lands","lat":-49.1,"lon":69.5,"l":2},{"n":"East Timor","lat":-8.7,"lon":125.9,"l":2},{"n":"South Africa","lat":-28.6,"lon":24.7,"l":1},{"n":"Lesotho","lat":-29.6,"lon":28.4,"l":2},{"n":"Mexico","lat":23.5,"lon":-102.0,"l":0},{"n":"Uruguay","lat":-32.7,"lon":-56.1,"l":2},{"n":"Brazil","lat":-10.0,"lon":-53.0,"l":0},{"n":"Bolivia","lat":-16.3,"lon":-64.1,"l":1},{"n":"Peru","lat":-7.8,"lon":-74.1,"l":1},{"n":"Colombia","lat":4.5,"lon":-72.7,"l":1},{"n":"Panama","lat":8.5,"lon":-80.3,"l":2},{"n":"Costa Rica","lat":9.8,"lon":-84.2,"l":2},{"n":"Nicaragua","lat":13.1,"lon":-85.0,"l":2},{"n":"Honduras","lat":14.7,"lon":-86.3,"l":2},{"n":"El Salvador","lat":13.9,"lon":-88.9,"l":2},{"n":"Guatemala","lat":15.5,"lon":-90.3,"l":2},{"n":"Belize","lat":17.4,"lon":-88.6,"l":2},{"n":"Venezuela","lat":7.2,"lon":-66.9,"l":1},{"n":"Guyana","lat":4.5,"lon":-58.9,"l":2},{"n":"Suriname","lat":3.7,"lon":-55.9,"l":2},{"n":"France","lat":46.5,"lon":2.5,"l":0},{"n":"Ecuador","lat":-1.6,"lon":-78.7,"l":2},{"n":"Puerto Rico","lat":18.3,"lon":-66.4,"l":2},{"n":"Jamaica","lat":18.2,"lon":-77.3,"l":2},{"n":"Cuba","lat":21.7,"lon":-79.7,"l":2},{"n":"Zimbabwe","lat":-18.9,"lon":29.7,"l":2},{"n":"Botswana","lat":-22.5,"lon":24.5,"l":2},{"n":"Namibia","lat":-21.6,"lon":17.9,"l":1},{"n":"Senegal","lat":13.9,"lon":-14.6,"l":2},{"n":"Mali","lat":17.0,"lon":-2.0,"l":1},{"n":"Mauritania","lat":18.8,"lon":-12.4,"l":1},{"n":"Benin","lat":9.8,"lon":2.3,"l":2},{"n":"Niger","lat":17.0,"lon":8.5,"l":1},{"n":"Nigeria","lat":9.7,"lon":8.3,"l":1},{"n":"Cameroon","lat":6.9,"lon":13.2,"l":2},{"n":"Togo","lat":8.9,"lon":0.9,"l":2},{"n":"Ghana","lat":8.3,"lon":-1.0,"l":2},{"n":"Ivory Coast","lat":7.9,"lon":-6.3,"l":2},{"n":"Guinea","lat":10.4,"lon":-11.0,"l":2},{"n":"Guinea-Bissau","lat":12.0,"lon":-15.2,"l":2},{"n":"Liberia","lat":6.8,"lon":-9.1,"l":2},{"n":"Sierra Leone","lat":8.6,"lon":-11.7,"l":2},{"n":"Burkina Faso","lat":12.1,"lon":-1.9,"l":2},{"n":"Central African Republic","lat":6.3,"lon":20.7,"l":1},{"n":"Republic of the Congo","lat":-0.9,"lon":14.9,"l":2},{"n":"Gabon","lat":-0.3,"lon":11.9,"l":2},{"n":"Equatorial Guinea","lat":1.6,"lon":10.1,"l":2},{"n":"Zambia","lat":-12.8,"lon":28.0,"l":1},{"n":"Malawi","lat":-12.9,"lon":34.1,"l":2},{"n":"Mozambique","lat":-17.7,"lon":35.0,"l":1},{"n":"Eswatini","lat":-26.4,"lon":31.4,"l":2},{"n":"Angola","lat":-12.0,"lon":18.0,"l":1},{"n":"Burundi","lat":-3.2,"lon":30.0,"l":2},{"n":"Israel","lat":32.0,"lon":35.1,"l":2},{"n":"Lebanon","lat":33.8,"lon":35.9,"l":2},{"n":"Madagascar","lat":-18.0,"lon":47.0,"l":2},{"n":"Palestine","lat":31.8,"lon":35.2,"l":2},{"n":"The Gambia","lat":13.5,"lon":-15.3,"l":2},{"n":"Tunisia","lat":34.0,"lon":9.8,"l":2},{"n":"Algeria","lat":28.0,"lon":2.5,"l":1},{"n":"Jordan","lat":31.1,"lon":36.7,"l":2},{"n":"United Arab Emirates","lat":24.2,"lon":54.2,"l":2},{"n":"Qatar","lat":25.3,"lon":51.2,"l":2},{"n":"Kuwait","lat":29.3,"lon":47.7,"l":2},{"n":"Iraq","lat":33.4,"lon":44.4,"l":2},{"n":"Oman","lat":20.9,"lon":56.6,"l":2},{"n":"Vanuatu","lat":-15.4,"lon":166.9,"l":2},{"n":"Cambodia","lat":12.6,"lon":104.9,"l":2},{"n":"Thailand","lat":13.2,"lon":100.7,"l":1},{"n":"Laos","lat":18.3,"lon":103.7,"l":2},{"n":"Myanmar","lat":20.0,"lon":97.2,"l":1},{"n":"Vietnam","lat":16.7,"lon":105.9,"l":1},{"n":"North Korea","lat":39.9,"lon":127.4,"l":2},{"n":"South Korea","lat":36.7,"lon":127.5,"l":2},{"n":"Mongolia","lat":47.2,"lon":104.6,"l":1},{"n":"India","lat":22.0,"lon":80.0,"l":0},{"n":"Bangladesh","lat":23.4,"lon":90.6,"l":2},{"n":"Bhutan","lat":27.5,"lon":90.6,"l":2},{"n":"Nepal","lat":28.2,"lon":84.6,"l":2},{"n":"Pakistan","lat":30.8,"lon":69.4,"l":1},{"n":"Afghanistan","lat":34.8,"lon":67.8,"l":1},{"n":"Tajikistan","lat":38.5,"lon":70.8,"l":2},{"n":"Kyrgyzstan","lat":41.4,"lon":74.0,"l":2},{"n":"Turkmenistan","lat":39.3,"lon":58.5,"l":1},{"n":"Iran","lat":33.4,"lon":53.2,"l":1},{"n":"Syria","lat":35.1,"lon":38.0,"l":2},{"n":"Armenia","lat":39.9,"lon":45.3,"l":2},{"n":"Sweden","lat":62.7,"lon":16.6,"l":1},{"n":"Belarus","lat":53.3,"lon":28.3,"l":2},{"n":"Ukraine","lat":48.7,"lon":30.5,"l":1},{"n":"Poland","lat":51.7,"lon":19.5,"l":2},{"n":"Austria","lat":47.6,"lon":13.5,"l":2},{"n":"Hungary","lat":47.4,"lon":19.2,"l":2},{"n":"Moldova","lat":47.0,"lon":28.5,"l":2},{"n":"Romania","lat":45.9,"lon":25.2,"l":2},{"n":"Lithuania","lat":55.2,"lon":24.0,"l":2},{"n":"Latvia","lat":56.9,"lon":24.9,"l":2},{"n":"Estonia","lat":58.7,"lon":26.1,"l":2},{"n":"Germany","lat":51.0,"lon":10.7,"l":2},{"n":"Bulgaria","lat":42.9,"lon":24.7,"l":2},{"n":"Greece","lat":39.8,"lon":23.1,"l":2},{"n":"Turkey","lat":38.4,"lon":36.9,"l":1},{"n":"Albania","lat":41.3,"lon":20.1,"l":2},{"n":"Croatia","lat":44.8,"lon":16.4,"l":2},{"n":"Switzerland","lat":46.8,"lon":8.3,"l":2},{"n":"Luxembourg","lat":49.8,"lon":6.0,"l":2},{"n":"Belgium","lat":50.7,"lon":4.4,"l":2},{"n":"Netherlands","lat":52.1,"lon":5.5,"l":2},{"n":"Portugal","lat":39.8,"lon":-8.0,"l":2},{"n":"Spain","lat":40.2,"lon":-4.5,"l":2},{"n":"Ireland","lat":53.5,"lon":-7.7,"l":2},{"n":"New Caledonia","lat":-21.2,"lon":165.5,"l":2},{"n":"Solomon Islands","lat":-7.9,"lon":159.1,"l":2},{"n":"New Zealand","lat":-38.2,"lon":175.5,"l":1},{"n":"Australia","lat":-25.0,"lon":134.0,"l":0},{"n":"Sri Lanka","lat":7.6,"lon":80.9,"l":2},{"n":"People's Republic of China","lat":35.0,"lon":104.0,"l":0},{"n":"Taiwan","lat":23.9,"lon":121.1,"l":2},{"n":"Italy","lat":43.1,"lon":12.6,"l":1},{"n":"Denmark","lat":56.3,"lon":9.6,"l":2},{"n":"United Kingdom","lat":53.9,"lon":-3.1,"l":2},{"n":"Iceland","lat":65.3,"lon":-19.3,"l":2},{"n":"Azerbaijan","lat":40.4,"lon":47.4,"l":2},{"n":"Georgia","lat":42.3,"lon":43.4,"l":2},{"n":"Philippines","lat":15.4,"lon":121.8,"l":1},{"n":"Malaysia","lat":3.7,"lon":114.8,"l":1},{"n":"Brunei","lat":4.7,"lon":115.0,"l":2},{"n":"Slovenia","lat":46.1,"lon":15.0,"l":2},{"n":"Finland","lat":65.2,"lon":25.9,"l":1},{"n":"Slovakia","lat":48.8,"lon":19.4,"l":2},{"n":"Czech Republic","lat":49.8,"lon":15.8,"l":2},{"n":"Eritrea","lat":14.7,"lon":39.6,"l":2},{"n":"Japan","lat":35.7,"lon":136.0,"l":1},{"n":"Paraguay","lat":-23.3,"lon":-57.6,"l":2},{"n":"Yemen","lat":15.5,"lon":46.5,"l":2},{"n":"Saudi Arabia","lat":24.0,"lon":44.0,"l":1},{"n":"Antarctica","lat":-73.0,"lon":-2.7,"l":0},{"n":"Turkish Republic of Northern Cyprus","lat":35.2,"lon":33.4,"l":2},{"n":"Cyprus","lat":35.0,"lon":33.2,"l":2},{"n":"Morocco","lat":28.8,"lon":-9.4,"l":1},{"n":"Egypt","lat":28.2,"lon":31.7,"l":1},{"n":"Libya","lat":28.5,"lon":16.6,"l":1},{"n":"Ethiopia","lat":9.0,"lon":39.2,"l":1},{"n":"Djibouti","lat":11.8,"lon":42.5,"l":2},{"n":"Somaliland","lat":10.5,"lon":46.4,"l":2},{"n":"Uganda","lat":1.3,"lon":32.0,"l":2},{"n":"Rwanda","lat":-2.0,"lon":29.9,"l":2},{"n":"Bosnia and Herzegovina","lat":44.2,"lon":17.9,"l":2},{"n":"North Macedonia","lat":41.7,"lon":21.6,"l":2},{"n":"Serbia","lat":43.9,"lon":20.9,"l":2},{"n":"Montenegro","lat":42.7,"lon":19.4,"l":2},{"n":"Kosovo","lat":42.5,"lon":21.0,"l":2},{"n":"Trinidad and Tobago","lat":10.5,"lon":-61.5,"l":2},{"n":"South Sudan","lat":8.0,"lon":30.1,"l":2}],"es":[{"n":"Fiyi","lat":-18.0,"lon":178.0,"l":0},{"n":"Tanzania","lat":-6.5,"lon":34.3,"l":1},{"n":"Sahara Occidental","lat":24.8,"lon":-12.0,"l":2},{"n":"Canadá","lat":56.0,"lon":-96.0,"l":0},{"n":"Estados Unidos","lat":39.5,"lon":-98.0,"l":0},{"n":"Kazajistán","lat":48.0,"lon":66.0,"l":0},{"n":"Uzbekistán","lat":41.2,"lon":65.3,"l":1},{"n":"Papúa Nueva Guinea","lat":-7.8,"lon":146.2,"l":1},{"n":"Indonesia","lat":-2.0,"lon":118.0,"l":0},{"n":"Argentina","lat":-36.0,"lon":-65.0,"l":0},{"n":"Chile","lat":-38.1,"lon":-71.4,"l":1},{"n":"República Democrática del Congo","lat":-3.0,"lon":24.0,"l":1},{"n":"Somalia","lat":6.6,"lon":46.9,"l":1},{"n":"Kenia","lat":1.1,"lon":37.8,"l":2},{"n":"Sudán","lat":15.0,"lon":29.0,"l":1},{"n":"Chad","lat":15.0,"lon":18.0,"l":1},{"n":"Haití","lat":18.8,"lon":-72.7,"l":2},{"n":"República Dominicana","lat":18.7,"lon":-70.5,"l":2},{"n":"Rusia","lat":61.0,"lon":90.0,"l":0},{"n":"Bahamas","lat":24.5,"lon":-77.9,"l":2},{"n":"Islas Malvinas","lat":-51.7,"lon":-59.6,"l":2},{"n":"Noruega","lat":65.0,"lon":14.0,"l":0},{"n":"Groenlandia","lat":72.0,"lon":-40.0,"l":0},{"n":"Tierras Australes y Antárticas Francesas","lat":-49.1,"lon":69.5,"l":2},{"n":"Timor Oriental","lat":-8.7,"lon":125.9,"l":2},{"n":"Sudáfrica","lat":-28.6,"lon":24.7,"l":1},{"n":"Lesoto","lat":-29.6,"lon":28.4,"l":2},{"n":"México","lat":23.5,"lon":-102.0,"l":0},{"n":"Uruguay","lat":-32.7,"lon":-56.1,"l":2},{"n":"Brasil","lat":-10.0,"lon":-53.0,"l":0},{"n":"Bolivia","lat":-16.3,"lon":-64.1,"l":1},{"n":"Perú","lat":-7.8,"lon":-74.1,"l":1},{"n":"Colombia","lat":4.5,"lon":-72.7,"l":1},{"n":"Panamá","lat":8.5,"lon":-80.3,"l":2},{"n":"Costa Rica","lat":9.8,"lon":-84.2,"l":2},{"n":"Nicaragua","lat":13.1,"lon":-85.0,"l":2},{"n":"Honduras","lat":14.7,"lon":-86.3,"l":2},{"n":"El Salvador","lat":13.9,"lon":-88.9,"l":2},{"n":"Guatemala","lat":15.5,"lon":-90.3,"l":2},{"n":"Belice","lat":17.4,"lon":-88.6,"l":2},{"n":"Venezuela","lat":7.2,"lon":-66.9,"l":1},{"n":"Guyana","lat":4.5,"lon":-58.9,"l":2},{"n":"Surinam","lat":3.7,"lon":-55.9,"l":2},{"n":"Francia","lat":46.5,"lon":2.5,"l":0},{"n":"Ecuador","lat":-1.6,"lon":-78.7,"l":2},{"n":"Puerto Rico","lat":18.3,"lon":-66.4,"l":2},{"n":"Jamaica","lat":18.2,"lon":-77.3,"l":2},{"n":"Cuba","lat":21.7,"lon":-79.7,"l":2},{"n":"Zimbabue","lat":-18.9,"lon":29.7,"l":2},{"n":"Botsuana","lat":-22.5,"lon":24.5,"l":2},{"n":"Namibia","lat":-21.6,"lon":17.9,"l":1},{"n":"Senegal","lat":13.9,"lon":-14.6,"l":2},{"n":"Malí","lat":17.0,"lon":-2.0,"l":1},{"n":"Mauritania","lat":18.8,"lon":-12.4,"l":1},{"n":"Benín","lat":9.8,"lon":2.3,"l":2},{"n":"Níger","lat":17.0,"lon":8.5,"l":1},{"n":"Nigeria","lat":9.7,"lon":8.3,"l":1},{"n":"Camerún","lat":6.9,"lon":13.2,"l":2},{"n":"Togo","lat":8.9,"lon":0.9,"l":2},{"n":"Ghana","lat":8.3,"lon":-1.0,"l":2},{"n":"Costa de Marfil","lat":7.9,"lon":-6.3,"l":2},{"n":"Guinea","lat":10.4,"lon":-11.0,"l":2},{"n":"Guinea-Bisáu","lat":12.0,"lon":-15.2,"l":2},{"n":"Liberia","lat":6.8,"lon":-9.1,"l":2},{"n":"Sierra Leona","lat":8.6,"lon":-11.7,"l":2},{"n":"Burkina Faso","lat":12.1,"lon":-1.9,"l":2},{"n":"República Centroafricana","lat":6.3,"lon":20.7,"l":1},{"n":"República del Congo","lat":-0.9,"lon":14.9,"l":2},{"n":"Gabón","lat":-0.3,"lon":11.9,"l":2},{"n":"Guinea Ecuatorial","lat":1.6,"lon":10.1,"l":2},{"n":"Zambia","lat":-12.8,"lon":28.0,"l":1},{"n":"Malaui","lat":-12.9,"lon":34.1,"l":2},{"n":"Mozambique","lat":-17.7,"lon":35.0,"l":1},{"n":"Suazilandia","lat":-26.4,"lon":31.4,"l":2},{"n":"Angola","lat":-12.0,"lon":18.0,"l":1},{"n":"Burundi","lat":-3.2,"lon":30.0,"l":2},{"n":"Israel","lat":32.0,"lon":35.1,"l":2},{"n":"Líbano","lat":33.8,"lon":35.9,"l":2},{"n":"Madagascar","lat":-18.0,"lon":47.0,"l":2},{"n":"Palestina","lat":31.8,"lon":35.2,"l":2},{"n":"Gambia","lat":13.5,"lon":-15.3,"l":2},{"n":"Túnez","lat":34.0,"lon":9.8,"l":2},{"n":"Argelia","lat":28.0,"lon":2.5,"l":1},{"n":"Jordania","lat":31.1,"lon":36.7,"l":2},{"n":"Emiratos Árabes Unidos","lat":24.2,"lon":54.2,"l":2},{"n":"Catar","lat":25.3,"lon":51.2,"l":2},{"n":"Kuwait","lat":29.3,"lon":47.7,"l":2},{"n":"Irak","lat":33.4,"lon":44.4,"l":2},{"n":"Omán","lat":20.9,"lon":56.6,"l":2},{"n":"Vanuatu","lat":-15.4,"lon":166.9,"l":2},{"n":"Camboya","lat":12.6,"lon":104.9,"l":2},{"n":"Tailandia","lat":13.2,"lon":100.7,"l":1},{"n":"Laos","lat":18.3,"lon":103.7,"l":2},{"n":"Birmania","lat":20.0,"lon":97.2,"l":1},{"n":"Vietnam","lat":16.7,"lon":105.9,"l":1},{"n":"Corea del Norte","lat":39.9,"lon":127.4,"l":2},{"n":"Corea del Sur","lat":36.7,"lon":127.5,"l":2},{"n":"Mongolia","lat":47.2,"lon":104.6,"l":1},{"n":"India","lat":22.0,"lon":80.0,"l":0},{"n":"Bangladés","lat":23.4,"lon":90.6,"l":2},{"n":"Bután","lat":27.5,"lon":90.6,"l":2},{"n":"Nepal","lat":28.2,"lon":84.6,"l":2},{"n":"Pakistán","lat":30.8,"lon":69.4,"l":1},{"n":"Afganistán","lat":34.8,"lon":67.8,"l":1},{"n":"Tayikistán","lat":38.5,"lon":70.8,"l":2},{"n":"Kirguistán","lat":41.4,"lon":74.0,"l":2},{"n":"Turkmenistán","lat":39.3,"lon":58.5,"l":1},{"n":"Irán","lat":33.4,"lon":53.2,"l":1},{"n":"Siria","lat":35.1,"lon":38.0,"l":2},{"n":"Armenia","lat":39.9,"lon":45.3,"l":2},{"n":"Suecia","lat":62.7,"lon":16.6,"l":1},{"n":"Bielorrusia","lat":53.3,"lon":28.3,"l":2},{"n":"Ucrania","lat":48.7,"lon":30.5,"l":1},{"n":"Polonia","lat":51.7,"lon":19.5,"l":2},{"n":"Austria","lat":47.6,"lon":13.5,"l":2},{"n":"Hungría","lat":47.4,"lon":19.2,"l":2},{"n":"Moldavia","lat":47.0,"lon":28.5,"l":2},{"n":"Rumania","lat":45.9,"lon":25.2,"l":2},{"n":"Lituania","lat":55.2,"lon":24.0,"l":2},{"n":"Letonia","lat":56.9,"lon":24.9,"l":2},{"n":"Estonia","lat":58.7,"lon":26.1,"l":2},{"n":"Alemania","lat":51.0,"lon":10.7,"l":2},{"n":"Bulgaria","lat":42.9,"lon":24.7,"l":2},{"n":"Grecia","lat":39.8,"lon":23.1,"l":2},{"n":"Turquía","lat":38.4,"lon":36.9,"l":1},{"n":"Albania","lat":41.3,"lon":20.1,"l":2},{"n":"Croacia","lat":44.8,"lon":16.4,"l":2},{"n":"Suiza","lat":46.8,"lon":8.3,"l":2},{"n":"Luxemburgo","lat":49.8,"lon":6.0,"l":2},{"n":"Bélgica","lat":50.7,"lon":4.4,"l":2},{"n":"Países Bajos","lat":52.1,"lon":5.5,"l":2},{"n":"Portugal","lat":39.8,"lon":-8.0,"l":2},{"n":"España","lat":40.2,"lon":-4.5,"l":2},{"n":"Irlanda","lat":53.5,"lon":-7.7,"l":2},{"n":"Nueva Caledonia","lat":-21.2,"lon":165.5,"l":2},{"n":"Islas Salomón","lat":-7.9,"lon":159.1,"l":2},{"n":"Nueva Zelanda","lat":-38.2,"lon":175.5,"l":1},{"n":"Australia","lat":-25.0,"lon":134.0,"l":0},{"n":"Sri Lanka","lat":7.6,"lon":80.9,"l":2},{"n":"China","lat":35.0,"lon":104.0,"l":0},{"n":"República de China","lat":23.9,"lon":121.1,"l":2},{"n":"Italia","lat":43.1,"lon":12.6,"l":1},{"n":"Dinamarca","lat":56.3,"lon":9.6,"l":2},{"n":"Reino Unido","lat":53.9,"lon":-3.1,"l":2},{"n":"Islandia","lat":65.3,"lon":-19.3,"l":2},{"n":"Azerbaiyán","lat":40.4,"lon":47.4,"l":2},{"n":"Georgia","lat":42.3,"lon":43.4,"l":2},{"n":"Filipinas","lat":15.4,"lon":121.8,"l":1},{"n":"Malasia","lat":3.7,"lon":114.8,"l":1},{"n":"Brunéi","lat":4.7,"lon":115.0,"l":2},{"n":"Eslovenia","lat":46.1,"lon":15.0,"l":2},{"n":"Finlandia","lat":65.2,"lon":25.9,"l":1},{"n":"Eslovaquia","lat":48.8,"lon":19.4,"l":2},{"n":"República Checa","lat":49.8,"lon":15.8,"l":2},{"n":"Eritrea","lat":14.7,"lon":39.6,"l":2},{"n":"Japón","lat":35.7,"lon":136.0,"l":1},{"n":"Paraguay","lat":-23.3,"lon":-57.6,"l":2},{"n":"Yemen","lat":15.5,"lon":46.5,"l":2},{"n":"Arabia Saudita","lat":24.0,"lon":44.0,"l":1},{"n":"Antártida","lat":-73.0,"lon":-2.7,"l":0},{"n":"República Turca del Norte de Chipre","lat":35.2,"lon":33.4,"l":2},{"n":"Chipre","lat":35.0,"lon":33.2,"l":2},{"n":"Marruecos","lat":28.8,"lon":-9.4,"l":1},{"n":"Egipto","lat":28.2,"lon":31.7,"l":1},{"n":"Libia","lat":28.5,"lon":16.6,"l":1},{"n":"Etiopía","lat":9.0,"lon":39.2,"l":1},{"n":"Yibuti","lat":11.8,"lon":42.5,"l":2},{"n":"Somalilandia","lat":10.5,"lon":46.4,"l":2},{"n":"Uganda","lat":1.3,"lon":32.0,"l":2},{"n":"Ruanda","lat":-2.0,"lon":29.9,"l":2},{"n":"Bosnia y Herzegovina","lat":44.2,"lon":17.9,"l":2},{"n":"Macedonia del Norte","lat":41.7,"lon":21.6,"l":2},{"n":"Serbia","lat":43.9,"lon":20.9,"l":2},{"n":"Montenegro","lat":42.7,"lon":19.4,"l":2},{"n":"Kosovo","lat":42.5,"lon":21.0,"l":2},{"n":"Trinidad y Tobago","lat":10.5,"lon":-61.5,"l":2},{"n":"Sudán del Sur","lat":8.0,"lon":30.1,"l":2}],"de":[{"n":"Fidschi","lat":-18.0,"lon":178.0,"l":0},{"n":"Tansania","lat":-6.5,"lon":34.3,"l":1},{"n":"Westsahara","lat":24.8,"lon":-12.0,"l":2},{"n":"Kanada","lat":56.0,"lon":-96.0,"l":0},{"n":"Vereinigte Staaten","lat":39.5,"lon":-98.0,"l":0},{"n":"Kasachstan","lat":48.0,"lon":66.0,"l":0},{"n":"Usbekistan","lat":41.2,"lon":65.3,"l":1},{"n":"Papua-Neuguinea","lat":-7.8,"lon":146.2,"l":1},{"n":"Indonesien","lat":-2.0,"lon":118.0,"l":0},{"n":"Argentinien","lat":-36.0,"lon":-65.0,"l":0},{"n":"Chile","lat":-38.1,"lon":-71.4,"l":1},{"n":"Demokratische Republik Kongo","lat":-3.0,"lon":24.0,"l":1},{"n":"Somalia","lat":6.6,"lon":46.9,"l":1},{"n":"Kenia","lat":1.1,"lon":37.8,"l":2},{"n":"Sudan","lat":15.0,"lon":29.0,"l":1},{"n":"Tschad","lat":15.0,"lon":18.0,"l":1},{"n":"Haiti","lat":18.8,"lon":-72.7,"l":2},{"n":"Dominikanische Republik","lat":18.7,"lon":-70.5,"l":2},{"n":"Russland","lat":61.0,"lon":90.0,"l":0},{"n":"Bahamas","lat":24.5,"lon":-77.9,"l":2},{"n":"Falklandinseln","lat":-51.7,"lon":-59.6,"l":2},{"n":"Norwegen","lat":65.0,"lon":14.0,"l":0},{"n":"Grönland","lat":72.0,"lon":-40.0,"l":0},{"n":"Französische Süd- und Antarktisgebiete","lat":-49.1,"lon":69.5,"l":2},{"n":"Osttimor","lat":-8.7,"lon":125.9,"l":2},{"n":"Südafrika","lat":-28.6,"lon":24.7,"l":1},{"n":"Lesotho","lat":-29.6,"lon":28.4,"l":2},{"n":"Mexiko","lat":23.5,"lon":-102.0,"l":0},{"n":"Uruguay","lat":-32.7,"lon":-56.1,"l":2},{"n":"Brasilien","lat":-10.0,"lon":-53.0,"l":0},{"n":"Bolivien","lat":-16.3,"lon":-64.1,"l":1},{"n":"Peru","lat":-7.8,"lon":-74.1,"l":1},{"n":"Kolumbien","lat":4.5,"lon":-72.7,"l":1},{"n":"Panama","lat":8.5,"lon":-80.3,"l":2},{"n":"Costa Rica","lat":9.8,"lon":-84.2,"l":2},{"n":"Nicaragua","lat":13.1,"lon":-85.0,"l":2},{"n":"Honduras","lat":14.7,"lon":-86.3,"l":2},{"n":"El Salvador","lat":13.9,"lon":-88.9,"l":2},{"n":"Guatemala","lat":15.5,"lon":-90.3,"l":2},{"n":"Belize","lat":17.4,"lon":-88.6,"l":2},{"n":"Venezuela","lat":7.2,"lon":-66.9,"l":1},{"n":"Guyana","lat":4.5,"lon":-58.9,"l":2},{"n":"Suriname","lat":3.7,"lon":-55.9,"l":2},{"n":"Frankreich","lat":46.5,"lon":2.5,"l":0},{"n":"Ecuador","lat":-1.6,"lon":-78.7,"l":2},{"n":"Puerto Rico","lat":18.3,"lon":-66.4,"l":2},{"n":"Jamaika","lat":18.2,"lon":-77.3,"l":2},{"n":"Kuba","lat":21.7,"lon":-79.7,"l":2},{"n":"Simbabwe","lat":-18.9,"lon":29.7,"l":2},{"n":"Botswana","lat":-22.5,"lon":24.5,"l":2},{"n":"Namibia","lat":-21.6,"lon":17.9,"l":1},{"n":"Senegal","lat":13.9,"lon":-14.6,"l":2},{"n":"Mali","lat":17.0,"lon":-2.0,"l":1},{"n":"Mauretanien","lat":18.8,"lon":-12.4,"l":1},{"n":"Benin","lat":9.8,"lon":2.3,"l":2},{"n":"Niger","lat":17.0,"lon":8.5,"l":1},{"n":"Nigeria","lat":9.7,"lon":8.3,"l":1},{"n":"Kamerun","lat":6.9,"lon":13.2,"l":2},{"n":"Togo","lat":8.9,"lon":0.9,"l":2},{"n":"Ghana","lat":8.3,"lon":-1.0,"l":2},{"n":"Elfenbeinküste","lat":7.9,"lon":-6.3,"l":2},{"n":"Guinea","lat":10.4,"lon":-11.0,"l":2},{"n":"Guinea-Bissau","lat":12.0,"lon":-15.2,"l":2},{"n":"Liberia","lat":6.8,"lon":-9.1,"l":2},{"n":"Sierra Leone","lat":8.6,"lon":-11.7,"l":2},{"n":"Burkina Faso","lat":12.1,"lon":-1.9,"l":2},{"n":"Zentralafrikanische Republik","lat":6.3,"lon":20.7,"l":1},{"n":"Republik Kongo","lat":-0.9,"lon":14.9,"l":2},{"n":"Gabun","lat":-0.3,"lon":11.9,"l":2},{"n":"Äquatorialguinea","lat":1.6,"lon":10.1,"l":2},{"n":"Sambia","lat":-12.8,"lon":28.0,"l":1},{"n":"Malawi","lat":-12.9,"lon":34.1,"l":2},{"n":"Mosambik","lat":-17.7,"lon":35.0,"l":1},{"n":"Eswatini","lat":-26.4,"lon":31.4,"l":2},{"n":"Angola","lat":-12.0,"lon":18.0,"l":1},{"n":"Burundi","lat":-3.2,"lon":30.0,"l":2},{"n":"Israel","lat":32.0,"lon":35.1,"l":2},{"n":"Libanon","lat":33.8,"lon":35.9,"l":2},{"n":"Madagaskar","lat":-18.0,"lon":47.0,"l":2},{"n":"Palästina","lat":31.8,"lon":35.2,"l":2},{"n":"Gambia","lat":13.5,"lon":-15.3,"l":2},{"n":"Tunesien","lat":34.0,"lon":9.8,"l":2},{"n":"Algerien","lat":28.0,"lon":2.5,"l":1},{"n":"Jordanien","lat":31.1,"lon":36.7,"l":2},{"n":"Vereinigte Arabische Emirate","lat":24.2,"lon":54.2,"l":2},{"n":"Katar","lat":25.3,"lon":51.2,"l":2},{"n":"Kuwait","lat":29.3,"lon":47.7,"l":2},{"n":"Irak","lat":33.4,"lon":44.4,"l":2},{"n":"Oman","lat":20.9,"lon":56.6,"l":2},{"n":"Vanuatu","lat":-15.4,"lon":166.9,"l":2},{"n":"Kambodscha","lat":12.6,"lon":104.9,"l":2},{"n":"Thailand","lat":13.2,"lon":100.7,"l":1},{"n":"Laos","lat":18.3,"lon":103.7,"l":2},{"n":"Myanmar","lat":20.0,"lon":97.2,"l":1},{"n":"Vietnam","lat":16.7,"lon":105.9,"l":1},{"n":"Nordkorea","lat":39.9,"lon":127.4,"l":2},{"n":"Südkorea","lat":36.7,"lon":127.5,"l":2},{"n":"Mongolei","lat":47.2,"lon":104.6,"l":1},{"n":"Indien","lat":22.0,"lon":80.0,"l":0},{"n":"Bangladesch","lat":23.4,"lon":90.6,"l":2},{"n":"Bhutan","lat":27.5,"lon":90.6,"l":2},{"n":"Nepal","lat":28.2,"lon":84.6,"l":2},{"n":"Pakistan","lat":30.8,"lon":69.4,"l":1},{"n":"Afghanistan","lat":34.8,"lon":67.8,"l":1},{"n":"Tadschikistan","lat":38.5,"lon":70.8,"l":2},{"n":"Kirgisistan","lat":41.4,"lon":74.0,"l":2},{"n":"Turkmenistan","lat":39.3,"lon":58.5,"l":1},{"n":"Iran","lat":33.4,"lon":53.2,"l":1},{"n":"Syrien","lat":35.1,"lon":38.0,"l":2},{"n":"Armenien","lat":39.9,"lon":45.3,"l":2},{"n":"Schweden","lat":62.7,"lon":16.6,"l":1},{"n":"Belarus","lat":53.3,"lon":28.3,"l":2},{"n":"Ukraine","lat":48.7,"lon":30.5,"l":1},{"n":"Polen","lat":51.7,"lon":19.5,"l":2},{"n":"Österreich","lat":47.6,"lon":13.5,"l":2},{"n":"Ungarn","lat":47.4,"lon":19.2,"l":2},{"n":"Republik Moldau","lat":47.0,"lon":28.5,"l":2},{"n":"Rumänien","lat":45.9,"lon":25.2,"l":2},{"n":"Litauen","lat":55.2,"lon":24.0,"l":2},{"n":"Lettland","lat":56.9,"lon":24.9,"l":2},{"n":"Estland","lat":58.7,"lon":26.1,"l":2},{"n":"Deutschland","lat":51.0,"lon":10.7,"l":2},{"n":"Bulgarien","lat":42.9,"lon":24.7,"l":2},{"n":"Griechenland","lat":39.8,"lon":23.1,"l":2},{"n":"Türkei","lat":38.4,"lon":36.9,"l":1},{"n":"Albanien","lat":41.3,"lon":20.1,"l":2},{"n":"Kroatien","lat":44.8,"lon":16.4,"l":2},{"n":"Schweiz","lat":46.8,"lon":8.3,"l":2},{"n":"Luxemburg","lat":49.8,"lon":6.0,"l":2},{"n":"Belgien","lat":50.7,"lon":4.4,"l":2},{"n":"Niederlande","lat":52.1,"lon":5.5,"l":2},{"n":"Portugal","lat":39.8,"lon":-8.0,"l":2},{"n":"Spanien","lat":40.2,"lon":-4.5,"l":2},{"n":"Irland","lat":53.5,"lon":-7.7,"l":2},{"n":"Neukaledonien","lat":-21.2,"lon":165.5,"l":2},{"n":"Salomonen","lat":-7.9,"lon":159.1,"l":2},{"n":"Neuseeland","lat":-38.2,"lon":175.5,"l":1},{"n":"Australien","lat":-25.0,"lon":134.0,"l":0},{"n":"Sri Lanka","lat":7.6,"lon":80.9,"l":2},{"n":"Volksrepublik China","lat":35.0,"lon":104.0,"l":0},{"n":"Republik China","lat":23.9,"lon":121.1,"l":2},{"n":"Italien","lat":43.1,"lon":12.6,"l":1},{"n":"Dänemark","lat":56.3,"lon":9.6,"l":2},{"n":"Vereinigtes Königreich","lat":53.9,"lon":-3.1,"l":2},{"n":"Island","lat":65.3,"lon":-19.3,"l":2},{"n":"Aserbaidschan","lat":40.4,"lon":47.4,"l":2},{"n":"Georgien","lat":42.3,"lon":43.4,"l":2},{"n":"Philippinen","lat":15.4,"lon":121.8,"l":1},{"n":"Malaysia","lat":3.7,"lon":114.8,"l":1},{"n":"Brunei","lat":4.7,"lon":115.0,"l":2},{"n":"Slowenien","lat":46.1,"lon":15.0,"l":2},{"n":"Finnland","lat":65.2,"lon":25.9,"l":1},{"n":"Slowakei","lat":48.8,"lon":19.4,"l":2},{"n":"Tschechien","lat":49.8,"lon":15.8,"l":2},{"n":"Eritrea","lat":14.7,"lon":39.6,"l":2},{"n":"Japan","lat":35.7,"lon":136.0,"l":1},{"n":"Paraguay","lat":-23.3,"lon":-57.6,"l":2},{"n":"Jemen","lat":15.5,"lon":46.5,"l":2},{"n":"Saudi-Arabien","lat":24.0,"lon":44.0,"l":1},{"n":"Antarktika","lat":-73.0,"lon":-2.7,"l":0},{"n":"Türkische Republik Nordzypern","lat":35.2,"lon":33.4,"l":2},{"n":"Republik Zypern","lat":35.0,"lon":33.2,"l":2},{"n":"Marokko","lat":28.8,"lon":-9.4,"l":1},{"n":"Ägypten","lat":28.2,"lon":31.7,"l":1},{"n":"Libyen","lat":28.5,"lon":16.6,"l":1},{"n":"Äthiopien","lat":9.0,"lon":39.2,"l":1},{"n":"Dschibuti","lat":11.8,"lon":42.5,"l":2},{"n":"Somaliland","lat":10.5,"lon":46.4,"l":2},{"n":"Uganda","lat":1.3,"lon":32.0,"l":2},{"n":"Ruanda","lat":-2.0,"lon":29.9,"l":2},{"n":"Bosnien und Herzegowina","lat":44.2,"lon":17.9,"l":2},{"n":"Nordmazedonien","lat":41.7,"lon":21.6,"l":2},{"n":"Serbien","lat":43.9,"lon":20.9,"l":2},{"n":"Montenegro","lat":42.7,"lon":19.4,"l":2},{"n":"Kosovo","lat":42.5,"lon":21.0,"l":2},{"n":"Trinidad und Tobago","lat":10.5,"lon":-61.5,"l":2},{"n":"Südsudan","lat":8.0,"lon":30.1,"l":2}]}
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
        html = generate_map_page(lang, map_data_js, world_json, clabels_json, clabels_by_lang)

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
