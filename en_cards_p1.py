#!/usr/bin/env python3
"""All 799 EN cards written manually. Part 1: Europe."""

CARDS = [
# ── FRANCE ──
("annecy","🏊","Lake Annecy","Jun–Sep — swimming in one of Europe's purest lakes, Talloires beaches."),
("annecy","🥾","Semnoz & Tournette","May–Oct — panoramic trails overlooking the lake, trailhead from old town."),
("annecy","🏰","Old town & Palais de l'Île","Year-round — cobblestone lanes, canals, Sunday market."),
("annecy","🚴","Lakeside greenway","Apr–Oct — 40 km bike path along the lake, easy rentals."),
("annecy","🧀","Savoyard cuisine","Oct–Mar — tartiflette, fondue, raclette in mountain farm-inns."),

("toulouse","🚀","Cité de l'Espace","Year-round — Europe's only space theme park, Ariane 5 replica, planetarium."),
("toulouse","🍽️","Southwest French cuisine","Year-round — cassoulet, foie gras, Victor Hugo covered markets."),
("toulouse","🏞️","Canal du Midi","Apr–Oct — cruise or cycle along the UNESCO canal, locks and plane trees."),
("toulouse","🌹","Pink city & Capitole","Year-round — Place du Capitole, Saint-Sernin basilica, Jacobins convent."),
("toulouse","✈️","Airbus factory tour","Year-round — A380 assembly line, Aeroscopia museum, aviation behind-the-scenes."),

("alsace","🍷","Wine route","Sep–Oct — harvest season, open cellars from Thann to Marlenheim, 170 km."),
("alsace","🎄","Christmas markets","Nov–Dec — Strasbourg, Colmar, Kaysersberg: Europe's oldest Christmas markets."),
("alsace","🏘️","Half-timbered villages","May–Sep — Riquewihr, Eguisheim, Kaysersberg in the sunshine."),
("alsace","🥾","Vosges hiking","Jun–Sep — Grand Ballon summit, Vosges ridge trails, marked paths."),
("alsace","🍺","Breweries & winstubs","Year-round — sauerkraut, flammekueche, local beers in Strasbourg."),

("la-rochelle","⛵","Old Port & sailing","May–Sep — historic harbor, regattas, illuminated medieval towers."),
("la-rochelle","🚲","Île de Ré","Jun–Sep — cycling between salt marshes, beaches and white villages."),
("la-rochelle","🐠","Aquarium","Year-round — one of Europe's largest, 12,000 marine species."),
("la-rochelle","🦪","Marennes-Oléron oysters","Oct–Mar — oyster season, tasting shacks by the harbor."),

("val-d-isere","⛷️","Espace Killy skiing","Dec–Apr — 300 km of runs shared with Tignes, guaranteed powder."),
("val-d-isere","🥾","Vanoise National Park","Jul–Aug — marmots, alpine lakes, marked trails."),
("val-d-isere","🚵","Mountain biking & trail","Jun–Sep — marked downhill runs, lifts open in summer."),
("val-d-isere","🏔️","Bellevarde face","Dec–Mar — 1992 Olympic run, 959 m vertical drop."),

("nantes","🐘","Machines of the Isle","Year-round — giant mechanical elephant, Carousel of the Marine Worlds."),
("nantes","🏰","Castle of the Dukes of Brittany","Year-round — medieval fortress, free history museum."),
("nantes","🍷","Muscadet & vineyards","Sep–Oct — Muscadet wine route, tastings along the Loire."),
("nantes","🎨","Voyage à Nantes","Jul–Aug — summer urban art trail, temporary installations."),

("cannes","🎬","Cannes Film Festival","May — red carpet ascent, Croisette buzz, open-air screenings."),
("cannes","🏖️","Beaches & La Croisette","Jun–Sep — public and private beaches, 24°C water."),
("cannes","🏝️","Lérins Islands","Apr–Oct — 15 min by boat, Sainte-Marguerite and Saint-Honorat."),
("cannes","🍾","Forville Market & Le Suquet bars","Year-round — Provençal market, Michelin-starred restaurants, old quarter."),

# ── SPAIN ──
("palma-de-majorque","🏛️","La Seu Cathedral","Year-round — seaside Gothic cathedral, giant rose window, Gaudí touches."),
("palma-de-majorque","🏖️","Turquoise coves","May–Oct — Cala Mondragó, Cala Varques, Es Trenc."),
("palma-de-majorque","🚴","Serra de Tramuntana","Mar–May or Sep–Oct — UNESCO cycling cols, panoramic roads."),
("palma-de-majorque","🍷","Wine & ensaïmada","Year-round — Binissalem DO, sobrasada, local markets."),

("ronda","🌉","Puente Nuevo & El Tajo gorge","Year-round — Puente Nuevo bridge, 100 m above the ravine."),
("ronda","🐂","Historic arena","Mar–Oct — Spain's oldest bullring (1785), bullfighting museum."),
("ronda","🍷","Ronda bodegas","Sep–Oct — high-altitude vineyards, local grape varieties, wine route."),
("ronda","🥾","El Tajo via ferrata","Apr–Jun or Sep–Nov — vertiginous route above the gorge."),

("marbella","🏖️","Beaches & chiringuitos","May–Oct — Nikki Beach, Nagüeles, 27 km of golden coast."),
("marbella","🏘️","Casco Antiguo","Year-round — whitewashed lanes, Plaza de los Naranjos, boutiques."),
("marbella","⛳","Golf","Oct–May — 15+ courses (La Quinta, Aloha), 18–22°C temperatures."),
("marbella","🍽️","Puerto Banús","Year-round — luxury marina, restaurants, nightlife."),

# ── ITALY ──
("bari","🏛️","Bari Vecchia & St Nicholas","Year-round — fortified old town, Romanesque basilica, cathedral."),
("bari","🍝","Orecchiette & focaccia","Year-round — handmade pasta in the alleys, focaccia barese."),
("bari","🏰","Castel del Monte","Mar–Oct — Frederick II's UNESCO masterpiece, 70 km from Bari."),
("bari","🏖️","Polignano a Mare","Jun–Sep — cliffs, coves, cliff diving."),

("lecce","🏛️","Lecce Baroque","Year-round — Santa Croce, Piazza del Duomo, carved golden stone."),
("lecce","🏖️","Salento beaches","Jun–Sep — Torre dell'Orso, Pescoluse 'Maldives of Puglia'."),
("lecce","🍷","Primitivo wine & pasticciotto","Year-round — Primitivo wine, local pastry, rustico leccese."),
("lecce","🎭","Sagre & festivals","Jul–Aug — patron saint feasts, food festivals in the villages."),

("genes","🏛️","Palazzi dei Rolli","Year-round — Europe's largest medieval center, UNESCO palaces."),
("genes","🍝","Pesto & focaccia di Recco","Year-round — pesto alla genovese, trofie, farinata."),
("genes","🐠","Genoa Aquarium","Year-round — Italy's largest aquarium, dolphins, jellyfish."),
("genes","🏖️","Cinque Terre","Apr–Oct — 5 villages 2h by train, coastal hiking."),

("catane","🌋","Mount Etna excursion","Apr–Oct — summit of Europe's largest active volcano, 3,357 m."),
("catane","🐟","Fish market & street food","Year-round — historic fish market, arancini, granita."),
("catane","🏛️","Sicilian Baroque","Year-round — Piazza del Duomo, Via Etnea, Benedictine Monastery."),
("catane","🏖️","Volcanic beaches","Jun–Sep — San Giovanni Li Cuti, Aci Trezza, black rocks."),

("sorrente","🍋","Limoncello & lemon groves","Year-round — citrus terraces, local artisan production."),
("sorrente","🏖️","Amalfi Coast","May–Oct — day trip to Positano, Amalfi, Ravello from Sorrento."),
("sorrente","🏝️","Capri","Apr–Oct — 20 min by ferry, Blue Grotto, Augustus Gardens."),
("sorrente","🍝","Gnocchi alla sorrentina","Year-round — local cuisine, seafood, coastal wine."),

("ravello","🎵","Ravello Festival","Jun–Sep — classical concerts at Villa Rufolo's Belvedere."),
("ravello","🏛️","Terrace of Infinity","Year-round — Villa Cimbrone, the finest view on the coast."),
("ravello","🥾","Path of the Gods","Apr–Oct — spectacular hike between Agerola and Positano."),
("ravello","💰","Budget","Oct–Nov — deserted coast, prices halved, autumn light."),

("taormina","🏛️","Greco-Roman theater","Year-round — Etna and bay views from the ancient tiers."),
("taormina","🏖️","Isola Bella","May–Sep — beach at the foot of the cliff, nature reserve."),
("taormina","🎬","Taormina Film Fest","Jun — open-air screenings in the ancient theater."),
("taormina","🍷","Etna wines","Year-round — Nerello Mascalese, cellars on the volcano slopes."),

("siena","🐎","Palio di Siena","Jul 2 & Aug 16 — medieval horse race, Piazza del Campo."),
("siena","🏛️","Piazza del Campo","Year-round — shell-shaped square, Palazzo Pubblico, Torre del Mangia."),
("siena","🍷","Chianti Classico","Sep–Oct — harvest, Chianti route through vineyards and hills."),
("siena","🏘️","Val d'Orcia","May–Jun or Sep — UNESCO hills, Pienza, Montalcino, Tuscan cypresses."),

("trieste","☕","Historic cafés","Year-round — San Marco, Antico Torinese: Italy's coffee capital."),
("trieste","🏰","Miramare Castle","Year-round — Habsburg palace by the sea, botanical gardens."),
("trieste","🌊","Barcola & Grotta Gigante","Jun–Sep — local swimming, world's largest tourist cave."),
("trieste","🍷","Karst osmize","Year-round — rural Karst taverns, jota triestina, local wines."),
]
