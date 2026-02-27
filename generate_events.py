#!/usr/bin/env python3
"""Generate contextual events for destination × month slots missing from events.csv.

Uses cards (activities) + climate data to create locally relevant events.
Does NOT overwrite existing events — only fills gaps.
"""
import csv, random

DATA = 'data'
MONTHS_FR = ['janvier','février','mars','avril','mai','juin','juillet','août','septembre','octobre','novembre','décembre']
MONTHS_EN = ['January','February','March','April','May','June','July','August','September','October','November','December']

# ── Load data ────────────────────────────────────────────────────────────────
def load():
    existing = set()
    existing_rows = []
    for r in csv.DictReader(open(f'{DATA}/events.csv', encoding='utf-8-sig', newline='')):
        clean = {k.strip(): v.strip() for k, v in r.items() if k is not None}
        existing.add((clean['slug'], int(clean['month'])))
        existing_rows.append(clean)
    
    cards = {}
    for r in csv.DictReader(open(f'{DATA}/cards.csv', encoding='utf-8-sig')):
        cards.setdefault(r['slug'], []).append(r)

    climate = {}
    for r in csv.DictReader(open(f'{DATA}/climate.csv', encoding='utf-8-sig')):
        mi = int(r['mois_num'])
        climate.setdefault(r['slug'], {})[mi] = {
            'tmax': int(r['tmax']), 'rain': int(r['rain_pct']),
            'score': float(r['score']), 'sun': float(r['sun_h']),
        }

    dests = {}
    for r in csv.DictReader(open(f'{DATA}/destinations.csv', encoding='utf-8-sig')):
        dests[r['slug_fr']] = r

    return existing, existing_rows, cards, climate, dests

# ── Event generators by context ──────────────────────────────────────────────

def parse_card_period(texte):
    """Extract month range from card text like 'Juin-septembre — ...' """
    parts = texte.split(' — ', 1)
    return parts[0] if len(parts) == 2 else ''

def month_in_card_period(mi, texte):
    """Check if month index (1-12) falls within a card's period."""
    period = parse_card_period(texte).lower()
    if 'toute l\'année' in period or 'year-round' in period:
        return True
    month_names_fr = {n: i+1 for i, n in enumerate(MONTHS_FR)}
    # Simple check: if the month name appears in the period
    return MONTHS_FR[mi-1] in period

def get_active_cards(card_list, month):
    """Get cards whose period covers this month."""
    active = []
    for c in card_list:
        if month_in_card_period(month, c['texte']):
            active.append(c)
    return active

def gen_beach_event(dest, month, clim, card):
    """Generate beach/swimming related event."""
    tmax = clim['tmax']
    nom = dest['nom_bare']
    m_fr = MONTHS_FR[month-1]
    m_en = MONTHS_EN[month-1]
    
    if tmax >= 28:
        return (
            f"Eau à {tmax-3}°C et plages animées — {m_fr} est un pic de baignade {_prep(dest)} {nom}",
            f"Water at {tmax-3}°C and lively beaches — {m_en} is peak swimming season in {dest.get('nom_en', nom)}"
        )
    elif tmax >= 22:
        return (
            f"Température idéale pour la plage ({tmax}°C) — affluence encore modérée",
            f"Ideal beach temperature ({tmax}°C) — crowds still moderate"
        )
    else:
        return (
            f"Plages calmes et peu fréquentées — idéal pour les promenades côtières",
            f"Quiet uncrowded beaches — ideal for coastal walks"
        )

def gen_hiking_event(dest, month, clim, card):
    nom = dest['nom_bare']
    tmax = clim['tmax']
    rain = clim['rain']
    m_fr = MONTHS_FR[month-1]
    m_en = MONTHS_EN[month-1]
    nom_en = dest.get('nom_en', nom)
    
    if rain <= 15 and 15 <= tmax <= 28:
        return (
            f"Conditions optimales de randonnée — {tmax}°C et faible risque de pluie ({rain}%)",
            f"Optimal hiking conditions — {tmax}°C and low rain risk ({rain}%)"
        )
    elif tmax >= 30:
        return (
            f"Randonnées à privilégier tôt le matin — chaleur marquée dès 11h ({tmax}°C)",
            f"Hike early morning to avoid the heat — temperatures reach {tmax}°C by 11am"
        )
    elif rain >= 40:
        return (
            f"Sentiers praticables mais humides — prévoir des chaussures adaptées et des pauses abritées",
            f"Trails walkable but wet — bring proper footwear and plan sheltered breaks"
        )
    else:
        return (
            f"Bonne fenêtre pour la randonnée — températures douces ({tmax}°C) et sentiers peu fréquentés",
            f"Good hiking window — mild temperatures ({tmax}°C) and uncrowded trails"
        )

def gen_culture_event(dest, month, clim, card):
    nom = dest['nom_bare']
    tmax = clim['tmax']
    nom_en = dest.get('nom_en', nom)
    score = clim['score']
    
    if score >= 8:
        return (
            f"Haute saison culturelle — musées et sites accessibles dans de bonnes conditions météo",
            f"Peak cultural season — museums and sites accessible in good weather conditions"
        )
    elif score >= 5:
        return (
            f"Sites culturels moins fréquentés qu'en haute saison — visites plus agréables",
            f"Cultural sites less crowded than peak season — more enjoyable visits"
        )
    else:
        return (
            f"Basse saison touristique — musées et monuments sans file d'attente",
            f"Tourist low season — museums and monuments without queues"
        )

def gen_food_event(dest, month, clim, card):
    nom = dest['nom_bare']
    m_fr = MONTHS_FR[month-1]
    m_en = MONTHS_EN[month-1]
    nom_en = dest.get('nom_en', nom)
    
    if month in (9, 10, 11):  # Harvest season
        return (
            f"Saison des récoltes — produits locaux frais sur les marchés et dans les restaurants",
            f"Harvest season — fresh local produce at markets and restaurants"
        )
    elif month in (12, 1, 2):  # Winter comfort food
        return (
            f"Plats d'hiver et spécialités réconfortantes dans les restaurants locaux",
            f"Winter dishes and comfort food specialities in local restaurants"
        )
    else:
        return (
            f"Terrasses ouvertes et marchés en plein air — meilleure saison pour manger dehors",
            f"Open terraces and outdoor markets — best season for al fresco dining"
        )

def gen_diving_event(dest, month, clim, card):
    tmax = clim['tmax']
    rain = clim['rain']
    
    if rain <= 20 and tmax >= 24:
        return (
            f"Visibilité sous-marine optimale — eau claire et conditions de plongée idéales",
            f"Optimal underwater visibility — clear water and ideal diving conditions"
        )
    elif rain >= 40:
        return (
            f"Plongée possible malgré la pluie — la visibilité sous-marine reste correcte en profondeur",
            f"Diving still possible despite rain — underwater visibility stays decent at depth"
        )
    else:
        return (
            f"Bonne saison de plongée — eau à bonne température et visibilité satisfaisante",
            f"Good diving season — comfortable water temperature and satisfactory visibility"
        )

def gen_budget_event(dest, month, clim, card):
    score = clim['score']
    nom = dest['nom_bare']
    nom_en = dest.get('nom_en', nom)
    
    if score >= 8:
        return (
            f"Haute saison — réserver à l'avance pour les meilleurs tarifs. Prix hébergements au plus haut",
            f"Peak season — book ahead for best rates. Accommodation prices at their highest"
        )
    elif score >= 5:
        return (
            f"Entre-saison — bon rapport qualité/prix avec des tarifs hébergement raisonnables",
            f"Shoulder season — good value with reasonable accommodation prices"
        )
    else:
        return (
            f"Basse saison — tarifs au plus bas et promotions fréquentes sur les hébergements",
            f"Low season — lowest prices and frequent accommodation deals"
        )

def gen_family_event(dest, month, clim, card):
    tmax = clim['tmax']
    score = clim['score']
    nom_en = dest.get('nom_en', dest['nom_bare'])
    
    if score >= 8 and tmax <= 32:
        return (
            f"Conditions idéales pour les familles — météo agréable et activités extérieures accessibles",
            f"Ideal conditions for families — pleasant weather and outdoor activities accessible"
        )
    elif tmax >= 33:
        return (
            f"Chaleur forte — privilégier les activités matinales et les espaces climatisés l'après-midi",
            f"Hot weather — prioritise morning activities and air-conditioned spaces in the afternoon"
        )
    elif score < 5:
        return (
            f"Période calme pour les familles — moins de monde mais activités extérieures limitées",
            f"Quiet period for families — fewer crowds but limited outdoor activities"
        )
    else:
        return (
            f"Bonne période famille — températures correctes et sites accessibles sans foule",
            f"Good family period — decent temperatures and sites accessible without crowds"
        )

def gen_nightlife_event(dest, month, clim, card):
    score = clim['score']
    if score >= 8:
        return (
            f"Saison haute — bars et clubs animés, terrasses ouvertes tard le soir",
            f"Peak season — bars and clubs buzzing, terraces open late into the evening"
        )
    else:
        return (
            f"Hors saison — ambiance locale plus authentique dans les bars et restaurants",
            f"Off-season — more authentic local atmosphere in bars and restaurants"
        )

def gen_surf_event(dest, month, clim, card):
    tmax = clim['tmax']
    m_fr = MONTHS_FR[month-1]
    m_en = MONTHS_EN[month-1]
    
    if month in (10, 11, 12, 1, 2, 3):
        return (
            f"Houle hivernale — vagues plus puissantes, idéal pour surfeurs confirmés",
            f"Winter swell — more powerful waves, ideal for experienced surfers"
        )
    elif month in (4, 5, 9):
        return (
            f"Conditions de surf équilibrées — vagues régulières et moins de monde au lineup",
            f"Balanced surf conditions — consistent waves and fewer surfers in the lineup"
        )
    else:
        return (
            f"Haute saison surf — spots fréquentés mais conditions fiables",
            f"Peak surf season — busy spots but reliable conditions"
        )

def gen_wine_event(dest, month, clim, card):
    if month in (9, 10):
        return (
            f"Vendanges — visites de domaines, dégustations et ambiance festive dans les vignobles",
            f"Grape harvest — winery visits, tastings and festive atmosphere in the vineyards"
        )
    elif month in (3, 4, 5):
        return (
            f"Vignobles en fleurs — route des vins agréable avant la chaleur estivale",
            f"Vineyards in bloom — wine route pleasant before summer heat"
        )
    elif month in (6, 7, 8):
        return (
            f"Maturation des raisins — visites œnologiques et terrasses de dégustation en plein air",
            f"Grapes ripening — wine tours and outdoor tasting terraces"
        )
    else:
        return (
            f"Saison calme dans les vignobles — dégustations intimistes et tarifs réduits",
            f"Quiet season in the vineyards — intimate tastings and reduced prices"
        )

def gen_generic_event(dest, month, clim):
    """Fallback: generate a weather-context event."""
    score = clim['score']
    tmax = clim['tmax']
    rain = clim['rain']
    nom = dest['nom_bare']
    nom_en = dest.get('nom_en', nom)
    m_fr = MONTHS_FR[month-1]
    m_en = MONTHS_EN[month-1]
    
    if score >= 9:
        return (
            f"L'un des meilleurs mois — {tmax}°C, ensoleillement maximal et conditions idéales",
            f"One of the best months — {tmax}°C, maximum sunshine and ideal conditions"
        )
    elif score >= 7:
        return (
            f"Bonne période — {tmax}°C avec un bon ensoleillement. Affluence raisonnable",
            f"Good period — {tmax}°C with good sunshine. Reasonable crowds"
        )
    elif score >= 5:
        return (
            f"Période acceptable — {tmax}°C mais {rain}% de risque de pluie. Prévoir des alternatives",
            f"Acceptable period — {tmax}°C but {rain}% rain risk. Plan alternatives"
        )
    elif score >= 3:
        return (
            f"Basse saison — {tmax}°C et conditions limitées. Avantage : prix réduits et peu de touristes",
            f"Low season — {tmax}°C and limited conditions. Upside: lower prices and few tourists"
        )
    else:
        return (
            f"Période déconseillée sauf budget serré — conditions météo difficiles ({tmax}°C, {rain}% pluie)",
            f"Not recommended unless on tight budget — difficult weather ({tmax}°C, {rain}% rain)"
        )


# ── Card title to generator mapping ──────────────────────────────────────────
CARD_GENERATORS = {
    'plage': gen_beach_event,
    'beach': gen_beach_event,
    'baignade': gen_beach_event,
    'surf': gen_surf_event,
    'bodyboard': gen_surf_event,
    'kitesurf': gen_surf_event,
    'randonnée': gen_hiking_event,
    'hiking': gen_hiking_event,
    'trek': gen_hiking_event,
    'sentier': gen_hiking_event,
    'vtt': gen_hiking_event,
    'cyclisme': gen_hiking_event,
    'vélo': gen_hiking_event,
    'musée': gen_culture_event,
    'culture': gen_culture_event,
    'patrimoine': gen_culture_event,
    'architecture': gen_culture_event,
    'histoire': gen_culture_event,
    'temple': gen_culture_event,
    'gastronomie': gen_food_event,
    'gastro': gen_food_event,
    'cuisine': gen_food_event,
    'marché': gen_food_event,
    'bouchon': gen_food_event,
    'hawker': gen_food_event,
    'street food': gen_food_event,
    'plongée': gen_diving_event,
    'diving': gen_diving_event,
    'snorkeling': gen_diving_event,
    'budget': gen_budget_event,
    'famille': gen_family_event,
    'family': gen_family_event,
    'fête': gen_nightlife_event,
    'vie nocturne': gen_nightlife_event,
    'nightlife': gen_nightlife_event,
    'club': gen_nightlife_event,
    'soirée': gen_nightlife_event,
    'vin': gen_wine_event,
    'vignoble': gen_wine_event,
    'oenotourisme': gen_wine_event,
    'route des vins': gen_wine_event,
    'chianti': gen_wine_event,
}

def _prep(dest):
    return dest.get('prep', 'à')

def find_generator(card_title):
    """Match a card title to its best event generator."""
    title_lower = card_title.lower()
    for keyword, gen in CARD_GENERATORS.items():
        if keyword in title_lower:
            return gen
    return None

# ── Main: generate missing events ────────────────────────────────────────────
def main():
    existing, existing_rows, cards, climate, dests = load()
    
    new_events = []
    used_generators = set()  # Track (slug, month, generator) to avoid duplicates
    
    for slug in sorted(dests.keys()):
        if slug not in climate:
            continue
        dest = dests[slug]
        card_list = cards.get(slug, [])
        
        for month in range(1, 13):
            if (slug, month) in existing:
                continue
            
            clim = climate[slug].get(month)
            if not clim:
                continue
            
            # Try to find a relevant card-based generator
            # Rotate through cards to avoid same event for every month
            event = None
            card_gens = []
            for card in card_list:
                gen = find_generator(card['titre'])
                if gen:
                    card_gens.append((gen, card))
            
            if card_gens:
                # Pick generator based on month index to rotate
                idx = (month - 1) % len(card_gens)
                gen, card = card_gens[idx]
                # If this generator was already used for this slug, try next
                attempts = 0
                while (slug, month, gen.__name__) in used_generators and attempts < len(card_gens):
                    idx = (idx + 1) % len(card_gens)
                    gen, card = card_gens[idx]
                    attempts += 1
                
                if (slug, month, gen.__name__) not in used_generators:
                    event = gen(dest, month, clim, card)
                    used_generators.add((slug, month, gen.__name__))
            
            # Fallback to generic weather-context event
            if not event:
                event = gen_generic_event(dest, month, clim)
            
            new_events.append({
                'slug': slug,
                'month': str(month),
                'event_fr': event[0],
                'event_en': event[1],
            })
    
    # Write all events (existing + new) sorted
    all_events = existing_rows + new_events
    all_events.sort(key=lambda x: (x['slug'], int(x['month'])))
    
    with open(f'{DATA}/events.csv', 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.DictWriter(f, fieldnames=['slug','month','event_fr','event_en'], quoting=csv.QUOTE_MINIMAL)
        w.writeheader()
        for row in all_events:
            # Ensure only known fields
            w.writerow({k: row[k] for k in ['slug','month','event_fr','event_en']})
    
    print(f"✅ Events: {len(existing_rows)} existing + {len(new_events)} new = {len(all_events)} total")
    print(f"   Coverage: {len(all_events)}/{len(dests)*12} slots ({len(all_events)/(len(dests)*12)*100:.0f}%)")
    
    # Show sample
    print("\n--- Sample new events ---")
    for e in new_events[:10]:
        print(f"  [{e['slug']}] M{e['month']}: {e['event_fr'][:80]}")

if __name__ == '__main__':
    main()
