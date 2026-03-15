# BestDateWeather

Plateforme météo et voyage — données climatiques et scores pour **700 destinations** mondiales en **5 langues** (FR, EN, EN-US, ES, DE).

**Site** : [bestdateweather.com](https://bestdateweather.com)

---

## Architecture des fichiers

```
├── index.html                      # Hub FR (app météo interactive)
├── en/
│   ├── app.html                    # Hub EN
│   ├── {slug}-weather-{month}.html # Pages mensuelles EN (700×12)
│   ├── best-time-to-visit-{slug}.html # Pages annuelles EN (700)
│   └── best-*.html                 # Classements EN
├── es/ de/ us/                     # Idem pour ES, DE, US (°F)
├── {slug}-meteo-{month}.html       # Pages mensuelles FR (700×12)
├── meilleure-periode-{slug}.html   # Pages annuelles FR (700)
├── js/
│   ├── core.js                     # Logique app (scoring, API, rendu) — SOURCE
│   ├── core.min.js                 # Minifié via terser (143KB → 93KB)
│   ├── weather-banner-2.js         # Bandeau météo live + autocomplete — SOURCE
│   ├── weather-banner-2.min.js     # Minifié via terser — FICHIER SERVI EN PROD
│   ├── fiche-slugs.js              # Autocomplete : alias → {fr, en, es, de} — SOURCE
│   ├── fiche-slugs.min.js          # Minifié via terser (97KB → 80KB)
│   ├── fiche-scores.js             # Scores pré-calculés par coordonnées
│   └── i18n-{lang}.js / .min.js   # Chaînes i18n (fr, en, en-us, es, de)
├── locales/
│   ├── fr.json                     # Textes FR générateurs (référence)
│   ├── en.json                     # Textes EN générateurs (x-default)
│   ├── es.json / de.json / en-us.json
├── data/
│   ├── destinations.csv            # 700 destinations (slugs, coords, pays, flags…)
│   ├── climate.csv                 # Données climatiques mensuelles (score, tmin, tmax, rain, sun…)
│   ├── editorial.json              # Contenus éditoriaux par destination
│   ├── events.csv                  # Événements/festivals
│   ├── monthly.json                # Données mensuelles agrégées pour l'app
│   ├── suggestions.json            # Destinations similaires par région climatique
│   ├── sea_temps.json              # Températures de mer
│   ├── cards.csv / cards_en.csv / cards_es.csv
│   └── overrides.csv               # Overrides manuels scoring
├── lib/
│   ├── common.py                   # Composants HTML partagés
│   └── page_config.py              # Chargement locales, utilitaires
├── scripts/
│   ├── check_locale.py             # Validation cohérence locales (exit 1 si erreur)
│   ├── fetch_climate.py            # Met à jour climate.csv via Open-Meteo
│   ├── fetch_sea_temps_mass.py     # Met à jour sea_temps.json
│   └── archive/                   # Scripts one-shot (migration, refetch…)
├── sitemap-{lang}.xml              # ~9 100 URLs par langue (fr/en/es/de/us)
├── sitemap-index.xml
├── robots.txt
└── vercel.json                     # Headers sécurité, 886 redirects, CSP
```

---

## Générateurs

| Script | Output | Commande |
|--------|--------|---------|
| `generate_pages.py` | Pages mensuelles + annuelles ×5 langues | `python3 generate_pages.py --lang fr [slugs…]` |
| `generate_piliers.py` | Pages piliers mensuels + annuels | `python3 generate_piliers.py` |
| `generate_classements.py` | Pages classements thématiques | `python3 generate_classements.py` |
| `generate_comparatifs.py` | Pages comparatifs A vs B | `python3 generate_comparatifs.py` |
| `generate_sitemaps.py` | 5 sitemaps XML | `python3 generate_sitemaps.py` |
| `generate_fiche_slugs.py` | `js/fiche-slugs.js` + `.min.js` | `python3 generate_fiche_slugs.py` |
| `scripts/fetch_climate.py` | Met à jour `climate.csv` | `python3 scripts/fetch_climate.py` |

### Régénération partielle

```bash
python3 generate_pages.py --lang fr                        # FR uniquement
python3 generate_pages.py --lang fr en en-us es de paris   # Slug spécifique, toutes langues
python3 generate_piliers.py --annual-only --lang fr        # Piliers annuels FR
```

---

## Règles de développement

### ⚠️ Règles impératives

1. **Minifier après modif JS** : `npx terser js/X.js -o js/X.min.js --compress --mangle`
2. **Vérifier syntaxe** : `node --check js/core.js`
3. **Commits atomiques** descriptifs
4. **Après modif `lib/`** → régénérer les pages concernées
5. **Après ajout destinations** → `python3 generate_sitemaps.py`
6. **Après modif locales** → `python3 scripts/check_locale.py`

---

## Cas courants

### Ajouter une destination

1. Ajouter ligne dans `data/destinations.csv`
2. `python3 scripts/fetch_climate.py --slug {slug}`
3. Si station de ski → mettre `mountain=True` (le score ski est calculé automatiquement)
4. `python3 generate_pages.py --lang fr en en-us es de {slug}`
5. `python3 generate_fiche_slugs.py`
6. `python3 generate_sitemaps.py`

### Modifier le scoring

1. Modifier `scoring.py` (source de vérité Python)
2. Propager dans `js/core.js` (réplique JS pour l'app live)
3. `npx terser js/core.js -o js/core.min.js --compress --mangle`

### Modifier les textes i18n

1. Modifier le(s) fichier(s) dans `locales/`
2. `python3 scripts/check_locale.py` → doit retourner exit 0
3. Relancer le(s) générateur(s) concerné(s)

### Modifier le bandeau météo

1. Modifier `js/weather-banner-2.js`
2. `npx terser js/weather-banner-2.js -o js/weather-banner-2.min.js --compress --mangle`

---

## Flux de données

```
destinations.csv ─────────────────────────────────────────┐
       │                                                    │
  fetch_climate.py                                    generate_*.py
       │                                                    │
  climate.csv ──── scoring.py ──── generate_pages.py    classements
                   │  └─ compute_ski_score()            piliers
                   │     (mountain=True)                comparatifs
               core.js
              (réplique JS)
```

### Scoring : 3 chemins parallèles

| Chemin | Source | Moteur | Output |
|--------|--------|--------|--------|
| Fiches statiques | `climate.csv` | `scoring.py` | Score /10 dans HTML |
| App mode date | Open-Meteo live | `core.js` `computeAndRenderScore()` | Score /100 live |
| App mode annuel | Open-Meteo archive | `core.js` + `fiche-scores.js` | Score /100 ancré |

⚠️ `scoring.py` est la source de vérité. `core.js` réplique `tIdeal()` et `rawScoreFiche()` — toute modification de l'un **doit** être propagée à l'autre.

### Scoring ski (destinations `mountain=True`)

Calculé par `compute_ski_score(tmax, rain_pct, sun_h)` dans `scoring.py`.
Sur les pages annuelles montagne : les KPIs hero (meilleurs mois, température, pluie) sont basés sur le **score ski**, pas le score général. Label : "Meilleures périodes ski" (clé `labels.best_ski_months_lbl_tpl` dans chaque locale).

---

## Schéma destinations.csv

| Colonne | Exemple | Notes |
|---------|---------|-------|
| `slug_fr` | `barcelone` | ASCII, a-z0-9- uniquement |
| `slug_en/es/de` | `barcelona` | |
| `nom_fr` | `Barcelone` | Nom affiché FR |
| `nom_bare` | `Barcelone` | Sans article |
| `pays` | `Espagne` | Pays en français |
| `flag` | `es` | Code ISO 2 lettres |
| `prep_fr/es/de` | `à` / `en` / `nach` | Préposition selon langue |
| `lat` / `lon` | `41.39` / `2.15` | Coordonnées décimales |
| `tropical` | `False` | Booléen |
| `mountain` | `False` | Booléen — active scoring ski + KPIs hero ski |
| `coastal` | `True` | Booléen |
| `monthly` | `True` | Pages mensuelles activées |
| `hero_sub_fr/en/es/de` | `"Barcelone, …"` | Tagline (120 chars max) |
| `nom_en/es/de` | `Barcelona` | |
| `country_en/es/de` | `Spain` | |
| `booking_dest_id` | `-372490` | ID Booking.com (négatif) ou vide |
| `aliases` | `barca bcn` | Espace-séparé, pour autocomplete |

---

## Régions (REGION_MAP)

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

- **Slugs** : ASCII strict. `koweit` pas `koweït`.
- **`weather-banner-2.min.js`** : fichier servi en prod. Source = `weather-banner-2.js` (reconstituée mars 2026 — noms de variables manglés, logique intacte).
- **`fiche-slugs.js`** : régénérer via `generate_fiche_slugs.py` après chaque batch de destinations.
- **EN-US vs EN** : variantes indépendantes (°F, `lang="en-US"`), pas des redirects. Le `x-default` hreflang pointe vers `/en/`.
- **Locales** : FR est la référence. Toute nouvelle clé en FR doit être répercutée dans les 4 autres. `scripts/check_locale.py` détecte les dérives.
- **Ski** : pas de `ski_seasons.csv`. Score calculé dynamiquement via `compute_ski_score()` pour toute destination avec `mountain=True`.
- **`data/`** : ne commiter que les fichiers actifs. Backups, logs et fichiers intermédiaires (`*.bak`, `*_progress.json`) vont dans `scripts/archive/` ou sont ignorés.

---

## Déploiement

Push sur `main` → Vercel déploie automatiquement.

**Domaine** : `bestdateweather.com` (non-www, canonique). `www` redirige en 308.

### Sécurité (vercel.json)

- HSTS : `max-age=31536000; includeSubDomains; preload`
- CSP : `script-src` inclut GTM, cdnjs, GetYourGuide, Google Ads. `unsafe-inline` maintenu (requis par GTM).
- `img-src` : inclut `cdn.getyourguide.com` et `widget.getyourguide.com`.
- `frame-src` : `widget.getyourguide.com`.
- `frame-ancestors 'self'` : protection clickjacking.
