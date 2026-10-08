#!/usr/bin/env python3
"""
Export du jeu de données ouvert « Climat de voyage : 12 mois × destinations ».

Publié par Gilles (data.gouv.fr, Kaggle, GitHub) sous licence CC BY 4.0 :
toute réutilisation doit citer BestDateWeather avec un lien. C'est la manière
propre d'obtenir des citations (et des liens) : on donne une ressource utile.

Exclut les destinations dont le point de référence est en altitude alors que
la destination est vécue sur la côte (ex. La Réunion à 1 615 m, Corse à
1 240 m) tant que leurs coordonnées n'ont pas été corrigées.

Usage : python3 scripts/export_open_data.py <dossier_sortie>
"""
import csv
import json
import os
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
EXCLUS = {'reunion': 'point de référence à 1 615 m (centre de l\'île)',
          'corse': 'point de référence à 1 240 m (centre de l\'île)'}


def main(out_dir):
    os.makedirs(out_dir, exist_ok=True)
    dests = {r['slug_fr']: r for r in csv.DictReader(open(os.path.join(ROOT, 'data', 'destinations.csv'), encoding='utf-8-sig'))}
    dup = set(json.load(open(os.path.join(ROOT, 'data', 'duplicate_destinations.json'))).keys())
    dv = json.load(open(os.path.join(ROOT, 'data', 'data_version.json'), encoding='utf-8'))
    rows = list(csv.DictReader(open(os.path.join(ROOT, 'data', 'climate.csv'), encoding='utf-8')))
    out = os.path.join(out_dir, 'bestdateweather-climat-voyage.csv')
    n_dest = set()
    with open(out, 'w', encoding='utf-8', newline='') as f:
        w = csv.writer(f)
        w.writerow(['destination', 'pays', 'latitude', 'longitude', 'precision_point', 'mois_num', 'mois',
                    'temp_max_c', 'temp_min_c', 'jours_pluie_pct', 'precip_mm_jour', 'soleil_h_jour',
                    'source_soleil', 'temp_mer_c', 'score_sur_10', 'url'])
        for r in rows:
            s = r['slug']
            d = dests.get(s)
            if not d or s in dup or s in EXCLUS:
                continue
            n_dest.add(s)
            w.writerow([d['nom_fr'], d['pays'], d['lat'], d['lon'], d.get('precision', ''), r['mois_num'], r['mois'],
                        r['tmax'], r['tmin'], r['rain_pct'], r['precip_mm'], r['sun_h'],
                        r.get('sun_source', ''), r.get('sea_temp', ''), r['score'],
                        f'https://bestdateweather.com/meilleure-periode-{s}'])
    readme = f"""# Climat de voyage : 12 mois pour {len(n_dest)} destinations (BestDateWeather)

Normales climatiques mensuelles et score de voyage sur 10, par destination.

## Contenu
Un fichier CSV (UTF-8), une ligne par destination et par mois :
température maximale et minimale moyennes (°C), part des jours avec au moins
1 mm de pluie (%), précipitations moyennes (mm/jour), ensoleillement (h/jour),
température de la mer (°C, destinations côtières), score de voyage sur 10.

## Sources et méthode
- Réanalyse ERA5 (Copernicus / ECMWF) via Open-Meteo, données quotidiennes {dv.get('periode_donnees', '2016-2025')}.
- Ensoleillement : normales de stations publiées quand elles existent
  (`source_soleil = observed`), sinon valeur ERA5 recalibrée (`calibrated`).
- Score : combinaison pondérée température, pluie, ensoleillement ; méthode
  décrite sur https://bestdateweather.com/methodologie
- Dernière mise à jour des données : {dv.get('donnees_mises_a_jour')}.

## Limites connues
- Les réanalyses lissent les reliefs : une destination « région » est
  représentée par un seul point (colonne `precision_point`).
- En zone tropicale, la réanalyse peut surestimer la fréquence des petites
  pluies par rapport aux stations ; à recouper avant toute conclusion forte.
- Exclues de cette version : {', '.join(f'{k} ({v})' for k, v in EXCLUS.items())}.

## Licence
CC BY 4.0. Réutilisation libre, y compris commerciale, à condition de citer :
« Source : BestDateWeather (bestdateweather.com), d'après ERA5 / Copernicus et Open-Meteo »
avec un lien vers https://bestdateweather.com

Contact : contact@bestdateweather.com
"""
    open(os.path.join(out_dir, 'LISEZMOI.md'), 'w', encoding='utf-8').write(readme)
    print(f'{out} : {len(n_dest)} destinations')


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'open-data-export')
