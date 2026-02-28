#!/usr/bin/env python3
"""Regenerate all ranking pages (5 FR + 5 EN) from climate.csv data."""
import csv, json
import html as H

MOIS_FR = ['Janvier','Février','Mars','Avril','Mai','Juin','Juillet','Août','Septembre','Octobre','Novembre','Décembre']
MOIS_EN = ['January','February','March','April','May','June','July','August','September','October','November','December']

# ── Load data ──────────────────────────────────────────
def load_data():
    dests = {}
    with open('data/destinations.csv', encoding='utf-8-sig') as f:
        for r in csv.DictReader(f):
            dests[r['slug_fr']] = r

    climate = {}  # slug → {mois_num: row}
    with open('data/climate.csv', encoding='utf-8-sig') as f:
        for r in csv.DictReader(f):
            s = r['slug']
            if s not in climate:
                climate[s] = {}
            climate[s][int(r['mois_num'])] = r

    # Compute annual stats per destination
    stats = []
    for slug, months in climate.items():
        if slug not in dests:
            continue
        d = dests[slug]
        scores = [float(months[m]['score']) for m in sorted(months)]
        avg = sum(scores) / len(scores)
        sun_h = sum(float(months[m]['sun_h']) for m in months) * 365.25 / 12  # approximate annual
        rain_pct = sum(float(months[m]['rain_pct']) for m in months) / len(months)
        best_month = max(months.items(), key=lambda x: float(x[1]['score']))
        best_m_num = best_month[0]
        rec_count = sum(1 for m in months.values() if m['classe'] == 'rec')
        mid_count = sum(1 for m in months.values() if m['classe'] == 'mid')
        avoid_count = sum(1 for m in months.values() if m['classe'] == 'avoid')

        # Summer (Jun-Aug) avg
        summer_scores = [float(months[m]['score']) for m in [6,7,8] if m in months]
        summer_avg = sum(summer_scores)/len(summer_scores) if summer_scores else 0

        # Winter (Dec-Jan-Feb) avg
        winter_scores = [float(months[m]['score']) for m in [12,1,2] if m in months]
        winter_avg = sum(winter_scores)/len(winter_scores) if winter_scores else 0

        # Constancy (std dev of scores - lower = more constant)
        import statistics
        std = statistics.stdev(scores) if len(scores) > 1 else 0

        stats.append({
            'slug': slug,
            'nom_fr': d['nom_fr'],
            'nom_bare': d['nom_bare'],
            'nom_en': d['nom_en'],
            'pays': d['pays'],
            'flag': d['flag'],
            'avg': round(avg, 1),
            'sun_h': round(sun_h),
            'rain_pct': round(rain_pct),
            'best_month': best_m_num,
            'best_score': round(float(best_month[1]['score']), 1),
            'rec': rec_count,
            'mid': mid_count,
            'avoid': avoid_count,
            'summer_avg': round(summer_avg, 1),
            'winter_avg': round(winter_avg, 1),
            'std': round(std, 2),
            'scores': scores,
            'months': months,
        })

    return stats, dests

# ── Region tags ──
def region_tag(pays):
    europe_sud = {'Italie','Grèce','Espagne','Portugal','Croatie','Malte','Monaco','Monténégro','Albanie','Chypre','Turquie','Slovénie'}
    europe_nord = {'Pays-Bas','Allemagne','Royaume-Uni','Écosse','Tchéquie','Autriche','Belgique','Hongrie','Pologne','Roumanie','Irlande','Islande','Suisse','Bulgarie','Slovaquie','Danemark','Suède','Norvège','Finlande','Estonie','Lettonie','Lituanie','Géorgie','Ouzbékistan'}
    if pays == 'France': return 'France'
    if pays in europe_sud: return 'Europe du Sud'
    if pays in europe_nord: return 'Europe du Nord'
    if pays in {'Maroc','Tunisie','Égypte','Sénégal','Cap-Vert'}: return 'Afrique du Nord'
    if pays in {'Kenya','Tanzanie','Namibie','Afrique du Sud','Madagascar'}: return 'Afrique'
    if pays in {'Maurice','Seychelles','Réunion','Mayotte','Maldives'}: return 'Océan Indien'
    if pays in {'Émirats Arabes Unis','Jordanie','Oman','Israël','Qatar'}: return 'Moyen-Orient'
    if pays in {'Thaïlande','Viêt Nam','Indonésie','Philippines','Malaisie','Cambodge','Laos','Singapour','Myanmar'}: return 'Asie du Sud-Est'
    if pays in {'Japon','Chine','Corée du Sud','Taïwan','Macao','Hong Kong'}: return "Asie de l'Est"
    if pays in {'Inde','Sri Lanka','Népal'}: return 'Asie du Sud'
    if pays in {'États-Unis','Canada'}: return 'Amérique du Nord'
    if pays in {'Mexique','Costa Rica','Panama','Guatemala','Belize','Nicaragua'}: return 'Amérique Centrale'
    if pays in {'Colombie','Pérou','Brésil','Chili','Argentine','Équateur','Bolivie','Uruguay'}: return 'Amérique du Sud'
    if pays in {'Australie','Nouvelle-Zélande'}: return 'Océanie'
    return 'Caraïbes'

def is_europe(pays, slug=''):
    # Overseas territories to exclude even if pays is France/UK
    overseas = {'reunion','guadeloupe','martinique','saint-martin','saint-barth',
                'nouvelle-caledonie','mayotte','guyane','saint-pierre-et-miquelon',
                'polynesie-française','polynésie-française','bermudes'}
    if slug in overseas:
        return False
    eu = {'France','Italie','Grèce','Espagne','Portugal','Croatie','Malte','Monaco','Monténégro','Albanie','Chypre','Turquie','Slovénie',
          'Pays-Bas','Allemagne','Royaume-Uni','Écosse','Tchéquie','Autriche','Belgique','Hongrie','Pologne','Roumanie','Irlande','Islande',
          'Suisse','Bulgarie','Slovaquie','Danemark','Suède','Norvège','Finlande','Estonie','Lettonie','Lituanie','Géorgie'}
    return pays in eu

# ── HTML generators ──
GA = '''<script async src="https://www.googletagmanager.com/gtag/js?id=G-NTCJTDPSJL"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}gtag("js",new Date());gtag("config","G-NTCJTDPSJL");</script>'''

FONTS = '''<link rel="preconnect" href="https://fonts.googleapis.com"/>
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin/>
<link rel="preload" as="style" href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;1,700&family=DM+Sans:wght@400;500;700&display=swap" onload="this.onload=null;this.rel='stylesheet'"/>
<noscript><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;1,700&family=DM+Sans:wght@400;500;700&display=swap"/></noscript>'''

CSS = ''':root{--navy:#0f1923;--gold:#c8a84b;--cream:#faf8f3;--cream2:#ece8de;--text:#1a1f2e;--slate:#4a5568;--slate2:#718096}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'DM Sans',-apple-system,sans-serif;background:var(--cream);color:var(--text)}
nav{display:flex;justify-content:space-between;align-items:center;padding:14px 24px;background:var(--navy);position:sticky;top:0;z-index:100}
.nav-brand{font-size:17px;font-weight:800;color:white;text-decoration:none;letter-spacing:-.3px}
.nav-brand em{color:var(--gold);font-style:normal}
.nav-cta{background:var(--gold);color:var(--navy);padding:7px 16px;border-radius:20px;font-size:13px;font-weight:700;text-decoration:none}
.hero{background:var(--navy);color:white;padding:64px 24px 48px;text-align:center}
.hero-eyebrow{font-size:11px;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:var(--gold);margin-bottom:14px}
.hero-title{font-family:'Playfair Display',Georgia,serif;font-size:clamp(24px,5vw,44px);font-weight:700;line-height:1.15;margin-bottom:16px;max-width:800px;margin-left:auto;margin-right:auto}
.hero-title em{color:var(--gold);font-style:italic}
.hero-sub{font-size:15px;opacity:.8;max-width:580px;margin:0 auto 24px;line-height:1.65}
.hero-stats{display:flex;justify-content:center;gap:40px;flex-wrap:wrap;margin-top:28px}
.hstat-val{display:block;font-family:'Playfair Display',Georgia,serif;font-size:34px;font-weight:700;color:var(--gold)}
.hstat-lbl{display:block;font-size:11px;text-transform:uppercase;letter-spacing:1px;opacity:.65;margin-top:4px}
.insights-bar{background:#1a2535;border-top:3px solid var(--gold);padding:28px 24px}
.insights-inner{max-width:900px;margin:0 auto}
.insights-label{font-size:11px;font-weight:800;color:var(--gold);text-transform:uppercase;letter-spacing:1.5px;margin-bottom:14px}
.insights-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:10px}
.insight-item{background:rgba(255,255,255,.07);border:1px solid rgba(200,168,75,.2);border-radius:10px;padding:14px 16px;font-size:13.5px;color:rgba(255,255,255,.9);line-height:1.5}
.insight-item strong{color:var(--gold);display:block;font-size:12px;margin-bottom:4px;text-transform:uppercase;letter-spacing:.5px}
.page{max-width:900px;margin:0 auto;padding:48px 20px 80px}
.section{margin-bottom:52px}
.eyebrow{font-size:11px;font-weight:800;color:var(--gold);text-transform:uppercase;letter-spacing:1.5px;margin-bottom:10px}
.sec-title{font-family:'Playfair Display',Georgia,serif;font-size:clamp(20px,3vw,26px);font-weight:700;margin-bottom:14px;line-height:1.2}
.sec-intro{font-size:15px;color:var(--slate);line-height:1.7;margin-bottom:22px}
.rt{width:100%;border-collapse:collapse;font-size:14px;border:1.5px solid var(--cream2);border-radius:14px;overflow:hidden}
.rt thead{background:var(--navy);color:white}
.rt th{padding:11px 13px;font-weight:600;font-size:11px;letter-spacing:.5px;text-align:left}
.rt td{padding:10px 13px;border-bottom:1px solid var(--cream2);vertical-align:middle}
.rt tbody tr:nth-child(odd){background:white}
.rt tbody tr:hover{background:#f0f4ff}
.rt tbody tr:last-child td{border-bottom:none}
.rank{font-weight:800;font-size:15px;text-align:center;width:44px}
.dest-link{font-weight:700;color:var(--text);text-decoration:none}
.dest-link:hover{color:var(--gold)}
.region-tag{display:block;font-size:10px;color:var(--slate2);font-weight:400;margin-top:2px}
.sc{font-weight:800;font-size:15px;color:var(--navy)}
.sc span{font-weight:400;color:var(--slate2);font-size:12px}
.meth{background:var(--navy);color:white;border-radius:14px;padding:30px;margin-bottom:40px}
.meth strong{color:var(--gold)}
.meth p{font-size:14px;line-height:1.75;opacity:.85;margin-top:8px}
.related-pages{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:12px;margin-top:16px}
.related-card{background:white;border:1.5px solid var(--cream2);border-radius:12px;padding:16px;text-decoration:none;color:var(--text);display:block}
.related-card:hover{border-color:var(--gold);background:#fffbf0}
.related-card strong{display:block;font-size:13px;font-weight:700;margin-bottom:4px}
.related-card span{font-size:11px;color:var(--slate2)}
footer{background:var(--navy);color:rgba(255,255,255,.7);text-align:center;padding:36px 20px;font-size:12px;line-height:2}
footer a{color:rgba(255,255,255,.8);text-decoration:none}
@media(max-width:640px){.rt th:nth-child(5),.rt td:nth-child(5){display:none}.hero-stats{gap:20px}}'''


def rank_icon(i):
    if i == 1: return '🥇'
    if i == 2: return '🥈'
    if i == 3: return '🥉'
    return str(i)


def table_row(i, s, is_fr, cols='main', prefix=''):
    name = s['nom_fr'] if is_fr else s['nom_en']
    slug = s['slug']
    href_prefix = 'meilleure-periode-' if is_fr else f'{prefix}best-time-to-visit-'
    month_names = MOIS_FR if is_fr else MOIS_EN
    best_m = month_names[s['best_month']-1]
    rt = region_tag(s['pays'])

    base = f'<tr><td class="rank">{rank_icon(i)}</td>'
    base += f'<td><a href="{href_prefix}{slug}.html" class="dest-link">{H.escape(name)}</a>'
    base += f'<span class="region-tag">{rt}</span></td>'

    if cols == 'main':
        base += f'<td>{best_m}</td>'
        base += f'<td class="sc">{s["avg"]}<span>/10</span></td>'
        base += f'<td>{s["sun_h"]}h</td>'
        base += f'<td>{s["rain_pct"]}%</td>'
    elif cols == 'summer':
        base += f'<td class="sc">{s["summer_avg"]}<span>/10</span></td>'
        base += f'<td class="sc">{s["avg"]}<span>/10</span></td>'
        base += f'<td>{s["rain_pct"]}%</td>'
    elif cols == 'winter':
        base += f'<td class="sc">{s["winter_avg"]}<span>/10</span></td>'
        base += f'<td class="sc">{s["avg"]}<span>/10</span></td>'
        base += f'<td>{s["rain_pct"]}%</td>'
    elif cols == 'nomad':
        base += f'<td class="sc">{s["avg"]}<span>/10</span></td>'
        base += f'<td>{s["std"]}</td>'
        base += f'<td>{s["rec"]}/12</td>'
        base += f'<td>{s["avoid"]}/12</td>'
    elif cols == 'sun':
        base += f'<td>{s["sun_h"]}h</td>'
        base += f'<td class="sc">{s["avg"]}<span>/10</span></td>'
        base += f'<td>{s["rain_pct"]}%</td>'
    elif cols == 'rain':
        base += f'<td>{s["rain_pct"]}%</td>'
        base += f'<td class="sc">{s["avg"]}<span>/10</span></td>'
        base += f'<td>{s["sun_h"]}h</td>'

    base += '</tr>'
    return base


def make_table(ranked, is_fr, cols, n=20, prefix=''):
    headers = {
        'main': ['Rang','Destination','Meilleur mois','Score annuel','Soleil/an','Pluie moy.'] if is_fr else ['Rank','Destination','Best month','Annual score','Sun/year','Avg rain'],
        'summer': ['Rang','Destination','Score été','Score annuel','Pluie moy.'] if is_fr else ['Rank','Destination','Summer score','Annual score','Avg rain'],
        'winter': ['Rang','Destination','Score hiver','Score annuel','Pluie moy.'] if is_fr else ['Rank','Destination','Winter score','Annual score','Avg rain'],
        'nomad': ['Rang','Destination','Score annuel','Écart-type','Mois rec','Mois avoid'] if is_fr else ['Rank','Destination','Annual score','Std dev','Rec months','Avoid months'],
        'sun': ['Rang','Destination','Soleil/an','Score annuel','Pluie moy.'] if is_fr else ['Rank','Destination','Sun/year','Annual score','Avg rain'],
        'rain': ['Rang','Destination','Pluie moy.','Score annuel','Soleil/an'] if is_fr else ['Rank','Destination','Avg rain','Annual score','Sun/year'],
    }
    h = headers[cols]
    rows = '<thead><tr>' + ''.join(f'<th>{c}</th>' for c in h) + '</tr></thead><tbody>'
    for i, s in enumerate(ranked[:n], 1):
        rows += table_row(i, s, is_fr, cols, prefix)
    rows += '</tbody>'
    return f'<div style="overflow-x:auto"><table class="rt">{rows}</table></div>'


def schema_json(ranked, n, is_fr):
    items = []
    for i, s in enumerate(ranked[:n], 1):
        name = s['nom_fr'] if is_fr else s['nom_en']
        prefix = 'meilleure-periode-' if is_fr else 'best-time-to-visit-'
        base = 'https://bestdateweather.com/' if is_fr else 'https://bestdateweather.com/en/'
        items.append({"@type":"ListItem","position":i,"name":name,"url":f"{base}{prefix}{s['slug']}.html"})
    title = f"Top {n} meilleures destinations météo 2026" if is_fr else f"Top {n} best weather destinations 2026"
    return json.dumps({"@context":"https://schema.org","@type":"ItemList","name":title,"numberOfItems":n,"itemListElement":items}, ensure_ascii=False)


def nav(is_fr, prefix=''):
    home = f'{prefix}index.html' if is_fr else f'{prefix}../index.html'
    app_text = "Tester l'app" if is_fr else "Try the app"
    return f'<nav><a class="nav-brand" href="{home}">Best<em>Date</em>Weather</a><a class="nav-cta" href="{home}">{app_text}</a></nav>'


def footer(is_fr, en_file='', fr_file='', prefix=''):
    meth = f'{prefix}note_modele.html' if is_fr else f'{prefix}../note_modele.html'
    home = f'{prefix}index.html' if is_fr else f'{prefix}../index.html'
    meth_label = 'Méthodologie' if is_fr else 'Methodology'
    app_label = 'Application météo' if is_fr else 'Weather app'
    lang_link = ''
    if is_fr and en_file:
        lang_link = f' · <a href="en/{en_file}" style="color:rgba(255,255,255,.7)"><img src="flags/gb.png" width="20" height="15" alt="" style="vertical-align:middle;border-radius:2px"> English</a>'
    elif not is_fr and fr_file:
        lang_link = f' · <a href="../{fr_file}" style="color:rgba(255,255,255,.7)"><img src="../flags/fr.png" width="20" height="15" alt="" style="vertical-align:middle;border-radius:2px"> Français</a>'
    return f'''<footer>
<p style="color:rgba(255,255,255,.7);font-size:13px;font-weight:700;margin-bottom:8px">bestdateweather.com</p>
<p><a href="https://open-meteo.com/" rel="noopener" style="color:rgba(255,255,255,.7)">Données météo par Open-Meteo.com</a> · Sources ECMWF, DWD, NOAA, Météo-France · CC BY 4.0</p>
<p style="margin-top:8px"><a href="{meth}" style="color:rgba(255,255,255,.7)">{meth_label}</a> · <a href="{home}" style="color:rgba(255,255,255,.7)">{app_label}</a>{lang_link}</p>
<p style="margin-top:8px;font-size:11px;opacity:.6"><a href="{prefix}{'mentions-legales' if is_fr else '../mentions-legales'}.html" style="color:rgba(255,255,255,.7)">{'Mentions légales' if is_fr else 'Legal'}</a></p>
</footer>'''


def related(is_fr, prefix=''):
    if is_fr:
        return '''<div class="related-pages">
<a href="classement-destinations-meteo-2026.html" class="related-card"><strong>🏆 Classement global 2026</strong><span>318 destinations</span></a>
<a href="classement-destinations-europe-meteo-2026.html" class="related-card"><strong>🇪🇺 Top Europe météo 2026</strong><span>Comparatif européen</span></a>
<a href="classement-destinations-meteo-ete-2026.html" class="related-card"><strong>☀️ Meilleures destinations été</strong><span>Juin–Juil–Août</span></a>
<a href="classement-destinations-meteo-hiver-2026.html" class="related-card"><strong>❄️ Meilleures destinations hiver</strong><span>Déc–Jan–Fév</span></a>
<a href="classement-destinations-meteo-nomades-2026.html" class="related-card"><strong>💻 Meilleures destinations nomades</strong><span>Régularité & confort</span></a>
</div>'''
    else:
        return '''<div class="related-pages">
<a href="best-destinations-weather-ranking-2026.html" class="related-card"><strong>🏆 Global ranking 2026</strong><span>318 destinations</span></a>
<a href="best-europe-weather-ranking-2026.html" class="related-card"><strong>🇪🇺 Europe weather ranking</strong><span>European comparison</span></a>
<a href="best-destinations-summer-weather-2026.html" class="related-card"><strong>☀️ Best summer destinations</strong><span>Jun–Jul–Aug</span></a>
<a href="best-destinations-winter-weather-2026.html" class="related-card"><strong>❄️ Best winter destinations</strong><span>Dec–Jan–Feb</span></a>
<a href="best-destinations-digital-nomads-weather-2026.html" class="related-card"><strong>💻 Best nomad destinations</strong><span>Consistency & comfort</span></a>
</div>'''


def meth_block(is_fr, n):
    if is_fr:
        return f'<div class="meth"><strong>Méthodologie</strong><p>Scores calculés sur 10 ans d\'archives Open-Meteo (ERA5). Chaque mois noté sur ensoleillement (40&nbsp;%), précipitations (30&nbsp;%), confort thermique (30&nbsp;%). Score annuel = moyenne des 12 mois. {n} destinations analysées.</p></div>'
    else:
        return f'<div class="meth"><strong>Methodology</strong><p>Scores computed from 10 years of Open-Meteo archives (ERA5). Each month rated on sunshine (40%), precipitation (30%), thermal comfort (30%). Annual score = average of 12 months. {n} destinations analyzed.</p></div>'


def page(title, desc, canonical, hreflang_fr, hreflang_en, hero_eyebrow, hero_title, hero_sub, hero_stats, insights, sections, is_fr, en_file='', fr_file='', prefix='', schema=''):
    flag_prefix = '' if is_fr else '../'
    og_img = f'{flag_prefix}og-image.png'
    return f'''<!DOCTYPE html>
<html lang="{'fr' if is_fr else 'en'}">
<head>
<meta charset="UTF-8"/><meta name="viewport" content="width=device-width,initial-scale=1.0"/>
<title>{H.escape(title)}</title>
<meta name="description" content="{H.escape(desc)}"/>
<link rel="canonical" href="{canonical}"/>
<link rel="alternate" hreflang="fr" href="{hreflang_fr}"/>
<link rel="alternate" hreflang="en" href="{hreflang_en}"/>
{GA}
<link rel="icon" type="image/x-icon" href="{flag_prefix}favicon.ico"/>
<style>{CSS}</style>
{FONTS}
{f'<script type="application/ld+json">{schema}</script>' if schema else ''}
<meta property="og:image" content="https://bestdateweather.com/og-image.png"/>
<meta property="og:image:width" content="1200"/><meta property="og:image:height" content="630"/>
<meta name="twitter:card" content="summary_large_image"/>
</head><body>
{nav(is_fr, prefix)}
<header class="hero">
<div class="hero-eyebrow">{hero_eyebrow}</div>
<h1 class="hero-title">{hero_title}</h1>
<p class="hero-sub">{hero_sub}</p>
<div class="hero-stats">{hero_stats}</div>
</header>
{insights}
<main class="page">
{''.join(sections)}
{meth_block(is_fr, 318)}
{related(is_fr, prefix)}
</main>
{footer(is_fr, en_file, fr_file, prefix)}
</body></html>'''


def hstat(val, label):
    return f'<div class="hstat"><span class="hstat-val">{val}</span><span class="hstat-lbl">{label}</span></div>'


def insight(title, text):
    return f'<div class="insight-item"><strong>{title}</strong>{text}</div>'


def insights_bar(items):
    grid = ''.join(items)
    return f'<div class="insights-bar"><div class="insights-inner"><div class="insights-label">Points clés</div><div class="insights-grid">{grid}</div></div></div>'


def section(eyebrow, title, intro, table_html):
    intro_html = f'<p class="sec-intro">{intro}</p>' if intro else ''
    return f'<div class="section"><div class="eyebrow">{eyebrow}</div><h2 class="sec-title">{title}</h2>{intro_html}{table_html}</div>'


# ── Generate pages ──────────────────────────────────────
def generate_all():
    stats, dests = load_data()
    total = len(stats)
    days_measured = total * 10 * 365
    days_str = f"{days_measured // 1000}\u2009000+"

    # Sort variants
    by_avg = sorted(stats, key=lambda x: -x['avg'])
    by_sun = sorted(stats, key=lambda x: -x['sun_h'])
    by_rain = sorted(stats, key=lambda x: x['rain_pct'])
    by_summer = sorted(stats, key=lambda x: -x['summer_avg'])
    by_winter = sorted(stats, key=lambda x: -x['winter_avg'])
    by_nomad = sorted(stats, key=lambda x: (-x['avg'], x['std']))
    by_nomad_constancy = sorted([s for s in stats if s['avoid'] <= 2], key=lambda x: (-x['avg'], x['std']))

    eu_stats = [s for s in stats if is_europe(s['pays'], s['slug'])]
    eu_by_avg = sorted(eu_stats, key=lambda x: -x['avg'])
    eu_by_summer = sorted(eu_stats, key=lambda x: -x['summer_avg'])
    eu_by_winter = sorted(eu_stats, key=lambda x: -x['winter_avg'])

    top1 = by_avg[0]
    top1_sun = by_sun[0]
    top1_dry = by_rain[0]
    eu_top1 = eu_by_avg[0]

    for is_fr in [True, False]:
        prefix = '' if is_fr else '../'
        pfx_file = '' if is_fr else 'en/'

        # ── 1. WORLD RANKING ──
        fname = 'classement-destinations-meteo-2026.html' if is_fr else 'en/best-destinations-weather-ranking-2026.html'
        n1 = top1['nom_fr'] if is_fr else top1['nom_en']

        sections_list = [
            section(
                'Classement mondial' if is_fr else 'World ranking',
                f'🏆 Top 20 mondial — Score climatique annuel' if is_fr else '🏆 Top 20 worldwide — Annual climate score',
                f'Score annuel = moyenne des 12 scores mensuels (0–10). {total} destinations analysées.' if is_fr else f'Annual score = average of 12 monthly scores (0–10). {total} destinations analyzed.',
                make_table(by_avg, is_fr, 'main', 20, prefix)
            ),
            section(
                'Ensoleillement' if is_fr else 'Sunshine',
                f'☀️ Top 10 les plus ensoleillées' if is_fr else '☀️ Top 10 sunniest',
                '', make_table(by_sun, is_fr, 'sun', 10, prefix)
            ),
            section(
                'Précipitations' if is_fr else 'Precipitation',
                f'🌂 Top 10 les moins pluvieuses' if is_fr else '🌂 Top 10 driest',
                '', make_table(by_rain, is_fr, 'rain', 10, prefix)
            ),
        ]

        html = page(
            title=f'Classement 2026 des meilleures destinations selon 10 ans de données météo' if is_fr else 'Best weather destinations 2026 — 10-year climate ranking',
            desc=f'{total} destinations classées sur 10 ans de données météo. {n1} en tête.' if is_fr else f'{total} destinations ranked on 10 years of weather data. {n1} leads.',
            canonical=f'https://bestdateweather.com/{fname}',
            hreflang_fr='https://bestdateweather.com/classement-destinations-meteo-2026.html',
            hreflang_en='https://bestdateweather.com/en/best-destinations-weather-ranking-2026.html',
            hero_eyebrow=f'{"Étude climatique indépendante" if is_fr else "Independent climate study"} · 2026',
            hero_title=f'Classement 2026 des meilleures<br/><em>destinations météo</em>' if is_fr else '2026 ranking of the best<br/><em>weather destinations</em>',
            hero_sub=f'{total} destinations analysées sur 10 ans. {n1} en tête avec {top1["avg"]}/10.' if is_fr else f'{total} destinations analyzed over 10 years. {n1} leads with {top1["avg"]}/10.',
            hero_stats=hstat(str(total), 'Destinations') + hstat('10 ans', 'Données' if is_fr else 'Data') + hstat(days_str, 'Jours mesurés' if is_fr else 'Days measured'),
            insights=insights_bar([
                insight('N°1 mondial' if is_fr else '#1 worldwide', f'{n1} — {top1["avg"]}/10 annuel.'),
                insight('Plus ensoleillé' if is_fr else 'Sunniest', f'{top1_sun["nom_fr" if is_fr else "nom_en"]} — {top1_sun["sun_h"]}h/an.'),
                insight('Plus sec' if is_fr else 'Driest', f'{top1_dry["nom_fr" if is_fr else "nom_en"]} — {top1_dry["rain_pct"]}% de pluie.' if is_fr else f'{top1_dry["nom_en"]} — {top1_dry["rain_pct"]}% rain.'),
                insight('Europe', f'{eu_top1["nom_fr" if is_fr else "nom_en"]} domine avec {eu_top1["avg"]}/10.' if is_fr else f'{eu_top1["nom_en"]} leads with {eu_top1["avg"]}/10.'),
            ]),
            sections=sections_list,
            is_fr=is_fr,
            en_file='best-destinations-weather-ranking-2026.html',
            fr_file='classement-destinations-meteo-2026.html',
            prefix=prefix,
            schema=schema_json(by_avg, 20, is_fr),
        )
        with open(fname, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f'  ✅ {fname}')

        # ── 2. EUROPE RANKING ──
        fname = 'classement-destinations-europe-meteo-2026.html' if is_fr else 'en/best-europe-weather-ranking-2026.html'
        eu_n1 = eu_top1['nom_fr'] if is_fr else eu_top1['nom_en']
        eu_total = len(eu_stats)

        sections_list = [
            section(
                'Classement Europe' if is_fr else 'Europe ranking',
                f'🏆 Top 20 Europe — Score annuel' if is_fr else '🏆 Top 20 Europe — Annual score',
                f'{eu_total} destinations européennes classées.' if is_fr else f'{eu_total} European destinations ranked.',
                make_table(eu_by_avg, is_fr, 'main', 20, prefix)
            ),
            section(
                'Été en Europe' if is_fr else 'Summer in Europe',
                '☀️ Top 10 Europe été (juin–août)' if is_fr else '☀️ Top 10 Europe summer (Jun–Aug)',
                '', make_table(eu_by_summer, is_fr, 'summer', 10, prefix)
            ),
            section(
                'Hiver en Europe' if is_fr else 'Winter in Europe',
                '❄️ Top 10 Europe hiver (déc–fév)' if is_fr else '❄️ Top 10 Europe winter (Dec–Feb)',
                '', make_table(eu_by_winter, is_fr, 'winter', 10, prefix)
            ),
        ]

        html = page(
            title=f'Classement météo Europe 2026 — Top destinations européennes' if is_fr else 'Europe weather ranking 2026 — Top European destinations',
            desc=f'{eu_total} destinations européennes classées. {eu_n1} en tête.' if is_fr else f'{eu_total} European destinations ranked. {eu_n1} leads.',
            canonical=f'https://bestdateweather.com/{fname}',
            hreflang_fr='https://bestdateweather.com/classement-destinations-europe-meteo-2026.html',
            hreflang_en='https://bestdateweather.com/en/best-europe-weather-ranking-2026.html',
            hero_eyebrow='Europe · 2026',
            hero_title=f'Classement météo<br/><em>Europe 2026</em>' if is_fr else 'Weather ranking<br/><em>Europe 2026</em>',
            hero_sub=f'{eu_total} destinations européennes. {eu_n1} en tête avec {eu_top1["avg"]}/10.' if is_fr else f'{eu_total} European destinations. {eu_n1} leads with {eu_top1["avg"]}/10.',
            hero_stats=hstat(str(eu_total), 'Destinations') + hstat('10 ans', 'Données' if is_fr else 'Data'),
            insights='',
            sections=sections_list,
            is_fr=is_fr,
            en_file='best-europe-weather-ranking-2026.html',
            fr_file='classement-destinations-europe-meteo-2026.html',
            prefix=prefix,
            schema=schema_json(eu_by_avg, 20, is_fr),
        )
        with open(fname, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f'  ✅ {fname}')

        # ── 3. SUMMER RANKING ──
        fname = 'classement-destinations-meteo-ete-2026.html' if is_fr else 'en/best-destinations-summer-weather-2026.html'
        s1 = by_summer[0]

        sections_list = [
            section(
                'Classement été' if is_fr else 'Summer ranking',
                '☀️ Top 20 mondial — Été 2026 (juin–août)' if is_fr else '☀️ Top 20 worldwide — Summer 2026 (Jun–Aug)',
                f'Score été = moyenne des scores juin, juillet, août.' if is_fr else 'Summer score = average of June, July, August scores.',
                make_table(by_summer, is_fr, 'summer', 20, prefix)
            ),
        ]

        html = page(
            title=f'Meilleures destinations été 2026 — Classement météo juin–août' if is_fr else 'Best summer destinations 2026 — Weather ranking Jun–Aug',
            desc=f'Top 20 des destinations avec la meilleure météo en été. {s1["nom_fr" if is_fr else "nom_en"]} en tête.' if is_fr else f'Top 20 destinations with the best summer weather.',
            canonical=f'https://bestdateweather.com/{fname}',
            hreflang_fr='https://bestdateweather.com/classement-destinations-meteo-ete-2026.html',
            hreflang_en='https://bestdateweather.com/en/best-destinations-summer-weather-2026.html',
            hero_eyebrow=f'{"Été" if is_fr else "Summer"} 2026',
            hero_title=f'Meilleures destinations<br/><em>été 2026</em>' if is_fr else 'Best destinations<br/><em>summer 2026</em>',
            hero_sub=f'{s1["nom_fr" if is_fr else "nom_en"]} en tête avec {s1["summer_avg"]}/10 en juin–août.' if is_fr else f'{s1["nom_en"]} leads with {s1["summer_avg"]}/10 in Jun–Aug.',
            hero_stats=hstat(str(total), 'Destinations') + hstat('Jun–Aug', 'Période' if is_fr else 'Period'),
            insights='',
            sections=sections_list,
            is_fr=is_fr,
            en_file='best-destinations-summer-weather-2026.html',
            fr_file='classement-destinations-meteo-ete-2026.html',
            prefix=prefix,
            schema=schema_json(by_summer, 20, is_fr),
        )
        with open(fname, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f'  ✅ {fname}')

        # ── 4. WINTER RANKING ──
        fname = 'classement-destinations-meteo-hiver-2026.html' if is_fr else 'en/best-destinations-winter-weather-2026.html'
        w1 = by_winter[0]

        sections_list = [
            section(
                'Classement hiver' if is_fr else 'Winter ranking',
                '❄️ Top 20 mondial — Hiver 2026 (déc–fév)' if is_fr else '❄️ Top 20 worldwide — Winter 2026 (Dec–Feb)',
                f'Score hiver = moyenne des scores décembre, janvier, février.' if is_fr else 'Winter score = average of December, January, February scores.',
                make_table(by_winter, is_fr, 'winter', 20, prefix)
            ),
        ]

        html = page(
            title=f'Meilleures destinations hiver 2026 — Soleil et chaleur garanti' if is_fr else 'Best winter destinations 2026 — Guaranteed sun and warmth',
            desc=f'Top 20 des destinations soleil en hiver. {w1["nom_fr" if is_fr else "nom_en"]} en tête.' if is_fr else f'Top 20 sun destinations in winter. {w1["nom_en"]} leads.',
            canonical=f'https://bestdateweather.com/{fname}',
            hreflang_fr='https://bestdateweather.com/classement-destinations-meteo-hiver-2026.html',
            hreflang_en='https://bestdateweather.com/en/best-destinations-winter-weather-2026.html',
            hero_eyebrow=f'{"Hiver" if is_fr else "Winter"} 2026',
            hero_title=f'Meilleures destinations<br/><em>hiver 2026</em>' if is_fr else 'Best destinations<br/><em>winter 2026</em>',
            hero_sub=f'{w1["nom_fr" if is_fr else "nom_en"]} en tête avec {w1["winter_avg"]}/10 en déc–fév.' if is_fr else f'{w1["nom_en"]} leads with {w1["winter_avg"]}/10 in Dec–Feb.',
            hero_stats=hstat(str(total), 'Destinations') + hstat('Dec–Feb', 'Période' if is_fr else 'Period'),
            insights='',
            sections=sections_list,
            is_fr=is_fr,
            en_file='best-destinations-winter-weather-2026.html',
            fr_file='classement-destinations-meteo-hiver-2026.html',
            prefix=prefix,
            schema=schema_json(by_winter, 20, is_fr),
        )
        with open(fname, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f'  ✅ {fname}')

        # ── 5. NOMAD RANKING ──
        fname = 'classement-destinations-meteo-nomades-2026.html' if is_fr else 'en/best-destinations-digital-nomads-weather-2026.html'
        nd1 = by_nomad_constancy[0] if by_nomad_constancy else by_nomad[0]

        sections_list = [
            section(
                'Classement nomades' if is_fr else 'Nomad ranking',
                '💻 Top 20 — Constance météo toute l\'année' if is_fr else '💻 Top 20 — Year-round weather consistency',
                f'Classement par score annuel + régularité (écart-type faible = météo stable). Exclut les destinations avec plus de 2 mois « avoid ».' if is_fr else 'Ranked by annual score + consistency (low std dev = stable weather). Excludes destinations with more than 2 "avoid" months.',
                make_table(by_nomad_constancy, is_fr, 'nomad', 20, prefix)
            ),
        ]

        html = page(
            title=f'Meilleures destinations digital nomads 2026 — Météo et régularité climatique' if is_fr else 'Best digital nomad destinations 2026 — Weather consistency ranking',
            desc=f'Classement des destinations à météo constante toute l\'année pour nomades digitaux.' if is_fr else 'Ranking of destinations with consistent year-round weather for digital nomads.',
            canonical=f'https://bestdateweather.com/{fname}',
            hreflang_fr='https://bestdateweather.com/classement-destinations-meteo-nomades-2026.html',
            hreflang_en='https://bestdateweather.com/en/best-destinations-digital-nomads-weather-2026.html',
            hero_eyebrow='Digital Nomads · 2026',
            hero_title=f'Meilleures destinations<br/><em>nomades digitaux 2026</em>' if is_fr else 'Best destinations<br/><em>digital nomads 2026</em>',
            hero_sub=f'Météo constante toute l\'année. {nd1["nom_fr" if is_fr else "nom_en"]} en tête.' if is_fr else f'Consistent weather year-round. {nd1["nom_en"]} leads.',
            hero_stats=hstat(str(len(by_nomad_constancy)), 'Destinations') + hstat('≤2', 'Mois avoid max' if is_fr else 'Max avoid months'),
            insights='',
            sections=sections_list,
            is_fr=is_fr,
            en_file='best-destinations-digital-nomads-weather-2026.html',
            fr_file='classement-destinations-meteo-nomades-2026.html',
            prefix=prefix,
            schema=schema_json(by_nomad_constancy, 20, is_fr),
        )
        with open(fname, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f'  ✅ {fname}')


if __name__ == '__main__':
    print('📊 Generating ranking pages...')
    generate_all()
    print('\n✅ 10 pages generated')
