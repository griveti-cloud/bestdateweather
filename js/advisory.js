/**
 * advisory.js — Live travel advisory update from /api/advisories
 * Updates .ti-chip[data-advisory-cc] on destination pages.
 * Source: Auswärtiges Amt (Germany), cached 6h server-side.
 */
(function() {
  var LABELS = {
    fr: {1:'Vigilance normale',2:'Vigilance renforcée',3:'Déconseillé',4:'Formellement déconseillé'},
    en: {1:'Normal vigilance',2:'High vigilance',3:'Avoid if possible',4:'Do not travel'},
    'en-us': {1:'Normal vigilance',2:'High vigilance',3:'Avoid if possible',4:'Do not travel'},
    es: {1:'Vigilancia normal',2:'Vigilancia reforzada',3:'Desaconsejado',4:'Formalmente desaconsejado'},
    de: {1:'Normale Wachsamkeit',2:'Erhöhte Wachsamkeit',3:'Nicht empfohlen',4:'Dringend abgeraten'},
  };
  var ICONS = {1:'🟢',2:'🟡',3:'🟠',4:'🔴'};
  var CLASSES = {1:'mae-1',2:'mae-2',3:'mae-3',4:'mae-4'};
  var SOURCE_LABEL = {
    fr:'Auswärtiges Amt (DE) · à vérifier avant de voyager',
    en:'Auswärtiges Amt (DE) · verify before travel',
    'en-us':'Auswärtiges Amt (DE) · verify before travel',
    es:'Auswärtiges Amt (DE) · verificar antes de viajar',
    de:'Auswärtiges Amt · vor Reiseantritt prüfen',
  };

  var chips = document.querySelectorAll('[data-advisory-cc]');
  if (!chips.length) return;

  fetch('/api/advisories')
    .then(function(r){ return r.ok ? r.json() : null; })
    .catch(function(){ return null; })
    .then(function(adv) {
      if (!adv || adv.error) return;
      var lang = (document.documentElement.lang || 'fr').toLowerCase();
      var labels = LABELS[lang] || LABELS.en;
      var srcLabel = SOURCE_LABEL[lang] || SOURCE_LABEL.en;
      var updated = adv._updated || '';

      chips.forEach(function(chip) {
        var cc = (chip.dataset.advisoryCc || '').toUpperCase();
        if (!cc || adv[cc] == null) return;
        var lvl = adv[cc];

        // Update chip class
        chip.className = chip.className.replace(/ti-chip--mae-\d/, 'ti-chip--' + CLASSES[lvl]);

        // Update icon
        var icon = chip.querySelector('.ti-chip-icon');
        if (icon) icon.textContent = ICONS[lvl];

        // Update label
        var val = chip.querySelector('.ti-chip-val');
        if (val) {
          val.textContent = labels[lvl] || '';
          val.className = val.className.replace(/ti-chip-val--mae-\d/, 'ti-chip-val--' + CLASSES[lvl]);
        }

        // Update source note
        var note = chip.closest('.travel-info-widget');
        if (note) {
          var live = note.querySelector('.ti-advisory-live');
          if (live && updated) {
            live.textContent = srcLabel + ' · ' + updated;
            live.style.display = 'inline';
          }
          // Hide static MAE source, show live one
          var detail = note.querySelector('.ti-safety-detail');
          if (detail) {
            var staticNote = detail.querySelector('.ti-safety-note');
            if (staticNote) staticNote.style.display = 'none';
          }
        }
      });
    });
})();
