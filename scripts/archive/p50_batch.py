#!/usr/bin/env python3
"""Process exactly N destinations for P50 re-fetch, then exit."""
import json, sys, os, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fetch_climate import load_destinations, process_destination, DEFAULT_START, DEFAULT_END

N = int(sys.argv[1]) if len(sys.argv) > 1 else 5
PROGRESS_FILE = 'data/p50_progress.json'

prog = json.load(open(PROGRESS_FILE))
dests = load_destinations()
done_set = set(prog['done'])
err_set = set(prog.get('errors', []))
remaining = [s for s in dests if s not in done_set and s not in err_set]

batch = remaining[:N]
if not batch:
    print(f"✅ All done! {len(done_set)}/512")
    sys.exit(0)

print(f"Batch: {len(batch)} | Done: {len(done_set)} | Remaining: {len(remaining)}")
ok_count = 0
for i, slug in enumerate(batch):
    try:
        ok = process_destination(slug, dests[slug], DEFAULT_START, DEFAULT_END,
                                  preview_only=False, force=True)
        if ok:
            prog['done'].append(slug)
            ok_count += 1
            print(f"  ✓ {slug} ({len(prog['done'])}/512)")
        else:
            prog['errors'].append(slug)
            print(f"  ✗ {slug}")
    except Exception as e:
        prog['errors'].append(slug)
        print(f"  ❌ {slug}: {e}")
    json.dump(prog, open(PROGRESS_FILE, 'w'), indent=2, ensure_ascii=False)
    if i < len(batch) - 1:
        time.sleep(0.3)

print(f"\nBatch done: {ok_count}/{len(batch)} OK | Total: {len(prog['done'])}/512 | Remaining: {len(remaining)-len(batch)}")
