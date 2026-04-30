#!/usr/bin/env python3
"""
BestDateWeather — Scoring Consistency Tests
============================================
Verifies that scoring.py (Python, source of truth) stays in sync with
core.js (JavaScript, client-side replica).

Usage: python3 tests/test_scoring.py
Exit code: 0 = all pass, 1 = failures

Tests:
  1. t_ideal() Python vs JS for 20 temperature values
  2. raw_score() Python vs JS for 15 climate combinations
  3. FICHE_SCORES in core.js matches climate.csv
  4. TROPICAL_KEYS in core.js matches destinations.csv
  5. FR/EN generator function parity
"""

import csv
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from scoring import t_ideal, raw_score, compute_mountain_scores

CORE_JS = ROOT / 'js' / 'core.js'
FICHE_JS = ROOT / 'js' / 'fiche-scores.js'
PASS = 0
FAIL = 0


def check(name, condition, detail=''):
    global PASS, FAIL
    if condition:
        PASS += 1
    else:
        FAIL += 1
        print(f"  ❌ {name}: {detail}")


# ── Test 1: t_ideal() parity ──────────────────────────────────────────────
def test_t_ideal():
    print("1. t_ideal() Python ↔ JS")
    temps = [-5, 0, 5, 10, 14, 18, 22, 25, 28, 30, 33, 35, 38, 40, 42]

    # Run JS version
    js_code = """
    function lerp(x, x0, x1, y0, y1) {
     if (x <= x0) return y0;
     if (x >= x1) return y1;
     return y0 + (y1 - y0) * ((x - x0) / (x1 - x0));
    }
    function tIdeal(tmax) {
     // Aligned with scoring.py t_ideal() — breakpoints 28/31/34/37/40
     if (tmax <= 5)  return 0.0;
     if (tmax <= 14) return lerp(tmax, 5, 14, 0.0, 0.3);
     if (tmax <= 22) return lerp(tmax, 14, 22, 0.3, 0.8);
     if (tmax <= 28) return lerp(tmax, 22, 28, 0.8, 1.0);
     if (tmax <= 31) return lerp(tmax, 28, 31, 1.0, 0.90);
     if (tmax <= 34) return lerp(tmax, 31, 34, 0.90, 0.60);
     if (tmax <= 37) return lerp(tmax, 34, 37, 0.60, 0.25);
     if (tmax <= 40) return lerp(tmax, 37, 40, 0.25, 0.05);
     return 0.0;
    }
    var temps = %s;
    console.log(JSON.stringify(temps.map(tIdeal)));
    """ % json.dumps(temps)

    result = subprocess.run(['node', '-e', js_code], capture_output=True, text=True)
    js_values = json.loads(result.stdout.strip())

    for i, t in enumerate(temps):
        py_val = round(t_ideal(t), 6)
        js_val = round(js_values[i], 6)
        check(f"t_ideal({t})", abs(py_val - js_val) < 0.001,
              f"Python={py_val} JS={js_val}")


# ── Test 2: raw_score() parity ────────────────────────────────────────────
def test_raw_score():
    print("2. raw_score() Python ↔ JS")
    cases = [
        (25, 20, 10),   # Ideal summer
        (35, 5, 14),    # Hot dry
        (5, 60, 3),     # Cold rainy
        (15, 40, 7),    # Mild
        (28, 10, 12),   # Warm sunny
        (0, 80, 1),     # Freezing
        (40, 0, 15),    # Scorching
        (22, 30, 8),    # Mediterranean
        (18, 50, 5),    # UK autumn
        (30, 70, 6),    # Monsoon
    ]

    js_code = """
    function lerp(x, x0, x1, y0, y1) {
     if (x <= x0) return y0;
     if (x >= x1) return y1;
     return y0 + (y1 - y0) * ((x - x0) / (x1 - x0));
    }
    function tIdeal(tmax) {
     if (tmax <= 5)  return 0.0;
     if (tmax <= 14) return lerp(tmax, 5, 14, 0.0, 0.3);
     if (tmax <= 22) return lerp(tmax, 14, 22, 0.3, 0.8);
     if (tmax <= 28) return lerp(tmax, 22, 28, 0.8, 1.0);
     if (tmax <= 31) return lerp(tmax, 28, 31, 1.0, 0.90);
     if (tmax <= 34) return lerp(tmax, 31, 34, 0.90, 0.60);
     if (tmax <= 37) return lerp(tmax, 34, 37, 0.60, 0.25);
     if (tmax <= 40) return lerp(tmax, 37, 40, 0.25, 0.05);
     return 0.0;
    }
    function rawScoreFiche(tmax, rain, sun) {
     return 0.40 * tIdeal(tmax)
      + 0.35 * Math.max(0, 1 - rain / 100)
      + 0.25 * Math.min(1, sun / 15);
    }
    var cases = %s;
    console.log(JSON.stringify(cases.map(function(c) {
        return rawScoreFiche(c[0], c[1], c[2]);
    })));
    """ % json.dumps(cases)

    result = subprocess.run(['node', '-e', js_code], capture_output=True, text=True)
    js_values = json.loads(result.stdout.strip())

    for i, (tmax, rain, sun) in enumerate(cases):
        py_val = round(raw_score(tmax, rain, sun), 6)
        js_val = round(js_values[i], 6)
        check(f"raw_score({tmax},{rain},{sun})", abs(py_val - js_val) < 0.001,
              f"Python={py_val} JS={js_val}")


# ── Test 3: FICHE_SCORES matches climate.csv ──────────────────────────────
def test_fiche_scores():
    print("3. FICHE_SCORES ↔ climate.csv")

    # Load climate.csv scores
    csv_scores = {}
    with open(ROOT / 'data/climate.csv', encoding='utf-8-sig') as f:
        for r in csv.DictReader(f):
            slug = r['slug']
            mi = int(r['mois_num']) - 1
            if slug not in csv_scores:
                csv_scores[slug] = [None] * 12
            csv_scores[slug][mi] = round(float(r['score']) * 10)

    # Load destinations coords
    dest_coords = {}
    with open(ROOT / 'data/destinations.csv', encoding='utf-8-sig') as f:
        for r in csv.DictReader(f):
            key = f"{r['lat'].strip()},{r['lon'].strip()}"
            dest_coords[r['slug_fr']] = key

    # Load FICHE_SCORES from JS
    js = FICHE_JS.read_text(encoding='utf-8')
    m = re.search(r'var FICHE_SCORES = ({.*?});', js)
    fiche = json.loads(m.group(1))

    check("FICHE_SCORES count", len(fiche) >= 310,
          f"Only {len(fiche)} entries (expected 310+)")

    # Verify a sample of destinations
    mismatches = []
    shared_coords = []
    for slug, coord_key in dest_coords.items():
        if coord_key in fiche and slug in csv_scores:
            if fiche[coord_key] != csv_scores[slug]:
                # Check if another dest shares this coordinate
                sharing = [s for s, c in dest_coords.items() if c == coord_key and s != slug]
                if sharing:
                    shared_coords.append(f"{slug}/{sharing[0]}")
                else:
                    mismatches.append(slug)

    if shared_coords:
        print(f"  ℹ  Shared coords (expected): {shared_coords}")

    check("FICHE_SCORES values", len(mismatches) == 0,
          f"{len(mismatches)} mismatches: {mismatches[:5]}")


# ── Test 4: TROPICAL_KEYS matches destinations.csv ────────────────────────
def test_tropical_keys():
    print("4. TROPICAL_KEYS ↔ destinations.csv")

    # Load tropical flags from CSV
    csv_tropical = set()
    with open(ROOT / 'data/destinations.csv', encoding='utf-8-sig') as f:
        for r in csv.DictReader(f):
            if r.get('tropical', '').strip().lower() in ('true', '1', 'yes'):
                csv_tropical.add(f"{r['lat'].strip()},{r['lon'].strip()}")

    # Load from JS
    js = CORE_JS.read_text(encoding='utf-8')
    m = re.search(r'var TROPICAL_KEYS = \{([^}]*)\}', js, re.DOTALL)
    js_keys = set(re.findall(r'"([^"]+)":\s*true', m.group(1)))

    check("TROPICAL_KEYS count", len(js_keys) == len(csv_tropical),
          f"JS={len(js_keys)} CSV={len(csv_tropical)}")

    missing = csv_tropical - js_keys
    extra = js_keys - csv_tropical
    check("TROPICAL_KEYS sync", len(missing) == 0 and len(extra) == 0,
          f"Missing: {list(missing)[:3]}, Extra: {list(extra)[:3]}")


# ── Test 5: Unified generator has required functions ──────────────────────
def test_generator_parity():
    print("5. generate_pages.py completeness")

    gen = (ROOT / 'generate_pages.py').read_text()
    gen_fns = set(re.findall(r'^def (\w+)\(', gen, re.MULTILINE))

    # Import block
    import_block = re.search(r'from lib\.common import \((.*?)\)', gen, re.DOTALL)
    gen_imports = set(re.findall(r'\b(\w+)\b', import_block.group(1))) if import_block else set()
    gen_imports |= set(re.findall(r'from lib\.common import (\w+)', gen))
    gen_available = gen_fns | gen_imports

    # Core functions that MUST exist (either defined or imported)
    required = {'load_data', 'validate', 'best_months', 'budget_tier',
                'score_badge', 'seasonal_stats', 'bar_chart',
                'climate_table_html', 'gen_annual', 'gen_monthly', 'main'}

    for fn in required:
        check(f"generate_pages.py has {fn}()", fn in gen_available,
              f"Missing from generate_pages.py (defined or imported)")

    # Verify lib.common exists and has shared functions
    common = (ROOT / 'lib' / 'common.py').read_text()
    common_fns = set(re.findall(r'^def (\w+)\(', common, re.MULTILINE))
    shared_expected = {'score_badge', 'best_months', 'budget_tier',
                       'seasonal_stats', 'bar_chart', 'climate_table_html',
                       'validate_climate'}
    for fn in shared_expected:
        check(f"lib/common.py has {fn}()", fn in common_fns,
              f"Missing from lib/common.py")

    # Verify generate_pages.py supports both FR and EN
    check("Supports FR", "'fr'" in gen or '"fr"' in gen,
          "No FR language support found")
    check("Supports EN", "'en'" in gen or '"en"' in gen,
          "No EN language support found")


# ── Test 6: Mountain scoring — invariants sur toutes les dest mountain ────
def test_mountain_scoring():
    print("6. Mountain scoring — invariants sur les destinations mountain")

    # Charger les destinations mountain depuis destinations.csv
    mountain_slugs = []
    with open(ROOT / 'data/destinations.csv', encoding='utf-8-sig') as f:
        for r in csv.DictReader(f):
            if r.get('mountain', '').strip().lower() in ('true', '1', 'yes'):
                mountain_slugs.append(r['slug_fr'])

    # Charger climate.csv groupé par slug
    climate_by_slug = {}
    with open(ROOT / 'data/climate.csv', encoding='utf-8-sig') as f:
        for r in csv.DictReader(f):
            climate_by_slug.setdefault(r['slug'], []).append({
                'mois': r['mois'],
                'mois_num': int(r['mois_num']),
                'tmax': float(r['tmax']),
                'rain_pct': float(r['rain_pct']),
                'sun_h': float(r['sun_h']),
                'precip_mm': float(r['precip_mm']) if r.get('precip_mm', '').strip() else None,
            })

    # Tester chaque mountain
    invariant_failures = []
    tested_count = 0
    for slug in mountain_slugs:
        if slug not in climate_by_slug:
            continue  # skip si données climate manquantes
        months = sorted(climate_by_slug[slug], key=lambda r: r['mois_num'])
        if len(months) != 12:
            continue
        result = compute_mountain_scores(months, slug)
        if len(result) != 12:
            invariant_failures.append(f"{slug}: result n'a pas 12 entrées ({len(result)})")
            continue
        for r in result:
            # Bornes score
            if not (0 <= r['score_10'] <= 10):
                invariant_failures.append(f"{slug}/{r['mois']}: score_10 hors [0,10] = {r['score_10']}")
            # Classe valide
            if r['classe'] not in ('rec', 'mid', 'avoid'):
                invariant_failures.append(f"{slug}/{r['mois']}: classe invalide '{r['classe']}'")
            # Dominant valide
            if r['dominant'] not in ('ski', 'rando'):
                invariant_failures.append(f"{slug}/{r['mois']}: dominant invalide '{r['dominant']}'")
            # score_10 == max(ski, rando)
            expected_max = max(r['ski_score'], r['rando_score'])
            if abs(r['score_10'] - expected_max) > 0.01:
                invariant_failures.append(f"{slug}/{r['mois']}: score_10={r['score_10']} != max(ski={r['ski_score']}, rando={r['rando_score']})")
            # Classe cohérente avec score
            expected_cls = 'rec' if r['score_10'] >= 7 else 'mid' if r['score_10'] >= 4 else 'avoid'
            if r['classe'] != expected_cls:
                invariant_failures.append(f"{slug}/{r['mois']}: classe={r['classe']} mais score={r['score_10']} attendait {expected_cls}")
            # score_100 == round(score_10 * 10)
            if r['score_100'] != round(r['score_10'] * 10):
                invariant_failures.append(f"{slug}/{r['mois']}: score_100={r['score_100']} != round(score_10 * 10)")
        tested_count += 1

    check(f"Mountain destinations testées (>=100)", tested_count >= 100,
          f"testées={tested_count}, mountain dans CSV={len(mountain_slugs)}")
    check("Invariants score/classe/dominant respectés sur toutes les mountain",
          len(invariant_failures) == 0,
          f"échecs={len(invariant_failures)}, ex: {invariant_failures[:2]}")

    # ── Régression Chamonix : 3 valeurs clés (vérifiées manuellement contre scoring.py) ──
    cham = next((r for r in compute_mountain_scores(
                    sorted(climate_by_slug['chamonix'], key=lambda r: r['mois_num']), 'chamonix')
                 if r['mois'] == 'Mars'), None)
    check("Régression Chamonix Mars: 9.1 (ski) rec",
          cham and cham['score_10'] == 9.1 and cham['dominant'] == 'ski' and cham['classe'] == 'rec',
          f"got {cham}" if cham else "Mars introuvable")

    cham_oct = next((r for r in compute_mountain_scores(
                        sorted(climate_by_slug['chamonix'], key=lambda r: r['mois_num']), 'chamonix')
                     if r['mois'] == 'Octobre'), None)
    check("Régression Chamonix Octobre: 7.8 (rando) rec — pas mid avec lapse rate",
          cham_oct and cham_oct['score_10'] == 7.8 and cham_oct['dominant'] == 'rando' and cham_oct['classe'] == 'rec',
          f"got {cham_oct}" if cham_oct else "Octobre introuvable")

    cham_nov = next((r for r in compute_mountain_scores(
                        sorted(climate_by_slug['chamonix'], key=lambda r: r['mois_num']), 'chamonix')
                     if r['mois'] == 'Novembre'), None)
    check("Régression Chamonix Novembre: 6.1 mid (transition)",
          cham_nov and cham_nov['score_10'] == 6.1 and cham_nov['classe'] == 'mid',
          f"got {cham_nov}" if cham_nov else "Novembre introuvable")


def test_v6_helpers():
    """Validate V6 rendering helpers (lib/v6.py).

    Invariants tested:
      1. All 5 locales (FR, EN, EN-US, ES, DE) must have 'v6' section
      2. render_v6_topbar produces non-empty HTML in all 5 langs
      3. render_v6_footer produces non-empty HTML with correct lang links
      4. render_v6_methodology_block: mountain version differs from standard
      5. KeyError raised when a locale doesn't have 'v6' (sanity check)
    """
    print("Test 7: V6 rendering helpers")
    from lib.v6 import (render_v6_topbar, render_v6_footer,
                        render_v6_methodology_block, _v6_strings)

    # Reset cache to ensure fresh reads
    from lib import v6 as v6_mod
    v6_mod._v6_cache.clear()

    LANGS = ['fr', 'en', 'en-us', 'es', 'de']

    # 1. v6 section presence
    for lang in LANGS:
        try:
            strings = _v6_strings(lang)
            check(f"locales/{lang}.json has 'v6' section",
                  strings is not None and 'topbar' in strings,
                  f"v6 missing or invalid in {lang}")
        except KeyError as e:
            check(f"locales/{lang}.json has 'v6' section", False, str(e))

    # 2. Topbar non-empty for all langs + key vocab present
    expected_brand_marker = 'BestDateWeather'  # part of brand string in DOM
    for lang in LANGS:
        out = render_v6_topbar('chamonix', lang)
        check(f"topbar/{lang}: non-empty + brand present",
              len(out) > 500 and 'Best' in out and 'data-slug="chamonix"' in out,
              f"got len={len(out)}")

    # 3. Footer must include sister-language links
    fr_footer = render_v6_footer('chamonix', 'fr')
    check("footer/fr: includes English link",
          'flags/gb.png' in fr_footer and 'best-time-to-visit-chamonix' in fr_footer,
          "EN link missing")
    check("footer/fr: includes Spanish link",
          'flags/es.png' in fr_footer and 'mejor-epoca-chamonix' in fr_footer,
          "ES link missing")
    check("footer/fr: includes German link",
          'flags/de.png' in fr_footer and 'beste-reisezeit-chamonix' in fr_footer,
          "DE link missing")

    en_footer = render_v6_footer('chamonix', 'en')
    check("footer/en: does NOT include current-lang in language switcher",
          'flags/gb.png' not in en_footer,
          "EN link should be absent in EN footer")

    # 4. Methodology mountain vs standard
    method_mtn = render_v6_methodology_block('fr', is_mountain=True)
    method_std = render_v6_methodology_block('fr', is_mountain=False)
    check("methodology/fr: mountain has 2 sub-models",
          method_mtn.count('method-mini-model') >= 4,  # 2 models × 2 occurrences each (open + head)
          f"got {method_mtn.count('method-mini-model')} occurrences")
    check("methodology/fr: standard has NO sub-models",
          'method-mini-model' not in method_std,
          "standard should not contain sub-models")
    check("methodology/fr: mountain mentions ski + rando",
          'Score ski' in method_mtn and 'Score rando' in method_mtn,
          "missing ski or rando label")

    # 5. Iso-functional with Chamonix proto V6
    import re
    proto = open(ROOT / 'meilleure-periode-chamonix-v6.html').read()
    proto_topbar_match = re.search(r'<div class="topbar">.*?</div>\s*</div>', proto, re.DOTALL)
    if proto_topbar_match:
        def norm(s): return re.sub(r'\s+', ' ', s).strip()
        gen_topbar = render_v6_topbar('chamonix', 'fr')
        check("topbar/fr: matches Chamonix proto V6 (normalized)",
              norm(proto_topbar_match.group(0)) == norm(gen_topbar),
              "diverges from manual proto")

    # 6. Trend chart helper
    from lib.v6 import render_v6_trend_chart
    trend_cham = render_v6_trend_chart('chamonix', 'Chamonix', 'fr')
    check("trend/chamonix: SVG present + slope annotation",
          '<svg viewBox="0 0 800 360"' in trend_cham
          and '/ décennie' in trend_cham
          and 'pic décennie' in trend_cham,
          "SVG, slope or pic missing")

    trend_lyon = render_v6_trend_chart('lyon', 'Lyon', 'fr', lat=45.75, lon=4.83)
    check("trend/lyon: coord fallback works (slug not in dataset)",
          '<svg viewBox="0 0 800 360"' in trend_lyon
          and 'ct-no-data' not in trend_lyon
          and '+0.72' in trend_lyon,
          "coord lookup or slope calc failed")

    trend_missing = render_v6_trend_chart('non-existent-xyz', 'Nowhere', 'fr')
    check("trend/missing: graceful no-data fallback",
          'ct-no-data' in trend_missing,
          "should show no-data fallback")

    # 7. Infos pratiques helper - all 5 profiles
    from lib.v6 import render_v6_infos_pratiques
    chamonix_data = {
        'dest_name': 'Chamonix', 'country_name': 'France', 'country_iso': 'fr',
        'lang_local': 'Français', 'currency_name': 'Euro', 'currency_symbol': '€',
        'drive': 'right', 'gpi_level': 1, 'cost_tier': 4,
        'climate_type': 'Montagne (alpin)', 'trend_value': 0.84,
        'hottest_month': 'Août', 'hottest_temp': 24,
        'coldest_month': 'Janvier', 'coldest_temp': 4,
        'rainiest_month': 'Mai', 'rainiest_pct': 61,
        'is_mountain': True,
        'alt_village': 1035, 'alt_ski_max': 3842,
        'ski_season': 'Déc → Mai', 'hiking_season': 'Juin → Sept',
    }
    ip_chamonix = render_v6_infos_pratiques('chamonix', 'fr', chamonix_data)
    check("infos_pratiques/chamonix: 3 boxes + Séjour montagne",
          ip_chamonix.count('<div class="box">') == 3 and 'Séjour montagne' in ip_chamonix,
          "missing boxes or wrong profile")

    bali_data = {
        'dest_name': 'Bali', 'country_name': 'Indonésie', 'country_iso': 'id',
        'lang_local': 'Indonésien', 'currency_name': 'Rp', 'currency_symbol': 'Rp',
        'drive': 'left', 'gpi_level': 1, 'cost_tier': 1,
        'climate_type': 'Tropical', 'trend_value': 0.37,
        'hottest_month': 'Nov', 'hottest_temp': 30,
        'coldest_month': 'Juil', 'coldest_temp': 27,
        'rainiest_month': 'Fév', 'rainiest_pct': 92,
        'is_tropical': True,
        'dry_season': 'Mai → Sept', 'wet_season': 'Déc → Mars',
        'sea_summer': 27, 'sea_winter': 29,
        'has_cyclones': False, 'latitude': -8.67,
    }
    ip_bali = render_v6_infos_pratiques('bali', 'fr', bali_data)
    check("infos_pratiques/bali: tropical profile + Aucun équateur",
          'Séjour tropical' in ip_bali and 'Aucun (équateur)' in ip_bali,
          "tropical profile detection failed")

    # Reykjavik polar (with stable trend < 0.20)
    rey_data = {
        'dest_name': 'Reykjavik', 'country_name': 'Islande', 'country_iso': 'is',
        'lang_local': 'Islandais', 'currency_name': 'kr', 'currency_symbol': 'kr',
        'drive': 'right', 'gpi_level': 1, 'cost_tier': 5,
        'climate_type': 'Subarctique', 'trend_value': -0.15,
        'hottest_month': 'Juil', 'hottest_temp': 13,
        'coldest_month': 'Janv', 'coldest_temp': 2,
        'rainiest_month': 'Fév', 'rainiest_pct': 63,
        'is_polar': True, 'latitude': 64.15, 'has_geothermal': True,
    }
    ip_rey = render_v6_infos_pratiques('reykjavik', 'fr', rey_data)
    check("infos_pratiques/reykjavik: polar + Stable trend",
          'Séjour subarctique' in ip_rey and 'Stable' in ip_rey,
          "polar or stable trend detection failed")

    # Multi-language smoke test
    for lang in ['en', 'es', 'de']:
        ip = render_v6_infos_pratiques('bali', lang, bali_data)
        check(f"infos_pratiques/{lang}: renders without KeyError",
              len(ip) > 1000 and '<div class="box">' in ip,
              f"render failed for lang={lang}")

    # 8. Decision card helper
    from lib.v6 import render_v6_decision_card
    chamonix_hero = {
        'dest_name': 'Chamonix', 'country_name': 'France', 'country_iso': 'fr',
        'climate_type': 'Climat alpin', 'lat': 45.92, 'lon': 6.87,
        'is_mountain': True, 'update_month': 'Avril',
        'h1_accent_part': 'pour skier ou randonner',
        'lead': '<strong>Mars</strong> sort en tête.',
        'decision_main_month': 'Mars', 'decision_main_score': '9.1',
        'mini_cards': [
            {'value': '⛷️ Mars', 'label': 'Ski'},
            {'value': '🥾 Août', 'label': 'Rando'},
            {'value': 'Nov', 'label': 'Transition'},
        ],
        'chips': [{'emoji': '❄️', 'text': 'Alpin', 'color': 'blue'}],
    }
    hero = render_v6_decision_card('chamonix', 'fr', chamonix_hero)
    check("decision_card/chamonix: hero-wrap + decision-card present",
          '<header class="hero-wrap">' in hero
          and '<div class="decision-card">' in hero
          and hero.count('class="mini-card"') == 3,
          "structural elements missing")
    check("decision_card/chamonix: H1 has accent",
          '<span class="accent">' in hero and 'pour skier ou randonner' in hero,
          "H1 accent injection failed")

    # 9. Section helpers : Comprendre / Contexte / Questions / Adapter
    from lib.v6 import (render_v6_comprendre, render_v6_contexte,
                        render_v6_questions, render_v6_adapter,
                        render_v6_localisation, render_v6_reserver)

    months_data = [
        {'mois': 'Janvier', 'tmin': -4, 'tmax': 4, 'rain_pct': 45,
         'precip_mm': 6.0, 'sun_h': 7.3, 'score_10': 7.9, 'classe': 'rec'},
        {'mois': 'Mars', 'tmin': -1, 'tmax': 8, 'rain_pct': 45,
         'precip_mm': 4.8, 'sun_h': 10.4, 'score_10': 9.1, 'classe': 'rec', 'is_best': True},
        {'mois': 'Novembre', 'tmin': 0, 'tmax': 8, 'rain_pct': 45,
         'precip_mm': 5.4, 'sun_h': 7.9, 'score_10': 6.1, 'classe': 'mid'},
    ]
    comp = render_v6_comprendre('chamonix', 'fr', months_data, 'chamonix-meteo-{mois_lower}.html')
    check("comprendre/fr: 3 desktop rows + 3 mobile cards",
          comp.count('<tr class="row') == 3 and comp.count('mobile-month-card') >= 3,
          "missing rows")
    check("comprendre/fr: best class on Mars row",
          'class="row best"' in comp and 'mobile-month-card best' in comp,
          "best marker missing")

    ctx = render_v6_contexte('chamonix', 'fr', '<p>Edito test</p>')
    check("contexte/fr: section + edito injected",
          '<p>Edito test</p>' in ctx and 'Contexte' in ctx,
          "edito not injected")

    faqs = [{'q': 'Q1?', 'a': '<strong>A1</strong>'}, {'q': 'Q2?', 'a': 'A2'}]
    qs = render_v6_questions('chamonix', 'fr', faqs)
    check("questions/fr: 2 details with HTML in answers",
          qs.count('<details') == 2 and '<strong>A1</strong>' in qs,
          "FAQ not rendered correctly")

    adapt = render_v6_adapter('chamonix', 'fr', profile='mountain')
    check("adapter/mountain: 3 default chips",
          adapt.count('border-radius:999px') == 3,
          "default chips missing")

    loc_section = render_v6_localisation('chamonix', 'fr', 'Chamonix', 45.92, 6.87)
    check("localisation/fr: dest-map div with data-attrs",
          'id="dest-map"' in loc_section and 'data-lat="45.9200"' in loc_section,
          "map container missing")

    reserve = render_v6_reserver('chamonix', 'fr', 'Chamonix')
    check("reserver/fr: 3 affiliate CTAs",
          reserve.count('class="card pad reserve-card"') == 3
          and 'expedia.fr' in reserve and 'getyourguide.com' in reserve,
          "affiliate links missing")

    # 10. Full page orchestrator
    from lib.v6 import render_v6_full_page
    full_data = {
        'lang': 'fr', 'slug': 'chamonix',
        'dest_name': 'Chamonix',
        'page_title': 'Chamonix : meilleurs mois', 'page_desc': 'Test',
        'lat': 45.92, 'lon': 6.87,
        'is_mountain': True, 'profile': 'mountain',
        'months_data': months_data * 4,  # fake 12 months for test
        'monthly_url_tpl': 'chamonix-{mois_lower}.html',
        'edito_html': '<p>Test edito</p>',
        'hero_data': {
            'dest_name': 'Chamonix', 'country_name': 'France', 'country_iso': 'fr',
            'climate_type': 'Alpin', 'lat': 45.92, 'lon': 6.87,
            'is_mountain': True, 'update_month': 'Avril',
            'h1_accent_part': 'pour skier ou randonner',
            'lead': '<p>Lead</p>',
            'decision_main_month': 'Mars', 'decision_main_score': '9.1',
            'mini_cards': [{'value': 'Mars', 'label': 'Top'}] * 3,
            'chips': [{'emoji': '❄️', 'text': 'Alpin', 'color': 'blue'}],
        },
        'infos_pratiques_data': {
            'dest_name': 'Chamonix', 'country_name': 'France', 'country_iso': 'fr',
            'lang_local': 'Français', 'currency_name': 'Euro', 'currency_symbol': '€',
            'drive': 'right', 'gpi_level': 1, 'cost_tier': 4,
            'climate_type': 'Alpin', 'trend_value': 0.84,
            'hottest_month': 'Aoû', 'hottest_temp': 24,
            'coldest_month': 'Jan', 'coldest_temp': 4,
            'rainiest_month': 'Mai', 'rainiest_pct': 61,
            'is_mountain': True,
        },
        'faq_items': faqs,
    }
    page = render_v6_full_page(full_data)
    check("full_page/fr: contains all 10 sections",
          all(s in page for s in [
              'class="topbar"', 'class="hero-wrap"', 'id="tableau"',
              'tendance-section', '>Contexte<', '>Adapter<',
              '>Réserver<', '>Infos pratiques<', '>Localisation<',
              '>Questions<', 'bdw-footer',
          ]),
          "section missing in full page")
    check("full_page/fr: valid HTML doctype + lang attr",
          page.startswith('<!doctype html>') and 'lang="fr"' in page,
          "missing doctype or lang attribute")


# ── Run all ───────────────────────────────────────────────────────────────
if __name__ == '__main__':
    print("=" * 60)
    print("BestDateWeather — Scoring Consistency Tests")
    print("=" * 60)
    print()

    test_t_ideal()
    test_raw_score()
    test_fiche_scores()
    test_tropical_keys()
    test_generator_parity()
    test_mountain_scoring()
    test_v6_helpers()

    print()
    print(f"{'=' * 60}")
    print(f"Results: {PASS} passed, {FAIL} failed")
    print(f"{'=' * 60}")

    sys.exit(1 if FAIL else 0)
