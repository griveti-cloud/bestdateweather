# Plan B : sortie du déclassement Google (octobre 2026)

Diagnostic complet : document de projet `claude/audit-seo-octobre-2026.md`.
Résumé : domaine créé le 20 février 2026, 50 000 pages publiées en 4 semaines,
puis rejet du site entier par Google (61 857 pages « Explorée, actuellement non
indexée », 7 pages indexées début octobre). Le plan B élague, assainit, puis gèle.

## Ce qui a été fait (8 octobre 2026)

| Phase | Changement | Fichiers |
|---|---|---|
| 1 | Avis « de Gilles » générés en série retirés ; seuls des avis réels, datés, seront affichés | `data/avis_reels.json`, `docs/avis_reels.md`, `lib/v6.py`, `lib/v6_adapter.py`, `lib/eeat.py` |
| 1 | Auteur JSON-LD : l'organisation, sauf avis réel de Gilles | `lib/v6_adapter.py` |
| 1 | Dates réelles : « Données mises à jour : août 2026 », dateModified et lastmod fixes | `data/data_version.json`, `lib/page_config.py` |
| 1 | Saisons inversées dans l'hémisphère sud, zone équatoriale sans saisons | `generate_pages.py` (context_paragraph) |
| 1 | « même si juillet reste théoriquement meilleur » sur la page de juillet supprimé | `generate_pages.py` |
| 1 | Pages US : « 25.0°F » (valeur en °C) corrigé | `lib/v6_adapter.py` |
| 1 | « L'été Paris » → « L'été à Paris » (préposition) | `lib/v6_adapter.py` |
| 1 | Pastilles climat calculées sur les données (fini « Pluies modérées » à Windhoek) | `lib/v6_adapter.py` |
| 1 | Titre des pages annuelles stable (il changeait à chaque régénération) | `lib/v6_adapter.py`, `locales/*.json` |
| 1 | Page « À propos » : section « Comment nos pages sont produites » (5 langues) | `a-propos.html`, `en/about.html`… |
| 2 | Ensemble indexable : 527 URL au lieu de 12 639 | `lib/indexation.py`, `data/indexation_policy.json`, `apply_indexation.py` |
| 2 | Sitemaps = exactement cet ensemble ; contrôle bloquant dans check_deploy | `generate_sitemaps.py`, `check_deploy.py` |
| 3 | Section « Semaine par semaine » (données ERA5 quotidiennes 2016-2025) | `lib/v6_weekly.py`, `scripts/fetch_weekly_history.py`, workflow quotidien |
| 4 | Garde-fou de gel : déploiement bloqué au-delà de 1 500 pages modifiées | `.github/workflows/deploy.yml` |
| + | IndexNow (Bing) à chaque déploiement | `scripts/indexnow_submit.py`, fichier clé à la racine |
| + | Bandeau du mois : déploiement automatique (il restait bloqué sur « Septembre ») | `.github/workflows/refresh-monthly-hub.yml` |
| + | `/en/`, `/us/`, `/es/`, `/de/` : redirection 301 au lieu de 307 | `_redirects` |

## Règles pendant le gel (3 à 6 mois)

- Pas de régénération massive. Corrections par petits lots.
- Toute nouvelle page indexable passe par `data/indexation_policy.json`.
- `data/data_version.json` ne change que si les données ou le contenu changent vraiment.
- Juger à la mise à jour principale de Google qui suit le déploiement : si moins
  de 50 pages indexées après celle-ci, passer à l'option C (nouveau domaine).

## Actions de Gilles

1. Search Console : resoumettre `sitemap-index.xml` ; supprimer les anciens
   sitemaps `sitemap-*-priority.xml` / `-secondary.xml` s'ils y figurent.
2. Search Console : « Sécurité et actions manuelles » doit afficher « Aucun problème ».
3. Bing Webmaster Tools : importer le site depuis la Search Console (2 minutes).
4. Écrire 20 à 30 avis réels dans `data/avis_reels.json` (format : `docs/avis_reels.md`).
5. Données structurées : `"foundingDate": "2024"` (À propos, accueil) alors que le
   domaine date de février 2026. Corriger si le projet n'existait pas en 2024.
6. Widgets : proposer l'intégration à des blogueurs voyage (modèle ci-dessous).

## Modèle de message aux blogueurs (widgets)

> Objet : un widget météo gratuit pour vos articles sur {destination}
>
> Bonjour {prénom},
>
> J'ai lu votre article sur {destination} ({lien}). Je développe
> BestDateWeather, un outil indépendant qui note chaque mois de l'année pour
> 754 destinations à partir de 10 ans de données climatiques (ERA5).
>
> J'ai préparé un petit widget gratuit, sans publicité ni traceur, qui affiche
> le score de {destination} mois par mois. Il s'intègre en une ligne :
> {code iframe depuis bestdateweather.com/integrer-widget}
>
> Si ça peut servir à vos lecteurs, il est à vous. Je reste disponible pour
> l'adapter à votre charte.
>
> Gilles, BestDateWeather
