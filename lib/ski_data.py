"""
Loader des données ski complémentaires (altitudes + glaciers) depuis
data/ski_altitudes.csv.

Usage :
    from lib.ski_data import get_ski_data

    ski = get_ski_data('chamonix')
    # → {'alt_village': 1035, 'alt_ski_max': 3842, 'has_glacier': True, 'is_ski_resort': True}

    if ski['is_ski_resort']:
        score = compute_ski_score(tmax, rain, sun,
                                   alt_village=ski['alt_village'],
                                   alt_ski_max=ski['alt_ski_max'],
                                   has_glacier=ski['has_glacier'])
"""

import csv
import os
from functools import lru_cache


_CSV_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'ski_altitudes.csv')


def _parse_int(s):
    s = s.strip()
    if not s:
        return None
    try:
        return int(s)
    except ValueError:
        return None


def _parse_bool(s):
    return s.strip().lower() in ('true', '1', 'yes')


@lru_cache(maxsize=1)
def _load_all():
    """Charge tout le CSV en cache (appelé une fois)."""
    data = {}
    if not os.path.exists(_CSV_PATH):
        return data
    with open(_CSV_PATH) as f:
        reader = csv.DictReader(f)
        for r in reader:
            slug = r.get('slug', '').strip()
            # Ignorer les commentaires et lignes vides
            if not slug or slug.startswith('#'):
                continue
            data[slug] = {
                'alt_village': _parse_int(r.get('alt_village', '')),
                'alt_ski_max': _parse_int(r.get('alt_ski_max', '')),
                'has_glacier': _parse_bool(r.get('has_glacier', '')),
                'is_ski_resort': _parse_bool(r.get('is_ski_resort', '')),
                'season_start': _parse_int(r.get('season_start', '')),
                'season_end': _parse_int(r.get('season_end', '')),
                'notes': r.get('notes', '').strip(),
            }
    return data


def is_month_in_season(month, season_start, season_end):
    """
    Détermine si un mois (1-12) tombe dans la saison d'ouverture.

    Gère le wrap annuel (ex: Décembre→Avril = start=12, end=4).

    Args:
        month : int 1-12
        season_start : int 1-12 ou None
        season_end : int 1-12 ou None

    Returns:
        bool : True si le mois est dans la saison, True aussi si pas de saison définie
               (pas de pénalité appliquée faute de data)
    """
    if season_start is None or season_end is None:
        return True  # pas d'info : on considère ouvert (pas de pénalité)
    if season_start <= season_end:
        # saison sur une année normale (ex: 6→10 pour hémisphère sud)
        return season_start <= month <= season_end
    else:
        # wrap annuel (ex: 12→4 alpes nord)
        return month >= season_start or month <= season_end


def get_ski_data(slug):
    """
    Retourne les données ski pour un slug donné.

    Returns:
        dict avec keys alt_village, alt_ski_max, has_glacier, is_ski_resort
        ou None si slug non trouvé (pas une destination mountain).
    """
    return _load_all().get(slug)


def is_ski_resort(slug):
    """Raccourci : True si destination est une vraie station de ski."""
    d = get_ski_data(slug)
    return d is not None and d['is_ski_resort']


# ══════════════════════════════════════════════════════════════════
# Tests
# ══════════════════════════════════════════════════════════════════

def _test():
    """Validation des cas clés."""
    # Chamonix : station ski avec glacier
    cham = get_ski_data('chamonix')
    assert cham is not None, "Chamonix manquant"
    assert cham['alt_village'] == 1035
    assert cham['alt_ski_max'] == 3842
    assert cham['has_glacier'] is True
    assert cham['is_ski_resort'] is True
    assert cham['season_start'] == 12
    assert cham['season_end'] == 5
    print(f"  ✓ chamonix : saison {cham['season_start']}→{cham['season_end']}")

    # Zell am See : station + glacier 365j
    zell = get_ski_data('zell-am-see')
    assert zell['has_glacier'] is True
    assert zell['alt_ski_max'] == 3029
    assert zell['season_start'] == 1 and zell['season_end'] == 12
    print(f"  ✓ zell-am-see : glacier Kitzsteinhorn (ouvert 365j)")

    # Innsbruck : mountain mais pas station ski
    ins = get_ski_data('innsbruck')
    assert ins['is_ski_resort'] is False
    assert ins['season_start'] is None
    print(f"  ✓ innsbruck : is_ski_resort=False (ville)")

    # Bariloche : hémisphère sud (saison 6→10)
    bari = get_ski_data('bariloche')
    assert bari['season_start'] == 6 and bari['season_end'] == 10
    print(f"  ✓ bariloche : saison juin→oct (hémisphère sud)")

    # Slug non mountain
    nope = get_ski_data('bali')
    assert nope is None, "Bali ne devrait pas être dans ski_altitudes.csv"
    print(f"  ✓ bali : None (pas mountain)")

    # Raccourci
    assert is_ski_resort('val-thorens') is True
    assert is_ski_resort('salzburg') is False
    print(f"  ✓ is_ski_resort() helper")

    # Test is_month_in_season : wrap annuel
    assert is_month_in_season(1, 12, 5) is True   # Janvier dans Déc→Mai
    assert is_month_in_season(3, 12, 5) is True   # Mars dans Déc→Mai
    assert is_month_in_season(6, 12, 5) is False  # Juin hors saison
    assert is_month_in_season(11, 12, 5) is False # Nov hors saison
    assert is_month_in_season(12, 12, 5) is True  # Déc dans saison
    print(f"  ✓ is_month_in_season (wrap annuel)")

    # Test hémisphère sud (pas de wrap)
    assert is_month_in_season(7, 6, 10) is True   # Juillet dans Juin→Oct
    assert is_month_in_season(2, 6, 10) is False  # Fév hors
    print(f"  ✓ is_month_in_season (hémisphère sud)")

    # Test glacier 365j
    assert is_month_in_season(6, 1, 12) is True
    assert is_month_in_season(1, 1, 12) is True
    print(f"  ✓ is_month_in_season (glacier 365j)")

    # Test None → True par défaut
    assert is_month_in_season(5, None, None) is True
    print(f"  ✓ is_month_in_season (None → True par défaut)")

    # Stats
    all_data = _load_all()
    print(f"\n  Total entrées : {len(all_data)}")
    ski_count = sum(1 for d in all_data.values() if d['is_ski_resort'])
    glacier_count = sum(1 for d in all_data.values() if d['has_glacier'])
    with_season = sum(1 for d in all_data.values() if d['season_start'] is not None)
    print(f"  Stations ski : {ski_count}")
    print(f"  Avec glacier : {glacier_count}")
    print(f"  Avec saison renseignée : {with_season}")


if __name__ == '__main__':
    _test()
