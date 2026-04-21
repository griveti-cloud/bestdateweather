"""
Helper pour charger et accéder à data/climate_trend.json.

Le JSON contient pour 616 destinations les données annuelles ERA5 sur
2016-2025 (T° min/moyenne/max), utilisé pour le graphique "Tendance 10 ans"
des fiches V6.

Structure JSON :
    {
      "paris": {
        "years": [2016, 2017, ..., 2025],
        "tmax":  [15.4, 16.1, ..., 16.9],
        "tmin":  [7.8, 8.0, ..., 8.7],
        "tmoy":  [11.6, 12.1, ..., 12.8],
        "cmip6_rate": null
      },
      ...
    }

Usage :
    from lib.climate_trend import load_trend, get_trend
    
    all_trends = load_trend()  # Charge tout (cache global)
    paris = get_trend("paris")  # → dict ou None si absent
"""
import json
import os
from functools import lru_cache

_DEFAULT_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data", "climate_trend.json"
)


@lru_cache(maxsize=1)
def load_trend(path=None):
    """
    Charge data/climate_trend.json en cache (1 seule lecture par process).

    Args:
        path: chemin vers le JSON. Si None, utilise data/climate_trend.json
              relatif à la racine du repo.

    Returns:
        dict {slug: {years, tmax, tmin, tmoy, cmip6_rate}}
    """
    p = path or _DEFAULT_PATH
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)


def get_trend(slug, path=None):
    """
    Récupère le trend annuel pour un slug donné.

    Args:
        slug: slug FR de la destination (ex: 'paris', 'bali', 'chamonix')
        path: chemin JSON optionnel

    Returns:
        dict ou None si la destination n'a pas de données trend
    """
    return load_trend(path).get(slug)
