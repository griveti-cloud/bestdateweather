/* Page « Où partir au soleil toute l'année ? » : miroir exact de lib/annual_engine.py.
 * Le HTML écrit par le générateur est l'état par défaut ; ce script ne recalcule
 * qu'après une action du visiteur. Données : engine/data-v1.json. */
(function () {
  'use strict';
  var C = window.BDW_ANNUAL;
  if (!C) return;
  var L = C.i18n, T = C.t, A = C.a, LANG = C.lang, NI = LANG === 'fr' ? 0 : 1, GOOD = 7.6;
  var UC_KEY = { gen: 's', plage: 'b', ski: 'k', rando: 'hk' };
  var st = JSON.parse(JSON.stringify(C.state));
  var DATA = null, pending = null, ADV = null;

  function $(id) { return document.getElementById(id); }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function fmt(s, o) { return s.replace(/\{(\w+)\}/g, function (m, k) { return Object.prototype.hasOwnProperty.call(o, k) ? o[k] : m; }); }
  function pad(n) { return (n < 10 ? '0' : '') + n; }
  function f1(x) { var s = (Math.round(x * 10 + 1e-9) / 10).toFixed(1); return LANG === 'fr' ? s.replace('.', ',') : s; }
  function r0(x) { return String(Math.round(x)); }
  function fmtH(h) { var t = Math.round(h * 12) * 5, hh = Math.floor(t / 60), mm = t % 60; return LANG === 'fr' ? hh + ' h ' + pad(mm) : hh + 'h' + pad(mm); }
  function fmtKm(km) { var n = String(Math.round(km)), sep = LANG === 'fr' ? ' ' : ',', out = ''; while (n.length > 3) { out = sep + n.slice(-3) + out; n = n.slice(0, -3); } return n + out + ' km'; }
  function hav(a, b, c, d) { var r = Math.PI / 180, p1 = a * r, p2 = c * r, dp = p2 - p1, dl = (d - b) * r; return 2 * 6371 * Math.asin(Math.sqrt(Math.pow(Math.sin(dp / 2), 2) + Math.cos(p1) * Math.cos(p2) * Math.pow(Math.sin(dl / 2), 2))); }
  function depOf() { return st.dep >= 0 ? L.deps[st.dep] : [st.depName, st.depLat, st.depLon]; }
  function cellCls(v) { return v == null ? 'n' : v >= 8.6 ? 'e' : v >= 7.6 ? 't' : v >= 6.3 ? 'b' : v >= 5 ? 'p' : v >= 3.5 ? 'm' : 'x'; }

  function evaluate(d, uc, dep) {
    var mtn = uc === 'ski' || uc === 'rando';
    if (mtn && !d.m) return null;
    var M = d.M, vals = M[UC_KEY[uc]], i;
    for (i = 0; i < 12; i++) if (vals[i] == null || M.tx[i] == null) return null;
    var good = 0, sum = 0, mx = -1, t1 = Infinity, t2 = -Infinity, rain = 0;
    for (i = 0; i < 12; i++) { if (vals[i] >= GOOD) good++; sum += vals[i]; if (vals[i] > mx) mx = vals[i]; t1 = Math.min(t1, M.tx[i]); t2 = Math.max(t2, M.tx[i]); rain += M.r[i]; }
    var order = []; for (i = 0; i < 12; i++) order.push(i);
    order.sort(function (a, b) { return (vals[b] - vals[a]) || (a - b); });
    var rl = d.rl; if (ADV && d.cc && ADV[d.cc] != null) rl = Math.max(rl, ADV[d.cc]);
    var o = { d: d, uc: uc, score: mtn ? mx : sum / 12, good: good, vals: vals, best3: order.slice(0, 3).sort(function (a, b) { return a - b; }), best: order[0], t1: t1, t2: t2, rain: rain / 12, rl: rl };
    o.km = hav(dep[1], dep[2], d.la, d.lo); o.h = 0.75 + o.km / 850;
    return o;
  }
  function cmpKeys(ka, kb) { for (var i = 0; i < ka.length; i++) { if (ka[i] < kb[i]) return -1; if (ka[i] > kb[i]) return 1; } return 0; }
  var KEYS = {
    score: function (x) { return [-x.score, x.d.s]; },
    regular: function (x) { return [-x.good, -x.score, x.d.s]; },
    near: function (x) { return [x.h, x.d.s]; },
    cheap: function (x) { return [x.d.bi, -x.score, x.d.s]; }
  };
  function sortBy(arr, key) { var f = KEYS[key]; return arr.slice().sort(function (a, b) { return cmpKeys(f(a), f(b)); }); }
  function dropParents(rows) { var p = {}; rows.forEach(function (x) { p[x.d.s] = 1; }); return rows.filter(function (x) { return !(x.d.ch || []).some(function (c) { return p[c]; }); }); }

  function computeView() {
    var dep = depOf(), ev = {}, mtn = st.uc === 'ski' || st.uc === 'rando';
    Object.keys(UC_KEY).forEach(function (k) { ev[k] = DATA.dests.map(function (d) { return evaluate(d, k, dep); }).filter(Boolean); });
    function okBase(x) { return x.rl <= st.rl && x.d.bi <= st.budget; }
    function okFly(x) { return st.fly >= 16 || x.h <= st.fly; }
    function okGood(x) { return x.good >= st.good; }
    function okReg(x) { return st.reg === 'all' || x.d.reg === st.reg; }
    var rows = sortBy(dropParents(ev[st.uc].filter(function (x) { return okBase(x) && okFly(x) && okGood(x) && okReg(x); })), st.sort);
    var facts = [], used = {};
    function pick(arr, key, fn) { for (var i = 0; i < arr.length; i++) { if (!used[arr[i].d.s]) { used[arr[i].d.s] = 1; facts.push({ k: key, x: arr[i], fn: fn }); return; } } }
    if (!mtn) {
      pick(sortBy(rows, 'regular'), 'f_regular', 'fd_regular');
      var cand = rows.filter(function (x) { return x.good >= 9; });
      pick(sortBy(cand, 'near'), 'f_near', 'fd_near');
      pick(sortBy(cand, 'cheap'), 'f_cheap', 'fd_cheap');
      pick(sortBy(rows.filter(function (x) { return x.d.reg === 'eu' || x.d.reg === 'atl'; }), 'regular'), 'f_europe', 'fd_europe');
    } else {
      pick(sortBy(rows, 'score'), 'f_best', 'fd_best');
      var c2 = rows.filter(function (x) { return x.score >= 7; });
      pick(sortBy(c2, 'near'), 'f_near_m', 'fd_best');
      pick(sortBy(c2, 'cheap'), 'f_cheap_m', 'fd_best');
    }
    var projects = {};
    ['plage', 'ski', 'rando'].forEach(function (k) { projects[k] = sortBy(dropParents(ev[k].filter(function (x) { return okBase(x) && okFly(x); })), 'score').slice(0, 5); });
    var g = dropParents(ev.gen.filter(okBase)), regions = {};
    Object.keys(L.regions).forEach(function (r) { if (r === 'other') return; var top = sortBy(g.filter(function (x) { return x.d.reg === r; }), 'score').slice(0, 4); if (top.length) regions[r] = top; });
    var months = [];
    for (var m = 0; m < 12; m++) months.push(g.slice().sort((function (mm) { return function (a, b) { return cmpKeys([-a.vals[mm], a.d.s], [-b.vals[mm], b.d.s]); }; })(m)).slice(0, 3));
    return { rows: rows, n_uc: ev[st.uc].length, facts: facts, projects: projects, regions: regions, months: months };
  }

  // ── rendu (miroir de lib/annual_engine.py) ──
  function nm(x) { return esc(x.d.n[NI]); }
  function href(x) { return fmt(C.annual, { s: x.d.s, e: x.d.e }); }
  function bestMonths(x) { return x.best3.map(function (i) { return L.ms[i]; }).join(', '); }
  function factText(f) { var x = f.x; return fmt(T[f.fn], { g: x.good, s: f1(x.score), h: fmtH(x.h), dep: depOf()[0], b: L.budget[String(x.d.bi)].toLowerCase(), t1: r0(x.t1), t2: r0(x.t2), bm: L.months[x.best] }); }
  function stripHtml(x) {
    var cells = x.vals.map(function (v, i) { return '<span class="ma-c ' + cellCls(v) + '" title="' + esc(fmt(T.cell, { m: L.months[i], s: f1(v) })) + '"></span>'; }).join('');
    return '<div class="ma-strip">' + cells + '</div><div class="ma-letters" aria-hidden="true">' + A.mi.map(function (l) { return '<span>' + l + '</span>'; }).join('') + '</div>';
  }
  function itemHtml(x, i) {
    var mtn = x.uc === 'ski' || x.uc === 'rando';
    var badges = '<span class="me-badge v' + x.rl + '">' + esc(L.secu[String(x.rl)]) + '</span><span class="me-badge">' + esc(L.budget[String(Math.max(1, Math.min(5, x.d.bi)))]) + '</span>';
    var sc = fmt(mtn ? T.score_best : T.score_year, { s: f1(x.score) });
    var cls = x.score < 5 ? ' low' : (x.score < 7.6 ? ' mid' : '');
    return '<article class="me-item ma-item"><div class="me-rank">' + (i + 1) + '</div>' +
      '<div class="me-name"><a href="' + href(x) + '">' + nm(x) + '</a><span>' + esc(x.d.p[NI]) + ' · ' + fmtKm(x.km) + '</span><div class="me-badges">' + badges + '</div></div>' +
      '<div class="me-metrics"><span class="me-t">' + esc(fmt(T.temps, { t1: r0(x.t1), t2: r0(x.t2) })) + '</span><span>' + esc(fmt(T.rain, { r: r0(x.rain) })) + ' · ' + esc(fmt(T.flight, { h: fmtH(x.h) })) + '</span></div>' +
      '<div class="me-dry">' + stripHtml(x) + '<div>' + fmt(T.good_line, { g: x.good, bm: esc(bestMonths(x)) }) + '</div></div>' +
      '<div class="me-side"><span class="me-score' + cls + '">' + esc(sc) + '</span><a href="' + href(x) + '">' + esc(T.card) + '</a></div></article>';
  }
  function miniLi(x) { return '<li><a href="' + href(x) + '">' + nm(x) + '</a><span>' + esc(fmt(T.mini, { g: x.good })) + ' · <b>' + f1(x.score) + '</b></span></li>'; }
  function monthLi(x, m) { return '<li><a href="' + href(x) + '">' + nm(x) + '</a><span><b>' + f1(x.vals[m]) + '</b></span></li>'; }
  function renderControls() {
    [['me-uc', 'uc', false], ['me-good', 'good', true], ['me-budget', 'budget', true], ['me-secu', 'rl', true]].forEach(function (g) {
      Array.prototype.forEach.call($(g[0]).querySelectorAll('.me-chip'), function (b) { var v = g[2] ? Number(b.dataset.v) : b.dataset.v; b.setAttribute('aria-pressed', String(v === st[g[1]])); });
    });
    $('me-fly-val').textContent = st.fly >= 16 ? T.fly_any : fmtH(st.fly).replace(LANG === 'fr' ? ' h 00' : 'h00', LANG === 'fr' ? ' h' : 'h');
    $('me-reg').value = st.reg; $('me-fly').value = String(st.fly); $('me-sort').value = st.sort;
    var sel = $('me-dep'), cust = sel.querySelector('option[value="custom"]');
    if (st.dep < 0) { if (!cust) { cust = document.createElement('option'); cust.value = 'custom'; sel.insertBefore(cust, sel.querySelector('option[value="other"]')); } cust.textContent = st.depName; sel.value = 'custom'; }
    else { if (cust) cust.remove(); sel.value = String(st.dep); }
  }
  function renderView(v) {
    $('me-facts').style.setProperty('--n', Math.max(1, v.facts.length));
    $('me-facts').innerHTML = v.facts.map(function (f) { return '<div class="me-fact"><div class="me-k">' + esc(T[f.k]) + '</div><a class="me-v" href="' + href(f.x) + '">' + nm(f.x) + '</a><div class="me-d">' + esc(factText(f)) + '</div></div>'; }).join('');
    var reg = st.reg !== 'all' ? ' · ' + L.regions[st.reg] : '';
    $('me-rank-title').textContent = fmt(T.top, { n: Math.min(st.shown, v.rows.length), uc: L.uc_t[st.uc], reg: reg });
    $('me-count').textContent = fmt(v.rows.length > 1 ? T.count : T.count1, { k: v.rows.length, n: v.n_uc });
    $('me-list').innerHTML = v.rows.length ? v.rows.slice(0, st.shown).map(itemHtml).join('') : '<p class="me-empty">' + esc(T.empty) + '</p>';
    $('me-more').hidden = v.rows.length <= st.shown;
    $('me-projects').innerHTML = ['plage', 'ski', 'rando'].map(function (k) {
      var top = v.projects[k];
      return '<div class="me-box"><div class="me-box-head"><h3>' + esc(L.uc[k]) + '</h3><button type="button" class="me-link" data-uc="' + k + '">' + esc(T.see_all) + '</button></div><ul class="me-mini">' + (top.length ? top.map(miniLi).join('') : '<li><span>' + esc(T.none) + '</span></li>') + '</ul></div>';
    }).join('');
    $('me-regions').innerHTML = Object.keys(L.regions).filter(function (r) { return v.regions[r]; }).map(function (r) {
      return '<div class="me-box"><div class="me-box-head"><h3>' + esc(L.regions[r]) + '</h3><button type="button" class="me-link" data-reg="' + r + '">' + esc(T.see) + '</button></div><ul class="me-mini">' + v.regions[r].map(miniLi).join('') + '</ul></div>';
    }).join('');
    Array.prototype.forEach.call($('me-bymonth').querySelectorAll('.me-mini'), function (ul, m) { ul.innerHTML = v.months[m].map(function (x) { return monthLi(x, m); }).join(''); });
  }
  function render() { renderControls(); if (DATA) renderView(computeView()); }
  function fail() { $('me-count').textContent = T.err_load; }
  function ensureData() {
    if (DATA) return Promise.resolve(DATA);
    if (!pending) {
      pending = fetch(C.data).then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); }).then(function (d) { DATA = d; return d; });
      fetch('/api/advisories').then(function (r) { return r.ok ? r.json() : null; }).catch(function () { return null; }).then(function (a) { if (a && !a.error) { ADV = a; if (DATA && C.touched) render(); } });
    }
    return pending;
  }
  function act(fn) { return function (e) { C.touched = true; var r = fn(e); if (r === false) return; render(); ensureData().then(render, fail); }; }
  function onChips(id, key, numeric) { $(id).addEventListener('click', act(function (e) { var b = e.target.closest('.me-chip'); if (!b) return false; st[key] = numeric ? Number(b.dataset.v) : b.dataset.v; st.shown = C.page; })); }
  function goList() { var el = $('me-classement'); if (el && el.scrollIntoView) el.scrollIntoView({ behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth', block: 'start' }); }
  onChips('me-uc', 'uc', false); onChips('me-good', 'good', true); onChips('me-budget', 'budget', true); onChips('me-secu', 'rl', true);
  $('me-reg').addEventListener('change', act(function (e) { st.reg = e.target.value; st.shown = C.page; }));
  $('me-fly').addEventListener('input', act(function (e) { st.fly = Number(e.target.value); st.shown = C.page; }));
  $('me-sort').addEventListener('change', act(function (e) { st.sort = e.target.value; }));
  $('me-more').addEventListener('click', act(function () { st.shown += C.page; }));
  $('me-projects').addEventListener('click', function (e) { var b = e.target.closest('[data-uc]'); if (!b) return; C.touched = true; st.uc = b.dataset.uc; st.shown = C.page; render(); ensureData().then(function () { render(); goList(); }, fail); });
  $('me-regions').addEventListener('click', function (e) { var b = e.target.closest('[data-reg]'); if (!b) return; C.touched = true; st.reg = b.dataset.reg; st.uc = 'gen'; st.shown = C.page; render(); ensureData().then(function () { render(); goList(); }, fail); });
  $('me-tool').addEventListener('submit', function (e) { e.preventDefault(); });
  // ville de départ (mêmes règles et même mémorisation que les pages mensuelles)
  function saveDep() { try { localStorage.setItem('bdw_dep_' + LANG, JSON.stringify(st.dep >= 0 ? { i: st.dep } : { n: st.depName, la: st.depLat, lo: st.depLon })); } catch (e) {} }
  $('me-dep').addEventListener('change', function (e) {
    var v = e.target.value;
    if (v === 'other') { $('me-city').hidden = false; $('me-city-q').value = ''; $('me-city-sug').innerHTML = ''; $('me-city-q').focus(); return; }
    $('me-city').hidden = true;
    if (v === 'custom') return;
    C.touched = true; st.dep = Number(v); saveDep(); render(); ensureData().then(render, fail);
  });
  var cityTimer = null, cityReq = 0;
  $('me-city-q').addEventListener('input', function (e) {
    var q = e.target.value.trim(), box = $('me-city-sug');
    clearTimeout(cityTimer);
    if (q.length < 2) { box.innerHTML = ''; return; }
    cityTimer = setTimeout(function () {
      var id = ++cityReq;
      fetch('https://geocoding-api.open-meteo.com/v1/search?count=6&language=' + LANG + '&name=' + encodeURIComponent(q)).then(function (r) { return r.json(); }).then(function (d) {
        if (id !== cityReq) return;
        var res = (d && d.results) || [];
        box.innerHTML = res.length ? res.map(function (x, i) { return '<button type="button" role="option" data-i="' + i + '">' + esc(x.name + ' (' + [x.admin1, x.country].filter(Boolean).join(', ') + ')') + '</button>'; }).join('') : '<p>' + esc(T.city_none) + '</p>';
        box.__res = res;
      }).catch(function () { if (id === cityReq) box.innerHTML = '<p>' + esc(T.city_err) + '</p>'; });
    }, 300);
  });
  $('me-city-sug').addEventListener('click', function (e) {
    var b = e.target.closest('button'); if (!b) return;
    var x = this.__res[Number(b.dataset.i)];
    st.dep = -1; st.depName = x.name; st.depLat = x.latitude; st.depLon = x.longitude; saveDep();
    $('me-city').hidden = true; C.touched = true; render(); ensureData().then(render, fail);
  });
  var fromStore = false;
  try { var sd = JSON.parse(localStorage.getItem('bdw_dep_' + LANG) || 'null'); if (sd) { if (sd.i != null && sd.i !== st.dep && L.deps[sd.i]) { st.dep = sd.i; fromStore = true; } else if (sd.n && typeof sd.la === 'number') { st.dep = -1; st.depName = sd.n; st.depLat = sd.la; st.depLon = sd.lo; fromStore = true; } } } catch (e) {}
  if (fromStore) { C.touched = true; render(); ensureData().then(render, fail); }
  var idle = window.requestIdleCallback || function (f) { return setTimeout(f, 1500); };
  idle(function () { ensureData().catch(function () {}); });
  window.BDW_ANNUAL_TEST = { compute: function (s) { st = JSON.parse(JSON.stringify(s)); return ensureData().then(function () { var v = computeView(); return { rows: v.rows.map(function (x) { return [x.d.s, f1(x.score), x.good]; }), facts: v.facts.map(function (f) { return [f.k, f.x.d.s]; }), months: v.months.map(function (a) { return a.map(function (x) { return x.d.s; }); }) }; }); } };
})();
