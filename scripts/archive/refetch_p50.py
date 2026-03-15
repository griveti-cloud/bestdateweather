#!/usr/bin/env python3
"""
refetch_p50.py — Resumable batch re-fetch of all climate data using P50 (median).

Wraps fetch_climate.py's process_destination() with progress tracking.
Safe to interrupt and restart — picks up where it left off.

Usage:
  python3 refetch_p50.py              # resume or start batch
  python3 refetch_p50.py --reset      # clear progress, start fresh
  python3 refetch_p50.py --status     # show progress without fetching
"""

import json, os, sys, time
from datetime import datetime

DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, DIR)

from fetch_climate import (
    load_destinations, process_destination,
    DEFAULT_START, DEFAULT_END
)

PROGRESS_FILE = os.path.join(DIR, 'data', 'p50_progress.json')
DELAY_BETWEEN = 0.5  # seconds between API calls (avoid Open-Meteo 429)


def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, encoding='utf-8') as f:
            return json.load(f)
    return {'done': [], 'errors': [], 'started': None}


def save_progress(prog):
    with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
        json.dump(prog, f, indent=2, ensure_ascii=False)


def main():
    args = sys.argv[1:]

    if '--status' in args:
        prog = load_progress()
        total_dests = len(load_destinations())
        done = len(prog.get('done', []))
        errors = len(prog.get('errors', []))
        remaining = total_dests - done - errors
        print(f"P50 re-fetch progress:")
        print(f"  Started:   {prog.get('started', 'never')}")
        print(f"  Done:      {done}/{total_dests}")
        print(f"  Errors:    {errors}")
        print(f"  Remaining: {remaining}")
        if prog.get('errors'):
            print(f"  Error slugs: {', '.join(prog['errors'][:20])}")
        return

    if '--reset' in args:
        if os.path.exists(PROGRESS_FILE):
            os.remove(PROGRESS_FILE)
            print("Progress reset.")
        else:
            print("No progress file to reset.")
        if '--reset' == args[-1]:
            return

    dests = load_destinations()
    all_slugs = list(dests.keys())
    prog = load_progress()

    if not prog.get('started'):
        prog['started'] = datetime.now().isoformat()

    done_set = set(prog.get('done', []))
    error_set = set(prog.get('errors', []))
    remaining = [s for s in all_slugs if s not in done_set and s not in error_set]

    print(f"P50 re-fetch — {len(all_slugs)} destinations")
    print(f"  Already done: {len(done_set)} | Errors: {len(error_set)} | Remaining: {len(remaining)}")
    print(f"  Delay: {DELAY_BETWEEN}s | Est. time: ~{len(remaining) * (DELAY_BETWEEN + 3) / 60:.0f} min")
    print()

    if not remaining:
        print("✅ All destinations already processed!")
        if error_set:
            print(f"⚠️  {len(error_set)} errors to review: {', '.join(sorted(error_set)[:20])}")
        return

    success = 0
    errors = 0
    start_time = time.time()

    for i, slug in enumerate(remaining):
        pct = (len(done_set) + i) / len(all_slugs) * 100
        elapsed = time.time() - start_time
        rate = (i + 1) / max(elapsed, 1)  # slugs/sec
        eta = (len(remaining) - i - 1) / max(rate, 0.01) / 60

        print(f"[{len(done_set)+i+1}/{len(all_slugs)}] ({pct:.0f}%) {slug}  (ETA: {eta:.0f}min)")

        try:
            ok = process_destination(
                slug, dests[slug],
                DEFAULT_START, DEFAULT_END,
                preview_only=False, force=True
            )
            if ok:
                prog['done'].append(slug)
                done_set.add(slug)
                success += 1
            else:
                prog['errors'].append(slug)
                error_set.add(slug)
                errors += 1
        except Exception as e:
            print(f"  ❌ Exception: {e}")
            prog['errors'].append(slug)
            error_set.add(slug)
            errors += 1

        # Save progress after every destination
        save_progress(prog)

        # Rate limit
        if i < len(remaining) - 1:
            time.sleep(DELAY_BETWEEN)

    elapsed_total = (time.time() - start_time) / 60
    print(f"\n{'─' * 50}")
    print(f"Batch complete: {success} OK / {errors} errors in {elapsed_total:.1f} min")
    print(f"Total progress: {len(done_set)}/{len(all_slugs)} destinations")

    if error_set:
        print(f"\n⚠️  Error slugs ({len(error_set)}):")
        for s in sorted(error_set):
            print(f"  - {s}")
        print("\nTo retry errors: remove them from data/p50_progress.json 'errors' list and re-run.")


if __name__ == '__main__':
    main()
