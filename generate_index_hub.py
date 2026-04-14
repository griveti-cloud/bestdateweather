#!/usr/bin/env python3
"""Regenerate SEO destination hub: search + 6 accordions + sub-accordions."""
import csv, re, os
import html as html_mod
from lib.regions import reg as _reg_pilier, NON_EUROPE_SLUGS, MACARONESIA_SLUGS

# ── slug → (mega_region, sub_region) overrides ──
# Priorité sur MAPPING[pays] pour les territoires géographiquement hors-métropole
SLUG_OVERRIDE = {
    # DOM-TOM français → régions géographiques
    'guadeloupe':     ('caraïbes', 'Caraïbes'),
    'martinique':     ('caraïbes', 'Caraïbes'),
    'saint-martin':   ('caraïbes', 'Caraïbes'),
    'saint-barthelemy': ('caraïbes', 'Caraïbes'),
    'guyane':         ('ameriques-s', 'Amérique du Sud'),
    'reunion':        ('af-sub', 'Océan Indien'),
    'mayotte':        ('af-sub', 'Océan Indien'),
    'polynesie':      ('oceanie', 'Pacifique & Outre-mer'),
    'bora-bora':      ('oceanie', 'Pacifique & Outre-mer'),
    'nouvelle-caledonie': ('oceanie', 'Pacifique & Outre-mer'),
    'saint-pierre-et-miquelon': ('ameriques-n', 'Amérique du Nord'),
    # Bermudes (Royaume-Uni) → Caraïbes
    'bermudes':       ('caraïbes', 'Caraïbes'),
    # Canaries/Madère/Cap-Vert → Îles Atlantiques
    'canaries':       ('atl', 'Îles Atlantiques'),
    'tenerife':       ('atl', 'Îles Atlantiques'),
    'gran-canaria':   ('atl', 'Îles Atlantiques'),
    'fuerteventura':  ('atl', 'Îles Atlantiques'),
    'lanzarote':      ('atl', 'Îles Atlantiques'),
    'la-palma':       ('atl', 'Îles Atlantiques'),
    'la-gomera':      ('atl', 'Îles Atlantiques'),
    'el-hierro':      ('atl', 'Îles Atlantiques'),
    # Macaronésie → Îles Atlantiques
    'madere':         ('atl', 'Îles Atlantiques'),
    'funchal':        ('atl', 'Îles Atlantiques'),
    'cap-vert':       ('atl', 'Îles Atlantiques'),
    'sal':            ('atl', 'Îles Atlantiques'),
    'praia':          ('atl', 'Îles Atlantiques'),
    'azores':         ('atl', 'Îles Atlantiques'),
}

# ── pays → (mega_region, sub_region) ──
MAPPING = {
    'France': ('europe', 'Europe du Sud & Méditerranée'),
    # EUROPE
    'Albanie': ('europe', 'Europe du Sud & Méditerranée'),
    'Bosnie-Herzégovine': ('europe', 'Europe du Sud & Méditerranée'),
    'Chypre': ('europe', 'Europe du Sud & Méditerranée'),
    'Croatie': ('europe', 'Europe du Sud & Méditerranée'),
    'Espagne': ('europe', 'Europe du Sud & Méditerranée'),
    'Grèce': ('europe', 'Europe du Sud & Méditerranée'),
    'Italie': ('europe', 'Europe du Sud & Méditerranée'),
    'Macédoine du Nord': ('europe', 'Europe du Sud & Méditerranée'),
    'Malte': ('europe', 'Europe du Sud & Méditerranée'),
    'Monaco': ('europe', 'Europe du Sud & Méditerranée'),
    'Monténégro': ('europe', 'Europe du Sud & Méditerranée'),
    'Portugal': ('europe', 'Europe du Sud & Méditerranée'),
    'Serbie': ('europe', 'Europe du Sud & Méditerranée'),
    'Slovénie': ('europe', 'Europe du Sud & Méditerranée'),
    'Turquie': ('europe', 'Europe du Sud & Méditerranée'),
    'Allemagne': ('europe', 'Europe du Nord & Centrale'),
    'Autriche': ('europe', 'Europe du Nord & Centrale'),
    'Belgique': ('europe', 'Europe du Nord & Centrale'),
    'Bulgarie': ('europe', 'Europe du Nord & Centrale'),
    'Hongrie': ('europe', 'Europe du Nord & Centrale'),
    'Irlande': ('europe', 'Europe du Nord & Centrale'),
    'Islande': ('europe', 'Europe du Nord & Centrale'),
    'Pays-Bas': ('europe', 'Europe du Nord & Centrale'),
    'Pologne': ('europe', 'Europe du Nord & Centrale'),
    'Roumanie': ('europe', 'Europe du Nord & Centrale'),
    'Royaume-Uni': ('europe', 'Europe du Nord & Centrale'),
    'Slovaquie': ('europe', 'Europe du Nord & Centrale'),
    'Suisse': ('europe', 'Europe du Nord & Centrale'),
    'Tchéquie': ('europe', 'Europe du Nord & Centrale'),
    'Écosse': ('europe', 'Europe du Nord & Centrale'),
    'Danemark': ('europe', 'Scandinavie & Baltique'),
    'Estonie': ('europe', 'Scandinavie & Baltique'),
    'Finlande': ('europe', 'Scandinavie & Baltique'),
    'Lettonie': ('europe', 'Scandinavie & Baltique'),
    'Lituanie': ('europe', 'Scandinavie & Baltique'),
    'Norvège': ('europe', 'Scandinavie & Baltique'),
    'Suède': ('europe', 'Scandinavie & Baltique'),
    'Géorgie': ('europe', 'Caucase & Asie Centrale'),
    'Arménie': ('europe', 'Caucase & Asie Centrale'),
    'Azerbaïdjan': ('europe', 'Caucase & Asie Centrale'),
    'Tadjikistan': ('europe', 'Caucase & Asie Centrale'),
    'Kazakhstan': ('europe', 'Caucase & Asie Centrale'),
    'Kirghizistan': ('europe', 'Caucase & Asie Centrale'),
    'Ouzbékistan': ('europe', 'Caucase & Asie Centrale'),
    'Andorre': ('europe', 'Europe du Sud & Méditerranée'),
    'Gibraltar': ('europe', 'Europe du Sud & Méditerranée'),
    'Ukraine': ('europe', 'Europe du Nord & Centrale'),
    # AFRIQUE & MOYEN-ORIENT
    'Maroc': ('af-nord', 'Afrique du Nord'),
    'Algérie': ('af-nord', 'Afrique du Nord'),
    'Tunisie': ('af-nord', 'Afrique du Nord'),
    'Égypte': ('af-nord', 'Afrique du Nord'),
    'Cap-Vert': ('atl', 'Îles Atlantiques'),
    "Côte d'Ivoire": ('afrique-mo', "Afrique de l'Ouest"),
    'Ghana': ('af-sub', "Afrique de l'Ouest"),
    'Nigeria': ('af-sub', "Afrique de l'Ouest"),
    'Sénégal': ('af-sub', "Afrique de l'Ouest"),
    'Burkina Faso': ('af-sub', "Afrique de l'Ouest"),
    'Bénin': ('af-sub', "Afrique de l'Ouest"),
    'Cameroun': ('af-sub', "Afrique de l'Ouest"),
    'Sierra Leone': ('af-sub', "Afrique de l'Ouest"),
    'Togo': ('af-sub', "Afrique de l'Ouest"),
    'Gabon': ('af-sub', "Afrique de l'Ouest"),
    'Gambie': ('af-sub', "Afrique de l'Ouest"),
    'Kenya': ('af-sub', "Afrique de l'Est"),
    'Ouganda': ('af-sub', "Afrique de l'Est"),
    'Rwanda': ('af-sub', "Afrique de l'Est"),
    'Tanzanie': ('af-sub', "Afrique de l'Est"),
    'Éthiopie': ('af-sub', "Afrique de l'Est"),
    'Afrique du Sud': ('af-sub', 'Afrique australe'),
    'Mozambique': ('af-sub', 'Afrique australe'),
    'Namibie': ('af-sub', 'Afrique australe'),
    'Zimbabwe': ('af-sub', 'Afrique australe'),
    'Botswana': ('af-sub', 'Afrique australe'),
    'Zambie': ('af-sub', 'Afrique australe'),
    'Malawi': ('af-sub', 'Afrique australe'),
    'Madagascar': ('af-sub', 'Océan Indien'),
    'Maurice': ('af-sub', 'Océan Indien'),
    'Seychelles': ('af-sub', 'Océan Indien'),
    'Arabie Saoudite': ('me', 'Moyen-Orient'),
    'Bahreïn': ('me', 'Moyen-Orient'),
    'Iran': ('me', 'Moyen-Orient'),
    'Israël': ('me', 'Moyen-Orient'),
    'Jordanie': ('me', 'Moyen-Orient'),
    'Koweït': ('me', 'Moyen-Orient'),
    'Liban': ('me', 'Moyen-Orient'),
    'Oman': ('me', 'Moyen-Orient'),
    'Qatar': ('me', 'Moyen-Orient'),
    'Émirats Arabes Unis': ('me', 'Moyen-Orient'),
    'Émirats arabes unis': ('me', 'Moyen-Orient'),
    'Yémen': ('me', 'Moyen-Orient'),
    # ASIE
    'Cambodge': ('asie', 'Asie du Sud-Est'),
    'Indonésie': ('asie', 'Asie du Sud-Est'),
    'Laos': ('asie', 'Asie du Sud-Est'),
    'Malaisie': ('asie', 'Asie du Sud-Est'),
    'Myanmar': ('asie', 'Asie du Sud-Est'),
    'Philippines': ('asie', 'Asie du Sud-Est'),
    'Singapour': ('asie', 'Asie du Sud-Est'),
    'Thaïlande': ('asie', 'Asie du Sud-Est'),
    'Viêt Nam': ('asie', 'Asie du Sud-Est'),
    'Chine': ('asie', "Asie de l'Est"),
    'Corée du Sud': ('asie', "Asie de l'Est"),
    'Hong Kong': ('asie', "Asie de l'Est"),
    'Japon': ('asie', "Asie de l'Est"),
    'Macao': ('asie', "Asie de l'Est"),
    'Taïwan': ('asie', "Asie de l'Est"),
    'Mongolie': ('asie', "Asie de l'Est"),
    'Inde': ('asie', 'Asie du Sud'),
    'Bhoutan': ('asie', 'Asie du Sud'),
    'Maldives': ('asie', 'Asie du Sud'),
    'Népal': ('asie', 'Asie du Sud'),
    'Sri Lanka': ('asie', 'Asie du Sud'),
    # AMÉRIQUES
    'Canada': ('ameriques-n', 'Amérique du Nord'),
    'États-Unis': ('ameriques-n', 'Amérique du Nord'),
    'Antigua-et-Barbuda': ('caraïbes', 'Caraïbes'),
    'Aruba': ('caraïbes', 'Caraïbes'),
    'Bahamas': ('caraïbes', 'Caraïbes'),
    'Barbade': ('caraïbes', 'Caraïbes'),
    'Cuba': ('caraïbes', 'Caraïbes'),
    'Curaçao': ('caraïbes', 'Caraïbes'),
    'Jamaïque': ('caraïbes', 'Caraïbes'),
    'Porto Rico': ('caraïbes', 'Caraïbes'),
    'République Dominicaine': ('caraïbes', 'Caraïbes'),
    'Sainte-Lucie': ('caraïbes', 'Caraïbes'),
    'Trinité-et-Tobago': ('caraïbes', 'Caraïbes'),
    'Turks-et-Caïcos': ('caraïbes', 'Caraïbes'),
    'Dominique': ('caraïbes', 'Caraïbes'),
    'Pays-Bas caribéens': ('caraïbes', 'Caraïbes'),
    'Saint-Vincent-et-les-Grenadines': ('caraïbes', 'Caraïbes'),
    'Îles Caïmans': ('caraïbes', 'Caraïbes'),
    'Îles Vierges américaines': ('caraïbes', 'Caraïbes'),
    'Belize': ('ameriques-n', 'Mexique & Amérique Centrale'),
    'Costa Rica': ('ameriques-n', 'Mexique & Amérique Centrale'),
    'Guatemala': ('ameriques-n', 'Mexique & Amérique Centrale'),
    'Honduras': ('ameriques-n', 'Mexique & Amérique Centrale'),
    'Mexique': ('ameriques-n', 'Mexique & Amérique Centrale'),
    'Nicaragua': ('ameriques-n', 'Mexique & Amérique Centrale'),
    'Panama': ('ameriques-n', 'Mexique & Amérique Centrale'),
    'Argentine': ('ameriques-s', 'Amérique du Sud'),
    'Bolivie': ('ameriques-s', 'Amérique du Sud'),
    'Brésil': ('ameriques-s', 'Amérique du Sud'),
    'Chili': ('ameriques-s', 'Amérique du Sud'),
    'Colombie': ('ameriques-s', 'Amérique du Sud'),
    'Paraguay': ('ameriques-s', 'Amérique du Sud'),
    'Pérou': ('ameriques-s', 'Amérique du Sud'),
    'Uruguay': ('ameriques-s', 'Amérique du Sud'),
    'Équateur': ('ameriques-s', 'Amérique du Sud'),
    # OCÉANIE & OUTRE-MER
    'Australie': ('oceanie', 'Australie & Nouvelle-Zélande'),
    'Nouvelle-Zélande': ('oceanie', 'Australie & Nouvelle-Zélande'),
    'Fidji': ('oceanie', 'Pacifique & Outre-mer'),
    'Îles Cook': ('oceanie', 'Pacifique & Outre-mer'),
    'Nouvelle-Calédonie': ('oceanie', 'Pacifique & Outre-mer'),
    'Polynésie française': ('oceanie', 'Pacifique & Outre-mer'),
    'Samoa': ('oceanie', 'Pacifique & Outre-mer'),
    'Tonga': ('oceanie', 'Pacifique & Outre-mer'),
    'Vanuatu': ('oceanie', 'Pacifique & Outre-mer'),
    'Papouasie-Nouvelle-Guinée': ('oceanie', 'Pacifique & Outre-mer'),
    'Palaos': ('oceanie', 'Pacifique & Outre-mer'),
    'Vietnam': ('asie', 'Asie du Sud-Est'),
}

# ── Country name translations {fr_name: {fr, en, es}} ──
COUNTRY_NAMES_TRANS = {
    'Afrique du Sud':{'fr':'Afrique du Sud','en':'South Africa','es':'Sudáfrica','de':'Südafrika'},
    'Albanie':{'fr':'Albanie','en':'Albania','es':'Albania','de':'Albanien'},
    'Algérie':{'fr':'Algérie','en':'Algeria','es':'Argelia','de':'Algerien'},
    'Allemagne':{'fr':'Allemagne','en':'Germany','es':'Alemania','de':'Deutschland'},
    'Andorre':{'fr':'Andorre','en':'Andorra','es':'Andorra','de':'Andorra'},
    'Antigua-et-Barbuda':{'fr':'Antigua-et-Barbuda','en':'Antigua & Barbuda','es':'Antigua y Barbuda','de':'Antigua und Barbuda'},
    'Arabie Saoudite':{'fr':'Arabie Saoudite','en':'Saudi Arabia','es':'Arabia Saudita','de':'Saudi-Arabien'},
    'Argentine':{'fr':'Argentine','en':'Argentina','es':'Argentina','de':'Argentinien'},
    'Arménie':{'fr':'Arménie','en':'Armenia','es':'Armenia','de':'Armenien'},
    'Aruba':{'fr':'Aruba','en':'Aruba','es':'Aruba','de':'Aruba'},
    'Australie':{'fr':'Australie','en':'Australia','es':'Australia','de':'Australien'},
    'Azerbaïdjan':{'fr':'Azerbaïdjan','en':'Azerbaijan','es':'Azerbaiyán','de':'Aserbaidschan'},
    'Autriche':{'fr':'Autriche','en':'Austria','es':'Austria','de':'Österreich'},
    'Bahamas':{'fr':'Bahamas','en':'Bahamas','es':'Bahamas','de':'Bahamas'},
    'Bahreïn':{'fr':'Bahreïn','en':'Bahrain','es':'Baréin','de':'Bahrain'},
    'Barbade':{'fr':'Barbade','en':'Barbados','es':'Barbados','de':'Barbados'},
    'Belgique':{'fr':'Belgique','en':'Belgium','es':'Bélgica','de':'Belgien'},
    'Belize':{'fr':'Belize','en':'Belize','es':'Belice','de':'Belize'},
    'Bhoutan':{'fr':'Bhoutan','en':'Bhutan','es':'Bután','de':'Bhutan'},
    'Bolivie':{'fr':'Bolivie','en':'Bolivia','es':'Bolivia','de':'Bolivien'},
    'Bosnie-Herzégovine':{'fr':'Bosnie-Herzégovine','en':'Bosnia & Herzegovina','es':'Bosnia y Herzegovina','de':'Bosnien und Herzegowina'},
    'Botswana':{'fr':'Botswana','en':'Botswana','es':'Botsuana','de':'Botswana'},
    'Brésil':{'fr':'Brésil','en':'Brazil','es':'Brasil','de':'Brasilien'},
    'Bulgarie':{'fr':'Bulgarie','en':'Bulgaria','es':'Bulgaria','de':'Bulgarien'},
    'Burkina Faso':{'fr':'Burkina Faso','en':'Burkina Faso','es':'Burkina Faso','de':'Burkina Faso'},
    'Bénin':{'fr':'Bénin','en':'Benin','es':'Benín','de':'Benin'},
    'Cambodge':{'fr':'Cambodge','en':'Cambodia','es':'Camboya','de':'Kambodscha'},
    'Cameroun':{'fr':'Cameroun','en':'Cameroon','es':'Camerún','de':'Kamerun'},
    'Canada':{'fr':'Canada','en':'Canada','es':'Canadá','de':'Kanada'},
    'Cap-Vert':{'fr':'Cap-Vert','en':'Cape Verde','es':'Cabo Verde','de':'Kap Verde'},
    'Chili':{'fr':'Chili','en':'Chile','es':'Chile','de':'Chile'},
    'Chine':{'fr':'Chine','en':'China','es':'China','de':'China'},
    'Chypre':{'fr':'Chypre','en':'Cyprus','es':'Chipre','de':'Zypern'},
    'Colombie':{'fr':'Colombie','en':'Colombia','es':'Colombia','de':'Kolumbien'},
    'Corée du Sud':{'fr':'Corée du Sud','en':'South Korea','es':'Corea del Sur','de':'Südkorea'},
    'Costa Rica':{'fr':'Costa Rica','en':'Costa Rica','es':'Costa Rica','de':'Costa Rica'},
    'Croatie':{'fr':'Croatie','en':'Croatia','es':'Croacia','de':'Kroatien'},
    'Cuba':{'fr':'Cuba','en':'Cuba','es':'Cuba','de':'Kuba'},
    'Curaçao':{'fr':'Curaçao','en':'Curaçao','es':'Curazao','de':'Curaçao'},
    "Côte d'Ivoire":{'fr':"Côte d'Ivoire",'en':'Ivory Coast','es':'Costa de Marfil'},
    'Danemark':{'fr':'Danemark','en':'Denmark','es':'Dinamarca','de':'Dänemark'},
    'Dominique':{'fr':'Dominique','en':'Dominica','es':'Dominica','de':'Dominica'},
    'Espagne':{'fr':'Espagne','en':'Spain','es':'España','de':'Spanien'},
    'Estonie':{'fr':'Estonie','en':'Estonia','es':'Estonia','de':'Estonia'},
    'Fidji':{'fr':'Fidji','en':'Fiji','es':'Fiyi','de':'Fidschi'},
    'Finlande':{'fr':'Finlande','en':'Finland','es':'Finlandia','de':'Finnland'},
    'France':{'fr':'France','en':'France','es':'Francia','de':'Frankreich'},
    'Ghana':{'fr':'Ghana','en':'Ghana','es':'Ghana','de':'Ghana'},
    'Grèce':{'fr':'Grèce','en':'Greece','es':'Grecia','de':'Griechenland'},
    'Guatemala':{'fr':'Guatemala','en':'Guatemala','es':'Guatemala','de':'Guatemala'},
    'Géorgie':{'fr':'Géorgie','en':'Georgia','es':'Georgia','de':'Georgien'},
    'Honduras':{'fr':'Honduras','en':'Honduras','es':'Honduras','de':'Honduras'},
    'Hongrie':{'fr':'Hongrie','en':'Hungary','es':'Hungría','de':'Ungarn'},
    'Inde':{'fr':'Inde','en':'India','es':'India','de':'Indien'},
    'Indonésie':{'fr':'Indonésie','en':'Indonesia','es':'Indonesia','de':'Indonesien'},
    'Iran':{'fr':'Iran','en':'Iran','es':'Irán','de':'Iran'},
    'Irlande':{'fr':'Irlande','en':'Ireland','es':'Irlanda','de':'Irland'},
    'Islande':{'fr':'Islande','en':'Iceland','es':'Islandia','de':'Island'},
    'Israël':{'fr':'Israël','en':'Israel','es':'Israel','de':'Israel'},
    'Italie':{'fr':'Italie','en':'Italy','es':'Italia','de':'Italien'},
    'Jamaïque':{'fr':'Jamaïque','en':'Jamaica','es':'Jamaica','de':'Jamaika'},
    'Japon':{'fr':'Japon','en':'Japan','es':'Japón','de':'Japan'},
    'Jordanie':{'fr':'Jordanie','en':'Jordan','es':'Jordania','de':'Jordanien'},
    'Kazakhstan':{'fr':'Kazakhstan','en':'Kazakhstan','es':'Kazajistán','de':'Kasachstan'},
    'Kenya':{'fr':'Kenya','en':'Kenya','es':'Kenia','de':'Kenia'},
    'Kirghizistan':{'fr':'Kirghizistan','en':'Kyrgyzstan','es':'Kirguistán','de':'Kirgisistan'},
    'Koweït':{'fr':'Koweït','en':'Kuwait','es':'Kuwait','de':'Kuwait'},
    'Laos':{'fr':'Laos','en':'Laos','es':'Laos','de':'Laos'},
    'Lettonie':{'fr':'Lettonie','en':'Latvia','es':'Letonia','de':'Latvia'},
    'Liban':{'fr':'Liban','en':'Lebanon','es':'Líbano','de':'Libanon'},
    'Lituanie':{'fr':'Lituanie','en':'Lithuania','es':'Lituania','de':'Lithuania'},
    'Macédoine du Nord':{'fr':'Macédoine du Nord','en':'North Macedonia','es':'Macedonia del Norte','de':'Nordmazedonien'},
    'Madagascar':{'fr':'Madagascar','en':'Madagascar','es':'Madagascar','de':'Madagaskar'},
    'Malaisie':{'fr':'Malaisie','en':'Malaysia','es':'Malasia','de':'Malaysia'},
    'Maldives':{'fr':'Maldives','en':'Maldives','es':'Maldivas','de':'Malediven'},
    'Malte':{'fr':'Malte','en':'Malta','es':'Malta','de':'Malta'},
    'Maroc':{'fr':'Maroc','en':'Morocco','es':'Marruecos','de':'Marokko'},
    'Maurice':{'fr':'Maurice','en':'Mauritius','es':'Mauricio','de':'Mauritius'},
    'Mexique':{'fr':'Mexique','en':'Mexico','es':'México','de':'Mexiko'},
    'Monaco':{'fr':'Monaco','en':'Monaco','es':'Mónaco','de':'Monaco'},
    'Mongolie':{'fr':'Mongolie','en':'Mongolia','es':'Mongolia','de':'Mongolei'},
    'Monténégro':{'fr':'Monténégro','en':'Montenegro','es':'Montenegro','de':'Montenegro'},
    'Mozambique':{'fr':'Mozambique','en':'Mozambique','es':'Mozambique','de':'Mosambik'},
    'Myanmar':{'fr':'Myanmar','en':'Myanmar','es':'Myanmar','de':'Myanmar'},
    'Namibie':{'fr':'Namibie','en':'Namibia','es':'Namibia','de':'Namibia'},
    'Nicaragua':{'fr':'Nicaragua','en':'Nicaragua','es':'Nicaragua','de':'Nicaragua'},
    'Nigeria':{'fr':'Nigeria','en':'Nigeria','es':'Nigeria','de':'Nigeria'},
    'Norvège':{'fr':'Norvège','en':'Norway','es':'Noruega','de':'Norwegen'},
    'Nouvelle-Calédonie':{'fr':'Nouvelle-Calédonie','en':'New Caledonia','es':'Nueva Caledonia','de':'Neukaledonien'},
    'Nouvelle-Zélande':{'fr':'Nouvelle-Zélande','en':'New Zealand','es':'Nueva Zelanda','de':'Neuseeland'},
    'Népal':{'fr':'Népal','en':'Nepal','es':'Nepal','de':'Nepal'},
    'Oman':{'fr':'Oman','en':'Oman','es':'Omán','de':'Oman'},
    'Ouganda':{'fr':'Ouganda','en':'Uganda','es':'Uganda','de':'Uganda'},
    'Ouzbékistan':{'fr':'Ouzbékistan','en':'Uzbekistan','es':'Uzbekistán','de':'Usbekistan'},
    'Panama':{'fr':'Panama','en':'Panama','es':'Panamá','de':'Panama'},
    'Papouasie-Nouvelle-Guinée':{'fr':'Papouasie-Nouvelle-Guinée','en':'Papua New Guinea','es':'Papúa Nueva Guinea','de':'Papua-Neuguinea'},
    'Paraguay':{'fr':'Paraguay','en':'Paraguay','es':'Paraguay','de':'Paraguay'},
    'Pays-Bas':{'fr':'Pays-Bas','en':'Netherlands','es':'Países Bajos','de':'Niederlande'},
    'Pays-Bas caribéens':{'fr':'Pays-Bas caribéens','en':'Caribbean Netherlands','es':'Países Bajos del Caribe','de':'Caribbean Netherlands'},
    'Philippines':{'fr':'Philippines','en':'Philippines','es':'Filipinas','de':'Philippinen'},
    'Pologne':{'fr':'Pologne','en':'Poland','es':'Polonia','de':'Polen'},
    'Polynésie française':{'fr':'Polynésie française','en':'French Polynesia','es':'Polinesia Francesa','de':'Französisch-Polynesien'},
    'Porto Rico':{'fr':'Porto Rico','en':'Puerto Rico','es':'Puerto Rico','de':'Puerto Rico'},
    'Portugal':{'fr':'Portugal','en':'Portugal','es':'Portugal','de':'Portugal'},
    'Pérou':{'fr':'Pérou','en':'Peru','es':'Perú','de':'Peru'},
    'Qatar':{'fr':'Qatar','en':'Qatar','es':'Catar','de':'Katar'},
    'Roumanie':{'fr':'Roumanie','en':'Romania','es':'Rumanía','de':'Rumänien'},
    'Royaume-Uni':{'fr':'Royaume-Uni','en':'United Kingdom','es':'Reino Unido','de':'Vereinigtes Königreich'},
    'Rwanda':{'fr':'Rwanda','en':'Rwanda','es':'Ruanda','de':'Ruanda'},
    'République Dominicaine':{'fr':'République Dominicaine','en':'Dominican Republic','es':'República Dominicana','de':'Dominikanische Republik'},
    'Saint-Vincent-et-les-Grenadines':{'fr':'Saint-Vincent-et-les-Grenadines','en':'St. Vincent & Grenadines','es':'San Vicente y las Granadinas','de':'Saint Vincent and the Grenadines'},
    'Sainte-Lucie':{'fr':'Sainte-Lucie','en':'Saint Lucia','es':'Santa Lucía','de':'St. Lucia'},
    'Samoa':{'fr':'Samoa','en':'Samoa','es':'Samoa','de':'Samoa'},
    'Serbie':{'fr':'Serbie','en':'Serbia','es':'Serbia','de':'Serbien'},
    'Seychelles':{'fr':'Seychelles','en':'Seychelles','es':'Seychelles','de':'Seychellen'},
    'Sierra Leone':{'fr':'Sierra Leone','en':'Sierra Leone','es':'Sierra Leona','de':'Sierra Leone'},
    'Singapour':{'fr':'Singapour','en':'Singapore','es':'Singapur','de':'Singapur'},
    'Slovaquie':{'fr':'Slovaquie','en':'Slovakia','es':'Eslovaquia','de':'Slowakei'},
    'Slovénie':{'fr':'Slovénie','en':'Slovenia','es':'Eslovenia','de':'Slowenien'},
    'Sri Lanka':{'fr':'Sri Lanka','en':'Sri Lanka','es':'Sri Lanka','de':'Sri Lanka'},
    'Suisse':{'fr':'Suisse','en':'Switzerland','es':'Suiza','de':'Schweiz'},
    'Suède':{'fr':'Suède','en':'Sweden','es':'Suecia','de':'Schweden'},
    'Sénégal':{'fr':'Sénégal','en':'Senegal','es':'Senegal','de':'Senegal'},
    'Tanzanie':{'fr':'Tanzanie','en':'Tanzania','es':'Tanzania','de':'Tansania'},
    'Taïwan':{'fr':'Taïwan','en':'Taiwan','es':'Taiwán','de':'Taiwan'},
    'Tchéquie':{'fr':'Tchéquie','en':'Czech Republic','es':'República Checa','de':'Tschechische Republik'},
    'Thaïlande':{'fr':'Thaïlande','en':'Thailand','es':'Tailandia','de':'Thailand'},
    'Togo':{'fr':'Togo','en':'Togo','es':'Togo','de':'Togo'},
    'Tonga':{'fr':'Tonga','en':'Tonga','es':'Tonga','de':'Tonga'},
    'Trinité-et-Tobago':{'fr':'Trinité-et-Tobago','en':'Trinidad & Tobago','es':'Trinidad y Tobago','de':'Trinidad und Tobago'},
    'Tunisie':{'fr':'Tunisie','en':'Tunisia','es':'Túnez','de':'Tunesien'},
    'Turks-et-Caïcos':{'fr':'Turks-et-Caïcos','en':'Turks & Caicos','es':'Islas Turcas y Caicos','de':'Turks and Caicos'},
    'Turquie':{'fr':'Turquie','en':'Turkey','es':'Turquía','de':'Türkei'},
    'Ukraine':{'fr':'Ukraine','en':'Ukraine','es':'Ucrania','de':'Ukraine'},
    'Uruguay':{'fr':'Uruguay','en':'Uruguay','es':'Uruguay','de':'Uruguay'},
    'Vanuatu':{'fr':'Vanuatu','en':'Vanuatu','es':'Vanuatu','de':'Vanuatu'},
    'Viêt Nam':{'fr':'Viêt Nam','en':'Vietnam','es':'Vietnam','de':'Vietnam'},
    'Yémen':{'fr':'Yémen','en':'Yemen','es':'Yemen','de':'Jemen'},
    'Zambie':{'fr':'Zambie','en':'Zambia','es':'Zambia','de':'Sambia'},
    'Zimbabwe':{'fr':'Zimbabwe','en':'Zimbabwe','es':'Zimbabue','de':'Simbabwe'},
    'Écosse':{'fr':'Écosse','en':'Scotland','es':'Escocia','de':'Scotland'},
    'Égypte':{'fr':'Égypte','en':'Egypt','es':'Egipto','de':'Ägypten'},
    'Émirats Arabes Unis':{'fr':'Émirats Arabes Unis','en':'United Arab Emirates','es':'Emiratos Árabes Unidos','de':'Vereinigte Arabische Emirate'},
    'Émirats arabes unis':{'fr':'Émirats Arabes Unis','en':'United Arab Emirates','es':'Emiratos Árabes Unidos','de':'UAE'},
    'Équateur':{'fr':'Équateur','en':'Ecuador','es':'Ecuador','de':'Ecuador'},
    'États-Unis':{'fr':'États-Unis','en':'United States','es':'Estados Unidos','de':'Vereinigte Staaten'},
    'Éthiopie':{'fr':'Éthiopie','en':'Ethiopia','es':'Etiopía','de':'Äthiopien'},
    'Gabon':{'fr':'Gabon','en':'Gabon','es':'Gabón','de':'Gabon'},
    'Gambie':{'fr':'Gambie','en':'Gambia','es':'Gambia','de':'Gambia'},
    'Gibraltar':{'fr':'Gibraltar','en':'Gibraltar','es':'Gibraltar','de':'Gibraltar'},
    'Îles Caïmans':{'fr':'Îles Caïmans','en':'Cayman Islands','es':'Islas Caimán','de':'Kaimaninseln'},
    'Îles Cook':{'fr':'Îles Cook','en':'Cook Islands','es':'Islas Cook','de':'Cook Islands'},
    'Îles Vierges américaines':{'fr':'Îles Vierges américaines','en':'U.S. Virgin Islands','es':'Islas Vírgenes de EE.UU.','de':'US Virgin Islands'},
    'Malawi':{'fr':'Malawi','en':'Malawi','es':'Malaui','de':'Malawi'},
    'Palaos':{'fr':'Palaos','en':'Palau','es':'Palaos','de':'Palau'},
    'Tadjikistan':{'fr':'Tadjikistan','en':'Tajikistan','es':'Tayikistán','de':'Tajikistan'},
    'Vietnam':{'fr':'Vietnam','en':'Vietnam','es':'Vietnam','de':'Vietnam'},
}

MIN_COUNTRY_SIZE = 3  # own accordion if >= 3 destinations
OTHERS_LABEL = {'fr':'Autres pays','en':'Other countries','es':'Otros países'}
# Megas that show a flat destination grid (no country sub-accordions)
FLAT_MEGAS = {'caraïbes', 'ameriques-n', 'ameriques-s', 'oceanie', 'af-nord', 'af-sub', 'atl'}

# 5 mega-regions in order (France merged into Europe)
MEGAS = [
    ('europe',     1, {'fr': '🌐 Europe',                         'en': '🌐 Europe',                    'es': '🌐 Europa',                'de': '🌐 Europa'}),
    ('af-nord',    2, {'fr': '🌐 Afrique du Nord',               'en': '🌐 North Africa',              'es': '🌐 África del Norte',        'de': '🌐 Nordafrika'}),
    ('atl',        3, {'fr': '🌐 Îles Atlantiques',             'en': '🌐 Atlantic Islands',          'es': '🌐 Islas Atlánticas',        'de': '🌐 Atlantische Inseln'}),
    ('af-sub',     4, {'fr': '🌐 Afrique & Océan Indien',         'en': '🌐 Africa & Indian Ocean',     'es': '🌐 África & Océano Índico',  'de': '🌐 Afrika & Indischer Ozean'}),
    ('me',         5, {'fr': '🌐 Moyen-Orient & Asie Centrale',   'en': '🌐 Middle East & Central Asia','es': '🌐 Oriente Medio & Asia Central','de': '🌐 Naher Osten & Zentralasien'}),
    ('asie',       6, {'fr': '🌐 Asie',                           'en': '🌐 Asia',                      'es': '🌐 Asia',                   'de': '🌐 Asien'}),
    ('ameriques-n',7, {'fr': '🌐 Amér. du Nord',                  'en': '🌐 N. America',                'es': '🌐 Norteamérica',           'de': '🌐 Nordamerika'}),
    ('caraïbes',   8, {'fr': '🌐 Caraïbes',                       'en': '🌐 Caribbean',                 'es': '🌐 Caribe',                 'de': '🌐 Karibik'}),
    ('ameriques-s',9, {'fr': '🌐 Amér. du Sud',                   'en': '🌐 S. America',                'es': '🌐 Sudamérica',             'de': '🌐 Südamerika'}),
    ('oceanie',   10, {'fr': '🌐 Océanie',                        'en': '🌐 Oceania',                   'es': '🌐 Oceanía',                'de': '🌐 Ozeanien'}),
]

# Sub-region name translations per language
SUB_NAMES = {
    'Europe du Sud & Méditerranée': {'fr': 'Europe du Sud & Méditerranée', 'en': 'Southern Europe & Mediterranean', 'es': 'Europa del Sur y Mediterráneo', 'de': 'Südeuropa & Mittelmeer'},
    'Europe du Nord & Centrale':    {'fr': 'Europe du Nord & Centrale',    'en': 'Northern & Central Europe',       'es': 'Europa del Norte y Central',   'de': 'Nord- & Mitteleuropa'},
    'Scandinavie & Baltique':       {'fr': 'Scandinavie & Baltique',       'en': 'Scandinavia & Baltics',           'es': 'Escandinavia y Báltico',       'de': 'Skandinavien & Baltikum'},
    'Caucase & Asie Centrale':      {'fr': 'Caucase & Asie Centrale',      'en': 'Caucasus & Central Asia',         'es': 'Cáucaso y Asia Central',       'de': 'Kaukasus & Zentralasien'},
    'Afrique du Nord':              {'fr': 'Afrique du Nord',              'en': 'North Africa',                    'es': 'África del Norte',             'de': 'Nordafrika'},
    "Afrique de l'Ouest":           {'fr': "Afrique de l'Ouest",           'en': 'West Africa',                     'es': 'África Occidental',            'de': 'Westafrika'},
    "Afrique de l'Est":             {'fr': "Afrique de l'Est",             'en': 'East Africa',                     'es': 'África Oriental',              'de': 'Ostafrika'},
    'Afrique australe':             {'fr': 'Afrique australe',             'en': 'Southern Africa',                 'es': 'África Austral',               'de': 'Südliches Afrika'},
    'Océan Indien':                 {'fr': 'Océan Indien',                 'en': 'Indian Ocean',                    'es': 'Océano Índico',                'de': 'Indischer Ozean'},
    'Moyen-Orient':                 {'fr': 'Moyen-Orient',                 'en': 'Middle East',                     'es': 'Oriente Medio',                'de': 'Naher Osten'},
    'Macaronésie':                  {'fr': 'Macaronésie',                  'en': 'Macaronesia',                     'es': 'Macaronesia',                  'de': 'Makaronesien'},
    'Asie du Sud-Est':              {'fr': 'Asie du Sud-Est',              'en': 'Southeast Asia',                  'es': 'Asia del Sudeste',             'de': 'Südostasien'},
    "Asie de l'Est":                {'fr': "Asie de l'Est",                'en': 'East Asia',                       'es': 'Asia Oriental',                'de': 'Ostasien'},
    'Asie du Sud':                  {'fr': 'Asie du Sud',                  'en': 'South Asia',                      'es': 'Asia del Sur',                 'de': 'Südasien'},
    'Amérique du Nord':             {'fr': 'Amérique du Nord',             'en': 'North America',                   'es': 'América del Norte',            'de': 'Nordamerika'},
    'Caraïbes':                     {'fr': 'Caraïbes',                     'en': 'Caribbean',                       'es': 'Caribe',                       'de': 'Karibik'},
    'Mexique & Amérique Centrale':  {'fr': 'Mexique & Amérique Centrale',  'en': 'Mexico & Central America',        'es': 'México y América Central',     'de': 'Mexiko & Mittelamerika'},
    'Amérique du Sud':              {'fr': 'Amérique du Sud',              'en': 'South America',                   'es': 'América del Sur',              'de': 'Südamerika'},
    'Australie & Nouvelle-Zélande': {'fr': 'Australie & Nouvelle-Zélande','en': 'Australia & New Zealand',         'es': 'Australia y Nueva Zelanda',    'de': 'Australien & Neuseeland'},
    'Îles Atlantiques':        {'fr': 'Îles Atlantiques',         'en': 'Atlantic Islands',                'es': 'Islas Atlánticas',             'de': 'Atlantische Inseln'},
    'Pacifique & Outre-mer':        {'fr': 'Pacifique',                    'en': 'Pacific',                         'es': 'Pacífico',                     'de': 'Pazifik'},
}

# Sub-region sort order within each mega
SUB_ORDER = {
    'Europe du Sud & Méditerranée': 1,
    'Europe du Nord & Centrale': 2,
    'Scandinavie & Baltique': 3,
    'Caucase & Asie Centrale': 4,
    'Afrique du Nord': 1,
    "Afrique de l'Ouest": 2,
    "Afrique de l'Est": 3,
    'Afrique australe': 4,
    'Océan Indien': 5,
    'Moyen-Orient': 6,
    'Macaronésie': 7,
    'Asie du Sud-Est': 1,
    "Asie de l'Est": 2,
    'Asie du Sud': 3,
    'Amérique du Nord': 1,
    'Caraïbes': 2,
    'Mexique & Amérique Centrale': 3,
    'Amérique du Sud': 4,
    'Australie & Nouvelle-Zélande': 1,
    'Îles Atlantiques':        {'fr': 'Îles Atlantiques',         'en': 'Atlantic Islands',                'es': 'Islas Atlánticas',             'de': 'Atlantische Inseln'},
    'Pacifique & Outre-mer': 2,
}

# ── CSS ──
CSS = """
/* ── Destination Hub ── */
.dh-search{position:relative;margin-bottom:24px}
.dh-search input{width:100%;padding:14px 16px 14px 44px;border:1.5px solid rgba(255,255,255,.12);border-radius:12px;font-size:15px;font-family:inherit;background:#131920;color:rgba(255,255,255,.85);outline:none;transition:border-color .2s;box-sizing:border-box}
.dh-search input:focus{border-color:#e8940a}
.dh-search input::placeholder{color:#9ca3af}
.dh-search-icon{position:absolute;left:14px;top:50%;transform:translateY(-50%);color:#9ca3af;pointer-events:none;font-size:18px}
.dh-search-clear{position:absolute;right:12px;top:50%;transform:translateY(-50%);background:none;border:none;font-size:18px;color:#9ca3af;cursor:pointer;padding:4px;display:none}
.dh-search-clear.show{display:block}
.dh-count{font-size:12px;color:#7a8fa8;margin:-16px 0 20px 4px;display:none}
.dh-count.show{display:block}

.dh-acc{border:1.5px solid rgba(255,255,255,.08);border-radius:14px;margin-bottom:10px;overflow:hidden;background:#131920}
.dh-acc-head{width:100%;display:flex;align-items:center;justify-content:space-between;padding:16px 18px;background:#131920;border:none;cursor:pointer;font-family:inherit;text-align:left;gap:12px;color:rgba(255,255,255,.85)}
.dh-acc-head:hover{background:#faf8f3}
.dh-acc-label{font-size:16px;font-weight:700;color:rgba(255,255,255,.9)}
.dh-acc-meta{display:flex;align-items:center;gap:10px;flex-shrink:0}
.dh-acc-count{font-size:12px;color:#7a8fa8;background:rgba(255,255,255,.1);border-radius:20px;padding:2px 10px;font-weight:600;color:rgba(255,255,255,.6)}
.dh-acc-chev{font-size:14px;color:#9ca3af;transition:transform .25s}
.dh-acc.open>.dh-acc-head .dh-acc-chev{transform:rotate(180deg)}
.dh-acc-body{display:none;padding:0 18px 14px}
.dh-acc.open>.dh-acc-body{display:block}

.dh-sub{border:1px solid rgba(255,255,255,.06);border-radius:10px;margin-bottom:8px;overflow:hidden;background:#0d1117}
.dh-sub-head{width:100%;display:flex;align-items:center;justify-content:space-between;padding:12px 14px;background:#0d1117;border:none;cursor:pointer;font-family:inherit;text-align:left;gap:10px;color:rgba(255,255,255,.7)}
.dh-sub-head:hover{background:#f5f0e5}
.dh-sub-label{font-size:13px;font-weight:700;color:#4a5568}
.dh-sub-count{font-size:11px;color:#9ca3af;font-weight:600}
.dh-sub-chev{font-size:12px;color:#bbb;transition:transform .25s}
.dh-sub.open>.dh-sub-head .dh-sub-chev{transform:rotate(180deg)}
.dh-sub-body{display:none;padding:6px 14px 12px}
.dh-sub.open>.dh-sub-body{display:block}

.dh-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(155px,1fr));gap:8px}
.dh-card{background:#1a2230;border-radius:10px;padding:10px 12px;text-decoration:none;border:1px solid rgba(255,255,255,.08);display:flex;align-items:center;gap:9px;transition:border-color .15s,box-shadow .15s}
.dh-card:hover{border-color:#e8940a;box-shadow:0 2px 8px rgba(232,148,10,.12)}
.dh-card img{flex-shrink:0}
.dh-card-name{font-size:12px;font-weight:700;color:rgba(255,255,255,.85);display:block;line-height:1.3}
.dh-card-sub{font-size:10px;color:#7a8fa8}
.dh-card.dh-hidden{display:none}
.dh-no-results{display:none;text-align:center;padding:32px 16px;color:#7a8fa8;font-size:14px}
.dh-no-results.show{display:block}

@media(max-width:640px){
 .dh-grid{grid-template-columns:repeat(2,1fr);gap:6px}
 .dh-card{padding:9px 10px}
 .dh-acc-head{padding:14px 14px}
 .dh-acc-label{font-size:15px}
 .dh-sub-head{padding:10px 12px}
 .dh-sub-body{padding:6px 6px 10px}
 .dh-acc-body{padding:10px 6px 14px}
}
"""

# ── JS ──
JS_TEMPLATE = """
(function(){
 var inp=document.getElementById('dh-input'),
     clear=document.getElementById('dh-clear'),
     count=document.getElementById('dh-count'),
     cards=document.querySelectorAll('.dh-card'),
     accs=document.querySelectorAll('.dh-acc'),
     subs=document.querySelectorAll('.dh-sub'),
     noRes=document.getElementById('dh-no-results');

 function norm(s){return s.normalize('NFD').replace(/[\\u0300-\\u036f]/g,'').toLowerCase()}
 var searching=false;

 function doSearch(){
  var q=norm(inp.value.trim());
  clear.className='dh-search-clear'+(q?' show':'');
  if(!q){
   searching=false;
   cards.forEach(function(c){c.classList.remove('dh-hidden')});
   accs.forEach(function(a){a.classList.remove('open','dh-sm');a.style.display=''});
   subs.forEach(function(s){s.classList.remove('open','dh-sm');s.style.display=''});
   count.className='dh-count';noRes.className='dh-no-results';
   return;
  }
  searching=true;
  var n=0;
  cards.forEach(function(c){
   var t=norm(c.getAttribute('data-name')||'');
   var p=norm(c.getAttribute('data-country')||'');
   var al=norm(c.getAttribute('data-aliases')||'');
   if(t.indexOf(q)>-1||p.indexOf(q)>-1||al.indexOf(q)>-1){c.classList.remove('dh-hidden');n++}
   else{c.classList.add('dh-hidden')}
  });
  subs.forEach(function(s){
   var vis=s.querySelectorAll('.dh-card:not(.dh-hidden)');
   if(vis.length){s.classList.add('open','dh-sm');s.style.display=''}
   else{s.style.display='none'}
  });
  accs.forEach(function(a){
   var vis=a.querySelectorAll('.dh-card:not(.dh-hidden)');
   if(vis.length){a.classList.add('open','dh-sm');a.style.display=''}
   else{a.style.display='none'}
  });
  count.textContent=n+' '+(n>1?'COUNT_PLURAL':'COUNT_SINGULAR');
  count.className='dh-count show';
  noRes.className='dh-no-results'+(n===0?' show':'');
 }

 inp.addEventListener('input',doSearch);
 clear.addEventListener('click',function(){inp.value='';doSearch();inp.focus()});

 function toggleAcc(el,cls){
  el.addEventListener('click',function(){
   if(searching)return;
   var acc=el.parentElement;
   var wasOpen=acc.classList.contains('open');
   acc.classList.toggle('open');
   if(!wasOpen)setTimeout(function(){acc.scrollIntoView({behavior:'smooth',block:'start'})},80);
  });
 }
 document.querySelectorAll('.dh-acc-head').forEach(function(h){toggleAcc(h)});
 document.querySelectorAll('.dh-sub-head').forEach(function(h){toggleAcc(h)});
})();
"""


def make_card(slug, name, bare, flag, country, asset_prefix, page_prefix, loc, csv_aliases=''):
    href = f'{page_prefix}{loc["gen"]["annual_href_tpl"].format(slug=slug)}'
    sub = loc['hub']['card_sub']
    parts = []
    if bare.lower() != name.lower():
        parts.append(bare)
    if csv_aliases:
        parts += [a.strip() for a in csv_aliases.split() if a.strip()]
    aliases = ' '.join(dict.fromkeys(parts))  # déduplique en préservant l'ordre
    alias_attr = f' data-aliases="{html_mod.escape(aliases)}"' if aliases else ''
    return (
        f'<a href="{href}" target="_top" class="dh-card" '
        f'data-name="{html_mod.escape(name)}" data-country="{html_mod.escape(country)}"{alias_attr}>'
        f'<img src="{asset_prefix}flags/{flag}.png" width="20" height="15" alt="{flag.upper()}" style="border-radius:2px">'
        f'<span><span class="dh-card-name">{html_mod.escape(name)}</span>'
        f'<span class="dh-card-sub">{sub}</span></span></a>')


def build_hub(destinations, loc):
    asset_prefix = loc['gen']['asset_prefix']
    page_prefix = ''  # pages are always in same dir as hub
    lang = loc['meta']['html_lang']
    # en-US uses same MEGAS/SUB_NAMES labels as en
    lang_key = 'en' if lang == 'en-US' else lang
    is_fr = (lang == 'fr')
    slug_key = 'slug_fr' if is_fr else ('slug_es' if lang == 'es' else ('slug_de' if lang == 'de' else 'slug_en'))
    name_key = 'nom_fr' if is_fr else ('nom_es' if lang == 'es' else ('nom_de' if lang == 'de' else 'nom_en'))

    # Group: mega → sub → [dests]
    # Build pays→flag mapping from destinations
    pays_flag = {d['pays']: d.get('flag', '') for d in destinations}
    megas = {}
    for d in destinations:
        slug = d['slug_fr']
        pays = d['pays']
        # Slug override takes priority (DOM-TOM, Canaries, Bermuda…)
        if slug in SLUG_OVERRIDE:
            mega_id, sub_name = SLUG_OVERRIDE[slug]
        elif pays not in MAPPING:
            print(f"  ⚠️  Pays sans mapping: {pays} ({d['nom_fr']})")
            continue
        else:
            mega_id, sub_name = MAPPING[pays]
        country_key = pays
        if mega_id not in megas:
            megas[mega_id] = {}
        if country_key not in megas[mega_id]:
            megas[mega_id][country_key] = []
        megas[mega_id][country_key].append(d)

    L = []

    # Search bar
    ph = loc['hub']['search_placeholder']
    L.append(f'<div class="dh-search"><span class="dh-search-icon">🔍</span>')
    L.append(f'<input type="text" id="dh-input" placeholder="{ph}" autocomplete="off">')
    L.append(f'<button id="dh-clear" class="dh-search-clear" aria-label="Clear">✕</button></div>')
    L.append(f'<div id="dh-count" class="dh-count"></div>')

    # 6 mega-accordions
    for mega_id, sort, labels in MEGAS:
        if mega_id not in megas:
            continue
        label = labels[lang_key]
        subs_data = megas[mega_id]
        cnt = sum(len(v) for v in subs_data.values())
        has_subs = mega_id not in FLAT_MEGAS

        L.append(f'<div class="dh-acc">')
        L.append(f'<button class="dh-acc-head" aria-expanded="false">')
        L.append(f'<span class="dh-acc-label">{label}</span>')
        L.append(f'<span class="dh-acc-meta"><span class="dh-acc-count">{cnt}</span>')
        L.append(f'<span class="dh-acc-chev">▾</span></span></button>')
        L.append(f'<div class="dh-acc-body">')

        big = {k: v for k, v in subs_data.items() if len(v) >= MIN_COUNTRY_SIZE}
        small = {k: v for k, v in subs_data.items() if len(v) < MIN_COUNTRY_SIZE}
        sorted_subs = sorted(big.items(), key=lambda x: (-len(x[1]), x[0]))
        if small:
            others_dests = [d for v in small.values() for d in v]
            sorted_subs = sorted_subs + [('__others__', others_dests)]

        if has_subs:
            for sub_name, dests in sorted_subs:
                sub_cnt = len(dests)
                L.append(f'<div class="dh-sub">')
                L.append(f'<button class="dh-sub-head">')
                if sub_name == '__others__':
                    sub_label = OTHERS_LABEL.get(lang_key, 'Other countries')
                    flag_img = ''
                else:
                    trans = COUNTRY_NAMES_TRANS.get(sub_name, {})
                    sub_label = trans.get(lang_key, sub_name)
                    flag_code = pays_flag.get(sub_name, '')
                    flag_img = f'<img src="{asset_prefix}flags/{flag_code}.png" width="20" height="15" alt="{flag_code}" class="flag-icon" style="margin-right:6px;vertical-align:middle;border-radius:2px"> ' if flag_code else ''
                L.append(f'<span class="dh-sub-label">{flag_img}{html_mod.escape(sub_label)}</span>')
                L.append(f'<span class="dh-acc-meta"><span class="dh-sub-count">{sub_cnt}</span>')
                L.append(f'<span class="dh-sub-chev">▾</span></span></button>')
                L.append(f'<div class="dh-sub-body">')
                # Split mountain vs other destinations
                mountain_dests = [d for d in dests if d.get('mountain','').strip() == 'True']
                city_dests     = [d for d in dests if d.get('mountain','').strip() != 'True']
                lbl_mountain   = loc.get('hub', {}).get('mountain_group', '\u26f7\ufe0f Mountain resorts')
                lbl_city       = loc.get('hub', {}).get('city_group', '\U0001f306 Cities & destinations')

                def render_group(group, label, show_label):
                    html = []
                    if show_label:
                        html.append(f'<div class="dh-group-label">{label}</div>')
                    html.append('<div class="dh-grid">')
                    for d in sorted(group, key=lambda x: x['nom_bare']):
                        s = d[slug_key]
                        n = d[name_key]
                        if is_fr:
                            cc = d['pays']
                        elif lang == 'es':
                            cc = d.get('country_es') or d['pays']
                        elif lang == 'de':
                            cc = d.get('country_de') or d['pays']
                        else:
                            cc = d.get('country_en') or d['pays']
                        html.append(make_card(s, n, d['nom_bare'], d['flag'], cc, asset_prefix, page_prefix, loc, d.get('aliases','')))
                    html.append('</div>')
                    return html

                use_groups = len(mountain_dests) >= 2 and len(city_dests) >= 1
                if use_groups:
                    if city_dests:
                        L.extend(render_group(city_dests, lbl_city, True))
                    L.extend(render_group(mountain_dests, lbl_mountain, True))
                else:
                    L.extend(render_group(dests, '', False))
                L.append(f'</div></div>')
        else:
            # Flat grid — no country sub-accordions
            all_dests = [d for v in subs_data.values() for d in v]
            mountain_dests = [d for d in all_dests if d.get('mountain','').strip() == 'True']
            city_dests     = [d for d in all_dests if d.get('mountain','').strip() != 'True']
            lbl_mountain   = loc.get('hub', {}).get('mountain_group', '⛷️ Mountain resorts')
            lbl_city       = loc.get('hub', {}).get('city_group', '🌆 Cities & destinations')
            def make_card_loc(d):
                if is_fr:
                    cc = d['pays']
                elif lang == 'es':
                    cc = d.get('country_es') or d['pays']
                elif lang == 'de':
                    cc = d.get('country_de') or d['pays']
                else:
                    cc = d.get('country_en') or d['pays']
                return make_card(d[slug_key], d[name_key], d['nom_bare'], d['flag'], cc, asset_prefix, page_prefix, loc, d.get('aliases',''))
            use_groups = len(mountain_dests) >= 2 and len(city_dests) >= 1
            if use_groups:
                if city_dests:
                    L.append(f'<div class="dh-group-label">{lbl_city}</div>')
                    L.append('<div class="dh-grid">')
                    for d in sorted(city_dests, key=lambda x: x['nom_bare']): L.append(make_card_loc(d))
                    L.append('</div>')
                L.append(f'<div class="dh-group-label">{lbl_mountain}</div>')
                L.append('<div class="dh-grid">')
                for d in sorted(mountain_dests, key=lambda x: x['nom_bare']): L.append(make_card_loc(d))
                L.append('</div>')
            else:
                L.append('<div class="dh-grid">')
                for d in sorted(all_dests, key=lambda x: x['nom_bare']): L.append(make_card_loc(d))
                L.append('</div>')

        L.append(f'</div></div>')

    no_msg = loc['hub']['no_results']
    L.append(f'<div id="dh-no-results" class="dh-no-results">{no_msg}</div>')
    return '\n'.join(L)



import datetime as _dt

def _top_now_cards(destinations, loc, lang, n=13):
    """Génère les cards V4 'Partir maintenant' pour le mois courant."""
    import csv as _csv, statistics as _stat
    MOIS = _dt.date.today().month
    MOIS_NAMES = {
        'fr': {1:'Janvier',2:'Février',3:'Mars',4:'Avril',5:'Mai',6:'Juin',
               7:'Juillet',8:'Août',9:'Septembre',10:'Octobre',11:'Novembre',12:'Décembre'},
        'en': {1:'January',2:'February',3:'March',4:'April',5:'May',6:'June',
               7:'July',8:'August',9:'September',10:'October',11:'November',12:'December'},
        'es': {1:'Enero',2:'Febrero',3:'Marzo',4:'Abril',5:'Mayo',6:'Junio',
               7:'Julio',8:'Agosto',9:'Septiembre',10:'Octubre',11:'Noviembre',12:'Diciembre'},
        'de': {1:'Januar',2:'Februar',3:'März',4:'April',5:'Mai',6:'Juni',
               7:'Juli',8:'August',9:'September',10:'Oktober',11:'November',12:'Dezember'},
    }
    lang_key = 'en' if lang in ('en-us','en-US') else lang
    mois_name = MOIS_NAMES.get(lang_key, MOIS_NAMES['fr']).get(MOIS, '')

    # Titres section par langue
    TITLES = {
        'fr': f'Partir en <em>{mois_name}</em>',
        'en': f'Travel in <em>{mois_name}</em>',
        'es': f'Viajar en <em>{mois_name}</em>',
        'de': f'Reisen im <em>{mois_name}</em>',
    }
    MORE = {'fr':'Tout voir →','en':'View all →','es':'Ver todo →','de':'Alle sehen →'}
    sec_title = TITLES.get(lang_key, TITLES['fr'])
    more_lbl = MORE.get(lang_key, MORE['fr'])
    more_href = '' # link to classement été/hiver selon mois

    # Charger climate + photos
    try:
        climate_raw = list(_csv.DictReader(open('data/climate.csv', encoding='utf-8-sig')))
    except FileNotFoundError:
        climate_raw = list(_csv.DictReader(open('../data/climate.csv', encoding='utf-8-sig')))
    climate = {}
    for r in climate_raw:
        s=r['slug']; m=int(r['mois_num'])
        climate.setdefault(s,{})[m]={
            'score':float(r.get('score') or 0),
            'tmax':float(r.get('tmax') or 0),
            'rain_pct':float(r.get('rain_pct') or 0),
        }

    try:
        photos = {r['slug_fr']: r for r in _csv.DictReader(open('data/destination_photos.csv'))}
    except FileNotFoundError:
        photos = {r['slug_fr']: r for r in _csv.DictReader(open('../data/destination_photos.csv'))}

    is_fr = (lang == 'fr')
    lang_k = 'en' if lang in ('en-us','en-US') else lang
    name_key = 'nom_fr' if is_fr else (f'nom_{lang_k}' if lang_k in ('es','de') else 'nom_en')
    slug_key = 'slug_fr' if is_fr else (f'slug_{lang_k}' if lang_k in ('es','de') else 'slug_en')
    href_tpl = loc['gen']['annual_href_tpl']
    asset_prefix = loc['gen']['asset_prefix']

    seen_pays = set()
    results = []
    dest_map = {d['slug_fr']: d for d in destinations}

    for slug, monthly in climate.items():
        if slug not in dest_map or len(monthly) < 12: continue
        d = dest_map[slug]
        if d.get('precision') == 'country': continue
        p = photos.get(slug, {})
        if not p.get('photo_url', '').strip(): continue
        pays = d.get('pays', '')
        if pays in seen_pays: continue
        seen_pays.add(pays)
        score_m = monthly.get(MOIS, {}).get('score', 0)
        tmax = monthly.get(MOIS, {}).get('tmax', 0)
        rain = monthly.get(MOIS, {}).get('rain_pct', 0)
        results.append({
            'slug': slug, 'dest': d, 'score': score_m,
            'tmax': tmax, 'rain': rain,
            'photo': p['photo_url'],
            'credit': p.get('photo_credit_name', ''),
        })

    results.sort(key=lambda x: -x['score'])
    top = results[:n]
    if not top:
        return ''

    # CSS inline pour les cards (compatible avec le thème existant cream)
    css = """<style>
.pm-section{padding:0 20px 32px;max-width:620px;margin:0 auto;font-family:'DM Sans',sans-serif}
.pm-head{display:flex;align-items:baseline;justify-content:space-between;margin-bottom:16px}
.pm-eyebrow{font-size:9px;letter-spacing:3px;text-transform:uppercase;color:#c99438;font-weight:700;margin-bottom:5px}
.pm-title{font-family:'Playfair Display',Georgia,serif;font-size:22px;font-weight:900;letter-spacing:-.4px;color:#09151f}
.pm-title em{font-style:italic;color:#e8b84b}
.pm-more{font-size:11px;color:#7a8fa3;text-decoration:none;white-space:nowrap}
.pm-scroll{display:flex;gap:10px;overflow-x:auto;margin:0 -20px;padding:0 20px 6px;scrollbar-width:none}
.pm-scroll::-webkit-scrollbar{display:none}
.pm-card{flex:0 0 155px;border-radius:16px;overflow:hidden;position:relative;aspect-ratio:9/14;cursor:pointer;text-decoration:none;display:block}
.pm-card img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;transition:transform .5s}
.pm-card:hover img{transform:scale(1.06)}
.pm-card-grad{position:absolute;inset:0;background:linear-gradient(to top,rgba(9,21,31,.95) 0%,rgba(9,21,31,.05) 55%,transparent 75%)}
.pm-score{position:absolute;bottom:12px;right:11px;background:linear-gradient(135deg,#c99438,#e8b84b);border-radius:100px;padding:4px 12px;font-family:'Playfair Display',Georgia,serif;font-size:16px;font-weight:900;color:#09151f;letter-spacing:-.2px;box-shadow:0 4px 12px rgba(201,148,56,.4)}
.pm-body{position:absolute;bottom:0;left:0;right:0;padding:12px 11px 40px}
.pm-name{font-family:'Playfair Display',Georgia,serif;font-size:15px;font-weight:700;color:#fff;line-height:1.1;margin-bottom:2px}
.pm-country{font-size:10px;color:rgba(255,255,255,.55)}
.pm-bar{height:2px;background:rgba(255,255,255,.15);border-radius:2px;margin:6px 0 5px}
.pm-bar-fill{height:100%;border-radius:2px;background:linear-gradient(to right,#c99438,#e8b84b)}
.pm-stats{display:flex;justify-content:space-between;font-size:10px;color:rgba(255,255,255,.5)}
</style>"""

    cards_html = []
    for r in top:
        d = r['dest']
        slug_val = d.get(slug_key, d.get('slug_fr', ''))
        href = f"{asset_prefix}{href_tpl.format(slug=slug_val)}"
        name = d.get(name_key) or d.get('nom_bare', '')
        pays = d.get('pays', '')
        score = r['score']
        tmax = r['tmax']
        rain = r['rain']
        photo = r['photo']
        # Resize Unsplash
        import re as _re
        img_url = _re.sub(r'\?.*$', '', photo.split('?')[0]) + '?w=400&q=75&fm=jpg&fit=crop&crop=entropy'
        bar_pct = min(100, int(score * 10))
        cards_html.append(
            f'<a href="{href}" class="pm-card" target="_top">'
            f'<img src="{img_url}" alt="{name}" loading="lazy" width="155" height="242"/>'
            f'<div class="pm-card-grad"></div>'
            f'<div class="pm-score">{score:.1f}</div>'
            f'<div class="pm-body">'
            f'<div class="pm-name">{name}</div>'
            f'<div class="pm-country">{pays}</div>'
            f'<div class="pm-bar"><div class="pm-bar-fill" style="width:{bar_pct}%"></div></div>'
            f'<div class="pm-stats"><span>☀️ {tmax:.0f}°C</span><span>🌧 {rain:.0f}%</span></div>'
            f'</div></a>'
        )

    return (
        f'{css}'
        f'<div class="pm-section">'
        f'<div class="pm-eyebrow">{mois_name.upper()} {_dt.date.today().year}</div>'
        f'<div class="pm-head">'
        f'<div class="pm-title">{sec_title}</div>'
        f'</div>'
        f'<div class="pm-scroll">{"".join(cards_html)}</div>'
        f'</div>'
    )

def inject(filepath, destinations, loc):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    total = len(destinations)

    # Update counts
    content = re.sub(r'Voir les guides destinations \(\d+ destinations\)',
                     f'Voir les guides destinations ({total} destinations)', content)
    content = re.sub(r'View destination guides \(\d+ destinations\)',
                     f'View destination guides ({total} destinations)', content)
    content = re.sub(r'Tableaux climatiques mensuels · \d+ destinations',
                     f'Tableaux climatiques mensuels · {total} destinations', content)
    content = re.sub(r'Monthly climate tables · \d+ destinations',
                     f'Monthly climate tables · {total} destinations', content)
    # Update guides shortcut counts
    content = re.sub(r'Guides destinations · \d+ fiches',
                     f'Guides destinations · {total} fiches', content)
    content = re.sub(r'Destination guides · \d+ cities',
                     f'Destination guides · {total} cities', content)

    # CSS is now in style.css — no injection needed

    # Build new SILO 1
    hub = build_hub(destinations, loc)
    count_plural = loc['hub']['count_plural']
    count_singular = loc['hub']['count_singular']
    js = JS_TEMPLATE.replace("'COUNT_PLURAL':'COUNT_SINGULAR'",
                              f"'{count_plural}':'{count_singular}'")
    title = loc['hub']['title']

    new_silo = f"""<!-- SILO 1 : MEILLEURE PERIODE - dominant -->
 <div style="margin-bottom:52px">
  <div style="display:flex;align-items:center;gap:14px;margin-bottom:22px">
   <p style="font-size:13px;font-weight:800;letter-spacing:.5px;text-transform:uppercase;color:rgba(255,255,255,.9);margin:0">🌍 {title}</p>
   <div style="flex:1;height:2px;background:linear-gradient(90deg,#e8940a,#e8e0d0)"></div>
  </div>
{hub}
 </div>
<script>
{js}
</script>"""

    # Injecter section "Partir maintenant" avant SILO 1
    pm_marker = '<!-- PARTIR-MAINTENANT -->'
    pm_idx = content.find(pm_marker)
    if pm_idx != -1:
        pm_html = _top_now_cards(destinations, loc, loc['meta']['html_lang'].lower())
        content = content[:pm_idx] + pm_marker + '\n' + pm_html + '\n\n' + content[pm_idx + len(pm_marker) + 1:]

    start_marker = '<!-- SILO 1 : MEILLEURE PERIODE - dominant -->'
    end_marker = '\n <!-- SILO 2'
    start_idx = content.find(start_marker)
    end_idx = content.find(end_marker, start_idx)

    if start_idx == -1 or end_idx == -1:
        print(f"  ⚠️  SILO markers not found in {filepath}")
        return False

    new_content = content[:start_idx] + new_silo + content[end_idx:]

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    return True


# ── Main ──
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib.page_config import load_locale, SUPPORTED_LANGS


LANG_CONFIG = {
    'fr':    {'output': 'index.html',   'i18n': 'js/i18n-fr.min.js?v=12',         'flatpickr_locale': 'fr'},
    'en':    {'output': 'en/app.html',  'i18n': '../js/i18n-en.min.js?v=12',       'flatpickr_locale': None},
    'en-us': {'output': 'us/app.html',  'i18n': '../js/i18n-en-us.min.js?v=12',    'flatpickr_locale': None},
    'es':    {'output': 'es/app.html',  'i18n': '../js/i18n-es.min.js?v=12',       'flatpickr_locale': 'es'},
    'de':    {'output': 'de/app.html',  'i18n': '../js/i18n-de.min.js?v=12',       'flatpickr_locale': 'de'},
}

FLATPICKR_CDN = 'https://cdnjs.cloudflare.com/ajax/libs/flatpickr/4.6.13'

def generate_from_template(lang, loc):
    """Génère le fichier hub depuis templates/app.template.html.
    Toute modification de structure doit se faire dans le template — jamais
    directement dans index.html ou les app.html multilingues.
    """
    cfg = LANG_CONFIG[lang]
    meta = loc.get('meta', {})
    asset_prefix = meta.get('asset_prefix', '../' if lang != 'fr' else '')
    html_lang = meta.get('html_lang', lang)

    template_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates', 'app.template.html')
    if not os.path.exists(template_path):
        print(f'  ⚠️  Template introuvable : {template_path}')
        return False

    content = open(template_path, encoding='utf-8').read()

    # Substitution i18n script
    i18n_script = f'<script defer src="{cfg["i18n"]}"></script>'

    # Substitution flatpickr locale
    fp_loc = cfg['flatpickr_locale']
    flatpickr_locale = (
        f'<script defer src="{FLATPICKR_CDN}/l10n/{fp_loc}.js"></script>\n'
        if fp_loc else ''
    )

    # Charger les blocs de contenu traduits
    blocks_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates', 'blocks')
    lang_key = lang if lang in ('fr', 'en', 'es', 'de') else 'en'
    def load_block(name):
        path = os.path.join(blocks_dir, f'{name}-{lang_key}.html')
        if os.path.exists(path):
            return open(path, encoding='utf-8').read()
        # Fallback FR
        path_fr = os.path.join(blocks_dir, f'{name}-fr.html')
        return open(path_fr, encoding='utf-8').read() if os.path.exists(path_fr) else ''

    # Passe 1 : substituer les blocs (qui peuvent contenir d'autres placeholders)
    blocks = {
        '{{TRUST_BLOCK}}':  load_block('trust'),
        '{{BRAND_BLOCK}}':  load_block('brand'),
        '{{SILO2_BLOCK}}':  load_block('silo2'),
        '{{SILO3_BLOCK}}':  load_block('silo3'),
    }
    for placeholder, value in blocks.items():
        content = content.replace(placeholder, value)

    # Passe 2 : substituer tous les autres placeholders (y compris ASSET_PREFIX dans les blocs)
    replacements = {
        '{{LANG}}':                html_lang,
        '{{ASSET_PREFIX}}':        asset_prefix,
        '{{I18N_SCRIPT}}':         i18n_script,
        '{{FLATPICKR_LOCALE}}':    flatpickr_locale,
        '{{META_DESC}}':           meta.get('meta_desc', ''),
        '{{PAGE_TITLE}}':          meta.get('page_title', 'BestDateWeather'),
        '{{APP_SUB}}':             meta.get('app_sub', ''),
        '{{APP_SUB_SEO}}':         meta.get('app_sub_seo', ''),
        '{{HOME_URL}}':            meta.get('home_url', 'index.html'),
        '{{UI_MODE_DATE}}':        meta.get('ui_mode_date', 'Date'),
        '{{UI_MODE_DATE_SUB}}':    meta.get('ui_mode_date_sub', ''),
        '{{UI_MODE_ANNUAL}}':      meta.get('ui_mode_annual', '12-month view'),
        '{{UI_MODE_ANNUAL_SUB}}':  meta.get('ui_mode_annual_sub', ''),
        '{{UI_CTA}}':              meta.get('ui_cta', 'Check the weather →'),
        '{{UI_DATE_PLACEHOLDER}}': meta.get('ui_date_placeholder', '📅  Choose a date'),
        '{{UI_FOOTER_ERA5}}':      meta.get('ui_footer_era5', 'ERA5 · 10 years'),
        '{{UI_FOOTER_GUIDES}}':    meta.get('ui_footer_guides', '697 destination guides'),
        '{{UI_GUIDES_TAG}}':       meta.get('ui_guides_tag', 'Destination guides'),
        '{{UI_GUIDES_TITLE}}':     meta.get('ui_guides_title', 'When to visit?'),
        '{{UI_GUIDES_SUB}}':       meta.get('ui_guides_sub', ''),
        '{{UI_GUIDES_DESC}}':      meta.get('ui_guides_desc', ''),
        '{{UI_CARD_SUB}}':         meta.get('ui_card_sub', 'Best time to visit'),
        '{{UI_DETAILS_TOGGLE}}':   meta.get('UI_DETAILS_TOGGLE', 'See details — hourly, scenarios, astro'),
        '{{UI_RAIN_PROB}}':        meta.get('UI_RAIN_PROB', '💧 Rain probability'),
        '{{UI_AVG_WIND}}':         meta.get('UI_AVG_WIND', '💨 Avg wind'),
        '{{UI_SKY}}':              meta.get('UI_SKY', '☁️ Sky'),
        '{{UI_MOON_PHASE}}':       meta.get('UI_MOON_PHASE', 'Moon phase'),
        '{{UI_SUNRISE}}':          meta.get('UI_SUNRISE', 'Sunrise'),
        '{{UI_SUNSET}}':           meta.get('UI_SUNSET', 'Sunset'),
        '{{UI_HOURLY}}':           meta.get('UI_HOURLY', 'Hourly forecast'),
        '{{UI_SCENARIOS}}':        meta.get('UI_SCENARIOS', 'Extreme scenarios'),
        '{{UI_HIST_TEMPS}}':       meta.get('UI_HIST_TEMPS', 'Historical temperatures'),
        '{{UI_SC_PESS_DEFAULT}}':  meta.get('UI_SC_PESS_DEFAULT', 'Cool · frequent rain'),
        '{{UI_UC_LABEL}}':          meta.get('UI_UC_LABEL', 'Refine score for:'),
        '{{UI_UC_GENERAL}}':        meta.get('UI_UC_GENERAL', '🌤️ Just the weather'),
        '{{UI_UC_BEACH}}':          meta.get('UI_UC_BEACH', '🏖️ Beach'),
        '{{UI_UC_SKI}}':            meta.get('UI_UC_SKI', '⛷️ Ski'),
        '{{UI_SC_PESS_LABEL}}':    meta.get('UI_SC_PESS_LABEL', 'Low scenario'),
        '{{UI_SC_OPT_LABEL}}':     meta.get('UI_SC_OPT_LABEL', 'High scenario'),
        '{{UI_SC_PESS_TTL}}':      meta.get('UI_SC_PESS_TTL', 'Difficult day'),
        '{{UI_SC_OPT_TTL}}':       meta.get('UI_SC_OPT_TTL', 'Ideal day'),
        '{{UI_SC_OPT_DEFAULT}}':   meta.get('UI_SC_OPT_DEFAULT', 'Hot · little rain'),
        '{{UI_HINT_SCENARIOS}}':   meta.get('UI_HINT_SCENARIOS', 'Statistical envelopes P10–P90'),
        '{{UI_HINT_HOURLY}}':      meta.get('UI_HINT_HOURLY', 'Temperatures & weather'),
        '{{UI_HINT_HIST}}':        meta.get('UI_HINT_HIST', '10-year trend'),
        '{{UI_ANN_BTN}}':          meta.get('UI_ANN_BTN', 'See the year'),
        '{{UI_ANN_SUBTITLE}}':     meta.get('UI_ANN_SUBTITLE', 'Monthly climate profile · 10-year average'),
        # Hero section i18n
        '{{HERO_KICKER}}':         meta.get('HERO_KICKER', 'Weather for your projects'),
        '{{HERO_H1}}':             meta.get('HERO_H1', 'What weather <em>for your trip?</em>'),
        '{{HERO_SUB}}':            meta.get('HERO_SUB', 'Climate scores /10 · 697 destinations · up to 1 year ahead · 10 years of ERA5 data'),
        '{{USP_HORIZON}}':         meta.get('USP_HORIZON', '1 year ahead'),
        # Dynamic sections — calculées à la génération
        '{{TOP_MONTHLY_SECTION}}': build_top_monthly(lang, loc),
        '{{RANKINGS_SECTION}}':    build_rankings_section(lang, loc),
        '{{TRUST_BAR}}':           '',
    }

    for placeholder, value in replacements.items():
        content = content.replace(placeholder, value)

    # Vérifier qu'il ne reste pas de placeholders non substitués
    import re as _re
    remaining = _re.findall(r'\{\{[A-Z_]+\}\}', content)
    if remaining:
        print(f'  ⚠️  Placeholders non substitués : {set(remaining)}')

    output = cfg['output']
    os.makedirs(os.path.dirname(output) if os.path.dirname(output) else '.', exist_ok=True)
    open(output, 'w', encoding='utf-8').write(content)
    return True



# ══════════════════════════════════════════
# HOMEPAGE SECTIONS — génération statique
# ══════════════════════════════════════════

import csv as _csv
import datetime as _dt

def _hero_gradient_home(tmax, tropical, rain_pct, idx=0):
    """Gradient contextuel selon profil climatique + variante visuelle."""
    hot_variants = [
        'linear-gradient(135deg,#c2410c 0%,#ea580c 30%,#f59e0b 65%,#fbbf24 100%)',
        'linear-gradient(135deg,#7c2d12 0%,#c2410c 35%,#f97316 70%,#fb923c 100%)',
        'linear-gradient(135deg,#854d0e 0%,#d97706 40%,#fcd34d 80%,#fef3c7 100%)',
        'linear-gradient(135deg,#991b1b 0%,#dc2626 35%,#f97316 70%,#fbbf24 100%)',
        'linear-gradient(135deg,#78350f 0%,#b45309 40%,#f59e0b 80%,#fde68a 100%)',
        'linear-gradient(135deg,#1e3a5f 0%,#1d4ed8 40%,#3b82f6 75%,#93c5fd 100%)',
    ]
    if tropical and rain_pct < 55:
        return 'linear-gradient(135deg,#14532d 0%,#15803d 35%,#4ade80 75%,#86efac 100%)'
    if tmax >= 26 and rain_pct < 20:
        return hot_variants[idx % len(hot_variants)]
    if tmax >= 20 and rain_pct < 40:
        return 'linear-gradient(135deg,#854d0e 0%,#ca8a04 40%,#fbbf24 80%,#fef08a 100%)'
    if tmax <= 10:
        return 'linear-gradient(135deg,#0c4a6e 0%,#0369a1 40%,#38bdf8 80%,#7dd3fc 100%)'
    if rain_pct >= 60:
        return 'linear-gradient(135deg,#44403c 0%,#78716c 40%,#a8a29e 80%,#d6d3d1 100%)'
    return 'linear-gradient(135deg,#1e3a5f 0%,#2563eb 40%,#60a5fa 80%,#bae6fd 100%)'


def build_top_monthly(lang, loc):
    """Calcule le top 6 destinations du mois courant et retourne le HTML."""
    import os
    mi = _dt.date.today().month
    months_names = loc.get('months', ['Jan','Fév','Mar','Avr','Mai','Jun','Jul','Aoû','Sep','Oct','Nov','Déc'])
    month_name = months_names[mi - 1] if mi <= len(months_names) else str(mi)

    # Labels i18n
    section_title = {
        'fr': f'Meilleurs scores · {month_name}',
        'en': f'Best scores · {month_name}',
        'en-us': f'Best scores · {month_name}',
        'es': f'Mejores puntuaciones · {month_name}',
        'de': f'Beste Bewertungen · {month_name}',
    }.get(lang, f'Best scores · {month_name}')

    ranking_link_lbl = {
        'fr': 'Voir le classement →',
        'en': 'See ranking →',
        'en-us': 'See ranking →',
        'es': 'Ver clasificación →',
        'de': 'Rangliste →',
    }.get(lang, 'See ranking →')

    # Lien vers page pilier mensuelle dynamique
    _mois_url = {1:'janvier',2:'fevrier',3:'mars',4:'avril',5:'mai',6:'juin',
                 7:'juillet',8:'aout',9:'septembre',10:'octobre',11:'novembre',12:'decembre'}
    _en_url   = {1:'january',2:'february',3:'march',4:'april',5:'may',6:'june',
                 7:'july',8:'august',9:'september',10:'october',11:'november',12:'december'}
    _es_url   = {1:'enero',2:'febrero',3:'marzo',4:'abril',5:'mayo',6:'junio',
                 7:'julio',8:'agosto',9:'septiembre',10:'octubre',11:'noviembre',12:'diciembre'}
    _de_url   = {1:'januar',2:'februar',3:'maerz',4:'april',5:'mai',6:'juni',
                 7:'juli',8:'august',9:'september',10:'oktober',11:'november',12:'dezember'}
    _ranking_pages = {
        'fr':    f'ou-partir-en-{_mois_url[mi]}.html',
        'en':    f'../en/where-to-go-in-{_en_url[mi]}.html',
        'en-us': f'../us/where-to-go-in-{_en_url[mi]}.html',
        'es':    f'../es/donde-ir-en-{_es_url[mi]}.html',
        'de':    f'../de/wohin-im-{_de_url[mi]}.html',
    }
    ranking_url = _ranking_pages.get(lang, f'ou-partir-en-{_mois_url[mi]}.html')

    asset_prefix = loc['meta'].get('asset_prefix', '')
    subdir = loc['meta'].get('subdir', '')

    # Charger les données
    climate_month = {}
    climate_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'climate.csv')
    dest_path    = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'destinations.csv')

    try:
        with open(climate_path) as f:
            for row in _csv.DictReader(f):
                if int(row.get('mois_num', 0)) == mi:
                    climate_month[row['slug']] = row
        dest_info = {}
        with open(dest_path) as f:
            for row in _csv.DictReader(f):
                dest_info[row['slug_fr']] = row
        photo_db = {}
        photos_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'destination_photos.csv')
        with open(photos_path) as f:
            for row in _csv.DictReader(f):
                if row.get('photo_url','').strip():
                    photo_db[row['slug_fr']] = row['photo_url'].strip()
    except Exception as e:
        print(f'  ⚠️  build_top_monthly: {e}')
        return ''

    # Nom selon langue
    nom_key = {'fr':'nom_fr','en':'nom_en','en-us':'nom_en','es':'nom_es','de':'nom_de'}.get(lang, 'nom_en')
    slug_key = {'fr':'slug_fr','en':'slug_en','en-us':'slug_en','es':'slug_es','de':'slug_de'}.get(lang, 'slug_en')
    url_prefix = {
        'fr': 'meilleure-periode-',
        'en': '../en/best-time-to-visit-',
        'en-us': '../us/best-time-to-visit-',
        'es': '../es/mejor-epoca-',
        'de': '../de/beste-reisezeit-',
    }.get(lang, 'meilleure-periode-')

    # Calculer top 13
    scored = []
    for slug, row in climate_month.items():
        if slug in dest_info and float(row.get('score') or 0) >= 7.5:
            d = dest_info[slug]
            try:
                tmax  = float(row.get('tmax') or 0)
                rain  = float(row.get('rain_pct') or 0)
                sun   = float(row.get('sun_h') or 0)
                score = float(row.get('score') or 0)
                trop  = d.get('tropical', '') in ('True','true','1')
                slug_dest = d.get(slug_key, slug)
                nom = d.get(nom_key) or d.get('nom_fr', slug)
                if slug_dest:
                    raw_url = photo_db.get(slug, '')
                    import re as _re2
                    photo_url = (_re2.sub(r'\?.*$', '', raw_url) + '?w=300&q=70&fm=webp&fit=crop&crop=entropy') if raw_url else ''
                    scored.append({
                        'nom': nom,
                        'slug_dest': slug_dest,
                        'score': score,
                        'tmax': round(tmax),
                        'rain': round(rain),
                        'sun': round(sun),
                        'tropical': trop,
                        'gradient': _hero_gradient_home(tmax, trop, rain, len(scored)),
                        'photo_url': photo_url,
                        'idx': len(scored),
                        'url': url_prefix + slug_dest + '.html',
                    })
            except: pass

    scored.sort(key=lambda x: -x['score'])
    top6 = scored[:13]
    if not top6:
        return ''

    # Construire HTML
    cards_html = ''
    for i, d in enumerate(top6):
        sun_str = f"{d['sun']}h"
        rain_str = f"{d['rain']}%"
        score_str = f"{d['score']:.1f}"
        gradient = _hero_gradient_home(d['tmax'], d['tropical'], d['rain'], i)
        _pu = d.get('photo_url', '')
        _bg = ('linear-gradient(to top,rgba(0,0,0,.65) 0%,rgba(0,0,0,.1) 60%,transparent 100%),url(' + _pu + ') center/cover no-repeat') if _pu else gradient
        cards_html += (
            f'<a class="top-card" href="{d["url"]}">'
            f'<div class="top-card-img" style="background:{_bg}">'
            f'<div class="top-card-score">{score_str}</div>'
            f'<div><div class="top-card-name">{d["nom"]}</div>'
            f'<div class="top-card-month">{month_name}</div></div>'
            f'</div>'
            f'<div class="top-card-foot">'
            f'<span class="top-card-stat">☀️ {sun_str}</span>'
            f'<span class="top-card-stat">💧 {rain_str}</span>'
            f'</div>'
            f'</a>'
        )

    return (
        f'<div class="home-divider"></div>'
        f'<div class="home-section">'
        f'<div class="home-section-head">'
        f'<div class="home-section-title">{section_title}</div>'
        f'<a class="home-section-link" href="{ranking_url}" aria-label="{ranking_link_lbl} — {section_title}">{ranking_link_lbl}</a>'
        f'</div>'
        f'<div class="top-cards">{cards_html}</div>'
        f'</div>'
    )


def build_rankings_section(lang, loc):
    """4 sections horizontales photo-scroll (top mondial, plage, été, europe)."""
    import os, re as _re3

    asset_prefix = loc['meta'].get('asset_prefix', '')
    nom_key  = {'fr':'nom_fr','en':'nom_en','en-us':'nom_en','es':'nom_es','de':'nom_de'}.get(lang,'nom_en')
    slug_key = {'fr':'slug_fr','en':'slug_en','en-us':'slug_en','es':'slug_es','de':'slug_de'}.get(lang,'slug_en')
    url_pfx  = {'fr':'meilleure-periode-','en':'../en/best-time-to-visit-','en-us':'../us/best-time-to-visit-',
                'es':'../es/mejor-epoca-','de':'../de/beste-reisezeit-'}.get(lang,'meilleure-periode-')
    link_lbl = {'fr':'Voir le classement →','en':'See ranking →','en-us':'See ranking →',
                'es':'Ver clasificación →','de':'Rangliste →'}.get(lang,'See ranking →')

    # Charger données
    climate_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'climate.csv')
    dest_path    = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'destinations.csv')
    photos_path  = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'destination_photos.csv')
    try:
        import csv as _c2
        climate_all = {}
        with open(climate_path) as f:
            for r in _c2.DictReader(f):
                s = r['slug']; m = int(r.get('mois_num',0))
                if s not in climate_all: climate_all[s] = {}
                climate_all[s][m] = r
        dest_info = {}
        with open(dest_path) as f:
            for r in _c2.DictReader(f): dest_info[r['slug_fr']] = r
        photo_db = {}
        with open(photos_path) as f:
            for r in _c2.DictReader(f):
                if r.get('photo_url','').strip(): photo_db[r['slug_fr']] = r['photo_url'].strip()
    except Exception as e:
        return ''

    EUROPE = {'Albanie','Allemagne','Andorre','Autriche','Belgique','Bosnie','Bulgarie','Chypre','Croatie',
              'Danemark','Espagne','Estonie','Finlande','France','Grèce','Hongrie','Irlande','Islande',
              'Italie','Kosovo','Lettonie','Lituanie','Luxembourg','Macédoine','Malte','Moldavie',
              'Monaco','Monténégro','Norvège','Pays-Bas','Pologne','Portugal','Roumanie','Serbie',
              'Slovaquie','Slovénie','Suède','Suisse','Tchéquie','Turquie','Ukraine','Royaume-Uni'}
    COASTAL = {'True','true','1'}

    def _avg_score(slug):
        ms = climate_all.get(slug, {})
        if len(ms) < 12: return 0
        return sum(float(ms[m].get('score',0)) for m in range(1,13)) / 12

    def _summer_score(slug):
        ms = climate_all.get(slug, {})
        if not all(m in ms for m in [6,7,8]): return 0
        return sum(float(ms[m].get('score',0)) for m in [6,7,8]) / 3

    def _beach_score(slug):
        ms = climate_all.get(slug, {})
        if len(ms) < 12: return 0
        d = dest_info.get(slug, {})
        if d.get('coastal','') not in COASTAL: return 0
        return sum(float(ms[m].get('score',0)) for m in range(1,13)) / 12

    def _top(scorer, n=12, europe_only=False):
        results = []
        for slug, d in dest_info.items():
            if d.get('precision') == 'country': continue
            if europe_only and d.get('pays','') not in EUROPE: continue
            sc = scorer(slug)
            if sc <= 0: continue
            sk = d.get(slug_key, slug)
            nm = d.get(nom_key) or d.get('nom_fr', slug)
            pu = photo_db.get(slug, '')
            if pu: pu = _re3.sub(r'\?.*$', '', pu) + '?w=300&q=70&fm=webp&fit=crop&crop=entropy'
            if sk: results.append({'nom':nm,'slug_dest':sk,'score':sc,'photo_url':pu,
                                   'url':url_pfx+sk+'.html'})
        results.sort(key=lambda x: -x['score'])
        return results[:n]

    def _cards_html(items):
        html = ''
        for d in items:
            pu = d.get('photo_url','')
            if pu:
                bg = f'linear-gradient(to top,rgba(0,0,0,.65) 0%,rgba(0,0,0,.1) 60%,transparent 100%),url({pu}) center/cover no-repeat'
            else:
                bg = 'linear-gradient(135deg,#1a2a3a,#243448)'
            html += (
                f'<a class="top-card" href="{d["url"]}">'
                f'<div class="top-card-img" style="background:{bg}">'
                f'<div class="top-card-score">{d["score"]:.1f}</div>'
                f'<div><div class="top-card-name">{d["nom"]}</div></div>'
                f'</div>'
                f'<div class="top-card-foot">'
                f'<span class="top-card-stat">⭐ {d["score"]:.1f}/10</span>'
                f'</div>'
                f'</a>'
            )
        return html

    sections_cfg = {
        'fr': [
            ('🏆 Top mondial', 'classement-destinations-meteo-2026.html', _top(_avg_score)),
            ('🏖️ Plage & baignade', 'classement-destinations-plage-2026.html', _top(_beach_score)),
            ('☀️ Destinations été', 'classement-destinations-meteo-ete-2026.html', _top(_summer_score)),
            ('🌍 Europe', 'classement-destinations-europe-meteo-2026.html', _top(_avg_score, europe_only=True)),
        ],
        'en': [
            ('🏆 Global top', '../en/best-destinations-weather-ranking-2026.html', _top(_avg_score)),
            ('🏖️ Beach', '../en/best-beach-destinations-weather-2026.html', _top(_beach_score)),
            ('☀️ Summer', '../en/best-destinations-summer-weather-2026.html', _top(_summer_score)),
            ('🌍 Europe', '../en/best-europe-weather-ranking-2026.html', _top(_avg_score, europe_only=True)),
        ],
    }
    sections_cfg['en-us'] = [(t, u.replace('../en/',  '../us/'), d) for t,u,d in sections_cfg['en']]
    sections_cfg['es']    = sections_cfg.get('es', sections_cfg['en'])
    sections_cfg['de']    = sections_cfg.get('de', sections_cfg['en'])

    sections = sections_cfg.get(lang, sections_cfg['en'])
    html = ''
    for title, url, items in sections:
        if not items: continue
        html += (
            f'<div class="home-divider"></div>'
            f'<div class="home-section">'
            f'<div class="home-section-head">'
            f'<div class="home-section-title">{title}</div>'
            f'<a class="home-section-link" href="{url}" aria-label="{link_lbl} — {title}">{link_lbl}</a>'
            f'</div>'
            f'<div class="top-cards">{_cards_html(items)}</div>'
            f'</div>'
        )
    return html


def build_trust_bar(lang):
    """Génère la trust bar avec les chiffres clés."""
    labels = {
        'fr': ('destinations', '10 ans données ERA5', "1 an à l'avance", 'langues'),
        'en': ('destinations', '10 yrs ERA5 data', '1 year ahead', 'languages'),
        'en-us': ('destinations', '10 yrs ERA5 data', '1 year ahead', 'languages'),
        'es': ('destinos', '10 años datos ERA5', '1 año de antelación', 'idiomas'),
        'de': ('Destinationen', '10 J. ERA5 Daten', '1 Jahr im Voraus', 'Sprachen'),
    }.get(lang, ('destinations', '10 yrs ERA5', '1 year ahead', 'languages'))

    return (
        f'<div class="home-divider"></div>'
        f'<div class="trust-bar">'
        f'<div class="trust-item"><div class="trust-n">697</div><div class="trust-l">{labels[0]}</div></div>'
        f'<div class="trust-item"><div class="trust-n">10 ans</div><div class="trust-l">{labels[1]}</div></div>'
        f'<div class="trust-item"><div class="trust-n">1 an</div><div class="trust-l">{labels[2]}</div></div>'
        f'<div class="trust-item"><div class="trust-n">5</div><div class="trust-l">{labels[3]}</div></div>'
        f'</div>'
    )

def build_hub_footer(current_lang, current_loc):
    """Generate the lang-switcher div for a hub page footer.

    Reads SUPPORTED_LANGS — adding a language requires no change here,
    only a new locale file + a new app.html.
    """
    current_sub = current_loc['meta']['subdir']  # '' for FR, 'en', 'es', 'us'
    links = []
    for lang in SUPPORTED_LANGS:
        if lang == current_lang:
            continue
        loc = load_locale(lang)
        sub = loc['meta']['subdir']
        flag_file = loc['meta']['flag']          # e.g. 'flags/gb.png'
        label = loc['meta']['lang_label']

        # Compute relative path from current hub to target app.html
        if current_sub == '':
            # root → sub/app.html
            href = f"{sub}/app.html" if sub else "index.html"
            flag_src = flag_file          # already relative to root
        else:
            # sub/ → ../app.html or ../other_sub/app.html
            href = "../index.html" if sub == '' else f"../{sub}/app.html"
            flag_src = f"../{flag_file}"

        # Valeur du cookie selon la langue cible
        cookie_val = 'en-us' if lang == 'en-us' else ('fr' if lang == 'fr' else lang)
        links.append(
            f'<a href="{href}" onclick="document.cookie=\'bdw_lang={cookie_val};path=/;max-age=31536000\'" style="color:inherit;text-decoration:none">'
            f'<img src="{flag_src}" width="20" height="15" alt="" '
            f'style="vertical-align:middle;border-radius:2px"> {label}</a>'
        )

    parts = []
    for i, link in enumerate(links):
        if i == 0:
            parts.append(f'<span style="white-space:nowrap">{link}</span>')
        else:
            parts.append('<span style="white-space:nowrap;opacity:.4">·</span>')
            parts.append(f'<span style="white-space:nowrap">{link}</span>')
    return ''.join(parts)


def inject_hub_footer(filepath, current_lang, current_loc):
    """Replace content between <!-- HUB-FOOTER-START --> / <!-- HUB-FOOTER-END --> markers.
    Also handles legacy one-shot <!-- HUB-FOOTER --> marker (upgrades it to START/END).
    """
    content = open(filepath, encoding='utf-8').read()
    START = '<!-- HUB-FOOTER-START -->'
    END   = '<!-- HUB-FOOTER-END -->'
    footer_html = build_hub_footer(current_lang, current_loc)

    # Legacy one-shot marker → upgrade to persistent markers
    legacy = '<!-- HUB-FOOTER -->'
    if legacy in content:
        content = content.replace(legacy, START + footer_html + END)
        open(filepath, 'w', encoding='utf-8').write(content)
        return True

    if START not in content or END not in content:
        return False

    import re
    new_content = re.sub(
        re.escape(START) + '.*?' + re.escape(END),
        START + footer_html + END,
        content,
        flags=re.DOTALL
    )
    open(filepath, 'w', encoding='utf-8').write(new_content)
    return True


dests = []
with open('data/destinations.csv', encoding='utf-8-sig') as f:
    for r in csv.DictReader(f):
        dests.append(r)
print(f"📦 {len(dests)} destinations")

FLAGS = {'fr': '🇫🇷', 'en': '🇬🇧', 'en-us': '🇺🇸', 'es': '🇪🇸', 'de': '🇩🇪'}
LINK_PATTERN = {'fr': 'meilleure-periode-', 'en': 'best-time-to-visit-', 'en-us': 'best-time-to-visit-', 'es': 'mejor-epoca-', 'de': 'beste-reisezeit-'}

for lang in ['fr', 'en', 'en-us', 'es', 'de']:
    cfg = LANG_CONFIG[lang]
    loc = load_locale(lang)
    output = cfg['output']
    flag = FLAGS.get(lang, '🌍')
    print(f"\n{flag} {output}...")

    # 1. Générer depuis le template (structure HTML commune)
    if generate_from_template(lang, loc):
        print(f"  ✅ Template appliqué")
    else:
        print(f"  ⚠️  Erreur template — fichier existant conservé")

    # 2. Injecter les SILOs (destinations)
    if 'SILO 1' in open(output).read():
        if inject(output, dests, loc):
            pattern = LINK_PATTERN.get(lang, 'meilleure-periode-')
            c = len(re.findall(pattern, open(output).read()))
            print(f"  ✅ {c} liens destinations")
    else:
        print(f"  ⚠️  Marqueur SILO 1 absent")

# Inject lang-switcher footers
print("\n🔗 Injection footers langue...")
for lang in ['fr', 'en', 'en-us', 'es', 'de']:
    filepath = LANG_CONFIG[lang]['output']
    loc = load_locale(lang)
    if os.path.exists(filepath):
        if inject_hub_footer(filepath, lang, loc):
            print(f"  ✅ {filepath} footer mis à jour")
        else:
            print(f"  ⚠️  {filepath} : marqueur <!-- HUB-FOOTER --> absent")

print("\n✅ Done")
