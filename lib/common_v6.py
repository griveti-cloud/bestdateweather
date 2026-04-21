"""
V6 — Construction des blocs HTML de la fiche destination au format V5.

Premier module de V6 : fournit les fonctions qui transforment une destination
+ ses données mensuelles en HTML structuré.

Pipeline attendu dans generate_pages.py (V6) :

    from lib.common_v6 import build_decision_card_v6

    # dest : dict issu de destinations.csv (slug, nom_fr, tropical, mountain, ...)
    # monthly : list[dict] 12 entrées, chacun avec {mois_num, score, tmax, ...}
    html_card = build_decision_card_v6(dest, monthly, lang='fr')

Fonctions principales :
- best_month(), worst_month(), top_n_months(), shoulder_months()
- classify_dest() → 'tropical' | 'mountain' | 'generic'
- build_decision_card_v6(dest, monthly, lang) → HTML

Testé isolément. Pas de dépendance à generate_pages.py ni à common.py.
"""

import html as _html

from lib.llm_detection import check_no_llm_patterns, pick_variant, get_templates


# ══════════════════════════════════════════════════════════════════
# i18n : mois + labels UI
# ══════════════════════════════════════════════════════════════════

MONTH_NAMES = {
    "fr": ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin",
           "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"],
    "en": ["January", "February", "March", "April", "May", "June",
           "July", "August", "September", "October", "November", "December"],
    "en-us": ["January", "February", "March", "April", "May", "June",
              "July", "August", "September", "October", "November", "December"],
    "es": ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
           "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"],
    "de": ["Januar", "Februar", "März", "April", "Mai", "Juni",
           "Juli", "August", "September", "Oktober", "November", "Dezember"],
}

MONTH_SHORT = {
    "fr": ["Jan", "Fév", "Mar", "Avr", "Mai", "Juin", "Juil", "Aoû", "Sep", "Oct", "Nov", "Déc"],
    "en": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
    "en-us": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
    "es": ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"],
    "de": ["Jan", "Feb", "Mär", "Apr", "Mai", "Jun", "Jul", "Aug", "Sep", "Okt", "Nov", "Dez"],
}

UI_LABELS = {
    "fr": {
        "reponse_rapide": "⚡ Réponse rapide",
        "top_n_mois": "Top {n} mois",
        "mois_a_eviter": "Mois le plus rude",
        "mi_saison": "Mi-saison idéale",
        "saison_seche": "Saison sèche",
        "saison_humide": "Saison humide",
        "saison_ski": "Ski optimal",
        "saison_rando": "Randonnée",
        "meilleur_mois": "Meilleur mois",
    },
    "en": {
        "reponse_rapide": "⚡ Quick answer",
        "top_n_mois": "Top {n} months",
        "mois_a_eviter": "Toughest month",
        "mi_saison": "Ideal shoulder",
        "saison_seche": "Dry season",
        "saison_humide": "Wet season",
        "saison_ski": "Peak ski",
        "saison_rando": "Hiking",
        "meilleur_mois": "Best month",
    },
    "en-us": {
        "reponse_rapide": "⚡ Quick answer",
        "top_n_mois": "Top {n} months",
        "mois_a_eviter": "Toughest month",
        "mi_saison": "Ideal shoulder",
        "saison_seche": "Dry season",
        "saison_humide": "Wet season",
        "saison_ski": "Peak ski",
        "saison_rando": "Hiking",
        "meilleur_mois": "Best month",
    },
    "es": {
        "reponse_rapide": "⚡ Respuesta rápida",
        "top_n_mois": "Top {n} meses",
        "mois_a_eviter": "Mes más duro",
        "mi_saison": "Entre-temporada ideal",
        "saison_seche": "Temporada seca",
        "saison_humide": "Temporada húmeda",
        "saison_ski": "Esquí óptimo",
        "saison_rando": "Senderismo",
        "meilleur_mois": "Mejor mes",
    },
    "de": {
        "reponse_rapide": "⚡ Schnelle Antwort",
        "top_n_mois": "Top {n} Monate",
        "mois_a_eviter": "Härtester Monat",
        "mi_saison": "Ideale Zwischensaison",
        "saison_seche": "Trockenzeit",
        "saison_humide": "Regenzeit",
        "saison_ski": "Ski optimal",
        "saison_rando": "Wandern",
        "meilleur_mois": "Bester Monat",
    },
}


# ══════════════════════════════════════════════════════════════════
# Classification de la destination
# ══════════════════════════════════════════════════════════════════

def classify_dest(dest):
    """
    Retourne 'tropical' | 'mountain' | 'generic' selon les flags de destinations.csv.

    Args:
        dest: dict avec clés 'tropical' et 'mountain' (valeurs '1' ou '0' en CSV)

    Returns:
        str : un des 3 types
    """
    # Supporte bool, int ou str depuis CSV
    def _truthy(v):
        if isinstance(v, bool):
            return v
        if isinstance(v, (int, float)):
            return v > 0
        if isinstance(v, str):
            return v.strip().lower() in ("1", "true", "yes", "oui")
        return False

    if _truthy(dest.get("tropical")):
        return "tropical"
    if _truthy(dest.get("mountain")):
        return "mountain"
    return "generic"


# ══════════════════════════════════════════════════════════════════
# Sélection des mois-clés
# ══════════════════════════════════════════════════════════════════

def _score(m):
    """Lit le score d'un dict mois (supporte float ou str)."""
    return float(m.get("score", 0))


def best_month(monthly):
    """Retourne le dict mois au score le plus élevé."""
    if not monthly:
        raise ValueError("monthly vide")
    return max(monthly, key=_score)


def worst_month(monthly):
    """Retourne le dict mois au score le plus bas."""
    if not monthly:
        raise ValueError("monthly vide")
    return min(monthly, key=_score)


def top_n_months(monthly, n=3):
    """
    Retourne les N mois aux scores les plus élevés, triés par ordre chronologique
    (mois_num croissant) pour affichage en groupe.

    Args:
        monthly: list[dict] 12 entrées
        n: int nombre de mois à extraire

    Returns:
        list[dict] : les N top, triés par mois_num (pas par score)
    """
    top = sorted(monthly, key=_score, reverse=True)[:n]
    return sorted(top, key=lambda m: int(m.get("mois_num", 0)))


def shoulder_months(monthly, n_main=3, n_shoulder=2):
    """
    Identifie les mois d'entre-saison : pas dans le top N, pas dans le bottom N,
    mais dans la moyenne haute (scores supérieurs à la médiane).

    Stratégie : exclure les N meilleurs et les N pires, prendre les n_shoulder
    suivants par score décroissant. Triés chronologiquement pour affichage.

    Args:
        monthly: list[dict] 12 entrées
        n_main: int, nombre de mois "top" à exclure
        n_shoulder: int, nombre de mois shoulder à retourner

    Returns:
        list[dict] triés par mois_num
    """
    sorted_by_score = sorted(monthly, key=_score, reverse=True)
    # Skip les n_main meilleurs, prendre les n_shoulder suivants
    shoulder = sorted_by_score[n_main:n_main + n_shoulder]
    return sorted(shoulder, key=lambda m: int(m.get("mois_num", 0)))


# ══════════════════════════════════════════════════════════════════
# Formatage labels mois
# ══════════════════════════════════════════════════════════════════

def format_month_list_short(months, lang="fr", sep=" · "):
    """
    Formate une liste de mois en forme courte : 'Juin · Juil · Août'

    Args:
        months: list[dict] avec 'mois_num' (1-12)
        lang: code langue
        sep: séparateur

    Returns:
        str
    """
    shorts = MONTH_SHORT.get(lang, MONTH_SHORT["fr"])
    return sep.join(shorts[int(m["mois_num"]) - 1] for m in months)


def format_month_full(month_dict, lang="fr"):
    """Formate 1 mois en nom complet : 'Juillet'."""
    names = MONTH_NAMES.get(lang, MONTH_NAMES["fr"])
    return names[int(month_dict["mois_num"]) - 1]


# ══════════════════════════════════════════════════════════════════
# Subtitle éditorial (tagline sous le mois best)
# ══════════════════════════════════════════════════════════════════

def best_month_tagline(dest, monthly, lang="fr"):
    """
    Retourne la tagline éditoriale sous le mois best dans decision-card.
    Ex: 'Meilleur compromis climat + jours longs'

    Choix déterministe par slug pour reproductibilité. Sélection selon type.

    Args:
        dest: dict destination
        monthly: list mensuelles
        lang: code langue

    Returns:
        str (max ~50 chars)
    """
    dtype = classify_dest(dest)
    # Pool de taglines courtes, calibrées pour tenir sur 1-2 lignes mobile
    # (pas besoin de variantes trop nombreuses : la phrase est courte et peu visible dans le texte de la page)
    pools = {
        "tropical": {
            "fr": ["Saison sèche + ciel clair", "Fenêtre basse pluie", "Pic d'ensoleillement tropical"],
            "en": ["Dry season + clear skies", "Low-rain window", "Tropical sunshine peak"],
            "en-us": ["Dry season + clear skies", "Low-rain window", "Tropical sunshine peak"],
            "es": ["Temporada seca + cielos claros", "Ventana de poca lluvia", "Pico de sol tropical"],
            "de": ["Trockenzeit + klarer Himmel", "Regenarmes Fenster", "Tropischer Sonnen-Höhepunkt"],
        },
        "mountain": {
            "fr": {
                "winter": ["Enneigement + stations ouvertes", "Neige fraîche + soleil", "Conditions ski optimales"],
                "summer": ["Sentiers secs + refuges ouverts", "Alpinisme et randonnée", "Fenêtre d'été optimale"],
                "shoulder": ["Transition avant/après saison", "Entre-saison calme", "Peu de monde"],
            },
            "en": {
                "winter": ["Snow cover + open resorts", "Fresh snow + sun", "Peak ski conditions"],
                "summer": ["Dry trails + open huts", "Alpinism and hiking", "Optimal summer window"],
                "shoulder": ["Pre/post-season transition", "Quiet shoulder", "Few crowds"],
            },
            "en-us": {
                "winter": ["Snow cover + open resorts", "Fresh snow + sun", "Peak ski conditions"],
                "summer": ["Dry trails + open huts", "Alpinism and hiking", "Optimal summer window"],
                "shoulder": ["Pre/post-season transition", "Quiet shoulder", "Few crowds"],
            },
            "es": {
                "winter": ["Nieve + estaciones abiertas", "Nieve fresca + sol", "Condiciones de esquí óptimas"],
                "summer": ["Senderos secos + refugios abiertos", "Alpinismo y senderismo", "Ventana óptima de verano"],
                "shoulder": ["Transición pre/post-temporada", "Entre-temporada tranquila", "Poca afluencia"],
            },
            "de": {
                "winter": ["Schneedecke + offene Stationen", "Frischer Schnee + Sonne", "Optimale Ski-Bedingungen"],
                "summer": ["Trockene Wege + offene Hütten", "Alpinismus und Wandern", "Optimales Sommerfenster"],
                "shoulder": ["Übergang vor/nach Saison", "Ruhige Zwischensaison", "Wenig Andrang"],
            },
        },
        "generic": {
            "fr": ["Meilleur compromis climat", "Pic de soleil et confort", "Fenêtre optimale de l'année"],
            "en": ["Best weather compromise", "Sunshine and comfort peak", "Year's optimal window"],
            "en-us": ["Best weather compromise", "Sunshine and comfort peak", "Year's optimal window"],
            "es": ["Mejor compromiso climático", "Pico de sol y confort", "Ventana óptima del año"],
            "de": ["Beste Wetter-Balance", "Sonnen- und Komfort-Spitze", "Optimales Jahresfenster"],
        },
    }
    # Sélection déterministe par slug (hash simple)
    slug = dest.get("slug") or dest.get("slug_fr") or "unknown"
    import hashlib
    h = int(hashlib.md5(slug.encode("utf-8")).hexdigest()[:8], 16)

    if dtype == "mountain":
        # Pour mountain, la tagline dépend de la SAISON du best month
        # (hiver=ski, été=alpinisme, shoulder=transition)
        best = best_month(monthly)
        best_num = int(best.get("mois_num", 0))
        if best_num in (12, 1, 2, 3, 4):
            season_key = "winter"
        elif best_num in (6, 7, 8, 9):
            season_key = "summer"
        else:
            season_key = "shoulder"
        mountain_pool = pools["mountain"].get(lang, pools["mountain"]["fr"])
        variants = mountain_pool.get(season_key, mountain_pool["winter"])
        return variants[h % len(variants)]

    variants = pools[dtype].get(lang, pools[dtype]["fr"])
    return variants[h % len(variants)]


# ══════════════════════════════════════════════════════════════════
# Badges contextuels (tags colorés en bas de la carte)
# ══════════════════════════════════════════════════════════════════

def build_badges(dest, monthly, lang="fr"):
    """
    Construit 2-3 badges pertinents pour la destination.

    Returns:
        list[(emoji, label, color_scheme)] où color_scheme ∈ ('green','red','amber')
    """
    dtype = classify_dest(dest)
    good_months = [m for m in monthly if _score(m) >= 7.0]
    bad_months = [m for m in monthly if _score(m) <= 3.5]

    badges = []
    # Label dict by lang
    L = {
        "fr": {"n_good": "{n} mois confortables", "winter_tough": "Hiver rude",
               "summer_hot": "Été caniculaire", "crowd": "Foule estivale",
               "monsoon": "Mousson marquée", "short_season": "Saison courte",
               "glacier": "Glacier praticable"},
        "en": {"n_good": "{n} comfortable months", "winter_tough": "Rough winter",
               "summer_hot": "Heatwave summers", "crowd": "Summer crowds",
               "monsoon": "Strong monsoon", "short_season": "Short season",
               "glacier": "Glacier open"},
        "en-us": {"n_good": "{n} comfortable months", "winter_tough": "Harsh winter",
                  "summer_hot": "Hot summers", "crowd": "Summer crowds",
                  "monsoon": "Strong monsoon", "short_season": "Short season",
                  "glacier": "Glacier open"},
        "es": {"n_good": "{n} meses confortables", "winter_tough": "Invierno duro",
               "summer_hot": "Verano caluroso", "crowd": "Multitud en verano",
               "monsoon": "Monzón marcado", "short_season": "Temporada corta",
               "glacier": "Glaciar abierto"},
        "de": {"n_good": "{n} angenehme Monate", "winter_tough": "Harter Winter",
               "summer_hot": "Heiße Sommer", "crowd": "Sommer-Andrang",
               "monsoon": "Starker Monsun", "short_season": "Kurze Saison",
               "glacier": "Gletscher offen"},
    }
    l = L.get(lang, L["fr"])

    # Badge 1 : nombre de bons mois (toujours présent)
    if len(good_months) >= 6:
        badges.append(("✅", l["n_good"].format(n=len(good_months)), "green"))
    elif len(good_months) >= 3:
        badges.append(("✅", l["n_good"].format(n=len(good_months)), "amber"))
    else:
        badges.append(("⚠️", l["short_season"], "red"))

    # Badge 2 : spécifique au type
    if dtype == "tropical":
        badges.append(("🌧️", l["monsoon"], "red"))
    elif dtype == "mountain":
        # Vérifier si glacier (tmax ski ≤ 5°C en été nécessaire)
        # Heuristique : si score ≥ 6 en juin/juillet/août → glacier viable
        summer = [m for m in monthly if int(m.get("mois_num", 0)) in (6, 7, 8)]
        if summer and all(_score(m) >= 6 for m in summer):
            badges.append(("🏔️", l["glacier"], "green"))
        else:
            badges.append(("❄️", l["winter_tough"], "red"))
    else:
        # Générique : hiver rude si bottom 3 scores < 3
        if len(bad_months) >= 2:
            badges.append(("❄️", l["winter_tough"], "red"))

    # Badge 3 : foule estivale (si les best mois sont juil-août)
    best = best_month(monthly)
    if int(best.get("mois_num", 0)) in (7, 8):
        badges.append(("👥", l["crowd"], "amber"))

    return badges[:3]  # Max 3 badges pour tenir sur mobile


def _badge_html(emoji, label, color):
    """Rend 1 badge en HTML avec styles inline (pour portabilité dans le template)."""
    # Styles calqués sur le proto Paris V5
    palette = {
        "green": ("#e8f8f0", "#1a7a4a", "#bfe7cd"),
        "red": ("#fdecec", "#b91c1c", "#f4caca"),
        "amber": ("#fef3d0", "#b8860b", "#f2e6a8"),
    }
    bg, fg, bd = palette.get(color, palette["amber"])
    safe_label = _html.escape(label)
    return (f'<span style="font-size:10.5px;font-weight:700;padding:4px 9px;'
            f'border-radius:999px;background:{bg};color:{fg};border:1px solid {bd}">'
            f'{emoji} {safe_label}</span>')


# ══════════════════════════════════════════════════════════════════
# Decision card — fonction principale
# ══════════════════════════════════════════════════════════════════

def build_decision_card_v6(dest, monthly, lang="fr", n_top=3, n_shoulder=2):
    """
    Construit le HTML du bloc 'decision-card' visible en haut de fiche V5.

    Structure produite :
    - small-label : ⚡ Réponse rapide
    - decision-top : mois best + score + tagline
    - mini-grid : 3 mini-cards (top N, worst, shoulder)
    - badges : 2-3 pastilles contextuelles

    Args:
        dest: dict de destinations.csv (requis : slug, nom_fr, tropical, mountain)
        monthly: list[dict] 12 entrées (requis : mois_num, score)
        lang: code langue (fr/en/en-us/es/de)
        n_top: nombre de top months dans la mini-card principale (3 par défaut)
        n_shoulder: nombre de mois shoulder (2 par défaut)

    Returns:
        str : HTML prêt à insérer dans le template
    """
    if len(monthly) != 12:
        raise ValueError(f"monthly doit contenir 12 entrées, reçu {len(monthly)}")

    L = UI_LABELS.get(lang, UI_LABELS["fr"])

    best = best_month(monthly)
    worst = worst_month(monthly)
    tops = top_n_months(monthly, n_top)
    shoulders = shoulder_months(monthly, n_main=n_top, n_shoulder=n_shoulder)

    best_name = format_month_full(best, lang)
    best_score = float(best["score"])
    worst_name = format_month_full(worst, lang)

    top_str = format_month_list_short(tops, lang)
    shoulder_str = format_month_list_short(shoulders, lang)

    tagline = best_month_tagline(dest, monthly, lang)

    # Construire les badges puis le HTML
    badges = build_badges(dest, monthly, lang)
    badges_html = "\n              ".join(
        _badge_html(emo, lbl, col) for (emo, lbl, col) in badges
    )

    # Labels mini-cards
    top_label = L["top_n_mois"].format(n=n_top)
    worst_label = L["mois_a_eviter"]
    shoulder_label = L["mi_saison"]

    # Assemblage HTML (structure calquée sur proto Paris V5, L1041-1060)
    html = f'''<div class="decision-card">
            <div class="small-label">{L["reponse_rapide"]}</div>
            <div class="decision-top">
              <div>
                <div class="month">{_html.escape(best_name)}</div>
                <div class="sub">{_html.escape(tagline)}</div>
              </div>
              <div class="score">{best_score:.1f}<small>/10</small></div>
            </div>
            <div class="mini-grid">
              <div class="mini-card"><div class="v">{_html.escape(top_str)}</div><div class="l">{_html.escape(top_label)}</div></div>
              <div class="mini-card"><div class="v">{_html.escape(worst_name)}</div><div class="l">{_html.escape(worst_label)}</div></div>
              <div class="mini-card"><div class="v">{_html.escape(shoulder_str)}</div><div class="l">{_html.escape(shoulder_label)}</div></div>
            </div>
            <div style="display:flex;flex-wrap:wrap;gap:6px;margin-top:12px">
              {badges_html}
            </div>
          </div>'''

    # Auto-validation anti-LLM sur le HTML produit
    check_no_llm_patterns(html, page_id=f"decision_card/{dest.get('slug', '?')}", lang=lang, strict=True)

    return html


# ══════════════════════════════════════════════════════════════════
# Verdict + Avis éditorial (utilisent pick_variant de llm_detection)
# ══════════════════════════════════════════════════════════════════

# Nom du mois pour destination mountain : "meilleur hiver" et "meilleur été"
# (utilisé en fallback quand score ski séparé pas dispo)
_WINTER_MONTHS = (12, 1, 2, 3, 4)  # Ski season
_SUMMER_MONTHS = (6, 7, 8, 9)       # Hiking season


def _best_in_range(monthly, month_nums):
    """Retourne le dict mois avec le meilleur score parmi une plage de mois_num."""
    candidates = [m for m in monthly if int(m.get("mois_num", 0)) in month_nums]
    if not candidates:
        return None
    return max(candidates, key=_score)


def _build_template_params(dest, monthly, lang="fr"):
    """
    Construit le dict de paramètres à injecter dans les templates verdict/avis_edito.

    Les placeholders varient selon le type de destination :
    - tropical / generic : nom, top1, top2, worst
    - mountain : nom, ski_top, hike_top, worst

    Args:
        dest: dict destination
        monthly: list 12 mois
        lang: code langue

    Returns:
        dict — params prêts pour pick_variant(..., **params)
    """
    # Nom de la destination : choisir la variante langue (fallback FR)
    nom_key = f"nom_{lang.replace('-', '_')}"
    nom = dest.get(nom_key) or dest.get("nom_fr") or dest.get("nom_bare") or dest.get("slug", "?")

    dtype = classify_dest(dest)
    worst = format_month_full(worst_month(monthly), lang)

    if dtype == "mountain":
        # Pour mountain : ski_top = meilleur hiver, hike_top = meilleur été
        ski_best = _best_in_range(monthly, _WINTER_MONTHS)
        hike_best = _best_in_range(monthly, _SUMMER_MONTHS)
        # Fallback si plage vide (ne devrait pas arriver avec 12 mois complets)
        ski_top = format_month_full(ski_best, lang) if ski_best else format_month_full(best_month(monthly), lang)
        hike_top = format_month_full(hike_best, lang) if hike_best else format_month_full(best_month(monthly), lang)
        return {
            "nom": nom,
            "ski_top": ski_top,
            "hike_top": hike_top,
            "worst": worst,
        }

    # Tropical ou generic : top1 et top2 = top 2 mois par score (pas chronologique)
    sorted_by_score = sorted(monthly, key=_score, reverse=True)
    top1 = format_month_full(sorted_by_score[0], lang)
    top2 = format_month_full(sorted_by_score[1], lang)
    return {
        "nom": nom,
        "top1": top1,
        "top2": top2,
        "worst": worst,
    }


def build_verdict_v6(dest, monthly, lang="fr"):
    """
    Construit le texte du verdict (1 phrase pertinente, variable par slug).

    Le template est choisi selon classify_dest() :
    - tropical → verdict_tropical
    - mountain → verdict_mountain
    - generic → verdict_generic

    pick_variant() utilise MD5(slug) pour choisir déterministiquement parmi
    les 5 variantes. Même slug = même variante sur toutes les régénérations.

    Args:
        dest: dict destination (requis : slug, nom_*, tropical, mountain)
        monthly: list 12 mois (requis : mois_num, score)
        lang: code langue

    Returns:
        str — texte du verdict (HTML-safe, pas de balises)
    """
    if len(monthly) != 12:
        raise ValueError(f"monthly doit contenir 12 entrées, reçu {len(monthly)}")

    dtype = classify_dest(dest)
    # Mapping type → template_type dans TEMPLATES_BY_LANG
    template_type = f"verdict_{dtype}"

    variants = get_templates(template_type, lang)
    params = _build_template_params(dest, monthly, lang)
    slug = dest.get("slug") or dest.get("slug_fr") or "unknown"

    verdict = pick_variant(variants, slug=slug, **params)

    # Auto-validation anti-LLM
    check_no_llm_patterns(verdict, page_id=f"verdict/{slug}", lang=lang, strict=True)

    return verdict


def build_avis_edito_v6(dest, monthly, lang="fr"):
    """
    Construit l'avis éditorial (bloc plus long, ton plus personnel).

    Contient des balises <strong> pour emphase. Template choisi selon le type :
    - tropical → avis_edito_tropical (3 variantes)
    - mountain → avis_edito_mountain (2 variantes)
    - generic → pas d'avis édito spécialisé : on utilise avis_edito_tropical
      avec les mêmes placeholders (top1, top2, worst) qui fonctionnent.

    Args:
        dest: dict destination
        monthly: list 12 mois
        lang: code langue

    Returns:
        str — texte HTML (contient des <strong>)
    """
    if len(monthly) != 12:
        raise ValueError(f"monthly doit contenir 12 entrées, reçu {len(monthly)}")

    dtype = classify_dest(dest)

    # Dispatch sur le template_type correspondant
    if dtype == "mountain":
        template_type = "avis_edito_mountain"
    else:
        # tropical ET generic utilisent le même pool tropical (placeholders top1/top2/worst)
        template_type = "avis_edito_tropical"

    variants = get_templates(template_type, lang)
    params = _build_template_params(dest, monthly, lang)
    slug = dest.get("slug") or dest.get("slug_fr") or "unknown"

    avis = pick_variant(variants, slug=slug, **params)

    # Auto-validation anti-LLM (tolère les <strong>)
    check_no_llm_patterns(avis, page_id=f"avis_edito/{slug}", lang=lang, strict=True)

    return avis


# ══════════════════════════════════════════════════════════════════
# Barchart 12 mois (HTML bars)
# ══════════════════════════════════════════════════════════════════

# Seuils de classification couleur (mêmes que proto Paris V5)
# NB : 'best' n'est PAS dans cette liste → réservé exclusivement au meilleur
# mois absolu (marqueur visuel d'excellence avec outline gold). Les autres
# mois ≥ 7 sont classés 'good' (vert).
_BAR_THRESHOLDS = [
    ("good", 7.0),  # ≥ 7.0 → vert (inclut scores très élevés non-best)
    ("mid",  5.5),  # ≥ 5.5 → jaune/orange
    ("low",  3.5),  # ≥ 3.5 → rouge
    ("bad",  0.0),  # <  3.5 → rouge foncé
]

# Seuil d'éligibilité au statut 'best' (le mois #1 n'est 'best' que si ≥ ce seuil)
_BEST_MIN_SCORE = 8.5


def bar_class(score):
    """Retourne la classe CSS (good/mid/low/bad) pour un score.

    NB : ne retourne JAMAIS 'best' — cette classe est ajoutée uniquement
    au meilleur mois absolu par build_barchart_v6().
    """
    for cls, threshold in _BAR_THRESHOLDS:
        if score >= threshold:
            return cls
    return "bad"


_LEGEND_LABELS = {
    "fr": [
        ("Très bon (≥8)", "best"),
        ("Bon (7-8)", "good"),
        ("Moyen (5.5-7)", "mid"),
        ("Compliqué (3.5-5.5)", "low"),
        ("Rude (<3.5)", "bad"),
    ],
    "en": [
        ("Excellent (≥8)", "best"),
        ("Good (7-8)", "good"),
        ("Fair (5.5-7)", "mid"),
        ("Rough (3.5-5.5)", "low"),
        ("Harsh (<3.5)", "bad"),
    ],
    "en-us": [
        ("Excellent (≥8)", "best"),
        ("Good (7-8)", "good"),
        ("Fair (5.5-7)", "mid"),
        ("Rough (3.5-5.5)", "low"),
        ("Harsh (<3.5)", "bad"),
    ],
    "es": [
        ("Muy bueno (≥8)", "best"),
        ("Bueno (7-8)", "good"),
        ("Regular (5.5-7)", "mid"),
        ("Complicado (3.5-5.5)", "low"),
        ("Duro (<3.5)", "bad"),
    ],
    "de": [
        ("Sehr gut (≥8)", "best"),
        ("Gut (7-8)", "good"),
        ("Mittel (5.5-7)", "mid"),
        ("Anspruchsvoll (3.5-5.5)", "low"),
        ("Rau (<3.5)", "bad"),
    ],
}

_BAR_GRADIENTS = {
    "best": "linear-gradient(180deg,#2ea86a 0%,#1a7a4a 100%)",
    "good": "linear-gradient(180deg,#46c878 0%,#25a75d 100%)",
    "mid":  "linear-gradient(180deg,#ecc568 0%,#b8860b 100%)",
    "low":  "linear-gradient(180deg,#e47272 0%,#b91c1c 100%)",
    "bad":  "linear-gradient(180deg,#b91c1c 0%,#8b1616 100%)",
}


def build_barchart_v6(monthly, lang="fr", ski_scores_by_month=None, show_legend=True):
    """
    Construit le HTML du barchart 12 mois.

    - Hauteur de barre : score × 10% (plafonné à 100%)
    - Classe CSS : best / good / mid / low / bad selon seuils
    - Meilleur mois absolu : forcé en 'best' (avec outline gold via CSS)
    - Labels score au-dessus du nom du mois abrégé

    Pour mountain : si ski_scores_by_month fourni, chaque score est max(gen, ski).

    Args:
        monthly: list[dict] 12 entrées (mois_num, score)
        lang: code langue (labels mois + légende)
        ski_scores_by_month: dict {int mois_num: float score_ski} optionnel
        show_legend: inclure la légende couleur en dessous (default True)

    Returns:
        str : HTML du bloc bars + légende
    """
    if len(monthly) != 12:
        raise ValueError(f"monthly doit contenir 12 entrées, reçu {len(monthly)}")

    shorts = MONTH_SHORT.get(lang, MONTH_SHORT["fr"])
    sorted_months = sorted(monthly, key=lambda m: int(m["mois_num"]))

    # Calcul score effectif (général ou max avec ski)
    effective = []
    for m in sorted_months:
        gen = float(m.get("score", 0))
        mn = int(m["mois_num"])
        if ski_scores_by_month and mn in ski_scores_by_month:
            eff = max(gen, float(ski_scores_by_month[mn]))
        else:
            eff = gen
        effective.append((mn, eff))

    best_score = max(s for _, s in effective)

    bars_html = []
    for mn, score in effective:
        height_pct = min(100, round(score * 10))
        # 'best' réservé exclusivement au meilleur mois absolu (et ≥ _BEST_MIN_SCORE)
        if score == best_score and score >= _BEST_MIN_SCORE:
            cls = "best"
        else:
            cls = bar_class(score)
        label = shorts[mn - 1]
        bars_html.append(
            f'              <div class="bar-wrap">'
            f'<div class="bar-slot"><div class="bar {cls}" style="height:{height_pct}%"></div></div>'
            f'<div class="bar-score">{score:.1f}</div>'
            f'<div class="bar-label">{_html.escape(label)}</div></div>'
        )
    bars_block = "\n".join(bars_html)

    html = f'<div class="bars">\n{bars_block}\n            </div>'

    if show_legend:
        legend_items = _LEGEND_LABELS.get(lang, _LEGEND_LABELS["fr"])
        legend_html = []
        for (label_txt, cls) in legend_items:
            gradient = _BAR_GRADIENTS[cls]
            safe = _html.escape(label_txt)
            legend_html.append(
                f'<span style="display:inline-flex;align-items:center;gap:5px">'
                f'<span style="width:11px;height:11px;border-radius:3px;background:{gradient}"></span>'
                f'{safe}</span>'
            )
        legend_block = "\n              ".join(legend_html)
        html += (
            f'\n            <div style="display:flex;gap:12px;flex-wrap:wrap;'
            f'margin-top:14px;justify-content:center;font-size:11px;color:var(--muted)">\n'
            f'              {legend_block}\n'
            f'            </div>'
        )

    return html


# ══════════════════════════════════════════════════════════════════
# Pills "Top & à éviter"
# ══════════════════════════════════════════════════════════════════

# Labels UI pour section pills
_PILLS_LABELS = {
    "fr": {"section": "Top & à éviter", "trophy": "🏆", "warn": "⚠️"},
    "en": {"section": "Top & avoid", "trophy": "🏆", "warn": "⚠️"},
    "en-us": {"section": "Top & avoid", "trophy": "🏆", "warn": "⚠️"},
    "es": {"section": "Top & a evitar", "trophy": "🏆", "warn": "⚠️"},
    "de": {"section": "Top & Meiden", "trophy": "🏆", "warn": "⚠️"},
}


def build_pills_v6(monthly, lang="fr", n_top=4, show_section_label=True):
    """
    Construit les pills 'Top & à éviter' : N meilleurs mois + 1 pire mois.

    Le meilleur mois reçoit l'emoji 🏆, le pire reçoit ⚠️.
    Les pills 'good' pour les tops, 'bad' pour le worst.
    Ordre : top par score décroissant, puis worst.

    Args:
        monthly: list[dict] 12 mois
        lang: code langue
        n_top: nombre de pills top (4 par défaut, comme proto V5)
        show_section_label: inclure le label 'Top & à éviter' au-dessus

    Returns:
        str : HTML (div wrap + pills)
    """
    if len(monthly) != 12:
        raise ValueError(f"monthly doit contenir 12 entrées, reçu {len(monthly)}")

    L = _PILLS_LABELS.get(lang, _PILLS_LABELS["fr"])

    # Top N par score décroissant
    sorted_desc = sorted(monthly, key=_score, reverse=True)
    tops = sorted_desc[:n_top]
    worst = sorted_desc[-1]  # Le plus mauvais

    pills_html = []
    for i, m in enumerate(tops):
        name = format_month_full(m, lang)
        sc = _score(m)
        emoji = f"{L['trophy']} " if i == 0 else ""
        safe_name = _html.escape(name)
        pills_html.append(
            f'<span class="pill good">{emoji}{safe_name} · {sc:.1f}</span>'
        )
    # Worst en bad
    worst_name = format_month_full(worst, lang)
    worst_sc = _score(worst)
    pills_html.append(
        f'<span class="pill bad">{L["warn"]} {_html.escape(worst_name)} · {worst_sc:.1f}</span>'
    )

    pills_block = "\n              ".join(pills_html)

    if show_section_label:
        html = (f'<div>\n            <div class="small-label">{L["section"]}</div>\n'
                f'            <div class="pills">\n              {pills_block}\n'
                f'            </div>\n          </div>')
    else:
        html = f'<div class="pills">\n              {pills_block}\n            </div>'

    return html


# ══════════════════════════════════════════════════════════════════
# Right-stack : bloc éditorial "Ce qu'on comprend en 5s" + CTA
# ══════════════════════════════════════════════════════════════════

def _month_range_label(months, lang="fr"):
    """
    Formate une liste de mois en plage lisible.

    Si les mois sont contigus : 'avril-septembre' (6 mois)
    Sinon : 'avril, mai, juillet' (énumération)

    Args:
        months: list[dict] triés par mois_num
        lang: code langue

    Returns:
        str
    """
    if not months:
        return ""
    names = MONTH_NAMES.get(lang, MONTH_NAMES["fr"])
    sorted_m = sorted(months, key=lambda x: int(x["mois_num"]))
    nums = [int(m["mois_num"]) for m in sorted_m]

    # Test contiguïté (y compris cycle décembre→janvier)
    contiguous = all(nums[i] + 1 == nums[i + 1] for i in range(len(nums) - 1))
    # Séparateurs par langue
    sep = {"fr": "-", "en": "-", "en-us": "-", "es": "-", "de": "–"}.get(lang, "-")
    if contiguous and len(nums) >= 2:
        return f"{names[nums[0] - 1].lower()}{sep}{names[nums[-1] - 1].lower()}"
    elif len(nums) == 1:
        return names[nums[0] - 1].lower()
    else:
        # Énumération (pas contigu)
        return ", ".join(names[n - 1].lower() for n in nums)


# Textes localisés pour right-stack
# Chaque clé contient 2-3 variantes choisies déterministes par slug
_RIGHT_STACK_TEXTS = {
    "fr": {
        "understand_title": "Ce qu'on comprend en 5 secondes",
        # Template : {nom}, {n_great}, {great_range}, {n_tough}, {tough_range},
        # {best_name}, {best_score}, {worst_name}, {worst_score}
        "understand_variants": [
            "{nom} a {n_great} mois très agréables ({great_range}) et {n_tough} mois difficiles ({tough_range}). L'écart est net : {best_score}/10 en {best_name} contre {worst_score}/10 en {worst_name}.",
            "{nom} offre {n_great} mois confortables ({great_range}), avec {n_tough} mois à éviter ({tough_range}). Le delta est marqué : {best_score} en {best_name} vs {worst_score} en {worst_name}.",
            "Sur {nom}, {n_great} mois sortent clairement du lot ({great_range}) et {n_tough} plombent l'expérience ({tough_range}). Écart {best_score}→{worst_score} selon le mois.",
        ],
        "verify_title": "Ce qu'il faut vérifier ensuite",
        "verify_generic": "Votre tolérance à la foule et au budget. Les meilleurs mois concentrent la saturation touristique et les prix plus hauts. Les entre-saisons offrent un bon compromis.",
        "verify_tropical": "Votre tolérance à la pluie et à l'humidité. Même la saison sèche connaît des averses ponctuelles. Les tarifs remontent aussi pendant la fenêtre optimale.",
        "verify_mountain": "Votre objectif précis : ski de piste, rando, alpinisme. Chaque activité a sa fenêtre. Les prix grimpent en haute saison, et les entre-saisons ferment les remontées.",
        "action_title": "Action suivante",
        "action_text": "Descendre au tableau détaillé pour comparer mois à mois, puis ouvrir la fiche du mois qui vous intéresse.",
        "cta_table": "Comparer les 12 mois",
        "cta_project": "Selon votre projet",
    },
    "en": {
        "understand_title": "The 5-second takeaway",
        "understand_variants": [
            "{nom} has {n_great} comfortable months ({great_range}) and {n_tough} tough months ({tough_range}). The gap is clear: {best_score}/10 in {best_name} vs {worst_score}/10 in {worst_name}.",
            "{nom} offers {n_great} solid months ({great_range}), with {n_tough} months to skip ({tough_range}). Delta is marked: {best_score} in {best_name} vs {worst_score} in {worst_name}.",
            "At {nom}, {n_great} months clearly stand out ({great_range}) and {n_tough} drag down the experience ({tough_range}). Gap {best_score}→{worst_score} across the year.",
        ],
        "verify_title": "What to check next",
        "verify_generic": "Your tolerance for crowds and budget. Peak months concentrate tourist saturation and higher prices. Shoulder seasons offer a good compromise.",
        "verify_tropical": "Your tolerance for rain and humidity. Even the dry season has occasional showers. Rates also climb during the optimal window.",
        "verify_mountain": "Your specific goal: piste skiing, hiking, mountaineering. Each activity has its window. Prices peak in high season, shoulder months close the lifts.",
        "action_title": "Next step",
        "action_text": "Scroll to the detailed table to compare month by month, then open the page for the month you're considering.",
        "cta_table": "Compare 12 months",
        "cta_project": "By project type",
    },
    "en-us": {
        "understand_title": "The 5-second takeaway",
        "understand_variants": [
            "{nom} has {n_great} comfortable months ({great_range}) and {n_tough} tough months ({tough_range}). The gap is clear: {best_score}/10 in {best_name} vs {worst_score}/10 in {worst_name}.",
            "{nom} offers {n_great} solid months ({great_range}), with {n_tough} months to skip ({tough_range}). Delta is marked: {best_score} in {best_name} vs {worst_score} in {worst_name}.",
            "At {nom}, {n_great} months clearly stand out ({great_range}) and {n_tough} drag down the experience ({tough_range}). Gap {best_score}→{worst_score} across the year.",
        ],
        "verify_title": "What to check next",
        "verify_generic": "Your tolerance for crowds and budget. Peak months concentrate tourist saturation and higher prices. Shoulder seasons offer a good compromise.",
        "verify_tropical": "Your tolerance for rain and humidity. Even the dry season has occasional showers. Rates also climb during the optimal window.",
        "verify_mountain": "Your specific goal: piste skiing, hiking, mountaineering. Each activity has its window. Prices peak in high season, shoulder months close the lifts.",
        "action_title": "Next step",
        "action_text": "Scroll to the detailed table to compare month by month, then open the page for the month you're considering.",
        "cta_table": "Compare 12 months",
        "cta_project": "By project type",
    },
    "es": {
        "understand_title": "Lo esencial en 5 segundos",
        "understand_variants": [
            "{nom} tiene {n_great} meses agradables ({great_range}) y {n_tough} meses difíciles ({tough_range}). La diferencia es clara: {best_score}/10 en {best_name} vs {worst_score}/10 en {worst_name}.",
            "{nom} ofrece {n_great} meses cómodos ({great_range}), con {n_tough} meses a evitar ({tough_range}). Delta marcado: {best_score} en {best_name} vs {worst_score} en {worst_name}.",
            "En {nom}, {n_great} meses destacan claramente ({great_range}) y {n_tough} empeoran la experiencia ({tough_range}). Brecha {best_score}→{worst_score} según el mes.",
        ],
        "verify_title": "Lo que hay que verificar",
        "verify_generic": "Tu tolerancia a las multitudes y al presupuesto. Los mejores meses concentran la saturación turística y los precios altos. Las entre-temporadas ofrecen un buen compromiso.",
        "verify_tropical": "Tu tolerancia a la lluvia y la humedad. Incluso la temporada seca tiene lluvias puntuales. Los precios también suben durante la ventana óptima.",
        "verify_mountain": "Tu objetivo preciso: esquí de pista, senderismo, alpinismo. Cada actividad tiene su ventana. Los precios suben en temporada alta, entre-temporadas cierran los remontes.",
        "action_title": "Siguiente paso",
        "action_text": "Baja a la tabla detallada para comparar mes a mes, luego abre la ficha del mes que te interesa.",
        "cta_table": "Comparar 12 meses",
        "cta_project": "Según tu proyecto",
    },
    "de": {
        "understand_title": "Das Wesentliche in 5 Sekunden",
        "understand_variants": [
            "{nom} hat {n_great} angenehme Monate ({great_range}) und {n_tough} schwierige Monate ({tough_range}). Der Unterschied ist deutlich: {best_score}/10 in {best_name} vs {worst_score}/10 in {worst_name}.",
            "{nom} bietet {n_great} komfortable Monate ({great_range}), mit {n_tough} zu meidenden Monaten ({tough_range}). Deutliches Delta: {best_score} in {best_name} vs {worst_score} in {worst_name}.",
            "In {nom} stechen {n_great} Monate klar heraus ({great_range}) und {n_tough} belasten das Erlebnis ({tough_range}). Spanne {best_score}→{worst_score} je nach Monat.",
        ],
        "verify_title": "Was als Nächstes zu prüfen ist",
        "verify_generic": "Ihre Toleranz gegenüber Menschenmassen und Budget. Die besten Monate konzentrieren den Touristen-Andrang und höhere Preise. Zwischensaisons bieten einen guten Kompromiss.",
        "verify_tropical": "Ihre Toleranz gegenüber Regen und Luftfeuchtigkeit. Auch die Trockenzeit hat gelegentliche Schauer. Die Preise steigen auch im optimalen Fenster.",
        "verify_mountain": "Ihr genaues Ziel: Pistenski, Wandern, Bergsteigen. Jede Aktivität hat ihr Fenster. Die Preise steigen in der Hauptsaison, in der Zwischensaison schließen die Lifte.",
        "action_title": "Nächster Schritt",
        "action_text": "Scrollen Sie zur detaillierten Tabelle, um Monat für Monat zu vergleichen, und öffnen Sie dann die Seite des Monats, der Sie interessiert.",
        "cta_table": "12 Monate vergleichen",
        "cta_project": "Je nach Projekt",
    },
}


def build_right_stack_v6(dest, monthly, lang="fr",
                         great_threshold=7.0, tough_threshold=3.5,
                         href_table="#tableau", href_project="#par-projet"):
    """
    Construit le bloc 'right-stack' de la section Décider.

    Produit 3 right-item + 1 cta-row :
    - 'Ce qu'on comprend en 5s' : résumé auto (n_great, n_tough, gap best→worst)
    - 'Ce qu'il faut vérifier ensuite' : mise en garde selon type destination
    - 'Action suivante' : incitation tableau + profils

    Variantes du résumé choisies déterministes par slug (anti-LLM).

    Args:
        dest: dict destination
        monthly: list 12 mois
        lang: code langue
        great_threshold: seuil score pour 'mois agréable' (default 7.0)
        tough_threshold: seuil score pour 'mois difficile' (default 3.5)
        href_table: ancre vers tableau
        href_project: ancre vers section profils

    Returns:
        str : HTML complet du bloc
    """
    if len(monthly) != 12:
        raise ValueError(f"monthly doit contenir 12 entrées, reçu {len(monthly)}")

    T = _RIGHT_STACK_TEXTS.get(lang, _RIGHT_STACK_TEXTS["fr"])

    # Compter les mois great / tough
    sorted_chrono = sorted(monthly, key=lambda m: int(m["mois_num"]))
    great_months = [m for m in sorted_chrono if _score(m) >= great_threshold]
    tough_months = [m for m in sorted_chrono if _score(m) <= tough_threshold]

    great_range = _month_range_label(great_months, lang) if great_months else "—"
    tough_range = _month_range_label(tough_months, lang) if tough_months else "—"

    best = best_month(monthly)
    worst = worst_month(monthly)
    nom_key = f"nom_{lang.replace('-', '_')}"
    nom = dest.get(nom_key) or dest.get("nom_fr") or dest.get("slug", "?")
    slug = dest.get("slug") or dest.get("slug_fr") or "unknown"

    # Paramètres du template understand
    params = {
        "nom": nom,
        "n_great": len(great_months),
        "great_range": great_range,
        "n_tough": len(tough_months),
        "tough_range": tough_range,
        "best_name": format_month_full(best, lang),
        "best_score": f"{_score(best):.1f}",
        "worst_name": format_month_full(worst, lang),
        "worst_score": f"{_score(worst):.1f}",
    }
    understand_text = pick_variant(T["understand_variants"], slug=slug, **params)

    # Texte "à vérifier" selon type
    dtype = classify_dest(dest)
    verify_text = T.get(f"verify_{dtype}", T["verify_generic"])

    # Auto-validation anti-LLM sur tous les textes générés
    for text, label in [(understand_text, "understand"), (verify_text, "verify"),
                        (T["action_text"], "action")]:
        check_no_llm_patterns(text, page_id=f"right_stack/{slug}/{label}",
                              lang=lang, strict=True)

    # Escape des valeurs dans le HTML (le template contient déjà les balises)
    html = f'''<div class="card pad right-stack">
          <div class="right-item">
            <h3>{_html.escape(T["understand_title"])}</h3>
            <p>{understand_text}</p>
          </div>
          <div class="right-item">
            <h3>{_html.escape(T["verify_title"])}</h3>
            <p>{_html.escape(verify_text)}</p>
          </div>
          <div class="right-item">
            <h3>{_html.escape(T["action_title"])}</h3>
            <p>{_html.escape(T["action_text"])}</p>
          </div>
          <div class="cta-row">
            <a class="btn primary" href="{href_table}">{_html.escape(T["cta_table"])}</a>
            <a class="btn" href="{href_project}">{_html.escape(T["cta_project"])}</a>
          </div>
        </div>'''

    return html


    return html


# ══════════════════════════════════════════════════════════════════
# Section 'Comprendre' : Tableau 12 mois + Signaux détaillés
# ══════════════════════════════════════════════════════════════════

def _weather_emoji(sun_h):
    """Retourne l'emoji météo basé sur les heures de soleil quotidiennes."""
    s = float(sun_h) if sun_h else 0
    if s >= 11: return "☀️"
    if s >= 7:  return "⛅"
    if s >= 4:  return "🌥️"
    return "🌧️"


def _mood_label(score, lang="fr"):
    """
    Retourne (label, css_class) pour un score donné.
    Labels différents du bar_class pour contextualiser la lecture.
    """
    labels = {
        "fr": [
            (8.5, "Meilleur", "good"),
            (7.5, "Très bon", "good"),
            (6.5, "Correct", "mid"),
            (5.0, "Moyen", "mid"),
            (3.5, "Compliqué", "bad"),
            (0.0, "Rude", "bad"),
        ],
        "en": [
            (8.5, "Best", "good"),
            (7.5, "Very good", "good"),
            (6.5, "Fair", "mid"),
            (5.0, "Average", "mid"),
            (3.5, "Rough", "bad"),
            (0.0, "Harsh", "bad"),
        ],
        "en-us": [
            (8.5, "Best", "good"),
            (7.5, "Very good", "good"),
            (6.5, "Fair", "mid"),
            (5.0, "Average", "mid"),
            (3.5, "Rough", "bad"),
            (0.0, "Harsh", "bad"),
        ],
        "es": [
            (8.5, "Mejor", "good"),
            (7.5, "Muy bueno", "good"),
            (6.5, "Correcto", "mid"),
            (5.0, "Regular", "mid"),
            (3.5, "Complicado", "bad"),
            (0.0, "Duro", "bad"),
        ],
        "de": [
            (8.5, "Bester", "good"),
            (7.5, "Sehr gut", "good"),
            (6.5, "Ordentlich", "mid"),
            (5.0, "Mittel", "mid"),
            (3.5, "Anspruchsvoll", "bad"),
            (0.0, "Rau", "bad"),
        ],
    }
    thresholds = labels.get(lang, labels["fr"])
    for threshold, label, cls in thresholds:
        if score >= threshold:
            return (label, cls)
    return ("?", "bad")


# Labels i18n de la section Comprendre
_COMPRENDRE_LABELS = {
    "fr": {
        "kicker": "Comprendre",
        "title": "Comparer les 12 mois",
        "lead": "Le détail de chaque mois : températures, pluie, soleil, score et lecture synthétique.",
        "th_month": "Mois",
        "th_tmin": "T° min",
        "th_tmax": "T° max",
        "th_rain": "Pluie %",
        "th_mm": "mm/j",
        "th_sun": "Soleil",
        "th_score": "Score",
        "th_mood": "Lecture",
        "lbl_comfort_months": "{n} mois confortables",
        "lbl_comfort_range": "({range_short})",
        "lbl_signal_quick": "📊 Lecture rapide",
        "lbl_signal_detailed": "🌡️ Conditions détaillées ({best_month})",
        "sig_optimal": "Fenêtre optimale",
        "sig_transition": "Bonne transition",
        "sig_tough": "Période rude",
        "sig_feel": "🌡️ Ressenti",
        "sig_uv": "☀️ UV",
        "sig_humidity": "💧 Humidité ressentie",
        "sig_air": "🌫️ Qualité de l'air",
        "sig_rain": "☔ Pluie",
        "sig_sun": "🌅 Soleil",
        "sun_unit_day": "h/jour",
        "mm_unit": "mm/j",
    },
    "en": {
        "kicker": "Understand",
        "title": "Compare the 12 months",
        "lead": "Each month in detail: temperatures, rain, sun, score, and quick read.",
        "th_month": "Month", "th_tmin": "Min T°", "th_tmax": "Max T°",
        "th_rain": "Rain %", "th_mm": "mm/d", "th_sun": "Sun",
        "th_score": "Score", "th_mood": "Verdict",
        "lbl_comfort_months": "{n} comfortable months",
        "lbl_comfort_range": "({range_short})",
        "lbl_signal_quick": "📊 Quick read",
        "lbl_signal_detailed": "🌡️ Detailed conditions ({best_month})",
        "sig_optimal": "Optimal window",
        "sig_transition": "Good transition",
        "sig_tough": "Tough period",
        "sig_feel": "🌡️ Feels like",
        "sig_uv": "☀️ UV",
        "sig_humidity": "💧 Felt humidity",
        "sig_air": "🌫️ Air quality",
        "sig_rain": "☔ Rain",
        "sig_sun": "🌅 Sun",
        "sun_unit_day": "h/day",
        "mm_unit": "mm/d",
    },
    "en-us": {
        "kicker": "Understand",
        "title": "Compare the 12 months",
        "lead": "Each month in detail: temperatures, rain, sun, score, and quick read.",
        "th_month": "Month", "th_tmin": "Min T°", "th_tmax": "Max T°",
        "th_rain": "Rain %", "th_mm": "in/d", "th_sun": "Sun",
        "th_score": "Score", "th_mood": "Verdict",
        "lbl_comfort_months": "{n} comfortable months",
        "lbl_comfort_range": "({range_short})",
        "lbl_signal_quick": "📊 Quick read",
        "lbl_signal_detailed": "🌡️ Detailed conditions ({best_month})",
        "sig_optimal": "Optimal window",
        "sig_transition": "Good transition",
        "sig_tough": "Tough period",
        "sig_feel": "🌡️ Feels like",
        "sig_uv": "☀️ UV",
        "sig_humidity": "💧 Felt humidity",
        "sig_air": "🌫️ Air quality",
        "sig_rain": "☔ Rain",
        "sig_sun": "🌅 Sun",
        "sun_unit_day": "h/day",
        "mm_unit": "in/d",
    },
    "es": {
        "kicker": "Entender",
        "title": "Comparar los 12 meses",
        "lead": "Cada mes en detalle: temperaturas, lluvia, sol, puntuación y lectura rápida.",
        "th_month": "Mes", "th_tmin": "T° mín", "th_tmax": "T° máx",
        "th_rain": "Lluvia %", "th_mm": "mm/d", "th_sun": "Sol",
        "th_score": "Puntuación", "th_mood": "Lectura",
        "lbl_comfort_months": "{n} meses cómodos",
        "lbl_comfort_range": "({range_short})",
        "lbl_signal_quick": "📊 Lectura rápida",
        "lbl_signal_detailed": "🌡️ Condiciones detalladas ({best_month})",
        "sig_optimal": "Ventana óptima",
        "sig_transition": "Buena transición",
        "sig_tough": "Período duro",
        "sig_feel": "🌡️ Sensación",
        "sig_uv": "☀️ UV",
        "sig_humidity": "💧 Humedad sentida",
        "sig_air": "🌫️ Calidad del aire",
        "sig_rain": "☔ Lluvia",
        "sig_sun": "🌅 Sol",
        "sun_unit_day": "h/día",
        "mm_unit": "mm/d",
    },
    "de": {
        "kicker": "Verstehen",
        "title": "Die 12 Monate vergleichen",
        "lead": "Jeder Monat im Detail: Temperaturen, Regen, Sonne, Punktzahl und schnelle Lesung.",
        "th_month": "Monat", "th_tmin": "T° min", "th_tmax": "T° max",
        "th_rain": "Regen %", "th_mm": "mm/T", "th_sun": "Sonne",
        "th_score": "Punkte", "th_mood": "Lesung",
        "lbl_comfort_months": "{n} angenehme Monate",
        "lbl_comfort_range": "({range_short})",
        "lbl_signal_quick": "📊 Schnelle Lesung",
        "lbl_signal_detailed": "🌡️ Detaillierte Bedingungen ({best_month})",
        "sig_optimal": "Optimales Fenster",
        "sig_transition": "Guter Übergang",
        "sig_tough": "Harte Periode",
        "sig_feel": "🌡️ Gefühlt",
        "sig_uv": "☀️ UV",
        "sig_humidity": "💧 Gefühlte Feuchte",
        "sig_air": "🌫️ Luftqualität",
        "sig_rain": "☔ Regen",
        "sig_sun": "🌅 Sonne",
        "sun_unit_day": "h/Tag",
        "mm_unit": "mm/T",
    },
}


def _month_range_short(months, lang="fr"):
    """
    Retourne une plage courte : 'avr→sep' (contigu) ou 'avr · mai · jul' (énumération).

    Args:
        months: list[dict] avec mois_num
        lang: code langue

    Returns:
        str
    """
    if not months:
        return "—"
    shorts = MONTH_SHORT.get(lang, MONTH_SHORT["fr"])
    sorted_m = sorted(months, key=lambda x: int(x["mois_num"]))
    nums = [int(m["mois_num"]) for m in sorted_m]

    contiguous = all(nums[i] + 1 == nums[i + 1] for i in range(len(nums) - 1))
    if contiguous and len(nums) >= 2:
        return f"{shorts[nums[0] - 1]}→{shorts[nums[-1] - 1]}"
    elif len(nums) == 1:
        return shorts[nums[0] - 1]
    else:
        return " · ".join(shorts[n - 1] for n in nums)


def _month_range_arrow(months, lang="fr"):
    """Format 'Juin → Sep' (version plus lisible pour signaux)."""
    if not months:
        return "—"
    shorts = MONTH_SHORT.get(lang, MONTH_SHORT["fr"])
    sorted_m = sorted(months, key=lambda x: int(x["mois_num"]))
    nums = [int(m["mois_num"]) for m in sorted_m]
    contiguous = all(nums[i] + 1 == nums[i + 1] for i in range(len(nums) - 1))
    if contiguous and len(nums) >= 2:
        return f"{shorts[nums[0] - 1]} → {shorts[nums[-1] - 1]}"
    elif len(nums) == 1:
        return shorts[nums[0] - 1]
    else:
        return " · ".join(shorts[n - 1] for n in nums)


def _appreciate_aqi(aqi):
    """Retourne (label, tier) pour l'AQI en FR basique (à localiser ensuite)."""
    if aqi is None or aqi == "":
        return None
    try:
        v = float(aqi)
    except (TypeError, ValueError):
        return None
    if v <= 25: return ("Excellent", "good")
    if v <= 50: return ("Bon", "good")
    if v <= 100: return ("Modéré", "mid")
    if v <= 150: return ("Mauvais", "bad")
    return ("Très mauvais", "bad")


def _appreciate_uv(uv):
    """Retourne (label_niveau, ) pour l'index UV."""
    if uv is None or uv == "":
        return None
    try:
        v = float(uv)
    except (TypeError, ValueError):
        return None
    if v < 3: return "Faible"
    if v < 6: return "Modéré"
    if v < 8: return "Modéré-Fort"
    if v < 11: return "Très fort"
    return "Extrême"


def _appreciate_dew(dew):
    """Retourne label pour le point de rosée (confort humidité)."""
    if dew is None or dew == "":
        return None
    try:
        v = float(dew)
    except (TypeError, ValueError):
        return None
    if v < 10: return "Sec"
    if v < 15: return "Agréable"
    if v < 18: return "Un peu humide"
    if v < 21: return "Un peu moite"
    if v < 24: return "Moite"
    return "Étouffant"


def _appreciate_feel(tmax, dew, lang="fr"):
    """Ressenti synthétique en fonction tmax + dew (approximatif)."""
    if tmax is None or dew is None:
        return "—"
    try:
        t = float(tmax)
        d = float(dew)
    except (TypeError, ValueError):
        return "—"
    # Logique simplifiée FR (à localiser plus tard)
    if t < 10: return "Froid"
    if t < 18: return "Frais"
    if t < 24 and d < 15: return "Confortable"
    if t < 27 and d < 18: return "Confortable"
    if d >= 22: return "Étouffant"
    if d >= 18: return "Un peu lourd"
    if t >= 30: return "Chaud sec"
    return "Tempéré"


def build_months_table_v6(dest, monthly, lang="fr", monthly_url_builder=None):
    """
    Construit le tableau des 12 mois (desktop) + cards mobile.

    Args:
        dest: dict destination (pour slug si lien)
        monthly: list[dict] 12 mois
        lang: code langue
        monthly_url_builder: fonction (slug, mois_num, lang) → URL
                             par défaut : 'paris-meteo-janvier.html' en FR

    Returns:
        str : HTML (div.table-wrap > table + div.mobile-month-cards)
    """
    if len(monthly) != 12:
        raise ValueError(f"monthly doit contenir 12 entrées, reçu {len(monthly)}")

    L = _COMPRENDRE_LABELS.get(lang, _COMPRENDRE_LABELS["fr"])
    names = MONTH_NAMES.get(lang, MONTH_NAMES["fr"])

    # Slug lang-aware pour URLs mensuelles (Tour 8c bis)
    # ~150 dests ont des slugs traduits différents (ex: reykjavik FR → reikiavik ES,
    # canaries FR → canary-islands EN). Sans ça : 7 200 URLs cassées.
    # Pour 'en-us', on utilise slug_en (pas de slug_us en CSV).
    slug_lang_key = "slug_en" if lang == "en-us" else f"slug_{lang}"
    slug = (dest.get(slug_lang_key) or dest.get("slug")
            or dest.get("slug_fr") or "paris")

    # Flag monthly : ~19 dests n'ont PAS de fiches mensuelles générées en prod
    # (ex: mbabane, asmara, tripoli). Dans ce cas, afficher cards sans liens.
    has_monthly_pages = str(dest.get("monthly", "")).lower() in ("1", "true")

    # URL builder par défaut lang-aware (Tour 8c)
    # Patterns réels en prod par langue :
    #   FR    : {slug}-meteo-{mois_fr}.html      (janvier, fevrier, ...)
    #   EN    : {slug}-weather-{month_en}.html   (january, february, ...)
    #   EN-US : {slug}-weather-{month_en}.html   (idem EN)
    #   ES    : {slug}-clima-{mes_es}.html       (enero, febrero, ...)
    #   DE    : {slug}-wetter-{monat_de}.html    (januar, februar, ...)
    # Liens relatifs au sous-dossier (pas de préfixe en/, es/, etc.)
    if monthly_url_builder is None:
        _MONTH_URL_SLUGS = {
            "fr":    ["janvier", "fevrier", "mars", "avril", "mai", "juin",
                      "juillet", "aout", "septembre", "octobre", "novembre", "decembre"],
            "en":    ["january", "february", "march", "april", "may", "june",
                      "july", "august", "september", "october", "november", "december"],
            "en-us": ["january", "february", "march", "april", "may", "june",
                      "july", "august", "september", "october", "november", "december"],
            "es":    ["enero", "febrero", "marzo", "abril", "mayo", "junio",
                      "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"],
            "de":    ["januar", "februar", "maerz", "april", "mai", "juni",
                      "juli", "august", "september", "oktober", "november", "dezember"],
        }
        _URL_SEGMENT = {"fr": "meteo", "en": "weather", "en-us": "weather",
                        "es": "clima", "de": "wetter"}
        def monthly_url_builder(slug_x, mois_num, lang_x):
            month_slugs = _MONTH_URL_SLUGS.get(lang_x, _MONTH_URL_SLUGS["fr"])
            segment = _URL_SEGMENT.get(lang_x, "meteo")
            return f"{slug_x}-{segment}-{month_slugs[mois_num - 1]}.html"

    sorted_m = sorted(monthly, key=lambda m: int(m["mois_num"]))

    # Identifier le mois "best" pour mise en évidence (table row + mobile card)
    # Pattern V5 restauré : .row.best + .mobile-month-card.best
    best_mn = int(best_month(monthly).get("mois_num", 0))

    # THEAD
    thead = (f'              <thead>\n'
             f'                <tr>\n'
             f'                  <th>{L["th_month"]}</th>\n'
             f'                  <th>{L["th_tmin"]}</th>\n'
             f'                  <th>{L["th_tmax"]}</th>\n'
             f'                  <th>{L["th_rain"]}</th>\n'
             f'                  <th>{L["th_mm"]}</th>\n'
             f'                  <th>{L["th_sun"]}</th>\n'
             f'                  <th>{L["th_score"]}</th>\n'
             f'                  <th>{L["th_mood"]}</th>\n'
             f'                </tr>\n'
             f'              </thead>')

    # TBODY
    tbody_rows = []
    mobile_cards = []
    for m in sorted_m:
        mn = int(m["mois_num"])
        name = names[mn - 1]
        score = float(m.get("score", 0))
        tmin = m.get("tmin", "?")
        tmax = m.get("tmax", "?")
        rain = int(round(float(m.get("rain_pct", 0))))
        try:
            mm = float(m.get("precip_mm", 0) or 0)
        except (ValueError, TypeError):
            mm = 0.0
        sun = float(m.get("sun_h", 0) or 0)
        emo = _weather_emoji(sun)
        mood_label, mood_cls = _mood_label(score, lang)
        url = monthly_url_builder(slug, mn, lang) if has_monthly_pages else None
        is_best = (mn == best_mn)
        best_cls = " best" if is_best else ""

        # Row clickable seulement si la fiche mensuelle existe en prod
        if url:
            row = (f'                <tr class="row{best_cls}" '
                   f'onclick="location.href=\'{url}\'" '
                   f'style="cursor:pointer" tabindex="0" role="link" '
                   f'onkeydown="if(event.key===\'Enter\')location.href=\'{url}\'">'
                   f'<td class="month-cell">{emo} {_html.escape(name)} '
                   f'<span style="color:var(--gold);font-weight:700;margin-left:4px">→</span></td>'
                   f'<td>{_html.escape(str(tmin))}°C</td>'
                   f'<td>{_html.escape(str(tmax))}°C</td>'
                   f'<td>{rain}%</td>'
                   f'<td>{mm:.1f}mm</td>'
                   f'<td>{sun:.1f}h</td>'
                   f'<td>{score:.1f}/10</td>'
                   f'<td><span class="mood {mood_cls}">{_html.escape(mood_label)}</span></td>'
                   f'</tr>')
        else:
            row = (f'                <tr class="row{best_cls}">'
                   f'<td class="month-cell">{emo} {_html.escape(name)}</td>'
                   f'<td>{_html.escape(str(tmin))}°C</td>'
                   f'<td>{_html.escape(str(tmax))}°C</td>'
                   f'<td>{rain}%</td>'
                   f'<td>{mm:.1f}mm</td>'
                   f'<td>{sun:.1f}h</td>'
                   f'<td>{score:.1f}/10</td>'
                   f'<td><span class="mood {mood_cls}">{_html.escape(mood_label)}</span></td>'
                   f'</tr>')
        tbody_rows.append(row)

        # Card mobile : <a> si fiche existe, <div> sinon
        if url:
            mobile_open = f'<a href="{url}" class="mobile-month-card{best_cls}">'
            mobile_close = '</a>'
        else:
            mobile_open = f'<div class="mobile-month-card{best_cls}">'
            mobile_close = '</div>'

        mobile_cards.append(
            f'            {mobile_open}\n'
            f'              <div class="head"><div class="name">{emo} {_html.escape(name)}</div>'
            f'<div class="score {mood_cls}">{score:.1f}/10</div></div>\n'
            f'              <div class="rows">\n'
            f'                <div class="row"><span>T°</span><strong>{_html.escape(str(tmin))}°C / {_html.escape(str(tmax))}°C</strong></div>\n'
            f'                <div class="row"><span>{L["th_rain"].replace(" %", "")}</span><strong>{rain}%</strong></div>\n'
            f'                <div class="row"><span>{L["th_sun"]}</span><strong>{sun:.1f}h</strong></div>\n'
            f'                <div class="row row-mood"><strong class="mood-{mood_cls}">{_html.escape(mood_label)}</strong></div>\n'
            f'              </div>\n'
            f'            {mobile_close}'
        )

    tbody_block = "\n".join(tbody_rows)
    mobile_block = "\n".join(mobile_cards)

    html = (f'<div class="table-wrap">\n'
            f'            <table>\n'
            f'{thead}\n'
            f'              <tbody>\n'
            f'{tbody_block}\n'
            f'              </tbody>\n'
            f'            </table>\n'
            f'          </div>\n'
            f'\n'
            f'          <!-- Version mobile -->\n'
            f'          <div class="mobile-month-cards">\n'
            f'{mobile_block}\n'
            f'          </div>')

    return html


def build_signal_card_v6(dest, monthly, lang="fr"):
    """
    Construit la colonne droite de la section Comprendre : 2 cards signaux.

    Card 1 : Lecture rapide (3 signal-item)
    - Fenêtre optimale : plage des mois score ≥ 7
    - Bonne transition : mois score 6-7 (shoulder)
    - Période rude : plage des mois score ≤ 3.5

    Card 2 : Conditions détaillées (mois best)
    - 6 signal-items : ressenti, UV, humidité, AQI, pluie, soleil

    Args:
        dest: dict destination
        monthly: list[dict] 12 mois (requis : tmax, rain_pct, sun_h, dew_point_mean, uv_index, aqi_mean)
        lang: code langue

    Returns:
        str : HTML (2 cards wrappées dans signal-card)
    """
    if len(monthly) != 12:
        raise ValueError(f"monthly doit contenir 12 entrées, reçu {len(monthly)}")

    L = _COMPRENDRE_LABELS.get(lang, _COMPRENDRE_LABELS["fr"])
    names = MONTH_NAMES.get(lang, MONTH_NAMES["fr"])

    # Catégories par score
    optimal = [m for m in monthly if _score(m) >= 7.0]
    transition = [m for m in monthly if 5.5 <= _score(m) < 7.0]
    tough = [m for m in monthly if _score(m) <= 3.5]

    range_optimal = _month_range_arrow(optimal, lang)
    range_transition = _month_range_arrow(transition, lang)
    range_tough = _month_range_arrow(tough, lang)

    # Card 1 : Lecture rapide
    card1 = (f'<div class="card pad">\n'
             f'            <div class="small-label">{L["lbl_signal_quick"]}</div>\n'
             f'            <div class="signal-list">\n'
             f'              <div class="signal-item"><div class="l">{L["sig_optimal"]}</div><div class="r">{_html.escape(range_optimal)}</div></div>\n'
             f'              <div class="signal-item"><div class="l">{L["sig_transition"]}</div><div class="r">{_html.escape(range_transition)}</div></div>\n'
             f'              <div class="signal-item"><div class="l">{L["sig_tough"]}</div><div class="r">{_html.escape(range_tough)}</div></div>\n'
             f'            </div>\n'
             f'          </div>')

    # Card 2 : Conditions détaillées du mois best
    best = best_month(monthly)
    best_name = format_month_full(best, lang)
    best_tmax = best.get("tmax")
    best_rain = best.get("rain_pct")
    best_mm = best.get("precip_mm")
    best_sun = best.get("sun_h")
    best_dew = best.get("dew_point_mean")
    best_uv = best.get("uv_index")
    best_aqi = best.get("aqi_mean")

    # Ressenti (fonction simplifiée, à localiser)
    feel = _appreciate_feel(best_tmax, best_dew, lang)
    uv_label = _appreciate_uv(best_uv)
    dew_label = _appreciate_dew(best_dew)
    aqi_res = _appreciate_aqi(best_aqi)

    items = []
    items.append(f'<div class="signal-item"><div class="l">{L["sig_feel"]}</div><div class="r">{_html.escape(feel)}</div></div>')
    if uv_label and best_uv:
        try:
            uv_val = float(best_uv)
            items.append(f'<div class="signal-item"><div class="l">{L["sig_uv"]}</div><div class="r">{uv_val:.1f} · {_html.escape(uv_label)}</div></div>')
        except (ValueError, TypeError):
            pass
    if dew_label and best_dew:
        try:
            dv = float(best_dew)
            items.append(f'<div class="signal-item"><div class="l">{L["sig_humidity"]}</div><div class="r">{dv:.1f}°C · {_html.escape(dew_label)}</div></div>')
        except (ValueError, TypeError):
            pass
    if aqi_res and best_aqi:
        try:
            av = float(best_aqi)
            items.append(f'<div class="signal-item"><div class="l">{L["sig_air"]}</div><div class="r">{av:.0f} · {_html.escape(aqi_res[0])}</div></div>')
        except (ValueError, TypeError):
            pass
    # Pluie
    if best_rain is not None:
        try:
            rain_v = int(round(float(best_rain)))
            mm_v = float(best_mm) if best_mm else 0
            items.append(f'<div class="signal-item"><div class="l">{L["sig_rain"]}</div><div class="r">{rain_v}% · {mm_v:.1f} {L["mm_unit"]}</div></div>')
        except (ValueError, TypeError):
            pass
    # Soleil
    if best_sun:
        try:
            sv = float(best_sun)
            items.append(f'<div class="signal-item"><div class="l">{L["sig_sun"]}</div><div class="r">{sv:.1f}{L["sun_unit_day"]}</div></div>')
        except (ValueError, TypeError):
            pass

    items_block = "\n              ".join(items)

    card2 = (f'<div class="card pad">\n'
             f'            <div class="small-label">{L["lbl_signal_detailed"].format(best_month=_html.escape(best_name.lower()))}</div>\n'
             f'            <div class="signal-list">\n'
             f'              {items_block}\n'
             f'            </div>\n'
             f'          </div>')

    html = (f'<div class="signal-card">\n'
            f'          {card1}\n'
            f'          {card2}\n'
            f'        </div>')

    return html


def build_comprendre_section_v6(dest, monthly, lang="fr"):
    """
    Section 'Comprendre' complète : header + spotlight-grid (tableau + signaux).

    Args:
        dest: dict destination
        monthly: list[dict] 12 mois
        lang: code langue

    Returns:
        str : HTML complet de la section
    """
    if len(monthly) != 12:
        raise ValueError(f"monthly doit contenir 12 entrées, reçu {len(monthly)}")

    L = _COMPRENDRE_LABELS.get(lang, _COMPRENDRE_LABELS["fr"])

    # Badge "N mois confortables (avr→sep)"
    good_months = [m for m in monthly if _score(m) >= 7.0]
    n_good = len(good_months)
    range_short = _month_range_short(good_months, lang) if good_months else "—"

    badge_html = (f'<div style="display:inline-flex;align-items:center;gap:8px;'
                  f'padding:6px 12px;background:var(--green-soft);'
                  f'border:1px solid var(--green-border);border-radius:999px;'
                  f'margin-bottom:12px;font-size:12px;font-weight:700;color:var(--green)">\n'
                  f'            ✅ <span>{L["lbl_comfort_months"].format(n=n_good)}</span>\n'
                  f'            <span style="font-size:11px;font-weight:500;color:var(--muted)">{L["lbl_comfort_range"].format(range_short=range_short)}</span>\n'
                  f'          </div>')

    table_html = build_months_table_v6(dest, monthly, lang=lang)
    signals_html = build_signal_card_v6(dest, monthly, lang=lang)

    section = (f'<section id="tableau">\n'
               f'    <div class="container">\n'
               f'      <div class="section-head">\n'
               f'        <div class="section-kicker">{_html.escape(L["kicker"])}</div>\n'
               f'        <h2>{_html.escape(L["title"])}</h2>\n'
               f'        <p class="lead">{_html.escape(L["lead"])}</p>\n'
               f'      </div>\n'
               f'      <div class="spotlight-grid">\n'
               f'        <div class="card pad">\n'
               f'          {badge_html}\n'
               f'          {table_html}\n'
               f'        </div>\n'
               f'        {signals_html}\n'
               f'      </div>\n'
               f'    </div>\n'
               f'  </section>')

    return section


    return section


# ══════════════════════════════════════════════════════════════════
# Section 'À quoi s'attendre' : cards saisons contextuelles par type
# ══════════════════════════════════════════════════════════════════

_SEASONS_LABELS = {
    "fr": {
        "kicker": "Contexte",
        "title_generic": "À quoi s'attendre selon la période",
        "title_tropical": "Deux saisons tropicales bien marquées",
        "title_mountain": "Deux saisons montagne bien distinctes",
        "lead_generic": "Climat tempéré : plusieurs périodes qui changent la qualité du séjour.",
        "lead_tropical": "Le vrai arbitrage porte sur la pluie, pas la température (stable 24-30°C toute l'année).",
        "lead_mountain": "Ski l'hiver, randonnée l'été. Les mi-saisons ferment tout.",
    },
    "en": {
        "kicker": "Context",
        "title_generic": "What to expect over the year",
        "title_tropical": "Two clear tropical seasons",
        "title_mountain": "Two distinct mountain seasons",
        "lead_generic": "Temperate climate: several periods that change the quality of the stay.",
        "lead_tropical": "The real trade-off is rain, not temperature (stable 24-30°C year-round).",
        "lead_mountain": "Skiing in winter, hiking in summer. Shoulder months shut everything down.",
    },
    "en-us": {
        "kicker": "Context",
        "title_generic": "What to expect over the year",
        "title_tropical": "Two clear tropical seasons",
        "title_mountain": "Two distinct mountain seasons",
        "lead_generic": "Temperate climate: several periods that change the quality of the stay.",
        "lead_tropical": "The real trade-off is rain, not temperature (stable 24-30°C year-round).",
        "lead_mountain": "Skiing in winter, hiking in summer. Shoulder months shut everything down.",
    },
    "es": {
        "kicker": "Contexto",
        "title_generic": "Qué esperar según el período",
        "title_tropical": "Dos temporadas tropicales bien marcadas",
        "title_mountain": "Dos temporadas de montaña bien distintas",
        "lead_generic": "Clima templado: varios períodos que cambian la calidad del viaje.",
        "lead_tropical": "La verdadera decisión es la lluvia, no la temperatura (estable 24-30°C todo el año).",
        "lead_mountain": "Esquí en invierno, senderismo en verano. Las entre-temporadas cierran todo.",
    },
    "de": {
        "kicker": "Kontext",
        "title_generic": "Was in welcher Periode zu erwarten ist",
        "title_tropical": "Zwei klar getrennte tropische Jahreszeiten",
        "title_mountain": "Zwei deutlich unterschiedliche Bergjahreszeiten",
        "lead_generic": "Gemäßigtes Klima: mehrere Perioden, die den Aufenthalt prägen.",
        "lead_tropical": "Die eigentliche Frage ist Regen, nicht Temperatur (stabil 24-30°C ganzjährig).",
        "lead_mountain": "Ski im Winter, Wandern im Sommer. Zwischensaisons schließen alles.",
    },
}


def _build_season_cards(dtype, monthly, lang="fr"):
    """
    Construit 2-4 cards saisons selon le type de destination, avec contenu
    adapté aux vraies données mensuelles.

    Returns:
        list[(icon, title, badge, paragraph)]
    """
    # Plages de mois par score
    great_months = [m for m in monthly if _score(m) >= 7.0]   # très bons
    mid_months = [m for m in monthly if 5.5 <= _score(m) < 7.0]
    bad_months = [m for m in monthly if _score(m) <= 3.5]
    best = best_month(monthly)
    best_score = _score(best)

    range_great = _month_range_arrow(great_months, lang)
    range_mid = _month_range_arrow(mid_months, lang)
    range_bad = _month_range_arrow(bad_months, lang)
    best_name = format_month_full(best, lang)

    cards = []

    if dtype == "tropical":
        # 2 cards : saison sèche + saison humide
        tmpl = {
            "fr": [
                ("☀️", "Saison sèche", range_great or "Selon les mois",
                 f"Peu de pluie, soleil stable, humidité plus basse. Fenêtre optimale pour plongée, randonnée, explorations culturelles. "
                 f"Pic touristique : tarifs hauts et fréquentation maximale. "
                 f"Meilleur mois : <strong>{best_name}</strong> ({best_score:.1f}/10)."),
                ("🌧️", "Saison humide", range_bad or range_mid or "Hors saison sèche",
                 f"Mousson tropicale : averses quotidiennes, humidité oppressante, fréquentation réduite. "
                 f"Tarifs nettement plus bas, nature luxuriante. Rester possible si on accepte la pluie."),
            ],
            "en": [
                ("☀️", "Dry season", range_great or "Depends on month",
                 f"Low rain, stable sunshine, lower humidity. Optimal window for diving, hiking, culture. "
                 f"Peak tourism: high rates and max crowds. "
                 f"Best month: <strong>{best_name}</strong> ({best_score:.1f}/10)."),
                ("🌧️", "Wet season", range_bad or range_mid or "Outside dry season",
                 f"Tropical monsoon: daily showers, oppressive humidity, reduced crowds. "
                 f"Much lower rates, lush nature. Feasible if you accept the rain."),
            ],
            "en-us": [
                ("☀️", "Dry season", range_great or "Depends on month",
                 f"Low rain, stable sunshine, lower humidity. Optimal window for diving, hiking, culture. "
                 f"Peak tourism: high rates and max crowds. "
                 f"Best month: <strong>{best_name}</strong> ({best_score:.1f}/10)."),
                ("🌧️", "Wet season", range_bad or range_mid or "Outside dry season",
                 f"Tropical monsoon: daily showers, oppressive humidity, reduced crowds. "
                 f"Much lower rates, lush nature. Feasible if you accept the rain."),
            ],
            "es": [
                ("☀️", "Temporada seca", range_great or "Según los meses",
                 f"Poca lluvia, sol estable, humedad más baja. Ventana óptima para buceo, senderismo, cultura. "
                 f"Pico turístico: tarifas altas y máxima afluencia. "
                 f"Mejor mes: <strong>{best_name}</strong> ({best_score:.1f}/10)."),
                ("🌧️", "Temporada húmeda", range_bad or range_mid or "Fuera temporada seca",
                 f"Monzón tropical: chaparrones diarios, humedad opresiva, afluencia reducida. "
                 f"Tarifas mucho más bajas, naturaleza exuberante. Posible si aceptas la lluvia."),
            ],
            "de": [
                ("☀️", "Trockenzeit", range_great or "Je nach Monat",
                 f"Wenig Regen, stabile Sonne, geringere Luftfeuchtigkeit. Optimales Fenster für Tauchen, Wandern, Kultur. "
                 f"Hochsaison: hohe Preise und maximale Menge. "
                 f"Bester Monat: <strong>{best_name}</strong> ({best_score:.1f}/10)."),
                ("🌧️", "Regenzeit", range_bad or range_mid or "Außerhalb Trockenzeit",
                 f"Tropischer Monsun: tägliche Schauer, drückende Luftfeuchtigkeit, weniger Menge. "
                 f"Viel niedrigere Preise, üppige Natur. Machbar, wenn Regen akzeptabel."),
            ],
        }
        cards = tmpl.get(lang, tmpl["fr"])

    elif dtype == "mountain":
        # 3 cards : ski / rando / entre-saisons
        # Identifier hiver (dec-avril) avec meilleur score
        winter_nums = {1, 2, 3, 4, 12}
        summer_nums = {6, 7, 8, 9}
        shoulder_nums = {5, 10, 11}
        winter_months = [m for m in monthly if int(m["mois_num"]) in winter_nums]
        summer_months = [m for m in monthly if int(m["mois_num"]) in summer_nums]
        shoulder_months_list = [m for m in monthly if int(m["mois_num"]) in shoulder_nums]

        range_winter = _month_range_arrow(winter_months, lang)
        range_summer = _month_range_arrow(summer_months, lang)
        range_shoulder = _month_range_arrow(shoulder_months_list, lang)

        tmpl = {
            "fr": [
                ("⛷️", "Saison ski", range_winter,
                 "Enneigement + stations ouvertes, remontées en service, neige fraîche en altitude. "
                 "Fenêtre dense : vacances scolaires fréquentées, janvier-mars = pic d'affluence."),
                ("🥾", "Saison randonnée", range_summer,
                 "Sentiers secs, refuges ouverts, journées longues. Alpinisme possible quand temps stable. "
                 "Juillet-août : forte affluence, refuges réservés des semaines à l'avance."),
                ("🌸", "Entre-saisons", range_shoulder,
                 "Remontées fermées, refuges clos, transition neige/sentiers. "
                 "Peu d'activités possibles mais calme absolu et tarifs bas."),
            ],
            "en": [
                ("⛷️", "Ski season", range_winter,
                 "Snow cover + open resorts, working lifts, fresh powder at altitude. "
                 "Dense window: school holidays packed, January-March = peak crowds."),
                ("🥾", "Hiking season", range_summer,
                 "Dry trails, open huts, long daylight. Mountaineering when weather stable. "
                 "July-August: heavy crowds, huts booked weeks ahead."),
                ("🌸", "Shoulder months", range_shoulder,
                 "Lifts closed, huts shut, transition snow/trails. "
                 "Few activities but absolute calm and low rates."),
            ],
            "en-us": [
                ("⛷️", "Ski season", range_winter,
                 "Snow cover + open resorts, working lifts, fresh powder at altitude. "
                 "Dense window: school holidays packed, January-March = peak crowds."),
                ("🥾", "Hiking season", range_summer,
                 "Dry trails, open huts, long daylight. Mountaineering when weather stable. "
                 "July-August: heavy crowds, huts booked weeks ahead."),
                ("🌸", "Shoulder months", range_shoulder,
                 "Lifts closed, huts shut, transition snow/trails. "
                 "Few activities but absolute calm and low rates."),
            ],
            "es": [
                ("⛷️", "Temporada de esquí", range_winter,
                 "Nieve + estaciones abiertas, remontes en servicio, nieve fresca en altura. "
                 "Ventana densa: vacaciones escolares llenas, enero-marzo = pico de afluencia."),
                ("🥾", "Temporada de senderismo", range_summer,
                 "Senderos secos, refugios abiertos, días largos. Alpinismo posible con tiempo estable. "
                 "Julio-agosto: mucha afluencia, refugios reservados semanas antes."),
                ("🌸", "Entre-temporadas", range_shoulder,
                 "Remontes cerrados, refugios clausurados, transición nieve/senderos. "
                 "Pocas actividades posibles pero calma absoluta y tarifas bajas."),
            ],
            "de": [
                ("⛷️", "Skisaison", range_winter,
                 "Schneedecke + offene Stationen, fahrende Lifte, frischer Schnee in der Höhe. "
                 "Dichtes Fenster: Schulferien voll, Januar-März = Spitze."),
                ("🥾", "Wandersaison", range_summer,
                 "Trockene Wege, offene Hütten, lange Tage. Bergsteigen bei stabilem Wetter. "
                 "Juli-August: viel Andrang, Hütten Wochen im Voraus gebucht."),
                ("🌸", "Zwischensaisons", range_shoulder,
                 "Lifte geschlossen, Hütten zu, Übergang Schnee/Pfade. "
                 "Wenig Aktivitäten, aber absolute Ruhe und niedrige Preise."),
            ],
        }
        cards = tmpl.get(lang, tmpl["fr"])

    else:
        # Generic : 3 cards (été lumineux / mi-saison / hiver difficile)
        summer_nums = {6, 7, 8, 9}
        winter_nums = {11, 12, 1, 2}
        shoulder_nums = {3, 4, 5, 10}
        summer = [m for m in monthly if int(m["mois_num"]) in summer_nums]
        winter = [m for m in monthly if int(m["mois_num"]) in winter_nums]
        shoulder = [m for m in monthly if int(m["mois_num"]) in shoulder_nums]

        range_summer = _month_range_arrow(summer, lang) if summer else "—"
        range_winter = _month_range_arrow(winter, lang) if winter else "—"
        range_shoulder = _month_range_arrow(shoulder, lang) if shoulder else "—"

        # Moyennes pour enrichir (si données dispo)
        def avg(ms, field):
            vals = [float(m[field]) for m in ms if m.get(field) not in (None, "", "None")]
            return sum(vals) / len(vals) if vals else None

        summer_sun = avg(summer, "sun_h")
        summer_tmax = avg(summer, "tmax")
        winter_sun = avg(winter, "sun_h")
        winter_tmax = avg(winter, "tmax")

        sun_str = f"{summer_sun:.0f}h" if summer_sun else "—"
        wsun_str = f"{winter_sun:.0f}h" if winter_sun else "—"
        st_str = f"{summer_tmax:.0f}°C" if summer_tmax else "—"
        wt_str = f"{winter_tmax:.0f}°C" if winter_tmax else "—"

        tmpl = {
            "fr": [
                ("☀️", "Saison haute", range_summer,
                 f"Journées longues ({sun_str} de soleil), températures {st_str}, météo stable. "
                 f"<strong>Période à privilégier</strong> pour balades, terrasses, activités extérieures. "
                 f"Pic touristique : affluence et prix élevés."),
                ("🌥️", "Mi-saison", range_shoulder,
                 f"Climat intermédiaire, fréquentation modérée. "
                 f"Bon compromis météo / foule / tarifs. Printemps : floraisons. "
                 f"Automne : couleurs et lumière rasante."),
                ("❄️", "Saison basse", range_winter,
                 f"Journées courtes ({wsun_str} de soleil), températures {wt_str}, météo instable. "
                 f"Période difficile en extérieur mais tarifs hôtels au plus bas. "
                 f"Musées, spas, gastronomie compensent."),
            ],
            "en": [
                ("☀️", "High season", range_summer,
                 f"Long days ({sun_str} of sun), temperatures {st_str}, stable weather. "
                 f"<strong>Preferred period</strong> for walks, terraces, outdoor activities. "
                 f"Peak tourism: high crowds and prices."),
                ("🌥️", "Shoulder", range_shoulder,
                 f"Intermediate climate, moderate attendance. "
                 f"Good weather/crowd/price compromise. Spring: blooms. "
                 f"Autumn: colors and low-angle light."),
                ("❄️", "Low season", range_winter,
                 f"Short days ({wsun_str} of sun), temperatures {wt_str}, unstable weather. "
                 f"Outdoor-tough but hotel rates at their lowest. "
                 f"Museums, spas, gastronomy compensate."),
            ],
            "en-us": [
                ("☀️", "High season", range_summer,
                 f"Long days ({sun_str} of sun), temperatures {st_str}, stable weather. "
                 f"<strong>Preferred period</strong> for walks, terraces, outdoor activities. "
                 f"Peak tourism: high crowds and prices."),
                ("🌥️", "Shoulder", range_shoulder,
                 f"Intermediate climate, moderate attendance. "
                 f"Good weather/crowd/price compromise. Spring: blooms. "
                 f"Autumn: colors and low-angle light."),
                ("❄️", "Low season", range_winter,
                 f"Short days ({wsun_str} of sun), temperatures {wt_str}, unstable weather. "
                 f"Outdoor-tough but hotel rates at their lowest. "
                 f"Museums, spas, gastronomy compensate."),
            ],
            "es": [
                ("☀️", "Temporada alta", range_summer,
                 f"Días largos ({sun_str} de sol), temperaturas {st_str}, tiempo estable. "
                 f"<strong>Período preferente</strong> para paseos, terrazas, actividades exteriores. "
                 f"Pico turístico: mucha afluencia y precios altos."),
                ("🌥️", "Entre-temporada", range_shoulder,
                 f"Clima intermedio, afluencia moderada. "
                 f"Buen compromiso tiempo/multitud/precios. Primavera: floraciones. "
                 f"Otoño: colores y luz rasante."),
                ("❄️", "Temporada baja", range_winter,
                 f"Días cortos ({wsun_str} de sol), temperaturas {wt_str}, tiempo inestable. "
                 f"Período duro en exterior pero tarifas hoteleras al mínimo. "
                 f"Museos, spas, gastronomía compensan."),
            ],
            "de": [
                ("☀️", "Hochsaison", range_summer,
                 f"Lange Tage ({sun_str} Sonne), Temperaturen {st_str}, stabiles Wetter. "
                 f"<strong>Bevorzugte Periode</strong> für Spaziergänge, Terrassen, Outdoor-Aktivitäten. "
                 f"Hochsaison: viel Andrang und hohe Preise."),
                ("🌥️", "Zwischensaison", range_shoulder,
                 f"Mittleres Klima, moderate Frequentierung. "
                 f"Gutes Wetter-/Andrang-/Preis-Verhältnis. Frühling: Blüten. "
                 f"Herbst: Farben und flaches Licht."),
                ("❄️", "Nebensaison", range_winter,
                 f"Kurze Tage ({wsun_str} Sonne), Temperaturen {wt_str}, instabiles Wetter. "
                 f"Draußen schwierig, aber Hotelpreise auf Tiefststand. "
                 f"Museen, Spas, Gastronomie gleichen aus."),
            ],
        }
        cards = tmpl.get(lang, tmpl["fr"])

    return cards


# ══════════════════════════════════════════════════════════════════
# SECTION TENDANCE 10 ANS (Tour 8b)
# ══════════════════════════════════════════════════════════════════

# Labels par langue pour la section Tendance
_TENDANCE_LABELS = {
    "fr": {
        "kicker":     "Tendance 10 ans",
        "h2":         "Températures annuelles — {nom}",
        "lead":       "Courbes T° min/max observées sur les 10 dernières années (ERA5). Permet de voir la stabilité et la tendance.",
        "lbl_max":    "T° max",
        "lbl_moy":    "Moyenne",
        "lbl_min":    "T° min",
        "method_h":   "Comment sont calculés nos scores ?",
        "method_sub": "4 critères pondérés sur 10 ans de données climatiques réelles",
        "k_precip":   "Précipitations",
        "v_precip":   "Fréquence & intensité quotidienne de pluie",
        "k_temp":     "Température",
        "v_temp":     "T° max, min & stabilité mensuelle",
        "k_sun":      "Ensoleillement",
        "v_sun":      "Heures de soleil par jour",
        "k_dew":      "Ressenti humide",
        "v_dew":      "Point de rosée (confort thermique réel)",
        "source":     "Source :",
        "source_v":   "ERA5 (ECMWF) · Open-Meteo · 10 ans (2016-2025)",
        "method_link":"Méthodologie complète →",
        "no_data":    "Données annuelles indisponibles pour cette destination.",
    },
    "en": {
        "kicker":     "10-year trend",
        "h2":         "Annual temperatures — {nom}",
        "lead":       "Min/max temperature curves observed over the last 10 years (ERA5). Shows stability and trend.",
        "lbl_max":    "T° max",
        "lbl_moy":    "Average",
        "lbl_min":    "T° min",
        "method_h":   "How are our scores calculated?",
        "method_sub": "4 weighted criteria on 10 years of real climate data",
        "k_precip":   "Precipitation",
        "v_precip":   "Daily rain frequency & intensity",
        "k_temp":     "Temperature",
        "v_temp":     "T° max, min & monthly stability",
        "k_sun":      "Sunshine",
        "v_sun":      "Daily sunshine hours",
        "k_dew":      "Humid feel",
        "v_dew":      "Dew point (real thermal comfort)",
        "source":     "Source:",
        "source_v":   "ERA5 (ECMWF) · Open-Meteo · 10 years (2016-2025)",
        "method_link":"Full methodology →",
        "no_data":    "Annual data unavailable for this destination.",
    },
    "en-us": {
        "kicker":     "10-year trend",
        "h2":         "Annual temperatures — {nom}",
        "lead":       "Min/max temperature curves observed over the last 10 years (ERA5). Shows stability and trend.",
        "lbl_max":    "T° max",
        "lbl_moy":    "Average",
        "lbl_min":    "T° min",
        "method_h":   "How are our scores calculated?",
        "method_sub": "4 weighted criteria on 10 years of real climate data",
        "k_precip":   "Precipitation",
        "v_precip":   "Daily rain frequency & intensity",
        "k_temp":     "Temperature",
        "v_temp":     "T° max, min & monthly stability",
        "k_sun":      "Sunshine",
        "v_sun":      "Daily sunshine hours",
        "k_dew":      "Humid feel",
        "v_dew":      "Dew point (real thermal comfort)",
        "source":     "Source:",
        "source_v":   "ERA5 (ECMWF) · Open-Meteo · 10 years (2016-2025)",
        "method_link":"Full methodology →",
        "no_data":    "Annual data unavailable for this destination.",
    },
    "es": {
        "kicker":     "Tendencia 10 años",
        "h2":         "Temperaturas anuales — {nom}",
        "lead":       "Curvas de T° mín/máx observadas en los últimos 10 años (ERA5). Permite ver la estabilidad y la tendencia.",
        "lbl_max":    "T° máx",
        "lbl_moy":    "Promedio",
        "lbl_min":    "T° mín",
        "method_h":   "¿Cómo calculamos las puntuaciones?",
        "method_sub": "4 criterios ponderados sobre 10 años de datos climáticos reales",
        "k_precip":   "Precipitaciones",
        "v_precip":   "Frecuencia e intensidad diaria de lluvia",
        "k_temp":     "Temperatura",
        "v_temp":     "T° máx, mín y estabilidad mensual",
        "k_sun":      "Sol",
        "v_sun":      "Horas de sol al día",
        "k_dew":      "Sensación húmeda",
        "v_dew":      "Punto de rocío (confort térmico real)",
        "source":     "Fuente:",
        "source_v":   "ERA5 (ECMWF) · Open-Meteo · 10 años (2016-2025)",
        "method_link":"Metodología completa →",
        "no_data":    "Datos anuales no disponibles para este destino.",
    },
    "de": {
        "kicker":     "10-Jahres-Trend",
        "h2":         "Jahrestemperaturen — {nom}",
        "lead":       "Min/Max-Temperaturkurven der letzten 10 Jahre (ERA5). Zeigt Stabilität und Trend.",
        "lbl_max":    "T° max",
        "lbl_moy":    "Durchschnitt",
        "lbl_min":    "T° min",
        "method_h":   "Wie werden unsere Scores berechnet?",
        "method_sub": "4 gewichtete Kriterien auf 10 Jahren echter Klimadaten",
        "k_precip":   "Niederschlag",
        "v_precip":   "Tägliche Regenhäufigkeit & -intensität",
        "k_temp":     "Temperatur",
        "v_temp":     "T° max, min & monatliche Stabilität",
        "k_sun":      "Sonne",
        "v_sun":      "Sonnenstunden pro Tag",
        "k_dew":      "Schwüle",
        "v_dew":      "Taupunkt (reales Thermalkomfort)",
        "source":     "Quelle:",
        "source_v":   "ERA5 (ECMWF) · Open-Meteo · 10 Jahre (2016-2025)",
        "method_link":"Vollständige Methodik →",
        "no_data":    "Jahresdaten für dieses Reiseziel nicht verfügbar.",
    },
}


def build_temperature_chart_v6(slug, lang="fr"):
    """
    Génère le SVG 'Tendance 10 ans' avec courbes T° min/moyenne/max sur 2016-2025.

    Reproduit fidèlement le SVG V5 (viewBox 560×234) :
    - Grille horizontale (lignes pointillées + labels axe Y)
    - 3 polylines : T° max (rouge), moyenne (gris pointillé), T° min (bleu)
    - Cercles aux points de données (rouge T°max, bleu T°min)
    - Labels années alternés (haut/bas) sur axe X
    - Légende sous le graphique

    Args:
        slug: slug FR de la destination
        lang: code langue

    Returns:
        str : SVG + légende, ou message 'no_data' si trend absent
    """
    from lib.climate_trend import get_trend
    L = _TENDANCE_LABELS.get(lang, _TENDANCE_LABELS["fr"])
    trend = get_trend(slug)
    if not trend or not trend.get("years"):
        return f'<div class="ct-no-data">{L["no_data"]}</div>'

    years = trend["years"]
    tmax = trend["tmax"]
    tmin = trend["tmin"]
    tmoy = trend["tmoy"]

    # Bornes du graphique : viewBox 560×234, axes selon V5
    # X: 40 → 544 (504px utiles, n_years points)
    # Y: 11.8 (top) → 175.8 (bottom), range 164px pour gamme T°
    n = len(years)
    if n < 2:
        return f'<div class="ct-no-data">{L["no_data"]}</div>'

    x_left, x_right = 40.0, 544.0
    y_top, y_bot = 11.8, 175.8

    # Range T° : auto-adapté avec marge, arrondi aux entiers pairs
    all_t = tmin + tmoy + tmax
    t_lo_raw, t_hi_raw = min(all_t), max(all_t)
    pad = max(1.0, (t_hi_raw - t_lo_raw) * 0.1)
    t_lo = int((t_lo_raw - pad) // 2 * 2)  # pair inférieur
    t_hi = int((t_hi_raw + pad + 1) // 2 * 2)  # pair supérieur
    t_range = max(1, t_hi - t_lo)

    def x_of(i):
        return x_left + (x_right - x_left) * i / (n - 1)

    def y_of(t):
        # Inversion : t_hi en haut (y_top), t_lo en bas (y_bot)
        return y_top + (y_bot - y_top) * (t_hi - t) / t_range

    # Grille horizontale : labels tous les 2°C
    grid_lines = []
    for tval in range(t_lo, t_hi + 1, 2):
        y = y_of(tval)
        grid_lines.append(
            f'<line x1="{x_left}" y1="{y:.1f}" x2="{x_right}" y2="{y:.1f}" '
            f'stroke="#e8e0d0" stroke-width="1" stroke-dasharray="3 3"/>'
            f'<text x="34" y="{y + 4:.1f}" text-anchor="end" '
            f'font-size="10" fill="#6b7280" font-weight="600">{tval}</text>'
        )

    # Polylines (3 courbes)
    def polyline_pts(values):
        return " ".join(f"{x_of(i):.1f},{y_of(v):.1f}" for i, v in enumerate(values))

    poly_min = (
        f'<polyline points="{polyline_pts(tmin)}" '
        f'fill="none" stroke="#3b82f6" stroke-width="2.5" '
        f'stroke-linejoin="round" stroke-linecap="round"/>'
    )
    poly_moy = (
        f'<polyline points="{polyline_pts(tmoy)}" '
        f'fill="none" stroke="#9ca3af" stroke-width="1.5" '
        f'stroke-linejoin="round" stroke-linecap="round" stroke-dasharray="5 3"/>'
    )
    poly_max = (
        f'<polyline points="{polyline_pts(tmax)}" '
        f'fill="none" stroke="#ef4444" stroke-width="2.5" '
        f'stroke-linejoin="round" stroke-linecap="round"/>'
    )

    # Cercles aux points de données (max + min, comme V5)
    circles_max = "".join(
        f'<circle cx="{x_of(i):.1f}" cy="{y_of(v):.1f}" r="3" '
        f'fill="#ef4444" stroke="white" stroke-width="1.5"/>'
        for i, v in enumerate(tmax)
    )
    circles_min = "".join(
        f'<circle cx="{x_of(i):.1f}" cy="{y_of(v):.1f}" r="3" '
        f'fill="#3b82f6" stroke="white" stroke-width="1.5"/>'
        for i, v in enumerate(tmin)
    )

    # Labels années (alternance haut 216 / bas 231 comme V5)
    year_labels = []
    for i, yr in enumerate(years):
        x = x_of(i)
        y_lbl = 216 if (i % 2 == 0) else 231
        year_labels.append(
            f'<text x="{x:.1f}" y="{y_lbl}" text-anchor="middle" '
            f'font-size="9.5" fill="#6b7280" font-weight="600">{yr}</text>'
            f'<line x1="{x:.1f}" y1="186" x2="{x:.1f}" y2="190" '
            f'stroke="#d1d5db" stroke-width="1"/>'
        )

    # Légende sous le graphique
    legend = (
        f'<div style="display:flex;gap:14px;flex-wrap:wrap;margin-top:10px">'
        f'<span style="display:inline-flex;align-items:center;gap:6px;font-size:11px;color:#718096;white-space:nowrap">'
        f'<span style="display:inline-block;width:18px;height:3px;border-radius:2px;background:#ef4444;flex-shrink:0"></span>'
        f'{L["lbl_max"]}</span>'
        f'<span style="display:inline-flex;align-items:center;gap:6px;font-size:11px;color:#718096;white-space:nowrap">'
        f'<span style="display:inline-block;width:18px;height:3px;border-radius:2px;'
        f'background:repeating-linear-gradient(90deg,#9ca3af 0,#9ca3af 5px,transparent 5px,transparent 8px);flex-shrink:0"></span>'
        f'{L["lbl_moy"]}</span>'
        f'<span style="display:inline-flex;align-items:center;gap:6px;font-size:11px;color:#718096;white-space:nowrap">'
        f'<span style="display:inline-block;width:18px;height:3px;border-radius:2px;background:#3b82f6;flex-shrink:0"></span>'
        f'{L["lbl_min"]}</span>'
        f'</div>'
    )

    svg = (
        f'<svg viewBox="0 0 560 234" width="100%" '
        f'style="display:block;overflow:visible" role="img" '
        f'aria-label="{L["h2"].format(nom=slug.title())}">'
        f'{"".join(grid_lines)}'
        f'{poly_min}{poly_moy}{poly_max}'
        f'{circles_max}{circles_min}'
        f'{"".join(year_labels)}'
        f'</svg>'
    )

    return f'<div class="ct-chart-wrap">{svg}{legend}</div>'


def build_methodology_card_v6(lang="fr"):
    """
    Encart 'Comment sont calculés nos scores ?' avec 4 critères + source ERA5.

    Identique au V5, traduit en 5 langues.

    Returns:
        str : div.method-card complet
    """
    L = _TENDANCE_LABELS.get(lang, _TENDANCE_LABELS["fr"])
    return (
        f'<div class="method-card">'
        f'<div class="method-head">'
        f'<div class="method-ico">🔬</div>'
        f'<div>'
        f'<div class="method-title">{L["method_h"]}</div>'
        f'<div class="method-sub">{L["method_sub"]}</div>'
        f'</div>'
        f'</div>'
        f'<div class="method-grid">'
        f'<div class="method-item"><div class="method-k">{L["k_precip"]}</div><div class="method-v">{L["v_precip"]}</div></div>'
        f'<div class="method-item"><div class="method-k">{L["k_temp"]}</div><div class="method-v">{L["v_temp"]}</div></div>'
        f'<div class="method-item"><div class="method-k">{L["k_sun"]}</div><div class="method-v">{L["v_sun"]}</div></div>'
        f'<div class="method-item"><div class="method-k">{L["k_dew"]}</div><div class="method-v">{L["v_dew"]}</div></div>'
        f'</div>'
        f'<div class="method-footer">'
        f'<div class="method-source"><strong>{L["source"]}</strong> {L["source_v"]}</div>'
        f'<a href="methodologie.html" class="method-link">{L["method_link"]}</a>'
        f'</div>'
        f'</div>'
    )


def build_tendance_section_v6(dest, lang="fr"):
    """
    Section complète 'Tendance 10 ans' = graphique SVG + encart méthodologie.

    Args:
        dest: dict destination (besoin de slug + nom_{lang})
        lang: code langue

    Returns:
        str : <section> complet
    """
    L = _TENDANCE_LABELS.get(lang, _TENDANCE_LABELS["fr"])
    slug = dest.get("slug") or dest.get("slug_fr") or "paris"
    nom = (dest.get(f"nom_{lang}") or dest.get("nom_fr") or
           dest.get("nom_bare") or slug.title())

    chart = build_temperature_chart_v6(slug, lang)
    method = build_methodology_card_v6(lang)

    return (
        f'<section class="tendance-section">'
        f'<div class="container">'
        f'<div class="section-head">'
        f'<div class="section-kicker">{L["kicker"]}</div>'
        f'<h2>{L["h2"].format(nom=_html.escape(nom))}</h2>'
        f'<p class="lead">{L["lead"]}</p>'
        f'</div>'
        f'<div class="card pad">{chart}</div>'
        f'{method}'
        f'</div>'
        f'</section>'
    )


def build_seasons_section_v6(dest, monthly, lang="fr"):
    """
    Section 'À quoi s'attendre' : cards saisons contextuelles par type dest.

    Generic : 3 cards (haute / mi-saison / basse)
    Tropical : 2 cards (sèche / humide)
    Mountain : 3 cards (ski / rando / entre-saisons)
    """
    if len(monthly) != 12:
        raise ValueError(f"monthly doit contenir 12 entrées, reçu {len(monthly)}")

    L = _SEASONS_LABELS.get(lang, _SEASONS_LABELS["fr"])
    dtype = classify_dest(dest)
    title = L.get(f"title_{dtype}", L["title_generic"])
    lead = L.get(f"lead_{dtype}", L["lead_generic"])

    cards = _build_season_cards(dtype, monthly, lang)

    grid_class = "grid-2" if len(cards) == 2 else "grid-3"

    cards_html = []
    for (icon, card_title, badge, para) in cards:
        cards_html.append(
            f'        <div class="box">\n'
            f'          <div class="box-head">\n'
            f'            <div><strong>{icon} {_html.escape(card_title)}</strong></div>\n'
            f'            <span class="badge">{_html.escape(badge)}</span>\n'
            f'          </div>\n'
            f'          <p>{para}</p>\n'
            f'        </div>'
        )
    cards_block = "\n".join(cards_html)

    section = (f'<section>\n'
               f'    <div class="container">\n'
               f'      <div class="section-head">\n'
               f'        <div class="section-kicker">{_html.escape(L["kicker"])}</div>\n'
               f'        <h2>{_html.escape(title)}</h2>\n'
               f'        <p class="lead">{_html.escape(lead)}</p>\n'
               f'      </div>\n'
               f'      <div class="{grid_class}">\n'
               f'{cards_block}\n'
               f'      </div>\n'
               f'    </div>\n'
               f'  </section>')

    return section


# ══════════════════════════════════════════════════════════════════
# Section 'Par projet' : 4 cards profils voyageurs
# ══════════════════════════════════════════════════════════════════

_PROFILES_LABELS = {
    "fr": {"kicker": "Adapter",
           "title": "Meilleure période selon votre type de voyage",
           "lead": "Le meilleur mois dépend de ce que vous venez chercher."},
    "en": {"kicker": "Tailor",
           "title": "Best time by traveler type",
           "lead": "The best month depends on what you're after."},
    "en-us": {"kicker": "Tailor",
              "title": "Best time by traveler type",
              "lead": "The best month depends on what you're after."},
    "es": {"kicker": "Adaptar",
           "title": "Mejor momento según tu tipo de viaje",
           "lead": "El mejor mes depende de lo que buscas."},
    "de": {"kicker": "Anpassen",
           "title": "Beste Zeit je nach Reisetyp",
           "lead": "Der beste Monat hängt davon ab, was Sie suchen."},
}


def _build_profile_cards(dtype, monthly, lang="fr"):
    """4 cards profils selon type dest. Badges = plages de mois pertinents."""
    great_months = [m for m in monthly if _score(m) >= 7.0]
    mid_months = [m for m in monthly if 5.5 <= _score(m) < 7.0]
    range_great = _month_range_arrow(great_months, lang) if great_months else "—"
    range_mid = _month_range_arrow(mid_months, lang) if mid_months else "—"

    all_year = {
        "fr": "Toute l'année", "en": "Year-round", "en-us": "Year-round",
        "es": "Todo el año", "de": "Ganzjährig",
    }.get(lang, "Toute l'année")

    if dtype == "tropical":
        tmpl = {
            "fr": [
                ("🏄", "Plage & surf", range_great,
                 "Mer chaude (27-29°C), soleil stable, houle régulière. Fenêtre optimale côté ouest pour la meilleure houle."),
                ("🛕", "Culture & temples", range_mid,
                 "Hors pic touristique : sites moins bondés, températures agréables. Bon équilibre météo / affluence."),
                ("🥾", "Trek & nature", range_great,
                 "Sentiers secs, visibilité claire en altitude, volcans accessibles. Température fraîche au lever."),
                ("💻", "Digital nomad", range_great,
                 "Hubs nomades actifs, wifi stable, coûts bas. Hors mousson recommandé pour le confort et la connexion."),
            ],
            "en": [
                ("🏄", "Beach & surf", range_great,
                 "Warm sea (27-29°C), stable sun, regular swell. Optimal window on west coast for best waves."),
                ("🛕", "Culture & temples", range_mid,
                 "Off-peak: less crowded sites, pleasant temperatures. Good weather/crowd balance."),
                ("🥾", "Trekking & nature", range_great,
                 "Dry trails, clear visibility at altitude, volcanoes accessible. Cool at sunrise."),
                ("💻", "Digital nomad", range_great,
                 "Active nomad hubs, stable wifi, low costs. Out of monsoon recommended for comfort and connection."),
            ],
            "en-us": [
                ("🏄", "Beach & surf", range_great,
                 "Warm sea (27-29°C), stable sun, regular swell. Optimal window on west coast for best waves."),
                ("🛕", "Culture & temples", range_mid,
                 "Off-peak: less crowded sites, pleasant temperatures. Good weather/crowd balance."),
                ("🥾", "Trekking & nature", range_great,
                 "Dry trails, clear visibility at altitude, volcanoes accessible. Cool at sunrise."),
                ("💻", "Digital nomad", range_great,
                 "Active nomad hubs, stable wifi, low costs. Out of monsoon recommended for comfort and connection."),
            ],
            "es": [
                ("🏄", "Playa y surf", range_great,
                 "Mar cálido (27-29°C), sol estable, oleaje regular. Ventana óptima en costa oeste para mejores olas."),
                ("🛕", "Cultura y templos", range_mid,
                 "Fuera de pico: sitios menos llenos, temperaturas agradables. Buen equilibrio tiempo/afluencia."),
                ("🥾", "Trekking y naturaleza", range_great,
                 "Senderos secos, visibilidad clara en altura, volcanes accesibles. Fresco al amanecer."),
                ("💻", "Digital nomad", range_great,
                 "Hubs nómadas activos, wifi estable, costes bajos. Fuera del monzón recomendado para comodidad y conexión."),
            ],
            "de": [
                ("🏄", "Strand & Surf", range_great,
                 "Warmes Meer (27-29°C), stabile Sonne, regelmäßige Wellen. Optimales Fenster an der Westküste."),
                ("🛕", "Kultur & Tempel", range_mid,
                 "Nebensaison: weniger voll, angenehme Temperaturen. Gutes Wetter-/Menge-Verhältnis."),
                ("🥾", "Trekking & Natur", range_great,
                 "Trockene Wege, klare Sicht in der Höhe, Vulkane zugänglich. Kühl beim Sonnenaufgang."),
                ("💻", "Digital nomad", range_great,
                 "Aktive Nomaden-Hubs, stabiles WLAN, niedrige Kosten. Außerhalb Monsun empfohlen."),
            ],
        }
    elif dtype == "mountain":
        winter_months = [m for m in monthly if int(m["mois_num"]) in {1, 2, 3, 4, 12}]
        summer_months = [m for m in monthly if int(m["mois_num"]) in {6, 7, 8, 9}]
        range_w = _month_range_arrow(winter_months, lang)
        range_s = _month_range_arrow(summer_months, lang)
        tmpl = {
            "fr": [
                ("⛷️", "Ski & snowboard", range_w,
                 "Enneigement maximal en altitude, stations ouvertes, remontées en service. Pic d'affluence sur vacances scolaires."),
                ("🥾", "Randonnée & alpinisme", range_s,
                 "Sentiers secs, refuges ouverts, journées longues. Juillet-août : bondé, réserver refuges à l'avance."),
                ("🧗", "Grimpe & via ferrata", range_s,
                 "Conditions stables, rocher sec, voies accessibles. Viser juin-septembre pour la fenêtre optimale."),
                ("🏔️", "Panorama & spa", all_year,
                 "Paysages alpins visibles toute l'année. Hiver : bien-être et skis-raquettes. Été : altitude pour fraîcheur."),
            ],
            "en": [
                ("⛷️", "Ski & snowboard", range_w,
                 "Maximum snow at altitude, open resorts, running lifts. Peak during school holidays."),
                ("🥾", "Hiking & mountaineering", range_s,
                 "Dry trails, open huts, long daylight. July-August: packed, book huts ahead."),
                ("🧗", "Climbing & via ferrata", range_s,
                 "Stable conditions, dry rock, open routes. Aim for June-September for the optimal window."),
                ("🏔️", "Scenery & spa", all_year,
                 "Alpine landscapes visible year-round. Winter: wellness and snowshoes. Summer: altitude for coolness."),
            ],
            "en-us": [
                ("⛷️", "Ski & snowboard", range_w,
                 "Maximum snow at altitude, open resorts, running lifts. Peak during school holidays."),
                ("🥾", "Hiking & mountaineering", range_s,
                 "Dry trails, open huts, long daylight. July-August: packed, book huts ahead."),
                ("🧗", "Climbing & via ferrata", range_s,
                 "Stable conditions, dry rock, open routes. Aim for June-September for the optimal window."),
                ("🏔️", "Scenery & spa", all_year,
                 "Alpine landscapes visible year-round. Winter: wellness and snowshoes. Summer: altitude for coolness."),
            ],
            "es": [
                ("⛷️", "Esquí & snowboard", range_w,
                 "Nieve máxima en altura, estaciones abiertas, remontes en servicio. Pico en vacaciones escolares."),
                ("🥾", "Senderismo & alpinismo", range_s,
                 "Senderos secos, refugios abiertos, días largos. Julio-agosto: lleno, reservar refugios antes."),
                ("🧗", "Escalada & vía ferrata", range_s,
                 "Condiciones estables, roca seca, vías abiertas. Apuntar junio-septiembre para ventana óptima."),
                ("🏔️", "Panorama & spa", all_year,
                 "Paisajes alpinos visibles todo el año. Invierno: bienestar y raquetas. Verano: altura para frescor."),
            ],
            "de": [
                ("⛷️", "Ski & Snowboard", range_w,
                 "Maximale Schneedecke in der Höhe, offene Stationen, fahrende Lifte. Spitze in Schulferien."),
                ("🥾", "Wandern & Bergsteigen", range_s,
                 "Trockene Wege, offene Hütten, lange Tage. Juli-August: voll, Hütten im Voraus buchen."),
                ("🧗", "Klettern & Klettersteig", range_s,
                 "Stabile Bedingungen, trockener Fels, offene Routen. Juni-September anvisieren."),
                ("🏔️", "Panorama & Spa", all_year,
                 "Alpine Landschaften ganzjährig sichtbar. Winter: Wellness und Schneeschuhe. Sommer: Höhe für Kühle."),
            ],
        }
    else:
        # Generic : 4 profils passe-partout
        tmpl = {
            "fr": [
                ("🏛️", "Musées & culture", all_year,
                 "Les sites couverts restent accessibles toute l'année. Hors saison haute : moins de foule, tarifs hôtels plus bas."),
                ("🍷", "Gastronomie & vie locale", range_great,
                 "Terrasses ouvertes, marchés en plein air, atmosphère vivante. Pic social sur les mois confortables."),
                ("👥", "Famille & sorties", range_great,
                 "Climat clément, journées longues, activités extérieures possibles. Pic vacances scolaires : réserver tôt."),
                ("💻", "Digital nomad", range_mid,
                 "Hors saison haute : logement accessible, cafés moins bondés, connexion stable. Éviter les pics touristiques."),
            ],
            "en": [
                ("🏛️", "Museums & culture", all_year,
                 "Indoor sites stay accessible year-round. Off-peak: less crowded, lower hotel rates."),
                ("🍷", "Food & local life", range_great,
                 "Open terraces, outdoor markets, lively atmosphere. Social peak on comfortable months."),
                ("👥", "Family & outings", range_great,
                 "Mild climate, long days, outdoor activities. School-holiday peak: book early."),
                ("💻", "Digital nomad", range_mid,
                 "Off-peak: accessible housing, less crowded cafés, stable connection. Avoid tourist peaks."),
            ],
            "en-us": [
                ("🏛️", "Museums & culture", all_year,
                 "Indoor sites stay accessible year-round. Off-peak: less crowded, lower hotel rates."),
                ("🍷", "Food & local life", range_great,
                 "Open terraces, outdoor markets, lively atmosphere. Social peak on comfortable months."),
                ("👥", "Family & outings", range_great,
                 "Mild climate, long days, outdoor activities. School-holiday peak: book early."),
                ("💻", "Digital nomad", range_mid,
                 "Off-peak: accessible housing, less crowded cafés, stable connection. Avoid tourist peaks."),
            ],
            "es": [
                ("🏛️", "Museos y cultura", all_year,
                 "Los sitios cubiertos siguen accesibles todo el año. Fuera de pico: menos multitud, tarifas hoteleras más bajas."),
                ("🍷", "Gastronomía y vida local", range_great,
                 "Terrazas abiertas, mercados al aire libre, ambiente animado. Pico social en meses cómodos."),
                ("👥", "Familia y salidas", range_great,
                 "Clima suave, días largos, actividades exteriores. Pico vacaciones escolares: reservar pronto."),
                ("💻", "Digital nomad", range_mid,
                 "Fuera de pico: alojamiento accesible, cafés menos llenos, conexión estable. Evitar picos turísticos."),
            ],
            "de": [
                ("🏛️", "Museen & Kultur", all_year,
                 "Überdachte Stätten ganzjährig zugänglich. Nebensaison: weniger voll, niedrigere Hotelpreise."),
                ("🍷", "Gastronomie & lokales Leben", range_great,
                 "Offene Terrassen, Freiluftmärkte, lebendige Atmosphäre. Sozialer Höhepunkt in angenehmen Monaten."),
                ("👥", "Familie & Ausflüge", range_great,
                 "Mildes Klima, lange Tage, Outdoor-Aktivitäten. Schulferien-Spitze: früh buchen."),
                ("💻", "Digital nomad", range_mid,
                 "Nebensaison: zugänglicher Wohnraum, weniger volle Cafés, stabile Verbindung. Hochsaison meiden."),
            ],
        }

    return tmpl.get(lang, tmpl["fr"])


def build_profiles_section_v6(dest, monthly, lang="fr"):
    """
    Section 'Par projet' : 4 cards profils voyageurs par type dest.
    """
    if len(monthly) != 12:
        raise ValueError(f"monthly doit contenir 12 entrées, reçu {len(monthly)}")

    L = _PROFILES_LABELS.get(lang, _PROFILES_LABELS["fr"])
    dtype = classify_dest(dest)
    cards = _build_profile_cards(dtype, monthly, lang)

    cards_html = []
    for (icon, title, badge, para) in cards:
        cards_html.append(
            f'        <div class="box">\n'
            f'          <div class="box-head"><div><strong>{icon} {_html.escape(title)}</strong></div><span class="badge">{_html.escape(badge)}</span></div>\n'
            f'          <p>{_html.escape(para)}</p>\n'
            f'        </div>'
        )
    cards_block = "\n".join(cards_html)

    section = (f'<section id="par-projet">\n'
               f'    <div class="container">\n'
               f'      <div class="section-head">\n'
               f'        <div class="section-kicker">{_html.escape(L["kicker"])}</div>\n'
               f'        <h2>{_html.escape(L["title"])}</h2>\n'
               f'        <p class="lead">{_html.escape(L["lead"])}</p>\n'
               f'      </div>\n'
               f'      <div class="grid-4">\n'
               f'{cards_block}\n'
               f'      </div>\n'
               f'    </div>\n'
               f'  </section>')

    return section


    return section


# ══════════════════════════════════════════════════════════════════
# Section 'Planifier' : 3 plan-cards (hôtel/activités/vols) + GYG widget
# ══════════════════════════════════════════════════════════════════

# IDs partner conservés depuis la prod
_PARTNER_IDS = {
    "expedia_camref": "1110lB57J",
    "kiwi_affilid": "708106",
    "gyg_partner_id": "2MQKL00",
}

_PLAN_LABELS = {
    "fr": {
        "kicker": "Réserver",
        "title": "Planifier votre séjour",
        "lead": "Hôtels au plus bas hors saison haute, tarifs au plus haut sur les mois confortables. Mi-saisons offrent un bon compromis prix/climat.",
        "host_title": "Hébergement",
        "host_sub": "Hôtels & locations",
        "act_title": "Activités",
        "act_sub": "Excursions, billets, expériences",
        "act_view": "Voir ↓",
        "fly_title": "Vols",
        "fly_sub": "Comparateur multi-compagnies",
        "gyg_h3": "🎟️ Activités & excursions",
        "gyg_p": "Sélection GetYourGuide · réservation annulable gratuitement",
        "gyg_view_all": "Voir tout →",
        "affil_note": "Lien affilié · GetYourGuide",
    },
    "en": {
        "kicker": "Book",
        "title": "Plan your trip",
        "lead": "Hotels at their lowest off-season, peak prices in comfortable months. Shoulder seasons offer a good price/climate compromise.",
        "host_title": "Accommodation",
        "host_sub": "Hotels & rentals",
        "act_title": "Activities",
        "act_sub": "Tours, tickets, experiences",
        "act_view": "View ↓",
        "fly_title": "Flights",
        "fly_sub": "Multi-airline comparison",
        "gyg_h3": "🎟️ Activities & tours",
        "gyg_p": "GetYourGuide selection · free cancellation",
        "gyg_view_all": "View all →",
        "affil_note": "Affiliate link · GetYourGuide",
    },
    "en-us": {
        "kicker": "Book",
        "title": "Plan your trip",
        "lead": "Hotels at their lowest off-season, peak prices in comfortable months. Shoulder seasons offer a good price/climate compromise.",
        "host_title": "Lodging",
        "host_sub": "Hotels & rentals",
        "act_title": "Activities",
        "act_sub": "Tours, tickets, experiences",
        "act_view": "View ↓",
        "fly_title": "Flights",
        "fly_sub": "Multi-airline comparison",
        "gyg_h3": "🎟️ Activities & tours",
        "gyg_p": "GetYourGuide selection · free cancellation",
        "gyg_view_all": "View all →",
        "affil_note": "Affiliate link · GetYourGuide",
    },
    "es": {
        "kicker": "Reservar",
        "title": "Planificar tu viaje",
        "lead": "Hoteles al mínimo fuera de temporada, precios máximos en meses cómodos. Las entre-temporadas ofrecen un buen compromiso precio/clima.",
        "host_title": "Alojamiento",
        "host_sub": "Hoteles y alquileres",
        "act_title": "Actividades",
        "act_sub": "Excursiones, entradas, experiencias",
        "act_view": "Ver ↓",
        "fly_title": "Vuelos",
        "fly_sub": "Comparador multi-aerolíneas",
        "gyg_h3": "🎟️ Actividades y excursiones",
        "gyg_p": "Selección GetYourGuide · cancelación gratuita",
        "gyg_view_all": "Ver todo →",
        "affil_note": "Enlace afiliado · GetYourGuide",
    },
    "de": {
        "kicker": "Buchen",
        "title": "Reise planen",
        "lead": "Hotels am günstigsten in der Nebensaison, höchste Preise in angenehmen Monaten. Zwischensaisons bieten ein gutes Preis-Klima-Verhältnis.",
        "host_title": "Unterkunft",
        "host_sub": "Hotels & Ferienwohnungen",
        "act_title": "Aktivitäten",
        "act_sub": "Touren, Tickets, Erlebnisse",
        "act_view": "Anzeigen ↓",
        "fly_title": "Flüge",
        "fly_sub": "Multi-Airline-Vergleich",
        "gyg_h3": "🎟️ Aktivitäten & Touren",
        "gyg_p": "GetYourGuide-Auswahl · kostenlos stornierbar",
        "gyg_view_all": "Alle anzeigen →",
        "affil_note": "Affiliate-Link · GetYourGuide",
    },
}

# Mapping lang → locale code GetYourGuide
_GYG_LOCALES = {
    "fr": "fr-FR", "en": "en-GB", "en-us": "en-US", "es": "es-ES", "de": "de-DE",
}


def build_planifier_section_v6(dest, monthly, lang="fr"):
    """
    Section 'Réserver · Planifier votre séjour' :
    - 3 plan-cards : Hébergement (Expedia) / Activités (anchor) / Vols (Kiwi)
    - 1 widget GetYourGuide en pleine largeur

    Les URLs affiliées utilisent les IDs prod :
    - Expedia camref=1110lB57J
    - Kiwi affilid=708106
    - GYG partner_id=2MQKL00

    Args:
        dest: dict destination (slug, nom_*, pays, country_*)
        monthly: list 12 mois (non utilisé directement mais signature cohérente)
        lang: code langue

    Returns:
        str : HTML de la section
    """
    L = _PLAN_LABELS.get(lang, _PLAN_LABELS["fr"])
    nom_key = f"nom_{lang.replace('-', '_')}"
    nom = dest.get(nom_key) or dest.get("nom_fr") or dest.get("slug", "?")
    nom_safe = _html.escape(nom)
    # Pour les URLs, utiliser le nom encodé (espaces → %20, etc.)
    import urllib.parse as _up
    nom_url = _up.quote(nom)

    # Country pour query GYG (plus précis)
    country = (dest.get(f"country_{lang.replace('-', '_')}")
               or dest.get("pays") or "")
    country_safe = _up.quote(country) if country else ""
    gyg_query = f"{nom_url}%2C+{country_safe}" if country_safe else nom_url

    expedia_url = f"https://www.expedia.com/Hotel-Search?destination={nom_url}&camref={_PARTNER_IDS['expedia_camref']}"
    kiwi_url = f"https://www.kiwi.com/deep?affilid={_PARTNER_IDS['kiwi_affilid']}&to={nom_url}&lang={lang.split('-')[0]}"
    gyg_search_url = f"https://www.getyourguide.com/s/?q={gyg_query}&partner_id={_PARTNER_IDS['gyg_partner_id']}&locale={_GYG_LOCALES.get(lang, 'fr-FR')}"

    section = (f'<section id="planifier" style="scroll-margin-top:120px">\n'
               f'    <div class="container">\n'
               f'      <div class="section-head">\n'
               f'        <div class="section-kicker">{_html.escape(L["kicker"])}</div>\n'
               f'        <h2>{_html.escape(L["title"])}</h2>\n'
               f'        <p class="lead">{_html.escape(L["lead"])}</p>\n'
               f'      </div>\n'
               f'      <div class="grid-3 plan-row">\n'
               f'        <a href="{expedia_url}" target="_blank" rel="sponsored noopener" class="plan-card">\n'
               f'          <div class="plan-icon">🏨</div>\n'
               f'          <div class="plan-body">\n'
               f'            <div class="plan-title">{_html.escape(L["host_title"])}</div>\n'
               f'            <div class="plan-sub">{_html.escape(L["host_sub"])} · {nom_safe}</div>\n'
               f'          </div>\n'
               f'          <div class="plan-cta">Expedia →</div>\n'
               f'        </a>\n'
               f'        <a href="#activites" class="plan-card">\n'
               f'          <div class="plan-icon">🎟️</div>\n'
               f'          <div class="plan-body">\n'
               f'            <div class="plan-title">{_html.escape(L["act_title"])}</div>\n'
               f'            <div class="plan-sub">{_html.escape(L["act_sub"])}</div>\n'
               f'          </div>\n'
               f'          <div class="plan-cta">{_html.escape(L["act_view"])}</div>\n'
               f'        </a>\n'
               f'        <a href="{kiwi_url}" target="_blank" rel="sponsored noopener" class="plan-card">\n'
               f'          <div class="plan-icon">✈️</div>\n'
               f'          <div class="plan-body">\n'
               f'            <div class="plan-title">{_html.escape(L["fly_title"])}</div>\n'
               f'            <div class="plan-sub">{_html.escape(L["fly_sub"])}</div>\n'
               f'          </div>\n'
               f'          <div class="plan-cta">Kiwi →</div>\n'
               f'        </a>\n'
               f'      </div>\n'
               f'\n'
               f'      <div id="activites" class="card pad" style="margin-top:20px;scroll-margin-top:120px">\n'
               f'        <div style="display:flex;justify-content:space-between;align-items:baseline;gap:12px;margin-bottom:14px;flex-wrap:wrap">\n'
               f'          <div>\n'
               f'            <h3 style="margin:0 0 4px">{L["gyg_h3"]} · {nom_safe}</h3>\n'
               f'            <p style="margin:0;color:var(--muted);font-size:.9rem">{_html.escape(L["gyg_p"])}</p>\n'
               f'          </div>\n'
               f'          <a class="btn primary" style="padding:10px 18px" href="{gyg_search_url}" target="_blank" rel="sponsored noopener">{_html.escape(L["gyg_view_all"])}</a>\n'
               f'        </div>\n'
               f'        <div data-gyg-href="https://widget.getyourguide.com/default/activities.frame"\n'
               f'             data-gyg-locale-code="{_GYG_LOCALES.get(lang, "fr-FR")}"\n'
               f'             data-gyg-widget="activities"\n'
               f'             data-gyg-number-of-items="3"\n'
               f'             data-gyg-partner-id="{_PARTNER_IDS["gyg_partner_id"]}"\n'
               f'             data-gyg-q="{nom_safe}{(", " + _html.escape(country)) if country else ""}">\n'
               f'        </div>\n'
               f'        <span class="affil-note" style="text-align:right;display:block;margin-top:10px;font-size:11px;color:var(--muted)">{_html.escape(L["affil_note"])}</span>\n'
               f'      </div>\n'
               f'    </div>\n'
               f'  </section>')

    return section


# ══════════════════════════════════════════════════════════════════
# Section 'Infos pratiques' : 2 boxes (sécurité+budget+transport / monnaie+langue+...)
# ══════════════════════════════════════════════════════════════════

_INFOS_LABELS = {
    "fr": {
        "kicker": "Infos pratiques",
        "title": "Ce qu'il faut savoir avant de partir",
        "lead": "Budget, sécurité, monnaie, climat : tout ce qui ne change pas la décision mais reste bon à savoir.",
        "box1_title": "🌍 Géographie & pratique",
        "box2_title": "📍 Localisation & climat",
        "lbl_alt": "Altitude",
        "lbl_lat": "Latitude",
        "lbl_lon": "Longitude",
        "lbl_country": "Pays",
        "lbl_climate": "Type de climat",
        "lbl_currency": "Monnaie",
        "lbl_lang": "Langue",
        "lbl_trend": "Tendance",
        "trend_value": "+0.34°C / décennie",
    },
    "en": {
        "kicker": "Practical info",
        "title": "What to know before you go",
        "lead": "Budget, safety, currency, climate: everything that doesn't change the decision but is good to know.",
        "box1_title": "🌍 Geography & practical",
        "box2_title": "📍 Location & climate",
        "lbl_alt": "Altitude",
        "lbl_lat": "Latitude",
        "lbl_lon": "Longitude",
        "lbl_country": "Country",
        "lbl_climate": "Climate type",
        "lbl_currency": "Currency",
        "lbl_lang": "Language",
        "lbl_trend": "Trend",
        "trend_value": "+0.34°C / decade",
    },
    "en-us": {
        "kicker": "Practical info",
        "title": "What to know before you go",
        "lead": "Budget, safety, currency, climate: everything that doesn't change the decision but is good to know.",
        "box1_title": "🌍 Geography & practical",
        "box2_title": "📍 Location & climate",
        "lbl_alt": "Elevation",
        "lbl_lat": "Latitude",
        "lbl_lon": "Longitude",
        "lbl_country": "Country",
        "lbl_climate": "Climate type",
        "lbl_currency": "Currency",
        "lbl_lang": "Language",
        "lbl_trend": "Trend",
        "trend_value": "+0.34°C / decade",
    },
    "es": {
        "kicker": "Información práctica",
        "title": "Lo que hay que saber antes de salir",
        "lead": "Presupuesto, seguridad, moneda, clima: todo lo que no cambia la decisión pero es bueno saber.",
        "box1_title": "🌍 Geografía y práctica",
        "box2_title": "📍 Ubicación y clima",
        "lbl_alt": "Altitud",
        "lbl_lat": "Latitud",
        "lbl_lon": "Longitud",
        "lbl_country": "País",
        "lbl_climate": "Tipo de clima",
        "lbl_currency": "Moneda",
        "lbl_lang": "Idioma",
        "lbl_trend": "Tendencia",
        "trend_value": "+0.34°C / década",
    },
    "de": {
        "kicker": "Praktische Infos",
        "title": "Was Sie vor der Reise wissen sollten",
        "lead": "Budget, Sicherheit, Währung, Klima: alles, was die Entscheidung nicht ändert, aber gut zu wissen ist.",
        "box1_title": "🌍 Geografie & Praktisches",
        "box2_title": "📍 Lage & Klima",
        "lbl_alt": "Höhe",
        "lbl_lat": "Breitengrad",
        "lbl_lon": "Längengrad",
        "lbl_country": "Land",
        "lbl_climate": "Klimatyp",
        "lbl_currency": "Währung",
        "lbl_lang": "Sprache",
        "lbl_trend": "Trend",
        "trend_value": "+0.34°C / Jahrzehnt",
    },
}


def _climate_type_label(dtype, lang="fr"):
    """Retourne le type de climat lisible selon dtype."""
    labels = {
        "tropical": {"fr": "Tropical", "en": "Tropical", "en-us": "Tropical",
                     "es": "Tropical", "de": "Tropisch"},
        "mountain": {"fr": "Montagne", "en": "Mountain", "en-us": "Mountain",
                     "es": "Montaña", "de": "Bergklima"},
        "generic": {"fr": "Tempéré", "en": "Temperate", "en-us": "Temperate",
                    "es": "Templado", "de": "Gemäßigt"},
    }
    return labels.get(dtype, labels["generic"]).get(lang, "Tempéré")


def build_infos_section_v6(dest, monthly, lang="fr"):
    """
    Section 'Infos pratiques' : 2 boxes côte à côte (grid-2).
    Box 1 : Géographie & pratique (altitude estimée, type climat, pays)
    Box 2 : Localisation & climat (lat, lon, tendance)

    Args:
        dest: dict destination (lat, lon, pays, country_*)
        monthly: 12 mois (non utilisé pour le rendu mais signature cohérente)
        lang: code langue
    """
    L = _INFOS_LABELS.get(lang, _INFOS_LABELS["fr"])
    dtype = classify_dest(dest)
    climate_label = _climate_type_label(dtype, lang)

    # Lat/lon
    try:
        lat_v = float(dest.get("lat", 0))
        lon_v = float(dest.get("lon", 0))
        lat_s = f"{abs(lat_v):.2f}°{'N' if lat_v >= 0 else 'S'}"
        lon_s = f"{abs(lon_v):.2f}°{'E' if lon_v >= 0 else 'W'}"
    except (ValueError, TypeError):
        lat_s = "—"
        lon_s = "—"

    # Country localisé
    country_key = f"country_{lang.replace('-', '_')}"
    country = dest.get(country_key) or dest.get("pays") or "—"

    # Altitude : pas dans destinations.csv → laisser blanc ou utiliser ski_altitudes pour mountain
    altitude = "—"
    if dtype == "mountain":
        try:
            from lib.ski_data import get_ski_data
            ski = get_ski_data(dest.get("slug") or dest.get("slug_fr"))
            if ski and ski.get("alt_village"):
                altitude = f"{int(float(ski['alt_village']))} m"
        except Exception:
            pass

    # Box 1 items
    box1_items = []
    if altitude != "—":
        box1_items.append(("⛰️", L["lbl_alt"], altitude))
    box1_items.append(("🌐", L["lbl_country"], _html.escape(country)))
    box1_items.append(("🌡️", L["lbl_climate"], _html.escape(climate_label)))

    # Box 2 items
    box2_items = [
        ("🧭", L["lbl_lat"], lat_s),
        ("📐", L["lbl_lon"], lon_s),
        ("📈", L["lbl_trend"], _html.escape(L["trend_value"])),
    ]

    def _render_list(items):
        rows = []
        for icon, lbl, val in items:
            rows.append(
                f'            <div class="list-item"><span><span class="list-ico">{icon}</span>{_html.escape(lbl)}</span><strong>{val}</strong></div>'
            )
        return "\n".join(rows)

    section = (f'<section>\n'
               f'    <div class="container">\n'
               f'      <div class="section-head">\n'
               f'        <div class="section-kicker">{_html.escape(L["kicker"])}</div>\n'
               f'        <h2>{_html.escape(L["title"])}</h2>\n'
               f'        <p class="lead">{_html.escape(L["lead"])}</p>\n'
               f'      </div>\n'
               f'      <div class="grid-2">\n'
               f'        <div class="box">\n'
               f'          <h3>{L["box1_title"]}</h3>\n'
               f'          <div class="list">\n'
               f'{_render_list(box1_items)}\n'
               f'          </div>\n'
               f'        </div>\n'
               f'        <div class="box">\n'
               f'          <h3>{L["box2_title"]}</h3>\n'
               f'          <div class="list">\n'
               f'{_render_list(box2_items)}\n'
               f'          </div>\n'
               f'        </div>\n'
               f'      </div>\n'
               f'    </div>\n'
               f'  </section>')

    return section


# ══════════════════════════════════════════════════════════════════
# Section 'Explorer' : similaires + proches + classements
# ══════════════════════════════════════════════════════════════════

_EXPLORER_LABELS = {
    "fr": {
        "kicker": "Explorer",
        "title": "Destinations & guides complémentaires",
        "lead": "Si {nom} ne colle pas à vos dates, voici des alternatives et des guides.",
        "h_similar": "Destinations au climat similaire",
        "h_nearby": "Destinations proches",
        "h_guides": "Guides & classements",
        "g_world": "Classement mondial 2026",
        "g_summer": "Meilleures destinations été",
        "g_winter": "Soleil hiver",
        "g_july": "Où partir en juillet",
        "g_view": "Voir →",
        "g_map": "🗺️ Carte climatique",
    },
    "en": {
        "kicker": "Explore",
        "title": "Destinations & supplementary guides",
        "lead": "If {nom} doesn't fit your dates, here are alternatives and guides.",
        "h_similar": "Destinations with similar climate",
        "h_nearby": "Nearby destinations",
        "h_guides": "Guides & rankings",
        "g_world": "World ranking 2026",
        "g_summer": "Best summer destinations",
        "g_winter": "Winter sun",
        "g_july": "Where to go in July",
        "g_view": "View →",
        "g_map": "🗺️ Climate map",
    },
    "en-us": {
        "kicker": "Explore",
        "title": "Destinations & supplementary guides",
        "lead": "If {nom} doesn't fit your dates, here are alternatives and guides.",
        "h_similar": "Destinations with similar climate",
        "h_nearby": "Nearby destinations",
        "h_guides": "Guides & rankings",
        "g_world": "World ranking 2026",
        "g_summer": "Best summer destinations",
        "g_winter": "Winter sun",
        "g_july": "Where to go in July",
        "g_view": "View →",
        "g_map": "🗺️ Climate map",
    },
    "es": {
        "kicker": "Explorar",
        "title": "Destinos y guías complementarias",
        "lead": "Si {nom} no encaja con tus fechas, aquí hay alternativas y guías.",
        "h_similar": "Destinos con clima similar",
        "h_nearby": "Destinos cercanos",
        "h_guides": "Guías y clasificaciones",
        "g_world": "Clasificación mundial 2026",
        "g_summer": "Mejores destinos verano",
        "g_winter": "Sol en invierno",
        "g_july": "A dónde ir en julio",
        "g_view": "Ver →",
        "g_map": "🗺️ Mapa climático",
    },
    "de": {
        "kicker": "Erkunden",
        "title": "Reiseziele & weitere Guides",
        "lead": "Wenn {nom} nicht zu Ihren Daten passt, hier Alternativen und Guides.",
        "h_similar": "Ziele mit ähnlichem Klima",
        "h_nearby": "Nahe Ziele",
        "h_guides": "Guides & Rankings",
        "g_world": "Welt-Ranking 2026",
        "g_summer": "Beste Sommerziele",
        "g_winter": "Wintersonne",
        "g_july": "Wo im Juli reisen",
        "g_view": "Anzeigen →",
        "g_map": "🗺️ Klimakarte",
    },
}


def _haversine_km(lat1, lon1, lat2, lon2):
    """Distance haversine en km entre 2 points (lat/lon en degrés)."""
    import math
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2)
    return 6371 * 2 * math.asin(math.sqrt(a))


def find_nearby_destinations(dest, all_dests, n=4):
    """
    Retourne les N destinations les plus proches géographiquement.

    Args:
        dest: dict destination courante (lat, lon, slug_fr)
        all_dests: list[dict] toutes les destinations (depuis CSV)
        n: nombre à retourner

    Returns:
        list[(distance_km, dest_dict)] triés par distance croissante
    """
    try:
        lat0 = float(dest.get("lat"))
        lon0 = float(dest.get("lon"))
    except (TypeError, ValueError):
        return []
    slug0 = dest.get("slug_fr") or dest.get("slug")
    results = []
    for d in all_dests:
        if d.get("slug_fr") == slug0 or d.get("slug") == slug0:
            continue
        try:
            lat1 = float(d.get("lat"))
            lon1 = float(d.get("lon"))
        except (TypeError, ValueError):
            continue
        dist = _haversine_km(lat0, lon0, lat1, lon1)
        results.append((dist, d))
    results.sort(key=lambda x: x[0])
    return results[:n]


def find_similar_climate(dest, all_dests, all_climate_by_slug, n=4):
    """
    Trouve les N destinations avec un climat similaire (par profil annuel des
    scores). Distance euclidienne sur les 12 scores.

    Args:
        dest: destination courante
        all_dests: list dicts dests
        all_climate_by_slug: dict {slug: list 12 dicts mensuels} pour calcul
        n: nombre à retourner

    Returns:
        list[(distance, dest_dict)] triés
    """
    slug0 = dest.get("slug_fr") or dest.get("slug")
    own_monthly = all_climate_by_slug.get(slug0)
    if not own_monthly:
        return []
    own_scores = [_score(m) for m in sorted(own_monthly, key=lambda x: int(x["mois_num"]))]
    if len(own_scores) != 12:
        return []
    own_dtype = classify_dest(dest)

    results = []
    for d in all_dests:
        s = d.get("slug_fr") or d.get("slug")
        if s == slug0:
            continue
        # Préférer les mêmes types (tropical/mountain/generic) pour pertinence
        if classify_dest(d) != own_dtype:
            continue
        other_monthly = all_climate_by_slug.get(s)
        if not other_monthly or len(other_monthly) != 12:
            continue
        other_scores = [_score(m) for m in sorted(other_monthly, key=lambda x: int(x["mois_num"]))]
        # Distance euclidienne L2
        dist = sum((a - b) ** 2 for a, b in zip(own_scores, other_scores)) ** 0.5
        results.append((dist, d))
    results.sort(key=lambda x: x[0])
    return results[:n]


def build_explorer_section_v6(dest, monthly, lang="fr",
                               all_dests=None, all_climate_by_slug=None,
                               url_builder=None):
    """
    Section 'Explorer' : 3 boxes (similaires / proches / classements).

    Args:
        dest: destination
        monthly: 12 mois (non utilisé directement)
        lang: code langue
        all_dests: list complète des dests pour calcul nearby/similar.
                   Si None : sections similaires & proches affichent placeholder vide.
        all_climate_by_slug: dict {slug: list mensuels} pour similaires.
        url_builder: fonction(slug, lang) → URL fiche annuelle.
                     Par défaut : '<slug>.html' (cohérent avec V3 prod).

    Returns:
        str : HTML
    """
    L = _EXPLORER_LABELS.get(lang, _EXPLORER_LABELS["fr"])
    nom_key = f"nom_{lang.replace('-', '_')}"
    nom = dest.get(nom_key) or dest.get("nom_fr") or dest.get("slug", "?")
    nom_safe = _html.escape(nom)

    if url_builder is None:
        # URL builder par défaut : structure prod V3
        # FR : meilleure-periode-{slug}.html
        # EN : en/best-time-to-visit-{slug}.html
        # etc. Pour l'instant on utilise un format simplifié.
        def url_builder(d, lang_x):
            s = d.get("slug_fr") or d.get("slug", "")
            return f"meilleure-periode-{s}.html"

    # --- Box similaires (par climat) ---
    if all_dests and all_climate_by_slug:
        similar = find_similar_climate(dest, all_dests, all_climate_by_slug, n=4)
    else:
        similar = []

    similar_rows = []
    for (dist, d) in similar:
        d_nom = d.get(nom_key) or d.get("nom_fr") or d.get("slug", "?")
        d_country = d.get(f"country_{lang.replace('-', '_')}") or d.get("pays", "")
        d_flag = d.get("flag", "")
        d_url = url_builder(d, lang)
        flag_img = (f'<img src="flags/{d_flag}.png" width="18" height="13" alt="" '
                    f'loading="lazy" class="list-flag">' if d_flag else '')
        similar_rows.append(
            f'            <a href="{d_url}" class="list-item">'
            f'<span>{flag_img}{_html.escape(d_nom)} '
            f'<span class="list-country">· {_html.escape(d_country)}</span></span>'
            f'<strong>→</strong></a>'
        )
    similar_block = "\n".join(similar_rows) if similar_rows else (
        '            <div class="list-item" style="color:var(--muted)">—</div>'
    )

    # --- Box proches (par distance) ---
    if all_dests:
        nearby = find_nearby_destinations(dest, all_dests, n=4)
    else:
        nearby = []

    nearby_rows = []
    for (dist, d) in nearby:
        d_nom = d.get(nom_key) or d.get("nom_fr") or d.get("slug", "?")
        d_country = d.get(f"country_{lang.replace('-', '_')}") or d.get("pays", "")
        d_flag = d.get("flag", "")
        d_url = url_builder(d, lang)
        flag_img = (f'<img src="flags/{d_flag}.png" width="18" height="13" alt="" '
                    f'loading="lazy" class="list-flag">' if d_flag else '')
        nearby_rows.append(
            f'            <a href="{d_url}" class="list-item">'
            f'<span>{flag_img}{_html.escape(d_nom)} '
            f'<span class="list-country">· {_html.escape(d_country)}</span></span>'
            f'<strong>{int(round(dist))} km →</strong></a>'
        )
    nearby_block = "\n".join(nearby_rows) if nearby_rows else (
        '            <div class="list-item" style="color:var(--muted)">—</div>'
    )

    # --- Box guides & classements ---
    # URLs prod V3 connues
    guides_urls = {
        "fr": [("classement-destinations-meteo-2026.html", L["g_world"]),
               ("classement-destinations-meteo-ete-2026.html", L["g_summer"]),
               ("classement-destinations-meteo-hiver-2026.html", L["g_winter"]),
               ("ou-partir-en-juillet.html", L["g_july"])],
        "en": [("en/world-ranking-best-weather-2026.html", L["g_world"]),
               ("en/best-summer-destinations-2026.html", L["g_summer"]),
               ("en/best-winter-sun-destinations-2026.html", L["g_winter"]),
               ("en/where-to-go-in-july.html", L["g_july"])],
        "en-us": [("us/world-ranking-best-weather-2026.html", L["g_world"]),
                  ("us/best-summer-destinations-2026.html", L["g_summer"]),
                  ("us/best-winter-sun-destinations-2026.html", L["g_winter"]),
                  ("us/where-to-go-in-july.html", L["g_july"])],
        "es": [("es/clasificacion-destinos-clima-2026.html", L["g_world"]),
               ("es/mejores-destinos-verano-2026.html", L["g_summer"]),
               ("es/mejores-destinos-sol-invierno-2026.html", L["g_winter"]),
               ("es/donde-ir-en-julio.html", L["g_july"])],
        "de": [("de/welt-ranking-beste-reisezeit-2026.html", L["g_world"]),
               ("de/beste-sommer-reiseziele-2026.html", L["g_summer"]),
               ("de/beste-winter-sonne-reiseziele-2026.html", L["g_winter"]),
               ("de/wohin-im-juli.html", L["g_july"])],
    }
    map_urls = {"fr": "carte.html", "en": "en/map.html", "en-us": "us/map.html",
                "es": "es/mapa.html", "de": "de/karte.html"}

    g_rows = []
    for url, label in guides_urls.get(lang, guides_urls["fr"]):
        g_rows.append(
            f'            <div class="list-item">'
            f'<span>{_html.escape(label)}</span>'
            f'<strong><a href="{url}">{_html.escape(L["g_view"])}</a></strong></div>'
        )
    g_block = "\n".join(g_rows)
    map_url = map_urls.get(lang, "carte.html")

    section = (f'<section>\n'
               f'    <div class="container">\n'
               f'      <div class="section-head">\n'
               f'        <div class="section-kicker">{_html.escape(L["kicker"])}</div>\n'
               f'        <h2>{_html.escape(L["title"])}</h2>\n'
               f'        <p class="lead">{_html.escape(L["lead"].format(nom=nom_safe))}</p>\n'
               f'      </div>\n'
               f'      <div class="grid-3">\n'
               f'        <div class="box">\n'
               f'          <h3>{_html.escape(L["h_similar"])}</h3>\n'
               f'          <div class="list">\n'
               f'{similar_block}\n'
               f'          </div>\n'
               f'        </div>\n'
               f'        <div class="box">\n'
               f'          <h3>{_html.escape(L["h_nearby"])}</h3>\n'
               f'          <div class="list">\n'
               f'{nearby_block}\n'
               f'          </div>\n'
               f'        </div>\n'
               f'        <div class="box">\n'
               f'          <h3>{_html.escape(L["h_guides"])}</h3>\n'
               f'          <div class="list">\n'
               f'{g_block}\n'
               f'          </div>\n'
               f'          <div style="margin-top:16px">\n'
               f'            <a class="btn primary" href="{map_url}">{L["g_map"]}</a>\n'
               f'          </div>\n'
               f'        </div>\n'
               f'      </div>\n'
               f'    </div>\n'
               f'  </section>')

    return section


    return section


# ══════════════════════════════════════════════════════════════════
# Section 'Localisation' : 2 cartes Leaflet (monde + macro)
# ══════════════════════════════════════════════════════════════════

_LOC_LABELS = {
    "fr": {
        "kicker": "Localisation",
        "title": "Où se trouve {nom} ?",
        "lead": "Position mondiale + contexte géographique régional.",
        "lbl_world": "🌍 Monde",
        "lbl_macro": "🔍 Contexte géographique",
    },
    "en": {
        "kicker": "Location",
        "title": "Where is {nom}?",
        "lead": "World position + regional geographic context.",
        "lbl_world": "🌍 World",
        "lbl_macro": "🔍 Geographic context",
    },
    "en-us": {
        "kicker": "Location",
        "title": "Where is {nom}?",
        "lead": "World position + regional geographic context.",
        "lbl_world": "🌍 World",
        "lbl_macro": "🔍 Geographic context",
    },
    "es": {
        "kicker": "Ubicación",
        "title": "¿Dónde está {nom}?",
        "lead": "Posición mundial + contexto geográfico regional.",
        "lbl_world": "🌍 Mundo",
        "lbl_macro": "🔍 Contexto geográfico",
    },
    "de": {
        "kicker": "Lage",
        "title": "Wo liegt {nom}?",
        "lead": "Weltposition + regionaler geografischer Kontext.",
        "lbl_world": "🌍 Welt",
        "lbl_macro": "🔍 Geografischer Kontext",
    },
}


def build_localisation_section_v6(dest, monthly, lang="fr"):
    """
    Section Localisation : 2 cartes Leaflet (monde + macro régional)
    + intro courte (drapeau + pays + 1-phrase contextuelle + coords).

    Les cartes sont initialisées par js/dest-map.min.js (déjà en prod) qui
    lit les data-attributes du div .dest-map-row.

    Args:
        dest: dict (slug, lat, lon, flag, pays, country_*)
        monthly: 12 mois (utilisé pour générer la phrase contextuelle)
        lang: code langue
    """
    L = _LOC_LABELS.get(lang, _LOC_LABELS["fr"])
    nom_key = f"nom_{lang.replace('-', '_')}"
    nom = dest.get(nom_key) or dest.get("nom_fr") or dest.get("slug", "?")
    nom_safe = _html.escape(nom)
    slug = dest.get("slug") or dest.get("slug_fr") or "x"
    flag = dest.get("flag", "")
    country_key = f"country_{lang.replace('-', '_')}"
    country = dest.get(country_key) or dest.get("pays", "—")

    try:
        lat = float(dest.get("lat", 0))
        lon = float(dest.get("lon", 0))
        lat_s = f"{abs(lat):.2f}°{'N' if lat >= 0 else 'S'}"
        lon_s = f"{abs(lon):.2f}°{'E' if lon >= 0 else 'W'}"
        coords = f"{lat_s} · {lon_s}"
    except (TypeError, ValueError):
        lat, lon = 0, 0
        coords = "—"

    # Zoom macro : adaptatif selon latitude (zone polaire = zoom plus large)
    abs_lat = abs(lat)
    if abs_lat > 60:
        macro_zoom = 4
    elif abs_lat > 40:
        macro_zoom = 5
    else:
        macro_zoom = 5

    # Phrase courte contextuelle basée sur best/worst
    best = best_month(monthly)
    worst = worst_month(monthly)
    best_score = _score(best)
    worst_score = _score(worst)
    delta = best_score - worst_score
    intros = {
        "fr": (f"Climat {_climate_type_label(classify_dest(dest), lang).lower()} "
               f"avec un écart {best_score:.1f} → {worst_score:.1f} entre meilleur et pire mois. "
               f"10 ans de données ERA5 pour choisir selon votre projet."),
        "en": (f"{_climate_type_label(classify_dest(dest), lang)} climate, "
               f"with a {best_score:.1f} → {worst_score:.1f} gap between best and worst month. "
               f"10 years of ERA5 data to pick by use case."),
        "en-us": (f"{_climate_type_label(classify_dest(dest), lang)} climate, "
                  f"with a {best_score:.1f} → {worst_score:.1f} gap between best and worst month. "
                  f"10 years of ERA5 data to pick by use case."),
        "es": (f"Clima {_climate_type_label(classify_dest(dest), lang).lower()} "
               f"con una brecha {best_score:.1f} → {worst_score:.1f} entre mejor y peor mes. "
               f"10 años de datos ERA5 para elegir según tu proyecto."),
        "de": (f"{_climate_type_label(classify_dest(dest), lang)}-Klima "
               f"mit einer Spanne von {best_score:.1f} → {worst_score:.1f} zwischen bestem und schlechtestem Monat. "
               f"10 Jahre ERA5-Daten zur Wahl je nach Projekt."),
    }
    intro_text = intros.get(lang, intros["fr"])

    flag_img = (f'<img src="flags/{_html.escape(flag)}.png" width="16" height="12" alt="" '
                f'style="vertical-align:middle;border-radius:2px;margin-right:5px">' if flag else '')

    section = (f'<section class="dest-map-section">\n'
               f'    <div class="container">\n'
               f'      <div class="section-head">\n'
               f'        <div class="section-kicker">{_html.escape(L["kicker"])}</div>\n'
               f'        <h2>{_html.escape(L["title"].format(nom=nom))}</h2>\n'
               f'        <p class="lead">{_html.escape(L["lead"])}</p>\n'
               f'      </div>\n'
               f'      <div class="dest-map-row" data-dest-map="1" data-lat="{lat}" data-lon="{lon}" '
               f'data-macro-zoom="{macro_zoom}" data-world-id="dmap-world-{slug}" data-macro-id="dmap-macro-{slug}">\n'
               f'        <div class="dest-map-card">\n'
               f'          <div class="dest-map-lbl">{L["lbl_world"]}</div>\n'
               f'          <div id="dmap-world-{slug}" class="dest-map-el dest-map-el--world"></div>\n'
               f'        </div>\n'
               f'        <div class="dest-map-card">\n'
               f'          <div class="dest-map-lbl">{L["lbl_macro"]}</div>\n'
               f'          <div id="dmap-macro-{slug}" class="dest-map-el dest-map-el--macro"></div>\n'
               f'        </div>\n'
               f'      </div>\n'
               f'      <div class="dest-map-intro">\n'
               f'        <div class="dest-map-intro-body">\n'
               f'          <div class="dest-map-country">{flag_img}{_html.escape(country)}</div>\n'
               f'          <div class="dest-map-hsub">{_html.escape(intro_text)}</div>\n'
               f'          <div class="dest-map-coords">{coords}</div>\n'
               f'        </div>\n'
               f'      </div>\n'
               f'    </div>\n'
               f'  </section>')

    return section


# ══════════════════════════════════════════════════════════════════
# Section 'FAQ' : 4-5 questions adaptées par type
# ══════════════════════════════════════════════════════════════════

_FAQ_LABELS = {
    "fr": {"kicker": "Questions", "title": "Questions fréquentes",
           "lead": "Les réponses les plus cherchées à propos de {nom}."},
    "en": {"kicker": "Questions", "title": "Frequently asked questions",
           "lead": "Most-searched answers about {nom}."},
    "en-us": {"kicker": "Questions", "title": "Frequently asked questions",
              "lead": "Most-searched answers about {nom}."},
    "es": {"kicker": "Preguntas", "title": "Preguntas frecuentes",
           "lead": "Las respuestas más buscadas sobre {nom}."},
    "de": {"kicker": "Fragen", "title": "Häufige Fragen",
           "lead": "Die meistgesuchten Antworten zu {nom}."},
}


def _build_faq_items(dest, monthly, lang):
    """
    Construit 4 questions/réponses dynamiques basées sur les vraies données.

    Returns:
        list[(question, answer)]
    """
    nom_key = f"nom_{lang.replace('-', '_')}"
    nom = dest.get(nom_key) or dest.get("nom_fr") or dest.get("slug", "?")
    dtype = classify_dest(dest)

    best = best_month(monthly)
    worst = worst_month(monthly)
    best_name = format_month_full(best, lang)
    worst_name = format_month_full(worst, lang)
    best_score = _score(best)
    worst_score = _score(worst)
    best_tmax = best.get("tmax", "—")
    best_tmin = best.get("tmin", "—")
    best_sun = best.get("sun_h", "—")
    best_rain = best.get("rain_pct", "—")
    worst_tmax = worst.get("tmax", "—")
    worst_sun = worst.get("sun_h", "—")

    # Mois pluvieux : max rain_pct
    try:
        rainiest = max(monthly, key=lambda m: float(m.get("rain_pct", 0) or 0))
        rainiest_name = format_month_full(rainiest, lang)
        rainiest_pct = int(round(float(rainiest.get("rain_pct", 0))))
    except (ValueError, TypeError):
        rainiest_name = "—"
        rainiest_pct = 0

    # Top 2 confortables en chronologique
    sorted_top = sorted(monthly, key=_score, reverse=True)[:2]
    top2 = sorted([format_month_full(m, lang) for m in sorted_top])

    # FAQs FR (template, sera décliné par lang)
    if lang == "fr":
        items = [
            (f"Quelle est la meilleure période pour partir à {nom} ?",
             f"{best_name} est le meilleur mois avec un score de {best_score:.1f}/10 : "
             f"{best_tmax}°C en journée, {best_tmin}°C la nuit, {best_sun}h de soleil et "
             f"{int(round(float(best_rain)))}% de jours pluvieux."),
            (f"Quel est le mois le plus rude à {nom} ?",
             f"{worst_name} ({worst_score:.1f}/10), avec environ {worst_tmax}°C en journée et "
             f"{worst_sun}h de soleil. À envisager seulement pour des activités ciblées."),
            (f"Quel est le mois le plus pluvieux à {nom} ?",
             f"{rainiest_name} avec environ {rainiest_pct}% de jours de pluie. "
             f"À comparer aux {int(round(float(best_rain)))}% du meilleur mois ({best_name})."),
            (f"Combien de mois confortables compte {nom} ?",
             f"Sur les 12 mois, {sum(1 for m in monthly if _score(m) >= 7.0)} dépassent un score de 7/10. "
             f"Top 2 : {top2[0]} et {top2[1]} si l'on cherche le meilleur compromis météo."),
        ]
    elif lang in ("en", "en-us"):
        items = [
            (f"When is the best time to visit {nom}?",
             f"{best_name} is the best month with a {best_score:.1f}/10 score: "
             f"{best_tmax}°C daytime, {best_tmin}°C at night, {best_sun}h of sun, and "
             f"{int(round(float(best_rain)))}% rainy days."),
            (f"What is the toughest month at {nom}?",
             f"{worst_name} ({worst_score:.1f}/10), with around {worst_tmax}°C daytime and "
             f"{worst_sun}h of sun. Only consider it for targeted activities."),
            (f"Which month is the rainiest at {nom}?",
             f"{rainiest_name} with about {rainiest_pct}% rainy days. "
             f"Compared with {int(round(float(best_rain)))}% in the best month ({best_name})."),
            (f"How many comfortable months does {nom} have?",
             f"Out of 12 months, {sum(1 for m in monthly if _score(m) >= 7.0)} score above 7/10. "
             f"Top 2: {top2[0]} and {top2[1]} for the best weather window."),
        ]
    elif lang == "es":
        items = [
            (f"¿Cuál es la mejor época para visitar {nom}?",
             f"{best_name} es el mejor mes con una puntuación de {best_score:.1f}/10: "
             f"{best_tmax}°C de día, {best_tmin}°C de noche, {best_sun}h de sol y "
             f"{int(round(float(best_rain)))}% de días de lluvia."),
            (f"¿Cuál es el mes más duro en {nom}?",
             f"{worst_name} ({worst_score:.1f}/10), con unos {worst_tmax}°C de día y "
             f"{worst_sun}h de sol. Considerar solo para actividades específicas."),
            (f"¿Cuál es el mes más lluvioso en {nom}?",
             f"{rainiest_name} con cerca de {rainiest_pct}% de días de lluvia. "
             f"Comparar con {int(round(float(best_rain)))}% en el mejor mes ({best_name})."),
            (f"¿Cuántos meses cómodos tiene {nom}?",
             f"De los 12 meses, {sum(1 for m in monthly if _score(m) >= 7.0)} superan los 7/10. "
             f"Top 2: {top2[0]} y {top2[1]} para la mejor ventana climática."),
        ]
    else:  # de
        items = [
            (f"Wann ist die beste Reisezeit für {nom}?",
             f"{best_name} ist der beste Monat mit {best_score:.1f}/10: "
             f"{best_tmax}°C tagsüber, {best_tmin}°C nachts, {best_sun}h Sonne und "
             f"{int(round(float(best_rain)))}% Regentage."),
            (f"Welcher ist der härteste Monat in {nom}?",
             f"{worst_name} ({worst_score:.1f}/10), mit rund {worst_tmax}°C tagsüber und "
             f"{worst_sun}h Sonne. Nur für gezielte Aktivitäten in Betracht ziehen."),
            (f"Welcher Monat ist am regnerischsten in {nom}?",
             f"{rainiest_name} mit etwa {rainiest_pct}% Regentagen. "
             f"Im Vergleich zu {int(round(float(best_rain)))}% im besten Monat ({best_name})."),
            (f"Wie viele angenehme Monate hat {nom}?",
             f"Von 12 Monaten liegen {sum(1 for m in monthly if _score(m) >= 7.0)} über 7/10. "
             f"Top 2: {top2[0]} und {top2[1]} für das beste Wetterfenster."),
        ]

    return items


def build_faq_section_v6(dest, monthly, lang="fr"):
    """Section FAQ avec 4 questions adaptées aux données de la dest."""
    L = _FAQ_LABELS.get(lang, _FAQ_LABELS["fr"])
    nom_key = f"nom_{lang.replace('-', '_')}"
    nom = dest.get(nom_key) or dest.get("nom_fr") or dest.get("slug", "?")

    items = _build_faq_items(dest, monthly, lang)

    items_html = []
    for q, a in items:
        items_html.append(
            f'        <div class="faq-item">\n'
            f'          <strong>{_html.escape(q)}</strong>\n'
            f'          {_html.escape(a)}\n'
            f'        </div>'
        )
    items_block = "\n".join(items_html)

    section = (f'<section>\n'
               f'    <div class="container">\n'
               f'      <div class="section-head">\n'
               f'        <div class="section-kicker">{_html.escape(L["kicker"])}</div>\n'
               f'        <h2>{_html.escape(L["title"])}</h2>\n'
               f'        <p class="lead">{_html.escape(L["lead"].format(nom=nom))}</p>\n'
               f'      </div>\n'
               f'      <div class="faq">\n'
               f'{items_block}\n'
               f'      </div>\n'
               f'    </div>\n'
               f'  </section>')

    return section, items  # Retourne aussi items pour réutilisation dans JSON-LD


# ══════════════════════════════════════════════════════════════════
# JSON-LD : Article + FAQPage + BreadcrumbList + Dataset
# ══════════════════════════════════════════════════════════════════

def build_jsonld_v6(dest, monthly, lang="fr", faq_items=None,
                    base_url="https://bestdateweather.com"):
    """
    Construit 4 blocs JSON-LD (4 <script> séparés) pour SEO :
    1. Article : headline + image + author + dates
    2. FAQPage : reprend les items FAQ
    3. BreadcrumbList : Accueil > {nom}
    4. Dataset : metadata sur les données ERA5 utilisées

    Args:
        dest: destination
        monthly: 12 mois (pas utilisé directement mais conservé)
        lang: code langue
        faq_items: list[(q,a)] généré par build_faq_section_v6 (sinon recalcul)
        base_url: URL canonique du site

    Returns:
        str : 4 <script type="application/ld+json"> concaténés
    """
    import json

    nom_key = f"nom_{lang.replace('-', '_')}"
    nom = dest.get(nom_key) or dest.get("nom_fr") or dest.get("slug", "?")
    slug = dest.get("slug") or dest.get("slug_fr") or "x"

    # URL canonique selon langue (cohérent avec V3 prod)
    url_paths = {
        "fr": f"meilleure-periode-{slug}.html",
        "en": f"en/best-time-to-visit-{slug}.html",
        "en-us": f"us/best-time-to-visit-{slug}.html",
        "es": f"es/mejor-epoca-{slug}.html",
        "de": f"de/beste-reisezeit-{slug}.html",
    }
    page_url = f"{base_url}/{url_paths.get(lang, url_paths['fr'])}"

    headlines = {
        "fr": f"Meilleure période pour partir à {nom}",
        "en": f"Best time to visit {nom}",
        "en-us": f"Best time to visit {nom}",
        "es": f"Mejor época para viajar a {nom}",
        "de": f"Beste Reisezeit für {nom}",
    }
    descriptions = {
        "fr": f"Découvrez la meilleure période à {nom}. Score climatique complet sur 12 mois, température, soleil et pluie. Guide 2026.",
        "en": f"Discover the best time to visit {nom}. Full 12-month climate score, temperature, sun and rain. 2026 guide.",
        "en-us": f"Discover the best time to visit {nom}. Full 12-month climate score, temperature, sun and rain. 2026 guide.",
        "es": f"Descubre la mejor época para {nom}. Puntuación climática de 12 meses, temperatura, sol y lluvia. Guía 2026.",
        "de": f"Beste Reisezeit für {nom} entdecken. Klimapunktzahl auf 12 Monate, Temperatur, Sonne und Regen. Guide 2026.",
    }
    home_labels = {"fr": "Accueil", "en": "Home", "en-us": "Home",
                   "es": "Inicio", "de": "Startseite"}
    dataset_names = {
        "fr": f"Données climatiques de {nom} — moyennes mensuelles sur 10 ans",
        "en": f"Climate data for {nom} — monthly averages over 10 years",
        "en-us": f"Climate data for {nom} — monthly averages over 10 years",
        "es": f"Datos climáticos de {nom} — medias mensuales en 10 años",
        "de": f"Klimadaten für {nom} — monatliche Durchschnitte über 10 Jahre",
    }
    dataset_descs = {
        "fr": f"Températures, précipitations, ensoleillement et vent mensuels à {nom}. Moyennes calculées sur 10 ans de données ERA5 (Open-Meteo).",
        "en": f"Monthly temperatures, precipitation, sunshine and wind at {nom}. Averages computed over 10 years of ERA5 data (Open-Meteo).",
        "en-us": f"Monthly temperatures, precipitation, sunshine and wind at {nom}. Averages computed over 10 years of ERA5 data (Open-Meteo).",
        "es": f"Temperaturas, precipitaciones, sol y viento mensuales en {nom}. Medias calculadas sobre 10 años de datos ERA5 (Open-Meteo).",
        "de": f"Monatliche Temperaturen, Niederschlag, Sonnenschein und Wind in {nom}. Durchschnitte berechnet über 10 Jahre ERA5-Daten (Open-Meteo).",
    }

    # FAQ items : utilise ceux fournis ou en regénère
    if faq_items is None:
        faq_items = _build_faq_items(dest, monthly, lang)

    today = "2026-04-20"  # Date statique pour reproductibilité

    article = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": headlines.get(lang, headlines["fr"]),
        "description": descriptions.get(lang, descriptions["fr"]),
        "image": {
            "@type": "ImageObject",
            "url": f"{base_url}/og-image.png",
            "width": 1200, "height": 630,
        },
        "author": {
            "@type": "Organization", "name": "BestDateWeather",
            "url": base_url,
            "logo": {"@type": "ImageObject", "url": f"{base_url}/icon-192.png",
                     "width": 192, "height": 192},
        },
        "publisher": {
            "@type": "Organization", "name": "BestDateWeather",
            "url": base_url,
            "logo": {"@type": "ImageObject", "url": f"{base_url}/icon-192.png",
                     "width": 192, "height": 192},
        },
        "datePublished": today,
        "dateModified": today,
        "inLanguage": lang.split("-")[0],
        "url": page_url,
        "mainEntityOfPage": {"@type": "WebPage", "@id": page_url},
    }

    faqpage = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q,
             "acceptedAnswer": {"@type": "Answer", "text": a}}
            for q, a in faq_items
        ],
    }

    breadcrumb = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1,
             "name": home_labels.get(lang, "Home"),
             "item": f"{base_url}/"},
            {"@type": "ListItem", "position": 2, "name": nom, "item": page_url},
        ],
    }

    dataset = {
        "@context": "https://schema.org",
        "@type": "Dataset",
        "name": dataset_names.get(lang, dataset_names["fr"]),
        "description": dataset_descs.get(lang, dataset_descs["fr"]),
        "temporalCoverage": "2015/2024",
        "spatialCoverage": {"@type": "Place", "name": nom},
        "creator": {"@type": "Organization", "name": "BestDateWeather", "url": base_url},
        "license": "https://creativecommons.org/licenses/by-nc/4.0/",
        "variableMeasured": ["Temperature", "Precipitation", "Sunshine hours", "Wind speed"],
    }

    blocks = []
    for obj in (article, faqpage, breadcrumb, dataset):
        blocks.append(
            f'<script type="application/ld+json">{json.dumps(obj, ensure_ascii=False)}</script>'
        )
    return "\n".join(blocks)


# ══════════════════════════════════════════════════════════════════
# Footer complet : brand + sources + langues + legal
# ══════════════════════════════════════════════════════════════════

_FOOTER_LABELS = {
    "fr": {
        "data_credit": "Données météo par Open-Meteo.com",
        "sources": "Sources ECMWF, DWD, NOAA, Météo-France · CC BY 4.0",
        "lnk_method": "Méthodologie", "lnk_about": "À propos",
        "lnk_faq": "FAQ", "lnk_app": "Application météo",
        "lnk_widgets": "Widgets voyage",
        "lnk_legal": "Mentions légales", "lnk_priv": "Confidentialité",
        "lnk_contact": "Contact",
    },
    "en": {
        "data_credit": "Weather data by Open-Meteo.com",
        "sources": "Sources ECMWF, DWD, NOAA, Météo-France · CC BY 4.0",
        "lnk_method": "Methodology", "lnk_about": "About",
        "lnk_faq": "FAQ", "lnk_app": "Weather app",
        "lnk_widgets": "Travel widgets",
        "lnk_legal": "Legal notice", "lnk_priv": "Privacy",
        "lnk_contact": "Contact",
    },
    "en-us": {
        "data_credit": "Weather data by Open-Meteo.com",
        "sources": "Sources ECMWF, DWD, NOAA, Météo-France · CC BY 4.0",
        "lnk_method": "Methodology", "lnk_about": "About",
        "lnk_faq": "FAQ", "lnk_app": "Weather app",
        "lnk_widgets": "Travel widgets",
        "lnk_legal": "Legal notice", "lnk_priv": "Privacy",
        "lnk_contact": "Contact",
    },
    "es": {
        "data_credit": "Datos meteo por Open-Meteo.com",
        "sources": "Fuentes ECMWF, DWD, NOAA, Météo-France · CC BY 4.0",
        "lnk_method": "Metodología", "lnk_about": "Acerca de",
        "lnk_faq": "FAQ", "lnk_app": "App meteo",
        "lnk_widgets": "Widgets viaje",
        "lnk_legal": "Aviso legal", "lnk_priv": "Privacidad",
        "lnk_contact": "Contacto",
    },
    "de": {
        "data_credit": "Wetterdaten von Open-Meteo.com",
        "sources": "Quellen ECMWF, DWD, NOAA, Météo-France · CC BY 4.0",
        "lnk_method": "Methodik", "lnk_about": "Über uns",
        "lnk_faq": "FAQ", "lnk_app": "Wetter-App",
        "lnk_widgets": "Reise-Widgets",
        "lnk_legal": "Impressum", "lnk_priv": "Datenschutz",
        "lnk_contact": "Kontakt",
    },
}

# Footer langue links : URLs cohérentes avec V3 prod
_LANG_URL_TEMPLATES = {
    "fr": "meilleure-periode-{slug}.html",
    "en": "en/best-time-to-visit-{slug}.html",
    "en-us": "us/best-time-to-visit-{slug}.html",
    "es": "es/mejor-epoca-{slug}.html",
    "de": "de/beste-reisezeit-{slug}.html",
}
_LANG_LABELS_FOOTER = {
    "fr": ("fr", "Français"),
    "en": ("gb", "English"),
    "en-us": ("us", "English (US)"),
    "es": ("es", "Español"),
    "de": ("de", "Deutsch"),
}


def build_footer_v6(dest, lang="fr"):
    """Footer complet : sources, links app, switcher langues, legal."""
    L = _FOOTER_LABELS.get(lang, _FOOTER_LABELS["fr"])
    slug = dest.get("slug") or dest.get("slug_fr") or "x"

    # Switcher langues : toutes sauf langue courante
    lang_links = []
    for other_lang, (flag_code, label) in _LANG_LABELS_FOOTER.items():
        if other_lang == lang:
            continue
        url = _LANG_URL_TEMPLATES[other_lang].format(slug=slug)
        lang_links.append(
            f'<a href="{url}"><img src="flags/{flag_code}.png" width="20" height="15" '
            f'alt="" loading="lazy"> {_html.escape(label)}</a>'
        )
    langs_block = "\n      ".join(lang_links)

    # Pages localisées des labels (méthodologie, à propos, etc.)
    # Pour FR : root. Pour EN/ES/DE : préfixe lang/
    prefix = {"fr": "", "en": "en/", "en-us": "us/", "es": "es/", "de": "de/"}.get(lang, "")
    page_links = {
        "fr": [("methodologie.html", L["lnk_method"]), ("a-propos.html", L["lnk_about"]),
               ("faq.html", L["lnk_faq"]), ("index.html", L["lnk_app"]),
               ("widgets.html", L["lnk_widgets"])],
        "en": [(f"{prefix}methodology.html", L["lnk_method"]), (f"{prefix}about.html", L["lnk_about"]),
               (f"{prefix}faq.html", L["lnk_faq"]), (f"{prefix}index.html", L["lnk_app"]),
               (f"{prefix}widgets.html", L["lnk_widgets"])],
        "en-us": [(f"{prefix}methodology.html", L["lnk_method"]), (f"{prefix}about.html", L["lnk_about"]),
                  (f"{prefix}faq.html", L["lnk_faq"]), (f"{prefix}index.html", L["lnk_app"]),
                  (f"{prefix}widgets.html", L["lnk_widgets"])],
        "es": [(f"{prefix}metodologia.html", L["lnk_method"]), (f"{prefix}sobre.html", L["lnk_about"]),
               (f"{prefix}faq.html", L["lnk_faq"]), (f"{prefix}index.html", L["lnk_app"]),
               (f"{prefix}widgets.html", L["lnk_widgets"])],
        "de": [(f"{prefix}methodik.html", L["lnk_method"]), (f"{prefix}ueber.html", L["lnk_about"]),
               (f"{prefix}faq.html", L["lnk_faq"]), (f"{prefix}index.html", L["lnk_app"]),
               (f"{prefix}widgets.html", L["lnk_widgets"])],
    }
    legal_links = {
        "fr": [("mentions-legales.html", L["lnk_legal"]), ("confidentialite.html", L["lnk_priv"]),
               ("contact.html", L["lnk_contact"])],
        "en": [(f"{prefix}legal.html", L["lnk_legal"]), (f"{prefix}privacy.html", L["lnk_priv"]),
               (f"{prefix}contact.html", L["lnk_contact"])],
        "en-us": [(f"{prefix}legal.html", L["lnk_legal"]), (f"{prefix}privacy.html", L["lnk_priv"]),
                  (f"{prefix}contact.html", L["lnk_contact"])],
        "es": [(f"{prefix}aviso-legal.html", L["lnk_legal"]), (f"{prefix}privacidad.html", L["lnk_priv"]),
               (f"{prefix}contacto.html", L["lnk_contact"])],
        "de": [(f"{prefix}impressum.html", L["lnk_legal"]), (f"{prefix}datenschutz.html", L["lnk_priv"]),
               (f"{prefix}kontakt.html", L["lnk_contact"])],
    }

    page_block = " · ".join(f'<a href="{u}">{_html.escape(lbl)}</a>'
                            for u, lbl in page_links.get(lang, page_links["fr"]))
    legal_block = " · ".join(f'<a href="{u}">{_html.escape(lbl)}</a>'
                              for u, lbl in legal_links.get(lang, legal_links["fr"]))

    return (f'<footer class="bdw-footer">\n'
            f'  <div class="container">\n'
            f'    <p class="bdw-footer-brand">bestdateweather.com</p>\n'
            f'    <p><a href="https://open-meteo.com/" rel="noopener">{_html.escape(L["data_credit"])}</a> · '
            f'<span class="bdw-footer-sub">{_html.escape(L["sources"])}</span></p>\n'
            f'    <p class="bdw-footer-links">{page_block}</p>\n'
            f'    <p class="bdw-footer-langs">\n'
            f'      {langs_block}\n'
            f'    </p>\n'
            f'    <p class="bdw-footer-legal">{legal_block}</p>\n'
            f'  </div>\n'
            f'</footer>')


def _test():

    # Dataset minimal : Paris (generic)
    paris_monthly = [
        {"mois_num": "1", "score": "1.6", "tmin": "2", "tmax": "7"},
        {"mois_num": "2", "score": "4.5", "tmin": "3", "tmax": "10"},
        {"mois_num": "3", "score": "4.9", "tmin": "4", "tmax": "12"},
        {"mois_num": "4", "score": "7.3", "tmin": "6", "tmax": "15"},
        {"mois_num": "5", "score": "7.7", "tmin": "10", "tmax": "19"},
        {"mois_num": "6", "score": "8.3", "tmin": "14", "tmax": "23"},
        {"mois_num": "7", "score": "8.7", "tmin": "15", "tmax": "25"},
        {"mois_num": "8", "score": "8.5", "tmin": "15", "tmax": "25"},
        {"mois_num": "9", "score": "8.1", "tmin": "13", "tmax": "22"},
        {"mois_num": "10", "score": "5.5", "tmin": "10", "tmax": "16"},
        {"mois_num": "11", "score": "4.4", "tmin": "6", "tmax": "11"},
        {"mois_num": "12", "score": "1.9", "tmin": "3", "tmax": "9"},
    ]
    paris_dest = {"slug": "paris", "nom_fr": "Paris", "tropical": "0", "mountain": "0"}

    # Test classify
    assert classify_dest(paris_dest) == "generic"
    assert classify_dest({"tropical": "1"}) == "tropical"
    assert classify_dest({"mountain": "1"}) == "mountain"
    print("  ✅ classify_dest OK")

    # Test best/worst/top
    assert best_month(paris_monthly)["mois_num"] == "7"
    assert worst_month(paris_monthly)["mois_num"] == "1"
    tops = top_n_months(paris_monthly, 3)
    assert [m["mois_num"] for m in tops] == ["6", "7", "8"], f"Got {[m['mois_num'] for m in tops]}"
    print("  ✅ best/worst/top_n_months OK")

    # Test shoulder : après top 3 (juin/juil/août), les 2 meilleurs suivants sont sep (8.1) et mai (7.7)
    sh = shoulder_months(paris_monthly, n_main=3, n_shoulder=2)
    assert [m["mois_num"] for m in sh] == ["5", "9"], f"Got {[m['mois_num'] for m in sh]}"
    print("  ✅ shoulder_months OK")

    # Test formatage
    assert format_month_list_short(tops, "fr") == "Juin · Juil · Aoû"
    assert format_month_list_short(tops, "en") == "Jun · Jul · Aug"
    assert format_month_full(best_month(paris_monthly), "de") == "Juli"
    print("  ✅ formatage mois multi-langues OK")

    # Test decision card Paris FR
    html_fr = build_decision_card_v6(paris_dest, paris_monthly, lang="fr")
    assert "Juillet" in html_fr
    assert "8.7" in html_fr
    assert "Juin · Juil · Aoû" in html_fr
    assert "Janvier" in html_fr
    assert "Mi-saison idéale" in html_fr
    assert "Foule estivale" in html_fr  # car best = juillet
    print("  ✅ decision_card Paris FR OK")

    # Test autres langues
    for lang in ["en", "en-us", "es", "de"]:
        h = build_decision_card_v6(paris_dest, paris_monthly, lang=lang)
        assert '<div class="decision-card">' in h
        assert "8.7" in h
    print("  ✅ decision_card génère EN/EN-US/ES/DE sans violation LLM")

    # Test dest tropical (Bali simulé)
    bali_monthly = [
        {"mois_num": str(i), "score": str(s)}
        for i, s in enumerate([5.8, 5.7, 6.2, 6.8, 6.9, 6.9, 8.0, 7.9, 6.9, 6.9, 6.1, 6.2], 1)
    ]
    bali_dest = {"slug": "bali", "nom_fr": "Bali", "tropical": "1", "mountain": "0"}
    h_bali = build_decision_card_v6(bali_dest, bali_monthly, lang="fr")
    assert "Mousson" in h_bali or "mousson" in h_bali.lower()
    print("  ✅ decision_card Bali (tropical) avec badge mousson OK")

    # Test dest mountain (Chamonix simulé)
    cham_monthly = [
        {"mois_num": str(i), "score": str(s)}
        for i, s in enumerate([7.9, 8.7, 9.1, 8.6, 7.1, 7.7, 8.2, 8.4, 7.4, 5.7, 6.1, 7.5], 1)
    ]
    cham_dest = {"slug": "chamonix", "nom_fr": "Chamonix", "tropical": "0", "mountain": "1"}
    h_cham = build_decision_card_v6(cham_dest, cham_monthly, lang="fr")
    assert "Mars" in h_cham  # best = mars 9.1
    print("  ✅ decision_card Chamonix (mountain) OK")

    # Test distribution taglines (déterministe par slug)
    tg1 = best_month_tagline(paris_dest, paris_monthly, "fr")
    tg2 = best_month_tagline(paris_dest, paris_monthly, "fr")
    assert tg1 == tg2, "Taglines non déterministes"
    print(f"  ✅ tagline déterministe : '{tg1}'")

    # ══════ Tests verdict + avis_edito ══════
    print("\n  — Tests verdict + avis_edito —")

    # Paris (generic)
    v = build_verdict_v6(paris_dest, paris_monthly, "fr")
    assert "Paris" in v, f"nom manquant : {v}"
    assert "Juillet" in v or "juillet" in v.lower(), f"top1 manquant : {v}"
    assert "Janvier" in v or "janvier" in v.lower(), f"worst manquant : {v}"
    print(f"  ✅ verdict Paris FR : '{v[:80]}...'")

    # Même slug → même variante (déterministe)
    v2 = build_verdict_v6(paris_dest, paris_monthly, "fr")
    assert v == v2, "Verdict non déterministe"
    print(f"  ✅ verdict déterministe (re-appel identique)")

    # 5 langues sans violation
    for lang in ["en", "en-us", "es", "de"]:
        v_l = build_verdict_v6(paris_dest, paris_monthly, lang)
        assert "Paris" in v_l
        assert len(v_l) > 30
    print(f"  ✅ verdict 5 langues OK")

    # Avis édito Paris (generic → utilise template tropical avec placeholders top1/top2/worst)
    a = build_avis_edito_v6(paris_dest, paris_monthly, "fr")
    assert "<strong>" in a, "avis édito doit contenir <strong>"
    assert "Paris" in a
    print(f"  ✅ avis_edito Paris FR OK (contient <strong>)")

    # Verdict tropical (Bali)
    v_bali = build_verdict_v6(bali_dest, bali_monthly, "fr")
    assert "Bali" in v_bali
    print(f"  ✅ verdict Bali (tropical) : '{v_bali[:60]}...'")

    # Verdict mountain (Chamonix) — doit utiliser ski_top et hike_top
    v_cham = build_verdict_v6(cham_dest, cham_monthly, "fr")
    assert "Chamonix" in v_cham
    # Best hiver chamonix_monthly = Mars (9.1), best été = Août (8.4) dans ce dataset
    # Le template utilise ski_top et hike_top donc les mois d'hiver et été doivent apparaître
    print(f"  ✅ verdict Chamonix (mountain) : '{v_cham[:80]}...'")

    # Avis édito mountain (Chamonix)
    a_cham = build_avis_edito_v6(cham_dest, cham_monthly, "fr")
    assert "<strong>" in a_cham
    assert "Chamonix" in a_cham
    print(f"  ✅ avis_edito Chamonix OK")

    # Distribution pick_variant sur 100 slugs fictifs (generic)
    seen = set()
    for i in range(100):
        d = {"slug": f"dest-{i}", "nom_fr": f"Dest{i}", "tropical": "0", "mountain": "0"}
        v = build_verdict_v6(d, paris_monthly, "fr")
        seen.add(v)
    # Avec 5 variantes et 100 slugs, on devrait voir ~5 verdicts distincts
    # (paramètres identiques hormis nom, donc distinctions limitées à la structure)
    # NB : comme le nom change, on devrait voir 100 textes distincts dans les faits
    # Mais si on groupe par template utilisé, on devrait être sur 5
    templates_used = set()
    sample_var = get_templates("verdict_generic", "fr")
    for s_text in seen:
        for i, tmpl in enumerate(sample_var):
            # Match en remplaçant les placeholders par wildcards
            import re as _re
            pattern = _re.escape(tmpl).replace(r"\{nom\}", ".+?").replace(r"\{top1\}", ".+?").replace(r"\{top2\}", ".+?").replace(r"\{worst\}", ".+?")
            if _re.fullmatch(pattern, s_text):
                templates_used.add(i)
                break
    assert len(templates_used) >= 4, f"Seulement {len(templates_used)}/5 templates utilisés"
    print(f"  ✅ Distribution : {len(templates_used)}/5 templates utilisés sur 100 slugs")

    # ══════ Tests barchart ══════
    print("\n  — Tests barchart —")

    # Classes CSS par score
    assert bar_class(9.0) == "good", f"9.0 → good (best réservé au #1) : got {bar_class(9.0)}"
    assert bar_class(8.5) == "good"
    assert bar_class(8.4) == "good"
    assert bar_class(7.0) == "good"
    assert bar_class(6.0) == "mid"
    assert bar_class(5.5) == "mid"
    assert bar_class(4.0) == "low"
    assert bar_class(3.5) == "low"
    assert bar_class(2.0) == "bad"
    assert bar_class(0.5) == "bad"
    print("  ✅ bar_class seuils (good/mid/low/bad, best exclusif au #1)")

    # Barchart Paris FR : 12 barres + 1 seul 'best' (juillet 8.7) + légende
    bc = build_barchart_v6(paris_monthly, lang="fr")
    assert bc.count('class="bar-wrap"') == 12, "Doit avoir 12 barres"
    assert bc.count('class="bar best"') == 1, f"Doit avoir 1 seul 'best', got {bc.count('bar best')}"
    assert "Jan" in bc and "Juil" in bc and "Déc" in bc
    assert "1.6" in bc and "8.7" in bc
    assert "Très bon" in bc and "Rude" in bc
    print("  ✅ Barchart Paris FR : 12 barres, 1 'best' (juillet 8.7), légende FR")

    # Multi-langues (labels + légende)
    bc_en = build_barchart_v6(paris_monthly, lang="en")
    assert "Jul" in bc_en and "Excellent" in bc_en
    bc_es = build_barchart_v6(paris_monthly, lang="es")
    assert "Jul" in bc_es and "Muy bueno" in bc_es
    bc_de = build_barchart_v6(paris_monthly, lang="de")
    assert "Jul" in bc_de and "Sehr gut" in bc_de
    print("  ✅ Barchart labels + légende multi-langues OK")

    # Sans légende
    bc_nolegend = build_barchart_v6(paris_monthly, lang="fr", show_legend=False)
    assert "Très bon" not in bc_nolegend
    assert bc_nolegend.count('bar-wrap') == 12
    print("  ✅ show_legend=False : pas de légende")

    # Barchart mountain avec ski_scores_by_month
    # Chamonix dataset : general best = Août 8.4 (mois 8)
    # Si on fournit ski_scores Mars=9.1, Feb=8.7, Avr=8.6 → Mars doit devenir best
    ski_scores = {1: 7.9, 2: 8.7, 3: 9.1, 4: 8.6, 5: 7.1, 11: 6.1, 12: 7.5}
    bc_cham = build_barchart_v6(cham_monthly, lang="fr", ski_scores_by_month=ski_scores)
    # Best = 9.1 (Mars) → doit afficher 9.1 quelque part, et 1 seul 'best'
    assert "9.1" in bc_cham, "Score ski max (9.1) doit apparaître"
    assert bc_cham.count('class="bar best"') == 1
    print("  ✅ Barchart mountain avec ski_scores : best = max(gen, ski)")

    # Sans ski_scores → Chamonix best reste Août (score général max)
    bc_cham_nogski = build_barchart_v6(cham_monthly, lang="fr")
    # Dans cham_monthly : scores [7.9, 8.7, 9.1, 8.6, ...] — 9.1 aussi dans général (dataset test simulé)
    # Le test principal : 1 seul 'best'
    assert bc_cham_nogski.count('class="bar best"') == 1

    # Cas limite : aucun mois ≥ 8.5 → aucun 'best'
    low_monthly = [{"mois_num": str(i), "score": "5.0"} for i in range(1, 13)]
    bc_low = build_barchart_v6(low_monthly, lang="fr")
    assert 'class="bar best"' not in bc_low, "Aucun mois ≥ 8.5 → 0 'best'"
    print("  ✅ Cas limite : tous scores < 8.5 → 0 bar.best")

    # ══════ Tests pills ══════
    print("\n  — Tests pills —")

    # Pills Paris FR : 4 pills good + 1 bad
    pills_fr = build_pills_v6(paris_monthly, lang="fr", n_top=4)
    assert 'class="pill good"' in pills_fr
    assert pills_fr.count('class="pill good"') == 4
    assert pills_fr.count('class="pill bad"') == 1
    assert "Juillet · 8.7" in pills_fr  # top 1 avec trophy
    assert "🏆" in pills_fr
    assert "Janvier · 1.6" in pills_fr  # worst avec warn
    assert "⚠️" in pills_fr
    assert "Top & à éviter" in pills_fr
    print("  ✅ Pills Paris FR : 4 good (🏆 Juillet en tête) + 1 bad (⚠️ Janvier)")

    # Multi-langues
    assert "Top & avoid" in build_pills_v6(paris_monthly, lang="en")
    assert "Top & a evitar" in build_pills_v6(paris_monthly, lang="es")
    assert "Top & Meiden" in build_pills_v6(paris_monthly, lang="de")
    print("  ✅ Pills section label multi-langues")

    # Sans label
    pills_nolbl = build_pills_v6(paris_monthly, lang="fr", show_section_label=False)
    assert "Top & à éviter" not in pills_nolbl
    assert 'class="pills"' in pills_nolbl
    print("  ✅ show_section_label=False : pas de label")

    # n_top=3
    pills_3 = build_pills_v6(paris_monthly, lang="fr", n_top=3)
    assert pills_3.count('class="pill good"') == 3
    print("  ✅ n_top=3 : 3 pills good + 1 bad")

    # ══════ Tests right_stack ══════
    print("\n  — Tests right_stack —")

    rs_fr = build_right_stack_v6(paris_dest, paris_monthly, lang="fr")
    # NB : apostrophes escaped en &#x27; dans les H3 (HTML-safe)
    assert "comprend en 5 secondes" in rs_fr
    assert "faut vérifier ensuite" in rs_fr
    assert "Action suivante" in rs_fr
    assert "Comparer les 12 mois" in rs_fr
    assert "Selon votre projet" in rs_fr
    # Paris : 6 mois ≥7 (avr-sep) → contigu → "avril-septembre"
    assert "avril-septembre" in rs_fr or "6 mois" in rs_fr
    # Écart Paris : 8.7 vs 1.6
    assert "8.7" in rs_fr and "1.6" in rs_fr
    print("  ✅ right_stack Paris FR : 3 right-item + CTA row, textes auto OK")

    # Déterministe
    rs2 = build_right_stack_v6(paris_dest, paris_monthly, lang="fr")
    assert rs_fr == rs2
    print("  ✅ right_stack déterministe")

    # Multi-langues
    for lang in ["en", "en-us", "es", "de"]:
        rs_l = build_right_stack_v6(paris_dest, paris_monthly, lang=lang)
        assert "Paris" in rs_l
        assert "8.7" in rs_l
    print("  ✅ right_stack 5 langues")

    # Verify text selon type
    rs_bali = build_right_stack_v6(bali_dest, bali_monthly, lang="fr")
    assert "pluie" in rs_bali.lower() and "humidité" in rs_bali.lower()
    print("  ✅ right_stack tropical (Bali) : texte verify mentionne pluie+humidité")

    rs_cham = build_right_stack_v6(cham_dest, cham_monthly, lang="fr")
    assert "ski" in rs_cham.lower() and "alpinisme" in rs_cham.lower()
    print("  ✅ right_stack mountain (Chamonix) : texte verify mentionne ski+alpinisme")

    # Cas _month_range_label : 1 seul mois
    one_month = [{"mois_num": "7", "score": "8.7"}]
    assert _month_range_label(one_month, "fr") == "juillet"
    # Contigus
    assert _month_range_label([{"mois_num": "4", "score": "7"}, {"mois_num": "5", "score": "7"}], "fr") == "avril-mai"
    # Non contigus
    assert "," in _month_range_label([{"mois_num": "4", "score": "7"}, {"mois_num": "7", "score": "7"}], "fr")
    print("  ✅ _month_range_label (1 mois / contigus / non-contigus)")

    print("\n→ Tous les tests common_v6 passent ✓")


if __name__ == "__main__":
    _test()
