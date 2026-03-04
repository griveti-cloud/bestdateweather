#!/usr/bin/env python3
"""Batch refetch all destinations with mean precip_mm."""
import sys, os, time, json

DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, DIR)
os.chdir(DIR)

from fetch_climate import (load_destinations, process_destination,
                           DEFAULT_START, DEFAULT_END)

PROGRESS = os.path.join(DIR, 'data', 'p50_progress.json')

def load_prog():
    if os.path.exists(PROGRESS):
        return json.load(open(PROGRESS))
    return {'done': [], 'errors': [], 'started': None}

def save_prog(p):
    json.dump(p, open(PROGRESS, 'w'), indent=2)

dests = load_destinations()
all_slugs = list(dests.keys())
prog = load_prog()
if not prog.get('started'):
    prog['started'] = time.strftime('%Y-%m-%dT%H:%M:%S')

done_set = set(prog.get('done', []))
error_set = set(prog.get('errors', []))
remaining = [s for s in all_slugs if s not in done_set and s not in error_set]

print(f"Refetch: {len(remaining)} remaining / {len(all_slugs)} total", flush=True)

for i, slug in enumerate(remaining):
    n = len(done_set) + i + 1
    print(f"[{n}/{len(all_slugs)}] {slug}", end='', flush=True)
    try:
        ok = process_destination(slug, dests[slug], DEFAULT_START, DEFAULT_END,
                                 preview_only=False, force=True)
        if ok:
            prog['done'].append(slug)
            done_set.add(slug)
        else:
            prog['errors'].append(slug)
            error_set.add(slug)
    except Exception as e:
        print(f"  ERR: {e}", flush=True)
        prog['errors'].append(slug)
        error_set.add(slug)

    save_prog(prog)
    time.sleep(1.5)

print(f"\nDone: {len(prog['done'])} ok, {len(prog['errors'])} errors", flush=True)
