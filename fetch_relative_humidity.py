"""
Fetch relative humidity mensuelle moyenne depuis Open-Meteo ERA5.
Enrichit climate.csv avec la colonne rh_mean (%).
"""
import csv, json, time, sys
from pathlib import Path
import urllib.request

BASE = "https://archive-api.open-meteo.com/v1/archive"
CLIMATE_FILE = Path("data/climate.csv")
DEST_FILE    = Path("data/destinations.csv")

def fetch_rh(lat, lon):
    """Retourne dict {mois_num: rh_mean} moyenné sur 2020-2024."""
    monthly = {m: [] for m in range(1, 13)}
    for year in range(2020, 2025):
        url = (f"{BASE}?latitude={lat}&longitude={lon}"
               f"&start_date={year}-01-01&end_date={year}-12-31"
               f"&hourly=relativehumidity_2m&timezone=auto")
        try:
            r = urllib.request.urlopen(url, timeout=30)
            d = json.loads(r.read())
        except Exception as e:
            print(f"  ERROR {year}: {e}", file=sys.stderr)
            continue
        times  = d.get("hourly", {}).get("time", [])
        values = d.get("hourly", {}).get("relativehumidity_2m", [])
        for t, v in zip(times, values):
            if v is None: continue
            m = int(t[5:7])
            monthly[m].append(v)
    return {m: round(sum(vs)/len(vs), 1) if vs else None
            for m, vs in monthly.items()}

def main():
    dests = {r["slug_fr"]: r for r in csv.DictReader(
        open(DEST_FILE, encoding="utf-8-sig"))}
    rows = list(csv.DictReader(open(CLIMATE_FILE, encoding="utf-8-sig")))

    if "rh_mean" not in rows[0]:
        for r in rows: r["rh_mean"] = ""

    # Slugs déjà traités
    done = {r["slug"] for r in rows if r.get("rh_mean", "")}
    slugs_todo = list({r["slug"] for r in rows if not r.get("rh_mean", "")})
    print(f"À fetcher: {len(slugs_todo)} slugs")

    slug_to_coords = {}
    for r in rows:
        s = r["slug"]
        if s not in slug_to_coords and s in dests:
            d = dests[s]
            slug_to_coords[s] = (float(d["lat"]), float(d["lon"]))

    results = {}
    for i, slug in enumerate(slugs_todo):
        if slug not in slug_to_coords:
            continue
        lat, lon = slug_to_coords[slug]
        print(f"[{i+1}/{len(slugs_todo)}] {slug}...")
        rh = fetch_rh(lat, lon)
        results[slug] = rh
        time.sleep(1.2)

    # Injecter dans les rows
    for r in rows:
        slug = r["slug"]
        m = int(r["mois_num"])
        if slug in results and results[slug].get(m) is not None:
            r["rh_mean"] = results[slug][m]

    # Réécrire le CSV
    fieldnames = list(rows[0].keys())
    with open(CLIMATE_FILE, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)

    print(f"✅ Done — {len(results)} slugs mis à jour")

if __name__ == "__main__":
    main()
