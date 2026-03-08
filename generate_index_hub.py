#!/usr/bin/env python3
"""Regenerate SEO destination hub: search + 6 accordions + sub-accordions."""
import csv, re, os
import html as html_mod

# ── slug → (mega_region, sub_region) overrides ──
# Priorité sur MAPPING[pays] pour les territoires géographiquement hors-métropole
SLUG_OVERRIDE = {
    # DOM-TOM français → régions géographiques
    'guadeloupe':     ('ameriques', 'Caraïbes'),
    'martinique':     ('ameriques', 'Caraïbes'),
    'saint-martin':   ('ameriques', 'Caraïbes'),
    'saint-barthelemy': ('ameriques', 'Caraïbes'),
    'guyane':         ('ameriques', 'Amérique du Sud'),
    'reunion':        ('afrique-mo', 'Océan Indien'),
    'mayotte':        ('afrique-mo', 'Océan Indien'),
    'polynesie':      ('oceanie', 'Pacifique & Outre-mer'),
    'bora-bora':      ('oceanie', 'Pacifique & Outre-mer'),
    'nouvelle-caledonie': ('oceanie', 'Pacifique & Outre-mer'),
    'saint-pierre-et-miquelon': ('ameriques', 'Amérique du Nord'),
    # Bermudes (Royaume-Uni) → Caraïbes
    'bermudes':       ('ameriques', 'Caraïbes'),
    # Canaries (Espagne) → Macaronésie
    'canaries':       ('afrique-mo', 'Macaronésie'),
    'tenerife':       ('afrique-mo', 'Macaronésie'),
    'gran-canaria':   ('afrique-mo', 'Macaronésie'),
    'fuerteventura':  ('afrique-mo', 'Macaronésie'),
    'lanzarote':      ('afrique-mo', 'Macaronésie'),
    'la-palma':       ('afrique-mo', 'Macaronésie'),
    'la-gomera':      ('afrique-mo', 'Macaronésie'),
    'el-hierro':      ('afrique-mo', 'Macaronésie'),
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
    'Maroc': ('afrique-mo', 'Afrique du Nord'),
    'Algérie': ('afrique-mo', 'Afrique du Nord'),
    'Tunisie': ('afrique-mo', 'Afrique du Nord'),
    'Égypte': ('afrique-mo', 'Afrique du Nord'),
    'Cap-Vert': ('afrique-mo', "Afrique de l'Ouest"),
    "Côte d'Ivoire": ('afrique-mo', "Afrique de l'Ouest"),
    'Ghana': ('afrique-mo', "Afrique de l'Ouest"),
    'Nigeria': ('afrique-mo', "Afrique de l'Ouest"),
    'Sénégal': ('afrique-mo', "Afrique de l'Ouest"),
    'Burkina Faso': ('afrique-mo', "Afrique de l'Ouest"),
    'Bénin': ('afrique-mo', "Afrique de l'Ouest"),
    'Cameroun': ('afrique-mo', "Afrique de l'Ouest"),
    'Sierra Leone': ('afrique-mo', "Afrique de l'Ouest"),
    'Togo': ('afrique-mo', "Afrique de l'Ouest"),
    'Gabon': ('afrique-mo', "Afrique de l'Ouest"),
    'Gambie': ('afrique-mo', "Afrique de l'Ouest"),
    'Kenya': ('afrique-mo', "Afrique de l'Est"),
    'Ouganda': ('afrique-mo', "Afrique de l'Est"),
    'Rwanda': ('afrique-mo', "Afrique de l'Est"),
    'Tanzanie': ('afrique-mo', "Afrique de l'Est"),
    'Éthiopie': ('afrique-mo', "Afrique de l'Est"),
    'Afrique du Sud': ('afrique-mo', 'Afrique australe'),
    'Mozambique': ('afrique-mo', 'Afrique australe'),
    'Namibie': ('afrique-mo', 'Afrique australe'),
    'Zimbabwe': ('afrique-mo', 'Afrique australe'),
    'Botswana': ('afrique-mo', 'Afrique australe'),
    'Zambie': ('afrique-mo', 'Afrique australe'),
    'Malawi': ('afrique-mo', 'Afrique australe'),
    'Madagascar': ('afrique-mo', 'Océan Indien'),
    'Maurice': ('afrique-mo', 'Océan Indien'),
    'Seychelles': ('afrique-mo', 'Océan Indien'),
    'Arabie Saoudite': ('afrique-mo', 'Moyen-Orient'),
    'Bahreïn': ('afrique-mo', 'Moyen-Orient'),
    'Iran': ('afrique-mo', 'Moyen-Orient'),
    'Israël': ('afrique-mo', 'Moyen-Orient'),
    'Jordanie': ('afrique-mo', 'Moyen-Orient'),
    'Koweït': ('afrique-mo', 'Moyen-Orient'),
    'Liban': ('afrique-mo', 'Moyen-Orient'),
    'Oman': ('afrique-mo', 'Moyen-Orient'),
    'Qatar': ('afrique-mo', 'Moyen-Orient'),
    'Émirats Arabes Unis': ('afrique-mo', 'Moyen-Orient'),
    'Émirats arabes unis': ('afrique-mo', 'Moyen-Orient'),
    'Yémen': ('afrique-mo', 'Moyen-Orient'),
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
    'Canada': ('ameriques', 'Amérique du Nord'),
    'États-Unis': ('ameriques', 'Amérique du Nord'),
    'Antigua-et-Barbuda': ('ameriques', 'Caraïbes'),
    'Aruba': ('ameriques', 'Caraïbes'),
    'Bahamas': ('ameriques', 'Caraïbes'),
    'Barbade': ('ameriques', 'Caraïbes'),
    'Cuba': ('ameriques', 'Caraïbes'),
    'Curaçao': ('ameriques', 'Caraïbes'),
    'Jamaïque': ('ameriques', 'Caraïbes'),
    'Porto Rico': ('ameriques', 'Caraïbes'),
    'République Dominicaine': ('ameriques', 'Caraïbes'),
    'Sainte-Lucie': ('ameriques', 'Caraïbes'),
    'Trinité-et-Tobago': ('ameriques', 'Caraïbes'),
    'Turks-et-Caïcos': ('ameriques', 'Caraïbes'),
    'Dominique': ('ameriques', 'Caraïbes'),
    'Pays-Bas caribéens': ('ameriques', 'Caraïbes'),
    'Saint-Vincent-et-les-Grenadines': ('ameriques', 'Caraïbes'),
    'Îles Caïmans': ('ameriques', 'Caraïbes'),
    'Îles Vierges américaines': ('ameriques', 'Caraïbes'),
    'Belize': ('ameriques', 'Mexique & Amérique Centrale'),
    'Costa Rica': ('ameriques', 'Mexique & Amérique Centrale'),
    'Guatemala': ('ameriques', 'Mexique & Amérique Centrale'),
    'Honduras': ('ameriques', 'Mexique & Amérique Centrale'),
    'Mexique': ('ameriques', 'Mexique & Amérique Centrale'),
    'Nicaragua': ('ameriques', 'Mexique & Amérique Centrale'),
    'Panama': ('ameriques', 'Mexique & Amérique Centrale'),
    'Argentine': ('ameriques', 'Amérique du Sud'),
    'Bolivie': ('ameriques', 'Amérique du Sud'),
    'Brésil': ('ameriques', 'Amérique du Sud'),
    'Chili': ('ameriques', 'Amérique du Sud'),
    'Colombie': ('ameriques', 'Amérique du Sud'),
    'Paraguay': ('ameriques', 'Amérique du Sud'),
    'Pérou': ('ameriques', 'Amérique du Sud'),
    'Uruguay': ('ameriques', 'Amérique du Sud'),
    'Équateur': ('ameriques', 'Amérique du Sud'),
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
    'Afrique du Sud':{'fr':'Afrique du Sud','en':'South Africa','es':'Sudáfrica'},
    'Albanie':{'fr':'Albanie','en':'Albania','es':'Albania'},
    'Algérie':{'fr':'Algérie','en':'Algeria','es':'Argelia'},
    'Allemagne':{'fr':'Allemagne','en':'Germany','es':'Alemania'},
    'Andorre':{'fr':'Andorre','en':'Andorra','es':'Andorra'},
    'Antigua-et-Barbuda':{'fr':'Antigua-et-Barbuda','en':'Antigua & Barbuda','es':'Antigua y Barbuda'},
    'Arabie Saoudite':{'fr':'Arabie Saoudite','en':'Saudi Arabia','es':'Arabia Saudita'},
    'Argentine':{'fr':'Argentine','en':'Argentina','es':'Argentina'},
    'Arménie':{'fr':'Arménie','en':'Armenia','es':'Armenia'},
    'Aruba':{'fr':'Aruba','en':'Aruba','es':'Aruba'},
    'Australie':{'fr':'Australie','en':'Australia','es':'Australia'},
    'Azerbaïdjan':{'fr':'Azerbaïdjan','en':'Azerbaijan','es':'Azerbaiyán'},
    'Autriche':{'fr':'Autriche','en':'Austria','es':'Austria'},
    'Bahamas':{'fr':'Bahamas','en':'Bahamas','es':'Bahamas'},
    'Bahreïn':{'fr':'Bahreïn','en':'Bahrain','es':'Baréin'},
    'Barbade':{'fr':'Barbade','en':'Barbados','es':'Barbados'},
    'Belgique':{'fr':'Belgique','en':'Belgium','es':'Bélgica'},
    'Belize':{'fr':'Belize','en':'Belize','es':'Belice'},
    'Bhoutan':{'fr':'Bhoutan','en':'Bhutan','es':'Bután'},
    'Bolivie':{'fr':'Bolivie','en':'Bolivia','es':'Bolivia'},
    'Bosnie-Herzégovine':{'fr':'Bosnie-Herzégovine','en':'Bosnia & Herzegovina','es':'Bosnia y Herzegovina'},
    'Botswana':{'fr':'Botswana','en':'Botswana','es':'Botsuana'},
    'Brésil':{'fr':'Brésil','en':'Brazil','es':'Brasil'},
    'Bulgarie':{'fr':'Bulgarie','en':'Bulgaria','es':'Bulgaria'},
    'Burkina Faso':{'fr':'Burkina Faso','en':'Burkina Faso','es':'Burkina Faso'},
    'Bénin':{'fr':'Bénin','en':'Benin','es':'Benín'},
    'Cambodge':{'fr':'Cambodge','en':'Cambodia','es':'Camboya'},
    'Cameroun':{'fr':'Cameroun','en':'Cameroon','es':'Camerún'},
    'Canada':{'fr':'Canada','en':'Canada','es':'Canadá'},
    'Cap-Vert':{'fr':'Cap-Vert','en':'Cape Verde','es':'Cabo Verde'},
    'Chili':{'fr':'Chili','en':'Chile','es':'Chile'},
    'Chine':{'fr':'Chine','en':'China','es':'China'},
    'Chypre':{'fr':'Chypre','en':'Cyprus','es':'Chipre'},
    'Colombie':{'fr':'Colombie','en':'Colombia','es':'Colombia'},
    'Corée du Sud':{'fr':'Corée du Sud','en':'South Korea','es':'Corea del Sur'},
    'Costa Rica':{'fr':'Costa Rica','en':'Costa Rica','es':'Costa Rica'},
    'Croatie':{'fr':'Croatie','en':'Croatia','es':'Croacia'},
    'Cuba':{'fr':'Cuba','en':'Cuba','es':'Cuba'},
    'Curaçao':{'fr':'Curaçao','en':'Curaçao','es':'Curazao'},
    "Côte d'Ivoire":{'fr':"Côte d'Ivoire",'en':'Ivory Coast','es':'Costa de Marfil'},
    'Danemark':{'fr':'Danemark','en':'Denmark','es':'Dinamarca'},
    'Dominique':{'fr':'Dominique','en':'Dominica','es':'Dominica'},
    'Espagne':{'fr':'Espagne','en':'Spain','es':'España'},
    'Estonie':{'fr':'Estonie','en':'Estonia','es':'Estonia'},
    'Fidji':{'fr':'Fidji','en':'Fiji','es':'Fiyi'},
    'Finlande':{'fr':'Finlande','en':'Finland','es':'Finlandia'},
    'France':{'fr':'France','en':'France','es':'Francia'},
    'Ghana':{'fr':'Ghana','en':'Ghana','es':'Ghana'},
    'Grèce':{'fr':'Grèce','en':'Greece','es':'Grecia'},
    'Guatemala':{'fr':'Guatemala','en':'Guatemala','es':'Guatemala'},
    'Géorgie':{'fr':'Géorgie','en':'Georgia','es':'Georgia'},
    'Honduras':{'fr':'Honduras','en':'Honduras','es':'Honduras'},
    'Hongrie':{'fr':'Hongrie','en':'Hungary','es':'Hungría'},
    'Inde':{'fr':'Inde','en':'India','es':'India'},
    'Indonésie':{'fr':'Indonésie','en':'Indonesia','es':'Indonesia'},
    'Iran':{'fr':'Iran','en':'Iran','es':'Irán'},
    'Irlande':{'fr':'Irlande','en':'Ireland','es':'Irlanda'},
    'Islande':{'fr':'Islande','en':'Iceland','es':'Islandia'},
    'Israël':{'fr':'Israël','en':'Israel','es':'Israel'},
    'Italie':{'fr':'Italie','en':'Italy','es':'Italia'},
    'Jamaïque':{'fr':'Jamaïque','en':'Jamaica','es':'Jamaica'},
    'Japon':{'fr':'Japon','en':'Japan','es':'Japón'},
    'Jordanie':{'fr':'Jordanie','en':'Jordan','es':'Jordania'},
    'Kazakhstan':{'fr':'Kazakhstan','en':'Kazakhstan','es':'Kazajistán'},
    'Kenya':{'fr':'Kenya','en':'Kenya','es':'Kenia'},
    'Kirghizistan':{'fr':'Kirghizistan','en':'Kyrgyzstan','es':'Kirguistán'},
    'Koweït':{'fr':'Koweït','en':'Kuwait','es':'Kuwait'},
    'Laos':{'fr':'Laos','en':'Laos','es':'Laos'},
    'Lettonie':{'fr':'Lettonie','en':'Latvia','es':'Letonia'},
    'Liban':{'fr':'Liban','en':'Lebanon','es':'Líbano'},
    'Lituanie':{'fr':'Lituanie','en':'Lithuania','es':'Lituania'},
    'Macédoine du Nord':{'fr':'Macédoine du Nord','en':'North Macedonia','es':'Macedonia del Norte'},
    'Madagascar':{'fr':'Madagascar','en':'Madagascar','es':'Madagascar'},
    'Malaisie':{'fr':'Malaisie','en':'Malaysia','es':'Malasia'},
    'Maldives':{'fr':'Maldives','en':'Maldives','es':'Maldivas'},
    'Malte':{'fr':'Malte','en':'Malta','es':'Malta'},
    'Maroc':{'fr':'Maroc','en':'Morocco','es':'Marruecos'},
    'Maurice':{'fr':'Maurice','en':'Mauritius','es':'Mauricio'},
    'Mexique':{'fr':'Mexique','en':'Mexico','es':'México'},
    'Monaco':{'fr':'Monaco','en':'Monaco','es':'Mónaco'},
    'Mongolie':{'fr':'Mongolie','en':'Mongolia','es':'Mongolia'},
    'Monténégro':{'fr':'Monténégro','en':'Montenegro','es':'Montenegro'},
    'Mozambique':{'fr':'Mozambique','en':'Mozambique','es':'Mozambique'},
    'Myanmar':{'fr':'Myanmar','en':'Myanmar','es':'Myanmar'},
    'Namibie':{'fr':'Namibie','en':'Namibia','es':'Namibia'},
    'Nicaragua':{'fr':'Nicaragua','en':'Nicaragua','es':'Nicaragua'},
    'Nigeria':{'fr':'Nigeria','en':'Nigeria','es':'Nigeria'},
    'Norvège':{'fr':'Norvège','en':'Norway','es':'Noruega'},
    'Nouvelle-Calédonie':{'fr':'Nouvelle-Calédonie','en':'New Caledonia','es':'Nueva Caledonia'},
    'Nouvelle-Zélande':{'fr':'Nouvelle-Zélande','en':'New Zealand','es':'Nueva Zelanda'},
    'Népal':{'fr':'Népal','en':'Nepal','es':'Nepal'},
    'Oman':{'fr':'Oman','en':'Oman','es':'Omán'},
    'Ouganda':{'fr':'Ouganda','en':'Uganda','es':'Uganda'},
    'Ouzbékistan':{'fr':'Ouzbékistan','en':'Uzbekistan','es':'Uzbekistán'},
    'Panama':{'fr':'Panama','en':'Panama','es':'Panamá'},
    'Papouasie-Nouvelle-Guinée':{'fr':'Papouasie-Nouvelle-Guinée','en':'Papua New Guinea','es':'Papúa Nueva Guinea'},
    'Paraguay':{'fr':'Paraguay','en':'Paraguay','es':'Paraguay'},
    'Pays-Bas':{'fr':'Pays-Bas','en':'Netherlands','es':'Países Bajos'},
    'Pays-Bas caribéens':{'fr':'Pays-Bas caribéens','en':'Caribbean Netherlands','es':'Países Bajos del Caribe'},
    'Philippines':{'fr':'Philippines','en':'Philippines','es':'Filipinas'},
    'Pologne':{'fr':'Pologne','en':'Poland','es':'Polonia'},
    'Polynésie française':{'fr':'Polynésie française','en':'French Polynesia','es':'Polinesia Francesa'},
    'Porto Rico':{'fr':'Porto Rico','en':'Puerto Rico','es':'Puerto Rico'},
    'Portugal':{'fr':'Portugal','en':'Portugal','es':'Portugal'},
    'Pérou':{'fr':'Pérou','en':'Peru','es':'Perú'},
    'Qatar':{'fr':'Qatar','en':'Qatar','es':'Catar'},
    'Roumanie':{'fr':'Roumanie','en':'Romania','es':'Rumanía'},
    'Royaume-Uni':{'fr':'Royaume-Uni','en':'United Kingdom','es':'Reino Unido'},
    'Rwanda':{'fr':'Rwanda','en':'Rwanda','es':'Ruanda'},
    'République Dominicaine':{'fr':'République Dominicaine','en':'Dominican Republic','es':'República Dominicana'},
    'Saint-Vincent-et-les-Grenadines':{'fr':'Saint-Vincent-et-les-Grenadines','en':'St. Vincent & Grenadines','es':'San Vicente y las Granadinas'},
    'Sainte-Lucie':{'fr':'Sainte-Lucie','en':'Saint Lucia','es':'Santa Lucía'},
    'Samoa':{'fr':'Samoa','en':'Samoa','es':'Samoa'},
    'Serbie':{'fr':'Serbie','en':'Serbia','es':'Serbia'},
    'Seychelles':{'fr':'Seychelles','en':'Seychelles','es':'Seychelles'},
    'Sierra Leone':{'fr':'Sierra Leone','en':'Sierra Leone','es':'Sierra Leona'},
    'Singapour':{'fr':'Singapour','en':'Singapore','es':'Singapur'},
    'Slovaquie':{'fr':'Slovaquie','en':'Slovakia','es':'Eslovaquia'},
    'Slovénie':{'fr':'Slovénie','en':'Slovenia','es':'Eslovenia'},
    'Sri Lanka':{'fr':'Sri Lanka','en':'Sri Lanka','es':'Sri Lanka'},
    'Suisse':{'fr':'Suisse','en':'Switzerland','es':'Suiza'},
    'Suède':{'fr':'Suède','en':'Sweden','es':'Suecia'},
    'Sénégal':{'fr':'Sénégal','en':'Senegal','es':'Senegal'},
    'Tanzanie':{'fr':'Tanzanie','en':'Tanzania','es':'Tanzania'},
    'Taïwan':{'fr':'Taïwan','en':'Taiwan','es':'Taiwán'},
    'Tchéquie':{'fr':'Tchéquie','en':'Czech Republic','es':'República Checa'},
    'Thaïlande':{'fr':'Thaïlande','en':'Thailand','es':'Tailandia'},
    'Togo':{'fr':'Togo','en':'Togo','es':'Togo'},
    'Tonga':{'fr':'Tonga','en':'Tonga','es':'Tonga'},
    'Trinité-et-Tobago':{'fr':'Trinité-et-Tobago','en':'Trinidad & Tobago','es':'Trinidad y Tobago'},
    'Tunisie':{'fr':'Tunisie','en':'Tunisia','es':'Túnez'},
    'Turks-et-Caïcos':{'fr':'Turks-et-Caïcos','en':'Turks & Caicos','es':'Islas Turcas y Caicos'},
    'Turquie':{'fr':'Turquie','en':'Turkey','es':'Turquía'},
    'Ukraine':{'fr':'Ukraine','en':'Ukraine','es':'Ucrania'},
    'Uruguay':{'fr':'Uruguay','en':'Uruguay','es':'Uruguay'},
    'Vanuatu':{'fr':'Vanuatu','en':'Vanuatu','es':'Vanuatu'},
    'Viêt Nam':{'fr':'Viêt Nam','en':'Vietnam','es':'Vietnam'},
    'Yémen':{'fr':'Yémen','en':'Yemen','es':'Yemen'},
    'Zambie':{'fr':'Zambie','en':'Zambia','es':'Zambia'},
    'Zimbabwe':{'fr':'Zimbabwe','en':'Zimbabwe','es':'Zimbabue'},
    'Écosse':{'fr':'Écosse','en':'Scotland','es':'Escocia'},
    'Égypte':{'fr':'Égypte','en':'Egypt','es':'Egipto'},
    'Émirats Arabes Unis':{'fr':'Émirats Arabes Unis','en':'United Arab Emirates','es':'Emiratos Árabes Unidos'},
    'Émirats arabes unis':{'fr':'Émirats Arabes Unis','en':'United Arab Emirates','es':'Emiratos Árabes Unidos'},
    'Équateur':{'fr':'Équateur','en':'Ecuador','es':'Ecuador'},
    'États-Unis':{'fr':'États-Unis','en':'United States','es':'Estados Unidos'},
    'Éthiopie':{'fr':'Éthiopie','en':'Ethiopia','es':'Etiopía'},
    'Gabon':{'fr':'Gabon','en':'Gabon','es':'Gabón'},
    'Gambie':{'fr':'Gambie','en':'Gambia','es':'Gambia'},
    'Gibraltar':{'fr':'Gibraltar','en':'Gibraltar','es':'Gibraltar'},
    'Îles Caïmans':{'fr':'Îles Caïmans','en':'Cayman Islands','es':'Islas Caimán'},
    'Îles Cook':{'fr':'Îles Cook','en':'Cook Islands','es':'Islas Cook'},
    'Îles Vierges américaines':{'fr':'Îles Vierges américaines','en':'U.S. Virgin Islands','es':'Islas Vírgenes de EE.UU.'},
    'Malawi':{'fr':'Malawi','en':'Malawi','es':'Malaui'},
    'Palaos':{'fr':'Palaos','en':'Palau','es':'Palaos'},
    'Tadjikistan':{'fr':'Tadjikistan','en':'Tajikistan','es':'Tayikistán'},
    'Vietnam':{'fr':'Vietnam','en':'Vietnam','es':'Vietnam'},
}

MIN_COUNTRY_SIZE = 3  # own accordion if >= 3 destinations
OTHERS_LABEL = {'fr':'Autres pays','en':'Other countries','es':'Otros países'}

# 5 mega-regions in order (France merged into Europe)
MEGAS = [
    ('europe',     1, {'fr': '🌐 Europe',                         'en': '🌐 Europe',                    'es': '🌐 Europa'}),
    ('afrique-mo', 2, {'fr': '🌐 Afrique & Moyen-Orient',        'en': '🌐 Africa & Middle East',      'es': '🌐 África & Oriente Medio'}),
    ('asie',       3, {'fr': '🌐 Asie',                           'en': '🌐 Asia',                      'es': '🌐 Asia'}),
    ('ameriques',  4, {'fr': '🌐 Amériques',                      'en': '🌐 Americas',                  'es': '🌐 Américas'}),
    ('oceanie',    5, {'fr': '🌐 Océanie & Outre-mer',            'en': '🌐 Oceania & Overseas',        'es': '🌐 Oceanía & Ultramar'}),
]

# Sub-region name translations per language
SUB_NAMES = {
    'Europe du Sud & Méditerranée': {'fr': 'Europe du Sud & Méditerranée', 'en': 'Southern Europe & Mediterranean', 'es': 'Europa del Sur y Mediterráneo'},
    'Europe du Nord & Centrale':    {'fr': 'Europe du Nord & Centrale',    'en': 'Northern & Central Europe',       'es': 'Europa del Norte y Central'},
    'Scandinavie & Baltique':       {'fr': 'Scandinavie & Baltique',       'en': 'Scandinavia & Baltics',           'es': 'Escandinavia y Báltico'},
    'Caucase & Asie Centrale':      {'fr': 'Caucase & Asie Centrale',      'en': 'Caucasus & Central Asia',         'es': 'Cáucaso y Asia Central'},
    'Afrique du Nord':              {'fr': 'Afrique du Nord',              'en': 'North Africa',                    'es': 'África del Norte'},
    "Afrique de l'Ouest":           {'fr': "Afrique de l'Ouest",           'en': 'West Africa',                     'es': 'África Occidental'},
    "Afrique de l'Est":             {'fr': "Afrique de l'Est",             'en': 'East Africa',                     'es': 'África Oriental'},
    'Afrique australe':             {'fr': 'Afrique australe',             'en': 'Southern Africa',                 'es': 'África Austral'},
    'Océan Indien':                 {'fr': 'Océan Indien',                 'en': 'Indian Ocean',                    'es': 'Océano Índico'},
    'Moyen-Orient':                 {'fr': 'Moyen-Orient',                 'en': 'Middle East',                     'es': 'Oriente Medio'},
    'Macaronésie':                  {'fr': 'Macaronésie',                  'en': 'Macaronesia',                     'es': 'Macaronesia'},
    'Asie du Sud-Est':              {'fr': 'Asie du Sud-Est',              'en': 'Southeast Asia',                  'es': 'Asia del Sudeste'},
    "Asie de l'Est":                {'fr': "Asie de l'Est",                'en': 'East Asia',                       'es': 'Asia Oriental'},
    'Asie du Sud':                  {'fr': 'Asie du Sud',                  'en': 'South Asia',                      'es': 'Asia del Sur'},
    'Amérique du Nord':             {'fr': 'Amérique du Nord',             'en': 'North America',                   'es': 'América del Norte'},
    'Caraïbes':                     {'fr': 'Caraïbes',                     'en': 'Caribbean',                       'es': 'Caribe'},
    'Mexique & Amérique Centrale':  {'fr': 'Mexique & Amérique Centrale',  'en': 'Mexico & Central America',        'es': 'México y América Central'},
    'Amérique du Sud':              {'fr': 'Amérique du Sud',              'en': 'South America',                   'es': 'América del Sur'},
    'Australie & Nouvelle-Zélande': {'fr': 'Australie & Nouvelle-Zélande','en': 'Australia & New Zealand',         'es': 'Australia y Nueva Zelanda'},
    'Pacifique & Outre-mer':        {'fr': 'Pacifique & Outre-mer',        'en': 'Pacific & Overseas',              'es': 'Pacífico y Ultramar'},
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
    'Pacifique & Outre-mer': 2,
}

# ── CSS ──
CSS = """
/* ── Destination Hub ── */
.dh-search{position:relative;margin-bottom:24px}
.dh-search input{width:100%;padding:14px 16px 14px 44px;border:1.5px solid #e8e0d0;border-radius:12px;font-size:15px;font-family:inherit;background:#fff;color:#1a1f2e;outline:none;transition:border-color .2s;box-sizing:border-box}
.dh-search input:focus{border-color:#e8940a}
.dh-search input::placeholder{color:#9ca3af}
.dh-search-icon{position:absolute;left:14px;top:50%;transform:translateY(-50%);color:#9ca3af;pointer-events:none;font-size:18px}
.dh-search-clear{position:absolute;right:12px;top:50%;transform:translateY(-50%);background:none;border:none;font-size:18px;color:#9ca3af;cursor:pointer;padding:4px;display:none}
.dh-search-clear.show{display:block}
.dh-count{font-size:12px;color:#7a8fa8;margin:-16px 0 20px 4px;display:none}
.dh-count.show{display:block}

.dh-acc{border:1.5px solid #e8e0d0;border-radius:14px;margin-bottom:10px;overflow:hidden;background:#fff}
.dh-acc-head{width:100%;display:flex;align-items:center;justify-content:space-between;padding:16px 18px;background:#fff;border:none;cursor:pointer;font-family:inherit;text-align:left;gap:12px}
.dh-acc-head:hover{background:#faf8f3}
.dh-acc-label{font-size:16px;font-weight:700;color:#1a1f2e}
.dh-acc-meta{display:flex;align-items:center;gap:10px;flex-shrink:0}
.dh-acc-count{font-size:12px;color:#7a8fa8;background:#f0ebe0;border-radius:20px;padding:2px 10px;font-weight:600}
.dh-acc-chev{font-size:14px;color:#9ca3af;transition:transform .25s}
.dh-acc.open>.dh-acc-head .dh-acc-chev{transform:rotate(180deg)}
.dh-acc-body{display:none;padding:0 18px 14px}
.dh-acc.open>.dh-acc-body{display:block}

.dh-sub{border:1px solid #f0ebe0;border-radius:10px;margin-bottom:8px;overflow:hidden;background:#faf8f3}
.dh-sub-head{width:100%;display:flex;align-items:center;justify-content:space-between;padding:12px 14px;background:#faf8f3;border:none;cursor:pointer;font-family:inherit;text-align:left;gap:10px}
.dh-sub-head:hover{background:#f5f0e5}
.dh-sub-label{font-size:13px;font-weight:700;color:#4a5568}
.dh-sub-count{font-size:11px;color:#9ca3af;font-weight:600}
.dh-sub-chev{font-size:12px;color:#bbb;transition:transform .25s}
.dh-sub.open>.dh-sub-head .dh-sub-chev{transform:rotate(180deg)}
.dh-sub-body{display:none;padding:6px 14px 12px}
.dh-sub.open>.dh-sub-body{display:block}

.dh-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(155px,1fr));gap:8px}
.dh-card{background:#fff;border-radius:10px;padding:10px 12px;text-decoration:none;border:1px solid #e8e0d0;display:flex;align-items:center;gap:9px;transition:border-color .15s,box-shadow .15s}
.dh-card:hover{border-color:#e8940a;box-shadow:0 2px 8px rgba(232,148,10,.12)}
.dh-card img{flex-shrink:0}
.dh-card-name{font-size:12px;font-weight:700;color:#1a1f2e;display:block;line-height:1.3}
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
   if(t.indexOf(q)>-1||p.indexOf(q)>-1){c.classList.remove('dh-hidden');n++}
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


def make_card(slug, name, bare, flag, country, asset_prefix, page_prefix, loc):
    href = f'{page_prefix}{loc["gen"]["annual_href_tpl"].format(slug=slug)}'
    sub = loc['hub']['card_sub']
    return (
        f'<a href="{href}" target="_top" class="dh-card" '
        f'data-name="{html_mod.escape(bare)}" data-country="{html_mod.escape(country)}">'
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
    slug_key = 'slug_fr' if is_fr else ('slug_es' if lang == 'es' else 'slug_en')
    name_key = 'nom_fr' if is_fr else ('nom_es' if lang == 'es' else 'nom_en')

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
        has_subs = True  # always group by country

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
                    sub_label = OTHERS_LABEL.get(lang, 'Other countries')
                    flag_img = ''
                else:
                    trans = COUNTRY_NAMES_TRANS.get(sub_name, {})
                    sub_label = trans.get(lang, sub_name)
                    flag_code = pays_flag.get(sub_name, '')
                    flag_img = f'<img src="{asset_prefix}flags/{flag_code}.png" width="20" height="15" alt="{flag_code}" class="flag-icon" style="margin-right:6px;vertical-align:middle;border-radius:2px"> ' if flag_code else ''
                L.append(f'<span class="dh-sub-label">{flag_img}{html_mod.escape(sub_label)}</span>')
                L.append(f'<span class="dh-acc-meta"><span class="dh-sub-count">{sub_cnt}</span>')
                L.append(f'<span class="dh-sub-chev">▾</span></span></button>')
                L.append(f'<div class="dh-sub-body"><div class="dh-grid">')
                for d in sorted(dests, key=lambda x: x['nom_bare']):
                    slug = d[slug_key]
                    name = d[name_key]
                    L.append(make_card(slug, name, d['nom_bare'], d['flag'], d['pays'], asset_prefix, page_prefix, loc))
                L.append(f'</div></div></div>')
        else:
            # Single sub-region: no sub-accordion, just grid
            dests = list(subs_data.values())[0]
            L.append(f'<div class="dh-grid">')
            for d in sorted(dests, key=lambda x: x['nom_bare']):
                slug = d[slug_key]
                name = d[name_key]
                L.append(make_card(slug, name, d['nom_bare'], d['flag'], d['pays'], asset_prefix, page_prefix, loc))
            L.append(f'</div>')

        L.append(f'</div></div>')

    no_msg = loc['hub']['no_results']
    L.append(f'<div id="dh-no-results" class="dh-no-results">{no_msg}</div>')
    return '\n'.join(L)


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
   <p style="font-size:13px;font-weight:800;letter-spacing:.5px;text-transform:uppercase;color:#1a1f2e;margin:0">&#127758; {title}</p>
   <div style="flex:1;height:2px;background:linear-gradient(90deg,#e8940a,#e8e0d0)"></div>
  </div>
{hub}
 </div>
<script>
{js}
</script>"""

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

        links.append(
            f'<a href="{href}" style="color:inherit;text-decoration:none">'
            f'<img src="{flag_src}" width="20" height="15" alt="" '
            f'style="vertical-align:middle;border-radius:2px"> {label}</a>'
        )

    sep = ' &nbsp;·&nbsp; '
    return sep.join(links)


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

loc_fr = load_locale('fr')
print("\n🇫🇷 index.html...")
if inject('index.html', dests, loc_fr):
    c = len(re.findall(r'meilleure-periode-', open('index.html').read()))
    print(f"  ✅ {c} liens")

if os.path.exists('en/app.html'):
    loc_en = load_locale('en')
    print("\n🇬🇧 en/app.html...")
    if 'SILO 1' in open('en/app.html').read():
        if inject('en/app.html', dests, loc_en):
            c = len(re.findall(r'best-time-to-visit-', open('en/app.html').read()))
            print(f"  ✅ {c} liens")

if os.path.exists('es/app.html'):
    loc_es = load_locale('es')
    print("\n🇪🇸 es/app.html...")
    if 'SILO 1' in open('es/app.html').read():
        if inject('es/app.html', dests, loc_es):
            c = len(re.findall(r'mejor-epoca-', open('es/app.html').read()))
            print(f"  ✅ {c} liens")

if os.path.exists('us/app.html'):
    loc_us = load_locale('en-us')
    print("\n🇺🇸 us/app.html...")
    if 'SILO 1' in open('us/app.html').read():
        if inject('us/app.html', dests, loc_us):
            c = len(re.findall(r'best-time-to-visit-', open('us/app.html').read()))
            print(f"  ✅ {c} liens")

# Inject lang-switcher footers in all hub pages
print("\n🔗 Injection footers langue...")
for lang, filepath in [('fr','index.html'),('en','en/app.html'),('es','es/app.html'),('en-us','us/app.html')]:
    if os.path.exists(filepath):
        loc = load_locale(lang)
        if inject_hub_footer(filepath, lang, loc):
            print(f"  ✅ {filepath} footer mis à jour")
        else:
            print(f"  ⚠️  {filepath} : marqueur <!-- HUB-FOOTER --> absent")

print("\n✅ Done")
