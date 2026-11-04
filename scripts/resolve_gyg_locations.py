#!/usr/bin/env python3
"""
Associe chaque destination à un lieu GetYourGuide (identifiant « l207 » = Grenade)
pour que le widget et le bouton « Voir tout » montrent le bon endroit.

Pourquoi : avec une simple recherche par nom (data-gyg-q), GetYourGuide choisit
lui-même le lieu, parfois le mauvais (Santiago → Cap-Vert, Saint-Georges de la
Grenade → Guadeloupe, N'Djamena → République dominicaine).

Méthode : on interroge le widget public (le même que celui des pages) avec
3 requêtes (« nom anglais, pays », « nom anglais », « nom français ») et
12 activités par requête. Chaque activité porte son lieu dans son adresse
(getyourguide.com/lisbon-l42/...). On retient le lieu le plus fréquent dont le
nom correspond à celui de la destination (Lisbonne : lisbon-l42, 10 activités
sur 12), sauf s'il porte le nom d'un autre pays ou d'un État américain
(la-paz-mexico pour La Paz en Bolivie, trinidad-colorado pour Trinidad à Cuba).
Niveau 2, sans lieu correspondant : on garde la recherche texte si le nom complet
de la destination figure dans les titres des activités proposées (Val Thorens :
« transfert privé de Genève à Val Thorens »). Sinon None : le bloc d'activités
n'est pas affiché (mieux vaut rien qu'un mauvais endroit).
Corrections manuelles : data/gyg_locations_manual.json (prioritaires).

Sortie : data/gyg_locations.json
  {slug: {"id": 207, "name": "granada", "q": "...", "rank": 1}      lieu précis
         {"id": null, "q": "Val Thorens", "rank": 2}                  recherche texte
         null}                                                        pas de bloc
Usage : python3 scripts/resolve_gyg_locations.py [--only slug1,slug2] [--force]
"""
import concurrent.futures as cf
import difflib
import json
import re
import ssl
import sys
import time
import unicodedata
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
OUT = ROOT / 'data' / 'gyg_locations.json'
PARTNER = '2MQKL00'
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0 Safari/537.36'
FRAME = ('https://widget.getyourguide.com/default/activities.frame?locale_code=en-US&widget=activities'
         f'&number_of_items=12&partner_id={PARTNER}&q=')
US_STATES = {'alabama', 'alaska', 'arizona', 'arkansas', 'california', 'colorado', 'connecticut', 'delaware', 'florida', 'georgia',
             'hawaii', 'idaho', 'illinois', 'indiana', 'iowa', 'kansas', 'kentucky', 'louisiana', 'maine', 'maryland', 'massachusetts',
             'michigan', 'minnesota', 'mississippi', 'missouri', 'montana', 'nebraska', 'nevada', 'hampshire', 'jersey', 'mexico',
             'york', 'carolina', 'dakota', 'ohio', 'oklahoma', 'oregon', 'pennsylvania', 'rhode', 'tennessee', 'texas', 'utah',
             'vermont', 'virginia', 'washington', 'wisconsin', 'wyoming'}
STOP = {'saint', 'st', 'ste', 'san', 'santa', 'sao', 'de', 'del', 'della', 'la', 'le', 'les', 'el', 'the', 'of', 'and', 'et', 'y',
        'island', 'islands', 'isla', 'islas', 'ile', 'iles', 'isle', 'insel', 'inseln', 'city', 'ville', 'stadt', 'national', 'park',
        'parc', 'region', 'coast', 'cote', 'bay', 'baie', 'mount', 'mont', 'lake', 'lac', 'valley', 'vallee', 'beach', 'plage',
        'old', 'town', 'north', 'south', 'east', 'west', 'nord', 'sud', 'great', 'grand', 'new', 'do', 'da', 'das', 'dos', 'di',
        'du', 'des', 'd', 'l', 'al', 'sur', 'mar', 'resort', 'area'}


def norm_tokens(s):
    s = unicodedata.normalize('NFD', str(s or '')).encode('ascii', 'ignore').decode().lower()
    return {t for t in re.split(r'[^a-z0-9]+', s) if len(t) >= 3 and t not in STOP}


def matches(loc_name, names):
    lt = norm_tokens(loc_name)
    if not lt:
        return False
    for n in names:
        nt = norm_tokens(n)
        for a in lt:
            for b in nt:
                if a == b or (len(a) >= 5 and len(b) >= 5 and difflib.SequenceMatcher(None, a, b).ratio() >= 0.8):
                    return True
    return False


_CTX = ssl.create_default_context()


def phrase(s):
    s = unicodedata.normalize('NFD', str(s or '')).encode('ascii', 'ignore').decode().lower()
    return ' ' + ' '.join(t for t in re.split(r'[^a-z0-9]+', s) if t) + ' '


def resolve_q(q):
    """Lieu GetYourGuide choisi par le widget pour la requête q : (id, nom du lieu, nb d'activités, titres)."""
    req = urllib.request.Request(FRAME + urllib.parse.quote(q), headers={'User-Agent': UA})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=30, context=_CTX) as r:
                html = r.read().decode('utf-8', 'ignore')
            break
        except Exception:
            time.sleep(2 + 3 * attempt)
    else:
        return None
    import html as _h
    n = html.count('data-gyg-event-tour-id=')
    locs = re.findall(r'getyourguide\.com/(?:[a-z]{2}-[a-z]{2}/)?([a-z0-9-]+)-l(\d+)/[a-z0-9-]+-t\d+', html)
    titles = [_h.unescape(re.sub(r'<[^>]+>', '', t)).strip() for t in re.findall(r'data-test-id="activity-title"[^>]*>(.*?)</', html, re.S)]
    m = re.search(r'getyourguide\.com/(?:[a-z]{2}-[a-z]{2}/)?([a-z0-9-]+)-l(\d+)/\?partner_id', html)
    return ([(nm, int(i)) for nm, i in locs], (m.group(1), int(m.group(2))) if m else None, n, titles)


def candidates(d):
    en, ce, fr = (d.get('nom_en') or '').strip(), (d.get('country_en') or '').strip(), (d.get('nom_bare') or '').strip()
    out = []
    for q in (f'{en}, {ce}' if en and ce and en != ce else '', en, fr):
        if q and q not in out:
            out.append(q)
    return out


def resolve(slug, d, all_country_tokens):
    names = {d.get(k) for k in ('nom_bare', 'nom_fr', 'nom_en', 'nom_es', 'nom_de', 'slug_en', 'slug_es', 'slug_de')} | {slug}
    names = {n for n in names if n} | {n.split('/')[0] for n in names if n and '/' in n}
    name_tok = set().union(*[norm_tokens(n) for n in names])
    ours = set().union(*[norm_tokens(d.get(k, '')) for k in ('pays', 'country_en', 'country_es', 'country_de')])
    foreign = (all_country_tokens | (US_STATES if 'states' not in ours else set())) - ours - name_tok

    def ok_loc(lname):
        toks = norm_tokens(lname.replace('-', ' '))
        return matches(lname.replace('-', ' '), names) and not (toks - name_tok) & foreign

    votes, tried, by_title = {}, [], None
    for rank, q in enumerate(candidates(d), 1):
        r = resolve_q(q)
        if r is None:
            return slug, 'ERREUR', tried
        locs, see_all, n, titles = r
        tried.append((q, locs[:12], see_all, n, titles[:4]))
        for lname, lid in locs + ([see_all] if see_all else []):
            if ok_loc(lname):
                v = votes.setdefault(lid, {'id': lid, 'name': lname, 'q': q, 'rank': rank, 'votes': 0})
                v['votes'] += 1
        if by_title is None and n:
            tt = phrase(' | '.join(titles))
            if any(len(phrase(nm).strip()) >= 6 and phrase(nm) in tt for nm in names):
                by_title = {'id': None, 'q': q, 'rank': rank + 10}
        if votes and max(v['votes'] for v in votes.values()) >= 3:
            break                     # lieu net dès la 1re requête : inutile d'aller plus loin
    if votes:
        best = max(votes.values(), key=lambda v: (v['votes'], -v['rank']))
        return slug, best, tried
    return slug, by_title, tried


def main():
    from generate_piliers import load_destinations
    dests = load_destinations()
    cur = json.load(open(OUT, encoding='utf-8')) if OUT.exists() else {}
    only = None
    if '--only' in sys.argv:
        only = set(sys.argv[sys.argv.index('--only') + 1].split(','))
    todo = [s for s in sorted(dests) if (only is None or s in only) and ('--force' in sys.argv or only or s not in cur)]
    print(f'{len(todo)} destinations à résoudre')
    log = {}
    act = set()
    for v in dests.values():
        for k in ('pays', 'country_en', 'country_es', 'country_de'):
            act |= norm_tokens(v.get(k, ''))
    with cf.ThreadPoolExecutor(max_workers=4) as ex:
        for slug, res, tried in ex.map(lambda s: resolve(s, dests[s], act), todo):
            if res == 'ERREUR':
                print(f'  ⚠️ {slug} : réseau, réessayer plus tard')
                continue
            cur[slug] = res
            log[slug] = tried
    manual = ROOT / 'data' / 'gyg_locations_manual.json'
    if manual.exists():
        for k, v in json.load(open(manual, encoding='utf-8')).items():
            if not k.startswith('_'):
                cur[k] = v
    json.dump(dict(sorted(cur.items())), open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    json.dump(log, open(ROOT / 'data' / 'gyg_locations_log.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    ok = sum(1 for v in cur.values() if v)
    print(f"  lieu précis : {sum(1 for v in cur.values() if v and v.get('id'))} ; recherche texte : {sum(1 for v in cur.values() if v and not v.get('id'))}")
    by_rank = {}
    for v in cur.values():
        if v:
            by_rank[v['rank']] = by_rank.get(v['rank'], 0) + 1
    print(f'{ok} / {len(cur)} destinations avec un lieu GetYourGuide ; par requête retenue : {by_rank} ; sans lieu : {len(cur) - ok}')


if __name__ == '__main__':
    main()
