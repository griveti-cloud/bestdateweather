/**
 * dest-map.js — Carte 2 niveaux lazy-loaded pour pages destination
 * Niveau 1 : planisphère complet (non-interactif)
 * Niveau 2 : continental/macro dezoomé (non-interactif)
 * Aucun lien externe — pas de rebond
 */
(function() {
  'use strict';

  function initDestMap(worldId, macroId, lat, lon, macroZoom) {
    if (!window.L) return;
    if (document.getElementById(worldId)._map) return;

    var pin = L.divIcon({
      html: '<div style="width:10px;height:10px;background:#e44;border-radius:50%;border:2px solid white;box-shadow:0 2px 8px rgba(0,0,0,.5)"></div>',
      iconSize: [10,10], iconAnchor: [5,5], className: ''
    });

    // Planisphère
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
    L.marker([lat,lon],{icon:pin,interactive:false}).addTo(mw);
    document.getElementById(worldId)._map = mw;

    // Continental
    var mm = L.map(macroId, {
      zoomControl:false, scrollWheelZoom:false,
      doubleClickZoom:false, dragging:false,
      attributionControl:true
    }).setView([lat, lon], macroZoom);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution:'© <a href="https://openstreetmap.org" tabindex="-1">OSM</a>',
      maxZoom:18
    }).addTo(mm);
    L.marker([lat,lon],{icon:pin,interactive:false}).addTo(mm);
    document.getElementById(macroId)._map = mm;
  }

  function getMacroZoom(lat, lon) {
    // Adapt zoom level based on geographic context
    var absLat = Math.abs(lat);
    // Pacific islands need wider view
    if (lon < -120 || lon > 150) return 3;
    // Polar regions
    if (absLat > 55) return 3;
    // Default continental view
    return 3;
  }

  window.initDestMap = initDestMap;

  // Auto-init via IntersectionObserver (lazy)
  if ('IntersectionObserver' in window) {
    var observed = document.querySelectorAll('[data-dest-map]');
    if (!observed.length) return;

    var loaded = false;
    var observer = new IntersectionObserver(function(entries) {
      entries.forEach(function(e) {
        if (!e.isIntersecting || loaded) return;
        loaded = true;
        observer.disconnect();

        // Load Leaflet CSS + JS then init
        if (!document.querySelector('link[href*="leaflet"]')) {
          var css = document.createElement('link');
          css.rel = 'stylesheet';
          css.href = 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css';
          document.head.appendChild(css);
        }
        if (!window.L) {
          var script = document.createElement('script');
          script.src = 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js';
          script.onload = doInit;
          document.head.appendChild(script);
        } else {
          doInit();
        }
      });
    }, {rootMargin: '200px'});

    observed.forEach(function(el) { observer.observe(el); });

    function doInit() {
      observed.forEach(function(el) {
        var lat   = parseFloat(el.dataset.lat);
        var lon   = parseFloat(el.dataset.lon);
        var mzoom = parseInt(el.dataset.macroZoom) || 3;
        var wId   = el.dataset.worldId;
        var mId   = el.dataset.macroId;
        if (wId && mId) initDestMap(wId, mId, lat, lon, mzoom);
      });
    }
  }
})();
