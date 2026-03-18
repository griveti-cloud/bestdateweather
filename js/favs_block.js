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
}

function bdwUpdateFavBtn(btn, active) {
  if (!btn) return;
  btn.setAttribute('aria-pressed', active ? 'true' : 'false');
  btn.setAttribute('aria-label', active ? 'Retirer des favoris' : 'Ajouter aux favoris');
  btn.style.color = active ? '#d97706' : '';
  btn.style.borderColor = active ? '#d97706' : '';
  var path = btn.querySelector('path');
  if (path) path.setAttribute('fill', active ? 'currentColor' : 'none');
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
