#!/usr/bin/env python3
"""
fetch_climate.py — BestDateWeather
====================================
Récupère les données climatiques via Open-Meteo ERA5 Historical Archive
et génère les 12 lignes climate.csv pour une ou plusieurs destinations.

Usage :
  python3 fetch_climate.py istanbul              # une destination (doit être dans destinations.csv)
  python3 fetch_climate.py --new                  # toutes les destinations sans données climate
  python3 fetch_climate.py --all                  # toutes les destinations (écrase les données existantes)
  python3 fetch_climate.py --preview istanbul     # affiche sans écrire
  python3 fetch_climate.py --years 2018-2023 istanbul  # période custom

Source : ERA5 reanalysis via https://open-meteo.com/en/docs/historical-weather-api
Période par défaut : 2019-2023 (5 ans complets)

Classification automatique :
  Classes (rec/mid/avoid) assignées par raw_score depuis scoring.py.
  Seuils : raw_score >= 0.55 → rec | >= 0.35 → mid | < 0.35 → avoid
  ⚠️  Auto-classification = approximation. Relecture recommandée pour
  les destinations atypiques (mousson, altitude, microclimat).

Scores calculés par scoring.py (source de vérité unique).
"""

import csv, json, os, sys, time, urllib.request
from datetime import date

DIR  = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(DIR, 'data')

# Import scoring from same directory
sys.path.insert(0, DIR)
from scoring import raw_score, compute_scores, TROPICAL_DESTINATIONS

# ── CONSTANTES ───────────────────────────────────────────────────────────────

MONTHS_FR = ['Janvier','Février','Mars','Avril','Mai','Juin',
             'Juillet','Août','Septembre','Octobre','Novembre','Décembre']

API_BASE = 'https://archive-api.open-meteo.com/v1/archive'
API_VARS = 'temperature_2m_max,temperature_2m_min,precipitation_sum,sunshine_duration'
RAIN_THRESHOLD_MM = 1.0  # WMO standard: jour pluvieux = précipitations >= 1mm

# Classification thresholds (based on raw_score from scoring.py)
# Calibrated against 996 existing months:
#   avoid p75=0.42, mid med=0.51, rec p25=0.62
# Conservative: ensures avoid is truly bad, rec is truly good
CLS_REC_THRESHOLD   = 0.55
CLS_AVOID_THRESHOLD = 0.35

DEFAULT_START = '2019-01-01'
DEFAULT_END   = '2023-12-31'


# ── DATA LOADING ─────────────────────────────────────────────────────────────

def load_destinations():
    """Load destinations.csv → {slug_fr: row_dict}"""
    dests = {}
    for row in csv.DictReader(open(f'{DATA}/destinations.csv', encoding='utf-8-sig')):
        dests[row['slug_fr']] = row
    return dests


def load_existing_climate_slugs():
    """Return set of slugs already in climate.csv."""
    slugs = set()
    for row in csv.DictReader(open(f'{DATA}/climate.csv', encoding='utf-8-sig')):
        slugs.add(row['slug'])
    return slugs


# ── API ──────────────────────────────────────────────────────────────────────

def fetch_daily(lat, lon, start_date, end_date, max_retries=5):
    """Fetch daily weather data from Open-Meteo ERA5 archive with retry."""
    url = (f'{API_BASE}?latitude={lat}&longitude={lon}'
           f'&start_date={start_date}&end_date={end_date}'
           f'&daily={API_VARS}&timezone=auto')

    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'BestDateWeather/1.0'})
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read())
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < max_retries - 1:
                wait = 2 ** (attempt + 1)  # 2, 4, 8, 16, 32s
                print(f"  ⏳ Rate limited, retry in {wait}s... ({attempt + 1}/{max_retries})")
                time.sleep(wait)
            else:
                raise


def compute_monthly_averages(data):
    """
    Compute monthly climate averages from daily Open-Meteo data.

    Returns: list of 12 dicts with keys:
      tmin, tmax, rain_pct, precip_mm, sun_h
    """
    daily = data['daily']
    n_years = len(set(d[:4] for d in daily['time']))

    # Group by month
    from collections import defaultdict
    months = defaultdict(lambda: {
        'tmax': [], 'tmin': [], 'precip': [], 'sun_s': [], 'rain_days': 0, 'total_days': 0
    })

    for i, dt in enumerate(daily['time']):
        m = int(dt[5:7])
        md = months[m]

        tmax = daily['temperature_2m_max'][i]
        tmin = daily['temperature_2m_min'][i]
        precip = daily['precipitation_sum'][i]
        sun = daily['sunshine_duration'][i]

        if tmax is not None:
            md['tmax'].append(tmax)
        if tmin is not None:
            md['tmin'].append(tmin)
        if precip is not None:
            md['precip'].append(precip)
            md['total_days'] += 1
            if precip >= RAIN_THRESHOLD_MM:
                md['rain_days'] += 1
        if sun is not None:
            md['sun_s'].append(sun)

    result = []
    for m in range(1, 13):
        md = months[m]
        if not md['tmax'] or not md['tmin']:
            raise ValueError(f"No temperature data for month {m}")

        tmin = round(sum(md['tmin']) / len(md['tmin']))
        tmax = round(sum(md['tmax']) / len(md['tmax']))
        rain_pct = round(md['rain_days'] / max(md['total_days'], 1) * 100)
        # precip_mm: average daily precipitation (matches existing format)
        precip_mm = round(sum(md['precip']) / max(len(md['precip']), 1), 1)
        sun_h = round(sum(s / 3600 for s in md['sun_s']) / max(len(md['sun_s']), 1), 1)

        result.append({
            'tmin': tmin,
            'tmax': tmax,
            'rain_pct': rain_pct,
            'precip_mm': precip_mm,
            'sun_h': sun_h,
        })

    return result


# ── CLASSIFICATION & SCORING ─────────────────────────────────────────────────

def auto_classify(monthly_data, slug=''):
    """
    Assign rec/mid/avoid classes based on raw_score thresholds.

    Uses scoring.py raw_score function (same weights as production scoring).
    Thresholds calibrated against 996 existing classified months.

    Returns: list of 12 class strings.
    """
    classes = []
    for md in monthly_data:
        rs = raw_score(md['tmax'], md['rain_pct'], md['sun_h'])
        if rs >= CLS_REC_THRESHOLD:
            classes.append('rec')
        elif rs >= CLS_AVOID_THRESHOLD:
            classes.append('mid')
        else:
            classes.append('avoid')
    return classes


def score_destination(monthly_data, classes, slug=''):
    """
    Compute final scores using scoring.py (source de vérité).

    Returns: list of 12 score floats (x.x /10).
    """
    months_input = []
    for i, md in enumerate(monthly_data):
        months_input.append({
            'cls': classes[i],
            'tmax': md['tmax'],
            'rain_pct': md['rain_pct'],
            'sun_h': md['sun_h'],
            'month': MONTHS_FR[i],
        })

    scores = compute_scores(months_input, slug)
    return [s['score_10'] for s in scores]


# ── CSV OUTPUT ───────────────────────────────────────────────────────────────

def format_csv_rows(slug, monthly_data, classes, scores):
    """Format 12 CSV rows for climate.csv."""
    rows = []
    for i in range(12):
        rows.append({
            'slug': slug,
            'mois': MONTHS_FR[i],
            'mois_num': str(i + 1),
            'tmin': str(monthly_data[i]['tmin']),
            'tmax': str(monthly_data[i]['tmax']),
            'rain_pct': str(monthly_data[i]['rain_pct']),
            'precip_mm': str(monthly_data[i]['precip_mm']),
            'sun_h': str(monthly_data[i]['sun_h']),
            'score': str(scores[i]),
            'classe': classes[i],
            'source': 'open-meteo',
        })
    return rows


def append_to_climate_csv(rows):
    """Append rows to climate.csv."""
    path = f'{DATA}/climate.csv'
    with open(path, 'a', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'slug', 'mois', 'mois_num', 'tmin', 'tmax',
            'rain_pct', 'precip_mm', 'sun_h', 'score', 'classe', 'source'
        ], lineterminator='\r\n')
        for row in rows:
            writer.writerow(row)


def remove_from_climate_csv(slug):
    """Remove existing rows for a slug from climate.csv."""
    path = f'{DATA}/climate.csv'
    with open(path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = [r for r in reader if r['slug'] != slug]

    with open(path, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator='\r\n')
        writer.writeheader()
        writer.writerows(rows)


# ── DISPLAY ──────────────────────────────────────────────────────────────────

def print_preview(slug, monthly_data, classes, scores):
    """Print formatted preview of climate data."""
    print(f"\n{'Mo':>3} {'Tmin':>5} {'Tmax':>5} {'Rain%':>6} {'Precip':>7} {'Sun_h':>6} {'Class':>6} {'Score':>6}")
    print('-' * 52)
    for i in range(12):
        md = monthly_data[i]
        cls_marker = {'rec': '🟢', 'mid': '🟡', 'avoid': '🔴'}[classes[i]]
        print(f"{i+1:>3} {md['tmin']:>5} {md['tmax']:>5} {md['rain_pct']:>6} "
              f"{md['precip_mm']:>7} {md['sun_h']:>6} {cls_marker} {classes[i]:>4} {scores[i]:>6}")

    rec_count = classes.count('rec')
    mid_count = classes.count('mid')
    avoid_count = classes.count('avoid')
    print(f"\n  Classification: {rec_count} rec / {mid_count} mid / {avoid_count} avoid")
    is_tropical = slug in TROPICAL_DESTINATIONS
    if is_tropical:
        print(f"  ⚡ Destination tropicale → correction mousson appliquée")


# ── MAIN ─────────────────────────────────────────────────────────────────────

def process_destination(slug, dest, start_date, end_date, preview_only=False, force=False):
    """Fetch, classify, score, and write climate data for one destination."""
    lat = dest['lat']
    lon = dest['lon']
    nom = dest.get('nom_bare', slug)

    print(f"\n{'─' * 50}")
    print(f"📍 {nom} ({slug}) — {lat}, {lon}")

    # Check existing
    existing = load_existing_climate_slugs()
    if slug in existing and not force:
        print(f"  ⏭  Déjà dans climate.csv. Utilisez --all pour écraser.")
        return False

    # Fetch
    print(f"  🌐 Requête Open-Meteo ERA5 ({start_date} → {end_date})...")
    try:
        data = fetch_daily(lat, lon, start_date, end_date)
    except Exception as e:
        print(f"  ❌ Erreur API: {e}")
        return False

    # Compute
    monthly_data = compute_monthly_averages(data)
    classes = auto_classify(monthly_data, slug)
    scores = score_destination(monthly_data, classes, slug)

    # Preview
    print_preview(slug, monthly_data, classes, scores)

    if preview_only:
        print(f"\n  [PREVIEW] Aucune écriture.")
        return True

    # Write
    if slug in existing:
        remove_from_climate_csv(slug)
        print(f"  🔄 Données existantes supprimées.")

    csv_rows = format_csv_rows(slug, monthly_data, classes, scores)
    append_to_climate_csv(csv_rows)
    print(f"  ✅ 12 lignes ajoutées à climate.csv")
    return True


def main():
    args = sys.argv[1:]
    preview = '--preview' in args
    force_all = '--all' in args
    new_only = '--new' in args
    args = [a for a in args if not a.startswith('--')]

    # Parse --years
    start_date = DEFAULT_START
    end_date = DEFAULT_END
    for i, a in enumerate(sys.argv[1:]):
        if a == '--years' and i + 1 < len(sys.argv[1:]):
            years = sys.argv[i + 2]
            if '-' in years:
                y1, y2 = years.split('-')
                start_date = f'{y1}-01-01'
                end_date = f'{y2}-12-31'

    print("BestDateWeather — fetch_climate.py")
    print(f"Période : {start_date} → {end_date}")
    print(f"Mode : {'preview' if preview else 'all (écrasement)' if force_all else 'new only' if new_only else 'production'}")

    dests = load_destinations()
    existing = load_existing_climate_slugs()

    if force_all:
        slugs = list(dests.keys())
    elif new_only:
        slugs = [s for s in dests.keys() if s not in existing]
        if not slugs:
            print("\n✅ Toutes les destinations ont déjà des données climatiques.")
            return
        print(f"\n{len(slugs)} destination(s) sans données climatiques.")
    elif args:
        slugs = []
        for a in args:
            a_clean = a.strip()
            if a_clean in dests:
                slugs.append(a_clean)
            else:
                print(f"⚠️  '{a_clean}' inconnu dans destinations.csv — ignoré")
    else:
        print("\nUsage :")
        print("  python3 fetch_climate.py <slug>        # une destination")
        print("  python3 fetch_climate.py --new          # destinations sans données")
        print("  python3 fetch_climate.py --all          # toutes (écrase)")
        print("  python3 fetch_climate.py --preview <slug>  # aperçu sans écriture")
        print("  python3 fetch_climate.py --years 2018-2023 <slug>")
        return

    success = 0
    errors = 0
    for slug in slugs:
        try:
            ok = process_destination(
                slug, dests[slug], start_date, end_date,
                preview_only=preview, force=force_all
            )
            if ok:
                success += 1
            # Rate limiting: 1s between API calls (Open-Meteo free tier)
            if len(slugs) > 1:
                time.sleep(1.0)
        except Exception as e:
            print(f"  ❌ Erreur inattendue pour {slug}: {e}")
            errors += 1

    print(f"\n{'─' * 50}")
    print(f"Terminé : {success} OK / {errors} erreurs / {len(slugs) - success - errors} ignorés")
    if not preview and success > 0:
        print(f"⚠️  Relecture recommandée : vérifiez les classes (rec/mid/avoid) dans climate.csv")
        print(f"    Les classes auto-assignées peuvent être inexactes pour certaines destinations.")


if __name__ == '__main__':
    main()
