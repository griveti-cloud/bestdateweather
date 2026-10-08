#!/usr/bin/env python3
"""
Historique quotidien 2016-2025 (ERA5 via Open-Meteo) → statistiques par semaine.

Une semaine « plutôt sèche » compte au plus 2 jours avec au moins 1 mm de pluie.

Plan B, phase 3. Produit data/weekly/{slug_fr}.json pour les destinations
indexées (lib/indexation.py), lu par lib/v6_weekly.py.

Quota Open-Meteo gratuit : 10 000 appels/jour, 5 000/heure, 600/minute, avec
un poids de (jours demandés / 14) par requête. 10 ans de données quotidiennes
= ~261 appels pondérés par destination, donc ~34 destinations par jour.
Le script est REPRENABLE : il saute les destinations déjà traitées, s'arrête
proprement en cas de quota atteint, et sauvegarde après chaque destination.
Il tourne chaque jour via .github/workflows/fetch-weekly-history.yml jusqu'à
couverture complète.

Usage :
    python3 scripts/fetch_weekly_history.py [--budget 9000] [--max-dest N]
    python3 scripts/fetch_weekly_history.py --selftest
"""
import argparse
import csv
import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import date, timedelta

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
sys.path.insert(0, ROOT)

OUT_DIR = os.path.join(ROOT, 'data', 'weekly')
START, END = date(2016, 1, 1), date(2025, 12, 31)
YEARS = list(range(START.year, END.year + 1))
API = 'https://archive-api.open-meteo.com/v1/archive'
WEIGHT = ((END - START).days + 1) / 14.0          # appels pondérés par destination
HOURLY_CAP = 4500                                  # marge sous 5 000/heure
RAIN_CODE = 51                                     # code WMO >= 51 = précipitation (règle de l'application, par jour)
RAIN_MM = 1.0                                      # jour de pluie = >= 1 mm (même règle que climate.csv)
DRY_WEEK_MAX = 2                                   # semaine « plutôt sèche » = au plus 2 jours de pluie


def doy_nonleap(d: date):
    """Jour de l'année (0-364) dans un calendrier non bissextile ; None pour le 29 février."""
    if d.month == 2 and d.day == 29:
        return None
    return (date(2015, d.month, d.day) - date(2015, 1, 1)).days


def week_blocks():
    """52 blocs : 51 de 7 jours puis un dernier de 8 jours (24-31 décembre)."""
    blocks = []
    for w in range(52):
        a = 7 * w
        b = a + 6 if w < 51 else 364
        blocks.append((a, b))
    return blocks


def mmdd(doy: int) -> str:
    d = date(2015, 1, 1) + timedelta(days=doy)
    return f'{d.month:02d}-{d.day:02d}'


def compute(times, tmax, codes, precip):
    """Agrège les séries quotidiennes en statistiques hebdomadaires et journalières.

    Hebdomadaire : jour de pluie = précipitations >= 1 mm (définition OMM, la
    même que le « % de jours de pluie » des pages). Par jour : mode du code
    météo sur ±3 jours, comme le verdict de l'application.
    """
    by = {}  # (year, doy) -> (tmax, code, precip)
    for t, x, c, pr in zip(times, tmax, codes, precip):
        d = date.fromisoformat(t)
        k = doy_nonleap(d)
        if k is None:
            continue
        by[(d.year, k)] = (x, c, pr)

    weeks = []
    for a, b in week_blocks():
        rain_days, dry_weeks, tsum, tn, ny = [], 0, 0.0, 0, 0
        for y in YEARS:
            vals = [by.get((y, k)) for k in range(a, b + 1)]
            vals = [v for v in vals if v is not None]
            if len(vals) < (b - a + 1) - 1:   # au plus 1 jour manquant toléré
                continue
            ny += 1
            r = sum(1 for _, _c, pr in vals if pr is not None and pr >= RAIN_MM)
            rain_days.append(r * 7.0 / len(vals))
            if r <= DRY_WEEK_MAX:
                dry_weeks += 1
            for x, _c, _p in vals:
                if x is not None:
                    tsum += x
                    tn += 1
        if ny < 8:
            return None
        weeks.append({
            'from': mmdd(a), 'to': mmdd(b),
            'rain_days': round(sum(rain_days) / len(rain_days), 1),
            'dry_weeks': round(dry_weeks * 10 / ny),      # ramené à « sur 10 »
            'tmax': round(tsum / tn, 1) if tn else None,
        })

    # Par jour (même règle que l'application : mode pondéré du code météo
    # sur ±3 jours, poids 3 pour le jour exact) : années sur 10 sans pluie.
    dry_by_day, sunny_by_day = [], []
    for k in range(365):
        dry = sunny = n = 0
        for y in YEARS:
            cnt = {}
            for off in range(-3, 4):
                kk = k + off
                if kk < 0 or kk > 364:
                    continue
                v = by.get((y, kk))
                if v is None or v[1] is None:
                    continue
                cnt[v[1]] = cnt.get(v[1], 0) + (3 if off == 0 else 1)
            if not cnt:
                continue
            mode = max(cnt.items(), key=lambda kv: (kv[1], -kv[0]))[0]
            n += 1
            dry += mode < RAIN_CODE
            sunny += mode <= 2
        dry_by_day.append(round(dry * 10 / n) if n else None)
        sunny_by_day.append(round(sunny * 10 / n) if n else None)
    return {'weeks': weeks, 'dry_years_by_day': dry_by_day, 'sunny_years_by_day': sunny_by_day}


class QuotaReached(Exception):
    pass


def fetch(lat, lon):
    url = (f'{API}?latitude={lat}&longitude={lon}&start_date={START}&end_date={END}'
           f'&daily=temperature_2m_max,precipitation_sum,weather_code&timezone=auto')
    last = None
    for attempt in range(3):
        try:
            with urllib.request.urlopen(url, timeout=120) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            body = e.read().decode('utf-8', 'replace')
            if 'limit' in body.lower():
                raise QuotaReached(body[:200])
            last = f'HTTP {e.code} {body[:200]}'
        except Exception as e:  # réseau
            last = str(e)
        time.sleep(10 * (attempt + 1))
    raise RuntimeError(last)


def targets():
    from lib.indexation import indexed_destinations, load_policy
    pol = load_policy()
    order = [s for s in pol.get('destinations_historique_gsc', [])] + \
            [s for s in pol.get('destinations_forte_demande', [])]
    allowed = set(indexed_destinations())
    seen, out = set(), []
    for s in order:
        if s in allowed and s not in seen:
            seen.add(s)
            out.append(s)
    return out


def selftest():
    # Série synthétique : pluie le lundi uniquement → 1 jour de pluie par semaine
    times, tmax, codes, precip = [], [], [], []
    d = START
    while d <= END:
        times.append(d.isoformat())
        tmax.append(20.0)
        rainy = d.weekday() in (0, 3)          # 2 jours de pluie par semaine
        codes.append(61 if rainy else 1)
        precip.append(5.0 if rainy else (0.4 if d.weekday() == 5 else 0.0))  # 0,4 mm ne compte pas
        d += timedelta(days=1)
    res = compute(times, tmax, codes, precip)
    assert len(res['weeks']) == 52
    w = res['weeks'][10]
    assert 1.9 <= w['rain_days'] <= 2.1, w
    assert w['dry_weeks'] == 10, w            # 2 jours de pluie = « plutôt sèche »
    assert res['weeks'][-1]['from'] == '12-24' and res['weeks'][-1]['to'] == '12-31'
    assert len(res['dry_years_by_day']) == 365
    assert all(0 <= v <= 10 for v in res['sunny_years_by_day'] if v is not None)
    assert all(0 <= v <= 10 for v in res['dry_years_by_day'] if v is not None)
    print('selftest OK')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--budget', type=float, default=9000, help='appels pondérés max pour ce lancement')
    ap.add_argument('--max-dest', type=int, default=0)
    ap.add_argument('--selftest', action='store_true')
    a = ap.parse_args()
    if a.selftest:
        selftest()
        return
    os.makedirs(OUT_DIR, exist_ok=True)
    rows = {r['slug_fr']: r for r in csv.DictReader(open(os.path.join(ROOT, 'data', 'destinations.csv'), encoding='utf-8-sig'))}
    todo = [s for s in targets() if not os.path.exists(os.path.join(OUT_DIR, f'{s}.json'))]
    print(f'{len(todo)} destination(s) à traiter ; poids {WEIGHT:.0f} appels chacune ; budget {a.budget:.0f}')
    spent, done, hour_start, hour_spent = 0.0, 0, time.time(), 0.0
    for s in todo:
        if a.max_dest and done >= a.max_dest:
            break
        if spent + WEIGHT > a.budget:
            print('Budget du jour atteint, reprise au prochain lancement.')
            break
        if hour_spent + WEIGHT > HOURLY_CAP:
            wait = 3600 - (time.time() - hour_start) + 30
            if wait > 0:
                print(f'Plafond horaire : pause {wait:.0f} s')
                time.sleep(wait)
            hour_start, hour_spent = time.time(), 0.0
        r = rows.get(s)
        if not r:
            continue
        try:
            data = fetch(r['lat'], r['lon'])
        except QuotaReached as e:
            print(f'Quota Open-Meteo atteint ({e}). Arrêt propre.')
            break
        except Exception as e:
            print(f'⚠️ {s} : échec ({e}), destination sautée')
            spent += WEIGHT
            hour_spent += WEIGHT
            continue
        spent += WEIGHT
        hour_spent += WEIGHT
        dly = data.get('daily') or {}
        res = compute(dly.get('time', []), dly.get('temperature_2m_max', []),
                      dly.get('weather_code', []), dly.get('precipitation_sum', []))
        if not res:
            print(f'⚠️ {s} : données incomplètes, ignorée')
            continue
        out = {
            'slug': s, 'lat': float(r['lat']), 'lon': float(r['lon']),
            'source': 'ERA5 (ECMWF) via Open-Meteo archive API, daily temperature_2m_max + precipitation_sum + weather_code',
            'years': [START.year, END.year],
            'rain_rule': 'semaines : jour de pluie = precipitation_sum >= 1 mm, semaine plutôt sèche = au plus 2 jours de pluie ; jours : mode du weather_code sur ±3 j, sec si < 51',
            'generated': date.today().isoformat(),
            **res,
        }
        with open(os.path.join(OUT_DIR, f'{s}.json'), 'w', encoding='utf-8') as f:
            json.dump(out, f, ensure_ascii=False, separators=(',', ':'))
        done += 1
        print(f'✓ {s} ({done})')
        time.sleep(2)
    total = len(targets())
    have = sum(1 for s in targets() if os.path.exists(os.path.join(OUT_DIR, f'{s}.json')))
    print(f'Couverture : {have}/{total} destinations')


if __name__ == '__main__':
    main()
