# BestDateWeather

Plateforme météo et voyage — données climatiques et scores pour **617 destinations** mondiales en **4 langues** (FR, EN, ES, EN-US).

**Site** : [bestdateweather.com](https://bestdateweather.com)

---

## Architecture des fichiers

```
├── index.html                      # Hub FR (app météo interactive)
├── en/
│   ├── app.html                    # Hub EN
│   ├── about.html / faq.html / methodology.html
│   ├── legal.html / privacy.html / contact.html
│   ├── {slug}-weather-{month}.html # Pages mensuelles EN (617×12)
│   ├── best-time-to-visit-{slug}.html # Pages annuelles EN (617)
│   ├── {a}-vs-{b}-weather.html     # Comparatifs EN (33)
│   └── best-*.html                 # Classements EN (28)
├── es/
│   ├── app.html                    # Hub ES
│   ├── faq.html / contacto.html / aviso-legal.html / privacidad.html
│   ├── {slug}-clima-{month}.html   # Pages mensuelles ES (617×12)
│   ├── mejor-epoca-{slug}.html     # Pages annuelles ES (617)
│   ├── {a}-vs-{b}-clima.html       # Comparatifs ES (33)
│   └── mejor-*.html                # Classements ES (28)
├── us/
│   ├── app.html                    # Hub US
│   ├── about.html / faq.html / methodology.html  # Températures en °F
│   ├── legal.html / privacy.html / contact.html
│   ├── {slug}-weather-{month}.html # Pages mensuelles US (617×12, °F)
│   ├── best-time-to-visit-{slug}.html # Pages annuelles US (617, °F)
│   ├── {a}-vs-{b}-weather.html     # Comparatifs US (33, °F)
│   └── best-*.html                 # Classements US (28)
├── {slug}-meteo-{month}.html       # Pages mensuelles FR (617×12)
├── meilleure-periode-{slug}.html   # Pages annuelles FR (617)
├── {a}-ou-{b}-climat.html          # Comparatifs FR (33)
├── best-*.html                     # Classements FR (28)
├── js/
│   ├── core.js                     # Logique app (scoring, API, rendu) — SOURCE
│   ├── core.min.js                 # = copie de core.js (pas de minification regex)
│   ├── fiche-scores.js             # Scores pré-calculés : 'lat,lon' → [12 scores]
│   ├── fiche-slugs.js              # Autocomplete : alias → {fr, en, es}
│   ├── fiche-slugs.min.js          # = copie de fiche-slugs.js
│   ├── i18n-fr.js / i18n-fr.min.js # Chaînes FR
│   ├── i18n-en.js / i18n-en.min.js # Chaînes EN
│   ├── i18n-es.js / i18n-es.min.js # Chaînes ES
│   └── i18n-en-us.js / i18n-en-us.min.js # Chaînes EN-US (°F, en-US locale)
├── locales/
│   ├── fr.json                     # Clés i18n générateurs FR
│   ├── en.json                     # Clés i18n générateurs EN
│   ├── es.json                     # Clés i18n générateurs ES
│   └── en-us.json                  # Clés i18n générateurs EN-US
├── data/
│   ├── destinations.csv            # 617 destinations (coords, slugs ×3, flags, config)
│   ├── climate.csv                 # 617×12 = 7404 rows (moyennes mensuelles P50, 10 ans)
│   ├── events.csv                  # Événements par destination/mois
│   └── overrides.csv               # Corrections manuelles scores
├── scoring.py                      # Algorithme scoring (SOURCE DE VÉRITÉ)
├── generate_pages.py               # Générateur fiches FR+EN+ES+US (monthly + annual)
├── generate_piliers.py             # Pages pilier par mois (FR+EN+ES+US)
├── generate_comparatifs.py         # Comparatifs A vs B — FR+EN+ES+US (33×4 = 132 pages)
├── generate_classements.py         # Classements top destinations — FR+EN+ES+US (28×4)
├── generate_index_hub.py           # Injection cartes dans hubs FR+EN+ES+US
├── generate_fiche_slugs.py         # Régénère fiche-slugs.js depuis destinations.csv
├── fetch_climate.py                # Récupération Open-Meteo → climate.csv (P50)
├── regenerate_scores.py            # Recalcul scores dans HTML existants
├── check_locale.py                 # Audit cohérence locales FR/EN/ES/EN-US
├── scripts/
│   ├── generate_sitemaps.py        # Régénère sitemap-fr/en/es/us.xml + sitemap-index.xml
│   └── archive/                    # Scripts one-shot archivés
├── sitemap-fr.xml                  # ~8080 URLs
├── sitemap-en.xml                  # ~8079 URLs
├── sitemap-es.xml                  # ~8081 URLs
├── sitemap-us.xml                  # ~8085 URLs
├── sitemap-index.xml               # Index FR+EN+ES+US
├── robots.txt                      # Disallow app.html? sur toutes langues
└── vercel.json                     # Config Vercel (headers, redirects 308/301)
```

---

## Pipeline de build

### Ajouter des destinations

1. Ajouter lignes dans `data/destinations.csv` (voir schéma ci-dessous)
2. `python3 fetch_climate.py` → remplit `climate.csv` via Open-Meteo
3. `python3 generate_pages.py` → génère 13 pages × 4 langues par destination
4. `python3 generate_classements.py` → met à jour classements FR+EN+ES+US
5. `python3 generate_piliers.py` → met à jour piliers FR+EN+ES+US
6. `python3 generate_fiche_slugs.py` → met à jour autocomplete
7. `python3 scripts/generate_sitemaps.py` → régénère les 4 sitemaps + index
8. Mettre à jour `js/fiche-scores.js` via `scripts/build_fiche_scores.py`

### Modifier le scoring

1. Modifier `scoring.py` (source de vérité Python)
2. Propager les changements dans `js/core.js` (réplique JS)
3. Copier `core.js` → `core.min.js` (**ne jamais utiliser de minification regex**)
4. `python3 regenerate_scores.py` → recalcule les scores dans les HTML existants

### Modifier les textes i18n

1. Modifier `locales/fr.json`, `locales/en.json`, `locales/es.json`, `locales/en-us.json`
2. `python3 check_locale.py` → vérifie parité des clés entre langues
3. Relancer le ou les générateurs concernés

### Régénérer les comparatifs

```bash
python3 generate_comparatifs.py   # génère FR+EN+ES+US (132 pages) + màj 4 sitemaps
```

---

## Flux de données

```
destinations.csv ──────────────────────────────────────────────┐
       │                                                         │
  fetch_climate.py                                         generate_*.py
       │                                                         │
  climate.csv ──┬──── scoring.py ──── generate_pages.py         │
                │          │                   │                 │
                │      core.js            HTML pages             │
                │     (réplique)        FR+EN+ES+US         classements
                │          │                               piliers
                │    Live scoring                          comparatifs
                │
           fiche-scores.js
          (scores pré-calculés
           par coordonnées)
```

### Scoring : 3 chemins parallèles

| Chemin | Source données | Moteur | Output |
|--------|---------------|--------|--------|
| Fiches statiques | `climate.csv` | `scoring.py` → `generate_pages.py` | Score /10 dans HTML |
| App mode date | Open-Meteo API live | `core.js` `computeAndRenderScore()` | Score /10 live |
| App mode annuel | Open-Meteo archive | `core.js` `rawScoreFiche()` + `fiche-scores.js` | Score /100 ancré |

⚠️ `scoring.py` est la source de vérité. `core.js` réplique `t_ideal()` et `raw_score()` — toute modification de l'un **doit** être propagée à l'autre.

---

## Schéma destinations.csv

| Colonne | Exemple | Notes |
|---------|---------|-------|
| `slug_fr` | `barcelone` | ASCII uniquement, a-z0-9- |
| `slug_en` | `barcelona` | |
| `slug_es` | `barcelona` | |
| `nom_fr` | `Barcelone` | Nom affiché FR |
| `nom_bare` | `Barcelone` | Sans article |
| `pays` | `Espagne` | Pays en français |
| `flag` | `es` | Code ISO 2 lettres |
| `prep_fr` | `à` | Préposition FR (à/en/au/aux) |
| `prep_es` | `en` | Préposition ES |
| `lat` / `lon` | `41.39` / `2.15` | Coordonnées décimales |
| `tropical` | `False` | Booléen |
| `mountain` | `False` | Booléen |
| `coastal` | `True` | Booléen |
| `monthly` | `True` | Pages mensuelles activées |
| `hero_sub_fr` | `"Barcelone, ..."` | Tagline FR (fallback générique si vide) |
| `hero_sub_en` | `"Barcelona, ..."` | Tagline EN |
| `hero_sub_es` | `"Barcelona, ..."` | Tagline ES |
| `nom_en` | `Barcelona` | |
| `nom_es` | `Barcelona` | |
| `country_en` | `Spain` | |
| `country_es` | `España` | |
| `booking_dest_id` | `-372490` | ID Booking.com (négatif) ou vide |
| `aliases` | `barca bcn` | Espace-séparé, pour autocomplete |

---

## Points d'attention

- **Slugs** : ASCII strict (a-z, 0-9, tiret). Jamais de caractères accentués (`koweit` pas `koweït`).
- **core.min.js** : toujours copier `core.js` tel quel. La minification regex casse l'UI.
- **fiche-slugs.js** : régénérer via `generate_fiche_slugs.py` après chaque batch de destinations.
- **EN-US vs EN** : les pages `/us/` sont des variantes indépendantes (°F, `lang="en-US"`), pas des redirects depuis `/en/`.
- **Localisation** : ~30 `is_fr` subsistent dans les générateurs pour des cas structurels complexes (FAQ, titres CSV-dépendants).
- **Comparatifs** : `generate_comparatifs.py` gère les 4 langues et met à jour les 4 sitemaps directement.

---

## Déploiement

Push sur `main` → Vercel déploie automatiquement.

**Domaine** : `bestdateweather.com` (non-www, canonique). `www` redirige en 308.
