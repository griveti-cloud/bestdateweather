"""
BestDateWeather — Page generation language config
===================================================
Provides build_config(lang, dest) to create a unified config dict
that gen_annual / gen_monthly use for all language-specific behavior.
"""

from datetime import date

YEAR = date.today().year
TODAY = date.today().strftime('%Y-%m-%d')

# ── Month names ──────────────────────────────────────────────────────────────

MONTHS_FR  = ['Janvier','Février','Mars','Avril','Mai','Juin',
              'Juillet','Août','Septembre','Octobre','Novembre','Décembre']
MONTHS_EN  = ['January','February','March','April','May','June',
              'July','August','September','October','November','December']
MONTH_URL  = ['january','february','march','april','may','june',
              'july','august','september','october','november','december']
MONTH_URL_FR = ['janvier','fevrier','mars','avril','mai','juin',
                'juillet','aout','septembre','octobre','novembre','decembre']
MONTH_ABBR_FR = ['Jan','Fév','Mar','Avr','Mai','Jun','Jul','Aoû','Sep','Oct','Nov','Déc']
MONTH_ABBR_EN = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']

# ── Season config ────────────────────────────────────────────────────────────

SEASONS_FR = {0:'Hiver',1:'Hiver',2:'Printemps',3:'Printemps',4:'Printemps',
              5:'Été',6:'Été',7:'Été',8:'Automne',9:'Automne',10:'Automne',11:'Hiver'}
SEASONS_EN = {0:'Winter',1:'Winter',2:'Spring',3:'Spring',4:'Spring',
              5:'Summer',6:'Summer',7:'Summer',8:'Autumn',9:'Autumn',10:'Autumn',11:'Winter'}
SEASON_ICONS = {'Printemps':'🌸','Été':'☀️','Automne':'🍂','Hiver':'❄️',
                'Spring':'🌸','Summer':'☀️','Autumn':'🍂','Winter':'❄️'}
SEASON_ORDER_FR = ['Printemps','Été','Automne','Hiver']
SEASON_ORDER_EN = ['Spring','Summer','Autumn','Winter']
SEASON_RANGE_FR = {'Printemps':'mars–mai','Été':'juin–août','Automne':'sept–nov','Hiver':'déc–fév'}
SEASON_RANGE_EN = {'Spring':'Mar–May','Summer':'Jun–Aug','Autumn':'Sep–Nov','Winter':'Dec–Feb'}


def build_config(lang):
    """Build a language config dict for page generation."""
    is_fr = (lang == 'fr')

    return {
        'lang': lang,
        'html_lang': lang,
        'is_fr': is_fr,

        # Months
        'months': MONTHS_FR if is_fr else MONTHS_EN,
        'month_url': MONTH_URL_FR if is_fr else MONTH_URL,
        'month_url_cross': MONTH_URL if is_fr else MONTH_URL_FR,  # for hreflang
        'month_abbr': MONTH_ABBR_FR if is_fr else MONTH_ABBR_EN,

        # Seasons
        'seasons_map': SEASONS_FR if is_fr else SEASONS_EN,
        'season_order': SEASON_ORDER_FR if is_fr else SEASON_ORDER_EN,
        'season_range': SEASON_RANGE_FR if is_fr else SEASON_RANGE_EN,
        'season_icons': SEASON_ICONS,

        # Paths
        'asset_prefix': '' if is_fr else '../',
        'cards_file': 'cards.csv' if is_fr else 'cards_en.csv',
        'card_title_key': 'titre' if is_fr else 'title',
        'card_text_key': 'texte' if is_fr else 'text',

        # URL patterns
        'annual_prefix': 'meilleure-periode-' if is_fr else 'best-time-to-visit-',
        'annual_suffix': '.html',
        'monthly_sep': '-meteo-' if is_fr else '-weather-',
        'pillar_prefix': 'ou-partir-en-' if is_fr else 'where-to-go-in-',
        'base_url': 'https://bestdateweather.com/' if is_fr else 'https://bestdateweather.com/en/',
        'base_url_cross': 'https://bestdateweather.com/en/' if is_fr else 'https://bestdateweather.com/',
        'canonical_prefix': 'https://bestdateweather.com/' if is_fr else 'https://bestdateweather.com/en/',

        # Booking
        'booking_lang': 'fr' if is_fr else 'en-gb',
        'booking_domain': 'searchresults.fr.html' if is_fr else 'searchresults.en-gb.html',

        # Footer
        'footer': {
            'data_by': 'Données météo par Open-Meteo.com' if is_fr else 'Weather data by Open-Meteo.com',
            'sources': 'Sources ECMWF, DWD, NOAA, Météo-France · CC BY 4.0' if is_fr else 'Sources: ECMWF, DWD, NOAA · CC BY 4.0',
            'methodology': ('methodologie.html', 'Méthodologie') if is_fr else ('methodology.html', 'Methodology'),
            'app': ('index.html', 'Application météo') if is_fr else ('app.html', 'Weather app'),
            'legal': ('mentions-legales.html', 'Mentions légales') if is_fr else ('legal.html', 'Legal'),
            'privacy': ('confidentialite.html', 'Confidentialité') if is_fr else ('privacy.html', 'Privacy'),
            'alt_lang_flag': 'gb' if is_fr else 'fr',
            'alt_lang_label': 'English' if is_fr else 'Français',
        },

        # Rankings
        'rankings': _rankings_fr() if is_fr else _rankings_en(),

        # ── Labels (page sections) ──────────────────────────────────────
        'lbl_quick_section': 'Décision en 30 secondes' if is_fr else 'Quick decision',
        'lbl_quick_title_tpl': 'Quand partir {name} ?' if is_fr else 'When to visit {name}?',
        'lbl_best_overall': '🌞 Meilleure période générale' if is_fr else '🌞 Best time overall',
        'lbl_optimal_temp': '🌡️ Température optimale' if is_fr else '🌡️ Optimal temperature',
        'lbl_least_rain': '🌧 Moins de pluie' if is_fr else '🌧 Least rain',
        'lbl_wettest': '🌧 Mois le plus pluvieux' if is_fr else '🌧 Wettest month',
        'lbl_best_score': '📅 Meilleur score' if is_fr else '📅 Best score',
        'lbl_rainy_days_in': 'de jours pluvieux en' if is_fr else 'rainy days in',
        'lbl_in': 'en' if is_fr else 'in',

        'lbl_cards_section': 'Selon votre projet' if is_fr else 'By trip type',
        'lbl_cards_title': 'Meilleure période selon votre type de voyage' if is_fr else 'Best time by type of trip',

        'lbl_table_section': 'Tableau climatique mensuel' if is_fr else 'Monthly climate data',
        'lbl_table_title_tpl': 'Météo {name} mois par mois' if is_fr else '{name} weather month by month',

        'lbl_season_section': 'Analyse saison par saison' if is_fr else 'Seasonal breakdown',
        'lbl_season_title': "À quoi s'attendre selon la période" if is_fr else 'What to expect each season',
        'lbl_season_temp_tpl': 'Températures moyennes {tmax}°C, {rain}% de jours avec pluie, {sun}h de soleil par jour. Score moyen : {score}/10.' if is_fr else 'Average {tmax}°C, {rain}% rainy days, {sun}h sunshine/day. Score: {score}/10.',

        'lbl_booking_section': 'Hébergement' if is_fr else 'Accommodation',
        'lbl_booking_title_tpl': "Trouver un hébergement {name}" if is_fr else 'Find a place to stay in {name}',
        'lbl_booking_cta': 'Voir les disponibilités sur la période recommandée' if is_fr else 'Check availability during the recommended period',
        'lbl_booking_btn': 'Rechercher sur Booking.com' if is_fr else 'Search on Booking.com',

        'lbl_monthly_section': 'Météo par mois' if is_fr else 'Monthly weather',
        'lbl_monthly_title': 'Météo détaillée mois par mois' if is_fr else 'Detailed weather by month',

        'lbl_faq_section': 'FAQ',
        'lbl_faq_title': 'Questions fréquentes' if is_fr else 'Frequently asked questions',

        'lbl_similar_section': 'Explorer aussi' if is_fr else 'Also explore',
        'lbl_similar_title': 'Destinations au climat similaire' if is_fr else 'Destinations with similar climate',
        'lbl_similar_match': 'Climat similaire · {pct} de correspondance' if is_fr else 'Similar climate · {pct} match',

        'lbl_ranking_section': 'Classements météo' if is_fr else 'Weather rankings',
        'lbl_ranking_title': 'Comparer les destinations par météo' if is_fr else 'Compare destinations by weather',

        'lbl_guides_section': 'Guides & comparatifs' if is_fr else 'Guides & comparisons',
        'lbl_guides_title': 'Explorer par mois ou comparer' if is_fr else 'Explore by month or compare',
        'lbl_pillar_tpl': '📅 Où partir en {month} — top 25' if is_fr else '📅 Where to go in {month} — top 25',
        'lbl_vs_tpl': '⚖️ {a} ou {b} ?' if is_fr else '⚖️ {a} vs {b}',

        'lbl_breadcrumb_home': 'Accueil' if is_fr else 'Home',
        'lbl_updated_tpl': 'Mis à jour : {date} · Open-Meteo · 10 ans · 12 mois comparés · {coords}' if is_fr else 'Updated: {date} · Open-Meteo · 10 years · 12 months compared · {coords}',
        'lbl_best_months': "Meilleur{s} mois" if is_fr else 'Best month{s}',
        'lbl_optimal_temp_stat': 'Température optimale' if is_fr else 'Optimal temperature',
        'lbl_rainy_days_stat': 'Jours pluvieux' if is_fr else 'Rainy days',
        'lbl_hero_sub_default_tpl': '{name}, une destination à découvrir selon la météo.' if is_fr else '{name}, a destination to discover based on weather data.',

        # Budget tips
        'lbl_tip_prefix': 'Conseil' if is_fr else 'Tip',
        'lbl_tip_good_tpl': '{months} {verb} un bon compromis météo/prix — score correct avec moins d\'affluence.' if is_fr else '{months} {verb} a good weather/price balance — decent score with fewer crowds.',
        'lbl_tip_offpeak_tpl': 'les mois hors pic ({m1}, {m2}) sont les moins chers mais la météo est nettement moins favorable.' if is_fr else 'off-peak months ({m1}, {m2}) are cheapest but weather is significantly worse.',
        'lbl_offer_sg': 'offre' if is_fr else 'offers',
        'lbl_offer_pl': 'offrent' if is_fr else 'offer',

        # Schema.org
        'schema_home_url': 'https://bestdateweather.com/' if is_fr else 'https://bestdateweather.com/en/app.html',

        # ── Monthly page labels ─────────────────────────────────────────
        'lbl_m_hero_tpl': 'Météo {name} en {month}' if is_fr else '{name} weather in {month}',
        'lbl_m_score_label': 'Score météo' if is_fr else 'Weather score',
        'lbl_m_temp_range': 'Températures' if is_fr else 'Temperatures',
        'lbl_m_rain_label': 'Pluie' if is_fr else 'Rain',
        'lbl_m_sun_label': 'Soleil' if is_fr else 'Sun',
        'lbl_m_overview_section': 'Résumé du mois' if is_fr else 'Month overview',
        'lbl_m_overview_title_tpl': '{name} en {month} : à quoi s\'attendre ?' if is_fr else '{name} in {month}: what to expect?',
        'lbl_m_detail_section': 'Détails climatiques' if is_fr else 'Climate details',
        'lbl_m_detail_title': 'Données détaillées' if is_fr else 'Detailed data',
        'lbl_m_temp_section_label': 'Températures' if is_fr else 'Temperatures',
        'lbl_m_rain_section_label': 'Précipitations' if is_fr else 'Precipitation',
        'lbl_m_sun_section_label': 'Ensoleillement' if is_fr else 'Sunshine',
        'lbl_m_min': 'Min' if is_fr else 'Min',
        'lbl_m_max': 'Max' if is_fr else 'Max',
        'lbl_m_rainy_days': 'Jours de pluie' if is_fr else 'Rainy days',
        'lbl_m_precip_day': 'Précipitations/jour' if is_fr else 'Precipitation/day',
        'lbl_m_sun_day': 'Soleil/jour' if is_fr else 'Sunshine/day',
        'lbl_m_other_months': 'Autres mois' if is_fr else 'Other months',
        'lbl_m_other_title_tpl': 'Météo {name} les autres mois' if is_fr else '{name} weather in other months',
        'lbl_m_compare_section': 'Comparer' if is_fr else 'Compare',
        'lbl_m_compare_title': 'Guides et comparaisons' if is_fr else 'Guides and comparisons',
        'lbl_m_back_annual_tpl': '← Meilleure période {name}' if is_fr else '← Best time to visit {name}',
        'lbl_m_month_nav_tpl': 'Météo en {month}' if is_fr else 'Weather in {month}',

        # Monthly context paragraph
        'lbl_m_context_excellent': 'C\'est le meilleur mois de l\'année {name}.' if is_fr else 'This is the best month of the year for {name}.',
        'lbl_m_context_good': 'C\'est une bonne période pour visiter {name}.' if is_fr else 'This is a good time to visit {name}.',
        'lbl_m_context_fair': 'Les conditions sont acceptables {name}.' if is_fr else 'Conditions are acceptable in {name}.',
        'lbl_m_context_poor': 'Ce n\'est pas la meilleure période {name}.' if is_fr else 'This is not the best time for {name}.',
        'lbl_m_better_month_tpl': 'Préférez {month} ({score}/10) pour de meilleures conditions.' if is_fr else 'Consider {month} ({score}/10) for better conditions.',
        'lbl_m_tropical_note': 'En zone tropicale, la pluie prend souvent la forme d\'averses courtes et intenses plutôt que de journées grises.' if is_fr else 'In tropical areas, rain often comes as short, intense showers rather than grey days.',

        # Validation
        'val_missing_months': '[P0] {slug}: mois manquants: {missing}' if is_fr else '[P0] {slug}: missing months: {missing}',
        'val_score_range': '[P0] {slug}/{month}: score hors plage ({score})' if is_fr else '[P0] {slug}/{month}: score out of range ({score})',
        'val_no_climate': '[P1] {slug}: dans destinations.csv mais pas de données climat' if is_fr else '[P1] {slug}: in destinations.csv but no climate data',

        # Console output
        'msg_title': 'BestDateWeather — generate_pages.py' ,
        'msg_target_all': 'toutes les destinations' if is_fr else 'all destinations',
        'msg_validation_ok': '✅ Validation OK\n',
        'msg_skip_unknown': '[SKIP] {slug}: destination inconnue' if is_fr else '[SKIP] {slug}: unknown destination',
        'msg_skip_incomplete': '[SKIP] {slug}: données climatiques incomplètes' if is_fr else '[SKIP] {slug}: incomplete climate data',
        'msg_monthly_done': '12 fiches mensuelles' if is_fr else '12 monthly pages',
        'msg_monthly_skip': 'mensuelles ignorées (monthly=False)' if is_fr else 'monthly skipped (monthly=False)',
        'msg_no_errors': '✅ Aucune erreur de génération' if is_fr else '✅ No generation errors',
    }


def dest_name(cfg, dest):
    """Return display name for destination: 'prep + nom_bare' (FR) or 'nom_en' (EN)."""
    if cfg['is_fr']:
        return dest.get('nom_bare', dest['slug_fr'])
    return dest.get('nom_en', dest.get('nom_bare', dest['slug_fr']))


def dest_name_full(cfg, dest):
    """Return full name with preposition (FR: 'à Paris') or plain name (EN: 'Paris')."""
    if cfg['is_fr']:
        return f"{dest.get('prep', 'à')} {dest.get('nom_bare', dest['slug_fr'])}"
    return dest.get('nom_en', dest.get('nom_bare', dest['slug_fr']))


def dest_slug(cfg, dest):
    """Return the slug for URL generation."""
    if cfg['is_fr']:
        return dest['slug_fr']
    return dest['slug_en']


def dest_country(cfg, dest):
    """Return country name."""
    if cfg['is_fr']:
        return dest.get('pays', '')
    return dest.get('country_en', dest.get('pays', ''))


def annual_url(cfg, slug):
    """Return annual page filename."""
    return f"{cfg['annual_prefix']}{slug}{cfg['annual_suffix']}"


def monthly_url(cfg, slug, mi):
    """Return monthly page filename."""
    return f"{slug}{cfg['monthly_sep']}{cfg['month_url'][mi]}.html"


def annual_url_cross(cfg, dest):
    """Return annual page URL in the OTHER language (for hreflang)."""
    if cfg['is_fr']:
        return f"best-time-to-visit-{dest['slug_en']}.html"
    return f"meilleure-periode-{dest['slug_fr']}.html"


def monthly_url_cross(cfg, dest, mi):
    """Return monthly page URL in the OTHER language (for hreflang)."""
    if cfg['is_fr']:
        return f"{dest['slug_en']}-weather-{MONTH_URL[mi]}.html"
    return f"{dest['slug_fr']}-meteo-{MONTH_URL_FR[mi]}.html"


def hero_sub(cfg, dest):
    """Return hero subtitle."""
    if cfg['is_fr']:
        return dest.get('hero_sub') or cfg['lbl_hero_sub_default_tpl'].format(name=dest_name(cfg, dest))
    return dest.get('hero_sub_en') or cfg['lbl_hero_sub_default_tpl'].format(name=dest_name(cfg, dest))


def pillar_url(cfg, mi):
    """Return pillar page URL for a month."""
    return f"{cfg['pillar_prefix']}{cfg['month_url'][mi]}.html"


def _rankings_fr():
    return [
        ('classement-destinations-meteo-2026.html', '🌍 Classement mondial 2026'),
        ('classement-destinations-meteo-ete-2026.html', '🌞 Meilleures destinations été'),
        ('classement-destinations-meteo-hiver-2026.html', '🌴 Destinations soleil hiver'),
    ]

def _rankings_en():
    return [
        ('best-destinations-weather-ranking-2026.html', '🌍 World ranking 2026'),
        ('best-europe-weather-ranking-2026.html', '🇪🇺 Best in Europe'),
    ]
