#!/usr/bin/env python3
"""
Generate all 10 ranking pages (5 FR + 5 EN) from climate.csv + destinations.csv.
Usage: python3 generate_classements.py
"""

import csv, html, json, statistics
from pathlib import Path

ROOT = Path(__file__).parent

# ── Data Loading ──────────────────────────────────────────────────────────────

def load_destinations():
    dests = {}
    with open(ROOT / 'data/destinations.csv', encoding='utf-8-sig') as f:
        for r in csv.DictReader(f):
            dests[r['slug_fr']] = r
    return dests

def load_climate():
    """Returns dict: slug -> list of {mois_num, score, classe, tmin, tmax, rain_pct, precip_mm, sun_h}"""
    data = {}
    with open(ROOT / 'data/climate.csv', encoding='utf-8-sig') as f:
        for r in csv.DictReader(f):
            slug = r['slug']
            if slug not in data:
                data[slug] = {}
            m = int(r['mois_num'])
            data[slug][m] = {
                'score': float(r['score']),
                'classe': r['classe'],
                'tmin': float(r['tmin']),
                'tmax': float(r['tmax']),
                'rain_pct': float(r['rain_pct']),
                'precip_mm': float(r['precip_mm']),
                'sun_h': float(r['sun_h']),
            }
    return data

# ── Region Mapping ────────────────────────────────────────────────────────────

REGION_TAG = {
    # Europe du Sud
    'Italie': 'Europe du Sud', 'Grèce': 'Europe du Sud', 'Espagne': 'Europe du Sud',
    'Portugal': 'Europe du Sud', 'Croatie': 'Europe du Sud', 'Malte': 'Europe du Sud',
    'Monténégro': 'Europe du Sud', 'Albanie': 'Europe du Sud', 'Chypre': 'Europe du Sud',
    'Slovénie': 'Europe du Sud', 'Turquie': 'Europe du Sud',
    # Europe du Nord & Centrale
    'France': 'France', 'Allemagne': 'Europe Centrale', 'Pays-Bas': 'Europe Centrale',
    'Belgique': 'Europe Centrale', 'Autriche': 'Europe Centrale', 'Suisse': 'Europe Centrale',
    'République Tchèque': 'Europe Centrale', 'Hongrie': 'Europe Centrale', 'Pologne': 'Europe Centrale',
    'Roumanie': 'Europe Centrale', 'Royaume-Uni': 'Europe du Nord',
    'Écosse': 'Europe du Nord', 'Irlande': 'Europe du Nord',
    # Scandinavie
    'Norvège': 'Scandinavie', 'Suède': 'Scandinavie', 'Finlande': 'Scandinavie',
    'Danemark': 'Scandinavie', 'Islande': 'Scandinavie', 'Estonie': 'Baltique',
    'Lettonie': 'Baltique', 'Lituanie': 'Baltique',
    # Caucase
    'Géorgie': 'Caucase', 'Arménie': 'Caucase', 'Azerbaïdjan': 'Caucase',
    'Ouzbékistan': 'Asie Centrale',
    # Afrique du Nord
    'Maroc': 'Afrique du Nord', 'Tunisie': 'Afrique du Nord', 'Égypte': 'Afrique du Nord',
    'Cap-Vert': 'Afrique du Nord',
    # Afrique
    'Sénégal': 'Afrique', 'Kenya': 'Afrique', 'Tanzanie': 'Afrique', 'Namibie': 'Afrique',
    'Afrique du Sud': 'Afrique', 'Madagascar': 'Afrique', 'Rwanda': 'Afrique',
    'Éthiopie': 'Afrique', 'Ghana': 'Afrique', 'Mozambique': 'Afrique', 'Ouganda': 'Afrique',
    # Moyen-Orient
    'Émirats Arabes Unis': 'Moyen-Orient', 'Oman': 'Moyen-Orient', 'Jordanie': 'Moyen-Orient',
    'Israël': 'Moyen-Orient', 'Liban': 'Moyen-Orient', 'Qatar': 'Moyen-Orient',
    'Arabie Saoudite': 'Moyen-Orient',
    # Océan Indien
    'Maurice': 'Océan Indien', 'Seychelles': 'Océan Indien', 'Maldives': 'Océan Indien',
    'La Réunion': 'Océan Indien', 'Mayotte': 'Océan Indien',
    # Asie du Sud-Est
    'Thaïlande': 'Asie du Sud-Est', 'Viêt Nam': 'Asie du Sud-Est', 'Indonésie': 'Asie du Sud-Est',
    'Philippines': 'Asie du Sud-Est', 'Cambodge': 'Asie du Sud-Est', 'Laos': 'Asie du Sud-Est',
    'Malaisie': 'Asie du Sud-Est', 'Myanmar': 'Asie du Sud-Est', 'Singapour': 'Asie du Sud-Est',
    # Asie de l'Est
    'Japon': 'Asie de l\'Est', 'Corée du Sud': 'Asie de l\'Est', 'Taïwan': 'Asie de l\'Est',
    'Chine': 'Asie de l\'Est', 'Mongolie': 'Asie de l\'Est',
    # Asie du Sud
    'Inde': 'Asie du Sud', 'Sri Lanka': 'Asie du Sud', 'Népal': 'Asie du Sud',
    # Amérique du Nord
    'États-Unis': 'Amérique du Nord', 'Canada': 'Amérique du Nord',
    # Caraïbes
    'Cuba': 'Caraïbes', 'République Dominicaine': 'Caraïbes', 'Jamaïque': 'Caraïbes',
    'Barbade': 'Caraïbes', 'Bahamas': 'Caraïbes', 'Aruba': 'Caraïbes',
    'Porto Rico': 'Caraïbes', 'Curaçao': 'Caraïbes', 'Trinité-et-Tobago': 'Caraïbes',
    'Saint-Martin': 'Caraïbes',
    # Amérique Centrale
    'Mexique': 'Amérique Centrale', 'Costa Rica': 'Amérique Centrale',
    'Guatemala': 'Amérique Centrale', 'Nicaragua': 'Amérique Centrale',
    'Panama': 'Amérique Centrale', 'Belize': 'Amérique Centrale',
    'Honduras': 'Amérique Centrale', 'El Salvador': 'Amérique Centrale',
    # DOM-TOM
    'Guadeloupe': 'Caraïbes', 'Martinique': 'Caraïbes',
    'Guyane Française': 'Amérique du Sud', 'Polynésie Française': 'Océanie',
    'Nouvelle-Calédonie': 'Océanie',
    # Amérique du Sud
    'Argentine': 'Amérique du Sud', 'Brésil': 'Amérique du Sud', 'Chili': 'Amérique du Sud',
    'Colombie': 'Amérique du Sud', 'Pérou': 'Amérique du Sud', 'Équateur': 'Amérique du Sud',
    'Uruguay': 'Amérique du Sud', 'Bolivie': 'Amérique du Sud',
    # Océanie
    'Australie': 'Océanie', 'Nouvelle-Zélande': 'Océanie', 'Fidji': 'Océanie',
}

REGION_TAG_EN = {
    'Europe du Sud': 'Southern Europe', 'Europe Centrale': 'Central Europe',
    'Europe du Nord': 'Northern Europe', 'France': 'France',
    'Scandinavie': 'Scandinavia', 'Baltique': 'Baltics',
    'Caucase': 'Caucasus', 'Asie Centrale': 'Central Asia',
    'Afrique du Nord': 'North Africa', 'Afrique': 'Africa',
    'Moyen-Orient': 'Middle East', 'Océan Indien': 'Indian Ocean',
    'Asie du Sud-Est': 'Southeast Asia', "Asie de l'Est": 'East Asia',
    'Asie du Sud': 'South Asia', 'Amérique du Nord': 'North America',
    'Caraïbes': 'Caribbean', 'Amérique Centrale': 'Central America',
    'Amérique du Sud': 'South America', 'Océanie': 'Oceania',
}

EUROPE_COUNTRIES = {
    'Italie', 'Grèce', 'Espagne', 'Portugal', 'Croatie', 'Malte', 'Monténégro',
    'Albanie', 'Chypre', 'Slovénie', 'Turquie', 'France', 'Allemagne', 'Pays-Bas',
    'Belgique', 'Autriche', 'Suisse', 'République Tchèque', 'Hongrie', 'Pologne',
    'Roumanie', 'Royaume-Uni', 'Écosse', 'Irlande', 'Norvège', 'Suède', 'Finlande',
    'Danemark', 'Islande', 'Estonie', 'Lettonie', 'Lituanie',
    'Géorgie', 'Arménie', 'Azerbaïdjan',
}

# DOM-TOM: administrativement France, géographiquement hors Europe
DOM_TOM_SLUGS = {
    'reunion', 'guadeloupe', 'martinique', 'polynesie', 'bora-bora',
    'saint-martin', 'nouvelle-caledonie', 'mayotte', 'saint-barthelemy',
    'guyane', 'saint-pierre-et-miquelon',
}

MOIS_FR = {1:'Janvier',2:'Février',3:'Mars',4:'Avril',5:'Mai',6:'Juin',
           7:'Juillet',8:'Août',9:'Septembre',10:'Octobre',11:'Novembre',12:'Décembre'}
MOIS_EN = {1:'January',2:'February',3:'March',4:'April',5:'May',6:'June',
           7:'July',8:'August',9:'September',10:'October',11:'November',12:'December'}

# ── Ranking Computations ─────────────────────────────────────────────────────

def compute_annual(climate, dests, europe_only=False):
    """Annual average score ranking."""
    results = []
    for slug, monthly in climate.items():
        if slug not in dests:
            continue
        d = dests[slug]
        if europe_only and (d['pays'] not in EUROPE_COUNTRIES or slug in DOM_TOM_SLUGS):
            continue
        if len(monthly) < 12:
            continue
        avg = sum(monthly[m]['score'] for m in range(1,13)) / 12
        sun_total = sum(monthly[m]['sun_h'] for m in range(1,13)) * 30.44  # monthly hours -> annual
        rain_avg = sum(monthly[m]['rain_pct'] for m in range(1,13)) / 12
        best_month = max(range(1,13), key=lambda m: monthly[m]['score'])
        results.append({
            'slug': slug, 'dest': d, 'avg': avg, 'sun_annual': sun_total,
            'rain_avg': rain_avg, 'best_month': best_month, 'monthly': monthly,
        })
    results.sort(key=lambda x: -x['avg'])
    return results

def compute_seasonal(climate, dests, months, europe_only=False):
    """Seasonal average score ranking for given months."""
    results = []
    for slug, monthly in climate.items():
        if slug not in dests:
            continue
        d = dests[slug]
        if europe_only and (d['pays'] not in EUROPE_COUNTRIES or slug in DOM_TOM_SLUGS):
            continue
        if not all(m in monthly for m in months):
            continue
        avg = sum(monthly[m]['score'] for m in months) / len(months)
        sun = sum(monthly[m]['sun_h'] for m in months) * 30.44
        rain = sum(monthly[m]['rain_pct'] for m in months) / len(months)
        tmax_avg = sum(monthly[m]['tmax'] for m in months) / len(months)
        results.append({
            'slug': slug, 'dest': d, 'avg': avg, 'sun': sun,
            'rain_avg': rain, 'tmax_avg': tmax_avg, 'monthly': monthly,
        })
    results.sort(key=lambda x: -x['avg'])
    return results

def compute_nomad(climate, dests):
    """Nomad ranking: high average + low variance."""
    results = []
    for slug, monthly in climate.items():
        if slug not in dests:
            continue
        d = dests[slug]
        if len(monthly) < 12:
            continue
        scores = [monthly[m]['score'] for m in range(1,13)]
        avg = sum(scores) / 12
        stdev = statistics.stdev(scores)
        # Nomad score = average - penalty for variance
        nomad_score = avg - stdev * 0.5
        worst_month = min(range(1,13), key=lambda m: monthly[m]['score'])
        worst_score = monthly[worst_month]['score']
        results.append({
            'slug': slug, 'dest': d, 'avg': avg, 'stdev': stdev,
            'nomad_score': nomad_score, 'worst_month': worst_month,
            'worst_score': worst_score, 'monthly': monthly,
        })
    results.sort(key=lambda x: -x['nomad_score'])
    return results

def compute_sunniest(climate, dests):
    results = []
    for slug, monthly in climate.items():
        if slug not in dests:
            continue
        if len(monthly) < 12:
            continue
        sun_total = sum(monthly[m]['sun_h'] for m in range(1,13)) * 30.44
        avg = sum(monthly[m]['score'] for m in range(1,13)) / 12
        rain = sum(monthly[m]['rain_pct'] for m in range(1,13)) / 12
        results.append({
            'slug': slug, 'dest': dests[slug], 'sun_annual': sun_total,
            'avg': avg, 'rain_avg': rain,
        })
    results.sort(key=lambda x: -x['sun_annual'])
    return results

def compute_driest(climate, dests):
    results = []
    for slug, monthly in climate.items():
        if slug not in dests:
            continue
        if len(monthly) < 12:
            continue
        rain = sum(monthly[m]['rain_pct'] for m in range(1,13)) / 12
        sun_total = sum(monthly[m]['sun_h'] for m in range(1,13)) * 30.44
        avg = sum(monthly[m]['score'] for m in range(1,13)) / 12
        results.append({
            'slug': slug, 'dest': dests[slug], 'rain_avg': rain,
            'avg': avg, 'sun_annual': sun_total,
        })
    results.sort(key=lambda x: x['rain_avg'])
    return results

# ── HTML Generation ───────────────────────────────────────────────────────────

CSS = r"""
*{margin:0;padding:0;box-sizing:border-box}
:root{--navy:#1a2332;--gold:#d4a853;--cream:#faf6ef;--cream2:#ede4d3;--text:#2c3e50;--slate:#5a6c7d;--slate2:#8899a6}
body{font-family:'DM Sans',system-ui,sans-serif;background:var(--cream);color:var(--text);line-height:1.6}
.hero{background:var(--navy);color:white;padding:48px 20px 36px;text-align:center}
.hero-eyebrow{font-size:11px;text-transform:uppercase;letter-spacing:2.5px;color:var(--gold);margin-bottom:12px;font-weight:700}
.hero-title{font-family:'Playfair Display',Georgia,serif;font-size:clamp(24px,5vw,38px);margin-bottom:10px;line-height:1.2}
.hero-title em{color:var(--gold);font-style:italic}
.hero-sub{font-size:15px;opacity:.75;max-width:600px;margin:0 auto 20px}
.hero-stats{display:flex;justify-content:center;gap:36px;margin-top:16px}
.hstat{text-align:center}.hstat-val{display:block;font-size:22px;font-weight:700;color:var(--gold)}.hstat-lbl{font-size:11px;opacity:.6;text-transform:uppercase;letter-spacing:1px}
.insights-bar{background:#1e2a3a;border-top:1px solid rgba(255,255,255,.06)}
.insights-inner{max-width:960px;margin:0 auto;padding:18px 20px}
.insights-label{font-size:10px;text-transform:uppercase;letter-spacing:2px;color:var(--gold);margin-bottom:10px;font-weight:700}
.insights-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:10px}
.insight-item{font-size:13px;color:rgba(255,255,255,.7);line-height:1.5}
.insight-item strong{color:var(--gold);display:block;font-size:11px;text-transform:uppercase;letter-spacing:.5px;margin-bottom:2px}
.page{max-width:960px;margin:0 auto;padding:28px 20px 40px}
.section{margin-bottom:36px}
.eyebrow{font-size:10px;text-transform:uppercase;letter-spacing:2px;color:var(--gold);font-weight:700;margin-bottom:6px}
.sec-title{font-family:'Playfair Display',Georgia,serif;font-size:clamp(18px,4vw,24px);margin-bottom:8px}
.sec-intro{font-size:14px;color:var(--slate);margin-bottom:18px}
.rt{width:100%;border-collapse:collapse;font-size:13px}
.rt th{background:var(--navy);color:white;padding:10px 12px;text-align:left;font-size:11px;text-transform:uppercase;letter-spacing:.5px;font-weight:700;position:sticky;top:0}
.rt td{padding:10px 12px;border-bottom:1px solid var(--cream2);vertical-align:middle}
.rt tr:hover{background:#fef9f0}
.rt .rank{font-weight:700;font-size:15px;text-align:center;width:48px}
.rt .sc{font-weight:700;color:var(--navy);font-size:14px;white-space:nowrap}
.rt .sc span{font-weight:400;color:var(--slate2);font-size:11px}
.dest-link{color:var(--text);text-decoration:none;font-weight:600}
.dest-link:hover{color:var(--gold)}
.region-tag{display:inline-block;font-size:10px;color:var(--slate2);background:var(--cream);padding:2px 8px;border-radius:10px;margin-left:8px;vertical-align:middle}
.card{background:white;border:1.5px solid var(--cream2);border-radius:14px;padding:24px;margin-bottom:20px}
.card h3{font-family:'Playfair Display',Georgia,serif;font-size:17px;margin-bottom:8px}
.card p{font-size:14px;color:var(--slate);line-height:1.7}
.card ol li strong,.card ul li strong{color:var(--text)}
.meth{background:var(--navy);color:white;border-radius:14px;padding:30px;margin-bottom:28px}
.meth h2,.meth strong{font-family:'Playfair Display',Georgia,serif;font-size:20px;margin-bottom:14px;color:var(--gold)}
.meth p,.meth li{font-size:14px;line-height:1.75;opacity:.85}
.meth ul{padding-left:20px;margin-top:10px}
.meth li{margin-bottom:5px}
.related-pages{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:12px;margin-top:16px}
.related-card{background:white;border:1.5px solid var(--cream2);border-radius:12px;padding:16px;text-decoration:none;color:var(--text);display:block}
.related-card:hover{border-color:var(--gold);background:#fffbf0}
.related-card strong{display:block;font-size:13px;font-weight:700;margin-bottom:4px}
.related-card span{font-size:11px;color:var(--slate2)}
footer{background:var(--navy);color:rgba(255,255,255,.7);text-align:center;padding:36px 20px;font-size:12px;line-height:2}
footer a{color:rgba(255,255,255,.8);text-decoration:none}
@media(max-width:640px){.rt th:nth-child(5),.rt td:nth-child(5){display:none}.hero-stats{gap:20px}}
"""

def e(s):
    """HTML-escape."""
    return html.escape(str(s))

def rank_icon(i):
    if i == 1: return '🥇'
    if i == 2: return '🥈'
    if i == 3: return '🥉'
    return str(i)

def dest_link(slug, nom, lang):
    if lang == 'fr':
        return f'meilleure-periode-{slug}.html'
    else:
        return f'../best-time-to-visit-{slug}.html'

def region_tag(pays, lang):
    tag = REGION_TAG.get(pays, '')
    if not tag:
        return ''
    if lang == 'en':
        tag = REGION_TAG_EN.get(tag, tag)
    return f'<span class="region-tag">{e(tag)}</span>'

def make_table_annual(entries, n, lang):
    """Generate top-N annual ranking table."""
    mois = MOIS_EN if lang == 'en' else MOIS_FR
    headers = {
        'fr': ('Rang','Destination','Meilleur mois','Score annuel','Soleil/an','Pluie moy.'),
        'en': ('Rank','Destination','Best month','Annual score','Sun/year','Avg. rain'),
    }
    h = headers[lang]
    rows = []
    for i, entry in enumerate(entries[:n], 1):
        d = entry['dest']
        nom = d['nom_en'] if lang == 'en' else d['nom_fr']
        link = dest_link(entry['slug'], nom, lang)
        rows.append(
            f'<tr><td class="rank">{rank_icon(i)}</td>'
            f'<td><a href="{link}" class="dest-link">{e(nom)}</a>{region_tag(d["pays"], lang)}</td>'
            f'<td>{mois[entry["best_month"]]}</td>'
            f'<td class="sc">{entry["avg"]:.1f}<span>/10</span></td>'
            f'<td>{entry["sun_annual"]:.0f}h</td>'
            f'<td>{entry["rain_avg"]:.0f}%</td></tr>'
        )
    return (
        f'<table class="rt"><thead><tr>{"".join(f"<th>{x}</th>" for x in h)}</tr></thead>'
        f'<tbody>{"".join(rows)}</tbody></table>'
    )

def make_table_seasonal(entries, n, lang):
    headers = {
        'fr': ('Rang','Destination','Score','Temp. max','Soleil','Pluie'),
        'en': ('Rank','Destination','Score','Max temp.','Sun','Rain'),
    }
    h = headers[lang]
    rows = []
    for i, entry in enumerate(entries[:n], 1):
        d = entry['dest']
        nom = d['nom_en'] if lang == 'en' else d['nom_fr']
        link = dest_link(entry['slug'], nom, lang)
        rows.append(
            f'<tr><td class="rank">{rank_icon(i)}</td>'
            f'<td><a href="{link}" class="dest-link">{e(nom)}</a>{region_tag(d["pays"], lang)}</td>'
            f'<td class="sc">{entry["avg"]:.1f}<span>/10</span></td>'
            f'<td>{entry["tmax_avg"]:.0f}°C</td>'
            f'<td>{entry["sun"]:.0f}h</td>'
            f'<td>{entry["rain_avg"]:.0f}%</td></tr>'
        )
    return (
        f'<table class="rt"><thead><tr>{"".join(f"<th>{x}</th>" for x in h)}</tr></thead>'
        f'<tbody>{"".join(rows)}</tbody></table>'
    )

def make_table_sun(entries, n, lang):
    headers = {
        'fr': ('Rang','Destination','Soleil/an','Score annuel','Pluie moy.'),
        'en': ('Rank','Destination','Sun/year','Annual score','Avg. rain'),
    }
    h = headers[lang]
    rows = []
    for i, entry in enumerate(entries[:n], 1):
        d = entry['dest']
        nom = d['nom_en'] if lang == 'en' else d['nom_fr']
        link = dest_link(entry['slug'], nom, lang)
        rows.append(
            f'<tr><td class="rank">{rank_icon(i)}</td>'
            f'<td><a href="{link}" class="dest-link">{e(nom)}</a>{region_tag(d["pays"], lang)}</td>'
            f'<td>{entry["sun_annual"]:.0f}h</td>'
            f'<td class="sc">{entry["avg"]:.1f}<span>/10</span></td>'
            f'<td>{entry["rain_avg"]:.0f}%</td></tr>'
        )
    return (
        f'<table class="rt"><thead><tr>{"".join(f"<th>{x}</th>" for x in h)}</tr></thead>'
        f'<tbody>{"".join(rows)}</tbody></table>'
    )

def make_table_rain(entries, n, lang):
    headers = {
        'fr': ('Rang','Destination','Pluie moy.','Score annuel','Soleil/an'),
        'en': ('Rank','Destination','Avg. rain','Annual score','Sun/year'),
    }
    h = headers[lang]
    rows = []
    for i, entry in enumerate(entries[:n], 1):
        d = entry['dest']
        nom = d['nom_en'] if lang == 'en' else d['nom_fr']
        link = dest_link(entry['slug'], nom, lang)
        rows.append(
            f'<tr><td class="rank">{rank_icon(i)}</td>'
            f'<td><a href="{link}" class="dest-link">{e(nom)}</a>{region_tag(d["pays"], lang)}</td>'
            f'<td>{entry["rain_avg"]:.0f}%</td>'
            f'<td class="sc">{entry["avg"]:.1f}<span>/10</span></td>'
            f'<td>{entry["sun_annual"]:.0f}h</td></tr>'
        )
    return (
        f'<table class="rt"><thead><tr>{"".join(f"<th>{x}</th>" for x in h)}</tr></thead>'
        f'<tbody>{"".join(rows)}</tbody></table>'
    )

def make_table_nomad(entries, n, lang):
    headers = {
        'fr': ('Rang','Destination','Score moyen','Écart-type','Pire mois','Score pire'),
        'en': ('Rank','Destination','Avg. score','Std. dev.','Worst month','Worst score'),
    }
    mois = MOIS_EN if lang == 'en' else MOIS_FR
    h = headers[lang]
    rows = []
    for i, entry in enumerate(entries[:n], 1):
        d = entry['dest']
        nom = d['nom_en'] if lang == 'en' else d['nom_fr']
        link = dest_link(entry['slug'], nom, lang)
        rows.append(
            f'<tr><td class="rank">{rank_icon(i)}</td>'
            f'<td><a href="{link}" class="dest-link">{e(nom)}</a>{region_tag(d["pays"], lang)}</td>'
            f'<td class="sc">{entry["avg"]:.1f}<span>/10</span></td>'
            f'<td>{entry["stdev"]:.2f}</td>'
            f'<td>{mois[entry["worst_month"]]}</td>'
            f'<td>{entry["worst_score"]:.1f}</td></tr>'
        )
    return (
        f'<table class="rt"><thead><tr>{"".join(f"<th>{x}</th>" for x in h)}</tr></thead>'
        f'<tbody>{"".join(rows)}</tbody></table>'
    )

# ── JSON-LD ───────────────────────────────────────────────────────────────────

def make_jsonld(entries, n, title, lang):
    items = []
    for i, entry in enumerate(entries[:n], 1):
        d = entry['dest']
        nom = d['nom_en'] if lang == 'en' else d['nom_fr']
        slug = entry['slug']
        if lang == 'fr':
            url = f'https://bestdateweather.com/meilleure-periode-{slug}.html'
        else:
            url = f'https://bestdateweather.com/best-time-to-visit-{slug}.html'
        items.append({"@type":"ListItem","position":i,"name":nom,"url":url})
    return json.dumps({
        "@context":"https://schema.org","@type":"ItemList",
        "name":title,"numberOfItems":n,"itemListElement":items
    }, ensure_ascii=False)

# ── Related Pages ─────────────────────────────────────────────────────────────

RELATED_FR = [
    ('classement-destinations-meteo-2026.html', '🏆 Classement global 2026', '318 destinations'),
    ('classement-destinations-europe-meteo-2026.html', '🇪🇺 Top Europe météo 2026', 'Comparatif européen'),
    ('classement-destinations-meteo-ete-2026.html', '☀️ Meilleures destinations été', 'Juin–Juil–Août'),
    ('classement-destinations-meteo-hiver-2026.html', '❄️ Meilleures destinations hiver', 'Déc–Jan–Fév'),
    ('classement-destinations-meteo-nomades-2026.html', '💻 Meilleures destinations nomades', 'Régularité & confort'),
]

RELATED_EN = [
    ('best-destinations-weather-ranking-2026.html', '🏆 Global ranking 2026', '318 destinations'),
    ('best-europe-weather-ranking-2026.html', '🇪🇺 Europe weather ranking', 'European comparison'),
    ('best-destinations-summer-weather-2026.html', '☀️ Best summer destinations', 'June–July–August'),
    ('best-destinations-winter-weather-2026.html', '❄️ Best winter destinations', 'Dec–Jan–Feb'),
    ('best-destinations-digital-nomads-weather-2026.html', '💻 Best nomad destinations', 'Consistency & comfort'),
]

def make_related(lang, exclude_href=''):
    related = RELATED_EN if lang == 'en' else RELATED_FR
    cards = ''
    for href, title, sub in related:
        if href == exclude_href:
            continue
        cards += f'<a href="{href}" class="related-card"><strong>{title}</strong><span>{sub}</span></a>\n'
    return f'<div class="related-pages">\n{cards}</div>'

# ── Methodology ───────────────────────────────────────────────────────────────

METH_FR = (
    '<div class="meth"><strong>Méthodologie</strong>'
    '<p>Scores calculés sur 10 ans d\'archives Open-Meteo (ERA5). '
    'Chaque mois noté sur ensoleillement (40&nbsp;%), précipitations (30&nbsp;%), '
    'confort thermique (30&nbsp;%). Score annuel = moyenne des 12 mois. '
    '318 destinations analysées.</p></div>'
)
METH_EN = (
    '<div class="meth"><strong>Methodology</strong>'
    '<p>Scores computed from 10 years of Open-Meteo archives (ERA5). '
    'Each month rated on sunshine (40%), precipitation (30%), '
    'thermal comfort (30%). Annual score = average of 12 months. '
    '318 destinations analyzed.</p></div>'
)

# ── Footer ────────────────────────────────────────────────────────────────────

FOOTER_FR = """<footer>
<p style="color:rgba(255,255,255,.7);font-size:13px;font-weight:700;margin-bottom:8px">bestdateweather.com</p>
<p><a href="https://open-meteo.com/" rel="noopener" style="color:rgba(255,255,255,.7)">Données météo par Open-Meteo.com</a> · Sources ECMWF, DWD, NOAA, Météo-France · CC BY 4.0</p>
<p style="margin-top:8px"><a href="note_modele.html" style="color:rgba(255,255,255,.7)">Méthodologie</a> · <a href="index.html" style="color:rgba(255,255,255,.7)">Application météo</a> · <a href="en/{en_file}" style="color:rgba(255,255,255,.7)"><img src="flags/gb.png" width="20" height="15" alt="" style="vertical-align:middle;border-radius:2px"> English</a></p>
<p style="margin-top:8px;font-size:11px;opacity:.6"><a href="mentions-legales.html" style="color:rgba(255,255,255,.7)">Mentions légales</a></p>
</footer>"""

FOOTER_EN = """<footer>
<p style="color:rgba(255,255,255,.7);font-size:13px;font-weight:700;margin-bottom:8px">bestdateweather.com</p>
<p><a href="https://open-meteo.com/" rel="noopener" style="color:rgba(255,255,255,.7)">Weather data by Open-Meteo.com</a> · Sources ECMWF, DWD, NOAA, Météo-France · CC BY 4.0</p>
<p style="margin-top:8px"><a href="../note_modele.html" style="color:rgba(255,255,255,.7)">Methodology</a> · <a href="app.html" style="color:rgba(255,255,255,.7)">Weather app</a> · <a href="../{fr_file}" style="color:rgba(255,255,255,.7)"><img src="../flags/fr.png" width="20" height="15" alt="" style="vertical-align:middle;border-radius:2px"> Français</a></p>
<p style="margin-top:8px;font-size:11px;opacity:.6"><a href="../mentions-legales.html" style="color:rgba(255,255,255,.7)">Legal</a></p>
</footer>"""

# ── Page Assembly ─────────────────────────────────────────────────────────────

def make_page(*, title, description, h1, hero_sub, stats_html, insights_html,
              sections, jsonld_str, related_html, meth_html, footer_html, lang, canonical):
    fonts = (
        '<link rel="preconnect" href="https://fonts.googleapis.com"/>'
        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin/>'
        '<link rel="preload" as="style" href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;1,700&family=DM+Sans:wght@400;500;700&display=swap" onload="this.onload=null;this.rel=\'stylesheet\'"/>'
        '<noscript><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;1,700&family=DM+Sans:wght@400;500;700&display=swap"/></noscript>'
    )
    sections_html = ''
    for sec in sections:
        sections_html += (
            f'<div class="section">'
            f'<div class="eyebrow">{sec["eyebrow"]}</div>'
            f'<h2 class="sec-title">{sec["h2"]}</h2>'
            f'<p class="sec-intro">{sec["intro"]}</p>'
            f'<div style="overflow-x:auto">{sec["table"]}</div>'
            f'</div>'
        )

    return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="UTF-8"/><meta name="viewport" content="width=device-width,initial-scale=1.0"/>
<title>{e(title)}</title>
<meta name="description" content="{e(description)}"/>
<link rel="canonical" href="{canonical}"/>
<style>{CSS}</style>
{fonts}
<script type="application/ld+json">{jsonld_str}</script>
<meta property="og:title" content="{e(title)}"/>
<meta property="og:description" content="{e(description)}"/>
<meta property="og:image" content="https://bestdateweather.com/og-image.png"/>
<meta property="og:image:width" content="1200"/>
<meta property="og:image:height" content="630"/>
<meta name="twitter:card" content="summary_large_image"/>
</head>
<body>
<header class="hero">
<div class="hero-eyebrow">{"Independent climate study · 2026" if lang == "en" else "Étude climatique indépendante · 2026"}</div>
<h1 class="hero-title">{h1}</h1>
<p class="hero-sub">{hero_sub}</p>
{stats_html}
</header>
{insights_html}
<main class="page">
{sections_html}
{meth_html}
{related_html}
</main>
{footer_html}
</body></html>"""


# ══════════════════════════════════════════════════════════════════════════════
# PAGE GENERATORS
# ══════════════════════════════════════════════════════════════════════════════

def gen_mondial(dests, climate, lang):
    annual = compute_annual(climate, dests)
    sunniest = compute_sunniest(climate, dests)
    driest = compute_driest(climate, dests)
    top1 = annual[0]
    sun1 = sunniest[0]
    dry1 = driest[0]
    # Find top Europe
    europe_annual = compute_annual(climate, dests, europe_only=True)
    eu1 = europe_annual[0]
    n_dests = len(annual)

    if lang == 'fr':
        title = f'Classement 2026 des meilleures destinations selon 10 ans de données météo'
        desc = f'{n_dests} destinations classées sur 10 ans de données météo. Top mondial, plus ensoleillées, moins pluvieuses.'
        h1 = 'Classement 2026 des meilleures<br/><em>destinations météo</em>'
        hero_sub = f'{n_dests} destinations analysées sur 10 ans. {top1["dest"]["nom_bare"]} en tête avec {top1["avg"]:.1f}/10.'
        stats = f'<div class="hero-stats"><div class="hstat"><span class="hstat-val">{n_dests}</span><span class="hstat-lbl">Destinations</span></div><div class="hstat"><span class="hstat-val">10 ans</span><span class="hstat-lbl">Données</span></div><div class="hstat"><span class="hstat-val">{n_dests * 10 * 365 // 1000}&nbsp;000+</span><span class="hstat-lbl">Jours mesurés</span></div></div>'
        insights = f'<div class="insights-bar"><div class="insights-inner"><div class="insights-label">Points clés</div><div class="insights-grid"><div class="insight-item"><strong>N°1 mondial</strong>{top1["dest"]["nom_bare"]} — {top1["avg"]:.1f}/10 annuel.</div><div class="insight-item"><strong>Plus ensoleillé</strong>{sun1["dest"]["nom_bare"]} — {sun1["sun_annual"]:.0f}h/an.</div><div class="insight-item"><strong>Plus sec</strong>{dry1["dest"]["nom_bare"]} — {dry1["rain_avg"]:.0f}% de pluie.</div><div class="insight-item"><strong>Europe</strong>{eu1["dest"]["nom_bare"]} domine avec {eu1["avg"]:.1f}/10.</div></div></div></div>'
        sections = [
            {'eyebrow':'Classement mondial', 'h2':f'🏆 Top 20 mondial — Score climatique annuel', 'intro':f'Score annuel = moyenne des 12 scores mensuels (0–10). {n_dests} destinations analysées.', 'table': make_table_annual(annual, 20, lang)},
            {'eyebrow':'Ensoleillement', 'h2':'☀️ Top 10 les plus ensoleillées', 'intro':'Heures de soleil cumulées sur l\'année.', 'table': make_table_sun(sunniest, 10, lang)},
            {'eyebrow':'Précipitations', 'h2':'🌂 Top 10 les moins pluvieuses', 'intro':'Pourcentage moyen de jours de pluie sur l\'année.', 'table': make_table_rain(driest, 10, lang)},
        ]
        jsonld = make_jsonld(annual, 40, f'Top {n_dests} meilleures destinations météo 2026', lang)
        related = make_related(lang, 'classement-destinations-meteo-2026.html')
        fr_file = 'classement-destinations-meteo-2026.html'
        en_file = 'best-destinations-weather-ranking-2026.html'
        canonical = f'https://bestdateweather.com/{fr_file}' if lang == 'fr' else f'https://bestdateweather.com/en/{en_file}'
        footer = FOOTER_FR.format(en_file=en_file)
        meth = METH_FR
        outfile = ROOT / fr_file
    else:
        title = 'Best weather destinations 2026 — 10-year climate ranking'
        desc = f'{n_dests} destinations ranked using 10 years of weather data. Global top, sunniest, driest.'
        h1 = 'Best weather<br/><em>destinations 2026</em>'
        hero_sub = f'{n_dests} destinations analyzed over 10 years. {top1["dest"]["nom_en"]} leads with {top1["avg"]:.1f}/10.'
        stats = f'<div class="hero-stats"><div class="hstat"><span class="hstat-val">{n_dests}</span><span class="hstat-lbl">Destinations</span></div><div class="hstat"><span class="hstat-val">10 years</span><span class="hstat-lbl">Data</span></div><div class="hstat"><span class="hstat-val">{n_dests * 10 * 365 // 1000},000+</span><span class="hstat-lbl">Days measured</span></div></div>'
        insights = f'<div class="insights-bar"><div class="insights-inner"><div class="insights-label">Key insights</div><div class="insights-grid"><div class="insight-item"><strong>#1 worldwide</strong>{top1["dest"]["nom_en"]} — {top1["avg"]:.1f}/10 annual.</div><div class="insight-item"><strong>Sunniest</strong>{sun1["dest"]["nom_en"]} — {sun1["sun_annual"]:.0f}h/yr.</div><div class="insight-item"><strong>Driest</strong>{dry1["dest"]["nom_en"]} — {dry1["rain_avg"]:.0f}% rain.</div><div class="insight-item"><strong>Europe</strong>{eu1["dest"]["nom_en"]} leads with {eu1["avg"]:.1f}/10.</div></div></div></div>'
        sections = [
            {'eyebrow':'Global ranking', 'h2':'🏆 Top 20 worldwide — Annual climate score', 'intro':f'Annual score = average of 12 monthly scores (0–10). {n_dests} destinations analyzed.', 'table': make_table_annual(annual, 20, lang)},
            {'eyebrow':'Sunshine', 'h2':'☀️ Top 10 sunniest', 'intro':'Cumulative sunshine hours per year.', 'table': make_table_sun(sunniest, 10, lang)},
            {'eyebrow':'Precipitation', 'h2':'🌂 Top 10 driest', 'intro':'Average percentage of rainy days per year.', 'table': make_table_rain(driest, 10, lang)},
        ]
        jsonld = make_jsonld(annual, 40, 'Top weather destinations 2026', lang)
        related = make_related(lang, 'best-destinations-weather-ranking-2026.html')
        fr_file = 'classement-destinations-meteo-2026.html'
        en_file = 'best-destinations-weather-ranking-2026.html'
        canonical = f'https://bestdateweather.com/en/{en_file}'
        footer = FOOTER_EN.format(fr_file=fr_file)
        meth = METH_EN
        outfile = ROOT / 'en' / en_file

    page = make_page(
        title=title, description=desc, h1=h1, hero_sub=hero_sub,
        stats_html=stats, insights_html=insights, sections=sections,
        jsonld_str=jsonld, related_html=related, meth_html=meth,
        footer_html=footer, lang=lang, canonical=canonical
    )
    outfile.write_text(page, encoding='utf-8')
    print(f'  ✓ {outfile.name} ({n_dests} dests, top={top1["dest"]["nom_bare"]})')


def gen_europe(dests, climate, lang):
    annual = compute_annual(climate, dests, europe_only=True)
    summer = compute_seasonal(climate, dests, [6,7,8], europe_only=True)
    winter = compute_seasonal(climate, dests, [12,1,2], europe_only=True)
    top1 = annual[0]
    n_dests = len(annual)

    if lang == 'fr':
        title = 'Classement météo Europe 2026 — Top destinations européennes'
        desc = f'{n_dests} destinations européennes classées. Top annuel, été et hiver.'
        h1 = 'Top destinations<br/><em>météo Europe 2026</em>'
        hero_sub = f'{n_dests} destinations européennes. {top1["dest"]["nom_bare"]} en tête avec {top1["avg"]:.1f}/10.'
        stats = f'<div class="hero-stats"><div class="hstat"><span class="hstat-val">{n_dests}</span><span class="hstat-lbl">Destinations</span></div><div class="hstat"><span class="hstat-val">10 ans</span><span class="hstat-lbl">Données</span></div></div>'
        insights = f'<div class="insights-bar"><div class="insights-inner"><div class="insights-label">Points clés</div><div class="insights-grid"><div class="insight-item"><strong>N°1 Europe</strong>{top1["dest"]["nom_bare"]} — {top1["avg"]:.1f}/10.</div><div class="insight-item"><strong>Été</strong>{summer[0]["dest"]["nom_bare"]} domine ({summer[0]["avg"]:.1f}/10).</div><div class="insight-item"><strong>Hiver</strong>{winter[0]["dest"]["nom_bare"]} en tête ({winter[0]["avg"]:.1f}/10).</div></div></div></div>'
        sections = [
            {'eyebrow':'Europe', 'h2':'🏆 Top 20 Europe — Score annuel', 'intro':f'{n_dests} destinations européennes classées par score annuel.', 'table': make_table_annual(annual, 20, lang)},
            {'eyebrow':'Été', 'h2':'☀️ Top 10 Europe été (juin–août)', 'intro':'Score moyen juin, juillet, août.', 'table': make_table_seasonal(summer, 10, lang)},
            {'eyebrow':'Hiver', 'h2':'❄️ Top 10 Europe hiver (déc–fév)', 'intro':'Score moyen décembre, janvier, février.', 'table': make_table_seasonal(winter, 10, lang)},
        ]
        jsonld = make_jsonld(annual, 20, 'Top destinations météo Europe 2026', lang)
        related = make_related(lang, 'classement-destinations-europe-meteo-2026.html')
        fr_file = 'classement-destinations-europe-meteo-2026.html'
        en_file = 'best-europe-weather-ranking-2026.html'
        canonical = f'https://bestdateweather.com/{fr_file}'
        footer = FOOTER_FR.format(en_file=en_file)
        meth = METH_FR
        outfile = ROOT / fr_file
    else:
        title = 'Europe weather ranking 2026 — Top European destinations'
        desc = f'{n_dests} European destinations ranked. Annual, summer and winter tops.'
        h1 = 'Top European<br/><em>weather destinations 2026</em>'
        hero_sub = f'{n_dests} European destinations. {top1["dest"]["nom_en"]} leads with {top1["avg"]:.1f}/10.'
        stats = f'<div class="hero-stats"><div class="hstat"><span class="hstat-val">{n_dests}</span><span class="hstat-lbl">Destinations</span></div><div class="hstat"><span class="hstat-val">10 years</span><span class="hstat-lbl">Data</span></div></div>'
        insights = f'<div class="insights-bar"><div class="insights-inner"><div class="insights-label">Key insights</div><div class="insights-grid"><div class="insight-item"><strong>#1 Europe</strong>{top1["dest"]["nom_en"]} — {top1["avg"]:.1f}/10.</div><div class="insight-item"><strong>Summer</strong>{summer[0]["dest"]["nom_en"]} leads ({summer[0]["avg"]:.1f}/10).</div><div class="insight-item"><strong>Winter</strong>{winter[0]["dest"]["nom_en"]} leads ({winter[0]["avg"]:.1f}/10).</div></div></div></div>'
        sections = [
            {'eyebrow':'Europe', 'h2':'🏆 Top 20 Europe — Annual score', 'intro':f'{n_dests} European destinations ranked by annual score.', 'table': make_table_annual(annual, 20, lang)},
            {'eyebrow':'Summer', 'h2':'☀️ Top 10 Europe summer (June–Aug)', 'intro':'Average score June, July, August.', 'table': make_table_seasonal(summer, 10, lang)},
            {'eyebrow':'Winter', 'h2':'❄️ Top 10 Europe winter (Dec–Feb)', 'intro':'Average score December, January, February.', 'table': make_table_seasonal(winter, 10, lang)},
        ]
        jsonld = make_jsonld(annual, 20, 'Top European weather destinations 2026', lang)
        related = make_related(lang, 'best-europe-weather-ranking-2026.html')
        fr_file = 'classement-destinations-europe-meteo-2026.html'
        en_file = 'best-europe-weather-ranking-2026.html'
        canonical = f'https://bestdateweather.com/en/{en_file}'
        footer = FOOTER_EN.format(fr_file=fr_file)
        meth = METH_EN
        outfile = ROOT / 'en' / en_file

    page = make_page(
        title=title, description=desc, h1=h1, hero_sub=hero_sub,
        stats_html=stats, insights_html=insights, sections=sections,
        jsonld_str=jsonld, related_html=related, meth_html=meth,
        footer_html=footer, lang=lang, canonical=canonical
    )
    outfile.write_text(page, encoding='utf-8')
    print(f'  ✓ {outfile.name} ({n_dests} dests Europe)')


def gen_ete(dests, climate, lang):
    summer = compute_seasonal(climate, dests, [6,7,8])
    top1 = summer[0]
    n_dests = len(summer)

    if lang == 'fr':
        title = 'Meilleures destinations été 2026 — Classement météo Juin–Août'
        desc = f'Top {n_dests} destinations pour l\'été 2026. Classement basé sur 10 ans de données météo juin–août.'
        h1 = 'Meilleures destinations<br/><em>été 2026</em>'
        hero_sub = f'{top1["dest"]["nom_bare"]} en tête avec {top1["avg"]:.1f}/10 sur juin–août.'
        stats = f'<div class="hero-stats"><div class="hstat"><span class="hstat-val">{n_dests}</span><span class="hstat-lbl">Destinations</span></div><div class="hstat"><span class="hstat-val">Juin–Août</span><span class="hstat-lbl">Période</span></div></div>'
        insights = f'<div class="insights-bar"><div class="insights-inner"><div class="insights-label">Points clés</div><div class="insights-grid"><div class="insight-item"><strong>N°1 été</strong>{top1["dest"]["nom_bare"]} — {top1["avg"]:.1f}/10.</div><div class="insight-item"><strong>N°2</strong>{summer[1]["dest"]["nom_bare"]} — {summer[1]["avg"]:.1f}/10.</div><div class="insight-item"><strong>N°3</strong>{summer[2]["dest"]["nom_bare"]} — {summer[2]["avg"]:.1f}/10.</div></div></div></div>'
        sections = [
            {'eyebrow':'Été 2026', 'h2':'☀️ Top 20 mondial — Été 2026 (juin–août)', 'intro':f'Score moyen sur les 3 mois d\'été. {n_dests} destinations.', 'table': make_table_seasonal(summer, 20, lang)},
        ]
        jsonld = make_jsonld(summer, 20, 'Meilleures destinations été 2026', lang)
        related = make_related(lang, 'classement-destinations-meteo-ete-2026.html')
        fr_file = 'classement-destinations-meteo-ete-2026.html'
        en_file = 'best-destinations-summer-weather-2026.html'
        canonical = f'https://bestdateweather.com/{fr_file}'
        footer = FOOTER_FR.format(en_file=en_file)
        meth = METH_FR
        outfile = ROOT / fr_file
    else:
        title = 'Best summer destinations 2026 — Weather ranking June–August'
        desc = f'Top {n_dests} destinations for summer 2026. Ranked using 10 years of June–August weather data.'
        h1 = 'Best summer<br/><em>destinations 2026</em>'
        hero_sub = f'{top1["dest"]["nom_en"]} leads with {top1["avg"]:.1f}/10 for June–August.'
        stats = f'<div class="hero-stats"><div class="hstat"><span class="hstat-val">{n_dests}</span><span class="hstat-lbl">Destinations</span></div><div class="hstat"><span class="hstat-val">Jun–Aug</span><span class="hstat-lbl">Period</span></div></div>'
        insights = f'<div class="insights-bar"><div class="insights-inner"><div class="insights-label">Key insights</div><div class="insights-grid"><div class="insight-item"><strong>#1 summer</strong>{top1["dest"]["nom_en"]} — {top1["avg"]:.1f}/10.</div><div class="insight-item"><strong>#2</strong>{summer[1]["dest"]["nom_en"]} — {summer[1]["avg"]:.1f}/10.</div><div class="insight-item"><strong>#3</strong>{summer[2]["dest"]["nom_en"]} — {summer[2]["avg"]:.1f}/10.</div></div></div></div>'
        sections = [
            {'eyebrow':'Summer 2026', 'h2':'☀️ Top 20 worldwide — Summer 2026 (June–Aug)', 'intro':f'Average score over 3 summer months. {n_dests} destinations.', 'table': make_table_seasonal(summer, 20, lang)},
        ]
        jsonld = make_jsonld(summer, 20, 'Best summer destinations 2026', lang)
        related = make_related(lang, 'best-destinations-summer-weather-2026.html')
        fr_file = 'classement-destinations-meteo-ete-2026.html'
        en_file = 'best-destinations-summer-weather-2026.html'
        canonical = f'https://bestdateweather.com/en/{en_file}'
        footer = FOOTER_EN.format(fr_file=fr_file)
        meth = METH_EN
        outfile = ROOT / 'en' / en_file

    page = make_page(
        title=title, description=desc, h1=h1, hero_sub=hero_sub,
        stats_html=stats, insights_html=insights, sections=sections,
        jsonld_str=jsonld, related_html=related, meth_html=meth,
        footer_html=footer, lang=lang, canonical=canonical
    )
    outfile.write_text(page, encoding='utf-8')
    print(f'  ✓ {outfile.name} (été, top={top1["dest"]["nom_bare"]})')


def gen_hiver(dests, climate, lang):
    winter = compute_seasonal(climate, dests, [12,1,2])
    top1 = winter[0]
    n_dests = len(winter)

    if lang == 'fr':
        title = 'Meilleures destinations hiver 2026 — Soleil et chaleur garanti'
        desc = f'Top {n_dests} destinations pour l\'hiver 2026. Classement basé sur 10 ans de données météo déc–fév.'
        h1 = 'Meilleures destinations<br/><em>hiver 2026</em>'
        hero_sub = f'{top1["dest"]["nom_bare"]} en tête avec {top1["avg"]:.1f}/10 sur déc–fév.'
        stats = f'<div class="hero-stats"><div class="hstat"><span class="hstat-val">{n_dests}</span><span class="hstat-lbl">Destinations</span></div><div class="hstat"><span class="hstat-val">Déc–Fév</span><span class="hstat-lbl">Période</span></div></div>'
        insights = f'<div class="insights-bar"><div class="insights-inner"><div class="insights-label">Points clés</div><div class="insights-grid"><div class="insight-item"><strong>N°1 hiver</strong>{top1["dest"]["nom_bare"]} — {top1["avg"]:.1f}/10.</div><div class="insight-item"><strong>N°2</strong>{winter[1]["dest"]["nom_bare"]} — {winter[1]["avg"]:.1f}/10.</div><div class="insight-item"><strong>N°3</strong>{winter[2]["dest"]["nom_bare"]} — {winter[2]["avg"]:.1f}/10.</div></div></div></div>'
        sections = [
            {'eyebrow':'Hiver 2026', 'h2':'❄️ Top 20 mondial — Hiver 2026 (déc–fév)', 'intro':f'Score moyen sur les 3 mois d\'hiver. {n_dests} destinations.', 'table': make_table_seasonal(winter, 20, lang)},
        ]
        jsonld = make_jsonld(winter, 20, 'Meilleures destinations hiver 2026', lang)
        related = make_related(lang, 'classement-destinations-meteo-hiver-2026.html')
        fr_file = 'classement-destinations-meteo-hiver-2026.html'
        en_file = 'best-destinations-winter-weather-2026.html'
        canonical = f'https://bestdateweather.com/{fr_file}'
        footer = FOOTER_FR.format(en_file=en_file)
        meth = METH_FR
        outfile = ROOT / fr_file
    else:
        title = 'Best winter destinations 2026 — Guaranteed sun & warmth'
        desc = f'Top {n_dests} destinations for winter 2026. Ranked using 10 years of Dec–Feb weather data.'
        h1 = 'Best winter<br/><em>destinations 2026</em>'
        hero_sub = f'{top1["dest"]["nom_en"]} leads with {top1["avg"]:.1f}/10 for Dec–Feb.'
        stats = f'<div class="hero-stats"><div class="hstat"><span class="hstat-val">{n_dests}</span><span class="hstat-lbl">Destinations</span></div><div class="hstat"><span class="hstat-val">Dec–Feb</span><span class="hstat-lbl">Period</span></div></div>'
        insights = f'<div class="insights-bar"><div class="insights-inner"><div class="insights-label">Key insights</div><div class="insights-grid"><div class="insight-item"><strong>#1 winter</strong>{top1["dest"]["nom_en"]} — {top1["avg"]:.1f}/10.</div><div class="insight-item"><strong>#2</strong>{winter[1]["dest"]["nom_en"]} — {winter[1]["avg"]:.1f}/10.</div><div class="insight-item"><strong>#3</strong>{winter[2]["dest"]["nom_en"]} — {winter[2]["avg"]:.1f}/10.</div></div></div></div>'
        sections = [
            {'eyebrow':'Winter 2026', 'h2':'❄️ Top 20 worldwide — Winter 2026 (Dec–Feb)', 'intro':f'Average score over 3 winter months. {n_dests} destinations.', 'table': make_table_seasonal(winter, 20, lang)},
        ]
        jsonld = make_jsonld(winter, 20, 'Best winter destinations 2026', lang)
        related = make_related(lang, 'best-destinations-winter-weather-2026.html')
        fr_file = 'classement-destinations-meteo-hiver-2026.html'
        en_file = 'best-destinations-winter-weather-2026.html'
        canonical = f'https://bestdateweather.com/en/{en_file}'
        footer = FOOTER_EN.format(fr_file=fr_file)
        meth = METH_EN
        outfile = ROOT / 'en' / en_file

    page = make_page(
        title=title, description=desc, h1=h1, hero_sub=hero_sub,
        stats_html=stats, insights_html=insights, sections=sections,
        jsonld_str=jsonld, related_html=related, meth_html=meth,
        footer_html=footer, lang=lang, canonical=canonical
    )
    outfile.write_text(page, encoding='utf-8')
    print(f'  ✓ {outfile.name} (hiver, top={top1["dest"]["nom_bare"]})')


def gen_nomades(dests, climate, lang):
    nomad = compute_nomad(climate, dests)
    top1 = nomad[0]
    n_dests = len(nomad)

    if lang == 'fr':
        title = 'Meilleures destinations digital nomads 2026 — Météo et régularité climatique'
        desc = f'{n_dests} destinations classées par constance météo. Idéal pour les nomades digitaux.'
        h1 = 'Meilleures destinations<br/><em>nomades digitaux 2026</em>'
        hero_sub = f'{top1["dest"]["nom_bare"]} en tête : {top1["avg"]:.1f}/10 moyen, écart-type {top1["stdev"]:.2f}.'
        stats = f'<div class="hero-stats"><div class="hstat"><span class="hstat-val">{n_dests}</span><span class="hstat-lbl">Destinations</span></div><div class="hstat"><span class="hstat-val">12 mois</span><span class="hstat-lbl">Constance</span></div></div>'
        insights = f'<div class="insights-bar"><div class="insights-inner"><div class="insights-label">Points clés</div><div class="insights-grid"><div class="insight-item"><strong>N°1 nomade</strong>{top1["dest"]["nom_bare"]} — régularité maximale.</div><div class="insight-item"><strong>N°2</strong>{nomad[1]["dest"]["nom_bare"]} — {nomad[1]["avg"]:.1f}/10.</div><div class="insight-item"><strong>Critère</strong>Score moyen pondéré par la variance.</div></div></div></div>'
        sections = [
            {'eyebrow':'Nomades digitaux', 'h2':'💻 Top 20 — Constance météo toute l\'année', 'intro':f'Score = moyenne annuelle − pénalité variance. Plus le score est haut, plus la météo est régulière et agréable.', 'table': make_table_nomad(nomad, 20, lang)},
        ]
        jsonld = make_jsonld(nomad, 20, 'Meilleures destinations nomades digitaux 2026', lang)
        related = make_related(lang, 'classement-destinations-meteo-nomades-2026.html')
        fr_file = 'classement-destinations-meteo-nomades-2026.html'
        en_file = 'best-destinations-digital-nomads-weather-2026.html'
        canonical = f'https://bestdateweather.com/{fr_file}'
        footer = FOOTER_FR.format(en_file=en_file)
        meth = METH_FR
        outfile = ROOT / fr_file
    else:
        title = 'Best digital nomad destinations 2026 — Weather consistency ranking'
        desc = f'{n_dests} destinations ranked by weather consistency. Ideal for digital nomads.'
        h1 = 'Best digital nomad<br/><em>destinations 2026</em>'
        hero_sub = f'{top1["dest"]["nom_en"]} leads: {top1["avg"]:.1f}/10 average, std dev {top1["stdev"]:.2f}.'
        stats = f'<div class="hero-stats"><div class="hstat"><span class="hstat-val">{n_dests}</span><span class="hstat-lbl">Destinations</span></div><div class="hstat"><span class="hstat-val">12 months</span><span class="hstat-lbl">Consistency</span></div></div>'
        insights = f'<div class="insights-bar"><div class="insights-inner"><div class="insights-label">Key insights</div><div class="insights-grid"><div class="insight-item"><strong>#1 nomad</strong>{top1["dest"]["nom_en"]} — maximum consistency.</div><div class="insight-item"><strong>#2</strong>{nomad[1]["dest"]["nom_en"]} — {nomad[1]["avg"]:.1f}/10.</div><div class="insight-item"><strong>Criteria</strong>Average score weighted by variance.</div></div></div></div>'
        sections = [
            {'eyebrow':'Digital nomads', 'h2':'💻 Top 20 — Year-round weather consistency', 'intro':'Score = annual average − variance penalty. Higher = more consistent and pleasant weather.', 'table': make_table_nomad(nomad, 20, lang)},
        ]
        jsonld = make_jsonld(nomad, 20, 'Best digital nomad destinations 2026', lang)
        related = make_related(lang, 'best-destinations-digital-nomads-weather-2026.html')
        fr_file = 'classement-destinations-meteo-nomades-2026.html'
        en_file = 'best-destinations-digital-nomads-weather-2026.html'
        canonical = f'https://bestdateweather.com/en/{en_file}'
        footer = FOOTER_EN.format(fr_file=fr_file)
        meth = METH_EN
        outfile = ROOT / 'en' / en_file

    page = make_page(
        title=title, description=desc, h1=h1, hero_sub=hero_sub,
        stats_html=stats, insights_html=insights, sections=sections,
        jsonld_str=jsonld, related_html=related, meth_html=meth,
        footer_html=footer, lang=lang, canonical=canonical
    )
    outfile.write_text(page, encoding='utf-8')
    print(f'  ✓ {outfile.name} (nomades, top={top1["dest"]["nom_bare"]})')


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main():
    print('Loading data...')
    dests = load_destinations()
    climate = load_climate()
    print(f'  {len(dests)} destinations, {len(climate)} climate entries')

    print('\nGenerating FR pages...')
    gen_mondial(dests, climate, 'fr')
    gen_europe(dests, climate, 'fr')
    gen_ete(dests, climate, 'fr')
    gen_hiver(dests, climate, 'fr')
    gen_nomades(dests, climate, 'fr')

    print('\nGenerating EN pages...')
    gen_mondial(dests, climate, 'en')
    gen_europe(dests, climate, 'en')
    gen_ete(dests, climate, 'en')
    gen_hiver(dests, climate, 'en')
    gen_nomades(dests, climate, 'en')

    print('\n✅ All 10 ranking pages generated.')

if __name__ == '__main__':
    main()
