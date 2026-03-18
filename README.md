# BestDateWeather

Plateforme météo et voyage — données climatiques ERA5 et scores pour **699 destinations** mondiales en **5 langues** (FR, EN, EN-US, ES, DE).

**Site** : [bestdateweather.com](https://bestdateweather.com)  
**Pages générées** : ~45 700 HTML statiques  
**Dernière mise à jour** : mars 2026  
**Hébergement** : Netlify (deploy auto sur push `main`)

---

## Chiffres clés

| Type | FR | EN | ES | DE | US |
|------|----|----|----|----|-----|
| Pages mensuelles | 8 370 | 8 372 | 8 367 | 8 371 | 8 372 |
| Pages annuelles | 699 | 700 | 699 | 699 | 699 |
| Comparatifs | 53 | 53 | 53 | 53 | 53 |
| Piliers mensuels | 12 | 12 | 12 | 12 | — |

**Éditorial** : `data/editorial.json` — 33 600+ textes différenciants par destination/mois/langue  
**Destinations** : 699 · **Paires comparatifs** : 53

---

## Architecture des fichiers

```
index.html                          # Hub FR (app météo interactive)
en/
  app.html                          # Hub EN
  {slug}-weather-{month}.html       # Pages mensuelles EN (699 × 12)
  best-time-to-visit-{slug}.html    # Pages annuelles EN (699)
  best-*.html                       # Classements EN
  {slug}-vs-{slug}-weather.html     # Comparatifs EN (53)
  where-to-go-in-{month}.html       # Piliers mensuels EN (12)
es/ de/ us/                         # Idem pour ES, DE, US
{slug}-meteo-{month}.html           # Pages mensuelles FR (699 × 12)
meilleure-periode-{slug}.html       # Pages annuelles FR (699)
ou-partir-en-{month}.html           # Piliers mensuels FR (12)
{slug}-ou-{slug}-climat.html        # Comparatifs FR (53)
meilleures-destinations-meteo.html  # Hub annuel FR

js/
  core.js                           # Logique app (scoring, API, rendu) — SOURCE
  core.min.js                       # Minifié via terser (?v=13)
  weather-banner-2.js               # Bandeau météo live + autocomplete — SOURCE
  weather-banner-2.min.js           # Minifié via terser — FICHIER SERVI EN PROD
  fiche-slugs.js                    # Autocomplete : alias → {fr, en, es, de} — SOURCE
  fiche-slugs.min.js                # Minifié via terser

locales/
  fr.json                           # Textes FR générateurs (référence)
  en.json / en-us.json
  es.json / de.json

data/
  destinations.csv                  # 699 destinations (slugs, coords, pays, flags…)
  climate.csv                       # Données climatiques mensuelles ERA5 (score, tmin, tmax, rain, sun, sea_temp…)
  editorial.json                    # 33 600+ textes éditoriaux par destination/mois/langue
  overrides.csv                     # Overrides manuels scoring

lib/
  common.py                         # Composants HTML partagés, score_badge, fill_tpl, footer
  page_config.py                    # Chargement locales, build_config, utilitaires

netlify/
  edge-functions/
    regex-redirects.js              # 2 patterns regex FR/EN (non supportés par _redirects)
```

---

## Générateurs

| Script | Rôle |
|--------|------|
| `generate_pages.py` | Pages mensuelles + annuelles (699 dest × 12 mois × 5 langues) |
| `generate_piliers.py` | Piliers mensuels + hubs annuels (5 langues) |
| `generate_classements.py` | Pages classements thématiques (5 langues) |
| `generate_comparatifs.py` | Pages comparatifs X vs Y (53 paires × 5 langues) |
| `generate_index_hub.py` | Injection SILO 1 dans app.html / index.html |
| `generate_sitemaps.py` | Sitemaps segmentés (10 fichiers) |

---

## Données climatiques

- **Source** : Open-Meteo (ERA5/ECMWF) — moyennes sur 10 ans
- **Méthode** : moyenne (mean) sur 10 ans. `precip_mm` en mean intentionnel (P50 → 0 sur mois secs)
- **Température mer** : `sea_temp` dans `climate.csv`, affiché dans les descriptions si disponible
- **Scoring** : algorithme propriétaire (tmax, rain_pct, sun_h, sea_temp, classe) — détails non publiés

---

## Déploiement

```bash
# Régénérer une destination (toutes langues)
python3 generate_pages.py --lang fr paris
python3 generate_pages.py --lang en paris

# Régénérer tous les piliers
python3 generate_piliers.py

# Régénérer les comparatifs
python3 generate_comparatifs.py

# Minifier JS après modification
npx terser js/core.js --compress --mangle -o js/core.min.js
# Bumper le cache-bust ?v=N dans les templates

# Push → deploy Netlify automatique
git push origin main
```

---

## Affiliés

| Partenaire | ID |
|------------|-----|
| GetYourGuide | `2MQKL00` |
| Travelpayouts | `708106` |
| Booking.com (CJ Affiliate) | PID 101696591 |

---

## SEO — État mars 2026

- **Titres** : 4 variants par page mensuelle, format question/insight/contraste
- **Descriptions** : soleil avant pluie, `rain_label` contextuel (tropical showers vs %), `sea_label`
- **Éditorial** : 100+ destinations enrichies via `editorial.json` (textes différenciants par mois/langue)
- **Linking interne** : similar destinations top-5 (était top-3)
- **Structured data** : Article + FAQPage + BreadcrumbList, publisher avec logo, `inLanguage`
- **Hreflang** : sur toutes les pages (5 langues + x-default)
- **Sitemaps** : 10 fichiers segmentés (FR/EN/ES/DE/US × priority/secondary)
