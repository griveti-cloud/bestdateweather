// BestDate Weather — Service Worker v2
// Stratégie : Cache-first pour assets statiques, Network-first pour HTML

const CACHE_NAME = 'bdw-v3';
const STATIC_ASSETS = [
  '/',
  '/app.css',
  '/js/core.min.js?v=13',
  '/js/weather-banner-2.min.js?v=3',
  '/js/fiche-slugs.min.js',
  '/icon-192.png',
  '/icon-512.png',
  '/favicon.ico'
];

// Install : précharger les assets critiques
self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(STATIC_ASSETS))
      .then(() => self.skipWaiting())
  );
});

// Activate : purger les anciens caches
self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys()
      .then(keys => Promise.all(
        keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k))
      ))
      .then(() => self.clients.claim())
  );
});

// Fetch : stratégie hybride
self.addEventListener('fetch', e => {
  const { request } = e;
  const url = new URL(request.url);

  // Ignorer requêtes non-GET et cross-origin (open-meteo, GA, etc.)
  if (request.method !== 'GET' || url.origin !== self.location.origin) return;

  // Assets statiques (JS, CSS, images) → Cache-first
  if (
    url.pathname.match(/\.(js|css|png|ico|svg|woff2|webp|jpg)(\?|$)/) ||
    url.pathname.startsWith('/icon')
  ) {
    e.respondWith(
      caches.match(request).then(cached => cached || fetch(request))
    );
    return;
  }

  // Pages HTML → Network-first, fallback cache
  e.respondWith(
    fetch(request)
      .then(response => {
        // Mettre en cache les fiches et pages index
        if (response.ok && (
          url.pathname === '/' ||
          url.pathname.match(/\/(fr|en|es|de|en-us)\//) 
        )) {
          const clone = response.clone();
          caches.open(CACHE_NAME).then(cache => cache.put(request, clone));
        }
        return response;
      })
      .catch(() => caches.match(request))
  );
});
