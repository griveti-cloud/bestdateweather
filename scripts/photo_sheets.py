#!/usr/bin/env python3
"""
Planches de vignettes pour choisir à l'œil la photo d'une destination.

Pour chaque destination : la photo actuelle (case 0, bordure rouge) puis les
candidats numérotés, avec le photographe et un avertissement si la photo sert
déjà à une autre destination.

Usage :
    python3 scripts/photo_sheets.py <dossier des candidats> <dossier de sortie> [slug1,slug2]
Dépendance : Pillow.
"""
import concurrent.futures as cf
import csv
import io
import json
import sys
import urllib.parse
import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
TW, TH, COLS = 420, 260, 5
UA = 'BestDateWeather-photo-audit/1.0 (https://bestdateweather.com)'


def font(size, bold=True):
    name = 'DejaVuSans-Bold.ttf' if bold else 'DejaVuSans.ttf'
    try:
        return ImageFont.truetype(f'/usr/share/fonts/truetype/dejavu/{name}', size)
    except OSError:
        return ImageFont.load_default()


def thumb(path):
    url = f'https://images.unsplash.com/{path}?w={TW}&h={TH}&fit=crop&q=60&fm=jpg'
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': UA}), timeout=40) as r:
            im = Image.open(io.BytesIO(r.read())).convert('RGB')
        s = max(TW / im.width, TH / im.height)
        im = im.resize((int(im.width * s) + 1, int(im.height * s) + 1))
        x, y = (im.width - TW) // 2, (im.height - TH) // 2
        return im.crop((x, y, x + TW, y + TH))
    except Exception:
        return None


def sheet(slug, cands, current, out):
    items = [('actuelle', current, '', [])] + [
        (str(i + 1), c['path'], c.get('user_name', ''), c.get('deja_utilisee_par', [])) for i, c in enumerate(cands)]
    with cf.ThreadPoolExecutor(8) as ex:
        ims = list(ex.map(lambda it: thumb(it[1]) if it[1] else None, items))
    rows = (len(items) + COLS - 1) // COLS
    W = Image.new('RGB', (COLS * (TW + 6), 44 + rows * (TH + 48)), 'white')
    d = ImageDraw.Draw(W)
    d.text((6, 8), slug, fill='black', font=font(24))
    for k, (it, im) in enumerate(zip(items, ims)):
        x, y = (k % COLS) * (TW + 6), 44 + (k // COLS) * (TH + 48)
        if im:
            W.paste(im, (x, y))
        if k == 0:
            d.rectangle((x, y, x + TW - 1, y + TH - 1), outline='#d00', width=5)
        d.text((x + 4, y + TH + 4), f'{it[0]}. {it[2]}'[:44], fill='black', font=font(15))
        if it[3]:
            d.text((x + 4, y + TH + 24), 'déjà utilisée : ' + ', '.join(it[3])[:30], fill='#d00', font=font(14, False))
    W.save(out / f'{slug}.jpg', quality=82)


def main():
    src, out = Path(sys.argv[1]), Path(sys.argv[2])
    only = set(sys.argv[3].split(',')) if len(sys.argv) > 3 else None
    out.mkdir(parents=True, exist_ok=True)
    current = {}
    for r in csv.DictReader(open(ROOT / 'data' / 'destination_photos.csv', encoding='utf-8-sig')):
        current[r['slug_fr']] = urllib.parse.urlparse(r['photo_url']).path.lstrip('/')
    for f in sorted(src.glob('*.json')):
        slug = f.stem
        if only and slug not in only:
            continue
        cands = json.load(open(f, encoding='utf-8'))
        sheet(slug, cands, current.get(slug, ''), out)
        print(f'{slug} : {len(cands)} candidats')


if __name__ == '__main__':
    main()
