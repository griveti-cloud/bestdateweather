#!/usr/bin/env python3
"""
Calibration des jours de pluie (rain_pct) sur des normales de stations.

Problème (octobre 2026) : ERA5 compte trop de jours avec au moins 1 mm dans
les climats à averses brèves (Bali juillet 59 % contre 11 % mesurés à
Denpasar ; Aruba avril 21 % contre 5 % ; Barcelone juillet 17 % contre 7 %).

Méthode (même logique que l'ensoleillement en août 2026) :
1. Normales publiées (data/station_normals.json, unité >= 1 mm uniquement)
   → valeur « observed » quand elle existe.
2. Ailleurs, modèle ajusté sur ces stations, validé PAR DESTINATION
   (validation croisée sans fuite entre les mois d'une même ville).

Usage :
    python3 scripts/calibrate_rain_days.py            # rapport seul
    python3 scripts/calibrate_rain_days.py --apply    # écrit climate.csv + data/rain_calibration.json
"""
import csv
import json
import math
import os
import sys

import numpy as np

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
DIM = [31, 28.25, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
MOIS = ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 'Juillet', 'Août',
        'Septembre', 'Octobre', 'Novembre', 'Décembre']


def logit(p):
    p = min(max(p, 0.005), 0.995)
    return math.log(p / (1 - p))


def inv(z):
    return 1 / (1 + math.exp(-z))


def load():
    dests = {r['slug_fr']: r for r in csv.DictReader(open(os.path.join(ROOT, 'data', 'destinations.csv'), encoding='utf-8-sig'))}
    rows = list(csv.DictReader(open(os.path.join(ROOT, 'data', 'climate.csv'), encoding='utf-8')))
    st = json.load(open(os.path.join(ROOT, 'data', 'station_normals.json'), encoding='utf-8'))
    return dests, rows, st


def era5_value(r):
    """rain_pct ERA5 d'origine (avant calibration éventuelle)."""
    v = r.get('rain_pct_era5') or r['rain_pct']
    return float(v)


def features(r, d):
    x = era5_value(r) / 100
    mm = float(r['precip_mm'] or 0)
    lat = abs(float(d['lat']))
    trop = 1.0 if str(d.get('tropical', '')).strip().lower() in ('true', '1') else 0.0
    return [1.0, logit(x), math.log(mm + 0.1), trop, lat / 90.0, logit(x) * trop]


MODELS = {
    'M1 logit(ERA5)': [0, 1],
    'M2 + intensité (mm/j)': [0, 1, 2],
    'M3 + tropical + latitude': [0, 1, 2, 3, 4],
    'M4 + interaction tropicale': [0, 1, 2, 3, 4, 5],
}


def dataset(dests, rows, st):
    data = []
    for r in rows:
        s = r['slug']
        n = st.get(s) or {}
        if 'rain_days' not in n or s not in dests:
            continue
        mi = int(r['mois_num']) - 1
        y = n['rain_days'][mi] / DIM[mi]
        if not (0 <= y <= 1):
            continue
        data.append((s, features(r, dests[s]), y, era5_value(r) / 100))
    return data


def fit(X, y):
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    return beta


def cv(data, cols, k=10):
    slugs = sorted({d[0] for d in data})
    rng = np.random.default_rng(42)
    rng.shuffle(slugs)
    fold = {s: i % k for i, s in enumerate(slugs)}
    errs = []
    for f in range(k):
        tr = [d for d in data if fold[d[0]] != f]
        te = [d for d in data if fold[d[0]] == f]
        X = np.array([[d[1][c] for c in cols] for d in tr])
        Y = np.array([logit(d[2]) for d in tr])
        b = fit(X, Y)
        for d in te:
            p = inv(float(np.dot(b, [d[1][c] for c in cols])))
            errs.append(abs(p - d[2]) * 100)
    return float(np.mean(errs)), float(np.percentile(errs, 90))


def main():
    apply = '--apply' in sys.argv
    dests, rows, st = load()
    data = dataset(dests, rows, st)
    n_dest = len({d[0] for d in data})
    print(f'Stations utilisables (>= 1 mm, <= 120 km) : {n_dest} destinations, {len(data)} mois')
    raw_err = [abs(d[3] - d[2]) * 100 for d in data]
    bias = float(np.mean([(d[3] - d[2]) * 100 for d in data]))
    print(f'ERA5 brut : erreur moyenne {np.mean(raw_err):.1f} pts, 90e centile {np.percentile(raw_err, 90):.1f} pts, biais moyen {bias:+.1f} pts')
    trop = [d for d in data if d[1][3] == 1.0]
    if trop:
        print(f'  dont tropicales ({len({d[0] for d in trop})} dest.) : erreur {np.mean([abs(d[3]-d[2])*100 for d in trop]):.1f} pts, biais {np.mean([(d[3]-d[2])*100 for d in trop]):+.1f} pts')
    results = {}
    for name, cols in MODELS.items():
        mae, p90 = cv(data, cols)
        results[name] = (mae, p90, cols)
        print(f'{name:30s} validation croisée par ville : erreur {mae:.1f} pts, 90e centile {p90:.1f} pts')
    # Parcimonie : le modèle le plus simple à moins de 0,1 point du meilleur
    best_mae = min(v[0] for v in results.values())
    best = next(k for k in MODELS if results[k][0] <= best_mae + 0.1)
    cols = results[best][2]
    X = np.array([[d[1][c] for c in cols] for d in data])
    Y = np.array([logit(d[2]) for d in data])
    beta = fit(X, Y)
    print(f'Modèle retenu : {best} ; coefficients {np.round(beta, 3).tolist()}')
    # Contrôle de monotonie : la prédiction doit croître avec ERA5
    if beta[1] <= 0:
        print('❌ Modèle non monotone en ERA5 : abandon')
        return
    # Exemples
    for s, m in [('bali', 7), ('aruba', 4), ('barcelone', 7), ('paris', 7), ('agadir', 4), ('bangkok', 1), ('phuket', 2), ('maldives', 2)]:
        r = next((x for x in rows if x['slug'] == s and int(x['mois_num']) == m), None)
        if not r or s not in dests:
            continue
        p = inv(float(np.dot(beta, [features(r, dests[s])[c] for c in cols]))) * 100
        obs = (st.get(s) or {}).get('rain_days')
        o = f'{obs[m-1]/DIM[m-1]*100:.0f} %' if obs else 'n.d.'
        print(f'  {s:10s} {MOIS[m-1]:9s} ERA5 {era5_value(r):3.0f} %  modèle {p:3.0f} %  station {o}')
    if not apply:
        return

    # ── Application ──
    fields = list(rows[0].keys())
    for c in ('rain_pct_era5', 'rain_source'):
        if c not in fields:
            fields.append(c)
    n_obs = n_cal = 0
    for r in rows:
        s = r['slug']
        if not r.get('rain_pct_era5'):
            r['rain_pct_era5'] = r['rain_pct']
        mi = int(r['mois_num']) - 1
        n = st.get(s) or {}
        if 'rain_days' in n:
            v = n['rain_days'][mi] / DIM[mi] * 100
            r['rain_pct'] = str(int(round(min(100, max(0, v)))))
            r['rain_source'] = 'observed'
            n_obs += 1
        elif s in dests:
            p = inv(float(np.dot(beta, [features(r, dests[s])[c] for c in cols]))) * 100
            r['rain_pct'] = str(int(round(p)))
            r['rain_source'] = 'calibrated'
            n_cal += 1
    with open(os.path.join(ROOT, 'data', 'climate.csv'), 'w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    json.dump({'model': best, 'columns': cols, 'coefficients': [float(b) for b in beta],
               'features': ['const', 'logit(era5)', 'log(mm+0.1)', 'tropical', 'abs_lat/90', 'logit(era5)*tropical'],
               'cv_mae_pts': results[best][0], 'era5_mae_pts': float(np.mean(raw_err)),
               'n_destinations_reference': n_dest, 'n_mois_reference': len(data)},
              open(os.path.join(ROOT, 'data', 'rain_calibration.json'), 'w'), indent=1)
    print(f'climate.csv mis à jour : {n_obs} mois « observed », {n_cal} mois « calibrated »')


if __name__ == '__main__':
    main()
