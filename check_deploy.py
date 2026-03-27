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
    ('Guyane avril',  28, 95,  9.1, 17.2, '⛈️'),
    ('Guyane mai',    28, 99,  8.0, 21.7, '⛈️'),
    ('Guyane juin',   28, 98,  9.7, 18.5, '⛈️'),
    ('Guyane juil',   29, 91, 11.1, 10.7, '🌧️'),
    ('Guyane sept',   30, 46, 11.4,  2.5, '🌤️'),
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
elif pct >= 95:
    warn(f"dew_point: {filled}/{total} ({pct:.1f}%) — quelques destinations manquantes")
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
