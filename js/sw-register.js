// Unregister any existing service worker and reload if one was active
// (prevents stale cached HTML from being served by an orphaned SW)
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.getRegistrations().then(function(regs) {
    if (regs.length === 0) return;
    Promise.all(regs.map(function(reg) { return reg.unregister(); }))
      .then(function() {
        return (self.caches && caches.keys) ? caches.keys().then(function(keys) {
          return Promise.all(keys.map(function(k) { return caches.delete(k); }));
        }) : null;
      })
      .then(function() {
        // Reload once to fetch the fresh HTML from the network
        if (!sessionStorage.getItem('sw_purged')) {
          sessionStorage.setItem('sw_purged', '1');
          location.reload();
        }
      });
  });
}
