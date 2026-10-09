"""
Rendu HTML du moteur « Où partir à mes dates » pour l'état par défaut d'une page.
Miroir exact des fonctions de rendu de js/date-engine.js : le script remplace
ces blocs à l'identique quand le visiteur change ses critères.
"""
import json
import math

from lib.date_engine import I18N, LEN, PAGE

CSS = r"""
body>nav{position:sticky;top:0;z-index:100;box-shadow:0 2px 12px rgba(26,31,46,.06)}
.me{--bg:#fffdfa;--card:#fff;--ink:#0d1117;--muted:#5f6772;--line:#e8e0d0;--gold:#9c5f00;--gold-strong:#e8940a;--gold-soft:#fef3d0;
--dry:#1a7a4a;--dry-soft:#e3f5ea;--mid:#8a6206;--mid-soft:#fbf0d2;--wet:#b93a0a;--wet-soft:#fbe5da;--chip:#f6f1e7;--focus:#1a5fd0;
color:var(--ink);font-family:'DM Sans',-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;line-height:1.55;max-width:1080px;margin:0 auto;padding:0 16px 48px}
.me *,.me *::before,.me *::after{box-sizing:border-box}
.me [hidden]{display:none!important}
.me a{color:inherit}
.me :focus-visible{outline:2px solid var(--focus);outline-offset:2px}
.me-hero{padding:26px 0 12px;display:grid;gap:8px}
.me-eyebrow{font-size:.78rem;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:var(--muted)}
.me h1{font-family:'Playfair Display',Georgia,serif;font-size:clamp(1.9rem,4.6vw,3rem);line-height:1.08;margin:0;text-wrap:balance;letter-spacing:-.015em}
.me h1 em{color:var(--gold-strong)}
.me-when{font-size:1.05rem;margin:0}
.me-sub{font-size:.9rem;color:var(--muted);margin:0;max-width:80ch}
.me-months{display:flex;gap:4px;flex-wrap:wrap;margin:6px 0 14px}
.me-months a{font-size:.85rem;color:var(--muted);padding:4px 8px;border-radius:6px;text-decoration:none}
.me-months a[aria-current="page"]{background:var(--ink);color:#fff;font-weight:700}
.me-tool{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:18px;display:grid;gap:16px}
.me-row{display:grid;gap:8px;align-content:start;min-width:0}
.me-lbl{font-size:.78rem;font-weight:700;letter-spacing:.06em;text-transform:uppercase;color:var(--muted)}
.me-help{font-size:.82rem;color:var(--muted);margin:0}
.me-chips{display:flex;flex-wrap:wrap;gap:6px}
.me-chip{font:inherit;font-size:.9rem;border:1px solid var(--line);background:var(--chip);color:var(--ink);border-radius:999px;padding:6px 12px;cursor:pointer}
.me-chip[aria-pressed="true"]{background:var(--ink);color:#fff;border-color:var(--ink)}
.me-zone{border-style:dashed}.me-zone[aria-pressed="true"]{border-style:solid}
.me select,.me input[type="date"]{font:inherit;font-size:.95rem;color:var(--ink);background:var(--bg);border:1px solid var(--line);border-radius:8px;padding:7px 10px;width:100%}
.me input[type="range"]{width:100%;accent-color:var(--gold-strong)}
.me-dates{display:flex;align-items:flex-end;gap:10px;flex-wrap:wrap}
.me-dates label{display:grid;gap:4px;font-size:.85rem;color:var(--muted);flex:1 1 170px;max-width:240px}
.me-dates input{font-size:1.05rem!important;font-weight:500;padding:10px 12px!important;border-color:var(--ink)!important}
.me-arrow{font-size:1.2rem;color:var(--muted);padding-bottom:10px}
.me-span{font-weight:700;padding-bottom:11px}
.me-city{display:grid;gap:6px}
.me-city input{font:inherit;font-size:.95rem;color:var(--ink);background:var(--bg);border:1px solid var(--ink);border-radius:8px;padding:8px 10px;width:100%}
.me-city-sug{display:grid;gap:2px}
.me-city-sug button{font:inherit;font-size:.92rem;text-align:left;border:0;background:var(--chip);color:var(--ink);border-radius:6px;padding:7px 10px;cursor:pointer}
.me-city-sug button:hover,.me-city-sug button:focus-visible{background:var(--gold-soft)}
.me-city-sug p{margin:0;font-size:.88rem;color:var(--muted)}
.me-quick{display:flex;align-items:center;gap:8px 10px;flex-wrap:wrap}
.me-quick-lbl{font-size:.88rem;color:var(--muted)}
.me-criteria{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:18px 28px;border-top:1px solid var(--line);padding-top:16px}
.me-wide{grid-column:1/-1}
@media(max-width:760px){.me-criteria{grid-template-columns:1fr}}
.me-facts{display:grid;grid-template-columns:repeat(var(--n,4),minmax(0,1fr));gap:14px;margin:22px 0 8px}
@media(max-width:980px){.me-facts{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media(max-width:560px){.me-facts{grid-template-columns:1fr}}
.me-fact{border-top:3px solid var(--dry);padding-top:10px;display:grid;gap:4px;min-width:0;align-content:start}
.me-fact.warn{border-top-color:var(--wet)}
.me-k{font-size:.78rem;font-weight:700;letter-spacing:.06em;text-transform:uppercase;color:var(--muted)}
.me-v{font-family:'Playfair Display',Georgia,serif;font-size:1.3rem;line-height:1.2;text-decoration:none}
.me-d{font-size:.92rem;color:var(--muted)}
.me h2{font-family:'Playfair Display',Georgia,serif;font-size:1.6rem;margin:0;text-wrap:balance}
.me h3{font-family:'Playfair Display',Georgia,serif;font-size:1.15rem;margin:0}
.me-sec{margin-top:40px;display:grid;gap:14px}
.me-sec-head{display:flex;justify-content:space-between;align-items:baseline;gap:12px;flex-wrap:wrap}
.me-lead{color:var(--muted);font-size:.95rem;margin:0}
.me-sortbox{display:flex;align-items:center;gap:8px;font-size:.9rem}
.me-sortbox select{width:auto}
.me-list{display:grid;border-top:1px solid var(--line)}
.me-item{display:grid;grid-template-columns:2.2rem minmax(0,1.6fr) minmax(0,1fr) minmax(0,1.6fr) auto;gap:14px;align-items:center;padding:13px 0;border-bottom:1px solid var(--line);font-variant-numeric:tabular-nums}
.me-rank{font-family:'Playfair Display',Georgia,serif;font-size:1.25rem;color:var(--muted);text-align:right}
.me-name{min-width:0}.me-name a{font-size:1.05rem;font-weight:700;display:block;text-decoration:none}.me-name a:hover{color:var(--gold)}.me-name span{font-size:.88rem;color:var(--muted)}
.me-badges{display:flex;gap:6px;flex-wrap:wrap;margin-top:4px}
.me-badge{font-size:.74rem;border-radius:999px;padding:1px 8px;background:var(--chip);color:var(--muted)}
.me-badge.v1{background:var(--dry-soft);color:var(--dry)}.me-badge.v2{background:var(--mid-soft);color:var(--mid)}
.me-metrics{display:grid;gap:2px;font-size:.92rem;min-width:0}.me-t{font-weight:700;font-size:1.05rem}
.me-dry{display:grid;gap:5px;min-width:0;font-size:.92rem}
.me-dry b{color:var(--dry)}.me-dry .me-low b{color:var(--wet)}.me-approx{color:var(--muted)}
.me-seasons{display:flex;gap:3px;flex-wrap:wrap}
.me-sq{display:inline-block;width:14px;height:14px;border-radius:3px;background:var(--line)}
.me-sq.d{background:var(--dry)}.me-sq.m{background:#c08a0e}.me-sq.w{background:var(--wet)}
.me-side{display:grid;gap:6px;justify-items:end}
.me-score{font-weight:700;font-size:.95rem;border-radius:8px;padding:3px 8px;background:var(--dry-soft);color:var(--dry)}
.me-score.mid{background:var(--mid-soft);color:var(--mid)}.me-score.low{background:var(--wet-soft);color:var(--wet)}
.me-side a,.me-link{font-size:.88rem;font-weight:700;color:var(--gold);text-decoration:none;background:none;border:0;padding:0;cursor:pointer;font-family:inherit}
.me-side a:hover,.me-link:hover{text-decoration:underline}
@media(max-width:760px){.me-item{grid-template-columns:2rem minmax(0,1fr) auto;row-gap:8px}.me-metrics,.me-dry{grid-column:2/4}.me-side{grid-row:1;grid-column:3}}
.me-more{font:inherit;font-weight:700;justify-self:start;border:1px solid var(--line);background:var(--card);color:var(--ink);border-radius:999px;padding:8px 16px;cursor:pointer}
.me-empty{padding:20px 0;color:var(--muted)}
.me-legend{display:flex;gap:14px;flex-wrap:wrap;font-size:.85rem;color:var(--muted)}
.me-legend span{display:inline-flex;align-items:center;gap:6px}
.me-cols{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:22px}
.me-regions{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:22px}
@media(max-width:760px){.me-cols{grid-template-columns:1fr}}
.me-box{display:grid;gap:8px;align-content:start;min-width:0}
.me-box-head{display:flex;justify-content:space-between;align-items:baseline;gap:8px;border-bottom:1px solid var(--line);padding-bottom:6px}
.me-mini{display:grid;gap:6px;margin:0;padding:0;list-style:none}
.me-mini li{display:flex;flex-wrap:wrap;align-items:baseline;column-gap:8px;font-size:.92rem;font-variant-numeric:tabular-nums}
.me-mini li a{min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;text-decoration:none}
.me-mini li a:hover{color:var(--gold)}
.me-mini li>span:last-child{color:var(--muted);white-space:nowrap;margin-left:auto}
.me-mini li b{color:var(--ink)}
.me-avoid li>span:last-child b{color:var(--wet)}
.me-hol{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:repeat(2,minmax(0,1fr));column-gap:28px;border-top:1px solid var(--line)}
@media(max-width:760px){.me-hol{grid-template-columns:1fr}}
.me-hol li{display:grid;grid-template-columns:1.6rem minmax(0,1fr);column-gap:8px;padding:9px 0;border-bottom:1px solid var(--line);font-size:.92rem;font-variant-numeric:tabular-nums}
.me-hol-n{font-family:'Playfair Display',Georgia,serif;color:var(--muted);grid-row:1/3}
.me-hol-d a{font-weight:700;text-decoration:none}.me-hol-d a:hover{color:var(--gold)}
.me-hol-x{color:var(--muted)}.me-hol-x b{color:var(--ink)}
.me-box .me-hol{grid-template-columns:1fr}
.me-others{display:flex;gap:8px;flex-wrap:wrap}
.me-others a{font-size:.9rem;border:1px solid var(--line);background:var(--card);border-radius:10px;padding:8px 12px;text-decoration:none}
.me-method{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:24px;border-top:1px solid var(--line);padding-top:22px}
@media(max-width:760px){.me-method{grid-template-columns:1fr}}
.me-method li{font-size:.92rem;color:var(--muted);max-width:65ch}
.me-method ul{padding-left:18px;margin:6px 0 0;display:grid;gap:4px}
"""


def esc(s):
    return str(s).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')


def fmt(_tpl, /, **o):
    import re
    return re.sub(r'\{(\w+)\}', lambda m: str(o[m.group(1)]) if m.group(1) in o else m.group(0), _tpl)


def js_round(x):
    return math.floor(x + 0.5)


class R:
    """Fonctions de mise en forme liées à une langue (identiques au script client)."""

    def __init__(self, lang, annual_tpl):
        self.lang, self.L, self.T = lang, I18N[lang], I18N[lang]['t']
        self.nf = self.L['nf']
        self.ni = self.nf['ni']
        self.imp = bool(self.nf['imp'])          # en-us : °F et miles
        self.U = ' °F' if self.imp else ' °C'
        self.annual = annual_tpl

    def f1(self, x):
        s = '%.1f' % (js_round(x * 10 + 1e-9) / 10)
        return s.replace('.', ',') if self.nf['dec'] == ',' else s

    def r0(self, x):
        return str(js_round(x))

    def tc(self, x):
        """Température (données en °C) dans l'unité de la langue."""
        return x * 9 / 5 + 32 if self.imp else x

    def t1(self, x):
        """Température précise : 1 décimale en °C, entier en °F."""
        return self.r0(self.tc(x)) if self.imp else self.f1(x)

    def t0(self, x):
        """Température arrondie à l'entier."""
        return self.r0(self.tc(x))

    def fmt_h(self, h):
        t = js_round(h * 12) * 5
        return fmt(self.nf['h'], h=t // 60, mm=f'{t % 60:02d}')

    def fmt_km(self, km):
        v = km / 1.609344 if self.imp else km
        n, sep, out = str(js_round(v)), self.nf['th'], ''
        while len(n) > 3:
            out = sep + n[-3:] + out
            n = n[:-3]
        return n + out + (' mi' if self.imp else ' km')

    def day_num(self, d):
        return self.nf['first'] if (d == 1 and self.nf['first']) else str(d)

    def long_date(self, iso):
        import datetime as dt
        d = dt.date.fromisoformat(iso)
        return fmt(self.nf['date'], wd=self.L['wd'][(d.weekday() + 1) % 7], d=self.day_num(d.day),
                   m=self.L['months'][d.month - 1], y=d.year)

    def href(self, x):
        return fmt(self.annual, s=x['d']['s'], e=x['d']['e'], se=x['d'].get('se', ''), sd=x['d'].get('sd', ''))

    def nm(self, x):
        return esc(x['d']['n'][self.ni])

    def where(self, st):
        h = holiday(self.L, st)
        if st['preset'] == 'month':
            return self.L['months'][st['month']]
        if h:
            return h.get('wh') or (h['chip'][0].lower() + h['chip'][1:])
        return self.T['your_dates_where']

    def dry_txt(self, x, w):
        T = self.T
        if x['daily']:
            return fmt(T['dry_years'], k=x['dry'], n=x['ns'])
        return fmt(T['lt1'], n=w['n']) if x['mean'] < 0.5 else fmt(T['approx_days'], x=self.f1(x['mean']), n=w['n'])

    def fact_text(self, f, w, st):
        x, L = f['x'], self.L
        s = fmt(self.T[f['fn']], t=self.t1(x['tmax']), h=self.fmt_h(x['h']), dep=L['deps'][st['dep']][0],
                b=L['budget'][str(x['d']['bi'])].lower(), dry=self.dry_txt(x, w), bm=L['months'][x['best']],
                bs=self.f1(x['bestSc']), x=self.f1(x['mean']), n=w['n'], s=self.f1(x['score']),
                tn=self.t0(x['tmin']), tx=self.t0(x['tmax']))
        return s[0].upper() + s[1:] if f['fn'] == 'fd_safe' else s


def holiday(L, st):
    for h in L['holidays'].get(str(st['month']), []):
        if h['id'] == st['preset']:
            return h
    return None


def score_cls(s):
    return '' if s >= 7.6 else (' mid' if s >= 5 else ' low')


def dry_html(r, x, w):
    T = r.T
    if x['uc'] == 'ski':
        return '<div class="me-approx">' + esc(fmt(T['ski_line'], s=r.f1(x['sun']), tn=r.t0(x['tmin']))) + '</div>'
    if x['daily']:
        sq = ''
        for s in x['seasons']:
            c = 'd' if s['rd'] <= w['limit'] else ('m' if s['rd'] <= 2 * w['limit'] else 'w')
            y = f"{s['y']}-{str(s['y'] + 1)[2:]}" if w['cross'] else str(s['y'])
            sq += '<span class="me-sq ' + c + '" title="' + esc(fmt(T['season_title'], y=y, r=s['rd'], p='s' if s['rd'] > 1 else '')) + '"></span>'
        low = ' class="me-low"' if x['dry'] / x['ns'] < 0.5 else ''
        return '<div' + low + '>' + fmt(T['dry_line'], k=x['dry'], n=x['ns'], x=r.f1(x['mean']), d=w['n']) + '</div><div class="me-seasons">' + sq + '</div>'
    inner = fmt(T['approx_lt1'], n=w['n']) if x['mean'] < 0.5 else fmt(T['approx_n'], x=r.f1(x['mean']), n=w['n'])
    return '<div class="me-approx">' + esc(fmt(T['approx_line'], x=inner)) + '</div>'


def item_html(r, x, i, w):
    L, T = r.L, r.T
    badges = ('<span class="me-badge v' + str(x['rl']) + '">' + esc(L['secu'][str(x['rl'])]) + '</span>'
              '<span class="me-badge">' + esc(L['budget'][str(max(1, min(5, x['d']['bi'])))]) + '</span>')
    temp = (r.t0(x['tmin']) + ' / ' + r.t0(x['tmax']) + r.U) if x['uc'] == 'ski' else (r.t1(x['tmax']) + r.U)
    sub = (fmt(T['sea'], t=r.t1(x['sea'])) + ' · ' if (x['sea'] is not None and x['uc'] != 'ski') else '') + fmt(T['flight'], h=r.fmt_h(x['h']))
    return ('<article class="me-item"><div class="me-rank">' + str(i + 1) + '</div>'
            '<div class="me-name"><a href="' + r.href(x) + '">' + r.nm(x) + '</a><span>' + esc(x['d']['p'][r.ni]) + ' · ' + r.fmt_km(x['km']) + '</span><div class="me-badges">' + badges + '</div></div>'
            '<div class="me-metrics"><span class="me-t">' + temp + '</span><span>' + esc(sub) + '</span></div>'
            '<div class="me-dry">' + dry_html(r, x, w) + '</div>'
            '<div class="me-side"><span class="me-score' + score_cls(x['score']) + '">' + r.f1(x['score']) + '/10</span><a href="' + r.href(x) + '">' + esc(T['card']) + '</a></div></article>')


def mini_li(r, x, show_p):
    rain = (r.t0(x['tmin']) + '/' + r.t0(x['tmax']) + r.U) if x['uc'] == 'ski' else fmt(r.T['mini_rain'], t=r.t0(x['tmax']), r=r.r0(x['share'] * 100))
    p = (' <span class="me-help">(' + esc(x['d']['p'][r.ni]) + ')</span>') if show_p else ''
    return '<li><a href="' + r.href(x) + '">' + r.nm(x) + '</a>' + p + '<span>' + esc(rain) + ' · <b>' + r.f1(x['score']) + '</b></span></li>'


def chips(items, cur, numeric=True, cls='me-chip'):
    out = ''
    for v, l in items:
        out += f'<button type="button" class="{cls}" data-v="{v}" aria-pressed="{"true" if v == cur else "false"}">{esc(l)}</button>'
    return out


def render_main(view, st, lang, annual_tpl, month_links, other_links, texts):
    """Corps complet de la page (outil + résultats) pour l'état par défaut."""
    r = R(lang, annual_tpl)
    L, T = r.L, r.T
    w = view['w']
    m = st['month']
    h = holiday(L, st)
    hs = L['holidays'].get(str(m), [])
    # en-tête
    h1 = fmt(T['h1_month'], m=L['months'][m])
    when = fmt(T['when'], a=r.long_date(st['from']), b=r.long_date(st['to']), n=w['n'])
    months_nav = ''.join(
        f'<a href="{u}"' + (' aria-current="page"' if i == m else '') + f'>{esc(L["ms"][i])}</a>' for i, u in enumerate(month_links))
    presets = (f'<button type="button" class="me-chip" data-p="month" aria-pressed="true">{esc(fmt(T["all_month"], m=L["months"][m]))}</button>'
               + ''.join(f'<button type="button" class="me-chip" data-p="{x["id"]}" aria-pressed="false">{esc(x["chip"])}{" ▾" if x.get("zones") else ""}</button>' for x in hs))
    uc_chips = ''.join(f'<button type="button" class="me-chip" data-v="{k}" aria-pressed="{"true" if k == st["uc"] else "false"}">{esc(v)}</button>' for k, v in L['uc'].items())
    reg_opts = f'<option value="all">{esc(T["world"])}</option>' + ''.join(f'<option value="{k}">{esc(v)}</option>' for k, v in L['regions'].items())
    dep_opts = ''.join(f'<option value="{i}"' + (' selected' if i == st['dep'] else '') + f'>{esc(d[0])}</option>' for i, d in enumerate(L['deps'])) + f'<option value="other">{esc(T["other_city"])}</option>'
    allowed = ['score', 'dry', 'hot', 'near', 'cheap']
    sort_opts = ''.join(f'<option value="{k}"' + (' selected' if k == st['sort'] else '') + f'>{esc(L["sorts"][k])}</option>' for k in allowed)
    # à retenir
    facts = ''.join('<div class="me-fact' + (' ' + f['cls'] if f['cls'] else '') + '"><div class="me-k">' + esc(T[f['k']]) + '</div><a class="me-v" href="' + r.href(f['x']) + '">' + r.nm(f['x']) + '</a><div class="me-d">' + esc(r.fact_text(f, w, st)) + '</div></div>' for f in view['facts'])
    rows = view['rows']
    rank_title = fmt(T['top'], n=min(st['shown'], len(rows)), uc=L['uc_t'][st['uc']], reg='', where=r.where(st))
    count = fmt(T['count'] if len(rows) > 1 else T['count1'], k=len(rows), n=view['n_uc'])
    lst = ''.join(item_html(r, x, i, w) for i, x in enumerate(rows[:st['shown']])) or '<p class="me-empty">' + esc(T['empty']) + '</p>'
    lim = w['limit']
    legend = ('<span><i class="me-sq d"></i>' + esc(fmt(T['lg_dry'], l=lim)) + '</span><span><i class="me-sq m"></i>' + esc(fmt(T['lg_mid'], a=lim + 1, b=2 * lim))
              + '</span><span><i class="me-sq w"></i>' + esc(fmt(T['lg_wet'], b=2 * lim)) + '</span><span>' + esc(T['lg_one_s'] if w['cross'] else T['lg_one_y'])
              + '</span><span>' + esc(T['lg_approx']) + '</span>')
    projects = ''
    for k in ('plage', 'ski', 'rando'):
        top = view['projects'][k]
        lis = ''.join(mini_li(r, x, False) for x in top) or '<li><span>' + esc(T['none']) + '</span></li>'
        projects += f'<div class="me-box"><div class="me-box-head"><h3>{esc(L["uc"][k])}</h3><button type="button" class="me-link" data-uc="{k}">{esc(T["see_all"])}</button></div><ul class="me-mini">{lis}</ul></div>'
    regions = ''
    for k in L['regions']:
        if k in view['regions']:
            regions += f'<div class="me-box"><div class="me-box-head"><h3>{esc(L["regions"][k])}</h3><button type="button" class="me-link" data-reg="{k}">{esc(T["see"])}</button></div><ul class="me-mini">' + ''.join(mini_li(r, x, False) for x in view['regions'][k]) + '</ul></div>'
    avoid = ''.join(mini_li(r, x, True) for x in view['avoid'])
    others = ''.join(f'<a href="{u}">{esc(t)}</a>' for t, u in other_links)
    X = texts
    return f"""<main class="me" id="me">
<section class="me-hero">
<div class="me-eyebrow">{esc(X['eyebrow'])}</div>
<h1 id="me-h1">{h1}</h1>
<p class="me-when" id="me-when">{when}</p>
<p class="me-sub" id="me-sub">{esc(T['sub_month'])}</p>
</section>
<div class="me-months" role="navigation" aria-label="{esc(X['months_label'])}">{months_nav}</div>
<form class="me-tool" id="me-tool" aria-label="{esc(X['criteria'])}">
<div class="me-row">
<div class="me-lbl">{esc(X['your_dates'])}</div>
<div class="me-dates"><label for="me-from">{esc(X['dep_date'])}<input type="date" id="me-from" value="{st['from']}" lang="{L['nf']['hl']}"></label><span class="me-arrow" aria-hidden="true">→</span><label for="me-to">{esc(X['ret_date'])}<input type="date" id="me-to" value="{st['to']}" lang="{L['nf']['hl']}"></label><span class="me-span" id="me-span">{esc(fmt(T['n_days'], n=w['n']))}</span></div>
<div class="me-quick"><span class="me-quick-lbl" id="me-lbl-quick">{esc(X['shortcuts'])}</span><div class="me-chips" id="me-presets" role="group" aria-labelledby="me-lbl-quick">{presets}</div></div>
<div class="me-chips" id="me-zone" role="group" aria-label="{esc(X['zone_label'])}" hidden></div>
</div>
<div class="me-criteria">
<div class="me-row me-wide"><div class="me-lbl" id="me-lbl-uc">{esc(X['trip_type'])}</div><div class="me-chips" id="me-uc" role="group" aria-labelledby="me-lbl-uc">{uc_chips}</div></div>
<div class="me-row"><label class="me-lbl" for="me-reg">{esc(X['region'])}</label><select id="me-reg">{reg_opts}</select></div>
<div class="me-row"><label class="me-lbl" for="me-dep">{esc(X['from_city'])}</label><select id="me-dep">{dep_opts}</select><div class="me-city" id="me-city" hidden><input type="search" id="me-city-q" autocomplete="off" placeholder="{esc(T['city_ph'])}" aria-label="{esc(T['city_ph'])}"><div class="me-city-sug" id="me-city-sug" role="listbox"></div></div></div>
<div class="me-row"><label class="me-lbl" for="me-fly">{esc(X['max_flight'])} <span id="me-fly-val">{esc(T['fly_any'])}</span></label><input type="range" id="me-fly" min="1" max="16" step="0.5" value="{st['fly']}"></div>
<div class="me-row" id="me-heat-row"><div class="me-lbl" id="me-lbl-heat">{esc(X['heat'])}</div><div class="me-chips" id="me-heat" role="group" aria-labelledby="me-lbl-heat">{chips(L['heat_opts'], st['heat'])}</div></div>
<div class="me-row"><div class="me-lbl" id="me-lbl-budget">{esc(X['budget'])}</div><div class="me-chips" id="me-budget" role="group" aria-labelledby="me-lbl-budget">{chips(L['budget_opts'], st['budget'])}</div><p class="me-help">{esc(X['budget_help'])}</p></div>
<div class="me-row"><div class="me-lbl" id="me-lbl-secu">{esc(X['safety'])}</div><div class="me-chips" id="me-secu" role="group" aria-labelledby="me-lbl-secu">{chips(L['secu_opts'], st['rl'])}</div><p class="me-help">{esc(X['safety_help'])}</p></div>
</div>
</form>
<section class="me-facts" id="me-facts" style="--n:{max(1, len(view['facts']))}" aria-label="{esc(X['key_points'])}">{facts}</section>
<section class="me-sec" id="me-classement">
<div class="me-sec-head"><div><h2 id="me-rank-title">{esc(rank_title)}</h2><div class="me-lead" id="me-count">{esc(count)}</div></div><label class="me-sortbox" for="me-sort">{esc(X['sort_by'])} <select id="me-sort">{sort_opts}</select></label></div>
<div class="me-list" id="me-list">{lst}</div>
<button type="button" class="me-more" id="me-more"{'' if len(rows) > st['shown'] else ' hidden'}>{esc(X['more'])}</button>
<div class="me-legend" id="me-legend">{legend}</div>
</section>
<section class="me-sec"><div><h2>{esc(X['projects_title'])}</h2><p class="me-lead">{esc(X['projects_lead'])}</p></div><div class="me-cols" id="me-projects">{projects}</div></section>
<section class="me-sec"><div><h2 id="me-reg-title">{esc(fmt(T['reg_title'], where=r.where(st)))}</h2><p class="me-lead">{esc(X['regions_lead'])}</p></div><div class="me-regions" id="me-regions">{regions}</div></section>
<section class="me-sec"><div><h2 id="me-avoid-title">{esc(fmt(T['avoid_title'], where=r.where(st)))}</h2><p class="me-lead" id="me-avoid-lead">{esc(fmt(T['avoid_lead'], n=view['n_gen']))}</p></div><ul class="me-mini me-avoid me-regions" id="me-avoid">{avoid}</ul></section>
<section class="me-sec"><h2>{esc(X['others_title'])}</h2><div class="me-others">{others}</div></section>
<section class="me-sec me-method">
<div><h3>{esc(X['method_title'])}</h3><ul>{''.join('<li>' + esc(t) + '</li>' for t in X['method'])}</ul></div>
<div><h3>{esc(X['know_title'])}</h3><ul>{''.join('<li>' + esc(t) + '</li>' for t in X['know'])}</ul></div>
</section>
</main>"""


def client_config(lang, st, data_url, annual_tpl):
    L = I18N[lang]
    keep = {k: L[k] for k in ('months', 'ms', 'wd', 'uc', 'uc_t', 'regions', 'secu', 'budget', 'sorts', 'deps', 'holidays', 'zones', 't', 'nf')}
    return json.dumps({'lang': lang, 'state': st, 'data': data_url, 'annual': annual_tpl, 'page': PAGE, 'i18n': keep},
                      ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
