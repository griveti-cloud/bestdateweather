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
    ('mentions-legales.html','monthly','0.3'),('confidentialite.html','monthly','0.3'),('contact.html','monthly','0.3'),
]
STATIC_EN = [
    ('en/app.html','weekly','1.0'),('en/best-weather-destinations.html','monthly','0.9'),
    ('en/about.html','monthly','0.4'),
    ('en/methodology.html','monthly','0.4'),('en/faq.html','monthly','0.4'),
    ('en/legal.html','monthly','0.3'),('en/privacy.html','monthly','0.3'),('en/contact.html','monthly','0.3'),
]
STATIC_ES = [('es/app.html','weekly','1.0'),('es/sobre-nosotros.html','monthly','0.4'),('es/metodologia.html','monthly','0.4')]
STATIC_DE = [('de/app.html','weekly','1.0'),('de/ueber-uns.html','monthly','0.4'),('de/methodik.html','monthly','0.4')]
STATIC_US = [('us/app.html','weekly','1.0'),('us/about.html','monthly','0.4')]

def collect(patterns, exclude_redirects=True, exclude_files=None):
    excl = set(exclude_files or [])
    result = []
    for pat, freq, pri in patterns:
        for f in sorted(glob.glob(pat)):
            if f in excl: continue
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
    collect([('en/where-to-go-in-*.html','monthly','0.8'),('en/ranking-*.html','monthly','0.7'),
             ('en/best-time-to-visit-*.html','monthly','0.8'),('en/*-weather-*.html','monthly','0.6'),
             ('en/compare-*.html','monthly','0.5')],
            exclude_files=[f for f,_,_ in STATIC_EN]),
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
# ── Sitemaps segmentés (priorité crawl) ───────────────────────────────────────
import csv as csv_mod, re as re_mod

def load_top_slugs():
    top = {'fr': set(), 'en': set(), 'es': set(), 'de': set()}
    with open('data/destinations.csv', encoding='utf-8-sig') as f:
        for row in csv_mod.DictReader(f):
            if row.get('booking_dest_id', '').strip():
                top['fr'].add(row['slug_fr'].lower())
                top['en'].add(row.get('slug_en', row['slug_fr']).lower())
                top['es'].add(row.get('slug_es', row['slug_fr']).lower())
                top['de'].add(row.get('slug_de', row['slug_fr']).lower())
    return top

def split_sitemap(src_path, dst_prio, dst_sec, top_slugs, monthly_pat):
    import xml.etree.ElementTree as ET2
    ns = 'http://www.sitemaps.org/schemas/sitemap/0.9'
    tree = ET2.parse(src_path)
    root = tree.getroot()
    prio, sec = [], []
    for url_el in root.findall(f'{{{ns}}}url'):
        loc = url_el.find(f'{{{ns}}}loc').text
        path = re_mod.sub(r'https://bestdateweather\.com/(en/|es/|de/|us/)?', '', loc)
        if monthly_pat not in path:
            prio.append(loc)
        else:
            # Vérifier que c'est vraiment une page mensuelle (finit par un mois)
            MONTH_SLUGS = {
                'january','february','march','april','may','june','july','august',
                'september','october','november','december',
                'janvier','fevrier','mars','avril','mai','juin','juillet','aout',
                'septembre','octobre','novembre','decembre',
                'enero','febrero','marzo','abril','mayo','junio','julio','agosto',
                'septiembre','octubre','noviembre','diciembre',
                'januar','februar','maerz','april','mai','juni','juli','august',
                'september','oktober','november','dezember',
            }
            stem = path.lower().replace('.html','').rstrip('/')
            last_part = stem.split('-')[-1]
            if last_part not in MONTH_SLUGS:
                prio.append(loc)
            else:
                slug = path.split(monthly_pat)[0].rstrip('-').lower()
                (prio if slug in top_slugs else sec).append(loc)
    for urls, dst in [(prio, dst_prio), (sec, dst_sec)]:
        lines = ['<?xml version="1.0" encoding="UTF-8"?>',
                 '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
        for u in urls:
            lines += [f'  <url>', f'    <loc>{u}</loc>',
                      f'    <lastmod>{TODAY}</lastmod>', f'  </url>']
        lines.append('</urlset>')
        open(dst, 'w').write('\n'.join(lines) + '\n')
        print(f"  {dst}: {len(urls)} URLs")

top = load_top_slugs()
split_sitemap('sitemap-fr.xml','sitemap-fr-priority.xml','sitemap-fr-secondary.xml',top['fr'],'-meteo-')
split_sitemap('sitemap-en.xml','sitemap-en-priority.xml','sitemap-en-secondary.xml',top['en'],'-weather-')
split_sitemap('sitemap-es.xml','sitemap-es-priority.xml','sitemap-es-secondary.xml',top['es'],'-clima-')
split_sitemap('sitemap-de.xml','sitemap-de-priority.xml','sitemap-de-secondary.xml',top['de'],'-wetter-')
split_sitemap('sitemap-us.xml','sitemap-us-priority.xml','sitemap-us-secondary.xml',top['en'],'-weather-')

idx = f'''<?xml version="1.0" encoding="UTF-8"?>
<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <sitemap><loc>https://bestdateweather.com/sitemap-fr-priority.xml</loc><lastmod>{TODAY}</lastmod></sitemap>
  <sitemap><loc>https://bestdateweather.com/sitemap-en-priority.xml</loc><lastmod>{TODAY}</lastmod></sitemap>
  <sitemap><loc>https://bestdateweather.com/sitemap-es-priority.xml</loc><lastmod>{TODAY}</lastmod></sitemap>
  <sitemap><loc>https://bestdateweather.com/sitemap-de-priority.xml</loc><lastmod>{TODAY}</lastmod></sitemap>
  <sitemap><loc>https://bestdateweather.com/sitemap-us-priority.xml</loc><lastmod>{TODAY}</lastmod></sitemap>
  <sitemap><loc>https://bestdateweather.com/sitemap-us-secondary.xml</loc><lastmod>{TODAY}</lastmod></sitemap>
  <sitemap><loc>https://bestdateweather.com/sitemap-fr-secondary.xml</loc><lastmod>{TODAY}</lastmod></sitemap>
  <sitemap><loc>https://bestdateweather.com/sitemap-en-secondary.xml</loc><lastmod>{TODAY}</lastmod></sitemap>
  <sitemap><loc>https://bestdateweather.com/sitemap-es-secondary.xml</loc><lastmod>{TODAY}</lastmod></sitemap>
  <sitemap><loc>https://bestdateweather.com/sitemap-de-secondary.xml</loc><lastmod>{TODAY}</lastmod></sitemap>
</sitemapindex>'''
open('sitemap-index.xml','w').write(idx)
print(f"  sitemap-index.xml: 10 sitemaps")

