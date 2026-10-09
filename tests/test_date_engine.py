"""Moteur « Où partir à mes dates » : règles de calcul de base (lib/date_engine.py).

La cohérence avec js/date-engine.js se vérifie dans un navigateur
(window.BDW_ENGINE_TEST.compute) : voir la procédure dans docs/plan_b.md.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from lib import date_engine as E  # noqa: E402


def test_fenetre_simple():
    w = E.window('2026-12-01', '2026-12-31')
    assert w['n'] == 31 and not w['cross'] and w['limit'] == 4
    assert w['days'][0] == (334, 0) and w['days'][-1] == (364, 0)


def test_fenetre_a_cheval_sur_deux_annees():
    w = E.window('2026-12-19', '2027-01-03')
    assert w['n'] == 16 and w['cross'] and w['limit'] == 2
    assert w['days'][-1] == (2, 1)


def test_fenetre_erreurs():
    assert E.window('2027-01-10', '2027-01-01')['error'] == 'err_order'
    assert E.window('2027-01-01', '2027-04-30')['error'] == 'err_long'
    assert E.window('', '2027-01-01')['error'] == 'err_missing'


def test_bits_aller_retour():
    line = ''.join('1' if i % 3 == 0 else '0' for i in range(365))
    b = E._bits_b64(line)
    assert all(E._bit(b, i) == (1 if i % 3 == 0 else 0) for i in range(365))


def _rec(slug, score, rain=10.0, ch=None, m=0):
    M = {k: [None] * 12 for k in ('s', 'b', 'k', 'hk', 'r', 'tx', 'tn', 'sun', 'sea')}
    for i in range(12):
        M['s'][i], M['r'][i], M['tx'][i], M['tn'][i], M['sun'][i] = score, rain, 25.0, 15.0, 8.0
    r = {'s': slug, 'e': slug, 'n': [slug, slug], 'p': ['X', 'X'], 'reg': 'eu', 'rl': 1, 'bi': 2, 'm': m, 'cc': 'XX',
         'la': 40.0, 'lo': 0.0, 'M': M}
    if ch:
        r['ch'] = ch
    return r


def test_classement_et_parent_retire():
    ds = [_rec('a', 8.0), _rec('b', 9.0), _rec('iles', 9.5, ch=['b'])]
    v = E.compute_view(ds, E.default_state(11, 'fr'), 'fr')
    assert [x['d']['s'] for x in v['rows']] == ['b', 'a']   # le parent disparaît, tri par score


def test_filtre_securite_par_defaut():
    ds = [_rec('a', 8.0), dict(_rec('z', 9.9), rl=4)]
    v = E.compute_view(ds, E.default_state(11, 'fr'), 'fr')
    assert [x['d']['s'] for x in v['rows']] == ['a']


def test_ski_seulement_montagne():
    ds = [_rec('a', 8.0), _rec('m', 5.0, m=1)]
    ds[1]['M']['k'] = [7.0] * 12
    st = dict(E.default_state(11, 'fr'), uc='ski')
    v = E.compute_view(ds, st, 'fr')
    assert [x['d']['s'] for x in v['rows']] == ['m']


def test_plus_sure_parmi_les_bonnes_destinations():
    # la moins pluvieuse (rain=0) a un score de 4 : elle ne doit pas être « la plus sûre »
    ds = [_rec('sec-mais-froid', 4.0, rain=0.0), _rec('bonne', 8.5, rain=5.0)]
    v = E.compute_view(ds, E.default_state(11, 'fr'), 'fr')
    assert [f['x']['d']['s'] for f in v['facts'] if f['k'] == 'f_safe'] == ['bonne']


def test_formats_par_langue():
    from lib.engine_render import R
    us, es, de, fr = R('en-us', ''), R('es', ''), R('de', ''), R('fr', '')
    assert us.t1(25.0) == '77' and us.t0(-10.0) == '14' and us.U == ' °F'
    assert us.fmt_km(1609.344) == '1,000 mi' and fr.fmt_km(1500) == '1 500 km' and de.fmt_km(1500) == '1.500 km'
    assert es.f1(7.25) == '7,3' and us.f1(7.25) == '7.3' and fr.t1(21.04) == '21,0'
    assert de.fmt_h(4.5) == '4:30 Std.' and es.fmt_h(4.5) == '4 h 30' and us.fmt_h(4.5) == '4h30'
    assert us.long_date('2026-11-26') == 'Thursday, November 26, 2026'
    assert es.long_date('2027-03-28') == 'domingo 28 de marzo de 2027'
    assert de.long_date('2027-05-17') == 'Montag, 17. Mai 2027'
    assert fr.long_date('2026-12-01') == 'mardi 1er décembre 2026'


def test_raccourcis_de_dates_valides():
    import datetime as dt
    for lang in E.LANGS:
        for mi, hs in E.I18N[lang]['holidays'].items():
            for h in hs:
                assert h['id'].isalpha() and h['id'].islower()          # liens #id du script client
                ranges = h['zones'].values() if h.get('zones') else [(h['a'], h['b'])]
                for a, b in ranges:
                    assert 'error' not in E.window(a, b), (lang, h['id'])
                    assert dt.date.fromisoformat(a).month == int(mi) + 1, (lang, h['id'])   # rangé sous son mois de départ


def test_textes_complets_dans_chaque_langue():
    ref = E.I18N['fr']
    for lang in E.LANGS:
        L = E.I18N[lang]
        assert set(L['t']) == set(ref['t']), (lang, set(ref['t']) ^ set(L['t']))
        assert len(L['months']) == len(L['ms']) == 12 and len(L['wd']) == 7
        assert set(L['regions']) == set(ref['regions']) and set(L['uc']) == set(ref['uc'])
