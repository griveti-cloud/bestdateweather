#!/usr/bin/env python3
"""
Normales de stations publiées (Wikipédia EN, tables « Weather box ») pour
calibrer les données ERA5 : jours de pluie (>= 1 mm) et température maximale.

Les tables Wikipédia reprennent les normales officielles (Météo-France, AEMET,
NOAA, DWD, JMA, IPMA…), en général 1991-2020. Même méthode que la correction
de l'ensoleillement d'août 2026 :
- VALIDATION PAR COORDONNÉES : la page est rejetée si elle est à plus de
  MAX_KM de la destination (évite les homonymes) ;
- seule l'unité « 1 mm » (ou « 1.0 mm ») est acceptée pour les jours de
  pluie : les seuils 0,1 / 0,2 / 0,25 mm (NOAA, BoM) ne sont pas comparables.

Reprenable : les résultats sont écrits après chaque destination dans
data/station_normals.json. Accès par index.php?action=raw, 1 requête/s.

Usage : python3 scripts/fetch_station_normals.py [--only slug,slug] [--refresh]
"""
import argparse
import csv
import json
import math
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
OUT = os.path.join(ROOT, 'data', 'station_normals.json')
UA = 'Mozilla/5.0 (compatible; BestDateWeather-normals/1.0; +https://bestdateweather.com)'
MAX_KM = 120
MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

# Destinations « région » : ville de la station la plus représentative du
# séjour touristique (le point du site peut être au centre, en altitude).
STATION_HINTS = {
    'bali': ['Denpasar'], 'canaries': ['Puerto del Rosario', 'Fuerteventura'],
    'reunion': ['Saint-Denis, Réunion'], 'corse': ['Ajaccio'], 'sardaigne': ['Cagliari'],
    'sicile': ['Palermo', 'Catania'], 'crete': ['Heraklion'], 'majorque': ['Palma de Mallorca'],
    'madere': ['Funchal'], 'guadeloupe': ['Pointe-à-Pitre', 'Les Abymes'], 'martinique': ['Fort-de-France'],
    'maldives': ['Malé'], 'seychelles': ['Victoria, Seychelles'], 'cap-vert': ['Praia', 'Sal, Cape Verde'],
    'algarve': ['Faro, Portugal'], 'cote-azur': ['Nice'], 'provence': ['Marseille', 'Avignon'],
    'bretagne': ['Brest, France', 'Rennes'], 'normandie': ['Caen', 'Rouen'], 'toscane': ['Florence'],
    'costa-rica': ['San José, Costa Rica'], 'jamaique': ['Kingston, Jamaica', 'Montego Bay'],
    'sri-lanka': ['Colombo'], 'goa': ['Panaji'], 'kerala': ['Kochi'], 'rajasthan': ['Jaipur'],
    'malte': ['Valletta', 'Luqa'], 'chypre': ['Larnaca', 'Limassol'], 'ibiza': ['Ibiza (town)', 'Ibiza'],
    'minorque': ['Mahón'], 'formentera': ['Ibiza'], 'mykonos': ['Mykonos'], 'santorin': ['Santorini'],
    'rhodes': ['Rhodes (city)', 'Rhodes'], 'corfou': ['Corfu (city)', 'Corfu'], 'acores': ['Ponta Delgada'],
    'sao-miguel': ['Ponta Delgada'], 'polynesie': ['Papeete'], 'tahiti': ['Papeete'], 'bora-bora': ['Bora Bora'],
    'moorea': ['Papeete'], 'nouvelle-caledonie': ['Nouméa'], 'philippines': ['Manila'], 'luzon': ['Manila'],
    'lombok': ['Mataram'], 'java': ['Yogyakarta', 'Jakarta'], 'madagascar': ['Antananarivo'],
    'kenya': ['Nairobi', 'Mombasa'], 'tanzanie': ['Dar es Salaam'], 'senegal': ['Dakar'],
    'namibie': ['Windhoek'], 'oman': ['Muscat'], 'jordanie': ['Amman'], 'bahamas': ['Nassau, Bahamas'],
    'panama': ['Panama City'], 'colombie': ['Bogotá'], 'perou': ['Lima'], 'chili': ['Santiago'],
    'bolivie': ['La Paz'], 'equateur': ['Quito'], 'uruguay': ['Montevideo'], 'guatemala': ['Guatemala City'],
    'belize': ['Belize City'], 'nicaragua': ['Managua'], 'cambodge': ['Phnom Penh'], 'laos': ['Vientiane'],
    'myanmar': ['Yangon'], 'nepal': ['Kathmandu'], 'bhutan': ['Thimphu'], 'mongolie': ['Ulaanbaatar'],
    'ouzbekistan': ['Tashkent', 'Samarkand'], 'georgie': ['Tbilisi'], 'albanie': ['Tirana'],
    'montenegro': ['Podgorica', 'Budva'], 'baie-halong': ['Hạ Long', 'Hai Phong'], 'borneo': ['Kota Kinabalu'],
    'fidji': ['Nadi', 'Suva'], 'vanuatu': ['Port Vila'], 'tonga': ["Nuku'alofa"], 'iles-cook': ['Rarotonga'],
    'papouasie': ['Port Moresby'], 'trinite-et-tobago': ['Port of Spain'], 'bermudes': ['Bermuda'],
    'guyane': ['Cayenne'], 'nouvelle-zelande': ['Auckland', 'Christchurch'], 'patagonie': ['Punta Arenas', 'El Calafate'],
    'whitsundays': ['Proserpine, Queensland', 'Airlie Beach'], 'bay-of-islands': ['Kerikeri', 'Paihia'],
    'cappadoce': ['Nevşehir', 'Göreme'], 'pouilles': ['Bari'], 'lac-come': ['Como'], 'lac-garde': ['Riva del Garda', 'Verona'],
    'cinque-terre': ['La Spezia'], 'amalfi': ['Naples', 'Salerno'], 'costa-brava': ['Girona', 'Barcelona'],
    'pays-basque': ['Biarritz', 'San Sebastián'], 'dordogne': ['Bergerac, Dordogne', 'Périgueux'], 'alsace': ['Strasbourg'],
    'gozo': ['Victoria, Gozo', 'Valletta'], 'elba': ['Portoferraio'], 'alentejo': ['Évora', 'Beja, Portugal'],
    'cotswolds': ['Cheltenham', 'Oxford'], 'cape-cod': ['Hyannis, Massachusetts', 'Chatham, Massachusetts'],
    'outer-banks': ['Cape Hatteras', 'Kill Devil Hills, North Carolina'], 'wild-atlantic-way': ['Galway', 'Shannon Airport'],
    'lac-bled': ['Bled', 'Ljubljana'], 'bahrein': ['Manama'], 'trinite': ['Port of Spain'],
}

DAYS_IN_MONTH = [31, 28.25, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]


def haversine(a, b, c, d):
    la1, lo1, la2, lo2 = map(math.radians, (a, b, c, d))
    x = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 6371 * 2 * math.asin(math.sqrt(x))


_last = [0.0]


def raw(title):
    """Wikitext brut d'une page (suit les redirections). None si absente."""
    for _ in range(4):
        wait = 1.1 - (time.time() - _last[0])
        if wait > 0:
            time.sleep(wait)
        _last[0] = time.time()
        url = 'https://en.wikipedia.org/w/index.php?' + urllib.parse.urlencode({'title': title, 'action': 'raw'})
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': UA}), timeout=30) as r:
                txt = r.read().decode('utf-8', 'replace')
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None, title
            if e.code == 429:
                time.sleep(30)
                continue
            return None, title
        except Exception:
            time.sleep(5)
            continue
        m = re.match(r'\s*#REDIRECT\s*\[\[([^\]|#]+)', txt, re.I)
        if m:
            title = m.group(1).strip()
            continue
        return txt, title
    return None, title


def parse_coord(txt):
    m = re.search(r'\{\{\s*coord\s*\|([^{}]*)\}\}', txt, re.I)
    if not m:
        return None
    parts = [p.strip() for p in m.group(1).split('|') if p.strip() and '=' not in p]
    nums, hemis = [], []
    for p in parts:
        if re.fullmatch(r'-?\d+(\.\d+)?', p):
            nums.append(float(p))
        elif p.upper() in ('N', 'S', 'E', 'W'):
            hemis.append((len(nums), p.upper()))
        else:
            break
    if not hemis:
        return (nums[0], nums[1]) if len(nums) >= 2 else None
    # format DMS : lat ... N/S lon ... E/W
    i1, h1 = hemis[0]
    lat_parts = nums[:i1]
    lon_parts = nums[i1:hemis[1][0]] if len(hemis) > 1 else nums[i1:]
    h2 = hemis[1][1] if len(hemis) > 1 else 'E'

    def dms(v):
        return sum(x / (60 ** k) for k, x in enumerate(v)) if v else None
    lat, lon = dms(lat_parts), dms(lon_parts)
    if lat is None or lon is None:
        return None
    return (-lat if h1 == 'S' else lat, -lon if h2 == 'W' else lon)


def num(s):
    s = re.sub(r'<ref[^>]*/>|<ref[^>]*>.*?</ref>|\{\{[^{}]*\}\}', '', s, flags=re.S)
    s = s.replace('−', '-').replace('–', '-').replace(',', '.').strip()
    m = re.match(r'-?\d+(\.\d+)?', s)
    return float(m.group(0)) if m else None


def weather_boxes(txt):
    """Liste des blocs {{Weather box ...}} (gère l'imbrication des accolades)."""
    out, i = [], 0
    while True:
        m = re.search(r'\{\{\s*Weather[ _]box\b', txt[i:], re.I)
        if not m:
            return out
        start = i + m.start()
        depth, j = 0, start
        while j < len(txt) - 1:
            if txt[j:j + 2] == '{{':
                depth += 1
                j += 2
                continue
            if txt[j:j + 2] == '}}':
                depth -= 1
                j += 2
                if depth == 0:
                    break
                continue
            j += 1
        out.append(txt[start:j])
        i = j


def params(box):
    d = {}
    for m in re.finditer(r'\|\s*([^=|{}\n]+?)\s*=\s*([^|\n]*)', box):
        d[m.group(1).strip().lower()] = m.group(2).strip()
    return d


def unit_is_1mm(u):
    u = (u or '').lower().replace('&nbsp;', ' ').replace('≥', '')
    return bool(re.fullmatch(r'\s*1(\.0+)?\s*mm\s*', u))


def extract(box):
    p = params(box)
    res = {'location': re.sub(r'\[\[|\]\]|<[^>]+>', '', p.get('location', ''))[:120]}
    for key in ('precipitation days', 'rain days'):
        if unit_is_1mm(p.get(f'unit {key}')):
            vals = [num(p.get(f'{mo.lower()} {key}', '')) for mo in MONTHS]
            if all(v is not None for v in vals):
                res['rain_days'] = vals
                res['rain_days_key'] = key
                res['rain_days_unit'] = p.get(f'unit {key}')
                break
    highs = [num(p.get(f'{mo.lower()} high c', '')) for mo in MONTHS]
    if all(v is not None for v in highs):
        res['high_c'] = highs
    return res


def candidates(d):
    slug, en = d['slug_fr'], (d.get('nom_en') or d['nom_fr']).strip()
    c = list(STATION_HINTS.get(slug, []))
    country = (d.get('country_en') or '').strip()
    c += [en, f'{en}, {country}' if country else None, f'Climate of {en}']
    seen, out = set(), []
    for t in c:
        if t and t not in seen:
            seen.add(t)
            out.append(t)
    return out


def find(d):
    lat0, lon0 = float(d['lat']), float(d['lon'])
    tried = []
    for title in candidates(d):
        txt, final = raw(title)
        tried.append(final)
        if not txt:
            continue
        coord = parse_coord(txt)
        texts = [(txt, final)]
        for tm in re.finditer(r'\{\{\s*([^{}|]*?weatherbox[^{}|]*?)\s*\}\}', txt, re.I):
            ttxt, tfinal = raw('Template:' + tm.group(1).strip())
            if ttxt:
                texts.append((ttxt, tfinal))
        if coord is not None:
            dist = haversine(lat0, lon0, *coord)
            if dist > MAX_KM:
                continue
            validation = 'coord'
        else:
            # Coordonnées tirées de Wikidata (absentes du texte) : on exige que
            # le pays de la destination figure dans l'introduction de la page.
            country = (d.get('country_en') or '').strip()
            if not country or country.lower() not in txt[:6000].lower():
                continue
            dist, validation = None, 'nom+pays'
        found = None
        for t, src in texts:
            for box in weather_boxes(t):
                r = extract(box)
                if 'rain_days' in r:
                    found = (r, src)
                    break
                if 'high_c' in r and found is None:
                    found = (r, src)
            if found and 'rain_days' in found[0]:
                break
        if found:
            r, src = found
            r.update({'page': final, 'box_source': src, 'page_coord': coord,
                      'dist_km': round(dist) if dist is not None else None, 'validation': validation})
            return r, tried
    return None, tried


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--only', default='')
    ap.add_argument('--refresh', action='store_true')
    a = ap.parse_args()
    dests = list(csv.DictReader(open(os.path.join(ROOT, 'data', 'destinations.csv'), encoding='utf-8-sig')))
    out = json.load(open(OUT, encoding='utf-8')) if os.path.exists(OUT) else {}
    only = {s for s in a.only.split(',') if s}
    n = 0
    for d in dests:
        s = d['slug_fr']
        if only and s not in only:
            continue
        if s in out and not a.refresh:
            continue
        r, tried = find(d)
        out[s] = r if r else {'not_found': tried}
        n += 1
        with open(OUT, 'w', encoding='utf-8') as f:
            json.dump(out, f, ensure_ascii=False, indent=0)
        flag = ('pluie ✓' if r and 'rain_days' in r else 'pluie ✗') + (' T ✓' if r and 'high_c' in r else '')
        print(f'{n:4d} {s:24s} {flag} {(r or {}).get("page", "")} {(r or {}).get("dist_km", "")}', flush=True)
    ok = sum(1 for v in out.values() if 'rain_days' in v)
    print(f'Jours de pluie >= 1 mm trouvés : {ok}/{len(out)}')


if __name__ == '__main__':
    main()
