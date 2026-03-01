"""
BestDateWeather — Shared generation utilities
==============================================
Common functions used by both generate_all.py (FR) and generate_all_en.py (EN).
Each function takes a `L` (lang config dict) parameter for language-specific strings.

Usage:
    from lib.common import score_badge, best_months, budget_tier, ...
"""


# ── Weather emoji ─────────────────────────────────────────────────────────────

def weather_emoji(tmax, rain_pct, sun_h=None):
    """Return a weather emoji based on temperature, rain probability and sunshine.
    Rain dominates above 50%. Temperature rules below 5°C.
    Sunshine upgrades the emoji when conditions are borderline."""
    if rain_pct >= 65:
        return '⛈️'     # Monsoon / very heavy rain
    if rain_pct >= 50:
        return '🌧️'     # Rainy
    if tmax < 0:
        return '❄️'      # Freezing
    if tmax <= 4:
        return '🌨️'     # Cold / snow likely
    if tmax >= 36:
        return '🥵'     # Extreme heat
    if tmax >= 25 and rain_pct < 25:
        return '☀️'      # Sunny & warm
    # Sunshine upgrade: warm + good sunshine despite moderate rain
    if tmax >= 22 and rain_pct < 50 and sun_h is not None and sun_h >= 10:
        return '🌤️'     # Fair (summer storms, but mostly sunny days)
    if tmax >= 25 and rain_pct < 45 and sun_h is not None and sun_h >= 8:
        return '🌤️'     # Fair (warm + decent sun)
    if tmax >= 18 and rain_pct < 35:
        return '🌤️'     # Fair weather
    if tmax >= 18 and rain_pct < 45 and sun_h is not None and sun_h >= 9:
        return '🌤️'     # Fair (enough sun to compensate moderate rain)
    if rain_pct >= 40 and tmax >= 12:
        return '🌦️'     # Mixed / showery
    if tmax >= 15 and rain_pct < 40:
        return '⛅'     # Variable / mild-warm
    if tmax >= 12 and rain_pct < 40:
        return '⛅'     # Variable / mild
    if rain_pct >= 35 and tmax >= 5:
        return '🌦️'     # Mixed
    # 5-11°C, rain < 35%
    return '🌫️'         # Grey / cool


# ── Language configs ──────────────────────────────────────────────────────────

MONTHS_FR = ['Janvier','Février','Mars','Avril','Mai','Juin',
             'Juillet','Août','Septembre','Octobre','Novembre','Décembre']

MONTHS_EN = ['January','February','March','April','May','June',
             'July','August','September','October','November','December']

LANG_FR = {
    'months': MONTHS_FR,
    'badge_excellent': '✅ Excellent',
    'badge_good': '✅ Favorable',
    'badge_fair': '⚠️ Acceptable',
    'badge_poor': '❌ Peu favorable',
    'tier_peak': '💸 Haute saison',
    'tier_low': '✅ Prix bas',
    'tier_shoulder': '🌿 Épaule',
    'seasons': {'Printemps': [2,3,4], 'Été': [5,6,7], 'Automne': [8,9,10], 'Hiver': [11,0,1]},
    'verdict_excellent': 'Excellente période',
    'verdict_good': 'Bonne période',
    'verdict_fair': 'Période acceptable',
    'verdict_poor': 'Période difficile',
    'table_aria': 'Tableau climat mensuel {}',
    'table_headers': '<th>Mois</th><th>T° min</th><th>T° max</th><th>Jours de pluie (%)</th><th>Précip. mm/j</th><th>Soleil h/j</th><th>Score</th>',
    'table_ski_header': '<th>Score ski 🎿</th>',
    'legend_ideal': 'Idéal',
    'legend_fair': 'Acceptable',
    'legend_off': 'Défavorable',
    'legend_source': 'Source Open-Meteo · 10 ans',
    'val_missing_months': '[P0] {slug}: mois manquants: {missing}',
    'val_score_range': '[P0] {slug}/{month}: score hors plage ({score})',
    'val_class_invalid': '[P0] {slug}/{month}: classe invalide ({cls})',
    'val_score_class': '[P1] {slug}/{month}: score {score} incohérent avec classe {cls}',
    'val_no_climate': '[P1] {slug}: dans destinations.csv mais pas de données climat',
    'val_card_missing': '[P2] {slug}: pas de card projet',
}

LANG_EN = {
    'months': MONTHS_EN,
    'badge_excellent': '✅ Excellent',
    'badge_good': '✅ Good',
    'badge_fair': '⚠️ Fair',
    'badge_poor': '❌ Poor',
    'tier_peak': '💸 Peak season',
    'tier_low': '✅ Low season',
    'tier_shoulder': '🌿 Shoulder',
    'seasons': {'Spring': [2,3,4], 'Summer': [5,6,7], 'Autumn': [8,9,10], 'Winter': [11,0,1]},
    'verdict_excellent': 'Excellent time',
    'verdict_good': 'Good time',
    'verdict_fair': 'Acceptable',
    'verdict_poor': 'Not recommended',
    'table_aria': 'Monthly climate table {}',
    'table_headers': '<th>Month</th><th>Min °C</th><th>Max °C</th><th>Rainy days (%)</th><th>Precip. mm/d</th><th>Sun h/d</th><th>Score</th>',
    'table_ski_header': '<th>Ski score 🎿</th>',
    'legend_ideal': 'Ideal',
    'legend_fair': 'Fair',
    'legend_off': 'Unfavourable',
    'legend_source': 'Source: Open-Meteo · 10 years',
    'val_missing_months': '[P0] {slug}: missing months: {missing}',
    'val_score_range': '[P0] {slug}/{month}: score out of range ({score})',
    'val_class_invalid': '[P0] {slug}/{month}: invalid class ({cls})',
    'val_score_class': '[P1] {slug}/{month}: score {score} inconsistent with class {cls}',
    'val_no_climate': '[P1] {slug}: in destinations.csv but no climate data',
    'val_card_missing': '[P2] {slug}: no project card',
}


# ── Shared functions ──────────────────────────────────────────────────────────

def score_badge(score, classe=None, L=LANG_FR):
    """Badge verdict aligned with editorial class from CSV."""
    if classe == 'rec':
        if score >= 9.0: return '#dcfce7', '#16a34a', L['badge_excellent']
        return '#dcfce7', '#16a34a', L['badge_good']
    if classe == 'mid':
        return '#fef9c3', '#ca8a04', L['badge_fair']
    if classe == 'avoid':
        return '#fee2e2', '#dc2626', L['badge_poor']
    # Fallback if no class
    if score >= 9.0: return '#dcfce7', '#16a34a', L['badge_excellent']
    if score >= 7.5: return '#dcfce7', '#16a34a', L['badge_good']
    if score >= 6.0: return '#fef9c3', '#ca8a04', L['badge_fair']
    return '#fee2e2', '#dc2626', L['badge_poor']


def best_months(months, L=LANG_FR):
    """Return list of months tied for highest score."""
    max_score = max(m['score'] for m in months)
    return [L['months'][i] for i, m in enumerate(months) if m['score'] == max_score]


def budget_tier(score, all_scores, L=LANG_FR):
    """Relative tier: top 4 = Peak, bottom 4 = Low, rest = Shoulder."""
    sorted_scores = sorted(all_scores, reverse=True)
    n = len(sorted_scores)
    top = sorted_scores[min(3, n-1)]
    bottom = sorted_scores[max(n-5, 0)]
    if score >= top:   return L['tier_peak']
    if score <= bottom: return L['tier_low']
    return L['tier_shoulder']


def seasonal_stats(months, L=LANG_FR):
    """Compute stats per season."""
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


def bar_chart(pct, max_val=100):
    """ASCII bar chart (language-independent)."""
    filled = round((pct / max_val) * 10)
    return '█' * filled + '░' * (10 - filled)


def climate_table_html(months, nom, is_mountain=False, L=LANG_FR):
    """Generate climate table HTML."""
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
                 f'<td>{weather_emoji(m["tmax"], m["rain_pct"], m["sun_h"])} {L["months"][i]}</td>'
                 f'<td>{m["tmin"]}°C</td><td>{m["tmax"]}°C</td>'
                 f'<td>{m["rain_pct"]}%</td>'
                 f'<td>{m["precip"]:.1f}</td>'
                 f'<td>{m["sun_h"]}h</td>'
                 f'<td>{m["score"]:.1f}/10</td>{ski_col}</tr>\n')
    ski_header = L['table_ski_header'] if is_mountain else ''
    wrap_class = 'climate-table-wrap mountain' if is_mountain else 'climate-table-wrap'
    return f'''<div class="{wrap_class}">
 <table class="climate-table" aria-label="{L['table_aria'].format(nom)}">
 <thead><tr>{L['table_headers']}{ski_header}</tr></thead>
 <tbody>{rows}</tbody>
 </table>
</div>
<div class="table-legend">
 <span><span class="legend-dot" style="background:#1a7a4a"></span>{L['legend_ideal']}</span>
 <span><span class="legend-dot" style="background:#d97706"></span>{L['legend_fair']}</span>
 <span><span class="legend-dot" style="background:#dc2626"></span>{L['legend_off']}</span>
 <span style="margin-left:auto">{L['legend_source']}</span>
</div>'''


def validate_climate(climate, months_list, L=LANG_FR):
    """Validate climate data consistency. Returns list of error strings."""
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
            # Score/class coherence
            if c == 'rec' and s < 6.5:
                errors.append(L['val_score_class'].format(slug=slug, month=month, score=s, cls=c))
            elif c == 'avoid' and s > 4.5:
                errors.append(L['val_score_class'].format(slug=slug, month=month, score=s, cls=c))
    return errors
