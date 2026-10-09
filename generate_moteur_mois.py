#!/usr/bin/env python3
"""
Pages « Où partir en [mois] » fusionnées avec le moteur par dates.

Remplace, pour les mois et langues listés dans data/moteur_config.json, les pages
produites par generate_piliers.py (qui les saute désormais). Le classement par
défaut (le mois entier) est écrit dans le HTML ; js/date-engine.js recalcule
quand le visiteur change ses dates ou ses critères, à partir de
engine/data-v1.json (régénéré ici).

Usage : python3 generate_moteur_mois.py
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from generate_piliers import load_destinations, load_climate, load_country_info, PILIER_LANGS, FONTS  # noqa: E402
from lib.page_config import load_locale, strip_html_from_internal_links as strip_links  # noqa: E402
from lib.common import footer_ranking_html, shared_nav_html  # noqa: E402
from lib import date_engine as E  # noqa: E402
from lib.engine_render import render_main, client_config, CSS, R, fmt, esc  # noqa: E402

CONFIG = ROOT / 'data' / 'moteur_config.json'
JS_VERSION = 1
DATA_URL = f'/engine/data-{E.DATA_VERSION}.json'


def load_config():
    c = json.load(open(CONFIG, encoding='utf-8'))
    return [m - 1 for m in c['mois']], c['langues']


TEXTS = {
    'fr': {
        'eyebrow': 'Étude climatique · 10 ans de données · 2026-2027', 'months_label': 'Autres mois', 'criteria': 'Critères',
        'your_dates': 'Vos dates', 'dep_date': 'Départ', 'ret_date': 'Retour', 'shortcuts': 'Raccourcis :',
        'zone_label': 'Votre zone scolaire', 'trip_type': 'Type de voyage', 'region': 'Région', 'from_city': 'Ville de départ',
        'max_flight': 'Temps de vol maximum :', 'heat': 'Chaleur l’après-midi', 'budget': 'Budget sur place',
        'budget_help': 'Coût de la vie, par pays (indice Numbeo 2026). Le prix du vol n’est pas compris.',
        'safety': 'Sécurité',
        'safety_help': 'Niveau du pays (le plus prudent de France Diplomatie et du ministère allemand des Affaires étrangères). Certaines régions peuvent être plus sévèrement classées : vérifiez avant de réserver.',
        'key_points': 'À retenir', 'sort_by': 'Trier par', 'more': 'Afficher 25 de plus',
        'projects_title': 'Selon votre projet',
        'projects_lead': 'Les meilleures destinations pour ces dates, par type de voyage (ville de départ, vol, budget et sécurité pris en compte).',
        'regions_lead': 'Les meilleures destinations de chaque région pour ces dates (budget et sécurité pris en compte, sans limite de vol).',
        'others_title': 'Autres classements',
        'method_title': 'Comment ce classement est calculé',
        'method': [
            'Score BestDateWeather (général, plage, ski ou randonnée) : celui des mois concernés, pondéré par le nombre de jours de votre séjour dans chaque mois.',
            'Pluie : quand l’historique quotidien existe, vos dates exactes sont rejouées sur chacune des années 2016 à 2025 (réanalyse ERA5, seuil recalé sur 318 stations météo). Sinon, le calcul part de la part de jours de pluie du mois.',
            '« Presque sec » : au plus un jour de pluie par semaine de séjour, en moyenne.',
            'Dates de vacances : calendrier scolaire officiel du ministère de l’Éducation nationale.',
        ],
        'know_title': 'Ce qu’il faut savoir',
        'know': [
            'Dix saisons, c’est un historique court : « 8 années sur 10 » veut dire « le plus souvent », pas « garanti ».',
            'Temps de vol estimé à partir de la distance (45 min + distance à 850 km/h), pour un vol direct. Avec une escale, comptez davantage.',
            'Températures issues de la réanalyse ERA5 : sur les petites îles, parfois 1 à 2 °C sous les relevés des stations côtières.',
        ],
        'holiday_title': '{chip} : où partir au soleil ?',
        'holiday_lead': 'Du {a} au {b}. Les meilleurs scores à 20 °C et plus, avec au plus 15 % de jours de pluie sur ces dates (sécurité : jusqu’à vigilance renforcée).',
        'holiday_cta': 'Voir le classement complet à ces dates',
        'title_m': 'Où partir en {m} {y} ? Top 25 destinations météo, jour par jour',
        'title_h': 'Où partir en {m} {y} et {em} ? Top 25 destinations météo',
        'desc': 'Classement de {n} destinations pour {m} {y}{h} : n°1 {top} ({s}/10, {t} °C). Calcul jour par jour sur 2016-2025, filtres dates, vol, budget et sécurité.',
        'desc_h': ' et {em}', 'crumb': 'Où partir en {m}',
        'faq_q1': 'Quelle est la meilleure destination en {m} ?', 'faq_a1': '{top} arrive en tête en {m} avec {s}/10 et {t} °C l’après-midi en moyenne.',
        'faq_q2': 'Où partir au soleil {em} ?', 'faq_a2': 'Pour les vacances du {a} au {b}, les meilleures destinations à 20 °C et plus, avec peu de pluie, sont {l}.',
        'prev': '← Où partir en {m}', 'next': 'Où partir en {m} →', 'world': '🌍 Classement mondial 2026', 'map': '🗺️ Carte climatique', 'year': '📅 Toute l’année',
    },
    'en': {
        'eyebrow': 'Climate study · 10 years of data · 2026-2027', 'months_label': 'Other months', 'criteria': 'Criteria',
        'your_dates': 'Your dates', 'dep_date': 'Departure', 'ret_date': 'Return', 'shortcuts': 'Shortcuts:',
        'zone_label': 'Your school zone', 'trip_type': 'Type of trip', 'region': 'Region', 'from_city': 'Departure city',
        'max_flight': 'Maximum flight time:', 'heat': 'Afternoon temperature', 'budget': 'Budget on the ground',
        'budget_help': 'Cost of living, by country (Numbeo 2026 index). Flights are not included.',
        'safety': 'Safety',
        'safety_help': 'Country level (the stricter of the French and German foreign ministries). Some regions may be rated more severely: check before booking.',
        'key_points': 'Key points', 'sort_by': 'Sort by', 'more': 'Show 25 more',
        'projects_title': 'Depending on your plans',
        'projects_lead': 'The best destinations for these dates, by type of trip (departure city, flight, budget and safety taken into account).',
        'regions_lead': 'The best destinations in each region for these dates (budget and safety taken into account, no flight limit).',
        'others_title': 'Other rankings',
        'method_title': 'How this ranking is calculated',
        'method': [
            'BestDateWeather score (general, beach, skiing or hiking): the score of the months concerned, weighted by the number of days of your trip in each month.',
            'Rain: where daily records exist, your exact dates are replayed on each year from 2016 to 2025 (ERA5 reanalysis, threshold adjusted to 318 weather stations). Otherwise, the calculation uses the share of rainy days in the month.',
            '"Nearly dry": at most one rainy day per week of travel, on average.',
        ],
        'know_title': 'Good to know',
        'know': [
            'Ten seasons is a short record: "8 years out of 10" means "most of the time", not "guaranteed".',
            'Flight time estimated from distance (45 min + distance at 850 km/h) for a direct flight. With a stopover, allow longer.',
            'Temperatures come from the ERA5 reanalysis: on small islands they can be 1 to 2 °C below coastal station readings.',
        ],
        'holiday_title': '{chip}: where to go for sunshine?',
        'holiday_lead': '{a} to {b}. The best scores at 20 °C and above, with at most 15% rainy days on these dates (safety: up to high vigilance).',
        'holiday_cta': 'See the full ranking for these dates',
        'title_m': 'Where to Go in {m} {y}: Top 25 Destinations by Weather',
        'title_h': 'Where to Go in {m} {y} and {em}: Top 25 by Weather',
        'desc': 'Ranking of {n} destinations for {m} {y}{h}: #1 {top} ({s}/10, {t} °C). Day-by-day calculation over 2016-2025, with date, flight, budget and safety filters.',
        'desc_h': ' and {em}', 'crumb': 'Where to go in {m}',
        'faq_q1': 'What is the best destination in {m}?', 'faq_a1': '{top} ranks first in {m} with {s}/10 and {t} °C in the afternoon on average.',
        'faq_q2': 'Where to go for sunshine {em}?', 'faq_a2': 'For {a} to {b}, the best destinations at 20 °C and above with little rain are {l}.',
        'prev': '← Where to go in {m}', 'next': 'Where to go in {m} →', 'world': '🌍 World ranking 2026', 'map': '🗺️ Climate map', 'year': '📅 All year',
    },
}


def urls(lang, loc, mi):
    sub = loc['meta']['subdir']
    base = f"{loc['pilier']['pillar_prefix']}{loc['month_url'][mi]}"
    rel = f'/{base}' if not sub else f'/{sub}/{base}'
    return rel, f'https://bestdateweather.com{rel}', (ROOT / f'{base}.html' if not sub else ROOT / sub / f'{base}.html')


def hreflang_tags(mi):
    out = {}
    for l2 in PILIER_LANGS:
        loc2 = load_locale(l2)
        out[l2] = urls(l2, loc2, mi)[1]
    lines = [f'<link rel="alternate" hreflang="{k}" href="{v}"/>' for k, v in sorted(out.items())]
    if 'en' in out:
        lines.append(f'<link rel="alternate" hreflang="x-default" href="{out["en"]}"/>')
    return '\n'.join(lines), out


def holiday_block(ds, lang, mi, r, X):
    """Bloc statique par vacances du mois (contenu lisible par Google, dates fixes)."""
    L = E.I18N[lang]
    out, faq = '', None
    for h in L['holidays'].get(str(mi), []):
        if h.get('zones'):
            continue  # zones : traitées dans les pages février et avril (étape suivante)
        st = E.default_state(mi, lang)
        st.update({'preset': h['id'], 'from': h['a'], 'to': h['b'], 'heat': 20, 'sort': 'score'})
        v = E.compute_view(ds, st, lang)
        top = [x for x in v['rows'] if x['share'] <= 0.15][:8]
        w = v['w']
        lis = ''.join('<li><span class="me-hol-n">' + str(i + 1) + '</span><span class="me-hol-d"><a href="' + r.href(x) + '">' + r.nm(x) + '</a> <span class="me-help">' + esc(x['d']['p'][r.ni]) + '</span></span><span class="me-hol-x">'
                      + esc(r.dry_txt(x, w)[:1].upper() + r.dry_txt(x, w)[1:]) + ' · ' + r.f1(x['tmax']) + ' °C · <b>' + r.f1(x['score']) + '/10</b></span></li>' for i, x in enumerate(top))
        a, b = r.long_date(h['a']), r.long_date(h['b'])
        lead = fmt(X['holiday_lead'], a=a, b=b)
        out += (f'<section class="me-sec" id="me-h-{h["id"]}"><div><h2>{esc(fmt(X["holiday_title"], chip=h["chip"]))}</h2>'
                f'<p class="me-lead">{esc(lead[0].upper() + lead[1:])}</p></div><ol class="me-hol">{lis}</ol>'
                f'<p><a class="me-link" href="#{h["id"]}">{esc(X["holiday_cta"])} →</a></p></section>')
        faq = (h, a, b, [x['d']['n'][r.ni] for x in top[:3]])
    return out, faq


def generate(mi, lang, ds):
    loc = load_locale(lang)
    gen, pil = loc['gen'], loc['pilier']
    L, X = E.I18N[lang], TEXTS[lang]
    annual_tpl = '/meilleure-periode-{s}' if lang == 'fr' else '/en/best-time-to-visit-{e}'
    r = R(lang, annual_tpl)
    st = E.default_state(mi, lang)
    view = E.compute_view(ds, st, lang)
    rel, canonical, path = urls(lang, loc, mi)
    hl_tags, _ = hreflang_tags(mi)
    month_links = [urls(lang, loc, i)[0] for i in range(12)]
    prev, nxt = (mi + 11) % 12, (mi + 1) % 12
    world = '/' + pil['world_ranking_url'].replace('.html', '') if lang == 'fr' else '/en/' + pil['world_ranking_url'].replace('.html', '')
    year_url = '/' + pil['all_year_url'].replace('.html', '') if lang == 'fr' else '/en/' + pil['all_year_url'].replace('.html', '')
    map_url = '/carte' if lang == 'fr' else '/en/map'
    others = [(fmt(X['prev'], m=L['months'][prev]), month_links[prev]), (fmt(X['next'], m=L['months'][nxt]), month_links[nxt]),
              (X['year'], year_url), (X['world'], world), (X['map'], map_url)]
    main = render_main(view, st, lang, annual_tpl, month_links, others, X)
    hol_html, faq_h = holiday_block(ds, lang, mi, r, X)
    # bloc vacances inséré juste après le classement
    main = main.replace('<section class="me-sec"><div><h2>' + esc(X['projects_title']), hol_html + '<section class="me-sec"><div><h2>' + esc(X['projects_title']), 1)

    m_name, y = L['months'][mi], int(st['from'][:4])
    m_title = m_name if lang == 'fr' else m_name
    hs = [h for h in L['holidays'].get(str(mi), []) if not h.get('zones')]
    top = view['rows'][0]
    title = fmt(X['title_h'], m=m_title, y=y, em=hs[0]['em']) if hs else fmt(X['title_m'], m=m_title, y=y)
    desc = fmt(X['desc'], n=view['n_uc'], m=m_name, y=y, h=fmt(X['desc_h'], em=hs[0]['em']) if hs else '',
               top=top['d']['n'][r.ni], s=r.f1(top['score']), t=r.r0(top['tmax']))
    canon_prefix = 'https://bestdateweather.com'
    itemlist = {'@context': 'https://schema.org', '@type': 'ItemList', 'name': title, 'numberOfItems': min(25, len(view['rows'])),
                'itemListElement': [{'@type': 'ListItem', 'position': i + 1, 'name': x['d']['n'][r.ni], 'url': canon_prefix + r.href(x)}
                                    for i, x in enumerate(view['rows'][:25])]}
    crumb = {'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [
        {'@type': 'ListItem', 'position': 1, 'name': loc['labels']['breadcrumb_home'], 'item': loc['meta']['schema_home_url']},
        {'@type': 'ListItem', 'position': 2, 'name': fmt(X['crumb'], m=m_name), 'item': canonical}]}
    faq_items = [{'@type': 'Question', 'name': fmt(X['faq_q1'], m=m_name),
                  'acceptedAnswer': {'@type': 'Answer', 'text': fmt(X['faq_a1'], m=m_name, top=top['d']['n'][r.ni], s=r.f1(top['score']), t=r.r0(top['tmax']))}}]
    if faq_h:
        h, a, b, names = faq_h
        lst = ', '.join(names[:-1]) + (' et ' if lang == 'fr' else ' and ') + names[-1] if len(names) > 1 else (names[0] if names else '')
        faq_items.append({'@type': 'Question', 'name': fmt(X['faq_q2'], em=h['em']),
                          'acceptedAnswer': {'@type': 'Answer', 'text': fmt(X['faq_a2'], a=a, b=b, l=lst)}})
    faq = {'@context': 'https://schema.org', '@type': 'FAQPage', 'mainEntity': faq_items}
    ld = lambda o: json.dumps(o, ensure_ascii=False).replace('</', '<\\/')
    cross = []
    for l2 in PILIER_LANGS:
        if l2 == lang:
            continue
        loc2 = load_locale(l2)
        cross.append({'url': urls(l2, loc2, mi)[0], 'flag': f'/{loc2["meta"]["flag"]}', 'label': loc2['meta']['lang_label']})
    nav = shared_nav_html(gen['home_url'], gen['try_app_label'], gen['share_label'], map_href=pil.get('map_href', ''), map_label=pil.get('map_nav_label', ''))
    cfg = client_config(lang, st, DATA_URL, annual_tpl)
    html = f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="UTF-8"/><meta name="viewport" content="width=device-width,initial-scale=1.0"/>
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}"/>
<link rel="canonical" href="{canonical}"/>
{hl_tags}
<meta property="og:type" content="article"/>
<meta property="og:title" content="{esc(title)}"/>
<meta property="og:description" content="{esc(desc)}"/>
<meta property="og:url" content="{canonical}"/>
{FONTS}
<link rel="stylesheet" href="{gen['asset_prefix']}style.css"/>
<style>{CSS}</style>
<script type="application/ld+json">{ld(crumb)}</script>
<script type="application/ld+json">{ld(itemlist)}</script>
<script type="application/ld+json">{ld(faq)}</script>
</head>
<body>
{nav}
{main}
{footer_ranking_html(lang, cross)}
<script>window.BDW_ENGINE={cfg};</script>
<script src="/js/date-engine.js?v={JS_VERSION}" defer></script>
<script src="{gen['asset_prefix']}js/share.js" defer></script>
</body></html>"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(strip_links(html), encoding='utf-8')
    return path, len(view['rows'])


def main():
    months, langs = load_config()
    dests, climate, ci = load_destinations(), load_climate(), load_country_info()
    ds = E.build_dataset(dests, climate, ci)
    p = E.write_dataset(ds)
    print(f'{p.relative_to(ROOT)} : {len(ds)} destinations, {sum(1 for x in ds if "r" in x)} avec historique quotidien')
    for lang in langs:
        for mi in months:
            path, n = generate(mi, lang, ds)
            print(f'  ✅ {path.relative_to(ROOT)} ({n} destinations classées par défaut)')


if __name__ == '__main__':
    main()
