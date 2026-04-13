"""
Générateur de la nouvelle homepage FR.
Branche: feature/homepage-redesign
Génère: index.html (FR uniquement)
"""
import json, csv, re, os
from datetime import datetime

# ── Données ──────────────────────────────────────────────────────────────────
def load_data():
    mi = datetime.now().month - 1
    months_fr = ['Janvier','Février','Mars','Avril','Mai','Juin','Juillet',
                 'Août','Septembre','Octobre','Novembre','Décembre']
    month_name = months_fr[mi]

    # Scores mensuels pré-calculés
    scores_raw = open('js/fiche-scores.js').read()
    json_str = re.search(r'var FICHE_SCORES = ({.*})', scores_raw, re.DOTALL)
    fiche_scores = json.loads(json_str.group(1))

    # Destinations CSV
    dests = list(csv.DictReader(open('data/destinations.csv')))
    coord_map = {}
    slug_map = {}
    for d in dests:
        try:
            key = f"{round(float(d['lat']),2)},{round(float(d['lon']),2)}"
            coord_map[key] = d
        except: pass
        slug_map[d.get('slug_fr','')] = d

    # Photos Unsplash
    photos = {}
    for p in csv.DictReader(open('data/destination_photos.csv')):
        url = p.get('photo_url','').strip()
        if url:
            photos[p['slug_fr']] = url

    # Climate CSV
    climate = {}
    for row in csv.DictReader(open('data/climate.csv')):
        slug = row.get('slug','')
        m = int(row.get('mois_num',0)) - 1
        if slug and 0 <= m < 12:
            if slug not in climate: climate[slug] = {}
            climate[slug][m] = row

    return mi, month_name, fiche_scores, coord_map, slug_map, photos, climate


def hero_gradient(tmax_str, rain_str, tropical):
    try: t = float(tmax_str)
    except: t = 20
    try: r = float(rain_str)
    except: r = 30
    if tropical in ('True','true','1') and r >= 55:
        return 'linear-gradient(135deg,#14532d 0%,#15803d 35%,#4ade80 75%,#86efac 100%)'
    if t >= 26 and r < 50:
        return 'linear-gradient(135deg,#c2410c 0%,#ea580c 30%,#f59e0b 65%,#fbbf24 100%)'
    if t <= 8:
        return 'linear-gradient(135deg,#0c4a6e 0%,#0369a1 40%,#38bdf8 80%,#7dd3fc 100%)'
    if r >= 60:
        return 'linear-gradient(135deg,#44403c 0%,#78716c 40%,#a8a29e 80%,#d6d3d1 100%)'
    if t >= 18:
        return 'linear-gradient(135deg,#854d0e 0%,#ca8a04 40%,#fbbf24 80%,#fef08a 100%)'
    return 'linear-gradient(135deg,#1e3a5f 0%,#2563eb 40%,#60a5fa 80%,#bae6fd 100%)'


def top_destinations(mi, fiche_scores, coord_map, photos, climate, n=6):
    ranked = []
    for coord, months in fiche_scores.items():
        if len(months) < 12: continue
        score = months[mi]
        if score < 72: continue
        dest = coord_map.get(coord)
        if not dest: continue
        slug = dest.get('slug_fr','')
        if not photos.get(slug): continue
        cl = climate.get(slug, {}).get(mi, {})
        tmax = cl.get('tmax','')
        rain = cl.get('rain_pct','')
        sun  = cl.get('sun_h','')
        trop = dest.get('tropical','False')
        ranked.append({
            'score':   round(score / 10, 1),
            'nom_fr':  dest.get('nom_fr',''),
            'nom_en':  dest.get('nom_en',''),
            'flag':    dest.get('flag',''),
            'slug_fr': slug,
            'photo':   photos[slug],
            'tmax':    tmax,
            'rain':    rain,
            'sun_h':   sun,
            'gradient': hero_gradient(tmax, rain, trop),
        })
    ranked.sort(key=lambda x: -x['score'])
    return ranked[:n]


def score_color(s):
    if s >= 8.6: return '#16a34a'
    if s >= 7.6: return '#22c55e'
    if s >= 6.3: return '#84cc16'
    if s >= 5.0: return '#f59e0b'
    if s >= 3.5: return '#f97316'
    return '#ef4444'


# ── Blocs HTML ────────────────────────────────────────────────────────────────
def dest_card_html(d, pfx=''):
    sc = d['score']
    col = score_color(sc)
    photo_url = d['photo'] + '&w=400&q=80&fm=jpg&fit=crop&crop=entropy' if '?' not in d['photo'] else d['photo']
    sun  = f"☀️ {float(d['sun_h']):.0f}h" if d.get('sun_h') else ''
    rain = f"💧 {d['rain']}%" if d.get('rain') else ''
    stats = ' · '.join(x for x in [sun, rain] if x)
    return f'''<a href="{pfx}meilleure-periode-{d['slug_fr']}.html" class="hd-card">
  <div class="hd-img" style="background-image:url('{photo_url}')">
    <div class="hd-img-overlay"></div>
    <div class="hd-score" style="color:{col}">{sc:.1f}</div>
    <div class="hd-name">{d['nom_fr']}<span class="hd-flag"><img src="{pfx}flags/{d['flag']}.png" width="16" height="12" alt=""></span></div>
  </div>
  {f'<div class="hd-stats">{stats}</div>' if stats else ''}
</a>'''


def ranking_cards_html(pfx=''):
    cards = [
        ('🏆', 'Top mondial', 'Meilleurs scores toutes destinations', f'{pfx}meilleures-destinations-meteo.html'),
        ('🏖️', 'Plage & baignade', 'Mer · soleil · peu de pluie', f'{pfx}classement-destinations-plage-2026.html'),
        ('⛷️', 'Ski & montagne', 'Neige · froid · ciel clair', f'{pfx}classement-destinations-ski-2026.html'),
        ('🌿', 'Tropical', 'Saison sèche · chaleur', f'{pfx}classement-destinations-soleil-2026.html'),
    ]
    html = '<div class="rank-grid">'
    for ico, title, sub, url in cards:
        html += f'''<a href="{url}" class="rank-card">
  <div class="rank-ico">{ico}</div>
  <div class="rank-title">{title}</div>
  <div class="rank-sub">{sub}</div>
  <div class="rank-arrow">Voir →</div>
</a>'''
    html += '</div>'
    return html


# ── Template HTML complet ────────────────────────────────────────────────────
def build_page(top6, month_name, pfx=''):
    cards_html = '\n'.join(dest_card_html(d, pfx) for d in top6)
    ranks_html = ranking_cards_html(pfx)

    return f'''<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>BestDateWeather — Quel temps pour votre voyage ?</title>
<meta name="description" content="Score climatique /10 pour 697 destinations mondiales. Jusqu'à 1 an à l'avance. Basé sur 10 ans de données ERA5.">
<link rel="canonical" href="https://bestdateweather.com/">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,wght@0,700;1,700&family=DM+Sans:wght@400;500;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{pfx}css/weather-banner.css?v=5">
<link rel="preload" href="{pfx}app.css?v=42" as="style" onload="this.onload=null;this.rel='stylesheet'">
<noscript><link rel="stylesheet" href="{pfx}app.css?v=42"></noscript>
<link rel="icon" href="{pfx}favicon.ico">
<meta name="theme-color" content="#0d1117">
{_styles()}
</head>
<body>

<!-- TOPBAR -->
<nav id="bdw-topbar" style="position:fixed;top:0;left:0;right:0;z-index:500;height:52px;background:#0d1117;border-bottom:1px solid rgba(255,255,255,.07);display:flex;align-items:center;justify-content:space-between;padding:0 20px">
  <a href="{pfx}index.html" style="font-family:'Fraunces',serif;font-size:17px;font-weight:700;color:#fff;text-decoration:none">Best<em style="color:#c99438;font-style:italic">Date</em>Weather</a>
  <div style="display:flex;align-items:center;gap:16px">
    <a href="{pfx}meilleures-destinations-meteo.html" class="nav-link">Classements</a>
    <a href="#seo-hub" class="nav-link nav-cta">697 destinations →</a>
    <button id="btn-fav-home" onclick="bdwShowFavorites()" class="topbar-fav" aria-label="Favoris">
      <svg width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/></svg>
    </button>
  </div>
</nav>

<!-- WEATHER BANNER -->
<div id="wb-container" style="min-height:54px;margin-top:52px"></div>

<!-- HERO -->
<section class="hero-section">
  <div class="hero-inner">

    <!-- Colonne gauche -->
    <div class="hero-left">
      <div class="hero-kicker">Météo pour vos projets</div>
      <h1 class="hero-h1">Quel temps<br><em>pour votre voyage ?</em></h1>
      <p class="hero-sub">Le seul site qui score le confort climatique sur 10.<br>697 destinations · jusqu'à 1 an à l'avance · 10 ans ERA5</p>
      <div class="usp-row">
        <span class="usp-pill">Score /10</span>
        <span class="usp-pill">1 an à l'avance</span>
        <span class="usp-pill">697 destinations</span>
        <span class="usp-pill">ERA5 · 10 ans</span>
        <span class="usp-pill">UV · Vagues · AQI</span>
      </div>
      <div class="proj-shortcuts">
        <button class="proj-btn" onclick="quickFill('plage');document.getElementById('inp-city').focus()">🏖️<span>Plage</span></button>
        <button class="proj-btn" onclick="quickFill('ski');document.getElementById('inp-city').focus()">⛷️<span>Ski</span></button>
        <button class="proj-btn" onclick="document.getElementById('inp-city').placeholder='Lieu du mariage…';document.getElementById('inp-city').focus()">💍<span>Mariage</span></button>
        <button class="proj-btn" onclick="document.getElementById('inp-city').focus()">🎪<span>Événement</span></button>
        <button class="proj-btn" onclick="document.getElementById('inp-city').focus()">🏔️<span>Rando</span></button>
      </div>
    </div>

    <!-- Colonne droite : search card -->
    <div class="hero-right">
      <div class="search-card" id="date-form">
        <div class="mode-toggle">
          <button class="mode-btn active" id="mode-date" onclick="switchMode('date')">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
            <span><span class="mode-btn-title">Date</span><span class="mode-btn-sub">Météo ce jour-là</span></span>
          </button>
          <button class="mode-btn" id="mode-annual" onclick="switchMode('annual')">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
            <span><span class="mode-btn-title">Vue 12 mois</span><span class="mode-btn-sub">Meilleur mois</span></span>
          </button>
        </div>

        <!-- Mode date -->
        <div id="date-wrap">
          <div class="field-group">
            <div class="field-wrap inp-wrap inp-wrap-icon">
              <span class="inp-icon">🌍</span>
              <input class="inp" type="text" id="inp-city" placeholder="Paris, Barcelone, Tokyo…" autocomplete="off">
              <button class="inp-clear" id="inp-city-clear" onclick="clearCity()">✕</button>
              <div class="ac-list" id="ac-list"></div>
            </div>
            <div class="field-wrap inp-wrap inp-wrap-icon">
              <span class="inp-icon">📅</span>
              <input class="inp" type="text" id="inp-date" placeholder="Choisir une date" readonly style="cursor:pointer;background:rgba(255,255,255,.07)">
            </div>
          </div>
          <button class="btn-go" id="btn-go">
            <span id="btn-go-text">Voir les conditions ce jour →</span>
          </button>
          <div class="prog-wrap" id="prog-wrap" style="display:none">
            <div class="prog-labels"><span id="prog-lbl">Analyse…</span><span id="prog-pct">0%</span></div>
            <div class="prog-track"><div class="prog-bar" id="prog-bar"></div></div>
          </div>
          <div class="err-box" id="err-box"></div>
        </div>

        <!-- Mode annual -->
        <div id="annual-wrap" style="display:none">
          <div class="annual-city-row">
            <div class="field-wrap inp-wrap inp-wrap-icon" style="flex:1">
              <span class="inp-icon">🌍</span>
              <input class="inp" type="text" id="ann-city" placeholder="Paris, Barcelone, Tokyo…" autocomplete="off">
              <button class="inp-clear" id="ann-city-clear" onclick="clearAnnCity()">✕</button>
              <div class="ac-list" id="ann-ac-list"></div>
            </div>
            <button class="annual-btn" id="ann-btn" onclick="runAnnual()">Voir l'année</button>
          </div>
          <div class="ann-prog-wrap" id="ann-prog-wrap" style="display:none;margin-top:12px">
            <div class="prog-labels"><span id="ann-prog-lbl">Analyse…</span><span id="ann-prog-pct">0%</span></div>
            <div class="prog-track"><div class="prog-bar" id="ann-prog-bar"></div></div>
          </div>
          <div class="err-box" id="ann-err-box"></div>
        </div>

        <!-- Recherches récentes dans la card -->
        <div id="wb-recent-section"></div>
      </div>

      <!-- UC pills sous la card -->
      <div class="uc-filter-wrap" id="uc-filter-wrap" style="display:none">
        <div class="uc-filter-label">Affiner le score pour</div>
        <div class="uc-pills-row">
          <button class="uc-pill uc-pill-neutral active" data-uc="general" onclick="quickFill('general')">🌤️ Juste la météo</button>
          <button class="uc-pill" data-uc="plage" onclick="quickFill('plage')">🏖️ Plage</button>
          <button class="uc-pill" data-uc="ski" onclick="quickFill('ski')">⛷️ Ski</button>
        </div>
      </div>
    </div>
  </div>
</section>

<!-- HERO RESULT (score, chips, etc.) -->
<div class="result-wrap" style="max-width:1160px;margin:0 auto;padding:0 20px">
  <div class="hero" id="hero" style="display:none;max-width:100%"></div>
  <div id="score-block" style="display:none"></div>
  <div id="empty" style="display:none"></div>
  <div id="foot-note" style="display:none"></div>
  <div class="sec-block" id="sec-hourly" style="display:none"></div>
  <div class="sec-block" id="sec-scenarios" style="display:none"></div>
  <div id="annual-result" style="display:none;margin-top:16px">
    <div class="annual-header"><div class="annual-city-name" id="ann-city-name"></div><div class="annual-subtitle" id="annual-subtitle">Profil climatique mensuel · moyenne des 10 dernières années</div><div class="annual-subtitle-uc" id="annual-subtitle-uc" style="display:none"></div></div>
    <div id="ann-narrative" style="display:none"></div>
    <div id="ann-uc-wrap" style="display:none;padding:8px 0"><div class="uc-filter-label">Affiner le score pour</div><div class="uc-pills-row"><button class="uc-pill uc-pill-neutral" data-uc="general" id="ann-uc-general" onclick="quickFill('general')">🌤️ Juste la météo</button><button class="uc-pill" data-uc="plage" onclick="quickFill('plage')">🏖️ Plage</button><button class="uc-pill" data-uc="ski" onclick="quickFill('ski')">⛷️ Ski</button></div></div>
    <div class="months-grid" id="months-grid"></div>
    <div id="ann-fiche-link-wrap"></div>
    <div id="ann-note" style="font-size:11px;color:#888;margin-top:12px;line-height:1.6"></div>
    <div class="ann-prog-wrap" id="ann-prog-wrap2" style="display:none"></div>
  </div>
</div>

<!-- SECTIONS DÉCOUVERTE -->
<div class="discover-wrap">

  <!-- Section "Mieux que vous" — remplie par JS -->
  <div id="wb-suggest-section"></div>
  <div id="wb-ranking-section"></div>

  <!-- Meilleurs scores ce mois -->
  <section class="discover-section">
    <div class="discover-head">
      <div class="discover-title">Meilleurs scores · {month_name}</div>
      <a href="{pfx}meilleures-destinations-meteo.html" class="discover-link">Classement complet →</a>
    </div>
    <div class="hd-grid">
      {cards_html}
    </div>
  </section>

  <!-- Classements par usage -->
  <section class="discover-section">
    <div class="discover-head">
      <div class="discover-title">Classements par usage</div>
      <a href="{pfx}meilleures-destinations-meteo.html" class="discover-link">Tous →</a>
    </div>
    {ranks_html}
  </section>

</div>

<!-- TRUST BAR -->
<div class="trust-bar">
  <div class="trust-item"><div class="trust-n">697</div><div class="trust-l">Destinations</div></div>
  <div class="trust-item"><div class="trust-n">10 ans</div><div class="trust-l">Données ERA5</div></div>
  <div class="trust-item"><div class="trust-n">1 an</div><div class="trust-l">À l'avance</div></div>
  <div class="trust-item"><div class="trust-n">5</div><div class="trust-l">Langues</div></div>
  <div class="trust-item"><div class="trust-n">45 700</div><div class="trust-l">Guides</div></div>
</div>

<!-- SEO HUB (bibliothèque destinations, accordéon) -->
<div style="padding:12px 20px;max-width:1160px;margin:0 auto">
  <button class="seo-hub-toggle" onclick="var h=document.getElementById('seo-hub');var o=h.classList.toggle('open');this.classList.toggle('open')" aria-expanded="false">
    <span>📍 697 guides destinations</span>
    <span class="seo-hub-toggle-icon">⌄</span>
  </button>
</div>
<div id="seo-hub" style="display:none;background:#faf8f3;border-top:1px solid #e8e0d0;padding:40px 20px">
  <!-- HUB-FOOTER-START --><!-- HUB-FOOTER-END -->
</div>

<!-- FOOTER -->
<footer style="background:#080c12;border-top:1px solid rgba(255,255,255,.05);padding:16px 20px;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:10px">
  <div class="footer-langs"><!-- HUB-FOOTER-START --><!-- HUB-FOOTER-END --></div>
  <div style="font-size:10px;color:rgba(255,255,255,.2)">© 2026 BestDateWeather · ERA5 · Open-Meteo · Numbeo</div>
</footer>

<!-- SCRIPTS -->
<script>var BDW_LANG='fr';var BDW_PFXROOT='{pfx}';</script>
<script src="{pfx}js/i18n-fr.min.js?v=11"></script>
<script defer src="{pfx}js/core.min.js?v=55"></script>
<script defer src="{pfx}js/weather-banner-2.min.js?v=9"></script>
<script defer src="{pfx}js/favs.min.js?v=1"></script>
<script defer src="{pfx}js/fiche-slugs.min.js?v=edd3b9"></script>
<script defer src="{pfx}js/dest-search.js?v=7"></script>
<script async src="https://www.googletagmanager.com/gtag/js?id=G-NTCJTDPSJL"></script>
<script defer src="{pfx}js/ga.js?v=11c00f"></script>

</body>
</html>'''


def _styles():
    return '''<style>
:root{--gold:#c99438;--gold2:#e8b84b;--navy:#0d1117;--r:13px}
*{box-sizing:border-box;margin:0;padding:0}
html{scroll-behavior:smooth}
body{font-family:'DM Sans',system-ui,sans-serif;background:#0a0e14;color:#f0ebe0;min-height:100vh;-webkit-font-smoothing:antialiased;padding-top:52px}

/* NAV */
.nav-link{font-size:12px;color:rgba(255,255,255,.45);text-decoration:none;letter-spacing:.3px}
.nav-link:hover{color:#fff}
.nav-cta{background:rgba(201,148,56,.12);color:#e8b84b;padding:5px 12px;border-radius:20px;border:0.5px solid rgba(201,148,56,.3)}
.topbar-fav{background:none;border:1.5px solid rgba(255,255,255,.2);border-radius:50%;width:32px;height:32px;cursor:pointer;color:rgba(255,255,255,.6);display:flex;align-items:center;justify-content:center}
.topbar-fav:hover{color:#fff}

/* HERO */
.hero-section{background:#0d1117;padding:36px 20px 28px}
.hero-inner{max-width:1160px;margin:0 auto;display:grid;grid-template-columns:1fr 440px;gap:48px;align-items:start}
@media(max-width:900px){.hero-inner{grid-template-columns:1fr}}
.hero-kicker{font-size:11px;font-weight:500;color:#c99438;text-transform:uppercase;letter-spacing:1px;margin-bottom:10px}
.hero-h1{font-size:clamp(32px,4vw,52px);font-weight:700;font-family:'Fraunces',Georgia,serif;color:#fff;line-height:1.1;margin-bottom:12px}
.hero-h1 em{color:#c99438;font-style:italic}
.hero-sub{font-size:15px;color:rgba(255,255,255,.45);line-height:1.65;margin-bottom:20px}
.usp-row{display:flex;gap:7px;flex-wrap:wrap;margin-bottom:24px}
.usp-pill{font-size:11px;font-weight:500;padding:4px 11px;border-radius:20px;border:0.5px solid rgba(201,148,56,.3);background:rgba(201,148,56,.08);color:#e8b84b}
.proj-shortcuts{display:flex;gap:8px;flex-wrap:wrap}
.proj-btn{background:#1a1f2e;border:0.5px solid rgba(255,255,255,.08);border-radius:10px;padding:10px 12px;cursor:pointer;display:flex;align-items:center;gap:7px;font-size:13px;font-weight:500;color:rgba(255,255,255,.65);transition:border-color .15s}
.proj-btn:hover{border-color:rgba(201,148,56,.4);color:#fff}
.proj-btn span{font-size:12px}

/* SEARCH CARD */
.search-card{background:#1a1f2e;border-radius:14px;padding:20px;border:0.5px solid rgba(255,255,255,.08)}
.mode-toggle{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:14px}
.mode-btn{padding:11px;border:1.5px solid rgba(255,255,255,.12);border-radius:10px;background:rgba(255,255,255,.06);font-family:'DM Sans',sans-serif;color:rgba(255,255,255,.6);cursor:pointer;display:flex;align-items:center;gap:8px;font-size:13px;transition:background .15s}
.mode-btn.active{background:linear-gradient(135deg,var(--gold),var(--gold2));border-color:var(--gold);color:#fff}
.mode-btn svg{width:15px;height:15px;flex-shrink:0;stroke:currentColor}
.mode-btn-title{font-size:13px;font-weight:700;display:block}
.mode-btn-sub{font-size:10px;display:block;margin-top:1px;opacity:.7}
.field-group{display:grid;grid-template-columns:1fr;gap:10px;margin-bottom:12px}
.field-wrap{position:relative}
.inp-wrap{position:relative}
.inp-wrap-icon .inp{padding-left:42px}
.inp-icon{position:absolute;left:14px;top:50%;transform:translateY(-50%);font-size:16px;pointer-events:none;opacity:.6;z-index:2}
.inp{width:100%;background:rgba(255,255,255,.07);border:1.5px solid rgba(255,255,255,.1);border-radius:10px;color:#fff;font-family:'DM Sans',sans-serif;font-size:14px;padding:12px 36px 12px 14px;outline:none;transition:border-color .15s}
.inp:focus{border-color:var(--gold)}
.inp::placeholder{color:rgba(255,255,255,.35)}
.inp-clear{position:absolute;right:10px;top:50%;transform:translateY(-50%);background:rgba(255,255,255,.15);border:none;border-radius:50%;width:20px;height:20px;cursor:pointer;color:#fff;font-size:13px;display:none;align-items:center;justify-content:center;line-height:1}
.inp-clear.visible{display:flex}
.btn-go{width:100%;background:linear-gradient(135deg,var(--gold),var(--gold2));border:none;border-radius:10px;color:#fff;font-family:'DM Sans',sans-serif;font-weight:700;font-size:15px;padding:14px;cursor:pointer;transition:filter .2s}
.btn-go:hover:not(:disabled){filter:brightness(1.06)}
.btn-go:disabled{opacity:.4;cursor:not-allowed}
.err-box{background:rgba(239,68,68,.1);border:1px solid rgba(239,68,68,.3);border-radius:8px;padding:10px 14px;font-size:13px;color:#fca5a5;margin-top:10px;display:none}
.ac-list{position:absolute;top:calc(100% + 4px);left:0;right:0;background:#1a1f2e;border:0.5px solid rgba(255,255,255,.15);border-radius:10px;z-index:100;display:none;max-height:220px;overflow-y:auto;box-shadow:0 8px 24px rgba(0,0,0,.4)}
.ac-item{padding:11px 14px;cursor:pointer;font-size:13px;color:#f0ebe0;display:flex;justify-content:space-between;border-bottom:0.5px solid rgba(255,255,255,.05)}
.ac-item:hover,.ac-item.sel{background:rgba(201,148,56,.1);color:#fff}
.ac-sub{font-size:11px;color:rgba(255,255,255,.4)}
.prog-wrap{margin-top:12px}
.prog-labels{display:flex;justify-content:space-between;font-size:11px;color:rgba(255,255,255,.4);margin-bottom:5px}
.prog-track{height:3px;background:rgba(255,255,255,.1);border-radius:2px;overflow:hidden}
.prog-bar{height:100%;width:0;background:linear-gradient(90deg,var(--gold),var(--gold2));border-radius:2px;transition:width .3s}

/* UC PILLS */
.uc-filter-wrap{padding:12px 0 4px}
.uc-filter-label{font-size:10px;font-weight:700;letter-spacing:.6px;text-transform:uppercase;color:rgba(255,255,255,.4);margin-bottom:8px}
.uc-pills-row{display:flex;flex-wrap:wrap;gap:6px}
.uc-pill{display:inline-flex;align-items:center;gap:4px;padding:5px 10px;background:rgba(255,255,255,.07);border:1px solid rgba(255,255,255,.12);border-radius:20px;font-size:11px;font-weight:500;color:rgba(255,255,255,.6);cursor:pointer;transition:.15s}
.uc-pill:hover,.uc-pill.active{border-color:var(--gold);background:rgba(201,148,56,.12);color:#e8b84b}

/* ANNUAL */
.annual-city-row{display:flex;gap:8px;align-items:stretch;margin-bottom:0}
.annual-btn{background:linear-gradient(135deg,var(--gold),var(--gold2));border:none;border-radius:10px;color:#fff;font-family:'DM Sans',sans-serif;font-weight:700;font-size:13px;padding:12px 16px;cursor:pointer;white-space:nowrap}
.annual-btn:disabled{opacity:.4}
.annual-header{margin-bottom:14px}
.annual-city-name{font-family:'Fraunces',serif;font-size:22px;font-weight:700;color:#fff}
.annual-subtitle{font-size:12px;color:rgba(255,255,255,.4);margin-top:3px}
.months-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:10px}
@media(max-width:600px){.months-grid{grid-template-columns:repeat(2,1fr)}}

/* HERO RESULT */
.result-wrap{margin:0 auto;padding:0 20px 20px}
.hero{background:#1a1f2e;border-radius:14px;border:0.5px solid rgba(255,255,255,.08);overflow:hidden;margin-bottom:16px;border-top:3px solid var(--gold)}
.sec-block{display:none}
.score-block{padding:20px;background:#1a1f2e;border-bottom:1px solid rgba(255,255,255,.06)}
.score-row{display:flex;align-items:center;gap:20px}
.score-ring-wrap{position:relative;flex-shrink:0;width:72px;height:72px}
.score-ring-wrap svg{transform:rotate(-90deg)}
.score-ring-bg{fill:none;stroke:rgba(255,255,255,.1);stroke-width:6}
.score-ring-fill{fill:none;stroke-width:6;stroke-linecap:round;transition:stroke-dashoffset .8s cubic-bezier(.4,0,.2,1),stroke .4s}
.score-num{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;font-family:'Fraunces',serif;font-size:16px;font-weight:700;color:#fff}
.score-info{flex:1;min-width:0}
.score-usecase{font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.6px;color:rgba(255,255,255,.4);margin-bottom:4px}
.score-verdict{font-size:14px;font-weight:700;color:#fff;margin-bottom:3px;line-height:1.35}
.score-risk{font-size:11px;color:rgba(255,255,255,.5);line-height:1.5}
.score-chips{display:grid;grid-template-columns:1fr 1fr;gap:6px;margin-top:12px;padding:0 20px 16px}
.score-chip{display:flex;align-items:center;gap:6px;padding:7px 10px;background:rgba(255,255,255,.05);border-radius:20px;border:0.5px solid rgba(255,255,255,.08)}
.score-chip-dot{width:7px;height:7px;border-radius:50%;flex-shrink:0}
.score-chip-lbl{font-size:11px;color:rgba(255,255,255,.5);flex:1;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.score-chip-val{font-size:11px;font-weight:700;color:#fff;white-space:nowrap}
.details-toggle{width:100%;display:flex;align-items:center;justify-content:space-between;padding:12px 20px;background:rgba(255,255,255,.04);border:none;border-top:0.5px solid rgba(255,255,255,.06);cursor:pointer;font-family:'DM Sans',sans-serif;font-size:13px;color:rgba(255,255,255,.5)}
.details-toggle-icon{transition:transform .2s}
.details-toggle.open .details-toggle-icon{transform:rotate(180deg)}
.details-panel{display:none}
.details-panel.open{display:block}

/* DISCOVER */
.discover-wrap{max-width:1160px;margin:0 auto;padding:0 20px 40px}
.discover-section{padding:28px 0;border-top:0.5px solid rgba(255,255,255,.07)}
.discover-head{display:flex;justify-content:space-between;align-items:center;margin-bottom:16px}
.discover-title{font-size:12px;font-weight:600;color:rgba(255,255,255,.4);text-transform:uppercase;letter-spacing:.7px}
.discover-link{font-size:12px;color:#c99438;text-decoration:none}
.discover-link:hover{text-decoration:underline}

/* DESTINATION CARDS */
.hd-grid{display:grid;grid-template-columns:repeat(6,1fr);gap:12px}
@media(max-width:900px){.hd-grid{grid-template-columns:repeat(3,1fr)}}
@media(max-width:600px){.hd-grid{grid-template-columns:repeat(2,1fr)}}
.hd-card{border-radius:12px;overflow:hidden;text-decoration:none;display:block;background:#1a1f2e}
.hd-card:hover .hd-img{transform:scale(1.03)}
.hd-img{height:110px;background-size:cover;background-position:center;position:relative;transition:transform .3s;overflow:hidden}
.hd-img-overlay{position:absolute;inset:0;background:linear-gradient(to top,rgba(0,0,0,.65) 0%,rgba(0,0,0,.1) 60%)}
.hd-score{position:absolute;top:7px;right:8px;font-size:13px;font-weight:700;font-family:'Fraunces',serif;background:rgba(0,0,0,.35);padding:2px 6px;border-radius:6px;color:#fff}
.hd-name{position:absolute;bottom:7px;left:8px;font-size:12px;font-weight:600;color:#fff;display:flex;align-items:center;gap:5px;text-shadow:0 1px 4px rgba(0,0,0,.5)}
.hd-flag img{border-radius:2px;vertical-align:middle}
.hd-stats{padding:6px 8px;font-size:10px;color:rgba(255,255,255,.4);background:#131920}

/* RANKINGS */
.rank-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}
@media(max-width:700px){.rank-grid{grid-template-columns:repeat(2,1fr)}}
.rank-card{background:#1a1f2e;border-radius:12px;padding:16px;border:0.5px solid rgba(255,255,255,.07);text-decoration:none;display:block;transition:border-color .15s}
.rank-card:hover{border-color:rgba(201,148,56,.35)}
.rank-ico{font-size:22px;margin-bottom:8px}
.rank-title{font-size:13px;font-weight:600;color:#fff;margin-bottom:4px}
.rank-sub{font-size:11px;color:rgba(255,255,255,.35);line-height:1.4}
.rank-arrow{font-size:11px;color:#c99438;margin-top:10px}

/* TRUST */
.trust-bar{display:flex;justify-content:center;gap:0;background:#080c12;border-top:0.5px solid rgba(255,255,255,.05);border-bottom:0.5px solid rgba(255,255,255,.05)}
.trust-item{flex:1;text-align:center;padding:16px 8px;border-right:0.5px solid rgba(255,255,255,.05)}
.trust-item:last-child{border-right:none}
.trust-n{font-size:18px;font-weight:700;color:#c99438;font-family:'Fraunces',serif}
.trust-l{font-size:9px;color:rgba(255,255,255,.3);text-transform:uppercase;letter-spacing:.5px;margin-top:3px}

/* SEO HUB */
.seo-hub-toggle{display:flex;width:100%;background:rgba(255,255,255,.04);border:0.5px solid rgba(255,255,255,.08);border-radius:10px;padding:10px 16px;font-size:13px;font-weight:600;color:rgba(255,255,255,.4);text-align:left;cursor:pointer;align-items:center;justify-content:space-between;margin:20px 0 0}
.seo-hub-toggle-icon{font-size:18px}
.seo-hub-toggle.open .seo-hub-toggle-icon{transform:rotate(180deg)}
#seo-hub.open{display:block!important}

/* FOOTER LANGS */
.footer-langs{display:flex;gap:14px;flex-wrap:wrap}
.footer-langs a{font-size:12px;color:rgba(255,255,255,.3);text-decoration:none;display:flex;align-items:center;gap:4px}
.footer-langs a:hover{color:#c99438}

/* SCORE INFO tooltip */
.score-info-btn{display:inline-flex;align-items:center;justify-content:center;width:16px;height:16px;border-radius:50%;background:rgba(255,255,255,.12);color:rgba(255,255,255,.5);font-size:10px;cursor:pointer;border:none;margin-left:6px;vertical-align:middle}
.score-tooltip{display:none;position:absolute;background:#1a1f2e;color:#fff;border-radius:10px;padding:12px 14px;font-size:11px;line-height:1.8;z-index:1000;border:0.5px solid rgba(255,255,255,.12);width:220px}
.score-info-wrap{position:relative;display:inline-block}
.score-tooltip.visible{display:block}

/* MONTH CARDS */
.month-card{background:#1a1f2e;border-radius:10px;padding:8px 10px 14px;border:1.5px solid rgba(255,255,255,.08);cursor:default;transition:transform .18s;position:relative;overflow:hidden}
.month-card::before{content:'';position:absolute;top:0;left:0;right:0;height:3px;background:var(--month-color,rgba(255,255,255,.1))}
.month-card:hover{transform:translateY(-2px)}
.mc-top{display:flex;align-items:center;gap:6px;margin-top:10px}
.mc-left{display:flex;flex-direction:column;gap:3px;min-width:38px}
.month-name{font-size:10px;font-weight:600;color:rgba(255,255,255,.5);text-transform:uppercase;letter-spacing:.3px}
.month-score{display:inline-flex;align-items:center;justify-content:center;padding:2px 6px;border-radius:8px;font-size:11px;font-weight:700;color:#fff;font-family:'Fraunces',serif}
.mc-icon{font-size:22px;flex-shrink:0}
.mc-right{flex:1;min-width:0}
.mc-temp{font-size:12px;font-weight:600;color:#fff;white-space:nowrap}
.mc-stats{font-size:10px;color:rgba(255,255,255,.4);margin-top:2px}
.month-bar{height:3px;background:rgba(255,255,255,.08);border-radius:2px;margin-top:8px;overflow:hidden}
.month-bar-fill{height:100%;background:rgba(201,148,56,.5);border-radius:2px}
.month-badge{position:absolute;top:5px;right:5px;font-size:8px;font-weight:700;padding:1px 5px;border-radius:6px;text-transform:uppercase;letter-spacing:.4px}
.month-badge.rec{background:#16a34a;color:#fff}
.month-badge.avoid{background:#ef4444;color:#fff}
.month-best-badge{position:absolute;top:-1px;left:50%;transform:translateX(-50%);font-size:9px;background:var(--gold);color:#fff;padding:1px 6px;border-radius:0 0 6px 6px}
.month-seas-badge{font-size:9px;color:#c99438;text-align:center;margin-top:4px}
.is-rec{border-color:#16a34a!important}
.is-avoid{border-color:#ef4444!important}
.score-num-uc{display:inline-flex;align-items:center;justify-content:center;padding:2px 6px;border-radius:8px;font-size:12px;font-weight:700;color:#fff;font-family:'Fraunces',serif}

/* MISC réutilisés depuis core.js */
.hero-top{background:#1a1f2e;padding:20px;color:#fff;position:relative;overflow:hidden;border-bottom:0.5px solid rgba(255,255,255,.08)}
.hero-loading-bar{height:2px;width:0;background:var(--gold);border-radius:2px;position:absolute;bottom:0;left:0;right:0;transition:width .3s}
.hero-loading-bar.active{width:100%;transition:width 3s}
.hero-horizon-label{font-size:11px;font-weight:700;padding:3px 8px;border-radius:20px;display:inline-block;margin-bottom:8px}
.hl-real{background:rgba(34,197,94,.15);color:#4ade80;border:0.5px solid rgba(34,197,94,.3)}
.hl-tendency{background:rgba(201,148,56,.15);color:#e8b84b;border:0.5px solid rgba(201,148,56,.3)}
.hl-profile{background:rgba(99,153,252,.15);color:#93c5fd;border:0.5px solid rgba(99,153,252,.3)}
.r-temp-wrap{display:flex;align-items:baseline;gap:4px;margin-bottom:4px}
.r-temp{font-size:52px;font-weight:700;font-family:'Fraunces',serif;color:#fff;line-height:1}
.r-temp sup{font-size:22px;vertical-align:super}
.r-cond{font-size:16px;font-weight:500;color:#fff}
.r-range{font-size:12px;color:rgba(255,255,255,.5);margin-top:3px}
.r-tempfreq{font-size:11px;color:rgba(255,255,255,.4);margin-top:3px}
.r-icon{font-size:48px;flex-shrink:0}
.r-icon svg{width:48px;height:48px}
.r-loc{font-size:13px;font-weight:500;color:rgba(255,255,255,.6);margin-bottom:2px}
.r-date{font-size:13px;color:rgba(255,255,255,.4)}
.r-seasinfo{font-size:10px;color:#c99438;margin-top:4px}
.hero-meta{padding:10px 20px;background:#131920;display:flex;gap:16px;flex-wrap:wrap;border-bottom:0.5px solid rgba(255,255,255,.06)}
.hero-meta-item{font-size:12px;color:rgba(255,255,255,.5)}
.hero-meta-val{font-weight:600;color:#fff}
.wb-section{padding:12px 16px}
.wb-section-head{display:flex;justify-content:space-between;align-items:center;margin-bottom:8px}
.wb-section-title{font-size:11px;font-weight:600;color:rgba(255,255,255,.5);text-transform:uppercase;letter-spacing:.5px}
.wb-section-sub{font-size:10px;color:rgba(255,255,255,.3);font-style:italic}
.wb-section-action{background:none;border:none;font-size:11px;color:#c99438;cursor:pointer}
.wb-recent,.wb-suggest{display:flex;align-items:center;justify-content:space-between;padding:8px 0;border-bottom:0.5px solid rgba(255,255,255,.05);cursor:pointer}
.wb-recent:last-child,.wb-suggest:last-child{border-bottom:none}
.wb-recent-left{display:flex;align-items:center;gap:8px}
.wb-recent-flag{font-size:16px;flex-shrink:0}
.wb-recent-info{display:flex;flex-direction:column;gap:1px}
.wb-recent-name{font-size:13px;font-weight:500;color:#fff}
.wb-recent-date{font-size:10px;color:rgba(255,255,255,.35)}
.wb-score{font-size:12px;font-weight:700;font-family:'Fraunces',serif;padding:2px 8px;border-radius:10px}
.wb-suggest-top{display:flex;align-items:center;gap:7px;flex:1}
.wb-suggest-name{font-size:13px;font-weight:500;color:#fff}
.wb-suggest-reason{font-size:10px;color:rgba(255,255,255,.35);font-style:italic}
.h-strip{display:flex;gap:4px;overflow-x:auto;padding:0 20px 12px}
.h-cell{flex-shrink:0;width:54px;text-align:center}
.h-cell-now .h-hr{color:#c99438;font-weight:700}
.h-hr{font-size:10px;color:rgba(255,255,255,.4);display:block;margin-bottom:4px}
.h-ic{font-size:20px;display:block;margin-bottom:2px}
.h-tp{font-size:12px;font-weight:600;color:#fff;display:block}
.h-lb{font-size:9px;color:rgba(255,255,255,.35);display:block;margin-top:1px}
.h-rb{height:3px;background:rgba(255,255,255,.1);border-radius:2px;margin-top:4px;overflow:hidden}
.h-rf{height:100%;background:#6ea8d9;border-radius:2px}
.sec-block{display:none;margin-bottom:0;padding:16px 20px;background:#1a1f2e;border-top:0.5px solid rgba(255,255,255,.06)}
.sec-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:12px}
.sec-title{font-size:13px;font-weight:700;color:#fff}
.sec-hint{font-size:10px;color:rgba(255,255,255,.35)}
.details-toggle{background:#131920;border:none;border-top:0.5px solid rgba(255,255,255,.06)}
.sc-row{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.sc-card{background:rgba(255,255,255,.04);border-radius:10px;padding:12px;border:0.5px solid rgba(255,255,255,.07)}
.sc-head{margin-bottom:10px}
.sc-label{font-size:9px;font-weight:700;padding:2px 7px;border-radius:8px;text-transform:uppercase;letter-spacing:.4px}
.sc-label.pess{background:rgba(99,102,241,.15);color:#a5b4fc}
.sc-label.opt{background:rgba(201,148,56,.15);color:#e8b84b}
.sc-ttl{font-size:13px;font-weight:700;color:#fff;margin-top:5px}
.sc-sub{font-size:11px;color:rgba(255,255,255,.4);margin-top:2px}
.sc-strip{display:flex;gap:3px;margin:10px 0}
.sc-cell{flex:1;text-align:center}
.sc-hr{font-size:9px;color:rgba(255,255,255,.35);display:block;margin-bottom:3px}
.sc-tp{font-size:11px;font-weight:600;color:#fff;display:block;margin-top:3px}
.sc-stats{display:flex;gap:10px;font-size:10px;color:rgba(255,255,255,.4)}
.sc-stat-val{font-size:13px;font-weight:700;color:#fff}
.sc-stat-lbl{font-size:9px;margin-top:1px}
.row-divider{display:flex;align-items:center;gap:10px;padding:10px 20px;border-top:0.5px solid rgba(255,255,255,.06)}
.row-divider-line{flex:1;height:0.5px;background:rgba(255,255,255,.08)}
.row-divider-label{font-size:10px;font-weight:700;color:rgba(255,255,255,.35);text-transform:uppercase;letter-spacing:.6px;white-space:nowrap}
.info-row{display:flex;gap:8px;padding:0 20px 16px;flex-wrap:wrap}
.info-cell{flex:1;min-width:80px;text-align:center;padding:10px 8px;background:rgba(255,255,255,.04);border-radius:8px}
.ic-ico{font-size:18px;margin-bottom:4px}
.ic-val{font-size:13px;font-weight:600;color:#fff}
.ic-sub{font-size:10px;color:rgba(255,255,255,.4);margin-top:2px}
.ic-lbl{font-size:9px;color:rgba(255,255,255,.3);text-transform:uppercase;letter-spacing:.4px;margin-top:6px}
.mb{height:3px;background:rgba(255,255,255,.1);border-radius:2px;margin:5px 0;overflow:hidden}
.mf{height:100%;border-radius:2px}
.bs{background:#e8b84b}.br{background:#f59e0b}.bb{background:#6ea8d9}.bc{background:#22d3ee}.bsk{background:#60a5fa}
.mcard-score{font-family:'Fraunces',serif}
.dec-secu-ok{color:#4ade80}.dec-secu-warn{color:#fbbf24}.dec-secu-alert{color:#f97316}.dec-secu-critical{color:#ef4444}
.dec-budget-1{color:#4ade80}.dec-budget-2{color:#86efac}.dec-budget-3{color:#fbbf24}.dec-budget-4{color:#fb923c}.dec-budget-5{color:#ef4444}
.fiche-link-btn{display:inline-flex;align-items:center;gap:6px;background:rgba(201,148,56,.12);border:1px solid rgba(201,148,56,.3);border-radius:20px;padding:6px 14px;font-size:12px;font-weight:600;color:#e8b84b;text-decoration:none}
.fiche-link-btn:hover{background:rgba(201,148,56,.2)}
#fiche-link-wrap,#ann-fiche-link-wrap{margin:8px 20px}
.date-nav{display:flex;align-items:center;gap:8px;padding:8px 20px;border-bottom:0.5px solid rgba(255,255,255,.06);display:none}
.date-nav-btn{background:rgba(255,255,255,.08);border:none;border-radius:8px;padding:6px 12px;color:#fff;cursor:pointer;font-size:12px}
.date-nav-btn:disabled{opacity:.3}
.date-nav-label{font-size:12px;color:rgba(255,255,255,.4);flex:1;text-align:center}
.forecast-strip{padding:8px 20px;border-bottom:0.5px solid rgba(255,255,255,.06)}
.fs-label{font-size:10px;color:rgba(255,255,255,.35);text-transform:uppercase;letter-spacing:.5px;margin-bottom:8px}
.fs-row{display:flex;gap:6px;overflow-x:auto}
.fs-day{flex-shrink:0;text-align:center;min-width:44px;padding:6px 4px;border-radius:8px;cursor:pointer}
.fs-day.fs-active{background:rgba(201,148,56,.15)}
.fs-day-name{font-size:10px;color:rgba(255,255,255,.4);display:block;margin-bottom:3px}
.fs-day-icon{font-size:16px;display:block}
.fs-day-temp{font-size:12px;font-weight:700;color:#fff;display:block;margin-top:2px}
.fs-day-min{font-size:10px;color:rgba(255,255,255,.4);display:block}
.fs-rain-bar{height:2px;background:rgba(110,168,217,.4);border-radius:1px;display:block;margin-top:3px}
.fs-rain-light{background:rgba(110,168,217,.5)}
.fs-rain-heavy{background:#6ea8d9}
.wb-hidden{display:none}
.reason-cell{flex:1;font-size:12px;line-height:1.5;padding:10px 12px;border-radius:8px;color:rgba(255,255,255,.7)}
.reason-cell.yes{background:rgba(34,197,94,.08);border:0.5px solid rgba(34,197,94,.2)}
.reason-cell.no{background:rgba(239,68,68,.08);border:0.5px solid rgba(239,68,68,.2)}
.reasons-row{display:flex;gap:10px;padding:0 20px 14px}
.verdict-editorial{padding:0 20px 14px;font-size:13px;line-height:1.6;color:rgba(255,255,255,.65)}
.verdict-banner{display:flex;align-items:center;justify-content:space-between;padding:14px 20px;border-bottom:0.5px solid rgba(255,255,255,.06)}
.v-rec{background:rgba(20,122,74,.12)}
.v-mid{background:rgba(234,88,12,.08)}
.v-avoid{background:rgba(239,68,68,.08)}
.verdict-left{display:flex;align-items:center;gap:12px}
.verdict-emoji{font-size:24px}
.verdict-month{font-size:16px;font-weight:700;color:#fff;font-family:'Fraunces',serif}
.verdict-pill{font-size:11px;color:rgba(255,255,255,.5);margin-top:2px}
.verdict-best-ref{font-size:10px;color:rgba(255,255,255,.35);margin-top:4px}
.verdict-score{font-size:36px;font-weight:700;font-family:'Fraunces',serif;color:#fff;line-height:1}
.verdict-score-denom{font-size:14px;font-weight:400;color:rgba(255,255,255,.4)}
.verdict-score-lbl{font-size:9px;color:rgba(255,255,255,.35);text-transform:uppercase;letter-spacing:.5px;margin-top:2px}
.season-strip{display:flex;height:6px;border-radius:3px;overflow:hidden;margin:0 20px 2px}
.ss-rec{flex:1;background:#16a34a}.ss-mid{flex:1;background:#f59e0b}.ss-avoid{flex:1;background:#ef4444}
.month-strip{display:flex;margin:0 20px 10px}
.ms-cell{flex:1;font-size:9px;text-align:center;padding:2px 0;color:rgba(255,255,255,.4)}
.ms-cell.rec{color:#4ade80;font-weight:600}.ms-cell.avoid{color:#fca5a5;font-weight:600}
.best-months{display:flex;align-items:center;gap:6px;flex-wrap:wrap;padding:8px 20px 14px}
.bm-lbl{font-size:10px;color:rgba(255,255,255,.4);text-transform:uppercase;letter-spacing:.5px}
.bm-pill{font-size:11px;font-weight:600;padding:3px 9px;border-radius:20px;background:rgba(34,197,94,.15);color:#4ade80;border:0.5px solid rgba(34,197,94,.3)}
.bm-avoid{background:rgba(239,68,68,.12);color:#fca5a5;border-color:rgba(239,68,68,.3)}
.wb-badge{font-size:9px;background:rgba(201,148,56,.25);border:1px solid rgba(201,148,56,.4);padding:1px 6px;border-radius:8px;font-weight:500;color:#e8b84b;margin-left:4px;text-transform:uppercase;letter-spacing:.3px}
.wb-badge-ip{cursor:pointer;background:rgba(255,255,255,.1);border-color:rgba(255,255,255,.2);color:rgba(255,255,255,.55)}
.source-footer{display:flex;justify-content:space-between;padding:10px 20px;border-top:0.5px solid rgba(255,255,255,.06);flex-wrap:wrap;gap:6px}
.source-tag{font-size:10px;color:rgba(255,255,255,.3);display:flex;align-items:center;gap:5px}
.source-dot{width:3px;height:3px;background:rgba(255,255,255,.2);border-radius:50%;display:inline-block}
.decision-card{border-radius:16px;overflow:hidden;box-shadow:0 4px 32px rgba(0,0,0,.3);margin-bottom:20px}
.ressenti-badge,.rb{font-size:9px;font-weight:700;padding:2px 8px;border-radius:8px;display:inline-block;margin-top:4px;text-transform:uppercase;letter-spacing:.3px}
.rb-green{background:rgba(34,197,94,.15);color:#4ade80}
.rb-blue{background:rgba(14,165,233,.15);color:#7dd3fc}
.rb-orange{background:rgba(249,115,22,.15);color:#fdba74}
.rb-red{background:rgba(239,68,68,.15);color:#fca5a5}
.rb-sky{background:rgba(124,58,237,.15);color:#c4b5fd}
.travel-info-widget,.ti-chip{display:none}
.unit-toggle{display:flex;gap:6px;margin-bottom:10px}
.unit-btn{background:rgba(255,255,255,.07);border:0.5px solid rgba(255,255,255,.12);border-radius:20px;padding:4px 12px;font-size:11px;color:rgba(255,255,255,.5);cursor:pointer;font-family:'DM Sans',sans-serif}
.unit-btn.active{background:linear-gradient(135deg,var(--gold),var(--gold2));border-color:var(--gold);color:#fff}
#uc-filter-wrap{padding:12px 0 4px}
.ann-prog-wrap{margin-top:10px}
.uc-hint{font-size:11px;color:#c99438;font-weight:600;text-align:center;margin-bottom:8px;display:none}
.uc-hint.visible{display:block}
#date-form.uc-required{opacity:.45;pointer-events:none}
#annual-wrap.uc-required-ann .search-card{opacity:.45;pointer-events:none}
@media(max-width:600px){
  .hero-section{padding:20px 16px}
  .discover-wrap{padding:0 16px 32px}
  .trust-bar{flex-wrap:wrap}
  .trust-item{flex:1 0 33%}
  .sc-row{grid-template-columns:1fr}
  .annual-city-row{flex-direction:column}
  .annual-btn{width:100%}
  .nav-link:not(.nav-cta){display:none}
}
.wb-modal-overlay{position:fixed;inset:0;background:rgba(0,0,0,.6);z-index:1000;display:flex;align-items:center;justify-content:center}
.wb-modal{background:#1a1f2e;border-radius:16px;padding:20px;width:90%;max-width:360px;border:0.5px solid rgba(255,255,255,.12)}
.wb-modal-head{display:flex;justify-content:space-between;align-items:center;margin-bottom:14px}
.wb-modal-title{font-size:14px;font-weight:600;color:#fff}
.wb-modal-close{background:none;border:none;color:rgba(255,255,255,.5);font-size:18px;cursor:pointer}
.wb-modal-inp-wrap{display:flex;align-items:center;gap:8px;background:rgba(255,255,255,.08);border-radius:10px;padding:10px 14px;border:0.5px solid rgba(255,255,255,.12);margin-bottom:10px}
.wb-modal-inp{border:none;background:none;flex:1;font-size:14px;color:#fff;font-family:'DM Sans',sans-serif;outline:none}
.wb-modal-geo{width:100%;background:rgba(201,148,56,.12);border:0.5px solid rgba(201,148,56,.3);border-radius:10px;padding:10px;color:#e8b84b;font-size:13px;cursor:pointer;display:flex;align-items:center;justify-content:center;gap:8px;font-family:'DM Sans',sans-serif;margin-bottom:10px}
.wb-modal-results{max-height:180px;overflow-y:auto}
.wb-modal-result{width:100%;background:none;border:none;border-bottom:0.5px solid rgba(255,255,255,.06);padding:10px 4px;text-align:left;cursor:pointer;color:#fff;font-size:13px;display:flex;flex-direction:column;gap:2px;font-family:'DM Sans',sans-serif}
.wb-modal-result:hover{background:rgba(255,255,255,.05)}
.wb-modal-result-sub{font-size:11px;color:rgba(255,255,255,.4)}
.wb-modal-current{font-size:11px;color:rgba(255,255,255,.35);margin-top:8px;text-align:center}
</style>'''


# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    print('🏗  Génération homepage FR...')
    mi, month_name, fiche_scores, coord_map, slug_map, photos, climate = load_data()
    print(f'   Mois courant : {month_name} (index {mi})')

    top6 = top_destinations(mi, fiche_scores, coord_map, photos, climate)
    print(f'   Top {len(top6)} destinations :')
    for d in top6:
        print(f'     {d["score"]:.1f} {d["nom_fr"]}')

    html = build_page(top6, month_name, pfx='')
    open('index.html', 'w', encoding='utf-8').write(html)
    print(f'✅ index.html généré ({len(html)//1024} Ko)')
