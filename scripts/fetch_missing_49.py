#!/usr/bin/env python3
"""Fetch climate data for 49 missing destinations via Open-Meteo archive API."""
import csv, io, json, os, sys, time
import urllib.request

DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEST_CSV   = os.path.join(DIR, 'data', 'destinations.csv')
CLIMATE_CSV = os.path.join(DIR, 'data', 'climate.csv')
PROGRESS   = os.path.join(DIR, 'data', 'fetch_49_progress.json')

MONTHS_FR = ['janvier','fevrier','mars','avril','mai','juin',
             'juillet','aout','septembre','octobre','novembre','decembre']

def fetch_open_meteo(lat, lon, slug):
    url = (
        f"https://archive-api.open-meteo.com/v1/archive"
        f"?latitude={lat}&longitude={lon}"
        f"&start_date=2014-01-01&end_date=2023-12-31"
        f"&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,sunshine_duration"
        f"&timezone=auto"
    )
    try:
        with urllib.request.urlopen(url, timeout=30) as r:
            return json.loads(r.read())
    except Exception as e:
        print(f"  ERROR {slug}: {e}")
        return None

def aggregate(data):
    """Aggregate daily data to monthly P50-style stats."""
    import statistics
    daily = data.get('daily', {})
    dates  = daily.get('time', [])
    tmax_d = daily.get('temperature_2m_max', [])
    tmin_d = daily.get('temperature_2m_min', [])
    prec_d = daily.get('precipitation_sum', [])
    sun_d  = daily.get('sunshine_duration', [])  # seconds

    by_month = {m: {'tmax':[],'tmin':[],'prec':[],'sun':[]} for m in range(1,13)}
    for i, d in enumerate(dates):
        m = int(d[5:7])
        if tmax_d[i] is not None: by_month[m]['tmax'].append(tmax_d[i])
        if tmin_d[i] is not None: by_month[m]['tmin'].append(tmin_d[i])
        if prec_d[i] is not None: by_month[m]['prec'].append(prec_d[i])
        if sun_d[i]  is not None: by_month[m]['sun'].append(sun_d[i]/3600)  # → hours

    rows = []
    for m in range(1,13):
        b = by_month[m]
        tmax = round(statistics.median(b['tmax']), 1) if b['tmax'] else 0
        tmin = round(statistics.median(b['tmin']), 1) if b['tmin'] else 0
        prec_vals = b['prec']
        rain_days = sum(1 for p in prec_vals if p > 1)
        total_days = len(prec_vals)
        rain_pct = round(rain_days / total_days * 100) if total_days else 0
        precip_mm = round(sum(prec_vals) / (total_days / 30) if total_days else 0, 1)
        sun_h = round(sum(b['sun']) / (total_days / 30) if total_days else 0, 1)
        rows.append({
            'tmax': tmax, 'tmin': tmin,
            'rain_pct': rain_pct, 'precip_mm': precip_mm,
            'sun_h': sun_h, 'month': m
        })
    return rows

def main():
    dest_rows = list(csv.DictReader(open(DEST_CSV, encoding='utf-8-sig')))
    climate_rows = list(csv.DictReader(open(CLIMATE_CSV, encoding='utf-8-sig')))
    existing_slugs = {r['slug'] for r in climate_rows}
    fieldnames = list(climate_rows[0].keys())

    missing = [r for r in dest_rows if r['slug_fr'] not in existing_slugs]
    print(f"To fetch: {len(missing)} destinations")

    progress = json.load(open(PROGRESS)) if os.path.exists(PROGRESS) else {'done': []}
    done = set(progress['done'])

    new_rows = []
    for i, dest in enumerate(missing):
        slug = dest['slug_fr']
        if slug in done:
            print(f"  [{i+1}/{len(missing)}] {slug} — already done, skipping")
            continue

        lat, lon = dest['lat'], dest['lon']
        print(f"  [{i+1}/{len(missing)}] Fetching {slug} ({lat}, {lon})...")
        data = fetch_open_meteo(lat, lon, slug)
        if not data:
            print(f"    FAILED — will retry next run")
            time.sleep(2)
            continue

        monthly = aggregate(data)
        for mo in monthly:
            row = {k: '' for k in fieldnames}
            row['slug']       = slug
            row['mois']       = MONTHS_FR[mo['month']-1]
            row['mois_num']   = mo['month']
            row['tmin']       = mo['tmin']
            row['tmax']       = mo['tmax']
            row['rain_pct']   = mo['rain_pct']
            row['precip_mm']  = mo['precip_mm']
            row['sun_h']      = mo['sun_h']
            row['score']      = ''
            row['classe']     = ''
            row['source']     = 'open-meteo-archive'
            row['sea_temp']   = ''
            row['beach_score'] = ''
            new_rows.append(row)

        done.add(slug)
        json.dump({'done': list(done)}, open(PROGRESS, 'w'))
        print(f"    OK — {slug}")
        time.sleep(0.5)

    if new_rows:
        # Append to climate.csv
        buf = io.StringIO()
        w = csv.DictWriter(buf, fieldnames=fieldnames)
        w.writerows(new_rows)
        with open(CLIMATE_CSV, 'a', encoding='utf-8', newline='') as f:
            f.write(buf.getvalue())
        print(f"\nAppended {len(new_rows)} rows ({len(new_rows)//12} destinations) to climate.csv")
    else:
        print("No new rows to append.")

    # Final check
    climate2 = list(csv.DictReader(open(CLIMATE_CSV, encoding='utf-8-sig')))
    covered = {r['slug'] for r in climate2}
    still_missing = [r['slug_fr'] for r in dest_rows if r['slug_fr'] not in covered]
    print(f"Still missing: {len(still_missing)}")
    if still_missing:
        print(f"  {still_missing}")

if __name__ == '__main__':
    main()
