// ─── FAVORIS localStorage ────────────────────────────────────────────────────
var BDW_FAV_KEY = 'bdw_favorites';

function bdwLoadFavs() {
  try { return JSON.parse(localStorage.getItem(BDW_FAV_KEY) || '{}'); }
  catch(e) { return {}; }
}
function bdwSaveFavs(favs) {
  try { localStorage.setItem(BDW_FAV_KEY, JSON.stringify(favs)); } catch(e) {}
}

function bdwToggleFav(btn) {
  var slug = btn.getAttribute('data-slug');
  if (!slug) return;
  var favs = bdwLoadFavs();
  var active;
  if (favs[slug]) {
    delete favs[slug];
    active = false;
  } else {
    var nameEl = document.querySelector('h1.hero-title em');
    var flagEl = document.querySelector('.dest-tag img');
    favs[slug] = { name: nameEl ? nameEl.textContent.trim() : slug, flag: flagEl ? flagEl.src : '', ts: Date.now() };
    active = true;
  }
  bdwSaveFavs(favs);
  bdwUpdateFavBtn(btn, active);
  btn.style.transform = 'scale(1.3)';
  setTimeout(function() { btn.style.transform = ''; }, 200);
  // Proposer l'email uniquement au moment de l'ajout
  if (active && typeof window.bdwShowEmailPopup === 'function') {
    var nameEl = document.querySelector('h1.hero-title em');
    var destName = nameEl ? nameEl.textContent.trim() : null;
    setTimeout(function() { window.bdwShowEmailPopup(destName); }, 600);
  }
}

function bdwUpdateFavBtn(btn, active) {
  if (!btn) return;
  btn.setAttribute('aria-pressed', active ? 'true' : 'false');
  btn.setAttribute('aria-label', active ? 'Retirer des favoris' : 'Ajouter aux favoris');
  btn.style.color = active ? '#d97706' : '';
  btn.style.borderColor = active ? '#d97706' : '';
  var svg = btn.querySelector('svg');
  var path = btn.querySelector('path');
  if (svg) {
    svg.setAttribute('stroke', active ? '#d97706' : 'currentColor');
  }
  if (path) {
    path.setAttribute('fill', active ? '#d97706' : 'none');
    path.setAttribute('stroke', active ? '#d97706' : 'currentColor');
  }
}

function bdwInitFavBtn() {
  var btn = document.getElementById('btn-fav');
  if (!btn) return;
  var slug = btn.getAttribute('data-slug');
  if (!slug) return;
  bdwUpdateFavBtn(btn, !!bdwLoadFavs()[slug]);
}

function bdwCloseFavsPanel() {
  var p = document.getElementById('bdw-favs-panel');
  if (p) p.remove();
  window.location.hash = '';
}

function bdwClearFavs() {
  if (!confirm('Effacer tous les favoris ?')) return;
  localStorage.removeItem(BDW_FAV_KEY);
  bdwCloseFavsPanel();
}

function bdwShowFavorites() {
  var favs = bdwLoadFavs();
  var keys = Object.keys(favs).sort(function(a,b) { return (favs[b].ts||0)-(favs[a].ts||0); });
  var existing = document.getElementById('bdw-favs-panel');
  if (existing) existing.remove();
  var panel = document.createElement('div');
  panel.id = 'bdw-favs-panel';
  panel.style.cssText = 'position:fixed;inset:0;background:rgba(26,31,46,.95);z-index:9999;overflow-y:auto;padding:20px 16px;color:#fff;font-family:DM Sans,sans-serif';
  var inner = document.createElement('div');
  inner.style.cssText = 'max-width:480px;margin:0 auto';
  var header = document.createElement('div');
  header.style.cssText = 'display:flex;align-items:center;gap:12px;margin-bottom:24px';
  var backBtn = document.createElement('button');
  backBtn.textContent = '←';
  backBtn.style.cssText = 'background:none;border:none;color:#fff;font-size:24px;cursor:pointer';
  backBtn.onclick = bdwCloseFavsPanel;
  var title = document.createElement('h2');
  title.style.cssText = 'margin:0;font-size:20px;font-weight:700';
  title.textContent = 'Mes destinations favorites';
  header.appendChild(backBtn);
  header.appendChild(title);
  inner.appendChild(header);
  if (keys.length === 0) {
    var empty = document.createElement('p');
    empty.style.cssText = 'color:#94a3b8;text-align:center;margin-top:40px';
    empty.innerHTML = 'Aucun favori.<br>Appuyez sur ♡ sur une fiche destination.';
    inner.appendChild(empty);
  } else {
    keys.forEach(function(slug) {
      var f = favs[slug];
      var a = document.createElement('a');
      a.href = 'meilleure-periode-' + slug + '.html';
      a.style.cssText = 'display:flex;align-items:center;gap:14px;background:#1e2a3a;border-radius:12px;padding:14px 16px;margin-bottom:10px;text-decoration:none;color:#fff';
      if (f.flag) {
        var img = document.createElement('img');
        img.src = f.flag; img.width = 24; img.height = 18;
        img.style.cssText = 'border-radius:3px;flex-shrink:0';
        a.appendChild(img);
      }
      var span = document.createElement('span');
      span.style.cssText = 'flex:1;font-weight:600';
      span.textContent = f.name || slug;
      a.appendChild(span);
      inner.appendChild(a);
    });
    var clearBtn = document.createElement('button');
    clearBtn.textContent = 'Effacer tous les favoris';
    clearBtn.style.cssText = 'width:100%;margin-top:16px;padding:12px;background:none;border:1.5px solid #475569;border-radius:10px;color:#94a3b8;cursor:pointer;font-size:14px';
    clearBtn.onclick = bdwClearFavs;
    inner.appendChild(clearBtn);
  }
  panel.appendChild(inner);
  document.body.appendChild(panel);
}

function bdwCheckHash() {
  if (window.location.hash === '#favoris') bdwShowFavorites();
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', function() { bdwInitFavBtn(); bdwCheckHash(); });
} else {
  bdwInitFavBtn();
  bdwCheckHash();
}
window.addEventListener('hashchange', bdwCheckHash);


// Exposer sur window pour les onclick HTML
window.bdwToggleFav = bdwToggleFav;
window.bdwShowFavorites = bdwShowFavorites;
window.bdwCloseFavsPanel = bdwCloseFavsPanel;
window.bdwClearFavs = bdwClearFavs;

// ─── CAPTURE EMAIL ────────────────────────────────────────────────────────────
(function() {
  var ASKED_KEY = 'bdw_email_asked';

  function alreadyAsked() {
    try {
      var v = localStorage.getItem(ASKED_KEY);
      if (!v) return false;
      // Réafficher après 30 jours
      return (Date.now() - parseInt(v)) < 30 * 24 * 3600 * 1000;
    } catch(e) { return false; }
  }

  function markAsked() {
    try { localStorage.setItem(ASKED_KEY, String(Date.now())); } catch(e) {}
  }

  function showEmailPopup(destName) {
    if (alreadyAsked()) return;
    markAsked();

    var overlay = document.createElement('div');
    overlay.id = 'bdw-email-overlay';
    overlay.style.cssText = 'position:fixed;inset:0;background:rgba(26,31,46,.6);z-index:10000;display:flex;align-items:flex-end;justify-content:center;padding:0 0 20px';

    var panel = document.createElement('div');
    panel.style.cssText = 'background:white;border-radius:16px;padding:24px 20px;max-width:420px;width:calc(100% - 32px);box-shadow:0 -4px 32px rgba(0,0,0,.15);font-family:DM Sans,sans-serif';

    var msg = destName
      ? 'Recevoir les meilleures périodes pour <strong>' + destName + '</strong> et vos autres destinations chaque mois.'
      : 'Recevoir les 5 meilleures destinations chaque mois.';

    panel.innerHTML =
      '<div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:12px">' +
        '<p style="margin:0;font-size:15px;font-weight:600;color:#1a1f2e;line-height:1.4">' +
          '📩 ' + msg +
        '</p>' +
        '<button id="bdw-email-close" style="background:none;border:none;font-size:20px;cursor:pointer;color:#94a3b8;padding:0 0 0 8px;flex-shrink:0">✕</button>' +
      '</div>' +
      '<div style="display:flex;gap:8px;margin-top:8px">' +
        '<input id="bdw-email-input" type="email" placeholder="votre@email.com" ' +
          'style="flex:1;padding:10px 12px;border:1.5px solid #e8e0d0;border-radius:8px;font-size:14px;outline:none;font-family:DM Sans,sans-serif">' +
        '<button id="bdw-email-submit" ' +
          'style="background:#d97706;color:white;border:none;border-radius:8px;padding:10px 16px;font-size:14px;font-weight:700;cursor:pointer;white-space:nowrap;font-family:DM Sans,sans-serif">' +
          'Recevoir' +
        '</button>' +
      '</div>' +
      '<p id="bdw-email-msg" style="margin:8px 0 0;font-size:12px;color:#64748b;min-height:16px"></p>' +
      '<p style="margin:8px 0 0;font-size:11px;color:#94a3b8">Pas de spam. Désabonnement en 1 clic. <a href="/confidentialite.html" style="color:#94a3b8;text-decoration:underline" target="_blank">Confidentialité</a></p>';

    overlay.appendChild(panel);
    document.body.appendChild(overlay);

    // Fermer
    document.getElementById('bdw-email-close').onclick = function() {
      overlay.remove();
    };
    overlay.onclick = function(e) {
      if (e.target === overlay) overlay.remove();
    };

    // Soumettre
    document.getElementById('bdw-email-submit').onclick = function() {
      submitEmail();
    };
    document.getElementById('bdw-email-input').addEventListener('keydown', function(e) {
      if (e.key === 'Enter') submitEmail();
    });

    function submitEmail() {
      var emailVal = document.getElementById('bdw-email-input').value.trim();
      var msgEl = document.getElementById('bdw-email-msg');
      var btn = document.getElementById('bdw-email-submit');
      if (!emailVal || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(emailVal)) {
        msgEl.style.color = '#ef4444';
        msgEl.textContent = 'Email invalide.';
        return;
      }
      btn.disabled = true;
      btn.textContent = '...';
      fetch('/subscribe', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: emailVal, source: 'favori' })
      })
      .then(function(r) { return r.json(); })
      .then(function(data) {
        if (data.success) {
          msgEl.style.color = '#16a34a';
          msgEl.textContent = '✓ Vous êtes inscrit !';
          btn.style.display = 'none';
          setTimeout(function() { overlay.remove(); }, 2000);
        } else {
          msgEl.style.color = '#ef4444';
          msgEl.textContent = 'Une erreur est survenue, réessayez.';
          btn.disabled = false;
          btn.textContent = 'Recevoir';
        }
      })
      .catch(function() {
        msgEl.style.color = '#ef4444';
        msgEl.textContent = 'Erreur réseau, réessayez.';
        btn.disabled = false;
        btn.textContent = 'Recevoir';
      });
    }
  }

  // Exposer pour bdwToggleFav
  window.bdwShowEmailPopup = showEmailPopup;
})();

// ─── CTA INSTALL PWA ──────────────────────────────────────────────────────────
(function() {
  var INSTALL_KEY = 'bdw_install_dismissed';
  var deferredPrompt = null;

  // Capturer l'événement natif Chrome (Android)
  window.addEventListener('beforeinstallprompt', function(e) {
    e.preventDefault();
    deferredPrompt = e;
    setTimeout(showInstallBanner, 30000); // après 30s
  });

  function alreadyDismissed() {
    try { return !!localStorage.getItem(INSTALL_KEY); } catch(e) { return true; }
  }

  function showInstallBanner() {
    if (alreadyDismissed()) return;
    if (document.getElementById('bdw-install-banner')) return;

    var banner = document.createElement('div');
    banner.id = 'bdw-install-banner';
    banner.style.cssText = 'position:fixed;bottom:0;left:0;right:0;z-index:9998;'
      + 'background:white;border-top:2px solid #e8e0d0;padding:14px 16px;'
      + 'display:flex;align-items:center;gap:12px;box-shadow:0 -4px 16px rgba(0,0,0,.1);'
      + 'font-family:DM Sans,sans-serif';

    banner.innerHTML =
      '<svg viewBox="0 0 24 24" width="28" height="28" fill="none" stroke="#d97706" stroke-width="2" flex-shrink:0" style="flex-shrink:0">'
      + '<path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z" fill="#d97706"/>'
      + '</svg>'
      + '<div style="flex:1">'
      + '<p style="margin:0;font-size:14px;font-weight:700;color:#1a1f2e">Installer BestDate</p>'
      + '<p style="margin:2px 0 0;font-size:12px;color:#64748b">Accès rapide depuis votre écran d\'accueil</p>'
      + '</div>'
      + '<button id="bdw-install-btn" style="background:#d97706;color:white;border:none;border-radius:8px;padding:9px 16px;font-size:13px;font-weight:700;cursor:pointer;white-space:nowrap;font-family:DM Sans,sans-serif">Installer</button>'
      + '<button id="bdw-install-close" style="background:none;border:none;font-size:20px;cursor:pointer;color:#94a3b8;padding:0 4px">✕</button>';

    document.body.appendChild(banner);

    document.getElementById('bdw-install-btn').onclick = function() {
      if (deferredPrompt) {
        deferredPrompt.prompt();
        deferredPrompt.userChoice.then(function(result) {
          if (result.outcome === 'accepted') {
            dismiss();
          }
          deferredPrompt = null;
        });
      } else {
        // Fallback : instructions manuelles
        alert('Sur Chrome : menu ⋮ → "Ajouter à l\'écran d\'accueil"');
        dismiss();
      }
    };

    document.getElementById('bdw-install-close').onclick = dismiss;

    function dismiss() {
      try { localStorage.setItem(INSTALL_KEY, '1'); } catch(e) {}
      var b = document.getElementById('bdw-install-banner');
      if (b) b.remove();
    }
  }

  // Sur iOS (pas de beforeinstallprompt), afficher quand même après 30s
  var isIOS = /iphone|ipad|ipod/i.test(navigator.userAgent);
  var isStandalone = window.navigator.standalone;
  if (isIOS && !isStandalone) {
    setTimeout(showInstallBanner, 30000);
  }
})();
