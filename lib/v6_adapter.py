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
    currency_name = cinfo.get('currency_name', '')
    currency_symbol = cinfo.get('currency_symbol', '')
    drive = cinfo.get('drive', 'right')
    gpi_level = _safe_int(cinfo.get('risk_level'))
    gpi_value = _safe_float(cinfo.get('gpi'))
    cost_tier = _safe_int(cinfo.get('budget_index'))
    cost_value = _safe_float(cinfo.get('budget_numbeo_col'))

    # Trend value
    trend_value = _compute_trend_value(slug=dest.get('slug_fr', slug),
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
        'is_mountain': is_mountain,
        'is_coastal': _bool(dest.get('coastal')),
        'is_tropical': is_tropical,
        'is_polar': profile == 'polar',
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
        infos_pratiques_data['ski_season'] = 'Déc → Mai'
        infos_pratiques_data['hiking_season'] = 'Juin → Sept'
    elif is_tropical:
        infos_pratiques_data['dry_season'] = 'Mai → Sept'
        infos_pratiques_data['wet_season'] = 'Déc → Mars'
        infos_pratiques_data['has_cyclones'] = abs(lat) > 10
        infos_pratiques_data['latitude'] = lat
        # Sea temps (à enrichir plus tard depuis climate.csv si colonne sea_temp)
    elif profile == 'polar':
        infos_pratiques_data['latitude'] = lat
        infos_pratiques_data['has_geothermal'] = country_name.lower() in ('islande', 'iceland', 'islandia', 'island')

    # ── Construction page_data ──
    canonical_url = f'https://bestdateweather.com/{cfg.get("canonical_prefix", "")}{cfg["annual_prefix"]}{slug}{cfg["annual_suffix"]}'

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

    # Meta description : générique mais informative
    if lang == 'fr':
        page_desc = (f'Quand partir à {nom} ? {best["mois"]} ({best["score_10"]:.1f}/10) sort en tête, '
                     f'{worst["mois"]} ({worst["score_10"]:.1f}/10) reste le plus rude. '
                     f'Données ERA5 sur 10 ans, scores des 12 mois.')
    elif lang in ('en', 'en-us'):
        page_desc = (f'When to visit {nom}? {best["mois"]} ({best["score_10"]:.1f}/10) is the standout, '
                     f'{worst["mois"]} ({worst["score_10"]:.1f}/10) the toughest. '
                     f'10-year ERA5 climate data, all 12 months scored.')
    elif lang == 'es':
        page_desc = (f'¿Cuándo ir a {nom}? {best["mois"]} ({best["score_10"]:.1f}/10) destaca, '
                     f'{worst["mois"]} ({worst["score_10"]:.1f}/10) es el más duro. '
                     f'Datos ERA5 de 10 años, 12 meses puntuados.')
    elif lang == 'de':
        page_desc = (f'Wann nach {nom} reisen? {best["mois"]} ({best["score_10"]:.1f}/10) liegt vorne, '
                     f'{worst["mois"]} ({worst["score_10"]:.1f}/10) ist am härtesten. '
                     f'ERA5-Daten 10 Jahre, alle 12 Monate bewertet.')
    else:
        page_desc = f'{nom}: {best["mois"]} ({best["score_10"]:.1f}/10) best, {worst["mois"]} ({worst["score_10"]:.1f}/10) worst.'

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

    # URL templates
    monthly_url_tpl = f'{slug}{cfg["monthly_sep"]}{{mois_lower}}.html'

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

    return render_v6_full_page(page_data)


def _build_related_v6(cfg: dict, dest: dict, similarities: dict | None,
                      all_dests: dict | None) -> list[dict]:
    """Construit la liste related pour la section Explorer.

    Reprend les top 3 destinations similaires (cosine sim sur tmax/rain/sun) si
    disponibles. Format de retour : [{href, name, sub}, ...].
    """
    if not similarities or not all_dests:
        return []

    slug_fr_canonical = dest.get('slug_fr', '')
    sims = similarities.get(slug_fr_canonical, [])
    if not sims:
        return []

    related = []
    lang = cfg['lang']

    for score, other_slug in sims[:3]:
        other = all_dests.get(other_slug)
        if not other:
            continue
        # Slug localisé pour href
        slug_lang = other.get(f'slug_{lang[:2]}', other.get('slug_fr', other_slug))
        href = f'{cfg["annual_prefix"]}{slug_lang}{cfg["annual_suffix"]}'
        # Name localisé
        name = other.get(f'nom_{lang[:2]}', other.get('nom_fr', other_slug.title()))
        # Sub : pays
        sub = other.get(f'country_{lang[:2]}', other.get('pays', ''))
        related.append({'href': href, 'name': name, 'sub': sub})
    return related


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
            'url': 'https://bestdateweather.com/a-propos.html',
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
