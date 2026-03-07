#!/usr/bin/env python3
"""
check_locale.py — Audit i18n locale consistency across all language files.

Usage:
    python check_locale.py            # check all locales, exit 1 if errors
    python check_locale.py --fix      # show missing keys with FR values as template
    python check_locale.py --verbose  # show passing checks too

Exit codes:
    0 — all locales consistent
    1 — missing keys found (blocks commit when used as git hook)
"""
import json, sys, os, argparse
from pathlib import Path
from collections import defaultdict

LOCALES_DIR = Path(__file__).parent / 'locales'
REFERENCE_LANG = 'fr'

# ── Allowlisted asymmetries ───────────────────────────────────────────────────
# These keys are legitimately different across locales by design.
ALLOWED_ASYMMETRIES = {
    # season_months / season_range are keyed by season name IN THAT LANGUAGE
    # (fr: Été/Hiver/Printemps/Automne, en: Summer/Winter/Spring/Autumn, es: Verano/...)
    # → structural asymmetry by design, not a bug
    'season_months',
    'season_range',
}

def is_allowed(key):
    """Return True if this key is in an allowlisted section."""
    top = key.split('.')[0].split('[')[0]
    return top in ALLOWED_ASYMMETRIES


# ── Flatten ───────────────────────────────────────────────────────────────────
def flatten(obj, prefix=''):
    """Flatten nested dict/list to dot-notation leaf keys."""
    items = {}
    if isinstance(obj, dict):
        for k, v in obj.items():
            items.update(flatten(v, f"{prefix}.{k}" if prefix else k))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            items.update(flatten(v, f"{prefix}[{i}]"))
    else:
        items[prefix] = obj
    return items


def section_keys(flat_keys):
    """Return set of top-level section names."""
    return {k.split('.')[0].split('[')[0] for k in flat_keys}


# ── Load locales ──────────────────────────────────────────────────────────────
def load_locales():
    locales = {}
    for path in sorted(LOCALES_DIR.glob('*.json')):
        lang = path.stem
        with open(path, encoding='utf-8') as f:
            locales[lang] = json.load(f)
    return locales


# ── Core check ───────────────────────────────────────────────────────────────
def check(verbose=False, fix=False):
    locales = load_locales()
    if REFERENCE_LANG not in locales:
        print(f"❌ Reference locale '{REFERENCE_LANG}' not found in {LOCALES_DIR}")
        return 1

    flat = {lang: flatten(loc) for lang, loc in locales.items()}
    ref_keys = set(flat[REFERENCE_LANG].keys())
    other_langs = [l for l in flat if l != REFERENCE_LANG]

    errors = defaultdict(list)   # lang → [missing_key, ...]
    warnings = defaultdict(list) # lang → [extra_key, ...]

    for lang in other_langs:
        lang_keys = set(flat[lang].keys())

        # Missing in lang vs reference
        for k in sorted(ref_keys - lang_keys):
            if not is_allowed(k):
                errors[lang].append(k)

        # Extra in lang vs reference (less critical — warn only)
        for k in sorted(lang_keys - ref_keys):
            if not is_allowed(k):
                warnings[lang].append(k)

    # ── Output ───────────────────────────────────────────────────────────────
    total_errors = sum(len(v) for v in errors.values())
    total_warnings = sum(len(v) for v in warnings.values())

    print(f"BestDateWeather locale check — reference: {REFERENCE_LANG}")
    print(f"Locales found: {', '.join(sorted(flat.keys()))}")
    print(f"Reference keys: {len(ref_keys)}")
    print()

    if not errors and not warnings:
        print("✅ All locales consistent.")
        return 0

    # Group by section for readability
    for lang in sorted(errors.keys()):
        missing = errors[lang]
        by_section = defaultdict(list)
        for k in missing:
            section = k.split('.')[0].split('[')[0]
            by_section[section].append(k)

        print(f"❌ [{lang}] {len(missing)} missing key(s):")
        for section in sorted(by_section.keys()):
            keys = by_section[section]
            print(f"   [{section}] {len(keys)} key(s):")
            for k in keys:
                ref_val = flat[REFERENCE_LANG].get(k, '')
                if fix:
                    print(f"      {k}")
                    print(f"        FR value: {repr(ref_val)}")
                else:
                    short_val = repr(ref_val)[:60] + ('…' if len(repr(ref_val)) > 60 else '')
                    print(f"      {k}  (FR: {short_val})")
        print()

    for lang in sorted(warnings.keys()):
        extras = warnings[lang]
        if extras:
            by_section = defaultdict(list)
            for k in extras:
                section = k.split('.')[0].split('[')[0]
                by_section[section].append(k)
            print(f"⚠️  [{lang}] {len(extras)} extra key(s) not in {REFERENCE_LANG} (won't break anything):")
            for section in sorted(by_section.keys()):
                keys = by_section[section]
                print(f"   [{section}]: {', '.join(keys[:5])}{'…' if len(keys)>5 else ''}")
            print()

    print(f"Summary: {total_errors} error(s), {total_warnings} warning(s)")
    if total_errors:
        print(f"→ Add missing keys to non-FR locales before committing.")
    return 1 if total_errors else 0


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Check locale key consistency')
    parser.add_argument('--fix', action='store_true', help='Show FR values as copy template')
    parser.add_argument('--verbose', action='store_true', help='Show passing checks too')
    args = parser.parse_args()
    sys.exit(check(verbose=args.verbose, fix=args.fix))
