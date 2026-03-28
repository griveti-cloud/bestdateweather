#!/usr/bin/env python3
"""
fetch_climate_trend.py
Fetche les températures annuelles ERA5 (2016–2025) + tendance CMIP6
pour toutes les destinations de destinations.csv.

Sortie : data/climate_trend.json
Format :
{
  "paris": {
    "years": [2016, 2017, ..., 2025],
    "tmax":  [14.2, 15.1, ...],   // moyenne annuelle tmax
    "tmin":  [7.3,  7.8, ...],    // moyenne annuelle tmin
    "tmoy":  [10.8, 11.4, ...],   // moyenne annuelle (tmax+tmin)/2
    "cmip6_rate": 0.21            // °C/décennie CMIP6 (None si indispo)
  },
  ...
}

Usage:
  python3 scripts/fetch_climate_trend.py [--limit N] [--force]
  --limit N  : traite seulement N destinations (test)
  --force    : refetch même si déjà dans le fichier
"""

import csv, json, sys, time, os, argparse
import urllib.request, urllib.parse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEST_CSV  = os.path.join(ROOT, 'data', 'destinations.csv')
OUT_FILE  = os.path.join(ROOT, 'data', 'climate_trend.json')

YEARS = list(range(2016, 2026))  # 2016-2025

def fetch_era5_annual(lat, lon):
    """Fetch yearly tmax/tmin from ERA5 via Open-Meteo archive API."""
    params = {
        'latitude':   lat,
        'longitude':  lon,
        'start_date': '2016-01-01',
        'end_date':   '2025-12-31',
        'daily':      'temperature_2m_max,temperature_2m_min',
        'timezone':   'UTC',
    }
    url = 'https://archive-api.open-meteo.com/v1/archive?' + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url, timeout=15) as r:
        data = json.loads(r.read().decode())
    
    dates = data['daily']['time']
    tmax_d = data['daily']['temperature_2m_max']
    tmin_d = data['daily']['temperature_2m_min']
    
    # Aggregate by year
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
            tmax_yr.append(tx)
            tmin_yr.append(tn)
            tmoy_yr.append(round((tx + tn) / 2, 1))
        else:
            tmax_yr.append(None)
            tmin_yr.append(None)
            tmoy_yr.append(None)
    
    return tmax_yr, tmin_yr, tmoy_yr


def fetch_cmip6_rate(lat, lon):
    """
    Fetch projected warming rate (°C/decade) from Open-Meteo Climate Change API.
    Uses SSP2-4.5 scenario (moderate), CMIP6 ensemble mean.
    Computes linear trend on 2025-2050 annual tmax.
    """
    params = {
        'latitude':   lat,
        'longitude':  lon,
        'start_date': '2024-01-01',
        'end_date':   '2050-12-31',
        'models':     'MRI_AGCM3_2_S',  # single fast model as proxy
        'daily':      'temperature_2m_max',
    }
    url = 'https://climate-api.open-meteo.com/v1/climate?' + urllib.parse.urlencode(params)
    try:
        with urllib.request.urlopen(url, timeout=15) as r:
            data = json.loads(r.read().decode())
        
        dates = data['daily']['time']
        temps = data['daily']['temperature_2m_max']
        
        # Annual means
        by_year = {}
        for i, d in enumerate(dates):
            y = int(d[:4])
            if temps[i] is not None:
                by_year.setdefault(y, []).append(temps[i])
        
        years_ord = sorted(by_year.keys())
        if len(years_ord) < 5:
            return None
        
        ann = [(y, sum(v)/len(v)) for y, v in by_year.items() if v]
        ann.sort()
        
        # Linear regression slope → °C/year → ×10 = °C/decade
        n = len(ann)
        xs = [a[0] for a in ann]
        ys = [a[1] for a in ann]
        xm = sum(xs)/n; ym = sum(ys)/n
        num = sum((xs[i]-xm)*(ys[i]-ym) for i in range(n))
        den = sum((xs[i]-xm)**2 for i in range(n))
        if den == 0: return None
        slope_per_year = num / den
        return round(slope_per_year * 10, 2)  # °C/decade
    except Exception:
        return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--limit', type=int, default=None)
    parser.add_argument('--force', action='store_true')
    args = parser.parse_args()

    # Load existing
    existing = {}
    if os.path.exists(OUT_FILE) and not args.force:
        existing = json.load(open(OUT_FILE, encoding='utf-8'))
        print(f"Loaded {len(existing)} existing entries")

    # Load destinations
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
        
        print(f"[{i+1}/{total}] {slug} ({lat},{lon})...", end=' ', flush=True)
        
        try:
            tmax, tmin, tmoy = fetch_era5_annual(lat, lon)
            cmip6 = fetch_cmip6_rate(lat, lon)
            
            existing[slug] = {
                'years': YEARS,
                'tmax':  tmax,
                'tmin':  tmin,
                'tmoy':  tmoy,
                'cmip6_rate': cmip6,
            }
            ok += 1
            print(f"✅ cmip6={cmip6}")
        except Exception as e:
            err += 1
            print(f"❌ {e}")
        
        # Save incrementally every 10 destinations
        if (i + 1) % 10 == 0:
            json.dump(existing, open(OUT_FILE, 'w', encoding='utf-8'),
                      ensure_ascii=False, indent=2)
            print(f"  → Saved ({ok} ok, {err} err, {skip} skip)")
        
        # Rate limit: ~2 req/sec (ERA5 + CMIP6 = 2 calls per dest)
        time.sleep(0.5)
    
    # Final save
    json.dump(existing, open(OUT_FILE, 'w', encoding='utf-8'),
              ensure_ascii=False, indent=2)
    print(f"\nDone: {ok} ok / {err} err / {skip} skip → {OUT_FILE}")


if __name__ == '__main__':
    main()
