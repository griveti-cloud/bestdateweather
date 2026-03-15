#!/usr/bin/env python3
"""Génère des hero_sub spécifiques pour les stations ski avec placeholders."""
import csv, json, re, time
import anthropic

# Exemples de bons hero_sub pour le prompt
GOOD_EXAMPLES = """
FR: "Chamonix, capitale mondiale de l'alpinisme — Mont-Blanc, Aiguille du Midi et ski d'exception."
EN: "Chamonix, world capital of mountaineering — Mont Blanc, Aiguille du Midi and exceptional skiing."
ES: "Chamonix, capital mundial del alpinismo — Mont Blanc, Aiguille du Midi y esquí de excepción."
DE: "Chamonix, Welthauptstadt des Alpinismus — Mont Blanc, Aiguille du Midi und außergewöhnliches Skifahren."

FR: "Val Gardena, Dolomites UNESCO — Sellaronda et 500 km de pistes reliées."
EN: "Val Gardena, UNESCO Dolomites — Sellaronda and 500 km of interconnected slopes."
ES: "Val Gardena, Dolomitas UNESCO — Sellaronda y 500 km de pistas conectadas."
DE: "Val Gardena, UNESCO-Dolomiten — Sellaronda und 500 km verbundene Pisten."

FR: "Sapporo, capitale de Hokkaido — festival de neige, ramen, ski à Niseko et nature sauvage."
EN: "Sapporo, capital of Hokkaido — snow festival, ramen, skiing at Niseko and wild nature."
ES: "Sapporo, capital de Hokkaido — festival de nieve, ramen, esquí en Niseko y naturaleza salvaje."
DE: "Sapporo, Hauptstadt Hokkaidos — Schneefestival, Ramen, Skifahren in Niseko und wilde Natur."
"""

SYSTEM = """Tu génères des hero_sub (sous-titres) pour des fiches météo de stations de ski.

Format strict : "[Nom], [descriptor unique court] — [2-3 éléments distinctifs concrets]."
- Maximum 120 caractères par langue
- Spécifique : mentionner ce qui rend cette station unique (domaine skiable, altitude, events, culture locale)
- PAS de "station de ski" générique
- Terminer par un point
- Ton factuel, pas publicitaire

Réponds UNIQUEMENT en JSON avec les 4 clés : fr, en, es, de"""

def generate_hero_subs(client, slug, nom, pays):
    prompt = f"""Station : {nom} ({pays})
Slug : {slug}

Génère les hero_sub en 4 langues (fr, en, es, de).

Exemples de référence :
{GOOD_EXAMPLES}

Réponds en JSON uniquement :
{{"fr": "...", "en": "...", "es": "...", "de": "..."}}"""

    resp = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=500,
        system=SYSTEM,
        messages=[{"role": "user", "content": prompt}]
    )
    text = resp.content[0].text.strip()
    # Nettoyer si markdown
    text = re.sub(r'^```json\s*', '', text)
    text = re.sub(r'\s*```$', '', text)
    return json.loads(text)


def main():
    client = anthropic.Anthropic()

    # Charger le CSV
    with open('data/destinations.csv', newline='', encoding='utf-8') as f:
        rows = list(csv.DictReader(f))
        fieldnames = csv.DictReader(open('data/destinations.csv')).fieldnames

    # Identifier les placeholders
    def is_placeholder(s):
        s = (s or '').strip()
        if not s: return True
        if re.match(r'^.{1,50} — station de ski .+\.$', s): return True
        if re.match(r'^.{1,50} — ski resort .+\.$', s): return True
        return False

    to_fix = [(i, r) for i, r in enumerate(rows)
              if r.get('mountain','').strip()=='True'
              and is_placeholder(r.get('hero_sub_fr',''))]

    print(f"À corriger : {len(to_fix)} destinations\n")

    for idx, (row_idx, row) in enumerate(to_fix):
        slug = row['slug_fr']
        nom  = row.get('nom_bare') or row.get('nom_fr', slug)
        pays = row.get('pays', '')
        print(f"[{idx+1:02d}/{len(to_fix)}] {slug} ({nom}, {pays})...", end=' ', flush=True)

        try:
            subs = generate_hero_subs(client, slug, nom, pays)
            rows[row_idx]['hero_sub_fr'] = subs['fr']
            rows[row_idx]['hero_sub_en'] = subs['en']
            rows[row_idx]['hero_sub_es'] = subs['es']
            rows[row_idx]['hero_sub_de'] = subs['de']
            print(f"✓  FR: {subs['fr'][:70]}")
        except Exception as e:
            print(f"✗ ERREUR: {e}")

        time.sleep(0.3)  # rate limit

    # Réécrire le CSV
    with open('data/destinations.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator='\r\n')
        writer.writeheader()
        writer.writerows(rows)

    print(f"\n✅ CSV mis à jour.")

if __name__ == '__main__':
    main()
