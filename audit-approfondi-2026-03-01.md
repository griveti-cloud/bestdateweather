# Audit approfondi BestDateWeather — 1er mars 2026

**Périmètre** : données, SEO, UX, structures, maintenabilité, sécurité, performance
**Base** : 517 destinations, ~13 500 pages FR+EN, 7 générateurs Python, 1 app JS

---

## Synthèse par sévérité

| Sévérité | Trouvailles | Impact |
|----------|------------|--------|
| **P0 — Cassé** | 4 problèmes | SEO toxic, liens 404, données incohérentes |
| **P1 — Significatif** | 7 problèmes | SEO dégradé, scoring faux, contenu manquant |
| **P2 — Dette technique** | 7 problèmes | Maintenabilité, performance, sécurité |

---

## P0 — CRITIQUE (cassé en production)

### 1. Sitemap : ~6 200 URLs fantômes par langue

**Constat** : `sitemap-fr.xml` contient 10 600 entrées dont 6 217 pointent vers des fichiers inexistants. Idem pour `sitemap-en.xml`.

**Cause** : Le sitemap référence un ancien format d'URL pour les pages mensuelles :
- Sitemap : `meilleure-periode-agadir-en-janvier.html` ← **n'existe pas**
- Réel : `agadir-meteo-janvier.html` ← **existe**
- EN : `best-time-to-visit-agadir-in-january.html` ← **n'existe pas**
- Réel EN : `en/agadir-weather-january.html` ← **existe**

Les URLs correctes sont AUSSI dans le sitemap → chaque page mensuelle y figure deux fois (une bonne, une fantôme).

**Impact** : Google crawle ~6 200 soft 404 par langue. Budget crawl gaspillé, signaux négatifs Search Console, dilution d'indexation.

**Fix** : Supprimer toutes les entrées au format `meilleure-periode-*-en-*.html` et `best-time-to-visit-*-in-*.html` des sitemaps. Intégrer la génération du sitemap au pipeline `make all`.

---

### 2. Footer EN : 3 liens cassés sur TOUTES les pages anglaises (~6 700 pages)

**Constat** : Le footer des pages EN contient :
```
../legal-en.html    → fichier inexistant (réel : en/legal.html → lien correct serait legal.html)
../privacy-en.html  → fichier inexistant (réel : en/privacy.html → lien correct serait privacy.html)  
../contact.html     → pointe vers le contact FR (pas de version EN dédiée)
```

**Cause** : `generate_all_en.py` utilise `../` pour remonter de `en/` vers la racine, mais les noms de fichiers sont erronés (`legal-en.html` au lieu de `legal.html` dans `en/`).

De plus, `../methodology-en.html` fonctionne car `methodology-en.html` existe à la racine, mais c'est une architecture incohérente (certaines pages EN sont dans `en/`, d'autres à la racine).

**Fix** : Corriger les liens footer dans `generate_all_en.py` → `legal.html`, `privacy.html`, `contact.html` (relatifs à `en/`). Régénérer toutes les pages EN.

---

### 3. 32 incohérences score/classe dans climate.csv

**Constat** : Des scores sont hors de la plage autorisée par leur classe éditoriale :

| Destination | Mois | Classe | Score | Plage attendue |
|------------|-------|--------|-------|----------------|
| Louxor | Juin | avoid | 7.1 | 0.5–3.9 |
| Louxor | Juillet | avoid | 7.1 | 0.5–3.9 |
| Las Vegas | Juin | mid | 8.6 | 4.0–6.9 |
| Las Vegas | Juillet | mid | 8.3 | 4.0–6.9 |
| Marrakech | Juillet | mid | 8.2 | 4.0–6.9 |
| Marrakech | Août | mid | 8.3 | 4.0–6.9 |
| Dubai | Juillet-Sept | mid | 7.0–7.3 | 4.0–6.9 |
| Rajasthan | Mai | mid | 8.0 | 4.0–6.9 |
| Côte d'Azur | Février | rec | 6.1 | 7.0–10.0 |
| Goa | Juin | rec | 6.0 | 7.0–10.0 |
| + 22 autres | ... | ... | ... | ... |

**Impact** : Le tableau climatique affiche des couleurs (vert/orange/rouge) basées sur la classe, mais le score numérique contredit la couleur. Un utilisateur voit Louxor en juillet en rouge (avoid) avec un score de 7.1/10 (excellent).

**Fix** : Pour chaque incohérence, décider si c'est le score ou la classe qui est correct, puis aligner l'autre. Exécuter `python3 scoring.py` pour valider la cohérence post-correction.

---

### 4. 5 paires de destinations dupliquées (même slug EN)

**Constat** :

| Slug EN partagé | Destination FR 1 | Destination FR 2 |
|----------------|-----------------|-----------------|
| `da-nang` | da-nang | danang |
| `cusco` | cuzco | cusco |
| `cartagena` | cartagene | cartagena |
| `new-orleans` | nouvelle-orleans | la-nouvelle-orleans |
| `stone-town` | stone-town | zanzibar-ville |

**Impact** : Quand `generate_all_en.py` s'exécute, la seconde destination écrase la page EN de la première. Résultat : hreflang FR↔EN pointe potentiellement vers la mauvaise fiche FR. Google reçoit des signaux contradictoires.

**Fix** : Fusionner les doublons dans `destinations.csv` (garder un seul slug FR par slug EN) ou attribuer des slugs EN distincts (ex: `cartagena-spain` vs `cartagena-colombia`, qui est déjà partiellement fait avec `cartagena-colombia`).

---

## P1 — SIGNIFICATIF

### 5. TROPICAL_DESTINATIONS totalement désynchronisé

**Constat** : `scoring.py` définit 8 destinations tropicales hardcodées. `destinations.csv` a `tropical=True` sur **171 destinations**. Le code Python de correction tropicale (remonter avoid → plage mid) ne s'applique qu'aux 8 hardcodées.

**Impact** : 163 destinations marquées tropicales dans les données ne bénéficient pas de la correction de score. Leurs mois de mousson restent scorés sur la plage avoid (0.5–3.9) au lieu de la plage mid (4.0–6.9), ce qui donne des scores anormalement bas pour des destinations voyageables.

**Fix** : Remplacer le set hardcodé dans `scoring.py` par une lecture de la colonne `tropical` de `destinations.csv`. Régénérer les scores de toutes les destinations tropicales.

---

### 6. URL www inconsistante sur les redirects Zante

**Constat** : 13 pages de redirect (meilleure-periode-zante.html + 12 zante-meteo-*.html) utilisent `https://www.bestdateweather.com/` dans leurs canonicals. Toutes les autres pages (13 400+) utilisent `https://bestdateweather.com/` sans www.

**Impact** : Google peut voir deux versions du site, dilution de PageRank.

**Fix** : Retirer `www.` des canonicals dans les fichiers zante.

---

### 7. 3 rankings EN manquants

**Constat** :
| Page FR | Page EN |
|---------|---------|
| classement-destinations-meteo-2026.html | ✅ best-destinations-weather-ranking-2026.html |
| classement-destinations-europe-meteo-2026.html | ✅ best-europe-weather-ranking-2026.html |
| classement-destinations-meteo-ete-2026.html | ❌ Manquant |
| classement-destinations-meteo-hiver-2026.html | ❌ Manquant |
| classement-destinations-meteo-nomades-2026.html | ❌ Manquant |

**Impact** : Contenu à fort potentiel SEO non traduit. Les pages FR n'ont pas de hreflang EN correspondant.

**Fix** : Étendre `generate_classements.py` pour générer les 3 rankings manquants en EN.

---

### 8. monthly.json incomplet (71/517 destinations = 14%)

**Constat** : `data/monthly.json` ne contient que 71 destinations sur 517. Ce fichier semble servir de cache/API pour l'app interactive.

**Impact** : Si l'app utilise ce fichier pour des fonctionnalités, 86% des destinations n'y ont pas de données.

**Note** : `FICHE_SCORES` dans `core.js` couvre 489 destinations. Les 28 manquantes n'ont pas de score pré-calculé côté client.

---

### 9. Données orphelines dans climate.csv

**Constat** : Le slug `luxor` existe dans `climate.csv` (12 lignes de données) mais n'a pas de correspondance dans `destinations.csv` (qui utilise `louxor` comme slug_fr et `luxor` comme slug_en). Résultat : `meilleure-periode-luxor.html` est référencé dans le sitemap mais n'existe pas.

**Fix** : Supprimer les lignes `luxor` de `climate.csv` (les données `louxor` existent déjà). Retirer l'entrée du sitemap.

---

### 10. Pas de génération automatique du sitemap

**Constat** : Aucun des 7 générateurs Python ne produit les sitemaps. Les fichiers `sitemap-fr.xml` et `sitemap-en.xml` sont maintenus manuellement ou par des scripts ad-hoc (`generate_comparatifs.py` et `generate_piliers.py` y ajoutent des entrées, mais ne les régénèrent pas entièrement).

**Impact** : Toute modification du catalogue (ajout/suppression de destinations) nécessite un update manuel du sitemap, source d'erreurs (cf. P0-1).

**Fix** : Ajouter une étape `sitemap` dans le Makefile qui régénère les deux sitemaps à partir des fichiers HTML réellement présents sur le disque.

---

### 11. Architecture EN incohérente (fichiers éparpillés)

**Constat** : Les pages EN sont réparties entre deux emplacements sans logique claire :
- `en/` : pages destination, legal, privacy, contact, app, pillar, comparison
- Racine : `methodology-en.html`
- `en/methodology.html` : redirect vers `../methodology-en.html`

Le footer EN utilise `../methodology-en.html` (racine) mais `legal.html` (dans en/). Le vercel.json redirige `/en/` vers `/en/app.html`.

**Impact** : Maintenance difficile, erreurs de chemins relatifs (cf. P0-2).

---

## P2 — DETTE TECHNIQUE

### 12. Duplication massive FR/EN des générateurs

**Constat** : `generate_all.py` (1401 lignes) et `generate_all_en.py` (1323 lignes) partagent ~60% de logique. 1759 lignes de diff, mais beaucoup ne sont que des traductions de chaînes.

**Impact** : Tout changement de structure (template, scoring, sections) doit être appliqué deux fois. Source de désynchronisation.

**Amélioration** : Extraire templates et logique dans `lib/common.py` (déjà commencé avec les fonctions partagées). Un seul générateur paramétré par langue.

---

### 13. 96 inline styles dans le générateur

**Constat** : `generate_all.py` contient 96 occurrences de `style=`. Les templates HTML embarquent du CSS inline au lieu d'utiliser des classes CSS.

**Impact** : Toute modification de style requiert un changement dans le Python + régénération de toutes les pages.

---

### 14. UTF-8 BOM sur tous les fichiers générés

**Constat** : Les fichiers sont écrits avec `encoding='utf-8-sig'` (BOM). Non standard pour le web, peut causer des problèmes d'interprétation avec certains parseurs.

**Fix** : Remplacer `utf-8-sig` par `utf-8` dans les `open(..., 'w')` des générateurs. Garder `utf-8-sig` uniquement en lecture des CSV (Excel).

---

### 15. Index.html : 210 KB sans lazy loading

**Constat** : La page d'accueil (app interactive) pèse 210 KB de HTML, dont 16 KB de CSS inline et 3.5 KB de JS inline. Le `FICHE_SCORES` dans core.js ajoute ~100 KB de JSON brut.

**Impact** : Time to First Contentful Paint dégradé sur mobile.

**Pistes** : Charger FICHE_SCORES en async, externaliser le CSS inline critique.

---

### 16. Pas de Content-Security-Policy

**Constat** : `vercel.json` définit HSTS, X-Frame-Options, X-Content-Type-Options mais aucun CSP.

**Impact** : Vulnérabilité aux injections XSS si du contenu utilisateur est jamais rendu.

---

### 17. PWA : screenshot-mobile.png manquant

**Constat** : `manifest.json` référence `screenshot-mobile.png` qui n'existe pas sur le disque.

**Impact** : L'install prompt PWA ne montre pas de preview sur Android.

---

### 18. Pages statiques manquantes

**Constat** : Aucune page "À propos" (ni FR ni EN). La page `confidentialite.html` existe mais n'a pas de pendant EN dédié (sitemap EN référence `en/privacy.html` qui existe). Pas de page FAQ standalone.

---

## Matrice de priorisation

| # | Fix | Effort | Impact SEO | Impact UX |
|---|-----|--------|-----------|-----------|
| 1 | Nettoyer sitemaps | 1h | 🔴 Critique | - |
| 2 | Footer EN | 30min + regen | 🔴 Critique | 🔴 Liens cassés |
| 3 | Score/classe | 2h data | 🟡 Moyen | 🔴 Données fausses |
| 4 | Doublons slugs | 1h data | 🔴 hreflang | 🟡 |
| 5 | Tropical sync | 1h code + regen | - | 🔴 Scores faux |
| 6 | WWW zante | 15min | 🟡 | - |
| 7 | Rankings EN | 2h | 🟡 | 🟡 |
| 8 | monthly.json | 1h | - | 🟡 |
| 9 | Orphan luxor | 15min | 🟡 | - |
| 10 | Sitemap auto | 3h | 🟢 Prévention | - |
| 11 | Archi EN | 4h+ | 🟡 | 🟡 |
| 12-18 | Dette tech | Variable | 🟢 | 🟢 |

**Ordre suggéré** : 1 → 2 → 4 → 6 → 9 (rapides, impact immédiat) → 3 → 5 (données) → 10 → 7 → reste.
