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
    }


# Backward-compatible exports
LANG_FR = build_lang('fr')
LANG_EN = build_lang('en')


# ── Weather emoji ─────────────────────────────────────────────────────────────

def _classify_rain_pattern(rain_pct, precip_mm, sun_h):
    """
    Distingue pluie bloquante vs averses tropicales courtes.

    burstiness = intensité journalière / fréquence → élevé = pluies concentrées/courtes
    Contexte : en climat convectif tropical, il peut pleuvoir 90% des jours
    mais seulement 1-2h en fin d'après-midi → journée exploitable.

    Returns: 'blocking' | 'tropical_showers' | 'heavy_blocking' | 'normal'
    """
    if rain_pct is None or rain_pct == 0:
        return 'normal'
    rain_freq = rain_pct / 100.0
    burstiness = (precip_mm or 0) / max(rain_freq, 0.05)

    # Pluie vraiment bloquante : peu de soleil OU pluie chronique sans intensité
    is_blocking = (
        rain_pct >= 70 and (
            (sun_h is not None and sun_h <= 7.5) or
            (precip_mm is not None and precip_mm >= 10 and burstiness < 12)
        )
    )
    # Très bloquant : pic de saison des pluies (mai Guyane = 99% + 21mm + 8h)
    is_heavy_blocking = (
        rain_pct >= 90 and
        precip_mm is not None and precip_mm >= 15 and
        sun_h is not None and sun_h < 9
    )
    # Bloquant intermédiaire : très fréquent + intense même avec soleil correct
    is_blocking_intense = (
        rain_pct >= 90 and
        precip_mm is not None and precip_mm >= 14
    )
    # Averses tropicales courtes : fréquent + intense + encore du soleil
    is_tropical_showers = (
        rain_pct >= 60 and
        precip_mm is not None and precip_mm >= 6 and
        sun_h is not None and sun_h >= 9.5 and
        burstiness >= 10
    )

    if is_heavy_blocking:
        return 'heavy_blocking'
    if is_blocking_intense:
        return 'heavy_blocking'
    if is_blocking:
        return 'blocking'
    if is_tropical_showers:
        return 'tropical_showers'
    return 'normal'


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
        avg_r  = round(sum(m['rain_pct'] for m in ms) / len(ms))
        avg_s  = round(sum(m['sun_h'] for m in ms) / len(ms), 1)
        avg_sc = round(sum(m['score'] for m in ms) / len(ms), 1)
        if avg_sc >= 8.5:  verdict = L['verdict_excellent']
        elif avg_sc >= 7.0: verdict = L['verdict_good']
        elif avg_sc >= 5.5: verdict = L['verdict_fair']
        else:               verdict = L['verdict_poor']
        result[name] = {'tmax': avg_t, 'rain_pct': avg_r, 'sun_h': avg_s,
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


def climate_table_html(months, nom, is_mountain=False, L=None):
    """Generate climate table HTML."""
    if L is None:
        L = LANG_FR
    rows = ''
    for i, m in enumerate(months):
        cls = m['classe']
        ski_col = ''
        if is_mountain:
            from scoring import compute_ski_score, best_class
            ski = compute_ski_score(m['tmax'], m['rain_pct'], m['sun_h'])
            cls = best_class(m['classe'], ski)
            ski_col = f'<td>{ski:.1f}/10</td>'
        # Indicateur chaleur dans la colonne tmax
        tmax_val = m['tmax']
        if tmax_val >= 38:
            heat_icon = ' <span title="Chaleur très intense" style="color:#f59e0b;font-size:.85em">🌡️</span>'
        elif tmax_val >= 35:
            heat_icon = ' <span title="Chaleur élevée" style="color:#f59e0b;font-size:.85em">🥵</span>'
        elif tmax_val >= 33:
            heat_icon = ' <span title="Chaleur notable" style="color:#f59e0b;font-size:.85em">☀️</span>'
        else:
            heat_icon = ''
        rows += (f'<tr class="{cls}" data-tmax="{m["tmax"]}" '
                 f'data-rain="{m["rain_pct"]}" data-sun="{m["sun_h"]}">'
                 f'<td>{weather_emoji(m["tmax"], m["rain_pct"], m["sun_h"], m.get("precip"))} {L["months"][i]}</td>'
                 f'<td data-label="{L["th_tmin"]}">{fmt_temp(m["tmin"], L)}</td>'
                 f'<td data-label="{L["th_tmax"]}">{fmt_temp(m["tmax"], L)}{heat_icon}</td>'
                 f'<td data-label="{L["th_rain"]}">{m["rain_pct"]}%</td>'
                 f'<td data-label="{L["th_precip"]}">{fmt_precip(m["precip"], L)}</td>'
                 f'<td data-label="{L["th_sun"]}">{m["sun_h"]}h</td>'
                 f'<td data-label="{L["th_score"]}">{m["score"]:.1f}/10</td>{ski_col}</tr>\n')
    ski_header = L['table_ski_header'] if is_mountain else ''
    wrap_class = 'climate-table-wrap mountain' if is_mountain else 'climate-table-wrap'
    legend_ideal_label = L.get('legend_ideal_mtn', L['legend_ideal']) if is_mountain else L['legend_ideal']
    legend_off_label   = L.get('legend_off_mtn',   L['legend_off'])   if is_mountain else L['legend_off']
    return f'''<div class="{wrap_class}">
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
            1: ('Vigilance normale',              'mae-1', '🟢'),
            2: ('Vigilance renforcée',            'mae-2', '🟡'),
            3: ('Déconseillé sauf impératif',     'mae-3', '🟠'),
            4: ('Formellement déconseillé',        'mae-4', '🔴'),
        },
        'en': {
            1: ('Normal vigilance',               'mae-1', '🟢'),
            2: ('Increased vigilance',            'mae-2', '🟡'),
            3: ('Avoid if possible',              'mae-3', '🟠'),
            4: ('Do not travel',                  'mae-4', '🔴'),
        },
        'es': {
            1: ('Vigilancia normal',              'mae-1', '🟢'),
            2: ('Vigilancia reforzada',           'mae-2', '🟡'),
            3: ('Desaconsejado salvo imperativo', 'mae-3', '🟠'),
            4: ('Formalmente desaconsejado',      'mae-4', '🔴'),
        },
        'de': {
            1: ('Normale Wachsamkeit',            'mae-1', '🟢'),
            2: ('Erhöhte Wachsamkeit',            'mae-2', '🟡'),
            3: ('Nur bei zwingendem Grund',       'mae-3', '🟠'),
            4: ('Dringend abgeraten',             'mae-4', '🔴'),
        },
    }
    lang_key = 'fr' if lang == 'fr' else ('es' if lang == 'es' else ('de' if lang == 'de' else 'en'))
    lvl = max(1, min(4, risk_level))
    return data[lang_key][lvl]


def travel_info_widget(pays: str, nom: str, lang: str = 'fr', L: dict = None) -> str:
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
            'budget_labels': ['Budget', 'Abordable', 'Intermédiaire', 'Haut de gamme', 'Premium'],
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
            'budget_labels': ['Budget', 'Affordable', 'Mid-range', 'Upscale', 'Premium'],
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
        'budget_labels': ['Budget', 'Affordable', 'Mid-range', 'Upscale', 'Premium'],
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
    main_lang = langs[0] if langs else '–'
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
        f'<div class="ti-chip ti-chip--{mae_cls}">'
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
        'fr': 'Conseils aux voyageurs — Ministère des Affaires Étrangères',
        'en': 'Travel advisories — French Ministry of Foreign Affairs',
        'en-us': 'Travel advisories — French Ministry of Foreign Affairs',
        'es': 'Consejos al viajero — Ministerio francés de Asuntos Exteriores',
        'de': 'Reisehinweise — Französisches Außenministerium',
    }
    safety_detail = (
        f'<div class="ti-safety-detail">'
        f'<span class="ti-safety-note">{mae_source_lbl.get(lang, mae_source_lbl["en"])}</span>'
        f'<span class="ti-safety-source">{lbl["gpi_note"]} ({gpi_year})</span>'
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
    W, H = 560, 180
    PAD_L, PAD_R, PAD_T, PAD_B = 36, 12, 16, 32

    all_vals = [v for row in [tmax, tmin, tmoy] for v in row if v is not None]
    y_min = min(all_vals) - 1
    y_max = max(all_vals) + 1
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

    # Y-axis grid lines
    grid_lines = ''
    y_ticks = 4
    for k in range(y_ticks + 1):
        y_val = y_min + k / y_ticks * y_range
        y_px  = sy(y_val)
        grid_lines += (
            f'<line x1="{PAD_L}" y1="{y_px:.1f}" x2="{W - PAD_R}" y2="{y_px:.1f}" '
            f'stroke="#e8e0d0" stroke-width="1"/>'
            f'<text x="{PAD_L - 4}" y="{y_px + 4:.1f}" text-anchor="end" '
            f'font-size="9" fill="#9ca3af">{y_val:.0f}</text>'
        )

    # X-axis labels (every 2 years)
    x_labels = ''
    for i, (y, *_) in enumerate(valid):
        if i % 2 == 0:
            x_labels += (
                f'<text x="{sx(i):.1f}" y="{H - 4}" text-anchor="middle" '
                f'font-size="9" fill="#9ca3af">{y}</text>'
            )

    svg = (
        f'<svg viewBox="0 0 {W} {H}" width="100%" style="display:block;overflow:visible" '
        f'role="img" aria-label="{title_lbl}">'
        f'{grid_lines}'
        f'{polyline("tmin", "#93c5fd", 1.5)}'
        f'{polyline("tmoy", "#a3a3a3", 1.2, "4 2")}'
        f'{polyline("tmax", "#f97316", 2)}'
        f'{x_labels}'
        f'</svg>'
    )

    # Legend — inline styles for reliability
    leg_style = 'display:inline-flex;align-items:center;gap:6px;font-size:11px;color:#718096;white-space:nowrap'
    dash_bg   = 'repeating-linear-gradient(90deg,#a3a3a3 0,#a3a3a3 4px,transparent 4px,transparent 6px)'
    legend = (
        f'<div style="display:flex;gap:14px;flex-wrap:wrap;margin-top:10px">'
        f'<span style="{leg_style}"><span style="display:inline-block;width:18px;height:3px;border-radius:2px;background:#f97316;flex-shrink:0"></span>{tmax_lbl}</span>'
        f'<span style="{leg_style}"><span style="display:inline-block;width:18px;height:3px;border-radius:2px;background:{dash_bg};flex-shrink:0"></span>{tmoy_lbl}</span>'
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
