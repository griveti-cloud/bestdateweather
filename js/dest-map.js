/**
 * dest-map.js v2 — Carte 2 niveaux lazy-loaded
 * Fix: invalidateSize() après rendu pour les cartes initialisées hors viewport
 */
(function() {
  'use strict';

  function initDestMap(worldId, macroId, lat, lon, macroZoom) {
    if (!window.L) return;
    var welEl = document.getElementById(worldId);
    var meEl  = document.getElementById(macroId);
    if (!welEl || !meEl || welEl._map) return;

    var pin = L.divIcon({
      html: '<div style="width:10px;height:10px;background:#e44;border-radius:50%;border:2px solid white;box-shadow:0 2px 8px rgba(0,0,0,.5)"></div>',
      iconSize:[10,10], iconAnchor:[5,5], className:''
    });

    // ── Niveau 1 : planisphère ──
    var mw = L.map(worldId, {
      zoomControl:false, scrollWheelZoom:false,
      doubleClickZoom:false, dragging:false,
      attributionControl:false, worldCopyJump:false
    }).setView([lat, lon], 1);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {maxZoom:18}).addTo(mw);
    var delta = 18;
    L.rectangle(
      [[lat-delta, lon-delta*1.8],[lat+delta, lon+delta*1.8]],
      {color:'#e44',weight:1.5,fillColor:'#e44',fillOpacity:.1,interactive:false}
    ).addTo(mw);
    L.marker([lat,lon], {icon:pin, interactive:false}).addTo(mw);
    welEl._map = mw;

    // ── Niveau 2 : continental ──
    var mm = L.map(macroId, {
      zoomControl:false, scrollWheelZoom:false,
      doubleClickZoom:false, dragging:false,
      attributionControl:true
    }).setView([lat, lon], macroZoom);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution:'© <a href="https://openstreetmap.org" rel="noopener" tabindex="-1">OSM</a>',
      maxZoom:18
    }).addTo(mm);
    L.marker([lat,lon], {icon:pin, interactive:false}).addTo(mm);
    meEl._map = mm;

    // Critical: invalidateSize after a tick so Leaflet recalculates
    // container dimensions (fixes grey tiles when init'd off-screen)
    setTimeout(function() {
      mw.invalidateSize();
      mm.invalidateSize();
    }, 100);
  }

  window.initDestMap = initDestMap;

  function loadLeafletAndInit(callback) {
    if (window.L) { callback(); return; }
    // CSS
    if (!document.querySelector('link[href*="leaflet"]')) {
      var css = document.createElement('link');
      css.rel = 'stylesheet';
      css.href = 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css';
      document.head.appendChild(css);
    }
    // JS
    var s = document.createElement('script');
    s.src = 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js';
    s.onload = callback;
    document.head.appendChild(s);
  }

  function doInitAll() {
    document.querySelectorAll('[data-dest-map]').forEach(function(el) {
      var lat  = parseFloat(el.dataset.lat);
      var lon  = parseFloat(el.dataset.lon);
      var mz   = parseInt(el.dataset.macroZoom) || 3;
      var wId  = el.dataset.worldId;
      var mId  = el.dataset.macroId;
      if (wId && mId) initDestMap(wId, mId, lat, lon, mz);
    });
  }

  if (!('IntersectionObserver' in window)) {
    // Fallback: load on DOMContentLoaded
    document.addEventListener('DOMContentLoaded', function() {
      loadLeafletAndInit(doInitAll);
    });
    return;
  }

  var observed = document.querySelectorAll('[data-dest-map]');
  if (!observed.length) return;

  var triggered = false;
  var observer = new IntersectionObserver(function(entries) {
    var visible = entries.some(function(e) { return e.isIntersecting; });
    if (!visible || triggered) return;
    triggered = true;
    observer.disconnect();
    loadLeafletAndInit(doInitAll);
  }, {rootMargin:'300px'});  // preload 300px before visible

  observed.forEach(function(el) { observer.observe(el); });
})();
