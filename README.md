# BestDateWeather

Plateforme météo et voyage — données climatiques et scores pour **672 destinations** mondiales en **5 langues** (FR, EN, EN-US, ES, DE).

**Site** : [bestdateweather.com](https://bestdateweather.com)

---

## Architecture des fichiers

```
├── index.html                      # Hub FR (app météo interactive)
├── en/
│   ├── app.html                    # Hub EN
│   ├── about.html / faq.html / methodology.html
│   ├── legal.html / privacy.html / contact.html
│   ├── {slug}-weather-{month}.html # Pages mensuelles EN (672×12)
│   ├── best-time-to-visit-{slug}.html # Pages annuelles EN (672)
│   ├── {a}-vs-{b}-weather.html     # Comparatifs EN
│   └── best-*.html                 # Classements EN
├── es/
│   ├── app.html                    # Hub ES
│   ├── faq.html / contacto.html / aviso-legal.html / privacidad.html
│   ├── {slug}-clima-{month}.html   # Pages mensuelles ES (672×12)
│   ├── mejor-epoca-{slug}.html     # Pages annuelles ES (672)
│   ├── {a}-vs-{b}-clima.html       # Comparatifs ES
│   └── mejor-*.html                # Classements ES
├── de/
│   ├── app.html                    # Hub DE
│   ├── faq.html / kontakt.html / impressum.html / datenschutz.html
│   ├── {slug}-wetter-{month}.html  # Pages mensuelles DE (672×12)
│   ├── beste-reisezeit-{slug}.html # Pages annuelles DE (672)
│   ├── {a}-vs-{b}-wetter.html      # Comparatifs DE
│   └── beste-*.html                # Classements DE
├── us/
│   ├── app.html                    # Hub US (°F)
│   ├── about.html / faq.html / methodology.html
│   ├── legal.html / privacy.html / contact.html
│   ├── {slug}-weather-{month}.html # Pages mensuelles US (672×12, °F)
│   ├── best-time-to-visit-{slug}.html # Pages annuelles US (672, °F)
│   ├── {a}-vs-{b}-weather.html     # Comparatifs US (°F)
│   └── best-*.html                 # Classements US (°F)
├── {slug}-meteo-{month}.html       # Pages mensuelles FR (672×12)
├── meilleure-periode-{slug}.html   # Pages annuelles FR (672)
├── {a}-ou-{b}-climat.html          # Comparatifs FR
├── meilleures-destinations-meteo.html  # Page classement annuel FR (pilier)
├── ou-partir-en-{month}.html       # Pages piliers mensuels FR (12)
├── js/
│   ├── core.js                     # Logique app (scoring, API, rendu) — SOURCE
│   ├── core.min.js                 # = copie de core.js (pas de minification regex)
│   ├── weather-banner.js           # Bandeau météo live + recherches récentes — SOURCE
│   ├── weather-banner.min.js       # Minifié via terser
│   ├── weather-banner-2.min.js     # = copie de weather-banner.min.js — FICHIER SERVI EN PROD
│   ├── fiche-scores.js             # Scores pré-calculés : 'lat,lon' → [12 scores]
│   ├── fiche-slugs.js              # Autocomplete : alias → {fr, en, es, de}
│   ├── fiche-slugs.min.js          # = copie de fiche-slugs.js
│   ├── i18n-fr.js / i18n-fr.min.js # Chaînes FR
│   ├── i18n-en.js / i18n-en.min.js # Chaînes EN
│   ├── i18n-es.js / i18n-es.min.js # Chaînes ES
│   ├── i18n-de.js / i18n-de.min.js # Chaînes DE
│   └── i18n-en-us.js / i18n-en-us.min.js # Chaînes EN-US (°F, en-US locale)
├── locales/
│   ├── fr.json                     # Textes FR générateurs
│   ├── en.json                     # Textes EN générateurs
│   ├── es.json                     # Textes ES générateurs
│   ├── de.json                     # Textes DE générateurs
│   └── en-us.json                  # Textes EN-US générateurs
├── data/
│   ├── destinations.csv            # 672 destinations (slugs, coords, pays, flags…)
│   ├── climate.csv                 # Données climatiques mensuelles (score, tmin, tmax, rain, sun, sea_temp, beach_score)
│   ├── ski_seasons.csv             # Mois de saison ski valides par destination (slug → liste mois 1-12)
│   └── suggestions.json           # Destinations similaires par région climatique
├── lib/
│   ├── common.py                   # Composants HTML partagés (tables, scores, footer…)
│   └── page_config.py              # Chargement locales
├── css/
│   └── weather-banner.css          # CSS du bandeau météo live
├── style.css                       # CSS global (tables, piliers, classements…)
├── app.css                         # CSS app interactive
├── sitemap-fr.xml                  # ~8717 URLs FR
├── sitemap-en.xml                  # ~8715 URLs EN
├── sitemap-es.xml                  # ~8706 URLs ES
├── sitemap-de.xml                  # ~8710 URLs DE
├── sitemap-us.xml                  # ~8710 URLs US
└── sitemap-index.xml               # Index des 5 sitemaps
```

---

## Générateurs

| Script | Output | Commande |
|--------|--------|---------|
| `generate_pages.py` | Pages mensuelles + annuelles FR/EN/ES/DE/US | `python3 generate_pages.py` |
| `generate_piliers.py` | Pages piliers mensuels + annuels (5 langues) | `python3 generate_piliers.py` |
| `generate_classements.py` | Pages classements thématiques | `python3 generate_classements.py` |
| `generate_comparatifs.py` | Pages comparatifs A vs B (4 langues) | `python3 generate_comparatifs.py` |
| `generate_sitemaps.py` | 5 sitemaps XML | `python3 generate_sitemaps.py` |
| `fetch_climate.py` | Met à jour `climate.csv` via Open-Meteo | `python3 fetch_climate.py` |

### Régénération partielle piliers

```bash
python3 generate_piliers.py --annual-only   # Pages annuelles uniquement
python3 generate_piliers.py --lang fr       # Une langue uniquement
```

---

## Règles de développement

### ⚠️ Règles impératives

1. **Minifier après modif JS** : `npx terser js/X.js -o js/X.min.js --compress --mangle`
2. **`weather-banner-2.min.js`** : toujours copier `weather-banner.min.js` vers ce fichier — c'est le fichier réellement servi en prod
3. **`core.min.js`** : copier `core.js` tel quel — ne jamais minifier (regex fragiles)
4. **Cache bust** : bumper `?v=N` dans les HTML après modif JS
5. **Vérifier syntaxe** : `node --check js/core.js`
6. **Commits atomiques** descriptifs
7. **Après modif `lib/common.py` ou générateurs** → régénérer les pages concernées
8. **Après ajout destinations** → `python3 generate_sitemaps.py`

---

## Cas courants

### Ajouter une destination

1. Ajouter ligne dans `data/destinations.csv`
2. Récupérer données climatiques : `python3 fetch_climate.py --slug {slug}`
3. Si station de ski : ajouter ligne dans `data/ski_seasons.csv` (mois séparés par `-`, ex: `12-1-2-3-4`)
4. Régénérer pages : `python3 generate_pages.py --slug {slug}`
5. Mettre à jour autocomplete : `python3 generate_fiche_slugs.py`
6. Mettre à jour scores : `python3 scripts/build_fiche_scores.py`
7. Mettre à jour sitemaps : `python3 generate_sitemaps.py`

### Modifier le scoring

1. Modifier `scoring.py` (source de vérité Python)
2. Propager les changements dans `js/core.js` (réplique JS)
3. Copier `core.js` → `core.min.js` (**ne jamais minifier**)
4. `python3 regenerate_scores.py` → recalcule les scores dans les HTML existants

### Modifier les textes i18n

1. Modifier `locales/fr.json`, `locales/en.json`, `locales/es.json`, `locales/de.json`, `locales/en-us.json`
2. `python3 check_locale.py` → vérifie parité des clés entre langues
3. Relancer le ou les générateurs concernés

### Modifier le bandeau météo (weather-banner)

1. Modifier `js/weather-banner.js`
2. `npx terser js/weather-banner.js -o js/weather-banner.min.js --compress --mangle`
3. `cp js/weather-banner.min.js js/weather-banner-2.min.js`

---

## Flux de données

```
destinations.csv ──────────────────────────────────────────────┐
       │                                                         │
  fetch_climate.py                                         generate_*.py
       │                                                         │
  climate.csv ──┬──── scoring.py ──── generate_pages.py         │
                │          │                   │                 │
  ski_seasons.csv          │             HTML pages              │
                │      core.js            FR+EN+ES+DE+US    classements
                │     (réplique)                            piliers
                │          │                               comparatifs
                │    Live scoring
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
| `slug_de` | `barcelona` | |
| `nom_fr` | `Barcelone` | Nom affiché FR |
| `nom_bare` | `Barcelone` | Sans article |
| `pays` | `Espagne` | Pays en français |
| `flag` | `es` | Code ISO 2 lettres |
| `prep_fr` | `à` | Préposition FR (à/en/au/aux) |
| `prep_es` | `en` | Préposition ES |
| `prep_de` | `nach` | Préposition DE |
| `lat` / `lon` | `41.39` / `2.15` | Coordonnées décimales |
| `tropical` | `False` | Booléen |
| `mountain` | `False` | Booléen — utilisé pour filtre ski + `ski_seasons.csv` |
| `coastal` | `True` | Booléen |
| `monthly` | `True` | Pages mensuelles activées |
| `hero_sub_fr` | `"Barcelone, ..."` | Tagline FR |
| `hero_sub_en` | `"Barcelona, ..."` | Tagline EN |
| `hero_sub_es` | `"Barcelona, ..."` | Tagline ES |
| `nom_en` | `Barcelona` | |
| `nom_es` | `Barcelona` | |
| `nom_de` | `Barcelona` | |
| `country_en` | `Spain` | |
| `country_es` | `España` | |
| `country_de` | `Spanien` | |
| `booking_dest_id` | `-372490` | ID Booking.com (négatif) ou vide |
| `aliases` | `barca bcn` | Espace-séparé, pour autocomplete |

## Schéma ski_seasons.csv

| Colonne | Exemple | Notes |
|---------|---------|-------|
| `slug` | `chamonix` | Correspond à `slug_fr` dans destinations.csv |
| `ski_months` | `12-1-2-3-4` | Mois valides séparés par `-`. Vide = pas de saison ski (mountain=True mais pas de ski commercial) |

Exemples : `bariloche` → `6-7-8-9` (hémisphère sud), `zermatt` → `1-2-3-4-5-7-8-9-10-11-12` (glacier, quasi année entière).

---

## Régions (REGION_MAP)

Codes utilisés dans les filtres des pages piliers :

| Code | Région |
|------|--------|
| `eu` | Europe |
| `af` | Afrique |
| `am` | Amériques |
| `as` | Asie |
| `me` | Moyen-Orient |
| `oc` | Océanie / Pacifique |

---

## Points d'attention

- **Slugs** : ASCII strict (a-z, 0-9, tiret). Jamais de caractères accentués (`koweit` pas `koweït`).
- **core.min.js** : toujours copier `core.js` tel quel. La minification regex casse l'UI.
- **weather-banner-2.min.js** : c'est CE fichier qui est chargé en prod (pas `weather-banner.min.js`). Toujours les synchroniser.
- **fiche-slugs.js** : régénérer via `generate_fiche_slugs.py` après chaque batch de destinations.
- **EN-US vs EN** : les pages `/us/` sont des variantes indépendantes (°F, `lang="en-US"`), pas des redirects depuis `/en/`.
- **Localisation** : ~30 `is_fr` subsistent dans les générateurs pour des cas structurels complexes.
- **Comparatifs** : `generate_comparatifs.py` gère les 4 langues et met à jour les 4 sitemaps directement.

---

## Déploiement

Push sur `main` → Vercel déploie automatiquement.

**Domaine** : `bestdateweather.com` (non-www, canonique). `www` redirige en 308.
