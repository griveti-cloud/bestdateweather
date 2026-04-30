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
    """
    slugs = {'fr': slug_fr, 'en': slug_en, 'en-us': slug_en, 'es': slug_es, 'de': slug_de}
    out = []
    for lang in ('en', 'en-us', 'es', 'de', 'fr'):
        if lang == current_lang:
            continue
        s = slugs.get(lang) or slug_fr
        cfg = _LANG_URL_PREFIX[lang]
        href = cfg['prefix'] + cfg['tpl'].format(slug=s)
        flag, label = _LANG_FLAGS[lang]
        out.append((href, flag, label))
    return out


def render_v6_footer(slug_fr: str, lang: str = 'fr',
                     slug_en: str = '', slug_es: str = '', slug_de: str = '') -> str:
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
            f'<a href="{h(href)}"><img src="flags/{flag}" width="20" height="15" alt="" loading="lazy"> {h(label)}</a>'
        )
    lang_html = '<span class="sep">·</span>'.join(lang_html_parts)

    # Liens internes (méthodologie/FAQ/etc.) - utilisent les noms i18n des pages
    # Pour FR : pages s'appellent methodologie.html / a-propos.html / faq.html / index.html / widgets.html
    # Pour autres langues : variantes traduites (à compléter ultérieurement)
    if lang == 'fr':
        m_url, a_url, faq_url, app_url, w_url = 'methodologie.html', 'a-propos.html', 'faq.html', 'index.html', 'widgets.html'
        ml_url, p_url, c_url = 'mentions-legales.html', 'confidentialite.html', 'contact.html'
    elif lang == 'en':
        m_url, a_url, faq_url, app_url, w_url = 'en/methodology.html', 'en/about.html', 'en/faq.html', 'en/index.html', 'en/widgets.html'
        ml_url, p_url, c_url = 'en/legal.html', 'en/privacy.html', 'en/contact.html'
    elif lang == 'en-us':
        m_url, a_url, faq_url, app_url, w_url = 'us/methodology.html', 'us/about.html', 'us/faq.html', 'us/index.html', 'us/widgets.html'
        ml_url, p_url, c_url = 'us/legal.html', 'us/privacy.html', 'us/contact.html'
    elif lang == 'es':
        m_url, a_url, faq_url, app_url, w_url = 'es/metodologia.html', 'es/acerca.html', 'es/faq.html', 'es/index.html', 'es/widgets.html'
        ml_url, p_url, c_url = 'es/aviso-legal.html', 'es/privacidad.html', 'es/contacto.html'
    elif lang == 'de':
        m_url, a_url, faq_url, app_url, w_url = 'de/methodologie.html', 'de/ueber.html', 'de/faq.html', 'de/index.html', 'de/widgets.html'
        ml_url, p_url, c_url = 'de/impressum.html', 'de/datenschutz.html', 'de/kontakt.html'
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
  <p class="method-mini-foot"><strong>{h(L['source'])} :</strong> {h(L['source_text'])} · <a href="methodologie.html">{h(L['full_link'])}</a></p>
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
  <p class="method-mini-foot"><strong>{h(L['source'])} :</strong> {h(L['source_text'])} · <a href="methodologie.html">{h(L['full_link'])}</a></p>
</div>'''
