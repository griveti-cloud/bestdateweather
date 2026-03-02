#!/usr/bin/env python3
"""
prepare_booking_script.py
=========================
Generates the browser console script with embedded destination data.

Usage:
    python3 scripts/prepare_booking_script.py > scripts/fetch_booking_ids_ready.js

Then paste the output into the browser console on https://www.booking.com
"""
import csv, json, os

DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(DIR, 'data', 'destinations.csv')
TEMPLATE = os.path.join(DIR, 'scripts', 'fetch_booking_ids.js')

# Load missing destinations
with open(CSV_PATH, encoding='utf-8-sig') as f:
    dests = list(csv.DictReader(f))

missing = [d for d in dests if not d.get('booking_dest_id', '').strip()]
entries = []
for d in missing:
    name = d.get('nom_en', d.get('nom_bare', d['slug_fr']))
    country = d.get('country_en', '')
    entries.append({'s': d['slug_fr'], 'q': f"{name}, {country}"})

# Read template and inject data
with open(TEMPLATE) as f:
    script = f.read()

script = script.replace('PLACEHOLDER_DESTINATIONS', json.dumps(entries, ensure_ascii=False))
print(script)
print(f"\n// {len(entries)} destinations to resolve", file=__import__('sys').stderr)
