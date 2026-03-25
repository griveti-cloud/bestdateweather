/* BestDateWeather — Destination search autocomplete for monthly pages */
window.initDestSearch = function(cfg) {
  var inp = document.getElementById('dest-search-inp');
  var ac  = document.getElementById('dest-search-ac');
  var btn = document.getElementById('dest-search-btn');
  if (!inp || !ac || !btn) return;

  var monthSuffix = cfg.suffix;
  var basePrefix  = cfg.prefix;
  var assetPrefix = cfg.assetPrefix !== undefined ? cfg.assetPrefix : cfg.prefix;
  var lang        = cfg.lang;
  var _selected   = null;
  var timer       = null;

  function normStr(s) {
    return s.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g,'').replace(/[^a-z0-9]/g,'').trim();
  }

  function doSearch(q) {
    var suggestions = window.BDW_DEST_DATA;
    if (!suggestions) { ac.style.display='none'; return; }
    var qNorm = normStr(q);
    var results = [];
    Object.keys(suggestions).forEach(function(slug) {
      var d = suggestions[slug];
      var name = d[lang] || d.fr || d.en || '';
      if (normStr(name).indexOf(qNorm) === 0) {
        results.push({slug:slug, name:name, flag:d.flag});
      }
    });
    results.sort(function(a,b){ return a.name.localeCompare(b.name); });
    showAC(results.slice(0, 6));
  }

  function showAC(items) {
    ac.innerHTML = '';
    if (!items.length) { ac.style.display='none'; return; }
    items.forEach(function(r) {
      var d = document.createElement('div');
      d.className = 'dest-search-ac-item';
      if (r.flag) {
        var img = document.createElement('img');
        img.src = assetPrefix + 'flags/' + r.flag + '.png';
        img.width = 20; img.height = 15;
        img.style.cssText = 'vertical-align:middle;border-radius:2px;margin-right:6px;flex-shrink:0';
        img.onerror = function() { this.style.display='none'; };
        d.appendChild(img);
      }
      var span = document.createElement('span');
      span.textContent = r.name;
      d.appendChild(span);
      d.onmousedown = function(e) {
        e.preventDefault();
        _selected = r;
        inp.value = r.name;
        ac.style.display = 'none';
      };
      ac.appendChild(d);
    });
    ac.style.display = 'block';
  }

  inp.addEventListener('input', function() {
    clearTimeout(timer);
    _selected = null;
    var q = inp.value.trim();
    if (q.length < 2) { ac.style.display='none'; return; }
    timer = setTimeout(function() { doSearch(q); }, 180);
  });

  btn.addEventListener('click', function() {
    var r = _selected;
    if (!r) return;
    window.location.href = basePrefix + r.slug + monthSuffix;
  });

  inp.addEventListener('keydown', function(e) {
    var items = ac.querySelectorAll('.dest-search-ac-item');
    var idx = -1;
    items.forEach(function(el, i) { if (el.classList.contains('hovered')) idx = i; });
    if (e.key === 'ArrowDown') {
      idx = Math.min(idx+1, items.length-1);
      items.forEach(function(el,i){ el.classList.toggle('hovered', i===idx); });
      e.preventDefault();
    } else if (e.key === 'ArrowUp') {
      idx = Math.max(idx-1, 0);
      items.forEach(function(el,i){ el.classList.toggle('hovered', i===idx); });
      e.preventDefault();
    } else if (e.key === 'Enter') {
      if (idx >= 0 && items[idx]) items[idx].dispatchEvent(new MouseEvent('mousedown'));
      else if (_selected) window.location.href = basePrefix + _selected.slug + monthSuffix;
    } else if (e.key === 'Escape') {
      ac.style.display = 'none';
    }
  });

  document.addEventListener('click', function(e) {
    if (!inp.contains(e.target) && !ac.contains(e.target)) ac.style.display = 'none';
  });
};
