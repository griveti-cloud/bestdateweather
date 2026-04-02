"""
Fetch UV index mensuel moyen depuis Open-Meteo historical-forecast-api.
Enrichit climate.csv avec la colonne uv_index.
"""
import csv, json, time, sys
from pathlib import Path
import urllib.request, urllib.error

BASE = "https://historical-forecast-api.open-meteo.com/v1/forecast"
CLIMATE_FILE = Path("data/climate.csv")
DEST_FILE    = Path("data/destinations.csv")
YEAR         = "2024"  # année de référence pour UV moyen

def fetch_uv_year(lat, lon):
    """Retourne dict {mois_num: uv_mean} pour les 12 mois."""
    url = (f"{BASE}?latitude={lat}&longitude={lon}"
           f"&start_date={YEAR}-01-01&end_date={YEAR}-12-31"
           f"&daily=uv_index_max&timezone=auto")
    try:
        r = urllib.request.urlopen(url, timeout=20)
        d = json.loads(r.read())
    except Exception as e:
        print(f"  ERROR: {e}", file=sys.stderr)
        return {}
    
    times  = d.get("daily", {}).get("time", [])
    values = d.get("daily", {}).get("uv_index_max", [])
    
    # Agréger par mois
    monthly = {}
    for t, v in zip(times, values):
        if v is None:
            continue
        month = int(t[5:7])
        monthly.setdefault(month, []).append(v)
    
    return {m: round(sum(vs)/len(vs), 1) for m, vs in monthly.items()}

def main():
    # Charger destinations
    dests = {r["slug_fr"]: r for r in csv.DictReader(
        open(DEST_FILE, encoding="utf-8-sig"))}
    
    # Charger climate.csv existant
    rows = list(csv.DictReader(open(CLIMATE_FILE, encoding="utf-8")))
    
    # Vérifier si colonne existe
    if "uv_index" not in rows[0]:
        for r in rows:
            r["uv_index"] = ""
    
    # Grouper par slug
    slugs_done = {r["slug"] for r in rows if r.get("uv_index")}
    slugs_todo = sorted({r["slug"] for r in rows if not r.get("uv_index")})
    
    print(f"UV à fetcher : {len(slugs_todo)} destinations ({len(slugs_done)} déjà faites)")
    
    # Construire index slug → (lat, lon)
    slug_coords = {}
    for slug, d in dests.items():
        try:
            slug_coords[slug] = (float(d["lat"]), float(d["lon"]))
        except:
            pass
    
    # UV cache
    uv_cache = {}
    
    for i, slug in enumerate(slugs_todo):
        if slug not in slug_coords:
            print(f"[{i+1}/{len(slugs_todo)}] {slug}: coords manquantes, skip")
            continue
        lat, lon = slug_coords[slug]
        print(f"[{i+1}/{len(slugs_todo)}] {slug} ({lat},{lon})...", end=" ", flush=True)
        uv = fetch_uv_year(lat, lon)
        if uv:
            uv_cache[slug] = uv
            print(f"OK ({len(uv)} mois)")
        else:
            print("FAIL")
        time.sleep(0.15)  # respecter rate limit
        
        # Sauvegarder tous les 50 slugs
        if (i+1) % 50 == 0:
            _write_csv(rows, uv_cache)
            print(f"  → Checkpoint sauvegardé ({i+1} traités)")
    
    _write_csv(rows, uv_cache)
    print(f"\nDone. {len(uv_cache)} destinations enrichies.")

def _write_csv(rows, uv_cache):
    # Injecter UV dans les rows
    for r in rows:
        slug = r["slug"]
        if slug in uv_cache:
            mois = int(r["mois_num"])
            r["uv_index"] = uv_cache[slug].get(mois, "")
    
    fieldnames = list(rows[0].keys())
    if "uv_index" not in fieldnames:
        fieldnames.append("uv_index")
    
    with open(CLIMATE_FILE, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)

if __name__ == "__main__":
    main()
