#!/usr/bin/env python3
"""
Applique aux pages déjà publiées les corrections de libellés du gabarit V6,
sans régénérer le reste de la page :
  - type de climat calculé selon Köppen (lib/koppen.py) au lieu de l'ancien
    libellé « côtier = tempéré océanique » ;
  - mini-cartes de l'en-tête traduites (« Plus rude » apparaissait en
    anglais, espagnol et allemand) et abréviations de mois sans collision
    (« Jui » pour juin et pour juillet) ;
  - préfixe du crédit photo traduit (« Photo par » sur les pages EN, ES, DE).

Méthode : la page est recalculée en mémoire avec le générateur actuel, puis
comparée ligne à ligne à la page publiée. Une ligne n'est remplacée que si
la seule différence entre les deux versions est l'une des corrections
ci-dessus (contrôle par substitution inverse). Toute autre différence
(données, liens hreflang, sections ajoutées après coup) est laissée telle
quelle et comptée.

Usage :
    python3 scripts/apply_hero_fixes.py --dry-run [--kind annual|monthly] [--langs fr,en] [--only slug1,slug2]
    python3 scripts/apply_hero_fixes.py --kind annual --langs fr [--autorise]
"""
import csv
import difflib
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import generate_pages as G  # noqa: E402
from lib.koppen import climate_label  # noqa: E402
from lib.v6_adapter import _build_climate_type, _bool, gen_annual_v6, gen_monthly_v6  # noqa: E402

LANGS = ['fr', 'en', 'en-us', 'es', 'de']
FREEZE = 1500
OLD_MINI = ('Top score', 'Alt.', 'Plus rude', 'Top ski', 'Top rando', 'Transition')
NEW_MINI = {
    'fr':    ('Meilleur mois', 'Alternative', 'Plus rude', 'Meilleur ski', 'Meilleure rando', 'Transition'),
    'en':    ('Best month', 'Runner-up', 'Toughest', 'Best for skiing', 'Best for hiking', 'Shoulder season'),
    'en-us': ('Best month', 'Runner-up', 'Toughest', 'Best for skiing', 'Best for hiking', 'Shoulder season'),
    'es':    ('Mejor mes', 'Alternativa', 'Más duro', 'Mejor para esquiar', 'Mejor para senderismo', 'Transición'),
    'de':    ('Bester Monat', 'Alternative', 'Schwierigster', 'Bester Skimonat', 'Bester Wandermonat', 'Übergangszeit'),
}
NEW_PREFIX = {'annual': {'en': 'Photo by', 'en-us': 'Photo by', 'es': 'Foto de', 'de': 'Foto von'},
              'monthly': {'en': 'Photo:', 'en-us': 'Photo:', 'es': 'Foto:', 'de': 'Foto:'}}
OLD_PREFIX = {'annual': 'Photo par', 'monthly': 'Photo :'}


def norm_fr_months(s):
    return s.replace('Juin', 'Jui').replace('Juil', 'Jui')


def acceptable(old, new, subs):
    """Vrai si new ne diffère de old que par les substitutions attendues,
    vérifié dans un sens ou dans l'autre (un libellé peut en contenir un autre :
    « Subarctic » dans « Subarctic oceanic »)."""
    back, fwd = new, old
    for n, o in subs:
        if n != o:
            back = back.replace(n, o)
            fwd = fwd.replace(o, n)
    return norm_fr_months(back) == norm_fr_months(old) or norm_fr_months(fwd) == norm_fr_months(new)


def patch(old_html, new_html, subs):
    a, b = old_html.split('\n'), new_html.split('\n')
    out, changed, refused = list(a), 0, 0
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag != 'replace' or (i2 - i1) != (j2 - j1):
            continue
        for k in range(i2 - i1):
            o, n = a[i1 + k], b[j1 + k]
            if acceptable(o, n, subs):
                out[i1 + k] = n
                changed += 1
            else:
                refused += 1
    return '\n'.join(out), changed, refused


def main():
    args = sys.argv[1:]
    dry = '--dry-run' in args
    kind = args[args.index('--kind') + 1] if '--kind' in args else 'annual'
    langs = args[args.index('--langs') + 1].split(',') if '--langs' in args else LANGS
    only = set(args[args.index('--only') + 1].split(',')) if '--only' in args else None
    edits, stats = {}, Counter()
    refused_pages = []
    for lang in langs:
        cfg = G.build_config(lang)
        fn = G._bind_lang(cfg)
        dests, climate, cards, overrides, events, photos = G.load_data(cfg)
        sims = G.compute_all_similarities(dests, climate)
        xlinks = G.compute_monthly_crosslinks(dests, climate) if kind == 'monthly' else None
        comp = G.build_comparison_index(cfg)
        out_dir = ROOT / cfg['out_subdir'] if cfg['out_subdir'] else ROOT
        for slug_key, dest in dests.items():
            if only and slug_key not in only:
                continue
            months = climate.get(slug_key)
            if not months or None in months:
                continue
            dest['_photo'] = photos.get(slug_key, {})
            lat = float(dest.get('lat') or 0)
            old_cl = _build_climate_type(dest, lat, lang)
            new_cl = climate_label(months, lat, lang, _bool(dest.get('mountain'))) or old_cl
            subs = [(new_cl, old_cl)]
            pre_new = NEW_PREFIX[kind].get(lang)
            if pre_new:
                subs.append((f'>{pre_new} <', f'>{OLD_PREFIX[kind]} <'))
            subs += [(f'>{n} (', f'>{o} (') for n, o in zip(NEW_MINI.get(lang, NEW_MINI['fr']), OLD_MINI)]
            subs.append((f'>{NEW_MINI.get(lang, NEW_MINI["fr"])[5]}<', '>Transition<'))
            slug = G.dest_slug(cfg, dest)
            jobs = [(out_dir / G.annual_url(cfg, slug), lambda: gen_annual_v6(cfg, fn, dest, months, cards.get(slug_key, []), dests, sims, comp))]
            if kind == 'monthly':
                if dest.get('monthly', 'True').strip().lower() not in ('true', '1', 'yes', ''):
                    continue
                jobs = [(out_dir / G.monthly_url(cfg, slug, mi),
                         (lambda mi=mi: gen_monthly_v6(cfg, fn, dest, months, mi, dests, sims, comp, climate, xlinks)))
                        for mi in range(12)]
            for f, make in jobs:
                if not f.exists():
                    continue
                try:
                    new_html = G.to_canonical_links(make())
                except Exception as e:  # noqa: BLE001
                    stats['erreurs de génération'] += 1
                    print(f'  ⚠️ {f.relative_to(ROOT)} : {e}')
                    continue
                old_html = f.read_text(encoding='utf-8')
                html, n_ok, n_ref = patch(old_html, new_html, subs)
                stats['lignes refusées'] += n_ref
                if n_ref and len(refused_pages) < 8:
                    refused_pages.append(str(f.relative_to(ROOT)))
                if html != old_html:
                    edits[f] = html
                    stats[f'pages {lang}'] += 1
                    stats['lignes corrigées'] += n_ok
                    if old_cl != new_cl:
                        stats['type de climat changé'] += 1
    print(('[essai] ' if dry else '') + f'{len(edits)} pages modifiées ; ' + ' ; '.join(f'{k} : {v}' for k, v in stats.items()))
    if refused_pages:
        print('  exemples de pages avec lignes non reprises :', refused_pages)
    if len(edits) > FREEZE and '--autorise' not in args:
        sys.exit(f'Plus de {FREEZE} pages : réduire (--langs, --only) ou --autorise après accord de Gilles.')
    if not dry:
        for f, t in edits.items():
            f.write_text(t, encoding='utf-8')


if __name__ == '__main__':
    main()
