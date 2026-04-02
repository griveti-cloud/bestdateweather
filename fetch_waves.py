"""
Fetch wave height + swell period depuis Marine API Open-Meteo.
Destinations côtières uniquement (417/697).
Enrichit climate.csv avec wave_height_mean + swell_period_mean.
"""
import csv, json, time, sys
from pathlib import Path
import urllib.request

MARINE_BASE = "https://marine-api.open-meteo.com/v1/marine"
CLIMATE_FILE = Path("data/climate.csv")
DEST_FILE    = Path("data/destinations.csv")
YEAR = "2024"

def fetch_waves_year(lat, lon):
    """Retourne dict {mois_num: (wave_h_mean, swell_period_mean)}"""
    url = (f"{MARINE_BASE}?latitude={lat}&longitude={lon}"
           f"&start_date={YEAR}-01-01&end_date={YEAR}-12-31"
           f"&daily=wave_height_max,swell_wave_period_max&timezone=auto")
    try:
        r = urllib.request.urlopen(url, timeout=20)
        d = json.loads(r.read())
    except Exception as e:
        print(f"  ERROR: {e}", file=sys.stderr)
        return {}

    times  = d.get("daily", {}).get("time", [])
    waves  = d.get("daily", {}).get("wave_height_max", [])
    swells = d.get("daily", {}).get("swell_wave_period_max", [])

    monthly_w, monthly_s = {}, {}
    for t, w, s in zip(times, waves, swells):
        m = int(t[5:7])
        if w is not None: monthly_w.setdefault(m, []).append(w)
        if s is not None: monthly_s.setdefault(m, []).append(s)

    result = {}
    for m in range(1, 13):
        wh = round(sum(monthly_w[m])/len(monthly_w[m]), 2) if m in monthly_w else None
        sp = round(sum(monthly_s[m])/len(monthly_s[m]), 1) if m in monthly_s else None
        if wh is not None:
            result[m] = (wh, sp)
    return result

def main():
    dests = {r["slug_fr"]: r for r in csv.DictReader(
        open(DEST_FILE, encoding="utf-8-sig"))}
    coastal_slugs = {slug for slug, d in dests.items()
                     if d.get("coastal","").strip().lower() in ("true","1","yes")}
    print(f"Destinations côtières : {len(coastal_slugs)}")

    rows = list(csv.DictReader(open(CLIMATE_FILE, encoding="utf-8")))
    for r in rows:
        r.setdefault("wave_height_mean", "")
        r.setdefault("swell_period_mean", "")

    slugs_done = {r["slug"] for r in rows
                  if r.get("wave_height_mean") and r["slug"] in coastal_slugs}
    slugs_todo = sorted(coastal_slugs - slugs_done)
    print(f"À fetcher : {len(slugs_todo)} ({len(slugs_done)} déjà faites)")

    slug_coords = {slug: (float(d["lat"]), float(d["lon"]))
                   for slug, d in dests.items() if slug in coastal_slugs}

    wave_cache = {}
    for i, slug in enumerate(slugs_todo):
        if slug not in slug_coords:
            print(f"[{i+1}/{len(slugs_todo)}] {slug}: coords manquantes")
            continue
        lat, lon = slug_coords[slug]
        print(f"[{i+1}/{len(slugs_todo)}] {slug}...", end=" ", flush=True)
        data = fetch_waves_year(lat, lon)
        if data:
            wave_cache[slug] = data
            print(f"OK ({len(data)} mois, ex. jan={data.get(1,('?','?'))[0]}m)")
        else:
            print("FAIL")
        time.sleep(0.15)

        if (i+1) % 50 == 0:
            _write_csv(rows, wave_cache)
            print(f"  → Checkpoint {i+1}")

    _write_csv(rows, wave_cache)
    print(f"\nDone. {len(wave_cache)} destinations enrichies.")

def _write_csv(rows, wave_cache):
    for r in rows:
        slug = r["slug"]
        if slug in wave_cache:
            m = int(r["mois_num"])
            if m in wave_cache[slug]:
                wh, sp = wave_cache[slug][m]
                r["wave_height_mean"] = wh if wh is not None else ""
                r["swell_period_mean"] = sp if sp is not None else ""

    fieldnames = list(rows[0].keys())
    with open(CLIMATE_FILE, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)

if __name__ == "__main__":
    main()
