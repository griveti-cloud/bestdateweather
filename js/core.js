// BestDateWeather — core.js
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


var IC = {
 sun: '<svg viewBox="0 0 40 40" fill="none"><circle cx="20" cy="20" r="8" fill="#f59e0b"/><g stroke="#f59e0b" stroke-width="2.2" stroke-linecap="round"><line x1="20" y1="4" x2="20" y2="9"/><line x1="20" y1="31" x2="20" y2="36"/><line x1="4" y1="20" x2="9" y2="20"/><line x1="31" y1="20" x2="36" y2="20"/><line x1="8.7" y1="8.7" x2="12.2" y2="12.2"/><line x1="27.8" y1="27.8" x2="31.3" y2="31.3"/><line x1="31.3" y1="8.7" x2="27.8" y2="12.2"/><line x1="12.2" y1="27.8" x2="8.7" y2="31.3"/></g></svg>',
 partcloud: '<svg viewBox="0 0 40 40" fill="none"><circle cx="15" cy="15" r="6" fill="#f59e0b" opacity=".9"/><g stroke="#f59e0b" stroke-width="1.8" stroke-linecap="round"><line x1="15" y1="5" x2="15" y2="8"/><line x1="5" y1="15" x2="8" y2="15"/><line x1="8.8" y1="8.8" x2="11" y2="11"/><line x1="21.2" y1="8.8" x2="19" y2="11"/></g><rect x="9" y="22" width="22" height="11" rx="5.5" fill="#93c5e8"/><ellipse cx="17" cy="22" rx="6" ry="5.5" fill="#a8d4f0"/><ellipse cx="23" cy="23" rx="5" ry="4.5" fill="#bde0f8"/></svg>',
 cloud: '<svg viewBox="0 0 40 40" fill="none"><rect x="7" y="20" width="26" height="13" rx="6.5" fill="#93a8c0"/><ellipse cx="17" cy="20" rx="8" ry="7" fill="#a8bccc"/><ellipse cx="25" cy="21" rx="7" ry="6" fill="#bcd0e0"/></svg>',
 lightrain: '<svg viewBox="0 0 40 40" fill="none"><rect x="6" y="11" width="28" height="11" rx="5.5" fill="#6a92b0"/><ellipse cx="16" cy="11" rx="8" ry="6.5" fill="#7aa2c0"/><ellipse cx="25" cy="12" rx="7" ry="5.5" fill="#8ab4d0"/><g stroke="#3b82f6" stroke-width="2.2" stroke-linecap="round"><line x1="18" y1="25" x2="16" y2="33"/></g></svg>',
 rain: '<svg viewBox="0 0 40 40" fill="none"><rect x="6" y="11" width="28" height="11" rx="5.5" fill="#6a92b0"/><ellipse cx="16" cy="11" rx="8" ry="6.5" fill="#7aa2c0"/><ellipse cx="25" cy="12" rx="7" ry="5.5" fill="#8ab4d0"/><g stroke="#3b82f6" stroke-width="2.2" stroke-linecap="round"><line x1="13" y1="25" x2="11" y2="33"/><line x1="20" y1="25" x2="18" y2="33"/><line x1="27" y1="25" x2="25" y2="33"/></g></svg>',
 heavyrain: '<svg viewBox="0 0 40 40" fill="none"><rect x="4" y="9" width="32" height="11" rx="5.5" fill="#5a7a98"/><ellipse cx="14" cy="9" rx="9" ry="7" fill="#6a8aa8"/><ellipse cx="27" cy="10" rx="9" ry="6.5" fill="#7a9ab8"/><g stroke="#2563eb" stroke-width="2.2" stroke-linecap="round"><line x1="10" y1="23" x2="8" y2="32"/><line x1="16" y1="23" x2="14" y2="32"/><line x1="22" y1="23" x2="20" y2="32"/><line x1="28" y1="23" x2="26" y2="32"/></g></svg>',
 storm: '<svg viewBox="0 0 40 40" fill="none"><rect x="3" y="7" width="34" height="12" rx="6" fill="#4a6070"/><ellipse cx="13" cy="7" rx="9" ry="7" fill="#5a7080"/><ellipse cx="28" cy="8" rx="9" ry="6.5" fill="#6a8090"/><polyline points="23,19 18,28 22,28 16,38" stroke="#f59e0b" stroke-width="2.8" stroke-linecap="round" stroke-linejoin="round" fill="none"/></svg>',
 snow: '<svg viewBox="0 0 40 40" fill="none"><rect x="6" y="11" width="28" height="11" rx="5.5" fill="#a0c4e0"/><ellipse cx="16" cy="11" rx="8" ry="6.5" fill="#b0d4f0"/><ellipse cx="25" cy="12" rx="7" ry="5.5" fill="#c0e0f8"/><g stroke="#60a0d0" stroke-width="2" stroke-linecap="round"><line x1="12" y1="26" x2="12" y2="35"/><line x1="8.5" y1="28" x2="15.5" y2="33"/><line x1="8.5" y1="33" x2="15.5" y2="28"/><line x1="20" y1="26" x2="20" y2="35"/><line x1="16.5" y1="28" x2="23.5" y2="33"/><line x1="16.5" y1="33" x2="23.5" y2="28"/></g></svg>',
 fog: '<svg viewBox="0 0 40 40" fill="none"><line x1="6" y1="12" x2="34" y2="12" stroke="#93a8c0" stroke-width="2.5" stroke-linecap="round" opacity=".9"/><line x1="8" y1="19" x2="32" y2="19" stroke="#7a94ac" stroke-width="2.5" stroke-linecap="round" opacity=".7"/><line x1="11" y1="26" x2="29" y2="26" stroke="#607888" stroke-width="2.5" stroke-linecap="round" opacity=".5"/></svg>',
 moon: '<svg viewBox="0 0 40 40" fill="none"><circle cx="29" cy="8" r="1.2" fill="#f0d080" opacity=".9"/><circle cx="34" cy="17" r=".9" fill="#f0d080" opacity=".7"/><circle cx="7" cy="11" r="1" fill="#f0d080" opacity=".5"/><circle cx="19" cy="21" r="12" fill="#d4c060"/><circle cx="24" cy="18" r="10" fill="#e8f0fc"/></svg>',
 nightcloud: '<svg viewBox="0 0 40 40" fill="none"><circle cx="33" cy="7" r="1" fill="#f0d080" opacity=".8"/><circle cx="10" cy="10" r="7" fill="#d4c060"/><circle cx="13" cy="8" r="5.8" fill="#e8f0fc"/><rect x="8" y="24" width="26" height="12" rx="6" fill="#8899b4"/><ellipse cx="18" cy="24" rx="8" ry="7" fill="#99aac4"/><ellipse cx="27" cy="25" rx="7" ry="6" fill="#aabbd4"/></svg>',
 nightrain: '<svg viewBox="0 0 40 40" fill="none"><circle cx="9" cy="9" r="6" fill="#d4c060"/><circle cx="12" cy="7" r="5" fill="#e8f0fc"/><rect x="6" y="17" width="28" height="11" rx="5.5" fill="#5a7090"/><ellipse cx="17" cy="17" rx="8" ry="6.5" fill="#6a8090"/><ellipse cx="26" cy="18" rx="7" ry="5.5" fill="#7a90a0"/><g stroke="#3b82f6" stroke-width="2.2" stroke-linecap="round"><line x1="13" y1="30" x2="11" y2="37"/><line x1="20" y1="30" x2="18" y2="37"/><line x1="27" y1="30" x2="25" y2="37"/></g></svg>',
 shower: '<svg viewBox="0 0 40 40" fill="none"><circle cx="14" cy="12" r="5.5" fill="#f59e0b" opacity=".9"/><g stroke="#f59e0b" stroke-width="1.7" stroke-linecap="round"><line x1="14" y1="3" x2="14" y2="6"/><line x1="5" y1="12" x2="8" y2="12"/><line x1="8" y1="7" x2="10" y2="9"/><line x1="20" y1="7" x2="18" y2="9"/></g><rect x="9" y="18" width="22" height="11" rx="5.5" fill="#6a92b0"/><ellipse cx="17" cy="18" rx="6" ry="5.5" fill="#7aa2c0"/><ellipse cx="23" cy="19" rx="5" ry="4.5" fill="#8ab4d0"/><g stroke="#3b82f6" stroke-width="2.2" stroke-linecap="round"><line x1="19" y1="31" x2="17" y2="37"/></g></svg>',
 nightshower:'<svg viewBox="0 0 40 40" fill="none"><circle cx="9" cy="9" r="6" fill="#d4c060"/><circle cx="12" cy="7" r="5" fill="#e8f0fc"/><rect x="6" y="17" width="28" height="11" rx="5.5" fill="#5a7090"/><ellipse cx="17" cy="17" rx="8" ry="6.5" fill="#6a8090"/><ellipse cx="26" cy="18" rx="7" ry="5.5" fill="#7a90a0"/><g stroke="#3b82f6" stroke-width="2.2" stroke-linecap="round"><line x1="20" y1="30" x2="18" y2="36"/></g></svg>',
 nightsnow: '<svg viewBox="0 0 40 40" fill="none"><circle cx="9" cy="9" r="6" fill="#d4c060"/><circle cx="12" cy="7" r="5" fill="#e8f0fc"/><rect x="6" y="17" width="28" height="11" rx="5.5" fill="#7090b0"/><ellipse cx="17" cy="17" rx="8" ry="6.5" fill="#80a0c0"/><ellipse cx="26" cy="18" rx="7" ry="5.5" fill="#90b0d0"/><g stroke="#60a0d0" stroke-width="2" stroke-linecap="round"><line x1="13" y1="31" x2="13" y2="38"/><line x1="10" y1="33.5" x2="16" y2="35.5"/><line x1="10" y1="35.5" x2="16" y2="33.5"/><line x1="22" y1="31" x2="22" y2="38"/><line x1="19" y1="33.5" x2="25" y2="35.5"/><line x1="19" y1="35.5" x2="25" y2="33.5"/></g></svg>'
};

/* QUICK FILL */
function quickFill(type) {
 currentUseCase = type;
 document.getElementById('score-block').style.display = 'block';
 // Unlock forms
 var df = document.getElementById('date-form');
 if (df) { df.classList.remove('uc-required'); }
 var aw = document.getElementById('annual-wrap');
 if (aw) { aw.classList.remove('uc-required-ann'); }
 var hint = document.getElementById('uc-hint');
 if (hint) { hint.style.display = 'none'; }
 var hintAnn = document.getElementById('uc-hint-ann');
 if (hintAnn) { hintAnn.style.display = 'none'; }
 var cityEl = document.getElementById('inp-city');
 var placeholders = {
 plage:T.phBeach,
 ski:T.phSki
 };
 cityEl.placeholder = placeholders[type] || T.phDefault;
 // Re-score instantly if results already shown
 var inAnnualMode = document.getElementById('mode-annual').classList.contains('active');
 if (inAnnualMode && _lastMonthly && _lastAnnLoc) {
 renderAnnual(_lastAnnLoc, _lastMonthly);
 } else if (!inAnnualMode && _lastRows && _lastSc) {
 computeAndRenderScore(_lastSc, _lastRows);
 // Snow depth : déclencher si switch vers ski avec résultats déjà affichés
 var _sdEl2 = document.getElementById('snow-depth-info');
 if (_sdEl2) _sdEl2.style.display = 'none';
 if (type === 'ski' && _sdEl2 && selectedLoc && window._lastYr != null) {
  fetchSnowDepth(selectedLoc.lat, selectedLoc.lon, window._lastYr, window._lastMo, window._lastDa).then(function(res) {
   if (!res) return;
   var elev = res.elevation ? Math.round(res.elevation) : null;
   if (elev && elev < 600) {
    _sdEl2.textContent = T.snowAltLow.replace('{e}', elev);
    _sdEl2.style.color = '#94a3b8';
   } else if (res.depth != null) {
    var elevStr = elev ? T.snowElevAt.replace('{e}', elev) : '';
    _sdEl2.textContent = T.snowEst.replace('{d}', res.depth).replace('{e}', elevStr);
    _sdEl2.style.color = '#6366f1';
   } else {
    _sdEl2.textContent = T.snowNA;
    _sdEl2.style.color = '#94a3b8';
   }
   _sdEl2.style.display = 'block';
  });
 }
 } else {
 if (window === window.top) { cityEl.focus(); }
 selectedLoc = null;
 }
 // Mark active pill LAST (after any recompute)
 var pills = document.querySelectorAll('.uc-pill[data-uc]');
 for (var i=0; i<pills.length; i++) {
 pills[i].classList.remove('active');
 if (pills[i].dataset.uc === type) pills[i].classList.add('active');
 }
}

function toggleDetails() {
 var btn = document.getElementById('details-toggle');
 var panel = document.getElementById('details-panel');
 var open = panel.classList.toggle('open');
 btn.classList.toggle('open', open);
 btn.setAttribute('aria-expanded', open);
 if(open)setTimeout(function(){btn.scrollIntoView({behavior:'smooth',block:'start'});},80);
}

function fillUseCase(type) { currentUseCase = type; document.getElementById("score-block").style.display = "block"; quickFill(type); }

function getIcon(h, temp, sol, rain, mm, snow, p25) {
 mm = mm || 0;
 snow = snow || 0;
 p25 = p25 != null ? p25 : temp;
 var night = sol < 15;
 var isSnowing = snow > 0.1 || (p25 != null && p25 <= 2 && mm > 0.1);
 if (night) {
 if (mm > 7 || (rain > 70 && mm > 2)) return IC.storm;
 if (isSnowing && rain > 15) return IC.nightsnow;
 if (temp <= 0 && rain > 20) return IC.nightsnow;
 if (rain > 35 && mm >= 1.5) return IC.nightrain;
 if (rain > 20 && mm >= 0.3) return IC.nightshower;
 if (sol < 5) return IC.moon;
 return IC.nightcloud;
 }
 if (mm > 7 || (rain > 70 && mm > 2)) return IC.storm;
 if (isSnowing && rain > 15) return IC.snow;
 if (temp <= 0 && rain > 20) return IC.snow;
 if (rain > 55 && mm >= 3) return IC.heavyrain;
 if (rain > 35 && mm >= 1.5) return IC.rain;
 if (rain > 20 && mm >= 0.3 && sol >= 200) return IC.shower;
 if (rain > 20 && mm >= 0.3) return IC.lightrain;
 // rain > 35% mais mm < 0.3 → pas de pluie mesurable, cascade vers sol
 if (sol < 60 && temp < 8) return IC.fog;
 if (sol < 130) return IC.cloud;
 if (sol < 420) return IC.partcloud;
 return IC.sun;
}

function getLabel(h, temp, sol, rain, mm, snow, p25) {
 mm = mm || 0; snow = snow || 0;
 p25 = p25 != null ? p25 : temp;
 var night = sol < 15;
 var isSnowing = snow > 0.1 || (p25 <= 2 && mm > 0.1);
 if (night) {
 if (mm > 7 || (rain > 70 && mm > 2)) return T.storm;
 if (isSnowing && rain > 15) return T.snow;
 if (temp <= 0 && rain > 20) return T.snow;
 if (rain > 35 && mm >= 1.5) return T.rain;
 if (rain > 20 && mm >= 0.3) return T.showers;
 if (sol < 5) return T.clearNight;
 return T.cloudyNight;
 }
 if (mm > 7 || (rain > 70 && mm > 2)) return T.storm;
 if (isSnowing && rain > 15) return T.snow;
 if (temp <= 0 && rain > 20) return T.snow;
 if (rain > 55 && mm >= 3) return T.heavyRain;
 if (rain > 35 && mm >= 1.5) return T.rain;
 if (rain > 20 && mm >= 0.3 && sol >= 200) return T.showers;
 if (rain > 20 && mm >= 0.3) return T.lightRain;
 // rain > 35% mais mm < 0.3 → pas de pluie mesurable, cascade vers sol
 if (sol < 60 && temp < 8) return T.fog;
 if (sol < 130) return T.overcast;
 if (sol < 420) return T.partlyCloudy;
 return T.sunny;
}

function pct(arr, p) {
 if (!arr || arr.length === 0) return null;
 var s = arr.slice().sort(function(a, b) { return a - b; });
 var pos = (p / 100) * (s.length - 1);
 var lo = Math.floor(pos), hi = Math.ceil(pos);
 return parseFloat((s[lo] + (s[hi] - s[lo]) * (pos - lo)).toFixed(1));
}
function cloneRow(r, overrides) {
 var out = {}, ks = Object.keys(r), os = Object.keys(overrides);
 for (var i = 0; i < ks.length; i++) out[ks[i]] = r[ks[i]];
 for (var j = 0; j < os.length; j++) out[os[j]] = overrides[os[j]];
 return out;
}
function genMain(rows) { var out = []; for (var i = 0; i < rows.length; i++) { var r = rows[i]; out.push(cloneRow(r, { temp: r.p50, sol: r.solP50 || 0 })); } return out; }

/* Générateur pseudo-aléatoire déterministe (mulberry32) */
var _seededRand = null;
function seedRand(seed) {
 var s = seed | 0;
 _seededRand = function() {
 s = Math.imul(s ^ (s >>> 15), s | 1);
 s ^= s + Math.imul(s ^ (s >>> 7), s | 61);
 return ((s ^ (s >>> 14)) >>> 0) / 4294967296;
 };
}
function seededRand() { return _seededRand ? _seededRand() : Math.random(); }
function makeSeed(lat, lon, yr, mo, da) {
 return Math.abs(Math.round(lat * 1000) * 100000 + Math.round(lon * 1000) * 100 + yr * 10000 + mo * 100 + da);
}

function genPess(rows) {
 var out = [];
 for (var i = 0; i < rows.length; i++) {
 var r = rows[i];
 out.push(cloneRow(r, { temp: r.p25 != null ? parseFloat((r.p25 - seededRand()).toFixed(1)) : r.p50, sol: Math.max(0, (r.solP25 || 0) * 0.4), rain: Math.min(100, Math.round(r.rain * 1.5 + 10)) }));
 }
 return out;
}
function genOpt(rows) {
 var out = [];
 for (var i = 0; i < rows.length; i++) {
 var r = rows[i];
 out.push(cloneRow(r, { temp: r.p75 != null ? parseFloat((r.p75 + seededRand()).toFixed(1)) : r.p50, sol: Math.min(900, (r.solP75 || 0) * 1.4), rain: Math.max(0, Math.round(r.rain * 0.35)) }));
 }
 return out;
}
function toISO(d) { var mo = d.getMonth() + 1, da = d.getDate(); return d.getFullYear() + '-' + (mo < 10 ? '0' : '') + mo + '-' + (da < 10 ? '0' : '') + da; }
function addDays(d, n) { var r = new Date(d.getTime()); r.setDate(r.getDate() + n); return r; }
function setP(p, lbl) { document.getElementById('prog-bar').style.width = p + '%'; document.getElementById('prog-pct').textContent = p + '%'; if (lbl) document.getElementById('prog-lbl').textContent = lbl; }

/* ASTRO */
function lunarPhase(year, month, day) {
 var y = year, m = month;
 if (m <= 2) { y -= 1; m += 12; }
 var A = Math.floor(y / 100), B = 2 - A + Math.floor(A / 4);
 var jd = Math.floor(365.25*(y+4716)) + Math.floor(30.6001*(m+1)) + day + B - 1524.5;
 var p = (jd - 2461057.5375) % 29.53058867;
 if (p < 0) p += 29.53058867;
 var name, svg;
 if (p < 1.85) { name=T.moonNew; svg='<svg viewBox="0 0 24 24" width="22" height="22"><circle cx="12" cy="12" r="9" fill="#c8d8f0" opacity=".25" stroke="rgba(26,31,46,.3)" stroke-width="1"/><circle cx="12" cy="12" r="9" fill="#1a2a3a" opacity=".7"/></svg>'; }
 else if (p < 7.38) { name=T.moonWaxCrescent; svg='<svg viewBox="0 0 24 24" width="22" height="22"><circle cx="12" cy="12" r="9" fill="#c8d8f0" opacity=".15"/><path d="M12 3 A9 9 0 0 1 12 21 A5 9 0 0 0 12 3 Z" fill="#f0e8a0" opacity=".9"/></svg>'; }
 else if (p < 9.22) { name=T.moonFirstQ; svg='<svg viewBox="0 0 24 24" width="22" height="22"><circle cx="12" cy="12" r="9" fill="#1a2a3a" opacity=".5"/><path d="M12 3 A9 9 0 0 1 12 21 Z" fill="#f0e8a0" opacity=".9"/></svg>'; }
 else if (p < 14.77) { name=T.moonWaxGibbous; svg='<svg viewBox="0 0 24 24" width="22" height="22"><circle cx="12" cy="12" r="9" fill="#f0e8a0" opacity=".9"/><path d="M12 3 A9 9 0 0 0 12 21 A3 9 0 0 1 12 3 Z" fill="#1a2a3a" opacity=".6"/></svg>'; }
 else if (p < 16.61) { name=T.moonFull; svg='<svg viewBox="0 0 24 24" width="22" height="22"><circle cx="12" cy="12" r="9" fill="#f0e8a0" opacity=".95"/><circle cx="9" cy="10" r="1.5" fill="#d4c060" opacity=".4"/><circle cx="15" cy="14" r="1" fill="#d4c060" opacity=".3"/><circle cx="11" cy="15" r="1.2" fill="#d4c060" opacity=".35"/></svg>'; }
 else if (p < 22.15) { name=T.moonWanGibbous; svg='<svg viewBox="0 0 24 24" width="22" height="22"><circle cx="12" cy="12" r="9" fill="#f0e8a0" opacity=".9"/><path d="M12 3 A9 9 0 0 1 12 21 A3 9 0 0 0 12 3 Z" fill="#1a2a3a" opacity=".6"/></svg>'; }
 else if (p < 23.99) { name=T.moonLastQ; svg='<svg viewBox="0 0 24 24" width="22" height="22"><circle cx="12" cy="12" r="9" fill="#1a2a3a" opacity=".5"/><path d="M12 3 A9 9 0 0 0 12 21 Z" fill="#f0e8a0" opacity=".9"/></svg>'; }
 else { name=T.moonWanCrescent; svg='<svg viewBox="0 0 24 24" width="22" height="22"><circle cx="12" cy="12" r="9" fill="#c8d8f0" opacity=".15"/><path d="M12 3 A9 9 0 0 0 12 21 A5 9 0 0 1 12 3 Z" fill="#f0e8a0" opacity=".9"/></svg>'; }
 return { phase: p, name: name, svg: svg };
}

function sunriseSunset(lat, lon, year, month, day) {
 var N1=Math.floor(275*month/9), N2=Math.floor((month+9)/12), N3=1+Math.floor((year-4*Math.floor(year/4)+2)/3);
 var N=N1-N2*N3+day-30, lngHour=lon/15;
 function calc(sr) {
 var t=sr?N+(6-lngHour)/24:N+(18-lngHour)/24, M=0.9856*t-3.289, mR=M*Math.PI/180;
 var L=M+1.916*Math.sin(mR)+0.020*Math.sin(2*mR)+282.634; L=((L%360)+360)%360;
 var lR=L*Math.PI/180, RA=Math.atan(0.91764*Math.tan(lR))*180/Math.PI; RA=((RA%360)+360)%360;
 var Lq=Math.floor(L/90)*90, RAq=Math.floor(RA/90)*90; RA=(RA+Lq-RAq)/15;
 var sinD=0.39782*Math.sin(lR), cosD=Math.cos(Math.asin(sinD));
 var cosH=(Math.cos(90.833*Math.PI/180)-sinD*Math.sin(lat*Math.PI/180))/(cosD*Math.cos(lat*Math.PI/180));
 if (cosH>1||cosH<-1) return null;
 var H=sr?(360-Math.acos(cosH)*180/Math.PI)/15:Math.acos(cosH)*180/Math.PI/15;
 var T=H+RA-0.06571*t-6.622; return ((T-lngHour)%24+24)%24;
 }
 function fmt(h) { if (h==null) return '--:--'; var hh=Math.floor(h), mm=Math.floor((h-hh)*60); return (hh<10?'0':'')+hh+'h'+(mm<10?'0':'')+mm; }
 return { rise: fmt(calc(true)), set: fmt(calc(false)) };
}

function applyTzOffset(utcStr, offsetSec) {
 // utcStr = "HHhMM", offsetSec = seconds east of UTC
 if (!utcStr || utcStr === '--:--') return utcStr;
 var parts = utcStr.split('h');
 var totalMin = parseInt(parts[0]) * 60 + parseInt(parts[1] || 0) + Math.round(offsetSec / 60);
 totalMin = ((totalMin % 1440) + 1440) % 1440;
 var hh = Math.floor(totalMin / 60), mm = totalMin % 60;
 return (hh < 10 ? '0' : '') + hh + 'h' + (mm < 10 ? '0' : '') + mm;
}

function renderAstro(lat, lon, yr, mo, da) {
 var moon=lunarPhase(yr, mo+1, da), sun=sunriseSunset(lat, lon, yr, mo+1, da);
 var offset = typeof _locTzOffset !== 'undefined' ? _locTzOffset : 0;
 var riseLocal = applyTzOffset(sun.rise, offset);
 var setLocal = applyTzOffset(sun.set, offset);
 var tzLabel = offset === 0 ? 'UTC' : (offset > 0 ? 'UTC+' : 'UTC') + (offset/3600).toFixed(1).replace('.0','');
 document.getElementById('astro-moon-ico').innerHTML = moon.svg;
 document.getElementById('astro-moon-name').textContent = moon.name;
 document.getElementById('astro-rise').textContent = riseLocal;
 document.getElementById('astro-set').textContent = setLocal;
 // Update labels
 var riseEl = document.getElementById('astro-rise').parentElement && document.getElementById('astro-rise').nextElementSibling;
 var lblEls = document.querySelectorAll('.astro-lbl');
 for (var i=0; i<lblEls.length; i++) {
 if (lblEls[i].textContent.indexOf('Lever') >= 0) lblEls[i].textContent = T.sunrise + ' (' + tzLabel + ')';
 if (lblEls[i].textContent.indexOf('Coucher') >= 0) lblEls[i].textContent = T.sunset + ' (' + tzLabel + ')';
 }
}

function applyHorizonWording(diffDays) {
 var label = document.getElementById('r-horizon-label');
 var btn = document.getElementById('btn-go');
 var btnTxt = btn.querySelector('span') || btn;

 var span = document.getElementById('btn-go-text');
 if (diffDays === 0) {
 label.className = 'hero-horizon-label hl-real';
 label.textContent = T.modeToday;
 if (span) span.textContent = T.checkWeather;
 } else if (diffDays >= 1 && diffDays <= 7) {
 label.className = 'hero-horizon-label hl-real';
 label.textContent = T.modeLive;
 if (span) span.textContent = T.checkWeather;
 } else if (diffDays <= 210) {
 label.className = 'hero-horizon-label hl-tendency';
 label.textContent = T.modeEcmwf;
 if (span) span.textContent = T.checkWeather;
 } else {
 label.className = 'hero-horizon-label hl-profile';
 label.textContent = T.modeClimate;
 if (span) span.textContent = T.checkWeather;
 }
}
function setConfBadge(diffDays) { /* badge supprimé */ }

/* GEOCODE */
function geocode(city) {
 // Strip formatting artifacts like 'Porto, Porto (Portugal)' → 'Porto'
 var clean = city.replace(/\s*\([^)]*\)/g, '').split(',')[0].trim();
 return fetch('https://geocoding-api.open-meteo.com/v1/search?name=' + encodeURIComponent(clean) + '&count=5&language=fr')
 .then(function(r) { return r.json(); })
 .then(function(d) {
 if (!d.results || !d.results.length) throw new Error('Ville introuvable');
 var r = d.results[0];
 var gRegion = (r.country_code === 'FR') ? '' : (r.admin1 || '');
 return { lat: r.latitude, lon: r.longitude, name: r.name, region: gRegion, country: r.country || COUNTRY_NAMES[r.country_code] || r.country_code || '' };
 });
}

/* ── SEA SURFACE TEMPERATURE ── */
var SEA_NAME_MAP = CFG.seaNameMap;
function slugFromName(name) {
 var n = CFG.slugNormalize(name);
 return SEA_NAME_MAP[n] || (SEA_CLIM_DATA[n] ? n : null);
}

var SEA_CLIM_DATA = CFG.seaClimData;

function getSeaComfortFR(sst) {
 if (sst >= 28) return {lbl:T.seaVeryWarm, color:'#ef4444'};
 if (sst >= 24) return {lbl:T.seaWarm, color:'#f59e0b'};
 if (sst >= 20) return {lbl:T.seaPleasant, color:'#16a34a'};
 if (sst >= 17) return {lbl:T.seaCool, color:'#0ea5e9'};
 if (sst >= 14) return {lbl:T.seaCold, color:'#6366f1'};
 return {lbl:T.seaVeryCold, color:'#64748b'};
}

function fetchMarineSST(lat, lon, yr, mo, da, slug) {
 var dateStr = yr+'-'+(mo<9?'0':'')+(mo+1)+'-'+(da<10?'0':'')+da;
 var today = new Date(); today.setHours(0,0,0,0);
 var target = new Date(yr,mo,da,0,0,0);
 var diffDays = Math.round((target.getTime()-today.getTime())/86400000);

 function tryClimatology() {
  var climData = slug && SEA_CLIM_DATA[slug] ? SEA_CLIM_DATA[slug] : null;
  if (climData && climData[mo] !== null) return Promise.resolve({sst:climData[mo],fallback:true});
  // Fallback par archive marine (coordonnées) — 3 ans de données autour de la date
  var endYr2 = new Date().getFullYear()-1;
  var s2 = (endYr2-2)+'-'+(mo<9?'0':'')+(mo+1)+'-'+(da<10?'0':'')+da;
  var e2 = endYr2+'-'+(mo<9?'0':'')+(mo+1)+'-'+(da<10?'0':'')+da;
  return fetch('https://marine-api.open-meteo.com/v1/marine?latitude='+lat+'&longitude='+lon+'&daily=sea_surface_temperature_max&start_date='+s2+'&end_date='+e2)
   .then(function(r){return r.ok?r.json():null;})
   .then(function(d){
    if(!d||!d.daily||!d.daily.sea_surface_temperature_max) return null;
    var vals=d.daily.sea_surface_temperature_max.filter(function(v){return v!=null;});
    if(!vals.length) return null;
    vals.sort(function(a,b){return a-b;});
    var median=vals[Math.floor(vals.length/2)];
    return {sst:Math.round(median*10)/10, fallback:true};
   }).catch(function(){return null;});
 }

 var refDate = new Date(2024,0,1);
 if (diffDays > 7 || target < refDate) return tryClimatology();

 var url;
 if (diffDays === 0 || (diffDays >= 1 && diffDays <= 7)) {
 url = 'https://marine-api.open-meteo.com/v1/marine?latitude='+lat+'&longitude='+lon+'&hourly=sea_surface_temperature&forecast_days=8';
 } else {
 url = 'https://marine-api.open-meteo.com/v1/marine?latitude='+lat+'&longitude='+lon+'&hourly=sea_surface_temperature&start_date='+dateStr+'&end_date='+dateStr;
 }

 return fetch(url)
 .then(function(r){ return r.ok ? r.json() : null; })
 .then(function(d){
 if (!d || d.error) return tryClimatology();
 var vals = (d.hourly && d.hourly.sea_surface_temperature) || [];
 var times = (d.hourly && d.hourly.time) || [];
 var sst = null;
 if (diffDays === 0) {
 var prefix = dateStr.slice(0,13);
 for (var i=0;i<times.length;i++){if(times[i].indexOf(prefix)===0&&vals[i]!=null){sst=vals[i];break;}}
 if(sst===null)for(var j=0;j<vals.length;j++){if(vals[j]!=null){sst=vals[j];break;}}
 } else if (diffDays >= 1 && diffDays <= 7) {
 var prefix = dateStr+'T12';
 for (var i=0;i<times.length;i++) {
 if (times[i].indexOf(prefix)===0 && vals[i]!=null) { sst=vals[i]; break; }
 }
 if (sst===null) for (var j=0;j<vals.length;j++) { if (vals[j]!=null) { sst=vals[j]; break; } }
 } else {
 for (var k=0;k<vals.length;k++) { if (vals[k]!=null) { sst=vals[k]; break; } }
 }
 if (sst===null) return tryClimatology();
 return {sst: Math.round(sst*10)/10, fallback:false};
 })
 .catch(function(){ return tryClimatology(); });
}

function renderSeaChip(sstResult) {
 if (!sstResult || sstResult.sst===null) return;
 var comfort = getSeaComfortFR(sstResult.sst);
 var lbl = sstResult.fallback ? T.seaLabelSeasonal : T.seaLabel;
 var chip = document.createElement('div');
 chip.className = 'score-chip';
 chip.id = 'sea-chip';
 chip.title = comfort.lbl;
 chip.innerHTML =
 '<span class="score-chip-dot" style="background:'+comfort.color+'"></span>'+
 '<span class="score-chip-lbl">'+lbl+'</span>'+
 '<span class="score-chip-val">'+fmtTemp(sstResult.sst)+'</span>';
 var chipsEl = document.getElementById('score-chips');
 if (chipsEl) chipsEl.appendChild(chip);
}

function fetchForecast(lat, lon, yr, mo, da) {
 var url='https://api.open-meteo.com/v1/forecast?latitude='+lat+'&longitude='+lon+'&hourly=temperature_2m,precipitation_probability,precipitation,snowfall,windspeed_10m,shortwave_radiation&timezone=auto&forecast_days=8';
 // _locTzOffset is global
 return fetch(url).then(function(r){if(!r.ok)throw new Error(T.errForecast);return r.json();}).then(function(data){
 if (data.utc_offset_seconds != null) _locTzOffset = data.utc_offset_seconds;
 var mo2=mo+1, prefix=yr+'-'+(mo2<10?'0':'')+mo2+'-'+(da<10?'0':'')+da, rows=[];
 for(var h=0;h<24;h++){
 var ts=prefix+'T'+(h<10?'0':'')+h+':00', idx=-1;
 for(var i=0;i<data.hourly.time.length;i++){if(data.hourly.time[i]===ts){idx=i;break;}}
 var t=idx>=0&&data.hourly.temperature_2m[idx]!=null?parseFloat(data.hourly.temperature_2m[idx].toFixed(1)):null;
 var rn=idx>=0&&data.hourly.precipitation_probability[idx]!=null?data.hourly.precipitation_probability[idx]:0;
 var mm_val=idx>=0&&data.hourly.precipitation&&data.hourly.precipitation[idx]!=null?parseFloat(data.hourly.precipitation[idx].toFixed(2)):0;
 var snow_val=idx>=0&&data.hourly.snowfall&&data.hourly.snowfall[idx]!=null?parseFloat(data.hourly.snowfall[idx].toFixed(2)):0;
 var w=idx>=0&&data.hourly.windspeed_10m[idx]!=null?parseFloat(data.hourly.windspeed_10m[idx].toFixed(1)):0;
 var s=idx>=0&&data.hourly.shortwave_radiation&&data.hourly.shortwave_radiation[idx]!=null?Math.max(0,data.hourly.shortwave_radiation[idx]):0;
 rows.push({h:h,label:(h<10?'0':'')+h+'h',p25:t,p50:t,p75:t,temp:t,rain:rn,mm:mm_val,windP50:w,solP25:s,solP50:s,solP75:s,sol:s,snow:snow_val,isForecast:true});
 }
 return rows;
 });
}

function fetchArchive(lat, lon, refDate) {
 var s=toISO(addDays(refDate,-10)), e=toISO(addDays(refDate,10));
 return fetch('https://archive-api.open-meteo.com/v1/archive?latitude='+lat+'&longitude='+lon+'&start_date='+s+'&end_date='+e+'&hourly=temperature_2m,precipitation,snowfall,windspeed_10m,shortwave_radiation,relative_humidity_2m&timezone=auto').then(function(r){if(!r.ok)throw new Error('Archive error');return r.json();}).then(function(d){if(d.utc_offset_seconds!=null)_locTzOffset=d.utc_offset_seconds;return d;});
}

function fetchSnowDepth(lat, lon, yr, mo, da) {
 // 10 années en parallèle — un seul appel couvrant toute la fenêtre
 var now = new Date();
 var endYr = now.getFullYear() - 1;
 // Construire une seule requête : start = (endYr-9)/mo/da-3j, end = endYr/mo/da+3j
 // Open-Meteo accepte des plages pluriannuelles sur l'archive
 var s = toISO(addDays(new Date(endYr-9, mo, da), -3));
 var e = toISO(addDays(new Date(endYr,   mo, da),  3));
 return fetch('https://archive-api.open-meteo.com/v1/archive?latitude='+lat+'&longitude='+lon+'&start_date='+s+'&end_date='+e+'&daily=snow_depth_max&timezone=auto')
  .then(function(r){if(!r.ok)return null;return r.json();})
  .then(function(d){
   if(!d||!d.daily||!d.daily.snow_depth_max) return {depth:null, elevation:d?d.elevation:null};
   // Garder uniquement les valeurs autour de la date cible (±3j par année)
   var times = d.daily.time;
   var depths = d.daily.snow_depth_max;
   var vals = [];
   for (var i=0; i<times.length; i++) {
    if (depths[i] == null) continue;
    var parts = times[i].split('-');
    // Comparer uniquement mois et jour (ignorer l'année)
    var dMo = parseInt(parts[1])-1, dDa = parseInt(parts[2]);
    var diff = Math.abs((dMo*31+dDa) - (mo*31+da));
    if (diff <= 3) vals.push(depths[i]);
   }
   var median = vals.length ? vals.slice().sort(function(a,b){return a-b;})[Math.floor(vals.length/2)] : null;
   return {depth: median!=null ? Math.round(median*100) : null, elevation: d.elevation||null};
  }).catch(function(){return {depth:null, elevation:null};});
}

function buildClimatology(lat, lon, yr, mo, da) {
 var target=new Date(yr,mo,da,12,0,0), now=new Date();
 var trend=Math.max(0,(target.getTime()-now.getTime())/(1000*60*60*24*365.25))*0.03;
 var endYr=now.getFullYear()-1, years=[];
 for(var y=endYr-9;y<=endYr;y++) years.push(y);
 var buckets=[]; for(var h=0;h<24;h++) buckets.push({t:[],p:[],w:[],s:[],sn:[],rh:[]});
 var idx=0;
 function step(){
 if(idx>=years.length) return Promise.resolve(buildRows(buckets,trend));
 var yr2=years[idx++];
 return fetchArchive(lat,lon,new Date(yr2,mo,da,12,0,0)).then(function(data){
 var T=data.hourly.temperature_2m, P=data.hourly.precipitation, W=data.hourly.windspeed_10m, S=data.hourly.shortwave_radiation||[], SN=data.hourly.snowfall||[], RH=data.hourly.relative_humidity_2m||[];
 for(var i=0;i<data.hourly.time.length;i++){var hh=new Date(data.hourly.time[i]).getHours();if(T[i]!=null)buckets[hh].t.push(T[i]);if(P[i]!=null)buckets[hh].p.push(P[i]);if(W[i]!=null)buckets[hh].w.push(W[i]);if(S[i]!=null)buckets[hh].s.push(S[i]);if(SN[i]!=null)buckets[hh].sn.push(SN[i]);if(RH[i]!=null)buckets[hh].rh.push(RH[i]);}
 }).catch(function(){}).then(function(){setP(Math.round((idx/years.length)*90),'Analyse '+yr2+'…');return new Promise(function(res){setTimeout(res,20);});}).then(step);
 }
 return step();
}

function buildRows(buckets, trend) {
 var rows=[];
 for(var h=0;h<24;h++){
 var b=buckets[h], wet=0;
 for(var i=0;i<b.p.length;i++) if(b.p[i]>0.1) wet++;
 var p25=pct(b.t,25), p50=pct(b.t,50), p75=pct(b.t,75);
 var avgSnow = b.sn && b.sn.length > 0 ? b.sn.reduce(function(s,v){return s+v;},0)/b.sn.length : 0;
 var p50v=p50!=null?p50+trend:null;
    var tempFreq=null;
    if(p50v!=null&&b.t.length>0){var _inRange=0;for(var _ti=0;_ti<b.t.length;_ti++)if(Math.abs(b.t[_ti]-p50v)<=2)_inRange++;tempFreq=Math.round(_inRange/b.t.length*100);}
    var avgRh = b.rh && b.rh.length > 0 ? b.rh.reduce(function(s,v){return s+v;},0)/b.rh.length : null;
    rows.push({h:h,label:(h<10?'0':'')+h+'h',p25:p25!=null?parseFloat((p25+trend).toFixed(1)):null,p50:p50v,p75:p75!=null?parseFloat((p75+trend).toFixed(1)):null,temp:p50v,rain:b.p.length>0?Math.round(wet/b.p.length*100):0,mm:b.p.length>0?(b.p.reduce(function(s,v){return s+v;},0)/b.p.length):0,snow:avgSnow,windP50:pct(b.w,50),solP25:Math.max(0,pct(b.s,25)||0),solP50:Math.max(0,pct(b.s,50)||0),solP75:Math.max(0,pct(b.s,75)||0),sol:Math.max(0,pct(b.s,50)||0),tempFreq:tempFreq,rh:avgRh});
 }
 return rows;
}

function fetchSeasonal(lat, lon, yr, mo, da) {
 var mo2=mo+1, mm=(mo2<10?'0':'')+mo2, dd=(da<10?'0':'')+da, dateStr=yr+'-'+mm+'-'+dd;
 return fetch('https://seasonal-api.open-meteo.com/v1/seasonal?latitude='+lat+'&longitude='+lon+'&daily=temperature_2m_mean,precipitation_sum,windspeed_10m_mean&start_date='+dateStr+'&end_date='+dateStr)
 .then(function(r){if(!r.ok)return null;return r.json();})
 .then(function(data){
 if(!data||!data.daily||!data.daily.time||data.daily.time[0]!==dateStr) return null;
 var daily=data.daily, ks=Object.keys(daily), tempM=[],precipM=[],windM=[];
 for(var i=0;i<ks.length;i++){var k=ks[i];if(k.indexOf('temperature_2m_mean_member')===0&&daily[k][0]!=null)tempM.push(daily[k][0]);if(k.indexOf('precipitation_sum_member')===0&&daily[k][0]!=null)precipM.push(daily[k][0]);if(k.indexOf('windspeed_10m_mean_member')===0&&daily[k][0]!=null)windM.push(daily[k][0]);}
 if(!tempM.length) return null;
 tempM.sort(function(a,b){return a-b;}); precipM.sort(function(a,b){return a-b;});
 var n=tempM.length, wet=0; for(var j=0;j<precipM.length;j++) if(precipM[j]>0.1) wet++;
 var windSum=0; for(var w=0;w<windM.length;w++) windSum+=windM[w];
 return {tMean:daily.temperature_2m_mean[0]||tempM[Math.floor(n*0.5)],tP25:tempM[Math.floor(n*0.25)],tP50:tempM[Math.floor(n*0.50)],tP75:tempM[Math.floor(n*0.75)],rainProb:precipM.length?Math.round(wet/precipM.length*100):null,windMean:windM.length?windSum/windM.length:null};
 }).catch(function(){return null;});
}

function applySeasonalCorrection(rows, seas) {
 if(!seas) return rows;
 var histSum=0,histCnt=0,histRainSum=0,histWindSum=0,histSpreadSum=0,spreadCnt=0;
 for(var i=0;i<rows.length;i++){var r=rows[i];if(r.p50!=null){histSum+=r.p50;histCnt++;}histRainSum+=r.rain;if(r.windP50)histWindSum+=r.windP50;if(r.p25!=null&&r.p75!=null){histSpreadSum+=(r.p75-r.p25)/2;spreadCnt++;}}
 if(!histCnt) return rows;
 var histMean=histSum/histCnt, offset=parseFloat((seas.tMean-histMean).toFixed(2));
 window._seasTempOffset = offset;
 window._seasRainOffset = seas.rainProb != null ? Math.round(seas.rainProb - (histRainSum/rows.length)) : null;
 var histSpreadAvg=spreadCnt?histSpreadSum/spreadCnt:1, seasSpread=(seas.tP75-seas.tP25)/2;
 var ratio=(histSpreadAvg>0.5&&seasSpread>0)?Math.min(2.5,Math.max(0.3,seasSpread/histSpreadAvg)):1;
 var histRainAvg=histRainSum/rows.length, histWindAvg=rows.length?histWindSum/rows.length:0;
 var out=[];
 for(var j=0;j<rows.length;j++){
 var ro=rows[j], newP50=ro.p50!=null?ro.p50+offset:null;
 var sp25=ro.p50!=null&&ro.p25!=null?ro.p50-ro.p25:0, sp75=ro.p50!=null&&ro.p75!=null?ro.p75-ro.p50:0;
 var newRain=ro.rain;
 if(seas.rainProb!==null){var anomalyRain=seas.rainProb-histRainAvg;newRain=Math.min(100,Math.max(0,Math.round(ro.rain+anomalyRain*0.25)));}
 var newWind=ro.windP50;
 if(seas.windMean!==null&&ro.windP50!=null){var wDelta=Math.min(5,Math.max(-5,(seas.windMean-histWindAvg)*0.35));newWind=Math.max(0,parseFloat((ro.windP50+wDelta).toFixed(1)));}
 out.push(cloneRow(ro,{p50:newP50!=null?parseFloat(newP50.toFixed(1)):null,p25:newP50!=null?parseFloat((newP50-sp25*ratio).toFixed(1)):null,p75:newP50!=null?parseFloat((newP50+sp75*ratio).toFixed(1)):null,temp:newP50!=null?parseFloat(newP50.toFixed(1)):null,sol:ro.solP50||0,rain:newRain,windP50:newWind}));
 }
 return out;
}

function showSection(id){document.getElementById(id).style.display='block';}
function hideSection(id){document.getElementById(id).style.display='none';}

function renderHourly(sc) {
 var strip=document.getElementById('h-strip'); strip.innerHTML='';
 var hours=[0,3,6,9,12,15,18,21,23];
 for(var i=0;i<hours.length;i++){
 var r=sc[hours[i]]; if(!r) continue;
 var lbl=(hours[i]===23)?'00h':r.label;
 var cell=document.createElement('div'); cell.className='h-cell';
 cell.innerHTML='<span class="h-hr">'+lbl+'</span><span class="h-ic">'+getIcon(r.h,r.temp,r.sol,r.rain,r.mm||0,r.snow||0,r.p25)+'</span><span class="h-tp">'+(r.temp!=null?fmtTempRaw(r.temp)+'°':'-')+'</span><span class="h-lb">'+getLabel(r.h,r.temp,r.sol,r.rain,r.mm||0,r.snow||0)+'</span><div class="h-rb"><div class="h-rf" style="width:'+r.rain+'%"></div></div>';
 strip.appendChild(cell);
 }
}


function scenarioLabel(rows, isOpt) {
 var temps = [], rains = [];
 for (var i=0; i<rows.length; i++) {
 if (rows[i].temp != null) temps.push(rows[i].temp);
 rains.push(rows[i].rain);
 }
 var tmax = temps.length ? Math.max.apply(null,temps) : null;
 var tmin = temps.length ? Math.min.apply(null,temps) : null;
 var avgRain = rains.length ? rains.reduce(function(a,b){return a+b;},0)/rains.length : 0;

 var title, sub;
 if (isOpt) {
 // Optimistic scenario
 if (tmax !== null && tmax >= 38) { title = T.heroVeryHot; sub = T.heroVeryHotSub; }
 else if (tmax !== null && tmax >= 32) { title = T.heroHotDay; sub = T.heroHotDaySub; }
 else if (tmax !== null && tmax <= 5) { title = T.heroColdDay; sub = T.heroColdDaySub; }
 else if (avgRain <= 15) { title = T.heroIdealDay; sub = T.heroIdealDaySub; }
 else { title = T.heroGoodDay; sub = T.heroGoodDaySub; }
 } else {
 // Pessimistic scenario
 if (avgRain >= 60) { title = T.heroVeryRainy; sub = T.heroVeryRainySub; }
 else if (tmax !== null && tmax >= 38) { title = T.heroCanicule; sub = T.heroChaniculeSub; }
 else if (tmin !== null && tmin <= 0) { title = T.heroFreezing; sub = T.heroFreezingSub; }
 else if (avgRain >= 35) { title = T.heroDifficult; sub = T.heroDifficultSub; }
 else { title = T.heroMixed; sub = T.heroMixedSub; }
 }
 return { title: title, sub: sub };
}

function updateScenarioLabels(pessRows, optRows) {
 var pess = scenarioLabel(pessRows, false);
 var opt = scenarioLabel(optRows, true);
 var pt = document.getElementById('sc-pess-ttl');
 var ps = document.getElementById('sc-pess-sub');
 var ot = document.getElementById('sc-opt-ttl');
 var os = document.getElementById('sc-opt-sub');
 if (pt) pt.textContent = pess.title;
 if (ps) ps.textContent = pess.sub;
 if (ot) ot.textContent = opt.title;
 if (os) os.textContent = opt.sub;
}

function renderScCard(sc, stripId, statsId) {
 var strip=document.getElementById(stripId); strip.innerHTML='';
 var hours=[0,3,6,9,12,15,18,21,23];
 for(var i=0;i<hours.length;i++){
 var r=sc[hours[i]]; if(!r) continue;
 var lbl=(hours[i]===23)?'00h':r.label;
 var cell=document.createElement('div'); cell.className='sc-cell';
 cell.innerHTML='<span class="sc-hr">'+lbl+'</span>'+getIcon(r.h,r.temp,r.sol,r.rain,r.mm||0,r.snow||0,r.p25)+'<span class="sc-tp">'+(r.temp!=null?fmtTempRaw(r.temp)+'°':'-')+'</span>';
 strip.appendChild(cell);
 }
 var temps=[],rSum=0,wSum=0;
 for(var j=0;j<sc.length;j++){if(sc[j].temp!=null)temps.push(sc[j].temp);rSum+=sc[j].rain;wSum+=(sc[j].windP50||0);}
 var tmin=temps.length?Math.min.apply(null,temps):'-', tmax=temps.length?Math.max.apply(null,temps):'-';
 document.getElementById(statsId).innerHTML='<div><div class="sc-stat-val">'+fmtTempRaw(tmin)+'°/'+fmtTempRaw(tmax)+'°</div><div class="sc-stat-lbl">'+T.statMinMax+'</div></div><div><div class="sc-stat-val">'+Math.round(rSum/sc.length)+'%</div><div class="sc-stat-lbl">'+T.statRain+'</div></div><div><div class="sc-stat-val">'+fmtWind(Math.round(wSum/sc.length))+'</div><div class="sc-stat-lbl">'+T.statWind+'</div></div>';
}


/* ── WEATHER SCORE ── */
var currentUseCase = 'general';
var _lastRows = null, _lastSc = null;
var _locTzOffset = 0; // global timezone offset from API
var _lastMonthly = null, _lastAnnLoc = null;

// Reference scores from destination pages
// Used by annual view for consistency with static pages statiques
var FICHE_SCORES = {"30.42,-9.6":[70,72,75,84,89,94,99,100,88,83,76,72],"37.1,-8.68":[69,70,77,86,93,100,100,99,99,86,72,40],"38.35,-0.48":[70,72,72,80,92,100,100,94,89,86,78,74],"40.63,14.6":[22,69,72,83,92,100,95,94,96,85,70,40],"52.37,4.89":[5,18,39,69,70,94,94,100,73,40,14,5],"-8.67,115.21":[40,69,70,79,90,97,100,100,94,85,73,69],"13.75,100.52":[99,88,75,70,50,42,40,41,51,69,78,100],"41.39,2.15":[70,72,73,79,87,96,100,94,84,82,73,73],"52.52,13.4":[5,39,40,69,70,100,98,100,78,54,39,14],"44.8378,-0.5792":[22,69,70,80,87,92,100,99,91,81,65,40],"48.1173,-1.6778":[22,54,69,74,82,94,100,98,88,70,57,40],"-34.61,-58.38":[99,98,93,85,79,73,70,78,82,87,96,100],"28.29,-16.62":[72,77,82,87,92,99,100,96,93,87,77,70],"21.16,-86.85":[82,88,95,100,83,73,74,70,70,76,84,81],"40.55,14.24":[5,40,70,81,92,100,98,97,98,84,69,39],"39.62,19.92":[40,69,70,80,88,99,100,96,92,86,71,67],"41.9266,8.7369":[40,70,73,82,90,99,100,97,92,84,72,69],"43.71,7.26":[40,61,70,80,92,100,99,98,97,82,69,22],"35.24,24.81":[40,69,71,88,98,100,98,97,99,89,70,54],"25.2,55.27":[93,96,100,86,78,74,71,70,73,78,92,94],"42.65,18.09":[5,39,40,70,80,95,100,93,90,78,69,31],"55.95,-3.19":[16,27,39,58,69,70,100,97,69,40,36,5],"43.77,11.25":[39,40,69,70,77,100,95,89,91,71,44,5],"27.93,-15.53":[70,71,75,79,87,91,100,99,90,83,76,72],"15.88,108.34":[72,86,100,96,81,76,74,70,59,69,63,40],"38.91,1.43":[69,70,77,86,95,100,97,96,96,90,73,40],"-20.16,57.5":[72,70,74,95,100,97,99,99,100,100,88,77],"41.01,28.96":[5,20,55,70,88,96,100,99,94,72,39,6],"27.71,85.32":[78,85,90,96,82,78,70,71,74,86,100,93],"23.14,-82.36":[93,98,100,92,83,73,73,70,71,79,89,95],"28.96,-13.55":[70,70,74,83,88,91,99,100,92,84,77,72],"38.72,-9.14":[55,70,75,82,88,97,100,97,95,82,69,40],"51.51,-0.13":[11,21,39,69,70,94,100,94,78,40,28,5],"45.764,4.8357":[5,52,69,71,77,92,100,98,88,70,40,39],"32.65,-16.91":[70,72,72,75,86,87,100,99,85,80,73,71],"39.57,2.65":[69,70,78,87,96,100,95,93,96,86,72,40],"36.72,-4.42":[70,71,73,80,92,100,96,93,93,84,77,73],"3.2,73.22":[99,100,95,83,70,88,81,82,82,83,74,82],"35.9,14.51":[40,70,78,89,98,100,95,94,96,90,77,69],"31.63,-8.00":[70,78,89,100,93,86,82,83,86,96,85,70],"43.2965,5.3698":[70,72,77,80,86,95,100,98,91,82,72,71],"43.73,7.41":[42,69,74,77,82,92,100,98,88,79,70,40],"37.44,25.37":[40,69,70,82,94,100,96,95,97,87,71,56],"40.71,-74.01":[5,9,39,69,85,100,98,100,96,70,40,15],"43.7102,7.262":[70,70,75,81,86,93,100,96,91,82,72,71],"48.8566,2.3522":[5,40,69,75,82,92,100,96,90,70,43,39],"7.88,98.39":[92,100,93,70,45,60,69,74,42,51,40,86],"41.16,-8.62":[40,60,69,70,82,89,100,100,90,74,64,47],"50.08,14.44":[5,37,40,69,70,94,100,96,83,57,39,7],"43.9493,4.8055":[69,72,79,86,94,100,100,99,98,87,70,40],"-21.11,55.54":[95,90,93,77,71,40,70,74,91,100,69,93],"64.14,-21.94":[5,10,19,25,39,40,59,69,28,17,9,7],"36.43,28.22":[70,74,78,87,94,100,96,96,98,93,85,74],"-22.91,-43.17":[77,70,79,89,90,92,100,92,97,78,78,77],"20.63,-87.08":[100,100,99,95,84,77,76,72,70,76,91,98],"41.9,12.5":[40,65,70,80,87,100,98,93,92,83,69,64],"36.39,25.46":[40,69,70,83,95,100,94,93,97,86,70,52],"40.12,9.01":[40,69,74,84,92,100,98,97,97,89,70,57],"-4.68,55.49":[76,88,100,79,77,72,71,72,70,83,86,72],"37.6,14.01":[40,70,78,89,100,100,92,90,93,93,76,69],"13.36,103.86":[100,93,79,73,69,70,40,43,44,75,80,99],"1.35,103.82":[93,99,100,70,52,69,99,96,99,54,40,56],"43.51,16.44":[22,52,70,78,85,100,98,95,94,84,69,40],"28.29,-16.63":[41,46,69,74,80,86,100,94,80,70,40,45],"35.68,139.69":[52,40,48,77,100,92,91,88,91,80,70,69],"43.78,11.24":[44,69,70,82,95,99,90,88,100,82,40,22],"39.47,-0.38":[70,72,73,78,91,100,98,90,87,84,76,71],"45.44,12.33":[8,39,55,73,88,96,100,99,91,70,31,5],"48.21,16.37":[5,40,69,74,79,94,100,99,90,70,39,6],"37.79,20.9":[55,72,74,87,93,100,97,97,96,90,75,70],"-6.17,39.2":[87,77,70,55,90,99,92,92,100,91,76,74]};

// Cache mensuel pré-calculé — chargé depuis data/monthly.json
var MONTHLY_CACHE = null;
var MONTHLY_CACHE_PROMISE = fetch(CFG.dataBase+'data/monthly.json')
 .then(function(r){ return r.ok ? r.json() : null; })
 .then(function(d){ MONTHLY_CACHE = d || {}; return MONTHLY_CACHE; })
 .catch(function(){ MONTHLY_CACHE = {}; return {}; });

function findCachedMonthly(lat, lon) {
 if (!MONTHLY_CACHE) return null;
 var exact = lat + ',' + lon;
 if (MONTHLY_CACHE[exact]) return MONTHLY_CACHE[exact].monthly;
 // Proximity match (0.15°)
 var best = null, bestDist = 0.15;
 for (var k in MONTHLY_CACHE) {
 var parts = k.split(',');
 var d = Math.sqrt(Math.pow(parseFloat(parts[0])-lat,2)+Math.pow(parseFloat(parts[1])-lon,2));
 if (d < bestDist) { bestDist = d; best = k; }
 }
 return best ? MONTHLY_CACHE[best].monthly : null;
}

var UC_CONFIG = {
 general: { label:T.ucGeneral, tempMin:16, tempMax:28, weights:{rain:30,temp:35,wind:15,sun:20} },
 plage:   { label:'Plage & baignade', tempMin:22, tempMax:38, weights:{rain:30,temp:45,wind:10,sun:15} },
 ski:     { label:'Ski & sports d\'hiver', tempMin:-8, tempMax:2, weights:{rain:20,temp:40,wind:10,sun:30} }
};


// ─────────────────────────────────────────────────────────────────────────────
// SCORING MENSUEL — traduction directe de scoring.py (source de vérité Python)
// Algorithme : ancrage sur classes rec/mid/avoid + normalisation min-max
// Toute modification ici doit être répercutée dans scoring.py (et vice versa)
// ─────────────────────────────────────────────────────────────────────────────

// Clés lat,lon des destinations à régime mousson.
// scoring.py : TROPICAL_DESTINATIONS — synchroniser à chaque ajout.
var TROPICAL_KEYS = {
 "13.75,100.52": true, // Bangkok — mousson mai-oct
 "7.88,98.39": true, // Phuket — mousson mai-nov (côte Andaman)
 "15.88,108.34": true, // Hoi An — mousson sept-déc
 "13.36,103.86": true, // Siem Reap — mousson mai-sept
 "1.35,103.82": true, // Singapour — pluies mai-oct
 "-6.17,39.2": true, // Zanzibar — grande saison des pluies avr
};

// Plages score par classe — scoring.py : SCORE_RANGES
var SCORE_RANGES_FICHE = { avoid:[0.5,3.9], mid:[4.0,6.9], rec:[7.0,10.0] };

// scoring.py : t_ideal()
function tIdeal(tmax) {
 if (tmax <= 5) return 0.0;
 if (tmax <= 14) return (tmax - 5) / 9 * 0.3;
 if (tmax <= 22) return 0.3 + (tmax - 14) / 8 * 0.5;
 if (tmax <= 28) return 0.8 + (tmax - 22) / 6 * 0.2;
 if (tmax <= 35) return 1.0 - (tmax - 28) / 7 * 0.4;
 return Math.max(0, 0.6 - (tmax - 35) / 10 * 0.3);
}

// scoring.py : raw_score() poids 40/35/25
function rawScoreFiche(tmax, rain, sun) {
 return 0.40 * tIdeal(tmax)
 + 0.35 * Math.max(0, 1 - rain / 100)
 + 0.25 * Math.min(1, sun / 15);
}

// Classification auto pour destinations sans fiche statique
function autoClass(r) { return r >= 0.55 ? 'rec' : r >= 0.38 ? 'mid' : 'avoid'; }

/**
 * scoring.py : compute_scores() — version JS batch.
 * Écrit monthly[i].ficheScore pour les mois où il est absent.
 * Les mois déjà renseignés (destinations connues via FICHE_SCORES) sont préservés.
 */

/**
 * Lookup FICHE_SCORES avec tolérance de proximité.
 * Le géocodeur Open-Meteo retourne des coords légèrement différentes
 * de celles stockées dans FICHE_SCORES (ex: Paris 48.85341 vs 48.8566).
 * Seuil : 0.15° (~17km) — aucune ambiguïté entre destinations du catalogue.
 * Retourne [key, scores] ou [null, null] si aucun match.
 */
function findFicheScores(lat, lon) {
 var exact = lat + ',' + lon;
 if (FICHE_SCORES[exact]) return [exact, FICHE_SCORES[exact]];
 var best = null, bestDist = 0.15; // seuil max 0.15°
 for (var k in FICHE_SCORES) {
 var parts = k.split(',');
 var dlat = Math.abs(parseFloat(parts[0]) - lat);
 var dlon = Math.abs(parseFloat(parts[1]) - lon);
 var dist = Math.sqrt(dlat*dlat + dlon*dlon);
 if (dist < bestDist) { bestDist = dist; best = k; }
 }
 return best ? [best, FICHE_SCORES[best]] : [null, null];
}

function computeAnchoredScores(monthly, ficheKey) {
 var isTropical = !!TROPICAL_KEYS[ficheKey];
 if (monthly.every(function(m){ return m.ficheScore != null; })) return;

 var items = monthly.map(function(m, i) {
 var tmax = m.avgTmax != null ? m.avgTmax : (m.avgTemp || 20);
 var rain = m.rainPct != null ? m.rainPct : 30;
 var sun = m.sunHrs != null ? m.sunHrs : 5;
 var raw = rawScoreFiche(tmax, rain, sun);
 return { i: i, raw: raw, cls: autoClass(raw) };
 });

 ['avoid','mid','rec'].forEach(function(cls) {
 var grp = items.filter(function(it){ return it.cls === cls; });
 if (!grp.length) return;
 var range = (isTropical && cls === 'avoid') ? SCORE_RANGES_FICHE.mid : SCORE_RANGES_FICHE[cls];
 var lo = range[0], hi = range[1];
 var raws = grp.map(function(it){ return it.raw; });
 var mn = Math.min.apply(null, raws), mx = Math.max.apply(null, raws);
 grp.forEach(function(it, j) {
 if (monthly[it.i].ficheScore != null) return;
 var norm = mx !== mn ? (raws[j] - mn) / (mx - mn) : 0.5;
 monthly[it.i].ficheScore = Math.round((lo + norm * (hi - lo)) * 10); // échelle ×10 = cohérent avec FICHE_SCORES
 });
 });
}

function scoreRain(pct) {
 if (pct <= 10) return 100;
 if (pct <= 25) return 100 - (pct - 10) * 2;
 if (pct <= 50) return 70 - (pct - 25) * 1.6;
 if (pct <= 80) return 30 - (pct - 50) * 0.8;
 return Math.max(0, 6 - (pct - 80) * 0.3);
}
function scoreRainSmart(pct, mmDay, avgTemp) {
 // Correction basée sur l'intensité réelle (mm/jour), indépendamment de la température.
 // < 3mm/j = bruine/averses légères → forte correction (pluie peu gênante)
 // 3–6mm/j = pluie modérée → correction partielle
 // > 6mm/j = pluie sérieuse → pas de correction
 var effective = pct;
 if (mmDay != null) {
 if (mmDay < 3) {
 var factor = 0.40 + (mmDay / 3) * 0.30;
 effective = pct * factor;
 } else if (mmDay < 6) {
 var factor = 0.70 + ((mmDay - 3) / 3) * 0.30;
 effective = pct * factor;
 }
 }
 return scoreRain(effective);
}

function scoreTemp(t, tMin, tMax) {
 if (t == null) return 50;
 var ideal = (tMin + tMax) / 2;
 var range = (tMax - tMin) / 2;
 if (t >= tMin && t <= tMax) {
 // 100 at ideal, 80 at edges
 return 100 - 20 * Math.abs(t - ideal) / range;
 }
 // Outside range: asymmetric penalty
 // Too cold = strong penalty (8pts/°C) — comfort strongly affected
 // Too hot = soft penalty (2pts/°C) — still pleasant, just warm
 if (t < tMin) {
 return Math.max(0, 80 - (tMin - t) * 8);
 } else {
 return Math.max(0, 80 - (t - tMax) * 2);
 }
}

function scoreWind(kmh) {
 if (kmh <= 10) return 100;
 if (kmh <= 20) return 100 - (kmh - 10) * 3;
 if (kmh <= 40) return 70 - (kmh - 20) * 2.5;
 return Math.max(0, 20 - (kmh - 40) * 1);
}

function scoreHumidity(rh, avgTemp) {
 // Malus humidité : pertinent si chaud + humide (ressenti désagréable)
 // Seuil : T > 24°C ET RH > 65% → malus progressif (jusqu'à -20pts à 38°C/95%)
 // En dessous de 24°C, l'humidité n'est pas gênante
 if (rh == null || avgTemp == null || avgTemp < 24) return 0;
 if (rh <= 65) return 0;
 var tempFactor = Math.min(1, (avgTemp - 24) / 14); // 0 à 24°C → 1 à 38°C
 var rhFactor = Math.min(1, (rh - 65) / 30);        // 0 à 65% → 1 à 95%
 return Math.round(20 * tempFactor * rhFactor);       // malus 0-20 pts
}

function scoreHumidityPlage(rh, avgTemp) {
 // Plage : humidité acceptable même haute si T confortable
 // Mais RH > 80% + T > 30°C = inconfort marqué (surtout tropiques)
 if (rh == null || avgTemp == null || avgTemp < 26) return 0;
 if (rh <= 75) return 0;
 var tempFactor = Math.min(1, (avgTemp - 26) / 12);
 var rhFactor = Math.min(1, (rh - 75) / 20);
 return Math.round(15 * tempFactor * rhFactor);
}

function scoreSun(peakSol) {
 if (peakSol >= 600) return 100;
 if (peakSol >= 300) return 60 + (peakSol - 300) / 300 * 40;
 if (peakSol >= 100) return 20 + (peakSol - 100) / 200 * 40;
 return Math.max(0, peakSol / 100 * 20);
}

function getScoreColor(score) {
 if (score >= 86) return '#1a7a4a';
 if (score >= 76) return '#2d9e60';
 if (score >= 63) return '#84cc16';
 if (score >= 50) return '#f59e0b';
 if (score >= 35) return '#f97316';
 return '#ef4444';
}

function getMainDriver(avgRain, avgTemp, avgWind, sRain, sTemp, sWind, uc) {
 var cfg = UC_CONFIG[uc] || UC_CONFIG.general;
 var penalties = [
  { key:'rain', score: sRain, test: avgRain > 35 },
  { key:'temp_cold', score: sTemp, test: avgTemp != null && avgTemp < cfg.tempMin },
  { key:'temp_hot', score: sTemp, test: avgTemp != null && avgTemp > cfg.tempMax },
  { key:'wind', score: sWind, test: avgWind > 28 }
 ];
 var worst = null;
 for (var i = 0; i < penalties.length; i++) {
  if (penalties[i].test && (!worst || penalties[i].score < worst.score)) worst = penalties[i];
 }
 if (!worst) return null;
 var labels = {
  rain: T.drvRain,
  temp_cold: T.drvCold,
  temp_hot: uc === 'plage' ? T.drvHotBeach : T.drvHotGen,
  wind: T.drvWind
 };
 return labels[worst.key];
}

function getVerdict(score, avgRain, avgTemp, avgWind, uc, isSeasonal) {
 uc = uc || 'general';
 var suffix = isSeasonal ? T.seasonalSuffix : '';
 var label;
 if (score >= 86) label = T.scIdeal;
 else if (score >= 76) label = T.scVeryGood;
 else if (score >= 63) label = T.scGood;
 else if (score >= 50) label = 'Variable';
 else if (score >= 35) label = T.scPoor;
 else label = T.scBad;
 var cfg = UC_CONFIG[uc] || UC_CONFIG.general;
 var driver = getMainDriver(avgRain, avgTemp, avgWind, scoreRain(avgRain), scoreTemp(avgTemp, cfg.tempMin, cfg.tempMax), scoreWind(avgWind), uc);
 var action;
 if (uc === 'ski') {
  if (score >= 76) action = T.actGoodSnow;
  else if (score >= 50) action = T.actCautionThaw;
  else action = T.actBadSnow;
  return label + ' · ' + action + suffix;
 }
 if (uc === 'plage') {
  if (score >= 76) action = T.actOptimalSwim;
  else if (score >= 50) action = driver ? T.actCautionBeach + ' — ' + driver : T.actCautionBeachFull;
  else action = driver ? T.actPoorBeach + ' — ' + driver : T.actPoorBeachFull;
  return label + ' · ' + action + suffix;
 }
 if (score >= 76) {
  action = driver ? T.actBookOk + ' — ' + driver + T.actResidual : T.actBookOk;
 } else if (score >= 50) {
  action = driver ? T.actPlanB + ' — ' + driver : T.actPlanBFull;
 } else {
  action = driver ? T.actUnstable + ' — ' + driver : T.actUnstable;
 }
 return label + ' · ' + action + suffix;
}

function getMainRisk(avgRain, avgTemp, avgWind, uc) {
 var cfg = UC_CONFIG[uc] || UC_CONFIG.general;
 var risks = [];
 if (avgRain > 50) risks.push(T.riskRainLikely.replace('{p}', Math.round(avgRain)));
 else if (avgRain > 30) risks.push(T.riskShowers.replace('{p}', Math.round(avgRain)));
 if (avgTemp < cfg.tempMin) risks.push(T.riskCoolTemp.replace('{t}', fmtTemp(avgTemp)));
 else if (avgTemp > cfg.tempMax) risks.push(T.riskHighHeat.replace('{t}', fmtTemp(avgTemp)));
 if (avgWind > 30) risks.push(T.riskWind.replace('{w}', fmtWind(avgWind)));
 if (risks.length === 0) return T.riskNone;
 return T.riskPrefix + risks.join(' · ');
}

function computeAndRenderScore(sc, rows) {
 _lastRows = rows; _lastSc = sc;
 var uc = currentUseCase;
 var cfg = UC_CONFIG[uc] || UC_CONFIG.general;
 var w = cfg.weights;

 // Compute daily averages
 var rSum=0, wSum=0, tSum=0, tCnt=0, peakSol=0, mmSum=0;
 for (var i=0; i<rows.length; i++) {
 rSum += rows[i].rain;
 wSum += (rows[i].windP50 || 0);
 mmSum += (rows[i].mm || 0);
 if (rows[i].temp != null) { tSum += rows[i].temp; tCnt++; }
 }
 for (var k=0; k<sc.length; k++) if ((sc[k].sol||0) > peakSol) peakSol = sc[k].sol;

 var avgRain = rSum / rows.length;
 var avgWind = wSum / rows.length;
 var avgTemp = tCnt ? tSum / tCnt : null;
 var rhSum = 0, rhCnt = 0;
 for (var j=0; j<rows.length; j++) { if (rows[j].rh != null) { rhSum += rows[j].rh; rhCnt++; } }
 var avgRh = rhCnt ? rhSum / rhCnt : null;

 // Individual scores
 var sRain = scoreRainSmart(avgRain, mmSum, avgTemp);
 var sTemp = scoreTemp(avgTemp, cfg.tempMin, cfg.tempMax);
 var sWind = scoreWind(avgWind);
 var sSun = scoreSun(peakSol);

 var total;

 // ── Ski : logique spécifique (même algo que monthScoreForUC) ─────────────
 if (uc === 'ski') {
  var tmax_ski = rows.length ? Math.max.apply(null, rows.map(function(r){return r.temp||0;})) : (avgTemp||10);
  var tmin_ski = rows.length ? Math.min.apply(null, rows.map(function(r){return r.temp||0;})) : (avgTemp||5);
  var avgMm = mmSum / rows.length;
  var sTempSki;
  if (tmax_ski > 10) sTempSki = 0;
  else if (tmax_ski > 5) sTempSki = Math.max(0, 50 - (tmax_ski - 5) * 10);
  else if (tmax_ski >= -2) sTempSki = 90 + (2 - Math.abs(tmax_ski)) * 2;
  else if (tmax_ski >= -12) sTempSki = 90 - (Math.abs(tmax_ski) - 2) * 3;
  else sTempSki = Math.max(30, 90 - (Math.abs(tmax_ski) - 2) * 3);
  var snowBonus = (tmin_ski < 0 && avgMm > 2) ? Math.min(100, 60 + avgMm * 3) : (tmin_ski < 0 && avgMm > 0 ? 55 : 20);
  var sSunSki = Math.min(100, (peakSol / 50) * 8);
  var sRainSki = tmax_ski > 2 ? Math.max(0, 100 - avgRain * 1.5) : Math.max(40, 100 - avgRain * 0.3);
  total = Math.round(sRainSki * 0.15 + sTempSki * 0.40 + snowBonus * 0.20 + sSunSki * 0.25);

 // ── Plage : logique spécifique ───────────────────────────────────────────
 } else if (uc === 'plage') {
  var tmax_plage = rows.length ? Math.max.apply(null, rows.map(function(r){return r.temp||0;})) : (avgTemp||20);
  var sTempPlage;
  if (tmax_plage < 18) sTempPlage = 0;
  else if (tmax_plage < 22) sTempPlage = (tmax_plage - 18) / 4 * 20;
  else if (tmax_plage < 26) sTempPlage = 20 + (tmax_plage - 22) / 4 * 60;
  else if (tmax_plage <= 35) sTempPlage = 80 + (tmax_plage - 26) / 9 * 20;
  else if (tmax_plage <= 40) sTempPlage = 100 - (tmax_plage - 35) / 5 * 30;
  else sTempPlage = Math.max(40, 70 - (tmax_plage - 40) * 5);
  var sRainPlage = Math.max(0, 100 - avgRain * 1.8);
  var sSunPlage = Math.min(100, (peakSol / 50) * 8);
  var humMalusPlage = scoreHumidityPlage(avgRh, avgTemp);
  total = Math.round(sRainPlage * 0.35 + sTempPlage * 0.45 + sSunPlage * 0.20) - humMalusPlage;

 // ── Général : pondération standard ──────────────────────────────────────
 } else {
  var humMalus = scoreHumidity(avgRh, avgTemp);
  total = Math.round(
   sRain * w.rain / 100 +
   sTemp * w.temp / 100 +
   sWind * w.wind / 100 +
   sSun * w.sun / 100
  ) - humMalus;
 }
 total = Math.min(100, Math.max(0, total));

 var color = getScoreColor(total);

 // Ring animation: circumference 188.5
 var offset = 188.5 * (1 - total / 100);
 var ring = document.getElementById('score-ring');
 ring.style.stroke = color;
 setTimeout(function() { ring.style.strokeDashoffset = offset; }, 50);

 document.getElementById('score-num').textContent = (total/10).toFixed(1) + ' / 10';
 var ucLabels = {
    plage:T.ucScoreBeach, ski:T.ucScoreSki, general:T.ucScoreGeneral
   };
 if (uc === 'general') {
 document.getElementById('score-usecase').textContent = T.ucScoreGeneral;
 document.getElementById('score-risk').innerHTML = T.clickProject;
 } else {
 document.getElementById('score-usecase').textContent = ucLabels[uc] || cfg.label;
 }
 var _isSeas = window._lastDiff != null ? (window._lastDiff > 7) : false;
 document.getElementById('score-verdict').textContent = getVerdict(total, avgRain, avgTemp, avgWind, uc, _isSeas);
 document.getElementById('score-verdict').style.color = color;
 updateScoreTooltip(uc);
 document.getElementById('score-risk').textContent = getMainRisk(avgRain, avgTemp, avgWind, uc);

 // Detail chips — show actual values with colored dot
 var totalMm = Math.round(mmSum * 10) / 10;
 var totalSnow = 0; for (var _s=0; _s<rows.length; _s++) { totalSnow += (rows[_s].snow || 0); } totalSnow = Math.round(totalSnow * 10) / 10;
 // Spread (variabilité) badge
 var allTemps = [];
 for (var _t=0; _t<rows.length; _t++) { if (rows[_t].p25 != null && rows[_t].p75 != null) { allTemps.push(rows[_t].p25); allTemps.push(rows[_t].p75); } }
 var spreadLabel = null, spreadColor = null;
 if (allTemps.length >= 4) {
  allTemps.sort(function(a,b){return a-b;});
  var spread = allTemps[allTemps.length-1] - allTemps[0];
  if (spread <= 8) { spreadLabel = T.spreadStable; spreadColor = '#1a7a4a'; }
  else if (spread >= 16) { spreadLabel = T.spreadVariable; spreadColor = '#f97316'; }
 }
 var chips = [
 { lbl: T.statRain, val: Math.round(avgRain)+'%', score: sRain },
 { lbl: T.chipPrecip, val: fmtPrecip(totalMm > 0 ? totalMm : 0), score: sRain },
 { lbl: T.chipTemp, val: avgTemp!=null?fmtTemp(avgTemp):'–', score: sTemp },
 { lbl: T.chipWind, val: fmtWind(avgWind), score: sWind }
 
 ];
 if (totalSnow > 0.5) chips.push({ lbl: T.chipSnow, val: totalSnow + ' cm', score: 0, color: '#6366f1' });
 if (avgRh != null && avgTemp != null && avgTemp > 22) {
  var rhScore = Math.max(0, 100 - Math.max(0, avgRh - 50) * 1.5);
  chips.push({ lbl: T.chipHumidity, val: Math.round(avgRh)+'%', score: rhScore });
 }
 if (spreadLabel) chips.push({ lbl: spreadLabel, val: '', score: -1, color: spreadColor, noDot: true });
 var chipsEl = document.getElementById('score-chips');
 chipsEl.innerHTML = '';
 for (var b=0; b<chips.length; b++) {
 var chipColor = chips[b].color || getScoreColor(chips[b].score);
 var chip = document.createElement('div');
 chip.className = 'score-chip';
 chip.innerHTML = chips[b].noDot
 ? '<span class="score-chip-lbl" style="padding-left:2px">' + chips[b].lbl + '</span>'
 : '<span class="score-chip-dot" style="background:'+chipColor+'"></span>' +
   '<span class="score-chip-lbl">' + chips[b].lbl + '</span>' +
   '<span class="score-chip-val">' + chips[b].val + '</span>';
 chipsEl.appendChild(chip);
 }
 // Ré-injecter le chip SST s'il a déjà été récupéré
 if (window._lastSSTResult) renderSeaChip(window._lastSSTResult);
}

function updateHero(sc, rows, mainHour) {
 var main=sc[mainHour!=null?mainHour:(13)]||sc[12];
 var temps=[]; for(var i=0;i<sc.length;i++) if(sc[i].temp!=null) temps.push(sc[i].temp);
 var tmin=temps.length?Math.min.apply(null,temps):'-', tmax=temps.length?Math.max.apply(null,temps):'-';
 var rSum=0,wSum=0,peakSol=0;
 for(var j=0;j<rows.length;j++){rSum+=rows[j].rain;wSum+=(rows[j].windP50||0);}
 for(var k=0;k<sc.length;k++) if((sc[k].sol||0)>peakSol) peakSol=sc[k].sol;
 var avgRain=Math.round(rSum/rows.length);
 var skyLbl;
 if(avgRain>55)skyLbl=T.skyRainy;else if(avgRain>35)skyLbl=T.skyCloudy;else if(peakSol>500&&avgRain<20)skyLbl=T.skyClearSky;else if(peakSol>250&&avgRain<30)skyLbl=T.skySunny;else if(peakSol>80)skyLbl=T.skyHazy;else if(peakSol>15)skyLbl=T.skyCloudy;else skyLbl=T.skyOvercast;
 window._heroTemp = main.temp || null;
 document.getElementById('r-temp').innerHTML=fmtTempRaw(main.temp||0)+'<sup>°</sup>';
 document.getElementById('r-range').textContent=fmtTempRaw(tmin)+'° / '+fmtTempRaw(tmax)+'° '+T.duringDayShort;
 var _tfEl=document.getElementById('r-tempfreq');
 var _tf=(sc[13]||sc[12]||{}).tempFreq;
 if(_tf!=null&&_tfEl){_tfEl.textContent=T.tempFreq.replace('{u}',fmtTempUnit()).replace('{t}',fmtTempRaw(main.temp||0)).replace('{p}',_tf);_tfEl.style.display='block';}
 else if(_tfEl){_tfEl.style.display='none';}
 var _siEl=document.getElementById('r-seasinfo');
 if(_siEl){
  var _to=window._seasTempOffset, _ro=window._seasRainOffset;
  if(_to!=null && Math.abs(_to)>=0.3){
   var _tSign=_to>0?'+':'', _parts=[_tSign+Math.round(_to*10)/10+'° /ECMWF'];
   if(_ro!=null && Math.abs(_ro)>=3) _parts.push((_ro>0?'+':'')+_ro+'% '+T.wordRain);
   _siEl.textContent=T.seasonalCorrection+' '+_parts.join(' · ');
   _siEl.style.display='block';
  } else { _siEl.style.display='none'; }
 }
 document.getElementById('r-cond').textContent=getLabel(main.h,main.temp,main.sol,main.rain,main.mm||0,main.snow||0,main.p25);
 document.getElementById('r-icon').innerHTML=getIcon(main.h,main.temp,main.sol,main.rain,main.mm||0,main.snow||0,main.p25);
 document.getElementById('r-rain').textContent=avgRain+'%';
 document.getElementById('r-wind').textContent=fmtWind(Math.round(wSum/rows.length));
 document.getElementById('r-sky').textContent=skyLbl;
 computeAndRenderScore(sc, rows);

 // Alerte neige
 var _snowAlert = document.getElementById('snow-alert');
 if (!_snowAlert) {
 _snowAlert = document.createElement('div');
 _snowAlert.id = 'snow-alert';
 _snowAlert.style.cssText = 'background:#ede9fe;border:1.5px solid #6366f1;border-radius:10px;padding:8px 14px;font-size:13px;font-weight:700;color:#4f46e5;display:none;margin-top:10px;text-align:center';
 var heroTop = document.querySelector('.hero-top');
 if (heroTop) heroTop.appendChild(_snowAlert);
 }
 var _snowRows = rows || sc;
 var _snowTotal = 0; for (var _si=0; _si<_snowRows.length; _si++) _snowTotal += (_snowRows[_si].snow||0);
 var _snowHours = 0, _snowFirstH = -1, _snowLastH = -1;
 if (_snowTotal < 0.5) {
 for (var _si=0; _si<_snowRows.length; _si++) {
 var _r = _snowRows[_si];
 var _t = (_r.p25 != null ? _r.p25 : _r.temp) || 99;
 if (_t <= 2 && (_r.mm||0) > 0.1 && (_r.rain||0) > 15) {
 _snowHours++;
 if (_snowFirstH < 0) _snowFirstH = _r.h;
 _snowLastH = _r.h;
 }
 }
 } else {
 // find hours with actual snowfall
 for (var _si=0; _si<_snowRows.length; _si++) {
 if ((_snowRows[_si].snow||0) > 0) {
 if (_snowFirstH < 0) _snowFirstH = _snowRows[_si].h;
 _snowLastH = _snowRows[_si].h;
 }
 }
 }
 function _snowTimeLbl(h) {
 if (h < 0) return '';
 if (h >= 22 || h < 6) return ' · la nuit';
 if (h < 10) return ' · le matin';
 if (h < 14) return T.duringDay;
 return ' · l’après-midi';
 }
 var _timeLbl = (_snowFirstH >= 0) ? _snowTimeLbl(_snowFirstH) : '';
 if (_snowTotal > 0.5) {
 _snowAlert.style.display = 'block';
 _snowAlert.textContent = T.snowExpected + _timeLbl + ' · ' + Math.round(_snowTotal*10)/10 + T.snowCmTotal;
 } else if (_snowHours >= 2) {
 _snowAlert.style.display = 'block';
 _snowAlert.textContent = T.snowLikely + _timeLbl + ' · ' + _snowHours + T.snowHoursBelow;
 } else if (_snowHours >= 1) {
 _snowAlert.style.display = 'block';
 _snowAlert.textContent = T.snowPossible + _timeLbl + T.snowNearFreezing;
 } else {
 _snowAlert.style.display = 'none';
 }
}

/* ── BANDE CONTEXTE ±3J (J+8 et au-delà) ── */




function showResults(sc, rows, isForecast, noteText, diffDays) {
 setConfBadge(diffDays);
 applyHorizonWording(diffDays);
 document.getElementById('score-block').style.display = 'block';
 showSection('hero');
 document.getElementById('uc-filter-wrap').style.display='block';
 showSection('sec-hourly');
 renderHourly(sc);
 if(!isForecast){
 showSection('sec-scenarios');
 var pessRows = genPess(rows);
 var optRows = genOpt(rows);
 renderScCard(pessRows,'sc-pess-strip','sc-pess-stats');
 renderScCard(optRows,'sc-opt-strip','sc-opt-stats');
 updateScenarioLabels(pessRows, optRows);
 }
 if(noteText){var fn=document.getElementById('foot-note');fn.innerHTML=noteText;fn.style.display='block';}
 setTimeout(function(){var el=document.getElementById('uc-filter-wrap');if(el)el.scrollIntoView({behavior:'smooth',block:'start'});},120);
}

/* AUTOCOMPLETE */
var acTimer=null, acIdx=-1, acData=[], selectedLoc=null;
function flagEmoji(code){
 if(!code||code.length!==2)return'';
 // DOM-TOM : pas de fichier drapeau propre, on utilise le drapeau FR
 var display = {'GF':'FR','GP':'FR','MQ':'FR','RE':'FR','PM':'FR','YT':'FR','NC':'FR','PF':'FR','WF':'FR','MF':'FR','BL':'FR'}[code] || code;
 return '<img src="'+CFG.flagBase+display.toLowerCase()+'.png" width="20" height="15" alt="'+code.toUpperCase()+'" style="vertical-align:middle;border-radius:2px;margin-right:4px" onerror="this.style.display=\'none\'">';
}

function hideAC(){document.getElementById('ac-list').style.display='none';acIdx=-1;}
function showAC(items){
 // Trier par population décroissante — la grande ville passe avant le hameau homonyme
 var sorted = (items||[]).slice().sort(function(a,b){ return (b.population||0)-(a.population||0); });
 acData=sorted;acIdx=-1;var list=document.getElementById('ac-list');list.innerHTML='';
 if(!acData.length){list.style.display='none';return;}
 for(var i=0;i<acData.length;i++){(function(item,pos){var div=document.createElement('div');div.className='ac-item';var sub=getAcSub(item);div.innerHTML='<span>'+flagEmoji(item.country_code)+' '+item.name+'</span><span class="ac-sub">'+sub+'</span>';div.onmousedown=function(e){e.preventDefault();selectAC(pos);};list.appendChild(div);})(acData[i],i);}
 list.style.display='block';
}


var COUNTRY_NAMES = CFG.countryFull;
function getCountryName(item) {
 return item.country || COUNTRY_NAMES[item.country_code] || item.country_code || '';
}

var DOMTOM_CODES = ['GP','MQ','RE','GF','YT','PM','NC','PF','WF','BL','MF'];
function isFranceMetro(item) {
 // France métro : lat 41-52, lon -5.5 à 10
 if (item.country_code !== 'FR') return false;
 var lat = parseFloat(item.latitude), lon = parseFloat(item.longitude);
 return lat >= 41 && lat <= 52 && lon >= -5.5 && lon <= 10;
}


var COUNTRY_NAMES = {
 'GP':'Guadeloupe','MQ':'Martinique','RE':'La Réunion','GF':'Guyane française',
 'YT':'Mayotte','PM':'Saint-Pierre-et-Miquelon','NC':'Nouvelle-Calédonie',
 'PF':'Polynésie française','WF':'Wallis-et-Futuna','BL':'Saint-Barthélemy',
 'MF':'Saint-Martin','FR':'France','BE':'Belgique','CH':'Suisse','LU':'Luxembourg',
 'CA':'Canada','US':'États-Unis','GB':'Royaume-Uni','DE':'Allemagne','ES':'Espagne',
 'IT':'Italie','PT':'Portugal','NL':'Pays-Bas','MA':'Maroc','TN':'Tunisie',
 'DZ':'Algérie','SN':'Sénégal','CI':'Côte d\'Ivoire','CM':'Cameroun'
};
function countryName(code, fallback) {
 return COUNTRY_NAMES[code] || fallback || code || '';
}

function getFrTerritory(lat, lon) {
 lat = parseFloat(lat); lon = parseFloat(lon);
 // France métropolitaine
 if (lat >= 41 && lat <= 52 && lon >= -5.5 && lon <= 10) return null;
 // DOM-TOM par coordonnées
 if (lat >= 14 && lat <= 18 && lon >= -63 && lon <= -60) return 'Guadeloupe';
 if (lat >= 14 && lat <= 15 && lon >= -61.5 && lon <= -60.5) return 'Martinique';
 if (lat >= -22 && lat <= -20 && lon >= 55 && lon <= 56) return 'La Réunion';
 if (lat >= 2 && lat <= 6 && lon >= -55 && lon <= -51) return 'Guyane';
 if (lat >= -14 && lat <= -12 && lon >= 44 && lon <= 46) return 'Mayotte';
 if (lat >= -23 && lat <= -20 && lon >= 163 && lon <= 168) return 'Nouvelle-Calédonie';
 if (lat >= -18 && lat <= -14 && lon >= -150 && lon <= -148) return 'Polynésie française';
 if (lat >= 46 && lat <= 48 && lon >= -57 && lon <= -52) return 'Saint-Pierre-et-Miquelon';
 return 'Outre-mer';
}

function getAcSub(item) {
 var FR_TERRITORIES = {'GF':'Guyane française','GP':'Guadeloupe','MQ':'Martinique','RE':'La Réunion','PM':'Saint-Pierre-et-Miquelon','YT':'Mayotte','NC':'Nouvelle-Calédonie','PF':'Polynésie française'};
 var isFrDom = !!FR_TERRITORIES[item.country_code];
 if (item.country_code === 'FR' || isFrDom) {
 var terr = isFrDom ? FR_TERRITORIES[item.country_code] : getFrTerritory(item.latitude, item.longitude);
 var region = terr || item.admin1 || '';
 return region + (region ? ', ' : '') + 'France';
 }
 return (item.admin1 || '') + (item.admin1 && item.country ? ', ' : '') + (item.country || '');
}

function selectAC(i){
 var item=acData[i];if(!item)return;
 // Pour FR : ne jamais afficher admin1, juste le pays
 var FR_DOM = {'GF':1,'GP':1,'MQ':1,'RE':1,'PM':1,'YT':1,'NC':1,'PF':1};
 var FR_TERRITORY_NAMES = {'GF':'Guyane française','GP':'Guadeloupe','MQ':'Martinique','RE':'La Réunion','PM':'Saint-Pierre-et-Miquelon','YT':'Mayotte','NC':'Nouvelle-Calédonie','PF':'Polynésie française'};
 var isFrDom = !!FR_DOM[item.country_code];
 var region = (item.country_code === 'FR' || isFrDom) ? (isFrDom ? FR_TERRITORY_NAMES[item.country_code] : '') : (item.admin1 || '');
 var country = isFrDom ? 'France' : getCountryName(item);
 selectedLoc={lat:item.latitude,lon:item.longitude,name:item.name,region:region,country:country};
 var label = item.name;
 if (region) label += ', ' + region;
 if (country) label += ' (' + country + ')';
 document.getElementById('inp-city').value = label;
 hideAC();
}
function normalizeQuery(s){
 // Remplacer espaces par tirets + supprimer accents pour meilleur matching API
 return s.replace(/ /g,'-').normalize('NFD').replace(/[̀-ͯ]/g,'');
}
function fetchAC(q){
 var hint=document.getElementById('city-hint');
 if(hint) hint.style.display='none';
 var base='https://geocoding-api.open-meteo.com/v1/search?count=6&language=fr&name=';
 var p1=fetch(base+encodeURIComponent(q)).then(function(r){return r.json();}).then(function(d){return d.results||[];});
 // Si espaces : aussi envoyer version normalisée (tirets + sans accents)
 var qNorm = normalizeQuery(q);
 var p2 = q.indexOf(' ')>=0
 ? fetch(base+encodeURIComponent(qNorm)).then(function(r){return r.json();}).then(function(d){return d.results||[];})
 : Promise.resolve([]);
 Promise.all([p1,p2]).then(function(both){
 var seen={}, merged=[];
 both[0].concat(both[1]).forEach(function(item){
 var key=item.name+'|'+item.latitude+'|'+item.longitude;
 if(!seen[key]){seen[key]=1;merged.push(item);}
 });
 merged.sort(function(a,b){return (b.population||0)-(a.population||0);});
 showAC(merged.slice(0,6));
 }).catch(function(){hideAC();});
}

/* RUN */
function run() {
 var city=document.getElementById('inp-city').value.trim();
 var _dateEl=document.getElementById('inp-date'); var dval=_dateEl._isoValue||_dateEl.value;
 var btnEl=document.getElementById('btn-go'), errEl=document.getElementById('err-box'), progEl=document.getElementById('prog-wrap');
 if(!city){
 errEl.textContent='⚠ Entrez une ville ou une destination avant de continuer.';
 errEl.style.display='block';
 var cityInp=document.getElementById('inp-city');
 cityInp.style.borderColor='#dc2626';cityInp.focus();
 cityInp.addEventListener('input',function(){cityInp.style.borderColor='';errEl.style.display='none';},{once:true});
 return;
 }
 if(!dval){
 errEl.textContent=T.errDate;
 errEl.style.display='block';
 var dateInp=document.getElementById('inp-date');
 dateInp.style.borderColor='#dc2626';dateInp.focus();
 dateInp.addEventListener('change',function(){dateInp.style.borderColor='';errEl.style.display='none';},{once:true});
 return;
 }
 var parts=dval.split('-');
 if(parts.length!==3){errEl.textContent='⚠ Format de date invalide.';errEl.style.display='block';return;}
 var yr=parseInt(parts[0],10), mo=parseInt(parts[1],10)-1, da=parseInt(parts[2],10);
 window._lastYr=yr; window._lastMo=mo; window._lastDa=da; window._lastDiff=null;
 var today=new Date();today.setHours(0,0,0,0);
 var target=new Date(yr,mo,da,0,0,0);
 var diffDays=Math.round((target.getTime()-today.getTime())/86400000);
 window._lastDiff=diffDays;
 btnEl.disabled=true; errEl.style.display='none';
 hideSection('hero');hideSection('sec-hourly');hideSection('sec-scenarios');
 document.getElementById('foot-note').style.display='none';
 progEl.style.display='block';setP(0,T.progLocating);
 // Avertir si pas de sélection depuis la liste (risque de mauvaise ville)
 if (!selectedLoc) {
 var errEl2 = document.getElementById('err-box');
 errEl2.textContent = T.errCity;
 errEl2.style.display = 'block';
 setTimeout(function(){errEl2.style.display='none';}, 4000);
 }
 var locP=selectedLoc?Promise.resolve(selectedLoc):geocode(city);
 locP.then(function(loc){
 setP(5,loc.name+T.progFound);
 document.getElementById('r-loc').textContent=loc.name+' — '+(loc.country||'');
 document.getElementById('r-date').textContent=new Date(yr,mo,da,12,0,0).toLocaleDateString(CFG.dateLocale,{weekday:'long',day:'numeric',month:'long',year:'numeric'});
 renderAstro(loc.lat,loc.lon,yr,mo,da);
 // Lancer SST en parallèle (silencieux — n'affecte pas le score principal)
 window._lastSSTResult = null;
 var slug = slugFromName(loc.name);
 fetchMarineSST(loc.lat,loc.lon,yr,mo,da,slug).then(function(sstResult){
 window._lastSSTResult = sstResult;
 var old = document.getElementById('sea-chip');
 if (old) old.parentNode.removeChild(old);
 renderSeaChip(sstResult);
 });
 if(diffDays>=0&&diffDays<=7){
 setP(30,T.progFetching);
 return fetchForecast(loc.lat,loc.lon,yr,mo,da).then(function(rows){
 renderAstro(loc.lat,loc.lon,yr,mo,da);
 setP(100,T.progDone);var _curH=13;if(diffDays===0){var _now=new Date(Date.now()+(_locTzOffset||0)*1000+new Date().getTimezoneOffset()*60000);_curH=_now.getHours();}updateHero(rows,rows,_curH);showResults(rows,rows,true,T.noteLive,diffDays);progEl.style.display='none';btnEl.disabled=false;
 });
 }
 return buildClimatology(loc.lat,loc.lon,yr,mo,da).then(function(rows){
 if(diffDays>7&&diffDays<=210){setP(92,T.progEcmwf);return fetchSeasonal(loc.lat,loc.lon,yr,mo,da).then(function(seas){return applySeasonalCorrection(rows,seas);});}
 return rows;
 }).then(function(rows){
 renderAstro(loc.lat,loc.lon,yr,mo,da);
 setP(100,T.progDone);seedRand(makeSeed(loc.lat,loc.lon,yr,mo,da));var sc=genMain(rows);updateHero(sc,rows);
    var note=(diffDays>7&&diffDays<=210)?T.noteEcmwf:T.noteClimate;
    showResults(sc,rows,false,note,diffDays);
    // Snow depth — uniquement si UC ski, en parallèle (silencieux si erreur)
    var _sdEl = document.getElementById('snow-depth-info');
    if (_sdEl) _sdEl.style.display = 'none';
    if (currentUseCase === 'ski' && _sdEl) {
     fetchSnowDepth(loc.lat, loc.lon, yr, mo, da).then(function(res) {
      if (!res) return;
      var elev = res.elevation ? Math.round(res.elevation) : null;
      if (elev && elev < 600) {
       _sdEl.textContent = T.snowAltLow.replace('{e}', elev);
       _sdEl.style.color = '#94a3b8';
      } else if (res.depth != null) {
       var elevStr = elev ? T.snowElevAt.replace('{e}', elev) : '';
       _sdEl.textContent = T.snowEst.replace('{d}', res.depth).replace('{e}', elevStr);
       _sdEl.style.color = '#6366f1';
      } else {
       _sdEl.textContent = T.snowNA;
       _sdEl.style.color = '#94a3b8';
      }
      _sdEl.style.display = 'block';
     });
    }
    progEl.style.display='none';btnEl.disabled=false;
 });
 }).catch(function(err){errEl.textContent=T.errPrefix+err.message;errEl.style.display='block';progEl.style.display='none';showSection('empty');btnEl.disabled=false;});
}


/* ── TOOLTIP SCORE ── */
function toggleScoreTooltip() {
 var tt = document.getElementById('score-tooltip');
 tt.classList.toggle('visible');
 // close on outside click
 if (tt.classList.contains('visible')) {
 setTimeout(function() {
 document.addEventListener('click', function closeTooltip(e) {
 if (!tt.contains(e.target) && e.target.id !== 'score-info-btn') {
 tt.classList.remove('visible');
 }
 document.removeEventListener('click', closeTooltip);
 });
 }, 10);
 }
}

function updateScoreTooltip(uc) {
 var cfg = UC_CONFIG[uc] || UC_CONFIG.general;
 var w = cfg.weights;
 var tt = document.getElementById('score-tooltip');
 var ucName = {plage:T.ucBeach,ski:T.ucSki,general:T.ucGeneral}[uc] || uc;
 tt.innerHTML =
 '<strong style="font-size:12px">Score · ' + ucName + '</strong><br>' +
 T.tipRainLbl + w.rain + '%<br>' +
 T.tipTempLbl + w.temp + '%<br>' +
 T.tipWindLbl + w.wind + '%<br>' +
 T.tipSunLbl + w.sun + '%<br>' +
 '<span style="opacity:.6;font-size:10px">'+T.tipIdealRange+' ' + fmtTempRaw(cfg.tempMin) + '–' + fmtTempRaw(cfg.tempMax) + fmtTempUnit() + '</span>';
}

/* ── RECOMMENDED BADGES (annual view) ── */
function markRecommendedMonths() {
 var cards = document.querySelectorAll('.month-card');
 if (!cards.length) return;
 var uc = currentUseCase === 'general' ? null : currentUseCase;
 if (!uc) return; // no use case = no recommendation

 // Collect scores for each card
 var scores = [];
 for (var i = 0; i < cards.length; i++) {
 var monthIdx = parseInt(cards[i].dataset.monthIdx);
 scores.push({ idx: i, monthIdx: monthIdx, score: parseFloat(cards[i].dataset.score || 0) });
 }
 if (!scores.length) return;

 scores.sort(function(a, b) { return b.score - a.score; });

 // Mark strictly top 1 or 2 (by rank, not by threshold)
 var topIdxs = [];
 for (var k = 0; k < Math.min(2, scores.length); k++) {
 if (scores[k].score >= 55) topIdxs.push(scores[k].idx);
 }

 for (var j = 0; j < cards.length; j++) {
 if (topIdxs.indexOf(j) >= 0) {
 cards[j].classList.add('recommended');
 } else {
 cards[j].classList.remove('recommended');
 }
 }
}


/* ── MODE SWITCH ── */
function switchMode(mode) {
 var isDate = mode === 'date';
 document.getElementById('mode-date').className = 'mode-btn' + (isDate ? ' active' : '');
 document.getElementById('mode-annual').className = 'mode-btn' + (!isDate ? ' active' : '');
 document.getElementById('annual-wrap').style.display = isDate ? 'none' : 'block';
 // show/hide date-mode elements
 var dateEls = ['date-form','hero','sec-hourly','sec-scenarios','empty','foot-note','uc-filter-wrap'];
 dateEls.forEach(function(id){
 var el = document.getElementById(id);
 if (el) el.style.display = isDate ? (id === 'empty' ? 'block' : el._wasDisplay || '') : 'none';
 });
 if (isDate) document.getElementById('empty').style.display = 'block';

}

/* ── ANNUAL AUTOCOMPLETE ── */
var annAcTimer = null, annAcIdx = -1, annAcData = [], annSelectedLoc = null;

function hideAnnAC() { document.getElementById('ann-ac-list').style.display = 'none'; annAcIdx = -1; }
function showAnnAC(items) {
 annAcData = items || []; annAcIdx = -1;
 var list = document.getElementById('ann-ac-list'); list.innerHTML = '';
 if (!annAcData.length) { list.style.display = 'none'; return; }
 for (var i = 0; i < annAcData.length; i++) {
 (function(item, pos) {
 var div = document.createElement('div'); div.className = 'ac-item';
 var sub = getAcSub(item);
 div.innerHTML = '<span>' + flagEmoji(item.country_code) + ' ' + item.name + '</span><span class="ac-sub">' + sub + '</span>';
 div.onmousedown = function(e) { e.preventDefault(); selectAnnAC(pos); };
 list.appendChild(div);
 })(annAcData[i], i);
 }
 list.style.display = 'block';
}
function selectAnnAC(i) {
 var item = annAcData[i]; if (!item) return;
 var region2 = (item.country_code === 'FR') ? '' : (item.admin1 || '');
 var country2 = getCountryName(item);
 annSelectedLoc = { lat: item.latitude, lon: item.longitude, name: item.name, region: region2, country: country2 };
 var label2 = item.name;
 if (region2) label2 += ', ' + region2;
 if (country2) label2 += ' (' + country2 + ')';
 document.getElementById('ann-city').value = label2;
 hideAnnAC();
}

/* ── ANNUAL DATA ── */
function runAnnual() {
 var city = document.getElementById('ann-city').value.trim();
 if (!city) {
 err.textContent = '⚠ Entrez une ville ou une destination avant de continuer.';
 err.style.display = 'block';
 var annInp = document.getElementById('ann-city');
 annInp.style.borderColor = '#dc2626'; annInp.focus();
 annInp.addEventListener('input', function(){ annInp.style.borderColor = ''; err.style.display = 'none'; }, { once: true });
 return;
 }
 var btn = document.getElementById('ann-btn');
 var prog = document.getElementById('ann-prog-wrap');
 var err = document.getElementById('ann-err-box');
 var res = document.getElementById('annual-result');
 btn.disabled = true; err.style.display = 'none'; res.style.display = 'none'; prog.style.display = 'block';
 setAnnP(0, T.progLocating);

 var locP = annSelectedLoc ? Promise.resolve(annSelectedLoc) : geocode(city);
 locP.then(function(loc) {
 setAnnP(10, T.progFetchData);
 var cached = findCachedMonthly(loc.lat, loc.lon);
 var archiveP = cached
 ? (setAnnP(30, T.progCache), Promise.resolve(cached))
 : (setAnnP(10, T.progDownload), MONTHLY_CACHE_PROMISE.then(function(){
 var c2 = findCachedMonthly(loc.lat, loc.lon);
 return c2 ? c2 : fetchAnnualArchive(loc);
 }));
 var seasP = fetchAnnualSeasonal(loc.lat, loc.lon);
 return Promise.all([archiveP, seasP]).then(function(results) {
 var monthly = results[0], seasonal = results[1] || {};
 // Inject fiche reference scores when destination is known
 // findFicheScores : lookup avec proximité 0.15° (géocodeur ≠ coords fiches)
 var _ficheMatch = findFicheScores(loc.lat, loc.lon);
 var _ficheKey = _ficheMatch[0] || (loc.lat + ',' + loc.lon);
 var _ficheRef = _ficheMatch[1] || null;
 if (_ficheRef) { for (var _fi=0; _fi<12; _fi++) monthly[_fi].ficheScore = _ficheRef[_fi]; }
 // Calcul ancré scoring.py pour destinations inconnues (ficheScore absent)
 computeAnchoredScores(monthly, _ficheKey);
 // Blend seasonal correction into relevant months
 var now = new Date();
 var nowMo = now.getMonth();
 for (var s = 0; s < 7; s++) {
 var mi = (nowMo + s) % 12;
 if (!seasonal[mi] || monthly[mi].avgTemp == null) continue;
 var seas = seasonal[mi];
 var clim = monthly[mi];
 // Temperature: blend 60% clim + 40% seasonal forecast
    var delta = seas.tMean - clim.avgTemp;
    var appliedTDelta = Math.round(delta * 0.4 * 10) / 10;
    clim.avgTemp = Math.round((clim.avgTemp + delta * 0.4) * 10) / 10;
    clim.avgTmax = clim.avgTmax != null ? Math.round((clim.avgTmax + delta * 0.4) * 10) / 10 : null;
    clim.avgTmin = clim.avgTmin != null ? Math.round((clim.avgTmin + delta * 0.4) * 10) / 10 : null;
    clim.seasTempDelta = Math.abs(appliedTDelta) >= 0.3 ? appliedTDelta : null;
    // Rain: blend 60% clim + 40% seasonal
    var appliedRainDelta = null;
    if (seas.rainProb != null) {
      var oldRain = clim.rainPct;
      clim.rainPct = Math.min(100, Math.max(0, Math.round(clim.rainPct * 0.6 + seas.rainProb * 0.4)));
      appliedRainDelta = clim.rainPct - oldRain;
    }
    clim.seasRainDelta = (appliedRainDelta != null && Math.abs(appliedRainDelta) >= 3) ? appliedRainDelta : null;
    clim.hasSeasonal = true;
 }
 setAnnP(100, T.progDone);
 renderAnnual(loc, monthly);
 prog.style.display = 'none';
 btn.disabled = false;
 });
 }).catch(function(e) {
 err.textContent = T.errPrefix + e.message;
 err.style.display = 'block';
 prog.style.display = 'none';
 btn.disabled = false;
 });
}

function setAnnP(p, lbl) {
 document.getElementById('ann-prog-bar').style.width = p + '%';
 document.getElementById('ann-prog-pct').textContent = p + '%';
 if (lbl) document.getElementById('ann-prog-lbl').textContent = lbl;
}

function fetchAnnualArchive(loc) {
 var now = new Date();
 var endYr = now.getFullYear() - 1;
 var startYr = endYr - 9; // 10 years
 var startDate = startYr + '-01-01';
 var endDate = endYr + '-12-31';
 var url = 'https://archive-api.open-meteo.com/v1/archive?latitude=' + loc.lat + '&longitude=' + loc.lon +
 '&start_date=' + startDate + '&end_date=' + endDate +
 '&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,shortwave_radiation_sum,sunshine_duration&timezone=auto';
 return fetch(url).then(function(r) {
 if (!r.ok) {
 return r.json().catch(function(){ return {}; }).then(function(body){
 var reason = (body && body.reason) ? body.reason : ('HTTP ' + r.status);
 throw new Error(T.errDataReason.replace('{r}', reason));
 });
 }
 return r.json();
 }).then(function(data) {
 if (!data || !data.daily || !data.daily.time || data.daily.time.length === 0) {
 throw new Error(T.errData);
 }
 setAnnP(70, T.progAggregation);
 return aggregateByMonth(data);
 }).catch(function(e) {
 // Fallback: retry without sunshine_duration
 if (e.message && e.message.indexOf('sunshine') >= 0) {
 var url2 = 'https://archive-api.open-meteo.com/v1/archive?latitude=' + loc.lat + '&longitude=' + loc.lon +
 '&start_date=' + startDate + '&end_date=' + endDate +
 '&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,shortwave_radiation_sum&timezone=auto';
 return fetch(url2).then(function(r) {
 if (!r.ok) throw new Error(T.errData);
 return r.json();
 }).then(function(data) {
 setAnnP(70, T.progAggregation);
 return aggregateByMonth(data);
 });
 }
 throw e;
 });
}

function fetchAnnualSeasonal(lat, lon) {
 var now = new Date();
 var start = now.toISOString().split('T')[0];
 var end = new Date(now.getTime() + 210 * 86400000).toISOString().split('T')[0];
 var url = 'https://seasonal-api.open-meteo.com/v1/seasonal?latitude=' + lat + '&longitude=' + lon +
 '&daily=temperature_2m_mean,precipitation_sum&start_date=' + start + '&end_date=' + end;
 return fetch(url).then(function(r) { if (!r.ok) return null; return r.json(); })
 .then(function(data) {
 if (!data || !data.daily || !data.daily.time) return {};
 var times = data.daily.time;
 var ks = Object.keys(data.daily);
 // Buckets by calendar month (0-11)
 var buckets = {};
 for (var i = 0; i < times.length; i++) {
 var mo = parseInt(times[i].split('-')[1], 10) - 1;
 if (!buckets[mo]) buckets[mo] = { temps: [], precips: [] };
 // Collect all member values for this day
 for (var k = 0; k < ks.length; k++) {
 var key = ks[k];
 var val = data.daily[key][i];
 if (val == null) continue;
 if (key.indexOf('temperature_2m_mean') === 0) buckets[mo].temps.push(val);
 if (key.indexOf('precipitation_sum') === 0) buckets[mo].precips.push(val);
 }
 }
 // Aggregate each month
 var result = {};
 var moKeys = Object.keys(buckets);
 for (var m = 0; m < moKeys.length; m++) {
 var mk = parseInt(moKeys[m], 10);
 var b = buckets[mk];
 if (!b.temps.length) continue;
 var tSum = 0; for (var t = 0; t < b.temps.length; t++) tSum += b.temps[t];
 var wet = 0; for (var p = 0; p < b.precips.length; p++) if (b.precips[p] > 0.5) wet++;
 result[mk] = {
 tMean: tSum / b.temps.length,
 rainProb: b.precips.length ? Math.round(wet / b.precips.length * 100) : null
 };
 }
 return result;
 }).catch(function() { return {}; });
}

function p50(arr) {
  if (!arr || !arr.length) return null;
  var s = arr.slice().sort(function(a,b){return a-b;});
  var mid = Math.floor(s.length / 2);
  return s.length % 2 ? s[mid] : (s[mid-1] + s[mid]) / 2;
}

function aggregateByMonth(data) {
 // buckets[0..11] for Jan..Dec
 var buckets = [];
 for (var m = 0; m < 12; m++) buckets.push({ tmax: [], tmin: [], precip: [], rad: [], sun: [] });

 var times = data.daily.time;
 var tmax = data.daily.temperature_2m_max;
 var tmin = data.daily.temperature_2m_min;
 var prec = data.daily.precipitation_sum;
 var rad = data.daily.shortwave_radiation_sum || [];
 var sunD = data.daily.sunshine_duration || []; // seconds/day

 for (var i = 0; i < times.length; i++) {
   var mo = parseInt(times[i].split('-')[1], 10) - 1;
   if (tmax[i] != null) buckets[mo].tmax.push(tmax[i]);
   if (tmin[i] != null) buckets[mo].tmin.push(tmin[i]);
   if (prec[i] != null) buckets[mo].precip.push(prec[i]);
   if (rad[i] != null) buckets[mo].rad.push(rad[i]);
   if (sunD[i] != null) buckets[mo].sun.push(sunD[i]);
 }

 return buckets.map(function(b, idx) {
   var avgTmax = p50(b.tmax);
   var avgTmin = p50(b.tmin);
   var avgTemp = (avgTmax != null && avgTmin != null) ? (avgTmax + avgTmin) / 2 : null;
   var rainDays = b.precip.filter(function(v){return v>1;}).length;
   var rainPct = b.precip.length ? Math.round(rainDays / b.precip.length * 100) : 0;
   var medRad = p50(b.rad) || 0;
   var sunHrs = b.sun.length ? Math.min(14, p50(b.sun) / 3600) : Math.min(14, medRad / 3.6);
   var avgPrecipMm = b.precip.length ? Math.round((p50(b.precip) || 0) * 10) / 10 : 0;
   return { month: idx, avgTmax: avgTmax, avgTmin: avgTmin, avgTemp: avgTemp, rainPct: rainPct, sunHrs: sunHrs, avgRad: medRad, avgPrecipMm: avgPrecipMm };
 });
}

function monthScoreForUC(d, uc) {
 // Si score de référence disponible (fiche statique) → l'utiliser directement
 if ((!uc || uc === 'general') && d.ficheScore != null) return d.ficheScore;
 var cfg = UC_CONFIG[uc] || UC_CONFIG.general;
 var w = cfg.weights;
 var sRain = scoreRainSmart(d.rainPct, d.avgPrecipMm, d.avgTemp);
 var sSun = scoreSun((d.sunHrs || 0) * 50);
 if (!uc || uc === 'general') {
 // ficheScore garanti par computeAnchoredScores (appelé dans runAnnual)
 // scoring.py est la source de vérité — ne pas recalculer ici
 return d.ficheScore != null ? Math.round(d.ficheScore * 10) : 50;
 }
 // ── Ski : logique spécifique ──────────────────────────────────────────────
 if (uc === 'ski') {
 var tmax = d.avgTmax != null ? d.avgTmax : (d.avgTemp != null ? d.avgTemp + 4 : 5);
 var tmin = d.avgTmin != null ? d.avgTmin : (d.avgTemp != null ? d.avgTemp - 4 : 0);
 var rain = d.rainPct || 0;
 var mm = d.avgPrecipMm || 0;
 var sun = d.sunHrs || 0;
 // Température : idéal -8 à 2°C (neige sèche) — trop chaud = 0 (pas de neige)
 var sTempSki;
 if (tmax > 10) sTempSki = 0; // plus de neige garantie
 else if (tmax > 5) sTempSki = Math.max(0, 50 - (tmax - 5) * 10); // dégel
 else if (tmax >= -2) sTempSki = 90 + (2 - Math.abs(tmax)) * 2; // idéal
 else if (tmax >= -12) sTempSki = 90 - (Math.abs(tmax) - 2) * 3; // froid acceptable
 else sTempSki = Math.max(30, 90 - (Math.abs(tmax) - 2) * 3); // très froid
 // Neige : précipitations avec froid = bonus (enneigement probable)
 var snowBonus = (tmin < 0 && mm > 2) ? Math.min(100, 60 + mm * 3) : (tmin < 0 && mm > 0 ? 55 : 20);
 // Soleil : ciel bleu = excellent en ski
 var sSunSki = Math.min(100, sun * 8);
 // Pluie chaude (tmax > 2 et pluie) = très mauvais (neige fondue, verglas)
 var sRainSki = tmax > 2 ? Math.max(0, 100 - rain * 1.5) : Math.max(40, 100 - rain * 0.3);
 return Math.round(sRainSki * 0.15 + sTempSki * 0.40 + snowBonus * 0.20 + sSunSki * 0.25);
 }
 // ── Plage : logique spécifique ───────────────────────────────────────────
 if (uc === 'plage') {
  var tmax = d.avgTmax != null ? d.avgTmax : (d.avgTemp != null ? d.avgTemp + 5 : 20);
  var rain = d.rainPct || 0;
  var sun = d.sunHrs || 0;
  // Température : idéal 26-35°C pour tmax — en dessous de 22°C inapte à la plage
  var sTempPlage;
  if (tmax < 18) sTempPlage = 0;
  else if (tmax < 22) sTempPlage = (tmax - 18) / 4 * 20;           // 0→20
  else if (tmax < 26) sTempPlage = 20 + (tmax - 22) / 4 * 60;     // 20→80
  else if (tmax <= 35) sTempPlage = 80 + (tmax - 26) / 9 * 20;    // 80→100
  else if (tmax <= 40) sTempPlage = 100 - (tmax - 35) / 5 * 30;   // 100→70
  else sTempPlage = Math.max(40, 70 - (tmax - 40) * 5);
  // Pluie : très pénalisante (journée plage gâchée)
  var sRainPlage = Math.max(0, 100 - rain * 1.8);
  // Soleil : très important pour la plage
  var sSunPlage = Math.min(100, sun * 8);
  return Math.round(sRainPlage * 0.35 + sTempPlage * 0.45 + sSunPlage * 0.20);
 }
 var sTemp = scoreTemp(d.avgTemp, cfg.tempMin, cfg.tempMax);
 var sWind = 85;
 return Math.round(sRain * w.rain/100 + sTemp * w.temp/100 + sWind * w.wind/100 + sSun * w.sun/100);
}
function monthScore(d) {
 return monthScoreForUC(d, currentUseCase !== 'general' ? currentUseCase : 'general');
}

function monthColor(d) {
 var t = d.avgTemp;
 if (t == null) return '#a0aec0';
 if (t >= 25) return '#f59e0b';
 if (t >= 18) return '#84cc16';
 if (t >= 10) return '#22d3ee';
 if (t >= 2) return '#818cf8';
 return '#93c5fd';
}

function monthIconFromData(d) {
 var sun = d.sunHrs || 0;
 var pct = d.rainPct || 0;

 // Snow
 var snowTemp = d.avgTmin != null ? d.avgTmin : d.avgTemp;
 if (snowTemp != null && snowTemp <= 2 && pct > 15) return IC.snow;

 // effPct = rainPct brut (mm P50 ≈ 0 partout → inutilisable pour pondérer)
 var effPct = pct;

 // Correction tropicale : pluies convectives courtes, soleil entre les averses
 var avgTemp = d.avgTemp != null ? d.avgTemp : (d.avgTmax != null ? d.avgTmax - 4 : null);
 if (avgTemp != null && avgTemp >= 22 && sun >= 4) {
  var tropFactor = avgTemp >= 24 ? 0.55 : 0.55 + (24 - avgTemp) / 2 * 0.10;
  effPct = effPct * tropFactor;
 }

 // ── Soleil dominant ─────────────────────────────────────────────
 if (effPct <= 25 && sun >= 6) return IC.sun;
 if (effPct <= 35 && sun >= 8) return IC.sun;

 // ── Averses avec soleil ─────────────────────────────────────────
 if (effPct <= 55 && sun >= 7) return IC.shower;
 if (effPct <= 45 && sun >= 5) return IC.shower;

 // ── Partiellement nuageux ───────────────────────────────────────
 if (effPct <= 45 && sun >= 3) return IC.partcloud;
 if (effPct <= 35) return IC.partcloud;

 // ── Pluie ───────────────────────────────────────────────────────
 if (effPct <= 65 && sun >= 3) return IC.lightrain;
 if (effPct <= 65) return IC.rain;
 if (effPct <= 80) return IC.rain;
 return IC.heavyrain;
}

var MONTHS_FR = T.months;
var MONTHS_SHORT = T.monthsShort;

function renderAnnual(loc, monthly) {
 _lastMonthly = monthly; _lastAnnLoc = loc;
 document.getElementById('ann-city-name').textContent = loc.name + (loc.country ? ' — ' + loc.country : '');
 var grid = document.getElementById('months-grid'); grid.innerHTML = '';

 var uc = currentUseCase !== 'general' ? currentUseCase : null;
 var ucNames = {plage:'plage',ski:'ski'};

 // Update subtitle
 var subEl = document.getElementById('annual-subtitle');
 var ucSubEl = document.getElementById('annual-subtitle-uc');
 if (uc && ucSubEl) {
 subEl.style.display = 'none';
 var ucLabels = {plage:T.bestBeach,ski:T.bestSki};
 ucSubEl.textContent = ucLabels[uc] || T.optimisedFor + ' ' + (ucNames[uc]||uc);
 ucSubEl.style.display = 'block';
 } else {
 if (subEl) subEl.style.display = 'block';
 if (ucSubEl) ucSubEl.style.display = 'none';
 }

 // Compute scores for all 12 months
 var scores = [];
 for (var m = 0; m < 12; m++) scores.push({ idx: m, score: monthScoreForUC(monthly[m], uc || 'general') });
 var sorted = scores.slice().sort(function(a,b){ return b.score - a.score; });
 // Ski : tous les mois >= 70 sont recommandés (pas seulement le top 2)
 var topIdxs, worstIdxs;
 if (uc === 'ski') {
 topIdxs = scores.filter(function(s){ return s.score >= 70; }).map(function(s){ return s.idx; });
 worstIdxs = scores.filter(function(s){ return s.score < 40; }).map(function(s){ return s.idx; });
 } else {
 topIdxs = sorted[0].score >= 55 ? (sorted[1].score >= 55 ? [sorted[0].idx, sorted[1].idx] : [sorted[0].idx]) : [];
 worstIdxs = sorted[11].score < 50 ? (sorted[10].score < 50 ? [sorted[10].idx, sorted[11].idx] : [sorted[11].idx]) : [];
 }

 var now = new Date();
 var startMonth = now.getMonth();

 for (var offset = 0; offset < 12; offset++) {
 var idx = (startMonth + offset) % 12;
 var d = monthly[idx];
 var score = scores[idx].score;
 var color = monthColor(d);
 var delay = offset * 40;
 var isRec = topIdxs.indexOf(idx) >= 0;
 var isAvoid = worstIdxs.indexOf(idx) >= 0;

 var card = document.createElement('div');
 card.className = 'month-card' + (isRec ? ' is-rec' : '') + (isAvoid ? ' is-avoid' : '');
 card.style.setProperty('--month-color', isRec ? '#1a7a4a' : (isAvoid ? CFG.avoidColor : color));
 card.style.animationDelay = delay + 'ms';

 var scoreNum = '<div class="month-score score-num-uc" style="background:' + getScoreColor(score) + ';color:white">' + (score === 100 ? '10' : (score/10).toFixed(1)) + '</div>';
 var seasParts = [];
    if (d.seasTempDelta != null) seasParts.push((d.seasTempDelta > 0 ? '+' : '') + d.seasTempDelta + '°');
    if (d.seasRainDelta != null) seasParts.push((d.seasRainDelta > 0 ? '+' : '') + d.seasRainDelta + '% '+T.wordRain);
    var seasDetail = seasParts.length ? ' · ' + seasParts.join(' · ') : '';
    var seasBadge = d.hasSeasonal ? '<div class="month-seas-badge">'+T.ecmwfTrend + (seasDetail ? '<br><span style="font-weight:500;text-transform:none;letter-spacing:0;color:#3b82f6">' + seasParts.join(' · ') + '</span>' : '') + '</div>' : '<div class="month-seas-badge" style="visibility:hidden">·</div>';
 var isBest = uc && idx === sorted[0].idx && sorted[0].score >= 60;
 var badgeHtml = (isRec ? '<div class="month-badge rec">'+T.badgeRec+'</div>' : (isAvoid ? '<div class="month-badge avoid">'+T.badgeAvoid+'</div>' : '')) + (isBest ? '<div class="month-best-badge">'+T.badgeBest+'</div>' : '');

 var tmaxStr = d.avgTmax != null ? fmtTempRaw(d.avgTmax) + '°' : '–';
 var tminStr = d.avgTmin != null ? fmtTempRaw(d.avgTmin) + '°' : '–';
 var tempStr = d.avgTemp != null ? fmtTempRaw(d.avgTemp) + '°' : '–';

 card.innerHTML =
 '<div class="month-name">' + MONTHS_FR[idx] + '</div>' +
 '<div class="month-icon">' + monthIconFromData(d) + '</div>' +
 '<div class="month-temp">' + tminStr + ' / ' + tmaxStr + '</div>' +
 '<div class="month-range">'+T.avgLabel+' ' + tempStr + '</div>' +
 '<div class="month-stats">' +
 '<span class="month-stat">💧 ' + d.rainPct + '% <span style="font-weight:400;color:var(--slate3);font-size:10px">(' + fmtPrecip(d.avgPrecipMm)+'/'+T.dayAbbr+')</span></span>' +
 '<span class="month-stat">☀ ' + Math.round(d.sunHrs) + 'h</span>' +
 '</div>' +
 '<div class="month-bar"><div class="month-bar-fill" style="width:' + d.rainPct + '%"></div></div>' +
 scoreNum + badgeHtml + seasBadge;

 grid.appendChild(card);
 }
 // ── Grid legend ──
 var legendEl = document.getElementById('annual-legend');
 if (!legendEl) {
 legendEl = document.createElement('div');
 legendEl.id = 'annual-legend';
 legendEl.style.cssText = 'display:flex;gap:16px;flex-wrap:wrap;font-size:11px;color:var(--slate3);margin-top:10px;align-items:center;padding:0 2px';
 legendEl.innerHTML = '<span><span style="display:inline-block;width:12px;height:3px;background:#1a7a4a;border-radius:2px;margin-right:5px;vertical-align:middle"></span>'+T.badgeRec+'</span>' +
 '<span><span style="display:inline-block;width:12px;height:3px;background:'+CFG.avoidColor+';border-radius:2px;margin-right:5px;vertical-align:middle"></span>'+T.badgeAvoid+'</span>' +
 '<span style="margin-left:auto;font-style:italic;font-size:10px">'+T.legendBarColor+'</span>';
 grid.parentNode.insertBefore(legendEl, grid.nextSibling);
 }


 document.getElementById('ann-note').innerHTML = T.annualNote;

 // ── Résumé narratif ──────────────────────────────────────────────────────
 var narEl = document.getElementById('ann-narrative');
 if (narEl) {
 var MNAMES = T.monthsLower;
 // Trouver les 2 meilleurs et 2 pires mois
 var sorted2 = scores.slice().sort(function(a,b){return b.score-a.score;});
 var best1 = sorted2[0], best2 = sorted2[1];
 var worst1 = sorted2[11], worst2 = sorted2[10];
 
 // Construire fenêtre optimale (mois consécutifs avec score >= 60)
 var goodMonths = scores.filter(function(s){return s.score >= 60;}).map(function(s){return s.idx;});
 
 var ucLabel = {'plage':T.narBeach,'ski':T.narSki,'general':T.narGeneral}[uc||'general'] || T.narGeneral;
 
 var bestName1 = MNAMES[best1.idx];
 var bestName2 = MNAMES[best2.idx];
 var worstName = MNAMES[worst1.idx];
 
 var emoji = best1.score >= 75 ? '🌟' : best1.score >= 60 ? '✅' : '⚠️';
 
 var narrative = emoji + ' <strong>'+T.narBestMonth+' ' + bestName1.charAt(0).toUpperCase() + bestName1.slice(1);
 if (best2.score >= 55) narrative += ' '+T.narAnd+' ' + bestName2;
 narrative += '</strong>';
 
 if (goodMonths.length >= 2) {
 narrative += ' · '+T.narWindow+' <strong>' + goodMonths.length + ' '+T.narMonths+'</strong>';
 }
 
 if (uc && worst1.score < 50) {
 narrative += ' · '+T.narAvoid+' <span style="color:#ef4444;font-weight:700">' + worstName + '</span>';
 if (worst2.score < 50) narrative += ' '+T.narAnd+' ' + MNAMES[worst2.idx];
 }
 
 // Température indicative du meilleur mois
 var bestData = monthly[best1.idx];
 if (bestData && bestData.avgTmax) {
 narrative += ' · ' + fmtTemp(bestData.avgTmax) + ' max · ' + bestData.rainPct + '% '+T.wordRain;
 }
 
 narEl.innerHTML = narrative;
 narEl.style.display = 'block';
 }
 // ── fin résumé narratif ──────────────────────────────────────────────────

 document.getElementById('annual-result').style.display = 'block';
 setTimeout(function(){var el=document.getElementById('annual-result');if(el)el.scrollIntoView({behavior:'smooth',block:'start'});},120);
}


document.getElementById('btn-go').onclick=function(){run();};
// Annual autocomplete listeners
function clearCity(){
 var el=document.getElementById('inp-city');
 el.value=''; selectedLoc=null;
 document.getElementById('inp-city-clear').classList.remove('visible');
 hideAC(); el.focus();
}
function clearAnnCity(){
 var el=document.getElementById('ann-city');
 el.value=''; annSelectedLoc=null;
 document.getElementById('ann-city-clear').classList.remove('visible');
 hideAnnAC(); el.focus();
}
document.getElementById('ann-city').oninput=function(){
 annSelectedLoc=null;var q=this.value.trim();clearTimeout(annAcTimer);
 document.getElementById('ann-city-clear').classList.toggle('visible',q.length>0);
 if(q.length<2){hideAnnAC();return;}
 annAcTimer=setTimeout(function(){fetch('https://geocoding-api.open-meteo.com/v1/search?name='+encodeURIComponent(q)+'&count=6&language=fr').then(function(r){return r.json();}).then(function(d){showAnnAC(d.results||[]);}).catch(function(){hideAnnAC();});},280);
};
document.getElementById('ann-city').onblur=function(){setTimeout(hideAnnAC,180);};
document.getElementById('ann-city').onkeydown=function(e){
 var list=document.getElementById('ann-ac-list'),items=list.querySelectorAll('.ac-item'),n=items.length;
 if(e.key==='ArrowDown'){e.preventDefault();annAcIdx=annAcIdx<n-1?annAcIdx+1:n-1;for(var i=0;i<n;i++)items[i].className='ac-item'+(i===annAcIdx?' sel':'');}
 else if(e.key==='ArrowUp'){e.preventDefault();annAcIdx=annAcIdx>0?annAcIdx-1:0;for(var i=0;i<n;i++)items[i].className='ac-item'+(i===annAcIdx?' sel':'');}
 else if(e.key==='Enter'){if(annAcIdx>=0&&list.style.display!=='none'){selectAnnAC(annAcIdx);}else{hideAnnAC();runAnnual();}}
 else if(e.key==='Escape'){hideAnnAC();}
};
document.getElementById('annual-wrap').style.display='none';
// Pre-select "Juste la météo" by default
quickFill('general');
// Show hint if user tries to interact before selecting use case
document.getElementById('date-form').addEventListener('click', function() {
 if (this.classList.contains('uc-required')) {
 var hint = document.getElementById('uc-hint');
 if (hint) { hint.classList.add('visible'); }
 // Highlight pills briefly
 var pills = document.querySelectorAll('.uc-pill');
 for (var i=0; i<pills.length; i++) {
 pills[i].style.borderColor = 'var(--gold)';
 (function(p){ setTimeout(function(){ p.style.borderColor=''; }, 800); })(pills[i]);
 }
 }
}, true);
document.getElementById('annual-wrap').addEventListener('click', function() {
 if (this.classList.contains('uc-required-ann')) {
 var hint = document.getElementById('uc-hint-ann');
 if (hint) { hint.classList.add('visible'); }
 var pills = document.querySelectorAll('.uc-pill');
 for (var i=0; i<pills.length; i++) {
 pills[i].style.borderColor = 'var(--gold)';
 (function(p){ setTimeout(function(){ p.style.borderColor=''; }, 800); })(pills[i]);
 }
 }
}, true);
document.addEventListener('DOMContentLoaded', function() {
 flatpickr(document.getElementById('inp-date'), {
 dateFormat: 'd/m/Y',
 locale: 'fr',
 minDate: 'today',
 maxDate: new Date(new Date().setFullYear(new Date().getFullYear()+1)),
 disableMobile: true,
 onChange: function(selectedDates, dateStr) {
 var el = document.getElementById('inp-date');
 el.classList.toggle('has-val', selectedDates.length > 0);
 if (selectedDates.length > 0) {
 var d = selectedDates[0];
 el._isoValue = d.getFullYear()+'-'+(d.getMonth()<9?'0':'')+(d.getMonth()+1)+'-'+(d.getDate()<10?'0':'')+d.getDate();
 } else {
 el._isoValue = '';
 }
 }
 });
});
document.getElementById('inp-city').oninput=function(){
 selectedLoc=null;
 // Don't reset use case when typing city — user keeps their project selection
 var q=this.value.trim();clearTimeout(acTimer);
 document.getElementById('inp-city-clear').classList.toggle('visible',q.length>0);
 if(q.length<2){hideAC();return;}
 acTimer=setTimeout(function(){fetchAC(q);},280);
};
document.getElementById('inp-city').onblur=function(){setTimeout(hideAC,180);};
document.getElementById('inp-city').onkeydown=function(e){
 var list=document.getElementById('ac-list'), items=list.querySelectorAll('.ac-item'), n=items.length;
 if(e.key==='ArrowDown'){e.preventDefault();acIdx=acIdx<n-1?acIdx+1:n-1;for(var i=0;i<n;i++)items[i].className='ac-item'+(i===acIdx?' sel':'');}
 else if(e.key==='ArrowUp'){e.preventDefault();acIdx=acIdx>0?acIdx-1:0;for(var i=0;i<n;i++)items[i].className='ac-item'+(i===acIdx?' sel':'');}
 else if(e.key==='Enter'){if(acIdx>=0&&list.style.display!=='none'){selectAC(acIdx);}else{hideAC();run();}}
 else if(e.key==='Escape'){hideAC();}
};
document.getElementById('inp-date').onkeydown=function(e){if(e.key==='Enter')run();};
var tom=new Date(), maxD=new Date();tom.setHours(0,0,0,0);maxD.setFullYear(maxD.getFullYear()+2);
// min/max gérés par flatpickr

// ── URL PARAMS : pré-remplir ville + lancer vue annuelle ──────────────────
(function() {
 function getParam(name) {
 var search = window.location.search.substring(1);
 var parts = search.split('&');
 for (var i = 0; i < parts.length; i++) {
 var kv = parts[i].split('=');
 if (decodeURIComponent(kv[0]) === name) return decodeURIComponent(kv[1] || '');
 }
 return null;
 }
 var city = getParam('city');
 var lat = getParam('lat');
 var lon = getParam('lon');
 var uc = getParam('uc');
 if (city && lat && lon) {
 switchMode('annual');
 var el = document.getElementById('ann-city');
 el.value = city;
 document.getElementById('ann-city-clear').classList.add('visible');
 annSelectedLoc = { lat: parseFloat(lat), lon: parseFloat(lon), name: city, region: '', country: '' };
 if (uc) { currentUseCase = uc; quickFill(uc); }
 setTimeout(function() { runAnnual(); }, 100);
 }
})();
