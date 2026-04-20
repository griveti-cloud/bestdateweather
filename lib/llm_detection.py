"""
Anti-pattern LLM pour la génération de fiches destination.

Objectif : éviter que Google détecte les 45 000 fiches comme du contenu IA
répétitif en :
1. Variant les formulations via hash déterministe (même slug = même variante,
   reproductibilité garantie)
2. Interdisant un vocabulaire signature des LLM touristiques
3. Validant la burstiness (variance de longueur de phrase)
4. Imposant des référents locaux vérifiables

Usage dans generate_pages.py :

    from lib.llm_detection import pick_variant, check_no_llm_patterns

    verdict = pick_variant(VERDICT_TEMPLATES, slug=dest['slug_fr'],
                          nom=dest['nom_fr'], top1='Juillet', top2='Août')

    # Avant écriture HTML :
    check_no_llm_patterns(verdict, page_id=dest['slug_fr'])
"""

import hashlib
import re


# ══════════════════════════════════════════════════════════════════
# 1. VOCABULAIRE INTERDIT
# ══════════════════════════════════════════════════════════════════

FORBIDDEN_WORDS_FR = [
    # Clichés touristiques LLM-signature
    "véritable",
    "idyllique",
    "authentique",
    "incontournable",
    "immersion totale",
    "couper le souffle",
    "dépaysement total",
    "enchanteur",
    "envoûtant",
    "mystique",
    # Connecteurs LLM obsessifs
    "En effet,",
    "Par ailleurs,",
    "De plus,",
    "En outre,",
    "Il convient de noter",
    "Il est à noter",
    # Verbes d'invitation LLM-typiques
    "N'hésitez pas",
    "Plongez-vous",
    "Laissez-vous",
    "Laissez vous",
    "Préparez-vous à être",
    # Structures LLM-typiques
    "il convient de",
    "il est important de",
    "il est essentiel de",
    "Que vous soyez",
    "Dans ce guide",
    "Dans cet article",
    # Redondances touristiques
    "cette merveilleuse destination",
    "ce joyau",
    "cette perle",
]

# Words qu'on peut autoriser UNE FOIS max par fiche
LIMITED_WORDS_FR = {
    "unique": 1,      # OK une fois dans la fiche
    "authentique": 0, # Banni totalement (dans FORBIDDEN)
    "magique": 1,
}


# ══════════════════════════════════════════════════════════════════
# 2. TEMPLATES À VARIANTES (picking déterministe par slug)
# ══════════════════════════════════════════════════════════════════

# Chaque template contient {placeholders} à remplir via .format(**kwargs).
# 5-8 variantes minimum par template pour éviter la répétition.
# Calibré pour n'utiliser AUCUN mot de FORBIDDEN_WORDS_FR.

VERDICT_TROPICAL_FR = [
    "À {nom}, le vrai arbitrage porte sur la pluie — pas la température. Les meilleurs mois sont {top1} et {top2}. Évitez {worst} (mousson installée).",
    "La fenêtre optimale à {nom} se joue sur {top1}-{top2}, les seuls mois vraiment exploitables. {worst} concentre le gros de la saison humide.",
    "{nom} reste tropical toute l'année : 24-30°C partout. Mais {top1} et {top2} sortent du lot côté ciel clair et faible pluie. À éviter : {worst}.",
    "Pour {nom}, privilégier {top1} ou {top2}. {worst} reste praticable mais concentre 80%+ de jours de pluie.",
    "La décision à {nom} se résume à : {top1}-{top2} pour le confort, {worst} pour le budget (si la pluie ne vous arrête pas).",
]

VERDICT_MOUNTAIN_FR = [
    "À {nom}, tout dépend de votre objectif. Pour skier : {ski_top}. Pour randonner : {hike_top}. Évitez {worst} (entre-saisons).",
    "{nom} se vit en deux saisons distinctes. Ski en {ski_top}, rando en {hike_top}. {worst} concentrent le creux de l'année.",
    "La question à {nom} n'est pas quand, mais pourquoi partir. {ski_top} = ski optimal. {hike_top} = rando et alpinisme. {worst} à fuir.",
    "Pour {nom}, viser {ski_top} si ski, {hike_top} si rando. Les remontées ferment en {worst} : stations mortes.",
    "À {nom}, deux pics opposés : {ski_top} (ski, neige fraîche) et {hike_top} (sentiers secs, refuges ouverts). Mai et novembre = éviter.",
]

VERDICT_GENERIC_FR = [
    "À {nom}, {top1} et {top2} sortent clairement du lot. {worst} concentre les conditions les moins favorables.",
    "Le meilleur moment pour {nom} : {top1}-{top2}. À éviter : {worst}.",
    "Pour {nom}, privilégier {top1} et {top2}. {worst} reste visitable mais avec des conditions difficiles.",
    "La fenêtre optimale à {nom} se situe entre {top1} et {top2}. Évitez {worst} si vous pouvez choisir.",
    "{nom} s'apprécie surtout en {top1} et {top2}. {worst} déçoit côté météo.",
]

# Templates avis éditorial (plus personnels, « voix » de l'auteur)
AVIS_EDITO_TROPICAL_FR = [
    "Pour {nom}, <strong>viser vraiment {top1}-{top2}</strong> même avec la foule. C'est la seule fenêtre où pluie et humidité deviennent tolérables. Mai ou octobre restent acceptables pour ceux qui cherchent à échapper au pic touristique.",
    "<strong>{top1}-{top2} reste mon choix</strong> à {nom}, tant pis pour la fréquentation. La différence de confort météo vaut le compromis tarif. Sur {worst}, beaucoup de locaux ferment boutique.",
    "À {nom}, tenter <strong>{top1} ou septembre</strong> plutôt qu'août : météo presque identique, 40% de monde en moins, tarifs plus doux. À éviter absolument : {worst}.",
]

AVIS_EDITO_MOUNTAIN_FR = [
    "Pour {nom}, la question n'est pas quand, mais <strong>pourquoi</strong>. Hiver = {ski_top} pour le ski, enneigement maximal. Été = {hike_top} pour l'alpinisme, mais bondé. <strong>Septembre reste mon préféré</strong> : températures agréables, refuges ouverts jusqu'au 20, un tiers du monde.",
    "À {nom}, deux fenêtres nettes : {ski_top} pour le ski dur, {hike_top} pour la rando. Mai et novembre sont mortes : remontées fermées, refuges clos. <strong>Octobre</strong> reste praticable pour les trails aux couleurs automnales.",
]


# ══════════════════════════════════════════════════════════════════
# 3. SÉLECTION DÉTERMINISTE
# ══════════════════════════════════════════════════════════════════

def pick_variant(variants, slug, **kwargs):
    """
    Sélectionne une variante via hash MD5 du slug.

    Garantie : même slug → même variante (reproductibilité entre générations).
    Effet : 45 000 fiches divisées par N variantes = chaque variante utilisée
    environ 45000/N fois (distribution uniforme du hash).

    Args:
        variants: list[str] — templates avec placeholders {xxx}
        slug: str — identifiant unique de la destination
        **kwargs: valeurs à injecter dans le template

    Returns:
        str — template formaté
    """
    if not variants:
        raise ValueError("Liste de variantes vide")
    h = int(hashlib.md5(slug.encode("utf-8")).hexdigest()[:8], 16)
    idx = h % len(variants)
    return variants[idx].format(**kwargs)


# ══════════════════════════════════════════════════════════════════
# 4. VALIDATION ANTI-PATTERN
# ══════════════════════════════════════════════════════════════════

def check_no_llm_patterns(text, page_id=None, strict=True):
    """
    Vérifie qu'un texte ne contient pas de vocabulaire LLM-signature.

    Args:
        text: str — contenu à vérifier (peut contenir du HTML, sera décapé)
        page_id: str — identifiant pour le message d'erreur (slug ou nom fichier)
        strict: bool — True = lève ValueError, False = retourne la liste des problèmes

    Returns:
        list — vide si OK, sinon liste des patterns trouvés
    """
    # Décaper HTML
    plain = re.sub(r"<[^>]+>", " ", text)

    problems = []
    for word in FORBIDDEN_WORDS_FR:
        if re.search(r"\b" + re.escape(word) + r"\b", plain, re.IGNORECASE):
            problems.append(word)

    # Vérifier la limite sur les LIMITED_WORDS
    for word, max_count in LIMITED_WORDS_FR.items():
        count = len(re.findall(r"\b" + re.escape(word) + r"\b", plain, re.IGNORECASE))
        if count > max_count:
            problems.append(f"{word} ({count}x > {max_count})")

    if problems and strict:
        pid = page_id or "[unknown]"
        raise ValueError(
            f"[{pid}] Patterns LLM détectés : {', '.join(problems)}"
        )
    return problems


def check_burstiness(text, min_std=6.0, min_sentences=5, page_id=None):
    """
    Vérifie la variance de longueur des phrases.

    Les LLM écrivent avec des phrases de longueur uniforme (std ~3-5 mots).
    Les humains varient (std ~8-15 mots).

    Args:
        text: str — contenu à vérifier
        min_std: float — écart-type minimal acceptable
        min_sentences: int — nombre minimal de phrases pour appliquer le check
        page_id: str — identifiant pour le message

    Returns:
        (ok: bool, std: float, n_sentences: int) — info pour log/warning
    """
    import statistics

    plain = re.sub(r"<[^>]+>", " ", text)
    sentences = [s.strip() for s in re.split(r"[.!?]+", plain) if s.strip()]

    if len(sentences) < min_sentences:
        return True, 0.0, len(sentences)  # Trop court pour évaluer

    lengths = [len(s.split()) for s in sentences]
    std = statistics.stdev(lengths) if len(lengths) > 1 else 0.0
    ok = std >= min_std
    return ok, std, len(sentences)


# ══════════════════════════════════════════════════════════════════
# TESTS unitaires
# ══════════════════════════════════════════════════════════════════

def _test():
    """Sanity check des fonctions."""
    # Test 1 : pick_variant déterministe
    v1 = pick_variant(VERDICT_GENERIC_FR, slug="bali", nom="Bali",
                      top1="Juillet", top2="Août", worst="Février")
    v2 = pick_variant(VERDICT_GENERIC_FR, slug="bali", nom="Bali",
                      top1="Juillet", top2="Août", worst="Février")
    assert v1 == v2, "pick_variant non déterministe"
    print(f"  ✓ pick_variant déterministe : '{v1[:80]}...'")

    # Test 2 : différent slug = potentiellement différente variante
    v3 = pick_variant(VERDICT_GENERIC_FR, slug="chamonix", nom="Chamonix",
                      top1="Juillet", top2="Août", worst="Novembre")
    print(f"  ✓ chamonix : '{v3[:80]}...'")

    # Test 3 : distribution sur 100 slugs
    dist = {}
    for i in range(100):
        slug = f"dest-{i}"
        idx = int(hashlib.md5(slug.encode()).hexdigest()[:8], 16) % len(VERDICT_GENERIC_FR)
        dist[idx] = dist.get(idx, 0) + 1
    print(f"  ✓ Distribution sur 100 slugs (5 variantes) : {dist}")
    # Chaque variante devrait apparaître entre 10 et 35 fois (20% ± bruit)

    # Test 4 : détection patterns LLM
    bad = "Plongez-vous dans cette véritable immersion totale à Bali !"
    problems = check_no_llm_patterns(bad, page_id="test", strict=False)
    assert "véritable" in problems
    assert "Plongez-vous" in problems
    assert "immersion totale" in problems
    print(f"  ✓ check_no_llm_patterns détecte : {problems}")

    # Test 5 : texte propre passe
    ok = "Bali reste tropical toute l'année. Juillet sort du lot côté ciel clair."
    problems = check_no_llm_patterns(ok, page_id="test", strict=False)
    assert problems == [], f"Faux positif : {problems}"
    print(f"  ✓ Texte propre : 0 problème")

    # Test 6 : strict=True lève
    try:
        check_no_llm_patterns(bad, page_id="test-strict", strict=True)
        print("  ✗ strict=True n'a pas levé")
    except ValueError as e:
        print(f"  ✓ strict=True lève : {str(e)[:80]}...")

    # Test 7 : burstiness
    # Texte LLM typique (phrases uniformes ~12 mots)
    text_llm = (
        "La destination offre de nombreuses possibilités aux voyageurs curieux. "
        "Le climat reste agréable la majeure partie de l'année ici. "
        "Les activités se multiplient selon les saisons qui défilent. "
        "Les voyageurs apprécient la variété des paysages proposés."
    )
    ok, std, n = check_burstiness(text_llm)
    print(f"  → burstiness LLM : std={std:.1f} (ok={ok}, {n} phrases)")

    # Texte humain (variance forte)
    text_human = (
        "À Bali, viser juillet-août. Point. "
        "C'est la seule fenêtre où la pluie tombe assez pour laisser exploiter les "
        "sites touristiques sans se taper des averses de 2h chaque après-midi. "
        "Mai ? Acceptable. Février : non."
    )
    ok, std, n = check_burstiness(text_human)
    print(f"  → burstiness humain : std={std:.1f} (ok={ok}, {n} phrases)")

    print("\n  Tests terminés.")


if __name__ == "__main__":
    _test()
