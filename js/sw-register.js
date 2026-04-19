// Registers sw.js (suicide SW) to purge legacy caches on old pages.
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('/sw.js', { scope: '/' }).catch(function(){});
}
