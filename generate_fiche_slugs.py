#!/usr/bin/env python3
"""
generate_fiche_slugs.py
-----------------------
Regenerate js/fiche-slugs.js from data/destinations.csv.

Each destination gets:
  - slug_fr as canonical key  → {fr, en, es}
  - slug_en as alias          → {fr, en, es}  (if different from slug_fr)
  - slug_es as alias          → {fr, en, es}  (if different from slug_fr and slug_en)
  - each token in 'aliases' field → same entry

Existing non-CSV aliases (manually added regional/alternate names like
"les canaries", "iles canaries", etc.) are PRESERVED from the existing file,
provided they still point to a valid destination.

Usage:
    python3 generate_fiche_slugs.py [--dry-run]
"""

import csv, json, re, os, sys, unicodedata, argparse

DEST_CSV   = 'data/destinations.csv'
SLUGS_JS   = 'js/fiche-slugs.js'
SLUGS_MINJS = 'js/fiche-slugs.min.js'
PREFIX     = '/* Auto-generated — do not edit manually */\nwindow.BDW_FICHE_SLUGS = '


def normalize(s: str) -> str:
    """Lowercase, strip accents, collapse non-alphanum to single hyphen."""
    s = s.lower().strip()
    s = unicodedata.normalize('NFD', s)
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    s = re.sub(r'[^a-z0-9]+', '-', s).strip('-')
    return s


def load_existing(path: str) -> dict:
    if not os.path.exists(path):
        return {}
    content = open(path, encoding='utf-8').read()
    if not content.startswith(PREFIX):
        return {}
    json_str = content[len(PREFIX):].rstrip()
    if json_str.endswith(';'):
        json_str = json_str[:-1]
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        return {}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()

    rows = list(csv.DictReader(open(DEST_CSV, encoding='utf-8-sig')))
    valid_slugs_fr = {r['slug_fr'] for r in rows}

    # Build target map: key → {fr, en, es}
    data: dict = {}

    for r in rows:
        sf = r['slug_fr']
        se = r['slug_en']
        ss = r['slug_es']
        entry = {'fr': sf, 'en': se, 'es': ss}

        # Canonical: slug_fr
        data[sf] = entry

        # Cross-lang aliases (only if different, avoid overwriting more specific entry)
        for alias in [se, ss]:
            if alias and alias not in data:
                data[alias] = entry

        # Aliases field (space-separated)
        for alias in r.get('aliases', '').split():
            alias = alias.strip()
            if alias and alias not in data:
                data[alias] = entry
            # Also add normalized version
            alias_norm = normalize(alias)
            if alias_norm and alias_norm not in data:
                data[alias_norm] = entry

    # Preserve non-CSV aliases from existing file (manual regional names etc.)
    existing = load_existing(SLUGS_JS)
    preserved = 0
    for key, entry in existing.items():
        if key in data:
            continue  # already covered
        # Only keep if it still points to a valid slug_fr
        if entry.get('fr') in valid_slugs_fr:
            data[key] = entry
            preserved += 1

    # Verify: all slug_fr covered
    missing = [r['slug_fr'] for r in rows if r['slug_fr'] not in {e['fr'] for e in data.values()}]

    print(f"Destinations: {len(rows)}")
    print(f"Total entries: {len(data)}")
    print(f"Preserved manual aliases: {preserved}")
    print(f"Missing slug_fr: {len(missing)}")
    if missing:
        print(f"  {missing}")
        sys.exit(1)

    output = PREFIX + json.dumps(data, ensure_ascii=False, separators=(',', ': ')) + ';\n'

    if args.dry_run:
        print("Dry run — no files written.")
        return

    open(SLUGS_JS, 'w', encoding='utf-8').write(output)
    open(SLUGS_MINJS, 'w', encoding='utf-8').write(output)
    print(f"Written: {SLUGS_JS} + {SLUGS_MINJS}")


if __name__ == '__main__':
    main()
