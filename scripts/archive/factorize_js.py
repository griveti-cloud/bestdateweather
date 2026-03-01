#!/usr/bin/env python3
"""
factorize_js.py — Extract core.js + i18n-fr.js + i18n-en.js from index.html/app.html
"""
import re, json

def extract_main_js(filepath):
    with open(filepath) as f:
        c = f.read()
    scripts = re.findall(r'<script(?:\s[^>]*)?>(.+?)</script>', c, re.DOTALL)
    return max(scripts, key=len)

# ── Read both versions ──
fr = extract_main_js('index.html')
en = extract_main_js('en/app.html')

# ── Start from FR, apply transformations ──
core = fr

# ══════════════════════════════════════════════════════════════════════════════
# 1. Add LANG dependency at top + units toggle (from EN, adapted)
# ══════════════════════════════════════════════════════════════════════════════

UNITS_BLOCK = """
/* ── UNITS TOGGLE ── */
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

# Insert units block after the first line (which is typically empty or a comment)
first_newline = core.index('\n')
core = core[:first_newline+1] + UNITS_BLOCK + core[first_newline+1:]

# ══════════════════════════════════════════════════════════════════════════════
# 2. Replace hardcoded strings with LANG references
# ══════════════════════════════════════════════════════════════════════════════

replacements = []

def R(old, new, count=1):
    """Register a replacement. count=0 means replace all occurrences."""
    replacements.append((old, new, count))

# ── Placeholders ──
R("plage:'Destination plage…'", "plage:LANG.placeholders.plage")
R("ski:'Station de ski…'", "ski:LANG.placeholders.ski")
R("placeholders[type] || 'Paris, Barcelone, Tokyo…'", "placeholders[type] || LANG.placeholders.fallback")

# ── Weather labels in getLabel() ──
# Night labels
R("return 'Nuit claire'", "return LANG.weatherLabels.clearNight")
R("return 'Nuit nuageuse'", "return LANG.weatherLabels.cloudyNight")
# Day labels (order matters - replace more specific first)
R("return 'Fortes pluies'", "return LANG.weatherLabels.heavyRain")
R("return 'Pluie légère'", "return LANG.weatherLabels.lightRain")

# The getLabel function has multiple returns for same words - need careful handling
# Storm appears twice (night + day)
R("if (mm > 7 || (rain > 70 && mm > 2)) return 'Orage';\n  if (isSnowing && rain > 15) return 'Neige';\n  if (temp <= 0 && rain > 20) return 'Neige';\n  if (rain > 35 && mm >= 1.5) return 'Pluie';\n  if (rain > 20 && mm >= 0.3) return 'Averses';\n  if (sol < 5) return 'Nuit claire';\n  return 'Nuit nuageuse';",
   "if (mm > 7 || (rain > 70 && mm > 2)) return LANG.weatherLabels.storm;\n  if (isSnowing && rain > 15) return LANG.weatherLabels.snow;\n  if (temp <= 0 && rain > 20) return LANG.weatherLabels.snow;\n  if (rain > 35 && mm >= 1.5) return LANG.weatherLabels.rain;\n  if (rain > 20 && mm >= 0.3) return LANG.weatherLabels.showers;\n  if (sol < 5) return LANG.weatherLabels.clearNight;\n  return LANG.weatherLabels.cloudyNight;")

R("if (mm > 7 || (rain > 70 && mm > 2)) return 'Orage';\n  if (isSnowing && rain > 15) return 'Neige';\n  if (temp <= 0 && rain > 20) return 'Neige';\n  if (rain > 55 && mm >= 3) return 'Fortes pluies';\n  if (rain > 35 && mm >= 1.5) return 'Pluie';\n  if (rain > 20 && mm >= 0.3 && sol >= 200) return 'Averses';\n  if (rain > 20 && mm >= 0.3) return 'Pluie légère';\n  if (rain > 35) return 'Pluie';\n  if (sol < 60 && temp < 8) return 'Brouillard';\n  if (sol < 130) return 'Couvert';\n  if (sol < 420) return 'Partiellement nuageux';\n  return 'Ensoleillé';",
   "if (mm > 7 || (rain > 70 && mm > 2)) return LANG.weatherLabels.storm;\n  if (isSnowing && rain > 15) return LANG.weatherLabels.snow;\n  if (temp <= 0 && rain > 20) return LANG.weatherLabels.snow;\n  if (rain > 55 && mm >= 3) return LANG.weatherLabels.heavyRain;\n  if (rain > 35 && mm >= 1.5) return LANG.weatherLabels.rain;\n  if (rain > 20 && mm >= 0.3 && sol >= 200) return LANG.weatherLabels.showers;\n  if (rain > 20 && mm >= 0.3) return LANG.weatherLabels.lightRain;\n  if (rain > 35) return LANG.weatherLabels.rain;\n  if (sol < 60 && temp < 8) return LANG.weatherLabels.fog;\n  if (sol < 130) return LANG.weatherLabels.overcast;\n  if (sol < 420) return LANG.weatherLabels.partlyCloudy;\n  return LANG.weatherLabels.sunny;")

# ── Lunar phases ──
R("name='Nouvelle lune'", "name=LANG.lunar.newMoon")
R("name='Premier croissant'", "name=LANG.lunar.waxingCrescent")
R("name='Premier quartier'", "name=LANG.lunar.firstQuarter")
R("name='Gibbeuse croissante'", "name=LANG.lunar.waxingGibbous")
R("name='Pleine lune'", "name=LANG.lunar.fullMoon")
R("name='Gibbeuse décroissante'", "name=LANG.lunar.waningGibbous")
R("name='Dernier quartier'", "name=LANG.lunar.lastQuarter")
R("name='Croissant décroissant'", "name=LANG.lunar.waningCrescent")

# ── Astro labels ──
R("lblEls[i].textContent = 'Lever soleil (' + tzLabel + ')'", "lblEls[i].textContent = LANG.astro.sunrise + ' (' + tzLabel + ')'")
R("lblEls[i].textContent = 'Coucher soleil (' + tzLabel + ')'", "lblEls[i].textContent = LANG.astro.sunset + ' (' + tzLabel + ')'")

# ── Horizon wording ──
R("label.textContent = \"Aujourd'hui \\u2014 météo en direct\";\n  if (span) span.textContent = \"Voir la météo\";",
   "label.textContent = LANG.horizon.today.label;\n  if (span) span.textContent = LANG.horizon.today.btn;")
R("label.textContent = 'Prévision météo réelle';\n  if (span) span.textContent = 'Voir la météo';",
   "label.textContent = LANG.horizon.forecast.label;\n  if (span) span.textContent = LANG.horizon.forecast.btn;")
R("label.textContent = 'Tendance ECMWF \\u2014 indicatif';\n  if (span) span.textContent = 'Voir la météo';",
   "label.textContent = LANG.horizon.ecmwf.label;\n  if (span) span.textContent = LANG.horizon.ecmwf.btn;")
R("label.textContent = 'Profil climatique historique';\n  if (span) span.textContent = 'Voir la météo';",
   "label.textContent = LANG.horizon.climate.label;\n  if (span) span.textContent = LANG.horizon.climate.btn;")

# ── Sea comfort ──
R("""function getSeaComfortFR(sst) {
  if (sst >= 28) return {lbl:'Très chaude', color:'#ef4444'};
  if (sst >= 24) return {lbl:'Chaude · baignade agréable', color:'#f59e0b'};
  if (sst >= 20) return {lbl:'Agréable', color:'#16a34a'};
  if (sst >= 17) return {lbl:'Fraîche', color:'#0ea5e9'};
  if (sst >= 14) return {lbl:'Froide', color:'#6366f1'};
  return {lbl:'Très froide', color:'#64748b'};
 }""",
   """function getSeaComfort(sst) {
  for (var i = 0; i < LANG.seaComfort.length; i++) {
   if (sst >= LANG.seaComfort[i].min) return {lbl:LANG.seaComfort[i].lbl, color:LANG.seaComfort[i].color};
  }
  return {lbl:LANG.seaComfort[LANG.seaComfort.length-1].lbl, color:LANG.seaComfort[LANG.seaComfort.length-1].color};
 }""")

# Fix references to renamed function
R("getSeaComfortFR(", "getSeaComfort(", 0)

# ── SEA_NAME_MAP → LANG ──
# Replace the entire var declaration
sea_map_match = re.search(r'var SEA_NAME_MAP = \{[^}]+\};', core)
if sea_map_match:
    core = core[:sea_map_match.start()] + 'var SEA_NAME_MAP = LANG.seaNameMap;' + core[sea_map_match.end():]

# ── SEA_CLIM_DATA → LANG ──
sea_clim_match = re.search(r'var SEA_CLIM_DATA = \{.+?\n \};', core, re.DOTALL)
if sea_clim_match:
    core = core[:sea_clim_match.start()] + 'var SEA_CLIM_DATA = LANG.seaClimData;' + core[sea_clim_match.end():]

# ── slugFromName: use LANG normalizer ──
R("""function slugFromName(name) {
  if (!name) return null;
  var n = name.toLowerCase()
  .replace(/[àâä]/g,'a').replace(/[éèêë]/g,'e').replace(/[îï]/g,'i')
  .replace(/[ôö]/g,'o').replace(/[ùûü]/g,'u').replace(/ç/g,'c')
  .replace(/[^a-z0-9 -]/g,'').trim();
  return SEA_NAME_MAP[n] || SEA_CLIM_DATA[n] ? (SEA_NAME_MAP[n] || n) : null;""",
   """function slugFromName(name) {
  if (!name) return null;
  var n = LANG.slugNormalize(name);
  return SEA_NAME_MAP[n] || SEA_CLIM_DATA[n] ? (SEA_NAME_MAP[n] || n) : null;""")

# ── Sea chip label ──
R("var lbl = sstResult.fallback ? '🌊 Mer (norm. sais.)' : '🌊 Mer';",
   "var lbl = sstResult.fallback ? LANG.seaChip.seasonal : LANG.seaChip.normal;")

# ── Sea chip value: use fmtTemp ──
R("'<span class=\"score-chip-val\">'+sstResult.sst+'°C</span>'",
   "'<span class=\"score-chip-val\">'+fmtTemp(sstResult.sst)+'</span>'")

# ── Fetch error ──
R("throw new Error('Prévisions indisponibles')", "throw new Error(LANG.errors.forecastUnavail)")

# ── Scenario labels ──
R("if (tmax !== null && tmax >= 38) { title = 'Journée très chaude'; sub = 'Chaleur intense · peu de pluie'; }",
   "if (tmax !== null && tmax >= 38) { title = LANG.scenario.veryHot.title; sub = LANG.scenario.veryHot.sub; }")
R("else if (tmax !== null && tmax >= 32) { title = 'Journée chaude'; sub = 'Chaud · ensoleillé'; }",
   "else if (tmax !== null && tmax >= 32) { title = LANG.scenario.hot.title; sub = LANG.scenario.hot.sub; }")
R("else if (tmax !== null && tmax <= 5) { title = 'Journée froide'; sub = 'Froid · peu de précipitations'; }",
   "else if (tmax !== null && tmax <= 5) { title = LANG.scenario.cold.title; sub = LANG.scenario.cold.sub; }")
R("else if (avgRain <= 15) { title = 'Belle journée'; sub = 'Ensoleillé · peu de pluie'; }",
   "else if (avgRain <= 15) { title = LANG.scenario.nice.title; sub = LANG.scenario.nice.sub; }")
R("else { title = 'Journée correcte'; sub = 'Conditions acceptables'; }",
   "else { title = LANG.scenario.ok.title; sub = LANG.scenario.ok.sub; }")

# ── Sky labels in updateHero ──
R("if(avgRain>55)skyLbl='Pluvieux';else if(avgRain>35)skyLbl='Nuageux';else if(peakSol>500&&avgRain<20)skyLbl='Plein soleil';else if(peakSol>250&&avgRain<30)skyLbl='Ensoleillé';else if(peakSol>80)skyLbl='Voilé';else if(peakSol>15)skyLbl='Nuageux';else skyLbl='Couvert';",
   "if(avgRain>55)skyLbl=LANG.sky.rainy;else if(avgRain>35)skyLbl=LANG.sky.cloudy;else if(peakSol>500&&avgRain<20)skyLbl=LANG.sky.clearSky;else if(peakSol>250&&avgRain<30)skyLbl=LANG.sky.sunny;else if(peakSol>80)skyLbl=LANG.sky.hazy;else if(peakSol>15)skyLbl=LANG.sky.cloudy;else skyLbl=LANG.sky.overcast;")

# ── Temperature display: use fmtTemp/fmtTempRaw ──
R("document.getElementById('r-temp').innerHTML=(main.temp||'-')+'<sup>\\u00b0</sup>'",
   "document.getElementById('r-temp').innerHTML=fmtTempRaw(main.temp||0)+'<sup>°</sup>'")
R("document.getElementById('r-range').textContent=tmin+'\\u00b0 / '+tmax+'\\u00b0 dans la journée'",
   "document.getElementById('r-range').textContent=fmtTempRaw(tmin)+'° / '+fmtTempRaw(tmax)+'° '+LANG.dateRange('')")

# ── Temp freq ──
R("_tfEl.textContent='Température dans ±2°C de '+Math.round(main.temp||0)+'° — '+_tf+'% des années à cette date'",
   "_tfEl.textContent=LANG.tempFreq(fmtTempRaw(main.temp||0), _tf)")

# ── Seasonal correction text ──
R("var _tSign=_to>0?'+':'', _parts=[_tSign+Math.round(_to*10)/10+'°C /ECMWF'];\n    if(_ro!=null && Math.abs(_ro)>=3) _parts.push((_ro>0?'+':'')+_ro+'% pluie');\n    _siEl.textContent='Correction saisonnière : '+_parts.join(' · ');",
   "var _tSign=_to>0?'+':'', _parts=[_tSign+Math.round(_to*10)/10+fmtTempUnit()+' /ECMWF'];\n    if(_ro!=null && Math.abs(_ro)>=3) _parts.push((_ro>0?'+':'')+_ro+'% '+LANG.notes.rainLabel);\n    _siEl.textContent=LANG.notes.seasonal+_parts.join(' · ');")

# ── Wind display ──
R("document.getElementById('r-wind').textContent=Math.round(wSum/rows.length)+' km/h'",
   "document.getElementById('r-wind').textContent=fmtWind(Math.round(wSum/rows.length))")

# ── Snow alerts ──
R("if (h < 14) return ' · en journée';", "if (h < 14) return LANG.snow.daytime;")

# Snow expected/likely/possible - these are inline so need careful replacement
R("_snowAlert.textContent = '❄️ Neige prévue' + _timeLbl + ' · ' + Math.round(_snowTotal*10)/10 + ' cm au total'",
   "_snowAlert.textContent = LANG.snow.expected(_timeLbl, Math.round(_snowTotal*10)/10)")
R("_snowAlert.textContent = '❄️ Neige probable' + _timeLbl + ' · ' + _snowHours + 'h de précipitations sous 2°C'",
   "_snowAlert.textContent = LANG.snow.likely(_timeLbl, _snowHours)")
R("_snowAlert.textContent = '❄️ Neige possible' + _timeLbl + ' · températures proches du gel avec précipitations'",
   "_snowAlert.textContent = LANG.snow.possible(_timeLbl)")

# ── Flag prefix ──
R("'flags/'", "LANG.flagPrefix", 0)

# But be careful - don't replace inside LANG definition... we'll handle that in i18n files

# ── Date locale ──
R("'fr-FR'", "LANG.locale")

# ── Progress messages ──
R("setP(0,'Localisation…')", "setP(0,LANG.progress.locating)")
R("setP(5,loc.name+' trouvé…')", "setP(5,LANG.progress.found(loc.name))")
R("setP(30,'Prévisions météo réelles…')", "setP(30,LANG.progress.forecast)")
R("setP(92,'Correction ECMWF saisonnière…')", "setP(92,LANG.progress.ecmwf)")
R("setP(100,'Terminé')", "setP(100,LANG.progress.done)", 0)

# ── Error messages ──
R("errEl.textContent='⚠ Choisissez une date pour votre projet.'", "errEl.textContent=LANG.errors.noDate")
R("errEl2.textContent = '⚠ Sélectionnez une ville dans la liste déroulante pour garantir la bonne localisation.'",
   "errEl2.textContent = LANG.errors.noCity")
R("errEl.textContent='Erreur : '+err.message", "errEl.textContent=LANG.errors.prefix+err.message")

# ── Data unavailable errors ──
R("throw new Error('Données météo indisponibles pour cette destination (' + reason + ')')",
   "throw new Error(LANG.errors.dataUnavail(reason))")
R("throw new Error('Données météo indisponibles pour cette destination')",
   "throw new Error(LANG.errors.dataUnavail(''))", 0)

# ── Notes ──
R("showResults(rows,rows,true,'<strong>Prévision réelle</strong> · données météo en temps réel, mise à jour toutes les heures.',diffDays)",
   "showResults(rows,rows,true,LANG.notes.live,diffDays)")

R("var note=(diffDays>7&&diffDays<=210)?'<strong>Tendance ECMWF</strong> · climatologie 10 ans corrigée par le modèle ECMWF — indicatif, non garanti.':'<strong>Profil climatique</strong> · moyenne statistique des 10 dernières années pour cette date et ce lieu.';",
   "var note=(diffDays>7&&diffDays<=210)?LANG.notes.ecmwf:LANG.notes.climate;")

# ── Avoid color ──
R("'#f97316'", "LANG.avoidColor", 0)

# ── Months ──
R("var MONTHS_FR = ['Janvier','Février','Mars','Avril','Mai','Juin','Juillet','Août','Septembre','Octobre','Novembre','Décembre'];",
   "var MONTHS_FR = LANG.months;")
R("var MONTHS_SHORT = ['Jan','Fév','Mar','Avr','Mai','Jun','Jul','Aoû','Sep','Oct','Nov','Déc'];",
   "var MONTHS_SHORT = LANG.monthsShort;")

# ── Annual view labels ──
R("var ucLabels = {plage:'Meilleurs mois pour la plage',ski:'Meilleurs mois pour le ski'};",
   "var ucLabels = LANG.ucLabels;")
R("ucSubEl.textContent = ucLabels[uc] || 'Score optimisé pour : ' + (ucNames[uc]||uc);",
   "ucSubEl.textContent = ucLabels[uc] || LANG.ucFallback(ucNames[uc]||uc);")

# ── Badges ──
R("'<div class=\"month-badge rec\">Recommandé</div>'", "'<div class=\"month-badge rec\">'+LANG.badges.rec+'</div>'")
R("'<div class=\"month-badge avoid\">Peu favorable</div>'", "'<div class=\"month-badge avoid\">'+LANG.badges.avoid+'</div>'")
R("'<div class=\"month-best-badge\">🔥 Meilleur mois</div>'", "'<div class=\"month-best-badge\">'+LANG.badges.best+'</div>'")
R("'<div class=\"month-seas-badge\">Tendance ECMWF'", "'<div class=\"month-seas-badge\">'+LANG.badges.seasBadge+'")

# ── Temperature display in annual cards: use fmtTempRaw ──
R("var tmaxStr = d.avgTmax != null ? Math.round(d.avgTmax) + '°' : '–';",
   "var tmaxStr = d.avgTmax != null ? fmtTempRaw(d.avgTmax) + '°' : '–';")
R("var tminStr = d.avgTmin != null ? Math.round(d.avgTmin) + '°' : '–';",
   "var tminStr = d.avgTmin != null ? fmtTempRaw(d.avgTmin) + '°' : '–';")
R("var tempStr = d.avgTemp != null ? Math.round(d.avgTemp) + '°' : '–';",
   "var tempStr = d.avgTemp != null ? fmtTempRaw(d.avgTemp) + '°' : '–';")

R("'<div class=\"month-range\">moy. ' + tempStr + '</div>'",
   "'<div class=\"month-range\">' + LANG.avg + ' ' + tempStr + '</div>'")

# ── Precip display ──
R("'(' + d.avgPrecipMm + ' mm/j)'", "'(' + fmtPrecip(d.avgPrecipMm) + '/d)'")

# ── Seasonal rain delta ──
R("+ '% pluie'", "+ '% ' + LANG.notes.rainLabel")

# ── Legend ──
R("'<span><span style=\"display:inline-block;width:12px;height:3px;background:#1a7a4a;border-radius:2px;margin-right:5px;vertical-align:middle\"></span>Recommandé</span>'",
   "'<span><span style=\"display:inline-block;width:12px;height:3px;background:#1a7a4a;border-radius:2px;margin-right:5px;vertical-align:middle\"></span>'+LANG.legend.rec+'</span>'")
R("'<span><span style=\"display:inline-block;width:12px;height:3px;background:#f97316;border-radius:2px;margin-right:5px;vertical-align:middle\"></span>Peu favorable</span>'",
   "'<span><span style=\"display:inline-block;width:12px;height:3px;background:'+LANG.avoidColor+';border-radius:2px;margin-right:5px;vertical-align:middle\"></span>'+LANG.legend.avoid+'</span>'")
R("'<span style=\"margin-left:auto;font-style:italic;font-size:10px\">Couleur barre = température moyenne du mois</span>'",
   "'<span style=\"margin-left:auto;font-style:italic;font-size:10px\">'+LANG.legend.barNote+'</span>'")

# ── Annual note ──
R("document.getElementById('ann-note').innerHTML = '<strong>Profil climatique</strong> · moyenne 10 ans (archive Open-Meteo) · les mois marqués <span style=\"background:#dbeafe;color:#1e40af;font-size:10px;font-weight:700;padding:1px 5px;border-radius:3px\">Tendance ECMWF</span> intègrent une correction par le modèle saisonnier ECMWF. Valeurs indicatives.';",
   "document.getElementById('ann-note').innerHTML = LANG.notes.annNote;")

# ── Narrative ──
R("var MNAMES = ['janvier','février','mars','avril','mai','juin','juillet','août','septembre','octobre','novembre','décembre'];",
   "var MNAMES = LANG.monthsLower;")
R("var ucLabel = {'plage':'aller à la plage','ski':'faire du ski','general':'partir'}[uc||'general'] || 'partir';",
   "var ucLabel = LANG.ucNarrative[uc||'general'] || LANG.ucNarrative.general;")
R("var narrative = emoji + ' <strong>Meilleur mois : '", "var narrative = emoji + ' <strong>' + LANG.narrative.bestMonth + '")
R("if (best2.score >= 55) narrative += ' et ' + bestName2;",
   "if (best2.score >= 55) narrative += LANG.narrative.and + bestName2;")
R("narrative += ' · Fenêtre favorable : <strong>' + goodMonths.length + ' mois</strong>'",
   "narrative += LANG.narrative.window + '<strong>' + goodMonths.length + LANG.narrative.monthsWord + '</strong>'")
R("narrative += ' · Éviter : <span style=\"color:#ef4444;font-weight:700\">' + worstName + '</span>'",
   "narrative += LANG.narrative.avoid + '<span style=\"color:#ef4444;font-weight:700\">' + worstName + '</span>'")
R("if (worst2.score < 50) narrative += ' et ' + MNAMES[worst2.idx];",
   "if (worst2.score < 50) narrative += LANG.narrative.and + MNAMES[worst2.idx];")
R("narrative += ' · ' + Math.round(bestData.avgTmax) + '°C max · ' + bestData.rainPct + '% pluie'",
   "narrative += ' · ' + fmtTemp(bestData.avgTmax) + LANG.narrative.maxTemp + ' · ' + bestData.rainPct + LANG.narrative.rainPct")

# ── Score tooltip ──
R("var ucName = {plage:'Plage',ski:'Ski',general:'Météo générale'}[uc] || uc;",
   "var ucName = LANG.ucNames[uc] || uc;")
R("'💧 Pluie", "'" + "' + LANG.tooltipLabels.rain + '")
R("'🌡 Température", "'" + "' + LANG.tooltipLabels.temp + '")
R("'💨 Vent", "'" + "' + LANG.tooltipLabels.wind + '")
R("'☀ Soleil", "'" + "' + LANG.tooltipLabels.sun + '")
R("'<span style=\"opacity:.6;font-size:10px\">Plage idéale : ' + cfg.tempMin + '–' + cfg.tempMax + '°C</span>'",
   "'<span style=\"opacity:.6;font-size:10px\">' + LANG.tooltipIdeal(fmtTempRaw(cfg.tempMin), fmtTempRaw(cfg.tempMax)) + '</span>'")

# ── DOM-TOM names ──
# Replace the two country name maps
# First map (DOM-TOM territories)
R("'GP':'Guadeloupe','MQ':'Martinique','RE':'La Réunion','GF':'Guyane',\n  'YT':'Mayotte','PM':'Saint-Pierre-et-Miquelon','NC':'Nouvelle-Calédonie',\n  'PF':'Polynésie française','WF':'Wallis-et-Futuna','BL':'Saint-Barthélemy','MF':'Saint-Martin'\n }",
   "'GP':LANG.domTomNames.GP,'MQ':LANG.domTomNames.MQ,'RE':LANG.domTomNames.RE,'GF':LANG.domTomNames.GF,\n  'YT':LANG.domTomNames.YT,'PM':LANG.domTomNames.PM,'NC':LANG.domTomNames.NC,\n  'PF':LANG.domTomNames.PF,'WF':LANG.domTomNames.WF,'BL':LANG.domTomNames.BL,'MF':LANG.domTomNames.MF\n }")

# Second map (country names including DOM-TOM)
core_lines = core.split('\n')
# Find the countryName function's object literal  
R("'GP':'Guadeloupe','MQ':'Martinique','RE':'La Réunion','GF':'Guyane française',\n  'YT':'Mayotte','PM':'Saint-Pierre-et-Miquelon','NC':'Nouvelle-Calédonie',\n  'PF':'Polynésie française','WF':'Wallis-et-Futuna','BL':'Saint-Barthélemy',",
   "'GP':LANG.countryNames.GP,'MQ':LANG.countryNames.MQ,'RE':LANG.countryNames.RE,'GF':LANG.countryNames.GF,\n  'YT':LANG.countryNames.YT,'PM':LANG.countryNames.PM,'NC':LANG.countryNames.NC,\n  'PF':LANG.countryNames.PF,'WF':LANG.countryNames.WF,'BL':LANG.countryNames.BL,")
R("'CA':'Canada','US':'États-Unis','GB':'Royaume-Uni','DE':'Allemagne','ES':'Espagne',",
   "'CA':LANG.countryNames.CA||'Canada','US':LANG.countryNames.US||'United States','GB':LANG.countryNames.GB||'Royaume-Uni','DE':LANG.countryNames.DE||'Allemagne','ES':LANG.countryNames.ES||'Espagne',")
R("'DZ':'Algérie','SN':'Sénégal','CI':'Côte d\\'Ivoire','CM':'Cameroun'",
   "'DZ':LANG.countryNames.DZ||'Algeria','SN':LANG.countryNames.SN||'Senegal','CI':LANG.countryNames.CI||\"Côte d'Ivoire\",'CM':LANG.countryNames.CM||'Cameroun'")

# ── Snow altitude messages (appear twice - in run() for live forecast and ski use case) ──
# First occurrence
R("_sdEl2.textContent = '❄ Altitude ' + elev + 'm — trop basse pour évaluer l\\'enneigement'",
   "_sdEl2.textContent = LANG.snow.snowAltLow(elev)")
R("_sdEl2.textContent = '❄ Enneigement estimé : ' + res.depth + ' cm' + elevStr + ' · mesure Open-Meteo (point géographique, non domaine skiable)'",
   "_sdEl2.textContent = LANG.snow.snowEst(res.depth, elev)")
R("_sdEl2.textContent = '❄ Données d\\'enneigement indisponibles pour cette date'",
   "_sdEl2.textContent = LANG.snow.snowUnavail")

# Second occurrence  
R("_sdEl.textContent = '❄ Altitude ' + elev + 'm — trop basse pour évaluer l\\'enneigement'",
   "_sdEl.textContent = LANG.snow.snowAltLow(elev)")
R("_sdEl.textContent = '❄ Enneigement estimé : ' + res.depth + ' cm' + elevStr + ' · mesure Open-Meteo (point géographique, non domaine skiable)'",
   "_sdEl.textContent = LANG.snow.snowEst(res.depth, elev)")
R("_sdEl.textContent = '❄ Données d\\'enneigement indisponibles pour cette date'",
   "_sdEl.textContent = LANG.snow.snowUnavail")

# ── Hourly display: use fmtTempRaw ──
R("(r.temp!=null?r.temp+'\\u00b0':'-')",
   "(r.temp!=null?fmtTempRaw(r.temp)+'°':'-')")

# ── Progress messages for annual view ──
R("setAnnP(0, 'Localisation…')", "setAnnP(0, LANG.progress.locating)")
R("setAnnP(10, 'Récupération des données…')", "setAnnP(10, LANG.progress.fetching)")
R("setAnnP(30, 'Données en cache…')", "setAnnP(30, LANG.progress.cache)")
R("setAnnP(10, 'Téléchargement archive…')", "setAnnP(10, LANG.progress.download)")
R("setAnnP(70, 'Agrégation mensuelle…')", "setAnnP(70, LANG.progress.aggregate)", 0)
R("setAnnP(100, 'Terminé')", "setAnnP(100, LANG.progress.done)")
R("err.textContent = 'Erreur : ' + e.message", "err.textContent = LANG.errors.prefix + e.message")

# ══════════════════════════════════════════════════════════════════════════════
# 3. Apply all replacements
# ══════════════════════════════════════════════════════════════════════════════

failed = []
for old, new, count in replacements:
    occurrences = core.count(old)
    if occurrences == 0:
        failed.append(old[:60])
        continue
    if count == 0:
        core = core.replace(old, new)
    else:
        core = core.replace(old, new, count)

if failed:
    print(f"⚠ {len(failed)} replacements not found:")
    for f in failed:
        print(f"  - {f}")
else:
    print("✓ All replacements applied successfully")

# Also remove the humidity line that's in FR but not EN (buildRows rh field)
# Actually keep it - it's harmless and better to have more data

# ══════════════════════════════════════════════════════════════════════════════
# 4. Write output files
# ══════════════════════════════════════════════════════════════════════════════

with open('js/core.js', 'w') as f:
    f.write(core)
print(f"✓ js/core.js written ({len(core)} chars, {core.count(chr(10))} lines)")

# ── Check for remaining French strings ──
fr_patterns = ['Prévision', 'Localisation', 'Erreur', 'Terminé', 'Données', 'indisponible',
               'Enneigement', 'Température dans', 'Correction saisonni', 'Fenêtre favorable',
               'Meilleur mois', 'Plage idéale', 'Nouvelle lune', 'Premier quartier',
               'Coucher soleil', 'Profil climatique', 'Tendance ECMWF']
remaining = []
for pat in fr_patterns:
    if pat in core:
        # Find the line
        for i, line in enumerate(core.split('\n'), 1):
            if pat in line and 'LANG' not in line:
                remaining.append(f"L{i}: {pat} → {line.strip()[:80]}")
                break
if remaining:
    print(f"\n⚠ {len(remaining)} possibly untranslated strings remain:")
    for r in remaining:
        print(f"  {r}")
else:
    print("✓ No obvious French strings remaining in core.js")

print(f"\nDone. Check js/core.js, js/i18n-fr.js, js/i18n-en.js")
