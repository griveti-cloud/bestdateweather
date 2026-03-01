#!/usr/bin/env python3
"""
factorize.py — BestDateWeather JS Factorization
=================================================
Transforms FR + EN inline JS into:
  - js/core.js       (shared logic, references T.xxx and CFG.xxx)
  - js/i18n-fr.js    (French strings + locale config)
  - js/i18n-en.js    (English strings + locale config)

Also updates index.html and en/app.html to reference external files.

Run: python3 factorize.py
Prerequisites: /tmp/orig_fr_main.js and /tmp/orig_en_main.js
  (extracted from git HEAD versions of index.html and en/app.html)
"""
import re, os, json, sys

ROOT = os.path.dirname(os.path.abspath(__file__))

# ── Read originals ────────────────────────────────────────────────────────────

with open('/tmp/orig_fr_main.js') as f:
    fr = f.read()
with open('/tmp/orig_en_main.js') as f:
    en = f.read()

# ── Replacement engine ────────────────────────────────────────────────────────

errors = []
warnings = []
core = fr  # Start from FR as base

def R(old, new, label='', count=1):
    """Replace exact string in core. count=0 means replace all."""
    global core
    actual = core.count(old)
    if actual == 0:
        errors.append(f'NOT FOUND [{label}]: {old[:80]}')
        return False
    if count > 0 and actual != count:
        warnings.append(f'COUNT [{label}]: expected {count}, found {actual}')
    core = core.replace(old, new, count if count > 0 else 999)
    return True

def RA(old, new, label=''):
    """Replace ALL occurrences."""
    return R(old, new, label, count=0)

# ══════════════════════════════════════════════════════════════════════════════
# STEP 0: Insert header + units functions (from EN, missing in FR)
# ══════════════════════════════════════════════════════════════════════════════

HEADER = """// BestDateWeather — core.js
// Requires: i18n-xx.js loaded BEFORE this file (sets window.BDW_T + window.BDW_CFG)
var T = window.BDW_T;
var CFG = window.BDW_CFG;

/* ── UNITS TOGGLE (°C/°F) ── */
var _units = 'metric';

function setUnits(sys) {
 _units = sys;
 var m = document.getElementById('btn-metric');
 var u = document.getElementById('btn-us');
 if (m) m.classList.toggle('active', sys === 'metric');
 if (u) u.classList.toggle('active', sys === 'us');
 if (window._lastRows && window._lastSc) {
  computeAndRenderScore(window._lastSc, window._lastRows);
  updateHero(window._lastSc, window._lastRows);
 }
}

function fmtTemp(c) {
 if (c == null) return '–';
 if (_units === 'us') return Math.round(c * 9/5 + 32) + '°F';
 return Math.round(c) + '°C';
}

function fmtTempRaw(c) {
 if (c == null) return null;
 if (_units === 'us') return Math.round(c * 9/5 + 32);
 return Math.round(c);
}

function fmtTempUnit() { return _units === 'us' ? '°F' : '°C'; }

function fmtWind(kmh) {
 if (kmh == null) return '–';
 if (_units === 'us') return Math.round(kmh * 0.621371) + ' mph';
 return Math.round(kmh) + ' km/h';
}

function fmtPrecip(mm) {
 if (mm == null) return '–';
 if (_units === 'us') { var inches = mm * 0.0393701; return (inches < 0.1 ? inches.toFixed(2) : inches.toFixed(1)) + ' in'; }
 return mm + ' mm';
}

"""

core = HEADER + core

# ══════════════════════════════════════════════════════════════════════════════
# STEP 1: Placeholders
# ══════════════════════════════════════════════════════════════════════════════

R("plage:'Destination plage…'", "plage:T.phBeach", 'ph beach')
R("ski:'Station de ski…'", "ski:T.phSki", 'ph ski')
R("placeholders[type] || 'Paris, Barcelone, Tokyo…'", "placeholders[type] || T.phDefault", 'ph default')

# ══════════════════════════════════════════════════════════════════════════════
# STEP 2: Snow alerts (appear TWICE each — live fetch + climate path)
# ══════════════════════════════════════════════════════════════════════════════

# Snow alt low — sdEl2 path
R("_sdEl2.textContent = '❄ Altitude ' + elev + 'm — trop basse pour évaluer l\\'enneigement';",
  "_sdEl2.textContent = T.snowAltLow.replace('{e}', elev);", 'snow alt low sdEl2')

# Snow estimated — sdEl2 path
R("var elevStr = elev ? ' à ' + elev + 'm' : '';\n     _sdEl2.textContent = '❄ Enneigement estimé : ' + res.depth + ' cm' + elevStr + ' · mesure Open-Meteo (point géographique, non domaine skiable)';",
  "var elevStr = elev ? T.snowElevAt.replace('{e}', elev) : '';\n     _sdEl2.textContent = T.snowEst.replace('{d}', res.depth).replace('{e}', elevStr);",
  'snow est sdEl2')

# Snow NA — sdEl2 path
R("_sdEl2.textContent = '❄ Données d\\'enneigement indisponibles pour cette date';",
  "_sdEl2.textContent = T.snowNA;", 'snow NA sdEl2')

# Snow alt low — sdEl path (climate path, later in file)
R("_sdEl.textContent = '❄ Altitude ' + elev + 'm — trop basse pour évaluer l\\'enneigement';",
  "_sdEl.textContent = T.snowAltLow.replace('{e}', elev);", 'snow alt low sdEl')

# Snow estimated — sdEl path
R("var elevStr = elev ? ' à ' + elev + 'm' : '';\n        _sdEl.textContent = '❄ Enneigement estimé : ' + res.depth + ' cm' + elevStr + ' · mesure Open-Meteo (point géographique, non domaine skiable)';",
  "var elevStr = elev ? T.snowElevAt.replace('{e}', elev) : '';\n        _sdEl.textContent = T.snowEst.replace('{d}', res.depth).replace('{e}', elevStr);",
  'snow est sdEl')

# Snow NA — sdEl path
R("_sdEl.textContent = '❄ Données d\\'enneigement indisponibles pour cette date';",
  "_sdEl.textContent = T.snowNA;", 'snow NA sdEl')

# ══════════════════════════════════════════════════════════════════════════════
# STEP 3: Weather condition labels (getIcon/getLabel — each appears 2x)
# ══════════════════════════════════════════════════════════════════════════════

weather_pairs = [
    ("return 'Orage';", "return T.storm;"),
    ("return 'Neige';", "return T.snow;"),
    ("return 'Pluie';", "return T.rain;"),
    ("return 'Averses';", "return T.showers;"),
    ("return 'Nuit claire';", "return T.clearNight;"),
    ("return 'Nuit nuageuse';", "return T.cloudyNight;"),
    ("return 'Fortes pluies';", "return T.heavyRain;"),
    ("return 'Pluie légère';", "return T.lightRain;"),
    ("return 'Brouillard';", "return T.fog;"),
    ("return 'Couvert';", "return T.overcast;"),
    ("return 'Partiellement nuageux';", "return T.partlyCloudy;"),
    ("return 'Ensoleillé';", "return T.sunny;"),
]
for old, new in weather_pairs:
    RA(old, new, f'weather: {old}')

# ══════════════════════════════════════════════════════════════════════════════
# STEP 4: Moon phases
# ══════════════════════════════════════════════════════════════════════════════

moon_pairs = [
    ("name='Nouvelle lune'", "name=T.moonNew"),
    ("name='Croissant croissant'", "name=T.moonWaxCrescent"),
    ("name='Premier quartier'", "name=T.moonFirstQ"),
    ("name='Gibbeuse croissante'", "name=T.moonWaxGibbous"),
    ("name='Pleine lune'", "name=T.moonFull"),
    ("name='Gibbeuse décroissante'", "name=T.moonWanGibbous"),
    ("name='Dernier quartier'", "name=T.moonLastQ"),
    ("name='Croissant décroissant'", "name=T.moonWanCrescent"),
]
for old, new in moon_pairs:
    R(old, new, f'moon: {old}')

# ══════════════════════════════════════════════════════════════════════════════
# STEP 5: Sunrise/Sunset labels
# ══════════════════════════════════════════════════════════════════════════════

R("lblEls[i].textContent = 'Lever soleil (' + tzLabel + ')'",
  "lblEls[i].textContent = T.sunrise + ' (' + tzLabel + ')'", 'sunrise')
R("lblEls[i].textContent = 'Coucher soleil (' + tzLabel + ')'",
  "lblEls[i].textContent = T.sunset + ' (' + tzLabel + ')'", 'sunset')

# ══════════════════════════════════════════════════════════════════════════════
# STEP 6: Time mode labels
# ══════════════════════════════════════════════════════════════════════════════

R("""label.textContent = "Aujourd'hui \\u2014 météo en direct";""",
  "label.textContent = T.modeToday;", 'mode today try1', count=0)
# If unicode didn't match, try the actual em dash
if "Aujourd'hui" in core:
    R('''label.textContent = "Aujourd'hui — météo en direct";''',
      "label.textContent = T.modeToday;", 'mode today em dash', count=0)
if "Aujourd'hui" in core:
    # Try with \u2014 literal
    R("label.textContent = \"Aujourd'hui \u2014 météo en direct\";",
      "label.textContent = T.modeToday;", 'mode today literal', count=0)

R("label.textContent = 'Prévision météo réelle';",
  "label.textContent = T.modeLive;", 'mode live')
R("label.textContent = 'Tendance ECMWF — indicatif';",
  "label.textContent = T.modeEcmwf;", 'mode ecmwf', count=0)
if 'Tendance ECMWF' in core:
    R("label.textContent = 'Tendance ECMWF \u2014 indicatif';",
      "label.textContent = T.modeEcmwf;", 'mode ecmwf literal', count=0)
R("label.textContent = 'Profil climatique historique';",
  "label.textContent = T.modeClimate;", 'mode climate')

# "Voir la météo" — check exact format
RA("""span.textContent = "Voir la météo";""",
   "span.textContent = T.checkWeather;", 'check weather dq')
RA("span.textContent = 'Voir la météo';",
   "span.textContent = T.checkWeather;", 'check weather sq')

# ══════════════════════════════════════════════════════════════════════════════
# STEP 7: SEA_NAME_MAP → CFG (replace whole block)
# ══════════════════════════════════════════════════════════════════════════════

sea_map_match = re.search(r'var SEA_NAME_MAP = \{[^}]+\};', core, re.DOTALL)
if sea_map_match:
    core = core[:sea_map_match.start()] + 'var SEA_NAME_MAP = CFG.seaNameMap;' + core[sea_map_match.end():]
else:
    errors.append('NOT FOUND: SEA_NAME_MAP block')

# slugFromName → use CFG.slugNormalize
slug_match = re.search(r'function slugFromName\(name\) \{[^}]+\}', core, re.DOTALL)
if slug_match:
    core = core[:slug_match.start()] + """function slugFromName(name) {
 var n = CFG.slugNormalize(name);
 return SEA_NAME_MAP[n] || (SEA_CLIM_DATA[n] ? n : null);
}""" + core[slug_match.end():]
else:
    errors.append('NOT FOUND: slugFromName function')

# SEA_CLIM_DATA → CFG
sea_clim_match = re.search(r'var SEA_CLIM_DATA = \{.*?\n\};', core, re.DOTALL)
if sea_clim_match:
    fr_sea_clim = sea_clim_match.group(0)
    core = core[:sea_clim_match.start()] + 'var SEA_CLIM_DATA = CFG.seaClimData;' + core[sea_clim_match.end():]
else:
    errors.append('NOT FOUND: SEA_CLIM_DATA block')
    fr_sea_clim = ''

# ══════════════════════════════════════════════════════════════════════════════
# STEP 8: Sea temperature labels
# ══════════════════════════════════════════════════════════════════════════════

R("lbl:'Très chaude'", "lbl:T.seaVeryWarm", 'sea very warm')
R("lbl:'Chaude · baignade agréable'", "lbl:T.seaWarm", 'sea warm')
R("lbl:'Agréable'", "lbl:T.seaPleasant", 'sea pleasant')
R("lbl:'Fraîche'", "lbl:T.seaCool", 'sea cool')
R("lbl:'Froide'", "lbl:T.seaCold", 'sea cold')
R("lbl:'Très froide'", "lbl:T.seaVeryCold", 'sea very cold')

R("var lbl = sstResult.fallback ? '🌊 Mer (norm. sais.)' : '🌊 Mer';",
  "var lbl = sstResult.fallback ? T.seaLabelSeasonal : T.seaLabel;", 'sea chip label')

# Sea temp display: fmtTemp
R("sstResult.sst+'°C'", "fmtTemp(sstResult.sst)", 'sea temp display')

# Rename functions to generic names
R("function fetchMarineSST(", "function fetchMarineSST(", 'fetchMarineSST')  # keep same name in core
R("function renderSeaChip(", "function renderSeaChip(", 'renderSeaChip')  # keep same name

# ══════════════════════════════════════════════════════════════════════════════
# STEP 9: Forecast fetch error
# ══════════════════════════════════════════════════════════════════════════════

R("throw new Error('Prévisions indisponibles')", "throw new Error(T.errForecast)", 'err forecast')

# ══════════════════════════════════════════════════════════════════════════════
# STEP 10: Hero hourly grid — use fmtTempRaw for display
# ══════════════════════════════════════════════════════════════════════════════

# Hourly cell temp display: r.temp+'°' → fmtTempRaw(r.temp)+'°'
R("(r.temp!=null?r.temp+'\\u00b0':'-')",
  "(r.temp!=null?fmtTempRaw(r.temp)+'°':'-')", 'hourly temp', count=0)

# Score strip temp
R("(r.temp!=null?r.temp+'\\u00b0':'-')",
  "(r.temp!=null?fmtTempRaw(r.temp)+'°':'-')", 'strip temp', count=0)

# ══════════════════════════════════════════════════════════════════════════════
# STEP 11: Hero title/subtitle pairs (ALL of them)
# ══════════════════════════════════════════════════════════════════════════════

# Good weather branch (score >= 50)
R("{ title = 'Journée très chaude'; sub = 'Chaleur intense · peu de pluie'; }",
  "{ title = T.heroVeryHot; sub = T.heroVeryHotSub; }", 'hero very hot')
R("{ title = 'Journée chaude'; sub = 'Chaud · ensoleillé'; }",
  "{ title = T.heroHotDay; sub = T.heroHotDaySub; }", 'hero hot day')
R("{ title = 'Journée froide'; sub = 'Froid · peu de précipitations'; }",
  "{ title = T.heroColdDay; sub = T.heroColdDaySub; }", 'hero cold day good')
R("{ title = 'Belle journée'; sub = 'Ensoleillé · peu de pluie'; }",
  "{ title = T.heroIdealDay; sub = T.heroIdealDaySub; }", 'hero ideal day')
R("{ title = 'Journée correcte'; sub = 'Conditions acceptables'; }",
  "{ title = T.heroGoodDay; sub = T.heroGoodDaySub; }", 'hero good day')

# Bad weather branch (score < 50)
R("{ title = 'Journée très pluvieuse'; sub = 'Pluie fréquente'; }",
  "{ title = T.heroVeryRainy; sub = T.heroVeryRainySub; }", 'hero very rainy')
R("{ title = 'Canicule'; sub = 'Chaleur extrême · risque sanitaire'; }",
  "{ title = T.heroCanicule; sub = T.heroChaniculeSub; }", 'hero canicule')
R("{ title = 'Journée glaciale'; sub = 'Gel possible · conditions difficiles'; }",
  "{ title = T.heroFreezing; sub = T.heroFreezingSub; }", 'hero freezing')
R("{ title = 'Journée difficile'; sub = 'Pluie · températures fraîches'; }",
  "{ title = T.heroDifficult; sub = T.heroDifficultSub; }", 'hero difficult')
R("{ title = 'Journée mitigée'; sub = \"Nuageux · risque d'averses\"; }",
  "{ title = T.heroMixed; sub = T.heroMixedSub; }", 'hero mixed')

# ══════════════════════════════════════════════════════════════════════════════
# STEP 12: Score strip stats (Mini/Maxi, Pluie, Vent)
# ══════════════════════════════════════════════════════════════════════════════

R("tmin+'\\u00b0/'+tmax+'\\u00b0'",
  "fmtTempRaw(tmin)+'°/'+fmtTempRaw(tmax)+'°'", 'strip temps', count=0)

R("'Mini/Maxi'", "T.statMinMax", 'stat minmax')
R("'Pluie'", "T.statRain", 'stat rain', count=0)
# Be careful: 'Pluie' also appears in many other contexts
# Actually let's be more specific with the stats line
R("""'<div><div class="sc-stat-val">'+fmtTempRaw(tmin)+'°/'+fmtTempRaw(tmax)+'°</div><div class="sc-stat-lbl">Mini/Maxi</div></div><div><div class="sc-stat-val">'+Math.round(rSum/sc.length)+'%</div><div class="sc-stat-lbl">Pluie</div></div><div><div class="sc-stat-val">'+Math.round(wSum/sc.length)+' km/h</div><div class="sc-stat-lbl">Vent</div></div>'""",
   """'<div><div class="sc-stat-val">'+fmtTempRaw(tmin)+'°/'+fmtTempRaw(tmax)+'°</div><div class="sc-stat-lbl">'+T.statMinMax+'</div></div><div><div class="sc-stat-val">'+Math.round(rSum/sc.length)+'%</div><div class="sc-stat-lbl">'+T.statRain+'</div></div><div><div class="sc-stat-val">'+fmtWind(Math.round(wSum/sc.length))+'</div><div class="sc-stat-lbl">'+T.statWind+'</div></div>'""",
   'stat labels block')

# Hmm, the stat block might not match because we already modified tmin/tmax. Let me try the original version
# Actually the replacements are sequential, so the fmtTempRaw is already applied. Let me try the full original line instead.

# ══════════════════════════════════════════════════════════════════════════════
# STEP 12b: Stats — replace the whole line from original
# ══════════════════════════════════════════════════════════════════════════════

# The original FR line uses raw tmin/tmax + 'km/h'
ORIG_STATS = """document.getElementById(statsId).innerHTML='<div><div class="sc-stat-val">'+tmin+'\\u00b0/'+tmax+'\\u00b0</div><div class="sc-stat-lbl">Mini/Maxi</div></div><div><div class="sc-stat-val">'+Math.round(rSum/sc.length)+'%</div><div class="sc-stat-lbl">Pluie</div></div><div><div class="sc-stat-val">'+Math.round(wSum/sc.length)+' km/h</div><div class="sc-stat-lbl">Vent</div></div>';"""

NEW_STATS = """document.getElementById(statsId).innerHTML='<div><div class="sc-stat-val">'+fmtTempRaw(tmin)+'°/'+fmtTempRaw(tmax)+'°</div><div class="sc-stat-lbl">'+T.statMinMax+'</div></div><div><div class="sc-stat-val">'+Math.round(rSum/sc.length)+'%</div><div class="sc-stat-lbl">'+T.statRain+'</div></div><div><div class="sc-stat-val">'+fmtWind(Math.round(wSum/sc.length))+'</div><div class="sc-stat-lbl">'+T.statWind+'</div></div>';"""

R(ORIG_STATS, NEW_STATS, 'stats block full')

# ══════════════════════════════════════════════════════════════════════════════
# STEP 13: Score verdict labels
# ══════════════════════════════════════════════════════════════════════════════

R("label = 'Idéal'", "label = T.scIdeal", 'score ideal')
R("label = 'Très favorable'", "label = T.scVeryGood", 'score very good')
R("label = 'Favorable'", "label = T.scGood", 'score good')
# 'Acceptable' — doesn't exist as score label in FR, check:
# FR has: >= 50: no specific label (defaults)
# The actual FR text: no 'Acceptable' as a standalone score label
R("label = 'Peu favorable'", "label = T.scPoor", 'score poor')
R("label = 'Conditions défavorables'", "label = T.scBad", 'score bad')

# ══════════════════════════════════════════════════════════════════════════════
# STEP 14: Score actions
# ══════════════════════════════════════════════════════════════════════════════

# Ski
R("action = 'Bon enneigement probable'", "action = T.actGoodSnow", 'act good snow')
R("action = 'Vigilance — redoux possible'",
  "action = T.actCautionThaw", 'act caution thaw', count=0)
if 'Vigilance' in core:
    R("action = 'Vigilance \u2014 redoux possible'",
      "action = T.actCautionThaw", 'act caution thaw em', count=0)
R("action = 'Enneigement insuffisant probable'", "action = T.actBadSnow", 'act bad snow')

# Beach
R("action = 'Température optimale pour la baignade'", "action = T.actOptimalSwim", 'act optimal swim')
R("action = driver ? 'Attention — ' + driver : 'Eau fraîche ou conditions instables'",
  "action = driver ? T.actCautionBeach + ' — ' + driver : T.actCautionBeachFull", 'act caution beach', count=0)
if 'Attention' in core:
    R("action = driver ? 'Attention \u2014 ' + driver : 'Eau fra\u00eeche ou conditions instables'",
      "action = driver ? T.actCautionBeach + ' — ' + driver : T.actCautionBeachFull", 'act caution beach em', count=0)
R("action = driver ? 'Peu adapté — ' + driver : 'Température insuffisante ou conditions défavorables'",
  "action = driver ? T.actPoorBeach + ' — ' + driver : T.actPoorBeachFull", 'act poor beach', count=0)
if 'Peu adapt' in core:
    R("action = driver ? 'Peu adapté \u2014 ' + driver : 'Température insuffisante ou conditions défavorables'",
      "action = driver ? T.actPoorBeach + ' — ' + driver : T.actPoorBeachFull", 'act poor beach em', count=0)

# General
R("action = driver ? 'Réserver sereinement — ' + driver + ' résiduel' : 'Réserver sereinement'",
  "action = driver ? T.actBookOk + ' — ' + driver + T.actResidual : T.actBookOk", 'act book ok', count=0)
if 'Réserver sereinement' in core:
    R("action = driver ? 'Réserver sereinement \u2014 ' + driver + ' résiduel' : 'Réserver sereinement'",
      "action = driver ? T.actBookOk + ' — ' + driver + T.actResidual : T.actBookOk", 'act book ok em', count=0)

R("action = driver ? 'Prévoir un plan B — ' + driver : 'Conditions variables — prévoir un plan B'",
  "action = driver ? T.actPlanB + ' — ' + driver : T.actPlanBFull", 'act plan b', count=0)
if 'Prévoir un plan B' in core:
    R("action = driver ? 'Prévoir un plan B \u2014 ' + driver : 'Conditions variables \u2014 prévoir un plan B'",
      "action = driver ? T.actPlanB + ' — ' + driver : T.actPlanBFull", 'act plan b em', count=0)

R("action = driver ? 'Période instable — ' + driver : 'Période instable'",
  "action = driver ? T.actUnstable + ' — ' + driver : T.actUnstable", 'act unstable', count=0)
if 'Période instable' in core:
    R("action = driver ? 'Période instable \u2014 ' + driver : 'Période instable'",
      "action = driver ? T.actUnstable + ' — ' + driver : T.actUnstable", 'act unstable em', count=0)

# ══════════════════════════════════════════════════════════════════════════════
# STEP 15: Score drivers
# ══════════════════════════════════════════════════════════════════════════════

R("rain: 'risque de pluie élevé'", "rain: T.drvRain", 'driver rain')
R("temp_cold: 'températures fraîches'", "temp_cold: T.drvCold", 'driver cold')
R("temp_hot: uc === 'plage' ? 'chaleur excessive' : 'chaleur élevée'",
  "temp_hot: uc === 'plage' ? T.drvHotBeach : T.drvHotGen", 'driver hot')
R("wind: 'vent fréquent'", "wind: T.drvWind", 'driver wind')

R("var suffix = isSeasonal ? ' · tendance saisonnière' : '';",
  "var suffix = isSeasonal ? T.seasonalSuffix : '';", 'seasonal suffix', count=0)
if 'tendance saisonni' in core:
    R("var suffix = isSeasonal ? ' \u00b7 tendance saisonni\u00e8re' : '';",
      "var suffix = isSeasonal ? T.seasonalSuffix : '';", 'seasonal suffix lit', count=0)

# ══════════════════════════════════════════════════════════════════════════════
# STEP 16: Risk messages
# ══════════════════════════════════════════════════════════════════════════════

R("risks.push('Pluie probable (' + Math.round(avgRain) + '%)')",
  "risks.push(T.riskRainLikely.replace('{p}', Math.round(avgRain)))", 'risk rain likely')

R("""risks.push("Risque d'averses (" + Math.round(avgRain) + '%)')""",
  "risks.push(T.riskShowers.replace('{p}', Math.round(avgRain)))", 'risk showers')

R("risks.push('Température fraîche (' + Math.round(avgTemp) + '°C)')",
  "risks.push(T.riskCoolTemp.replace('{t}', fmtTemp(avgTemp)))", 'risk cool temp')

R("risks.push('Chaleur élevée (' + Math.round(avgTemp) + '°C)')",
  "risks.push(T.riskHighHeat.replace('{t}', fmtTemp(avgTemp)))", 'risk high heat')

R("risks.push('Vent soutenu (' + Math.round(avgWind) + ' km/h)')",
  "risks.push(T.riskWind.replace('{w}', fmtWind(avgWind)))", 'risk wind')

R("return 'Aucun risque majeur identifié'",
  "return T.riskNone", 'risk none')

R("return 'Risque : ' + risks.join(' · ')",
  "return T.riskPrefix + risks.join(' · ')", 'risk prefix')

# ══════════════════════════════════════════════════════════════════════════════
# STEP 17: Score chips
# ══════════════════════════════════════════════════════════════════════════════

R("{ lbl: 'Pluie', val: Math.round(avgRain)+'%'",
  "{ lbl: T.chipRain, val: Math.round(avgRain)+'%'", 'chip rain')
R("{ lbl: 'Précip.', val: totalMm > 0 ? totalMm + ' mm' : '0 mm'",
  "{ lbl: T.chipPrecip, val: fmtPrecip(totalMm > 0 ? totalMm : 0)", 'chip precip')
R("{ lbl: 'Temp.', val: avgTemp!=null?Math.round(avgTemp)+'°C':'–'",
  "{ lbl: T.chipTemp, val: avgTemp!=null?fmtTemp(avgTemp):'–'", 'chip temp')
R("{ lbl: 'Vent', val: Math.round(avgWind)+' km/h'",
  "{ lbl: T.chipWind, val: fmtWind(avgWind)", 'chip wind')
R("{ lbl: 'Neige', val: totalSnow + ' cm'",
  "{ lbl: T.chipSnow, val: totalSnow + ' cm'", 'chip snow')

# Humidity chip (FR-only feature — keep it, use T)
R("{ lbl: 'Humidité', val: Math.round(avgRh)+'%'",
  "{ lbl: T.chipHumidity, val: Math.round(avgRh)+'%'", 'chip humidity')

# Spread badge (FR-only)
R("spreadLabel = '🌡 Stable'", "spreadLabel = T.spreadStable", 'spread stable')
R("spreadLabel = '🌡 Variable'", "spreadLabel = T.spreadVariable", 'spread variable')

# renderSeaChip call
R("renderSeaChip(window._lastSSTResult)", "renderSeaChip(window._lastSSTResult)", 'sea chip call')

# ══════════════════════════════════════════════════════════════════════════════
# STEP 18: Use case labels
# ══════════════════════════════════════════════════════════════════════════════

R("general: { label:'Météo générale'", "general: { label:T.ucGeneral", 'uc general')
R("plage:'Score optimisé · Plage', ski:'Score optimisé · Ski', general:'Météo générale'",
  "plage:T.ucScoreBeach, ski:T.ucScoreSki, general:T.ucScoreGeneral", 'uc score labels', count=0)
if 'Score optimisé' in core:
    R("plage:'Score optimis\u00e9 \u00b7 Plage', ski:'Score optimis\u00e9 \u00b7 Ski', general:'M\u00e9t\u00e9o g\u00e9n\u00e9rale'",
      "plage:T.ucScoreBeach, ski:T.ucScoreSki, general:T.ucScoreGeneral", 'uc score labels lit', count=0)

R("document.getElementById('score-usecase').textContent = 'Score météo général'",
  "document.getElementById('score-usecase').textContent = T.ucScoreGeneral", 'uc score general default')

R("{plage:'Plage',ski:'Ski',general:'Météo générale'}",
  "{plage:T.ucBeach,ski:T.ucSki,general:T.ucGeneral}", 'uc names', count=0)
if "Météo générale" in core:
    R("{plage:'Plage',ski:'Ski',general:'M\u00e9t\u00e9o g\u00e9n\u00e9rale'}",
      "{plage:T.ucBeach,ski:T.ucSki,general:T.ucGeneral}", 'uc names lit', count=0)

# ══════════════════════════════════════════════════════════════════════════════
# STEP 19: Sky labels in updateHero
# ══════════════════════════════════════════════════════════════════════════════

RA("skyLbl='Pluvieux'", "skyLbl=T.skyRainy")
RA("skyLbl='Nuageux'", "skyLbl=T.skyCloudy")
RA("skyLbl='Plein soleil'", "skyLbl=T.skyClearSky")
RA("skyLbl='Ensoleillé'", "skyLbl=T.skySunny")
RA("skyLbl='Voilé'", "skyLbl=T.skyHazy")
RA("skyLbl='Couvert'", "skyLbl=T.skyOvercast")

# ══════════════════════════════════════════════════════════════════════════════
# STEP 20: Hero temperature display + range
# ══════════════════════════════════════════════════════════════════════════════

R("(main.temp||'-')+'<sup>\\u00b0</sup>'",
  "fmtTempRaw(main.temp||0)+'<sup>°</sup>'", 'hero temp')

R("tmin+'\\u00b0 / '+tmax+'\\u00b0 dans la journée'",
  "fmtTempRaw(tmin)+'° / '+fmtTempRaw(tmax)+'° '+T.duringDayShort", 'temp range')

# Temperature frequency
R("'Température dans ±2°C de '+Math.round(main.temp||0)+'° — '+_tf+'% des années à cette date'",
  "T.tempFreq.replace('{u}',fmtTempUnit()).replace('{t}',fmtTempRaw(main.temp||0)).replace('{p}',_tf)",
  'temp freq', count=0)
# Try with unicode
if 'Température dans' in core:
    R("'Temp\u00e9rature dans \u00b12\u00b0C de '+Math.round(main.temp||0)+'\u00b0 \u2014 '+_tf+'% des ann\u00e9es \u00e0 cette date'",
      "T.tempFreq.replace('{u}',fmtTempUnit()).replace('{t}',fmtTempRaw(main.temp||0)).replace('{p}',_tf)",
      'temp freq lit', count=0)

# ══════════════════════════════════════════════════════════════════════════════
# STEP 21: Seasonal correction display
# ══════════════════════════════════════════════════════════════════════════════

R("_tSign+Math.round(_to*10)/10+'°C /ECMWF'",
  "_tSign+Math.round(_to*10)/10+'° /ECMWF'", 'seasonal temp')
RA("(_ro>0?'+':'')+_ro+'% pluie'",
   "(_ro>0?'+':'')+_ro+'% '+T.wordRain")
R("_siEl.textContent='Correction saisonnière : '+_parts.join(' · ')",
  "_siEl.textContent=T.seasonalCorrection+' '+_parts.join(' · ')", 'seasonal correction', count=0)
if 'Correction saisonni' in core:
    R("_siEl.textContent='Correction saisonni\u00e8re : '+_parts.join(' \u00b7 ')",
      "_siEl.textContent=T.seasonalCorrection+' '+_parts.join(' · ')", 'seasonal correction lit', count=0)

# Wind display in hero
R("Math.round(wSum/rows.length)+' km/h'",
  "fmtWind(Math.round(wSum/rows.length))", 'hero wind', count=0)

# ══════════════════════════════════════════════════════════════════════════════
# STEP 22: Snow forecast alerts
# ══════════════════════════════════════════════════════════════════════════════

R("if (h < 14) return ' · en journée'",
  "if (h < 14) return T.duringDay", 'during day')

R("'❄️ Neige prévue' + _timeLbl + ' · ' + Math.round(_snowTotal*10)/10 + ' cm au total'",
  "T.snowExpected + _timeLbl + ' · ' + Math.round(_snowTotal*10)/10 + T.snowCmTotal",
  'snow expected')

R("'❄️ Neige probable' + _timeLbl + ' · ' + _snowHours + 'h de précipitations sous 2°C'",
  "T.snowLikely + _timeLbl + ' · ' + _snowHours + T.snowHoursBelow",
  'snow likely')

R("'❄️ Neige possible' + _timeLbl + ' · températures proches du gel avec précipitations'",
  "T.snowPossible + _timeLbl + T.snowNearFreezing",
  'snow possible')

# ══════════════════════════════════════════════════════════════════════════════
# STEP 23: Flag & data paths
# ══════════════════════════════════════════════════════════════════════════════

R("src=\"flags/'+", "src=\"'+CFG.flagBase+'", 'flag path')
R("fetch('data/monthly.json')", "fetch(CFG.dataBase+'data/monthly.json')", 'data path')

# ══════════════════════════════════════════════════════════════════════════════
# STEP 24: Date locale
# ══════════════════════════════════════════════════════════════════════════════

R("'fr-FR'", "CFG.dateLocale", 'date locale')

# ══════════════════════════════════════════════════════════════════════════════
# STEP 25: Error / progress messages
# ══════════════════════════════════════════════════════════════════════════════

R("errEl.textContent='⚠ Choisissez une date pour votre projet.'",
  "errEl.textContent=T.errDate", 'err date')
R("errEl2.textContent = '⚠ Sélectionnez une ville dans la liste déroulante pour garantir la bonne localisation.'",
  "errEl2.textContent = T.errCity", 'err city')

RA("throw new Error('Données météo indisponibles pour cette destination (' + reason + ')')",
   "throw new Error(T.errDataReason.replace('{r}', reason))")
RA("throw new Error('Données météo indisponibles pour cette destination')",
   "throw new Error(T.errData)")

R("errEl.textContent='Erreur : '+err.message", "errEl.textContent=T.errPrefix+err.message", 'err prefix 1')
R("err.textContent = 'Erreur : ' + e.message", "err.textContent = T.errPrefix + e.message", 'err prefix 2')

R("setP(0,'Localisation…')", "setP(0,T.progLocating)", 'prog locating')
R("setP(5,loc.name+' trouvé…')", "setP(5,loc.name+T.progFound)", 'prog found')
R("setP(30,'Prévisions météo réelles…')", "setP(30,T.progFetching)", 'prog fetching')
RA("setP(100,'Terminé')", "setP(100,T.progDone)")
R("setP(92,'Correction ECMWF saisonnière…')", "setP(92,T.progEcmwf)", 'prog ecmwf', count=0)
if 'Correction ECMWF' in core:
    R("setP(92,'Correction ECMWF saisonni\u00e8re\u2026')", "setP(92,T.progEcmwf)", 'prog ecmwf lit', count=0)

R("setAnnP(0, 'Localisation…')", "setAnnP(0, T.progLocating)", 'ann prog locating')
R("setAnnP(10, 'Récupération des données…')", "setAnnP(10, T.progFetchData)", 'ann prog fetch')
R("setAnnP(30, 'Données en cache…')", "setAnnP(30, T.progCache)", 'ann prog cache')
R("setAnnP(10, 'Téléchargement archive…')", "setAnnP(10, T.progDownload)", 'ann prog download')
RA("setAnnP(70, 'Agrégation mensuelle…')", "setAnnP(70, T.progAggregation)")
R("setAnnP(100, 'Terminé')", "setAnnP(100, T.progDone)", 'ann prog done')

# ══════════════════════════════════════════════════════════════════════════════
# STEP 26: Live/Climate/ECMWF notes
# ══════════════════════════════════════════════════════════════════════════════

R("'<strong>Prévision réelle</strong> · données météo en temps réel, mise à jour toutes les heures.'",
  "T.noteLive", 'note live')
R("'<strong>Tendance ECMWF</strong> · climatologie 10 ans corrigée par le modèle ECMWF — indicatif, non garanti.'",
  "T.noteEcmwf", 'note ecmwf', count=0)
if 'climatologie 10 ans' in core:
    R("'<strong>Tendance ECMWF</strong> \u00b7 climatologie 10 ans corrig\u00e9e par le mod\u00e8le ECMWF \u2014 indicatif, non garanti.'",
      "T.noteEcmwf", 'note ecmwf lit', count=0)
R("'<strong>Profil climatique</strong> · moyenne statistique des 10 dernières années pour cette date et ce lieu.'",
  "T.noteClimate", 'note climate', count=0)
if 'moyenne statistique' in core:
    R("'<strong>Profil climatique</strong> \u00b7 moyenne statistique des 10 derni\u00e8res ann\u00e9es pour cette date et ce lieu.'",
      "T.noteClimate", 'note climate lit', count=0)

# ══════════════════════════════════════════════════════════════════════════════
# STEP 27: COUNTRY_NAMES → CFG
# ══════════════════════════════════════════════════════════════════════════════

cn_short_match = re.search(r'var COUNTRY_NAMES_SHORT = \{[^}]+\};', core, re.DOTALL)
if cn_short_match:
    core = core[:cn_short_match.start()] + 'var COUNTRY_NAMES_SHORT = CFG.countryShort;' + core[cn_short_match.end():]

cn_full_match = re.search(r'var COUNTRY_NAMES = \{[^}]+\};', core, re.DOTALL)
if cn_full_match:
    core = core[:cn_full_match.start()] + 'var COUNTRY_NAMES = CFG.countryFull;' + core[cn_full_match.end():]

# ══════════════════════════════════════════════════════════════════════════════
# STEP 28: Weight tooltip labels
# ══════════════════════════════════════════════════════════════════════════════

R("'💧 Pluie &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'", "T.tipRainLbl", 'tip rain')
R("'🌡 Température '", "T.tipTempLbl", 'tip temp', count=0)
if '🌡 Temp' in core:
    R("'\U0001f321 Temp\u00e9rature '", "T.tipTempLbl", 'tip temp lit', count=0)
R("'💨 Vent &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'", "T.tipWindLbl", 'tip wind')
R("'☀ Soleil &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'", "T.tipSunLbl", 'tip sun')

R("'<span style=\"opacity:.6;font-size:10px\">Plage idéale : '",
  "'<span style=\"opacity:.6;font-size:10px\">'+T.tipIdealRange+' '", 'tip ideal range')
R("cfg.tempMin + '–' + cfg.tempMax + '°C</span>'",
  "fmtTempRaw(cfg.tempMin) + '–' + fmtTempRaw(cfg.tempMax) + fmtTempUnit() + '</span>'", 'tip temp range')

# ══════════════════════════════════════════════════════════════════════════════
# STEP 29: Monthly/Annual view
# ══════════════════════════════════════════════════════════════════════════════

R("var MONTHS_FR = ['Janvier','Février','Mars','Avril','Mai','Juin','Juillet','Août','Septembre','Octobre','Novembre','Décembre'];",
  "var MONTHS_FR = T.months;", 'months full')
R("var MONTHS_SHORT = ['Jan','Fév','Mar','Avr','Mai','Jun','Jul','Aoû','Sep','Oct','Nov','Déc'];",
  "var MONTHS_SHORT = T.monthsShort;", 'months short')

R("var ucLabels = {plage:'Meilleurs mois pour la plage',ski:'Meilleurs mois pour le ski'};",
  "var ucLabels = {plage:T.bestBeach,ski:T.bestSki};", 'best months labels')
R("ucSubEl.textContent = ucLabels[uc] || 'Score optimisé pour : ' + (ucNames[uc]||uc);",
  "ucSubEl.textContent = ucLabels[uc] || T.optimisedFor + ' ' + (ucNames[uc]||uc);", 'optimised for', count=0)
if 'Score optimisé pour' in core:
    R("ucSubEl.textContent = ucLabels[uc] || 'Score optimis\u00e9 pour : ' + (ucNames[uc]||uc);",
      "ucSubEl.textContent = ucLabels[uc] || T.optimisedFor + ' ' + (ucNames[uc]||uc);", 'optimised for lit', count=0)

# Avoid color: FR uses #f97316, EN uses #ef4444 — use CFG
RA("isAvoid ? '#f97316'", "isAvoid ? CFG.avoidColor")

# Seasonal badge
RA("'Tendance ECMWF'", "T.ecmwfTrend")
RA("'% pluie'", "'% '+T.wordRain")

# Badges
R("'<div class=\"month-badge rec\">Recommandé</div>'",
  "'<div class=\"month-badge rec\">'+T.badgeRec+'</div>'", 'badge rec')
R("'<div class=\"month-badge avoid\">Peu favorable</div>'",
  "'<div class=\"month-badge avoid\">'+T.badgeAvoid+'</div>'", 'badge avoid')
R("'<div class=\"month-best-badge\">🔥 Meilleur mois</div>'",
  "'<div class=\"month-best-badge\">'+T.badgeBest+'</div>'", 'badge best')

# Monthly card temps
R("d.avgTmax != null ? Math.round(d.avgTmax) + '°' : '–'",
  "d.avgTmax != null ? fmtTempRaw(d.avgTmax) + '°' : '–'", 'month tmax')
R("d.avgTmin != null ? Math.round(d.avgTmin) + '°' : '–'",
  "d.avgTmin != null ? fmtTempRaw(d.avgTmin) + '°' : '–'", 'month tmin')
R("d.avgTemp != null ? Math.round(d.avgTemp) + '°' : '–'",
  "d.avgTemp != null ? fmtTempRaw(d.avgTemp) + '°' : '–'", 'month tavg')

R("'moy. '", "T.avgLabel+' '", 'avg label')
R("d.avgPrecipMm + ' mm/j'", "fmtPrecip(d.avgPrecipMm)+'/'+T.dayAbbr", 'precip per day')

# Legend
R("""legendEl.innerHTML = '<span><span style="display:inline-block;width:12px;height:3px;background:#1a7a4a;border-radius:2px;margin-right:5px;vertical-align:middle"></span>Recommandé</span>' +
  '<span><span style="display:inline-block;width:12px;height:3px;background:#f97316;border-radius:2px;margin-right:5px;vertical-align:middle"></span>Peu favorable</span>' +
  '<span style="margin-left:auto;font-style:italic;font-size:10px">Couleur barre = température moyenne du mois</span>';""",
  """legendEl.innerHTML = '<span><span style="display:inline-block;width:12px;height:3px;background:#1a7a4a;border-radius:2px;margin-right:5px;vertical-align:middle"></span>'+T.badgeRec+'</span>' +
  '<span><span style="display:inline-block;width:12px;height:3px;background:'+CFG.avoidColor+';border-radius:2px;margin-right:5px;vertical-align:middle"></span>'+T.badgeAvoid+'</span>' +
  '<span style="margin-left:auto;font-style:italic;font-size:10px">'+T.legendBarColor+'</span>';""",
  'legend block')

# Annual note
R("""document.getElementById('ann-note').innerHTML = '<strong>Profil climatique</strong> · moyenne 10 ans (archive Open-Meteo) · les mois marqués <span style="background:#dbeafe;color:#1e40af;font-size:10px;font-weight:700;padding:1px 5px;border-radius:3px">Tendance ECMWF</span> intègrent une correction par le modèle saisonnier ECMWF. Valeurs indicatives.';""",
  "document.getElementById('ann-note').innerHTML = T.annualNote;", 'annual note')

# ══════════════════════════════════════════════════════════════════════════════
# STEP 30: Narrative
# ══════════════════════════════════════════════════════════════════════════════

R("var MNAMES = ['janvier','février','mars','avril','mai','juin','juillet','août','septembre','octobre','novembre','décembre'];",
  "var MNAMES = T.monthsLower;", 'months lower')

R("var ucLabel = {'plage':'aller à la plage','ski':'faire du ski','general':'partir'}[uc||'general'] || 'partir';",
  "var ucLabel = {'plage':T.narBeach,'ski':T.narSki,'general':T.narGeneral}[uc||'general'] || T.narGeneral;", 'nar uc label')

R("' <strong>Meilleur mois : '", "' <strong>'+T.narBestMonth+' '", 'nar best month')

# 'et' in narrative
R("if (best2.score >= 55) narrative += ' et ' + bestName2;",
  "if (best2.score >= 55) narrative += ' '+T.narAnd+' ' + bestName2;", 'nar and 1')
R("if (worst2.score < 50) narrative += ' et ' + MNAMES[worst2.idx];",
  "if (worst2.score < 50) narrative += ' '+T.narAnd+' ' + MNAMES[worst2.idx];", 'nar and 2')

R("' · Fenêtre favorable : <strong>'", "' · '+T.narWindow+' <strong>'", 'nar window', count=0)
if 'Fenêtre favorable' in core:
    R("' \u00b7 Fen\u00eatre favorable : <strong>'", "' · '+T.narWindow+' <strong>'", 'nar window lit', count=0)

R("' mois</strong>'", "' '+T.narMonths+'</strong>'", 'nar months')

R("' · Éviter : <span style=\"color:#ef4444;font-weight:700\">'",
  "' · '+T.narAvoid+' <span style=\"color:#ef4444;font-weight:700\">'", 'nar avoid', count=0)
if 'Éviter' in core:
    R("' \u00b7 \u00c9viter : <span style=\"color:#ef4444;font-weight:700\">'",
      "' · '+T.narAvoid+' <span style=\"color:#ef4444;font-weight:700\">'", 'nar avoid lit', count=0)

R("Math.round(bestData.avgTmax) + '°C max · ' + bestData.rainPct + '% pluie'",
  "fmtTemp(bestData.avgTmax) + ' max · ' + bestData.rainPct + '% ' + T.wordRain", 'nar stats')

# ══════════════════════════════════════════════════════════════════════════════
# STEP 31: Use case names in tooltip area
# ══════════════════════════════════════════════════════════════════════════════

R("var ucName = {plage:'Plage',ski:'Ski',general:'Météo générale'}[uc] || uc;",
  "var ucName = {plage:T.ucBeach,ski:T.ucSki,general:T.ucGeneral}[uc] || uc;", 'uc names tooltip')

# ══════════════════════════════════════════════════════════════════════════════
# STEP 32: Translate FR-only comments to neutral
# ══════════════════════════════════════════════════════════════════════════════

core = core.replace(
    "// Scores de référence extraits des fiches destination (83 destinations)",
    "// Reference scores from destination pages")
core = core.replace(
    "// Utilisés par la vue 12 mois pour cohérence exacte avec les fiches",
    "// Used by annual view for consistency with static pages")
core = core.replace("/* ── SCORE MÉTÉO PROJET ── */", "/* ── WEATHER SCORE ── */")
core = core.replace("// ── Légende grille ──", "// ── Grid legend ──")


# ══════════════════════════════════════════════════════════════════════════════
# WRITE core.js
# ══════════════════════════════════════════════════════════════════════════════

os.makedirs(f'{ROOT}/js', exist_ok=True)
with open(f'{ROOT}/js/core.js', 'w') as f:
    f.write(core)

print(f'✅ core.js: {len(core):,} chars, {len(core.splitlines())} lines')

# ══════════════════════════════════════════════════════════════════════════════
# Verify: check for remaining French strings
# ══════════════════════════════════════════════════════════════════════════════

french_patterns = [
    'Localisation', 'Terminé', 'Erreur :', 'Données météo',
    'Prévision', 'Profil climatique', 'Tendance ECMWF',
    'Meilleur mois', 'Recommandé', 'Peu favorable',
    'Température', 'Ensoleillé', 'Pluvieux', 'Nuageux',
    'Nouvelle lune', 'Pleine lune',
    'aller à la plage', 'faire du ski',
    'Destination plage', 'Station de ski',
    'Lever soleil', 'Coucher soleil',
    "Aujourd'hui", 'Voir la météo',
    'Très chaude', 'Fraîche', 'Froide',
    'Journée très', 'Canicule', 'Journée glaciale',
    'Journée chaude', 'Belle journée', 'Journée correcte',
    'Journée difficile', 'Journée mitigée',
    'Pluie probable', "Risque d'averses",
    'Gel possible', 'Vent soutenu', 'Chaleur élevée',
    'Température fraîche', 'risque de pluie',
    'températures fraîches', 'chaleur excessive',
    'Réserver sereinement', 'Prévoir un plan',
    'Période instable', 'Bon enneigement',
    'dans la journée', 'en journée',
    'Correction saisonnière', 'tendance saisonnière',
    'Enneigement estimé', "Données d'enneigement",
    'Meilleurs mois', 'Score optimisé',
    'mm/j', "'fr-FR'",
    'Fenêtre favorable', 'Éviter',
    'Mini/Maxi', 'Vent</div>',
    'Récupération', 'Téléchargement', 'Agrégation',
    'Sélectionnez une ville', 'Choisissez une date',
    'Météo générale',
]

remaining = []
for p in french_patterns:
    if p in core:
        for i, line in enumerate(core.splitlines(), 1):
            if p in line and not line.strip().startswith('//'):
                remaining.append(f'  L{i}: "{p}" in: {line.strip()[:100]}')
                break

if remaining:
    print(f'\n⚠ {len(remaining)} French strings still in core.js:')
    for r in remaining:
        print(r)
else:
    print('✅ No remaining French strings detected')

if errors:
    print(f'\n❌ {len(errors)} replacement errors:')
    for e in errors:
        print(f'  {e}')

if warnings:
    print(f'\n⚠ {len(warnings)} warnings:')
    for w in warnings:
        print(f'  {w}')

if not errors:
    print('\n✅ All replacements successful')


# ══════════════════════════════════════════════════════════════════════════════
# BUILD i18n FILES
# ══════════════════════════════════════════════════════════════════════════════

# Extract SEA data from originals for i18n files
def extract_block(src, varname):
    m = re.search(rf'var {varname}\s*=\s*(\{{.*?\n\}});', src, re.DOTALL)
    return m.group(1) if m else '{}'

fr_sea_name_map = extract_block(fr, 'SEA_NAME_MAP')
en_sea_name_map = extract_block(en, 'SEA_NAME_MAP_EN')
fr_sea_clim_data = extract_block(fr, 'SEA_CLIM_DATA')
en_sea_clim_data = extract_block(en, 'SEA_CLIM_DATA_EN')
fr_country_short = extract_block(fr, 'COUNTRY_NAMES_SHORT')
en_country_short = extract_block(en, 'COUNTRY_NAMES_SHORT')
fr_country_full = extract_block(fr, 'COUNTRY_NAMES')
en_country_full = extract_block(en, 'COUNTRY_NAMES')

# ── i18n-fr.js ──

FR_I18N = f"""// BestDateWeather — i18n-fr.js (French locale)
window.BDW_T = {{
 // Placeholders
 phBeach: 'Destination plage…',
 phSki: 'Station de ski…',
 phDefault: 'Paris, Barcelone, Tokyo…',

 // Weather conditions
 storm: 'Orage', snow: 'Neige', rain: 'Pluie', showers: 'Averses',
 clearNight: 'Nuit claire', cloudyNight: 'Nuit nuageuse',
 heavyRain: 'Fortes pluies', lightRain: 'Pluie légère',
 fog: 'Brouillard', overcast: 'Couvert',
 partlyCloudy: 'Partiellement nuageux', sunny: 'Ensoleillé',

 // Moon phases
 moonNew: 'Nouvelle lune', moonWaxCrescent: 'Croissant croissant',
 moonFirstQ: 'Premier quartier', moonWaxGibbous: 'Gibbeuse croissante',
 moonFull: 'Pleine lune', moonWanGibbous: 'Gibbeuse décroissante',
 moonLastQ: 'Dernier quartier', moonWanCrescent: 'Croissant décroissant',

 // Sunrise/Sunset
 sunrise: 'Lever soleil', sunset: 'Coucher soleil',

 // Time modes
 modeToday: "Aujourd'hui \\u2014 météo en direct",
 modeLive: 'Prévision météo réelle',
 modeEcmwf: 'Tendance ECMWF \\u2014 indicatif',
 modeClimate: 'Profil climatique historique',
 checkWeather: 'Voir la météo',

 // Snow alerts
 snowAltLow: '❄ Altitude {{e}}m \\u2014 trop basse pour évaluer l\\'enneigement',
 snowElevAt: ' à {{e}}m',
 snowEst: '❄ Enneigement estimé : {{d}} cm{{e}} · mesure Open-Meteo (point géographique, non domaine skiable)',
 snowNA: '❄ Données d\\'enneigement indisponibles pour cette date',
 snowExpected: '❄️ Neige prévue',
 snowCmTotal: ' cm au total',
 snowLikely: '❄️ Neige probable',
 snowHoursBelow: 'h de précipitations sous 2°C',
 snowPossible: '❄️ Neige possible',
 snowNearFreezing: ' · températures proches du gel avec précipitations',
 duringDay: ' · en journée',

 // Sea temperature
 seaVeryWarm: 'Très chaude', seaWarm: 'Chaude · baignade agréable',
 seaPleasant: 'Agréable', seaCool: 'Fraîche',
 seaCold: 'Froide', seaVeryCold: 'Très froide',
 seaLabel: '🌊 Mer', seaLabelSeasonal: '🌊 Mer (norm. sais.)',

 // Hero titles
 heroVeryHot: 'Journée très chaude', heroVeryHotSub: 'Chaleur intense · peu de pluie',
 heroHotDay: 'Journée chaude', heroHotDaySub: 'Chaud · ensoleillé',
 heroColdDay: 'Journée froide', heroColdDaySub: 'Froid · peu de précipitations',
 heroIdealDay: 'Belle journée', heroIdealDaySub: 'Ensoleillé · peu de pluie',
 heroGoodDay: 'Journée correcte', heroGoodDaySub: 'Conditions acceptables',
 heroVeryRainy: 'Journée très pluvieuse', heroVeryRainySub: 'Pluie fréquente',
 heroCanicule: 'Canicule', heroChaniculeSub: 'Chaleur extrême · risque sanitaire',
 heroFreezing: 'Journée glaciale', heroFreezingSub: 'Gel possible · conditions difficiles',
 heroDifficult: 'Journée difficile', heroDifficultSub: 'Pluie · températures fraîches',
 heroMixed: 'Journée mitigée', heroMixedSub: "Nuageux · risque d'averses",

 // Stats
 statMinMax: 'Mini/Maxi', statRain: 'Pluie', statWind: 'Vent',
 duringDayShort: 'dans la journée',

 // Temperature frequency
 tempFreq: 'Température dans ±2{{u}} de {{t}}° \\u2014 {{p}}% des années à cette date',

 // Seasonal
 seasonalCorrection: 'Correction saisonnière :',
 seasonalSuffix: ' · tendance saisonnière',
 wordRain: 'pluie',

 // Score verdicts
 scIdeal: 'Idéal', scVeryGood: 'Très favorable', scGood: 'Favorable',
 scPoor: 'Peu favorable', scBad: 'Conditions défavorables',

 // Score actions — ski
 actGoodSnow: 'Bon enneigement probable',
 actCautionThaw: 'Vigilance \\u2014 redoux possible',
 actBadSnow: 'Enneigement insuffisant probable',

 // Score actions — beach
 actOptimalSwim: 'Température optimale pour la baignade',
 actCautionBeach: 'Attention',
 actCautionBeachFull: 'Eau fraîche ou conditions instables',
 actPoorBeach: 'Peu adapté',
 actPoorBeachFull: 'Température insuffisante ou conditions défavorables',

 // Score actions — general
 actBookOk: 'Réserver sereinement',
 actResidual: ' résiduel',
 actPlanB: 'Prévoir un plan B',
 actPlanBFull: 'Conditions variables \\u2014 prévoir un plan B',
 actUnstable: 'Période instable',

 // Score drivers
 drvRain: 'risque de pluie élevé', drvCold: 'températures fraîches',
 drvHotBeach: 'chaleur excessive', drvHotGen: 'chaleur élevée',
 drvWind: 'vent fréquent',

 // Risks
 riskRainLikely: 'Pluie probable ({{p}}%)',
 riskShowers: "Risque d'averses ({{p}}%)",
 riskCoolTemp: 'Température fraîche ({{t}})',
 riskHighHeat: 'Chaleur élevée ({{t}})',
 riskWind: 'Vent soutenu ({{w}})',
 riskNone: 'Aucun risque majeur identifié',
 riskPrefix: 'Risque : ',

 // Chips
 chipRain: 'Pluie', chipPrecip: 'Précip.', chipTemp: 'Temp.',
 chipWind: 'Vent', chipSnow: 'Neige', chipHumidity: 'Humidité',
 spreadStable: '🌡 Stable', spreadVariable: '🌡 Variable',

 // Sky labels
 skyRainy: 'Pluvieux', skyCloudy: 'Nuageux', skyClearSky: 'Plein soleil',
 skySunny: 'Ensoleillé', skyHazy: 'Voilé', skyOvercast: 'Couvert',

 // Use cases
 ucGeneral: 'Météo générale', ucBeach: 'Plage', ucSki: 'Ski',
 ucScoreBeach: 'Score optimisé · Plage',
 ucScoreSki: 'Score optimisé · Ski',
 ucScoreGeneral: 'Score météo général',
 optimisedFor: 'Score optimisé pour :',

 // Weight tooltips
 tipRainLbl: '💧 Pluie &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;',
 tipTempLbl: '🌡 Température ',
 tipWindLbl: '💨 Vent &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;',
 tipSunLbl: '☀ Soleil &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;',
 tipIdealRange: 'Plage idéale :',

 // Months
 months: ['Janvier','Février','Mars','Avril','Mai','Juin','Juillet','Août','Septembre','Octobre','Novembre','Décembre'],
 monthsShort: ['Jan','Fév','Mar','Avr','Mai','Jun','Jul','Aoû','Sep','Oct','Nov','Déc'],
 monthsLower: ['janvier','février','mars','avril','mai','juin','juillet','août','septembre','octobre','novembre','décembre'],

 // Annual view
 bestBeach: 'Meilleurs mois pour la plage',
 bestSki: 'Meilleurs mois pour le ski',
 ecmwfTrend: 'Tendance ECMWF',
 badgeRec: 'Recommandé', badgeAvoid: 'Peu favorable',
 badgeBest: '🔥 Meilleur mois',
 avgLabel: 'moy.', dayAbbr: 'j',
 legendBarColor: 'Couleur barre = température moyenne du mois',
 annualNote: '<strong>Profil climatique</strong> · moyenne 10 ans (archive Open-Meteo) · les mois marqués <span style="background:#dbeafe;color:#1e40af;font-size:10px;font-weight:700;padding:1px 5px;border-radius:3px">Tendance ECMWF</span> intègrent une correction par le modèle saisonnier ECMWF. Valeurs indicatives.',

 // Narrative
 narBeach: 'aller à la plage', narSki: 'faire du ski', narGeneral: 'partir',
 narBestMonth: 'Meilleur mois :', narAnd: 'et',
 narWindow: 'Fenêtre favorable :', narMonths: 'mois',
 narAvoid: 'Éviter :',

 // Notes
 noteLive: '<strong>Prévision réelle</strong> · données météo en temps réel, mise à jour toutes les heures.',
 noteEcmwf: '<strong>Tendance ECMWF</strong> · climatologie 10 ans corrigée par le modèle ECMWF \\u2014 indicatif, non garanti.',
 noteClimate: '<strong>Profil climatique</strong> · moyenne statistique des 10 dernières années pour cette date et ce lieu.',

 // Error / Progress
 errDate: '⚠ Choisissez une date pour votre projet.',
 errCity: '⚠ Sélectionnez une ville dans la liste déroulante pour garantir la bonne localisation.',
 errForecast: 'Prévisions indisponibles',
 errDataReason: 'Données météo indisponibles pour cette destination ({{r}})',
 errData: 'Données météo indisponibles pour cette destination',
 errPrefix: 'Erreur : ',
 progLocating: 'Localisation…', progFound: ' trouvé…',
 progFetching: 'Prévisions météo réelles…', progDone: 'Terminé',
 progEcmwf: 'Correction ECMWF saisonnière…',
 progFetchData: 'Récupération des données…',
 progCache: 'Données en cache…', progDownload: 'Téléchargement archive…',
 progAggregation: 'Agrégation mensuelle…'
}};

window.BDW_CFG = {{
 dateLocale: 'fr-FR',
 flagBase: 'flags/',
 dataBase: '',
 avoidColor: '#f97316',
 seaNameMap: {fr_sea_name_map},
 seaClimData: {fr_sea_clim_data},
 slugNormalize: function(name) {{
  return name.toLowerCase()
   .replace(/[àâä]/g,'a').replace(/[éèêë]/g,'e').replace(/[îï]/g,'i')
   .replace(/[ôö]/g,'o').replace(/[ùûü]/g,'u').replace(/ç/g,'c')
   .replace(/[^a-z0-9 -]/g,'').trim();
 }},
 countryShort: {fr_country_short},
 countryFull: {fr_country_full}
}};
"""

with open(f'{ROOT}/js/i18n-fr.js', 'w') as f:
    f.write(FR_I18N)
print(f'✅ i18n-fr.js: {len(FR_I18N):,} chars')


# ── i18n-en.js ──

EN_I18N = f"""// BestDateWeather — i18n-en.js (English locale)
window.BDW_T = {{
 // Placeholders
 phBeach: 'Beach destination…',
 phSki: 'Ski resort…',
 phDefault: 'Paris, Barcelona, Tokyo…',

 // Weather conditions
 storm: 'Storm', snow: 'Snow', rain: 'Rain', showers: 'Showers',
 clearNight: 'Clear night', cloudyNight: 'Cloudy night',
 heavyRain: 'Heavy rain', lightRain: 'Light rain',
 fog: 'Fog', overcast: 'Overcast',
 partlyCloudy: 'Partly cloudy', sunny: 'Sunny',

 // Moon phases
 moonNew: 'New moon', moonWaxCrescent: 'Waxing crescent',
 moonFirstQ: 'First quarter', moonWaxGibbous: 'Waxing gibbous',
 moonFull: 'Full moon', moonWanGibbous: 'Waning gibbous',
 moonLastQ: 'Last quarter', moonWanCrescent: 'Waning crescent',

 // Sunrise/Sunset
 sunrise: 'Sunrise', sunset: 'Sunset',

 // Time modes
 modeToday: 'Today \\u2014 live forecast',
 modeLive: 'Live weather forecast',
 modeEcmwf: 'ECMWF Trend \\u2014 indicative',
 modeClimate: 'Historical climate profile',
 checkWeather: 'Check the weather',

 // Snow alerts
 snowAltLow: '❄ Altitude {{e}}m \\u2014 too low to assess snow cover',
 snowElevAt: ' to {{e}}m',
 snowEst: '❄ Estimated snow depth: {{d}} cm{{e}} · Open-Meteo measurement (geographic point, not ski resort)',
 snowNA: '❄ Snow depth data unavailable for this date',
 snowExpected: '❄️ Snow expected',
 snowCmTotal: ' cm total',
 snowLikely: '❄️ Snow likely',
 snowHoursBelow: 'h of precipitation below 2°C',
 snowPossible: '❄️ Snow possible',
 snowNearFreezing: ' · near-freezing temperatures with precipitation',
 duringDay: ' · during the day',

 // Sea temperature
 seaVeryWarm: 'Very warm', seaWarm: 'Warm · good for swimming',
 seaPleasant: 'Pleasant', seaCool: 'Cool',
 seaCold: 'Cold', seaVeryCold: 'Very cold',
 seaLabel: '🌊 Sea', seaLabelSeasonal: '🌊 Sea (seasonal avg.)',

 // Hero titles
 heroVeryHot: 'Very hot day', heroVeryHotSub: 'Intense heat · little rain',
 heroHotDay: 'Hot day', heroHotDaySub: 'Hot · sunny',
 heroColdDay: 'Cold day', heroColdDaySub: 'Cold · little rain',
 heroIdealDay: 'Ideal day', heroIdealDaySub: 'Sunny · little rain',
 heroGoodDay: 'Good day', heroGoodDaySub: 'Acceptable conditions',
 heroVeryRainy: 'Very rainy day', heroVeryRainySub: 'Frequent rain',
 heroCanicule: 'Canicule', heroChaniculeSub: 'Extreme heat · health risk',
 heroFreezing: 'Freezing day', heroFreezingSub: 'Possible frost · difficult conditions',
 heroDifficult: 'Difficult day', heroDifficultSub: 'Rain · cool temperatures',
 heroMixed: 'Mixed day', heroMixedSub: 'Cloudy · possible showers',

 // Stats
 statMinMax: 'Min/Max', statRain: 'Rain', statWind: 'Wind',
 duringDayShort: 'during the day',

 // Temperature frequency
 tempFreq: 'Temperature within ±2{{u}} of {{t}}° \\u2014 {{p}}% of years on this date',

 // Seasonal
 seasonalCorrection: 'Seasonal correction:',
 seasonalSuffix: ' · seasonal trend',
 wordRain: 'rain',

 // Score verdicts
 scIdeal: 'Ideal', scVeryGood: 'Very favourable', scGood: 'Favourable',
 scPoor: 'Unfavourable', scBad: 'Poor conditions',

 // Score actions — ski
 actGoodSnow: 'Good snow cover likely',
 actCautionThaw: 'Caution \\u2014 thaw possible',
 actBadSnow: 'Insufficient snow cover likely',

 // Score actions — beach
 actOptimalSwim: 'Optimal temperature for swimming',
 actCautionBeach: 'Caution',
 actCautionBeachFull: 'Cool water or unstable conditions',
 actPoorBeach: 'Poor fit',
 actPoorBeachFull: 'Insufficient temperature or poor conditions',

 // Score actions — general
 actBookOk: 'Book with confidence',
 actResidual: '',
 actPlanB: 'Have a backup plan',
 actPlanBFull: 'Variable \\u2014 have a backup plan',
 actUnstable: 'Unstable period',

 // Score drivers
 drvRain: 'high rain risk', drvCold: 'cool temperatures',
 drvHotBeach: 'excessive heat', drvHotGen: 'high heat',
 drvWind: 'frequent wind',

 // Risks
 riskRainLikely: 'Rain likely ({{p}}%)',
 riskShowers: 'Possible showers ({{p}}%)',
 riskCoolTemp: 'Cool temperature ({{t}})',
 riskHighHeat: 'High heat ({{t}})',
 riskWind: 'Strong wind ({{w}})',
 riskNone: 'No major risk identified',
 riskPrefix: 'Risk: ',

 // Chips
 chipRain: 'Rain', chipPrecip: 'Precip.', chipTemp: 'Temp.',
 chipWind: 'Wind', chipSnow: 'Snow', chipHumidity: 'Humidity',
 spreadStable: '🌡 Stable', spreadVariable: '🌡 Variable',

 // Sky labels
 skyRainy: 'Rainy', skyCloudy: 'Cloudy', skyClearSky: 'Clear sky',
 skySunny: 'Sunny', skyHazy: 'Overcast', skyOvercast: 'Overcast',

 // Use cases
 ucGeneral: 'General weather', ucBeach: 'Beach', ucSki: 'Ski',
 ucScoreBeach: 'Optimised · Beach',
 ucScoreSki: 'Optimised · Ski',
 ucScoreGeneral: 'General weather score',
 optimisedFor: 'Optimised score for:',

 // Weight tooltips
 tipRainLbl: '💧 Rain &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;',
 tipTempLbl: '🌡 Temperature ',
 tipWindLbl: '💨 Wind &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;',
 tipSunLbl: '☀ Sunshine &nbsp;&nbsp;&nbsp;',
 tipIdealRange: 'Ideal range:',

 // Months
 months: ['January','February','March','April','May','June','July','August','September','October','November','December'],
 monthsShort: ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'],
 monthsLower: ['January','February','March','April','May','June','July','August','September','October','November','December'],

 // Annual view
 bestBeach: 'Best months for beach',
 bestSki: 'Best months for skiing',
 ecmwfTrend: 'ECMWF Trend',
 badgeRec: 'Recommended', badgeAvoid: 'Less favourable',
 badgeBest: '🔥 Best month',
 avgLabel: 'avg.', dayAbbr: 'd',
 legendBarColor: 'Bar colour = average monthly temperature',
 annualNote: '<strong>Climate profile</strong> · 10-year average (Open-Meteo archive) · months marked <span style="background:#dbeafe;color:#1e40af;font-size:10px;font-weight:700;padding:1px 5px;border-radius:3px">ECMWF Trend</span> include a seasonal model correction. Indicative values.',

 // Narrative
 narBeach: 'go to the beach', narSki: 'go skiing', narGeneral: 'travel',
 narBestMonth: 'Best month:', narAnd: 'and',
 narWindow: 'Best window:', narMonths: 'months',
 narAvoid: 'Avoid:',

 // Notes
 noteLive: '<strong>Live forecast</strong> · real-time weather data, updated hourly.',
 noteEcmwf: '<strong>ECMWF Trend</strong> · 10-year climatology adjusted by the ECMWF model \\u2014 indicative, not guaranteed.',
 noteClimate: '<strong>Climate profile</strong> · statistical average of the last 10 years for this date and location.',

 // Error / Progress
 errDate: '⚠ Choose a date for your project.',
 errCity: '⚠ Select a city from the dropdown to ensure correct location.',
 errForecast: 'Forecast unavailable',
 errDataReason: 'Weather data unavailable for this destination ({{r}})',
 errData: 'Weather data unavailable for this destination',
 errPrefix: 'Error: ',
 progLocating: 'Locating…', progFound: ' found…',
 progFetching: 'Fetching live forecast…', progDone: 'Done',
 progEcmwf: 'Applying ECMWF correction…',
 progFetchData: 'Fetching data…',
 progCache: 'Loading from cache…', progDownload: 'Downloading archive…',
 progAggregation: 'Monthly aggregation…'
}};

window.BDW_CFG = {{
 dateLocale: 'en-GB',
 flagBase: '../flags/',
 dataBase: '../',
 avoidColor: '#ef4444',
 seaNameMap: {en_sea_name_map},
 seaClimData: {en_sea_clim_data},
 slugNormalize: function(name) {{
  return name.toLowerCase().replace(/[^a-z0-9 -]/g,'').trim();
 }},
 countryShort: {en_country_short},
 countryFull: {en_country_full}
}};
"""

with open(f'{ROOT}/js/i18n-en.js', 'w') as f:
    f.write(EN_I18N)
print(f'✅ i18n-en.js: {len(EN_I18N):,} chars')


# ══════════════════════════════════════════════════════════════════════════════
# UPDATE HTML FILES
# ══════════════════════════════════════════════════════════════════════════════

def update_html(filepath, i18n_src, core_src):
    """Replace the big inline <script> with external file references."""
    with open(filepath) as f:
        html = f.read()

    # Find the biggest inline script
    pattern = re.compile(r'<script>(.*?)</script>', re.DOTALL)
    matches = list(pattern.finditer(html))
    biggest = max(matches, key=lambda m: len(m.group(1)))

    replacement = f'<script src="{i18n_src}"></script>\n<script src="{core_src}"></script>'
    html = html[:biggest.start()] + replacement + html[biggest.end():]

    with open(filepath, 'w') as f:
        f.write(html)

    # Count lines
    line_count = len(html.splitlines())
    print(f'✅ {filepath}: {line_count} lines (was {len(open(filepath).readlines()) if False else "?"})')
    return line_count

# index.html (FR) — i18n + core are in js/ relative to root
update_html(f'{ROOT}/index.html', 'js/i18n-fr.js', 'js/core.js')

# en/app.html (EN) — i18n + core are in ../js/ relative to en/
update_html(f'{ROOT}/en/app.html', '../js/i18n-en.js', '../js/core.js')


# ══════════════════════════════════════════════════════════════════════════════
# SUMMARY
# ══════════════════════════════════════════════════════════════════════════════

print('\n' + '='*60)
print('FACTORIZATION COMPLETE')
print('='*60)
for fpath in ['js/core.js', 'js/i18n-fr.js', 'js/i18n-en.js']:
    full = os.path.join(ROOT, fpath)
    sz = os.path.getsize(full)
    lines = len(open(full).readlines())
    print(f'  {fpath}: {sz:,} bytes, {lines} lines')

print(f'\n  Total errors: {len(errors)}')
print(f'  Total warnings: {len(warnings)}')
