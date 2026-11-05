"""
Classification climatique de Köppen-Geiger calculée à partir des normales
mensuelles du site (data/climate.csv : tmin, tmax en °C, precip_mm en mm par
jour en moyenne).

Pourquoi : l'ancien libellé (lib/v6_adapter._build_climate_type) déduisait le
climat de deux indicateurs du fichier des destinations (« côtier »,
« tropical ») et de la latitude. Toute ville côtière entre 10° et 60° de
latitude devenait « Tempéré océanique » : Los Angeles, Barcelone, Dubaï,
Athènes… La classification de Köppen se calcule directement à partir des
températures et des pluies mensuelles déjà présentes dans les données.

Règles (Peel, Finlayson et McMahon, 2007, Hydrology and Earth System
Sciences 11, 1633-1644) :
- température moyenne du mois = (tmin + tmax) / 2 (approximation) ;
- pluie du mois = precip_mm × nombre de jours ;
- été = avril à septembre dans l'hémisphère nord, octobre à mars au sud.
"""
DAYS = [31, 28.25, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

LABELS = {
    'Af':  {'fr': 'Équatorial', 'en': 'Equatorial', 'es': 'Ecuatorial', 'de': 'Äquatorial'},
    'Af_humid': {'fr': 'Tropical humide', 'en': 'Tropical rainforest', 'es': 'Tropical húmedo', 'de': 'Tropisch-feucht'},
    'Am':  {'fr': 'Tropical de mousson', 'en': 'Tropical monsoon', 'es': 'Tropical monzónico', 'de': 'Tropischer Monsun'},
    'Aw':  {'fr': 'Tropical à saison sèche', 'en': 'Tropical savanna', 'es': 'Tropical de sabana', 'de': 'Tropische Savanne'},
    'BWh': {'fr': 'Désertique chaud', 'en': 'Hot desert', 'es': 'Desértico cálido', 'de': 'Heißes Wüstenklima'},
    'BWk': {'fr': 'Désertique froid', 'en': 'Cold desert', 'es': 'Desértico frío', 'de': 'Kaltes Wüstenklima'},
    'BSh': {'fr': 'Semi-aride chaud', 'en': 'Hot semi-arid', 'es': 'Semiárido cálido', 'de': 'Heißes Steppenklima'},
    'BSk': {'fr': 'Semi-aride froid', 'en': 'Cold semi-arid', 'es': 'Semiárido frío', 'de': 'Kaltes Steppenklima'},
    'Cs':  {'fr': 'Méditerranéen', 'en': 'Mediterranean', 'es': 'Mediterráneo', 'de': 'Mittelmeerklima'},
    'Cs_dry': {'fr': 'Méditerranéen sec', 'en': 'Dry Mediterranean', 'es': 'Mediterráneo seco', 'de': 'Trockenes Mittelmeerklima'},
    'Cwa': {'fr': 'Subtropical à hiver sec', 'en': 'Subtropical, dry winter', 'es': 'Subtropical de invierno seco', 'de': 'Subtropisch, trockener Winter'},
    'Cwb': {'fr': 'Tropical d’altitude', 'en': 'Subtropical highland', 'es': 'Subtropical de altitud', 'de': 'Subtropisches Höhenklima'},
    'Cfa': {'fr': 'Subtropical humide', 'en': 'Humid subtropical', 'es': 'Subtropical húmedo', 'de': 'Feuchtes Subtropenklima'},
    'Cfb': {'fr': 'Océanique', 'en': 'Oceanic', 'es': 'Oceánico', 'de': 'Ozeanisch'},
    'Cfc': {'fr': 'Océanique subpolaire', 'en': 'Subpolar oceanic', 'es': 'Oceánico subpolar', 'de': 'Subpolar-ozeanisch'},
    'Dhot': {'fr': 'Continental à été chaud', 'en': 'Hot-summer continental', 'es': 'Continental de verano cálido', 'de': 'Kontinental, heißer Sommer'},
    'Dwarm': {'fr': 'Continental', 'en': 'Humid continental', 'es': 'Continental húmedo', 'de': 'Feuchtes Kontinentalklima'},
    'Dc':  {'fr': 'Subarctique', 'en': 'Subarctic', 'es': 'Subártico', 'de': 'Subarktisch'},
    'ET':  {'fr': 'Toundra', 'en': 'Tundra', 'es': 'Tundra', 'de': 'Tundra'},
    'EF':  {'fr': 'Polaire', 'en': 'Polar ice cap', 'es': 'Polar', 'de': 'Polarklima'},
}


def classify(months, lat):
    """months : 12 dicts (ordre janvier à décembre) avec tmin, tmax et precip_mm
    (fichier) ou precip (dicts du générateur), en mm par jour.
    Retourne le code de Köppen (ex. 'Csa'), ou '' si les données manquent."""
    try:
        t = [(float(m['tmin']) + float(m['tmax'])) / 2 for m in months]
        p = [float(m['precip_mm'] if 'precip_mm' in m else m['precip']) * d for m, d in zip(months, DAYS)]
    except (KeyError, TypeError, ValueError):
        return ''
    if len(t) != 12:
        return ''
    north = float(lat) >= 0
    summer = [3, 4, 5, 6, 7, 8] if north else [9, 10, 11, 0, 1, 2]
    winter = [i for i in range(12) if i not in summer]
    tmax, tmin, tann, pann = max(t), min(t), sum(t) / 12, sum(p)
    if tmax < 10:
        return 'EF' if tmax < 0 else 'ET'
    psum, pwin = sum(p[i] for i in summer), sum(p[i] for i in winter)
    pth = 20 * tann + (280 if psum >= 0.7 * pann else 0 if pwin >= 0.7 * pann else 140)
    if pann < pth:                        # Peel et al. : MAP < 10 × (2 × MAT + 0/14/28), soit ce seuil en mm
        # chaud / froid : variante « mois le plus froid au-dessus de 0 °C » plutôt que la moyenne
        # annuelle de 18 °C, qui classait Lanzarote en « désert froid » à cause de normales
        # légèrement sous-estimées sur les petites îles.
        return ('BW' if pann < pth / 2 else 'BS') + ('h' if tmin > 0 else 'k')
    if tmin >= 18:
        pdry = min(p)
        if pdry >= 60:
            return 'Af'
        return 'Am' if pdry >= 100 - pann / 25 else 'Aw'
    ps_min, ps_max = min(p[i] for i in summer), max(p[i] for i in summer)
    pw_min, pw_max = min(p[i] for i in winter), max(p[i] for i in winter)
    if ps_min < 40 and ps_min < pw_max / 3:
        second = 's'
    elif pw_min < ps_max / 10:
        second = 'w'
    else:
        second = 'f'
    warm = sum(1 for x in t if x >= 10)
    third = 'a' if tmax >= 22 else 'b' if warm >= 4 else 'c'
    return ('C' if tmin > 0 else 'D') + second + third


def label(code, lang='fr', mountain=False, lat=None, winter_rain=False):
    """Libellé affiché. Les stations de montagne gardent « climat alpin ».
    Deux précisions de lecture, sans changer le code de Köppen :
    - Af hors de la bande 10° N-10° S (Miami, Maurice) : « tropical humide »
      plutôt qu'« équatorial » ;
    - C à été frais (3e lettre b ou c) entre les tropiques (Quito, Bogota,
      Mexico, Machu Picchu) : « tropical d’altitude », pas « océanique » ni
      « méditerranéen » ;
    - steppe (BS) à pluies d'hiver entre 30° et 45° de latitude :
      « méditerranéen sec » (Malte, Santorin, Marrakech)."""
    lang = 'en' if lang == 'en-us' else lang
    if mountain:
        return {'fr': 'Climat alpin de montagne', 'en': 'Alpine mountain climate',
                'es': 'Clima alpino de montaña', 'de': 'Alpines Bergklima'}.get(lang, 'Climat alpin de montagne')
    if not code:
        return ''
    alat = abs(float(lat)) if lat is not None else None
    if code == 'Af' and alat is not None and alat > 10:
        key = 'Af_humid'
    elif code[0] == 'C' and alat is not None and (alat < 20 or (alat < 23.5 and code[2] in 'bc')):
        key = 'Cwb'                       # climat tempéré entre les tropiques = altitude (Arusha, Quito)
    elif code.startswith('BS') and winter_rain and alat is not None and 30 <= alat <= 45:
        key = 'Cs_dry'                    # steppe à pluies d'hiver du bassin méditerranéen (Malte, Santorin)
    elif code.startswith('Cs'):
        key = 'Cs'
    elif code[0] == 'D':
        key = 'Dc' if code[2] in 'cd' else 'Dhot' if code[2] == 'a' else 'Dwarm'
    elif code in ('Cwc',):
        key = 'Cwb'
    elif code in ('As',):
        key = 'Aw'
    else:
        key = code
    return LABELS.get(key, {}).get(lang, '')


def winter_rain(months, lat):
    """Vrai si au moins 60 % des pluies tombent pendant le semestre d'hiver."""
    try:
        p = [float(m['precip_mm'] if 'precip_mm' in m else m['precip']) * d for m, d in zip(months, DAYS)]
    except (KeyError, TypeError, ValueError):
        return False
    summer = [3, 4, 5, 6, 7, 8] if float(lat) >= 0 else [9, 10, 11, 0, 1, 2]
    tot = sum(p)
    return tot > 0 and sum(p[i] for i in range(12) if i not in summer) >= 0.6 * tot


def climate_label(months, lat, lang='fr', mountain=False):
    """Libellé affiché sur les pages, à partir des 12 normales mensuelles."""
    return label(classify(months, lat), lang, mountain, lat, winter_rain(months, lat))
