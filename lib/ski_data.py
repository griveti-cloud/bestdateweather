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
                'notes': r.get('notes', '').strip(),
            }
    return data


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
    print(f"  ✓ chamonix : {cham}")

    # Zell am See : station + glacier
    zell = get_ski_data('zell-am-see')
    assert zell['has_glacier'] is True
    assert zell['alt_ski_max'] == 3029
    print(f"  ✓ zell-am-see : glacier Kitzsteinhorn")

    # Innsbruck : mountain mais pas station ski
    ins = get_ski_data('innsbruck')
    assert ins['is_ski_resort'] is False
    print(f"  ✓ innsbruck : is_ski_resort=False (ville capitale)")

    # Slug non mountain
    nope = get_ski_data('bali')
    assert nope is None, "Bali ne devrait pas être dans ski_altitudes.csv"
    print(f"  ✓ bali : None (pas mountain)")

    # Raccourci
    assert is_ski_resort('val-thorens') is True
    assert is_ski_resort('salzburg') is False
    print(f"  ✓ is_ski_resort() helper")

    # Stats
    all_data = _load_all()
    print(f"\n  Total entrées : {len(all_data)}")
    ski_count = sum(1 for d in all_data.values() if d['is_ski_resort'])
    glacier_count = sum(1 for d in all_data.values() if d['has_glacier'])
    print(f"  Stations ski : {ski_count}")
    print(f"  Avec glacier : {glacier_count}")


if __name__ == '__main__':
    _test()
