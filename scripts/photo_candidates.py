#!/usr/bin/env python3
"""
Recherche de photos candidates sur Unsplash pour remplacer les photos de
destination fausses ou faibles (audit visuel du 4 novembre 2026).

Pourquoi : en avril, fetch_photos_v2.py choisissait seul la photo d'après les
mots-clés et les « j'aime ». Les métadonnées Unsplash sont trop peu fiables
(« Zagreb » ramenait une photo d'encre colorée). Ici, le script ne choisit
rien : il rapporte 20 candidats par destination, choisis ensuite à l'œil sur
une planche de vignettes (scripts/photo_sheets.py).

La clé n'est jamais dans le dépôt : elle vient de la variable d'environnement
UNSPLASH_KEY (secret GitHub Actions, flux .github/workflows/photo-candidates.yml).

Usage :
    python3 scripts/photo_candidates.py --lot 1
    python3 scripts/photo_candidates.py --only los-angeles,tokyo
    python3 scripts/photo_candidates.py --track <id>,<id>   # signale à Unsplash
        les photos retenues (règle de l'API : déclencher le « téléchargement »)
Sortie : out/photo_candidates/<slug>.json
"""
import csv
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'out' / 'photo_candidates'
API = 'https://api.unsplash.com'
MIN_RESULTS = 10          # en dessous, on essaie la 2e requête


def key():
    k = os.environ.get('UNSPLASH_KEY', '').strip()
    if not k:
        sys.exit('UNSPLASH_KEY absent : ajouter le secret du dépôt (Settings > Secrets and variables > Actions).')
    return k


def call(path, params=None):
    url = API + path + ('?' + urllib.parse.urlencode(params) if params else '')
    req = urllib.request.Request(url, headers={'Authorization': f'Client-ID {key()}', 'Accept-Version': 'v1'})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=40) as r:
                remaining = int(r.headers.get('X-Ratelimit-Remaining', '50'))
                data = json.load(r)
            if remaining <= 1:
                print('  quota horaire épuisé : pause de 61 minutes')
                time.sleep(61 * 60)
            return data
        except urllib.error.HTTPError as e:
            if e.code == 403 and 'Rate Limit' in e.read().decode('utf-8', 'ignore'):
                print('  limite atteinte : pause de 61 minutes')
                time.sleep(61 * 60)
                continue
            if e.code == 401:
                sys.exit('Clé refusée (401) : vérifier le secret UNSPLASH_KEY.')
            time.sleep(5 * (attempt + 1))
        except Exception:
            time.sleep(5 * (attempt + 1))
    return None


def used_photos():
    used = {}
    for r in csv.DictReader(open(ROOT / 'data' / 'destination_photos.csv', encoding='utf-8-sig')):
        path = urllib.parse.urlparse(r['photo_url']).path.lstrip('/')
        used.setdefault(path, []).append(r['slug_fr'])
    return used


def slim(p, used, query):
    path = urllib.parse.urlparse(p['urls']['raw']).path.lstrip('/')
    return {
        'id': p['id'], 'path': path, 'query': query,
        'w': p.get('width'), 'h': p.get('height'), 'likes': p.get('likes'),
        'alt': p.get('alt_description') or '', 'desc': p.get('description') or '',
        'user_name': (p.get('user') or {}).get('name', ''),
        'user_url': ((p.get('user') or {}).get('links') or {}).get('html', ''),
        'page_url': (p.get('links') or {}).get('html', ''),
        'download_location': (p.get('links') or {}).get('download_location', ''),
        'thumb': p['urls'].get('small', ''),
        'deja_utilisee_par': used.get(path, []),
    }


def search(slug, queries, used):
    found, seen = [], set()
    for q in queries:
        data = call('/search/photos', {'query': q, 'per_page': 20, 'orientation': 'landscape', 'content_filter': 'high'})
        if data is None:
            print(f'  ⚠️ {slug} : échec réseau sur « {q} »')
            continue
        for p in data.get('results', []):
            if p['id'] not in seen:
                seen.add(p['id'])
                found.append(slim(p, used, q))
        if len(found) >= MIN_RESULTS:
            break
    return found


def track(ids):
    """Règle de l'API Unsplash : signaler chaque photo réellement utilisée."""
    index = {}
    for f in OUT.glob('*.json'):
        for c in json.load(open(f, encoding='utf-8')):
            index[c['id']] = c
    for i in ids:
        c = index.get(i)
        if not c or not c.get('download_location'):
            print(f'  ⚠️ {i} : candidat inconnu, non signalé')
            continue
        dl = urllib.parse.urlparse(c['download_location'])
        call(dl.path, dict(urllib.parse.parse_qsl(dl.query)))
        print(f'  signalé : {i}')


def main():
    args = sys.argv[1:]
    cfg = json.load(open(ROOT / 'data' / 'photo_queries.json', encoding='utf-8'))
    if '--track' in args:
        track([x for x in args[args.index('--track') + 1].split(',') if x])
        return
    if '--lot' in args:
        slugs = cfg['lots'][args[args.index('--lot') + 1]]
    elif '--only' in args:
        slugs = [s for s in args[args.index('--only') + 1].split(',') if s]
    else:
        sys.exit('Préciser --lot N ou --only slug1,slug2')
    OUT.mkdir(parents=True, exist_ok=True)
    used = used_photos()
    for slug in slugs:
        queries = cfg['queries'].get(slug)
        if not queries:
            print(f'  ⚠️ {slug} : pas de requête dans data/photo_queries.json')
            continue
        res = search(slug, queries, used)
        json.dump(res, open(OUT / f'{slug}.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print(f'{slug} : {len(res)} candidats')


if __name__ == '__main__':
    main()
