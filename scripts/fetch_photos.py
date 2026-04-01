#!/usr/bin/env python3
"""
fetch_photos.py — Fetch Unsplash hero photos for all destinations
Resumable: skips slugs already in destination_photos.csv
Rate limit: 50 req/h (demo) → sleeps automatically

Selection: picks the best photo from top-10 results, scored on:
  - Name/city mention in tags or description (location clarity)
  - Likes (quality signal)
  - Avoids portraits/food (landscape/cityscape preferred)

Usage:
  UNSPLASH_KEY="your_key" python3 scripts/fetch_photos.py
  UNSPLASH_KEY="your_key" python3 scripts/fetch_photos.py --dry-run
"""

import csv, json, os, sys, time, urllib.request, urllib.parse

UNSPLASH_KEY = os.environ.get("UNSPLASH_KEY", "")
DEST_CSV     = "data/destinations.csv"
PHOTOS_CSV   = "data/destination_photos.csv"
SLEEP_SEC    = 75   # safe margin for 50 req/h demo key

SKIP_TAGS = {'portrait','person','people','food','dish','restaurant',
             'interior','indoor','bedroom','cooking','meal'}

def score_photo(photo, nom_en, country_en):
    """Score a photo for how well it represents a destination visually."""
    score = 0

    # 1. Location match in tags — strongest signal
    tags = [t.get('title','').lower() for t in photo.get('tags', [])]
    nom_lower = nom_en.lower()
    country_lower = (country_en or '').lower()
    if any(nom_lower in t for t in tags):
        score += 40
    if any(country_lower in t for t in tags):
        score += 10

    # 2. Location match in description/alt
    desc = (photo.get('description') or photo.get('alt_description') or '').lower()
    if nom_lower in desc:
        score += 20
    if country_lower in desc:
        score += 5

    # 3. Likes (popularity = quality signal) — log scale
    likes = photo.get('likes', 0)
    if likes > 500:   score += 20
    elif likes > 100: score += 12
    elif likes > 30:  score += 6

    # 4. Penalize portrait/food tags
    if any(t in SKIP_TAGS for t in tags):
        score -= 30

    # 5. Prefer landscape orientation
    w = photo.get('width', 1)
    h = photo.get('height', 1)
    if w > h * 1.2:  # clearly landscape
        score += 5

    return score

def search_unsplash(query, nom_en, country_en, access_key):
    """Search Unsplash, return best-scored landscape photo or None."""
    params = urllib.parse.urlencode({
        "query": query,
        "per_page": 10,
        "orientation": "landscape",
        "order_by": "relevant",
    })
    url = f"https://api.unsplash.com/search/photos?{params}"
    req = urllib.request.Request(url, headers={
        "Authorization": f"Client-ID {access_key}",
        "Accept-Version": "v1",
    })
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            remaining = r.headers.get("X-Ratelimit-Remaining", "?")
            data = json.loads(r.read())
        results = data.get("results", [])
        if not results:
            return None, remaining

        # Score all results, pick best
        scored = sorted(
            [(score_photo(p, nom_en, country_en), p) for p in results],
            key=lambda x: -x[0]
        )
        best_score, photo = scored[0]

        # Reject if score too low (no location signal at all)
        if best_score < 5:
            # Try second query without suffix
            fallback_query = f"{nom_en} {country_en}"
            if fallback_query.strip() != query.strip():
                return search_unsplash(fallback_query, nom_en, country_en, access_key)
            return None, remaining

        photo_id  = photo["id"]
        url_cdn   = photo["urls"]["raw"] + "&w=1400&q=85&fm=jpg&fit=crop&crop=entropy"
        credit_name = photo["user"]["name"]
        username    = photo["user"]["username"]
        utm = "utm_source=bestdateweather&utm_medium=referral"
        profile_url   = f"https://unsplash.com/@{username}?{utm}"
        photo_url_attr = f"https://unsplash.com/photos/{photo_id}?{utm}"

        return {
            "url":         url_cdn,
            "credit_name": credit_name,
            "credit_url":  profile_url,
            "photo_url":   photo_url_attr,
            "_score":      best_score,
            "_likes":      photo.get("likes", 0),
        }, remaining

    except Exception as e:
        print(f"  [ERROR] {e}")
        return None, "?"

def build_query(dest):
    """Build search query with location-identifying suffix."""
    nom     = dest.get("nom_en") or dest.get("nom_bare") or dest.get("nom_fr", "")
    country = dest.get("country_en") or dest.get("pays", "")
    is_mountain = dest.get("mountain", "False").strip() == "True"
    is_coastal  = dest.get("coastal",  "False").strip() == "True"
    is_tropical = dest.get("tropical", "False").strip() == "True"

    if is_mountain:
        suffix = "mountain snow"
    elif is_coastal and is_tropical:
        suffix = "beach turquoise water"
    elif is_coastal:
        suffix = "sea coast"
    else:
        suffix = "city landmark"

    return f"{nom} {country} {suffix}".strip(), nom, country

def load_existing(csv_path):
    done = {}
    if not os.path.exists(csv_path):
        return done
    with open(csv_path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            done[row["slug_fr"]] = row
    return done

def load_destinations(csv_path):
    with open(csv_path, encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))

def main():
    dry_run = "--dry-run" in sys.argv
    if not UNSPLASH_KEY:
        print("❌ UNSPLASH_KEY not set. Usage: UNSPLASH_KEY=xxx python3 scripts/fetch_photos.py")
        sys.exit(1)

    dests    = load_destinations(DEST_CSV)
    existing = load_existing(PHOTOS_CSV)

    to_process = [d for d in dests if d["slug_fr"] not in existing]
    print(f"Total: {len(dests)} | Done: {len(existing)} | Remaining: {len(to_process)}")

    if dry_run:
        print("\n[DRY RUN] First 5 queries:")
        for d in to_process[:5]:
            q, nom, country = build_query(d)
            print(f"  {d['slug_fr']:25} → {q!r}")
        return

    file_exists = os.path.exists(PHOTOS_CSV)
    with open(PHOTOS_CSV, "a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "slug_fr","photo_url","photo_credit_name","photo_credit_url","photo_page_url"
        ])
        if not file_exists:
            writer.writeheader()

        for i, dest in enumerate(to_process, 1):
            slug    = dest["slug_fr"]
            query, nom_en, country_en = build_query(dest)
            print(f"[{i:3}/{len(to_process)}] {slug:30} query={query!r} ... ", end="", flush=True)

            photo, remaining = search_unsplash(query, nom_en, country_en, UNSPLASH_KEY)

            if photo:
                writer.writerow({
                    "slug_fr":            slug,
                    "photo_url":          photo["url"],
                    "photo_credit_name":  photo["credit_name"],
                    "photo_credit_url":   photo["credit_url"],
                    "photo_page_url":     photo.get("photo_url", ""),
                })
                f.flush()
                print(f"✓ score={photo['_score']} likes={photo['_likes']} (remaining={remaining})")
            else:
                writer.writerow({
                    "slug_fr": slug, "photo_url": "",
                    "photo_credit_name": "", "photo_credit_url": "", "photo_page_url": ""
                })
                f.flush()
                print(f"✗ no result (remaining={remaining})")

            # Rate limit guard
            try:
                if int(remaining) <= 2:
                    print(f"⏳ Rate limit low, sleeping 3600s ...")
                    time.sleep(3600)
                else:
                    time.sleep(SLEEP_SEC)
            except (ValueError, TypeError):
                time.sleep(SLEEP_SEC)

    print(f"\n✅ Done. {PHOTOS_CSV} updated.")

if __name__ == "__main__":
    main()
