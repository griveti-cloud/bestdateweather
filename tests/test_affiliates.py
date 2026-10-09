"""Liens de monétisation (lib/affiliates.py) : formats vérifiés le 9 octobre 2026."""
import sys
import urllib.parse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from lib import affiliates as A  # noqa: E402


def _qs(url):
    return urllib.parse.parse_qs(urllib.parse.urlsplit(url).query)


def test_expedia_passe_par_le_suivi_affilie():
    for lang, dom in A.EXPEDIA_DOMAIN.items():
        u = A.expedia_url(lang, A.dest('paris'))
        assert u.startswith('https://www.expedia.com/affiliate?siteid=1&landingPage=')
        q = _qs(u)
        assert q['camref'] == ['1110lB57J'] and q['creativeref'] and q['adref']
        landing = q['landingPage'][0]          # page d'arrivée locale, ville + pays
        assert landing.startswith(f'https://www.{dom}/Hotel-Search?destination=')
        assert _qs(landing)['destination'] == ['Paris, France']


def test_kiwi_par_travelpayouts_avec_code_aeroport():
    u = A.kiwi_url('es', A.dest('sarajevo'), 'monthly')
    q = _qs(u)
    assert u.startswith('https://c111.travelpayouts.com/click?')
    assert q['shmarker'] == ['708106.monthlyes'] and q['promo_id'] == ['3791']
    assert q['custom_url'] == ['https://www.kiwi.com/deep?to=SJJ&lang=es']


def test_getyourguide_lieu_precis_ou_rien():
    paris = A.gyg('fr', A.dest('paris'))
    assert paris['mode'] == 'location' and paris['location_id'] == 16
    assert paris['url'].startswith('https://www.getyourguide.fr/') and 'partner_id=2MQKL00' in paris['url']
    # homonymes corrigés : Santiago du Chili (pas le Cap-Vert), La Paz en Bolivie (pas le Mexique)
    assert A.gyg('en', A.dest('santiago'))['location_id'] == 226
    assert A.gyg('en', A.dest('la-paz'))['location_id'] == 4674
    # aucun lieu pertinent : pas de bloc
    assert A.gyg('fr', A.dest('ndjamena')) is None


def test_bloc_reserver_echappe_une_seule_fois():
    from lib.v6 import render_v6_reserver
    out = render_v6_reserver('cortina-dampezzo', 'fr', "Cortina d'Ampezzo", slug_fr='cortina-dampezzo')
    assert "Cortina d&#x27;Ampezzo" in out and '&amp;#x27;' not in out
    assert 'data-gyg-location-id="2208"' in out and 'data-gyg-q' not in out
    sans = render_v6_reserver('ndjamena', 'fr', "N'Djamena", slug_fr='ndjamena')
    assert sans.count('class="plan-card"') == 2 and 'grid-2' in sans and 'id="activites"' not in sans
