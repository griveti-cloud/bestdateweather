# Audit avis FR — détection style LLM/encyclopédique

**Date** : 2026-05-11 21:48  
**Source** : `data/avis_annuel.json`  
**Total avis FR** : 754  
**Candidats détectés (score ≥ 3)** : 75 (10%)  
**Origine de cet audit** : remontée Gilles 2026-05-11 22h sur Guyane

## Contexte

Découverte d'un avis Guyane FR mal écrit (style LLM brut, 4174 chars,
énumérations à virgules sans articulation, équations '= signature', anglicisme
"Devil's Island" non traduit). Hypothèse : l'audit qualité préalable
("754/754 avis FR completed, Zero LLM patterns globally") a laissé passer
certains avis. Cet audit identifie les candidats potentiels.

## Méthodologie

Score additionné selon 7 patterns heuristiques :

| Pattern | Détection | Points |
|---|---|---|
| 1. `= signature` récurrent | ≥ 2 occurrences | +2 |
| 2. Anglicisme entre guillemets | mots EN clés (street/island/old/etc) | +1 |
| 3. Équations `= X` Wikipedia-style | ≥ 4 occurrences ` = ` | +2 |
| 4. Pourcentages enchaînés | ≥ 5 occurrences `%` | +1 |
| 5. Énumérations longues | ≥ 5 séquences `A, B, C, D` | +1 |
| 6. Longueur excessive | > 3500 chars | +1 |
| 7. Absence voix perso (mon/je) | si len > 1500 | +1 |

**Seuil retenu** : score ≥ 3 (cumul de 2-3 patterns)  
**Limites** : heuristique. Faux positifs possibles (avis détaillés légitimes).
Faux négatifs aussi (avis moches sans ces patterns). Lecture humaine recommandée
avant réécriture.

## Répartition par score

| Score | N avis | Priorité |
|---|---|---|
| 5 | 6 | 🔴 Très haute |
| 4 | 5 | 🟡 Haute |
| 3 | 64 | 🟢 Moyenne |

## Liste complète des 75 candidats

Classés par score décroissant puis longueur. Format compact pour scan rapide.

### 1. 🔴 `peloponnese` — score 5, 4753 chars

**Raisons** : 4× '= signature' · 8× ' = ' · len 4753 chars
  - _Exemples '= signature': les 4 ans pendant 1170 ans = signature culturelle universelle | parabolique avant chaque JO depuis 1936 = signature visuelle des cérémonies olympiques modernes_

> Péloponnèse (Πελοπόννησος), grande péninsule du sud de la Grèce reliée à la Grèce continentale par l'isthme de Corinthe : 1,15 million d'habitants sur 21 549 km². Berceau de la civilisation grecque an...

### 2. 🔴 `jinja` — score 5, 4258 chars

**Raisons** : 3× '= signature' · 6× ' = ' · len 4258 chars
  - _Exemples '= signature': 6695 km vers la Méditerranée Egypte = signature géographique majeure mondialement | découvert la source du Nil 1858 = signature géographique majeure_

> Jinja, ville de l'Ouganda sur la rive nord du Lac Victoria à 80 km à l'est de Kampala : 75 000 habitants. Capitale mondiale du rafting White Water sur le Nil Blanc qui sort directement du Lac Victoria...

### 3. 🔴 `guyane` — score 5, 4189 chars

**Raisons** : 2× '= signature' · 11× ' = ' · len 4189 chars
  - _Exemples '= signature': 1969 = signature historique majeure de la Guyane | un bagnard chinois Pierre Huguet 1893 = signature artistique guyanaise unique_

> Guyane française, département-région d'outre-mer français en Amérique du Sud entre Brésil et Suriname : 300 000 habitants sur 84 000 km² (le plus grand département français en superficie + 1 des plus

### 4. 🔴 `nouvelle-caledonie` — score 5, 4144 chars

**Raisons** : 2× '= signature' · 7× ' = ' · len 4144 chars
  - _Exemples '= signature': Marie Tjibaou assassiné 1989 = signature culturelle majeure du Pacifique | spécifiquement = signature visuelle avec sa plage de 25_

> Nouvelle-Calédonie (Kanaky en mélanésien), collectivité d'outre-mer française dans le sud-ouest Pacifique à 1500 km à l'est de l'Australie : 270 000 habitants sur 18 575 km² (Grande Terre 16 372 km² p...

### 5. 🔴 `chongqing` — score 5, 3834 chars

**Raisons** : 2× '= signature' · 12× ' = ' · len 3834 chars
  - _Exemples '= signature': illuminé la nuit en or = signature visuelle cyberpunk de Chongqing | Chongqing hot pot = signature culinaire_

> Chongqing, plus grande municipalité de Chine au cœur du sud-ouest sur le fleuve Yangtsé : 32 millions d'habitants en aire métropolitaine + statut de municipalité directe (équivalent Pékin-Shanghai-Tia...

### 6. 🔴 `qingdao` — score 5, 3783 chars

**Raisons** : 2× '= signature' · 9× ' = ' · len 3783 chars
  - _Exemples '= signature': international = signature de Qingdao | dégustation = signature touristique de Qingdao_

> Qingdao, ville côtière du Shandong sur la mer Jaune en Chine : 9,5 millions d'habitants. Ancienne concession allemande 1898-1914 qui a légué une architecture coloniale unique en Chine + la brasserie T...

### 7. 🟡 `majuro` — score 4, 3974 chars

**Raisons** : 1× anglicisme suspect · 8× ' = ' · len 3974 chars
  - _Anglicismes: "Island Hopper"_

> Majuro, capitale des Iles Marshall (République des Iles Marshall) dans l'océan Pacifique central : 28 000 habitants sur un atoll-bande de sable de 64 km de long et seulement 200m de large maximum. Pay...

### 8. 🟡 `grenadines` — score 4, 3707 chars

**Raisons** : 6× ' = ' · 5× énum >4 items · len 3707 chars

> Grenadines (Saint-Vincent-et-les-Grenadines), micro-état caribéen au sud des Petites Antilles : 110 000 habitants sur 32 îles dont 9 habitées. Le pays est constitué de l'île principale Saint-Vincent +...

### 9. 🟡 `palikir` — score 4, 3655 chars

**Raisons** : 1× anglicisme suspect · 5× ' = ' · len 3655 chars
  - _Anglicismes: "Island Hopper"_

> Palikir, capitale des États fédérés de Micronésie (Federated States of Micronesia, FSM) sur l'île de Pohnpei dans le Pacifique central : 7000 habitants. Pays archipélagique de 607 îles dispersées sur

### 10. 🟡 `accra` — score 4, 3573 chars

**Raisons** : 1× anglicisme suspect · 5× ' = ' · len 3573 chars
  - _Anglicismes: "Black Star Square"_

> Accra, capitale du Ghana sur la côte du golfe de Guinée : 2,5 millions d'habitants en intra-muros, 4 millions en aire urbaine. Le Ghana = première colonie britannique d'Afrique sub-saharienne à obteni...

### 11. 🟡 `georgie` — score 4, 2648 chars

**Raisons** : 2× '= signature' · 4× ' = '
  - _Exemples '= signature': perchée à 2170m sur une colline = signature visuelle de la Géorgie | XIIe siècle = signature culturelle géorgienne_

> Géorgie (Sakartvelo), pays du Caucase du Sud entre Russie, Turquie, Arménie, Azerbaïdjan : 3,7 millions d'habitants. Pays au croisement Europe-Asie, alphabet géorgien unique, langue isolée non-indo-eu...

### 12. 🟢 `san-salvador` — score 3, 4969 chars

**Raisons** : 11× ' = ' · len 4969 chars

> San Salvador, capitale du Salvador (El Salvador) en Amérique centrale : 525 000 habitants en intra-muros, 2,4 millions en aire urbaine = 40% de la population salvadorienne totale. Plus petit pays cont...

### 13. 🟢 `entebbe` — score 3, 4758 chars

**Raisons** : 10× ' = ' · len 4758 chars

> Entebbe, ville côtière du Lac Victoria en Ouganda à 35 km au sud de la capitale Kampala : 70 000 habitants. Capitale historique du protectorat britannique d'Ouganda 1894-1962, conservée comme capitale...

### 14. 🟢 `granada-nicaragua` — score 3, 4606 chars

**Raisons** : 11× ' = ' · len 4606 chars

> Granada, ville coloniale du Nicaragua sur les rives du Lac Nicaragua = la "perle coloniale" du pays : 130 000 habitants. L'une des plus vieilles villes coloniales espagnoles d'Amérique fondée en 1524

### 15. 🟢 `dili` — score 3, 4333 chars

**Raisons** : 12× ' = ' · len 4333 chars

> Dili, capitale du Timor oriental (Timor-Leste) sur la côte nord de l'île de Timor en Asie du Sud-Est : 280 000 habitants. Plus jeune pays d'Asie = indépendance le 20 mai 2002 après 24 ans d'occupation...

### 16. 🟢 `are` — score 3, 4319 chars

**Raisons** : 5× ' = ' · len 4319 chars

> Åre, principale station de ski de la Suède dans la province de Jämtland en Scandinavie centrale : 1400 habitants permanents (15 000 en saison touristique). Plus grande station de ski des pays nordique...

### 17. 🟢 `papouasie` — score 3, 4292 chars

**Raisons** : 9× ' = ' · len 4292 chars

> Papouasie-Nouvelle-Guinée (PNG, "Papua New Guinea"), pays-archipel de la Mélanésie au nord de l'Australie : 11 millions d'habitants sur 462 840 km². Pays unique au monde pour sa diversité ethnoculture...

### 18. 🟢 `oman` — score 3, 4217 chars

**Raisons** : 5× ' = ' · len 4217 chars

> Oman (Sultanat d'Oman), pays de la péninsule arabique à l'extrême sud-est : 5 millions d'habitants sur 309 500 km². L'un des pays arabes les plus stables et préservés = monarchie sultanique sous le su...

### 19. 🟢 `levi` — score 3, 4209 chars

**Raisons** : 6× ' = ' · len 4209 chars

> Levi, principale station de ski de la Laponie finlandaise à 250 km au nord du cercle polaire arctique : 1100 habitants permanents (10 000 en saison touristique). Plus grande station de ski de Finlande...

### 20. 🟢 `svalbard` — score 3, 4189 chars

**Raisons** : 4× ' = ' · len 4189 chars

> Svalbard (Spitzberg), archipel arctique norvégien à mi-chemin entre Norvège continentale et pôle Nord : 2900 habitants sur 61 022 km². Territoire norvégien le plus septentrional habité au monde = capi...

### 21. 🟢 `bujumbura` — score 3, 4171 chars

**Raisons** : 6× ' = ' · len 4171 chars

> Bujumbura, capitale économique du Burundi en Afrique des Grands Lacs sur les rives du lac Tanganyika : 600 000 habitants. Capitale officielle administrative depuis 2018 = Gitega (à 100 km dans l'intér...

### 22. 🟢 `funafuti` — score 3, 4145 chars

**Raisons** : 6× ' = ' · len 4145 chars

> Funafuti, capitale des Tuvalu dans le Pacifique central : 6300 habitants sur l'atoll principal des Tuvalu (île principale + 5 motus de 26 km² total). Tuvalu = 4e plus petit pays du monde par superfici...

### 23. 🟢 `guatemala` — score 3, 4124 chars

**Raisons** : 12× ' = ' · len 4124 chars

> Guatemala, pays d'Amérique centrale entre Mexique et Honduras-Salvador : 17,6 millions d'habitants. Le pays le plus peuplé d'Amérique centrale, le berceau de la civilisation maya classique (Tikal IIe-...

### 24. 🟢 `panama` — score 3, 4116 chars

**Raisons** : 8× ' = ' · len 4116 chars

> Panama, pays d'Amérique centrale entre Costa Rica et Colombie reliant Amérique du Nord et Amérique du Sud : 4,4 millions d'habitants. Capitale Panama City. Pays unique au monde grâce au canal de Panam...

### 25. 🟢 `riviera-maya` — score 3, 4105 chars

**Raisons** : 4× ' = ' · len 4105 chars

> Riviera Maya, côte caraïbe du Mexique dans l'État de Quintana Roo au sud-est du pays : 130 km de côte de Cancún à Tulum, 1,5 million d'habitants. Capitale touristique du Mexique avec plus de 13 millio...

### 26. 🟢 `harbin` — score 3, 4084 chars

**Raisons** : 8× ' = ' · len 4084 chars

> Harbin, capitale de la province du Heilongjiang à l'extrême nord-est de la Chine près de la frontière russe : 5,5 millions d'habitants. "Moscou de l'Orient" = ancienne ville russe construite par l'Emp...

### 27. 🟢 `nantes` — score 3, 4084 chars

**Raisons** : 9× ' = ' · len 4084 chars

> Nantes, capitale historique du duché de Bretagne sur la Loire en France : 320 000 habitants en intra-muros, 670 000 en aire urbaine. Ancienne capitale bretonne (1532 réunion à la France), aujourd'hui

### 28. 🟢 `kinshasa` — score 3, 4084 chars

**Raisons** : 10× ' = ' · len 4084 chars

> Kinshasa, capitale de la République Démocratique du Congo (RDC, "Congo-Kinshasa") sur le fleuve Congo : 17 millions d'habitants en aire urbaine = 2e plus grande mégapole d'Afrique sub-saharienne après...

### 29. 🟢 `alentejo` — score 3, 4080 chars

**Raisons** : 5× ' = ' · len 4080 chars

> Alentejo, région du sud du Portugal entre le Tage au nord et l'Algarve au sud : 700 000 habitants sur 31 600 km² (1/3 du territoire portugais mais 7% de la population, l'une des régions européennes le...

### 30. 🟢 `trinite-et-tobago` — score 3, 4061 chars

**Raisons** : 10× ' = ' · len 4061 chars

> Trinité-et-Tobago, micro-état des Petites Antilles au sud des Caraïbes à 11 km au large du Venezuela : 1,4 million d'habitants sur 2 îles principales (Trinité 4768 km² + Tobago 300 km²). Indépendant d...

### 31. 🟢 `san-cristobal` — score 3, 4052 chars

**Raisons** : 4× ' = ' · len 4052 chars

> San Cristóbal de las Casas, ville coloniale du Chiapas au sud du Mexique dans les hautes terres mayas : 220 000 habitants à 2200m d'altitude. Capitale culturelle des peuples autochtones mayas tzotzil

### 32. 🟢 `saint-pierre-et-miquelon` — score 3, 4030 chars

**Raisons** : 5× ' = ' · len 4030 chars

> Saint-Pierre-et-Miquelon, collectivité d'outre-mer française dans l'Atlantique nord au large de Terre-Neuve canadienne : 6000 habitants sur 242 km² répartis sur 8 îles dont 2 principales habitées (Sai...

### 33. 🟢 `belize` — score 3, 4027 chars

**Raisons** : 6× ' = ' · len 4027 chars

> Belize (anciennement Honduras britannique), petit pays anglophone d'Amérique centrale entre Mexique et Guatemala sur la côte caraïbe : 410 000 habitants. Seul pays anglophone d'Amérique centrale (héri...

### 34. 🟢 `maseru` — score 3, 3913 chars

**Raisons** : 8× ' = ' · len 3913 chars

> Maseru, capitale du Lesotho en Afrique australe : 330 000 habitants à 1600m d'altitude sur la rivière Caledon frontalière avec Afrique du Sud. Seul pays au monde entièrement situé au-dessus de 1000m d...

### 35. 🟢 `ipoh` — score 3, 3903 chars

**Raisons** : 4× ' = ' · len 3903 chars

> Ipoh, capitale de l'État de Perak au nord-ouest de la Malaisie péninsulaire : 660 000 habitants en aire urbaine, 3e plus grande ville malaisienne après Kuala Lumpur et George Town Penang. Ancien centr...

### 36. 🟢 `salalah` — score 3, 3900 chars

**Raisons** : 7× ' = ' · len 3900 chars

> Salalah, 2e ville du Sultanat d'Oman dans la province du Dhofar à l'extrême sud, à 1000 km au sud de Muscat près de la frontière yéménite : 200 000 habitants. Climat unique au Moyen-Orient grâce au Kh...

### 37. 🟢 `monteverde` — score 3, 3891 chars

**Raisons** : 4× ' = ' · len 3891 chars

> Monteverde (Cloud Forest Reserve), réserve naturelle dans le centre du Costa Rica sur la Cordillère de Tilarán : 7000 habitants à 1300-1850m d'altitude. Forêt nuageuse tropicale = écosystème unique où...

### 38. 🟢 `ndjamena` — score 3, 3881 chars

**Raisons** : 7× ' = ' · len 3881 chars

> N'Djamena ("la ville où nous nous sommes reposés" en arabe), capitale du Tchad dans le Sahel central sur le fleuve Chari frontière camerounaise : 1,4 million d'habitants. Pays parmi les plus pauvres e...

### 39. 🟢 `lac-bled` — score 3, 3870 chars

**Raisons** : 4× ' = ' · len 3870 chars

> Lac de Bled, lac glaciaire alpin de Slovénie dans les Alpes Juliennes : 2,1 km², à 500m d'altitude au pied du Triglav (2864m, point culminant de Slovénie). L'image-carte postale signature de la Slovén...

### 40. 🟢 `queenstown-ski` — score 3, 3868 chars

**Raisons** : 6× ' = ' · len 3868 chars

> Queenstown Ski ("Coronet Peak" et "The Remarkables"), domaines skiables près de Queenstown sur l'Île du Sud de Nouvelle-Zélande dans la région d'Otago : pas de population permanente (Queenstown ville-...

### 41. 🟢 `matsuyama` — score 3, 3867 chars

**Raisons** : 9× ' = ' · len 3867 chars

> Matsuyama, capitale de Shikoku (la plus petite des 4 grandes îles du Japon) sur la mer Intérieure de Seto : 510 000 habitants. Plus grande ville de Shikoku, capitale culturelle de l'île 4 fois sur la

### 42. 🟢 `freetown` — score 3, 3857 chars

**Raisons** : 11× ' = ' · len 3857 chars

> Freetown, capitale de la Sierra Leone sur la côte atlantique d'Afrique de l'Ouest : 1,2 million d'habitants. Ville fondée en 1792 comme refuge pour esclaves affranchis rapatriés d'Amérique du Nord et

### 43. 🟢 `basseterre` — score 3, 3818 chars

**Raisons** : 4× ' = ' · len 3818 chars

> Basseterre, capitale de Saint-Christophe-et-Niévès (Saint Kitts and Nevis) dans les Petites Antilles : 13 000 habitants. Plus petit pays indépendant des Amériques = 261 km², 53 000 habitants au total,...

### 44. 🟢 `tarawa` — score 3, 3817 chars

**Raisons** : 4× ' = ' · len 3817 chars

> Tarawa, capitale des Kiribati sur l'atoll de Tarawa Sud dans le Pacifique central : 65 000 habitants. Pays archipélagique micro-état de 33 atolls dispersés sur 3,5 millions de km² d'océan ("plus grand...

### 45. 🟢 `kumasi` — score 3, 3815 chars

**Raisons** : 7× ' = ' · len 3815 chars

> Kumasi, 2e ville du Ghana et capitale culturelle de la région Ashanti : 2,5 millions d'habitants en aire urbaine. Capitale historique du Royaume Ashanti / Asante 1670-1957 = l'un des plus puissants ro...

### 46. 🟢 `pantelleria` — score 3, 3794 chars

**Raisons** : 4× ' = ' · len 3794 chars

> Pantelleria, île volcanique italienne entre Sicile et Tunisie : 7700 habitants sur 83 km², plus proche de la Tunisie (60 km) que de la Sicile (110 km), considérée comme l'île la plus secrète d'Italie....

### 47. 🟢 `honiara` — score 3, 3793 chars

**Raisons** : 11× ' = ' · len 3793 chars

> Honiara, capitale des Iles Salomon (Solomon Islands) sur l'île de Guadalcanal dans le Pacifique sud-ouest : 85 000 habitants. Pays archipelagique mélanésien de 992 îles, 700 000 habitants au total, in...

### 48. 🟢 `banjul` — score 3, 3786 chars

**Raisons** : 6× ' = ' · len 3786 chars

> Banjul, capitale de la Gambie sur la côte atlantique d'Afrique de l'Ouest : 31 000 habitants en intra-muros, 400 000 en aire urbaine avec Serekunda. Plus petit pays d'Afrique continentale = 11 300 km²...

### 49. 🟢 `bandar-seri-begawan` — score 3, 3779 chars

**Raisons** : 7× ' = ' · len 3779 chars

> Bandar Seri Begawan ("BSB"), capitale de Brunéi (Brunei Darussalam) sur l'île de Bornéo : 100 000 habitants en intra-muros, 280 000 en aire urbaine. Sultanat absolu dirigé par le Sultan Hassanal Bolki...

### 50. 🟢 `san-juan` — score 3, 3762 chars

**Raisons** : 4× ' = ' · len 3762 chars

> San Juan, capitale de Porto Rico (Puerto Rico) sur la côte nord-est : 320 000 habitants en intra-muros, 2,3 millions en aire urbaine. Porto Rico = territoire non incorporé des États-Unis depuis 1898 (...

### 51. 🟢 `dacca` — score 3, 3761 chars

**Raisons** : 6× ' = ' · len 3761 chars

> Dacca (Dhaka), capitale du Bangladesh sur le delta du Gange-Brahmapoutre : 10 millions d'habitants en intra-muros, 22 millions en aire urbaine = l'une des mégapoles les plus densément peuplées au mond...

### 52. 🟢 `douala` — score 3, 3755 chars

**Raisons** : 4× ' = ' · len 3755 chars

> Douala, capitale économique du Cameroun sur le golfe de Guinée à l'embouchure du fleuve Wouri : 3 millions d'habitants en aire urbaine. Capitale politique = Yaoundé (à 250 km dans l'intérieur, plus ha...

### 53. 🟢 `djibouti` — score 3, 3754 chars

**Raisons** : 9× ' = ' · len 3754 chars

> Djibouti (Djibouti-ville), capitale du Djibouti sur le golfe d'Aden à l'entrée stratégique de la mer Rouge : 600 000 habitants. Pays-stratégique au cœur de la Corne de l'Afrique = passage obligé de 30...

### 54. 🟢 `lilongwe` — score 3, 3750 chars

**Raisons** : 5× ' = ' · len 3750 chars

> Lilongwe, capitale du Malawi en Afrique australe : 990 000 habitants. Capitale planifiée construite ex-nihilo dans les années 1970 (capitale précédente = Zomba et Blantyre demeure capitale économique)...

### 55. 🟢 `cotonou` — score 3, 3726 chars

**Raisons** : 8× ' = ' · len 3726 chars

> Cotonou, capitale économique du Bénin sur la côte atlantique du golfe de Guinée : 800 000 habitants en intra-muros, 2,4 millions en aire urbaine. Capitale officielle = Porto-Novo (à 30 km à l'est) mai...

### 56. 🟢 `gudauri` — score 3, 3725 chars

**Raisons** : 5× ' = ' · len 3725 chars

> Gudauri, principale station de ski de Géorgie sur la Voie Militaire de Géorgie à 120 km au nord de Tbilissi : 1500 habitants à 2200m d'altitude au pied du massif du Grand Caucase. Station développée à...

### 57. 🟢 `isla-holbox` — score 3, 3709 chars

**Raisons** : 4× ' = ' · len 3709 chars

> Isla Holbox, petite île au nord du Yucatán au Mexique dans la Réserve de la Biosphère Yum Balam : 2000 habitants permanents sur 41 km de long et 2 km de large, île de sable où aucune voiture n'est aut...

### 58. 🟢 `tripoli` — score 3, 3686 chars

**Raisons** : 6× ' = ' · len 3686 chars

> Tripoli (Tarabulus), capitale de la Libye sur la côte méditerranéenne : 1,2 million d'habitants. Fondée par les Phéniciens VIIe siècle av JC sous le nom Oea, l'une des trois villes "Tripolis" ("3 vill...

### 59. 🟢 `nicaragua` — score 3, 3670 chars

**Raisons** : 6× ' = ' · len 3670 chars

> Nicaragua, pays d'Amérique centrale entre Honduras et Costa Rica : 6,7 millions d'habitants. Capitale Managua. Pays marqué par la révolution sandiniste 1979 (chute de la dictature Somoza) puis guerre

### 60. 🟢 `sao-tome` — score 3, 3668 chars

**Raisons** : 6× ' = ' · len 3668 chars

> Sao Tomé-et-Principe, micro-état insulaire dans le golfe de Guinée au large de l'Afrique équatoriale : 220 000 habitants sur 2 îles principales (Sao Tomé 854 km², Principe 142 km²) sur l'équateur géog...

### 61. 🟢 `luanda` — score 3, 3667 chars

**Raisons** : 5× ' = ' · len 3667 chars

> Luanda, capitale de l'Angola sur la côte atlantique de l'Afrique australe : 8 millions d'habitants en aire urbaine. Ancienne colonie portugaise (1575-1975), indépendance par guerre coloniale puis guer...

### 62. 🟢 `kaohsiung` — score 3, 3634 chars

**Raisons** : 5× ' = ' · len 3634 chars

> Kaohsiung, 2e ville de Taïwan sur la côte sud-ouest : 2,8 millions d'habitants (3e en aire urbaine après Taipei + New Taipei). Principal port de Taïwan = 4e plus grand port à conteneurs au monde, capi...

### 63. 🟢 `costa-rica` — score 3, 3621 chars

**Raisons** : 6× ' = ' · len 3621 chars

> Costa Rica, pays d'Amérique centrale entre Nicaragua et Panama : 5 millions d'habitants. "Pura Vida" = devise nationale qui résume la philosophie costaricaine. Pays unique au monde : aucune armée depu...

### 64. 🟢 `luzon` — score 3, 3621 chars

**Raisons** : 8× ' = ' · len 3621 chars

> Luzon, plus grande île des Philippines et la 17e plus grande île au monde : 50 millions d'habitants sur 109 965 km² = 50% de la population philippine totale. Île principale abritant la capitale Manill...

### 65. 🟢 `al-ula` — score 3, 3613 chars

**Raisons** : 5× ' = ' · len 3613 chars

> Al-Ula (AlUla), oasis archéologique du nord-ouest de l'Arabie Saoudite dans le désert du Hijaz : 5000 habitants. Joyau touristique nouvellement ouvert de l'Arabie Saoudite depuis 2019 dans le cadre de...

### 66. 🟢 `philippines` — score 3, 3608 chars

**Raisons** : 13× ' = ' · len 3608 chars

> Philippines (Pilipinas), pays archipélagique du sud-est asiatique : 113 millions d'habitants sur 7641 îles. 3e pays anglophone au monde par nombre de locuteurs (héritage colonial américain 1898-1946),...

### 67. 🟢 `malabo` — score 3, 3605 chars

**Raisons** : 5× ' = ' · len 3605 chars

> Malabo, capitale de la Guinée Équatoriale sur l'île de Bioko dans le golfe de Guinée : 250 000 habitants. Particularité géographique unique au monde = la capitale est sur une île (Bioko) à 250 km du c...

### 68. 🟢 `lome` — score 3, 3602 chars

**Raisons** : 6× ' = ' · len 3602 chars

> Lomé, capitale du Togo sur la côte atlantique du golfe de Guinée : 840 000 habitants en intra-muros, 2 millions en aire urbaine. Le Togo = ancienne colonie allemande (1884-1914 = "Togoland" = colonie

### 69. 🟢 `libreville` — score 3, 3587 chars

**Raisons** : 6× ' = ' · len 3587 chars

> Libreville, capitale du Gabon sur la côte atlantique de l'Afrique centrale : 800 000 habitants en aire urbaine = 50% de la population gabonaise totale. Ancienne colonie française "Gabon" 1885-1960 (le...

### 70. 🟢 `baqueira-beret` — score 3, 3580 chars

**Raisons** : 5× ' = ' · len 3580 chars

> Baqueira Beret, plus grande station de ski d'Espagne et des Pyrénées espagnoles dans la Vallée d'Aran en Catalogne : 30 habitants permanents (10 000 en saison ski). Station favorite de la famille roya...

### 71. 🟢 `bagdad` — score 3, 3578 chars

**Raisons** : 6× ' = ' · len 3578 chars

> Bagdad, capitale de l'Irak sur le fleuve Tigre : 7 millions d'habitants. Ancienne capitale du Califat abbasside 762-1258 = l'une des plus grandes villes du monde médiéval avec 1,2 million d'habitants

### 72. 🟢 `khartoum` — score 3, 3541 chars

**Raisons** : 7× ' = ' · len 3541 chars

> Khartoum (Al-Khartoum), capitale du Soudan au confluent du Nil Blanc et du Nil Bleu formant le Nil qui s'écoule ensuite vers l'Egypte : 5,3 millions d'habitants en aire métropolitaine "Triple Capitale...

### 73. 🟢 `monrovia` — score 3, 3516 chars

**Raisons** : 4× ' = ' · len 3516 chars

> Monrovia, capitale du Liberia sur la côte atlantique d'Afrique de l'Ouest : 1,1 million d'habitants. Pays unique en Afrique sub-saharienne = colonie d'anciens esclaves américains affranchis envoyés de...

### 74. 🟢 `myanmar` — score 3, 2891 chars

**Raisons** : 1× anglicisme suspect · 4× ' = '
  - _Anglicismes: "Golden Rock"_

> Myanmar (Birmanie), pays d'Asie du Sud-Est entre Inde, Chine, Bangladesh, Thaïlande : 54 millions d'habitants. Pays mystérieux et fermé pendant des décennies sous junte militaire (1962-2011), brève ou...

### 75. 🟢 `gili` — score 3, 2706 chars

**Raisons** : 1× anglicisme suspect · 7× ' = '
  - _Anglicismes: "Honeymoon Island"_

> Iles Gili, archipel de 3 îles au large de l'île de Lombok en Indonésie (à l'est de Bali) : Gili Trawangan (la plus grande, festive), Gili Air (intermédiaire, atmosphère bohème), Gili Meno (la plus pet...

## Plan de remédiation suggéré

### Phase 1 — Quick wins (priorité 🔴 très haute, score ≥ 5)

6 avis à réécrire en priorité (les plus marqués) :
- [ ] `peloponnese`
- [ ] `jinja`
- [ ] `guyane`
- [ ] `nouvelle-caledonie`
- [ ] `chongqing`
- [ ] `qingdao`

**Stratégie** :
- Pour chacun, lire l'avis FR → identifier voix narrative manquante
- Réécrire en 1500-2500 chars max (vs 3500-4700 actuels)
- Remplacer les énumérations à virgules par phrases articulées
- Bannir les patterns 'X = signature Y', 'X = la Y la plus Z au monde'
- Ajouter voix Gilles : 'mon mois préféré', 'j'aime', 'je conseille'
- Garder les noms de lieux dans la langue locale (`Place des Palmistes` OK)
- Anglicismes : à remplacer par version FR
- Une fois FR validé, propager EN/EN-US/ES/DE

### Phase 2 — Score 4 (🟡)

5 avis intermédiaires. Vérifier visuellement avant décision.

### Phase 3 — Score 3 (🟢)

64 avis faiblement suspects. Audit visuel rapide pour confirmer/écarter.

## Workflow recommandé pour réécriture

```bash
# 1. Lire l'avis actuel
python3 -c "import json; d=json.load(open('data/avis_annuel.json')); print(d['SLUG:fr'])"

# 2. Modifier dans data/avis_annuel.json (FR puis traduire EN/EN-US/ES/DE)
# Validation : pas de '= signature', pas d'anglicisme, présence voix perso, < 2500 chars

# 3. Régénérer les pages affectées
for lang in fr en en-us es de; do
  python3 generate_pages.py --lang $lang --v6 SLUG
done

# 4. Commit + push
git add data/avis_annuel.json *.html en/ us/ es/ de/
git commit -m "Avis SLUG: réécriture (audit AUDIT_AVIS_FR_2026-05)"
git push origin main
```

## Fichiers liés

- Source : `data/avis_annuel.json`
- Backup déjà existant : `data/avis_annuel.json.backup_20260511_205615`
- Script d'audit : `/tmp/audit_avis_fr.py` (à conserver pour relancer)
