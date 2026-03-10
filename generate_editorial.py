#!/usr/bin/env python3
"""
generate_editorial.py — Génération éditoriale résiliente via API Claude
- Sauvegarde après CHAQUE appel réussi
- Retry automatique (3x) sur erreur réseau/5xx
- Pause auto sur 429
- Reprise automatique (skip si déjà généré)
- Exit immédiat si clé invalide

Usage:
  python3 generate_editorial.py --key sk-ant-...
  python3 generate_editorial.py --key sk-ant-... --top 10 --lang fr en
  python3 generate_editorial.py --key sk-ant-... --dest paris bali
  python3 generate_editorial.py --key sk-ant-... --overwrite
"""

import argparse, json, os, time, sys
import urllib.request, urllib.error
import pandas as pd

OUTPUT_FILE  = 'data/editorial.json'
CLIMATE_FILE = 'data/climate.csv'
DESTS_FILE   = 'data/destinations.csv'

MODEL         = 'claude-haiku-4-5-20251001'
MAX_TOKENS    = 250
API_URL       = 'https://api.anthropic.com/v1/messages'
DELAY_OK      = 0.3
DELAY_RETRY   = 5.0
DELAY_RL      = 65.0
MAX_RETRIES   = 3
TOP_N_DEFAULT = 50
LANGS_DEFAULT = ['fr', 'en', 'es', 'de']

MONTHS = {
    'fr': ['Janvier','Février','Mars','Avril','Mai','Juin','Juillet','Août','Septembre','Octobre','Novembre','Décembre'],
    'en': ['January','February','March','April','May','June','July','August','September','October','November','December'],
    'es': ['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre'],
    'de': ['Januar','Februar','März','April','Mai','Juni','Juli','August','September','Oktober','November','Dezember'],
}

SYSTEM = {
    'fr': "Tu es un rédacteur de guides de voyage, bienveillant et factuel. Écris 2-3 phrases (max 55 mots) sur la météo d'une destination un mois donné. Style : ami expert. Positif mais honnête. Transforme chaque contrainte en profil voyageur. Langue : français. Texte brut uniquement.",
    'en': "You are a warm, factual travel guide writer. Write 2-3 sentences (max 55 words) about the weather at a destination in a given month. Style: knowledgeable friend. Positive but honest. Turn every constraint into a traveler profile. English only. Plain text.",
    'es': "Eres un redactor de guías de viaje, cálido y factual. Escribe 2-3 frases (máx 55 palabras) sobre el clima de un destino en un mes. Estilo: amigo experto. Positivo pero honesto. Convierte cada limitación en perfil de viajero. Español. Texto simple.",
    'de': "Du bist ein freundlicher, sachlicher Reiseführer-Autor. Schreibe 2-3 Sätze (max. 55 Wörter) über das Wetter an einem Reiseziel in einem Monat. Stil: kundiger Freund. Positiv aber ehrlich. Verwandle jede Einschränkung in ein Reisenden-Profil. Deutsch. Einfacher Text.",
}

USER_TPL = {
    'fr': "Destination : {nom} ({pays})\nMois : {month}\nTempérature : {tmin:.0f}–{tmax:.0f}°C | Pluie : {rain:.0f}% | Soleil : {sun:.1f}h/j | Score : {score:.1f}/10\nContexte : {ctx}\n\nÉcris le paragraphe \"Notre avis\". Commence directement sans titre.",
    'en': "Destination: {nom} ({pays})\nMonth: {month}\nTemp: {tmin:.0f}–{tmax:.0f}°C | Rain: {rain:.0f}% | Sun: {sun:.1f}h/d | Score: {score:.1f}/10\nContext: {ctx}\n\nWrite the \"Our take\" paragraph. Start directly, no title.",
    'es': "Destino: {nom} ({pays})\nMes: {month}\nTemp: {tmin:.0f}–{tmax:.0f}°C | Lluvia: {rain:.0f}% | Sol: {sun:.1f}h/d | Puntuación: {score:.1f}/10\nContexto: {ctx}\n\nEscribe el párrafo \"Nuestra opinión\". Empieza directamente, sin título.",
    'de': "Reiseziel: {nom} ({pays})\nMonat: {month}\nTemp: {tmin:.0f}–{tmax:.0f}°C | Regen: {rain:.0f}% | Sonne: {sun:.1f}h/T | Score: {score:.1f}/10\nKontext: {ctx}\n\nSchreibe den Absatz \"Unser Fazit\". Beginne direkt, ohne Titel.",
}

def ctx(row, lang):
    s, tx, rain, sun = row['score'], row['tmax'], row['rain_pct'], row['sun_h']
    sea = row.get('sea_temp')
    if lang == 'fr':
        q = "excellent" if s>=9 else ("très bon" if s>=7.5 else ("correct" if s>=6 else ("mitigé" if s>=4.5 else "difficile")))
        t = "chaleur intense" if tx>=35 else ("très chaud" if tx>=28 else ("doux" if tx>=18 else ("frais" if tx>=10 else "froid")))
        r = "sec" if rain<=10 else ("peu de pluie" if rain<=30 else ("pluies fréquentes" if rain<=55 else "saison des pluies"))
        sk = f"mer {sea:.0f}°C" if pd.notna(sea) and sea>0 else ""
    elif lang == 'en':
        q = "excellent" if s>=9 else ("very good" if s>=7.5 else ("decent" if s>=6 else ("mixed" if s>=4.5 else "challenging")))
        t = "intense heat" if tx>=35 else ("very warm" if tx>=28 else ("mild" if tx>=18 else ("cool" if tx>=10 else "cold")))
        r = "dry" if rain<=10 else ("little rain" if rain<=30 else ("frequent rain" if rain<=55 else "rainy season"))
        sk = f"sea {sea:.0f}°C" if pd.notna(sea) and sea>0 else ""
    elif lang == 'es':
        q = "excelente" if s>=9 else ("muy bueno" if s>=7.5 else ("aceptable" if s>=6 else ("mixto" if s>=4.5 else "difícil")))
        t = "calor intenso" if tx>=35 else ("muy cálido" if tx>=28 else ("templado" if tx>=18 else ("fresco" if tx>=10 else "frío")))
        r = "seco" if rain<=10 else ("poca lluvia" if rain<=30 else ("lluvias frecuentes" if rain<=55 else "temporada lluvias"))
        sk = f"mar {sea:.0f}°C" if pd.notna(sea) and sea>0 else ""
    else:
        q = "ausgezeichnet" if s>=9 else ("sehr gut" if s>=7.5 else ("annehmbar" if s>=6 else ("gemischt" if s>=4.5 else "schwierig")))
        t = "intensive Hitze" if tx>=35 else ("sehr warm" if tx>=28 else ("mild" if tx>=18 else ("kühl" if tx>=10 else "kalt")))
        r = "trocken" if rain<=10 else ("wenig Regen" if rain<=30 else ("häufiger Regen" if rain<=55 else "Regenzeit"))
        sk = f"Meer {sea:.0f}°C" if pd.notna(sea) and sea>0 else ""
    parts = [q, t, r]
    if sk: parts.append(sk)
    return ', '.join(parts)

def call_api(key, system_prompt, user_prompt):
    payload = json.dumps({
        'model': MODEL, 'max_tokens': MAX_TOKENS,
        'system': system_prompt,
        'messages': [{'role': 'user', 'content': user_prompt}]
    }).encode('utf-8')

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            req = urllib.request.Request(API_URL, data=payload, headers={
                'Content-Type': 'application/json',
                'anthropic-version': '2023-06-01',
                'x-api-key': key,
            }, method='POST')
            with urllib.request.urlopen(req, timeout=45) as resp:
                data = json.loads(resp.read())
                return data['content'][0]['text'].strip()

        except urllib.error.HTTPError as e:
            body = e.read().decode()
            if e.code == 401:
                print("\n❌ CLÉ API INVALIDE — vérifiez votre clé Anthropic")
                sys.exit(1)
            if e.code == 429:
                print(f"  ⏳ Rate limit — pause {DELAY_RL:.0f}s...")
                time.sleep(DELAY_RL)
                continue
            if e.code >= 500:
                if attempt < MAX_RETRIES:
                    time.sleep(DELAY_RETRY * attempt)
                    continue
            raise RuntimeError(f"HTTP {e.code}: {body[:100]}")

        except (OSError, TimeoutError) as e:
            if attempt < MAX_RETRIES:
                print(f"  ⚠️  Réseau ({attempt}/{MAX_RETRIES}): {e} — retry dans {DELAY_RETRY}s")
                time.sleep(DELAY_RETRY * attempt)
                continue
            raise

    raise RuntimeError(f"Échec après {MAX_RETRIES} tentatives")

def save(data):
    tmp = OUTPUT_FILE + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, OUTPUT_FILE)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--key',       required=True)
    parser.add_argument('--top',       type=int, default=TOP_N_DEFAULT)
    parser.add_argument('--lang',      nargs='+', default=LANGS_DEFAULT)
    parser.add_argument('--dest',      nargs='+', default=None)
    parser.add_argument('--overwrite', action='store_true')
    args = parser.parse_args()

    climate = pd.read_csv(CLIMATE_FILE)
    dests   = pd.read_csv(DESTS_FILE)

    if args.dest:
        target_slugs = args.dest
    else:
        avg = climate.groupby('slug')['score'].mean().reset_index()
        avg.columns = ['slug_fr', 'avg_score']
        top = avg.merge(dests[['slug_fr']], on='slug_fr').sort_values('avg_score', ascending=False).head(args.top)
        target_slugs = top['slug_fr'].tolist()

    # Charger existant
    editorial = {}
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, encoding='utf-8') as f:
            editorial = json.load(f)

    # Construire tâches
    tasks = []
    for slug in target_slugs:
        clim = climate[climate['slug'] == slug].sort_values('mois_num')
        dest_rows = dests[dests['slug_fr'] == slug]
        if clim.empty or dest_rows.empty:
            continue
        dest = dest_rows.iloc[0]
        for _, row in clim.iterrows():
            mi = int(row['mois_num'])
            for lang in args.lang:
                k = f"{slug}:{mi}:{lang}"
                if k not in editorial or args.overwrite:
                    tasks.append((k, mi, row, dest, lang))

    already = (len(target_slugs) * 12 * len(args.lang)) - len(tasks)
    print(f"\n📊 {already} déjà ok | {len(tasks)} à générer | {len(editorial)} total")
    if not tasks:
        print("✅ Rien à générer.")
        return

    done = errors = 0
    for i, (k, mi, row, dest, lang) in enumerate(tasks, 1):
        month = MONTHS[lang][mi - 1]
        nom_col  = {'fr':'nom_fr','en':'nom_en','es':'nom_es','de':'nom_de'}.get(lang,'nom_en')
        pays_col = {'fr':'pays','en':'country_en','es':'country_es','de':'country_de'}.get(lang,'pays')
        nom  = str(dest.get(nom_col,  dest['nom_bare'])); nom  = dest['nom_bare'] if nom=='nan'  else nom
        pays = str(dest.get(pays_col, dest['pays']));      pays = dest['pays']    if pays=='nan' else pays

        user_prompt = USER_TPL[lang].format(
            nom=nom, pays=pays, month=month,
            tmin=row['tmin'], tmax=row['tmax'],
            rain=row['rain_pct'], sun=row['sun_h'],
            score=row['score'], ctx=ctx(row, lang)
        )

        try:
            text = call_api(args.key, SYSTEM[lang], user_prompt)
            editorial[k] = text
            save(editorial)  # ← sauvegarde immédiate après chaque succès
            done += 1
            pct = done / len(tasks) * 100
            print(f"  [{i}/{len(tasks)} {pct:.0f}%] ✅ {nom} {month} ({lang}): {text[:50]}…")
            time.sleep(DELAY_OK)

        except SystemExit:
            raise
        except Exception as e:
            errors += 1
            print(f"  [{i}/{len(tasks)}] ❌ {k}: {e}")
            # Continue sur les autres

    print(f"\n{'─'*55}")
    print(f"✅ {done} générés | ❌ {errors} erreurs | 📄 {len(editorial)} total")

if __name__ == '__main__':
    main()
