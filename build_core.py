#!/usr/bin/env python3
"""
Transform inline JS from index.html (FR) into:
  - js/core.js (shared logic with T.xxx references)
  - js/i18n-fr.js (French strings + config)
  - js/i18n-en.js (English strings + config)

Also extracts the hub search script.
"""
import re

ROOT = '/home/claude/bestdateweather'

# ── Read source files ─────────────────────────────────────────────────────────

with open(f'{ROOT}/index.html') as f:
    fr_html = f.read()
with open(f'{ROOT}/en/app.html') as f:
    en_html = f.read()

# Extract main JS blocks
def extract_scripts(html):
    return re.findall(r'<script(?:\s[^>]*)?>(.+?)</script>', html, re.DOTALL)

fr_scripts = extract_scripts(fr_html)
en_scripts = extract_scripts(en_html)

# Script indices: 0=gtag, 1=GA config, 2=hub search, 3=main app, 4=SW, 5=UC default
fr_main = [s for s in fr_scripts if len(s) > 10000][0]
en_main = [s for s in en_scripts if len(s) > 10000][0]
fr_hub = [s for s in fr_scripts if 'dh-input' in s][0]
en_hub = [s for s in en_scripts if 'dh-input' in s][0]

# ── Build core.js from FR main ────────────────────────────────────────────────

core = fr_main

# 1. Add i18n header at the very top
HEADER = """// BestDateWeather — core.js
// Requires: i18n-fr.js or i18n-en.js loaded BEFORE this file
var T = window.BDW_T;
var CFG = window.BDW_CFG;

/* ── UNITS ── */
var _units = 'metric';

function setUnits(sys) {
 _units = sys;
 var btnM = document.getElementById('btn-metric');
 var btnU = document.getElementById('btn-us');
 if (btnM) btnM.classList.toggle('active', sys === 'metric');
 if (btnU) btnU.classList.toggle('active', sys === 'us');
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

# 2. Remove FR-only toggleDetails (it's defined differently in the flow, we keep the EN position)
# Actually keep it - it's identical logic, just positioned differently

# ── String replacements: Weather conditions ───────────────────────────────────

WEATHER_REPLACEMENTS = [
    # Night conditions
    ("return 'Nuit claire';", "return T.clearNight;"),
    ("return 'Nuit nuageuse';", "return T.cloudyNight;"),
    # Day/night shared
    ("return 'Orage';", "return T.storm;"),
    ("return 'Neige';", "return T.snow;"),
    ("return 'Fortes pluies';", "return T.heavyRain;"),
    ("return 'Pluie';", "return T.rain;"),
    ("return 'Averses';", "return T.showers;"),
    ("return 'Pluie légère';", "return T.lightRain;"),
    ("return 'Brouillard';", "return T.fog;"),
    ("return 'Couvert';", "return T.overcast;"),
    ("return 'Partiellement nuageux';", "return T.partlyCloudy;"),
    ("return 'Ensoleillé';", "return T.sunny;"),
]

for old, new in WEATHER_REPLACEMENTS:
    core = core.replace(old, new)

# ── Moon phases ───────────────────────────────────────────────────────────────

MOON_REPLACEMENTS = [
    ("name='Nouvelle lune'", "name=T.moonNew"),
    ("name='Croissant croissant'", "name=T.moonWaxCrescent"),
    ("name='Premier quartier'", "name=T.moonFirstQ"),
    ("name='Gibbeuse croissante'", "name=T.moonWaxGibbous"),
    ("name='Pleine lune'", "name=T.moonFull"),
    ("name='Gibbeuse décroissante'", "name=T.moonWanGibbous"),
    ("name='Dernier quartier'", "name=T.moonLastQ"),
    ("name='Croissant décroissant'", "name=T.moonWanCrescent"),
]

for old, new in MOON_REPLACEMENTS:
    core = core.replace(old, new)

# ── Placeholders ──────────────────────────────────────────────────────────────

core = core.replace("plage:'Destination plage…'", "plage:T.phBeach")
core = core.replace("ski:'Station de ski…'", "ski:T.phSki")
core = core.replace("placeholders[type] || 'Paris, Barcelone, Tokyo…'", "placeholders[type] || T.phDefault")

# ── Snow alerts ───────────────────────────────────────────────────────────────

core = core.replace(
    "'❄ Altitude ' + elev + 'm — trop basse pour évaluer l\\'enneigement'",
    "T.snowAltLow.replace('{e}', elev)")
# There are TWO snow blocks (one in each position)
core = core.replace(
    "'❄ Enneigement estimé : ' + res.depth + ' cm' + elevStr + ' · mesure Open-Meteo (point géographique, non domaine skiable)'",
    "T.snowEst.replace('{d}', res.depth).replace('{e}', elevStr)")
core = core.replace(
    "'❄ Données d\\'enneigement indisponibles pour cette date'",
    "T.snowNA")

core = core.replace("var elevStr = elev ? ' à ' + elev + 'm' : '';",
                     "var elevStr = elev ? T.snowElevAt.replace('{e}', elev) : '';")

# Snow forecast alerts
core = core.replace(
    "'❄️ Neige prévue' + _timeLbl + ' · ' + Math.round(_snowTotal*10)/10 + ' cm au total'",
    "T.snowExpected + _timeLbl + ' · ' + Math.round(_snowTotal*10)/10 + T.snowCmTotal")
core = core.replace(
    "'❄️ Neige probable' + _timeLbl + ' · ' + _snowHours + 'h de précipitations sous 2°C'",
    "T.snowLikely + _timeLbl + ' · ' + _snowHours + T.snowHoursBelow")
core = core.replace(
    "'❄️ Neige possible' + _timeLbl + ' · températures proches du gel avec précipitations'",
    "T.snowPossible + _timeLbl + T.snowNearFreezing")

core = core.replace("' · en journée'", "T.duringDay")

# ── Sunrise/Sunset ────────────────────────────────────────────────────────────

core = core.replace(
    "lblEls[i].textContent = 'Lever soleil (' + tzLabel + ')'",
    "lblEls[i].textContent = T.sunrise + ' (' + tzLabel + ')'")
core = core.replace(
    "lblEls[i].textContent = 'Coucher soleil (' + tzLabel + ')'",
    "lblEls[i].textContent = T.sunset + ' (' + tzLabel + ')'")

# ── Time mode labels ─────────────────────────────────────────────────────────

core = core.replace("label.textContent = \"Aujourd'hui — météo en direct\"",
                     "label.textContent = T.modeToday")
core = core.replace("label.textContent = 'Prévision météo réelle'",
                     "label.textContent = T.modeLive")
core = core.replace("label.textContent = 'Tendance ECMWF — indicatif'",
                     "label.textContent = T.modeEcmwf")
core = core.replace("label.textContent = 'Profil climatique historique'",
                     "label.textContent = T.modeClimate")
# "Voir la météo" buttons
core = core.replace("span.textContent = \"Voir la météo\"", "span.textContent = T.checkWeather")
core = core.replace("span.textContent = 'Voir la météo'", "span.textContent = T.checkWeather")

# ── Score labels ──────────────────────────────────────────────────────────────

core = core.replace("label = 'Idéal'", "label = T.scIdeal")
core = core.replace("label = 'Très favorable'", "label = T.scVeryGood")
core = core.replace("label = 'Favorable'", "label = T.scGood")
core = core.replace("label = 'Acceptable'", "label = T.scAcceptable")
core = core.replace("label = 'Peu favorable'", "label = T.scPoor")
core = core.replace("label = 'Conditions défavorables'", "label = T.scBad")

# Score actions - ski
core = core.replace("action = 'Bon enneigement probable'", "action = T.actGoodSnow")
core = core.replace("action = 'Vigilance — redoux possible'", "action = T.actCautionThaw")

# Score actions - beach
core = core.replace("action = 'Température optimale pour la baignade'", "action = T.actOptimalSwim")

# Score actions - general
core = core.replace(
    "action = driver ? 'Réserver sereinement — ' + driver + ' résiduel' : 'Réserver sereinement'",
    "action = driver ? T.actBookOk + ' — ' + driver : T.actBookOk")
core = core.replace(
    "action = driver ? 'Prévoir un plan B — ' + driver : 'Conditions variables — prévoir un plan B'",
    "action = driver ? T.actPlanB + ' — ' + driver : T.actPlanBFull")
core = core.replace(
    "action = driver ? 'Période instable — ' + driver : 'Période instable'",
    "action = driver ? T.actUnstable + ' — ' + driver : T.actUnstable")

# Score drivers
core = core.replace("rain: 'risque de pluie élevé'", "rain: T.drvRain")
core = core.replace("temp_cold: 'températures fraîches'", "temp_cold: T.drvCold")
core = core.replace(
    "temp_hot: uc === 'plage' ? 'chaleur excessive' : 'chaleur importante'",
    "temp_hot: uc === 'plage' ? T.drvHotBeach : T.drvHotGen")

# Seasonal suffix
core = core.replace("' · tendance saisonnière'", "T.seasonalSuffix")

# ── Risk messages ─────────────────────────────────────────────────────────────

RISK_REPLACEMENTS = [
    ("'Pluie probable (' + Math.round(avgRain) + '%)'", "T.riskRainLikely.replace('{p}', Math.round(avgRain))"),
    ("\"Risque d'averses\"", "T.riskShowers"),
    ("'Vent fort — ' + Math.round(avgWind) + ' km/h'", "T.riskStrongWind.replace('{w}', fmtWind(Math.round(avgWind)))"),
    ("'Rafales — ' + Math.round(avgGust) + ' km/h'", "T.riskGusts.replace('{w}', fmtWind(Math.round(avgGust)))"),
    ("'Journée très chaude — ' + Math.round(maxTemp) + '°C'", "T.riskVeryHot.replace('{t}', fmtTemp(maxTemp))"),
    ("'Froid — ' + Math.round(minTemp) + '°C minimum'", "T.riskCold.replace('{t}', fmtTemp(minTemp))"),
    ("'Gel possible — ' + Math.round(minTemp) + '°C'", "T.riskFreezing.replace('{t}', fmtTemp(minTemp))"),
    ("'Fraîcheur en soirée — ' + Math.round(minTemp) + '°C'", "T.riskCoolEvening.replace('{t}', fmtTemp(minTemp))"),
    ("'Risque de forte pluie — ' + avgMm.toFixed(1) + ' mm/h'", "T.riskHeavyRain.replace('{mm}', fmtPrecip(avgMm.toFixed(1)))"),
]

for old, new in RISK_REPLACEMENTS:
    core = core.replace(old, new)

# ── Progress & error messages ─────────────────────────────────────────────────

core = core.replace("setP(0,'Localisation…')", "setP(0,T.progLocating)")
core = core.replace("setP(5,loc.name+' trouvé…')", "setP(5,loc.name+T.progFound)")
core = core.replace("setP(30,'Prévisions météo réelles…')", "setP(30,T.progFetching)")
core = core.replace("setP(100,'Terminé')", "setP(100,T.progDone)")
core = core.replace("setP(92,'Correction ECMWF saisonnière…')", "setP(92,T.progEcmwf)")
core = core.replace("setAnnP(0, 'Localisation…')", "setAnnP(0, T.progLocating)")
core = core.replace("setAnnP(10, 'Récupération des données…')", "setAnnP(10, T.progFetchData)")
core = core.replace("setAnnP(30, 'Données en cache…')", "setAnnP(30, T.progCache)")
core = core.replace("setAnnP(10, 'Téléchargement archive…')", "setAnnP(10, T.progDownload)")
core = core.replace("setAnnP(70, 'Agrégation mensuelle…')", "setAnnP(70, T.progAggregation)")
core = core.replace("setAnnP(100, 'Terminé')", "setAnnP(100, T.progDone)")

core = core.replace("errEl.textContent='⚠ Choisissez une date pour votre projet.'",
                     "errEl.textContent=T.errDate")
core = core.replace(
    "errEl2.textContent = '⚠ Sélectionnez une ville dans la liste déroulante pour garantir la bonne localisation.'",
    "errEl2.textContent = T.errCity")
core = core.replace("throw new Error('Prévisions indisponibles')", "throw new Error(T.errForecast)")

# Multiple occurrences of data unavailable
core = core.replace(
    "throw new Error('Données météo indisponibles pour cette destination (' + reason + ')')",
    "throw new Error(T.errDataReason.replace('{r}', reason))")
core = core.replace(
    "throw new Error('Données météo indisponibles pour cette destination')",
    "throw new Error(T.errData)")
core = core.replace(
    "if (!r.ok) throw new Error('Données météo indisponibles pour cette destination')",
    "if (!r.ok) throw new Error(T.errData)")

core = core.replace("errEl.textContent='Erreur : '+err.message", "errEl.textContent=T.errPrefix+err.message")
core = core.replace("err.textContent = 'Erreur : ' + e.message", "err.textContent = T.errPrefix + e.message")

# ── Date locale ───────────────────────────────────────────────────────────────

core = core.replace("'fr-FR'", "CFG.dateLocale")

# ── Flag path ─────────────────────────────────────────────────────────────────

core = core.replace("'flags/'", "CFG.flagBase")

# ── Data path ─────────────────────────────────────────────────────────────────

core = core.replace("fetch('data/monthly.json')", "fetch(CFG.dataBase + 'data/monthly.json')")

# ── Sea name map and functions ────────────────────────────────────────────────

# Replace FR-specific variable names with generic ones
core = core.replace("var SEA_NAME_MAP = {", "var SEA_NAME_MAP = CFG.seaNameMap || {")
# Actually, let's replace the whole map with a config reference
# First, extract the full map block
sea_map_match = re.search(r'var SEA_NAME_MAP = \{.*?\};', core, re.DOTALL)
if sea_map_match:
    core = core[:sea_map_match.start()] + 'var SEA_NAME_MAP = CFG.seaNameMap;' + core[sea_map_match.end():]

# Replace SEA_CLIM_DATA similarly
sea_clim_match = re.search(r'var SEA_CLIM_DATA = \{.*?\};', core, re.DOTALL)
if sea_clim_match:
    core = core[:sea_clim_match.start()] + 'var SEA_CLIM_DATA = CFG.seaClimData;' + core[sea_clim_match.end():]

# slugFromName -> use generic name, config-based
slug_fn_match = re.search(r'function slugFromName\(name\) \{.*?^}', core, re.DOTALL | re.MULTILINE)
if slug_fn_match:
    core = core[:slug_fn_match.start()] + """function slugFromName(name) {
 var n = CFG.slugNormalize(name);
 return SEA_NAME_MAP[n] || (SEA_CLIM_DATA[n] ? n : null);
}""" + core[slug_fn_match.end():]

# fetchMarineSST -> just rename refs to use generic names
# (the function body is the same, just uses different var names)
core = core.replace('fetchMarineSST(', 'fetchMarineSST(')  # already correct
core = core.replace('renderSeaChip(sstResult)', 'renderSeaChip(sstResult)')  # already correct

# ── Sea temperature labels ────────────────────────────────────────────────────

core = core.replace("lbl:'Très chaude'", "lbl:T.seaVeryWarm")
core = core.replace("lbl:'Chaude · baignade agréable'", "lbl:T.seaWarm")
core = core.replace("lbl:'Agréable'", "lbl:T.seaPleasant")
core = core.replace("lbl:'Fraîche'", "lbl:T.seaCool")
core = core.replace("lbl:'Froide'", "lbl:T.seaCold")
core = core.replace("lbl:'Très froide'", "lbl:T.seaVeryCold")

# Sea chip label
core = core.replace("'🌊 Mer (norm. sais.)'", "T.seaLabelSeasonal")
core = core.replace("'🌊 Mer'", "T.seaLabel")

# Sea chip value - use fmtTemp
core = core.replace(
    "sstResult.sst+'°C'",
    "fmtTemp(sstResult.sst)")

# ── Sky labels in updateHero ──────────────────────────────────────────────────

SKY_REPLACEMENTS = [
    ("skyLbl='Pluvieux'", "skyLbl=T.skyRainy"),
    ("skyLbl='Nuageux'", "skyLbl=T.skyCloudy"),
    ("skyLbl='Plein soleil'", "skyLbl=T.skyClearSky"),
    ("skyLbl='Ensoleillé'", "skyLbl=T.skySunny"),
    ("skyLbl='Voilé'", "skyLbl=T.skyHazy"),
    ("skyLbl='Couvert'", "skyLbl=T.skyOvercast"),
]
for old, new in SKY_REPLACEMENTS:
    core = core.replace(old, new)

# ── Hero titles ───────────────────────────────────────────────────────────────

HERO_REPLACEMENTS = [
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

for old, new in HERO_REPLACEMENTS:
    core = core.replace(old, new)

# ── Temperature display in updateHero ─────────────────────────────────────────

# FR: (main.temp||'-')+'<sup>...'  -> use fmtTempRaw
core = core.replace(
    "(main.temp||'-')+'<sup>\\u00b0</sup>'",
    "fmtTempRaw(main.temp||0)+'<sup>\\u00b0</sup>'")

# FR: tmin+'°' / tmax+'°' dans la journée
core = core.replace(
    "tmin+'\\u00b0 / '+tmax+'\\u00b0 dans la journée'",
    "fmtTempRaw(tmin)+'° / '+fmtTempRaw(tmax)+'° '+T.duringDayShort")

# Temperature frequency
core = core.replace(
    "'Température dans ±2°C de '+Math.round(main.temp||0)+'° — '+_tf+'% des années à cette date'",
    "T.tempFreq.replace('{u}',fmtTempUnit()).replace('{t}',fmtTempRaw(main.temp||0)).replace('{p}',_tf)")

# Seasonal correction display
core = core.replace(
    "_tSign+Math.round(_to*10)/10+'°C /ECMWF'",
    "_tSign+Math.round(_to*10)/10+'° /ECMWF'")
core = core.replace(
    "(_ro>0?'+':'')+_ro+'% pluie'",
    "(_ro>0?'+':'')+_ro+'% '+T.wordRain")
core = core.replace(
    "'Correction saisonnière : '",
    "T.seasonalCorrection+' '")

# Wind display
core = core.replace(
    "Math.round(wSum/rows.length)+' km/h'",
    "fmtWind(Math.round(wSum/rows.length))")

# ── Score chip labels ─────────────────────────────────────────────────────────

core = core.replace("lbl: 'Pluie'", "lbl: T.chipRain")
core = core.replace("lbl: 'Précip.'", "lbl: T.chipPrecip")
core = core.replace("lbl: 'Neige'", "lbl: T.chipSnow")

# Precip value
core = core.replace("val: totalMm > 0 ? totalMm + ' mm' : '0 mm'", "val: fmtPrecip(totalMm > 0 ? totalMm : 0)")

# ── UC labels ─────────────────────────────────────────────────────────────────

core = core.replace(
    "general: { label:'Météo générale'",
    "general: { label:T.ucGeneral")
core = core.replace(
    "plage:'Score optimisé · Plage', ski:'Score optimisé · Ski', general:'Météo générale'",
    "plage:T.ucScoreBeach, ski:T.ucScoreSki, general:T.ucScoreGeneral")
core = core.replace(
    "'Score météo général'",
    "T.ucScoreGeneral")

# UC weights tooltip
core = core.replace(
    "var ucName = {plage:'Plage',ski:'Ski',general:'Météo générale'}[uc] || uc",
    "var ucName = {plage:T.ucBeach,ski:T.ucSki,general:T.ucGeneral}[uc] || uc")
core = core.replace("'💧 Pluie", "T.tipRain+'")
# Actually these are complex template strings, let me handle them differently
# Revert the last one
core = core.replace("T.tipRain+'", "'💧 Pluie")

# Handle the weight tooltip block more carefully - replace the labels
core = core.replace(
    "'💧 Pluie &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'",
    "T.tipRainLbl")
core = core.replace(
    "'🌡 Température '",
    "T.tipTempLbl")
core = core.replace(
    "'💨 Vent &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'",
    "T.tipWindLbl")
core = core.replace(
    "'☀ Soleil &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'",
    "T.tipSunLbl")
core = core.replace(
    "'<span style=\"opacity:.6;font-size:10px\">Plage idéale : '",
    "'<span style=\"opacity:.6;font-size:10px\">'+T.tipIdealRange+' '")
core = core.replace(
    "cfg.tempMin + '–' + cfg.tempMax + '°C</span>'",
    "fmtTempRaw(cfg.tempMin) + '–' + fmtTempRaw(cfg.tempMax) + fmtTempUnit() + '</span>'")

# ── Annual view labels ────────────────────────────────────────────────────────

core = core.replace(
    "var MONTHS_FR = ['Janvier','Février','Mars','Avril','Mai','Juin','Juillet','Août','Septembre','Octobre','Novembre','Décembre'];",
    "var MONTHS_FR = T.months;")
core = core.replace(
    "var MONTHS_SHORT = ['Jan','Fév','Mar','Avr','Mai','Jun','Jul','Aoû','Sep','Oct','Nov','Déc'];",
    "var MONTHS_SHORT = T.monthsShort;")

# Best months labels
core = core.replace(
    "var ucLabels = {plage:'Meilleurs mois pour la plage',ski:'Meilleurs mois pour le ski'};",
    "var ucLabels = {plage:T.bestBeach,ski:T.bestSki};")
core = core.replace(
    "ucSubEl.textContent = ucLabels[uc] || 'Score optimisé pour : ' + (ucNames[uc]||uc);",
    "ucSubEl.textContent = ucLabels[uc] || T.optimisedFor + ' ' + (ucNames[uc]||uc);")

# Avoid color
core = core.replace(
    "isAvoid ? '#f97316'",
    "isAvoid ? CFG.avoidColor")

# Seasonal badge
core = core.replace(
    "seasRainDelta > 0 ? '+' : '') + d.seasRainDelta + '% pluie'",
    "seasRainDelta > 0 ? '+' : '') + d.seasRainDelta + '% ' + T.wordRain")
core = core.replace(
    "'Tendance ECMWF'",
    "T.ecmwfTrend")

# Badges
core = core.replace("'Recommandé'", "T.badgeRec")
core = core.replace("'Peu favorable'", "T.badgeAvoid")
core = core.replace("'🔥 Meilleur mois'", "T.badgeBest")

# Monthly card temps - use fmtTempRaw
core = core.replace(
    "d.avgTmax != null ? Math.round(d.avgTmax) + '°' : '–'",
    "d.avgTmax != null ? fmtTempRaw(d.avgTmax) + '°' : '–'")
core = core.replace(
    "d.avgTmin != null ? Math.round(d.avgTmin) + '°' : '–'",
    "d.avgTmin != null ? fmtTempRaw(d.avgTmin) + '°' : '–'")
core = core.replace(
    "d.avgTemp != null ? Math.round(d.avgTemp) + '°' : '–'",
    "d.avgTemp != null ? fmtTempRaw(d.avgTemp) + '°' : '–'")

# "moy." label
core = core.replace("'moy. '", "T.avgLabel+' '")

# Precip in monthly card
core = core.replace(
    "d.avgPrecipMm + ' mm/j'",
    "fmtPrecip(d.avgPrecipMm) + '/'+T.dayAbbr")

# Legend
core = core.replace(
    "'>Recommandé</span>' +",
    "'>'+T.badgeRec+'</span>' +")
core = core.replace(
    "'>Peu favorable</span>'",
    "'>'+T.badgeAvoid+'</span>'")
# The last legend line about bar color
core = core.replace(
    "'Couleur barre = température moyenne du mois'",
    "T.legendBarColor")

# Annual note
core = core.replace(
    "'<strong>Profil climatique</strong> · moyenne 10 ans (archive Open-Meteo) · les mois marqués <span style=\"background:#dbeafe;color:#1e40af;font-size:10px;font-weight:700;padding:1px 5px;border-radius:3px\">Tendance ECMWF</span> intègrent une correction par le modèle saisonnier ECMWF. Valeurs indicatives.'",
    "T.annualNote")

# ── Narrative ─────────────────────────────────────────────────────────────────

core = core.replace(
    "var MNAMES = ['janvier','février','mars','avril','mai','juin','juillet','août','septembre','octobre','novembre','décembre'];",
    "var MNAMES = T.monthsLower;")

core = core.replace(
    "var ucLabel = {'plage':'aller à la plage','ski':'faire du ski','general':'partir'}[uc||'general'] || 'partir';",
    "var ucLabel = {'plage':T.narBeach,'ski':T.narSki,'general':T.narGeneral}[uc||'general'] || T.narGeneral;")

core = core.replace("' <strong>Meilleur mois : '", "' <strong>'+T.narBestMonth+' '")
core = core.replace("narrative += ' et '", "narrative += ' '+T.narAnd+' '")
core = core.replace("' · Fenêtre favorable : <strong>'", "' · '+T.narWindow+' <strong>'")
core = core.replace("' mois</strong>'", "' '+T.narMonths+'</strong>'")
core = core.replace("' · Éviter : <span style=\"color:#ef4444;font-weight:700\">'",
                     "' · '+T.narAvoid+' <span style=\"color:#ef4444;font-weight:700\">'")
# "et" in worst months
# Note: there's a second "et" for worst months
core = core.replace(
    "if (worst2.score < 50) narrative += ' et ' + MNAMES[worst2.idx];",
    "if (worst2.score < 50) narrative += ' '+T.narAnd+' ' + MNAMES[worst2.idx];")

core = core.replace(
    "Math.round(bestData.avgTmax) + '°C max · ' + bestData.rainPct + '% pluie'",
    "fmtTemp(bestData.avgTmax) + ' max · ' + bestData.rainPct + '% ' + T.wordRain")

# ── Live/Climate note strings ─────────────────────────────────────────────────

core = core.replace(
    "'<strong>Prévision réelle</strong> · données météo en temps réel, mise à jour toutes les heures.'",
    "T.noteLive")
core = core.replace(
    "'<strong>Tendance ECMWF</strong> · climatologie 10 ans corrigée par le modèle ECMWF — indicatif, non garanti.'",
    "T.noteEcmwf")
core = core.replace(
    "'<strong>Profil climatique</strong> · moyenne statistique des 10 dernières années pour cette date et ce lieu.'",
    "T.noteClimate")

# ── Country names ─────────────────────────────────────────────────────────────

# Replace the full COUNTRY_NAMES_SHORT and COUNTRY_NAMES objects with config
cn_short_match = re.search(r'var COUNTRY_NAMES_SHORT = \{.*?\};', core, re.DOTALL)
if cn_short_match:
    core = core[:cn_short_match.start()] + 'var COUNTRY_NAMES_SHORT = CFG.countryShort;' + core[cn_short_match.end():]

cn_full_match = re.search(r'var COUNTRY_NAMES = \{.*?\};', core, re.DOTALL)
if cn_full_match:
    core = core[:cn_full_match.start()] + 'var COUNTRY_NAMES = CFG.countryFull;' + core[cn_full_match.end():]

# ── Score stats labels ────────────────────────────────────────────────────────

# Stats in score strip - use fmtTempRaw  
core = core.replace(
    "tmin+'\\u00b0/'+tmax+'\\u00b0'",
    "fmtTempRaw(tmin)+'°/'+fmtTempRaw(tmax)+'°'")

# ── Final result: Write core.js ───────────────────────────────────────────────

with open(f'{ROOT}/js/core.js', 'w') as f:
    f.write(core)

print(f'core.js: {len(core)} chars ({len(core.splitlines())} lines)')

# ── Hub search script ─────────────────────────────────────────────────────────

hub_core = fr_hub.replace(
    "n+' '+(n>1?'destinations trouvées':'destination trouvée')",
    "n+' '+(n>1?T.hubFound_p:T.hubFound_s)")

with open(f'{ROOT}/js/hub-search.js', 'w') as f:
    f.write('// Hub search — requires BDW_T\nvar T = window.BDW_T;\n' + hub_core)

print(f'hub-search.js: {len(hub_core)} chars')
print('\nDone. Now create i18n files.')
PYEOF