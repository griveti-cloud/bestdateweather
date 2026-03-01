#!/usr/bin/env python3
"""
enrich_destinations.py — BestDateWeather
=========================================
Adds original taglines (hero_sub / hero_sub_en) and activity cards
for 236 destinations that currently have generic content.

Usage:
  python3 enrich_destinations.py          # update CSVs
  python3 enrich_destinations.py --dry-run # preview without writing
"""

import csv, os, sys

DIR = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(DIR, 'data')

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TAGLINES: {slug: (hero_sub_fr, hero_sub_en)}
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TAGLINES = {
# ── GRÈCE ──
'athenes': ("Berceau de la civilisation, Acropole et tavernes — l'été athénien est étouffant, le printemps et l'automne parfaits.",
            "Cradle of civilisation, Acropolis and tavernas — Athens summers are scorching, spring and autumn perfect."),
'zakynthos': ("Eaux turquoise de Navagio, tortues Caretta Caretta et criques secrètes.",
              "Turquoise waters of Navagio, Caretta Caretta turtles and hidden coves."),
'naxos': ("La plus grande île des Cyclades — plages infinies, temples antiques et fromage local.",
          "The largest Cycladic island — endless beaches, ancient temples and local cheese."),
'paros': ("Cyclades authentiques, villages blancs et vent du Meltemi.",
          "Authentic Cyclades, whitewashed villages and Meltemi winds."),
'kefalonia': ("Plages turquoise, grottes sous-marines et villages de montagne — la plus grande île Ionienne.",
              "Turquoise beaches, underwater caves and mountain villages — the largest Ionian island."),
'kos': ("Île du Dodécanèse entre plages et sources thermales, face aux côtes turques.",
        "Dodecanese island between beaches and thermal springs, facing the Turkish coast."),
'lefkada': ("Falaises blanches et eaux bleu électrique — l'une des plus belles côtes de Grèce.",
            "White cliffs and electric blue waters — one of Greece's most beautiful coastlines."),
'thessalonique': ("Deuxième ville de Grèce — marchés ottomans, front de mer animé et gastronomie du nord.",
                  "Greece's second city — Ottoman markets, lively waterfront and northern cuisine."),
'hydra': ("Île sans voiture à une heure d'Athènes — sentiers côtiers, tavernes et art contemporain.",
          "Car-free island one hour from Athens — coastal trails, tavernas and contemporary art."),
'milos': ("Cyclades volcaniques — plages multicolores de Sarakiniko et Firiplaka.",
          "Volcanic Cyclades — multicoloured beaches of Sarakiniko and Firiplaka."),

# ── ITALIE ──
'milan': ("Capitale du design et de la mode — Duomo, La Cène et quartiers créatifs.",
          "Capital of design and fashion — Duomo, The Last Supper and creative districts."),
'naples': ("Chaos vibrant, pizza originale et porte d'entrée de Pompéi et de la côte amalfitaine.",
           "Vibrant chaos, original pizza and gateway to Pompeii and the Amalfi Coast."),
'lac-come': ("Villas Belle Époque, eaux alpines et jardins botaniques — le lac le plus glamour d'Italie.",
             "Belle Époque villas, alpine waters and botanical gardens — Italy's most glamorous lake."),
'lac-garde': ("Le plus grand lac d'Italie — entre montagnes, citronniers et sports nautiques.",
              "Italy's largest lake — between mountains, lemon groves and water sports."),
'cinque-terre': ("Cinq villages accrochés aux falaises de Ligurie — sentiers, pesto et vignobles en terrasses.",
                 "Five villages clinging to Ligurian cliffs — trails, pesto and terraced vineyards."),
'bologne': ("Capitale gastronomique de l'Italie — mortadelle, tortellini, Lambrusco et portiques sans fin.",
            "Italy's food capital — mortadella, tortellini, Lambrusco and endless porticoes."),
'pouilles': ("Trulli de pierre, mer cristalline et huile d'olive — le talon de la botte italienne.",
             "Stone trulli, crystal-clear sea and olive oil — the heel of Italy's boot."),
'palerme': ("Carrefour de cultures — street food arabe-normand, Mondello et marchés de Ballarò.",
            "Cultural crossroads — Arab-Norman street food, Mondello and Ballarò markets."),
'turin': ("Première capitale de l'Italie — Alpes en toile de fond, chocolat et musées égyptiens.",
          "Italy's first capital — Alps backdrop, chocolate and Egyptian museums."),
'verone': ("Cité de Roméo et Juliette — arènes romaines, opéra en plein air et vins de Valpolicella.",
           "City of Romeo and Juliet — Roman arena, open-air opera and Valpolicella wines."),
'dolomites': ("Cathédrales de calcaire, ski de classe mondiale et refuges alpins.",
              "Limestone cathedrals, world-class skiing and alpine refuges."),

# ── ESPAGNE ──
'madrid': ("Capitale nocturne de l'Europe — Prado, Reina Sofía et terrasses tapas jusqu'à minuit.",
           "Europe's nightlife capital — Prado, Reina Sofía and tapas terraces until midnight."),
'grenade': ("L'Alhambra, le quartier de l'Albaicín et la Sierra Nevada à 30 minutes.",
            "The Alhambra, Albaicín quarter and Sierra Nevada 30 minutes away."),
'cordoue': ("Mosquée-cathédrale, patios fleuris et chaleur estivale intense.",
            "Mosque-cathedral, flower-filled patios and intense summer heat."),
'cadix': ("La plus ancienne ville d'Europe occidentale — plages de surf, carnaval et gastronomie maritime.",
          "Western Europe's oldest city — surf beaches, carnival and seafood cuisine."),
'costa-brava': ("Criques rocheuses, eaux cristallines et héritage Dalí — la côte sauvage de Catalogne.",
                "Rocky coves, crystal waters and Dalí heritage — Catalonia's wild coast."),
'saint-sebastien': ("Gastronomie au sommet mondial — pintxos, plage de la Concha et surf à Zurriola.",
                    "World-class gastronomy — pintxos, La Concha beach and surfing at Zurriola."),
'bilbao': ("Guggenheim, pintxos et montagnes basques — la renaissance culturelle du nord de l'Espagne.",
           "Guggenheim, pintxos and Basque mountains — northern Spain's cultural renaissance."),
'formentera': ("L'île secrète des Baléares — plages caribéennes à 30 minutes d'Ibiza.",
               "The Balearics' secret island — Caribbean-like beaches 30 minutes from Ibiza."),
'la-gomera': ("Forêt de laurisylve, sentiers spectaculaires et sifflement Silbo Gomero.",
              "Laurel forest, spectacular trails and Silbo Gomero whistling language."),
'la-palma': ("La Isla Bonita — volcans, ciel étoilé et forêts de pins canariens.",
             "La Isla Bonita — volcanoes, starry skies and Canary Island pine forests."),
'el-hierro': ("Réserve de biosphère — l'île la plus sauvage des Canaries, plongée volcanique.",
              "Biosphere reserve — the wildest Canary Island, volcanic diving."),

# ── PORTUGAL ──
'acores': ("Archipel volcanique en plein Atlantique — lacs de cratère, baleines et hortensias.",
           "Volcanic archipelago in the mid-Atlantic — crater lakes, whales and hydrangeas."),
'faro': ("Porte d'entrée de l'Algarve — Ria Formosa, île déserte et vieille ville fortifiée.",
         "Gateway to the Algarve — Ria Formosa, desert islands and fortified old town."),
'sintra': ("Palais enchantés dans la brume — à 30 minutes de Lisbonne, une autre dimension.",
           "Enchanted palaces in the mist — 30 minutes from Lisbon, another dimension."),

# ── FRANCE ──
'biarritz': ("Surf et élégance basque — rocher de la Vierge, vagues de la Côte des Basques et chocolat.",
             "Surf and Basque elegance — Rocher de la Vierge, Côte des Basques waves and chocolate."),
'pays-basque': ("Montagnes, océan et gastronomie d'exception — Espelette, Bayonne et criques sauvages.",
                "Mountains, ocean and exceptional gastronomy — Espelette, Bayonne and wild coves."),
'normandie': ("Plages du Débarquement, Mont-Saint-Michel et Camembert — l'histoire de France face à la Manche.",
              "D-Day beaches, Mont-Saint-Michel and Camembert — French history facing the Channel."),
'dordogne': ("Châteaux médiévaux, grottes préhistoriques et gastronomie périgourdine — foie gras, truffes et noix.",
             "Medieval castles, prehistoric caves and Périgord cuisine — foie gras, truffles and walnuts."),
'chamonix': ("Au pied du Mont-Blanc — ski, alpinisme et Aiguille du Midi à 3 842 m.",
             "At the foot of Mont Blanc — skiing, mountaineering and Aiguille du Midi at 3,842m."),
'montpellier': ("Cité universitaire méditerranéenne — entre plages du Languedoc et garrigues du Pic Saint-Loup.",
                "Mediterranean university city — between Languedoc beaches and Pic Saint-Loup garrigue."),
'strasbourg': ("Capitale européenne — petite France, marché de Noël et choucroute alsacienne.",
               "European capital — Petite France, Christmas market and Alsatian sauerkraut."),
'guadeloupe': ("Papillon des Caraïbes — volcans, mangroves, plages et rhum agricole.",
               "Caribbean butterfly — volcanoes, mangroves, beaches and agricultural rum."),
'martinique': ("Île aux fleurs — montagne Pelée, plages de sable noir et blanc, yoles rondes.",
               "Island of flowers — Mount Pelée, black and white sand beaches, traditional yoles."),
'guyane': ("Forêt amazonienne française — Centre Spatial Guyanais, biodiversité extrême.",
           "French Amazonia — Guiana Space Centre, extreme biodiversity."),
'mayotte': ("Lagon fermé le plus grand du monde — tortues marines, makis et récif corallien préservé.",
            "World's largest enclosed lagoon — sea turtles, lemurs and preserved coral reef."),
'polynesie': ("Îles du Pacifique Sud — lagons turquoise, bungalows sur pilotis et culture polynésienne.",
              "South Pacific islands — turquoise lagoons, overwater bungalows and Polynesian culture."),
'nouvelle-caledonie': ("Lagon inscrit à l'UNESCO, récif-barrière et culture kanak — bout du monde français.",
                       "UNESCO-listed lagoon, barrier reef and Kanak culture — France's far end."),
'saint-barthelemy': ("Petit bijou des Antilles — plages intimistes, gastronomie française et luxe discret.",
                     "Caribbean gem — intimate beaches, French gastronomy and understated luxury."),
'saint-martin': ("Deux nations sur une île — plages, cuisine créole côté français, casinos côté néerlandais.",
                 "Two nations on one island — beaches, Creole cuisine on the French side, casinos on the Dutch."),
'saint-pierre-et-miquelon': ("Archipel français au large du Canada — brumes, morues et ambiance terre-neuvienne.",
                              "French archipelago off Canada — fog, cod and Newfoundland atmosphere."),

# ── CROATIE ──
'hvar': ("Île de lavande et de vignobles — Stari Grad, plages secrètes et vie nocturne glamour.",
         "Island of lavender and vineyards — Stari Grad, secret beaches and glamorous nightlife."),
'kotor': ("Fjord des Balkans — remparts vénitiens, vieille ville médiévale et montagnes plongeant dans l'Adriatique.",
          "Balkan fjord — Venetian ramparts, medieval old town and mountains plunging into the Adriatic."),
'zadar': ("Orgues marines, soleil de Hitchcock et îles Kornati — la Dalmatie authentique.",
          "Sea organ, Hitchcock's sunset and Kornati islands — authentic Dalmatia."),
'zagreb': ("Capitale méconnue — marchés, musées décalés et scène café-culture effervescente.",
           "Overlooked capital — markets, quirky museums and buzzing café culture."),
'plitvice': ("Lacs en cascade turquoise au cœur de la Croatie — sentiers dans la forêt primaire.",
             "Cascading turquoise lakes in the heart of Croatia — trails through primeval forest."),
'montenegro': ("Bouches de Kotor, Sveti Stefan et montagnes sauvages — le joyau caché de l'Adriatique.",
               "Bay of Kotor, Sveti Stefan and wild mountains — the Adriatic's hidden gem."),

# ── TURQUIE ──
'antalya': ("Riviera turque — plages de sable, vieille ville Kaleiçi et cascades de Düden.",
            "Turkish Riviera — sandy beaches, Kaleiçi old town and Düden waterfalls."),
'bodrum': ("Saint-Tropez de la Turquie — château croisé, plages et vie nocturne cosmopolite.",
           "Turkey's Saint-Tropez — crusader castle, beaches and cosmopolitan nightlife."),
'cappadoce': ("Paysages lunaires, montgolfières à l'aube et cités souterraines millénaires.",
              "Lunar landscapes, dawn hot air balloons and ancient underground cities."),
'fethiye': ("Lagune d'Ölüdeniz, voie lycienne et parapente au-dessus de la mer Turquoise.",
            "Ölüdeniz lagoon, Lycian Way and paragliding over the Turquoise Coast."),
'izmir': ("Troisième ville de Turquie — bazar Kemeraltı, Éphèse à 1 h et côte égéenne préservée.",
          "Turkey's third city — Kemeraltı bazaar, Ephesus 1h away and preserved Aegean coast."),

# ── EUROPE DU NORD ──
'dublin': ("Pubs vivants, falaises de Howth et histoire littéraire — quand la météo le permet.",
           "Lively pubs, Howth cliffs and literary history — when the weather allows."),
'copenhague': ("Design scandinave, Nyhavn et vélo — la ville la plus heureuse du monde.",
               "Scandinavian design, Nyhavn and cycling — the world's happiest city."),
'stockholm': ("14 îles, musée Vasa et archipel — les nuits blanches d'été transforment la ville.",
              "14 islands, Vasa museum and archipelago — white summer nights transform the city."),
'oslo': ("Fjords urbains, saunas au bord de l'eau et scène gastronomique nordique.",
         "Urban fjords, waterside saunas and Nordic culinary scene."),
'helsinki': ("Architecture Art Nouveau, saunas et îles — Helsinki surprend par sa lumière estivale.",
             "Art Nouveau architecture, saunas and islands — Helsinki surprises with its summer light."),
'bergen': ("Porte des fjords — maisons en bois de Bryggen, pluie fréquente et nature spectaculaire.",
           "Gateway to the fjords — Bryggen wooden houses, frequent rain and spectacular nature."),
'tromso': ("Aurores boréales en hiver, soleil de minuit en été — l'Arctique accessible.",
           "Northern lights in winter, midnight sun in summer — the accessible Arctic."),
'lofoten': ("Îles arctiques spectaculaires — pêche, surf polaire et aurores boréales.",
            "Spectacular Arctic islands — fishing, polar surfing and northern lights."),
'laponie': ("Rennes, aurores boréales et silence blanc — le Grand Nord finlandais.",
            "Reindeer, northern lights and white silence — the Finnish Far North."),

# ── EUROPE CENTRALE & EST ──
'budapest': ("Bains thermaux, ruin bars et Danube — la plus belle capitale d'Europe centrale.",
             "Thermal baths, ruin bars and Danube — Central Europe's most beautiful capital."),
'cracovie': ("Vieille ville médiévale, mines de sel de Wieliczka et mémoire d'Auschwitz.",
             "Medieval old town, Wieliczka salt mines and Auschwitz memorial."),
'bruxelles': ("Grand-Place, BD, gaufres et art nouveau — l'Europe en concentré.",
              "Grand-Place, comics, waffles and Art Nouveau — Europe in concentrate."),
'bruges': ("Canaux médiévaux, chocolat et beffroi — la Venise du Nord figée dans le temps.",
           "Medieval canals, chocolate and belfry — the Venice of the North frozen in time."),
'bratislava': ("Petite capitale danubienne — château, vieille ville compacte et vignobles à 15 minutes.",
               "Small Danubian capital — castle, compact old town and vineyards 15 minutes away."),
'bucarest': ("Palais du Parlement, quartier bohème Lipscani et vie nocturne intense.",
             "Palace of Parliament, bohemian Lipscani quarter and intense nightlife."),
'varsovie': ("Capitale reconstruite — vieille ville UNESCO, musées poignants et scène culinaire moderne.",
             "Rebuilt capital — UNESCO old town, moving museums and modern food scene."),
'sofia': ("Cathédrale Alexandre-Nevski, mont Vitosha et thermes romains — la capitale la plus abordable d'Europe.",
          "Alexander Nevsky Cathedral, Vitosha mountain and Roman baths — Europe's most affordable capital."),
'transylvanie': ("Châteaux de Dracula, villages saxons et Carpates sauvages.",
                 "Dracula's castles, Saxon villages and wild Carpathians."),
'vilnius': ("Vieille ville baroque, street art et forêts de pins — la perle méconnue de la Baltique.",
            "Baroque old town, street art and pine forests — the Baltic's hidden pearl."),
'tallinn': ("Cité médiévale intacte, scène tech et côte baltique — l'Estonie entre passé et futur.",
            "Intact medieval city, tech scene and Baltic coast — Estonia between past and future."),
'riga': ("Art Nouveau monumental, marché central et vieille ville hanséatique.",
         "Monumental Art Nouveau, central market and Hanseatic old town."),
'ljubljana': ("Dragon de bronze, rivière Ljubljanica et grotte de Postojna à 45 minutes.",
              "Bronze dragon, Ljubljanica river and Postojna cave 45 minutes away."),
'georgie': ("Caucase, vin naturel 8000 ans et hospitalité légendaire — entre Europe et Asie.",
            "Caucasus, 8000-year natural wine and legendary hospitality — between Europe and Asia."),
'tbilissi': ("Bains sulfureux, forteresse Narikala et cuisine géorgienne au carrefour des mondes.",
             "Sulphur baths, Narikala fortress and Georgian cuisine at the crossroads of worlds."),
'ouzbekistan': ("Route de la Soie — Samarcande, Boukhara et Khiva, architectures turquoise millénaires.",
                "Silk Road — Samarkand, Bukhara and Khiva, millenary turquoise architecture."),

# ── ALLEMAGNE, SUISSE, AUTRICHE ──
'munich': ("Bière, Alpes et culture — Marienplatz, jardins anglais et Oktoberfest.",
           "Beer, Alps and culture — Marienplatz, English Garden and Oktoberfest."),
'francfort': ("Skyline bancaire, cidre de pomme et musées du Main — escale ou séjour.",
              "Banking skyline, apple cider and Main riverbank museums — stopover or stay."),
'hambourg': ("Port gigantesque, Speicherstadt et scène musicale — la ville la plus rock d'Allemagne.",
             "Giant port, Speicherstadt and music scene — Germany's most rock'n'roll city."),
'geneve': ("Jet d'eau, montres et diplomatie — entre lac Léman et Mont-Blanc.",
           "Jet d'Eau, watches and diplomacy — between Lake Geneva and Mont Blanc."),
'zurich': ("Capitale financière, lac cristallin et vieille ville médiévale — l'élégance suisse.",
           "Financial capital, crystal-clear lake and medieval old town — Swiss elegance."),

# ── ASIE DU SUD-EST ──
'chiang-mai': ("Temples dorés, marchés nocturnes et montagnes — le nord spirituel de la Thaïlande.",
               "Golden temples, night markets and mountains — Thailand's spiritual north."),
'koh-lanta': ("Île tranquille de la mer d'Andaman — plages longues, mangroves et vie décontractée.",
              "Peaceful Andaman Sea island — long beaches, mangroves and laid-back life."),
'koh-samui': ("Cocotiers, temples dorés et Full Moon Party voisine — le golfe de Thaïlande accessible.",
              "Coconut palms, golden temples and nearby Full Moon Party — accessible Gulf of Thailand."),
'koh-phi-phi': ("Falaises karstiques, snorkeling et Maya Bay — l'archipel iconique de Thaïlande.",
                "Karst cliffs, snorkelling and Maya Bay — Thailand's iconic archipelago."),
'koh-tao': ("Capitale mondiale de la plongée accessible — récifs coralliens et requins-baleines.",
            "World capital of accessible diving — coral reefs and whale sharks."),
'krabi': ("Falaises de calcaire, îles aux quatre-îles et Railay Beach — la mer d'Andaman côté continent.",
          "Limestone cliffs, Four Islands and Railay Beach — Andaman Sea from the mainland."),
'pattaya': ("Station balnéaire animée du golfe de Thaïlande — plages, temples et îles proches.",
            "Bustling Gulf of Thailand beach resort — beaches, temples and nearby islands."),
'hanoi': ("Vieux quartier millénaire, phở matinal et lac Hoàn Kiếm — le cœur du Vietnam.",
          "Thousand-year-old quarter, morning phở and Hoàn Kiếm lake — the heart of Vietnam."),
'ho-chi-minh': ("Saïgon effervescente — scooters, street food et vestiges coloniaux.",
                "Buzzing Saigon — scooters, street food and colonial vestiges."),
'da-nang': ("Plage de My Khe, pont Dragon et Bà Nà Hills — le Vietnam balnéaire moderne.",
            "My Khe beach, Dragon Bridge and Bà Nà Hills — modern coastal Vietnam."),
'baie-halong': ("3 000 îlots karstiques émergeant de la brume — l'une des merveilles naturelles du monde.",
                "3,000 karst islets emerging from the mist — one of the world's natural wonders."),
'da-lat': ("Station d'altitude vietnamienne — cascades, fleurs et fraîcheur à 1 500 m.",
           "Vietnamese hill station — waterfalls, flowers and cool air at 1,500m."),
'nha-trang': ("Baie aux îles, plongée et vie nocturne — la station balnéaire du sud Vietnam.",
              "Island-studded bay, diving and nightlife — southern Vietnam's beach resort."),
'sapa': ("Rizières en terrasses, ethnies H'mong et Dao, trek dans les montagnes du Tonkin.",
         "Terraced rice paddies, H'mong and Dao peoples, trekking in Tonkin mountains."),
'cambodge': ("Angkor Vat, Phnom Penh et côte méconnue — temples khmers et renaissance culturelle.",
             "Angkor Wat, Phnom Penh and hidden coast — Khmer temples and cultural renaissance."),
'phnom-penh': ("Capitale cambodgienne en plein essor — Palais Royal, marchés et bords du Mékong.",
               "Booming Cambodian capital — Royal Palace, markets and Mekong riverbanks."),
'laos': ("Luang Prabang, Mékong et temples dorés — le pays le plus tranquille d'Asie du Sud-Est.",
         "Luang Prabang, Mekong and golden temples — Southeast Asia's most tranquil country."),
'luang-prabang': ("Moines à l'aube, cascades de Kuang Si et bords du Mékong — joyau de l'UNESCO.",
                  "Monks at dawn, Kuang Si falls and Mekong banks — UNESCO gem."),
'myanmar': ("Pagodes de Bagan, lac Inle et hospitalité birmane — un pays hors du temps.",
            "Bagan pagodas, Inle Lake and Burmese hospitality — a country beyond time."),
'kuala-lumpur': ("Tours Petronas, street food multiculturelle et grottes de Batu.",
                "Petronas Towers, multicultural street food and Batu Caves."),
'langkawi': ("Archipel malaisien duty-free — plages, mangroves et téléphérique panoramique.",
             "Duty-free Malaysian archipelago — beaches, mangroves and panoramic cable car."),
'penang': ("Capitale du street food asiatique — George Town UNESCO et art de rue.",
           "Asian street food capital — UNESCO George Town and street art."),

# ── INDONÉSIE ──
'ubud': ("Cœur culturel de Bali — rizières de Tegallalang, temples et yoga.",
         "Bali's cultural heart — Tegallalang rice terraces, temples and yoga."),
'canggu': ("Surf, cafés hipster et couchers de soleil sur le temple de Tanah Lot.",
           "Surf, hipster cafés and sunsets over Tanah Lot temple."),
'lombok': ("Voisine sauvage de Bali — mont Rinjani, îles Gili et plages désertes.",
           "Bali's wild neighbour — Mount Rinjani, Gili Islands and deserted beaches."),
'gili': ("Trois îlots sans voiture — snorkeling avec les tortues, couchers de soleil légendaires.",
         "Three car-free islets — snorkelling with turtles, legendary sunsets."),
'nusa-penida': ("Falaises dramatiques, raies manta et plages sauvages — le Bali brut.",
                "Dramatic cliffs, manta rays and wild beaches — raw Bali."),
'java': ("Borobudur, volcans actifs et culture javanaise — le cœur de l'Indonésie.",
         "Borobudur, active volcanoes and Javanese culture — the heart of Indonesia."),
'komodo': ("Dragons de Komodo, snorkeling de classe mondiale et savane tropicale.",
           "Komodo dragons, world-class snorkelling and tropical savannah."),
'borneo': ("Orangs-outans, forêt primaire et plongée à Sipadan — la nature à l'état brut.",
           "Orangutans, primary forest and diving at Sipadan — nature in its purest state."),

# ── PHILIPPINES ──
'philippines': ("7 107 îles — rizières d'Ifugao, plages de sable blanc et requins-baleines.",
                "7,107 islands — Ifugao rice terraces, white sand beaches and whale sharks."),
'palawan': ("Dernière frontière des Philippines — lagons secrets, El Nido et rivière souterraine.",
            "The Philippines' last frontier — secret lagoons, El Nido and underground river."),
'el-nido': ("Lagons turquoise entre falaises karstiques — le paradis philippin.",
            "Turquoise lagoons between karst cliffs — the Philippine paradise."),
'cebu': ("Requins-baleines d'Oslob, cascades de Kawasan et plongée à Moalboal.",
         "Oslob whale sharks, Kawasan falls and diving at Moalboal."),
'boracay': ("White Beach légendaire — 4 km de sable blanc, vie nocturne et sports nautiques.",
            "Legendary White Beach — 4km of white sand, nightlife and water sports."),
'siargao': ("Capitale du surf aux Philippines — Cloud 9, lagons et palmiers à perte de vue.",
            "Philippines' surf capital — Cloud 9, lagoons and endless palm trees."),

# ── ASIE DU NORD-EST ──
'kyoto': ("Ancienne capitale impériale — 2 000 temples, jardins zen et geishas de Gion.",
          "Former imperial capital — 2,000 temples, zen gardens and Gion geishas."),
'osaka': ("Capitale du street food japonais — takoyaki, Dōtonbori et château d'Osaka.",
          "Japan's street food capital — takoyaki, Dōtonbori and Osaka Castle."),
'hiroshima': ("Mémorial de la Paix, île de Miyajima et okonomiyaki — résilience et beauté.",
              "Peace Memorial, Miyajima island and okonomiyaki — resilience and beauty."),
'okinawa': ("Japon subtropical — plages de corail, cuisine centenaire et culture Ryukyu.",
            "Subtropical Japan — coral beaches, centenarian cuisine and Ryukyu culture."),
'seoul': ("K-pop, palais royaux et street food — mégapole entre tradition et hyper-modernité.",
          "K-pop, royal palaces and street food — megacity between tradition and hyper-modernity."),
'busan': ("Deuxième ville de Corée — plage de Haeundae, temple Haedong Yonggungsa et marché de Jagalchi.",
          "Korea's second city — Haeundae beach, Haedong Yonggungsa temple and Jagalchi market."),
'jeju': ("Île volcanique coréenne — haenyeo plongeuses, cascades et cratère Hallasan.",
         "Korean volcanic island — haenyeo divers, waterfalls and Hallasan crater."),
'pekin': ("Cité Interdite, Grande Muraille et canard laqué — 3 000 ans d'histoire impériale.",
          "Forbidden City, Great Wall and Peking duck — 3,000 years of imperial history."),
'shanghai': ("Skyline futuriste du Bund, concessions françaises et xiaolongbao.",
             "Futuristic Bund skyline, French Concession and xiaolongbao."),
'hong-kong': ("Gratte-ciels, dim sum et sentiers de montagne — entre Chine et monde.",
              "Skyscrapers, dim sum and mountain trails — between China and the world."),
'macao': ("Las Vegas d'Asie — casinos, patrimoine portugais et egg tarts.",
          "Asia's Las Vegas — casinos, Portuguese heritage and egg tarts."),
'taipei': ("Temples, marchés nocturnes et Taipei 101 — la perle méconnue d'Asie de l'Est.",
           "Temples, night markets and Taipei 101 — East Asia's hidden pearl."),

# ── INDE & NÉPAL ──
'delhi': ("Chaos organisé, forts moghols et street food épicée — porte d'entrée de l'Inde.",
          "Organised chaos, Mughal forts and spicy street food — gateway to India."),
'kerala': ("Backwaters, plantations de thé et Ayurveda — le pays de Dieu au sud de l'Inde.",
           "Backwaters, tea plantations and Ayurveda — God's Own Country in southern India."),
'rajasthan': ("Palais de maharajas, désert du Thar et forts spectaculaires — l'Inde royale.",
              "Maharaja palaces, Thar desert and spectacular forts — royal India."),
'nepal': ("Himalaya, Katmandou et trek de l'Annapurna — le toit du monde accessible.",
          "Himalayas, Kathmandu and Annapurna trek — the accessible roof of the world."),
'sri-lanka': ("Temples bouddhistes, plantations de thé et plages dorées — l'île aux mille visages.",
              "Buddhist temples, tea plantations and golden beaches — the island of a thousand faces."),

# ── MOYEN-ORIENT ──
'abu-dhabi': ("Louvre du désert, mosquée Sheikh Zayed et îles de mangrove — le luxe émirien mesuré.",
              "Desert Louvre, Sheikh Zayed mosque and mangrove islands — measured Emirati luxury."),
'jordanie': ("Petra, Wadi Rum et mer Morte — entre histoire nabatéenne et désert martien.",
             "Petra, Wadi Rum and the Dead Sea — between Nabataean history and Martian desert."),
'oman': ("Fjords du Musandam, dunes de Wahiba et souks à l'encens — l'Arabie authentique.",
         "Musandam fjords, Wahiba dunes and frankincense souks — authentic Arabia."),
'doha': ("Musée d'art islamique, souq Waqif et skyline futuriste — le Qatar en pleine mutation.",
         "Museum of Islamic Art, Souq Waqif and futuristic skyline — Qatar in transformation."),
'tel-aviv': ("Bauhaus blanc, plages urbaines et gastronomie fusion — la ville qui ne dort jamais.",
             "White Bauhaus, urban beaches and fusion cuisine — the city that never sleeps."),

# ── ÉGYPTE ──
'le-caire': ("Pyramides de Gizeh, souk Khan el-Khalili et musée national — 5 000 ans d'histoire.",
             "Giza Pyramids, Khan el-Khalili souk and national museum — 5,000 years of history."),
'hurghada': ("Plongée en mer Rouge, récifs coralliens et soleil garanti — la station balnéaire égyptienne.",
             "Red Sea diving, coral reefs and guaranteed sunshine — Egypt's beach resort."),
'louxor': ("Vallée des Rois, temples de Karnak et croisière sur le Nil — l'Égypte antique concentrée.",
           "Valley of the Kings, Karnak temples and Nile cruise — concentrated ancient Egypt."),
'sharm-el-sheikh': ("Snorkeling au Ras Mohammed, désert du Sinaï et stations all-inclusive.",
                    "Ras Mohammed snorkelling, Sinai desert and all-inclusive resorts."),
'marsa-alam': ("Dugongs, récifs vierges et tortues vertes — la mer Rouge préservée.",
               "Dugongs, pristine reefs and green turtles — the preserved Red Sea."),

# ── AFRIQUE ──
'kenya': ("Safari Big Five, migration du Masaï Mara et plages de Diani — l'Afrique essentielle.",
          "Big Five safari, Masai Mara migration and Diani beaches — essential Africa."),
'diani': ("Plage de sable blanc sur l'océan Indien — cocotiers, plongée et vie décontractée.",
          "White sand beach on the Indian Ocean — coconut palms, diving and laid-back life."),
'tanzanie': ("Serengeti, Kilimandjaro et Zanzibar — safari et plage dans un seul voyage.",
             "Serengeti, Kilimanjaro and Zanzibar — safari and beach in one trip."),
'namibie': ("Dunes de Sossusvlei, faune du désert et Skeleton Coast — paysages d'un autre monde.",
            "Sossusvlei dunes, desert wildlife and Skeleton Coast — otherworldly landscapes."),
'senegal': ("Dakar, Saint-Louis et parc du Djoudj — musique, hospitalité teranga et oiseaux migrateurs.",
            "Dakar, Saint-Louis and Djoudj park — music, teranga hospitality and migratory birds."),
'dakar': ("Île de Gorée, surf et scène musicale — la porte de l'Afrique de l'Ouest.",
          "Gorée Island, surfing and music scene — the gateway to West Africa."),
'madagascar': ("Lémuriens, baobabs et récifs coralliens — biodiversité unique au monde.",
               "Lemurs, baobabs and coral reefs — unique biodiversity in the world."),
'nosybe': ("Île aux parfums — plages, baleines à bosse et ylang-ylang.",
           "Island of perfumes — beaches, humpback whales and ylang-ylang."),
'cap-vert': ("Archipel volcanique entre Afrique et Atlantique — musique, plages et randonnée.",
             "Volcanic archipelago between Africa and Atlantic — music, beaches and hiking."),

# ── TUNISIE ──
'djerba': ("Île de Djerba — synagogue de la Ghriba, plages et architecture blanche.",
           "Djerba Island — Ghriba synagogue, beaches and white architecture."),
'tunis': ("Médina UNESCO, Carthage et musée du Bardo — civilisations superposées.",
          "UNESCO medina, Carthage and Bardo museum — layered civilisations."),
'hammamet': ("Station balnéaire tunisienne — plages de sable, jasmin et golf.",
             "Tunisian beach resort — sandy beaches, jasmine and golf."),

# ── MAROC ──
'essaouira': ("Port de pêche, alizés et medina bleu-blanc — le Maroc bohème face à l'Atlantique.",
              "Fishing port, trade winds and blue-white medina — bohemian Morocco facing the Atlantic."),
'fes': ("Plus grande médina du monde, tanneries et artisanat — le Maroc médiéval vivant.",
        "World's largest medina, tanneries and craftsmanship — living medieval Morocco."),
'chefchaouen': ("Ville bleue du Rif — ruelles peintes, montagnes et fromage de chèvre.",
                "Blue city of the Rif — painted alleys, mountains and goat cheese."),
'ouarzazate': ("Porte du désert — kasbahs, studios de cinéma et route des mille kasbahs.",
               "Gateway to the desert — kasbahs, film studios and the road of a thousand kasbahs."),

# ── AMÉRIQUES ──
'chicago': ("Architecture spectaculaire, deep-dish pizza et blues — la ville du vent sur le lac Michigan.",
            "Spectacular architecture, deep-dish pizza and blues — the Windy City on Lake Michigan."),
'las-vegas': ("Casinos, shows et désert — une oasis artificielle dans le Nevada.",
              "Casinos, shows and desert — an artificial oasis in Nevada."),
'san-francisco': ("Golden Gate, cable cars et quartiers excentriques — brouillard et créativité.",
                  "Golden Gate, cable cars and eccentric neighbourhoods — fog and creativity."),
'boston': ("Berceau de la révolution américaine — universités, fruits de mer et Freedom Trail.",
          "Cradle of the American Revolution — universities, seafood and the Freedom Trail."),
'washington': ("Monuments, musées Smithsonian et cerisiers en fleurs — la capitale du monde libre.",
               "Monuments, Smithsonian museums and cherry blossoms — capital of the free world."),
'seattle': ("Café, tech et nature — Pike Place Market, mont Rainier et scène musicale.",
            "Coffee, tech and nature — Pike Place Market, Mount Rainier and music scene."),
'key-west': ("Bout des Keys — couchers de soleil à Mallory Square, Hemingway et conch fritters.",
             "End of the Keys — Mallory Square sunsets, Hemingway and conch fritters."),
'orlando': ("Parcs à thèmes, Disney World et Universal — la capitale mondiale du divertissement.",
            "Theme parks, Disney World and Universal — the world entertainment capital."),
'nouvelle-orleans': ("Jazz, Mardi Gras et cuisine cajun — la ville la plus musicale d'Amérique.",
                     "Jazz, Mardi Gras and Cajun cuisine — America's most musical city."),
'montreal': ("Vieux-Port, festivals et poutine — la métropole francophone d'Amérique du Nord.",
             "Old Port, festivals and poutine — North America's francophone metropolis."),
'quebec-ville': ("Château Frontenac, rues pavées et hiver féérique — l'Europe en Amérique.",
                 "Château Frontenac, cobbled streets and fairytale winter — Europe in America."),
'toronto': ("CN Tower, quartiers multiculturels et îles de Toronto — le Canada cosmopolite.",
            "CN Tower, multicultural neighbourhoods and Toronto Islands — cosmopolitan Canada."),
'vancouver': ("Montagnes, océan et Stanley Park — la ville la plus nature du Canada.",
              "Mountains, ocean and Stanley Park — Canada's most nature-oriented city."),
'cancun': ("Ruines mayas, cénotes et plages de sable blanc — le Mexique balnéaire tout-inclus.",
           "Mayan ruins, cenotes and white sand beaches — all-inclusive beach Mexico."),
'playa-del-carmen': ("Cinquième Avenue, plongée à Cozumel et cénotes — la Riviera Maya animée.",
                     "Fifth Avenue, Cozumel diving and cenotes — the lively Riviera Maya."),
'cabo-san-lucas': ("Arche rocheuse, observation de baleines et désert — le Mexique Pacifique.",
                   "Rocky arch, whale watching and desert — Pacific Mexico."),
'mexico': ("Mégapole culturelle — pyramides, musées, tacos et Frida Kahlo.",
           "Cultural megacity — pyramids, museums, tacos and Frida Kahlo."),
'oaxaca': ("Mole, mezcal et artisanat zapotèque — le Mexique authentique du sud.",
           "Mole, mezcal and Zapotec craftsmanship — authentic southern Mexico."),
'puerto-vallarta': ("Malecón, plages du Pacifique et Sierra Madre — le charme mexicain côté ouest.",
                    "Malecón, Pacific beaches and Sierra Madre — Mexican charm on the west side."),
'isla-holbox': ("Île sans voiture du Yucatán — bioluminescence, requins-baleines et hamacs.",
                "Car-free Yucatán island — bioluminescence, whale sharks and hammocks."),
'belize': ("Barrière de corail, ruines mayas et jungle — l'Amérique centrale anglophone.",
           "Coral barrier reef, Mayan ruins and jungle — English-speaking Central America."),
'guatemala': ("Antigua, lac Atitlán et Tikal — volcans, culture maya et couleurs.",
              "Antigua, Lake Atitlán and Tikal — volcanoes, Mayan culture and colours."),
'nicaragua': ("Volcans, lacs et surf — l'Amérique centrale encore préservée du tourisme de masse.",
              "Volcanoes, lakes and surfing — Central America still preserved from mass tourism."),
'panama': ("Canal, Bocas del Toro et skyline moderne — le trait d'union des Amériques.",
           "Canal, Bocas del Toro and modern skyline — the link between the Americas."),
'costa-rica': ("Forêts tropicales, volcans et plages deux océans — la pura vida.",
               "Rainforests, volcanoes and two-ocean beaches — the pura vida."),
'colombie': ("Carthagène, Medellín et café — le pays qui se réinvente.",
             "Cartagena, Medellín and coffee — the country reinventing itself."),
'cartagene': ("Murailles coloniales, rues colorées et musique caribéenne.",
              "Colonial walls, colourful streets and Caribbean music."),
'medellin': ("Ville du printemps éternel — innovation, street art et téléphériques urbains.",
             "City of eternal spring — innovation, street art and urban cable cars."),
'bogota': ("Capitale andine — La Candelaria, musée de l'Or et gastronomie émergente.",
           "Andean capital — La Candelaria, Gold Museum and emerging gastronomy."),
'equateur': ("Galápagos, Andes et Amazonie en un seul petit pays.",
             "Galápagos, Andes and Amazon in one small country."),
'galapagos': ("L'archipel de Darwin — tortues géantes, iguanes marins et faune sans peur de l'homme.",
              "Darwin's archipelago — giant tortoises, marine iguanas and fearless wildlife."),
'perou': ("Machu Picchu, ceviche et Amazonie — civilisations précolombiennes et biodiversité extrême.",
          "Machu Picchu, ceviche and Amazon — pre-Columbian civilisations and extreme biodiversity."),
'machu-picchu': ("Cité inca dans les nuages — l'un des sites les plus emblématiques de la planète.",
                 "Inca city in the clouds — one of the planet's most iconic sites."),
'cuzco': ("Ancienne capitale inca à 3 400 m — temples, marché de San Pedro et vallée sacrée.",
          "Former Inca capital at 3,400m — temples, San Pedro market and Sacred Valley."),
'bolivie': ("Salar d'Uyuni, La Paz et lac Titicaca — paysages extrêmes à haute altitude.",
            "Uyuni salt flats, La Paz and Lake Titicaca — extreme landscapes at high altitude."),
'chili': ("Du désert d'Atacama à la Patagonie — 4 300 km de contrastes géographiques.",
          "From the Atacama Desert to Patagonia — 4,300km of geographic contrasts."),
'santiago': ("Capitale entre Andes et Pacifique — vignobles, marchés et quartier Bellavista.",
             "Capital between Andes and Pacific — vineyards, markets and Bellavista quarter."),
'valparaiso': ("Collines colorées, ascenseurs funiculaires et art de rue — le Montmartre du Pacifique.",
               "Colourful hills, funicular lifts and street art — the Montmartre of the Pacific."),
'patagonie': ("Torres del Paine, glaciers et guanacos — le bout du monde sauvage.",
              "Torres del Paine, glaciers and guanacos — the wild end of the world."),
'uruguay': ("Punta del Este, Colonia del Sacramento et asados — l'Amérique du Sud discrète.",
            "Punta del Este, Colonia del Sacramento and asados — understated South America."),

# ── CARAÏBES ──
'antigua': ("365 plages, une pour chaque jour — l'île la plus ensoleillée des Antilles.",
            "365 beaches, one for each day — the sunniest island in the Caribbean."),
'aruba': ("Happy Island — plages de sable blanc, vent constant et soleil garanti hors cyclones.",
          "Happy Island — white sand beaches, constant wind and guaranteed sunshine outside hurricane belt."),
'bahamas': ("Cochons nageurs, trous bleus et plages roses — 700 îles paradisiaques.",
            "Swimming pigs, blue holes and pink beaches — 700 paradise islands."),
'barbade': ("Plages de sable blanc et eau turquoise — une île des Caraïbes idéale toute l'année.",
            "White sand beaches and turquoise water — a year-round perfect Caribbean island."),
'bermudes': ("Plages roses, maisons pastel et épaves de plongée — à mi-chemin entre USA et Europe.",
             "Pink beaches, pastel houses and dive wrecks — halfway between USA and Europe."),
'curacao': ("Architecture Handelskade, plongée et plages secrètes — les Antilles néerlandaises colorées.",
            "Handelskade architecture, diving and secret beaches — colourful Dutch Antilles."),
'republique-dominicaine': ("Plages de Punta Cana, forêt tropicale et merengue — les Caraïbes accessibles.",
                           "Punta Cana beaches, tropical forest and merengue — accessible Caribbean."),
'punta-cana': ("30 km de plages de cocotiers, resorts tout-inclus et excursions en catamaran.",
               "30km of coconut palm beaches, all-inclusive resorts and catamaran trips."),
'saint-lucie': ("Pitons volcaniques, sources chaudes et plages de sable noir — les Caraïbes sauvages.",
                "Volcanic Pitons, hot springs and black sand beaches — the wild Caribbean."),
'trinite-et-tobago': ("Carnaval de Trinidad, récifs de Tobago et forêt tropicale — deux îles, deux mondes.",
                      "Trinidad carnival, Tobago reefs and tropical forest — two islands, two worlds."),
'porto-rico': ("Vieux San Juan, bioluminescence et forêt tropicale El Yunque — les Caraïbes américaines.",
               "Old San Juan, bioluminescence and El Yunque rainforest — American Caribbean."),

# ── OCÉANIE ──
'sydney': ("Opéra, Harbour Bridge et plages de Bondi — l'icône australienne.",
           "Opera House, Harbour Bridge and Bondi Beach — the Australian icon."),
'melbourne': ("Street art, café culture et sport — la ville la plus vivante d'Australie.",
              "Street art, café culture and sport — Australia's most vibrant city."),
'cairns': ("Porte de la Grande Barrière de corail et forêt tropicale de Daintree.",
           "Gateway to the Great Barrier Reef and Daintree rainforest."),
'gold-coast': ("40 km de plage, surf et parcs à thèmes — le Florida australien.",
               "40km of beach, surfing and theme parks — Australia's Florida."),
'perth': ("Ville la plus isolée du monde — plages, vignobles de la Swan Valley et quokkas de Rottnest.",
          "World's most isolated city — beaches, Swan Valley vineyards and Rottnest quokkas."),
'fidji': ("333 îles tropicales — récifs coralliens, villages traditionnels et hospitalité Bula.",
          "333 tropical islands — coral reefs, traditional villages and Bula hospitality."),
'nouvelle-zelande': ("Montagnes, fjords et Terre du Milieu — aventure et nature à chaque tournant.",
                     "Mountains, fjords and Middle-earth — adventure and nature at every turn."),
'yellowstone': ("Premier parc national du monde — geysers, bisons et sources chaudes multicolores.",
                "World's first national park — geysers, bison and multicoloured hot springs."),

# ── IRLANDE ──
'wild-atlantic-way': ("2 500 km de côte sauvage — falaises de Moher, pubs et paysages de bout du monde.",
                      "2,500km of wild coast — Cliffs of Moher, pubs and edge-of-the-world landscapes."),

# ── MALTE ──
'gozo': ("Sœur tranquille de Malte — temples mégalithiques, plongée et paysages agricoles.",
         "Malta's quiet sister — megalithic temples, diving and agricultural landscapes."),
'chypre': ("Aphrodite, plages et vignobles de Troodos — carrefour gréco-turc en Méditerranée.",
           "Aphrodite, beaches and Troodos vineyards — Greco-Turkish crossroads in the Mediterranean."),
'paphos': ("Parc archéologique UNESCO, plage de corail et mosaïques romaines.",
           "UNESCO archaeological park, coral beach and Roman mosaics."),

# ── RESTE ──
'rodrigues': ("Île créole préservée — lagon émeraude, randonnée et simplicité.",
              "Preserved Creole island — emerald lagoon, hiking and simplicity."),
'albanie': ("Riviera albanaise, Butrint UNESCO et Berat — le secret le mieux gardé des Balkans.",
            "Albanian Riviera, Butrint UNESCO and Berat — the Balkans' best-kept secret."),
'gdansk': ("Ambre, chantiers navals de Solidarność et vieille ville hanséatique reconstruite.",
           "Amber, Solidarity shipyards and rebuilt Hanseatic old town."),
}


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CARDS: {slug: [(icon, titre_fr, texte_fr, titre_en, texte_en), ...]}
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CARDS = {
# ── GRÈCE ──
'athenes': [
    ('🏛️', 'Archéologie', 'Avril-mai ou octobre — Acropole, Agora antique, musée national sans la foule.', 'Archaeology', 'April-May or October — Acropolis, Ancient Agora, National Museum without the crowds.'),
    ('🍽️', 'Gastronomie', 'Toute l\'année — souvlaki, tavernes de Plaka, marché central.', 'Gastronomy', 'Year-round — souvlaki, Plaka tavernas, central market.'),
    ('🏖️', 'Plage', 'Juin-septembre — Riviera athénienne à 30 min (Vouliagmeni, Glyfada).', 'Beach', 'June-September — Athenian Riviera 30 min away (Vouliagmeni, Glyfada).'),
    ('👨‍👩‍👧', 'Famille', 'Avril-juin — températures douces, sites accessibles, Jardins nationaux.', 'Family', 'April-June — mild temperatures, accessible sites, National Gardens.'),
],
'zakynthos': [
    ('🏖️', 'Plage & Navagio', 'Juin-septembre — plage du Naufrage accessible en bateau, Gerakas pour les tortues.', 'Beach & Navagio', 'June-September — Shipwreck Beach by boat, Gerakas for turtles.'),
    ('🐢', 'Tortues Caretta', 'Juin-août — nidification à Laganas, observation respectueuse.', 'Caretta Turtles', 'June-August — nesting at Laganas, respectful observation.'),
    ('🤿', 'Plongée', 'Mai-octobre — grottes sous-marines, épave de Navagio vue d\'en bas.', 'Diving', 'May-October — underwater caves, Navagio wreck from below.'),
    ('🚤', 'Tour de l\'île', 'Juin-septembre — Blue Caves, Keri Caves et criques secrètes en bateau.', 'Island Tour', 'June-September — Blue Caves, Keri Caves and secret coves by boat.'),
],
'naxos': [
    ('🏖️', 'Plage', 'Juin-septembre — Agios Prokopios, Plaka, 4 km de sable.', 'Beach', 'June-September — Agios Prokopios, Plaka, 4km of sand.'),
    ('🏛️', 'Archéologie', 'Avril-octobre — Portara, temple de Déméter, villages vénitiens.', 'Archaeology', 'April-October — Portara, Temple of Demeter, Venetian villages.'),
    ('🥾', 'Randonnée', 'Mars-mai ou octobre — mont Zeus (1004m), vallées intérieures.', 'Hiking', 'March-May or October — Mount Zeus (1004m), inland valleys.'),
    ('🧀', 'Gastronomie locale', 'Toute l\'année — fromage Graviera, pommes de terre Naxos, Kitron.', 'Local Food', 'Year-round — Graviera cheese, Naxos potatoes, Kitron liqueur.'),
],
'paros': [
    ('🏖️', 'Plage', 'Juin-septembre — Kolymbithres, Santa Maria, Golden Beach.', 'Beach', 'June-September — Kolymbithres, Santa Maria, Golden Beach.'),
    ('🏄', 'Windsurf & kitesurf', 'Juillet-août — Golden Beach, Meltemi régulier, spots de classe mondiale.', 'Windsurf & Kitesurf', 'July-August — Golden Beach, regular Meltemi, world-class spots.'),
    ('🏘️', 'Villages', 'Avril-octobre — Naoussa, Lefkes, Parikia et ruelles blanches.', 'Villages', 'April-October — Naoussa, Lefkes, Parikia and whitewashed alleys.'),
    ('🍷', 'Vin & gastronomie', 'Toute l\'année — vignobles locaux, poisson grillé, fromage Paros.', 'Wine & Food', 'Year-round — local vineyards, grilled fish, Paros cheese.'),
],
'kefalonia': [
    ('🏖️', 'Plage', 'Juin-septembre — Myrtos, Antisamos, Makris Gialos.', 'Beach', 'June-September — Myrtos, Antisamos, Makris Gialos.'),
    ('🕳️', 'Grottes', 'Mai-octobre — lac souterrain de Melissani, grotte de Drogarati.', 'Caves', 'May-October — Melissani underground lake, Drogarati cave.'),
    ('🚢', 'Excursion Ithaque', 'Juin-septembre — île d\'Ulysse à 30 min en bateau.', 'Ithaca Trip', 'June-September — Odysseus\' island 30 min by boat.'),
    ('🍷', 'Vin Robola', 'Août-octobre — vendanges, cépage unique Robola, vignobles de montagne.', 'Robola Wine', 'August-October — harvest, unique Robola grape, mountain vineyards.'),
],
'kos': [
    ('🏖️', 'Plage', 'Juin-septembre — Paradise Beach, Tigaki, Kardamena.', 'Beach', 'June-September — Paradise Beach, Tigaki, Kardamena.'),
    ('♨️', 'Sources thermales', 'Toute l\'année — Embros Therme, bains naturels en bord de mer.', 'Hot Springs', 'Year-round — Embros Therme, natural seaside baths.'),
    ('🚲', 'Vélo', 'Avril-juin ou septembre-octobre — île plate, réseau cyclable, villages intérieurs.', 'Cycling', 'April-June or September-October — flat island, cycle network, inland villages.'),
    ('🏛️', 'Hippocrate', 'Avril-octobre — Asklepion, platane d\'Hippocrate, château des Chevaliers.', 'Hippocrates', 'April-October — Asklepion, Hippocrates\' plane tree, Knights\' Castle.'),
],
'lefkada': [
    ('🏖️', 'Plage', 'Juin-septembre — Porto Katsiki, Egremni, Kathisma.', 'Beach', 'June-September — Porto Katsiki, Egremni, Kathisma.'),
    ('🏄', 'Kitesurf', 'Juin-août — Vassiliki, l\'un des meilleurs spots d\'Europe.', 'Kitesurfing', 'June-August — Vassiliki, one of Europe\'s best spots.'),
    ('🚤', 'Excursion îles', 'Juin-septembre — Meganisi, Skorpios (île d\'Onassis) en bateau.', 'Island Trips', 'June-September — Meganisi, Skorpios (Onassis\' island) by boat.'),
    ('🥾', 'Randonnée', 'Avril-mai ou octobre — sentiers côtiers, cascades de Dimosari.', 'Hiking', 'April-May or October — coastal trails, Dimosari waterfalls.'),
],
'thessalonique': [
    ('🏛️', 'Histoire', 'Toute l\'année — Tour Blanche, Arc de Galère, musée archéologique.', 'History', 'Year-round — White Tower, Arch of Galerius, archaeological museum.'),
    ('🍽️', 'Gastronomie', 'Toute l\'année — marchés Modiano et Kapani, bougatsa, meze du port.', 'Gastronomy', 'Year-round — Modiano and Kapani markets, bougatsa, port meze.'),
    ('🎉', 'Vie nocturne', 'Toute l\'année — Ladadika, bars sur les toits, scène musicale.', 'Nightlife', 'Year-round — Ladadika, rooftop bars, music scene.'),
    ('👨‍👩‍👧', 'Famille', 'Mai-juin ou septembre — front de mer, parc Nea Paralia, musée des Sciences.', 'Family', 'May-June or September — waterfront, Nea Paralia park, Science Museum.'),
],
'hydra': [
    ('🚶', 'Randonnée', 'Mars-mai ou octobre — sentiers côtiers vers Vlychos et Bisti.', 'Hiking', 'March-May or October — coastal trails to Vlychos and Bisti.'),
    ('🎨', 'Art & culture', 'Juin-septembre — galeries, école des Beaux-Arts, musée historique.', 'Art & Culture', 'June-September — galleries, School of Fine Arts, historical museum.'),
    ('🏊', 'Baignade', 'Juin-septembre — rochers de Spilia, Kaminia, eaux cristallines.', 'Swimming', 'June-September — Spilia rocks, Kaminia, crystal-clear waters.'),
    ('⛵', 'Excursion bateau', 'Mai-octobre — tour de l\'île, plages accessibles uniquement par mer.', 'Boat Trip', 'May-October — island tour, beaches accessible only by sea.'),
],
'milos': [
    ('🏖️', 'Plages volcaniques', 'Juin-septembre — Sarakiniko, Firiplaka, Tsigrado, Kleftiko.', 'Volcanic Beaches', 'June-September — Sarakiniko, Firiplaka, Tsigrado, Kleftiko.'),
    ('🚤', 'Tour en bateau', 'Juin-septembre — Kleftiko, grottes marines et formations rocheuses.', 'Boat Tour', 'June-September — Kleftiko, sea caves and rock formations.'),
    ('🤿', 'Plongée', 'Mai-octobre — eaux cristallines, épaves et fonds volcaniques.', 'Diving', 'May-October — crystal-clear waters, wrecks and volcanic seabeds.'),
    ('🏘️', 'Villages', 'Avril-octobre — Plaka, Tripiti, catacombes et théâtre antique.', 'Villages', 'April-October — Plaka, Tripiti, catacombs and ancient theatre.'),
],

# ── ITALIE ──
'milan': [
    ('🎨', 'Art & design', 'Toute l\'année — La Cène, Pinacothèque de Brera, Fondation Prada.', 'Art & Design', 'Year-round — The Last Supper, Brera Gallery, Prada Foundation.'),
    ('🛍️', 'Shopping', 'Janvier ou juillet — soldes, Quadrilatère de la mode, Galleria Vittorio Emanuele.', 'Shopping', 'January or July — sales, Fashion Quadrilateral, Galleria Vittorio Emanuele.'),
    ('🍽️', 'Gastronomie', 'Toute l\'année — risotto alla milanese, ossobuco, Navigli.', 'Gastronomy', 'Year-round — risotto alla milanese, ossobuco, Navigli.'),
    ('⚽', 'Football', 'Septembre-mai — San Siro, derby Inter-Milan.', 'Football', 'September-May — San Siro, Inter-Milan derby.'),
],
'naples': [
    ('🍕', 'Pizza', 'Toute l\'année — berceau de la pizza, Sorbillo, Da Michele, Starita.', 'Pizza', 'Year-round — birthplace of pizza, Sorbillo, Da Michele, Starita.'),
    ('🏛️', 'Pompéi & Herculanum', 'Mars-mai ou octobre — ruines sans la chaleur écrasante de l\'été.', 'Pompeii & Herculaneum', 'March-May or October — ruins without the crushing summer heat.'),
    ('🌋', 'Vésuve', 'Avril-octobre — ascension du cratère, vue sur la baie de Naples.', 'Vesuvius', 'April-October — crater ascent, view over the Bay of Naples.'),
    ('🏖️', 'Côte & îles', 'Juin-septembre — Capri, Ischia, Procida depuis le port de Naples.', 'Coast & Islands', 'June-September — Capri, Ischia, Procida from Naples port.'),
],
'lac-come': [
    ('🚢', 'Croisière', 'Mai-septembre — ferry entre Bellagio, Varenna et Menaggio.', 'Cruise', 'May-September — ferry between Bellagio, Varenna and Menaggio.'),
    ('🏡', 'Villas & jardins', 'Avril-octobre — Villa Carlotta, Villa del Balbianello, Villa Melzi.', 'Villas & Gardens', 'April-October — Villa Carlotta, Villa del Balbianello, Villa Melzi.'),
    ('🥾', 'Randonnée', 'Mai-juin ou septembre — Greenway del Lago, sentier de Brunate.', 'Hiking', 'May-June or September — Greenway del Lago, Brunate trail.'),
    ('🍽️', 'Gastronomie', 'Toute l\'année — missoltino, polenta, restaurants étoilés.', 'Gastronomy', 'Year-round — missoltino, polenta, Michelin-starred restaurants.'),
],
'lac-garde': [
    ('⛵', 'Voile & sports nautiques', 'Juin-septembre — vent du Pelèr régulier, kitesurf à Torbole.', 'Sailing & Water Sports', 'June-September — regular Pelèr wind, kitesurfing at Torbole.'),
    ('🏖️', 'Plage', 'Juin-août — Sirmione, Bardolino, plages de galets et sable.', 'Beach', 'June-August — Sirmione, Bardolino, pebble and sand beaches.'),
    ('🏰', 'Châteaux', 'Avril-octobre — Scaliger de Sirmione, Malcesine, villages fortifiés.', 'Castles', 'April-October — Sirmione Scaliger, Malcesine, fortified villages.'),
    ('🍷', 'Vin', 'Septembre-octobre — vendanges Bardolino, Lugana, Valpolicella à proximité.', 'Wine', 'September-October — Bardolino harvest, Lugana, nearby Valpolicella.'),
    ('👨‍👩‍👧', 'Famille', 'Juin-août — Gardaland, plages sécurisées, vélo sur piste cyclable.', 'Family', 'June-August — Gardaland, safe beaches, cycling on bike paths.'),
],
'cinque-terre': [
    ('🥾', 'Sentiero Azzurro', 'Avril-mai ou septembre-octobre — sentier côtier entre les 5 villages.', 'Blue Trail', 'April-May or September-October — coastal path between the 5 villages.'),
    ('🏖️', 'Baignade', 'Juin-septembre — plages de Monterosso, rochers de Riomaggiore.', 'Swimming', 'June-September — Monterosso beaches, Riomaggiore rocks.'),
    ('🍷', 'Vin & pesto', 'Toute l\'année — Sciacchetrà, pesto de Ligurie, focaccia.', 'Wine & Pesto', 'Year-round — Sciacchetrà, Ligurian pesto, focaccia.'),
    ('📸', 'Photographie', 'Septembre-octobre — lumière dorée, villages sans foule.', 'Photography', 'September-October — golden light, villages without crowds.'),
],
'bologne': [
    ('🍝', 'Gastronomie', 'Toute l\'année — tortellini, mortadelle, ragù, marché del Quadrilatero.', 'Food', 'Year-round — tortellini, mortadella, ragù, Quadrilatero market.'),
    ('🏛️', 'Architecture', 'Avril-juin — 40 km de portiques UNESCO, Due Torri, piazza Maggiore.', 'Architecture', 'April-June — 40km of UNESCO porticoes, Due Torri, Piazza Maggiore.'),
    ('🎓', 'Université', 'Toute l\'année — plus ancienne université du monde (1088), Archiginnasio.', 'University', 'Year-round — world\'s oldest university (1088), Archiginnasio.'),
    ('🏎️', 'Motor Valley', 'Toute l\'année — Ferrari, Lamborghini, Ducati à 30 min.', 'Motor Valley', 'Year-round — Ferrari, Lamborghini, Ducati 30 min away.'),
],
'pouilles': [
    ('🏠', 'Trulli d\'Alberobello', 'Avril-juin ou septembre — UNESCO sans la chaleur, lumière parfaite.', 'Alberobello Trulli', 'April-June or September — UNESCO without the heat, perfect light.'),
    ('🏖️', 'Plage', 'Juin-septembre — Polignano a Mare, Porto Cesareo, côte du Salento.', 'Beach', 'June-September — Polignano a Mare, Porto Cesareo, Salento coast.'),
    ('🍽️', 'Gastronomie', 'Toute l\'année — orecchiette, burrata, huile d\'olive, vin Primitivo.', 'Gastronomy', 'Year-round — orecchiette, burrata, olive oil, Primitivo wine.'),
    ('🚲', 'Vélo', 'Mars-mai ou octobre — plaines du Salento, masseries, oliveraies.', 'Cycling', 'March-May or October — Salento plains, masserie, olive groves.'),
],
'palerme': [
    ('🍽️', 'Street food', 'Toute l\'année — arancini, panelle, sfincione, marchés de Ballarò et Vucciria.', 'Street Food', 'Year-round — arancini, panelle, sfincione, Ballarò and Vucciria markets.'),
    ('🏛️', 'Architecture arabe-normande', 'Mars-mai ou octobre — cathédrale, Cappella Palatina, Monreale.', 'Arab-Norman Architecture', 'March-May or October — cathedral, Cappella Palatina, Monreale.'),
    ('🏖️', 'Plage', 'Juin-septembre — Mondello à 20 min, Cefalù à 1 h.', 'Beach', 'June-September — Mondello 20 min away, Cefalù 1h away.'),
    ('🎭', 'Culture', 'Toute l\'année — Teatro Massimo, Quattro Canti, fêtes religieuses.', 'Culture', 'Year-round — Teatro Massimo, Quattro Canti, religious festivals.'),
],
'turin': [
    ('🍫', 'Chocolat & café', 'Toute l\'année — gianduja, bicerin, cafés historiques.', 'Chocolate & Coffee', 'Year-round — gianduja, bicerin, historic cafés.'),
    ('🏛️', 'Musées', 'Toute l\'année — Musée égyptien (2e mondial), Mole Antonelliana, cinéma.', 'Museums', 'Year-round — Egyptian Museum (2nd worldwide), Mole Antonelliana, cinema.'),
    ('⛷️', 'Ski', 'Décembre-mars — Via Lattea, Bardonecchia à 1 h.', 'Skiing', 'December-March — Via Lattea, Bardonecchia 1h away.'),
    ('🍷', 'Vin & gastronomie', 'Septembre-novembre — vendanges Barolo, truffes d\'Alba.', 'Wine & Food', 'September-November — Barolo harvest, Alba truffles.'),
],
'verone': [
    ('🎶', 'Opéra', 'Juin-août — saison lyrique aux arènes, spectacles en plein air.', 'Opera', 'June-August — opera season at the Arena, open-air performances.'),
    ('🏛️', 'Histoire', 'Avril-octobre — arènes romaines, piazza delle Erbe, Castelvecchio.', 'History', 'April-October — Roman arena, Piazza delle Erbe, Castelvecchio.'),
    ('🍷', 'Vin', 'Septembre-octobre — Valpolicella, Amarone, Soave à 30 min.', 'Wine', 'September-October — Valpolicella, Amarone, Soave 30 min away.'),
    ('❤️', 'Romantique', 'Toute l\'année — maison de Juliette, balades au bord de l\'Adige.', 'Romantic', 'Year-round — Juliet\'s house, walks along the Adige.'),
],
'dolomites': [
    ('⛷️', 'Ski', 'Décembre-mars — Cortina, Val Gardena, Alta Badia, Sellaronda.', 'Skiing', 'December-March — Cortina, Val Gardena, Alta Badia, Sellaronda.'),
    ('🥾', 'Randonnée', 'Juin-septembre — Tre Cime di Lavaredo, Alta Via 1, refuges.', 'Hiking', 'June-September — Tre Cime di Lavaredo, Alta Via 1, mountain huts.'),
    ('🚴', 'Vélo de route', 'Juin-septembre — cols mythiques, Stelvio et Giau à proximité.', 'Road Cycling', 'June-September — legendary passes, Stelvio and Giau nearby.'),
    ('📸', 'Photographie', 'Septembre-octobre — mélèzes dorés, lumière alpine, Alpe di Siusi.', 'Photography', 'September-October — golden larches, alpine light, Alpe di Siusi.'),
],
}

# I'll continue adding more cards in the next section — this file is getting large
# For now let's handle the remaining destinations with a template-based approach

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# REMAINING CARDS — Batch 2
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# ── ESPAGNE suite ──
'madrid': [
    ('🏛️', 'Musées', 'Toute l\'année — Prado, Reina Sofía, Thyssen-Bornemisza, triangle d\'or.', 'Museums', 'Year-round — Prado, Reina Sofía, Thyssen-Bornemisza, golden triangle.'),
    ('🍽️', 'Tapas & gastronomie', 'Toute l\'année — Mercado de San Miguel, La Latina, terrasses de Malasaña.', 'Tapas & Food', 'Year-round — Mercado de San Miguel, La Latina, Malasaña terraces.'),
    ('⚽', 'Football', 'Septembre-mai — Santiago Bernabéu, Metropolitano.', 'Football', 'September-May — Santiago Bernabéu, Metropolitano.'),
    ('🌙', 'Vie nocturne', 'Toute l\'année — Chueca, Malasaña, dîner à 22h, sortir à minuit.', 'Nightlife', 'Year-round — Chueca, Malasaña, dinner at 10pm, going out at midnight.'),
],
'grenade': [
    ('🏰', 'Alhambra', 'Mars-mai ou octobre — réserver 2 mois avant, lumière dorée sans la chaleur.', 'Alhambra', 'March-May or October — book 2 months ahead, golden light without the heat.'),
    ('🏘️', 'Albaicín', 'Toute l\'année — ruelles arabes, miradors et tapas gratuites.', 'Albaicín', 'Year-round — Arab alleys, viewpoints and free tapas.'),
    ('⛷️', 'Sierra Nevada', 'Décembre-mars — ski à 30 min de la ville, ski et plage le même jour.', 'Sierra Nevada', 'December-March — skiing 30 min from the city, ski and beach same day.'),
    ('🎸', 'Flamenco', 'Toute l\'année — Sacromonte, cuevas, spectacles intimes.', 'Flamenco', 'Year-round — Sacromonte, cave shows, intimate performances.'),
],
'cordoue': [
    ('🕌', 'Mosquée-cathédrale', 'Mars-mai ou octobre — chef-d\'œuvre unique sans la canicule estivale.', 'Mosque-Cathedral', 'March-May or October — unique masterpiece without summer heat.'),
    ('🌸', 'Patios', 'Mai — festival des patios de Cordoue, classé UNESCO.', 'Patios', 'May — Córdoba Patio Festival, UNESCO listed.'),
    ('🏘️', 'Judería', 'Toute l\'année — quartier juif médiéval, Alcázar, pont romain.', 'Judería', 'Year-round — medieval Jewish quarter, Alcázar, Roman bridge.'),
    ('🍽️', 'Gastronomie', 'Toute l\'année — salmorejo, flamenquín, vins de Montilla-Moriles.', 'Gastronomy', 'Year-round — salmorejo, flamenquín, Montilla-Moriles wines.'),
],
'cadix': [
    ('🏖️', 'Plage', 'Juin-septembre — Playa de la Victoria, Bolonia, Tarifa.', 'Beach', 'June-September — Playa de la Victoria, Bolonia, Tarifa.'),
    ('🏄', 'Surf & kitesurf', 'Toute l\'année — Tarifa, vent du Levante, capitale du kite en Europe.', 'Surf & Kitesurf', 'Year-round — Tarifa, Levante wind, Europe\'s kite capital.'),
    ('🎭', 'Carnaval', 'Février-mars — l\'un des plus grands carnavals d\'Espagne.', 'Carnival', 'February-March — one of Spain\'s largest carnivals.'),
    ('🍽️', 'Gastronomie maritime', 'Toute l\'année — fritures de poisson, atún rojo de Barbate.', 'Seafood', 'Year-round — fried fish, Barbate red tuna.'),
],
'costa-brava': [
    ('🏖️', 'Plage & criques', 'Juin-septembre — Tossa de Mar, Calella de Palafrugell, Sa Tuna.', 'Beach & Coves', 'June-September — Tossa de Mar, Calella de Palafrugell, Sa Tuna.'),
    ('🎨', 'Dalí', 'Avril-octobre — musée de Figueres, maison de Portlligat, château de Púbol.', 'Dalí', 'April-October — Figueres museum, Portlligat house, Púbol castle.'),
    ('🤿', 'Plongée', 'Mai-octobre — Îles Medes, réserve marine protégée.', 'Diving', 'May-October — Medes Islands, protected marine reserve.'),
    ('🥾', 'Camí de Ronda', 'Avril-juin ou septembre — sentier côtier historique entre criques.', 'Camí de Ronda', 'April-June or September — historic coastal path between coves.'),
],
'saint-sebastien': [
    ('🍽️', 'Gastronomie', 'Toute l\'année — pintxos de la Parte Vieja, plus haute densité d\'étoiles Michelin au monde.', 'Gastronomy', 'Year-round — Parte Vieja pintxos, highest Michelin star density in the world.'),
    ('🏖️', 'Plage', 'Juin-septembre — La Concha, Ondarreta, eau à 20-22°C.', 'Beach', 'June-September — La Concha, Ondarreta, water at 20-22°C.'),
    ('🏄', 'Surf', 'Toute l\'année — Zurriola, vagues régulières, compétitions internationales.', 'Surfing', 'Year-round — Zurriola, regular waves, international competitions.'),
    ('🎬', 'Festival du film', 'Septembre — Festival International du Film de San Sebastián.', 'Film Festival', 'September — San Sebastián International Film Festival.'),
],
'bilbao': [
    ('🏛️', 'Guggenheim', 'Toute l\'année — architecture Gehry, collections contemporaines.', 'Guggenheim', 'Year-round — Gehry architecture, contemporary collections.'),
    ('🍽️', 'Pintxos', 'Toute l\'année — Casco Viejo, Plaza Nueva, gastronomie basque.', 'Pintxos', 'Year-round — Casco Viejo, Plaza Nueva, Basque cuisine.'),
    ('🥾', 'Nature', 'Mai-septembre — San Juan de Gaztelugatxe, côte basque, verdure.', 'Nature', 'May-September — San Juan de Gaztelugatxe, Basque coast, greenery.'),
    ('🏙️', 'Architecture', 'Toute l\'année — Zubizuri, Azkuna Zentroa, reconversion urbaine.', 'Architecture', 'Year-round — Zubizuri, Azkuna Zentroa, urban regeneration.'),
],
'formentera': [
    ('🏖️', 'Plage', 'Juin-septembre — Ses Illetes, Platja de Migjorn, eaux caribéennes.', 'Beach', 'June-September — Ses Illetes, Platja de Migjorn, Caribbean-like waters.'),
    ('🚲', 'Vélo', 'Mai-octobre — île plate, 32 km de bout en bout, pistes cyclables.', 'Cycling', 'May-October — flat island, 32km end to end, bike paths.'),
    ('🤿', 'Snorkeling', 'Juin-septembre — herbiers de posidonie, eaux cristallines.', 'Snorkelling', 'June-September — posidonia meadows, crystal-clear waters.'),
    ('🌅', 'Détente', 'Mai-juin ou septembre — ambiance bohème, loin de la foule d\'Ibiza.', 'Relaxation', 'May-June or September — bohemian vibe, away from Ibiza crowds.'),
],
'la-gomera': [
    ('🥾', 'Randonnée Garajonay', 'Toute l\'année — forêt de laurisylve UNESCO, sentiers balisés.', 'Garajonay Hiking', 'Year-round — UNESCO laurel forest, marked trails.'),
    ('🗣️', 'Silbo Gomero', 'Toute l\'année — langage sifflé unique, démonstrations dans les restaurants.', 'Silbo Gomero', 'Year-round — unique whistled language, demonstrations in restaurants.'),
    ('🐬', 'Observation cétacés', 'Toute l\'année — dauphins et baleines pilotes depuis Valle Gran Rey.', 'Whale Watching', 'Year-round — dolphins and pilot whales from Valle Gran Rey.'),
    ('🌿', 'Nature', 'Mars-mai — floraison, vallées verdoyantes, terrasses agricoles.', 'Nature', 'March-May — blooming season, green valleys, agricultural terraces.'),
],
'la-palma': [
    ('⭐', 'Astronomie', 'Toute l\'année — Observatoire du Roque de los Muchachos, réserve Starlight.', 'Astronomy', 'Year-round — Roque de los Muchachos Observatory, Starlight reserve.'),
    ('🌋', 'Volcans', 'Toute l\'année — Caldera de Taburiente, volcan Tajogaite (2021).', 'Volcanoes', 'Year-round — Caldera de Taburiente, Tajogaite volcano (2021).'),
    ('🥾', 'Randonnée', 'Mars-juin ou octobre — GR-130, forêts de pins, sentiers volcaniques.', 'Hiking', 'March-June or October — GR-130, pine forests, volcanic trails.'),
    ('🤿', 'Plongée', 'Mai-octobre — réserve marine, eaux volcaniques claires.', 'Diving', 'May-October — marine reserve, clear volcanic waters.'),
],
'el-hierro': [
    ('🤿', 'Plongée', 'Mai-octobre — réserve marine de La Restinga, eaux volcaniques.', 'Diving', 'May-October — La Restinga marine reserve, volcanic waters.'),
    ('🥾', 'Randonnée', 'Toute l\'année — sentiers à travers genévriers millénaires et paysages lunaires.', 'Hiking', 'Year-round — trails through ancient junipers and lunar landscapes.'),
    ('🌿', 'Écotourisme', 'Toute l\'année — réserve de biosphère, 100% énergies renouvelables.', 'Ecotourism', 'Year-round — biosphere reserve, 100% renewable energy.'),
    ('🌊', 'Piscines naturelles', 'Juin-septembre — Charco Azul, La Maceta, baignade volcanique.', 'Natural Pools', 'June-September — Charco Azul, La Maceta, volcanic bathing.'),
],

# ── PORTUGAL suite ──
'acores': [
    ('🐋', 'Observation baleines', 'Mai-septembre — cachalots, dauphins, baleines bleues.', 'Whale Watching', 'May-September — sperm whales, dolphins, blue whales.'),
    ('🥾', 'Randonnée', 'Avril-octobre — Sete Cidades, Lagoa do Fogo, sentiers volcaniques.', 'Hiking', 'April-October — Sete Cidades, Lagoa do Fogo, volcanic trails.'),
    ('♨️', 'Sources thermales', 'Toute l\'année — Furnas, cozido cuit dans le sol volcanique.', 'Hot Springs', 'Year-round — Furnas, cozido cooked in volcanic soil.'),
    ('🤿', 'Plongée', 'Juin-octobre — Formigas, raies manta, requins bleus.', 'Diving', 'June-October — Formigas, manta rays, blue sharks.'),
],
'faro': [
    ('🦩', 'Ria Formosa', 'Mars-octobre — lagune, flamants, îles désertes accessibles en bateau.', 'Ria Formosa', 'March-October — lagoon, flamingos, desert islands by boat.'),
    ('🏖️', 'Plage', 'Juin-septembre — Ilha Deserta, Praia de Faro, sable blanc.', 'Beach', 'June-September — Ilha Deserta, Praia de Faro, white sand.'),
    ('🏘️', 'Vieille ville', 'Toute l\'année — Cidade Velha fortifiée, cathédrale, os Capela dos Ossos.', 'Old Town', 'Year-round — fortified Cidade Velha, cathedral, Capela dos Ossos.'),
    ('🍽️', 'Gastronomie', 'Toute l\'année — cataplana, fruits de mer, vins de l\'Algarve.', 'Gastronomy', 'Year-round — cataplana, seafood, Algarve wines.'),
],
'sintra': [
    ('🏰', 'Palais', 'Avril-juin ou septembre-octobre — Pena, Quinta da Regaleira, Monserrate sans foule.', 'Palaces', 'April-June or September-October — Pena, Quinta da Regaleira, Monserrate without crowds.'),
    ('🥾', 'Randonnée', 'Mars-juin — Serra de Sintra, chemins forestiers jusqu\'à Cabo da Roca.', 'Hiking', 'March-June — Serra de Sintra, forest paths to Cabo da Roca.'),
    ('🍰', 'Gastronomie', 'Toute l\'année — travesseiros, queijadas, pâtisseries traditionnelles.', 'Pastries', 'Year-round — travesseiros, queijadas, traditional pastries.'),
    ('📸', 'Photographie', 'Septembre-octobre — lumière dorée, brume matinale sur les palais.', 'Photography', 'September-October — golden light, morning mist over palaces.'),
],

# ── FRANCE suite ──
'biarritz': [
    ('🏄', 'Surf', 'Toute l\'année — Côte des Basques, Grande Plage, houle atlantique.', 'Surfing', 'Year-round — Côte des Basques, Grande Plage, Atlantic swell.'),
    ('🏖️', 'Plage', 'Juin-septembre — Port Vieux, plage Marbella, eau à 20-22°C.', 'Beach', 'June-September — Port Vieux, Marbella beach, water at 20-22°C.'),
    ('🍽️', 'Gastronomie basque', 'Toute l\'année — Halles de Biarritz, piment d\'Espelette, gâteau basque.', 'Basque Food', 'Year-round — Biarritz market hall, Espelette pepper, Basque cake.'),
    ('♨️', 'Thalasso', 'Toute l\'année — cure marine, spa océan, tradition Belle Époque.', 'Thalasso', 'Year-round — ocean spa, sea-water therapy, Belle Époque tradition.'),
],
'pays-basque': [
    ('🍽️', 'Gastronomie', 'Toute l\'année — piment d\'Espelette, jambon de Bayonne, fromage Ossau-Iraty.', 'Gastronomy', 'Year-round — Espelette pepper, Bayonne ham, Ossau-Iraty cheese.'),
    ('🏄', 'Surf', 'Toute l\'année — Anglet, Guéthary, Hendaye pour les débutants.', 'Surfing', 'Year-round — Anglet, Guéthary, Hendaye for beginners.'),
    ('🥾', 'Randonnée', 'Mai-octobre — sentier du littoral, La Rhune, gorges de Kakuetta.', 'Hiking', 'May-October — coastal path, La Rhune, Kakuetta gorges.'),
    ('🏘️', 'Villages', 'Toute l\'année — Espelette, Ainhoa, Saint-Jean-Pied-de-Port.', 'Villages', 'Year-round — Espelette, Ainhoa, Saint-Jean-Pied-de-Port.'),
],
'normandie': [
    ('🏰', 'D-Day & histoire', 'Avril-septembre — plages du Débarquement, cimetière américain, Mémorial de Caen.', 'D-Day & History', 'April-September — D-Day beaches, American cemetery, Caen Memorial.'),
    ('🏝️', 'Mont-Saint-Michel', 'Mars-mai ou septembre-octobre — marées spectaculaires, moins de foule.', 'Mont-Saint-Michel', 'March-May or September-October — spectacular tides, fewer crowds.'),
    ('🍎', 'Gastronomie', 'Toute l\'année — Camembert, cidre, calvados, fruits de mer de Honfleur.', 'Gastronomy', 'Year-round — Camembert, cider, calvados, Honfleur seafood.'),
    ('🎨', 'Impressionnisme', 'Mai-septembre — Giverny, Étretat, lumière de Monet.', 'Impressionism', 'May-September — Giverny, Étretat, Monet\'s light.'),
],
'dordogne': [
    ('🏰', 'Châteaux', 'Avril-octobre — Beynac, Castelnaud, Château des Milandes.', 'Castles', 'April-October — Beynac, Castelnaud, Château des Milandes.'),
    ('🎨', 'Grottes préhistoriques', 'Toute l\'année — Lascaux IV, Font-de-Gaume, grotte de Rouffignac.', 'Prehistoric Caves', 'Year-round — Lascaux IV, Font-de-Gaume, Rouffignac cave.'),
    ('🍽️', 'Gastronomie', 'Octobre-février — truffes et foie gras. Toute l\'année — marchés de Sarlat.', 'Gastronomy', 'October-February — truffles and foie gras. Year-round — Sarlat markets.'),
    ('🛶', 'Canoë', 'Juin-septembre — descente de la Dordogne et de la Vézère.', 'Canoeing', 'June-September — Dordogne and Vézère river descents.'),
],
'chamonix': [
    ('⛷️', 'Ski', 'Décembre-avril — Grands Montets, Brévent, Vallée Blanche.', 'Skiing', 'December-April — Grands Montets, Brévent, Vallée Blanche.'),
    ('🥾', 'Randonnée', 'Juin-septembre — Tour du Mont-Blanc, Lac Blanc, Mer de Glace.', 'Hiking', 'June-September — Tour of Mont Blanc, Lac Blanc, Mer de Glace.'),
    ('🚡', 'Aiguille du Midi', 'Mai-octobre — téléphérique à 3842m, vue Mont-Blanc, Pas dans le Vide.', 'Aiguille du Midi', 'May-October — cable car to 3842m, Mont Blanc view, Step into the Void.'),
    ('🧗', 'Alpinisme', 'Juin-août — ascension Mont-Blanc, Via Ferrata, courses en haute montagne.', 'Mountaineering', 'June-August — Mont Blanc ascent, Via Ferrata, high mountain routes.'),
],
'montpellier': [
    ('🏖️', 'Plage', 'Juin-septembre — Palavas, Carnon, Grande-Motte à 15 min.', 'Beach', 'June-September — Palavas, Carnon, La Grande-Motte 15 min away.'),
    ('🏘️', 'Centre historique', 'Toute l\'année — Écusson, Place de la Comédie, arc de triomphe du Peyrou.', 'Historic Centre', 'Year-round — Écusson, Place de la Comédie, Peyrou triumphal arch.'),
    ('🍷', 'Vin', 'Septembre-octobre — Pic Saint-Loup, terrasses du Larzac, vendanges.', 'Wine', 'September-October — Pic Saint-Loup, Larzac terraces, harvest.'),
    ('🎭', 'Festivals', 'Juin-juillet — Festival de Radio France, Festival Arabesques.', 'Festivals', 'June-July — Radio France Festival, Arabesques Festival.'),
],
'strasbourg': [
    ('🎄', 'Marché de Noël', 'Fin novembre-décembre — plus ancien marché de Noël de France (1570).', 'Christmas Market', 'Late November-December — France\'s oldest Christmas market (1570).'),
    ('🏘️', 'Petite France', 'Toute l\'année — maisons à colombages, canaux, cathédrale gothique.', 'Petite France', 'Year-round — half-timbered houses, canals, Gothic cathedral.'),
    ('🍽️', 'Gastronomie alsacienne', 'Toute l\'année — choucroute, flammekueche, Kougelhopf, vins d\'Alsace.', 'Alsatian Cuisine', 'Year-round — sauerkraut, flammekueche, Kougelhopf, Alsace wines.'),
    ('🏛️', 'Institutions européennes', 'Toute l\'année — Parlement européen, Conseil de l\'Europe (visites possibles).', 'European Institutions', 'Year-round — European Parliament, Council of Europe (visits available).'),
],
'guadeloupe': [
    ('🏖️', 'Plage', 'Décembre-avril — Grande-Anse, Sainte-Anne, Marie-Galante.', 'Beach', 'December-April — Grande-Anse, Sainte-Anne, Marie-Galante.'),
    ('🌋', 'Soufrière', 'Décembre-mai — randonnée au sommet (1467m), forêt tropicale.', 'La Soufrière', 'December-May — summit hike (1467m), tropical forest.'),
    ('🤿', 'Plongée', 'Décembre-mai — réserve Cousteau, tortues, coraux.', 'Diving', 'December-May — Cousteau reserve, turtles, corals.'),
    ('🍹', 'Rhum & gastronomie', 'Toute l\'année — distilleries, accras, bokit, colombo.', 'Rum & Food', 'Year-round — distilleries, accras, bokit, colombo.'),
],
'martinique': [
    ('🏖️', 'Plage', 'Décembre-avril — Anse Dufour, Les Salines, plages du sud.', 'Beach', 'December-April — Anse Dufour, Les Salines, southern beaches.'),
    ('🌋', 'Montagne Pelée', 'Décembre-mai — randonnée au sommet, forêt tropicale.', 'Mount Pelée', 'December-May — summit hike, tropical forest.'),
    ('🍹', 'Rhum', 'Toute l\'année — distilleries AOC, rhum agricole, dégustations.', 'Rum', 'Year-round — AOC distilleries, agricultural rum, tastings.'),
    ('⛵', 'Yoles rondes', 'Juillet-août — courses traditionnelles, Tour de la Martinique.', 'Traditional Sailing', 'July-August — traditional races, Tour of Martinique.'),
],
'guyane': [
    ('🚀', 'Centre Spatial', 'Toute l\'année — lancements Ariane depuis Kourou (calendrier ESA).', 'Space Centre', 'Year-round — Ariane launches from Kourou (ESA calendar).'),
    ('🌿', 'Forêt amazonienne', 'Juillet-octobre — saison sèche, excursions en pirogue.', 'Amazon Rainforest', 'July-October — dry season, canoe excursions.'),
    ('🐢', 'Tortues luths', 'Avril-juillet — ponte sur les plages de Rémire-Montjoly.', 'Leatherback Turtles', 'April-July — nesting on Rémire-Montjoly beaches.'),
    ('🎭', 'Carnaval', 'Janvier-mars — Touloulous, le plus long carnaval du monde.', 'Carnival', 'January-March — Touloulous, the world\'s longest carnival.'),
],
'mayotte': [
    ('🐢', 'Tortues marines', 'Toute l\'année — ponte et éclosion sur les plages de N\'Gouja.', 'Sea Turtles', 'Year-round — nesting and hatching on N\'Gouja beaches.'),
    ('🤿', 'Lagon & plongée', 'Mai-novembre — visibilité maximale, raies manta, baleines.', 'Lagoon & Diving', 'May-November — maximum visibility, manta rays, whales.'),
    ('🐋', 'Baleines à bosse', 'Juillet-octobre — observation depuis le lagon, saison de reproduction.', 'Humpback Whales', 'July-October — lagoon observation, breeding season.'),
    ('🌿', 'Randonnée', 'Mai-octobre — mont Choungui, mont Bénara, forêts tropicales.', 'Hiking', 'May-October — Mount Choungui, Mount Bénara, tropical forests.'),
],
'polynesie': [
    ('🏖️', 'Plage & lagon', 'Avril-octobre — Bora Bora, Moorea, Rangiroa, saison sèche.', 'Beach & Lagoon', 'April-October — Bora Bora, Moorea, Rangiroa, dry season.'),
    ('🤿', 'Plongée', 'Toute l\'année — passes de Fakarava, raies manta de Tikehau.', 'Diving', 'Year-round — Fakarava passes, Tikehau manta rays.'),
    ('🐋', 'Baleines à bosse', 'Août-octobre — observation à Moorea et Rurutu.', 'Humpback Whales', 'August-October — observation at Moorea and Rurutu.'),
    ('🏄', 'Surf', 'Mai-septembre — Teahupo\'o, l\'une des vagues les plus puissantes du monde.', 'Surfing', 'May-September — Teahupo\'o, one of the world\'s most powerful waves.'),
],
'nouvelle-caledonie': [
    ('🤿', 'Plongée & snorkeling', 'Septembre-décembre — lagon UNESCO, récif-barrière, dugongs.', 'Diving & Snorkelling', 'September-December — UNESCO lagoon, barrier reef, dugongs.'),
    ('🏖️', 'Plage', 'Septembre-décembre — Île des Pins, Ouvéa, plages de sable blanc.', 'Beach', 'September-December — Isle of Pines, Ouvéa, white sand beaches.'),
    ('🌿', 'Randonnée', 'Mai-novembre — Parc de la Rivière Bleue, Grande Randonnée.', 'Hiking', 'May-November — Blue River Park, Grande Randonnée.'),
    ('🏘️', 'Culture kanak', 'Toute l\'année — Centre Tjibaou, tribus, coutumes et pilou.', 'Kanak Culture', 'Year-round — Tjibaou Centre, tribes, customs and pilou.'),
],
'saint-barthelemy': [
    ('🏖️', 'Plage', 'Décembre-avril — Colombier, Gouverneur, Saline.', 'Beach', 'December-April — Colombier, Gouverneur, Saline.'),
    ('🍽️', 'Gastronomie', 'Toute l\'année — restaurants français étoilés, cuisine créole raffinée.', 'Gastronomy', 'Year-round — Michelin-starred French restaurants, refined Creole cuisine.'),
    ('⛵', 'Voile', 'Novembre-avril — régate de Saint-Barth, Bucket Regatta.', 'Sailing', 'November-April — Saint Barth regatta, Bucket Regatta.'),
    ('🛍️', 'Shopping', 'Toute l\'année — boutiques duty-free, marques de luxe, Gustavia.', 'Shopping', 'Year-round — duty-free boutiques, luxury brands, Gustavia.'),
],
'saint-martin': [
    ('🏖️', 'Plage', 'Décembre-avril — Orient Bay, Baie Rouge, Maho (avions).', 'Beach', 'December-April — Orient Bay, Baie Rouge, Maho (planes).'),
    ('🍽️', 'Gastronomie', 'Toute l\'année — 300+ restaurants, fusion franco-caribéenne.', 'Gastronomy', 'Year-round — 300+ restaurants, Franco-Caribbean fusion.'),
    ('🤿', 'Snorkeling', 'Décembre-mai — réserve de Pinel, Tintamarre, tortues.', 'Snorkelling', 'December-May — Pinel reserve, Tintamarre, turtles.'),
    ('⛵', 'Excursion Anguilla', 'Décembre-avril — 20 min en bateau, plages désertes.', 'Anguilla Trip', 'December-April — 20 min by boat, deserted beaches.'),
],
'saint-pierre-et-miquelon': [
    ('🐋', 'Baleines', 'Juin-août — baleines à bosse et rorquals au large.', 'Whales', 'June-August — humpback and fin whales offshore.'),
    ('🥾', 'Randonnée', 'Juin-septembre — île aux Marins, cap Percé, tourbières.', 'Hiking', 'June-September — Île aux Marins, Cap Percé, peat bogs.'),
    ('🏘️', 'Patrimoine', 'Toute l\'année — maisons colorées, musée Heritage, phares.', 'Heritage', 'Year-round — colourful houses, Heritage museum, lighthouses.'),
    ('🎣', 'Pêche', 'Juin-septembre — morue, flétan, tradition terre-neuvienne.', 'Fishing', 'June-September — cod, halibut, Newfoundland tradition.'),
],

# ── CROATIE suite ──
'hvar': [
    ('🏖️', 'Plage', 'Juin-septembre — Stiniva, Dubovica, îles Pakleni en bateau.', 'Beach', 'June-September — Stiniva, Dubovica, Pakleni Islands by boat.'),
    ('💜', 'Lavande', 'Juin-juillet — champs en fleur, distilleries artisanales.', 'Lavender', 'June-July — blooming fields, artisanal distilleries.'),
    ('🌙', 'Vie nocturne', 'Juillet-août — Hula Hula, Carpe Diem, bars sur les toits.', 'Nightlife', 'July-August — Hula Hula, Carpe Diem, rooftop bars.'),
    ('🍷', 'Vin', 'Septembre-octobre — cépage Plavac Mali, vignobles de Stari Grad.', 'Wine', 'September-October — Plavac Mali grape, Stari Grad vineyards.'),
],
'kotor': [
    ('🏰', 'Vieille ville', 'Avril-juin ou septembre-octobre — remparts, Saint-Tryphon sans les croisières.', 'Old Town', 'April-June or September-October — ramparts, St. Tryphon without cruise ships.'),
    ('🥾', 'Forteresse', 'Mars-novembre — 1350 marches jusqu\'au château, vue sur les bouches.', 'Fortress', 'March-November — 1350 steps to the castle, view over the bay.'),
    ('🚤', 'Bouches de Kotor', 'Mai-octobre — Perast, Notre-Dame-du-Rocher, Blue Cave.', 'Bay of Kotor', 'May-October — Perast, Our Lady of the Rocks, Blue Cave.'),
    ('🤿', 'Plongée', 'Juin-septembre — Blue Cave, épaves, grottes sous-marines.', 'Diving', 'June-September — Blue Cave, wrecks, underwater caves.'),
],
'zadar': [
    ('🎵', 'Orgue marin', 'Toute l\'année — installation sonore unique, coucher de soleil sur la mer.', 'Sea Organ', 'Year-round — unique sound installation, sunset over the sea.'),
    ('🏖️', 'Plage', 'Juin-septembre — Sakarun, Kraljičina Plaža, eaux turquoise.', 'Beach', 'June-September — Sakarun, Kraljičina Plaža, turquoise waters.'),
    ('🏝️', 'Kornati', 'Mai-septembre — archipel de 89 îles, excursions en bateau.', 'Kornati', 'May-September — archipelago of 89 islands, boat excursions.'),
    ('🏛️', 'Histoire', 'Toute l\'année — forum romain, église Saint-Donat, ville 3000 ans.', 'History', 'Year-round — Roman forum, St. Donatus church, 3000-year-old city.'),
],
'zagreb': [
    ('🏛️', 'Musées', 'Toute l\'année — Musée des Relations Rompues, Mimara, musée Naïf.', 'Museums', 'Year-round — Museum of Broken Relationships, Mimara, Naïve Art Museum.'),
    ('🍽️', 'Gastronomie', 'Toute l\'année — Dolac marché, štrukli, cuisine continentale.', 'Gastronomy', 'Year-round — Dolac market, štrukli, continental cuisine.'),
    ('🎄', 'Avent', 'Décembre — élu meilleur marché de Noël d\'Europe plusieurs années de suite.', 'Advent', 'December — voted best European Christmas market multiple years running.'),
    ('🏘️', 'Ville haute', 'Toute l\'année — Gornji Grad, cathédrale, funiculaire, porte de pierre.', 'Upper Town', 'Year-round — Gornji Grad, cathedral, funicular, Stone Gate.'),
],
'plitvice': [
    ('🥾', 'Randonnée', 'Avril-juin ou septembre-octobre — 8 sentiers balisés, chutes sans foule.', 'Hiking', 'April-June or September-October — 8 marked trails, waterfalls without crowds.'),
    ('📸', 'Photographie', 'Octobre-novembre — feuillages d\'automne sur les lacs turquoise.', 'Photography', 'October-November — autumn foliage over turquoise lakes.'),
    ('🚤', 'Bateau électrique', 'Avril-octobre — traversée du lac Kozjak, incluse dans l\'entrée.', 'Electric Boat', 'April-October — Lake Kozjak crossing, included in entry.'),
    ('❄️', 'Hiver', 'Janvier-février — lacs gelés, chutes glacées, magie hivernale.', 'Winter', 'January-February — frozen lakes, icy waterfalls, winter magic.'),
],
'montenegro': [
    ('🏖️', 'Plage', 'Juin-septembre — Sveti Stefan, Budva, Velika Plaža d\'Ulcinj (13 km).', 'Beach', 'June-September — Sveti Stefan, Budva, Velika Plaža of Ulcinj (13km).'),
    ('🏔️', 'Montagne', 'Juin-septembre — Durmitor, canyon de Tara, lac Noir.', 'Mountains', 'June-September — Durmitor, Tara canyon, Black Lake.'),
    ('🚤', 'Bouches de Kotor', 'Mai-octobre — croisière fjord, Perast, îlots vénitiens.', 'Bay of Kotor', 'May-October — fjord cruise, Perast, Venetian islets.'),
    ('🥾', 'Randonnée', 'Mai-octobre — sentiers Prokletije, Biogradska Gora, forêt vierge.', 'Hiking', 'May-October — Prokletije trails, Biogradska Gora, virgin forest.'),
],

# ── TURQUIE suite ──
'antalya': [
    ('🏖️', 'Plage', 'Mai-octobre — Konyaaltı, Lara, Kaputaş à 3h.', 'Beach', 'May-October — Konyaaltı, Lara, Kaputaş 3h away.'),
    ('🏛️', 'Ruines', 'Mars-mai ou octobre — Perge, Aspendos, Side.', 'Ruins', 'March-May or October — Perge, Aspendos, Side.'),
    ('🌊', 'Cascades', 'Toute l\'année — Düden, Manavgat, Kurşunlu.', 'Waterfalls', 'Year-round — Düden, Manavgat, Kurşunlu.'),
    ('👨‍👩‍👧', 'Famille', 'Juin ou septembre — aquaparks, plages sécurisées, hôtels tout-inclus.', 'Family', 'June or September — waterparks, safe beaches, all-inclusive hotels.'),
],
'bodrum': [
    ('🏖️', 'Plage', 'Juin-septembre — Bitez, Gümbet, Türkbükü.', 'Beach', 'June-September — Bitez, Gümbet, Türkbükü.'),
    ('🏰', 'Château Saint-Pierre', 'Avril-octobre — musée d\'archéologie sous-marine.', 'Castle of St. Peter', 'April-October — museum of underwater archaeology.'),
    ('⛵', 'Croisière bleue', 'Juin-septembre — goélette traditionnelle le long de la côte turque.', 'Blue Cruise', 'June-September — traditional gulet along the Turkish coast.'),
    ('🌙', 'Vie nocturne', 'Juillet-août — bars, clubs et restaurants du front de mer.', 'Nightlife', 'July-August — waterfront bars, clubs and restaurants.'),
],
'cappadoce': [
    ('🎈', 'Montgolfière', 'Avril-octobre — vol au lever du soleil sur les cheminées de fée.', 'Hot Air Balloon', 'April-October — sunrise flight over fairy chimneys.'),
    ('🥾', 'Randonnée', 'Avril-juin ou septembre-octobre — vallées Rose, Rouge, Ihlara.', 'Hiking', 'April-June or September-October — Rose, Red, Ihlara valleys.'),
    ('🕳️', 'Cités souterraines', 'Toute l\'année — Derinkuyu, Kaymaklı, 8 niveaux sous terre.', 'Underground Cities', 'Year-round — Derinkuyu, Kaymaklı, 8 levels underground.'),
    ('🏨', 'Hôtel troglodyte', 'Toute l\'année — dormir dans une grotte creusée dans le tuf.', 'Cave Hotel', 'Year-round — sleep in a cave carved from tuff.'),
],
'fethiye': [
    ('🪂', 'Parapente', 'Avril-novembre — Babadağ, 1969m au-dessus du lagon d\'Ölüdeniz.', 'Paragliding', 'April-November — Babadağ, 1969m above Ölüdeniz lagoon.'),
    ('🏖️', 'Plage', 'Mai-octobre — Ölüdeniz, Butterfly Valley, Kabak.', 'Beach', 'May-October — Ölüdeniz, Butterfly Valley, Kabak.'),
    ('🥾', 'Voie lycienne', 'Mars-mai ou octobre — sentier de 540 km, ruines antiques.', 'Lycian Way', 'March-May or October — 540km trail, ancient ruins.'),
    ('⛵', 'Croisière', 'Juin-septembre — 12 îles, Butterfly Valley en goélette.', 'Cruise', 'June-September — 12 islands, Butterfly Valley by gulet.'),
],
'izmir': [
    ('🏛️', 'Éphèse', 'Mars-mai ou octobre — site antique majeur à 1h, sans la chaleur.', 'Ephesus', 'March-May or October — major ancient site 1h away, without the heat.'),
    ('🏘️', 'Bazars', 'Toute l\'année — Kemeraltı, 3500 boutiques, caravansérails.', 'Bazaars', 'Year-round — Kemeraltı, 3500 shops, caravanserais.'),
    ('🏖️', 'Plage', 'Juin-septembre — Çeşme, Alaçatı, côte égéenne.', 'Beach', 'June-September — Çeşme, Alaçatı, Aegean coast.'),
    ('🍽️', 'Gastronomie', 'Toute l\'année — boyoz, kumru, poisson frais du Kordon.', 'Gastronomy', 'Year-round — boyoz, kumru, fresh fish from Kordon.'),
]

def main():
    dry_run = '--dry-run' in sys.argv

    # ── 1. Update destinations.csv with taglines ──
    dest_path = os.path.join(DATA, 'destinations.csv')
    rows = []
    with open(dest_path, encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        for row in reader:
            slug = row['slug_fr']
            if slug in TAGLINES:
                fr, en = TAGLINES[slug]
                row['hero_sub'] = fr
                row['hero_sub_en'] = en
            rows.append(row)

    updated_tags = sum(1 for r in rows if r['slug_fr'] in TAGLINES)
    print(f"Taglines: {updated_tags} destinations updated")

    if not dry_run:
        with open(dest_path, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        print(f"  → Written to {dest_path}")

    # ── 2. Append new cards to cards.csv ──
    cards_path = os.path.join(DATA, 'cards.csv')
    cards_en_path = os.path.join(DATA, 'cards_en.csv')

    # Read existing slugs
    existing_slugs = set()
    with open(cards_path, encoding='utf-8-sig') as f:
        for row in csv.DictReader(f):
            existing_slugs.add(row['slug'])

    new_fr = []
    new_en = []
    for slug, card_list in CARDS.items():
        if slug in existing_slugs:
            continue
        for c in card_list:
            icon, titre_fr, texte_fr, titre_en, texte_en = c
            new_fr.append({'slug': slug, 'icon': icon, 'titre': titre_fr, 'texte': texte_fr})
            new_en.append({'slug': slug, 'icon': icon, 'titre': titre_en, 'texte': texte_en})

    print(f"Cards: {len(new_fr)} new FR cards for {len(set(r['slug'] for r in new_fr))} destinations")

    if not dry_run and new_fr:
        with open(cards_path, 'a', encoding='utf-8-sig', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['slug', 'icon', 'titre', 'texte'])
            writer.writerows(new_fr)
        print(f"  → Appended to {cards_path}")

        with open(cards_en_path, 'a', encoding='utf-8-sig', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['slug', 'icon', 'titre', 'texte'])
            writer.writerows(new_en)
        print(f"  → Appended to {cards_en_path}")

    # Summary
    still_missing_tags = [slug for slug, (fr, en) in TAGLINES.items()]
    all_slugs_needing_cards = set()
    with open(dest_path, encoding='utf-8-sig') as f:
        for row in csv.DictReader(f):
            all_slugs_needing_cards.add(row['slug_fr'])
    covered_cards = existing_slugs | set(CARDS.keys())
    missing_cards = all_slugs_needing_cards - covered_cards
    print(f"\nRemaining without cards: {len(missing_cards)} destinations")
    if missing_cards:
        print(f"  Slugs: {sorted(missing_cards)[:20]}...")

if __name__ == '__main__':
    main()
