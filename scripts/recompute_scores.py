#!/usr/bin/env python3
"""
Recalcule classe et score de tous les mois de data/climate.csv.

Procédure identique à celle d'août 2026 (ensoleillement) :
classify_effective pour la classe, bornes globales par classe recalculées
sur le CSV, puis compute_scores destination par destination.

    python3 scripts/recompute_scores.py          # contrôle : compare aux scores actuels
    python3 scripts/recompute_scores.py --apply  # écrit climate.csv
    python3 scripts/recompute_scores.py --delta-from ANCIEN.csv --apply
        # n'applique que l'effet des données modifiées (recommandé)
"""
import csv
import os
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
sys.path.insert(0, ROOT)
import scoring  # noqa: E402

PATH = os.path.join(ROOT, 'data', 'climate.csv')


def fnum(v):
    return float(v) if v not in ('', None) else None


def score_all(rows):
    """Classe effective + score (procédure canonique) pour une liste de lignes.

    Retourne {(slug, mois_num): (classe, score_10)}. Les bornes globales sont
    recalculées sur ces lignes (comme scoring._load_global_bounds).
    """
    cls = {}
    for r in rows:
        cls[(r['slug'], r['mois_num'])] = scoring.classify_effective(
            float(r['tmax']), float(r['rain_pct']), float(r['sun_h']),
            fnum(r.get('precip_mm')), fnum(r.get('dew_point_mean')))
    by = {'rec': [], 'mid': [], 'avoid': []}
    for r in rows:
        by[cls[(r['slug'], r['mois_num'])]].append(scoring.raw_score(
            float(r['tmax']), float(r['rain_pct']), float(r['sun_h']), fnum(r.get('precip_mm'))))
    saved = scoring.GLOBAL_RAW_BOUNDS
    scoring.GLOBAL_RAW_BOUNDS = {k: (min(v), max(v)) for k, v in by.items() if v}
    out = {}
    by_slug = {}
    for r in rows:
        by_slug.setdefault(r['slug'], []).append(r)
    for slug, ms in by_slug.items():
        ms = sorted(ms, key=lambda r: int(r['mois_num']))
        months = [{'cls': cls[(r['slug'], r['mois_num'])], 'tmax': float(r['tmax']),
                   'rain_pct': float(r['rain_pct']), 'sun_h': float(r['sun_h']),
                   'precip_mm': fnum(r.get('precip_mm')), 'dew_point': fnum(r.get('dew_point_mean')),
                   'aqi_mean': fnum(r.get('aqi_mean')), 'month': r['mois']} for r in ms]
        for r, s in zip(ms, scoring.compute_scores(months, slug=slug)):
            out[(r['slug'], r['mois_num'])] = (cls[(r['slug'], r['mois_num'])], s['score_10'])
    scoring.GLOBAL_RAW_BOUNDS = saved
    return out


def main_delta(old_path, apply):
    """Applique l'EFFET MARGINAL d'un changement de données sur les scores publiés.

    Les scores actuels ne sont pas reproductibles à l'identique par le code
    (procédure d'août 2026 non archivée). Pour ne changer que ce qui découle
    des nouvelles données : score = ancien + (S(nouveau) - S(ancien)), où S
    est la procédure canonique. Un mois dont les données ne changent pas
    garde exactement son score.
    """
    new_rows = list(csv.DictReader(open(PATH, encoding='utf-8')))
    old_rows = list(csv.DictReader(open(old_path, encoding='utf-8')))
    old_score = {(r['slug'], r['mois_num']): float(r['score']) for r in old_rows}
    s_old, s_new = score_all(old_rows), score_all(new_rows)
    fields = list(new_rows[0].keys())
    deltas = []
    canon = 0
    for r in new_rows:
        k = (r['slug'], r['mois_num'])
        d = s_new[k][1] - s_old[k][1]
        v = round(min(10.0, max(0.0, old_score[k] + d)), 1)
        cls = s_new[k][0]
        # Le score doit rester dans la plage de sa classe (plage « mid » pour
        # une destination tropicale classée « avoid », comme compute_scores) ;
        # sinon on prend le score canonique.
        lo, hi = scoring.SCORE_RANGES['mid' if (cls == 'avoid' and r['slug'] in scoring.TROPICAL_DESTINATIONS) else cls]
        if not (lo - 0.05 <= v <= hi + 0.05):
            v = s_new[k][1]
            canon += 1
        deltas.append(v - old_score[k])
        r['score'] = f'{v}'
        r['classe'] = cls
    n = len(deltas)
    up = sum(1 for d in deltas if d > 0.05)
    down = sum(1 for d in deltas if d < -0.05)
    print(f'{n} mois ; en hausse {up}, en baisse {down}, inchangés {n-up-down} ; '
          f'écart moyen {sum(abs(d) for d in deltas)/n:.2f}, max {max(deltas):+.1f} / {min(deltas):+.1f} ; '
          f'{canon} mois recalés sur le score canonique (hors plage de leur classe)')
    if apply:
        with open(PATH, 'w', encoding='utf-8', newline='') as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            w.writerows(new_rows)
        print('climate.csv écrit')


def main():
    apply = '--apply' in sys.argv
    if '--delta-from' in sys.argv:
        return main_delta(sys.argv[sys.argv.index('--delta-from') + 1], apply)
    rows = list(csv.DictReader(open(PATH, encoding='utf-8')))
    fields = list(rows[0].keys())
    # 1. Classes effectives
    for r in rows:
        r['_classe'] = scoring.classify_effective(float(r['tmax']), float(r['rain_pct']), float(r['sun_h']),
                                                  fnum(r.get('precip_mm')), fnum(r.get('dew_point_mean')))
    # 2. Bornes globales (même calcul que scoring._load_global_bounds)
    by = {'rec': [], 'mid': [], 'avoid': []}
    for r in rows:
        by[r['_classe']].append(scoring.raw_score(float(r['tmax']), float(r['rain_pct']), float(r['sun_h']),
                                                  fnum(r.get('precip_mm'))))
    scoring.GLOBAL_RAW_BOUNDS = {k: (min(v), max(v)) for k, v in by.items() if v}
    # 3. Scores par destination
    by_slug = {}
    for r in rows:
        by_slug.setdefault(r['slug'], []).append(r)
    diffs, changed = [], 0
    for slug, ms in by_slug.items():
        ms.sort(key=lambda r: int(r['mois_num']))
        months = [{'cls': r['_classe'], 'tmax': float(r['tmax']), 'rain_pct': float(r['rain_pct']),
                   'sun_h': float(r['sun_h']), 'precip_mm': fnum(r.get('precip_mm')),
                   'dew_point': fnum(r.get('dew_point_mean')), 'aqi_mean': fnum(r.get('aqi_mean')),
                   'month': r['mois']} for r in ms]
        sc = scoring.compute_scores(months, slug=slug)
        for r, s in zip(ms, sc):
            new = s['score_10']
            old = float(r['score'])
            diffs.append(abs(new - old))
            if r['classe'] != r['_classe'] or abs(new - old) > 1e-9:
                changed += 1
            r['score'] = f'{new}'
            r['classe'] = r['_classe']
    n = len(diffs)
    print(f'{n} mois ; modifiés : {changed} ; écart moyen {sum(diffs)/n:.3f} ; max {max(diffs):.2f}')
    if apply:
        for r in rows:
            r.pop('_classe', None)
        with open(PATH, 'w', encoding='utf-8', newline='') as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            w.writerows(rows)
        print('climate.csv écrit')


if __name__ == '__main__':
    main()
