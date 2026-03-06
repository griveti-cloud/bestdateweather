const CACHE = 'bdw-v24';

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
    }).catch(() =>
      caches.match(e.request).then(cached => {
        if (cached) return cached;
        // Fallback offline uniquement pour les navigations HTML
        if (e.request.mode === 'navigate') {
          return caches.match('/index.html').then(page => page || new Response(
            '<!doctype html><html lang="fr"><head><meta charset="utf-8"><title>Hors-ligne</title><style>body{font-family:system-ui,sans-serif;display:flex;align-items:center;justify-content:center;min-height:100vh;margin:0;background:#f8fafc}div{text-align:center;padding:2rem}h1{font-size:1.5rem;color:#1e293b;margin-bottom:.5rem}p{color:#64748b;font-size:.95rem}</style></head><body><div><h1>📡 Hors-ligne</h1><p>BestDateWeather nécessite une connexion internet.<br>Reconnectez-vous et rechargez la page.</p></div></body></html>',
            { headers: { 'Content-Type': 'text/html; charset=utf-8' } }
          ));
        }
        return new Response('', { status: 503 });
      })
    )
  );
});
