"""
Politique d'indexation : source unique de vérité (plan B, octobre 2026).

Contexte : le site a publié ~50 000 pages en 4 semaines (février-mars 2026) ;
Google a exploré ~62 000 URL et refusé de les indexer (« Explorée, actuellement
non indexée »). Le plan B réduit l'ensemble indexable aux pages qui ont une
raison d'exister dans les résultats : pages pratiques et hubs FR/EN, pages
annuelles d'une sélection de destinations, et les pages qui ont réellement
reçu des impressions Google.

Toute page HTML hors de cet ensemble reçoit <meta name="robots"
content="noindex,follow"/> (apply_indexation.py) et sort du sitemap
(generate_sitemaps.py). check_deploy.py bloque le déploiement si une page
s'écarte de la politique.

Les paramètres éditables sont dans data/indexation_policy.json.
"""

import csv
import glob
import json
import os

_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
_POLICY_PATH = os.path.join(_ROOT, 'data', 'indexation_policy.json')
_DUP_PATH = os.path.join(_ROOT, 'data', 'duplicate_destinations.json')
_DEST_PATH = os.path.join(_ROOT, 'data', 'destinations.csv')

# Pages pratiques indexables (chemins servis, sans .html ; '' = racine FR)
_STATIC_FR = ['', 'carte', 'a-propos', 'methodologie', 'faq', 'contact',
              'mentions-legales', 'confidentialite', 'meilleures-destinations-meteo']
_STATIC_EN = ['en/app', 'en/map', 'en/about', 'en/methodology', 'en/faq',
              'en/contact', 'en/legal', 'en/privacy']

# Hubs indexables (motifs de fichiers relatifs à la racine)
_HUB_GLOBS = {
    'fr': ['ou-partir-en-*.html', 'classement-*.html'],
    'en': ['en/where-to-go-in-*.html', 'en/best-*-20[0-9][0-9].html'],
}

_cache = {}


def _root_path(rel):
    return os.path.join(_ROOT, rel)


def served_path(rel_html: str) -> str:
    """'index.html' -> '' ; 'en/app.html' -> 'en/app' ; chemin servi par le worker."""
    rel = rel_html.replace(os.sep, '/').lstrip('./')
    if rel == 'index.html':
        return ''
    if rel.endswith('/index.html'):
        return rel[:-len('index.html')].rstrip('/')
    return rel[:-5] if rel.endswith('.html') else rel


def load_policy() -> dict:
    if 'policy' not in _cache:
        with open(_POLICY_PATH, encoding='utf-8') as f:
            _cache['policy'] = json.load(f)
    return _cache['policy']


def _duplicates() -> set:
    if 'dup' not in _cache:
        try:
            _cache['dup'] = set(json.load(open(_DUP_PATH, encoding='utf-8')).keys())
        except Exception:
            _cache['dup'] = set()
    return _cache['dup']


def indexed_destinations() -> list:
    """Destinations (slug_fr) dont la page annuelle FR/EN est indexable."""
    if 'dests' not in _cache:
        pol = load_policy()
        dup = _duplicates()
        sel = set(pol.get('destinations_historique_gsc', [])) | set(pol.get('destinations_forte_demande', []))
        _cache['dests'] = sorted(s for s in sel if s not in dup)
    return _cache['dests']


def is_indexed_destination(slug_fr: str) -> bool:
    return slug_fr in set(indexed_destinations())


def _dest_rows() -> dict:
    if 'rows' not in _cache:
        with open(_DEST_PATH, encoding='utf-8-sig') as f:
            _cache['rows'] = {r['slug_fr']: r for r in csv.DictReader(f)}
    return _cache['rows']


def indexable_paths() -> set:
    """Ensemble des chemins servis indexables (sans .html, '' pour la racine).

    Seuls les chemins dont le fichier existe sont retenus.
    """
    if 'paths' in _cache:
        return _cache['paths']
    pol = load_policy()
    paths = set()

    def add(p):
        f = 'index.html' if p == '' else p + '.html'
        if os.path.exists(_root_path(f)):
            paths.add(p)

    for p in _STATIC_FR + _STATIC_EN + pol.get('applis_internationales', []):
        add(p)
    for lang, globs in _HUB_GLOBS.items():
        if lang not in pol.get('langues_indexees', ['fr', 'en']):
            continue
        for g in globs:
            for f in glob.glob(_root_path(g)):
                rel = os.path.relpath(f, _ROOT)
                if '/best-time-to-visit-' in '/' + rel:
                    continue
                paths.add(served_path(rel))
    rows = _dest_rows()
    for slug in indexed_destinations():
        r = rows.get(slug)
        if not r:
            continue
        add(f'meilleure-periode-{slug}')
        slug_en = (r.get('slug_en') or '').strip()
        if slug_en:
            add(f'en/best-time-to-visit-{slug_en}')
    for p in pol.get('exceptions_gsc', []):
        add(p)
    _cache['paths'] = paths
    return paths


def is_indexable(rel_html: str) -> bool:
    return served_path(rel_html) in indexable_paths()


def lang_of(path: str) -> str:
    """Langue d'un chemin servi : 'fr', 'en', 'en-us', 'es', 'de'."""
    head = path.split('/', 1)[0] if '/' in path else ''
    return {'en': 'en', 'us': 'en-us', 'es': 'es', 'de': 'de'}.get(head, 'fr')


def is_indexable_url(url: str) -> bool:
    """Même test à partir d'une URL canonique (https://bestdateweather.com/...)."""
    import re as _re
    p = _re.sub(r'^https?://(?:www\.)?bestdateweather\.com/?', '', url or '')
    p = p.split('#')[0].split('?')[0]
    if p.endswith('.html'):
        p = p[:-5]
    if p == 'index':
        p = ''
    return p.rstrip('/') in indexable_paths()
