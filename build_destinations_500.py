#!/usr/bin/env python3
"""
build_destinations_500.py — BestDateWeather
=============================================
Génère la liste des ~420 nouvelles destinations à ajouter à destinations.csv.
Valide les coordonnées via Open-Meteo Geocoding API.

Usage :
  python3 build_destinations_500.py --preview        # affiche la liste
  python3 build_destinations_500.py --validate       # vérifie coords via API
  python3 build_destinations_500.py --write           # ajoute à destinations.csv

Priorités :
  P1 : Volume de recherche élevé FR+EN, destinations incontournables (~120)
  P2 : Volume moyen, couverture géographique importante (~150)
  P3 : Couverture complète, long-tail SEO (~150)
"""

import csv, json, os, sys, time, urllib.request

DIR  = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(DIR, 'data')

# ── MASTER LIST ──────────────────────────────────────────────────────────────
# Format: (slug_fr, slug_en, nom_fr, nom_bare, pays, flag, prep, lat, lon,
#           tropical, nom_en, country_en, priority)
#
# prep: à (cities), en (fem regions/islands/countries), au (masc countries),
#       aux (plural), sur la (coasts), à la (La Réunion style)
# tropical: True if monsoon correction applies (warm year-round, heavy but short rains)

NEW_DESTINATIONS = [

    # ══════════════════════════════════════════════════════════════════════════
    # EUROPE — Capitales & grandes villes manquantes
    # ══════════════════════════════════════════════════════════════════════════

    # Grèce
    ("athenes", "athens", "Athènes", "Athènes", "Grèce", "gr", "à", 37.98, 23.73, False, "Athens", "Greece", "P1"),
    ("thessalonique", "thessaloniki", "Thessalonique", "Thessalonique", "Grèce", "gr", "à", 40.64, 22.94, False, "Thessaloniki", "Greece", "P2"),
    ("naxos", "naxos", "Naxos", "Naxos", "Grèce", "gr", "à", 37.10, 25.37, False, "Naxos", "Greece", "P2"),
    ("paros", "paros", "Paros", "Paros", "Grèce", "gr", "à", 37.09, 25.15, False, "Paros", "Greece", "P2"),
    ("kefalonia", "kefalonia", "Céphalonie", "Céphalonie", "Grèce", "gr", "à", 38.18, 20.49, False, "Kefalonia", "Greece", "P2"),
    ("lefkada", "lefkada", "Leucade", "Leucade", "Grèce", "gr", "à", 38.71, 20.65, False, "Lefkada", "Greece", "P3"),
    ("kos", "kos", "Kos", "Kos", "Grèce", "gr", "à", 36.89, 27.09, False, "Kos", "Greece", "P3"),
    ("milos", "milos", "Milos", "Milos", "Grèce", "gr", "à", 36.74, 24.43, False, "Milos", "Greece", "P3"),
    ("hydra", "hydra", "Hydra", "Hydra", "Grèce", "gr", "à", 37.35, 23.47, False, "Hydra", "Greece", "P3"),

    # Italie
    ("milan", "milan", "Milan", "Milan", "Italie", "it", "à", 45.46, 9.19, False, "Milan", "Italy", "P1"),
    ("naples", "naples", "Naples", "Naples", "Italie", "it", "à", 40.85, 14.27, False, "Naples", "Italy", "P1"),
    ("lac-come", "lake-como", "le Lac de Côme", "Lac de Côme", "Italie", "it", "au", 45.99, 9.26, False, "Lake Como", "Italy", "P1"),
    ("pouilles", "puglia", "les Pouilles", "Pouilles", "Italie", "it", "dans les", 41.01, 16.51, False, "Puglia", "Italy", "P2"),
    ("lac-garde", "lake-garda", "le Lac de Garde", "Lac de Garde", "Italie", "it", "au", 45.65, 10.68, False, "Lake Garda", "Italy", "P2"),
    ("cinque-terre", "cinque-terre", "les Cinque Terre", "Cinque Terre", "Italie", "it", "aux", 44.13, 9.71, False, "Cinque Terre", "Italy", "P1"),
    ("turin", "turin", "Turin", "Turin", "Italie", "it", "à", 45.07, 7.69, False, "Turin", "Italy", "P3"),
    ("bologne", "bologna", "Bologne", "Bologne", "Italie", "it", "à", 44.49, 11.34, False, "Bologna", "Italy", "P3"),
    ("verone", "verona", "Vérone", "Vérone", "Italie", "it", "à", 45.44, 10.99, False, "Verona", "Italy", "P3"),
    ("palerme", "palermo", "Palerme", "Palerme", "Italie", "it", "à", 38.12, 13.36, False, "Palermo", "Italy", "P2"),
    ("dolomites", "dolomites", "les Dolomites", "Dolomites", "Italie", "it", "dans les", 46.41, 11.84, False, "Dolomites", "Italy", "P2"),

    # Espagne
    ("madrid", "madrid", "Madrid", "Madrid", "Espagne", "es", "à", 40.42, -3.70, False, "Madrid", "Spain", "P1"),
    ("grenade", "granada", "Grenade", "Grenade", "Espagne", "es", "à", 37.18, -3.60, False, "Granada", "Spain", "P1"),
    ("cadix", "cadiz", "Cadix", "Cadix", "Espagne", "es", "à", 36.53, -6.29, False, "Cadiz", "Spain", "P2"),
    ("saint-sebastien", "san-sebastian", "Saint-Sébastien", "Saint-Sébastien", "Espagne", "es", "à", 43.32, -1.98, False, "San Sebastián", "Spain", "P2"),
    ("bilbao", "bilbao", "Bilbao", "Bilbao", "Espagne", "es", "à", 43.26, -2.93, False, "Bilbao", "Spain", "P3"),
    ("formentera", "formentera", "Formentera", "Formentera", "Espagne", "es", "à", 38.70, 1.44, False, "Formentera", "Spain", "P2"),
    ("costa-brava", "costa-brava", "la Costa Brava", "Costa Brava", "Espagne", "es", "sur la", 41.87, 3.10, False, "Costa Brava", "Spain", "P2"),
    ("la-palma", "la-palma", "La Palma", "La Palma", "Espagne", "es", "à", 28.68, -17.76, False, "La Palma", "Spain", "P3"),
    ("la-gomera", "la-gomera", "La Gomera", "La Gomera", "Espagne", "es", "à", 28.09, -17.11, False, "La Gomera", "Spain", "P3"),
    ("cordoue", "cordoba", "Cordoue", "Cordoue", "Espagne", "es", "à", 37.88, -4.78, False, "Córdoba", "Spain", "P2"),

    # Portugal
    ("faro", "faro", "Faro", "Faro", "Portugal", "pt", "à", 37.02, -7.93, False, "Faro", "Portugal", "P2"),
    ("acores", "azores", "les Açores", "Açores", "Portugal", "pt", "aux", 37.75, -25.67, False, "Azores", "Portugal", "P1"),
    ("sintra", "sintra", "Sintra", "Sintra", "Portugal", "pt", "à", 38.80, -9.38, False, "Sintra", "Portugal", "P3"),

    # France
    ("normandie", "normandy", "la Normandie", "Normandie", "France", "fr", "en", 49.18, -0.37, False, "Normandy", "France", "P2"),
    ("pays-basque", "french-basque-country", "le Pays Basque", "Pays Basque", "France", "fr", "au", 43.37, -1.30, False, "French Basque Country", "France", "P2"),
    ("dordogne", "dordogne", "la Dordogne", "Dordogne", "France", "fr", "en", 44.86, 0.58, False, "Dordogne", "France", "P3"),
    ("strasbourg", "strasbourg", "Strasbourg", "Strasbourg", "France", "fr", "à", 48.57, 7.75, False, "Strasbourg", "France", "P3"),
    ("chamonix", "chamonix", "Chamonix", "Chamonix", "France", "fr", "à", 45.92, 6.87, False, "Chamonix", "France", "P3"),
    ("biarritz", "biarritz", "Biarritz", "Biarritz", "France", "fr", "à", 43.48, -1.56, False, "Biarritz", "France", "P2"),
    ("montpellier", "montpellier", "Montpellier", "Montpellier", "France", "fr", "à", 43.61, 3.88, False, "Montpellier", "France", "P3"),

    # Croatie
    ("zadar", "zadar", "Zadar", "Zadar", "Croatie", "hr", "à", 44.12, 15.23, False, "Zadar", "Croatia", "P2"),
    ("hvar", "hvar", "Hvar", "Hvar", "Croatie", "hr", "à", 43.17, 16.44, False, "Hvar", "Croatia", "P2"),
    ("plitvice", "plitvice", "Plitvice", "Plitvice", "Croatie", "hr", "à", 44.88, 15.62, False, "Plitvice", "Croatia", "P3"),
    ("zagreb", "zagreb", "Zagreb", "Zagreb", "Croatie", "hr", "à", 45.81, 15.98, False, "Zagreb", "Croatia", "P3"),

    # Turquie
    ("antalya", "antalya", "Antalya", "Antalya", "Turquie", "tr", "à", 36.90, 30.69, False, "Antalya", "Turkey", "P1"),
    ("bodrum", "bodrum", "Bodrum", "Bodrum", "Turquie", "tr", "à", 37.04, 27.43, False, "Bodrum", "Turkey", "P2"),
    ("cappadoce", "cappadocia", "la Cappadoce", "Cappadoce", "Turquie", "tr", "en", 38.64, 34.83, False, "Cappadocia", "Turkey", "P1"),
    ("izmir", "izmir", "Izmir", "Izmir", "Turquie", "tr", "à", 38.42, 27.13, False, "Izmir", "Turkey", "P3"),
    ("fethiye", "fethiye", "Fethiye", "Fethiye", "Turquie", "tr", "à", 36.65, 29.13, False, "Fethiye", "Turkey", "P3"),

    # Allemagne
    ("munich", "munich", "Munich", "Munich", "Allemagne", "de", "à", 48.14, 11.58, False, "Munich", "Germany", "P2"),
    ("hambourg", "hamburg", "Hambourg", "Hambourg", "Allemagne", "de", "à", 53.55, 9.99, False, "Hamburg", "Germany", "P3"),
    ("francfort", "frankfurt", "Francfort", "Francfort", "Allemagne", "de", "à", 50.11, 8.68, False, "Frankfurt", "Germany", "P3"),

    # Scandinavie
    ("copenhague", "copenhagen", "Copenhague", "Copenhague", "Danemark", "dk", "à", 55.68, 12.57, False, "Copenhagen", "Denmark", "P1"),
    ("stockholm", "stockholm", "Stockholm", "Stockholm", "Suède", "se", "à", 59.33, 18.07, False, "Stockholm", "Sweden", "P2"),
    ("oslo", "oslo", "Oslo", "Oslo", "Norvège", "no", "à", 59.91, 10.75, False, "Oslo", "Norway", "P2"),
    ("helsinki", "helsinki", "Helsinki", "Helsinki", "Finlande", "fi", "à", 60.17, 24.94, False, "Helsinki", "Finland", "P3"),
    ("lofoten", "lofoten", "les Îles Lofoten", "Îles Lofoten", "Norvège", "no", "aux", 68.24, 14.57, False, "Lofoten Islands", "Norway", "P2"),
    ("laponie", "lapland", "la Laponie", "Laponie", "Finlande", "fi", "en", 68.44, 27.42, False, "Lapland", "Finland", "P2"),
    ("tromso", "tromso", "Tromsø", "Tromsø", "Norvège", "no", "à", 69.65, 18.96, False, "Tromsø", "Norway", "P3"),
    ("bergen", "bergen", "Bergen", "Bergen", "Norvège", "no", "à", 60.39, 5.32, False, "Bergen", "Norway", "P3"),

    # Europe centrale & orientale
    ("budapest", "budapest", "Budapest", "Budapest", "Hongrie", "hu", "à", 47.50, 19.04, False, "Budapest", "Hungary", "P1"),
    ("cracovie", "krakow", "Cracovie", "Cracovie", "Pologne", "pl", "à", 50.06, 19.94, False, "Krakow", "Poland", "P1"),
    ("varsovie", "warsaw", "Varsovie", "Varsovie", "Pologne", "pl", "à", 52.23, 21.01, False, "Warsaw", "Poland", "P3"),
    ("bucarest", "bucharest", "Bucarest", "Bucarest", "Roumanie", "ro", "à", 44.43, 26.10, False, "Bucharest", "Romania", "P3"),
    ("sofia", "sofia", "Sofia", "Sofia", "Bulgarie", "bg", "à", 42.70, 23.32, False, "Sofia", "Bulgaria", "P3"),
    ("tallinn", "tallinn", "Tallinn", "Tallinn", "Estonie", "ee", "à", 59.44, 24.75, False, "Tallinn", "Estonia", "P3"),
    ("riga", "riga", "Riga", "Riga", "Lettonie", "lv", "à", 56.95, 24.11, False, "Riga", "Latvia", "P3"),
    ("vilnius", "vilnius", "Vilnius", "Vilnius", "Lituanie", "lt", "à", 54.69, 25.28, False, "Vilnius", "Lithuania", "P3"),
    ("bratislava", "bratislava", "Bratislava", "Bratislava", "Slovaquie", "sk", "à", 48.15, 17.11, False, "Bratislava", "Slovakia", "P3"),
    ("ljubljana", "ljubljana", "Ljubljana", "Ljubljana", "Slovénie", "si", "à", 46.06, 14.51, False, "Ljubljana", "Slovenia", "P3"),

    # Balkans & Méditerranée orientale
    ("montenegro", "montenegro", "le Monténégro", "Monténégro", "Monténégro", "me", "au", 42.28, 18.84, False, "Montenegro", "Montenegro", "P1"),
    ("kotor", "kotor", "Kotor", "Kotor", "Monténégro", "me", "à", 42.42, 18.77, False, "Kotor", "Montenegro", "P2"),
    ("albanie", "albania", "l'Albanie", "Albanie", "Albanie", "al", "en", 41.33, 19.82, False, "Albania", "Albania", "P2"),
    ("chypre", "cyprus", "Chypre", "Chypre", "Chypre", "cy", "à", 34.71, 33.02, False, "Cyprus", "Cyprus", "P1"),
    ("paphos", "paphos", "Paphos", "Paphos", "Chypre", "cy", "à", 34.78, 32.42, False, "Paphos", "Cyprus", "P3"),

    # Suisse & Benelux
    ("zurich", "zurich", "Zurich", "Zurich", "Suisse", "ch", "à", 47.38, 8.54, False, "Zurich", "Switzerland", "P3"),
    ("geneve", "geneva", "Genève", "Genève", "Suisse", "ch", "à", 46.20, 6.14, False, "Geneva", "Switzerland", "P3"),
    ("bruxelles", "brussels", "Bruxelles", "Bruxelles", "Belgique", "be", "à", 50.85, 4.35, False, "Brussels", "Belgium", "P2"),
    ("bruges", "bruges", "Bruges", "Bruges", "Belgique", "be", "à", 51.21, 3.22, False, "Bruges", "Belgium", "P3"),

    # Îles & destinations spéciales Europe
    ("gozo", "gozo", "Gozo", "Gozo", "Malte", "mt", "à", 36.04, 14.24, False, "Gozo", "Malta", "P3"),

    # ══════════════════════════════════════════════════════════════════════════
    # AFRIQUE DU NORD & MOYEN-ORIENT
    # ══════════════════════════════════════════════════════════════════════════

    # Maroc
    ("fes", "fes", "Fès", "Fès", "Maroc", "ma", "à", 34.03, -4.98, False, "Fes", "Morocco", "P1"),
    ("essaouira", "essaouira", "Essaouira", "Essaouira", "Maroc", "ma", "à", 31.51, -9.77, False, "Essaouira", "Morocco", "P2"),
    ("chefchaouen", "chefchaouen", "Chefchaouen", "Chefchaouen", "Maroc", "ma", "à", 35.17, -5.27, False, "Chefchaouen", "Morocco", "P3"),
    ("ouarzazate", "ouarzazate", "Ouarzazate", "Ouarzazate", "Maroc", "ma", "à", 30.92, -6.90, False, "Ouarzazate", "Morocco", "P3"),

    # Tunisie
    ("tunis", "tunis", "Tunis", "Tunis", "Tunisie", "tn", "à", 36.81, 10.17, False, "Tunis", "Tunisia", "P2"),
    ("djerba", "djerba", "Djerba", "Djerba", "Tunisie", "tn", "à", 33.81, 10.86, False, "Djerba", "Tunisia", "P1"),
    ("hammamet", "hammamet", "Hammamet", "Hammamet", "Tunisie", "tn", "à", 36.40, 10.62, False, "Hammamet", "Tunisia", "P3"),

    # Égypte
    ("le-caire", "cairo", "Le Caire", "Caire", "Égypte", "eg", "au", 30.04, 31.24, False, "Cairo", "Egypt", "P1"),
    ("hurghada", "hurghada", "Hurghada", "Hurghada", "Égypte", "eg", "à", 27.26, 33.81, False, "Hurghada", "Egypt", "P1"),
    ("sharm-el-sheikh", "sharm-el-sheikh", "Sharm el-Sheikh", "Sharm el-Sheikh", "Égypte", "eg", "à", 27.98, 34.38, False, "Sharm el-Sheikh", "Egypt", "P2"),
    ("louxor", "luxor", "Louxor", "Louxor", "Égypte", "eg", "à", 25.69, 32.64, False, "Luxor", "Egypt", "P2"),
    ("marsa-alam", "marsa-alam", "Marsa Alam", "Marsa Alam", "Égypte", "eg", "à", 25.07, 34.90, False, "Marsa Alam", "Egypt", "P3"),

    # Moyen-Orient
    ("jordanie", "jordan", "la Jordanie", "Jordanie", "Jordanie", "jo", "en", 30.33, 35.44, False, "Jordan", "Jordan", "P1"),
    ("oman", "oman", "Oman", "Oman", "Oman", "om", "à", 23.61, 58.54, False, "Oman", "Oman", "P2"),
    ("abu-dhabi", "abu-dhabi", "Abu Dhabi", "Abu Dhabi", "Émirats Arabes Unis", "ae", "à", 24.45, 54.65, False, "Abu Dhabi", "UAE", "P2"),
    ("doha", "doha", "Doha", "Doha", "Qatar", "qa", "à", 25.29, 51.53, False, "Doha", "Qatar", "P3"),
    ("tel-aviv", "tel-aviv", "Tel-Aviv", "Tel-Aviv", "Israël", "il", "à", 32.09, 34.77, False, "Tel Aviv", "Israel", "P2"),

    # ══════════════════════════════════════════════════════════════════════════
    # AFRIQUE SUBSAHARIENNE
    # ══════════════════════════════════════════════════════════════════════════

    ("kenya", "kenya", "le Kenya", "Kenya", "Kenya", "ke", "au", -1.29, 36.82, True, "Kenya", "Kenya", "P1"),
    ("senegal", "senegal", "le Sénégal", "Sénégal", "Sénégal", "sn", "au", 14.50, -14.45, True, "Senegal", "Senegal", "P2"),
    ("madagascar", "madagascar", "Madagascar", "Madagascar", "Madagascar", "mg", "à", -18.88, 47.51, True, "Madagascar", "Madagascar", "P1"),
    ("cap-vert", "cape-verde", "le Cap-Vert", "Cap-Vert", "Cap-Vert", "cv", "au", 14.93, -23.51, True, "Cape Verde", "Cape Verde", "P2"),
    ("namibie", "namibia", "la Namibie", "Namibie", "Namibie", "na", "en", -22.57, 17.08, False, "Namibia", "Namibia", "P2"),
    ("tanzanie", "tanzania", "la Tanzanie", "Tanzanie", "Tanzanie", "tz", "en", -6.37, 35.75, True, "Tanzania", "Tanzania", "P2"),

    # ══════════════════════════════════════════════════════════════════════════
    # ASIE
    # ══════════════════════════════════════════════════════════════════════════

    # Thaïlande
    ("chiang-mai", "chiang-mai", "Chiang Mai", "Chiang Mai", "Thaïlande", "th", "à", 18.79, 98.98, True, "Chiang Mai", "Thailand", "P1"),
    ("koh-samui", "koh-samui", "Koh Samui", "Koh Samui", "Thaïlande", "th", "à", 9.51, 100.06, True, "Koh Samui", "Thailand", "P1"),
    ("krabi", "krabi", "Krabi", "Krabi", "Thaïlande", "th", "à", 8.09, 98.91, True, "Krabi", "Thailand", "P2"),
    ("koh-lanta", "koh-lanta", "Koh Lanta", "Koh Lanta", "Thaïlande", "th", "à", 7.53, 99.04, True, "Koh Lanta", "Thailand", "P2"),
    ("koh-phi-phi", "koh-phi-phi", "Koh Phi Phi", "Koh Phi Phi", "Thaïlande", "th", "à", 7.74, 98.78, True, "Koh Phi Phi", "Thailand", "P3"),
    ("koh-tao", "koh-tao", "Koh Tao", "Koh Tao", "Thaïlande", "th", "à", 10.10, 99.84, True, "Koh Tao", "Thailand", "P3"),
    ("pattaya", "pattaya", "Pattaya", "Pattaya", "Thaïlande", "th", "à", 12.93, 100.88, True, "Pattaya", "Thailand", "P3"),

    # Vietnam
    ("hanoi", "hanoi", "Hanoï", "Hanoï", "Viêt Nam", "vn", "à", 21.03, 105.85, True, "Hanoi", "Vietnam", "P1"),
    ("ho-chi-minh", "ho-chi-minh", "Hô Chi Minh-Ville", "Hô Chi Minh-Ville", "Viêt Nam", "vn", "à", 10.82, 106.63, True, "Ho Chi Minh City", "Vietnam", "P1"),
    ("baie-halong", "halong-bay", "la Baie d'Hạ Long", "Baie d'Hạ Long", "Viêt Nam", "vn", "dans la", 20.91, 107.18, True, "Halong Bay", "Vietnam", "P2"),
    ("da-nang", "da-nang", "Da Nang", "Da Nang", "Viêt Nam", "vn", "à", 16.05, 108.22, True, "Da Nang", "Vietnam", "P2"),
    ("phu-quoc", "phu-quoc", "Phú Quốc", "Phú Quốc", "Viêt Nam", "vn", "à", 10.23, 103.97, True, "Phu Quoc", "Vietnam", "P2"),

    # Indonésie
    ("lombok", "lombok", "Lombok", "Lombok", "Indonésie", "id", "à", -8.65, 116.32, True, "Lombok", "Indonesia", "P2"),
    ("java", "java", "Java", "Java", "Indonésie", "id", "à", -7.80, 110.36, True, "Java", "Indonesia", "P2"),
    ("ubud", "ubud", "Ubud", "Ubud", "Indonésie", "id", "à", -8.51, 115.26, True, "Ubud", "Indonesia", "P2"),
    ("gili", "gili-islands", "les Îles Gili", "Îles Gili", "Indonésie", "id", "aux", -8.35, 116.04, True, "Gili Islands", "Indonesia", "P3"),
    ("nusa-penida", "nusa-penida", "Nusa Penida", "Nusa Penida", "Indonésie", "id", "à", -8.73, 115.54, True, "Nusa Penida", "Indonesia", "P3"),
    ("komodo", "komodo", "Komodo", "Komodo", "Indonésie", "id", "à", -8.55, 119.49, True, "Komodo", "Indonesia", "P3"),

    # Japon
    ("kyoto", "kyoto", "Kyoto", "Kyoto", "Japon", "jp", "à", 35.01, 135.77, False, "Kyoto", "Japan", "P1"),
    ("osaka", "osaka", "Osaka", "Osaka", "Japon", "jp", "à", 34.69, 135.50, False, "Osaka", "Japan", "P2"),
    ("okinawa", "okinawa", "Okinawa", "Okinawa", "Japon", "jp", "à", 26.33, 127.80, True, "Okinawa", "Japan", "P3"),
    ("hiroshima", "hiroshima", "Hiroshima", "Hiroshima", "Japon", "jp", "à", 34.40, 132.46, False, "Hiroshima", "Japan", "P3"),

    # Chine
    ("pekin", "beijing", "Pékin", "Pékin", "Chine", "cn", "à", 39.90, 116.40, False, "Beijing", "China", "P2"),
    ("shanghai", "shanghai", "Shanghai", "Shanghai", "Chine", "cn", "à", 31.23, 121.47, False, "Shanghai", "China", "P2"),
    ("hong-kong", "hong-kong", "Hong Kong", "Hong Kong", "Chine", "cn", "à", 22.32, 114.17, True, "Hong Kong", "China", "P1"),

    # Corée du Sud
    ("seoul", "seoul", "Séoul", "Séoul", "Corée du Sud", "kr", "à", 37.57, 126.98, False, "Seoul", "South Korea", "P1"),
    ("busan", "busan", "Busan", "Busan", "Corée du Sud", "kr", "à", 35.18, 129.08, False, "Busan", "South Korea", "P3"),
    ("jeju", "jeju", "Jeju", "Jeju", "Corée du Sud", "kr", "à", 33.50, 126.53, False, "Jeju", "South Korea", "P3"),

    # Asie du Sud-Est
    ("philippines", "philippines", "les Philippines", "Philippines", "Philippines", "ph", "aux", 14.60, 120.98, True, "Philippines", "Philippines", "P1"),
    ("palawan", "palawan", "Palawan", "Palawan", "Philippines", "ph", "à", 10.21, 118.99, True, "Palawan", "Philippines", "P2"),
    ("cebu", "cebu", "Cebu", "Cebu", "Philippines", "ph", "à", 10.32, 123.89, True, "Cebu", "Philippines", "P3"),
    ("boracay", "boracay", "Boracay", "Boracay", "Philippines", "ph", "à", 11.97, 121.92, True, "Boracay", "Philippines", "P3"),
    ("kuala-lumpur", "kuala-lumpur", "Kuala Lumpur", "Kuala Lumpur", "Malaisie", "my", "à", 3.14, 101.69, True, "Kuala Lumpur", "Malaysia", "P1"),
    ("langkawi", "langkawi", "Langkawi", "Langkawi", "Malaisie", "my", "à", 6.35, 99.73, True, "Langkawi", "Malaysia", "P3"),
    ("penang", "penang", "Penang", "Penang", "Malaisie", "my", "à", 5.42, 100.33, True, "Penang", "Malaysia", "P3"),
    ("myanmar", "myanmar", "le Myanmar", "Myanmar", "Myanmar", "mm", "au", 16.87, 96.20, True, "Myanmar", "Myanmar", "P3"),
    ("laos", "laos", "le Laos", "Laos", "Laos", "la", "au", 19.86, 102.14, True, "Laos", "Laos", "P2"),
    ("luang-prabang", "luang-prabang", "Luang Prabang", "Luang Prabang", "Laos", "la", "à", 19.89, 102.13, True, "Luang Prabang", "Laos", "P3"),

    # Inde & sous-continent
    ("rajasthan", "rajasthan", "le Rajasthan", "Rajasthan", "Inde", "in", "au", 26.92, 75.79, True, "Rajasthan", "India", "P1"),
    ("kerala", "kerala", "le Kerala", "Kerala", "Inde", "in", "au", 10.85, 76.27, True, "Kerala", "India", "P2"),
    ("delhi", "delhi", "Delhi", "Delhi", "Inde", "in", "à", 28.61, 77.21, True, "Delhi", "India", "P2"),
    ("sri-lanka", "sri-lanka", "le Sri Lanka", "Sri Lanka", "Sri Lanka", "lk", "au", 7.87, 80.77, True, "Sri Lanka", "Sri Lanka", "P1"),

    # Asie centrale & Caucase
    ("georgie", "georgia", "la Géorgie", "Géorgie", "Géorgie", "ge", "en", 42.27, 43.60, False, "Georgia", "Georgia", "P2"),
    ("ouzbekistan", "uzbekistan", "l'Ouzbékistan", "Ouzbékistan", "Ouzbékistan", "uz", "en", 41.31, 69.28, False, "Uzbekistan", "Uzbekistan", "P3"),

    # ══════════════════════════════════════════════════════════════════════════
    # AMÉRIQUES
    # ══════════════════════════════════════════════════════════════════════════

    # USA
    ("san-francisco", "san-francisco", "San Francisco", "San Francisco", "États-Unis", "us", "à", 37.77, -122.42, False, "San Francisco", "USA", "P1"),
    ("las-vegas", "las-vegas", "Las Vegas", "Las Vegas", "États-Unis", "us", "à", 36.17, -115.14, False, "Las Vegas", "USA", "P1"),
    ("chicago", "chicago", "Chicago", "Chicago", "États-Unis", "us", "à", 41.88, -87.63, False, "Chicago", "USA", "P2"),
    ("boston", "boston", "Boston", "Boston", "États-Unis", "us", "à", 42.36, -71.06, False, "Boston", "USA", "P3"),
    ("washington", "washington-dc", "Washington", "Washington", "États-Unis", "us", "à", 38.91, -77.04, False, "Washington DC", "USA", "P2"),
    ("orlando", "orlando", "Orlando", "Orlando", "États-Unis", "us", "à", 28.54, -81.38, False, "Orlando", "USA", "P2"),
    ("seattle", "seattle", "Seattle", "Seattle", "États-Unis", "us", "à", 47.61, -122.33, False, "Seattle", "USA", "P3"),
    ("nouvelle-orleans", "new-orleans", "La Nouvelle-Orléans", "Nouvelle-Orléans", "États-Unis", "us", "à la", 29.95, -90.07, False, "New Orleans", "USA", "P2"),
    ("key-west", "key-west", "Key West", "Key West", "États-Unis", "us", "à", 24.56, -81.78, False, "Key West", "USA", "P3"),
    ("yellowstone", "yellowstone", "Yellowstone", "Yellowstone", "États-Unis", "us", "à", 44.43, -110.59, False, "Yellowstone", "USA", "P3"),

    # Canada
    ("montreal", "montreal", "Montréal", "Montréal", "Canada", "ca", "à", 45.50, -73.57, False, "Montreal", "Canada", "P2"),
    ("vancouver", "vancouver", "Vancouver", "Vancouver", "Canada", "ca", "à", 49.28, -123.12, False, "Vancouver", "Canada", "P2"),
    ("toronto", "toronto", "Toronto", "Toronto", "Canada", "ca", "à", 43.65, -79.38, False, "Toronto", "Canada", "P3"),
    ("quebec-ville", "quebec-city", "Québec", "Québec", "Canada", "ca", "à", 46.81, -71.21, False, "Quebec City", "Canada", "P3"),

    # Caraïbes
    ("guadeloupe", "guadeloupe", "la Guadeloupe", "Guadeloupe", "France", "gp", "en", 16.25, -61.55, True, "Guadeloupe", "Guadeloupe", "P1"),
    ("martinique", "martinique", "la Martinique", "Martinique", "France", "mq", "en", 14.64, -61.02, True, "Martinique", "Martinique", "P1"),
    ("republique-dominicaine", "dominican-republic", "la République Dominicaine", "République Dominicaine", "République Dominicaine", "do", "en", 18.47, -69.90, True, "Dominican Republic", "Dominican Republic", "P1"),
    ("punta-cana", "punta-cana", "Punta Cana", "Punta Cana", "République Dominicaine", "do", "à", 18.58, -68.40, True, "Punta Cana", "Dominican Republic", "P1"),
    ("bahamas", "bahamas", "les Bahamas", "Bahamas", "Bahamas", "bs", "aux", 25.05, -77.35, True, "Bahamas", "Bahamas", "P2"),
    ("saint-lucie", "saint-lucia", "Sainte-Lucie", "Sainte-Lucie", "Sainte-Lucie", "lc", "à", 13.91, -60.98, True, "Saint Lucia", "Saint Lucia", "P2"),
    ("curacao", "curacao", "Curaçao", "Curaçao", "Curaçao", "cw", "à", 12.17, -68.98, True, "Curaçao", "Curaçao", "P3"),
    ("aruba", "aruba", "Aruba", "Aruba", "Aruba", "aw", "à", 12.51, -69.97, True, "Aruba", "Aruba", "P3"),
    ("saint-martin", "saint-martin", "Saint-Martin", "Saint-Martin", "France", "mf", "à", 18.07, -63.05, True, "Saint Martin", "Saint Martin", "P2"),
    ("porto-rico", "puerto-rico", "Porto Rico", "Porto Rico", "États-Unis", "pr", "à", 18.47, -66.11, True, "Puerto Rico", "Puerto Rico", "P3"),
    ("trinite-et-tobago", "trinidad-and-tobago", "Trinité-et-Tobago", "Trinité-et-Tobago", "Trinité-et-Tobago", "tt", "à", 10.65, -61.50, True, "Trinidad and Tobago", "Trinidad and Tobago", "P3"),
    ("antigua", "antigua", "Antigua", "Antigua", "Antigua-et-Barbuda", "ag", "à", 17.12, -61.85, True, "Antigua", "Antigua and Barbuda", "P3"),

    # Mexique
    ("mexico", "mexico-city", "Mexico", "Mexico", "Mexique", "mx", "à", 19.43, -99.13, False, "Mexico City", "Mexico", "P2"),
    ("playa-del-carmen", "playa-del-carmen", "Playa del Carmen", "Playa del Carmen", "Mexique", "mx", "à", 20.63, -87.08, True, "Playa del Carmen", "Mexico", "P2"),
    ("puerto-vallarta", "puerto-vallarta", "Puerto Vallarta", "Puerto Vallarta", "Mexique", "mx", "à", 20.65, -105.23, True, "Puerto Vallarta", "Mexico", "P2"),
    ("oaxaca", "oaxaca", "Oaxaca", "Oaxaca", "Mexique", "mx", "à", 17.06, -96.73, True, "Oaxaca", "Mexico", "P3"),
    ("cabo-san-lucas", "cabo-san-lucas", "Cabo San Lucas", "Cabo San Lucas", "Mexique", "mx", "à", 22.89, -109.91, False, "Cabo San Lucas", "Mexico", "P2"),

    # Amérique centrale
    ("panama", "panama", "le Panama", "Panama", "Panama", "pa", "au", 8.98, -79.52, True, "Panama", "Panama", "P2"),
    ("guatemala", "guatemala", "le Guatemala", "Guatemala", "Guatemala", "gt", "au", 14.63, -90.51, True, "Guatemala", "Guatemala", "P3"),
    ("belize", "belize", "le Belize", "Belize", "Belize", "bz", "au", 17.25, -88.77, True, "Belize", "Belize", "P3"),
    ("nicaragua", "nicaragua", "le Nicaragua", "Nicaragua", "Nicaragua", "ni", "au", 12.11, -86.27, True, "Nicaragua", "Nicaragua", "P3"),

    # Amérique du Sud
    ("perou", "peru", "le Pérou", "Pérou", "Pérou", "pe", "au", -12.05, -77.04, False, "Peru", "Peru", "P1"),
    ("machu-picchu", "machu-picchu", "le Machu Picchu", "Machu Picchu", "Pérou", "pe", "au", -13.16, -72.55, False, "Machu Picchu", "Peru", "P1"),
    ("colombie", "colombia", "la Colombie", "Colombie", "Colombie", "co", "en", 4.60, -74.08, True, "Colombia", "Colombia", "P1"),
    ("cartagene", "cartagena", "Carthagène", "Carthagène", "Colombie", "co", "à", 10.39, -75.51, True, "Cartagena", "Colombia", "P2"),
    ("medellin", "medellin", "Medellín", "Medellín", "Colombie", "co", "à", 6.25, -75.56, True, "Medellín", "Colombia", "P2"),
    ("chili", "chile", "le Chili", "Chili", "Chili", "cl", "au", -35.00, -71.00, False, "Chile", "Chile", "P2"),
    ("santiago", "santiago", "Santiago du Chili", "Santiago", "Chili", "cl", "à", -33.45, -70.67, False, "Santiago", "Chile", "P3"),
    ("patagonie", "patagonia", "la Patagonie", "Patagonie", "Argentine", "ar", "en", -51.73, -69.37, False, "Patagonia", "Argentina", "P2"),
    ("equateur", "ecuador", "l'Équateur", "Équateur", "Équateur", "ec", "en", -0.18, -78.47, True, "Ecuador", "Ecuador", "P3"),
    ("galapagos", "galapagos", "les Galápagos", "Galápagos", "Équateur", "ec", "aux", -0.95, -90.97, True, "Galápagos", "Ecuador", "P2"),
    ("bolivie", "bolivia", "la Bolivie", "Bolivie", "Bolivie", "bo", "en", -16.50, -68.15, False, "Bolivia", "Bolivia", "P3"),
    ("uruguay", "uruguay", "l'Uruguay", "Uruguay", "Uruguay", "uy", "en", -34.91, -56.19, False, "Uruguay", "Uruguay", "P3"),

    # ══════════════════════════════════════════════════════════════════════════
    # OCÉANIE & PACIFIQUE
    # ══════════════════════════════════════════════════════════════════════════

    ("sydney", "sydney", "Sydney", "Sydney", "Australie", "au", "à", -33.87, 151.21, False, "Sydney", "Australia", "P1"),
    ("melbourne", "melbourne", "Melbourne", "Melbourne", "Australie", "au", "à", -37.81, 144.96, False, "Melbourne", "Australia", "P2"),
    ("nouvelle-zelande", "new-zealand", "la Nouvelle-Zélande", "Nouvelle-Zélande", "Nouvelle-Zélande", "nz", "en", -41.29, 174.78, False, "New Zealand", "New Zealand", "P1"),
    ("fidji", "fiji", "les Fidji", "Fidji", "Fidji", "fj", "aux", -17.71, 177.99, True, "Fiji", "Fiji", "P2"),
    ("polynesie", "french-polynesia", "la Polynésie Française", "Polynésie", "France", "pf", "en", -17.53, -149.57, True, "French Polynesia", "French Polynesia", "P1"),
    ("bora-bora", "bora-bora", "Bora Bora", "Bora Bora", "France", "pf", "à", -16.50, -151.74, True, "Bora Bora", "French Polynesia", "P1"),
    ("nouvelle-caledonie", "new-caledonia", "la Nouvelle-Calédonie", "Nouvelle-Calédonie", "France", "nc", "en", -22.28, 166.46, True, "New Caledonia", "New Caledonia", "P2"),
    ("gold-coast", "gold-coast", "la Gold Coast", "Gold Coast", "Australie", "au", "sur la", -28.02, 153.43, False, "Gold Coast", "Australia", "P3"),
    ("cairns", "cairns", "Cairns", "Cairns", "Australie", "au", "à", -16.92, 145.77, True, "Cairns", "Australia", "P3"),
    ("perth", "perth", "Perth", "Perth", "Australie", "au", "à", -31.95, 115.86, False, "Perth", "Australia", "P3"),

    # ══════════════════════════════════════════════════════════════════════════
    # OCÉAN INDIEN
    # ══════════════════════════════════════════════════════════════════════════

    ("mayotte", "mayotte", "Mayotte", "Mayotte", "France", "yt", "à", -12.78, 45.23, True, "Mayotte", "Mayotte", "P2"),
    ("rodrigues", "rodrigues", "Rodrigues", "Rodrigues", "Maurice", "mu", "à", -19.72, 63.43, True, "Rodrigues", "Mauritius", "P3"),
    ("nosybe", "nosy-be", "Nosy Be", "Nosy Be", "Madagascar", "mg", "à", -13.33, 48.27, True, "Nosy Be", "Madagascar", "P3"),

    # ══════════════════════════════════════════════════════════════════════════
    # COMPLÉMENT EUROPE — villes moyennes à fort potentiel SEO
    # ══════════════════════════════════════════════════════════════════════════


    # Irlande
    ("dublin", "dublin", "Dublin", "Dublin", "Irlande", "ie", "à", 53.35, -6.26, False, "Dublin", "Ireland", "P1"),
    ("wild-atlantic-way", "wild-atlantic-way", "le Wild Atlantic Way", "Wild Atlantic Way", "Irlande", "ie", "sur le", 52.97, -9.43, False, "Wild Atlantic Way", "Ireland", "P3"),

    # Pologne côte
    ("gdansk", "gdansk", "Gdańsk", "Gdańsk", "Pologne", "pl", "à", 54.35, 18.65, False, "Gdańsk", "Poland", "P3"),

    # Roumanie
    ("transylvanie", "transylvania", "la Transylvanie", "Transylvanie", "Roumanie", "ro", "en", 46.77, 23.60, False, "Transylvania", "Romania", "P3"),

    # ══════════════════════════════════════════════════════════════════════════
    # DESTINATIONS "DIGITAL NOMAD" & TENDANCE
    # ══════════════════════════════════════════════════════════════════════════

    ("taipei", "taipei", "Taipei", "Taipei", "Taïwan", "tw", "à", 25.03, 121.57, True, "Taipei", "Taiwan", "P2"),
    ("da-lat", "da-lat", "Đà Lạt", "Đà Lạt", "Viêt Nam", "vn", "à", 11.94, 108.44, True, "Da Lat", "Vietnam", "P3"),
    ("tbilissi", "tbilisi", "Tbilissi", "Tbilissi", "Géorgie", "ge", "à", 41.72, 44.79, False, "Tbilisi", "Georgia", "P3"),
    ("canggu", "canggu", "Canggu", "Canggu", "Indonésie", "id", "à", -8.66, 115.13, True, "Canggu", "Indonesia", "P3"),

    # ══════════════════════════════════════════════════════════════════════════
    # COMPLÉMENT — Destinations prisées des voyageurs FR
    # ══════════════════════════════════════════════════════════════════════════

    # Canaries détaillées (compléter Gran Canaria, Fuerteventura, Tenerife, Lanzarote existants)
    ("el-hierro", "el-hierro", "El Hierro", "El Hierro", "Espagne", "es", "à", 27.74, -18.01, False, "El Hierro", "Spain", "P3"),

    # Baléares (compléter Majorque, Minorque, Ibiza existants)
    # Formentera already added above

    # DOM-TOM FR
    ("guyane", "french-guiana", "la Guyane", "Guyane", "France", "gf", "en", 4.94, -52.33, True, "French Guiana", "French Guiana", "P3"),
    ("saint-barthelemy", "saint-barthelemy", "Saint-Barthélemy", "Saint-Barthélemy", "France", "bl", "à", 17.90, -62.83, True, "Saint Barthélemy", "Saint Barthélemy", "P2"),
    ("saint-pierre-et-miquelon", "saint-pierre-and-miquelon", "Saint-Pierre-et-Miquelon", "Saint-Pierre-et-Miquelon", "France", "pm", "à", 46.78, -56.18, False, "Saint-Pierre and Miquelon", "Saint-Pierre and Miquelon", "P3"),

    # Compléments Afrique
    ("diani", "diani-beach", "Diani Beach", "Diani Beach", "Kenya", "ke", "à", -4.28, 39.58, True, "Diani Beach", "Kenya", "P3"),
    ("dakar", "dakar", "Dakar", "Dakar", "Sénégal", "sn", "à", 14.69, -17.44, True, "Dakar", "Senegal", "P3"),

    # Compléments Asie
    ("sapa", "sapa", "Sa Pa", "Sa Pa", "Viêt Nam", "vn", "à", 22.34, 103.84, False, "Sa Pa", "Vietnam", "P3"),
    ("nha-trang", "nha-trang", "Nha Trang", "Nha Trang", "Viêt Nam", "vn", "à", 12.24, 109.19, True, "Nha Trang", "Vietnam", "P3"),
    ("siargao", "siargao", "Siargao", "Siargao", "Philippines", "ph", "à", 9.85, 126.05, True, "Siargao", "Philippines", "P3"),
    ("el-nido", "el-nido", "El Nido", "El Nido", "Philippines", "ph", "à", 11.19, 119.39, True, "El Nido", "Philippines", "P2"),
    ("borneo", "borneo", "Bornéo", "Bornéo", "Malaisie", "my", "à", 4.97, 115.06, True, "Borneo", "Malaysia", "P3"),
    ("macao", "macau", "Macao", "Macao", "Chine", "cn", "à", 22.20, 113.54, True, "Macau", "China", "P3"),
    ("cambodge", "cambodia", "le Cambodge", "Cambodge", "Cambodge", "kh", "au", 12.57, 104.99, True, "Cambodia", "Cambodia", "P2"),
    ("phnom-penh", "phnom-penh", "Phnom Penh", "Phnom Penh", "Cambodge", "kh", "à", 11.56, 104.92, True, "Phnom Penh", "Cambodia", "P3"),
    ("nepal", "nepal", "le Népal", "Népal", "Népal", "np", "au", 27.72, 85.32, False, "Nepal", "Nepal", "P2"),

    # Compléments Amériques
    ("bermudes", "bermuda", "les Bermudes", "Bermudes", "Royaume-Uni", "bm", "aux", 32.32, -64.76, False, "Bermuda", "Bermuda", "P3"),
    ("cuzco", "cusco", "Cuzco", "Cuzco", "Pérou", "pe", "à", -13.53, -71.97, False, "Cusco", "Peru", "P2"),
    ("bogota", "bogota", "Bogota", "Bogota", "Colombie", "co", "à", 4.71, -74.07, True, "Bogota", "Colombia", "P3"),
    ("isla-holbox", "isla-holbox", "Isla Holbox", "Holbox", "Mexique", "mx", "à", 21.52, -87.38, True, "Isla Holbox", "Mexico", "P3"),
    ("valparaiso", "valparaiso", "Valparaíso", "Valparaíso", "Chili", "cl", "à", -33.05, -71.62, False, "Valparaíso", "Chile", "P3"),
]

# ── Remove duplicates with slug_fr matching existing ─────────────────────────

def load_existing_slugs():
    slugs = set()
    for row in csv.DictReader(open(f'{DATA}/destinations.csv', encoding='utf-8-sig')):
        slugs.add(row['slug_fr'])
    return slugs


def validate_no_dupes(destinations):
    """Check for internal duplicates."""
    seen_fr = set()
    seen_en = set()
    dupes = []
    for d in destinations:
        if d[0] in seen_fr:
            dupes.append(f"Duplicate slug_fr: {d[0]}")
        if d[1] in seen_en:
            dupes.append(f"Duplicate slug_en: {d[1]}")
        seen_fr.add(d[0])
        seen_en.add(d[1])
    return dupes


def geocode_validate(lat, lon, name, timeout=10):
    """Validate coordinates via Open-Meteo geocoding (reverse check)."""
    url = f"https://geocoding-api.open-meteo.com/v1/search?name={urllib.parse.quote(name)}&count=1"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'BestDateWeather/1.0'})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read())
            if data.get('results'):
                r = data['results'][0]
                dist_km = ((r['latitude'] - lat)**2 + (r['longitude'] - lon)**2)**0.5 * 111
                return {
                    'found': r['name'],
                    'lat': r['latitude'],
                    'lon': r['longitude'],
                    'dist_km': round(dist_km, 1),
                    'ok': dist_km < 100,
                }
            return {'found': None, 'ok': False}
    except Exception as e:
        return {'found': None, 'ok': False, 'error': str(e)}


def main():
    import urllib.parse

    args = sys.argv[1:]
    preview = '--preview' in args
    validate = '--validate' in args
    write = '--write' in args
    priority_filter = None
    for a in args:
        if a in ('P1', 'P2', 'P3'):
            priority_filter = a

    existing = load_existing_slugs()

    # Filter out already existing
    new_dests = [d for d in NEW_DESTINATIONS if d[0] not in existing]
    skipped = [d for d in NEW_DESTINATIONS if d[0] in existing]

    if skipped:
        print(f"⚠️  {len(skipped)} destinations déjà existantes (ignorées):")
        for d in skipped:
            print(f"   {d[0]}")

    # Filter by priority
    if priority_filter:
        new_dests = [d for d in new_dests if d[12] == priority_filter]

    # Check for internal duplicates
    dupes = validate_no_dupes(new_dests)
    if dupes:
        print("❌ Doublons internes:")
        for d in dupes:
            print(f"   {d}")
        if write:
            sys.exit(1)

    # Stats
    from collections import Counter
    priorities = Counter(d[12] for d in new_dests)
    countries = Counter(d[4] for d in new_dests)

    print(f"\n{'═' * 60}")
    print(f"  BestDateWeather — build_destinations_500.py")
    print(f"{'═' * 60}")
    print(f"  Existantes : {len(existing)}")
    print(f"  Nouvelles  : {len(new_dests)}")
    print(f"  Total      : {len(existing) + len(new_dests)}")
    print(f"\n  Par priorité :")
    for p in ('P1', 'P2', 'P3'):
        print(f"    {p} : {priorities.get(p, 0)}")
    print(f"\n  Par pays (top 10) :")
    for c, n in countries.most_common(10):
        print(f"    {c}: {n}")
    print(f"  ... et {len(countries) - 10} autres pays")

    if preview or (not validate and not write):
        print(f"\n{'─' * 60}")
        print(f"{'slug_fr':<25} {'nom_bare':<25} {'pays':<15} {'P':>3}")
        print(f"{'─' * 60}")
        for d in new_dests:
            print(f"{d[0]:<25} {d[3]:<25} {d[4]:<15} {d[12]:>3}")

    if validate:
        print(f"\n{'─' * 60}")
        print("Validation géocodage (Open-Meteo)...")
        errors = 0
        for i, d in enumerate(new_dests[:20]):  # Sample first 20
            result = geocode_validate(d[7], d[8], d[3])
            status = "✅" if result['ok'] else "⚠️ "
            print(f"  {status} {d[0]:<25} ({d[7]}, {d[8]}) → {result.get('found', '?')} ({result.get('dist_km', '?')}km)")
            if not result['ok']:
                errors += 1
            time.sleep(0.2)
        if errors:
            print(f"\n⚠️  {errors} coordonnées à vérifier")

    if write:
        print(f"\n{'─' * 60}")
        print("Écriture dans destinations.csv...")

        # Read existing
        with open(f'{DATA}/destinations.csv', 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            rows = list(reader)

        # Append new
        for d in new_dests:
            rows.append({
                'slug_fr': d[0],
                'slug_en': d[1],
                'nom_fr': d[2],
                'nom_bare': d[3],
                'pays': d[4],
                'flag': d[5],
                'prep': d[6],
                'lat': str(d[7]),
                'lon': str(d[8]),
                'tropical': str(d[9]),
                'hero_sub': '',
                'booking_dest_id': '',
                'nom_en': d[10],
                'country_en': d[11],
                'hero_sub_en': '',
                'monthly': 'False',
            })

        with open(f'{DATA}/destinations.csv', 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator='\r\n')
            writer.writeheader()
            writer.writerows(rows)

        print(f"✅ {len(new_dests)} destinations ajoutées ({len(rows)} total)")
        print(f"\nProchaines étapes :")
        print(f"  1. python3 fetch_climate.py --new")
        print(f"  2. Vérifier classes (rec/mid/avoid) dans climate.csv")
        print(f"  3. python3 generate_all.py")
        print(f"  4. python3 generate_all_en.py")


if __name__ == '__main__':
    main()
