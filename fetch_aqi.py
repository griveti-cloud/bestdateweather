"""
Fetch AQI mensuel moyen depuis Open-Meteo Air Quality API.
Toutes les 697 destinations. Agrégation en moyenne mensuelle.
Seuil d'affichage : AQI > 40 (European scale).
"""
import csv, json, time, sys
from pathlib import Path
import urllib.request

AQI_BASE = "https://air-quality-api.open-meteo.com/v1/air-quality"
CLIMATE_FILE = Path("data/climate.csv")
DEST_FILE    = Path("data/destinations.csv")
YEAR = "2024"

def fetch_aqi_year(lat, lon):
    """Retourne dict {mois_num: aqi_mean}"""
    url = (f"{AQI_BASE}?latitude={lat}&longitude={lon}"
           f"&start_date={YEAR}-01-01&end_date={YEAR}-12-31"
           f"&hourly=european_aqi&timezone=auto")
    try:
        r = urllib.request.urlopen(url, timeout=20)
        d = json.loads(r.read())
    except Exception as e:
        print(f"  ERROR: {e}", file=sys.stderr)
        return {}
    times = d.get("hourly", {}).get("time", [])
    vals  = d.get("hourly", {}).get("european_aqi", [])
    monthly = {}
    for t, v in zip(times, vals):
        if v is None: continue
        m = int(t[5:7])
        monthly.setdefault(m, []).append(v)
    return {m: round(sum(vs)/len(vs)) for m, vs in monthly.items()}

def main():
    dests = {r["slug_fr"]: r for r in csv.DictReader(
        open(DEST_FILE, encoding="utf-8-sig"))}
    rows = list(csv.DictReader(open(CLIMATE_FILE, encoding="utf-8")))
    for r in rows:
        r.setdefault("aqi_mean", "")
    slugs_done = {r["slug"] for r in rows if r.get("aqi_mean")}
    slugs_todo = sorted({r["slug"] for r in rows} - slugs_done)
    print(f"AQI à fetcher : {len(slugs_todo)} ({len(slugs_done)} déjà faites)")
    slug_coords = {slug: (float(d["lat"]), float(d["lon"]))
                   for slug, d in dests.items()}
    aqi_cache = {}
    for i, slug in enumerate(slugs_todo):
        if slug not in slug_coords:
            print(f"[{i+1}] {slug}: coords manquantes"); continue
        lat, lon = slug_coords[slug]
        print(f"[{i+1}/{len(slugs_todo)}] {slug}...", end=" ", flush=True)
        data = fetch_aqi_year(lat, lon)
        if data:
            aqi_cache[slug] = data
            max_aqi = max(data.values())
            print(f"OK (max={max_aqi})")
        else:
            print("FAIL")
        time.sleep(0.15)
        if (i+1) % 50 == 0:
            _write_csv(rows, aqi_cache)
            print(f"  → Checkpoint {i+1}")
    _write_csv(rows, aqi_cache)
    print(f"\nDone. {len(aqi_cache)} destinations enrichies.")
    # Stats
    all_rows = list(csv.DictReader(open(CLIMATE_FILE)))
    polluted = {r["slug"] for r in all_rows if r.get("aqi_mean") and float(r["aqi_mean"]) > 40}
    print(f"Destinations avec AQI > 40 au moins 1 mois : {len(polluted)}")

def _write_csv(rows, aqi_cache):
    for r in rows:
        slug = r["slug"]
        if slug in aqi_cache:
            m = int(r["mois_num"])
            r["aqi_mean"] = aqi_cache[slug].get(m, "")
    fieldnames = list(rows[0].keys())
    with open(CLIMATE_FILE, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)

if __name__ == "__main__":
    main()
