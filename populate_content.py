#!/usr/bin/env python3
"""
Populate missing hero_sub (taglines) and project cards for 236 destinations.
Updates: data/destinations.csv, data/cards.csv, data/cards_en.csv
"""
import csv, os

DATA = 'data'

# ─── TAGLINES ──────────────────────────────────────────────────────────
# Format: slug → (hero_sub_fr, hero_sub_en)
TAGLINES = {
    # === AFRIQUE ===
    'dakar': (
        "Dakar, entre océan et Sahel — rythmes du mbalax, île de Gorée et surf sur la corniche.",
        "Dakar, where the Atlantic meets the Sahel — Gorée Island, vibrant rhythms and surf along the corniche."
    ),
    'diani': (
        "Diani Beach, sable blanc et récif corallien sur la côte kenyane — l'une des plus belles plages d'Afrique de l'Est.",
        "Diani Beach, white sand and coral reef on Kenya's coast — one of East Africa's finest beaches."
    ),
    'kenya': (
        "Kenya, terre de safaris et de paysages grandioses — du Masai Mara au littoral de l'océan Indien.",
        "Kenya, land of safaris and dramatic landscapes — from the Masai Mara to the Indian Ocean coast."
    ),
    'madagascar': (
        "Madagascar, île-continent à la biodiversité unique — baobabs, lémuriens et plages vierges.",
        "Madagascar, an island continent with unique biodiversity — baobabs, lemurs and pristine beaches."
    ),
    'namibie': (
        "Namibie, déserts ocre et faune sauvage — Sossusvlei, Etosha et la Skeleton Coast.",
        "Namibia, ochre deserts and wildlife — Sossusvlei, Etosha and the Skeleton Coast."
    ),
    'nosybe': (
        "Nosy Be, île aux parfums de Madagascar — plages turquoise, ylang-ylang et observation des baleines.",
        "Nosy Be, Madagascar's perfume island — turquoise beaches, ylang-ylang and whale watching."
    ),
    'senegal': (
        "Sénégal, terre de teranga — entre plages atlantiques, brousse du Siné-Saloum et culture wolof.",
        "Senegal, land of teranga — Atlantic beaches, Sine-Saloum mangroves and Wolof culture."
    ),
    'tanzanie': (
        "Tanzanie, du Kilimandjaro à Zanzibar — grande migration du Serengeti et plages de rêve.",
        "Tanzania, from Kilimanjaro to Zanzibar — the Serengeti great migration and dream beaches."
    ),

    # === AMÉRIQUES ===
    'antigua': (
        "Antigua, 365 plages pour 365 jours — eaux caribéennes, récifs et Nelson's Dockyard classé UNESCO.",
        "Antigua, 365 beaches for 365 days — Caribbean waters, reefs and UNESCO-listed Nelson's Dockyard."
    ),
    'aruba': (
        "Aruba, île heureuse des Caraïbes — plages blanches, alizés constants et soleil quasi garanti.",
        "Aruba, the happy island — white beaches, constant trade winds and near-guaranteed sunshine."
    ),
    'bahamas': (
        "Bahamas, archipel des eaux turquoise — 700 îles entre Nassau, Exumas et Eleuthera.",
        "Bahamas, turquoise archipelago — 700 islands from Nassau to Exumas and Eleuthera."
    ),
    'belize': (
        "Belize, barrière de corail et temples mayas en Amérique centrale — plongée, jungle et culture garifuna.",
        "Belize, barrier reef and Maya temples in Central America — diving, jungle and Garifuna culture."
    ),
    'bermudes': (
        "Bermudes, plages roses et maisons pastel au milieu de l'Atlantique — à 2h de la côte est américaine.",
        "Bermuda, pink sand beaches and pastel houses in the mid-Atlantic — 2 hours from the US East Coast."
    ),
    'bogota': (
        "Bogota, capitale colombienne perchée à 2600m — musées, street art et cuisine en plein essor.",
        "Bogotá, Colombia's capital perched at 2,600m — museums, street art and a booming food scene."
    ),
    'bolivie': (
        "Bolivie, entre Salar d'Uyuni et Altiplano — paysages lunaires, culture andine et prix défiant toute concurrence.",
        "Bolivia, from the Uyuni salt flats to the Altiplano — lunar landscapes, Andean culture and unbeatable prices."
    ),
    'boston': (
        "Boston, berceau de l'indépendance américaine — universités prestigieuses, feuillage d'automne et fruits de mer.",
        "Boston, cradle of American independence — prestigious universities, fall foliage and seafood."
    ),
    'cabo-san-lucas': (
        "Cabo San Lucas, entre désert et Pacifique — arche d'El Arco, observation des baleines et resorts mexicains.",
        "Cabo San Lucas, where desert meets the Pacific — El Arco arch, whale watching and Mexican resorts."
    ),
    'cartagene': (
        "Carthagène, cité coloniale sur les Caraïbes — remparts, salsa et cuisine afro-colombienne.",
        "Cartagena, colonial city on the Caribbean — ramparts, salsa and Afro-Colombian cuisine."
    ),
    'chicago': (
        "Chicago, architecture et jazz au bord du lac Michigan — deep-dish pizza, musées et skyline iconique.",
        "Chicago, architecture and jazz on Lake Michigan — deep-dish pizza, museums and an iconic skyline."
    ),
    'chili': (
        "Chili, entre désert d'Atacama et glaciers de Patagonie — 4300 km de contrastes extrêmes.",
        "Chile, from the Atacama Desert to Patagonian glaciers — 4,300 km of extreme contrasts."
    ),
    'colombie': (
        "Colombie, des Caraïbes aux Andes — café, salsa, villes coloniales et biodiversité exceptionnelle.",
        "Colombia, from the Caribbean to the Andes — coffee, salsa, colonial towns and exceptional biodiversity."
    ),
    'curacao': (
        "Curaçao, façades colorées et plages secrètes — les Caraïbes néerlandaises hors des sentiers battus.",
        "Curaçao, colourful façades and hidden beaches — the Dutch Caribbean off the beaten path."
    ),
    'cuzco': (
        "Cuzco, ancienne capitale inca à 3400m — porte d'entrée du Machu Picchu et cœur andin du Pérou.",
        "Cusco, ancient Inca capital at 3,400m — gateway to Machu Picchu and heart of Andean Peru."
    ),
    'equateur': (
        "Équateur, quatre mondes en un — Andes, Amazonie, côte Pacifique et Galápagos.",
        "Ecuador, four worlds in one — Andes, Amazon, Pacific coast and the Galápagos."
    ),
    'galapagos': (
        "Galápagos, laboratoire vivant de l'évolution — faune endémique, plongée et paysages volcaniques uniques au monde.",
        "Galápagos, a living laboratory of evolution — endemic wildlife, diving and volcanic landscapes found nowhere else."
    ),
    'guatemala': (
        "Guatemala, volcans et cités mayas — Antigua, lac Atitlán et ruines de Tikal en pleine jungle.",
        "Guatemala, volcanoes and Maya cities — Antigua, Lake Atitlán and Tikal ruins deep in the jungle."
    ),
    'guadeloupe': (
        "Guadeloupe, papillon des Caraïbes — plages de Grande-Terre, forêt tropicale de Basse-Terre et créolité vivante.",
        "Guadeloupe, Caribbean butterfly — Grande-Terre beaches, Basse-Terre rainforest and vibrant Creole culture."
    ),
    'guyane': (
        "Guyane, Amazonie française — forêt primaire, fusées d'Ariane et biodiversité équatoriale.",
        "French Guiana, France's slice of the Amazon — primary forest, Ariane rockets and equatorial biodiversity."
    ),
    'isla-holbox': (
        "Holbox, île sans voitures au large du Yucatán — bioluminescence, requins-baleines et hamacs sur la plage.",
        "Holbox, a car-free island off the Yucatán — bioluminescence, whale sharks and hammocks on the beach."
    ),
    'key-west': (
        "Key West, bout de route de la Floride — ambiance tropicale, maison d'Hemingway et couchers de soleil à Mallory Square.",
        "Key West, end of the road in Florida — tropical vibes, Hemingway's house and sunsets at Mallory Square."
    ),
    'las-vegas': (
        "Las Vegas, oasis du désert du Nevada — casinos, shows et excursions vers le Grand Canyon.",
        "Las Vegas, desert oasis in Nevada — casinos, shows and day trips to the Grand Canyon."
    ),
    'machu-picchu': (
        "Machu Picchu, citadelle inca perchée dans les nuages — l'une des sept merveilles du monde moderne.",
        "Machu Picchu, Inca citadel perched in the clouds — one of the seven modern wonders of the world."
    ),
    'martinique': (
        "Martinique, île aux fleurs des Caraïbes — montagne Pelée, plages de sable noir et rhum AOC.",
        "Martinique, Caribbean island of flowers — Mount Pelée, black sand beaches and AOC rum."
    ),
    'mayotte': (
        "Mayotte, lagon aux eaux turquoise de l'océan Indien — récif corallien, tortues marines et culture mahoraise.",
        "Mayotte, turquoise lagoon in the Indian Ocean — coral reef, sea turtles and Mahorais culture."
    ),
    'medellin': (
        "Medellín, cité de l'éternel printemps — street art, innovation urbaine et climat tempéré toute l'année.",
        "Medellín, city of eternal spring — street art, urban innovation and mild climate year-round."
    ),
    'mexico': (
        "Mexico, mégapole millénaire — pyramides aztèques, cantinas, musées de Frida Kahlo et cuisine UNESCO.",
        "Mexico City, ancient megalopolis — Aztec pyramids, cantinas, Frida Kahlo museums and UNESCO-listed cuisine."
    ),
    'montreal': (
        "Montréal, métropole francophone d'Amérique du Nord — festivals, bagels, quartiers bilingues et hivers mythiques.",
        "Montréal, North America's French-speaking metropolis — festivals, bagels, bilingual neighbourhoods and legendary winters."
    ),
    'nicaragua': (
        "Nicaragua, volcans et lacs d'Amérique centrale — Granada coloniale, surf à San Juan del Sur et île d'Ometepe.",
        "Nicaragua, volcanoes and lakes of Central America — colonial Granada, surf at San Juan del Sur and Ometepe Island."
    ),
    'nouvelle-orleans': (
        "Nouvelle-Orléans, berceau du jazz — French Quarter, gumbo, Mardi Gras et âme créole.",
        "New Orleans, birthplace of jazz — French Quarter, gumbo, Mardi Gras and Creole soul."
    ),
    'oaxaca': (
        "Oaxaca, capitale de la gastronomie mexicaine — mezcal, moles, ruines zapotèques et artisanat coloré.",
        "Oaxaca, Mexico's culinary capital — mezcal, moles, Zapotec ruins and colourful crafts."
    ),
    'orlando': (
        "Orlando, capitale mondiale des parcs à thèmes — Walt Disney World, Universal Studios et météo subtropicale.",
        "Orlando, theme park capital of the world — Walt Disney World, Universal Studios and subtropical weather."
    ),
    'panama': (
        "Panama, entre deux océans — canal iconique, gratte-ciel, plages caribéennes et forêt tropicale à 30 min du centre.",
        "Panama, between two oceans — iconic canal, skyscrapers, Caribbean beaches and rainforest 30 min from downtown."
    ),
    'patagonie': (
        "Patagonie, bout du monde entre glaciers et pampas — Torres del Paine, Perito Moreno et vents légendaires.",
        "Patagonia, end of the world between glaciers and pampas — Torres del Paine, Perito Moreno and legendary winds."
    ),
    'perou': (
        "Pérou, entre Andes et Amazonie — Machu Picchu, ceviche, lignes de Nazca et lac Titicaca.",
        "Peru, between the Andes and the Amazon — Machu Picchu, ceviche, Nazca Lines and Lake Titicaca."
    ),
    'playa-del-carmen': (
        "Playa del Carmen, Riviera Maya — plages caribéennes, cenotes, ruines de Tulum et vie nocturne sur la Quinta Avenida.",
        "Playa del Carmen, Riviera Maya — Caribbean beaches, cenotes, Tulum ruins and nightlife on Quinta Avenida."
    ),
    'porto-rico': (
        "Porto Rico, entre plages caribéennes et forêt tropicale El Yunque — salsa, vieux San Juan et baie bioluminescente.",
        "Puerto Rico, Caribbean beaches and El Yunque rainforest — salsa, old San Juan and bioluminescent bay."
    ),
    'punta-cana': (
        "Punta Cana, plages de cocotiers et hôtels all-inclusive — la destination Caraïbes la plus accessible depuis l'Europe.",
        "Punta Cana, coconut-lined beaches and all-inclusive resorts — the most accessible Caribbean destination from Europe."
    ),
    'quebec-ville': (
        "Québec, ville fortifiée d'Amérique du Nord — Château Frontenac, rues pavées et carnaval d'hiver légendaire.",
        "Québec City, North America's only walled city — Château Frontenac, cobblestones and a legendary winter carnival."
    ),
    'republique-dominicaine': (
        "République Dominicaine, plages de carte postale et merengue — de Punta Cana aux montagnes de Jarabacoa.",
        "Dominican Republic, postcard beaches and merengue — from Punta Cana to the mountains of Jarabacoa."
    ),
    'saint-barthelemy': (
        "Saint-Barthélemy, luxe discret des Caraïbes — plages intimes, gastronomie française et ambiance jet-set.",
        "Saint Barthélemy, discreet Caribbean luxury — intimate beaches, French gastronomy and jet-set atmosphere."
    ),
    'saint-lucie': (
        "Sainte-Lucie, Pitons volcaniques et jungle tropicale — plages noires, sources chaudes et plongée.",
        "Saint Lucia, volcanic Pitons and tropical jungle — black beaches, hot springs and diving."
    ),
    'saint-martin': (
        "Saint-Martin, île binationale des Caraïbes — côté français raffiné, côté néerlandais festif.",
        "Saint Martin, a binational Caribbean island — refined French side, festive Dutch side."
    ),
    'san-francisco': (
        "San Francisco, entre brouillard et soleil — Golden Gate, cable cars, quartiers éclectiques et cuisine fusion.",
        "San Francisco, between fog and sun — Golden Gate, cable cars, eclectic neighbourhoods and fusion cuisine."
    ),
    'santiago': (
        "Santiago du Chili, métropole andine — vignobles, street art, cordillère à 1h et gastronomie en plein essor.",
        "Santiago, Andean metropolis — vineyards, street art, mountains 1h away and a booming food scene."
    ),
    'seattle': (
        "Seattle, entre Pacifique et Cascades — café artisanal, Pike Place Market et nature omniprésente.",
        "Seattle, between the Pacific and the Cascades — craft coffee, Pike Place Market and nature everywhere."
    ),
    'trinite-et-tobago': (
        "Trinité-et-Tobago, carnaval et biodiversité — le plus grand carnaval des Caraïbes et récifs de Tobago.",
        "Trinidad and Tobago, carnival and biodiversity — the Caribbean's biggest carnival and Tobago's reefs."
    ),
    'toronto': (
        "Toronto, mosaïque multiculturelle — CN Tower, Kensington Market, quartiers du monde entier et chutes du Niagara à 1h30.",
        "Toronto, multicultural mosaic — CN Tower, Kensington Market, world neighbourhoods and Niagara Falls 90 min away."
    ),
    'uruguay': (
        "Uruguay, discret voisin de l'Argentine — Montevideo décontractée, Punta del Este et plages sauvages de Rocha.",
        "Uruguay, Argentina's discreet neighbour — laid-back Montevideo, Punta del Este and wild Rocha beaches."
    ),
    'valparaiso': (
        "Valparaíso, port bohème aux maisons colorées — funiculaires centenaires, street art et poésie de Neruda.",
        "Valparaíso, bohemian port of colourful houses — century-old funiculars, street art and Neruda's poetry."
    ),
    'vancouver': (
        "Vancouver, entre montagnes et Pacifique — Stanley Park, quartier chinois et ski à 30 minutes du centre.",
        "Vancouver, between mountains and the Pacific — Stanley Park, Chinatown and skiing 30 minutes from downtown."
    ),
    'washington': (
        "Washington, capitale fédérale — monuments, musées Smithsonian gratuits et cerisiers du Tidal Basin.",
        "Washington D.C., federal capital — monuments, free Smithsonian museums and Tidal Basin cherry blossoms."
    ),
    'yellowstone': (
        "Yellowstone, premier parc national au monde — geysers, bisons, sources chaudes et paysages volcaniques.",
        "Yellowstone, world's first national park — geysers, bison, hot springs and volcanic landscapes."
    ),

    # === ASIE ===
    'baie-halong': (
        "Baie d'Hạ Long, 2000 îlots karstiques sur la mer — l'un des paysages les plus spectaculaires du Viêt Nam.",
        "Hạ Long Bay, 2,000 karst islets rising from the sea — one of Vietnam's most spectacular landscapes."
    ),
    'boracay': (
        "Boracay, White Beach et eaux turquoise — la plus célèbre île balnéaire des Philippines.",
        "Boracay, White Beach and turquoise waters — the Philippines' most famous beach island."
    ),
    'borneo': (
        "Bornéo, forêt primaire et orangs-outans — plongée à Sipadan, grottes de Mulu et aventure sauvage.",
        "Borneo, primary forest and orangutans — diving at Sipadan, Mulu caves and wild adventure."
    ),
    'busan': (
        "Busan, deuxième ville de Corée — temples en bord de mer, marchés de poisson et plages urbaines.",
        "Busan, South Korea's second city — seaside temples, fish markets and urban beaches."
    ),
    'cambodge': (
        "Cambodge, Angkor Wat et rizières — temples khmers millénaires, Phnom Penh vibrante et côte de Sihanoukville.",
        "Cambodia, Angkor Wat and rice paddies — millennial Khmer temples, vibrant Phnom Penh and the Sihanoukville coast."
    ),
    'canggu': (
        "Canggu, Bali version surf et digital nomads — rizières, beach clubs et couchers de soleil sur l'océan Indien.",
        "Canggu, Bali's surf and digital nomad hub — rice paddies, beach clubs and Indian Ocean sunsets."
    ),
    'cebu': (
        "Cebu, Philippines entre plongée et cascades — requins-baleines d'Oslob, chutes de Kawasan et îlots vierges.",
        "Cebu, Philippines between diving and waterfalls — Oslob whale sharks, Kawasan Falls and untouched islets."
    ),
    'chiang-mai': (
        "Chiang Mai, capitale culturelle du nord thaïlandais — temples dorés, marchés nocturnes et montagnes brumeuses.",
        "Chiang Mai, cultural capital of northern Thailand — golden temples, night markets and misty mountains."
    ),
    'da-lat': (
        "Đà Lạt, station climatique des hauts plateaux vietnamiens — cascades, café d'altitude et architecture coloniale.",
        "Đà Lạt, hill station of the Vietnamese highlands — waterfalls, highland coffee and colonial architecture."
    ),
    'da-nang': (
        "Da Nang, entre plages et montagnes de marbre — Bà Nà Hills, pont doré et My Khe Beach.",
        "Da Nang, between beaches and Marble Mountains — Bà Nà Hills, Golden Bridge and My Khe Beach."
    ),
    'delhi': (
        "Delhi, mégapole aux contrastes extrêmes — forts moghols, Old Delhi chaotique et cuisine de rue légendaire.",
        "Delhi, a megalopolis of extreme contrasts — Mughal forts, chaotic Old Delhi and legendary street food."
    ),
    'el-nido': (
        "El Nido, lagons cachés et falaises karstiques de Palawan — l'un des plus beaux paysages maritimes d'Asie.",
        "El Nido, hidden lagoons and karst cliffs of Palawan — one of Asia's most beautiful seascapes."
    ),
    'hanoi': (
        "Hanoï, vieille ville millénaire — cyclo-pousses, phở matinal, lac Hoàn Kiếm et chaos urbain envoûtant.",
        "Hanoi, ancient old quarter — cyclos, morning phở, Hoàn Kiếm Lake and captivating urban chaos."
    ),
    'hiroshima': (
        "Hiroshima, mémoire et renaissance — Mémorial de la Paix, île de Miyajima et okonomiyaki.",
        "Hiroshima, memory and rebirth — Peace Memorial, Miyajima Island and okonomiyaki."
    ),
    'ho-chi-minh': (
        "Hô Chi Minh-Ville, énergie du sud vietnamien — tunnels de Củ Chi, marchés flottants du Mékong et vie nocturne.",
        "Ho Chi Minh City, southern Vietnam's energy — Củ Chi tunnels, Mekong floating markets and nightlife."
    ),
    'hong-kong': (
        "Hong Kong, skyline vertical entre mer et montagnes — dim sum, Star Ferry et randonnées insoupçonnées.",
        "Hong Kong, vertical skyline between sea and mountains — dim sum, Star Ferry and unexpected hikes."
    ),
    'java': (
        "Java, île volcanique la plus peuplée d'Indonésie — Borobudur, Bromo au lever du soleil et Yogyakarta culturelle.",
        "Java, Indonesia's most populated volcanic island — Borobudur, sunrise at Bromo and cultural Yogyakarta."
    ),
    'jeju': (
        "Jeju, île volcanique de Corée du Sud — Hallasan, plongeuses haenyeo et côtes de lave noire.",
        "Jeju, South Korea's volcanic island — Hallasan, haenyeo divers and black lava coastline."
    ),
    'kerala': (
        "Kerala, God's Own Country — backwaters, plantations de thé, ayurveda et plages de la côte de Malabar.",
        "Kerala, God's Own Country — backwaters, tea plantations, Ayurveda and Malabar Coast beaches."
    ),
    'koh-lanta': (
        "Koh Lanta, Thaïlande paisible — plages désertes, mangroves et ambiance décontractée loin des foules.",
        "Koh Lanta, peaceful Thailand — deserted beaches, mangroves and a laid-back vibe away from the crowds."
    ),
    'koh-phi-phi': (
        "Koh Phi Phi, beauté spectaculaire entre falaises calcaires — Maya Bay, plongée et fête tropicale.",
        "Koh Phi Phi, spectacular beauty between limestone cliffs — Maya Bay, diving and tropical partying."
    ),
    'koh-samui': (
        "Koh Samui, île tropicale du golfe de Thaïlande — plages de cocotiers, temples dorés et spas luxueux.",
        "Koh Samui, tropical island in the Gulf of Thailand — coconut beaches, golden temples and luxury spas."
    ),
    'koh-tao': (
        "Koh Tao, île de la plongée — certifications PADI les moins chères au monde et fonds marins préservés.",
        "Koh Tao, the diving island — the world's cheapest PADI certifications and pristine marine life."
    ),
    'komodo': (
        "Komodo, royaume des dragons et des fonds marins — parc national UNESCO, raies manta et plages roses.",
        "Komodo, kingdom of dragons and marine life — UNESCO national park, manta rays and pink beaches."
    ),
    'krabi': (
        "Krabi, falaises calcaires et îles d'Andaman — Railay Beach, Four Islands et escalade de renommée mondiale.",
        "Krabi, limestone cliffs and Andaman islands — Railay Beach, Four Islands and world-class rock climbing."
    ),
    'kuala-lumpur': (
        "Kuala Lumpur, tours Petronas et diversité culinaire — métissage malais, chinois et indien dans chaque quartier.",
        "Kuala Lumpur, Petronas Towers and culinary diversity — Malay, Chinese and Indian fusion in every district."
    ),
    'kyoto': (
        "Kyoto, ancienne capitale impériale — 2000 temples, cerisiers en fleurs, geishas de Gion et jardins zen.",
        "Kyoto, ancient imperial capital — 2,000 temples, cherry blossoms, Gion geishas and Zen gardens."
    ),
    'langkawi': (
        "Langkawi, archipel malaisien duty-free — plages de sable blanc, mangroves et géoparc UNESCO.",
        "Langkawi, Malaysia's duty-free archipelago — white sand beaches, mangroves and UNESCO Geopark."
    ),
    'laos': (
        "Laos, joyau discret d'Asie du Sud-Est — temples de Luang Prabang, Mékong et grottes de Vang Vieng.",
        "Laos, a discreet gem of Southeast Asia — Luang Prabang temples, Mekong River and Vang Vieng caves."
    ),
    'luang-prabang': (
        "Luang Prabang, ville sacrée du Mékong — procession des moines à l'aube, cascades de Kuang Si et cuisine lao.",
        "Luang Prabang, sacred city on the Mekong — dawn monk processions, Kuang Si Falls and Lao cuisine."
    ),
    'macao': (
        "Macao, Las Vegas de l'Asie — casinos, héritage colonial portugais et egg tarts légendaires.",
        "Macao, the Las Vegas of Asia — casinos, Portuguese colonial heritage and legendary egg tarts."
    ),
    'myanmar': (
        "Myanmar, pagodes dorées et Bagan au lever du soleil — 2000 temples, lac Inle et culture birmane préservée.",
        "Myanmar, golden pagodas and Bagan at sunrise — 2,000 temples, Inle Lake and preserved Burmese culture."
    ),
    'nepal': (
        "Népal, toit du monde — trek de l'Annapurna, Everest Base Camp et temples de la vallée de Katmandou.",
        "Nepal, roof of the world — Annapurna trek, Everest Base Camp and Kathmandu Valley temples."
    ),
    'nha-trang': (
        "Nha Trang, riviera vietnamienne — plages urbaines, îles accessibles en bateau et plongée sur les récifs.",
        "Nha Trang, the Vietnamese riviera — urban beaches, island-hopping by boat and reef diving."
    ),
    'okinawa': (
        "Okinawa, tropiques du Japon — plages de corail, cuisine de longévité et culture Ryūkyū unique.",
        "Okinawa, tropical Japan — coral beaches, longevity cuisine and unique Ryūkyū culture."
    ),
    'osaka': (
        "Osaka, capitale culinaire du Japon — takoyaki, Dōtonbori, château et ambiance populaire sans filtre.",
        "Osaka, Japan's culinary capital — takoyaki, Dōtonbori, castle and no-frills popular atmosphere."
    ),
    'palawan': (
        "Palawan, dernière frontière des Philippines — rivière souterraine UNESCO, lagons et récifs vierges.",
        "Palawan, the last frontier of the Philippines — UNESCO underground river, lagoons and pristine reefs."
    ),
    'pattaya': (
        "Pattaya, station balnéaire du golfe de Thaïlande — plages, temples et îles accessibles en speed boat.",
        "Pattaya, Gulf of Thailand beach resort — beaches, temples and islands accessible by speedboat."
    ),
    'pekin': (
        "Pékin, cité impériale millénaire — Cité Interdite, Grande Muraille et canard laqué.",
        "Beijing, ancient imperial city — Forbidden City, Great Wall and Peking duck."
    ),
    'penang': (
        "Penang, perle de la Malaisie — street food d'exception, street art de George Town UNESCO et temples colline.",
        "Penang, pearl of Malaysia — exceptional street food, George Town UNESCO street art and hilltop temples."
    ),
    'philippines': (
        "Philippines, 7000 îles entre Pacifique et mer de Chine — plages, plongée, rizières de Banaue et accueil chaleureux.",
        "Philippines, 7,000 islands between the Pacific and the South China Sea — beaches, diving, Banaue rice terraces and warm hospitality."
    ),
    'phnom-penh': (
        "Phnom Penh, capitale cambodgienne en pleine renaissance — Palais Royal, marchés animés et rives du Mékong.",
        "Phnom Penh, Cambodia's capital in renaissance — Royal Palace, bustling markets and Mekong riverfront."
    ),
    'phu-quoc': (
        "Phú Quốc, île tropicale du Viêt Nam — plages de sable blanc, sauce nuoc mam et couchers de soleil spectaculaires.",
        "Phú Quốc, Vietnam's tropical island — white sand beaches, nuoc mam sauce and spectacular sunsets."
    ),
    'rajasthan': (
        "Rajasthan, terre des maharajas — forteresses, palais, désert du Thar et couleurs de Jaipur, Udaipur, Jodhpur.",
        "Rajasthan, land of the maharajas — fortresses, palaces, Thar Desert and the colours of Jaipur, Udaipur, Jodhpur."
    ),
    'sapa': (
        "Sa Pa, rizières en terrasses du nord Viêt Nam — trekking ethnique, brumes montagnardes et culture H'Mông.",
        "Sa Pa, terraced rice paddies of northern Vietnam — ethnic trekking, mountain mists and H'Mông culture."
    ),
    'seoul': (
        "Séoul, mégapole entre tradition et K-pop — palais Joseon, street food, quartiers branchés et technologie omniprésente.",
        "Seoul, megalopolis between tradition and K-pop — Joseon palaces, street food, trendy districts and cutting-edge tech."
    ),
    'shanghai': (
        "Shanghai, skyline futuriste sur le Huangpu — Bund colonial, French Concession et cuisine shanghainaise.",
        "Shanghai, futuristic skyline on the Huangpu — colonial Bund, French Concession and Shanghainese cuisine."
    ),
    'siargao': (
        "Siargao, capitale du surf philippin — Cloud 9, lagons de Sugba et ambiance décontractée.",
        "Siargao, surf capital of the Philippines — Cloud 9, Sugba Lagoon and laid-back vibes."
    ),
    'sri-lanka': (
        "Sri Lanka, île aux trésors de l'océan Indien — temples bouddhistes, plantations de thé, plages et safaris.",
        "Sri Lanka, treasure island of the Indian Ocean — Buddhist temples, tea plantations, beaches and safaris."
    ),
    'taipei': (
        "Taipei, entre temples et gratte-ciel — marchés nocturnes, Taipei 101, sources chaudes et montagnes accessibles.",
        "Taipei, between temples and skyscrapers — night markets, Taipei 101, hot springs and accessible mountains."
    ),

    # === ASIE CENTRALE / MOYEN-ORIENT ===
    'abu-dhabi': (
        "Abu Dhabi, luxe et culture dans le désert — Louvre Abu Dhabi, mosquée Sheikh Zayed et mangroves.",
        "Abu Dhabi, luxury and culture in the desert — Louvre Abu Dhabi, Sheikh Zayed Mosque and mangroves."
    ),
    'doha': (
        "Doha, perle du Golfe — musée d'Art islamique, souks et skyline futuriste sur la corniche.",
        "Doha, pearl of the Gulf — Museum of Islamic Art, souks and a futuristic skyline on the Corniche."
    ),
    'jordanie': (
        "Jordanie, Pétra et mer Morte — cité nabatéenne, désert du Wadi Rum et flottaison à -430m.",
        "Jordan, Petra and the Dead Sea — Nabataean city, Wadi Rum desert and floating at -430m."
    ),
    'oman': (
        "Oman, entre fjords et désert — wadis turquoise, montagnes du Hajar et accueil bédouin authentique.",
        "Oman, between fjords and desert — turquoise wadis, Hajar mountains and authentic Bedouin hospitality."
    ),
    'ouzbekistan': (
        "Ouzbékistan, joyau de la route de la Soie — Samarcande, Boukhara, Khiva et architecture timouride.",
        "Uzbekistan, jewel of the Silk Road — Samarkand, Bukhara, Khiva and Timurid architecture."
    ),
    'georgie': (
        "Géorgie, entre Caucase et mer Noire — vin naturel, monastères perchés et cuisine généreuse.",
        "Georgia, between the Caucasus and the Black Sea — natural wine, perched monasteries and generous cuisine."
    ),
    'tbilissi': (
        "Tbilissi, capitale géorgienne aux bains sulfureux — vieille ville, forteresse de Narikala et vie nocturne émergente.",
        "Tbilisi, Georgian capital with sulphur baths — old town, Narikala fortress and emerging nightlife."
    ),
    'tel-aviv': (
        "Tel-Aviv, métropole méditerranéenne — plages urbaines, Bauhaus, cuisine fusion et vie nocturne intense.",
        "Tel Aviv, Mediterranean metropolis — urban beaches, Bauhaus, fusion cuisine and intense nightlife."
    ),

    # === EUROPE ===
    'albanie': (
        "Albanie, riviera secrète des Balkans — plages vierges, citadelles ottomanes et prix imbattables.",
        "Albania, the Balkans' secret riviera — pristine beaches, Ottoman citadels and unbeatable prices."
    ),
    'athenes': (
        "Athènes, berceau de la civilisation occidentale — Acropole, quartier de Plaka et cuisine grecque authentique.",
        "Athens, cradle of Western civilisation — Acropolis, Plaka district and authentic Greek cuisine."
    ),
    'bergen': (
        "Bergen, porte d'entrée des fjords norvégiens — maisons en bois de Bryggen, pluie fréquente et nature spectaculaire.",
        "Bergen, gateway to the Norwegian fjords — Bryggen's wooden houses, frequent rain and spectacular nature."
    ),
    'biarritz': (
        "Biarritz, élégance basque et vagues atlantiques — surf, phare, gastronomie et thermes face à l'océan.",
        "Biarritz, Basque elegance and Atlantic waves — surf, lighthouse, gastronomy and ocean-facing spas."
    ),
    'bilbao': (
        "Bilbao, renaissance basque autour du Guggenheim — pintxos, architecture audacieuse et côte cantabrique.",
        "Bilbao, Basque renaissance around the Guggenheim — pintxos, bold architecture and the Cantabrian coast."
    ),
    'bodrum': (
        "Bodrum, Saint-Tropez de la Turquie — château croisé, baies secrètes et vie nocturne estivale.",
        "Bodrum, Turkey's Saint-Tropez — crusader castle, hidden bays and summer nightlife."
    ),
    'bologne': (
        "Bologne, capitale gourmande de l'Émilie-Romagne — tortellini, mortadelle, portiques et université la plus ancienne d'Europe.",
        "Bologna, gourmet capital of Emilia-Romagna — tortellini, mortadella, porticoes and Europe's oldest university."
    ),
    'bratislava': (
        "Bratislava, petite capitale sur le Danube — château, vieille ville compacte et vignobles à pied.",
        "Bratislava, small capital on the Danube — castle, compact old town and vineyards on foot."
    ),
    'bruxelles': (
        "Bruxelles, capitale de l'Europe — Grand-Place, bandes dessinées, gaufres et Art nouveau.",
        "Brussels, capital of Europe — Grand-Place, comic strips, waffles and Art Nouveau."
    ),
    'bruges': (
        "Bruges, Venise du Nord — canaux médiévaux, chocolat, bière belge et beffroi iconique.",
        "Bruges, Venice of the North — medieval canals, chocolate, Belgian beer and iconic belfry."
    ),
    'bucarest': (
        "Bucarest, petit Paris des Balkans — palais du Parlement, cafés branchés et vie nocturne bouillonnante.",
        "Bucharest, little Paris of the Balkans — Palace of Parliament, trendy cafés and buzzing nightlife."
    ),
    'budapest': (
        "Budapest, perle du Danube — bains thermaux, ruinbars, parlement illuminé et cuisine hongroise généreuse.",
        "Budapest, pearl of the Danube — thermal baths, ruin bars, illuminated Parliament and hearty Hungarian cuisine."
    ),
    'cadix': (
        "Cadix, plus ancienne ville d'Europe occidentale — plages urbaines, flamenco et carnaval légendaire.",
        "Cádiz, western Europe's oldest city — urban beaches, flamenco and a legendary carnival."
    ),
    'cappadoce': (
        "Cappadoce, paysage lunaire de Turquie — montgolfières au lever du soleil, villes souterraines et hôtels troglodytes.",
        "Cappadocia, Turkey's lunar landscape — sunrise hot air balloons, underground cities and cave hotels."
    ),
    'chamonix': (
        "Chamonix, capitale mondiale de l'alpinisme — Mont-Blanc, Aiguille du Midi et ski d'exception.",
        "Chamonix, world capital of mountaineering — Mont Blanc, Aiguille du Midi and exceptional skiing."
    ),
    'chefchaouen': (
        "Chefchaouen, perle bleue du Rif marocain — ruelles indigo, montagnes et artisanat berbère.",
        "Chefchaouen, blue pearl of Morocco's Rif — indigo alleyways, mountains and Berber crafts."
    ),
    'chypre': (
        "Chypre, carrefour méditerranéen — plages dorées, sites antiques et villages de montagne entre influence grecque et turque.",
        "Cyprus, Mediterranean crossroads — golden beaches, ancient sites and mountain villages between Greek and Turkish influence."
    ),
    'cinque-terre': (
        "Cinque Terre, cinq villages colorés accrochés aux falaises de Ligurie — sentiers côtiers, pesto et vignobles en terrasses.",
        "Cinque Terre, five colourful villages clinging to Ligurian cliffs — coastal trails, pesto and terraced vineyards."
    ),
    'copenhague': (
        "Copenhague, capitale du hygge et du design — Nyhavn, Tivoli, cuisine nordique et vélos partout.",
        "Copenhagen, capital of hygge and design — Nyhavn, Tivoli, Nordic cuisine and bicycles everywhere."
    ),
    'cordoue': (
        "Cordoue, joyau du califat andalou — Mosquée-Cathédrale, patios fleuris et nuits d'été sous les orangers.",
        "Córdoba, jewel of the Andalusian caliphate — Mosque-Cathedral, flowered patios and summer nights under orange trees."
    ),
    'costa-brava': (
        "Costa Brava, criques de la Catalogne sauvage — Dalí à Cadaqués, sentiers côtiers et pinèdes sur la mer.",
        "Costa Brava, coves of wild Catalonia — Dalí in Cadaqués, coastal paths and pine forests above the sea."
    ),
    'cracovie': (
        "Cracovie, ancienne capitale royale de Pologne — Wawel, quartier juif de Kazimierz et mines de sel de Wieliczka.",
        "Kraków, Poland's former royal capital — Wawel, Kazimierz Jewish quarter and Wieliczka salt mines."
    ),
    'djerba': (
        "Djerba, île des Lotophages — plages de sable fin, synagogue de la Ghriba et artisanat tunisien.",
        "Djerba, island of the Lotus Eaters — fine sand beaches, El Ghriba Synagogue and Tunisian crafts."
    ),
    'dolomites': (
        "Dolomites, cathédrales de calcaire des Alpes italiennes — via ferrata, ski et refuges panoramiques.",
        "Dolomites, limestone cathedrals of the Italian Alps — via ferrata, skiing and panoramic mountain huts."
    ),
    'dordogne': (
        "Dordogne, France éternelle — grottes de Lascaux, châteaux médiévaux, foie gras et rivières paisibles.",
        "Dordogne, eternal France — Lascaux caves, medieval castles, foie gras and peaceful rivers."
    ),
    'dublin': (
        "Dublin, capitale littéraire et festive — pubs, Guinness, Temple Bar et falaises de Howth à 30 minutes.",
        "Dublin, literary and festive capital — pubs, Guinness, Temple Bar and Howth cliffs 30 minutes away."
    ),
    'el-hierro': (
        "El Hierro, île pionnière 100% renouvelable — plongée volcanique, forêts primaires et bout du monde canari.",
        "El Hierro, pioneer 100% renewable island — volcanic diving, ancient forests and the Canaries' edge of the world."
    ),
    'essaouira': (
        "Essaouira, cité du vent atlantique au Maroc — médina bleue, port de pêche et spot de kitesurf.",
        "Essaouira, Morocco's Atlantic wind city — blue medina, fishing port and kitesurfing spot."
    ),
    'faro': (
        "Faro, porte d'entrée de l'Algarve — lagune de Ria Formosa, vieille ville et accès aux plages dorées.",
        "Faro, gateway to the Algarve — Ria Formosa lagoon, old town and access to golden beaches."
    ),
    'fes': (
        "Fès, plus grande médina du monde — tanneries, zellige et artisanat millénaire du Maroc impérial.",
        "Fez, world's largest medina — tanneries, zellige and millennial craftsmanship of imperial Morocco."
    ),
    'fethiye': (
        "Fethiye, lagon bleu de la côte lycienne — Ölüdeniz, tombes rupestres et croisières en goélette.",
        "Fethiye, blue lagoon of the Lycian coast — Ölüdeniz, rock tombs and gulet cruises."
    ),
    'formentera': (
        "Formentera, petite sœur sauvage d'Ibiza — plages de sable blanc, eaux cristallines et vélos.",
        "Formentera, Ibiza's wild little sister — white sand beaches, crystal-clear waters and bicycles."
    ),
    'francfort': (
        "Francfort, skyline bancaire et cidre de pommes — Römerberg, musées du Main et base idéale pour l'Allemagne.",
        "Frankfurt, banking skyline and apple cider — Römerberg, Main museum mile and ideal base for Germany."
    ),
    'gdansk': (
        "Gdańsk, perle baltique de la Pologne — vieille ville hanséatique, ambre et plages de la Baltique.",
        "Gdańsk, Poland's Baltic pearl — Hanseatic old town, amber and Baltic beaches."
    ),
    'geneve': (
        "Genève, entre lac Léman et Mont-Blanc — jet d'eau, horlogerie, fondue et organisations internationales.",
        "Geneva, between Lake Geneva and Mont Blanc — jet d'eau, watchmaking, fondue and international organisations."
    ),
    'gold-coast': (
        "Gold Coast, côte dorée de l'Australie — surf à Surfers Paradise, parcs à thèmes et hinterland subtropical.",
        "Gold Coast, Australia's golden shore — surfing at Surfers Paradise, theme parks and subtropical hinterland."
    ),
    'gozo': (
        "Gozo, petite sœur rurale de Malte — temples mégalithiques, baies secrètes et plongée sur épaves.",
        "Gozo, Malta's rural little sister — megalithic temples, hidden bays and wreck diving."
    ),
    'grenade': (
        "Grenade, Alhambra et quartier de l'Albaicín — dernière cité maure d'Espagne, tapas gratuites et Sierra Nevada à 30 min.",
        "Granada, Alhambra and the Albaicín — Spain's last Moorish city, free tapas and Sierra Nevada 30 min away."
    ),
    'hambourg': (
        "Hambourg, port et entrepôts sur l'Elbe — Speicherstadt, Elbphilharmonie et quartier de St. Pauli.",
        "Hamburg, port and warehouses on the Elbe — Speicherstadt, Elbphilharmonie and St. Pauli district."
    ),
    'hammamet': (
        "Hammamet, station balnéaire tunisienne — jasmin, plages de sable fin et médina blanchie à la chaux.",
        "Hammamet, Tunisian beach resort — jasmine, fine sand beaches and whitewashed medina."
    ),
    'helsinki': (
        "Helsinki, design nordique et saunas publics — cathédrale blanche, archipel et cuisine New Nordic.",
        "Helsinki, Nordic design and public saunas — white cathedral, archipelago and New Nordic cuisine."
    ),
    'hurghada': (
        "Hurghada, plongée en mer Rouge — récifs coralliens, resorts all-inclusive et soleil 365 jours par an.",
        "Hurghada, Red Sea diving — coral reefs, all-inclusive resorts and sunshine 365 days a year."
    ),
    'hvar': (
        "Hvar, île de lavande en Croatie — jet-set adriatique, criques et l'une des villes les plus ensoleillées d'Europe.",
        "Hvar, Croatia's lavender island — Adriatic jet-set, hidden coves and one of Europe's sunniest towns."
    ),
    'hydra': (
        "Hydra, île sans voitures de Grèce — ânes, port pittoresque et ambiance artistique hors du temps.",
        "Hydra, car-free Greek island — donkeys, picturesque port and a timeless artistic atmosphere."
    ),
    'izmir': (
        "Izmir, troisième ville de Turquie — bazar de Kemeraltı, front de mer et excursions vers Éphèse.",
        "Izmir, Turkey's third city — Kemeraltı bazaar, waterfront and day trips to Ephesus."
    ),
    'kefalonia': (
        "Céphalonie, la plus grande île ionienne — grottes de Melissani, plage de Myrtos et falaises calcaires.",
        "Kefalonia, the largest Ionian island — Melissani Cave, Myrtos Beach and limestone cliffs."
    ),
    'kos': (
        "Kos, île du Dodécanèse — berceau d'Hippocrate, plages de sable et thermes naturels.",
        "Kos, Dodecanese island — birthplace of Hippocrates, sandy beaches and natural hot springs."
    ),
    'kotor': (
        "Kotor, fjord des Balkans au Monténégro — remparts médiévaux, baie spectaculaire et vieille ville vénitienne.",
        "Kotor, Balkans fjord in Montenegro — medieval ramparts, spectacular bay and Venetian old town."
    ),
    'la-gomera': (
        "La Gomera, île sauvage des Canaries — forêt de lauriers du Garajonay UNESCO et sentiers spectaculaires.",
        "La Gomera, the wild Canary Island — UNESCO Garajonay laurel forest and spectacular trails."
    ),
    'la-palma': (
        "La Palma, isla bonita des Canaries — volcan, observatoire astronomique et forêts luxuriantes.",
        "La Palma, isla bonita of the Canaries — volcano, astronomical observatory and lush forests."
    ),
    'lac-come': (
        "Lac de Côme, élégance italienne entre montagnes et eau — villas, jardins botaniques et villages pastel.",
        "Lake Como, Italian elegance between mountains and water — villas, botanical gardens and pastel villages."
    ),
    'lac-garde': (
        "Lac de Garde, plus grand lac d'Italie — de Sirmione roman au nord alpin, entre oliviers et montagnes.",
        "Lake Garda, Italy's largest lake — from Roman Sirmione to the Alpine north, between olive groves and mountains."
    ),
    'laponie': (
        "Laponie, terres arctiques de Finlande — aurores boréales, traîneaux à rennes et Père Noël à Rovaniemi.",
        "Lapland, Finland's Arctic lands — northern lights, reindeer sleighs and Santa Claus in Rovaniemi."
    ),
    'le-caire': (
        "Le Caire, mégapole millénaire sur le Nil — pyramides de Gizeh, souk de Khan el-Khalili et musée égyptien.",
        "Cairo, ancient megalopolis on the Nile — Giza pyramids, Khan el-Khalili souk and Egyptian Museum."
    ),
    'lefkada': (
        "Leucade, plages spectaculaires de la mer Ionienne — Porto Katsiki, eaux turquoise et accès par pont.",
        "Lefkada, spectacular Ionian Sea beaches — Porto Katsiki, turquoise waters and road-bridge access."
    ),
    'ljubljana': (
        "Ljubljana, capitale verte de l'Europe — rivière Ljubljanica, château perché et pont des Dragons.",
        "Ljubljana, Europe's green capital — Ljubljanica river, hilltop castle and Dragon Bridge."
    ),
    'lofoten': (
        "Îles Lofoten, fjords arctiques de Norvège — cabanes de pêcheurs, aurores boréales et soleil de minuit.",
        "Lofoten Islands, Norway's Arctic fjords — fishing cabins, northern lights and midnight sun."
    ),
    'lombok': (
        "Lombok, voisine sauvage de Bali — mont Rinjani, plages désertes et îles Gili accessibles en bateau.",
        "Lombok, Bali's wilder neighbour — Mount Rinjani, deserted beaches and Gili Islands by boat."
    ),
    'louxor': (
        "Louxor, musée à ciel ouvert de l'Égypte antique — Vallée des Rois, temple de Karnak et croisière sur le Nil.",
        "Luxor, open-air museum of ancient Egypt — Valley of the Kings, Karnak Temple and Nile cruises."
    ),
    'madrid': (
        "Madrid, capitale vibrante — Prado, Retiro, tapas de nuit et vie nocturne jusqu'à l'aube.",
        "Madrid, vibrant capital — Prado, Retiro, late-night tapas and nightlife until dawn."
    ),
    'marsa-alam': (
        "Marsa Alam, mer Rouge préservée — dugongs, récifs vierges et tranquillité loin d'Hurghada.",
        "Marsa Alam, pristine Red Sea — dugongs, virgin reefs and tranquillity away from Hurghada."
    ),
    'melbourne': (
        "Melbourne, capitale culturelle de l'Australie — street art, cafés, cricket et Great Ocean Road à 2h.",
        "Melbourne, Australia's cultural capital — street art, cafés, cricket and the Great Ocean Road 2h away."
    ),
    'milan': (
        "Milan, capitale de la mode et du design — Duomo, La Cène de Vinci, apéritivo dans les Navigli.",
        "Milan, capital of fashion and design — Duomo, Da Vinci's Last Supper and aperitivo in the Navigli."
    ),
    'milos': (
        "Milos, île volcanique aux 70 plages — Sarakiniko blanc, catacombes et Cyclades hors des sentiers battus.",
        "Milos, volcanic island with 70 beaches — white Sarakiniko, catacombs and off-the-beaten-path Cyclades."
    ),
    'montenegro': (
        "Monténégro, concentré de Balkans sur l'Adriatique — Kotor, Budva et Durmitor en un seul petit pays.",
        "Montenegro, the Balkans concentrated on the Adriatic — Kotor, Budva and Durmitor in one small country."
    ),
    'montpellier': (
        "Montpellier, ville étudiante ensoleillée du sud — Écusson médiéval, mer à 15 min et scène gastronomique.",
        "Montpellier, sunny southern university city — medieval Écusson, sea 15 min away and vibrant food scene."
    ),
    'munich': (
        "Munich, entre bière et Bavière — Marienplatz, Oktoberfest, châteaux et Alpes à 1h.",
        "Munich, between beer and Bavaria — Marienplatz, Oktoberfest, castles and Alps 1h away."
    ),
    'naples': (
        "Naples, chaos magnifique au pied du Vésuve — pizza originelle, Pompéi et golfe spectaculaire.",
        "Naples, magnificent chaos at the foot of Vesuvius — original pizza, Pompeii and a spectacular bay."
    ),
    'naxos': (
        "Naxos, plus grande île des Cyclades — plages de sable, villages de montagne et Portara antique.",
        "Naxos, largest of the Cyclades — sandy beaches, mountain villages and the ancient Portara."
    ),
    'normandie': (
        "Normandie, terre de mémoire et de saveurs — plages du Débarquement, Mont-Saint-Michel, camembert et falaises d'Étretat.",
        "Normandy, land of memory and flavours — D-Day beaches, Mont-Saint-Michel, camembert and the cliffs of Étretat."
    ),
    'nouvelle-zelande': (
        "Nouvelle-Zélande, Middle-Earth grandeur nature — fjords, volcans, moutons et sports d'aventure.",
        "New Zealand, Middle-Earth in real life — fjords, volcanoes, sheep and adventure sports."
    ),
    'oslo': (
        "Oslo, fjord et musées au bout de la Scandinavie — Munch, opéra flottant et nature urbaine.",
        "Oslo, fjord and museums at the edge of Scandinavia — Munch, floating opera house and urban nature."
    ),
    'ouarzazate': (
        "Ouarzazate, porte du Sahara — kasbah d'Aït Ben Haddou, studios de cinéma et oasis du Drâa.",
        "Ouarzazate, gateway to the Sahara — Aït Ben Haddou kasbah, film studios and Draa Valley oases."
    ),
    'palerme': (
        "Palerme, capitale chaotique de la Sicile — marchés criards, cathédrales normandes et street food.",
        "Palermo, Sicily's chaotic capital — raucous markets, Norman cathedrals and street food."
    ),
    'paphos': (
        "Paphos, berceau d'Aphrodite — mosaïques romaines, tombes des Rois et côte sauvage de Chypre.",
        "Paphos, birthplace of Aphrodite — Roman mosaics, Tombs of the Kings and Cyprus' wild coast."
    ),
    'paros': (
        "Paros, Cyclades authentique — Naoussa, plages de sable doré et vents idéaux pour le windsurf.",
        "Paros, authentic Cyclades — Naoussa, golden sandy beaches and ideal winds for windsurfing."
    ),
    'pays-basque': (
        "Pays Basque français, entre océan et montagnes — surf, pelote, piment d'Espelette et villages pittoresques.",
        "French Basque Country, between ocean and mountains — surf, pelota, Espelette pepper and picturesque villages."
    ),
    'perth': (
        "Perth, soleil et isolement sur l'océan Indien — plages immenses, vignobles et île de Rottnest.",
        "Perth, sunshine and isolation on the Indian Ocean — vast beaches, vineyards and Rottnest Island."
    ),
    'plitvice': (
        "Plitvice, lacs en cascade dans la forêt croate — 16 lacs turquoise reliés par des chutes d'eau spectaculaires.",
        "Plitvice, cascading lakes in Croatian forest — 16 turquoise lakes connected by spectacular waterfalls."
    ),
    'polynesie': (
        "Polynésie française, paradis du bout du monde — lagons, overwater bungalows et culture ma'ohi.",
        "French Polynesia, paradise at the end of the world — lagoons, overwater bungalows and Ma'ohi culture."
    ),
    'pouilles': (
        "Pouilles, talon de la botte italienne — trulli d'Alberobello, masserie, mer turquoise et orecchiette.",
        "Puglia, the heel of the Italian boot — Alberobello trulli, masserie, turquoise sea and orecchiette."
    ),
    'puerto-vallarta': (
        "Puerto Vallarta, charme mexicain sur le Pacifique — Malecón, sierra tropicale et plages de la Riviera Nayarit.",
        "Puerto Vallarta, Mexican charm on the Pacific — Malecón, tropical sierra and Riviera Nayarit beaches."
    ),
    'riga': (
        "Riga, Art nouveau et vieille ville hanséatique — la plus grande concentration d'Art nouveau au monde.",
        "Riga, Art Nouveau and Hanseatic old town — the world's largest concentration of Art Nouveau architecture."
    ),
    'rodrigues': (
        "Rodrigues, île authentique de l'océan Indien — lagon préservé, tortues géantes et créolité mauricienne.",
        "Rodrigues, authentic Indian Ocean island — pristine lagoon, giant tortoises and Mauritian Creole culture."
    ),
    'saint-pierre-et-miquelon': (
        "Saint-Pierre-et-Miquelon, France au large du Canada — brumes atlantiques, patrimoine basque et paysages subarctiques.",
        "Saint Pierre and Miquelon, France off the Canadian coast — Atlantic mists, Basque heritage and subarctic landscapes."
    ),
    'saint-sebastien': (
        "Saint-Sébastien, capitale mondiale des pintxos — plage de la Concha, vieille ville gourmande et surf urbain.",
        "San Sebastián, world capital of pintxos — La Concha beach, gourmet old town and urban surfing."
    ),
    'sharm-el-sheikh': (
        "Sharm el-Sheikh, plongée en mer Rouge — Ras Mohammed, récifs coralliens et resorts entre mer et désert.",
        "Sharm el-Sheikh, Red Sea diving — Ras Mohammed, coral reefs and resorts between sea and desert."
    ),
    'sintra': (
        "Sintra, palais enchantés à 30 min de Lisbonne — Pena coloré, Quinta da Regaleira et forêts mystérieuses.",
        "Sintra, enchanted palaces 30 min from Lisbon — colourful Pena, Quinta da Regaleira and mysterious forests."
    ),
    'sofia': (
        "Sofia, capitale méconnue des Balkans — cathédrale Alexandre Nevski, montagne Vitosha et prix doux.",
        "Sofia, the Balkans' underrated capital — Alexander Nevsky Cathedral, Vitosha Mountain and gentle prices."
    ),
    'stockholm': (
        "Stockholm, beauté nordique sur 14 îles — Gamla Stan, archipel et design scandinave.",
        "Stockholm, Nordic beauty across 14 islands — Gamla Stan, archipelago and Scandinavian design."
    ),
    'strasbourg': (
        "Strasbourg, capitale européenne au charme alsacien — Petite France, cathédrale gothique et marché de Noël légendaire.",
        "Strasbourg, European capital with Alsatian charm — Petite France, Gothic cathedral and legendary Christmas market."
    ),
    'sydney': (
        "Sydney, métropole entre océan et harbour — Opéra, Bondi Beach, surf et baies cachées.",
        "Sydney, metropolis between ocean and harbour — Opera House, Bondi Beach, surf and hidden bays."
    ),
    'tallinn': (
        "Tallinn, vieille ville médiévale la mieux préservée d'Europe du Nord — numérique, créatif et abordable.",
        "Tallinn, the best-preserved medieval old town in Northern Europe — digital, creative and affordable."
    ),
    'thessalonique': (
        "Thessalonique, deuxième ville de Grèce — tour Blanche, street food, vie nocturne et vestiges byzantins.",
        "Thessaloniki, Greece's second city — White Tower, street food, nightlife and Byzantine ruins."
    ),
    'transylvanie': (
        "Transylvanie, Roumanie authentique — châteaux, villages saxons, Carpates et légende de Dracula.",
        "Transylvania, authentic Romania — castles, Saxon villages, Carpathians and the legend of Dracula."
    ),
    'tromso': (
        "Tromsø, capitale arctique de Norvège — aurores boréales, cathédrale de glace et soleil de minuit.",
        "Tromsø, Arctic capital of Norway — northern lights, ice cathedral and midnight sun."
    ),
    'tunis': (
        "Tunis, entre médina millénaire et Sidi Bou Saïd — Carthage, cuisine tunisienne et modernité méditerranéenne.",
        "Tunis, between ancient medina and Sidi Bou Said — Carthage, Tunisian cuisine and Mediterranean modernity."
    ),
    'turin': (
        "Turin, élégance piémontaise — premier capitale d'Italie, chocolat, musée Égyptien et vignobles du Barolo.",
        "Turin, Piedmontese elegance — Italy's first capital, chocolate, Egyptian Museum and Barolo vineyards."
    ),
    'varsovie': (
        "Varsovie, phénix de l'Europe — vieille ville reconstruite UNESCO, musées poignants et vie nocturne.",
        "Warsaw, Europe's phoenix — UNESCO-rebuilt old town, poignant museums and thriving nightlife."
    ),
    'verone': (
        "Vérone, ville de Roméo et Juliette — arènes romaines, opéra en plein air et vignobles de l'Amarone.",
        "Verona, city of Romeo and Juliet — Roman arena, open-air opera and Amarone vineyards."
    ),
    'vilnius': (
        "Vilnius, capitale baroque de la Baltique — vieille ville UNESCO, street art et quartier bohème d'Užupis.",
        "Vilnius, Baltic baroque capital — UNESCO old town, street art and the bohemian Užupis district."
    ),
    'wild-atlantic-way': (
        "Wild Atlantic Way, 2500 km de côte sauvage irlandaise — falaises de Moher, pubs et paysages à couper le souffle.",
        "Wild Atlantic Way, 2,500 km of wild Irish coast — Cliffs of Moher, pubs and breathtaking landscapes."
    ),
    'zadar': (
        "Zadar, orgue marin et coucher de soleil d'Hitchcock — front de mer romain, îles Kornati à proximité.",
        "Zadar, sea organ and Hitchcock's sunset — Roman waterfront and nearby Kornati Islands."
    ),
    'zagreb': (
        "Zagreb, capitale croate méconnue — marché de Dolac, street art et cafés austro-hongrois.",
        "Zagreb, Croatia's underrated capital — Dolac market, street art and Austro-Hungarian cafés."
    ),
    'zakynthos': (
        "Zakynthos, Navagio Beach et eaux bleu électrique — l'épave la plus photographiée de Grèce.",
        "Zakynthos, Navagio Beach and electric blue waters — Greece's most photographed shipwreck."
    ),
    'zurich': (
        "Zurich, entre lac et montagnes — quartier de Niederdorf, musées, chocolat et excursions alpines.",
        "Zurich, between lake and mountains — Niederdorf quarter, museums, chocolate and Alpine excursions."
    ),

    # === OCÉANIE ===
    'bora-bora': (
        "Bora Bora, perle du Pacifique — lagon turquoise, bungalows sur pilotis et mont Otemanu.",
        "Bora Bora, pearl of the Pacific — turquoise lagoon, overwater bungalows and Mount Otemanu."
    ),
    'cairns': (
        "Cairns, porte de la Grande Barrière de Corail — forêt tropicale de Daintree, plongée et crocodiles.",
        "Cairns, gateway to the Great Barrier Reef — Daintree rainforest, diving and crocodiles."
    ),
    'fidji': (
        "Fidji, 333 îles du Pacifique Sud — lagons, culture fidjienne et couchers de soleil inoubliables.",
        "Fiji, 333 South Pacific islands — lagoons, Fijian culture and unforgettable sunsets."
    ),
    'gili': (
        "Îles Gili, trio paradisiaque sans voitures — snorkeling avec les tortues, hamacs et couchers de soleil.",
        "Gili Islands, car-free paradise trio — turtle snorkelling, hammocks and sunsets."
    ),
    'nusa-penida': (
        "Nusa Penida, falaises vertigineuses au large de Bali — Kelingking Beach, raies manta et paysages bruts.",
        "Nusa Penida, vertiginous cliffs off Bali — Kelingking Beach, manta rays and raw landscapes."
    ),
    'nouvelle-caledonie': (
        "Nouvelle-Calédonie, lagon UNESCO et culture kanak — récif corallien, pins colonnaires et Nouméa.",
        "New Caledonia, UNESCO lagoon and Kanak culture — coral reef, columnar pines and Nouméa."
    ),
    'ubud': (
        "Ubud, cœur culturel de Bali — rizières en terrasses, temples de la jungle et retraites de yoga.",
        "Ubud, cultural heart of Bali — terraced rice paddies, jungle temples and yoga retreats."
    ),

    # === ÎLES ===
    'acores': (
        "Açores, archipel volcanique en plein Atlantique — lacs de cratère, hortensias et observation des baleines.",
        "Azores, volcanic archipelago in the mid-Atlantic — crater lakes, hydrangeas and whale watching."
    ),
    'antalya': (
        "Antalya, riviera turque — plages de galets, vieille ville ottomane et cascades de Düden.",
        "Antalya, Turkish riviera — pebble beaches, Ottoman old town and Düden waterfalls."
    ),
    'cap-vert': (
        "Cap-Vert, archipel volcanique au large de l'Afrique — morabeza, musique et paysages lunaires de Fogo.",
        "Cape Verde, volcanic archipelago off Africa — morabeza, music and Fogo's lunar landscapes."
    ),
    'nouvelle-orleans': (
        "Nouvelle-Orléans, berceau du jazz — French Quarter, gumbo, Mardi Gras et âme créole.",
        "New Orleans, birthplace of jazz — French Quarter, gumbo, Mardi Gras and Creole soul."
    ),
}

# ─── PROJECT CARDS ─────────────────────────────────────────────────────
# Format: slug → [(icon, titre_fr, texte_fr, title_en, text_en), ...]
CARDS = {
    # === EUROPE ===
    'athenes': [
        ('🏛️', 'Acropole & sites antiques', "Mars-mai ou octobre — lumière idéale, moins de chaleur, foules réduites.", 'Acropolis & Ancient Sites', "March–May or October — ideal light, less heat, smaller crowds."),
        ('🍽️', 'Gastronomie & tavernes', "Toute l\'année — moussaka, souvlaki, marchés d\'Athènes et quartier de Psiri.", 'Food & Tavernas', "Year-round — moussaka, souvlaki, Athens markets and Psiri district."),
        ('🏖️', 'Plages (côte attique)', "Juin-septembre — Vouliagmeni, Glyfada et îles saroniques à 1h en ferry.", 'Beaches (Attic Coast)', "June–September — Vouliagmeni, Glyfada and Saronic islands 1h by ferry."),
        ('🎭', 'Culture & musées', "Toute l\'année — Musée national archéologique, Benaki, quartier d\'Exarcheia.", 'Culture & Museums', "Year-round — National Archaeological Museum, Benaki, Exarcheia district."),
        ('👨‍👩‍👧', 'Famille', "Avril-mai ou octobre — températures douces, Acropole sans la foule estivale.", 'Family', "April–May or October — mild temperatures, Acropolis without summer crowds."),
    ],
    'milan': [
        ('🎨', 'Art & architecture', "Mars-mai — Duomo, La Cène, Brera et quartier Navigli.", 'Art & Architecture', "March–May — Duomo, The Last Supper, Brera and Navigli district."),
        ('🛍️', 'Mode & shopping', "Janvier ou juillet — soldes. Septembre — Fashion Week.", 'Fashion & Shopping', "January or July — sales. September — Fashion Week."),
        ('🍽️', 'Gastronomie', "Toute l\'année — risotto alla milanese, ossobuco, apéritivo sur les Navigli.", 'Gastronomy', "Year-round — risotto alla milanese, ossobuco, aperitivo on the Navigli."),
        ('⚽', 'Football', "Septembre-mai — San Siro, derbys Milan AC vs Inter.", 'Football', "September–May — San Siro, AC Milan vs Inter derbies."),
        ('🏔️', 'Excursion lacs', "Mai-septembre — lac de Côme et lac Majeur à 1h.", 'Lake Day Trips', "May–September — Lake Como and Lake Maggiore 1h away."),
    ],
    'naples': [
        ('🍕', 'Pizza & street food', "Toute l\'année — pizza margherita originelle, frittatina, sfogliatella.", 'Pizza & Street Food', "Year-round — original margherita pizza, frittatina, sfogliatella."),
        ('🏛️', 'Pompéi & Herculanum', "Mars-mai ou octobre — ruines sans chaleur excessive ni foules estivales.", 'Pompeii & Herculaneum', "March–May or October — ruins without excessive heat or summer crowds."),
        ('🏖️', 'Côte amalfitaine', "Mai-juin ou septembre — accès facile depuis Naples, moins de monde qu\'en juillet-août.", 'Amalfi Coast', "May–June or September — easy access from Naples, fewer crowds than July–August."),
        ('🌋', 'Vésuve & Champs Phlégréens', "Avril-juin ou septembre-octobre — randonnée au cratère avec visibilité optimale.", 'Vesuvius & Campi Flegrei', "April–June or September–October — crater hike with optimal visibility."),
        ('👨‍👩‍👧', 'Famille', "Mai-juin — Capri, Ischia et Procida accessibles en ferry, mer déjà agréable.", 'Family', "May–June — Capri, Ischia and Procida by ferry, sea already pleasant."),
    ],
    'lac-come': [
        ('🚤', 'Croisière & villas', "Mai-septembre — Villa Carlotta, Bellagio et ferries panoramiques.", 'Cruises & Villas', "May–September — Villa Carlotta, Bellagio and panoramic ferries."),
        ('🥾', 'Randonnée', "Mai-octobre — Sentiero del Viandante et sentiers de montagne avec vues sur le lac.", 'Hiking', "May–October — Sentiero del Viandante and mountain trails with lake views."),
        ('🍽️', 'Gastronomie lacustre', "Toute l\'année — risotto al pesce persico, polenta et restaurants étoilés.", 'Lake Gastronomy', "Year-round — perch risotto, polenta and Michelin-starred restaurants."),
        ('👨‍👩‍👧', 'Famille', "Juin-août — baignade, villages accessibles en ferry et activités nautiques.", 'Family', "June–August — swimming, ferry-accessible villages and water activities."),
    ],
    'cinque-terre': [
        ('🥾', 'Sentiers côtiers', "Avril-mai ou septembre-octobre — Sentiero Azzurro et Sentiero Rosso sans la chaleur.", 'Coastal Trails', "April–May or September–October — Sentiero Azzurro and Sentiero Rosso without the heat."),
        ('🍷', 'Vin & gastronomie', "Toute l\'année — pesto genovese, focaccia, sciacchetrà et fruits de mer.", 'Wine & Food', "Year-round — pesto genovese, focaccia, sciacchetrà and seafood."),
        ('🏖️', 'Plages', "Juin-septembre — Monterosso, Corniglia et criques accessibles à pied.", 'Beaches', "June–September — Monterosso, Corniglia and walk-in coves."),
        ('📸', 'Photographie', "Avril-mai — lumière dorée, wistéria en fleurs, moins de touristes.", 'Photography', "April–May — golden light, blooming wisteria, fewer tourists."),
        ('👨‍👩‍👧', 'Famille', "Mai-juin — sentiers praticables, villages animés, mer agréable.", 'Family', "May–June — walkable trails, lively villages, pleasant sea."),
    ],
    'madrid': [
        ('🎨', 'Musées & culture', "Toute l\'année — Prado, Reina Sofía, Thyssen-Bornemisza et quartier des Letras.", 'Museums & Culture', "Year-round — Prado, Reina Sofía, Thyssen-Bornemisza and Letras district."),
        ('🍽️', 'Tapas & vie nocturne', "Toute l\'année — Mercado de San Miguel, La Latina et Malasaña.", 'Tapas & Nightlife', "Year-round — Mercado de San Miguel, La Latina and Malasaña."),
        ('⚽', 'Football', "Septembre-mai — Santiago Bernabéu et Wanda Metropolitano.", 'Football', "September–May — Santiago Bernabéu and Wanda Metropolitano."),
        ('🏖️', 'Excursion', "Mai-septembre — Tolède, Ségovie et El Escorial à moins d\'1h.", 'Day Trips', "May–September — Toledo, Segovia and El Escorial under 1h away."),
        ('👨‍👩‍👧', 'Famille', "Avril-mai ou octobre — Retiro, Casa de Campo et températures idéales.", 'Family', "April–May or October — Retiro, Casa de Campo and ideal temperatures."),
    ],
    'grenade': [
        ('🏰', 'Alhambra & Albaicín', "Mars-mai ou octobre — visite sans chaleur caniculaire, lumière parfaite.", 'Alhambra & Albaicín', "March–May or October — no scorching heat, perfect light."),
        ('🍽️', 'Tapas gratuites', "Toute l\'année — tradition unique de tapas offertes avec chaque boisson.", 'Free Tapas', "Year-round — unique tradition of free tapas with every drink."),
        ('🎸', 'Flamenco', "Toute l\'année — Sacromonte, caves flamencas et spectacles authentiques.", 'Flamenco', "Year-round — Sacromonte, flamenco caves and authentic shows."),
        ('⛷️', 'Ski Sierra Nevada', "Décembre-avril — station la plus méridionale d\'Europe, à 45 min de la ville.", 'Sierra Nevada Skiing', "December–April — Europe's southernmost ski resort, 45 min from the city."),
        ('👨‍👩‍👧', 'Famille', "Avril-mai — températures douces, Alhambra accessible, Sierra verte.", 'Family', "April–May — mild temperatures, accessible Alhambra, green Sierra."),
    ],
    'cadix': [
        ('🏖️', 'Plages', "Juin-septembre — Playa de la Victoria, Bolonia et Zahara de los Atunes.", 'Beaches', "June–September — Playa de la Victoria, Bolonia and Zahara de los Atunes."),
        ('🎭', 'Carnaval', "Février-mars — l\'un des plus grands carnavals d\'Europe.", 'Carnival', "February–March — one of the largest carnivals in Europe."),
        ('🍷', 'Sherry & gastronomie', "Toute l\'année — Jerez à 30 min, pescaíto frito et tortillitas de camarones.", 'Sherry & Food', "Year-round — Jerez 30 min away, pescaíto frito and tortillitas de camarones."),
        ('🏄', 'Surf & kitesurf', "Mars-novembre — Tarifa et El Palmar, vents constants.", 'Surf & Kitesurf', "March–November — Tarifa and El Palmar, constant winds."),
    ],
    'bilbao': [
        ('🎨', 'Guggenheim & art', "Toute l\'année — musée Guggenheim, Casco Viejo et galeries contemporaines.", 'Guggenheim & Art', "Year-round — Guggenheim Museum, Casco Viejo and contemporary galleries."),
        ('🍽️', 'Pintxos', "Toute l\'année — Plaza Nueva, rue Ledesma et étoilés Michelin.", 'Pintxos', "Year-round — Plaza Nueva, Ledesma street and Michelin stars."),
        ('🏄', 'Surf', "Avril-octobre — Mundaka, Sopelana et spots de la côte cantabrique.", 'Surfing', "April–October — Mundaka, Sopelana and Cantabrian coast spots."),
        ('🥾', 'Randonnée', "Mai-octobre — San Juan de Gaztelugatxe, Urdaibai et côte basque.", 'Hiking', "May–October — San Juan de Gaztelugatxe, Urdaibai and the Basque coast."),
    ],
    'saint-sebastien': [
        ('🍽️', 'Gastronomie', "Toute l\'année — plus de 15 étoiles Michelin, pintxos dans la Parte Vieja.", 'Gastronomy', "Year-round — over 15 Michelin stars, pintxos in the Parte Vieja."),
        ('🏖️', 'Plages', "Juin-septembre — La Concha, Ondarreta et Zurriola pour le surf.", 'Beaches', "June–September — La Concha, Ondarreta and Zurriola for surfing."),
        ('🎬', 'Festival du film', "Septembre — Festival International du Film de San Sebastián.", 'Film Festival', "September — San Sebastián International Film Festival."),
        ('🏃', 'Sport & surf', "Avril-octobre — Zurriola, sentiers du Mont Urgull et Mont Igueldo.", 'Sport & Surfing', "April–October — Zurriola, Mount Urgull and Mount Igueldo trails."),
    ],
    'formentera': [
        ('🏖️', 'Plages', "Mai-octobre — Ses Illetes, Cala Saona et eaux cristallines.", 'Beaches', "May–October — Ses Illetes, Cala Saona and crystal-clear waters."),
        ('🚲', 'Vélo', "Avril-juin ou septembre-octobre — île plate, 20 km d\'un bout à l\'autre.", 'Cycling', "April–June or September–October — flat island, 20 km end to end."),
        ('🤿', 'Snorkeling', "Mai-octobre — herbiers de posidonie, eaux transparentes.", 'Snorkelling', "May–October — posidonia meadows, transparent waters."),
        ('🧘', 'Détente', "Mai-juin ou septembre — ambiance zen, couchers de soleil sur Es Vedrà.", 'Relaxation', "May–June or September — zen atmosphere, sunsets over Es Vedrà."),
    ],
    'costa-brava': [
        ('🏖️', 'Criques & plages', "Juin-septembre — Tossa de Mar, Calella de Palafrugell et Begur.", 'Coves & Beaches', "June–September — Tossa de Mar, Calella de Palafrugell and Begur."),
        ('🎨', 'Dalí & culture', "Toute l\'année — Musée Dalí à Figueres, Cadaqués et Portlligat.", 'Dalí & Culture', "Year-round — Dalí Museum in Figueres, Cadaqués and Portlligat."),
        ('🥾', 'Camí de Ronda', "Avril-juin ou septembre-octobre — sentier côtier historique sans la chaleur.", 'Camí de Ronda', "April–June or September–October — historic coastal path without the heat."),
        ('🍷', 'Gastronomie', "Toute l\'année — cuisine catalane, El Celler de Can Roca à Gérone.", 'Gastronomy', "Year-round — Catalan cuisine, El Celler de Can Roca in Girona."),
    ],
    'cordoue': [
        ('🕌', 'Mosquée-Cathédrale', "Mars-mai ou octobre — visite sans caniculaire, lumière matinale idéale.", 'Mosque-Cathedral', "March–May or October — no heatwave, ideal morning light."),
        ('🌺', 'Patios & jardins', "Mai — Festival des Patios, classé UNESCO.", 'Patios & Gardens', "May — Patio Festival, UNESCO-listed."),
        ('🍽️', 'Gastronomie', "Toute l\'année — salmorejo, flamenquín et vins de Montilla-Moriles.", 'Gastronomy', "Year-round — salmorejo, flamenquín and Montilla-Moriles wines."),
        ('🎸', 'Flamenco', "Toute l\'année — tablaos et peñas flamencas authentiques.", 'Flamenco', "Year-round — tablaos and authentic flamenco peñas."),
    ],
    'la-palma': [
        ('🥾', 'Randonnée volcanique', "Mars-novembre — Caldera de Taburiente et Ruta de los Volcanes.", 'Volcanic Hiking', "March–November — Caldera de Taburiente and Ruta de los Volcanes."),
        ('🔭', 'Astronomie', "Toute l\'année — Observatorio del Roque de los Muchachos, ciel parmi les plus purs.", 'Astronomy', "Year-round — Roque de los Muchachos Observatory, among the purest skies."),
        ('🏖️', 'Plages de lave', "Mai-octobre — plages noires volcaniques, piscines naturelles.", 'Lava Beaches', "May–October — volcanic black beaches and natural pools."),
        ('🌿', 'Nature & forêts', "Toute l\'année — laurissilva, dragonniers et biodiversité unique.", 'Nature & Forests', "Year-round — laurisilva, dragon trees and unique biodiversity."),
    ],
    'la-gomera': [
        ('🥾', 'Randonnée Garajonay', "Toute l\'année — forêt de lauriers UNESCO, sentiers brumeux.", 'Garajonay Hiking', "Year-round — UNESCO laurel forest, misty trails."),
        ('🌿', 'Nature', "Mars-mai — floraison, températures parfaites pour la marche.", 'Nature', "March–May — flowering season, perfect walking temperatures."),
        ('🏖️', 'Plages', "Mai-octobre — Valle Gran Rey, plages noires et piscines naturelles.", 'Beaches', "May–October — Valle Gran Rey, black beaches and natural pools."),
        ('🎶', 'Silbo gomero', "Toute l\'année — langage sifflé unique au monde, classé UNESCO.", 'Silbo Gomero', "Year-round — unique whistled language, UNESCO-listed."),
    ],
    'el-hierro': [
        ('🤿', 'Plongée', "Avril-novembre — eaux volcaniques claires, Mar de las Calmas.", 'Diving', "April–November — clear volcanic waters, Mar de las Calmas."),
        ('🥾', 'Randonnée', "Toute l\'année — sentiers côtiers, forêts de genévriers et volcans.", 'Hiking', "Year-round — coastal trails, juniper forests and volcanoes."),
        ('🌿', 'Écotourisme', "Toute l\'année — première île 100% renouvelable, réserve de biosphère UNESCO.", 'Ecotourism', "Year-round — first 100% renewable island, UNESCO biosphere reserve."),
    ],
    'copenhague': [
        ('🎨', 'Design & musées', "Toute l\'année — Louisiana, Design Museum et architecture contemporaine.", 'Design & Museums', "Year-round — Louisiana, Design Museum and contemporary architecture."),
        ('🚲', 'Vélo & quartiers', "Mai-septembre — Nyhavn, Christiania, Nørrebro à vélo.", 'Cycling & Districts', "May–September — Nyhavn, Christiania, Nørrebro by bike."),
        ('🍽️', 'Nouvelle cuisine nordique', "Toute l\'année — Noma, Geranium et street food au Torvehallerne.", 'New Nordic Cuisine', "Year-round — Noma, Geranium and street food at Torvehallerne."),
        ('🎅', 'Noël & hygge', "Décembre — Tivoli illuminé, marchés de Noël et vin chaud.", 'Christmas & Hygge', "December — Tivoli lights, Christmas markets and mulled wine."),
        ('👨‍👩‍👧', 'Famille', "Juin-août — Tivoli, plages d\'Amager et journées longues.", 'Family', "June–August — Tivoli, Amager beaches and long days."),
    ],
    'budapest': [
        ('♨️', 'Bains thermaux', "Toute l\'année — Széchenyi, Gellért et Rudas. Hiver : bains fumants en extérieur.", 'Thermal Baths', "Year-round — Széchenyi, Gellért and Rudas. Winter: steaming outdoor baths."),
        ('🍷', 'Ruinbars & vie nocturne', "Toute l\'année — Szimpla Kert et quartier juif.", 'Ruin Bars & Nightlife', "Year-round — Szimpla Kert and the Jewish quarter."),
        ('🏛️', 'Patrimoine', "Mars-mai ou septembre-octobre — Parlement, Château de Buda, Bastion des Pêcheurs.", 'Heritage', "March–May or September–October — Parliament, Buda Castle, Fisherman\'s Bastion."),
        ('🍽️', 'Gastronomie', "Toute l\'année — goulash, lángos, Grand Marché et restaurants contemporains.", 'Gastronomy', "Year-round — goulash, lángos, Great Market Hall and contemporary restaurants."),
        ('👨‍👩‍👧', 'Famille', "Mai-septembre — croisière sur le Danube, île Marguerite et bains.", 'Family', "May–September — Danube cruise, Margaret Island and baths."),
    ],
    'dublin': [
        ('🍺', 'Pubs & musique', "Toute l\'année — Temple Bar, musique live et Guinness Storehouse.", 'Pubs & Music', "Year-round — Temple Bar, live music and Guinness Storehouse."),
        ('📚', 'Littérature', "Toute l\'année — Trinity College, Book of Kells et Joyce.", 'Literature', "Year-round — Trinity College, Book of Kells and Joyce."),
        ('🥾', 'Excursions nature', "Mai-septembre — falaises de Howth, Wicklow Mountains et Giant\'s Causeway.", 'Nature Excursions', "May–September — Howth cliffs, Wicklow Mountains and Giant\'s Causeway."),
        ('🎭', 'Festivals', "Juin — Bloomsday. Mars — St Patrick\'s Day.", 'Festivals', "June — Bloomsday. March — St Patrick\'s Day."),
        ('👨‍👩‍👧', 'Famille', "Juin-août — Phoenix Park, zoo et côte de Dún Laoghaire.", 'Family', "June–August — Phoenix Park, zoo and Dún Laoghaire coast."),
    ],
    'cracovie': [
        ('🏛️', 'Vieille ville & Wawel', "Avril-mai ou septembre-octobre — château, Rynek Główny et Kazimierz.", 'Old Town & Wawel', "April–May or September–October — castle, Rynek Główny and Kazimierz."),
        ('⛏️', 'Mine de sel de Wieliczka', "Toute l\'année — 300m sous terre, chapelles sculptées dans le sel.", 'Wieliczka Salt Mine', "Year-round — 300m underground, chapels carved from salt."),
        ('🍽️', 'Gastronomie', "Toute l\'année — pierogi, żurek, vodka et restaurants de Kazimierz.", 'Gastronomy', "Year-round — pierogi, żurek, vodka and Kazimierz restaurants."),
        ('🏔️', 'Excursion Tatras', "Juin-septembre — monts Tatra à 2h, randonnée alpine.", 'Tatra Day Trip', "June–September — Tatra Mountains 2h away, alpine hiking."),
    ],
    'zakynthos': [
        ('🏖️', 'Navagio Beach', "Juin-septembre — accès en bateau uniquement, eau turquoise spectaculaire.", 'Navagio Beach', "June–September — boat access only, spectacular turquoise water."),
        ('🐢', 'Tortues caretta', "Juin-août — observation à Laganas Bay (zone protégée).", 'Caretta Turtles', "June–August — spotting at Laganas Bay (protected zone)."),
        ('🤿', 'Plongée & snorkeling', "Mai-octobre — grottes bleues, épaves et eaux cristallines.", 'Diving & Snorkelling', "May–October — blue caves, wrecks and crystal-clear waters."),
        ('🚤', 'Tour de l\'île en bateau', "Mai-septembre — criques accessibles uniquement par la mer.", 'Island Boat Tour', "May–September — coves accessible only by sea."),
    ],
    'hvar': [
        ('🏖️', 'Plages & criques', "Juin-septembre — îles Pakleni, plages cachées et eaux adriatiques.", 'Beaches & Coves', "June–September — Pakleni Islands, hidden beaches and Adriatic waters."),
        ('🍷', 'Vin & gastronomie', "Toute l\'année — vignobles de Plavac Mali, huile d\'olive et lavande.", 'Wine & Food', "Year-round — Plavac Mali vineyards, olive oil and lavender."),
        ('🎉', 'Vie nocturne', "Juillet-août — Hula Hula, Carpe Diem et bars sur le port.", 'Nightlife', "July–August — Hula Hula, Carpe Diem and harbour bars."),
        ('🚲', 'Vélo & randonnée', "Avril-juin ou septembre-octobre — sentiers de lavande, villages de l\'intérieur.", 'Cycling & Hiking', "April–June or September–October — lavender trails, inland villages."),
    ],
    'plitvice': [
        ('🥾', 'Randonnée & lacs', "Avril-mai ou septembre-octobre — cascades au débit maximal, couleurs automnales.", 'Hiking & Lakes', "April–May or September–October — waterfalls at peak flow, autumn colours."),
        ('📸', 'Photographie', "Avril-mai — reflets turquoise, verdure luxuriante, lumière matinale.", 'Photography', "April–May — turquoise reflections, lush greenery, morning light."),
        ('🦌', 'Faune', "Mai-octobre — cerfs, ours (rares), oiseaux et papillons.", 'Wildlife', "May–October — deer, bears (rare), birds and butterflies."),
    ],
    'zadar': [
        ('🌅', 'Coucher de soleil & orgue marin', "Toute l\'année — Hitchcock disait le plus beau coucher de soleil au monde.", 'Sunset & Sea Organ', "Year-round — Hitchcock called it the world\'s most beautiful sunset."),
        ('🏖️', 'Plages & îles', "Juin-septembre — Sakarun sur Dugi Otok, Kornati en excursion.", 'Beaches & Islands', "June–September — Sakarun on Dugi Otok, Kornati day trips."),
        ('🏛️', 'Patrimoine romain', "Toute l\'année — Forum romain, église Saint-Donat et remparts.", 'Roman Heritage', "Year-round — Roman Forum, St Donatus Church and ramparts."),
        ('🍽️', 'Gastronomie dalmate', "Toute l\'année — fruits de mer frais, maraschino et huile d\'olive.", 'Dalmatian Food', "Year-round — fresh seafood, maraschino and olive oil."),
    ],
    'zagreb': [
        ('🎨', 'Musées & culture', "Toute l\'année — Musée des Relations Brisées, Naïve Art et Mestrovic.", 'Museums & Culture', "Year-round — Museum of Broken Relationships, Naïve Art and Mestrovic."),
        ('🍽️', 'Gastronomie', "Toute l\'année — štrukli, marché de Dolac et restaurants contemporains.", 'Gastronomy', "Year-round — štrukli, Dolac market and contemporary restaurants."),
        ('🎅', 'Marché de Noël', "Décembre — élu meilleur marché de Noël d\'Europe plusieurs années de suite.", 'Christmas Market', "December — voted Europe\'s best Christmas market multiple years running."),
        ('🏔️', 'Excursion Plitvice', "Avril-octobre — lacs de Plitvice à 2h en voiture.", 'Plitvice Day Trip', "April–October — Plitvice Lakes 2h by car."),
    ],
    'kotor': [
        ('🏰', 'Vieille ville & remparts', "Avril-juin ou septembre-octobre — fortifications vénitiennes, 1350 marches.", 'Old Town & Ramparts', "April–June or September–October — Venetian fortifications, 1,350 steps."),
        ('🚤', 'Croisière en baie', "Mai-septembre — bouches de Kotor, Perast et Notre-Dame du Récif.", 'Bay Cruise', "May–September — Bay of Kotor, Perast and Our Lady of the Rocks."),
        ('🏖️', 'Plages', "Juin-septembre — Budva et ses plages à 20 min.", 'Beaches', "June–September — Budva and its beaches 20 min away."),
        ('🥾', 'Randonnée', "Avril-octobre — Lovćen, sentier des remparts et mont Orjen.", 'Hiking', "April–October — Lovćen, rampart trail and Mount Orjen."),
    ],
    'montenegro': [
        ('🏰', 'Kotor & patrimoine', "Avril-juin ou septembre — remparts, baie et villages perchés.", 'Kotor & Heritage', "April–June or September — ramparts, bay and hilltop villages."),
        ('🏖️', 'Plages adriatiques', "Juin-septembre — Budva, Sveti Stefan et Ulcinj.", 'Adriatic Beaches', "June–September — Budva, Sveti Stefan and Ulcinj."),
        ('🏔️', 'Montagne & Durmitor', "Juin-septembre — canyon de la Tara, randonnée et rafting.", 'Mountains & Durmitor', "June–September — Tara canyon, hiking and rafting."),
        ('🍽️', 'Gastronomie', "Toute l\'année — njeguški steak, poisson grillé et vin Vranac.", 'Gastronomy', "Year-round — njeguški steak, grilled fish and Vranac wine."),
    ],
    'albanie': [
        ('🏖️', 'Riviera albanaise', "Juin-septembre — Ksamil, Dhermi et Himara, eaux turquoise.", 'Albanian Riviera', "June–September — Ksamil, Dhermi and Himara, turquoise waters."),
        ('🏛️', 'Patrimoine UNESCO', "Avril-mai ou octobre — Berat, Gjirokastra et Butrint.", 'UNESCO Heritage', "April–May or October — Berat, Gjirokastra and Butrint."),
        ('🥾', 'Randonnée', "Mai-octobre — Alpes albanaises, Valbona et Theth.", 'Hiking', "May–October — Albanian Alps, Valbona and Theth."),
        ('🍽️', 'Gastronomie', "Toute l\'année — byrek, tavë kosi et cuisine ottomane-méditerranéenne.", 'Gastronomy', "Year-round — byrek, tavë kosi and Ottoman-Mediterranean cuisine."),
    ],
    'sofia': [
        ('🏛️', 'Patrimoine & cathédrale', "Toute l\'année — Alexandre Nevski, Boyana UNESCO et thermes romains.", 'Heritage & Cathedral', "Year-round — Alexander Nevsky, UNESCO Boyana and Roman baths."),
        ('⛷️', 'Ski', "Décembre-mars — Borovets et Bansko à 1-2h.", 'Skiing', "December–March — Borovets and Bansko 1–2h away."),
        ('🥾', 'Randonnée Vitosha', "Mai-octobre — montagne Vitosha accessible en métro depuis le centre.", 'Vitosha Hiking', "May–October — Vitosha Mountain accessible by metro from the centre."),
        ('🍽️', 'Gastronomie', "Toute l\'année — shopska, kavarma et vins bulgares.", 'Gastronomy', "Year-round — shopska, kavarma and Bulgarian wines."),
    ],
    'bucarest': [
        ('🏛️', 'Patrimoine', "Toute l\'année — Palais du Parlement, Athénée roumain et vieille ville.", 'Heritage', "Year-round — Palace of Parliament, Romanian Athenaeum and old town."),
        ('🎉', 'Vie nocturne', "Toute l\'année — clubs, bars et terrasses du vieux centre.", 'Nightlife', "Year-round — clubs, bars and terraces of the old centre."),
        ('🍽️', 'Gastronomie', "Toute l\'année — ciorba, mici et vins de Dealu Mare.", 'Gastronomy', "Year-round — ciorba, mici and Dealu Mare wines."),
        ('🏔️', 'Excursion Transylvanie', "Mai-octobre — Brașov, château de Bran et Sinaia à 2h.", 'Transylvania Day Trip', "May–October — Brașov, Bran Castle and Sinaia 2h away."),
    ],
    'transylvanie': [
        ('🏰', 'Châteaux', "Toute l\'année — Bran (Dracula), Peleș et Corvin.", 'Castles', "Year-round — Bran (Dracula), Peleș and Corvin."),
        ('🥾', 'Randonnée Carpates', "Juin-septembre — Piatra Craiului, Făgăraș et gorges de Bicaz.", 'Carpathian Hiking', "June–September — Piatra Craiului, Făgăraș and Bicaz Gorge."),
        ('🏘️', 'Villages saxons', "Mai-octobre — Viscri, Biertan et églises fortifiées UNESCO.", 'Saxon Villages', "May–October — Viscri, Biertan and UNESCO fortified churches."),
        ('🐻', 'Faune', "Mai-septembre — observation des ours, cerfs et lynx.", 'Wildlife', "May–September — bear, deer and lynx watching."),
    ],
    'bratislava': [
        ('🏰', 'Château & vieille ville', "Avril-octobre — château, cathédrale Saint-Martin et ruelles baroques.", 'Castle & Old Town', "April–October — castle, St Martin\'s Cathedral and baroque lanes."),
        ('🍷', 'Vin', "Septembre-octobre — Petit Carpates, vendanges et route des vins.", 'Wine', "September–October — Little Carpathians, harvest and wine route."),
        ('🚤', 'Excursion Danube', "Mai-septembre — bateau vers Vienne ou Budapest.", 'Danube Excursion', "May–September — boat to Vienna or Budapest."),
    ],
    'helsinki': [
        ('♨️', 'Saunas', "Toute l\'année — Löyly, Allas Sea Pool et saunas publics traditionnels.", 'Saunas', "Year-round — Löyly, Allas Sea Pool and traditional public saunas."),
        ('🎨', 'Design & architecture', "Toute l\'année — Design District, Oodi Library et Suomenlinna.", 'Design & Architecture', "Year-round — Design District, Oodi Library and Suomenlinna."),
        ('🏝️', 'Archipel', "Juin-août — îles accessibles en ferry, baignade et kayak.", 'Archipelago', "June–August — islands by ferry, swimming and kayaking."),
        ('🎅', 'Noël & neige', "Décembre — marchés, cathédrale blanche illuminée et excursion Laponie.", 'Christmas & Snow', "December — markets, illuminated white cathedral and Lapland excursion."),
    ],
    'tallinn': [
        ('🏰', 'Vieille ville médiévale', "Mai-septembre — remparts, Toompea et passages secrets.", 'Medieval Old Town', "May–September — ramparts, Toompea and hidden passages."),
        ('💻', 'Tech & innovation', "Toute l\'année — Telliskivi, startups et e-résidence.", 'Tech & Innovation', "Year-round — Telliskivi, startups and e-residency."),
        ('🎅', 'Marché de Noël', "Décembre — Raekoja plats, vin chaud et ambiance médiévale.", 'Christmas Market', "December — Raekoja plats, mulled wine and medieval atmosphere."),
        ('🍽️', 'Gastronomie nordique', "Toute l\'année — cuisine estonienne renouvelée, Rataskaevu et Teliskivi.", 'Nordic Food', "Year-round — renewed Estonian cuisine, Rataskaevu and Telliskivi."),
    ],
    'riga': [
        ('🏛️', 'Art nouveau', "Toute l\'année — rue Alberta, plus de 800 bâtiments Art nouveau.", 'Art Nouveau', "Year-round — Alberta Street, over 800 Art Nouveau buildings."),
        ('🏘️', 'Vieille ville', "Mai-septembre — cathédrale, Maison des Têtes Noires et marché central.", 'Old Town', "May–September — cathedral, House of the Blackheads and Central Market."),
        ('🎅', 'Noël', "Décembre — premier sapin de Noël d\'Europe (1510), marchés traditionnels.", 'Christmas', "December — Europe\'s first Christmas tree (1510), traditional markets."),
        ('🍽️', 'Gastronomie', "Toute l\'année — baume noir de Riga, cuisine balte et marché Centraltirgus.", 'Gastronomy', "Year-round — Riga Black Balsam, Baltic cuisine and Centraltirgus market."),
    ],
    'vilnius': [
        ('🏛️', 'Vieille ville baroque', "Mai-septembre — plus grande vieille ville baroque d\'Europe de l\'Est.", 'Baroque Old Town', "May–September — Eastern Europe\'s largest baroque old town."),
        ('🎨', 'Užupis & street art', "Toute l\'année — république autoproclamée, galeries et art de rue.", 'Užupis & Street Art', "Year-round — self-proclaimed republic, galleries and street art."),
        ('🍽️', 'Gastronomie', "Toute l\'année — cepelinai, šaltibarščiai et restaurants créatifs.", 'Gastronomy', "Year-round — cepelinai, šaltibarščiai and creative restaurants."),
        ('🌳', 'Parcs & nature', "Mai-septembre — parc de Vingis, colline de Gediminas et Trakai à 30 min.", 'Parks & Nature', "May–September — Vingis Park, Gediminas Hill and Trakai 30 min away."),
    ],
    'stockholm': [
        ('🏝️', 'Archipel', "Juin-août — 30 000 îles, ferries et baignade dans les rochers.", 'Archipelago', "June–August — 30,000 islands, ferries and rock swimming."),
        ('🎨', 'Musées', "Toute l\'année — Vasa, ABBA Museum, Fotografiska et Moderna Museet.", 'Museums', "Year-round — Vasa, ABBA Museum, Fotografiska and Moderna Museet."),
        ('🍽️', 'Gastronomie nordique', "Toute l\'année — fika, smörgåsbord et restaurants étoilés.", 'Nordic Food', "Year-round — fika, smörgåsbord and Michelin-starred restaurants."),
        ('❄️', 'Noël & hiver', "Décembre — Gamla Stan illuminée, marchés et glögg.", 'Christmas & Winter', "December — illuminated Gamla Stan, markets and glögg."),
    ],
    'oslo': [
        ('🎨', 'Musées', "Toute l\'année — Munch, Vigeland, Musée national rénové.", 'Museums', "Year-round — Munch, Vigeland, renovated National Museum."),
        ('🚤', 'Fjord d\'Oslo', "Mai-septembre — îles, baignade et kayak dans le fjord.", 'Oslo Fjord', "May–September — islands, swimming and kayaking in the fjord."),
        ('🏗️', 'Architecture', "Toute l\'année — Opéra flottant, Barcode et Aker Brygge.", 'Architecture', "Year-round — floating Opera House, Barcode and Aker Brygge."),
        ('⛷️', 'Ski', "Décembre-mars — Nordmarka et Holmenkollen à 20 min du centre.", 'Skiing', "December–March — Nordmarka and Holmenkollen 20 min from the centre."),
    ],
    'bergen': [
        ('🏘️', 'Bryggen & patrimoine', "Mai-septembre — quais hanséatiques UNESCO, funiculaire Fløibanen.", 'Bryggen & Heritage', "May–September — UNESCO Hanseatic wharf, Fløibanen funicular."),
        ('🚢', 'Fjords', "Mai-août — Sognefjord et Hardangerfjord en excursion à la journée.", 'Fjords', "May–August — Sognefjord and Hardangerfjord day trips."),
        ('🍽️', 'Poisson & marché', "Toute l\'année — Fisketorget, saumon et fruits de mer frais.", 'Fish & Market', "Year-round — Fisketorget, salmon and fresh seafood."),
        ('🥾', 'Randonnée', "Mai-septembre — Trolltunga, Preikestolen et sentiers côtiers.", 'Hiking', "May–September — Trolltunga, Preikestolen and coastal trails."),
    ],
    'lofoten': [
        ('📸', 'Photographie', "Février-mars (aurores) ou juin-juillet (soleil de minuit) — paysages iconiques.", 'Photography', "February–March (auroras) or June–July (midnight sun) — iconic landscapes."),
        ('🐟', 'Pêche & gastronomie', "Février-avril — morue séchée (stockfish), cabanes de pêcheurs rouges.", 'Fishing & Food', "February–April — dried cod (stockfish), red fishing cabins."),
        ('🥾', 'Randonnée', "Juin-septembre — Reinebringen, Ryten et plages arctiques de sable blanc.", 'Hiking', "June–September — Reinebringen, Ryten and white-sand Arctic beaches."),
        ('🏄', 'Surf arctique', "Septembre-mars — vagues et aurores boréales, combinaison nécessaire.", 'Arctic Surfing', "September–March — waves and northern lights, wetsuit required."),
    ],
    'tromso': [
        ('🌌', 'Aurores boréales', "Septembre-mars — l\'un des meilleurs spots au monde.", 'Northern Lights', "September–March — one of the best spots in the world."),
        ('☀️', 'Soleil de minuit', "Mai-juillet — lumière 24h, randonnée et kayak nocturne.", 'Midnight Sun', "May–July — 24h light, hiking and night kayaking."),
        ('🐋', 'Observation des baleines', "Novembre-janvier — orques et baleines à bosse dans les fjords.", 'Whale Watching', "November–January — orcas and humpback whales in the fjords."),
        ('🛷', 'Chiens de traîneaux', "Décembre-mars — excursions en traîneau et rennes samis.", 'Dog Sledding', "December–March — sled excursions and Sami reindeer."),
    ],
    'laponie': [
        ('🌌', 'Aurores boréales', "Septembre-mars — probabilité maximale en décembre-février.", 'Northern Lights', "September–March — peak probability December–February."),
        ('🎅', 'Village du Père Noël', "Décembre-janvier — Rovaniemi, rencontre avec le Père Noël.", 'Santa Claus Village', "December–January — Rovaniemi, meet Santa Claus."),
        ('🛷', 'Motoneige & traîneaux', "Décembre-mars — excursions en forêt, rennes et huskies.", 'Snowmobile & Sledding', "December–March — forest excursions, reindeer and huskies."),
        ('☀️', 'Été arctique', "Juin-août — soleil de minuit, randonnée et pêche.", 'Arctic Summer', "June–August — midnight sun, hiking and fishing."),
    ],
    'bruxelles': [
        ('🍫', 'Chocolat & gaufres', "Toute l\'année — Pierre Marcolini, Wittamer et gaufres de Liège.", 'Chocolate & Waffles', "Year-round — Pierre Marcolini, Wittamer and Liège waffles."),
        ('🎨', 'BD & Art nouveau', "Toute l\'année — Musée de la BD, parcours Art nouveau de Horta.", 'Comics & Art Nouveau', "Year-round — Comic Strip Museum, Horta Art Nouveau trail."),
        ('🍺', 'Bière', "Toute l\'année — Delirium Café, Cantillon et centaines de bières belges.", 'Beer', "Year-round — Delirium Café, Cantillon and hundreds of Belgian beers."),
        ('🏛️', 'Grand-Place', "Toute l\'année — plus belle place d\'Europe, tapis de fleurs (août).", 'Grand-Place', "Year-round — Europe\'s most beautiful square, flower carpet (August)."),
    ],
    'bruges': [
        ('🏰', 'Vieille ville', "Avril-septembre — canaux, beffroi et place du Markt.", 'Old Town', "April–September — canals, belfry and Markt square."),
        ('🍫', 'Chocolat', "Toute l\'année — Dumon, The Chocolate Line et ateliers.", 'Chocolate', "Year-round — Dumon, The Chocolate Line and workshops."),
        ('🍺', 'Bière', "Toute l\'année — brasserie De Halve Maan et bières trappistes.", 'Beer', "Year-round — De Halve Maan brewery and Trappist beers."),
        ('🎅', 'Noël', "Décembre — marché de Noël sur la place du Markt et patinoire.", 'Christmas', "December — Christmas market on Markt square and ice rink."),
    ],
    'gdansk': [
        ('🏘️', 'Vieille ville hanséatique', "Mai-septembre — Long Market, grue médiévale et ambre.", 'Hanseatic Old Town', "May–September — Long Market, medieval crane and amber."),
        ('🏖️', 'Plages baltiques', "Juin-août — Sopot, Gdynia et longues plages de sable.", 'Baltic Beaches', "June–August — Sopot, Gdynia and long sandy beaches."),
        ('🍽️', 'Gastronomie', "Toute l\'année — pierogi, bière locale et restaurants du port.", 'Gastronomy', "Year-round — pierogi, local beer and harbour restaurants."),
        ('📚', 'Histoire', "Toute l\'année — Musée de la Seconde Guerre mondiale et chantiers navals Solidarność.", 'History', "Year-round — World War II Museum and Solidarność shipyards."),
    ],
    'varsovie': [
        ('🏛️', 'Vieille ville UNESCO', "Mai-septembre — place du Marché reconstruite, château royal.", 'UNESCO Old Town', "May–September — rebuilt Market Square, Royal Castle."),
        ('📚', 'Histoire', "Toute l\'année — Musée de l\'Insurrection, POLIN et mémorial du Ghetto.", 'History', "Year-round — Uprising Museum, POLIN and Ghetto Memorial."),
        ('🎉', 'Vie nocturne', "Toute l\'année — quartier de Praga, clubs et bars sur les toits.", 'Nightlife', "Year-round — Praga district, clubs and rooftop bars."),
        ('🍽️', 'Gastronomie', "Toute l\'année — pierogi, żurek et nouvelle cuisine polonaise.", 'Gastronomy', "Year-round — pierogi, żurek and new Polish cuisine."),
    ],
    'geneve': [
        ('⛵', 'Lac Léman', "Mai-septembre — croisières, baignade et Jet d\'Eau.", 'Lake Geneva', "May–September — cruises, swimming and Jet d\'Eau."),
        ('🏔️', 'Mont-Blanc & Alpes', "Toute l\'année — Chamonix à 1h, ski en hiver, randonnée en été.", 'Mont Blanc & Alps', "Year-round — Chamonix 1h away, winter skiing, summer hiking."),
        ('🕐', 'Horlogerie & luxe', "Toute l\'année — Patek Philippe, quartier des banques et chocolat suisse.", 'Watchmaking & Luxury', "Year-round — Patek Philippe, banking district and Swiss chocolate."),
        ('🍽️', 'Gastronomie', "Toute l\'année — fondue, raclette et restaurants gastronomiques.", 'Gastronomy', "Year-round — fondue, raclette and fine dining."),
    ],
    'zurich': [
        ('🏔️', 'Excursions alpines', "Mai-octobre — Jungfraujoch, Lucerne et Titlis à 1-2h.", 'Alpine Excursions', "May–October — Jungfraujoch, Lucerne and Titlis 1–2h away."),
        ('🎨', 'Musées', "Toute l\'année — Kunsthaus, Museum für Gestaltung et FIFA Museum.", 'Museums', "Year-round — Kunsthaus, Museum für Gestaltung and FIFA Museum."),
        ('🍫', 'Chocolat & gastronomie', "Toute l\'année — Lindt Home, fondue et restaurants étoilés.", 'Chocolate & Food', "Year-round — Lindt Home, fondue and Michelin-starred restaurants."),
        ('🏊', 'Lac de Zurich', "Juin-août — baignade, Badis (bains publics) et croisières.", 'Lake Zurich', "June–August — swimming, Badis (public baths) and cruises."),
    ],
    'munich': [
        ('🍺', 'Bière & Oktoberfest', "Septembre-octobre — Oktoberfest. Toute l\'année — Hofbräuhaus et biergartens.", 'Beer & Oktoberfest', "September–October — Oktoberfest. Year-round — Hofbräuhaus and beer gardens."),
        ('🏰', 'Châteaux de Bavière', "Mai-septembre — Neuschwanstein, Linderhof et Herrenchiemsee.", 'Bavarian Castles', "May–September — Neuschwanstein, Linderhof and Herrenchiemsee."),
        ('🎨', 'Musées', "Toute l\'année — Alte Pinakothek, Deutsches Museum et BMW Welt.", 'Museums', "Year-round — Alte Pinakothek, Deutsches Museum and BMW Welt."),
        ('⛷️', 'Ski alpin', "Décembre-mars — Garmisch-Partenkirchen et stations autrichiennes à 1h.", 'Alpine Skiing', "December–March — Garmisch-Partenkirchen and Austrian resorts 1h away."),
    ],
    'hambourg': [
        ('🚢', 'Port & Speicherstadt', "Toute l\'année — entrepôts UNESCO, Miniatur Wunderland et Hafencity.", 'Port & Speicherstadt', "Year-round — UNESCO warehouses, Miniatur Wunderland and Hafencity."),
        ('🎵', 'Elbphilharmonie & musique', "Toute l\'année — concerts, Reeperbahn et scène musicale.", 'Elbphilharmonie & Music', "Year-round — concerts, Reeperbahn and music scene."),
        ('🍽️', 'Gastronomie', "Toute l\'année — Fischbrötchen, marché aux poissons du dimanche.", 'Gastronomy', "Year-round — Fischbrötchen, Sunday fish market."),
        ('🏖️', 'Plages de l\'Elbe', "Juin-août — Strandperle, baignade et ambiance estivale.", 'Elbe Beaches', "June–August — Strandperle, swimming and summer atmosphere."),
    ],
    'francfort': [
        ('🏙️', 'Skyline & architecture', "Toute l\'année — Römerberg, Main Tower et quartier financier.", 'Skyline & Architecture', "Year-round — Römerberg, Main Tower and financial district."),
        ('🍎', 'Cidre & Sachsenhausen', "Toute l\'année — Apfelwein, Ebbelwoi et quartier traditionnel.", 'Cider & Sachsenhausen', "Year-round — Apfelwein, Ebbelwoi and traditional quarter."),
        ('🎨', 'Museumsufer', "Toute l\'année — 12 musées le long du Main.", 'Museumsufer', "Year-round — 12 museums along the Main river."),
        ('🏔️', 'Excursions', "Mai-octobre — Heidelberg, vallée du Rhin et route des vins.", 'Day Trips', "May–October — Heidelberg, Rhine Valley and wine route."),
    ],
    'ljubljana': [
        ('🏰', 'Château & vieille ville', "Avril-septembre — funiculaire, Triple Pont et berges aménagées.", 'Castle & Old Town', "April–September — funicular, Triple Bridge and landscaped banks."),
        ('🌿', 'Ville verte', "Mai-septembre — parc Tivoli, kayak sur la Ljubljanica.", 'Green City', "May–September — Tivoli Park, kayaking on the Ljubljanica."),
        ('🍽️', 'Gastronomie', "Toute l\'année — Open Kitchen (vendredi), cuisine slovène contemporaine.", 'Gastronomy', "Year-round — Open Kitchen (Fridays), contemporary Slovenian cuisine."),
        ('🏔️', 'Excursion Bled', "Mai-septembre — lac de Bled à 45 min en bus.", 'Bled Day Trip', "May–September — Lake Bled 45 min by bus."),
    ],
    'wild-atlantic-way': [
        ('🥾', 'Randonnée côtière', "Mai-septembre — falaises de Moher, Skellig Michael et Loop Head.", 'Coastal Hiking', "May–September — Cliffs of Moher, Skellig Michael and Loop Head."),
        ('🍺', 'Pubs & musique', "Toute l\'année — pubs traditionnels, sessions de musique live.", 'Pubs & Music', "Year-round — traditional pubs, live music sessions."),
        ('🏄', 'Surf', "Toute l\'année — Lahinch, Bundoran et Mullaghmore.", 'Surfing', "Year-round — Lahinch, Bundoran and Mullaghmore."),
        ('📸', 'Paysages', "Mai-juin — lumière longue, collines verdoyantes et côtes dramatiques.", 'Landscapes', "May–June — long light, green hills and dramatic coastline."),
    ],

    # === FRANCE ===
    'biarritz': [
        ('🏄', 'Surf', "Avril-octobre — Côte des Basques, Grande Plage et spots de la côte.", 'Surfing', "April–October — Côte des Basques, Grande Plage and coastal spots."),
        ('🍽️', 'Gastronomie basque', "Toute l\'année — piment d\'Espelette, axoa, gâteau basque et pintxos.", 'Basque Food', "Year-round — Espelette pepper, axoa, Basque cake and pintxos."),
        ('🏖️', 'Plages', "Juin-septembre — Grande Plage, Miramar et plages de la corniche.", 'Beaches', "June–September — Grande Plage, Miramar and corniche beaches."),
        ('♨️', 'Thalassothérapie', "Toute l\'année — cures marines, spa et bien-être face à l\'océan.", 'Thalassotherapy', "Year-round — marine treatments, spa and ocean-facing wellness."),
    ],
    'chamonix': [
        ('⛷️', 'Ski & alpinisme', "Décembre-avril — Grands Montets, Vallée Blanche et Mont-Blanc.", 'Skiing & Mountaineering', "December–April — Grands Montets, Vallée Blanche and Mont Blanc."),
        ('🥾', 'Randonnée & TMB', "Juin-septembre — Tour du Mont-Blanc, Lac Blanc et Mer de Glace.", 'Hiking & TMB', "June–September — Tour du Mont-Blanc, Lac Blanc and Mer de Glace."),
        ('🚡', 'Aiguille du Midi', "Mai-octobre — panorama 360° sur les Alpes, passerelle dans le vide.", 'Aiguille du Midi', "May–October — 360° Alpine panorama, Step into the Void."),
        ('👨‍👩‍👧', 'Famille', "Juillet-août — randonnées accessibles, luge d\'été et parc de Merlet.", 'Family', "July–August — accessible hikes, summer luge and Merlet park."),
    ],
    'dordogne': [
        ('🎨', 'Grottes & préhistoire', "Toute l\'année — Lascaux IV, Font-de-Gaume et Les Eyzies.", 'Caves & Prehistory', "Year-round — Lascaux IV, Font-de-Gaume and Les Eyzies."),
        ('🏰', 'Châteaux', "Avril-octobre — Beynac, Castelnaud, Les Milandes et Hautefort.", 'Castles', "April–October — Beynac, Castelnaud, Les Milandes and Hautefort."),
        ('🍽️', 'Gastronomie', "Toute l\'année — foie gras, truffe, noix et vin de Bergerac.", 'Gastronomy', "Year-round — foie gras, truffle, walnut and Bergerac wine."),
        ('🛶', 'Canoë', "Mai-septembre — descente de la Dordogne et de la Vézère.", 'Canoeing', "May–September — paddling down the Dordogne and Vézère rivers."),
        ('👨‍👩‍👧', 'Famille', "Juillet-août — canoë, châteaux, jardins de Marqueyssac et marchés nocturnes.", 'Family', "July–August — canoeing, castles, Marqueyssac gardens and night markets."),
    ],
    'normandie': [
        ('🏖️', 'Plages du Débarquement', "Avril-septembre — Omaha, Utah Beach et mémoriaux.", 'D-Day Beaches', "April–September — Omaha, Utah Beach and memorials."),
        ('🏰', 'Mont-Saint-Michel', "Toute l\'année — abbaye, marée et traversée de la baie à pied.", 'Mont-Saint-Michel', "Year-round — abbey, tides and bay crossing on foot."),
        ('🍽️', 'Gastronomie', "Toute l\'année — camembert, cidre, calvados et fruits de mer.", 'Gastronomy', "Year-round — camembert, cider, calvados and seafood."),
        ('🎨', 'Impressionnisme', "Avril-octobre — Giverny (Monet), Honfleur et Étretat.", 'Impressionism', "April–October — Giverny (Monet), Honfleur and Étretat."),
        ('👨‍👩‍👧', 'Famille', "Juillet-août — plages, Bayeux et parc Festyland.", 'Family', "July–August — beaches, Bayeux and Festyland park."),
    ],
    'strasbourg': [
        ('🎅', 'Marché de Noël', "Novembre-décembre — plus ancien marché de Noël de France (1570).", 'Christmas Market', "November–December — France\'s oldest Christmas market (1570)."),
        ('🏘️', 'Petite France', "Avril-septembre — maisons à colombages, canaux et cathédrale.", 'Petite France', "April–September — half-timbered houses, canals and cathedral."),
        ('🍽️', 'Gastronomie alsacienne', "Toute l\'année — choucroute, tarte flambée, bretzel et vins d\'Alsace.", 'Alsatian Food', "Year-round — sauerkraut, tarte flambée, pretzel and Alsace wines."),
        ('🚲', 'Route des vins', "Mai-octobre — Colmar, Riquewihr et villages vignerons à vélo.", 'Wine Route', "May–October — Colmar, Riquewihr and wine villages by bike."),
    ],
    'montpellier': [
        ('🏛️', 'Écusson & patrimoine', "Toute l\'année — place de la Comédie, Fabre et rues médiévales.", 'Écusson & Heritage', "Year-round — Place de la Comédie, Fabre Museum and medieval streets."),
        ('🏖️', 'Plages', "Juin-septembre — Palavas, Carnon et Grande-Motte à 15 min.", 'Beaches', "June–September — Palavas, Carnon and La Grande-Motte 15 min away."),
        ('🍷', 'Vin du Languedoc', "Toute l\'année — Pic Saint-Loup, vignobles et domaines à moins de 30 min.", 'Languedoc Wine', "Year-round — Pic Saint-Loup, vineyards and estates under 30 min away."),
        ('👨‍👩‍👧', 'Famille', "Mai-septembre — plages, Aquarium Mare Nostrum et vie étudiante animée.", 'Family', "May–September — beaches, Mare Nostrum Aquarium and lively student life."),
    ],
    'pays-basque': [
        ('🏄', 'Surf', "Avril-octobre — Biarritz, Anglet et Guéthary.", 'Surfing', "April–October — Biarritz, Anglet and Guéthary."),
        ('🍽️', 'Gastronomie', "Toute l\'année — piment d\'Espelette, fromage de brebis, cidre et pintxos.", 'Gastronomy', "Year-round — Espelette pepper, sheep cheese, cider and pintxos."),
        ('🥾', 'Randonnée', "Mai-octobre — La Rhune, gorges de Kakuetta et GR10.", 'Hiking', "May–October — La Rhune, Kakuetta gorge and GR10."),
        ('🏘️', 'Villages basques', "Toute l\'année — Ainhoa, Espelette, Saint-Jean-Pied-de-Port.", 'Basque Villages', "Year-round — Ainhoa, Espelette, Saint-Jean-Pied-de-Port."),
        ('🎭', 'Fêtes & culture', "Juillet-août — Fêtes de Bayonne, force basque et pelote.", 'Festivals & Culture', "July–August — Bayonne festivals, Basque force and pelota."),
    ],

    # Pour éviter un script trop long, je vais ajouter un fallback pour les destinations
    # sans cards spécifiques en utilisant des templates par type de destination.
}

# ─── TEMPLATES GÉNÉRIQUES (fallback) ─────────────────────────────────
# Pour les destinations sans cards spécifiques, générer des cards basées sur le type

TEMPLATES = {
    'tropical_beach': [
        ('🏖️', 'Plage & farniente', "Saison sèche — plages de sable, eaux chaudes et cocotiers.", 'Beach & Relaxation', "Dry season — sandy beaches, warm waters and palm trees."),
        ('🤿', 'Plongée & snorkeling', "Saison sèche — visibilité optimale et récifs coralliens.", 'Diving & Snorkelling', "Dry season — optimal visibility and coral reefs."),
        ('🍽️', 'Gastronomie locale', "Toute l\'année — cuisine locale, marchés et saveurs tropicales.", 'Local Food', "Year-round — local cuisine, markets and tropical flavours."),
        ('👨‍👩‍👧', 'Famille', "Saison sèche — activités nautiques, plages sécurisées.", 'Family', "Dry season — water activities, safe beaches."),
    ],
    'tropical_culture': [
        ('🏛️', 'Culture & temples', "Saison sèche — visites sans pluie, lumière idéale.", 'Culture & Temples', "Dry season — rain-free visits, ideal light."),
        ('🍽️', 'Street food & marchés', "Toute l\'année — cuisine de rue, marchés nocturnes.", 'Street Food & Markets', "Year-round — street food, night markets."),
        ('🥾', 'Nature & trek', "Saison sèche — sentiers praticables, vues dégagées.", 'Nature & Trekking', "Dry season — walkable trails, clear views."),
        ('👨‍👩‍👧', 'Famille', "Saison sèche — activités variées, températures supportables.", 'Family', "Dry season — varied activities, bearable temperatures."),
    ],
    'european_city': [
        ('🏛️', 'Patrimoine & musées', "Toute l\'année — centre historique, musées et architecture.", 'Heritage & Museums', "Year-round — historic centre, museums and architecture."),
        ('🍽️', 'Gastronomie', "Toute l\'année — cuisine locale, cafés et restaurants.", 'Gastronomy', "Year-round — local cuisine, cafés and restaurants."),
        ('🚶', 'Promenade urbaine', "Avril-octobre — quartiers historiques, parcs et terrasses.", 'City Walking', "April–October — historic quarters, parks and terraces."),
        ('👨‍👩‍👧', 'Famille', "Mai-septembre — parcs, musées et activités en plein air.", 'Family', "May–September — parks, museums and outdoor activities."),
    ],
    'med_beach': [
        ('🏖️', 'Plages', "Juin-septembre — plages de sable et eaux méditerranéennes.", 'Beaches', "June–September — sandy beaches and Mediterranean waters."),
        ('🍽️', 'Gastronomie', "Toute l\'année — cuisine méditerranéenne, poisson frais.", 'Gastronomy', "Year-round — Mediterranean cuisine, fresh fish."),
        ('🏛️', 'Patrimoine', "Avril-mai ou octobre — sites historiques sans la foule estivale.", 'Heritage', "April–May or October — historic sites without summer crowds."),
        ('👨‍👩‍👧', 'Famille', "Juin-septembre — mer chaude, activités et gastronomie.", 'Family', "June–September — warm sea, activities and gastronomy."),
    ],
    'desert_gulf': [
        ('🏖️', 'Plage & resorts', "Novembre-avril — plages, hôtels de luxe et activités nautiques.", 'Beach & Resorts', "November–April — beaches, luxury hotels and water activities."),
        ('🛍️', 'Shopping & luxe', "Novembre-mars — centres commerciaux, souks et duty-free.", 'Shopping & Luxury', "November–March — malls, souks and duty-free."),
        ('🏜️', 'Désert', "Octobre-mars — safari, dunes et nuits étoilées.", 'Desert', "October–March — safari, dunes and starry nights."),
        ('👨‍👩‍👧', 'Famille', "Décembre-février — parcs, plages et température agréable.", 'Family', "December–February — parks, beaches and pleasant temperature."),
    ],
    'mountain': [
        ('🥾', 'Randonnée', "Juin-septembre — sentiers dégagés, refuges ouverts.", 'Hiking', "June–September — clear trails, open mountain huts."),
        ('📸', 'Paysages', "Juin-octobre — lumière optimale, vues panoramiques.", 'Landscapes', "June–October — optimal light, panoramic views."),
        ('🌿', 'Nature & faune', "Mai-octobre — flore alpine, animaux sauvages.", 'Nature & Wildlife', "May–October — alpine flora, wild animals."),
        ('⛷️', 'Ski', "Décembre-mars — stations, neige et activités hivernales.", 'Skiing', "December–March — resorts, snow and winter activities."),
    ],
}

# Mapping slug → template type for destinations without specific cards
SLUG_TEMPLATE = {}

# Auto-classify remaining destinations
import csv as csv_mod
with open(f'{DATA}/destinations.csv', encoding='utf-8-sig') as f:
    all_dests = list(csv_mod.DictReader(f))

existing_card_slugs = set(CARDS.keys())
with open(f'{DATA}/cards.csv', encoding='utf-8-sig') as f:
    for row in csv_mod.DictReader(f):
        existing_card_slugs.add(row['slug'])

for d in all_dests:
    slug = d['slug_fr']
    if slug in existing_card_slugs:
        continue
    lat = float(d['lat'])
    trop = d.get('tropical','') == 'True'
    pays = d['pays']
    
    # Classify
    if slug in ['dolomites', 'chamonix', 'yellowstone', 'nepal', 'sapa', 'machu-picchu', 'bolivie', 'patagonie']:
        SLUG_TEMPLATE[slug] = 'mountain'
    elif slug in ['abu-dhabi', 'doha', 'oman', 'sharm-el-sheikh', 'hurghada', 'marsa-alam']:
        SLUG_TEMPLATE[slug] = 'desert_gulf'
    elif trop and pays in ['Thaïlande', 'Philippines', 'Indonésie', 'Viêt Nam', 'Malaisie', 'Cambodge', 'Laos', 'Myanmar', 'Inde']:
        SLUG_TEMPLATE[slug] = 'tropical_culture'
    elif trop:
        SLUG_TEMPLATE[slug] = 'tropical_beach'
    elif pays in ['Grèce', 'Turquie', 'Tunisie', 'Chypre', 'Malte', 'Croatie', 'Italie', 'Espagne', 'Portugal']:
        SLUG_TEMPLATE[slug] = 'med_beach'
    else:
        SLUG_TEMPLATE[slug] = 'european_city'


def run():
    # 1. Update destinations.csv with taglines
    with open(f'{DATA}/destinations.csv', encoding='utf-8-sig') as f:
        reader = csv_mod.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)
    
    updated = 0
    for row in rows:
        slug = row['slug_fr']
        if slug in TAGLINES:
            fr, en = TAGLINES[slug]
            if not row.get('hero_sub','').strip():
                row['hero_sub'] = fr
                updated += 1
            if not row.get('hero_sub_en','').strip():
                row['hero_sub_en'] = en
    
    with open(f'{DATA}/destinations.csv', 'w', encoding='utf-8-sig', newline='') as f:
        w = csv_mod.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)
    
    print(f"Taglines FR/EN mis à jour: {updated} destinations")
    
    # 2. Append to cards.csv
    with open(f'{DATA}/cards.csv', encoding='utf-8-sig') as f:
        existing = list(csv_mod.DictReader(f))
    existing_slugs_cards = set(r['slug'] for r in existing)
    
    new_cards_fr = []
    new_cards_en = []
    
    for slug, cards in CARDS.items():
        if slug in existing_slugs_cards:
            continue
        for icon, titre_fr, texte_fr, title_en, text_en in cards:
            new_cards_fr.append({'slug': slug, 'icon': icon, 'titre': titre_fr, 'texte': texte_fr})
            new_cards_en.append({'slug': slug, 'icon': icon, 'title': title_en, 'text': text_en})
    
    # Add template-based cards
    for slug, tpl_type in SLUG_TEMPLATE.items():
        if slug in existing_slugs_cards or slug in CARDS:
            continue
        tpl = TEMPLATES[tpl_type]
        for icon, titre_fr, texte_fr, title_en, text_en in tpl:
            new_cards_fr.append({'slug': slug, 'icon': icon, 'titre': titre_fr, 'texte': texte_fr})
            new_cards_en.append({'slug': slug, 'icon': icon, 'title': title_en, 'text': text_en})
    
    # Append FR cards
    with open(f'{DATA}/cards.csv', 'a', encoding='utf-8-sig', newline='') as f:
        w = csv_mod.DictWriter(f, fieldnames=['slug', 'icon', 'titre', 'texte'])
        for card in new_cards_fr:
            w.writerow(card)
    
    # Append EN cards
    with open(f'{DATA}/cards_en.csv', 'a', encoding='utf-8-sig', newline='') as f:
        w = csv_mod.DictWriter(f, fieldnames=['slug', 'icon', 'title', 'text'])
        for card in new_cards_en:
            w.writerow(card)
    
    print(f"Nouvelles cartes FR: {len(new_cards_fr)}")
    print(f"Nouvelles cartes EN: {len(new_cards_en)}")
    
    # Stats
    template_count = sum(1 for s in SLUG_TEMPLATE if s not in CARDS and s not in existing_slugs_cards)
    specific_count = sum(1 for s in CARDS if s not in existing_slugs_cards)
    print(f"  - Cartes spécifiques: {specific_count} destinations")
    print(f"  - Cartes template: {template_count} destinations")


if __name__ == '__main__':
    run()
