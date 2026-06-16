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
        f'          {chips_block}\n'
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
