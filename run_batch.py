#!/usr/bin/env python3
"""Run refetch in small batches to avoid timeout."""
import json, os, sys, time
DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, DIR)
from fetch_climate import load_destinations, process_destination, DEFAULT_START, DEFAULT_END

PROGRESS_FILE = os.path.join(DIR, 'data', 'p50_progress.json')
BATCH_SIZE = int(sys.argv[1]) if len(sys.argv) > 1 else 40
DELAY = 1.5

def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, encoding='utf-8') as f:
            return json.load(f)
    return {'done': [], 'errors': [], 'started': None}

def save_progress(prog):
    with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
        json.dump(prog, f, indent=2, ensure_ascii=False)

dests = load_destinations()
all_slugs = list(dests.keys())
prog = load_progress()
done_set = set(prog.get('done', []))
error_set = set(prog.get('errors', []))
remaining = [s for s in all_slugs if s not in done_set and s not in error_set]

batch = remaining[:BATCH_SIZE]
print(f"Batch of {len(batch)} / {len(remaining)} remaining ({len(done_set)} done, {len(error_set)} errors)")

ok = err = 0
for i, slug in enumerate(batch):
    print(f"  [{len(done_set)+i+1}/{len(all_slugs)}] {slug}", end=" ", flush=True)
    try:
        result = process_destination(slug, dests[slug], DEFAULT_START, DEFAULT_END, preview_only=False, force=True)
        if result:
            prog['done'].append(slug)
            done_set.add(slug)
            ok += 1
            print("✓")
        else:
            prog['errors'].append(slug)
            error_set.add(slug)
            err += 1
            print("✗")
    except Exception as e:
        prog['errors'].append(slug)
        error_set.add(slug)
        err += 1
        print(f"✗ {e}")
    save_progress(prog)
    if i < len(batch) - 1:
        time.sleep(DELAY)

print(f"\nBatch done: {ok} OK, {err} errors")
print(f"Total: {len(done_set)}/{len(all_slugs)} done, {len(error_set)} errors, {len(all_slugs)-len(done_set)-len(error_set)} remaining")
