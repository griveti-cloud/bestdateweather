"""
E-E-A-T (Experience, Expertise, Authoritativeness, Trustworthiness) — Bloc Avis Gilles.

Insère un bloc "Avis du fondateur" sur les pages annuelles avec :
- Avatar "G" stylisé (gradient gold)
- Label "L'avis de Gilles" / "Gilles' view" / etc. par langue
- Sub-label "Fondateur · BestDateWeather"
- Paragraphe édito rédigé manuellement (3,770 textes uniques dans avis_annuel.json)
- Lien vers la page "À propos" (renforce signal authorship)

Objectif SEO : signal d'authority / authorship contre la classification
"commodity content" / "scaled content" du Google March 2026 Core Update.

CSS inline (pas de cascade depuis style.css) — évite les pb cache.
"""

import json
import os
from typing import Optional

_AVIS_CACHE: Optional[dict] = None


def _load_avis() -> dict:
    """Charge data/avis_annuel.json en cache."""
    global _AVIS_CACHE
    if _AVIS_CACHE is None:
        path = os.path.join(os.path.dirname(__file__), '..', 'data', 'avis_annuel.json')
        with open(path, encoding='utf-8') as f:
            _AVIS_CACHE = json.load(f)
    return _AVIS_CACHE


# Labels i18n + path vers about par langue
_LABELS = {
    'fr':    {'label': "L'avis de Gilles",  'role': "Fondateur · BestDateWeather",
              'section_label': "Avis du fondateur",
              'about_link': "À propos de Gilles →",  'about_path': 'a-propos.html'},
    'en':    {'label': "Gilles' view",      'role': "Founder · BestDateWeather",
              'section_label': "Founder's view",
              'about_link': "About the founder →", 'about_path': 'en/about.html'},
    'en-us': {'label': "Gilles' view",      'role': "Founder · BestDateWeather",
              'section_label': "Founder's view",
              'about_link': "About the founder →", 'about_path': 'us/about.html'},
    'es':    {'label': "La opinión de Gilles", 'role': "Fundador · BestDateWeather",
              'section_label': "Opinión del fundador",
              'about_link': "Sobre el fundador →",  'about_path': 'es/sobre-nosotros.html'},
    'de':    {'label': "Gilles' Meinung",   'role': "Gründer · BestDateWeather",
              'section_label': "Meinung des Gründers",
              'about_link': "Über den Gründer →",  'about_path': 'de/ueber-uns.html'},
}

# CSS inline (hex pur, pas de var CSS — Lighthouse ne résout pas les vars)
_STYLE_CARD   = 'padding:18px 20px;background:#fff;border:1px solid #e6e8eb;border-radius:14px;border-left:3px solid #1a2230;margin:0'
_STYLE_HEAD   = 'display:flex;align-items:center;gap:10px;margin-bottom:10px'
_STYLE_AVATAR = ('width:36px;height:36px;border-radius:50%;'
                 'background:linear-gradient(135deg,#f5d060,#b8860b);'
                 'display:flex;align-items:center;justify-content:center;'
                 'color:#fff;font-weight:900;font-size:17px;flex-shrink:0;'
                 "font-family:'Playfair Display',Georgia,serif")
_STYLE_META   = 'display:flex;flex-direction:column;gap:1px;min-width:0'
_STYLE_LABEL  = 'font-size:13px;font-weight:700;color:#1a2230;line-height:1.2'
_STYLE_ROLE   = 'font-size:11px;color:#6b7280;line-height:1.3'
_STYLE_EDITO  = 'margin:10px 0 12px;font-size:14px;line-height:1.6;color:#1a2230'
_STYLE_AUTHOR_LINK = ('display:inline-block;font-size:12px;font-weight:600;'
                      'color:#b8860b;text-decoration:none;border-bottom:1px solid #f5d060;padding-bottom:1px')


def eeat_avis_section_html(slug_fr: str, lang: str = 'fr', asset_prefix: str = '') -> str:
    """Retourne le HTML d'une <section> contenant le bloc avis Gilles.

    Args:
        slug_fr: slug FR de la destination
        lang: 'fr' | 'en' | 'en-us' | 'es' | 'de'
        asset_prefix: '' pour FR root, '../' pour sous-dossiers (passé par gen_annual)

    Returns:
        HTML de la section ou chaîne vide si avis introuvable.
    """
    avis_data = _load_avis()
    key = f'{slug_fr}:{lang}'
    edito = avis_data.get(key, '').strip()
    if not edito or len(edito) < 50:
        edito = avis_data.get(f'{slug_fr}:fr', '').strip()
    if not edito or len(edito) < 50:
        return ''

    labels = _LABELS.get(lang, _LABELS['fr'])
    about_url = f'{asset_prefix}{labels["about_path"]}'

    return (
        f'<section class="section">\n'
        f' <div class="section-label">{labels["section_label"]}</div>\n'
        f' <div class="avis-card" style="{_STYLE_CARD}">\n'
        f'  <div class="avis-head" style="{_STYLE_HEAD}">\n'
        f'   <div class="avis-avatar" style="{_STYLE_AVATAR}">G</div>\n'
        f'   <div class="avis-meta" style="{_STYLE_META}">\n'
        f'    <div class="avis-label" style="{_STYLE_LABEL}">{labels["label"]}</div>\n'
        f'    <div class="avis-role" style="{_STYLE_ROLE}">{labels["role"]}</div>\n'
        f'   </div>\n'
        f'  </div>\n'
        f'  <p class="avis-edito" style="{_STYLE_EDITO}">{edito}</p>\n'
        f'  <a href="{about_url}" class="avis-author-link" style="{_STYLE_AUTHOR_LINK}" rel="author">{labels["about_link"]}</a>\n'
        f' </div>\n'
        f'</section>'
    )


def has_avis(slug_fr: str, lang: str = 'fr') -> bool:
    """Vérifie si un avis existe pour cette dest/langue."""
    avis_data = _load_avis()
    return bool(avis_data.get(f'{slug_fr}:{lang}', '').strip())
