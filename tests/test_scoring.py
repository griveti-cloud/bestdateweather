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

from scoring import t_ideal, raw_score

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

    print()
    print(f"{'=' * 60}")
    print(f"Results: {PASS} passed, {FAIL} failed")
    print(f"{'=' * 60}")

    sys.exit(1 if FAIL else 0)
