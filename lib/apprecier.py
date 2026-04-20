"""
Fonctions pures d'appréciation qualitative des métriques météo/conditions.

Utilisées pour produire les labels textuels des fiches v6 (tooltips, signal cards,
mobile cards). Chaque fonction retourne (label, classe_css) pour un affichage cohérent.

Sources des seuils :
- Dew point : NOAA/NWS Humidity Classification (degré de moiteur ressentie)
- Vagues : échelles surf WSL / Surfline
- Mer : échelle baignade standard (confort thermique)
- AQI : OMS / US EPA Air Quality Index
- UV : OMS UV Index (exposition recommandée)
- Enneigement : seuils station de ski (moyenne mi-saison)

Conventions :
- label : str en français (sera localisé via lib/common.py:LANG_*)
- classe : str dans {'good', 'mid', 'bad'} pour CSS color coding
- Si valeur = None ou invalide : retourne (None, None)
"""

def apprecier_humidite(dew_point_c):
    """
    Confort humide selon point de rosée (°C).
    Indépendant de la T° ambiante — meilleur que l'humidité relative (%).

    Seuils NOAA :
      < 13°C : très sec, confortable
      13-15 : agréable
      16-18 : acceptable
      19-21 : un peu moite
      22-24 : oppressant
      >= 25 : étouffant
    """
    if dew_point_c is None:
        return None, None
    if dew_point_c < 13:
        return "Confortable", "good"
    if dew_point_c < 16:
        return "Agréable", "good"
    if dew_point_c < 19:
        return "Acceptable", "mid"
    if dew_point_c < 22:
        return "Un peu moite", "mid"
    if dew_point_c < 25:
        return "Oppressant", "bad"
    return "Étouffant", "bad"


def apprecier_vagues(hauteur_m):
    """
    Conditions surf selon hauteur de houle (m).

    Seuils adaptés pour non-experts (pas spot-spécifique) :
      < 0.5 : plat (pas de vagues)
      0.5-1.0 : petit, débutant
      1.0-1.5 : modéré, intermédiaire
      1.5-2.0 : bon surf
      2.0-3.0 : puissant, confirmé
      > 3.0 : grosse houle, experts
    """
    if hauteur_m is None:
        return None, None
    if hauteur_m < 0.5:
        return "Plat", "bad"
    if hauteur_m < 1.0:
        return "Débutant", "mid"
    if hauteur_m < 1.5:
        return "Intermédiaire", "good"
    if hauteur_m < 2.0:
        return "Bon surf", "good"
    if hauteur_m < 3.0:
        return "Puissant", "mid"
    return "Grosse houle", "bad"


def apprecier_mer(temp_c):
    """
    Confort baignade selon température de la mer (°C).

    Seuils pratiques :
      < 18 : froide (baignade courte seulement)
      18-20 : fraîche
      20-22 : baignable
      22-24 : agréable
      24-26 : très agréable
      26-28 : chaude
      >= 28 : bain chaud (inconfort possible en plein soleil)
    """
    if temp_c is None:
        return None, None
    if temp_c < 18:
        return "Froide", "bad"
    if temp_c < 20:
        return "Fraîche", "mid"
    if temp_c < 22:
        return "Baignable", "mid"
    if temp_c < 24:
        return "Agréable", "good"
    if temp_c < 26:
        return "Très agréable", "good"
    if temp_c < 28:
        return "Chaude", "good"
    return "Bain chaud", "mid"


def apprecier_aqi(aqi):
    """
    Qualité de l'air selon AQI standardisé (OMS/EPA).

    Seuils officiels :
      0-50 : excellent (pas de précaution)
      51-100 : modéré
      101-150 : mauvais pour groupes sensibles
      151-200 : mauvais
      > 200 : très mauvais (éviter activité outdoor)
    """
    if aqi is None:
        return None, None
    if aqi <= 50:
        return "Excellent", "good"
    if aqi <= 100:
        return "Modéré", "mid"
    if aqi <= 150:
        return "Sensible", "bad"
    if aqi <= 200:
        return "Mauvais", "bad"
    return "Très mauvais", "bad"


def apprecier_uv(uv_index):
    """
    Index UV OMS.

    Seuils :
      < 3 : faible
      3-5 : modéré
      6-7 : fort
      8-10 : très fort (crème obligatoire)
      >= 11 : extrême (éviter exposition 11h-16h)
    """
    if uv_index is None:
        return None, None
    if uv_index < 3:
        return "Faible", "good"
    if uv_index < 6:
        return "Modéré", "good"
    if uv_index < 8:
        return "Fort", "mid"
    if uv_index < 11:
        return "Très fort", "bad"
    return "Extrême", "bad"


def apprecier_enneigement(hauteur_cm):
    """
    Conditions ski selon hauteur moyenne du manteau neigeux à 1 800 m (cm).

    Seuils approximatifs pour stations alpines :
      < 30 : insuffisant
      30-60 : limité
      60-100 : correct
      100-150 : bon
      150-250 : excellent
      > 250 : exceptionnel
    """
    if hauteur_cm is None:
        return None, None
    if hauteur_cm < 30:
        return "Insuffisant", "bad"
    if hauteur_cm < 60:
        return "Limité", "mid"
    if hauteur_cm < 100:
        return "Correct", "mid"
    if hauteur_cm < 150:
        return "Bon", "good"
    if hauteur_cm < 250:
        return "Excellent", "good"
    return "Exceptionnel", "good"


def apprecier_ressenti_synthese(tmax, dew):
    """
    Label de confort thermique global.
    Délègue à lib/common.py:ressenti() qui est la fonction de prod
    (ne pas dupliquer la logique ici).

    Retourne (label, color_hex) — pour compatibilité avec l'existant.
    """
    from lib.common import ressenti
    return ressenti(tmax, dew, lang='fr')


# ══════════════════════════════════════════════════════════════════
# TESTS unitaires minimaux (à lancer avec: python3 -m lib.apprecier)
# ══════════════════════════════════════════════════════════════════

def _test():
    """Tests de sanity check des seuils."""
    tests = [
        # (fonction, valeur, label_attendu, classe_attendue)
        (apprecier_humidite, 10, "Confortable", "good"),
        (apprecier_humidite, 14, "Agréable", "good"),
        (apprecier_humidite, 21.7, "Un peu moite", "mid"),  # Bali juillet
        (apprecier_humidite, 25, "Étouffant", "bad"),
        (apprecier_humidite, None, None, None),

        (apprecier_vagues, 0.3, "Plat", "bad"),
        (apprecier_vagues, 1.56, "Bon surf", "good"),  # Bali juillet
        (apprecier_vagues, 3.5, "Grosse houle", "bad"),

        (apprecier_mer, 15, "Froide", "bad"),
        (apprecier_mer, 27.8, "Chaude", "good"),  # Bali juillet
        (apprecier_mer, 30, "Bain chaud", "mid"),

        (apprecier_aqi, 24, "Excellent", "good"),  # Bali
        (apprecier_aqi, 80, "Modéré", "mid"),
        (apprecier_aqi, 180, "Mauvais", "bad"),

        (apprecier_uv, 2.5, "Faible", "good"),  # Chamonix janvier
        (apprecier_uv, 6.8, "Fort", "mid"),  # Bali juillet
        (apprecier_uv, 12, "Extrême", "bad"),

        (apprecier_enneigement, 150, "Excellent", "good"),  # Chamonix janvier
        (apprecier_enneigement, 40, "Limité", "mid"),
        (apprecier_enneigement, 280, "Exceptionnel", "good"),
    ]

    passed = 0
    for fn, val, exp_label, exp_class in tests:
        label, cls = fn(val)
        ok = (label == exp_label) and (cls == exp_class)
        status = "✓" if ok else "✗"
        if ok:
            passed += 1
        else:
            print(f"  {status} {fn.__name__}({val}) = ({label!r}, {cls!r}) — attendu ({exp_label!r}, {exp_class!r})")
    print(f"\n  {passed}/{len(tests)} tests passés")


if __name__ == "__main__":
    _test()
