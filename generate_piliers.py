#!/usr/bin/env python3
"""
Generate 24 seasonal pillar pages (12 FR + 12 EN):
  FR: ou-partir-en-janvier.html … ou-partir-en-decembre.html
  EN: en/where-to-go-in-january.html … en/where-to-go-in-december.html

Each page ranks top 25 destinations for that month by weather score.
Usage: python3 generate_piliers.py
"""

import csv, html as html_mod, json, sys, os
from pathlib import Path
from lib.common import footer_ranking_html, c_to_f
from datetime import date
from scoring import compute_ski_score

sys.path.insert(0, str(Path(__file__).parent))
from lib.page_config import load_locale
from generate_classements import COUNTRY_SLUGS, NON_EUROPE_SLUGS, dedup_country

ROOT = Path(__file__).parent
TODAY = date.today().isoformat()
YEAR = date.today().year

TOP_N = 25

# Derived from locale files present in locales/ — add a new locale file to expand
PILIER_LANGS = sorted(
    p.stem for p in (Path(__file__).parent / 'locales').glob('*.json')
)

# ── Data Loading ──────────────────────────────────────────────────────────────

def load_destinations():
    dests = {}
    with open(ROOT / 'data/destinations.csv', encoding='utf-8-sig') as f:
        for r in csv.DictReader(f):
            dests[r['slug_fr']] = r
    return dests

def load_climate():
    data = {}
    with open(ROOT / 'data/climate.csv', encoding='utf-8-sig') as f:
        for r in csv.DictReader(f):
            slug = r['slug']
            if slug not in data:
                data[slug] = {}
            m = int(r['mois_num'])
            data[slug][m] = {
                'score': float(r['score']),
                'tmin': float(r['tmin']),
                'tmax': float(r['tmax']),
                'rain_pct': float(r['rain_pct']),
                'precip_mm': float(r['precip_mm']),
                'sun_h': float(r['sun_h']),
                'beach_score': float(r['beach_score']) if r.get('beach_score') else None,
            }
    return data

# ── Helpers ───────────────────────────────────────────────────────────────────

def e(s):
    return html_mod.escape(str(s))

def rank_icon(i):
    if i == 1: return '🥇'
    if i == 2: return '🥈'
    if i == 3: return '🥉'
    return str(i)

def score_class(s):
    if s >= 8.6: return '#1a7a4a'
    if s >= 7.6: return '#2d9e60'
    if s >= 6.3: return '#84cc16'
    if s >= 5.0: return '#f59e0b'
    if s >= 3.5: return '#f97316'
    return '#ef4444'

REGION_CHILDREN = {
    'canaries': {'lanzarote', 'fuerteventura', 'gran-canaria', 'tenerife',
                 'la-palma', 'la-gomera', 'el-hierro'},
}

# ── Geographic region mapping (pays → region code) ────────────────────────────
REGION_MAP = {
    # Europe
    'Albanie':'eu','Allemagne':'eu','Andorre':'eu','Arménie':'eu','Autriche':'eu',
    'Azerbaïdjan':'eu','Belgique':'eu','Bosnie-Herzégovine':'eu','Bulgarie':'eu',
    'Chypre':'eu','Croatie':'eu','Danemark':'eu','Espagne':'eu','Estonie':'eu',
    'Finlande':'eu','France':'eu','Gibraltar':'eu','Grèce':'eu','Géorgie':'eu',
    'Hongrie':'eu','Irlande':'eu','Islande':'eu','Italie':'eu','Lettonie':'eu',
    'Lituanie':'eu','Macédoine du Nord':'eu','Malte':'eu','Monaco':'eu',
    'Monténégro':'eu','Norvège':'eu','Pays-Bas':'eu','Pologne':'eu','Portugal':'eu',
    'Roumanie':'eu','Royaume-Uni':'eu','Russie':'eu','Serbie':'eu','Slovaquie':'eu',
    'Slovénie':'eu','Suisse':'eu','Suède':'eu','Tchéquie':'eu','Ukraine':'eu',
    'Écosse':'eu',
    # Afrique
    'Afrique du Sud':'af','Algérie':'af','Bénin':'af','Botswana':'af',
    'Burkina Faso':'af','Cameroun':'af','Cap-Vert':'af',"Côte d'Ivoire":'af',
    'Égypte':'af','Éthiopie':'af','Gabon':'af','Gambie':'af','Ghana':'af',
    'Kenya':'af','Madagascar':'af','Malawi':'af','Maroc':'af','Maurice':'af',
    'Mozambique':'af','Namibie':'af','Nigeria':'af','Ouganda':'af','Rwanda':'af',
    'Sénégal':'af','Seychelles':'af','Sierra Leone':'af','Tanzanie':'af',
    'Togo':'af','Tunisie':'af','Zambie':'af','Zimbabwe':'af',
    # Amériques (Nord + Central + Caraïbes + Sud)
    'Antigua-et-Barbuda':'am','Argentine':'am','Aruba':'am','Bahamas':'am',
    'Barbade':'am','Belize':'am','Bolivie':'am','Brésil':'am','Canada':'am',
    'Chili':'am','Colombie':'am','Costa Rica':'am','Cuba':'am','Curaçao':'am',
    'Dominique':'am','Équateur':'am','États-Unis':'am','Guatemala':'am',
    'Honduras':'am','Îles Caïmans':'am','Îles Vierges américaines':'am',
    'Jamaïque':'am','Mexique':'am','Nicaragua':'am','Panama':'am',
    'Pays-Bas caribéens':'am','Paraguay':'am','Pérou':'am','Porto Rico':'am',
    'République Dominicaine':'am','Saint-Vincent-et-les-Grenadines':'am',
    'Sainte-Lucie':'am','Trinité-et-Tobago':'am','Turks-et-Caïcos':'am',
    'Uruguay':'am',
    # Moyen-Orient (+ Asie centrale + Turquie)
    'Arabie Saoudite':'me','Bahreïn':'me','Émirats Arabes Unis':'me',
    'Émirats arabes unis':'me','Iran':'me','Israël':'me','Jordanie':'me',
    'Kazakhstan':'me','Kirghizistan':'me','Koweït':'me','Liban':'me',
    'Oman':'me','Ouzbékistan':'me','Qatar':'me','Tadjikistan':'me',
    'Turquie':'me','Yémen':'me',
    # Asie
    'Bhoutan':'as','Cambodge':'as','Chine':'as','Corée du Sud':'as',
    'Inde':'as','Indonésie':'as','Japon':'as','Laos':'as','Malaisie':'as',
    'Maldives':'as','Mongolie':'as','Myanmar':'as','Népal':'as',
    'Philippines':'as','Singapour':'as','Sri Lanka':'as','Taïwan':'as',
    'Thaïlande':'as','Vietnam':'as','Viêt Nam':'as',
    # Océanie
    'Australie':'oc','Fidji':'oc','Nouvelle-Calédonie':'oc','Nouvelle-Zélande':'oc','Îles Cook':'oc',
    'Palaos':'oc','Papouasie-Nouvelle-Guinée':'oc','Polynésie française':'oc',
    'Samoa':'oc','Tonga':'oc','Vanuatu':'oc',
}

MACARONESIA_SLUGS = {
    'canaries','tenerife','gran-canaria','fuerteventura','lanzarote',
    'la-palma','la-gomera','el-hierro',  # Canaries
    'madere','funchal',                   # Madère
    'azores',                             # Açores
    'cap-vert','sal','praia',             # Cap-Vert (déjà af mais par sécurité)
}
def _reg(pays, slug=None):
    if slug and slug in MACARONESIA_SLUGS:
        return 'af'
    return REGION_MAP.get(pays, 'other')

_REGION_LABELS = {
    'fr': {'all':'Monde','eu':'Europe','af':'Afrique',
           'am':'Amériques','as':'Asie','me':'Moyen-Orient','oc':'Océanie'},
    'en': {'all':'World','eu':'Europe','af':'Africa',
           'am':'Americas','as':'Asia','me':'Middle East','oc':'Oceania'},
    'es': {'all':'Mundo','eu':'Europa','af':'África',
           'am':'Américas','as':'Asia','me':'Oriente Medio','oc':'Oceanía'},
    'de': {'all':'Welt','eu':'Europa','af':'Afrika',
           'am':'Amerika','as':'Asien','me':'Naher Osten','oc':'Ozeanien'},
}

def build_region_tabs(lang):
    labels = _REGION_LABELS.get(lang, _REGION_LABELS['en'])
    btns = ''.join(
        f'<button class="reg-tab{" active" if k=="all" else ""}" data-reg="{k}">{v}</button>'
        for k, v in labels.items()
    )
    return btns  # juste les boutons — le wrapper est dans filter-panel


def get_rankings(climate, dests, month_idx):
    """Return top destinations for given month (1-indexed), sorted by score desc."""
    entries = []
    for slug, dest in dests.items():
        if slug not in climate or month_idx not in climate[slug]:
            continue
        m = climate[slug][month_idx]
        ski = compute_ski_score(m['tmax'], m['rain_pct'], m['sun_h'])
        entries.append({
            'slug_fr': slug,
            'slug_en': dest.get('slug_en', slug),
            'nom_bare': dest.get('nom_bare', slug),
            'nom_en': dest.get('nom_en', dest.get('nom_bare', slug)),
            'pays': dest.get('pays', ''),
            'pays_en': dest.get('country_en', dest.get('pays', '')),
            'pays_es': dest.get('country_es', dest.get('pays', '')),
            'pays_de': dest.get('country_de', dest.get('pays', '')),
            'nom_es': dest.get('nom_es', dest.get('nom_bare', '')),
            'slug_es': dest.get('slug_es', dest.get('slug_en', '')),
            'flag': dest.get('flag', ''),
            'score': m['score'],
            'tmin': m['tmin'],
            'tmax': m['tmax'],
            'rain_pct': m['rain_pct'],
            'sun_h': m['sun_h'],
            'beach_score': m['beach_score'],
            'ski_score': ski,
        })
    entries.sort(key=lambda x: (-x['score'], x['nom_bare']))
    # Remove region parents when a child island is also ranked
    ranked = {e['slug_fr'] for e in entries}
    remove = {p for p, ch in REGION_CHILDREN.items() if p in ranked and ranked & ch}
    if remove:
        entries = [e for e in entries if e['slug_fr'] not in remove]
    # Keep only best-scoring destination per country (no city+country duplicate)
    seen_countries = {}
    deduped = []
    for e in entries:
        pays = e['pays']
        if pays not in seen_countries:
            seen_countries[pays] = e['score']
            deduped.append(e)
        # else: skip — a higher-scoring entry for this country already included
    return deduped[:TOP_N]

def get_pool_entries(climate, dests, month_idx, pool_size=80, ski_boost=20):
    """Return broader pool for beach/ski JS filtering.

    - General pool: top pool_size destinations by general score (country-deduped)
    - Ski boost: top ski_boost mountain=True destinations by ski_score injected on top
      (skipping duplicates already in the general pool)
    """
    # Slugs à ignorer (doublons legacy)
    SKI_DUPES = {'val-disere', 'sierra-nevada', 'queenstown-ski'}

    all_entries = []
    for slug, dest in dests.items():
        if slug in SKI_DUPES:
            continue
        if slug not in climate or month_idx not in climate[slug]:
            continue
        m = climate[slug][month_idx]
        ski = compute_ski_score(m['tmax'], m['rain_pct'], m['sun_h'])
        all_entries.append({
            'slug_fr': slug,
            'slug_en': dest.get('slug_en', slug),
            'nom_bare': dest.get('nom_bare', slug),
            'nom_en': dest.get('nom_en', dest.get('nom_bare', slug)),
            'nom_es': dest.get('nom_es', dest.get('nom_bare', '')),
            'nom_de': dest.get('nom_de', dest.get('nom_en', '')),
            'slug_es': dest.get('slug_es', dest.get('slug_en', '')),
            'slug_de': dest.get('slug_de', dest.get('slug_en', '')),
            'pays': dest.get('pays', ''),
            'pays_en': dest.get('country_en', dest.get('pays', '')),
            'pays_es': dest.get('country_es', dest.get('pays', '')),
            'pays_de': dest.get('country_de', dest.get('pays', '')),
            'flag': dest.get('flag', ''),
            'score': m['score'],
            'tmin': m['tmin'],
            'tmax': m['tmax'],
            'rain_pct': m['rain_pct'],
            'sun_h': m['sun_h'],
            'beach_score': m['beach_score'],
            'ski_score': ski,
            'is_mountain': dest.get('mountain', 'False') == 'True',
            'is_coastal':  dest.get('coastal',  'False') == 'True',
        })

    # --- General pool (country-deduped, by general score) ---
    general = sorted(all_entries, key=lambda x: (-x['score'], x['nom_bare']))
    ranked = {e['slug_fr'] for e in general}
    remove = {p for p, ch in REGION_CHILDREN.items() if p in ranked and ranked & ch}
    if remove:
        general = [e for e in general if e['slug_fr'] not in remove]
    # Remove country-slugs when ANY city from the same country exists in all_entries
    countries_with_cities = {e['pays'] for e in general if e['slug_fr'] not in COUNTRY_SLUGS}
    general = [e for e in general
               if e['slug_fr'] not in COUNTRY_SLUGS or e['pays'] not in countries_with_cities]
    # 1 destination per country
    seen_countries: dict = {}
    deduped: list = []
    for e in general:
        if e['pays'] not in seen_countries:
            seen_countries[e['pays']] = True
            deduped.append(e)
    general_pool = deduped[:pool_size]
    general_slugs = {e['slug_fr'] for e in general_pool}

    # --- Ski boost: top mountain destinations not already in general pool ---
    ski_candidates = [e for e in all_entries if e['is_mountain'] and e['slug_fr'] not in general_slugs]
    ski_candidates.sort(key=lambda x: (-x['ski_score'], x['nom_bare']))
    ski_injected = ski_candidates[:ski_boost]

    # --- Region boost: ensure EU has enough entries for JS filter ---
    from generate_classements import EUROPE_COUNTRIES, NON_EUROPE_SLUGS as _NEU
    all_in_pool = {e['slug_fr'] for e in general_pool + ski_injected}
    eu_candidates = [e for e in all_entries
                     if e['pays'] in EUROPE_COUNTRIES
                     and e['slug_fr'] not in _NEU
                     and not e['is_mountain']
                     and e['slug_fr'] not in all_in_pool]
    eu_candidates.sort(key=lambda x: (-x['score'], x['nom_bare']))
    eu_seen: dict = {}
    eu_boost = []
    for e in eu_candidates:
        if e['pays'] not in eu_seen and len(eu_boost) < 30:
            eu_seen[e['pays']] = True
            eu_boost.append(e)

    # --- Beach boost: top coastal destinations by beach_score, 1 per country ---
    # Ensures beach tab ranking reflects true beach quality, not just general score
    all_slugs = {e['slug_fr'] for e in general_pool + ski_injected + eu_boost}
    countries_in_pool2 = {e['pays'] for e in general_pool + ski_injected + eu_boost}
    beach_candidates = [e for e in all_entries
                        if e.get('beach_score') is not None
                        and e.get('is_coastal', False)
                        and (e['beach_score'] or 0) >= 3.5
                        and e['slug_fr'] not in all_slugs
                        and not (e['slug_fr'] in COUNTRY_SLUGS and e['pays'] in countries_in_pool2)]
    beach_candidates.sort(key=lambda x: (-(x['beach_score'] or 0), x['nom_bare']))
    seen_beach_countries: dict = {}
    beach_injected = []
    for e in beach_candidates:
        if e['pays'] not in seen_beach_countries:
            seen_beach_countries[e['pays']] = True
            beach_injected.append(e)
    beach_injected = beach_injected[:40]

    return general_pool + ski_injected + eu_boost + beach_injected

CSS = r"""
*{margin:0;padding:0;box-sizing:border-box}
:root{--navy:#1a2332;--gold:#d4a853;--cream:#faf6ef;--cream2:#ede4d3;--text:#2c3e50;--slate:#5a6c7d;--slate2:#8899a6}
body{font-family:'DM Sans',system-ui,sans-serif;background:var(--cream);color:var(--text);line-height:1.6}
.pillar-hero{background:var(--navy);color:white;padding:48px 20px 36px;text-align:center}
.hero-eyebrow{font-size:11px;text-transform:uppercase;letter-spacing:2.5px;color:#9c5f00;margin-bottom:12px;font-weight:700}
.hero-title{font-family:'Playfair Display',Georgia,serif;font-size:clamp(24px,5vw,38px);margin-bottom:10px;line-height:1.2}
.hero-title em{color:var(--gold);font-style:italic}
.hero-sub{font-size:15px;opacity:.75;max-width:600px;margin:0 auto 20px}
.hero-stats{display:flex;justify-content:center;gap:36px;margin-top:16px}
.hstat{text-align:center}.hstat-val{display:block;font-size:22px;font-weight:700;color:var(--gold)}.hstat-lbl{font-size:11px;opacity:.6;text-transform:uppercase;letter-spacing:1px}
.page{max-width:960px;margin:0 auto;padding:28px 16px 40px}
.section{margin-bottom:36px}
.eyebrow{font-size:10px;text-transform:uppercase;letter-spacing:2px;color:#9c5f00;font-weight:700;margin-bottom:6px}
.sec-title{font-family:'Playfair Display',Georgia,serif;font-size:clamp(18px,4vw,24px);margin-bottom:8px}
.sec-intro{font-size:14px;color:var(--slate);margin-bottom:18px}
.rt{width:100%;border-collapse:collapse;font-size:13px}
.rt th{background:var(--navy);color:white;padding:10px 10px;text-align:left;font-size:11px;text-transform:uppercase;letter-spacing:.5px;font-weight:700;position:sticky;top:0;white-space:nowrap}
.rt td{padding:9px 10px;border-bottom:1px solid var(--cream2);vertical-align:middle;white-space:nowrap}
.rt tr:hover{background:#fef9f0}
.rt .rank{font-weight:700;font-size:15px;text-align:center;width:36px;padding-left:4px}
.rt .sc{font-weight:700;color:var(--navy);font-size:14px;white-space:nowrap}
.rt td:nth-child(2){white-space:normal;min-width:130px}
.dest-link{color:var(--text);text-decoration:none;font-weight:600}
.dest-link:hover{color:var(--gold)}
.region-tag{display:inline-block;font-size:10px;color:var(--slate);background:var(--cream);padding:2px 8px;border-radius:10px;margin-left:8px;vertical-align:middle}
.filter-panel{background:var(--cream);border:1.5px solid var(--cream2);border-radius:14px 14px 0 0;padding:8px 14px 6px;margin-bottom:0;display:flex;flex-direction:column;gap:0}.filter-row{display:flex;flex-direction:column;gap:6px;padding:5px 0;border-bottom:1px solid var(--cream2)}.filter-row:last-child{border-bottom:none;padding-bottom:2px}.filter-label{font-size:9px;font-weight:700;color:var(--slate);letter-spacing:.08em;text-transform:uppercase}.filter-btns{display:flex;gap:4px;flex-wrap:wrap;align-items:center}.month-nav{display:flex;gap:4px;flex-wrap:wrap;align-items:center}.month-nav a{padding:4px 8px;border-radius:10px;font-size:11px;font-weight:600;text-decoration:none;background:white;border:1.5px solid var(--cream2);color:var(--navy);white-space:nowrap;flex-shrink:0}.month-nav a.active{background:var(--gold);color:white;border-color:var(--gold)}.month-nav a:hover{border-color:var(--gold)}
.filter-panel+.section{border:1.5px solid var(--cream2);border-top:none;border-radius:0 0 14px 14px;padding:12px 14px 0;margin-bottom:16px}.cta-box{background:linear-gradient(135deg,#d4a853,#c69a3a);border-radius:14px;padding:24px;text-align:center;margin:28px 0}
.cta-box a{color:white;font-weight:700;font-size:15px;text-decoration:none}
.related-pages{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:12px;margin-top:16px}
.related-card{background:white;border:1.5px solid var(--cream2);border-radius:12px;padding:16px;text-decoration:none;color:var(--text);display:block}
.related-card:hover{border-color:var(--gold);background:#fffbf0}
.related-card strong{display:block;font-size:13px;font-weight:700;margin-bottom:4px}
.related-card span{font-size:11px;color:var(--slate2)}
footer{background:var(--navy);color:#b8bcc8;text-align:center;padding:36px 20px;font-size:12px;line-height:2}
footer a{color:#f5d060;text-decoration:none}
.nav-share{display:none}
@media(pointer:coarse),(max-width:768px){.nav-share{display:flex}}
@media(max-width:640px){.rt th:nth-child(5),.rt td:nth-child(5){display:none}.hero-stats{gap:20px}}
.mode-tabs{display:flex;gap:6px;flex-wrap:wrap}
.mode-tab{display:inline-flex;align-items:center;gap:5px;padding:5px 11px;border-radius:10px;font-size:12px;font-weight:600;cursor:pointer;border:1.5px solid var(--cream2);background:white;color:var(--navy);transition:all .15s}
.mode-tab.active{background:var(--gold);color:white;border-color:var(--gold);border-radius:10px}
.mode-tab:hover:not(.active){border-color:var(--gold)}
.reg-tabs{display:flex;gap:6px;flex-wrap:wrap}
.reg-tab{padding:5px 11px;border-radius:10px;font-size:12px;font-weight:600;cursor:pointer;border:1.5px solid var(--cream2);background:white;color:var(--navy);transition:all .15s;white-space:nowrap}
.reg-tab.active{background:var(--gold);color:white;border-color:var(--gold)}
.reg-tab:hover:not(.active){border-color:var(--gold)}
"""

FONTS = (
    '<link rel="preconnect" href="https://fonts.googleapis.com"/>'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin/>'
    '<link rel="preload" as="style" href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;1,700&family=DM+Sans:wght@400;500;700&display=swap" onload="this.onload=null;this.rel=\'stylesheet\'"/>'
    '<noscript><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;1,700&family=DM+Sans:wght@400;500;700&display=swap"/></noscript>'
)

# ── Page Builders ─────────────────────────────────────────────────────────────

def build_table(entries, loc, mi):
    """Build tbody rows only (thead injected by JS for mode switching)."""
    is_fr = loc['meta']['html_lang'] == 'fr'
    is_es = loc['meta']['html_lang'] == 'es'
    imperial = loc['meta'].get('imperial', False)
    gen = loc['gen']
    month_url = loc['month_url']

    def _ft(celsius): return f"{c_to_f(celsius):.0f}°F" if imperial else f"{celsius:.0f}°C"

    rows = ''
    for i, entry in enumerate(entries, 1):
        slug = entry['slug_fr'] if is_fr else (entry.get('slug_es') or entry['slug_en'] if is_es else entry['slug_en'])
        nom = entry['nom_bare'] if is_fr else (entry.get('nom_es') or entry['nom_bare'] if is_es else entry['nom_en'])
        lang = loc['meta']['html_lang']
        if is_fr:
            pays = entry['pays']
        elif is_es:
            pays = entry.get('pays_es') or entry['pays']
        elif lang == 'de':
            pays = entry.get('pays_de') or entry['pays']
        else:
            pays = entry.get('pays_en') or entry['pays']
        href = gen['monthly_href_tpl'].format(slug=slug, month_slug=month_url[mi])
        flag_img = f'<img src="{gen["asset_prefix"]}flags/{entry["flag"]}.png" width="16" height="12" alt="" style="vertical-align:middle;margin-right:6px;border-radius:1px">'
        sc = entry['score']
        sc_color = score_class(sc)
        pays_html = f'<span class="region-tag">{e(pays)}</span>' if pays else ''
        rows += (
            f'<tr>'
            f'<td class="rank">{rank_icon(i)}</td>'
            f'<td>{flag_img}<a href="{href}" class="dest-link">{e(nom)}</a>{pays_html}</td>'
            f'<td class="sc" style="color:{sc_color}">{sc:.1f}<span>/10</span></td>'
            f'<td>{_ft(entry["tmin"])}–{_ft(entry["tmax"])}</td>'
            f'<td>{entry["rain_pct"]:.0f}%</td>'
            f'<td>{entry["sun_h"]:.1f}h</td>'
            f'</tr>'
        )
    return rows

def build_month_nav(mi, loc, is_annual=False):
    """Build month navigation bar. mi=-1 means annual page."""
    months = loc['months']
    month_url = loc['month_url']
    pil = loc['pilier']
    prefix = pil['pillar_prefix']
    all_year_url = pil.get('all_year_url', '')
    all_year_nav = pil.get('all_year_nav', 'All year')
    # "Toute l'année" button
    active_annual = ' class="active"' if is_annual else ''
    links = f'<a href="{all_year_url}"{active_annual}>{all_year_nav}</a>'
    for i in range(12):
        active = ' class="active"' if (not is_annual and i == mi) else ''
        links += f'<a href="{prefix}{month_url[i]}.html"{active}>{months[i][:3]}</a>'
    return f'<div class="month-nav" aria-label="{pil["months_label"]}">{links}</div>'

def build_related(mi, loc):
    """Build related ranking cards."""
    months = loc['months']
    month_url = loc['month_url']
    pil = loc['pilier']
    prefix = pil['pillar_prefix']
    cards = []
    # Adjacent months
    for offset in [-1, 1]:
        adj = (mi + offset) % 12
        month_name = months[adj]
        label = pil['where_to_go_tpl'].format(month=month_name.lower() if loc['meta'].get('lowercase_months') else month_name)
        cards.append(f'<a href="{prefix}{month_url[adj]}.html" class="related-card"><strong>{label}</strong><span>Top {TOP_N} {pil["top_n_label"]}</span></a>')
    # General ranking
    cards.append(f'<a href="{pil["world_ranking_url"]}" class="related-card"><strong>{pil["world_ranking_label"]}</strong><span>{pil["world_ranking_sub"]}</span></a>')
    return f'<div class="section"><div class="eyebrow">{pil["also_explore"]}</div><h2 class="sec-title">{pil["other_rankings"]}</h2><div class="related-pages">{"".join(cards)}</div></div>'


def generate_page(mi, lang, dests, climate):
    """Generate one pillar page for month mi (0-indexed) in given language."""
    loc = load_locale(lang)
    gen = loc['gen']
    pil = loc['pilier']
    is_fr = (lang == 'fr')
    imperial = loc['meta'].get('imperial', False)
    months = loc['months']
    month_url = loc['month_url']
    month_name = months[mi]
    month_slug = month_url[mi]
    season_map = {int(k): v for k, v in loc['seasons_map'].items()}
    season = season_map.get(mi, '')

    # Temperature formatting helper
    def ft(celsius): return f"{c_to_f(celsius):.0f}°F" if imperial else f"{celsius:.0f}°C"
    def ft_unit(): return '°F' if imperial else '°C'

    entries = get_rankings(climate, dests, mi + 1)  # climate.csv is 1-indexed
    pool = get_pool_entries(climate, dests, mi + 1)  # broader pool for beach/ski JS
    if not entries:
        print(f"  ⚠️  No data for month {mi}")
        return

    top = entries[0]
    avg_score = sum(x['score'] for x in entries[:10]) / 10
    avg_temp_raw = sum(x['tmax'] for x in entries[:10]) / 10
    avg_temp = c_to_f(avg_temp_raw) if imperial else avg_temp_raw

    # File paths — cross-lang links built dynamically from all locales
    is_es = (lang == 'es')
    is_de = (lang == 'de')
    src_sub = loc['meta']['subdir']  # '' for FR, 'en', 'es', ...
    filename = f'{pil["pillar_prefix"]}{month_slug}.html'

    if src_sub == '':
        filepath = ROOT / filename
    else:
        filepath = ROOT / src_sub / filename
    canonical = (f'https://bestdateweather.com/{filename}'
                 if src_sub == '' else
                 f'https://bestdateweather.com/{src_sub}/{filename}')

    # Build cross-lang link list for all other langs
    # PILIER_LANGS is module-level, derived from locales/ at import time

    def _cross_url(dst_lang):
        """Relative URL from src_sub to dst pilier page."""
        dst_loc = load_locale(dst_lang)
        dst_sub = dst_loc['meta']['subdir']
        dst_file = f'{dst_loc["pilier"]["pillar_prefix"]}{dst_loc["month_url"][mi]}.html'
        if src_sub == dst_sub:
            return dst_file
        elif src_sub == '':
            return f'{dst_sub}/{dst_file}'
        elif dst_sub == '':
            return f'../{dst_file}'
        else:
            return f'../{dst_sub}/{dst_file}'

    cross_links = []
    for dst_lang in PILIER_LANGS:
        if dst_lang == lang:
            continue
        dst_loc = load_locale(dst_lang)
        cross_links.append({
            'lang':  dst_lang,
            'url':   _cross_url(dst_lang),
            'flag':  f'{loc["meta"]["asset_prefix"]}{dst_loc["meta"]["flag"]}',
            'label': dst_loc['meta']['lang_label'],
            'abs':   (f'https://bestdateweather.com/{dst_loc["pilier"]["pillar_prefix"]}{dst_loc["month_url"][mi]}.html'
                      if dst_loc['meta']['subdir'] == '' else
                      f'https://bestdateweather.com/{dst_loc["meta"]["subdir"]}/{dst_loc["pilier"]["pillar_prefix"]}{dst_loc["month_url"][mi]}.html'),
        })

    # Build hreflang data from cross_links + self
    _all_hreflang = {c['lang']: c['abs'] for c in cross_links}
    _all_hreflang[lang] = canonical  # self
    hreflang_fr = _all_hreflang.get('fr', '')
    hreflang_en = _all_hreflang.get('en', '')
    # Generate <link> tags dynamically for all langs
    _hreflang_lines = []
    for _hl_lang, _hl_url in sorted(_all_hreflang.items()):
        _hreflang_lines.append(f'<link rel="alternate" hreflang="{_hl_lang}" href="{_hl_url}"/>')
    if hreflang_en:
        _hreflang_lines.append(f'<link rel="alternate" hreflang="x-default" href="{hreflang_en}"/>')
    hreflang_tags = '\n'.join(_hreflang_lines)

    # Month name for display (lowercase in FR)
    mn_lc = month_name.lower() if loc['meta'].get('lowercase_months') else month_name

    # Content — keep is_fr for complex text blocks
    nom_es = lambda e: e.get('nom_es') or e.get('nom_bare', '')
    if is_es:
        title = f"Adónde ir en {month_name} {YEAR} — Top {TOP_N} destinos por clima"
        desc = (f"¿Adónde ir en {month_name} {YEAR}? Top {TOP_N} destinos por clima. "
                f"N°1: {nom_es(top)} ({top['score']:.1f}/10, {top['tmax']:.0f}°C). "
                f"Basado en 10 años de datos Open-Meteo.")
        h1 = f"¿Adónde ir en <em>{month_name}</em>?"
        hero_sub = (f"Los {TOP_N} mejores destinos por clima en {month_name} {YEAR}, "
                    f"clasificados por puntuación climática basada en 10 años de datos.")
        sec_eyebrow = f"Ranking {month_name} {YEAR}"
        sec_title = f"Top {TOP_N} destinos en {month_name}"
        sec_intro = (f"Puntuación media top 10: <strong>{avg_score:.1f}/10</strong> · "
                     f"Temperatura media: <strong>{avg_temp:.0f}°C</strong>")
        cta_text = f"🎯 Elige una fecha exacta para tu viaje en {month_name}"
    elif is_fr:
        title = f"Où partir en {mn_lc} {YEAR} ? Top {TOP_N} destinations météo"
        desc = (f"Où partir en {mn_lc} {YEAR} ? Classement des {TOP_N} meilleures destinations "
                f"par score météo. N°1 : {top['nom_bare']} ({top['score']:.1f}/10, {top['tmax']:.0f}°C). "
                f"Données 10 ans Open-Meteo.")
        h1 = f"Où partir en <em>{mn_lc}</em> ?"
        hero_sub = (f"Les {TOP_N} meilleures destinations météo pour {mn_lc} {YEAR}, "
                    f"classées par score climatique sur 10 ans de données.")
        sec_eyebrow = f"Classement {month_name} {YEAR}"
        sec_title = f"Top {TOP_N} destinations en {mn_lc}"
        sec_intro = (f"Score moyen du top 10 : <strong>{avg_score:.1f}/10</strong> · "
                     f"Température moyenne : <strong>{avg_temp:.0f}°C</strong>")
        cta_text = f"🎯 Choisir une date précise pour votre voyage en {mn_lc}"
    elif is_de:
        nom_de = lambda e: e.get('nom_de') or e.get('nom_en', '')
        title = f"Wohin im {month_name} {YEAR} — Top {TOP_N} Reiseziele nach Wetter"
        desc = (f"Wohin im {month_name} {YEAR}? Top {TOP_N} Reiseziele nach Wetter-Score. "
                f"Nr. 1: {nom_de(top)} ({top['score']:.1f}/10, {top['tmax']:.0f}°C). "
                f"Basierend auf 10 Jahren Open-Meteo-Daten.")
        h1 = f"Wohin im <em>{month_name}</em>?"
        hero_sub = (f"Die {TOP_N} besten Reiseziele nach Wetter im {month_name} {YEAR}, "
                    f"gerankt nach Klima-Score auf Basis von 10 Jahren Daten.")
        sec_eyebrow = f"{month_name} {YEAR} Ranking"
        sec_title = f"Top {TOP_N} Reiseziele im {month_name}"
        sec_intro = (f"Ø Score Top 10: <strong>{avg_score:.1f}/10</strong> · "
                     f"Ø Temperatur: <strong>{avg_temp:.0f}°C</strong>")
        cta_text = f"🎯 Genaues Datum für Ihre Reise im {month_name} wählen"
    else:
        title = f"Where to Go in {month_name} {YEAR} — Top {TOP_N} Weather Destinations"
        desc = (f"Where to go in {month_name} {YEAR}? Top {TOP_N} destinations ranked by weather score. "
                f"#1: {top['nom_en']} ({top['score']:.1f}/10, {ft(top['tmax'])}). "
                f"Based on 10 years of Open-Meteo data.")
        h1 = f"Where to Go in <em>{month_name}</em>"
        hero_sub = (f"The {TOP_N} best weather destinations for {month_name} {YEAR}, "
                    f"ranked by climate score based on 10 years of data.")
        sec_eyebrow = f"{month_name} {YEAR} ranking"
        sec_title = f"Top {TOP_N} destinations in {month_name}"
        sec_intro = (f"Top 10 average score: <strong>{avg_score:.1f}/10</strong> · "
                     f"Average temperature: <strong>{avg_temp:.0f}{ft_unit()}</strong>")
        cta_text = f"🎯 Choose a specific date for your {month_name} trip"

    cta_href = gen['home_url']
    flag_prefix = gen['asset_prefix']
    if is_fr:
        tab_meteo = '☀️ Météo générale'
        tab_beach = '🏖️ Plage'
        tab_ski   = '⛷️ Ski'
        th_score_beach = 'Score plage'
        th_score_ski   = 'Score ski'
        th_score_gen   = 'Score'
        no_beach_msg   = "Aucune destination côtière dans ce classement pour ce mois."
        no_ski_msg     = "Aucune destination ski dans ce classement pour ce mois."
        no_meteo_msg   = "Aucune destination dans cette région pour ce mois."
    elif is_es:
        tab_meteo = '☀️ Clima general'
        tab_beach = '🏖️ Playa'
        tab_ski   = '⛷️ Esquí'
        th_score_beach = 'Score playa'
        th_score_ski   = 'Score esquí'
        th_score_gen   = 'Score'
        no_beach_msg   = "No hay destinos costeros en este ranking para este mes."
        no_ski_msg     = "No hay destinos de esquí en este ranking para este mes."
        no_meteo_msg   = "No hay destinos en esta región para este mes."
    elif is_de:
        tab_meteo = '☀️ Allgemeines Wetter'
        tab_beach = '🏖️ Strand'
        tab_ski   = '⛷️ Ski'
        th_score_beach = 'Strand-Score'
        th_score_ski   = 'Ski-Score'
        th_score_gen   = 'Score'
        no_beach_msg   = "Keine Küstenziele in diesem Ranking für diesen Monat."
        no_ski_msg     = "Keine Ski-Ziele in diesem Ranking für diesen Monat."
        no_meteo_msg   = "Keine Ziele in dieser Region für diesen Monat."
    else:
        tab_meteo = '☀️ General weather'
        tab_beach = '🏖️ Beach'
        tab_ski   = '⛷️ Ski'
        th_score_beach = 'Beach score'
        th_score_ski   = 'Ski score'
        th_score_gen   = 'Score'
        no_beach_msg   = "No coastal destinations in this ranking for this month."
        no_ski_msg     = "No ski destinations in this ranking for this month."
        no_meteo_msg   = "No destinations in this region for this month."

    # ── Pool JSON for JS rendering ────────────────────────────────────────────
    def entry_nom(entry):
        if is_fr: return entry['nom_bare']
        if is_es: return entry.get('nom_es') or entry['nom_bare']
        if is_de: return entry.get('nom_de') or entry['nom_en']
        return entry['nom_en']
    def entry_slug(entry):
        if is_fr: return entry['slug_fr']
        if is_es: return entry.get('slug_es') or entry['slug_en']
        if is_de: return entry.get('slug_de') or entry['slug_en']
        return entry['slug_en']
    def entry_pays(entry):
        if is_fr: return entry['pays']
        if is_es: return entry.get('pays_es') or entry['pays']
        if is_de: return entry.get('pays_de') or entry['pays']
        return entry.get('pays_en') or entry['pays']

    pool_json = json.dumps([{
        'n': entry_nom(p),
        'p': entry_pays(p),
        'f': p['flag'],
        'h': gen['monthly_href_tpl'].format(slug=entry_slug(p), month_slug=month_url[mi]),
        's': round(p['score'], 1),
        'b': round(p['beach_score'], 1) if p['beach_score'] is not None else None,
        'br': round(p['beach_score'], 4) if p['beach_score'] is not None else None,
        'k': round(p['ski_score'], 1),
        'm': 1 if p['is_mountain'] else 0,
        'ap': f'{flag_prefix}flags/{p["flag"]}.png',
        'r': round(p['rain_pct'], 0),
        'sun': round(p['sun_h'], 1),
        'tmin': round(p['tmin'], 0),
        'tmax': round(p['tmax'], 0),
        'reg': _reg(p['pays'], p['slug_fr']),
        'xeu': 1 if p['slug_fr'] in NON_EUROPE_SLUGS else 0,
    } for p in pool], ensure_ascii=False)

    region_tabs = build_region_tabs(lang)
    table_body = build_table(entries, loc, mi)
    month_nav = build_month_nav(mi, loc)
    related = build_related(mi, loc)

    mode_tabs_inner = (
        f'<button class="mode-tab active" data-mode="meteo">{tab_meteo}</button>'
        f'<button class="mode-tab" data-mode="beach">{tab_beach}</button>'
        f'<button class="mode-tab" data-mode="ski">{tab_ski}</button>'
    )
    region_tabs_inner = region_tabs
    fp_period = loc.get('fp_period', 'PÉRIODE')
    fp_region = loc.get('fp_region', 'RÉGION')
    fp_type   = loc.get('fp_type',   'TYPE')

    rank_js = (
        '<script>(function(){'
        f'var POOL={pool_json};'
        'var TOP=25;var CUR_REG="all";'
        f'var TH_GEN="{e(th_score_gen)}",TH_BEACH="{e(th_score_beach)}",TH_SKI="{e(th_score_ski)}";'
        f'var NO_BEACH="{e(no_beach_msg)}",NO_SKI="{e(no_ski_msg)}",NO_METEO="{e(no_meteo_msg)}";'
        'function sc(s){return s>=8.6?"#1a7a4a":s>=7.6?"#2d9e60":s>=6.3?"#84cc16":s>=5?"#f59e0b":s>=3.5?"#f97316":"#ef4444";}'
        'function ri(i){return i===1?"🥇":i===2?"🥈":i===3?"🥉":String(i);}'
        'function render(mode){'
        'var tb=document.getElementById("rt-body");'
        'var th=document.getElementById("rt-head");'
        'var msg=document.getElementById("rt-msg");'
        'if(!tb)return;'
        'var key=mode==="beach"?"b":mode==="ski"?"k":"s";'
        'var list=POOL.filter(function(d){var rOk=CUR_REG==="all"||(d.reg===CUR_REG&&!(CUR_REG==="eu"&&d.xeu));var mOk=mode==="beach"?(d.b!=null&&d.b>=3.5):mode==="ski"?(d.m===1&&d.k>=4&&d.tmax<=25):(d.m!==1);return rOk&&mOk;});'
        'list.sort(function(a,b){var d=(b[key]||0)-(a[key]||0);return d!==0?d:(key==="b"?(b.br||0)-(a.br||0):0);});'
        'list=list.slice(0,TOP);'
        'if(list.length===0){tb.innerHTML="";msg.textContent=mode==="beach"?NO_BEACH:(mode==="ski"?NO_SKI:NO_METEO);msg.style.display="block";return;}'
        'msg.style.display="none";'
        'var label=mode==="beach"?TH_BEACH:mode==="ski"?TH_SKI:TH_GEN;'
        'th.innerHTML="<tr><th>#</th><th>Destination</th><th>"+label+"</th><th>Temp.</th><th>Pluie</th><th>Soleil/j</th></tr>";'
        'var html="";'
        'list.forEach(function(d,i){'
        'var v=d[key]!=null?d[key]:d.s;'
        'var tmp=d.tmin!=null?(d.tmin.toFixed(0)+"°–"+d.tmax.toFixed(0)+"°"):"—";'
        'html+="<tr>"'
        '+"<td class=\'rank\'>"+ri(i+1)+"</td>"'
        '+"<td><img src=\'"+d.ap+"\' width=\'16\' height=\'12\' alt=\'\' style=\'vertical-align:middle;margin-right:6px;border-radius:1px\'><a href=\'"+d.h+"\' class=\'dest-link\'>"+d.n+"</a>"+(d.p?"<span style=\'display:block;font-size:11px;color:#5a6c7d\'>"+d.p+"</span>":"")+"</td>"'
        '+"<td class=\'sc\' style=\'color:"+sc(v)+"\'>"+v.toFixed(1)+"<span>/10</span></td>"'
        '+"<td>"+tmp+"</td>"'
        '+"<td>"+(d.r!=null?d.r.toFixed(0)+"%":"—")+"</td>"'
        '+"<td>"+(d.sun!=null?d.sun.toFixed(1)+"h":"—")+"</td>"'
        '+"</tr>";'
        '});'
        'tb.innerHTML=html;'
        'var _s1=document.getElementById("stat-score");'
        'if(_s1&&list.length){'
        'var _top=list[0];var _topV=_top[key]!=null?_top[key]:_top.s;'
        '_s1.textContent=_topV.toFixed(1);'
        'document.getElementById("stat-count").textContent=list.length;'
        'var _avgT=list.slice(0,10).reduce(function(a,d){return a+(d.tmin+d.tmax)/2;},0)/Math.min(10,list.length);'
        'var _s3=document.getElementById("stat-temp");if(_s3)_s3.textContent=Math.round(_avgT)+"°";'
        '}'
        '}'
        'document.getElementById("mode-tabs").addEventListener("click",function(ev){'
        'var btn=ev.target.closest(".mode-tab");'
        'if(!btn)return;'
        'document.querySelectorAll(".mode-tab").forEach(function(b){b.classList.remove("active");});'
        'btn.classList.add("active");'
        'render(btn.dataset.mode);'
        '});'
        'document.getElementById("reg-tabs").addEventListener("click",function(ev){'
        'var btn=ev.target.closest(".reg-tab");'
        'if(!btn)return;'
        'document.querySelectorAll(".reg-tab").forEach(function(b){b.classList.remove("active");});'
        'btn.classList.add("active");'
        'CUR_REG=btn.dataset.reg;'
        'var activeMode=document.querySelector(".mode-tab.active");'
        'render(activeMode?activeMode.dataset.mode:"meteo");'
        '});'
        'var _p=new URLSearchParams(location.search);var _initMode=_p.get("mode")||"meteo";var _initReg=_p.get("reg")||"all";CUR_REG=_initReg;if(_initReg!=="all"){document.querySelectorAll(".reg-tab").forEach(function(b){b.classList.toggle("active",b.dataset.reg===_initReg);});}if(_initMode!=="meteo"){document.querySelectorAll(".mode-tab").forEach(function(b){b.classList.toggle("active",b.dataset.mode===_initMode);});}render(_initMode);document.querySelectorAll(".month-nav a").forEach(function(a){a.addEventListener("click",function(ev){var am=document.querySelector(".mode-tab.active");var ar=document.querySelector(".reg-tab.active");var m=am?am.dataset.mode:"meteo";var r=ar?ar.dataset.reg:"all";if(m==="meteo"&&r==="all")return;ev.preventDefault();var url=this.href.split("?")[0];var q=[];if(m!=="meteo")q.push("mode="+m);if(r!=="all")q.push("reg="+r);location.href=url+(q.length?"?"+q.join("&"):"");});});'
        '})();</script>'
    )

    # Schema.org
    breadcrumb_name = pil['where_to_go_tpl'].format(month=mn_lc)
    breadcrumb = json.dumps({
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1,
             "name": loc['labels']['breadcrumb_home'],
             "item": loc['meta']['schema_home_url']},
            {"@type": "ListItem", "position": 2,
             "name": breadcrumb_name, "item": canonical}
        ]
    }, ensure_ascii=False)

    itemlist = json.dumps({
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": title,
        "numberOfItems": len(entries),
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": i + 1,
                "name": entry['nom_bare'] if is_fr else (entry.get('nom_es') or entry['nom_bare'] if is_es else (entry.get('nom_de') or entry['nom_en'] if is_de else entry['nom_en'])),
                "url": loc['meta']['canonical_prefix'] + gen['monthly_href_tpl'].format(
                    slug=entry['slug_fr'] if is_fr else (entry.get('slug_es') or entry['slug_en'] if is_es else (entry.get('slug_de') or entry['slug_en'] if is_de else entry['slug_en'])),
                    month_slug=month_url[mi])
            }
            for i, entry in enumerate(entries)
        ]
    }, ensure_ascii=False)

    # FAQ — keep is_fr for complex content
    faq_items = []
    if is_fr:
        faq_items.append({"@type": "Question",
            "name": f"Quelle est la meilleure destination en {mn_lc} ?",
            "acceptedAnswer": {"@type": "Answer",
                "text": f"{top['nom_bare']} est la destination n°1 en {mn_lc} avec un score de {top['score']:.1f}/10 et {top['tmax']:.0f}°C."}})
        faq_items.append({"@type": "Question",
            "name": f"Où partir au soleil en {mn_lc} ?",
            "acceptedAnswer": {"@type": "Answer",
                "text": f"Les destinations les plus ensoleillées en {mn_lc} sont {entries[0]['nom_bare']}, {entries[1]['nom_bare']} et {entries[2]['nom_bare']}, avec des scores de {entries[0]['score']:.1f} à {entries[2]['score']:.1f}/10."}})
    elif is_es:
        faq_items.append({"@type": "Question",
            "name": f"¿Cuál es el mejor destino en {month_name}?",
            "acceptedAnswer": {"@type": "Answer",
                "text": f"{nom_es(top)} es el destino n°1 en {month_name} con una puntuación de {top['score']:.1f}/10 y {top['tmax']:.0f}°C."}})
        faq_items.append({"@type": "Question",
            "name": f"¿Adónde ir con buen tiempo en {month_name}?",
            "acceptedAnswer": {"@type": "Answer",
                "text": f"Los destinos con mejor clima en {month_name} son {nom_es(entries[0])}, {nom_es(entries[1])} y {nom_es(entries[2])}, con puntuaciones de {entries[0]['score']:.1f} a {entries[2]['score']:.1f}/10."}})
    elif is_de:
        nom_de_fn = lambda e: e.get('nom_de') or e.get('nom_en', '')
        faq_items.append({"@type": "Question",
            "name": f"Was ist das beste Reiseziel im {month_name}?",
            "acceptedAnswer": {"@type": "Answer",
                "text": f"{nom_de_fn(top)} ist das Top-Reiseziel im {month_name} mit einem Score von {top['score']:.1f}/10 und {top['tmax']:.0f}°C."}})
        faq_items.append({"@type": "Question",
            "name": f"Wohin reisen mit gutem Wetter im {month_name}?",
            "acceptedAnswer": {"@type": "Answer",
                "text": f"Die besten Reiseziele im {month_name} sind {nom_de_fn(entries[0])}, {nom_de_fn(entries[1])} und {nom_de_fn(entries[2])}, mit Scores von {entries[2]['score']:.1f} bis {entries[0]['score']:.1f}/10."}})
    else:
        faq_items.append({"@type": "Question",
            "name": f"What is the best destination in {month_name}?",
            "acceptedAnswer": {"@type": "Answer",
                "text": f"{top['nom_en']} is the #1 destination in {month_name} with a score of {top['score']:.1f}/10 and {ft(top['tmax'])}."}})
        faq_items.append({"@type": "Question",
            "name": f"Where is it sunny in {month_name}?",
            "acceptedAnswer": {"@type": "Answer",
                "text": f"The sunniest destinations in {month_name} are {entries[0]['nom_en']}, {entries[1]['nom_en']} and {entries[2]['nom_en']}, with scores from {entries[2]['score']:.1f} to {entries[0]['score']:.1f}/10."}})

    faq_schema = json.dumps({
        "@context": "https://schema.org", "@type": "FAQPage",
        "mainEntity": faq_items
    }, ensure_ascii=False)

    # Footer — built from ranking_footer locale section + cross-language links
    footer = footer_ranking_html(lang, [{'url': c['url'], 'flag': c['flag'], 'label': c['label']} for c in cross_links])

    flag_prefix = gen['asset_prefix']

    page_html = f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="UTF-8"/><meta name="viewport" content="width=device-width,initial-scale=1.0"/>
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}"/>
<link rel="canonical" href="{canonical}"/>
{hreflang_tags}
<meta property="og:type" content="article"/>
<meta property="og:title" content="{e(title)}"/>
<meta property="og:description" content="{e(desc)}"/>
<meta property="og:url" content="{canonical}"/>
<style>{CSS}</style>
{FONTS}
<script type="application/ld+json">{breadcrumb}</script>
<script type="application/ld+json">{itemlist}</script>
<script type="application/ld+json">{faq_schema}</script>
</head>
<body>
<nav style="display:flex;align-items:center;justify-content:space-between;padding:16px 20px;max-width:900px;margin:0 auto">
 <a href="{gen["home_url"]}" style="text-decoration:none;font-family:'Playfair Display',serif;font-size:20px;font-weight:700;color:#1a2332">Best<em style="color:#d4a853;font-style:italic">Date</em>Weather</a>
 <div style="display:flex;align-items:center;gap:12px">
  <button class="nav-share" onclick="shareThis()" aria-label="{gen["share_label"]}" style="background:none;border:1.5px solid #e8e0d0;border-radius:8px;padding:8px 10px;cursor:pointer;align-items:center;color:#5a6c7d"><svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><path d="M8.59 13.51l6.83 3.98M15.41 6.51l-6.82 3.98"/></svg></button>
  <a href="{gen["home_url"]}" style="display:inline-block;background:#d4a853;color:white;font-size:12px;font-weight:700;padding:10px 20px;border-radius:8px;text-decoration:none">{gen["try_app_label"]}</a>
 </div>
</nav>
<header class="pillar-hero">
<div class="hero-eyebrow">{pil["hero_eyebrow_prefix"]}{YEAR}</div>
<h1 class="hero-title">{h1}</h1>
<p class="hero-sub">{hero_sub}</p>
<div class="hero-stats">
<div class="hstat"><span class="hstat-val" id="stat-score">{top['score']:.1f}</span><span class="hstat-lbl">{pil["score_n1"]}</span></div>
<div class="hstat"><span class="hstat-val" id="stat-count">{TOP_N}</span><span class="hstat-lbl">{pil["top_n_label"]}</span></div>
<div class="hstat"><span class="hstat-val" id="stat-temp">{avg_temp:.0f}{ft_unit()}</span><span class="hstat-lbl">{pil["top10_avg"]}</span></div>
</div>
</header>
<main class="page">
<div class="filter-panel"><div class="filter-row"><span class="filter-label">{fp_period}</span><div class="filter-btns">{month_nav}</div></div><div class="filter-row"><span class="filter-label">{fp_region}</span><div class="filter-btns" id="reg-tabs">{region_tabs_inner}</div></div><div class="filter-row"><span class="filter-label">{fp_type}</span><div class="filter-btns" id="mode-tabs">{mode_tabs_inner}</div></div></div><div class="section"><div class="eyebrow">{sec_eyebrow}</div><h2 class="sec-title">{sec_title}</h2><p class="sec-intro">{sec_intro}</p>
<p id="rt-msg" style="display:none;color:var(--slate);font-size:14px;padding:16px 0"></p>
<div style="overflow-x:auto"><table class="rt" aria-label="Classement"><thead id="rt-head"><tr>{"".join(f"<th>{c}</th>" for c in loc['pilier']['th'])}</tr></thead><tbody id="rt-body">{table_body}</tbody></table></div>
</div>
<div class="cta-box"><a href="{cta_href}">{cta_text} →</a></div>
{related}
</main>
{footer}
{rank_js}
<script src="{gen['asset_prefix']}js/share.js" defer></script>
</body></html>"""

    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(page_html)

    return filename, canonical, hreflang_fr, hreflang_en, _all_hreflang


# ── Sitemap Update ────────────────────────────────────────────────────────────



def get_annual_pool(climate, dests, pool_size=80, ski_boost=20):
    """Annual pool: avg score/beach/ski over 12 months, for JS tab switching."""
    SKI_DUPES = {'val-disere', 'sierra-nevada', 'queenstown-ski'}
    all_entries = []
    for slug, dest in dests.items():
        if slug in SKI_DUPES:
            continue
        if slug not in climate or len(climate[slug]) < 12:
            continue
        months = climate[slug]
        avg_score = sum(float(months[m]['score']) for m in range(1,13)) / 12
        avg_beach = None
        beach_vals = [float(months[m]['beach_score']) for m in range(1,13)
                      if months[m].get('beach_score') not in (None, '', '0', 0)]
        if beach_vals and dest.get('coastal','False') == 'True':
            avg_beach = sum(beach_vals) / len(beach_vals)
        # ski: average of ski_score computed from monthly data
        ski_vals = [compute_ski_score(float(months[m]['tmax']),
                                      float(months[m]['rain_pct']),
                                      float(months[m]['sun_h']))
                    for m in range(1,13)]
        # Use best winter month ski score (Dec/Jan/Feb average) — more meaningful
        ski_winter = sum(compute_ski_score(float(months[m]['tmax']),
                                           float(months[m]['rain_pct']),
                                           float(months[m]['sun_h']))
                         for m in [12,1,2]) / 3
        best_m = max(range(1,13), key=lambda m: float(months[m]['score']))
        m_data = months[best_m]
        all_entries.append({
            'slug_fr':    slug,
            'slug_en':    dest.get('slug_en', slug),
            'slug_es':    dest.get('slug_es', dest.get('slug_en', slug)),
            'slug_de':    dest.get('slug_de', dest.get('slug_en', slug)),
            'nom_bare':   dest.get('nom_bare', slug),
            'nom_en':     dest.get('nom_en', dest.get('nom_bare', slug)),
            'nom_es':     dest.get('nom_es', dest.get('nom_bare', '')),
            'nom_de':     dest.get('nom_de', dest.get('nom_en', '')),
            'pays':       dest.get('pays', ''),
            'pays_en':    dest.get('country_en', dest.get('pays', '')),
            'pays_es':    dest.get('country_es', dest.get('pays', '')),
            'pays_de':    dest.get('country_de', dest.get('pays', '')),
            'flag':       dest.get('flag', ''),
            'score':      avg_score,
            'beach_score': avg_beach,
            'ski_score':  ski_winter,
            'is_mountain': dest.get('mountain', 'False') == 'True',
            'is_coastal':  dest.get('coastal',  'False') == 'True',
            'tmin':       float(m_data['tmin']),
            'tmax':       float(m_data['tmax']),
            'rain_pct':   float(m_data['rain_pct']),
            'sun_h':      float(m_data['sun_h']),
            'dest':       dest,
            'slug':       slug,
        })

    # General pool: country-dedup by general score (same as classement mondial)
    general = sorted(all_entries, key=lambda x: (-x['score'], x['nom_bare']))
    ranked = {e['slug_fr'] for e in general}
    remove = {p for p, ch in REGION_CHILDREN.items() if p in ranked and ranked & ch}
    general = [e for e in general if e['slug_fr'] not in remove]
    # Inline dedup: remove country-slug when a city from the same country is also ranked
    countries_with_cities = {e['pays'] for e in general if e['slug_fr'] not in COUNTRY_SLUGS}
    general = [e for e in general
               if e['slug_fr'] not in COUNTRY_SLUGS or e['pays'] not in countries_with_cities]
    general = general[:pool_size]
    general_slugs = {e['slug_fr'] for e in general}

    # Ski boost
    ski_candidates = [e for e in all_entries if e['is_mountain'] and e['slug_fr'] not in general_slugs]
    ski_candidates.sort(key=lambda x: (-x['ski_score'], x['nom_bare']))
    ski_injected = ski_candidates[:ski_boost]

    # Beach boost
    all_slugs = {e['slug_fr'] for e in general + ski_injected}
    countries_in_pool = {e['pays'] for e in general + ski_injected}
    beach_candidates = [e for e in all_entries
                        if e.get('beach_score') is not None
                        and e.get('is_coastal', False)
                        and (e['beach_score'] or 0) >= 3.5
                        and e['slug_fr'] not in all_slugs
                        and not (e['slug_fr'] in COUNTRY_SLUGS and e['pays'] in countries_in_pool)]
    beach_candidates.sort(key=lambda x: (-(x['beach_score'] or 0), x['nom_bare']))
    seen_bc: dict = {}
    beach_injected = []
    for e in beach_candidates:
        if e['pays'] not in seen_bc:
            seen_bc[e['pays']] = True
            beach_injected.append(e)
    beach_injected = beach_injected[:40]

    return general + ski_injected + beach_injected

def get_annual_rankings(climate, dests, pool_size=80):
    """Return top destinations ranked by mean annual score — same logic as classement mondial."""
    raw = []
    for slug, dest in dests.items():
        if slug not in climate: continue
        months = climate[slug]
        if len(months) < 12: continue
        avg   = sum(float(months[m]['score']) for m in range(1, 13)) / 12
        best_m = max(range(1, 13), key=lambda m: float(months[m]['score']))
        m_data = months[best_m]
        raw.append({
            'slug':      slug,
            'slug_fr':   slug,
            'slug_en':   dest.get('slug_en', slug),
            'slug_es':   dest.get('slug_es', dest.get('slug_en', slug)),
            'slug_de':   dest.get('slug_de', dest.get('slug_en', slug)),
            'nom_bare':  dest.get('nom_bare', slug),
            'nom_en':    dest.get('nom_en', dest.get('nom_bare', slug)),
            'nom_es':    dest.get('nom_es', dest.get('nom_bare', slug)),
            'nom_de':    dest.get('nom_de', dest.get('nom_en', dest.get('nom_bare', slug))),
            'pays':      dest.get('pays', ''),
            'pays_en':   dest.get('country_en', dest.get('pays', '')),
            'pays_es':   dest.get('country_es', dest.get('pays', '')),
            'pays_de':   dest.get('country_de', dest.get('pays', '')),
            'flag':      dest.get('flag', ''),
            'score':     avg,
            'best_month': best_m,
            'tmax':      float(m_data['tmax']),
            'tmin':      float(m_data['tmin']),
            'rain_pct':  float(m_data['rain_pct']),
            'sun_h':     float(m_data['sun_h']),
            'dest':      dest,
        })
    raw.sort(key=lambda x: (-x['score'], x['nom_bare']))
    # Same dedup as classement mondial (dedup_country from generate_classements)
    deduped = dedup_country(raw, dests)
    return deduped[:pool_size]


def generate_annual_page(lang, dests, climate):
    """Generate the all-year ranking page for a given language."""
    loc   = load_locale(lang)
    gen   = loc['gen']
    pil   = loc['pilier']
    months_labels = loc['months']
    imperial = loc['meta'].get('imperial', False)
    def ft(c): return f"{c_to_f(c):.0f}°F" if imperial else f"{c:.0f}°C"
    def ft_unit(): return '°F' if imperial else '°C'

    entries = get_annual_rankings(climate, dests)
    if not entries:
        return None

    top     = entries[0]
    avg_score  = sum(x['score'] for x in entries[:10]) / 10
    avg_temp_raw = sum(x['tmax'] for x in entries[:10]) / 10
    avg_temp = c_to_f(avg_temp_raw) if imperial else avg_temp_raw

    src_sub  = loc['meta']['subdir']
    filename = pil.get('all_year_url', 'meilleures-destinations-meteo.html')
    filepath = ROOT / filename if src_sub == '' else ROOT / src_sub / filename
    canonical = (f'https://bestdateweather.com/{filename}'
                 if src_sub == '' else
                 f'https://bestdateweather.com/{src_sub}/{filename}')

    # Slug key
    is_fr = (lang == 'fr')
    is_es = (lang == 'es')
    is_de = (lang == 'de')
    slug_key = 'slug_fr' if is_fr else ('slug_es' if is_es else ('slug_de' if is_de else 'slug_en'))
    name_key = 'nom_bare' if is_fr else ('nom_es' if is_es else ('nom_de' if is_de else 'nom_en'))
    pays_key = 'pays' if is_fr else ('pays_es' if is_es else ('pays_de' if is_de else 'pays_en'))
    annual_href_tpl = gen['annual_href_tpl']

    # Table
    rows = ''
    for i, e in enumerate(entries[:TOP_N], 1):
        medal = ['🥇','🥈','🥉'][i-1] if i <= 3 else str(i)
        slug  = e[slug_key]
        name  = e[name_key]
        pays  = e[pays_key] or e['pays']
        flag  = e['flag']
        href  = annual_href_tpl.format(slug=slug)
        temp_str = f"{ft(e['tmin'])}–{ft(e['tmax'])}"
        flag_img = (f'<img src="{gen["asset_prefix"]}flags/{flag}.png" '
                    f'width="16" height="12" alt="{flag}" '
                    f'style="margin-right:4px;vertical-align:middle;border-radius:1px">'
                    if flag else '')
        best_m_label = months_labels[e['best_month'] - 1]
        rows += (f'<tr>'
                 f'<td class="rank">{medal}</td>'
                 f'<td><a href="{href}" class="dest-link">'
                 f'{flag_img}{name}</a>'
                 f'<span style="display:block;font-size:11px;color:var(--slate)">{pays}</span></td>'
                 f'<td class="sc">{e["score"]:.1f}/10</td>'
                 f'<td>{temp_str}</td>'
                 f'<td>{e["rain_pct"]:.0f}%</td>'
                 f'<td>{e["sun_h"]:.1f}h</td>'
                 f'</tr>\n')

    h1  = pil.get('all_year_h1', 'Best weather destinations')
    sub = pil.get('all_year_sub', '')
    eyebrow = pil.get('all_year_eyebrow', '')
    sec_title = pil.get('all_year_sec', '')
    sec_intro = pil.get('all_year_intro', '')
    th_list   = pil['th']
    month_nav = build_month_nav(-1, loc, is_annual=True)
    region_tabs = build_region_tabs(lang)
    footer    = footer_ranking_html(lang, [])

    # ── Mode tabs (Météo / Plage / Ski) ───────────────────────────────────────
    if lang == 'fr':
        tab_meteo = '☀️ Météo générale'; tab_beach = '🏖️ Plage'; tab_ski = '⛷️ Ski'
        th_score_gen = 'Score annuel'; th_score_beach = 'Score plage'; th_score_ski = 'Score ski'
        no_beach_msg = 'Aucune destination balnéaire dans ce classement.'
        no_ski_msg   = 'Aucune station de ski dans ce classement.'
        no_meteo_msg = 'Aucune destination dans cette région.'
    elif lang == 'es':
        tab_meteo = '☀️ Clima general'; tab_beach = '🏖️ Playa'; tab_ski = '⛷️ Esquí'
        th_score_gen = 'Puntuación'; th_score_beach = 'Puntuación playa'; th_score_ski = 'Puntuación esquí'
        no_beach_msg = 'Sin destinos de playa en este ranking.'
        no_ski_msg   = 'Sin estaciones de esquí en este ranking.'
        no_meteo_msg = 'No hay destinos en esta región.'
    elif lang == 'de':
        tab_meteo = '☀️ Allgemeines Wetter'; tab_beach = '🏖️ Strand'; tab_ski = '⛷️ Ski'
        th_score_gen = 'Jahreswertung'; th_score_beach = 'Strandwertung'; th_score_ski = 'Skiwertung'
        no_beach_msg = 'Keine Strandziele in diesem Ranking.'
        no_ski_msg   = 'Keine Skigebiete in diesem Ranking.'
        no_meteo_msg = 'Keine Ziele in dieser Region.'
    else:  # en / en-us
        tab_meteo = '☀️ General weather'; tab_beach = '🏖️ Beach'; tab_ski = '⛷️ Ski'
        th_score_gen = 'Annual score'; th_score_beach = 'Beach score'; th_score_ski = 'Ski score'
        no_beach_msg = 'No beach destinations in this ranking.'
        no_ski_msg   = 'No ski resorts in this ranking.'
        no_meteo_msg = 'No destinations in this region.'

    # Build annual pool
    annual_pool = get_annual_pool(climate, dests)
    flag_prefix = gen['asset_prefix']
    annual_href_tpl2 = gen['annual_href_tpl']

    def _pool_slug(e):
        if is_fr: return e['slug_fr']
        if is_es: return e.get('slug_es') or e['slug_en']
        if is_de: return e.get('slug_de') or e['slug_en']
        return e['slug_en']

    pool_json = json.dumps([{
        'n':   e[name_key] if e.get(name_key) else e['nom_bare'],
        'p':   e[pays_key] if e.get(pays_key) else e['pays'],
        'f':   e['flag'],
        'h':   annual_href_tpl2.format(slug=_pool_slug(e)),
        's':   round(e['score'], 1),
        'b':   round(e['beach_score'], 1) if e.get('beach_score') is not None else None,
        'br':  round(e['beach_score'], 4) if e.get('beach_score') is not None else None,
        'k':   round(e['ski_score'], 1),
        'm':   1 if e['is_mountain'] else 0,
        'ap':  f'{flag_prefix}flags/{e["flag"]}.png',
        'r':   round(e['rain_pct'], 0),
        'sun': round(e['sun_h'], 1),
        'tmin': round(e['tmin'], 0),
        'tmax': round(e['tmax'], 0),
        'reg': _reg(e['pays'], e.get('slug_fr', e.get('slug',''))),
        'xeu': 1 if e.get('slug', e.get('slug_fr','')) in NON_EUROPE_SLUGS else 0,
    } for e in annual_pool], ensure_ascii=False)

    mode_tabs_inner = (
        f'<button class="mode-tab active" data-mode="meteo">{tab_meteo}</button>'
        f'<button class="mode-tab" data-mode="beach">{tab_beach}</button>'
        f'<button class="mode-tab" data-mode="ski">{tab_ski}</button>'
    )
    region_tabs_inner = build_region_tabs(lang)
    fp_period = loc.get('fp_period', 'PÉRIODE')
    fp_region = loc.get('fp_region', 'RÉGION')
    fp_type   = loc.get('fp_type',   'TYPE')

    def _e(s): return s.replace('"', '&quot;')
    rank_js = (
        '<script>(function(){'+
        f'var POOL={pool_json};'+
        'var TOP=25;var CUR_REG="all";'+
        f'var TH_GEN="{_e(th_score_gen)}",TH_BEACH="{_e(th_score_beach)}",TH_SKI="{_e(th_score_ski)}";'+
        f'var NO_BEACH="{_e(no_beach_msg)}",NO_SKI="{_e(no_ski_msg)}",NO_METEO="{_e(no_meteo_msg)}";'+
        'function sc(s){return s>=8.6?"#1a7a4a":s>=7.6?"#2d9e60":s>=6.3?"#84cc16":s>=5?"#f59e0b":s>=3.5?"#f97316":"#ef4444";}'+
        'function ri(i){return i===1?"🥇":i===2?"🥈":i===3?"🥉":String(i);}'+
        'function render(mode){'+
        'var tb=document.getElementById("rt-body");'+
        'var th=document.getElementById("rt-head");'+
        'var msg=document.getElementById("rt-msg");'+
        'if(!tb)return;'+
        'var key=mode==="beach"?"b":mode==="ski"?"k":"s";'+
        'var list=POOL.filter(function(d){var rOk=CUR_REG==="all"||(d.reg===CUR_REG&&!(CUR_REG==="eu"&&d.xeu));var mOk=mode==="beach"?(d.b!=null&&d.b>=3.5):mode==="ski"?(d.m===1&&d.k>=4&&d.tmax<=25):(d.m!==1);return rOk&&mOk;});'+
        'list.sort(function(a,b){var d=(b[key]||0)-(a[key]||0);return d!==0?d:(key==="b"?(b.br||0)-(a.br||0):0);});'+
        'list=list.slice(0,TOP);'+
        'if(list.length===0){tb.innerHTML="";msg.textContent=mode==="beach"?NO_BEACH:(mode==="ski"?NO_SKI:NO_METEO);msg.style.display="block";return;}'+
        'msg.style.display="none";'+
        'var label=mode==="beach"?TH_BEACH:mode==="ski"?TH_SKI:TH_GEN;'+
        'th.innerHTML="<tr><th>#</th><th>Destination</th><th>"+label+"</th><th>Temp.</th><th>Pluie</th><th>Soleil/j</th></tr>";'+
        'var html="";'+
        'list.forEach(function(d,i){'+
        'var v=d[key]!=null?d[key]:d.s;'+
        'var tmp=d.tmin!=null?(d.tmin.toFixed(0)+"°–"+d.tmax.toFixed(0)+"°"):"—";'+
        'html+="<tr>"'+
        '+"<td class=\'rank\'>"+ri(i+1)+"</td>"'+
        '+"<td><img src=\'"+d.ap+"\' width=\'16\' height=\'12\' alt=\'\'  style=\'vertical-align:middle;margin-right:6px;border-radius:1px\'><a href=\'"+d.h+"\' class=\'dest-link\'>"+d.n+"</a>"+(d.p?"<span style=\'display:block;font-size:11px;color:#5a6c7d\'>"+d.p+"</span>":"")+"</td>"'+
        '+"<td class=\'sc\' style=\'color:"+sc(v)+"\'>"+v.toFixed(1)+"<span>/10</span></td>"'+
        '+"<td>"+tmp+"</td>"'+
        '+"<td>"+(d.r!=null?d.r.toFixed(0)+"%":"—")+"</td>"'+
        '+"<td>"+(d.sun!=null?d.sun.toFixed(1)+"h":"—")+"</td>"'+
        '+"</tr>";'+
        '});'+
        'tb.innerHTML=html;'+
        'var _s1=document.getElementById("stat-score");'+
        'if(_s1&&list.length){'+
        'var _top10=list.slice(0,10);'+
        '_s1.textContent=list[0][key].toFixed(1);'+
        'document.getElementById("stat-count").textContent=list.length;'+
        'var _avgT=_top10.reduce(function(a,d){return a+(d.tmax||0);},0)/_top10.length;'+
        'var _s3=document.getElementById("stat-temp");if(_s3)_s3.textContent=Math.round(_avgT)+"°";'+
        '}'+
        '}'+
        'document.getElementById("mode-tabs").addEventListener("click",function(ev){'+
        'var btn=ev.target.closest(".mode-tab");'+
        'if(!btn)return;'+
        'document.querySelectorAll(".mode-tab").forEach(function(b){b.classList.remove("active");});'+
        'btn.classList.add("active");'+
        'render(btn.dataset.mode);'+
        '});'+
        'document.getElementById("reg-tabs").addEventListener("click",function(ev){'+
        'var btn=ev.target.closest(".reg-tab");'+
        'if(!btn)return;'+
        'document.querySelectorAll(".reg-tab").forEach(function(b){b.classList.remove("active");});'+
        'btn.classList.add("active");'+
        'CUR_REG=btn.dataset.reg;'+
        'var activeMode=document.querySelector(".mode-tab.active");'+
        'render(activeMode?activeMode.dataset.mode:"meteo");'+
        '});'+
        'var _p=new URLSearchParams(location.search);var _initMode=_p.get("mode")||"meteo";var _initReg=_p.get("reg")||"all";CUR_REG=_initReg;if(_initReg!=="all"){document.querySelectorAll(".reg-tab").forEach(function(b){b.classList.toggle("active",b.dataset.reg===_initReg);});}if(_initMode!=="meteo"){document.querySelectorAll(".mode-tab").forEach(function(b){b.classList.toggle("active",b.dataset.mode===_initMode);});}render(_initMode);document.querySelectorAll(".month-nav a").forEach(function(a){a.addEventListener("click",function(ev){var am=document.querySelector(".mode-tab.active");var ar=document.querySelector(".reg-tab.active");var m=am?am.dataset.mode:"meteo";var r=ar?ar.dataset.reg:"all";if(m==="meteo"&&r==="all")return;ev.preventDefault();var url=this.href.split("?")[0];var q=[];if(m!=="meteo")q.push("mode="+m);if(r!=="all")q.push("reg="+r);location.href=url+(q.length?"?"+q.join("&"):"");});});'+
        '})();</script>'
    )

    # hreflang
    hreflang_tags = ''
    for hl_lang in PILIER_LANGS:
        hl_loc  = load_locale(hl_lang)
        hl_sub  = hl_loc['meta']['subdir']
        hl_file = hl_loc['pilier'].get('all_year_url', filename)
        hl_url  = (f'https://bestdateweather.com/{hl_file}'
                   if hl_sub == '' else
                   f'https://bestdateweather.com/{hl_sub}/{hl_file}')
        hl_code = hl_loc['meta'].get('hreflang', hl_lang)
        hreflang_tags += f'<link rel="alternate" hreflang="{hl_code}" href="{hl_url}">\n'

    page_html = f"""<!DOCTYPE html>
<html lang="{loc['meta']['html_lang']}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{h1} — BestDateWeather</title>
<meta name="description" content="{sub}">
<link rel="canonical" href="{canonical}">
{hreflang_tags}<style>{CSS}.pillar-hero{{padding-bottom:64px}}</style>
<link rel="preconnect" href="https://fonts.googleapis.com"/><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin/><link rel="preload" as="style" href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;1,700&family=DM+Sans:wght@400;500;700&display=swap" onload="this.onload=null;this.rel='stylesheet'"/><noscript><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;1,700&family=DM+Sans:wght@400;500;700&display=swap"/></noscript>
</head>
<body>
<nav style="display:flex;align-items:center;justify-content:space-between;padding:16px 20px;max-width:900px;margin:0 auto">
 <a href="{gen['home_url']}" style="text-decoration:none;font-family:'Playfair Display',serif;font-size:20px;font-weight:700;color:#1a2332">Best<em style="color:#d4a853;font-style:italic">Date</em>Weather</a>
 <div style="display:flex;align-items:center;gap:12px">
  <button class="nav-share" onclick="shareThis()" aria-label="{gen['share_label']}" style="background:none;border:1.5px solid #e8e0d0;border-radius:8px;padding:8px 10px;cursor:pointer;align-items:center;color:#5a6c7d"><svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><path d="M8.59 13.51l6.83 3.98M15.41 6.51l-6.82 3.98"/></svg></button>
  <a href="{gen['home_url']}" style="display:inline-block;background:#d4a853;color:white;font-size:12px;font-weight:700;padding:10px 20px;border-radius:8px;text-decoration:none">{gen['try_app_label']}</a>
 </div>
</nav>
<header class="pillar-hero">
<div class="hero-eyebrow">{pil["hero_eyebrow_prefix"]}{YEAR}</div>
<h1 class="hero-title">{h1}</h1>
<p class="hero-sub">{sub}</p>
<div class="hero-stats">
<div class="hstat"><span class="hstat-val" id="stat-score">{top['score']:.1f}</span><span class="hstat-lbl">{pil["score_n1"]}</span></div>
<div class="hstat"><span class="hstat-val" id="stat-count">{TOP_N}</span><span class="hstat-lbl">{pil["top_n_label"]}</span></div>
<div class="hstat"><span class="hstat-val" id="stat-temp">{avg_temp:.0f}{ft_unit()}</span><span class="hstat-lbl">{pil["top10_avg"]}</span></div>
</div>
</header>
<main class="page">
<div class="filter-panel"><div class="filter-row"><span class="filter-label">{fp_period}</span><div class="filter-btns">{month_nav}</div></div><div class="filter-row"><span class="filter-label">{fp_region}</span><div class="filter-btns" id="reg-tabs">{region_tabs_inner}</div></div><div class="filter-row"><span class="filter-label">{fp_type}</span><div class="filter-btns" id="mode-tabs">{mode_tabs_inner}</div></div></div>
<div class="section">
<p id="rt-msg" style="display:none;color:var(--slate);font-size:14px;padding:16px 0"></p>
<div style="overflow-x:auto"><table class="rt" aria-label="{sec_title}">
<thead id="rt-head"><tr>{"".join(f"<th>{c}</th>" for c in th_list)}</tr></thead>
<tbody id="rt-body">{rows}</tbody>
</table></div>
</div>
</main>
{footer}
{rank_js}
<script src="{gen['asset_prefix']}js/share.js" defer></script>
</body></html>"""

    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(page_html)

    return filename, canonical


def update_sitemaps(fr_pages, en_pages):
    """Append new pillar pages to existing sitemaps if not already present."""
    for sitemap_file, pages in [('sitemap-fr.xml', fr_pages), ('sitemap-en.xml', en_pages)]:
        path = ROOT / sitemap_file
        if not path.exists():
            print(f"  ⚠️  {sitemap_file} not found, skipping")
            continue

        content = path.read_text(encoding='utf-8')
        added = 0
        updated = 0
        for page in pages:
            entry = f"""  <url>
    <loc>{page['canonical']}</loc>
    <lastmod>{TODAY}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>"""
            if page['canonical'] in content:
                # Replace existing entry if it lacks hreflang
                import re
                pattern = (
                    r'<url>\s*'
                    + re.escape(f"<loc>{page['canonical']}</loc>") + r'\s*'
                    + r'<lastmod>[^<]*</lastmod>\s*'
                    + r'<changefreq>[^<]*</changefreq>\s*'
                    + r'<priority>[^<]*</priority>\s*'
                    + r'</url>'
                )
                if re.search(pattern, content):
                    content = re.sub(pattern, entry, content)
                    updated += 1
                continue
            content = content.replace('</urlset>', entry + '\n</urlset>')
            added += 1
        path.write_text(content, encoding='utf-8')
        if added:
            print(f"  📍 {sitemap_file}: +{added} URLs")


# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    print("generate_piliers.py — seasonal pillar pages")
    dests = load_destinations()
    climate = load_climate()
    print(f"📦 {len(dests)} destinations, {len(climate)} climate entries\n")

    pages_by_lang = {lang: [] for lang in PILIER_LANGS}

    for lang in PILIER_LANGS:
        lang_loc = load_locale(lang)
        subdir = lang_loc['meta']['subdir']
        prefix = f"{subdir}/" if subdir else ""
        for mi in range(12):
            result = generate_page(mi, lang, dests, climate)
            if result:
                filename, canonical, hreflang_fr, hreflang_en, all_hreflang = result
                pages_by_lang[lang].append({
                    'canonical': canonical,
                    'hreflang_fr': hreflang_fr,
                    'hreflang_en': hreflang_en,
                })
                print(f"  ✅ {prefix}{filename}")

    counts = " + ".join(f"{len(pages_by_lang[l])} {l.upper()}" for l in PILIER_LANGS)
    print(f"\n📄 {counts} pillar pages generated")

    # Generate annual pages
    print("\n📅 Generating all-year pages...")
    for lang in PILIER_LANGS:
        result = generate_annual_page(lang, dests, climate)
        if result:
            filename, canonical = result
            lang_loc = load_locale(lang)
            subdir = lang_loc['meta']['subdir']
            prefix = f"{subdir}/" if subdir else ""
            print(f"  ✅ {prefix}{filename}")

    fr_pages = pages_by_lang.get('fr', [])
    en_pages = pages_by_lang.get('en', [])
    update_sitemaps(fr_pages, en_pages)
    print("\n✅ Done")
