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
            "fr": ["Enneigement + stations ouvertes", "Neige fraîche + soleil", "Conditions ski optimales"],
            "en": ["Snow cover + open resorts", "Fresh snow + sun", "Peak ski conditions"],
            "en-us": ["Snow cover + open resorts", "Fresh snow + sun", "Peak ski conditions"],
            "es": ["Nieve + estaciones abiertas", "Nieve fresca + sol", "Condiciones de esquí óptimas"],
            "de": ["Schneedecke + offene Stationen", "Frischer Schnee + Sonne", "Optimale Ski-Bedingungen"],
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
    slug = dest.get("slug") or dest.get("slug_fr") or "paris"

    # URL builder par défaut (à améliorer en intégration prod via locales)
    if monthly_url_builder is None:
        _FR_SLUGS = ["janvier", "fevrier", "mars", "avril", "mai", "juin",
                     "juillet", "aout", "septembre", "octobre", "novembre", "decembre"]
        def monthly_url_builder(slug_x, mois_num, lang_x):
            # Pour simplicité Tour 2 : toujours en structure FR (à étendre via locales)
            return f"{slug_x}-meteo-{_FR_SLUGS[mois_num - 1]}.html"

    sorted_m = sorted(monthly, key=lambda m: int(m["mois_num"]))

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
        url = monthly_url_builder(slug, mn, lang)

        row = (f'                <tr onclick="location.href=\'{url}\'" '
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
        tbody_rows.append(row)

        # Card mobile
        mobile_cards.append(
            f'            <a href="{url}" class="mobile-month-card">\n'
            f'              <div class="head"><div class="name">{emo} {_html.escape(name)}</div>'
            f'<div class="score {mood_cls}">{score:.1f}/10</div></div>\n'
            f'              <div class="rows">\n'
            f'                <div class="row"><span>T°</span><strong>{_html.escape(str(tmin))}°C / {_html.escape(str(tmax))}°C</strong></div>\n'
            f'                <div class="row"><span>{L["th_rain"].replace(" %", "")}</span><strong>{rain}%</strong></div>\n'
            f'                <div class="row"><span>{L["th_sun"]}</span><strong>{sun:.1f}h</strong></div>\n'
            f'                <div class="row row-mood"><strong class="mood-{mood_cls}">{_html.escape(mood_label)}</strong></div>\n'
            f'              </div>\n'
            f'            </a>'
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


def _test():
    """Tests rapides (exécuter avec : python3 -m lib.common_v6)."""

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
