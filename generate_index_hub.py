#!/usr/bin/env python3
"""Regenerate the SEO destination hub in index.html and en/app.html from destinations.csv"""
import csv, re

# Region mapping: country → (region_name, emoji, sort_order)
REGIONS = {
    # France
    'France': ('🇫🇷 France', 1),
    # Méditerranée & Europe du Sud
    'Italie': ('🌊 Méditerranée & Europe du Sud', 2),
    'Grèce': ('🌊 Méditerranée & Europe du Sud', 2),
    'Espagne': ('🌊 Méditerranée & Europe du Sud', 2),
    'Portugal': ('🌊 Méditerranée & Europe du Sud', 2),
    'Croatie': ('🌊 Méditerranée & Europe du Sud', 2),
    'Malte': ('🌊 Méditerranée & Europe du Sud', 2),
    'Monaco': ('🌊 Méditerranée & Europe du Sud', 2),
    'Monténégro': ('🌊 Méditerranée & Europe du Sud', 2),
    'Albanie': ('🌊 Méditerranée & Europe du Sud', 2),
    'Chypre': ('🌊 Méditerranée & Europe du Sud', 2),
    'Turquie': ('🌊 Méditerranée & Europe du Sud', 2),
    # Europe du Nord & Centrale
    'Pays-Bas': ('🏰 Europe du Nord & Centrale', 3),
    'Allemagne': ('🏰 Europe du Nord & Centrale', 3),
    'Royaume-Uni': ('🏰 Europe du Nord & Centrale', 3),
    'Tchéquie': ('🏰 Europe du Nord & Centrale', 3),
    'Autriche': ('🏰 Europe du Nord & Centrale', 3),
    'Belgique': ('🏰 Europe du Nord & Centrale', 3),
    'Hongrie': ('🏰 Europe du Nord & Centrale', 3),
    'Pologne': ('🏰 Europe du Nord & Centrale', 3),
    'Roumanie': ('🏰 Europe du Nord & Centrale', 3),
    'Irlande': ('🏰 Europe du Nord & Centrale', 3),
    'Islande': ('🏰 Europe du Nord & Centrale', 3),
    # Scandinavie
    'Danemark': ('❄️ Scandinavie & Baltique', 4),
    'Suède': ('❄️ Scandinavie & Baltique', 4),
    'Norvège': ('❄️ Scandinavie & Baltique', 4),
    'Finlande': ('❄️ Scandinavie & Baltique', 4),
    # Caucase & Europe de l'Est
    'Géorgie': ('🏔️ Caucase', 5),
    # Afrique & Océan Indien
    'Maroc': ('🌴 Afrique & Océan Indien', 6),
    'Tunisie': ('🌴 Afrique & Océan Indien', 6),
    'Égypte': ('🌴 Afrique & Océan Indien', 6),
    'Kenya': ('🌴 Afrique & Océan Indien', 6),
    'Tanzanie': ('🌴 Afrique & Océan Indien', 6),
    'Madagascar': ('🌴 Afrique & Océan Indien', 6),
    'Île Maurice': ('🌴 Afrique & Océan Indien', 6),
    'Seychelles': ('🌴 Afrique & Océan Indien', 6),
    'Réunion': ('🌴 Afrique & Océan Indien', 6),
    'Mayotte': ('🌴 Afrique & Océan Indien', 6),
    'Namibie': ('🌴 Afrique & Océan Indien', 6),
    'Sénégal': ('🌴 Afrique & Océan Indien', 6),
    'Cap-Vert': ('🌴 Afrique & Océan Indien', 6),
    # Moyen-Orient
    'EAU': ('🕌 Moyen-Orient', 7),
    'Jordanie': ('🕌 Moyen-Orient', 7),
    'Oman': ('🕌 Moyen-Orient', 7),
    'Israël': ('🕌 Moyen-Orient', 7),
    # Asie du Sud-Est
    'Thaïlande': ('🌏 Asie du Sud-Est', 8),
    'Viêt Nam': ('🌏 Asie du Sud-Est', 8),
    'Indonésie': ('🌏 Asie du Sud-Est', 8),
    'Philippines': ('🌏 Asie du Sud-Est', 8),
    'Malaisie': ('🌏 Asie du Sud-Est', 8),
    'Cambodge': ('🌏 Asie du Sud-Est', 8),
    'Laos': ('🌏 Asie du Sud-Est', 8),
    # Asie de l'Est
    'Japon': ('🏯 Asie de l\'Est', 9),
    'Chine': ('🏯 Asie de l\'Est', 9),
    'Corée du Sud': ('🏯 Asie de l\'Est', 9),
    'Hong Kong': ('🏯 Asie de l\'Est', 9),
    'Taïwan': ('🏯 Asie de l\'Est', 9),
    'Macao': ('🏯 Asie de l\'Est', 9),
    # Asie du Sud
    'Inde': ('🕉️ Asie du Sud', 10),
    'Sri Lanka': ('🕉️ Asie du Sud', 10),
    'Népal': ('🕉️ Asie du Sud', 10),
    'Maldives': ('🕉️ Asie du Sud', 10),
    # Amérique du Nord
    'États-Unis': ('🗽 Amérique du Nord', 11),
    'Canada': ('🗽 Amérique du Nord', 11),
    # Caraïbes
    'Guadeloupe': ('🏝️ Caraïbes', 12),
    'Martinique': ('🏝️ Caraïbes', 12),
    'République dominicaine': ('🏝️ Caraïbes', 12),
    'Cuba': ('🏝️ Caraïbes', 12),
    'Bahamas': ('🏝️ Caraïbes', 12),
    'Sainte-Lucie': ('🏝️ Caraïbes', 12),
    'Saint-Martin': ('🏝️ Caraïbes', 12),
    'Saint-Barthélemy': ('🏝️ Caraïbes', 12),
    'Curaçao': ('🏝️ Caraïbes', 12),
    'Aruba': ('🏝️ Caraïbes', 12),
    'Porto Rico': ('🏝️ Caraïbes', 12),
    'Trinité-et-Tobago': ('🏝️ Caraïbes', 12),
    'Antigua-et-Barbuda': ('🏝️ Caraïbes', 12),
    'Bermudes': ('🏝️ Caraïbes', 12),
    # Mexique & Amérique Centrale
    'Mexique': ('🌮 Mexique & Amérique Centrale', 13),
    'Costa Rica': ('🌮 Mexique & Amérique Centrale', 13),
    'Panama': ('🌮 Mexique & Amérique Centrale', 13),
    'Guatemala': ('🌮 Mexique & Amérique Centrale', 13),
    'Belize': ('🌮 Mexique & Amérique Centrale', 13),
    'Nicaragua': ('🌮 Mexique & Amérique Centrale', 13),
    # Amérique du Sud
    'Colombie': ('🌎 Amérique du Sud', 14),
    'Pérou': ('🌎 Amérique du Sud', 14),
    'Brésil': ('🌎 Amérique du Sud', 14),
    'Chili': ('🌎 Amérique du Sud', 14),
    'Argentine': ('🌎 Amérique du Sud', 14),
    'Équateur': ('🌎 Amérique du Sud', 14),
    'Bolivie': ('🌎 Amérique du Sud', 14),
    'Uruguay': ('🌎 Amérique du Sud', 14),
    # Océanie & Pacifique
    'Australie': ('🦘 Océanie & Pacifique', 15),
    'Nouvelle-Zélande': ('🦘 Océanie & Pacifique', 15),
    'Polynésie française': ('🦘 Océanie & Pacifique', 15),
    'Fidji': ('🦘 Océanie & Pacifique', 15),
    'Nouvelle-Calédonie': ('🦘 Océanie & Pacifique', 15),
    # DOM-TOM / France d'outre-mer
    'Guyane': ('🇫🇷 France d\'outre-mer', 16),
    'Saint-Pierre-et-Miquelon': ('🇫🇷 France d\'outre-mer', 16),
    # Additional countries
    'Émirats Arabes Unis': ('🕌 Moyen-Orient', 7),
    'Qatar': ('🕌 Moyen-Orient', 7),
    'Maurice': ('🌴 Afrique & Océan Indien', 6),
    'Afrique du Sud': ('🌴 Afrique & Océan Indien', 6),
    'Écosse': ('🏰 Europe du Nord & Centrale', 3),
    'Suisse': ('🏰 Europe du Nord & Centrale', 3),
    'Bulgarie': ('🏰 Europe du Nord & Centrale', 3),
    'Estonie': ('❄️ Scandinavie & Baltique', 4),
    'Lettonie': ('❄️ Scandinavie & Baltique', 4),
    'Lituanie': ('❄️ Scandinavie & Baltique', 4),
    'Slovénie': ('🌊 Méditerranée & Europe du Sud', 2),
    'Slovaquie': ('🏰 Europe du Nord & Centrale', 3),
    'Barbade': ('🏝️ Caraïbes', 12),
    'Jamaïque': ('🏝️ Caraïbes', 12),
    'République Dominicaine': ('🏝️ Caraïbes', 12),
    'Cuba': ('🏝️ Caraïbes', 12),
    'Singapour': ('🌏 Asie du Sud-Est', 8),
    'Myanmar': ('🌏 Asie du Sud-Est', 8),
    'Hong Kong': ('🏯 Asie de l\'Est', 9),
    'Macao': ('🏯 Asie de l\'Est', 9),
    'Brésil': ('🌎 Amérique du Sud', 14),
    'Argentine': ('🌎 Amérique du Sud', 14),
    'Ouzbékistan': ('🏔️ Caucase', 5),
    'Hongrie': ('🏰 Europe du Nord & Centrale', 3),
}

def make_card(slug, name, flag, is_fr=True):
    if is_fr:
        href = f'meilleure-periode-{slug}.html'
        sub = 'Quand partir'
    else:
        href = f'best-time-to-visit-{slug}.html'
        sub = 'When to visit'
    return (
        f'<a href="{href}" target="_top" style="background:white;border-radius:12px;padding:14px 12px;'
        f'text-decoration:none;border:1.5px solid #e8e0d0;display:flex;align-items:center;gap:10px">'
        f'<img src="{"" if is_fr else "../"}flags/{flag}.png" width="20" height="15" alt="{flag.upper()}" '
        f'style="vertical-align:middle;border-radius:2px">'
        f'<span><span style="font-size:12px;font-weight:700;color:#1a1f2e;display:block">{name}</span>'
        f'<span style="font-size:10px;color:#5a6478">{sub}</span></span></a>'
    )

def generate_silo1(destinations, is_fr=True):
    """Generate HTML for SILO 1 block"""
    # Group by region
    regions = {}
    for d in destinations:
        pays = d['pays']
        if pays in REGIONS:
            region_name, sort_order = REGIONS[pays]
        else:
            region_name, sort_order = ('🌍 Autres', 99)
            print(f"  ⚠️  Pays sans région: {pays} ({d['nom_fr']})")
        
        if region_name not in regions:
            regions[region_name] = {'order': sort_order, 'dests': []}
        regions[region_name]['dests'].append(d)
    
    # Sort regions by order, destinations alphabetically within
    sorted_regions = sorted(regions.items(), key=lambda x: x[1]['order'])
    
    lines = []
    for region_name, data in sorted_regions:
        dests = sorted(data['dests'], key=lambda x: x['nom_fr'])
        lines.append(f'<h3 style="font-size:13px;font-weight:800;color:#4a5568;text-transform:uppercase;letter-spacing:.08em;margin:28px 0 14px">{region_name}</h3>')
        lines.append('<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:10px;margin-bottom:8px">')
        for d in dests:
            slug = d['slug_fr'] if is_fr else d['slug_en']
            name = d['nom_fr'] if is_fr else d['nom_en']
            lines.append(make_card(slug, name, d['flag'], is_fr))
        lines.append('</div>')
    
    return '\n'.join(lines)


def update_index(filepath, destinations, is_fr=True):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    total = len(destinations)
    
    # Update count in toggle button
    if is_fr:
        content = re.sub(
            r'Voir les guides destinations \(\d+ destinations\)',
            f'Voir les guides destinations ({total} destinations)',
            content
        )
        content = re.sub(
            r'Tableaux climatiques mensuels · \d+ destinations',
            f'Tableaux climatiques mensuels · {total} destinations',
            content
        )
    
    # Replace SILO 1 content
    silo1_html = generate_silo1(destinations, is_fr)
    
    # Find and replace between SILO 1 marker and SILO 2 marker
    pattern = r'(<!-- SILO 1 : MEILLEURE PERIODE - dominant -->.*?<div style="margin-top:8px">)\n.*?(</div>\n\n <!-- SILO 2)'
    replacement = f'\\1\n{silo1_html}\n\\2'
    
    new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    if new_content == content:
        print(f"  ⚠️  Pattern not found in {filepath}")
        return False
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    return True


# Load destinations
destinations = []
with open('data/destinations.csv', encoding='utf-8-sig') as f:
    for r in csv.DictReader(f):
        destinations.append(r)

print(f"📦 {len(destinations)} destinations chargées")

# Update FR index
print("\n🇫🇷 Mise à jour index.html...")
if update_index('index.html', destinations, is_fr=True):
    count = len(re.findall(r'meilleure-periode-', open('index.html').read()))
    print(f"  ✅ {count} liens meilleure-periode dans index.html")
else:
    print("  ❌ Échec")

# Update EN index if exists
import os
en_path = 'en/app.html'
if os.path.exists(en_path):
    print(f"\n🇬🇧 Mise à jour {en_path}...")
    # Check if EN has same structure
    with open(en_path) as f:
        en_content = f.read()
    if 'SILO 1' in en_content:
        if update_index(en_path, destinations, is_fr=False):
            count = len(re.findall(r'best-time-to-visit-', open(en_path).read()))
            print(f"  ✅ {count} liens best-time-to-visit dans en/app.html")
        else:
            print("  ❌ Échec")
    else:
        print("  ⚠️  Pas de bloc SILO 1 dans en/app.html")

print("\n✅ Terminé")
