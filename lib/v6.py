"""
lib/v6.py — Helpers pour le rendu HTML V6.

Architecture Option B : ce module est isolé de V5. Il fournit des fonctions
pures qui retournent des chunks HTML, pour être appelées depuis
generate_pages.py::gen_annual_v6() (à venir).

Convention de signature :
    Tous les helpers prennent au minimum (slug: str, lang: str) et accèdent
    aux locales V6 via _v6_strings(lang).

Conventions HTML :
    - Aucun `<html>`, `<head>` ou `<body>` ici, que des fragments de section.
    - Indentation 4 espaces dans les fragments.
    - Pas de `style="..."` inline sauf nécessité (filtres SVG, etc.).
    - Toutes les chaînes d'interface viennent de locales/*.json sous "v6".
"""

from __future__ import annotations
import json
import os
from html import escape as h

from lib.common import c_to_f


def _fmt_t(value: float, lang: str) -> str:
    """Format température selon langue. EN-US imperial → °F, sinon °C.

    Args:
        value: température en °C (toujours stockée en °C dans les data)
        lang: langue UI ('fr', 'en', 'en-us', 'es', 'de')
    Returns:
        '72°F' si lang='en-us', sinon '22°C'
    """
    if lang == 'en-us':
        return f'{c_to_f(value)}°F'
    return f'{value:.0f}°C'

_LOCALE_DIR = os.path.join(os.path.dirname(__file__), '..', 'locales')
_v6_cache: dict[str, dict] = {}


def _v6_strings(lang: str) -> dict:
    """Charge et cache les chaînes V6 pour une langue donnée.

    Retourne un dict structuré : {topbar:{...}, footer:{...}, method:{...}, ...}.
    Lève KeyError si la clé "v6" n'existe pas dans le locale (= langue pas
    encore traduite pour V6).
    """
    if lang in _v6_cache:
        return _v6_cache[lang]
    path = os.path.join(_LOCALE_DIR, f'{lang}.json')
    with open(path, encoding='utf-8') as f:
        loc = json.load(f)
    if 'v6' not in loc:
        raise KeyError(
            f"locales/{lang}.json n'a pas de section 'v6'. "
            f"V6 multilangue requiert que toutes les langues aient les chaînes V6."
        )
    _v6_cache[lang] = loc['v6']
    return _v6_cache[lang]


# ─────────────────────────────────────────────────────────────────────────────
# Helper 1 : TOPBAR
# ─────────────────────────────────────────────────────────────────────────────

def render_v6_topbar(slug: str, lang: str = 'fr') -> str:
    """Rend le topbar V6 : brand · ♡ · share · CTA Planifier.

    Le brand pointe toujours vers '/' (home). Le CTA pointe vers #planifier
    (ancre dans la page). Les SVG icônes sont en currentColor pour héritage
    du style depuis le CSS .topbar-icon-btn.
    """
    L = _v6_strings(lang)['topbar']
    fav_aria = h(L['fav_aria'])
    share_aria = h(L['share_aria'])
    cta_long = h(L['cta_long'])
    cta_short = h(L['cta_short'])
    slug_attr = h(slug)

    return f'''<div class="topbar">
  <div class="container topbar-inner">
    <a class="brand" href="/">Best<em>Date</em>Weather</a>
    <div class="topbar-actions">
      <button id="btn-fav" class="topbar-icon-btn btn-fav" data-slug="{slug_attr}" onclick="bdwToggleFav(this)" aria-label="{fav_aria}" aria-pressed="false"><svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/></svg></button>
      <button class="topbar-icon-btn nav-share" onclick="shareThis()" aria-label="{share_aria}"><svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><path d="M8.59 13.51l6.83 3.98M15.41 6.51l-6.82 3.98"/></svg></button>
    </div>
    <a class="btn primary cta-plan" href="#planifier">✈️ <span class="cta-label-long">{cta_long}</span><span class="cta-label-short">{cta_short}</span></a>
  </div>
</div>'''


# ─────────────────────────────────────────────────────────────────────────────
# Helper 2 : FOOTER
# ─────────────────────────────────────────────────────────────────────────────

# Mapping des slugs i18n par langue : prefix URL + slug spécifique langue
# Le slug FR est utilisé comme clé (référence canonique).
_LANG_URL_PREFIX = {
    'fr':    {'prefix': '',        'tpl': 'meilleure-periode-{slug}.html'},
    'en':    {'prefix': 'en/',     'tpl': 'best-time-to-visit-{slug}.html'},
    'en-us': {'prefix': 'us/',     'tpl': 'best-time-to-visit-{slug}.html'},
    'es':    {'prefix': 'es/',     'tpl': 'mejor-epoca-{slug}.html'},
    'de':    {'prefix': 'de/',     'tpl': 'beste-reisezeit-{slug}.html'},
}

_LANG_FLAGS = {
    'en':    ('gb.png', 'English'),
    'en-us': ('us.png', 'English (US)'),
    'es':    ('es.png', 'Español'),
    'de':    ('de.png', 'Deutsch'),
    'fr':    ('fr.png', 'Français'),
}


def _other_lang_links(slug_fr: str, slug_en: str, slug_es: str, slug_de: str,
                      current_lang: str) -> list[tuple[str, str, str]]:
    """Retourne la liste (href, flag_filename, label) pour les langues autres
    que current_lang. Utilise les slugs spécifiques par langue.

    Note: si current_lang est dans un sous-dossier (en/us/es/de), prefixe ../
    pour remonter d'un cran avant d'accéder au préfixe de la langue cible.
    """
    slugs = {'fr': slug_fr, 'en': slug_en, 'en-us': slug_en, 'es': slug_es, 'de': slug_de}
    # Préfixe ../ si on est dans un sous-dossier
    parent = '../' if current_lang != 'fr' else ''
    out = []
    for lang in ('en', 'en-us', 'es', 'de', 'fr'):
        if lang == current_lang:
            continue
        s = slugs.get(lang) or slug_fr
        cfg = _LANG_URL_PREFIX[lang]
        href = parent + cfg['prefix'] + cfg['tpl'].format(slug=s)
        flag, label = _LANG_FLAGS[lang]
        out.append((href, flag, label))
    return out


def render_v6_footer(slug_fr: str, lang: str = 'fr',
                     slug_en: str = '', slug_es: str = '', slug_de: str = '',
                     asset_prefix: str = '') -> str:
    """Rend le footer V6 dark navy avec drapeaux des autres langues sur 1 ligne.

    Args:
        slug_fr: slug canonique FR (ex: 'chamonix')
        lang: langue actuelle ('fr', 'en', 'en-us', 'es', 'de')
        slug_en/slug_es/slug_de: slugs traduits dans destinations.csv. Si
            vide, fallback sur slug_fr.

    Returns:
        HTML <footer> complet, prêt à insérer.
    """
    L = _v6_strings(lang)['footer']
    slug_en = slug_en or slug_fr
    slug_es = slug_es or slug_fr
    slug_de = slug_de or slug_fr

    # Construire les liens vers les pages-soeurs
    links = _other_lang_links(slug_fr, slug_en, slug_es, slug_de, lang)
    lang_html_parts = []
    for href, flag, label in links:
        lang_html_parts.append(
            f'<a href="{h(href)}"><img src="{asset_prefix}flags/{flag}" width="20" height="15" alt="" loading="lazy"> {h(label)}</a>'
        )
    lang_html = '<span class="sep">·</span>'.join(lang_html_parts)

    # Liens internes (méthodologie/FAQ/etc.) - utilisent les noms i18n des pages
    # Pour FR : pages s'appellent methodologie.html / a-propos.html / faq.html / index.html / widgets.html
    # Pour autres langues : variantes traduites (à compléter ultérieurement)
    if lang == 'fr':
        m_url, a_url, faq_url, app_url, w_url = 'methodologie.html', 'a-propos.html', 'faq.html', 'index.html', 'widgets.html'
        ml_url, p_url, c_url = 'mentions-legales.html', 'confidentialite.html', 'contact.html'
    elif lang == 'en':
        m_url, a_url, faq_url, app_url = '../en/methodology.html', '../en/about.html', '../en/faq.html', '../en/app.html'
        w_url = '../widgets.html'  # widgets uniquement en FR pour l'instant
        ml_url, p_url, c_url = '../en/legal.html', '../en/privacy.html', '../en/contact.html'
    elif lang == 'en-us':
        m_url, a_url, faq_url, app_url = '../us/methodology.html', '../us/about.html', '../us/faq.html', '../us/app.html'
        w_url = '../widgets.html'  # widgets uniquement en FR pour l'instant
        ml_url, p_url, c_url = '../us/legal.html', '../us/privacy.html', '../us/contact.html'
    elif lang == 'es':
        m_url, a_url, faq_url, app_url = '../es/metodologia.html', '../es/sobre-nosotros.html', '../es/faq.html', '../es/app.html'
        w_url = '../widgets.html'  # widgets uniquement en FR pour l'instant
        ml_url, p_url, c_url = '../es/aviso-legal.html', '../es/privacidad.html', '../es/contacto.html'
    elif lang == 'de':
        m_url, a_url, faq_url, app_url = '../de/methodik.html', '../de/ueber-uns.html', '../de/faq.html', '../de/app.html'
        w_url = '../widgets.html'  # widgets uniquement en FR pour l'instant
        ml_url, p_url, c_url = '../de/impressum.html', '../de/datenschutz.html', '../de/kontakt.html'
    else:
        raise ValueError(f"Unknown lang: {lang}")

    return f'''<footer class="bdw-footer">
  <div class="container">
    <p class="bdw-footer-brand">bestdateweather.com</p>
    <p><a href="https://open-meteo.com/" rel="noopener">{h(L['data_link'])}</a> · <span class="bdw-footer-sub">{h(L['data_sources'])}</span></p>
    <p class="bdw-footer-links"><a href="{m_url}">{h(L['methodology'])}</a> · <a href="{a_url}">{h(L['about'])}</a> · <a href="{faq_url}">{h(L['faq'])}</a> · <a href="{app_url}">{h(L['app'])}</a> · <a href="{w_url}">{h(L['widgets'])}</a></p>
    <p class="bdw-footer-langs">{lang_html}</p>
    <p class="bdw-footer-legal"><a href="{ml_url}">{h(L['legal'])}</a> · <a href="{p_url}">{h(L['privacy'])}</a> · <a href="{c_url}">{h(L['contact'])}</a></p>
  </div>
</footer>'''


# ─────────────────────────────────────────────────────────────────────────────
# Helper 3 : METHODOLOGY BLOCK
# ─────────────────────────────────────────────────────────────────────────────

def render_v6_methodology_block(lang: str = 'fr', is_mountain: bool = False) -> str:
    """Rend le bloc méthodologie compacté pour le right-stack du decider."""
    # URL méthodologie localisée
    method_urls = {
        'fr': 'methodologie.html',
        'en': 'en/methodology.html',
        'en-us': 'us/methodology.html',
        'es': 'es/metodologia.html',
        'de': 'de/methodik.html',
    }
    method_url = method_urls.get(lang, 'methodologie.html')
    # Sur les pages dans /en/ /us/ /es/ /de/, on doit remonter d'un cran
    if lang != 'fr':
        method_url = '../' + method_url
    """Rend le bloc 'Comment on calcule le score' pour le right-stack du Décider.

    - Mountain : 2 sub-cards (Score ski + Score rando) avec leurs critères et
      pondérations alignées sur scoring.py::compute_ski_score / compute_hiking_score.
    - Standard : 1 liste avec les 4 critères de compute_score.

    L'output va dans la section .right-stack du Décider, après cta-row.
    """
    L = _v6_strings(lang)['method']

    if is_mountain:
        return f'''<div class="method-mini">
  <h3>{h(L['title'])}</h3>
  <p class="method-mini-intro">{L['intro_mtn']}</p>
  <div class="method-mini-model">
    <div class="method-mini-model-head">
      <span class="method-mini-ico">⛷️</span><strong>{h(L['ski_title'])}</strong>
      <span class="method-mini-period">{h(L['ski_period'])}</span>
    </div>
    <ul class="method-mini-list">
      <li>{L['ski_c1']}</li>
      <li>{L['ski_c2']}</li>
      <li>{L['ski_c3']}</li>
      <li>{L['ski_c4']}</li>
    </ul>
  </div>
  <div class="method-mini-model">
    <div class="method-mini-model-head">
      <span class="method-mini-ico">🥾</span><strong>{h(L['rando_title'])}</strong>
      <span class="method-mini-period">{h(L['rando_period'])}</span>
    </div>
    <ul class="method-mini-list">
      <li>{L['rando_c1']}</li>
      <li>{L['rando_c2']}</li>
      <li>{L['rando_c3']}</li>
    </ul>
  </div>
  <p class="method-mini-foot"><strong>{h(L['source'])} :</strong> {h(L['source_text'])} · <a href="{method_url}">{h(L['full_link'])}</a></p>
</div>'''
    else:
        return f'''<div class="method-mini">
  <h3>{h(L['title'])}</h3>
  <p class="method-mini-intro">{L['intro_std']}</p>
  <ul class="method-mini-list">
    <li>{L['std_c1']}</li>
    <li>{L['std_c2']}</li>
    <li>{L['std_c3']}</li>
    <li>{L['std_c4']}</li>
  </ul>
  <p class="method-mini-foot"><strong>{h(L['source'])} :</strong> {h(L['source_text'])} · <a href="{method_url}">{h(L['full_link'])}</a></p>
</div>'''


# ─────────────────────────────────────────────────────────────────────────────
# Helper 4 : DECIDER (section "Quand partir à X ?" - reprend le prototype)
# ─────────────────────────────────────────────────────────────────────────────

# Labels i18n inline (5 langues × ~20 strings)
_DECIDER_I18N = {
    'fr': {
        'kicker': 'Décider',
        'h2_tpl': 'Quand partir à {dest} ?',
        'lead': 'La décision se joue sur plusieurs critères. Score climatique, foule touristique et activités possibles.',
        'verdict_label': 'Verdict :',
        'verdict_tpl': 'À {dest}, {top1} et {top2} sortent clairement du lot. {worst} concentre les conditions les moins favorables.',
        'avis_label': "L'avis de Gilles",
        'avis_role': 'Fondateur · BestDateWeather',
        'top_avoid': 'Top & à éviter',
        'legend_best': 'Meilleure période · ≥ 7',
        'legend_mid': 'Période correcte · 4 – 7',
        'legend_bad': 'Conditions marquées · < 4',
        'right1_title': "Ce qu'on comprend en 5 secondes",
        'summary_tpl': '{dest} offre {n_good} mois confortables, avec {n_bad} mois à éviter ({bad_months}). Le delta est marqué : {top} en {top_month} vs {worst} en {worst_month}.',
        'summary_no_bad': '{dest} offre {n_good} mois confortables, sans mois vraiment à éviter. Le delta reste mesuré : {top} en {top_month} vs {worst} en {worst_month}.',
        'right2_title': "Ce qu'il faut vérifier ensuite",
        'right2_text': 'Votre tolérance à la foule et au budget. Les meilleurs mois concentrent la saturation touristique et les prix plus hauts. Les entre-saisons offrent un bon compromis.',
        'right3_title': 'Action suivante',
        'right3_text': 'Descendre au tableau détaillé pour comparer mois à mois, puis ouvrir la fiche du mois qui vous intéresse.',
        'cta_compare': 'Comparer les 12 mois',
        'cta_byproject': 'Selon votre projet',
        'none': 'aucun',
    },
    'en': {
        'kicker': 'Decide',
        'h2_tpl': 'When to visit {dest}?',
        'lead': 'The decision rests on several criteria. Climate score, tourist crowds and feasible activities.',
        'verdict_label': 'Verdict:',
        'verdict_tpl': 'In {dest}, {top1} and {top2} clearly stand out. {worst} concentrates the least favourable conditions.',
        'avis_label': "Gilles's view",
        'avis_role': 'Founder · BestDateWeather',
        'top_avoid': 'Top & avoid',
        'legend_best': 'Best period · ≥ 7',
        'legend_mid': 'Decent period · 4 – 7',
        'legend_bad': 'Tough conditions · < 4',
        'right1_title': 'What you grasp in 5 seconds',
        'summary_tpl': '{dest} offers {n_good} comfortable months, with {n_bad} months to avoid ({bad_months}). The gap is sharp: {top} in {top_month} vs {worst} in {worst_month}.',
        'summary_no_bad': '{dest} offers {n_good} comfortable months, without any month really to avoid. The gap stays moderate: {top} in {top_month} vs {worst} in {worst_month}.',
        'right2_title': 'What to check next',
        'right2_text': 'Your tolerance for crowds and budget. The best months concentrate tourist saturation and higher prices. Shoulder seasons offer a good compromise.',
        'right3_title': 'Next action',
        'right3_text': 'Scroll down to the detailed table to compare month by month, then open the page of the month that interests you.',
        'cta_compare': 'Compare the 12 months',
        'cta_byproject': 'By your project',
        'none': 'none',
    },
    'en-us': {
        'kicker': 'Decide',
        'h2_tpl': 'When to visit {dest}?',
        'lead': 'The decision rests on several criteria. Climate score, tourist crowds and feasible activities.',
        'verdict_label': 'Verdict:',
        'verdict_tpl': 'In {dest}, {top1} and {top2} clearly stand out. {worst} concentrates the least favorable conditions.',
        'avis_label': "Gilles's view",
        'avis_role': 'Founder · BestDateWeather',
        'top_avoid': 'Top & avoid',
        'legend_best': 'Best period · ≥ 7',
        'legend_mid': 'Decent period · 4 – 7',
        'legend_bad': 'Tough conditions · < 4',
        'right1_title': 'What you grasp in 5 seconds',
        'summary_tpl': '{dest} offers {n_good} comfortable months, with {n_bad} months to avoid ({bad_months}). The gap is sharp: {top} in {top_month} vs {worst} in {worst_month}.',
        'summary_no_bad': '{dest} offers {n_good} comfortable months, without any month really to avoid. The gap stays moderate: {top} in {top_month} vs {worst} in {worst_month}.',
        'right2_title': 'What to check next',
        'right2_text': 'Your tolerance for crowds and budget. The best months concentrate tourist saturation and higher prices. Shoulder seasons offer a good compromise.',
        'right3_title': 'Next action',
        'right3_text': 'Scroll down to the detailed table to compare month by month, then open the page of the month that interests you.',
        'cta_compare': 'Compare the 12 months',
        'cta_byproject': 'By your project',
        'none': 'none',
    },
    'es': {
        'kicker': 'Decidir',
        'h2_tpl': '¿Cuándo viajar a {dest}?',
        'lead': 'La decisión depende de varios criterios. Puntuación climática, multitudes turísticas y actividades posibles.',
        'verdict_label': 'Veredicto:',
        'verdict_tpl': 'En {dest}, {top1} y {top2} destacan claramente. {worst} concentra las condiciones menos favorables.',
        'avis_label': 'La opinión de Gilles',
        'avis_role': 'Fundador · BestDateWeather',
        'top_avoid': 'Mejores y peores',
        'legend_best': 'Mejor periodo · ≥ 7',
        'legend_mid': 'Periodo correcto · 4 – 7',
        'legend_bad': 'Condiciones difíciles · < 4',
        'right1_title': 'Lo que se entiende en 5 segundos',
        'summary_tpl': '{dest} ofrece {n_good} meses cómodos, con {n_bad} meses a evitar ({bad_months}). La diferencia es marcada: {top} en {top_month} vs {worst} en {worst_month}.',
        'summary_no_bad': '{dest} ofrece {n_good} meses cómodos, sin meses realmente a evitar. La diferencia es moderada: {top} en {top_month} vs {worst} en {worst_month}.',
        'right2_title': 'Lo que hay que verificar después',
        'right2_text': 'Su tolerancia a las multitudes y al presupuesto. Los mejores meses concentran la saturación turística y los precios más altos. Las temporadas intermedias ofrecen un buen compromiso.',
        'right3_title': 'Acción siguiente',
        'right3_text': 'Bajar a la tabla detallada para comparar mes a mes, luego abrir la ficha del mes que le interese.',
        'cta_compare': 'Comparar los 12 meses',
        'cta_byproject': 'Según su proyecto',
        'none': 'ninguno',
    },
    'de': {
        'kicker': 'Entscheiden',
        'h2_tpl': 'Wann nach {dest} reisen?',
        'lead': 'Die Entscheidung hängt von mehreren Kriterien ab. Klimawert, Touristenandrang und mögliche Aktivitäten.',
        'verdict_label': 'Urteil:',
        'verdict_tpl': 'In {dest} stechen {top1} und {top2} klar hervor. {worst} konzentriert die ungünstigsten Bedingungen.',
        'avis_label': 'Gilles\' Meinung',
        'avis_role': 'Gründer · BestDateWeather',
        'top_avoid': 'Beste & schlechteste',
        'legend_best': 'Beste Zeit · ≥ 7',
        'legend_mid': 'Akzeptable Zeit · 4 – 7',
        'legend_bad': 'Schwierige Bedingungen · < 4',
        'right1_title': 'Was man in 5 Sekunden versteht',
        'summary_tpl': '{dest} bietet {n_good} angenehme Monate, mit {n_bad} zu vermeidenden Monaten ({bad_months}). Der Unterschied ist deutlich: {top} im {top_month} vs {worst} im {worst_month}.',
        'summary_no_bad': '{dest} bietet {n_good} angenehme Monate, ohne wirklich zu vermeidenden Monat. Der Unterschied bleibt moderat: {top} im {top_month} vs {worst} im {worst_month}.',
        'right2_title': 'Was als Nächstes zu prüfen ist',
        'right2_text': 'Ihre Toleranz gegenüber Menschenmassen und Budget. Die besten Monate konzentrieren die touristische Sättigung und die höheren Preise. Die Zwischensaisons bieten einen guten Kompromiss.',
        'right3_title': 'Nächste Aktion',
        'right3_text': 'Nach unten zur Detailtabelle scrollen, um Monat für Monat zu vergleichen, dann die Seite des gewünschten Monats öffnen.',
        'cta_compare': 'Die 12 Monate vergleichen',
        'cta_byproject': 'Nach Ihrem Projekt',
        'none': 'keine',
    },
}


# Abréviations courtes mois (3-4 lettres) pour les barres du décider.
# Évite les collisions ('Juin'→'Jui' et 'Juillet'→'Jui' = collision en FR).
# Aligné avec le prototype paris-v6.html.
_MONTH_ABBR = {
    'fr':    ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin', 'Juil', 'Aoû',  'Sep', 'Oct', 'Nov', 'Déc'],
    'en':    ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',  'Jul',  'Aug',  'Sep', 'Oct', 'Nov', 'Dec'],
    'en-us': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',  'Jul',  'Aug',  'Sep', 'Oct', 'Nov', 'Dec'],
    'es':    ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun',  'Jul',  'Ago',  'Sep', 'Oct', 'Nov', 'Dic'],
    'de':    ['Jan', 'Feb', 'Mär', 'Apr', 'Mai', 'Jun',  'Jul',  'Aug',  'Sep', 'Okt', 'Nov', 'Dez'],
}


def _bar_class(score: float, is_top: bool) -> str:
    """Détermine la classe CSS d'une barre de score (best/good/mid/low/bad)."""
    if score >= 7 and is_top:
        return 'best'
    if score >= 7:
        return 'good'
    if score >= 5:
        return 'mid'
    if score >= 4:
        return 'low'
    return 'bad'


def render_v6_decider(slug: str, lang: str, dest_name: str,
                       months_data: list[dict], editorial_html: str,
                       is_mountain: bool = False) -> str:
    """Rend la section #decider du prototype V6 (Quand partir à X ?).

    Reproduit la structure complète du prototype paris-v6.html :
    - Verdict + avis Gilles (avatar G + édito) + pills (Top 4 + 1 bad)
    - Bars chart 12 mois avec scores + légende
    - Right-stack : 3 right-items + cta-row + method-mini compactée

    Args:
        slug: identifiant destination (FR canonical)
        lang: 'fr', 'en', 'en-us', 'es', 'de'
        dest_name: nom localisé de la destination (ex 'Paris', 'Cinque Terre')
        months_data: liste de 12 dicts avec 'mois' (localisé) et 'score_10' (0-10)
        editorial_html: HTML édito de l'avis Gilles depuis avis_annuel.json
        is_mountain: True si destination mountain (méthodologie ski/rando)
    """
    L = _DECIDER_I18N.get(lang, _DECIDER_I18N['fr'])
    method_block = render_v6_methodology_block(lang, is_mountain=is_mountain)

    # ── Calculs : top 4 mois, worst, etc. ──
    sorted_months = sorted(months_data, key=lambda m: -m['score_10'])
    top_months = sorted_months[:4]
    worst_month = sorted_months[-1]
    top_score = top_months[0]['score_10']
    worst_score = worst_month['score_10']

    # ── Verdict text auto-généré ──
    verdict_text = L['verdict_tpl'].format(
        dest=dest_name,
        top1=top_months[0]['mois'],
        top2=top_months[1]['mois'],
        worst=worst_month['mois'],
    )

    # ── Avis card ──
    avis_card = (
        f'<div class="avis-card">\n'
        f'  <div class="avis-head">\n'
        f'    <div class="avis-avatar">G</div>\n'
        f'    <div class="avis-meta">\n'
        f'      <div class="avis-label">{h(L["avis_label"])}</div>\n'
        f'      <div class="avis-role">{h(L["avis_role"])}</div>\n'
        f'    </div>\n'
        f'  </div>\n'
        f'  <p class="avis-edito">{editorial_html}</p>\n'
        f'</div>'
    )

    # ── Pills : Top 4 + 1 bad ──
    pill_items = []
    for i, m in enumerate(top_months):
        prefix = '🏆 ' if i == 0 else ''
        pill_items.append(
            f'<span class="pill good">{prefix}{h(m["mois"])} · {m["score_10"]:.1f}</span>'
        )
    pill_items.append(
        f'<span class="pill bad">⚠️ {h(worst_month["mois"])} · {worst_score:.1f}</span>'
    )
    pills_html = '\n              '.join(pill_items)

    # ── Bars chart 12 mois ──
    top_month_name = top_months[0]['mois']
    abbr_list = _MONTH_ABBR.get(lang, _MONTH_ABBR['fr'])
    bar_items = []
    for i, m in enumerate(months_data):
        score = m['score_10']
        height_pct = max(5, int(score * 10))  # min 5% pour visibilité barre vide
        is_top = (m['mois'] == top_month_name)
        bar_class = _bar_class(score, is_top)
        # Abréviation mois (3-4 lettres) sans collision (Juin/Juil distincts en FR)
        label = abbr_list[i] if i < 12 else m['mois'][:3]
        bar_items.append(
            f'<div class="bar-wrap"><div class="bar-slot">'
            f'<div class="bar {bar_class}" style="height:{height_pct}%"></div></div>'
            f'<div class="bar-score">{score:.1f}</div>'
            f'<div class="bar-label">{h(label)}</div></div>'
        )
    bars_html = '\n              '.join(bar_items)

    # ── Légende bars ──
    legend_html = (
        f'<div style="display:flex;gap:14px;flex-wrap:wrap;margin-top:14px;'
        f'justify-content:center;font-size:11px;color:var(--muted)">\n'
        f'  <span style="display:inline-flex;align-items:center;gap:5px">'
        f'<span style="width:11px;height:11px;border-radius:3px;'
        f'background:linear-gradient(180deg,#2ea86a 0%,#1a7a4a 100%)"></span>'
        f'{h(L["legend_best"])}</span>\n'
        f'  <span style="display:inline-flex;align-items:center;gap:5px">'
        f'<span style="width:11px;height:11px;border-radius:3px;'
        f'background:linear-gradient(180deg,#ecc568 0%,#b8860b 100%)"></span>'
        f'{h(L["legend_mid"])}</span>\n'
        f'  <span style="display:inline-flex;align-items:center;gap:5px">'
        f'<span style="width:11px;height:11px;border-radius:3px;'
        f'background:linear-gradient(180deg,#b91c1c 0%,#8b1616 100%)"></span>'
        f'{h(L["legend_bad"])}</span>\n'
        f'</div>'
    )

    # ── Right-stack : 3 right-items + cta-row + method-mini ──
    n_good = sum(1 for m in months_data if m['score_10'] >= 7)
    bad_months_list = [m['mois'] for m in months_data if m['score_10'] < 4]
    n_bad = len(bad_months_list)
    bad_months_str = ', '.join(bad_months_list) if bad_months_list else L['none']
    summary_tpl = L['summary_tpl'] if n_bad > 0 else L['summary_no_bad']
    summary_5s = summary_tpl.format(
        dest=dest_name, n_good=n_good, n_bad=n_bad,
        bad_months=bad_months_str,
        top=f'{top_score:.1f}',
        worst=f'{worst_score:.1f}',
        top_month=top_months[0]['mois'],
        worst_month=worst_month['mois'],
    )

    right_stack = (
        f'<div class="card pad right-stack">\n'
        f'  <div class="right-item">\n'
        f'    <h3>{h(L["right1_title"])}</h3>\n'
        f'    <p>{h(summary_5s)}</p>\n'
        f'  </div>\n'
        f'  <div class="right-item">\n'
        f'    <h3>{h(L["right2_title"])}</h3>\n'
        f'    <p>{h(L["right2_text"])}</p>\n'
        f'  </div>\n'
        f'  <div class="right-item">\n'
        f'    <h3>{h(L["right3_title"])}</h3>\n'
        f'    <p>{h(L["right3_text"])}</p>\n'
        f'  </div>\n'
        f'  <div class="cta-row">\n'
        f'    <a class="btn primary" href="#tableau">{h(L["cta_compare"])}</a>\n'
        f'    <a class="btn" href="#par-projet">{h(L["cta_byproject"])}</a>\n'
        f'  </div>\n'
        f'  {method_block}\n'
        f'</div>'
    )

    # ── Assemblage final ──
    h2_text = L['h2_tpl'].format(dest=dest_name)
    return (
        f'<section id="decider">\n'
        f'  <div class="container">\n'
        f'    <div class="section-head">\n'
        f'      <div class="section-kicker">{h(L["kicker"])}</div>\n'
        f'      <h2>{h(h2_text)}</h2>\n'
        f'      <p class="lead">{h(L["lead"])}</p>\n'
        f'    </div>\n'
        f'    <div class="decider-grid">\n'
        f'      <div class="verdict-box">\n'
        f'        <div class="verdict-note"><strong>{h(L["verdict_label"])}</strong> {h(verdict_text)}</div>\n'
        f'        {avis_card}\n'
        f'        <div>\n'
        f'          <div class="small-label">{h(L["top_avoid"])}</div>\n'
        f'          <div class="pills">\n'
        f'              {pills_html}\n'
        f'          </div>\n'
        f'        </div>\n'
        f'        <div>\n'
        f'          <div class="bars">\n'
        f'              {bars_html}\n'
        f'          </div>\n'
        f'          {legend_html}\n'
        f'        </div>\n'
        f'      </div>\n'
        f'      {right_stack}\n'
        f'    </div>\n'
        f'  </div>\n'
        f'</section>'
    )


# ─────────────────────────────────────────────────────────────────────────────
# Helper 5 : INFOS PRATIQUES (Box 3 adaptative selon profil)
# ─────────────────────────────────────────────────────────────────────────────

# Mapping pays → code drapeau ISO 3166-1 alpha-2 (fichier flags/{iso2}.png)
# La carto est dans country_info.json indirectement, mais on a aussi un mapping
# direct dans destinations.csv (colonne 'flag').
def _safe_int(v) -> int | None:
    try:
        return int(v) if v is not None and str(v).strip() else None
    except (ValueError, TypeError):
        return None


def _list_item(icon: str, label: str, value: str, hint: str | None = None) -> str:
    """Helper : un .list-item avec icône, label, value, et tooltip optionnel."""
    hint_html = (
        f' <span class="signal-hint" title="{h(hint)}">ⓘ</span>'
        if hint else ''
    )
    return (f'<div class="list-item"><span><span class="list-ico">{icon}</span>'
            f'{h(label)}{hint_html}</span><strong>{value}</strong></div>')


def _detect_profile(is_mountain: bool, is_coastal: bool, is_tropical: bool,
                    is_polar: bool = False) -> str:
    """Détermine le profil pour Box 3.

    Ordre de priorité (un seul profil retourné) :
        polar > tropical > mountain > coastal > city
    """
    if is_polar:
        return 'polar'
    if is_tropical:
        return 'tropical'
    if is_mountain:
        return 'mountain'
    if is_coastal:
        return 'coastal'
    return 'city'


def _box1_country(L_ip: dict, country_name: str, country_iso: str,
                  lang_local: str, currency_name: str, currency_symbol: str,
                  drive: str, gpi_level: int | None,
                  cost_tier: int | None, gpi_value: float | None = None,
                  cost_value: float | None = None,
                  asset_prefix: str = '') -> str:
    """Box 1 : Pays · {country}. 5 list-items.

    gpi_level: 1-5 (1=très sûr). cost_tier: 1-5 (1=très bon marché).
    Si None, on omet le tier badge mais on garde le label vide (cohérence visuelle).
    """
    flag_html = (f'<img src="{asset_prefix}flags/{country_iso}.png" width="20" height="14" alt="" '
                 f'style="vertical-align:middle;border-radius:2px;margin-right:6px">'
                 if country_iso else '')
    title_tpl = L_ip['box1_title_tpl']
    title = f'{flag_html}{title_tpl.format(country=h(country_name))}'

    drive_lbl = L_ip['drive_left'] if drive == 'left' else L_ip['drive_right']

    safe_label = L_ip.get(f'tier_safe_{gpi_level}', '—') if gpi_level else '—'
    cost_label = L_ip.get(f'tier_cost_{cost_tier}', '—') if cost_tier else '—'

    # i18n des hints GPI / cost
    HINT_GPI = {
        'fr': 'GPI (Global Peace Index) 2024 : {v:.2f}/5 — niveau {l}/5',
        'en': 'GPI (Global Peace Index) 2024: {v:.2f}/5 — level {l}/5',
        'en-us': 'GPI (Global Peace Index) 2024: {v:.2f}/5 — level {l}/5',
        'es': 'GPI (Global Peace Index) 2024: {v:.2f}/5 — nivel {l}/5',
        'de': 'GPI (Global Peace Index) 2024: {v:.2f}/5 — Stufe {l}/5',
    }
    HINT_COST = {
        'fr': 'Numbeo Cost of Living 2026 : {v:.1f} — niveau {l}/5',
        'en': 'Numbeo Cost of Living 2026: {v:.1f} — level {l}/5',
        'en-us': 'Numbeo Cost of Living 2026: {v:.1f} — level {l}/5',
        'es': 'Numbeo Cost of Living 2026: {v:.1f} — nivel {l}/5',
        'de': 'Numbeo Cost of Living 2026: {v:.1f} — Stufe {l}/5',
    }
    lang_h = L_ip.get('_lang', 'fr')
    safe_hint = (HINT_GPI.get(lang_h, HINT_GPI['fr']).format(v=gpi_value, l=gpi_level)
                 if gpi_value and gpi_level else None)
    cost_hint = (HINT_COST.get(lang_h, HINT_COST['fr']).format(v=cost_value, l=cost_tier)
                 if cost_value and cost_tier else None)

    items = [
        _list_item('🗣️', L_ip['lbl_lang'], h(lang_local)),
        _list_item('💶', L_ip['lbl_currency'], f'{h(currency_name)} ({h(currency_symbol)})'),
        _list_item('🚗', L_ip['lbl_drive'], h(drive_lbl)),
        _list_item('🛡️', L_ip['lbl_security'], h(safe_label), hint=safe_hint),
        _list_item('💰', L_ip['lbl_cost'], h(cost_label), hint=cost_hint),
    ]
    return (f'<div class="box"><h3>{title}</h3>'
            f'<div class="list">{"".join(items)}</div></div>')


def _box2_climate(L_ip: dict, climate_type: str, trend_value: float | None,
                  hottest_month: str, hottest_temp: float,
                  coldest_month: str, coldest_temp: float,
                  rainiest_month: str, rainiest_pct: float,
                  slug: str = '', dest_name: str = '',
                  lang: str = 'fr') -> str:
    """Box 2 : Climat. Trend = None ⇒ 'Données indisponibles'."""
    # Pour EN-US: slope en delta °C → delta °F = ×9/5 (sans +32)
    trend_for_display = (trend_value * 9 / 5) if (trend_value is not None and lang == 'en-us') else trend_value

    # Templates tooltip i18n
    HINT_NS = {  # non-significatif
        'fr': 'ERA5 2016-2025 — slope {v:+.2f}{unit}/décennie non significatif sur 10 ans',
        'en': 'ERA5 2016-2025 — slope {v:+.2f}{unit}/decade not significant over 10 years',
        'en-us': 'ERA5 2016-2025 — slope {v:+.2f}{unit}/decade not significant over 10 years',
        'es': 'ERA5 2016-2025 — pendiente {v:+.2f}{unit}/década no significativa en 10 años',
        'de': 'ERA5 2016-2025 — Slope {v:+.2f}{unit}/Jahrzehnt nicht signifikant auf 10 Jahre',
    }
    HINT_TREND = {  # avec slope significatif
        'fr': 'Régression linéaire ERA5 2016-2025 — {n} : {v:+.2f}{unit} par décennie',
        'en': 'ERA5 2016-2025 linear regression — {n}: {v:+.2f}{unit} per decade',
        'en-us': 'ERA5 2016-2025 linear regression — {n}: {v:+.2f}{unit} per decade',
        'es': 'Regresión lineal ERA5 2016-2025 — {n}: {v:+.2f}{unit} por década',
        'de': 'ERA5 2016-2025 lineare Regression — {n}: {v:+.2f}{unit} pro Jahrzehnt',
    }
    unit = '°F' if lang == 'en-us' else '°C'

    if trend_value is None:
        trend_str = L_ip['trend_unavailable']
        trend_hint = None
    elif abs(trend_value) < 0.20:
        # Slope non significatif sur 10 ans
        trend_str = L_ip['trend_stable']
        trend_hint = HINT_NS.get(lang, HINT_NS['fr']).format(v=trend_for_display, unit=unit)
    else:
        trend_str = L_ip['trend_tpl'].format(val=f'{trend_for_display:.2f}')
        trend_hint = HINT_TREND.get(lang, HINT_TREND['fr']).format(
            n=(dest_name or slug), v=trend_for_display, unit=unit)

    HINT_RAINIEST = {
        'fr': 'Probabilité de jour pluvieux la plus haute sur l\'année — données ERA5 10 ans',
        'en': 'Highest probability of rainy day in the year — ERA5 10-year data',
        'en-us': 'Highest probability of rainy day in the year — ERA5 10-year data',
        'es': 'Mayor probabilidad de día lluvioso en el año — datos ERA5 10 años',
        'de': 'Höchste Wahrscheinlichkeit eines Regentags im Jahr — ERA5-Daten 10 Jahre',
    }
    items = [
        _list_item('🌍', L_ip['lbl_climate'], h(climate_type)),
        _list_item('📈', L_ip['lbl_trend'], h(trend_str), hint=trend_hint),
        _list_item('🔥', L_ip['lbl_hottest'], f'{h(hottest_month)} · {_fmt_t(hottest_temp, lang)}'),
        _list_item('❄️', L_ip['lbl_coldest'], f'{h(coldest_month)} · {_fmt_t(coldest_temp, lang)}'),
        _list_item('🌧️', L_ip['lbl_rainiest'],
                   f'{h(rainiest_month)} · {rainiest_pct:.0f}%',
                   hint=HINT_RAINIEST.get(lang, HINT_RAINIEST['fr'])),
    ]
    return (f'<div class="box"><h3>🌡️ {h(L_ip["box2_title"])}</h3>'
            f'<div class="list">{"".join(items)}</div></div>')


def _box3_mountain(L_ip: dict, alt_village: int | None, alt_ski_max: int | None,
                   ski_season: str, hiking_season: str,
                   high_alt_warning: bool = True, lang: str = 'fr') -> str:
    """Box 3 mountain : altitudes, saisons ski/rando, haute montagne."""
    # FIX: convertir m → ft pour EN-US (1 m = 3.28084 ft)
    is_us = (lang == 'en-us')
    unit = 'ft' if is_us else 'm'
    def _alt(v):
        if v is None: return None
        return round(v * 3.28084) if is_us else v
    av, am = _alt(alt_village), _alt(alt_ski_max)
    alt_v = f'{av} {unit}' if av else '—'
    alt_dom = (f'{av} → {am} {unit}' if av and am else '—')
    items = [
        _list_item('⛰️', L_ip['mtn_alt_village'], alt_v),
        _list_item('🎿', L_ip['mtn_ski_domain'], alt_dom),
        _list_item('⛷️', L_ip['mtn_season_ski'], h(ski_season)),
        _list_item('🥾', L_ip['mtn_season_hiking'], h(hiking_season)),
    ]
    if high_alt_warning:
        items.append(
            _list_item('🧗', L_ip['mtn_high_alt'], h(L_ip['mtn_high_alt_value']),
                       hint='Au-delà de 3000 m, un guide est fortement recommandé pour la sécurité')
        )
    return (f'<div class="box"><h3>🏔️ {h(L_ip["box3_mountain"])}</h3>'
            f'<div class="list">{"".join(items)}</div></div>')


def _box3_tropical(L_ip: dict, dry_season: str, wet_season: str,
                   sea_summer: float | None, sea_winter: float | None,
                   has_cyclones: bool, latitude: float = 0,
                   lang: str = 'fr') -> str:
    """Box 3 tropical : saisons sèche/humide, mer, cyclones."""
    lang_h = L_ip.get('_lang', 'fr')
    # i18n hints
    HINT_DRY = {
        'fr': 'Période de moindre pluviosité',
        'en': 'Period of lowest rainfall',
        'en-us': 'Period of lowest rainfall',
        'es': 'Periodo de menor pluviosidad',
        'de': 'Zeit mit geringstem Niederschlag',
    }
    HINT_WET = {
        'fr': 'Mousson — averses souvent courtes en après-midi',
        'en': 'Monsoon — showers often short, in the afternoon',
        'en-us': 'Monsoon — showers often short, in the afternoon',
        'es': 'Monzón — chubascos breves a menudo por la tarde',
        'de': 'Monsun — oft kurze Regenschauer am Nachmittag',
    }
    HINT_CYC_YES = {
        'fr': 'Latitude {lat:.1f}° — zone de formation cyclonique',
        'en': 'Latitude {lat:.1f}° — tropical cyclone formation zone',
        'en-us': 'Latitude {lat:.1f}° — tropical cyclone formation zone',
        'es': 'Latitud {lat:.1f}° — zona de formación de ciclones',
        'de': 'Breitengrad {lat:.1f}° — Entstehungszone tropischer Wirbelstürme',
    }
    HINT_CYC_NO = {
        'fr': 'Zone équatoriale (~{lat:.0f}°) hors zone des cyclones tropicaux',
        'en': 'Equatorial zone (~{lat:.0f}°), outside tropical cyclone belt',
        'en-us': 'Equatorial zone (~{lat:.0f}°), outside tropical cyclone belt',
        'es': 'Zona ecuatorial (~{lat:.0f}°), fuera del cinturón de ciclones',
        'de': 'Äquatoriale Zone (~{lat:.0f}°), außerhalb der Wirbelsturmzone',
    }
    CYC_SEASON = {'fr': 'Saison Nov-Avr', 'en': 'Season Nov-Apr', 'en-us': 'Season Nov-Apr',
                  'es': 'Temporada Nov-Abr', 'de': 'Saison Nov-Apr'}

    items = [
        _list_item('🌞', L_ip['tro_dry_season'], h(dry_season),
                   hint=HINT_DRY.get(lang_h, HINT_DRY['fr'])),
        _list_item('🌧️', L_ip['tro_wet_season'], h(wet_season),
                   hint=HINT_WET.get(lang_h, HINT_WET['fr'])),
    ]
    if sea_summer is not None:
        items.append(_list_item('🌊', L_ip['tro_sea_summer'], f'~{_fmt_t(sea_summer, lang_h)}'))
    if sea_winter is not None:
        items.append(_list_item('🌊', L_ip['tro_sea_winter'], f'~{_fmt_t(sea_winter, lang_h)}'))
    cyclone_val = (CYC_SEASON.get(lang_h, CYC_SEASON['fr']) if has_cyclones else h(L_ip['tro_no_cyclones']))
    cyclone_hint = (HINT_CYC_YES.get(lang_h, HINT_CYC_YES['fr']).format(lat=latitude)
                    if has_cyclones
                    else HINT_CYC_NO.get(lang_h, HINT_CYC_NO['fr']).format(lat=abs(latitude)))
    items.append(_list_item('🌀', L_ip['tro_cyclones'], cyclone_val, hint=cyclone_hint))
    return (f'<div class="box"><h3>🏝️ {h(L_ip["box3_tropical"])}</h3>'
            f'<div class="list">{"".join(items)}</div></div>')


def _box3_polar(L_ip: dict, lat: float, has_geothermal: bool = False) -> str:
    """Box 3 polar : aurores, jour polaire, géothermie, vent."""
    aurora_period = 'Sept → Mars' if lat > 60 else 'Oct → Fév'
    polar_day = '~21h' if lat > 60 else '~19h'
    items = [
        _list_item('🌌', L_ip['pol_aurora'], h(aurora_period),
                   hint=f'Latitude {lat:.0f}°N : zone aurorale active'),
        _list_item('☀️', L_ip['pol_polar_day'], f'Juin ({polar_day})',
                   hint='Soleil de minuit relatif — quasi pas de coucher de soleil'),
    ]
    if has_geothermal:
        items.append(_list_item('🌋', L_ip['pol_geothermal'], 'Geysir, Blue Lagoon'))
    items.append(_list_item('🌬️', L_ip['pol_wind'], h(L_ip['pol_wind_value'])))
    return (f'<div class="box"><h3>🌌 {h(L_ip["box3_polar"])}</h3>'
            f'<div class="list">{"".join(items)}</div></div>')


def _box3_coastal(L_ip: dict, sea_summer: float | None, sea_winter: float | None,
                  high_season: str = 'Juin → Sept',
                  lang: str = 'fr') -> str:
    """Box 3 coastal : mer, saisons, houle."""
    items = [_list_item('📅', L_ip['coa_high_season'], h(high_season))]
    if sea_summer is not None:
        items.append(_list_item('🌊', L_ip['coa_sea_summer'], f'~{_fmt_t(sea_summer, lang)}'))
    if sea_winter is not None:
        items.append(_list_item('🌊', L_ip['coa_sea_winter'], f'~{_fmt_t(sea_winter, lang)}'))
    items.append(_list_item('🏖️', L_ip['coa_waves'], 'Modérée',
                            hint='Houle hivernale — saison automne-hiver plus agitée'))
    return (f'<div class="box"><h3>🏖️ {h(L_ip["box3_coastal"])}</h3>'
            f'<div class="list">{"".join(items)}</div></div>')


def _box3_city(L_ip: dict, high_season: str = 'Juin → Août',
               unesco: str | None = None,
               transport: str = 'Bon',
               visa_text: str | None = None) -> str:
    """Box 3 city : tourisme, UNESCO, transport, visa."""
    visa_text = visa_text or L_ip['city_visa_schengen']
    items = [
        _list_item('📅', L_ip['city_high_season'], h(high_season)),
        _list_item('☔', L_ip['city_indoor_visits'], h(L_ip['city_indoor_value']),
                   hint='Musées, monuments couverts : la météo n\'est pas un bloqueur'),
    ]
    if unesco:
        items.append(_list_item('🏛️', L_ip['city_unesco'], h(unesco)))
    items.append(_list_item('🚇', L_ip['city_transport'], h(transport)))
    items.append(_list_item('🛂', L_ip['city_visa'], h(visa_text)))
    return (f'<div class="box"><h3>🏛️ {h(L_ip["box3_city"])}</h3>'
            f'<div class="list">{"".join(items)}</div></div>')


def render_v6_infos_pratiques(slug: str, lang: str, dest_data: dict, asset_prefix: str = '') -> str:
    """Rend la section <section> Infos pratiques avec Box 3 adaptative.

    Args:
        slug: slug FR
        lang: langue UI
        dest_data: dict avec les clés suivantes (toutes optionnelles sauf country_*) :
            - dest_name: nom affichable (ex: 'Chamonix')
            - country_name: nom pays localisé (ex: 'France')
            - country_iso: code ISO 3166-1 alpha-2 (ex: 'fr')
            - lang_local: langue parlée localement (ex: 'Français')
            - currency_name, currency_symbol
            - drive: 'left' ou 'right'
            - gpi_level (1-5), gpi_value (raw)
            - cost_tier (1-5), cost_value (raw)
            - climate_type: ex 'Tempéré océanique', 'Tropical équatorial'...
            - trend_value: float par décennie ou None
            - hottest_month, hottest_temp, coldest_month, coldest_temp
            - rainiest_month, rainiest_pct
            - is_mountain, is_coastal, is_tropical, is_polar (booléens)
            - profil-specific:
              mountain: alt_village, alt_ski_max, ski_season, hiking_season
              tropical: dry_season, wet_season, sea_summer, sea_winter, has_cyclones, latitude
              polar:    latitude, has_geothermal
              coastal:  sea_summer, sea_winter, high_season
              city:     high_season, unesco, transport, visa_text
    """
    L_ip = _v6_strings(lang)['infos_pratiques']
    L_ip['_lang'] = lang  # pour i18n hints (GPI, cost, tropical)
    d = dest_data

    profile = _detect_profile(
        is_mountain=d.get('is_mountain', False),
        is_coastal=d.get('is_coastal', False),
        is_tropical=d.get('is_tropical', False),
        is_polar=d.get('is_polar', False),
    )

    lead_key = f'lead_{profile}'
    lead = L_ip.get(lead_key, L_ip['lead_city'])

    box1 = _box1_country(L_ip,
        country_name=d.get('country_name', ''),
        country_iso=d.get('country_iso', ''),
        lang_local=d.get('lang_local', ''),
        currency_name=d.get('currency_name', ''),
        currency_symbol=d.get('currency_symbol', ''),
        drive=d.get('drive', 'right'),
        gpi_level=_safe_int(d.get('gpi_level')),
        gpi_value=d.get('gpi_value'),
        cost_tier=_safe_int(d.get('cost_tier')),
        cost_value=d.get('cost_value'),
        asset_prefix=asset_prefix,
    )

    box2 = _box2_climate(L_ip,
        climate_type=d.get('climate_type', '—'),
        trend_value=d.get('trend_value'),
        hottest_month=d.get('hottest_month', '—'),
        hottest_temp=d.get('hottest_temp', 0),
        coldest_month=d.get('coldest_month', '—'),
        coldest_temp=d.get('coldest_temp', 0),
        rainiest_month=d.get('rainiest_month', '—'),
        rainiest_pct=d.get('rainiest_pct', 0),
        slug=slug,
        dest_name=d.get('dest_name', ''),
        lang=lang,
    )

    if profile == 'mountain':
        box3 = _box3_mountain(L_ip,
            alt_village=d.get('alt_village'),
            alt_ski_max=d.get('alt_ski_max'),
            ski_season=d.get('ski_season', 'Déc → Mai'),
            hiking_season=d.get('hiking_season', 'Juin → Sept'),
            high_alt_warning=d.get('high_alt_warning', True),
            lang=lang,
        )
    elif profile == 'tropical':
        box3 = _box3_tropical(L_ip,
            dry_season=d.get('dry_season', '—'),
            wet_season=d.get('wet_season', '—'),
            sea_summer=d.get('sea_summer'),
            sea_winter=d.get('sea_winter'),
            has_cyclones=d.get('has_cyclones', False),
            latitude=d.get('latitude', 0),
            lang=lang,
        )
    elif profile == 'polar':
        box3 = _box3_polar(L_ip,
            lat=d.get('latitude', 64),
            has_geothermal=d.get('has_geothermal', False),
        )
    elif profile == 'coastal':
        box3 = _box3_coastal(L_ip,
            sea_summer=d.get('sea_summer'),
            sea_winter=d.get('sea_winter'),
            high_season=d.get('high_season', 'Juin → Sept'),
            lang=lang,
        )
    else:  # city
        # Default 'transport' i18n: localise selon lang
        transport_default = {'fr': 'Bon', 'en': 'Good', 'en-us': 'Good',
                             'es': 'Bueno', 'de': 'Gut'}.get(lang, 'Bon')
        # Default 'high_season' city i18n
        high_season_default = {'fr': 'Juin → Août', 'en': 'June → August',
                               'en-us': 'June → August', 'es': 'Jun. → Ago.',
                               'de': 'Juni → August'}.get(lang, 'Juin → Août')
        box3 = _box3_city(L_ip,
            high_season=d.get('high_season', high_season_default),
            unesco=d.get('unesco'),
            transport=d.get('transport', transport_default),
            visa_text=d.get('visa_text'),
        )

    return (f'<section><div class="container">'
            f'<div class="section-head">'
            f'<div class="section-kicker">{h(L_ip["kicker"])}</div>'
            f'<h2>{h(L_ip["title"])}</h2>'
            f'<p class="lead">{h(lead)}</p>'
            f'</div>'
            f'<div class="grid-3">{box1}{box2}{box3}</div>'
            f'</div></section>')

def _trend_data(slug: str, lat: float = None, lon: float = None) -> dict | None:
    """Récupère les données trend ERA5 pour un slug.

    Le dataset climate_trend.json a un schéma double :
    - 458 entrées sous clé slug (ex: 'paris', 'bali')
    - 158 entrées sous clé coord 'lat,lon' (ex: '45.75,4.83' pour Lyon)

    Schéma de retour normalisé :
        {'years': [...], 'tmax': [...], 'tmoy': [...], 'tmin': [...], 'cmip6_rate': float?}

    Returns None si pas trouvé.
    """
    path = os.path.join(_LOCALE_DIR, '..', 'data', 'climate_trend.json')
    with open(path, encoding='utf-8') as f:
        d = json.load(f)

    # 1. Try slug key
    if slug in d:
        entry = d[slug]
        if 'years' in entry:
            # Format slug : { years:[...], tmax:[...], tmoy:[...], tmin:[...], cmip6_rate:... }
            return {
                'years': entry['years'],
                'tmax': entry['tmax'],
                'tmoy': entry['tmoy'],
                'tmin': entry['tmin'],
                'cmip6_rate': entry.get('cmip6_rate'),
            }

    # 2. Try coord key
    if lat is not None and lon is not None:
        key = f'{lat:.2f},{lon:.2f}'
        if key in d:
            entry = d[key]
            if 'annual' in entry:
                # Format coord : { annual: { '2016': {tmax, tmin, tmean}, ... } }
                ann = entry['annual']
                years = sorted(int(y) for y in ann.keys())
                return {
                    'years': years,
                    'tmax': [ann[str(y)]['tmax'] for y in years],
                    'tmoy': [ann[str(y)]['tmean'] for y in years],
                    'tmin': [ann[str(y)]['tmin'] for y in years],
                    'cmip6_rate': entry.get('cmip6_trend_per_decade'),
                }

    return None


def _linreg_slope(years: list[int], values: list[float]) -> float:
    """Régression linéaire simple → slope par décennie."""
    n = len(years)
    my = sum(years) / n
    mt = sum(values) / n
    num = sum((years[i] - my) * (values[i] - mt) for i in range(n))
    den = sum((years[i] - my) ** 2 for i in range(n))
    if den == 0:
        return 0.0
    return (num / den) * 10  # par décennie


def render_v6_trend_chart(slug: str, nom: str, lang: str = 'fr',
                          lat: float = None, lon: float = None) -> str:
    """Rend la section <section class="tendance-section"> avec SVG 800×360.

    Style éditorial V6 : palette burgundy (#8b3a3a) / steel-blue (#2c5d80) /
    muted-grey (#9aa1ad) sur fond ivory, font Georgia serif, annotations
    italiques pour pic décennie + slope.

    Args:
        slug: slug FR de la destination
        nom: nom affichable (ex: 'Chamonix')
        lang: langue UI ('fr', 'en', 'en-us', 'es', 'de')
        lat, lon: coordonnées (utilisées en fallback si slug absent du JSON)

    Returns:
        HTML <section> complet. Si pas de données : section avec lead "Données indisponibles".
    """
    L = _v6_strings(lang)['trend']
    nom_h = h(nom)
    title = L['title_tpl'].format(nom=nom_h)

    # Section header (toujours présent même sans data)
    head_html = (f'<section class="tendance-section"><div class="container">'
                 f'<div class="section-head">'
                 f'<div class="section-kicker">{h(L["kicker"])}</div>'
                 f'<h2>{title}</h2>'
                 f'<p class="lead">{h(L["lead"])}</p>'
                 f'</div>')

    data = _trend_data(slug, lat=lat, lon=lon)
    if not data or not data.get('years'):
        # Fallback no-data
        return (head_html
                + f'<div class="card pad"><div class="ct-no-data">{h(L["no_data"])}</div></div>'
                + '</div></section>')

    years = data['years']
    tmax = data['tmax']
    tmoy = data['tmoy']
    tmin = data['tmin']

    # Y-axis : englobe la plage des données avec marge ronde
    y_lo = min(tmin) - 1
    y_hi = max(tmax) + 1
    # Arrondir à entiers pairs pour graduation tous les 2°
    y_lo_int = int(y_lo) - (int(y_lo) % 2)
    y_hi_int = int(y_hi) + (2 - int(y_hi) % 2 if int(y_hi) % 2 else 0)

    # Plot area : viewBox 800x360, marges fixes
    Y_TOP, Y_BOTTOM = 50, 300
    X_LEFT, X_RIGHT = 60, 770

    def y_to_svg(t: float) -> float:
        return Y_TOP + (y_hi_int - t) / (y_hi_int - y_lo_int) * (Y_BOTTOM - Y_TOP)

    def x_to_svg(i: int) -> float:
        return X_LEFT + i * (X_RIGHT - X_LEFT) / (len(years) - 1)

    # Slope
    slope = _linreg_slope(years, tmoy)
    intercept = sum(tmoy) / len(tmoy) - slope / 10 * (sum(years) / len(years))
    y_2016 = (slope / 10) * years[0] + intercept
    y_2025 = (slope / 10) * years[-1] + intercept

    # Pic décennie (max tmax)
    pic_idx = tmax.index(max(tmax))
    pic_x = x_to_svg(pic_idx)
    pic_y = y_to_svg(tmax[pic_idx])

    parts = [
        f'<svg viewBox="0 0 800 360" width="100%" style="display:block;overflow:visible" role="img" '
        f'aria-label="{h(title)} {years[0]}-{years[-1]}">'
    ]

    # Légende inline
    parts.append(
        f'<line x1="60" y1="22" x2="78" y2="22" stroke="#8b3a3a" stroke-width="2.5" stroke-linecap="round"/>'
        f'<text x="84" y="26" font-size="11" fill="#6b7280" font-family="Georgia, serif">{h(L["legend_tmax"])}</text>'
        f'<line x1="140" y1="22" x2="158" y2="22" stroke="#9aa1ad" stroke-width="2.5" stroke-linecap="round"/>'
        f'<text x="164" y="26" font-size="11" fill="#6b7280" font-family="Georgia, serif">{h(L["legend_tmoy"])}</text>'
        f'<line x1="235" y1="22" x2="253" y2="22" stroke="#2c5d80" stroke-width="2.5" stroke-linecap="round"/>'
        f'<text x="259" y="26" font-size="11" fill="#6b7280" font-family="Georgia, serif">{h(L["legend_tmin"])}</text>'
    )

    # Lignes horizontales graduées (tous les 2°)
    for tval in range(y_lo_int, y_hi_int + 1, 2):
        yy = y_to_svg(tval)
        # Pour EN-US, afficher la graduation convertie en °F (delta = ×9/5 + 32 sur les valeurs absolues)
        tval_display = c_to_f(tval) if lang == 'en-us' else tval
        parts.append(
            f'<line x1="60" y1="{yy:.1f}" x2="770" y2="{yy:.1f}" '
            f'stroke="#e8e0d0" stroke-width="1" stroke-dasharray="2 4"/>'
            f'<text x="50" y="{yy + 4:.1f}" text-anchor="end" font-size="11" '
            f'fill="#9aa1ad" font-family="Georgia, serif">{tval_display}°</text>'
        )

    # Trend line gold dashed
    parts.append(
        f'<line x1="{x_to_svg(0):.1f}" y1="{y_to_svg(y_2016):.1f}" '
        f'x2="{x_to_svg(len(years)-1):.1f}" y2="{y_to_svg(y_2025):.1f}" '
        f'stroke="#c9962b" stroke-width="1.2" stroke-dasharray="4 3" opacity="0.55"/>'
    )

    # Série Tmin (steel-blue)
    pts_min = ' '.join(f'{x_to_svg(i):.1f},{y_to_svg(tmin[i]):.1f}' for i in range(len(years)))
    parts.append(
        f'<polyline points="{pts_min}" fill="none" stroke="#2c5d80" stroke-width="2.0" '
        f'stroke-linejoin="round" stroke-linecap="round"/>'
    )
    for i in range(len(years)):
        parts.append(f'<circle cx="{x_to_svg(i):.1f}" cy="{y_to_svg(tmin[i]):.1f}" r="2.5" fill="#2c5d80"/>')

    # Série Tmoy (grey dashed)
    pts_moy = ' '.join(f'{x_to_svg(i):.1f},{y_to_svg(tmoy[i]):.1f}' for i in range(len(years)))
    parts.append(
        f'<polyline points="{pts_moy}" fill="none" stroke="#9aa1ad" stroke-width="1.5" '
        f'stroke-linejoin="round" stroke-linecap="round" stroke-dasharray="4 3"/>'
    )
    for i in range(len(years)):
        parts.append(f'<circle cx="{x_to_svg(i):.1f}" cy="{y_to_svg(tmoy[i]):.1f}" r="2.5" fill="#9aa1ad"/>')

    # Série Tmax (burgundy)
    pts_max = ' '.join(f'{x_to_svg(i):.1f},{y_to_svg(tmax[i]):.1f}' for i in range(len(years)))
    parts.append(
        f'<polyline points="{pts_max}" fill="none" stroke="#8b3a3a" stroke-width="2.2" '
        f'stroke-linejoin="round" stroke-linecap="round"/>'
    )
    for i in range(len(years)):
        parts.append(f'<circle cx="{x_to_svg(i):.1f}" cy="{y_to_svg(tmax[i]):.1f}" r="2.5" fill="#8b3a3a"/>')

    # Labels années
    for i, yr in enumerate(years):
        parts.append(
            f'<text x="{x_to_svg(i):.1f}" y="322" text-anchor="middle" font-size="11" '
            f'fill="#9aa1ad" font-family="Georgia, serif">{yr}</text>'
        )

    # Annotation pic décennie (cercle + texte italique)
    parts.append(
        f'<circle cx="{pic_x:.1f}" cy="{pic_y:.1f}" r="4.5" fill="none" stroke="#8b3a3a" stroke-width="1.5"/>'
    )
    pic_label = L['annot_pic_tpl'].format(
        val=(c_to_f(tmax[pic_idx]) if lang == 'en-us' else tmax[pic_idx]),
        year=years[pic_idx])
    parts.append(
        f'<text x="{pic_x - 8:.1f}" y="{pic_y - 12:.1f}" text-anchor="end" font-size="13" '
        f'fill="#8b3a3a" font-style="italic" font-family="Georgia, serif">{h(pic_label)}</text>'
    )

    # Annotation slope (gold italique, en bas à droite)
    # NB: slope est en delta de température/décennie. Pour EN-US, conversion delta °C → °F = ×9/5 (pas de +32).
    slope_display = (slope * 9 / 5) if lang == 'en-us' else slope
    slope_label = L['annot_slope_tpl'].format(val=f'{slope_display:.2f}')
    parts.append(
        f'<text x="765.0" y="{y_to_svg(y_2025) - 8:.1f}" text-anchor="end" font-size="13" '
        f'fill="#c9962b" font-style="italic" font-family="Georgia, serif">{h(slope_label)}</text>'
    )

    parts.append('</svg>')
    svg = ''.join(parts)

    return (head_html
            + f'<div class="card pad"><div class="ct-chart-wrap">{svg}</div></div>'
            + '</div></section>')


# ─────────────────────────────────────────────────────────────────────────────
# Helper 6 : DECISION CARD (hero shell)
# ─────────────────────────────────────────────────────────────────────────────

def _hero_chip(emoji: str, text: str, color: str = 'blue') -> str:
    """Chip caractéristique climat dans le decision-card.

    color : 'blue' | 'gold' | 'purple' (mapping vers couleurs CSS inline pour V6).
    """
    palettes = {
        'blue':   ('#dbeafe', '#1e40af', '#bfdbfe'),
        'gold':   ('#fef3d0', '#b8860b', '#f2e6a8'),
        'purple': ('#ede9fe', '#6d28d9', '#ddd6fe'),
        'green':  ('#dcfce7', '#166534', '#bbf7d0'),
        'red':    ('#fee2e2', '#991b1b', '#fecaca'),
    }
    bg, fg, br = palettes.get(color, palettes['blue'])
    return (f'<span style="font-size:10.5px;font-weight:700;padding:4px 9px;'
            f'border-radius:999px;background:{bg};color:{fg};border:1px solid {br}">'
            f'{emoji} {h(text)}</span>')


def _coord_label(lat: float, lon: float) -> str:
    """Format coordonnées en notation N/S E/W."""
    ns = 'N' if lat >= 0 else 'S'
    ew = 'E' if lon >= 0 else 'W'
    return f'{abs(lat):.2f}°{ns} · {abs(lon):.2f}°{ew}'


def render_v6_decision_card(slug: str, lang: str, hero_data: dict, asset_prefix: str = '') -> str:
    """Rend la section <header class="hero-wrap"> avec le decision-card.

    Args:
        slug: slug FR
        lang: langue UI
        hero_data: dict avec :
            - dest_name (str)         : ex 'Chamonix'
            - country_name (str)      : ex 'France'
            - country_iso (str)       : ex 'fr'
            - climate_type (str)      : ex 'Climat alpin de montagne'
            - h1_accent_part (str)    : partie italique du h1, ex 'pour skier ou randonner'
            - lead (str)              : phrase HTML autorisée (best/worst déjà formatés)
            - update_month (str)      : ex 'Avril' (i18n côté caller)
            - lat, lon (float)
            - photo_url (str)         : URL Unsplash optionnelle
            - photo_credit (str)      : ex '<a href="...">Photographe</a>' (HTML autorisé)
            - is_mountain (bool)      : si True : layout dual ski/rando
            - decision_main_month (str)  : ex 'Mars · Août'
            - decision_main_score (str)  : ex '9.1'
            - mini_cards: liste de 3 dicts {'value': '⛷️ Mars', 'label': 'Top ski (9.1/10)'}
            - chips: liste de dicts {'emoji': '❄️', 'text': 'Climat alpin', 'color': 'blue'}
    """
    L_dec = _v6_strings(lang)['decision']
    d = hero_data

    nom_h = h(d['dest_name'])
    country_h = h(d.get('country_name', ''))
    climate_h = h(d.get('climate_type', ''))
    iso = d.get('country_iso', '').lower()

    # Background image (optional)
    photo_url = d.get('photo_url', '')
    bg_style = (f' style="background-image:url(\'{h(photo_url)}\')"'
                if photo_url else '')

    # H1 avec accent italique
    h1_full = L_dec['h1_mtn_tpl' if d.get('is_mountain') else 'h1_std_tpl']
    accent_part = h(d.get('h1_accent_part', ''))
    # Insert <span class="accent">{accent}</span> by replacing in template
    # Template format: "{nom} : meilleurs mois <em>pour partir</em>"
    # We replace <em>...</em> with <span class="accent">...</span>
    if '<em>' in h1_full:
        # Build by extracting the em part — we re-inject the dynamic accent
        h1_html = h1_full.format(nom=nom_h)
        h1_html = h1_html.replace('<em>', '<span class="accent">').replace('</em>', '</span>')
    else:
        h1_html = h1_full.format(nom=nom_h)

    lead_html = d.get('lead', '')  # HTML autorisé
    update_lbl = L_dec['tag_update'].format(month=h(d.get('update_month', '—')))
    coords_lbl = _coord_label(d.get('lat', 0), d.get('lon', 0))

    eyebrow = (f'<img src="{asset_prefix}flags/{iso}.png" alt=""/>{nom_h}, {country_h} · {climate_h}'
               if iso and country_h
               else f'{nom_h} · {climate_h}')

    # Mini-grid (3 cards)
    mini_cards = d.get('mini_cards', [])
    mini_html = ''.join(
        f'<div class="mini-card"><div class="v">{h(c["value"])}</div>'
        f'<div class="l">{h(c["label"])}</div></div>'
        for c in mini_cards
    )

    # Chips (3 climat features)
    chips = d.get('chips', [])
    chips_html = ''.join(
        _hero_chip(c.get('emoji', '·'), c.get('text', ''), c.get('color', 'blue'))
        for c in chips
    )
    chips_block = (f'<div style="display:flex;flex-wrap:wrap;gap:6px;margin-top:12px">'
                   f'{chips_html}</div>') if chips_html else ''

    photo_credit = d.get('photo_credit', '')
    photo_credit_block = (f'<div class="hero-photo-credit">Photo par {photo_credit}</div>'
                          if photo_credit else '')

    return (f'<header class="hero-wrap">\n'
            f'  <div class="container">\n'
            f'    <div class="hero-shell"{bg_style}>\n'
            f'      <div class="hero-grid">\n'
            f'        <div class="hero-main">\n'
            f'          <div class="eyebrow">{eyebrow}</div>\n'
            f'          <h1>{h1_html}</h1>\n'
            f'          <p class="hero-lead">{lead_html}</p>\n'
            f'          <div class="hero-meta">\n'
            f'            <span>📅 {h(update_lbl)}</span>\n'
            f'            <span>🛰️ {h(L_dec["tag_data"])}</span>\n'
            f'            <span>📍 {coords_lbl}</span>\n'
            f'          </div>\n'
            f'        </div>\n'
            f'        <div class="hero-side">\n'
            f'          <div class="decision-card">\n'
            f'            <div class="small-label">⚡ {h(L_dec["quick_label"])}</div>\n'
            f'            <div class="decision-top">\n'
            f'              <div>\n'
            f'                <div class="month">{h(d.get("decision_main_month", "—"))}</div>\n'
            f'                <div class="sub">{h(L_dec["quick_sub_mtn" if d.get("is_mountain") else "quick_sub_std"])}</div>\n'
            f'              </div>\n'
            f'              <div class="score">{h(d.get("decision_main_score", "—"))}<small>/10</small></div>\n'
            f'            </div>\n'
            f'            <div class="mini-grid">{mini_html}</div>\n'
            f'            {chips_block}\n'
            f'          </div>\n'
            f'        </div>\n'
            f'      </div>\n'
            f'      {photo_credit_block}\n'
            f'    </div>\n'
            f'  </div>\n'
            f'</header>')


# ─────────────────────────────────────────────────────────────────────────────
# Helper 7 : COMPRENDRE (table 12 mois)
# ─────────────────────────────────────────────────────────────────────────────

def _emoji_for_score(score: float, classe: str = '') -> str:
    """Emoji météo selon le score (proche de scoring.py logic)."""
    if score >= 7.5:
        return '☀️'
    if score >= 6:
        return '⛅'
    if score >= 4:
        return '🌥️'
    return '🌧️'


def _mood_class(classe: str) -> str:
    """Map classe (rec/mid/avoid) → CSS class (good/mid/bad)."""
    return {'rec': 'good', 'mid': 'mid', 'avoid': 'bad'}.get(classe, 'mid')


# ─────────────────────────────────────────────────────────────────────────────
# Helpers pour les 2 cards droite de la section "Comprendre"
# (Lecture rapide + Conditions détaillées)
# ─────────────────────────────────────────────────────────────────────────────

# Labels i18n pour les 2 cards (5 langues)
_COMPREHENSION_I18N = {
    'fr': {
        'lecture_label': '📊 Lecture rapide',
        'window_optimal': 'Fenêtre optimale',
        'good_transition': 'Bonne transition',
        'tough_period': 'Période rude',
        'no_optimal': 'Aucun mois > 7',
        'no_transition': '—',
        'no_tough': 'aucune',
        'conditions_label': '🌡️ Conditions détaillées ({month})',
        'feel': '🌡️ Ressenti',
        'uv': '☀️ UV',
        'humidity': '💧 Humidité ressentie',
        'rain': '☔ Pluie',
        'sun': '🌅 Soleil',
        # Ressenti labels
        'feel_cold': 'Frais', 'feel_cool': 'Tempéré', 'feel_comfortable': 'Confortable',
        'feel_warm': 'Chaud', 'feel_hot': 'Très chaud', 'feel_humid_heat': 'Chaleur humide',
        # UV labels
        'uv_low': 'Faible', 'uv_moderate': 'Modéré', 'uv_moderate_strong': 'Modéré-Fort',
        'uv_strong': 'Fort', 'uv_very_strong': 'Très fort', 'uv_extreme': 'Extrême',
        # Humidité labels
        'hum_dry': 'Sec', 'hum_pleasant': 'Agréable', 'hum_humid': 'Lourd', 'hum_oppressive': 'Étouffant',
        # Format mois "(juillet)"
        'month_lower': True,  # mois en minuscules entre parenthèses
    },
    'en': {
        'lecture_label': '📊 Quick read',
        'window_optimal': 'Optimal window',
        'good_transition': 'Good transition',
        'tough_period': 'Tough period',
        'no_optimal': 'No month > 7',
        'no_transition': '—',
        'no_tough': 'none',
        'conditions_label': '🌡️ Detailed conditions ({month})',
        'feel': '🌡️ Feel',
        'uv': '☀️ UV',
        'humidity': '💧 Humidity feel',
        'rain': '☔ Rain',
        'sun': '🌅 Sunshine',
        'feel_cold': 'Cold', 'feel_cool': 'Cool', 'feel_comfortable': 'Comfortable',
        'feel_warm': 'Warm', 'feel_hot': 'Hot', 'feel_humid_heat': 'Humid heat',
        'uv_low': 'Low', 'uv_moderate': 'Moderate', 'uv_moderate_strong': 'Moderate-Strong',
        'uv_strong': 'Strong', 'uv_very_strong': 'Very strong', 'uv_extreme': 'Extreme',
        'hum_dry': 'Dry', 'hum_pleasant': 'Pleasant', 'hum_humid': 'Humid', 'hum_oppressive': 'Oppressive',
        'month_lower': False,
    },
    'en-us': {
        'lecture_label': '📊 Quick read',
        'window_optimal': 'Optimal window',
        'good_transition': 'Good transition',
        'tough_period': 'Tough period',
        'no_optimal': 'No month > 7',
        'no_transition': '—',
        'no_tough': 'none',
        'conditions_label': '🌡️ Detailed conditions ({month})',
        'feel': '🌡️ Feel',
        'uv': '☀️ UV',
        'humidity': '💧 Humidity feel',
        'rain': '☔ Rain',
        'sun': '🌅 Sunshine',
        'feel_cold': 'Cold', 'feel_cool': 'Cool', 'feel_comfortable': 'Comfortable',
        'feel_warm': 'Warm', 'feel_hot': 'Hot', 'feel_humid_heat': 'Humid heat',
        'uv_low': 'Low', 'uv_moderate': 'Moderate', 'uv_moderate_strong': 'Moderate-Strong',
        'uv_strong': 'Strong', 'uv_very_strong': 'Very strong', 'uv_extreme': 'Extreme',
        'hum_dry': 'Dry', 'hum_pleasant': 'Pleasant', 'hum_humid': 'Humid', 'hum_oppressive': 'Oppressive',
        'month_lower': False,
    },
    'es': {
        'lecture_label': '📊 Lectura rápida',
        'window_optimal': 'Ventana óptima',
        'good_transition': 'Buena transición',
        'tough_period': 'Periodo duro',
        'no_optimal': 'Ningún mes > 7',
        'no_transition': '—',
        'no_tough': 'ninguno',
        'conditions_label': '🌡️ Condiciones detalladas ({month})',
        'feel': '🌡️ Sensación',
        'uv': '☀️ UV',
        'humidity': '💧 Humedad sentida',
        'rain': '☔ Lluvia',
        'sun': '🌅 Sol',
        'feel_cold': 'Frío', 'feel_cool': 'Templado', 'feel_comfortable': 'Confortable',
        'feel_warm': 'Cálido', 'feel_hot': 'Caluroso', 'feel_humid_heat': 'Calor húmedo',
        'uv_low': 'Bajo', 'uv_moderate': 'Moderado', 'uv_moderate_strong': 'Moderado-Fuerte',
        'uv_strong': 'Fuerte', 'uv_very_strong': 'Muy fuerte', 'uv_extreme': 'Extremo',
        'hum_dry': 'Seco', 'hum_pleasant': 'Agradable', 'hum_humid': 'Húmedo', 'hum_oppressive': 'Opresivo',
        'month_lower': False,
    },
    'de': {
        'lecture_label': '📊 Schnellüberblick',
        'window_optimal': 'Optimales Fenster',
        'good_transition': 'Gute Übergangszeit',
        'tough_period': 'Harte Periode',
        'no_optimal': 'Kein Monat > 7',
        'no_transition': '—',
        'no_tough': 'keine',
        'conditions_label': '🌡️ Detaillierte Bedingungen ({month})',
        'feel': '🌡️ Empfinden',
        'uv': '☀️ UV',
        'humidity': '💧 Empfundene Feuchte',
        'rain': '☔ Regen',
        'sun': '🌅 Sonne',
        'feel_cold': 'Kalt', 'feel_cool': 'Kühl', 'feel_comfortable': 'Angenehm',
        'feel_warm': 'Warm', 'feel_hot': 'Heiß', 'feel_humid_heat': 'Feuchte Hitze',
        'uv_low': 'Niedrig', 'uv_moderate': 'Mäßig', 'uv_moderate_strong': 'Mäßig-Stark',
        'uv_strong': 'Stark', 'uv_very_strong': 'Sehr stark', 'uv_extreme': 'Extrem',
        'hum_dry': 'Trocken', 'hum_pleasant': 'Angenehm', 'hum_humid': 'Schwül', 'hum_oppressive': 'Drückend',
        'month_lower': False,
    },
}


def _build_lecture_rapide(months_data: list[dict], lang: str, abbr_list: list[str]) -> dict:
    """Calcule les 3 valeurs de la card 'Lecture rapide'.

    Returns: {'window': 'Avr → Sep', 'transition': 'Oct', 'tough': 'Jan · Déc'}
    """
    L = _COMPREHENSION_I18N.get(lang, _COMPREHENSION_I18N['fr'])

    # Fenêtre optimale : range mois 'rec' consécutifs (le plus long)
    rec_indices = [i for i, m in enumerate(months_data) if m.get('classe') == 'rec']
    if not rec_indices:
        window_str = L['no_optimal']
    else:
        # Trouve la plus longue séquence consécutive
        ranges = []
        start = rec_indices[0]
        prev = start
        for idx in rec_indices[1:]:
            if idx == prev + 1:
                prev = idx
            else:
                ranges.append((start, prev))
                start = idx
                prev = idx
        ranges.append((start, prev))
        # Plus longue range
        longest = max(ranges, key=lambda r: r[1] - r[0])
        if longest[0] == longest[1]:
            window_str = abbr_list[longest[0]]
        else:
            window_str = f'{abbr_list[longest[0]]} → {abbr_list[longest[1]]}'

    # Bonne transition : mois 'mid' adjacent à au moins un 'rec'
    transition_months = []
    n_months = len(months_data)
    if n_months > 0:
        for i, m in enumerate(months_data):
            if m.get('classe') == 'mid':
                prev_cls = months_data[(i - 1) % n_months].get('classe', '')
                next_cls = months_data[(i + 1) % n_months].get('classe', '')
                if 'rec' in (prev_cls, next_cls):
                    transition_months.append(abbr_list[i])
    transition_str = ' · '.join(transition_months) if transition_months else L['no_transition']

    # Période rude : mois 'avoid'
    tough_months = [abbr_list[i] for i, m in enumerate(months_data) if m.get('classe') == 'avoid']
    tough_str = ' · '.join(tough_months) if tough_months else L['no_tough']

    return {'window': window_str, 'transition': transition_str, 'tough': tough_str}


def _feel_label(tmax: float, dew: float, lang: str) -> str:
    """Détermine le label de ressenti thermique selon tmax + dew_point."""
    L = _COMPREHENSION_I18N.get(lang, _COMPREHENSION_I18N['fr'])
    # Chaleur humide : tmax >= 26 + dew >= 22
    if tmax >= 26 and dew >= 22:
        return L['feel_humid_heat']
    if tmax >= 32:
        return L['feel_hot']
    if tmax >= 26:
        return L['feel_warm']
    if tmax >= 18:
        return L['feel_comfortable']
    if tmax >= 10:
        return L['feel_cool']
    return L['feel_cold']


def _uv_label(uv: float, lang: str) -> str:
    """Label UV selon valeur (0-15+)."""
    L = _COMPREHENSION_I18N.get(lang, _COMPREHENSION_I18N['fr'])
    if uv >= 11:
        return L['uv_extreme']
    if uv >= 8:
        return L['uv_very_strong']
    if uv >= 6:
        return L['uv_moderate_strong']
    if uv >= 3:
        return L['uv_moderate']
    return L['uv_low']


def _humidity_label(dew: float, lang: str) -> str:
    """Label humidité ressentie selon dew point (°C)."""
    L = _COMPREHENSION_I18N.get(lang, _COMPREHENSION_I18N['fr'])
    if dew >= 22:
        return L['hum_oppressive']
    if dew >= 18:
        return L['hum_humid']
    if dew >= 13:
        return L['hum_pleasant']
    return L['hum_dry']


def render_v6_comprendre(slug: str, lang: str, months_data: list[dict],
                         monthly_url_tpl: str = '') -> str:
    """Section "Comprendre" : table desktop + cards mobile pour les 12 mois.

    Args:
        slug: slug FR
        lang: langue UI
        months_data: liste de 12 dicts avec :
            - mois (str)             : nom localisé du mois (ex 'Janvier' / 'January')
            - tmin (float)           : °C
            - tmax (float)           : °C
            - rain_pct (float)       : %
            - precip_mm (float)      : mm/j
            - sun_h (float)          : h/jour
            - score_10 (float)       : 0-10
            - classe (str)           : 'rec' | 'mid' | 'avoid'
            - is_best (bool)         : marquage rangée best
        monthly_url_tpl: template URL fiche mensuelle, ex '{slug}-meteo-{mois_short}.html'
            (les variables disponibles : {slug}, {mois_lower}, {mois_short})

    Note: monthly_url_tpl est différent par langue (FR=meteo-, EN=weather-, etc.).
        Le caller doit fournir le bon template.
    """
    L = _v6_strings(lang)['comprendre']
    n_comfortable = sum(1 for m in months_data if m.get('classe') == 'rec')
    comfortable_months = [m['mois'][:3] for m in months_data if m.get('classe') == 'rec']

    comfort_label = L['comfort_tpl'].format(n=n_comfortable)
    months_inline = ' · '.join(comfortable_months)

    # Header tableau
    th_html = ''.join(f'<th>{h(L[k])}</th>' for k in
                      ['th_month', 'th_tmin', 'th_tmax', 'th_rain', 'th_mm', 'th_sun', 'th_score', 'th_reading'])

    mood_label = {'good': h(L['mood_good']), 'mid': h(L['mood_mid']), 'bad': h(L['mood_bad'])}

    # Table desktop rows
    rows_html = []
    for m in months_data:
        # mois_slug : version sans accents pour URL ('Février' → 'fevrier')
        import unicodedata
        mois_slug = ''.join(c for c in unicodedata.normalize('NFD', m['mois'].lower())
                            if unicodedata.category(c) != 'Mn')
        url = monthly_url_tpl.format(slug=slug, mois_lower=mois_slug,
                                     mois_short=mois_slug[:3]) if monthly_url_tpl else '#'
        emoji = _emoji_for_score(m['score_10'], m.get('classe', ''))
        mood_cls = _mood_class(m.get('classe', ''))
        best_attr = ' best' if m.get('is_best') else ''
        rows_html.append(
            f'<tr class="row{best_attr}" onclick="location.href=\'{h(url)}\'" '
            f'style="cursor:pointer" tabindex="0" role="link" '
            f'onkeydown="if(event.key===\'Enter\')location.href=\'{h(url)}\'">'
            f'<td class="month-cell">{emoji} {h(m["mois"])} '
            f'<span style="color:var(--gold);font-weight:700;margin-left:4px">→</span></td>'
            f'<td>{_fmt_t(m["tmin"], lang)}</td>'
            f'<td>{_fmt_t(m["tmax"], lang)}</td>'
            f'<td>{m["rain_pct"]:.0f}%</td>'
            f'<td>{m["precip_mm"]:.1f}mm</td>'
            f'<td>{m["sun_h"]:.1f}h</td>'
            f'<td>{m["score_10"]:.1f}/10</td>'
            f'<td><span class="mood {mood_cls}">{mood_label[mood_cls]}</span></td>'
            f'</tr>'
        )

    # Mobile cards
    mobile_cards = []
    for m in months_data:
        # mois_slug : version sans accents pour URL ('Février' → 'fevrier')
        import unicodedata
        mois_slug = ''.join(c for c in unicodedata.normalize('NFD', m['mois'].lower())
                            if unicodedata.category(c) != 'Mn')
        url = monthly_url_tpl.format(slug=slug, mois_lower=mois_slug,
                                     mois_short=mois_slug[:3]) if monthly_url_tpl else '#'
        emoji = _emoji_for_score(m['score_10'], m.get('classe', ''))
        mood_cls = _mood_class(m.get('classe', ''))
        best_cls = ' best' if m.get('is_best') else ''
        score_cls = 'good' if m['score_10'] >= 7 else ('mid' if m['score_10'] >= 4 else 'bad')
        mobile_cards.append(
            f'<a href="{h(url)}" class="mobile-month-card{best_cls}">'
            f'<div class="head"><div class="name">{emoji} {h(m["mois"])}</div>'
            f'<div class="score {score_cls}">{m["score_10"]:.1f}/10</div></div>'
            f'<div class="rows">'
            f'<div class="row"><span>T°</span><strong>{_fmt_t(m["tmin"], lang)} / {_fmt_t(m["tmax"], lang)}</strong></div>'
            f'<div class="row"><span>{h(L["th_rain"])}</span><strong>{m["rain_pct"]:.0f}%</strong></div>'
            f'<div class="row"><span>{h(L["th_sun"])}</span><strong>{m["sun_h"]:.1f}h</strong></div>'
            f'<div class="row row-mood"><strong class="mood-{mood_cls}">{mood_label[mood_cls]}</strong></div>'
            f'</div></a>'
        )

    # ── Calcul des 2 cards droite (Lecture rapide + Conditions détaillées) ──
    L_comp = _COMPREHENSION_I18N.get(lang, _COMPREHENSION_I18N['fr'])
    abbr_list = _MONTH_ABBR.get(lang, _MONTH_ABBR['fr'])

    lecture = _build_lecture_rapide(months_data, lang, abbr_list)

    # Top mois pour Conditions détaillées
    top_month = max(months_data, key=lambda m: m['score_10'])
    top_name = top_month['mois'].lower() if L_comp.get('month_lower') else top_month['mois']
    conditions_label = L_comp['conditions_label'].format(month=top_name)

    feel_str = _feel_label(top_month['tmax'], top_month.get('dew_point', 0), lang)
    uv = top_month.get('uv_index', 0)
    uv_str = f'{uv:.1f} · {_uv_label(uv, lang)}' if uv > 0 else '—'
    dew = top_month.get('dew_point', 0)
    hum_str = f'{_fmt_t(dew, lang)} · {_humidity_label(dew, lang)}' if dew is not None else '—'
    rain_unit = {'fr': 'mm/j', 'en': 'mm/day', 'en-us': 'mm/day', 'es': 'mm/d', 'de': 'mm/Tag'}.get(lang, 'mm/j')
    rain_str = f'{top_month["rain_pct"]:.0f}% · {top_month["precip_mm"]:.1f} {rain_unit}'
    sun_unit = {'fr': 'h/jour', 'en': 'h/day', 'en-us': 'h/day', 'es': 'h/día', 'de': 'h/Tag'}.get(lang, 'h/day')
    sun_str = f'{top_month["sun_h"]:.1f}{sun_unit}'

    cards_right = (
        f'<div class="card pad">\n'
        f'  <div class="small-label">{h(L_comp["lecture_label"])}</div>\n'
        f'  <div class="signal-list">\n'
        f'    <div class="signal-item"><div class="l">{h(L_comp["window_optimal"])}</div><div class="r">{h(lecture["window"])}</div></div>\n'
        f'    <div class="signal-item"><div class="l">{h(L_comp["good_transition"])}</div><div class="r">{h(lecture["transition"])}</div></div>\n'
        f'    <div class="signal-item"><div class="l">{h(L_comp["tough_period"])}</div><div class="r">{h(lecture["tough"])}</div></div>\n'
        f'  </div>\n'
        f'</div>\n'
        f'<div class="card pad">\n'
        f'  <div class="small-label">{h(conditions_label)}</div>\n'
        f'  <div class="signal-list">\n'
        f'    <div class="signal-item"><div class="l">{h(L_comp["feel"])}</div><div class="r">{h(feel_str)}</div></div>\n'
        f'    <div class="signal-item"><div class="l">{h(L_comp["uv"])}</div><div class="r">{h(uv_str)}</div></div>\n'
        f'    <div class="signal-item"><div class="l">{h(L_comp["humidity"])}</div><div class="r">{h(hum_str)}</div></div>\n'
        f'    <div class="signal-item"><div class="l">{h(L_comp["rain"])}</div><div class="r">{h(rain_str)}</div></div>\n'
        f'    <div class="signal-item"><div class="l">{h(L_comp["sun"])}</div><div class="r">{h(sun_str)}</div></div>\n'
        f'  </div>\n'
        f'</div>'
    )

    return f'''  <section id="tableau">
    <div class="container">
      <div class="section-head">
        <div class="section-kicker">{h(L['kicker'])}</div>
        <h2>{h(L['title'])}</h2>
        <p class="lead">{h(L['lead'])}</p>
      </div>
      <div class="spotlight-grid">
        <div class="card pad">
          <div style="display:inline-flex;align-items:center;gap:8px;padding:6px 12px;background:var(--green-soft);border:1px solid var(--green-border);border-radius:999px;margin-bottom:12px;font-size:12px;font-weight:700;color:var(--green)">
            ✅ <span>{h(comfort_label)}</span>
            <span style="font-size:11px;font-weight:500;color:var(--muted)">{L['comfort_list_tpl'].format(months=h(months_inline))}</span>
          </div>
          <div class="table-wrap">
            <table>
              <thead><tr>{th_html}</tr></thead>
              <tbody>{''.join(rows_html)}</tbody>
            </table>
          </div>
          <div class="mobile-month-cards">
            {''.join(mobile_cards)}
          </div>
        </div>
        <div class="spotlight-side">
          {cards_right}
        </div>
      </div>
    </div>
  </section>'''


# ─────────────────────────────────────────────────────────────────────────────
# Helper 8 : CONTEXTE (édito)
# ─────────────────────────────────────────────────────────────────────────────

def render_v6_contexte(slug: str, lang: str, edito_html: str) -> str:
    """Section "Contexte" : édito de la destination (HTML autorisé).

    Le contenu vient de data/avis_annuel.json (clé '{slug}:{lang}').
    Si pas d'édito pour cette langue, fallback sur FR.
    """
    L = _v6_strings(lang)['contexte']
    return f'''  <section>
    <div class="container">
      <div class="section-head">
        <div class="section-kicker">{h(L['kicker'])}</div>
        <h2>{h(L['title'])}</h2>
      </div>
      <div class="card pad editorial">
        {edito_html}
      </div>
    </div>
  </section>'''


# ─────────────────────────────────────────────────────────────────────────────
# Helper 9 : QUESTIONS (FAQ)
# ─────────────────────────────────────────────────────────────────────────────

def render_v6_questions(slug: str, lang: str, faq_items: list[dict]) -> str:
    """Section "Questions" : FAQ accessible.

    faq_items: liste de dicts {'q': '...', 'a': '...'} (HTML autorisé dans 'a')
    """
    L = _v6_strings(lang)['questions']
    items_html = []
    for it in faq_items:
        items_html.append(
            f'<details class="faq-item">'
            f'<summary>{h(it["q"])}</summary>'
            f'<div class="faq-a">{it["a"]}</div>'
            f'</details>'
        )
    return f'''  <section>
    <div class="container">
      <div class="section-head">
        <div class="section-kicker">{h(L['kicker'])}</div>
        <h2>{h(L['title'])}</h2>
      </div>
      <div class="card pad faq-list">
        {''.join(items_html)}
      </div>
    </div>
  </section>'''


# ─────────────────────────────────────────────────────────────────────────────
# Helper 10 : ADAPTER / EXPLORER / LOCALISATION / RÉSERVER (stubs minimalistes)
# ─────────────────────────────────────────────────────────────────────────────
# Ces sections sont volontairement minimales pour la V1 V6. Elles seront
# enrichies progressivement après validation visuelle du squelette.

def render_v6_adapter(slug: str, lang: str, profile: str = 'city',
                      chips: list[dict] = None) -> str:
    """Section "Adapter" : suggestions selon profil de séjour.

    chips: optionnel, liste {'emoji': '...', 'text': '...', 'color': '...'}.
        Si vide, on génère 3 chips par défaut selon profil.
    """
    L = _v6_strings(lang)['adapter']
    if chips is None:
        # Mapping i18n: 5 profiles × 5 langues × 3 chips
        # Ordre des chips conservé pour cohérence visuelle entre langues
        DEFAULTS_I18N = {
            'mountain': {
                'fr':    [('⛷️', 'Ski : Déc → Mai', 'blue'), ('🥾', 'Rando : Juin → Sept', 'green'), ('🧗', 'Haute mont. : guide', 'gold')],
                'en':    [('⛷️', 'Ski: Dec → May', 'blue'),  ('🥾', 'Hiking: Jun → Sept', 'green'),  ('🧗', 'High mountains: guide', 'gold')],
                'en-us': [('⛷️', 'Ski: Dec → May', 'blue'),  ('🥾', 'Hiking: Jun → Sept', 'green'),  ('🧗', 'High mountains: guide', 'gold')],
                'es':    [('⛷️', 'Esquí: Dic → May', 'blue'),('🥾', 'Senderismo: Jun → Sept', 'green'),('🧗', 'Alta montaña: guía', 'gold')],
                'de':    [('⛷️', 'Ski: Dez → Mai', 'blue'),  ('🥾', 'Wandern: Juni → Sept', 'green'), ('🧗', 'Hochgebirge: Guide', 'gold')],
            },
            'tropical': {
                'fr':    [('🌞', 'Saison sèche', 'gold'),    ('🏖️', 'Plages', 'blue'),    ('🌊', 'Surf', 'green')],
                'en':    [('🌞', 'Dry season', 'gold'),       ('🏖️', 'Beaches', 'blue'),   ('🌊', 'Surf', 'green')],
                'en-us': [('🌞', 'Dry season', 'gold'),       ('🏖️', 'Beaches', 'blue'),   ('🌊', 'Surf', 'green')],
                'es':    [('🌞', 'Temporada seca', 'gold'),  ('🏖️', 'Playas', 'blue'),    ('🌊', 'Surf', 'green')],
                'de':    [('🌞', 'Trockenzeit', 'gold'),     ('🏖️', 'Strände', 'blue'),   ('🌊', 'Surfen', 'green')],
            },
            'polar': {
                'fr':    [('🌌', 'Aurores : Sept → Mars', 'purple'),  ('☀️', 'Jour polaire : juin', 'gold'),  ('🌋', 'Géothermie', 'red')],
                'en':    [('🌌', 'Auroras: Sept → Mar', 'purple'),    ('☀️', 'Polar day: June', 'gold'),       ('🌋', 'Geothermal', 'red')],
                'en-us': [('🌌', 'Auroras: Sept → Mar', 'purple'),    ('☀️', 'Polar day: June', 'gold'),       ('🌋', 'Geothermal', 'red')],
                'es':    [('🌌', 'Auroras: Sept → Mar', 'purple'),    ('☀️', 'Día polar: junio', 'gold'),      ('🌋', 'Geotermia', 'red')],
                'de':    [('🌌', 'Polarlichter: Sept → März', 'purple'),('☀️', 'Polartag: Juni', 'gold'),       ('🌋', 'Geothermie', 'red')],
            },
            'coastal': {
                'fr':    [('🏖️', 'Plages : juin-sept', 'gold'),  ('🌊', 'Houle : sept-mars', 'blue'),  ('🚤', 'Activités nautiques', 'green')],
                'en':    [('🏖️', 'Beaches: Jun-Sept', 'gold'),    ('🌊', 'Swell: Sept-Mar', 'blue'),     ('🚤', 'Water activities', 'green')],
                'en-us': [('🏖️', 'Beaches: Jun-Sept', 'gold'),    ('🌊', 'Swell: Sept-Mar', 'blue'),     ('🚤', 'Water activities', 'green')],
                'es':    [('🏖️', 'Playas: Jun-Sept', 'gold'),     ('🌊', 'Marejada: Sept-Mar', 'blue'),  ('🚤', 'Actividades náuticas', 'green')],
                'de':    [('🏖️', 'Strände: Jun-Sept', 'gold'),    ('🌊', 'Dünung: Sept-März', 'blue'),   ('🚤', 'Wasseraktivitäten', 'green')],
            },
            'city': {
                'fr':    [('🏛️', 'Patrimoine', 'gold'),     ('🍴', 'Gastronomie', 'red'),  ('☔', 'Visites couvertes', 'blue')],
                'en':    [('🏛️', 'Heritage', 'gold'),        ('🍴', 'Gastronomy', 'red'),    ('☔', 'Indoor sights', 'blue')],
                'en-us': [('🏛️', 'Heritage', 'gold'),        ('🍴', 'Gastronomy', 'red'),    ('☔', 'Indoor sights', 'blue')],
                'es':    [('🏛️', 'Patrimonio', 'gold'),      ('🍴', 'Gastronomía', 'red'),   ('☔', 'Visitas cubiertas', 'blue')],
                'de':    [('🏛️', 'Kulturerbe', 'gold'),      ('🍴', 'Gastronomie', 'red'),   ('☔', 'Indoor-Sehensw.', 'blue')],
            },
        }
        profile_chips_i18n = DEFAULTS_I18N.get(profile, DEFAULTS_I18N['city'])
        triplets = profile_chips_i18n.get(lang, profile_chips_i18n['fr'])
        chips = [{'emoji': e, 'text': t, 'color': c} for e, t, c in triplets]

    chips_html = ''.join(_hero_chip(c['emoji'], c['text'], c.get('color', 'blue')) for c in chips)
    return f'''  <section id="par-projet">
    <div class="container">
      <div class="section-head">
        <div class="section-kicker">{h(L['kicker'])}</div>
        <h2>{h(L['title'])}</h2>
        <p class="lead">{h(L['lead'])}</p>
      </div>
      <div class="card pad">
        <div style="display:flex;flex-wrap:wrap;gap:8px">{chips_html}</div>
      </div>
    </div>
  </section>'''


def render_v6_explorer(slug: str, lang: str, related: dict | list = None,
                       asset_prefix: str = '') -> str:
    """Section "Explorer" : 3 boxes (Climat similaire + Proximité + Guides).

    Aligné prototype paris-v6.html.

    Args:
        related: dict {'climate': [...], 'proximity': [...]} OU liste plate (legacy)
                  Items: {href, name, country, country_iso, distance_km?}
    """
    # Compatibilité legacy : si related est une liste plate, la mettre dans 'climate'
    if isinstance(related, list):
        related = {'climate': related, 'proximity': []}
    if not related:
        related = {'climate': [], 'proximity': []}
    if not related.get('climate') and not related.get('proximity'):
        return ''

    # i18n labels
    EXPLORER_I18N = {
        'fr':    {'kicker': 'Explorer', 'title': 'Destinations & guides complémentaires',
                  'lead_tpl': 'Si {dest} ne colle pas à vos dates, voici des alternatives et des guides.',
                  'box_climate': 'Destinations au climat similaire',
                  'box_proximity': 'Destinations proches',
                  'box_guides': 'Guides & classements',
                  'guide_world': 'Classement mondial 2026', 'guide_world_url': 'classement-destinations-meteo-2026.html',
                  'guide_summer': 'Meilleures destinations été', 'guide_summer_url': 'classement-destinations-meteo-ete-2026.html',
                  'guide_winter': 'Soleil hiver', 'guide_winter_url': 'classement-destinations-meteo-hiver-2026.html',
                  'guide_jul': 'Où partir en juillet', 'guide_jul_url': 'ou-partir-en-juillet.html',
                  'see': 'Voir →',
                  'map_btn': '🗺️ Carte climatique des 754 destinations', 'map_url': 'carte.html',
                  },
        'en':    {'kicker': 'Explore', 'title': 'Related destinations & guides',
                  'lead_tpl': "If {dest} doesn't fit your dates, here are alternatives and guides.",
                  'box_climate': 'Similar climate destinations',
                  'box_proximity': 'Nearby destinations',
                  'box_guides': 'Guides & rankings',
                  'guide_world': 'World ranking 2026', 'guide_world_url': 'en/world-weather-ranking-2026.html',
                  'guide_summer': 'Best summer destinations', 'guide_summer_url': 'en/best-summer-destinations-2026.html',
                  'guide_winter': 'Winter sun', 'guide_winter_url': 'en/winter-sun-destinations-2026.html',
                  'guide_jul': 'Where to go in July', 'guide_jul_url': 'en/where-to-go-in-july.html',
                  'see': 'See →',
                  'map_btn': '🗺️ Climate map of 754 destinations', 'map_url': 'en/map.html',
                  },
        'en-us': {'kicker': 'Explore', 'title': 'Related destinations & guides',
                  'lead_tpl': "If {dest} doesn't fit your dates, here are alternatives and guides.",
                  'box_climate': 'Similar climate destinations',
                  'box_proximity': 'Nearby destinations',
                  'box_guides': 'Guides & rankings',
                  'guide_world': 'World ranking 2026', 'guide_world_url': 'us/world-weather-ranking-2026.html',
                  'guide_summer': 'Best summer destinations', 'guide_summer_url': 'us/best-summer-destinations-2026.html',
                  'guide_winter': 'Winter sun', 'guide_winter_url': 'us/winter-sun-destinations-2026.html',
                  'guide_jul': 'Where to go in July', 'guide_jul_url': 'us/where-to-go-in-july.html',
                  'see': 'See →',
                  'map_btn': '🗺️ Climate map of 754 destinations', 'map_url': 'us/map.html',
                  },
        'es':    {'kicker': 'Explorar', 'title': 'Destinos & guías complementarias',
                  'lead_tpl': 'Si {dest} no encaja con sus fechas, aquí hay alternativas y guías.',
                  'box_climate': 'Destinos con clima similar',
                  'box_proximity': 'Destinos cercanos',
                  'box_guides': 'Guías & clasificaciones',
                  'guide_world': 'Clasificación mundial 2026', 'guide_world_url': 'es/clasificacion-clima-mundial-2026.html',
                  'guide_summer': 'Mejores destinos verano', 'guide_summer_url': 'es/mejores-destinos-verano-2026.html',
                  'guide_winter': 'Sol de invierno', 'guide_winter_url': 'es/sol-invierno-destinos-2026.html',
                  'guide_jul': 'Adónde ir en julio', 'guide_jul_url': 'es/adonde-ir-julio.html',
                  'see': 'Ver →',
                  'map_btn': '🗺️ Mapa climático de 754 destinos', 'map_url': 'es/mapa.html',
                  },
        'de':    {'kicker': 'Erkunden', 'title': 'Verwandte Reiseziele & Guides',
                  'lead_tpl': 'Wenn {dest} nicht zu Ihren Daten passt, hier sind Alternativen und Guides.',
                  'box_climate': 'Reiseziele mit ähnlichem Klima',
                  'box_proximity': 'Nahegelegene Reiseziele',
                  'box_guides': 'Guides & Rankings',
                  'guide_world': 'Welt-Ranking 2026', 'guide_world_url': 'de/welt-wetter-ranking-2026.html',
                  'guide_summer': 'Beste Sommerziele', 'guide_summer_url': 'de/beste-sommerziele-2026.html',
                  'guide_winter': 'Wintersonne', 'guide_winter_url': 'de/wintersonne-reiseziele-2026.html',
                  'guide_jul': 'Wohin im Juli', 'guide_jul_url': 'de/wohin-im-juli.html',
                  'see': 'Sehen →',
                  'map_btn': '🗺️ Klimakarte mit 754 Reisezielen', 'map_url': 'de/karte.html',
                  },
    }
    L = EXPLORER_I18N.get(lang, EXPLORER_I18N['fr'])

    # Récupérer le nom localisé depuis le 1er climate ou proximity (fallback slug)
    dest_name = ''
    if related.get('climate'):
        # Nom de la dest courante n'est pas dans related — on doit le passer en param.
        # Workaround simple: on n'utilise pas {dest} dans le lead, on simplifie.
        pass

    # Helper pour rendre un list-item destination
    def _dest_item(item: dict, with_distance: bool = False) -> str:
        flag = (f'<img src="{asset_prefix}flags/{item["country_iso"]}.png" width="18" height="13" alt="" '
                f'loading="lazy" class="list-flag">'
                if item.get('country_iso') else '')
        # FIX EN-US: convertir km → miles (1 km = 0.621371 miles)
        if with_distance and 'distance_km' in item:
            if lang == 'en-us':
                miles = round(item['distance_km'] * 0.621371)
                right = f'{miles} mi →'
            else:
                right = f'{item["distance_km"]} km →'
        else:
            right = '→'
        return (f'<a href="{h(item["href"])}" class="list-item">'
                f'<span>{flag}{h(item["name"])} <span class="list-country">· {h(item["country"])}</span></span>'
                f'<strong>{h(right)}</strong>'
                f'</a>')

    # Box 1 : Climat similaire
    climate_items = ''.join(_dest_item(it) for it in related.get('climate', [])[:4])
    box_climate = (f'<div class="box">\n'
                   f'  <h3>{h(L["box_climate"])}</h3>\n'
                   f'  <div class="list">{climate_items}</div>\n'
                   f'</div>') if climate_items else ''

    # Box 2 : Proximité
    proximity_items = ''.join(_dest_item(it, with_distance=True) for it in related.get('proximity', [])[:4])
    box_proximity = (f'<div class="box">\n'
                     f'  <h3>{h(L["box_proximity"])}</h3>\n'
                     f'  <div class="list">{proximity_items}</div>\n'
                     f'</div>') if proximity_items else ''

    # Box 3 : Guides & classements (statique)
    box_guides = (
        f'<div class="box box-guides">\n'
        f'  <h3>{h(L["box_guides"])}</h3>\n'
        f'  <div class="list">\n'
        f'    <div class="list-item"><span>{h(L["guide_world"])}</span><strong><a href="{h(L["guide_world_url"])}">{h(L["see"])}</a></strong></div>\n'
        f'    <div class="list-item"><span>{h(L["guide_summer"])}</span><strong><a href="{h(L["guide_summer_url"])}">{h(L["see"])}</a></strong></div>\n'
        f'    <div class="list-item"><span>{h(L["guide_winter"])}</span><strong><a href="{h(L["guide_winter_url"])}">{h(L["see"])}</a></strong></div>\n'
        f'    <div class="list-item"><span>{h(L["guide_jul"])}</span><strong><a href="{h(L["guide_jul_url"])}">{h(L["see"])}</a></strong></div>\n'
        f'  </div>\n'
        f'  <div style="margin-top:16px">\n'
        f'    <a class="btn outlined" href="{h(L["map_url"])}">{h(L["map_btn"])}</a>\n'
        f'  </div>\n'
        f'</div>'
    )

    # Lead simplifié sans {dest} (variable difficile à propager ici)
    lead = L['lead_tpl'].replace('{dest}', '')
    lead = lead.replace('  ', ' ').replace(' ne ', ' ne ').strip()
    # FR: "Si  ne colle pas..." → "Si cette destination ne colle pas..."
    # Plus simple : variante générique sans {dest}
    LEAD_GENERIC = {
        'fr': 'Si cette destination ne colle pas à vos dates, voici des alternatives et des guides.',
        'en': "If this destination doesn't fit your dates, here are alternatives and guides.",
        'en-us': "If this destination doesn't fit your dates, here are alternatives and guides.",
        'es': 'Si este destino no encaja con sus fechas, aquí hay alternativas y guías.',
        'de': 'Wenn dieses Reiseziel nicht zu Ihren Daten passt, hier sind Alternativen und Guides.',
    }
    lead = LEAD_GENERIC.get(lang, LEAD_GENERIC['fr'])

    return f'''  <section>
    <div class="container">
      <div class="section-head">
        <div class="section-kicker">{h(L['kicker'])}</div>
        <h2>{h(L['title'])}</h2>
        <p class="lead">{h(lead)}</p>
      </div>
      <div class="grid-3">
        {box_climate}
        {box_proximity}
        {box_guides}
      </div>
    </div>
  </section>'''


def render_v6_localisation(slug: str, lang: str, nom: str,
                           lat: float, lon: float,
                           country_iso: str = '', country_name: str = '',
                           climate_type: str = '',
                           best_month: str = '', best_score: float = 0,
                           worst_month: str = '', worst_score: float = 0,
                           macro_zoom: int = 5,
                           asset_prefix: str = '') -> str:
    """Section "Localisation" : 2 cartes Leaflet (Monde + Contexte) + intro.

    Reproduit la structure du prototype paris-v6.html :
    - Carte 'Monde' : zoom 1 (vue mondiale, point rouge sur dest)
    - Carte 'Contexte' : zoom variable (5 par défaut, vue régionale)
    - Intro : drapeau pays + description (climat + écart score) + coords

    Args:
        slug: slug FR canonique (utilisé pour ids uniques)
        lang: 'fr', 'en', 'en-us', 'es', 'de'
        nom: nom localisé (ex 'Paris', 'Cinque Terre')
        lat, lon: coordonnées GPS
        country_iso: code ISO 2 lettres (fr, gb, us...) pour drapeau
        country_name: nom pays localisé
        climate_type: ex 'Tempéré océanique', 'Alpine climate', etc.
        best_month, best_score: mois meilleur + son score
        worst_month, worst_score: mois pire + son score
        macro_zoom: zoom Leaflet pour la carte 'Contexte' (5 par défaut, plus haut = plus zoom)
    """
    L = _v6_strings(lang)['localisation']
    title = L['title_tpl'].format(nom=h(nom))

    # i18n labels
    LOCAL_I18N = {
        'fr':    {'world': '🌍 Monde', 'context': '🔍 Contexte géographique',
                  'lead': 'Position mondiale + contexte géographique régional.',
                  'desc_tpl': 'Climat {climate} avec un écart {best} → {worst} entre meilleur et pire mois. 10 ans de données ERA5 pour choisir selon votre projet.'},
        'en':    {'world': '🌍 World', 'context': '🔍 Geographic context',
                  'lead': 'Global position + regional geographic context.',
                  'desc_tpl': '{climate} climate with a {best} → {worst} gap between best and worst month. 10 years of ERA5 data to choose by project.'},
        'en-us': {'world': '🌍 World', 'context': '🔍 Geographic context',
                  'lead': 'Global position + regional geographic context.',
                  'desc_tpl': '{climate} climate with a {best} → {worst} gap between best and worst month. 10 years of ERA5 data to choose by project.'},
        'es':    {'world': '🌍 Mundo', 'context': '🔍 Contexto geográfico',
                  'lead': 'Posición mundial + contexto geográfico regional.',
                  'desc_tpl': 'Clima {climate} con una diferencia {best} → {worst} entre el mejor y el peor mes. 10 años de datos ERA5 para elegir según su proyecto.'},
        'de':    {'world': '🌍 Welt', 'context': '🔍 Geografischer Kontext',
                  'lead': 'Globale Position + regionaler geografischer Kontext.',
                  'desc_tpl': '{climate}es Klima mit einer {best} → {worst} Differenz zwischen besten und schlechtesten Monat. 10 Jahre ERA5-Daten zur Auswahl nach Projekt.'},
    }
    L2 = LOCAL_I18N.get(lang, LOCAL_I18N['fr'])

    flag_html = (f'<img src="{asset_prefix}flags/{country_iso}.png" width="16" height="12" alt="" '
                 f'style="vertical-align:middle;border-radius:2px;margin-right:5px">'
                 if country_iso else '')

    desc = L2['desc_tpl'].format(
        climate=h(climate_type) if climate_type else '—',
        best=f'{best_score:.1f}',
        worst=f'{worst_score:.1f}',
    )

    world_id = f'dmap-world-{slug}'
    macro_id = f'dmap-macro-{slug}'

    return f'''  <section class="dest-map-section">
    <div class="container">
      <div class="section-head">
        <div class="section-kicker">{h(L['kicker'])}</div>
        <h2>{title} ?</h2>
        <p class="lead">{h(L2['lead'])}</p>
      </div>
      <div class="dest-map-row" data-dest-map="1" data-lat="{lat:.4f}" data-lon="{lon:.4f}"
           data-macro-zoom="{macro_zoom}" data-world-id="{world_id}" data-macro-id="{macro_id}">
        <div class="dest-map-card">
          <div class="dest-map-lbl">{h(L2['world'])}</div>
          <div id="{world_id}" class="dest-map-el dest-map-el--world"></div>
        </div>
        <div class="dest-map-card">
          <div class="dest-map-lbl">{h(L2['context'])}</div>
          <div id="{macro_id}" class="dest-map-el dest-map-el--macro"></div>
        </div>
      </div>
      <div class="dest-map-intro">
        <div class="dest-map-intro-body">
          <div class="dest-map-country">{flag_html}{h(country_name)}</div>
          <div class="dest-map-hsub">{h(desc)}</div>
          <div class="dest-map-coords">{_coord_label(lat, lon)}</div>
        </div>
      </div>
    </div>
  </section>'''


def render_v6_reserver(slug: str, lang: str, dest_name: str,
                       gyg_partner: str = '2MQKL00',
                       travelpayouts_marker: str = '708106',
                       expedia_camref: str = '1110lB57J') -> str:
    """Section "Réserver" / "Planifier votre séjour" : 3 plan-cards riches +
    widget GetYourGuide embarqué (aligné prototype paris-v6.html).

    Reproduit la structure du prototype:
    - 3 plan-cards avec icon + title + sub + cta (Hébergement / Activités / Vols)
    - Bloc Activités GYG (id=#activites) avec widget GetYourGuide 3 items
    """
    # i18n labels
    RESERVER_I18N = {
        'fr':    {'kicker': 'Réserver', 'title': 'Planifier votre séjour',
                  'lead': 'Hôtels au plus bas hors saison haute, tarifs au plus haut sur les mois confortables. Mi-saisons offrent un bon compromis prix/climat.',
                  'plan_hotel_title': 'Hébergement', 'plan_hotel_sub': 'Hôtels & locations · {dest}',
                  'plan_activity_title': 'Activités', 'plan_activity_sub': 'Excursions, billets, expériences',
                  'plan_flight_title': 'Vols', 'plan_flight_sub': 'Comparateur multi-compagnies',
                  'plan_see': 'Voir ↓', 'expedia_cta': 'Expedia →', 'kiwi_cta': 'Kiwi →',
                  'gyg_h3': '🎟️ Activités & excursions · {dest}',
                  'gyg_sub': 'Sélection GetYourGuide · réservation annulable gratuitement',
                  'gyg_see_all': 'Voir tout →',
                  'affil_note': 'Lien affilié · GetYourGuide',
                  'gyg_locale': 'fr-FR', 'expedia_domain': 'expedia.fr',
                  },
        'en':    {'kicker': 'Book', 'title': 'Plan your trip',
                  'lead': 'Hotels at their lowest outside peak season, highest on comfortable months. Shoulder seasons offer a good price/climate compromise.',
                  'plan_hotel_title': 'Stay', 'plan_hotel_sub': 'Hotels & rentals · {dest}',
                  'plan_activity_title': 'Activities', 'plan_activity_sub': 'Tours, tickets, experiences',
                  'plan_flight_title': 'Flights', 'plan_flight_sub': 'Multi-airline comparator',
                  'plan_see': 'See ↓', 'expedia_cta': 'Expedia →', 'kiwi_cta': 'Kiwi →',
                  'gyg_h3': '🎟️ Activities & tours · {dest}',
                  'gyg_sub': 'GetYourGuide selection · free cancellation',
                  'gyg_see_all': 'See all →',
                  'affil_note': 'Affiliate link · GetYourGuide',
                  'gyg_locale': 'en-GB', 'expedia_domain': 'expedia.co.uk',
                  },
        'en-us': {'kicker': 'Book', 'title': 'Plan your trip',
                  'lead': 'Hotels at their lowest outside peak season, highest on comfortable months. Shoulder seasons offer a good price/climate compromise.',
                  'plan_hotel_title': 'Stay', 'plan_hotel_sub': 'Hotels & rentals · {dest}',
                  'plan_activity_title': 'Activities', 'plan_activity_sub': 'Tours, tickets, experiences',
                  'plan_flight_title': 'Flights', 'plan_flight_sub': 'Multi-airline comparator',
                  'plan_see': 'See ↓', 'expedia_cta': 'Expedia →', 'kiwi_cta': 'Kiwi →',
                  'gyg_h3': '🎟️ Activities & tours · {dest}',
                  'gyg_sub': 'GetYourGuide selection · free cancellation',
                  'gyg_see_all': 'See all →',
                  'affil_note': 'Affiliate link · GetYourGuide',
                  'gyg_locale': 'en-US', 'expedia_domain': 'expedia.com',
                  },
        'es':    {'kicker': 'Reservar', 'title': 'Planificar su viaje',
                  'lead': 'Hoteles más baratos fuera de temporada alta, más caros en los meses cómodos. Las medias temporadas ofrecen un buen compromiso precio/clima.',
                  'plan_hotel_title': 'Alojamiento', 'plan_hotel_sub': 'Hoteles y apartamentos · {dest}',
                  'plan_activity_title': 'Actividades', 'plan_activity_sub': 'Excursiones, entradas, experiencias',
                  'plan_flight_title': 'Vuelos', 'plan_flight_sub': 'Comparador multi-aerolíneas',
                  'plan_see': 'Ver ↓', 'expedia_cta': 'Expedia →', 'kiwi_cta': 'Kiwi →',
                  'gyg_h3': '🎟️ Actividades y excursiones · {dest}',
                  'gyg_sub': 'Selección GetYourGuide · cancelación gratuita',
                  'gyg_see_all': 'Ver todo →',
                  'affil_note': 'Enlace afiliado · GetYourGuide',
                  'gyg_locale': 'es-ES', 'expedia_domain': 'expedia.es',
                  },
        'de':    {'kicker': 'Buchen', 'title': 'Reise planen',
                  'lead': 'Hotels am günstigsten außerhalb der Hochsaison, am teuersten in den angenehmen Monaten. Zwischensaisons bieten einen guten Preis/Klima-Kompromiss.',
                  'plan_hotel_title': 'Unterkunft', 'plan_hotel_sub': 'Hotels & Vermietungen · {dest}',
                  'plan_activity_title': 'Aktivitäten', 'plan_activity_sub': 'Touren, Tickets, Erlebnisse',
                  'plan_flight_title': 'Flüge', 'plan_flight_sub': 'Multi-Airline-Vergleich',
                  'plan_see': 'Sehen ↓', 'expedia_cta': 'Expedia →', 'kiwi_cta': 'Kiwi →',
                  'gyg_h3': '🎟️ Aktivitäten & Touren · {dest}',
                  'gyg_sub': 'GetYourGuide-Auswahl · kostenlose Stornierung',
                  'gyg_see_all': 'Alle ansehen →',
                  'affil_note': 'Affiliate-Link · GetYourGuide',
                  'gyg_locale': 'de-DE', 'expedia_domain': 'expedia.de',
                  },
    }
    L = RESERVER_I18N.get(lang, RESERVER_I18N['fr'])
    nom_q = h(dest_name)

    # URLs affiliés
    expedia_url = (f'https://www.{L["expedia_domain"]}/Hotel-Search?destination={nom_q}'
                   f'&camref={expedia_camref}')
    kiwi_url = f'https://www.kiwi.com/deep?affilid={travelpayouts_marker}&to={nom_q}&lang={lang[:2]}'
    gyg_search_url = (f'https://www.getyourguide.com/s/?q={nom_q}'
                      f'&partner_id={gyg_partner}&locale={L["gyg_locale"]}')
    gyg_widget_q = f'{nom_q}'  # GYG widget query

    return f'''  <section id="planifier" style="scroll-margin-top:120px">
    <div class="container">
      <div class="section-head">
        <div class="section-kicker">{h(L['kicker'])}</div>
        <h2>{h(L['title'])}</h2>
        <p class="lead">{h(L['lead'])}</p>
      </div>
      <div class="grid-3 plan-row">
        <a href="{h(expedia_url)}" target="_blank" rel="sponsored noopener" class="plan-card">
          <div class="plan-icon">🏨</div>
          <div class="plan-body">
            <div class="plan-title">{h(L['plan_hotel_title'])}</div>
            <div class="plan-sub">{h(L['plan_hotel_sub'].format(dest=nom_q))}</div>
          </div>
          <div class="plan-cta">{h(L['expedia_cta'])}</div>
        </a>
        <a href="#activites" class="plan-card">
          <div class="plan-icon">🎟️</div>
          <div class="plan-body">
            <div class="plan-title">{h(L['plan_activity_title'])}</div>
            <div class="plan-sub">{h(L['plan_activity_sub'])}</div>
          </div>
          <div class="plan-cta">{h(L['plan_see'])}</div>
        </a>
        <a href="{h(kiwi_url)}" target="_blank" rel="sponsored noopener" class="plan-card">
          <div class="plan-icon">✈️</div>
          <div class="plan-body">
            <div class="plan-title">{h(L['plan_flight_title'])}</div>
            <div class="plan-sub">{h(L['plan_flight_sub'])}</div>
          </div>
          <div class="plan-cta">{h(L['kiwi_cta'])}</div>
        </a>
      </div>

      <div id="activites" class="card pad" style="margin-top:20px;scroll-margin-top:120px">
        <div style="display:flex;justify-content:space-between;align-items:baseline;gap:12px;margin-bottom:14px;flex-wrap:wrap">
          <div>
            <h3 style="margin:0 0 4px">{h(L['gyg_h3'].format(dest=nom_q))}</h3>
            <p style="margin:0;color:var(--muted);font-size:.9rem">{h(L['gyg_sub'])}</p>
          </div>
          <a class="btn primary" style="padding:10px 18px" href="{h(gyg_search_url)}" target="_blank" rel="sponsored noopener">{h(L['gyg_see_all'])}</a>
        </div>
        <div data-gyg-href="https://widget.getyourguide.com/default/activities.frame"
             data-gyg-locale-code="{h(L['gyg_locale'])}"
             data-gyg-widget="activities"
             data-gyg-number-of-items="3"
             data-gyg-partner-id="{h(gyg_partner)}"
             data-gyg-q="{h(gyg_widget_q)}">
        </div>
        <span class="affil-note" style="text-align:right;display:block;margin-top:10px;font-size:11px;color:var(--muted)">{h(L['affil_note'])}</span>
      </div>
    </div>
  </section>'''


# ─────────────────────────────────────────────────────────────────────────────
# ORCHESTRATEUR : render_v6_full_page()
# ─────────────────────────────────────────────────────────────────────────────
# Assemble tous les helpers en une page HTML complète, prête à écrire sur disque.
# Cet orchestrateur reste volontairement focalisé sur le contenu/structure :
# l'extraction des données depuis CSV/JSON est faite côté generate_pages.py
# (dans gen_annual_v6() à venir) qui prépare un dict 'page_data' complet.

# Note: les SEO meta (title, description, canonical, hreflang, JSON-LD) sont
# laissés au caller pour rester découplé. Cet orchestrateur ne touche pas au
# <head>.

def render_v6_head(lang: str, page_title: str, page_desc: str,
                   canonical_url: str = '',
                   asset_prefix: str = '',
                   bg_image_url: str = '',
                   hreflang_tags: str = '',
                   og_image_url: str = '',
                   json_ld_blocks: list[str] = None) -> str:
    """Rend le <head> V6 avec SEO complet.

    Args:
        lang: 'fr', 'en', 'en-us', 'es', 'de'
        page_title: <title>
        page_desc: meta description (limitée à ~160 chars idéalement)
        canonical_url: URL canonique absolue
        asset_prefix: préfixe URL assets (vide si racine, '../' si sous-dossier)
        bg_image_url: si fourni, ajoute un preload pour LCP optimisation
        hreflang_tags: HTML des balises <link rel="alternate" hreflang="...">
            préfabriqué par build_hreflang_tags() — laissé externe pour
            ne pas dépendre de page_config dans v6.py
        og_image_url: URL image og (1200x630). Si vide, utilise bg_image_url.
        json_ld_blocks: liste de strings JSON-LD à injecter (Article, FAQPage, ...)
    """
    html_lang = {'fr': 'fr', 'en': 'en', 'en-us': 'en-US', 'es': 'es', 'de': 'de'}.get(lang, 'fr')
    canonical_html = (f'<link rel="canonical" href="{h(canonical_url)}"/>'
                      if canonical_url else '')
    preload_bg = (f'<link rel="preload" as="image" href="{h(bg_image_url)}" fetchpriority="high">'
                  if bg_image_url else '')

    # OpenGraph minimal
    og_image = og_image_url or bg_image_url or ''
    og_html = ''
    if og_image or canonical_url:
        og_parts = []
        og_parts.append(f'<meta property="og:title" content="{h(page_title)}"/>')
        og_parts.append(f'<meta property="og:description" content="{h(page_desc)}"/>')
        og_parts.append(f'<meta property="og:type" content="article"/>')
        if canonical_url:
            og_parts.append(f'<meta property="og:url" content="{h(canonical_url)}"/>')
        if og_image:
            og_parts.append(f'<meta property="og:image" content="{h(og_image)}"/>')
        og_parts.append(f'<meta name="twitter:card" content="summary_large_image"/>')
        og_html = '\n'.join(og_parts)

    # JSON-LD
    json_ld_html = ''
    if json_ld_blocks:
        json_ld_html = '\n'.join(
            f'<script type="application/ld+json">{block}</script>'
            for block in json_ld_blocks
        )

    return f'''<!doctype html>
<html lang="{html_lang}">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>{h(page_title)}</title>
<meta name="description" content="{h(page_desc)}"/>
{canonical_html}
{hreflang_tags}
{og_html}
{preload_bg}
<link rel="preconnect" href="https://images.unsplash.com" crossorigin>
<link rel="stylesheet" href="{asset_prefix}css/v6.css?v=20"/>
{json_ld_html}
</head>
<body>'''


def render_v6_scripts(asset_prefix: str = '') -> str:
    """Scripts à charger en fin de body.

    Inclut Leaflet (CSS + JS) pour la carte de localisation, sinon L est undefined
    et la carte reste vide (bug visible 2026-05-09 sur staging).
    """
    return f'''<link rel="stylesheet" href="{asset_prefix}vendor/leaflet/leaflet.min.css">
<script src="{asset_prefix}vendor/leaflet/leaflet.min.js"></script>
<script async defer src="https://widget.getyourguide.com/dist/pa.umd.production.min.js" data-gyg-partner-id="2MQKL00"></script>
<script src="{asset_prefix}js/favs.min.js?v=1"></script>
<script src="{asset_prefix}js/share.js"></script>
<script>
// Init 2 cartes Leaflet (Monde + Contexte) - aligné prototype paris-v6.html
(function(){{
  function initOne(row) {{
    var lat = parseFloat(row.dataset.lat);
    var lon = parseFloat(row.dataset.lon);
    var mz = parseInt(row.dataset.macroZoom) || 5;
    var welEl = document.getElementById(row.dataset.worldId);
    var meEl = document.getElementById(row.dataset.macroId);
    if (!welEl || !meEl) return;
    if (welEl._map) return;  // déjà initialisé
    try {{
      // Pin custom (divIcon) pour éviter le bug marker-icon.png par défaut
      var pinHtml = '<div style="width:10px;height:10px;background:#e44;border-radius:50%;border:2px solid white;box-shadow:0 1px 3px rgba(0,0,0,0.4)"></div>';
      var pin = L.divIcon({{html: pinHtml, iconSize:[10,10], iconAnchor:[5,5], className:''}});
      var tileUrl = 'https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png';
      // Carte Monde : zoom 1, statique, sans contrôles ni attribution
      var mw = L.map(welEl.id, {{zoomControl:false, scrollWheelZoom:false, doubleClickZoom:false, dragging:false, attributionControl:false}}).setView([lat, lon], 1);
      L.tileLayer(tileUrl, {{maxZoom:18}}).addTo(mw);
      L.marker([lat, lon], {{icon:pin, interactive:false}}).addTo(mw);
      welEl._map = mw;
      // Carte Contexte : zoom variable, statique, avec attribution OSM
      var mm = L.map(meEl.id, {{zoomControl:false, scrollWheelZoom:false, doubleClickZoom:false, dragging:false, attributionControl:true}}).setView([lat, lon], mz);
      L.tileLayer(tileUrl, {{attribution:'OSM', maxZoom:18}}).addTo(mm);
      L.marker([lat, lon], {{icon:pin, interactive:false}}).addTo(mm);
      meEl._map = mm;
      mm.attributionControl.setPrefix(false);
      // Force invalidateSize après tick pour rendu correct des tiles
      setTimeout(function(){{ mw.invalidateSize(); mm.invalidateSize(); }}, 100);
    }} catch(e) {{}}
  }}
  function initAll(retries) {{
    retries = retries || 0;
    if (!window.L) {{
      if (retries > 50) return;
      setTimeout(function(){{ initAll(retries + 1); }}, 100);
      return;
    }}
    document.querySelectorAll('[data-dest-map]').forEach(initOne);
  }}
  if (document.readyState === 'loading') {{
    document.addEventListener('DOMContentLoaded', function(){{ initAll(0); }});
  }} else {{
    initAll(0);
  }}
}})();
</script>
</body>
</html>'''


def render_v6_full_page(page_data: dict) -> str:
    """Orchestrateur principal : assemble une page V6 complète.

    Args:
        page_data: dict structuré avec toutes les données nécessaires :
            # SEO + head
            - lang (str, requis)
            - page_title (str, requis)
            - page_desc (str, requis)
            - canonical_url (str)
            - asset_prefix (str, défaut '')

            # Identité
            - slug (str, requis)
            - slug_en, slug_es, slug_de (str)  - pour les liens footer
            - dest_name (str, requis)

            # Sections (toutes les clés que les helpers attendent)
            - hero_data (dict)            - pour render_v6_decision_card
            - months_data (list)          - pour render_v6_comprendre
            - monthly_url_tpl (str)       - template URL fiches mensuelles
            - edito_html (str)            - pour render_v6_contexte
            - faq_items (list)            - pour render_v6_questions
            - infos_pratiques_data (dict) - pour render_v6_infos_pratiques
            - profile (str)               - pour render_v6_adapter
            - related (list)              - pour render_v6_explorer
            - lat, lon (float)            - pour render_v6_localisation
            - is_mountain (bool)          - pour méthodologie

    Returns:
        HTML complet de la page (string).
    """
    d = page_data
    lang = d['lang']
    slug = d['slug']
    asset_prefix = d.get('asset_prefix', '')

    head = render_v6_head(
        lang=lang,
        page_title=d['page_title'],
        page_desc=d['page_desc'],
        canonical_url=d.get('canonical_url', ''),
        asset_prefix=asset_prefix,
        bg_image_url=d.get('hero_data', {}).get('photo_url', ''),
        hreflang_tags=d.get('hreflang_tags', ''),
        og_image_url=d.get('og_image_url', ''),
        json_ld_blocks=d.get('json_ld_blocks', []),
    )

    topbar = render_v6_topbar(slug, lang)
    hero = render_v6_decision_card(slug, lang, d['hero_data'], asset_prefix=asset_prefix)

    # FIX 2026-05-06: section #decider (verdict + avis Gilles + pills + bars)
    # remplace l'ancienne method_section autonome (qui était un workaround V1)
    # car la méthodologie est maintenant compactée dans le right-stack du decider.
    decider = render_v6_decider(
        slug=slug, lang=lang, dest_name=d['dest_name'],
        months_data=d['months_data'],
        editorial_html=d.get('edito_html', '<p>—</p>'),
        is_mountain=d.get('is_mountain', False),
    )

    comprendre = render_v6_comprendre(
        slug=slug, lang=lang,
        months_data=d['months_data'],
        monthly_url_tpl=d.get('monthly_url_tpl', ''),
    )

    trend = render_v6_trend_chart(
        slug=slug, nom=d['dest_name'], lang=lang,
        lat=d.get('lat'), lon=d.get('lon'),
    )

    contexte = render_v6_contexte(slug, lang, d.get('edito_html', '<p>—</p>'))

    adapter = render_v6_adapter(slug, lang, profile=d.get('profile', 'city'))

    reserver = render_v6_reserver(slug, lang, d['dest_name'])

    infos = render_v6_infos_pratiques(slug, lang, d['infos_pratiques_data'], asset_prefix=asset_prefix)

    explorer = render_v6_explorer(slug, lang, related=d.get('related', []),
                                   asset_prefix=asset_prefix)

    # Best/worst depuis months_data
    sorted_m = sorted(d['months_data'], key=lambda m: -m['score_10'])
    best_m = sorted_m[0] if sorted_m else {}
    worst_m = sorted_m[-1] if sorted_m else {}

    localisation = render_v6_localisation(
        slug=slug, lang=lang, nom=d['dest_name'],
        lat=d.get('lat', 0), lon=d.get('lon', 0),
        country_iso=d.get('country_iso', ''),
        country_name=d.get('country_name', ''),
        climate_type=d.get('climate_type', d.get('hero_data', {}).get('climate_type', '')),
        best_month=best_m.get('mois', ''),
        best_score=best_m.get('score_10', 0),
        worst_month=worst_m.get('mois', ''),
        worst_score=worst_m.get('score_10', 0),
        macro_zoom=d.get('macro_zoom', 5),
        asset_prefix=asset_prefix,
    )

    questions = render_v6_questions(slug, lang, d.get('faq_items', []))

    footer = render_v6_footer(
        slug_fr=d.get('slug_fr', slug) if lang != 'fr' else slug,
        lang=lang,
        slug_en=d.get('slug_en', ''),
        slug_es=d.get('slug_es', ''),
        slug_de=d.get('slug_de', ''),
        asset_prefix=asset_prefix,
    )

    scripts = render_v6_scripts(asset_prefix=asset_prefix)

    body = f'''{topbar}
{hero}
<main>
{decider}
{comprendre}
{trend}
{adapter}
{reserver}
{infos}
{explorer}
{localisation}
{questions}
</main>
{footer}'''

    return head + '\n' + body + '\n' + scripts
