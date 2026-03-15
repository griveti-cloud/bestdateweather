#!/usr/bin/env python3
"""Met à jour les hero_sub des 40 stations ski avec contenu spécifique."""
import csv

HERO_SUBS = {
    "courchevel": {
        "fr": "Courchevel, joyau des Trois Vallées — 600 km de pistes, prestige et ski glaciaire au-dessus de 2 700 m.",
        "en": "Courchevel, jewel of the Trois Vallées — 600 km of slopes, prestige skiing and glaciers above 2,700 m.",
        "es": "Courchevel, joya de los Tres Valles — 600 km de pistas, esquí de prestigio y glaciares a más de 2 700 m.",
        "de": "Courchevel, Juwel der Trois Vallées — 600 km Pisten, Prestigeski und Gletscher über 2 700 m.",
    },
    "meribel": {
        "fr": "Méribel, cœur des Trois Vallées — chalets en bois, neige fiable et accès direct à 600 km de pistes.",
        "en": "Méribel, heart of the Trois Vallées — timber chalets, reliable snow and direct access to 600 km of runs.",
        "es": "Méribel, corazón de los Tres Valles — chalets de madera, nieve fiable y acceso directo a 600 km de pistas.",
        "de": "Méribel, Herz der Trois Vallées — Holzchalets, zuverlässiger Schnee und direkter Zugang zu 600 km Pisten.",
    },
    "tignes": {
        "fr": "Tignes, domaine skiable à 3 456 m — glacier Grande Motte, ski été-hiver et snowpark de référence.",
        "en": "Tignes, ski domain at 3,456 m — Grande Motte glacier, year-round skiing and world-class snowpark.",
        "es": "Tignes, dominio esquiable a 3 456 m — glaciar Grande Motte, esquí todo el año y snowpark de referencia.",
        "de": "Tignes, Skigebiet auf 3 456 m — Grande-Motte-Gletscher, ganzjähriges Skifahren und Top-Snowpark.",
    },
    "alpe-dhuez": {
        "fr": "Alpe d'Huez, 300 jours de soleil par an — 250 km de pistes et la mythique descente de la Sarenne.",
        "en": "Alpe d'Huez, 300 sunny days a year — 250 km of runs and the legendary Sarenne descent.",
        "es": "Alpe d'Huez, 300 días de sol al año — 250 km de pistas y el mítico descenso de la Sarenne.",
        "de": "Alpe d'Huez, 300 Sonnentage im Jahr — 250 km Pisten und der legendäre Sarenne-Abfahrt.",
    },
    "les-arcs": {
        "fr": "Les Arcs, architecture avant-gardiste des années 70 — Paradiski, 425 km de pistes reliées avec La Plagne.",
        "en": "Les Arcs, avant-garde 1970s architecture — Paradiski, 425 km of runs linked with La Plagne.",
        "es": "Les Arcs, arquitectura vanguardista de los 70 — Paradiski, 425 km de pistas unidas con La Plagne.",
        "de": "Les Arcs, Avantgarde-Architektur der 70er — Paradiski, 425 km Pisten verbunden mit La Plagne.",
    },
    "megeve": {
        "fr": "Megève, station chic du Mont-Blanc — village médiéval, 445 km de pistes et gastronomie étoilée.",
        "en": "Megève, chic Mont Blanc resort — medieval village, 445 km of runs and Michelin-starred restaurants.",
        "es": "Megève, estación chic del Mont Blanc — pueblo medieval, 445 km de pistas y gastronomía con estrellas.",
        "de": "Megève, schickes Mont-Blanc-Resort — mittelalterliches Dorf, 445 km Pisten und Sterne-Gastronomie.",
    },
    "verbier": {
        "fr": "Verbier, freeride capital des Alpes suisses — 4 Vallées, 412 km de pistes et dénivelé de 2 200 m.",
        "en": "Verbier, freeride capital of the Swiss Alps — 4 Vallées, 412 km of runs and 2,200 m vertical drop.",
        "es": "Verbier, capital del freeride en los Alpes suizos — 4 Vallées, 412 km de pistas y 2 200 m de desnivel.",
        "de": "Verbier, Freeride-Hauptstadt der Schweizer Alpen — 4 Vallées, 412 km Pisten und 2 200 m Höhenunterschied.",
    },
    "zermatt": {
        "fr": "Zermatt, au pied du Cervin — ski sans voiture, glacier permanent à 3 883 m et vue iconique sur le Matterhorn.",
        "en": "Zermatt, at the foot of the Matterhorn — car-free village, permanent glacier at 3,883 m and iconic views.",
        "es": "Zermatt, al pie del Cervino — sin coches, glaciar permanente a 3 883 m y vistas icónicas al Matterhorn.",
        "de": "Zermatt, am Fuß des Matterhorns — autofreies Dorf, Ganzjahresgletscher auf 3 883 m und Ikonen-Aussicht.",
    },
    "davos": {
        "fr": "Davos, plus grande station de Suisse — 300 km de pistes, Parsenn légendaire et Forum économique mondial.",
        "en": "Davos, Switzerland's largest resort — 300 km of slopes, legendary Parsenn and World Economic Forum.",
        "es": "Davos, la mayor estación de Suiza — 300 km de pistas, el legendario Parsenn y el Foro Económico Mundial.",
        "de": "Davos, größtes Skigebiet der Schweiz — 300 km Pisten, legendäres Parsenn und Weltwirtschaftsforum.",
    },
    "grindelwald": {
        "fr": "Grindelwald, face nord de l'Eiger — Jungfrau ski region, 213 km de pistes et chemin de fer emblématique.",
        "en": "Grindelwald, beneath the Eiger north face — Jungfrau ski region, 213 km of runs and iconic railway.",
        "es": "Grindelwald, frente a la cara norte del Eiger — región de esquí Jungfrau, 213 km de pistas y tren emblemático.",
        "de": "Grindelwald, unter der Eiger-Nordwand — Jungfrau Skiregion, 213 km Pisten und legendäre Zahnradbahn.",
    },
    "saas-fee": {
        "fr": "Saas-Fee, le village des glaciers — 145 km de pistes, ski été garanti et panorama 4 000 m sans voiture.",
        "en": "Saas-Fee, the glacier village — 145 km of runs, guaranteed summer skiing and car-free 4,000 m panorama.",
        "es": "Saas-Fee, el pueblo de los glaciares — 145 km de pistas, esquí de verano garantizado y sin coches a 4 000 m.",
        "de": "Saas-Fee, das Gletscherdorf — 145 km Pisten, garantiertes Sommerskifahren und autofreies 4 000-m-Panorama.",
    },
    "crans-montana": {
        "fr": "Crans-Montana, soleil des Alpes valaisannes — 140 km de pistes, golf 18 trous et panorama sur les 4 000 m.",
        "en": "Crans-Montana, sun of the Valais Alps — 140 km of runs, 18-hole golf and panorama over the 4,000 m peaks.",
        "es": "Crans-Montana, sol de los Alpes del Valais — 140 km de pistas, golf de 18 hoyos y panorama a los 4 000 m.",
        "de": "Crans-Montana, Sonnenseite der Walliser Alpen — 140 km Pisten, 18-Loch-Golf und Panorama über die 4 000er.",
    },
    "kitzbuhel": {
        "fr": "Kitzbühel, station mythique du Tyrol — descente de Hahnenkamm, 179 km de pistes et vieille ville médiévale.",
        "en": "Kitzbühel, legendary Tyrolean resort — Hahnenkamm downhill, 179 km of runs and medieval old town.",
        "es": "Kitzbühel, estación mítica del Tirol — descenso de Hahnenkamm, 179 km de pistas y casco medieval.",
        "de": "Kitzbühel, legendäres Tiroler Skigebiet — Hahnenkamm-Abfahrt, 179 km Pisten und mittelalterliche Altstadt.",
    },
    "st-anton": {
        "fr": "St-Anton, berceau du ski alpin — Arlberg, 305 km de pistes de compétition et après-ski réputé.",
        "en": "St Anton, birthplace of alpine skiing — Arlberg, 305 km of race runs and world-famous après-ski.",
        "es": "St. Anton, cuna del esquí alpino — Arlberg, 305 km de pistas de competición y après-ski de fama mundial.",
        "de": "St. Anton, Wiege des alpinen Skisports — Arlberg, 305 km Rennpisten und weltberühmtes Après-Ski.",
    },
    "ischgl": {
        "fr": "Ischgl, station la plus animée des Alpes — Silvretta Arena, 238 km de pistes et concerts de fermeture légendaires.",
        "en": "Ischgl, the Alps' most vibrant resort — Silvretta Arena, 238 km of runs and legendary closing concerts.",
        "es": "Ischgl, la estación más animada de los Alpes — Silvretta Arena, 238 km de pistas y legendarios conciertos de cierre.",
        "de": "Ischgl, lebendigstes Skigebiet der Alpen — Silvretta Arena, 238 km Pisten und legendäre Abschlusskonzerte.",
    },
    "saalbach": {
        "fr": "Saalbach-Hinterglemm, Skicircus autrichien — 270 km de pistes en anneau, après-ski animé et neige fiable.",
        "en": "Saalbach-Hinterglemm, Austrian Skicircus — 270 km circuit of runs, lively après-ski and reliable snow.",
        "es": "Saalbach-Hinterglemm, Skicircus austriaco — 270 km de pistas en circuito, animado après-ski y nieve fiable.",
        "de": "Saalbach-Hinterglemm, österreichischer Skicircus — 270 km Rundkurs, lebhaftes Après-Ski und zuverlässiger Schnee.",
    },
    "livigno": {
        "fr": "Livigno, zone franche des Alpes italiennes — 115 km de pistes à 1 800 m, duty-free et snowpark de compétition.",
        "en": "Livigno, Italian Alps duty-free zone — 115 km of runs at 1,800 m, tax-free shopping and competition snowpark.",
        "es": "Livigno, zona franca de los Alpes italianos — 115 km de pistas a 1 800 m, duty-free y snowpark de competición.",
        "de": "Livigno, Freihandelszone der Italienischen Alpen — 115 km Pisten auf 1 800 m, Duty-free und Wettkampf-Snowpark.",
    },
    "cervinia": {
        "fr": "Cervinia, ski transfrontalier sous le Cervin — relié à Zermatt, 360 km de pistes et glacier à 3 883 m.",
        "en": "Cervinia, cross-border skiing under the Matterhorn — linked to Zermatt, 360 km of runs and glacier at 3,883 m.",
        "es": "Cervinia, esquí transfronterizo bajo el Cervino — conectado con Zermatt, 360 km de pistas y glaciar a 3 883 m.",
        "de": "Cervinia, grenzüberschreitendes Skifahren unterm Matterhorn — mit Zermatt verbunden, 360 km Pisten und Gletscher auf 3 883 m.",
    },
    "madonna-di-campiglio": {
        "fr": "Madonna di Campiglio, perle des Dolomites de Brenta — 150 km de pistes, Tre Valli et élégance italienne.",
        "en": "Madonna di Campiglio, pearl of the Brenta Dolomites — 150 km of runs, Tre Valli and Italian elegance.",
        "es": "Madonna di Campiglio, perla de las Dolomitas de Brenta — 150 km de pistas, Tre Valli y elegancia italiana.",
        "de": "Madonna di Campiglio, Perle der Brenta-Dolomiten — 150 km Pisten, Tre Valli und italienische Eleganz.",
    },
    "sestriere": {
        "fr": "Sestrière, fondée par Fiat en 1934 — Via Lattea, 400 km de pistes et site des JO Turin 2006.",
        "en": "Sestriere, founded by Fiat in 1934 — Via Lattea, 400 km of runs and Turin 2006 Olympic venue.",
        "es": "Sestrière, fundada por Fiat en 1934 — Via Lattea, 400 km de pistas y sede de los JJ.OO. Turín 2006.",
        "de": "Sestriere, 1934 von Fiat gegründet — Via Lattea, 400 km Pisten und Olympiaort Turin 2006.",
    },
    "aspen": {
        "fr": "Aspen, capitale du ski américain — quatre domaines distincts, art contemporain et 1 600 m de dénivelé.",
        "en": "Aspen, US ski capital — four distinct mountains, contemporary art scene and 1,600 m vertical drop.",
        "es": "Aspen, capital del esquí americano — cuatro montañas distintas, arte contemporáneo y 1 600 m de desnivel.",
        "de": "Aspen, US-Skihauptstadt — vier eigenständige Berge, zeitgenössische Kunstszene und 1 600 m Höhenunterschied.",
    },
    "vail": {
        "fr": "Vail, plus grande station des États-Unis — Back Bowls légendaires, 5 300 ha skiables et village tyrolien.",
        "en": "Vail, largest ski resort in the US — legendary Back Bowls, 5,300 skiable acres and Tyrolean village.",
        "es": "Vail, la mayor estación de esquí de EE.UU. — legendarios Back Bowls, 5 300 ha esquiables y pueblo tirolés.",
        "de": "Vail, größtes Skigebiet der USA — legendäre Back Bowls, 5 300 ha Skigelände und Tiroler Dorf.",
    },
    "breckenridge": {
        "fr": "Breckenridge, Colorado — cinq pics au-dessus de 3 900 m, ville historique de la ruée vers l'or et 187 pistes.",
        "en": "Breckenridge, Colorado — five peaks above 12,800 ft, gold rush historic town and 187 trails.",
        "es": "Breckenridge, Colorado — cinco cimas por encima de 3 900 m, histórica ciudad de la fiebre del oro y 187 pistas.",
        "de": "Breckenridge, Colorado — fünf Gipfel über 3 900 m, historische Goldgräberstadt und 187 Pisten.",
    },
    "park-city": {
        "fr": "Park City, Utah — Greatest Snow on Earth, 330 pistes reliées et siège de l'Institut Sundance.",
        "en": "Park City, Utah — Greatest Snow on Earth, 330 linked trails and home of the Sundance Institute.",
        "es": "Park City, Utah — la mejor nieve del mundo, 330 pistas unidas y sede del Instituto Sundance.",
        "de": "Park City, Utah — Greatest Snow on Earth, 330 verbundene Pisten und Heimat des Sundance Institute.",
    },
    "telluride": {
        "fr": "Telluride, Colorado — box canyon isolé, neige poudreuse légendaire, 2 000 m de dénivelé et festival de jazz.",
        "en": "Telluride, Colorado — isolated box canyon, legendary powder snow, 2,000 m vertical and jazz festival.",
        "es": "Telluride, Colorado — cañón aislado, legendaria nieve polvo, 2 000 m de desnivel y festival de jazz.",
        "de": "Telluride, Colorado — abgelegenes Box-Canyon, legendärer Pulverschnee, 2 000 m Höhenunterschied und Jazzfestival.",
    },
    "steamboat-springs": {
        "fr": "Steamboat Springs, Colorado — neige Champagne Powder® certifiée, 165 pistes et 1 000 km de sentiers nordiques.",
        "en": "Steamboat Springs, Colorado — certified Champagne Powder® snow, 165 trails and 1,000 km of Nordic terrain.",
        "es": "Steamboat Springs, Colorado — nieve Champagne Powder® certificada, 165 pistas y 1 000 km de esquí nórdico.",
        "de": "Steamboat Springs, Colorado — zertifizierter Champagne Powder®-Schnee, 165 Pisten und 1 000 km Langlaufgelände.",
    },
    "whistler": {
        "fr": "Whistler, plus grand domaine skiable d'Amérique du Nord — deux sommets, 200 pistes et village piétonnier vibrant.",
        "en": "Whistler, largest ski resort in North America — two peaks, 200 runs and vibrant pedestrian village.",
        "es": "Whistler, la mayor estación de esquí de América del Norte — dos cimas, 200 pistas y animado pueblo peatonal.",
        "de": "Whistler, größtes Skigebiet Nordamerikas — zwei Gipfel, 200 Pisten und lebendiges Fußgängerdorf.",
    },
    "banff": {
        "fr": "Banff, ski dans les Rocheuses canadiennes — trois domaines UNESCO, sources chaudes et faune sauvage spectaculaire.",
        "en": "Banff, skiing in the Canadian Rockies — three UNESCO domains, hot springs and spectacular wildlife.",
        "es": "Banff, esquí en las Montañas Rocosas canadienses — tres dominios UNESCO, aguas termales y fauna espectacular.",
        "de": "Banff, Skifahren in den Kanadischen Rockies — drei UNESCO-Gebiete, Thermalquellen und spektakuläre Tierwelt.",
    },
    "mont-tremblant": {
        "fr": "Mont-Tremblant, Alpes québécoises — 102 pistes, village piétonnier laurentien et neige naturelle abondante.",
        "en": "Mont-Tremblant, Quebec Alps — 102 runs, Laurentian pedestrian village and abundant natural snowfall.",
        "es": "Mont-Tremblant, los Alpes de Quebec — 102 pistas, pueblo peatonal laurentino y abundante nieve natural.",
        "de": "Mont-Tremblant, Québecer Alpen — 102 Pisten, laurentianisches Fußgängerdorf und reichlich Naturschnee.",
    },
    "hakuba": {
        "fr": "Hakuba, vallée des Alpes japonaises — onze stations, neige JO Nagano 1998 et ryokans traditionnels.",
        "en": "Hakuba, Japanese Alps valley — eleven resorts, Nagano 1998 Olympic snow and traditional ryokans.",
        "es": "Hakuba, valle de los Alpes japoneses — once estaciones, nieve de los JO Nagano 1998 y ryokans tradicionales.",
        "de": "Hakuba, Tal der Japanischen Alpen — elf Resorts, Olympia-Schnee Nagano 1998 und traditionelle Ryokans.",
    },
    "nozawa-onsen": {
        "fr": "Nozawa Onsen, village thermal des Alpes japonaises — 13 sources publiques gratuites, poudreuse légendaire et festival du feu.",
        "en": "Nozawa Onsen, hot spring village in the Japanese Alps — 13 free public baths, legendary powder and fire festival.",
        "es": "Nozawa Onsen, pueblo termal de los Alpes japoneses — 13 baños públicos gratuitos, polvillo legendario y festival del fuego.",
        "de": "Nozawa Onsen, Thermaldorf in den Japanischen Alpen — 13 kostenlose öffentliche Bäder, legendärer Pulverschnee und Feuerfest.",
    },
    "are": {
        "fr": "Åre, première station scandinave — 100 pistes, ski sous les aurores boréales et Coupe du Monde 2019.",
        "en": "Åre, Scandinavia's premier resort — 100 runs, skiing under the northern lights and 2019 World Cup.",
        "es": "Åre, la primera estación escandinava — 100 pistas, esquí bajo las auroras boreales y Copa del Mundo 2019.",
        "de": "Åre, führendes skandinavisches Skigebiet — 100 Pisten, Skifahren unterm Nordlicht und Weltcup 2019.",
    },
    "hemsedal": {
        "fr": "Hemsedal, Alpes scandinaves de Norvège — 52 pistes à 1 450 m, neige fiable et ambiance village authentique.",
        "en": "Hemsedal, Norway's Scandinavian Alps — 52 runs at 1,450 m, reliable snow and authentic village atmosphere.",
        "es": "Hemsedal, los Alpes escandinavos de Noruega — 52 pistas a 1 450 m, nieve fiable y auténtico ambiente de pueblo.",
        "de": "Hemsedal, Skandinavische Alpen Norwegens — 52 Pisten auf 1 450 m, zuverlässiger Schnee und authentische Dorfatmosphäre.",
    },
    "levi": {
        "fr": "Lévi, station arctique de Finlande — ski sous les aurores boréales, safaris en renne et 43 pistes illuminées.",
        "en": "Levi, Arctic ski resort in Finland — skiing under the northern lights, reindeer safaris and 43 lit runs.",
        "es": "Lévi, estación ártica de Finlandia — esquí bajo las auroras boreales, safaris en reno y 43 pistas iluminadas.",
        "de": "Levi, arktisches Skigebiet in Finnland — Skifahren unterm Nordlicht, Rentier-Safaris und 43 beleuchtete Pisten.",
    },
    "geilo": {
        "fr": "Geilo, station historique de Norvège — entre Oslo et Bergen, 35 pistes et ski de fond sur 220 km de tracés.",
        "en": "Geilo, Norway's historic resort — between Oslo and Bergen, 35 runs and 220 km of cross-country trails.",
        "es": "Geilo, estación histórica de Noruega — entre Oslo y Bergen, 35 pistas y 220 km de esquí de fondo.",
        "de": "Geilo, Norwegens historisches Skigebiet — zwischen Oslo und Bergen, 35 Pisten und 220 km Langlaufloipen.",
    },
    "gudauri": {
        "fr": "Gudauri, station d'altitude du Caucase géorgien — 2 200 m en bas de piste, heli-ski sauvage et culture khinkali.",
        "en": "Gudauri, high-altitude Caucasus resort in Georgia — 2,200 m base, wild heli-skiing and khinkali culture.",
        "es": "Gudauri, estación de altitud en el Cáucaso georgiano — 2 200 m de cota baja, heli-ski salvaje y cultura khinkali.",
        "de": "Gudauri, Hochgebirgsresort im georgischen Kaukasus — 2 200 m Talboden, wildes Heli-Ski und Khinkali-Kultur.",
    },
    "krasnaya-polyana": {
        "fr": "Krasnaya Polyana, domaines ski des JO Sotchi 2014 — Rosa Khutor, 102 pistes et mer Noire à 40 km.",
        "en": "Krasnaya Polyana, Sochi 2014 Olympic ski venues — Rosa Khutor, 102 runs and the Black Sea 40 km away.",
        "es": "Krasnaya Polyana, estaciones esquí de los JO Sochi 2014 — Rosa Khutor, 102 pistas y el mar Negro a 40 km.",
        "de": "Krasnaya Polyana, Olympia-Skigebiete Sotschi 2014 — Rosa Khutor, 102 Pisten und Schwarzes Meer 40 km entfernt.",
    },
    "baqueira-beret": {
        "fr": "Baqueira-Beret, meilleure station d'Espagne — Val d'Aran pyrénéen, 105 pistes et refuge de la famille royale.",
        "en": "Baqueira-Beret, Spain's premier ski resort — Pyrenean Val d'Aran, 105 runs and royal family retreat.",
        "es": "Baqueira-Beret, la mejor estación de España — Val d'Arán pirenaico, 105 pistas y refugio de la familia real.",
        "de": "Baqueira-Beret, Spaniens bestes Skigebiet — Pyrenäisches Val d'Aran, 105 Pisten und Refugium der Königsfamilie.",
    },
    "yongpyong": {
        "fr": "Yongpyong, plus ancienne station de Corée — 31 pistes JO Pyeongchang 2018, ski de nuit et K-drama emblématique.",
        "en": "Yongpyong, South Korea's oldest resort — 31 Pyeongchang 2018 Olympic runs, night skiing and iconic K-drama setting.",
        "es": "Yongpyong, la estación más antigua de Corea — 31 pistas de los JO Pyeongchang 2018, esquí nocturno y k-drama icónico.",
        "de": "Yongpyong, ältestes Resort Südkoreas — 31 Olympia-Pisten Pyeongchang 2018, Nachtskifahren und ikonisches K-Drama-Setting.",
    },
    "grandvalira": {
        "fr": "Grandvalira, plus grand domaine skiable d'Andorre — 210 km de pistes duty-free entre France et Espagne.",
        "en": "Grandvalira, Andorra's largest ski domain — 210 km of duty-free runs between France and Spain.",
        "es": "Grandvalira, el mayor dominio esquiable de Andorra — 210 km de pistas duty-free entre Francia y España.",
        "de": "Grandvalira, größtes Skigebiet Andorras — 210 km zollfreie Pisten zwischen Frankreich und Spanien.",
    },
}


def main():
    with open('data/destinations.csv', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)

    updated = 0
    for row in rows:
        slug = row['slug_fr']
        if slug in HERO_SUBS:
            subs = HERO_SUBS[slug]
            row['hero_sub_fr'] = subs['fr']
            row['hero_sub_en'] = subs['en']
            row['hero_sub_es'] = subs['es']
            row['hero_sub_de'] = subs['de']
            updated += 1
            print(f"✓ {slug:30} FR: {subs['fr'][:65]}")

    with open('data/destinations.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator='\r\n')
        writer.writeheader()
        writer.writerows(rows)

    print(f"\n✅ {updated} destinations mises à jour dans destinations.csv")


if __name__ == '__main__':
    main()
