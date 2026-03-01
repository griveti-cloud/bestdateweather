#!/usr/bin/env python3
"""
Génère sitemap-fr.xml et sitemap-en.xml à partir des fichiers HTML réels.

Source de vérité : les fichiers .html présents sur le disque.
Mapping FR↔EN : lu depuis data/destinations.csv pour les hreflang.
Pages statiques : définies dans STATIC_PAGES.

Usage:
    python scripts/generate_sitemaps.py          # génère les deux sitemaps
    python scripts/generate_sitemaps.py --dry-run # affiche sans écrire
"""

import csv
import glob
import os
import sys
from datetime import date

DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_URL = 'https://bestdateweather.com'
TODAY = date.today().isoformat()

# ── Pages statiques avec leur mapping FR↔EN ──────────────────────────────
STATIC_PAGES_FR = {
    'index.html':            ('index.html', 'en/app.html', 1.0),
    'methodologie.html':     ('methodologie.html', 'en/methodology.html', 0.5),
    'mentions-legales.html': ('mentions-legales.html', 'en/legal.html', 0.3),
    'confidentialite.html':  ('confidentialite.html', 'en/privacy.html', 0.3),
    'contact.html':          ('contact.html', 'en/contact.html', 0.3),
}

STATIC_PAGES_EN = {
    'en/app.html':          ('en/app.html', 'index.html', 0.9),
    'en/methodology.html':  ('en/methodology.html', 'methodologie.html', 0.5),
    'en/legal.html':        ('en/legal.html', 'mentions-legales.html', 0.3),
    'en/privacy.html':      ('en/privacy.html', 'confidentialite.html', 0.3),
    'en/contact.html':      ('en/contact.html', 'contact.html', 0.3),
}

MONTHS_FR = ['janvier','fevrier','mars','avril','mai','juin',
             'juillet','aout','septembre','octobre','novembre','decembre']
MONTHS_EN = ['january','february','march','april','may','june',
             'july','august','september','october','november','december']


def load_slug_mapping():
    """Charge le mapping slug_fr → slug_en depuis destinations.csv."""
    mapping = {}
    csv_path = os.path.join(DIR, 'data', 'destinations.csv')
    with open(csv_path, encoding='utf-8-sig') as f:
        for row in csv.DictReader(f):
            mapping[row['slug_fr'].strip()] = row['slug_en'].strip()
    return mapping


def find_fr_pages():
    """Trouve toutes les pages FR destination (annual + monthly)."""
    pages = []
    for f in sorted(glob.glob(os.path.join(DIR, 'meilleure-periode-*.html'))):
        pages.append(os.path.basename(f))
    for f in sorted(glob.glob(os.path.join(DIR, '*-meteo-*.html'))):
        pages.append(os.path.basename(f))
    return pages


def find_en_pages():
    """Trouve toutes les pages EN destination (annual + monthly)."""
    pages = []
    for f in sorted(glob.glob(os.path.join(DIR, 'en', 'best-time-to-visit-*.html'))):
        pages.append('en/' + os.path.basename(f))
    for f in sorted(glob.glob(os.path.join(DIR, 'en', '*-weather-*.html'))):
        pages.append('en/' + os.path.basename(f))
    return pages


def find_ranking_pages():
    """Trouve les pages classement/ranking FR et EN."""
    fr = sorted(glob.glob(os.path.join(DIR, 'classement-*.html')))
    en = sorted(glob.glob(os.path.join(DIR, 'en', 'best-*-ranking-*.html')))
    return [os.path.basename(f) for f in fr], ['en/' + os.path.basename(f) for f in en]


def find_comparison_pages():
    """Trouve les pages comparatif/comparison FR et EN."""
    fr = sorted(glob.glob(os.path.join(DIR, 'comparatif-*.html')))
    en = sorted(glob.glob(os.path.join(DIR, 'en', 'compare-*.html')))
    return [os.path.basename(f) for f in fr], ['en/' + os.path.basename(f) for f in en]


def find_pillar_pages():
    """Trouve les pages pilier/pillar FR et EN."""
    fr = sorted(glob.glob(os.path.join(DIR, 'quand-partir-*.html')))
    en = sorted(glob.glob(os.path.join(DIR, 'en', 'when-to-visit-*.html')))
    return [os.path.basename(f) for f in fr], ['en/' + os.path.basename(f) for f in en]


def get_en_counterpart(fr_file, slug_map):
    """Trouve la page EN correspondant à une page FR destination."""
    basename = fr_file

    # Annual page: meilleure-periode-{slug_fr}.html → en/best-time-to-visit-{slug_en}.html
    if basename.startswith('meilleure-periode-'):
        slug_fr = basename.replace('meilleure-periode-', '').replace('.html', '')
        slug_en = slug_map.get(slug_fr)
        if slug_en:
            en_file = f'en/best-time-to-visit-{slug_en}.html'
            if os.path.exists(os.path.join(DIR, en_file)):
                return en_file
        return None

    # Monthly page: {slug_fr}-meteo-{mois_fr}.html → en/{slug_en}-weather-{month_en}.html
    for i, mois in enumerate(MONTHS_FR):
        suffix = f'-meteo-{mois}.html'
        if basename.endswith(suffix):
            slug_fr = basename.replace(suffix, '')
            slug_en = slug_map.get(slug_fr)
            if slug_en:
                en_file = f'en/{slug_en}-weather-{MONTHS_EN[i]}.html'
                if os.path.exists(os.path.join(DIR, en_file)):
                    return en_file
            return None

    return None


def get_fr_counterpart(en_file, slug_map):
    """Trouve la page FR correspondant à une page EN destination."""
    basename = en_file.replace('en/', '')
    reverse_map = {v: k for k, v in slug_map.items()}

    # Annual
    if basename.startswith('best-time-to-visit-'):
        slug_en = basename.replace('best-time-to-visit-', '').replace('.html', '')
        slug_fr = reverse_map.get(slug_en)
        if slug_fr:
            fr_file = f'meilleure-periode-{slug_fr}.html'
            if os.path.exists(os.path.join(DIR, fr_file)):
                return fr_file
        return None

    # Monthly
    for i, month in enumerate(MONTHS_EN):
        suffix = f'-weather-{month}.html'
        if basename.endswith(suffix):
            slug_en = basename.replace(suffix, '')
            slug_fr = reverse_map.get(slug_en)
            if slug_fr:
                fr_file = f'{slug_fr}-meteo-{MONTHS_FR[i]}.html'
                if os.path.exists(os.path.join(DIR, fr_file)):
                    return fr_file
            return None

    return None


def make_url_entry(loc, hreflang_fr=None, hreflang_en=None, priority=0.8,
                   changefreq='monthly', lastmod=None):
    """Génère un bloc <url> XML."""
    lm = lastmod or TODAY
    lines = ['  <url>']
    lines.append(f'    <loc>{BASE_URL}/{loc}</loc>')
    lines.append(f'    <lastmod>{lm}</lastmod>')
    lines.append(f'    <changefreq>{changefreq}</changefreq>')
    lines.append(f'    <priority>{priority}</priority>')
    if hreflang_fr:
        lines.append(f'    <xhtml:link rel="alternate" hreflang="fr" href="{BASE_URL}/{hreflang_fr}" />')
    if hreflang_en:
        lines.append(f'    <xhtml:link rel="alternate" hreflang="en" href="{BASE_URL}/{hreflang_en}" />')
    lines.append('  </url>')
    return '\n'.join(lines)


def generate_sitemap(lang, dry_run=False):
    """Génère le sitemap pour la langue donnée."""
    slug_map = load_slug_mapping()

    entries = []

    # 1. Pages statiques
    static = STATIC_PAGES_FR if lang == 'fr' else STATIC_PAGES_EN
    for loc, (href_self, href_other, prio) in static.items():
        if os.path.exists(os.path.join(DIR, loc)):
            if lang == 'fr':
                entries.append(make_url_entry(loc, hreflang_fr=href_self,
                                              hreflang_en=href_other, priority=prio))
            else:
                entries.append(make_url_entry(loc, hreflang_en=href_self,
                                              hreflang_fr=href_other, priority=prio))

    # 2. Pages destination
    if lang == 'fr':
        for page in find_fr_pages():
            en_page = get_en_counterpart(page, slug_map)
            is_annual = page.startswith('meilleure-periode-')
            prio = 0.8 if is_annual else 0.6
            entries.append(make_url_entry(page, hreflang_fr=page,
                                          hreflang_en=en_page, priority=prio))
    else:
        for page in find_en_pages():
            fr_page = get_fr_counterpart(page, slug_map)
            is_annual = 'best-time-to-visit' in page
            prio = 0.8 if is_annual else 0.6
            entries.append(make_url_entry(page, hreflang_en=page,
                                          hreflang_fr=fr_page, priority=prio))

    # 3. Pages classement/ranking
    rankings_fr, rankings_en = find_ranking_pages()
    pages_list = rankings_fr if lang == 'fr' else rankings_en
    for page in pages_list:
        entries.append(make_url_entry(page, priority=0.7))

    # 4. Pages comparatif/comparison
    comparisons_fr, comparisons_en = find_comparison_pages()
    pages_list = comparisons_fr if lang == 'fr' else comparisons_en
    for page in pages_list:
        entries.append(make_url_entry(page, priority=0.6))

    # 5. Pages pilier/pillar
    pillars_fr, pillars_en = find_pillar_pages()
    pages_list = pillars_fr if lang == 'fr' else pillars_en
    for page in pages_list:
        entries.append(make_url_entry(page, priority=0.7))

    # Assemble XML
    xml = ['<?xml version="1.0" encoding="UTF-8"?>']
    xml.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"'
               ' xmlns:xhtml="http://www.w3.org/1999/xhtml">')
    xml.extend(entries)
    xml.append('</urlset>')
    content = '\n'.join(xml) + '\n'

    filename = f'sitemap-{lang}.xml'
    filepath = os.path.join(DIR, filename)

    if dry_run:
        print(f'[DRY-RUN] {filename}: {len(entries)} URLs')
    else:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'{filename}: {len(entries)} URLs')

    return len(entries)


if __name__ == '__main__':
    dry_run = '--dry-run' in sys.argv
    n_fr = generate_sitemap('fr', dry_run)
    n_en = generate_sitemap('en', dry_run)
    print(f'\nTotal: {n_fr} FR + {n_en} EN = {n_fr + n_en} URLs')
