"""
BestDateWeather — Shared generation utilities
==============================================
Common functions used by generate_pages.py.
Each function takes a `L` (lang config dict) parameter for language-specific strings.

Language dicts are built from locales/{lang}.json.
"""

import json, os

_LOCALE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'locales')
_locale_cache = {}

def _load_locale(lang):
    if lang not in _locale_cache:
        path = os.path.join(_LOCALE_DIR, f'{lang}.json')
        with open(path, encoding='utf-8') as f:
            _locale_cache[lang] = json.load(f)
    return _locale_cache[lang]


def build_lang(lang):
    """Build a lang dict for shared functions from locale JSON."""
    loc = _load_locale(lang)
    return {
        'months': loc['months'],
        'badge_excellent': loc['badges']['excellent'],
        'badge_good': loc['badges']['good'],
        'badge_fair': loc['badges']['fair'],
        'badge_poor': loc['badges']['poor'],
        'badge_tropical_good': loc['badges'].get('tropical_good', loc['badges']['good']),
        'badge_tropical_fair': loc['badges'].get('tropical_fair', loc['badges']['fair']),
        'tier_peak': loc['tiers']['peak'],
        'tier_low': loc['tiers']['low'],
        'tier_shoulder': loc['tiers']['shoulder'],
        'seasons': loc['season_months'],
        'verdict_excellent': loc['verdicts']['excellent'],
        'verdict_good': loc['verdicts']['good'],
        'verdict_fair': loc['verdicts']['fair'],
        'verdict_poor': loc['verdicts']['poor'],
        'table_aria': loc['table']['aria'],
        'table_headers': loc['table']['headers'],
        'table_ski_header': loc['table']['ski_header'],
        'th_tmin': loc.get('monthly', {}).get('th_tmin', loc['table'].get('th_tmin', 'Tmin')),
        'th_tmax': loc.get('monthly', {}).get('th_tmax', loc['table'].get('th_tmax', 'Tmax')),
        'th_rain': loc.get('monthly', {}).get('th_rain', loc['table'].get('th_rain', 'Rain')),
        'th_precip': loc.get('monthly', {}).get('th_precip', loc['table'].get('th_precip', 'Precip')),
        'th_sun': loc.get('monthly', {}).get('th_sun', loc['table'].get('th_sun', 'Sun')),
        'th_score': loc.get('monthly', {}).get('th_score', loc['table'].get('th_score', 'Score')),
        'legend_ideal': loc['table']['legend_ideal'],
        'legend_fair': loc['table']['legend_fair'],
        'legend_off': loc['table']['legend_off'],
        'legend_source': loc['table']['legend_source'],
        'legend_ideal_mtn': loc['table'].get('legend_ideal_mtn', loc['table']['legend_ideal']),
        'legend_off_mtn': loc['table'].get('legend_off_mtn', loc['table']['legend_off']),
        'val_missing_months': loc['validation']['missing_months'],
        'val_score_range': loc['validation']['score_range'],
        'val_class_invalid': loc['validation']['class_invalid'],
        'val_score_class': loc['validation']['score_class'],
        'val_no_climate': loc['validation']['no_climate'],
        'val_card_missing': loc['validation']['card_missing'],
        'lang': lang,
    }


# Backward-compatible exports
LANG_FR = build_lang('fr')
LANG_EN = build_lang('en')


# ── Weather emoji ─────────────────────────────────────────────────────────────

def _classify_rain_pattern(rain_pct, precip_mm, sun_h):
    """
    Distingue pluie bloquante vs averses tropicales courtes.

    burstiness = mm/j moyen / fréquence pluie → élevé = pluies concentrées
    Contexte : en climat convectif tropical, il peut pleuvoir 90% des jours
    mais seulement 1-2h en fin d'après-midi → journée exploitable.

    Returns: 'heavy_blocking' | 'blocking' | 'tropical_showers' | 'normal'
    """
    if rain_pct is None or rain_pct == 0:
        return 'normal'
    rain_freq = rain_pct / 100.0
    burstiness = (precip_mm or 0) / max(rain_freq, 0.05)

    # 1. Très bloquant : pic saison des pluies intense + peu de soleil
    is_heavy_blocking = (
        rain_pct >= 90 and
        precip_mm is not None and precip_mm >= 14 and
        sun_h is not None and sun_h < 9
    )

    # 2. Averses tropicales : convectif avec encore du soleil — vérifié AVANT blocking
    is_tropical_showers = (
        rain_pct >= 60 and
        precip_mm is not None and precip_mm >= 5 and
        sun_h is not None and sun_h >= 9.0 and
        burstiness >= 8
    )

    # 3. Bloquant : pluie fréquente + peu de soleil OU chronique sans intensité
    is_blocking = (
        rain_pct >= 65 and (
            (sun_h is not None and sun_h <= 5.0) or
            (sun_h is not None and sun_h <= 7.5 and rain_pct >= 70) or
            (precip_mm is not None and precip_mm >= 10 and burstiness < 10 and
             (sun_h is None or sun_h < 9.0))
        )
    )

    if is_heavy_blocking:
        return 'heavy_blocking'
    if is_tropical_showers:
        return 'tropical_showers'
    if is_blocking:
        return 'blocking'
    return 'normal'


def compute_weather_stability(rain_pct, precip_mm, sun_h):
    """
    Prévisibilité / stabilité météo du mois.
    Returns: 'stable' | 'variable' | 'unstable'
    """
    if rain_pct is None:
        return 'stable'
    if rain_pct < 25:
        return 'stable'
    rain_freq = rain_pct / 100.0
    burst = (precip_mm or 0) / max(rain_freq, 0.05)
    # Très peu de soleil + pluie → changeant
    if sun_h is not None and sun_h < 2 and rain_pct >= 40:
        return 'unstable'
    # Pluie fréquente + peu de soleil + pluie non concentrée
    if rain_pct >= 60 and (sun_h is None or sun_h < 5) and burst < 12:
        return 'unstable'
    if rain_pct >= 70 and (sun_h is None or sun_h < 7) and burst < 10:
        return 'unstable'
    # Pluie modérée à fréquente
    if rain_pct >= 35:
        return 'variable'
    return 'stable'


def classify_waves(wave_h, swell_period):
    """
    Classifie les conditions de mer depuis wave_height + swell_period.
    Returns: 'calm' | 'light' | 'surf' | 'rough' | None
    """
    if wave_h is None:
        return None
    if wave_h < 0.5:
        return 'calm'
    if wave_h < 0.9:
        return 'light'
    if wave_h >= 1.0 and swell_period is not None and swell_period >= 8:
        return 'surf'
    if wave_h >= 1.8:
        return 'rough'
    return None


# Traduction des noms de langues (source: FR dans country_info.json)
_LANG_NAMES = {
    'Afrikaans':       {'en': 'Afrikaans',   'es': 'Afrikáans',   'de': 'Afrikaans'},
    'Albanais':        {'en': 'Albanian',     'es': 'Albanés',     'de': 'Albanisch'},
    'Allemand':        {'en': 'German',       'es': 'Alemán',      'de': 'Deutsch'},
    'Amharique':       {'en': 'Amharic',      'es': 'Amhárico',    'de': 'Amharisch'},
    'Anglais':         {'en': 'English',      'es': 'Inglés',      'de': 'Englisch'},
    'Arabe':           {'en': 'Arabic',       'es': 'Árabe',       'de': 'Arabisch'},
    'Arménien':        {'en': 'Armenian',     'es': 'Armenio',     'de': 'Armenisch'},
    'Aymara':          {'en': 'Aymara',       'es': 'Aimara',      'de': 'Aymara'},
    'Azerbaïdjanais':  {'en': 'Azerbaijani',  'es': 'Azerbaiyano', 'de': 'Aserbaidschanisch'},
    'Berbère':         {'en': 'Berber',       'es': 'Bereber',     'de': 'Berberisch'},
    'Birman':          {'en': 'Burmese',      'es': 'Birmano',     'de': 'Burmesisch'},
    'Bislama':         {'en': 'Bislama',      'es': 'Bislama',     'de': 'Bislama'},
    'Bosnien':         {'en': 'Bosnian',      'es': 'Bosnio',      'de': 'Bosnisch'},
    'Bulgare':         {'en': 'Bulgarian',    'es': 'Búlgaro',     'de': 'Bulgarisch'},
    'Catalan':         {'en': 'Catalan',      'es': 'Catalán',     'de': 'Katalanisch'},
    'Chichewa':        {'en': 'Chichewa',     'es': 'Chichewa',    'de': 'Chichewa'},
    'Cingalais':       {'en': 'Sinhala',      'es': 'Cingalés',    'de': 'Singhalesisch'},
    'Cook Islands Maori': {'en': 'Cook Islands Māori', 'es': 'Maorí de Cook', 'de': 'Cookinseln-Māori'},
    'Coréen':          {'en': 'Korean',       'es': 'Coreano',     'de': 'Koreanisch'},
    'Croate':          {'en': 'Croatian',     'es': 'Croata',      'de': 'Kroatisch'},
    'Créole':          {'en': 'Creole',       'es': 'Criollo',     'de': 'Kreolisch'},
    'Danois':          {'en': 'Danish',       'es': 'Danés',       'de': 'Dänisch'},
    'Dhivehi':         {'en': 'Dhivehi',      'es': 'Dhivehi',     'de': 'Dhivehi'},
    'Dzongkha':        {'en': 'Dzongkha',     'es': 'Dzongkha',    'de': 'Dzongkha'},
    'Espagnol':        {'en': 'Spanish',      'es': 'Español',     'de': 'Spanisch'},
    'Estonien':        {'en': 'Estonian',     'es': 'Estonio',     'de': 'Estnisch'},
    'Fidjien':         {'en': 'Fijian',       'es': 'Fiyiano',     'de': 'Fidschianisch'},
    'Filipino':        {'en': 'Filipino',     'es': 'Filipino',    'de': 'Filipino'},
    'Finnois':         {'en': 'Finnish',      'es': 'Finlandés',   'de': 'Finnisch'},
    'Français':        {'en': 'French',       'es': 'Francés',     'de': 'Französisch'},
    'Gaélique':        {'en': 'Gaelic',       'es': 'Gaélico',     'de': 'Gälisch'},
    'Grec':            {'en': 'Greek',        'es': 'Griego',      'de': 'Griechisch'},
    'Guaraní':         {'en': 'Guaraní',      'es': 'Guaraní',     'de': 'Guaraní'},
    'Géorgien':        {'en': 'Georgian',     'es': 'Georgiano',   'de': 'Georgisch'},
    'Hindi':           {'en': 'Hindi',        'es': 'Hindi',       'de': 'Hindi'},
    'Hongrois':        {'en': 'Hungarian',    'es': 'Húngaro',     'de': 'Ungarisch'},
    'Hébreu':          {'en': 'Hebrew',       'es': 'Hebreo',      'de': 'Hebräisch'},
    'Indonésien':      {'en': 'Indonesian',   'es': 'Indonesio',   'de': 'Indonesisch'},
    'Irlandais':       {'en': 'Irish',        'es': 'Irlandés',    'de': 'Irisch'},
    'Islandais':       {'en': 'Icelandic',    'es': 'Islandés',    'de': 'Isländisch'},
    'Italien':         {'en': 'Italian',      'es': 'Italiano',    'de': 'Italienisch'},
    'Japonais':        {'en': 'Japanese',     'es': 'Japonés',     'de': 'Japanisch'},
    'Kazakh':          {'en': 'Kazakh',       'es': 'Kazajo',      'de': 'Kasachisch'},
    'Khmer':           {'en': 'Khmer',        'es': 'Jemer',       'de': 'Khmer'},
    'Kinyarwanda':     {'en': 'Kinyarwanda',  'es': 'Kinyarwanda', 'de': 'Kinyarwanda'},
    'Kirghiz':         {'en': 'Kyrgyz',       'es': 'Kirguís',     'de': 'Kirgisisch'},
    'Laotien':         {'en': 'Lao',          'es': 'Laosiano',    'de': 'Laotisch'},
    'Letton':          {'en': 'Latvian',      'es': 'Letón',       'de': 'Lettisch'},
    'Lituanien':       {'en': 'Lithuanian',   'es': 'Lituano',     'de': 'Litauisch'},
    'Macédonien':      {'en': 'Macedonian',   'es': 'Macedonio',   'de': 'Mazedonisch'},
    'Malais':          {'en': 'Malay',        'es': 'Malayo',      'de': 'Malaiisch'},
    'Malgache':        {'en': 'Malagasy',     'es': 'Malgache',    'de': 'Malagasy'},
    'Maltais':         {'en': 'Maltese',      'es': 'Maltés',      'de': 'Maltesisch'},
    'Mandarin':        {'en': 'Mandarin',     'es': 'Mandarín',    'de': 'Mandarin'},
    'Maori':           {'en': 'Māori',        'es': 'Maorí',       'de': 'Māori'},
    'Mongol':          {'en': 'Mongolian',    'es': 'Mongol',      'de': 'Mongolisch'},
    'Monténégrin':     {'en': 'Montenegrin',  'es': 'Montenegrino','de': 'Montenegrinisch'},
    'Ndebele':         {'en': 'Ndebele',      'es': 'Ndebele',     'de': 'Ndebele'},
    'Norvégien':       {'en': 'Norwegian',    'es': 'Noruego',     'de': 'Norwegisch'},
    'Néerlandais':     {'en': 'Dutch',        'es': 'Neerlandés',  'de': 'Niederländisch'},
    'Népalais':        {'en': 'Nepali',       'es': 'Nepalés',     'de': 'Nepalesisch'},
    'Ouzbek':          {'en': 'Uzbek',        'es': 'Uzbeko',      'de': 'Usbekisch'},
    'Palauan':         {'en': 'Palauan',      'es': 'Palauano',    'de': 'Palauisch'},
    'Papiamento':      {'en': 'Papiamento',   'es': 'Papiamento',  'de': 'Papiamento'},
    'Persan':          {'en': 'Persian',      'es': 'Persa',       'de': 'Persisch'},
    'Polonais':        {'en': 'Polish',       'es': 'Polaco',      'de': 'Polnisch'},
    'Portugais':       {'en': 'Portuguese',   'es': 'Portugués',   'de': 'Portugiesisch'},
    'Quechua':         {'en': 'Quechua',      'es': 'Quechua',     'de': 'Quechua'},
    'Roumain':         {'en': 'Romanian',     'es': 'Rumano',      'de': 'Rumänisch'},
    'Russe':           {'en': 'Russian',      'es': 'Ruso',        'de': 'Russisch'},
    'Samoan':          {'en': 'Samoan',       'es': 'Samoano',     'de': 'Samoanisch'},
    'Serbe':           {'en': 'Serbian',      'es': 'Serbio',      'de': 'Serbisch'},
    'Setswana':        {'en': 'Setswana',     'es': 'Setswana',    'de': 'Setswana'},
    'Shona':           {'en': 'Shona',        'es': 'Shona',       'de': 'Shona'},
    'Slovaque':        {'en': 'Slovak',       'es': 'Eslovaco',    'de': 'Slowakisch'},
    'Slovène':         {'en': 'Slovenian',    'es': 'Esloveno',    'de': 'Slowenisch'},
    'Sotho':           {'en': 'Sotho',        'es': 'Sotho',       'de': 'Sotho'},
    'Suédois':         {'en': 'Swedish',      'es': 'Sueco',       'de': 'Schwedisch'},
    'Swahili':         {'en': 'Swahili',      'es': 'Swahili',     'de': 'Swahili'},
    'Tadjik':          {'en': 'Tajik',        'es': 'Tayiko',      'de': 'Tadschikisch'},
    'Tahitien':        {'en': 'Tahitian',     'es': 'Tahitiano',   'de': 'Tahitianisch'},
    'Tamoul':          {'en': 'Tamil',        'es': 'Tamil',       'de': 'Tamilisch'},
    'Tchèque':         {'en': 'Czech',        'es': 'Checo',       'de': 'Tschechisch'},
    'Thaï':            {'en': 'Thai',         'es': 'Tailandés',   'de': 'Thaiisch'},
    'Tok Pisin':       {'en': 'Tok Pisin',    'es': 'Tok Pisin',   'de': 'Tok Pisin'},
    'Tongan':          {'en': 'Tongan',       'es': 'Tongano',     'de': 'Tongaisch'},
    'Turc':            {'en': 'Turkish',      'es': 'Turco',       'de': 'Türkisch'},
    'Ukrainien':       {'en': 'Ukrainian',    'es': 'Ucraniano',   'de': 'Ukrainisch'},
    'Vietnamien':      {'en': 'Vietnamese',   'es': 'Vietnamita',  'de': 'Vietnamesisch'},
    'Wolof':           {'en': 'Wolof',        'es': 'Wólof',       'de': 'Wolof'},
    'Xhosa':           {'en': 'Xhosa',        'es': 'Xhosa',       'de': 'Xhosa'},
    'Zulu':            {'en': 'Zulu',         'es': 'Zulú',        'de': 'Zulu'},
}

def _translate_lang(lang_fr: str, target_lang: str) -> str:
    """Traduit un nom de langue depuis le français vers la langue cible."""
    if target_lang in ('fr',):
        return lang_fr
    entry = _LANG_NAMES.get(lang_fr, {})
    key = 'en' if target_lang in ('en', 'en-us') else target_lang
    return entry.get(key, lang_fr)


def weather_emoji(tmax, rain_pct, sun_h=None, precip_mm=None, score=None):
    """Return a weather emoji based on temperature, rain, sunshine, intensity.

    Distingue 4 patterns pluie :
    - heavy_blocking  : ⛈️  (saison des pluies intense)
    - blocking        : 🌧️  (pluie fréquente et gênante)
    - tropical_showers: 🌦️  (averses courtes, journée exploitable)
    - normal          : ☀️/🌤️/⛅/🌦️ selon température et fréquence
    """
    # ── Extreme cold ──
    if tmax < 0:
        return '❄️'
    if tmax <= 4:
        return '🌨️'
    # ── Extreme heat (sec — humide pris en charge plus bas) ──
    if tmax >= 38:
        return '🥵'

    # ── Classify rain pattern (tropical awareness) ──
    pattern = _classify_rain_pattern(rain_pct, precip_mm, sun_h)

    if pattern == 'heavy_blocking':
        return '⛈️'
    if pattern == 'blocking':
        return '🌧️'
    if pattern == 'tropical_showers':
        # Averses tropicales courtes : positif mais honnête
        if tmax >= 36:
            return '🥵'   # chaud + humide malgré tout
        if sun_h is not None and sun_h >= 11:
            return '🌦️'   # beaucoup de soleil + averses
        return '🌦️'

    # ── Normal path — tempéré ou tropical sec ──
    if tmax >= 36:
        return '🥵'
    if tmax >= 25:
        # Tropical sans pluie problématique
        if sun_h is not None and sun_h >= 10:
            if rain_pct < 25:  return '☀️'
            if rain_pct < 55:  return '🌤️'
            if rain_pct < 80:  return '⛅'
            return '🌦️'
        if sun_h is not None and sun_h >= 8:
            if rain_pct < 30:  return '☀️'
            if rain_pct < 55:  return '🌤️'
            if rain_pct < 75:  return '⛅'
            return '🌦️'
        if rain_pct < 25:  return '☀️'
        if rain_pct < 50:  return '🌤️'
        if rain_pct < 70:  return '🌦️'
        return '🌧️'

    # ── Tempéré (tmax 5-24) ──
    if rain_pct >= 65:  return '🌧️'
    if rain_pct >= 50:  return '🌦️'
    if tmax >= 22 and rain_pct < 50 and sun_h is not None and sun_h >= 10:
        return '🌤️'
    if tmax >= 18 and rain_pct < 35:  return '🌤️'
    if tmax >= 18 and rain_pct < 45 and sun_h is not None and sun_h >= 9:
        return '🌤️'
    if rain_pct >= 40 and tmax >= 12:  return '🌦️'
    if tmax >= 15 and rain_pct < 40:   return '⛅'
    if tmax >= 12 and rain_pct < 40:   return '⛅'
    if rain_pct >= 35 and tmax >= 5:   return '🌦️'
    return '🌫️'


# ── Shared functions ──────────────────────────────────────────────────────────

def score_badge(score, classe=None, L=None, is_tropical=False):
    """Badge verdict aligned with editorial class from CSV."""
    if L is None:
        L = LANG_FR
    if classe == 'rec':
        if score >= 9.0: return '#dcfce7', '#16a34a', L['badge_excellent']
        return '#dcfce7', '#16a34a', L['badge_good']
    if classe == 'mid':
        return '#fef9c3', '#ca8a04', L['badge_fair']
    if classe == 'avoid':
        return '#fee2e2', '#dc2626', L['badge_poor']
    if score >= 9.0: return '#dcfce7', '#16a34a', L['badge_excellent']
    if is_tropical:
        if score >= 7.5: return '#dcfce7', '#16a34a', L['badge_tropical_good']
        if score >= 5.5: return '#e0f2fe', '#0369a1', L['badge_tropical_fair']
        return '#fee2e2', '#dc2626', L['badge_poor']
    if score >= 7.5: return '#dcfce7', '#16a34a', L['badge_good']
    if score >= 6.0: return '#fef9c3', '#ca8a04', L['badge_fair']
    return '#fee2e2', '#dc2626', L['badge_poor']


def best_months(months, L=None):
    """Return list of months tied for highest score."""
    if L is None:
        L = LANG_FR
    max_score = max(m['score'] for m in months)
    return [L['months'][i] for i, m in enumerate(months) if m['score'] == max_score]


def budget_tier(score, all_scores, L=None):
    """Relative tier: top 4 = Peak, bottom 4 = Low, rest = Shoulder."""
    if L is None:
        L = LANG_FR
    sorted_scores = sorted(all_scores, reverse=True)
    n = len(sorted_scores)
    top = sorted_scores[min(3, n-1)]
    bottom = sorted_scores[max(n-5, 0)]
    if score >= top:   return L['tier_peak']
    if score <= bottom: return L['tier_low']
    return L['tier_shoulder']


def seasonal_stats(months, L=None):
    """Compute stats per season."""
    if L is None:
        L = LANG_FR
    result = {}
    for name, idxs in L['seasons'].items():
        ms = [months[i] for i in idxs]
        avg_t  = round(sum(m['tmax'] for m in ms) / len(ms))
        avg_tmin = round(sum(m['tmin'] for m in ms) / len(ms))
        avg_r  = round(sum(m['rain_pct'] for m in ms) / len(ms))
        avg_s  = round(sum(m['sun_h'] for m in ms) / len(ms), 1)
        avg_sc = round(sum(m['score'] for m in ms) / len(ms), 1)
        if avg_sc >= 8.5:  verdict = L['verdict_excellent']
        elif avg_sc >= 7.0: verdict = L['verdict_good']
        elif avg_sc >= 5.5: verdict = L['verdict_fair']
        else:               verdict = L['verdict_poor']
        result[name] = {'tmax': avg_t, 'tmin': avg_tmin, 'rain_pct': avg_r, 'sun_h': avg_s,
                        'score': avg_sc, 'verdict': verdict}
    return result


# ── Unit conversion helpers ───────────────────────────────────────────────

def c_to_f(celsius):
    """Celsius → Fahrenheit, rounded to nearest integer."""
    return round(celsius * 9 / 5 + 32)


def mm_to_in(mm):
    """Millimetres → inches, 1 decimal place."""
    return round(mm / 25.4, 1)


def fmt_temp(value, cfg):
    """Format a temperature with correct unit symbol for the locale.

    Args:
        value : int|float — always stored in °C in the data
        cfg   : lang config dict (must have cfg['imperial'] bool)
    Returns e.g. "72°F" or "22°C"
    """
    if cfg.get('imperial'):
        return f"{c_to_f(value)}°F"
    return f"{value}°C"


def fmt_precip(value_mm, cfg):
    """Format precipitation with correct unit for the locale.

    Args:
        value_mm : float — always stored in mm in the data
        cfg      : lang config dict
    Returns e.g. "0.4in" or "9.7"  (no unit on metric — matches existing display)
    """
    if cfg.get('imperial'):
        return f"{mm_to_in(value_mm)}in"
    return f"{value_mm:.1f}"


def fill_tpl(template, cfg, **kwargs):
    """Fill a locale template string.

    If cfg['imperial'], substitutes °C→°F and mm→in in the template string.
    Only replaces in literal text, not inside {format_keys}, to avoid corrupting
    key names when °C appears adjacent to a format placeholder.
    Numeric values must already be converted before calling (use c_to_f/mm_to_in).
    """
    if cfg.get('imperial'):
        # Split on {key} tokens, replace only in literal parts
        import re as _re
        parts = _re.split(r'(\{[^}]*\})', template)
        parts = [p if p.startswith('{') else p.replace('°C', '°F').replace('mm', 'in')
                 for p in parts]
        template = ''.join(parts)
    return template.format(**kwargs)


def bar_chart(pct, max_val=100):
    """ASCII bar chart (language-independent)."""
    filled = round((pct / max_val) * 10)
    return '█' * filled + '░' * (10 - filled)



def ressenti(tmax, dew, lang='fr'):
    """Return (label, color) for thermal comfort. Seuils calibrés GPT/Claude."""
    LABELS = {
        'froid':          {'fr':'Froid',         'en':'Cold',         'en-us':'Cold',       'es':'Frío',        'de':'Kalt'},
        'frais':          {'fr':'Frais',          'en':'Fresh',        'en-us':'Fresh',      'es':'Fresco',      'de':'Frisch'},
        'confortable':    {'fr':'Confortable',    'en':'Comfortable',  'en-us':'Comfortable','es':'Cómodo',      'de':'Angenehm'},
        'lourd':          {'fr':'Lourd',          'en':'Oppressive',   'en-us':'Oppressive', 'es':'Pesado',      'de':'Schwül'},
        'chaleur_humide': {'fr':'Chaleur humide', 'en':'Humid heat',   'en-us':'Humid heat', 'es':'Calor húmedo','de':'Feuchte Hitze'},
        'tres_chaud':     {'fr':'Très chaud',     'en':'Very hot',     'en-us':'Very hot',   'es':'Muy caluroso','de':'Sehr heiß'},
    }
    COLORS = {'froid':'#7c3aed','frais':'#0ea5e9','confortable':'#22c55e',
              'lourd':'#f97316','chaleur_humide':'#ef4444','tres_chaud':'#dc2626'}
    if tmax is None or dew is None:
        return None, None
    if tmax < 0:                      key = 'froid'
    elif dew < 16 and tmax < 20:      key = 'frais'
    elif dew < 18 and tmax <= 32:     key = 'confortable'
    elif dew <= 22 and tmax <= 38:    key = 'lourd'
    elif dew > 22:                    key = 'chaleur_humide'
    else:                             key = 'tres_chaud'
    l = lang if lang in ('fr','en','en-us','es','de') else 'en'
    return LABELS[key][l], COLORS[key]

def climate_table_html(months, nom, is_mountain=False, L=None):
    """Generate climate table HTML."""
    if L is None:
        L = LANG_FR
    # Dominant ressenti: if ≥9/12 months identical → header badge, no per-row
    _lang_r = L.get('lang', 'fr')
    _all_r = [ressenti(m['tmax'], m.get('dew_point'), _lang_r)[0] for m in months]
    _dom_lbl = max(set(l for l in _all_r if l), key=lambda x: _all_r.count(x)) if any(_all_r) else None
    _dom_cnt = _all_r.count(_dom_lbl) if _dom_lbl else 0
    _show_row_r = _dom_cnt < 9
    _dom_col = ressenti(months[0]['tmax'], months[0].get('dew_point'), _lang_r)[1] if not _show_row_r else None
    _header_badge = (
        f'<div class="table-ressenti-badge" style="margin-bottom:8px">'
        f'<span style="font-size:11px;font-weight:700;color:{_dom_col}">{_dom_lbl}</span>'
        f'<span style="font-size:10px;color:#aaa;margin-left:6px">({_dom_cnt}/12 mois)</span>'
        f'</div>'
    ) if not _show_row_r and _dom_lbl else ''

    rows = ''
    for i, m in enumerate(months):
        cls = m['classe']
        ski_col = ''
        if is_mountain:
            from scoring import compute_ski_score, best_class
            ski = compute_ski_score(m['tmax'], m['rain_pct'], m['sun_h'])
            cls = best_class(m['classe'], ski)
            ski_col = f'<td>{ski:.1f}/10</td>'
        rows += (f'<tr class="{cls}" data-tmax="{m["tmax"]}" '
                 f'data-rain="{m["rain_pct"]}" data-sun="{m["sun_h"]}">'
                 f'<td>{weather_emoji(m["tmax"], m["rain_pct"], m["sun_h"], m.get("precip"))} {L["months"][i]}</td>'
                 f'<td data-label="{L["th_tmin"]}">{fmt_temp(m["tmin"], L)}</td>'
                 f'<td data-label="{L["th_tmax"]}">{fmt_temp(m["tmax"], L)}</td>'
                 f'<td data-label="{L["th_rain"]}">{m["rain_pct"]}%</td>'
                 f'<td data-label="{L["th_precip"]}">{fmt_precip(m["precip"], L)}</td>'
                 f'<td data-label="{L["th_sun"]}">{m["sun_h"]}h</td>'
                 '<td data-label="' + L['th_score'] + '">' +
                 f'{m["score"]:.1f}/10' +
                 (lambda r,c: f'<br><span style="font-size:9px;font-weight:700;color:{c};letter-spacing:.2px">{r}</span>' if (r and _show_row_r) else '')(*ressenti(m['tmax'], m.get('dew_point'), L.get('lang','fr'))) +
                 f'</td>{ski_col}</tr>\n')
    ski_header = L['table_ski_header'] if is_mountain else ''
    wrap_class = 'climate-table-wrap mountain' if is_mountain else 'climate-table-wrap'
    legend_ideal_label = L.get('legend_ideal_mtn', L['legend_ideal']) if is_mountain else L['legend_ideal']
    legend_off_label   = L.get('legend_off_mtn',   L['legend_off'])   if is_mountain else L['legend_off']
    return f'''{_header_badge}<div class="{wrap_class}">
 <table class="climate-table climate-table--horizontal" aria-label="{L['table_aria'].format(nom=nom)}">
 <thead><tr>{L['table_headers']}{ski_header}</tr></thead>
 <tbody>{rows}</tbody>
 </table>
</div>
<div class="table-legend">
 <span><span class="legend-dot legend-rec"></span>{legend_ideal_label}</span>
 <span><span class="legend-dot legend-mid"></span>{L['legend_fair']}</span>
 <span><span class="legend-dot legend-avoid"></span>{legend_off_label}</span>
 <span class="ml-auto">{L['legend_source']}</span>
</div>'''


def validate_climate(climate, months_list, L=None):
    """Validate climate data consistency. Returns list of error strings."""
    if L is None:
        L = LANG_FR
    errors = []
    for slug, months in climate.items():
        if None in months:
            missing = [L['months'][i] for i, m in enumerate(months) if m is None]
            errors.append(L['val_missing_months'].format(slug=slug, missing=missing))
            continue

        scores = [m['score'] for m in months]
        classes = [m['classe'] for m in months]

        for i, (s, c) in enumerate(zip(scores, classes)):
            month = L['months'][i]
            if not (0 <= s <= 10):
                errors.append(L['val_score_range'].format(slug=slug, month=month, score=s))
            if c not in ('rec', 'mid', 'avoid'):
                errors.append(L['val_class_invalid'].format(slug=slug, month=month, cls=c))
            if c == 'rec' and s < 6.5:
                errors.append(L['val_score_class'].format(slug=slug, month=month, score=s, cls=c))
            elif c == 'avoid' and s > 4.5:
                errors.append(L['val_score_class'].format(slug=slug, month=month, score=s, cls=c))
    return errors


def footer_ranking_html(lang, alt_links):
    """
    Generate a unified footer for ranking/pillar pages (classements + piliers).
    
    Args:
        lang: language code ('fr', 'en', 'es', ...)
        alt_links: list of dicts [{url, flag, label}] for cross-language links
                   e.g. [{'url': 'en/best-dest.html', 'flag': 'flags/gb.png', 'label': 'English'}]
    
    Returns: HTML string
    """
    loc = _load_locale(lang)
    fc = loc['ranking_footer']

    alt_html = ''.join(
        f'<a href="{a["url"]}" style="color:rgba(255,255,255,.7)">'
        f'<img loading="lazy" src="{a["flag"]}" width="20" height="15" alt="" '
        f'style="vertical-align:middle;border-radius:2px"> {a["label"]}</a>'
        for a in alt_links
    )
    alt_sep = ' · '.join(
        f'<a href="{a["url"]}" style="color:rgba(255,255,255,.7)">'
        f'<img loading="lazy" src="{a["flag"]}" width="20" height="15" alt="" '
        f'style="vertical-align:middle;border-radius:2px"> {a["label"]}</a>'
        for a in alt_links
    )

    alt_nowrap = ' · '.join(
        f'<span style="white-space:nowrap"><a href="{a["url"]}" style="color:rgba(255,255,255,.7)">'
        f'<img loading="lazy" src="{a["flag"]}" width="20" height="15" alt="" '
        f'style="vertical-align:middle;border-radius:2px"> {a["label"]}</a></span>'
        for a in alt_links
    )

    return f"""<footer>
<p style="color:rgba(255,255,255,.7);font-size:13px;font-weight:700;margin-bottom:8px">bestdateweather.com</p>
<p><a href="https://open-meteo.com/" rel="noopener" style="color:rgba(255,255,255,.7)">{fc['data_by']}</a> · {fc['sources']}</p>
<p style="margin-top:8px"><a href="{fc['methodology_url']}" style="color:rgba(255,255,255,.7)">{fc['methodology_label']}</a> · <a href="{fc['about_url']}" style="color:rgba(255,255,255,.7)">{fc['about_label']}</a> · <a href="{fc['faq_url']}" style="color:rgba(255,255,255,.7)">{fc['faq_label']}</a> · <a href="{fc['app_url']}" style="color:rgba(255,255,255,.7)">{fc['app_label']}</a> · <a href="{fc['widget_url']}" style="color:rgba(255,255,255,.7)">{fc['widget_label']}</a></p>
{f'<p style="margin-top:8px">{alt_nowrap}</p>' if alt_nowrap else ''}
<p style="margin-top:8px;font-size:11px;opacity:.6"><a href="{fc['legal_url']}" style="color:rgba(255,255,255,.7)">{fc['legal_label']}</a> · <a href="{fc['privacy_url']}" style="color:rgba(255,255,255,.7)">{fc['privacy_label']}</a> · <a href="{fc['contact_url']}" style="color:rgba(255,255,255,.7)">{fc['contact_label']}</a></p>
</footer>"""


def shared_nav_html(home_href, cta_label, share_label="Share", slug_fr=None):
    """Nav using same CSS classes as fiche pages (requires style.css to be loaded)."""
    svg_share = ('<svg viewBox="0 0 24 24" width="18" height="18" fill="none" '
                 'stroke="currentColor" stroke-width="2">'
                 '<circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/>'
                 '<circle cx="18" cy="19" r="3"/>'
                 '<path d="M8.59 13.51l6.83 3.98M15.41 6.51l-6.82 3.98"/></svg>')
    svg_heart = ('<svg viewBox="0 0 24 24" width="18" height="18" fill="none" '
                 'stroke="currentColor" stroke-width="2">'
                 '<path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06'
                 'a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06'
                 'a5.5 5.5 0 0 0 0-7.78z"/></svg>')

    fav_btn = (
        f'<button id="btn-fav" class="nav-share" style="display:flex" '
        f'data-slug="{slug_fr}" onclick="bdwToggleFav(this)" '
        f'aria-label="Ajouter aux favoris" aria-pressed="false">'
        f'{svg_heart}</button>'
    ) if slug_fr else ''

    return (
        f'<nav>'
        f'<a class="nav-brand" href="{home_href}">Best<em>Date</em>Weather</a>'
        f'<div class="nav-actions">'
        f'{fav_btn}'
        f'<button class="nav-share" onclick="shareThis()" aria-label="{share_label}">'
        f'{svg_share}</button>'
        f'<a class="nav-cta" href="{home_href}">{cta_label}</a>'
        f'</div></nav>'
    )


# ── Travel Info Widget ────────────────────────────────────────────────────────

import json as _json
import os as _os

_COUNTRY_INFO = None

def _load_country_info():
    global _COUNTRY_INFO
    if _COUNTRY_INFO is None:
        p = _os.path.join(_os.path.dirname(__file__), '..', 'data', 'country_info.json')
        _COUNTRY_INFO = _json.load(open(p, encoding='utf-8'))
    return _COUNTRY_INFO


def _gpi_label(gpi: float, lang: str = 'fr') -> tuple:
    """Return (label, color_class) for a GPI score."""
    labels = {
        'fr': [
            (1.5, 'Très sûr', 'safe-high'),
            (2.0, 'Sûr',      'safe-mid'),
            (2.5, 'Prudence', 'safe-low'),
            (3.0, 'Vigilance','safe-warn'),
            (9.9, 'Dangereux','safe-danger'),
        ],
        'en': [
            (1.5, 'Very Safe',          'safe-high'),
            (2.0, 'Safe',               'safe-mid'),
            (2.5, 'Exercise Caution',   'safe-low'),
            (3.0, 'High Caution',       'safe-warn'),
            (9.9, 'High Risk',          'safe-danger'),
        ],
    }
    for threshold, label, cls in labels.get(lang, labels['en']):
        if gpi < threshold:
            return label, cls
    return labels.get(lang, labels['en'])[-1][1], labels.get(lang, labels['en'])[-1][2]


def _mae_label(risk_level: int, lang: str = 'fr') -> tuple:
    """Return (label, color_class, icon) for a MAE risk level (1–4)."""
    data = {
        'fr': {
            1: ('Vigilance normale',     'mae-1', '🟢'),
            2: ('Vigilance renforcée',   'mae-2', '🟡'),
            3: ('Déconseillé',           'mae-3', '🟠'),
            4: ('Formellement déconseillé', 'mae-4', '🔴'),
        },
        'en': {
            1: ('Normal vigilance',      'mae-1', '🟢'),
            2: ('High vigilance',        'mae-2', '🟡'),
            3: ('Avoid if possible',     'mae-3', '🟠'),
            4: ('Do not travel',         'mae-4', '🔴'),
        },
        'es': {
            1: ('Vigilancia normal',     'mae-1', '🟢'),
            2: ('Vigilancia reforzada',  'mae-2', '🟡'),
            3: ('Desaconsejado',         'mae-3', '🟠'),
            4: ('Formalmente desaconsejado', 'mae-4', '🔴'),
        },
        'de': {
            1: ('Normale Wachsamkeit',   'mae-1', '🟢'),
            2: ('Erhöhte Wachsamkeit',   'mae-2', '🟡'),
            3: ('Nicht empfohlen',       'mae-3', '🟠'),
            4: ('Dringend abgeraten',    'mae-4', '🔴'),
        },
    }
    lang_key = 'fr' if lang == 'fr' else ('es' if lang == 'es' else ('de' if lang == 'de' else 'en'))
    lvl = max(1, min(4, risk_level))
    return data[lang_key][lvl]


def get_risk_level(pays: str) -> int:
    """Return risk level (1-4) for a country from country_info.json."""
    info = _load_country_info().get(pays, {})
    return max(1, min(4, info.get('risk_level', 1)))

def get_country_iso2(pays: str) -> str:
    """Return ISO2 code stored in country_info, fallback empty string."""
    info = _load_country_info().get(pays, {})
    return info.get('iso2', '')

def get_mae_label(pays: str, lang: str = 'fr') -> tuple:
    """Return (label, cls, icon) for the risk level of a country."""
    return _mae_label(get_risk_level(pays), lang)

def travel_info_widget(pays: str, nom: str, lang: str = 'fr', L: dict = None, iso2: str = '') -> str:
    """
    Generates the Essential Travel Info widget for a destination page.
    Returns empty string if country data unavailable.
    """
    info = _load_country_info().get(pays)
    if not info:
        return ''

    # Labels by language
    lbl = {
        'fr': {
            'title': f'Infos pratiques — {nom}',
            'currency': 'Monnaie',
            'language': 'Langue(s)',
            'drive': 'Conduite',
            'drive_left': 'À gauche',
            'drive_right': 'À droite',
            'safety': 'Sécurité',
            'gpi_note': 'Global Peace Index : 1 = très pacifique, 5 = peu pacifique',
            'source': 'Source : Institute for Economics & Peace',
            'more': '+{n} autres',
            'budget': 'Budget',
            'budget_labels': ['Économique', 'Abordable', 'Modéré', 'Coûteux', 'Très coûteux'],
            'budget_icons': ['💚', '💚', '🟡', '🟠', '💎'],
        },
        'en': {
            'title': f'Essential Travel Info — {nom}',
            'currency': 'Currency',
            'language': 'Language(s)',
            'drive': 'Driving',
            'drive_left': 'Left side',
            'drive_right': 'Right side',
            'safety': 'Safety',
            'gpi_note': 'Global Peace Index: 1 = most peaceful, 5 = least peaceful',
            'source': 'Source: Institute for Economics & Peace',
            'more': '+{n} more',
            'budget': 'Budget',
            'budget_labels': ['Budget-friendly', 'Affordable', 'Moderate', 'Expensive', 'Very expensive'],
            'budget_icons': ['💚', '💚', '🟡', '🟠', '💎'],
        },
    }.get(lang, {
        'title': f'Essential Travel Info — {nom}',
        'currency': 'Currency',
        'language': 'Language(s)',
        'drive': 'Driving',
        'drive_left': 'Left side',
        'drive_right': 'Right side',
        'safety': 'Safety',
        'gpi_note': 'Global Peace Index: 1 = most peaceful, 5 = least peaceful',
        'source': 'Source: Institute for Economics & Peace',
        'more': '+{n} more',
        'budget': 'Budget',
        'budget_labels': ['Budget-friendly', 'Affordable', 'Moderate', 'Expensive', 'Very expensive'],
        'budget_icons': ['💚', '💚', '🟡', '🟠', '💎'],
    })

    # Currency chip
    currency_html = (
        f'<div class="ti-chip">'
        f'<div class="ti-chip-label">{lbl["currency"]}</div>'
        f'<div class="ti-chip-row">'
        f'<span class="ti-chip-icon">💰</span>'
        f'<span class="ti-chip-val">{info["currency"]}</span>'
        f'</div>'
        f'<div class="ti-chip-sub">{info["currency_symbol"]} · {info["currency_name"]}</div>'
        f'</div>'
    )

    # Languages chip
    langs = info.get('languages', [])
    main_lang = _translate_lang(langs[0], lang) if langs else '–' 
    extra = len(langs) - 1
    extra_html = (f' <span class="ti-chip-more">+{extra}</span>') if extra > 0 else ''
    language_html = (
        f'<div class="ti-chip">'
        f'<div class="ti-chip-label">{lbl["language"]}</div>'
        f'<div class="ti-chip-row">'
        f'<span class="ti-chip-icon">🗣️</span>'
        f'<span class="ti-chip-val">{main_lang}{extra_html}</span>'
        f'</div>'
        f'</div>'
    )

    # Driving chip
    drive = info.get('drive', 'right')
    drive_label = lbl['drive_left'] if drive == 'left' else lbl['drive_right']
    drive_icon = '🚗⬅️' if drive == 'left' else '🚗➡️'
    driving_html = (
        f'<div class="ti-chip">'
        f'<div class="ti-chip-label">{lbl["drive"]}</div>'
        f'<div class="ti-chip-row">'
        f'<span class="ti-chip-icon">{drive_icon}</span>'
        f'<span class="ti-chip-val">{drive_label}</span>'
        f'</div>'
        f'</div>'
    )

    # Safety chip — MAE advisory level (primary) + GPI (subtitle)
    risk_level = info.get('risk_level', 1)
    gpi = info.get('gpi', 2.0)
    gpi_year = info.get('gpi_year', 2024)
    mae_label, mae_cls, mae_icon = _mae_label(risk_level, lang)
    safety_html = (
        f'<div class="ti-chip ti-chip--{mae_cls}" data-advisory-cc="{iso2.upper() if iso2 else ""}" data-advisory-lang="{lang}">'
        f'<div class="ti-chip-label">{lbl["safety"]}</div>'
        f'<div class="ti-chip-row">'
        f'<span class="ti-chip-icon">{mae_icon}</span>'
        f'<span class="ti-chip-val ti-chip-val--{mae_cls}">{mae_label}</span>'
        f'</div>'
        f'<div class="ti-chip-sub">GPI {gpi:.2f}</div>'
        f'</div>'
    )

    # Budget chip
    budget_idx = info.get('budget_index', 3)
    bidx = max(1, min(5, budget_idx)) - 1
    budget_label = lbl['budget_labels'][bidx]
    budget_icon  = lbl['budget_icons'][bidx]
    budget_html = (
        f'<div class="ti-chip ti-chip--budget-{budget_idx}">'
        f'<div class="ti-chip-label">{lbl["budget"]}</div>'
        f'<div class="ti-chip-row">'
        f'<span class="ti-chip-icon">{budget_icon}</span>'
        f'<span class="ti-chip-val ti-chip-val--budget-{budget_idx}">{budget_label}</span>'
        f'</div>'
        f'</div>'
    )

    # Safety detail box
    mae_source_lbl = {
        'fr': 'Conseils aux voyageurs MAE',
        'en': 'French Foreign Ministry advisory',
        'en-us': 'French Foreign Ministry advisory',
        'es': 'Consejos viajero MAE Francia',
        'de': 'Reisehinweise Außenministerium',
    }
    gpi_sub = lbl["gpi_note"].replace(' : ', ': ')
    safety_detail = (
        f'<div class="ti-safety-detail" id="ti-advisory-note-{iso2.upper() if iso2 else pays[:3]}">'
        f'<span class="ti-safety-note">'
        f'{mae_source_lbl.get(lang, mae_source_lbl["en"])}'
        f' &nbsp;·&nbsp; '
        f'<span class="ti-safety-source">{gpi_sub} ({gpi_year})</span>'
        f'</span>'
        f'<span class="ti-advisory-live" style="display:none;font-size:10px;color:#888;margin-left:6px"></span>'
        f'</div>'
    )

    return (
        f'<section class="travel-info-widget">'
        f'<h3 class="ti-title">{lbl["title"]}</h3>'
        f'<div class="ti-chips">'
        f'{currency_html}'
        f'{language_html}'
        f'{driving_html}'
        f'{safety_html}'
        f'{budget_html}'
        f'</div>'
        f'{safety_detail}'
        f'</section>'
    )


# ── Climate Trend SVG ─────────────────────────────────────────────────────────

_CLIMATE_TREND = None

def _load_climate_trend():
    global _CLIMATE_TREND
    if _CLIMATE_TREND is None:
        p = _os.path.join(_os.path.dirname(__file__), '..', 'data', 'climate_trend.json')
        if _os.path.exists(p):
            _CLIMATE_TREND = _json.load(open(p, encoding='utf-8'))
        else:
            _CLIMATE_TREND = {}
    return _CLIMATE_TREND


def climate_trend_section(slug_fr: str, nom: str, lang: str = 'fr', C: dict = None,
                           lat: float = None, lon: float = None) -> str:
    """
    Generates climate trend section with SVG chart + CMIP6 rate.
    Supports both slug_fr keys and lat/lon coord keys.
    Returns empty string if data unavailable.
    """
    db = _load_climate_trend()
    # Try coord key first (format: "lat,lon" with 2 decimals)
    trend = None
    if lat is not None and lon is not None:
        coord_key = f"{float(lat):.2f},{float(lon):.2f}"
        trend = db.get(coord_key)
    if trend is None:
        trend = db.get(slug_fr)
    if not trend:
        return ''

    # Support both formats:
    # New: {years:[...], tmax:[...], tmin:[...], tmoy:[...], cmip6_rate: X}
    # Old: {annual: {"2016": {tmax, tmin, tmean}, ...}, cmip6_trend_per_decade: X}
    if 'annual' in trend:
        ann = trend['annual']
        years = sorted(int(y) for y in ann.keys())
        tmax  = [ann[str(y)]['tmax']  for y in years]
        tmin  = [ann[str(y)]['tmin']  for y in years]
        tmoy  = [ann[str(y)]['tmean'] for y in years]
        cmip6 = trend.get('cmip6_trend_per_decade')
    else:
        years = trend.get('years', [])
        tmax  = trend.get('tmax', [])
        tmin  = trend.get('tmin', [])
        tmoy  = trend.get('tmoy', [])
        cmip6 = trend.get('cmip6_rate')

    # Filter valid data points
    valid = [(years[i], tmax[i], tmin[i], tmoy[i])
             for i in range(len(years))
             if tmax[i] is not None and tmin[i] is not None]
    if len(valid) < 3:
        return ''

    # Labels
    if lang == 'fr':
        title_lbl  = f'Températures annuelles — {nom}'
        sec_lbl    = 'TENDANCE CLIMATIQUE'
        tmax_lbl   = 'T° max'
        tmin_lbl   = 'T° min'
        tmoy_lbl   = 'Moyenne'
        cmip6_lbl  = 'Tendance projetée'
        cmip6_unit = '°C/décennie (CMIP6 SSP2)'
        note_lbl   = 'Moyennes annuelles ERA5 · données 2016–2025'
    else:
        title_lbl  = f'Annual Temperatures — {nom}'
        sec_lbl    = 'CLIMATE TREND'
        tmax_lbl   = 'Max temp'
        tmin_lbl   = 'Min temp'
        tmoy_lbl   = 'Average'
        cmip6_lbl  = 'Projected trend'
        cmip6_unit = '°C/decade (CMIP6 SSP2)'
        note_lbl   = 'Annual ERA5 means · 2016–2025 data'

    # SVG dimensions
    W, H = 560, 220
    PAD_L, PAD_R, PAD_T, PAD_B = 40, 16, 20, 36

    all_vals = [v for row in [tmax, tmin, tmoy] for v in row if v is not None]
    _raw_min = min(all_vals)
    _raw_max = max(all_vals)
    _span = max(_raw_max - _raw_min, 4)  # min 4°C visible range
    y_min = _raw_min - _span * 0.25
    y_max = _raw_max + _span * 0.25
    y_range = y_max - y_min or 1

    chart_w = W - PAD_L - PAD_R
    chart_h = H - PAD_T - PAD_B
    n = len(valid)

    def sx(i):
        return PAD_L + (i / (n - 1)) * chart_w if n > 1 else PAD_L + chart_w / 2

    def sy(v):
        return PAD_T + (1 - (v - y_min) / y_range) * chart_h

    def polyline(vals, color, width=1.5, dash=''):
        pts = ' '.join(f'{sx(i):.1f},{sy(v):.1f}' for i, (_, tx, tn, tm) in enumerate(valid)
                       if (v := (tx if vals == 'tmax' else tn if vals == 'tmin' else tm)) is not None)
        dash_attr = f' stroke-dasharray="{dash}"' if dash else ''
        return f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="{width}" stroke-linejoin="round" stroke-linecap="round"{dash_attr}/>'

    # Y-axis grid lines + labels
    grid_lines = ''
    y_ticks = 4
    for k in range(y_ticks + 1):
        y_val = y_min + k / y_ticks * y_range
        y_px  = sy(y_val)
        grid_lines += (
            f'<line x1="{PAD_L}" y1="{y_px:.1f}" x2="{W - PAD_R}" y2="{y_px:.1f}" '
            f'stroke="#e8e0d0" stroke-width="1" stroke-dasharray="3 3"/>'
            f'<text x="{PAD_L - 6}" y="{y_px + 4:.1f}" text-anchor="end" '
            f'font-size="10" fill="#6b7280" font-weight="600">{y_val:.0f}</text>'
        )

    # X-axis labels — ALL years, staggered (odd years slightly lower)
    x_labels = ''
    for i, (y, *_) in enumerate(valid):
        y_offset = H - 4 if i % 2 == 0 else H + 11
        x_labels += (
            f'<text x="{sx(i):.1f}" y="{y_offset}" text-anchor="middle" '
            f'font-size="9.5" fill="#6b7280" font-weight="600">{y}</text>'
        )
        # Tick mark
        x_labels += (
            f'<line x1="{sx(i):.1f}" y1="{H - PAD_B + 2}" x2="{sx(i):.1f}" y2="{H - PAD_B + 6}" '
            f'stroke="#d1d5db" stroke-width="1"/>'
        )

    # Dots at data points
    dots = ''
    for series, color in [('tmax', '#ef4444'), ('tmin', '#3b82f6')]:
        for i, (_, tx, tn, tm) in enumerate(valid):
            v = tx if series == 'tmax' else tn
            if v is not None:
                dots += f'<circle cx="{sx(i):.1f}" cy="{sy(v):.1f}" r="3" fill="{color}" stroke="white" stroke-width="1.5"/>'

    svg = (
        f'<svg viewBox="0 0 {W} {H + 14}" width="100%" style="display:block;overflow:visible" '
        f'role="img" aria-label="{title_lbl}">'
        f'{grid_lines}'
        f'{polyline("tmin", "#3b82f6", 2.5)}'
        f'{polyline("tmoy", "#9ca3af", 1.5, "5 3")}'
        f'{polyline("tmax", "#ef4444", 2.5)}'
        f'{dots}'
        f'{x_labels}'
        f'</svg>'
    )

    # Legend — inline styles for reliability
    leg_style = 'display:inline-flex;align-items:center;gap:6px;font-size:11px;color:#718096;white-space:nowrap'
    dash_bg   = 'repeating-linear-gradient(90deg,#a3a3a3 0,#a3a3a3 4px,transparent 4px,transparent 6px)'
    legend = (
        f'<div style="display:flex;gap:14px;flex-wrap:wrap;margin-top:10px">'
        f'<span style="{leg_style}"><span style="display:inline-block;width:18px;height:3px;border-radius:2px;background:#f97316;flex-shrink:0"></span>{tmax_lbl}</span>'
        f'<span style="{leg_style}"><span style="display:inline-block;width:18px;height:3px;border-radius:2px;background:repeating-linear-gradient(90deg,#9ca3af 0,#9ca3af 5px,transparent 5px,transparent 8px);flex-shrink:0"></span>{tmoy_lbl}</span>'
        f'<span style="{leg_style}"><span style="display:inline-block;width:18px;height:3px;border-radius:2px;background:#93c5fd;flex-shrink:0"></span>{tmin_lbl}</span>'
        f'</div>'
    )

    # CMIP6 rate badge — inline styles for reliability
    if cmip6 is not None:
        sign  = '+' if cmip6 >= 0 else ''
        color = '#c2410c' if cmip6 > 0.3 else '#a16207' if cmip6 > 0.15 else '#15803d'
        cmip6_badge = (
            f'<div style="display:flex;align-items:center;gap:12px;background:#faf8f3;'
            f'border:1.5px solid #e8e0d0;border-radius:10px;padding:12px 16px;margin-bottom:10px">'
            f'<span style="font-size:20px;flex-shrink:0">📅</span>'
            f'<div style="display:flex;flex-direction:column;gap:2px">'
            f'<span style="font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.5px;color:#9ca3af">{cmip6_lbl}</span>'
            f'<span style="font-size:20px;font-weight:800;color:{color};line-height:1.1">{sign}{cmip6:.2f}&thinsp;°C</span>'
            f'<span style="font-size:11px;color:#718096">{cmip6_unit}</span>'
            f'</div>'
            f'</div>'
        )
    else:
        cmip6_badge = ''

    return (
        f'<section class="section ct-section">'
        f'<div class="section-label">{sec_lbl}</div>'
        f'<h2 class="section-title">{title_lbl}</h2>'
        f'<div class="ct-chart-wrap">'
        f'{svg}'
        f'{legend}'
        f'</div>'
        f'{cmip6_badge}'
        f'<p class="ct-note">{note_lbl}</p>'
        f'</section>'
    )


# ── Decision card (fusion Décision + Infos pratiques) ─────────────────────────

def decision_card_html(dest, months, mi_best, C, nom,
                       is_mountain=False, is_coastal=False,
                       oui_si='', non_si='', verdict_txt='',
                       is_monthly=False, mi_current=None,
                       best_month_name='', best_month_score=0.0,
                       is_tropical=False) -> str:
    """
    Unified decision + practical info card.
    Works for both annual pages (mi_best = best month index)
    and monthly pages (is_monthly=True, mi_current = current month).
    """
    from scoring import compute_ski_score
    import json as _json

    lang = C.get('lang', 'fr')
    L = C  # C already has all lbl_* keys

    # ── Country info ──
    ci = _load_country_info()
    pays = dest.get('pays', '')
    info = ci.get(pays, {})
    currency     = info.get('currency', '')
    currency_name = info.get('currency_name', '')
    currency_sym  = info.get('currency_symbol', '')
    languages    = info.get('languages', [])
    drive        = info.get('drive', 'right')
    budget_idx   = max(1, min(5, info.get('budget_index', 3)))
    risk_level   = info.get('risk_level', 1)
    iso2         = (dest.get('flag') or '').upper()

    # ── Month to display ──
    mi = mi_current if is_monthly else mi_best
    m  = months[mi]
    score = float(m.get('score', 0))

    # ── Verdict colors (reuse existing dec CSS vars) ──
    classe = m.get('classe', 'mid')
    if classe == 'rec':
        vb_cls = 'v-rec'; txt = '#c8940a'; bg = '#fef9c3'
        verdict_lbl = L.get('lbl_table_legend_ideal', L.get('table_legend_ideal', 'Meilleure période'))
        emoji = '🏆'
    elif classe == 'avoid':
        vb_cls = 'v-avoid'; txt = '#dc2626'; bg = '#fef2f2'
        verdict_lbl = L.get('lbl_table_legend_off', L.get('table_legend_off', 'Conditions marquées'))
        emoji = '⚠️'
    else:
        vb_cls = 'v-mid'; txt = '#ea580c'; bg = '#fff7ed'
        verdict_lbl = L.get('lbl_table_legend_fair', L.get('table_legend_fair', 'Période correcte'))
        emoji = '📅'

    # ── Month name ──
    months_names = C.get('months', ['Jan','Fév','Mar','Avr','Mai','Jun','Jul','Aoû','Sep','Oct','Nov','Déc'])
    month_name = months_names[mi] if mi < len(months_names) else ''

    # ── Ressenti ──
    r_lbl, r_col = ressenti(float(m.get('tmax', 25)), m.get('dew_point'), lang)
    if r_lbl and r_col:
        # Map color to CSS class
        col_map = {'#ef4444':'rb-red','#dc2626':'rb-red','#f97316':'rb-orange',
                   '#22c55e':'rb-green','#0ea5e9':'rb-blue','#7c3aed':'rb-sky'}
        rb_cls = col_map.get(r_col, 'rb-orange')
        ressenti_badge = f'<div class="ressenti-badge rb {rb_cls}">{r_lbl}</div>'
    else:
        ressenti_badge = ''

    # ── Bar widths ──
    sun_h    = float(m.get('sun_h', 0))
    rain_pct  = float(m.get('rain_pct', 0))
    precip_mm = float(m.get('precip_mm', 0) or m.get('precip', 0) or 0)
    tmax      = float(m.get('tmax', 20))
    sun_bar   = round(min(sun_h, 14) / 14 * 100)

    # UV index label
    _uv_val = m.get('uv_index')
    _uv_labels = {
        'fr':    {1:'UV Faible', 2:'UV Modéré', 3:'UV Élevé', 4:'UV Très élevé', 5:'UV Extrême'},
        'en':    {1:'UV Low',    2:'UV Moderate',3:'UV High',  4:'UV Very High',   5:'UV Extreme'},
        'en-us': {1:'UV Low',    2:'UV Moderate',3:'UV High',  4:'UV Very High',   5:'UV Extreme'},
        'es':    {1:'UV Bajo',   2:'UV Moderado',3:'UV Alto',  4:'UV Muy alto',    5:'UV Extremo'},
        'de':    {1:'UV Niedrig',2:'UV Mäßig',   3:'UV Hoch',  4:'UV Sehr hoch',   5:'UV Extrem'},
    }
    _uv_colors = {1:'#22c55e', 2:'#84cc16', 3:'#f59e0b', 4:'#f97316', 5:'#ef4444'}
    def _uv_level(v):
        if v is None or v < 3: return 0
        if v < 6:  return 2  # Modéré
        if v < 8:  return 3  # Élevé
        if v < 11: return 4  # Très élevé
        return 5             # Extrême
    _uv_lvl = _uv_level(_uv_val)
    if _uv_lvl > 0:
        _uv_lbl = _uv_labels.get(lang, _uv_labels['en']).get(_uv_lvl, '')
        _uv_color = _uv_colors.get(_uv_lvl, '#f59e0b')
        _uv_sub = (
            f'<div class="ic-sub" style="font-size:9px;font-weight:700;color:{_uv_color};'
            f'margin-top:2px;text-transform:uppercase;letter-spacing:.3px">{_uv_lbl}</div>'
        )
    else:
        _uv_sub = ''

    # Weather stability label — affiché seulement si variable ou unstable
    _stab = compute_weather_stability(rain_pct, precip_mm, sun_h)
    _stab_labels = {
        'fr':    {'variable': 'Météo variable', 'unstable': 'Météo changeante'},
        'en':    {'variable': 'Variable weather', 'unstable': 'Changeable weather'},
        'en-us': {'variable': 'Variable weather', 'unstable': 'Changeable weather'},
        'es':    {'variable': 'Tiempo variable', 'unstable': 'Tiempo cambiante'},
        'de':    {'variable': 'Wechselhaftes Wetter', 'unstable': 'Unbeständiges Wetter'},
    }
    _stab_colors = {'variable': '#8b5cf6', 'unstable': '#6366f1'}
    if _stab in ('variable', 'unstable'):
        _stab_lbl = _stab_labels.get(lang, _stab_labels['en']).get(_stab, '')
        _stab_color = _stab_colors[_stab]
        _stab_sub = (
            f'<div class="ic-sub" style="font-size:9px;font-weight:700;color:{_stab_color};'
            f'margin-top:2px;text-transform:uppercase;letter-spacing:.3px">{_stab_lbl}</div>'
        )
    else:
        _stab_sub = ''

    # AQI — affiché seulement si > 60
    _aqi_val = m.get('aqi')
    _aqi_sub = ''
    if _aqi_val is not None and _aqi_val > 60:
        _aqi_labels = {
            'fr':    {60: 'Air modéré', 80: 'Pollution élevée', 100: 'Air très pollué'},
            'en':    {60: 'Moderate air', 80: 'High pollution',  100: 'Very poor air'},
            'en-us': {60: 'Moderate air', 80: 'High pollution',  100: 'Very poor air'},
            'es':    {60: 'Aire moderado',80: 'Contaminación',   100: 'Aire muy contaminado'},
            'de':    {60: 'Mäßige Luft',  80: 'Luftverschmutzung', 100: 'Sehr schlechte Luft'},
        }
        _aqi_lvl = 100 if _aqi_val > 100 else (80 if _aqi_val > 80 else 60)
        _aqi_lbl = _aqi_labels.get(lang, _aqi_labels['en']).get(_aqi_lvl, '')
        _aqi_color = '#ef4444' if _aqi_val > 100 else ('#f97316' if _aqi_val > 80 else '#f59e0b')
        _aqi_sub = (
            f'<div class="ic-sub" style="font-size:9px;font-weight:700;color:{_aqi_color};'
            f'margin-top:2px;text-transform:uppercase;letter-spacing:.3px">{_aqi_lbl}</div>'
        )
    rain_bar  = min(int(rain_pct), 100)
    temp_bar  = round(min(tmax, 40) / 40 * 100)

    # Rain type label (burstiness logic)
    _rain_pattern = _classify_rain_pattern(rain_pct, precip_mm, sun_h)
    _rain_type_labels = {
        'fr':    {'tropical_showers': 'Averses courtes', 'blocking': 'Pluie persistante', 'heavy_blocking': 'Pluie bloquante', 'normal': ''},
        'en':    {'tropical_showers': 'Short showers',   'blocking': 'Persistent rain',   'heavy_blocking': 'Heavy rain',      'normal': ''},
        'en-us': {'tropical_showers': 'Short showers',   'blocking': 'Persistent rain',   'heavy_blocking': 'Heavy rain',      'normal': ''},
        'es':    {'tropical_showers': 'Chubascos cortos','blocking': 'Lluvia persistente', 'heavy_blocking': 'Lluvia intensa',  'normal': ''},
        'de':    {'tropical_showers': 'Kurze Schauer',   'blocking': 'Anhaltender Regen', 'heavy_blocking': 'Starkregen',      'normal': ''},
    }
    _rain_type_lbl = _rain_type_labels.get(lang, _rain_type_labels['en']).get(_rain_pattern, '')
    _rain_sub = (
        f'<div class="ic-sub" style="font-size:9px;font-weight:700;color:#0369a1;margin-top:2px;'
        f'text-transform:uppercase;letter-spacing:.3px">{_rain_type_lbl}</div>'
    ) if _rain_type_lbl else ''

    # ── Temp display ──
    tmin_str = fmt_temp(float(m.get('tmin', 15)), C)
    tmax_str = fmt_temp(tmax, C)
    sun_str  = f"{sun_h}{C.get('locale', {}).get('comp', {}).get('sun_per_day_short', 'h/j')}"

    # ── Security ──
    from lib.common import _mae_label
    secu_lbl, secu_cls, secu_icon = _mae_label(risk_level, lang)

    # ── Budget ──
    _budget_labels = {
        'fr':    {1:'Économique', 2:'Abordable', 3:'Modéré',    4:'Coûteux',   5:'Très coûteux'},
        'en':    {1:'Budget-friendly', 2:'Affordable', 3:'Moderate',  4:'Expensive', 5:'Very expensive'},
        'en-us': {1:'Budget-friendly', 2:'Affordable', 3:'Moderate',  4:'Expensive', 5:'Very expensive'},
        'es':    {1:'Económico',  2:'Asequible',  3:'Moderado',  4:'Caro',      5:'Muy caro'},
        'de':    {1:'Günstig',    2:'Erschwinglich',3:'Moderat', 4:'Teuer',     5:'Sehr teuer'},
    }
    _budget_icons = {1:'💚',2:'💚',3:'🟡',4:'🟠',5:'💎'}
    blang = lang if lang in _budget_labels else 'en'
    budget_lbl_text = _budget_labels[blang][budget_idx]
    budget_icon = _budget_icons[budget_idx]

    # ── Drive ──
    drive_lbl = L.get('lbl_dec_lbl_drive_left') if drive == 'left' else L.get('lbl_dec_lbl_drive_right')
    drive_icon = '🚗↩️' if drive == 'left' else '🚗'

    # ── Languages (max 2 + overflow) ──
    lang_str = ', '.join(_translate_lang(l, lang) for l in languages[:2])
    if len(languages) > 2:
        more = L.get('lbl_more', '+{n}').format(n=len(languages)-2) if '{n}' in L.get('lbl_more','') else f'+{len(languages)-2}'
        lang_str += f' {more}'

    # ── Wettest month ──
    wettest_mi  = max(range(12), key=lambda i: float(months[i].get('rain_pct', 0)))
    wettest_name = months_names[wettest_mi] if wettest_mi < len(months_names) else ''
    wettest_pct  = int(float(months[wettest_mi].get('rain_pct', 0)))
    is_mtn_dest  = dest.get('mountain','') in ('True','true','1')
    jours_lbl = L.get('lbl_dec_jours_prec') if is_mtn_dest else L.get('lbl_dec_jours_pluie')

    # ── Labels ──
    def lbl(key):
        return L.get(f'lbl_dec_lbl_{key}', key)

    row_meteo   = L.get('lbl_dec_row_meteo', '☀️ Météo')
    row_prat    = L.get('lbl_dec_row_pratique', '🧳 Pratique')
    row_mer     = L.get('lbl_dec_row_mer', '🌊 Mer')
    row_ski     = L.get('lbl_dec_row_ski', '⛷️ Ski')
    best_lbl    = L.get('lbl_dec_score_lbl', L.get('lbl_m_score_label', 'Score météo')) if is_monthly else L.get('lbl_dec_best_score_lbl', 'Meilleur score')
    ideal_lbl   = L.get('lbl_dec_ideal_lbl', 'Idéal')
    eviter_lbl  = L.get('lbl_dec_eviter_lbl', 'À éviter')

    # ── Source strip ──
    secu_source = info.get('risk_source', 'Auswärtiges Amt (DE)')
    secu_date   = info.get('risk_updated', '')[:10] if info.get('risk_updated','') else ''
    verify_lbl  = {'fr':'à vérifier avant de voyager','en':'verify before travel',
                   'en-us':'verify before travel','es':'verificar antes de viajar',
                   'de':'vor der Reise prüfen'}.get(lang, 'verify before travel')

    # ══════════════════════════════════════════
    # ANNUAL ONLY: season band + best/worst pills
    # ══════════════════════════════════════════
    season_band = ''
    best_avoid_strip = ''

    if not is_monthly:
        # 12-month color band
        cls_map = {'rec':'ss-rec','mid':'ss-mid','avoid':'ss-avoid'}
        band_cells = ''.join(
            f'<div class="{cls_map.get(months[i].get("classe","mid"),"ss-mid")}"></div>'
            for i in range(12)
        )
        short_months = [mn[:3] for mn in months_names[:12]]
        month_cells = ''.join(
            '<div class="ms-cell ' + months[i].get('classe','mid') + '">' + short_months[i] + '</div>'
            for i in range(12)
        )
        season_band = (
            f'<div class="season-strip">{band_cells}</div>'
            f'<div class="month-strip">{month_cells}</div>'
        )

        # Best months (rec class, sorted by score desc, top 4)
        rec_months = sorted(
            [(i, float(months[i].get('score',0))) for i in range(12) if months[i].get('classe')=='rec'],
            key=lambda x: -x[1]
        )[:4]
        avoid_months = sorted(
            [(i, float(months[i].get('score',0))) for i in range(12) if months[i].get('classe')=='avoid'],
            key=lambda x: x[1]
        )[:3]

        best_pills = ''.join(f'<span class="bm-pill">{short_months[i]}</span>' for i,_ in rec_months)
        avoid_pills = ''.join(f'<span class="bm-pill bm-avoid">{short_months[i]}</span>' for i,_ in avoid_months) or '<span class="bm-pill bm-avoid">—</span>'

        best_avoid_strip = (
            f'<div class="best-months">'
            f'<span class="bm-lbl">{ideal_lbl}</span>{best_pills}'
            f'<span class="bm-lbl" style="margin-left:8px">{eviter_lbl}</span>{avoid_pills}'
            f'</div>'
        )

    # ══════════════════════════════════════════
    # ROW 1 : Météo
    # ══════════════════════════════════════════
    row1 = (
        f'<div class="info-row cols-5">'
        f'<div class="info-cell">'
        f'<div class="ic-ico">☀️</div>'
        f'<div class="ic-val">{sun_str}</div>'
        f'<div class="mb"><div class="mf bs" style="width:{sun_bar}%"></div></div>'
        f'{_uv_sub}'
        f'{_stab_sub}'
        f'<div class="ic-lbl">{lbl("soleil")}</div>'
        f'</div>'
        f'<div class="info-cell">'
        f'<div class="ic-ico">🌡️</div>'
        f'<div class="ic-val">{tmin_str}–{tmax_str}</div>'
        f'<div class="mb"><div class="mf br" style="width:{temp_bar}%"></div></div>'
        f'{ressenti_badge}'
        f'<div class="ic-lbl">{lbl("temp")}</div>'
        f'</div>'
        f'<div class="info-cell">'
        f'<div class="ic-ico">🌂</div>'
        f'<div class="ic-val">{int(rain_pct)}%</div>'
        f'<div class="mb"><div class="mf bb" style="width:{rain_bar}%"></div></div>'
        f'{_rain_sub}'
        f'<div class="ic-lbl">{lbl("pluie")}</div>'
        f'</div>'
        f'<div class="info-cell" data-advisory-cc="{iso2}">'
        f'<div class="ic-ico">{secu_icon}</div>'
        f'<div class="ic-val dec-secu-{secu_cls}" style="font-size:11px">{secu_lbl}</div>'
        f'{_aqi_sub}'
        f'<div class="ic-lbl">{lbl("secu")}</div>'
        f'</div>'
        f'<div class="info-cell">'
        f'<div class="ic-ico">{budget_icon}</div>'
        f'<div class="ic-val dec-budget-{budget_idx}">{budget_lbl_text}</div>'
        f'<div class="ic-sub">{L.get("lbl_dec_budget_sublabel", L.get("lbl_budget_sublabel", ""))}' + '</div>'
        f'<div class="ic-lbl">{lbl("budget")}</div>'
        f'</div>'
        f'</div>'
    )

    # ══════════════════════════════════════════
    # ROW 2 : Pratique
    # ══════════════════════════════════════════
    row2 = (
        f'<div class="info-row cols-4">'
        f'<div class="info-cell">'
        f'<div class="ic-ico">💰</div>'
        f'<div class="ic-val ic-mono">{currency}</div>'
        f'<div class="ic-sub">{currency_sym} · {currency_name}</div>'
        f'<div class="ic-lbl">{lbl("monnaie")}</div>'
        f'</div>'
        f'<div class="info-cell">'
        f'<div class="ic-ico">🗣️</div>'
        f'<div class="ic-val">{lang_str}</div>'
        f'<div class="ic-lbl">{lbl("langue")}</div>'
        f'</div>'
        f'<div class="info-cell">'
        f'<div class="ic-ico">{drive_icon}</div>'
        f'<div class="ic-val" style="font-size:11px">{drive_lbl}</div>'
        f'<div class="ic-lbl">{lbl("conduite")}</div>'
        f'</div>'
        f'<div class="info-cell">'
        f'<div class="ic-ico">🌧️</div>'
        f'<div class="ic-val">{wettest_name}</div>'
        f'<div class="ic-sub">{wettest_pct}% {jours_lbl}</div>'
        f'<div class="ic-lbl">{lbl("wettest")}</div>'
        f'</div>'
        f'</div>'
    )

    # ══════════════════════════════════════════
    # ROW 3 (conditional) : Mer ou Ski
    # ══════════════════════════════════════════
    row3 = ''
    if is_coastal:
        # Sea temp: group by season — tropical = 2 groups, temperate = 4
        _trop_sea = is_tropical and C.get('locale', {}).get('tropical_seasons')
        if _trop_sea:
            _dry_m  = [i for i in range(12) if float(months[i].get('rain_pct', 0)) < 60]
            _wet_m  = [i for i in range(12) if float(months[i].get('rain_pct', 0)) >= 60]
            _ts = C['locale']['tropical_seasons']['names']
            season_groups = [
                (None, None, 'seche',  _dry_m),
                (None, None, 'humide', _wet_m),
            ]
        else:
            season_groups = [(0,2,'hiver'),(3,5,'print'),(6,8,'ete'),(9,11,'auto')]
        sea_cells = ''
        for entry in season_groups:
            if _trop_sea:
                _, _, key, idxs = entry
                temps = [float(months[i].get('sea_temp',0)) for i in idxs if months[i].get('sea_temp','').strip()]
            else:
                start, end, key = entry
                idxs = list(range(start, end+1))
                temps = [float(months[i].get('sea_temp',0)) for i in idxs if months[i].get('sea_temp','').strip()]
            if not temps:
                continue
            avg = round(sum(temps)/len(temps), 1)
            # Color class
            if avg < 16: sc = 'sea-cold'; ico = '🥶'
            elif avg < 21: sc = 'sea-ok'; ico = '🌊'
            elif avg < 26: sc = 'sea-warm'; ico = '🏖️'
            else: sc = 'sea-hot'; ico = '☀️'
            bar_w = round((avg - 10) / 20 * 100)
            sea_cells += (
                f'<div class="info-cell">'
                f'<div class="ic-ico">{ico}</div>'
                f'<div class="ic-val {sc}">{fmt_temp(avg, C)}</div>'
                f'<div class="mb"><div class="mf bc" style="width:{bar_w}%"></div></div>'
                f'<div class="ic-lbl">{L.get(f"lbl_dec_lbl_mer_{key}", key)}</div>'
                f'</div>'
            )
        # Wave chip pour page mensuelle
        wave_cell = ''
        if is_monthly and mi_current is not None:
            _wh = m.get('wave_h')
            _sp = m.get('swell_p')
            _wave_cls = classify_waves(_wh, _sp)
            _wave_labels = {
                'fr':    {'calm': 'Mer calme', 'light': 'Mer douce', 'surf': 'Conditions surf', 'rough': 'Mer agitée'},
                'en':    {'calm': 'Calm sea',  'light': 'Gentle sea','surf': 'Surf conditions','rough': 'Rough sea'},
                'en-us': {'calm': 'Calm sea',  'light': 'Gentle sea','surf': 'Surf conditions','rough': 'Rough sea'},
                'es':    {'calm': 'Mar calmo', 'light': 'Mar suave', 'surf': 'Condiciones surf','rough': 'Mar agitado'},
                'de':    {'calm': 'Ruhige See','light': 'Leichte See','surf': 'Surfbedingungen','rough': 'Rauhe See'},
            }
            _wave_colors = {'calm': '#22c55e', 'light': '#0ea5e9', 'surf': '#f59e0b', 'rough': '#f97316'}
            _wave_icons  = {'calm': '🟢', 'light': '🔵', 'surf': '🏄', 'rough': '🟠'}
            if _wave_cls and _wh is not None:
                _wlbl = _wave_labels.get(lang, _wave_labels['en']).get(_wave_cls, '')
                _wcol = _wave_colors.get(_wave_cls, '#64748b')
                _wico = _wave_icons.get(_wave_cls, '🌊')
                _wh_str = f'{_wh:.1f}m'
                _sp_str = f' · {_sp:.0f}s' if _sp else ''
                wave_cell = (
                    f'<div class="info-cell">'
                    f'<div class="ic-ico">{_wico}</div>'
                    f'<div class="ic-val" style="color:{_wcol};font-weight:700">{_wh_str}{_sp_str}</div>'
                    f'<div class="mb"><div class="mf" style="width:{min(100,int(_wh/3*100))}%;background:{_wcol}"></div></div>'
                    f'<div class="ic-lbl">{_wlbl}</div>'
                    f'</div>'
                )

        if sea_cells or wave_cell:
            _sea_cols = 'cols-2' if _trop_sea else ('cols-4' if not wave_cell else 'cols-5')
            row3 = (
                f'<div class="rd"><div class="rdl"></div>'
                f'<div class="rdt">{row_mer}</div>'
                f'<div class="rdl"></div></div>'
                f'<div class="info-row {_sea_cols}">{sea_cells}{wave_cell}</div>'
            )

    elif is_mountain:
        # Ski scores: find best ski month + rando month + season
        ski_scores = [(i, compute_ski_score(float(months[i].get('tmax',0)), float(months[i].get('rain_pct',0)), float(months[i].get('sun_h',0)))) for i in range(12)]
        best_ski = max(ski_scores, key=lambda x: x[1])
        # Rando = warmest month with score > 5
        rando_months = [(i,s) for i,s in ski_scores if float(months[i].get('tmax',0)) > 8 and s < 5.5]
        best_rando = max(rando_months, key=lambda x: float(months[x[0]].get('score',0))) if rando_months else None
        # Ski season = consecutive months with ski > 5.5
        ski_season = [months_names[i][:3] for i,s in ski_scores if s >= 5.5]
        ski_season_str = f"{ski_season[0]}–{ski_season[-1]}" if len(ski_season) >= 2 else (ski_season[0] if ski_season else '—')

        best_ski_name = months_names[best_ski[0]][:3]
        ski_bar = round(best_ski[1] / 10 * 100)

        rando_cell = ''
        if best_rando:
            ri, rs = best_rando
            rando_name = months_names[ri][:3]
            rando_climate_score = float(months[ri].get('score', 0))
            rando_bar = round(rando_climate_score / 10 * 100)
            rando_cell = (
                f'<div class="info-cell">'
                f'<div class="ic-ico">🏔️</div>'
                f'<div class="ic-val" style="color:#16a34a;font-size:15px;font-weight:900">'
                f'{rando_climate_score:.1f}<span style="font-size:10px;opacity:.5">/10</span></div>'
                f'<div class="mb"><div class="mf bs" style="width:{rando_bar}%"></div></div>'
                f'<div class="ic-lbl">{rando_name} · {L.get("lbl_dec_lbl_randonnee","Rando")}</div>'
                f'</div>'
            )

        row3 = (
            f'<div class="rd"><div class="rdl"></div>'
            f'<div class="rdt">{row_ski}</div>'
            f'<div class="rdl"></div></div>'
            f'<div class="info-row cols-4">'
            f'<div class="info-cell">'
            f'<div class="ic-ico">⛷️</div>'
            f'<div class="ic-val" style="color:#0369a1;font-size:15px;font-weight:900">'
            f'{best_ski[1]:.1f}<span style="font-size:10px;opacity:.5">/10</span></div>'
            f'<div class="mb"><div class="mf bsk" style="width:{ski_bar}%"></div></div>'
            f'<div class="ic-lbl">{best_ski_name} · {L.get("lbl_dec_lbl_ski_best","Best")}</div>'
            f'</div>'
            f'{rando_cell}'
            f'<div class="info-cell">'
            f'<div class="ic-ico">📅</div>'
            f'<div class="ic-val" style="font-size:11px">{ski_season_str}</div>'
            f'<div class="ic-sub">{L.get("lbl_dec_lbl_ski_saison","Saison")} ski</div>'
            f'<div class="ic-lbl">{L.get("lbl_dec_lbl_ski_saison","Saison")}</div>'
            f'</div>'
            f'</div>'
        )

    # ══════════════════════════════════════════
    # Oui si / Non si + verdict text (monthly only)
    # ══════════════════════════════════════════
    reasons = ''
    verdict_para = ''
    if is_monthly and (oui_si or non_si):
        yes_lbl = C.get('yes_lbl', '✅ Oui si')
        no_lbl  = C.get('no_lbl',  '⚠️ Attention si')
        reasons = (
            f'<div class="reasons-row">'
            f'<div class="reason-cell yes"><strong>{yes_lbl}</strong> {oui_si}</div>'
            f'<div class="reason-cell no"><strong>{no_lbl}</strong> {non_si}</div>'
            f'</div>'
        )
    if is_monthly and verdict_txt:
        intro = C.get('verdict_intro', 'En résumé :')
        verdict_para = (
            f'<div class="verdict-editorial">'
            f'<strong>{intro}</strong> {verdict_txt}'
            f'</div>'
        )

    # ══════════════════════════════════════════
    # SOURCE FOOTER
    # ══════════════════════════════════════════
    source = (
        f'<div class="source-footer">'
        f'<div class="source-tag">🛡️ {secu_source}'
        f'<span class="source-dot"></span>{verify_lbl}'
        f'{f"<span class=\"source-dot\"></span>{secu_date}" if secu_date else ""}'
        f'</div>'
        f'<div class="source-tag">ERA5 · Open-Meteo · 10 ans<span class="source-dot"></span>Numbeo 2026</div>'
        f'</div>'
    )

    # ══════════════════════════════════════════
    # VERDICT BANNER
    # ══════════════════════════════════════════
    banner = (
        f'<div class="verdict-banner {vb_cls}">'
        f'<div class="verdict-left">'
        f'<div class="verdict-emoji">{emoji}</div>'
        f'<div class="verdict-text-wrap">'
        f'<div class="verdict-month">{month_name}</div>'
        f'<div class="verdict-pill">✦ {verdict_lbl}</div>'
        + (f'<div class="verdict-best-ref" style="font-size:10px;color:rgba(0,0,0,.45);margin-top:4px">'
           f'{L.get("lbl_m_qf_best_month","Meilleur mois")} : <strong>{best_month_name}</strong> ({best_month_score:.1f}/10)</div>'
           if is_monthly and best_month_name else '')
        + f'</div></div>'
        f'<div class="verdict-score-wrap">'
        f'<div class="verdict-score">{score:.1f}<span class="verdict-score-denom">/10</span></div>'
        f'<div class="verdict-score-lbl">{best_lbl}</div>'
        f'</div></div>'
    )

    # ══════════════════════════════════════════
    # ASSEMBLE
    # ══════════════════════════════════════════
    def divider(label):
        return (f'<div class="row-divider"><div class="row-divider-line"></div>'
                f'<div class="row-divider-label">{label}</div>'
                f'<div class="row-divider-line"></div></div>')

    return (
        f'<div class="decision-card">'
        f'{banner}'
        f'{season_band}'
        f'{best_avoid_strip}'
        f'{divider(row_meteo)}'
        f'{row1}'
        f'{divider(row_prat)}'
        f'{row2}'
        f'{row3}'
        f'{reasons}'
        f'{verdict_para}'
        f'{source}'
        f'</div>'
    )
