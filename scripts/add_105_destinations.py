#!/usr/bin/env python3
"""
add_105_destinations.py
-----------------------
Add 105 new destinations to destinations.csv.
Generates hero_sub FR/EN/ES via Claude API for each destination.

Usage:
    ANTHROPIC_API_KEY=sk-ant-... python3 scripts/add_105_destinations.py
    # or if key already in env:
    python3 scripts/add_105_destinations.py
"""

import csv, json, os, sys, time, io
import anthropic

DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(DIR, 'data', 'destinations.csv')

# ── 105 destinations ──────────────────────────────────────────────────────────
# Format: (slug_fr, slug_en, slug_es, nom_fr, nom_bare, nom_en, nom_es,
#          pays, flag, country_en, country_es, prep_fr, prep_es,
#          lat, lon, tropical, coastal, mountain, monthly, booking_dest_id, aliases)

NEW_DESTINATIONS = [
    # ── ALGÉRIE (5) ──
    ("alger","algiers","argel","Alger","Alger","Algiers","Argel","Algérie","dz","Algeria","Argelia","à","en",36.74,3.06,False,True,False,True,-3747120,""),
    ("oran","oran","oran","Oran","Oran","Oran","Orán","Algérie","dz","Algeria","Argelia","à","en",35.70,-0.64,False,True,False,True,-3747121,""),
    ("constantine","constantine","constantine","Constantine","Constantine","Constantine","Constantina","Algérie","dz","Algeria","Argelia","à","en",36.37,6.61,False,False,False,True,-3747122,""),
    ("annaba","annaba","annaba","Annaba","Annaba","Annaba","Annaba","Algérie","dz","Algeria","Argelia","à","en",36.90,7.77,False,True,False,True,-3747123,""),
    ("batna","batna","batna","Batna","Batna","Batna","Batna","Algérie","dz","Algeria","Argelia","à","en",35.56,6.17,False,False,True,True,-3747124,""),

    # ── UK (5) ──
    ("bath","bath","bath","Bath","Bath","Bath","Bath","Royaume-Uni","gb","United Kingdom","Reino Unido","à","en",51.38,-2.36,False,False,False,True,-2595386,""),
    ("cotswolds","cotswolds","cotswolds","les Cotswolds","Cotswolds","Cotswolds","Cotswolds","Royaume-Uni","gb","United Kingdom","Reino Unido","dans les","en los",51.88,-1.78,False,False,False,True,-2595394,"cotswold"),
    ("lake-district","lake-district","lake-district","le Lake District","Lake District","Lake District","Lake District","Royaume-Uni","gb","United Kingdom","Reino Unido","dans le","en el",54.46,-3.08,False,False,True,True,-2595395,""),
    ("isle-of-skye","isle-of-skye","isle-of-skye","l'île de Skye","Île de Skye","Isle of Skye","Isla de Skye","Royaume-Uni","gb","United Kingdom","Reino Unido","sur","en",57.27,-6.21,False,True,True,True,-2595396,"skye"),
    ("york","york","york","York","York","York","York","Royaume-Uni","gb","United Kingdom","Reino Unido","à","en",53.96,-1.08,False,False,False,True,-2595397,""),

    # ── EUROPE CENTRALE / ALPES (5) ──
    ("salzburg","salzburg","salzburgo","Salzburg","Salzburg","Salzburg","Salzburgo","Autriche","at","Austria","Austria","à","en",47.80,13.04,False,False,True,True,-714482,"salzbourg"),
    ("interlaken","interlaken","interlaken","Interlaken","Interlaken","Interlaken","Interlaken","Suisse","ch","Switzerland","Suiza","à","en",46.69,7.86,False,False,True,True,-2657893,""),
    ("lucerne","lucerne","lucerna","Lucerne","Lucerne","Lucerne","Lucerna","Suisse","ch","Switzerland","Suiza","à","en",47.05,8.31,False,False,False,True,-2659811,"luzern"),
    ("cologne","cologne","colonia","Cologne","Cologne","Cologne","Colonia","Allemagne","de","Germany","Alemania","à","en",50.94,6.96,False,False,False,True,-2886242,"koln köln koeln"),
    ("dresde","dresden","dresde","Dresde","Dresde","Dresden","Dresde","Allemagne","de","Germany","Alemania","à","en",51.05,13.74,False,False,False,True,-2935022,""),

    # ── ALCÚDIA (marché DE) ──
    ("alcudia","alcudia","alcudia","Alcúdia","Alcúdia","Alcúdia","Alcúdia","Espagne","es","Spain","España","à","en",39.85,3.12,False,True,False,True,-390625,"alcudia majorque mallorca nord"),

    # ── JAPON (5) ──
    ("fukuoka","fukuoka","fukuoka","Fukuoka","Fukuoka","Fukuoka","Fukuoka","Japon","jp","Japan","Japón","à","en",33.59,130.40,False,True,False,True,-1863900,"hakata"),
    ("kanazawa","kanazawa","kanazawa","Kanazawa","Kanazawa","Kanazawa","Kanazawa","Japon","jp","Japan","Japón","à","en",36.56,136.65,False,False,False,True,-1860243,""),
    ("hakone","hakone","hakone","Hakone","Hakone","Hakone","Hakone","Japon","jp","Japan","Japón","à","en",35.23,139.01,False,False,True,True,-1862396,""),
    ("nikko","nikko","nikko","Nikko","Nikko","Nikko","Nikko","Japon","jp","Japan","Japón","à","en",36.75,139.60,False,False,True,True,-1855524,""),
    ("nagoya","nagoya","nagoya","Nagoya","Nagoya","Nagoya","Nagoya","Japon","jp","Japan","Japón","à","en",35.18,136.90,False,False,False,True,-1856057,""),

    # ── CHINE (6) ──
    ("hangzhou","hangzhou","hangzhou","Hangzhou","Hangzhou","Hangzhou","Hangzhou","Chine","cn","China","China","à","en",30.27,120.15,False,False,False,True,-1810821,""),
    ("suzhou","suzhou","suzhou","Suzhou","Suzhou","Suzhou","Suzhou","Chine","cn","China","China","à","en",31.30,120.62,False,False,False,True,-1796395,""),
    ("kunming","kunming","kunming","Kunming","Kunming","Kunming","Kunming","Chine","cn","China","China","à","en",25.05,102.71,False,False,True,True,-1802796,""),
    ("qingdao","qingdao","qingdao","Qingdao","Qingdao","Qingdao","Qingdao","Chine","cn","China","China","à","en",36.07,120.38,False,True,False,True,-1797929,"tsingtao"),
    ("harbin","harbin","harbin","Harbin","Harbin","Harbin","Harbin","Chine","cn","China","China","à","en",45.75,126.63,False,False,False,True,-2032858,""),
    ("chongqing","chongqing","chongqing","Chongqing","Chongqing","Chongqing","Chongqing","Chine","cn","China","China","à","en",29.56,106.55,False,False,False,True,-1815286,""),

    # ── INDE (7) ──
    ("amritsar","amritsar","amritsar","Amritsar","Amritsar","Amritsar","Amritsar","Inde","in","India","India","à","en",31.63,74.87,False,False,False,True,-1278718,"temple d'or golden temple"),
    ("jodhpur","jodhpur","jodhpur","Jodhpur","Jodhpur","Jodhpur","Jodhpur","Inde","in","India","India","à","en",26.29,73.02,False,False,False,True,-1268754,"ville bleue blue city"),
    ("jaisalmer","jaisalmer","jaisalmer","Jaisalmer","Jaisalmer","Jaisalmer","Jaisalmer","Inde","in","India","India","à","en",26.92,70.91,False,False,False,True,-1268527,""),
    ("rishikesh","rishikesh","rishikesh","Rishikesh","Rishikesh","Rishikesh","Rishikesh","Inde","in","India","India","à","en",30.09,78.27,False,False,True,True,-1258986,""),
    ("darjeeling","darjeeling","darjeeling","Darjeeling","Darjeeling","Darjeeling","Darjeeling","Inde","in","India","India","à","en",27.04,88.26,False,False,True,True,-1273294,""),
    ("mysore","mysore","mysore","Mysore","Mysore","Mysore","Mysore","Inde","in","India","India","à","en",12.30,76.65,False,False,False,True,-1263780,"mysuru"),
    ("shimla","shimla","shimla","Shimla","Shimla","Shimla","Shimla","Inde","in","India","India","à","en",31.10,77.17,False,False,True,True,-1255529,"simla"),

    # ── ASIE DU SUD-EST (3) ──
    ("vientiane","vientiane","vientiane","Vientiane","Vientiane","Vientiane","Vientiane","Laos","la","Laos","Laos","à","en",17.97,102.60,True,False,False,True,-1581298,""),
    ("hua-hin","hua-hin","hua-hin","Hua Hin","Hua Hin","Hua Hin","Hua Hin","Thaïlande","th","Thailand","Tailandia","à","en",12.57,99.96,True,True,False,True,-617070,""),
    ("koh-chang","koh-chang","koh-chang","Koh Chang","Koh Chang","Koh Chang","Koh Chang","Thaïlande","th","Thailand","Tailandia","à","en",12.07,102.33,True,True,False,True,-617280,"ko chang"),

    # ── CAUCASE (2) ──
    ("yerevan","yerevan","erevan","Erevan","Erevan","Yerevan","Ereván","Arménie","am","Armenia","Armenia","à","en",40.18,44.51,False,False,False,True,-616052,"erevan arménie"),
    ("baku","baku","baku","Bakou","Bakou","Baku","Bakú","Azerbaïdjan","az","Azerbaijan","Azerbaiyán","à","en",40.41,49.87,False,True,False,True,-587273,"azerbaidjan"),

    # ── MOYEN-ORIENT (2) ──
    ("amman","amman","aman","Amman","Amman","Amman","Ammán","Jordanie","jo","Jordan","Jordania","à","en",31.96,35.94,False,False,False,True,-250441,""),
    ("fujairah","fujairah","fujairah","Fujairah","Fujairah","Fujairah","Fujairah","Émirats arabes unis","ae","UAE","Emiratos Árabes Unidos","à","en",25.12,56.34,False,True,False,True,-290594,""),

    # ── AFRIQUE DE L'OUEST (4) ──
    ("libreville","libreville","libreville","Libreville","Libreville","Libreville","Libreville","Gabon","ga","Gabon","Gabón","à","en",-0.39,9.45,True,True,False,True,-2400547,"gabon"),
    ("banjul","banjul","banjul","Banjul","Banjul","Banjul","Banjul","Gambie","gm","Gambia","Gambia","à","en",13.45,-16.57,True,True,False,True,-2413459,"gambie gambia"),
    ("abuja","abuja","abuja","Abuja","Abuja","Abuja","Abuya","Nigeria","ng","Nigeria","Nigeria","à","en",9.07,7.40,True,False,False,True,-2352458,"nigeria"),
    ("kumasi","kumasi","kumasi","Kumasi","Kumasi","Kumasi","Kumasi","Ghana","gh","Ghana","Ghana","à","en",6.69,-1.62,True,False,False,True,-2300660,"ghana ashanti"),

    # ── AFRIQUE DE L'EST (2) ──
    ("moshi","moshi","moshi","Moshi","Moshi","Moshi","Moshi","Tanzanie","tz","Tanzania","Tanzania","à","en",-3.35,37.34,True,False,True,True,-152930,"kilimanjaro"),
    ("entebbe","entebbe","entebbe","Entebbe","Entebbe","Entebbe","Entebbe","Ouganda","ug","Uganda","Uganda","à","en",0.06,32.46,True,False,False,True,-232072,"ouganda uganda"),

    # ── AFRIQUE AUSTRALE (2) ──
    ("harare","harare","harare","Harare","Harare","Harare","Harare","Zimbabwe","zw","Zimbabwe","Zimbabue","à","en",-17.82,31.05,False,False,False,True,-892640,"zimbabwe"),
    ("lilongwe","lilongwe","lilongwe","Lilongwe","Lilongwe","Lilongwe","Lilongwe","Malawi","mw","Malawi","Malaui","à","en",-13.97,33.79,False,False,False,True,-927967,"malawi"),

    # ── AMÉRIQUE DU SUD (8) ──
    ("cuenca-equateur","cuenca-ecuador","cuenca-ecuador","Cuenca","Cuenca","Cuenca","Cuenca","Équateur","ec","Ecuador","Ecuador","à","en",-2.90,-79.00,False,False,True,True,-3652238,"cuenca ecuador"),
    ("cordoba-argentine","cordoba-argentina","cordoba-argentina","Córdoba","Córdoba","Córdoba","Córdoba","Argentine","ar","Argentina","Argentina","à","en",-31.42,-64.19,False,False,False,True,-3860259,"cordoba argentine"),
    ("chapada-diamantina","chapada-diamantina","chapada-diamantina","Chapada Diamantina","Chapada Diamantina","Chapada Diamantina","Chapada Diamantina","Brésil","br","Brazil","Brasil","dans la","en la",-12.45,-41.42,True,False,True,True,-3466306,""),
    ("porto-alegre","porto-alegre","porto-alegre","Porto Alegre","Porto Alegre","Porto Alegre","Porto Alegre","Brésil","br","Brazil","Brasil","à","en",-30.03,-51.22,False,False,False,True,-3452925,""),
    ("punta-del-este","punta-del-este","punta-del-este","Punta del Este","Punta del Este","Punta del Este","Punta del Este","Uruguay","uy","Uruguay","Uruguay","à","en",-34.97,-54.95,False,True,False,True,-3440777,""),
    ("rosario","rosario","rosario","Rosario","Rosario","Rosario","Rosario","Argentine","ar","Argentina","Argentina","à","en",-32.95,-60.64,False,False,False,True,-3838583,""),
    ("belem","belem","belem","Belém","Belém","Belém","Belém","Brésil","br","Brazil","Brasil","à","en",-1.46,-48.50,True,False,False,True,-3405870,"belem bresil para"),
    ("natal-bresil","natal-brazil","natal-brasil","Natal","Natal","Natal","Natal","Brésil","br","Brazil","Brasil","à","en",-5.79,-35.21,True,True,False,True,-3394023,"natal bresil nordeste"),

    # ── CARAÏBES (4) ──
    ("cayman-islands","cayman-islands","islas-caiman","les Îles Caïmans","Îles Caïmans","Cayman Islands","Islas Caimán","Îles Caïmans","ky","Cayman Islands","Islas Caimán","aux","en las",19.31,-81.25,True,True,False,True,-3580661,"cayman grand cayman"),
    ("saint-thomas","saint-thomas","saint-thomas","Saint Thomas","Saint Thomas","Saint Thomas","Saint Thomas","Îles Vierges américaines","vi","US Virgin Islands","Islas Vírgenes de EE.UU.","à","en",18.34,-64.93,True,True,False,True,-4795346,"us virgin islands usvi"),
    ("saint-vincent","saint-vincent","san-vicente","Saint-Vincent","Saint-Vincent","Saint Vincent","San Vicente","Saint-Vincent-et-les-Grenadines","vc","Saint Vincent and the Grenadines","San Vicente y las Granadinas","à","en",13.15,-61.20,True,True,False,True,-3577430,""),
    ("providencia","providencia","providencia","Providencia","Providencia","Providencia","Providencia","Colombie","co","Colombia","Colombia","à","en",13.35,-81.37,True,True,False,True,-3674533,"providencia colombia isla"),

    # ── USA (9) ──
    ("asheville","asheville","asheville","Asheville","Asheville","Asheville","Asheville","États-Unis","us","United States","Estados Unidos","à","en",35.58,-82.55,False,False,True,True,-4453066,""),
    ("palm-springs","palm-springs","palm-springs","Palm Springs","Palm Springs","Palm Springs","Palm Springs","États-Unis","us","United States","Estados Unidos","à","en",33.83,-116.54,False,False,False,True,-5351405,""),
    ("santa-fe","santa-fe","santa-fe-nm","Santa Fe","Santa Fe","Santa Fe","Santa Fe","États-Unis","us","United States","Estados Unidos","à","en",35.69,-105.94,False,False,True,True,-5490920,"santa fe new mexico nm"),
    ("lake-tahoe","lake-tahoe","lake-tahoe","Lake Tahoe","Lake Tahoe","Lake Tahoe","Lake Tahoe","États-Unis","us","United States","Estados Unidos","au","en el",39.10,-120.03,False,False,True,True,-5370774,"tahoe ski sierra nevada"),
    ("cape-cod","cape-cod","cape-cod","Cape Cod","Cape Cod","Cape Cod","Cape Cod","États-Unis","us","United States","Estados Unidos","sur","en",41.67,-70.22,False,True,False,True,-4929714,""),
    ("outer-banks","outer-banks","outer-banks","Outer Banks","Outer Banks","Outer Banks","Outer Banks","États-Unis","us","United States","Estados Unidos","dans les","en los",35.56,-75.46,False,True,False,True,-4480499,"obx carolina"),
    ("saint-augustine","saint-augustine","san-agustin-florida","Saint Augustine","Saint Augustine","Saint Augustine","San Agustín","États-Unis","us","United States","Estados Unidos","à","en",29.89,-81.32,False,True,False,True,-4170239,"st augustine florida"),
    ("monterey","monterey","monterey","Monterey","Monterey","Monterey","Monterey","États-Unis","us","United States","Estados Unidos","à","en",36.60,-121.89,False,True,False,True,-5374232,"big sur carmel"),
    ("santa-barbara","santa-barbara","santa-barbara","Santa Barbara","Santa Barbara","Santa Barbara","Santa Bárbara","États-Unis","us","United States","Estados Unidos","à","en",34.42,-119.70,False,True,False,True,-5392528,""),

    # ── ITALIE (4) ──
    ("procida","procida","procida","Procida","Procida","Procida","Procida","Italie","it","Italy","Italia","à","en",40.76,14.02,False,True,False,True,-3170335,""),
    ("matera","matera","matera","Matera","Matera","Matera","Matera","Italie","it","Italy","Italia","à","en",40.67,16.61,False,False,False,True,-3172774,"sassi"),
    ("alberobello","alberobello","alberobello","Alberobello","Alberobello","Alberobello","Alberobello","Italie","it","Italy","Italia","à","en",40.78,17.24,False,False,False,True,-3183526,"trulli pouilles"),
    ("tropea","tropea","tropea","Tropea","Tropea","Tropea","Tropea","Italie","it","Italy","Italia","à","en",38.68,15.90,False,True,False,True,-3165761,"calabre calabria"),

    # ── GRÈCE (3) ──
    ("samos","samos","samos","Samos","Samos","Samos","Samos","Grèce","gr","Greece","Grecia","à","en",37.75,26.97,False,True,False,True,-734022,""),
    ("skiathos","skiathos","skiathos","Skiathos","Skiathos","Skiathos","Skiathos","Grèce","gr","Greece","Grecia","à","en",39.16,23.49,False,True,False,True,-735158,"mamma mia"),
    ("kalamata","kalamata","kalamata","Kalamata","Kalamata","Kalamata","Kalamata","Grèce","gr","Greece","Grecia","à","en",37.04,22.11,False,True,False,True,-736515,"peloponnese"),

    # ── MALTE (1) ──
    ("valletta","valletta","la-valeta","La Valette","La Valette","Valletta","La Valeta","Malte","mt","Malta","Malta","à","en",35.90,14.51,False,True,False,True,-2562305,"la valette malte valleta"),

    # ── EUROPE DU NORD/EST (2) ──
    ("aarhus","aarhus","aarhus","Aarhus","Aarhus","Aarhus","Aarhus","Danemark","dk","Denmark","Dinamarca","à","en",56.16,10.21,False,True,False,True,-2624652,"arhus"),
    ("wroclaw","wroclaw","wroclaw","Wrocław","Wroclaw","Wrocław","Wrocław","Pologne","pl","Poland","Polonia","à","en",51.11,17.02,False,False,False,True,-3081368,"breslau wroclau"),

    # ── MALAISIE (2) ──
    ("malacca","malacca","malaca","Malacca","Malacca","Malacca","Malaca","Malaisie","my","Malaysia","Malasia","à","en",2.19,102.25,True,True,False,True,-1732903,"melaka"),
    ("kota-kinabalu","kota-kinabalu","kota-kinabalu","Kota Kinabalu","Kota Kinabalu","Kota Kinabalu","Kota Kinabalu","Malaisie","my","Malaysia","Malasia","à","en",5.98,116.07,True,True,True,True,-1733999,"sabah bornéo borneo"),

    # ── MEXIQUE (3) ──
    ("puerto-escondido","puerto-escondido","puerto-escondido","Puerto Escondido","Puerto Escondido","Puerto Escondido","Puerto Escondido","Mexique","mx","Mexico","México","à","en",15.86,-97.07,True,True,False,True,-3521081,"oaxaca surf"),
    ("san-miguel-de-allende","san-miguel-de-allende","san-miguel-de-allende","San Miguel de Allende","San Miguel de Allende","San Miguel de Allende","San Miguel de Allende","Mexique","mx","Mexico","México","à","en",20.91,-100.74,False,False,True,True,-3984671,""),
    ("merida","merida","merida","Mérida","Mérida","Mérida","Mérida","Mexique","mx","Mexico","México","à","en",20.97,-89.62,True,False,False,True,-3523349,"yucatan"),

    # ── VIETNAM (2) ──
    ("mui-ne","mui-ne","mui-ne","Mui Ne","Mui Ne","Mui Ne","Mui Né","Vietnam","vn","Vietnam","Vietnam","à","en",10.94,108.29,True,True,False,True,-1568574,"mui né kite surf"),
    ("quy-nhon","quy-nhon","quy-nhon","Quy Nhon","Quy Nhon","Quy Nhon","Quy Nhon","Vietnam","vn","Vietnam","Vietnam","à","en",13.77,109.23,True,True,False,True,-1568273,"binh dinh"),

    # ── OCÉANIE (3) ──
    ("palau","palau","palaos","Palaos","Palaos","Palau","Palaos","Palaos","pw","Palau","Palaos","aux","en",7.51,134.58,True,True,False,True,-1559582,"palau plongée diving"),
    ("bay-of-islands","bay-of-islands","bahia-de-las-islas","Bay of Islands","Bay of Islands","Bay of Islands","Bahía de las Islas","Nouvelle-Zélande","nz","New Zealand","Nueva Zelanda","dans la","en la",-35.23,174.11,False,True,False,True,-2193733,""),
    ("ischia","ischia","ischia","Ischia","Ischia","Ischia","Ischia","Italie","it","Italy","Italia","à","en",40.73,13.90,False,True,False,True,-3172616,"thermes thermal naples"),

    # ── ASIE CENTRALE (2) ──
    ("douchanbé","dushanbe","dushanbé","Douchanbé","Douchanbé","Dushanbe","Dushanbé","Tadjikistan","tj","Tajikistan","Tayikistán","à","en",38.56,68.77,False,False,True,True,-1221874,"tadjikistan tajikistan"),
    ("astana","astana","astana","Astana","Astana","Astana","Astana","Kazakhstan","kz","Kazakhstan","Kazajistán","à","en",51.18,71.45,False,False,False,True,-1526273,"nur sultan nour-sultan kazakhstan"),

    # ── ESPAGNE (2) ──
    ("salamanque","salamanca","salamanca","Salamanque","Salamanque","Salamanca","Salamanca","Espagne","es","Spain","España","à","en",40.96,-5.66,False,False,False,True,-3119841,""),
    ("tolede","toledo","toledo","Tolède","Tolède","Toledo","Toledo","Espagne","es","Spain","España","à","en",39.86,-4.02,False,False,False,True,-2510911,""),

    # ── PORTUGAL (1) ──
    ("alentejo","alentejo","alentejo","l'Alentejo","Alentejo","Alentejo","Alentejo","Portugal","pt","Portugal","Portugal","en","en el",38.56,-7.90,False,False,False,True,-2268806,"alentejo portugal plains"),

    # ── MICROSTATES (2) ──
    ("andorre","andorra","andorra","Andorre","Andorre","Andorra","Andorra","Andorre","ad","Andorra","Andorra","à","en",42.51,1.52,False,False,True,True,-3041565,"andorre ski"),
    ("gibraltar","gibraltar","gibraltar","Gibraltar","Gibraltar","Gibraltar","Gibraltar","Gibraltar","gi","Gibraltar","Gibraltar","à","en",36.14,-5.35,False,True,False,True,-2411586,""),

    # ── ITALIE suite (3) ──
    ("elba","elba","elba","l'île d'Elbe","Île d'Elbe","Elba Island","Isla de Elba","Italie","it","Italy","Italia","sur","en",42.78,10.28,False,True,False,True,-3176689,"ile d'elbe napoleon toscane"),
    ("pantelleria","pantelleria","pantelleria","Pantelleria","Pantelleria","Pantelleria","Pantelleria","Italie","it","Italy","Italia","à","en",36.84,11.96,False,True,False,True,-2523650,""),
    ("poznan","poznan","poznan","Poznań","Poznan","Poznań","Poznań","Pologne","pl","Poland","Polonia","à","en",52.41,16.93,False,False,False,True,-3088171,"poznan pologne"),

    # ── RESTE (5) ──
    ("ipoh","ipoh","ipoh","Ipoh","Ipoh","Ipoh","Ipoh","Malaisie","my","Malaysia","Malasia","à","en",4.60,101.07,True,False,False,True,-1736799,""),
    ("matsuyama","matsuyama","matsuyama","Matsuyama","Matsuyama","Matsuyama","Matsuyama","Japon","jp","Japan","Japón","à","en",33.84,132.77,False,True,False,True,-1857275,"shikoku onsen dogo"),
    ("trinidad-cuba","trinidad-cuba","trinidad-cuba","Trinidad","Trinidad","Trinidad","Trinidad","Cuba","cu","Cuba","Cuba","à","en",21.80,-79.98,True,False,False,True,-3537728,"trinidad cuba colonial"),
    ("taupo","taupo","taupo","Taupo","Taupo","Taupo","Taupo","Nouvelle-Zélande","nz","New Zealand","Nueva Zelanda","à","en",-38.69,176.08,False,False,False,True,-2183619,"lac taupo geysers nouvelle zelande"),
    ("loreto-mexique","loreto-baja","loreto-baja","Loreto","Loreto","Loreto","Loreto","Mexique","mx","Mexico","México","à","en",26.01,-111.34,False,True,False,True,-3996322,"basse californie mer cortez"),
]

# ── hero_sub generation via Claude API ────────────────────────────────────────

def generate_hero_subs(client, nom_fr, nom_en, nom_es, pays, country_en, coastal, mountain, tropical):
    """Generate hero_sub_fr, hero_sub_en, hero_sub_es for a destination."""
    prompt = f"""Tu génères des taglines courtes (1-2 phrases, 20-35 mots) pour un site météo voyage.

Destination: {nom_fr} ({nom_en} / {nom_es})
Pays: {pays} ({country_en})
Coastal: {coastal}, Mountain: {mountain}, Tropical: {tropical}

Génère exactement un JSON avec ces 3 clés:
{{
  "fr": "Tagline en français — commence par le nom de la destination, décrit le caractère unique en lien avec la météo/saisons/expérience voyageur",
  "en": "Tagline in English — same structure",
  "es": "Tagline en español — misma estructura"
}}

Règles:
- Commence toujours par le nom de la ville/destination
- Mentionne 1-2 aspects concrets (type de paysage, activité phare, fait météo)
- Ton factuel et attrayant, pas publicitaire
- Pas de guillemets dans le texte
- JSON uniquement, pas d'explication"""

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=400,
        messages=[{"role": "user", "content": prompt}]
    )
    text = response.content[0].text.strip()
    # Strip markdown fences if any
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    return json.loads(text.strip())


def main():
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        # Try to get from git config or env
        api_key = os.popen("echo $ANTHROPIC_API_KEY").read().strip()

    client = anthropic.Anthropic(api_key=api_key) if api_key else None

    # Load existing
    rows = list(csv.DictReader(open(CSV_PATH, encoding='utf-8-sig')))
    existing_slugs = {r['slug_fr'] for r in rows}
    fieldnames = list(rows[0].keys())

    print(f"Existing destinations: {len(rows)}")
    new_to_add = [d for d in NEW_DESTINATIONS if d[0] not in existing_slugs]
    print(f"New to add: {len(new_to_add)}")

    if not new_to_add:
        print("Nothing to add.")
        return

    # Progress file
    progress_file = os.path.join(DIR, 'data', 'add105_progress.json')
    progress = {}
    if os.path.exists(progress_file):
        progress = json.load(open(progress_file))

    new_rows = []
    for i, dest in enumerate(new_to_add):
        (slug_fr, slug_en, slug_es, nom_fr, nom_bare, nom_en, nom_es,
         pays, flag, country_en, country_es, prep_fr, prep_es,
         lat, lon, tropical, coastal, mountain, monthly, booking_dest_id, aliases) = dest

        print(f"[{i+1}/{len(new_to_add)}] {nom_fr}...", end=" ", flush=True)

        # Get hero_subs
        if slug_fr in progress:
            subs = progress[slug_fr]
            print("(cached)")
        elif client:
            try:
                subs = generate_hero_subs(client, nom_fr, nom_en, nom_es, pays, country_en, coastal, mountain, tropical)
                progress[slug_fr] = subs
                json.dump(progress, open(progress_file, 'w'), ensure_ascii=False, indent=2)
                print("✓")
                time.sleep(0.3)  # gentle rate limit
            except Exception as e:
                print(f"ERROR: {e}")
                subs = {"fr": "", "en": "", "es": ""}
        else:
            print("(no API key — empty subs)")
            subs = {"fr": "", "en": "", "es": ""}

        row = {
            'slug_fr': slug_fr,
            'slug_en': slug_en,
            'nom_fr': nom_fr,
            'nom_bare': nom_bare,
            'pays': pays,
            'flag': flag,
            'prep_fr': prep_fr,
            'lat': lat,
            'lon': lon,
            'tropical': tropical,
            'hero_sub_fr': subs.get('fr', ''),
            'booking_dest_id': booking_dest_id,
            'nom_en': nom_en,
            'country_en': country_en,
            'country_es': country_es,
            'hero_sub_en': subs.get('en', ''),
            'monthly': monthly,
            'mountain': mountain,
            'aliases': aliases,
            'coastal': coastal,
            'nom_es': nom_es,
            'slug_es': slug_es,
            'prep_es': prep_es,
            'hero_sub_es': subs.get('es', ''),
        }
        new_rows.append(row)

    # Append to CSV
    with open(CSV_PATH, 'a', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writerows(new_rows)

    print(f"\n✅ Added {len(new_rows)} destinations to {CSV_PATH}")

    # Cleanup progress file
    if os.path.exists(progress_file):
        os.remove(progress_file)

if __name__ == '__main__':
    main()
