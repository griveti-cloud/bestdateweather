#!/usr/bin/env python3
"""Micro-batch P50 re-fetch — processes N destinations then exits.
Designed to work within container execution time limits.

Usage: python3 refetch_p50_micro.py [N]    (default N=5)
"""
import json, os, sys, time

DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, DIR)
os.chdir(DIR)

from fetch_climate import load_destinations, process_destination, DEFAULT_START, DEFAULT_END

PROGRESS_FILE = os.path.join(DIR, 'data', 'p50_progress.json')

def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE) as f:
            return json.load(f)
    return {'done': [], 'errors': []}

def save_progress(prog):
    with open(PROGRESS_FILE, 'w') as f:
        json.dump(prog, f)

N = int(sys.argv[1]) if len(sys.argv) > 1 else 5

dests = load_destinations()
all_slugs = list(dests.keys())
prog = load_progress()
done_set = set(prog.get('done', []))
error_set = set(prog.get('errors', []))
remaining = [s for s in all_slugs if s not in done_set and s not in error_set]

if not remaining:
    print(f"✅ All {len(all_slugs)} destinations done! Errors: {len(error_set)}")
    sys.exit(0)

batch = remaining[:N]
print(f"P50 micro-batch: {len(batch)} of {len(remaining)} remaining ({len(done_set)}/{len(all_slugs)} done)")

ok = 0
for slug in batch:
    try:
        result = process_destination(slug, dests[slug], DEFAULT_START, DEFAULT_END, preview_only=False, force=True)
        if result:
            prog.setdefault('done', []).append(slug)
            done_set.add(slug)
            ok += 1
        else:
            prog.setdefault('errors', []).append(slug)
    except Exception as e:
        print(f"  ❌ {slug}: {e}")
        prog.setdefault('errors', []).append(slug)
    save_progress(prog)
    time.sleep(1)

print(f"\n✅ Batch: {ok}/{len(batch)} | Total: {len(done_set)}/{len(all_slugs)} | Remaining: {len(remaining)-len(batch)}")
