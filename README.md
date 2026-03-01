# BestDateWeather

Plateforme météo et voyage — données climatiques et recommandations pour 318+ destinations mondiales.

**Site** : [bestdateweather.com](https://bestdateweather.com)

## Architecture

```
├── index.html              # Hub FR (app météo interactive)
├── en/app.html             # Hub EN
├── js/
│   ├── core.js             # Logique app partagée FR/EN (scoring, API, rendu)
│   ├── i18n-fr.js          # Chaînes FR
│   └── i18n-en.js          # Chaînes EN
├── style.css               # CSS partagé (fiches destination)
├── data/
│   ├── destinations.csv    # 318 destinations (coords, slugs, flags, config)
│   ├── climate.csv         # Données climatiques mensuelles (10 ans ERA5)
│   ├── cards.csv           # Cartes projet FR
│   ├── cards_en.csv        # Cartes projet EN
│   ├── events.csv          # Événements par destination/mois
│   └── overrides.csv       # Corrections manuelles
├── scoring.py              # Algorithme de scoring (SOURCE DE VÉRITÉ)
├── generate_all.py         # Générateur fiches destination FR
├── generate_all_en.py      # Générateur fiches destination EN
├── generate_piliers.py     # Pages pilier (par continent/thème)
├── generate_comparatifs.py # Pages comparaison (ville A vs ville B)
├── generate_classements.py # Pages classement (top destinations)
├── fetch_climate.py        # Récupération données Open-Meteo → climate.csv
├── regenerate_scores.py    # Recalcul scores dans pages existantes
├── generate_events.py      # Génération events.csv
├── generate_index_hub.py   # Injection liens dans hubs
├── Makefile                # Pipeline de build
├── vercel.json             # Config Vercel (headers, redirects)
└── scripts/archive/        # Scripts utilitaires one-shot (non utilisés au quotidien)
```

## Build

```bash
make all          # Rebuild complet (~10s)
make destinations # Fiches destination uniquement
make test         # Tests de cohérence scoring
make deploy       # Commit + push → Vercel
```

## Flux de données

```
                     climate.csv
                         │
            ┌────────────┼────────────┐
            ▼            ▼            ▼
       scoring.py    core.js     generate_*.py
       (Python)      (JS app)    (Python → HTML)
            │            │            │
            ▼            ▼            ▼
     FICHE_SCORES   Live scoring   8 000+ pages
     (core.js)      (date/annual)  statiques
```

### Scoring : 3 chemins parallèles

| Chemin | Source | Moteur | Output |
|---|---|---|---|
| Fiches statiques | climate.csv | `scoring.py` → `generate_all.py` | Score /10 dans HTML |
| App mode date | Open-Meteo API live | `core.js` (`computeAndRenderScore`) | Score /10 live |
| App mode annuel | Open-Meteo archive | `core.js` (`rawScoreFiche` + `FICHE_SCORES`) | Score /100 ancré |

⚠️ `scoring.py` est la source de vérité. `core.js` réplique `t_ideal()` et `raw_score()` — toute modification de l'un doit être propagée à l'autre.

## Données

- **climate.csv** : moyennes mensuelles sur 10 ans (ERA5/Open-Meteo) pour 318 destinations
- **Classes éditoriales** : `rec` (recommandé), `mid` (acceptable), `avoid` (déconseillé) — définies manuellement dans climate.csv
- **Scoring ancré** : les scores /10 sont contraints dans la plage de leur classe (rec: 7-10, mid: 4-6.9, avoid: 0.5-3.9)

## Déploiement

Push sur `main` → Vercel déploie automatiquement.

**Domaine** : `bestdateweather.com` (non-www, canonique). `www` redirige en 308.
