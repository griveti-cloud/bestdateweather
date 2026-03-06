#!/usr/bin/env python3
"""Ajoute/met à jour le champ 'coastal' dans destinations.csv."""
import csv

# Destinations clairement sans accès mer direct
INLAND = {
    # France intérieur
    'paris','lyon','bordeaux','toulouse','strasbourg','lille','nantes','rennes',
    'clermont-ferrand','dijon','grenoble','reims','montpellier','alsace','dordogne',
    # Allemagne/Autriche/Suisse
    'berlin','munich','vienne','zurich','geneve','berne','luxembourg','francfort',
    # Europe centrale/est
    'budapest','prague','varsovie','cracovie','bratislava','sofia','bucarest',
    'belgrade','zagreb','sarajevo','tirana','skopje','lviv','transylvanie',
    # Îles/lacs alpins
    'hallstatt','lac-bled','lac-come','lac-garde','annecy',
    # Moyen-Orient intérieur
    'riyad','amman','petra','wadi-rum','jerash','jerusalem','al-ula','ispahan','teheran',
    # Afrique intérieure
    'nairobi','addis-abeba','kampala','kigali','harare','lusaka','arusha','gondar',
    'lalibela','johannesburg','maun','etosha','windhoek','victoria-falls','livingstone',
    # Asie intérieure
    'katmandou','bhutan','pokhara','nepal','delhi','agra','jaipur','varanasi',
    'udaipur','jodhpur','pekin','xian','chengdu','lijiang','guilin','zhangjiajie',
    'kyoto','nara','osaka', # osaka a une baie mais pas de vraie plage
    'seoul','taipei',
    # Asie centrale
    'samarcande','boukhara','khiva','tachkent','ouzbekistan','mongolie','almaty',
    # Amérique du Sud intérieur
    'bogota','medellin','quito','cuzco','machu-picchu','cusco-ville','la-paz',
    'sucre','asuncion','la-paz-bolivie','mendoza','sao-paulo','guanajuato',
    'san-cristobal','antigua-guatemala',
    # Mexique intérieur
    'mexico','oaxaca','guadalajara','monterrey',
    # USA intérieur
    'chicago','denver','las-vegas','phoenix','nashville','atlanta','austin',
    'san-antonio','napa-valley','sedona','yellowstone','orlando','washington',
    'memphis',
    # Canada intérieur
    'montreal',
    # Russie intérieur
    'moscou',
    # Maroc intérieur
    'marrakech','fes','ouarzazate','merzouga','chefchaouen','ronda',
    # Divers intérieur
    'cappadoce','ankara','plitvice','ohrid','lac-ohrid','oaxaca',
    'jakarta', # grande ville côtière mais pas destination plage
    'mandalay','kandy','rotorua','uluru','livingstone',
    'patagonie', # vaste région, pas de plage tropicale
    'laponie', # froid, pas de baignade
    'svalbard', # polaire
    'anchorage', # froid
    'yellowstone','portland',
    'provence','normandie','bretagne', # régions françaises côtières mais pas "plage" au sens strict
    # Jordanie/Pérou/Bolivie en tant que pays interior-dominant
    'jordanie','bolivie','perou',
}

# Destinations clairement avec accès mer/plage
COASTAL = {
    # France côtière
    'nice','cannes','marseille','biarritz','la-rochelle','saint-malo','monaco',
    'corse','cote-azur','pays-basque',
    # Espagne côtière
    'barcelone','valence','malaga','marbella','cadix','bilbao','alicante',
    'costa-brava','costa-del-sol','ibiza','majorque','minorque','formentera',
    'palma-de-majorque','lanzarote','fuerteventura','gran-canaria','tenerife',
    'el-hierro','la-palma','la-gomera','canaries','algarve',
    # Portugal
    'lisbonne','porto','funchal','faro','sintra','madere','acores','sao-miguel',
    # Italie côtière
    'rome','naples','genes','ancone','bari','palerme','catane','siracuse',
    'amalfi','capri','cinque-terre','sorrente','ravello','taormina',
    'sardaigne','sicile','lecce','pouilles','trieste','venise','lac-come',
    # Grèce
    'athenes','thessalonique','rhodes','corfou','mykonos','santorin','crete',
    'zakynthos','kos','naxos','paros','milos','hydra','kefalonia','lefkada',
    'peloponnese','hvar',
    # Croatie/Balkans côtiers
    'dubrovnik','split','kotor','tivat','zadar','trogir','piran','budva',
    'hvar','lac-bled',
    # Méditerranée orientale
    'istanbul','antalya','bodrum','fethiye','izmir','alacati','larnaca','paphos',
    'chypre','malte','gozo','djerba','hammamet',
    # Afrique du Nord côtière
    'casablanca','tanger','agadir','essaouira','tunis','sfax','marsa-alam',
    'hurghada','sharm-el-sheikh','aqaba','salalah',
    # Moyen-Orient côtier
    'dubai','abu-dhabi','doha','muscat','bahrein','koweït','ras-al-khaimah',
    # Afrique subsaharienne côtière
    'lagos','accra','dakar','abidjan','mombasa','dar-es-salaam','zanzibar',
    'le-cap','durban','cape-town',
    # Scandinavie côtière
    'oslo','bergen','stockholm','helsinki','copenhague','reykjavik','riga',
    'tallinn','vilnius','gdansk','lofoten','tromso','göteborg',
    # Îles atlantiques
    'bermudes','svalbard','saint-pierre-et-miquelon',
    # UK/Ireland côtier
    'dublin','edimbourg','londres','wild-atlantic-way',
    # Inde côtière
    'mumbai','goa','chennai','kochi','colombo',
    # Asie du Sud-Est côtière
    'singapore','penang','danang','da-nang','hoi-an','ho-chi-minh','hanoi',
    'phuket','koh-samui','krabi','bangkok','bali','lombok','flores',
    'boracay','cebu','palawan','manille',
    # Asie du Nord-Est côtière
    'tokyo','hiroshima','nagasaki','busan','osaka','seoul',
    'jeju',
    # Japon/Corée
    'osaka',
    # Océanie
    'sydney','melbourne','brisbane','perth','cairns','hobart','gold-coast',
    'auckland','christchurch','wellington','nouvelle-zelande','rotorua',
    # Amériques côtières
    'new-york','miami','los-angeles','san-francisco','seattle','boston',
    'vancouver','toronto','montreal','quebec-ville','san-diego',
    'charleston','savannah','savannah-ga','nouvelle-orleans','key-west',
    'cancun','playa-del-carmen','tulum','los-cabos','puerto-vallarta',
    'acapulco','cabo-san-lucas',
    'lima','valparaiso','montevideo','buenos-aires','rio-de-janeiro',
    'florianopolis','natal','fortaleza','salvador-de-bahia','recife','santiago',
    'cartagene','santa-marta',
    'la-havane','varadero','punta-cana','saint-domingue','fort-de-france',
    'pointe-a-pitre','jamaique','barbade','saint-martin','saint-barth',
    'martinique','guadeloupe','guyane',
    # Îles et paradis tropicaux
    'maldives','seychelles','ile-maurice','reunion','mayotte','tahiti',
    'bora-bora','nouvelle-caledonie','hawaii','fiji',
    'cap-vert',
    # Moyen-Orient et Afrique orientale
    'tel-aviv','beyrouth','alexandrie','oman',
    'djerba','hammamet',
    # Balkans côtiers
    'albanie','montenegro',
    # Divers clairement côtiers
    'bergen','bergen-op-zoom',
    'edinbourg','edimbourg',
    'bahrein','oman',
    'sao-miguel','acores',
    'la-rochelle',
    # Régions côtières
    'normandie','bretagne',
    # Autres
    'al-ula',  # désert, pas côtier
    'taiwan','hong-kong','macao',
    'phnom-penh','siem-reap',
    'rangoun','yangon',
    # Divers unknowns qui sont clairement côtiers
    'georgie',  # Géorgie a Batoumi sur la mer Noire
    'chili',    # façade pacifique
    'uruguay',  # côtier
    'paros','naxos','milos',
    'pouilles','cinque-terre',
    'cote-azur','costa-brava',
    'adelaide','hobart',
    'ghent',  # belgique intérieure → INLAND
    'bruges',  # Belgique nord, pas vraiment mer → INLAND
}

# Quelques corrections
INLAND.add('ghent')
INLAND.add('bruges')
INLAND.discard('osaka')
INLAND.discard('seoul')
COASTAL.discard('patagonie')
COASTAL.discard('laponie')
COASTAL.discard('svalbard')
COASTAL.discard('anchorage')
COASTAL.discard('normandie')
COASTAL.discard('bretagne')
COASTAL.discard('al-ula')

def get_coastal(slug, tropical, mountain):
    if slug in COASTAL: return True
    if slug in INLAND: return False
    if mountain: return False
    if tropical: return True
    return True  # défaut : True (mieux vaut afficher que masquer par erreur)

with open('data/destinations.csv', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames
    rows = list(reader)

# Add coastal column if missing
if 'coastal' not in fieldnames:
    fieldnames = list(fieldnames) + ['coastal']

for r in rows:
    slug = r['slug_fr']
    tropical = r.get('tropical','False') == 'True'
    mountain = r.get('mountain','False') == 'True'
    r['coastal'] = str(get_coastal(slug, tropical, mountain))

# Write back
with open('data/destinations.csv', 'w', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

# Report
coastal_t = sum(1 for r in rows if r['coastal']=='True')
coastal_f = sum(1 for r in rows if r['coastal']=='False')
print(f"coastal=True: {coastal_t}, coastal=False: {coastal_f}")

# Spot check
checks = ['paris','nice','bali','chamonix','marrakech','dubai','guyane','budapest','reykjavik','kyoto','tokyo']
for r in rows:
    if r['slug_fr'] in checks:
        print(f"  {r['slug_fr']}: coastal={r['coastal']}")
