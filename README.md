# BestDateWeather

Plateforme météo et voyage — données climatiques ERA5 et scores pour **697 destinations** mondiales en **5 langues** (FR, EN, EN-US, ES, DE).

**Site** : [bestdateweather.com](https://bestdateweather.com)  
**Pages générées** : ~45 700 HTML statiques  
**Dernière mise à jour** : mars 2026  
**Hébergement** : Cloudflare Workers Assets (`bestdateweather-prod`)

---

## Chiffres clés

| Type | FR | EN | ES | DE | US |
|------|----|----|----|----|-----|
| Pages mensuelles | 8 370 | 8 372 | 8 367 | 8 371 | 8 372 |
| Pages annuelles | 699 | 700 | 699 | 699 | 699 |
| Comparatifs | 50 | 50 | 50 | 50 | 50 |
| Piliers mensuels | 12 | 12 | 12 | 12 | — |

**Éditorial** : `data/editorial.json` — 33 600+ textes différenciants par destination/mois/langue  
**Destinations** : 697 · **Paires comparatifs** : 50

---

## Architecture des fichiers

```
index.html                          # Hub FR (app météo interactive)
en/
  app.html                          # Hub EN
  {slug}-weather-{month}.html       # Pages mensuelles EN (697 × 12)
  best-time-to-visit-{slug}.html    # Pages annuelles EN (697)
  best-*.html                       # Classements EN
  {slug}-vs-{slug}-weather.html     # Comparatifs EN (50)
  where-to-go-in-{month}.html       # Piliers mensuels EN (12)
es/ de/ us/                         # Idem pour ES, DE, US
{slug}-meteo-{month}.html           # Pages mensuelles FR (697 × 12)
meilleure-periode-{slug}.html       # Pages annuelles FR (697)
ou-partir-en-{month}.html           # Piliers mensuels FR (12)
{slug}-ou-{slug}-climat.html        # Comparatifs FR (50)
meilleures-destinations-meteo.html  # Hub annuel FR

js/
  core.js                           # Logique app (scoring, API, rendu) — SOURCE
  core.min.js                       # Minifié via terser (?v=28)
  weather-banner-2.js               # Bandeau météo live + autocomplete — SOURCE
  weather-banner-2.min.js           # Minifié (?v=5)
  fiche-slugs.js / fiche-slugs.min.js  # Autocomplete : alias → slugs 5 langues
  fiche-scores.js                   # Scores précalculés par coord lat/lon (697 dest × 12 mois)
  dest-search.js / dest-data.js     # Recherche destinations

locales/
  fr.json / en.json / en-us.json / es.json / de.json

data/
  destinations.csv                  # 697 destinations (slugs, coords, pays, flags, tropical, gyg_active…)
  climate.csv                       # Données climatiques mensuelles ERA5 (score, tmin, tmax, rain, sun, sea_temp, dew_point_mean…)
  monthly.json                      # Données résumées par coord pour app annuelle (inclut dewPoint)
  editorial.json                    # 33 600+ textes éditoriaux — clé : {slug_fr}:{mois_num}:{lang}
  overrides.csv                     # Overrides manuels scoring

lib/
  common.py                         # Composants HTML partagés, weather_emoji, _classify_rain_pattern, score_badge…
  page_config.py                    # Chargement locales, build_config, utilitaires

check_deploy.py                     # Vérification cohérence cross-surfaces (à lancer avant chaque deploy)
```

---

## Générateurs

| Script | Rôle |
|--------|------|
| `generate_pages.py` | Pages mensuelles + annuelles (697 dest × 12 mois × 5 langues) + sync `CORE_JS_VERSION` |
| `generate_piliers.py` | Piliers mensuels + hubs annuels (5 langues) |
| `generate_classements.py` | Pages classements thématiques (5 langues) |
| `generate_comparatifs.py` | Pages comparatifs X vs Y (50 paires × 5 langues) |
| `generate_index_hub.py` | Injection SILO 1 dans app.html / index.html |
| `generate_sitemaps.py` | Sitemaps segmentés (10 fichiers) |

---

## Données climatiques

- **Source** : Open-Meteo (ERA5) — moyennes sur 10 ans
- **Méthode** : moyenne (mean) sur 10 ans. `precip_mm` en mean intentionnel (P50 → 0 sur mois secs)
- **Dew point** : `dew_point_mean` dans `climate.csv` (ERA5 `dew_point_2m_mean`) — 697 destinations, nearest-neighbor pour 29 manquants
- **Température mer** : `sea_temp` dans `climate.csv`
- **Scoring** : algorithme propriétaire — voir section Scoring ci-dessous

---

## Scoring

### Modèle (scoring.py → core.js)

```
raw_score = 0.40 × t_ideal(tmax) + 0.35 × (1 - effective_rain/100) + 0.25 × min(1, sun_h/15)
         - dew_point_penalty(tmax, dew_point)
```

**Courbe thermique `t_ideal(tmax)` — breakpoints :**

| Plage | Valeur |
|-------|--------|
| ≤ 5°C | 0.00 |
| 5 → 14°C | 0.00 → 0.30 |
| 14 → 22°C | 0.30 → 0.80 |
| 22 → 28°C | 0.80 → 1.00 |
| 28 → 31°C | 1.00 → 0.90 |
| 31 → 34°C | 0.90 → 0.60 |
| 34 → 37°C | 0.60 → 0.25 |
| 37 → 40°C | 0.25 → 0.05 |
| > 40°C | 0.00 |

**Caps de classe (effective_classe) :**
- `tmax ≥ 38°C` → classe `avoid`
- `tmax ≥ 34°C + classe rec` → classe `mid`
- `tmax ≥ 30°C + dew_point ≥ 16°C + classe rec` → classe `mid` (**cap humidité**)

**Pénalité humidité (`dew_point_penalty`) :**
- Active si `tmax ≥ 26°C` ET `dew_point ≥ 16°C`
- Max −0.20 pts bruts (coeff 0.20 × facteur_tmax × facteur_dew)

**Normalisation :** score brut → [0.5–3.9] / [4.0–6.9] / [7.0–10.0] selon classe, via percentiles globaux (p5–p95) + courbe puissance (exposant 2.0)

**Correction tropicale :** mois `avoid` sur destinations `tropical=True` → normalisé dans la plage `mid`

### Emojis météo (`lib/common.py` → `js/core.js`)

Logique **burstiness** pour distinguer pluie tropicale vs pluie bloquante :

```
burstiness = precip_mm_day / (rain_pct / 100)
```

| Pattern | Condition | Emoji |
|---------|-----------|-------|
| `heavy_blocking` | rain ≥ 90% + precip ≥ 14mm/j | ⛈️ |
| `blocking` | rain ≥ 70% + (sun ≤ 7.5h ou precip ≥ 10mm + burstiness < 12) | 🌧️ |
| `tropical_showers` | rain ≥ 60% + precip ≥ 6mm + sun ≥ 9.5h + burstiness ≥ 10 | 🌦️ |
| `normal` | tout le reste | ☀️/🌤️/⛅/🌦️ selon temp+rain |

---

## Workflow de déploiement

```bash
# 1. Modifier scoring.py / core.js / lib/common.py

# 2. Régénérer les pages (5 langues)
for lang in fr en en-us es de; do python3 generate_pages.py --lang $lang; done

# 3. Si scores recalculés dans climate.csv → régénérer fiche-scores.js
python3 -c "
import csv, json
dests = list(csv.DictReader(open('data/destinations.csv', encoding='utf-8-sig')))
climate = list(csv.DictReader(open('data/climate.csv', encoding='utf-8-sig')))
slug_to_coord = {d['slug_fr']: f\"{float(d['lat']):.2f},{float(d['lon']):.2f}\" for d in dests}
scores = {}
for r in climate:
    coord = slug_to_coord.get(r['slug'])
    if not coord: continue
    mi = int(r['mois_num']) - 1
    scores.setdefault(coord, [None]*12)[mi] = round(float(r['score'])*10)
scores = {k:v for k,v in scores.items() if all(x is not None for x in v)}
open('js/fiche-scores.js','w').write(f'var FICHE_SCORES = {json.dumps(scores, separators=chr(44)+chr(58))};')
"

# 4. Vérification cohérence cross-surfaces (OBLIGATOIRE)
python3 check_deploy.py

# 5. Commit + push + deploy CF Workers
git add -A && git commit -m "..."
git push origin main
wrangler deploy
```

**`check_deploy.py`** vérifie : scoring CSV↔pages (5 cas), cohérence 5 langues, emojis Python (8 cas), pages annuelles 5 langues, version `core.min.js` sur 10 fichiers (index + app), couverture dew_point, monthly.json.

### Version JS

`CORE_JS_VERSION` dans `generate_pages.py` est la source de vérité. `_sync_core_version()` est appelée automatiquement à chaque génération et propage la version dans `index.html` et `*/app.html`.

**Ne jamais bumper manuellement** ces fichiers — toujours passer par `CORE_JS_VERSION`.

---

## Affiliés

| Partenaire | ID |
|------------|-----|
| GetYourGuide | `2MQKL00` |
| Travelpayouts | `708106` |
| Expedia | `camref=1110lB57J` + `creativeref=1100l68075` |

---

## SEO — État mars 2026

- **Titres** : 4 variants par page mensuelle, format question/insight/contraste
- **Descriptions** : soleil avant pluie, `rain_label` contextuel (tropical showers vs %), `sea_label`
- **Éditorial** : 33 600+ textes via `editorial.json` (clé : `{slug_fr}:{mois_num}:{lang}`)
- **Linking interne** : similar destinations top-5
- **Structured data** : Article + FAQPage + BreadcrumbList, publisher avec logo, `inLanguage`
- **Hreflang** : sur toutes les pages (5 langues + x-default)
- **Sitemaps** : 10 fichiers segmentés

---

## CI/CD

GitHub Actions — `.github/workflows/` :
- **Python Generators** : lint `generate_pages.py`, `scoring.py`, `lib/`
- **JS Syntax Check** : `node --check` sur tous les `.js`
- **Sitemap Coverage** : vérifie couverture sitemaps
- **HTML Validation** : échantillon pages
- **JS Minified Sync** : core.js → core.min.js cohérent
- **Scoring Consistency** : `tests/test_scoring.py` — `t_ideal()` Python↔JS, `raw_score()`, `FICHE_SCORES`↔climate.csv, `TROPICAL_KEYS`↔destinations.csv
