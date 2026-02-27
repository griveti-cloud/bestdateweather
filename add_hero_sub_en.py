#!/usr/bin/env python3
"""Add hero_sub_en column to destinations.csv with English translations of hero_sub."""
import csv

HERO_SUB_EN = {
    'agadir': "Agadir, Morocco's beach resort — 300 days of sunshine per year, long sandy beach and modern resorts.",
    'algarve': "300 days of sunshine, golden cliffs and Atlantic ocean — the Algarve is the most accessible coastal destination from Western Europe.",
    'alicante': "Alicante, Costa Blanca — one of Europe's sunniest cities, with white sand beaches at reasonable prices.",
    'amalfi': "Italy's most beautiful coastline — with unique logistical constraints in July-August. June and September are the no-compromise windows.",
    'amsterdam': "Amsterdam, canals and tulips — the unpredictable northern weather plays a crucial role in choosing your dates.",
    'bali': "Bali can be visited year-round but the monsoon (Nov-Mar) increases rain risk sixfold. 10 years of data to choose according to your plans.",
    'bangkok': "Bangkok, Thailand's capital — temples, street food and nightlife, but the monsoon dictates everything.",
    'barcelone': "Barcelona, Gaudí, beaches and nightlife — a four-season destination where weather changes everything by month.",
    'berlin': "Berlin, the capital of creativity — street art, legendary clubs and History everywhere.",
    'bordeaux': "World capital of wine, UNESCO-listed architecture.",
    'bretagne': "Wild coastlines, crêperies and authentic Celtic culture.",
    'buenos-aires': "Buenos Aires — tango, asado and European architecture in the southern hemisphere. Seasons are reversed.",
    'cancun': "Cancún — Caribbean beaches, Mayan cenotes and all-inclusive hotels. Hurricane season changes everything.",
    'capri': "Capri is the island of luxury and dolce vita. Only accessible by ferry — but the Faraglioni, Blue Grotto and private villas are worth the journey.",
    'canaries': "The Canary Islands are the only year-round destination in this guide: tropical summer and mild winter guaranteed. 10 years of data.",
    'corfou': "Corfu, Greece's green island — lush vegetation, Venetian old town and crystal-clear Ionian sea.",
    'corse': "The island of beauty, wild beaches and fragrant maquis.",
    'costa-rica': "Costa Rica, exceptional biodiversity, volcanoes and beaches — ecotourism at its finest.",
    'cote-azur': "The French Riviera is accessible year-round. The long May-September window offers 5 months of excellent weather — with a golden window in June.",
    'crete': "Crete is open all year. Bigger, cheaper and more diverse than Santorini or Mykonos.",
    'dubai': "Dubai is unbearable from June to September. But from November to April, it has one of the best weather records in the world.",
    'dubrovnik': "Dubrovnik, the Pearl of the Adriatic — medieval ramparts, turquoise waters and Game of Thrones scenery.",
    'edimbourg': "Edinburgh — castle on a volcanic rock, Festival Fringe and Highland whisky. Unpredictable weather.",
    'florence': "Florence, capital of the Renaissance — between the Uffizi, Duomo and Chianti, weather shapes the cultural experience.",
    'fuerteventura': "Fuerteventura, dunes and sandy beaches in the Canary Islands — a paradise for water sports.",
    'goa': "Goa, tropical beaches, spicy cuisine and Portuguese heritage — India's pearl.",
    'gran-canaria': "Gran Canaria, a continent in miniature — dune beaches, pine forests and lively towns all in one island.",
    'hawaii': "Maui, volcanoes, black lava beaches and legendary surf — Hawaii in all its splendour.",
    'hoi-an': "Hội An, UNESCO ancient town — lanterns, tailors and beaches 4km away, between culture and relaxation.",
    'ibiza': "Ibiza isn't just about the clubs. Wild calas, fincas and iconic sunsets — with very different months depending on your plans.",
    'ile-maurice': "Mauritius is one of the world's most beautiful destinations — but cyclone season (Jan-Mar) means you must choose your dates carefully. 10 years of data.",
    'istanbul': "Istanbul is the only city in the world straddling two continents. Bosphorus, Ottoman palaces, ancient bazaars — an incomparable cultural destination.",
    'jamaique': "Jamaica, reggae, white sand beaches and waterfalls — the soul of the Caribbean.",
    'katmandou': "Kathmandu, gateway to the Himalayas — Buddhist temples, Everest base camp and a unique culture.",
    'la-havane': "Havana — 1950s American cars, rum, salsa and the Malecón. Cuba frozen in time.",
    'lanzarote': "Lanzarote, the volcanic Canary Island — Martian landscapes, black beaches and year-round sunshine.",
    'le-cap': "Cape Town, between Table Mountain, vineyards and spectacular landscapes — the pearl of South Africa.",
    'lisbonne': "Lisbon enjoys ~300 days of sunshine per year and easy access from most of Europe. 10 years of data to help you choose.",
    'londres': "London — Big Ben, free museums and Victorian pubs. Unpredictable weather is the main challenge.",
    'los-angeles': "Los Angeles, Californian sunshine, Hollywood and legendary beaches — the city of dreams.",
    'lyon': "Capital of French gastronomy, Roman and Renaissance city.",
    'madere': "Madeira, the island of eternal spring — a unique climate year-round thanks to the Atlantic and altitude.",
    'majorque': "Mallorca is accessible year-round but July-August exceeds 34°C. June and September-October offer the best weather-price-tranquillity ratio.",
    'maldives': "Maldives — atolls, overwater bungalows and turquoise waters. The tropical paradise by definition.",
    'malaga': "Málaga, gateway to the Costa del Sol — 320 days of sunshine per year, Picasso and the best sunshine-to-price ratio in Europe.",
    'malte': "Malta is one of the sunniest Mediterranean destinations — 320 days of sunshine per year. Medieval bastions, Blue Lagoon of Comino, crystal-clear waters.",
    'marrakech': "Marrakech is 3 hours from Paris — but 41°C in July. Two ideal windows: March-April and October-November.",
    'marseille': "The Phocaean city, Calanques and Mediterranean culture.",
    'miami': "Miami, art deco, golden beaches and electric nightlife — Florida's sunshine capital.",
    'minorque': "Menorca, wild coves and crystal-clear waters — the most preserved of the Balearic Islands.",
    'monaco': "Monaco, the world's smallest state — Grand Prix, Monte-Carlo Casino and the Mediterranean at your doorstep.",
    'mykonos': "Mykonos is open 6 months out of 12. The Meltemi wind in July-August can disrupt terrace activities — June and September remain the best months.",
    'new-york': "New York, the city that never sleeps — four distinct seasons that radically transform the experience.",
    'nice': "The pearl of the French Riviera, blue sea and baroque old town.",
    'paris': "The City of Light, world-class museums and gastronomy.",
    'phuket': "Phuket, Andaman pearl — crystal beaches and turquoise sea, but the monsoon splits the year in two.",
    'porto': "Porto, capital of wine — port wine cellars, Dom Luís bridge and authentic gastronomy along the Douro.",
    'prague': "Prague, the golden city — castle, Charles Bridge and craft beer. Weather strongly influences tourist numbers.",
    'provence': "Lavender fields, Provençal markets and perched villages.",
    'reunion': "Réunion, the intense island — hikes through volcanic cirques, turquoise lagoon and exceptional climatic diversity.",
    'reykjavik': "Reykjavik — Northern Lights, geysers and glaciers. Weather dictates everything in this extreme destination.",
    'rhodes': "Rhodes, the island of sun — the sunniest in the Mediterranean with over 300 days of sunshine per year.",
    'rio-de-janeiro': "Rio de Janeiro — Copacabana, Ipanema and Christ the Redeemer. Carnival and the rainy season dictate everything.",
    'riviera-maya': "December-April is the golden window without risk. Sargassum May-November and hurricanes August-October must be factored into your planning.",
    'rome': "Rome, the Eternal City — Colosseum, Vatican and trattorie. Summer is sweltering, spring is perfect.",
    'santorin': "Santorini shuts down 6 months out of 12. June and September are the ideal windows — the Meltemi wind in July-August can disrupt terrace activities.",
    'sardaigne': "Sardinia — Costa Smeralda, turquoise water and white sand dunes. The quintessential Italian postcard.",
    'seville': "Seville, flamenco, tapas and Moorish architecture — the jewel of Andalusia.",
    'seychelles': "Seychelles — granite boulders, white sand beaches and crystal-clear waters. The last Eden.",
    'sicile': "Sicily enjoys one of the best climates in the Mediterranean with prices lower than mainland Italy.",
    'siem-reap': "Siem Reap, gateway to Angkor — the world's largest religious complex, between jungle and Khmer art.",
    'singapour': "Singapore, futuristic city-state — Gardens by the Bay, incredible street food and iconic architecture.",
    'split': "Split — Diocletian's Palace, gateway to the Dalmatian islands and ideal base for exploring the Croatian coast.",
    'tenerife': "Tenerife, island of Mount Teide — the largest Canary Island, with a unique microclimate varying by altitude and coast.",
    'tokyo': "Tokyo — cherry blossoms, humid summer, fiery autumn: each season offers a radically different city.",
    'toscane': "Tuscany is accessible year-round but July-August reaches 36-38°C. 10 years of data to choose according to your plans.",
    'tulum': "Tulum, Mayan ruins, cenotes and wild beaches — the bohemian destination of the Yucatán.",
    'valence': "Valencia, capital of paella and Las Fallas — Mediterranean sunshine with fewer tourists than Barcelona.",
    'venise': "Venice is beautiful year-round — but acqua alta in winter and 30 million tourists in summer make it a destination to plan carefully.",
    'vienne': "Vienna — Opera, Schönbrunn and Viennese coffee houses. The Austrian capital plays the culture card all year.",
    'zakynthos': "Zakynthos, Navagio Beach and the famous Shipwreck Cove — turquoise waters and dramatic cliffs in the Ionian Sea.",
    'zanzibar': "Zanzibar, spices and corals — Stone Town and white sand beaches in the Tanzanian Indian Ocean.",
    'barbade': "Barbados, white sand beaches and turquoise water — a Caribbean island ideal year-round.",
}

# Read existing CSV
with open('data/destinations.csv', encoding='utf-8-sig', newline='') as f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames
    rows = list(reader)

# Add hero_sub_en field
if 'hero_sub_en' not in fieldnames:
    fieldnames = list(fieldnames) + ['hero_sub_en']

for row in rows:
    slug = row['slug_fr']
    row['hero_sub_en'] = HERO_SUB_EN.get(slug, '')

# Write back
with open('data/destinations.csv', 'w', encoding='utf-8-sig', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

# Verify
missing = [r['slug_fr'] for r in rows if not r.get('hero_sub_en')]
print(f"✅ Added hero_sub_en for {len(rows) - len(missing)}/{len(rows)} destinations")
if missing:
    print(f"⚠️ Missing: {missing}")
