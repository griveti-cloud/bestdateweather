#!/usr/bin/env python3
"""
Vérifie la cohérence des clés entre les 5 locales.
Usage : python3 scripts/check_locale.py
Retourne exit code 1 si des clés critiques manquent.
"""
import json, sys
from pathlib import Path

LOCALES_DIR = Path(__file__).parent.parent / 'locales'
LANGS = ['fr', 'en', 'en-us', 'es', 'de']

LANG_SPECIFIC = {
    'fr': {'season_months.Printemps','season_months.Été','season_months.Automne','season_months.Hiver',
           'season_range.Printemps','season_range.Été','season_range.Automne','season_range.Hiver'},
    'en': {'season_months.Spring','season_months.Summer','season_months.Autumn','season_months.Winter',
           'season_range.Spring','season_range.Summer','season_range.Autumn','season_range.Winter'},
    'en-us': {'season_months.Spring','season_months.Summer','season_months.Autumn','season_months.Winter',
              'season_range.Spring','season_range.Summer','season_range.Autumn','season_range.Winter'},
    'es': {'season_months.Primavera','season_months.Verano','season_months.Otoño','season_months.Invierno',
           'season_range.Primavera','season_range.Verano','season_range.Otoño','season_range.Invierno'},
    'de': {'season_months.Frühling','season_months.Sommer','season_months.Herbst','season_months.Winter',
           'season_range.Frühling','season_range.Sommer','season_range.Herbst','season_range.Winter',
           'classement_pages.beach.de_file','classement_pages.caraibes.de_file',
           'classement_pages.ete.de_file','classement_pages.europe.de_file',
           'classement_pages.hiver.de_file','classement_pages.mondial.de_file',
           'classement_pages.nomades.de_file'},
}

CRITICAL_KEYS = {
    'annual_hero_subs_ski', 'context_paragraphs_ski', 'monthly_hero_subs_ski',
    'labels.best_ski_months_lbl_tpl', 'monthly.sec_similar_ski_tpl', 'monthly.sim_label_ski',
    'pilier.sec_title_meteo', 'pilier.sec_title_beach', 'pilier.sec_title_ski',
}

def get_all_keys(d, prefix=''):
    keys = set()
    for k, v in d.items():
        full = f'{prefix}.{k}' if prefix else k
        keys.add(full)
        if isinstance(v, dict):
            keys |= get_all_keys(v, full)
    return keys

def main():
    locales = {}
    for lang in LANGS:
        with open(LOCALES_DIR / f'{lang}.json', encoding='utf-8') as f:
            locales[lang] = json.load(f)
    key_sets = {l: get_all_keys(locales[l]) for l in LANGS}
    all_keys = set().union(*key_sets.values())
    errors, warnings = [], []

    for key in sorted(CRITICAL_KEYS):
        for lang in LANGS:
            if key not in key_sets[lang]:
                errors.append(f"[{lang}] Clé critique manquante: {key}")

    langs_xdefault = [l for l in LANGS if 'meta.x_default' in key_sets[l]]
    if len(langs_xdefault) != 1:
        errors.append(f"meta.x_default doit être dans exactement 1 locale, trouvé dans: {langs_xdefault}")

    ref_keys = key_sets['fr']
    for lang in ['en','en-us','es','de']:
        specific = LANG_SPECIFIC.get(lang,set()) | LANG_SPECIFIC.get('fr',set())
        missing = ref_keys - key_sets[lang] - specific
        for k in sorted(missing):
            warnings.append(f"[{lang}] Clé FR manquante: {k}")

    print(f"Audit locales — {len(LANGS)} langues, {len(all_keys)} clés total\n")
    for lang in LANGS:
        xd = '✓ x-default' if 'meta.x_default' in key_sets[lang] else ''
        print(f"  {lang:6}: {len(key_sets[lang]):3} clés  {xd}")

    if errors:
        print(f"\n❌ ERREURS ({len(errors)}):")
        for e in errors: print(f"  {e}")
    if warnings:
        print(f"\n⚠️  AVERTISSEMENTS ({len(warnings)}):")
        for w in warnings[:20]: print(f"  {w}")
    if not errors and not warnings:
        print("\n✅ Toutes les locales sont cohérentes")
    return 1 if errors else 0

if __name__ == '__main__':
    sys.exit(main())
