#!/usr/bin/env python3
"""
Signale à IndexNow (Bing, Yandex, Seznam, Naver…) les URL indexables modifiées.

Bing ne dépend pas du classement Google : c'est un canal de visibilité
indépendant (et Bing alimente une partie d'autres moteurs). La clé est le
fichier {cle}.txt à la racine du site (protocole IndexNow).

Usage (dans deploy.yml, après le déploiement) :
    python3 scripts/indexnow_submit.py --changed   # URL indexables modifiées par le dernier commit
    python3 scripts/indexnow_submit.py --all       # toutes les URL indexables
"""
import glob
import json
import os
import subprocess
import sys
import urllib.request

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
sys.path.insert(0, ROOT)
from lib.indexation import indexable_paths, served_path  # noqa: E402

HOST = 'bestdateweather.com'


def key():
    for f in glob.glob(os.path.join(ROOT, '*.txt')):
        n = os.path.basename(f)[:-4]
        if len(n) == 32 and all(c in '0123456789abcdef' for c in n):
            if open(f).read().strip() == n:
                return n
    raise SystemExit('Clé IndexNow introuvable (fichier <cle>.txt à la racine)')


def changed_paths():
    out = subprocess.run(['git', 'diff', '--name-only', 'HEAD~1', 'HEAD'], cwd=ROOT,
                         capture_output=True, text=True).stdout.split()
    return {served_path(f) for f in out if f.endswith('.html')}


def main():
    idx = indexable_paths()
    if '--all' in sys.argv:
        paths = sorted(idx)
    else:
        paths = sorted(idx & changed_paths())
    if not paths:
        print('IndexNow : aucune URL indexable modifiée.')
        return
    k = key()
    urls = [f'https://{HOST}/{p}' if p else f'https://{HOST}/' for p in paths]
    body = json.dumps({'host': HOST, 'key': k, 'keyLocation': f'https://{HOST}/{k}.txt',
                       'urlList': urls[:10000]}).encode()
    req = urllib.request.Request('https://api.indexnow.org/indexnow', data=body,
                                 headers={'Content-Type': 'application/json; charset=utf-8'})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            print(f'IndexNow : {len(urls)} URL envoyées, HTTP {r.status}')
    except urllib.error.HTTPError as e:
        # 202 = accepté (clé en cours de vérification) ; 4xx = à corriger, non bloquant
        print(f'IndexNow : HTTP {e.code} {e.read()[:200]!r} (non bloquant)')
    except Exception as e:
        print(f'IndexNow : échec réseau {e} (non bloquant)')


if __name__ == '__main__':
    main()
