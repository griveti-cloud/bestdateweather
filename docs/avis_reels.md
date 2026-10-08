# Avis réels de Gilles (data/avis_reels.json)

Depuis le plan B (octobre 2026), le bloc « L'avis de Gilles » n'apparaît que
pour une destination **réellement visitée**. Les 3 774 textes générés en série
(`data/avis_annuel.json`, avril-mai 2026) ne sont plus affichés : ils
présentaient comme une expérience personnelle des préférences sur 754
destinations, et leurs scores contredisaient souvent ceux de la page.

## Format

Une entrée par destination et par langue, clé `slug_fr:langue`
(`fr`, `en`, `en-us`, `es`, `de`). Pas de repli d'une langue vers une autre.

```json
{
  "lisbonne:fr": {
    "html": "Texte de l'avis. <strong>Gras</strong> autorisé.",
    "visite": "mai 2024"
  },
  "lisbonne:en": {
    "html": "Review text.",
    "visite": "May 2024"
  }
}
```

`visite` est obligatoire : la page affiche « (Visité en mai 2024) » et la page
« À propos » promet la date du voyage.

## Règles

1. Uniquement des lieux où tu es allé. Pas d'avis « de bureau ».
2. Ce que tu as vu et vécu : un détail concret par avis (un quartier, une
   averse, une chaleur, une foule, un prix) vaut mieux qu'un résumé du climat.
3. Si tu cites un score, prends celui de la page le jour où tu écris ; la
   cohérence est vérifiée à la régénération (les scores peuvent bouger).
4. Les règles de style de `docs/regles_avis_annuels.md` restent valables.
5. Une photo personnelle peut remplacer la photo Unsplash : à prévoir.

## Effet sur la page

- Bloc « L'avis de Gilles » affiché sur la page annuelle de cette langue, et
  un extrait sur les pages mensuelles.
- Le balisage Article de la page déclare alors Gilles comme auteur ; sinon
  l'auteur est l'organisation BestDateWeather.
