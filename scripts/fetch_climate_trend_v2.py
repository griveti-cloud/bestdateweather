#!/usr/bin/env python3
"""
fetch_climate_trend_v2.py - avec retry backoff sur 429, sleep 2s entre requêtes
"""
import csv, json, sys, time, os, argparse
import urllib.request, urllib.parse, urllib.error

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEST_CSV = os.path.join(ROOT, 'data', 'destinations.csv')
OUT_FILE = os.path.join(ROOT, 'data', 'climate_trend.json')
YEARS = list(range(2016, 2026))
SLEEP_BETWEEN = 2.0  # secondes entre chaque destination


def fetch_url(url, retries=5):
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(url, timeout=20) as r:
                return json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            if e.code == 429:
                wait = 60 * (2 ** attempt)
                print(f"\n  ⏳ 429, attente {wait}s...", end=' ', flush=True)
                time.sleep(wait)
            else:
                raise
    raise Exception("Max retries exceeded")


def fetch_era5_annual(lat, lon):
    params = {
        'latitude': lat, 'longitude': lon,
        'start_date': '2016-01-01', 'end_date': '2025-12-31',
        'daily': 'temperature_2m_max,temperature_2m_min',
        'timezone': 'UTC',
    }
    url = 'https://archive-api.open-meteo.com/v1/archive?' + urllib.parse.urlencode(params)
    data = fetch_url(url)
    dates = data['daily']['time']
    tmax_d = data['daily']['temperature_2m_max']
    tmin_d = data['daily']['temperature_2m_min']
    by_year = {}
    for i, d in enumerate(dates):
        y = int(d[:4])
        if y not in by_year:
            by_year[y] = {'tmax': [], 'tmin': []}
        if tmax_d[i] is not None:
            by_year[y]['tmax'].append(tmax_d[i])
        if tmin_d[i] is not None:
            by_year[y]['tmin'].append(tmin_d[i])
    tmax_yr, tmin_yr, tmoy_yr = [], [], []
    for y in YEARS:
        if y in by_year and by_year[y]['tmax']:
            tx = round(sum(by_year[y]['tmax']) / len(by_year[y]['tmax']), 1)
            tn = round(sum(by_year[y]['tmin']) / len(by_year[y]['tmin']), 1)
            tmax_yr.append(tx); tmin_yr.append(tn)
            tmoy_yr.append(round((tx + tn) / 2, 1))
        else:
            tmax_yr.append(None); tmin_yr.append(None); tmoy_yr.append(None)
    return tmax_yr, tmin_yr, tmoy_yr


def fetch_cmip6_rate(lat, lon):
    try:
        params = {
            'latitude': lat, 'longitude': lon,
            'models': 'MRI_AGCM3_2_S',
            'daily': 'temperature_2m_max',
            'start_date': '2015-01-01', 'end_date': '2050-12-31',
        }
        url = 'https://climate-api.open-meteo.com/v1/climate?' + urllib.parse.urlencode(params)
        data = fetch_url(url)
        daily = data.get('daily', {})
        dates = daily.get('time', [])
        temps = daily.get('temperature_2m_max', [])
        by_year = {}
        for i, d in enumerate(dates):
            y = int(d[:4])
            if temps[i] is not None:
                by_year.setdefault(y, []).append(temps[i])
        ann = [(y, sum(v)/len(v)) for y, v in by_year.items() if v]
        if len(ann) < 5:
            return None
        ann.sort()
        xs = [a[0] for a in ann]; ys = [a[1] for a in ann]
        xm = sum(xs)/len(xs); ym = sum(ys)/len(ys)
        num = sum((xs[i]-xm)*(ys[i]-ym) for i in range(len(xs)))
        den = sum((xs[i]-xm)**2 for i in range(len(xs)))
        if den == 0: return None
        return round(num/den * 10, 2)
    except Exception:
        return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--limit', type=int, default=None)
    parser.add_argument('--force', action='store_true')
    args = parser.parse_args()

    existing = {}
    if os.path.exists(OUT_FILE) and not args.force:
        existing = json.load(open(OUT_FILE, encoding='utf-8'))
        print(f"Chargé {len(existing)} entrées existantes")

    dests = list(csv.DictReader(open(DEST_CSV, encoding='utf-8-sig')))
    if args.limit:
        dests = dests[:args.limit]

    total = len(dests)
    ok = err = skip = 0

    for i, d in enumerate(dests):
        slug = d['slug_fr']
        lat, lon = d['lat'].strip(), d['lon'].strip()

        if slug in existing and not args.force:
            skip += 1
            continue

        print(f"[{i+1}/{total}] {slug}...", end=' ', flush=True)

        try:
            tmax, tmin, tmoy = fetch_era5_annual(lat, lon)
            cmip6 = fetch_cmip6_rate(lat, lon)
            existing[slug] = {
                'years': YEARS, 'tmax': tmax, 'tmin': tmin,
                'tmoy': tmoy, 'cmip6_rate': cmip6,
            }
            ok += 1
            print(f"✅ cmip6={cmip6}")
        except Exception as e:
            err += 1
            print(f"❌ {e}")

        if (i + 1) % 10 == 0:
            json.dump(existing, open(OUT_FILE, 'w', encoding='utf-8'),
                      ensure_ascii=False, indent=2)
            print(f"  → Sauvegardé ({ok} ok, {err} err, {skip} skip)")

        time.sleep(SLEEP_BETWEEN)

    json.dump(existing, open(OUT_FILE, 'w', encoding='utf-8'),
              ensure_ascii=False, indent=2)
    print(f"\nFini: {ok} ok / {err} err / {skip} skip → {OUT_FILE}")


if __name__ == '__main__':
    main()
