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


def _extract_climate_extremes(months: list[dict]) -> dict:
    """À partir des 12 mois, extrait hottest/coldest/rainiest/sunniest.

    Args:
        months: liste de 12 dicts climate.csv (avec 'mois', 'tmax', 'tmin',
            'rain_pct', 'sun_h')

    Returns:
        {hottest_month, hottest_temp, coldest_month, coldest_temp,
         rainiest_month, rainiest_pct, sunniest_month, sunniest_h}
    """
    hottest = max(months, key=lambda m: _safe_float(m.get('tmax')))
    coldest = min(months, key=lambda m: _safe_float(m.get('tmax')))
    rainiest = max(months, key=lambda m: _safe_float(m.get('rain_pct')))
    sunniest = max(months, key=lambda m: _safe_float(m.get('sun_h')))
    return {
        'hottest_month': hottest['mois'],
        'hottest_temp': _safe_float(hottest['tmax']),
        'coldest_month': coldest['mois'],
        'coldest_temp': _safe_float(coldest['tmax']),
        'rainiest_month': rainiest['mois'],
        'rainiest_pct': _safe_float(rainiest['rain_pct']),
        'sunniest_month': sunniest['mois'],
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
    """
    if 'polaire' in climate_type.lower() or 'subarctique' in climate_type.lower():
        return 'polar'
    if _bool(dest.get('tropical')):
        return 'tropical'
    if _bool(dest.get('mountain')):
        return 'mountain'
    if _bool(dest.get('coastal')):
        return 'coastal'
    return 'city'


def _build_climate_type(dest: dict, lat: float) -> str:
    """Génère un libellé climat type depuis flags CSV + latitude.

    Approche pragmatique : on fait du Köppen-light pour avoir un texte.
    À enrichir plus tard avec une vraie classif Köppen-Geiger.
    """
    if _bool(dest.get('mountain')):
        return 'Climat alpin de montagne'
    if abs(lat) < 10:
        return 'Tropical équatorial'
    if _bool(dest.get('tropical')):
        return 'Tropical'
    if abs(lat) > 60:
        return 'Subarctique océanique'
    if _bool(dest.get('coastal')):
        return 'Tempéré océanique'
    return 'Tempéré'


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
    for i, mc in enumerate(months_climate):
        score_entry = months_with_scores[i] if i < len(months_with_scores) else {}
        months_data.append({
            'mois': mc['mois'],
            'tmin': _safe_float(mc.get('tmin')),
            'tmax': _safe_float(mc.get('tmax')),
            'rain_pct': _safe_float(mc.get('rain_pct')),
            'precip_mm': _safe_float(mc.get('precip_mm')),
            'sun_h': _safe_float(mc.get('sun_h')),
            'score_10': _safe_float(score_entry.get('score_10', score_entry.get('score', 0))),
            'classe': score_entry.get('classe', score_entry.get('cls', 'mid')),
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
    climate_type = _build_climate_type(dest, lat)
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
    extremes = _extract_climate_extremes(months_climate)

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

    # Chips climat (heuristique simple selon profil)
    chips_by_profile = {
        'mountain': [
            {'emoji': '❄️', 'text': 'Climat alpin', 'color': 'blue'},
            {'emoji': '☀️', 'text': 'UV altitude', 'color': 'gold'},
            {'emoji': '🌦️', 'text': 'Météo changeante', 'color': 'purple'},
        ],
        'tropical': [
            {'emoji': '🌴', 'text': 'Tropical', 'color': 'green'},
            {'emoji': '☀️', 'text': 'UV élevé', 'color': 'gold'},
            {'emoji': '🌧️', 'text': 'Mousson saison', 'color': 'blue'},
        ],
        'polar': [
            {'emoji': '❄️', 'text': 'Subarctique', 'color': 'blue'},
            {'emoji': '🌌', 'text': 'Aurores', 'color': 'purple'},
            {'emoji': '🌬️', 'text': 'Vents fréquents', 'color': 'gold'},
        ],
        'coastal': [
            {'emoji': '🌊', 'text': 'Bord de mer', 'color': 'blue'},
            {'emoji': '☀️', 'text': 'Lumineux', 'color': 'gold'},
            {'emoji': '🍴', 'text': 'Gastronomie', 'color': 'red'},
        ],
        'city': [
            {'emoji': '🏛️', 'text': 'Patrimoine', 'color': 'gold'},
            {'emoji': '🌧️', 'text': 'Pluies modérées', 'color': 'blue'},
            {'emoji': '☔', 'text': 'Visites couvertes', 'color': 'purple'},
        ],
    }
    chips = chips_by_profile.get(profile, chips_by_profile['city'])

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

    return {
        'lang': lang,
        'slug': slug,
        'slug_fr': dest.get('slug_fr', slug),
        'slug_en': dest.get('slug_en', ''),
        'slug_es': dest.get('slug_es', ''),
        'slug_de': dest.get('slug_de', ''),
        'dest_name': nom,
        'page_title': f'{nom} : meilleurs mois pour partir',  # à enrichir
        'page_desc': f'Quand partir à {nom} ? {best["mois"]} ({best["score_10"]:.1f}/10) en tête. Données ERA5 sur 10 ans.',
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
    from lib.page_config import dest_slug, dest_name, dest_country
    from scoring import compute_scores, compute_mountain_scores

    slug = dest_slug(cfg, dest)
    nom = dest_name(cfg, dest)
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
        # Wrap dans <p> si plain text
        editorial_html = f'<p>{editorial_html}</p>'

    # Photo Unsplash (depuis dest._photo si présent)
    photo = dest.get('_photo', {})
    photo_url = photo.get('url', '')
    photo_credit_html = ''
    if photo.get('credit_name') and photo.get('credit_url'):
        photo_credit_html = (
            f'<a href="{photo["credit_url"]}" target="_blank" '
            f'rel="noopener nofollow">{photo["credit_name"]}</a> via Unsplash'
        )

    # Update month (mois courant localisé)
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

    return render_v6_full_page(page_data)
