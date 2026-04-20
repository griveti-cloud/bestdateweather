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

FORBIDDEN_WORDS_EN = [
    # Clichés touristiques LLM-signature (communs EN + EN-US)
    "breathtaking",
    "picturesque",
    "charming",
    "enchanting",
    "mesmerizing",
    "mystical",
    "idyllic",
    "hidden gem",
    "must-see",
    "must-visit",
    "a true gem",
    "truly unique",
    "a paradise",
    "paradise found",
    "nestled in",
    "steeped in history",
    # Connecteurs LLM obsessifs
    "Furthermore,",
    "Moreover,",
    "Additionally,",
    "In addition,",
    "It is worth noting",
    "It should be noted",
    # Verbes d'invitation LLM-typiques
    "Immerse yourself",
    "Dive into",
    "Allow yourself",
    "Don't miss",
    "Be prepared to",
    # Structures LLM-typiques
    "It is important to",
    "It is essential to",
    "Whether you're",
    "Whether you are",
    "In this guide",
    "In this article",
    # Redondances touristiques
    "this wonderful destination",
    "this gem",
    "this jewel",
]

FORBIDDEN_WORDS_ES = [
    # Clichés touristicos LLM-signature
    "pintoresco",
    "auténtico",
    "mágico",
    "encantador",
    "imperdible",
    "imprescindible",
    "único",
    "joya oculta",
    "un verdadero",
    "una verdadera joya",
    "un paraíso",
    "rincón escondido",
    # Connecteurs LLM
    "Además,",
    "Por otra parte,",
    "Asimismo,",
    "Cabe destacar",
    "Es importante destacar",
    # Verbes LLM
    "Sumérgete",
    "Déjate llevar",
    "No dudes",
    "No te pierdas",
    "Prepárate para",
    # Structures LLM
    "Es importante",
    "Es esencial",
    "Ya sea",
    "En esta guía",
    "En este artículo",
    # Redondances
    "este maravilloso destino",
    "esta joya",
    "esta maravilla",
]

FORBIDDEN_WORDS_DE = [
    # Clichés touristisch LLM-signature
    "atemberaubend",
    "malerisch",
    "authentisch",
    "bezaubernd",
    "unvergesslich",
    "mystisch",
    "idyllisch",
    "ein wahres",
    "eine wahre Perle",
    "verstecktes Juwel",
    "ein Paradies",
    # Connecteurs LLM
    "Darüber hinaus",
    "Außerdem,",
    "Zudem,",
    "Des Weiteren",
    "Es sei angemerkt",
    "Es ist wichtig",
    # Verbes LLM
    "Tauchen Sie ein",
    "Lassen Sie sich",
    "Zögern Sie nicht",
    "Verpassen Sie nicht",
    "Bereiten Sie sich",
    # Structures LLM
    "Es ist wichtig zu",
    "Es ist essentiell",
    "Ob Sie",
    "In diesem Artikel",
    "In diesem Guide",
    # Redondances
    "dieses wunderbare Reiseziel",
    "dieses Juwel",
    "diese Perle",
]

# Dictionnaire pour accès par code langue
FORBIDDEN_WORDS_BY_LANG = {
    "fr": FORBIDDEN_WORDS_FR,
    "en": FORBIDDEN_WORDS_EN,
    "en-us": FORBIDDEN_WORDS_EN,  # Même vocabulaire anglais
    "es": FORBIDDEN_WORDS_ES,
    "de": FORBIDDEN_WORDS_DE,
}

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

# ── EN (Anglais international) ──────────────────────────────────────

VERDICT_TROPICAL_EN = [
    "At {nom}, the real trade-off is rain, not temperature. The best months are {top1} and {top2}. Skip {worst} (monsoon in full swing).",
    "The sweet spot at {nom} is {top1}-{top2}, the only months that really work. {worst} concentrates the bulk of the wet season.",
    "{nom} stays tropical year-round: 24-30°C everywhere. But {top1} and {top2} stand out for clear skies and low rainfall. Skip: {worst}.",
    "For {nom}, go with {top1} or {top2}. {worst} is doable but 80%+ rainy days.",
    "The call for {nom} comes down to: {top1}-{top2} for comfort, {worst} for budget (if rain doesn't bother you).",
]

VERDICT_MOUNTAIN_EN = [
    "At {nom}, it depends on your goal. Skiing: {ski_top}. Hiking: {hike_top}. Skip {worst} (shoulder months).",
    "{nom} has two distinct seasons. Ski in {ski_top}, hike in {hike_top}. {worst} is the dead of the year.",
    "The question at {nom} isn't when, but why. {ski_top} = peak ski. {hike_top} = hiking and climbing. {worst} to avoid.",
    "For {nom}, aim for {ski_top} (ski) or {hike_top} (hike). Lifts close in {worst}: dead resort town.",
    "At {nom}, two opposite peaks: {ski_top} (ski, fresh snow) and {hike_top} (dry trails, open huts). May and November = skip.",
]

VERDICT_GENERIC_EN = [
    "At {nom}, {top1} and {top2} clearly stand out. {worst} has the least favorable conditions.",
    "Best time for {nom}: {top1}-{top2}. Skip: {worst}.",
    "For {nom}, go with {top1} and {top2}. {worst} is still visitable but with tough weather.",
    "The best window for {nom} is between {top1} and {top2}. Skip {worst} if you can.",
    "{nom} shines in {top1} and {top2}. {worst} disappoints weather-wise.",
]

AVIS_EDITO_TROPICAL_EN = [
    "For {nom}, <strong>really target {top1}-{top2}</strong> even with the crowds. It's the only window where rain and humidity become tolerable. May or October work for those dodging peak tourism.",
    "<strong>{top1}-{top2} is my call</strong> for {nom}, despite the crowds. The weather comfort gap justifies the price trade-off. In {worst}, many local businesses close.",
    "At {nom}, try <strong>{top1} or September</strong> over August: almost identical weather, 40% fewer tourists, softer prices. Avoid at all costs: {worst}.",
]

AVIS_EDITO_MOUNTAIN_EN = [
    "At {nom}, the question isn't when but <strong>why</strong>. Winter = {ski_top} for skiing, max snowpack. Summer = {hike_top} for mountaineering, but packed. <strong>September is my pick</strong>: good temps, huts open through the 20th, a third of the crowds.",
    "At {nom}, two clear windows: {ski_top} for serious skiing, {hike_top} for hiking. May and November are dead: lifts closed, huts shut. <strong>October</strong> still works for trails in fall colors.",
]

# ── ES (Espagnol) ───────────────────────────────────────────────────

VERDICT_TROPICAL_ES = [
    "En {nom}, el verdadero dilema es la lluvia, no la temperatura. Los mejores meses son {top1} y {top2}. Evita {worst} (monzón en plena fuerza).",
    "La ventana óptima en {nom} es {top1}-{top2}, los pocos meses realmente viables. {worst} concentra el grueso de la temporada húmeda.",
    "{nom} es tropical todo el año: 24-30°C en todos lados. Pero {top1} y {top2} destacan por cielos despejados y poca lluvia. Evitar: {worst}.",
    "Para {nom}, apuesta por {top1} o {top2}. {worst} sigue siendo posible pero con 80%+ de días de lluvia.",
    "La decisión para {nom} se reduce a: {top1}-{top2} por el confort, {worst} por el presupuesto (si la lluvia no te para).",
]

VERDICT_MOUNTAIN_ES = [
    "En {nom} depende de tu objetivo. Para esquiar: {ski_top}. Para senderismo: {hike_top}. Evita {worst} (entre-temporadas).",
    "{nom} tiene dos temporadas bien marcadas. Esquí en {ski_top}, senderismo en {hike_top}. {worst} es el vacío del año.",
    "La pregunta en {nom} no es cuándo, sino por qué. {ski_top} = esquí óptimo. {hike_top} = senderismo y alpinismo. {worst} evitar.",
    "Para {nom}, apuntar a {ski_top} si esquí, {hike_top} si senderismo. Los remontes cierran en {worst}: estación muerta.",
    "En {nom}, dos picos opuestos: {ski_top} (esquí, nieve fresca) y {hike_top} (senderos secos, refugios abiertos). Mayo y noviembre = evitar.",
]

VERDICT_GENERIC_ES = [
    "En {nom}, {top1} y {top2} destacan claramente. {worst} concentra las condiciones menos favorables.",
    "El mejor momento para {nom}: {top1}-{top2}. A evitar: {worst}.",
    "Para {nom}, apostar por {top1} y {top2}. {worst} sigue siendo visitable pero con condiciones difíciles.",
    "La ventana óptima para {nom} se sitúa entre {top1} y {top2}. Evitar {worst} si se puede elegir.",
    "{nom} brilla sobre todo en {top1} y {top2}. {worst} decepciona por el tiempo.",
]

AVIS_EDITO_TROPICAL_ES = [
    "Para {nom}, <strong>apuntar realmente a {top1}-{top2}</strong> incluso con la multitud. Es la única ventana donde lluvia y humedad son tolerables. Mayo u octubre sirven para quien huye del pico turístico.",
    "<strong>{top1}-{top2} sigue siendo mi elección</strong> para {nom}, pese a la afluencia. La diferencia de confort climático compensa el coste. En {worst}, muchos negocios locales cierran.",
    "En {nom}, intentar <strong>{top1} o septiembre</strong> antes que agosto: tiempo casi idéntico, 40% menos de gente, precios más suaves. A evitar del todo: {worst}.",
]

AVIS_EDITO_MOUNTAIN_ES = [
    "En {nom}, la pregunta no es cuándo, sino <strong>por qué</strong>. Invierno = {ski_top} para esquí, máxima nieve. Verano = {hike_top} para alpinismo, pero lleno. <strong>Septiembre sigue siendo mi preferido</strong>: temperaturas agradables, refugios abiertos hasta el 20, un tercio del mundo.",
    "En {nom}, dos ventanas claras: {ski_top} para esquí exigente, {hike_top} para senderismo. Mayo y noviembre están muertos: remontes cerrados, refugios clausurados. <strong>Octubre</strong> sigue siendo practicable para rutas en colores otoñales.",
]

# ── DE (Allemand) ───────────────────────────────────────────────────

VERDICT_TROPICAL_DE = [
    "In {nom} geht es nicht um die Temperatur, sondern um den Regen. Die besten Monate sind {top1} und {top2}. Meiden Sie {worst} (Monsun voll im Gange).",
    "Das optimale Fenster in {nom} liegt in {top1}-{top2}, den einzigen wirklich nutzbaren Monaten. {worst} trägt das Hauptgewicht der Regenzeit.",
    "{nom} bleibt ganzjährig tropisch: überall 24-30°C. Aber {top1} und {top2} stechen bei klarem Himmel und wenig Regen heraus. Meiden: {worst}.",
    "Für {nom}, setzen Sie auf {top1} oder {top2}. {worst} ist machbar, aber 80%+ Regentage.",
    "Die Entscheidung für {nom} läuft auf dies hinaus: {top1}-{top2} für den Komfort, {worst} fürs Budget (wenn Regen nicht stört).",
]

VERDICT_MOUNTAIN_DE = [
    "In {nom} hängt alles vom Ziel ab. Ski: {ski_top}. Wandern: {hike_top}. Meiden {worst} (Zwischensaison).",
    "{nom} kennt zwei klare Jahreszeiten. Ski in {ski_top}, Wandern in {hike_top}. {worst} ist die tote Zeit.",
    "Die Frage in {nom} ist nicht wann, sondern warum. {ski_top} = Ski-Peak. {hike_top} = Wandern und Bergsteigen. {worst} meiden.",
    "Für {nom}, zielen Sie auf {ski_top} (Ski) oder {hike_top} (Wandern). Lifte schließen in {worst}: tote Station.",
    "In {nom}, zwei gegensätzliche Spitzen: {ski_top} (Ski, frischer Schnee) und {hike_top} (trockene Pfade, offene Hütten). Mai und November = meiden.",
]

VERDICT_GENERIC_DE = [
    "In {nom}, {top1} und {top2} stechen klar heraus. {worst} konzentriert die ungünstigsten Bedingungen.",
    "Beste Zeit für {nom}: {top1}-{top2}. Meiden: {worst}.",
    "Für {nom}, setzen Sie auf {top1} und {top2}. {worst} ist besuchbar, aber mit schwierigen Bedingungen.",
    "Das optimale Fenster für {nom} liegt zwischen {top1} und {top2}. Meiden {worst}, wenn Sie wählen können.",
    "{nom} glänzt vor allem in {top1} und {top2}. {worst} enttäuscht wettermäßig.",
]

AVIS_EDITO_TROPICAL_DE = [
    "Für {nom}, <strong>wirklich auf {top1}-{top2} zielen</strong>, auch mit dem Andrang. Es ist das einzige Fenster, in dem Regen und Luftfeuchtigkeit erträglich werden. Mai oder Oktober passen für alle, die der Hauptsaison ausweichen.",
    "<strong>{top1}-{top2} bleibt meine Wahl</strong> für {nom}, trotz der Menge. Der Komfort-Unterschied rechtfertigt den Preis. In {worst} schließen viele lokale Betriebe.",
    "In {nom}, <strong>{top1} oder September</strong> statt August versuchen: fast identisches Wetter, 40% weniger Menschen, weichere Preise. Absolut meiden: {worst}.",
]

AVIS_EDITO_MOUNTAIN_DE = [
    "In {nom} ist die Frage nicht wann, sondern <strong>warum</strong>. Winter = {ski_top} für Ski, maximaler Schnee. Sommer = {hike_top} für Bergsteigen, aber voll. <strong>September bleibt mein Favorit</strong>: angenehme Temperaturen, Hütten bis 20. offen, ein Drittel der Menge.",
    "In {nom}, zwei klare Fenster: {ski_top} für harten Ski, {hike_top} für Wandern. Mai und November sind tot: Lifte geschlossen, Hütten zu. <strong>Oktober</strong> bleibt für Trails in Herbstfarben praktikabel.",
]

# ── Dictionnaire d'accès par (template_type, lang) ──────────────────

TEMPLATES_BY_LANG = {
    "verdict_tropical": {
        "fr": VERDICT_TROPICAL_FR, "en": VERDICT_TROPICAL_EN, "en-us": VERDICT_TROPICAL_EN,
        "es": VERDICT_TROPICAL_ES, "de": VERDICT_TROPICAL_DE,
    },
    "verdict_mountain": {
        "fr": VERDICT_MOUNTAIN_FR, "en": VERDICT_MOUNTAIN_EN, "en-us": VERDICT_MOUNTAIN_EN,
        "es": VERDICT_MOUNTAIN_ES, "de": VERDICT_MOUNTAIN_DE,
    },
    "verdict_generic": {
        "fr": VERDICT_GENERIC_FR, "en": VERDICT_GENERIC_EN, "en-us": VERDICT_GENERIC_EN,
        "es": VERDICT_GENERIC_ES, "de": VERDICT_GENERIC_DE,
    },
    "avis_edito_tropical": {
        "fr": AVIS_EDITO_TROPICAL_FR, "en": AVIS_EDITO_TROPICAL_EN, "en-us": AVIS_EDITO_TROPICAL_EN,
        "es": AVIS_EDITO_TROPICAL_ES, "de": AVIS_EDITO_TROPICAL_DE,
    },
    "avis_edito_mountain": {
        "fr": AVIS_EDITO_MOUNTAIN_FR, "en": AVIS_EDITO_MOUNTAIN_EN, "en-us": AVIS_EDITO_MOUNTAIN_EN,
        "es": AVIS_EDITO_MOUNTAIN_ES, "de": AVIS_EDITO_MOUNTAIN_DE,
    },
}


def get_templates(template_type, lang="fr"):
    """Récupère les variantes d'un template pour une langue donnée."""
    if template_type not in TEMPLATES_BY_LANG:
        raise ValueError(f"Unknown template_type: {template_type}. Available: {list(TEMPLATES_BY_LANG.keys())}")
    lang_map = TEMPLATES_BY_LANG[template_type]
    if lang not in lang_map:
        raise ValueError(f"Unknown lang: {lang}. Available: {list(lang_map.keys())}")
    return lang_map[lang]


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

def check_no_llm_patterns(text, page_id=None, strict=True, lang="fr"):
    """
    Vérifie qu'un texte ne contient pas de vocabulaire LLM-signature.

    Args:
        text: str — contenu à vérifier (peut contenir du HTML, sera décapé)
        page_id: str — identifiant pour le message d'erreur (slug ou nom fichier)
        strict: bool — True = lève ValueError, False = retourne la liste des problèmes
        lang: str — 'fr', 'en', 'en-us', 'es', 'de'. Utilise la wordlist correspondante.

    Returns:
        list — vide si OK, sinon liste des patterns trouvés
    """
    # Décaper HTML
    plain = re.sub(r"<[^>]+>", " ", text)

    forbidden = FORBIDDEN_WORDS_BY_LANG.get(lang, FORBIDDEN_WORDS_FR)

    problems = []
    # Suffixes morphologiques courants : pluriels (s/n), déclinaisons DE (e/er/es/en/em),
    # accords FR (s/e/es). Permet de détecter racine + flexion courte.
    suffix_pattern = r"(?:e|er|es|en|em|s|n|ment)?\b"
    for word in forbidden:
        # Si le mot contient déjà un espace ou ponctuation, match exact ; sinon racine + suffixe optionnel
        if " " in word or "," in word or "'" in word:
            pat = r"\b" + re.escape(word) + r"\b"
        else:
            pat = r"\b" + re.escape(word) + suffix_pattern
        if re.search(pat, plain, re.IGNORECASE):
            problems.append(word)

    # Vérifier la limite sur les LIMITED_WORDS (FR uniquement pour l'instant)
    if lang == "fr":
        for word, max_count in LIMITED_WORDS_FR.items():
            count = len(re.findall(r"\b" + re.escape(word) + r"\b", plain, re.IGNORECASE))
            if count > max_count:
                problems.append(f"{word} ({count}x > {max_count})")

    if problems and strict:
        pid = page_id or "[unknown]"
        raise ValueError(
            f"[{pid}] Patterns LLM ({lang}) détectés : {', '.join(problems)}"
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
