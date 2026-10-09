"""
Moteur « Où partir à mes dates » (pages « Où partir en [mois] » fusionnées).

Une seule logique, deux exécutions :
  - ici, en Python, pour écrire dans le HTML l'état par défaut de chaque page
    (classement, à retenir, projets, régions, à éviter) : c'est ce que lit Google ;
  - dans js/date-engine.js, à l'identique, quand le visiteur change ses dates
    ou ses critères.
Toute modification de calcul doit être faite dans les deux fichiers
(tests/test_date_engine.py compare les deux sur des cas fixes).

Données (engine/data-v1.json, publié avec le site) :
  - par destination et par mois : score général, plage, ski, randonnée, part des
    jours de pluie, températures, soleil, mer (mêmes fonctions que les pages
    mensuelles : scoring.compute_ski_score, compute_hiking_score) ;
  - pour les destinations collectées (data/weekly), la pluie jour par jour
    2016-2025 (1 = jour de pluie selon le seuil du mois recalé sur les stations)
    et la température maximale par semaine.
"""
import base64
import csv
import datetime as dt
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
YEARS = list(range(2016, 2026))
CUM = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
LEN = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
SKI_DUPES = {'val-disere', 'sierra-nevada', 'queenstown-ski'}
UC_KEY = {'gen': 's', 'plage': 'b', 'ski': 'k', 'rando': 'hk'}
UC_MTN = {'ski', 'rando'}
PAGE = 25
DATA_VERSION = 'v1'

# ── Textes (source unique : injectés dans la page pour le script client) ─────

I18N = {
    'fr': {
        'months': ['janvier', 'février', 'mars', 'avril', 'mai', 'juin', 'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre'],
        'ms': ['janv.', 'févr.', 'mars', 'avr.', 'mai', 'juin', 'juil.', 'août', 'sept.', 'oct.', 'nov.', 'déc.'],
        'wd': ['dimanche', 'lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi'],
        'uc': {'gen': '☀️ Météo générale', 'plage': '🏖️ Plage', 'ski': '⛷️ Ski', 'rando': '🥾 Randonnée'},
        'uc_t': {'gen': 'Météo générale', 'plage': 'Plage et baignade', 'ski': 'Montagne et ski', 'rando': 'Randonnée'},
        'regions': {'eu': 'Europe', 'af-nord': 'Afrique du Nord', 'af': 'Afrique et océan Indien', 'atl': 'Îles atlantiques',
                    'am-n': 'Amérique du Nord', 'car': 'Caraïbes', 'am-s': 'Amérique du Sud', 'as': 'Asie',
                    'me': 'Moyen-Orient', 'oc': 'Océanie', 'other': 'Autres pays'},
        'secu': {'1': '🟢 Vigilance normale', '2': '🟡 Vigilance renforcée', '3': '🟠 Déconseillé', '4': '🔴 Formellement déconseillé'},
        'budget': {'1': '💚 Économique', '2': '💛 Abordable', '3': '🟡 Modéré', '4': '🟠 Coûteux', '5': '🔴 Très coûteux'},
        'budget_opts': [[5, 'Tous budgets'], [2, 'Jusqu’à 💛 Abordable'], [3, 'Jusqu’à 🟡 Modéré'], [4, 'Jusqu’à 🟠 Coûteux']],
        'secu_opts': [[4, 'Toutes destinations'], [2, 'Jusqu’à 🟡 Vigilance renforcée'], [1, '🟢 Vigilance normale seulement']],
        'heat_opts': [[-99, 'Peu importe'], [16, '16 °C et plus'], [20, '20 °C et plus'], [24, '24 °C et plus']],
        'sorts': {'score': 'Score BestDateWeather', 'dry': 'Les plus sûres (moins de pluie)', 'hot': 'Les plus chaudes',
                  'near': 'Les plus proches', 'cheap': 'Les moins chères sur place'},
        'deps': [['Paris', 48.86, 2.35], ['Lyon', 45.76, 4.84], ['Marseille', 43.30, 5.37], ['Nice', 43.70, 7.27],
                 ['Toulouse', 43.60, 1.44], ['Bordeaux', 44.84, -0.58], ['Nantes', 47.22, -1.55], ['Lille', 50.63, 3.06],
                 ['Bruxelles', 50.85, 4.35], ['Genève', 46.20, 6.14]],
        'holidays': {
            '9': [{'id': 'toussaint', 'chip': 'Vacances de la Toussaint', 'em': 'à la Toussaint', 'a': '2026-10-17', 'b': '2026-11-01',
                   'note': 'Vacances de la Toussaint, mêmes dates pour les trois zones.'}],
            '11': [{'id': 'noel', 'chip': 'Vacances de Noël', 'em': 'à Noël', 'a': '2026-12-19', 'b': '2027-01-03',
                    'note': 'Vacances de Noël, mêmes dates pour les trois zones.'}],
            '1': [{'id': 'hiver', 'chip': 'Vacances de février', 'em': 'aux vacances de février',
                   'zones': {'A': ['2027-02-13', '2027-02-28'], 'B': ['2027-02-20', '2027-03-07'], 'C': ['2027-02-06', '2027-02-21']}}],
            '3': [{'id': 'printemps', 'chip': 'Vacances de printemps', 'em': 'aux vacances de printemps',
                   'zones': {'A': ['2027-04-10', '2027-04-25'], 'B': ['2027-04-17', '2027-05-02'], 'C': ['2027-04-03', '2027-04-18']}}],
        },
        'zones': {'A': 'Besançon, Bordeaux, Clermont-Ferrand, Dijon, Grenoble, Limoges, Lyon, Poitiers',
                  'B': 'Aix-Marseille, Amiens, Lille, Nancy-Metz, Nantes, Nice, Normandie, Orléans-Tours, Reims, Rennes, Strasbourg',
                  'C': 'Créteil, Montpellier, Paris, Toulouse, Versailles'},
        't': {
            'h1_month': 'Où partir en <em>{m}</em> ?', 'h1_other': 'Où partir <em>{x}</em> ?', 'h1_dates': 'Où partir <em>{x}</em> ?',
            'your_dates': 'à vos dates', 'when': '<b>Du {a} au {b}</b>, soit {n} jours.', 'n_days': '{n} jours',
            'sub_month': 'Classement établi jour par jour sur 2016-2025 quand l’historique existe, sinon sur les moyennes du mois.',
            'sub_dates': 'Classement calculé pour vos dates exactes.',
            'sub_zone': 'Vacances scolaires, zone {z} : académies de {list}.',
            'all_month': 'Tout {m}', 'zone_chip': 'Zone {z} · {r}',
            'top': 'Top {n} · {uc}{reg} · {where}', 'your_dates_where': 'vos dates',
            'count': '{k} destinations sur {n} analysées correspondent à vos critères.',
            'count1': '{k} destination sur {n} analysées correspond à vos critères.',
            'empty': 'Aucune destination ne correspond. Allongez le temps de vol, élargissez la région ou baissez la chaleur demandée.',
            'err_missing': 'Indiquez une date de départ et une date de retour.', 'err_order': 'La date de retour doit suivre la date de départ.',
            'err_long': 'Choisissez un séjour de deux mois au plus.',
            'f_safe': 'La plus sûre', 'f_near': 'La plus proche au sec', 'f_cheap': 'La moins chère au sec',
            'f_trap': 'Bonne destination, mauvaises dates', 'f_trap_far': 'Plus loin, le piège',
            'f_best_ski': 'Le meilleur score ski', 'f_best_rando': 'Le meilleur score randonnée', 'f_near_m': 'La plus proche', 'f_cheap_m': 'La moins chère',
            'dry_years': 'presque sèche {k} années sur {n}', 'lt1': 'moins d’un jour de pluie sur {n}', 'approx_days': '≈ {x} j de pluie sur {n}',
            'fd_safe': '{dry}, {t} °C, ≈ {h} de vol.', 'fd_near': '≈ {h} de vol depuis {dep}, {t} °C, {dry}.',
            'fd_cheap': 'Budget {b}, {t} °C, {dry}.', 'fd_trap': 'Excellente en {bm} ({bs}/10), mais {x} jours de pluie sur {n} à ces dates.',
            'fd_best_m': '{s}/10, {tn} à {tx} °C, ≈ {h} de vol.', 'fd_near_m': '≈ {h} de vol depuis {dep}, score {s}/10.', 'fd_cheap_m': 'Budget {b}, score {s}/10.',
            'flight': '≈ {h} de vol', 'sea': 'Mer {t} °C', 'card': 'Fiche',
            'dry_line': 'Presque sec <b>{k} années sur {n}</b> · {x} j de pluie sur {d}', 'approx_line': '{x} (moyenne du mois)',
            'approx_lt1': 'Moins d’un jour de pluie sur {n}', 'approx_n': '≈ {x} j de pluie sur {n}',
            'ski_line': 'Soleil {s} h/j · nuits à {tn} °C', 'season_title': '{y} : {r} jour{p} de pluie',
            'lg_dry': 'Presque sec (au plus {l} j de pluie)', 'lg_mid': '{a} à {b} j', 'lg_wet': 'Plus de {b} j',
            'lg_one_y': 'Une case par année (2016 à 2025)', 'lg_one_s': 'Une case par saison (2016-17 à 2024-25)',
            'lg_approx': 'Sans cases : moyenne du mois (historique quotidien en cours de collecte)',
            'mini_rain': '{t} °C · {r} % pluie', 'see_all': 'Tout voir', 'see': 'Voir', 'none': 'Aucune destination avec ces critères',
            'reg_title': 'Par région · {where}', 'avoid_title': 'À éviter · {where}',
            'avoid_lead': 'Les destinations les moins favorables pour ces dates, sur les {n} analysées (stations de montagne exclues : voir le classement ski).',
            'fly_any': 'peu importe', 'world': 'Monde entier', 'err_load': 'Impossible de charger les données. Rechargez la page.',
            'other_city': 'Autre ville…', 'city_ph': 'Tapez une ville (ex. Rennes, Bâle, Montréal)', 'city_none': 'Aucune ville trouvée.', 'city_err': 'Recherche indisponible, réessayez.',
        },
    },
    'en': {
        'months': ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'],
        'ms': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
        'wd': ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'],
        'uc': {'gen': '☀️ General weather', 'plage': '🏖️ Beach', 'ski': '⛷️ Skiing', 'rando': '🥾 Hiking'},
        'uc_t': {'gen': 'General weather', 'plage': 'Beach and swimming', 'ski': 'Mountain and skiing', 'rando': 'Hiking'},
        'regions': {'eu': 'Europe', 'af-nord': 'North Africa', 'af': 'Africa and Indian Ocean', 'atl': 'Atlantic islands',
                    'am-n': 'North America', 'car': 'Caribbean', 'am-s': 'South America', 'as': 'Asia',
                    'me': 'Middle East', 'oc': 'Oceania', 'other': 'Other countries'},
        'secu': {'1': '🟢 Normal', '2': '🟡 High vigilance', '3': '🟠 Avoid if possible', '4': '🔴 Do not travel'},
        'budget': {'1': '💚 Budget', '2': '💛 Affordable', '3': '🟡 Moderate', '4': '🟠 Expensive', '5': '🔴 Very expensive'},
        'budget_opts': [[5, 'All budgets'], [2, 'Up to 💛 Affordable'], [3, 'Up to 🟡 Moderate'], [4, 'Up to 🟠 Expensive']],
        'secu_opts': [[4, 'All destinations'], [2, 'Up to 🟡 High vigilance'], [1, '🟢 Normal only']],
        'heat_opts': [[-99, 'Any'], [16, '16 °C and above'], [20, '20 °C and above'], [24, '24 °C and above']],
        'sorts': {'score': 'BestDateWeather score', 'dry': 'Safest (least rain)', 'hot': 'Warmest',
                  'near': 'Closest', 'cheap': 'Cheapest on the ground'},
        'deps': [['London', 51.51, -0.13], ['Manchester', 53.48, -2.24], ['Dublin', 53.35, -6.26], ['Amsterdam', 52.37, 4.90],
                 ['Frankfurt', 50.11, 8.68], ['New York', 40.71, -74.01], ['Chicago', 41.88, -87.63], ['Los Angeles', 34.05, -118.24],
                 ['Toronto', 43.65, -79.38], ['Sydney', -33.87, 151.21]],
        'holidays': {
            '11': [{'id': 'christmas', 'chip': 'Christmas and New Year', 'em': 'for Christmas', 'a': '2026-12-19', 'b': '2027-01-03',
                    'note': 'Christmas and New Year: 19 December to 3 January.'}],
        },
        'zones': {},
        't': {
            'h1_month': 'Where to go in <em>{m}</em>', 'h1_other': 'Where to go <em>{x}</em>', 'h1_dates': 'Where to go <em>{x}</em>',
            'your_dates': 'on your dates', 'when': '<b>{a} to {b}</b>, {n} days.', 'n_days': '{n} days',
            'sub_month': 'Ranked day by day over 2016-2025 where daily records exist, otherwise on monthly averages.',
            'sub_dates': 'Ranking calculated for your exact dates.', 'sub_zone': '',
            'all_month': 'All of {m}', 'zone_chip': 'Zone {z} · {r}',
            'top': 'Top {n} · {uc}{reg} · {where}', 'your_dates_where': 'your dates',
            'count': '{k} of {n} destinations analysed match your criteria.',
            'count1': '{k} of {n} destinations analysed matches your criteria.',
            'empty': 'No destination matches. Allow a longer flight, widen the region or lower the temperature.',
            'err_missing': 'Enter a departure date and a return date.', 'err_order': 'The return date must come after the departure date.',
            'err_long': 'Choose a trip of two months at most.',
            'f_safe': 'Safest bet', 'f_near': 'Closest dry option', 'f_cheap': 'Cheapest dry option',
            'f_trap': 'Great place, wrong dates', 'f_trap_far': 'Further away, the trap',
            'f_best_ski': 'Best skiing score', 'f_best_rando': 'Best hiking score', 'f_near_m': 'Closest', 'f_cheap_m': 'Cheapest',
            'dry_years': 'nearly dry {k} years out of {n}', 'lt1': 'less than one rainy day out of {n}', 'approx_days': '≈ {x} rainy days out of {n}',
            'fd_safe': '{dry}, {t} °C, ≈ {h} flight.', 'fd_near': '≈ {h} flight from {dep}, {t} °C, {dry}.',
            'fd_cheap': 'Cost of living: {b}, {t} °C, {dry}.', 'fd_trap': 'Excellent in {bm} ({bs}/10), but {x} rainy days out of {n} on these dates.',
            'fd_best_m': '{s}/10, {tn} to {tx} °C, ≈ {h} flight.', 'fd_near_m': '≈ {h} flight from {dep}, score {s}/10.', 'fd_cheap_m': 'Cost of living: {b}, score {s}/10.',
            'flight': '≈ {h} flight', 'sea': 'Sea {t} °C', 'card': 'Guide',
            'dry_line': 'Nearly dry <b>{k} years out of {n}</b> · {x} rainy days out of {d}', 'approx_line': '{x} (monthly average)',
            'approx_lt1': 'Less than one rainy day out of {n}', 'approx_n': '≈ {x} rainy days out of {n}',
            'ski_line': 'Sun {s} h/day · nights at {tn} °C', 'season_title': '{y}: {r} rainy day{p}',
            'lg_dry': 'Nearly dry (at most {l} rainy days)', 'lg_mid': '{a} to {b} days', 'lg_wet': 'More than {b} days',
            'lg_one_y': 'One square per year (2016 to 2025)', 'lg_one_s': 'One square per season (2016-17 to 2024-25)',
            'lg_approx': 'No squares: monthly average (daily records still being collected)',
            'mini_rain': '{t} °C · {r}% rain', 'see_all': 'See all', 'see': 'See', 'none': 'No destination with these criteria',
            'reg_title': 'By region · {where}', 'avoid_title': 'Best avoided · {where}',
            'avoid_lead': 'The least favourable destinations for these dates, out of {n} analysed (mountain resorts excluded: see the skiing ranking).',
            'fly_any': 'any', 'world': 'Whole world', 'err_load': 'Could not load the data. Please reload the page.',
            'other_city': 'Other city…', 'city_ph': 'Type a city (e.g. Bristol, Zurich, Boston)', 'city_none': 'No city found.', 'city_err': 'Search unavailable, please try again.',
        },
    },
}
I18N['en']['holidays']['11'][0]['wh'] = 'Christmas and New Year'

# Espagnol, allemand, anglais américain (°F, miles) : lib/engine_langs.py
from lib import engine_langs as _EL  # noqa: E402
I18N['es'] = _EL.I18N_ES
I18N['de'] = _EL.I18N_DE
I18N['en-us'] = _EL.us_i18n(I18N['en'])
for _l, _d in I18N.items():
    _d['nf'] = _EL.NF[_l]
LANGS = list(I18N)


# ── Données ───────────────────────────────────────────────────────────────────

def _bits_b64(line):
    """365 caractères '0'/'1' → 46 octets en base64 (bit de poids fort en premier)."""
    by = bytearray(46)
    for i, c in enumerate(line):
        if c == '1':
            by[i >> 3] |= 1 << (7 - (i & 7))
    return base64.b64encode(bytes(by)).decode('ascii')


def _daily(slug):
    f = ROOT / 'data' / 'weekly' / f'{slug}.json'
    if not f.exists():
        return None
    w = json.load(open(f, encoding='utf-8'))
    start = dt.date.fromisoformat(w['precip_daily']['start'])
    vals = w['precip_daily']['values']
    thr = {int(k): (float(v) if v is not None else 1.0) for k, v in w['rain_threshold_mm'].items()}
    years = []
    for y in YEARS:
        line, day, ok = [], dt.date(y, 1, 1), True
        while day.year == y:
            if not (day.month == 2 and day.day == 29):
                i = (day - start).days
                v = vals[i] if 0 <= i < len(vals) else None
                if v is None:
                    ok = False
                line.append('1' if (v is not None and v >= thr[day.month]) else '0')
            day += dt.timedelta(days=1)
        years.append(_bits_b64(''.join(line)) if ok else None)
    return {'r': years, 'tw': [x['tmax'] for x in w['weeks']]}


def build_dataset(dests, climate, country_info):
    """Une entrée par destination classable (mêmes exclusions que les pages mensuelles)."""
    from scoring import compute_ski_score, compute_hiking_score
    from lib.regions import reg
    from lib.region_children import REGION_CHILDREN
    dup = set(json.load(open(ROOT / 'data' / 'duplicate_destinations.json', encoding='utf-8')).keys())
    sea = {}
    with open(ROOT / 'data' / 'climate.csv', encoding='utf-8-sig') as f:
        for r in csv.DictReader(f):
            sea.setdefault(r['slug'], [None] * 12)[int(r['mois_num']) - 1] = float(r['sea_temp']) if r.get('sea_temp') else None
    out = []
    for slug in sorted(dests):
        d = dests[slug]
        if slug in SKI_DUPES or slug in dup or d.get('precision') == 'country' or slug not in climate:
            continue
        mtn = str(d.get('mountain', '')).strip().lower() in ('true', '1', 'yes')
        coastal = str(d.get('coastal', '')).strip().lower() in ('true', '1', 'yes')
        M = {k: [None] * 12 for k in ('s', 'b', 'k', 'hk', 'r', 'tx', 'tn', 'sun')}
        for m in range(1, 13):
            c = climate[slug].get(m)
            if not c:
                continue
            i = m - 1
            M['s'][i] = round(c['score'], 1)
            M['b'][i] = round(c['beach_score'], 1) if (coastal and c.get('beach_score') is not None) else None
            if mtn:
                M['k'][i] = round(compute_ski_score(c['tmax'], c['rain_pct'], c['sun_h']), 1)
                M['hk'][i] = round(compute_hiking_score(c['tmax'], c['rain_pct'], c['sun_h'], c.get('precip_mm')), 1)
            M['r'][i] = round(c['rain_pct'], 1)
            M['tx'][i] = round(c['tmax'], 1)
            M['tn'][i] = round(c['tmin'], 1)
            M['sun'][i] = round(c['sun_h'], 1)
        M['sea'] = sea.get(slug, [None] * 12)
        ci = (country_info or {}).get(d.get('pays', ''), {})
        nom_fr = d.get('nom_bare') or slug
        nom_en = d.get('nom_en') or nom_fr
        rec = {
            # slugs : s = fr, e = en et en-us, se = es, sd = de (mêmes règles que generate_piliers.get_slug)
            's': slug, 'e': d.get('slug_en') or slug,
            'se': d.get('slug_es') or d.get('slug_en') or slug, 'sd': d.get('slug_de') or d.get('slug_en') or slug,
            # noms et pays : [fr, en, es, de] (mêmes règles que generate_piliers.get_nom / get_pays)
            'n': [nom_fr, nom_en, d.get('nom_es') or nom_fr, d.get('nom_de') or nom_en],
            'p': [d.get('pays', ''), d.get('country_en') or d.get('pays', ''),
                  d.get('country_es') or d.get('pays', ''), d.get('country_de') or d.get('pays', '')],
            'reg': reg(d.get('pays', ''), slug), 'rl': int(ci.get('risk_level', 2)), 'bi': int(ci.get('budget_index', 3)),
            'm': 1 if mtn else 0, 'cc': (d.get('flag') or '').upper(),
            'la': round(float(d['lat']), 3), 'lo': round(float(d['lon']), 3), 'M': M,
        }
        if slug in REGION_CHILDREN and REGION_CHILDREN[slug]:
            rec['ch'] = sorted(REGION_CHILDREN[slug])
        daily = _daily(slug)
        if daily:
            rec.update(daily)
        out.append(rec)
    return out


def write_dataset(dataset, path=None):
    path = Path(path or (ROOT / 'engine' / f'data-{DATA_VERSION}.json'))
    path.parent.mkdir(parents=True, exist_ok=True)
    json.dump({'years': YEARS, 'dests': dataset}, open(path, 'w', encoding='utf-8'),
              ensure_ascii=False, separators=(',', ':'))
    return path


# ── Calcul (miroir exact de js/date-engine.js) ───────────────────────────────

def _D(iso):
    return dt.date.fromisoformat(iso)


def _doy(mmdd):
    m, d = (int(x) for x in mmdd.split('-'))
    return CUM[m - 1] + d - 1


def _month_of(i):
    m = 11
    while CUM[m] > i:
        m -= 1
    return m


def window(date_from, date_to):
    if not date_from or not date_to:
        return {'error': 'err_missing'}
    span = (_D(date_to) - _D(date_from)).days + 1
    if span < 1:
        return {'error': 'err_order'}
    if span > 62:
        return {'error': 'err_long'}
    f, t = date_from[5:], date_to[5:]
    if f == '02-29':
        f = '03-01'
    if t == '02-29':
        t = '02-28'
    a, b = _doy(f), _doy(t)
    cross = a > b
    days = [(i, 0) for i in range(a, b + 1)] if not cross else \
        [(i, 0) for i in range(a, 365)] + [(i, 1) for i in range(0, b + 1)]
    return {'days': days, 'cross': cross, 'n': len(days), 'limit': max(1, round(len(days) / 7))}


def _hav(a, b, c, d):
    r = math.pi / 180
    p1, p2 = a * r, c * r
    dp, dl = p2 - p1, (d - b) * r
    return 2 * 6371 * math.asin(math.sqrt(math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2))


def flight_h(km):
    return 0.75 + km / 850


def _bit(b64, i, _cache={}):
    by = _cache.get(b64)
    if by is None:
        by = _cache[b64] = base64.b64decode(b64)
    return (by[i >> 3] >> (7 - (i & 7))) & 1


def evaluate(rec, w, uc, dep):
    if uc in UC_MTN and not rec['m']:
        return None
    k = UC_KEY[uc]
    M = rec['M']
    sc = tx = tn = sun = rr = sea = 0.0
    sea_ok = True
    for i, _ in w['days']:
        m = _month_of(i)
        v = M[k][m]
        if v is None or M['tx'][m] is None:
            return None
        sc += v
        tx += rec['tw'][min(51, i // 7)] if 'tw' in rec else M['tx'][m]
        tn += M['tn'][m]
        sun += M['sun'][m]
        rr += M['r'][m] / 100
        if M['sea'][m] is None:
            sea_ok = False
        else:
            sea += M['sea'][m]
    n = w['n']
    o = {'d': rec, 'uc': uc, 'score': sc / n, 'tmax': tx / n, 'tmin': tn / n, 'sun': sun / n,
         'sea': sea / n if sea_ok else None, 'mean': rr, 'share': rr / n, 'daily': False}
    if 'r' in rec:
        n_s = len(YEARS) - 1 if w['cross'] else len(YEARS)
        seasons = []
        for kk in range(n_s):
            ok = True
            rd = 0
            for i, off in w['days']:
                b = rec['r'][kk + off]
                if b is None:
                    ok = False
                    break
                rd += _bit(b, i)
            if ok:
                seasons.append({'y': YEARS[kk], 'rd': rd})
        if len(seasons) >= 6:
            o['daily'] = True
            o['seasons'] = seasons
            o['mean'] = sum(x['rd'] for x in seasons) / len(seasons)
            o['share'] = o['mean'] / n
            o['dry'] = sum(1 for x in seasons if x['rd'] <= w['limit'])
            o['ns'] = len(seasons)
    o['km'] = _hav(dep[1], dep[2], rec['la'], rec['lo'])
    o['h'] = flight_h(o['km'])
    s_all = [x for x in M['s'] if x is not None]
    o['bestSc'] = max(s_all)
    o['rl'] = rec['rl']
    o['best'] = M['s'].index(o['bestSc'])
    return o


SORTERS = {
    'score': lambda x: (-x['score'], x['d']['s']),
    'dry': lambda x: (x['share'], -((x.get('dry') or 0) / (x.get('ns') or 1)), -x['score'], x['d']['s']),
    'hot': lambda x: (-x['tmax'], x['d']['s']),
    'near': lambda x: (x['h'], x['d']['s']),
    'cheap': lambda x: (x['d']['bi'], -x['score'], x['d']['s']),
}


def drop_parents(rows):
    """Une région « parente » (Canaries) disparaît si l'une de ses îles est classée."""
    present = {x['d']['s'] for x in rows}
    return [x for x in rows if not any(c in present for c in x['d'].get('ch', ()))]


def default_state(month_idx, lang):
    y = 2026 if month_idx >= 9 else 2027
    return {'month': month_idx, 'preset': 'month', 'zone': 'C',
            'from': f'{y}-{month_idx + 1:02d}-01', 'to': f'{y}-{month_idx + 1:02d}-{LEN[month_idx]:02d}',
            'uc': 'gen', 'reg': 'all', 'dep': 0, 'fly': 16, 'heat': -99, 'budget': 5, 'rl': 2, 'sort': 'score', 'shown': PAGE}


def compute_view(dataset, st, lang):
    """Tout ce que la page affiche pour un état donné (mêmes règles que le script client)."""
    L = I18N[lang]
    w = window(st['from'], st['to'])
    if 'error' in w:
        return {'error': w['error']}
    dep = L['deps'][st['dep']]
    ev = {k: [o for o in (evaluate(r, w, k, dep) for r in dataset) if o] for k in UC_KEY}
    mtn = st['uc'] in UC_MTN

    def ok_base(x): return x['rl'] <= st['rl'] and x['d']['bi'] <= st['budget']
    def ok_fly(x): return st['fly'] >= 16 or x['h'] <= st['fly']
    def ok_heat(x): return mtn or x['tmax'] >= st['heat']
    def ok_reg(x): return st['reg'] == 'all' or x['d']['reg'] == st['reg']

    rows = drop_parents([x for x in ev[st['uc']] if ok_base(x) and ok_fly(x) and ok_heat(x) and ok_reg(x)])
    rows.sort(key=SORTERS[st['sort']])

    facts, used = [], set()

    def pick(arr, key, fn, cls=''):
        for x in arr:
            if x['d']['s'] not in used:
                used.add(x['d']['s'])
                facts.append({'k': key, 'x': x, 'cls': cls, 'fn': fn})
                return

    if not mtn:
        # « La plus sûre » : la moins pluvieuse parmi les bonnes destinations (score ≥ 7), comme les deux suivantes
        good = [x for x in rows if x['score'] >= 7]
        pick(sorted(good or rows, key=SORTERS['dry']), 'f_safe', 'fd_safe')
        cand = [x for x in rows if x['share'] <= 0.10 and x['score'] >= 7]
        pick(sorted(cand, key=SORTERS['near']), 'f_near', 'fd_near')
        pick(sorted(cand, key=SORTERS['cheap']), 'f_cheap', 'fd_cheap')

        def ww(arr):
            return sorted([x for x in arr if x['bestSc'] >= 7.5 and x['tmax'] >= max(st['heat'], 20) and x['share'] >= 0.35],
                          key=lambda x: (-x['tmax'], x['d']['s']))
        near = ww([x for x in ev[st['uc']] if ok_base(x) and ok_fly(x)])
        if near:
            pick(near, 'f_trap', 'fd_trap', 'warn')
        else:
            pick(ww([x for x in ev[st['uc']] if ok_base(x)]), 'f_trap_far', 'fd_trap', 'warn')
    else:
        pick(sorted(rows, key=SORTERS['score']), 'f_best_ski' if st['uc'] == 'ski' else 'f_best_rando', 'fd_best_m')
        cand = [x for x in rows if x['score'] >= 7]
        pick(sorted(cand, key=SORTERS['near']), 'f_near_m', 'fd_near_m')
        pick(sorted(cand, key=SORTERS['cheap']), 'f_cheap_m', 'fd_cheap_m')

    projects = {}
    for k in ('plage', 'ski', 'rando'):
        projects[k] = sorted(drop_parents([x for x in ev[k] if ok_base(x) and ok_fly(x)]), key=SORTERS['score'])[:5]
    g = drop_parents([x for x in ev['gen'] if ok_base(x)])
    regions = {}
    for r in L['regions']:
        if r == 'other':
            continue
        top = sorted([x for x in g if x['d']['reg'] == r], key=SORTERS['score'])[:4]
        if top:
            regions[r] = top
    avoid = sorted(drop_parents([x for x in ev['gen'] if not x['d']['m']]), key=lambda x: (x['score'], x['d']['s']))[:8]
    return {'w': w, 'rows': rows, 'n_uc': len(ev[st['uc']]), 'n_gen': len(ev['gen']), 'facts': facts,
            'projects': projects, 'regions': regions, 'avoid': avoid}
