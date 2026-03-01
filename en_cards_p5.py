"""Part 5: Americas + remaining Europe/misc"""

CARDS = [
# ── REMAINING EUROPE ──
("alacati","🏄","Windsurfing & kitesurfing","May–Oct — Turkey's best wind spot, thermal winds, flat water."),
("alacati","🏘️","Cobblestone streets & boutiques","Apr–Oct — restored stone houses, bougainvillea, cafés."),
("alacati","🍽️","Aegean cuisine","Year-round — wild herbs, olive oil, mezes, fish market."),
("alacati","💰","Budget","Nov–Mar — off-season, prices –50%, mild 15°C winters."),

("peloponnese","🏛️","Ancient sites","Mar–May or Sep–Nov — Olympia, Epidaurus, Mycenae, Corinth."),
("peloponnese","🏖️","Wild beaches","Jun–Sep — Elafonisos, Voidokilia, Simos, uncrowded shores."),
("peloponnese","🍷","Nemea wines","Sep–Oct — harvest, Agiorgitiko grape, hillside vineyards."),
("peloponnese","🥾","Lousios Gorge & Mani","Apr–Jun or Sep–Nov — gorge monasteries, Mani tower villages."),

("larnaca","🏖️","Beaches & promenade","May–Oct — Finikoudes, Mackenzie Beach, warm water."),
("larnaca","🦩","Salt lake & Hala Sultan Tekke","Nov–Mar — flamingos, Ottoman mosque, stunning reflections."),
("larnaca","🤿","Zenobia wreck","Apr–Oct — one of the world's top wreck dives, 42 m deep."),
("larnaca","🏛️","Kition & Choirokoitia","Year-round — Phoenician ruins, Neolithic UNESCO site."),

("göteborg","🏝️","Gothenburg archipelago","Jun–Aug — car-free islands, swimming, seafood shacks."),
("göteborg","☕","Fika & seafood","Year-round — coffee culture, Feskekôrka fish market, shrimp."),
("göteborg","🎢","Liseberg","May–Dec — Scandinavia's largest amusement park, Christmas market."),
("göteborg","💰","Budget","Sep–Nov — off-season, cheaper hotels, autumn colors."),

("innsbruck","🏔️","Nordkette & Golden Roof","Year-round — cable car to 2,300 m, Gothic balcony, old town."),
("innsbruck","⛷️","Alpine skiing","Dec–Mar — 9 ski areas within 30 min, Olympic runs."),
("innsbruck","🏛️","Old town & Hofburg","Year-round — Maria-Theresien-Straße, Imperial Palace."),
("innsbruck","🍺","Biergarten & Tiroler Gröstl","Year-round — hearty Tyrolean food, mountain huts, local beer."),

("ghent","🎨","Mystic Lamb & cathedral","Year-round — Van Eyck's Ghent Altarpiece, St Bavo's Cathedral."),
("ghent","🎵","Ghent Festival","Jul — Europe's largest cultural festival, 10 days of music and theater."),
("ghent","🍽️","Food & frituren","Year-round — waterzooi, frites, craft beer, Michelin-starred restaurants."),
("ghent","💰","Budget","Year-round — cheaper alternative to Bruges, same charm."),

("hallstatt","🏘️","Alpine village & lake","May–Oct — UNESCO lakeside village, pastel houses, mountain views."),
("hallstatt","⛏️","Prehistoric salt mine","Year-round — world's oldest salt mine (7,000 years), underground lake."),
("hallstatt","🏔️","Skywalk & 5 Fingers","May–Oct — panoramic platforms above the lake and Dachstein."),
("hallstatt","💰","Budget","Nov–Mar — fewer crowds, winter magic, cheaper accommodation."),

("lviv","☕","Coffee & chocolate","Year-round — historic coffee houses, Lviv chocolate workshops."),
("lviv","🏛️","UNESCO historic center","Year-round — Rynok Square, Armenian quarter, opera house."),
("lviv","🍺","Breweries & restaurants","Year-round — underground themed restaurants, craft beer."),
("lviv","💰","Budget","Year-round — one of Europe's most affordable cities, meals €3–5."),

("funchal","🌺","Tropical gardens","Year-round — Monte Palace, Botanical Garden, exotic flowers."),
("funchal","🛷","Monte toboggan ride","Year-round — wicker sled descent, traditional since 1850."),
("funchal","🍷","Madeira wine & levadas","Year-round — wine cellars, levada hikes through laurel forests."),
("funchal","🎆","New Year's fireworks","Dec 31 — Guinness record fireworks display, harbor views."),

# ── SOUTH AMERICA ──
("sao-paulo","🍽️","World-class gastronomy","Year-round — 12,000+ restaurants, Italian, Japanese, Brazilian fusion."),
("sao-paulo","🎨","Museums & Beco do Batman","Year-round — MASP, Pinacoteca, Vila Madalena street art."),
("sao-paulo","🎵","Nightlife & samba","Year-round — Vila Madalena, Jardins, live samba bars."),
("sao-paulo","💰","Budget","Apr–Jun — shoulder season, cheaper hotels, mild weather."),

("salvador-de-bahia","🏛️","Pelourinho & Olodum","Year-round — colorful UNESCO quarter, Afro-Brazilian drumming."),
("salvador-de-bahia","🎭","Salvador Carnival","Feb–Mar — largest street party on Earth, axé music, trios elétricos."),
("salvador-de-bahia","🍽️","Bahian cuisine","Year-round — acarajé, moqueca, dendê oil, coconut milk."),
("salvador-de-bahia","🏖️","Itapuã & Porto da Barra","Nov–Mar — urban beaches, warm water year-round."),

("cusco","🏛️","Inca historic center","Apr–Oct — Qorikancha, Plaza de Armas, Inca walls, altitude 3,400 m."),
("cusco","🏔️","Machu Picchu","Apr–Oct — Inca citadel 80 km away, dry season, train or trek."),
("cusco","🌈","Rainbow Mountain","May–Sep — Vinicunca at 5,200 m, colorful mineral layers."),
("cusco","🍽️","Novoandean cuisine","Year-round — ceviche, cuy, pisco sour, San Pedro Market."),

("cusco-ville","🏛️","Plaza de Armas & Qorikancha","Apr–Oct — Inca walls, cathedral, Sun Temple foundations."),
("cusco-ville","🏞️","Sacred Valley","Apr–Oct — Ollantaytambo, Pisac, Moray, Maras salt mines."),
("cusco-ville","🌈","Rainbow Mountain","May–Sep — Vinicunca at 5,200 m, colorful mineral layers."),
("cusco-ville","🍽️","Novoandean cuisine","Year-round — San Pedro Market, ceviche, pisco sour, cuy."),

("lima","🍽️","Gastronomy capital","Year-round — ceviche, Nikkei, Central and Maido among world's best."),
("lima","🏛️","Centro histórico","Year-round — Plaza Mayor, catacombs, colonial churches."),
("lima","🏖️","Costa Verde & Barranco","Dec–Mar — clifftop promenades, bohemian quarter, nightlife."),
("lima","🏛️","Huaca Pucllana","Year-round — pre-Inca pyramid in the Miraflores neighborhood."),

("cartagena","🏰","Walled City","Dec–Mar — colonial UNESCO quarter, colorful buildings, balconies."),
("cartagena","🏖️","Rosario Islands","Dec–Apr — island hopping, turquoise water, snorkeling."),
("cartagena","🍽️","Caribbean cuisine","Year-round — ceviche, arepas de huevo, Getsemaní food scene."),
("cartagena","💰","Budget","May–Jun or Sep–Nov — fewer tourists, prices –30%, occasional rain."),

("cartagena-col","🏰","Walled City","Dec–Mar — colonial UNESCO quarter, colorful streets, plazas."),
("cartagena-col","🏖️","Rosario Islands","Dec–Apr — turquoise waters, mangroves, snorkeling."),
("cartagena-col","🍽️","Ceviche & Getsemaní","Year-round — street food, cocktails, vibrant neighborhood."),
("cartagena-col","💰","Budget","May–Jun or Sep–Nov — rainy season, prices –30%, fewer crowds."),

("montevideo","🍖","Asado & Mercado del Puerto","Year-round — grilled meats in the historic iron market."),
("montevideo","🏖️","Rambla & Ciudad Vieja","Year-round — 22 km promenade, Art Deco quarter, tango bars."),
("montevideo","🍷","Tannat & bodegas","Mar–May — harvest, Uruguay's signature grape, wine routes."),
("montevideo","💰","Budget","Apr–Oct — winter, prices –30%, mild 15°C, fewer tourists."),

("quito","🏛️","Centro histórico","Year-round — best-preserved colonial center in the Americas, UNESCO."),
("quito","🌋","Avenue of Volcanoes","Jun–Sep — Cotopaxi, Chimborazo, spectacular Andean corridor."),
("quito","🌿","Mindo cloud forest","Year-round — hummingbirds, orchids, zip-lines, 2h from Quito."),
("quito","🍽️","Ecuadorian cuisine","Year-round — locro de papa, ceviche, chocolate tastings."),

("la-paz","🏔️","Altiplano & Illimani","May–Oct — world's highest capital, 6,438 m peak backdrop."),
("la-paz","🚴","Death Road by mountain bike","Year-round — 64 km descent from 4,650 to 1,200 m."),
("la-paz","🏛️","Witches' Market","Year-round — Mercado de Hechicería, llama fetuses, folklore."),
("la-paz","💰","Budget","May–Oct — dry season, one of South America's cheapest capitals."),

("la-paz-bolivie","🏔️","Altiplano & Illimani","May–Oct — 3,640 m altitude, highest capital, spectacular views."),
("la-paz-bolivie","🚴","Death Road MTB","Year-round — world's most dangerous road, 64 km descent."),
("la-paz-bolivie","🏛️","Witches' Market","Year-round — traditional remedies, folklore, llama offerings."),
("la-paz-bolivie","💰","Budget","May–Oct — dry season, meals €2–3, hostel €8–12."),

("asuncion","🏛️","Casco histórico & Panteón","Year-round — colonial quarter, Heroes' Pantheon, Cabildo."),
("asuncion","🍽️","Guaraní cuisine","Year-round — chipa, sopa paraguaya, tereré, asado."),
("asuncion","🏞️","Ñeembucú & Chaco","May–Sep — wetlands, birdwatching, wild Chaco savanna."),
("asuncion","💰","Budget","May–Sep — dry winter, one of South America's cheapest capitals."),

("bariloche","🏞️","Seven Lakes Route","Nov–Mar — 107 km scenic drive, pristine Patagonian lakes."),
("bariloche","⛷️","Cerro Catedral skiing","Jul–Sep — South America's largest ski resort, lake views."),
("bariloche","🍫","Artisan chocolate","Year-round — Alpine-style chocolateries, Swiss heritage."),
("bariloche","🏔️","Circuito Chico","Nov–Mar — loop drive, Llao Llao, Moreno viewpoint."),

("mendoza","🍷","Malbec & bodegas","Mar–May — harvest, Luján de Cuyo, Uco Valley, 1,500+ wineries."),
("mendoza","🏔️","Aconcagua & Andes","Nov–Mar — views of the Americas' highest peak (6,961 m)."),
("mendoza","🚣","Río Mendoza rafting","Nov–Mar — Class III–IV rapids, Andean canyon scenery."),
("mendoza","🍽️","Asado & gastronomy","Year-round — Argentine grill, paired with Malbec."),

("florianopolis","🏖️","42 beaches","Dec–Mar — Praia Mole, Joaquina, Campeche, warm Atlantic."),
("florianopolis","🏄","Surfing & kitesurfing","Nov–Apr — consistent waves, Joaquina championship beach."),
("florianopolis","🏞️","Lagoa da Conceição","Year-round — lagoon with restaurants, dunes, nightlife."),
("florianopolis","💰","Budget","Apr–Jun — shoulder season, prices –40%, mild 20°C."),

("manaus","🌿","Amazon lodges","Jun–Nov — jungle lodges, wildlife, low water exposes beaches."),
("manaus","🌊","Meeting of the Waters","Year-round — Rio Negro meets Amazon, 6 km two-tone river."),
("manaus","🐊","Amazon wildlife","Jun–Nov — pink dolphins, caimans, monkeys, birds."),
("manaus","🏛️","Teatro Amazonas","Year-round — Belle Époque opera house, rubber boom symbol."),

("sucre","🏛️","White colonial center","Apr–Oct — Bolivia's prettiest city, UNESCO, whitewashed buildings."),
("sucre","🦕","Cretaceous Park","Year-round — 5,000+ dinosaur footprints on a cliff face."),
("sucre","🍫","Chocolate & markets","Year-round — Tarabuco indigenous market (Sundays), chocolate workshops."),
("sucre","💰","Budget","Year-round — meals €2–3, hostel €6–10, very affordable."),

("iguazu","🌊","Iguazú Falls","Year-round — 275 waterfalls, Devil's Throat, spectacular mist."),
("iguazu","🌿","Subtropical wildlife","Year-round — toucans, coatis, butterflies, jungle trails."),
("iguazu","🚤","Speedboat under the falls","Year-round — boat ride into the spray, thrilling experience."),
("iguazu","💰","Budget","Apr–Jun — fewer crowds, milder temperatures, falls still impressive."),

# ── CENTRAL AMERICA & CARIBBEAN ──
("san-jose","🌋","Poás & Irazú volcanoes","Dec–Apr — active craters, cloud forests, dry season."),
("san-jose","🌿","Monteverde & Arenal","Dec–Apr — hanging bridges, hot springs, wildlife."),
("san-jose","🍽️","Mercado Central","Year-round — casado, gallo pinto, fresh tropical juices."),
("san-jose","💰","Budget","May–Nov — green season, prices –30%, lush landscapes."),

("monteverde","🐦","Resplendent quetzal","Feb–May — cloud forest birding, nesting season."),
("monteverde","🌿","Hanging bridges & zip-lines","Year-round — canopy walkways, zip-lines, night tours."),
("monteverde","☕","Coffee & chocolate","Year-round — plantation tours, bean-to-bar chocolate."),
("monteverde","🦥","Sloth sanctuary","Year-round — sloth watching, guided forest walks."),

("antigua-guatemala","🏛️","Colonial ruins","Nov–Apr — earthquake-ruined churches, cobblestones, volcanoes."),
("antigua-guatemala","🌋","Volcán de Fuego","Year-round — active volcano visible from town, hikes."),
("antigua-guatemala","☕","Guatemalan coffee","Nov–Mar — harvest season, plantation tours, tastings."),
("antigua-guatemala","🎭","Semana Santa","Mar–Apr — elaborate Holy Week processions, flower carpets."),

("san-juan","🏖️","Condado & Isla Verde","Year-round — urban beaches, warm Caribbean water."),
("san-juan","🏰","Viejo San Juan","Year-round — pastel colonial streets, El Morro fortress, UNESCO."),
("san-juan","🍹","Piña colada & cuisine","Year-round — birthplace of piña colada, mofongo, lechón."),
("san-juan","💰","Budget","May–Nov — hurricane season but prices –30%, fewer tourists."),

("nassau","🏖️","Cable Beach & Paradise Island","Nov–Apr — powdery white sand, Atlantis resort."),
("nassau","🐷","Exuma swimming pigs","Year-round — boat trip to Big Major Cay, iconic experience."),
("nassau","🤿","Diving & sharks","Year-round — shark feeding, blue holes, coral reefs."),
("nassau","🍽️","Conch salad & Fish Fry","Year-round — fresh conch, Arawak Cay fish shacks."),

("turks-et-caicos","🏖️","Grace Bay Beach","Year-round — consistently ranked world's #1 beach."),
("turks-et-caicos","🤿","Barrier reef diving","Year-round — 3rd largest reef, wall dives, whales (Jan–Apr)."),
("turks-et-caicos","🦩","Flamingo reserve","Year-round — North Caicos, wild flamingos, mangroves."),
("turks-et-caicos","💰","Budget","May–Nov — off-season, rates –40%, still beautiful weather."),

("granada-nicaragua","🏛️","Colonial architecture","Nov–Apr — colorful churches, calesas, Calle La Calzada."),
("granada-nicaragua","🌋","Masaya Volcano","Year-round — active lava crater, night visits, 30 min away."),
("granada-nicaragua","🏝️","Las Isletas","Nov–Apr — kayaking among 365 volcanic islets on Lake Nicaragua."),
("granada-nicaragua","💰","Budget","Nov–Apr — dry season, one of Central America's cheapest."),

("guanajuato","🏘️","Callejones & colorful houses","Oct–May — hillside painted houses, underground tunnels."),
("guanajuato","🎭","Festival Cervantino","Oct — international arts festival, theater, music, street performances."),
("guanajuato","🏛️","Mummies & mines","Year-round — Mummy Museum, La Valenciana silver mine."),
("guanajuato","💰","Budget","Jun–Sep — rainy but prices –30%, university town atmosphere."),

("san-cristobal","🌿","Cloud forest","Nov–Mar — misty pine-oak forests, orchids, birding."),
("san-cristobal","🏛️","Tzotzil & Tzeltal culture","Year-round — indigenous villages, San Juan Chamula church."),
("san-cristobal","🏘️","Colonial center","Year-round — cobblestones, Santo Domingo church, amber market."),
("san-cristobal","☕","Chiapas cacao & coffee","Nov–Apr — coffee plantations, chocolate workshops."),

("dominique","♨️","Boiling Lake","Year-round — world's 2nd largest hot lake, 6h trek."),
("dominique","🤿","Champagne Reef","Year-round — volcanic bubbles underwater, snorkeling."),
("dominique","🌿","Rainforest & waterfalls","Year-round — Morne Trois Pitons UNESCO, Trafalgar Falls."),
("dominique","🐋","Resident sperm whales","Nov–Mar — year-round population, whale watching."),

("bonaire","🤿","Shore diving","Year-round — 80+ numbered dive sites directly from shore."),
("bonaire","🦩","Flamingos","Year-round — wild flamingo colonies, salt pans."),
("bonaire","🏄","Lac Bay windsurfing","Year-round — flat lagoon, consistent trade winds."),
("bonaire","💰","Budget","Sep–Nov — off-season, cheaper flights and accommodation."),

("grenadines","⛵","Island-to-island sailing","Dec–May — trade winds, secluded anchorages, crystal water."),
("grenadines","🐢","Tobago Cays","Year-round — marine park, turtles, white sand, gin-clear water."),
("grenadines","🤿","Snorkeling & reefs","Year-round — pristine reefs, tropical fish, Mustique, Bequia."),
("grenadines","💰","Budget","Jun–Nov — hurricane season but prices –50%, quiet islands."),

("roatan","🤿","Mesoamerican Barrier Reef","Year-round — world's 2nd largest reef, easy shore diving."),
("roatan","🏖️","West Bay Beach","Dec–Apr — white sand, palm trees, turquoise water."),
("roatan","🌿","Gumbalimba Park","Year-round — monkeys, sloths, canopy zip-line, botanical garden."),
("roatan","💰","Budget","May–Nov — rainy season but dive prices –30%, quieter."),

("sal","🏖️","Santa Maria beaches","Year-round — 8 km of golden sand, turquoise Atlantic."),
("sal","🏄","Windsurfing & kite","Nov–Jun — strong trade winds, Kite Beach, Ponta Preta."),
("sal","🧂","Pedra de Lume salt pans","Year-round — volcanic crater salt lake, floating like Dead Sea."),
("sal","🐢","Sea turtles","Jul–Oct — loggerhead turtle nesting, guided night walks."),

# ── USA ──
("denver","🏔️","Rocky Mountains","Jun–Sep — Rocky Mountain NP, Trail Ridge Road, alpine tundra."),
("denver","🍺","Craft breweries","Year-round — 100+ breweries, RiNo district, Great Divide."),
("denver","⛷️","Skiing 2h away","Dec–Apr — Breckenridge, Keystone, Vail accessible as day trips."),
("denver","🎵","Art & Red Rocks","May–Oct — Red Rocks amphitheater, Denver Art Museum, LoDo."),

("nashville","🎵","Honky tonks & country","Year-round — Broadway neon, live music every night."),
("nashville","🍗","Hot chicken & BBQ","Year-round — Prince's Hot Chicken, Martin's BBQ, meat-and-three."),
("nashville","🎤","Live music & Ryman","Year-round — Ryman Auditorium, Grand Ole Opry, Bluebird Café."),
("nashville","💰","Budget","Jan–Mar — off-season, hotel prices –30%, no festival crowds."),

("la-nouvelle-orleans","🎷","Jazz & Bourbon Street","Year-round — live jazz clubs, Preservation Hall, street music."),
("la-nouvelle-orleans","🎭","Mardi Gras","Feb–Mar — parades, floats, beads, world's biggest party."),
("la-nouvelle-orleans","🍽️","Cajun & Creole cuisine","Year-round — gumbo, crawfish, beignets, po' boys."),
("la-nouvelle-orleans","🏛️","French Quarter","Year-round — wrought-iron balconies, Jackson Square, cemeteries."),

("savannah","🌳","Squares & live oaks","Mar–May — 22 garden squares, Spanish moss, azaleas."),
("savannah","🏛️","Historic District","Year-round — America's largest historic district, antebellum mansions."),
("savannah","🍽️","Low Country cuisine","Year-round — shrimp and grits, she-crab soup, pecan pie."),
("savannah","💰","Budget","Jan–Feb — mild winter, cheapest hotels, peaceful squares."),

("savannah-ga","🌳","Squares & Spanish moss","Mar–May — 22 historic squares draped in moss, azaleas."),
("savannah-ga","🏛️","Largest US historic district","Year-round — Forsyth Park, antebellum architecture, River Street."),
("savannah-ga","🍽️","Southern cuisine","Year-round — fried green tomatoes, shrimp and grits, pralines."),
("savannah-ga","👻","Haunted Savannah","Year-round — ghost tours, one of America's most haunted cities."),

("charleston","🏛️","Historic District & Rainbow Row","Mar–May — pastel houses, Battery promenade, cobblestones."),
("charleston","🍽️","Low Country cuisine","Year-round — she-crab soup, shrimp and grits, Husk, FIG."),
("charleston","🏖️","Folly & Sullivan's beaches","May–Sep — local surf beaches, Morris Island lighthouse."),
("charleston","🎭","Spoleto Festival","May–Jun — international performing arts, 17 days."),

("honolulu","🏖️","Waikiki Beach","Year-round — iconic crescent beach, warm Pacific, 26°C water."),
("honolulu","🌋","Diamond Head","Year-round — volcanic crater hike, panoramic Oahu views."),
("honolulu","🏄","North Shore surfing","Nov–Feb — Pipeline, Sunset Beach, monster winter swells."),
("honolulu","🌺","Hawaiian culture","Year-round — hula, lei-making, luau, Pearl Harbor memorial."),

("austin","🎵","Live Music Capital","Year-round — 6th Street, SXSW (Mar), Austin City Limits (Oct)."),
("austin","🍖","Texas BBQ","Year-round — Franklin Barbecue, brisket, live oak smokers."),
("austin","🦇","Congress Bridge bats","Mar–Oct — 1.5 million bats at sunset, world's largest urban colony."),
("austin","🏊","Barton Springs Pool","Apr–Oct — natural spring-fed pool, 20°C year-round."),

("san-diego","🏖️","Mission & Pacific Beach","Year-round — surfing, boardwalk, year-round 20–25°C."),
("san-diego","🐼","San Diego Zoo","Year-round — world-famous zoo, 3,700+ animals, 100 acres."),
("san-diego","🌮","Fish tacos & Gaslamp","Year-round — authentic fish tacos, Gaslamp Quarter nightlife."),
("san-diego","🏛️","Balboa Park","Year-round — 17 museums, Spanish Colonial architecture, gardens."),

("portland","🍺","Craft beer & food trucks","Year-round — 70+ breweries, food cart pods, farm-to-table."),
("portland","🏔️","Columbia River Gorge","May–Oct — Multnomah Falls, hiking, windsurfing."),
("portland","📚","Powell's & indie culture","Year-round — world's largest indie bookstore, record shops."),
("portland","🌹","Rose Garden & Forest Park","May–Jun — International Rose Test Garden, 5,200-acre urban forest."),

("phoenix","🌵","Sonoran Desert","Nov–Mar — saguaro cacti, desert hikes, Camelback Mountain."),
("phoenix","⛳","Golf","Nov–Apr — 200+ courses, ideal winter 22–28°C."),
("phoenix","🏛️","Taliesin West","Oct–May — Frank Lloyd Wright's desert masterpiece, tours."),
("phoenix","💰","Budget","Jun–Sep — extreme heat but prices –50%, pools everywhere."),

("san-antonio","🏛️","The Alamo","Year-round — 1836 battle shrine, Texas history icon."),
("san-antonio","🛶","River Walk","Year-round — 24 km riverwalk, restaurants, boat tours."),
("san-antonio","🌮","Tex-Mex & Market Square","Year-round — puffy tacos, enchiladas, largest Mexican market in US."),
("san-antonio","💰","Budget","Jun–Aug — hot but prices –30%, indoor attractions."),

("sedona","🏜️","Red Rocks","Year-round — Cathedral Rock, Bell Rock, dramatic red formations."),
("sedona","🧘","Vortex & wellness","Year-round — energy vortexes, spas, yoga retreats."),
("sedona","🚗","Scenic drives","Year-round — Red Rock Scenic Byway, Oak Creek Canyon."),
("sedona","🎨","Art galleries","Year-round — Tlaquepaque Arts Village, 80+ galleries."),

("anchorage","🐻","Bear watching","Jul–Sep — Katmai NP, Brooks Falls salmon run, brown bears."),
("anchorage","🏔️","Glaciers & fjords","May–Sep — Kenai Fjords NP, glacier cruises, calving ice."),
("anchorage","🌅","Midnight sun","Jun–Jul — 22h of daylight, hiking, fishing."),
("anchorage","🐋","Marine wildlife","May–Sep — orcas, humpbacks, sea otters, Seward boat tours."),

("napa-valley","🍷","Wine tasting","Year-round — 400+ wineries, Cabernet Sauvignon, Opus One."),
("napa-valley","🎈","Hot air balloon ride","Apr–Oct — sunrise flight over vineyards, valley views."),
("napa-valley","🍽️","Michelin-starred dining","Year-round — French Laundry, farm-to-table, wine-pairing menus."),
("napa-valley","💰","Budget","Nov–Mar — crush season over, tasting fees reduced, fewer crowds."),

("jackson-hole","⛷️","Jackson Hole skiing","Dec–Apr — expert terrain, 1,260 m vertical, Corbet's Couloir."),
("jackson-hole","🏔️","Grand Teton & Yellowstone","Jun–Sep — 2 iconic parks, geysers, wildlife, alpine scenery."),
("jackson-hole","🚣","Snake River rafting","Jun–Aug — scenic float or whitewater, bald eagles, moose."),
("jackson-hole","💰","Budget","Apr–May or Oct–Nov — shoulder seasons, prices –40%."),

("memphis","🎵","Beale Street & blues","Year-round — neon-lit blues clubs, live music every night."),
("memphis","🎸","Graceland & Sun Studio","Year-round — Elvis mansion, birthplace of rock 'n' roll."),
("memphis","🍖","Memphis BBQ","Year-round — dry-rub ribs, pulled pork, Central BBQ, Rendezvous."),
("memphis","🏛️","National Civil Rights Museum","Year-round — Lorraine Motel, MLK Jr. assassination site."),

("maui","🌴","Road to Hana","Year-round — 64 bridges, 600 curves, waterfalls, bamboo forests."),
("maui","🐋","Humpback whales","Dec–Apr — 10,000+ whales migrate, boat tours from Lahaina."),
("maui","🌋","Haleakalā","Year-round — sunrise above the clouds at 3,055 m, lunar crater."),
("maui","🏄","Surfing & beaches","Year-round — Ho'okipa, Ka'anapali, warm water all year."),
]
