#!/usr/bin/env python3
"""Génère js/dest-data.js depuis data/destinations.csv (inclut aliases)."""
import csv, json, sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
CSV  = ROOT / 'data' / 'destinations.csv'
OUT  = ROOT / 'js' / 'dest-data.js'

LANGS = ['fr','en','es','de']

data = {}
with open(CSV, encoding='utf-8-sig') as f:
    for row in csv.DictReader(f):
        slug = row['slug_fr']
        entry = {
            'fr': row['nom_fr'],
            'en': row['nom_en'],
            'es': row['nom_es'],
            'de': row['nom_de'],
            'flag': row['flag'],
            'slugs': {
                'fr':    row['slug_fr'],
                'en':    row['slug_en'],
                'es':    row['slug_es'],
                'de':    row['slug_de'],
                'en-us': row['slug_en'],  # same as en
            },
        }
        aliases_raw = row.get('aliases','').strip()
        if aliases_raw:
            entry['aliases'] = aliases_raw.split()
        data[slug] = entry

js = 'window.BDW_DEST_DATA=' + json.dumps(data, ensure_ascii=False, separators=(',',':')) + ';'
OUT.write_text(js, encoding='utf-8')
print(f'✅ {len(data)} destinations → {OUT}')
