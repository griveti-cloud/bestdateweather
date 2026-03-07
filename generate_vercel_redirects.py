#!/usr/bin/env python3
"""
generate_vercel_redirects.py
============================
Régénère la section "redirects" de vercel.json depuis les données CSV.

Règle : slug_en != slug_es → les URLs /es/{slug_en}-... doivent
        rediriger vers /es/{slug_es}-... (1 annual + 12 monthly).

Usage :
    python3 generate_vercel_redirects.py [--dry-run]

--dry-run : affiche les redirects générés sans écrire vercel.json.
"""

import csv, json, sys, os

# ── Redirects statiques à conserver tels quels ────────────────────────────
# Ordre conservé : routing lang → one-off historiques
STATIC_REDIRECTS = [
    # Routing racine des versions linguistiques
    {"source": "/fr",  "destination": "/",                                  "permanent": False},
    {"source": "/fr/", "destination": "/",                                  "permanent": False},
    {"source": "/en",  "destination": "/en/app.html",                       "permanent": False},
    {"source": "/en/", "destination": "/en/app.html",                       "permanent": False},
    {"source": "/es",  "destination": "/es/mejores-destinos-clima-2026.html","permanent": False},
    {"source": "/es/", "destination": "/es/mejores-destinos-clima-2026.html","permanent": False},
    # Corrections historiques (URLs FR+EN publiées, indexées)
    {"source": "/methodology-en.html",               "destination": "/en/methodology.html",              "permanent": True},
    {"source": "/meilleure-periode-danang.html",      "destination": "/meilleure-periode-da-nang.html",   "permanent": True},
    {"source": "/danang-meteo-:month.html",           "destination": "/da-nang-meteo-:month.html",        "permanent": True},
    {"source": "/en/best-time-to-visit-danang.html",  "destination": "/en/best-time-to-visit-da-nang.html","permanent": True},
    {"source": "/en/danang-weather-:month.html",      "destination": "/en/da-nang-weather-:month.html",   "permanent": True},
    {"source": "/meilleure-periode-la-nouvelle-orleans.html",    "destination": "/meilleure-periode-nouvelle-orleans.html",      "permanent": True},
    {"source": "/la-nouvelle-orleans-meteo-:month.html",         "destination": "/nouvelle-orleans-meteo-:month.html",           "permanent": True},
    {"source": "/en/best-time-to-visit-la-nouvelle-orleans.html","destination": "/en/best-time-to-visit-nouvelle-orleans.html",  "permanent": True},
    {"source": "/en/la-nouvelle-orleans-weather-:month.html",    "destination": "/en/nouvelle-orleans-weather-:month.html",      "permanent": True},
    {"source": "/meilleure-periode-cartagene.html",   "destination": "/meilleure-periode-cartagena.html", "permanent": True},
    {"source": "/cartagene-meteo-:month.html",        "destination": "/cartagena-meteo-:month.html",      "permanent": True},
    {"source": "/en/best-time-to-visit-cartagene.html","destination": "/en/best-time-to-visit-cartagena.html","permanent": True},
    {"source": "/en/cartagene-weather-:month.html",   "destination": "/en/cartagena-weather-:month.html", "permanent": True},
    {"source": "/meilleure-periode-cuzco.html",       "destination": "/meilleure-periode-cusco.html",     "permanent": True},
    {"source": "/cuzco-meteo-:month.html",            "destination": "/cusco-meteo-:month.html",          "permanent": True},
    {"source": "/en/best-time-to-visit-cuzco.html",   "destination": "/en/best-time-to-visit-cusco.html","permanent": True},
    {"source": "/en/cuzco-weather-:month.html",       "destination": "/en/cusco-weather-:month.html",     "permanent": True},
    {"source": "/meilleure-periode-zanzibar-ville.html",    "destination": "/meilleure-periode-stone-town.html",     "permanent": True},
    {"source": "/zanzibar-ville-meteo-:month.html",         "destination": "/stone-town-meteo-:month.html",          "permanent": True},
    {"source": "/en/best-time-to-visit-zanzibar-ville.html","destination": "/en/best-time-to-visit-stone-town.html", "permanent": True},
    {"source": "/en/zanzibar-ville-weather-:month.html",    "destination": "/en/stone-town-weather-:month.html",     "permanent": True},
]

ES_MONTHS = ['enero','febrero','marzo','abril','mayo','junio',
             'julio','agosto','septiembre','octubre','noviembre','diciembre']


def generate_es_redirects(dests: list[dict]) -> list[dict]:
    """Pour chaque destination où slug_en != slug_es, génère :
    - 1 redirect annual  : /es/mejor-epoca-{slug_en}.html → /es/mejor-epoca-{slug_es}.html
    - 12 redirects monthly : /es/{slug_en}-clima-{mes}.html → /es/{slug_es}-clima-{mes}.html
    """
    redirects = []
    mismatches = [(d['slug_en'], d['slug_es']) for d in dests
                  if d.get('slug_en') and d.get('slug_es') and d['slug_en'] != d['slug_es']]
    mismatches.sort(key=lambda x: x[0])  # ordre déterministe

    for slug_en, slug_es in mismatches:
        redirects.append({
            "source":      f"/es/mejor-epoca-{slug_en}.html",
            "destination": f"/es/mejor-epoca-{slug_es}.html",
            "permanent":   True,
        })
        for mes in ES_MONTHS:
            redirects.append({
                "source":      f"/es/{slug_en}-clima-{mes}.html",
                "destination": f"/es/{slug_es}-clima-{mes}.html",
                "permanent":   True,
            })
    return redirects


def main():
    dry_run = '--dry-run' in sys.argv
    root = os.path.dirname(__file__)

    dests = list(csv.DictReader(open(
        os.path.join(root, 'data', 'destinations.csv'), encoding='utf-8-sig')))

    es_redirects = generate_es_redirects(dests)

    all_redirects = STATIC_REDIRECTS + es_redirects

    print(f"Redirects statiques  : {len(STATIC_REDIRECTS)}")
    print(f"Redirects ES générés : {len(es_redirects)} "
          f"({len(es_redirects)//13} destinations × 13)")
    print(f"Total                : {len(all_redirects)}")

    if dry_run:
        print("\n[DRY-RUN] vercel.json non modifié.")
        return

    vercel_path = os.path.join(root, 'vercel.json')
    v = json.load(open(vercel_path, encoding='utf-8'))
    v['redirects'] = all_redirects
    json.dump(v, open(vercel_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    print("\n✅ vercel.json mis à jour.")


if __name__ == '__main__':
    main()
