import os
#!/usr/bin/env python3
import json, csv, time, urllib.request, urllib.error, sys

KEY = os.environ.get('ANTHROPIC_API_KEY', '')
OUTPUT = 'data/editorial.json'
API = 'https://api.anthropic.com/v1/messages'
MODEL = 'claude-haiku-4-5-20251001'
LANGS = ['fr','en','es','de']

MONTHS = {
    'fr': ['Janvier','Fevrier','Mars','Avril','Mai','Juin','Juillet','Aout','Septembre','Octobre','Novembre','Decembre'],
    'en': ['January','February','March','April','May','June','July','August','September','October','November','December'],
    'es': ['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre'],
    'de': ['Januar','Februar','Maerz','April','Mai','Juni','Juli','August','September','Oktober','November','Dezember'],
}

SYS = {
    'fr': "Redacteur guides de voyage. 2-3 phrases max 55 mots sur la meteo d'une destination un mois. Style ami expert, positif mais honnete. Francais, texte brut.",
    'en': "Travel guide writer. 2-3 sentences max 55 words about weather at a destination in a given month. Knowledgeable friend style, honest. English plain text.",
    'es': "Redactor guias de viaje. 2-3 frases max 55 palabras sobre el clima. Amigo experto, honesto. Espanol, texto simple.",
    'de': "Reisefuehrer-Autor. 2-3 Saetze max 55 Woerter ueber Wetter. Freundlich, ehrlich. Deutsch, einfacher Text.",
}

def build_user(lang, nom, pays, month, bmonth, tmin, tmax, rain, sun, score, bs, sea_v):
    sea = ", sea {:.0f}C".format(sea_v) if sea_v else ""
    if lang == 'fr':
        return "Dest:{} ({}) Mois:{} {:.0f}-{:.0f}C pluie:{:.0f}% soleil:{:.1f}h score:{:.1f}/10 meilleur:{} ({:.1f}/10){}. Redige Notre avis, commence directement.".format(nom, pays, month, tmin, tmax, rain, sun, score, bmonth, bs, sea)
    elif lang == 'en':
        return "Dest:{} ({}) Month:{} {:.0f}-{:.0f}C rain:{:.0f}% sun:{:.1f}h score:{:.1f}/10 best:{} ({:.1f}/10){}. Write Our take, start directly.".format(nom, pays, month, tmin, tmax, rain, sun, score, bmonth, bs, sea)
    elif lang == 'es':
        return "Dest:{} ({}) Mes:{} {:.0f}-{:.0f}C lluvia:{:.0f}% sol:{:.1f}h punt:{:.1f}/10 mejor:{} ({:.1f}/10){}. Escribe Nuestra opinion, empieza directamente.".format(nom, pays, month, tmin, tmax, rain, sun, score, bmonth, bs, sea)
    else:
        return "Dest:{} ({}) Monat:{} {:.0f}-{:.0f}C Regen:{:.0f}% Sonne:{:.1f}h Score:{:.1f}/10 Bester:{} ({:.1f}/10){}. Schreibe Unser Fazit, beginne direkt.".format(nom, pays, month, tmin, tmax, rain, sun, score, bmonth, bs, sea)

def api_call(system, user):
    payload = json.dumps({'model': MODEL, 'max_tokens': 250, 'system': system, 'messages': [{'role': 'user', 'content': user}]}).encode()
    for i in range(3):
        try:
            req = urllib.request.Request(API, data=payload, headers={'Content-Type': 'application/json', 'anthropic-version': '2023-06-01', 'x-api-key': KEY}, method='POST')
            with urllib.request.urlopen(req, timeout=45) as r:
                return json.loads(r.read())['content'][0]['text'].strip()
        except urllib.error.HTTPError as e:
            if e.code == 429:
                print("  Rate limit, pause 65s...")
                sys.stdout.flush()
                time.sleep(65)
                continue
            raise
        except Exception:
            if i < 2:
                time.sleep(5)
                continue
            raise

ed = json.load(open(OUTPUT))
clim = {}
for r in csv.DictReader(open('data/climate.csv', encoding='utf-8-sig')):
    clim.setdefault(r['slug'], []).append(r)
dests = {r['slug_fr']: r for r in csv.DictReader(open('data/destinations.csv', encoding='utf-8-sig'))}

slugs = open('/tmp/remaining.txt').read().split()
done_slugs = set(k.split(':')[0] for k in ed)
todo = [s for s in slugs if s not in done_slugs]
total_calls = len(todo) * 48
print("A traiter: {} destinations, {} appels".format(len(todo), total_calls))
sys.stdout.flush()

n = 0
for slug in todo:
    months = sorted(clim.get(slug, []), key=lambda r: int(r['mois_num']))
    dest = dests.get(slug)
    if not dest or not months:
        continue
    best = max(months, key=lambda r: float(r['score']))
    bmi = int(best['mois_num']) - 1
    bs = float(best['score'])

    for row in months:
        mi = int(row['mois_num']) - 1
        tmin = float(row['tmin'])
        tmax = float(row['tmax'])
        rain = float(row['rain_pct'])
        sun = float(row['sun_h'])
        score = float(row['score'])
        sea_raw = row.get('sea_temp', '')
        sea_v = float(sea_raw) if sea_raw and sea_raw not in ('', 'nan') else None

        for lang in LANGS:
            k = "{}:{}:{}".format(slug, mi + 1, lang)
            if k in ed:
                continue
            M = MONTHS[lang]
            month = M[mi]
            bmonth = M[bmi]
            nc = {'fr': 'nom_fr', 'en': 'nom_en', 'es': 'nom_es', 'de': 'nom_de'}[lang]
            pc = {'fr': 'pays', 'en': 'country_en', 'es': 'country_es', 'de': 'country_de'}[lang]
            nom = (dest.get(nc, '') or dest.get('nom_bare', '')).replace('nan', '').strip() or slug
            pays = (dest.get(pc, '') or dest.get('pays', '')).replace('nan', '').strip()
            user = build_user(lang, nom, pays, month, bmonth, tmin, tmax, rain, sun, score, bs, sea_v)
            try:
                text = api_call(SYS[lang], user)
                ed[k] = text
                n += 1
                if n % 192 == 0:
                    json.dump(ed, open(OUTPUT, 'w'), ensure_ascii=False, indent=2)
                    print("[{}/{} {:.0f}%] {} {} ({}): {}...".format(n, total_calls, n/total_calls*100, nom, month, lang, text[:50]))
                    sys.stdout.flush()
                time.sleep(0.3)
            except Exception as ex:
                print("ERR {}: {}".format(k, ex))
                sys.stdout.flush()

json.dump(ed, open(OUTPUT, 'w'), ensure_ascii=False, indent=2)
print("Termine: {} generes, total={}".format(n, len(ed)))
