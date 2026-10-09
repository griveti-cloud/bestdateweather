"""
Page « Où partir au soleil toute l'année ? » (meilleures-destinations-meteo).

Même données que le moteur par dates (engine/data-v1.json), mais à l'échelle de
l'année : score annuel, nombre de bons mois, frise des 12 mois, vrais chiffres
annuels (et non ceux du meilleur mois, comme l'ancienne page).
Miroir exact de js/annual-engine.js : toute modification doit être faite dans
les deux fichiers.
"""
from lib.date_engine import I18N, PAGE, UC_KEY, UC_MTN, _hav, flight_h, drop_parents
from lib.engine_render import esc, fmt, R

GOOD = 7.6   # niveau « Très bien » de la légende de la carte

A18N = {
    'fr': {
        'mi': ['J', 'F', 'M', 'A', 'M', 'J', 'J', 'A', 'S', 'O', 'N', 'D'],
        'sorts': {'score': 'Score annuel', 'regular': 'Régularité (bons mois)', 'near': 'Les plus proches', 'cheap': 'Les moins chères sur place'},
        'good_opts': [[0, 'Peu importe'], [6, '6 mois et plus'], [9, '9 mois et plus'], [12, 'Les 12 mois']],
        't': {
            'top': 'Top {n} · {uc}{reg} · toute l’année',
            'count': '{k} destinations sur {n} analysées correspondent à vos critères.',
            'count1': '{k} destination sur {n} analysées correspond à vos critères.',
            'empty': 'Aucune destination ne correspond. Allongez le temps de vol, élargissez la région ou baissez le nombre de bons mois demandé.',
            'f_regular': 'La plus régulière', 'f_near': 'La plus proche toute l’année', 'f_cheap': 'La moins chère toute l’année',
            'f_europe': 'La meilleure en Europe (îles comprises)', 'f_best': 'Le meilleur score', 'f_near_m': 'La plus proche', 'f_cheap_m': 'La moins chère',
            'fd_regular': '{g} bons mois sur 12, score annuel {s}/10, ≈ {h} de vol.',
            'fd_near': '≈ {h} de vol depuis {dep}, {g} bons mois sur 12.',
            'fd_cheap': 'Budget {b}, {g} bons mois sur 12.',
            'fd_europe': '{g} bons mois sur 12, maximales de {t1} à {t2} °C.',
            'fd_best': 'Meilleur mois : {bm} ({s}/10), ≈ {h} de vol.',
            'good_line': '<b>{g} bons mois sur 12</b> · meilleurs : {bm}',
            'temps': 'Maximales de {t1} à {t2} °C', 'rain': '≈ {r} % de jours de pluie sur l’année',
            'score_year': '{s}/10', 'score_best': '{s}/10 au meilleur mois',
            'cell': '{m} : {s}/10', 'flight': '≈ {h} de vol', 'card': 'Fiche',
            'lg': ['8,6 et plus', '7,6 à 8,5', '6,3 à 7,5', '5 à 6,2', '3,5 à 4,9', 'moins de 3,5'],
            'lg_lead': 'Score du mois :', 'see_all': 'Tout voir', 'see': 'Voir', 'none': 'Aucune destination avec ces critères',
            'month_more': 'Classement complet', 'fly_any': 'peu importe', 'world': 'Monde entier', 'err_load': 'Impossible de charger les données. Rechargez la page.',
            'other_city': 'Autre ville…', 'city_ph': 'Tapez une ville (ex. Rennes, Bâle, Montréal)', 'city_none': 'Aucune ville trouvée.', 'city_err': 'Recherche indisponible, réessayez.',
            'mini': '{g}/12 bons mois',
        },
    },
    'en': {
        'mi': ['J', 'F', 'M', 'A', 'M', 'J', 'J', 'A', 'S', 'O', 'N', 'D'],
        'sorts': {'score': 'Annual score', 'regular': 'Consistency (good months)', 'near': 'Closest', 'cheap': 'Cheapest on the ground'},
        'good_opts': [[0, 'Any'], [6, '6 months or more'], [9, '9 months or more'], [12, 'All 12 months']],
        't': {
            'top': 'Top {n} · {uc}{reg} · all year',
            'count': '{k} of {n} destinations analysed match your criteria.',
            'count1': '{k} of {n} destinations analysed matches your criteria.',
            'empty': 'No destination matches. Allow a longer flight, widen the region or ask for fewer good months.',
            'f_regular': 'Most consistent', 'f_near': 'Closest all year', 'f_cheap': 'Cheapest all year',
            'f_europe': 'Best in Europe (islands included)', 'f_best': 'Best score', 'f_near_m': 'Closest', 'f_cheap_m': 'Cheapest',
            'fd_regular': '{g} good months out of 12, annual score {s}/10, ≈ {h} flight.',
            'fd_near': '≈ {h} flight from {dep}, {g} good months out of 12.',
            'fd_cheap': '{b} budget, {g} good months out of 12.',
            'fd_europe': '{g} good months out of 12, highs of {t1} to {t2} °C.',
            'fd_best': 'Best month: {bm} ({s}/10), ≈ {h} flight.',
            'good_line': '<b>{g} good months out of 12</b> · best: {bm}',
            'temps': 'Highs of {t1} to {t2} °C', 'rain': '≈ {r}% rainy days over the year',
            'score_year': '{s}/10', 'score_best': '{s}/10 in the best month',
            'cell': '{m}: {s}/10', 'flight': '≈ {h} flight', 'card': 'Guide',
            'lg': ['8.6 and above', '7.6 to 8.5', '6.3 to 7.5', '5 to 6.2', '3.5 to 4.9', 'below 3.5'],
            'lg_lead': 'Monthly score:', 'see_all': 'See all', 'see': 'See', 'none': 'No destination with these criteria',
            'month_more': 'Full ranking', 'fly_any': 'any', 'world': 'Whole world', 'err_load': 'Could not load the data. Please reload the page.',
            'other_city': 'Other city…', 'city_ph': 'Type a city (e.g. Bristol, Zurich, Boston)', 'city_none': 'No city found.', 'city_err': 'Search unavailable, please try again.',
            'mini': '{g}/12 good months',
        },
    },
}


def default_state():
    return {'uc': 'gen', 'reg': 'all', 'dep': 0, 'fly': 16, 'good': 0, 'budget': 5, 'rl': 2, 'sort': 'score', 'shown': PAGE}


def cell_cls(v):
    if v is None:
        return 'n'
    if v >= 8.6:
        return 'e'
    if v >= 7.6:
        return 't'
    if v >= 6.3:
        return 'b'
    if v >= 5:
        return 'p'
    if v >= 3.5:
        return 'm'
    return 'x'


def evaluate(rec, uc, dep):
    if uc in UC_MTN and not rec['m']:
        return None
    k = UC_KEY[uc]
    M = rec['M']
    vals = M[k]
    if any(v is None for v in vals) or any(v is None for v in M['tx']):
        return None
    good = sum(1 for v in vals if v >= GOOD)
    tot = rain = 0.0
    for i in range(12):   # addition dans l'ordre, comme en JavaScript (sum() de Python 3.12 compense les arrondis)
        tot += vals[i]
        rain += M['r'][i]
    score = max(vals) if uc in UC_MTN else tot / 12
    order = sorted(range(12), key=lambda i: (-vals[i], i))
    best3 = sorted(order[:3])
    o = {'d': rec, 'uc': uc, 'score': score, 'good': good, 'vals': vals, 'best3': best3, 'best': order[0],
         't1': min(M['tx']), 't2': max(M['tx']), 'rain': rain / 12, 'rl': rec['rl']}
    o['km'] = _hav(dep[1], dep[2], rec['la'], rec['lo'])
    o['h'] = flight_h(o['km'])
    return o


SORTERS = {
    'score': lambda x: (-x['score'], x['d']['s']),
    'regular': lambda x: (-x['good'], -x['score'], x['d']['s']),
    'near': lambda x: (x['h'], x['d']['s']),
    'cheap': lambda x: (x['d']['bi'], -x['score'], x['d']['s']),
}


def compute_view(dataset, st, lang):
    L = I18N[lang]
    dep = L['deps'][st['dep']]
    ev = {k: [o for o in (evaluate(r, k, dep) for r in dataset) if o] for k in UC_KEY}
    mtn = st['uc'] in UC_MTN

    def ok_base(x): return x['rl'] <= st['rl'] and x['d']['bi'] <= st['budget']
    def ok_fly(x): return st['fly'] >= 16 or x['h'] <= st['fly']
    def ok_good(x): return x['good'] >= st['good']
    def ok_reg(x): return st['reg'] == 'all' or x['d']['reg'] == st['reg']

    rows = drop_parents([x for x in ev[st['uc']] if ok_base(x) and ok_fly(x) and ok_good(x) and ok_reg(x)])
    rows.sort(key=SORTERS[st['sort']])
    facts, used = [], set()

    def pick(arr, key, fn):
        for x in arr:
            if x['d']['s'] not in used:
                used.add(x['d']['s'])
                facts.append({'k': key, 'x': x, 'fn': fn})
                return
    if not mtn:
        pick(sorted(rows, key=SORTERS['regular']), 'f_regular', 'fd_regular')
        cand = [x for x in rows if x['good'] >= 9]
        pick(sorted(cand, key=SORTERS['near']), 'f_near', 'fd_near')
        pick(sorted(cand, key=SORTERS['cheap']), 'f_cheap', 'fd_cheap')
        pick(sorted([x for x in rows if x['d']['reg'] in ('eu', 'atl')], key=SORTERS['regular']), 'f_europe', 'fd_europe')
    else:
        pick(sorted(rows, key=SORTERS['score']), 'f_best', 'fd_best')
        cand = [x for x in rows if x['score'] >= 7]
        pick(sorted(cand, key=SORTERS['near']), 'f_near_m', 'fd_best')
        pick(sorted(cand, key=SORTERS['cheap']), 'f_cheap_m', 'fd_best')
    projects = {k: sorted(drop_parents([x for x in ev[k] if ok_base(x) and ok_fly(x)]), key=SORTERS['score'])[:5] for k in ('plage', 'ski', 'rando')}
    g = drop_parents([x for x in ev['gen'] if ok_base(x)])
    regions = {}
    for r in L['regions']:
        if r == 'other':
            continue
        top = sorted([x for x in g if x['d']['reg'] == r], key=SORTERS['score'])[:4]
        if top:
            regions[r] = top
    months = []
    for m in range(12):
        months.append(sorted(g, key=lambda x: (-x['vals'][m], x['d']['s']))[:3])
    return {'rows': rows, 'n_uc': len(ev[st['uc']]), 'facts': facts, 'projects': projects, 'regions': regions, 'months': months}


# ── rendu ────────────────────────────────────────────────────────────────────

class RA(R):
    def __init__(self, lang, annual_tpl):
        super().__init__(lang, annual_tpl)
        self.A, self.TA = A18N[lang], A18N[lang]['t']

    def best_months(self, x):
        return ', '.join(self.L['ms'][i] for i in x['best3'])

    def fact_text(self, f, st):
        x, L = f['x'], self.L
        return fmt(self.TA[f['fn']], g=x['good'], s=self.f1(x['score']), h=self.fmt_h(x['h']), dep=L['deps'][st['dep']][0],
                   b=L['budget'][str(x['d']['bi'])].lower(), t1=self.r0(x['t1']), t2=self.r0(x['t2']),
                   bm=L['months'][x['best']])


def strip_html(r, x):
    cells = ''.join('<span class="ma-c ' + cell_cls(v) + '" title="' + esc(fmt(r.TA['cell'], m=r.L['months'][i], s=r.f1(v))) + '"></span>'
                    for i, v in enumerate(x['vals']))
    letters = ''.join('<span>' + l + '</span>' for l in r.A['mi'])
    return '<div class="ma-strip">' + cells + '</div><div class="ma-letters" aria-hidden="true">' + letters + '</div>'


def item_html(r, x, i):
    L, TA = r.L, r.TA
    badges = ('<span class="me-badge v' + str(x['rl']) + '">' + esc(L['secu'][str(x['rl'])]) + '</span>'
              '<span class="me-badge">' + esc(L['budget'][str(max(1, min(5, x['d']['bi'])))]) + '</span>')
    sc = fmt(TA['score_best'] if x['uc'] in UC_MTN else TA['score_year'], s=r.f1(x['score']))
    return ('<article class="me-item ma-item"><div class="me-rank">' + str(i + 1) + '</div>'
            '<div class="me-name"><a href="' + r.href(x) + '">' + r.nm(x) + '</a><span>' + esc(x['d']['p'][r.ni]) + ' · ' + r.fmt_km(x['km']) + '</span><div class="me-badges">' + badges + '</div></div>'
            '<div class="me-metrics"><span class="me-t">' + esc(fmt(TA['temps'], t1=r.r0(x['t1']), t2=r.r0(x['t2']))) + '</span><span>'
            + esc(fmt(TA['rain'], r=r.r0(x['rain']))) + ' · ' + esc(fmt(TA['flight'], h=r.fmt_h(x['h']))) + '</span></div>'
            '<div class="me-dry">' + strip_html(r, x) + '<div>' + fmt(TA['good_line'], g=x['good'], bm=esc(r.best_months(x))) + '</div></div>'
            '<div class="me-side"><span class="me-score' + (' ' + 'mid' if x['score'] < 7.6 and x['score'] >= 5 else (' low' if x['score'] < 5 else '')) + '">' + esc(sc) + '</span><a href="' + r.href(x) + '">' + esc(TA['card']) + '</a></div></article>')


def mini_li(r, x):
    return ('<li><a href="' + r.href(x) + '">' + r.nm(x) + '</a><span>' + esc(fmt(r.TA['mini'], g=x['good'])) + ' · <b>' + r.f1(x['score']) + '</b></span></li>')


def month_li(r, x, m):
    return '<li><a href="' + r.href(x) + '">' + r.nm(x) + '</a><span><b>' + r.f1(x['vals'][m]) + '</b></span></li>'


ANNUAL_CSS = r"""
.ma-strip{display:grid;grid-template-columns:repeat(12,minmax(0,1fr));gap:2px;max-width:252px}
.ma-letters{display:grid;grid-template-columns:repeat(12,minmax(0,1fr));gap:2px;max-width:252px;font-size:.66rem;color:var(--muted);text-align:center;line-height:1.2}
.ma-c{height:14px;border-radius:3px;background:var(--line)}
.ma-c.e{background:#1a7a4a}.ma-c.t{background:#2d9e60}.ma-c.b{background:#84cc16}.ma-c.p{background:#f59e0b}.ma-c.m{background:#f97316}.ma-c.x{background:#ef4444}
.ma-legend{display:flex;gap:12px;flex-wrap:wrap;font-size:.85rem;color:var(--muted);align-items:center}
.ma-legend span{display:inline-flex;align-items:center;gap:6px}
.ma-legend .ma-c{display:inline-block;width:14px}
.ma-dates{display:flex;gap:10px 16px;align-items:center;flex-wrap:wrap;background:var(--gold-soft);border-radius:10px;padding:10px 14px;font-size:.92rem}
.ma-dates b{font-weight:700}
.ma-months{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:22px}
"""


def render_main(view, st, lang, annual_tpl, month_links, other_links, X, self_url):
    r = RA(lang, annual_tpl)
    L, T, TA, A = r.L, r.T, r.TA, r.A
    months_nav = (f'<a href="{self_url}" aria-current="page">' + esc(X['all_year']) + '</a>'
                  + ''.join(f'<a href="{u}">{esc(L["ms"][i])}</a>' for i, u in enumerate(month_links)))
    uc_chips = ''.join(f'<button type="button" class="me-chip" data-v="{k}" aria-pressed="{"true" if k == st["uc"] else "false"}">{esc(v)}</button>' for k, v in L['uc'].items())
    reg_opts = f'<option value="all">{esc(TA["world"])}</option>' + ''.join(f'<option value="{k}">{esc(v)}</option>' for k, v in L['regions'].items())
    dep_opts = ''.join(f'<option value="{i}"' + (' selected' if i == st['dep'] else '') + f'>{esc(d[0])}</option>' for i, d in enumerate(L['deps'])) + f'<option value="other">{esc(TA["other_city"])}</option>'
    sort_opts = ''.join(f'<option value="{k}"' + (' selected' if k == st['sort'] else '') + f'>{esc(v)}</option>' for k, v in A['sorts'].items())

    def chips(items, cur):
        return ''.join(f'<button type="button" class="me-chip" data-v="{v}" aria-pressed="{"true" if v == cur else "false"}">{esc(l)}</button>' for v, l in items)
    facts = ''.join('<div class="me-fact"><div class="me-k">' + esc(TA[f['k']]) + '</div><a class="me-v" href="' + r.href(f['x']) + '">' + r.nm(f['x']) + '</a><div class="me-d">' + esc(r.fact_text(f, st)) + '</div></div>' for f in view['facts'])
    rows = view['rows']
    rank_title = fmt(TA['top'], n=min(st['shown'], len(rows)), uc=L['uc_t'][st['uc']], reg='')
    count = fmt(TA['count'] if len(rows) > 1 else TA['count1'], k=len(rows), n=view['n_uc'])
    lst = ''.join(item_html(r, x, i) for i, x in enumerate(rows[:st['shown']])) or '<p class="me-empty">' + esc(TA['empty']) + '</p>'
    legend = '<span>' + esc(TA['lg_lead']) + '</span>' + ''.join('<span><i class="ma-c ' + c + '"></i>' + esc(l) + '</span>' for c, l in zip('etbpmx', TA['lg']))
    projects = ''
    for k in ('plage', 'ski', 'rando'):
        lis = ''.join(mini_li(r, x) for x in view['projects'][k]) or '<li><span>' + esc(TA['none']) + '</span></li>'
        projects += f'<div class="me-box"><div class="me-box-head"><h3>{esc(L["uc"][k])}</h3><button type="button" class="me-link" data-uc="{k}">{esc(TA["see_all"])}</button></div><ul class="me-mini">{lis}</ul></div>'
    regions = ''
    for k in L['regions']:
        if k in view['regions']:
            regions += f'<div class="me-box"><div class="me-box-head"><h3>{esc(L["regions"][k])}</h3><button type="button" class="me-link" data-reg="{k}">{esc(TA["see"])}</button></div><ul class="me-mini">' + ''.join(mini_li(r, x) for x in view['regions'][k]) + '</ul></div>'
    months = ''
    for m in range(12):
        months += (f'<div class="me-box"><div class="me-box-head"><h3><a href="{month_links[m]}">{esc(L["months"][m][0].upper() + L["months"][m][1:])}</a></h3>'
                   f'<a class="me-link" href="{month_links[m]}">{esc(TA["month_more"])}</a></div><ul class="me-mini">' + ''.join(month_li(r, x, m) for x in view['months'][m]) + '</ul></div>')
    others = ''.join(f'<a href="{u}">{esc(t)}</a>' for t, u in other_links)
    return f"""<main class="me" id="me">
<section class="me-hero">
<div class="me-eyebrow">{esc(X['eyebrow'])}</div>
<h1>{X['h1']}</h1>
<p class="me-sub">{esc(X['sub'])}</p>
</section>
<div class="me-months" role="navigation" aria-label="{esc(X['months_label'])}">{months_nav}</div>
<p class="ma-dates"><b>{esc(X['dates_q'])}</b> {esc(X['dates_a'])}</p>
<form class="me-tool" id="me-tool" aria-label="{esc(X['criteria'])}">
<div class="me-criteria" style="border-top:0;padding-top:0">
<div class="me-row me-wide"><div class="me-lbl" id="me-lbl-uc">{esc(X['trip_type'])}</div><div class="me-chips" id="me-uc" role="group" aria-labelledby="me-lbl-uc">{uc_chips}</div></div>
<div class="me-row"><label class="me-lbl" for="me-reg">{esc(X['region'])}</label><select id="me-reg">{reg_opts}</select></div>
<div class="me-row"><label class="me-lbl" for="me-dep">{esc(X['from_city'])}</label><select id="me-dep">{dep_opts}</select><div class="me-city" id="me-city" hidden><input type="search" id="me-city-q" autocomplete="off" placeholder="{esc(TA['city_ph'])}" aria-label="{esc(TA['city_ph'])}"><div class="me-city-sug" id="me-city-sug" role="listbox"></div></div></div>
<div class="me-row"><label class="me-lbl" for="me-fly">{esc(X['max_flight'])} <span id="me-fly-val">{esc(TA['fly_any'])}</span></label><input type="range" id="me-fly" min="1" max="16" step="0.5" value="{st['fly']}"></div>
<div class="me-row"><div class="me-lbl" id="me-lbl-good">{esc(X['good_months'])}</div><div class="me-chips" id="me-good" role="group" aria-labelledby="me-lbl-good">{chips(A['good_opts'], st['good'])}</div></div>
<div class="me-row"><div class="me-lbl" id="me-lbl-budget">{esc(X['budget'])}</div><div class="me-chips" id="me-budget" role="group" aria-labelledby="me-lbl-budget">{chips(L['budget_opts'], st['budget'])}</div><p class="me-help">{esc(X['budget_help'])}</p></div>
<div class="me-row"><div class="me-lbl" id="me-lbl-secu">{esc(X['safety'])}</div><div class="me-chips" id="me-secu" role="group" aria-labelledby="me-lbl-secu">{chips(L['secu_opts'], st['rl'])}</div><p class="me-help">{esc(X['safety_help'])}</p></div>
</div>
</form>
<section class="me-facts" id="me-facts" style="--n:{max(1, len(view['facts']))}" aria-label="{esc(X['key_points'])}">{facts}</section>
<section class="me-sec" id="me-classement">
<div class="me-sec-head"><div><h2 id="me-rank-title">{esc(rank_title)}</h2><div class="me-lead" id="me-count">{esc(count)}</div></div><label class="me-sortbox" for="me-sort">{esc(X['sort_by'])} <select id="me-sort">{sort_opts}</select></label></div>
<div class="me-list" id="me-list">{lst}</div>
<button type="button" class="me-more" id="me-more"{'' if len(rows) > st['shown'] else ' hidden'}>{esc(X['more'])}</button>
<div class="ma-legend">{legend}</div>
</section>
<section class="me-sec"><div><h2>{esc(X['by_month_title'])}</h2><p class="me-lead">{esc(X['by_month_lead'])}</p></div><div class="ma-months" id="me-bymonth">{months}</div></section>
<section class="me-sec"><div><h2>{esc(X['projects_title'])}</h2><p class="me-lead">{esc(X['projects_lead'])}</p></div><div class="me-cols" id="me-projects">{projects}</div></section>
<section class="me-sec"><div><h2>{esc(X['regions_title'])}</h2><p class="me-lead">{esc(X['regions_lead'])}</p></div><div class="me-regions" id="me-regions">{regions}</div></section>
<section class="me-sec"><h2>{esc(X['others_title'])}</h2><div class="me-others">{others}</div></section>
<section class="me-sec me-method">
<div><h3>{esc(X['method_title'])}</h3><ul>{''.join('<li>' + esc(t) + '</li>' for t in X['method'])}</ul></div>
<div><h3>{esc(X['know_title'])}</h3><ul>{''.join('<li>' + esc(t) + '</li>' for t in X['know'])}</ul></div>
</section>
</main>"""
