# V6 — Scoping industrialisation generate_pages.py

> Document de travail. Phase 1 du plan de rollout V6.
> Audit fait : **30 avr 2026**.
> Décisions stratégiques : **30 avr 2026**.

## 0. Décisions stratégiques (verrouillées)

| Question | Décision |
|---|---|
| **Périmètre rollout** | Bloquer V6 tant que les 4 langues ne sont pas prêtes (rédaction ~3000 éditos d'abord) |
| **Pilote post-GSC** | Tout FR d'un coup (754 fiches), 1 semaine après prep — mais subordonné au multilangue |
| **Stratégie GSC pendant rédaction (mai-juin)** | Option 2 — tout figer en V5, déployer V6 multilangue d'un coup (1 seule perturbation GSC) |
| **Rédaction des 3000 éditos EN/EN-US/ES/DE** | Claude rédige avec traduction idiomatique (pas mot-à-mot), spot-check 10% par Gilles, validation par batches de 50 |
| **Architecture refactor** | À VALIDER (Option A in-place vs B fork) |

## 0.1 Garde-fous rédaction multilangue

- EN-UK : registre voyage premium, vocabulaire britannique
- EN-US : températures °F par défaut, dates US format, vocabulaire américain
- ES : tutoiement (registre voyage hispanique)
- DE : registre à valider (Sie/Du selon style site)
- Test pattern-LLM automatique après chaque batch (`incontournable`/`inoubliable`/`découvrez` < 2%)
- Refus de générer si donnée manquante → "non confirmé" plutôt qu'inventer
- Cadence cible : ~150 éditos/jour à 2000 chars qualité maintenue = 5 jours par langue

## 1. État des lieux factuel

### 1.1 Couverture éditos
| Type | Total | FR | EN | EN-US | ES | DE |
|---|---|---|---|---|---|---|
| Mountain | 111 | 111 (100%) | 0 | 0 | 0 | 0 |
| Coastal | 419 | 419 (100%) | 0 | 0 | 0 | 0 |
| Tropical | 224 | 224 (100%) | 0 | 0 | 0 | 0 |
| **Total** | **754** | **754** | **0** | **0** | **0** | **0** |

**→ Pour V6 multilangue : ~3000 éditos à rédiger (754 × 4 langues manquantes).**

### 1.2 Qualité éditos FR
- Longueur : 750-4969 chars (moy 2138)
- Patterns LLM-typés : 1.5% (`incontournable` 9× / `inoubliable` 2×) — sain
- Aucun édito < 200 chars
- 0 incohérence détectée vs scoring V6 sur 643 non-mountain
- 1 incohérence corrigée sur mountain (Chamonix Octobre)

**→ Base FR exploitable telle quelle pour V6.**

### 1.3 Comparaison V5 vs V6
| Métrique | V5 | V6 | Delta |
|---|---|---|---|
| Lignes HTML | 255 | 685 | +430 (+169%) |
| Sections | 5 | 10 | +5 |
| CSS file | app.css 53 KB | v6.css 35 KB | nouveau |
| Trend chart | non | oui | nouveau |
| Méthodologie | dans card_decision | sub-cards distincts | nouveau |
| Infos pratiques | inline rapide | grid-3 box adaptatives | nouveau |
| Footer | dark navy | dark navy (aligné) | identique post-fix |

## 2. Refactor generate_pages.py — sections à modifier

### 2.1 Architecture cible
**Option A** — refactor in-place : modifier `gen_annual()` (ligne 562, ~1000 lignes) pour produire HTML V6.
- Risque : régression V5 sur les 35k pages existantes
- Bénéfice : un seul code path

**Option B** — fork dédié : créer `gen_annual_v6()` + flag `--v6` dans la CLI.
- Risque : code dupliqué, divergence à terme
- Bénéfice : zéro risque sur PROD V5, rollback instantané

**Recommandation (certitude HAUTE)** : Option B pour la phase pilote (mountain FR), puis Option A après validation 4 semaines GSC.

### 2.2 Helpers V6 à créer dans lib/common.py

```python
# Nouvelles fonctions à coder
def render_v6_topbar(slug, lang) -> str:
    """Brand + ♡ + share + CTA Planifier"""

def render_v6_decision_card(slug, lang, months_data, scores, mountain) -> str:
    """Hero shell sombre avec dual ski/rando si mountain, single sinon"""

def render_v6_methodology_block(lang, mountain) -> str:
    """Sub-cards dual ski/rando si mountain, single sinon"""

def render_v6_trend_chart(slug, lang, lat, lon) -> str:
    """SVG 800x360 burgundy avec annotations italiques"""

def render_v6_infos_pratiques(slug, lang, country, mountain, coastal, tropical, nomade) -> str:
    """grid-3 adaptatif :
    - mountain: Pays / Climat / Séjour montagne (altitudes, saisons)
    - coastal: Pays / Climat / Séjour balnéaire (mer, plages, houle)
    - tropical: Pays / Climat / Séjour tropical (saisons sèche/humide, cyclones, mer)
    - nomade: Pays / Climat / Séjour nomade (visa, internet, coût, saison)
    - default: Pays / Climat / Séjour citadin (UNESCO, transport, visa)
    """

def render_v6_footer(slug, lang) -> str:
    """Dark navy + langs single-line"""
```

**Estimation dev** : ~3 jours (avec tests).

### 2.3 Données nouvelles requises

| Donnée | Source | Statut |
|---|---|---|
| `flag` 2x retina | `flags/2x/*.png` | ✅ existe (PROD V5 utilise déjà) |
| `country_info` enrichi (UNESCO, transport) | nouveau | ❌ à créer pour ~190 pays |
| Profils par destination (citadin/balnéaire/nomade) | nouveau | ❌ à dériver de mountain/coastal/tropical/nomade |
| Climate trend coord-fix | `data/climate_trend.json` | ⚠️ schéma double 458 slugs + 158 coords (lib/common.py gère) |
| Edito synchro avis_annuel | `data/avis_annuel.json` | ✅ 754 FR, fallback texte si lang manquante |

### 2.4 i18n — chaînes nouvelles
Sections nouvelles V6 nécessitant des labels traduits :
- Méthodologie (titre, intro, "Score ski"/"Score rando", "Méthodologie complète →") : ~10 chaînes
- Trend chart (titre, légende, annotation pic décennie, "+X°C/décennie") : ~6 chaînes
- Infos pratiques box headers + signal-hints tooltips : ~50 chaînes
- Topbar boutons aria-label + share : ~5 chaînes
- Footer aucun changement

**→ ~70 chaînes × 4 langues (EN/EN-US/ES/DE) = 280 traductions à ajouter dans `locales/*.json`.**

## 3. Tests

### 3.1 À étendre dans tests/test_scoring.py
- ✅ Mountain max(ski, rando) sur 111 dest (déjà fait)
- ❌ Test V6 helpers : produisent HTML valide (BeautifulSoup parse)
- ❌ Test V6 Box 3 adaptative : mountain → "Séjour montagne", coastal → "Séjour balnéaire", etc.
- ❌ Test V6 footer : tous les liens i18n présents

### 3.2 Tests visuels (manuels)
- Chamonix V6 (mountain) → validé
- 1 destination par profil à valider visuellement après refactor :
  - mountain : Chamonix
  - coastal : Nice ou Biarritz
  - tropical : Bali
  - nomade : Lisbonne ou Bali (a deux profils)
  - citadin : Paris ou Lyon

## 4. Plan séquentiel verrouillé (révisé après décisions)

### Mai 2026 — préparation code + EN
- **Sem 1** : helpers V6 dans `lib/common.py` + `gen_annual_v6()` (selon arch A/B à décider)
- **Sem 2** : tests étendus + validation locale 5 protos (Chamonix/Paris/Lyon/Bali/Reykjavik)
- **Sem 3-4** : rédaction 754 éditos EN-UK (cadence 150/j × 5j = 1 batch)

### Juin 2026 — rédaction ES + DE + EN-US
- **Sem 1-2** : rédaction 754 éditos ES (5j) + 754 éditos DE (5j)
- **Sem 3** : rédaction 754 éditos EN-US (dérivable d'EN avec adaptations °F/dates/vocab US)
- **Sem 4** : staging full Cloudflare + validation visuelle 5 langues × 5 destinations échantillon

### Juillet 2026 — déploiement
- **Sem 1** : déploiement 754 × 5 langues = 3770 fiches V6 d'un coup sur PROD
- **Sem 2-4** : monitoring GSC strict, mesure trafic, ajustements

### Critère go/no-go juillet
- Tests automatisés `tests/test_scoring.py` 100% pass
- Validation visuelle 5×5 = 25 fiches échantillon OK
- Pattern-LLM < 2% sur les 4 langues nouvelles
- Cloudflare staging stable 1 semaine sans incident

## 5. Limites & ce que je n'ai PAS vérifié

- **JSON-LD / SEO meta V6** : pas inspecté. Risque de régression GSC si les schémas changent.
- **Performance** : pas mesuré le poids V6 vs V5 (685 lignes HTML vs 255). Impact LCP/CLS inconnu.
- **Service Worker** : `sw-register.js` chargé en V5, pas dans V6 prototypes. Si SW cache app.css, conflit possible avec v6.css.
- **Internal linking** : V5 a `crosslinks` (ligne 277 generate_pages.py) pour SEO interne. V6 prototypes n'en ont pas. Risque de perdre du jus SEO.
- **Sitemap.xml / hreflang** : pas vérifié si la migration impacte les fichiers de sitemap.

## 6. Décisions à valider avant de coder

1. ⏳ **Architecture refactor (Option A vs B)** — en attente
2. ✅ ~~Périmètre rollout V6~~ → bloquer multilangue
3. ✅ ~~Profils Box 3~~ → décision technique, "Séjour citadin" par défaut
4. ⏳ **Crosslinks et SEO interne** → on les ajoute en V6 ou pas ? (à décider semaine 1 mai)
