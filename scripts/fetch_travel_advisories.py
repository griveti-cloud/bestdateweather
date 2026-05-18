#!/usr/bin/env python3
"""
Fetch travel advisory levels from the French Ministry of Foreign Affairs (MAE).
Updates data/country_info.json with risk_level (1–4) and risk_updated fields.

Risk levels:
  1 = Vigilance normale (green)
  2 = Vigilance renforcée (yellow)
  3 = Déconseillé sauf raison impérative (orange)
  4 = Formellement déconseillé (red)
"""

import json
import re
import time
import urllib.request
import urllib.error
from datetime import date
from pathlib import Path

ROOT = Path(__file__).parent.parent
INFO_PATH = ROOT / "data" / "country_info.json"

# MAE URL slugs per country name (French)
MAE_SLUGS = {
    "Afrique du Sud": "afrique-du-sud",
    "Albanie": "albanie",
    "Algérie": "algerie",
    "Allemagne": "allemagne",
    "Andorre": "andorre",
    "Angola": "angola",
    "Antigua-et-Barbuda": "antigua-et-barbuda",
    "Arabie Saoudite": "arabie-saoudite",
    "Argentine": "argentine",
    "Arménie": "armenie",
    "Australie": "australie",
    "Autriche": "autriche",
    "Azerbaïdjan": "azerbaidjan",
    "Bahamas": "bahamas",
    "Bahreïn": "bahrein",
    "Bangladesh": "bangladesh",
    "Barbade": "barbade",
    "Belgique": "belgique",
    "Belize": "belize",
    "Bénin": "benin",
    "Bhutan": "bhoutan",
    "Bolivie": "bolivie",
    "Bosnie-Herzégovine": "bosnie-herzegovine",
    "Botswana": "botswana",
    "Brésil": "bresil",
    "Bulgarie": "bulgarie",
    "Burkina Faso": "burkina-faso",
    "Cambodge": "cambodge",
    "Cameroun": "cameroun",
    "Canada": "canada",
    "Cap-Vert": "cap-vert",
    "Chili": "chili",
    "Chine": "chine",
    "Chypre": "chypre",
    "Colombie": "colombie",
    "Comores": "comores",
    "Congo": "republique-du-congo",
    "Costa Rica": "costa-rica",
    "Côte d'Ivoire": "cote-d-ivoire",
    "Croatie": "croatie",
    "Cuba": "cuba",
    "Danemark": "danemark",
    "Djibouti": "djibouti",
    "Dominique": "dominique",
    "Égypte": "egypte",
    "Émirats Arabes Unis": "emirats-arabes-unis",
    "Équateur": "equateur",
    "Espagne": "espagne",
    "Estonie": "estonie",
    "Eswatini": "eswatini",
    "États-Unis": "etats-unis",
    "Éthiopie": "ethiopie",
    "Fidji": "fidji",
    "Finlande": "finlande",
    "France": "france",
    "Gabon": "gabon",
    "Gambie": "gambie",
    "Géorgie": "georgie",
    "Ghana": "ghana",
    "Grèce": "grece",
    "Guatemala": "guatemala",
    "Guinée": "guinee",
    "Honduras": "honduras",
    "Hongrie": "hongrie",
    "Îles Cook": "iles-cook",
    "Îles Maurice": "ile-maurice",
    "Inde": "inde",
    "Indonésie": "indonesie",
    "Irak": "irak",
    "Iran": "iran",
    "Irlande": "irlande",
    "Islande": "islande",
    "Israël": "israel",
    "Italie": "italie",
    "Jamaïque": "jamaique",
    "Japon": "japon",
    "Jordanie": "jordanie",
    "Kazakhstan": "kazakhstan",
    "Kenya": "kenya",
    "Kirghizstan": "kirghizstan",
    "Kosovo": "kosovo",
    "Laos": "laos",
    "Lettonie": "lettonie",
    "Liban": "liban",
    "Lituanie": "lituanie",
    "Luxembourg": "luxembourg",
    "Macédoine du Nord": "macedoine-du-nord",
    "Madagascar": "madagascar",
    "Malaisie": "malaisie",
    "Malawi": "malawi",
    "Maldives": "maldives",
    "Mali": "mali",
    "Malte": "malte",
    "Maroc": "maroc",
    "Martinique": "martinique",
    "Mexique": "mexique",
    "Moldavie": "moldavie",
    "Monaco": "monaco",
    "Mongolie": "mongolie",
    "Monténégro": "montenegro",
    "Mozambique": "mozambique",
    "Myanmar": "birmanie-myanmar",
    "Namibie": "namibie",
    "Népal": "nepal",
    "Nicaragua": "nicaragua",
    "Niger": "niger",
    "Nigéria": "nigeria",
    "Norvège": "norvege",
    "Nouvelle-Calédonie": "nouvelle-caledonie",
    "Nouvelle-Zélande": "nouvelle-zelande",
    "Oman": "oman",
    "Ouganda": "ouganda",
    "Ouzbékistan": "ouzbekistan",
    "Pakistan": "pakistan",
    "Palestine": "territoires-palestiniens",
    "Panama": "panama",
    "Papouasie-Nouvelle-Guinée": "papouasie-nouvelle-guinee",
    "Paraguay": "paraguay",
    "Pays-Bas": "pays-bas",
    "Pérou": "perou",
    "Philippines": "philippines",
    "Pologne": "pologne",
    "Polynésie française": "polynesie-francaise",
    "Portugal": "portugal",
    "Qatar": "qatar",
    "Réunion": "la-reunion",
    "République dominicaine": "republique-dominicaine",
    "République tchèque": "republique-tcheque",
    "Roumanie": "roumanie",
    "Royaume-Uni": "royaume-uni",
    "Russie": "russie",
    "Rwanda": "rwanda",
    "Saint-Kitts-et-Nevis": "saint-kitts-et-nevis",
    "Saint-Lucie": "sainte-lucie",
    "Saint-Vincent-et-les-Grenadines": "saint-vincent-et-les-grenadines",
    "Sénégal": "senegal",
    "Serbie": "serbie",
    "Seychelles": "seychelles",
    "Sierra Leone": "sierra-leone",
    "Singapour": "singapour",
    "Slovaquie": "slovaquie",
    "Slovénie": "slovenie",
    "Somalie": "somalie",
    "Soudan": "soudan",
    "Soudan du Sud": "soudan-du-sud",
    "Sri Lanka": "sri-lanka",
    "Suède": "suede",
    "Suisse": "suisse",
    "Suriname": "suriname",
    "Syrie": "syrie",
    "Tadjikistan": "tadjikistan",
    "Taiwan": "taiwan",
    "Tanzanie": "tanzanie",
    "Thaïlande": "thailande",
    "Timor-Leste": "timor-leste",
    "Togo": "togo",
    "Trinité-et-Tobago": "trinite-et-tobago",
    "Tunisie": "tunisie",
    "Turkménistan": "turkmenistan",
    "Turquie": "turquie",
    "Ukraine": "ukraine",
    "Uruguay": "uruguay",
    "Venezuela": "venezuela",
    "Vietnam": "vietnam",
    "Yémen": "yemen",
    "Zambie": "zambie",
    "Zimbabwe": "zimbabwe",
}

BASE_URL = "https://www.diplomatie.gouv.fr/fr/conseils-aux-voyageurs/conseils-par-pays-destination/{slug}/"


def fetch_risk_level(slug: str, country: str) -> int | None:
    """
    Fetch MAE page and extract global risk level (1–4).
    Returns None on error.
    """
    url = BASE_URL.format(slug=slug)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        html = urllib.request.urlopen(req, timeout=12).read().decode("utf-8", errors="ignore")
    except Exception as e:
        print(f"  ✗ {country}: fetch error — {e}")
        return None

    # MAE uses color classes in the security section
    # Priority: red (4) > orange (3) > yellow/orange-light (2) > green (1)
    # Look for the FIRST/global advisory, not zone-specific
    
    # Pattern 1: explicit "formellement déconseillé" (level 4)
    if re.search(r"formellement\s+déconseillé", html, re.I):
        # Check if it applies globally (before any zone mention)
        m = re.search(r"formellement\s+déconseillé[^\.]{0,300}", html, re.I)
        if m and "zone" not in m.group().lower()[:100]:
            return 4

    # Pattern 2: "déconseillé sauf" globally (level 3)
    m3 = re.search(r"déconseillé\s+sauf\s+raison\s+impérative[^\.]{0,200}", html, re.I)
    if m3 and "zone" not in m3.group().lower()[:100]:
        return 3

    # Pattern 3: look for CSS color classes in security section
    # MAE wraps global level in a coloured band
    color_map = {
        "rouge": 4,
        "orange": 3,
        "jaune": 2,
        "vert": 1,
    }
    # Find the security/safety section header and the color near it
    sec_match = re.search(
        r'(?:sécurité|niveau\s+de\s+risque)[^<]{0,500}?(rouge|orange|jaune|vert)',
        html, re.I | re.S
    )
    if sec_match:
        color = sec_match.group(1).lower()
        return color_map.get(color, 2)

    # Pattern 4: look for colored badges/chips in page header
    badge_match = re.search(
        r'class="[^"]*(?:pastille|badge|label|tag)[^"]*(?:rouge|orange|jaune|vert)[^"]*"',
        html, re.I
    )
    if badge_match:
        for color, level in color_map.items():
            if color in badge_match.group().lower():
                return level

    # Pattern 5: "vigilance renforcée" = level 2
    if re.search(r"vigilance\s+renforcée", html, re.I):
        return 2

    # Default: vigilance normale
    return 1


def main():
    info = json.load(open(INFO_PATH))
    today = date.today().isoformat()

    countries = sorted(info.keys())
    total = len(countries)
    updated = 0
    skipped = 0
    errors = 0

    print(f"=== fetch_travel_advisories.py — {today} ===")
    print(f"Pays à traiter : {total}")
    print()

    for i, country in enumerate(countries, 1):
        entry = info[country]

        # Skip if already updated today
        if entry.get("risk_updated") == today:
            skipped += 1
            continue

        slug = MAE_SLUGS.get(country)
        if not slug:
            print(f"  [{i}/{total}] {country}: pas de slug MAE — skip")
            entry["risk_level"] = 1
            entry["risk_updated"] = today
            updated += 1
            continue

        risk = fetch_risk_level(slug, country)

        if risk is None:
            errors += 1
            # Keep existing or default to 1
            if "risk_level" not in entry:
                entry["risk_level"] = 1
        else:
            entry["risk_level"] = risk
            entry["risk_updated"] = today
            entry["risk_source"] = "MAE France"
            updated += 1
            label = {1: "✅ Normal", 2: "🟡 Renforcé", 3: "🟠 Déconseillé", 4: "🔴 Formellement déconseillé"}
            print(f"  [{i}/{total}] {country}: {label[risk]}")

        # Save after each country to avoid data loss
        json.dump(info, open(INFO_PATH, "w"), ensure_ascii=False, indent=2)

        # Polite delay
        time.sleep(0.8)

    print()
    print(f"=== Terminé ===")
    print(f"Mis à jour : {updated} | Déjà à jour : {skipped} | Erreurs : {errors}")

    # Summary of non-normal levels
    print("\nPays avec niveau > 1 :")
    for country, entry in sorted(info.items(), key=lambda x: -x[1].get("risk_level", 1)):
        lvl = entry.get("risk_level", 1)
        if lvl > 1:
            print(f"  {country}: {lvl}")


if __name__ == "__main__":
    main()
