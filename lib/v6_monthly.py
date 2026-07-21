"""
lib/v6_monthly.py — Blocs V6 spécifiques aux pages MENSUELLES.

Les pages annuelles utilisent lib/v6.py (decider-grid sur 12 mois, méthodologie,
trend chart). Les pages mensuelles ont un contenu différent : le score d'UN mois,
sa comparaison au meilleur mois, etc.

Ce module fournit les 2 blocs propres au monthly, dans le MÊME langage visuel V6
(hero-shell, decision-card, section-kicker/head, cards) :
  - render_v6_monthly_hero()      : hero avec le score du mois consulté
  - render_v6_monthly_vs_best()   : section "[Mois] vs meilleur mois"

Tous les autres blocs (contexte, FAQ, réserver, explorer, localisation, infos
pratiques, topbar, footer, head, scripts) sont RÉUTILISÉS depuis lib/v6.py.
"""

from html import escape as h
from lib.v6 import _v6_strings, _coord_label, _hero_chip


def _verdict_from_score(score):
    """Retourne (clé_verdict, clé_lead) selon le score /10."""
    if score >= 8.0:
        return 'go', 'excellent'
    if score >= 6.5:
        return 'go', 'good'
    if score >= 4.5:
        return 'maybe', 'mixed'
    return 'avoid', 'poor'


def _verdict_color(verdict_key):
    """Couleur de la pastille verdict."""
    return {'go': '#1a9e5c', 'maybe': '#d68a00', 'avoid': '#c0392b'}.get(verdict_key, '#6b7280')


def render_v6_monthly_hero(slug, lang, hero_data, asset_prefix=''):
    """Hero V6 pour une page mensuelle.

    Reprend exactement la structure CSS V6 (hero-wrap/shell/grid/decision-card/
    mini-grid) mais affiche le score DU MOIS consulté, pas le meilleur mois.

    hero_data attendu :
        - dest_name (str)        : 'Paris'
        - mois (str)             : 'Juillet' (localisé)
        - country_name (str)     : 'France'
        - country_iso (str)      : 'fr'
        - climate_type (str)     : 'Climat océanique'
        - score (float)          : 8.7  (score du mois /10)
        - tmin, tmax (float)     : pour le mini-card température
        - rain_pct (float)       : pour le mini-card pluie
        - sun_h (float)          : pour le mini-card soleil
        - lat, lon (float)
        - photo_url (str)
        - photo_credit (str)     : HTML autorisé
        - update_month (str)     : mois courant localisé (pour le tag MAJ)
        - chips (list)           : [{'emoji','text','color'}]  (optionnel)
    """
    L = _v6_strings(lang)['monthly']
    d = hero_data
    nom = d['dest_name']
    mois = d['mois']
    score = d.get('score', 0) or 0

    verdict_key, lead_key = _verdict_from_score(score)
    verdict_label = L[f'quick_verdict_{verdict_key}']
    verdict_col = _verdict_color(verdict_key)

    nom_h = h(nom)
    # Casse du mois selon la langue : FR/ES en minuscule en milieu de phrase,
    # EN (mois toujours capitalisés) et DE (noms communs capitalisés) gardent la majuscule.
    if lang in ('fr', 'es'):
        mois_inline = mois[0].lower() + mois[1:] if mois else mois
    else:
        mois_inline = mois
    mois_h = h(mois_inline)
    country_h = h(d.get('country_name', ''))
    climate_h = h(d.get('climate_type', ''))
    iso = d.get('country_iso', '').lower()
    score_str = f'{score:.1f}'

    # H1 : "Paris en juillet : partir ou pas ?"
    h1_html = L['h1_tpl'].format(nom=nom_h, mois=mois_h)
    h1_html = h1_html.replace('<em>', '<span class="accent">').replace('</em>', '</span>')

    # Lead selon verdict
    lead_html = L[f'lead_verdict_{lead_key}'].format(nom=nom_h, mois=mois_h, score=score_str)

    # Eyebrow
    eyebrow = (f'<img src="{asset_prefix}flags/{iso}.png" alt=""/>{nom_h}, {country_h} · {climate_h}'
               if iso and country_h
               else f'{nom_h} · {climate_h}')

    # Tags hero-meta
    update_lbl = L['tag_update'].format(month=h(d.get('update_month', '—')))
    coords_lbl = _coord_label(d.get('lat', 0), d.get('lon', 0))

    # Mini-cards : Température / Pluie / Soleil (les 3 données clés du mois)
    tmin = d.get('tmin')
    tmax = d.get('tmax')
    rain = d.get('rain_pct')
    sun = d.get('sun_h')
    temp_v = (f'{int(round(tmin))}–{int(round(tmax))}°'
              if tmin is not None and tmax is not None else '—')
    rain_v = f'{int(round(rain))}%' if rain is not None else '—'
    sun_v = f'{sun:.0f}h' if sun is not None else '—'
    mini_cards = [
        {'value': temp_v, 'label': L['mini_temp']},
        {'value': rain_v, 'label': L['mini_rain']},
        {'value': sun_v,  'label': L['mini_sun']},
    ]
    mini_html = ''.join(
        f'<div class="mini-card"><div class="v">{h(c["value"])}</div>'
        f'<div class="l">{h(c["label"])}</div></div>'
        for c in mini_cards
    )

    # Chips climat (optionnel)
    chips = d.get('chips', [])
    chips_html = ''.join(
        _hero_chip(c.get('emoji', '·'), c.get('text', ''), c.get('color', 'blue'))
        for c in chips
    )
    chips_block = (f'<div style="display:flex;flex-wrap:wrap;gap:6px;margin-top:12px">'
                   f'{chips_html}</div>') if chips_html else ''

    # Photo
    photo_url = d.get('photo_url', '')
    bg_style = (f' style="background-image:url(\'{h(photo_url)}\')"' if photo_url else '')
    photo_credit = d.get('photo_credit', '')
    photo_credit_block = (f'<div class="hero-photo-credit">Photo : {photo_credit}</div>'
                          if photo_credit else '')

    return (
        f'<header class="hero-wrap">\n'
        f'  <div class="container">\n'
        f'    <div class="hero-shell"{bg_style}>\n'
        f'      <div class="hero-grid">\n'
        f'        <div class="hero-main">\n'
        f'          <div class="eyebrow">{eyebrow}</div>\n'
        f'          <h1>{h1_html}</h1>\n'
        f'          <p class="hero-lead">{lead_html}</p>\n'
        f'          <div class="hero-meta">\n'
        f'            <span>📅 {h(update_lbl)}</span>\n'
        f'            <span>🛰️ {h(L["tag_data"])}</span>\n'
        f'            <span>📍 {coords_lbl}</span>\n'
        f'          </div>\n'
        f'        </div>\n'
        f'        <div class="hero-side">\n'
        f'          <div class="decision-card">\n'
        f'            <div class="small-label">⚡ {h(L["quick_label"])}</div>\n'
        f'            <div class="decision-top">\n'
        f'              <div>\n'
        f'                <div class="month" style="color:{verdict_col}">{h(verdict_label)}</div>\n'
        f'                <div class="sub">{nom_h} · {mois_h}</div>\n'
        f'              </div>\n'
        f'              <div class="score">{score_str}</div>\n'
        f'            </div>\n'
        f'            <div class="mini-grid">{mini_html}</div>\n'
        f'            {chips_block}\n'
        f'          </div>\n'
        f'          {photo_credit_block}\n'
        f'        </div>\n'
        f'      </div>\n'
        f'    </div>\n'
        f'  </div>\n'
        f'</header>'
    )


def render_v6_monthly_vs_best(slug, lang, vs_data):
    """Section "Ce mois vs meilleur mois" (signature visuelle V6 : section-kicker/head).

    vs_data :
        - mois (str)              : mois consulté localisé
        - dest_name (str)
        - is_best (bool)          : True si le mois consulté EST le meilleur
        - best_month (str)        : meilleur mois localisé
        - best_score (float)
        - this_score (float)
        - best_href (str)         : lien vers la fiche du meilleur mois (sans .html)
        - annual_href (str)       : lien vers la fiche annuelle (sans .html)
    """
    L = _v6_strings(lang)['monthly']
    d = vs_data
    nom_h = h(d['dest_name'])
    mois_raw = d['mois']
    # Titre commence par le mois → capitale. Body en milieu de phrase → minuscule (FR/ES).
    mois_title = h(mois_raw)
    if lang in ('fr', 'es') and mois_raw:
        mois_inline = h(mois_raw[0].lower() + mois_raw[1:])
    else:
        mois_inline = h(mois_raw)

    title = L['vs_title_tpl'].format(mois=mois_title)

    if d.get('is_best'):
        body = L['vs_same_best'].format(mois=mois_title, nom=nom_h)
        cta = (f'<a href="{h(d.get("annual_href", "#"))}" class="vs-cta">'
               f'{h(L["vs_see_annual"])} →</a>')
    else:
        delta = abs(d.get('best_score', 0) - d.get('this_score', 0))
        delta_str = f'{delta:.1f} pt' + ('s' if delta >= 2 else '')
        body = L['vs_better_exists'].format(
            nom=nom_h, best_month=h(d.get('best_month', '')),
            best_score=f'{d.get("best_score", 0):.1f}', mois=mois_inline, delta=delta_str)
        cta = (f'<a href="{h(d.get("best_href", "#"))}" class="vs-cta">'
               f'{h(L["vs_see_best"].format(best_month=d.get("best_month", "")))} →</a>'
               f'<a href="{h(d.get("annual_href", "#"))}" class="vs-cta vs-cta-ghost">'
               f'{h(L["vs_see_annual"])} →</a>')

    # Style inline (cohérent V6, hex pur)
    return (
        f'<section class="section">\n'
        f'  <div class="container">\n'
        f'    <div class="section-head">\n'
        f'      <div class="section-kicker">{h(L["vs_kicker"])}</div>\n'
        f'      <h2>{title}</h2>\n'
        f'    </div>\n'
        f'    <div class="vs-card" style="background:#fff;border:1px solid #e6e8eb;'
        f'border-radius:16px;padding:22px 24px;border-left:4px solid #1a2230">\n'
        f'      <p style="margin:0 0 14px;font-size:16px;line-height:1.6;color:#1a2230">{body}</p>\n'
        f'      <div style="display:flex;flex-wrap:wrap;gap:10px">{cta}</div>\n'
        f'    </div>\n'
        f'  </div>\n'
        f'</section>'
    )


def render_v6_monthly_explore(slug, lang, explore_data, asset_prefix=''):
    """Section "Explorer ce mois" : cross-links MENSUELS (design V6).

    Reproduit les 3 blocs de cross-link du V5 mais avec les liens vers les
    pages DU MÊME MOIS (pas annuelles), dans le langage visuel V6 (3 boxes).

    explore_data :
        - mois (str)           : mois localisé
        - prev_month (dict)    : {'name','href'} mois précédent
        - next_month (dict)    : {'name','href'} mois suivant
        - similar (list)       : [{'name','href','country','iso'}] climat similaire ce mois
        - nearby (list)        : [{'name','href','country','iso','distance_km'}] proches ce mois
        - other_top (list)     : [{'name','href','country','iso','score'}] autres top ce mois
        - map_href (str)       : lien carte
    """
    L = _v6_strings(lang)['monthly']
    d = explore_data
    mois = d['mois']

    # i18n
    I = {
        'fr': {'kicker': 'Explorer', 'title_tpl': 'Autres destinations en {mois}',
               'lead_tpl': 'Si {mois} ne vous convainc pas pour cette destination, comparez avec d\'autres.',
               'box_similar': 'Climat similaire', 'box_nearby': 'À proximité',
               'box_other': 'Autres tops du mois', 'box_nav': 'Mois adjacents',
               'prev_lbl': 'Mois précédent', 'next_lbl': 'Mois suivant',
               'map_lbl': '🗺️ Voir les 754 destinations sur la carte', 'see': '→'},
        'en': {'kicker': 'Explore', 'title_tpl': 'Other destinations in {mois}',
               'lead_tpl': 'If {mois} doesn\'t convince you for this destination, compare with others.',
               'box_similar': 'Similar climate', 'box_nearby': 'Nearby',
               'box_other': 'Other top picks', 'box_nav': 'Adjacent months',
               'prev_lbl': 'Previous month', 'next_lbl': 'Next month',
               'map_lbl': '🗺️ See all 754 destinations on the map', 'see': '→'},
        'en-us': {'kicker': 'Explore', 'title_tpl': 'Other destinations in {mois}',
               'lead_tpl': 'If {mois} doesn\'t convince you for this destination, compare with others.',
               'box_similar': 'Similar climate', 'box_nearby': 'Nearby',
               'box_other': 'Other top picks', 'box_nav': 'Adjacent months',
               'prev_lbl': 'Previous month', 'next_lbl': 'Next month',
               'map_lbl': '🗺️ See all 754 destinations on the map', 'see': '→'},
        'es': {'kicker': 'Explorar', 'title_tpl': 'Otros destinos en {mois}',
               'lead_tpl': 'Si {mois} no te convence para este destino, compara con otros.',
               'box_similar': 'Clima similar', 'box_nearby': 'Cerca',
               'box_other': 'Otros destacados', 'box_nav': 'Meses adyacentes',
               'prev_lbl': 'Mes anterior', 'next_lbl': 'Mes siguiente',
               'map_lbl': '🗺️ Ver los 754 destinos en el mapa', 'see': '→'},
        'de': {'kicker': 'Entdecken', 'title_tpl': 'Andere Reiseziele im {mois}',
               'lead_tpl': 'Wenn {mois} Sie für dieses Ziel nicht überzeugt, vergleichen Sie mit anderen.',
               'box_similar': 'Ähnliches Klima', 'box_nearby': 'In der Nähe',
               'box_other': 'Weitere Top-Ziele', 'box_nav': 'Angrenzende Monate',
               'prev_lbl': 'Vorheriger Monat', 'next_lbl': 'Nächster Monat',
               'map_lbl': '🗺️ Alle 754 Reiseziele auf der Karte', 'see': '→'},
    }
    t = I.get(lang, I['en'])

    # Casse mois (FR/ES minuscule)
    mois_inline = (mois[0].lower() + mois[1:]) if (lang in ('fr', 'es') and mois) else mois

    def _link_item(item, extra=''):
        iso = item.get('iso', '').lower()
        flag = f'<img src="{asset_prefix}flags/{iso}.png" alt="" style="width:18px;height:13px;border-radius:2px;flex-shrink:0"/>' if iso else ''
        country = h(item.get('country', ''))
        extra_html = f'<span style="color:#9ca3af;font-size:12px;margin-left:auto">{h(extra)}</span>' if extra else ''
        return (
            f'<a href="{h(item["href"])}" style="display:flex;align-items:center;gap:8px;'
            f'padding:9px 0;text-decoration:none;color:#1a2230;border-bottom:1px solid #f0f1f3;font-size:14px">'
            f'{flag}<span>{h(item["name"])}</span>'
            f'<span style="color:#9ca3af;font-size:12px">{country}</span>{extra_html}</a>'
        )

    boxes = []

    # Box 1 : Climat similaire
    if d.get('similar'):
        items = ''.join(_link_item(it) for it in d['similar'][:5])
        boxes.append(
            f'<div class="explore-box" style="background:#fff;border:1px solid #e6e8eb;'
            f'border-radius:14px;padding:16px 18px">'
            f'<div style="font-weight:700;font-size:13px;color:#1a2230;margin-bottom:8px;'
            f'text-transform:uppercase;letter-spacing:.5px">{h(t["box_similar"])}</div>{items}</div>'
        )

    # Box 2 : À proximité
    if d.get('nearby'):
        items = ''.join(
            _link_item(it, extra=f'{it["distance_km"]} km' if it.get('distance_km') else '')
            for it in d['nearby'][:5])
        boxes.append(
            f'<div class="explore-box" style="background:#fff;border:1px solid #e6e8eb;'
            f'border-radius:14px;padding:16px 18px">'
            f'<div style="font-weight:700;font-size:13px;color:#1a2230;margin-bottom:8px;'
            f'text-transform:uppercase;letter-spacing:.5px">{h(t["box_nearby"])}</div>{items}</div>'
        )

    # Box 3 : Autres tops du mois
    if d.get('other_top'):
        items = ''.join(
            _link_item(it, extra=f'{it["score"]:.1f}' if it.get('score') else '')
            for it in d['other_top'][:5])
        boxes.append(
            f'<div class="explore-box" style="background:#fff;border:1px solid #e6e8eb;'
            f'border-radius:14px;padding:16px 18px">'
            f'<div style="font-weight:700;font-size:13px;color:#1a2230;margin-bottom:8px;'
            f'text-transform:uppercase;letter-spacing:.5px">{h(t["box_other"])}</div>{items}</div>'
        )

    if not boxes:
        return ''

    boxes_html = ''.join(boxes)

    # Navigation mois adjacents (prev/next) + carte
    nav_items = []
    if d.get('prev_month'):
        nav_items.append(
            f'<a href="{h(d["prev_month"]["href"])}" class="month-nav-btn" '
            f'style="display:inline-flex;align-items:center;gap:6px;padding:10px 16px;'
            f'background:#fff;border:1px solid #d0d4da;border-radius:10px;text-decoration:none;'
            f'color:#1a2230;font-weight:600;font-size:14px">← {h(d["prev_month"]["name"])}</a>')
    if d.get('next_month'):
        nav_items.append(
            f'<a href="{h(d["next_month"]["href"])}" class="month-nav-btn" '
            f'style="display:inline-flex;align-items:center;gap:6px;padding:10px 16px;'
            f'background:#fff;border:1px solid #d0d4da;border-radius:10px;text-decoration:none;'
            f'color:#1a2230;font-weight:600;font-size:14px">{h(d["next_month"]["name"])} →</a>')
    nav_html = (f'<div style="display:flex;gap:10px;flex-wrap:wrap;margin-top:16px">{"".join(nav_items)}</div>'
                if nav_items else '')

    map_html = ''
    if d.get('map_href'):
        map_html = (
            f'<a href="{h(d["map_href"])}" style="display:inline-block;margin-top:14px;'
            f'padding:11px 18px;background:#1a2230;color:#fff;text-decoration:none;'
            f'border-radius:10px;font-weight:600;font-size:14px">{h(t["map_lbl"])}</a>')

    return (
        f'<section class="section">\n'
        f'  <div class="container">\n'
        f'    <div class="section-head">\n'
        f'      <div class="section-kicker">{h(t["kicker"])}</div>\n'
        f'      <h2>{h(t["title_tpl"].format(mois=mois_inline))}</h2>\n'
        f'      <p style="color:#6b7280;font-size:15px;margin:6px 0 0">{h(t["lead_tpl"].format(mois=mois_inline))}</p>\n'
        f'    </div>\n'
        f'    <div class="explore-grid" style="display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:14px">\n'
        f'      {boxes_html}\n'
        f'    </div>\n'
        f'    {nav_html}\n'
        f'    {map_html}\n'
        f'  </div>\n'
        f'</section>'
    )


# CSS additionnel pour .vs-cta (injecté dans le head V6 via gen_monthly_v6)
VS_CTA_CSS = (
    '.vs-cta{display:inline-block;padding:10px 18px;background:#1a2230;color:#fff;'
    'text-decoration:none;border-radius:10px;font-weight:600;font-size:14px;'
    'transition:opacity .15s}'
    '.vs-cta:hover{opacity:.85}'
    '.vs-cta-ghost{background:transparent;color:#1a2230;border:1px solid #d0d4da}'
)


def render_v6_monthly_expect(slug, lang, expect_data):
    """Section "À quoi s'attendre ce mois" (signature visuelle V6).

    Reprend le contenu riche du V5 (températures, soleil, pluie, événement,
    conseil) dans une card V6.

    expect_data :
        - mois (str)         : mois localisé (capitale, début de titre)
        - paragraph_html (str) : le paragraphe descriptif (HTML autorisé)
    """
    L = _v6_strings(lang)['monthly']
    mois = expect_data['mois']
    para = expect_data.get('paragraph_html', '')
    if not para:
        return ''

    # Titre i18n "À quoi s'attendre en {mois}"
    titles = {
        'fr': f'À quoi s\'attendre en {mois.lower() if mois else mois}',
        'en': f'What to expect in {mois}',
        'en-us': f'What to expect in {mois}',
        'es': f'Qué esperar en {mois.lower() if mois else mois}',
        'de': f'Was Sie im {mois} erwartet',
    }
    kickers = {'fr': 'Le mois en détail', 'en': 'The month in detail',
               'en-us': 'The month in detail', 'es': 'El mes en detalle',
               'de': 'Der Monat im Detail'}
    title = titles.get(lang, titles['en'])
    kicker = kickers.get(lang, kickers['en'])

    return (
        f'<section class="section">\n'
        f'  <div class="container">\n'
        f'    <div class="section-head">\n'
        f'      <div class="section-kicker">{h(kicker)}</div>\n'
        f'      <h2>{h(title)}</h2>\n'
        f'    </div>\n'
        f'    <div class="expect-card" style="background:#fff;border:1px solid #e6e8eb;'
        f'border-radius:16px;padding:22px 24px;font-size:16px;line-height:1.7;color:#1a2230">\n'
        f'      {para}\n'
        f'    </div>\n'
        f'  </div>\n'
        f'</section>'
    )


# ═════════════════════════════════════════════════════════════════════════════
# Enrichissement contenu distinctif par mois (juillet 2026)
# Contexte SEO : les 12 pages mensuelles d'une destination partageaient 85% de
# vocabulaire (36 mots distinctifs seulement) → signal "contenu dupliqué" pour
# Google (67k pages 'Explorée, actuellement non indexée'). Ces sections
# exploitent les données du CSV variables par mois (UV, ressenti, mer, heures
# de jour, rang, deltas) : contenu réel, différent chaque mois par construction.
# ═════════════════════════════════════════════════════════════════════════════

import math


def _daylight_hours(lat: float, month_idx: int) -> float:
    """Durée du jour (h) au 15 du mois, formule de déclinaison solaire standard."""
    day_of_year = [15, 46, 74, 105, 135, 166, 196, 227, 258, 288, 319, 349][month_idx]
    decl = math.radians(23.45) * math.sin(math.radians(360 / 365 * (284 + day_of_year)))
    lat_r = math.radians(max(-66.5, min(66.5, lat)))  # clamp cercles polaires
    x = -math.tan(lat_r) * math.tan(decl)
    x = max(-1.0, min(1.0, x))
    return round(24 / math.pi * math.acos(x), 1)


_DETAILS_I18N = {
    'fr': {
        'kicker': 'Conditions du mois', 'title_tpl': 'En pratique en {mois}',
        'uv': 'Indice UV', 'feel': 'Ressenti', 'sea': 'Mer', 'day': 'Durée du jour',
        'air': 'Qualité de l\'air',
        'uv_lbl': ['faible', 'modéré', 'élevé', 'très élevé', 'extrême'],
        'uv_tip': ['protection inutile', 'protection aux heures centrales',
                   'crème et chapeau recommandés', 'protection indispensable', 'éviter le soleil de midi'],
        'feel_lbl': ['air sec', 'confortable', 'lourd par moments', 'très humide', 'chaleur oppressante'],
        'sea_lbl': ['froide, baignade sportive', 'fraîche, vivifiante', 'agréable pour la baignade', 'chaude, idéale'],
        'day_tpl': '{h}h de jour',
        'air_lbl': ['excellent', 'bon', 'moyen', 'dégradé'],
    },
    'en': {
        'kicker': 'This month\'s conditions', 'title_tpl': 'What it\'s like in {mois}',
        'uv': 'UV index', 'feel': 'Feels like', 'sea': 'Sea', 'day': 'Daylight',
        'air': 'Air quality',
        'uv_lbl': ['low', 'moderate', 'high', 'very high', 'extreme'],
        'uv_tip': ['no protection needed', 'protect during midday hours',
                   'sunscreen and hat advised', 'protection essential', 'avoid midday sun'],
        'feel_lbl': ['dry air', 'comfortable', 'muggy at times', 'very humid', 'oppressive heat'],
        'sea_lbl': ['cold, for the brave', 'cool, invigorating', 'pleasant for swimming', 'warm, ideal'],
        'day_tpl': '{h}h of daylight',
        'air_lbl': ['excellent', 'good', 'fair', 'poor'],
    },
    'en-us': {
        'kicker': 'This month\'s conditions', 'title_tpl': 'What it\'s like in {mois}',
        'uv': 'UV index', 'feel': 'Feels like', 'sea': 'Sea', 'day': 'Daylight',
        'air': 'Air quality',
        'uv_lbl': ['low', 'moderate', 'high', 'very high', 'extreme'],
        'uv_tip': ['no protection needed', 'protect during midday hours',
                   'sunscreen and hat advised', 'protection essential', 'avoid midday sun'],
        'feel_lbl': ['dry air', 'comfortable', 'muggy at times', 'very humid', 'oppressive heat'],
        'sea_lbl': ['cold, for the brave', 'cool, invigorating', 'pleasant for swimming', 'warm, ideal'],
        'day_tpl': '{h}h of daylight',
        'air_lbl': ['excellent', 'good', 'fair', 'poor'],
    },
    'es': {
        'kicker': 'Condiciones del mes', 'title_tpl': 'Cómo es {mois} en la práctica',
        'uv': 'Índice UV', 'feel': 'Sensación', 'sea': 'Mar', 'day': 'Horas de luz',
        'air': 'Calidad del aire',
        'uv_lbl': ['bajo', 'moderado', 'alto', 'muy alto', 'extremo'],
        'uv_tip': ['sin protección necesaria', 'protección en horas centrales',
                   'crema y sombrero recomendados', 'protección indispensable', 'evitar el sol del mediodía'],
        'feel_lbl': ['aire seco', 'confortable', 'pesado a ratos', 'muy húmedo', 'calor agobiante'],
        'sea_lbl': ['fría, para valientes', 'fresca, vigorizante', 'agradable para el baño', 'cálida, ideal'],
        'day_tpl': '{h}h de luz',
        'air_lbl': ['excelente', 'buena', 'media', 'degradada'],
    },
    'de': {
        'kicker': 'Bedingungen des Monats', 'title_tpl': 'So ist der {mois} konkret',
        'uv': 'UV-Index', 'feel': 'Gefühlt', 'sea': 'Meer', 'day': 'Tageslicht',
        'air': 'Luftqualität',
        'uv_lbl': ['niedrig', 'mäßig', 'hoch', 'sehr hoch', 'extrem'],
        'uv_tip': ['kein Schutz nötig', 'Schutz zur Mittagszeit',
                   'Sonnencreme und Hut empfohlen', 'Schutz unverzichtbar', 'Mittagssonne meiden'],
        'feel_lbl': ['trockene Luft', 'angenehm', 'zeitweise schwül', 'sehr feucht', 'drückende Hitze'],
        'sea_lbl': ['kalt, nur für Mutige', 'kühl, belebend', 'angenehm zum Baden', 'warm, ideal'],
        'day_tpl': '{h}h Tageslicht',
        'air_lbl': ['ausgezeichnet', 'gut', 'mittel', 'belastet'],
    },
}


def render_v6_monthly_details(slug, lang, details_data):
    """Section "Conditions du mois" : UV, ressenti, mer, durée du jour, air.

    Toutes les valeurs varient par mois (données CSV + calcul astronomique) →
    contenu distinctif réel entre les 12 pages mensuelles d'une destination.
    """
    L = _DETAILS_I18N.get(lang, _DETAILS_I18N['en'])
    d = details_data
    mois = d['mois']
    mois_inline = (mois[0].lower() + mois[1:]) if (lang in ('fr', 'es') and mois) else mois

    items = []  # (label, valeur, note)

    uv = d.get('uv')
    if uv is not None and uv > 0:
        i = 0 if uv < 3 else (1 if uv < 6 else (2 if uv < 8 else (3 if uv < 11 else 4)))
        items.append((L['uv'], f'{uv:.0f} · {L["uv_lbl"][i]}', L['uv_tip'][i]))

    dew = d.get('dew')
    tmax = d.get('tmax', 20)
    if dew is not None and dew != 0:
        i = 0 if dew < 10 else (1 if dew < 16 else (2 if dew < 21 else (3 if dew < 24 else 4)))
        if i >= 3 and tmax < 27:
            i = 2
        items.append((L['feel'], L['feel_lbl'][i], f'{dew:.0f}°'))

    sea = d.get('sea')
    if sea is not None and sea > 0:
        i = 0 if sea < 18 else (1 if sea < 22 else (2 if sea < 26 else 3))
        items.append((L['sea'], f'{sea:.0f}°C', L['sea_lbl'][i]))

    lat = d.get('lat')
    if lat is not None:
        h_day = _daylight_hours(lat, d.get('month_idx', 0))
        items.append((L['day'], L['day_tpl'].format(h=h_day), ''))

    aqi = d.get('aqi')
    if aqi is not None and aqi > 0:
        i = 0 if aqi < 20 else (1 if aqi < 40 else (2 if aqi < 60 else 3))
        items.append((L['air'], L['air_lbl'][i], f'AQI {aqi:.0f}'))

    if len(items) < 2:
        return ''

    cells = ''.join(
        f'<div style="background:#fff;border:1px solid #e6e8eb;border-radius:12px;'
        f'padding:14px 16px"><div style="font-size:11px;font-weight:700;'
        f'text-transform:uppercase;letter-spacing:.5px;color:#6b7280;margin-bottom:4px">'
        f'{h(lbl)}</div><div style="font-size:15px;font-weight:700;color:#1a2230">{h(val)}</div>'
        + (f'<div style="font-size:12.5px;color:#6b7280;margin-top:2px">{h(note)}</div>' if note else '')
        + '</div>'
        for lbl, val, note in items
    )

    return (
        f'<section class="section">\n'
        f'  <div class="container">\n'
        f'    <div class="section-head">\n'
        f'      <div class="section-kicker">{h(L["kicker"])}</div>\n'
        f'      <h2>{h(L["title_tpl"].format(mois=mois_inline))}</h2>\n'
        f'    </div>\n'
        f'    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:12px">\n'
        f'      {cells}\n'
        f'    </div>\n'
        f'  </div>\n'
        f'</section>'
    )


_DYN_I18N = {
    'fr': {
        'rank_1': '{mois} est le meilleur mois de l\'année à {nom}.',
        'rank_n': '{mois} est le {rank}e meilleur mois de l\'année à {nom} (sur 12).',
        'vs_prev': 'Par rapport à {prev} : {parts}.',
        'temp_up': '+{v}°C en journée', 'temp_down': '−{v}°C en journée',
        'rain_up': '{v} pts de jours pluvieux en plus', 'rain_down': '{v} pts de jours pluvieux en moins',
        'sun_up': '+{v}h de soleil par jour', 'sun_down': '−{v}h de soleil par jour',
    },
    'en': {
        'rank_1': '{mois} is the best month of the year in {nom}.',
        'rank_n': '{mois} ranks {rank} out of 12 months in {nom}.',
        'vs_prev': 'Compared to {prev}: {parts}.',
        'temp_up': '+{v}°C daytime', 'temp_down': '−{v}°C daytime',
        'rain_up': '{v} pts more rainy days', 'rain_down': '{v} pts fewer rainy days',
        'sun_up': '+{v}h of sun per day', 'sun_down': '−{v}h of sun per day',
    },
    'en-us': {
        'rank_1': '{mois} is the best month of the year in {nom}.',
        'rank_n': '{mois} ranks {rank} out of 12 months in {nom}.',
        'vs_prev': 'Compared to {prev}: {parts}.',
        'temp_up': '+{v}°F daytime', 'temp_down': '−{v}°F daytime',
        'rain_up': '{v} pts more rainy days', 'rain_down': '{v} pts fewer rainy days',
        'sun_up': '+{v}h of sun per day', 'sun_down': '−{v}h of sun per day',
    },
    'es': {
        'rank_1': '{mois} es el mejor mes del año en {nom}.',
        'rank_n': '{mois} es el {rank}º mejor mes del año en {nom} (de 12).',
        'vs_prev': 'Respecto a {prev}: {parts}.',
        'temp_up': '+{v}°C de día', 'temp_down': '−{v}°C de día',
        'rain_up': '{v} pts más de días lluviosos', 'rain_down': '{v} pts menos de días lluviosos',
        'sun_up': '+{v}h de sol al día', 'sun_down': '−{v}h de sol al día',
    },
    'de': {
        'rank_1': 'Der {mois} ist der beste Monat des Jahres in {nom}.',
        'rank_n': 'Der {mois} ist der {rank}.-beste Monat des Jahres in {nom} (von 12).',
        'vs_prev': 'Im Vergleich zum {prev}: {parts}.',
        'temp_up': '+{v}°C tagsüber', 'temp_down': '−{v}°C tagsüber',
        'rain_up': '{v} Pkt. mehr Regentage', 'rain_down': '{v} Pkt. weniger Regentage',
        'sun_up': '+{v}h Sonne pro Tag', 'sun_down': '−{v}h Sonne pro Tag',
    },
}


def monthly_dynamics_paragraph(lang, nom, mois, rank, prev_month,
                               d_tmax, d_rain, d_sun, is_us=False):
    """Paragraphe de dynamique mensuelle : rang du mois + deltas vs mois précédent.

    Chiffres différents chaque mois par construction → contenu distinctif.
    """
    L = _DYN_I18N.get(lang, _DYN_I18N['en'])
    prev_i = (prev_month[0].lower() + prev_month[1:]) if (lang in ('fr', 'es') and prev_month) else prev_month

    if rank == 1:
        rank_txt = L['rank_1'].format(mois=h(mois), nom=h(nom))
    else:
        rank_txt = L['rank_n'].format(mois=h(mois), rank=rank, nom=h(nom))

    deltas = []
    dt = round(d_tmax * (1.8 if is_us else 1))
    if abs(dt) >= 2:
        deltas.append((L['temp_up'] if dt > 0 else L['temp_down']).format(v=abs(dt)))
    dr = round(d_rain)
    if abs(dr) >= 5:
        deltas.append((L['rain_up'] if dr > 0 else L['rain_down']).format(v=abs(dr)))
    ds = round(d_sun, 1)
    if abs(ds) >= 0.5:
        deltas.append((L['sun_up'] if ds > 0 else L['sun_down']).format(v=abs(ds)))

    txt = rank_txt
    if deltas:
        txt += ' ' + L['vs_prev'].format(prev=h(prev_i), parts=', '.join(deltas))
    return f'<p style="margin:14px 0 0;font-size:15px;line-height:1.65;color:#3a4150">{txt}</p>'


_MFAQ_I18N = {
    'fr': {
        'q_swim': 'Peut-on se baigner à {nom} en {mois} ?',
        'a_swim': 'En {mois}, la mer est à {sea}°C en moyenne à {nom} : {lbl}. {extra}',
        'swim_yes': 'La baignade est agréable sans combinaison.',
        'swim_warm': 'Conditions idéales pour la baignade et le snorkeling.',
        'swim_cool': 'Baignade possible mais vivifiante ; les plus frileux préféreront une combinaison.',
        'swim_no': 'Réservée aux nageurs aguerris ou équipés d\'une combinaison.',
        'q_uv': 'Faut-il une protection solaire à {nom} en {mois} ?',
        'a_uv': 'L\'indice UV moyen atteint {uv} en {mois} à {nom} ({lbl}), avec environ {day}h de jour. {tip}',
    },
    'en': {
        'q_swim': 'Can you swim in {nom} in {mois}?',
        'a_swim': 'In {mois}, the sea averages {sea}°C in {nom}: {lbl}. {extra}',
        'swim_yes': 'Swimming is pleasant without a wetsuit.',
        'swim_warm': 'Ideal conditions for swimming and snorkeling.',
        'swim_cool': 'Swimming is possible but brisk; sensitive swimmers may prefer a wetsuit.',
        'swim_no': 'Best left to hardened swimmers or those with a wetsuit.',
        'q_uv': 'Do you need sun protection in {nom} in {mois}?',
        'a_uv': 'The average UV index reaches {uv} in {mois} in {nom} ({lbl}), with about {day}h of daylight. {tip}',
    },
    'en-us': {
        'q_swim': 'Can you swim in {nom} in {mois}?',
        'a_swim': 'In {mois}, the sea averages {sea}°F in {nom}: {lbl}. {extra}',
        'swim_yes': 'Swimming is pleasant without a wetsuit.',
        'swim_warm': 'Ideal conditions for swimming and snorkeling.',
        'swim_cool': 'Swimming is possible but brisk; sensitive swimmers may prefer a wetsuit.',
        'swim_no': 'Best left to hardened swimmers or those with a wetsuit.',
        'q_uv': 'Do you need sun protection in {nom} in {mois}?',
        'a_uv': 'The average UV index reaches {uv} in {mois} in {nom} ({lbl}), with about {day}h of daylight. {tip}',
    },
    'es': {
        'q_swim': '¿Se puede nadar en {nom} en {mois}?',
        'a_swim': 'En {mois}, el mar está a {sea}°C de media en {nom}: {lbl}. {extra}',
        'swim_yes': 'El baño es agradable sin neopreno.',
        'swim_warm': 'Condiciones ideales para el baño y el esnórquel.',
        'swim_cool': 'El baño es posible pero vigorizante; los frioleros preferirán neopreno.',
        'swim_no': 'Reservado a nadadores curtidos o con neopreno.',
        'q_uv': '¿Hace falta protección solar en {nom} en {mois}?',
        'a_uv': 'El índice UV medio alcanza {uv} en {mois} en {nom} ({lbl}), con unas {day}h de luz. {tip}',
    },
    'de': {
        'q_swim': 'Kann man in {nom} im {mois} baden?',
        'a_swim': 'Im {mois} hat das Meer in {nom} durchschnittlich {sea}°C: {lbl}. {extra}',
        'swim_yes': 'Baden ist ohne Neopren angenehm.',
        'swim_warm': 'Ideale Bedingungen zum Baden und Schnorcheln.',
        'swim_cool': 'Baden ist möglich, aber erfrischend; Kälteempfindliche bevorzugen Neopren.',
        'swim_no': 'Nur für abgehärtete Schwimmer oder mit Neoprenanzug.',
        'q_uv': 'Braucht man in {nom} im {mois} Sonnenschutz?',
        'a_uv': 'Der mittlere UV-Index erreicht {uv} im {mois} in {nom} ({lbl}), bei rund {day}h Tageslicht. {tip}',
    },
}


def monthly_faq_items(lang, nom, mois, sea=None, uv=None, lat=None,
                      month_idx=0, is_us=False):
    """1-2 items FAQ spécifiques AU MOIS (réponses chiffrées depuis le CSV).

    Contenu distinctif réel : sea_temp/uv/durée du jour varient chaque mois.
    Retourne une liste de dicts {'q','a'} (0 à 2 items, dégradation propre).
    """
    L = _MFAQ_I18N.get(lang, _MFAQ_I18N['en'])
    D = _DETAILS_I18N.get(lang, _DETAILS_I18N['en'])
    mois_i = (mois[0].lower() + mois[1:]) if (lang in ('fr', 'es') and mois) else mois
    items = []

    if sea is not None and sea > 0:
        i = 0 if sea < 18 else (1 if sea < 22 else (2 if sea < 26 else 3))
        extra = [L['swim_no'], L['swim_cool'], L['swim_yes'], L['swim_warm']][i]
        sea_v = round(sea * 1.8 + 32) if is_us else round(sea)
        items.append({
            'q': L['q_swim'].format(nom=nom, mois=mois_i),
            'a': L['a_swim'].format(mois=mois_i, sea=sea_v, nom=nom,
                                    lbl=D['sea_lbl'][i], extra=extra),
        })

    if uv is not None and uv > 0:
        i = 0 if uv < 3 else (1 if uv < 6 else (2 if uv < 8 else (3 if uv < 11 else 4)))
        day = _daylight_hours(lat, month_idx) if lat is not None else None
        items.append({
            'q': L['q_uv'].format(nom=nom, mois=mois_i),
            'a': L['a_uv'].format(uv=round(uv), mois=mois_i, nom=nom,
                                  lbl=D['uv_lbl'][i],
                                  day=day if day is not None else '—',
                                  tip=D['uv_tip'][i].capitalize() + '.'),
        })
    return items
