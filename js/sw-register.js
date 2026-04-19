// Active le SW suicide (sw.js) — écrase tout vieux SW, purge caches, reload.
// Le SW suicide prend le contrôle, désinstalle tout, puis se suicide lui-même.
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('/sw.js', { scope: '/' })
    .then(function(reg) {
      // skipWaiting + activate va déclencher le nettoyage
      if (reg.waiting) reg.waiting.postMessage({ action: 'skipWaiting' });
    })
    .catch(function() { /* ignore */ });
}
