"""
Single source of truth for geographic region logic.
Imported by all generators: generate_piliers, generate_classements,
generate_index_hub, generate_comparatifs, generate_pages, generate_widgets.
"""

REGION_MAP = {
    # Europe
    'Albanie':'eu','Allemagne':'eu','Andorre':'eu','Arménie':'eu','Autriche':'eu',
    'Azerbaïdjan':'eu','Belgique':'eu','Bosnie-Herzégovine':'eu','Bulgarie':'eu',
    'Chypre':'eu','Croatie':'eu','Danemark':'eu','Espagne':'eu','Estonie':'eu',
    'Finlande':'eu','France':'eu','Gibraltar':'eu','Grèce':'eu','Géorgie':'eu',
    'Hongrie':'eu','Irlande':'eu','Islande':'eu','Italie':'eu','Lettonie':'eu',
    'Lituanie':'eu','Macédoine du Nord':'eu','Malte':'eu','Monaco':'eu',
    'Monténégro':'eu','Norvège':'eu','Pays-Bas':'eu','Pologne':'eu','Portugal':'eu',
    'Roumanie':'eu','Royaume-Uni':'eu','Russie':'eu','Serbie':'eu','Slovaquie':'eu',
    'Slovénie':'eu','Suisse':'eu','Suède':'eu','Tchéquie':'eu','Ukraine':'eu',
    'Écosse':'eu',
    # Afrique
    'Afrique du Sud':'af','Algérie':'af','Bénin':'af','Botswana':'af',
    'Burkina Faso':'af','Cameroun':'af','Cap-Vert':'af',"Côte d'Ivoire":'af',
    'Égypte':'af','Éthiopie':'af','Gabon':'af','Gambie':'af','Ghana':'af',
    'Kenya':'af','Madagascar':'af','Malawi':'af','Maroc':'af','Maurice':'af',
    'Mozambique':'af','Namibie':'af','Nigeria':'af','Ouganda':'af','Rwanda':'af',
    'Sénégal':'af','Seychelles':'af','Sierra Leone':'af','Tanzanie':'af',
    'Togo':'af','Tunisie':'af','Zambie':'af','Zimbabwe':'af',
    # Amériques
    'Antigua-et-Barbuda':'am','Argentine':'am','Aruba':'am','Bahamas':'am',
    'Barbade':'am','Belize':'am','Bolivie':'am','Brésil':'am','Canada':'am',
    'Chili':'am','Colombie':'am','Costa Rica':'am','Cuba':'am','Curaçao':'am',
    'Dominique':'am','Équateur':'am','États-Unis':'am','Guatemala':'am',
    'Honduras':'am','Îles Caïmans':'am','Îles Vierges américaines':'am',
    'Jamaïque':'am','Mexique':'am','Nicaragua':'am','Panama':'am',
    'Pays-Bas caribéens':'am','Paraguay':'am','Pérou':'am','Porto Rico':'am',
    'République Dominicaine':'am','Saint-Vincent-et-les-Grenadines':'am',
    'Sainte-Lucie':'am','Trinité-et-Tobago':'am','Turks-et-Caïcos':'am',
    'Uruguay':'am',
    # Moyen-Orient & Asie Centrale
    'Arabie Saoudite':'me','Bahreïn':'me','Émirats Arabes Unis':'me',
    'Émirats arabes unis':'me','Iran':'me','Israël':'me','Jordanie':'me',
    'Kazakhstan':'me','Kirghizistan':'me','Koweït':'me','Liban':'me',
    'Oman':'me','Ouzbékistan':'me','Qatar':'me','Tadjikistan':'me',
    'Turquie':'me','Yémen':'me',
    # Asie
    'Bhoutan':'as','Cambodge':'as','Chine':'as','Corée du Sud':'as',
    'Inde':'as','Indonésie':'as','Japon':'as','Laos':'as','Malaisie':'as',
    'Maldives':'as','Mongolie':'as','Myanmar':'as','Népal':'as',
    'Philippines':'as','Singapour':'as','Sri Lanka':'as','Taïwan':'as',
    'Thaïlande':'as','Vietnam':'as','Viêt Nam':'as',
    # Océanie
    'Australie':'oc','Fidji':'oc','Nouvelle-Calédonie':'oc','Nouvelle-Zélande':'oc',
    'Îles Cook':'oc','Palaos':'oc','Papouasie-Nouvelle-Guinée':'oc',
    'Polynésie française':'oc','Samoa':'oc','Tonga':'oc','Vanuatu':'oc',
}

MACARONESIA_SLUGS = {
    'canaries','tenerife','gran-canaria','fuerteventura','lanzarote',
    'la-palma','la-gomera','el-hierro',  # Canaries
    'madere','funchal',                   # Madère
    'azores',                             # Açores
    'cap-vert','sal','praia',             # Cap-Vert
}

SLUG_REGION_OVERRIDE = {
    # Caraïbes
    'martinique':'car','guadeloupe':'car','saint-martin':'car',
    'saint-barthelemy':'car','saint-pierre-et-miquelon':'am-n',
    'bermudes':'car','guyane':'am-s',
    # Afrique / Océan Indien
    'reunion':'af','mayotte':'af',
    # Pacifique / Océanie
    'polynesie':'oc','bora-bora':'oc','nouvelle-caledonie':'oc','moorea':'oc',
    # Caribbean islands
    'punta-cana':'car','nassau':'car','barbade':'car','sainte-lucie':'car',
    'saint-thomas':'car','san-juan':'car','roatan':'car','curacao':'car',
    'aruba':'car','dominique':'car','grenadines':'car','saint-vincent':'car',
    'cayman-islands':'car','turks-et-caicos':'car','bonaire':'car','providencia':'car',
}

CARIBBEAN_COUNTRIES = {
    'Cuba','République Dominicaine','Bahamas','Barbade','Sainte-Lucie',
    'Jamaïque','Curaçao','Aruba','Trinité-et-Tobago','Antigua-et-Barbuda',
    'Dominique','Turks-et-Caïcos','Îles Caïmans','Îles Vierges américaines',
    'Saint-Vincent-et-les-Grenadines','Pays-Bas caribéens',
}
NORTH_AM_COUNTRIES  = {'États-Unis','Canada','Mexique'}
NORTH_AFRICA_COUNTRIES = {'Maroc','Tunisie','Algérie','Égypte','Libye','Soudan'}

def reg(pays, slug=None):
    """Return the region code for a destination."""
    if slug and slug in SLUG_REGION_OVERRIDE:
        return SLUG_REGION_OVERRIDE[slug]
    if slug and slug in MACARONESIA_SLUGS:
        return 'atl'
    base = REGION_MAP.get(pays, 'other')
    if base == 'am':
        if pays in CARIBBEAN_COUNTRIES:  return 'car'
        if pays in NORTH_AM_COUNTRIES:   return 'am-n'
        return 'am-s'
    if base == 'af':
        return 'af-nord' if pays in NORTH_AFRICA_COUNTRIES else 'af'
    return base

REGION_LABELS = {
    'fr':    {'all':'Monde','eu':'Europe','af-nord':'Afrique du Nord',
              'af':'Afrique & Océan Indien','atl':'Îles Atlantiques',
              'am-n':'Amér. du Nord','am-s':'Amér. du Sud','car':'Caraïbes',
              'as':'Asie','me':'Moyen-Orient','oc':'Océanie'},
    'en':    {'all':'World','eu':'Europe','af-nord':'North Africa',
              'af':'Africa & Indian Ocean','atl':'Atlantic Islands',
              'am-n':'N. America','am-s':'S. America','car':'Caribbean',
              'as':'Asia','me':'Middle East','oc':'Oceania'},
    'en-us': {'all':'World','eu':'Europe','af-nord':'North Africa',
              'af':'Africa & Indian Ocean','atl':'Atlantic Islands',
              'am-n':'N. America','am-s':'S. America','car':'Caribbean',
              'as':'Asia','me':'Middle East','oc':'Oceania'},
    'es':    {'all':'Mundo','eu':'Europa','af-nord':'África del Norte',
              'af':'África & Océano Índico','atl':'Islas Atlánticas',
              'am-n':'Norteamérica','am-s':'Sudamérica','car':'Caribe',
              'as':'Asia','me':'Oriente Medio','oc':'Oceanía'},
    'de':    {'all':'Welt','eu':'Europa','af-nord':'Nordafrika',
              'af':'Afrika & Indischer Ozean','atl':'Atlantische Inseln',
              'am-n':'Nordamerika','am-s':'Südamerika','car':'Karibik',
              'as':'Asien','me':'Naher Osten','oc':'Ozeanien'},
}

# NON_EUROPE_SLUGS kept for backward compat with generate_classements
NON_EUROPE_SLUGS = set(MACARONESIA_SLUGS) | set(SLUG_REGION_OVERRIDE.keys())
