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
        "mois_a_eviter": "Mois à éviter",
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
        "mois_a_eviter": "Month to avoid",
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
        "mois_a_eviter": "Month to avoid",
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
        "mois_a_eviter": "Mes a evitar",
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
        "mois_a_eviter": "Monat zu meiden",
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

    print("\n→ Tous les tests common_v6 passent ✓")


if __name__ == "__main__":
    _test()
