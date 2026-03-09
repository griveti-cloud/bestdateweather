#!/usr/bin/env python3
"""
generate_editorial.py
Génère des paragraphes éditoriaux "Notre avis" uniques pour les top N destinations
× 12 mois × langues configurées, via l'API Claude.

Sortie : data/editorial.json
Format : { "slug_fr:mois_num:lang": "texte éditorial" }

Usage :
  python3 generate_editorial.py                  # top 50, toutes langues
  python3 generate_editorial.py --top 10          # top 10 seulement
  python3 generate_editorial.py --lang fr en      # FR et EN seulement
  python3 generate_editorial.py --dest paris bali # destinations spécifiques
  python3 generate_editorial.py --resume          # reprendre où on s'est arrêté
"""

import argparse
import json
import os
import time
import pandas as pd
import urllib.request
import urllib.error

# ── Config ────────────────────────────────────────────────────────────────────

OUTPUT_FILE = 'data/editorial.json'
PROGRESS_FILE = 'data/editorial_progress.json'
MODEL = 'claude-opus-4-6'  # meilleur pour contenu éditorial
MAX_TOKENS = 300
DELAY_BETWEEN_CALLS = 0.5  # secondes entre appels API
TOP_N_DEFAULT = 50

LANGS = ['fr', 'en', 'es', 'de']

MONTH_NAMES = {
    'fr': ['Janvier','Février','Mars','Avril','Mai','Juin',
           'Juillet','Août','Septembre','Octobre','Novembre','Décembre'],
    'en': ['January','February','March','April','May','June',
           'July','August','September','October','November','December'],
    'es': ['Enero','Febrero','Marzo','Abril','Mayo','Junio',
           'Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre'],
    'de': ['Januar','Februar','März','April','Mai','Juni',
           'Juli','August','September','Oktober','November','Dezember'],
}

SYSTEM_PROMPTS = {
    'fr': """Tu es un rédacteur de guides de voyage expert, bienveillant et factuel.
Tu écris des paragraphes courts (2-3 phrases, max 60 mots) sur les conditions météo d'une destination un mois donné.
Ton style : conseiller ami qui connaît bien la destination. Positif mais honnête.
Règles :
- Transforme chaque contrainte en filtre de profil voyageur ("idéal pour...", "convient aux...")
- Jamais alarmiste ni découragent
- Toujours ancré dans les données fournies (températures, pluie, soleil)
- Langue : français uniquement
- Format : texte brut, pas de markdown, pas de listes""",

    'en': """You are an expert travel guide writer — warm, factual, and helpful.
Write short paragraphs (2-3 sentences, max 60 words) about weather conditions at a destination in a given month.
Your style: a knowledgeable friend who knows the destination well. Positive but honest.
Rules:
- Turn every constraint into a traveler profile filter ("ideal for...", "perfect for...", "suits...")
- Never alarming or discouraging
- Always grounded in the provided data (temperatures, rain, sunshine)
- Language: English only
- Format: plain text, no markdown, no lists""",

    'es': """Eres un redactor experto de guías de viaje — cálido, factual y útil.
Escribe párrafos cortos (2-3 frases, máx 60 palabras) sobre las condiciones meteorológicas de un destino en un mes determinado.
Tu estilo: un amigo con mucho conocimiento que conoce bien el destino. Positivo pero honesto.
Reglas:
- Convierte cada limitación en un filtro de perfil de viajero ("ideal para...", "perfecto para...", "adecuado para...")
- Nunca alarmista ni desalentador
- Siempre basado en los datos proporcionados (temperaturas, lluvia, sol)
- Idioma: español únicamente
- Formato: texto simple, sin markdown, sin listas""",

    'de': """Du bist ein erfahrener Reiseführer-Autor — freundlich, sachlich und hilfreich.
Schreibe kurze Absätze (2-3 Sätze, max. 60 Wörter) über die Wetterbedingungen an einem Reiseziel in einem bestimmten Monat.
Dein Stil: ein gut informierter Freund, der das Reiseziel gut kennt. Positiv, aber ehrlich.
Regeln:
- Verwandle jede Einschränkung in ein Reisenden-Profil-Filter ("ideal für...", "perfekt für...", "geeignet für...")
- Niemals alarmierend oder entmutigend
- Immer basierend auf den bereitgestellten Daten (Temperaturen, Regen, Sonnenschein)
- Sprache: nur Deutsch
- Format: einfacher Text, kein Markdown, keine Listen""",
}

USER_PROMPT_TPL = {
    'fr': """Destination : {nom} ({pays})
Mois : {month}
Données climatiques :
- Température : {tmin:.0f}°C min / {tmax:.0f}°C max
- Jours de pluie : {rain_pct:.0f}%
- Ensoleillement : {sun_h:.1f}h/jour
- Score météo : {score:.1f}/10
- Contexte : {context}

Écris le paragraphe "Notre avis" pour ce mois. Commence directement par le contenu, sans titre.""",

    'en': """Destination: {nom} ({pays})
Month: {month}
Climate data:
- Temperature: {tmin:.0f}°C min / {tmax:.0f}°C max
- Rain days: {rain_pct:.0f}%
- Sunshine: {sun_h:.1f}h/day
- Weather score: {score:.1f}/10
- Context: {context}

Write the "Our take" paragraph for this month. Start directly with the content, no title.""",

    'es': """Destino: {nom} ({pays})
Mes: {month}
Datos climáticos:
- Temperatura: {tmin:.0f}°C mín / {tmax:.0f}°C máx
- Días de lluvia: {rain_pct:.0f}%
- Sol: {sun_h:.1f}h/día
- Puntuación meteorológica: {score:.1f}/10
- Contexto: {context}

Escribe el párrafo "Nuestra opinión" para este mes. Empieza directamente con el contenido, sin título.""",

    'de': """Reiseziel: {nom} ({pays})
Monat: {month}
Klimadaten:
- Temperatur: {tmin:.0f}°C min / {tmax:.0f}°C max
- Regentage: {rain_pct:.0f}%
- Sonnenschein: {sun_h:.1f}h/Tag
- Wetter-Score: {score:.1f}/10
- Kontext: {context}

Schreibe den Absatz "Unser Fazit" für diesen Monat. Beginne direkt mit dem Inhalt, ohne Titel.""",
}

# Contexte automatique basé sur les données
def build_context(row, lang):
    score = row['score']
    tmax = row['tmax']
    rain = row['rain_pct']
    sun = row['sun_h']
    classe = row.get('classe', '')
    sea = row.get('sea_temp')

    facts = []

    if lang == 'fr':
        if score >= 9.0: facts.append("conditions excellentes, mois idéal")
        elif score >= 7.5: facts.append("très bonnes conditions")
        elif score >= 6.0: facts.append("conditions correctes")
        elif score >= 4.5: facts.append("conditions mitigées")
        else: facts.append("conditions difficiles")

        if tmax >= 35: facts.append("chaleur intense")
        elif tmax >= 28: facts.append("chaleur agréable")
        elif tmax <= 5: facts.append("froid hivernal")
        elif tmax <= 12: facts.append("fraîcheur automnale/printanière")

        if rain <= 10: facts.append("très peu de pluie")
        elif rain >= 60: facts.append("saison des pluies")
        elif rain >= 40: facts.append("pluies fréquentes")

        if sun >= 12: facts.append("ensoleillement maximal")
        elif sun <= 4: facts.append("journées courtes")

        if pd.notna(sea) and sea >= 24: facts.append(f"mer à {sea:.0f}°C, baignade excellente")
        elif pd.notna(sea) and sea >= 20: facts.append(f"mer à {sea:.0f}°C, baignade agréable")

    elif lang == 'en':
        if score >= 9.0: facts.append("excellent conditions, ideal month")
        elif score >= 7.5: facts.append("very good conditions")
        elif score >= 6.0: facts.append("decent conditions")
        elif score >= 4.5: facts.append("mixed conditions")
        else: facts.append("challenging conditions")

        if tmax >= 35: facts.append("intense heat")
        elif tmax >= 28: facts.append("pleasant warmth")
        elif tmax <= 5: facts.append("winter cold")
        elif tmax <= 12: facts.append("cool temperatures")

        if rain <= 10: facts.append("very little rain")
        elif rain >= 60: facts.append("rainy season")
        elif rain >= 40: facts.append("frequent rain")

        if sun >= 12: facts.append("maximum sunshine")
        elif sun <= 4: facts.append("short days")

        if pd.notna(sea) and sea >= 24: facts.append(f"sea at {sea:.0f}°C, excellent swimming")
        elif pd.notna(sea) and sea >= 20: facts.append(f"sea at {sea:.0f}°C, pleasant swimming")

    elif lang == 'es':
        if score >= 9.0: facts.append("condiciones excelentes, mes ideal")
        elif score >= 7.5: facts.append("muy buenas condiciones")
        elif score >= 6.0: facts.append("condiciones aceptables")
        elif score >= 4.5: facts.append("condiciones mixtas")
        else: facts.append("condiciones difíciles")

        if tmax >= 35: facts.append("calor intenso")
        elif tmax >= 28: facts.append("calor agradable")
        elif tmax <= 5: facts.append("frío invernal")
        elif tmax <= 12: facts.append("temperaturas frescas")

        if rain <= 10: facts.append("muy poca lluvia")
        elif rain >= 60: facts.append("temporada de lluvias")
        elif rain >= 40: facts.append("lluvias frecuentes")

        if sun >= 12: facts.append("máxima insolación")
        elif sun <= 4: facts.append("días cortos")

        if pd.notna(sea) and sea >= 24: facts.append(f"mar a {sea:.0f}°C, baño excelente")
        elif pd.notna(sea) and sea >= 20: facts.append(f"mar a {sea:.0f}°C, baño agradable")

    elif lang == 'de':
        if score >= 9.0: facts.append("ausgezeichnete Bedingungen, idealer Monat")
        elif score >= 7.5: facts.append("sehr gute Bedingungen")
        elif score >= 6.0: facts.append("annehmbare Bedingungen")
        elif score >= 4.5: facts.append("gemischte Bedingungen")
        else: facts.append("schwierige Bedingungen")

        if tmax >= 35: facts.append("intensive Hitze")
        elif tmax >= 28: facts.append("angenehme Wärme")
        elif tmax <= 5: facts.append("Winterkälte")
        elif tmax <= 12: facts.append("kühle Temperaturen")

        if rain <= 10: facts.append("sehr wenig Regen")
        elif rain >= 60: facts.append("Regenzeit")
        elif rain >= 40: facts.append("häufiger Regen")

        if sun >= 12: facts.append("maximale Sonnenstunden")
        elif sun <= 4: facts.append("kurze Tage")

        if pd.notna(sea) and sea >= 24: facts.append(f"Meer bei {sea:.0f}°C, ausgezeichnetes Baden")
        elif pd.notna(sea) and sea >= 20: facts.append(f"Meer bei {sea:.0f}°C, angenehmes Baden")

    return ', '.join(facts) if facts else 'données standard'


def call_claude(system_prompt, user_prompt):
    """Appel API Claude via HTTP direct."""
    payload = json.dumps({
        'model': MODEL,
        'max_tokens': MAX_TOKENS,
        'system': system_prompt,
        'messages': [{'role': 'user', 'content': user_prompt}]
    }).encode('utf-8')

    req = urllib.request.Request(
        'https://api.anthropic.com/v1/messages',
        data=payload,
        headers={
            'Content-Type': 'application/json',
            'anthropic-version': '2023-06-01',
            'x-api-key': os.environ.get('ANTHROPIC_API_KEY', '')
        },
        method='POST'
    )

    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read())
        return data['content'][0]['text'].strip()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--top', type=int, default=TOP_N_DEFAULT)
    parser.add_argument('--lang', nargs='+', default=LANGS)
    parser.add_argument('--dest', nargs='+', default=None, help='Slugs spécifiques')
    parser.add_argument('--resume', action='store_true', help='Reprendre sans écraser')
    parser.add_argument('--dry-run', action='store_true', help='Afficher prompts sans appeler API')
    args = parser.parse_args()

    # Charger données
    climate = pd.read_csv('data/climate.csv')
    dests = pd.read_csv('data/destinations.csv')

    # Sélectionner destinations
    if args.dest:
        target_slugs = args.dest
    else:
        avg = climate.groupby('slug')['score'].mean().reset_index()
        avg.columns = ['slug_fr', 'avg_score']
        merged = avg.merge(dests[['slug_fr', 'nom_bare', 'nom_en', 'nom_de', 'nom_es',
                                   'pays', 'country_en', 'country_de', 'country_es',
                                   'coastal', 'mountain', 'tropical']], on='slug_fr')
        top = merged.sort_values('avg_score', ascending=False).head(args.top)
        target_slugs = top['slug_fr'].tolist()

    # Charger données existantes
    editorial = {}
    if args.resume and os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, encoding='utf-8') as f:
            editorial = json.load(f)
        print(f"Reprise : {len(editorial)} entrées existantes chargées")

    # Compteurs
    total = len(target_slugs) * 12 * len(args.lang)
    done = 0
    skipped = 0
    errors = 0

    print(f"\n{'DRY RUN — ' if args.dry_run else ''}Génération éditoriale")
    print(f"Destinations : {len(target_slugs)} | Langues : {args.lang} | Total : {total} appels\n")

    for slug in target_slugs:
        # Infos destination
        dest_row = dests[dests['slug_fr'] == slug]
        if dest_row.empty:
            print(f"  ⚠️  {slug} : non trouvé dans destinations.csv")
            continue
        dest = dest_row.iloc[0]

        dest_names = {
            'fr': dest.get('nom_fr', dest['nom_bare']),
            'en': dest.get('nom_en', dest['nom_bare']),
            'es': dest.get('nom_es', dest['nom_bare']),
            'de': dest.get('nom_de', dest['nom_bare']),
        }
        country_names = {
            'fr': dest['pays'],
            'en': dest.get('country_en', dest['pays']),
            'es': dest.get('country_es', dest['pays']),
            'de': dest.get('country_de', dest['pays']),
        }

        # Données climatiques pour ce slug
        clim = climate[climate['slug'] == slug].sort_values('mois_num')
        if clim.empty:
            print(f"  ⚠️  {slug} : pas de données climatiques")
            continue

        for _, row in clim.iterrows():
            mois_num = int(row['mois_num'])

            for lang in args.lang:
                key = f"{slug}:{mois_num}:{lang}"

                # Skip si déjà généré (mode resume)
                if args.resume and key in editorial:
                    skipped += 1
                    continue

                month_name = MONTH_NAMES[lang][mois_num - 1]
                nom = dest_names.get(lang, dest['nom_bare'])
                pays = country_names.get(lang, dest['pays'])
                # Fallback si nan
                if not isinstance(nom, str) or nom == 'nan': nom = dest['nom_bare']
                if not isinstance(pays, str) or pays == 'nan': pays = dest['pays']

                context = build_context(row, lang)

                user_prompt = USER_PROMPT_TPL[lang].format(
                    nom=nom, pays=pays, month=month_name,
                    tmin=row['tmin'], tmax=row['tmax'],
                    rain_pct=row['rain_pct'], sun_h=row['sun_h'],
                    score=row['score'], context=context
                )

                if args.dry_run:
                    print(f"\n[{key}]")
                    print(f"SYSTEM: {SYSTEM_PROMPTS[lang][:80]}...")
                    print(f"USER: {user_prompt}")
                    done += 1
                    continue

                try:
                    text = call_claude(SYSTEM_PROMPTS[lang], user_prompt)
                    editorial[key] = text
                    done += 1

                    if done % 10 == 0:
                        # Sauvegarder régulièrement
                        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
                            json.dump(editorial, f, ensure_ascii=False, indent=2)
                        print(f"  💾 {done}/{total} ({skipped} skipped, {errors} errors)")

                    print(f"  ✅ [{lang}] {nom} {month_name} : {text[:60]}...")
                    time.sleep(DELAY_BETWEEN_CALLS)

                except urllib.error.HTTPError as e:
                    body = e.read().decode()
                    print(f"  ❌ [{key}] HTTP {e.code}: {body[:100]}")
                    errors += 1
                    if e.code == 429:
                        print("  ⏳ Rate limit — pause 60s")
                        time.sleep(60)
                except Exception as e:
                    print(f"  ❌ [{key}] Erreur: {e}")
                    errors += 1

    # Sauvegarde finale
    if not args.dry_run:
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(editorial, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Terminé : {done} générés, {skipped} skippés, {errors} erreurs")
    print(f"📄 Fichier : {OUTPUT_FILE} ({len(editorial)} entrées)")


if __name__ == '__main__':
    main()
