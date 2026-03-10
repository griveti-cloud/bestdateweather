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

def weather_emoji(tmax, rain_pct, sun_h=None, precip_mm=None, score=None):
    """Return a weather emoji based on temperature, rain, sunshine, intensity and score.
    
    In tropical climates (tmax >= 25), high rain_pct (frequency of rainy days) does NOT
    mean all-day rain. Brief afternoon showers are normal. We use precip_mm (daily intensity)
    and sun_h to distinguish tropical showers from actual bad weather.
    """
    # ── Extreme cold ──
    if tmax < 0:
        return '❄️'
    if tmax <= 4:
        return '🌨️'
    # ── Extreme heat ──
    if tmax >= 36:
        return '🥵'
    
    # ── Tropical / warm climates (tmax >= 25) — softer rain thresholds ──
    if tmax >= 25:
        # Sun hours take priority: 10h+ sun = significant clear skies regardless of rain frequency
        if sun_h is not None and sun_h >= 10:
            if rain_pct < 25:
                return '☀️'
            if rain_pct < 60:
                return '🌤️'
            if rain_pct < 85:
                return '⛅'  # lots of sun + frequent brief showers
            return '🌦️'  # extreme rain frequency but still sunny
        if sun_h is not None and sun_h >= 8:
            if rain_pct < 30:
                return '☀️'
            if rain_pct < 55:
                return '🌤️'
            if rain_pct < 80:
                return '⛅'
            # 8h+ sun but 80%+ rain → heavy tropical rain season
            if precip_mm is not None and precip_mm >= 12:
                return '🌧️'
            return '🌦️'
        # Less than 8h sun — genuinely overcast/rainy
        if rain_pct >= 75 and precip_mm is not None and precip_mm >= 8:
            return '🌧️'
        # Warm but less sun
        if rain_pct < 25:
            return '☀️'
        if rain_pct < 45:
            return '🌤️'
        if rain_pct < 65:
            return '🌦️'
        return '🌧️'
    
    # ── Mild / temperate climates (tmax 5-24) ──
    if rain_pct >= 65:
        return '🌧️'
    if rain_pct >= 50:
        return '🌦️'
    if tmax >= 22 and rain_pct < 50 and sun_h is not None and sun_h >= 10:
        return '🌤️'
    if tmax >= 18 and rain_pct < 35:
        return '🌤️'
    if tmax >= 18 and rain_pct < 45 and sun_h is not None and sun_h >= 9:
        return '🌤️'
    if rain_pct >= 40 and tmax >= 12:
        return '🌦️'
    if tmax >= 15 and rain_pct < 40:
        return '⛅'
    if tmax >= 12 and rain_pct < 40:
        return '⛅'
    if rain_pct >= 35 and tmax >= 5:
        return '🌦️'
    return '🌫️'


# ── Shared functions ──────────────────────────────────────────────────────────

def score_badge(score, classe=None, L=None):
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
    Numeric values must already be converted before calling (use c_to_f/mm_to_in).
    """
    if cfg.get('imperial'):
        template = template.replace('°C', '°F').replace('mm', 'in')
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
        rows += (f'<tr class="{cls}" data-tmax="{m["tmax"]}" '
                 f'data-rain="{m["rain_pct"]}" data-sun="{m["sun_h"]}">'
                 f'<td>{weather_emoji(m["tmax"], m["rain_pct"], m["sun_h"], m.get("precip"))} {L["months"][i]}</td>'
                 f'<td data-label="{L["th_tmin"]}">{fmt_temp(m["tmin"], L)}</td>'
                 f'<td data-label="{L["th_tmax"]}">{fmt_temp(m["tmax"], L)}</td>'
                 f'<td data-label="{L["th_rain"]}">{m["rain_pct"]}%</td>'
                 f'<td data-label="{L["th_precip"]}">{fmt_precip(m["precip"], L)}</td>'
                 f'<td data-label="{L["th_sun"]}">{m["sun_h"]}h</td>'
                 f'<td data-label="{L["th_score"]}">{m["score"]:.1f}/10</td>{ski_col}</tr>\n')
    ski_header = L['table_ski_header'] if is_mountain else ''
    wrap_class = 'climate-table-wrap mountain' if is_mountain else 'climate-table-wrap'
    return f'''<div class="{wrap_class}">
 <table class="climate-table climate-table--horizontal" aria-label="{L['table_aria'].format(nom=nom)}">
 <thead><tr>{L['table_headers']}{ski_header}</tr></thead>
 <tbody>{rows}</tbody>
 </table>
</div>
<div class="table-legend">
 <span><span class="legend-dot legend-rec"></span>{L['legend_ideal']}</span>
 <span><span class="legend-dot legend-mid"></span>{L['legend_fair']}</span>
 <span><span class="legend-dot legend-avoid"></span>{L['legend_off']}</span>
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
        f'<img src="{a["flag"]}" width="20" height="15" alt="" '
        f'style="vertical-align:middle;border-radius:2px"> {a["label"]}</a>'
        for a in alt_links
    )
    alt_sep = ' · '.join(
        f'<a href="{a["url"]}" style="color:rgba(255,255,255,.7)">'
        f'<img src="{a["flag"]}" width="20" height="15" alt="" '
        f'style="vertical-align:middle;border-radius:2px"> {a["label"]}</a>'
        for a in alt_links
    )

    return f"""<footer>
<p style="color:rgba(255,255,255,.7);font-size:13px;font-weight:700;margin-bottom:8px">bestdateweather.com</p>
<p><a href="https://open-meteo.com/" rel="noopener" style="color:rgba(255,255,255,.7)">{fc['data_by']}</a> · {fc['sources']}</p>
<p style="margin-top:8px"><a href="{fc['methodology_url']}" style="color:rgba(255,255,255,.7)">{fc['methodology_label']}</a> · <a href="{fc['app_url']}" style="color:rgba(255,255,255,.7)">{fc['app_label']}</a></p>
<p style="margin-top:4px;white-space:nowrap;overflow-x:auto">{alt_sep}</p>
<p style="margin-top:8px;font-size:11px;opacity:.6"><a href="{fc['legal_url']}" style="color:rgba(255,255,255,.7)">{fc['legal_label']}</a></p>
</footer>"""
