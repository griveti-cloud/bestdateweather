"""Part 4: SE Asia, South Asia, Oceania"""

CARDS = [
# ── VIETNAM ──
("danang","🏖️","My Khe & An Bang beaches","Mar–Sep — warm waters, surfing, 30 km of coast."),
("danang","🏛️","Hoi An 30 km away","Feb–May — lanterns, UNESCO old town, custom tailors."),
("danang","🏔️","Bà Nà Hills & Golden Bridge","Feb–Sep — iconic golden bridge, cable car, hill station."),
("danang","🍜","Central Vietnamese cuisine","Year-round — mì quảng, bánh xèo, cao lầu in Hoi An."),

("hue","🏛️","Imperial Citadel","Feb–Apr — Nguyễn UNESCO citadel, pagodas, royal tombs."),
("hue","🛶","Perfume River","Feb–Apr — cruise to the Celestial Lady Pagoda, tombs."),
("hue","🍜","Imperial cuisine","Year-round — bún bò Huế, bánh khoái, refined court cuisine."),
("hue","💰","Budget","Sep–Nov — off-season, accommodation €10–15, rain possible."),

("ninh-binh","🛶","Tam Coc & Trang An","Feb–May — rowboats on river, karst caves, UNESCO rice paddies."),
("ninh-binh","🚲","Rice paddy walk","May–Jun — golden rice paddies, pagodas, temples among the peaks."),
("ninh-binh","🏛️","Ancient capital Hoa Lu","Year-round — temples of the Dinh and Lê kings, 10th century."),
("ninh-binh","💰","Budget","Year-round — affordable Ha Long alternative, boat €5, hotel €10."),

# ── PHILIPPINES ──
("manille","🏛️","Intramuros & Fort Santiago","Nov–May — Spanish walls, San Agustin UNESCO church."),
("manille","🍽️","Binondo street food","Year-round — world's oldest Chinatown, dumplings, halo-halo."),
("manille","🏖️","Batangas islands","Nov–May — 2h from Manila, Anilao diving, secret beaches."),
("manille","💰","Budget","Jun–Oct — monsoon but prices –40%, abundant cheap food."),

("coron","🤿","Japanese WWII wrecks","Nov–May — 12 WWII wrecks in crystal waters, legendary diving."),
("coron","🏞️","Kayangan & Twin Lagoon","Nov–May — emerald lakes between limestone cliffs."),
("coron","🏖️","Island hopping","Nov–May — Malcapuya, Banana Island, white sand."),
("coron","💰","Budget","Jun–Oct — rainy season but tours –50%, affordable lodging."),

("luzon","🏞️","Banaue Rice Terraces","Mar–May — 2,000-year-old UNESCO terraces, spectacular views."),
("luzon","🌋","Mayon & Taal volcanoes","Nov–May — perfect cones, treks, lake inside a volcano."),
("luzon","🏖️","Vigan & Ilocos coast","Nov–May — UNESCO Spanish colonial town, wild beaches."),
("luzon","🍽️","Regional cuisine","Year-round — Bicol express, pinakbet, Luzon lechon."),

# ── SRI LANKA ──
("colombo","🏛️","Fort & Gangaramaya","Year-round — colonial quarter, eclectic Buddhist temple."),
("colombo","🍛","Sri Lankan cuisine","Year-round — rice and curry, kottu roti, Pettah street food."),
("colombo","🛍️","Pettah Market","Year-round — chaotic and colorful bazaar, spices, textiles."),
("colombo","💰","Budget","May–Sep — southwest monsoon but Colombo manageable, low prices."),

("kandy","🛕","Temple of the Tooth","Year-round — sacred Buddha relic, Esala Perahera (Jul–Aug)."),
("kandy","🌿","Royal Botanic Gardens","Year-round — Peradeniya, 60 ha of tropical species."),
("kandy","🚂","Kandy-Ella train","Year-round — one of the world's most beautiful train rides, 6h."),
("kandy","🍵","Tea plantations","Jan–Mar — Nuwara Eliya plantation visits, tastings."),

("ella","🚂","Nine Arches Bridge","Year-round — iconic railway bridge in the jungle, photos."),
("ella","🥾","Little Adam's Peak","Jan–Mar — easy 2h hike, 360° mountain views."),
("ella","🍵","Tea plantations","Jan–Mar — endless tea fields, picking, tasting."),
("ella","💰","Budget","May–Sep — fewer tourists, guesthouses €10/night."),

# ── MYANMAR ──
("yangon","🛕","Shwedagon Pagoda","Nov–Feb — 99 m golden stupa, sunset views, dry season."),
("yangon","🏛️","Colonial quarter","Nov–Feb — British architecture, Strand Hotel, Bogyoke Market."),
("yangon","🍜","Burmese cuisine","Year-round — mohinga (soup), tea leaf salad, shan noodles."),
("yangon","💰","Budget","Nov–Feb — peak season but still affordable, guesthouses €15–20."),

("mandalay","🏛️","Royal palace & hill","Oct–Feb — panoramic views, teak monasteries, Kuthodaw Pagoda."),
("mandalay","🌅","U Bein Bridge","Year-round — world's longest teak bridge, sunset views."),
("mandalay","🛕","Bagan temples","Oct–Feb — 2,000+ temples, sunrise balloon ride, UNESCO site."),
("mandalay","🍜","Mandalay cuisine","Year-round — meeshay, tohu thoke, Myanmar beer."),

# ── CAMBODIA & THAILAND ──
("battambang","🏛️","Colonial architecture","Nov–Mar — preserved French buildings, emerging art galleries."),
("battambang","🚂","Bamboo Train","Year-round — handmade bamboo train, rice paddies, unique experience."),
("battambang","🏞️","Temples & countryside","Nov–Mar — Phnom Sampeau, Wat Banan, authentic Khmer countryside."),
("battambang","💰","Budget","Year-round — very affordable Cambodia, hotel €8, meal €2."),

("chiang-rai","🏛️","White Temple (Wat Rong Khun)","Nov–Feb — surreal contemporary temple, cool season."),
("chiang-rai","🍵","Doi Mae Salong tea plantations","Nov–Feb — Chinese-influenced tea hills, misty views."),
("chiang-rai","🏔️","Golden Triangle","Nov–Feb — Mekong confluence, Laos-Myanmar-Thailand, opium museum."),
("chiang-rai","💰","Budget","May–Oct — rainy season but prices –30%, lush nature."),

# ── INDONESIA ──
("yogyakarta","🛕","Borobudur at sunrise","Apr–Oct — world's largest Buddhist temple, morning mist."),
("yogyakarta","🏛️","Prambanan","Apr–Oct — 9th-century Hindu temples, Ramayana ballet (summer)."),
("yogyakarta","🎨","Batik & crafts","Year-round — batik workshops, sultan's kraton, wayang kulit."),
("yogyakarta","🍽️","Malioboro street food","Year-round — gudeg, bakpia, nasi gudeg, hip cafés."),

("labuan-bajo","🐉","Komodo dragons","Apr–Oct — Komodo National Park, giant monitors, Pink Beach."),
("labuan-bajo","🤿","Manta Point diving","Apr–Nov — manta rays, rich currents, spectacular corals."),
("labuan-bajo","🌅","Padar & Rinca cruise","Apr–Oct — panoramic Padar view, hiking, snorkeling."),
("labuan-bajo","💰","Budget","Nov–Mar — rainy season but tours –30%, affordable lodging."),

("raja-ampat","🤿","Diving & snorkeling","Oct–Apr — world's greatest marine biodiversity, 1,500 species."),
("raja-ampat","🏖️","Islands & lagoons","Oct–Apr — Pianemo, Wayag, turquoise lagoons among karsts."),
("raja-ampat","🐦","Birds of paradise","Oct–Apr — bird of paradise watching, tropical forest."),
("raja-ampat","💰","Budget","May–Sep — rainy season but homestays €30, fewer crowds."),

# ── BHUTAN & NEPAL ──
("bhutan","🏛️","Tiger's Nest (Taktsang)","Mar–May or Sep–Nov — monastery perched 900 m above the valley."),
("bhutan","🎭","Tshechu festivals","Mar–Apr or Sep–Oct — sacred masked dances in the dzongs."),
("bhutan","🏔️","Himalayan treks","Mar–May or Sep–Nov — Druk Path, Jomolhari, pristine landscapes."),
("bhutan","🏛️","Punakha & Paro dzongs","Year-round — fortress-monasteries at river confluences."),

("pokhara","🏔️","Annapurna & Machapuchare views","Oct–Nov — breathtaking Himalayan panorama from Phewa Lake."),
("pokhara","🪂","Sarangkot paragliding","Oct–Apr — flying facing 8,000 m peaks, world-class spot."),
("pokhara","🥾","Annapurna Base Camp trek","Oct–Nov or Mar–Apr — legendary 7–12 day trek."),
("pokhara","⛵","Phewa Lake","Year-round — sunset boat ride, Barahi Temple, mountain reflections."),

# ── OCEANIA ──
("auckland","⛵","City of Sails","Oct–Apr — more boats per capita than anywhere, America's Cup."),
("auckland","🌋","Volcanoes & Rangitoto","Year-round — 53 extinct volcanoes, Rangitoto ferry (2h return)."),
("auckland","🍷","Waiheke Island","Nov–Mar — vineyards, golden beaches, 35 min by ferry."),
("auckland","🍽️","Pacific fusion cuisine","Year-round — seafood, hangi, Ponsonby markets."),

("queenstown","🪂","Bungee jumping","Year-round — birthplace of bungee (Kawarau Bridge, 43 m)."),
("queenstown","⛷️","Remarkables & Coronet Peak skiing","Jun–Sep — skiing with Lake Wakatipu views."),
("queenstown","🚤","Milford Sound","Year-round — fjord cruise, waterfalls, dolphins."),
("queenstown","🍷","Central Otago Pinot Noir","Feb–Apr — world's southernmost vineyards, exceptional Pinot Noir."),

("rotorua","♨️","Geysers & hot springs","Year-round — Te Puia, Wai-O-Tapu, bubbling mud pools."),
("rotorua","🏛️","Māori culture","Year-round — haka, hangi, Tamaki Village, cultural shows."),
("rotorua","🌲","Redwoods & mountain biking","Year-round — redwood forest, 130+ km of MTB trails."),
("rotorua","🛶","Lakes & kayaking","Nov–Mar — Lake Tarawera, blue water, Hot Water Beach kayak."),

("wellington","🎬","Weta Workshop & film","Year-round — Lord of the Rings studios, cinema museum."),
("wellington","🍺","Craft beer & cafés","Year-round — NZ's coffee capital, Cuba Street, breweries."),
("wellington","🏔️","Te Papa & wild coast","Nov–Mar — free national museum, Red Rocks, seals."),
("wellington","🍽️","Food & night market","Year-round — inventive restaurants, Wellington Night Market."),

("christchurch","🏔️","Arthur's Pass & Canterbury","Nov–Mar — alpine trekking, turquoise rivers, TranzAlpine train."),
("christchurch","🌿","Botanical gardens","Sep–Mar — 21 ha of gardens, Avon River punting."),
("christchurch","🎨","Street art & renaissance","Year-round — city creatively rebuilt after 2011."),
("christchurch","🏖️","Banks Peninsula","Nov–Mar — volcanoes, bays, Hector's dolphins, French Akaroa."),

("darwin","🐊","Crocodiles & Kakadu","May–Oct — Kakadu NP, Aboriginal paintings, giant crocs."),
("darwin","🌅","Mindil Beach Markets","May–Oct — sunset, night markets, Asian cuisine."),
("darwin","🏛️","Aboriginal culture","Year-round — Museum and Art Gallery, Kakadu rock art."),
("darwin","💰","Budget","Nov–Apr — wet season, prices –50%, spectacular storms."),

("hobart","🏔️","Cradle Mountain","Nov–Mar — Overland Track, glacial lakes, endemic wildlife."),
("hobart","🍽️","MONA & food scene","Year-round — avant-garde museum, Tasmanian whisky, oysters."),
("hobart","🏞️","Salamanca Market","Saturdays year-round — waterfront artisan market."),
("hobart","🐧","Bruny Island","Nov–Mar — penguins, artisan cheeses, old-growth forests."),

("adelaide","🍷","Barossa Valley","Mar–May — harvest, world-renowned Shiraz, cellar doors."),
("adelaide","🏖️","Glenelg & Kangaroo Island","Nov–Mar — beach, sea lions, koalas, Cape Jervis ferry."),
("adelaide","🎭","Adelaide Festival","Mar — Australia's oldest arts festival, Fringe Festival."),
("adelaide","🍽️","Central Market","Year-round — covered market since 1869, local produce, cafés."),

("brisbane","🐨","Lone Pine Koala Sanctuary","Year-round — world's oldest koala sanctuary."),
("brisbane","🏖️","Gold Coast & Sunshine Coast","Sep–May — surfing, golden beaches, 1h from Brisbane."),
("brisbane","🏞️","South Bank Parklands","Year-round — man-made beach, QAGOMA galleries, restaurants."),
("brisbane","🍽️","Eat Street Northshore","Fri–Sun year-round — night market, world cuisine, atmosphere."),

("whitsundays","🏖️","Whitehaven Beach","May–Oct — silica white sand, Hill Inlet, turquoise water."),
("whitsundays","🤿","Great Barrier Reef","Jun–Oct — snorkeling, diving, turtles, manta rays."),
("whitsundays","⛵","Sailing & island hopping","May–Oct — sailing among 74 islands, paradise anchorages."),
("whitsundays","💰","Budget","Nov–Mar — wet season but reduced prices, warm sea."),

("uluru","🏜️","Uluru sunrise & sunset","Apr–Oct — changing colors of the sacred monolith, 348 m."),
("uluru","🏛️","Aṉangu culture","Year-round — Aboriginal art, dot painting, Maruku Arts."),
("uluru","🏞️","Kata Tjuta (The Olgas)","Apr–Oct — Valley of the Winds walk, 36 red rock domes."),
("uluru","🌌","Field of Light","Year-round — 50,000 luminous spheres by Bruce Munro, starry night."),

# ── PACIFIC ISLANDS ──
("samoa","🏖️","To Sua Ocean Trench","May–Oct — turquoise natural pool in a grotto, iconic."),
("samoa","🌴","Lalomanu beaches","May–Oct — white sand, traditional fale huts, reefs."),
("samoa","🏛️","Samoan culture","Year-round — fiafia, ava ceremony, traditional pe'a tattoo."),
("samoa","💰","Budget","May–Oct — dry season, fale accommodation €20–40/night."),

("vanuatu","🌋","Yasur Volcano","Year-round — accessible active volcano, nighttime eruptions."),
("vanuatu","🤿","SS President Coolidge wreck","Apr–Oct — world's largest diveable wreck, Espiritu Santo."),
("vanuatu","🪢","Naghol land diving","Apr–Jun — original bungee jumping ritual, Pentecost Island."),
("vanuatu","🏖️","Blue Lagoon & Champagne Beach","May–Oct — crystal waters, wild beaches."),

("tonga","🐋","Humpback whales","Jul–Oct — swimming with whales, Ha'apai and Vava'u."),
("tonga","🏖️","Ha'apai beaches","May–Oct — deserted atolls, white sand, snorkeling."),
("tonga","🏛️","Polynesian culture","Year-round — Pacific's last kingdom, dance, kava."),
("tonga","💰","Budget","May–Jun — early season, affordable family lodges."),

("rarotonga","🏖️","Muri Lagoon","May–Oct — turquoise lagoon, motu islets, snorkeling, kayaking."),
("rarotonga","🥾","Cross-Island Track","May–Oct — 4h island crossing, jungle, Te Rua Manga waterfall."),
("rarotonga","🛵","Island tour","Year-round — 32 km by scooter, beaches, markets, Cook culture."),
("rarotonga","💰","Budget","Nov–Mar — rainy season but lodges –30%, warm sea."),

("iles-cook","🏖️","Aitutaki Lagoon","May–Oct — Pacific's most beautiful lagoon, One Foot Island."),
("iles-cook","🤿","Snorkeling & turtles","Year-round — accessible reefs, turtles, tropical fish."),
("iles-cook","🏛️","Polynesian culture","Year-round — dances, weaving, ukulele, Saturday markets."),
("iles-cook","💰","Budget","Nov–Mar — rainy season but lodging –30%, warm sea."),

("noumea","🏖️","Isle of Pines","May–Oct — Oro natural pool, columnar pines, lagoon."),
("noumea","🤿","UNESCO lagoon","Year-round — world's largest enclosed lagoon, diving."),
("noumea","🏛️","Tjibaou Cultural Centre","Year-round — Renzo Piano architecture, Kanak culture."),
("noumea","🍽️","Franco-Melanesian fusion","Year-round — bougna, raw fish in coconut milk, brasseries."),

("tahiti","🏄","Teahupo'o surfing","May–Oct — legendary wave, world competitions, 2024 Olympics."),
("tahiti","🏖️","Black sand beaches & lagoons","May–Oct — volcanic sand, Faarumai waterfalls, turquoise lagoon."),
("tahiti","🌺","Polynesian culture","Jul — Heiva i Tahiti, traditional dances, competitions."),
("tahiti","🍽️","Raw fish in coconut milk","Year-round — national dish, Papeete markets, food trucks."),

("moorea","🏖️","Beaches & lagoons","May–Oct — Temae Beach, Cook's Bay, crystal water."),
("moorea","🐋","Whales & dolphins","Jul–Nov — humpback whales in the lagoon, dolphin swims."),
("moorea","🍍","Pineapple & farming","Year-round — Moorea is the pineapple island, plantations, fresh juice."),
("moorea","🥾","Belvédère viewpoint","Year-round — viewpoint over both bays, forest hike."),

("papouasie","🌿","Highlands & tribes","May–Oct — Baliem Valley, preserved tribal cultures."),
("papouasie","🎭","Goroka Show","Sep — gathering of 100+ tribes, costumes, ritual dances."),
("papouasie","🤿","Kimbe Bay diving","Oct–Apr — pristine reefs, WWII wrecks, exceptional biodiversity."),
("papouasie","💰","Budget","May–Oct — dry season, limited access, tours $100–150/day."),

("sao-miguel","♨️","Caldeiras & Sete Cidades","May–Sep — volcanic lakes, hot springs, cozido cooked underground."),
("sao-miguel","🐋","Whale watching","Apr–Oct — resident sperm whales, dolphins, petrels."),
("sao-miguel","🌿","Volcanic hiking","May–Sep — coastal trails, craters, laurel forests."),
("sao-miguel","🍵","Tea & pineapple","Year-round — Europe's only tea plantation, pineapple greenhouses."),

("socotra","🌳","Dragon blood trees","Oct–Apr — endemic dragon trees, otherworldly landscape."),
("socotra","🏖️","Deserted beaches","Nov–Mar — Qalansiyah, Detwah Lagoon, white sand with no tourists."),
("socotra","🌿","Unique biodiversity","Oct–Apr — 37% endemic plants, Indian Ocean's Galápagos."),
("socotra","💰","Budget","Oct–Apr — limited access, mandatory tour $80–120/day all-inclusive."),

("svalbard","🐻‍❄️","Polar bears","Mar–Jun — observation by boat or snowmobile, population ~3,000."),
("svalbard","🌅","Midnight sun","May–Jul — continuous light, kayaking, tundra hiking."),
("svalbard","🏔️","Glaciers & fjords","Jun–Aug — coastal cruise, glacier fronts, walruses."),
("svalbard","🌌","Northern lights","Nov–Feb — polar night, spectacular auroras, snowmobile."),
]
