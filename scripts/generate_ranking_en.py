#!/usr/bin/env python3
"""
Generate EN ranking pages from FR ranking pages.
Translates content, converts links, adjusts paths.

Usage: python3 scripts/generate_ranking_en.py
"""

import csv
import re
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# ── Slug mapping ──────────────────────────────────────────────────────────
def load_slug_map():
    slug_map = {}
    name_map = {}  # slug_fr → nom_en
    with open(ROOT / 'data/destinations.csv', encoding='utf-8-sig') as f:
        for r in csv.DictReader(f):
            sfr = r['slug_fr'].strip()
            slug_map[sfr] = r['slug_en'].strip()
            name_map[sfr] = r.get('nom_en', r.get('nom_bare', sfr)).strip()
    return slug_map, name_map

# ── Page mapping ──────────────────────────────────────────────────────────
PAGES = {
    'classement-destinations-meteo-2026.html':
        'en/best-destinations-weather-ranking-2026.html',
    'classement-destinations-europe-meteo-2026.html':
        'en/best-europe-weather-ranking-2026.html',
    'classement-destinations-meteo-ete-2026.html':
        'en/best-destinations-summer-weather-2026.html',
    'classement-destinations-meteo-hiver-2026.html':
        'en/best-destinations-winter-weather-2026.html',
    'classement-destinations-meteo-nomades-2026.html':
        'en/best-destinations-digital-nomads-weather-2026.html',
}

# ── FR → EN text replacements (order matters for overlapping patterns) ────
TEXT_MAP = [
    # HTML attributes — only the html tag, NOT hreflang
    ('<html lang="fr">', '<html lang="en">'),

    # Navigation
    ("Tester l'application", "Try the app"),
    ('Partager', 'Share'),

    # Hero
    ('Étude climatique indépendante · 2026', 'Independent climate study · 2026'),

    # Global page — classement mondial
    ('Classement 2026 des meilleures destinations selon 10 ans de données météo',
     '2026 Best Weather Destinations — 10-Year Climate Data Ranking'),
    ('512 destinations classées sur 10 ans de données météo. Top mondial, plus ensoleillées, moins pluvieuses.',
     '512 destinations ranked on 10 years of weather data. Global top, sunniest, driest.'),
    ('Classement 2026 des meilleures<br/><em>destinations météo</em>',
     '2026 Best<br/><em>Weather Destinations</em>'),
    ('512 destinations analysées sur 10 ans. Dakar en tête avec 9.1/10.',
     '512 destinations analyzed over 10 years. Dakar leads with 9.1/10.'),
    ('Top 512 meilleures destinations météo 2026',
     'Top 512 best weather destinations 2026'),

    # Europe page
    ('Classement météo Europe 2026 — Top destinations européennes',
     'Europe Weather Ranking 2026 — Top European Destinations'),
    ('Les meilleures destinations européennes classées sur 10 ans de données météo.',
     'The best European destinations ranked on 10 years of weather data.'),
    ('Top destinations<br/><em>européennes météo 2026</em>',
     'Top European<br/><em>Weather Destinations 2026</em>'),
    ('destinations européennes analysées sur 10 ans.',
     'European destinations analyzed over 10 years.'),
    ('Top Europe météo 2026', 'Top Europe Weather 2026'),
    ('Comparatif européen', 'European comparison'),
    ('Europe domine', 'Europe leads'),

    # Summer page
    ('Meilleures destinations été 2026 — Classement météo Juin–Août',
     'Best Summer Destinations 2026 — Weather Ranking June–August'),
    ('Top 40 destinations été classées sur les scores météo de Juin à Août.',
     'Top 40 summer destinations ranked by June–August weather scores.'),
    ('Meilleures destinations<br/><em>été 2026</em>',
     'Best<br/><em>Summer Destinations 2026</em>'),
    ('destinations classées sur leur score été (Juin–Août).',
     'destinations ranked by summer score (June–August).'),
    ('Meilleures destinations été', 'Best summer destinations'),

    # Winter page
    ('Meilleures destinations hiver 2026 — Soleil et chaleur garanti',
     'Best Winter Sun Destinations 2026 — Guaranteed Warmth'),
    ('Top 40 destinations soleil en hiver classées sur les scores météo Déc–Fév.',
     'Top 40 winter sun destinations ranked by Dec–Feb weather scores.'),
    ('Meilleures destinations<br/><em>soleil hiver 2026</em>',
     'Best<br/><em>Winter Sun Destinations 2026</em>'),
    ('destinations classées sur leur score hiver (Déc–Jan–Fév).',
     'destinations ranked by winter score (Dec–Jan–Feb).'),
    ('Meilleures destinations hiver', 'Best winter destinations'),
    ('Destinations soleil hiver', 'Winter sun destinations'),

    # Nomad page
    ('Meilleures destinations digital nomads 2026 — Météo et régularité climatique',
     'Best Digital Nomad Destinations 2026 — Weather Consistency Ranking'),
    ('Top 40 destinations pour nomades classées sur la régularité météo annuelle.',
     'Top 40 destinations for digital nomads ranked by year-round weather consistency.'),
    ('Meilleures destinations<br/><em>digital nomads 2026</em>',
     'Best Destinations for<br/><em>Digital Nomads 2026</em>'),
    ('destinations classées sur la régularité climatique.',
     'destinations ranked by climate consistency.'),
    ('Meilleures destinations nomades', 'Best nomad destinations'),
    ('Régularité &amp; confort', 'Consistency &amp; comfort'),
    ('Régularité & confort', 'Consistency & comfort'),

    # Section headers & labels
    ('Classement mondial', 'Global ranking'),
    ('Classement européen', 'European ranking'),
    ('Classement été', 'Summer ranking'),
    ('Classement hiver', 'Winter ranking'),
    ('Classement nomades', 'Nomad ranking'),
    ('Points clés', 'Key insights'),
    ('Ensoleillement', 'Sunshine'),
    ('Précipitations', 'Precipitation'),
    ('Régularité climatique', 'Climate consistency'),
    ('Score climatique annuel', 'Annual climate score'),
    ('Score été', 'Summer score'),
    ('Score hiver', 'Winter score'),
    ('Score annuel', 'Annual score'),
    ('Meilleur mois', 'Best month'),
    ('Soleil/an', 'Sun/year'),
    ('Pluie moy.', 'Avg rain'),
    ('Rang', 'Rank'),
    ('Destination', 'Destination'),

    # Key insights
    ('N°1 mondial', 'World #1'),
    ('N°1 Europe', 'Europe #1'),
    ('N°1 été', 'Summer #1'),
    ('N°1 hiver', 'Winter #1'),
    ('N°1 nomades', 'Nomad #1'),
    ('Plus ensoleillé', 'Sunniest'),
    ('Plus sec', 'Driest'),
    ('Plus régulier', 'Most consistent'),
    ('Plus stable', 'Most stable'),
    ('Europe', 'Europe'),
    ('annuel', 'annual'),

    # Top sections
    ('Top 20 mondial', 'Top 20 global'),
    ('Top 20 européen', 'Top 20 European'),
    ('Top 20 été', 'Top 20 summer'),
    ('Top 20 hiver', 'Top 20 winter'),
    ('Top 20 nomades', 'Top 20 nomad'),
    ('les plus ensoleillées', 'sunniest'),
    ('les moins pluvieuses', 'driest'),
    ('les plus régulières', 'most consistent'),
    ('Heures de soleil cumulées sur l\'année.', 'Cumulative sunshine hours per year.'),
    ("Heures de soleil cumulées sur l'année.", 'Cumulative sunshine hours per year.'),
    ("Pourcentage moyen de jours de pluie sur l'année.", 'Average percentage of rainy days per year.'),
    ("Pourcentage moyen de jours de pluie sur l&#x27;année.", 'Average percentage of rainy days per year.'),
    ('Score annuel = moyenne des 12 scores mensuels (0–10).', 'Annual score = average of 12 monthly scores (0–10).'),
    ('destinations analysées.', 'destinations analyzed.'),

    # Methodology
    ('Méthodologie', 'Methodology'),
    ("Scores calculés sur 10 ans d'archives Open-Meteo (ERA5).",
     'Scores computed from 10 years of Open-Meteo archives (ERA5).'),
    ("Scores calculés sur 10 ans d&#x27;archives Open-Meteo (ERA5).",
     'Scores computed from 10 years of Open-Meteo archives (ERA5).'),
    ('Chaque mois noté sur ensoleillement (40&nbsp;%), précipitations (30&nbsp;%), confort thermique (30&nbsp;%).',
     'Each month scored on sunshine (40%), precipitation (30%), thermal comfort (30%).'),
    ('Score annuel = moyenne des 12 mois.', 'Annual score = average of 12 months.'),
    ('Score été = moyenne Juin–Août.', 'Summer score = average June–August.'),
    ('Score hiver = moyenne Déc–Fév.', 'Winter score = average Dec–Feb.'),
    ('destinations analysées', 'destinations analyzed'),

    # Related pages
    ('Meilleures destinations nomades', 'Best nomad destinations'),
    ('💻 Meilleures destinations nomades', '💻 Best nomad destinations'),
    ('☀️ Meilleures destinations été', '☀️ Best summer destinations'),
    ('❄️ Meilleures destinations hiver', '❄️ Best winter destinations'),

    # Footer
    ('Données météo par Open-Meteo.com', 'Weather data by Open-Meteo.com'),
    ('Application météo', 'Weather app'),
    ('Mentions légales', 'Legal notice'),

    # Month names in content
    ('Janvier', 'January'), ('Février', 'February'), ('Mars', 'March'),
    ('Avril', 'April'), ('Mai', 'May'), ('Juin', 'June'),
    ('Juillet', 'July'), ('Août', 'August'), ('Septembre', 'September'),
    ('Octobre', 'October'), ('Novembre', 'November'), ('Décembre', 'December'),
    ('Juin–Juil–Août', 'Jun–Jul–Aug'),
    ('Déc–Jan–Fév', 'Dec–Jan–Feb'),
]

# ── FR month to EN month (lowercase, for slug matching) ──────────────────
MONTHS_FR_EN = {
    'janvier': 'january', 'fevrier': 'february', 'mars': 'march',
    'avril': 'april', 'mai': 'may', 'juin': 'june', 'juillet': 'july',
    'aout': 'august', 'septembre': 'september', 'octobre': 'october',
    'novembre': 'november', 'decembre': 'december'
}


def convert_links(html, slug_map):
    """Convert FR destination links to EN equivalents."""
    def replace_dest_link(m):
        slug_fr = m.group(1)
        slug_en = slug_map.get(slug_fr, slug_fr)
        return f'href="../en/best-time-to-visit-{slug_en}.html"'

    # Annual pages: meilleure-periode-{slug}.html → ../en/best-time-to-visit-{slug_en}.html
    # But since we're IN en/ folder, use best-time-to-visit-{slug}.html
    def replace_annual(m):
        slug_fr = m.group(1)
        slug_en = slug_map.get(slug_fr, slug_fr)
        return f'href="best-time-to-visit-{slug_en}.html"'

    html = re.sub(r'href="meilleure-periode-([^"]+)\.html"', replace_annual, html)

    # Static links
    html = html.replace('href="index.html"', 'href="../en/app.html"')
    html = html.replace('href="note_modele.html"', 'href="methodology.html"')
    html = html.replace('href="mentions-legales.html"', 'href="legal.html"')

    # Related ranking pages
    for fr_file, en_file in PAGES.items():
        en_basename = os.path.basename(en_file)
        html = html.replace(f'href="{fr_file}"', f'href="{en_basename}"')

    return html


def swap_hreflang(html, fr_file, en_file):
    """Swap canonical and hreflang so EN page points to itself as canonical."""
    fr_url = f'https://bestdateweather.com/{fr_file}'
    en_url = f'https://bestdateweather.com/{en_file}'

    # Canonical → EN
    html = html.replace(f'<link rel="canonical" href="{fr_url}"/>',
                        f'<link rel="canonical" href="{en_url}"/>')

    # hreflang already correct in FR source — just verify
    return html


def fix_asset_paths(html):
    """Adjust paths for en/ subdirectory."""
    html = html.replace('src="flags/', 'src="../flags/')
    html = html.replace('href="og-image.png"', 'href="../og-image.png"')
    html = html.replace('"https://bestdateweather.com/og-image.png"',
                        '"https://bestdateweather.com/og-image.png"')  # absolute OK
    return html


def add_en_switch(html, fr_file):
    """Replace the EN switch link in footer with FR switch."""
    # Find the English link in footer and replace with French
    en_basename = os.path.basename(PAGES[fr_file])
    html = html.replace(
        f'<a href="en/{en_basename}" style="color:rgba(255,255,255,.7)"><img src="flags/gb.png"',
        f'<a href="../{fr_file}" style="color:rgba(255,255,255,.7)"><img src="../flags/fr.png"'
    )
    # Also handle if the link text says "English"
    html = html.replace(
        f'> English</a>',
        f'> Français</a>'
    )
    return html


def process_file(fr_file, en_file, slug_map, name_map):
    """Generate EN version from FR source."""
    html = (ROOT / fr_file).read_text(encoding='utf-8')

    # 0. Load FR name → slug mapping for display name replacement
    fr_name_to_slug = {}
    with open(ROOT / 'data/destinations.csv', encoding='utf-8-sig') as f:
        for r in csv.DictReader(f):
            sfr = r['slug_fr'].strip()
            nom_fr = r.get('nom_fr', '').strip()
            if nom_fr:
                fr_name_to_slug[nom_fr] = sfr
            # Also map HTML-escaped versions
            if "'" in nom_fr:
                fr_name_to_slug[nom_fr.replace("'", "&#x27;")] = sfr

    # 1. Text translations
    for fr_text, en_text in TEXT_MAP:
        html = html.replace(fr_text, en_text)

    # 2. Convert destination links
    html = convert_links(html, slug_map)

    # 3. Replace FR destination display names with EN names in table rows
    def replace_dest_name(m):
        prefix = m.group(1)  # <a ... class="dest-link">
        fr_name = m.group(2)
        suffix = m.group(3)  # </a>
        # Find slug from FR name
        slug_fr = fr_name_to_slug.get(fr_name)
        if slug_fr and slug_fr in name_map:
            return f'{prefix}{name_map[slug_fr]}{suffix}'
        return m.group(0)

    html = re.sub(r'(class="dest-link">)([^<]+)(</a>)', replace_dest_name, html)

    # 4. Replace FR names in schema.org JSON-LD
    def replace_schema_name(m):
        fr_name = m.group(1)
        slug_fr = fr_name_to_slug.get(fr_name)
        if slug_fr and slug_fr in name_map:
            return f'"name": "{name_map[slug_fr]}"'
        return m.group(0)

    html = re.sub(r'"name":\s*"([^"]+)"', replace_schema_name, html)
    # Keep the ItemList name as translated title
    html = re.sub(r'"name": "Top \d+ best weather destinations 2026"',
                  '"name": "Top 512 best weather destinations 2026"', html, flags=re.IGNORECASE)

    # 5. Swap hreflang/canonical
    html = swap_hreflang(html, fr_file, en_file)

    # 6. Fix asset paths
    html = fix_asset_paths(html)

    # 7. Fix language switch in footer
    html = add_en_switch(html, fr_file)

    # 8. Fix schema.org URLs
    html = re.sub(
        r'"url":\s*"https://bestdateweather\.com/meilleure-periode-([^"]+)\.html"',
        lambda m: f'"url": "https://bestdateweather.com/en/best-time-to-visit-{slug_map.get(m.group(1), m.group(1))}.html"',
        html
    )

    # Write EN file
    out_path = ROOT / en_file
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html, encoding='utf-8')
    print(f'  ✓ {en_file} ({len(html)} bytes)')


def main():
    slug_map, name_map = load_slug_map()
    print(f'Generating {len(PAGES)} EN ranking pages...\n')

    for fr_file, en_file in PAGES.items():
        process_file(fr_file, en_file, slug_map, name_map)

    print(f'\n✅ Done — {len(PAGES)} EN ranking pages generated')


if __name__ == '__main__':
    main()
