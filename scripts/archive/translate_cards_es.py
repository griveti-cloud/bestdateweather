#!/usr/bin/env python3
"""Translate cards_en.csv to Spanish using Claude API, with resume support."""
import csv, json, os, time, sys
import anthropic

DATA = 'data'
INPUT = f'{DATA}/cards_en.csv'
OUTPUT = f'{DATA}/cards_es.csv'
PROGRESS = f'{DATA}/cards_es_progress.json'
BATCH = 40

import os
os.environ['ANTHROPIC_API_KEY'] = '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'
client = anthropic.Anthropic()

rows = list(csv.DictReader(open(INPUT, encoding='utf-8-sig')))
total = len(rows)

# Load progress
done = {}
if os.path.exists(PROGRESS):
    done = json.load(open(PROGRESS))
    print(f"Resuming: {len(done)}/{total} rows done")

SYSTEM = """You are a professional travel content translator. Translate English travel card content to Spanish (Latin American, neutral).

Rules:
- Translate `title` and `text` fields only. Keep `slug` and `icon` unchanged.
- `title` = short label (2-5 words), translate naturally (e.g. "Beach & Surfing" → "Playa y surf")
- `text` = 1-2 sentences with season + key highlights. Translate faithfully, keep proper nouns (place names, brand names) in English/original language.
- Keep the em-dash (—) format: "Época — descripción."
- Output ONLY valid JSON array, no markdown, no explanation.
"""

def translate_batch(batch_rows):
    items = [{"slug": r['slug'], "icon": r['icon'], "title": r['title'], "text": r['text']} for r in batch_rows]
    prompt = f"""Translate these {len(items)} travel cards from English to Spanish. Return a JSON array with the same structure.

Input:
{json.dumps(items, ensure_ascii=False, indent=2)}

Output (JSON array only):"""
    
    resp = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=4096,
        system=SYSTEM,
        messages=[{"role": "user", "content": prompt}]
    )
    text = resp.content[0].text.strip()
    # Strip markdown fences if present
    if text.startswith('```'):
        text = text.split('\n', 1)[1]
        text = text.rsplit('```', 1)[0]
    return json.loads(text)

# Process in batches
translated = list(done.values()) if done else []
pending = [r for i, r in enumerate(rows) if str(i) not in done]

print(f"Pending: {len(pending)} rows")

i = 0
while i < len(pending):
    batch = pending[i:i+BATCH]
    start_idx = len(done) + i
    print(f"Batch {i//BATCH + 1}/{(len(pending)+BATCH-1)//BATCH} (rows {start_idx}–{start_idx+len(batch)-1})...", end=' ', flush=True)
    
    try:
        results = translate_batch(batch)
        if len(results) != len(batch):
            print(f"⚠ Expected {len(batch)} got {len(results)}, skipping batch")
            i += BATCH
            continue
        
        for j, (orig, trans) in enumerate(zip(batch, results)):
            idx = str(rows.index(orig))
            done[idx] = {
                'slug': orig['slug'],
                'icon': orig['icon'],
                'title': trans.get('title', orig['title']),
                'text': trans.get('text', orig['text'])
            }
        
        json.dump(done, open(PROGRESS, 'w'), ensure_ascii=False)
        print(f"✓ ({len(done)}/{total})")
        i += BATCH
        time.sleep(0.5)
        
    except Exception as e:
        print(f"Error: {e}")
        print("Retrying in 5s...")
        time.sleep(5)

# Write final CSV
print(f"\nWriting {OUTPUT}...")
with open(OUTPUT, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=['slug', 'icon', 'title', 'text'])
    writer.writeheader()
    # Preserve original row order
    for i, orig in enumerate(rows):
        key = str(i)
        if key in done:
            writer.writerow(done[key])
        else:
            writer.writerow({'slug': orig['slug'], 'icon': orig['icon'], 
                           'title': orig['title'], 'text': orig['text']})

print(f"✅ Done: {OUTPUT}")
if os.path.exists(PROGRESS):
    os.remove(PROGRESS)
