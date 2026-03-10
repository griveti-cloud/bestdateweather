if ('serviceWorker' in navigator) {
  window.addEventListener('load', function() {
    navigator.serviceWorker.register('/sw.js').then(function(reg) {
      // Force check for new SW on every page load
      reg.update();
      // When a new SW takes control, reload the page to get fresh assets
      navigator.serviceWorker.addEventListener('controllerchange', function() {
        window.location.reload();
      });
    }).catch(function(err) {
      console.log('SW erreur:', err);
    });
  });
}
