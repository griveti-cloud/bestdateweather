#!/usr/bin/env python3
"""
BESTDATEWEATHER — Régénération des scores des fiches destination
================================================================
Usage :
  python3 regenerate_scores.py             # toutes les fiches FR + EN
  python3 regenerate_scores.py paris       # une seule destination
  python3 regenerate_scores.py --dry-run   # vérifier sans écrire
  python3 regenerate_scores.py --check     # audit RMSE sans modifier

Ce script :
  1. Lit le tableau climatique de chaque fiche
  2. Ajoute/met à jour les attributs data-tmax, data-rain, data-sun sur chaque <tr>
     (traçabilité : données sources visibles dans le DOM)
  3. Recalcule les scores via scoring.py (SOURCE DE VÉRITÉ)
  4. Met à jour les cellules <td>X/10</td> dans le tableau
  5. Ajoute un commentaire <!-- SCORING : ... --> dans la page pour l'audit

LIEN ALGORITHME ↔ DONNÉES
  Chaque <tr class="rec|mid|avoid" data-tmax="26" data-rain="29" data-sun="11.2">
  permet à n'importe qui de vérifier ou reproduire le score avec scoring.py.
"""

import re
import sys
import glob
import os
from scoring import compute_scores, TROPICAL_DESTINATIONS

# ── PARSING ────────────────────────────────────────────────────────────────

ROW_PATTERN = re.compile(
    r'(<tr[^>]+class=")(rec|mid|avoid)("[^>]*>)'  # groupe 1: avant classe, 2: classe, 3: après
    r'(<td>)([^<]+)(</td>)'                         # 4-6 : mois
    r'(<td>)(-?\d+)(°C</td>)'                       # 7-9 : tmin
    r'(<td>)(-?\d+)(°C</td>)'                       # 10-12: tmax
    r'(<td>)(\d+)(%</td>)'                          # 13-15: rain_pct
    r'(<td>)([\d.]+[^<]*)(</td>)'                   # 16-18: precip
    r'(<td>)([\d.]+)(h?</td>)'                      # 19-21: sun_h
    r'(<td>)([\d.]+/10)(</td></tr>)',                # 22-24: score
    re.DOTALL
)


def parse_climate_table(html: str):
    """
    Extrait la table climatique principale (celle avec le plus de lignes rec/mid/avoid).
    Retourne (table_html, match_object) ou (None, None).
    """
    tables = list(re.finditer(
        r'<table[^>]*climate-table[^>]*>.*?</table>', html, re.DOTALL
    ))
    if not tables:
        return None, None
    best = max(tables,
               key=lambda m: len(re.findall(r'<tr[^>]+class="(?:rec|mid|avoid)"', m.group(0))))
    return best.group(0), best


def extract_months(table_html: str) -> list:
    """
    Parse toutes les lignes de données de la table.
    Retourne une liste de dicts avec toutes les colonnes.
    """
    months = []
    for m in ROW_PATTERN.finditer(table_html):
        months.append({
            'cls'      : m.group(2),
            'month'    : m.group(5),
            'tmin'     : int(m.group(8)),
            'tmax'     : int(m.group(11)),
            'rain_pct' : int(m.group(14)),
            'precip'   : m.group(17),       # gardé tel quel (mm + unité)
            'sun_h'    : float(m.group(20)),
            'score_cur': m.group(23),        # ex: "3.9/10"
        })
    return months


# ── RECONSTRUCTION ─────────────────────────────────────────────────────────

def build_updated_table(table_html: str, months: list, new_scores: list) -> str:
    """
    Reconstruit la table avec :
    - data-tmax, data-rain, data-sun ajoutés sur chaque <tr>
    - scores /10 mis à jour
    """
    result = table_html
    for i, m in enumerate(months):
        score_10 = new_scores[i]['score_10']
        old_row_pattern = re.compile(
            r'<tr[^>]+class="' + re.escape(m['cls']) + r'"[^>]*>'
            r'<td>' + re.escape(m['month']) + r'</td>'
            r'.*?</tr>',
            re.DOTALL
        )
        # Reconstruire la ligne avec data-attrs et nouveau score
        new_row = (
            f'<tr class="{m["cls"]}" '
            f'data-tmax="{m["tmax"]}" '
            f'data-rain="{m["rain_pct"]}" '
            f'data-sun="{m["sun_h"]}">'
            f'<td>{m["month"]}</td>'
            f'<td>{m["tmin"]}°C</td>'
            f'<td>{m["tmax"]}°C</td>'
            f'<td>{m["rain_pct"]}%</td>'
            f'<td>{m["precip"]}</td>'
            f'<td>{m["sun_h"]}h</td>'
            f'<td>{score_10}/10</td>'
            f'</tr>'
        )
        match = old_row_pattern.search(result)
        if match:
            result = result[:match.start()] + new_row + result[match.end():]

    return result


def add_scoring_comment(html: str, slug: str, version: str = '1.0') -> str:
    """
    Ajoute/met à jour le commentaire d'audit scoring dans le <head>.
    Format : <!-- SCORING: scoring.py v1.0 | slug=paris | tropical=false -->
    Permet de savoir quelle version de l'algo a généré les scores.
    """
    is_tropical = slug in TROPICAL_DESTINATIONS
    comment = (
        f'<!-- SCORING: scoring.py v{version} | '
        f'slug={slug} | '
        f'tropical={"true" if is_tropical else "false"} -->'
    )
    # Remplacer un commentaire existant ou insérer après <head>
    existing = re.search(r'<!-- SCORING:.*?-->', html)
    if existing:
        return html[:existing.start()] + comment + html[existing.end():]
    return re.sub(r'(<head[^>]*>)', r'\1\n' + comment, html, count=1)


# ── TRAITEMENT D'UN FICHIER ─────────────────────────────────────────────────

def process_file(path: str, dry_run: bool = False, check_only: bool = False) -> dict:
    """
    Traite un fichier HTML.
    Retourne {'slug': str, 'status': 'ok'|'error'|'unchanged', 'rmse': float}
    """
    slug = re.search(r'(?:meilleure-periode-|best-time-to-visit-)(.+)\.html',
                     os.path.basename(path))
    slug = slug.group(1) if slug else 'unknown'

    try:
        content = open(path, encoding='utf-8').read()
    except Exception as e:
        return {'slug': slug, 'status': 'error', 'msg': str(e)}

    table_html, table_match = parse_climate_table(content)
    if not table_html:
        return {'slug': slug, 'status': 'error', 'msg': 'table introuvable'}

    months = extract_months(table_html)
    if len(months) < 12:
        return {'slug': slug, 'status': 'error', 'msg': f'seulement {len(months)} lignes parsées'}

    # Calculer les nouveaux scores
    new_scores = compute_scores(months, slug)

    # Calculer le RMSE vs scores actuels
    import math
    diffs = []
    for i, m in enumerate(months):
        try:
            cur_100 = round(float(m['score_cur'].replace('/10', '')) * 10)
            diffs.append(new_scores[i]['score_100'] - cur_100)
        except ValueError:
            diffs.append(0)
    rmse = math.sqrt(sum(d * d for d in diffs) / len(diffs)) if diffs else 0

    if check_only:
        return {'slug': slug, 'status': 'checked', 'rmse': rmse, 'diffs': diffs}

    if dry_run:
        return {'slug': slug, 'status': 'dry-run', 'rmse': rmse}

    # Reconstruire la table
    new_table = build_updated_table(table_html, months, new_scores)

    # Remplacer dans le contenu
    new_content = content.replace(table_html, new_table)
    new_content = add_scoring_comment(new_content, slug)

    if new_content == content:
        return {'slug': slug, 'status': 'unchanged', 'rmse': rmse}

    open(path, 'w', encoding='utf-8').write(new_content)
    return {'slug': slug, 'status': 'ok', 'rmse': rmse}


# ── POINT D'ENTRÉE ──────────────────────────────────────────────────────────

if __name__ == '__main__':
    dry_run = '--dry-run' in sys.argv
    check_only = '--check' in sys.argv

    # Déterminer les fichiers à traiter
    slugs = [a for a in sys.argv[1:] if not a.startswith('--')]

    if slugs:
        files = []
        for s in slugs:
            files += glob.glob(f'meilleure-periode-{s}.html')
            files += glob.glob(f'en/best-time-to-visit-{s}.html')
        files = sorted(set(files))
    else:
        files = (sorted(glob.glob('meilleure-periode-*.html'))
               + sorted(glob.glob('en/best-time-to-visit-*.html')))

    if not files:
        print('Aucun fichier trouvé.')
        sys.exit(1)

    print(f'{"DRY-RUN " if dry_run else "CHECK " if check_only else ""}Traitement de {len(files)} fichiers...\n')

    stats = {'ok': 0, 'unchanged': 0, 'error': 0}
    errors = []

    for f in files:
        result = process_file(f, dry_run=dry_run, check_only=check_only)
        slug = result['slug']
        rmse = result.get('rmse', 0)
        status = result['status']

        if status == 'error':
            print(f'  [ERR] {slug:35} {result.get("msg", "")}')
            errors.append(result)
            stats['error'] += 1
        elif status in ('ok', 'dry-run'):
            mark = '✓' if rmse < 0.5 else '△'
            print(f'  [{mark}  ] {slug:35} RMSE={rmse:.2f}')
            stats['ok'] += 1
        elif status == 'unchanged':
            print(f'  [—  ] {slug:35} inchangé')
            stats['unchanged'] += 1
        elif status == 'checked':
            mark = 'OK ' if rmse < 0.5 else 'ERR'
            diffs_nonzero = [d for d in result.get('diffs', []) if d != 0]
            diff_str = f'  diffs non-nuls: {diffs_nonzero}' if diffs_nonzero else ''
            print(f'  [{mark}] {slug:35} RMSE={rmse:.2f}{diff_str}')
            if rmse >= 0.5:
                stats['error'] += 1
            else:
                stats['ok'] += 1

    print(f'\nRésultat : {stats["ok"]} OK  |  {stats["unchanged"]} inchangés  |  {stats["error"]} erreurs')
    if errors:
        print('\nErreurs détail :')
        for e in errors:
            print(f'  {e["slug"]}: {e.get("msg", "")}')
