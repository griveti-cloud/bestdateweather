"""
gen_hero_sub_es.py — Generate hero_sub_es for all destinations via Claude API.

Usage:
    ANTHROPIC_API_KEY=sk-ant-... python3 gen_hero_sub_es.py

Reads:  data/destinations.csv  (hero_sub_en + hero_sub as inputs)
Writes: data/destinations.csv  (hero_sub_es filled in-place)

Progress saved in data/hero_sub_es_progress.json — resumable.
Rate-limited to ~50 req/min to stay safe.
"""

import csv, json, os, time, pathlib, sys
import anthropic

PROGRESS_FILE = pathlib.Path('data/hero_sub_es_progress.json')
CSV_FILE = pathlib.Path('data/destinations.csv')
BATCH_SIZE = 20          # destinations per API call
SLEEP_BETWEEN = 1.5      # seconds between batches

def load_progress():
    if PROGRESS_FILE.exists():
        return json.loads(PROGRESS_FILE.read_text())
    return {}

def save_progress(p):
    PROGRESS_FILE.write_text(json.dumps(p, ensure_ascii=False, indent=2))

def make_prompt(batch):
    """batch = list of {slug, nom_en, hero_sub_en} dicts"""
    items = '\n'.join(
        f'{i+1}. [{r["slug"]}] {r["src"]}'
        for i, r in enumerate(batch)
    )
    return f"""Tu es rédacteur pour un site de météo voyage. Traduis ces sous-titres héros de l'anglais vers l'espagnol.

Règles :
- Traduction naturelle, pas littérale — adapte le style si nécessaire
- Garde le même ton (accrocheur, concis, informatif)
- Conserve les chiffres, les mois et les noms propres tels quels
- Maximum ~200 caractères par ligne
- Format : JSON array avec "slug" et "hero_sub_es" seulement

Entrées :
{items}

Réponds UNIQUEMENT avec un JSON array, sans markdown ni commentaire :
[{{"slug": "...", "hero_sub_es": "..."}}, ...]"""

def translate_batch(client, batch):
    prompt = make_prompt(batch)
    msg = client.messages.create(
        model='claude-haiku-4-5-20251001',
        max_tokens=2000,
        messages=[{'role': 'user', 'content': prompt}]
    )
    raw = msg.content[0].text.strip()
    # Strip markdown fences if present
    if raw.startswith('```'):
        raw = raw.split('\n', 1)[1].rsplit('```', 1)[0].strip()
    results = json.loads(raw)
    return {r['slug']: r['hero_sub_es'] for r in results}

def main():
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        print('ERROR: ANTHROPIC_API_KEY not set')
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)

    # Load CSV
    with open(CSV_FILE, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)

    print(f'Loaded {len(rows)} destinations')

    # Load progress
    progress = load_progress()
    print(f'Already done: {len(progress)} destinations')

    # Build work queue — skip already done, skip those with no EN source
    todo = []
    for r in rows:
        slug = r['slug_fr']
        if slug in progress:
            continue
        src = r.get('hero_sub_en', '').strip() or r.get('hero_sub', '').strip()
        if not src:
            progress[slug] = ''  # nothing to translate
            continue
        todo.append({'slug': slug, 'src': src})

    print(f'To translate: {len(todo)}')

    # Process in batches
    for i in range(0, len(todo), BATCH_SIZE):
        batch = todo[i:i+BATCH_SIZE]
        print(f'Batch {i//BATCH_SIZE + 1}/{(len(todo)-1)//BATCH_SIZE + 1} ({len(batch)} items)...', end=' ', flush=True)
        try:
            results = translate_batch(client, batch)
            for item in batch:
                slug = item['slug']
                progress[slug] = results.get(slug, '')
                if not progress[slug]:
                    print(f'[WARN: {slug} got empty result]', end=' ')
            save_progress(progress)
            print('✓')
        except Exception as ex:
            print(f'ERROR: {ex}')
            print('Saving progress and retrying next run...')
            save_progress(progress)
            # Don't crash — let next run resume
            time.sleep(5)
            continue

        time.sleep(SLEEP_BETWEEN)

    # Write back to CSV
    print('Writing CSV...', end=' ')
    for r in rows:
        slug = r['slug_fr']
        if slug in progress:
            r['hero_sub_es'] = progress[slug]

    with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    filled = sum(1 for r in rows if r.get('hero_sub_es', '').strip())
    print(f'✓ — {filled}/{len(rows)} hero_sub_es filled')

    # Clean up progress file
    PROGRESS_FILE.unlink(missing_ok=True)
    print('Done.')

if __name__ == '__main__':
    main()
