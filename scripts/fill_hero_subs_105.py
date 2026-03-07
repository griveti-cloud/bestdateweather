#!/usr/bin/env python3
"""Fill hero_sub_fr/en/es for the 105 new destinations."""

HERO_SUBS = {
    # ── ALGÉRIE ──
    "alger": {
        "fr": "Alger, la Blanche de Méditerranée — vieille ville ottomane, corniche atlantique et art de vivre algérien entre mer et collines.",
        "en": "Algiers, the White City of the Mediterranean — Ottoman old town, seafront corniche and Algerian way of life between sea and hills.",
        "es": "Argel, la Ciudad Blanca del Mediterráneo — casco antiguo otomano, cornisa costera y arte de vivir argelino entre mar y colinas."
    },
    "oran": {
        "fr": "Oran, deuxième ville d'Algérie — architecture andalouse et française, ambiance musicale raï et façade maritime sur la Méditerranée.",
        "en": "Oran, Algeria's second city — Andalusian and French architecture, raï music scene and Mediterranean seafront.",
        "es": "Orán, segunda ciudad de Argelia — arquitectura andaluza y francesa, escena musical raï y fachada marítima mediterránea."
    },
    "constantine": {
        "fr": "Constantine, la ville des ponts suspendus — cité antique perchée sur des gorges vertigineuses, carrefour du nord-est algérien.",
        "en": "Constantine, city of suspended bridges — ancient city perched above dramatic gorges, crossroads of northeastern Algeria.",
        "es": "Constantina, la ciudad de los puentes colgantes — ciudad antigua sobre gargantas dramáticas, cruce de caminos del noreste argelino."
    },
    "annaba": {
        "fr": "Annaba, joyau côtier de l'est algérien — plages de sable fin, vestiges romains d'Hippone et douceur de vivre méditerranéenne.",
        "en": "Annaba, coastal gem of eastern Algeria — sandy beaches, Roman ruins of Hippo Regius and Mediterranean ease.",
        "es": "Annaba, joya costera del este argelino — playas de arena fina, ruinas romanas de Hipona y dulzura de vida mediterránea."
    },
    "batna": {
        "fr": "Batna, porte des Aurès — carrefour des hautes plaines algériennes aux portes du massif montagneux berbère et des gorges de Tighanimine.",
        "en": "Batna, gateway to the Aurès — crossroads of the Algerian high plains at the edge of the Berber mountains and Tighanimine gorges.",
        "es": "Batna, puerta del Aurès — cruce de las altas llanuras argelinas a las puertas del macizo bereber y los barrancos de Tighanimine."
    },
    # ── UK ──
    "bath": {
        "fr": "Bath, cité romaine et géorgienne — thermes antiques, architecture Regency et campagne anglaise à deux heures de Londres.",
        "en": "Bath, Roman and Georgian gem — ancient thermal baths, Regency architecture and English countryside two hours from London.",
        "es": "Bath, ciudad romana y georgiana — termas antiguas, arquitectura Regency y campiña inglesa a dos horas de Londres."
    },
    "cotswolds": {
        "fr": "Les Cotswolds, quintessence de la campagne anglaise — villages en pierre dorée, jardins fleuris et chemins de randonnée bucoliques.",
        "en": "The Cotswolds, quintessential English countryside — honey-stone villages, flowering gardens and bucolic walking trails.",
        "es": "Los Cotswolds, quintaesencia del campo inglés — pueblos de piedra dorada, jardines floridos y rutas de senderismo bucólicas."
    },
    "lake-district": {
        "fr": "Le Lake District, paysages romantiques d'Angleterre — lacs glaciaires, sommets verdoyants et villages de pêcheurs au cœur des fells.",
        "en": "The Lake District, England's romantic landscape — glacial lakes, green peaks and fishing villages in the heart of the fells.",
        "es": "El Lake District, paisajes románticos de Inglaterra — lagos glaciares, cumbres verdes y pueblos de pescadores en el corazón de los fells."
    },
    "isle-of-skye": {
        "fr": "L'île de Skye, joyau des Highlands écossais — falaises de basalte, châteaux en ruine et lumières magiques sur les Cuillins.",
        "en": "Isle of Skye, jewel of the Scottish Highlands — basalt cliffs, ruined castles and magical light over the Cuillin mountains.",
        "es": "La isla de Skye, joya de las Highlands escocesas — acantilados de basalto, castillos en ruinas y luz mágica sobre los Cuillins."
    },
    "york": {
        "fr": "York, deux mille ans d'histoire anglaise — remparts médiévaux, cathédrale gothique et musées vikings au cœur du Yorkshire.",
        "en": "York, two thousand years of English history — medieval walls, Gothic minster and Viking museums in the heart of Yorkshire.",
        "es": "York, dos mil años de historia inglesa — murallas medievales, catedral gótica y museos vikingos en el corazón de Yorkshire."
    },
    # ── EUROPE CENTRALE / ALPES ──
    "salzburg": {
        "fr": "Salzburg, ville de Mozart et des Alpes autrichiennes — vieille ville baroque au bord de la Salzach, festivals de musique et forteresse imprenable.",
        "en": "Salzburg, Mozart's city in the Austrian Alps — Baroque old town along the Salzach, music festivals and imposing fortress.",
        "es": "Salzburgo, la ciudad de Mozart en los Alpes austríacos — casco antiguo barroco a orillas del Salzach, festivales de música y fortaleza imponente."
    },
    "interlaken": {
        "fr": "Interlaken, capitale de l'aventure alpine — entre lacs de Thoune et de Brienz, avec l'Eiger en toile de fond et sports extrêmes toute l'année.",
        "en": "Interlaken, alpine adventure capital — between Lakes Thun and Brienz, with the Eiger as backdrop and extreme sports year-round.",
        "es": "Interlaken, capital de la aventura alpina — entre los lagos Thun y Brienz, con el Eiger de fondo y deportes extremos todo el año."
    },
    "lucerne": {
        "fr": "Lucerne, perle de la Suisse centrale — pont de la Chapelle médiéval, lac des Quatre-Cantons et vieux quartier impeccablement préservé.",
        "en": "Lucerne, pearl of central Switzerland — medieval Chapel Bridge, Lake Lucerne and an impeccably preserved old town.",
        "es": "Lucerna, perla de la Suiza central — puente de la Capilla medieval, lago de los Cuatro Cantones y casco antiguo impecablemente conservado."
    },
    "cologne": {
        "fr": "Cologne, métropole rhénane — cathédrale gothique classée UNESCO, art contemporain et brasseries traditionnelles sur les rives du Rhin.",
        "en": "Cologne, Rhine metropolis — UNESCO Gothic cathedral, contemporary art and traditional breweries along the Rhine.",
        "es": "Colonia, metrópolis renana — catedral gótica declarada Patrimonio UNESCO, arte contemporáneo y cervecerías tradicionales a orillas del Rin."
    },
    "dresde": {
        "fr": "Dresde, Florence de l'Elbe — Zwinger baroque, galerie de maîtres anciens et renouveau culturel sur les rives de la Saxe.",
        "en": "Dresden, Florence of the Elbe — Baroque Zwinger, Old Masters Gallery and cultural renaissance along the Saxony riverfront.",
        "es": "Dresde, la Florencia del Elba — Zwinger barroco, Galería de los Maestros Antiguos y renacimiento cultural a orillas del Sajonia."
    },
    "alcudia": {
        "fr": "Alcúdia, Majorque préservée — vieille ville médiévale, baie aux eaux turquoise et dunes naturelles loin de l'agitation du sud.",
        "en": "Alcúdia, unspoilt Mallorca — medieval walled town, turquoise bay and natural dunes far from the southern crowds.",
        "es": "Alcúdia, Mallorca preservada — ciudad amurallada medieval, bahía de aguas turquesas y dunas naturales lejos del bullicio del sur."
    },
    # ── JAPON ──
    "fukuoka": {
        "fr": "Fukuoka, capitale du ramen et de Kyushu — gastronomie réputée, château historique et accès facile à la Corée du Sud par ferry.",
        "en": "Fukuoka, ramen capital of Kyushu — renowned food scene, historic castle and easy ferry connections to South Korea.",
        "es": "Fukuoka, capital del ramen y de Kyushu — reconocida gastronomía, castillo histórico y fácil acceso a Corea del Sur en ferry."
    },
    "kanazawa": {
        "fr": "Kanazawa, Kyoto sans les touristes — jardins Kenroku-en parmi les plus beaux du Japon, quartiers geisha et artisanat d'or.",
        "en": "Kanazawa, Kyoto without the crowds — Kenroku-en among Japan's finest gardens, geisha districts and gold leaf crafts.",
        "es": "Kanazawa, el Kioto sin turistas — jardín Kenroku-en entre los más bellos de Japón, barrios geisha y artesanía en oro."
    },
    "hakone": {
        "fr": "Hakone, sanctuaire du mont Fuji — ryokans avec onsen, vue emblématique sur le Fuji par temps clair et lac Ashi en torii flottant.",
        "en": "Hakone, Mount Fuji's sanctuary — onsen ryokans, iconic Fuji views on clear days and Lake Ashi with its floating torii.",
        "es": "Hakone, santuario del monte Fuji — ryokans con onsen, vistas icónicas del Fuji en días despejados y lago Ashi con su torii flotante."
    },
    "nikko": {
        "fr": "Nikko, site UNESCO entre forêts et cascades — sanctuaires shintoïstes dorés, gorges de Kegon et fraîcheur montagnarde proche de Tokyo.",
        "en": "Nikko, UNESCO site among forests and waterfalls — gilded Shinto shrines, Kegon gorge and cool mountain air near Tokyo.",
        "es": "Nikko, patrimonio UNESCO entre bosques y cascadas — santuarios sintoístas dorados, hoz de Kegon y frescor montañoso cerca de Tokio."
    },
    "nagoya": {
        "fr": "Nagoya, capitale industrielle du Japon central — château reconstruit, gastronomie unique et musées de l'automobile et de la céramique.",
        "en": "Nagoya, industrial capital of central Japan — reconstructed castle, unique local cuisine and museums of automobile and ceramics.",
        "es": "Nagoya, capital industrial del Japón central — castillo reconstruido, gastronomía única y museos de automoción y cerámica."
    },
    # ── CHINE ──
    "hangzhou": {
        "fr": "Hangzhou, paradis au bord du lac de l'Ouest — jardins classiques, temples bouddhistes et théiers en terrasses dans la brume.",
        "en": "Hangzhou, paradise on West Lake — classical gardens, Buddhist temples and terraced tea plantations in the mist.",
        "es": "Hangzhou, paraíso a orillas del Lago del Oeste — jardines clásicos, templos budistas y plantaciones de té en terraza entre la bruma."
    },
    "suzhou": {
        "fr": "Suzhou, ville des jardins impériaux — jardins classiques chinois classés UNESCO, canaux et soierie brodée millénaire.",
        "en": "Suzhou, city of imperial gardens — UNESCO classical Chinese gardens, canals and thousand-year-old embroidered silk.",
        "es": "Suzhou, ciudad de los jardines imperiales — jardines clásicos chinos declarados Patrimonio UNESCO, canales y seda bordada milenaria."
    },
    "kunming": {
        "fr": "Kunming, cité du printemps éternel — altitude modérée qui garantit un climat doux toute l'année, porte sur le Yunnan et le Sud-Est asiatique.",
        "en": "Kunming, city of eternal spring — moderate altitude guarantees mild weather year-round, gateway to Yunnan and Southeast Asia.",
        "es": "Kunming, ciudad de la primavera eterna — altitud moderada que garantiza clima suave todo el año, puerta de Yunnan y el Sudeste Asiático."
    },
    "qingdao": {
        "fr": "Qingdao, Méditerranée de Chine — architecture allemande coloniale, plages de sable et festival de bière international chaque août.",
        "en": "Qingdao, China's Mediterranean — colonial German architecture, sandy beaches and international beer festival every August.",
        "es": "Qingdao, el Mediterráneo de China — arquitectura colonial alemana, playas de arena y festival internacional de cerveza cada agosto."
    },
    "harbin": {
        "fr": "Harbin, capitale de glace et de neige — festival de sculptures de glace mondialement connu, architecture russe et hivers sibériens spectaculaires.",
        "en": "Harbin, ice and snow capital — world-famous ice sculpture festival, Russian architecture and spectacular Siberian winters.",
        "es": "Harbin, capital del hielo y la nieve — mundialmente famoso festival de esculturas de hielo, arquitectura rusa e inviernos siberianos espectaculares."
    },
    "chongqing": {
        "fr": "Chongqing, mégalopole des brumes — ville de montagne sur le Yangtsé, gastronomie hot-pot et accès aux Trois Gorges.",
        "en": "Chongqing, misty megacity — mountain city on the Yangtze, hot-pot gastronomy and gateway to the Three Gorges.",
        "es": "Chongqing, megaciudad entre brumas — ciudad montañosa en el Yangtsé, gastronomía hot-pot y acceso a las Tres Gargantas."
    },
    # ── INDE ──
    "amritsar": {
        "fr": "Amritsar, cœur spirituel du Penjab — Temple d'Or des Sikhs, cérémonies du coucher de soleil à Wagah et cuisine la plus généreuse d'Inde.",
        "en": "Amritsar, spiritual heart of Punjab — Sikh Golden Temple, Wagah border sunset ceremony and India's most generous cuisine.",
        "es": "Amritsar, corazón espiritual del Punjab — Templo Dorado sij, ceremonia del atardecer en Wagah y la gastronomía más generosa de India."
    },
    "jodhpur": {
        "fr": "Jodhpur, la ville bleue du Rajasthan — fort Mehrangarh dominant 5000 maisons peintes en indigo, désert du Thar à portée.",
        "en": "Jodhpur, Rajasthan's blue city — Mehrangarh Fort towering over 5,000 indigo-painted houses, with the Thar Desert within reach.",
        "es": "Jodhpur, la ciudad azul de Rajastán — fuerte Mehrangarh dominando 5.000 casas pintadas de añil, con el desierto de Thar al alcance."
    },
    "jaisalmer": {
        "fr": "Jaisalmer, forteresse dorée du désert — cité médiévale en grès jaune au cœur du Thar, nuits sous les étoiles et dunes à dos de chameau.",
        "en": "Jaisalmer, golden desert fortress — medieval yellow sandstone city in the heart of the Thar, starlit nights and camel dune rides.",
        "es": "Jaisalmer, fortaleza dorada del desierto — ciudad medieval de arenisca amarilla en el corazón del Thar, noches estrelladas y excursiones en camello."
    },
    "rishikesh": {
        "fr": "Rishikesh, capitale mondiale du yoga — ashrams au bord du Gange, rafting en eaux vives et portes de l'Himalaya à 24 heures de Delhi.",
        "en": "Rishikesh, world capital of yoga — ashrams along the Ganges, white-water rafting and Himalayan foothills a day from Delhi.",
        "es": "Rishikesh, capital mundial del yoga — ashrams a orillas del Ganges, rafting en aguas bravas y estribaciones del Himalaya a un día de Delhi."
    },
    "darjeeling": {
        "fr": "Darjeeling, paradis du thé en altitude — plantations verdoyantes à 2100m, vue sur le Kangchenjunga et train jouet classé UNESCO.",
        "en": "Darjeeling, high-altitude tea paradise — lush plantations at 2,100m, views of Kangchenjunga and UNESCO toy train railway.",
        "es": "Darjeeling, paraíso del té en altura — exuberantes plantaciones a 2.100m, vistas al Kangchenjunga y tren de juguete declarado Patrimonio UNESCO."
    },
    "mysore": {
        "fr": "Mysore, ville des maharajas — palais illuminé le dimanche soir, marché aux épices et capitale de la soie du Karnataka.",
        "en": "Mysore, city of maharajas — palace lit up on Sunday evenings, spice market and silk capital of Karnataka.",
        "es": "Mysore, ciudad de los maharajás — palacio iluminado los domingos por la noche, mercado de especias y capital de la seda de Karnataka."
    },
    "shimla": {
        "fr": "Shimla, ancienne capitale estivale des Indes britanniques — architecture coloniale en altitude, air frais himalayan et vues sur les contreforts.",
        "en": "Shimla, former summer capital of British India — high-altitude colonial architecture, Himalayan fresh air and views over the foothills.",
        "es": "Shimla, antigua capital de verano de la India británica — arquitectura colonial en altura, aire fresco himalayo y vistas sobre las estribaciones."
    },
    # ── ASIE DU SUD-EST ──
    "vientiane": {
        "fr": "Vientiane, capitale la plus tranquille d'Asie — temples dorés au bord du Mékong, pace de vie nonchalante et gastronomie laotienne.",
        "en": "Vientiane, Asia's most laid-back capital — golden temples on the Mekong, unhurried pace and Laotian gastronomy.",
        "es": "Vientiane, la capital más tranquila de Asia — templos dorados a orillas del Mekong, ritmo de vida pausado y gastronomía laosiana."
    },
    "hua-hin": {
        "fr": "Hua Hin, station balnéaire royale de Thaïlande — plages calmes à 3h de Bangkok, golf, fruits de mer et marché nocturne animé.",
        "en": "Hua Hin, Thailand's royal beach resort — calm beaches 3 hours from Bangkok, golf courses, seafood and lively night market.",
        "es": "Hua Hin, balneario real de Tailandia — playas tranquilas a 3 horas de Bangkok, golf, mariscos y animado mercado nocturno."
    },
    "koh-chang": {
        "fr": "Koh Chang, deuxième plus grande île de Thaïlande — forêt tropicale jusqu'à la mer, plages peu fréquentées et plongée sur récifs intacts.",
        "en": "Koh Chang, Thailand's second largest island — jungle to the sea, uncrowded beaches and diving on pristine reefs.",
        "es": "Koh Chang, segunda isla más grande de Tailandia — selva hasta el mar, playas tranquilas y buceo en arrecifes prístinos."
    },
    # ── CAUCASE ──
    "yerevan": {
        "fr": "Erevan, ville rose au pied de l'Ararat — architecture soviétique et cafés branchés, vignobles millénaires et vue imprenable sur le mont sacré.",
        "en": "Yerevan, pink city at the foot of Ararat — Soviet architecture and trendy cafés, ancient vineyards and unmissable views of the sacred mountain.",
        "es": "Ereván, ciudad rosada al pie del Ararat — arquitectura soviética y cafés modernos, viñedos milenarios y vistas impresionantes de la montaña sagrada."
    },
    "baku": {
        "fr": "Bakou, carrefour du pétrole et de la modernité — vieille ville icheri sheher classée UNESCO, flammes architecturales et Caspienne à portée.",
        "en": "Baku, crossroads of oil and modernity — UNESCO-listed Icheri Sheher old city, Flame Towers and the Caspian Sea at its doorstep.",
        "es": "Bakú, cruce entre petróleo y modernidad — casco antiguo Icheri Sheher declarado Patrimonio UNESCO, Torres Llama y el Caspio al alcance."
    },
    # ── MOYEN-ORIENT ──
    "amman": {
        "fr": "Amman, capitale de la Jordanie — cité sur sept collines, citadelle antique, gastronomie levantine et point de départ pour Pétra et Wadi Rum.",
        "en": "Amman, Jordan's capital — city on seven hills, ancient citadel, Levantine gastronomy and base for Petra and Wadi Rum.",
        "es": "Ammán, capital de Jordania — ciudad sobre siete colinas, ciudadela antigua, gastronomía levantina y base para Petra y Wadi Rum."
    },
    "fujairah": {
        "fr": "Fujairah, côte est des Émirats — seul émirat sur le golfe d'Oman, eaux claires pour la plongée et forteresse historique sur fond de montagnes.",
        "en": "Fujairah, the UAE's east coast — the only emirate on the Gulf of Oman, clear waters for diving and historic fort against a mountain backdrop.",
        "es": "Fujairah, costa este de los Emiratos — único emirato en el golfo de Omán, aguas claras para buceo y fortaleza histórica ante un telón de montañas."
    },
    # ── AFRIQUE DE L'OUEST ──
    "libreville": {
        "fr": "Libreville, capitale du Gabon atlantique — plages de sable blond, mangroves et porte d'entrée vers les parcs à gorilles du pays le plus forestier d'Afrique.",
        "en": "Libreville, capital of Atlantic Gabon — sandy beaches, mangroves and gateway to gorilla parks in Africa's most forested country.",
        "es": "Libreville, capital del Gabón atlántico — playas de arena blanca, manglares y puerta de entrada a los parques de gorilas del país más forestal de África."
    },
    "banjul": {
        "fr": "Banjul, destination hivernale des Britanniques — plages sur l'Atlantique, observation des oiseaux le long du Gambie et hospitalité réputée.",
        "en": "Banjul, British winter favourite — Atlantic beaches, birdwatching along the Gambia River and renowned local hospitality.",
        "es": "Banjul, destino invernal de los británicos — playas atlánticas, observación de aves a lo largo del río Gambia y reconocida hospitalidad local."
    },
    "abuja": {
        "fr": "Abuja, capitale planifiée du Nigeria — ville moderne en savane, Aso Rock monumental et effervescence culturelle de la plus grande économie d'Afrique.",
        "en": "Abuja, Nigeria's planned capital — modern city in the savannah, monumental Aso Rock and cultural energy of Africa's largest economy.",
        "es": "Abuya, capital planificada de Nigeria — ciudad moderna en sabana, monumental Aso Rock y efervescencia cultural de la mayor economía de África."
    },
    "kumasi": {
        "fr": "Kumasi, capitale de l'empire Ashanti — marché Kejetia parmi les plus grands d'Afrique, artisanat en tissu kente et palais royal en pleine forêt tropicale.",
        "en": "Kumasi, capital of the Ashanti Empire — Kejetia market among Africa's largest, kente cloth crafts and royal palace in the tropical forest.",
        "es": "Kumasi, capital del Imperio Ashanti — mercado Kejetia entre los más grandes de África, artesanía en tela kente y palacio real en plena selva tropical."
    },
    # ── AFRIQUE DE L'EST ──
    "moshi": {
        "fr": "Moshi, camp de base du Kilimandjaro — ville de marché animée au pied du toit de l'Afrique, café local et lumières matinales sur les neiges éternelles.",
        "en": "Moshi, Kilimanjaro base camp — lively market town at the foot of Africa's roof, local coffee and morning light on the eternal snows.",
        "es": "Moshi, campo base del Kilimanjaro — animado pueblo mercado al pie del techo de África, café local y luz matinal sobre las nieves eternas."
    },
    "entebbe": {
        "fr": "Entebbe, porte du lac Victoria — ville verte en altitude, jardins botaniques, plages lacustres et accès aux gorilles des Bwindi.",
        "en": "Entebbe, gateway to Lake Victoria — green hillside town, botanical gardens, lakeside beaches and access to Bwindi gorillas.",
        "es": "Entebbe, puerta del lago Victoria — ciudad verde en altura, jardines botánicos, playas lacustres y acceso a los gorilas de Bwindi."
    },
    # ── AFRIQUE AUSTRALE ──
    "harare": {
        "fr": "Harare, capitale du Zimbabwe — ville jardin en altitude à climat tempéré, marché Mbare et point de départ pour les chutes Victoria et Hwange.",
        "en": "Harare, Zimbabwe's capital — garden city at altitude with temperate climate, Mbare market and base for Victoria Falls and Hwange.",
        "es": "Harare, capital de Zimbabue — ciudad jardín en altura con clima templado, mercado Mbare y punto de partida para las cataratas Victoria y Hwange."
    },
    "lilongwe": {
        "fr": "Lilongwe, capitale tranquille du Malawi — ville entre savanes et lac Malawi cristallin, réserves naturelles et hospitalité africaine chaleureuse.",
        "en": "Lilongwe, Malawi's quiet capital — city between savannahs and crystal-clear Lake Malawi, nature reserves and warm African hospitality.",
        "es": "Lilongwe, tranquila capital de Malaui — ciudad entre sabanas y el cristalino lago Malaui, reservas naturales y cálida hospitalidad africana."
    },
    # ── AMÉRIQUE DU SUD ──
    "cuenca-equateur": {
        "fr": "Cuenca, joyau colonial de l'Équateur — cathédrale bleue au cœur d'une ville UNESCO, artisanat en chapeau panama et altitude clémente à 2500m.",
        "en": "Cuenca, Ecuador's colonial jewel — blue cathedral in a UNESCO city, Panama hat crafts and pleasant altitude at 2,500m.",
        "es": "Cuenca, joya colonial de Ecuador — catedral azul en una ciudad Patrimonio UNESCO, artesanía en sombrero de paja toquilla y altitud amable a 2.500m."
    },
    "cordoba-argentine": {
        "fr": "Córdoba, deuxième ville d'Argentine — jésuitisme colonial classé UNESCO, sierras verdoyantes en toile de fond et vie estudiantine animée.",
        "en": "Córdoba, Argentina's second city — UNESCO Jesuit heritage, green sierras as backdrop and vibrant student life.",
        "es": "Córdoba, segunda ciudad de Argentina — patrimonio jesuita declarado UNESCO, sierras verdes de telón de fondo y animada vida universitaria."
    },
    "chapada-diamantina": {
        "fr": "Chapada Diamantina, paradis des randonneurs — tabletops de grès, cascades dissimulées et grottes à diamants au cœur du Bahia tropical.",
        "en": "Chapada Diamantina, hikers' paradise — sandstone tabletops, hidden waterfalls and diamond caves in the heart of tropical Bahia.",
        "es": "Chapada Diamantina, paraíso de los senderistas — mesetas de arenisca, cascadas escondidas y cuevas de diamantes en el corazón del Bahia tropical."
    },
    "porto-alegre": {
        "fr": "Porto Alegre, capitale gaúcha du Brésil du Sud — culture européenne distincte, gastronomie churrasco et Rio Guaíba aux couchers de soleil spectaculaires.",
        "en": "Porto Alegre, gaucho capital of southern Brazil — distinct European culture, churrasco gastronomy and spectacular sunsets over the Guaíba River.",
        "es": "Porto Alegre, capital gaucha del sur de Brasil — cultura europea diferenciada, gastronomía churrasco y espectaculares atardeceres sobre el río Guaíba."
    },
    "punta-del-este": {
        "fr": "Punta del Este, Saint-Tropez de l'Atlantique Sud — plages d'été glamour, marina internationale et art contemporain au soleil uruguayen.",
        "en": "Punta del Este, Saint-Tropez of the South Atlantic — glamorous summer beaches, international marina and contemporary art under the Uruguayan sun.",
        "es": "Punta del Este, el Saint-Tropez del Atlántico Sur — glamurosas playas de verano, marina internacional y arte contemporáneo bajo el sol uruguayo."
    },
    "rosario": {
        "fr": "Rosario, ville du Che Guevara et du football argentin — Paraná en ligne d'horizon, culture du tango et gastronomie sur fond de gratte-ciels.",
        "en": "Rosario, city of Che Guevara and Argentine football — Paraná skyline, tango culture and gastronomy against a backdrop of skyscrapers.",
        "es": "Rosario, ciudad del Che Guevara y el fútbol argentino — horizonte del Paraná, cultura del tango y gastronomía ante un telón de rascacielos."
    },
    "belem": {
        "fr": "Belém, porte de l'Amazonie — marché Ver-o-Peso sur l'embouchure du Pará, gastronomie amazonienne unique et architecture coloniale portuguesa.",
        "en": "Belém, gateway to the Amazon — Ver-o-Peso market on the Pará estuary, unique Amazonian gastronomy and Portuguese colonial architecture.",
        "es": "Belém, puerta de la Amazonia — mercado Ver-o-Peso en el estuario del Pará, gastronomía amazónica única y arquitectura colonial portuguesa."
    },
    "natal-bresil": {
        "fr": "Natal, ville du soleil nordestino — dunes de sable blanc sur l'Atlantique, eaux chaudes et ciel le plus dégagé du Brésil.",
        "en": "Natal, northeastern Brazil's sun city — white sand dunes on the Atlantic, warm waters and the clearest skies in Brazil.",
        "es": "Natal, ciudad del sol del nordeste brasileño — dunas de arena blanca en el Atlántico, aguas cálidas y el cielo más despejado de Brasil."
    },
    # ── CARAÏBES ──
    "cayman-islands": {
        "fr": "Les Îles Caïmans, paradis des plongeurs et des banques — Seven Mile Beach parmi les plus belles des Caraïbes, eaux cristallines et raies apprivoisées.",
        "en": "The Cayman Islands, divers' and bankers' paradise — Seven Mile Beach among the Caribbean's finest, crystal waters and friendly stingrays.",
        "es": "Las Islas Caimán, paraíso de buceadores y banqueros — Seven Mile Beach entre las mejores del Caribe, aguas cristalinas y rayas amistosas."
    },
    "saint-thomas": {
        "fr": "Saint Thomas, perle des Îles Vierges américaines — port de croisière au charme colonial danois, plages turquoise et plongée sur épaves.",
        "en": "Saint Thomas, gem of the US Virgin Islands — cruise port with Danish colonial charm, turquoise beaches and wreck diving.",
        "es": "Saint Thomas, joya de las Islas Vírgenes de EE.UU. — puerto de cruceros con encanto colonial danés, playas turquesas y buceo en pecios."
    },
    "saint-vincent": {
        "fr": "Saint-Vincent, île volcanique des Caraïbes — jungle de la Soufrière jusqu'à la mer, pêche traditionnelle et tremplin vers les Grenadines.",
        "en": "Saint Vincent, volcanic Caribbean island — Soufrière jungle to the sea, traditional fishing and springboard to the Grenadines.",
        "es": "San Vicente, isla volcánica del Caribe — selva de la Soufrière hasta el mar, pesca tradicional y trampolín hacia las Granadinas."
    },
    "providencia": {
        "fr": "Providencia, île colombienne préservée — récif corallien parmi les mieux préservés des Caraïbes, anglais créole et accès limité garant d'authenticité.",
        "en": "Providencia, Colombia's pristine island — one of the Caribbean's best-preserved coral reefs, Creole English and limited access guaranteeing authenticity.",
        "es": "Providencia, isla colombiana prístina — uno de los arrecifes de coral mejor conservados del Caribe, inglés criollo y acceso limitado que garantiza autenticidad."
    },
    # ── USA ──
    "asheville": {
        "fr": "Asheville, capitale des arts des Appalaches — Blue Ridge Parkway, brasseries artisanales et domaine Biltmore dans la montagne de Caroline du Nord.",
        "en": "Asheville, Appalachian arts capital — Blue Ridge Parkway, craft breweries and Biltmore Estate in the North Carolina mountains.",
        "es": "Asheville, capital de las artes de los Apalaches — Blue Ridge Parkway, cervecerías artesanales y el dominio Biltmore en las montañas de Carolina del Norte."
    },
    "palm-springs": {
        "fr": "Palm Springs, oasis du désert californien — architecture moderniste du milieu du siècle, piscines turquoise et soleil 350 jours par an dans le désert de Coachella.",
        "en": "Palm Springs, Californian desert oasis — mid-century modern architecture, turquoise pools and 350 days of sunshine in the Coachella Valley.",
        "es": "Palm Springs, oasis del desierto californiano — arquitectura modernista de mediados de siglo, piscinas turquesas y 350 días de sol en el valle de Coachella."
    },
    "santa-fe": {
        "fr": "Santa Fe, capitale de l'art du Nouveau-Mexique — adobe pueblo, musées d'art amérindien et cuisine fusion mexicaine à 2100m d'altitude.",
        "en": "Santa Fe, New Mexico's art capital — adobe pueblo, Native American art museums and Mexican fusion cuisine at 7,000 feet.",
        "es": "Santa Fe, capital del arte de Nuevo México — adobe pueblo, museos de arte nativo americano y cocina fusión mexicana a 2.100m de altitud."
    },
    "lake-tahoe": {
        "fr": "Lake Tahoe, lac alpin de la Sierra Nevada — eaux d'un bleu improbable à 1900m, stations de ski réputées et randonnée estivale spectaculaire.",
        "en": "Lake Tahoe, alpine lake in the Sierra Nevada — impossibly blue waters at 6,200 feet, renowned ski resorts and spectacular summer hiking.",
        "es": "Lake Tahoe, lago alpino en la Sierra Nevada — aguas de un azul inverosímil a 1.900m, reconocidas estaciones de esquí y senderismo espectacular en verano."
    },
    "cape-cod": {
        "fr": "Cape Cod, péninsule estivale du Massachusetts — phares sur l'Atlantique, villages de pêcheurs et fruits de mer réputés depuis les pèlerins du Mayflower.",
        "en": "Cape Cod, Massachusetts summer peninsula — Atlantic lighthouses, fishing villages and renowned seafood since the Mayflower Pilgrims.",
        "es": "Cape Cod, península estival de Massachusetts — faros atlánticos, pueblos de pescadores y mariscos reconocidos desde los peregrinos del Mayflower."
    },
    "outer-banks": {
        "fr": "Outer Banks, barrière d'îles de Caroline du Nord — plages sauvages sur l'Atlantique, premier vol des frères Wright et chevaux sauvages à Corolla.",
        "en": "Outer Banks, North Carolina's barrier islands — wild Atlantic beaches, Wright Brothers first flight and wild horses at Corolla.",
        "es": "Outer Banks, islas barrera de Carolina del Norte — playas salvajes atlánticas, primer vuelo de los hermanos Wright y caballos salvajes en Corolla."
    },
    "saint-augustine": {
        "fr": "Saint Augustine, plus ancienne ville des États-Unis — fondée en 1565 par les Espagnols, fort Castillo de San Marcos et plages de Floride préservées.",
        "en": "Saint Augustine, oldest city in the United States — founded by Spain in 1565, Castillo de San Marcos fort and unspoilt Florida beaches.",
        "es": "San Agustín, ciudad más antigua de Estados Unidos — fundada por España en 1565, fuerte Castillo de San Marcos y playas preservadas de Florida."
    },
    "monterey": {
        "fr": "Monterey, perle de la côte californienne — aquarium de classe mondiale, paysages de Big Sur à portée et baleines en migration de novembre à mars.",
        "en": "Monterey, pearl of the California coast — world-class aquarium, Big Sur landscapes within reach and migrating whales from November to March.",
        "es": "Monterey, perla de la costa californiana — acuario de talla mundial, paisajes de Big Sur al alcance y ballenas migratorias de noviembre a marzo."
    },
    "santa-barbara": {
        "fr": "Santa Barbara, Riviera américaine — architecture mission espagnole, vignobles de Santa Ynez et plages entre océan et montagnes de Santa Ynez.",
        "en": "Santa Barbara, the American Riviera — Spanish mission architecture, Santa Ynez vineyards and beaches between ocean and mountains.",
        "es": "Santa Bárbara, la Riviera americana — arquitectura de misión española, viñedos de Santa Ynez y playas entre el océano y las montañas."
    },
    # ── ITALIE ──
    "procida": {
        "fr": "Procida, île secrète du golfe de Naples — maisons pastel de pêcheurs, ruelles authentiques et révélée au monde par Elsa Morante.",
        "en": "Procida, secret island of the Bay of Naples — pastel fishermen's houses, authentic alleyways and revealed to the world by Elsa Morante.",
        "es": "Procida, isla secreta del golfo de Nápoles — casas de pescadores en tonos pastel, callejones auténticos y revelada al mundo por Elsa Morante."
    },
    "matera": {
        "fr": "Matera, cité des Sassi millénaires — grottes creusées dans le tuf, une des plus anciennes villes habitées du monde et décor de films bibliques.",
        "en": "Matera, city of ancient Sassi — cave dwellings carved in tufa, one of the world's oldest inhabited cities and backdrop for Biblical films.",
        "es": "Matera, ciudad de los Sassi milenarios — viviendas excavadas en la toba, una de las ciudades habitadas más antiguas del mundo y escenario de películas bíblicas."
    },
    "alberobello": {
        "fr": "Alberobello, village des trulli des Pouilles — constructions coniques en pierre sèche classées UNESCO, vignobles Primitivo et gastronomie pugliese.",
        "en": "Alberobello, Puglia's trulli village — UNESCO dry-stone conical buildings, Primitivo vineyards and Puglian gastronomy.",
        "es": "Alberobello, pueblo de los trulli de Puglia — construcciones cónicas de piedra seca declaradas Patrimonio UNESCO, viñedos Primitivo y gastronomía pugliesa."
    },
    "tropea": {
        "fr": "Tropea, Calabre la méconnue — eaux turquoise parmi les plus belles de Méditerranée, vieille ville perchée sur falaise et oignons rouges renommés.",
        "en": "Tropea, overlooked Calabria — some of the Mediterranean's finest turquoise waters, clifftop old town and famous red onions.",
        "es": "Tropea, la Calabria desconocida — aguas turquesas entre las más bellas del Mediterráneo, casco antiguo sobre el acantilado y famosas cebollas rojas."
    },
    # ── GRÈCE ──
    "samos": {
        "fr": "Samos, île de Pythagore et du muscat grec — vignobles en terrasses, forêt vierge de montagne et détroit étroit face aux côtes turques.",
        "en": "Samos, island of Pythagoras and Greek muscat — terraced vineyards, mountain forest and narrow strait facing the Turkish coast.",
        "es": "Samos, isla de Pitágoras y el moscatel griego — viñedos en terrazas, bosque virgen de montaña y estrecho frente a las costas turcas."
    },
    "skiathos": {
        "fr": "Skiathos, île tournage de Mamma Mia — 60 plages de sable blanc sur 12km², pinèdes et vie nocturne animée dans l'archipel des Sporades.",
        "en": "Skiathos, Mamma Mia filming island — 60 white-sand beaches in 12km², pine forests and vibrant nightlife in the Sporades archipelago.",
        "es": "Skiathos, isla del rodaje de Mamma Mia — 60 playas de arena blanca en 12km², bosques de pinos y vida nocturna animada en el archipiélago de las Espóradas."
    },
    "kalamata": {
        "fr": "Kalamata, capitale des olives et du Péloponnèse — plage de galets noirs, danses de combat Tsakonikos et citadelle médiévale sur les contreforts du Taygète.",
        "en": "Kalamata, capital of olives and the Peloponnese — black pebble beach, Tsakonikos war dances and medieval citadel on the Taygetos foothills.",
        "es": "Kalamata, capital de las aceitunas y el Peloponeso — playa de guijarros negros, danzas de guerra Tsakonikos y ciudadela medieval en las estribaciones del Taigeto."
    },
    # ── MALTE ──
    "valletta": {
        "fr": "La Valette, plus petite capitale de l'UE — chevaliers de Malte, architecture baroque et co-capitale culturelle européenne 2018 sur falaises méditerranéennes.",
        "en": "Valletta, EU's smallest capital — Knights of Malta, Baroque architecture and 2018 European Capital of Culture on Mediterranean cliffs.",
        "es": "La Valeta, la capital más pequeña de la UE — caballeros de Malta, arquitectura barroca y Capital Cultural Europea 2018 sobre acantilados mediterráneos."
    },
    # ── EUROPE DU NORD/EST ──
    "aarhus": {
        "fr": "Aarhus, deuxième ville du Danemark — musée ARoS au rainbow panorama, vieux quartier Den Gamle By et festival de musique estival réputé.",
        "en": "Aarhus, Denmark's second city — ARoS museum with rainbow panorama, Den Gamle By open-air museum and renowned summer music festival.",
        "es": "Aarhus, segunda ciudad de Dinamarca — museo ARoS con panorama arcoíris, museo al aire libre Den Gamle By y reconocido festival de música estival."
    },
    "wroclaw": {
        "fr": "Wrocław, ville des 300 ponts et des gnomes — architecture germano-polonaise sur l'Oder, université baroque et marché de Noël réputé.",
        "en": "Wrocław, city of 300 bridges and gnomes — German-Polish architecture on the Oder, Baroque university and renowned Christmas market.",
        "es": "Wrocław, ciudad de los 300 puentes y los gnomos — arquitectura germanopolaca sobre el Óder, universidad barroca y reconocido mercado navideño."
    },
    # ── MALAISIE ──
    "malacca": {
        "fr": "Malacca, carrefour des civilisations — vieille ville UNESCO aux influences portugaises, hollandaises et chinoises sur le détroit du même nom.",
        "en": "Malacca, crossroads of civilisations — UNESCO old town with Portuguese, Dutch and Chinese influences on the strait of the same name.",
        "es": "Malaca, cruce de civilizaciones — casco antiguo Patrimonio UNESCO con influencias portuguesas, holandesas y chinas en el estrecho homónimo."
    },
    "kota-kinabalu": {
        "fr": "Kota Kinabalu, porte de Bornéo malaisien — mont Kinabalu en toile de fond, plongée sur récifs de Sipadan et couchers de soleil sur la mer de Chine.",
        "en": "Kota Kinabalu, gateway to Malaysian Borneo — Mount Kinabalu as backdrop, Sipadan reef diving and sunsets over the South China Sea.",
        "es": "Kota Kinabalu, puerta del Borneo malayo — monte Kinabalu de telón de fondo, buceo en los arrecifes de Sipadan y atardeceres sobre el mar del Sur de China."
    },
    # ── MEXIQUE ──
    "puerto-escondido": {
        "fr": "Puerto Escondido, capitale mondiale du surf sauvage — Pipeline mexicain, plages de pêcheurs préservées et mezcal au coucher de soleil sur l'Oaxaca.",
        "en": "Puerto Escondido, wild surf world capital — Mexican Pipeline, unspoilt fishing beaches and mezcal at sunset on the Oaxacan coast.",
        "es": "Puerto Escondido, capital mundial del surf salvaje — Pipeline mexicano, playas de pescadores preservadas y mezcal al atardecer en la costa oaxaqueña."
    },
    "san-miguel-de-allende": {
        "fr": "San Miguel de Allende, ville coloniale la plus belle du Mexique — cathédrale néogothique rose, ruelles pavées et art contemporain en altitude.",
        "en": "San Miguel de Allende, Mexico's most beautiful colonial city — pink neo-Gothic cathedral, cobbled streets and contemporary art at altitude.",
        "es": "San Miguel de Allende, la ciudad colonial más bella de México — catedral neogótica rosa, calles empedradas y arte contemporáneo en altura."
    },
    "merida": {
        "fr": "Mérida, capitale blanche du Yucatán — haciendas coloniales espagnoles, culture maya vivante et porte d'entrée pour Chichén Itzá et Uxmal.",
        "en": "Mérida, white capital of Yucatán — Spanish colonial haciendas, living Maya culture and gateway to Chichén Itzá and Uxmal.",
        "es": "Mérida, capital blanca del Yucatán — haciendas coloniales españolas, cultura maya viva y puerta de entrada a Chichén Itzá y Uxmal."
    },
    # ── VIETNAM ──
    "mui-ne": {
        "fr": "Mui Ne, capitale du kite surf de l'Asie du Sud-Est — dunes de sable rouge et blanc sur l'Atlantique de l'Orient et brises marines constantes.",
        "en": "Mui Ne, Southeast Asia's kite surfing capital — red and white sand dunes on the Orient's Atlantic and constant sea breezes.",
        "es": "Mui Ne, capital del kitesurf del Sudeste Asiático — dunas de arena roja y blanca sobre el Atlántico de Oriente y brisas marinas constantes."
    },
    "quy-nhon": {
        "fr": "Quy Nhon, perle méconnue du centre Vietnam — plages désertes, lagunes turquoise et culture cham préservée loin des circuits touristiques.",
        "en": "Quy Nhon, overlooked gem of central Vietnam — deserted beaches, turquoise lagoons and preserved Cham culture off the tourist trail.",
        "es": "Quy Nhon, joya desconocida del centro de Vietnam — playas desiertas, lagunas turquesas y cultura cham preservada fuera de los circuitos turísticos."
    },
    # ── OCÉANIE ──
    "palau": {
        "fr": "Palaos, sanctuaire marin du Pacifique — requins et raies en nombre, lac de méduses sans danger et récifs parmi les plus intacts de la planète.",
        "en": "Palau, Pacific marine sanctuary — sharks and rays in abundance, jellyfish lake with no sting and some of the world's most pristine reefs.",
        "es": "Palaos, santuario marino del Pacífico — tiburones y rayas en abundancia, lago de medusas sin peligro y arrecifes entre los más prístinos del planeta."
    },
    "bay-of-islands": {
        "fr": "Bay of Islands, berceau de la Nouvelle-Zélande — 144 îles dans le Pacifique, lieu du traité de Waitangi et navigation, plongée et dauphins.",
        "en": "Bay of Islands, birthplace of New Zealand — 144 islands in the Pacific, site of the Treaty of Waitangi and sailing, diving and dolphins.",
        "es": "Bay of Islands, cuna de Nueva Zelanda — 144 islas en el Pacífico, lugar del Tratado de Waitangi y navegación, buceo y delfines."
    },
    "ischia": {
        "fr": "Ischia, île thermale du golfe de Naples — jardins botaniques de Mortella, eaux hydrothermales et Castello Aragonese sur l'îlot face à Capri.",
        "en": "Ischia, thermal island of the Bay of Naples — Mortella botanical gardens, hydrothermal waters and Aragonese Castle on a rocky islet opposite Capri.",
        "es": "Ischia, isla termal del golfo de Nápoles — jardines botánicos de Mortella, aguas hidrotermales y Castillo Aragonés en el islote frente a Capri."
    },
    # ── ASIE CENTRALE ──
    "douchanbé": {
        "fr": "Douchanbé, capitale du Tadjikistan entre cimes et bazars — proximité du Pamir, marchés animés et renouveau architectural sur fond de montagnes.",
        "en": "Dushanbe, Tajikistan's capital between peaks and bazaars — Pamir proximity, lively markets and architectural revival against a mountain backdrop.",
        "es": "Dushambé, capital de Tayikistán entre cimas y bazares — proximidad al Pamir, mercados animados y renacimiento arquitectónico ante un telón de montañas."
    },
    "astana": {
        "fr": "Astana, capitale futuriste du Kazakhstan — architecture extravagante sur les steppes, Baiterek et Khantchaty au cœur de l'Eurasie.",
        "en": "Astana, Kazakhstan's futuristic capital — extravagant architecture on the steppes, Baiterek and Khan Shatyr at the heart of Eurasia.",
        "es": "Astana, la capital futurista de Kazajistán — arquitectura extravagante en las estepas, Baiterek y Khan Shatyr en el corazón de Eurasia."
    },
    # ── ESPAGNE ──
    "salamanque": {
        "fr": "Salamanque, cité universitaire UNESCO — grès doré du Plateresque espagnol, Plaza Mayor classée et une des plus vieilles universités d'Europe.",
        "en": "Salamanca, UNESCO university city — golden Plateresque sandstone, listed Plaza Mayor and one of Europe's oldest universities.",
        "es": "Salamanca, ciudad universitaria Patrimonio UNESCO — arenisca dorada plateresca, Plaza Mayor catalogada y una de las universidades más antiguas de Europa."
    },
    "tolede": {
        "fr": "Tolède, cité des trois cultures — cathédrale gothique et synagogues dans l'ancienne capitale de l'Espagne wisigothique, sur un méandre du Tage.",
        "en": "Toledo, city of three cultures — Gothic cathedral and synagogues in the old Visigothic capital of Spain, on a meander of the Tagus.",
        "es": "Toledo, ciudad de las tres culturas — catedral gótica y sinagogas en la antigua capital visigótica de España, en un meandro del Tajo."
    },
    # ── PORTUGAL ──
    "alentejo": {
        "fr": "L'Alentejo, tiers du Portugal préservé — plaines de chênes-lièges, vins récompensés et lumière dorée qui a inspiré peintres et poètes.",
        "en": "Alentejo, Portugal's preserved heartland — cork oak plains, award-winning wines and golden light that has inspired painters and poets.",
        "es": "El Alentejo, el tercio preservado de Portugal — llanuras de alcornoques, vinos premiados y luz dorada que ha inspirado pintores y poetas."
    },
    # ── MICROSTATES ──
    "andorre": {
        "fr": "Andorre, mini-État pyrénéen — ski à prix réduit, shopping hors-taxes et randonnée estivale à 2000m entre France et Espagne.",
        "en": "Andorra, Pyrenean mini-state — affordable skiing, duty-free shopping and summer hiking at 2,000m between France and Spain.",
        "es": "Andorra, mini-estado pirenaico — esquí a precio reducido, compras libres de impuestos y senderismo estival a 2.000m entre Francia y España."
    },
    "gibraltar": {
        "fr": "Gibraltar, rocher anglais au bout de l'Europe — macaques de Barbarie, tunnel de la Deuxième Guerre mondiale et vues sur l'Afrique par temps clair.",
        "en": "Gibraltar, British rock at Europe's tip — Barbary macaques, World War II tunnels and views of Africa on clear days.",
        "es": "Gibraltar, roca británica en el extremo de Europa — macacos de Berbería, túneles de la Segunda Guerra Mundial y vistas a África en días despejados."
    },
    # ── ITALIE SUITE ──
    "elba": {
        "fr": "L'île d'Elbe, île toscane de Napoléon — eaux cristallines sur granit, vignobles en pente douce et forteresse de l'exil du petit caporal.",
        "en": "Elba Island, Napoleon's Tuscan island — crystal waters over granite, gently sloping vineyards and the little corporal's exile fortress.",
        "es": "Isla de Elba, la isla toscana de Napoleón — aguas cristalinas sobre granito, viñedos en suave pendiente y fortaleza del exilio del pequeño cabo."
    },
    "pantelleria": {
        "fr": "Pantelleria, île volcanique entre Sicile et Tunisie — Dammusi en lave noire, câpres mondialement connues et eaux géothermales du lac Specchio di Venere.",
        "en": "Pantelleria, volcanic island between Sicily and Tunisia — black lava Dammusi houses, world-famous capers and geothermal waters of Venus's Mirror lake.",
        "es": "Pantelleria, isla volcánica entre Sicilia y Túnez — Dammusi de lava negra, alcaparras mundialmente conocidas y aguas geotermales del lago Espejo de Venus."
    },
    "poznan": {
        "fr": "Poznań, berceau de la Pologne — Stary Rynek aux façades bariolées, chèvres mécaniques de la mairie et foire internationale la plus ancienne d'Europe.",
        "en": "Poznań, cradle of Poland — Stary Rynek with colourful facades, mechanical goats of the town hall and Europe's oldest international trade fair.",
        "es": "Poznań, cuna de Polonia — Stary Rynek con fachadas coloridas, cabras mecánicas del ayuntamiento y la feria internacional más antigua de Europa."
    },
    # ── RESTE ──
    "ipoh": {
        "fr": "Ipoh, ville de la street food malaisienne — curry laksa et dim sum dans une ville coloniale britannique entourée de karsts calcaires spectaculaires.",
        "en": "Ipoh, Malaysia's street food city — curry laksa and dim sum in a British colonial town surrounded by spectacular limestone karsts.",
        "es": "Ipoh, ciudad de la comida callejera malaya — curry laksa y dim sum en una ciudad colonial británica rodeada de espectaculares karsts de caliza."
    },
    "matsuyama": {
        "fr": "Matsuyama, sanctuaire de Shikoku — château japonais originel et onsen de Dogo parmi les plus anciens du Japon, loin des circuits touristiques.",
        "en": "Matsuyama, Shikoku's sanctuary — original Japanese castle and Dogo Onsen among Japan's oldest hot springs, well off the tourist trail.",
        "es": "Matsuyama, santuario de Shikoku — castillo japonés original y onsen de Dogo entre los más antiguos de Japón, lejos de los circuitos turísticos."
    },
    "trinidad-cuba": {
        "fr": "Trinidad, joyau colonial de Cuba — Plaza Mayor classée UNESCO, musique son cubain en direct et plages de la péninsule de Ancón à 15 minutes.",
        "en": "Trinidad, Cuba's colonial jewel — UNESCO Plaza Mayor, live son cubano music and Ancón peninsula beaches 15 minutes away.",
        "es": "Trinidad, joya colonial de Cuba — Plaza Mayor declarada Patrimonio UNESCO, música son cubano en vivo y playas de la península de Ancón a 15 minutos."
    },
    "taupo": {
        "fr": "Taupo, lac volcanique de Nouvelle-Zélande — plus grand lac du pays formé par une super-éruption, saut en parachute, géysers de Wairakei et truite en abondance.",
        "en": "Taupo, New Zealand's volcanic lake — country's largest lake formed by a super-eruption, skydiving, Wairakei geysers and abundant trout fishing.",
        "es": "Taupo, lago volcánico de Nueva Zelanda — el lago más grande del país formado por una super-erupción, paracaidismo, géiseres de Wairakei y pesca de trucha."
    },
    "loreto-mexique": {
        "fr": "Loreto, oasis de la mer de Cortez — première capitale de la Basse-Californie, récifs aux raies géantes et baleine grise en hivernage de janvier à mars.",
        "en": "Loreto, oasis of the Sea of Cortez — first capital of Baja California, giant manta ray reefs and grey whale winter grounds from January to March.",
        "es": "Loreto, oasis del mar de Cortés — primera capital de Baja California, arrecifes con rayas gigantes y ballenas grises invernando de enero a marzo."
    },
}

print(f"Hero subs defined: {len(HERO_SUBS)}")

import csv, io, os, sys

DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(DIR, 'data', 'destinations.csv')

rows = list(csv.DictReader(open(CSV_PATH, encoding='utf-8-sig')))
fieldnames = list(rows[0].keys())

updated = 0
not_found = []
for row in rows:
    slug = row['slug_fr']
    if not row.get('hero_sub_fr', '').strip() and slug in HERO_SUBS:
        row['hero_sub_fr'] = HERO_SUBS[slug]['fr']
        row['hero_sub_en'] = HERO_SUBS[slug]['en']
        row['hero_sub_es'] = HERO_SUBS[slug]['es']
        updated += 1
    elif not row.get('hero_sub_fr', '').strip():
        not_found.append(slug)

buf = io.StringIO()
w = csv.DictWriter(buf, fieldnames=fieldnames)
w.writeheader()
w.writerows(rows)
open(CSV_PATH, 'w', encoding='utf-8', newline='').write(buf.getvalue())

print(f"Updated: {updated}")
print(f"Still empty (no hero_sub defined): {len(not_found)}")
if not_found:
    print(f"  {not_found}")
