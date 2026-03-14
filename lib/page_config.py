"""
BestDateWeather — Page generation language config
===================================================
Provides build_config(lang) to create a unified config dict
that gen_annual / gen_monthly use for all language-specific behavior.

Loads strings from locales/{lang}.json — no more if-is_fr-else.
"""

import json, os
from datetime import date

YEAR = date.today().year
TODAY = date.today().strftime('%Y-%m-%d')
# Set manually when climate data is updated — do NOT use TODAY for schema.org
DATA_UPDATED = '2026-03-02'

_LOCALE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'locales')
_locale_cache = {}

def _load_locale(lang):
    """Load and cache a locale JSON file."""
    if lang not in _locale_cache:
        path = os.path.join(_LOCALE_DIR, f'{lang}.json')
        with open(path, encoding='utf-8') as f:
            _locale_cache[lang] = json.load(f)
    return _locale_cache[lang]

# Public alias for use by other generators
load_locale = _load_locale


# Cross-language mapping for hreflang
_CROSS_LANG = {'fr': 'en', 'en': 'fr', 'es': 'fr', 'en-us': 'fr'}

# Season icons (shared across languages)
SEASON_ICONS = {'Printemps':'🌸','Été':'☀️','Automne':'🍂','Hiver':'❄️',
                'Frühling':'🌸','Sommer':'☀️','Herbst':'🍂','Winter':'❄️',
                'Spring':'🌸','Summer':'☀️','Autumn':'🍂','Winter':'❄️',
                'Primavera':'🌸','Verano':'☀️','Otoño':'🍂','Invierno':'❄️'}

# Backward-compatible constants still imported by generate_pages.py
MONTH_URL    = ['january','february','march','april','may','june',
                'july','august','september','october','november','december']
MONTH_URL_FR = ['janvier','fevrier','mars','avril','mai','juin',
                'juillet','aout','septembre','octobre','novembre','decembre']


def date_modified_for(slug, suffix=''):
    """Per-page dateModified staggered over 30 days before DATA_UPDATED."""
    from datetime import timedelta
    base = date.fromisoformat(DATA_UPDATED)
    offset = hash(slug + suffix) % 30
    return (base - timedelta(days=offset)).isoformat()


def build_config(lang):
    """Build a language config dict for page generation.

    Loads locales/{lang}.json and flattens it into a dict compatible
    with all existing callers (cfg['lbl_*'], cfg['months'], etc.).
    """
    loc = _load_locale(lang)
    cross_lang = _CROSS_LANG.get(lang, 'en')
    cross_loc = _load_locale(cross_lang)
    is_fr = (lang == 'fr')

    cfg = {
        'lang': lang,
        'html_lang': loc['meta']['html_lang'],
        'is_fr': is_fr,  # kept for grammar-dependent logic
        'imperial': loc['meta'].get('imperial', False),  # True pour en-us
        'cross_lang': cross_lang,

        # Months
        'months': loc['months'],
        'month_url': loc['month_url'],
        'month_url_cross': cross_loc['month_url'],
        'month_abbr': loc['month_abbr'],

        # Seasons
        'seasons_map': {int(k): v for k, v in loc['seasons_map'].items()},
        'season_order': loc['season_order'],
        'season_range': loc['season_range'],
        'season_months': loc.get('season_months', {}),
        'season_icons': SEASON_ICONS,

        # Paths
        'asset_prefix': loc['meta']['asset_prefix'],
        'cards_file': loc['cards']['file'],
        'card_title_key': loc['cards']['title_key'],
        'card_text_key': loc['cards']['text_key'],

        # URL patterns
        'annual_prefix': loc['url']['annual_prefix'],
        'annual_suffix': loc['url']['annual_suffix'],
        'monthly_sep': loc['url']['monthly_sep'],
        'pillar_prefix': loc['url']['pillar_prefix'],
        'pillar_month_url': loc['url'].get('pillar_month_url', None),
        'base_url': loc['meta']['base_url'],
        'base_url_cross': cross_loc['meta']['base_url'],
        'canonical_prefix': loc['meta']['canonical_prefix'],

        # Cross-language URL patterns (for hreflang)
        'cross_annual_prefix': loc['url']['cross_annual_prefix'],
        'cross_monthly_sep': loc['url']['cross_monthly_sep'],

        # Booking
        'booking_lang': loc['meta']['booking_lang'],
        'booking_domain': loc['meta']['booking_domain'],

        # Footer
        'footer': loc['footer'],

        # Rankings
        'rankings': [tuple(r) for r in loc['rankings']],

        # Schema.org
        'schema_home_url': loc['meta']['schema_home_url'],

        # Destination field mappings
        'dest_fields': loc['dest_fields'],

        # Full locale data (for complex lookups)
        'locale': loc,
    }

    # Flatten labels → cfg['lbl_quick_section'], etc.
    for key, val in loc['labels'].items():
        cfg[f'lbl_{key}'] = val

    # Flatten monthly labels → cfg['lbl_m_hero_tpl'], etc.
    for key, val in loc['monthly'].items():
        cfg[f'lbl_m_{key}'] = val

    # Table config
    cfg['table_aria'] = loc['table']['aria']
    cfg['table_headers'] = loc['table']['headers']
    cfg['table_ski_header'] = loc['table']['ski_header']
    cfg['table_legend_ideal'] = loc['table']['legend_ideal']
    cfg['table_legend_fair'] = loc['table']['legend_fair']
    cfg['table_legend_off'] = loc['table']['legend_off']
    cfg['table_legend_source'] = loc['table']['legend_source']

    # Navigation
    cfg['nav_cta_label'] = loc['nav']['cta_label']
    cfg['nav_cta_href'] = loc['nav']['cta_href']

    # Badges, tiers, verdicts
    cfg['badges'] = loc['badges']
    cfg['tiers'] = loc['tiers']
    cfg['verdicts'] = loc['verdicts']

    # Narratives, FAQ templates, decision criteria
    cfg['narratives'] = loc['narratives']
    cfg['faq_templates'] = loc['faq_templates']
    cfg['decision'] = loc['decision']
    cfg['verdict_words'] = loc['verdict_words']

    # Console / validation messages
    cfg['console'] = loc['console']
    cfg['validation'] = loc['validation']

    # Legacy validation keys (used by validate())
    cfg['val_missing_months'] = loc['validation']['missing_months']
    cfg['val_score_range'] = loc['validation']['score_range']
    cfg['val_no_climate'] = loc['validation']['no_climate']

    # Affiliate / partner
    cfg['gyg_domain'] = loc['meta']['gyg_domain']
    cfg['gyg_lang'] = loc['meta']['gyg_lang']
    cfg['out_subdir'] = loc['meta']['out_subdir']
    cfg['lowercase_months'] = loc['meta']['lowercase_months']
    cfg['in_language'] = loc['meta'].get('in_language')
    cfg['cross_links'] = loc['meta'].get('cross_links', [])

    # Content templates (annual)
    cfg['annual_titles'] = loc.get('annual_titles', [])
    cfg['annual_h1s'] = loc.get('annual_h1s', [])
    cfg['annual_descs'] = loc.get('annual_descs', [])
    cfg['annual_faq_mountain'] = loc.get('annual_faq_mountain', [])
    cfg['annual_faq_standard'] = loc.get('annual_faq_standard', [])
    cfg['annual_faq_winter_verdicts'] = loc.get('annual_faq_winter_verdicts', {})
    cfg['annual_faq_bests_suffix'] = loc.get('annual_faq_bests_suffix', '')

    # Content templates (monthly)
    cfg['monthly_hero_subs'] = loc.get('monthly_hero_subs', {})
    cfg['monthly_hero_subs_ski'] = loc.get('monthly_hero_subs_ski', {})
    cfg['annual_hero_subs_ski'] = loc.get('annual_hero_subs_ski', [])
    cfg['context_paragraphs_ski'] = loc.get('context_paragraphs_ski', {})
    cfg['lbl_m_sec_similar_ski_tpl'] = loc.get('monthly', {}).get('sec_similar_ski_tpl', '')
    cfg['lbl_m_sim_label_ski'] = loc.get('monthly', {}).get('sim_label_ski', '')
    cfg['monthly_verdicts'] = loc.get('monthly_verdicts', {})
    cfg['monthly_oui_si'] = loc.get('monthly_oui_si', {})
    cfg['context_paragraphs'] = loc.get('context_paragraphs', {})

    # Content templates (monthly titles/descs/h1s)
    cfg['monthly_titles'] = loc.get('monthly_titles', [])
    cfg['monthly_descs'] = loc.get('monthly_descs', [])
    cfg['monthly_h1s'] = loc.get('monthly_h1s', [])
    cfg['monthly_article_headline_tpl'] = loc.get('monthly_article_headline_tpl', '')
    cfg['monthly_article_desc_tpl'] = loc.get('monthly_article_desc_tpl', '')

    return cfg


def month_lc(cfg, name):
    """Lowercase month name for FR ('en janvier'), keep as-is for EN ('in January')."""
    return name.lower() if cfg['lowercase_months'] else name


def dest_name(cfg, dest):
    """Return display name for destination."""
    key = cfg['dest_fields']['name_key']
    return dest.get(key, dest.get('nom_bare', dest['slug_fr']))


def dest_name_full(cfg, dest):
    """Return full name with preposition (FR) or plain name (EN)."""
    if cfg['lang'] == 'fr':
        return f"{dest.get('prep_fr', 'à')} {dest.get('nom_bare', dest['slug_fr'])}"
    return dest.get(cfg['dest_fields']['name_key'], dest.get('nom_bare', dest['slug_fr']))


def dest_slug(cfg, dest):
    """Return the slug for URL generation."""
    key = cfg['dest_fields']['slug_key']
    return dest.get(key, dest['slug_fr'])


def dest_country(cfg, dest):
    """Return country name."""
    key = cfg['dest_fields']['country_key']
    return dest.get(key, dest.get('pays', ''))


# Langues actives. Pour ajouter DE : 1) créer locales/de.json 2) ajouter 'de' ici.
SUPPORTED_LANGS = ['fr', 'en', 'en-us', 'es', 'de']

# Cache des configs par langue pour éviter de recharger les locales à chaque page
_lang_cfg_cache: dict = {}

def _get_lang_cfg(lang: str) -> dict | None:
    """Retourne le config minimal d'une langue (base_url + url patterns + month_url).
    Retourne None si le fichier locale n'existe pas."""
    if lang in _lang_cfg_cache:
        return _lang_cfg_cache[lang]
    locale_path = os.path.join(os.path.dirname(__file__), '..', 'locales', f'{lang}.json')
    if not os.path.exists(locale_path):
        _lang_cfg_cache[lang] = None
        return None
    loc = json.load(open(locale_path, encoding='utf-8'))
    _lang_cfg_cache[lang] = {
        'html_lang':        loc['meta']['html_lang'],
        'base_url':         loc['meta']['base_url'].rstrip('/') + '/',
        'annual_prefix':    loc['url']['annual_prefix'],
        'annual_suffix':    loc['url']['annual_suffix'],
        'monthly_sep':      loc['url']['monthly_sep'],
        'month_url':        loc['month_url'],
        'x_default':        loc['meta'].get('x_default', False),
    }
    return _lang_cfg_cache[lang]


def build_hreflang_tags(dest: dict, mi: int | None = None) -> str:
    """Génère les balises <link rel="alternate" hreflang="..."> pour toutes les langues.

    Itère sur SUPPORTED_LANGS — ajouter une langue = ajouter à la liste + créer le locale.
    mi=None → page annuelle ; mi=int → page mensuelle (0-based).

    Retourne une chaîne HTML multiligne prête à insérer dans <head>.
    """
    BASE = 'https://bestdateweather.com'
    tags = []
    x_default_url = None

    for lang in SUPPORTED_LANGS:
        lc = _get_lang_cfg(lang)
        if lc is None:
            continue

        slug = dest.get(f'slug_{lang}', dest.get('slug_en', dest.get('slug_fr', '')))
        if not slug:
            continue

        if mi is None:
            path = f"{lc['annual_prefix']}{slug}{lc['annual_suffix']}"
        else:
            month_key = lc['month_url'][mi]
            path = f"{slug}{lc['monthly_sep']}{month_key}.html"

        # base_url déjà absolu (ex: "https://bestdateweather.com/en/")
        # On reconstruit proprement pour ne pas doubler le domaine
        url_base = lc['base_url']
        if url_base.startswith('http'):
            url = url_base + path
        else:
            url = f"{BASE}/{url_base.lstrip('/')}{path}"

        html_lang = lc['html_lang']
        tags.append(f'<link rel="alternate" hreflang="{html_lang}" href="{url}"/>')

        if lc.get('x_default'):
            x_default_url = url

    # x-default : EN si non défini dans locale
    if x_default_url is None:
        en_lc = _get_lang_cfg('en')
        if en_lc:
            slug = dest.get('slug_en', dest.get('slug_fr', ''))
            if mi is None:
                path = f"{en_lc['annual_prefix']}{slug}{en_lc['annual_suffix']}"
            else:
                month_key = en_lc['month_url'][mi]
                path = f"{slug}{en_lc['monthly_sep']}{month_key}.html"
            x_default_url = en_lc['base_url'] + path

    if x_default_url:
        tags.append(f'<link rel="alternate" hreflang="x-default" href="{x_default_url}"/>')

    return '\n'.join(tags)


def annual_url(cfg, slug):
    """Return annual page filename."""
    return f"{cfg['annual_prefix']}{slug}{cfg['annual_suffix']}"


def monthly_url(cfg, slug, mi):
    """Return monthly page filename."""
    return f"{slug}{cfg['monthly_sep']}{cfg['month_url'][mi]}.html"


def annual_url_cross(cfg, dest):
    """Return annual page URL in the OTHER language (for hreflang)."""
    cross_slug_key = 'slug_en' if cfg['lang'] == 'fr' else 'slug_fr'
    return f"{cfg['cross_annual_prefix']}{dest[cross_slug_key]}.html"


def monthly_url_cross(cfg, dest, mi):
    """Return monthly page URL in the OTHER language (for hreflang)."""
    cross_slug_key = 'slug_en' if cfg['lang'] == 'fr' else 'slug_fr'
    return f"{dest[cross_slug_key]}{cfg['cross_monthly_sep']}{cfg['month_url_cross'][mi]}.html"


def hero_sub(cfg, dest):
    """Return hero subtitle."""
    key = cfg['dest_fields']['hero_sub_key']
    custom = dest.get(key)
    if custom:
        return custom
    return cfg['lbl_hero_sub_default_tpl'].format(name=dest_name(cfg, dest))


def pillar_url(cfg, mi):
    """Return pillar page URL for a month."""
    month_key = cfg['pillar_month_url'][mi] if cfg.get('pillar_month_url') else cfg['month_url'][mi]
    return f"{cfg['pillar_prefix']}{month_key}.html"
