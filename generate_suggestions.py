#!/usr/bin/env python3
"""
generate_suggestions.py — Build data/suggestions.json from destinations.csv + climate.csv.

Replaces the manually-maintained suggestions.json with an auto-generated version.
Run after any change to destinations.csv or climate.csv.

Output schema (per slug key):
{
  "fr":      "nom_bare",         # FR display name (no article)
  "en":      "nom_en",
  "es":      "nom_es",
  "flag":    "xx",               # ISO country code
  "similar": [                   # top-5 climatically similar destinations
    {"slug": "...", "fr": "...", "en": "...", "flag": "...", "score_avg": 7.9},
    ...
  ]
}

Usage:
    python3 generate_suggestions.py
    python3 generate_suggestions.py --dry-run   # print stats only, no write
"""

import csv, json, math, sys, argparse
from pathlib import Path

ROOT = Path(__file__).parent


# ── Load data ─────────────────────────────────────────────────────────────────

def load_destinations():
    dests = {}
    with open(ROOT / 'data/destinations.csv', encoding='utf-8-sig') as f:
        for r in csv.DictReader(f):
            dests[r['slug_fr']] = r
    return dests


def load_climate():
    """Return {slug_fr: [monthly_row, ...]} — 12 rows per slug, ordered Jan–Dec."""
    by_slug = {}
    with open(ROOT / 'data/climate.csv', encoding='utf-8-sig') as f:
        for r in csv.DictReader(f):
            by_slug.setdefault(r['slug'], []).append(r)
    # Sort by month number if mois_num present
    for slug in by_slug:
        try:
            by_slug[slug].sort(key=lambda r: int(r.get('mois_num', 0)))
        except (ValueError, TypeError):
            pass
    return by_slug


# ── Similarity computation ────────────────────────────────────────────────────

def _profile(months):
    """Build climate profile vector: 12×tmax + 12×rain_pct + 12×sun_h."""
    try:
        return (
            [float(m['tmax'])     for m in months] +
            [float(m['rain_pct']) for m in months] +
            [float(m['sun_h'])    for m in months]
        )
    except (KeyError, ValueError):
        return None


def _cosine(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    na  = math.sqrt(sum(x * x for x in a))
    nb  = math.sqrt(sum(x * x for x in b))
    return dot / (na * nb) if na and nb else 0.0


def compute_similarities(climate):
    """Return {slug: [(score, similar_slug), ...]} top-5 per destination."""
    profiles = {}
    for slug, months in climate.items():
        if len(months) < 12:
            continue
        p = _profile(months)
        if p:
            profiles[slug] = p

    slugs = list(profiles.keys())
    similarities = {}
    for i, s1 in enumerate(slugs):
        sims = []
        for j, s2 in enumerate(slugs):
            if i == j:
                continue
            sims.append((_cosine(profiles[s1], profiles[s2]), s2))
        sims.sort(reverse=True)
        similarities[s1] = sims[:5]
    return similarities


# ── Score average ─────────────────────────────────────────────────────────────

def score_avg(months):
    """Mean of monthly scores from climate.csv (already normalised)."""
    scores = []
    for m in months:
        try:
            scores.append(float(m['score']))
        except (KeyError, ValueError):
            pass
    if not scores:
        return None
    return round(sum(scores) / len(scores), 1)


# ── Build output ──────────────────────────────────────────────────────────────

def build(dests, climate, similarities):
    output = {}
    skipped = []

    for slug, dest in sorted(dests.items()):
        if slug not in climate or len(climate[slug]) < 12:
            skipped.append(slug)
            continue

        # Root entry
        entry = {
            'fr':   dest.get('nom_bare') or dest.get('nom_fr', slug),
            'en':   dest.get('nom_en', slug),
            'es':   dest.get('nom_es') or dest.get('nom_en', slug),
            'flag': dest.get('flag', ''),
        }

        # Similar destinations
        similar = []
        for _sim_score, sim_slug in similarities.get(slug, []):
            sim_dest = dests.get(sim_slug)
            if not sim_dest:
                continue
            sim_months = climate.get(sim_slug, [])
            avg = score_avg(sim_months)
            similar.append({
                'slug':      sim_slug,
                'fr':        sim_dest.get('nom_bare') or sim_dest.get('nom_fr', sim_slug),
                'en':        sim_dest.get('nom_en', sim_slug),
                'flag':      sim_dest.get('flag', ''),
                'score_avg': avg if avg is not None else 0.0,
            })

        entry['similar'] = similar
        output[slug] = entry

    return output, skipped


# ── Entry point ───────────────────────────────────────────────────────────────

def main(dry_run=False):
    print("generate_suggestions.py")
    print(f"  Loading destinations…", end=' ', flush=True)
    dests = load_destinations()
    print(f"{len(dests)} entries")

    print(f"  Loading climate…", end=' ', flush=True)
    climate = load_climate()
    print(f"{len(climate)} slugs")

    print(f"  Computing similarities (cosine on tmax/rain/sun)…", end=' ', flush=True)
    similarities = compute_similarities(climate)
    print(f"{len(similarities)} profiles")

    print(f"  Building output…", end=' ', flush=True)
    output, skipped = build(dests, climate, similarities)
    print(f"{len(output)} entries")

    if skipped:
        print(f"  ⚠️  Skipped {len(skipped)} (no climate data): {', '.join(skipped[:5])}{'…' if len(skipped)>5 else ''}")

    out_path = ROOT / 'data' / 'suggestions.json'
    if dry_run:
        print(f"\n  [dry-run] Would write {out_path}")
        sample = list(output.items())[0]
        print(f"  Sample entry ({sample[0]}):", json.dumps(sample[1], ensure_ascii=False, indent=2)[:300])
    else:
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        size_kb = out_path.stat().st_size // 1024
        print(f"\n✅ Written: {out_path}  ({size_kb} KB, {len(output)} entries)")

    return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate data/suggestions.json from CSV sources')
    parser.add_argument('--dry-run', action='store_true', help='Print stats only, no file write')
    args = parser.parse_args()
    sys.exit(main(dry_run=args.dry_run))
