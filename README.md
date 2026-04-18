# BestDateWeather

Plateforme météo et voyage — données climatiques ERA5 et scores pour **746 destinations** mondiales en **5 langues** (FR, EN, EN-US, ES, DE).

**Site** : [bestdateweather.com](https://bestdateweather.com)  
**Pages générées** : ~45 700 HTML statiques  
**Dernière mise à jour** : avril 2026  
**Hébergement** : Cloudflare Workers Assets (`bestdateweather-prod`)

---

## Chiffres clés

| Type | FR | EN | ES | DE | US |
|------|----|----|----|----|-----|
| Pages mensuelles | 8 340 | 8 340 | 8 340 | 8 340 | 8 340 |
| Pages annuelles | 746 | 746 | 746 | 746 | 746 |
| Comparatifs | 50 | 50 | 50 | 50 | 50 |
| Piliers mensuels | 12 | 12 | 12 | 12 | — |

**Éditorial** : `data/editorial.json` — 33 600+ textes différenciants par destination/mois/langue  
**Destinations** : 746 · **Paires comparatifs** : 50

---

## Architecture des fichiers

```
index.html                          # Hub FR (app météo interactive)
en/
  app.html                          # Hub EN
  {slug}-weather-{month}.html       # Pages mensuelles EN (746 × 12)
  best-time-to-visit-{slug}.html    # Pages annuelles EN (746)
  best-*.html                       # Classements EN
  {slug}-vs-{slug}-weather.html     # Comparatifs EN (50)
  where-to-go-in-{month}.html       # Piliers mensuels EN (12)
es/ de/ us/                         # Idem pour ES, DE, US
{slug}-meteo-{month}.html           # Pages mensuelles FR (746 × 12)
meilleure-periode-{slug}.html       # Pages annuelles FR (746)
ou-partir-en-{month}.html           # Piliers mensuels FR (12)
{slug}-ou-{slug}-climat.html        # Comparatifs FR (50)
meilleures-destinations-meteo.html  # Hub annuel FR

js/
  core.js                           # Logique app (scoring, API, rendu) — SOURCE
  core.min.js                       # Minifié via terser (?v=64)
  weather-banner-2.js               # Bandeau météo live + autocomplete — SOURCE
  weather-banner-2.min.js           # Minifié (?v=18)
  fiche-slugs.js / fiche-slugs.min.js  # Autocomplete : alias → slugs 5 langues
  fiche-scores.js                   # Scores précalculés par coord lat/lon (746 dest × 12 mois)
  dest-search.js                    # Recherche destinations (?v=7)
  favs.min.js                       # Favoris (?v=1)

locales/
  fr.json / en.json / en-us.json / es.json / de.json

data/
  destinations.csv                  # 746 destinations (slugs, coords, pays, flags, tropical…)
  climate.csv                       # Données climatiques ERA5 (score, tmin, tmax, rain, sun, sea_temp, dew_point_mean…)
  monthly.json                      # Données résumées par coord pour app annuelle
  editorial.json                    # 33 600+ textes éditoriaux — clé : {slug_fr}:{mois_num}:{lang}
  country_info.json                 # Par pays : currency, drive, languages, risk_level, budget_index

lib/
  common.py                         # Composants HTML partagés, scoring helpers, decision_card_html…
  page_config.py                    # Chargement locales, build_config, utilitaires

scoring.py                          # Algorithme de score — source de vérité Python
check_deploy.py                     # Vérification cohérence cross-surfaces (lancer avant chaque push)
worker-assets.js                    # CF Worker : routing, proxies JSON, subscribe, advisories
wrangler.toml                       # Config Cloudflare Workers
```

---

## Générateurs

| Script | Rôle |
|--------|------|
| `generate_pages.py` | Pages mensuelles + annuelles (746 dest × 12 mois × 5 langues) |
| `generate_piliers.py` | Piliers mensuels + hubs annuels (5 langues) |
| `generate_classements.py` | Pages classements thématiques (5 langues) |
| `generate_comparatifs.py` | Pages comparatifs X vs Y (50 paires × 5 langues) |
| `generate_index_hub.py` | Injection hubs destinations dans app.html / index.html |
| `generate_sitemaps.py` | Sitemaps segmentés (10 fichiers) |

---

## Données climatiques

- **Source** : Open-Meteo (ERA5) — moyennes sur 10 ans (2015–2024)
- **Méthode** : mean sur 10 ans. `precip_mm` en mean intentionnel (P50 → 0 sur mois secs)
- **Dew point** : `dew_point_mean` dans `climate.csv` (ERA5 `dew_point_2m_mean`)
- **Température mer** : `sea_temp` dans `climate.csv`

---

## Scoring

### Modèle (`scoring.py` → `core.js`)

```
raw_score = 0.40 × t_ideal(tmax)
          + 0.35 × (1 - effective_rain/100)
          + 0.25 × min(1, sun_h/15)
          - dew_point_penalty(tmax, dew_point)
```

**Courbe thermique `t_ideal(tmax)` :**

| Plage | Valeur |
|-------|--------|
| ≤ 5°C | 0.00 |
| 5 → 14°C | 0.00 → 0.30 |
| 14 → 22°C | 0.30 → 0.80 |
| 22 → 28°C | 0.80 → 1.00 (optimum) |
| 28 → 31°C | 1.00 → 0.90 |
| 31 → 34°C | 0.90 → 0.60 |
| 34 → 37°C | 0.60 → 0.25 |
| 37 → 40°C | 0.25 → 0.05 |
| > 40°C | 0.00 |

**Caps de classe (`effective_classe`) :**
- `tmax ≥ 38°C` → classe `avoid`
- `tmax ≥ 34°C + rec` → `mid`
- `tmax ≥ 30°C + dew ≥ 16°C + rec` → `mid`
- `tmax ≥ 26°C + dew ≥ 22°C + rec` → `mid` *(chaleur humide tropicale)*

**Pénalité humidité :** max −0.20 pts si `tmax ≥ 26°C + dew ≥ 16°C`

**Plages par classe :** `avoid` 0.5–3.9 · `mid` 4.0–6.9 · `rec` 7.0–10.0  
**Normalisation :** percentiles globaux (p5–p95) + courbe puissance (exposant 2.0)  
**Correction tropicale :** mois `avoid` sur `tropical=True` → normalisé dans plage `mid`

### Légende des classes

| Classe | Label FR | Label EN |
|--------|----------|----------|
| `rec` | Meilleure période | Best period |
| `mid` | Période correcte | Decent period |
| `avoid` | Moins favorable | Less favorable |

### Ressenti thermique (6 niveaux)

| Niveau | FR | Condition |
|--------|----|-----------|
| 🟣 Froid | Froid | Tmax < 0°C |
| 🔵 Frais | Frais | Dew < 16°C + Tmax < 20°C |
| 🟢 Confortable | Confortable | Dew < 18°C + Tmax ≤ 32°C |
| 🟠 Lourd | Lourd | Dew ≤ 22°C + Tmax ≤ 38°C |
| 🔴 Chaleur humide | Chaleur humide | Dew > 22°C (tropical humide) |
| 🔴 Très chaud | Très chaud | Dew ≤ 22°C + Tmax > 38°C |

---

## Sécurité (advisory)

- **Source** : Auswärtiges Amt (DE) — API temps-réel, cache 6h via CF Worker
- **Stockage** : `data/country_info.json` (champ `risk_level` 1–4)
- **Surfaces** : pages destination, classements, piliers

## Budget

- **Source** : Numbeo Cost of Living Index 2026
- **Seuils** : `[30, 48, 65, 82]` — 14 destinations-étalon + 21 proxies régionaux
- **Labels** : Économique / Abordable / Intermédiaire / Coûteux / Très coûteux

---

## Workflow de déploiement

```bash
# 1. Modifier scoring.py / lib/ / locales/ / core.js

# 2. Régénérer les pages (5 langues)
for lang in fr en en-us es de; do python3 generate_pages.py --lang $lang; done

# 3. Si JS modifié : minifier + bumper version
npx terser js/core.js -o js/core.min.js --compress --mangle
# Bumper CORE_JS_VERSION dans generate_pages.py → relancer génération

# 4. Régénérer les hubs (OBLIGATOIRE si app.css ou template modifié)
python3 generate_index_hub.py
# ⚠️  RÈGLE : à chaque bump de version app.css → relancer generate_index_hub.py
# Sans ça, les hubs référencent l'ancienne version CSS → régression fond clair

# 5. Régénérer comparatifs + classements si locales ou scoring modifiés
python3 generate_comparatifs.py
python3 generate_classements.py

# 6. Vérification cohérence (OBLIGATOIRE)
python3 check_deploy.py

# 7. Commit + push → GitHub Actions → wrangler deploy (auto)
git add -A && git commit -m "..."
git push origin main
```

**CI/CD** : GitHub Actions → `wrangler deploy` automatique sur push `main`.  
**`check_deploy.py`** vérifie : scoring CSV↔pages, cohérence 5 langues, version core.min.js, dew_point, monthly.json.

> **Piège récurrent** : oublier `generate_index_hub.py` après un bump CSS provoque une régression du fond sombre sur les hubs (app.css versionné, les hubs pointent vers l'ancienne version).

### Versions JS actives

| Fichier | Version |
|---------|---------|
| `core.min.js` | ?v=64 |
| `weather-banner-2.min.js` | ?v=18 |
| `dest-search.js` | ?v=7 |
| `favs.min.js` | ?v=1 |
| `app.css` | ?v=51 |
| `style.css` | ?v=14 |

---

## Affiliés

| Partenaire | ID |
|------------|-----|
| GetYourGuide | `2MQKL00` |
| Travelpayouts | `708106` |
| Expedia | `camref=1110lB57J` |

---

## SEO

- **Titres** : 4 variants par page mensuelle
- **Éditorial** : 33 600+ textes via `editorial.json`
- **Structured data** : Article + FAQPage + BreadcrumbList
- **Hreflang** : 5 langues + x-default sur toutes les pages
- **Sitemaps** : 10 fichiers segmentés

---

## ⚠️ Actions en attente

- [ ] Repo GitHub → passer en **privé** (clés API dans l'historique git)
- [ ] Révoquer clé Anthropic `sk-ant-api03-E6oWt...`
- [ ] Révoquer clé PSI `AIzaSyD9xeMh...`
- [ ] PSI manuel sur pagespeed.web.dev (autres langues)
- [ ] ~251 destinations sans photo Unsplash
- [ ] Vérifier secret `BREVO_API_KEY` dans CF Workers dashboard
- [ ] 12 testeurs Android Play Store (fenêtre 14j)
- [ ] Hotels.com via Travelpayouts (pending approbation)
- [ ] **Backlinks SEO en cours** (avril 2026) : 15 blogs contactés (widgets), 9 médias pitchés (Digital PR angle "124 destinations pires en été"), 3 tourism boards, Wikipedia en cours
