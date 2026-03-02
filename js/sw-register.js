if ('serviceWorker' in navigator) {
 window.addEventListener('load', function() {
 navigator.serviceWorker.register('/sw.js').then(function(reg) {
 console.log('SW enregistré:', reg.scope);
 }).catch(function(err) {
 console.log('SW erreur:', err);
 });
 });
}