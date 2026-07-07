#!/usr/bin/env python3
"""
refetch_precip.py — Re-fetch CHIRURGICAL de precip_mm + rain_pct pour les
destinations aux données cassées (valeurs 100-400x trop élevées héritées
d'une version boguée du fetch), avec recalcul score + classe EFFECTIVE.

1. Re-fetch precip_mm (mm/jour moyen) + rain_pct depuis ERA5 (2015-2024)
2. Recalcule classe via scoring.classify_effective (inclut déclassements
   chaleur/humidité — fix incohérence classe/score type Marrakech)
3. Recalcule score via compute_scores
4. PRÉSERVE les colonnes annexes (sea_temp, beach_score, dew_point_mean,
   uv_index, wave_height_mean, swell_period_mean, aqi_mean)

Usage:
    python3 scripts/refetch_precip.py            # liste /tmp/broken_precip.json
    python3 scripts/refetch_precip.py paris lyon # destinations spécifiques

Sauvegarde incrémentale tous les 5 (protection timeout).
"""
import sys
import os
import csv
import json
import time
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scoring import classify_effective, compute_scores

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLIMATE_CSV = os.path.join(ROOT, 'data', 'climate.csv')
DEST_CSV = os.path.join(ROOT, 'data', 'destinations.csv')

RAIN_THRESHOLD_MM = 1.0  # WMO : jour pluvieux = precip >= 1mm
MONTHS_FR = ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin',
             'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']


def _f(v, default=None):
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


def fetch_precip(lat, lon, max_retries=6):
    url = (f'https://archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}'
           f'&start_date=2015-01-01&end_date=2024-12-31'
           f'&daily=precipitation_sum&timezone=auto')
    for attempt in range(max_retries):
        try:
            data = json.load(urllib.request.urlopen(url, timeout=30))
            times = data['daily']['time']
            precip = data['daily']['precipitation_sum']
            by_month = {m: {'vals': [], 'rain_days': 0} for m in range(1, 13)}
            for i, dt in enumerate(times):
                p = precip[i]
                if p is None:
                    continue
                m = int(dt[5:7])
                by_month[m]['vals'].append(p)
                if p >= RAIN_THRESHOLD_MM:
                    by_month[m]['rain_days'] += 1
            out = {}
            for m in range(1, 13):
                d = by_month[m]
                if not d['vals']:
                    out[m] = {'precip_mm': None, 'rain_pct': None}
                else:
                    out[m] = {
                        'precip_mm': round(sum(d['vals']) / len(d['vals']), 1),
                        'rain_pct': round(d['rain_days'] / len(d['vals']) * 100),
                    }
            return out
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
            else:
                print(f"    échec API: {e}")
                return None


def recompute_dest(by_key, slug):
    """Recalcule classe effective + score pour les 12 mois d'une destination."""
    months_input = []
    for mi in range(1, 13):
        row = by_key.get((slug, mi))
        if not row:
            return
        tmax = _f(row['tmax'], 0)
        rain = _f(row['rain_pct'], 0)
        sun = _f(row['sun_h'], 0)
        mm = _f(row['precip_mm'])
        dew = _f(row.get('dew_point_mean'))
        cls = classify_effective(tmax, rain, sun, mm, dew)
        row['classe'] = cls
        months_input.append({'cls': cls, 'tmax': tmax, 'rain_pct': rain,
                             'sun_h': sun, 'month': MONTHS_FR[mi - 1],
                             'precip_mm': mm, 'dew_point': dew})
    scores = compute_scores(months_input, slug)
    for idx, mi in enumerate(range(1, 13)):
        row = by_key.get((slug, mi))
        if row and idx < len(scores):
            row['score'] = str(scores[idx]['score_10'])


def save(fieldnames, all_rows):
    with open(CLIMATE_CSV, 'w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(all_rows)


def main():
    dests = {d['slug_fr']: d for d in csv.DictReader(open(DEST_CSV, encoding='utf-8-sig'))}
    with open(CLIMATE_CSV, encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        all_rows = list(reader)
    by_key = {(r['slug'], int(r['mois_num'])): r for r in all_rows}

    targets = sys.argv[1:] if len(sys.argv) > 1 else json.load(open('/tmp/broken_precip.json'))
    print(f"Re-fetch precip: {len(targets)} destinations")

    done, failed = 0, []
    for slug in targets:
        if slug not in dests:
            failed.append(slug)
            continue
        d = dests[slug]
        new_p = fetch_precip(d['lat'], d['lon'])
        if new_p is None:
            failed.append(slug)
            continue
        for mi in range(1, 13):
            row = by_key.get((slug, mi))
            if not row:
                continue
            np = new_p.get(mi, {})
            if np.get('precip_mm') is not None:
                row['precip_mm'] = str(np['precip_mm'])
            if np.get('rain_pct') is not None:
                row['rain_pct'] = str(np['rain_pct'])
        recompute_dest(by_key, slug)
        done += 1
        if done % 10 == 0:
            print(f"  [{done}/{len(targets)}] {slug}")
        if done % 5 == 0:
            save(fieldnames, all_rows)
        time.sleep(0.3)

    save(fieldnames, all_rows)
    print(f"\nOK: {done} re-fetchées" + (f" | {len(failed)} échecs: {failed}" if failed else ""))


if __name__ == '__main__':
    main()
