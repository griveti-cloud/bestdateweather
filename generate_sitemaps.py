#!/usr/bin/env python3
"""
Sitemaps = exactement l'ensemble indexable défini par lib/indexation.py.

Plan B (octobre 2026) : plus de sitemap construit par motifs de fichiers ; une
seule source de vérité partagée avec apply_indexation.py et check_deploy.py.
Le lastmod est la date RÉELLE de dernière modification du contenu
(data/data_version.json), pas la date du build.

Fichiers produits :
    sitemap-pages-fr.xml, sitemap-pages-en.xml, sitemap-pages-intl.xml
    sitemap-index.xml (référencé par robots.txt) et sitemap.xml (même contenu)
"""
import glob
import os

from lib.indexation import indexable_paths, lang_of
from lib.page_config import DATA_UPDATED

BASE = 'https://bestdateweather.com'
GROUPS = {'fr': 'sitemap-pages-fr.xml', 'en': 'sitemap-pages-en.xml', 'intl': 'sitemap-pages-intl.xml'}


def loc(path: str) -> str:
    return f'{BASE}/{path}' if path else BASE + '/'


def main():
    paths = sorted(indexable_paths())
    buckets = {k: [] for k in GROUPS}
    for p in paths:
        lang = lang_of(p)
        buckets['fr' if lang == 'fr' else 'en' if lang == 'en' else 'intl'].append(p)

    # Anciens sitemaps segmentés (priority/secondary) : supprimés
    for old in glob.glob('sitemap-*-priority.xml') + glob.glob('sitemap-*-secondary.xml'):
        os.remove(old)
        print(f'  supprimé : {old}')

    written = []
    for key, fn in GROUPS.items():
        urls = buckets[key]
        if not urls:
            if os.path.exists(fn):
                os.remove(fn)
            continue
        lines = ['<?xml version="1.0" encoding="UTF-8"?>',
                 '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
        for p in urls:
            lines.append(f'  <url><loc>{loc(p)}</loc><lastmod>{DATA_UPDATED}</lastmod></url>')
        lines.append('</urlset>')
        with open(fn, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines) + '\n')
        written.append(fn)
        print(f'✓ {fn} : {len(urls)} URL')

    idx = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for fn in written:
        idx.append(f'  <sitemap><loc>{BASE}/{fn}</loc><lastmod>{DATA_UPDATED}</lastmod></sitemap>')
    idx.append('</sitemapindex>')
    for fn in ('sitemap-index.xml', 'sitemap.xml'):
        with open(fn, 'w', encoding='utf-8') as f:
            f.write('\n'.join(idx) + '\n')
    print(f'✓ sitemap-index.xml et sitemap.xml : {len(written)} sitemaps, {len(paths)} URL au total')


if __name__ == '__main__':
    main()
