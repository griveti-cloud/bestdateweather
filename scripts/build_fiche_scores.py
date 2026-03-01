#!/usr/bin/env python3
"""
Build FICHE_SCORES and TROPICAL_KEYS in js/core.js from CSV data.

Reads:
  - data/destinations.csv  (lat, lon, tropical flag)
  - data/climate.csv       (monthly scores per destination)

Writes:
  - js/core.js             (replaces FICHE_SCORES and TROPICAL_KEYS blocks)

Usage: python3 scripts/build_fiche_scores.py
"""

import csv
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CORE_JS = ROOT / 'js' / 'core.js'


def load_destinations():
    """Load destinations with coords and tropical flag."""
    dests = {}
    with open(ROOT / 'data/destinations.csv', encoding='utf-8-sig') as f:
        for r in csv.DictReader(f):
            dests[r['slug_fr']] = {
                'lat': r['lat'].strip(),
                'lon': r['lon'].strip(),
                'tropical': r.get('tropical', '').strip().lower() in ('true', '1', 'yes'),
                'nom_bare': r.get('nom_bare', r['slug_fr']),
            }
    return dests


def load_climate_scores():
    """Load monthly scores (×10) from climate.csv."""
    climate = {}
    with open(ROOT / 'data/climate.csv', encoding='utf-8-sig') as f:
        for r in csv.DictReader(f):
            slug = r['slug']
            mi = int(r['mois_num']) - 1
            if slug not in climate:
                climate[slug] = [None] * 12
            climate[slug][mi] = round(float(r['score']) * 10)
    return climate


def build_fiche_scores(dests, climate):
    """Build {lat,lon: [s1,...,s12]} dict."""
    fiche = {}
    for slug, d in dests.items():
        scores = climate.get(slug)
        if not scores or any(s is None for s in scores):
            print(f"  ⚠ {slug}: climate data incomplete, skipped")
            continue
        key = f"{d['lat']},{d['lon']}"
        if key in fiche:
            # Duplicate coords — keep first (already warned at data level)
            continue
        fiche[key] = scores
    return fiche


def build_tropical_keys(dests):
    """Build {lat,lon: true} dict for tropical destinations."""
    tropical = {}
    for slug, d in dests.items():
        if d['tropical']:
            key = f"{d['lat']},{d['lon']}"
            tropical[key] = d['nom_bare']
    return tropical


def inject_into_core_js(fiche, tropical):
    """Replace FICHE_SCORES and TROPICAL_KEYS blocks in core.js."""
    js = CORE_JS.read_text(encoding='utf-8')

    # Build FICHE_SCORES line
    fiche_json = json.dumps(fiche, separators=(',', ':'))
    new_fiche = f'var FICHE_SCORES = {fiche_json};'

    # Build TROPICAL_KEYS block
    lines = ['var TROPICAL_KEYS = {']
    for key, name in sorted(tropical.items()):
        lines.append(f' "{key}": true, // {name}')
    lines.append('};')
    new_tropical = '\n'.join(lines)

    # Replace FICHE_SCORES (single line)
    pattern_fiche = r'var FICHE_SCORES = \{.*?\};'
    if not re.search(pattern_fiche, js):
        print("ERROR: FICHE_SCORES block not found in core.js")
        sys.exit(1)
    js = re.sub(pattern_fiche, new_fiche, js, count=1)

    # Replace TROPICAL_KEYS (multiline block)
    pattern_tropical = r'var TROPICAL_KEYS = \{[^}]*\};'
    if not re.search(pattern_tropical, js, re.DOTALL):
        print("ERROR: TROPICAL_KEYS block not found in core.js")
        sys.exit(1)
    js = re.sub(pattern_tropical, new_tropical, js, count=1, flags=re.DOTALL)

    CORE_JS.write_text(js, encoding='utf-8')


def main():
    dests = load_destinations()
    climate = load_climate_scores()
    fiche = build_fiche_scores(dests, climate)
    tropical = build_tropical_keys(dests)

    print(f"FICHE_SCORES: {len(fiche)} entries (was 71)")
    print(f"TROPICAL_KEYS: {len(tropical)} entries")

    inject_into_core_js(fiche, tropical)
    print(f"✅ Updated {CORE_JS}")


if __name__ == '__main__':
    main()
