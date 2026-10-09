"""
Liens de monétisation : source unique pour les pages (fiches annuelles et
mensuelles V6, ancien gabarit). Le script de l'application (js/core.js) suit
les mêmes formats.

Audit du 9 octobre 2026 (formats vérifiés en conditions réelles) :
- Expedia : passer par https://www.expedia.com/affiliate?... (Link builder).
  Un lien direct expedia.xx/Hotel-Search?…&camref=… n'est pas suivi.
- Kiwi.com : passer par le lien de clic Travelpayouts (c111.travelpayouts.com)
  avec un code aéroport (IATA). Un nom de ville (to=Paris) renvoie vers
  l'accueil de Kiwi, et affilid=708106 n'est pas reconnu.
- GetYourGuide : partner_id sur toute adresse GetYourGuide ; le widget est
  ancré sur un lieu précis (data/gyg_locations.json, résolu par
  scripts/resolve_gyg_locations.py) car la recherche par nom envoie parfois
  ailleurs (Santiago → Cap-Vert, La Paz → Mexique).
"""
import csv
import json
import urllib.parse
from functools import lru_cache
from pathlib import Path

from config import (GYG_PARTNER_ID, TP_MARKER, TP_KIWI_PROMO_ID,
                    EXPEDIA_CAMREF, EXPEDIA_CREATIVEREF, EXPEDIA_ADREF)

ROOT = Path(__file__).resolve().parent.parent

EXPEDIA_DOMAIN = {'fr': 'expedia.fr', 'en': 'expedia.co.uk', 'en-us': 'expedia.com', 'es': 'expedia.es', 'de': 'expedia.de'}
# Domaines locaux GetYourGuide : redirigent vers getyourguide.com/fr-fr/… (partner_id conservé)
GYG_DOMAIN = {'fr': 'getyourguide.fr', 'en': 'getyourguide.co.uk', 'en-us': 'getyourguide.com', 'es': 'getyourguide.es', 'de': 'getyourguide.de'}
GYG_LOCALE = {'fr': 'fr-FR', 'en': 'en-GB', 'en-us': 'en-US', 'es': 'es-ES', 'de': 'de-DE'}
KIWI_LANG = {'fr': 'fr', 'en': 'en', 'en-us': 'en', 'es': 'es', 'de': 'de'}


def q(s):
    return urllib.parse.quote(str(s), safe='')


@lru_cache(maxsize=1)
def _dests():
    """Destinations indexées par tous leurs slugs (fr, en, es, de) → ligne du CSV."""
    out = {}
    with open(ROOT / 'data' / 'destinations.csv', encoding='utf-8-sig') as f:
        for r in csv.DictReader(f):
            for k in ('slug_fr', 'slug_en', 'slug_es', 'slug_de'):
                if r.get(k):
                    out.setdefault(r[k], r)
    return out


@lru_cache(maxsize=1)
def _gyg_locations():
    p = ROOT / 'data' / 'gyg_locations.json'
    return json.load(open(p, encoding='utf-8')) if p.exists() else {}


def dest(slug):
    return _dests().get(slug) or {}


def place_query(d):
    """« Nom anglais, pays » (« Paris, France ») : désambiguïse les homonymes
    (Santiago, Córdoba…). « Hawaii / Maui » → « Hawaii »."""
    name = (d.get('nom_en') or d.get('nom_bare') or '').split('/')[0].strip()
    country = (d.get('country_en') or '').strip()
    return f'{name}, {country}' if country and country.lower() != name.lower() else name


def sub_id(kind, lang):
    """Sous-identifiant de suivi (tableaux de bord partenaires) : annualfr, monthlyenus…"""
    return f"{kind}{lang.replace('-', '')}"


def expedia_url(lang, d):
    landing = f'https://www.{EXPEDIA_DOMAIN.get(lang, "expedia.com")}/Hotel-Search?destination={q(place_query(d))}'
    return (f'https://www.expedia.com/affiliate?siteid=1&landingPage={q(landing)}'
            f'&camref={EXPEDIA_CAMREF}&creativeref={EXPEDIA_CREATIVEREF}&adref={EXPEDIA_ADREF}')


def kiwi_url(lang, d, kind='annual'):
    """Vols vers l'aéroport de la destination ; départ = position du visiteur (Kiwi)."""
    iata = (d.get('iata') or '').strip().upper()
    if len(iata) != 3 or not iata.isalpha():
        return None
    deep = f'https://www.kiwi.com/deep?to={iata}&lang={KIWI_LANG.get(lang, "en")}'
    return (f'https://c111.travelpayouts.com/click?shmarker={TP_MARKER}.{sub_id(kind, lang)}'
            f'&promo_id={TP_KIWI_PROMO_ID}&source_type=customlink&type=click&custom_url={q(deep)}')


def gyg(lang, d, kind='annual'):
    """Activités GetYourGuide : {'mode': 'location'|'search', 'url', 'location_id'} ou None (pas de bloc)."""
    slug_fr = d.get('slug_fr', '')
    loc = _gyg_locations().get(slug_fr)
    dom = GYG_DOMAIN.get(lang, 'getyourguide.com')
    track = f'partner_id={GYG_PARTNER_ID}&cmp={sub_id(kind, lang)}'
    if loc and loc.get('id'):
        return {'mode': 'location', 'location_id': int(loc['id']),
                'url': f"https://www.{dom}/{loc.get('name') or 'x'}-l{int(loc['id'])}/?{track}"}
    if loc:
        return {'mode': 'search', 'location_id': None, 'url': f'https://www.{dom}/s/?q={q(place_query(d))}&{track}'}
    return None
