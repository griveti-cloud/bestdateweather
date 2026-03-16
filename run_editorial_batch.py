#!/usr/bin/env python3
"""Lance generate_editorial.py par batch de N destinations, relançable à l'infini."""
import subprocess, json, csv, sys, time

KEY = "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"
BATCH = 25  # destinations par batch

def get_incomplete():
    data = json.load(open('data/editorial.json'))
    with open('data/destinations.csv', encoding='utf-8-sig') as f:
        rows = list(csv.DictReader(f))
    claude_orig = {'agadir','alicante','banjul','cabo-san-lucas','canaries','cap-vert',
    'casablanca','chypre','dakar','djerba','essaouira','fuerteventura','gran-canaria',
    'guanajuato','harare','honolulu','hurghada','jordanie','la-gomera','la-palma',
    'larnaca','lilongwe','lima','loreto-mexique','los-angeles','maputo','marsa-alam',
    'namibie','oaxaca','pantelleria','paphos','paris','perou','petra','puerto-escondido',
    'puerto-vallarta','saint-thomas','sal','salalah','samos','san-miguel-de-allende',
    'santa-barbara','santiago','socotra','tanzanie','tel-aviv','tofo','trinidad-cuba',
    'turks-et-caicos','valletta','windhoek'}
    priority = sorted(r['slug_fr'] for r in rows
                      if r.get('booking_dest_id','').strip()
                      and r['slug_fr'] not in claude_orig)
    sc = {}
    for k in data:
        s = k.split(':')[0]
        if s in set(priority): sc[s] = sc.get(s,0)+1
    return [s for s in priority if sc.get(s,0) < 48], len([s for s in priority if sc.get(s,0)==48])

incomplete, done = get_incomplete()
total_priority = done + len(incomplete)
print(f"\n{'='*60}")
print(f"État : {done}/{total_priority} complètes | {len(incomplete)} restantes")
print(f"Batches de {BATCH} → {len(incomplete)//BATCH + 1} itérations")
print(f"{'='*60}\n")

batch_num = 0
while True:
    incomplete, done = get_incomplete()
    if not incomplete:
        print(f"\n✅ TERMINÉ ! {done}/504 destinations complètes.")
        break

    batch = incomplete[:BATCH]
    batch_num += 1
    pct = done / total_priority * 100
    print(f"[Batch {batch_num}] {done}/{total_priority} ({pct:.0f}%) — {len(batch)} destinations : {batch[0]}...{batch[-1]}")

    # Écrire fichier temporaire
    with open('/tmp/batch_slugs.txt', 'w') as f:
        f.write('\n'.join(batch))

    result = subprocess.run(
        ['python3', 'generate_editorial.py',
         '--key', KEY,
         '--dest-file', '/tmp/batch_slugs.txt',
         '--lang', 'fr', 'en', 'es', 'de'],
        capture_output=True, text=True, timeout=300
    )

    # Compter succès dans output
    ok = result.stdout.count('✅')
    err = result.stdout.count('❌')
    print(f"  → {ok} générés, {err} erreurs")

    if result.returncode != 0 and '❌ CLÉ API INVALIDE' in result.stdout:
        print("❌ Clé API invalide — arrêt.")
        sys.exit(1)

    # Pause courte entre batches
    time.sleep(2)

# Résumé final
incomplete, done = get_incomplete()
print(f"\n📊 Final : {done}/504 complètes")
