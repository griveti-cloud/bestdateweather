#!/usr/bin/env python3
"""
Replace 176 template-based project cards with hand-crafted specific content.
Updates: data/cards.csv, data/cards_en.csv
Then regenerate all pages.
"""
import csv, os

DATA = 'data'

# Format: slug → [(icon, titre_fr, texte_fr, title_en, text_en), ...]
# Every destination gets 4-6 unique cards with specific places, dates, activities.

SPECIFIC_CARDS = {
    # ══════════════════════════════════════════════════════════════════
    # AFRIQUE & OCÉAN INDIEN
    # ══════════════════════════════════════════════════════════════════
    'cap-vert': [
        ('🏖️', 'Plage & windsurf', "Novembre-juin — Sal et Boa Vista, alizés constants et plages infinies.", 'Beach & Windsurfing', "November–June — Sal and Boa Vista, constant trade winds and endless beaches."),
        ('🌋', 'Randonnée volcanique', "Novembre-mai — ascension du Pico do Fogo (2829m) et cratère habité.", 'Volcanic Hiking', "November–May — Pico do Fogo ascent (2,829m) and inhabited crater."),
        ('🎵', 'Musique & culture', "Toute l\'année — morna, coladeira et héritage de Cesária Évora à Mindelo.", 'Music & Culture', "Year-round — morna, coladeira and Cesária Évora\'s legacy in Mindelo."),
        ('🤿', 'Plongée', "Juin-novembre — eaux chaudes, raies manta et tortues à Sal.", 'Diving', "June–November — warm waters, manta rays and turtles off Sal."),
    ],
    'dakar': [
        ('🏖️', 'Plages & surf', "Novembre-mai — Ngor, Yoff et spots de surf de la presqu\'île.", 'Beaches & Surf', "November–May — Ngor, Yoff and peninsula surf spots."),
        ('🏛️', 'Île de Gorée', "Toute l\'année — Maison des Esclaves, musées et architecture coloniale.", 'Gorée Island', "Year-round — House of Slaves, museums and colonial architecture."),
        ('🎵', 'Musique & vie nocturne', "Toute l\'année — mbalax, bars de la corniche et scène musicale vibrante.", 'Music & Nightlife', "Year-round — mbalax, corniche bars and vibrant music scene."),
        ('🍽️', 'Gastronomie sénégalaise', "Toute l\'année — thiéboudienne, yassa et street food du marché Sandaga.", 'Senegalese Food', "Year-round — thiéboudienne, yassa and Sandaga market street food."),
    ],
    'diani': [
        ('🏖️', 'Plage & farniente', "Janvier-mars ou juillet-octobre — sable blanc, cocotiers et eau turquoise.", 'Beach & Relaxation', "January–March or July–October — white sand, palm trees and turquoise water."),
        ('🤿', 'Plongée & snorkeling', "Octobre-mars — récif de Kisite-Mpunguti, dauphins et tortues.", 'Diving & Snorkelling', "October–March — Kisite-Mpunguti reef, dolphins and turtles."),
        ('🐘', 'Safari côtier', "Juin-octobre — Shimba Hills à 30 min, éléphants et antilopes.", 'Coastal Safari', "June–October — Shimba Hills 30 min away, elephants and antelopes."),
        ('🏄', 'Kitesurf', "Janvier-mars — vent constant, eaux plates du lagon.", 'Kitesurfing', "January–March — constant wind, flat lagoon waters."),
    ],
    'kenya': [
        ('🦁', 'Safari Masai Mara', "Juillet-octobre — grande migration des gnous, Big Five.", 'Masai Mara Safari', "July–October — great wildebeest migration, Big Five."),
        ('🏖️', 'Côte de l\'océan Indien', "Janvier-mars — Diani, Watamu et archipel de Lamu.", 'Indian Ocean Coast', "January–March — Diani, Watamu and Lamu archipelago."),
        ('🏔️', 'Mont Kenya', "Janvier-mars ou juillet-octobre — trek au deuxième sommet d\'Afrique.", 'Mount Kenya', "January–March or July–October — trek to Africa\'s second summit."),
        ('🐦', 'Observation oiseaux', "Novembre-avril — lac Nakuru, lac Naivasha et vallée du Rift.", 'Birdwatching', "November–April — Lake Nakuru, Lake Naivasha and the Rift Valley."),
        ('👨‍👩‍👧', 'Famille', "Juillet-octobre — safaris familiaux, lodges et plage ensuite.", 'Family', "July–October — family safaris, lodges then beach time."),
    ],
    'madagascar': [
        ('🦎', 'Faune endémique', "Avril-novembre — lémuriens, caméléons et parc de Ranomafana.", 'Endemic Wildlife', "April–November — lemurs, chameleons and Ranomafana park."),
        ('🏖️', 'Plages & îles', "Mai-novembre — Nosy Iranja, Sainte-Marie et côte ouest.", 'Beaches & Islands', "May–November — Nosy Iranja, Sainte-Marie and the west coast."),
        ('🌳', 'Allée des Baobabs', "Mai-septembre — paysage iconique à Morondava, couchers de soleil.", 'Avenue of Baobabs', "May–September — iconic landscape in Morondava, sunsets."),
        ('🥾', 'Trekking', "Avril-octobre — Tsingy de Bemaraha, Isalo et Andringitra.", 'Trekking', "April–October — Tsingy de Bemaraha, Isalo and Andringitra."),
    ],
    'namibie': [
        ('🏜️', 'Sossusvlei & dunes', "Mai-octobre — dunes rouges au lever du soleil, Dead Vlei.", 'Sossusvlei & Dunes', "May–October — red dunes at sunrise, Dead Vlei."),
        ('🦁', 'Safari Etosha', "Juin-novembre — points d\'eau, lions, éléphants et rhinocéros.", 'Etosha Safari', "June–November — waterholes, lions, elephants and rhinos."),
        ('💀', 'Skeleton Coast', "Mai-septembre — épaves, otaries et paysages lunaires.", 'Skeleton Coast', "May–September — shipwrecks, seals and lunar landscapes."),
        ('🌌', 'Astronomie', "Mai-octobre — NamibRand, l\'un des ciels les plus purs au monde.", 'Stargazing', "May–October — NamibRand, one of the world\'s purest skies."),
        ('👨‍👩‍👧', 'Famille', "Juillet-août — safaris sûrs, routes praticables et lodges familiaux.", 'Family', "July–August — safe safaris, good roads and family lodges."),
    ],
    'nosybe': [
        ('🏖️', 'Plages & lagon', "Mai-novembre — Andilana, sable blanc et eaux turquoise.", 'Beaches & Lagoon', "May–November — Andilana, white sand and turquoise waters."),
        ('🐋', 'Baleines à bosse', "Juillet-septembre — observation depuis Nosy Be et Sainte-Marie.", 'Humpback Whales', "July–September — whale watching from Nosy Be and Sainte-Marie."),
        ('🤿', 'Plongée', "Avril-décembre — récifs, requins-baleines (oct-déc) et Nosy Tanikely.", 'Diving', "April–December — reefs, whale sharks (Oct–Dec) and Nosy Tanikely."),
        ('🌿', 'Ylang-ylang & épices', "Toute l\'année — distilleries, vanille et plantations tropicales.", 'Ylang-Ylang & Spices', "Year-round — distilleries, vanilla and tropical plantations."),
    ],
    'senegal': [
        ('🦁', 'Parc du Niokolo-Koba', "Décembre-avril — savane, faune et randonnée.", 'Niokolo-Koba Park', "December–April — savanna, wildlife and hiking."),
        ('🏖️', 'Plages atlantiques', "Novembre-mai — Saly, Cap Skirring et petite côte.", 'Atlantic Beaches', "November–May — Saly, Cap Skirring and the Petite Côte."),
        ('🛶', 'Sine-Saloum', "Novembre-avril — mangroves en pirogue, oiseaux migrateurs.", 'Sine-Saloum', "November–April — mangrove pirogue trips, migratory birds."),
        ('🎵', 'Culture & musique', "Toute l\'année — Saint-Louis du Sénégal, festival de jazz.", 'Culture & Music', "Year-round — Saint-Louis, jazz festival."),
        ('👨‍👩‍👧', 'Famille', "Novembre-mars — plages sécurisées, réserves animalières et accueil.", 'Family', "November–March — safe beaches, wildlife reserves and hospitality."),
    ],
    'tanzanie': [
        ('🦁', 'Serengeti & migration', "Juin-octobre — grande migration, Big Five en concentrations maximales.", 'Serengeti & Migration', "June–October — great migration, peak Big Five concentrations."),
        ('🏔️', 'Kilimandjaro', "Janvier-mars ou juin-octobre — saison sèche, meilleures conditions de trek.", 'Kilimanjaro', "January–March or June–October — dry season, best trekking conditions."),
        ('🏖️', 'Zanzibar', "Juin-octobre ou décembre-février — plages, épices et Stone Town.", 'Zanzibar', "June–October or December–February — beaches, spices and Stone Town."),
        ('🌳', 'Ngorongoro', "Juin-octobre — cratère, flamants roses et densité animale unique.", 'Ngorongoro', "June–October — crater, flamingos and unique animal density."),
        ('👨‍👩‍👧', 'Famille', "Juillet-août — safari + Zanzibar, combo classique familial.", 'Family', "July–August — safari + Zanzibar, classic family combo."),
    ],
    'rodrigues': [
        ('🏖️', 'Lagon & plages', "Octobre-avril — baignade, sable fin et eaux peu profondes.", 'Lagoon & Beaches', "October–April — swimming, fine sand and shallow waters."),
        ('🥾', 'Randonnée', "Mai-novembre — sentiers côtiers, grottes et réserves naturelles.", 'Hiking', "May–November — coastal trails, caves and nature reserves."),
        ('🐙', 'Pêche & gastronomie', "Toute l\'année — ourite (poulpe séché), cuisine créole mauricienne.", 'Fishing & Food', "Year-round — ourite (dried octopus), Mauritian Creole cuisine."),
        ('🐢', 'Tortues géantes', "Toute l\'année — réserve François Leguat et faune endémique.", 'Giant Tortoises', "Year-round — François Leguat reserve and endemic wildlife."),
    ],
    'martinique': [
        ('🏖️', 'Plages du sud', "Décembre-avril — Salines, Diamant et Anse Dufour.", 'Southern Beaches', "December–April — Salines, Diamant and Anse Dufour."),
        ('🌋', 'Montagne Pelée', "Janvier-avril — randonnée au sommet, forêt tropicale humide.", 'Mount Pelée', "January–April — summit hike, tropical rainforest."),
        ('🥃', 'Rhum & distilleries', "Toute l\'année — route des rhums, Saint-James, Clément et Depaz.", 'Rum & Distilleries', "Year-round — rum trail, Saint-James, Clément and Depaz."),
        ('🤿', 'Plongée', "Décembre-mai — Rocher du Diamant, épaves de Saint-Pierre.", 'Diving', "December–May — Diamond Rock, Saint-Pierre wrecks."),
        ('👨‍👩‍👧', 'Famille', "Février-avril — plages calmes, jardin de Balata et zoo de Martinique.", 'Family', "February–April — calm beaches, Balata Garden and Martinique zoo."),
    ],
    'guadeloupe': [
        ('🏖️', 'Plages de Grande-Terre', "Décembre-avril — Sainte-Anne, Saint-François et Pointe des Châteaux.", 'Grande-Terre Beaches', "December–April — Sainte-Anne, Saint-François and Pointe des Châteaux."),
        ('🌿', 'Forêt tropicale', "Toute l\'année — chutes du Carbet, Soufrière et parc national.", 'Rainforest', "Year-round — Carbet Falls, La Soufrière and national park."),
        ('🤿', 'Réserve Cousteau', "Décembre-mai — plongée sur récif, tortues et coraux de Malendure.", 'Cousteau Reserve', "December–May — reef diving, turtles and Malendure corals."),
        ('🍽️', 'Gastronomie créole', "Toute l\'année — bokit, colombo, accras et ti\'punch.", 'Creole Food', "Year-round — bokit, colombo, accras and ti\'punch."),
        ('👨‍👩‍👧', 'Famille', "Février-avril — plages lagon, aquarium et balade en mangrove.", 'Family', "February–April — lagoon beaches, aquarium and mangrove trips."),
    ],
    'mayotte': [
        ('🐢', 'Tortues marines', "Mai-novembre — ponte sur les plages (juil-nov), snorkeling avec tortues vertes.", 'Sea Turtles', "May–November — nesting on beaches (Jul–Nov), snorkelling with green turtles."),
        ('🤿', 'Lagon & plongée', "Août-novembre — visibilité maximale dans le plus grand lagon fermé au monde.", 'Lagoon & Diving', "August–November — peak visibility in the world\'s largest enclosed lagoon."),
        ('🐋', 'Baleines à bosse', "Juillet-octobre — observation dans le lagon et la passe de Longoni.", 'Humpback Whales', "July–October — spotting in the lagoon and Longoni pass."),
        ('🏖️', 'Plages', "Mai-novembre — N\'Gouja, Saziley et îlot de sable blanc.", 'Beaches', "May–November — N\'Gouja, Saziley and white sand islet."),
    ],
    'guyane': [
        ('🚀', 'Centre spatial', "Toute l\'année — lanceurs Ariane depuis Kourou, musée de l\'Espace.", 'Space Centre', "Year-round — Ariane launches from Kourou, Space Museum."),
        ('🌳', 'Amazonie', "Juillet-novembre — pirogue sur les fleuves, faune et villages amérindiens.", 'Amazonia', "July–November — river pirogue trips, wildlife and Amerindian villages."),
        ('🐢', 'Tortues luth', "Avril-juillet — ponte sur les plages d\'Awala-Yalimapo.", 'Leatherback Turtles', "April–July — nesting on Awala-Yalimapo beaches."),
        ('🏝️', 'Îles du Salut', "Août-novembre — anciens bagnes, faune tropicale et histoire.", 'Salvation Islands', "August–November — former penal colonies, tropical wildlife and history."),
    ],
    'saint-barthelemy': [
        ('🏖️', 'Plages', "Décembre-mai — Saint-Jean, Colombier et Gouverneur.", 'Beaches', "December–May — Saint-Jean, Colombier and Gouverneur."),
        ('🍽️', 'Gastronomie française', "Toute l\'année — bistrots étoilés, cuisine créole et produits importés.", 'French Gastronomy', "Year-round — starred bistros, Creole cuisine and imported produce."),
        ('⛵', 'Voile & yachting', "Décembre-avril — régates, charters et mouillages privés.", 'Sailing & Yachting', "December–April — regattas, charters and private moorings."),
        ('🛍️', 'Shopping duty-free', "Toute l\'année — Gustavia, boutiques de luxe sans taxes.", 'Duty-Free Shopping', "Year-round — Gustavia, tax-free luxury boutiques."),
    ],
    'saint-lucie': [
        ('🏔️', 'Pitons & randonnée', "Décembre-avril — Gros Piton trek, vues spectaculaires.", 'Pitons & Hiking', "December–April — Gros Piton trek, spectacular views."),
        ('🤿', 'Plongée', "Décembre-mai — récif d\'Anse Chastanet, Soufrière Marine Reserve.", 'Diving', "December–May — Anse Chastanet reef, Soufrière Marine Reserve."),
        ('♨️', 'Sources chaudes', "Toute l\'année — Sulphur Springs, bains de boue volcanique.", 'Hot Springs', "Year-round — Sulphur Springs, volcanic mud baths."),
        ('🏖️', 'Plages', "Décembre-avril — Anse des Pitons, Reduit Beach et Marigot Bay.", 'Beaches', "December–April — Anse des Pitons, Reduit Beach and Marigot Bay."),
        ('👨‍👩‍👧', 'Famille', "Février-avril — plages calmes, tyrolienne dans la canopée et chocolat.", 'Family', "February–April — calm beaches, canopy zip-lining and chocolate."),
    ],
    'saint-martin': [
        ('🏖️', 'Plages', "Décembre-avril — Orient Bay côté français, Maho Beach côté néerlandais.", 'Beaches', "December–April — Orient Bay (French side), Maho Beach (Dutch side)."),
        ('🍽️', 'Gastronomie binationale', "Toute l\'année — lolos français, restaurants de Grand Case et cuisine caribéenne.", 'Binational Food', "Year-round — French lolos, Grand Case restaurants and Caribbean cuisine."),
        ('⛵', 'Sports nautiques', "Décembre-mai — voile, kitesurf et excursions vers Anguilla.", 'Water Sports', "December–May — sailing, kitesurfing and day trips to Anguilla."),
        ('🛍️', 'Shopping duty-free', "Toute l\'année — Philipsburg (néerlandais), bijoux, alcool et électronique.", 'Duty-Free Shopping', "Year-round — Philipsburg (Dutch side), jewellery, spirits and electronics."),
    ],
    'saint-pierre-et-miquelon': [
        ('🐦', 'Ornithologie', "Mai-août — colonies de macareux, fous de Bassan et sternes.", 'Birdwatching', "May–August — puffin colonies, gannets and terns."),
        ('🏛️', 'Patrimoine basque & breton', "Toute l\'année — architecture, musée Heritage et culture de pêcheurs.", 'Basque & Breton Heritage', "Year-round — architecture, Heritage Museum and fishing culture."),
        ('🐋', 'Observation baleines', "Juin-septembre — baleines à bosse et rorquals au large.", 'Whale Watching', "June–September — humpback and fin whales offshore."),
        ('🥾', 'Randonnée subarctique', "Juin-septembre — tourbières, littoral sauvage et Miquelon-Langlade.", 'Subarctic Hiking', "June–September — peatlands, wild coastline and Miquelon-Langlade."),
    ],

    # ══════════════════════════════════════════════════════════════════
    # ASIE
    # ══════════════════════════════════════════════════════════════════
    'baie-halong': [
        ('🚢', 'Croisière en jonque', "Octobre-avril — nuit sur la baie, grottes karstiques et coucher de soleil.", 'Junk Boat Cruise', "October–April — overnight on the bay, karst caves and sunset."),
        ('🏖️', 'Plages & îles', "Mai-septembre — Cat Ba, kayak et plages moins fréquentées.", 'Beaches & Islands', "May–September — Cat Ba, kayaking and less crowded beaches."),
        ('🧗', 'Escalade', "Octobre-mars — Cat Ba, falaises calcaires au-dessus de l\'eau.", 'Rock Climbing', "October–March — Cat Ba, limestone cliffs above the water."),
        ('📸', 'Photographie', "Octobre-novembre — brumes matinales, lumière dorée sur les pitons.", 'Photography', "October–November — morning mists, golden light on the pinnacles."),
    ],
    'boracay': [
        ('🏖️', 'White Beach', "Novembre-mai — 4 km de sable blanc, couchers de soleil iconiques.", 'White Beach', "November–May — 4 km of white sand, iconic sunsets."),
        ('🏄', 'Kitesurf & sports', "Novembre-avril — Bulabog Beach, vent régulier pour kite et windsurf.", 'Kitesurfing & Sports', "November–April — Bulabog Beach, steady wind for kite and windsurf."),
        ('🤿', 'Plongée', "Novembre-mai — Crocodile Island, Yapak et coraux préservés.", 'Diving', "November–May — Crocodile Island, Yapak and preserved corals."),
        ('🎉', 'Vie nocturne', "Toute l\'année — bars sur la plage, feu de camp et soirées tropicales.", 'Nightlife', "Year-round — beachfront bars, bonfires and tropical parties."),
    ],
    'borneo': [
        ('🦧', 'Orangs-outans', "Mars-octobre — Sepilok, Danum Valley et Kinabatangan.", 'Orangutans', "March–October — Sepilok, Danum Valley and Kinabatangan."),
        ('🤿', 'Plongée Sipadan', "Avril-décembre — l\'un des meilleurs sites de plongée au monde.", 'Sipadan Diving', "April–December — one of the world\'s best dive sites."),
        ('🏔️', 'Mont Kinabalu', "Février-avril — ascension du plus haut sommet d\'Asie du Sud-Est.", 'Mount Kinabalu', "February–April — climbing Southeast Asia\'s highest peak."),
        ('🌿', 'Grottes de Mulu', "Mars-octobre — plus grand réseau karstique au monde, UNESCO.", 'Mulu Caves', "March–October — world\'s largest karst network, UNESCO-listed."),
    ],
    'busan': [
        ('🏖️', 'Haeundae Beach', "Juin-septembre — plage urbaine, festivals et fruits de mer.", 'Haeundae Beach', "June–September — urban beach, festivals and seafood."),
        ('🛕', 'Temple Haedong Yonggungsa', "Toute l\'année — temple bouddhiste en bord de mer, unique en Corée.", 'Haedong Yonggungsa Temple', "Year-round — seaside Buddhist temple, unique in Korea."),
        ('🍽️', 'Marché Jagalchi', "Toute l\'année — plus grand marché de poisson de Corée, sashimi frais.", 'Jagalchi Market', "Year-round — Korea\'s largest fish market, fresh sashimi."),
        ('🌸', 'Festival des cerisiers', "Avril — fleuraison à Dalmaji Hill et parc Samnak.", 'Cherry Blossom Festival', "April — blooming at Dalmaji Hill and Samnak Park."),
        ('🎬', 'BIFF', "Octobre — Busan International Film Festival, le plus grand d\'Asie.", 'BIFF', "October — Busan International Film Festival, Asia\'s largest."),
    ],
    'cambodge': [
        ('🛕', 'Angkor Wat', "Novembre-mars — temples au lever du soleil, Bayon et Ta Prohm.", 'Angkor Wat', "November–March — sunrise temples, Bayon and Ta Prohm."),
        ('🏖️', 'Côte & îles', "Novembre-mai — Koh Rong, Koh Rong Samloem et Sihanoukville.", 'Coast & Islands', "November–May — Koh Rong, Koh Rong Samloem and Sihanoukville."),
        ('🍽️', 'Cuisine khmère', "Toute l\'année — amok, lok lak et cours de cuisine à Siem Reap.", 'Khmer Cuisine', "Year-round — amok, lok lak and cooking classes in Siem Reap."),
        ('🏛️', 'Phnom Penh', "Novembre-février — Palais Royal, marchés et rivières du Mékong.", 'Phnom Penh', "November–February — Royal Palace, markets and Mekong rivers."),
        ('👨‍👩‍👧', 'Famille', "Décembre-février — Angkor accessible, plages et Phnom Kulen.", 'Family', "December–February — accessible Angkor, beaches and Phnom Kulen."),
    ],
    'canggu': [
        ('🏄', 'Surf', "Avril-octobre — Echo Beach, Batu Bolong et vagues régulières.", 'Surfing', "April–October — Echo Beach, Batu Bolong and consistent waves."),
        ('💻', 'Digital nomad', "Toute l\'année — coworkings, cafés Wi-Fi et communauté internationale.", 'Digital Nomad', "Year-round — coworking spaces, Wi-Fi cafés and international community."),
        ('🧘', 'Yoga & bien-être', "Toute l\'année — retraites, spas et alimentation healthy.", 'Yoga & Wellness', "Year-round — retreats, spas and healthy dining."),
        ('🍽️', 'Food scene', "Toute l\'année — brunch, smoothie bowls et restaurants fusion.", 'Food Scene', "Year-round — brunch, smoothie bowls and fusion restaurants."),
    ],
    'cebu': [
        ('🐋', 'Requins-baleines d\'Oslob', "Toute l\'année — observation éthique des requins-baleines.", 'Oslob Whale Sharks', "Year-round — ethical whale shark encounters."),
        ('🏖️', 'Plages & îles', "Décembre-mai — Bantayan, Malapascua et île de Camotes.", 'Beaches & Islands', "December–May — Bantayan, Malapascua and Camotes Island."),
        ('💧', 'Kawasan Falls', "Toute l\'année — canyoning, cascades turquoise et jungle.", 'Kawasan Falls', "Year-round — canyoneering, turquoise waterfalls and jungle."),
        ('🤿', 'Plongée', "Décembre-mai — Moalboal (sardine run), Malapascua (requins-renards).", 'Diving', "December–May — Moalboal (sardine run), Malapascua (thresher sharks)."),
    ],
    'chiang-mai': [
        ('🛕', 'Temples', "Novembre-février — Doi Suthep, Wat Chedi Luang et centaines de temples.", 'Temples', "November–February — Doi Suthep, Wat Chedi Luang and hundreds of temples."),
        ('🎉', 'Festivals', "Novembre — Yi Peng (lanternes). Avril — Songkran (eau).", 'Festivals', "November — Yi Peng (lanterns). April — Songkran (water)."),
        ('🍽️', 'Street food & marchés', "Toute l\'année — Warorot, Night Bazaar et khao soi.", 'Street Food & Markets', "Year-round — Warorot, Night Bazaar and khao soi."),
        ('🥾', 'Trek & nature', "Novembre-février — montagnes du nord, villages ethniques et cascades.", 'Trekking & Nature', "November–February — northern mountains, hill tribe villages and waterfalls."),
        ('💆', 'Massage & bien-être', "Toute l\'année — écoles de massage, spas et retraites méditation.", 'Massage & Wellness', "Year-round — massage schools, spas and meditation retreats."),
    ],
    'da-lat': [
        ('☕', 'Café & terroirs', "Toute l\'année — café weasel, plantations d\'altitude et cafés originaux.", 'Coffee & Terroirs', "Year-round — weasel coffee, highland plantations and quirky cafés."),
        ('💧', 'Cascades', "Juin-novembre — Datanla, Elephant Falls et Pongour.", 'Waterfalls', "June–November — Datanla, Elephant Falls and Pongour."),
        ('🌺', 'Jardins & fleurs', "Décembre-mars — floraison, vallée de l\'Amour et parc des fleurs.", 'Gardens & Flowers', "December–March — blooming season, Valley of Love and flower park."),
        ('🚲', 'Vélo', "Novembre-avril — collines de thé, villages et temples en altitude.", 'Cycling', "November–April — tea hills, villages and highland temples."),
    ],
    'da-nang': [
        ('🏖️', 'My Khe Beach', "Mai-septembre — l\'une des plus belles plages d\'Asie, surf possible.", 'My Khe Beach', "May–September — one of Asia\'s finest beaches, surfing possible."),
        ('🌉', 'Bà Nà Hills', "Février-mai — Golden Bridge, parc à thèmes et brumes matinales.", 'Bà Nà Hills', "February–May — Golden Bridge, theme park and morning mists."),
        ('🛕', 'Montagnes de Marbre', "Toute l\'année — grottes, temples bouddhistes et panoramas.", 'Marble Mountains', "Year-round — caves, Buddhist temples and panoramic views."),
        ('🍽️', 'Street food', "Toute l\'année — mì quảng, bánh xèo et marchés nocturnes.", 'Street Food', "Year-round — mì quảng, bánh xèo and night markets."),
    ],
    'delhi': [
        ('🏛️', 'Forts moghols', "Octobre-mars — Fort Rouge, Qutb Minar et Humayun Tomb.", 'Mughal Forts', "October–March — Red Fort, Qutb Minar and Humayun\'s Tomb."),
        ('🍽️', 'Street food', "Octobre-mars — Chandni Chowk, paratha, chaat et tandoori.", 'Street Food', "October–March — Chandni Chowk, paratha, chaat and tandoori."),
        ('🛍️', 'Shopping & bazars', "Toute l\'année — Connaught Place, Dilli Haat et marchés de Khan.", 'Shopping & Bazaars', "Year-round — Connaught Place, Dilli Haat and Khan markets."),
        ('🕌', 'Spiritualité', "Toute l\'année — temples, mosquées, gurdwaras et Lotus Temple.", 'Spirituality', "Year-round — temples, mosques, gurdwaras and Lotus Temple."),
    ],
    'el-nido': [
        ('🏖️', 'Lagons cachés', "Décembre-mai — Big Lagoon, Small Lagoon et Secret Beach.", 'Hidden Lagoons', "December–May — Big Lagoon, Small Lagoon and Secret Beach."),
        ('🤿', 'Plongée & snorkeling', "Novembre-mai — récifs, tortues et visibilité exceptionnelle.", 'Diving & Snorkelling', "November–May — reefs, turtles and exceptional visibility."),
        ('🚣', 'Kayak & island hopping', "Décembre-mai — tours A, B, C, D entre îlots karstiques.", 'Kayak & Island Hopping', "December–May — tours A, B, C, D between karst islets."),
        ('🌅', 'Coucher de soleil', "Toute l\'année — Corong-Corong, Las Cabañas et Nacpan Beach.", 'Sunsets', "Year-round — Corong-Corong, Las Cabañas and Nacpan Beach."),
    ],
    'hanoi': [
        ('🏛️', 'Vieux quartier', "Octobre-décembre — 36 rues, lac Hoàn Kiếm et temples millénaires.", 'Old Quarter', "October–December — 36 streets, Hoàn Kiếm Lake and ancient temples."),
        ('🍜', 'Phở & street food', "Toute l\'année — phở, bún chả et café à l\'œuf dans le quartier ancien.", 'Phở & Street Food', "Year-round — phở, bún chả and egg coffee in the old quarter."),
        ('🎭', 'Marionnettes sur l\'eau', "Toute l\'année — spectacle traditionnel au théâtre Thăng Long.", 'Water Puppets', "Year-round — traditional show at Thăng Long Theatre."),
        ('🚲', 'Vélo & campagne', "Octobre-mars — excursions vers Ninh Binh et pagodes parfumées.", 'Cycling & Countryside', "October–March — day trips to Ninh Binh and Perfume Pagoda."),
    ],
    'hiroshima': [
        ('🕊️', 'Mémorial de la Paix', "Toute l\'année — Dôme Genbaku, musée et parc du Mémorial.", 'Peace Memorial', "Year-round — Genbaku Dome, museum and Memorial Park."),
        ('⛩️', 'Miyajima', "Toute l\'année — torii flottant, daims et temple Itsukushima.", 'Miyajima', "Year-round — floating torii, deer and Itsukushima shrine."),
        ('🍽️', 'Okonomiyaki', "Toute l\'année — version Hiroshima en couches, Hiroshima Okonomimura.", 'Okonomiyaki', "Year-round — layered Hiroshima-style, Okonomimura food hall."),
        ('🌸', 'Cerisiers', "Fin mars-début avril — fleuraison le long de la rivière et dans le parc.", 'Cherry Blossoms', "Late March–early April — blooming along the river and in the park."),
    ],
    'ho-chi-minh': [
        ('🏛️', 'Patrimoine', "Décembre-avril — Palais de la Réunification, Notre-Dame et poste centrale.", 'Heritage', "December–April — Reunification Palace, Notre-Dame and Central Post Office."),
        ('🍜', 'Street food', "Toute l\'année — phở, bánh mì, cơm tấm et marchés de nuit.", 'Street Food', "Year-round — phở, bánh mì, cơm tấm and night markets."),
        ('🛶', 'Delta du Mékong', "Décembre-mai — marchés flottants de Cái Bè et Cần Thơ.", 'Mekong Delta', "December–May — Cái Bè and Cần Thơ floating markets."),
        ('🏎️', 'Tunnels de Củ Chi', "Toute l\'année — réseau souterrain de 250 km, à 1h du centre.", 'Củ Chi Tunnels', "Year-round — 250 km underground network, 1h from the centre."),
    ],
    'hong-kong': [
        ('🏙️', 'Skyline & Peak', "Octobre-décembre — Victoria Peak, Star Ferry et Symphony of Lights.", 'Skyline & Peak', "October–December — Victoria Peak, Star Ferry and Symphony of Lights."),
        ('🍽️', 'Dim sum & cuisine', "Toute l\'année — Tim Ho Wan, dai pai dong et cuisine cantonaise.", 'Dim Sum & Food', "Year-round — Tim Ho Wan, dai pai dong and Cantonese cuisine."),
        ('🥾', 'Randonnée', "Octobre-mars — Dragon\'s Back, Lantau Peak et Hong Kong Trail.", 'Hiking', "October–March — Dragon\'s Back, Lantau Peak and Hong Kong Trail."),
        ('🛍️', 'Shopping', "Toute l\'année — Tsim Sha Tsui, Causeway Bay et marchés de nuit.", 'Shopping', "Year-round — Tsim Sha Tsui, Causeway Bay and night markets."),
    ],
    'java': [
        ('🌋', 'Volcans', "Avril-octobre — Bromo au lever du soleil, Ijen (lac acide bleu).", 'Volcanoes', "April–October — Bromo at sunrise, Ijen (blue acid lake)."),
        ('🛕', 'Borobudur & Prambanan', "Avril-octobre — plus grands temples bouddhiste et hindou du monde.", 'Borobudur & Prambanan', "April–October — world\'s largest Buddhist and Hindu temples."),
        ('🎭', 'Culture javanaise', "Toute l\'année — Yogyakarta, batik, wayang et gamelan.", 'Javanese Culture', "Year-round — Yogyakarta, batik, wayang and gamelan."),
        ('🍽️', 'Street food', "Toute l\'année — nasi goreng, sate et warungs de Yogya.", 'Street Food', "Year-round — nasi goreng, satay and Yogya warungs."),
    ],
    'jeju': [
        ('🌋', 'Hallasan & volcans', "Avril-mai ou octobre — ascension du sommet (1950m), couleurs automnales.", 'Hallasan & Volcanoes', "April–May or October — summit climb (1,950m), autumn colours."),
        ('🧜‍♀️', 'Haenyeo', "Toute l\'année — plongeuses traditionnelles, spectacles et marchés.", 'Haenyeo Divers', "Year-round — traditional women divers, shows and markets."),
        ('🏖️', 'Plages de lave', "Juin-août — Hyeopjae, Hamdeok et côtes volcaniques noires.", 'Lava Beaches', "June–August — Hyeopjae, Hamdeok and black volcanic coastline."),
        ('🍊', 'Mandarines & gastronomie', "Novembre-janvier — récolte mandarines, black pork BBQ et fruits de mer.", 'Tangerines & Food', "November–January — tangerine harvest, black pork BBQ and seafood."),
    ],
    'kerala': [
        ('🛶', 'Backwaters', "Septembre-mars — croisière en houseboat, rizières et villages lacustres.", 'Backwaters', "September–March — houseboat cruise, rice paddies and lakeside villages."),
        ('💆', 'Ayurveda', "Juin-septembre — cures ayurvédiques traditionnelles pendant la mousson.", 'Ayurveda', "June–September — traditional Ayurvedic treatments during monsoon."),
        ('🌿', 'Plantations de thé', "Septembre-mars — Munnar, collines verdoyantes et fabriques de thé.", 'Tea Plantations', "September–March — Munnar, green hills and tea factories."),
        ('🏖️', 'Plages', "Novembre-mars — Varkala, Kovalam et Marari Beach.", 'Beaches', "November–March — Varkala, Kovalam and Marari Beach."),
        ('🎭', 'Kathakali', "Toute l\'année — danse traditionnelle, temples et festivals de Kochi.", 'Kathakali', "Year-round — traditional dance, temples and Kochi festivals."),
    ],
    'koh-lanta': [
        ('🏖️', 'Plages désertes', "Novembre-avril — Long Beach, Kantiang Bay et Ba Kan Tieng.", 'Deserted Beaches', "November–April — Long Beach, Kantiang Bay and Ba Kan Tieng."),
        ('🤿', 'Plongée', "Novembre-avril — Koh Haa, Hin Daeng et Hin Muang.", 'Diving', "November–April — Koh Haa, Hin Daeng and Hin Muang."),
        ('🌿', 'Mangroves & kayak', "Novembre-avril — parc national de Mu Ko Lanta, kayak de mer.", 'Mangroves & Kayaking', "November–April — Mu Ko Lanta national park, sea kayaking."),
        ('👨‍👩‍👧', 'Famille', "Décembre-mars — plages sûres, rythme tranquille et prix abordables.", 'Family', "December–March — safe beaches, relaxed pace and affordable prices."),
    ],
    'koh-phi-phi': [
        ('🏖️', 'Maya Bay', "Novembre-avril — baie de The Beach, quota visiteurs limité.", 'Maya Bay', "November–April — The Beach bay, limited visitor quota."),
        ('🤿', 'Plongée', "Décembre-avril — Shark Point, Anemone Reef et épave King Cruiser.", 'Diving', "December–April — Shark Point, Anemone Reef and King Cruiser wreck."),
        ('🥾', 'Viewpoint', "Toute l\'année — montée au viewpoint, panorama 360° sur les deux baies.", 'Viewpoint', "Year-round — viewpoint climb, 360° panorama over both bays."),
        ('🎉', 'Vie nocturne', "Novembre-avril — fêtes sur la plage, fire shows et bars.", 'Nightlife', "November–April — beach parties, fire shows and bars."),
    ],
    'koh-samui': [
        ('🏖️', 'Plages', "Décembre-avril — Chaweng, Lamai et plages de la côte sud.", 'Beaches', "December–April — Chaweng, Lamai and south coast beaches."),
        ('🛕', 'Big Buddha & temples', "Toute l\'année — Wat Phra Yai, Wat Plai Laem et Secret Buddha Garden.", 'Big Buddha & Temples', "Year-round — Wat Phra Yai, Wat Plai Laem and Secret Buddha Garden."),
        ('💆', 'Spa & bien-être', "Toute l\'année — resorts spa, détox et retraites de yoga.", 'Spa & Wellness', "Year-round — spa resorts, detox and yoga retreats."),
        ('🎉', 'Full Moon Party', "Toute l\'année — Koh Phangan voisine, fête mensuelle (ferry 30 min).", 'Full Moon Party', "Year-round — neighbouring Koh Phangan, monthly party (30 min ferry)."),
        ('👨‍👩‍👧', 'Famille', "Janvier-mars — plages calmes, Aquapark et excursions Ang Thong.", 'Family', "January–March — calm beaches, Aquapark and Ang Thong excursions."),
    ],
    'koh-tao': [
        ('🤿', 'Plongée PADI', "Mars-octobre — certifications à prix réduit, 25+ sites.", 'PADI Diving', "March–October — low-cost certifications, 25+ sites."),
        ('🐢', 'Snorkeling tortues', "Toute l\'année — Shark Bay, Japanese Garden et Aow Leuk.", 'Turtle Snorkelling', "Year-round — Shark Bay, Japanese Garden and Aow Leuk."),
        ('🏖️', 'Plages', "Mars-septembre — Sairee, Freedom Beach et Tanote Bay.", 'Beaches', "March–September — Sairee, Freedom Beach and Tanote Bay."),
        ('🧗', 'Escalade & bouldering', "Mars-octobre — falaises en bord de mer, spots pour tous niveaux.", 'Climbing & Bouldering', "March–October — seaside cliffs, spots for all levels."),
    ],
    'komodo': [
        ('🦎', 'Dragons de Komodo', "Avril-décembre — observation des varans, Rinca et Komodo.", 'Komodo Dragons', "April–December — monitor lizard observation, Rinca and Komodo."),
        ('🤿', 'Plongée', "Avril-novembre — raies manta à Manta Point, courants riches.", 'Diving', "April–November — manta rays at Manta Point, nutrient-rich currents."),
        ('🏖️', 'Pink Beach', "Avril-décembre — plage de sable rose, snorkeling sur le récif.", 'Pink Beach', "April–December — pink sand beach, reef snorkelling."),
        ('🚤', 'Croisière Liveaboard', "Avril-octobre — 2-3 jours entre îles, nuits sur le bateau.", 'Liveaboard Cruise', "April–October — 2–3 days between islands, nights on the boat."),
    ],
    'krabi': [
        ('🏖️', 'Railay Beach', "Novembre-avril — accès en bateau uniquement, falaises spectaculaires.", 'Railay Beach', "November–April — boat-access only, spectacular cliffs."),
        ('🧗', 'Escalade', "Novembre-mars — plus de 700 voies sur calcaire, niveau débutant à expert.", 'Rock Climbing', "November–March — over 700 limestone routes, beginner to expert."),
        ('🏝️', 'Four Islands', "Novembre-avril — tour des 4 îles, snorkeling et plages.", 'Four Islands', "November–April — 4-island tour, snorkelling and beaches."),
        ('🌿', 'Tiger Cave Temple', "Toute l\'année — 1237 marches, panorama sur la province.", 'Tiger Cave Temple', "Year-round — 1,237 steps, panoramic provincial views."),
    ],
    'kuala-lumpur': [
        ('🏙️', 'Petronas & skyline', "Toute l\'année — tours Petronas, KL Tower et Bukit Bintang.", 'Petronas & Skyline', "Year-round — Petronas Towers, KL Tower and Bukit Bintang."),
        ('🍽️', 'Food capitals', "Toute l\'année — Jalan Alor, nasi lemak, roti canai et satay.", 'Food Capital', "Year-round — Jalan Alor, nasi lemak, roti canai and satay."),
        ('🛕', 'Batu Caves', "Toute l\'année — grottes hindoues, escalier arc-en-ciel de 272 marches.", 'Batu Caves', "Year-round — Hindu caves, 272-step rainbow staircase."),
        ('🛍️', 'Shopping', "Toute l\'année — malls climatisés, marchés et duty-free.", 'Shopping', "Year-round — air-conditioned malls, markets and duty-free."),
    ],
    'kyoto': [
        ('🌸', 'Cerisiers', "Fin mars-mi-avril — Philosophe, Maruyama Park et Kiyomizu-dera.", 'Cherry Blossoms', "Late March–mid-April — Philosopher\'s Path, Maruyama Park and Kiyomizu-dera."),
        ('🍁', 'Momiji (automne)', "Mi-novembre-début décembre — Tōfuku-ji, Eikan-dō et forêts d\'érables.", 'Autumn Foliage', "Mid-November–early December — Tōfuku-ji, Eikan-dō and maple forests."),
        ('⛩️', 'Temples & jardins zen', "Toute l\'année — Kinkaku-ji, Fushimi Inari et Ryōan-ji.", 'Temples & Zen Gardens', "Year-round — Kinkaku-ji, Fushimi Inari and Ryōan-ji."),
        ('🎎', 'Geishas de Gion', "Toute l\'année — quartier de Gion, maiko et soirées traditionnelles.", 'Gion Geishas', "Year-round — Gion district, maiko and traditional evenings."),
        ('🍵', 'Thé & gastronomie', "Toute l\'année — matcha, kaiseki et marchés de Nishiki.", 'Tea & Food', "Year-round — matcha, kaiseki and Nishiki Market."),
    ],
    'langkawi': [
        ('🏖️', 'Plages', "Décembre-mars — Cenang, Tengah et Datai Bay.", 'Beaches', "December–March — Cenang, Tengah and Datai Bay."),
        ('🌿', 'Sky Bridge & géoparc', "Toute l\'année — pont suspendu, téléphérique et mangroves UNESCO.", 'Sky Bridge & Geopark', "Year-round — suspension bridge, cable car and UNESCO mangroves."),
        ('🛍️', 'Duty-free', "Toute l\'année — alcool, chocolat et shopping détaxé.", 'Duty-Free', "Year-round — spirits, chocolate and tax-free shopping."),
        ('🤿', 'Plongée & snorkeling', "Décembre-avril — Pulau Payar, récifs et eaux claires.", 'Diving & Snorkelling', "December–April — Pulau Payar, reefs and clear waters."),
    ],
    'laos': [
        ('🛕', 'Luang Prabang', "Novembre-mars — aumône des moines, Kuang Si et temples dorés.", 'Luang Prabang', "November–March — monk alms, Kuang Si and golden temples."),
        ('🛶', 'Mékong', "Novembre-avril — croisière en slow boat, grottes de Pak Ou.", 'Mekong', "November–April — slow boat cruise, Pak Ou caves."),
        ('🧗', 'Vang Vieng', "Novembre-mars — kayak, tubing, grottes et falaises karstiques.", 'Vang Vieng', "November–March — kayaking, tubing, caves and karst cliffs."),
        ('🍽️', 'Cuisine lao', "Toute l\'année — laap, khao piak et marchés nocturnes de Vientiane.", 'Lao Cuisine', "Year-round — laap, khao piak and Vientiane night markets."),
    ],
    'luang-prabang': [
        ('🛕', 'Moines & temples', "Toute l\'année — aumône à l\'aube, Wat Xieng Thong et Mont Phousi.", 'Monks & Temples', "Year-round — dawn alms-giving, Wat Xieng Thong and Mount Phousi."),
        ('💧', 'Kuang Si Falls', "Novembre-avril — cascades turquoise, baignade et ours.", 'Kuang Si Falls', "November–April — turquoise waterfalls, swimming and bears."),
        ('🛶', 'Mékong', "Novembre-mars — croisière, grottes de Pak Ou et villages riverains.", 'Mekong', "November–March — cruise, Pak Ou caves and riverside villages."),
        ('🍽️', 'Marché nocturne', "Toute l\'année — artisanat, buffet végétarien et cuisine locale.", 'Night Market', "Year-round — crafts, vegetarian buffet and local cuisine."),
    ],
    'macao': [
        ('🎰', 'Casinos', "Toute l\'année — Cotai Strip, Venetian et Grand Lisboa.", 'Casinos', "Year-round — Cotai Strip, Venetian and Grand Lisboa."),
        ('🏛️', 'Patrimoine portugais', "Octobre-mars — ruines de São Paulo, Senado Square UNESCO.", 'Portuguese Heritage', "October–March — São Paulo ruins, UNESCO Senado Square."),
        ('🍽️', 'Egg tarts & fusion', "Toute l\'année — pastéis de nata, cuisine macanese et dim sum.", 'Egg Tarts & Fusion', "Year-round — pastéis de nata, Macanese cuisine and dim sum."),
        ('🎆', 'Feux d\'artifice', "Septembre-octobre — International Fireworks Display Contest.", 'Fireworks', "September–October — International Fireworks Display Contest."),
    ],
    'myanmar': [
        ('🛕', 'Bagan', "Novembre-février — 2000 temples au lever du soleil depuis une pagode.", 'Bagan', "November–February — 2,000 temples at sunrise from a pagoda."),
        ('🚣', 'Lac Inle', "Octobre-mars — pêcheurs sur une jambe, jardins flottants et marchés.", 'Inle Lake', "October–March — one-legged fishermen, floating gardens and markets."),
        ('🏛️', 'Mandalay', "Novembre-février — palais royal, colline de Mandalay et pont d\'U Bein.", 'Mandalay', "November–February — royal palace, Mandalay Hill and U Bein Bridge."),
        ('🕊️', 'Shwedagon Pagoda', "Toute l\'année — pagode dorée de Yangon, coucher de soleil spectaculaire.", 'Shwedagon Pagoda', "Year-round — Yangon\'s golden pagoda, spectacular sunset."),
    ],
    'nha-trang': [
        ('🏖️', 'Plages urbaines', "Février-septembre — 6 km de sable, eau chaude et promenade.", 'Urban Beaches', "February–September — 6 km of sand, warm water and promenade."),
        ('🤿', 'Plongée', "Février-octobre — Hòn Mun, récifs coralliens et vie marine riche.", 'Diving', "February–October — Hòn Mun, coral reefs and rich marine life."),
        ('♨️', 'Bains de boue', "Toute l\'année — Thap Ba et I-Resort, boue minérale et sources chaudes.", 'Mud Baths', "Year-round — Thap Ba and I-Resort, mineral mud and hot springs."),
        ('🏝️', 'Îles', "Février-septembre — Hòn Tằm, Hòn Tre et excursions en bateau.", 'Islands', "February–September — Hòn Tằm, Hòn Tre and boat excursions."),
    ],
    'okinawa': [
        ('🤿', 'Plongée & snorkeling', "Avril-octobre — Kerama, raies manta et eaux tropicales claires.", 'Diving & Snorkelling', "April–October — Kerama, manta rays and clear tropical waters."),
        ('🏖️', 'Plages', "Mai-octobre — Naminoue, Emerald Beach et îles Kerama.", 'Beaches', "May–October — Naminoue, Emerald Beach and Kerama Islands."),
        ('🛕', 'Châteaux Ryūkyū', "Toute l\'année — Shuri Castle UNESCO et patrimoine unique.", 'Ryūkyū Castles', "Year-round — UNESCO Shuri Castle and unique heritage."),
        ('🍽️', 'Cuisine de longévité', "Toute l\'année — gōyā chanpurū, soba d\'Okinawa et taco rice.", 'Longevity Cuisine', "Year-round — gōyā chanpurū, Okinawa soba and taco rice."),
    ],
    'osaka': [
        ('🍽️', 'Dōtonbori & street food', "Toute l\'année — takoyaki, okonomiyaki, gyōza et néons.", 'Dōtonbori & Street Food', "Year-round — takoyaki, okonomiyaki, gyōza and neon lights."),
        ('🏯', 'Château d\'Osaka', "Mars-avril (cerisiers) ou novembre — château, parc et panorama.", 'Osaka Castle', "March–April (cherry blossoms) or November — castle, park and panorama."),
        ('🎢', 'Universal Studios', "Toute l\'année — Harry Potter, Nintendo World et attractions.", 'Universal Studios', "Year-round — Harry Potter, Nintendo World and rides."),
        ('🍶', 'Shinsekai & izakayas', "Toute l\'année — quartier rétro, kushikatsu et bière froide.", 'Shinsekai & Izakayas', "Year-round — retro district, kushikatsu and cold beer."),
    ],
    'palawan': [
        ('🏖️', 'El Nido & lagons', "Décembre-mai — island hopping, lagons cachés et falaises karstiques.", 'El Nido & Lagoons', "December–May — island hopping, hidden lagoons and karst cliffs."),
        ('🌊', 'Rivière souterraine', "Décembre-mai — Puerto Princesa Underground River UNESCO.", 'Underground River', "December–May — Puerto Princesa Underground River UNESCO."),
        ('🤿', 'Plongée', "Novembre-mai — Tubbataha Reef (mars-juin), récifs vierges.", 'Diving', "November–May — Tubbataha Reef (March–June), pristine reefs."),
        ('🏝️', 'Port Barton & îles', "Décembre-mai — plages désertes, snorkeling et rythme lent.", 'Port Barton & Islands', "December–May — deserted beaches, snorkelling and slow pace."),
    ],
    'pattaya': [
        ('🏖️', 'Plages & îles', "Novembre-février — Koh Larn, Jomtien et plages de la côte.", 'Beaches & Islands', "November–February — Koh Larn, Jomtien and coastal beaches."),
        ('🤿', 'Sports nautiques', "Novembre-avril — jet-ski, parachute ascensionnel et plongée.", 'Water Sports', "November–April — jet-ski, parasailing and diving."),
        ('🎉', 'Vie nocturne', "Toute l\'année — Walking Street, spectacles et bars.", 'Nightlife', "Year-round — Walking Street, shows and bars."),
        ('⛳', 'Golf', "Novembre-février — 20+ parcours, tarifs compétitifs et climat idéal.", 'Golf', "November–February — 20+ courses, competitive rates and ideal climate."),
    ],
    'pekin': [
        ('🏯', 'Cité Interdite', "Mars-mai ou septembre-octobre — palais impérial, Temple du Ciel.", 'Forbidden City', "March–May or September–October — imperial palace, Temple of Heaven."),
        ('🧱', 'Grande Muraille', "Avril-mai ou octobre — Mutianyu ou Jinshanling, lumière dorée.", 'Great Wall', "April–May or October — Mutianyu or Jinshanling, golden light."),
        ('🍽️', 'Canard laqué', "Toute l\'année — Quanjude, Da Dong et hutong food tours.", 'Peking Duck', "Year-round — Quanjude, Da Dong and hutong food tours."),
        ('🏛️', 'Hutongs', "Toute l\'année — ruelles historiques, maisons à cour et vie locale.", 'Hutongs', "Year-round — historic alleyways, courtyard houses and local life."),
    ],
    'penang': [
        ('🍽️', 'Street food UNESCO', "Toute l\'année — char kway teow, laksa, cendol et hawker stalls.", 'UNESCO Street Food', "Year-round — char kway teow, laksa, cendol and hawker stalls."),
        ('🎨', 'Street art George Town', "Toute l\'année — fresques, architecture coloniale et clan jetties.", 'George Town Street Art', "Year-round — murals, colonial architecture and clan jetties."),
        ('🛕', 'Kek Lok Si', "Toute l\'année — plus grand temple bouddhiste de Malaisie, Penang Hill.", 'Kek Lok Si', "Year-round — Malaysia\'s largest Buddhist temple, Penang Hill."),
        ('🏖️', 'Plages', "Décembre-mars — Batu Ferringhi et plages du nord.", 'Beaches', "December–March — Batu Ferringhi and northern beaches."),
    ],
    'philippines': [
        ('🏖️', 'Plages & îles', "Décembre-mai — Boracay, El Nido, Siargao et Coron.", 'Beaches & Islands', "December–May — Boracay, El Nido, Siargao and Coron."),
        ('🤿', 'Plongée', "Novembre-mai — Tubbataha, Apo Reef et Malapascua.", 'Diving', "November–May — Tubbataha, Apo Reef and Malapascua."),
        ('🌾', 'Rizières de Banaue', "Mars-mai — terrasses UNESCO, culture ifugao.", 'Banaue Rice Terraces', "March–May — UNESCO terraces, Ifugao culture."),
        ('🐋', 'Requins-baleines', "Novembre-juin — Donsol ou Oslob, nage avec les géants.", 'Whale Sharks', "November–June — Donsol or Oslob, swimming with giants."),
        ('👨‍👩‍👧', 'Famille', "Janvier-avril — plages sûres, accueil chaleureux et prix abordables.", 'Family', "January–April — safe beaches, warm hospitality and affordable prices."),
    ],
    'phnom-penh': [
        ('🏛️', 'Palais Royal', "Novembre-février — Palais Royal, Pagode d\'Argent et musée national.", 'Royal Palace', "November–February — Royal Palace, Silver Pagoda and National Museum."),
        ('📚', 'Mémoire', "Toute l\'année — musée du Génocide Tuol Sleng et Killing Fields.", 'Memory', "Year-round — Tuol Sleng Genocide Museum and Killing Fields."),
        ('🍽️', 'Street food & marchés', "Toute l\'année — marché central, marché russe et cuisine khmère.", 'Street Food & Markets', "Year-round — Central Market, Russian Market and Khmer cuisine."),
        ('🌅', 'Bord du Mékong', "Toute l\'année — Sisowath Quay, coucher de soleil et terrasses.", 'Mekong Riverside', "Year-round — Sisowath Quay, sunsets and terraces."),
    ],
    'phu-quoc': [
        ('🏖️', 'Plages', "Novembre-mars — Sao Beach, Long Beach et Kem Beach.", 'Beaches', "November–March — Sao Beach, Long Beach and Kem Beach."),
        ('🤿', 'Snorkeling & plongée', "Novembre-mai — An Thoi, coraux et eaux claires.", 'Snorkelling & Diving', "November–May — An Thoi, corals and clear waters."),
        ('🍽️', 'Nuoc mam & fruits de mer', "Toute l\'année — fabriques de sauce poisson, marché nocturne de Dinh Cau.", 'Nuoc Mam & Seafood', "Year-round — fish sauce factories, Dinh Cau night market."),
        ('🌅', 'Couchers de soleil', "Toute l\'année — côte ouest, Sunset Town et téléphérique de Hon Thom.", 'Sunsets', "Year-round — west coast, Sunset Town and Hon Thom cable car."),
    ],
    'rajasthan': [
        ('🏰', 'Forteresses & palais', "Octobre-mars — Jaipur, Jodhpur, Udaipur et Jaisalmer.", 'Forts & Palaces', "October–March — Jaipur, Jodhpur, Udaipur and Jaisalmer."),
        ('🐪', 'Désert du Thar', "Novembre-février — safari en chameau, nuit sous les étoiles.", 'Thar Desert', "November–February — camel safari, night under the stars."),
        ('🎨', 'Artisanat & couleurs', "Toute l\'année — textiles, bijoux, tie-dye et festivals.", 'Crafts & Colours', "Year-round — textiles, jewellery, tie-dye and festivals."),
        ('🐯', 'Safari tigres', "Octobre-juin — Ranthambore, Sariska et Keoladeo.", 'Tiger Safari', "October–June — Ranthambore, Sariska and Keoladeo."),
    ],
    'sapa': [
        ('🌾', 'Rizières en terrasses', "Septembre-octobre — récolte dorée, paysages spectaculaires.", 'Terraced Rice Paddies', "September–October — golden harvest, spectacular landscapes."),
        ('🥾', 'Trek ethnique', "Mars-mai ou septembre-novembre — villages H\'Mông, Dao et Tày.", 'Ethnic Trekking', "March–May or September–November — H\'Mông, Dao and Tày villages."),
        ('🏔️', 'Fansipan', "Octobre-mars — toit de l\'Indochine (3143m), téléphérique ou trek.", 'Fansipan', "October–March — roof of Indochina (3,143m), cable car or trek."),
        ('📸', 'Photographie', "Septembre-octobre — brumes, lumière dorée et rizières vertes.", 'Photography', "September–October — mists, golden light and green terraces."),
    ],
    'seoul': [
        ('🏛️', 'Palais Joseon', "Mars-mai ou octobre — Gyeongbokgung, Changdeokgung et hanbok.", 'Joseon Palaces', "March–May or October — Gyeongbokgung, Changdeokgung and hanbok."),
        ('🍽️', 'K-food', "Toute l\'année — BBQ coréen, bibimbap, street food de Myeongdong.", 'K-Food', "Year-round — Korean BBQ, bibimbap, Myeongdong street food."),
        ('🎵', 'K-pop & Hallyu', "Toute l\'année — Gangnam, HYBE, concerts et quartiers branchés.", 'K-Pop & Hallyu', "Year-round — Gangnam, HYBE, concerts and trendy districts."),
        ('🌸', 'Cerisiers', "Début avril — Yeouido, palais et rivière Cheonggyecheon.", 'Cherry Blossoms', "Early April — Yeouido, palaces and Cheonggyecheon Stream."),
        ('♨️', 'Jjimjilbang', "Toute l\'année — saunas coréens, Dragon Hill Spa et Siloam.", 'Jjimjilbang', "Year-round — Korean saunas, Dragon Hill Spa and Siloam."),
    ],
    'shanghai': [
        ('🏙️', 'Bund & Pudong', "Octobre-novembre — skyline, Oriental Pearl et promenade nocturne.", 'Bund & Pudong', "October–November — skyline, Oriental Pearl and evening promenade."),
        ('🏘️', 'French Concession', "Avril-mai ou octobre — platanes, cafés et architecture Art déco.", 'French Concession', "April–May or October — plane trees, cafés and Art Deco architecture."),
        ('🍽️', 'Cuisine shanghainaise', "Toute l\'année — xiaolongbao, hairy crab (automne) et food streets.", 'Shanghainese Cuisine', "Year-round — xiaolongbao, hairy crab (autumn) and food streets."),
        ('🛍️', 'Shopping', "Toute l\'année — Nanjing Road, Tianzifang et M50 Art District.", 'Shopping', "Year-round — Nanjing Road, Tianzifang and M50 Art District."),
    ],
    'siargao': [
        ('🏄', 'Surf Cloud 9', "Septembre-novembre — vague droite légendaire, compétitions.", 'Cloud 9 Surfing', "September–November — legendary right-hander, competitions."),
        ('🏝️', 'Island hopping', "Mars-octobre — Naked Island, Daku et Guyam.", 'Island Hopping', "March–October — Naked Island, Daku and Guyam."),
        ('🌿', 'Sugba Lagoon', "Toute l\'année — lagon turquoise, paddle et plongeon depuis le ponton.", 'Sugba Lagoon', "Year-round — turquoise lagoon, paddleboarding and cliff jumping."),
        ('🌴', 'Coconut Road', "Toute l\'année — route bordée de cocotiers, moto et ambiance décontractée.", 'Coconut Road', "Year-round — palm-lined road, motorbike rides and laid-back vibes."),
    ],
    'sri-lanka': [
        ('🛕', 'Temples & patrimoine', "Décembre-mars — Sigiriya, Dambulla, Kandy et Triangle Culturel.", 'Temples & Heritage', "December–March — Sigiriya, Dambulla, Kandy and Cultural Triangle."),
        ('🚂', 'Train des montagnes', "Janvier-avril — Ella, plantations de thé et paysages spectaculaires.", 'Highland Train', "January–April — Ella, tea plantations and spectacular scenery."),
        ('🐘', 'Safari Yala', "Février-juillet — léopards, éléphants et oiseaux au parc national.", 'Yala Safari', "February–July — leopards, elephants and birds at the national park."),
        ('🏖️', 'Plages', "Décembre-mars (sud/ouest) ou mai-septembre (est) — Mirissa, Unawatuna, Arugam Bay.", 'Beaches', "December–March (south/west) or May–September (east) — Mirissa, Unawatuna, Arugam Bay."),
        ('👨‍👩‍👧', 'Famille', "Janvier-mars — côte sud, tortues et train panoramique.", 'Family', "January–March — south coast, turtles and scenic train."),
    ],
    'taipei': [
        ('🍽️', 'Marchés nocturnes', "Toute l\'année — Shilin, Raohe et Tonghua, street food sans fin.", 'Night Markets', "Year-round — Shilin, Raohe and Tonghua, endless street food."),
        ('🏙️', 'Taipei 101', "Toute l\'année — gratte-ciel, observatoire et quartier de Xinyi.", 'Taipei 101', "Year-round — skyscraper, observatory and Xinyi district."),
        ('♨️', 'Sources chaudes', "Octobre-mars — Beitou, Yangmingshan et bains en plein air.", 'Hot Springs', "October–March — Beitou, Yangmingshan and outdoor baths."),
        ('🛕', 'Temples', "Toute l\'année — Longshan, Dalongdong Baoan et Jiufen à 1h.", 'Temples', "Year-round — Longshan, Dalongdong Baoan and Jiufen 1h away."),
    ],

    # ══════════════════════════════════════════════════════════════════
    # MOYEN-ORIENT & ASIE CENTRALE
    # ══════════════════════════════════════════════════════════════════
    'abu-dhabi': [
        ('🏛️', 'Louvre Abu Dhabi', "Novembre-mars — musée-dôme sur l\'eau, collection universelle.", 'Louvre Abu Dhabi', "November–March — dome museum on water, universal collection."),
        ('🕌', 'Mosquée Sheikh Zayed', "Toute l\'année — plus grande mosquée des EAU, visite gratuite.", 'Sheikh Zayed Mosque', "Year-round — UAE\'s largest mosque, free visit."),
        ('🏖️', 'Plages & îles', "Octobre-avril — Saadiyat, Yas et excursion mangroves en kayak.", 'Beaches & Islands', "October–April — Saadiyat, Yas and mangrove kayak excursion."),
        ('🏎️', 'Ferrari World & Yas', "Toute l\'année — Ferrari World, Yas Waterworld et circuit F1.", 'Ferrari World & Yas', "Year-round — Ferrari World, Yas Waterworld and F1 circuit."),
        ('🏜️', 'Désert', "Octobre-mars — safari en 4x4, dunes et nuit bédouine.", 'Desert', "October–March — 4x4 safari, dunes and Bedouin night."),
    ],
    'doha': [
        ('🏛️', 'Musée d\'Art islamique', "Novembre-mars — chef-d\'œuvre de I.M. Pei, collection millénaire.", 'Museum of Islamic Art', "November–March — I.M. Pei masterpiece, millennial collection."),
        ('🛍️', 'Souq Waqif', "Toute l\'année — souk restauré, faucons, épices et restaurants.", 'Souq Waqif', "Year-round — restored souk, falcons, spices and restaurants."),
        ('🏖️', 'Inland Sea & désert', "Octobre-mars — Khor Al Adaid, dune bashing et mer intérieure.", 'Inland Sea & Desert', "October–March — Khor Al Adaid, dune bashing and inland sea."),
        ('🏙️', 'Skyline & Pearl', "Toute l\'année — The Pearl, Lusail et corniche au coucher du soleil.", 'Skyline & Pearl', "Year-round — The Pearl, Lusail and corniche at sunset."),
    ],
    'jordanie': [
        ('🏛️', 'Pétra', "Mars-mai ou octobre-novembre — cité nabatéenne, Treasury au lever du jour.", 'Petra', "March–May or October–November — Nabataean city, Treasury at dawn."),
        ('🏜️', 'Wadi Rum', "Mars-mai ou octobre — désert rouge, nuit bédouine et 4x4.", 'Wadi Rum', "March–May or October — red desert, Bedouin night and 4x4."),
        ('🏊', 'Mer Morte', "Toute l\'année — flottaison, boue thérapeutique et spas.", 'Dead Sea', "Year-round — floating, therapeutic mud and spas."),
        ('🤿', 'Aqaba & mer Rouge', "Toute l\'année — plongée, récifs et eaux chaudes.", 'Aqaba & Red Sea', "Year-round — diving, reefs and warm waters."),
    ],
    'oman': [
        ('🏜️', 'Wahiba Sands', "Octobre-mars — dunes, campement bédouin et ciel étoilé.", 'Wahiba Sands', "October–March — dunes, Bedouin camp and starry sky."),
        ('🏊', 'Wadis turquoise', "Octobre-avril — Wadi Shab, Wadi Bani Khalid et baignade.", 'Turquoise Wadis', "October–April — Wadi Shab, Wadi Bani Khalid and swimming."),
        ('🏔️', 'Jebel Akhdar', "Octobre-mars — montagnes du Hajar, villages en terrasses et roses.", 'Jebel Akhdar', "October–March — Hajar mountains, terraced villages and roses."),
        ('🕌', 'Mascate', "Octobre-mars — Grande Mosquée, souk de Mutrah et corniche.", 'Muscat', "October–March — Grand Mosque, Mutrah Souk and corniche."),
    ],
    'ouzbekistan': [
        ('🕌', 'Samarcande', "Avril-mai ou septembre-octobre — Registan, Shah-i-Zinda et Bibi-Khanym.", 'Samarkand', "April–May or September–October — Registan, Shah-i-Zinda and Bibi-Khanym."),
        ('🏛️', 'Boukhara', "Avril-mai ou septembre-octobre — 140 monuments, Ark et Poi-Kalon.", 'Bukhara', "April–May or September–October — 140 monuments, Ark and Poi-Kalon."),
        ('🏘️', 'Khiva', "Avril-mai ou septembre-octobre — Itchan Kala, ville-musée fortifiée.", 'Khiva', "April–May or September–October — Itchan Kala, fortified museum-city."),
        ('🍽️', 'Cuisine ouzbèke', "Toute l\'année — plov, samsa, lagman et bazars.", 'Uzbek Cuisine', "Year-round — plov, samsa, lagman and bazaars."),
    ],
    'georgie': [
        ('🍷', 'Vin & qvevri', "Septembre-octobre — vendanges en Kakhétie, vin en amphores.", 'Wine & Qvevri', "September–October — Kakheti harvest, wine in clay vessels."),
        ('🏔️', 'Caucase', "Juin-septembre — Kazbegi, Svanétie et trek de Mestia à Ushguli.", 'Caucasus', "June–September — Kazbegi, Svaneti and Mestia to Ushguli trek."),
        ('🍽️', 'Cuisine géorgienne', "Toute l\'année — khinkali, khachapuri, lobio et churchkhela.", 'Georgian Cuisine', "Year-round — khinkali, khachapuri, lobio and churchkhela."),
        ('🏛️', 'Monastères', "Toute l\'année — Jvari, Gergeti Trinity et monastères rupestres.", 'Monasteries', "Year-round — Jvari, Gergeti Trinity and cave monasteries."),
    ],
    'tbilissi': [
        ('♨️', 'Bains sulfureux', "Toute l\'année — Abanotubani, bains en brique du quartier historique.", 'Sulphur Baths', "Year-round — Abanotubani, brick baths in the historic quarter."),
        ('🏛️', 'Vieille ville', "Avril-juin ou septembre-octobre — Narikala, Meidan et Fabrika.", 'Old Town', "April–June or September–October — Narikala, Meidan and Fabrika."),
        ('🍷', 'Vin & cuisine', "Toute l\'année — bars à vin naturel, khachapuri et marchés.", 'Wine & Food', "Year-round — natural wine bars, khachapuri and markets."),
        ('🎉', 'Vie nocturne', "Toute l\'année — Bassiani, clubs techno et scène underground.", 'Nightlife', "Year-round — Bassiani, techno clubs and underground scene."),
    ],
    'tel-aviv': [
        ('🏖️', 'Plages', "Mai-octobre — Gordon, Frishman et Hilton Beach.", 'Beaches', "May–October — Gordon, Frishman and Hilton Beach."),
        ('🍽️', 'Cuisine fusion', "Toute l\'année — Carmel Market, shakshuka, hummus et restaurants.", 'Fusion Food', "Year-round — Carmel Market, shakshuka, hummus and restaurants."),
        ('🏛️', 'Bauhaus & White City', "Toute l\'année — plus de 4000 bâtiments Bauhaus UNESCO.", 'Bauhaus & White City', "Year-round — over 4,000 UNESCO Bauhaus buildings."),
        ('🎉', 'Vie nocturne', "Toute l\'année — Florentin, Rothschild et clubs jusqu\'à l\'aube.", 'Nightlife', "Year-round — Florentin, Rothschild and clubs until dawn."),
    ],

    # ══════════════════════════════════════════════════════════════════
    # AMÉRIQUES
    # ══════════════════════════════════════════════════════════════════
    'antigua': [
        ('🏖️', '365 plages', "Décembre-avril — Dickenson Bay, Half Moon Bay et Valley Church.", '365 Beaches', "December–April — Dickenson Bay, Half Moon Bay and Valley Church."),
        ('⛵', 'Voile & régates', "Décembre-avril — Antigua Sailing Week (avril), charters.", 'Sailing & Regattas', "December–April — Antigua Sailing Week (April), charters."),
        ('🏛️', 'Nelson\'s Dockyard', "Toute l\'année — chantier naval historique UNESCO, English Harbour.", 'Nelson\'s Dockyard', "Year-round — UNESCO historic dockyard, English Harbour."),
        ('🤿', 'Snorkeling', "Décembre-juin — Cades Reef, épaves et eaux cristallines.", 'Snorkelling', "December–June — Cades Reef, wrecks and crystal-clear waters."),
    ],
    'aruba': [
        ('🏖️', 'Eagle & Palm Beach', "Toute l\'année — alizés, soleil garanti et eaux calmes.", 'Eagle & Palm Beach', "Year-round — trade winds, guaranteed sun and calm waters."),
        ('🏄', 'Windsurf & kitesurf', "Juin-août — Fisherman\'s Huts, vent constant.", 'Windsurf & Kitesurf', "June–August — Fisherman\'s Huts, constant wind."),
        ('🏜️', 'Arikok', "Toute l\'année — parc national, formations rocheuses et grottes.", 'Arikok', "Year-round — national park, rock formations and caves."),
        ('🍽️', 'Gastronomie', "Toute l\'année — keshi yena, fresh catch et restaurants internationaux.", 'Gastronomy', "Year-round — keshi yena, fresh catch and international restaurants."),
    ],
    'bahamas': [
        ('🏖️', 'Plages & îles', "Décembre-avril — Exuma, Harbour Island (sable rose) et Nassau.", 'Beaches & Islands', "December–April — Exuma, Harbour Island (pink sand) and Nassau."),
        ('🐷', 'Swimming Pigs', "Toute l\'année — Big Major Cay, cochons nageurs des Exumas.", 'Swimming Pigs', "Year-round — Big Major Cay, Exumas swimming pigs."),
        ('🤿', 'Plongée', "Novembre-mai — Thunderball Grotto, requins et trous bleus.", 'Diving', "November–May — Thunderball Grotto, sharks and blue holes."),
        ('🎰', 'Atlantis & Nassau', "Toute l\'année — Atlantis Resort, musée des pirates et Fish Fry.", 'Atlantis & Nassau', "Year-round — Atlantis Resort, pirate museum and Fish Fry."),
    ],
    'belize': [
        ('🤿', 'Blue Hole & récif', "Mars-juin — plongée au Great Blue Hole, deuxième barrière au monde.", 'Blue Hole & Reef', "March–June — Great Blue Hole dive, world\'s second largest reef."),
        ('🏛️', 'Temples mayas', "Décembre-mai — Xunantunich, Caracol et Lamanai en jungle.", 'Maya Temples', "December–May — Xunantunich, Caracol and Lamanai in the jungle."),
        ('🌿', 'Jungle & faune', "Février-mai — jaguars, toucans et Cockscomb Basin.", 'Jungle & Wildlife', "February–May — jaguars, toucans and Cockscomb Basin."),
        ('🏝️', 'Cayes', "Décembre-mai — Caye Caulker, Ambergris Caye et snorkeling.", 'Cayes', "December–May — Caye Caulker, Ambergris Caye and snorkelling."),
    ],
    'bermudes': [
        ('🏖️', 'Plages roses', "Mai-octobre — Horseshoe Bay, Elbow Beach et Warwick Long Bay.", 'Pink Beaches', "May–October — Horseshoe Bay, Elbow Beach and Warwick Long Bay."),
        ('🤿', 'Plongée sur épaves', "Mai-octobre — plus de 300 épaves, visibilité 20-40m.", 'Wreck Diving', "May–October — over 300 wrecks, 20–40m visibility."),
        ('🏛️', 'Hamilton & St. George', "Toute l\'année — architecture coloniale, musées et UNESCO St. George.", 'Hamilton & St. George', "Year-round — colonial architecture, museums and UNESCO St. George."),
        ('⛳', 'Golf', "Mars-novembre — parcours de classe mondiale en bord de mer.", 'Golf', "March–November — world-class seaside courses."),
    ],
    'bogota': [
        ('🎨', 'Musées & street art', "Toute l\'année — Musée de l\'Or, Botero et quartier de La Candelaria.", 'Museums & Street Art', "Year-round — Gold Museum, Botero and La Candelaria district."),
        ('🍽️', 'Gastronomie', "Toute l\'année — ajiaco, arepas et restaurants contemporains.", 'Gastronomy', "Year-round — ajiaco, arepas and contemporary restaurants."),
        ('🏔️', 'Monserrate', "Toute l\'année — funiculaire, panorama à 3150m et sanctuaire.", 'Monserrate', "Year-round — funicular, panorama at 3,150m and sanctuary."),
        ('☕', 'Café colombien', "Toute l\'année — cafés de spécialité, torréfaction locale.", 'Colombian Coffee', "Year-round — specialty cafés, local roasting."),
    ],
    'bolivie': [
        ('🏜️', 'Salar d\'Uyuni', "Décembre-mars (miroir d\'eau) ou juin-octobre (sec, étoiles).", 'Uyuni Salt Flat', "December–March (water mirror) or June–October (dry, stars)."),
        ('🏔️', 'La Paz & Altiplano', "Mai-octobre — Vallée de la Lune, marché des sorcières.", 'La Paz & Altiplano', "May–October — Moon Valley, witches\' market."),
        ('🚲', 'Route de la Mort', "Avril-octobre — descente en VTT, 3600m de dénivelé.", 'Death Road', "April–October — mountain bike descent, 3,600m drop."),
        ('🌿', 'Amazonie bolivienne', "Mai-octobre — Rurrenabaque, pampas et jungle.", 'Bolivian Amazon', "May–October — Rurrenabaque, pampas and jungle."),
    ],
    'boston': [
        ('🏛️', 'Freedom Trail', "Avril-octobre — 4 km d\'histoire américaine, 16 sites.", 'Freedom Trail', "April–October — 4 km of American history, 16 sites."),
        ('🍁', 'Feuillage d\'automne', "Octobre — Nouvelle-Angleterre, couleurs spectaculaires.", 'Fall Foliage', "October — New England, spectacular colours."),
        ('🍽️', 'Fruits de mer', "Toute l\'année — clam chowder, lobster roll et Legal Sea Foods.", 'Seafood', "Year-round — clam chowder, lobster roll and Legal Sea Foods."),
        ('🎓', 'Harvard & MIT', "Toute l\'année — campus, librairies et quartier de Cambridge.", 'Harvard & MIT', "Year-round — campuses, bookshops and Cambridge district."),
    ],
    'cabo-san-lucas': [
        ('🐋', 'Observation des baleines', "Décembre-mars — baleines grises et à bosse dans le Pacifique.", 'Whale Watching', "December–March — grey and humpback whales in the Pacific."),
        ('🏖️', 'Plages', "Octobre-mai — Medano Beach, Lover\'s Beach et Chileno Bay.", 'Beaches', "October–May — Medano Beach, Lover\'s Beach and Chileno Bay."),
        ('🤿', 'Plongée', "Juillet-octobre — raies manta, requins-marteaux et Cabo Pulmo.", 'Diving', "July–October — manta rays, hammerheads and Cabo Pulmo."),
        ('🏌️', 'Golf', "Octobre-mai — Diamante, Quivira et Cabo del Sol.", 'Golf', "October–May — Diamante, Quivira and Cabo del Sol."),
    ],
    'cartagene': [
        ('🏛️', 'Vieille ville coloniale', "Décembre-avril — remparts, balcons fleuris et place San Pedro.", 'Colonial Old Town', "December–April — ramparts, flowered balconies and San Pedro square."),
        ('🏖️', 'Îles Rosario', "Décembre-avril — plages, snorkeling et eaux caribéennes.", 'Rosario Islands', "December–April — beaches, snorkelling and Caribbean waters."),
        ('🍽️', 'Cuisine afro-colombienne', "Toute l\'année — ceviche, arepa de huevo et cocadas.", 'Afro-Colombian Food', "Year-round — ceviche, arepa de huevo and cocadas."),
        ('💃', 'Salsa & vie nocturne', "Toute l\'année — Getsemaní, bars et musique live.", 'Salsa & Nightlife', "Year-round — Getsemaní, bars and live music."),
    ],
    'chicago': [
        ('🏗️', 'Architecture', "Avril-octobre — croisière architecturale sur la rivière, Frank Lloyd Wright.", 'Architecture', "April–October — river architecture cruise, Frank Lloyd Wright."),
        ('🍕', 'Deep-dish pizza', "Toute l\'année — Lou Malnati\'s, Giordano\'s et Pequod\'s.", 'Deep-Dish Pizza', "Year-round — Lou Malnati\'s, Giordano\'s and Pequod\'s."),
        ('🎵', 'Blues & jazz', "Toute l\'année — Kingston Mines, Buddy Guy\'s Legends et clubs.", 'Blues & Jazz', "Year-round — Kingston Mines, Buddy Guy\'s Legends and clubs."),
        ('🎨', 'Art Institute', "Toute l\'année — l\'un des meilleurs musées d\'art au monde.", 'Art Institute', "Year-round — one of the world\'s finest art museums."),
        ('👨‍👩‍👧', 'Famille', "Juin-août — Millennium Park, Navy Pier et Shedd Aquarium.", 'Family', "June–August — Millennium Park, Navy Pier and Shedd Aquarium."),
    ],
    'chili': [
        ('🏜️', 'Atacama', "Mars-novembre — désert le plus sec, geysers du Tatio et Valle de la Luna.", 'Atacama', "March–November — driest desert, Tatio geysers and Valle de la Luna."),
        ('🏔️', 'Patagonie chilienne', "Novembre-mars — Torres del Paine, glaciers et trek W.", 'Chilean Patagonia', "November–March — Torres del Paine, glaciers and W trek."),
        ('🍷', 'Vallées viticoles', "Mars-mai — vendanges, Casablanca, Colchagua et Maipo.", 'Wine Valleys', "March–May — harvest, Casablanca, Colchagua and Maipo."),
        ('🏝️', 'Île de Pâques', "Octobre-mars — moaïs, Rano Raraku et Anakena.", 'Easter Island', "October–March — moai, Rano Raraku and Anakena."),
    ],
    'colombie': [
        ('☕', 'Triangle du café', "Toute l\'année — Salento, Valle de Cocora et fincas.", 'Coffee Triangle', "Year-round — Salento, Cocora Valley and fincas."),
        ('🏛️', 'Villes coloniales', "Décembre-mars — Cartagena, Villa de Leyva et Barichara.", 'Colonial Towns', "December–March — Cartagena, Villa de Leyva and Barichara."),
        ('🌿', 'Amazonie & faune', "Juin-octobre — Leticia, dauphins roses et jungle.", 'Amazon & Wildlife', "June–October — Leticia, pink dolphins and jungle."),
        ('🏖️', 'Caraïbes', "Décembre-avril — San Andrés, Providencia et îles Rosario.", 'Caribbean', "December–April — San Andrés, Providencia and Rosario Islands."),
        ('💃', 'Salsa à Cali', "Toute l\'année — capitale mondiale de la salsa, écoles et clubs.", 'Salsa in Cali', "Year-round — world salsa capital, schools and clubs."),
    ],
    'curacao': [
        ('🏖️', 'Plages & criques', "Toute l\'année — Cas Abao, Playa Kenepa et Klein Curaçao.", 'Beaches & Coves', "Year-round — Cas Abao, Playa Kenepa and Klein Curaçao."),
        ('🏘️', 'Willemstad', "Toute l\'année — Handelskade coloré, Punda et marché flottant.", 'Willemstad', "Year-round — colourful Handelskade, Punda and floating market."),
        ('🤿', 'Plongée', "Toute l\'année — accès au récif depuis la plage, 60+ sites.", 'Diving', "Year-round — shore-access reef, 60+ sites."),
        ('🍽️', 'Cuisine créole', "Toute l\'année — stoba, keshi yena et liqueur de Blue Curaçao.", 'Creole Cuisine', "Year-round — stoba, keshi yena and Blue Curaçao liqueur."),
    ],
    'cuzco': [
        ('🏛️', 'Cité inca', "Avril-octobre — Plaza de Armas, Sacsayhuamán et Qoricancha.", 'Inca City', "April–October — Plaza de Armas, Sacsayhuamán and Qoricancha."),
        ('🏔️', 'Machu Picchu', "Avril-octobre — train depuis Ollantaytambo ou trek Inca Trail.", 'Machu Picchu', "April–October — train from Ollantaytambo or Inca Trail trek."),
        ('🌈', 'Rainbow Mountain', "Avril-novembre — Vinicunca, montagne arc-en-ciel à 5000m.", 'Rainbow Mountain', "April–November — Vinicunca, rainbow mountain at 5,000m."),
        ('🍽️', 'Gastronomie andine', "Toute l\'année — cuy, ceviche andin et restaurants de San Blas.", 'Andean Food', "Year-round — cuy, Andean ceviche and San Blas restaurants."),
    ],
    'equateur': [
        ('🐢', 'Galápagos', "Juin-novembre — faune endémique, plongée et paysages volcaniques.", 'Galápagos', "June–November — endemic wildlife, diving and volcanic landscapes."),
        ('🌿', 'Amazonie', "Toute l\'année — lodges en forêt primaire, kayak et biodiversité.", 'Amazon', "Year-round — primary forest lodges, kayaking and biodiversity."),
        ('🏔️', 'Avenue des Volcans', "Juin-septembre — Cotopaxi, Chimborazo et randonnée d\'altitude.", 'Avenue of Volcanoes', "June–September — Cotopaxi, Chimborazo and altitude hiking."),
        ('🏛️', 'Quito colonial', "Juin-septembre — centre historique UNESCO, églises baroques.", 'Colonial Quito', "June–September — UNESCO historic centre, baroque churches."),
    ],
    'galapagos': [
        ('🐢', 'Tortues géantes', "Toute l\'année — Charles Darwin Station, Santa Cruz et Isabela.", 'Giant Tortoises', "Year-round — Charles Darwin Station, Santa Cruz and Isabela."),
        ('🤿', 'Plongée', "Juin-novembre — eaux froides, requins-marteaux, raies et otaries.", 'Diving', "June–November — cold waters, hammerheads, rays and sea lions."),
        ('🐦', 'Oiseaux', "Avril-juin — fous à pieds bleus, albatros et frégates.", 'Birds', "April–June — blue-footed boobies, albatross and frigatebirds."),
        ('🏖️', 'Snorkeling', "Janvier-mai — eaux plus chaudes, tortues et iguanes marins.", 'Snorkelling', "January–May — warmer waters, turtles and marine iguanas."),
    ],
    'guatemala': [
        ('🏛️', 'Tikal', "Décembre-avril — temples mayas en jungle, lever du soleil depuis Temple IV.", 'Tikal', "December–April — Maya temples in jungle, sunrise from Temple IV."),
        ('🌋', 'Antigua & volcans', "Novembre-avril — ville coloniale, Acatenango et Fuego.", 'Antigua & Volcanoes', "November–April — colonial town, Acatenango and Fuego."),
        ('🏞️', 'Lac Atitlán', "Novembre-mars — villages mayas, randonnée et marchés.", 'Lake Atitlán', "November–March — Maya villages, hiking and markets."),
        ('🎨', 'Marchés indigènes', "Toute l\'année — Chichicastenango le jeudi et dimanche.", 'Indigenous Markets', "Year-round — Chichicastenango on Thursdays and Sundays."),
    ],
    'isla-holbox': [
        ('🐋', 'Requins-baleines', "Juin-septembre — nage avec les requins-baleines, excursion en bateau.", 'Whale Sharks', "June–September — swimming with whale sharks, boat excursion."),
        ('🌌', 'Bioluminescence', "Mai-octobre — plancton lumineux dans le lagon nocturne.", 'Bioluminescence', "May–October — glowing plankton in the night lagoon."),
        ('🏖️', 'Plage', "Novembre-mai — sable blanc, hamacs et pas de voitures.", 'Beach', "November–May — white sand, hammocks and no cars."),
        ('🦩', 'Flamants roses', "Avril-octobre — observation dans les mangroves et lagunes.", 'Flamingos', "April–October — spotting in mangroves and lagoons."),
    ],
    'key-west': [
        ('🌅', 'Mallory Square', "Toute l\'année — coucher de soleil, artistes de rue et jongleurs.", 'Mallory Square', "Year-round — sunset, street artists and performers."),
        ('🏛️', 'Maison Hemingway', "Toute l\'année — chats polydactyles, jardin tropical et histoire.", 'Hemingway House', "Year-round — polydactyl cats, tropical garden and history."),
        ('🤿', 'Snorkeling & récifs', "Avril-octobre — John Pennekamp, troisième barrière de corail.", 'Snorkelling & Reefs', "April–October — John Pennekamp, third-largest barrier reef."),
        ('🍹', 'Duval Street', "Toute l\'année — bars, key lime pie et ambiance tropicale.", 'Duval Street', "Year-round — bars, key lime pie and tropical atmosphere."),
    ],
    'las-vegas': [
        ('🎰', 'Strip & casinos', "Toute l\'année — Bellagio, Venetian, MGM et shows.", 'Strip & Casinos', "Year-round — Bellagio, Venetian, MGM and shows."),
        ('🏜️', 'Grand Canyon', "Mars-mai ou septembre-octobre — excursion à la journée (4h30).", 'Grand Canyon', "March–May or September–October — day trip (4h30)."),
        ('🎤', 'Shows & concerts', "Toute l\'année — Cirque du Soleil, résidences et spectacles.", 'Shows & Concerts', "Year-round — Cirque du Soleil, residencies and performances."),
        ('🍽️', 'Gastronomie', "Toute l\'année — buffets, restaurants de chefs étoilés sur le Strip.", 'Gastronomy', "Year-round — buffets, celebrity chef restaurants on the Strip."),
    ],
    'machu-picchu': [
        ('🏛️', 'Citadelle inca', "Avril-octobre — lever de soleil, Temple du Soleil et Intihuatana.", 'Inca Citadel', "April–October — sunrise, Temple of the Sun and Intihuatana."),
        ('🥾', 'Inca Trail', "Avril-octobre — trek de 4 jours, Porte du Soleil et passes d\'altitude.", 'Inca Trail', "April–October — 4-day trek, Sun Gate and high-altitude passes."),
        ('🏔️', 'Huayna Picchu', "Toute l\'année — montée vertigineuse, 400 places/jour, réservation.", 'Huayna Picchu', "Year-round — vertiginous climb, 400 spots/day, reservation."),
        ('🚂', 'Train panoramique', "Toute l\'année — Vistadome ou Hiram Bingham depuis Ollantaytambo.", 'Scenic Train', "Year-round — Vistadome or Hiram Bingham from Ollantaytambo."),
    ],
    'medellin': [
        ('🚡', 'Metrocable & Comuna 13', "Toute l\'année — téléphérique, escalators et street art.", 'Metrocable & Comuna 13', "Year-round — cable car, escalators and street art."),
        ('🌺', 'Feria de las Flores', "Août — défilé des silleteros, fleurs et musique.", 'Flower Festival', "August — silleteros parade, flowers and music."),
        ('☕', 'Coffee tours', "Toute l\'année — fincas caféières à 2h, torréfaction et dégustation.", 'Coffee Tours', "Year-round — coffee fincas 2h away, roasting and tasting."),
        ('🍽️', 'Gastronomie', "Toute l\'année — bandeja paisa, Mercado del Río et restaurants branchés.", 'Gastronomy', "Year-round — bandeja paisa, Mercado del Río and trendy restaurants."),
    ],
    'mexico': [
        ('🏛️', 'Zócalo & Teotihuacán', "Octobre-avril — pyramides, Palais national et Templo Mayor.", 'Zócalo & Teotihuacán', "October–April — pyramids, National Palace and Templo Mayor."),
        ('🍽️', 'Cuisine UNESCO', "Toute l\'année — tacos al pastor, mole, mezcal et marchés.", 'UNESCO Cuisine', "Year-round — tacos al pastor, mole, mezcal and markets."),
        ('🎨', 'Frida & Diego', "Toute l\'année — Casa Azul, Palacio de Bellas Artes et Coyoacán.", 'Frida & Diego', "Year-round — Casa Azul, Palacio de Bellas Artes and Coyoacán."),
        ('🏘️', 'Quartiers branchés', "Toute l\'année — Roma, Condesa, cafés et vie nocturne.", 'Trendy Neighbourhoods', "Year-round — Roma, Condesa, cafés and nightlife."),
        ('👨‍👩‍👧', 'Famille', "Novembre-mars — Chapultepec, Xochimilco et musées interactifs.", 'Family', "November–March — Chapultepec, Xochimilco and interactive museums."),
    ],
    'montreal': [
        ('🎉', 'Festivals', "Juin-août — Jazz Festival, Juste pour rire, Osheaga et Tam-Tams.", 'Festivals', "June–August — Jazz Festival, Just for Laughs, Osheaga and Tam-Tams."),
        ('🍽️', 'Gastronomie', "Toute l\'année — poutine, bagels, smoked meat et cabanes à sucre (mars).", 'Gastronomy', "Year-round — poutine, bagels, smoked meat and sugar shacks (March)."),
        ('❄️', 'Hiver', "Décembre-mars — patinoire, Igloofest et marché de Noël.", 'Winter', "December–March — ice rink, Igloofest and Christmas market."),
        ('🏛️', 'Patrimoine', "Toute l\'année — Vieux-Montréal, basilique Notre-Dame et Mont-Royal.", 'Heritage', "Year-round — Old Montréal, Notre-Dame Basilica and Mount Royal."),
    ],
    'nicaragua': [
        ('🌋', 'Volcans', "Novembre-avril — Masaya la nuit, Cerro Negro en luge, Ometepe.", 'Volcanoes', "November–April — Masaya at night, Cerro Negro sandboarding, Ometepe."),
        ('🏖️', 'Plages Pacifique', "Novembre-avril — San Juan del Sur, surf et plages préservées.", 'Pacific Beaches', "November–April — San Juan del Sur, surfing and pristine beaches."),
        ('🏛️', 'Granada coloniale', "Novembre-avril — architecture colorée, isletas et cathédrale.", 'Colonial Granada', "November–April — colourful architecture, isletas and cathedral."),
        ('🏝️', 'Corn Islands', "Mars-mai — Little Corn Island, plongée et Caribbean vibes.", 'Corn Islands', "March–May — Little Corn Island, diving and Caribbean vibes."),
    ],
    'nouvelle-orleans': [
        ('🎵', 'Jazz & musique live', "Toute l\'année — Frenchmen Street, Preservation Hall et clubs.", 'Jazz & Live Music', "Year-round — Frenchmen Street, Preservation Hall and clubs."),
        ('🎭', 'Mardi Gras', "Février-mars — parades, déguisements et fête dans les rues.", 'Mardi Gras', "February–March — parades, costumes and street celebration."),
        ('🍽️', 'Cuisine créole & cajun', "Toute l\'année — gumbo, jambalaya, beignets du Café du Monde.", 'Creole & Cajun Food', "Year-round — gumbo, jambalaya, Café du Monde beignets."),
        ('🏛️', 'French Quarter', "Toute l\'année — Jackson Square, cathédrale Saint-Louis et balcons en fer.", 'French Quarter', "Year-round — Jackson Square, St Louis Cathedral and iron balconies."),
    ],
    'oaxaca': [
        ('🍽️', 'Gastronomie', "Toute l\'année — 7 moles, tlayudas, mezcal et chapulines.", 'Gastronomy', "Year-round — 7 moles, tlayudas, mezcal and chapulines."),
        ('💀', 'Día de Muertos', "Fin octobre-début novembre — cimetières, autels et processions.", 'Day of the Dead', "Late October–early November — cemeteries, altars and processions."),
        ('🏛️', 'Monte Albán', "Octobre-avril — ruines zapotèques à 2500m, panoramas.", 'Monte Albán', "October–April — Zapotec ruins at 2,500m, panoramic views."),
        ('🎨', 'Artisanat', "Toute l\'année — alebrijes, tapis, barro negro et marchés.", 'Crafts', "Year-round — alebrijes, rugs, barro negro and markets."),
    ],
    'orlando': [
        ('🎢', 'Walt Disney World', "Toute l\'année — 4 parcs, Magic Kingdom et Epcot.", 'Walt Disney World', "Year-round — 4 parks, Magic Kingdom and Epcot."),
        ('🎬', 'Universal Studios', "Toute l\'année — Wizarding World, Jurassic World et Islands of Adventure.", 'Universal Studios', "Year-round — Wizarding World, Jurassic World and Islands of Adventure."),
        ('🐊', 'Everglades', "Décembre-avril — airboat, alligators et faune subtropicale à 3h.", 'Everglades', "December–April — airboat, alligators and subtropical wildlife 3h away."),
        ('👨‍👩‍👧', 'Famille', "Février-mars ou octobre-novembre — files d\'attente réduites, prix bas.", 'Family', "February–March or October–November — shorter queues, lower prices."),
    ],
    'panama': [
        ('🚢', 'Canal de Panama', "Toute l\'année — écluses de Miraflores, Agua Clara et musée.", 'Panama Canal', "Year-round — Miraflores Locks, Agua Clara and museum."),
        ('🏝️', 'San Blas', "Décembre-avril — îles Guna Yala, sable blanc et culture kuna.", 'San Blas', "December–April — Guna Yala islands, white sand and Kuna culture."),
        ('🌿', 'Boquete & café', "Décembre-avril — randonnée Volcán Barú, plantations de café Geisha.", 'Boquete & Coffee', "December–April — Volcán Barú hike, Geisha coffee plantations."),
        ('🏙️', 'Casco Viejo', "Toute l\'année — centre historique, rooftops et vie nocturne.", 'Casco Viejo', "Year-round — historic centre, rooftops and nightlife."),
    ],
    'patagonie': [
        ('🏔️', 'Torres del Paine', "Novembre-mars — trek W, glaciers et guanacos.", 'Torres del Paine', "November–March — W trek, glaciers and guanacos."),
        ('🧊', 'Perito Moreno', "Toute l\'année — glacier actif, passerelles et ruptures de glace.", 'Perito Moreno', "Year-round — active glacier, walkways and ice calving."),
        ('🐧', 'Péninsule Valdés', "Septembre-novembre — baleines, manchots et éléphants de mer.", 'Valdés Peninsula', "September–November — whales, penguins and elephant seals."),
        ('🥾', 'Fitz Roy', "Novembre-mars — El Chaltén, trek vers Laguna de los Tres.", 'Fitz Roy', "November–March — El Chaltén, trek to Laguna de los Tres."),
    ],
    'perou': [
        ('🏛️', 'Machu Picchu', "Avril-octobre — citadelle inca, Inca Trail ou train panoramique.", 'Machu Picchu', "April–October — Inca citadel, Inca Trail or scenic train."),
        ('🍽️', 'Gastronomie', "Toute l\'année — ceviche, lomo saltado et restaurants de Lima.", 'Gastronomy', "Year-round — ceviche, lomo saltado and Lima restaurants."),
        ('🏜️', 'Lignes de Nazca', "Toute l\'année — survol des géoglyphes, désert côtier.", 'Nazca Lines', "Year-round — geoglyph overflight, coastal desert."),
        ('🏞️', 'Lac Titicaca', "Avril-octobre — îles Uros, Taquile et culture aymara.", 'Lake Titicaca', "April–October — Uros Islands, Taquile and Aymara culture."),
        ('🌿', 'Amazonie', "Avril-octobre — Iquitos, Puerto Maldonado et jungle.", 'Amazon', "April–October — Iquitos, Puerto Maldonado and jungle."),
    ],
    'playa-del-carmen': [
        ('🏖️', 'Plages', "Novembre-avril — Quinta Avenida, playa Mamitas et clubs de plage.", 'Beaches', "November–April — Quinta Avenida, Mamitas beach and beach clubs."),
        ('🏛️', 'Tulum & cenotes', "Novembre-avril — ruines face à la mer, cenotes Gran et Dos Ojos.", 'Tulum & Cenotes', "November–April — seaside ruins, Gran Cenote and Dos Ojos."),
        ('🤿', 'Plongée cenotes', "Toute l\'année — cavernes sous-marines, visibilité cristalline.", 'Cenote Diving', "Year-round — underwater caverns, crystal visibility."),
        ('🎉', 'Vie nocturne', "Toute l\'année — Calle 12, rooftops et clubs sur la 5ème Avenue.", 'Nightlife', "Year-round — Calle 12, rooftops and clubs on 5th Avenue."),
    ],
    'porto-rico': [
        ('🏛️', 'Vieux San Juan', "Décembre-avril — forteresses, rues pavées et architecture colorée.", 'Old San Juan', "December–April — fortresses, cobblestones and colourful architecture."),
        ('🌌', 'Baie bioluminescente', "Toute l\'année — Mosquito Bay (Vieques), kayak nocturne.", 'Bioluminescent Bay', "Year-round — Mosquito Bay (Vieques), night kayaking."),
        ('🌿', 'El Yunque', "Décembre-avril — seule forêt tropicale des États-Unis.", 'El Yunque', "December–April — the only tropical rainforest in the US."),
        ('🏖️', 'Plages', "Décembre-avril — Flamenco Beach, Luquillo et Condado.", 'Beaches', "December–April — Flamenco Beach, Luquillo and Condado."),
    ],
    'punta-cana': [
        ('🏖️', 'Plages all-inclusive', "Décembre-avril — Bávaro, Cap Cana et Macao.", 'All-Inclusive Beaches', "December–April — Bávaro, Cap Cana and Macao."),
        ('🤿', 'Plongée & snorkeling', "Décembre-avril — récifs, épaves et parc sous-marin.", 'Diving & Snorkelling', "December–April — reefs, wrecks and underwater park."),
        ('⛳', 'Golf', "Novembre-avril — Punta Espada, Corales et parcours de classe mondiale.", 'Golf', "November–April — Punta Espada, Corales and world-class courses."),
        ('🐋', 'Baleines à bosse', "Janvier-mars — excursion depuis Samaná (3h).", 'Humpback Whales', "January–March — excursion from Samaná (3h)."),
    ],
    'quebec-ville': [
        ('🏰', 'Vieux-Québec', "Toute l\'année — Château Frontenac, Petit-Champlain et fortifications.", 'Old Québec', "Year-round — Château Frontenac, Petit-Champlain and fortifications."),
        ('❄️', 'Carnaval d\'hiver', "Février — Bonhomme, palais de glace et sculptures sur neige.", 'Winter Carnival', "February — Bonhomme, ice palace and snow sculptures."),
        ('🍽️', 'Gastronomie québécoise', "Toute l\'année — poutine, tourtière, cabane à sucre (mars).", 'Québécois Food', "Year-round — poutine, tourtière, sugar shack (March)."),
        ('🍁', 'Feuillage d\'automne', "Fin septembre-mi-octobre — île d\'Orléans et Charlevoix.", 'Fall Foliage', "Late September–mid-October — Île d\'Orléans and Charlevoix."),
    ],
    'republique-dominicaine': [
        ('🏖️', 'Plages', "Décembre-avril — Punta Cana, Samaná et Las Terrenas.", 'Beaches', "December–April — Punta Cana, Samaná and Las Terrenas."),
        ('🐋', 'Baleines à Samaná', "Janvier-mars — baleines à bosse dans la baie.", 'Samaná Whales', "January–March — humpback whales in the bay."),
        ('🏛️', 'Santo Domingo', "Toute l\'année — plus ancienne ville européenne des Amériques.", 'Santo Domingo', "Year-round — oldest European city in the Americas."),
        ('🏔️', 'Jarabacoa & montagne', "Novembre-mars — cascades, canyoning et air frais.", 'Jarabacoa & Mountains', "November–March — waterfalls, canyoning and fresh air."),
    ],
    'san-francisco': [
        ('🌉', 'Golden Gate & baie', "Septembre-octobre — été indien, brouillard dissipé et vues dégagées.", 'Golden Gate & Bay', "September–October — Indian summer, cleared fog and open views."),
        ('🏘️', 'Quartiers', "Toute l\'année — Haight-Ashbury, Mission, Castro et Chinatown.", 'Neighbourhoods', "Year-round — Haight-Ashbury, Mission, Castro and Chinatown."),
        ('🍽️', 'Gastronomie', "Toute l\'année — Fisherman\'s Wharf, restaurants fusion et marchés.", 'Gastronomy', "Year-round — Fisherman\'s Wharf, fusion restaurants and markets."),
        ('🍷', 'Vignobles', "Août-octobre — Napa et Sonoma à 1h, vendanges et dégustations.", 'Vineyards', "August–October — Napa and Sonoma 1h away, harvest and tastings."),
    ],
    'santiago': [
        ('🏔️', 'Cordillère & ski', "Juin-septembre — Portillo, Valle Nevado à 1h du centre.", 'Andes & Skiing', "June–September — Portillo, Valle Nevado 1h from the centre."),
        ('🍷', 'Vignobles', "Mars-mai — Maipo, Casablanca et Colchagua à portée de Santiago.", 'Vineyards', "March–May — Maipo, Casablanca and Colchagua near Santiago."),
        ('🍽️', 'Gastronomie', "Toute l\'année — ceviche, empanadas, Barrio Lastarria et Mercado Central.", 'Gastronomy', "Year-round — ceviche, empanadas, Barrio Lastarria and Mercado Central."),
        ('🎨', 'Street art & culture', "Toute l\'année — Bellavista, musée de la Mémoire et Cerro Santa Lucía.", 'Street Art & Culture', "Year-round — Bellavista, Museum of Memory and Cerro Santa Lucía."),
    ],
    'seattle': [
        ('☕', 'Café & culture', "Toute l\'année — premier Starbucks, cafés artisanaux et scène indie.", 'Coffee & Culture', "Year-round — first Starbucks, craft cafés and indie scene."),
        ('🐟', 'Pike Place Market', "Toute l\'année — poisson volant, fleurs et artisanat.", 'Pike Place Market', "Year-round — flying fish, flowers and artisan crafts."),
        ('🏔️', 'Mont Rainier', "Juin-septembre — randonnée, glaciers et meadows de fleurs sauvages.", 'Mount Rainier', "June–September — hiking, glaciers and wildflower meadows."),
        ('🎵', 'Musique', "Toute l\'année — MoPOP, scène grunge historique et concerts.", 'Music', "Year-round — MoPOP, historic grunge scene and concerts."),
    ],
    'toronto': [
        ('🏙️', 'CN Tower & skyline', "Mai-septembre — tour, île de Toronto et croisière Harbour.", 'CN Tower & Skyline', "May–September — tower, Toronto Island and Harbour cruise."),
        ('🍽️', 'Quartiers du monde', "Toute l\'année — Kensington, Little Italy, Greektown et Chinatown.", 'World Neighbourhoods', "Year-round — Kensington, Little Italy, Greektown and Chinatown."),
        ('💧', 'Chutes du Niagara', "Avril-octobre — excursion à la journée (1h30), croisière Hornblower.", 'Niagara Falls', "April–October — day trip (1h30), Hornblower cruise."),
        ('🎬', 'TIFF & culture', "Septembre — Toronto International Film Festival. Toute l\'année — ROM et AGO.", 'TIFF & Culture', "September — Toronto International Film Festival. Year-round — ROM and AGO."),
    ],
    'trinite-et-tobago': [
        ('🎭', 'Carnaval', "Février-mars — le plus grand carnaval des Caraïbes, soca et mas.", 'Carnival', "February–March — the Caribbean\'s biggest carnival, soca and mas."),
        ('🏖️', 'Plages de Tobago', "Décembre-mai — Pigeon Point, Englishman\'s Bay et récifs.", 'Tobago Beaches', "December–May — Pigeon Point, Englishman\'s Bay and reefs."),
        ('🐦', 'Birdwatching', "Toute l\'année — Caroni Swamp (ibis rouges), Asa Wright.", 'Birdwatching', "Year-round — Caroni Swamp (scarlet ibis), Asa Wright."),
        ('🤿', 'Plongée', "Janvier-mai — Speyside, récifs et raies manta géantes.", 'Diving', "January–May — Speyside, reefs and giant manta rays."),
    ],
    'uruguay': [
        ('🏖️', 'Punta del Este', "Décembre-mars — plage Brava, Casapueblo et jet-set sud-américain.", 'Punta del Este', "December–March — Brava beach, Casapueblo and South American jet-set."),
        ('🏛️', 'Montevideo', "Toute l\'année — Ciudad Vieja, Mercado del Puerto et rambla.", 'Montevideo', "Year-round — Ciudad Vieja, Mercado del Puerto and rambla."),
        ('🐎', 'Estancias', "Octobre-mars — gaucho culture, chevaux et asado.", 'Estancias', "October–March — gaucho culture, horses and asado."),
        ('🍷', 'Vin tannat', "Mars-mai — vignobles de Canelones et route des vins.", 'Tannat Wine', "March–May — Canelones vineyards and wine route."),
    ],
    'valparaiso': [
        ('🎨', 'Street art', "Toute l\'année — collines colorées, murales et art de rue.", 'Street Art', "Year-round — colourful hills, murals and street art."),
        ('🚋', 'Funiculaires', "Toute l\'année — ascensores centenaires, panoramas sur le port.", 'Funiculars', "Year-round — century-old ascensores, harbour panoramas."),
        ('📚', 'Neruda', "Toute l\'année — La Sebastiana, musée et poésie.", 'Neruda', "Year-round — La Sebastiana, museum and poetry."),
        ('🍷', 'Vin de Casablanca', "Mars-mai — vallée viticole à 45 min.", 'Casablanca Wine', "March–May — wine valley 45 min away."),
    ],
    'vancouver': [
        ('🏔️', 'Montagnes & ski', "Décembre-mars — Whistler, Grouse Mountain et neige en ville.", 'Mountains & Skiing', "December–March — Whistler, Grouse Mountain and city-close snow."),
        ('🌲', 'Stanley Park', "Toute l\'année — forêt ancienne, seawall et totems.", 'Stanley Park', "Year-round — old-growth forest, seawall and totem poles."),
        ('🍽️', 'Cuisine fusion', "Toute l\'année — sushi, dim sum et marché de Granville Island.", 'Fusion Cuisine', "Year-round — sushi, dim sum and Granville Island Market."),
        ('🐻', 'Nature', "Mai-octobre — observation d\'ours, kayak et Sea-to-Sky Highway.", 'Nature', "May–October — bear watching, kayaking and Sea-to-Sky Highway."),
    ],
    'washington': [
        ('🏛️', 'Monuments & Smithsonian', "Mars-mai ou septembre-octobre — tous les musées gratuits.", 'Monuments & Smithsonian', "March–May or September–October — all museums free."),
        ('🌸', 'Cerisiers', "Fin mars-début avril — Tidal Basin, 3000 cerisiers en fleurs.", 'Cherry Blossoms', "Late March–early April — Tidal Basin, 3,000 cherry trees in bloom."),
        ('🏛️', 'Capitol Hill', "Toute l\'année — Capitole, Bibliothèque du Congrès et Cour suprême.", 'Capitol Hill', "Year-round — Capitol, Library of Congress and Supreme Court."),
        ('🍽️', 'Georgetown', "Toute l\'année — quartier historique, restaurants et vie étudiante.", 'Georgetown', "Year-round — historic district, restaurants and student life."),
    ],
    'yellowstone': [
        ('🌋', 'Geysers & Old Faithful', "Mai-septembre — Old Faithful toutes les 90 min, Grand Prismatic.", 'Geysers & Old Faithful', "May–September — Old Faithful every 90 min, Grand Prismatic."),
        ('🦬', 'Faune', "Mai-octobre — bisons, ours, loups et wapitis dans Lamar Valley.", 'Wildlife', "May–October — bison, bears, wolves and elk in Lamar Valley."),
        ('🥾', 'Randonnée', "Juin-septembre — 1600 km de sentiers, canyons et cascades.", 'Hiking', "June–September — 1,600 km of trails, canyons and waterfalls."),
        ('♨️', 'Sources chaudes', "Toute l\'année — Mammoth Hot Springs, terrasses de travertin.", 'Hot Springs', "Year-round — Mammoth Hot Springs, travertine terraces."),
    ],

    # ══════════════════════════════════════════════════════════════════
    # EUROPE (restants)
    # ══════════════════════════════════════════════════════════════════
    'acores': [
        ('🐋', 'Observation baleines', "Avril-octobre — cachalots, dauphins et baleines bleues.", 'Whale Watching', "April–October — sperm whales, dolphins and blue whales."),
        ('🥾', 'Randonnée volcanique', "Avril-octobre — Sete Cidades, Fogo et sentiers côtiers.", 'Volcanic Hiking', "April–October — Sete Cidades, Fogo and coastal trails."),
        ('♨️', 'Sources chaudes', "Toute l\'année — Furnas, cozido das caldeiras et piscines naturelles.", 'Hot Springs', "Year-round — Furnas, cozido das caldeiras and natural pools."),
        ('🏖️', 'Plages volcaniques', "Juin-septembre — sable noir, piscines naturelles et surf.", 'Volcanic Beaches', "June–September — black sand, natural pools and surfing."),
    ],
    'antalya': [
        ('🏖️', 'Plages & criques', "Mai-octobre — Konyaaltı, Lara et Kaputaş.", 'Beaches & Coves', "May–October — Konyaaltı, Lara and Kaputaş."),
        ('🏛️', 'Vieille ville & sites antiques', "Mars-mai ou octobre — Kaleiçi, Perge et Aspendos.", 'Old Town & Ancient Sites', "March–May or October — Kaleiçi, Perge and Aspendos."),
        ('💧', 'Cascades Düden', "Toute l\'année — Düden supérieure et inférieure, la seconde tombe en mer.", 'Düden Waterfalls', "Year-round — upper and lower Düden, the second falls into the sea."),
        ('🚤', 'Excursion côtière', "Mai-octobre — Kekova, villes englouties et grottes marines.", 'Coastal Excursion', "May–October — Kekova, sunken cities and sea caves."),
    ],
    'bodrum': [
        ('🏰', 'Château Saint-Pierre', "Toute l\'année — château croisé, musée d\'archéologie sous-marine.", 'Castle of St Peter', "Year-round — crusader castle, underwater archaeology museum."),
        ('🏖️', 'Plages & baies', "Juin-septembre — Bitez, Gümüşlük et Türkbükü.", 'Beaches & Bays', "June–September — Bitez, Gümüşlük and Türkbükü."),
        ('⛵', 'Blue Cruise', "Mai-octobre — goélette, criques et côte lycienne.", 'Blue Cruise', "May–October — gulet, coves and Lycian coast."),
        ('🎉', 'Vie nocturne', "Juin-septembre — Halikarnas, bars et clubs en bord de mer.", 'Nightlife', "June–September — Halikarnas, bars and seaside clubs."),
    ],
    'cappadoce': [
        ('🎈', 'Montgolfières', "Avril-novembre — lever de soleil, cheminées de fées et vallées.", 'Hot Air Balloons', "April–November — sunrise, fairy chimneys and valleys."),
        ('🏨', 'Hôtels troglodytes', "Toute l\'année — Göreme, chambres creusées dans la roche.", 'Cave Hotels', "Year-round — Göreme, rooms carved into rock."),
        ('🥾', 'Vallées & randonnée', "Avril-juin ou septembre-octobre — Love Valley, Red Valley et Ihlara.", 'Valleys & Hiking', "April–June or September–October — Love Valley, Red Valley and Ihlara."),
        ('🏛️', 'Villes souterraines', "Toute l\'année — Derinkuyu et Kaymaklı, 8 niveaux sous terre.", 'Underground Cities', "Year-round — Derinkuyu and Kaymaklı, 8 levels underground."),
    ],
    'chefchaouen': [
        ('📸', 'Médina bleue', "Mars-mai ou septembre-novembre — ruelles indigo et lumière douce.", 'Blue Medina', "March–May or September–November — indigo alleyways and soft light."),
        ('🥾', 'Randonnée Rif', "Avril-juin ou septembre-octobre — cascades d\'Akchour et pont de Dieu.", 'Rif Hiking', "April–June or September–October — Akchour waterfalls and God\'s Bridge."),
        ('🍽️', 'Cuisine rifaine', "Toute l\'année — tajine, msemen et fromage de chèvre local.", 'Rif Cuisine', "Year-round — tagine, msemen and local goat cheese."),
        ('🎨', 'Artisanat', "Toute l\'année — tissage, poterie et maroquinerie berbère.", 'Crafts', "Year-round — weaving, pottery and Berber leather goods."),
    ],
    'chypre': [
        ('🏖️', 'Plages', "Mai-octobre — Ayia Napa, Fig Tree Bay et Lara Beach.", 'Beaches', "May–October — Ayia Napa, Fig Tree Bay and Lara Beach."),
        ('🏛️', 'Patrimoine antique', "Mars-mai ou octobre — Kourion, Paphos et tombeaux des Rois.", 'Ancient Heritage', "March–May or October — Kourion, Paphos and Tombs of the Kings."),
        ('🍷', 'Vin & villages', "Toute l\'année — Commandaria, Troodos et villages viticoles.", 'Wine & Villages', "Year-round — Commandaria, Troodos and wine villages."),
        ('🐢', 'Tortues', "Juin-août — ponte à Lara Bay, observation nocturne.", 'Turtles', "June–August — nesting at Lara Bay, night observation."),
    ],
    'djerba': [
        ('🏖️', 'Plages', "Mai-octobre — Sidi Mahrez, Seguia et plage de la Pointe.", 'Beaches', "May–October — Sidi Mahrez, Seguia and Pointe beach."),
        ('🕍', 'Ghriba', "Toute l\'année — plus ancienne synagogue d\'Afrique, pèlerinage annuel.", 'El Ghriba', "Year-round — Africa\'s oldest synagogue, annual pilgrimage."),
        ('🎨', 'Street art Djerbahood', "Toute l\'année — village d\'Erriadh, 150 fresques d\'artistes internationaux.", 'Djerbahood Street Art', "Year-round — Erriadh village, 150 murals by international artists."),
        ('🍽️', 'Gastronomie', "Toute l\'année — couscous au poisson, brik et spécialités djerbienne.", 'Gastronomy', "Year-round — fish couscous, brik and Djerbian specialities."),
    ],
    'dolomites': [
        ('🥾', 'Randonnée', "Juin-septembre — Tre Cime, Seceda et Alta Via 1.", 'Hiking', "June–September — Tre Cime, Seceda and Alta Via 1."),
        ('⛷️', 'Ski', "Décembre-mars — Cortina, Val Gardena et Sellaronda.", 'Skiing', "December–March — Cortina, Val Gardena and Sellaronda."),
        ('🧗', 'Via ferrata', "Juin-septembre — parcours exposés, échelles et câbles sur calcaire.", 'Via Ferrata', "June–September — exposed routes, ladders and cables on limestone."),
        ('📸', 'Photographie', "Juin-juillet ou octobre — lumière dorée sur les aiguilles dolomitiques.", 'Photography', "June–July or October — golden light on Dolomite spires."),
    ],
    'essaouira': [
        ('🏄', 'Windsurf & kitesurf', "Avril-septembre — alizés forts, spots de Moulay Bouzerktoun.", 'Windsurf & Kitesurf', "April–September — strong trade winds, Moulay Bouzerktoun spots."),
        ('🏛️', 'Médina UNESCO', "Toute l\'année — remparts, port de pêche et galeries d\'art.", 'UNESCO Medina', "Year-round — ramparts, fishing port and art galleries."),
        ('🎵', 'Festival Gnaoua', "Juin — musique gnaoua et world music dans la médina.", 'Gnaoua Festival', "June — Gnaoua and world music in the medina."),
        ('🍽️', 'Poisson grillé', "Toute l\'année — sardines grillées au port, tajine et cuisine mogadorienne.", 'Grilled Fish', "Year-round — grilled sardines at the port, tagine and Mogadorian cuisine."),
    ],
    'faro': [
        ('🏖️', 'Plages d\'Algarve', "Mai-octobre — Ilha Deserta, Ilha de Faro et Praia de Faro.", 'Algarve Beaches', "May–October — Ilha Deserta, Ilha de Faro and Praia de Faro."),
        ('🦩', 'Ria Formosa', "Toute l\'année — lagune, flamants roses et oiseaux migrateurs.", 'Ria Formosa', "Year-round — lagoon, flamingos and migratory birds."),
        ('🏛️', 'Vieille ville', "Toute l\'année — Arco da Vila, cathédrale et ruelles pavées.", 'Old Town', "Year-round — Arco da Vila, cathedral and cobbled lanes."),
        ('⛳', 'Golf', "Toute l\'année — Vilamoura, Vale do Lobo et Quinta do Lago.", 'Golf', "Year-round — Vilamoura, Vale do Lobo and Quinta do Lago."),
    ],
    'fes': [
        ('🏛️', 'Médina Fès el-Bali', "Mars-mai ou octobre-novembre — plus grande médina piétonne au monde.", 'Fes el-Bali Medina', "March–May or October–November — world\'s largest car-free medina."),
        ('🎨', 'Tanneries & zellige', "Toute l\'année — tanneries Chouara, mosaïque et artisanat.", 'Tanneries & Zellige', "Year-round — Chouara tanneries, mosaics and craftsmanship."),
        ('🍽️', 'Gastronomie fassi', "Toute l\'année — pastilla, tajine de pigeon et pâtisseries au miel.", 'Fassi Gastronomy', "Year-round — pastilla, pigeon tagine and honey pastries."),
        ('🕌', 'Medersa Bou Inania', "Toute l\'année — architecture mérinide, calligraphie et stuc sculpté.", 'Bou Inania Medersa', "Year-round — Marinid architecture, calligraphy and carved stucco."),
    ],
    'fethiye': [
        ('🏖️', 'Ölüdeniz', "Mai-octobre — lagon bleu, parapente depuis le Babadağ.", 'Ölüdeniz', "May–October — blue lagoon, paragliding from Babadağ."),
        ('⛵', 'Blue Cruise', "Mai-octobre — croisière en goélette, criques et 12 îles.", 'Blue Cruise', "May–October — gulet cruise, coves and 12 islands."),
        ('🏛️', 'Tombes lyciennes', "Toute l\'année — tombes rupestres d\'Amintas sculptées dans la falaise.", 'Lycian Tombs', "Year-round — Amintas rock tombs carved into the cliff."),
        ('🦋', 'Vallée des papillons', "Juin-septembre — crique accessible en bateau, papillons endémiques.", 'Butterfly Valley', "June–September — boat-access cove, endemic butterflies."),
    ],
    'gold-coast': [
        ('🏄', 'Surf', "Mars-mai ou septembre-novembre — Snapper Rocks, Burleigh Heads et Kirra.", 'Surfing', "March–May or September–November — Snapper Rocks, Burleigh Heads and Kirra."),
        ('🎢', 'Parcs à thèmes', "Toute l\'année — Dreamworld, Sea World et Warner Bros Movie World.", 'Theme Parks', "Year-round — Dreamworld, Sea World and Warner Bros Movie World."),
        ('🌿', 'Hinterland', "Avril-octobre — Springbrook, Lamington et forêts subtropicales.", 'Hinterland', "April–October — Springbrook, Lamington and subtropical forests."),
        ('👨‍👩‍👧', 'Famille', "Septembre-novembre — météo douce, parcs et plages sans foules.", 'Family', "September–November — mild weather, parks and uncrowded beaches."),
    ],
    'gozo': [
        ('🤿', 'Plongée', "Avril-novembre — Blue Hole, épaves et grottes sous-marines.", 'Diving', "April–November — Blue Hole, wrecks and underwater caves."),
        ('🛕', 'Temples mégalithiques', "Toute l\'année — Ggantija, plus vieux temples du monde.", 'Megalithic Temples', "Year-round — Ggantija, world\'s oldest temples."),
        ('🏖️', 'Plages & baies', "Juin-septembre — Ramla Bay (sable rouge), Xlendi et Dwejra.", 'Beaches & Bays', "June–September — Ramla Bay (red sand), Xlendi and Dwejra."),
        ('🥾', 'Randonnée', "Octobre-mai — sentiers côtiers, falaises et salines.", 'Hiking', "October–May — coastal trails, cliffs and salt pans."),
    ],
    'hammamet': [
        ('🏖️', 'Plages', "Mai-octobre — plage de Hammamet, Yasmine et sable fin.", 'Beaches', "May–October — Hammamet beach, Yasmine and fine sand."),
        ('🏛️', 'Médina', "Toute l\'année — remparts blanchis, souks et villa Dar Sebastian.", 'Medina', "Year-round — whitewashed ramparts, souks and Villa Dar Sebastian."),
        ('⛳', 'Golf', "Octobre-mai — Citrus et Yasmine, parcours internationaux.", 'Golf', "October–May — Citrus and Yasmine, international courses."),
        ('💆', 'Thalassothérapie', "Toute l\'année — cures marines, hammam et spas.", 'Thalassotherapy', "Year-round — marine treatments, hammam and spas."),
    ],
    'hurghada': [
        ('🤿', 'Plongée mer Rouge', "Toute l\'année — Giftun, épave du Thistlegorm et récifs coralliens.", 'Red Sea Diving', "Year-round — Giftun, Thistlegorm wreck and coral reefs."),
        ('🏖️', 'Plages & resorts', "Octobre-avril — sable fin, all-inclusive et soleil garanti.", 'Beaches & Resorts', "October–April — fine sand, all-inclusive and guaranteed sun."),
        ('🏜️', 'Excursion désert', "Octobre-mars — quad, safari bédouin et nuit sous les étoiles.", 'Desert Excursion', "October–March — quad biking, Bedouin safari and night under the stars."),
        ('🐬', 'Dauphins', "Toute l\'année — Dolphin House, snorkeling avec dauphins sauvages.", 'Dolphins', "Year-round — Dolphin House, snorkelling with wild dolphins."),
    ],
    'hydra': [
        ('🚶', 'Île sans voitures', "Avril-octobre — port à ânes, promenade et silence.", 'Car-Free Island', "April–October — donkey port, walks and silence."),
        ('🎨', 'Art & galeries', "Mai-septembre — artistes, galeries et maisons de capitaines.", 'Art & Galleries', "May–September — artists, galleries and captain\'s houses."),
        ('🏖️', 'Plages & criques', "Juin-septembre — Vlychos, Bisti et Agios Nikolaos.", 'Beaches & Coves', "June–September — Vlychos, Bisti and Agios Nikolaos."),
        ('🍽️', 'Tavernes', "Toute l\'année — poisson grillé sur le port, cuisine grecque simple.", 'Tavernas', "Year-round — grilled fish at the harbour, simple Greek cuisine."),
    ],
    'izmir': [
        ('🏛️', 'Éphèse', "Mars-mai ou octobre — cité antique à 1h, bibliothèque de Celsus.", 'Ephesus', "March–May or October — ancient city 1h away, Library of Celsus."),
        ('🛍️', 'Kemeraltı', "Toute l\'année — bazar historique, mosquées et caravansérails.", 'Kemeraltı', "Year-round — historic bazaar, mosques and caravanserais."),
        ('🍽️', 'Gastronomie', "Toute l\'année — boyoz, kumru et restaurants de la corniche.", 'Gastronomy', "Year-round — boyoz, kumru and waterfront restaurants."),
        ('🏖️', 'Plages', "Juin-septembre — Çeşme et Alaçatı, windsurf et criques.", 'Beaches', "June–September — Çeşme and Alaçatı, windsurfing and coves."),
    ],
    'kefalonia': [
        ('🏖️', 'Myrtos Beach', "Juin-septembre — plage iconique, falaises blanches et eau turquoise.", 'Myrtos Beach', "June–September — iconic beach, white cliffs and turquoise water."),
        ('💎', 'Grotte Melissani', "Avril-octobre — lac souterrain bleu, lumière zénithale.", 'Melissani Cave', "April–October — blue underground lake, zenith light."),
        ('🍷', 'Vin Robola', "Septembre-octobre — vendanges, cépage unique et vignobles de Robola.", 'Robola Wine', "September–October — harvest, unique grape and Robola vineyards."),
        ('⛵', 'Navigation', "Mai-septembre — Fiskardo, Assos et criques secrètes.", 'Sailing', "May–September — Fiskardo, Assos and hidden coves."),
    ],
    'kos': [
        ('🏖️', 'Plages', "Juin-septembre — Paradise Beach, Tigaki et Therma (sources chaudes).", 'Beaches', "June–September — Paradise Beach, Tigaki and Therma (hot springs)."),
        ('🏛️', 'Asklepion', "Mars-octobre — site d\'Hippocrate, vue sur la Turquie.", 'Asklepion', "March–October — Hippocrates\' site, view over Turkey."),
        ('🚲', 'Vélo', "Avril-octobre — île plate, pistes cyclables et villages intérieurs.", 'Cycling', "April–October — flat island, cycle paths and inland villages."),
        ('♨️', 'Sources chaudes', "Toute l\'année — Therma Beach, sources volcaniques en bord de mer.", 'Hot Springs', "Year-round — Therma Beach, volcanic seaside springs."),
    ],
    'lac-garde': [
        ('⛵', 'Voile & sports nautiques', "Mai-septembre — vent constant, windsurf à Torbole et voile.", 'Sailing & Water Sports', "May–September — constant wind, windsurfing in Torbole and sailing."),
        ('🏛️', 'Sirmione', "Toute l\'année — château scaliger, grottes de Catulle et thermes.", 'Sirmione', "Year-round — Scaliger castle, Grotte di Catullo and thermal baths."),
        ('🍷', 'Vin & gastronomie', "Toute l\'année — Lugana, huile d\'olive de Bardolino et cuisine lacustre.", 'Wine & Food', "Year-round — Lugana, Bardolino olive oil and lake cuisine."),
        ('🥾', 'Randonnée', "Avril-octobre — Monte Baldo (téléphérique), sentiers panoramiques.", 'Hiking', "April–October — Monte Baldo (cable car), panoramic trails."),
        ('👨‍👩‍👧', 'Famille', "Juin-août — Gardaland, plages et villages accessibles en ferry.", 'Family', "June–August — Gardaland, beaches and ferry-accessible villages."),
    ],
    'le-caire': [
        ('🏛️', 'Pyramides de Gizeh', "Octobre-avril — Khéops, Sphinx et spectacle son et lumière.", 'Giza Pyramids', "October–April — Khufu, Sphinx and sound and light show."),
        ('🏛️', 'Musée égyptien', "Toute l\'année — Grand Egyptian Museum (GEM), Toutankhamon.", 'Egyptian Museum', "Year-round — Grand Egyptian Museum (GEM), Tutankhamun."),
        ('🛍️', 'Khan el-Khalili', "Toute l\'année — souk millénaire, mosquées fatimides et artisanat.", 'Khan el-Khalili', "Year-round — ancient souk, Fatimid mosques and crafts."),
        ('🚢', 'Nil', "Octobre-mars — felucca au coucher du soleil, dîner-croisière.", 'Nile', "October–March — sunset felucca, dinner cruise."),
    ],
    'lefkada': [
        ('🏖️', 'Porto Katsiki', "Juin-septembre — falaises blanches, eaux turquoise spectaculaires.", 'Porto Katsiki', "June–September — white cliffs, spectacular turquoise waters."),
        ('🏄', 'Windsurf & kitesurf', "Mai-septembre — Vasiliki, l\'un des meilleurs spots d\'Europe.", 'Windsurf & Kitesurf', "May–September — Vasiliki, one of Europe\'s best spots."),
        ('⛵', 'Navigation', "Mai-septembre — bases de charter, îlots Meganisi et Kastos.", 'Sailing', "May–September — charter bases, Meganisi and Kastos islets."),
        ('🏖️', 'Plages', "Juin-septembre — Egremni, Kathisma et Milos Beach.", 'Beaches', "June–September — Egremni, Kathisma and Milos Beach."),
    ],
    'louxor': [
        ('🏛️', 'Vallée des Rois', "Octobre-mars — tombes pharaoniques, Toutankhamon et Ramsès.", 'Valley of the Kings', "October–March — pharaonic tombs, Tutankhamun and Ramesses."),
        ('🛕', 'Temple de Karnak', "Octobre-mars — allée des sphinx, salle hypostyle et obélisques.", 'Karnak Temple', "October–March — sphinx avenue, hypostyle hall and obelisks."),
        ('🚢', 'Croisière sur le Nil', "Octobre-avril — Louxor-Assouan, temples et felouques.", 'Nile Cruise', "October–April — Luxor to Aswan, temples and feluccas."),
        ('🎈', 'Montgolfière', "Octobre-avril — lever de soleil sur la rive ouest et les temples.", 'Hot Air Balloon', "October–April — sunrise over the West Bank and temples."),
    ],
    'marsa-alam': [
        ('🤿', 'Plongée', "Toute l\'année — Elphinstone, Fury Shoals et récifs vierges.", 'Diving', "Year-round — Elphinstone, Fury Shoals and pristine reefs."),
        ('🐢', 'Dugongs & tortues', "Toute l\'année — Abu Dabbab, dugongs et tortues vertes.", 'Dugongs & Turtles', "Year-round — Abu Dabbab, dugongs and green turtles."),
        ('🏖️', 'Plages', "Octobre-mai — sable blanc, mangroves et tranquillité.", 'Beaches', "October–May — white sand, mangroves and tranquillity."),
        ('🏜️', 'Désert & mines', "Octobre-mars — temples de Wadi el-Gemal et mines d\'émeraude.", 'Desert & Mines', "October–March — Wadi el-Gemal temples and emerald mines."),
    ],
    'melbourne': [
        ('🎨', 'Street art & laneways', "Toute l\'année — Hosier Lane, AC/DC Lane et galeries.", 'Street Art & Laneways', "Year-round — Hosier Lane, AC/DC Lane and galleries."),
        ('☕', 'Cafés', "Toute l\'année — culture café artisanale, brunch et rooftops.", 'Cafés', "Year-round — artisan coffee culture, brunch and rooftops."),
        ('🏏', 'Sport', "Mars-septembre (AFL) — MCG, Australian Open (jan) et F1 (mars).", 'Sport', "March–September (AFL) — MCG, Australian Open (Jan) and F1 (March)."),
        ('🛤️', 'Great Ocean Road', "Toute l\'année — Twelve Apostles, forêts et koalas à 2h.", 'Great Ocean Road', "Year-round — Twelve Apostles, forests and koalas 2h away."),
    ],
    'milos': [
        ('🏖️', 'Sarakiniko', "Mai-septembre — rochers blancs lunaires, piscines naturelles.", 'Sarakiniko', "May–September — lunar white rocks, natural pools."),
        ('🏖️', 'Plages volcaniques', "Juin-septembre — Firiplaka, Tsigrado et Papafragas.", 'Volcanic Beaches', "June–September — Firiplaka, Tsigrado and Papafragas."),
        ('🚤', 'Tour en bateau', "Mai-septembre — 70+ plages, grottes et village de pêcheurs de Klima.", 'Boat Tour', "May–September — 70+ beaches, caves and Klima fishing village."),
        ('🏛️', 'Catacombes', "Toute l\'année — plus anciennes catacombes chrétiennes de Grèce.", 'Catacombs', "Year-round — Greece\'s oldest Christian catacombs."),
    ],
    'naxos': [
        ('🏖️', 'Plages', "Juin-septembre — Agios Prokopios, Plaka et Mikri Vigla.", 'Beaches', "June–September — Agios Prokopios, Plaka and Mikri Vigla."),
        ('🏛️', 'Portara', "Toute l\'année — porte du temple d\'Apollon, coucher de soleil iconique.", 'Portara', "Year-round — Apollo temple gate, iconic sunset."),
        ('🧀', 'Fromage & gastronomie', "Toute l\'année — graviera de Naxos, kitro et cuisine insulaire.", 'Cheese & Food', "Year-round — Naxos graviera, kitro and island cuisine."),
        ('🥾', 'Randonnée', "Avril-juin ou septembre-octobre — mont Zeus, villages de montagne.", 'Hiking', "April–June or September–October — Mount Zeus, mountain villages."),
    ],
    'ouarzazate': [
        ('🎬', 'Studios de cinéma', "Toute l\'année — Atlas Studios, décors de Gladiator et Game of Thrones.", 'Film Studios', "Year-round — Atlas Studios, Gladiator and Game of Thrones sets."),
        ('🏰', 'Aït Ben Haddou', "Toute l\'année — ksar UNESCO, architecture en pisé et panoramas.", 'Aït Ben Haddou', "Year-round — UNESCO ksar, rammed-earth architecture and panoramas."),
        ('🏜️', 'Porte du Sahara', "Octobre-avril — route vers Merzouga, gorges du Dadès et du Todra.", 'Sahara Gateway', "October–April — road to Merzouga, Dadès and Todra gorges."),
        ('🌅', 'Vallée du Drâa', "Octobre-mars — oasis, palmeraies et kasbahs en ruines.", 'Draa Valley', "October–March — oasis, palm groves and ruined kasbahs."),
    ],
    'palerme': [
        ('🍽️', 'Street food & marchés', "Toute l\'année — arancini, panelle, Ballarò et Vucciria.", 'Street Food & Markets', "Year-round — arancini, panelle, Ballarò and Vucciria."),
        ('🏛️', 'Cathédrales normandes', "Toute l\'année — cathédrale, chapelle Palatine et Monreale.", 'Norman Cathedrals', "Year-round — cathedral, Palatine Chapel and Monreale."),
        ('🏖️', 'Plages & Mondello', "Juin-septembre — Mondello, Cefalù et Riserva dello Zingaro.", 'Beaches & Mondello', "June–September — Mondello, Cefalù and Riserva dello Zingaro."),
        ('🎭', 'Opera dei Pupi', "Toute l\'année — théâtre de marionnettes sicilien, UNESCO.", 'Opera dei Pupi', "Year-round — Sicilian puppet theatre, UNESCO."),
    ],
    'paphos': [
        ('🏛️', 'Mosaïques & tombeaux', "Mars-mai ou octobre — mosaïques romaines et Tombes des Rois.", 'Mosaics & Tombs', "March–May or October — Roman mosaics and Tombs of the Kings."),
        ('🏖️', 'Plages', "Mai-octobre — Coral Bay, Lara Bay et Blue Lagoon d\'Akamas.", 'Beaches', "May–October — Coral Bay, Lara Bay and Akamas Blue Lagoon."),
        ('🥾', 'Péninsule d\'Akamas', "Mars-mai ou octobre — gorges d\'Avakas et sentiers côtiers.", 'Akamas Peninsula', "March–May or October — Avakas Gorge and coastal trails."),
        ('🍷', 'Vin', "Toute l\'année — villages viticoles de la région, Commandaria.", 'Wine', "Year-round — regional wine villages, Commandaria."),
    ],
    'paros': [
        ('🏖️', 'Plages', "Juin-septembre — Kolymbithres, Santa Maria et Golden Beach.", 'Beaches', "June–September — Kolymbithres, Santa Maria and Golden Beach."),
        ('🏄', 'Windsurf', "Juin-septembre — Golden Beach, spot de championnats mondiaux.", 'Windsurfing', "June–September — Golden Beach, world championship spot."),
        ('🏘️', 'Naoussa', "Toute l\'année — port de pêche, ruelles blanches et vie nocturne.", 'Naoussa', "Year-round — fishing port, white alleyways and nightlife."),
        ('🏛️', 'Parikia', "Toute l\'année — Ekatontapyliani, château vénitien et marbre de Paros.", 'Parikia', "Year-round — Ekatontapyliani, Venetian castle and Parian marble."),
    ],
    'pouilles': [
        ('🏘️', 'Trulli d\'Alberobello', "Toute l\'année — habitations coniques UNESCO, Valle d\'Itria.", 'Alberobello Trulli', "Year-round — UNESCO conical dwellings, Valle d\'Itria."),
        ('🏖️', 'Plages', "Juin-septembre — Polignano a Mare, Porto Cesareo et Torre dell\'Orso.", 'Beaches', "June–September — Polignano a Mare, Porto Cesareo and Torre dell\'Orso."),
        ('🍽️', 'Gastronomie', "Toute l\'année — orecchiette, burrata, focaccia barese et vin Primitivo.", 'Gastronomy', "Year-round — orecchiette, burrata, focaccia barese and Primitivo wine."),
        ('🏰', 'Lecce baroque', "Avril-juin ou septembre-octobre — Florence du Sud, églises et piazza.", 'Baroque Lecce', "April–June or September–October — Florence of the South, churches and piazzas."),
    ],
    'sharm-el-sheikh': [
        ('🤿', 'Plongée Ras Mohammed', "Toute l\'année — Shark Reef, Yolanda et Thistlegorm.", 'Ras Mohammed Diving', "Year-round — Shark Reef, Yolanda and Thistlegorm."),
        ('🏖️', 'Plages & snorkeling', "Octobre-mai — Naama Bay, Ras Um Sid et récif accessible.", 'Beaches & Snorkelling', "October–May — Naama Bay, Ras Um Sid and accessible reef."),
        ('🏜️', 'Excursion Sinaï', "Octobre-mars — lever de soleil au Mont Sinaï (2285m).", 'Sinai Excursion', "October–March — sunrise at Mount Sinai (2,285m)."),
        ('👨‍👩‍👧', 'Famille', "Octobre-avril — resorts, piscines et activités nautiques.", 'Family', "October–April — resorts, pools and water activities."),
    ],
    'sintra': [
        ('🏰', 'Palais de Pena', "Mars-mai ou octobre — palais coloré, jardins romantiques.", 'Pena Palace', "March–May or October — colourful palace, romantic gardens."),
        ('🏛️', 'Quinta da Regaleira', "Toute l\'année — puits initiatique, grottes et jardins mystiques.", 'Quinta da Regaleira', "Year-round — initiation well, caves and mystical gardens."),
        ('🌲', 'Forêt de Sintra', "Avril-octobre — sentiers, microclimats et biodiversité unique.", 'Sintra Forest', "April–October — trails, microclimates and unique biodiversity."),
        ('🏖️', 'Cabo da Roca', "Toute l\'année — point le plus occidental d\'Europe continentale.", 'Cabo da Roca', "Year-round — westernmost point of continental Europe."),
    ],
    'thessalonique': [
        ('🏛️', 'Tour Blanche & patrimoine', "Toute l\'année — Tour Blanche, rotonde, Ano Poli et remparts.", 'White Tower & Heritage', "Year-round — White Tower, Rotunda, Ano Poli and ramparts."),
        ('🍽️', 'Gastronomie', "Toute l\'année — bougatsa, gyros et mezze du marché Modiano.", 'Gastronomy', "Year-round — bougatsa, gyros and Modiano market mezze."),
        ('🎉', 'Vie nocturne', "Toute l\'année — Ladadika, bars et clubs jusqu\'à l\'aube.", 'Nightlife', "Year-round — Ladadika, bars and clubs until dawn."),
        ('🏖️', 'Plages Halkidiki', "Juin-septembre — Kassandra et Sithonia à 1h.", 'Halkidiki Beaches', "June–September — Kassandra and Sithonia 1h away."),
    ],
    'tunis': [
        ('🏛️', 'Carthage & Sidi Bou Saïd', "Mars-mai ou octobre — ruines puniques et village bleu et blanc.", 'Carthage & Sidi Bou Said', "March–May or October — Punic ruins and blue-and-white village."),
        ('🕌', 'Médina de Tunis', "Toute l\'année — souks, Zitouna et architecture aghlabide.", 'Tunis Medina', "Year-round — souks, Zitouna and Aghlabid architecture."),
        ('🍽️', 'Gastronomie', "Toute l\'année — couscous, lablabi, brik et pâtisseries tunisiennes.", 'Gastronomy', "Year-round — couscous, lablabi, brik and Tunisian pastries."),
        ('🏛️', 'Bardo', "Toute l\'année — plus grande collection de mosaïques romaines au monde.", 'Bardo', "Year-round — world\'s largest collection of Roman mosaics."),
    ],
    'turin': [
        ('🍫', 'Chocolat & café', "Toute l\'année — bicerin, gianduja et cafés historiques.", 'Chocolate & Coffee', "Year-round — bicerin, gianduja and historic cafés."),
        ('🏛️', 'Musée Égyptien', "Toute l\'année — deuxième plus grande collection égyptienne au monde.", 'Egyptian Museum', "Year-round — world\'s second-largest Egyptian collection."),
        ('🍷', 'Vignobles piémontais', "Septembre-novembre — Barolo, Barbaresco et truffes blanches d\'Alba.", 'Piedmont Vineyards', "September–November — Barolo, Barbaresco and Alba white truffles."),
        ('⛷️', 'Ski', "Décembre-mars — Via Lattea et Bardonecchia à 1h.", 'Skiing', "December–March — Via Lattea and Bardonecchia 1h away."),
    ],
    'verone': [
        ('🎭', 'Opéra aux Arènes', "Juin-septembre — opéra en plein air dans l\'amphithéâtre romain.", 'Arena Opera', "June–September — open-air opera in the Roman amphitheatre."),
        ('❤️', 'Roméo & Juliette', "Toute l\'année — balcon de Juliette, Casa di Giulietta.", 'Romeo & Juliet', "Year-round — Juliet\'s balcony, Casa di Giulietta."),
        ('🍷', 'Vin de Valpolicella', "Septembre-octobre — vendanges, Amarone et route des vins.", 'Valpolicella Wine', "September–October — harvest, Amarone and wine route."),
        ('🏛️', 'Piazza delle Erbe', "Toute l\'année — place historique, marché et architecture médiévale.", 'Piazza delle Erbe', "Year-round — historic square, market and medieval architecture."),
    ],
    'bologne': [
        ('🍝', 'Capitale du goût', "Toute l\'année — tortellini, ragù, mortadelle et Mercato delle Erbe.", 'Food Capital', "Year-round — tortellini, ragù, mortadella and Mercato delle Erbe."),
        ('🏛️', 'Portiques UNESCO', "Toute l\'année — 40 km de portiques, tours médiévales et basilique.", 'UNESCO Porticoes', "Year-round — 40 km of porticoes, medieval towers and basilica."),
        ('🎓', 'Université', "Toute l\'année — plus ancienne université d\'Europe (1088), quartier étudiant.", 'University', "Year-round — Europe\'s oldest university (1088), student quarter."),
        ('🏔️', 'Excursions', "Mai-octobre — collines bolonaises, Ravenne (mosaïques) à 1h.", 'Day Trips', "May–October — Bolognese hills, Ravenna (mosaics) 1h away."),
    ],

    # ══════════════════════════════════════════════════════════════════
    # OCÉANIE
    # ══════════════════════════════════════════════════════════════════
    'bora-bora': [
        ('🏨', 'Bungalows sur pilotis', "Mai-octobre — séjour iconique, lagon cristallin.", 'Overwater Bungalows', "May–October — iconic stay, crystalline lagoon."),
        ('🤿', 'Plongée & snorkeling', "Mai-novembre — raies manta, requins citron et jardin de corail.", 'Diving & Snorkelling', "May–November — manta rays, lemon sharks and coral garden."),
        ('🛶', 'Excursion lagon', "Toute l\'année — tour en pirogue, raies pastenagues et pique-nique.", 'Lagoon Excursion', "Year-round — outrigger tour, stingrays and picnic."),
        ('🏔️', 'Mont Otemanu', "Mai-octobre — randonnée et panorama sur le lagon.", 'Mount Otemanu', "May–October — hike and lagoon panorama."),
    ],
    'cairns': [
        ('🤿', 'Grande Barrière', "Juin-octobre — plongée et snorkeling sur le plus grand récif au monde.", 'Great Barrier Reef', "June–October — diving and snorkelling on the world\'s largest reef."),
        ('🌿', 'Forêt Daintree', "Mai-octobre — forêt tropicale la plus ancienne, croisière rivière.", 'Daintree Rainforest', "May–October — world\'s oldest rainforest, river cruise."),
        ('🐊', 'Crocodiles', "Toute l\'année — croisière Daintree River, observation de salties.", 'Crocodiles', "Year-round — Daintree River cruise, saltie spotting."),
        ('🥾', 'Atherton Tablelands', "Toute l\'année — cascades, lacs de cratère et fermes tropicales.", 'Atherton Tablelands', "Year-round — waterfalls, crater lakes and tropical farms."),
    ],
    'fidji': [
        ('🏖️', 'Plages & îles', "Mai-octobre — Mamanuca et Yasawa, sable blanc et lagon.", 'Beaches & Islands', "May–October — Mamanuca and Yasawa, white sand and lagoon."),
        ('🤿', 'Plongée', "Avril-octobre — Beqa Lagoon (requins), Great Astrolabe Reef.", 'Diving', "April–October — Beqa Lagoon (sharks), Great Astrolabe Reef."),
        ('🎭', 'Culture fidjienne', "Toute l\'année — kava, meke (danse) et villages traditionnels.", 'Fijian Culture', "Year-round — kava, meke (dance) and traditional villages."),
        ('🏄', 'Surf', "Avril-octobre — Cloudbreak et Restaurants, vagues de classe mondiale.", 'Surfing', "April–October — Cloudbreak and Restaurants, world-class waves."),
    ],
    'gili': [
        ('🐢', 'Snorkeling tortues', "Toute l\'année — Gili Trawangan, Gili Air et Gili Meno.", 'Turtle Snorkelling', "Year-round — Gili Trawangan, Gili Air and Gili Meno."),
        ('🤿', 'Plongée', "Avril-novembre — statues sous-marines, récifs et cours PADI.", 'Diving', "April–November — underwater statues, reefs and PADI courses."),
        ('🌅', 'Couchers de soleil', "Toute l\'année — hamacs, vue sur le Rinjani et Bali.", 'Sunsets', "Year-round — hammocks, Rinjani and Bali views."),
        ('🚲', 'Vélo', "Toute l\'année — pas de voitures, cidomo (calèches) et vélos.", 'Cycling', "Year-round — no cars, cidomo (horse carts) and bicycles."),
    ],
    'lombok': [
        ('🏔️', 'Mont Rinjani', "Avril-octobre — trek 2-3 jours, lac de cratère et lever de soleil.", 'Mount Rinjani', "April–October — 2–3 day trek, crater lake and sunrise."),
        ('🏖️', 'Plages du sud', "Mai-octobre — Kuta Lombok, Tanjung Aan et Mawun.", 'Southern Beaches', "May–October — Kuta Lombok, Tanjung Aan and Mawun."),
        ('🏄', 'Surf', "Mai-septembre — Desert Point, Gerupuk et vagues puissantes.", 'Surfing', "May–September — Desert Point, Gerupuk and powerful waves."),
        ('🏝️', 'Îles Gili', "Toute l\'année — Gili Trawangan, Air et Meno en bateau.", 'Gili Islands', "Year-round — Gili Trawangan, Air and Meno by boat."),
    ],
    'nusa-penida': [
        ('📸', 'Kelingking Beach', "Avril-octobre — falaise en forme de T-Rex, vue spectaculaire.", 'Kelingking Beach', "April–October — T-Rex shaped cliff, spectacular view."),
        ('🤿', 'Raies manta', "Juillet-octobre — Manta Point, snorkeling avec les raies géantes.", 'Manta Rays', "July–October — Manta Point, snorkelling with giant rays."),
        ('🏖️', 'Crystal Bay', "Avril-octobre — plage de sable blanc, snorkeling et coucher de soleil.", 'Crystal Bay', "April–October — white sand beach, snorkelling and sunset."),
        ('🌿', 'Nature sauvage', "Toute l\'année — Angel\'s Billabong, Broken Beach et forêts.", 'Wild Nature', "Year-round — Angel\'s Billabong, Broken Beach and forests."),
    ],
    'nouvelle-caledonie': [
        ('🤿', 'Lagon UNESCO', "Septembre-décembre — plus grand lagon du monde, plongée et snorkeling.", 'UNESCO Lagoon', "September–December — world\'s largest lagoon, diving and snorkelling."),
        ('🏖️', 'Îles Loyauté', "Septembre-novembre — Lifou, Maré et Ouvéa (plus belle plage).", 'Loyalty Islands', "September–November — Lifou, Maré and Ouvéa (most beautiful beach)."),
        ('🎭', 'Culture kanak', "Toute l\'année — Centre Tjibaou, coutumes et cases traditionnelles.", 'Kanak Culture', "Year-round — Tjibaou Centre, customs and traditional houses."),
        ('🥾', 'Randonnée', "Mai-octobre — Grande Terre, parcs provinciaux et forêts humides.", 'Hiking', "May–October — Grande Terre, provincial parks and rainforests."),
    ],
    'nouvelle-zelande': [
        ('🏔️', 'Fiordland & Milford Sound', "Novembre-mars — croisière, cascades et paysages de fjords.", 'Fiordland & Milford Sound', "November–March — cruise, waterfalls and fjord landscapes."),
        ('🌋', 'Tongariro Alpine Crossing', "Décembre-mars — trek volcanique d\'une journée, lacs émeraude.", 'Tongariro Alpine Crossing', "December–March — one-day volcanic trek, emerald lakes."),
        ('🏄', 'Sports d\'aventure', "Toute l\'année — saut à l\'élastique, rafting et ski (juin-oct).", 'Adventure Sports', "Year-round — bungee jumping, rafting and skiing (June–Oct)."),
        ('🐑', 'Paysages & nature', "Octobre-avril — Hobbiton, glaciers Fox/Franz Josef et Wanaka.", 'Landscapes & Nature', "October–April — Hobbiton, Fox/Franz Josef glaciers and Wanaka."),
    ],
    'polynesie': [
        ('🏨', 'Overwater bungalows', "Mai-octobre — Bora Bora, Moorea et Tikehau.", 'Overwater Bungalows', "May–October — Bora Bora, Moorea and Tikehau."),
        ('🤿', 'Plongée', "Avril-novembre — Rangiroa (requins), Fakarava et passes mythiques.", 'Diving', "April–November — Rangiroa (sharks), Fakarava and legendary passes."),
        ('🎭', 'Culture ma\'ohi', "Juillet — Heiva (festival), danse, pirogue et traditions.", 'Ma\'ohi Culture', "July — Heiva (festival), dance, outrigger and traditions."),
        ('🏄', 'Surf', "Mai-octobre — Teahupo\'o, vague mythique de Tahiti.", 'Surfing', "May–October — Teahupo\'o, Tahiti\'s legendary wave."),
    ],
    'sydney': [
        ('🏛️', 'Opéra & Harbour', "Toute l\'année — Opera House, Harbour Bridge et ferries.", 'Opera & Harbour', "Year-round — Opera House, Harbour Bridge and ferries."),
        ('🏖️', 'Bondi & plages', "Novembre-mars — Bondi, Manly et Bronte, surf et bains oceaniques.", 'Bondi & Beaches', "November–March — Bondi, Manly and Bronte, surf and ocean pools."),
        ('🥾', 'Coastal Walk', "Toute l\'année — Bondi to Coogee, North Head et Blue Mountains à 2h.", 'Coastal Walk', "Year-round — Bondi to Coogee, North Head and Blue Mountains 2h away."),
        ('🍽️', 'Gastronomie', "Toute l\'année — Chinatown, fish market et restaurants multi-ethniques.", 'Gastronomy', "Year-round — Chinatown, fish market and multi-ethnic restaurants."),
    ],
    'ubud': [
        ('🌾', 'Rizières en terrasses', "Avril-octobre — Tegallalang, Jatiluwih UNESCO et promenades.", 'Terraced Rice Paddies', "April–October — Tegallalang, UNESCO Jatiluwih and walks."),
        ('🧘', 'Yoga & bien-être', "Toute l\'année — Yoga Barn, retraites et spas balinais.", 'Yoga & Wellness', "Year-round — Yoga Barn, retreats and Balinese spas."),
        ('🛕', 'Temples de la jungle', "Toute l\'année — Tirta Empul, Goa Gajah et Monkey Forest.", 'Jungle Temples', "Year-round — Tirta Empul, Goa Gajah and Monkey Forest."),
        ('🎨', 'Art & artisanat', "Toute l\'année — galeries, peinture balinaise et marché d\'Ubud.", 'Art & Crafts', "Year-round — galleries, Balinese painting and Ubud Market."),
    ],
    'perth': [
        ('🏖️', 'Plages', "Novembre-mars — Cottesloe, Scarborough et plages de sable blanc.", 'Beaches', "November–March — Cottesloe, Scarborough and white sand beaches."),
        ('🦘', 'Rottnest Island', "Septembre-mai — quokkas, vélo et snorkeling.", 'Rottnest Island', "September–May — quokkas, cycling and snorkelling."),
        ('🍷', 'Swan Valley', "Mars-mai — vignobles, brasseries et producteurs locaux à 25 min.", 'Swan Valley', "March–May — vineyards, breweries and local producers 25 min away."),
        ('🌿', 'Kings Park', "Septembre-novembre — fleurs sauvages, vue sur le CBD et la rivière.", 'Kings Park', "September–November — wildflowers, CBD views and the river."),
    ],
    'puerto-vallarta': [
        ('🏖️', 'Plages', "Novembre-mai — Playa de los Muertos, Conchas Chinas et Sayulita.", 'Beaches', "November–May — Playa de los Muertos, Conchas Chinas and Sayulita."),
        ('🐋', 'Baleines à bosse', "Décembre-mars — observation dans la baie de Banderas.", 'Humpback Whales', "December–March — spotting in Banderas Bay."),
        ('🎨', 'Malecón & art', "Toute l\'année — sculptures sur la promenade, galeries et Zona Romántica.", 'Malecón & Art', "Year-round — promenade sculptures, galleries and Zona Romántica."),
        ('🍽️', 'Gastronomie', "Toute l\'année — fruits de mer, tacos et restaurants du Malecón.", 'Gastronomy', "Year-round — seafood, tacos and Malecón restaurants."),
    ],
}

def run():
    # Template titles to identify template cards
    template_titles_fr = {
        'Plage & farniente', 'Plongée & snorkeling', 'Gastronomie locale',
        'Culture & temples', 'Street food & marchés', 'Nature & trek',
        'Patrimoine & musées', 'Gastronomie', 'Promenade urbaine',
        'Plages', 'Patrimoine',
        'Plage & resorts', 'Shopping & luxe', 'Désert',
        'Randonnée', 'Paysages', 'Nature & faune', 'Ski',
        'Famille'
    }
    template_titles_en = {
        'Beach & Relaxation', 'Diving & Snorkelling', 'Local Food',
        'Culture & Temples', 'Street Food & Markets', 'Nature & Trekking',
        'Heritage & Museums', 'Gastronomy', 'City Walking',
        'Beaches', 'Heritage',
        'Beach & Resorts', 'Shopping & Luxury', 'Desert',
        'Hiking', 'Landscapes', 'Nature & Wildlife', 'Skiing',
        'Family'
    }

    slugs_to_replace = set(SPECIFIC_CARDS.keys())

    # 1. Process FR cards
    with open(f'{DATA}/cards.csv', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)

    # Remove template cards for slugs we're replacing
    kept = [r for r in rows if r['slug'] not in slugs_to_replace or r['titre'] not in template_titles_fr]
    # Also remove any that ARE in slugs_to_replace (catch-all)
    kept = [r for r in rows if r['slug'] not in slugs_to_replace]

    # Add new specific cards
    for slug, cards in SPECIFIC_CARDS.items():
        for icon, titre_fr, texte_fr, title_en, text_en in cards:
            kept.append({'slug': slug, 'icon': icon, 'titre': titre_fr, 'texte': texte_fr})

    with open(f'{DATA}/cards.csv', 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(kept)

    # 2. Process EN cards
    with open(f'{DATA}/cards_en.csv', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        fieldnames_en = reader.fieldnames
        rows_en = list(reader)

    kept_en = [r for r in rows_en if r['slug'] not in slugs_to_replace]

    for slug, cards in SPECIFIC_CARDS.items():
        for icon, titre_fr, texte_fr, title_en, text_en in cards:
            kept_en.append({'slug': slug, 'icon': icon, 'title': title_en, 'text': text_en})

    with open(f'{DATA}/cards_en.csv', 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fieldnames_en)
        w.writeheader()
        w.writerows(kept_en)

    print(f"Replaced template cards for {len(slugs_to_replace)} destinations")
    print(f"FR cards total: {len(kept)}")
    print(f"EN cards total: {len(kept_en)}")

    # Verify no template cards remain
    from collections import defaultdict
    slug_cards = defaultdict(list)
    for c in kept:
        slug_cards[c['slug']].append(c['titre'])
    
    template_remaining = 0
    for slug, titles in slug_cards.items():
        if all(t in template_titles_fr for t in titles):
            template_remaining += 1
    print(f"Template-only destinations remaining: {template_remaining}")

if __name__ == '__main__':
    run()
