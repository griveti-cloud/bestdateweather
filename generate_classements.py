#!/usr/bin/env python3
"""
Generate all 10 ranking pages (5 FR + 5 EN) from climate.csv + destinations.csv.
Usage: python3 generate_classements.py
"""

import csv, html, json, statistics
from pathlib import Path
from lib.common import footer_ranking_html, shared_nav_html

# ── Locale loading ───────────────────────────────────────────────────────────
_locale_cache = {}
def load_locale(lang):
    if lang not in _locale_cache:
        import os
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "locales", f"{lang}.json")
        with open(path, encoding="utf-8") as f:
            _locale_cache[lang] = json.load(f)
    return _locale_cache[lang]


ROOT = Path(__file__).parent

# ── Data Loading ──────────────────────────────────────────────────────────────

def load_destinations():
    dests = {}
    with open(ROOT / 'data/destinations.csv', encoding='utf-8-sig') as f:
        for r in csv.DictReader(f):
            dests[r['slug_fr']] = r
    return dests

def load_country_info():
    with open(ROOT / 'data/country_info.json', encoding='utf-8') as f:
        return json.load(f)

def load_climate():
    """Returns dict: slug -> list of {mois_num, score, classe, tmin, tmax, rain_pct, precip_mm, sun_h, sea_temp, beach_score}"""
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
                'sea_temp': float(r['sea_temp']) if r.get('sea_temp') else None,
                'beach_score': float(r['beach_score']) if r.get('beach_score') else None,
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
    'France': 'Europe du Sud', 'Allemagne': 'Europe Centrale', 'Pays-Bas': 'Europe Centrale',
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
    'Europe du Nord': 'Northern Europe',
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

# Territoires hors Europe géographique (malgré pays européen)
NON_EUROPE_SLUGS = DOM_TOM_SLUGS | {
    'bermudes',                                                          # Royaume-Uni, Atlantique
    'canaries', 'tenerife', 'gran-canaria', 'fuerteventura',            # Espagne, Macaronésie
    'lanzarote', 'la-palma', 'la-gomera', 'el-hierro',                  # Espagne, Macaronésie
    'madere', 'funchal',                                                 # Portugal, Macaronésie
    'azores',                                                            # Portugal, Atlantique
}

# Destinations caribéennes (pays + territoires, toutes nationalités)
CARIBBEAN_SLUGS = {
    'antigua', 'aruba', 'bahamas', 'barbade', 'bermudes', 'bonaire',
    'cayman-islands', 'curacao', 'dominique', 'grenadines', 'guadeloupe',
    'jamaique', 'la-havane', 'martinique', 'nassau', 'porto-rico',
    'punta-cana', 'republique-dominicaine', 'saint-barthelemy', 'saint-lucie',
    'saint-martin', 'saint-thomas', 'saint-vincent', 'san-juan',
    'trinidad-cuba', 'trinite-et-tobago', 'turks-et-caicos', 'cuba',
}

# Override region tag par slug (priorité sur REGION_TAG par pays)
SLUG_REGION_TAG = {
    'reunion': 'Océan Indien',
    'mayotte': 'Océan Indien',
    'guadeloupe': 'Caraïbes',
    'martinique': 'Caraïbes',
    'saint-martin': 'Caraïbes',
    'saint-barthelemy': 'Caraïbes',
    'polynesie': 'Océanie',
    'bora-bora': 'Océanie',
    'nouvelle-caledonie': 'Océanie',
    'guyane': 'Amérique du Sud',
    'saint-pierre-et-miquelon': 'Amérique du Nord',
}

# MOIS_* removed — loaded from locales at runtime via get_mois(lang)
def get_mois(lang):
    months = load_locale('en' if lang == 'en-us' else lang)['months']  # list index 0=Jan
    return {i+1: m for i, m in enumerate(months)}

def _ft(c, lang):
    """Format temperature: °C for all langs except en-us → °F."""
    if lang == 'en-us':
        return f'{round(c * 9/5 + 32)}°F'
    return f'{round(c)}°C'


# ── Country-level deduplication ───────────────────────────────────────────────
# Slugs that represent an entire country (not a city/region/island).
# When a country-slug and a city from the same country both rank,
# keep only the city (more specific / actionable for travelers).
COUNTRY_SLUGS = {
    'albanie', 'bahamas', 'bolivie', 'cambodge', 'cap-vert', 'chili', 'chypre',
    'colombie', 'costa-rica', 'equateur', 'georgie', 'guatemala', 'iles-cook',
    'jordanie', 'kenya', 'laos', 'madagascar', 'malte', 'montenegro', 'myanmar',
    'namibie', 'nepal', 'nicaragua', 'nouvelle-zelande', 'oman', 'ouzbekistan',
    'perou', 'philippines', 'porto-rico', 'republique-dominicaine', 'senegal', 'sri-lanka',
    'tanzanie', 'uruguay',
}

# Region/archipelago slugs mapped to their child slugs.
# Remove the parent when any child is also ranked.
REGION_CHILDREN = {
    'canaries': {'lanzarote', 'fuerteventura', 'gran-canaria', 'tenerife',
                 'la-palma', 'la-gomera', 'el-hierro'},
    'porto-rico': {'san-juan'},
}

def dedup_country(results, dests):
    """Remove country-level and region-level entries when a more specific sibling is also ranked."""
    # Collect which countries have city-level entries in results
    countries_with_cities = set()
    for r in results:
        if r['slug'] not in COUNTRY_SLUGS:
            countries_with_cities.add(r['dest']['pays'])
    # Collect which region parents should be removed
    ranked_slugs = {r['slug'] for r in results}
    regions_to_remove = set()
    for parent, children in REGION_CHILDREN.items():
        if parent in ranked_slugs and ranked_slugs & children:
            regions_to_remove.add(parent)
    # Filter
    return [r for r in results
            if (r['slug'] not in COUNTRY_SLUGS or r['dest']['pays'] not in countries_with_cities)
            and r['slug'] not in regions_to_remove]

# ── Ranking Computations ─────────────────────────────────────────────────────

def compute_annual(climate, dests, europe_only=False, caribbean_only=False):
    """Annual average score ranking."""
    results = []
    for slug, monthly in climate.items():
        if slug not in dests:
            continue
        d = dests[slug]
        if d.get('precision') == 'country':
            continue
        if europe_only and (d['pays'] not in EUROPE_COUNTRIES or slug in NON_EUROPE_SLUGS):
            continue
        if caribbean_only and slug not in CARIBBEAN_SLUGS:
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

def compute_seasonal(climate, dests, months, europe_only=False, caribbean_only=False):
    """Seasonal average score ranking for given months."""
    results = []
    for slug, monthly in climate.items():
        if slug not in dests:
            continue
        d = dests[slug]
        if d.get('precision') == 'country':
            continue
        if europe_only and (d['pays'] not in EUROPE_COUNTRIES or slug in NON_EUROPE_SLUGS):
            continue
        if caribbean_only and slug not in CARIBBEAN_SLUGS:
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
        if d.get('precision') == 'country':
            continue
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

def compute_beach(climate, dests):
    """Beach ranking: annual average beach_score for coastal destinations."""
    MOIS_FR_SHORT = {1:'Jan',2:'Fév',3:'Mar',4:'Avr',5:'Mai',6:'Jun',
                     7:'Jul',8:'Aoû',9:'Sep',10:'Oct',11:'Nov',12:'Déc'}
    results = []
    for slug, monthly in climate.items():
        if slug not in dests:
            continue
        d = dests[slug]
        if d.get('precision') == 'country':
            continue
        # Only coastal destinations (have beach_score)
        if not all(m in monthly for m in range(1,13)):
            continue
        if monthly[1].get('beach_score') is None:
            continue
        scores = [monthly[m]['beach_score'] for m in range(1,13)]
        sea_temps = [monthly[m].get('sea_temp', 0) or 0 for m in range(1,13)]
        avg = sum(scores) / 12
        best_month = max(range(1,13), key=lambda m: monthly[m]['beach_score'])
        best_score = monthly[best_month]['beach_score']
        best_sea = monthly[best_month].get('sea_temp', 0) or 0
        avg_sea = sum(sea_temps) / 12
        # Months with beach_score >= 7.0
        good_months = sum(1 for s in scores if s >= 7.0)
        results.append({
            'slug': slug, 'dest': d, 'avg': avg,
            'best_month': best_month, 'best_score': best_score,
            'best_sea': best_sea, 'avg_sea': avg_sea,
            'good_months': good_months, 'monthly': monthly,
        })
    results.sort(key=lambda x: (-x['avg'], -x['good_months']))
    return results

def compute_beach_seasonal(climate, dests, months):
    """Beach ranking for specific months."""
    results = []
    for slug, monthly in climate.items():
        if slug not in dests:
            continue
        d = dests[slug]
        if d.get('precision') == 'country':
            continue
        if not all(m in monthly for m in months):
            continue
        if monthly[months[0]].get('beach_score') is None:
            continue
        avg = sum(monthly[m]['beach_score'] for m in months) / len(months)
        avg_sea = sum((monthly[m].get('sea_temp') or 0) for m in months) / len(months)
        avg_tmax = sum(monthly[m]['tmax'] for m in months) / len(months)
        avg_rain = sum(monthly[m]['rain_pct'] for m in months) / len(months)
        avg_sun = sum(monthly[m]['sun_h'] for m in months) / len(months)
        results.append({
            'slug': slug, 'dest': d, 'avg': avg,
            'avg_sea': avg_sea, 'tmax_avg': avg_tmax,
            'rain_avg': avg_rain, 'sun_avg': avg_sun,
            'monthly': monthly,
        })
    results.sort(key=lambda x: -x['avg'])
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
nav{background:white;border-bottom:1px solid var(--cream2);padding:14px 24px;display:flex;align-items:center;justify-content:space-between;position:sticky;top:0;z-index:100;box-shadow:0 2px 12px rgba(26,31,46,.06)}
.nav-brand{font-family:'Playfair Display',Georgia,serif;font-size:17px;font-weight:700;color:var(--navy);text-decoration:none}
.nav-brand em{font-style:italic;color:#9c5f00}
.nav-cta{background:var(--gold);color:var(--navy);border:none;border-radius:8px;padding:8px 16px;font-family:'DM Sans',sans-serif;font-size:12px;font-weight:700;text-decoration:none;transition:all .2s;display:inline-block}
.nav-cta:hover{opacity:.85;transform:translateY(-1px)}
.nav-actions{display:flex;align-items:center;gap:10px}
.nav-share{background:none;border:1.5px solid #e8e0d0;border-radius:8px;padding:7px 9px;cursor:pointer;display:none;align-items:center;color:#5a6c7d}
.nav-share:hover{border-color:var(--gold);color:var(--gold)}
@media(pointer:coarse),(max-width:768px){.nav-share{display:flex}}
.hero{background:var(--navy);color:white;padding:48px 20px 36px;text-align:center}
.hero-eyebrow{font-size:11px;text-transform:uppercase;letter-spacing:2.5px;color:#9c5f00;margin-bottom:12px;font-weight:700}
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
.eyebrow{font-size:10px;text-transform:uppercase;letter-spacing:2px;color:#9c5f00;font-weight:700;margin-bottom:6px}
.sec-title{font-family:'Playfair Display',Georgia,serif;font-size:clamp(18px,4vw,24px);margin-bottom:8px}
.sec-intro{font-size:14px;color:var(--slate);margin-bottom:18px}
.rt{width:100%;border-collapse:collapse;font-size:13px}
.rt th{background:var(--navy);color:white;padding:10px 12px;text-align:left;font-size:11px;text-transform:uppercase;letter-spacing:.5px;font-weight:700;position:sticky;top:0}
.rt td{padding:10px 12px;border-bottom:1px solid var(--cream2);vertical-align:middle}
.rt tr:hover{background:#fef9f0}
.rt .rank{font-weight:700;font-size:15px;text-align:center;width:48px}
.rt .sc{font-weight:700;color:var(--navy);font-size:14px;white-space:nowrap}
.rt .sc span{font-weight:400;color:var(--slate);font-size:11px}
.dest-link{color:var(--text);text-decoration:none;font-weight:600}
.dest-link:hover{color:var(--gold)}
.region-tag{display:inline-block;font-size:10px;color:var(--slate);background:var(--cream);padding:2px 8px;border-radius:10px;margin-left:8px;vertical-align:middle}
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
footer{background:var(--navy);color:#b8bcc8;text-align:center;padding:36px 20px;font-size:12px;line-height:2}
footer a{color:#f5d060;text-decoration:none}
@media(max-width:640px){.rt th:nth-child(5),.rt td:nth-child(5),.rt th:nth-child(6),.rt td:nth-child(6){display:none}.hero-stats{gap:20px}}
"""

def e(s):
    """HTML-escape."""
    return html.escape(str(s))

def rank_icon(i):
    if i == 1: return '🥇'
    if i == 2: return '🥈'
    if i == 3: return '🥉'
    return str(i)

def dest_link(slug, nom, lang, dest=None):
    if lang == 'fr':
        return f'meilleure-periode-{slug}.html'
    elif lang == 'es':
        slug_es = dest.get('slug_es', slug) if dest else slug
        return f'../es/mejor-epoca-{slug_es}.html'
    elif lang == 'de':
        slug_de = dest.get('slug_de', dest.get('slug_en', slug)) if dest else slug
        return f'beste-reisezeit-{slug_de}.html'
    else:  # en, en-us
        slug_en = dest.get('slug_en', slug) if dest else slug
        return f'best-time-to-visit-{slug_en}.html'

def country_tag(d, lang, slug=''):
    """Show country name (or DOM-TOM territory) next to destination."""
    # DOM-TOM: show territory name instead of "France"
    SLUG_TERRITORY = {
        'reunion': 'La Réunion', 'mayotte': 'Mayotte',
        'guadeloupe': 'Guadeloupe', 'martinique': 'Martinique',
        'saint-martin': 'Saint-Martin', 'saint-barthelemy': 'Saint-Barthélemy',
        'polynesie': 'Polynésie', 'bora-bora': 'Polynésie',
        'tahiti': 'Polynésie', 'moorea': 'Polynésie',
        'nouvelle-caledonie': 'Nouvelle-Calédonie',
        'guyane': 'Guyane', 'saint-pierre-et-miquelon': 'Saint-Pierre-et-Miquelon',
    }
    SLUG_TERRITORY_EN = {
        'reunion': 'Réunion', 'mayotte': 'Mayotte',
        'guadeloupe': 'Guadeloupe', 'martinique': 'Martinique',
        'saint-martin': 'Saint Martin', 'saint-barthelemy': 'Saint Barthélemy',
        'polynesie': 'French Polynesia', 'bora-bora': 'French Polynesia',
        'tahiti': 'French Polynesia', 'moorea': 'French Polynesia',
        'nouvelle-caledonie': 'New Caledonia',
        'guyane': 'French Guiana', 'saint-pierre-et-miquelon': 'Saint Pierre & Miquelon',
    }
    if slug in SLUG_TERRITORY:
        tag = SLUG_TERRITORY_EN[slug] if lang in ('en', 'es') else SLUG_TERRITORY[slug]
    elif lang in ('en', 'en-us'):
        tag = d.get('country_en', '') or d.get('pays', '')
    elif lang == 'es':
        tag = d.get('country_es', '') or d.get('country_en', '') or d.get('pays', '')
    elif lang == 'de':
        tag = d.get('country_de', '') or d.get('country_en', '') or d.get('pays', '')
    else:
        tag = d.get('pays', '')
    if not tag:
        return ''
    return f'<span class="region-tag">{e(tag)}</span>'

def safety_badge(dest, country_info):
    """Return a safety badge based on risk_level from country_info."""
    pays = dest.get('pays', '')
    info = country_info.get(pays, {})
    level = info.get('risk_level', 1)
    if level == 1:
        return '<span class="safety-1" title="Sûr">🟢</span>'
    elif level == 2:
        return '<span class="safety-2" title="Vigilance normale">🟡</span>'
    elif level == 3:
        return '<span class="safety-3" title="Vigilance renforcée">🟠</span>'
    else:
        return '<span class="safety-4" title="Déconseillé">🔴</span>'

def make_table_annual(entries, n, lang, country_info=None):
    """Generate top-N annual ranking table."""
    mois = get_mois(lang)
    headers = {
        'fr': ('Rang','Destination',['Meilleur mois'],'Score annuel',['Soleil/an'],['Pluie moy.'],'Sécu.'),
        'en': ('Rank','Destination',['Best month'],'Annual score',['Sun/year'],['Avg. rain'],'Safety'),
        'es': ('Pos.','Destino',['Mejor mes'],'Puntuación anual',['Sol/año'],['Lluvia media'],'Seg.'),
        'de': ('Rang','Ziel',['Bester Monat'],'Jahreswertung',['Sonne/Jahr'],['Ø Regen'],'Sicher.'),
    }
    h = headers['en' if lang == 'en-us' else lang]
    rows = []
    for i, entry in enumerate(entries[:n], 1):
        d = entry['dest']
        nom = d.get('nom_de', d['nom_en']) if lang == 'de' else (d['nom_en'] if lang in ('en', 'en-us', 'es') else d['nom_fr'])
        link = dest_link(entry['slug'], nom, lang, entry['dest'])
        rows.append(
            f'<tr><td class="rank">{rank_icon(i)}</td>'
            f'<td><a href="{link}" class="dest-link">{e(nom)}</a>{country_tag(d, lang, entry["slug"])}</td>'
            f'<td class="rt-sec">{mois[entry["best_month"]]}</td>'
            f'<td class="sc">{entry["avg"]:.1f}<span>/10</span></td>'
            f'<td class="rt-sec">{entry["sun_annual"]:.0f}h</td>'
            f'<td class="rt-sec">{entry["rain_avg"]:.0f}%</td>'
            f'<td class="safety-col">{safety_badge(d, country_info or {})}</td></tr>'
        )
    return (
        f'<table class="rt"><thead><tr>{"".join(f'<th class="rt-sec">{x[0]}</th>' if isinstance(x,list) else f'<th>{x}</th>' for x in h)}</tr></thead>'
        f'<tbody>{"".join(rows)}</tbody></table>'
    )

def make_table_seasonal(entries, n, lang, country_info=None):
    headers = {
        'fr': ('Rang','Destination','Score',['Temp. max'],['Soleil'],['Pluie'],'Sécu.'),
        'en': ('Rank','Destination','Score',['Max temp.'],['Sun'],['Rain'],'Safety'),
        'es': ('Pos.','Destino','Puntuación',['Temp. máx'],['Sol'],['Lluvia'],'Seg.'),
        'de': ('Rang','Ziel','Wertung',['Max-Temp.'],['Sonne'],['Regen'],'Sicher.'),
    }
    h = headers['en' if lang == 'en-us' else lang]
    rows = []
    for i, entry in enumerate(entries[:n], 1):
        d = entry['dest']
        nom = d.get('nom_de', d['nom_en']) if lang == 'de' else (d['nom_en'] if lang in ('en', 'en-us', 'es') else d['nom_fr'])
        link = dest_link(entry['slug'], nom, lang, entry['dest'])
        rows.append(
            f'<tr><td class="rank">{rank_icon(i)}</td>'
            f'<td><a href="{link}" class="dest-link">{e(nom)}</a>{country_tag(d, lang, entry["slug"])}</td>'
            f'<td class="sc">{entry["avg"]:.1f}<span>/10</span></td>'
            f'<td class="rt-sec">{_ft(entry["tmax_avg"], lang)}</td>'
            f'<td class="rt-sec">{entry["sun"]:.0f}h</td>'
            f'<td class="rt-sec">{entry["rain_avg"]:.0f}%</td>'
            f'<td class="safety-col">{safety_badge(d, country_info or {})}</td></tr>'
        )
    return (
        f'<table class="rt"><thead><tr>{"".join(f'<th class="rt-sec">{x[0]}</th>' if isinstance(x,list) else f'<th>{x}</th>' for x in h)}</tr></thead>'
        f'<tbody>{"".join(rows)}</tbody></table>'
    )

def make_table_sun(entries, n, lang, country_info=None):
    headers = {
        'fr': ('Rang','Destination','Soleil/an',['Pluie moy.'],'Score'),
        'en': ('Rank','Destination','Sun/year',['Avg. rain'],'Score'),
        'es': ('Pos.','Destino','Sol/año',['Lluvia media'],'Punt.'),
        'de': ('Rang','Ziel','Sonne/Jahr',['Ø Regen'],'Score'),
    }
    h = headers['en' if lang == 'en-us' else lang]
    rows = []
    for i, entry in enumerate(entries[:n], 1):
        d = entry['dest']
        nom = d.get('nom_de', d['nom_en']) if lang == 'de' else (d['nom_en'] if lang in ('en', 'en-us', 'es') else d['nom_fr'])
        link = dest_link(entry['slug'], nom, lang, entry['dest'])
        rows.append(
            f'<tr><td class="rank">{rank_icon(i)}</td>'
            f'<td><a href="{link}" class="dest-link">{e(nom)}</a>{country_tag(d, lang, entry["slug"])}<span class="dest-safety">{safety_badge(d, country_info or {})}</span></td>'
            f'<td>{entry["sun_annual"]:.0f}h</td>'
            f'<td class="rt-sec">{entry["rain_avg"]:.0f}%</td>'
            f'<td class="sc">{entry["avg"]:.1f}<span>/10</span></td></tr>'
        )
    return (
        f'<table class="rt rt-compact"><thead><tr>{"".join(f'<th class="rt-sec">{x[0]}</th>' if isinstance(x,list) else f'<th>{x}</th>' for x in h)}</tr></thead>'
        f'<tbody>{"".join(rows)}</tbody></table>'
    )

def make_table_rain(entries, n, lang, country_info=None):
    headers = {
        'fr': ('Rang','Destination','Pluie moy.',['Soleil/an'],'Score'),
        'en': ('Rank','Destination','Avg. rain',['Sun/year'],'Score'),
        'es': ('Pos.','Destino','Lluvia media',['Sol/año'],'Punt.'),
        'de': ('Rang','Ziel','Ø Regen',['Sonne/Jahr'],'Score'),
    }
    h = headers['en' if lang == 'en-us' else lang]
    rows = []
    for i, entry in enumerate(entries[:n], 1):
        d = entry['dest']
        nom = d.get('nom_de', d['nom_en']) if lang == 'de' else (d['nom_en'] if lang in ('en', 'en-us', 'es') else d['nom_fr'])
        link = dest_link(entry['slug'], nom, lang, entry['dest'])
        rows.append(
            f'<tr><td class="rank">{rank_icon(i)}</td>'
            f'<td><a href="{link}" class="dest-link">{e(nom)}</a>{country_tag(d, lang, entry["slug"])}<span class="dest-safety">{safety_badge(d, country_info or {})}</span></td>'
            f'<td>{entry["rain_avg"]:.0f}%</td>'
            f'<td class="rt-sec">{entry["sun_annual"]:.0f}h</td>'
            f'<td class="sc">{entry["avg"]:.1f}<span>/10</span></td></tr>'
        )
    return (
        f'<table class="rt rt-compact"><thead><tr>{"".join(f'<th class="rt-sec">{x[0]}</th>' if isinstance(x,list) else f'<th>{x}</th>' for x in h)}</tr></thead>'
        f'<tbody>{"".join(rows)}</tbody></table>'
    )

def make_table_nomad(entries, n, lang):
    headers = {
        'fr': ('Rang','Destination','Score moyen','Écart-type','Pire mois','Score pire'),
        'en': ('Rank','Destination','Avg. score','Std. dev.','Worst month','Worst score'),
        'es': ('Pos.','Destino','Punt. media','Desv. típica','Peor mes','Punt. peor mes'),
        'de': ('Rang','Ziel','Ø Wertung','Std.-Abw.','Schlechtester Monat','Schlechteste Note'),
    }
    mois = get_mois(lang)
    h = headers['en' if lang == 'en-us' else lang]
    rows = []
    for i, entry in enumerate(entries[:n], 1):
        d = entry['dest']
        nom = d.get('nom_de', d['nom_en']) if lang == 'de' else (d['nom_en'] if lang in ('en', 'en-us', 'es') else d['nom_fr'])
        link = dest_link(entry['slug'], nom, lang, entry['dest'])
        rows.append(
            f'<tr><td class="rank">{rank_icon(i)}</td>'
            f'<td><a href="{link}" class="dest-link">{e(nom)}</a>{country_tag(d, lang, entry["slug"])}</td>'
            f'<td class="sc">{entry["avg"]:.1f}<span>/10</span></td>'
            f'<td>{entry["stdev"]:.2f}</td>'
            f'<td>{mois[entry["worst_month"]]}</td>'
            f'<td>{entry["worst_score"]:.1f}</td></tr>'
        )
    return (
        f'<table class="rt"><thead><tr>{"".join(f'<th class="rt-sec">{x[0]}</th>' if isinstance(x,list) else f'<th>{x}</th>' for x in h)}</tr></thead>'
        f'<tbody>{"".join(rows)}</tbody></table>'
    )

def make_table_beach(entries, n, lang):
    headers = {
        'fr': ('Rang','Destination','Score plage','Mer','Temp.','Soleil/j','Pluie'),
        'en': ('Rank','Destination','Beach score','Sea','Temp.','Sun/day','Rain'),
        'es': ('Pos.','Destino','Score playa','Mar','Temp.','Sol/día','Lluvia'),
        'de': ('Rang','Ziel','Strand-Score','Meer','Temp.','Sonne/Tag','Regen'),
    }
    h = headers['en' if lang == 'en-us' else lang]
    rows = []
    for i, entry in enumerate(entries[:n], 1):
        d = entry['dest']
        nom = d.get('nom_de', d['nom_en']) if lang == 'de' else (d['nom_en'] if lang in ('en', 'en-us', 'es') else d['nom_fr'])
        link = dest_link(entry['slug'], nom, lang, entry['dest'])
        rows.append(
            f'<tr><td class="rank">{rank_icon(i)}</td>'
            f'<td><a href="{link}" class="dest-link">{e(nom)}</a>{country_tag(d, lang, entry["slug"])}</td>'
            f'<td class="sc">{entry["avg"]:.1f}<span>/10</span></td>'
            f'<td>{_ft(entry["avg_sea"], lang)}</td>'
            f'<td>{_ft(entry["tmax_avg"], lang)}</td>'
            f'<td>{entry["sun_avg"]:.1f}h</td>'
            f'<td>{entry["rain_avg"]:.0f}%</td></tr>'
        )
    return (
        f'<table class="rt"><thead><tr>{"".join(f'<th class="rt-sec">{x[0]}</th>' if isinstance(x,list) else f'<th>{x}</th>' for x in h)}</tr></thead>'
        f'<tbody>{"".join(rows)}</tbody></table>'
    )

def make_table_beach_annual(entries, n, lang):
    mois = get_mois(lang)
    headers = {
        'fr': ('Rang','Destination','Score plage','Mer moy.','Meilleur mois','Mois ≥7/10'),
        'en': ('Rank','Destination','Beach score','Avg. sea','Best month','Months ≥7/10'),
        'es': ('Pos.','Destino','Score playa','Mar medio','Mejor mes','Meses ≥7/10'),
        'de': ('Rang','Ziel','Strand-Score','Ø Meer','Bester Monat','Monate ≥7/10'),
    }
    h = headers['en' if lang == 'en-us' else lang]
    rows = []
    for i, entry in enumerate(entries[:n], 1):
        d = entry['dest']
        nom = d.get('nom_de', d['nom_en']) if lang == 'de' else (d['nom_en'] if lang in ('en', 'en-us', 'es') else d['nom_fr'])
        link = dest_link(entry['slug'], nom, lang, entry['dest'])
        rows.append(
            f'<tr><td class="rank">{rank_icon(i)}</td>'
            f'<td><a href="{link}" class="dest-link">{e(nom)}</a>{country_tag(d, lang, entry["slug"])}</td>'
            f'<td class="sc">{entry["avg"]:.1f}<span>/10</span></td>'
            f'<td>{_ft(entry["avg_sea"], lang)}</td>'
            f'<td>{mois[entry["best_month"]]} ({entry["best_score"]:.1f})</td>'
            f'<td>{entry["good_months"]}</td></tr>'
        )
    return (
        f'<table class="rt"><thead><tr>{"".join(f'<th class="rt-sec">{x[0]}</th>' if isinstance(x,list) else f'<th>{x}</th>' for x in h)}</tr></thead>'
        f'<tbody>{"".join(rows)}</tbody></table>'
    )

# ── JSON-LD ───────────────────────────────────────────────────────────────────

def make_jsonld(entries, n, title, lang):
    items = []
    for i, entry in enumerate(entries[:n], 1):
        d = entry['dest']
        if lang == 'de':
            nom = d.get('nom_de', d['nom_en'])
        elif lang in ('en', 'en-us', 'es'):
            nom = d['nom_en']
        else:
            nom = d['nom_fr']
        slug = entry['slug']
        if lang == 'fr':
            url = f'https://bestdateweather.com/meilleure-periode-{slug}.html'
        elif lang == 'es':
            slug_es = d.get('slug_es', slug)
            url = f'https://bestdateweather.com/es/mejor-epoca-{slug_es}.html'
        elif lang == 'de':
            slug_de = d.get('slug_de', d.get('slug_en', slug))
            url = f'https://bestdateweather.com/de/beste-reisezeit-{slug_de}.html'
        else:
            slug_en = d.get('slug_en', slug)
            url = f'https://bestdateweather.com/best-time-to-visit-{slug_en}.html'
        items.append({"@type":"ListItem","position":i,"name":nom,"url":url})
    return json.dumps({
        "@context":"https://schema.org","@type":"ItemList",
        "name":title,"numberOfItems":n,"itemListElement":items
    }, ensure_ascii=False)

# ── Related Pages ─────────────────────────────────────────────────────────────

# RELATED_* removed — loaded from locales[classements][related]
def make_related(lang, exclude_href=''):
    related = load_locale('en' if lang == 'en-us' else lang)['classements']['related']
    cards = ''
    for href, title, sub in related:
        if href == exclude_href:
            continue
        cards += f'<a href="{href}" class="related-card"><strong>{title}</strong><span>{sub}</span></a>\n'
    return f'<div class="related-pages">\n{cards}</div>'

# ── Methodology ───────────────────────────────────────────────────────────────

# METH_* removed — loaded from locales[classements][methodology]

# ── Footer ────────────────────────────────────────────────────────────────────

# FOOTER_FR removed — use footer_ranking_html(lang, alt_links)

# FOOTER_EN removed — use footer_ranking_html(lang, alt_links)

# FOOTER_ES removed — use footer_ranking_html(lang, alt_links)

# ── Page Assembly ─────────────────────────────────────────────────────────────

def make_page(*, title, description, h1, hero_sub, stats_html, insights_html,
              sections, jsonld_str, related_html, meth_html, footer_html, lang, canonical,
              hreflang_fr='', hreflang_en='', hreflang_es='', hreflang_de='', hreflang_us='',
              asset_prefix=''):
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
            f'<div class="rt-wrap">{sec["table"]}</div>'
            f'</div>'
        )

    return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="UTF-8"/><meta name="viewport" content="width=device-width,initial-scale=1.0"/>
<title>{e(title)}</title>
<meta name="description" content="{e(description)}"/>
<link rel="canonical" href="{canonical}"/>
{f'<link rel="alternate" hreflang="fr" href="{hreflang_fr}"/>' if hreflang_fr else ''}
{f'<link rel="alternate" hreflang="en" href="{hreflang_en}"/>' if hreflang_en else ''}
{f'<link rel="alternate" hreflang="es" href="{hreflang_es}"/>' if hreflang_es else ''}
{f'<link rel="alternate" hreflang="de" href="{hreflang_de}"/>' if hreflang_de else ''}
{f'<link rel="alternate" hreflang="en-us" href="{hreflang_us}"/>' if hreflang_us else ''}
{f'<link rel="alternate" hreflang="x-default" href="{hreflang_en}"/>' if hreflang_en else ''}
<style>{CSS}</style>
{fonts}
<link rel="stylesheet" href="{asset_prefix}style.css"/>
<script type="application/ld+json">{jsonld_str}</script>
<meta property="og:title" content="{e(title)}"/>
<meta property="og:description" content="{e(description)}"/>
<meta property="og:image" content="https://bestdateweather.com/og-image.png"/>
<meta property="og:image:width" content="1200"/>
<meta property="og:image:height" content="630"/>
<meta name="twitter:card" content="summary_large_image"/>
</head>
<body>
{shared_nav_html(load_locale(lang)['nav']['cta_href'], load_locale(lang)['classements']['nav_cta_label'], load_locale(lang)['classements']['share_label'])}
<header class="hero">
<div class="hero-eyebrow">{load_locale(lang)['classements']['hero_eyebrow']}</div>
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
<script src="{load_locale(lang)['classements']['share_js']}"></script>
</body></html>"""



# ── Classement page helpers ────────────────────────────────────────────────────

def _dest_name(dest, lang):
    """Return display name for a destination in the given language."""
    if lang == 'fr':
        return dest.get('nom_bare', dest.get('nom_fr', ''))
    elif lang == 'es':
        return dest.get('nom_es') or dest.get('nom_en', '')
    elif lang == 'de':
        return dest.get('nom_de') or dest.get('nom_en', '')
    return dest.get('nom_en', '')


def _tpl(s, ctx):
    try:
        return s.format(**ctx)
    except (KeyError, ValueError):
        return s


def _stats_html(stats, ctx):
    divs = ''.join(
        f'<div class="hstat"><span class="hstat-val">{_tpl(v, ctx)}</span>'
        f'<span class="hstat-lbl">{lbl}</span></div>'
        for v, lbl in stats
    )
    return f'<div class="hero-stats">{divs}</div>'


def _insights_html(label, items, ctx):
    grid = ''.join(
        f'<div class="insight-item"><strong>{strong}</strong>{_tpl(tpl, ctx)}</div>'
        for strong, tpl in items
    )
    return (f'<div class="insights-bar"><div class="insights-inner">'
            f'<div class="insights-label">{label}</div>'
            f'<div class="insights-grid">{grid}</div></div></div>')


def _sections(sections_cfg, ctx, tables):
    return [
        {'eyebrow': s['eyebrow'], 'h2': s['h2'],
         'intro': _tpl(s.get('intro_tpl', s.get('intro', '')), ctx),
         'table': tables[i]}
        for i, s in enumerate(sections_cfg)
    ]


def _cl_layout(pc, lang):
    BASE = 'https://bestdateweather.com'
    fr_file, en_file, es_file = pc['fr_file'], pc['en_file'], pc['es_file']
    # de_file is always stored in the DE locale — load it from there
    _page_key = next((k for k, v in load_locale('de').get('classement_pages', {}).items()
                      if v.get('en_file') == en_file), None)
    de_file = load_locale('de')['classement_pages'][_page_key]['de_file'] if _page_key else pc.get('de_file', en_file)
    if lang == 'fr':
        canonical = f'{BASE}/{fr_file}'
        footer = footer_ranking_html('fr', [
            {'url': f'en/{en_file}',  'flag': 'flags/gb.png',    'label': 'English'},
            {'url': f'us/{en_file}',  'flag': 'flags/us.png',    'label': 'English (US)'},
            {'url': f'es/{es_file}',  'flag': 'flags/es.png',    'label': 'Español'},
            {'url': f'de/{de_file}',  'flag': 'flags/de.png',    'label': 'Deutsch'},
        ])
        outfile = ROOT / fr_file
    elif lang == 'en-us':
        canonical = f'{BASE}/us/{en_file}'
        footer = footer_ranking_html('en', [
            {'url': f'../{fr_file}',    'flag': '../flags/fr.png', 'label': 'Français'},
            {'url': f'../en/{en_file}', 'flag': '../flags/gb.png', 'label': 'English'},
            {'url': f'../es/{es_file}', 'flag': '../flags/es.png', 'label': 'Español'},
            {'url': f'../de/{de_file}', 'flag': '../flags/de.png', 'label': 'Deutsch'},
        ])
        outfile = ROOT / 'us' / en_file
    elif lang == 'en':
        canonical = f'{BASE}/en/{en_file}'
        footer = footer_ranking_html('en', [
            {'url': f'../{fr_file}',    'flag': '../flags/fr.png', 'label': 'Français'},
            {'url': f'../us/{en_file}', 'flag': '../flags/us.png', 'label': 'English (US)'},
            {'url': f'../es/{es_file}', 'flag': '../flags/es.png', 'label': 'Español'},
            {'url': f'../de/{de_file}', 'flag': '../flags/de.png', 'label': 'Deutsch'},
        ])
        outfile = ROOT / 'en' / en_file
    elif lang == 'de':
        canonical = f'{BASE}/de/{de_file}'
        footer = footer_ranking_html('de', [
            {'url': f'../{fr_file}',    'flag': '../flags/fr.png', 'label': 'Français'},
            {'url': f'../en/{en_file}', 'flag': '../flags/gb.png', 'label': 'English'},
            {'url': f'../es/{es_file}', 'flag': '../flags/es.png', 'label': 'Español'},
            {'url': f'../us/{en_file}', 'flag': '../flags/us.png', 'label': 'US English'},
        ])
        outfile = ROOT / 'de' / de_file
    else:  # es
        canonical = f'{BASE}/es/{es_file}'
        footer = footer_ranking_html('es', [
            {'url': f'../{fr_file}',    'flag': '../flags/fr.png', 'label': 'Français'},
            {'url': f'../en/{en_file}', 'flag': '../flags/gb.png', 'label': 'English'},
            {'url': f'../de/{de_file}', 'flag': '../flags/de.png', 'label': 'Deutsch'},
            {'url': f'../us/{en_file}', 'flag': '../flags/us.png', 'label': 'US English'},
        ])
        outfile = ROOT / 'es' / es_file
    return canonical, footer, outfile, fr_file, en_file, es_file, de_file


def _cl_render(pc, lang, ctx, tables, jsonld_data, jsonld_n, print_suffix=''):
    title    = _tpl(pc['title_tpl'],    ctx)
    desc     = _tpl(pc['desc_tpl'],     ctx)
    h1       = pc['h1']
    hero_sub = _tpl(pc['hero_sub_tpl'], ctx)
    stats    = _stats_html(pc['stats'], ctx)
    insights = _insights_html(pc['insights_label'], pc['insights'], ctx)
    sections = _sections(pc['sections'], ctx, tables)
    jsonld   = make_jsonld(jsonld_data, jsonld_n, _tpl(pc['jsonld_title_tpl'], ctx), lang)
    _meth_tpl = pc.get('meth') or load_locale('en' if lang == 'en-us' else lang)['classements']['methodology']
    meth      = _meth_tpl.format(**ctx) if '{n}' in _meth_tpl else _meth_tpl
    canonical, footer, outfile, fr_file, en_file, es_file, de_file = _cl_layout(pc, lang)
    rel_file = es_file if lang == 'es' else (de_file if lang == 'de' else (fr_file if lang == 'fr' else en_file))
    related  = make_related(lang, rel_file)
    pfx = '' if lang == 'fr' else '../'
    page = make_page(
        title=title, description=desc, h1=h1, hero_sub=hero_sub,
        stats_html=stats, insights_html=insights, sections=sections,
        jsonld_str=jsonld, related_html=related, meth_html=meth,
        footer_html=footer, lang=lang, canonical=canonical,
        hreflang_fr=f'https://bestdateweather.com/{fr_file}',
        hreflang_en=f'https://bestdateweather.com/en/{en_file}',
        hreflang_es=f'https://bestdateweather.com/es/{es_file}',
        hreflang_de=f'https://bestdateweather.com/de/{de_file}',
        hreflang_us=f'https://bestdateweather.com/us/{en_file}',
        asset_prefix=pfx,
    )
    outfile.write_text(page, encoding='utf-8')
    print(f'  ✓ {outfile.name}{print_suffix}')

# ══════════════════════════════════════════════════════════════════════════════
# PAGE GENERATORS
# ══════════════════════════════════════════════════════════════════════════════

def gen_mondial(dests, climate, lang, country_info=None):
    annual   = dedup_country(compute_annual(climate, dests), dests)
    sunniest = dedup_country(compute_sunniest(climate, dests), dests)
    driest   = dedup_country(compute_driest(climate, dests), dests)
    europe_annual = dedup_country(compute_annual(climate, dests, europe_only=True), dests)
    top1 = annual[0]; sun1 = sunniest[0]; dry1 = driest[0]; eu1 = europe_annual[0]
    n_dests = len(annual)
    pc  = load_locale(lang)['classement_pages']['mondial']
    ctx = dict(
        n=n_dests, days=n_dests * 10 * 365 // 1000,
        top1=_dest_name(top1['dest'], lang),  top1_avg=f'{top1["avg"]:.1f}',
        sun1=_dest_name(sun1['dest'], lang),  sun1_h=int(sun1['sun_annual']),
        dry1=_dest_name(dry1['dest'], lang),  dry1_r=int(dry1['rain_avg']),
        eu1=_dest_name(eu1['dest'], lang),    eu1_avg=f'{eu1["avg"]:.1f}',
    )
    _cl_render(pc, lang, ctx,
               tables=[make_table_annual(annual, 20, lang, country_info),
                       make_table_sun(sunniest, 10, lang, country_info),
                       make_table_rain(driest, 10, lang, country_info)],
               jsonld_data=annual, jsonld_n=40,
               print_suffix=f' ({n_dests} dests, top={top1["dest"]["nom_bare"]})')

def gen_europe(dests, climate, lang, country_info=None):
    annual  = dedup_country(compute_annual(climate, dests, europe_only=True), dests)
    summer  = dedup_country(compute_seasonal(climate, dests, [6,7,8], europe_only=True), dests)
    winter  = dedup_country(compute_seasonal(climate, dests, [12,1,2], europe_only=True), dests)
    top1    = annual[0]
    n_dests = len(annual)
    pc  = load_locale(lang)['classement_pages']['europe']
    ctx = dict(
        n=n_dests,
        top1=_dest_name(top1['dest'], lang),         top1_avg=f'{top1["avg"]:.1f}',
        summer1=_dest_name(summer[0]['dest'], lang),  summer1_avg=f'{summer[0]["avg"]:.1f}',
        winter1=_dest_name(winter[0]['dest'], lang),  winter1_avg=f'{winter[0]["avg"]:.1f}',
    )
    _cl_render(pc, lang, ctx,
               tables=[make_table_annual(annual, 20, lang, country_info),
                       make_table_seasonal(summer, 10, lang, country_info),
                       make_table_seasonal(winter, 10, lang, country_info)],
               jsonld_data=annual, jsonld_n=20,
               print_suffix=f' (Europe, top={top1["dest"]["nom_bare"]})')

def gen_ete(dests, climate, lang, country_info=None):
    summer  = dedup_country(compute_seasonal(climate, dests, [6,7,8]), dests)
    top1    = summer[0]
    n_dests = len(summer)
    pc  = load_locale(lang)['classement_pages']['ete']
    ctx = dict(
        n=n_dests,
        top1=_dest_name(top1['dest'], lang),     top1_avg=f'{top1["avg"]:.1f}',
        top2=_dest_name(summer[1]['dest'], lang), top2_avg=f'{summer[1]["avg"]:.1f}',
        top3=_dest_name(summer[2]['dest'], lang), top3_avg=f'{summer[2]["avg"]:.1f}',
    )
    _cl_render(pc, lang, ctx,
               tables=[make_table_seasonal(summer, 20, lang, country_info)],
               jsonld_data=summer, jsonld_n=20,
               print_suffix=f' (été, top={top1["dest"]["nom_bare"]})')

def gen_hiver(dests, climate, lang, country_info=None):
    winter  = dedup_country(compute_seasonal(climate, dests, [12,1,2]), dests)
    top1    = winter[0]
    n_dests = len(winter)
    pc  = load_locale(lang)['classement_pages']['hiver']
    ctx = dict(
        n=n_dests,
        top1=_dest_name(top1['dest'], lang),     top1_avg=f'{top1["avg"]:.1f}',
        top2=_dest_name(winter[1]['dest'], lang), top2_avg=f'{winter[1]["avg"]:.1f}',
        top3=_dest_name(winter[2]['dest'], lang), top3_avg=f'{winter[2]["avg"]:.1f}',
    )
    _cl_render(pc, lang, ctx,
               tables=[make_table_seasonal(winter, 20, lang, country_info)],
               jsonld_data=winter, jsonld_n=20,
               print_suffix=f' (hiver, top={top1["dest"]["nom_bare"]})')

def gen_nomades(dests, climate, lang, country_info=None):
    nomad   = dedup_country(compute_nomad(climate, dests), dests)
    top1    = nomad[0]
    n_dests = len(nomad)
    pc  = load_locale(lang)['classement_pages']['nomades']
    ctx = dict(
        n=n_dests,
        top1=_dest_name(top1['dest'], lang),    top1_avg=f'{top1["avg"]:.1f}',
        top2=_dest_name(nomad[1]['dest'], lang), top2_avg=f'{nomad[1]["avg"]:.1f}',
        top1_stdev=f'{top1["stdev"]:.2f}',
    )
    _cl_render(pc, lang, ctx,
               tables=[make_table_nomad(nomad, 20, lang)],
               jsonld_data=nomad, jsonld_n=20,
               print_suffix=f' (nomades, top={top1["dest"]["nom_bare"]})')

def gen_beach(dests, climate, lang, country_info=None):
    annual  = dedup_country(compute_beach(climate, dests), dests)
    summer  = dedup_country(compute_beach_seasonal(climate, dests, [6,7,8]), dests)
    winter  = dedup_country(compute_beach_seasonal(climate, dests, [12,1,2]), dests)
    top1    = annual[0]
    n_dests = len(annual)
    pc  = load_locale(lang)['classement_pages']['beach']
    ctx = dict(
        n=n_dests,
        top1=_dest_name(top1['dest'], lang),          top1_avg=f'{top1["avg"]:.1f}',
        top1_sea=f'{top1["avg_sea"]:.0f}',            top1_months=top1['good_months'],
        summer1=_dest_name(summer[0]['dest'], lang),   summer1_avg=f'{summer[0]["avg"]:.1f}',
        winter1=_dest_name(winter[0]['dest'], lang),   winter1_avg=f'{winter[0]["avg"]:.1f}',
    )
    _cl_render(pc, lang, ctx,
               tables=[make_table_beach_annual(annual, 25, lang),
                       make_table_beach(summer, 20, lang),
                       make_table_beach(winter, 20, lang)],
               jsonld_data=annual, jsonld_n=25,
               print_suffix=f' (plage, {n_dests} coastal, top={top1["dest"]["nom_bare"]})')

def gen_caribbean(dests, climate, lang, country_info=None):
    annual  = dedup_country(compute_annual(climate, dests, caribbean_only=True), dests)
    summer  = dedup_country(compute_seasonal(climate, dests, [12,1,2], caribbean_only=True), dests)  # "été" caribéen = hiver boréal
    winter  = dedup_country(compute_seasonal(climate, dests, [6,7,8], caribbean_only=True), dests)   # saison humide
    top1    = annual[0]
    n_dests = len(annual)
    pc  = load_locale('en' if lang == 'en-us' else lang)['classement_pages']['caraibes']
    ctx = dict(
        n=n_dests,
        top1=_dest_name(top1['dest'], lang),         top1_avg=f'{top1["avg"]:.1f}',
        dry1=_dest_name(summer[0]['dest'], lang),     dry1_avg=f'{summer[0]["avg"]:.1f}',
        wet1=_dest_name(winter[0]['dest'], lang),     wet1_avg=f'{winter[0]["avg"]:.1f}',
    )
    _cl_render(pc, lang, ctx,
               tables=[make_table_annual(annual, n_dests, lang, country_info),
                       make_table_seasonal(summer, n_dests, lang, country_info),
                       make_table_seasonal(winter, n_dests, lang, country_info)],
               jsonld_data=annual, jsonld_n=n_dests,
               print_suffix=f' (Caraïbes, {n_dests} dests, top={top1["dest"]["nom_bare"]})')

# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main():
    print('Loading data...')
    dests = load_destinations()
    climate = load_climate()
    country_info = load_country_info()
    print(f'  {len(dests)} destinations, {len(climate)} climate entries')

    print('\nGenerating FR pages...')
    gen_mondial(dests, climate, 'fr', country_info)
    gen_europe(dests, climate, 'fr', country_info)
    gen_ete(dests, climate, 'fr', country_info)
    gen_hiver(dests, climate, 'fr', country_info)
    gen_nomades(dests, climate, 'fr', country_info)
    gen_beach(dests, climate, 'fr', country_info)
    gen_caribbean(dests, climate, 'fr', country_info)

    print('\nGenerating EN pages...')
    gen_mondial(dests, climate, 'en', country_info)
    gen_europe(dests, climate, 'en', country_info)
    gen_ete(dests, climate, 'en', country_info)
    gen_hiver(dests, climate, 'en', country_info)
    gen_nomades(dests, climate, 'en', country_info)
    gen_beach(dests, climate, 'en', country_info)
    gen_caribbean(dests, climate, 'en', country_info)

    print('\nGenerating ES pages...')
    gen_mondial(dests, climate, 'es', country_info)
    gen_europe(dests, climate, 'es', country_info)
    gen_ete(dests, climate, 'es', country_info)
    gen_hiver(dests, climate, 'es', country_info)
    gen_nomades(dests, climate, 'es', country_info)
    gen_beach(dests, climate, 'es', country_info)
    gen_caribbean(dests, climate, 'es', country_info)

    print('\nGenerating EN-US pages (°F)...')
    gen_mondial(dests, climate, 'en-us', country_info)
    gen_europe(dests, climate, 'en-us', country_info)
    gen_ete(dests, climate, 'en-us', country_info)
    gen_hiver(dests, climate, 'en-us', country_info)
    gen_nomades(dests, climate, 'en-us', country_info)
    gen_beach(dests, climate, 'en-us', country_info)
    gen_caribbean(dests, climate, 'en-us', country_info)

    print('\nGenerating DE pages...')
    gen_mondial(dests, climate, 'de', country_info)
    gen_europe(dests, climate, 'de', country_info)
    gen_ete(dests, climate, 'de', country_info)
    gen_hiver(dests, climate, 'de', country_info)
    gen_nomades(dests, climate, 'de', country_info)
    gen_beach(dests, climate, 'de', country_info)
    gen_caribbean(dests, climate, 'de', country_info)

    print('\n✅ All 35 ranking pages generated (FR + EN + ES + EN-US + DE).')

if __name__ == '__main__':
    main()
