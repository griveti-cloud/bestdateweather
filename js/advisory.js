/**
 * advisory.js — Actualisation live du niveau de sécurité.
 *
 * Source : /api/advisories (Worker Cloudflare) qui interroge l'opendata
 * officielle de l'Auswärtiges Amt, cache 6h côté serveur.
 *
 * Cible : l'item "Sécurité" de la box V6 "Pays", porteur de
 * data-advisory-cc="XX" (ISO2). Le HTML statique contient déjà la valeur
 * issue de la MÊME source au build ; ce script la rafraîchit à l'affichage
 * pour que l'info reste à jour entre deux régénérations du site.
 *
 * Les libellés sont identiques à ceux du rendu statique (tier_safe_N) :
 * aucun changement visuel si la valeur n'a pas bougé.
 */
(function () {
  var LABELS = {
    fr:      {1:'Très sûr · 1/5', 2:'Sûr · 2/5', 3:'Modéré · 3/5', 4:'À risque · 4/5'},
    en:      {1:'Very safe · 1/5', 2:'Safe · 2/5', 3:'Moderate · 3/5', 4:'At risk · 4/5'},
    'en-us': {1:'Very safe · 1/5', 2:'Safe · 2/5', 3:'Moderate · 3/5', 4:'At risk · 4/5'},
    es:      {1:'Muy seguro · 1/5', 2:'Seguro · 2/5', 3:'Moderado · 3/5', 4:'Con riesgo · 4/5'},
    de:      {1:'Sehr sicher · 1/5', 2:'Sicher · 2/5', 3:'Mittel · 3/5', 4:'Risikobehaftet · 4/5'}
  };
  var SRC = {
    fr:      'Niveau relevé (Auswärtiges Amt, {d}) · à vérifier avant de voyager',
    en:      'Auswärtiges Amt (DE) · updated {d} · verify before travel',
    'en-us': 'Auswärtiges Amt (DE) · updated {d} · verify before travel',
    es:      'Auswärtiges Amt (DE) · actualizado {d} · verificar antes de viajar',
    de:      'Auswärtiges Amt · Stand {d} · vor Reiseantritt prüfen'
  };

  var items = document.querySelectorAll('[data-advisory-cc]');
  if (!items.length || !window.fetch) return;

  fetch('/api/advisories')
    .then(function (r) { return r.ok ? r.json() : null; })
    .catch(function () { return null; })
    .then(function (adv) {
      if (!adv || adv.error) return;               // échec silencieux : la valeur statique reste
      var lang = (document.documentElement.lang || 'fr').toLowerCase();
      var labels = LABELS[lang] || LABELS.en;
      var srcTpl = SRC[lang] || SRC.en;
      var updated = adv._updated || '';

      items.forEach(function (item) {
        var cc = (item.getAttribute('data-advisory-cc') || '').toUpperCase();
        var lvl = cc ? adv[cc] : null;
        if (!lvl || !labels[lvl]) return;
        var val = item.querySelector('strong');
        if (!val) return;
        // RÈGLE DE SÉCURITÉ : ne jamais ABAISSER le niveau rendu au build.
        // Celui-ci est déjà le max(MAE France, Auswärtiges Amt) ; l'AA est
        // parfois moins prudent que le MAE (Tchad, Bangladesh, Turkménistan).
        // On ne relève donc que si la source live est PLUS alarmante.
        var cur = 0, txt = val.textContent.trim();
        for (var k in labels) { if (labels[k] === txt) { cur = +k; break; } }
        if (cur && lvl <= cur) return;
        val.textContent = labels[lvl];
        var hint = item.querySelector('.signal-hint');
        if (hint) hint.setAttribute('title', srcTpl.replace('{d}', updated));
      });
    });
})();
