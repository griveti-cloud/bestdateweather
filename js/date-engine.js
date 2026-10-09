/* Moteur « Où partir à mes dates » : pages « Où partir en [mois] ».
 * Miroir exact de lib/date_engine.py + lib/engine_render.py : le HTML écrit par
 * le générateur est l'état par défaut ; ce script ne recalcule qu'après une
 * action du visiteur. Données : engine/data-v1.json (chargées à la demande). */
(function () {
  'use strict';
  var C = window.BDW_ENGINE;
  if (!C) return;
  var L = C.i18n, T = L.t, LANG = C.lang, NF = L.nf, IMP = !!NF.imp, U = IMP ? ' °F' : ' °C';
  var CUM = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334];
  var UC_KEY = { gen: 's', plage: 'b', ski: 'k', rando: 'hk' };
  var st = JSON.parse(JSON.stringify(C.state));
  var DATA = null, pending = null, ADV = null;
  function depOf() { return st.dep >= 0 ? L.deps[st.dep] : [st.depName, st.depLat, st.depLon]; }

  function $(id) { return document.getElementById(id); }
  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
  function fmt(s, o) { return s.replace(/\{(\w+)\}/g, function (m, k) { return Object.prototype.hasOwnProperty.call(o, k) ? o[k] : m; }); }
  function pad(n) { return (n < 10 ? '0' : '') + n; }
  function f1(x) { var s = (Math.round(x * 10 + 1e-9) / 10).toFixed(1); return NF.dec === ',' ? s.replace('.', ',') : s; }
  function r0(x) { return String(Math.round(x)); }
  function tc(x) { return IMP ? x * 9 / 5 + 32 : x; }          // données en °C → unité de la langue
  function t1(x) { return IMP ? r0(tc(x)) : f1(x); }
  function t0(x) { return r0(tc(x)); }
  function fmtH(h) { var t = Math.round(h * 12) * 5; return fmt(NF.h, { h: Math.floor(t / 60), mm: pad(t % 60) }); }
  function fmtKm(km) { var n = String(Math.round(IMP ? km / 1.609344 : km)), sep = NF.th, out = ''; while (n.length > 3) { out = sep + n.slice(-3) + out; n = n.slice(0, -3); } return n + out + (IMP ? ' mi' : ' km'); }
  function D(iso) { var p = iso.split('-'); return new Date(Date.UTC(+p[0], +p[1] - 1, +p[2])); }
  function doy(mmdd) { var p = mmdd.split('-'); return CUM[+p[0] - 1] + (+p[1]) - 1; }
  function monthOf(i) { var m = 11; while (CUM[m] > i) m--; return m; }
  function dayNum(d) { return (NF.first && d === 1) ? NF.first : String(d); }
  function longDate(iso) { var d = D(iso); return fmt(NF.date, { wd: L.wd[d.getUTCDay()], d: dayNum(d.getUTCDate()), m: L.months[d.getUTCMonth()], y: d.getUTCFullYear() }); }
  function shortRange() {
    var a = D(st.from), b = D(st.to), ma = a.getUTCMonth(), mb = b.getUTCMonth(), da = dayNum(a.getUTCDate()), db = dayNum(b.getUTCDate());
    return ma === mb ? fmt(NF.rs, { a: da, b: db, m: L.months[mb] }) : fmt(NF.rd, { a: da, ma: L.months[ma], b: db, mb: L.months[mb] });
  }
  function hav(a, b, c, d) { var r = Math.PI / 180, p1 = a * r, p2 = c * r, dp = p2 - p1, dl = (d - b) * r; return 2 * 6371 * Math.asin(Math.sqrt(Math.pow(Math.sin(dp / 2), 2) + Math.cos(p1) * Math.cos(p2) * Math.pow(Math.sin(dl / 2), 2))); }
  function holidays() { return L.holidays[String(st.month)] || []; }
  function holiday() { var hs = holidays(); for (var i = 0; i < hs.length; i++) if (hs[i].id === st.preset) return hs[i]; return null; }
  function rangeOf(h) { return h.zones ? h.zones[st.zone] : [h.a, h.b]; }
  function monthRange() { var m = st.month, y = m >= 9 ? 2026 : 2027, len = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][m]; return [y + '-' + pad(m + 1) + '-01', y + '-' + pad(m + 1) + '-' + pad(len)]; }

  // ── calcul (miroir de lib/date_engine.py) ──
  function windowOf() {
    if (!st.from || !st.to) return { error: 'err_missing' };
    var span = (D(st.to) - D(st.from)) / 864e5 + 1;
    if (span < 1) return { error: 'err_order' };
    if (span > 62) return { error: 'err_long' };
    var f = st.from.slice(5), t = st.to.slice(5);
    if (f === '02-29') f = '03-01';
    if (t === '02-29') t = '02-28';
    var a = doy(f), b = doy(t), cross = a > b, days = [], i;
    if (!cross) { for (i = a; i <= b; i++) days.push([i, 0]); }
    else { for (i = a; i <= 364; i++) days.push([i, 0]); for (i = 0; i <= b; i++) days.push([i, 1]); }
    return { days: days, cross: cross, n: days.length, limit: Math.max(1, Math.round(days.length / 7)) };
  }
  var BYTES = {};
  function bit(b64, i) { var by = BYTES[b64]; if (!by) { var s = atob(b64); by = BYTES[b64] = []; for (var j = 0; j < s.length; j++) by.push(s.charCodeAt(j)); } return (by[i >> 3] >> (7 - (i & 7))) & 1; }
  function rl(d) { var v = d.rl; if (ADV && d.cc && ADV[d.cc] != null) v = Math.max(v, ADV[d.cc]); return v; }
  function evaluate(d, w, uc, dep) {
    if ((uc === 'ski' || uc === 'rando') && !d.m) return null;
    var k = UC_KEY[uc], M = d.M, sc = 0, tx = 0, tn = 0, sun = 0, rr = 0, sea = 0, seaOk = true;
    for (var j = 0; j < w.days.length; j++) {
      var i = w.days[j][0], m = monthOf(i), v = M[k][m];
      if (v == null || M.tx[m] == null) return null;
      sc += v; tx += d.tw ? d.tw[Math.min(51, Math.floor(i / 7))] : M.tx[m]; tn += M.tn[m]; sun += M.sun[m]; rr += M.r[m] / 100;
      if (M.sea[m] == null) seaOk = false; else sea += M.sea[m];
    }
    var n = w.n, o = { d: d, uc: uc, score: sc / n, tmax: tx / n, tmin: tn / n, sun: sun / n, sea: seaOk ? sea / n : null, mean: rr, share: rr / n, daily: false };
    if (d.r) {
      var Y = DATA.years, nS = w.cross ? Y.length - 1 : Y.length, seasons = [];
      for (var kk = 0; kk < nS; kk++) {
        var ok = true, rd = 0;
        for (var q = 0; q < w.days.length; q++) { var b = d.r[kk + w.days[q][1]]; if (b == null) { ok = false; break; } rd += bit(b, w.days[q][0]); }
        if (ok) seasons.push({ y: Y[kk], rd: rd });
      }
      if (seasons.length >= 6) {
        var tot = 0; seasons.forEach(function (x) { tot += x.rd; });
        o.daily = true; o.seasons = seasons; o.mean = tot / seasons.length; o.share = o.mean / n;
        o.dry = seasons.filter(function (x) { return x.rd <= w.limit; }).length; o.ns = seasons.length;
      }
    }
    o.km = hav(dep[1], dep[2], d.la, d.lo); o.h = 0.75 + o.km / 850;
    var best = -1, bi = 0; M.s.forEach(function (x, ix) { if (x != null && x > best) { best = x; bi = ix; } });
    o.bestSc = best; o.best = bi; o.rl = rl(d);
    return o;
  }
  function cmpKeys(ka, kb) { for (var i = 0; i < ka.length; i++) { if (ka[i] < kb[i]) return -1; if (ka[i] > kb[i]) return 1; } return 0; }
  var KEYS = {
    score: function (x) { return [-x.score, x.d.s]; },
    dry: function (x) { return [x.share, -((x.dry || 0) / (x.ns || 1)), -x.score, x.d.s]; },
    hot: function (x) { return [-x.tmax, x.d.s]; },
    near: function (x) { return [x.h, x.d.s]; },
    cheap: function (x) { return [x.d.bi, -x.score, x.d.s]; }
  };
  function sortBy(arr, key) { var f = KEYS[key]; return arr.slice().sort(function (a, b) { return cmpKeys(f(a), f(b)); }); }
  function dropParents(rows) { var p = {}; rows.forEach(function (x) { p[x.d.s] = 1; }); return rows.filter(function (x) { return !(x.d.ch || []).some(function (c) { return p[c]; }); }); }

  function computeView() {
    var w = windowOf();
    if (w.error) return { error: w.error };
    var dep = depOf(), ev = {}, mtn = st.uc === 'ski' || st.uc === 'rando';
    Object.keys(UC_KEY).forEach(function (k) { ev[k] = DATA.dests.map(function (d) { return evaluate(d, w, k, dep); }).filter(Boolean); });
    function okBase(x) { return x.rl <= st.rl && x.d.bi <= st.budget; }
    function okFly(x) { return st.fly >= 16 || x.h <= st.fly; }
    function okHeat(x) { return mtn || x.tmax >= st.heat; }
    function okReg(x) { return st.reg === 'all' || x.d.reg === st.reg; }
    var rows = sortBy(dropParents(ev[st.uc].filter(function (x) { return okBase(x) && okFly(x) && okHeat(x) && okReg(x); })), st.sort);
    var facts = [], used = {};
    function pick(arr, key, fn, cls) { for (var i = 0; i < arr.length; i++) { if (!used[arr[i].d.s]) { used[arr[i].d.s] = 1; facts.push({ k: key, x: arr[i], cls: cls || '', fn: fn }); return; } } }
    if (!mtn) {
      var good = rows.filter(function (x) { return x.score >= 7; });
      pick(sortBy(good.length ? good : rows, 'dry'), 'f_safe', 'fd_safe');
      var cand = rows.filter(function (x) { return x.share <= 0.10 && x.score >= 7; });
      pick(sortBy(cand, 'near'), 'f_near', 'fd_near');
      pick(sortBy(cand, 'cheap'), 'f_cheap', 'fd_cheap');
      var ww = function (arr) { return arr.filter(function (x) { return x.bestSc >= 7.5 && x.tmax >= Math.max(st.heat, 20) && x.share >= 0.35; }).sort(function (a, b) { return cmpKeys([-a.tmax, a.d.s], [-b.tmax, b.d.s]); }); };
      var near = ww(ev[st.uc].filter(function (x) { return okBase(x) && okFly(x); }));
      if (near.length) pick(near, 'f_trap', 'fd_trap', 'warn'); else pick(ww(ev[st.uc].filter(okBase)), 'f_trap_far', 'fd_trap', 'warn');
    } else {
      pick(sortBy(rows, 'score'), st.uc === 'ski' ? 'f_best_ski' : 'f_best_rando', 'fd_best_m');
      var c2 = rows.filter(function (x) { return x.score >= 7; });
      pick(sortBy(c2, 'near'), 'f_near_m', 'fd_near_m');
      pick(sortBy(c2, 'cheap'), 'f_cheap_m', 'fd_cheap_m');
    }
    var projects = {};
    ['plage', 'ski', 'rando'].forEach(function (k) { projects[k] = sortBy(dropParents(ev[k].filter(function (x) { return okBase(x) && okFly(x); })), 'score').slice(0, 5); });
    var g = dropParents(ev.gen.filter(okBase)), regions = {};
    Object.keys(L.regions).forEach(function (r) { if (r === 'other') return; var top = sortBy(g.filter(function (x) { return x.d.reg === r; }), 'score').slice(0, 4); if (top.length) regions[r] = top; });
    var avoid = dropParents(ev.gen.filter(function (x) { return !x.d.m; })).sort(function (a, b) { return cmpKeys([a.score, a.d.s], [b.score, b.d.s]); }).slice(0, 8);
    return { w: w, rows: rows, n_uc: ev[st.uc].length, n_gen: ev.gen.length, facts: facts, projects: projects, regions: regions, avoid: avoid };
  }

  // ── rendu (miroir de lib/engine_render.py) ──
  var NI = NF.ni;
  function nm(x) { return esc(x.d.n[NI]); }
  function href(x) { return fmt(C.annual, { s: x.d.s, e: x.d.e, se: x.d.se || '', sd: x.d.sd || '' }); }
  function where() { var h = holiday(); return st.preset === 'month' ? L.months[st.month] : (h ? (h.wh || h.chip.charAt(0).toLowerCase() + h.chip.slice(1)) : T.your_dates_where); }
  function scoreCls(s) { return s >= 7.6 ? '' : (s >= 5 ? ' mid' : ' low'); }
  function dryTxt(x, w) { return x.daily ? fmt(T.dry_years, { k: x.dry, n: x.ns }) : (x.mean < 0.5 ? fmt(T.lt1, { n: w.n }) : fmt(T.approx_days, { x: f1(x.mean), n: w.n })); }
  function cap(s) { return s.charAt(0).toUpperCase() + s.slice(1); }
  function factText(f, w) {
    var x = f.x, o = { t: t1(x.tmax), h: fmtH(x.h), dep: depOf()[0], b: L.budget[String(x.d.bi)].toLowerCase(), dry: dryTxt(x, w), bm: L.months[x.best], bs: f1(x.bestSc), x: f1(x.mean), n: w.n, s: f1(x.score), tn: t0(x.tmin), tx: t0(x.tmax) };
    var s = fmt(T[f.fn], o);
    return f.fn === 'fd_safe' ? cap(s) : s;
  }
  function renderHero(w) {
    var h = holiday();
    if (st.preset === 'month') $('me-h1').innerHTML = fmt(T.h1_month, { m: L.months[st.month] });
    else $('me-h1').innerHTML = fmt(T.h1_other, { x: h ? h.em : (w.error ? T.your_dates : shortRange()) });
    $('me-when').innerHTML = w.error ? '' : fmt(T.when, { a: longDate(st.from), b: longDate(st.to), n: w.n });
    $('me-sub').textContent = h ? (h.zones ? fmt(T.sub_zone, { z: st.zone, list: L.zones[st.zone] }) : h.note) : (st.preset === 'month' ? T.sub_month : T.sub_dates);
    $('me-span').textContent = w.error ? '' : fmt(T.n_days, { n: w.n });
  }
  function renderPresets() {
    var hs = holidays(), h = holiday();
    $('me-presets').innerHTML = '<button type="button" class="me-chip" data-p="month" aria-pressed="' + (st.preset === 'month') + '">' + esc(fmt(T.all_month, { m: L.months[st.month] })) + '</button>' +
      hs.map(function (x) { return '<button type="button" class="me-chip" data-p="' + x.id + '" aria-pressed="' + (st.preset === x.id) + '">' + esc(x.chip) + (x.zones ? ' ▾' : '') + '</button>'; }).join('');
    var z = $('me-zone');
    z.hidden = !(h && h.zones);
    if (h && h.zones) z.innerHTML = ['A', 'B', 'C'].map(function (k) {
      var A = D(h.zones[k][0]), B = D(h.zones[k][1]);
      var r = A.getUTCMonth() === B.getUTCMonth() ? A.getUTCDate() + ' → ' + B.getUTCDate() + ' ' + L.ms[B.getUTCMonth()] : A.getUTCDate() + ' ' + L.ms[A.getUTCMonth()] + ' → ' + B.getUTCDate() + ' ' + L.ms[B.getUTCMonth()];
      return '<button type="button" class="me-chip me-zone" data-z="' + k + '" aria-pressed="' + (k === st.zone) + '">' + esc(fmt(T.zone_chip, { z: k, r: r })) + '</button>';
    }).join('');
  }
  function renderControls() {
    $('me-from').value = st.from; $('me-to').value = st.to;
    [['me-uc', 'uc', false], ['me-heat', 'heat', true], ['me-budget', 'budget', true], ['me-secu', 'rl', true]].forEach(function (g) {
      var box = $(g[0]); if (!box) return;
      Array.prototype.forEach.call(box.querySelectorAll('.me-chip'), function (b) { var v = g[2] ? Number(b.dataset.v) : b.dataset.v; b.setAttribute('aria-pressed', String(v === st[g[1]])); });
    });
    $('me-heat-row').hidden = st.uc === 'ski' || st.uc === 'rando';
    $('me-fly-val').textContent = st.fly >= 16 ? T.fly_any : (st.fly % 1 === 0 ? fmt(NF.h0, { h: st.fly }) : fmtH(st.fly));
    var allowed = (st.uc === 'ski' || st.uc === 'rando') ? ['score', 'near', 'cheap'] : ['score', 'dry', 'hot', 'near', 'cheap'];
    if (allowed.indexOf(st.sort) < 0) st.sort = 'score';
    $('me-sort').innerHTML = allowed.map(function (k) { return '<option value="' + k + '"' + (k === st.sort ? ' selected' : '') + '>' + esc(L.sorts[k]) + '</option>'; }).join('');
    $('me-reg').value = st.reg; $('me-fly').value = String(st.fly);
    var sel = $('me-dep'), cust = sel.querySelector('option[value="custom"]');
    if (st.dep < 0) { if (!cust) { cust = document.createElement('option'); cust.value = 'custom'; sel.insertBefore(cust, sel.querySelector('option[value="other"]')); } cust.textContent = st.depName; sel.value = 'custom'; }
    else { if (cust) cust.remove(); sel.value = String(st.dep); }
  }
  function seasonLbl(y, cross) { return cross ? y + '-' + String(y + 1).slice(2) : String(y); }
  function dryHtml(x, w) {
    if (x.uc === 'ski') return '<div class="me-approx">' + esc(fmt(T.ski_line, { s: f1(x.sun), tn: t0(x.tmin) })) + '</div>';
    if (x.daily) {
      var sq = x.seasons.map(function (s) { var c = s.rd <= w.limit ? 'd' : (s.rd <= 2 * w.limit ? 'm' : 'w'); return '<span class="me-sq ' + c + '" title="' + esc(fmt(T.season_title, { y: seasonLbl(s.y, w.cross), r: s.rd, p: s.rd > 1 ? 's' : '' })) + '"></span>'; }).join('');
      return '<div' + (x.dry / x.ns < 0.5 ? ' class="me-low"' : '') + '>' + fmt(T.dry_line, { k: x.dry, n: x.ns, x: f1(x.mean), d: w.n }) + '</div><div class="me-seasons">' + sq + '</div>';
    }
    var inner = x.mean < 0.5 ? fmt(T.approx_lt1, { n: w.n }) : fmt(T.approx_n, { x: f1(x.mean), n: w.n });
    return '<div class="me-approx">' + esc(fmt(T.approx_line, { x: inner })) + '</div>';
  }
  function itemHtml(x, i, w) {
    var badges = '<span class="me-badge v' + x.rl + '">' + esc(L.secu[String(x.rl)]) + '</span><span class="me-badge">' + esc(L.budget[String(Math.max(1, Math.min(5, x.d.bi)))]) + '</span>';
    var temp = x.uc === 'ski' ? t0(x.tmin) + ' / ' + t0(x.tmax) + U : t1(x.tmax) + U;
    var sub = (x.sea != null && x.uc !== 'ski' ? fmt(T.sea, { t: t1(x.sea) }) + ' · ' : '') + fmt(T.flight, { h: fmtH(x.h) });
    return '<article class="me-item"><div class="me-rank">' + (i + 1) + '</div>' +
      '<div class="me-name"><a href="' + href(x) + '">' + nm(x) + '</a><span>' + esc(x.d.p[NI]) + ' · ' + fmtKm(x.km) + '</span><div class="me-badges">' + badges + '</div></div>' +
      '<div class="me-metrics"><span class="me-t">' + temp + '</span><span>' + esc(sub) + '</span></div>' +
      '<div class="me-dry">' + dryHtml(x, w) + '</div>' +
      '<div class="me-side"><span class="me-score' + scoreCls(x.score) + '">' + f1(x.score) + '/10</span><a href="' + href(x) + '">' + esc(T.card) + '</a></div></article>';
  }
  function miniRain(x) { return x.uc === 'ski' ? t0(x.tmin) + '/' + t0(x.tmax) + U : fmt(T.mini_rain, { t: t0(x.tmax), r: r0(x.share * 100) }); }
  function miniLi(x, showP) { return '<li><a href="' + href(x) + '">' + nm(x) + '</a>' + (showP ? ' <span class="me-help">(' + esc(x.d.p[NI]) + ')</span>' : '') + '<span>' + esc(miniRain(x)) + ' · <b>' + f1(x.score) + '</b></span></li>'; }
  function renderView(v) {
    var w = v.w;
    if (v.error) {
      $('me-list').innerHTML = '<p class="me-empty">' + esc(T[v.error]) + '</p>';
      ['me-facts', 'me-projects', 'me-regions', 'me-avoid', 'me-legend'].forEach(function (id) { $(id).innerHTML = ''; });
      $('me-count').textContent = ''; $('me-more').hidden = true; return;
    }
    $('me-facts').style.setProperty('--n', Math.max(1, v.facts.length));
    $('me-facts').innerHTML = v.facts.map(function (f) { return '<div class="me-fact' + (f.cls ? ' ' + f.cls : '') + '"><div class="me-k">' + esc(T[f.k]) + '</div><a class="me-v" href="' + href(f.x) + '">' + nm(f.x) + '</a><div class="me-d">' + esc(factText(f, w)) + '</div></div>'; }).join('');
    var reg = st.reg !== 'all' ? ' · ' + L.regions[st.reg] : '';
    $('me-rank-title').textContent = fmt(T.top, { n: Math.min(st.shown, v.rows.length), uc: L.uc_t[st.uc], reg: reg, where: where() });
    $('me-count').textContent = fmt(v.rows.length > 1 ? T.count : T.count1, { k: v.rows.length, n: v.n_uc });
    $('me-list').innerHTML = v.rows.length ? v.rows.slice(0, st.shown).map(function (x, i) { return itemHtml(x, i, w); }).join('') : '<p class="me-empty">' + esc(T.empty) + '</p>';
    $('me-more').hidden = v.rows.length <= st.shown;
    var l = w.limit, mtn = st.uc === 'ski' || st.uc === 'rando';
    $('me-legend').innerHTML = mtn ? '' : '<span><i class="me-sq d"></i>' + esc(fmt(T.lg_dry, { l: l })) + '</span><span><i class="me-sq m"></i>' + esc(fmt(T.lg_mid, { a: l + 1, b: 2 * l })) + '</span><span><i class="me-sq w"></i>' + esc(fmt(T.lg_wet, { b: 2 * l })) + '</span><span>' + esc(w.cross ? T.lg_one_s : T.lg_one_y) + '</span><span>' + esc(T.lg_approx) + '</span>';
    $('me-projects').innerHTML = ['plage', 'ski', 'rando'].map(function (k) {
      var top = v.projects[k];
      return '<div class="me-box"><div class="me-box-head"><h3>' + esc(L.uc[k]) + '</h3><button type="button" class="me-link" data-uc="' + k + '">' + esc(T.see_all) + '</button></div><ul class="me-mini">' + (top.length ? top.map(function (x) { return miniLi(x, false); }).join('') : '<li><span>' + esc(T.none) + '</span></li>') + '</ul></div>';
    }).join('');
    $('me-reg-title').textContent = fmt(T.reg_title, { where: where() });
    $('me-regions').innerHTML = Object.keys(L.regions).filter(function (r) { return v.regions[r]; }).map(function (r) {
      return '<div class="me-box"><div class="me-box-head"><h3>' + esc(L.regions[r]) + '</h3><button type="button" class="me-link" data-reg="' + r + '">' + esc(T.see) + '</button></div><ul class="me-mini">' + v.regions[r].map(function (x) { return miniLi(x, false); }).join('') + '</ul></div>';
    }).join('');
    $('me-avoid-title').textContent = fmt(T.avoid_title, { where: where() });
    $('me-avoid-lead').textContent = fmt(T.avoid_lead, { n: v.n_gen });
    $('me-avoid').innerHTML = v.avoid.map(function (x) { return miniLi(x, true); }).join('');
  }

  // ── cycle de vie ──
  function render() { var w = windowOf(); renderHero(w); renderPresets(); renderControls(); if (DATA) renderView(computeView()); }
  function ensureData() {
    if (DATA) return Promise.resolve(DATA);
    if (!pending) {
      pending = fetch(C.data).then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); }).then(function (d) { DATA = d; return d; });
      fetch('/api/advisories').then(function (r) { return r.ok ? r.json() : null; }).catch(function () { return null; }).then(function (a) { if (a && !a.error) { ADV = a; if (DATA && C.touched) render(); } });
    }
    return pending;
  }
  function fail() { $('me-count').textContent = T.err_load; }
  function act(fn) { return function (e) { C.touched = true; var r = fn(e); if (r === false) return; render(); ensureData().then(render, fail); }; }
  function onChips(id, key, numeric) { var box = $(id); if (!box) return; box.addEventListener('click', act(function (e) { var b = e.target.closest('.me-chip'); if (!b) return false; st[key] = numeric ? Number(b.dataset.v) : b.dataset.v; st.shown = C.page; })); }
  function goList() { var el = $('me-classement'); if (el && el.scrollIntoView) el.scrollIntoView({ behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth', block: 'start' }); }
  function matchDates() {
    var mr = monthRange();
    if (mr[0] === st.from && mr[1] === st.to) { st.preset = 'month'; return; }
    var hs = holidays();
    for (var i = 0; i < hs.length; i++) {
      var h = hs[i];
      if (h.zones) { for (var z in h.zones) if (h.zones[z][0] === st.from && h.zones[z][1] === st.to) { st.preset = h.id; st.zone = z; return; } }
      else if (h.a === st.from && h.b === st.to) { st.preset = h.id; return; }
    }
    st.preset = null;
  }
  onChips('me-uc', 'uc', false); onChips('me-heat', 'heat', true); onChips('me-budget', 'budget', true); onChips('me-secu', 'rl', true);
  $('me-presets').addEventListener('click', act(function (e) {
    var b = e.target.closest('.me-chip'); if (!b) return false;
    if (b.dataset.p === 'month') { st.preset = 'month'; var r = monthRange(); st.from = r[0]; st.to = r[1]; }
    else { var hs = holidays(); for (var i = 0; i < hs.length; i++) if (hs[i].id === b.dataset.p) { st.preset = hs[i].id; var rr = rangeOf(hs[i]); st.from = rr[0]; st.to = rr[1]; } }
    st.shown = C.page;
  }));
  $('me-zone').addEventListener('click', act(function (e) { var b = e.target.closest('.me-chip'); if (!b) return false; st.zone = b.dataset.z; var h = holiday(); if (h) { var r = rangeOf(h); st.from = r[0]; st.to = r[1]; } st.shown = C.page; }));
  $('me-reg').addEventListener('change', act(function (e) { st.reg = e.target.value; st.shown = C.page; }));
  // ville de départ : liste courte + recherche libre (géocodage Open-Meteo, déjà utilisé par l'application)
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
      fetch('https://geocoding-api.open-meteo.com/v1/search?count=6&language=' + LANG.slice(0, 2) + '&name=' + encodeURIComponent(q)).then(function (r) { return r.json(); }).then(function (d) {
        if (id !== cityReq) return;
        var res = (d && d.results) || [];
        box.innerHTML = res.length ? res.map(function (x, i) { var lab = x.name + ' (' + [x.admin1, x.country].filter(Boolean).join(', ') + ')'; return '<button type="button" role="option" data-i="' + i + '">' + esc(lab) + '</button>'; }).join('') : '<p>' + esc(T.city_none) + '</p>';
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
  $('me-fly').addEventListener('input', act(function (e) { st.fly = Number(e.target.value); st.shown = C.page; }));
  $('me-sort').addEventListener('change', act(function (e) { st.sort = e.target.value; }));
  var onDate = act(function () { st.from = $('me-from').value; st.to = $('me-to').value; if (st.from && st.to) { if (st.to < st.from) st.to = st.from; matchDates(); } st.shown = C.page; });
  $('me-from').addEventListener('change', onDate); $('me-to').addEventListener('change', onDate);
  $('me-more').addEventListener('click', act(function () { st.shown += C.page; }));
  $('me-projects').addEventListener('click', function (e) { var b = e.target.closest('[data-uc]'); if (!b) return; C.touched = true; st.uc = b.dataset.uc; st.shown = C.page; render(); ensureData().then(function () { render(); goList(); }, fail); });
  $('me-regions').addEventListener('click', function (e) { var b = e.target.closest('[data-reg]'); if (!b) return; C.touched = true; st.reg = b.dataset.reg; st.uc = 'gen'; st.shown = C.page; render(); ensureData().then(function () { render(); goList(); }, fail); });
  $('me-tool').addEventListener('submit', function (e) { e.preventDefault(); });
  // liens profonds : #noel, #christmas, #semanasanta, #hiver-c…
  function fromHash() {
    var m = (location.hash || '').slice(1).match(/^([a-z]+)(?:-([abc]))?$/), hs = holidays();
    if (!m) return false;
    for (var i = 0; i < hs.length; i++) if (hs[i].id === m[1]) { st.preset = hs[i].id; if (m[2]) st.zone = m[2].toUpperCase(); var r = rangeOf(hs[i]); st.from = r[0]; st.to = r[1]; st.shown = C.page; return true; }
    return false;
  }
  window.addEventListener('hashchange', function () { if (fromHash()) { C.touched = true; render(); ensureData().then(function () { render(); goList(); }, fail); } });
  var fromStore = false;
  try { var sd = JSON.parse(localStorage.getItem('bdw_dep_' + LANG) || 'null'); if (sd) { if (sd.i != null && sd.i !== st.dep && L.deps[sd.i]) { st.dep = sd.i; fromStore = true; } else if (sd.n && typeof sd.la === 'number') { st.dep = -1; st.depName = sd.n; st.depLat = sd.la; st.depLon = sd.lo; fromStore = true; } } } catch (e) {}
  if (fromHash() || fromStore) { C.touched = true; render(); ensureData().then(render, fail); }
  // préchargement discret pour que la première action soit instantanée
  var idle = window.requestIdleCallback || function (f) { return setTimeout(f, 1500); };
  idle(function () { ensureData().catch(function () {}); });
  window.BDW_ENGINE_TEST = { compute: function (s) { st = JSON.parse(JSON.stringify(s)); return ensureData().then(function () { var v = computeView(); return v.error ? v : { rows: v.rows.map(function (x) { return [x.d.s, f1(x.score), x.daily ? x.dry : null]; }), facts: v.facts.map(function (f) { return [f.k, f.x.d.s]; }), avoid: v.avoid.map(function (x) { return x.d.s; }) }; }); } };
})();
