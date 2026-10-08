#!/usr/bin/env python3
"""
Applique la politique d'indexation (lib/indexation.py) à toutes les pages HTML.

À lancer après tous les générateurs et avant generate_sitemaps.py :

    python3 apply_indexation.py          # applique
    python3 apply_indexation.py --check  # vérifie seulement (code 1 si écart)

Pour chaque page :
- indexable  : aucune balise robots « noindex » ; liens hreflang conservés
               uniquement vers des pages elles-mêmes indexables ;
- sinon      : <meta name="robots" content="noindex,follow"/> (une
               balise « noindex,nofollow » déjà présente est conservée) et
               suppression des liens hreflang (une page hors index ne doit
               pas déclarer d'alternatives, sinon erreurs « pas de lien de
               retour » dans la Search Console).
"""

import os
import re
import sys

from lib.indexation import indexable_paths, served_path

ROOT = os.path.dirname(os.path.abspath(__file__))
SKIP_DIRS = {'.git', 'node_modules', 'templates', 'vendor', 'data', 'widget',
             '.wrangler', 'scripts', 'tests', 'docs', '.github', 'netlify', 'functions'}
BASE_RE = re.compile(r'^https?://(?:www\.)?bestdateweather\.com/?')
ROBOTS_RE = re.compile(r'<meta\s+name=["\']robots["\'][^>]*>\s*', re.I)
HREFLANG_RE = re.compile(r'[ \t]*<link\b[^>]*\bhreflang=["\']([^"\']+)["\'][^>]*>[ \t]*\n?', re.I)
HREF_RE = re.compile(r'\bhref=["\']([^"\']+)["\']', re.I)
NOINDEX_TAG = '<meta name="robots" content="noindex,follow"/>'


def href_to_path(href: str) -> str:
    p = BASE_RE.sub('', href).split('#')[0].split('?')[0]
    if p.endswith('.html'):
        p = p[:-5]
    if p == 'index':
        p = ''
    return p.rstrip('/')


def process(html: str, path: str, indexable: set) -> str:
    end = html.find('</head>')
    if end < 0:
        return html
    head, rest = html[:end], html[end:]
    idx = path in indexable

    # ── Balise robots ──
    tags = ROBOTS_RE.findall(head)
    if idx:
        for t in tags:
            if 'noindex' in t.lower():
                head = head.replace(t, '', 1)
    else:
        has_noindex = any('noindex' in t.lower() for t in tags)
        if not has_noindex:
            for t in tags:
                head = head.replace(t, '', 1)
            m = re.search(r'<meta\s+charset=[^>]*>\s*\n?', head, re.I) or re.search(r'<head[^>]*>\s*\n?', head, re.I)
            pos = m.end() if m else 0
            head = head[:pos] + NOINDEX_TAG + '\n' + head[pos:]

    # ── Liens hreflang ──
    links = list(HREFLANG_RE.finditer(head))
    if links:
        keep, seen_lang = [], set()
        for m in links:
            hm = HREF_RE.search(m.group(0))
            target = href_to_path(hm.group(1)) if hm else None
            lang_code = m.group(1).lower()
            if idx and target is not None and target in indexable and lang_code not in seen_lang:
                seen_lang.add(lang_code)      # un seul lien par code (doublons x-default)
                keep.append((m, target))
        # Si seule la page elle-même subsiste, hreflang n'a plus d'objet
        if all(t == path for _, t in keep):
            keep = []
        keep_map = {m.start(): t for m, t in keep}
        for m in reversed(links):
            if m.start() not in keep_map:
                head = head[:m.start()] + head[m.end():]
            else:
                # URL canonique sans .html (sinon « Page avec redirection »)
                t = keep_map[m.start()]
                canon = f'https://bestdateweather.com/{t}' if t else 'https://bestdateweather.com/'
                tag = HREF_RE.sub(f'href="{canon}"', m.group(0), count=1)
                head = head[:m.start()] + tag + head[m.end():]
    return head + rest


def iter_html():
    for dirpath, dirnames, filenames in os.walk(ROOT):
        rel_dir = os.path.relpath(dirpath, ROOT)
        top = rel_dir.split(os.sep)[0]
        if top in SKIP_DIRS:
            dirnames[:] = []
            continue
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in filenames:
            if fn.endswith('.html'):
                yield os.path.relpath(os.path.join(dirpath, fn), ROOT)


def main():
    check = '--check' in sys.argv
    indexable = indexable_paths()
    changed, n_idx, n_noidx, total = [], 0, 0, 0
    for rel in iter_html():
        total += 1
        path = served_path(rel)
        full = os.path.join(ROOT, rel)
        html = open(full, encoding='utf-8').read()
        new = process(html, path, indexable)
        if path in indexable:
            n_idx += 1
        else:
            n_noidx += 1
        if new != html:
            changed.append(rel)
            if not check:
                with open(full, 'w', encoding='utf-8') as f:
                    f.write(new)
    print(f'Pages HTML : {total} | indexables : {n_idx} | noindex : {n_noidx}')
    if check:
        if changed:
            print(f'❌ {len(changed)} page(s) non conforme(s) à la politique d\'indexation, ex. : {changed[:5]}')
            print('   → lancer python3 apply_indexation.py')
            sys.exit(1)
        print('✅ Toutes les pages sont conformes à la politique d\'indexation')
    else:
        print(f'Pages modifiées : {len(changed)}')


if __name__ == '__main__':
    main()
