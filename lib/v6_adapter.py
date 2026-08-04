"""
lib/v6_adapter.py — Adaptateur entre les données génériques (CSV/JSON) et
le orchestrateur lib/v6.py::render_v6_full_page().

Architecture Option B : ce module est appelé par gen_annual_v6() dans
generate_pages.py. Il prend les mêmes inputs que gen_annual() V5 (cfg, dest,
months, etc.) et produit le HTML V6 via les helpers lib/v6.py.

Ce module ne touche pas à V5 et n'est appelé que si le flag --v6 est passé.
"""

from __future__ import annotations
import json
import os

from lib.v6 import render_v6_full_page

# Cache des fichiers JSON ouverts (chargés une seule fois par run)
_data_cache: dict[str, dict] = {}


def _load_json_cached(path: str) -> dict:
    """Charge un JSON et cache le résultat pour les appels suivants."""
    if path not in _data_cache:
        with open(path, encoding='utf-8') as f:
            _data_cache[path] = json.load(f)
    return _data_cache[path]


# ─────────────────────────────────────────────────────────────────────────────
# Helpers d'extraction
# ─────────────────────────────────────────────────────────────────────────────

def _safe_float(v, default=0.0) -> float:
    try:
        return float(v) if v not in (None, '') else default
    except (ValueError, TypeError):
        return default


def _safe_int(v, default=0) -> int:
    try:
        return int(v) if v not in (None, '') else default
    except (ValueError, TypeError):
        return default


def _bool(v) -> bool:
    """Parse les valeurs CSV bool ('True'/'False'/'1'/'0'/'yes'/...)."""
    if isinstance(v, bool):
        return v
    if v is None:
        return False
    return str(v).strip().lower() in ('true', '1', 'yes', 'oui')


def _extract_climate_extremes(months: list[dict], months_loc: list[str] = None) -> dict:
    """À partir des 12 mois, extrait hottest/coldest/rainiest/sunniest.

    Args:
        months: liste de 12 dicts climate.csv (avec 'mois', 'tmax', 'tmin',
            'rain_pct', 'sun_h')
        months_loc: liste optionnelle de 12 noms de mois localisés
            (cfg['months']). Si fourni, les noms hottest/coldest/rainiest/
            sunniest_month sont localisés. Sinon fallback sur mc['mois'] (FR).

    Returns:
        {hottest_month, hottest_temp, coldest_month, coldest_temp,
         rainiest_month, rainiest_pct, sunniest_month, sunniest_h}
    """
    def loc(m):
        """Renvoie le nom du mois localisé si possible."""
        if months_loc:
            try:
                idx = months.index(m)
                return months_loc[idx]
            except (ValueError, IndexError):
                pass
        return m['mois']

    hottest = max(months, key=lambda m: _safe_float(m.get('tmax')))
    coldest = min(months, key=lambda m: _safe_float(m.get('tmax')))
    rainiest = max(months, key=lambda m: _safe_float(m.get('rain_pct')))
    sunniest = max(months, key=lambda m: _safe_float(m.get('sun_h')))
    return {
        'hottest_month': loc(hottest),
        'hottest_temp': _safe_float(hottest['tmax']),
        'coldest_month': loc(coldest),
        'coldest_temp': _safe_float(coldest['tmax']),
        'rainiest_month': loc(rainiest),
        'rainiest_pct': _safe_float(rainiest['rain_pct']),
        'sunniest_month': loc(sunniest),
        'sunniest_h': _safe_float(sunniest['sun_h']),
    }


def _compute_trend_value(slug: str, lat: float = None, lon: float = None) -> float | None:
    """Calcule la slope ERA5 par décennie pour une destination.

    Returns None si dataset absent (le helper trend_chart gère ce cas).
    """
    path = os.path.join(os.path.dirname(__file__), '..', 'data', 'climate_trend.json')
    try:
        d = _load_json_cached(path)
    except FileNotFoundError:
        return None

    # Schema slug-keyed
    if slug in d and 'years' in d[slug]:
        entry = d[slug]
        years = entry['years']
        tmoy = entry['tmoy']
    elif lat is not None and lon is not None:
        key = f'{lat:.2f},{lon:.2f}'
        if key in d and 'annual' in d[key]:
            ann = d[key]['annual']
            years = sorted(int(y) for y in ann.keys())
            tmoy = [ann[str(y)]['tmean'] for y in years]
        else:
            return None
    else:
        return None

    n = len(years)
    if n < 3:
        return None
    my = sum(years) / n
    mt = sum(tmoy) / n
    num = sum((years[i] - my) * (tmoy[i] - mt) for i in range(n))
    den = sum((years[i] - my) ** 2 for i in range(n))
    if den == 0:
        return None
    return (num / den) * 10  # par décennie


def _trend_is_significant(slug: str, lat: float = None, lon: float = None) -> bool:
    """Test de significativité de la pente (régression linéaire, p<0.05).

    Une pente sur 10 ans peut être forte mais dominée par la variabilité
    naturelle. On teste t = |slope| / SE(slope) contre la valeur critique de
    Student (dof = n-2 = 8 → 2.306 à 5% bilatéral). Sert à n'afficher une
    tendance CHIFFRÉE que si elle est statistiquement solide; sinon 'stable'.
    """
    import math
    path = os.path.join(os.path.dirname(__file__), '..', 'data', 'climate_trend.json')
    try:
        d = _load_json_cached(path)
    except FileNotFoundError:
        return False
    if slug in d and 'years' in d[slug]:
        years = d[slug]['years']; tmoy = d[slug]['tmoy']
    elif lat is not None and lon is not None:
        key = f'{lat:.2f},{lon:.2f}'
        ann = d.get(key, {}).get('annual')
        if not ann:
            return False
        years = sorted(int(y) for y in ann.keys())
        tmoy = [ann[str(y)]['tmean'] for y in years]
    else:
        return False
    n = len(years)
    if n < 4:
        return False
    my = sum(years) / n; mt = sum(tmoy) / n
    den = sum((y - my) ** 2 for y in years)
    if den == 0:
        return False
    b = sum((years[i] - my) * (tmoy[i] - mt) for i in range(n)) / den
    a = mt - b * my
    resid = [tmoy[i] - (a + b * years[i]) for i in range(n)]
    sse = sum(r * r for r in resid)
    if sse <= 0:
        return True  # ajustement parfait
    se = math.sqrt(sse / (n - 2) / den)
    if se == 0:
        return True
    # t critique Student dof=8, p<0.05 bilatéral
    T_CRIT = {4: 4.303, 5: 3.182, 6: 2.776, 7: 2.571, 8: 2.447,
              9: 2.365, 10: 2.306}.get(n - 2, 2.306)
    return abs(b / se) >= T_CRIT


def _detect_profile(dest: dict, climate_type: str = '') -> str:
    """Détecte le profil pour Box 3 et Adapter.

    Lit d'abord les flags du CSV destinations.csv, fallback sur climate_type.
    Ordre de priorité : polar > tropical > mountain > coastal > city.

    FIX i18n: pour 'polar', accepte les keywords FR/EN/ES/DE pour rester
    robuste après la localisation de _build_climate_type.
    """
    ct_lower = climate_type.lower()
    polar_keywords = ('polaire', 'subarctique',           # FR
                      'subarctic', 'polar',               # EN
                      'subártico', 'polar',               # ES (polar = même mot)
                      'subarktisch', 'polarklima')        # DE
    if any(kw in ct_lower for kw in polar_keywords):
        return 'polar'
    if _bool(dest.get('tropical')):
        return 'tropical'
    if _bool(dest.get('mountain')):
        return 'mountain'
    if _bool(dest.get('coastal')):
        return 'coastal'
    return 'city'


def _build_climate_type(dest: dict, lat: float, lang: str = 'fr') -> str:
    """Génère un libellé climat type depuis flags CSV + latitude.

    Approche pragmatique : on fait du Köppen-light pour avoir un texte.
    À enrichir plus tard avec une vraie classif Köppen-Geiger.

    FIX i18n: localise le libellé selon lang (FR/EN/EN-US/ES/DE).
    """
    # Détermination de la clé climat
    if _bool(dest.get('mountain')):
        key = 'alpine'
    elif abs(lat) < 10:
        key = 'tropical_equatorial'
    elif _bool(dest.get('tropical')):
        key = 'tropical'
    elif abs(lat) > 60:
        key = 'subarctic_oceanic'
    elif _bool(dest.get('coastal')):
        key = 'temperate_oceanic'
    else:
        key = 'temperate'

    # Mapping i18n
    LABELS = {
        'alpine': {
            'fr': 'Climat alpin de montagne', 'en': 'Alpine mountain climate',
            'en-us': 'Alpine mountain climate', 'es': 'Clima alpino de montaña',
            'de': 'Alpines Bergklima',
        },
        'tropical_equatorial': {
            'fr': 'Tropical équatorial', 'en': 'Equatorial tropical',
            'en-us': 'Equatorial tropical', 'es': 'Tropical ecuatorial',
            'de': 'Äquatorial-tropisch',
        },
        'tropical': {
            'fr': 'Tropical', 'en': 'Tropical', 'en-us': 'Tropical',
            'es': 'Tropical', 'de': 'Tropisch',
        },
        'subarctic_oceanic': {
            'fr': 'Subarctique océanique', 'en': 'Subarctic oceanic',
            'en-us': 'Subarctic oceanic', 'es': 'Subártico oceánico',
            'de': 'Subarktisch-ozeanisch',
        },
        'temperate_oceanic': {
            'fr': 'Tempéré océanique', 'en': 'Temperate oceanic',
            'en-us': 'Temperate oceanic', 'es': 'Templado oceánico',
            'de': 'Gemäßigt ozeanisch',
        },
        'temperate': {
            'fr': 'Tempéré', 'en': 'Temperate', 'en-us': 'Temperate',
            'es': 'Templado', 'de': 'Gemäßigt',
        },
    }
    return LABELS[key].get(lang, LABELS[key]['fr'])


def _country_info(country_name_fr: str) -> dict:
    """Retourne le dict country_info.json pour le pays donné, ou {} si absent."""
    path = os.path.join(os.path.dirname(__file__), '..', 'data', 'country_info.json')
    d = _load_json_cached(path)
    return d.get(country_name_fr, {})


def _flag_iso(flag_value: str) -> str:
    """Extrait le code ISO 2-lettres depuis la valeur flag du CSV.

    Format attendu : 'fr', 'us', 'gb', etc. (déjà ISO 2-letter dans destinations.csv).
    """
    return (flag_value or '').lower().strip()


# ─────────────────────────────────────────────────────────────────────────────
# Construction du page_data complet
# ─────────────────────────────────────────────────────────────────────────────

def build_page_data_v6(cfg: dict, dest: dict, months_climate: list[dict],
                       months_with_scores: list[dict],
                       slug: str, nom: str,
                       country_name: str, country_iso: str,
                       monthly_url_tpl: str,
                       editorial_html: str = '',
                       photo_url: str = '',
                       photo_credit: str = '',
                       update_month: str = '') -> dict:
    """Construit le dict page_data attendu par render_v6_full_page().

    Args:
        cfg: config langue (build_config)
        dest: dict ligne destinations.csv
        months_climate: 12 dicts climate.csv (avec mois, tmax, tmin, rain_pct, sun_h, precip_mm)
        months_with_scores: 12 dicts avec score_10 + classe ('rec'/'mid'/'avoid'),
            résultat de compute_scores ou compute_mountain_scores
        slug: slug local (FR/EN/ES/DE selon langue)
        nom: nom affichable
        country_name: nom pays localisé
        country_iso: code ISO 2-lettres pour drapeau
        monthly_url_tpl: template URL fiches mensuelles ({slug}, {mois_lower}, {mois_short})
        editorial_html: contenu édito annuel (HTML autorisé)
        photo_url: URL Unsplash hero (optionnel)
        photo_credit: HTML crédit photo (optionnel)
        update_month: mois localisé pour le tag '📅 Mise à jour X'
    """
    lang = cfg['lang']
    lat = _safe_float(dest['lat'])
    lon = _safe_float(dest['lon'])

    # Merge climate + scores en un seul flux 12 mois
    months_data = []
    MONTHS_LOC = cfg['months']  # noms localisés selon lang (FR/EN/EN-US/ES/DE)
    for i, mc in enumerate(months_climate):
        score_entry = months_with_scores[i] if i < len(months_with_scores) else {}
        months_data.append({
            'mois': MONTHS_LOC[i],  # FIX i18n: utiliser noms localisés (était mc['mois'] en FR brut)
            'tmin': _safe_float(mc.get('tmin')),
            'tmax': _safe_float(mc.get('tmax')),
            'rain_pct': _safe_float(mc.get('rain_pct')),
            'precip_mm': _safe_float(mc.get('precip', mc.get('precip_mm', 0))),  # FIX: clé 'precip' dans climate dict
            'sun_h': _safe_float(mc.get('sun_h')),
            'score_10': _safe_float(mc.get('score', score_entry.get('score_10', score_entry.get('score', 0)))),  # FIX Option C: score depuis CSV (recalculé via /tmp/regen_scores.py), fallback sur recalc live
            'classe': mc.get('classe', score_entry.get('classe', score_entry.get('cls', 'mid'))),  # FIX: classe vient du CSV (compute_scores ne la retourne pas)
            'uv_index': _safe_float(mc.get('uv_index', 0)),  # FIX: pour Conditions détaillées
            'dew_point': _safe_float(mc.get('dew_point', 0)),  # FIX: pour Humidité ressentie
        })

    # Best/worst pour le hero lead
    sorted_by_score = sorted(months_data, key=lambda m: m['score_10'], reverse=True)
    best = sorted_by_score[0]
    worst = sorted_by_score[-1]
    best['is_best'] = True  # pour la rangée surlignée dans Comprendre

    # Marquer is_best dans months_data (pas seulement dans la copie sortée)
    for m in months_data:
        if m['mois'] == best['mois']:
            m['is_best'] = True

    # Climate type + profile
    climate_type = _build_climate_type(dest, lat, lang)
    profile = _detect_profile(dest, climate_type)

    # Country info enrichi
    cinfo = _country_info(dest.get('pays', ''))
    lang_local = (cinfo.get('languages') or [''])[0]

    # i18n du nom de la langue parlée + nom de la monnaie (sources country_info.json en FR)
    LANG_NAME_I18N = {
        'Français': {'en': 'French', 'en-us': 'French', 'es': 'Francés', 'de': 'Französisch'},
        'Anglais': {'en': 'English', 'en-us': 'English', 'es': 'Inglés', 'de': 'Englisch'},
        'Espagnol': {'en': 'Spanish', 'en-us': 'Spanish', 'es': 'Español', 'de': 'Spanisch'},
        'Allemand': {'en': 'German', 'en-us': 'German', 'es': 'Alemán', 'de': 'Deutsch'},
        'Italien': {'en': 'Italian', 'en-us': 'Italian', 'es': 'Italiano', 'de': 'Italienisch'},
        'Portugais': {'en': 'Portuguese', 'en-us': 'Portuguese', 'es': 'Portugués', 'de': 'Portugiesisch'},
        'Néerlandais': {'en': 'Dutch', 'en-us': 'Dutch', 'es': 'Neerlandés', 'de': 'Niederländisch'},
        'Japonais': {'en': 'Japanese', 'en-us': 'Japanese', 'es': 'Japonés', 'de': 'Japanisch'},
        'Mandarin': {'en': 'Mandarin', 'en-us': 'Mandarin', 'es': 'Mandarín', 'de': 'Mandarin'},
        'Coréen': {'en': 'Korean', 'en-us': 'Korean', 'es': 'Coreano', 'de': 'Koreanisch'},
        'Arabe': {'en': 'Arabic', 'en-us': 'Arabic', 'es': 'Árabe', 'de': 'Arabisch'},
        'Russe': {'en': 'Russian', 'en-us': 'Russian', 'es': 'Ruso', 'de': 'Russisch'},
        'Hindi': {'en': 'Hindi', 'en-us': 'Hindi', 'es': 'Hindi', 'de': 'Hindi'},
        'Thaï': {'en': 'Thai', 'en-us': 'Thai', 'es': 'Tailandés', 'de': 'Thailändisch'},
        'Vietnamien': {'en': 'Vietnamese', 'en-us': 'Vietnamese', 'es': 'Vietnamita', 'de': 'Vietnamesisch'},
        'Indonésien': {'en': 'Indonesian', 'en-us': 'Indonesian', 'es': 'Indonesio', 'de': 'Indonesisch'},
        'Malais': {'en': 'Malay', 'en-us': 'Malay', 'es': 'Malayo', 'de': 'Malaiisch'},
        'Tamoul': {'en': 'Tamil', 'en-us': 'Tamil', 'es': 'Tamil', 'de': 'Tamilisch'},
        'Hébreu': {'en': 'Hebrew', 'en-us': 'Hebrew', 'es': 'Hebreo', 'de': 'Hebräisch'},
        'Turc': {'en': 'Turkish', 'en-us': 'Turkish', 'es': 'Turco', 'de': 'Türkisch'},
        'Grec': {'en': 'Greek', 'en-us': 'Greek', 'es': 'Griego', 'de': 'Griechisch'},
        'Polonais': {'en': 'Polish', 'en-us': 'Polish', 'es': 'Polaco', 'de': 'Polnisch'},
        'Tchèque': {'en': 'Czech', 'en-us': 'Czech', 'es': 'Checo', 'de': 'Tschechisch'},
        'Hongrois': {'en': 'Hungarian', 'en-us': 'Hungarian', 'es': 'Húngaro', 'de': 'Ungarisch'},
        'Suédois': {'en': 'Swedish', 'en-us': 'Swedish', 'es': 'Sueco', 'de': 'Schwedisch'},
        'Danois': {'en': 'Danish', 'en-us': 'Danish', 'es': 'Danés', 'de': 'Dänisch'},
        'Norvégien': {'en': 'Norwegian', 'en-us': 'Norwegian', 'es': 'Noruego', 'de': 'Norwegisch'},
        'Finnois': {'en': 'Finnish', 'en-us': 'Finnish', 'es': 'Finlandés', 'de': 'Finnisch'},
        'Islandais': {'en': 'Icelandic', 'en-us': 'Icelandic', 'es': 'Islandés', 'de': 'Isländisch'},
        'Croate': {'en': 'Croatian', 'en-us': 'Croatian', 'es': 'Croata', 'de': 'Kroatisch'},
        'Roumain': {'en': 'Romanian', 'en-us': 'Romanian', 'es': 'Rumano', 'de': 'Rumänisch'},
        'Albanais': {'en': 'Albanian', 'en-us': 'Albanian', 'es': 'Albanés', 'de': 'Albanisch'},
        'Bambara': {'en': 'Bambara', 'en-us': 'Bambara', 'es': 'Bambara', 'de': 'Bambara'},
        'Bengali': {'en': 'Bengali', 'en-us': 'Bengali', 'es': 'Bengalí', 'de': 'Bengalisch'},
        'Biélorusse': {'en': 'Belarusian', 'en-us': 'Belarusian', 'es': 'Bielorruso', 'de': 'Belarussisch'},
        'Comorien': {'en': 'Comorian', 'en-us': 'Comorian', 'es': 'Comorense', 'de': 'Komorisch'},
        'Créole haïtien': {'en': 'Haitian Creole', 'en-us': 'Haitian Creole', 'es': 'Criollo haitiano', 'de': 'Haitianisch'},
        'Gilbertin': {'en': 'Gilbertese', 'en-us': 'Gilbertese', 'es': 'Gilbertés', 'de': 'Kiribatisch'},
        'Kirundi': {'en': 'Kirundi', 'en-us': 'Kirundi', 'es': 'Kirundi', 'de': 'Kirundi'},
        'Kurde': {'en': 'Kurdish', 'en-us': 'Kurdish', 'es': 'Kurdo', 'de': 'Kurdisch'},
        'Luxembourgeois': {'en': 'Luxembourgish', 'en-us': 'Luxembourgish', 'es': 'Luxemburgués', 'de': 'Luxemburgisch'},
        'Marshallais': {'en': 'Marshallese', 'en-us': 'Marshallese', 'es': 'Marshalés', 'de': 'Marshallesisch'},
        'Ourdou': {'en': 'Urdu', 'en-us': 'Urdu', 'es': 'Urdu', 'de': 'Urdu'},
        'Sango': {'en': 'Sango', 'en-us': 'Sango', 'es': 'Sango', 'de': 'Sango'},
        'Serbe': {'en': 'Serbian', 'en-us': 'Serbian', 'es': 'Serbio', 'de': 'Serbisch'},
        'Sesotho': {'en': 'Sesotho', 'en-us': 'Sesotho', 'es': 'Sesoto', 'de': 'Sesotho'},
        'Somali': {'en': 'Somali', 'en-us': 'Somali', 'es': 'Somalí', 'de': 'Somali'},
        'Swati': {'en': 'Swati', 'en-us': 'Swati', 'es': 'Suazi', 'de': 'Siswati'},
        'Tigrigna': {'en': 'Tigrinya', 'en-us': 'Tigrinya', 'es': 'Tigriña', 'de': 'Tigrinya'},
        'Turkmène': {'en': 'Turkmen', 'en-us': 'Turkmen', 'es': 'Turcomano', 'de': 'Turkmenisch'},
        'Tuvaluan': {'en': 'Tuvaluan', 'en-us': 'Tuvaluan', 'es': 'Tuvaluano', 'de': 'Tuvaluisch'},
        'Tétoum': {'en': 'Tetum', 'en-us': 'Tetum', 'es': 'Tetun', 'de': 'Tetum'},
    }
    if lang in ('en', 'en-us', 'es', 'de') and lang_local in LANG_NAME_I18N:
        lang_local = LANG_NAME_I18N[lang_local].get(lang, lang_local)
    currency_name = cinfo.get('currency_name', '')
    # i18n nom monnaie (source country_info.json en FR)
    CUR_NAME_I18N = {
        'Euro': {'en': 'Euro', 'en-us': 'Euro', 'es': 'Euro', 'de': 'Euro'},
        'Dollar américain': {'en': 'US Dollar', 'en-us': 'US Dollar', 'es': 'Dólar estadounidense', 'de': 'US-Dollar'},
        'Livre sterling': {'en': 'Pound Sterling', 'en-us': 'Pound Sterling', 'es': 'Libra esterlina', 'de': 'Pfund Sterling'},
        'Yen': {'en': 'Yen', 'en-us': 'Yen', 'es': 'Yen', 'de': 'Yen'},
        'Yuan': {'en': 'Yuan', 'en-us': 'Yuan', 'es': 'Yuan', 'de': 'Yuan'},
        'Franc suisse': {'en': 'Swiss Franc', 'en-us': 'Swiss Franc', 'es': 'Franco suizo', 'de': 'Schweizer Franken'},
        'Dollar canadien': {'en': 'Canadian Dollar', 'en-us': 'Canadian Dollar', 'es': 'Dólar canadiense', 'de': 'Kanadischer Dollar'},
        'Dollar australien': {'en': 'Australian Dollar', 'en-us': 'Australian Dollar', 'es': 'Dólar australiano', 'de': 'Australischer Dollar'},
        'Dollar néo-zélandais': {'en': 'New Zealand Dollar', 'en-us': 'New Zealand Dollar', 'es': 'Dólar neozelandés', 'de': 'Neuseeland-Dollar'},
        'Dollar de Singapour': {'en': 'Singapore Dollar', 'en-us': 'Singapore Dollar', 'es': 'Dólar de Singapur', 'de': 'Singapur-Dollar'},
        'Dollar de Hong Kong': {'en': 'Hong Kong Dollar', 'en-us': 'Hong Kong Dollar', 'es': 'Dólar de Hong Kong', 'de': 'Hongkong-Dollar'},
        'Couronne suédoise': {'en': 'Swedish Krona', 'en-us': 'Swedish Krona', 'es': 'Corona sueca', 'de': 'Schwedische Krone'},
        'Couronne danoise': {'en': 'Danish Krone', 'en-us': 'Danish Krone', 'es': 'Corona danesa', 'de': 'Dänische Krone'},
        'Couronne norvégienne': {'en': 'Norwegian Krone', 'en-us': 'Norwegian Krone', 'es': 'Corona noruega', 'de': 'Norwegische Krone'},
        'Couronne islandaise': {'en': 'Icelandic Krona', 'en-us': 'Icelandic Krona', 'es': 'Corona islandesa', 'de': 'Isländische Krone'},
        'Couronne tchèque': {'en': 'Czech Koruna', 'en-us': 'Czech Koruna', 'es': 'Corona checa', 'de': 'Tschechische Krone'},
        'Forint hongrois': {'en': 'Hungarian Forint', 'en-us': 'Hungarian Forint', 'es': 'Forinto húngaro', 'de': 'Ungarischer Forint'},
        'Zloty polonais': {'en': 'Polish Zloty', 'en-us': 'Polish Zloty', 'es': 'Zloty polaco', 'de': 'Polnischer Zloty'},
        'Rouble': {'en': 'Ruble', 'en-us': 'Ruble', 'es': 'Rublo', 'de': 'Rubel'},
        'Roupie indienne': {'en': 'Indian Rupee', 'en-us': 'Indian Rupee', 'es': 'Rupia india', 'de': 'Indische Rupie'},
        'Rupiah indonésienne': {'en': 'Indonesian Rupiah', 'en-us': 'Indonesian Rupiah', 'es': 'Rupia indonesia', 'de': 'Indonesische Rupiah'},
        'Baht thaïlandais': {'en': 'Thai Baht', 'en-us': 'Thai Baht', 'es': 'Baht tailandés', 'de': 'Thailändischer Baht'},
        'Dong vietnamien': {'en': 'Vietnamese Dong', 'en-us': 'Vietnamese Dong', 'es': 'Dong vietnamita', 'de': 'Vietnamesischer Dong'},
        'Ringgit malaisien': {'en': 'Malaysian Ringgit', 'en-us': 'Malaysian Ringgit', 'es': 'Ringgit malayo', 'de': 'Malaysischer Ringgit'},
        'Won sud-coréen': {'en': 'South Korean Won', 'en-us': 'South Korean Won', 'es': 'Won surcoreano', 'de': 'Südkoreanischer Won'},
        'Peso mexicain': {'en': 'Mexican Peso', 'en-us': 'Mexican Peso', 'es': 'Peso mexicano', 'de': 'Mexikanischer Peso'},
        'Real brésilien': {'en': 'Brazilian Real', 'en-us': 'Brazilian Real', 'es': 'Real brasileño', 'de': 'Brasilianischer Real'},
        'Peso argentin': {'en': 'Argentine Peso', 'en-us': 'Argentine Peso', 'es': 'Peso argentino', 'de': 'Argentinischer Peso'},
        'Peso chilien': {'en': 'Chilean Peso', 'en-us': 'Chilean Peso', 'es': 'Peso chileno', 'de': 'Chilenischer Peso'},
        'Bolívar': {'en': 'Bolívar', 'en-us': 'Bolívar', 'es': 'Bolívar', 'de': 'Bolívar'},
        'Dinar irakien': {'en': 'Iraqi Dinar', 'en-us': 'Iraqi Dinar', 'es': 'Dinar iraquí', 'de': 'Irakischer Dinar'},
        'Dinar libyen': {'en': 'Libyan Dinar', 'en-us': 'Libyan Dinar', 'es': 'Dinar libio', 'de': 'Libyscher Dinar'},
        'Dobra': {'en': 'Dobra', 'en-us': 'Dobra', 'es': 'Dobra', 'de': 'Dobra'},
        'Dollar de Brunéi': {'en': 'Brunei Dollar', 'en-us': 'Brunei Dollar', 'es': 'Dólar de Brunéi', 'de': 'Brunei-Dollar'},
        'Dollar des Caraïbes orientales': {'en': 'East Caribbean Dollar', 'en-us': 'East Caribbean Dollar', 'es': 'Dólar del Caribe Oriental', 'de': 'Ostkaribischer Dollar'},
        'Dollar des Îles Salomon': {'en': 'Solomon Islands Dollar', 'en-us': 'Solomon Islands Dollar', 'es': 'Dólar de las Islas Salomón', 'de': 'Salomonen-Dollar'},
        'Dollar du Guyana': {'en': 'Guyanese Dollar', 'en-us': 'Guyanese Dollar', 'es': 'Dólar guyanés', 'de': 'Guyana-Dollar'},
        'Dollar libérien': {'en': 'Liberian Dollar', 'en-us': 'Liberian Dollar', 'es': 'Dólar liberiano', 'de': 'Liberianischer Dollar'},
        'Dollar surinamais': {'en': 'Surinamese Dollar', 'en-us': 'Surinamese Dollar', 'es': 'Dólar surinamés', 'de': 'Suriname-Dollar'},
        'Franc CFA (BCEAO)': {'en': 'West African CFA Franc', 'en-us': 'West African CFA Franc', 'es': 'Franco CFA (BCEAO)', 'de': 'CFA-Franc (BCEAO)'},
        'Franc CFA (BEAC)': {'en': 'Central African CFA Franc', 'en-us': 'Central African CFA Franc', 'es': 'Franco CFA (BEAC)', 'de': 'CFA-Franc (BEAC)'},
        'Franc burundais': {'en': 'Burundian Franc', 'en-us': 'Burundian Franc', 'es': 'Franco burundés', 'de': 'Burundi-Franc'},
        'Franc comorien': {'en': 'Comorian Franc', 'en-us': 'Comorian Franc', 'es': 'Franco comorense', 'de': 'Komoren-Franc'},
        'Franc congolais': {'en': 'Congolese Franc', 'en-us': 'Congolese Franc', 'es': 'Franco congoleño', 'de': 'Kongo-Franc'},
        'Franc djiboutien': {'en': 'Djiboutian Franc', 'en-us': 'Djiboutian Franc', 'es': 'Franco yibutiano', 'de': 'Dschibuti-Franc'},
        'Franc guinéen': {'en': 'Guinean Franc', 'en-us': 'Guinean Franc', 'es': 'Franco guineano', 'de': 'Guinea-Franc'},
        'Gourde': {'en': 'Gourde', 'en-us': 'Gourde', 'es': 'Gourde', 'de': 'Gourde'},
        'Kwanza': {'en': 'Kwanza', 'en-us': 'Kwanza', 'es': 'Kwanza', 'de': 'Kwanza'},
        'Leu moldave': {'en': 'Moldovan Leu', 'en-us': 'Moldovan Leu', 'es': 'Leu moldavo', 'de': 'Moldauischer Leu'},
        'Lilangeni': {'en': 'Lilangeni', 'en-us': 'Lilangeni', 'es': 'Lilangeni', 'de': 'Lilangeni'},
        'Livre soudanaise': {'en': 'Sudanese Pound', 'en-us': 'Sudanese Pound', 'es': 'Libra sudanesa', 'de': 'Sudanesisches Pfund'},
        'Livre sud-soudanaise': {'en': 'South Sudanese Pound', 'en-us': 'South Sudanese Pound', 'es': 'Libra sursudanesa', 'de': 'Südsudanesisches Pfund'},
        'Livre syrienne': {'en': 'Syrian Pound', 'en-us': 'Syrian Pound', 'es': 'Libra siria', 'de': 'Syrisches Pfund'},
        'Loti': {'en': 'Loti', 'en-us': 'Loti', 'es': 'Loti', 'de': 'Loti'},
        'Manat turkmène': {'en': 'Turkmen Manat', 'en-us': 'Turkmen Manat', 'es': 'Manat turcomano', 'de': 'Turkmenischer Manat'},
        'Nakfa': {'en': 'Nakfa', 'en-us': 'Nakfa', 'es': 'Nakfa', 'de': 'Nakfa'},
        'Ouguiya': {'en': 'Ouguiya', 'en-us': 'Ouguiya', 'es': 'Uguiya', 'de': 'Ouguiya'},
        'Rouble biélorusse': {'en': 'Belarusian Ruble', 'en-us': 'Belarusian Ruble', 'es': 'Rublo bielorruso', 'de': 'Belarussischer Rubel'},
        'Roupie pakistanaise': {'en': 'Pakistani Rupee', 'en-us': 'Pakistani Rupee', 'es': 'Rupia pakistaní', 'de': 'Pakistanische Rupie'},
        'Shilling somalien': {'en': 'Somali Shilling', 'en-us': 'Somali Shilling', 'es': 'Chelín somalí', 'de': 'Somalia-Schilling'},
        'Taka': {'en': 'Taka', 'en-us': 'Taka', 'es': 'Taka', 'de': 'Taka'},
        'Sol péruvien': {'en': 'Peruvian Sol', 'en-us': 'Peruvian Sol', 'es': 'Sol peruano', 'de': 'Peruanischer Sol'},
        'Rand sud-africain': {'en': 'South African Rand', 'en-us': 'South African Rand', 'es': 'Rand sudafricano', 'de': 'Südafrikanischer Rand'},
        'Dirham marocain': {'en': 'Moroccan Dirham', 'en-us': 'Moroccan Dirham', 'es': 'Dirham marroquí', 'de': 'Marokkanischer Dirham'},
        'Dinar tunisien': {'en': 'Tunisian Dinar', 'en-us': 'Tunisian Dinar', 'es': 'Dinar tunecino', 'de': 'Tunesischer Dinar'},
        'Livre égyptienne': {'en': 'Egyptian Pound', 'en-us': 'Egyptian Pound', 'es': 'Libra egipcia', 'de': 'Ägyptisches Pfund'},
        'Lira turque': {'en': 'Turkish Lira', 'en-us': 'Turkish Lira', 'es': 'Lira turca', 'de': 'Türkische Lira'},
        'Shekel': {'en': 'Shekel', 'en-us': 'Shekel', 'es': 'Shekel', 'de': 'Schekel'},
        'Dirham émirati': {'en': 'UAE Dirham', 'en-us': 'UAE Dirham', 'es': 'Dirham emiratí', 'de': 'VAE-Dirham'},
        'Kuna croate': {'en': 'Croatian Kuna', 'en-us': 'Croatian Kuna', 'es': 'Kuna croata', 'de': 'Kroatische Kuna'},
        'Leu roumain': {'en': 'Romanian Leu', 'en-us': 'Romanian Leu', 'es': 'Leu rumano', 'de': 'Rumänischer Leu'},
    }
    if lang in ('en', 'en-us', 'es', 'de') and currency_name in CUR_NAME_I18N:
        currency_name = CUR_NAME_I18N[currency_name].get(lang, currency_name)
    currency_symbol = cinfo.get('currency_symbol', '')
    drive = cinfo.get('drive', 'right')
    gpi_level = _safe_int(cinfo.get('risk_level'))
    gpi_value = _safe_float(cinfo.get('gpi'))
    cost_tier = _safe_int(cinfo.get('budget_index'))
    cost_value = _safe_float(cinfo.get('budget_numbeo_col'))

    # Trend value
    trend_value = _compute_trend_value(slug=dest.get('slug_fr', slug),
                                       lat=lat, lon=lon)
    trend_significant = _trend_is_significant(slug=dest.get('slug_fr', slug),
                                              lat=lat, lon=lon)

    # Climate extremes
    extremes = _extract_climate_extremes(months_climate, months_loc=MONTHS_LOC)

    # ── Hero data ──
    is_mountain = _bool(dest.get('mountain'))
    is_tropical = _bool(dest.get('tropical'))

    # H1 accent part (variable selon profil)
    if is_mountain:
        h1_accent = 'pour skier ou randonner' if lang == 'fr' else (
            'for skiing or hiking' if lang in ('en', 'en-us') else
            'para esquiar o senderismo' if lang == 'es' else 'zum Skifahren oder Wandern'
        )
    else:
        h1_accent = 'pour partir' if lang == 'fr' else (
            'to visit' if lang in ('en', 'en-us') else
            'para visitar' if lang == 'es' else 'zum Reisen'
        )

    # Decision card lead (best/worst auto)
    gap = best['score_10'] - worst['score_10']
    if lang == 'fr':
        if is_mountain:
            lead_html = (f'En montagne, deux univers : hiver pour le ski, été pour la randonnée. '
                         f'<strong>{best["mois"]}</strong> sort en tête ({best["score_10"]:.1f}/10), '
                         f'{worst["mois"]} reste le plus rude ({worst["score_10"]:.1f}/10). '
                         f'Écart de {gap:.1f} points entre les deux.')
        else:
            lead_html = (f'<strong>{best["mois"]}</strong> sort en tête ({best["score_10"]:.1f}/10), '
                         f'{worst["mois"]} reste le plus rude ({worst["score_10"]:.1f}/10). '
                         f'Écart de {gap:.1f} points entre les deux.')
    else:
        # Pour les autres langues, on utilise les templates de locales/v6
        # Note : pour la V1 on peut garder le FR ou utiliser un fallback simple.
        # L'orchestrateur appellera render_v6_decision_card qui formatera depuis le hero_data['lead']
        lead_html = (f'<strong>{best["mois"]}</strong> ({best["score_10"]:.1f}/10) · '
                     f'{worst["mois"]} ({worst["score_10"]:.1f}/10).')

    # Mini-cards selon profil
    if is_mountain:
        # Recherche meilleur ski (déc-mai) et meilleure rando (juin-sept)
        ski_months_idx = [11, 0, 1, 2, 3, 4]   # Déc, Jan, Fev, Mar, Avr, Mai
        rando_months_idx = [5, 6, 7, 8]         # Juin, Juil, Aoû, Sep
        ski_best = max((months_data[i] for i in ski_months_idx if i < 12),
                       key=lambda m: m['score_10'], default=None)
        rando_best = max((months_data[i] for i in rando_months_idx if i < 12),
                         key=lambda m: m['score_10'], default=None)
        # Mois de transition = 1 des "mid"
        transition = next((m for m in months_data if m['classe'] == 'mid'), None)
        mini_cards = []
        if ski_best:
            mini_cards.append({'value': f'⛷️ {ski_best["mois"][:3]}',
                               'label': f'Top ski ({ski_best["score_10"]:.1f}/10)'})
        if rando_best:
            mini_cards.append({'value': f'🥾 {rando_best["mois"][:3]}',
                               'label': f'Top rando ({rando_best["score_10"]:.1f}/10)'})
        if transition:
            mini_cards.append({'value': transition['mois'], 'label': 'Transition'})
        # Garantir 3 cartes max
        mini_cards = mini_cards[:3]
        # Header décision : "Mois ski · Mois rando" et score = max
        if ski_best and rando_best:
            decision_main_month = f'{ski_best["mois"][:3]} · {rando_best["mois"][:3]}'
            decision_main_score = f'{max(ski_best["score_10"], rando_best["score_10"]):.1f}'
        else:
            decision_main_month = best['mois']
            decision_main_score = f'{best["score_10"]:.1f}'
    else:
        # Standard : top 1 + top 2 + worst
        top2 = sorted_by_score[1] if len(sorted_by_score) > 1 else best
        mini_cards = [
            {'value': f'☀️ {best["mois"][:3]}', 'label': f'Top score ({best["score_10"]:.1f}/10)'},
            {'value': f'🌤️ {top2["mois"][:3]}', 'label': f'Alt. ({top2["score_10"]:.1f}/10)'},
            {'value': worst['mois'][:3], 'label': f'Plus rude ({worst["score_10"]:.1f}/10)'},
        ]
        decision_main_month = best['mois']
        decision_main_score = f'{best["score_10"]:.1f}'

    # Chips climat (heuristique simple selon profil) — localisés selon lang
    HERO_CHIPS_I18N = {
        'mountain': {
            'fr':    [('❄️', 'Climat alpin', 'blue'),     ('☀️', 'UV altitude', 'gold'),    ('🌦️', 'Météo changeante', 'purple')],
            'en':    [('❄️', 'Alpine climate', 'blue'),    ('☀️', 'High-altitude UV', 'gold'),('🌦️', 'Changeable weather', 'purple')],
            'en-us': [('❄️', 'Alpine climate', 'blue'),    ('☀️', 'High-altitude UV', 'gold'),('🌦️', 'Changeable weather', 'purple')],
            'es':    [('❄️', 'Clima alpino', 'blue'),      ('☀️', 'UV altitud', 'gold'),     ('🌦️', 'Tiempo cambiante', 'purple')],
            'de':    [('❄️', 'Alpenklima', 'blue'),        ('☀️', 'UV in Höhe', 'gold'),     ('🌦️', 'Wechselhaftes Wetter', 'purple')],
        },
        'tropical': {
            'fr':    [('🌴', 'Tropical', 'green'),         ('☀️', 'UV élevé', 'gold'),       ('🌧️', 'Mousson saison', 'blue')],
            'en':    [('🌴', 'Tropical', 'green'),         ('☀️', 'High UV', 'gold'),         ('🌧️', 'Monsoon season', 'blue')],
            'en-us': [('🌴', 'Tropical', 'green'),         ('☀️', 'High UV', 'gold'),         ('🌧️', 'Monsoon season', 'blue')],
            'es':    [('🌴', 'Tropical', 'green'),         ('☀️', 'UV alto', 'gold'),         ('🌧️', 'Temporada monzón', 'blue')],
            'de':    [('🌴', 'Tropisch', 'green'),         ('☀️', 'Hoher UV', 'gold'),        ('🌧️', 'Monsunzeit', 'blue')],
        },
        'polar': {
            'fr':    [('❄️', 'Subarctique', 'blue'),       ('🌌', 'Aurores', 'purple'),      ('🌬️', 'Vents fréquents', 'gold')],
            'en':    [('❄️', 'Subarctic', 'blue'),         ('🌌', 'Auroras', 'purple'),       ('🌬️', 'Frequent winds', 'gold')],
            'en-us': [('❄️', 'Subarctic', 'blue'),         ('🌌', 'Auroras', 'purple'),       ('🌬️', 'Frequent winds', 'gold')],
            'es':    [('❄️', 'Subártico', 'blue'),         ('🌌', 'Auroras', 'purple'),       ('🌬️', 'Vientos frecuentes', 'gold')],
            'de':    [('❄️', 'Subarktisch', 'blue'),       ('🌌', 'Polarlichter', 'purple'),  ('🌬️', 'Häufige Winde', 'gold')],
        },
        'coastal': {
            'fr':    [('🌊', 'Bord de mer', 'blue'),       ('☀️', 'Lumineux', 'gold'),        ('🍴', 'Gastronomie', 'red')],
            'en':    [('🌊', 'Seaside', 'blue'),           ('☀️', 'Bright', 'gold'),          ('🍴', 'Gastronomy', 'red')],
            'en-us': [('🌊', 'Seaside', 'blue'),           ('☀️', 'Bright', 'gold'),          ('🍴', 'Gastronomy', 'red')],
            'es':    [('🌊', 'Costa', 'blue'),             ('☀️', 'Luminoso', 'gold'),        ('🍴', 'Gastronomía', 'red')],
            'de':    [('🌊', 'Meeresnähe', 'blue'),        ('☀️', 'Lichtreich', 'gold'),      ('🍴', 'Gastronomie', 'red')],
        },
        'city': {
            'fr':    [('🏛️', 'Patrimoine', 'gold'),        ('🌧️', 'Pluies modérées', 'blue'),('☔', 'Visites couvertes', 'purple')],
            'en':    [('🏛️', 'Heritage', 'gold'),           ('🌧️', 'Moderate rain', 'blue'),    ('☔', 'Indoor sights', 'purple')],
            'en-us': [('🏛️', 'Heritage', 'gold'),           ('🌧️', 'Moderate rain', 'blue'),    ('☔', 'Indoor sights', 'purple')],
            'es':    [('🏛️', 'Patrimonio', 'gold'),         ('🌧️', 'Lluvias moderadas', 'blue'),('☔', 'Visitas cubiertas', 'purple')],
            'de':    [('🏛️', 'Kulturerbe', 'gold'),         ('🌧️', 'Moderater Regen', 'blue'),  ('☔', 'Indoor-Sehensw.', 'purple')],
        },
    }
    profile_chips = HERO_CHIPS_I18N.get(profile, HERO_CHIPS_I18N['city'])
    triplets = profile_chips.get(lang, profile_chips['fr'])
    chips = [{'emoji': e, 'text': t, 'color': c} for e, t, c in triplets]

    hero_data = {
        'dest_name': nom,
        'country_name': country_name,
        'country_iso': country_iso,
        'climate_type': climate_type,
        'photo_url': photo_url,
        'photo_credit': photo_credit,
        'is_mountain': is_mountain,
        'update_month': update_month,
        'lat': lat,
        'lon': lon,
        'lead': lead_html,
        'h1_accent_part': h1_accent,
        'decision_main_month': decision_main_month,
        'decision_main_score': decision_main_score,
        'mini_cards': mini_cards,
        'chips': chips,
    }

    # ── Infos pratiques data ──
    infos_pratiques_data = {
        'dest_name': nom,
        'country_name': country_name,
        'country_iso': country_iso,
        'lang_local': lang_local,
        'currency_name': currency_name,
        'currency_symbol': currency_symbol,
        'drive': drive,
        'gpi_level': gpi_level,
        'gpi_value': gpi_value,
        'cost_tier': cost_tier,
        'cost_value': cost_value,
        'climate_type': climate_type,
        'trend_value': trend_value,
        'trend_significant': trend_significant,
        'is_mountain': is_mountain,
        'is_coastal': _bool(dest.get('coastal')),
        'is_tropical': is_tropical,
        'is_polar': profile == 'polar',
        # Visa : uniquement pour les pays de l'espace Schengen (source: Commission
        # UE, 29 pays au 01/01/2025). Ailleurs, le visa dépend de la nationalité
        # du lecteur — is_schengen=False -> la ligne est masquée plutôt que
        # d'afficher un 'Schengen · 90j' faux (ex-fallback appliqué à ~516
        # destinations hors zone, dont Turkménistan, Irak, Chine...).
        'is_schengen': dest.get('pays', '') in _SCHENGEN_COUNTRIES,
        **extremes,  # hottest_month, hottest_temp, coldest_month, coldest_temp, rainiest_month, rainiest_pct
    }

    # Profil-specific Box 3 fields
    if is_mountain:
        # Charger ski_altitudes.csv pour cette destination
        ski_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'ski_altitudes.csv')
        try:
            import csv as _csv
            with open(ski_path, encoding='utf-8') as f:
                for row in _csv.DictReader(f):
                    if row.get('slug') == dest.get('slug_fr'):
                        infos_pratiques_data['alt_village'] = _safe_int(row.get('alt_village'))
                        infos_pratiques_data['alt_ski_max'] = _safe_int(row.get('alt_ski_max'))
                        break
        except FileNotFoundError:
            pass
        # i18n des saisons (FR/EN/EN-US/ES/DE)
        SEASON_MTN = {
            'fr': ('Déc → Mai', 'Juin → Sept'),
            'en': ('Dec → May', 'Jun → Sep'),
            'en-us': ('Dec → May', 'Jun → Sep'),
            'es': ('Dic → May', 'Jun → Sep'),
            'de': ('Dez → Mai', 'Jun → Sep'),
        }
        ski_s, hike_s = SEASON_MTN.get(lang, SEASON_MTN['fr'])
        infos_pratiques_data['ski_season'] = ski_s
        infos_pratiques_data['hiking_season'] = hike_s
    elif is_tropical:
        SEASON_TROP = {
            'fr': ('Mai → Sept', 'Déc → Mars'),
            'en': ('May → Sep', 'Dec → Mar'),
            'en-us': ('May → Sep', 'Dec → Mar'),
            'es': ('May → Sep', 'Dic → Mar'),
            'de': ('Mai → Sep', 'Dez → Mär'),
        }
        dry_s, wet_s = SEASON_TROP.get(lang, SEASON_TROP['fr'])
        infos_pratiques_data['dry_season'] = dry_s
        infos_pratiques_data['wet_season'] = wet_s
        infos_pratiques_data['has_cyclones'] = abs(lat) > 10
        infos_pratiques_data['latitude'] = lat
        # Sea temps (à enrichir plus tard depuis climate.csv si colonne sea_temp)
    elif profile == 'polar':
        infos_pratiques_data['latitude'] = lat
        infos_pratiques_data['has_geothermal'] = country_name.lower() in ('islande', 'iceland', 'islandia', 'island')

    # ── Construction page_data ──
    canonical_path = f'{cfg["annual_prefix"]}{slug}{cfg["annual_suffix"]}'
    # Strip .html (worker serves URLs without extension, avoids GSC "page with redirect")
    if canonical_path.endswith('.html'):
        canonical_path = canonical_path[:-5]
    canonical_url = f'{cfg.get("canonical_prefix", "")}{canonical_path}'

    # Page title : utilise les annual_titles V5 (rotation déterministe par slug
    # pour éviter le pattern uniforme suspect de SEO)
    annual_titles = cfg.get('annual_titles', []) or []
    title_idx = abs(hash(dest.get('slug_fr', slug))) % len(annual_titles) if annual_titles else 0
    title_tpl = annual_titles[title_idx] if annual_titles else '{nom_bare} : meilleurs mois'

    from datetime import datetime
    year = datetime.now().year

    title_vars = {
        'nom_bare': dest.get('nom_bare', nom),
        'nom': nom,
        'prep': dest.get(f'prep_{lang[:2]}', dest.get('prep_fr', 'à')),
        'best_score': f'{best["score_10"]:.1f}',
        'best_month': best['mois'],
        'year': year,
    }
    try:
        page_title = title_tpl.format(**title_vars)
    except (KeyError, IndexError):
        page_title = f'{nom} : meilleurs mois'

    # ── Meta description ────────────────────────────────────────────────
    # Objectif CTR : les 754 descriptions partageaient un gabarit identique
    # ("X (N/10) is the standout... 10-year ERA5 climate data"), centré sur un
    # score abstrait et du jargon. Résultat : 0,17% de CTR global, 779 des
    # 1000 premières requêtes à zéro clic. On donne désormais les chiffres que
    # l'internaute cherche (température, pluie, ensoleillement) et une
    # recommandation en clair, ce qui différencie aussi chaque destination.
    def _fmt_t(v, us=False):
        return f'{round(v * 9 / 5 + 32)}°F' if us else f'{round(v)}°C'

    _us = (lang == 'en-us')
    _bt = _fmt_t(best.get('tmax') or 0, _us)
    _br = round(best.get('rain_pct') or 0)
    # Raison du mois à éviter : on cite le facteur réellement discriminant
    # (pluie si mois très pluvieux, sinon chaleur ou froid), sinon la mention
    # n'explique rien (ex. « éviter août, 31°C » quand le meilleur est à 29°C).
    _wtmax = worst.get('tmax') or 0
    _wrain = round(worst.get('rain_pct') or 0)
    _rain_driven = _wrain >= 40 and _wrain > (round(best.get('rain_pct') or 0) + 15)
    _WHY = {
        'fr': (f'{_wrain}% de jours de pluie' if _rain_driven else _fmt_t(_wtmax, _us)),
        'en': (f'{_wrain}% rainy days' if _rain_driven else _fmt_t(_wtmax, _us)),
        'es': (f'{_wrain}% de días de lluvia' if _rain_driven else _fmt_t(_wtmax, _us)),
        'de': (f'{_wrain}% Regentage' if _rain_driven else _fmt_t(_wtmax, _us)),
    }
    _wt = _WHY.get('en' if lang in ('en', 'en-us') else lang, _WHY['en'])
    _bsun = best.get('sun_h') or 0

    if lang == 'fr':
        page_desc = (f'{best["mois"]} est le meilleur mois à {nom} : {_bt} en journée, '
                     f'{_br}% de jours de pluie. '
                     f'{worst["mois"]} est à éviter ({_wt}). Les 12 mois comparés.')
    elif lang in ('en', 'en-us'):
        page_desc = (f'{best["mois"]} is the best month in {nom}: {_bt} by day, '
                     f'{_br}% rainy days. '
                     f'{worst["mois"]} is the one to avoid ({_wt}). All 12 months compared.')
    elif lang == 'es':
        page_desc = (f'{best["mois"]} es el mejor mes en {nom}: {_bt} de día, '
                     f'{_br}% de días de lluvia. '
                     f'{worst["mois"]} es el mes a evitar ({_wt}). Los 12 meses comparados.')
    elif lang == 'de':
        page_desc = (f'{best["mois"]} ist der beste Monat in {nom}: {_bt} tagsüber, '
                     f'{_br}% Regentage. '
                     f'{worst["mois"]} sollte man meiden ({_wt}). Alle 12 Monate im Vergleich.')
    else:
        page_desc = f'{nom}: {best["mois"]} best ({_bt}), {worst["mois"]} worst.'

    return {
        'lang': lang,
        'slug': slug,
        'slug_fr': dest.get('slug_fr', slug),
        'slug_en': dest.get('slug_en', ''),
        'slug_es': dest.get('slug_es', ''),
        'slug_de': dest.get('slug_de', ''),
        'dest_name': nom,
        'page_title': page_title,
        'page_desc': page_desc,
        'canonical_url': canonical_url,
        'asset_prefix': cfg.get('asset_prefix', ''),
        'lat': lat, 'lon': lon,
        'is_mountain': is_mountain,
        'profile': profile,
        'months_data': months_data,
        'monthly_url_tpl': monthly_url_tpl,
        'edito_html': editorial_html or '<p>—</p>',
        'hero_data': hero_data,
        'infos_pratiques_data': infos_pratiques_data,
        'faq_items': [],  # à enrichir avec generation FAQ depuis données
        'related': [],    # à enrichir avec similarities V5
    }


# ─────────────────────────────────────────────────────────────────────────────
# Entry point principal : gen_annual_v6
# ─────────────────────────────────────────────────────────────────────────────

# Espace Schengen — 29 pays (Commission européenne, dernière extension
# Bulgarie + Roumanie le 01/01/2025). 25 UE + 4 non-UE (Islande, Norvège,
# Suisse, Liechtenstein). Chypre et Irlande sont UE mais HORS Schengen.
# Sert à n'afficher la ligne "Visa" que là où "Schengen · 90j" est vrai.
_SCHENGEN_COUNTRIES = frozenset({
    'Allemagne', 'Autriche', 'Belgique', 'Bulgarie', 'Croatie', 'Danemark',
    'Espagne', 'Estonie', 'Finlande', 'France', 'Grèce', 'Hongrie', 'Islande',
    'Italie', 'Lettonie', 'Liechtenstein', 'Lituanie', 'Luxembourg', 'Malte',
    'Norvège', 'Pays-Bas', 'Pologne', 'Portugal', 'Roumanie', 'Slovaquie',
    'Slovénie', 'Suède', 'Suisse', 'Tchéquie',
})


def gen_annual_v6(cfg: dict, fn, dest: dict, months: list,
                  dest_cards=None, all_dests=None,
                  similarities=None, comparison_index=None) -> str:
    """Version V6 de gen_annual(). Retourne le HTML complet de la fiche annuelle.

    Signature compatible avec gen_annual() V5 pour pouvoir être branché
    facilement dans le main loop avec un simple dispatch sur le flag --v6.

    Args:
        cfg: config langue depuis build_config(lang)
        fn: bound translation function depuis _bind_lang(cfg)
        dest: ligne destinations.csv
        months: 12 dicts climate.csv pour cette destination
        dest_cards: ignoré pour V1 V6 (sera utilisé pour FAQ enrichie)
        all_dests: dict {slug: dest} pour cross-links (utilisé pour related)
        similarities: dict de similarités pré-calculées (V5 input)
        comparison_index: index comparatifs (V5 input)

    Returns:
        HTML complet de la page V6.
    """
    from lib.page_config import (dest_slug, dest_name, dest_country,
                                  dest_name_full, build_hreflang_tags,
                                  date_modified_for, month_lc)
    from lib.common import fill_tpl
    from scoring import compute_scores, compute_mountain_scores

    slug = dest_slug(cfg, dest)
    nom = dest_name(cfg, dest)
    nom_bare = dest.get('nom_bare', nom)
    prep = dest.get(f'prep_{cfg["lang"][:2]}', dest.get('prep_fr', 'à'))
    country_name = dest_country(cfg, dest)
    country_iso = _flag_iso(dest.get('flag', ''))

    is_mountain = _bool(dest.get('mountain'))
    slug_fr_canonical = dest.get('slug_fr', slug)

    # Calcul scores
    months_input = []
    for m in months:
        months_input.append({
            'cls': m.get('classe', m.get('class', 'mid')),  # CSV uses 'classe'
            'tmax': _safe_float(m.get('tmax')),
            'rain_pct': _safe_float(m.get('rain_pct')),
            'sun_h': _safe_float(m.get('sun_h')),
            'month': m.get('mois', ''),
        })

    if is_mountain:
        scores = compute_mountain_scores(months_input, slug=slug_fr_canonical)
    else:
        scores = compute_scores(months_input, slug=slug_fr_canonical)

    # URL templates — sans .html pour les liens internes (worker sert sans extension)
    # 19 destinations ont monthly=False (exclusion volontaire, destinations.csv):
    # leurs fiches mensuelles n'existent pas -> pas de template = le tableau des
    # 12 mois n'est pas rendu cliquable (sinon 12 liens 404 par langue).
    _has_monthly = str(dest.get('monthly', 'True')).strip().lower() in ('true', '1', 'yes', '')
    monthly_url_tpl = f'{slug}{cfg["monthly_sep"]}{{mois_lower}}' if _has_monthly else None

    # Edito annuel
    avis_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'avis_annuel.json')
    avis = _load_json_cached(avis_path)
    edito_key_lang = f'{slug_fr_canonical}:{cfg["lang"]}'
    edito_key_fr = f'{slug_fr_canonical}:fr'
    editorial_html = avis.get(edito_key_lang) or avis.get(edito_key_fr) or ''
    if editorial_html and not editorial_html.startswith('<'):
        editorial_html = f'<p>{editorial_html}</p>'

    # Photo Unsplash
    photo = dest.get('_photo', {})
    photo_url = photo.get('url', '')
    photo_credit_html = ''
    if photo.get('credit_name') and photo.get('credit_url'):
        photo_credit_html = (
            f'<a href="{photo["credit_url"]}" target="_blank" '
            f'rel="noopener nofollow">{photo["credit_name"]}</a> via Unsplash'
        )

    # Update month
    from datetime import datetime
    current_month_idx = datetime.now().month - 1
    update_month = cfg['months'][current_month_idx]

    # Build page_data
    page_data = build_page_data_v6(
        cfg=cfg,
        dest=dest,
        months_climate=months,
        months_with_scores=scores,
        slug=slug,
        nom=nom,
        country_name=country_name,
        country_iso=country_iso,
        monthly_url_tpl=monthly_url_tpl,
        editorial_html=editorial_html,
        photo_url=photo_url,
        photo_credit=photo_credit_html,
        update_month=update_month,
    )

    # ── Enrichissements Phase 3 : SEO + FAQ ──

    # 1. Hreflang tags
    page_data['hreflang_tags'] = build_hreflang_tags(dest, mi=None)

    # 2. FAQ items depuis les templates V5 (annual_faq_mountain / annual_faq_standard)
    page_data['faq_items'] = _build_faq_items(cfg, dest, months, scores,
                                              is_mountain, slug_fr_canonical,
                                              prep, nom, nom_bare)

    # 3. JSON-LD blocks (Article + FAQPage)
    page_data['json_ld_blocks'] = _build_json_ld_blocks(
        cfg=cfg, dest=dest, slug=slug, nom=nom,
        page_title=page_data['page_title'],
        page_desc=page_data['page_desc'],
        canonical_url=page_data['canonical_url'],
        faq_items=page_data['faq_items'],
    )

    # 4. og:image (si pas de photo Unsplash, fallback sur og-image.png)
    page_data['og_image_url'] = photo_url or 'https://bestdateweather.com/og-image.png'

    # 5. Related destinations (cross-links interne SEO)
    page_data['related'] = _build_related_v6(cfg, dest, similarities, all_dests)

    html = render_v6_full_page(page_data)
    # Post-traitement : retirer .html des liens internes (footer, cross-lang, related...)
    from lib.page_config import strip_html_from_internal_links
    return strip_html_from_internal_links(html)


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Distance grand cercle en km entre 2 points GPS (formule haversine)."""
    import math
    R = 6371.0  # rayon terre en km
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam/2)**2
    return 2 * R * math.asin(math.sqrt(a))


def _build_related_v6(cfg: dict, dest: dict, similarities: dict | None,
                      all_dests: dict | None) -> dict:
    """Construit les listes related pour la section Explorer.

    Retourne dict avec 2 clés:
    - 'climate': top 4 dest similaires en climat (cosine sim tmax/rain/sun)
    - 'proximity': top 4 dest géographiquement proches (haversine, exclut dest courante)

    Format chaque item: {href, name, country, country_iso, distance_km (proximity only)}
    """
    result = {'climate': [], 'proximity': []}
    if not all_dests:
        return result

    slug_fr_canonical = dest.get('slug_fr', '')
    lang = cfg['lang']

    def _build_item(other: dict, distance_km: float | None = None) -> dict:
        slug_lang = other.get(f'slug_{lang[:2]}', other.get('slug_fr', ''))
        href = f'{cfg["annual_prefix"]}{slug_lang}{cfg["annual_suffix"]}'
        name = other.get(f'nom_{lang[:2]}', other.get('nom_fr', slug_lang.title()))
        country = other.get(f'country_{lang[:2]}', other.get('pays', ''))
        country_iso = other.get('flag', '').lower().strip()
        item = {'href': href, 'name': name, 'country': country, 'country_iso': country_iso}
        if distance_km is not None:
            item['distance_km'] = round(distance_km)
        return item

    # ── Climat similaire ──
    if similarities:
        sims = similarities.get(slug_fr_canonical, [])
        for score, other_slug in sims[:4]:
            other = all_dests.get(other_slug)
            if other:
                result['climate'].append(_build_item(other))

    # ── Proximité géographique ──
    try:
        cur_lat = float(dest.get('lat', 0))
        cur_lon = float(dest.get('lon', 0))
    except (TypeError, ValueError):
        cur_lat = cur_lon = 0
    if cur_lat or cur_lon:
        candidates = []
        for other_slug, other in all_dests.items():
            if other_slug == slug_fr_canonical:
                continue
            try:
                olat = float(other.get('lat', 0))
                olon = float(other.get('lon', 0))
            except (TypeError, ValueError):
                continue
            if not (olat or olon):
                continue
            d = _haversine_km(cur_lat, cur_lon, olat, olon)
            candidates.append((d, other_slug, other))
        # Trier par distance asc, prendre top 4 (mais éviter mêmes que climat)
        candidates.sort(key=lambda c: c[0])
        already_in_climate = {item['name'] for item in result['climate']}
        for distance, other_slug, other in candidates:
            if len(result['proximity']) >= 4:
                break
            item = _build_item(other, distance_km=distance)
            if item['name'] in already_in_climate:
                continue
            result['proximity'].append(item)

    return result


# ─────────────────────────────────────────────────────────────────────────────
# Helpers Phase 3 : FAQ + JSON-LD
# ─────────────────────────────────────────────────────────────────────────────

def _build_faq_items(cfg: dict, dest: dict, months: list, scores: list,
                     is_mountain: bool, slug_fr: str,
                     prep: str, nom: str, nom_bare: str) -> list[dict]:
    """Génère la liste des FAQ items {q, a} en réutilisant les templates V5.

    Templates dans cfg['annual_faq_mountain'] / cfg['annual_faq_standard'].
    Les variables (best_month, best_tmax, etc.) sont calculées ici depuis
    months + scores.
    """
    from lib.common import fill_tpl
    from lib.page_config import month_lc
    from scoring import compute_ski_score
    from lib.common import _ski_kwargs

    MONTHS = cfg['months']

    # Indexes triés par score
    score_by_idx = {i: _safe_float(scores[i].get('score_10', scores[i].get('score', 0)))
                    for i in range(min(12, len(scores)))}
    best_idx = max(score_by_idx, key=score_by_idx.get)
    worst_idx = min(score_by_idx, key=score_by_idx.get)

    best_score = f'{score_by_idx[best_idx]:.1f}'
    best_tmax = _safe_float(months[best_idx]['tmax'])
    best_tmin = _safe_float(months[best_idx]['tmin'])
    best_sun = round(_safe_float(months[best_idx]['sun_h']), 1)
    best_rain = _safe_float(months[best_idx]['rain_pct'])
    worst_rain = _safe_float(months[worst_idx]['rain_pct'])

    # Wettest = max rain_pct
    rain_by_idx = {i: _safe_float(months[i]['rain_pct']) for i in range(12)}
    wettest_idx = max(rain_by_idx, key=rain_by_idx.get)
    wettest_rain = rain_by_idx[wettest_idx]

    # Bests = list of months with score in top quartile (used for std FAQ suffix)
    sorted_idxs = sorted(score_by_idx, key=score_by_idx.get, reverse=True)
    bests = [MONTHS[i] for i in sorted_idxs[:3] if score_by_idx[i] >= 7]

    if is_mountain:
        # Best ski month
        best_ski_idx = max(range(12), key=lambda i: compute_ski_score(
            _safe_float(months[i]['tmax']),
            _safe_float(months[i]['rain_pct']),
            _safe_float(months[i]['sun_h']),
            **_ski_kwargs(slug_fr, month=i+1)
        ))
        best_ski_score = f'{compute_ski_score(_safe_float(months[best_ski_idx]["tmax"]), _safe_float(months[best_ski_idx]["rain_pct"]), _safe_float(months[best_ski_idx]["sun_h"]), **_ski_kwargs(slug_fr, month=best_ski_idx+1)):.1f}'

        winter_idxs = [11, 0, 1]  # Déc, Jan, Fév
        winter_ski = [compute_ski_score(_safe_float(months[i]['tmax']), _safe_float(months[i]['rain_pct']), _safe_float(months[i]['sun_h']), **_ski_kwargs(slug_fr, month=i+1)) for i in winter_idxs]
        winter_ski_avg = f'{sum(winter_ski)/len(winter_ski):.1f}'

        faq_vars = dict(
            prep=prep, nom_bare=nom_bare, nom=nom,
            best_ski_month=MONTHS[best_ski_idx],
            best_ski_month_lc=month_lc(cfg, MONTHS[best_ski_idx]),
            best_ski_score=best_ski_score,
            best_month=MONTHS[best_idx],
            best_month_lc=month_lc(cfg, MONTHS[best_idx]),
            best_score=best_score,
            best_tmax=best_tmax,
            worst_month=MONTHS[worst_idx],
            worst_rain=worst_rain,
            wettest_month=MONTHS[wettest_idx],
            wettest_rain=wettest_rain,
            winter_ski_avg=winter_ski_avg,
            jan_tmax=months[0]['tmax'],
        )
        templates = cfg.get('annual_faq_mountain', [])
    else:
        bests_suffix = ''
        if len(bests) > 1 and cfg.get('annual_faq_bests_suffix'):
            bests_suffix = cfg['annual_faq_bests_suffix'].format(bests_str=' & '.join(bests[:2]))

        # Winter season key (FR='Hiver', EN='Winter', ES='Invierno', DE='Winter')
        winter_key = cfg['season_order'][-1] if cfg.get('season_order') else 'Hiver'
        winter_idxs = [11, 0, 1]
        winter_score = sum(score_by_idx.get(i, 0) for i in winter_idxs) / 3
        winter_verdict = (cfg.get('annual_faq_winter_verdicts', {}).get('ok', '')
                          if winter_score >= 5.5
                          else cfg.get('annual_faq_winter_verdicts', {}).get('bad', ''))

        from lib.common import c_to_f
        _best_tmax_v = c_to_f(best_tmax) if cfg.get('imperial') else best_tmax
        _best_tmin = c_to_f(best_tmin) if cfg.get('imperial') else best_tmin
        _temp_unit = cfg.get('temp_unit', '°C')

        faq_vars = dict(
            prep=prep, nom_bare=nom_bare, nom=nom,
            best_month=MONTHS[best_idx],
            best_month_lc=month_lc(cfg, MONTHS[best_idx]),
            best_score=best_score, best_rain=best_rain,
            best_tmax=_best_tmax_v, best_tmin=_best_tmin,
            best_sun=best_sun, temp_unit=_temp_unit,
            worst_month=MONTHS[worst_idx],
            worst_rain=worst_rain,
            wettest_month=MONTHS[wettest_idx],
            wettest_rain=wettest_rain,
            bests_suffix=bests_suffix,
            winter_score=f'{winter_score:.1f}',
            winter_verdict=winter_verdict,
        )
        templates = cfg.get('annual_faq_standard', [])

    # Apply templates
    faq_items = []
    for tpl in templates:
        try:
            q = fill_tpl(tpl['q'], cfg, **faq_vars)
            a = fill_tpl(tpl['a'], cfg, **faq_vars)
            faq_items.append({'q': q, 'a': a})
        except (KeyError, IndexError) as e:
            # Skip items with missing variables (defensive)
            continue
    return faq_items


def _build_json_ld_blocks(cfg: dict, dest: dict, slug: str, nom: str,
                          page_title: str, page_desc: str, canonical_url: str,
                          faq_items: list[dict]) -> list[str]:
    """Construit les blocks JSON-LD (Article + FAQPage) en strings prêtes."""
    import json as _json
    from lib.page_config import date_modified_for

    slug_fr = dest.get('slug_fr', slug)
    date_mod = date_modified_for(slug_fr) or '2026-04-01'
    in_lang = cfg.get('in_language', cfg['lang'])

    article = {
        '@context': 'https://schema.org',
        '@type': 'Article',
        'headline': page_title,
        'description': page_desc,
        'image': {
            '@type': 'ImageObject',
            'url': 'https://bestdateweather.com/og-image.png',
            'width': 1200, 'height': 630,
        },
        'author': {
            '@type': 'Person',
            '@id': 'https://bestdateweather.com/#gilles',
            'name': 'Gilles',
            'url': 'https://bestdateweather.com/a-propos',
        },
        'publisher': {
            '@type': 'Organization',
            '@id': 'https://bestdateweather.com/#organization',
            'name': 'BestDateWeather',
            'url': 'https://bestdateweather.com',
            'logo': {
                '@type': 'ImageObject',
                'url': 'https://bestdateweather.com/icon-192.png',
                'width': 192, 'height': 192,
            },
        },
        'datePublished': date_mod,
        'dateModified': date_mod,
        'inLanguage': in_lang,
        'url': canonical_url,
        'mainEntityOfPage': {
            '@type': 'WebPage',
            '@id': canonical_url,
        },
    }

    blocks = [_json.dumps(article, ensure_ascii=False)]

    # BreadcrumbList : Accueil > Destination (signal hiérarchie pour Google)
    home_url = cfg.get('canonical_prefix', 'https://bestdateweather.com/')
    if not home_url.startswith('http'):
        home_url = 'https://bestdateweather.com/'
    # Racine de langue (FR = /, EN = /en/app, etc. servies en 200)
    lang = cfg['lang']
    home_map = {
        'fr': 'https://bestdateweather.com/',
        'en': 'https://bestdateweather.com/en/app',
        'en-us': 'https://bestdateweather.com/us/app',
        'es': 'https://bestdateweather.com/es/app',
        'de': 'https://bestdateweather.com/de/app',
    }
    home_lbl = {'fr': 'Accueil', 'en': 'Home', 'en-us': 'Home', 'es': 'Inicio', 'de': 'Startseite'}
    breadcrumb = {
        '@context': 'https://schema.org',
        '@type': 'BreadcrumbList',
        'itemListElement': [
            {'@type': 'ListItem', 'position': 1,
             'name': home_lbl.get(lang, 'Home'),
             'item': home_map.get(lang, 'https://bestdateweather.com/')},
            {'@type': 'ListItem', 'position': 2, 'name': nom, 'item': canonical_url},
        ],
    }
    blocks.append(_json.dumps(breadcrumb, ensure_ascii=False))

    if faq_items:
        faq_page = {
            '@context': 'https://schema.org',
            '@type': 'FAQPage',
            'mainEntity': [
                {
                    '@type': 'Question',
                    'name': item['q'],
                    'acceptedAnswer': {
                        '@type': 'Answer',
                        # Strip HTML tags from FAQ answers for JSON-LD
                        'text': _strip_html(item['a']),
                    },
                }
                for item in faq_items
            ],
        }
        blocks.append(_json.dumps(faq_page, ensure_ascii=False))

    return blocks


def _strip_html(s: str) -> str:
    """Supprime les balises HTML d'une string. Naïf mais suffisant pour les FAQ."""
    import re as _re
    s = _re.sub(r'<[^>]+>', '', s)
    return _re.sub(r'\s+', ' ', s).strip()


# ═══════════════════════════════════════════════════════════════════════════════
# Entry point : gen_monthly_v6 — pages MENSUELLES en design V6
# ═══════════════════════════════════════════════════════════════════════════════

import datetime as _dt
_MONTH_YEAR = _dt.date.today().year
_MONTHLY_INDEXABLE = None


def _monthly_indexable(slug: str) -> bool:
    """True si les pages mensuelles de cette destination doivent être indexées.

    Liste construite empiriquement depuis la Search Console (destinations
    concentrant l'essentiel des impressions), pas choisie a priori.
    """
    global _MONTHLY_INDEXABLE
    if _MONTHLY_INDEXABLE is None:
        import json as _j
        p = os.path.join(os.path.dirname(__file__), '..', 'data', 'monthly_indexable.json')
        try:
            _MONTHLY_INDEXABLE = set(_j.load(open(p, encoding='utf-8')))
        except Exception:
            _MONTHLY_INDEXABLE = set()
    return slug in _MONTHLY_INDEXABLE


def gen_monthly_v6(cfg, fn, dest, months, mi, all_dests=None,
                   similarities=None, comparison_index=None,
                   all_climate=None, monthly_crosslinks=None) -> str:
    """Version V6 d'une page mensuelle. Retourne le HTML complet.

    Réutilise build_page_data_v6() pour toutes les données partagées, puis
    assemble une page avec le hero MENSUEL (score du mois mi) + section
    "mois vs meilleur mois", et réutilise les blocs V6 partagés (contexte,
    réserver, explorer, localisation, infos pratiques, FAQ, topbar, footer).

    Args:
        cfg, fn: config + bound translation (comme gen_monthly V5)
        dest: ligne destinations.csv
        months: 12 dicts climate.csv
        mi: index du mois (0-11)
        all_dests, similarities, comparison_index: pour related
    """
    from lib.page_config import (dest_slug, dest_name, dest_country,
                                  build_hreflang_tags, to_canonical_url,
                                  monthly_href, annual_href)
    from lib.v6 import (render_v6_topbar, render_v6_head, render_v6_scripts,
                        render_v6_footer, render_v6_contexte, render_v6_questions,
                        render_v6_reserver,
                        render_v6_localisation, render_v6_infos_pratiques)
    from lib.v6_monthly import (render_v6_monthly_hero, render_v6_monthly_vs_best,
                                render_v6_monthly_expect, render_v6_monthly_explore,
                                render_v6_monthly_details, monthly_dynamics_paragraph,
                                monthly_faq_items, edito_teaser,
                                VS_CTA_CSS)
    from scoring import compute_scores, compute_mountain_scores
    from datetime import datetime

    lang = cfg['lang']
    slug = dest_slug(cfg, dest)
    slug_fr = dest.get('slug_fr', slug)
    nom = dest_name(cfg, dest)
    country_name = dest_country(cfg, dest)
    country_iso = _flag_iso(dest.get('flag', ''))
    is_mountain = _bool(dest.get('mountain'))
    MONTHS_LOC = cfg['months']
    mois_loc = MONTHS_LOC[mi]
    asset_prefix = cfg['asset_prefix']

    # Réutiliser build_page_data_v6 pour récupérer TOUTES les données partagées
    months_input = [{
        'cls': m.get('classe', m.get('class', 'mid')),
        'tmax': _safe_float(m.get('tmax')),
        'rain_pct': _safe_float(m.get('rain_pct')),
        'sun_h': _safe_float(m.get('sun_h')),
        'month': m.get('mois', ''),
    } for m in months]
    scores = (compute_mountain_scores(months_input, slug=slug_fr) if is_mountain
              else compute_scores(months_input, slug=slug_fr))

    monthly_url_tpl = f'{slug}{cfg["monthly_sep"]}{{mois_lower}}'

    avis_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'avis_annuel.json')
    avis = _load_json_cached(avis_path)
    editorial_html = (avis.get(f'{slug_fr}:{lang}') or avis.get(f'{slug_fr}:fr') or '')
    if editorial_html and not editorial_html.startswith('<'):
        editorial_html = f'<p>{editorial_html}</p>'

    photo = dest.get('_photo', {})
    photo_url = photo.get('url', '')
    photo_credit_html = ''
    if photo.get('credit_name') and photo.get('credit_url'):
        photo_credit_html = (f'<a href="{photo["credit_url"]}" target="_blank" '
                             f'rel="noopener nofollow">{photo["credit_name"]}</a> via Unsplash')

    current_month_idx = datetime.now().month - 1
    update_month = MONTHS_LOC[current_month_idx]

    page_data = build_page_data_v6(
        cfg=cfg, dest=dest, months_climate=months, months_with_scores=scores,
        slug=slug, nom=nom, country_name=country_name, country_iso=country_iso,
        monthly_url_tpl=monthly_url_tpl, editorial_html=editorial_html,
        photo_url=photo_url, photo_credit=photo_credit_html, update_month=update_month,
    )

    # ── Données du mois mi ──
    m = months[mi]
    this_score = _safe_float(m.get('score'), 0)
    md = page_data['months_data']
    best = max(md, key=lambda x: x['score_10'])
    best_idx = md.index(best)
    is_best = (best_idx == mi)

    climate_type = page_data.get('climate_type',
                                 page_data.get('hero_data', {}).get('climate_type', ''))

    # ── Hero monthly ──
    hero = render_v6_monthly_hero(slug, lang, {
        'dest_name': nom, 'mois': mois_loc,
        'country_name': country_name, 'country_iso': country_iso,
        'climate_type': climate_type, 'score': this_score,
        'tmin': _safe_float(m.get('tmin')), 'tmax': _safe_float(m.get('tmax')),
        'rain_pct': _safe_float(m.get('rain_pct')), 'sun_h': _safe_float(m.get('sun_h')),
        'lat': _safe_float(dest['lat']), 'lon': _safe_float(dest['lon']),
        'photo_url': photo_url, 'photo_credit': photo_credit_html,
        'update_month': update_month,
        'chips': page_data.get('hero_data', {}).get('chips', []),
    }, asset_prefix=asset_prefix)

    # ── Section "mois vs meilleur mois" ──
    best_mois_url = cfg['month_url'][best_idx]
    vs = render_v6_monthly_vs_best(slug, lang, {
        'mois': mois_loc, 'dest_name': nom, 'is_best': is_best,
        'best_month': MONTHS_LOC[best_idx], 'best_score': best['score_10'],
        'this_score': this_score,
        'best_href': monthly_href(cfg, slug, best_idx),
        'annual_href': annual_href(cfg, slug),
    })

    # ── Section "Explorer ce mois" : cross-links MENSUELS ──
    # Reproduit les 3 blocs du V5 (similaires / proches / autres tops) mais
    # avec liens vers les pages DU MÊME MOIS, pas annuelles.
    from lib.page_config import dest_name as _dn, dest_country as _dc
    # related n'est pas construit par build_page_data_v6 (seulement par gen_annual_v6),
    # on l'appelle nous-mêmes pour récupérer proximity.
    related = _build_related_v6(cfg, dest, similarities, all_dests)

    def _to_monthly(item_slug_fr):
        """Construit un item explore (lien mensuel) depuis un slug_fr."""
        od = all_dests.get(item_slug_fr) if all_dests else None
        if not od:
            return None
        oslug = dest_slug(cfg, od)
        return {
            'name': _dn(cfg, od),
            'href': monthly_href(cfg, oslug, mi),
            'country': _dc(cfg, od),
            'iso': _flag_iso(od.get('flag', '')),
        }

    # Box "Climat similaire" — via similarities (climat)
    # similarities[slug] = liste de tuples (cos_sim_score, other_slug)
    similar_items = []
    if similarities:
        for entry in similarities.get(slug_fr, [])[:5]:
            s = entry[1] if isinstance(entry, (tuple, list)) else entry
            it = _to_monthly(s)
            if it:
                similar_items.append(it)

    # Box "À proximité" — réutilise related['proximity'] mais href → mensuel
    nearby_items = []
    name_to_slug = {}
    if all_dests:
        for sfr, od in all_dests.items():
            name_to_slug[_dn(cfg, od)] = sfr
    for prox in related.get('proximity', [])[:5]:
        match_slug = name_to_slug.get(prox.get('name', ''))
        if match_slug:
            oslug = dest_slug(cfg, all_dests[match_slug])
            nearby_items.append({
                'name': prox.get('name', ''),
                'href': monthly_href(cfg, oslug, mi),
                'country': prox.get('country', ''),
                'iso': prox.get('country_iso', ''),
                'distance_km': prox.get('distance_km'),
            })

    # Box "Autres tops du mois" — via monthly_crosslinks
    other_top_items = []
    if monthly_crosslinks:
        for s in (monthly_crosslinks.get(slug_fr) or {}).get(mi, [])[:5]:
            it = _to_monthly(s)
            if it:
                if all_climate and s in all_climate:
                    try:
                        it['score'] = all_climate[s][mi]['score']
                    except (KeyError, IndexError, TypeError):
                        pass
                other_top_items.append(it)

    # Navigation mois adjacents
    prev_mi = (mi - 1) % 12
    next_mi = (mi + 1) % 12
    explore_html = render_v6_monthly_explore(slug, lang, {
        'mois': mois_loc,
        'prev_month': {'name': MONTHS_LOC[prev_mi], 'href': monthly_href(cfg, slug, prev_mi)},
        'next_month': {'name': MONTHS_LOC[next_mi], 'href': monthly_href(cfg, slug, next_mi)},
        'similar': similar_items,
        'nearby': nearby_items,
        'other_top': other_top_items,
        'map_href': cfg.get('map_href', cfg.get('carte_href', '')),
    }, asset_prefix=asset_prefix)

    # ── Section "À quoi s'attendre ce mois" (contenu riche du V5) ──
    expect_html = ''
    try:
        from generate_pages import context_paragraph
        nom_f = dest.get(f'nom_{lang[:2]}', nom)
        is_tropical = _bool(dest.get('tropical'))
        m_for_ctx = {
            'tmax': _safe_float(m.get('tmax')),
            'rain_pct': _safe_float(m.get('rain_pct')),
            'sun_h': _safe_float(m.get('sun_h')),
            'classe': m.get('classe', 'mid'),
        }
        ctx_para = context_paragraph(
            cfg, nom, nom_f, m_for_ctx, mi, this_score,
            MONTHS_LOC[best_idx], best['score_10'], is_tropical,
            event_text=None, is_mountain=is_mountain, ski_sc=0,
        )
        if ctx_para:
            expect_html = render_v6_monthly_expect(slug, lang, {
                'mois': mois_loc, 'paragraph_html': ctx_para,
            })
    except Exception:
        expect_html = ''  # si context_paragraph échoue, on omet la section (non bloquant)

    # ── Dynamique mensuelle : rang du mois + deltas vs mois précédent ──
    # (contenu distinctif par mois — fix similarité inter-mois 85%)
    try:
        rank = 1 + sum(1 for x in md if x['score_10'] > md[mi]['score_10'])
        prev_mi_dyn = (mi - 1) % 12
        m_prev = months[prev_mi_dyn]
        dyn_html = monthly_dynamics_paragraph(
            lang, nom, mois_loc, rank, MONTHS_LOC[prev_mi_dyn],
            d_tmax=_safe_float(m.get('tmax')) - _safe_float(m_prev.get('tmax')),
            d_rain=_safe_float(m.get('rain_pct')) - _safe_float(m_prev.get('rain_pct')),
            d_sun=_safe_float(m.get('sun_h')) - _safe_float(m_prev.get('sun_h')),
            is_us=(lang == 'en-us'),
        )
        if expect_html and dyn_html:
            expect_html = expect_html.replace('</div>\n  </div>\n</section>',
                                              f'{dyn_html}</div>\n  </div>\n</section>', 1)
    except Exception:
        pass

    # ── Section "Conditions du mois" (UV, ressenti, mer, jour, air) ──
    try:
        details_html = render_v6_monthly_details(slug, lang, {
            'mois': mois_loc,
            'uv': _safe_float(m.get('uv_index')) or None,
            'dew': _safe_float(m.get('dew_point', m.get('dew_point_mean'))) or None,
            'sea': _safe_float(m.get('sea_temp')) or None,
            'aqi': _safe_float(m.get('aqi_mean')) or None,
            'lat': _safe_float(dest.get('lat')),
            'month_idx': mi,
            'tmax': _safe_float(m.get('tmax')),
        })
    except Exception:
        details_html = ''

    # ── Blocs V6 partagés ──
    topbar = render_v6_topbar(slug, lang)
    # Option C (juil. 2026) : l'avis annuel intégral était dupliqué sur les 12
    # pages mensuelles (120 mots de boilerplate). Teaser 2 phrases + lien vers
    # l'avis complet sur la page annuelle. Section omise si pas d'avis.
    _teaser = edito_teaser(editorial_html, annual_href(cfg, slug), lang)
    contexte = render_v6_contexte(slug, lang, _teaser) if _teaser else ''
    reserver = render_v6_reserver(slug, lang, nom)
    infos = render_v6_infos_pratiques(slug, lang, page_data['infos_pratiques_data'],
                                      asset_prefix=asset_prefix)
    worst = min(md, key=lambda x: x['score_10'])
    localisation = render_v6_localisation(
        slug=slug, lang=lang, nom=nom,
        lat=_safe_float(dest['lat']), lon=_safe_float(dest['lon']),
        country_iso=country_iso, country_name=country_name,
        climate_type=climate_type,
        best_month=best['mois'], best_score=best['score_10'],
        worst_month=worst['mois'], worst_score=worst['score_10'],
        macro_zoom=page_data.get('macro_zoom', 5), asset_prefix=asset_prefix,
    )

    # FAQ mensuelle : réutilise les items annuels (couvre la destination).
    # build_page_data_v6 retourne faq_items=[] (placeholder enrichi seulement
    # dans gen_annual_v6), donc on les construit nous-mêmes ici.
    nom_bare = dest.get('nom_bare', nom)
    prep = dest.get(f'prep_{lang[:2]}', dest.get('prep_fr', 'à'))
    faq_items = _build_faq_items(cfg, dest, months, scores,
                                 is_mountain, slug_fr, prep, nom, nom_bare)
    # + 1-2 questions spécifiques AU MOIS (baignade/UV, réponses chiffrées) —
    # contenu distinctif inter-mois + JSON-LD FAQPage enrichi
    try:
        faq_items = faq_items + monthly_faq_items(
            lang, nom, mois_loc,
            sea=_safe_float(m.get('sea_temp')) or None,
            uv=_safe_float(m.get('uv_index')) or None,
            lat=_safe_float(dest.get('lat')), month_idx=mi,
            is_us=(lang == 'en-us'))
    except Exception:
        pass
    questions = render_v6_questions(slug, lang, faq_items)

    footer = render_v6_footer(
        slug_fr=slug_fr if lang != 'fr' else slug, lang=lang,
        slug_en=dest.get('slug_en', ''), slug_es=dest.get('slug_es', ''),
        slug_de=dest.get('slug_de', ''), asset_prefix=asset_prefix,
    )

    # ── HEAD (titre/desc monthly, canonical sans .html) ──
    canonical = cfg['canonical_prefix'] + to_canonical_url(
        f'{slug}{cfg["monthly_sep"]}{cfg["month_url"][mi]}.html')

    # Titre/desc mensuels.
    # L'ANNÉE est explicitée : les données GSC montrent que les requêtes datées
    # ("kos weather may 2026") ont un CTR de 0,93% contre 0,07% sans année, et
    # concentrent 69% des clics — l'encart météo de Google ne couvre que ~10
    # jours et laisse donc la place sur les intentions de planification.
    _yr = _MONTH_YEAR
    page_title = f'{nom} en {mois_loc} {_yr} : météo et score {this_score:.1f}/10'
    if lang in ('en', 'en-us'):
        page_title = f'{nom} Weather in {mois_loc} {_yr}: what to expect ({this_score:.1f}/10)'
    elif lang == 'es':
        page_title = f'{nom} en {mois_loc} {_yr}: clima y puntuación {this_score:.1f}/10'
    elif lang == 'de':
        page_title = f'{nom} im {mois_loc} {_yr}: Wetter und Bewertung {this_score:.1f}/10'
    _m=m
    _t=_safe_float(_m.get('tmax')); _r=round(_safe_float(_m.get('rain_pct')))
    _tt=f'{round(_t*9/5+32)}°F' if lang=='en-us' else f'{round(_t)}°C'
    if lang == 'fr':
        page_desc = (f'Météo à {nom} en {mois_loc} {_yr} : {_tt} en journée, {_r}% de jours '
                     f'de pluie, score {this_score:.1f}/10. Faut-il y aller ce mois-ci ?')
    elif lang in ('en', 'en-us'):
        page_desc = (f'{nom} weather in {mois_loc} {_yr}: {_tt} by day, {_r}% rainy days, '
                     f'rated {this_score:.1f}/10. Is it a good month to go?')
    elif lang == 'es':
        page_desc = (f'Clima en {nom} en {mois_loc} {_yr}: {_tt} de día, {_r}% de días de '
                     f'lluvia, puntuación {this_score:.1f}/10. ¿Buen mes para ir?')
    else:
        page_desc = (f'Wetter in {nom} im {mois_loc} {_yr}: {_tt} tagsüber, {_r}% Regentage, '
                     f'Bewertung {this_score:.1f}/10. Lohnt sich dieser Monat?')
    page_desc = page_desc[:165]

    hreflang_tags = build_hreflang_tags(dest, mi=mi)

    # JSON-LD: Article + FAQPage (construits ici car build_page_data_v6 renvoie []).
    # On utilise le titre/canonical du MOIS et les faq_items mensuels.
    monthly_json_ld = _build_json_ld_blocks(
        cfg=cfg, dest=dest, slug=slug, nom=nom,
        page_title=page_title, page_desc=page_desc,
        canonical_url=canonical, faq_items=faq_items,
    )
    # _build_json_ld_blocks ajoute un BreadcrumbList 2-niveaux (Accueil > Destination)
    # qui pointerait la page mensuelle comme "Destination". On le retire pour le
    # remplacer par un breadcrumb 3-niveaux (Accueil > Destination annuelle > Mois).
    monthly_json_ld = [b for b in monthly_json_ld if '"BreadcrumbList"' not in b]
    # BreadcrumbList: Accueil > Destination (annuel) > Mois
    import json as _json_bc
    home_map = {
        'fr': 'https://bestdateweather.com/', 'en': 'https://bestdateweather.com/en/app',
        'en-us': 'https://bestdateweather.com/us/app', 'es': 'https://bestdateweather.com/es/app',
        'de': 'https://bestdateweather.com/de/app',
    }
    home_lbl = {'fr': 'Accueil', 'en': 'Home', 'en-us': 'Home', 'es': 'Inicio', 'de': 'Startseite'}
    annual_canonical = cfg['canonical_prefix'] + annual_href(cfg, slug)
    breadcrumb = {
        '@context': 'https://schema.org', '@type': 'BreadcrumbList',
        'itemListElement': [
            {'@type': 'ListItem', 'position': 1, 'name': home_lbl.get(lang, 'Home'),
             'item': home_map.get(lang, 'https://bestdateweather.com/')},
            {'@type': 'ListItem', 'position': 2, 'name': nom, 'item': annual_canonical},
            {'@type': 'ListItem', 'position': 3, 'name': f'{nom} · {mois_loc}', 'item': canonical},
        ],
    }
    monthly_json_ld.append(_json_bc.dumps(breadcrumb, ensure_ascii=False))

    head = render_v6_head(
        lang=lang, page_title=page_title, page_desc=page_desc,
        canonical_url=canonical, asset_prefix=asset_prefix,
        bg_image_url=photo_url, hreflang_tags=hreflang_tags,
        og_image_url=page_data.get('og_image_url', ''),
        json_ld_blocks=monthly_json_ld,
        # Indexation SÉLECTIVE des pages mensuelles.
        # Les données GSC montrent que les requêtes datées ("X weather may
        # 2026") captent 69% des clics pour 14% des impressions (CTR 0,93%
        # contre 0,07% sans année) : l'encart météo de Google ne couvre que
        # ~10 jours et ne répond donc pas à une intention de planification.
        # Ces requêtes pointent vers les pages mensuelles. On en réindexe donc
        # les 149 destinations qui concentrent 88% des impressions réelles
        # (data/monthly_indexable.json, sélection empirique via GSC), soit
        # ~1 800 pages au lieu des 44 000 qui avaient valu la rétrogradation.
        noindex=not _monthly_indexable(dest.get('slug_fr', slug)),
    )
    # Injecter le CSS .vs-cta dans le head
    head = head.replace('</head>', f'<style>{VS_CTA_CSS}</style>\n</head>')

    scripts = render_v6_scripts(asset_prefix=asset_prefix)

    body = (f'{topbar}\n{hero}\n<main>\n'
            f'{expect_html}\n{details_html}\n{vs}\n{contexte}\n{reserver}\n{infos}\n{explore_html}\n'
            f'{localisation}\n{questions}\n</main>\n{footer}')

    html = head + '\n' + body + '\n' + scripts
    from lib.page_config import strip_html_from_internal_links
    return strip_html_from_internal_links(html)
