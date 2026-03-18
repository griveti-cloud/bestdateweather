/* comparatifs-hub.js — injected via JS to bypass static HTML issues */
(function() {
  'use strict';
  
  // Labels par langue
  var LABELS = {
    fr: {title: '⚖️ Comparatifs de destinations', intro: 'Comparaisons météo côte-à-côte pour choisir entre destinations similaires.', badge: 'Comparatif météo'},
    en: {title: '⚖️ Destination comparisons', intro: 'Side-by-side weather comparisons to help you choose between similar destinations.', badge: 'Weather comparison'},
    es: {title: '⚖️ Comparativas de destinos', intro: 'Comparaciones del clima para elegir entre destinos similares.', badge: 'Comparativa del clima'},
    de: {title: '⚖️ Reiseziel-Vergleiche', intro: 'Klimavergleiche für ähnliche Reiseziele.', badge: 'Wetter-Vergleich'}
  };
  
  // Paires de comparatifs
  var PAIRS = [
    ['🌏','Bali','bali','phuket'],['🏝️','Maldives/Seychelles','maldives','seychelles'],
    ['🌊','Mallorca/Sardaigne','mallorca','sardinia'],['⛵','Mykonos/Santorin','mykonos','santorini'],
    ['🌋','Tenerife/Madère','tenerife','madeira'],['☀️','Algarve/Canaries','algarve','canary-islands'],
    ['🐘','Chiang Mai/Bangkok','chiang-mai','bangkok'],['⚓','Dubrovnik/Split','dubrovnik','split'],
    ['🍷','Lisbonne/Porto','lisbon','porto'],['🏛️','Barcelone/Lisbonne','barcelona','lisbon'],
    ['🎵','Ibiza/Majorque','ibiza','mallorca'],['🏖️','Corse/Sardaigne','corsica','sardinia'],
    ['🏙️','Dubaï/Abu Dhabi','dubai','abu-dhabi'],['🌺','Maurice/Réunion','mauritius','reunion'],
    ['🕌','Marrakech/Agadir','marrakech','agadir'],['🌿','Bali/Sri Lanka','bali','sri-lanka'],
    ['🏄','Algarve/Côte d\'Azur','algarve','french-riviera'],['🌊','Canaries/Madère','canary-islands','madeira'],
    ['🐢','Cancún/Riviera Maya','cancun','riviera-maya'],['🏄','Fuerteventura/Gran Canaria','fuerteventura','gran-canaria'],
    ['🎨','Nice/Barcelone','nice','barcelona'],['🏛️','Malte/Sicile','malta','sicily'],
    ['🐠','Maldives/Zanzibar','maldives','zanzibar'],['🕌','Marrakech/Fès','marrakech','fes'],
    ['⛵','Koh Samui/Koh Lanta','koh-samui','koh-lanta'],['🌴','Langkawi/Phuket','langkawi','phuket'],
    ['⛵','Côte d\'Azur/Costa Brava','french-riviera','costa-brava'],['🦋','Costa Rica/Colombie','costa-rica','colombia'],
    ['🎵','Rép. Dom./Jamaïque','dominican-republic','jamaica'],['🌺','Guadeloupe/Martinique','guadeloupe','martinique'],
    ['🌴','Bali/Rép. Dom.','bali','dominican-republic'],['🏛️','Crète/Sardaigne','crete','sardinia'],
    ['🏛️','Sicile/Crète','sicily','crete']
  ];

  function getLink(emoji, label, a, b, lang, base) {
    var href, badge;
    var L = LABELS[lang] || LABELS.en;
    badge = L.badge;
    if (lang === 'fr') href = base + a + '-ou-' + b + '-climat.html';
    else if (lang === 'es') href = base + a + '-vs-' + b + '-clima.html';
    else if (lang === 'de') href = base + a + '-vs-' + b + '-wetter.html';
    else href = base + a + '-vs-' + b + '-weather.html';
    return '<a href="' + href + '" style="background:white;border-radius:12px;padding:14px 16px;text-decoration:none;border:1.5px solid #e8e0d0;display:flex;align-items:center;gap:12px"><span style="font-size:20px">' + emoji + '</span><span><span style="font-size:13px;font-weight:700;color:#1a1f2e;display:block">' + label + '</span><span style="font-size:11px;color:#5a6478">' + badge + '</span></span></a>';
  }

  function inject() {
    // Détecter la langue
    var lang = document.documentElement.lang || 'fr';
    if (lang.startsWith('en-US') || lang.startsWith('en-us')) lang = 'en';
    else if (lang.startsWith('en')) lang = 'en';
    else if (lang.startsWith('es')) lang = 'es';
    else if (lang.startsWith('de')) lang = 'de';
    else lang = 'fr';
    
    // Base URL selon langue
    var base = lang === 'fr' ? '../' : '';
    
    var L = LABELS[lang] || LABELS.en;
    
    var cards = PAIRS.map(function(p) {
      var label = lang === 'fr' ? p[1] : (p[2] + ' vs ' + p[3]).replace(/-/g,' ');
      return getLink(p[0], label, p[2], p[3], lang, base);
    }).join('');
    
    var html = '<div id="silo3-comparatifs" style="max-width:860px;margin:0 auto;padding:32px 16px 0"><div style="padding-top:32px;border-top:1.5px solid #e8e0d0"><div style="display:flex;align-items:center;gap:14px;margin-bottom:18px"><p style="font-size:13px;font-weight:800;letter-spacing:.5px;text-transform:uppercase;color:#1a1f2e;margin:0">' + L.title + '</p><div style="flex:1;height:2px;background:linear-gradient(90deg,#e8940a,#e8e0d0)"></div></div><p style="color:#4a5568;font-size:14px;margin-bottom:24px;line-height:1.7">' + L.intro + '</p><div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:10px">' + cards + '</div></div></div>';
    
    // Trouver le point d'insertion : bouton mois-par-mois ou trust-block
    var insertBefore = document.querySelector('.trust-block') || document.querySelector('.brand-block') || document.querySelector('[class*="trust"]');
    
    if (!insertBefore) {
      // Fallback: après les boutons "où partir"
      var monthBtns = document.querySelectorAll('a[href*="ou-partir-en-"], a[href*="where-to-go-in-"], a[href*="donde-ir-en-"], a[href*="wohin-reisen-"]');
      if (monthBtns.length > 0) {
        insertBefore = monthBtns[monthBtns.length - 1].closest('div[style*="grid"]') || monthBtns[monthBtns.length - 1].parentElement.parentElement.parentElement;
        if (insertBefore && insertBefore.nextSibling) {
          insertBefore.parentNode.insertAdjacentHTML('afterend', html);
          return;
        }
      }
      // Dernier fallback : fin de main
      var main = document.querySelector('main');
      if (main) main.insertAdjacentHTML('beforeend', html);
      return;
    }
    
    insertBefore.insertAdjacentHTML('beforebegin', html);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', inject);
  } else {
    inject();
  }
})();
