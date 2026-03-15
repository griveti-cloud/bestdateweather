#!/usr/bin/env python3
import csv, re

MONTH_FULL = {
    'January':'enero','February':'febrero','March':'marzo','April':'abril',
    'May':'mayo','June':'junio','July':'julio','August':'agosto',
    'September':'septiembre','October':'octubre','November':'noviembre','December':'diciembre',
}
MONTH_SHORT = {
    'Jan':'ene.','Feb':'feb.','Mar':'mar.','Apr':'abr.',
    'Jun':'jun.','Jul':'jul.','Aug':'ago.','Sep':'sep.',
    'Oct':'oct.','Nov':'nov.','Dec':'dic.',
}
SEASON_MAP = {
    'Year-round':'Todo el año','year-round':'Todo el año',
    'All year':'Todo el año','All-year':'Todo el año',
    'Dry season':'Temporada seca','Rainy season':'Temporada de lluvias',
    'Winter':'Invierno','Summer':'Verano','Spring':'Primavera',
    'Autumn':'Otoño','Fall':'Otoño',
}
TITLE_EXACT = {
    'Budget':'Presupuesto bajo','Budget Travel':'Viaje económico','Tight Budget':'Presupuesto ajustado',
    'Family':'Familia','Honeymoon':'Luna de miel','Relaxation':'Descanso',
    'Digital Nomad':'Nómada digital','Shopping':'Compras','Luxury':'Lujo',
    'Yoga & Wellness':'Yoga y bienestar','Spa & Wellness':'Spa y bienestar',
    'Spa & Relaxation':'Spa y descanso','Spa & Honeymoon':'Spa y luna de miel',
    'Retreat / Yoga':'Retiro / Yoga','Wellness':'Bienestar','Nightlife':'Vida nocturna',
    'Nightlife & Clubs':'Vida nocturna y clubes','Parties & Clubs':'Fiestas y clubes',
    'Parties & Nightlife':'Fiestas y vida nocturna','Parties & Festivals':'Fiestas y festivales',
    'Beach':'Playa','Beaches':'Playas','Beaches & Islands':'Playas e islas',
    'Beach & Islands':'Playa e islas','Beaches & Coves':'Playas y calas',
    'Coves & Beaches':'Calas y playas','Beach & Lagoon':'Playa y laguna',
    'Beaches & Lagoon':'Playas y laguna','Beaches & lagoons':'Playas y lagunas',
    'Beach & Surfing':'Playa y surf','Beach & Swimming':'Playa y natación',
    'Beach & Snorkelling':'Playa y snorkel','Beach & Relaxation':'Playa y descanso',
    'Beach & Kitesurfing':'Playa y kitesurf','Beach & Windsurfing':'Playa y windsurf',
    'Beach & Dunes':'Playa y dunas','Beach & Caribbean':'Playa y Caribe',
    'Beach & Cliffs':'Playa y acantilados','Beach & Coves':'Playa y calas',
    'Beach & Cenotes':'Playa y cenotes','Beach Route':'Ruta de playas',
    'Beaches & Snorkelling':'Playas y snorkel','Beaches & Bays':'Playas y bahías',
    'Beaches & Surf':'Playas y surf','Beaches & Resorts':'Playas y resorts',
    'Swimming & Coves':'Baño y calas','Surf & Beach':'Surf y playa',
    'Surfing':'Surf','Surfing & beaches':'Surf y playas','Surfing & kitesurfing':'Surf y kitesurf',
    'Kitesurfing':'Kitesurf','Kitesurfing & Sports':'Kitesurf y deportes',
    'Windsurfing':'Windsurf','Windsurfing & kite':'Windsurf y kite',
    'Windsurfing & kitesurfing':'Windsurf y kitesurf','Windsurf & Kitesurf':'Windsurf y kitesurf',
    'Sailing':'Vela','Sailing & Yachting':'Vela y yate','Sailing & Water Sports':'Vela y deportes acuáticos',
    'Sailing & Regattas':'Vela y regatas','Sailing & island hopping':'Vela e island hopping',
    'Water Sports':'Deportes acuáticos','Snorkelling':'Snorkel','Snorkelling & Diving':'Snorkel y buceo',
    'Snorkelling & Reefs':'Snorkel y arrecifes','Snorkeling & reefs':'Snorkel y arrecifes',
    'Snorkeling & turtles':'Snorkel y tortugas','Island Hopping':'Island hopping',
    'Island hopping':'Island hopping','Blue Cruise':'Crucero azul',
    'Boat Trip':'Excursión en barco','Boat Tour':'Tour en barco',
    'Coastal Walk':'Paseo costero','Coastal Path':'Camino costero',
    'Coastal Trails':'Senderos costeros','Coastal Hiking':'Senderismo costero',
    'Coastal Excursion':'Excursión costera','Car-Free Island':'Isla sin coches',
    'Overwater Bungalows':'Bungalós sobre el agua',
    'Diving':'Buceo','Diving & Snorkelling':'Buceo y snorkel','Diving & Surfing':'Buceo y surf',
    'Diving & Cenotes':'Buceo y cenotes','Diving & Caves':'Buceo y cuevas',
    'Diving & Delos Trip':'Buceo y excursión a Delos','Diving & Phi Phi Islands':'Buceo e islas Phi Phi',
    'Diving & pearl heritage':'Buceo y patrimonio perlas','Diving & sharks':'Buceo y tiburones',
    'Diving & snorkeling':'Buceo y snorkel','Red Sea Diving':'Buceo en el Mar Rojo',
    'Red Sea diving':'Buceo en el Mar Rojo','Cenote Diving':'Buceo en cenotes',
    'Wreck Diving':'Buceo en pecios','Shore diving':'Buceo desde la costa',
    'Liveaboard Cruise':'Crucero liveaboard','PADI Diving':'Buceo PADI',
    'Manta ray diving':'Buceo con mantas rayas','Manta Point diving':'Buceo en Manta Point',
    'Wildlife':'Fauna salvaje','Wildlife & Chitwan':'Fauna y Chitwan',
    'Birdwatching':'Observación de aves','Birds':'Aves',
    'Whale Watching':'Avistamiento de ballenas','Whale watching':'Avistamiento de ballenas',
    'Humpback Whales':'Ballenas jorobadas','Humpback whales':'Ballenas jorobadas',
    'Dolphins & Whales':'Delfines y ballenas','Whales & Dolphins':'Ballenas y delfines',
    'Whales & dolphins':'Ballenas y delfines','Whales & Penguins':'Ballenas y pingüinos',
    'Sea Turtles':'Tortugas marinas','Sea turtles':'Tortugas marinas',
    'Turtle Snorkelling':'Snorkel con tortugas','Turtles':'Tortugas',
    'Whale Sharks':'Tiburones ballena','Whale sharks':'Tiburones ballena',
    'Flamingos':'Flamencos','Flamingo reserve':'Reserva de flamencos',
    'Dolphins':'Delfines','Giant Tortoises':'Tortugas gigantes',
    'Penguins':'Pingüinos','Polar bears':'Osos polares',
    'Crocodiles':'Cocodrilos','Komodo Dragons':'Dragones de Komodo',
    'Komodo dragons':'Dragones de Komodo','Orangutans':'Orangutanes',
    'Gorillas':'Gorilas','Manta Rays':'Mantas rayas','Endemic Wildlife':'Fauna endémica',
    'Marine wildlife':'Fauna marina','Dugongs & Turtles':'Dugongos y tortugas',
    'Black rhinos':'Rinocerontes negros','Birds of paradise':'Aves del paraíso',
    'Leatherback Turtles':'Tortugas laúd','Bear watching':'Observación de osos',
    'Dog Sledding':'Trineo con perros','Snowmobile & Sledding':'Moto de nieve y trineo',
    'Hiking':'Senderismo','Hiking & Wildlife':'Senderismo y fauna',
    'Hiking & Lakes':'Senderismo y lagos','Hiking & TMB':'Senderismo y TMB',
    'Hiking & Teide':'Senderismo y Teide','Mountain Biking & Hiking':'BTT y senderismo',
    'Cycling':'Ciclismo','Cycling & Hiking':'Ciclismo y senderismo',
    'Cycling & Canals':'Ciclismo y canales','Cycling & Countryside':'Ciclismo por el campo',
    'Cycling & Villages':'Ciclismo y pueblos','Cycling & Districts':'Ciclismo y barrios',
    'Rock Climbing':'Escalada','Climbing & Bouldering':'Escalada y boulder',
    'Bouldering':'Boulder','Trekking':'Senderismo','Trekking & Nature':'Senderismo y naturaleza',
    'Via Ferrata':'Vía ferrata','Hot Air Balloon':'Globo aerostático',
    'Hot Air Balloons':'Globos aerostáticos','Hot air balloon ride':'Vuelo en globo',
    'Paragliding':'Parapente','Bungee jumping':'Puenting',
    'Photography':'Fotografía','Sport':'Deporte','Adventure Sports':'Deportes de aventura',
    'Stargazing':'Astronomía','Astronomy':'Astronomía',
    'Kayaking & Canyoning':'Kayak y barranquismo','Kayaking & Caves':'Kayak y cuevas',
    'Mangroves & Kayaking':'Manglares y kayak',
    'Alpine Skiing':'Esquí alpino','Alpine skiing':'Esquí alpino','Skiing':'Esquí',
    'Skiing & Mountaineering':'Esquí y montañismo','Skiing 2h away':'Esquí a 2h',
    'Mountains & Skiing':'Montañas y esquí','Andes & Skiing':'Andes y esquí',
    'Rainforest':'Selva tropical','Rainforest & waterfalls':'Selva tropical y cascadas',
    'Jungle & Wildlife':'Selva y fauna','Cloud forest':'Bosque nublado',
    'Ecotourism':'Ecoturismo','Ecotourism & Rainforest':'Ecoturismo y selva tropical',
    'Nature':'Naturaleza','Nature & Forests':'Naturaleza y bosques',
    'Landscapes':'Paisajes','Landscapes & Nature':'Paisajes y naturaleza',
    'Wild Nature':'Naturaleza salvaje','Wild beaches':'Playas salvajes',
    'Deserted beaches':'Playas desiertas','Deserted Beaches':'Playas desiertas',
    'Hot Springs':'Aguas termales','Thermal Baths':'Baños termales',
    'Geysers & Geothermal':'Géiseres y geotermia','Geysers & hot springs':'Géiseres y termas',
    'Glaciers & fjords':'Glaciares y fiordos','Fjords':'Fiordos',
    'Waterfalls':'Cascadas','Unique biodiversity':'Biodiversidad única',
    'Tropical gardens':'Jardines tropicales','Botanical gardens':'Jardines botánicos',
    'Gardens & Flowers':'Jardines y flores','Lavender':'Lavanda',
    'Parks & Nature':'Parques y naturaleza','National park & hiking':'Parque nacional y senderismo',
    'Archipelago':'Archipiélago','Islands':'Islas','Coast & Islands':'Costa e islas',
    'Culture':'Cultura','Culture & Heritage':'Cultura y patrimonio',
    'Culture & Museums':'Cultura y museos','Culture & Music':'Cultura y música',
    'Culture & Temples':'Cultura y templos','Culture & Fado':'Cultura y fado',
    'Culture & Mosques':'Cultura y mezquitas',
    'Heritage':'Patrimonio','History':'Historia','History & Museums':'Historia y museos',
    'Historical Sites':'Sitios históricos','Architecture':'Arquitectura',
    'Architecture & Culture':'Arquitectura y cultura','Design & Architecture':'Diseño y arquitectura',
    'Art & Architecture':'Arte y arquitectura','Art & Galleries':'Arte y galerías',
    'Art & Crafts':'Arte y artesanía','Street Art':'Arte urbano',
    'Crafts':'Artesanía','Museums':'Museos','Museums & Culture':'Museos y cultura',
    'Old Town':'Casco antiguo','Medieval Old Town':'Casco antiguo medieval',
    'UNESCO Old Town':'Casco antiguo UNESCO','UNESCO Heritage':'Patrimonio UNESCO',
    'Colonial Old Town':'Casco antiguo colonial','Historic District':'Distrito histórico',
    'Historic center':'Centro histórico','Ancient Heritage':'Patrimonio antiguo',
    'Temples':'Templos','Temples & Culture':'Templos y cultura',
    'Mayan Ruins':'Ruinas mayas','Inca Trail':'Camino del Inca',
    'Roman Heritage':'Patrimonio romano','Archaeology':'Arqueología',
    'Medina':'Medina','Medina & Souks':'Medina y zocos','Walled City':'Ciudad amurallada',
    'Gastronomy':'Gastronomía','Food & Dining':'Gastronomía','Food & Wine':'Gastronomía y vino',
    'Food & Tapas':'Gastronomía y tapas','Food Scene':'Escena gastronómica',
    'Street Food':'Comida callejera','Street Food & Markets':'Comida callejera y mercados',
    'Night Market':'Mercado nocturno','Night Markets':'Mercados nocturnos',
    'Seafood':'Mariscos','Wine & Food':'Vino y gastronomía','Wine':'Vino',
    'Wine Route':'Ruta del vino','Wine Tourism':'Turismo enológico',
    'Wine tasting':'Cata de vinos','Vineyards':'Viñedos','Beer':'Cerveza',
    'Chocolate':'Chocolate','Coffee & Culture':'Café y cultura',
    'Coffee Tours':'Rutas del café','Coffee Triangle':'Triángulo del café',
    'Tea Plantations':'Plantaciones de té','Tea plantations':'Plantaciones de té',
    'Pintxos':'Pintxos','Tapas & Nightlife':'Tapas y vida nocturna',
    'Free Tapas':'Tapas gratis','Paella & Food':'Paella y gastronomía',
    'Spice Tour':'Tour de especias',
    'Festivals':'Festivales','Festivals & Culture':'Festivales y cultura',
    'Festival':'Festival','Carnival':'Carnaval','Music':'Música',
    'Music & Culture':'Música y cultura','Music & Nightlife':'Música y vida nocturna',
    'Music Scene':'Escena musical','Classical Music':'Música clásica',
    'Blues & Jazz':'Blues y jazz','Flamenco':'Flamenco','Tango':'Tango',
    'Salsa & Nightlife':'Salsa y vida nocturna','Mardi Gras':'Mardi Gras',
    'Christmas':'Navidad','Christmas Market':'Mercado navideño',
    'Christmas Markets':'Mercados navideños','Christmas & Markets':'Navidad y mercados',
    'Christmas & Snow':'Navidad y nieve','Winter Carnival':'Carnaval de invierno',
    'Day of the Dead':'Día de los Muertos','Semana Santa':'Semana Santa',
    'Cherry Blossoms':'Flores de cerezo','Northern Lights':'Auroras boreales',
    'Midnight Sun':'Sol de medianoche','Midnight sun':'Sol de medianoche',
    'Autumn Foliage':'Follaje otoñal','Fall Foliage':'Follaje otoñal',
    'Massage & Wellness':'Masaje y bienestar','Ayurveda':'Ayurveda',
    'Mud Baths':'Baños de barro','Sulphur Baths':'Baños de azufre',
    'Day Trips':'Excursiones','Ecotourism':'Ecoturismo',
    'Sunsets':'Atardeceres','Sunset':'Atardecer','Stargazing':'Astronomía',
    'Spirituality':'Espiritualidad','Scenic Train':'Tren panorámico',
    'Fashion & Shopping':'Moda y compras','Football':'Fútbol','Golf':'Golf',
    'Theme Parks':'Parques temáticos','Duty-Free':'Duty-Free',
    'Volcanic Hiking':'Senderismo volcánico','Volcanic Beaches':'Playas volcánicas',
    'Volcanic beaches':'Playas volcánicas',
    'Polynesian culture':'Cultura polinesia',
    'Indigenous Markets':'Mercados indígenas','Ethnic Trekking':'Senderismo étnico',
    'Water Puppets':'Títeres acuáticos',
    'Snorkeling & reefs': 'Snorkel y arrecifes',
    'Birdwatching': 'Observación de aves',
    'Kayak & Island Hopping': 'Kayak e island hopping',
    'Subarctic Hiking': 'Senderismo subártico',
    'Serra de Tramuntana': 'Serra de Tramuntana',
    'Machu Picchu': 'Machu Picchu',
    'Rainbow Mountain': 'Montaña de Colores',
    'Inca City': 'Ciudad inca',
}

def translate_title(t):
    return TITLE_EXACT.get(t, t)

def translate_text(text):
    if '—' not in text:
        return text
    parts = text.split('—', 1)
    prefix = parts[0].strip()
    desc = parts[1].strip()
    tp = SEASON_MAP.get(prefix, None)
    if not tp:
        tp = prefix
        for en, es in MONTH_FULL.items():
            tp = re.sub(r'\b' + re.escape(en) + r'\b', es, tp)
        for en, es in MONTH_SHORT.items():
            tp = re.sub(r'\b' + re.escape(en) + r'\.?\b', es, tp)
        tp = tp.replace(' or ', ' o ')
        if tp:
            tp = tp[0].upper() + tp[1:]
    # Minimal desc: just 'and' → 'y'
    desc = re.sub(r'\band\b', 'y', desc)
    return f"{tp} — {desc}"

rows = list(csv.DictReader(open('data/cards_en.csv', encoding='utf-8-sig')))
translated = sum(1 for r in rows if translate_title(r['title']) != r['title'])

with open('data/cards_es.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=['slug','icon','title','text'])
    w.writeheader()
    for row in rows:
        w.writerow({'slug':row['slug'],'icon':row['icon'],
                    'title':translate_title(row['title']),
                    'text':translate_text(row['text'])})

print(f"✅ Generated data/cards_es.csv ({len(rows)} rows)")
print(f"   Titles translated: {translated}/{len(rows)} ({100*translated//len(rows)}%)")

es_rows = list(csv.DictReader(open('data/cards_es.csv', encoding='utf-8')))
for slug in ['chicago','bali','paris','dubai']:
    cards = [r for r in es_rows if r['slug'] == slug]
    print(f"\n{slug}:")
    for r in cards:
        print(f"  {r['icon']} {r['title']}: {r['text'][:75]}")
