"""Part 3: Africa + Central/East Asia"""

CARDS = [
# ── EAST AFRICA ──
("nairobi","🦁","Nairobi National Park safari","Jun–Oct — lions and giraffes with the skyline in the background."),
("nairobi","🦒","Giraffe Centre & Sheldrick Trust","Year-round — hand-fed giraffes, orphaned baby elephants."),
("nairobi","🏔️","Rift Valley excursion","Jun–Oct — Lake Naivasha, Lake Nakuru, flamingos."),
("nairobi","🍽️","Nairobi food scene","Year-round — nyama choma, ugali, Karen quarter restaurants."),

("mombasa","🏖️","Diani & Nyali beaches","Jan–Mar or Jul–Oct — white sand, turquoise water, reefs."),
("mombasa","🏰","Fort Jesus","Year-round — 1593 Portuguese UNESCO fortress, museum."),
("mombasa","🤿","Diving & snorkeling","Oct–Mar — Kisite-Mpunguti marine park, turtles, dolphins."),
("mombasa","🍽️","Swahili cuisine","Year-round — Mombasa biryani, pilau, spiced seafood."),

("stone-town","🏘️","Zanzibar medina","Jun–Oct — UNESCO labyrinthine lanes, carved doors, spices."),
("stone-town","🌶️","Spice Tour","Jul–Oct — clove, vanilla, nutmeg plantations."),
("stone-town","🏖️","Nungwi beaches","Jun–Oct — white sand, turquoise water, traditional dhows."),
("stone-town","🍽️","Forodhani Gardens","Year-round — seafood night market, Zanzibar pizza."),

("zanzibar-ville","🏘️","Stone Town & carved doors","Jun–Oct — UNESCO labyrinthine lanes, House of Wonders."),
("zanzibar-ville","🌶️","Spice Tour","Jul–Oct — clove, vanilla, nutmeg, aromatic plantations."),
("zanzibar-ville","🏖️","Nungwi & Kendwa beaches","Jun–Oct — white sand, sunset views, dhows at anchor."),
("zanzibar-ville","🍽️","Forodhani Night Market","Year-round — skewers, Zanzibar pizza, sugarcane juice."),

("dar-es-salaam","🏖️","Kigamboni beaches","Jun–Oct — wild beaches, kitesurfing, fresh seafood."),
("dar-es-salaam","🛶","Bongoyo Island","Jun–Oct — snorkeling 30 min by boat, pristine reefs."),
("dar-es-salaam","🍽️","Kivukoni Fish Market","Year-round — ultra-fresh grilled fish, harbor atmosphere."),
("dar-es-salaam","💰","Budget","Jun–Oct — peak season but very low prices, accommodation €15–25."),

("arusha","🦁","Serengeti & Ngorongoro safari","Jun–Oct — Big Five, Great Migration, spectacular crater."),
("arusha","🏔️","Mount Meru","Jun–Oct — acclimatization trek before Kili, Kilimanjaro views."),
("arusha","☕","Coffee plantations","Year-round — arabica coffee farming, visits and roasting."),
("arusha","🏛️","Maasai Market","Year-round — Maasai crafts, jewelry, shuka fabrics."),

("victoria-falls","🌊","Victoria Falls","Feb–May — peak flow, spray visible 30 km away, rainbows."),
("victoria-falls","🚣","Zambezi rafting","Aug–Dec — Class V rapids among the world's best."),
("victoria-falls","🦁","Chobe safari","May–Oct — Chobe Park 80 km away, thousands of elephants."),
("victoria-falls","🌉","Bridge & bungee jumping","Year-round — 111 m above the gorge, falls views."),

("livingstone","🌊","Victoria Falls (Zambia side)","Feb–May — Knife Edge Bridge, monumental spray, rainbows."),
("livingstone","🚣","Zambezi rafting","Aug–Dec — Class V rapids from Livingstone, full day."),
("livingstone","🦏","Mosi-oa-Tunya NP","Jun–Oct — white rhinos, giraffes, walking safari."),
("livingstone","🌅","Zambezi sunset cruise","Year-round — cruise with hippos, crocodiles, sundowners."),

("kigali","🦍","Virunga gorillas","Jun–Sep — trek in Volcanoes NP, 1h face-to-face with gorillas."),
("kigali","🏛️","Genocide Memorial","Year-round — Gisozi memorial, essential duty of remembrance."),
("kigali","☕","Rwandan coffee","Year-round — plantations, artisan roasting, tastings."),
("kigali","🌿","Nyungwe Forest","Jun–Sep — tropical forest, chimpanzees, 50 m canopy walk."),

("addis-abeba","🏛️","National Museum & Lucy","Year-round — australopithecus skeleton, 3.2 million years old."),
("addis-abeba","☕","Coffee ceremony","Year-round — birthplace of coffee, ritual roasting, jebena."),
("addis-abeba","🍽️","Injera & Ethiopian cuisine","Year-round — injera with spiced wots, tibs, Merkato markets."),
("addis-abeba","💰","Budget","Oct–May — dry season, cheap domestic flights."),

("gondar","🏰","Fasil Ghebbi","Oct–Mar — Ethiopian UNESCO castles, 'Africa's Camelot'."),
("gondar","🎭","Timkat (Epiphany)","January — colorful procession, ritual baths, Ethiopia's biggest festival."),
("gondar","🏔️","Simien Mountains","Oct–Mar — trekking, geladas, Ethiopian wolves, vertiginous landscapes."),
("gondar","💰","Budget","Oct–Mar — dry season, Ethiopia very affordable, trek €30/day."),

("lalibela","⛪","Rock-hewn churches","Oct–Mar — 11 churches carved from rock, UNESCO, 12th century."),
("lalibela","🎭","Ethiopian Christmas (Genna)","Jan 7 — nighttime mass in the churches, unique pilgrimage."),
("lalibela","🥾","Abuna Yosef hiking","Oct–Feb — trek at 4,000 m, views of the churches, geladas."),
("lalibela","💰","Budget","Oct–Mar — accommodation €10–15, mandatory guide €20/day."),

("kampala","🦍","Bwindi gorillas","Jun–Sep — trek from Kampala, UNESCO impenetrable forest."),
("kampala","🏛️","Buganda Royal Tombs","Year-round — UNESCO Kasubi site, royal culture."),
("kampala","🍽️","Rolex wraps & street food","Year-round — omelette rolled in chapati, matoke, local cuisine."),
("kampala","💰","Budget","Jun–Aug — dry season, cheaper safaris and lodges."),

("jinja","🚣","Nile source rafting","Year-round — Class V rapids, one of the world's best spots."),
("jinja","🏞️","Source of the Nile","Year-round — White Nile starting point from Lake Victoria."),
("jinja","🐒","Mabira Forest","Jun–Sep — primates, birds, canopy walk, mountain biking."),
("jinja","💰","Budget","Year-round — full day rafting $100–130, accommodation €10–15."),

("lamu","🏘️","Swahili old town","Jun–Oct — UNESCO, coral stone lanes, donkeys (no cars)."),
("lamu","⛵","Dhow sunset cruise","Jul–Oct — traditional sailing, Shela Beach, Manda Island."),
("lamu","🎭","Maulidi Festival","Mar (varies) — Prophet's celebration, music, dances, donkey races."),
("lamu","💰","Budget","May–Jun — pre-season, guesthouses €15–25, local food €3–5."),

# ── SOUTHERN AFRICA ──
("johannesburg","🏛️","Apartheid Museum","Year-round — national memory, Constitution Hill, Soweto."),
("johannesburg","🦁","Pilanesberg safari","May–Oct — Big Five 2.5h from Joburg, ideal dry season."),
("johannesburg","🎨","Maboneng & Arts on Main","Year-round — arty quarter, galleries, street food, markets."),
("johannesburg","💰","Budget","May–Aug — dry winter, best Europe-Africa flight prices."),

("durban","🏖️","Golden Mile","Year-round — urban beach, surfing, warm water all year (21–26°C)."),
("durban","🍛","Bunny chow & curry","Year-round — curry in hollowed bread, unique Indo-South African cuisine."),
("durban","🦏","Hluhluwe-Imfolozi","May–Oct — rhino reserve 3h away, Big Five, dry season."),
("durban","💰","Budget","May–Aug — mild winter 22°C, low prices, fewer tourists."),

("maun","🦁","Okavango Delta","May–Oct — mokoro safari, Big Five, peak flood levels."),
("maun","🐘","Moremi Game Reserve","Jun–Oct — reserve within the delta, elephants, leopards, wild dogs."),
("maun","🦅","Scenic delta flight","Year-round — small plane over delta channels and islands."),
("maun","💰","Budget","Nov–Mar — green season, lodges –40%, baby animals."),

("tofo","🤿","Manta ray diving","Oct–Mar — giant manta rays, whale sharks, reefs."),
("tofo","🏖️","Tofo Beach","May–Oct — white sand, turquoise water, surfing, dry season."),
("tofo","🐋","Whale sharks","Oct–Mar — swimming with whale sharks, unique experience."),
("tofo","💰","Budget","May–Oct — backpackers €10/night, diving €35, meals €3–5."),

("etosha","🦁","Etosha safari","May–Oct — waterholes make easy game viewing, lions, elephants, rhinos."),
("etosha","📸","Etosha Pan","Year-round — 5,000 km² white dried lake, lunar landscape."),
("etosha","🦏","Black rhinos","May–Oct — one of the last large populations, nighttime waterholes."),
("etosha","💰","Budget","Nov–Mar — green season, campsites €10–15, animals with babies."),

("windhoek","🏛️","Christuskirche & Alte Feste","Year-round — German colonial architecture, national museum."),
("windhoek","🍺","Joe's Beerhouse & cuisine","Year-round — oryx, kudu, potjiekos, Namibian beers."),
("windhoek","🏜️","Sossusvlei excursion","May–Oct — world's tallest red dunes, 5h drive."),
("windhoek","💰","Budget","Nov–Mar — green season, lodges –40%, spectacular storms."),

("maputo","🍽️","Seafood & market","Year-round — giant prawns, matapa, piri-piri, Mercado Central."),
("maputo","🏛️","CFM Station & Fort","Year-round — Eiffel-style station, Portuguese fortress, street art."),
("maputo","🏖️","Inhaca Island beaches","May–Oct — island 1h by ferry, snorkeling, mangroves."),
("maputo","🎵","Marrabenta & nightlife","Year-round — Mozambican music, Baixa bars, dancing."),

# ── WEST AFRICA ──
("lagos","🎵","Afrobeats & nightlife","Year-round — Lekki, Victoria Island, clubs and live concerts."),
("lagos","🏖️","Tarkwa Bay & Elegushi","Nov–Mar — boat-access beaches, dry season."),
("lagos","🍽️","Street food & jollof rice","Year-round — grilled suya, jollof rice, Lekki markets."),
("lagos","🎨","Nike Art Gallery","Year-round — 4 floors of contemporary Nigerian art, workshops."),

("accra","🏖️","Labadi Beach","Nov–Mar — lively beach, reggae, coconut palms, dry season."),
("accra","🏰","Cape Coast Castle","Year-round — UNESCO slave fort 2h away, poignant memorial."),
("accra","🍽️","Street food & Makola Market","Year-round — jollof rice, kelewele, waakye, bustling markets."),
("accra","🥁","Chale Wote Festival","Aug — street art, music, performances in the Jamestown quarter."),

("abidjan","🏖️","Grand-Bassam beaches","Nov–Mar — UNESCO colonial resort 40 km away, dry season."),
("abidjan","🍽️","Maquis bars & attiéké","Year-round — open-air restaurants, grilled chicken, alloco."),
("abidjan","🏛️","Plateau & cathedral","Year-round — modernist business district, St Paul (Aldo Rossi)."),
("abidjan","💰","Budget","Dec–Feb — dry season, affordable accommodation in Plateau."),

("ouagadougou","🎬","FESPACO","Feb–Mar (biennial) — Africa's largest film festival."),
("ouagadougou","🎭","Central market & crafts","Oct–Feb — masks, bronzes, traditional fabrics, dry season."),
("ouagadougou","🍽️","Burkinabè cuisine","Year-round — tô, grilled chicken, dolo (millet beer), maquis."),
("ouagadougou","💰","Budget","Nov–Feb — dry season, accommodation €15–25, meals €2–3."),

("cotonou","🏛️","Ganvié (Venice of Africa)","Nov–Mar — lake village on stilts, pirogue, 30,000 inhabitants."),
("cotonou","🎭","Dantokpa Market","Year-round — West Africa's largest market, voodoo, fabrics."),
("cotonou","🏖️","Beach Route","Nov–Mar — coconut palm beaches, fishing villages, dry season."),
("cotonou","💰","Budget","Nov–Feb — ideal season, accommodation €15–20, zémidjan €0.50."),

("lome","🏖️","Beach & fetish market","Nov–Mar — Lomé beach, Akodessewa voodoo market, unique in the world."),
("lome","🏛️","Togoville & Lake Togo","Year-round — historic village, cathedral, pirogue crossing."),
("lome","🍽️","Togolese cuisine","Year-round — fufu, akoumé, tchoukoutou, lively maquis."),
("lome","💰","Budget","Nov–Feb — ultra-affordable destination, meals €1–2, hotels €10–15."),

("douala","🏛️","The Pagoda & central market","Year-round — colonial architecture, bustling market."),
("douala","🌿","Mount Cameroon","Nov–Mar — West Africa's highest peak, 2–3 day trek."),
("douala","🍽️","Cameroonian cuisine","Year-round — ndolé, grilled fish, bean-banana fritters."),
("douala","💰","Budget","Dec–Feb — dry season, affordable regional flights."),

("freetown","🏖️","Peninsula beaches","Nov–Apr — Tokeh, River No.2, golden sand, dry season."),
("freetown","🏛️","Cotton Tree & history","Year-round — symbolic tree, National Museum, freed slave history."),
("freetown","🌿","Tacugama Sanctuary","Year-round — chimpanzee sanctuary, forest hikes."),
("freetown","💰","Budget","Nov–Apr — dry season, emerging tourism, preserved authenticity."),

# ── CENTRAL ASIA ──
("samarcande","🕌","Registan","Apr–May or Sep–Oct — 3 madrasas, turquoise mosaics, Silk Road heart."),
("samarcande","🏛️","Shah-i-Zinda","Apr–Oct — blue-tiled mausoleum necropolis, Central Asia's finest."),
("samarcande","🍽️","Plov & bazaars","Year-round — Uzbek pilaf, tandoor bread, Siab bazaar."),
("samarcande","💰","Budget","Nov–Feb — hotels –40%, uncrowded sites, cold but dry."),

("boukhara","🕌","Historic center","Apr–May or Sep–Oct — Kalon Minaret, Ark Citadel, Lyab-i-Hauz."),
("boukhara","🏛️","Samanid Mausoleum","Year-round — 10th-century masterpiece, intricate brickwork."),
("boukhara","🧵","Carpets & crafts","Year-round — weaving workshops, suzani embroidery, ikat silk."),
("boukhara","💰","Budget","Nov–Feb — hotels –40%, cheaper artisan shops."),

("khiva","🏰","Itchan Kala","Apr–May or Sep–Oct — UNESCO walled inner city, Kalta Minor minaret."),
("khiva","🏛️","Tosh-Hovli Palace","Apr–Oct — 19th-century palace, blue tiles, restored harem."),
("khiva","🌅","Sunset from the ramparts","Apr–Oct — views over the museum-city from medieval walls."),
("khiva","💰","Budget","Nov–Feb — hotels in madrasas €15, cold but magical."),

("almaty","🏔️","Tian Shan Mountains","Jun–Sep — Kok Tobe cable car, Shymbulak resort, Big Almaty Lake."),
("almaty","⛷️","Shymbulak skiing","Dec–Mar — resort 30 min from downtown, affordable powder."),
("almaty","🍎","Green bazaar & cuisine","Year-round — Green Bazaar, beshbarmak, original wild apples."),
("almaty","🏞️","Charyn Canyon","May–Oct — 'Grand Canyon of Kazakhstan', 200 km from Almaty."),

("bichkek","🏔️","Ala-Archa & Tian Shan","Jun–Sep — gorge 30 min away, alpine treks, accessible glaciers."),
("bichkek","🐴","Yurts & nomadic life","Jun–Sep — yurt stays, Song Kul, horseback riding at altitude."),
("bichkek","🏞️","Issyk-Kul Lake","Jul–Aug — world's 2nd largest alpine lake, mountain beaches."),
("bichkek","💰","Budget","Year-round — one of Central Asia's cheapest countries, meals €2–3."),

("mongolie","🐴","Steppes & nomadic life","Jun–Sep — yurts, horseback riding, Mongolian hospitality, vastness."),
("mongolie","🏜️","Gobi Desert","Jun–Sep — Khongoryn Els dunes, Bayanzag cliffs, camels."),
("mongolie","🎭","Naadam Festival","Jul 11–13 — wrestling, archery, horse racing, national celebration."),
("mongolie","💰","Budget","Jun–Sep — only practicable window, organized tours $50–80/day."),

# ── EAST ASIA ──
("xian","🏛️","Terracotta Army","Mar–May or Sep–Nov — 8,000 warriors, UNESCO, avoid summer heat."),
("xian","🏰","Xi'an city walls","Year-round — 14 km Ming dynasty wall by bike, panoramic views."),
("xian","🍜","Muslim Quarter","Year-round — roujiamo (Chinese burger), biang biang noodles, skewers."),
("xian","💰","Budget","Nov–Feb — tickets and hotels –30%, cold but bearable 5–10°C."),

("chengdu","🐼","Giant Panda Base","Year-round — baby pandas, early morning visit to see them active."),
("chengdu","🌶️","Sichuan cuisine","Year-round — hotpot, mapo tofu, dan dan noodles, Sichuan pepper."),
("chengdu","🍵","Teahouses","Year-round — People's Park, tea culture, mahjong games."),
("chengdu","🏛️","Leshan Giant Buddha","Mar–May or Sep–Nov — 71 m statue 2h away, UNESCO."),

("guilin","🏞️","Li River cruise","Apr–Oct — iconic karst landscapes between Guilin and Yangshuo."),
("guilin","🚲","Yangshuo & cycling","Apr–Oct — rice paddies, karst peaks, climbing, bohemian vibe."),
("guilin","🌾","Longji Rice Terraces","May–Jun or Sep–Oct — terraced rice paddies, Zhuang and Yao villages."),
("guilin","🍜","Guilin rice noodles","Year-round — guilin mifen, iconic local specialty."),

("zhangjiajie","🏞️","Avatar Hallelujah Mountains","Mar–May or Sep–Nov — sandstone pillars from the film, glass bridge."),
("zhangjiajie","🚡","Bailong Elevator","Year-round — 326 m outdoor elevator, world record."),
("zhangjiajie","🌿","National park & hiking","Mar–May or Sep–Nov — misty trails, lush forests."),
("zhangjiajie","💰","Budget","Dec–Feb — park entry –50%, cheaper hotels, cold but magical."),

("lijiang","🏘️","Naxi old town","Mar–May or Sep–Nov — canals, tile roofs, UNESCO Naxi culture."),
("lijiang","🏔️","Jade Dragon Snow Mountain","Apr–Oct — glacier at 4,500 m, cable car, Zhang Yimou show."),
("lijiang","🏞️","Tiger Leaping Gorge","Mar–May or Sep–Nov — one of the world's deepest gorges, 2-day trek."),
("lijiang","🍵","Naxi & Dongba culture","Year-round — pictographic script, Naxi music, butter tea."),

("kaohsiung","🏛️","Dragon Tiger Pagodas","Year-round — Lotus Pond, colorful pagodas, Taoist temples."),
("kaohsiung","🍽️","Night markets","Year-round — Liuhe, Ruifeng, stinky tofu, original bubble tea."),
("kaohsiung","🏖️","Cijin Island","Oct–May — ferry ride, seafood, temple, beach, lighthouse."),
("kaohsiung","🎨","Pier-2 Art Center","Year-round — converted warehouses, contemporary art, street art."),
]
