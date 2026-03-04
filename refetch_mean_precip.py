#!/usr/bin/env python3
"""
refetch_mean_precip.py — Refetch ALL destinations to update precip_mm from P50 → mean.
=======================================================================================

Usage:
  python3 refetch_mean_precip.py              # resume or start batch
  python3 refetch_mean_precip.py --reset      # clear progress, start fresh
  python3 refetch_mean_precip.py --status     # show progress without fetching
  python3 refetch_mean_precip.py --finalize   # recalculate bounds + regenerate scores

Why:
  precip_mm was P50 of ALL daily values (including 0mm dry days), making it
  near-zero for any month with <50% rain days. Now uses mean (sum/days),
  giving realistic values like Paris Jan = 2.3mm/j instead of 0.5mm/j.

  Combined with the new bidirectional effective_rain_pct() in scoring.py,
  this allows rain_pct to be adjusted by actual intensity:
  - Light rain (bruine): effective rain_pct reduced → better score
  - Heavy rain (storms): effective rain_pct increased → worse score

After refetch completes:
  1. Run: python3 refetch_mean_precip.py --finalize
     (recalculates GLOBAL_RAW_BOUNDS, regenerates all pages)
  2. Or manually:
     python3 regenerate_scores.py
     python3 generate_pages.py --lang fr
     python3 generate_pages.py --lang en
     python3 generate_classements.py
     python3 generate_piliers.py
     python3 generate_comparatifs.py
     python3 generate_index_hub.py
"""

import json, os, sys, time, csv, subprocess
from datetime import datetime

DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, DIR)

from fetch_climate import (
    load_destinations, fetch_daily, compute_monthly_averages,
    auto_classify, score_destination, format_csv_rows,
    remove_from_climate_csv, append_to_climate_csv,
    DEFAULT_START, DEFAULT_END
)

PROGRESS_FILE = os.path.join(DIR, 'data', 'refetch_mean_progress.json')
DELAY = 3.0  # seconds between API calls


def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE) as f:
            return json.load(f)
    return {'done': [], 'errors': [], 'started': None}


def save_progress(prog):
    with open(PROGRESS_FILE, 'w') as f:
        json.dump(prog, f, indent=2, ensure_ascii=False)


def show_status():
    prog = load_progress()
    total = len(load_destinations())
    done = len(prog.get('done', []))
    errs = len(prog.get('errors', []))
    print(f"Mean-precip refetch progress:")
    print(f"  Started:   {prog.get('started', 'never')}")
    print(f"  Done:      {done}/{total}")
    print(f"  Errors:    {errs}")
    print(f"  Remaining: {total - done - errs}")
    if prog.get('errors'):
        print(f"  Error slugs: {', '.join(prog['errors'][:30])}")


def finalize():
    """Recalculate bounds and regenerate all pages."""
    print("=== Finalization: recalculating scores and regenerating pages ===\n")

    # 1. Recalculate GLOBAL_RAW_BOUNDS (2-pass convergence)
    print("Step 1: Recalculating scores (may need 2 passes for convergence)...")
    for pass_num in range(3):
        # Force reimport scoring with fresh bounds
        if 'scoring' in sys.modules:
            del sys.modules['scoring']
        from scoring import compute_scores, raw_score, GLOBAL_RAW_BOUNDS

        csv_path = os.path.join(DIR, 'data', 'climate.csv')
        from collections import OrderedDict
        with open(csv_path, encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            all_rows = list(reader)

        grouped = OrderedDict()
        for r in all_rows:
            grouped.setdefault(r['slug'], []).append(r)

        changes = 0
        for slug, rows in grouped.items():
            if len(rows) != 12:
                continue
            months_input = [{
                'cls': r['classe'], 'tmax': float(r['tmax']),
                'rain_pct': float(r['rain_pct']), 'sun_h': float(r['sun_h']),
                'precip_mm': float(r['precip_mm']) if r.get('precip_mm', '') else None
            } for r in rows]
            new_scores = compute_scores(months_input, slug)
            for r, ns in zip(rows, new_scores):
                new_s = str(ns['score_10'])
                if r['score'] != new_s:
                    changes += 1
                    r['score'] = new_s

        with open(csv_path, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator='\r\n')
            writer.writeheader()
            for rows in grouped.values():
                writer.writerows(rows)

        print(f"  Pass {pass_num + 1}: {changes} scores updated")
        if changes == 0:
            break

    # 2. Regenerate all pages
    print("\nStep 2: Regenerating pages...")
    scripts = [
        ['python3', 'regenerate_scores.py'],
        ['python3', 'generate_pages.py', '--lang', 'fr'],
        ['python3', 'generate_pages.py', '--lang', 'en'],
        ['python3', 'generate_classements.py'],
        ['python3', 'generate_piliers.py'],
        ['python3', 'generate_comparatifs.py'],
        ['python3', 'generate_index_hub.py'],
    ]
    for cmd in scripts:
        print(f"  Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, cwd=DIR, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"    ❌ Error: {result.stderr[:200]}")
        else:
            # Print last non-empty line of output
            lines = [l for l in result.stdout.strip().split('\n') if l.strip()]
            if lines:
                print(f"    {lines[-1]}")

    # 3. Regenerate fiche-scores.js
    print("\nStep 3: Regenerating js/fiche-scores.js...")
    dests = {}
    with open(os.path.join(DIR, 'data/destinations.csv'), encoding='utf-8-sig') as f:
        for r in csv.DictReader(f):
            dests[r['slug_fr']] = (r['lat'], r['lon'])

    scores = {}
    with open(os.path.join(DIR, 'data/climate.csv'), encoding='utf-8-sig') as f:
        for r in csv.DictReader(f):
            slug = r['slug']
            if slug not in scores:
                scores[slug] = [None] * 12
            mi = int(r['mois_num']) - 1
            scores[slug][mi] = round(float(r['score']) * 10)

    fiche = {}
    for slug, coords in dests.items():
        if slug in scores and all(s is not None for s in scores[slug]):
            key = f"{coords[0]},{coords[1]}"
            fiche[key] = scores[slug]

    js_path = os.path.join(DIR, 'js/fiche-scores.js')
    with open(js_path, 'w') as f:
        f.write(f"var FICHE_SCORES = {json.dumps(fiche, separators=(',', ':'))};\n")
    print(f"  {len(fiche)} destinations")

    # 4. Copy core.js to core.min.js
    import shutil
    shutil.copy2(os.path.join(DIR, 'js/core.js'), os.path.join(DIR, 'js/core.min.js'))
    print("  core.min.js updated")

    print("\n✅ Finalization complete. Review changes and commit.")


def main():
    args = sys.argv[1:]

    if '--status' in args:
        show_status()
        return

    if '--finalize' in args:
        finalize()
        return

    if '--reset' in args:
        if os.path.exists(PROGRESS_FILE):
            os.remove(PROGRESS_FILE)
            print("Progress reset.")
        return

    dests = load_destinations()
    all_slugs = list(dests.keys())
    prog = load_progress()

    if not prog.get('started'):
        prog['started'] = datetime.now().isoformat()

    done = set(prog.get('done', []))
    errors = set(prog.get('errors', []))
    remaining = [s for s in all_slugs if s not in done and s not in errors]

    print(f"Mean-precip refetch — {len(all_slugs)} destinations")
    print(f"  Done: {len(done)} | Errors: {len(errors)} | Remaining: {len(remaining)}")
    print(f"  Delay: {DELAY}s | Est. time: ~{len(remaining) * (DELAY + 5) / 60:.0f} min\n")

    if not remaining:
        print("✅ All done! Run --finalize to regenerate scores and pages.")
        return

    ok = err = 0
    t0 = time.time()

    for i, slug in enumerate(remaining):
        d = dests[slug]
        pct = (len(done) + i) / len(all_slugs) * 100
        elapsed = time.time() - t0
        rate = (i + 1) / max(elapsed, 1)
        eta = (len(remaining) - i - 1) / max(rate, 0.01) / 60

        print(f"[{len(done)+i+1}/{len(all_slugs)}] ({pct:.0f}%) {slug}  (ETA: {eta:.0f}min)...",
              end=" ", flush=True)

        try:
            data = fetch_daily(d['lat'], d['lon'], DEFAULT_START, DEFAULT_END)
            monthly = compute_monthly_averages(data)
            classes = auto_classify(monthly, slug)
            scores = score_destination(monthly, classes, slug)
            remove_from_climate_csv(slug)
            rows = format_csv_rows(slug, monthly, classes, scores)
            append_to_climate_csv(rows)
            prog['done'].append(slug)
            done.add(slug)
            ok += 1
            # Show sample mm values
            mms = [str(m['precip_mm']) for m in monthly]
            print(f"✅ mm=[{','.join(mms)}]")
        except Exception as e:
            prog['errors'].append(slug)
            errors.add(slug)
            err += 1
            print(f"❌ {str(e)[:60]}")

        save_progress(prog)
        if i < len(remaining) - 1:
            time.sleep(DELAY)

    total_min = (time.time() - t0) / 60
    print(f"\n{'─' * 50}")
    print(f"Batch: {ok} OK / {err} errors in {total_min:.1f} min")
    print(f"Total: {len(done)}/{len(all_slugs)} destinations")

    if len(done) == len(all_slugs):
        print("\n✅ All destinations refetched! Run --finalize next.")
    elif errors:
        print(f"\n⚠️  {len(errors)} errors. Fix and re-run (errors are skipped).")


if __name__ == '__main__':
    main()
