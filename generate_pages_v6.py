"""
V6 — Générateur de pages autonome utilisant les briques de lib/common_v6.py

Ce module produit une page HTML complète pour une destination donnée, en
assemblant les sections via les build_*_v6() fonctions.

Stratégie : indépendant de generate_pages.py (V3) pour permettre la
coexistence et les tests en parallèle sans risque sur la prod.

Usage :
    from generate_pages_v6 import render_annual_v6

    html = render_annual_v6(dest, monthly_data, lang='fr',
                            ski_scores_by_month=None)
    # html = page complète (DOCTYPE → </html>)

Tests via CLI :
    python3 generate_pages_v6.py --slug paris --lang fr \
        --output /tmp/paris-v6.html

STATUS : en construction progressive (build progressive par sections).
Les sections intégrées sont listées dans docstring de render_annual_v6().
"""

import argparse
import csv
import html as _html
import os
import sys

# Path pour import lib depuis racine repo
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lib.common_v6 import (
    build_decision_card_v6,
    build_verdict_v6,
    build_avis_edito_v6,
    build_barchart_v6,
    build_pills_v6,
    build_right_stack_v6,
    build_comprendre_section_v6,
    build_seasons_section_v6,
    build_profiles_section_v6,
    classify_dest,
    best_month,
    worst_month,
    format_month_full,
    MONTH_NAMES,
    UI_LABELS,
)


# ══════════════════════════════════════════════════════════════════
# i18n : labels section headers
# ══════════════════════════════════════════════════════════════════

_SECTION_LABELS = {
    "fr": {
        "decider_kicker": "Décider",
        "decider_title": "Quand partir à {nom} ?",
        "decider_lead": "La décision se joue sur plusieurs critères. Score climatique, foule touristique et activités possibles.",
        "brand_suffix": "· BestDateWeather",
        "hero_ctx": "climat tempéré",
    },
    "en": {
        "decider_kicker": "Decide",
        "decider_title": "When to visit {nom}?",
        "decider_lead": "The decision comes down to several criteria. Weather score, crowds, and available activities.",
        "brand_suffix": "· BestDateWeather",
        "hero_ctx": "temperate climate",
    },
    "en-us": {
        "decider_kicker": "Decide",
        "decider_title": "When to visit {nom}?",
        "decider_lead": "The decision comes down to several criteria. Weather score, crowds, and available activities.",
        "brand_suffix": "· BestDateWeather",
        "hero_ctx": "temperate climate",
    },
    "es": {
        "decider_kicker": "Decidir",
        "decider_title": "¿Cuándo ir a {nom}?",
        "decider_lead": "La decisión depende de varios criterios. Puntuación climática, multitudes y actividades posibles.",
        "brand_suffix": "· BestDateWeather",
        "hero_ctx": "clima templado",
    },
    "de": {
        "decider_kicker": "Entscheiden",
        "decider_title": "Wann nach {nom} reisen?",
        "decider_lead": "Die Entscheidung hängt von mehreren Kriterien ab. Klimapunktzahl, Menschenmassen und mögliche Aktivitäten.",
        "brand_suffix": "· BestDateWeather",
        "hero_ctx": "gemäßigtes Klima",
    },
}


# ══════════════════════════════════════════════════════════════════
# CSS embarqué (minimal, copié depuis proto V5)
# ══════════════════════════════════════════════════════════════════

# Pour un vrai intégration prod, ces styles seraient dans un fichier .css
# externe versionné. Pour ce MVP V6, on les embarque pour portabilité
# (chaque page est self-contained pour tests visuels).

_CSS_BASE = """
:root{
  --ink:#0d1117;--muted:#6b7280;--gold:#e8940a;--card:#fff;--bg:#fffdfa;
  --border:#e8e0d0;--shadow:0 1px 3px rgba(0,0,0,.05);
  --amber:#b8860b;--amber-soft:#fef3d0;--amber-border:#f2e6a8;
  --green:#1a7a4a;--green-soft:#e8f8f0;--green-border:#bfe7cd;
}
*,*::before,*::after{box-sizing:border-box}
body{margin:0;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;
  color:var(--ink);background:var(--bg);line-height:1.55}
.container{max-width:1200px;margin:0 auto;padding:0 20px}
main{padding:20px 0 60px}
header{background:linear-gradient(180deg,#fff 0%,#fffbf2 100%);
  padding:30px 0 0;border-bottom:1px solid var(--border)}

.hero-grid{display:grid;grid-template-columns:1.5fr 1fr;gap:40px;
  align-items:start;padding:20px 0 40px}
@media (max-width:768px){.hero-grid{grid-template-columns:1fr;gap:24px}}
.hero-main h1{font-family:'Playfair Display',Georgia,serif;
  font-size:clamp(28px,5vw,44px);margin:0 0 16px;line-height:1.1}
.hero-eyebrow{font-size:12px;font-weight:700;color:var(--gold);
  text-transform:uppercase;letter-spacing:.08em;margin-bottom:10px}
.hero-lead{font-size:17px;color:var(--muted);margin:0 0 20px}
.hero-meta{display:flex;gap:16px;flex-wrap:wrap;font-size:14px;color:var(--muted)}
.hero-meta span{display:inline-flex;gap:6px;align-items:center}

.decision-card{background:var(--card);border:1px solid var(--border);
  border-radius:20px;padding:22px;box-shadow:var(--shadow)}
.small-label{font-size:11px;font-weight:700;color:var(--gold);
  text-transform:uppercase;letter-spacing:.07em;margin-bottom:14px}
.decision-top{display:flex;justify-content:space-between;align-items:flex-start;gap:12px}
.decision-top .month{font-family:'Playfair Display',Georgia,serif;
  font-size:32px;font-weight:700;line-height:1}
.decision-top .sub{color:var(--muted);font-size:13px;margin-top:4px}
.decision-top .score{font-family:'Playfair Display',Georgia,serif;
  font-size:44px;font-weight:700;color:var(--ink)}
.decision-top .score small{font-size:14px;color:var(--muted);font-weight:500}
.mini-grid{display:grid;grid-template-columns:1fr;gap:10px;margin-top:16px}
.mini-card{background:#faf8f3;border:1px solid var(--border);
  border-radius:12px;padding:10px 14px}
.mini-card .v{font-weight:700;font-size:15px}
.mini-card .l{font-size:12px;color:var(--muted);margin-top:2px}

/* Section Décider */
.section-head{margin-bottom:24px}
.section-kicker{font-size:12px;font-weight:700;color:var(--gold);
  text-transform:uppercase;letter-spacing:.08em;margin-bottom:8px}
.section-head h2{font-family:'Playfair Display',Georgia,serif;
  font-size:clamp(26px,4vw,36px);margin:0 0 12px;line-height:1.15}
.section-head .lead{color:var(--muted);font-size:16px;margin:0;max-width:700px}

.decider-grid{display:grid;grid-template-columns:1.3fr 1fr;gap:28px;margin-top:32px}
@media (max-width:900px){.decider-grid{grid-template-columns:1fr}}
.verdict-box{background:var(--card);border:1px solid var(--border);
  border-radius:20px;padding:26px;box-shadow:var(--shadow);display:flex;
  flex-direction:column;gap:24px}
.verdict-box .verdict-txt{font-size:17px;line-height:1.55;margin:0}
.verdict-box .avis-edito{font-size:15px;line-height:1.6;color:#2c323a;
  background:#faf8f3;border-left:3px solid var(--gold);padding:14px 18px;
  border-radius:0 10px 10px 0;margin:0}

/* Pills */
.pills{display:flex;flex-wrap:wrap;gap:8px;margin-top:8px}
.pill{display:inline-flex;align-items:center;padding:6px 12px;
  border-radius:999px;font-size:13px;font-weight:700;
  border:1px solid transparent}
.pill.good{background:#e8f8f0;color:#1a7a4a;border-color:#bfe7cd}
.pill.bad{background:#fdecec;color:#b91c1c;border-color:#f4caca}

/* Barchart */
.bars{display:grid;grid-template-columns:repeat(12,minmax(0,1fr));
  gap:8px;margin-top:10px;min-width:0;align-items:stretch}
.bar-wrap{display:flex;flex-direction:column;align-items:center;gap:6px;min-width:0}
.bar-slot{width:100%;height:130px;display:flex;align-items:flex-end;justify-content:center}
.bar{width:100%;min-height:18px;border-radius:8px 8px 4px 4px;
  transition:transform .2s ease}
.bar:hover{transform:scaleY(1.03)}
.bar.best{background:linear-gradient(180deg,#2ea86a 0%,#1a7a4a 100%);
  outline:2px solid var(--gold);outline-offset:1px;
  box-shadow:0 0 0 4px rgba(232,148,10,.15)}
.bar.good{background:linear-gradient(180deg,#46c878 0%,#25a75d 100%)}
.bar.mid{background:linear-gradient(180deg,#ecc568 0%,#b8860b 100%)}
.bar.low{background:linear-gradient(180deg,#e47272 0%,#b91c1c 100%)}
.bar.bad{background:linear-gradient(180deg,#b91c1c 0%,#8b1616 100%)}
.bar-score{font-size:.72rem;color:var(--ink);font-weight:800}
.bar-label{font-size:.72rem;color:var(--muted);font-weight:600}
@media (max-width:640px){.bars{gap:5px}.bar-slot{height:110px}
  .bar-label,.bar-score{font-size:.6rem}.bar-score{font-size:.62rem}}

/* Right-stack */
.right-stack{background:var(--card);border:1px solid var(--border);
  border-radius:20px;padding:26px;box-shadow:var(--shadow);
  display:flex;flex-direction:column;gap:20px}
.right-item h3{font-family:'Playfair Display',Georgia,serif;font-size:18px;
  margin:0 0 6px;font-weight:700}
.right-item p{margin:0;color:var(--muted);font-size:14.5px;line-height:1.55}
.cta-row{display:flex;gap:10px;flex-wrap:wrap;margin-top:4px}
.btn{display:inline-block;padding:10px 18px;border-radius:999px;
  font-size:14px;font-weight:700;text-decoration:none;
  border:1px solid var(--border);color:var(--ink);background:#fff}
.btn.primary{background:var(--gold);color:#fff;border-color:var(--gold)}
.btn:hover{transform:translateY(-1px)}

/* Section Comprendre : tableau + signaux */
section{padding:40px 0}
.spotlight-grid{display:grid;grid-template-columns:minmax(0,1.15fr) minmax(0,.85fr);
  gap:24px;margin-top:24px}
@media (max-width:900px){.spotlight-grid{grid-template-columns:1fr}}
.card{background:var(--card);border:1px solid var(--border);border-radius:20px;
  box-shadow:var(--shadow)}
.card.pad{padding:22px}
.table-wrap{overflow:visible;margin:0 -4px}
table{width:100%;border-collapse:collapse;font-size:13px;table-layout:auto}
thead th{text-align:left;padding:10px 8px;color:var(--muted);font-weight:700;
  border-bottom:1px solid var(--border);font-size:11.5px;text-transform:uppercase;
  letter-spacing:.03em}
tbody td{padding:10px 8px;border-bottom:1px solid #f2eadb;font-weight:600}
tbody tr:hover{background:#fffbf2}
.month-cell{font-weight:700}
.mood{display:inline-block;padding:3px 9px;border-radius:999px;font-size:11.5px;
  font-weight:700}
.mood.good{background:#e8f8f0;color:#1a7a4a;border:1px solid #bfe7cd}
.mood.mid{background:#fef3d0;color:#b8860b;border:1px solid #f2e6a8}
.mood.bad{background:#fdecec;color:#b91c1c;border:1px solid #f4caca}

.mobile-month-cards{display:none}
@media (max-width:640px){
  .table-wrap{display:none}
  .mobile-month-cards{display:flex;flex-direction:column;gap:8px}
  .mobile-month-card{background:#faf8f3;border:1px solid var(--border);
    border-radius:12px;padding:12px;text-decoration:none;color:var(--ink);
    display:block}
  .mobile-month-card .head{display:flex;justify-content:space-between;
    align-items:center;margin-bottom:6px}
  .mobile-month-card .head .name{font-weight:700;font-size:14px}
  .mobile-month-card .head .score{padding:2px 8px;border-radius:999px;
    font-size:12px;font-weight:700}
  .mobile-month-card .head .score.good{background:#e8f8f0;color:#1a7a4a}
  .mobile-month-card .head .score.mid{background:#fef3d0;color:#b8860b}
  .mobile-month-card .head .score.bad{background:#fdecec;color:#b91c1c}
  .mobile-month-card .rows{display:grid;grid-template-columns:1fr 1fr;
    gap:4px 14px;font-size:12px}
  .mobile-month-card .row span{color:var(--muted)}
  .mobile-month-card .row-mood{grid-column:span 2;margin-top:4px}
  .mood-good{color:#1a7a4a;font-weight:700}
  .mood-mid{color:#b8860b;font-weight:700}
  .mood-bad{color:#b91c1c;font-weight:700}
}

/* Signaux */
.signal-card{display:flex;flex-direction:column;gap:14px}
.signal-list{display:flex;flex-direction:column;gap:0}
.signal-item{display:flex;justify-content:space-between;align-items:center;
  padding:10px 0;border-bottom:1px solid #f2eadb;font-size:14px}
.signal-item:last-child{border-bottom:none}
.signal-item .l{color:var(--muted);font-weight:500}
.signal-item .r{font-weight:700}

/* Grids génériques pour cards saisons et profils */
.grid-2{display:grid;grid-template-columns:repeat(2,1fr);gap:20px}
.grid-3{display:grid;grid-template-columns:repeat(3,1fr);gap:20px}
.grid-4{display:grid;grid-template-columns:repeat(4,1fr);gap:18px}
@media (max-width:900px){.grid-4{grid-template-columns:repeat(2,1fr)}}
@media (max-width:640px){
  .grid-2,.grid-3,.grid-4{grid-template-columns:1fr;gap:14px}
}
.box{background:var(--card);border:1px solid var(--border);border-radius:16px;
  padding:20px;box-shadow:var(--shadow)}
.box-head{display:flex;justify-content:space-between;align-items:center;
  gap:10px;margin-bottom:10px;flex-wrap:wrap}
.box-head strong{font-size:15px}
.box p{margin:0;color:var(--muted);font-size:14px;line-height:1.55}
.box p strong{color:var(--ink)}
.badge{display:inline-block;padding:4px 10px;border-radius:999px;
  background:#faf8f3;border:1px solid var(--border);font-size:11.5px;
  font-weight:700;color:var(--ink);white-space:nowrap}
"""


# ══════════════════════════════════════════════════════════════════
# Helpers rendu
# ══════════════════════════════════════════════════════════════════

def _render_head(dest, lang, page_title):
    """Rend le <head> HTML avec meta + CSS embarqué."""
    brand = _SECTION_LABELS.get(lang, _SECTION_LABELS["fr"])["brand_suffix"]
    full_title = f"{page_title} {brand}"
    return f'''<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1.0"/>
<meta name="robots" content="index,follow"/>
<title>{_html.escape(full_title)}</title>
<link rel="preconnect" href="https://fonts.googleapis.com"/>
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin/>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&display=swap"/>
<style>{_CSS_BASE}</style>
</head>'''


def _render_hero(dest, monthly, lang):
    """
    Rend le <header> + hero-grid avec hero-main (eyebrow/h1/lead/meta)
    et hero-side (decision-card via build_decision_card_v6).
    """
    L = _SECTION_LABELS.get(lang, _SECTION_LABELS["fr"])
    UI = UI_LABELS.get(lang, UI_LABELS["fr"])
    nom_key = f"nom_{lang.replace('-', '_')}"
    nom = dest.get(nom_key) or dest.get("nom_fr") or dest.get("slug", "?")
    flag = dest.get("flag", "")

    # Hero title par langue (simplifié — en prod on utilisera locales/*.json)
    hero_titles = {
        "fr": f"Quand partir à {nom} ?",
        "en": f"When to visit {nom}?",
        "en-us": f"When to visit {nom}?",
        "es": f"¿Cuándo ir a {nom}?",
        "de": f"Wann nach {nom} reisen?",
    }
    hero_eyebrows = {
        "fr": "Meilleure période",
        "en": "Best time",
        "en-us": "Best time",
        "es": "Mejor época",
        "de": "Beste Reisezeit",
    }
    # Lead court : delta best vs worst
    best = best_month(monthly)
    worst = worst_month(monthly)
    hero_leads = {
        "fr": f"Le meilleur mois est <strong>{format_month_full(best, lang)}</strong> avec un score de {float(best['score']):.1f}/10. Le plus rude : {format_month_full(worst, lang)} ({float(worst['score']):.1f}/10).",
        "en": f"Best month is <strong>{format_month_full(best, lang)}</strong> with a {float(best['score']):.1f}/10 score. Toughest: {format_month_full(worst, lang)} ({float(worst['score']):.1f}/10).",
        "en-us": f"Best month is <strong>{format_month_full(best, lang)}</strong> with a {float(best['score']):.1f}/10 score. Toughest: {format_month_full(worst, lang)} ({float(worst['score']):.1f}/10).",
        "es": f"El mejor mes es <strong>{format_month_full(best, lang)}</strong> con una puntuación de {float(best['score']):.1f}/10. El más duro: {format_month_full(worst, lang)} ({float(worst['score']):.1f}/10).",
        "de": f"Der beste Monat ist <strong>{format_month_full(best, lang)}</strong> mit {float(best['score']):.1f}/10. Härtester: {format_month_full(worst, lang)} ({float(worst['score']):.1f}/10).",
    }

    # Labels hero-meta par langue
    meta_labels = {
        "fr": {"update": "📅 Mise à jour", "era5": "🛰️ ERA5 · 10 ans",
               "loc": "📍 {lat}°N · {lon}°E"},
        "en": {"update": "📅 Updated", "era5": "🛰️ ERA5 · 10 years",
               "loc": "📍 {lat}°N · {lon}°E"},
        "en-us": {"update": "📅 Updated", "era5": "🛰️ ERA5 · 10 years",
                  "loc": "📍 {lat}°N · {lon}°E"},
        "es": {"update": "📅 Actualizado", "era5": "🛰️ ERA5 · 10 años",
               "loc": "📍 {lat}°N · {lon}°E"},
        "de": {"update": "📅 Aktualisiert", "era5": "🛰️ ERA5 · 10 Jahre",
               "loc": "📍 {lat}°N · {lon}°E"},
    }
    ML = meta_labels.get(lang, meta_labels["fr"])

    # Récupérer lat/lon (fallback 0 si absent)
    try:
        lat_s = f"{float(dest.get('lat', 0)):.2f}"
        lon_s = f"{float(dest.get('lon', 0)):.2f}"
    except (ValueError, TypeError):
        lat_s, lon_s = "0", "0"

    decision_card_html = build_decision_card_v6(dest, monthly, lang=lang)

    hero = f'''<header>
  <div class="container">
    <div class="hero-grid">
      <div class="hero-main">
        <div class="hero-eyebrow">{_html.escape(hero_eyebrows[lang])}</div>
        <h1>{_html.escape(hero_titles[lang])}</h1>
        <p class="hero-lead">{hero_leads[lang]}</p>
        <div class="hero-meta">
          <span>{ML["update"]} Avril 2026</span>
          <span>{ML["era5"]}</span>
          <span>{ML["loc"].format(lat=lat_s, lon=lon_s)}</span>
        </div>
      </div>
      <div class="hero-side">
        {decision_card_html}
      </div>
    </div>
  </div>
</header>'''
    return hero


def _render_decider_section(dest, monthly, lang, ski_scores_by_month=None):
    """
    Rend la section 'Décider' complète :
    - section-head (kicker, h2, lead)
    - decider-grid : verdict-box (verdict + avis_edito + pills + barchart) + right-stack
    """
    L = _SECTION_LABELS.get(lang, _SECTION_LABELS["fr"])
    nom_key = f"nom_{lang.replace('-', '_')}"
    nom = dest.get(nom_key) or dest.get("nom_fr") or dest.get("slug", "?")

    verdict_txt = build_verdict_v6(dest, monthly, lang=lang)
    avis_edito = build_avis_edito_v6(dest, monthly, lang=lang)
    pills_html = build_pills_v6(monthly, lang=lang, n_top=4)
    barchart_html = build_barchart_v6(monthly, lang=lang,
                                       ski_scores_by_month=ski_scores_by_month)
    right_stack_html = build_right_stack_v6(dest, monthly, lang=lang)

    title = L["decider_title"].format(nom=_html.escape(nom))

    return f'''<section>
    <div class="container">
      <div class="section-head">
        <div class="section-kicker">{_html.escape(L["decider_kicker"])}</div>
        <h2>{title}</h2>
        <p class="lead">{_html.escape(L["decider_lead"])}</p>
      </div>
      <div class="decider-grid">
        <div class="verdict-box">
          <p class="verdict-txt">{verdict_txt}</p>
          <p class="avis-edito">{avis_edito}</p>
          {pills_html}
          <div>
            {barchart_html}
          </div>
        </div>
        {right_stack_html}
      </div>
    </div>
  </section>'''


def _render_footer(dest, lang):
    """Rend un footer minimal (V6 Tour 1)."""
    brand_lines = {
        "fr": ("Données météo : Open-Meteo · ERA5",
               "Sources ECMWF, DWD, NOAA, Météo-France"),
        "en": ("Weather data: Open-Meteo · ERA5",
               "Sources ECMWF, DWD, NOAA, Météo-France"),
        "en-us": ("Weather data: Open-Meteo · ERA5",
                  "Sources ECMWF, DWD, NOAA, Météo-France"),
        "es": ("Datos meteorológicos: Open-Meteo · ERA5",
               "Fuentes ECMWF, DWD, NOAA, Météo-France"),
        "de": ("Wetterdaten: Open-Meteo · ERA5",
               "Quellen ECMWF, DWD, NOAA, Météo-France"),
    }
    l1, l2 = brand_lines.get(lang, brand_lines["fr"])
    return f'''<footer style="border-top:1px solid var(--border);padding:40px 0;text-align:center;color:var(--muted);font-size:13px">
  <div class="container">
    <p style="margin:0 0 6px"><strong>bestdateweather.com</strong></p>
    <p style="margin:0 0 4px">{_html.escape(l1)}</p>
    <p style="margin:0;font-size:11px;opacity:.7">{_html.escape(l2)}</p>
  </div>
</footer>'''


# ══════════════════════════════════════════════════════════════════
# Fonction principale
# ══════════════════════════════════════════════════════════════════

def render_annual_v6(dest, monthly, lang="fr", ski_scores_by_month=None):
    """
    Rend une page HTML complète (DOCTYPE → </html>) pour une destination.

    SECTIONS INTÉGRÉES (Tour 1) :
    - <head> avec CSS embarqué + Playfair Display
    - <header> hero (eyebrow/h1/lead/meta + decision-card)
    - <section> Décider (verdict + avis_edito + pills + barchart + right-stack)
    - <footer> minimal

    SECTIONS NON ENCORE INTÉGRÉES (prochains tours) :
    - Comprendre (tableau 12 mois + signaux)
    - À quoi s'attendre (4 cards saisons)
    - Par projet (4 cards profils)
    - Planifier (affiliés + widget GYG)
    - Infos pratiques (altitude, monnaie, etc.)
    - Explorer (similaires + proches + classements)
    - Localisation (maps Leaflet)
    - FAQ + JSON-LD

    Args:
        dest: dict destination (slug, nom_*, tropical, mountain, flag, lat, lon)
        monthly: list[dict] 12 mois (mois_num, score, tmin, tmax, rain_pct, sun_h, ...)
        lang: code langue ('fr', 'en', 'en-us', 'es', 'de')
        ski_scores_by_month: dict optionnel {mois_num: score_ski} pour mountain

    Returns:
        str : page HTML complète
    """
    if len(monthly) != 12:
        raise ValueError(f"monthly doit contenir 12 entrées, reçu {len(monthly)}")
    if lang not in _SECTION_LABELS:
        raise ValueError(f"Langue non supportée : {lang}. Disponibles : {list(_SECTION_LABELS.keys())}")

    nom_key = f"nom_{lang.replace('-', '_')}"
    nom = dest.get(nom_key) or dest.get("nom_fr") or dest.get("slug", "?")

    page_titles = {
        "fr": f"Quand partir à {nom} — météo & meilleure période",
        "en": f"When to visit {nom} — weather & best time",
        "en-us": f"When to visit {nom} — weather & best time",
        "es": f"Cuándo ir a {nom} — tiempo y mejor época",
        "de": f"Wann nach {nom} reisen — Wetter & beste Reisezeit",
    }
    page_title = page_titles[lang]

    head = _render_head(dest, lang, page_title)
    hero = _render_hero(dest, monthly, lang)
    decider = _render_decider_section(dest, monthly, lang, ski_scores_by_month)
    comprendre = build_comprendre_section_v6(dest, monthly, lang=lang)
    seasons = build_seasons_section_v6(dest, monthly, lang=lang)
    profiles = build_profiles_section_v6(dest, monthly, lang=lang)
    footer = _render_footer(dest, lang)

    html = f'''{head}
<body>
{hero}
<main>
  {decider}
  {comprendre}
  {seasons}
  {profiles}
</main>
{footer}
</body>
</html>'''

    return html


# ══════════════════════════════════════════════════════════════════
# CLI pour tests
# ══════════════════════════════════════════════════════════════════

def _load_dest_and_monthly(slug, data_dir="data"):
    """Charge une destination + ses données mensuelles depuis CSV."""
    monthly = sorted(
        [r for r in csv.DictReader(open(os.path.join(data_dir, "climate.csv")))
         if r["slug"] == slug],
        key=lambda m: int(m["mois_num"])
    )
    if len(monthly) != 12:
        raise ValueError(f"Destination '{slug}' : {len(monthly)} mois trouvés (12 attendus)")

    dests = list(csv.DictReader(open(os.path.join(data_dir, "destinations.csv"))))
    dest = next((d for d in dests if d["slug_fr"] == slug), None)
    if not dest:
        raise ValueError(f"Destination '{slug}' non trouvée dans destinations.csv")
    dest["slug"] = slug  # Normaliser pour les helpers

    return dest, monthly


def main():
    parser = argparse.ArgumentParser(
        description="Générer une fiche V6 pour une destination."
    )
    parser.add_argument("--slug", required=True, help="Slug FR (ex : paris, bali, chamonix)")
    parser.add_argument("--lang", default="fr",
                        choices=["fr", "en", "en-us", "es", "de"],
                        help="Langue de sortie")
    parser.add_argument("--output", required=True, help="Fichier HTML de sortie")
    parser.add_argument("--data-dir", default="data", help="Répertoire CSV")
    args = parser.parse_args()

    dest, monthly = _load_dest_and_monthly(args.slug, args.data_dir)
    html = render_annual_v6(dest, monthly, lang=args.lang)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"✅ {args.output}  ({len(html):,} chars · {dest['nom_fr']} · {args.lang})")


if __name__ == "__main__":
    main()
