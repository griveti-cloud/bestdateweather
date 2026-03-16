// BestDateWeather — core.js
// Requires: i18n-xx.js loaded BEFORE this file (sets window.BDW_T + window.BDW_CFG)
/* global _showDateNav */
var T = window.BDW_T;
var CFG = window.BDW_CFG;

/* ── AFFILIATE CHIPS ── */
function updateAffilChips(loc) {
  var wrap = document.getElementById('affil-chips');
  if (!wrap) return;
  var name = loc.name || '';
  var country = loc.country || '';
  var dest = name + (country ? ', ' + country : '');
  var destEnc = encodeURIComponent(dest);
  var lang = (CFG && CFG.lang) ? CFG.lang : 'fr';
  var gygDomain = (CFG && CFG.gyg_domain) ? CFG.gyg_domain : 'getyourguide.fr';

  // Hébergements — Hotels.com via CJ
  var hotelsDomain = (CFG && CFG.booking_domain) ? CFG.booking_domain : 'fr';
  var hotelsUrl = 'https://' + hotelsDomain + '.hotels.com/Hotel-Search?destination=' + destEnc + '&camref=1110IB57J';
  var elH = document.getElementById('affil-hotel');
  if (elH) { elH.href = hotelsUrl; if(T.chip_hotel) elH.innerHTML = '🏨 ' + T.chip_hotel; }

  // Activités — GYG
  var gygLocale = (CFG && CFG.gyg_lang) ? CFG.gyg_lang : 'fr';
  var gygUrl = 'https://www.' + gygDomain + '/s/?q=' + destEnc + '&partner_id=2MQKLO0&locale=' + gygLocale;
  var elA = document.getElementById('affil-activ');
  if (elA) { elA.href = gygUrl; if(T.chip_activ) elA.innerHTML = '🎟️ ' + T.chip_activ; }

  // Vols — Kiwi via Travelpayouts
  var kiwiSlug = (name + (country ? '-' + country : ''))
    .toLowerCase()
    .normalize('NFD').replace(/[\u0300-\u036f]/g, '')
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-|-$/g, '');
  var kiwiDeep = 'https://www.kiwi.com/' + lang + '/search/results/anywhere/' + kiwiSlug + '/anytime/anytime';
  var flightsUrl = 'https://c111.travelpayouts.com/click?shmarker=708106&promo_id=3791&source_type=customlink&type=click&custom_url=' + encodeURIComponent(kiwiDeep);
  var elF = document.getElementById('affil-flight');
  if (elF) { elF.href = flightsUrl; if(T.chip_flight) elF.innerHTML = '✈️ ' + T.chip_flight; }

  wrap.style.display = 'flex';
}

/* ── UNITS TOGGLE (°C/°F) ── */
var _units = (CFG && CFG.defaultUnits) ? CFG.defaultUnits : 'metric';

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
 // Refresh weather banner units
 if (typeof window.wbRefreshUnits === 'function') window.wbRefreshUnits();
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

function fmtWindDir(deg) {
 if (deg == null) return '';
 var dirs;
 var _lg=(document.documentElement.lang||'fr').toLowerCase();
 if (_lg==='de') dirs=['N','NO','O','SO','S','SW','W','NW'];
 else if (_lg==='en'||_lg==='en-us') dirs=['N','NE','E','SE','S','SW','W','NW'];
 else if (_lg==='es') dirs=['N','NE','E','SE','S','SO','O','NO'];
 else dirs=['N','NE','E','SE','S','SO','O','NO'];
 return dirs[Math.round(((deg%360)+360)%360/45)%8];
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
 shower: '<svg viewBox="0 0 40 40" fill="none"><circle cx="14" cy="12" r="5.5" fill="#f59e0b" opacity=".9"/><g stroke="#f59e0b" stroke-width="1.7" stroke-linecap="round"><line x1="14" y1="3" x2="14" y2="6"/><line x1="5" y1="12" x2="8" y2="12"/><line x1="8" y1="7" x2="10" y2="9"/><line x1="20" y1="7" x2="18" y2="9"/></g><rect x="9" y="18" width="22" height="11" rx="5.5" fill="#93c5e8"/><ellipse cx="17" cy="18" rx="6" ry="5.5" fill="#a8d4f0"/><ellipse cx="23" cy="19" rx="5" ry="4.5" fill="#bde0f8"/><g stroke="#3b82f6" stroke-width="2.2" stroke-linecap="round"><line x1="19" y1="31" x2="17" y2="37"/></g></svg>',
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
 // Ski altitude warning on UC switch
 var _skiWD2 = document.getElementById('ski-alt-warn-daily');
 if (_skiWD2) {
  if (type === 'ski' && selectedLoc && selectedLoc.elevation != null && selectedLoc.elevation < 800) {
   _skiWD2.textContent = T.skiAltWarn.replace('{e}', Math.round(selectedLoc.elevation));
   _skiWD2.style.display = 'block';
  } else {
   _skiWD2.style.display = 'none';
  }
 }
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
 if(open){
  setTimeout(function(){btn.scrollIntoView({behavior:'smooth',block:'start'});},80);
  // Lazy-load historique températures au premier ouverture
  if(!_histLoaded && !_histLoading && selectedLoc && window._lastMo!=null && window._lastDa!=null){
   _histLoading=true;
   fetchHistoricalTemps(selectedLoc.lat,selectedLoc.lon,window._lastMo,window._lastDa)
    .then(function(data){_histLoaded=true;_histLoading=false;renderHistoricalChart(data);})
    .catch(function(){_histLoading=false;var s=document.getElementById('sec-history');if(s)s.style.display='none';});
  }
 }
}

/* ══════════════════════════════════════════════
   HISTORICAL TEMPERATURE CHART
   1 seul appel API sur 10 ans, fenêtre ±3 jours
   ══════════════════════════════════════════════ */
var _histLoaded=false, _histLoading=false;

function fetchHistoricalTemps(lat, lon, mo, da) {
 var now=new Date(), endYr=now.getFullYear()-1;
 var s=toISO(addDays(new Date(endYr-9,mo,da),-3));
 var e=toISO(addDays(new Date(endYr,mo,da),3));
 return fetch('https://archive-api.open-meteo.com/v1/archive?latitude='+lat+'&longitude='+lon
  +'&start_date='+s+'&end_date='+e
  +'&daily=temperature_2m_max,temperature_2m_min,temperature_2m_mean,weather_code&timezone=auto')
  .then(function(r){if(!r.ok)throw new Error('hist');return r.json();})
  .then(function(d){
   if(!d||!d.daily||!d.daily.time)return[];
   var times=d.daily.time,tmaxA=d.daily.temperature_2m_max||[],
    tminA=d.daily.temperature_2m_min||[],tmeanA=d.daily.temperature_2m_mean||[],
    wcA=d.daily.weather_code||[];
   var byYear={};
   for(var i=0;i<times.length;i++){
    var pts=times[i].split('-');
    var yr=parseInt(pts[0]),dMo=parseInt(pts[1])-1,dDa=parseInt(pts[2]);
    var dist=Math.abs((dMo*31+dDa)-(mo*31+da));
    if(dist>3)continue;
    if(!byYear[yr])byYear[yr]={mx:[],mn:[],me:[],wc:[],wd:[]};
    if(tmaxA[i]!=null)byYear[yr].mx.push(tmaxA[i]);
    if(tminA[i]!=null)byYear[yr].mn.push(tminA[i]);
    if(tmeanA[i]!=null)byYear[yr].me.push(tmeanA[i]);
    // Stocker code météo avec poids (jour exact = poids 3, sinon 1)
    if(wcA[i]!=null)byYear[yr].wc.push(wcA[i]),byYear[yr].wd.push(dist===0?3:1);
   }
   var avg=function(a){return a.length?a.reduce(function(s,v){return s+v;},0)/a.length:null;};
   // Mode pondéré du weather_code (code le plus fréquent autour de la date exacte)
   var modeWC=function(codes,weights){
    if(!codes||!codes.length)return null;
    var cnt={};
    for(var i=0;i<codes.length;i++){
     var c=codes[i];cnt[c]=(cnt[c]||0)+weights[i];
    }
    var best=null,bv=0;
    for(var k in cnt){if(cnt[k]>bv){bv=cnt[k];best=parseInt(k);}}
    return best;
   };
   var res=[];
   for(var y=endYr-9;y<=endYr;y++){
    var b=byYear[y];
    if(!b||!b.mx.length)continue;
    res.push({year:y,tmax:avg(b.mx),tmin:avg(b.mn),tmean:avg(b.me),wc:modeWC(b.wc,b.wd)});
   }
   return res;
  });
}

function histWeatherEmoji(code){
 if(code==null)return'❓';
 if(code===0)return'☀️';
 if(code<=2)return'⛅';
 if(code===3)return'☁️';
 if(code<=48)return'🌫️';
 if(code<=55)return'🌦️';
 if(code<=65)return'🌧️';
 if(code<=75)return'❄️';
 if(code<=82)return'🌧️';
 return'⛈️';
}

function renderHistoricalChart(data){
 var el=document.getElementById('sec-history');
 if(!el)return;
 var ct=document.getElementById('hist-chart-container');
 if(!ct)return;
 if(!data||!data.length){el.style.display='none';return;}
 var isUS=window._units==='us';
 function toD(c){return c==null?null:(isUS?Math.round(c*9/5+32):Math.round(c*10)/10);}
 var allV=[];
 for(var i=0;i<data.length;i++){if(data[i].tmax!=null)allV.push(toD(data[i].tmax));if(data[i].tmin!=null)allV.push(toD(data[i].tmin));}
 var minV=Math.floor(Math.min.apply(null,allV))-2,maxV=Math.ceil(Math.max.apply(null,allV))+2;
 var range=maxV-minV||1;
 var W=320,H=140,PL=30,PR=8,PT=10,PB=22,w=W-PL-PR,h=H-PT-PB,n=data.length;
 function xP(i){return PL+(i/(n-1))*w;}
 function yP(v){return v==null?null:PT+h-((toD(v)-minV)/range)*h;}
 function mkPath(key){
  var segs='';
  for(var i=0;i<data.length;i++){var y=yP(data[i][key]);if(y!=null)segs+=(segs?'L ':' M ')+xP(i)+','+y;}
  return segs;
 }
 var grid='';
 for(var g=0;g<=4;g++){
  var gv=minV+(range*g/4),gy=PT+h-(range*g/4)/range*h;
  grid+='<line x1="'+PL+'" y1="'+gy+'" x2="'+(W-PR)+'" y2="'+gy+'" stroke="#ede8e0" stroke-width="1"/>';
  grid+='<text x="'+(PL-3)+'" y="'+(gy+4)+'" text-anchor="end" font-size="9" fill="#aaa">'+Math.round(gv)+'</text>';
 }
 var xlbl='';
 for(var j=0;j<data.length;j++){
  if(j%2===0||j===data.length-1){
   xlbl+='<text x="'+xP(j)+'" y="'+(H-5)+'" text-anchor="middle" font-size="9" fill="#aaa">'+data[j].year+'</text>';
  }
 }
 var dots='';
 for(var k=0;k<data.length;k++){
  var dy=yP(data[k].tmax);
  if(dy!=null)dots+='<circle cx="'+xP(k)+'" cy="'+dy+'" r="2.5" fill="#e07040"/>';
 }
 var svg='<svg viewBox="0 0 '+W+' '+H+'" style="width:100%;height:auto;display:block">'+
  grid+xlbl+
  '<path d="'+mkPath('tmin')+'" fill="none" stroke="#6ea8d9" stroke-width="1.5" stroke-linejoin="round"/>'+
  '<path d="'+mkPath('tmean')+'" fill="none" stroke="#b0a080" stroke-width="1.5" stroke-dasharray="4 2" stroke-linejoin="round"/>'+
  '<path d="'+mkPath('tmax')+'" fill="none" stroke="#e07040" stroke-width="2" stroke-linejoin="round"/>'+
  dots+'</svg>';
 // Ligne emojis alignée sous chaque point du graphique
 var emojiRow='<div style="display:flex;padding:0 '+PR+'px 0 '+PL+'px;margin-top:-2px">';
 for(var e2=0;e2<data.length;e2++){
  var flex=e2===0?'0 0 0px':'1';
  emojiRow+='<div style="flex:'+flex+';text-align:center;font-size:14px;line-height:1" title="'+data[e2].year+'">'+histWeatherEmoji(data[e2].wc)+'</div>';
 }
 emojiRow+='</div>';
 var leg='<div style="display:flex;gap:14px;margin-top:6px;font-size:11px;color:#888;flex-wrap:wrap">'+
  '<span><span style="display:inline-block;width:12px;height:2px;background:#e07040;vertical-align:middle;margin-right:3px;border-radius:1px"></span>Tmax</span>'+
  '<span><span style="display:inline-block;width:12px;height:2px;background:#b0a080;vertical-align:middle;margin-right:3px;border-radius:1px;border-top:2px dashed #b0a080"></span>Moy.</span>'+
  '<span><span style="display:inline-block;width:12px;height:2px;background:#6ea8d9;vertical-align:middle;margin-right:3px;border-radius:1px"></span>Tmin</span>'+
  '</div>';
 ct.innerHTML=svg+emojiRow+leg;
 el.style.display='block';
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
 var clean = city.replace(/\s*\([^)]*\)/g, '').split(/,|\s+[—–-]\s+/)[0].trim();
 var _gl=(document.documentElement.lang||'fr').toLowerCase(); if(_gl==='en-us')_gl='en'; if(_gl!=='en'&&_gl!=='es'&&_gl!=='de')_gl='fr'; return fetch('https://geocoding-api.open-meteo.com/v1/search?name=' + encodeURIComponent(clean) + '&count=5&language='+_gl)
 .then(function(r) { return r.json(); })
 .then(function(d) {
 if (!d.results || !d.results.length) throw new Error('Ville introuvable');
 var r = d.results[0];
 var gRegion = (r.country_code === 'FR') ? '' : (r.admin1 || '');
 return { lat: r.latitude, lon: r.longitude, name: r.name, region: gRegion, country: r.country || COUNTRY_NAMES[r.country_code] || r.country_code || '', country_code: r.country_code || '' };
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
 var url='https://api.open-meteo.com/v1/forecast?latitude='+lat+'&longitude='+lon+'&hourly=temperature_2m,precipitation_probability,precipitation,snowfall,windspeed_10m,winddirection_10m,shortwave_radiation,weather_code&daily=weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max,precipitation_sum&timezone=auto&forecast_days=8';
 // _locTzOffset is global
 return fetch(url).then(function(r){if(!r.ok)throw new Error(T.errForecast);return r.json();}).then(function(data){
 if (data.utc_offset_seconds != null) _locTzOffset = data.utc_offset_seconds;
 // Store daily forecast for 7-day strip
 window._forecastDaily = data.daily || null;
 _modelElevation = data.elevation != null ? Math.round(data.elevation) : null;
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
 var wmo_h=idx>=0&&data.hourly.weather_code&&data.hourly.weather_code[idx]!=null?data.hourly.weather_code[idx]:null;
 var wd_fc=idx>=0&&data.hourly.winddirection_10m&&data.hourly.winddirection_10m[idx]!=null?data.hourly.winddirection_10m[idx]:null;
    rows.push({h:h,label:(h<10?'0':'')+h+'h',p25:t,p50:t,p75:t,temp:t,rain:rn,mm:mm_val,windP50:w,windDir:wd_fc,solP25:s,solP50:s,solP75:s,sol:s,snow:snow_val,isForecast:true,wmo:wmo_h});
 }
 return rows;
 });
}

// ── 7-day forecast strip ─────────────────────────────────────────────────
function wmoIcon(code, precip, rainP) {
 // Override: if negligible precipitation, force non-rain icon
 if (precip != null && precip < 0.2 && (rainP == null || rainP < 20)) {
  if (code >= 51) code = (code >= 45 && code <= 48) ? 45 : 2; // keep fog, otherwise partly cloudy
 }
 // WMO 4677 codes used by Open-Meteo
 if (code === 0) return '☀️';
 if (code <= 2) return '⛅';
 if (code === 3) return '☁️';
 if (code === 45 || code === 48) return '🌫️';
 if (code >= 51 && code <= 57) return '🌦️';
 if (code >= 61 && code <= 67) return '🌧️';
 if (code >= 71 && code <= 77) return '🌨️';
 if (code >= 80 && code <= 82) return '🌦️';
 if (code >= 85 && code <= 86) return '🌨️';
 if (code >= 95) return '⛈️';
 return '⛅';
}

function render7DayStrip(diffDays) {
 var el = document.getElementById('forecast-strip');
 if (!el) return;
 var d = window._forecastDaily;
 if (!d || !d.time || d.time.length < 2) { el.style.display = 'none'; return; }
 if (diffDays == null || diffDays !== 0) { el.style.display = 'none'; return; }
 var html = '<div class="fs-label">' + (T.forecast7dLabel || 'Prévisions 7 jours') + '</div><div class="fs-row">';
 var locale = CFG.dateLocale || 'fr-FR';
 var todayStr = new Date().toISOString().slice(0, 10);
 var todayIdx = d.time.indexOf(todayStr);
 if (todayIdx < 0) todayIdx = 0;
 var count = Math.min(d.time.length - todayIdx, 7);
 for (var i = 0; i < count; i++) {
  var idx = todayIdx + i;
  var parts = d.time[idx].split('-');
  var dd = new Date(parseInt(parts[0]), parseInt(parts[1]) - 1, parseInt(parts[2]));
  var dayName = (i === 0) ? (T.dayToday || 'Auj.') : dd.toLocaleDateString(locale, { weekday: 'short' }).replace('.', '');
  var tMax = d.temperature_2m_max[idx] != null ? Math.round(d.temperature_2m_max[idx]) : '–';
  var tMin = d.temperature_2m_min[idx] != null ? Math.round(d.temperature_2m_min[idx]) : '–';
  var wCode = d.weather_code ? (d.weather_code[idx] || 0) : 0;
  // For today: use current hour's WMO from hourly rows (not daily worst-case)
  if (i === 0 && window._lastSc) {
   var _nowH = new Date().getHours();
   var _curRow = window._lastSc[_nowH] || window._lastSc[Math.min(_nowH, window._lastSc.length-1)];
   if (_curRow && _curRow.wmo != null) wCode = _curRow.wmo;
  }
  var rainP = d.precipitation_probability_max ? (d.precipitation_probability_max[idx] || 0) : 0;
  var precip = d.precipitation_sum ? (d.precipitation_sum[idx] || 0) : 0;
  // For today: use current hour's rain probability instead of daily max
  if (i === 0 && window._lastSc) {
   var _nowH2 = new Date().getHours();
   var _curRow2 = window._lastSc[_nowH2] || window._lastSc[Math.min(_nowH2, window._lastSc.length-1)];
   if (_curRow2) { rainP = _curRow2.rain || 0; precip = _curRow2.mm || 0; }
  }
  var icon = wmoIcon(wCode, precip, rainP);
  var isActive = (i === diffDays);
  var rainClass = precip > 5 ? 'fs-rain-heavy' : (precip > 0.5 ? 'fs-rain-light' : (rainP > 40 ? 'fs-rain-maybe' : ''));
  html += '<div class="fs-day' + (isActive ? ' fs-active' : '') + '">';
  html += '<span class="fs-day-name">' + dayName + '</span>';
  html += '<span class="fs-day-icon">' + icon + '</span>';
  html += '<span class="fs-day-temp">' + fmtTempRaw(tMax) + '°</span>';
  html += '<span class="fs-day-min">' + fmtTempRaw(tMin) + '°</span>';
  if (rainClass) html += '<span class="fs-rain-bar ' + rainClass + '"></span>';
  html += '</div>';
 }
 html += '</div>';
 el.innerHTML = html;
 el.style.display = 'block';
}

function fetchArchive(lat, lon, refDate) {
 var s=toISO(addDays(refDate,-10)), e=toISO(addDays(refDate,10));
 return fetch('https://archive-api.open-meteo.com/v1/archive?latitude='+lat+'&longitude='+lon+'&start_date='+s+'&end_date='+e+'&hourly=temperature_2m,precipitation,snowfall,windspeed_10m,winddirection_10m,shortwave_radiation,relative_humidity_2m&timezone=auto').then(function(r){if(!r.ok)throw new Error('Archive error');return r.json();}).then(function(d){if(d.utc_offset_seconds!=null)_locTzOffset=d.utc_offset_seconds;if(d.elevation!=null)_modelElevation=Math.round(d.elevation);return d;});
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
 var buckets=[]; for(var h=0;h<24;h++) buckets.push({t:[],p:[],w:[],s:[],sn:[],rh:[],wd:[]});
 var idx=0;
 function step(){
 if(idx>=years.length) return Promise.resolve(buildRows(buckets,trend));
 var yr2=years[idx++];
 return fetchArchive(lat,lon,new Date(yr2,mo,da,12,0,0)).then(function(data){
 var T=data.hourly.temperature_2m, P=data.hourly.precipitation, W=data.hourly.windspeed_10m, WD=data.hourly.winddirection_10m||[], S=data.hourly.shortwave_radiation||[], SN=data.hourly.snowfall||[], RH=data.hourly.relative_humidity_2m||[];
 for(var i=0;i<data.hourly.time.length;i++){var hh=new Date(data.hourly.time[i]).getHours();if(T[i]!=null)buckets[hh].t.push(T[i]);if(P[i]!=null)buckets[hh].p.push(P[i]);if(W[i]!=null)buckets[hh].w.push(W[i]);if(WD[i]!=null)buckets[hh].wd.push(WD[i]);if(S[i]!=null)buckets[hh].s.push(S[i]);if(SN[i]!=null)buckets[hh].sn.push(SN[i]);if(RH[i]!=null)buckets[hh].rh.push(RH[i]);}
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
    var windDirMean=null;if(b.wd&&b.wd.length>0){var _sinS=0,_cosS=0;for(var _di=0;_di<b.wd.length;_di++){var _rad=b.wd[_di]*Math.PI/180;_sinS+=Math.sin(_rad);_cosS+=Math.cos(_rad);}windDirMean=((Math.atan2(_sinS/b.wd.length,_cosS/b.wd.length)*180/Math.PI)+360)%360;}
    rows.push({h:h,label:(h<10?'0':'')+h+'h',p25:p25!=null?parseFloat((p25+trend).toFixed(1)):null,p50:p50v,p75:p75!=null?parseFloat((p75+trend).toFixed(1)):null,temp:p50v,rain:b.p.length>0?Math.round(wet/b.p.length*100):0,mm:b.p.length>0?(b.p.reduce(function(s,v){return s+v;},0)/b.p.length):0,snow:avgSnow,windP50:pct(b.w,50),windDir:windDirMean,solP25:Math.max(0,pct(b.s,25)||0),solP50:Math.max(0,pct(b.s,50)||0),solP75:Math.max(0,pct(b.s,75)||0),sol:Math.max(0,pct(b.s,50)||0),tempFreq:tempFreq,rh:avgRh});
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
 var nowH = new Date().getHours();
 var activeSlot = hours[0];
 for(var k=0;k<hours.length;k++){ if(hours[k]<=nowH) activeSlot=hours[k]; }
 for(var i=0;i<hours.length;i++){
 var r=sc[hours[i]]; if(!r) continue;
 var lbl=(hours[i]===23)?'00h':r.label;
 var icon = (r.isForecast && r.wmo != null) ? (wmoToIcon(r.wmo,r.sol)||getIcon(r.h,r.temp,r.sol,r.rain,r.mm||0,r.snow||0,r.p25)) : getIcon(r.h,r.temp,r.sol,r.rain,r.mm||0,r.snow||0,r.p25);
 var label = (r.isForecast && r.wmo != null) ? (wmoToLabel(r.wmo)||getLabel(r.h,r.temp,r.sol,r.rain,r.mm||0,r.snow||0)) : getLabel(r.h,r.temp,r.sol,r.rain,r.mm||0,r.snow||0);
 var isNow = (hours[i]===activeSlot);
 var cell=document.createElement('div'); cell.className='h-cell'+(isNow?' h-cell-now':'');
 cell.innerHTML='<span class="h-hr">'+lbl+'</span><span class="h-ic">'+icon+'</span><span class="h-tp">'+(r.temp!=null?fmtTempRaw(r.temp)+'°':'-')+'</span><span class="h-lb">'+label+'</span><div class="h-rb"><div class="h-rf" style="width:'+r.rain+'%"></div></div>';
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
var _modelElevation = null; // elevation of model grid cell (from API response)
var _annModelElevation = null; // model elevation for annual mode

// ── Altitude correction for ski scoring ──────────────────────────────────
// Open-Meteo returns temperatures at model grid elevation, which can differ
// significantly from the actual location elevation (especially in mountains).
// Lapse rate: ~6.5°C per 1000m elevation gain.
function altCorrection(temp, locElevation, modelElevation) {
 if (temp == null || locElevation == null || modelElevation == null) return temp;
 var delta = locElevation - modelElevation;
 if (Math.abs(delta) < 50) return temp; // negligible difference
 return temp - 6.5 * delta / 1000;
}

// Reference scores from destination pages
// Used by annual view for consistency with static pages statiques
/* FICHE_SCORES loaded from fiche-scores.js */// Cache mensuel pré-calculé — chargé depuis data/monthly.json
var MONTHLY_CACHE = null;
var _monthlyPromise = null;
function getMonthlyCache() {
 if (!_monthlyPromise) {
  _monthlyPromise = fetch(CFG.dataBase+'data/monthly.json')
   .then(function(r){ return r.ok ? r.json() : null; })
   .then(function(d){ MONTHLY_CACHE = d || {}; return MONTHLY_CACHE; })
   .catch(function(){ MONTHLY_CACHE = {}; return {}; });
 }
 return _monthlyPromise;
}

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
var TROPICAL_KEYS = {"-8.67,115.21":true,"13.75,100.52":true,"9.93,-84.08":true,"15.49,73.82":true,"15.88,108.33":true,"-20.35,57.55":true,"18.1,-77.3":true,"23.14,-82.36":true,"3.2,73.22":true,"7.88,98.39":true,"-21.11,55.54":true,"-22.9,-43.17":true,"20.62,-87.08":true,"-4.68,55.49":true,"13.36,103.86":true,"1.35,103.82":true,"-6.16,39.2":true,"13.19,-59.54":true,"-1.29,36.82":true,"-18.88,47.51":true,"18.79,98.98":true,"9.51,100.06":true,"21.03,105.85":true,"10.82,106.63":true,"22.32,114.17":true,"14.6,120.98":true,"3.14,101.69":true,"26.92,75.79":true,"7.87,80.77":true,"16.25,-61.55":true,"14.64,-61.02":true,"18.47,-69.9":true,"18.58,-68.4":true,"4.6,-74.08":true,"-17.53,-149.57":true,"-16.5,-151.74":true,"14.5,-14.45":true,"14.93,-23.51":true,"-6.37,35.75":true,"8.09,98.91":true,"7.53,99.04":true,"20.91,107.18":true,"16.05,108.22":true,"10.23,103.97":true,"-8.65,116.32":true,"-7.8,110.36":true,"-8.51,115.26":true,"10.21,118.99":true,"19.86,102.14":true,"10.85,76.27":true,"28.61,77.21":true,"25.05,-77.35":true,"13.91,-60.98":true,"18.07,-63.05":true,"20.63,-87.08":true,"20.65,-105.23":true,"8.98,-79.52":true,"6.25,-75.56":true,"-0.95,-90.97":true,"-17.71,177.99":true,"-22.28,166.46":true,"-12.78,45.23":true,"25.03,121.57":true,"17.9,-62.83":true,"11.19,119.39":true,"12.57,104.99":true,"7.74,98.78":true,"10.1,99.84":true,"12.93,100.88":true,"-8.35,116.04":true,"-8.73,115.54":true,"-8.55,119.49":true,"26.33,127.8":true,"10.32,123.89":true,"11.97,121.92":true,"6.35,99.73":true,"5.42,100.33":true,"16.87,96.2":true,"19.89,102.13":true,"12.17,-68.98":true,"12.51,-69.97":true,"18.47,-66.11":true,"10.65,-61.5":true,"17.12,-61.85":true,"17.06,-96.73":true,"14.63,-90.51":true,"17.25,-88.77":true,"12.11,-86.27":true,"-0.18,-78.47":true,"-16.92,145.77":true,"-19.72,63.43":true,"-13.33,48.27":true,"11.94,108.44":true,"-8.66,115.13":true,"4.94,-52.33":true,"-4.28,39.58":true,"14.69,-17.44":true,"12.24,109.19":true,"9.85,126.05":true,"4.97,115.06":true,"22.2,113.54":true,"11.56,104.92":true,"4.71,-74.07":true,"21.52,-87.38":true,"-4.04,39.67":true,"5.56,-0.19":true,"5.36,-4.01":true,"-1.94,30.06":true,"-6.16,39.19":true,"0.35,32.58":true,"6.52,3.38":true,"-6.79,39.28":true,"19.08,72.88":true,"6.93,79.84":true,"-12.97,-38.51":true,"10.39,-75.51":true,"25.05,-77.34":true,"21.77,-72.34":true,"-12.46,130.84":true,"-13.83,-171.76":true,"-17.73,168.32":true,"-21.21,-175.15":true,"16.46,107.6":true,"-25.97,32.57":true,"11.93,79.83":true,"21.31,-157.86":true,"-21.24,-159.78":true,"-25.69,-54.44":true,"10.31,-84.82":true,"8.48,-13.23":true,"12.37,-1.52":true,"6.37,2.39":true,"6.13,1.22":true,"4.05,9.77":true,"0.42,33.21":true,"-2.27,40.9":true,"-23.75,35.54":true,"-0.23,130.52":true,"-8.49,119.88":true,"19.91,99.83":true,"20.25,105.97":true,"12.0,120.2":true,"13.1,103.2":true,"17.1,121.55":true,"22.63,120.3":true,"15.33,76.46":true,"9.93,76.26":true,"6.87,81.05":true,"20.8,-156.32":true,"15.41,-61.37":true,"12.14,-68.26":true,"13.01,-61.23":true,"16.32,-86.53":true,"11.93,-85.96":true,"-3.12,-60.02":true,"-20.28,148.95":true,"-17.53,-149.83":true,"-6.31,147.18":true,"16.73,-22.93":true,"12.47,53.87":true,"17.97,102.6":true,"12.57,99.96":true,"12.07,102.33":true,"-0.39,9.45":true,"13.45,-16.57":true,"9.07,7.4":true,"6.69,-1.62":true,"-3.35,37.34":true,"0.06,32.46":true,"-12.45,-41.42":true,"-1.46,-48.5":true,"-5.79,-35.21":true,"19.31,-81.25":true,"18.34,-64.93":true,"13.15,-61.2":true,"13.35,-81.37":true,"2.19,102.25":true,"5.98,116.07":true,"15.86,-97.07":true,"20.97,-89.62":true,"10.94,108.29":true,"13.77,109.23":true,"7.51,134.58":true,"4.6,101.07":true,"21.8,-79.98":true};

// Plages score par classe — scoring.py : SCORE_RANGES
var SCORE_RANGES_FICHE = { avoid:[0.5,3.9], mid:[4.0,6.9], rec:[7.0,10.0] };

// Bornes globales raw_score par classe — scoring.py : GLOBAL_RAW_BOUNDS
var GLOBAL_RAW_BOUNDS = { rec:[0.506,0.965], mid:[0.350,0.688], avoid:[0.119,0.553] };
var SCORE_POWER = 2.0;

// scoring.py : t_ideal()
function tIdeal(tmax) {
 // Aligned with scoring.py t_ideal() — source of truth
 if (tmax <= 5)  return 0.0;
 if (tmax <= 14) return (tmax - 5) / 9 * 0.3;
 if (tmax <= 22) return 0.3 + (tmax - 14) / 8 * 0.5;
 if (tmax <= 28) return 0.8 + (tmax - 22) / 6 * 0.2;
 if (tmax <= 32) return 1.0 - (tmax - 28) / 4 * 0.25;
 if (tmax <= 36) return 0.75 - (tmax - 32) / 4 * 0.45;
 return Math.max(0.0, 0.30 - (tmax - 36) / 6 * 0.30);
}

// scoring.py : raw_score() poids 40/35/25
// scoring.py : effective_rain_pct() — bidirectional intensity correction
function effectiveRainPct(pct, mmDay) {
 if (mmDay == null) return pct;
 var factor;
 if (mmDay < 2) factor = 0.60 + (mmDay / 2) * 0.25;
 else if (mmDay < 5) factor = 0.85 + ((mmDay - 2) / 3) * 0.15;
 else if (mmDay < 10) factor = 1.0;
 else if (mmDay < 20) factor = 1.0 + ((mmDay - 10) / 10) * 0.15;
 else factor = Math.min(1.25, 1.15 + ((mmDay - 20) / 20) * 0.10);
 return Math.min(100, pct * factor);
}

function rawScoreFiche(tmax, rain, sun, mm) {
 var effRain = effectiveRainPct(rain, mm);
 return 0.40 * tIdeal(tmax)
 + 0.35 * Math.max(0, 1 - effRain / 100)
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
 var mm = m.avgPrecipMm != null ? m.avgPrecipMm : null;
 var raw = rawScoreFiche(tmax, rain, sun, mm);
 return { i: i, raw: raw, cls: autoClass(raw), tmax: tmax };
 });

 // Heat cap: canicule ≥36°C → mid max, extreme ≥42°C → avoid
 items.forEach(function(it) {
  if (it.tmax >= 42 && it.cls !== 'avoid') it.cls = 'avoid';
  else if (it.tmax >= 36 && it.cls === 'rec') it.cls = 'mid';
 });

 ['avoid','mid','rec'].forEach(function(cls) {
 var grp = items.filter(function(it){ return it.cls === cls; });
 if (!grp.length) return;
 var range = (isTropical && cls === 'avoid') ? SCORE_RANGES_FICHE.mid : SCORE_RANGES_FICHE[cls];
 var lo = range[0], hi = range[1];
 var raws = grp.map(function(it){ return it.raw; });
 var gBounds = GLOBAL_RAW_BOUNDS[cls] || [0,1];
 var gmn = gBounds[0], gmx = gBounds[1];
 grp.forEach(function(it, j) {
 if (monthly[it.i].ficheScore != null) return;
 var norm = gmx !== gmn ? Math.max(0, Math.min(1, (raws[j] - gmn) / (gmx - gmn))) : 0.5;
 var stretched = Math.pow(norm, SCORE_POWER);
 monthly[it.i].ficheScore = Math.round((lo + stretched * (hi - lo)) * 10);
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
 // Bidirectional: bruine reduces effective rain, heavy storms increase it.
 // Matches scoring.py effective_rain_pct().
 var effective = pct;
 if (mmDay != null) {
 var factor;
 if (mmDay < 2) { factor = 0.60 + (mmDay / 2) * 0.25; }       // 0.60-0.85
 else if (mmDay < 5) { factor = 0.85 + ((mmDay - 2) / 3) * 0.15; } // 0.85-1.00
 else if (mmDay < 10) { factor = 1.0; }                              // neutral
 else if (mmDay < 20) { factor = 1.0 + ((mmDay - 10) / 10) * 0.15; } // 1.00-1.15
 else { factor = Math.min(1.25, 1.15 + ((mmDay - 20) / 20) * 0.10); } // 1.15-1.25 cap
 effective = Math.min(100, pct * factor);
 }
 return scoreRain(effective);
}

function scoreTemp(t, tMin, tMax) {
 if (t == null) return 50;
 var ideal = (tMin + tMax) / 2;
 var range = (tMax - tMin) / 2;
 if (t >= tMin && t <= tMax) {
 return 100 - 20 * Math.abs(t - ideal) / range;
 }
 if (t < tMin) {
 return Math.max(0, 80 - (tMin - t) * 8);
 }
 // Progressive heat penalty: accelerates above 32°C
 var over = t - tMax;
 if (over <= 4) return Math.max(0, 80 - over * 4);
 if (over <= 8) return Math.max(0, 64 - (over - 4) * 7);
 return Math.max(0, 36 - (over - 8) * 6);
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
  // Altitude correction: adjust temps from model grid elevation to actual location elevation
  if (selectedLoc && selectedLoc.elevation != null && _modelElevation != null) {
   tmax_ski = altCorrection(tmax_ski, selectedLoc.elevation, _modelElevation);
   tmin_ski = altCorrection(tmin_ski, selectedLoc.elevation, _modelElevation);
  }
  var avgMm = mmSum / rows.length;
  // ── Température idéale ski (même logique que Python t_ideal_winter) ──
  var tIdeaSki;
  if (tmax_ski <= -15) tIdeaSki = 30;
  else if (tmax_ski <= -5) tIdeaSki = 30 + (tmax_ski + 15) / 10 * 60;
  else if (tmax_ski <= 5)  tIdeaSki = 90 + (5 - Math.abs(tmax_ski)) / 5 * 10;
  else if (tmax_ski <= 15) tIdeaSki = 90 - (tmax_ski - 5) / 10 * 70;
  else tIdeaSki = Math.max(0, 20 - (tmax_ski - 15) / 10 * 20);
  // ── Enneigement proxy (même logique que Python _snow_reliability) ──
  // Seuil +4°C en vallée ≈ -2°C à 2000m ; précip froides = bonus poudreuse
  var sSnow;
  if (tmax_ski <= 0) {
   var powderBonus = Math.min(20, avgRain * 0.45);
   sSnow = Math.min(90, 70 + powderBonus);
  } else if (tmax_ski <= 4) {
   var coldF = (4 - tmax_ski) / 4;
   var heavyPen = Math.max(0, avgRain - 60) / 100 * 15;
   sSnow = Math.max(50, 65 + coldF * 5 - heavyPen);
  } else if (tmax_ski <= 6) {
   sSnow = Math.max(30, 50 - (tmax_ski - 4) / 2 * 20 - avgRain * 0.15);
  } else if (tmax_ski <= 12) {
   sSnow = Math.max(5, 30 - (tmax_ski - 6) / 6 * 20 - avgRain * 0.15);
  } else {
   sSnow = 0;
  }
  // ── Soleil ski ──
  var sSunSki = Math.min(100, (peakSol / 50) * 8);
  // ── Score final : 40% enneigement + 40% température + 20% soleil ──
  total = Math.round(sSnow * 0.40 + tIdeaSki * 0.40 + sSunSki * 0.20);
  if (tmax_ski > 15) total = Math.min(total, 5);
  else if (tmax_ski > 12) total = Math.min(total, 15);

 // ── Plage : logique spécifique ───────────────────────────────────────────
 } else if (uc === 'plage') {
  var tmax_plage = rows.length ? Math.max.apply(null, rows.map(function(r){return r.temp||0;})) : (avgTemp||20);
  // t_beach : seuil abaissé à 16°C, pic à 28-32°C
  var sTempPlage;
  if (tmax_plage <= 16) sTempPlage = 0;
  else if (tmax_plage <= 22) sTempPlage = (tmax_plage - 16) / 6 * 45;
  else if (tmax_plage <= 30) sTempPlage = 45 + (tmax_plage - 22) / 8 * 55;
  else if (tmax_plage <= 36) sTempPlage = 100 - (tmax_plage - 30) / 6 * 35;
  else if (tmax_plage <= 42) sTempPlage = 65 - (tmax_plage - 36) / 6 * 35;
  else sTempPlage = 0;
  // t_sea : plus généreux à 18-24°C
  var sst_plage = (window._lastSSTResult && window._lastSSTResult.sst != null) ? window._lastSSTResult.sst : null;
  var sSeaPlage = 50; // valeur neutre si pas de données
  if (sst_plage != null) {
   if (sst_plage < 14) sSeaPlage = 0;
   else if (sst_plage <= 18) sSeaPlage = (sst_plage - 14) / 4 * 25;
   else if (sst_plage <= 22) sSeaPlage = 25 + (sst_plage - 18) / 4 * 30;
   else if (sst_plage <= 26) sSeaPlage = 55 + (sst_plage - 22) / 4 * 35;
   else if (sst_plage <= 30) sSeaPlage = 90 + (sst_plage - 26) / 4 * 10;
   else sSeaPlage = Math.max(50, 100 - (sst_plage - 30) / 5 * 50);
  }
  var sRainPlage = Math.max(0, 100 - avgRain * 1.8);
  var sSunPlage = Math.min(100, (peakSol / 50) * 8);
  var humMalusPlage = scoreHumidityPlage(avgRh, avgTemp);
  // 30% air + 30% mer + 20% pluie + 20% soleil (aligné scoring.py)
  total = Math.round(sTempPlage * 0.30 + sSeaPlage * 0.30 + sRainPlage * 0.20 + sSunPlage * 0.20) - humMalusPlage;

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
 var _riskTxt = getMainRisk(avgRain, avgTemp, avgWind, uc);
 var _riskEl = document.getElementById('score-risk');
 if (_riskTxt && _riskTxt !== T.riskNone) {
  _riskEl.innerHTML = '<span style="color:#c8bfb0;font-weight:600">⚠ </span>' + _riskTxt;
 } else {
  _riskEl.textContent = _riskTxt;
 }

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

function wmoToLabel(code) {
 if (code == null) return null;
 if (code === 0) return T.sunny;
 if (code <= 2) return T.partlyCloudy;
 if (code === 3) return T.overcast;
 if (code === 45 || code === 48) return T.fog;
 if (code >= 51 && code <= 57) return T.lightRain;
 if (code >= 61 && code <= 65) return T.rain;
 if (code >= 66 && code <= 67) return T.rain;
 if (code >= 71 && code <= 77) return T.snow;
 if (code >= 80 && code <= 82) return T.showers;
 if (code >= 85 && code <= 86) return T.snow;
 if (code >= 95) return T.storm;
 return null;
}
function wmoToIcon(code, sol) {
 if (code == null) return null;
 var night = (sol != null && sol < 15);
 if (code === 0) return night ? IC.moon : IC.sun;
 if (code <= 2) return night ? IC.nightcloud : IC.partcloud;
 if (code === 3) return night ? IC.nightcloud : IC.cloud;
 if (code === 45 || code === 48) return IC.fog;
 if (code >= 51 && code <= 57) return night ? IC.nightshower : IC.lightrain;
 if (code >= 61 && code <= 65) return night ? IC.nightrain : IC.rain;
 if (code >= 66 && code <= 67) return night ? IC.nightrain : IC.rain;
 if (code >= 71 && code <= 77) return night ? IC.nightsnow : IC.snow;
 if (code >= 80 && code <= 82) return night ? IC.nightshower : IC.shower;
 if (code >= 85 && code <= 86) return night ? IC.nightsnow : IC.snow;
 if (code >= 95) return IC.storm;
 return null;
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
 document.getElementById('r-cond').textContent=(main.isForecast && main.wmo != null && wmoToLabel(main.wmo)) ? wmoToLabel(main.wmo) : getLabel(main.h,main.temp,main.sol,main.rain,main.mm||0,main.snow||0,main.p25);
 document.getElementById('r-icon').innerHTML=(main.isForecast && main.wmo != null && wmoToIcon(main.wmo,main.sol)) ? wmoToIcon(main.wmo,main.sol) : getIcon(main.h,main.temp,main.sol,main.rain,main.mm||0,main.snow||0,main.p25);
 document.getElementById('r-rain').textContent=avgRain+'%';
 var _windAvg=Math.round(wSum/rows.length);
 var _mainDir=(rows[Math.round(rows.length/2)]&&rows[Math.round(rows.length/2)].windDir!=null)?rows[Math.round(rows.length/2)].windDir:null;
 var _wdirStr=_mainDir!=null?' '+fmtWindDir(_mainDir):'';
 document.getElementById('r-wind').textContent=fmtWind(_windAvg)+_wdirStr;
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
 var _heroEl=document.getElementById('hero');
 if(_heroEl){_heroEl.style.opacity='';_heroEl.style.pointerEvents='';}
 var _lb=document.getElementById('hero-loading-bar');
 if(_lb){_lb.classList.remove('active');}
 setConfBadge(diffDays);
 applyHorizonWording(diffDays);
 document.getElementById('score-block').style.display = 'block';
 if (selectedLoc) updateAffilChips(selectedLoc);
 showSection('hero');
 if (typeof _showDateNav === 'function') _showDateNav();
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
 if (item._local) return ""; // local index match — no geocoder sub
 var lang = (document.documentElement.lang || 'fr').toLowerCase();
 var langKey = lang === 'en' || lang === 'en-us' ? 'en' : lang === 'es' ? 'es' : lang === 'de' ? 'de' : 'fr';
 var FR_TERRITORIES = {
   fr: {'GF':'Guyane française','GP':'Guadeloupe','MQ':'Martinique','RE':'La Réunion','PM':'Saint-Pierre-et-Miquelon','YT':'Mayotte','NC':'Nouvelle-Calédonie','PF':'Polynésie française'},
   en: {'GF':'French Guiana','GP':'Guadeloupe','MQ':'Martinique','RE':'Réunion','PM':'Saint Pierre and Miquelon','YT':'Mayotte','NC':'New Caledonia','PF':'French Polynesia'},
   es: {'GF':'Guayana Francesa','GP':'Guadalupe','MQ':'Martinica','RE':'Reunión','PM':'San Pedro y Miquelón','YT':'Mayotte','NC':'Nueva Caledonia','PF':'Polinesia Francesa'},
   de: {'GF':'Französisch-Guayana','GP':'Guadeloupe','MQ':'Martinique','RE':'Réunion','PM':'Saint-Pierre und Miquelon','YT':'Mayotte','NC':'Neukaledonien','PF':'Französisch-Polynesien'}
 };
 var FRANCE_LABEL = {fr:'France',en:'France',es:'Francia',de:'Frankreich'};
 var COUNTRY_OVERRIDE = {
   de: {'GB':'Vereinigtes Königreich','US':'Vereinigte Staaten','AU':'Australien','NZ':'Neuseeland','AE':'Vereinigte Arabische Emirate','ZA':'Südafrika','MX':'Mexiko','AR':'Argentinien','CL':'Chile','BR':'Brasilien','TH':'Thailand','VN':'Vietnam','PH':'Philippinen','JP':'Japan','CN':'China','IN':'Indien','TR':'Türkei','EG':'Ägypten','MA':'Marokko','TZ':'Tansania','KE':'Kenia','MZ':'Mosambik','MU':'Mauritius','MV':'Malediven','LK':'Sri Lanka','CD':'Demokratische Republik Kongo','CG':'Republik Kongo'}
 };
 var terrMap = FR_TERRITORIES[langKey] || FR_TERRITORIES.fr;
 var isFrDom = !!terrMap[item.country_code];
 if (item.country_code === 'FR' || isFrDom) {
   var terr = isFrDom ? terrMap[item.country_code] : getFrTerritory(item.latitude, item.longitude);
   var region = terr || item.admin1 || '';
   return region + (region ? ', ' : '') + FRANCE_LABEL[langKey];
 }
 var countryName = item.country || '';
 if (COUNTRY_OVERRIDE[langKey] && COUNTRY_OVERRIDE[langKey][item.country_code]) {
   countryName = COUNTRY_OVERRIDE[langKey][item.country_code];
 }
 return (item.admin1 || '') + (item.admin1 && countryName ? ', ' : '') + countryName;
}

function selectAC(i){
 var item=acData[i];if(!item)return;
 // Local index match: use name directly, trigger geocode via selectedLoc=null
 if (item._local) {
   selectedLoc = null;
   document.getElementById('inp-city').value = item.name;
   var clearBtn = document.getElementById('inp-city-clear');
   if (clearBtn) clearBtn.classList.add('visible');
   hideAC();
   return;
 }
 // Pour FR : ne jamais afficher admin1, juste le pays
 var FR_DOM = {'GF':1,'GP':1,'MQ':1,'RE':1,'PM':1,'YT':1,'NC':1,'PF':1};
 var FR_TERRITORY_NAMES = {'GF':'Guyane française','GP':'Guadeloupe','MQ':'Martinique','RE':'La Réunion','PM':'Saint-Pierre-et-Miquelon','YT':'Mayotte','NC':'Nouvelle-Calédonie','PF':'Polynésie française'};
 var isFrDom = !!FR_DOM[item.country_code];
 var region = (item.country_code === 'FR' || isFrDom) ? (isFrDom ? FR_TERRITORY_NAMES[item.country_code] : '') : (item.admin1 || '');
 var country = isFrDom ? 'France' : getCountryName(item);
 selectedLoc={lat:item.latitude,lon:item.longitude,name:item.name,region:region,country:country,country_code:item.country_code||"",elevation:item.elevation||null};
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
 var _gl2=(document.documentElement.lang||'fr').toLowerCase(); if(_gl2==='en-us')_gl2='en'; if(_gl2!=='en'&&_gl2!=='es'&&_gl2!=='de')_gl2='fr';
 // Local index search: inject matching destinations from suggestions.json (supports ES names)
 var localMatches = [];
 if(window._wbSuggestions){
   var qLow=q.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g,'');
   Object.keys(window._wbSuggestions).forEach(function(slug){
     var d=window._wbSuggestions[slug];
     var name=d[_gl2]||d.fr||'';
     var nameLow=name.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g,'');
     if(nameLow.indexOf(qLow)===0){
       localMatches.push({name:name,country_code:d.flag?d.flag.toUpperCase():'',population:9999999,_local:true,_slug:slug,_flag:d.flag});
     }
   });
   localMatches.sort(function(a,b){return a.name.localeCompare(b.name);});
 }
 var base='https://geocoding-api.open-meteo.com/v1/search?count=10&language='+_gl2+'&name=';
 var p1=fetch(base+encodeURIComponent(q)).then(function(r){return r.json();}).then(function(d){return d.results||[];});
 // Si espaces : aussi envoyer version normalisée (tirets + sans accents)
 var qNorm = normalizeQuery(q);
 var p2 = q.indexOf(' ')>=0
 ? fetch(base+encodeURIComponent(qNorm)).then(function(r){return r.json();}).then(function(d){return d.results||[];})
 : Promise.resolve([]);
 Promise.all([p1,p2]).then(function(both){
 var coordSeen={}, merged=[];
 both[0].concat(both[1]).forEach(function(item){
 // Filter airports
 if(item.feature_code==='AIRP'||item.feature_code==='RSTN')return;
 var key=item.name+'|'+item.latitude+'|'+item.longitude;
 if(!coordSeen[key]){coordSeen[key]=1;merged.push(item);}
 });
 merged.sort(function(a,b){return (b.population||0)-(a.population||0);});
 // Track max population per name
 var namePop={};
 for(var j=0;j<merged.length;j++){
  var nm=merged[j].name.toLowerCase(), pop=merged[j].population||0;
  if(!namePop[nm]||pop>namePop[nm]) namePop[nm]=pop;
 }
 // Deduplicate: skip no-pop homonyms when a significant city exists
 var terrSeen={}, deduped=[];
 var domTom={GF:1,GP:1,MQ:1,RE:1,PM:1,YT:1,NC:1,PF:1,WF:1,MF:1,BL:1};
 for(var i=0;i<merged.length&&deduped.length<6;i++){
  var rName=merged[i].name.toLowerCase();
  if(namePop[rName]>=5000&&!(merged[i].population>0)) continue;
  var cc=(merged[i].country_code||'').toUpperCase();
  var territory=domTom[cc]?cc:(cc==='FR'?'FR':cc);
  var tKey=rName+'|'+territory;
  if(!terrSeen[tKey]){terrSeen[tKey]=1;deduped.push(merged[i]);}
 }
 // Prepend local matches not already in deduped
 var localUniq=localMatches.filter(function(lm){
   return !deduped.some(function(d){return d.name.toLowerCase()===lm.name.toLowerCase();});
 }).slice(0,3);
 showAC(localUniq.concat(deduped).slice(0,6));
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
 _histLoaded=false; _histLoading=false;
 var _hSec=document.getElementById('sec-history');
 if(_hSec){_hSec.style.display='';var _hCt=document.getElementById('hist-chart-container');if(_hCt)_hCt.innerHTML='<div class="hist-loader" style="text-align:center;padding:20px;color:#aaa;font-size:13px">⏳</div>';}
 var today=new Date();today.setHours(0,0,0,0);
 var target=new Date(yr,mo,da,0,0,0);
 var diffDays=Math.round((target.getTime()-today.getTime())/86400000);
 window._lastDiff=diffDays;
 // Offline check
 if (!navigator.onLine) { errEl.textContent=T.errOffline; errEl.style.display='block'; return; }
 btnEl.disabled=true; errEl.style.display='none';
 var _heroEl=document.getElementById('hero');
 if(_heroEl&&_heroEl.style.display!=='none'){
   _heroEl.style.opacity='0.35';_heroEl.style.pointerEvents='none';
   var _lb=document.getElementById('hero-loading-bar');
   if(!_lb){_lb=document.createElement('div');_lb.id='hero-loading-bar';_lb.className='hero-loading-bar';var _ht=_heroEl.querySelector('.hero-top');if(_ht)_ht.appendChild(_lb);}
   _lb.classList.add('active');
 } else {
   hideSection('hero');
 }
 hideSection('sec-hourly');hideSection('sec-scenarios');
 var _achips=document.getElementById('affil-chips');if(_achips)_achips.style.display='none';
 var _flw=document.getElementById('fiche-link-wrap');if(_flw){_flw.style.display='none';_flw.innerHTML='';}
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
 // Fiche destination link
 (function(){
  var fw=document.getElementById('fiche-link-wrap');
  if(!fw)return;
  fw.style.display='none'; fw.innerHTML='';
  var slugMap=window.BDW_FICHE_SLUGS;
  if(!slugMap)return;
  var _normStr=function(s){return s.toLowerCase().replace(/[àâä]/g,'a').replace(/[éèêë]/g,'e').replace(/[îï]/g,'i').replace(/[ôö]/g,'o').replace(/[ùûü]/g,'u').replace(/ç/g,'c').replace(/[^a-z0-9 ]/g,'').trim();};
  // Try 1: full name
  var entry=slugMap[_normStr(loc.name)];
  // Try 2: first word only (handles "Guyane française" → "guyane")
  if(!entry) entry=slugMap[_normStr(loc.name.split(/[\s,\-]/)[0])];
  // Try 3: without leading articles (la, le, les, l')
  if(!entry){var bare=loc.name.replace(/^(la |le |les |l'|l')/i,'');entry=slugMap[_normStr(bare)];}
  if(!entry)return;
  var isFr=(CFG.dateLocale==='fr-FR'||CFG.dateLocale==='fr');
  var isEs=(CFG.dateLocale==='es-ES'||CFG.dateLocale==='es');
  var isDe=(CFG.dateLocale==='de-DE'||CFG.dateLocale==='de');
  var ficheSlug=isFr?entry.fr:(isEs?(entry.es||entry.en):entry.en);
  var ficheUrl=isFr?'meilleure-periode-'+ficheSlug+'.html':(isEs?'../es/mejor-epoca-'+ficheSlug+'.html':(isDe?'../de/beste-reisezeit-'+ficheSlug+'.html':'best-time-to-visit-'+ficheSlug+'.html'));
  var label=isFr?'Analyse complète de '+(loc.name):(isEs?'Guía completa de '+loc.name:(isDe?(T.guide_label||'Reiseführer')+' '+loc.name:'Complete guide for '+loc.name));
  fw.innerHTML='<a class="fiche-link-btn" href="'+ficheUrl+'">↗ '+label+'</a>';
  fw.style.display='block';
 })();
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
 setP(100,T.progDone);var _curH=13;if(diffDays===0){var _now=new Date(Date.now()+(_locTzOffset||0)*1000+new Date().getTimezoneOffset()*60000);_curH=_now.getHours();}updateHero(rows,rows,_curH);render7DayStrip(diffDays);showResults(rows,rows,true,T.noteLive,diffDays);progEl.style.display='none';btnEl.disabled=false;
 });
 }
 return buildClimatology(loc.lat,loc.lon,yr,mo,da).then(function(rows){
 if(diffDays>7&&diffDays<=210){setP(92,T.progEcmwf);return fetchSeasonal(loc.lat,loc.lon,yr,mo,da).then(function(seas){return applySeasonalCorrection(rows,seas);});}
 return rows;
 }).then(function(rows){
 renderAstro(loc.lat,loc.lon,yr,mo,da);
 setP(100,T.progDone);seedRand(makeSeed(loc.lat,loc.lon,yr,mo,da));var sc=genMain(rows);updateHero(sc,rows);
    var _fsEl=document.getElementById('forecast-strip');if(_fsEl)_fsEl.style.display='none';
    var note=(diffDays>7&&diffDays<=210)?T.noteEcmwf:T.noteClimate;
    showResults(sc,rows,false,note,diffDays);
    // Snow depth — uniquement si UC ski, en parallèle (silencieux si erreur)
    var _sdEl = document.getElementById('snow-depth-info');
    if (_sdEl) _sdEl.style.display = 'none';
    // Ski altitude warning — vallée < 800m
    var _skiWD = document.getElementById('ski-alt-warn-daily');
    if (!_skiWD) {
     _skiWD = document.createElement('div');
     _skiWD.id = 'ski-alt-warn-daily';
     _skiWD.style.cssText = 'display:none;margin-top:8px;background:#fef3c7;border:1.5px solid #f59e0b;border-radius:8px;padding:10px 12px;font-size:11.5px;color:#92400e;line-height:1.5';
     if (_sdEl && _sdEl.parentNode) _sdEl.parentNode.insertBefore(_skiWD, _sdEl);
    }
    if (currentUseCase === 'ski' && selectedLoc && selectedLoc.elevation != null && selectedLoc.elevation < 800) {
     _skiWD.textContent = T.skiAltWarn.replace('{e}', Math.round(selectedLoc.elevation));
     _skiWD.style.display = 'block';
    } else {
     _skiWD.style.display = 'none';
    }
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
 }).catch(function(err){
  var isNetErr = !navigator.onLine || err instanceof TypeError;
  errEl.textContent = isNetErr ? T.errOffline : T.errPrefix+err.message;
  errEl.style.display='block';progEl.style.display='none';showSection('empty');btnEl.disabled=false;
});
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
 var md = document.getElementById('mode-date');
 var ma = document.getElementById('mode-annual');
 var aw = document.getElementById('annual-wrap');
 if (md) md.className = 'mode-btn' + (isDate ? ' active' : '');
 if (ma) ma.className = 'mode-btn' + (!isDate ? ' active' : '');
 if (aw) aw.style.display = isDate ? 'none' : 'block';
 var dateEls = ['date-form','hero','sec-hourly','sec-scenarios','empty','foot-note'];
 dateEls.forEach(function(id){
  var el = document.getElementById(id);
  if (el) el.style.display = isDate ? '' : 'none';
 });
 // uc-filter-wrap must stay hidden until showResults() — never reset to ''
 var ucfw = document.getElementById('uc-filter-wrap');
 if (ucfw) ucfw.style.display = 'none';
 if (isDate) { var empt = document.getElementById('empty'); if (empt) empt.style.display = 'block'; }
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
 annSelectedLoc = { lat: item.latitude, lon: item.longitude, name: item.name, region: region2, country: country2, elevation: item.elevation||null };
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
 : (setAnnP(10, T.progDownload), getMonthlyCache().then(function(){
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
 _annModelElevation = data.elevation != null ? Math.round(data.elevation) : null;
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
 _annModelElevation = data.elevation != null ? Math.round(data.elevation) : null;
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
 // Altitude correction: adjust temps from model grid elevation to actual location elevation
 var _annLoc = _lastAnnLoc || annSelectedLoc;
 if (_annLoc && _annLoc.elevation != null && _annModelElevation != null) {
  tmax = altCorrection(tmax, _annLoc.elevation, _annModelElevation);
  tmin = altCorrection(tmin, _annLoc.elevation, _annModelElevation);
 }
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
 // Neige : précipitations avec froid = bonus — 0 si pas de gel (neige fond)
 var snowBonus = (tmin < 0 && mm > 2) ? Math.min(100, 60 + mm * 3) : (tmin < 0 && mm > 0 ? 55 : (tmin < 0 ? 15 : 0));
 // Soleil : utile seulement s'il y a de la neige (tmax ≤ 5 = plein, 5-10 = réduit, >10 = inutile)
 var sSunSki = Math.min(100, sun * 8);
 if (tmax > 10) sSunSki = 0;
 else if (tmax > 5) sSunSki = Math.round(sSunSki * 0.4);
 // Pluie chaude (tmax > 2 et pluie) = très mauvais (neige fondue, verglas)
 var sRainSki = tmax > 2 ? Math.max(0, 100 - rain * 1.5) : Math.max(40, 100 - rain * 0.3);
 var total = Math.round(sRainSki * 0.15 + sTempSki * 0.40 + snowBonus * 0.20 + sSunSki * 0.25);
 // Hard cap : ski impossible si trop chaud
 if (tmax > 15) total = Math.min(total, 5);
 else if (tmax > 10) total = Math.min(total, 10);
 return total;
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

 // ── Ski altitude warning ──────────────────────────────────────────────────
 var skiWarnEl = document.getElementById('ski-alt-warn');
 if (!skiWarnEl) {
  skiWarnEl = document.createElement('div');
  skiWarnEl.id = 'ski-alt-warn';
  skiWarnEl.style.cssText = 'display:none;margin:10px 0 6px;background:#fef3c7;border:1.5px solid #f59e0b;border-radius:10px;padding:12px 14px;font-size:12.5px;color:#92400e;line-height:1.5';
  grid.parentNode.insertBefore(skiWarnEl, grid);
 }
 if (uc === 'ski' && loc.elevation != null && loc.elevation < 800) {
  skiWarnEl.textContent = T.skiAltWarn.replace('{e}', Math.round(loc.elevation));
  skiWarnEl.style.display = 'block';
 } else {
  skiWarnEl.style.display = 'none';
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
 var ucw=document.getElementById('ann-uc-wrap');if(ucw)ucw.style.display='';
 setTimeout(function(){var el=document.getElementById('ann-uc-wrap');if(el)el.scrollIntoView({behavior:'smooth',block:'start'});},120);
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
 var _gl3=(document.documentElement.lang||'fr').toLowerCase(); if(_gl3==='en-us')_gl3='en'; if(_gl3!=='en'&&_gl3!=='es'&&_gl3!=='de')_gl3='fr'; annAcTimer=setTimeout(function(){fetch('https://geocoding-api.open-meteo.com/v1/search?name='+encodeURIComponent(q)+'&count=10&language='+_gl3).then(function(r){return r.json();}).then(function(d){var items=(d.results||[]).filter(function(r){return r.feature_code!=='AIRP'&&r.feature_code!=='RSTN'});items.sort(function(a,b){return(b.population||0)-(a.population||0)});var np={};for(var j=0;j<items.length;j++){var nm=items[j].name.toLowerCase(),pop=items[j].population||0;if(!np[nm]||pop>np[nm])np[nm]=pop;}var dt={GF:1,GP:1,MQ:1,RE:1,PM:1,YT:1,NC:1,PF:1,WF:1,MF:1,BL:1},seen={},out=[];for(var i=0;i<items.length&&out.length<6;i++){var rn=items[i].name.toLowerCase();if(np[rn]>=5000&&!(items[i].population>0))continue;var cc=(items[i].country_code||'').toUpperCase(),terr=dt[cc]?cc:(cc==='FR'?'FR':cc),k=rn+'|'+terr;if(!seen[k]){seen[k]=1;out.push(items[i]);}}showAnnAC(out);}).catch(function(){hideAnnAC();});},280);
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
 // Sync unit toggle buttons with default units from i18n config
 setUnits(_units);
 // Sync date placeholder from i18n config
 var inpDate = document.getElementById('inp-date');
 if (inpDate && CFG.datePlaceholder) inpDate.placeholder = CFG.datePlaceholder;
 flatpickr(document.getElementById('inp-date'), {
 dateFormat: CFG.dateFormat || 'd/m/Y',
 locale: CFG.fpLocale || 'fr',
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
 annSelectedLoc = { lat: parseFloat(lat), lon: parseFloat(lon), name: city, region: '', country: '', elevation: null };
 if (uc) { currentUseCase = uc; quickFill(uc); }
 setTimeout(function() { runAnnual(); }, 100);
 }
})();

// ── Date navigation (prev/next day arrows + swipe) ──────────────────────────
(function() {
  var navEl, prevBtn, nextBtn, labelEl;
  var _fp = null; // flatpickr instance reference

  function _pad(n) { return n < 10 ? '0' + n : '' + n; }

  function _dateFromState() {
    if (window._lastYr == null) return null;
    return new Date(window._lastYr, window._lastMo, window._lastDa, 0, 0, 0);
  }

  function _today() {
    var d = new Date(); d.setHours(0,0,0,0); return d;
  }

  function _maxDate() {
    var d = new Date(); d.setHours(0,0,0,0);
    d.setDate(d.getDate() + 365);
    return d;
  }

  function _updateButtons() {
    if (!prevBtn) prevBtn = document.getElementById('date-nav-prev');
    if (!nextBtn) nextBtn = document.getElementById('date-nav-next');
    if (!prevBtn || !nextBtn) return;
    var cur = _dateFromState();
    if (!cur) return;
    prevBtn.disabled = cur <= _today();
    nextBtn.disabled = cur >= _maxDate();
  }

  function _navTo(delta) {
    var cur = _dateFromState();
    if (!cur) return;
    var newDate = new Date(cur.getTime());
    newDate.setDate(newDate.getDate() + delta);
    var minD = _today(), maxD = _maxDate();
    if (newDate < minD || newDate > maxD) return;

    var iso = newDate.getFullYear() + '-' + _pad(newDate.getMonth()+1) + '-' + _pad(newDate.getDate());

    // Update flatpickr if available
    var inpDate = document.getElementById('inp-date');
    if (inpDate && inpDate._flatpickr) {
      inpDate._flatpickr.setDate(iso, false);
    }
    inpDate._isoValue = iso;

    // Also update the city field to keep state consistent
    if (typeof run === 'function') { run(); }
  }

  function _showNav() {
    if (!navEl) navEl = document.getElementById('date-nav');
    if (!navEl) return;
    navEl.style.display = 'flex';
    _updateButtons();
  }

  // Expose globally so showResults() can call it
  window._showDateNav = _showNav;

  document.addEventListener('DOMContentLoaded', function() {
    navEl   = document.getElementById('date-nav');
    prevBtn = document.getElementById('date-nav-prev');
    nextBtn = document.getElementById('date-nav-next');
    labelEl = document.getElementById('date-nav-label');

    if (!navEl) return;

    prevBtn.addEventListener('click', function() { _navTo(-1); });
    nextBtn.addEventListener('click', function() { _navTo(+1); });

    // Hide nav when a new search starts (hero is hidden)
    var _hero = document.getElementById('hero');
    if (_hero) {
      new MutationObserver(function() {
        if (_hero.style.display === 'none') navEl.style.display = 'none';
      }).observe(_hero, { attributes: true, attributeFilter: ['style'] });
    }

    // Swipe support on hero
    var hero = document.getElementById('hero');
    if (hero) {
      var _tx = 0;
      hero.addEventListener('touchstart', function(e) {
        _tx = e.changedTouches[0].clientX;
      }, { passive: true });
      hero.addEventListener('touchend', function(e) {
        var dx = e.changedTouches[0].clientX - _tx;
        if (Math.abs(dx) > 50) { _navTo(dx < 0 ? +1 : -1); }
      }, { passive: true });
    }
  });
})();
