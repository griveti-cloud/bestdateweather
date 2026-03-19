#!/usr/bin/env python3
"""5 formats de widgets : compact/small/medium/large/wide"""

import csv, json
from pathlib import Path

SITE_URL = 'https://bestdateweather.com'
MOIS_ABBR = ['Jan','Fév','Mar','Avr','Mai','Jui','Jul','Aoû','Sep','Oct','Nov','Déc']

def load_data():
    with open('data/climate.csv', encoding='utf-8-sig') as f:
        climate = {}
        for r in csv.DictReader(f):
            climate.setdefault(r['slug'], []).append(r)
    for s in climate: climate[s].sort(key=lambda x: int(x['mois_num']))
    with open('data/destinations.csv', encoding='utf-8-sig') as f:
        dests = {r['slug_fr']: r for r in csv.DictReader(f)}
    return climate, dests

def sc(s):
    s=float(s)
    return '#22c55e' if s>=8.5 else ('#f97316' if s>=7 else '#ef4444')

def prep(slug, dest, climate):
    months = climate.get(slug,[])
    if not months: return None
    top3  = sorted(months, key=lambda x:float(x['score']), reverse=True)[:3]
    hott  = max(months, key=lambda x:float(x['tmax']))
    cold  = min(months, key=lambda x:float(x['tmin']))
    dry   = min(months, key=lambda x:float(x['rain_pct']))
    return dict(
        nom=dest.get('nom_fr',slug), pays=dest.get('pays',''), flag=dest.get('flag',''),
        flag_url=f"{SITE_URL}/flags/{dest['flag']}.png" if dest.get('flag') else '',
        fiche=f"{SITE_URL}/meilleure-periode-{slug}.html",
        top3=[MOIS_ABBR[int(m['mois_num'])-1] for m in top3],
        hottest={'t':hott['tmax'],'m':MOIS_ABBR[int(hott['mois_num'])-1]},
        coldest={'t':cold['tmin'],'m':MOIS_ABBR[int(cold['mois_num'])-1]},
        driest={'p':dry['rain_pct'],'m':MOIS_ABBR[int(dry['mois_num'])-1]},
        scores=months,
    )

def flag_img(d, w=20, h=14):
    return f'<img src="{d["flag_url"]}" width="{w}" height="{h}" style="border-radius:2px;flex-shrink:0" alt="">' if d['flag_url'] else ''

def badges(d, fs=11, pad='3px 9px'):
    return ''.join(
        f'<span style="background:#f97316;color:white;padding:{pad};border-radius:20px;font-size:{fs}px;font-weight:700">{m}</span>'
        for m in d['top3']
    )

def bars(d, height=60, sub='#94a3b8'):
    out=''
    for i,m in enumerate(d['scores']):
        s=float(m['score']); h=max(4,int(s/10*height)); c=sc(s)
        out+=(f'<div style="display:flex;flex-direction:column;align-items:center;gap:2px;flex:1">'
              f'<div style="width:100%;background:{c};border-radius:2px 2px 0 0;height:{h}px"></div>'
              f'<span style="font-size:8px;color:{sub}">{MOIS_ABBR[i]}</span></div>')
    return f'<div style="display:flex;gap:2px;align-items:flex-end;height:{height+12}px">{out}</div>'

def stats_grid(d, bg='#f8fafc', text='#0f172a', sub='#94a3b8', border='#f1f5f9'):
    def s(ico,lbl,val,mo):
        return (f'<div style="background:{bg};border-radius:8px;padding:8px;text-align:center">'
                f'<div style="font-size:15px;margin-bottom:2px">{ico}</div>'
                f'<div style="font-size:8px;color:{sub};text-transform:uppercase;letter-spacing:.3px;margin-bottom:2px">{lbl}</div>'
                f'<div style="font-size:13px;font-weight:800;color:{text}">{val}</div>'
                f'<div style="font-size:9px;color:{sub};margin-top:1px">{mo}</div></div>')
    return (f'<div style="padding:10px 14px;border-bottom:1px solid {border}">'
            f'<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:6px">'
            f'{s("🌡️","Chaud",d["hottest"]["t"]+"°C",d["hottest"]["m"])}'
            f'{s("❄️","Froid",d["coldest"]["t"]+"°C",d["coldest"]["m"])}'
            f'{s("🌤️","Sec",d["driest"]["p"]+"%",d["driest"]["m"])}'
            f'</div></div>')

def table_monthly(d, text='#0f172a', sub='#94a3b8', alt='#f8fafc', best='#fff8ec'):
    best_i=max(range(12),key=lambda i:float(d['scores'][i]['score']))
    rows=''
    for i,m in enumerate(d['scores']):
        s=float(m['score']); c=sc(s); ib=i==best_i
        bg=best if ib else (alt if i%2==0 else '#fff')
        fw='font-weight:700;' if ib else ''
        star='⭐' if ib else ''
        bw=max(6,int(s/10*80))
        rows+=(f'<tr style="background:{bg}">'
               f'<td style="padding:3px 10px;font-size:10px;{fw}color:{text}">{star}{MOIS_ABBR[i]}</td>'
               f'<td style="padding:3px 6px;text-align:center;font-size:10px;{fw}color:{c}">{s:.1f}</td>'
               f'<td style="padding:3px 6px;text-align:center;font-size:10px;color:{sub}">{m["tmax"]}°C</td>'
               f'<td style="padding:3px 10px"><div style="height:6px;background:{c};border-radius:3px;width:{bw}%"></div></td>'
               f'</tr>')
    return (f'<table style="width:100%;border-collapse:collapse">'
            f'<thead><tr style="background:{alt}">'
            f'<th style="padding:4px 10px;font-size:8px;font-weight:700;color:{sub};text-align:left;text-transform:uppercase">Mois</th>'
            f'<th style="padding:4px 6px;font-size:8px;font-weight:700;color:{sub};text-transform:uppercase">Score</th>'
            f'<th style="padding:4px 6px;font-size:8px;font-weight:700;color:{sub};text-transform:uppercase">T°max</th>'
            f'<th style="padding:4px 10px;font-size:8px;font-weight:700;color:{sub};text-align:left;text-transform:uppercase">Météo</th>'
            f'</tr></thead><tbody>{rows}</tbody></table>')

def footer(d, bg='#f8fafc', sub='#cbd5e1'):
    return (f'<div style="padding:8px 14px;display:flex;align-items:center;justify-content:space-between;background:{bg}">'
            f'<span style="font-size:9px;color:{sub};font-weight:600">bestdateweather.com</span>'
            f'<a href="{d["fiche"]}" target="_blank" style="background:#f97316;color:white;font-size:10px;font-weight:700;padding:5px 11px;border-radius:7px;text-decoration:none">Guide →</a>'
            f'</div>')

def wrap(body, w, bg='#fff', border='#e2e8f0'):
    return (f'<!DOCTYPE html><html lang="fr"><head><meta charset="UTF-8"/>'
            f'<style>*{{margin:0;padding:0;box-sizing:border-box}}body{{font-family:DM Sans,Arial,sans-serif;'
            f'background:{bg};border:1px solid {border};border-radius:12px;overflow:hidden;width:{w}px}}</style>'
            f'</head><body>{body}</body></html>')

# ─── 5 formats ───────────────────────────────────────────────────────────────

def gen_compact(d):
    """320×165 — dark, header chiffres + meilleur mois/score + barres avec scores"""
    hottest = d['hottest']; driest = d['driest']
    top1_score = max(float(m['score']) for m in d['scores'])
    top1_m = d['top3'][0]
    best_color = sc(top1_score)
    b=''
    for i,m in enumerate(d['scores']):
        s=float(m['score']); h=max(4,int(s/10*44)); c=sc(s)
        b+=(f'<div style="display:flex;flex-direction:column;align-items:center;flex:1;justify-content:flex-end;gap:1px">'
            f'<span style="font-size:7px;color:{c};font-weight:700;line-height:1">{s:.0f}</span>'
            f'<div style="width:100%;background:{c};border-radius:2px 2px 0 0;height:{h}px"></div>'
            f'<span style="font-size:7px;color:#64748b">{MOIS_ABBR[i]}</span></div>')
    body=(f'<div style="background:#1a1f2e;padding:10px 12px 8px">'
          f'<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:6px">'
          f'<div style="display:flex;align-items:center;gap:7px">{flag_img(d,18,13)}'
          f'<div style="font-size:13px;font-weight:800;color:#f1f5f9">{d["nom"]}</div></div>'
          f'<div style="display:flex;align-items:center;gap:6px">'
          f'<span style="font-size:10px;color:#94a3b8">{hottest["t"]}°C</span>'
          f'<span style="font-size:9px;color:#475569">·</span>'
          f'<span style="font-size:10px;color:#94a3b8">{driest["p"]}% pluie</span>'
          f'</div></div>'
          f'<div style="display:flex;align-items:center;gap:8px">'
          f'<span style="font-size:8px;font-weight:700;color:#64748b;text-transform:uppercase;letter-spacing:.4px">Meilleur :</span>'
          f'<span style="background:#f97316;color:white;padding:2px 8px;border-radius:20px;font-size:10px;font-weight:700">{top1_m}</span>'
          f'<span style="font-size:14px;font-weight:800;color:{best_color};margin-left:2px">{top1_score:.1f}'
          f'<span style="font-size:10px;font-weight:500;color:#64748b">/10</span></span>'
          f'</div></div>'
          f'<div style="padding:6px 10px 0;display:flex;gap:1px;align-items:flex-end">{b}</div>'
          f'<div style="padding:3px 12px 6px;display:flex;justify-content:space-between;align-items:center">'
          f'<span style="font-size:8px;color:#475569">bestdateweather.com</span>'
          f'<a href="{d["fiche"]}" target="_blank" style="background:#f97316;color:white;font-size:9px;font-weight:700;padding:3px 9px;border-radius:6px;text-decoration:none">Guide →</a>'
          f'</div>')
    return wrap(body,320,'#0f172a','#1e293b')

def gen_small(d):
    """350×240 — header + badges + stats"""
    hdr=(f'<div style="padding:12px 14px;display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid #f1f5f9">'
         f'<div style="display:flex;align-items:center;gap:8px">{flag_img(d)}'
         f'<div><div style="font-size:14px;font-weight:800;color:#0f172a">{d["nom"]}</div>'
         f'<div style="font-size:10px;color:#94a3b8">{d["pays"]}</div></div></div>'
         f'<span style="background:#f1f5f9;color:#64748b;font-size:9px;font-weight:700;padding:2px 7px;border-radius:20px">10 ans ERA5</span></div>')
    best=(f'<div style="padding:10px 14px;border-bottom:1px solid #f1f5f9">'
          f'<div style="font-size:9px;font-weight:700;color:#94a3b8;text-transform:uppercase;letter-spacing:.5px;margin-bottom:5px">☀️ Meilleure période</div>'
          f'<div style="display:flex;gap:5px">{badges(d)}</div></div>')
    return wrap(hdr+best+stats_grid(d)+footer(d),350)

def gen_medium(d):
    """400×340 — small + graphique"""
    hdr=(f'<div style="padding:12px 14px;display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid #f1f5f9">'
         f'<div style="display:flex;align-items:center;gap:8px">{flag_img(d)}'
         f'<div><div style="font-size:14px;font-weight:800;color:#0f172a">{d["nom"]}</div>'
         f'<div style="font-size:10px;color:#94a3b8">{d["pays"]}</div></div></div>'
         f'<span style="background:#f1f5f9;color:#64748b;font-size:9px;font-weight:700;padding:2px 7px;border-radius:20px">10 ans ERA5</span></div>')
    best=(f'<div style="padding:10px 14px;border-bottom:1px solid #f1f5f9">'
          f'<div style="font-size:9px;font-weight:700;color:#94a3b8;text-transform:uppercase;letter-spacing:.5px;margin-bottom:5px">☀️ Meilleure période</div>'
          f'<div style="display:flex;gap:5px">{badges(d)}</div></div>')
    chart=(f'<div style="padding:10px 14px 6px;border-bottom:1px solid #f1f5f9">'
           f'<div style="font-size:9px;font-weight:700;color:#94a3b8;text-transform:uppercase;letter-spacing:.5px;margin-bottom:5px">📈 Score mensuel</div>'
           f'{bars(d,60)}</div>')
    return wrap(hdr+best+stats_grid(d)+chart+footer(d),400)

def gen_large(d):
    """400×460 — medium + tableau mensuel"""
    hdr=(f'<div style="padding:12px 14px;display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid #f1f5f9">'
         f'<div style="display:flex;align-items:center;gap:8px">{flag_img(d)}'
         f'<div><div style="font-size:14px;font-weight:800;color:#0f172a">{d["nom"]}</div>'
         f'<div style="font-size:10px;color:#94a3b8">{d["pays"]}</div></div></div>'
         f'<span style="background:#f1f5f9;color:#64748b;font-size:9px;font-weight:700;padding:2px 7px;border-radius:20px">10 ans ERA5</span></div>')
    best=(f'<div style="padding:10px 14px;border-bottom:1px solid #f1f5f9">'
          f'<div style="font-size:9px;font-weight:700;color:#94a3b8;text-transform:uppercase;letter-spacing:.5px;margin-bottom:5px">☀️ Meilleure période</div>'
          f'<div style="display:flex;gap:5px">{badges(d)}</div></div>')
    chart=(f'<div style="padding:10px 14px 6px;border-bottom:1px solid #f1f5f9">'
           f'<div style="font-size:9px;font-weight:700;color:#94a3b8;text-transform:uppercase;letter-spacing:.5px;margin-bottom:5px">📈 Score mensuel</div>'
           f'{bars(d,50)}</div>')
    return wrap(hdr+best+stats_grid(d)+chart+f'<div style="border-top:1px solid #f1f5f9">{table_monthly(d)}</div>'+footer(d),400)

def gen_wide(d):
    """600×200 — horizontal : infos gauche + graphique droite"""
    def srow(ico,val,mo):
        return (f'<div style="display:flex;align-items:center;gap:6px;margin-bottom:4px">'
                f'<span style="font-size:14px">{ico}</span>'
                f'<div><div style="font-size:12px;font-weight:700;color:#0f172a">{val}</div>'
                f'<div style="font-size:9px;color:#94a3b8">{mo}</div></div></div>')
    b=''
    for i,m in enumerate(d['scores']):
        s=float(m['score']); h=max(4,int(s/10*64)); c=sc(s)
        b+=(f'<div style="display:flex;flex-direction:column;align-items:center;gap:2px;flex:1">'
            f'<div style="width:100%;background:{c};border-radius:2px 2px 0 0;height:{h}px"></div>'
            f'<span style="font-size:8px;color:#94a3b8">{MOIS_ABBR[i]}</span></div>')
    body=(f'<div style="display:flex;height:200px">'
          # gauche
          f'<div style="width:220px;flex-shrink:0;padding:14px;display:flex;flex-direction:column;justify-content:space-between;border-right:1px solid #e2e8f0">'
          f'<div>'
          f'<div style="display:flex;align-items:center;gap:8px;margin-bottom:8px">{flag_img(d,22,16)}'
          f'<div><div style="font-size:14px;font-weight:800;color:#0f172a">{d["nom"]}</div>'
          f'<div style="font-size:10px;color:#94a3b8">{d["pays"]}</div></div></div>'
          f'<div style="font-size:8px;font-weight:700;color:#94a3b8;text-transform:uppercase;letter-spacing:.5px;margin-bottom:5px">☀️ Meilleure période</div>'
          f'<div style="display:flex;gap:4px;flex-wrap:wrap;margin-bottom:10px">{badges(d,10,"2px 8px")}</div>'
          f'{srow("🌡️",d["hottest"]["t"]+"°C",d["hottest"]["m"])}'
          f'{srow("❄️",d["coldest"]["t"]+"°C",d["coldest"]["m"])}'
          f'</div>'
          f'<a href="{d["fiche"]}" target="_blank" style="background:#f97316;color:white;font-size:11px;font-weight:700;padding:6px 0;border-radius:7px;text-decoration:none;text-align:center;display:block">Guide complet →</a>'
          f'</div>'
          # droite
          f'<div style="flex:1;padding:12px 12px 8px;display:flex;flex-direction:column;justify-content:space-between">'
          f'<div style="font-size:9px;font-weight:700;color:#94a3b8;text-transform:uppercase;letter-spacing:.5px">📈 Score mensuel</div>'
          f'<div style="display:flex;gap:2px;align-items:flex-end;height:80px">{b}</div>'
          f'<div style="font-size:8px;color:#cbd5e1;text-align:right">bestdateweather.com · ERA5</div>'
          f'</div></div>')
    return wrap(body,600)

FORMATS = {
    'compact': gen_compact,
    'small':   gen_small,
    'medium':  gen_medium,
    'large':   gen_large,
    'wide':    gen_wide,
}

def main():
    climate, dests = load_data()
    out = Path('widget'); out.mkdir(exist_ok=True)
    counts = {f:0 for f in FORMATS}
    for slug, dest in dests.items():
        d = prep(slug, dest, climate)
        if not d: continue
        for fmt, fn in FORMATS.items():
            html = fn(d)
            if html:
                (out/f'{slug}-{fmt}.html').write_text(html, encoding='utf-8')
                counts[fmt] += 1
    for fmt,n in counts.items():
        print(f'✅ {n:4d} {fmt}')

    # widget-data.js
    data = {}
    for slug, dest in dests.items():
        months = climate.get(slug,[])
        if not months: continue
        top3  = sorted(months,key=lambda x:float(x['score']),reverse=True)[:3]
        hott  = max(months,key=lambda x:float(x['tmax']))
        cold  = min(months,key=lambda x:float(x['tmin']))
        dry   = min(months,key=lambda x:float(x['rain_pct']))
        data[slug]={
            'nom':dest.get('nom_fr',slug),'pays':dest.get('pays',''),'flag':dest.get('flag',''),
            'top3':[MOIS_ABBR[int(m['mois_num'])-1] for m in top3],
            'hottest':{'t':hott['tmax'],'m':MOIS_ABBR[int(hott['mois_num'])-1]},
            'coldest':{'t':cold['tmin'],'m':MOIS_ABBR[int(cold['mois_num'])-1]},
            'driest':{'p':dry['rain_pct'],'m':MOIS_ABBR[int(dry['mois_num'])-1]},
            'scores':[float(m['score']) for m in months],
        }
    js=f'var BDW_WIDGET_DATA = {json.dumps(data,ensure_ascii=False)};'
    with open('js/widget-data.js','w',encoding='utf-8') as f: f.write(js)
    print(f'✅ widget-data.js — {len(data)} destinations')

if __name__=='__main__':
    main()
