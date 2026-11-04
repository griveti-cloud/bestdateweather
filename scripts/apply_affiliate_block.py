#!/usr/bin/env python3
"""
Remplace la section « Planifier votre séjour » (<section id="planifier">) des
fiches annuelles et mensuelles déjà générées par la version actuelle de
lib/v6.render_v6_reserver (liens de lib/affiliates.py), sans régénérer le
reste de la page.

Pourquoi un remplacement ciblé : les liens de monétisation sont la seule
chose qui change ; régénérer 47 000 pages réécrirait aussi tout leur contenu
(risque inutile, cf. garde-fou de gel du plan B).

Usage :
    python3 scripts/apply_affiliate_block.py            # applique
    python3 scripts/apply_affiliate_block.py --dry-run  # compte seulement
"""
import csv
import html as H
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from lib.v6 import render_v6_reserver  # noqa: E402

LANGS = ['fr', 'en', 'en-us', 'es', 'de']
START = '  <section id="planifier"'
END = '\n  </section>'


def main(dry=False):
    rows = list(csv.DictReader(open(ROOT / 'data' / 'destinations.csv', encoding='utf-8-sig')))
    stats = {'modifiées': 0, 'inchangées': 0, 'ignorées': 0, 'noms différents': 0}
    odd = []
    for lang in LANGS:
        loc = json.load(open(ROOT / 'locales' / f'{lang}.json', encoding='utf-8'))
        fields, url = loc['dest_fields'], loc['url']
        by_slug = {r[fields['slug_key']]: r for r in rows if r.get(fields['slug_key'])}
        sub = loc['meta']['subdir']
        folder = ROOT / sub if sub else ROOT
        a_pre, m_sep, months = url['annual_prefix'], url['monthly_sep'], loc['month_url']
        for f in sorted(folder.glob('*.html')):
            name = f.name
            if name.startswith(a_pre):
                slug, kind = name[len(a_pre):-5], 'annual'
            else:
                m = next((mo for mo in months if name.endswith(f'{m_sep}{mo}.html')), None)
                if not m:
                    continue
                slug, kind = name[:-(len(m_sep) + len(m) + 5)], 'monthly'
            row = by_slug.get(slug)
            if not row:
                continue
            txt = f.read_text(encoding='utf-8')
            i = txt.find(START)
            if i < 0:
                continue
            j = txt.find(END, i)
            if j < 0 or 'plan-card' not in txt[i:j]:
                stats['ignorées'] += 1
                odd.append(str(f.relative_to(ROOT)))
                continue
            j += len(END)
            dname = row.get(fields['name_key']) or row.get('nom_bare') or row['slug_fr']
            mq = re.search(r'data-gyg-q="([^"]*)"', txt[i:j])
            if mq and H.unescape(H.unescape(mq.group(1))) != dname:
                stats['noms différents'] += 1
                if stats['noms différents'] <= 5:
                    print(f'  ⚠️ nom différent {f.relative_to(ROOT)} : page « {H.unescape(H.unescape(mq.group(1)))} » / données « {dname} »')
            new = render_v6_reserver(slug, lang, dname, slug_fr=row['slug_fr'], kind=kind)
            out = txt[:i] + new.rstrip('\n') + txt[j:]
            if out == txt:
                stats['inchangées'] += 1
                continue
            stats['modifiées'] += 1
            if not dry:
                f.write_text(out, encoding='utf-8')
    print(('[essai] ' if dry else '') + ' ; '.join(f'{k} : {v}' for k, v in stats.items()))
    if odd:
        print('  sections non reconnues :', odd[:10])


if __name__ == '__main__':
    main(dry='--dry-run' in sys.argv)
