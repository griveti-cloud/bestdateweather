// v2 — Registers sw.js (suicide SW) to purge legacy caches.
// Old pages still reference sw-register.js (v1) which is kept as a redirect.
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('/sw.js', { scope: '/' }).catch(function(){});
}
