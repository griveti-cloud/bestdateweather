"""Part 2: India, Japan, Balkans, Middle East"""

CARDS = [
# ── INDIA ──
("mumbai","🏛️","Gateway of India & Colaba","Oct–Mar — Taj Mahal Palace, Crawford Market, colonial quarter."),
("mumbai","🎬","Bollywood","Year-round — Film City studios, set visits, Dharavi."),
("mumbai","🍛","Chowpatty street food","Year-round — vada pav, pav bhaji, bhel puri on the beach."),
("mumbai","🏝️","Elephanta Caves","Oct–May — UNESCO sculpted caves, 1h ferry from the harbor."),

("jaipur","🏰","Amber Fort & Hawa Mahal","Oct–Mar — Pink City forts and palaces, ideal 20–25°C."),
("jaipur","🐘","Elephant festival","Mar — Holi with decorated elephants, explosion of colors."),
("jaipur","🧵","Bazaars & crafts","Year-round — Johari Bazaar (jewelry), block-print textiles, Bapu Bazaar."),
("jaipur","🍛","Rajasthani cuisine","Year-round — dal baati churma, laal maas, lassi at Lassiwala."),

("varanasi","🛕","Ganges ghats","Oct–Mar — Ganga Aarti ceremony at sunset, sunrise boat ride."),
("varanasi","🕉️","Kashi Vishwanath & Sarnath","Year-round — golden temple, Buddhist site, ancient sacred quarter."),
("varanasi","🎵","Dhrupad Festival","Feb–Mar — Hindustani classical music, millennial traditions."),
("varanasi","🍛","Sacred street food","Year-round — kachori, chaat, saffron lassi, vegetarian thali."),

("udaipur","🏰","Lake Palace & City Palace","Oct–Mar — floating palace, Monsoon Palace at sunset."),
("udaipur","⛵","Lake Pichola","Oct–Mar — sunset boat ride, Jag Mandir, golden reflections."),
("udaipur","🎨","Miniature painting","Year-round — miniature art school, Rajasthani artisan workshops."),
("udaipur","💰","Budget","Jul–Sep — monsoon but prices –50%, palaces and riads nearly empty."),

("agra","🕌","Taj Mahal at sunrise","Oct–Mar — golden dawn light, fewer crowds at 6am."),
("agra","🏰","Agra Fort","Oct–Mar — Mughal UNESCO fortress, Taj view from the ramparts."),
("agra","🕌","Fatehpur Sikri","Oct–Mar — ghost Mughal city 40 km away, carved red sandstone."),
("agra","🍛","Mughal cuisine","Year-round — petha (local sweet), kebabs, Agra biryani."),

("pondicherry","🏘️","French Quarter","Year-round — pastel colonial streets, cafés, bougainvillea."),
("pondicherry","🧘","Auroville & Matrimandir","Year-round — utopian community, golden sphere, meditation."),
("pondicherry","🏖️","Paradise Beach","Nov–Mar — beach accessible by boat, ideal dry season."),
("pondicherry","🍛","Franco-Indian cuisine","Year-round — curry crêpes, dosai, Suffren Street cafés."),

("hampi","🏛️","Vijayanagara ruins","Oct–Mar — UNESCO temples, Vittala Temple and stone chariot."),
("hampi","🧗","Bouldering","Oct–Mar — legendary granite boulders, active climbing community."),
("hampi","🚲","Cycling through ruins","Nov–Feb — 500+ monuments to explore by bike, 20–28°C."),
("hampi","💰","Budget","Nov–Feb — guesthouses at €5/night, thali at €1, cheapest India."),

("kochi","🎣","Chinese fishing nets & Fort Cochin","Oct–Mar — historic nets, Portuguese churches, Jewish synagogue."),
("kochi","💃","Kathakali dance","Year-round — ritual dance performances, elaborate makeup."),
("kochi","🛶","Alleppey backwaters","Sep–Mar — houseboat through rice paddies and Kerala canals."),
("kochi","🍛","Kerala cuisine","Year-round — appam, fish curry, thali on banana leaf."),

# ── JAPAN ──
("sapporo","❄️","Snow festival","February — giant ice sculptures at Odori Park, 2M+ visitors."),
("sapporo","🍜","Miso ramen & crab","Year-round — Sapporo ramen, king crab, Genghis Khan BBQ."),
("sapporo","⛷️","Niseko & Furano skiing","Dec–Mar — legendary powder, 15 m of snow/year, post-ski onsen."),
("sapporo","🌸","Late cherry blossoms","May — hanami one month after Tokyo, Maruyama Park, Goryokaku."),

("nara","🦌","Park deer","Year-round — 1,200 free-roaming deer, shika senbei crackers."),
("nara","🛕","Todai-ji","Year-round — world's largest wooden structure, 15 m Buddha."),
("nara","🍂","Fall foliage","Nov — park and temples in red and gold, fewer crowds than Kyoto."),
("nara","🍡","Nakatanidou mochi","Year-round — live mochi pounding, kakinoha sushi, matcha."),

("nagasaki","🕊️","Peace Memorial","Year-round — Peace Park, museum, August 9 ceremony."),
("nagasaki","🏘️","Glover Garden","Mar–May — hillside gardens, Western architecture, bay views."),
("nagasaki","🐉","Kunchi Festival","October — 400-year-old Chinese dragon festival, Dejima quarter."),
("nagasaki","🍜","Champon & castella","Year-round — champon noodles, Portuguese castella cake, shippoku."),

# ── BALKANS ──
("sarajevo","🕌","Baščaršija","Year-round — Ottoman bazaar, Gazi Husrev-beg mosque, ćevapi."),
("sarajevo","🏔️","Olympic Mountains","Dec–Mar — skiing Jahorina and Bjelašnica, 1984 Olympic sites."),
("sarajevo","☕","Bosnian coffee culture","Year-round — coffee brewed in džezva, Sebilj fountain, old town."),
("sarajevo","🏛️","Tunnel of Hope","Year-round — 1992–96 siege tunnel, living war memorial."),

("belgrade","🎵","Nightlife & splavovi","May–Oct — floating bars on the Danube, Savamala, Skadarlija."),
("belgrade","🏰","Kalemegdan Fortress","Year-round — citadel at the Danube-Sava confluence, panoramic views."),
("belgrade","🍽️","Serbian cuisine","Year-round — ćevapčići, pljeskavica, rakija in the kafanas."),
("belgrade","💰","Budget","Year-round — Europe's cheapest capital, meals €5–8."),

("skopje","🏛️","Old Ottoman bazaar","Year-round — largest Balkan bazaar after Istanbul."),
("skopje","🏔️","Matka Canyon","Apr–Oct — gorge 30 min away, kayaking, caves, medieval monasteries."),
("skopje","🍽️","Tavče gravče & kebapi","Year-round — Macedonian cuisine, Tikveš wines, rakija."),
("skopje","💰","Budget","Year-round — accommodation €20–30/night, full meal €5."),

("tirana","🎨","Street art & Blloku","Year-round — trendy quarter, murals, hip cafés."),
("tirana","🏔️","Dajti Express","Apr–Oct — cable car to Mount Dajti, city-wide views."),
("tirana","🏛️","Skanderbeg Square","Year-round — Et'hem Bey mosque, national museum, bunkers."),
("tirana","💰","Budget","Year-round — one of Europe's cheapest capitals, meals €3–5."),

("budva","🏖️","Beaches & old town","Jun–Sep — Mogren Beach, Venetian citadel, Sveti Stefan nearby."),
("budva","🎵","Sea Dance Festival","Jul — beach music festival on Jaz Beach, international DJs."),
("budva","🏛️","Kotor 30 min away","Year-round — UNESCO bay, ramparts, Montenegrin fjord."),
("budva","💰","Budget","May or Sep–Oct — nearly empty beaches, prices –40%, sea still warm."),

("trogir","🏛️","UNESCO historic center","Year-round — St Lawrence Cathedral, Radovan's portal."),
("trogir","🏖️","Čiovo beaches","Jun–Sep — island linked by bridge, coves, crystal water."),
("trogir","⛵","Split-Trogir sailing","Jun–Sep — sailing between islands, Šolta, Brač within reach."),
("trogir","💰","Budget","May or Oct — neighboring Split crowded, Trogir calm and –30%."),

("ohrid","🏛️","Lake & UNESCO old town","Jun–Sep — 3-million-year-old lake, St John Kaneo church on the cliff."),
("ohrid","🛕","Byzantine churches","Year-round — 365 churches, medieval frescoes, Samuel's Fortress."),
("ohrid","🏖️","Lakeside beaches","Jul–Aug — clear water, pebble and sand beaches, 24–26°C."),
("ohrid","💰","Budget","Sep–Oct — golden late season, accommodation €15–20, quiet town."),

("piran","🏘️","Venetian old town","May–Sep — Tartini Square, ramparts, medieval lanes, bell tower."),
("piran","🏖️","Beaches & Sečovlje salt pans","Jun–Sep — historic salt pans, swimming, Portorož 10 min away."),
("piran","🍽️","Seafood & wine","Year-round — harbor restaurants, local Refošk wine, olive oil."),
("piran","💰","Budget","Oct–Apr — affordable alternative to the nearby Croatian coast."),

("lac-bled","🏊","Lake & island church","Jun–Sep — swimming, pletna boat to the island, Baroque church."),
("lac-bled","🏰","Medieval castle","Year-round — perched castle, panoramic view, Bled cream cake."),
("lac-bled","🥾","Vintgar Gorge","Apr–Oct — walkways above the turquoise river, 1.6 km."),
("lac-bled","💰","Budget","Oct–Nov — autumn colors, prices –40%, peaceful lake."),

# ── MIDDLE EAST ──
("riyad","🏛️","Diriyah & At-Turaif","Oct–Mar — UNESCO site, birthplace of the Saudi kingdom, restored quarter."),
("riyad","🏙️","Riyadh Boulevard","Oct–Mar — entertainment park, restaurants, cultural events."),
("riyad","🏜️","Edge of the World","Nov–Feb — spectacular cliffs 90 min away, striking sunset."),
("riyad","💰","Budget","Nov–Feb — outside Ramadan, bearable 20–25°C temperatures."),

("djeddah","🏛️","Al-Balad","Oct–Apr — UNESCO old town, mashrabiya houses, souks."),
("djeddah","🤿","Red Sea diving","Year-round — coral reefs, wrecks, 26–30°C water."),
("djeddah","🍽️","Corniche waterfront","Oct–Apr — 30 km promenade, seafood restaurants, sunset."),
("djeddah","💰","Budget","Nov–Feb — mild temperatures, outside Hajj season."),

("bahrein","🏛️","Bahrain Fort","Oct–Apr — UNESCO site, 4,000 years of history, archaeological museum."),
("bahrein","🤿","Diving & pearl heritage","Oct–May — UNESCO pearl trail, dive sites, clear water."),
("bahrein","🏎️","F1 Grand Prix","Mar — Sakhir circuit, night race, international atmosphere."),
("bahrein","🍽️","Manama & souks","Oct–Apr — Bab al-Bahrain souk, Gulf cuisine, restaurants."),

("koweït","🏛️","Kuwait Towers","Nov–Mar — architectural icons, panoramic bay views."),
("koweït","🛍️","Souks & Mubarakiya","Year-round — historic market, spices, dates, Bedouin crafts."),
("koweït","🏖️","Failaka Island","Oct–Apr — archaeological island, Greek ruins, quiet beaches."),
("koweït","💰","Budget","Nov–Feb — 22°C, free museums, accessible public beaches."),

("beyrouth","🍽️","Lebanese cuisine","Year-round — mezze, manoushe, Gemmayzeh and Mar Mikhael restaurants."),
("beyrouth","🏔️","Cedars & Qadisha Valley","May–Oct — ancient UNESCO cedar forest, spectacular gorge, hiking."),
("beyrouth","🏛️","Byblos & Baalbek","Apr–Oct — Phoenician cities and colossal Roman temples."),
("beyrouth","🏖️","Batroun & Tyre","Jun–Sep — northern coast beaches, Tyre and its seaside ruins."),

("muscat","🕌","Sultan Qaboos Grand Mosque","Oct–Mar — one of the world's finest mosques, giant Persian carpet."),
("muscat","🏜️","Wahiba Sands","Nov–Mar — golden dunes, Bedouin bivouac, 4x4 desert safari."),
("muscat","🤿","Musandam fjords","Oct–Apr — dhow cruise, diving, dolphins, spectacular scenery."),
("muscat","🏛️","Muttrah souks","Oct–Apr — frankincense, Omani silver, seaside corniche."),

("petra","🏛️","Treasury (Al-Khazneh)","Mar–May or Oct–Nov — rose-carved façade, spectacular Siq entrance."),
("petra","🌌","Petra by Night","Mon–Wed–Thu — 1,500 candles illuminate the Treasury, unique experience."),
("petra","🥾","Monastery (Ad-Deir)","Mar–May or Oct–Nov — 800 steps, 50 m façade, sweeping views."),
("petra","💰","Budget","Jun–Aug — intense heat but Jordan Pass worthwhile, fewer crowds."),

("aqaba","🤿","Red Sea diving","Year-round — coral reefs, wrecks, 22–28°C water, visa-free zone."),
("aqaba","🏖️","Red Sea beaches","Apr–Oct — Berenice Beach, South Beach, crystal water."),
("aqaba","🏰","Aqaba Fort","Year-round — Mamluk fort, 1917 Arab Revolt."),
("aqaba","💰","Budget","May–Jun or Sep–Oct — outside intense summer and winter peak."),

("wadi-rum","🏜️","Desert 4x4 & camel rides","Oct–Apr — Martian landscapes, natural arches, Nabataean inscriptions."),
("wadi-rum","🏕️","Bedouin bivouac","Year-round — night under the stars, fireside tea, traditional zarb."),
("wadi-rum","🌌","Stargazing","Year-round — zero light pollution, spectacular Milky Way."),
("wadi-rum","🎬","Film locations","Year-round — The Martian, Dune, Lawrence of Arabia, iconic landscapes."),

("al-ula","🏛️","Hegra (Mada'in Salih)","Oct–Mar — Saudi Petra, UNESCO Nabataean tombs carved in sandstone."),
("al-ula","🏜️","Elephant Rock & desert","Oct–Mar — sculpted rock formations, sunset views."),
("al-ula","🎭","AlUla Moments Festival","Dec–Mar — art installations, concerts, cultural events."),
("al-ula","🌌","Stargazing","Year-round — desert with no light pollution, spectacular nights."),

("ras-al-khaimah","🏔️","Jebel Jais & via ferrata","Oct–Apr — UAE's highest peak, world's longest zip-line."),
("ras-al-khaimah","🏖️","Beaches & mangroves","Oct–May — pristine beaches, mangrove kayaking."),
("ras-al-khaimah","🏜️","Desert & dunes","Nov–Mar — 4x4 safari, glamping, falconry."),
("ras-al-khaimah","💰","Budget","May–Sep — prices –50% vs Dubai, lesser-known UAE alternative."),

("salalah","🌿","Khareef (monsoon)","Jul–Sep — the peninsula's only monsoon, lush green hills."),
("salalah","🏖️","Beaches & wadis","Oct–Mar — Mughsail Beach, freshwater wadis, coconut palms."),
("salalah","🏛️","Sumhuram ruins","Oct–Apr — ancient frankincense port, UNESCO, sea views."),
("salalah","🐪","Frankincense route","Oct–Apr — millennial frankincense trees, Rub al-Khali desert."),

("casablanca","🕌","Hassan II Mosque","Year-round — world's 3rd largest mosque, 210 m minaret over the sea."),
("casablanca","🏛️","Art Deco district","Year-round — 1930s architecture, Boulevard Mohammed V."),
("casablanca","🍽️","Food & central market","Year-round — seafood, pastilla, tagines, pastries."),
("casablanca","💰","Budget","Nov–Feb — off-season, cheaper flights and hotels, 18°C."),

("tanger","🌊","Cap Spartel & Hercules Caves","Apr–Oct — Atlantic-Mediterranean confluence, panoramic views."),
("tanger","🏛️","Kasbah & medina","Year-round — Kasbah Museum, Dar el-Makhzen palace, Café Hafa."),
("tanger","🍽️","Tangier cuisine","Year-round — grilled fish at the port, mint tea, pastilla."),
("tanger","🎨","Literary city","Year-round — Bowles, Burroughs, Matisse: the city that inspired artists."),

("merzouga","🏜️","Erg Chebbi & camels","Oct–Apr — 150 m dunes, bivouac under the stars, spectacular sunrise."),
("merzouga","🎵","Gnaoua Festival","Jun — Gnaoua music in the desert, trance and traditions."),
("merzouga","🏍️","Quad & 4x4","Oct–Apr — dune excursions, Saharan tracks."),
("merzouga","🌌","Stargazing","Year-round — Sahara with zero light pollution, Milky Way."),

("assouan","⛵","Nile felucca ride","Oct–Apr — traditional sailing, islands, sunset temples."),
("assouan","🏛️","Philae Temple","Oct–Apr — Isis temple on Agilkia Island, sound and light show."),
("assouan","🏜️","Abu Simbel","Oct–Apr — Ramesses II temples, 3h drive or flight, UNESCO."),
("assouan","🍽️","Nubian cuisine","Year-round — colorful villages, falafel, hibiscus, karkadé tea."),

("ispahan","🕌","Naqsh-e Jahan Square","Mar–May or Sep–Nov — world's 2nd largest square, mosques, bazaar."),
("ispahan","🌉","Historic bridges","Year-round — Si-o-se-pol (33 arches), Khaju, evening strolls."),
("ispahan","🎨","Crafts & miniatures","Year-round — miniature painting workshops, enamels, Persian carpets."),
("ispahan","🍽️","Isfahan cuisine","Year-round — beryani (local dish), gaz (nougat), rose tea."),

("teheran","🏛️","Golestan Palace & museums","Mar–May or Sep–Nov — UNESCO Golestan Palace, national museum, Treasury."),
("teheran","🏔️","Mount Damavand","Jun–Sep — Iran's highest peak (5,610 m), 2-day trek."),
("teheran","🍽️","Bazaar & Persian cuisine","Year-round — Grand Bazaar, kebab koobideh, tahdig, saffron tea."),
("teheran","💰","Budget","Nov–Feb — off-season, Iran very affordable, favorable exchange rate."),
]
