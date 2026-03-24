// BestDate Weather — Service Worker v3
// Stratégie : Cache UNIQUEMENT les assets statiques, JAMAIS les pages HTML

const CACHE_NAME = 'bdw-v3';
const STATIC_ASSETS = [
  '/app.css',
  '/js/core.min.js?v=17',
  '/js/weather-banner-2.min.js?v=5',
  '/js/dest-data.js?v=2',
  '/js/favs.min.js?v=1',
  '/icon-192.png',
  '/icon-512.png',
  '/favicon.ico'
];

self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(STATIC_ASSETS))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys()
      .then(keys => Promise.all(
        keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k))
      ))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', e => {
  const { request } = e;
  const url = new URL(request.url);

  if (request.method !== 'GET' || url.origin !== self.location.origin) return;

  // Pages HTML → TOUJOURS depuis le réseau, jamais depuis le cache
  if (url.pathname.endsWith('.html') || url.pathname === '/' || url.pathname === '') {
    e.respondWith(
      fetch(request).catch(() => caches.match(request))
    );
    return;
  }

  // Assets statiques (JS, CSS, images) → Cache-first
  if (url.pathname.match(/\.(js|css|png|ico|svg|woff2|webp|jpg)(\?|$)/)) {
    e.respondWith(
      caches.match(request).then(cached => cached || fetch(request).then(response => {
        if (response.ok) {
          caches.open(CACHE_NAME).then(cache => cache.put(request, response.clone()));
        }
        return response;
      }))
    );
    return;
  }
});
