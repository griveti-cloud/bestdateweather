const CACHE = 'bdw-v5';

// Installation légère — pas de précache pour ne pas ralentir le premier chargement
self.addEventListener('install', e => {
  self.skipWaiting();
});

// Activation : supprimer anciens caches
self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

// Fetch : network-first, mise en cache en arrière-plan (stale-while-revalidate)
self.addEventListener('fetch', e => {
  const url = new URL(e.request.url);
  
  // Ne pas intercepter les appels API externes
  if (url.hostname !== self.location.hostname) return;
  
  // Network-first pour tout : réseau d'abord, cache en fallback
  e.respondWith(
    fetch(e.request).then(res => {
      if (res.ok && e.request.method === 'GET') {
        const clone = res.clone();
        caches.open(CACHE).then(c => c.put(e.request, clone));
      }
      return res;
    }).catch(() => caches.match(e.request))
  );
});
