#!/usr/bin/env python3
"""
fetch_photos.py — Fetch Unsplash hero photos for all destinations
Resumable: skips slugs already in destination_photos.csv
Rate limit: 50 req/h (demo) → sleeps automatically

Usage:
  UNSPLASH_KEY="your_key" python3 scripts/fetch_photos.py
  UNSPLASH_KEY="your_key" python3 scripts/fetch_photos.py --dry-run
"""

import csv, json, os, sys, time, urllib.request, urllib.parse

UNSPLASH_KEY = os.environ.get("UNSPLASH_KEY", "")
DEST_CSV     = "data/destinations.csv"
PHOTOS_CSV   = "data/destination_photos.csv"
RATE_LIMIT   = 50   # req/h demo
SLEEP_SEC    = 75   # sec between requests (safe margin: ~48 req/h)

def search_unsplash(query, access_key):
    """Search Unsplash, return best landscape photo or None."""
    params = urllib.parse.urlencode({
        "query": query,
        "per_page": 5,
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
        # Pick first result (Unsplash relevance sort)
        photo = results[0]
        photo_id = photo["id"]
        # Use raw URL with width param — stable, hotlink-allowed
        url_cdn = photo["urls"]["raw"] + "&w=1400&q=85&fm=jpg&fit=crop&crop=entropy"
        credit_name = photo["user"]["name"]
        credit_url  = f"https://unsplash.com/photos/{photo_id}"
        return {
            "url": url_cdn,
            "credit_name": f"{credit_name} via Unsplash",
            "credit_url": credit_url,
        }, remaining
    except Exception as e:
        print(f"  [ERROR] {e}")
        return None, "?"

def load_existing(csv_path):
    """Return set of slug_fr already processed."""
    done = {}
    if not os.path.exists(csv_path):
        return done
    with open(csv_path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            done[row["slug_fr"]] = row
    return done

def load_destinations(csv_path):
    rows = []
    with open(csv_path, encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            rows.append(row)
    return rows

def build_query(dest):
    """Build a good Unsplash search query from destination data."""
    nom = dest.get("nom_en") or dest.get("nom_bare") or dest.get("nom_fr", "")
    country = dest.get("country_en") or dest.get("pays", "")
    is_tropical = dest.get("tropical", "False").strip() == "True"
    is_mountain = dest.get("mountain", "False").strip() == "True"
    is_coastal  = dest.get("coastal", "False").strip() == "True"

    if is_coastal or is_tropical:
        suffix = "beach"
    elif is_mountain:
        suffix = "mountain landscape"
    else:
        suffix = "cityscape"

    return f"{nom} {country} {suffix}".strip()

def main():
    dry_run = "--dry-run" in sys.argv
    if not UNSPLASH_KEY:
        print("❌ UNSPLASH_KEY not set")
        sys.exit(1)

    dests   = load_destinations(DEST_CSV)
    existing = load_existing(PHOTOS_CSV)

    to_process = [d for d in dests if d["slug_fr"] not in existing]
    total = len(dests)
    done  = len(existing)
    todo  = len(to_process)

    print(f"Total: {total} | Already done: {done} | Remaining: {todo}")
    if dry_run:
        print("[DRY RUN] First 3 queries:")
        for d in to_process[:3]:
            print(f"  {d['slug_fr']} → {build_query(d)}")
        return

    # Write header if file doesn't exist
    file_exists = os.path.exists(PHOTOS_CSV)
    with open(PHOTOS_CSV, "a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["slug_fr","photo_url","photo_credit_name","photo_credit_url"])
        if not file_exists:
            writer.writeheader()

        for i, dest in enumerate(to_process):
            slug = dest["slug_fr"]
            query = build_query(dest)
            print(f"[{done+i+1}/{total}] {slug} — {query}", end=" ... ", flush=True)

            photo, remaining = search_unsplash(query, UNSPLASH_KEY)

            if photo:
                writer.writerow({
                    "slug_fr": slug,
                    "photo_url": photo["url"],
                    "photo_credit_name": photo["credit_name"],
                    "photo_credit_url": photo["credit_url"],
                })
                f.flush()
                print(f"✓ (remaining: {remaining})")
            else:
                # Write empty row so we don't retry (uses gradient fallback)
                writer.writerow({
                    "slug_fr": slug,
                    "photo_url": "",
                    "photo_credit_name": "",
                    "photo_credit_url": "",
                })
                f.flush()
                print(f"✗ no result (remaining: {remaining})")

            # Rate limit guard
            if str(remaining) != "?" and int(remaining) <= 2:
                print(f"⏳ Rate limit low ({remaining}), sleeping 3600s ...")
                time.sleep(3600)
            else:
                time.sleep(SLEEP_SEC)

    print(f"\n✅ Done. {PHOTOS_CSV} updated.")

if __name__ == "__main__":
    main()
