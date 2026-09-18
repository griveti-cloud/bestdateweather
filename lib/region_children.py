# Entites regionales et leurs enfants (archipels, regions touristiques).
# Source UNIQUE : la table etait dupliquee dans generate_piliers.py et
# generate_classements.py, avec des contenus DIFFERENTS, et absente de
# generate_index_hub.py. D'ou l'incoherence signalee entre les apercus de
# la page d'accueil et les pages de classement (les Canaries apparaissaient
# en 2e position sur l'accueil et nulle part dans le classement).
REGION_CHILDREN = {
    'algarve': {'faro'},
    'bretagne': set(),
    'canaries': {'el-hierro', 'fuerteventura', 'gran-canaria', 'la-gomera', 'la-palma', 'lanzarote', 'tenerife'},
    'corse': set(),
    'cote-azur': {'cannes', 'nice'},
    'crete': set(),
    'formentera': set(),
    'ibiza': set(),
    'madere': {'funchal'},
    'majorque': {'alcudia', 'palma-de-majorque'},
    'minorque': set(),
    'porto-rico': {'san-juan'},
    'provence': {'marseille'},
    'sardaigne': set(),
    'sicile': {'catane', 'palerme', 'taormina'},
    'toscane': {'florence', 'sienne'},
}


def strip_region_parents(entries, key='slug_fr'):
    """Retire une entite regionale quand un de ses enfants est deja classe.

    Evite de presenter a la fois 'les Canaries' et 'La Gomera', qui
    designent en partie la meme chose.
    """
    ranked = {e.get(key) for e in entries}
    remove = {p for p, ch in REGION_CHILDREN.items() if p in ranked and ranked & ch}
    return [e for e in entries if e.get(key) not in remove] if remove else entries
