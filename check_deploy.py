#!/usr/bin/env python3
"""
check_deploy.py — Vérification post-déploiement de cohérence cross-surfaces.

Lance après chaque modification de scoring, emoji ou logique d'affichage.
Usage : python3 check_deploy.py
"""
import csv, json, re, sys, os, importlib
sys.path.insert(0, os.path.dirname(__file__))

ERRORS = []
WARNINGS = []

def err(msg):  ERRORS.append(f"❌ {msg}")
def warn(msg): WARNINGS.append(f"⚠️  {msg}")
def ok(msg):   print(f"  ✅ {msg}")

# ── Helpers ──────────────────────────────────────────────────────────────────

def get_score_in_page(filepath, slug=None):
    """Extrait le premier score /10 d'une page HTML."""
    try:
        content = open(filepath, encoding='utf-8').read()
        m = re.search(r'(\d\.\d)/10', content)
        return float(m.group(1)) if m else None
    except FileNotFoundError:
        return None

def get_emoji_in_table(filepath):
    """Extrait les emojis de la première colonne du tableau climatique."""
    try:
        content = open(filepath, encoding='utf-8').read()
        rows = re.findall(r'<tr class="[^"]+"[^>]*><td>([^<]+)</td>', content)
        return [r.split()[0] for r in rows[:12] if r]
    except FileNotFoundError:
        return []

def get_csv_score(climate_rows, slug, mois):
    for r in climate_rows:
        if r['slug'] == slug and r['mois'] == mois:
            return float(r['score'])
    return None

# ── Charger les données de référence ────────────────────────────────────────

print("\n=== check_deploy.py — Vérification cohérence cross-surfaces ===\n")

climate = list(csv.DictReader(open('data/climate.csv', encoding='utf-8-sig')))
dests   = list(csv.DictReader(open('data/destinations.csv', encoding='utf-8-sig')))

# ── 1. SCORING : cohérence CSV → pages statiques ────────────────────────────
print("1. Scoring CSV → pages statiques")

test_cases = [
    ('tokyo',    'Juillet', 'tokyo-meteo-juillet.html',       'en/tokyo-weather-july.html'),
    ('bangkok',  'Juillet', 'bangkok-meteo-juillet.html',     'en/bangkok-weather-july.html'),
    ('paris',    'Juillet', 'paris-meteo-juillet.html',       'en/paris-weather-july.html'),
    ('dubai',    'Juillet', 'dubai-meteo-juillet.html',       'en/dubai-weather-july.html'),
    ('guyane',   'Juin',    'guyane-meteo-juin.html',         'en/french-guiana-weather-june.html'),
]

for slug, mois, fr_page, en_page in test_cases:
    csv_score = get_csv_score(climate, slug, mois)
    if csv_score is None:
        warn(f"{slug}/{mois}: absent de climate.csv")
        continue
    # FR page
    fr_score = get_score_in_page(fr_page)
    if fr_score is None:
        warn(f"{fr_page}: introuvable ou pas de score")
    elif abs(fr_score - csv_score) > 0.05:
        err(f"{slug}/{mois}: CSV={csv_score} ≠ FR page={fr_score}")
    else:
        ok(f"{slug}/{mois}: CSV={csv_score} == FR={fr_score}")
    # EN page
    en_score = get_score_in_page(en_page)
    if en_score and abs(en_score - csv_score) > 0.05:
        err(f"{slug}/{mois}: CSV={csv_score} ≠ EN page={en_score}")

# ── 2. SCORING : 5 langues cohérentes entre elles ───────────────────────────
print("\n2. Cohérence scores entre langues")

lang_files = {
    'FR': 'tokyo-meteo-juillet.html',
    'EN': 'en/tokyo-weather-july.html',
    'ES': 'es/tokio-clima-julio.html',
    'DE': 'de/tokyo-wetter-juli.html',
    'US': 'us/tokyo-weather-july.html',
}
scores_by_lang = {}
for lang, f in lang_files.items():
    s = get_score_in_page(f)
    if s: scores_by_lang[lang] = s

if len(set(scores_by_lang.values())) == 1:
    ok(f"Tokyo juillet: {list(scores_by_lang.values())[0]} identique sur {list(scores_by_lang.keys())}")
elif scores_by_lang:
    err(f"Tokyo juillet scores divergent : {scores_by_lang}")

# ── 3. EMOJIS : cohérence Python (static) vs logique attendue ────────────────
print("\n3. Emojis — pages statiques")

from lib.common import weather_emoji, _classify_rain_pattern

emoji_cases = [
    # Guyane : climat convectif. Avec sun_h >= 9.0 → averses tropicales (🌦️),
    # journée exploitable malgré rain_pct élevé. Logique affinée juin 2026.
    ('Guyane avril',  28, 95,  9.1, 17.2, '🌦️'),  # sun 9.1 ≥ 9 → tropical_showers
    ('Guyane juin',   28, 98,  9.7, 18.5, '🌦️'),  # sun 9.7 ≥ 9 → tropical_showers
    ('Guyane juil',   29, 91, 11.1, 10.7, '🌦️'),  # sun 11.1 ≥ 9 → tropical_showers
    ('Guyane sept',   30, 46, 11.4,  2.5, '🌤️'),  # peu de pluie → beau temps
    ('Bali août',     27, 65, 11.5,  4.5, None),  # ne doit PAS être ⛈️
    ('Paris juil',    25, 31, 12.8,  1.9, None),  # ne doit PAS être ⛈️/🌧️
    ('Marrakech juil',39,  1, 12.8,  0.0, '🥵'),
]

for label, tmax, rain, sun, mm, expected in emoji_cases:
    got = weather_emoji(tmax, rain, sun, mm)
    if expected is None:
        if got in ('⛈️', '🌧️'):
            err(f"{label}: emoji inattendu {got} (destination agréable sur-pénalisée)")
        else:
            ok(f"{label}: {got} (pas de sur-pénalisation)")
    elif got != expected:
        err(f"{label}: attendu {expected}, obtenu {got}")
    else:
        ok(f"{label}: {got}")

# ── 4. EMOJIS : pages HTML annuelles cohérentes avec lib/common.py ───────────
print("\n4. Emojis — cohérence pages annuelles FR/EN")

guyane_emojis_fr = get_emoji_in_table('meilleure-periode-guyane.html')
expected_guyane = {'Avril': '⛈️', 'Mai': '⛈️', 'Juin': '⛈️', 'Juillet': '🌧️'}
months_fr = ['Janvier','Février','Mars','Avril','Mai','Juin','Juillet','Août','Septembre','Octobre','Novembre','Décembre']

for i, emoji in enumerate(guyane_emojis_fr[:12]):
    m = months_fr[i]
    if m in expected_guyane and emoji != expected_guyane[m]:
        err(f"Guyane FR annuelle — {m}: attendu {expected_guyane[m]}, obtenu {emoji}")
    elif m in expected_guyane:
        ok(f"Guyane FR annuelle — {m}: {emoji}")

# ── 5. SCORING : pages annuelles présentes pour les 5 langues ─────────────────
print("\n5. Pages annuelles — 5 langues")

annual_files = {
    'FR': 'meilleure-periode-tokyo.html',
    'EN': 'en/best-time-to-visit-tokyo.html',
    'ES': 'es/mejor-epoca-tokio.html',
    'DE': 'de/beste-reisezeit-tokyo.html',
    'US': 'us/best-time-to-visit-tokyo.html',
}
for lang, f in annual_files.items():
    if os.path.exists(f):
        ok(f"{lang}: {f}")
    else:
        err(f"{lang}: {f} ABSENT")

# ── 6. JS : version core.min.js cohérente dans toutes les index ───────────────
print("\n6. Version core.min.js — cohérence entre index pages")

index_files = {
    'FR':    'index.html',
    'EN app': 'en/app.html',
    'ES app': 'es/app.html',
    'DE app': 'de/app.html',
    'US app': 'us/app.html',
}
versions = {}
for lang, f in index_files.items():
    try:
        content = open(f, encoding='utf-8').read()
        m = re.search(r'core\.min\.js\?v=(\d+)', content)
        if m: versions[lang] = m.group(1)
    except: pass

if len(set(versions.values())) == 1:
    ok(f"core.min.js v{list(versions.values())[0]} identique sur {list(versions.keys())}")
else:
    err(f"core.min.js versions divergent : {versions}")

# Check app.css version too
css_versions = {}
for lang, f in index_files.items():
    try:
        content2 = open(f, encoding='utf-8').read()
        m = re.search(r'app\.css\?v=(\d+)', content2)
        if m: css_versions[lang] = m.group(1)
    except: pass
if len(set(css_versions.values())) == 1:
    ok(f"app.css v{list(css_versions.values())[0]} identique sur {list(css_versions.keys())}")
elif css_versions:
    err(f"app.css versions divergent : {css_versions}")

# ── 7. dew_point : couverture climate.csv ────────────────────────────────────
print("\n7. dew_point_mean — couverture climate.csv")

total = len(climate)
filled = sum(1 for r in climate if r.get('dew_point_mean','').strip() and True)
pct = filled / total * 100
if pct >= 99:
    ok(f"dew_point: {filled}/{total} ({pct:.1f}%)")
elif pct >= 90:
    # Dette de données connue (non-bloquante pour le déploiement SEO).
    # dew_point sert au ressenti thermique tropical, pas à la structure des pages.
    warn(f"dew_point: {filled}/{total} ({pct:.1f}%) — {total-filled} dest à recalculer (non-bloquant)")
else:
    err(f"dew_point: seulement {filled}/{total} ({pct:.1f}%) — recalcul requis")

# ── 8. monthly.json : dewPoint présent ───────────────────────────────────────
print("\n8. dewPoint dans monthly.json")

monthly = json.load(open('data/monthly.json'))
has_dew = sum(1 for v in monthly.values() if any('dewPoint' in m for m in v.get('monthly', [])))
if has_dew > 400:
    ok(f"monthly.json: dewPoint présent sur {has_dew} destinations")
else:
    err(f"monthly.json: dewPoint absent ou incomplet ({has_dew} dest)")

# ── Validation JS inline (pages piliers) ─────────────────────────────────────
import subprocess, re as _re

PILIER_CHECKS = [
    'ou-partir-en-avril.html',
    'ou-partir-en-janvier.html',
    'meilleures-destinations-meteo.html',
]
DEAD_ELEMENTS = ['mode-tabs', 'reg-tabs', 'secu-tabs', 'budget-tabs']

for page in PILIER_CHECKS:
    if not os.path.exists(page):
        warn(f"JS check: {page} introuvable")
        continue
    content = open(page).read()
    start = content.find('<script>(function()')
    end = content.find('})();', start)
    if start < 0 or end < 0:
        err(f"JS {page}: IIFE introuvable (closing missing)")
        continue
    js = content[start+8:end+5]
    # Syntaxe
    r = subprocess.run(['node', '--check', '--input-type=module'],
                       input=js, capture_output=True, text=True)
    if r.returncode != 0:
        err(f"JS {page}: syntaxe invalide — {r.stderr.strip()[:120]}")
    else:
        ok(f"JS syntaxe OK: {page}")
    # render() présent
    if 'render(' not in js:
        err(f"JS {page}: render() absent — table vide au chargement")
    # Listeners sur éléments supprimés
    for dead in DEAD_ELEMENTS:
        if f'getElementById("{dead}")' in js:
            err(f"JS {page}: listener mort sur #{dead}")

# ══════════════════════════════════════════════════════════════════════════════
# CHECKS SEO STRUCTURELS (ajoutés juin 2026 après les bugs de la session)
# Ces checks attrapent les régressions qui nous ont coûté cher :
#   - liens .html internes (bug "Page avec redirection", millions de 307)
#   - régression V5→V6 silencieuse
#   - canonical pointant vers une URL qui redirige
#   - sitemap pollué (doublons, noindex, .html)
#   - contradiction sécurité classement vs fiche
# ══════════════════════════════════════════════════════════════════════════════

import glob

def _internal_html_links(html):
    """Retourne les href internes qui finissent en .html (hors externes)."""
    return [m for m in re.findall(r'href="([^"]+)"', html)
            if m.endswith('.html') and '://' not in m]

# ── 9. LIENS .html INTERNES = 0 (le bug majeur de la session) ────────────────
print("\n9. Liens .html internes (doit être 0 partout)")
SEO_SAMPLE = [
    'meilleure-periode-paris.html', 'paris-meteo-juillet.html',
    'ou-partir-en-mai.html', 'meilleures-destinations-meteo.html',
    'index.html', 'a-propos.html', 'methodologie.html',
    'en/best-time-to-visit-paris.html', 'en/app.html',
    'de/beste-reisezeit-bali.html', 'es/mejor-epoca-paris.html',
    'us/app.html',
]
html_link_pages = 0
checked = 0
for page in SEO_SAMPLE:
    if not os.path.exists(page):
        warn(f"SEO check: {page} introuvable")
        continue
    checked += 1
    links = _internal_html_links(open(page, encoding='utf-8').read())
    if links:
        html_link_pages += 1
        err(f"Liens .html internes dans {page}: {len(links)} (ex: {links[0]}) → redirige 307")
if html_link_pages == 0 and checked > 0:
    ok(f"0 lien .html interne sur {checked} pages échantillon")

# ── 10. MARKERS V6 présents (anti-régression V5→V6) ──────────────────────────
print("\n10. Format V6 sur les pages annuelles (anti-régression)")
V6_MARKERS = ['decider-grid', 'verdict-note', 'method-mini']
V6_SAMPLE = [
    'meilleure-periode-paris.html', 'meilleure-periode-bali.html',
    'en/best-time-to-visit-paris.html', 'de/beste-reisezeit-bali.html',
    'es/mejor-epoca-paris.html',
]
v5_regressions = 0
for page in V6_SAMPLE:
    if not os.path.exists(page):
        continue
    content = open(page, encoding='utf-8').read()
    missing = [m for m in V6_MARKERS if m not in content]
    if missing:
        v5_regressions += 1
        err(f"RÉGRESSION V5→V6 sur {page}: markers absents {missing} "
            f"(régénérer avec --v6 !)")
if v5_regressions == 0:
    ok(f"Markers V6 présents sur {len([p for p in V6_SAMPLE if os.path.exists(p)])} pages annuelles")

# ── 11. CANONICAL sans .html + cohérent (anti-redirect canonical) ────────────
print("\n11. Canonical sans .html (anti 'canonical → redirect')")
CANON_SAMPLE = [
    ('meilleure-periode-paris.html', 'https://bestdateweather.com/meilleure-periode-paris'),
    ('paris-meteo-juillet.html', 'https://bestdateweather.com/paris-meteo-juillet'),
    ('ou-partir-en-mai.html', 'https://bestdateweather.com/ou-partir-en-mai'),
    ('a-propos.html', 'https://bestdateweather.com/a-propos'),
    ('en/app.html', 'https://bestdateweather.com/en/app'),
    ('us/app.html', 'https://bestdateweather.com/us/app'),
]
canon_issues = 0
for page, expected in CANON_SAMPLE:
    if not os.path.exists(page):
        continue
    content = open(page, encoding='utf-8').read()
    m = re.search(r'rel="canonical" href="([^"]+)"', content)
    if not m:
        canon_issues += 1
        err(f"Canonical absent sur {page}")
    elif '.html' in m.group(1):
        canon_issues += 1
        err(f"Canonical .html sur {page}: {m.group(1)} → redirige 307")
    elif m.group(1) != expected:
        warn(f"Canonical inattendu sur {page}: {m.group(1)} (attendu {expected})")
if canon_issues == 0:
    ok("Canonical sans .html sur l'échantillon")

# ── 12. SITEMAP : 0 .html, 0 noindex, 0 doublon ──────────────────────────────
print("\n12. Intégrité des sitemaps")
# 12a. Pas de vieux sitemap-{lang}.xml (doublons fantômes)
legacy_sitemaps = [f for f in glob.glob('sitemap-??.xml')
                   if re.match(r'sitemap-(fr|en|es|de|us)\.xml$', f)]
if legacy_sitemaps:
    err(f"Vieux sitemaps présents (doublons): {legacy_sitemaps} → git rm")
else:
    ok("Pas de vieux sitemap-{lang}.xml (anti-doublon)")

# 12b. Aucune URL .html dans les sitemaps actifs
sitemap_html = 0
sitemap_files = glob.glob('sitemap-*-priority.xml') + glob.glob('sitemap-*-secondary.xml')
for sm in sitemap_files:
    content = open(sm, encoding='utf-8').read()
    n = content.count('.html</loc>')
    if n:
        sitemap_html += n
        err(f"{sm}: {n} URLs .html (doivent être sans extension)")
if sitemap_html == 0 and sitemap_files:
    ok(f"0 URL .html dans {len(sitemap_files)} sitemaps")

# 12c. Aucune URL noindex (prototype/v6) dans les sitemaps
sitemap_noindex = 0
for sm in sitemap_files:
    content = open(sm, encoding='utf-8').read()
    n = len(re.findall(r'(prototype-|-v6</loc>|-v6\.html)', content))
    if n:
        sitemap_noindex += n
        err(f"{sm}: {n} URLs prototype/v6 (noindex, hors sitemap)")
if sitemap_noindex == 0 and sitemap_files:
    ok("0 URL noindex (prototype/v6) dans les sitemaps")

# ── 13. SÉCURITÉ : cohérence classement vs fiche (anti-contradiction) ─────────
print("\n13. Cohérence sécurité (classement utilise Math.max FR/DE)")
secu_issues = 0
mai_pilier = 'ou-partir-en-mai.html'
if os.path.exists(mai_pilier):
    content = open(mai_pilier, encoding='utf-8').read()
    # Le classement doit combiner les 2 sources avec Math.max (jamais écraser FR par DE)
    if 'Math.max(POOL' not in content:
        secu_issues += 1
        err(f"{mai_pilier}: pas de Math.max sur les advisories → risque "
            f"d'écraser le niveau FR prudent par DE permissif")
    # country_info.json doit avoir risk_source = 'MAE France' (pas DE héritée)
    try:
        ci = json.load(open('data/country_info.json'))
        de_sources = sum(1 for p, v in ci.items()
                         if isinstance(v, dict) and v.get('risk_source') == 'Auswärtiges Amt (DE)')
        if de_sources > 0:
            warn(f"country_info.json: {de_sources} pays avec risk_source DE "
                 f"(devrait être 'MAE France')")
    except Exception:
        pass
if secu_issues == 0:
    ok("Sécurité: classement combine les sources avec Math.max")

# ── Résumé ────────────────────────────────────────────────────────────────────
print(f"\n{'='*55}")
if not ERRORS and not WARNINGS:
    print("✅ Tout OK — déploiement cohérent sur toutes les surfaces")
else:
    for w in WARNINGS: print(w)
    for e in ERRORS:   print(e)
    if ERRORS:
        print(f"\n{len(ERRORS)} erreur(s) à corriger avant deploy !")
        sys.exit(1)
    else:
        print(f"\n{len(WARNINGS)} avertissement(s) — vérifier avant deploy")
