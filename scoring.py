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

    Plage optimale :     22 – 28°C  →  0.8 – 1.0
    Frais :               14 – 22°C  →  0.3 – 0.8
    Froid :                5 – 14°C  →  0.0 – 0.3
    Très froid :          ≤ 5°C       →  0.0
    Chaud :               28 – 31°C  →  1.0 → 0.90  (légèrement chaud, tolérable)
    Très chaud :          31 – 34°C  →  0.90 → 0.60  (inconfort croissant)
    Canicule :            34 – 37°C  →  0.60 → 0.25  (pénalisé, inconfortable)
    Canicule sévère :     37 – 40°C  →  0.25 → 0.05  (dangereux)
    Extrême :             > 40°C     →  0.0
    """
    if tmax <= 5:   return 0.0
    if tmax <= 14:  return (tmax - 5) / 9 * 0.3
    if tmax <= 22:  return 0.3 + (tmax - 14) / 8 * 0.5
    if tmax <= 28:  return 0.8 + (tmax - 22) / 6 * 0.2
    if tmax <= 31:  return 1.0 - (tmax - 28) / 3 * 0.10   # 1.0 -> 0.90
    if tmax <= 34:  return 0.90 - (tmax - 31) / 3 * 0.30  # 0.90 -> 0.60
    if tmax <= 37:  return 0.60 - (tmax - 34) / 3 * 0.35  # 0.60 -> 0.25
    if tmax <= 40:  return 0.25 - (tmax - 37) / 3 * 0.20  # 0.25 -> 0.05
    return 0.0


def effective_rain_pct(rain_pct: float, precip_mm: float = None) -> float:
    """
    Ajuste le rain_pct en fonction de l'intensité réelle (mm/jour moyen).

    Bidirectionnel :
    - Bruine (< 2mm/j)  : réduit le rain_pct effectif (pluie peu gênante)
    - Modéré (2-5mm/j)  : légère réduction
    - Normal (5-10mm/j) : pas d'ajustement
    - Fort (10-20mm/j)  : augmente le rain_pct effectif (orages, perturbant)
    - Extrême (> 20mm/j): forte augmentation (mousson, déluge)

    Si precip_mm est None, retourne rain_pct inchangé (rétro-compatible).
    """
    if precip_mm is None:
        return rain_pct
    if precip_mm < 2:
        factor = 0.60 + (precip_mm / 2) * 0.25       # 0.60 -> 0.85
    elif precip_mm < 5:
        factor = 0.85 + ((precip_mm - 2) / 3) * 0.15  # 0.85 -> 1.00
    elif precip_mm < 10:
        factor = 1.0                                    # neutre
    elif precip_mm < 20:
        factor = 1.0 + ((precip_mm - 10) / 10) * 0.15  # 1.00 -> 1.15
    else:
        factor = min(1.25, 1.15 + ((precip_mm - 20) / 20) * 0.10)  # 1.15 -> 1.25 cap
    return min(100.0, rain_pct * factor)


def dew_point_penalty(tmax: float, dew_point: float) -> float:
    """
    Pénalité humidité [0, 0.20] basée sur le point de rosée moyen.

    Le point de rosée est le meilleur indicateur du ressenti humide :
      < 10°C  → air très sec, pas de pénalité
      10–16°C → légèrement humide, confort OK
      16–18°C → seuil de gêne (début de sudation visible)
      18–21°C → inconfort notable (la plupart des gens transpirent)
      21–24°C → oppressant (voyageur moyen très gêné)
      > 24°C  → dangereux combiné à forte chaleur

    La pénalité ne s'applique QUE si tmax > 26°C (chaleur activant
    l'inconfort thermique). En dessous, humidité = non problématique.
    """
    if tmax < 26 or dew_point is None:
        return 0.0
    if dew_point < 16:
        return 0.0
    # Pénalité progressive : 0 à 16°C → 0.20 à 26°C+
    # Modulée par la chaleur : plus il fait chaud, plus c'est pénalisé
    heat_factor = min(1.0, (tmax - 26) / 12)  # 0 à 26°C → 1 à 38°C
    dew_factor  = min(1.0, (dew_point - 16) / 10)  # 0 à 16°C → 1 à 26°C
    return round(0.20 * heat_factor * dew_factor, 3)


def aqi_penalty(aqi_mean: float) -> float:
    """
    Pénalité qualité de l'air [0.0, 0.08] sur le score /10 (post-processing).

    Seuil : AQI European > 60 (Moderate/Poor).
    Maximum à AQI = 120+ (Very Poor / Extremely Poor).

    Application : soustraite directement du score /10 final (pas du raw_score),
    pour rendre l'impact transparent et auditable.

    Cas typiques :
      Delhi janvier    AQI=138 → pénalité 0.080 → -0.8 pts /10
      Pékin décembre   AQI=129 → pénalité 0.080 → -0.8 pts /10
      Dubaï juin       AQI= 89 → pénalité 0.039 → -0.4 pts /10
      Milan décembre   AQI= 77 → pénalité 0.023 → -0.2 pts /10
      Paris juillet    AQI= 25 → pénalité 0.000 → inchangé
    """
    if aqi_mean is None or aqi_mean <= 60:
        return 0.0
    factor = min(1.0, (aqi_mean - 60) / 60)  # linéaire 0 à 60 → 1 à 120+
    return round(0.08 * factor, 3)


def rh_from_dew_tmax(dew_point: float, tmax: float) -> float:
    """
    Approximation de l'humidité relative (%) depuis dew point et tmax.
    Formule de Magnus : RH ≈ 100 × es(dew) / es(tmax)
    """
    import math
    if dew_point is None or tmax is None:
        return None
    es_dew  = math.exp(17.27 * dew_point / (dew_point + 237.3))
    es_tmax = math.exp(17.27 * tmax       / (tmax       + 237.3))
    if es_tmax == 0:
        return None
    return min(100.0, max(0.0, 100.0 * es_dew / es_tmax))


def dry_climate_penalty(tmax: float, dew_point: float) -> float:
    """
    Pénalité sécheresse [0, 0.10] pour les climats très secs à température élevée.

    Basée sur l'humidité relative calculée depuis dew point + tmax.

    Justification : air très sec (HR < 25%) provoque déshydratation invisible,
    irritation des muqueuses, écart de ressenti froid/chaud extrême (nuits très
    froides / journées brûlantes). Le TCI de Mieczkowski pénalise l'air très sec
    via le tableau de Terjung (stress hygrothermique par aridité).

    S'applique seulement si tmax > 25°C (la sécheresse n'est gênante qu'avec la
    chaleur — en hiver l'air sec peut même être agréable).

    Seuils :
      RH > 30%  → pas de pénalité
      RH 20-30% → pénalité légère (0 → 0.05)
      RH < 20%  → pénalité forte (0.05 → 0.10)
    """
    if tmax is None or dew_point is None or tmax < 25:
        return 0.0
    rh = rh_from_dew_tmax(dew_point, tmax)
    if rh is None or rh >= 30:
        return 0.0
    if rh >= 20:
        # 0.0 à RH=30 → 0.05 à RH=20
        return round(0.05 * (30 - rh) / 10, 3)
    # 0.05 à RH=20 → 0.10 à RH=0
    return round(0.05 + 0.05 * (20 - rh) / 20, 3)

def raw_score(tmax: float, rain_pct: float, sun_h: float,
              precip_mm: float = None, dew_point: float = None) -> float:
    """
    Score brut [0, 1] AVANT ancrage sur la plage de classe.

    Poids de base :
      40%  temperature  -> t_ideal(tmax)
      35%  pluie        -> 1 - effective_rain_pct / 100
      25%  soleil       -> sun_h / 15  (15h/j = maximum theorique = 1.0)

    Pénalité humidité soustraite après pondération (max -0.20 pts bruts)
    uniquement quand tmax > 26°C ET dew_point > 16°C.
    """
    eff_rain = effective_rain_pct(rain_pct, precip_mm)
    base = (0.40 * t_ideal(tmax)
          + 0.35 * max(0.0, 1.0 - eff_rain / 100.0)
          + 0.25 * min(1.0, sun_h / 15.0))
    penalty = dew_point_penalty(tmax, dew_point)
    penalty += dry_climate_penalty(tmax, dew_point)
    return max(0.0, base - penalty)



def _norm(values: list) -> list:
    """Normalisation min-max → [0, 1]. Retourne [0.5, ...] si tous égaux."""
    mn, mx = min(values), max(values)
    if mx == mn:
        return [0.5] * len(values)
    return [(v - mn) / (mx - mn) for v in values]


# ── NORMALISATION GLOBALE ──────────────────────────────────────────────────
#
# Au lieu de normaliser par destination (→ best mois = 10.0 pour TOUTES les
# destinations), on normalise sur l'ensemble des ~4500 mois rec / ~1300 mid /
# ~350 avoid de toutes les destinations.
#
# Avantage : les classements mensuels ("où partir en mai") ont des scores
# différenciés. Paris juin ≠ Lisbonne juillet.
#
# Power curve (SCORE_POWER) : étire les différences dans le haut de l'échelle.
# p=1 → linéaire, p=2 → quadratique (meilleure discrimination top destinations).
#
# Les bornes sont recalculées depuis climate.csv à chaque import.
# Si climate.csv n'existe pas (tests unitaires), fallback sur bornes par défaut.

SCORE_POWER = 2.0   # exposant de la courbe de puissance

def _load_global_bounds():
    """Calcule min/max raw_score par classe effective depuis climate.csv."""
    import csv, os
    csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'climate.csv')
    bounds = {}
    try:
        by_class = {'rec': [], 'mid': [], 'avoid': []}
        with open(csv_path, encoding='utf-8-sig') as f:
            for r in csv.DictReader(f):
                cls = r['classe']
                mm = float(r['precip_mm']) if r.get('precip_mm', '') not in ('', None) else None
                raw = raw_score(float(r['tmax']), float(r['rain_pct']), float(r['sun_h']), mm)
                if cls in by_class:
                    by_class[cls].append(raw)
        for cls, raws in by_class.items():
            if raws:
                bounds[cls] = (min(raws), max(raws))
    except FileNotFoundError:
        pass
    # Fallback si fichier absent ou classe vide
    bounds.setdefault('rec',   (0.40, 0.97))
    bounds.setdefault('mid',   (0.30, 0.70))
    bounds.setdefault('avoid', (0.13, 0.57))
    return bounds

GLOBAL_RAW_BOUNDS = _load_global_bounds()


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
      1. Séparer les mois par classe (avec déclassement chaleur extrême)
      2. Calculer raw_score pour chaque mois
      3. Normaliser sur les bornes GLOBALES de la classe (toutes destinations)
      4. Appliquer courbe de puissance (SCORE_POWER) pour étirer le haut
      5. Mapper sur la plage [lo, hi] de la classe
      6. score_10 = arrondi à 1 décimale, score_100 = arrondi entier × 10
    """
    is_tropical = slug in TROPICAL_DESTINATIONS

    # ── Déclassement chaleur + humidité ──────────────────────────────────
    # Un mois ne peut pas être "recommandé" si temp ou humidité excessive.
    # Chaleur : ≥38°C → avoid, ≥34°C → mid max
    # Humidité : tmax ≥ 30°C + dew_point ≥ 16°C → mid max (ressenti oppressant)
    HEAT_CAP_AVOID = 38  # °C — canicule sévère, stress thermique dangereux
    HEAT_CAP_MID   = 34  # °C — inconfortable pour la majorité des voyageurs
    DEW_CAP_TMAX   = 30  # °C — seuil temp pour activer cap humidité
    DEW_CAP_DEW    = 16  # °C — point de rosée = début gêne avec chaleur

    effective_months = []
    for m in months:
        em = dict(m)  # copie pour ne pas muter l'original
        tmax = em['tmax']
        cls = em['cls']
        dew = em.get('dew_point')
        if tmax >= HEAT_CAP_AVOID and cls != 'avoid':
            em['cls'] = 'avoid'
        elif tmax >= HEAT_CAP_MID and cls == 'rec':
            em['cls'] = 'mid'
        elif tmax >= DEW_CAP_TMAX and dew is not None and dew >= DEW_CAP_DEW and cls == 'rec':
            em['cls'] = 'mid'
        elif tmax >= 26 and dew is not None and dew >= 22 and cls == 'rec':
            em['cls'] = 'mid'  # chaleur humide tropicale (dew ≥ 22°C + tmax ≥ 26°C)
        effective_months.append(em)

    # Plages effectives selon type de destination
    def get_range(cls: str) -> tuple:
        if is_tropical and cls == 'avoid':
            return SCORE_RANGES['mid']   # correction tropicale
        return SCORE_RANGES[cls]

    scores = [None] * len(effective_months)

    for cls in ('avoid', 'mid', 'rec'):
        idxs = [i for i, m in enumerate(effective_months) if m['cls'] == cls]
        if not idxs:
            continue
        lo, hi = get_range(cls)
        glob_mn, glob_mx = GLOBAL_RAW_BOUNDS.get(cls, (0.0, 1.0))
        raws = [raw_score(effective_months[i]['tmax'], effective_months[i]['rain_pct'], effective_months[i]['sun_h'],
                         effective_months[i].get('precip_mm'), effective_months[i].get('dew_point'))
                for i in idxs]
        for j, i in enumerate(idxs):
            # Normalisation globale : position relative dans l'ensemble de la classe
            if glob_mx > glob_mn:
                norm = max(0.0, min(1.0, (raws[j] - glob_mn) / (glob_mx - glob_mn)))
            else:
                norm = 0.5
            # Courbe de puissance : étire les différences en haut de l'échelle
            stretched = norm ** SCORE_POWER
            val_10_raw = lo + stretched * (hi - lo)
            # Malus AQI (post-processing, transparent et auditable)
            _aqi = effective_months[i].get('aqi_mean')
            _aqi_pen = aqi_penalty(float(_aqi) if _aqi is not None else None)
            val_10 = round(max(0.0, val_10_raw - _aqi_pen * 10), 1)
            scores[i] = {
                'month'     : effective_months[i].get('month', ''),
                'score_10'  : val_10,
                'score_100' : round(val_10 * 10),
            }

    return scores


# ── SCORING PLAGE / BEACH ──────────────────────────────────────────────────
#
# Score dédié plage : combine température air, température mer, pluie, soleil.
# Uniquement pour les destinations côtières (sea_temp disponible).
# Échelle : 0 – 10, normalisation globale comme le score principal.

def effective_classe(tmax: float, classe: str, dew_point: float = None) -> str:
    """Applique le déclassement chaleur + humidité (même logique que compute_scores).
    tmax >= 38°C -> 'avoid'  |  tmax >= 34°C + classe=='rec' -> 'mid'
    tmax >= 30°C + dew_point >= 16°C + classe=='rec' -> 'mid'  (cap humidité)
    """
    if tmax >= 38 and classe != 'avoid':
        return 'avoid'
    if tmax >= 34 and classe == 'rec':
        return 'mid'
    if tmax >= 30 and dew_point is not None and dew_point >= 16 and classe == 'rec':
        return 'mid'
    if tmax >= 26 and dew_point is not None and dew_point >= 22 and classe == 'rec':
        return 'mid'  # chaleur humide tropicale
    return classe


def t_beach(tmax: float) -> float:
    """Confort thermique plage [0, 1]. Seuil abaissé à 16°C, pic à 28-32°C."""
    if tmax <= 16:  return 0.0
    if tmax <= 22:  return (tmax - 16) / 6 * 0.45
    if tmax <= 30:  return 0.45 + (tmax - 22) / 8 * 0.55
    if tmax <= 36:  return 1.0 - (tmax - 30) / 6 * 0.35
    if tmax <= 42:  return 0.65 - (tmax - 36) / 6 * 0.35
    return 0.0

def t_sea(sea_temp: float) -> float:
    """Score température mer [0, 1]. Plus généreux à 18-24°C (baignade possible)."""
    if sea_temp < 14:   return 0.0
    if sea_temp <= 18:  return (sea_temp - 14) / 4 * 0.25
    if sea_temp <= 22:  return 0.25 + (sea_temp - 18) / 4 * 0.30
    if sea_temp <= 26:  return 0.55 + (sea_temp - 22) / 4 * 0.35
    if sea_temp <= 30:  return 0.90 + (sea_temp - 26) / 4 * 0.10
    return max(0.5, 1.0 - (sea_temp - 30) / 5 * 0.5)

def t_wave(wave_h: float) -> float:
    """Score conditions de mer [0, 1] selon hauteur de houle (m).
    < 0.5m : parfait (lagon, eau calme)
    0.5-1.0m : très bon (légères vagues, baignade aisée)
    1.0-1.5m : bon (vagues modérées, baignade possible)
    1.5-2.0m : moyen (mer formée, baignade difficile)
    > 2.0m : mauvais (mer agitée, dangereux)
    """
    if wave_h <= 0.5:  return 1.0
    if wave_h <= 1.0:  return 1.0 - (wave_h - 0.5) / 0.5 * 0.15
    if wave_h <= 1.5:  return 0.85 - (wave_h - 1.0) / 0.5 * 0.25
    if wave_h <= 2.0:  return 0.60 - (wave_h - 1.5) / 0.5 * 0.30
    return max(0.0, 0.30 - (wave_h - 2.0) / 2.0 * 0.30)


def raw_beach_score(tmax: float, rain_pct: float, sun_h: float, sea_temp: float,
                    wave_h: float = None) -> float:
    """
    Score brut plage [0, 1].

    Sans vagues (wave_h=None) :
      30%  température air  → t_beach(tmax)
      30%  température mer  → t_sea(sea_temp)
      20%  pluie            → 1 - rain_pct / 100
      20%  soleil           → sun_h / 15

    Avec vagues (wave_h fourni) :
      25%  température air
      25%  température mer
      20%  conditions vagues → t_wave(wave_h)
      15%  pluie
      15%  soleil
    """
    rain_s = max(0.0, 1.0 - rain_pct / 100.0)
    sun_s  = min(1.0, sun_h / 15.0)
    if wave_h is not None:
        return (0.25 * t_beach(tmax)
              + 0.25 * t_sea(sea_temp)
              + 0.20 * t_wave(wave_h)
              + 0.15 * rain_s
              + 0.15 * sun_s)
    return (0.30 * t_beach(tmax)
          + 0.30 * t_sea(sea_temp)
          + 0.20 * rain_s
          + 0.20 * sun_s)


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
    tmax doit être la T° **sur les pistes** (pas en vallée).
    Utiliser apply_lapse_rate() pour convertir tmax_vallée en tmax_piste.

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


# Lapse rate standard atmosphère : environ -6.5°C par 1000 m
# Source : OACI atmosphère standard
LAPSE_RATE_C_PER_M = 6.5 / 1000.0

# Altitude moyenne du domaine skiable = 60% entre village et sommet
# Représente le niveau moyen où on skie (pas tout en haut, pas tout en bas)
SKI_DOMAIN_AVG_RATIO = 0.60


def apply_lapse_rate(tmax_vallee: float, alt_village: float, alt_ski_max: float) -> float:
    """
    Convertit la température en vallée vers la température moyenne du domaine skiable.

    Utilise le lapse rate standard (-6.5°C / 1000m) et pondère à 60% entre village et sommet
    pour représenter la zone où on skie le plus.

    Exemple Chamonix : tmax_vallée=7°C (févr.), alt_village=1035m, alt_ski_max=3842m
      → alt_ski_moy = 1035 + (3842-1035)*0.60 = 2719m
      → delta = 2719 - 1035 = 1684m
      → tmax_piste = 7 - 1684 * 6.5/1000 = 7 - 10.9 = -3.9°C → neige garantie
    """
    if alt_ski_max is None or alt_ski_max <= alt_village:
        return tmax_vallee  # Pas de correction si pas d'info altitude ou aberrante
    alt_ski_moy = alt_village + (alt_ski_max - alt_village) * SKI_DOMAIN_AVG_RATIO
    delta_alt = alt_ski_moy - alt_village
    return tmax_vallee - delta_alt * LAPSE_RATE_C_PER_M


def _snow_reliability(tmax_piste: float, rain_pct: float, has_glacier: bool = False) -> float:
    """
    Proxy enneigement [0, 1] basé sur la T° SUR LES PISTES (pas vallée).

    IMPORTANT : tmax_piste doit être déjà corrigé via apply_lapse_rate().

    Logique :
      - tmax_piste ≤ 0°C    : poudreuse garantie
      - 0 à 3°C             : neige quasi certaine
      - 3 à 7°C             : neige dégradée mais skiable
      - 7 à 12°C            : fin de saison (zones basses)
      - > 12°C              : pas de neige

    Bonus glacier : +0.15 minimum garanti pour les stations équipées
    (Hintertux, Zell am See/Kitzsteinhorn, Zermatt/Klein Matterhorn, etc.).
    """
    # Score de base selon T° pistes
    if tmax_piste <= 0:
        base = 0.70
        powder_bonus = min(0.20, rain_pct / 100 * 0.45)
        score = base + powder_bonus
    elif tmax_piste <= 3:
        cold_factor = (3 - tmax_piste) / 3
        base = 0.65 + cold_factor * 0.10
        heavy_penalty = max(0, rain_pct - 60) / 100 * 0.15
        score = max(0.55, base - heavy_penalty)
    elif tmax_piste <= 7:
        # Neige dégradée mais encore présente sur les pistes d'altitude
        score = max(0.35, 0.55 - (tmax_piste - 3) / 4 * 0.20 - rain_pct / 100 * 0.10)
    elif tmax_piste <= 12:
        score = max(0.10, 0.35 - (tmax_piste - 7) / 5 * 0.25 - rain_pct / 100 * 0.15)
    else:
        score = 0.0

    # Bonus glacier : garantie neige uniquement quand il fait encore froid en altitude.
    # Évite les scores trop optimistes en mai/octobre où le glacier existe mais les pistes
    # sont largement fermées (sauf ski d'alpinisme spécialisé).
    if has_glacier and tmax_piste <= 5:
        score = max(score, 0.65)

    return min(1.0, score)


def raw_score_winter(tmax_vallee: float, rain_pct: float, sun_h: float,
                     alt_village: float = None, alt_ski_max: float = None,
                     has_glacier: bool = False) -> float:
    """
    Score brut [0, 1] pour activités ski/montagne hiver.

    Args:
        tmax_vallee : T° max en vallée (°C) — telle que dans climate.csv
        rain_pct    : % de jours de précipitations (0-100)
        sun_h       : heures de soleil quotidien moyen
        alt_village : altitude du centre-ville (m) — optionnel
        alt_ski_max : altitude max du domaine skiable (m) — optionnel
        has_glacier : True si glacier permanent

    Si alt_village/alt_ski_max sont fournis : correction altitude appliquée.
    Sinon : fallback sur l'ancien modèle (backward-compat).

    Poids :
      40% enneigement proxy (sur tmax_piste corrigé si altitude connue)
      40% température confort (sur tmax_piste corrigé)
      20% soleil
    """
    # Correction altitude si données disponibles
    if alt_village is not None and alt_ski_max is not None:
        tmax_piste = apply_lapse_rate(tmax_vallee, alt_village, alt_ski_max)
    else:
        # Backward-compat : utilise tmax vallée directement
        tmax_piste = tmax_vallee

    t    = t_ideal_winter(tmax_piste)
    snow = _snow_reliability(tmax_piste, rain_pct, has_glacier)
    sun  = min(1.0, sun_h / 12.0)
    return 0.40 * t + 0.40 * snow + 0.20 * sun


def compute_ski_score(tmax: float, rain_pct: float, sun_h: float,
                      alt_village: float = None, alt_ski_max: float = None,
                      has_glacier: bool = False) -> float:
    """
    Score ski direct /10 (mapping linéaire).

    Signature étendue avec paramètres altitude/glacier.
    Les 3 premiers arguments restent compatibles avec l'ancien appel.
    """
    return round(raw_score_winter(tmax, rain_pct, sun_h,
                                   alt_village, alt_ski_max, has_glacier) * 10, 1)


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


# ── PROFILS DE SCORING PERSONNALISÉS ─────────────────────────────────────────

def t_ideal_cool(tmax: float) -> float:
    """Profil ❄️ Prefer cool — optimum 15-20°C, pénalise la chaleur plus tôt."""
    if tmax <= 3:   return 0.0
    if tmax <= 10:  return (tmax - 3) / 7 * 0.3
    if tmax <= 18:  return 0.3 + (tmax - 10) / 8 * 0.6   # optimum 18°C
    if tmax <= 22:  return 0.9 - (tmax - 18) / 4 * 0.2   # 0.9 -> 0.7
    if tmax <= 27:  return 0.7 - (tmax - 22) / 5 * 0.4   # 0.7 -> 0.3
    if tmax <= 32:  return 0.3 - (tmax - 27) / 5 * 0.25  # 0.3 -> 0.05
    return 0.0


def t_ideal_warm(tmax: float) -> float:
    """Profil 🔥 Prefer warm — optimum 27-32°C, tolère la chaleur, pénalise le froid."""
    if tmax <= 8:   return 0.0
    if tmax <= 18:  return (tmax - 8) / 10 * 0.2          # froid fortement pénalisé
    if tmax <= 24:  return 0.2 + (tmax - 18) / 6 * 0.4
    if tmax <= 32:  return 0.6 + (tmax - 24) / 8 * 0.4   # optimum 32°C
    if tmax <= 36:  return 1.0 - (tmax - 32) / 4 * 0.3   # 1.0 -> 0.7
    if tmax <= 40:  return 0.7 - (tmax - 36) / 4 * 0.5   # 0.7 -> 0.2
    return 0.0


def dew_point_penalty_sensitive(tmax: float, dew_point: float) -> float:
    """
    Profil 💧 Humidity sensitive — pénalité dew point renforcée.
    Seuil abaissé à 14°C (vs 16°C standard), pénalité max 0.35 (vs 0.20).
    S'applique dès tmax > 22°C (vs 26°C standard).
    """
    if tmax < 22 or dew_point is None:
        return 0.0
    if dew_point < 14:
        return 0.0
    heat_factor = min(1.0, (tmax - 22) / 14)
    dew_factor  = min(1.0, (dew_point - 14) / 10)
    return round(0.35 * heat_factor * dew_factor, 3)


def profile_score(tmax, rain_pct, sun_h, dew_point, profile='balanced',
                  precip_mm=None):
    """
    Calcule un score brut [0,1] selon le profil utilisateur.
    Utilise le même squelette que raw_score() mais avec des fonctions
    de température et pénalités humidité adaptées.

    Profils :
      'balanced'  → comportement identique au moteur standard
      'cool'      → t_ideal_cool, même pluie/soleil
      'warm'      → t_ideal_warm, même pluie/soleil
      'humid'     → t_ideal standard, dew_point_penalty_sensitive
    """
    # Poids communs
    w_t, w_r, w_s = 0.40, 0.35, 0.25

    # Température
    if profile == 'cool':
        t = t_ideal_cool(tmax)
    elif profile == 'warm':
        t = t_ideal_warm(tmax)
    else:
        t = t_ideal(tmax)

    # Pluie
    eff_rain = effective_rain_pct(rain_pct, precip_mm)
    r = max(0.0, 1.0 - eff_rain / 100)

    # Soleil
    s = min(1.0, sun_h / 15.0)

    raw = w_t * t + w_r * r + w_s * s

    # Pénalité humidité
    if profile == 'humid':
        raw -= dew_point_penalty_sensitive(tmax, dew_point)
    else:
        raw -= dew_point_penalty(tmax, dew_point or 0)
    # Pénalité sécheresse dans tous les profils
    raw -= dry_climate_penalty(tmax, dew_point)

    return max(0.0, min(1.0, raw))



# ═══════════════════════════════════════════════════════════════════
# SCORING RANDONNÉE MONTAGNE (hiking_score)
# ═══════════════════════════════════════════════════════════════════
#
# Destinations concernées : mountain=True (111 dans destinations.csv).
# Problème résolu : le score été standard pénalise tort les montagnes en
# été (ex: Dolomites Juil = 12°C tmax → t_ideal=0.26 alors que pour la
# randonnée 12°C journée est idéal).
#
# Différences vs raw_score standard :
#   • Optimum thermique 10-22°C (au lieu de 22-28°C)
#   • Pluie pénalisée 40% (au lieu de 35%) — plus critique en montagne
#   • Soleil pondéré 20% (au lieu de 25%) — moins crucial qu'en balnéaire
#   • Pas de pénalité humidité (pas de bain de sueur à 28°C/90%)
#   • Dessous 0°C = 0 (neige/verglas)

def t_ideal_hiking(tmax: float) -> float:
    """Confort randonnée montagne [0,1] selon tmax.

    < 0°C : 0.0  (neige/verglas, impraticable sans équipement alpin)
    0-5°C : 0.0-0.25  (très froid)
    5-10°C : 0.25-0.65  (frais, faisable avec équipement)
    10-22°C : 0.85-1.0  (zone optimale randonnée)
    22-25°C : 0.85-0.70  (chaud)
    25-28°C : 0.70-0.45  (fatiguant à l'effort)
    28-32°C : 0.45-0.15  (dangereux effort soutenu)
    > 32°C : 0.15-0.0  (canicule, rando déconseillée)
    """
    if tmax < 0:   return 0.0
    if tmax <= 5:  return tmax / 5 * 0.25
    if tmax <= 10: return 0.25 + (tmax - 5) / 5 * 0.40    # 0.25 → 0.65
    if tmax <= 14: return 0.65 + (tmax - 10) / 4 * 0.25   # 0.65 → 0.90
    if tmax <= 22: return 0.90 + (tmax - 14) / 8 * 0.10   # 0.90 → 1.00 (pic à 22°C)
    if tmax <= 25: return 1.00 - (tmax - 22) / 3 * 0.15   # 1.00 → 0.85
    if tmax <= 28: return 0.85 - (tmax - 25) / 3 * 0.15   # 0.85 → 0.70, corrigé ci-dessous
    if tmax <= 32: return 0.70 - (tmax - 28) / 4 * 0.55   # 0.70 → 0.15
    if tmax <= 38: return max(0.0, 0.15 - (tmax - 32) / 6 * 0.15)
    return 0.0


def raw_score_hiking(tmax: float, rain_pct: float, sun_h: float,
                     precip_mm: float = None) -> float:
    """Score brut randonnée [0,1] avant mapping /10.

    Poids : 40% température (t_ideal_hiking), 40% pluie, 20% soleil.
    Pas de pénalité humidité (non-critique en rando vs balnéaire).
    """
    eff_rain = effective_rain_pct(rain_pct, precip_mm)
    base = (0.40 * t_ideal_hiking(tmax)
          + 0.40 * max(0.0, 1.0 - eff_rain / 100.0)
          + 0.20 * min(1.0, sun_h / 12.0))
    return max(0.0, min(1.0, base))


def compute_hiking_score(tmax: float, rain_pct: float, sun_h: float,
                         precip_mm: float = None) -> float:
    """Score randonnée sur /10 (mapping linéaire depuis raw_score_hiking)."""
    return round(raw_score_hiking(tmax, rain_pct, sun_h, precip_mm) * 10, 1)
