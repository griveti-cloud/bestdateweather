#!/usr/bin/env python3
"""
Applique les photos choisies (data/photo_choices.json) : met à jour
data/destination_photos.csv puis remplace la photo et son crédit dans les pages
déjà générées, sans régénérer le reste.

Pourquoi un remplacement ciblé : seule la photo change. Régénérer 80 pages par
destination réécrirait tout leur contenu (garde-fou de gel du plan B).

Ce qui est remplacé :
  - pages de la destination (fiche annuelle et 12 fiches mensuelles, 5 langues) :
    image d'en-tête, préchargement, og:image (paramètre ?w=1400) et crédit ;
  - autres pages (accueil, classements, hubs) : la photo seulement à l'intérieur
    des liens <a> qui pointent vers la destination, pour ne pas toucher une autre
    destination qui partagerait la même photo.

Usage :
    python3 scripts/apply_photo_choice.py --dry-run [--only slug1,slug2]
    python3 scripts/apply_photo_choice.py [--only ...] [--autorise]
--autorise : nécessaire au-delà de 1 500 pages modifiées (garde-fou de gel).
"""
import csv
import datetime
import html as H
import json
import re
import subprocess
import sys
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LANGS = ['fr', 'en', 'en-us', 'es', 'de']
PHOTOS = ROOT / 'data' / 'destination_photos.csv'
CHOICES = ROOT / 'data' / 'photo_choices.json'
FREEZE = 1500


def path_of(url):
    return urllib.parse.urlparse(url).path.lstrip('/')


def credit_html(name, url):
    return f'<a href="{url}" target="_blank" rel="noopener nofollow">{name}</a> via Unsplash'


def files_with(text):
    try:
        out = subprocess.run(['rg', '-l', '-F', text, '--glob', '*.html', str(ROOT)],
                             capture_output=True, text=True, timeout=600).stdout
        return [Path(p) for p in out.split()]
    except FileNotFoundError:
        return [p for p in ROOT.rglob('*.html') if text in p.read_text(encoding='utf-8', errors='ignore')]


def main():
    args = sys.argv[1:]
    dry = '--dry-run' in args
    only = set(args[args.index('--only') + 1].split(',')) if '--only' in args else None
    dests = {r['slug_fr']: r for r in csv.DictReader(open(ROOT / 'data' / 'destinations.csv', encoding='utf-8-sig'))}
    rows = list(csv.DictReader(open(PHOTOS, encoding='utf-8-sig')))
    fields = list(rows[0].keys())
    if 'photo_verifie_le' not in fields:
        fields.append('photo_verifie_le')
    by_slug = {r['slug_fr']: r for r in rows}
    choices = {k: v for k, v in json.load(open(CHOICES, encoding='utf-8')).items() if not k.startswith('_')}
    if only:
        choices = {k: v for k, v in choices.items() if k in only}
    locs = {l: json.load(open(ROOT / 'locales' / f'{l}.json', encoding='utf-8')) for l in LANGS}
    today = datetime.date.today().isoformat()

    new_paths = {}
    for slug, c in choices.items():
        if c['path'] in new_paths.values():
            sys.exit(f'Photo {c["path"]} choisie pour deux destinations : {slug} et une autre')
        new_paths[slug] = c['path']
    used_elsewhere = {path_of(r['photo_url']): r['slug_fr'] for r in rows if r['slug_fr'] not in choices}
    for slug, p in new_paths.items():
        if p in used_elsewhere:
            sys.exit(f'{slug} : la photo choisie sert déjà à {used_elsewhere[p]}')

    edits = {}            # fichier -> texte modifié
    report = []

    def get(f):
        return edits.get(f) if f in edits else f.read_text(encoding='utf-8')

    for slug, c in sorted(choices.items()):
        d, old = dests.get(slug), by_slug.get(slug)
        if not d:
            print(f'  ⚠️ {slug} : destination inconnue')
            continue
        old_path = path_of(old['photo_url']) if old else ''
        old_name = (old or {}).get('photo_credit_name', '').replace(' via Unsplash', '').replace(' via unsplash', '')
        old_credit = credit_html(old_name, (old or {}).get('photo_credit_url', '')) if old else ''
        new_name = H.escape(c['user_name'], quote=False)
        new_credit = credit_html(new_name, c['user_url'])
        owned, hub_files, n_hero, n_cards = set(), set(), 0, 0
        hits = files_with(old_path) if old_path else []
        for l, loc in locs.items():
            sub = loc['meta']['subdir']
            folder = ROOT / sub if sub else ROOT
            sl = d.get(loc['dest_fields']['slug_key']) or slug
            names = [f"{loc['url']['annual_prefix']}{sl}"] + [f"{sl}{loc['url']['monthly_sep']}{m}" for m in loc['month_url']]
            for nm in names:
                f = folder / f'{nm}.html'
                if not f.exists():
                    continue
                owned.add(f)
                t = get(f)
                t2 = t.replace(f'images.unsplash.com/{old_path}?w=1400', f'images.unsplash.com/{c["path"]}?w=1400') if old_path else t
                n_hero += t.count(f'images.unsplash.com/{old_path}?w=1400') if old_path else 0
                if old_credit and old_credit in t2:
                    t2 = t2.replace(old_credit, new_credit)
                if t2 != t:
                    edits[f] = t2
            # cartes ailleurs : liens <a> vers la destination contenant l'ancienne photo
            if old_path:
                alt = '|'.join(re.escape(n) for n in names)
                rx = re.compile(r'<a\b[^>]*href="(?:[^"]*/)?(?:' + alt + r')(?:\.html)?"[^>]*>.*?</a>', re.S)
                for f in hits:
                    if f in owned or (sub and f.parent != folder) or (not sub and f.parent != ROOT):
                        continue
                    t = get(f)
                    def sw(m):
                        return m.group(0).replace(f'images.unsplash.com/{old_path}', f'images.unsplash.com/{c["path"]}')
                    t2, k = rx.subn(lambda m: sw(m) if old_path in m.group(0) else m.group(0), t)
                    if t2 != t:
                        edits[f] = t2
                        hub_files.add(f)
                        n_cards += t.count(old_path) - t2.count(old_path)
        report.append((slug, len([f for f in owned if f in edits]), n_hero, len(hub_files), n_cards))
        row = by_slug.setdefault(slug, {k: '' for k in fields} | {'slug_fr': slug})
        row.update({
            'photo_url': f'https://images.unsplash.com/{c["path"]}?w=1400&q=85&fm=jpg&fit=crop&crop=entropy',
            'photo_credit_name': f'{c["user_name"]} via Unsplash',
            'photo_credit_url': c['user_url'],
            'photo_page_url': c['page_url'],
            'photo_verifie_le': today,
        })

    for slug, n_own, n_hero, n_hub, n_cards in report:
        print(f'{slug:28} pages de la destination : {n_own:3} (images {n_hero:3}) ; autres pages : {n_hub:2} (cartes {n_cards:2})')
    total = len(edits)
    print(f'{"[essai] " if dry else ""}{total} fichiers HTML modifiés pour {len(report)} destinations')
    if total > FREEZE and '--autorise' not in args:
        sys.exit(f'Plus de {FREEZE} pages : réduire le lot (--only) ou relancer avec --autorise après accord.')
    if dry:
        return
    for f, t in edits.items():
        f.write_text(t, encoding='utf-8')
    out = [by_slug[r['slug_fr']] for r in rows] + [v for k, v in by_slug.items() if k not in {r['slug_fr'] for r in rows}]
    with open(PHOTOS, 'w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=fields, lineterminator='\n')
        w.writeheader()
        for r in out:
            w.writerow({k: r.get(k, '') for k in fields})
    print('data/destination_photos.csv mis à jour')


if __name__ == '__main__':
    main()
