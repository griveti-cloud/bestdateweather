#!/usr/bin/env python3
"""
BestDateWeather JS Factorization
=================================
Transforms FR + EN inline JS into:
  - js/core.js (shared logic, uses T.xxx for strings)
  - js/i18n-fr.js (French strings + locale config)
  - js/i18n-en.js (English strings + locale config)

Run: python3 build_js.py
"""
import re, json, os, sys

ROOT = '/home/claude/bestdateweather'

# ── Read source JS from saved originals ───────────────────────────────────────

with open('/tmp/orig_fr_main.js') as f:
    fr = f.read()
with open('/tmp/orig_en_main.js') as f:
    en = f.read()
with open('/tmp/orig_fr_hub.js') as f:
    fr_hub = f.read()
with open('/tmp/orig_en_hub.js') as f:
    en_hub = f.read()

# ── Helper ────────────────────────────────────────────────────────────────────

errors = []
def R(old, new, msg='', count=1):
    """Replace in core, verify exact count of replacements."""
    global core
    actual = core.count(old)
    if actual == 0:
        errors.append(f'NOT FOUND: {msg or old[:60]}')
        return
    if count > 0 and actual != count:
        errors.append(f'COUNT MISMATCH: expected {count}, found {actual} for: {msg or old[:60]}')
    core = core.replace(old, new, count if count > 0 else -1)

# Start from FR
core = fr

# ══════════════════════════════════════════════════════════════════════════════
# STEP 1: Add header + unit functions (from EN, missing in FR)
# ══════════════════════════════════════════════════════════════════════════════

HEADER = """// BestDateWeather — core.js
// Requires: window.BDW_T and window.BDW_CFG (from i18n-xx.js)
var T = window.BDW_T;
var CFG = window.BDW_CFG;

/* ── UNITS (°C/°F toggle) ── */
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
function fmtTemp(c) { if (c == null) return '–'; if (_units === 'us') return Math.round(c * 9/5 + 32) + '°F'; return Math.round(c) + '°C'; }
function fmtTempRaw(c) { if (c == null) return null; if (_units === 'us') return Math.round(c * 9/5 + 32); return Math.round(c); }
function fmtTempUnit() { return _units === 'us' ? '°F' : '°C'; }
function fmtWind(kmh) { if (kmh == null) return '–'; if (_units === 'us') return Math.round(kmh * 0.621371) + ' mph'; return Math.round(kmh) + ' km/h'; }
function fmtPrecip(mm) { if (mm == null) return '–'; if (_units === 'us') { var inches = mm * 0.0393701; return (inches < 0.1 ? inches.toFixed(2) : inches.toFixed(1)) + ' in'; } return mm + ' mm'; }

"""

core = HEADER + core

# ══════════════════════════════════════════════════════════════════════════════
# STEP 2: Placeholders
# ══════════════════════════════════════════════════════════════════════════════

R("plage:'Destination plage…'", "plage:T.phBeach", 'placeholder beach')
R("ski:'Station de ski…'", "ski:T.phSki", 'placeholder ski')
R("placeholders[type] || 'Paris, Barcelone, Tokyo…'", "placeholders[type] || T.phDefault", 'placeholder default')

# ══════════════════════════════════════════════════════════════════════════════
# STEP 3: Snow alerts (appear TWICE — once in live fetch callback, once in climate)
# ══════════════════════════════════════════════════════════════════════════════

# elevStr — appears twice
R("var elevStr = elev ? ' à ' + elev + 'm' : '';",
  "var elevStr = elev ? T.snowElevAt.replace('{e}', elev) : '';",
  'elevStr', count=2)

# Alt low — appears twice
R("_sdEl2.textContent = '❄ Altitude ' + elev + 'm — trop basse pour évaluer l\\'enneigement'",
  "_sdEl2.textContent = T.snowAltLow.replace('{e}', elev)",
  'snow alt low sdEl2')

R("_sdEl.textContent = '❄ Altitude ' + elev + 'm — trop basse pour évaluer l\\'enneigement'",
  "_sdEl.textContent = T.snowAltLow.replace('{e}', elev)",
  'snow alt low sdEl')

# Snow est — appears twice (sdEl2 and sdEl)
R("_sdEl2.textContent = '❄ Enneigement estimé : ' + res.depth + ' cm' + elevStr + ' · mesure Open-Meteo (point géographique, non domaine skiable)'",
  "_sdEl2.textContent = T.snowEst.replace('{d}', res.depth).replace('{e}', elevStr)",
  'snow est sdEl2')

R("_sdEl.textContent = '❄ Enneigement estimé : ' + res.depth + ' cm' + elevStr + ' · mesure Open-Meteo (point géographique, non domaine skiable)'",
  "_sdEl.textContent = T.snowEst.replace('{d}', res.depth).replace('{e}', elevStr)",
  'snow est sdEl')

# Snow NA — appears twice
R("_sdEl2.textContent = '❄ Données d\\'enneigement indisponibles pour cette date'",
  "_sdEl2.textContent = T.snowNA",
  'snow NA sdEl2')
R("_sdEl.textContent = '❄ Données d\\'enneigement indisponibles pour cette date'",
  "_sdEl.textContent = T.snowNA",
  'snow NA sdEl')

# Snow forecast alerts
R("'❄️ Neige prévue' + _timeLbl + ' · ' + Math.round(_snowTotal*10)/10 + ' cm au total'",
  "T.snowExpected + _timeLbl + ' · ' + Math.round(_snowTotal*10)/10 + T.snowCmTotal",
  'snow expected')
R("'❄️ Neige probable' + _timeLbl + ' · ' + _snowHours + 'h de précipitations sous 2°C'",
  "T.snowLikely + _timeLbl + ' · ' + _snowHours + T.snowHoursBelow",
  'snow likely')
R("'❄️ Neige possible' + _timeLbl + ' · températures proches du gel avec précipitations'",
  "T.snowPossible + _timeLbl + T.snowNearFreezing",
  'snow possible')

R("return ' · en journée'", "return T.duringDay", 'during day')

# ══════════════════════════════════════════════════════════════════════════════
# STEP 4: Weather condition strings (getIcon function)
# These appear in the getIcon function, each TWICE (night path + day path)
# ══════════════════════════════════════════════════════════════════════════════

# Storm, Snow — each appears 4x (2 night + 2 day in duplicated block)
for old_str, t_key in [
    ("return 'Orage';", "return T.storm;"),
    ("return 'Neige';", "return T.snow;"),
]:
    actual = core.count(old_str)
    core = core.replace(old_str, t_key)

# Day-only weather strings (appear 2x each — duplicated code block)
for old_str, t_key in [
    ("return 'Fortes pluies';", "return T.heavyRain;"),
    ("return 'Pluie légère';", "return T.lightRain;"),
    ("return 'Brouillard';", "return T.fog;"),
    ("return 'Couvert';", "return T.overcast;"),
    ("return 'Partiellement nuageux';", "return T.partlyCloudy;"),
    ("return 'Ensoleillé';", "return T.sunny;"),
    ("return 'Nuit claire';", "return T.clearNight;"),
    ("return 'Nuit nuageuse';", "return T.cloudyNight;"),
]:
    core = core.replace(old_str, t_key)

# 'Pluie' and 'Averses' are trickier because 'Pluie' appears in many contexts
# Only replace the exact return statements
R("return 'Pluie';", "return T.rain;", 'return rain', count=0)  # multiple
R("return 'Averses';", "return T.showers;", 'return showers', count=0)

# ══════════════════════════════════════════════════════════════════════════════
# STEP 5: Moon phases
# ══════════════════════════════════════════════════════════════════════════════

for old_str, t_key in [
    ("name='Nouvelle lune'", "name=T.moonNew"),
    ("name='Croissant croissant'", "name=T.moonWaxCrescent"),
    ("name='Premier quartier'", "name=T.moonFirstQ"),
    ("name='Gibbeuse croissante'", "name=T.moonWaxGibbous"),
    ("name='Pleine lune'", "name=T.moonFull"),
    ("name='Gibbeuse décroissante'", "name=T.moonWanGibbous"),
    ("name='Dernier quartier'", "name=T.moonLastQ"),
    ("name='Croissant décroissant'", "name=T.moonWanCrescent"),
]:
    core = core.replace(old_str, t_key)

# ══════════════════════════════════════════════════════════════════════════════
# STEP 6: Sunrise/Sunset
# ══════════════════════════════════════════════════════════════════════════════

R("lblEls[i].textContent = 'Lever soleil (' + tzLabel + ')'",
  "lblEls[i].textContent = T.sunrise + ' (' + tzLabel + ')'", 'sunrise')
R("lblEls[i].textContent = 'Coucher soleil (' + tzLabel + ')'",
  "lblEls[i].textContent = T.sunset + ' (' + tzLabel + ')'", 'sunset')

# ══════════════════════════════════════════════════════════════════════════════
# STEP 7: Time mode labels
# ══════════════════════════════════════════════════════════════════════════════

R('''label.textContent = "Aujourd'hui \\u2014 m\\u00e9t\\u00e9o en direct"''',
  'label.textContent = T.modeToday', 'mode today')
# Hmm, the file might have the actual characters, not unicode escapes
# Try the actual text
if "Aujourd'hui" in core:
    R("label.textContent = \"Aujourd'hui \\u2014 météo en direct\"",
      'label.textContent = T.modeToday', 'mode today v2', count=0)
    if "Aujourd'hui" in core:
        # Try with em dash
        R("label.textContent = \"Aujourd'hui — météo en direct\"",
          'label.textContent = T.modeToday', 'mode today v3', count=0)

R("label.textContent = 'Prévision météo réelle'",
  'label.textContent = T.modeLive', 'mode live')
R("label.textContent = 'Tendance ECMWF — indicatif'",
  'label.textContent = T.modeEcmwf', 'mode ecmwf')
R("label.textContent = 'Profil climatique historique'",
  'label.textContent = T.modeClimate', 'mode climate')

# "Voir la météo" — appears 4x (once per mode)
R("span.textContent = \"Voir la météo\"", "span.textContent = T.checkWeather", 'check weather dq', count=0)
R("span.textContent = 'Voir la météo'", "span.textContent = T.checkWeather", 'check weather sq', count=0)

# ══════════════════════════════════════════════════════════════════════════════
# STEP 8: Score verdict labels
# ══════════════════════════════════════════════════════════════════════════════

R("label = 'Idéal'", "label = T.scIdeal", 'score ideal')
R("label = 'Très favorable'", "label = T.scVeryGood", 'score very good')
R("label = 'Favorable'", "label = T.scGood", 'score good')
R("label = 'Acceptable'", "label = T.scAcceptable", 'score acceptable')

# 'Peu favorable' appears as score label AND badge — be specific
R("label = 'Peu favorable'", "label = T.scPoor", 'score poor')
R("label = 'Conditions défavorables'", "label = T.scBad", 'score bad')

# Score actions
R("action = 'Bon enneigement probable'", "action = T.actGoodSnow", 'act good snow')
R("action = 'Vigilance — redoux possible'", "action = T.actCautionThaw", 'act caution thaw')
R("action = 'Température optimale pour la baignade'", "action = T.actOptimalSwim", 'act optimal swim')

R("action = driver ? 'Réserver sereinement — ' + driver + ' résiduel' : 'Réserver sereinement'",
  "action = driver ? T.actBookOk + ' — ' + driver : T.actBookOk", 'act book ok')
R("action = driver ? 'Prévoir un plan B — ' + driver : 'Conditions variables — prévoir un plan B'",
  "action = driver ? T.actPlanB + ' — ' + driver : T.actPlanBFull", 'act plan b')
R("action = driver ? 'Période instable — ' + driver : 'Période instable'",
  "action = driver ? T.actUnstable + ' — ' + driver : T.actUnstable", 'act unstable')

# Score drivers
R("rain: 'risque de pluie élevé'", "rain: T.drvRain", 'driver rain')
R("temp_cold: 'températures fraîches'", "temp_cold: T.drvCold", 'driver cold')
R("temp_hot: uc === 'plage' ? 'chaleur excessive' : 'chaleur importante'",
  "temp_hot: uc === 'plage' ? T.drvHotBeach : T.drvHotGen", 'driver hot')

R("var suffix = isSeasonal ? ' · tendance saisonnière' : ''",
  "var suffix = isSeasonal ? T.seasonalSuffix : ''", 'seasonal suffix')

# ══════════════════════════════════════════════════════════════════════════════
# STEP 9: Risk messages
# ══════════════════════════════════════════════════════════════════════════════

R("risks.push('Pluie probable (' + Math.round(avgRain) + '%)')",
  "risks.push(T.riskRainLikely.replace('{p}', Math.round(avgRain)))", 'risk rain')
R("risks.push(\"Risque d'averses\")",
  "risks.push(T.riskShowers)", 'risk showers')
R("risks.push('Vent fort — ' + Math.round(avgWind) + ' km/h')",
  "risks.push(T.riskStrongWind.replace('{w}', fmtWind(Math.round(avgWind))))", 'risk wind')
R("risks.push('Rafales — ' + Math.round(avgGust) + ' km/h')",
  "risks.push(T.riskGusts.replace('{w}', fmtWind(Math.round(avgGust))))", 'risk gusts')
R("risks.push('Journée très chaude — ' + Math.round(maxTemp) + '°C')",
  "risks.push(T.riskVeryHot.replace('{t}', fmtTemp(maxTemp)))", 'risk very hot')
R("risks.push('Froid — ' + Math.round(minTemp) + '°C minimum')",
  "risks.push(T.riskCold.replace('{t}', fmtTemp(minTemp)))", 'risk cold')
R("risks.push('Gel possible — ' + Math.round(minTemp) + '°C')",
  "risks.push(T.riskFreezing.replace('{t}', fmtTemp(minTemp)))", 'risk freezing')
R("risks.push('Fraîcheur en soirée — ' + Math.round(minTemp) + '°C')",
  "risks.push(T.riskCoolEvening.replace('{t}', fmtTemp(minTemp)))", 'risk cool evening')
R("risks.push('Risque de forte pluie — ' + avgMm.toFixed(1) + ' mm/h')",
  "risks.push(T.riskHeavyRain.replace('{mm}', fmtPrecip(parseFloat(avgMm.toFixed(1)))))", 'risk heavy rain')

# ══════════════════════════════════════════════════════════════════════════════
# STEP 10: Progress & error messages
# ══════════════════════════════════════════════════════════════════════════════

R("setP(0,'Localisation…')", "setP(0,T.progLocating)", 'prog locating')
R("setP(5,loc.name+' trouvé…')", "setP(5,loc.name+T.progFound)", 'prog found')
R("setP(30,'Prévisions météo réelles…')", "setP(30,T.progFetching)", 'prog fetching')
# setP(100,'Terminé') appears twice
R("setP(100,'Terminé')", "setP(100,T.progDone)", 'prog done', count=2)
R("setP(92,'Correction ECMWF saisonnière…')", "setP(92,T.progEcmwf)", 'prog ecmwf')

R("setAnnP(0, 'Localisation…')", "setAnnP(0, T.progLocating)", 'ann prog locating')
R("setAnnP(10, 'Récupération des données…')", "setAnnP(10, T.progFetchData)", 'ann prog fetch')
R("setAnnP(30, 'Données en cache…')", "setAnnP(30, T.progCache)", 'ann prog cache')
R("setAnnP(10, 'Téléchargement archive…')", "setAnnP(10, T.progDownload)", 'ann prog download')
# setAnnP(70, ...) appears twice
R("setAnnP(70, 'Agrégation mensuelle…')", "setAnnP(70, T.progAggregation)", 'ann prog aggregation', count=2)
R("setAnnP(100, 'Terminé')", "setAnnP(100, T.progDone)", 'ann prog done')

R("errEl.textContent='⚠ Choisissez une date pour votre projet.'", "errEl.textContent=T.errDate", 'err date')
R("errEl2.textContent = '⚠ Sélectionnez une ville dans la liste déroulante pour garantir la bonne localisation.'",
  "errEl2.textContent = T.errCity", 'err city')

# Error throws
R("throw new Error('Prévisions indisponibles')", "throw new Error(T.errForecast)", 'err forecast')
R("throw new Error('Données météo indisponibles pour cette destination (' + reason + ')')",
  "throw new Error(T.errDataReason.replace('{r}', reason))", 'err data reason')
# 'Données météo indisponibles...' without reason — appears multiple times
cnt_err = core.count("throw new Error('Données météo indisponibles pour cette destination')")
core = core.replace(
    "throw new Error('Données météo indisponibles pour cette destination')",
    "throw new Error(T.errData)")

R("errEl.textContent='Erreur : '+err.message", "errEl.textContent=T.errPrefix+err.message", 'err prefix 1')
R("err.textContent = 'Erreur : ' + e.message", "err.textContent = T.errPrefix + e.message", 'err prefix 2')

# ══════════════════════════════════════════════════════════════════════════════
# STEP 11: Date locale
# ══════════════════════════════════════════════════════════════════════════════

R("'fr-FR'", "CFG.dateLocale", 'date locale')

# ══════════════════════════════════════════════════════════════════════════════
# STEP 12: Flag & data paths
# ══════════════════════════════════════════════════════════════════════════════

R("src=\"flags/'+", "src=\"'+CFG.flagBase+'", 'flag path')
R("fetch('data/monthly.json')", "fetch(CFG.dataBase+'data/monthly.json')", 'data path')

# ══════════════════════════════════════════════════════════════════════════════
# STEP 13: SEA_NAME_MAP, SEA_CLIM_DATA, slugFromName
# ══════════════════════════════════════════════════════════════════════════════

# Replace the whole SEA_NAME_MAP block
sea_map_match = re.search(r'var SEA_NAME_MAP = \{[^}]+\};', core, re.DOTALL)
if sea_map_match:
    core = core[:sea_map_match.start()] + 'var SEA_NAME_MAP = CFG.seaNameMap;' + core[sea_map_match.end():]
else:
    errors.append('NOT FOUND: SEA_NAME_MAP block')

# Replace SEA_CLIM_DATA block — this has numeric arrays so use a different pattern
sea_clim_match = re.search(r'var SEA_CLIM_DATA = \{.*?\n\};\n', core, re.DOTALL)
if sea_clim_match:
    # Save the FR data for the i18n file
    fr_sea_clim_data = sea_clim_match.group(0)
    core = core[:sea_clim_match.start()] + 'var SEA_CLIM_DATA = CFG.seaClimData;\n' + core[sea_clim_match.end():]
else:
    errors.append('NOT FOUND: SEA_CLIM_DATA block')
    fr_sea_clim_data = ''

# Replace slugFromName function
slug_match = re.search(r'function slugFromName\(name\) \{[^}]+\}', core, re.DOTALL)
if slug_match:
    core = core[:slug_match.start()] + """function slugFromName(name) {
 var n = CFG.slugNormalize(name);
 return SEA_NAME_MAP[n] || (SEA_CLIM_DATA[n] ? n : null);
}""" + core[slug_match.end():]
else:
    errors.append('NOT FOUND: slugFromName function')

# ══════════════════════════════════════════════════════════════════════════════
# STEP 14: Sea temperature labels
# ══════════════════════════════════════════════════════════════════════════════

R("lbl:'Très chaude'", "lbl:T.seaVeryWarm", 'sea very warm')
R("lbl:'Chaude · baignade agréable'", "lbl:T.seaWarm", 'sea warm')
R("lbl:'Agréable'", "lbl:T.seaPleasant", 'sea pleasant')
R("lbl:'Fraîche'", "lbl:T.seaCool", 'sea cool')
R("lbl:'Froide'", "lbl:T.seaCold", 'sea cold')
R("lbl:'Très froide'", "lbl:T.seaVeryCold", 'sea very cold')

R("var lbl = sstResult.fallback ? '🌊 Mer (norm. sais.)' : '🌊 Mer'",
  "var lbl = sstResult.fallback ? T.seaLabelSeasonal : T.seaLabel", 'sea chip label')

# Sea temp display: use fmtTemp
R("sstResult.sst+'°C'", "fmtTemp(sstResult.sst)", 'sea temp display')

# ══════════════════════════════════════════════════════════════════════════════
# STEP 15: Sky labels in updateHero
# ══════════════════════════════════════════════════════════════════════════════

for old, new in [
    ("skyLbl='Pluvieux'", "skyLbl=T.skyRainy"),
    ("skyLbl='Plein soleil'", "skyLbl=T.skyClearSky"),
]:
    R(old, new, f'sky {new}')

# 'Nuageux' appears twice in the sky logic
core = core.replace("skyLbl='Nuageux'", "skyLbl=T.skyCloudy")

for old, new in [
    ("skyLbl='Ensoleillé'", "skyLbl=T.skySunny"),
    ("skyLbl='Voilé'", "skyLbl=T.skyHazy"),
    ("skyLbl='Couvert'", "skyLbl=T.skyOvercast"),
]:
    R(old, new, f'sky {new}')

# ══════════════════════════════════════════════════════════════════════════════
# STEP 16: Hero titles
# ══════════════════════════════════════════════════════════════════════════════

HERO_PAIRS = [
    ("title = 'Journée très chaude'", "title = T.heroVeryHot"),
    ("sub = 'Chaleur intense · peu de pluie'", "sub = T.heroVeryHotSub"),
    ("title = 'Chaud et ensoleillé'", "title = T.heroHotSunny"),
    ("sub = 'Beau temps · léger risque d\\'averses'", "sub = T.heroHotSunnySub"),
    ("title = 'Agréable et doux'", "title = T.heroWarmPleasant"),
    ("sub = 'Bon équilibre température/soleil'", "sub = T.heroWarmPleasantSub"),
    ("title = 'Temps variable'", "title = T.heroVariable"),
    ("sub = 'Alternance soleil et nuages'", "sub = T.heroVariableSub"),
    ("title = 'Journée fraîche'", "title = T.heroCoolDay"),
    ("sub = 'Couvrez-vous bien'", "sub = T.heroCoolDaySub"),
    ("title = 'Journée froide'", "title = T.heroColdDay"),
    ("sub = 'Températures basses · habillez-vous chaudement'", "sub = T.heroColdDaySub"),
    ("title = 'Journée très pluvieuse'", "title = T.heroVeryRainy"),
    ("sub = 'Pluie fréquente'", "sub = T.heroVeryRainySub"),
    ("title = 'Canicule et orages'", "title = T.heroHeatStorm"),
    ("sub = 'Chaleur extrême avec risque d\\'orages'", "sub = T.heroHeatStormSub"),
    ("title = 'Journée hivernale'", "title = T.heroWinter"),
    ("sub = 'Froid et précipitations · neige possible'", "sub = T.heroWinterSub"),
]

for old, new in HERO_PAIRS:
    core = core.replace(old, new)

# ══════════════════════════════════════════════════════════════════════════════
# STEP 17: Temperature display (use fmtTempRaw instead of raw Math.round)
# ══════════════════════════════════════════════════════════════════════════════

R("(main.temp||'-')+'<sup>\\u00b0</sup>'",
  "fmtTempRaw(main.temp||0)+'<sup>\\u00b0</sup>'", 'hero temp')
R("tmin+'\\u00b0 / '+tmax+'\\u00b0 dans la journée'",
  "fmtTempRaw(tmin)+'° / '+fmtTempRaw(tmax)+'° '+T.duringDayShort", 'temp range')

# Temperature frequency
R("'Température dans ±2°C de '+Math.round(main.temp||0)+'° — '+_tf+'% des années à cette date'",
  "T.tempFreq.replace('{u}',fmtTempUnit()).replace('{t}',fmtTempRaw(main.temp||0)).replace('{p}',_tf)",
  'temp freq')

# Seasonal correction display
R("_tSign+Math.round(_to*10)/10+'°C /ECMWF'",
  "_tSign+Math.round(_to*10)/10+'° /ECMWF'", 'seasonal temp')
R("(_ro>0?'+':'')+_ro+'% pluie'",
  "(_ro>0?'+':'')+_ro+'% '+T.wordRain", 'seasonal rain')
R("_siEl.textContent='Correction saisonnière : '+_parts.join(' · ')",
  "_siEl.textContent=T.seasonalCorrection+' '+_parts.join(' · ')", 'seasonal correction label')

# Wind display
R("Math.round(wSum/rows.length)+' km/h'",
  "fmtWind(Math.round(wSum/rows.length))", 'wind display')

# ══════════════════════════════════════════════════════════════════════════════
# STEP 18: Score chips
# ══════════════════════════════════════════════════════════════════════════════

R("{ lbl: 'Pluie', val:", "{ lbl: T.chipRain, val:", 'chip rain')
R("{ lbl: 'Précip.', val:", "{ lbl: T.chipPrecip, val:", 'chip precip')

# Precip value
R("val: totalMm > 0 ? totalMm + ' mm' : '0 mm'",
  "val: fmtPrecip(totalMm > 0 ? totalMm : 0)", 'chip precip val')

R("{ lbl: 'Neige', val:", "{ lbl: T.chipSnow, val:", 'chip snow')

# ══════════════════════════════════════════════════════════════════════════════
# STEP 19: Use case labels
# ══════════════════════════════════════════════════════════════════════════════

R("general: { label:'Météo générale'", "general: { label:T.ucGeneral", 'uc general label')
R("plage:'Score optimisé · Plage', ski:'Score optimisé · Ski', general:'Météo générale'",
  "plage:T.ucScoreBeach, ski:T.ucScoreSki, general:T.ucScoreGeneral", 'uc score labels')
R("'Score météo général'", "T.ucScoreGeneral", 'uc score general')

R("{plage:'Plage',ski:'Ski',general:'Météo générale'}",
  "{plage:T.ucBeach,ski:T.ucSki,general:T.ucGeneral}", 'uc names')

# Weight tooltip labels
R("'💧 Pluie &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'", "T.tipRainLbl", 'tip rain')
R("'🌡 Température '", "T.tipTempLbl", 'tip temp')
R("'💨 Vent &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'", "T.tipWindLbl", 'tip wind')
R("'☀ Soleil &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'", "T.tipSunLbl", 'tip sun')

R("'<span style=\"opacity:.6;font-size:10px\">Plage idéale : '",
  "'<span style=\"opacity:.6;font-size:10px\">'+T.tipIdealRange+' '", 'tip ideal range')
R("cfg.tempMin + '–' + cfg.tempMax + '°C</span>'",
  "fmtTempRaw(cfg.tempMin) + '–' + fmtTempRaw(cfg.tempMax) + fmtTempUnit() + '</span>'", 'tip temp range')

# ══════════════════════════════════════════════════════════════════════════════
# STEP 20: Monthly/Annual view
# ══════════════════════════════════════════════════════════════════════════════

R("var MONTHS_FR = ['Janvier','Février','Mars','Avril','Mai','Juin','Juillet','Août','Septembre','Octobre','Novembre','Décembre'];",
  "var MONTHS_FR = T.months;", 'months full')
R("var MONTHS_SHORT = ['Jan','Fév','Mar','Avr','Mai','Jun','Jul','Aoû','Sep','Oct','Nov','Déc'];",
  "var MONTHS_SHORT = T.monthsShort;", 'months short')

R("var ucLabels = {plage:'Meilleurs mois pour la plage',ski:'Meilleurs mois pour le ski'};",
  "var ucLabels = {plage:T.bestBeach,ski:T.bestSki};", 'best months labels')
R("ucSubEl.textContent = ucLabels[uc] || 'Score optimisé pour : ' + (ucNames[uc]||uc);",
  "ucSubEl.textContent = ucLabels[uc] || T.optimisedFor + ' ' + (ucNames[uc]||uc);", 'optimised for')

# Avoid color
core = core.replace("isAvoid ? '#f97316'", "isAvoid ? CFG.avoidColor")

# Seasonal badge
R("d.seasRainDelta + '% pluie'", "d.seasRainDelta + '% ' + T.wordRain", 'seas rain delta', count=0)
core = core.replace("'Tendance ECMWF'", "T.ecmwfTrend")

# Badges
R("'<div class=\"month-badge rec\">Recommandé</div>'",
  "'<div class=\"month-badge rec\">'+T.badgeRec+'</div>'", 'badge rec')
R("'<div class=\"month-badge avoid\">Peu favorable</div>'",
  "'<div class=\"month-badge avoid\">'+T.badgeAvoid+'</div>'", 'badge avoid')
R("'<div class=\"month-best-badge\">🔥 Meilleur mois</div>'",
  "'<div class=\"month-best-badge\">'+T.badgeBest+'</div>'", 'badge best')

# Monthly card temps — use fmtTempRaw
R("d.avgTmax != null ? Math.round(d.avgTmax) + '°' : '–'",
  "d.avgTmax != null ? fmtTempRaw(d.avgTmax) + '°' : '–'", 'month tmax')
R("d.avgTmin != null ? Math.round(d.avgTmin) + '°' : '–'",
  "d.avgTmin != null ? fmtTempRaw(d.avgTmin) + '°' : '–'", 'month tmin')
R("d.avgTemp != null ? Math.round(d.avgTemp) + '°' : '–'",
  "d.avgTemp != null ? fmtTempRaw(d.avgTemp) + '°' : '–'", 'month tavg')

R("'moy. '", "T.avgLabel+' '", 'avg label')
R("d.avgPrecipMm + ' mm/j'", "fmtPrecip(d.avgPrecipMm)+'/'+T.dayAbbr", 'precip per day')

# Legend
R("'<span style=\"display:inline-block;width:12px;height:3px;background:#1a7a4a;border-radius:2px;margin-right:5px;vertical-align:middle\"></span>Recommandé</span>'",
  "'<span style=\"display:inline-block;width:12px;height:3px;background:#1a7a4a;border-radius:2px;margin-right:5px;vertical-align:middle\"></span>'+T.badgeRec+'</span>'",
  'legend rec')
R("'<span style=\"display:inline-block;width:12px;height:3px;background:#f97316;border-radius:2px;margin-right:5px;vertical-align:middle\"></span>Peu favorable</span>'",
  "'<span style=\"display:inline-block;width:12px;height:3px;background:'+CFG.avoidColor+';border-radius:2px;margin-right:5px;vertical-align:middle\"></span>'+T.badgeAvoid+'</span>'",
  'legend avoid')
R("'Couleur barre = température moyenne du mois'", "T.legendBarColor", 'legend bar color')

# Annual note
R("document.getElementById('ann-note').innerHTML = '<strong>Profil climatique</strong> · moyenne 10 ans (archive Open-Meteo) · les mois marqués <span style=\"background:#dbeafe;color:#1e40af;font-size:10px;font-weight:700;padding:1px 5px;border-radius:3px\">Tendance ECMWF</span> intègrent une correction par le modèle saisonnier ECMWF. Valeurs indicatives.';",
  "document.getElementById('ann-note').innerHTML = T.annualNote;", 'annual note')

# ══════════════════════════════════════════════════════════════════════════════
# STEP 21: Narrative
# ══════════════════════════════════════════════════════════════════════════════

R("var MNAMES = ['janvier','février','mars','avril','mai','juin','juillet','août','septembre','octobre','novembre','décembre'];",
  "var MNAMES = T.monthsLower;", 'months lower')

R("var ucLabel = {'plage':'aller à la plage','ski':'faire du ski','general':'partir'}[uc||'general'] || 'partir';",
  "var ucLabel = {'plage':T.narBeach,'ski':T.narSki,'general':T.narGeneral}[uc||'general'] || T.narGeneral;", 'nar uc label')

R("' <strong>Meilleur mois : '", "' <strong>'+T.narBestMonth+' '", 'nar best month')

# "et" in narrative — appears multiple times, replace carefully
core = core.replace(
    "if (best2.score >= 55) narrative += ' et ' + bestName2;",
    "if (best2.score >= 55) narrative += ' '+T.narAnd+' ' + bestName2;")
core = core.replace(
    "if (worst2.score < 50) narrative += ' et ' + MNAMES[worst2.idx];",
    "if (worst2.score < 50) narrative += ' '+T.narAnd+' ' + MNAMES[worst2.idx];")

R("' · Fenêtre favorable : <strong>'", "' · '+T.narWindow+' <strong>'", 'nar window')
R("' mois</strong>'", "' '+T.narMonths+'</strong>'", 'nar months')
R("' · Éviter : <span style=\"color:#ef4444;font-weight:700\">'",
  "' · '+T.narAvoid+' <span style=\"color:#ef4444;font-weight:700\">'", 'nar avoid')

R("Math.round(bestData.avgTmax) + '°C max · ' + bestData.rainPct + '% pluie'",
  "fmtTemp(bestData.avgTmax) + ' max · ' + bestData.rainPct + '% ' + T.wordRain", 'nar stats')

# ══════════════════════════════════════════════════════════════════════════════
# STEP 22: Live/Climate notes
# ══════════════════════════════════════════════════════════════════════════════

R("'<strong>Prévision réelle</strong> · données météo en temps réel, mise à jour toutes les heures.'",
  "T.noteLive", 'note live')
R("'<strong>Tendance ECMWF</strong> · climatologie 10 ans corrigée par le modèle ECMWF — indicatif, non garanti.'",
  "T.noteEcmwf", 'note ecmwf')
R("'<strong>Profil climatique</strong> · moyenne statistique des 10 dernières années pour cette date et ce lieu.'",
  "T.noteClimate", 'note climate')

# ══════════════════════════════════════════════════════════════════════════════
# STEP 23: Country names (replace whole blocks)
# ══════════════════════════════════════════════════════════════════════════════

cn_short_match = re.search(r'var COUNTRY_NAMES_SHORT = \{[^}]+\};', core, re.DOTALL)
if cn_short_match:
    core = core[:cn_short_match.start()] + 'var COUNTRY_NAMES_SHORT = CFG.countryShort;' + core[cn_short_match.end():]

cn_full_match = re.search(r'var COUNTRY_NAMES = \{[^}]+\};', core, re.DOTALL)
if cn_full_match:
    core = core[:cn_full_match.start()] + 'var COUNTRY_NAMES = CFG.countryFull;' + core[cn_full_match.end():]

# ══════════════════════════════════════════════════════════════════════════════
# STEP 24: Stats display (score strip) — use fmtTempRaw
# ══════════════════════════════════════════════════════════════════════════════

# The stats display in score strip
core = core.replace(
    "tmin+'\\u00b0/'+tmax+'\\u00b0'",
    "fmtTempRaw(tmin)+'°/'+fmtTempRaw(tmax)+'°'")

# ══════════════════════════════════════════════════════════════════════════════
# STEP 25: Comments (translate FR-only comments)
# ══════════════════════════════════════════════════════════════════════════════

core = core.replace(
    "// Scores de référence extraits des fiches destination (83 destinations)",
    "// Reference scores from destination pages")
core = core.replace(
    "// Utilisés par la vue 12 mois pour cohérence exacte avec les fiches",
    "// Used by annual view for consistency with static pages")
core = core.replace(
    "// Pre-select \"Juste la météo\" by default",
    "// Pre-select default use case")
core = core.replace(
    "// ── Légende grille ──",
    "// ── Grid legend ──")

# ══════════════════════════════════════════════════════════════════════════════
# WRITE FILES
# ══════════════════════════════════════════════════════════════════════════════

os.makedirs(f'{ROOT}/js', exist_ok=True)

with open(f'{ROOT}/js/core.js', 'w') as f:
    f.write(core)

print(f'core.js: {len(core)} chars, {len(core.splitlines())} lines')

# ── Verify: check for remaining French strings ──
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
    'mm/j', "'fr-FR'",
    'Très chaude', 'Fraîche', 'Froide',
    'Journée très', 'Canicule',
    'Pluie probable', "Risque d'averses",
    'Gel possible', 'Vent fort',
]

remaining = []
for p in french_patterns:
    if p in core:
        # Find line number
        for i, line in enumerate(core.splitlines(), 1):
            if p in line:
                remaining.append(f'  L{i}: "{p}" in: {line.strip()[:80]}')
                break

if remaining:
    print(f'\n⚠ {len(remaining)} French strings still in core.js:')
    for r in remaining:
        print(r)
else:
    print('\n✅ No remaining French strings detected')

if errors:
    print(f'\n⚠ {len(errors)} replacement issues:')
    for e in errors:
        print(f'  {e}')
else:
    print('✅ All replacements successful')

print(f'\nSaved: {ROOT}/js/core.js')
