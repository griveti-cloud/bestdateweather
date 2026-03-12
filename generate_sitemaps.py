#!/usr/bin/env python3
"""Regenerate all 5 sitemaps from HTML files present on disk."""
import glob
from datetime import date

TODAY = date.today().isoformat()
BASE  = "https://bestdateweather.com"

def is_redirect(filepath):
    try:
        with open(filepath) as f:
            return 'meta http-equiv="refresh"' in f.read(500)
    except:
        return False

def make_sitemap(urls, path):
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for url, freq, pri in urls:
        lines += [f'  <url>',
                  f'    <loc>{BASE}/{url}</loc>',
                  f'    <lastmod>{TODAY}</lastmod>',
                  f'    <changefreq>{freq}</changefreq>',
                  f'    <priority>{pri}</priority>',
                  f'  </url>']
    lines.append('</urlset>')
    with open(path, 'w') as f:
        f.write('\n'.join(lines) + '\n')
    print(f"✓ {path}: {len(urls)} URLs")

STATIC_FR = [
    ('index.html','weekly','1.0'),('a-propos.html','monthly','0.4'),
    ('methodologie.html','monthly','0.4'),('faq.html','monthly','0.4'),
    ('legal.html','monthly','0.3'),('privacy.html','monthly','0.3'),('contact.html','monthly','0.3'),
]
STATIC_EN = [
    ('en/app.html','weekly','1.0'),('en/about.html','monthly','0.4'),
    ('en/methodology.html','monthly','0.4'),('en/faq.html','monthly','0.4'),
    ('en/legal.html','monthly','0.3'),('en/privacy.html','monthly','0.3'),('en/contact.html','monthly','0.3'),
]
STATIC_ES = [('es/app.html','weekly','1.0'),('es/sobre-nosotros.html','monthly','0.4'),('es/metodologia.html','monthly','0.4')]
STATIC_DE = [('de/app.html','weekly','1.0'),('de/ueber-uns.html','monthly','0.4'),('de/methodik.html','monthly','0.4')]
STATIC_US = [('us/app.html','weekly','1.0'),('us/about.html','monthly','0.4')]

def collect(patterns, exclude_redirects=True):
    result = []
    for pat, freq, pri in patterns:
        for f in sorted(glob.glob(pat)):
            if exclude_redirects and is_redirect(f): continue
            result.append((f, freq, pri))
    return result

make_sitemap(
    [(f,freq,pri) for f,freq,pri in STATIC_FR if glob.glob(f)] +
    collect([('meilleures-destinations-meteo.html','monthly','0.9'),
             ('ou-partir-en-*.html','monthly','0.8'),('classement-*.html','monthly','0.7'),
             ('meilleure-periode-*.html','monthly','0.8'),('*-meteo-*.html','monthly','0.6'),
             ('comparer-*.html','monthly','0.5')]),
    'sitemap-fr.xml')

make_sitemap(
    [(f,freq,pri) for f,freq,pri in STATIC_EN if glob.glob(f)] +
    collect([('en/best-weather-destinations.html','monthly','0.9'),
             ('en/where-to-go-in-*.html','monthly','0.8'),('en/ranking-*.html','monthly','0.7'),
             ('en/best-time-to-visit-*.html','monthly','0.8'),('en/*-weather-*.html','monthly','0.6'),
             ('en/compare-*.html','monthly','0.5')]),
    'sitemap-en.xml')

make_sitemap(
    [(f,freq,pri) for f,freq,pri in STATIC_ES if glob.glob(f)] +
    collect([('es/mejores-destinos-climaticos.html','monthly','0.9'),
             ('es/donde-ir-en-*.html','monthly','0.8'),('es/mejor-epoca-*.html','monthly','0.8'),
             ('es/*-clima-*.html','monthly','0.6')]),
    'sitemap-es.xml')

make_sitemap(
    [(f,freq,pri) for f,freq,pri in STATIC_DE if glob.glob(f)] +
    collect([('de/beste-reiseziele-klima.html','monthly','0.9'),
             ('de/wohin-im-*.html','monthly','0.8'),('de/beste-reisezeit-*.html','monthly','0.8'),
             ('de/*-wetter-*.html','monthly','0.6')]),
    'sitemap-de.xml')

make_sitemap(
    [(f,freq,pri) for f,freq,pri in STATIC_US if glob.glob(f)] +
    collect([('us/best-weather-destinations.html','monthly','0.9'),
             ('us/where-to-go-in-*.html','monthly','0.8'),('us/best-time-to-visit-*.html','monthly','0.8'),
             ('us/*-weather-*.html','monthly','0.6')]),
    'sitemap-us.xml')
