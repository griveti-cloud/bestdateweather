#!/usr/bin/env python3
"""Merge new specific cards into cards.csv/cards_en.csv, replacing old generated ones."""

import csv, re

# ── Load originals (first 1446 rows) ──
with open('data/cards.csv', encoding='utf-8-sig') as f:
    all_fr = list(csv.DictReader(f))
with open('data/cards_en.csv', encoding='utf-8-sig') as f:
    all_en = list(csv.DictReader(f))

orig_fr = all_fr[:1446]
orig_en = all_en[:1446]

# ── Load new specific FR cards ──
with open('data/cards_new_fr.csv', encoding='utf-8-sig') as f:
    new_fr = list(csv.DictReader(f))

print(f"Original FR: {len(orig_fr)} cards")
print(f"New specific FR: {len(new_fr)} cards")

# Count destinations covered
new_slugs = set(c['slug'] for c in new_fr)
print(f"New destinations: {len(new_slugs)}")

# ── Simple FR→EN translation map for card content ──
# We'll do programmatic translation for common patterns

PERIOD_MAP = {
    "Toute l'année": "Year-round",
    "Toute l'année": "Year-round",
}

MONTH_FR_EN = {
    'Jan': 'Jan', 'Fév': 'Feb', 'Mars': 'Mar', 'Avr': 'Apr',
    'Mai': 'May', 'Juin': 'Jun', 'Juil': 'Jul', 'Août': 'Aug',
    'Sep': 'Sep', 'Oct': 'Oct', 'Nov': 'Nov', 'Déc': 'Dec',
    'Février': 'February', 'Janvier': 'January', 'Mars': 'March',
    'Avril': 'April', 'Mai': 'May', 'Juin': 'June', 'Juillet': 'July',
    'Août': 'August', 'Septembre': 'September', 'Octobre': 'October',
    'Novembre': 'November', 'Décembre': 'December',
}

TITLE_MAP = {
    'Budget': 'Budget',
    'Famille': 'Family',
    'Gastronomie': 'Gastronomy',
    'Culture & visites': 'Culture & sightseeing',
    'Plage & baignade': 'Beach & swimming',
    'Randonnée': 'Hiking',
    'Nature & exploration': 'Nature & exploration',
}

# Common FR→EN word replacements for texte
WORD_MAP = [
    ("Toute l'année", "Year-round"),
    ("toute l'année", "year-round"),
    ("saison sèche", "dry season"),
    ("saison humide", "wet season"),
    ("haute saison", "peak season"),
    ("hors haute saison", "off-peak season"),
    ("hors saison", "off-season"),
    ("prix réduits", "lower prices"),
    ("prix -", "prices -"),
    ("prix bas", "low prices"),
    ("hébergement", "accommodation"),
    ("hôtels", "hotels"),
    ("moins de monde", "fewer crowds"),
    ("moins chers", "cheaper"),
    ("moins de touristes", "fewer tourists"),
    ("vols", "flights"),
    ("repas", "meals"),
    ("nuit", "night"),
    ("jour", "day"),
    ("eau", "water"),
    ("mer", "sea"),
    ("plage", "beach"),
    ("plages", "beaches"),
    ("soleil", "sun"),
    ("coucher de soleil", "sunset"),
    ("lever du soleil", "sunrise"),
    ("pluie", "rain"),
    ("chaleur", "heat"),
    ("froid", "cold"),
    ("vent", "wind"),
    ("neige", "snow"),
    ("montagne", "mountain"),
    ("randonnée", "hiking"),
    ("sentiers", "trails"),
    ("vue", "view"),
    ("ville", "city"),
    ("vieille ville", "old town"),
    ("quartier", "quarter"),
    ("marché", "market"),
    ("marchés", "markets"),
    ("musée", "museum"),
    ("musées", "museums"),
    ("cuisine", "cuisine"),
    ("restaurants", "restaurants"),
    ("Toute l'année", "Year-round"),
]


def translate_period(text):
    """Translate month periods."""
    result = text
    # Replace full month names first
    for fr, en in sorted(MONTH_FR_EN.items(), key=lambda x: -len(x[0])):
        result = result.replace(fr, en)
    return result


def generate_en_card(fr_card):
    """Generate EN card from FR card. Keep specific names, translate common patterns."""
    slug = fr_card['slug']
    icon = fr_card['icon']
    titre_fr = fr_card['titre']
    texte_fr = fr_card['texte']
    
    # Title: keep as-is for specific titles, translate generic ones
    titre_en = TITLE_MAP.get(titre_fr, titre_fr)
    
    # Texte: translate period prefix, keep specific content
    texte_en = translate_period(texte_fr)
    
    return {'slug': slug, 'icon': icon, 'titre': titre_en, 'texte': texte_en}


# Generate EN cards
new_en = [generate_en_card(c) for c in new_fr]

# ── Write merged files ──
with open('data/cards.csv', 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.DictWriter(f, fieldnames=['slug', 'icon', 'titre', 'texte'])
    w.writeheader()
    for c in orig_fr:
        w.writerow(c)
    for c in new_fr:
        w.writerow(c)

with open('data/cards_en.csv', 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.DictWriter(f, fieldnames=['slug', 'icon', 'titre', 'texte'])
    w.writeheader()
    for c in orig_en:
        w.writerow(c)
    for c in new_en:
        w.writerow(c)

print(f"\n✅ FR: {len(orig_fr) + len(new_fr)} cards")
print(f"✅ EN: {len(orig_en) + len(new_en)} cards")

# ── Coverage check ──
with open('data/destinations.csv', encoding='utf-8-sig') as f:
    dest_slugs = set(d['slug_fr'] for d in csv.DictReader(f))

with open('data/cards.csv', encoding='utf-8-sig') as f:
    card_slugs = set(c['slug'] for c in csv.DictReader(f))

missing = dest_slugs - card_slugs
if missing:
    print(f"\n⚠️ Still missing {len(missing)}: {sorted(missing)}")
else:
    print(f"\n✅ All {len(dest_slugs)} destinations covered")

# Show sample
print("\n=== Sample new cards ===")
for c in new_fr[:3]:
    print(f"  FR: {c['icon']} {c['titre']}: {c['texte'][:60]}...")
for c in new_en[:3]:
    print(f"  EN: {c['icon']} {c['titre']}: {c['texte'][:60]}...")
