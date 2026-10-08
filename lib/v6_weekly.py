"""
Section « Semaine par semaine » des pages annuelles (plan B, phase 3).

Ce que le site est seul à proposer : la fréquence, sur 10 ans, des semaines
plutôt sèches (au plus 2 jours de pluie >= 1 mm) pour chaque semaine de l'année. Jusqu'ici ce calcul n'existait
que dans l'application (JavaScript, invisible pour Google) ; il est ici rendu
en HTML à partir de data/weekly/{slug_fr}.json, produit par
scripts/fetch_weekly_history.py (ERA5 via Open-Meteo, 2016-2025).

Rien n'est rendu si le fichier de données n'existe pas.
"""

import json
import os
from html import escape as h

_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'weekly')

_MONTHS = {
    'fr': ['janv.', 'févr.', 'mars', 'avr.', 'mai', 'juin', 'juil.', 'août', 'sept.', 'oct.', 'nov.', 'déc.'],
    'en': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
    'es': ['ene.', 'feb.', 'mar.', 'abr.', 'may.', 'jun.', 'jul.', 'ago.', 'sept.', 'oct.', 'nov.', 'dic.'],
    'de': ['Jan.', 'Feb.', 'März', 'Apr.', 'Mai', 'Juni', 'Juli', 'Aug.', 'Sept.', 'Okt.', 'Nov.', 'Dez.'],
}
_MONTHS['en-us'] = _MONTHS['en']
_MONTHS_FULL = {
    'fr': ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre'],
    'en': ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'],
    'es': ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'],
    'de': ['Januar', 'Februar', 'März', 'April', 'Mai', 'Juni', 'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember'],
}
_MONTHS_FULL['en-us'] = _MONTHS_FULL['en']

_L = {
    'fr': {
        'kicker': 'Semaine par semaine',
        'h2': '{dest} semaine par semaine : vos chances d\'éviter la pluie',
        'lead': 'Pour chaque semaine de l\'année : combien d\'années sur 10 elle a été plutôt sèche (au plus 2 jours de pluie), de 2016 à 2025.',
        'best': 'Semaine la plus sûre : du {a} au {b}, plutôt sèche {n} années sur 10 ({r} jour(s) de pluie en moyenne).',
        'worst': 'La plus exposée : du {a} au {b}, plutôt sèche {n} années sur 10 ({r} jours de pluie en moyenne).',
        'cell_title': 'Du {a} au {b} : plutôt sèche {n} années sur 10, {r} jour(s) de pluie en moyenne, {t} en journée',
        'legend': 'Chiffre = années sur 10 avec au plus 2 jours de pluie dans la semaine.',
        'source': 'Source : réanalyse ERA5 (ECMWF) via Open-Meteo, données quotidiennes 2016-2025. Jour de pluie = au moins 1 mm, comme dans le reste du site.',
        'app': 'Une date précise ? L\'application calcule le même indicateur jour par jour.',
        'app_href': './',
        'week': 'Semaine',
    },
    'en': {
        'kicker': 'Week by week',
        'h2': '{dest} week by week: your odds of avoiding rain',
        'lead': 'For each week of the year: in how many years out of 10 it was mostly dry (at most 2 rainy days), 2016 to 2025.',
        'best': 'Safest week: {a} to {b}, mostly dry in {n} years out of 10 ({r} rainy day(s) on average).',
        'worst': 'Most exposed: {a} to {b}, mostly dry in {n} years out of 10 ({r} rainy days on average).',
        'cell_title': '{a} to {b}: mostly dry in {n} years out of 10, {r} rainy day(s) on average, {t} by day',
        'legend': 'Number = years out of 10 with at most 2 rainy days in the week.',
        'source': 'Source: ERA5 reanalysis (ECMWF) via Open-Meteo, daily data 2016-2025. Rainy day = at least 1 mm, as everywhere on the site.',
        'app': 'A specific date? The app computes the same figure day by day.',
        'app_href': 'app',
        'week': 'Week',
    },
    'es': {
        'kicker': 'Semana a semana',
        'h2': '{dest} semana a semana: tus probabilidades de evitar la lluvia',
        'lead': 'Para cada semana del año: cuántos años de 10 fue más bien seca (como mucho 2 días de lluvia), de 2016 a 2025.',
        'best': 'Semana más segura: del {a} al {b}, más bien seca {n} años de 10 ({r} día(s) de lluvia de media).',
        'worst': 'La más expuesta: del {a} al {b}, más bien seca {n} años de 10 ({r} días de lluvia de media).',
        'cell_title': 'Del {a} al {b}: más bien seca {n} años de 10, {r} día(s) de lluvia de media, {t} de día',
        'legend': 'Cifra = años de 10 con como mucho 2 días de lluvia en la semana.',
        'source': 'Fuente: reanálisis ERA5 (ECMWF) vía Open-Meteo, datos diarios 2016-2025. Día de lluvia = al menos 1 mm, como en el resto del sitio.',
        'app': '¿Una fecha concreta? La aplicación calcula el mismo indicador día a día.',
        'app_href': 'app',
        'week': 'Semana',
    },
    'de': {
        'kicker': 'Woche für Woche',
        'h2': '{dest} Woche für Woche: Ihre Chancen, dem Regen zu entgehen',
        'lead': 'Für jede Woche des Jahres: in wie vielen von 10 Jahren sie überwiegend trocken war (höchstens 2 Regentage), 2016 bis 2025.',
        'best': 'Sicherste Woche: {a} bis {b}, überwiegend trocken in {n} von 10 Jahren (im Schnitt {r} Regentag(e)).',
        'worst': 'Am stärksten betroffen: {a} bis {b}, überwiegend trocken in {n} von 10 Jahren (im Schnitt {r} Regentage).',
        'cell_title': '{a} bis {b}: überwiegend trocken in {n} von 10 Jahren, im Schnitt {r} Regentag(e), {t} tagsüber',
        'legend': 'Zahl = Jahre von 10 mit höchstens 2 Regentagen in der Woche.',
        'source': 'Quelle: ERA5-Reanalyse (ECMWF) über Open-Meteo, Tageswerte 2016-2025. Regentag = mindestens 1 mm, wie überall auf der Website.',
        'app': 'Ein bestimmtes Datum? Die App berechnet denselben Wert Tag für Tag.',
        'app_href': 'app',
        'week': 'Woche',
    },
}
_L['en-us'] = dict(_L['en'])


def load_weekly(slug_fr: str):
    p = os.path.join(_DIR, f'{slug_fr}.json')
    if not os.path.exists(p):
        return None
    try:
        with open(p, encoding='utf-8') as f:
            d = json.load(f)
        return d if len(d.get('weeks', [])) == 52 else None
    except Exception:
        return None


def _fmt_day(mmdd: str, lang: str) -> str:
    m, d = int(mmdd[:2]), int(mmdd[3:5])
    mon = _MONTHS.get(lang, _MONTHS['fr'])[m - 1]
    if lang in ('en', 'en-us'):
        return f'{mon} {d}'
    if lang == 'de':
        return f'{d}. {mon}'
    return f'{d} {mon}'


def _fmt_num(x: float, lang: str) -> str:
    s = f'{x:.1f}'
    return s.replace('.', ',') if lang in ('fr', 'es', 'de') else s


def _fmt_t(c: float, lang: str) -> str:
    return f'{round(c * 9 / 5 + 32)}°F' if lang == 'en-us' else f'{round(c)}°C'


def _color(n: int):
    if n >= 7:
        return '#1a7a4a', 'rgba(26,122,74,.12)'
    if n >= 4:
        return '#8a6508', 'rgba(184,134,11,.14)'
    return '#b91c1c', 'rgba(185,28,28,.10)'


def render_v6_weekly(slug_fr: str, lang: str, dest_name: str, asset_prefix: str = '') -> str:
    data = load_weekly(slug_fr)
    if not data:
        return ''
    L = _L.get(lang, _L['fr'])
    weeks = data['weeks']

    # Semaine la plus sûre / la plus exposée (départage : moins de jours de pluie)
    best = max(weeks, key=lambda w: (w['dry_weeks'], -w['rain_days']))
    worst = min(weeks, key=lambda w: (w['dry_weeks'], -w['rain_days']))
    best_txt = L['best'].format(a=_fmt_day(best['from'], lang), b=_fmt_day(best['to'], lang),
                                n=best['dry_weeks'], r=_fmt_num(best['rain_days'], lang))
    worst_txt = ''
    if worst['dry_weeks'] < best['dry_weeks']:
        worst_txt = L['worst'].format(a=_fmt_day(worst['from'], lang), b=_fmt_day(worst['to'], lang),
                                      n=worst['dry_weeks'], r=_fmt_num(worst['rain_days'], lang))

    # Grille : une ligne par mois, une cellule par semaine commençant ce mois-là
    months_short = _MONTHS.get(lang, _MONTHS['fr'])
    rows = []
    for mi in range(12):
        cells = []
        for w in weeks:
            if int(w['from'][:2]) != mi + 1:
                continue
            fg, bg = _color(w['dry_weeks'])
            title = L['cell_title'].format(a=_fmt_day(w['from'], lang), b=_fmt_day(w['to'], lang),
                                           n=w['dry_weeks'], r=_fmt_num(w['rain_days'], lang),
                                           t=_fmt_t(w['tmax'], lang))
            cells.append(
                f'<td title="{h(title)}" style="background:{bg};color:{fg};text-align:center;'
                f'padding:5px 2px;border-radius:8px;min-width:44px">'
                f'<span style="display:block;font-size:10px;color:#6b7280;font-weight:600">'
                f'{h(_fmt_day(w["from"], lang))}</span>'
                f'<strong style="font-size:15px">{w["dry_weeks"]}/10</strong>'
                f'<span style="display:block;font-size:10px;color:#6b7280">{h(_fmt_t(w["tmax"], lang))}</span>'
                f'</td>')
        while len(cells) < 5:
            cells.append('<td></td>')
        rows.append(f'<tr><th scope="row" style="text-align:left;font-size:12px;font-weight:700;'
                    f'color:#1a2230;padding-right:6px;white-space:nowrap">{h(months_short[mi])}</th>'
                    + ''.join(cells) + '</tr>')

    h2 = L['h2'].format(dest=dest_name)
    # Liens relatifs au dossier de langue : FR -> './' (accueil = application),
    # autres langues -> 'app' (en/app, es/app...). asset_prefix ne sert pas ici.
    app_href = L['app_href']
    return f'''  <section id="semaines">
    <div class="container">
      <div class="section-head">
        <div class="section-kicker">{h(L['kicker'])}</div>
        <h2>{h(h2)}</h2>
        <p class="lead">{h(L['lead'])}</p>
      </div>
      <div class="card pad">
        <p style="margin:0 0 6px"><strong>{h(best_txt)}</strong></p>
        {f'<p style="margin:0 0 14px">{h(worst_txt)}</p>' if worst_txt else ''}
        <div style="overflow-x:auto">
          <table style="border-collapse:separate;border-spacing:4px;width:100%;font-variant-numeric:tabular-nums">
            <caption style="caption-side:bottom;text-align:left;font-size:11px;color:#6b7280;padding-top:8px">{h(L['legend'])} {h(L['source'])}</caption>
            <tbody>
              {''.join(rows)}
            </tbody>
          </table>
        </div>
        <p style="margin:12px 0 0;font-size:13px"><a href="{h(app_href)}" style="color:#b8860b;font-weight:600;text-decoration:none;border-bottom:1px solid #f5d060">{h(L['app'])}</a></p>
      </div>
    </div>
  </section>'''
