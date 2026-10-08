# Dépôt sur data.gouv.fr : fiche à copier-coller

## Étape 1 : compte

En haut à droite : **S'enregistrer**. Confirmer l'adresse e-mail reçue.

## Étape 2 : organisation BestDateWeather (recommandé)

**Publier sur data.gouv.fr** (en haut à droite) → **Une organisation**.
Vérifier d'abord qu'elle n'existe pas déjà (recherche « BestDateWeather »).

| Champ | À saisir |
|---|---|
| Nom | BestDateWeather |
| Acronyme | (vide) |
| Numéro SIRET | Le SIRET à 14 chiffres de l'entreprise individuelle (annuaire-entreprises.data.gouv.fr si besoin) |
| Description | Voir ci-dessous |
| Site Internet | https://bestdateweather.com |
| Logo | logo-bestdateweather.png |

Description de l'organisation :

> BestDateWeather est un outil gratuit et indépendant d'aide au choix des dates de voyage. Il note chaque mois de l'année pour 754 destinations à partir de dix ans de données climatiques (réanalyse ERA5, Copernicus / ECMWF). Édité par une entreprise individuelle basée à Chatou (Yvelines). Contact : contact@bestdateweather.com

## Étape 3 : jeu de données

**Publier sur data.gouv.fr** → **Un jeu de données** → choisir l'organisation BestDateWeather comme producteur.

| Champ | À saisir |
|---|---|
| Titre | Climat de voyage : normales mensuelles et score pour 730 destinations dans le monde |
| Sigle | (vide) |
| Licence | Creative Commons Attribution (CC BY) |
| Fréquence de mise à jour | Annuelle si tu comptes ajouter chaque année la dernière année complète ; sinon Ponctuelle |
| Couverture temporelle | du 01/01/2016 au 31/12/2025 |
| Granularité spatiale | La valeur la plus fine proposée qui corresponde à « point / ville » ; à défaut « Autre » |
| Mots clés | climat, tourisme, voyage, météo, normales climatiques, era5, copernicus |
| Mode brouillon | Activé pendant la saisie, désactivé à la fin |

Description (le champ accepte la mise en forme simple) :

> Pour chaque destination et chaque mois : température maximale et minimale moyennes (°C), part des jours avec au moins 1 mm de pluie (%), précipitations moyennes (mm par jour), ensoleillement (heures par jour), température de la mer (°C, destinations côtières) et score de voyage sur 10.
>
> **Sources** : réanalyse ERA5 (Copernicus / ECMWF) via Open-Meteo, données quotidiennes 2016-2025. Ensoleillement : normales de stations quand elles existent (colonne source_soleil = observed), sinon valeur ERA5 recalibrée (calibrated).
>
> **Méthode du score** : https://bestdateweather.com/methodologie
>
> **Limites** : une destination « région » est représentée par un seul point (colonne precision_point) ; en zone tropicale, la réanalyse peut surestimer la fréquence des petites pluies par rapport aux stations. La Réunion et la Corse sont exclues de cette version (point de référence en altitude, en cours de correction).
>
> **Citation demandée** : « Source : BestDateWeather (bestdateweather.com), d'après ERA5 / Copernicus et Open-Meteo ».
>
> Contact : contact@bestdateweather.com

## Étape 4 : fichiers (« Ajoutez vos ressources »)

| Fichier | Mode | Titre de la ressource | Type |
|---|---|---|---|
| bestdateweather-climat-voyage.csv | Téléverser depuis l'ordinateur | Climat de voyage, 730 destinations, 12 mois (CSV) | Fichier principal |
| LISEZMOI.md | Téléverser depuis l'ordinateur | Documentation : colonnes, sources, limites, licence | Documentation |

Puis désactiver le **mode brouillon** et publier.

## Étape 5 : déclarer le site comme réutilisation

Depuis la page du jeu de données publié : bouton de réutilisation, ou
**Publier sur data.gouv.fr** → **Une réutilisation**.

| Champ | À saisir |
|---|---|
| Titre | Carte mondiale du climat de voyage : le meilleur mois pour 754 destinations |
| URL | https://bestdateweather.com/carte |
| Type | Visualisation |
| Description | Carte interactive qui classe 754 destinations selon leur score climatique de voyage, mois par mois, avec filtres de sécurité et de budget. Construite à partir de ce jeu de données (ERA5 2016-2025). Chaque destination renvoie vers une fiche détaillée. |
| Mots clés | voyage, climat, carte, tourisme |
| Jeux de données associés | Le jeu de données de l'étape 3 (associé par défaut) |
| Image | capture-carte.png |

## Étape 6 : renvoyer l'adresse du jeu de données

Une fois publié, me donner l'URL : je l'ajoute sur la page Méthodologie, dans
le LISEZMOI et dans le communiqué « Noël au soleil ».
