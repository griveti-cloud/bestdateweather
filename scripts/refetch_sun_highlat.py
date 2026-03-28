#!/usr/bin/env python3
"""
Refetch sun_h for high-latitude oceanic destinations using direct_radiation > 120 W/m².

ERA5 sunshine_duration counts diffuse radiation at high latitudes, heavily
overestimating sunshine at 50-70°N in summer. direct_radiation > 120 W/m² matches
WMO "bright sunshine" definition and aligns with station measurements.

Affected destinations: ~12 high-lat, non-tropical coastal/temperate locations.
Updates climate.csv sun_h + score + classe in place.
"""

import csv
import json
import time
import urllib.request
from collections import defaultdict
from pathlib import Path
import sys
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))
from scoring import raw_score, GLOBAL_RAW_BOUNDS, SCORE_RANGES, SCORE_POWER

def compute_score_and_class(tmax: float, rain_pct: float, sun_h: float, precip_mm: float):
    """Compute normalized score + class using global bounds (mirrors compute_scores logic)."""
    raw = raw_score(tmax, rain_pct, sun_h, precip_mm)
    raw_rec = GLOBAL_RAW_BOUNDS.get('rec',   (0.5, 1.0))
    raw_mid = GLOBAL_RAW_BOUNDS.get('mid',   (0.2, 0.7))
    cls = 'rec' if raw >= raw_rec[0] else ('mid' if raw >= raw_mid[0] else 'avoid')
    glob_mn, glob_mx = GLOBAL_RAW_BOUNDS.get(cls, (0.0, 1.0))
    lo, hi = SCORE_RANGES[cls]
    norm = max(0.0, min(1.0, (raw - glob_mn) / (glob_mx - glob_mn))) if glob_mx > glob_mn else 0.5
    score = round(lo + (norm ** SCORE_POWER) * (hi - lo), 1)
    return score, cls

CLIMATE_CSV = ROOT / "data" / "climate.csv"

# Years to average (same as main fetch_climate.py)
YEARS = list(range(2014, 2024))  # 10 years

# Destinations to refetch
# lat > 50°N, non-tropical, coastal/temperate (NOT high-altitude ski)
TARGETS = {
    'wild-atlantic-way':(52.97, -9.43),
    'lake-district':    (54.46, -3.08),
    'edimbourg':        (55.95, -3.19),
    'acores':           (37.75,-25.67),
    'reykjavik':        (64.15,-21.94),
    'oslo':             (59.91, 10.75),
    'stockholm':        (59.33, 18.07),
    'helsinki':         (60.17, 24.94),
    'dublin':           (53.35, -6.26),
}

MONTHS_FR = ['Janvier','Février','Mars','Avril','Mai','Juin',
             'Juillet','Août','Septembre','Octobre','Novembre','Décembre']


def fetch_direct_sun(lat: float, lon: float, year: int) -> dict[int, float]:
    """
    Fetch hourly direct_radiation for a year, return dict {month_num: mean_sun_h_per_day}.
    Sunshine hours = hours where direct_radiation > 120 W/m² (WMO bright sunshine).
    """
    url = (
        f"https://archive-api.open-meteo.com/v1/archive?"
        f"latitude={lat}&longitude={lon}"
        f"&start_date={year}-01-01&end_date={year}-12-31"
        f"&hourly=direct_radiation"
        f"&timezone=UTC"
    )
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    # Retry up to 3 times with increasing timeout
    data = None
    for attempt, timeout in enumerate([25, 45, 90], 1):
        try:
            data = json.loads(urllib.request.urlopen(req, timeout=timeout).read())
            break
        except Exception as e:
            if attempt == 3:
                raise
            print(f"(retry {attempt}) ", end='', flush=True)
            time.sleep(5)

    hourly = data['hourly']
    times = hourly['time']
    direct = hourly['direct_radiation']

    # Aggregate: sum hours > 120 W/m² per day
    daily_sun = defaultdict(float)
    day_month = {}
    for t, d in zip(times, direct):
        day = t[:10]
        month = int(t[5:7])
        day_month[day] = month
        if (d or 0) > 120:
            daily_sun[day] += 1.0

    # Average per month
    month_days = defaultdict(list)
    for day, m in day_month.items():
        month_days[m].append(daily_sun[day])

    return {m: round(sum(v)/len(v), 2) for m, v in month_days.items()}


def compute_10yr_mean(lat: float, lon: float) -> dict[int, float]:
    """Average sun_h per month over YEARS."""
    all_years = defaultdict(list)
    for year in YEARS:
        print(f"    Fetching {year}...", end=' ', flush=True)
        try:
            monthly = fetch_direct_sun(lat, lon, year)
            for m, v in monthly.items():
                all_years[m].append(v)
            print(f"OK ({sum(monthly.values())/12:.1f}h avg)")
        except Exception as e:
            print(f"ERROR: {e}")
        time.sleep(0.4)

    return {m: round(sum(v)/len(v), 1) for m, v in all_years.items() if v}


def main():
    # Load current climate.csv
    rows = []
    with open(CLIMATE_CSV, newline='') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        for row in reader:
            rows.append(row)

    # Index by (slug, mois_num)
    idx = {(r['slug'], int(r['mois_num'])): i for i, r in enumerate(rows)}

    print(f"=== refetch_sun_highlat.py ===")
    print(f"Targets: {len(TARGETS)} destinations, {len(YEARS)} years each\n")

    updated_slugs = []
    for slug, (lat, lon) in TARGETS.items():
        print(f"\n[{slug}] lat={lat}, lon={lon}")

        # Check slug exists in climate.csv
        if (slug, 1) not in idx:
            print(f"  ⚠️  Not found in climate.csv — skip")
            continue

        # Show current values
        current = [(rows[idx[(slug, m)]]['sun_h'], rows[idx[(slug, m)]]['rain_pct'])
                   for m in range(1, 13) if (slug, m) in idx]
        print(f"  Current sun_h: {[c[0] for c in current]}")

        # Fetch new values
        new_sun = compute_10yr_mean(lat, lon)

        if len(new_sun) < 12:
            print(f"  ⚠️  Only {len(new_sun)} months fetched — skip")
            continue

        print(f"  New sun_h:     {[new_sun.get(m, '?') for m in range(1, 13)]}")

        # Update rows
        for m in range(1, 13):
            key = (slug, m)
            if key not in idx:
                continue
            row = rows[idx[key]]
            old_sun = float(row['sun_h'])
            new_s = new_sun.get(m, old_sun)
            new_score, new_cls = compute_score_and_class(
                float(row['tmax']),
                float(row['rain_pct']),
                new_s,
                float(row['precip_mm']) if row.get('precip_mm') else None
            )
            row['sun_h'] = str(new_s)
            row['score'] = str(new_score)
            row['classe'] = new_cls

        updated_slugs.append(slug)
        print(f"  ✅ Updated {slug}")

        # Save after each destination
        with open(CLIMATE_CSV, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

        time.sleep(1.0)

    print(f"\n=== Done — {len(updated_slugs)} destinations updated ===")
    print("Updated:", updated_slugs)
    print("\nNext: run generate_pages.py + check_deploy.py + git push")


if __name__ == '__main__':
    main()
