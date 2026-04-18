"""
Fetch données ERA5 (Open-Meteo) pour les nouvelles destinations
et les intègre dans climate.csv avec scoring complet.

Usage: python3 fetch_new_destinations.py
"""
import csv, json, time, sys, math
from pathlib import Path
import urllib.request, urllib.error
import pandas as pd
import importlib.util

# ── Config ──────────────────────────────────────────────────────────────────
DEST_FILE    = Path("data/destinations.csv")
CLIMATE_FILE = Path("data/climate.csv")
BASE_ARCHIVE = "https://archive-api.open-meteo.com/v1/archive"
YEARS        = list(range(2014, 2024))  # 10 ans ERA5
MOIS_FR      = ["Janvier","Février","Mars","Avril","Mai","Juin",
                "Juillet","Août","Septembre","Octobre","Novembre","Décembre"]

# ── Charger scoring ──────────────────────────────────────────────────────────
import scoring

# ── Destinations déjà dans climate.csv ──────────────────────────────────────
existing_climate = pd.read_csv(CLIMATE_FILE)
existing_slugs   = set(existing_climate['slug'].unique())

# ── Destinations à fetcher ───────────────────────────────────────────────────
dest_df = pd.read_csv(DEST_FILE)
to_fetch = dest_df[~dest_df['slug_fr'].isin(existing_slugs)].copy()
print(f"Destinations à fetcher : {len(to_fetch)}")
for _, r in to_fetch.iterrows():
    print(f"  {r['slug_fr']} ({r['nom_fr']}, {r['pays']}) lat={r['lat']} lon={r['lon']}")

# ── Fetch ERA5 ───────────────────────────────────────────────────────────────
def fetch_era5(lat, lon, year):
    """Fetch variables journalières ERA5 pour une année."""
    url = (
        f"{BASE_ARCHIVE}?latitude={lat}&longitude={lon}"
        f"&start_date={year}-01-01&end_date={year}-12-31"
        f"&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,"
        f"sunshine_duration,shortwave_radiation_sum"
        f"&timezone=auto"
    )
    try:
        r = urllib.request.urlopen(url, timeout=30)
        return json.loads(r.read())
    except Exception as e:
        print(f"    ERROR fetch {year}: {e}", file=sys.stderr)
        return None

def aggregate_monthly(data_years):
    """Agréger les données journalières en moyennes mensuelles sur 10 ans."""
    # Accumulateurs par mois
    monthly = {m: {'tmax':[],'tmin':[],'precip':[],'sun_h':[]} for m in range(1,13)}

    for d in data_years:
        if not d:
            continue
        daily = d.get('daily', {})
        times  = daily.get('time', [])
        tmax   = daily.get('temperature_2m_max', [])
        tmin   = daily.get('temperature_2m_min', [])
        precip = daily.get('precipitation_sum', [])
        sun    = daily.get('sunshine_duration', [])  # secondes

        for i, t in enumerate(times):
            m = int(t[5:7])
            if i < len(tmax) and tmax[i] is not None:
                monthly[m]['tmax'].append(tmax[i])
            if i < len(tmin) and tmin[i] is not None:
                monthly[m]['tmin'].append(tmin[i])
            if i < len(precip) and precip[i] is not None:
                monthly[m]['precip'].append(precip[i])
            if i < len(sun) and sun[i] is not None:
                monthly[m]['sun_h'].append(sun[i] / 3600)  # s → h

    result = {}
    for m in range(1, 13):
        vals = monthly[m]
        if not vals['tmax']:
            continue
        n_days = len(vals['tmax'])
        n_rainy = sum(1 for p in vals['precip'] if p > 1.0)
        result[m] = {
            'tmax': round(sum(vals['tmax'])/len(vals['tmax']), 1),
            'tmin': round(sum(vals['tmin'])/len(vals['tmin']), 1),
            'precip_mm': round(sum(vals['precip']), 1),
            'rain_pct': round(100 * n_rainy / n_days) if n_days else 0,
            'sun_h': round(sum(vals['sun_h'])/len(vals['sun_h']), 1),
        }
    return result

# ── Traitement ───────────────────────────────────────────────────────────────
new_rows = []

for _, dest in to_fetch.iterrows():
    slug = dest['slug_fr']
    lat  = float(dest['lat'])
    lon  = float(dest['lon'])
    is_tropical = str(dest.get('tropical', 'False')).strip().lower() in ('true','1','yes')

    print(f"\n→ {slug} ({dest['nom_fr']}) lat={lat} lon={lon}")

    # Fetch 10 années
    data_years = []
    for year in YEARS:
        print(f"  fetch {year}...", end=' ', flush=True)
        d = fetch_era5(lat, lon, year)
        data_years.append(d)
        print("OK" if d else "FAIL")
        time.sleep(0.3)  # rate limiting

    # Agréger
    monthly = aggregate_monthly(data_years)
    if not monthly:
        print(f"  ⚠️  Pas de données pour {slug}, skip")
        continue

    # Calculer les scores via scoring.py
    months_data = []
    for m_num in range(1, 13):
        if m_num not in monthly:
            continue
        mv = monthly[m_num]
        # Score brut
        score_raw = scoring.raw_score(
            mv['tmax'], mv['rain_pct'], mv['sun_h']
        )
        score = round(min(10, max(0, score_raw)), 1)
        classe = scoring.ski_class(score)

        new_rows.append({
            'slug': slug,
            'mois': MOIS_FR[m_num-1],
            'mois_num': m_num,
            'tmin': mv['tmin'],
            'tmax': mv['tmax'],
            'rain_pct': mv['rain_pct'],
            'precip_mm': mv['precip_mm'],
            'sun_h': mv['sun_h'],
            'score': score,
            'classe': classe,
            'source': 'open-meteo',
            'sea_temp': '',
            'beach_score': '',
            'dew_point_mean': '',
            'uv_index': '',
            'wave_height_mean': '',
            'swell_period_mean': '',
            'aqi_mean': '',
        })

    if any(r['slug'] == slug for r in new_rows):
        scores = [r['score'] for r in new_rows if r['slug'] == slug]
        print(f"  ✅ {len(scores)} mois | scores: {min(scores):.1f}–{max(scores):.1f}")
    
    time.sleep(0.5)

# ── Sauvegarder ─────────────────────────────────────────────────────────────
if new_rows:
    new_df = pd.DataFrame(new_rows)
    combined = pd.concat([existing_climate, new_df], ignore_index=True)
    combined.to_csv(CLIMATE_FILE, index=False)
    print(f"\n✅ climate.csv mis à jour : {len(existing_climate)} → {len(combined)} lignes")
    print(f"   {len(new_rows)} lignes ajoutées pour {len(new_rows)//12} destinations")
else:
    print("\n⚠️  Aucune donnée ajoutée")
