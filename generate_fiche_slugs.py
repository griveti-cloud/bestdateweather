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

Also written (20 Nov 2026), used by js/core.js (bdwFicheFor) to link a searched
place to a guide:
  - destination names in the 5 languages as extra keys (the geocoder returns
    names, not slugs: "Grande Canarie", "Teneriffa"...);
  - window.BDW_FICHE_SLUGS = {key: slug_fr} (was {key: {fr, en, es}} before 20 Nov 2026);
  - window.BDW_FICHE_DEST = {slug_fr: [lat, lon, flag, nom_fr, nom_en, nom_es, nom_de,
    slug_en, slug_es, slug_de]}: names left empty when identical to nom_fr, slug_en empty
    when identical to slug_fr, slug_es and slug_de empty when identical to slug_en.
    Used for the URLs, the country check and the nearest-destination fallback
    (Maspalomas -> Gran Canaria, 26 km).
Keys use the same normalisation as bdwFicheNorm() in js/core.js.

Usage:
    python3 generate_fiche_slugs.py [--dry-run]
    then: npx terser js/fiche-slugs.js --compress --mangle -o js/fiche-slugs.min.js
"""

import csv, json, re, os, sys, unicodedata, argparse

DEST_CSV   = 'data/destinations.csv'
SLUGS_JS   = 'js/fiche-slugs.js'
SLUGS_MINJS = 'js/fiche-slugs.min.js'
PREFIX     = '/* Auto-generated — do not edit manually */\nwindow.BDW_FICHE_SLUGS = '
DEST_PREFIX = 'window.BDW_FICHE_DEST = '


SPECIAL = {'đ': 'd', 'ø': 'o', 'ł': 'l', 'æ': 'ae', 'œ': 'oe', 'ß': 'ss', 'ı': 'i'}


def normalize(s: str) -> str:
    """Lowercase, strip accents, collapse non-alphanum to single hyphen.
    Must stay identical to bdwFicheNorm() in js/core.js."""
    s = s.lower().strip()
    s = ''.join(SPECIAL.get(c, c) for c in s)
    s = unicodedata.normalize('NFD', s)
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    s = re.sub(r'[^a-z0-9]+', '-', s).strip('-')
    return s


# Tokens trop génériques pour être des clés de lookup fiables
# (évite que "saint-nazaire" → les-arcs à cause de l'alias "bourg saint maurice")
GENERIC_TOKENS = {
    'saint', 'sainte', 'mer', 'val', 'lac', 'ile', 'les', 'mont', 'arc',
    'bourg', 'ville', 'city', 'ski', 'new', 'big', 'sur', 'way', 'du',
    'd', 'la', 'le', 'de', 'en', 'et', 'des', 'les', 'au', 'aux',
    'blanc', 'mont', 'plage', 'station', 'resort', 'hotel', 'village',
}


def load_existing(path: str) -> dict:
    if not os.path.exists(path):
        return {}
    content = open(path, encoding='utf-8').read()
    if not content.startswith(PREFIX):
        return {}
    json_str = content[len(PREFIX):].split('\n')[0].rstrip()
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

    def entry_of(r):
        return r['slug_fr']

    # Names in the 5 languages (after slugs, before aliases; never overwrite)
    name_keys = []
    for r in rows:
        for k in ('nom_bare', 'nom_en', 'nom_es', 'nom_de'):
            for part in (r.get(k) or '').split('/'):
                key = normalize(part)
                if key and key not in GENERIC_TOKENS and len(key) > 2:
                    name_keys.append((key, r))

    for r in rows:
        sf = r['slug_fr']
        se = r['slug_en']
        ss = r['slug_es']
        entry = entry_of(r)

        # Canonical: slug_fr
        data[sf] = entry

        # Cross-lang aliases (only if different, avoid overwriting more specific entry)
        for alias in [se, ss]:
            if alias and alias not in data:
                data[alias] = entry

    # Destination names: slugs keep priority over names, names over aliases
    for key, r in name_keys:
        if key not in data:
            data[key] = entry_of(r)

    for r in rows:
        entry = data[r['slug_fr']]
        # Aliases field (space-separated)
        for alias in r.get('aliases', '').split():
            alias = alias.strip()
            alias_norm = normalize(alias)
            # Skip tokens that are too generic to be reliable lookup keys
            if alias_norm in GENERIC_TOKENS or len(alias_norm) <= 2:
                continue
            if alias and alias not in data:
                data[alias] = entry
            if alias_norm and alias_norm not in data:
                data[alias_norm] = entry

    # Preserve non-CSV aliases from existing file (manual regional names etc.)
    existing = load_existing(SLUGS_JS)
    preserved = 0
    for key, entry in existing.items():
        if key in data:
            continue  # already covered
        # Skip generic tokens even if manually added
        if key in GENERIC_TOKENS or len(key) <= 2:
            continue
        # Only keep if it still points to a valid slug_fr
        if (entry if isinstance(entry, str) else entry.get('fr')) in valid_slugs_fr:
            data[key] = entry if isinstance(entry, str) else entry['fr']
            preserved += 1

    # Verify: all slug_fr covered
    missing = [r['slug_fr'] for r in rows if r['slug_fr'] not in set(data.values())]

    print(f"Destinations: {len(rows)}")
    print(f"Total entries: {len(data)}")
    print(f"Preserved manual aliases: {preserved}")
    print(f"Missing slug_fr: {len(missing)}")
    if missing:
        print(f"  {missing}")
        sys.exit(1)

    dest = {}
    for r in rows:
        names = [(r.get(k) or '').split('/')[0].strip() for k in ('nom_bare', 'nom_en', 'nom_es', 'nom_de')]
        sf, se = r['slug_fr'], r['slug_en'] or r['slug_fr']
        slugs = [se if se != sf else '',
                 r['slug_es'] if r.get('slug_es') and r['slug_es'] != se else '',
                 r['slug_de'] if r.get('slug_de') and r['slug_de'] != se else '']
        dest[sf] = ([round(float(r['lat']), 3), round(float(r['lon']), 3), (r.get('flag') or '').lower(), names[0]]
                    + [n if n != names[0] else '' for n in names[1:]] + slugs)

    output = (PREFIX + json.dumps(data, ensure_ascii=False, separators=(',', ':')) + ';\n'
              + DEST_PREFIX + json.dumps(dest, ensure_ascii=False, separators=(',', ':')) + ';\n')

    if args.dry_run:
        print("Dry run — no files written.")
        return

    open(SLUGS_JS, 'w', encoding='utf-8').write(output)
    print(f"Written: {SLUGS_JS} (minify to {SLUGS_MINJS} with terser)")


if __name__ == '__main__':
    main()
