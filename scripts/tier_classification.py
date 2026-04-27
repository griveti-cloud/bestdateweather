"""
Classification V3 - basée sur notoriété touristique mondiale RÉELLE.

Tier 1 (~150) : "Bucket list" mondial. Tout touriste informé connaît.
  - Capitales mondiales majeures (Tokyo, Rome, Paris, NY, etc.)
  - Sites UNESCO bucket-list (Machu Picchu, Petra, Angkor, Taj Mahal, etc.)
  - Iles paradis (Maldives, Bora Bora, Bali)
  - Stations ski super premium (Chamonix, Zermatt, Verbier, Aspen, Niseko)

Tier 2 (~280) : Bien connue. Le touriste français/européen y va.
  - Capitales nationales européennes secondaires (Riga, Sofia, etc.)
  - Villes secondaires touristiques (Lyon, Florence, Salzburg, Prague, etc.)
  - Plages connues (Caraïbes principales, îles grecques, Costa del Sol)
  - Stations ski moyennes

Tier 3 (~250) : Niche/secondaire. Connaissance limitée mais possible.
  - Villes secondaires moins connues
  - Stations ski peu fréquentées
  - Destinations émergentes
  → Avis data-driven, pas d'insider tips

Tier 4 (~75) : OBSCURE. Risque d'invention si avis "riche".
  - Capitales pacifiques micro-États
  - Capitales africaines instables
  - Asie centrale peu touristique
  → FALLBACK templates obligatoire
"""
import json

data = json.load(open('/tmp/all_slugs.json'))
all_slugs = set(data['all'])

# ===== TIER 4 : OBSCURES (priorité absolue) =====
TIER4 = {
    # Pacifique micro-États
    'palikir', 'majuro', 'funafuti', 'tarawa', 'honiara',
    
    # Capitales africaines instables/peu touristiques
    'mogadiscio', 'bangui', 'djouba', 'ndjamena', 'nouakchott', 'niamey',
    'bamako', 'ouagadougou', 'monrovia', 'conakry', 'bissau', 'banjul',
    'freetown', 'lome', 'cotonou', 'maseru', 'mbabane', 'malabo',
    'libreville', 'brazzaville', 'kinshasa', 'luanda', 'bujumbura',
    'lilongwe', 'djibouti', 'khartoum', 'tripoli', 'douala', 'sao-tome',
    'moroni', 'abuja', 'gondar', 'kumasi', 'asmara',
    'kampala', 'jinja', 'entebbe',  # Ouganda secondaire
    'batna', 'annaba', 'constantine',  # Algérie secondaire
    'tofo' if False else None,
    
    # Asie centrale peu touristique
    'achgabat', 'douchanbé', 'bichkek',
    
    # Moyen-Orient instable
    'bagdad', 'damas',
    
    # Asie SE peu visitée
    'dili',
    
    # Russie villes secondaires
    'novossibirsk', 'irkoutsk', 'vladivostok', 'ekaterinbourg', 'kazan',
    
    # Amérique latine secondaires/instables
    'rosario', 'sucre', 'asuncion', 'georgetown-guyana', 'paramaribo',
    'caracas', 'port-au-prince',
    
    # Stations ski peu connues
    'shahdag', 'gudauri', 'bakuriani',
    
    # Iles très isolées
    'rodrigues',
    
    # Pays vastes, peu d'infos pratiques
    'mongolie',
    
    # Capitales Asie peu touristiques
    'dacca', 'islamabad',
    
    # Bandar Seri (capitale Brunei)
    'bandar-seri-begawan',
}
TIER4 = {s for s in TIER4 if s} & all_slugs

# ===== TIER 1 : ICÔNIQUES MONDIAUX STRICTS =====
# Ce qui est dans tous les guides "Top 50 destinations mondiales"
TIER1 = {
    # Asie - vraiment bucket-list
    'tokyo', 'kyoto', 'bangkok', 'phuket', 'hong-kong', 'shanghai', 'pekin',
    'singapour', 'seoul', 'siem-reap', 'hanoi', 'ho-chi-minh', 'baie-halong',
    'bali', 'ubud', 'maldives', 'sri-lanka', 'kuala-lumpur',
    'delhi', 'mumbai', 'jaipur', 'agra', 'varanasi', 'kerala', 'goa',
    'taipei', 'macao', 'lhasa', 'katmandou',
    'osaka', 'hiroshima', 'okinawa', 'nikko', 'hakone', 'sapporo',
    'chiang-mai', 'krabi', 'koh-samui',
    
    # Europe - vraiment bucket-list
    'rome', 'florence', 'venise', 'milan', 'naples', 'amalfi', 'cinque-terre',
    'capri', 'sicile', 'sardaigne',
    'londres', 'edimbourg', 'dublin',
    'amsterdam', 'bruxelles', 'bruges', 'berlin', 'munich',
    'vienne', 'salzburg', 'hallstatt',
    'prague', 'budapest', 'cracovie',
    'oslo', 'stockholm', 'copenhague', 'reykjavik',
    'tromso', 'lofoten', 'laponie',
    'madrid', 'barcelone', 'seville', 'grenade', 'cordoue',
    'ibiza', 'majorque',
    'athenes', 'mykonos', 'santorin', 'crete',
    'istanbul', 'cappadoce',
    'paris', 'nice', 'cannes',
    'lisbonne', 'porto',
    'dubrovnik', 'split', 'plitvice',
    'monaco', 'malte',
    'moscou', 'saint-petersbourg',
    
    # Amérique du Nord - vraiment bucket-list
    'new-york', 'chicago', 'miami', 'orlando', 'las-vegas',
    'san-francisco', 'los-angeles', 'seattle',
    'yellowstone',
    'aspen', 'whistler', 'banff', 'lake-louise',
    'montreal', 'toronto', 'vancouver', 'quebec-ville',
    'hawaii', 'maui', 'honolulu',
    'nouvelle-orleans',
    
    # Amérique latine - vraiment bucket-list
    'rio-de-janeiro', 'buenos-aires',
    'cusco', 'machu-picchu',
    'galapagos',
    'la-havane',
    'mexico', 'cancun', 'playa-del-carmen', 'tulum',
    'patagonie', 'iguazu',
    'sao-paulo',  # mégapole mondiale
    
    # Afrique - vraiment bucket-list
    'le-caire', 'louxor',
    'marrakech', 'fes',
    'le-cap',
    'zanzibar',
    'victoria-falls',
    
    # Moyen-Orient - vraiment bucket-list
    'dubai', 'abu-dhabi',
    'petra', 'wadi-rum',
    'tel-aviv',
    
    # Océanie - vraiment bucket-list
    'sydney', 'melbourne', 'auckland', 'queenstown',
    'uluru', 'whitsundays',
    'tahiti', 'bora-bora', 'moorea',
    
    # Stations ski iconiques mondiales
    'chamonix', 'val-d-isere', 'courchevel', 'meribel', 'val-thorens',
    'zermatt', 'verbier', 'davos',
    'st-anton', 'kitzbuhel', 'lech',
    'cortina-dampezzo',
    'niseko',
    
    # Caraïbes iconiques
    'martinique', 'guadeloupe', 'saint-barthelemy',
    'bahamas', 'jamaique', 'porto-rico', 'barbade',
    'turks-et-caicos',
    
    # Iles iconiques
    'seychelles', 'ile-maurice', 'reunion',
    'fidji',
    
    # Sites/régions iconiques France
    'corse', 'cote-azur', 'provence', 'alsace', 'normandie', 'bretagne',
    'dordogne',
    'biarritz', 'bordeaux', 'lyon', 'marseille', 'strasbourg',
    
    # Iconiques Espagne
    'canaries', 'tenerife', 'gran-canaria',
    'malaga',
    
    # Iconiques Italie
    'lac-come', 'lac-garde', 'toscane', 'matera',
    
    # Iconiques Portugal
    'sintra', 'algarve', 'madere',
    
    # Iconiques Maroc
    'agadir', 'casablanca', 'essaouira', 'chefchaouen', 'tanger',
    
    # Iconiques Egypte
    'sharm-el-sheikh',
    
    # Iconiques Croatie
    'hvar', 'kotor',
    
    # Iconiques Pérou
    'lima',
    
    # Iconiques USA
    'boston', 'austin', 'nashville', 'washington', 'denver',
    'memphis', 'charleston', 'savannah', 'palm-springs', 'sedona',
    'napa-valley', 'phoenix',  # phoenix déjà couvert
    'san-diego', 'monterey', 'santa-barbara', 'key-west', 'cape-cod',
    'park-city', 'jackson-hole', 'vail', 'breckenridge',
    'lake-tahoe',
    
    # Iconiques Antilles
    'saint-martin', 'saint-lucie',
    
    # Iconiques Sud Asie
    'jodhpur', 'udaipur',
}
TIER1 = {s for s in TIER1 if s} & all_slugs
TIER1 = TIER1 - TIER4

# ===== TIER 2 : BIEN CONNUES =====
TIER2 = {
    # Capitales nationales européennes secondaires
    'bratislava', 'sofia', 'bucarest', 'belgrade', 'sarajevo', 'zagreb',
    'tallinn', 'riga', 'vilnius', 'minsk', 'chisinau', 'tirana', 'pristina',
    'skopje', 'ljubljana', 'helsinki', 'bergen',
    'baku', 'yerevan', 'tbilissi',
    'luxembourg',
    
    # Villes secondaires européennes touristiques
    'francfort', 'cologne', 'dresde', 'hambourg',
    'innsbruck', 'graz' if False else None,
    'gdansk', 'wroclaw', 'poznan', 'lviv',
    'lac-bled', 'piran',
    'budva', 'kotor', 'montenegro',
    'zadar', 'trogir',
    'ohrid',
    'sao-miguel', 'funchal',
    'bath', 'lake-district', 'cotswolds', 'isle-of-skye', 'wild-atlantic-way',
    'lille' if False else None, 'rennes', 'nantes', 'la-rochelle', 'la-baule',
    'avignon' if False else None, 'aix-en-provence' if False else None,
    'colmar' if False else None, 'annecy', 'montpellier', 'toulouse',
    'pays-basque', 'mayotte', 'guyane',
    'oviedo' if False else None,
    'salamanque', 'tolede', 'bilbao', 'saint-sebastien', 'valence',
    'marbella', 'ronda', 'palma-de-majorque', 'minorque', 'alcudia',
    'costa-brava', 'sierra-nevada', 'baqueira-beret', 'cadix',
    'la-palma', 'la-gomera', 'el-hierro', 'fuerteventura', 'lanzarote',
    'formentera', 'gibraltar',
    'palerme', 'catane', 'taormina', 'bari', 'alberobello', 'lecce',
    'pouilles', 'siena', 'perouse', 'bologne', 'genes', 'turin', 'verone',
    'sorrente', 'ravello', 'tropea', 'elba', 'pantelleria',
    'ischia', 'procida',
    'gozo', 'valletta',
    'paphos', 'larnaca', 'chypre',
    'corfou', 'naxos', 'paros', 'milos', 'rhodes',
    'kos', 'lefkada', 'samos', 'zakynthos', 'skiathos', 'hydra', 'kefalonia',
    'peloponnese', 'thessalonique', 'kalamata',
    'antalya', 'bodrum', 'fethiye', 'izmir', 'alacati',
    'acores', 'alentejo', 'faro',
    'transylvanie',
    'aarhus', 'goteborg' if False else None,
    'are', 'svalbard',
    'sao-tome',
    
    # Stations ski moyennes
    'megeve', 'morzine', 'les-arcs', 'la-plagne', 'serre-chevalier',
    'alpe-dhuez', 'les-deux-alpes', 'la-clusaz', 'les-gets', 'flaine',
    'les-menuires', 'tignes', 'montgenevre',
    'crans-montana', 'saas-fee', 'laax', 'engelberg', 'gstaad',
    'grindelwald', 'wengen', 'interlaken', 'lucerne', 'geneve', 'zurich',
    'mayrhofen', 'schladming', 'ischgl', 'saalbach', 'zell-am-see', 'hintertux',
    'sestriere', 'cervinia', 'madonna-di-campiglio', 'val-gardena',
    'courmayeur', 'livigno', 'dolomites',
    'andorre', 'grandvalira',
    'hakuba', 'furano', 'nozawa-onsen',
    'big-white', 'revelstoke', 'mont-tremblant',
    'park-city', 'telluride', 'mammoth-mountain', 'sun-valley',
    'steamboat-springs', 'killington', 'stowe',
    'hemsedal', 'geilo', 'levi',
    'bansko', 'jasna',
    'thredbo', 'perisher',
    'yongpyong',
    'oukaimeden',
    'valle-nevado', 'portillo',
    'gulmarg', 'shimla',
    
    # Capitales asiatiques moyennes
    'phnom-penh', 'luang-prabang', 'vientiane',
    'jakarta', 'denpasar', 'yogyakarta', 'java', 'lombok',
    'cebu', 'manille', 'boracay', 'el-nido', 'palawan', 'coron', 'siargao',
    'mandalay', 'yangon',
    'kandy', 'colombo', 'ella',
    
    # Asie centrale connues
    'samarcande', 'boukhara', 'khiva', 'ouzbekistan',
    'almaty', 'astana',
    'georgie',
    
    # Inde villes secondaires
    'mysore', 'amritsar', 'kochi', 'hampi', 'pondicherry', 'rajasthan',
    'rishikesh', 'jaisalmer', 'darjeeling',
    
    # Asie supplémentaires
    'fukuoka', 'nagoya', 'nagasaki', 'kanazawa', 'matsuyama', 'nara',
    'kaohsiung', 'jeju', 'busan',
    'penang', 'malacca', 'ipoh', 'langkawi', 'kota-kinabalu', 'kuching',
    'da-nang', 'hoi-an', 'sapa', 'da-lat', 'nha-trang', 'mui-ne',
    'phu-quoc', 'hue', 'ninh-binh', 'quy-nhon',
    'pattaya', 'hua-hin', 'chiang-rai', 'koh-tao', 'koh-lanta', 'koh-chang',
    'gili', 'nusa-penida', 'borneo', 'komodo', 'canggu',
    'hangzhou', 'suzhou', 'chengdu', 'kunming', 'lijiang', 'zhangjiajie',
    'qingdao', 'chongqing', 'harbin', 'xian', 'guilin',
    'labuan-bajo', 'raja-ampat',
    'thimphu', 'bhutan',
    'pokhara', 'nepal',
    'philippines',
    'luzon',
    'cambodge', 'laos', 'myanmar',
    
    # Caraïbes secondaires
    'aruba', 'curacao', 'bonaire',
    'antigua', 'saint-thomas', 'dominique', 'grenadines', 'saint-vincent',
    'saint-georges-grenade', 'trinite-et-tobago',
    'cayman-islands', 'bermudes', 'providencia', 'basseterre',
    'republique-dominicaine', 'nassau',
    'saint-pierre-et-miquelon',
    
    # Afrique secondaires
    'rabat', 'oran', 'alger',
    'arusha', 'moshi', 'tanzanie', 'dar-es-salaam',
    'mombasa', 'lamu', 'diani', 'kenya', 'nairobi',
    'maun', 'windhoek', 'etosha', 'livingstone', 'harare', 'maputo',
    'madagascar', 'nosybe', 'namibie',
    'durban', 'johannesburg',
    'dakar', 'senegal',
    'addis-abeba', 'lalibela',
    'kigali',
    'lagos', 'abidjan', 'accra',
    'stone-town',
    'assouan', 'alexandrie' if False else None,
    'djerba', 'hammamet', 'tunis',
    'ouarzazate', 'merzouga',
    
    # Amérique latine secondaires
    'cartagena-col', 'medellin', 'bogota', 'colombie', 'quito',
    'la-paz', 'bolivie',
    'santiago', 'valparaiso', 'mendoza', 'salta',
    'montevideo', 'punta-del-este', 'uruguay',
    'oaxaca', 'guanajuato', 'san-miguel-de-allende', 'merida',
    'puerto-vallarta', 'cabo-san-lucas', 'loreto-mexique', 'isla-holbox',
    'puerto-escondido', 'san-cristobal', 'riviera-maya',
    'cuenca-equateur', 'equateur', 'perou',
    'porto-alegre', 'manaus', 'belem', 'natal-bresil', 'chapada-diamantina',
    'salvador-de-bahia', 'florianopolis',
    'antigua-guatemala', 'guatemala', 'panama', 'belize', 'roatan',
    'monteverde', 'san-jose', 'costa-rica',
    'granada-nicaragua', 'nicaragua', 'san-salvador',
    'punta-cana', 'bariloche',
    'asuncion' if False else None,  # déjà tier 4
    'trinidad-cuba', 'chili',
    
    # Asie supplémentaires supplémentaires
    'sotchi', 'krasnaya-polyana',
    
    # Pacifique
    'noumea', 'nouvelle-caledonie', 'vanuatu', 'samoa', 'tonga',
    'iles-cook', 'rarotonga', 'polynesie', 'palau', 'nouvelle-zelande',
    
    # Moyen-Orient
    'beyrouth', 'jordanie', 'amman', 'aqaba', 'ispahan', 'teheran',
    'bahrein', 'koweit', 'doha', 'oman', 'muscat', 'salalah',
    'fujairah', 'ras-al-khaimah', 'al-ula', 'djeddah', 'riyad',
    'hurghada', 'marsa-alam',
    
    # Iles
    'cap-vert', 'sal',
    'socotra',
    
    # Australie
    'darwin', 'adelaide', 'hobart', 'brisbane', 'perth', 'cairns',
    'wellington', 'christchurch', 'taupo', 'bay-of-islands', 'rotorua',
    'gold-coast',
    
    # Russie/Caucase moyennes (déjà tier 4 secondaire)
    
    # Italie/Europe Sud secondaires
    'cordoba-argentine',
    
    # Trieste
    'trieste',
    
    # Vatican / Liechtenstein
    'vaduz',
    
    # Stations ski supplémentaires
    'queenstown-ski',
    
    # Chypre
    'paphos',
    
    # Other
    'york', 'ghent',
    'fortaleza' if False else None,
    'sotchi',
    'nassau',  # déjà
    
    # Mongolie est tier 4
    
    # Ouganda
    'mombasa',
    
    # Algérie villes (Alger seul est tier 2, le reste tier 4)
    
    # Portugal
    'algarve',
    
    # Espagne sup
    'alicante',
    
    # Petit peu tier 1
    'sao-tome',
    
    # Misc
    'cervinia',
    
    # Iles
    'samoa',
}
TIER2 = {s for s in TIER2 if s} & all_slugs
TIER2 = TIER2 - TIER4 - TIER1

# ===== TIER 3 : reste =====
TIER3 = all_slugs - TIER1 - TIER2 - TIER4

print(f"Total destinations : {len(all_slugs)}")
print()
print(f"Tier 1 (iconique mondial)              : {len(TIER1):>4} ({len(TIER1)*100//754}%)")
print(f"Tier 2 (bien connue)                   : {len(TIER2):>4} ({len(TIER2)*100//754}%)")
print(f"Tier 3 (data-driven)                   : {len(TIER3):>4} ({len(TIER3)*100//754}%)")
print(f"Tier 4 (OBSCURE - FALLBACK)            : {len(TIER4):>4} ({len(TIER4)*100//754}%)")
print(f"Total                                   : {len(TIER1)+len(TIER2)+len(TIER3)+len(TIER4):>4}")

with open('/tmp/tiers_v3.json', 'w') as f:
    json.dump({
        'tier1': sorted(TIER1),
        'tier2': sorted(TIER2),
        'tier3': sorted(TIER3),
        'tier4': sorted(TIER4),
    }, f, indent=2)
