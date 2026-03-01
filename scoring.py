"""
BESTDATEWEATHER — Algorithme de scoring climatique
===================================================
Version : 1.0 — 2026-02-25
Auteur  : BestDateWeather EI micro

SOURCE DE VÉRITÉ pour tous les scores mensuels des fiches destination.

Ce fichier est importé par :
  - regenerate_scores.py   → recalcule et réécrit les scores des pages existantes
  - generate_destination.py → génère une nouvelle fiche avec scores cohérents

PRINCIPE : scoring ancré sur classes
─────────────────────────────────────
Chaque mois reçoit d'abord une classe éditoriale : rec | mid | avoid
(classement manuel, reflète la réalité locale au-delà des seules données numériques)

Le score numérique est ensuite calculé PAR CLASSE :
  avoid  →  0.5 – 3.9 / 10
  mid    →  4.0 – 6.9 / 10
  rec    →  7.0 – 10.0 / 10

Dans chaque classe, les mois sont rangés par raw_score (temp + pluie + soleil)
et la plage est distribuée par normalisation min-max.
→ Le meilleur mois d'une classe atteint la borne haute,
  le moins bon atteint la borne basse.
→ Si la classe ne contient qu'un seul mois, il prend le milieu de la plage.

EXCEPTIONS TROPICALES / MOUSSON
─────────────────────────────────
Pour certaines destinations, les mois "avoid" restent voyageables malgré
la pluie intense (averses courtes, infrastructure adaptée, température stable).
Correction : la plage avoid est remontée sur la plage mid (4.0 – 6.9).
Les classes mid et rec ne sont pas affectées.

Voir TROPICAL_DESTINATIONS ci-dessous.

DONNÉES D'ENTRÉE (colonnes du tableau climatique des fiches)
─────────────────────────────────────────────────────────────
  tmax      : température maximale moyenne du mois (°C)       — colonne "T° max"
  rain_pct  : pourcentage de jours avec précipitations (%)    — colonne "Pluie %"
  sun_h     : ensoleillement moyen journalier (heures/jour)   — colonne "Soleil h/j"

TRAÇABILITÉ DANS LES PAGES HTML
─────────────────────────────────
Chaque <tr> du tableau climatique porte les attributs data-* :
  data-tmax="26" data-rain="29" data-sun="11.2"
permettant de recalculer n'importe quel score directement depuis le DOM.
"""

# ── PLAGES DE SCORE PAR CLASSE ─────────────────────────────────────────────
SCORE_RANGES = {
    'avoid': (0.5, 3.9),
    'mid':   (4.0, 6.9),
    'rec':   (7.0, 10.0),
}

# ── CORRECTION TROPICALE ───────────────────────────────────────────────────
# Pour les destinations marquées tropical=True dans destinations.csv,
# les mois "avoid" (mousson) restent voyageables.
# La plage avoid est remontée à la plage mid : (0.5–3.9) → (4.0–6.9)
# Justification : pluies tropicales intenses mais courtes, pas de vrai obstacle
# au voyage (≠ hiver nordique ou saison des typhons en côte exposée).

def _load_tropical_destinations():
    """Charge les slugs FR+EN des destinations tropicales depuis destinations.csv."""
    import csv, os
    csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'destinations.csv')
    slugs = set()
    try:
        with open(csv_path, encoding='utf-8-sig') as f:
            for r in csv.DictReader(f):
                if r.get('tropical', '').strip().lower() == 'true':
                    slugs.add(r['slug_fr'].strip())
                    slugs.add(r['slug_en'].strip())
    except FileNotFoundError:
        # Fallback minimal si le CSV n'est pas trouvé (ex: tests unitaires)
        slugs = {'bangkok', 'phuket', 'hoi-an', 'siem-reap', 'singapour',
                 'singapore', 'zanzibar', 'goa'}
    return slugs

TROPICAL_DESTINATIONS = _load_tropical_destinations()


# ── FONCTIONS DE SCORE ─────────────────────────────────────────────────────

def t_ideal(tmax: float) -> float:
    """
    Confort thermique normalisé [0, 1] en fonction de tmax (°C).

    Plage confortable :  22 – 28°C  →  score 0.8 – 1.0
    Frais :               14 – 22°C  →  score 0.3 – 0.8
    Froid :                5 – 14°C  →  score 0.0 – 0.3
    Très froid :          ≤ 5°C       →  0.0
    Chaud :               28 – 35°C  →  1.0 → 0.6 (pénalité progressive)
    Très chaud :          > 35°C      →  ≤ 0.6 (pénalité forte)
    """
    if tmax <= 5:   return 0.0
    if tmax <= 14:  return (tmax - 5) / 9 * 0.3
    if tmax <= 22:  return 0.3 + (tmax - 14) / 8 * 0.5
    if tmax <= 28:  return 0.8 + (tmax - 22) / 6 * 0.2
    if tmax <= 35:  return 1.0 - (tmax - 28) / 7 * 0.4
    return max(0.0, 0.6 - (tmax - 35) / 10 * 0.3)


def raw_score(tmax: float, rain_pct: float, sun_h: float) -> float:
    """
    Score brut [0, 1] AVANT ancrage sur la plage de classe.

    Poids :
      40%  température  → t_ideal(tmax)
      35%  pluie        → 1 - rain_pct / 100   (0% pluie = 1.0, 100% pluie = 0.0)
      25%  soleil       → sun_h / 15            (15h/j = maximum théorique = 1.0)

    Ce score ne sert qu'à ordonner les mois à l'intérieur d'une classe.
    Le score final /10 est déterminé par la position dans la plage de la classe.
    """
    return (0.40 * t_ideal(tmax)
          + 0.35 * max(0.0, 1.0 - rain_pct / 100.0)
          + 0.25 * min(1.0, sun_h / 15.0))


def _norm(values: list) -> list:
    """Normalisation min-max → [0, 1]. Retourne [0.5, ...] si tous égaux."""
    mn, mx = min(values), max(values)
    if mx == mn:
        return [0.5] * len(values)
    return [(v - mn) / (mx - mn) for v in values]


def compute_scores(months: list, slug: str = '') -> list:
    """
    Calcule les scores /100 pour une liste de 12 mois.

    Paramètre months : liste de dicts avec au minimum :
      {
        'cls'      : 'rec' | 'mid' | 'avoid',   # classe éditoriale
        'tmax'     : float,                       # °C
        'rain_pct' : float,                       # %
        'sun_h'    : float,                       # h/jour
        'month'    : str,                         # label (optionnel, pour sortie)
      }

    Paramètre slug : identifiant slug de la destination
      → si présent dans TROPICAL_DESTINATIONS, correction tropicale appliquée

    Retourne une liste de dicts :
      [{'month': ..., 'score_100': int, 'score_10': float}, ...]

    Algorithme :
      1. Séparer les mois par classe
      2. Calculer raw_score pour chaque mois
      3. Normaliser min-max à l'intérieur de la classe
      4. Mapper la position normalisée sur la plage [lo, hi] de la classe
         (correction tropicale : avoid → plage mid pour TROPICAL_DESTINATIONS)
      5. score_10 = arrondi à 1 décimale, score_100 = arrondi entier × 10
    """
    is_tropical = slug in TROPICAL_DESTINATIONS

    # Plages effectives selon type de destination
    def get_range(cls: str) -> tuple:
        if is_tropical and cls == 'avoid':
            return SCORE_RANGES['mid']   # correction tropicale
        return SCORE_RANGES[cls]

    scores = [None] * len(months)

    for cls in ('avoid', 'mid', 'rec'):
        idxs = [i for i, m in enumerate(months) if m['cls'] == cls]
        if not idxs:
            continue
        lo, hi = get_range(cls)
        raws = [raw_score(months[i]['tmax'], months[i]['rain_pct'], months[i]['sun_h'])
                for i in idxs]
        norms = _norm(raws)
        for j, i in enumerate(idxs):
            val_10 = round(lo + norms[j] * (hi - lo), 1)
            scores[i] = {
                'month'     : months[i].get('month', ''),
                'score_10'  : val_10,
                'score_100' : round(val_10 * 10),
            }

    return scores


# ── SCORING MONTAGNE / SKI ─────────────────────────────────────────────────
#
# Pour les destinations marquées mountain=True dans destinations.csv.
# Le score ski s'affiche en seconde colonne à côté du score standard.
# La classe de la ligne (couleur) prend le meilleur des deux scores.
#
# Principe : le froid est un atout, la neige un bonus, le soleil reste positif.
# Score direct 0-10 sans passer par les classes rec/mid/avoid.

def t_ideal_winter(tmax: float) -> float:
    """
    Confort ski normalisé [0, 1] en fonction de tmax (°C).

    Sweet spot :    -5 à  5°C  →  0.9 – 1.0  (neige garantie, froid supportable)
    Froid correct : -15 à -5°C →  0.3 – 0.9  (très froid mais skiable)
    Trop froid :    ≤ -15°C     →  0.3  (conditions extrêmes)
    Doux :           5 à 15°C  →  0.9 – 0.2  (neige fondante → pas de ski)
    Chaud :         > 15°C      →  ≤ 0.2  (pas de neige)
    """
    if tmax <= -15:  return 0.3
    if tmax <= -5:   return 0.3 + (tmax + 15) / 10 * 0.6
    if tmax <= 5:    return 0.9 + (5 - abs(tmax)) / 5 * 0.1
    if tmax <= 15:   return 0.9 - (tmax - 5) / 10 * 0.7
    return max(0.0, 0.2 - (tmax - 15) / 10 * 0.2)


def raw_score_winter(tmax: float, rain_pct: float, sun_h: float) -> float:
    """
    Score brut [0, 1] pour activités ski/montagne hiver.

    Poids :
      50%  température  → t_ideal_winter(tmax)
      25%  précipitations → neutre si froid (neige), pénalisé si chaud (pluie)
      25%  soleil       → sun_h / 12  (12h = max hivernal réaliste)
    """
    t = t_ideal_winter(tmax)

    # Quand il fait ≤ 2°C, les précipitations tombent en neige → neutre/positif
    if tmax <= 2:
        precip_score = 0.7
    elif tmax <= 8:
        precip_score = max(0.2, 1.0 - rain_pct / 100.0)
    else:
        precip_score = max(0.0, 1.0 - rain_pct / 100.0)

    sun = min(1.0, sun_h / 12.0)
    return 0.50 * t + 0.25 * precip_score + 0.25 * sun


def compute_ski_score(tmax: float, rain_pct: float, sun_h: float) -> float:
    """Score ski direct /10 (pas de classes, mapping linéaire)."""
    return round(raw_score_winter(tmax, rain_pct, sun_h) * 10, 1)


def ski_class(score_10: float) -> str:
    """Classe éditoriale dérivée du score ski."""
    if score_10 >= 7.0: return 'rec'
    if score_10 >= 4.0: return 'mid'
    return 'avoid'


def best_class(summer_cls: str, ski_score_10: float) -> str:
    """Pour mountain destinations : prend la meilleure classe entre été et ski."""
    rank = {'avoid': 0, 'mid': 1, 'rec': 2}
    ski_cls = ski_class(ski_score_10)
    return summer_cls if rank.get(summer_cls, 0) >= rank.get(ski_cls, 0) else ski_cls


# ── UTILITAIRE DE VÉRIFICATION ─────────────────────────────────────────────

def verify_destination(slug: str, rows_with_class: list, cur_scores_100: list) -> dict:
    """
    Compare les scores actuels d'une fiche avec ceux calculés par l'algo.

    Paramètre rows_with_class : [(cls, month, tmin, tmax, rain_pct, sun_h), ...]
    Paramètre cur_scores_100  : [int, ...] — scores actuels ×100

    Retourne :
      {'rmse': float, 'max_diff': int, 'diffs': [int, ...], 'ok': bool}
    """
    import math
    months = [{'cls': r[0], 'month': r[1], 'tmax': r[3], 'rain_pct': r[4], 'sun_h': r[5]}
              for r in rows_with_class]
    calc = compute_scores(months, slug)
    diffs = [calc[i]['score_100'] - cur_scores_100[i] for i in range(len(months))]
    rmse = math.sqrt(sum(d * d for d in diffs) / len(diffs))
    return {
        'rmse'    : round(rmse, 2),
        'max_diff': max(abs(d) for d in diffs),
        'diffs'   : diffs,
        'ok'      : rmse < 1.0,
    }


# ── POINT D'ENTRÉE CLI (vérification rapide) ───────────────────────────────

if __name__ == '__main__':
    import sys, re, glob, math

    def get_data_from_fiche(path):
        html = open(path).read()
        tables = list(re.finditer(r'<table[^>]*climate-table[^>]*>.*?</table>', html, re.DOTALL))
        if not tables:
            return None, None
        t = max(tables,
                key=lambda t: len(re.findall(r'<tr class="(?:rec|mid|avoid)">', t.group(0)))).group(0)
        rows = re.findall(
            r'<tr[^>]+class="(rec|mid|avoid)"[^>]*>'
            r'<td>([^<]+)</td>'           # mois
            r'<td>(-?\d+)°C</td>'         # tmin
            r'<td>(-?\d+)°C</td>'         # tmax
            r'<td>(\d+)%</td>'            # rain_pct
            r'<td>([\d.]+)[^<]*</td>'     # precip mm
            r'<td>([\d.]+)h?</td>'        # sun_h
            r'<td>([\d.]+)/10</td>',      # score_10 actuel
            t
        )
        if len(rows) < 12:
            return None, None
        rows_p = [(cls, m, int(a), int(b), int(c), float(e))
                  for cls, m, a, b, c, d, e, sc in rows]
        cur = [round(float(sc) * 10) for cls, m, a, b, c, d, e, sc in rows]
        return rows_p, cur

    target = sys.argv[1] if len(sys.argv) > 1 else '*'
    pattern = f'meilleure-periode-{target}.html'
    files = sorted(glob.glob(pattern))

    if not files:
        print(f'Aucun fichier trouvé : {pattern}')
        sys.exit(1)

    total_ok = total_fail = 0
    for f in files:
        slug = re.search(r'meilleure-periode-(.+)\.html', f).group(1)
        rows, cur = get_data_from_fiche(f)
        if rows is None:
            print(f'[PARSE ERROR] {slug}')
            total_fail += 1
            continue
        result = verify_destination(slug, rows, cur)
        status = 'OK ' if result['ok'] else 'ERR'
        print(f'[{status}] {slug:30} RMSE={result["rmse"]:5.2f}  max_diff={result["max_diff"]}')
        if not result['ok']:
            total_fail += 1
        else:
            total_ok += 1

    print(f'\nTotal : {total_ok} OK / {total_fail} erreurs')
