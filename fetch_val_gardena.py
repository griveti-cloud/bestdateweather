#!/usr/bin/env python3
"""
Fetch Val Gardena climate data from Open-Meteo archive (2014-2023)
et remplace les données estimées dans data/climate.csv.

Usage : python3 fetch_val_gardena.py
Prérequis : quota Open-Meteo disponible (réinitialisé chaque jour)
"""

import sys, os, csv, json, time, urllib.request
from collections import defaultdict

# ── Config ────────────────────────────────────────────────────────────────
SLUG   = "val-gardena"
LAT    = 46.57
LON    = 11.77
TZ     = "Europe/Rome"
YEARS  = [("2014-01-01","2018-12-31"), ("2019-01-01","2023-12-31")]
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# ── Helpers ───────────────────────────────────────────────────────────────
MOIS = ["","Janvier","Février","Mars","Avril","Mai","Juin",
        "Juillet","Août","Septembre","Octobre","Novembre","Décembre"]

def fetch_year_range(start, end):
    url = (
        "https://archive-api.open-meteo.com/v1/archive"
        f"?latitude={LAT}&longitude={LON}"
        f"&start_date={start}&end_date={end}"
        "&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,sunshine_duration"
        f"&timezone={TZ.replace('/','%2F')}"
    )
    print(f"  Fetching {start} → {end}...")
    with urllib.request.urlopen(url, timeout=60) as r:
        data = json.loads(r.read())
    if "error" in data:
        raise RuntimeError(data.get("reason", str(data)))
    d = data["daily"]
    return list(zip(d["time"], d["temperature_2m_max"],
                    d["temperature_2m_min"], d["precipitation_sum"],
                    d["sunshine_duration"]))

def aggregate_monthly(daily_rows):
    monthly = defaultdict(lambda: {"tmax":[],"tmin":[],"precip":[],"rain_days":[],"sun_h":[]})
    for date, tx, tn, pr, su in daily_rows:
        m = int(date[5:7])
        if tx is None or tn is None: continue
        monthly[m]["tmax"].append(tx)
        monthly[m]["tmin"].append(tn)
        if pr is not None:
            monthly[m]["precip"].append(pr)
            monthly[m]["rain_days"].append(1 if pr >= 1 else 0)
        if su is not None:
            monthly[m]["sun_h"].append(su / 3600)
    return monthly

def score_classe(tmax, rain_pct, precip_mm, sun_h):
    """Score simplifié cohérent avec scoring.py (hors normalisation globale)."""
    # On utilisera scoring.py directement — voir ci-dessous
    pass

# ── Fetch ──────────────────────────────────────────────────────────────────
print(f"\n{'='*55}")
print(f"  Fetch Open-Meteo archive — {SLUG} ({LAT},{LON})")
print(f"{'='*55}")

all_rows = []
for start, end in YEARS:
    rows = fetch_year_range(start, end)
    all_rows.extend(rows)
    print(f"  → {len(rows)} jours récupérés")
    time.sleep(2)  # pause entre requêtes

monthly = aggregate_monthly(all_rows)
print(f"\n  Agrégation : {len(all_rows)} jours → 12 mois")

# ── Calcul stats mensuelles ────────────────────────────────────────────────
# Import scoring.py pour utiliser compute_scores exact
sys.path.insert(0, SCRIPT_DIR)
from scoring import compute_scores

months_input = []
for m in range(1, 13):
    d = monthly[m]
    tmax     = round(sum(d["tmax"]) / len(d["tmax"]), 1)
    tmin     = round(sum(d["tmin"]) / len(d["tmin"]), 1)
    precip   = round(sum(d["precip"]) / len(d["precip"]) * 30, 1) if d["precip"] else 0.0
    rain_pct = round(sum(d["rain_days"]) / len(d["rain_days"]) * 100) if d["rain_days"] else 0
    sun_h    = round(sum(d["sun_h"]) / len(d["sun_h"]) * 30, 1) if d["sun_h"] else 0.0

    # Classe éditoriale brute (avant scoring normalisé)
    if tmax >= 20 and rain_pct < 40:
        cls = "rec"
    elif tmax < 3 or (tmax < 8 and rain_pct > 50):
        cls = "avoid"
    else:
        cls = "mid"

    months_input.append({
        "month": MOIS[m], "mois_num": m,
        "tmax": tmax, "tmin": tmin,
        "rain_pct": rain_pct, "precip_mm": precip,
        "sun_h": sun_h, "cls": cls,
    })

scores = compute_scores(months_input, slug=SLUG)

# ── Affichage & construction lignes CSV ────────────────────────────────────
print(f"\n  Résultats climatiques Val Gardena :")
print(f"  {'Mois':<12} {'Tmin':>5} {'Tmax':>5} {'Pluie%':>7} {'Précip':>7} {'Soleil':>7} {'Score':>6} {'Cls'}")
print(f"  {'-'*65}")

new_rows = []
for mi, mo in enumerate(months_input):
    s = scores[mi]
    score_10 = s["score_10"]
    cls = mo["cls"]
    # Recalculer classe depuis score_10 pour cohérence
    if score_10 >= 7.0: cls = "rec"
    elif score_10 >= 4.0: cls = "mid"
    else: cls = "avoid"

    print(f"  {mo['month']:<12} {mo['tmin']:>5.1f} {mo['tmax']:>5.1f} "
          f"{mo['rain_pct']:>7} {mo['precip_mm']:>7.1f} {mo['sun_h']:>7.1f} "
          f"{score_10:>6.1f} [{cls}]")

    new_rows.append(
        f"{SLUG},{mo['month']},{mo['mois_num']},"
        f"{mo['tmin']},{mo['tmax']},{mo['rain_pct']},"
        f"{mo['precip_mm']},{mo['sun_h']},{score_10},{cls},open-meteo,,"
    )

# ── Mise à jour climate.csv ────────────────────────────────────────────────
climate_path = os.path.join(SCRIPT_DIR, "data", "climate.csv")
with open(climate_path) as f:
    lines = f.readlines()

# Supprimer les anciennes lignes val-gardena
filtered = [l for l in lines if not l.startswith(f"{SLUG},")]
removed = len(lines) - len(filtered)
print(f"\n  Suppression : {removed} anciennes lignes val-gardena")

# Trouver position d'insertion (après val-disere)
insert_pos = len(filtered)
in_vald = False
for i, line in enumerate(filtered):
    if line.startswith("val-disere,"):
        in_vald = True
    elif in_vald:
        insert_pos = i
        break

final_lines = filtered[:insert_pos] + [r+"\n" for r in new_rows] + filtered[insert_pos:]
with open(climate_path, "w") as f:
    f.writelines(final_lines)

print(f"  Insertion : {len(new_rows)} nouvelles lignes à position {insert_pos}")

# ── Régénération des pages ─────────────────────────────────────────────────
print(f"\n  Régénération des pages ({SLUG}) :")
import subprocess
for lang in ["fr", "en", "en-us", "es", "de"]:
    r = subprocess.run(
        ["python3", "generate_pages.py", "--lang", lang, SLUG],
        capture_output=True, text=True, cwd=SCRIPT_DIR
    )
    line = next((l for l in r.stdout.splitlines() if "annual" in l or "Error" in l), r.stdout.strip()[-60:])
    print(f"  [{lang:5s}] {line}")

# ── Git commit ─────────────────────────────────────────────────────────────
print(f"\n  Commit git...")
subprocess.run(["git", "add", "-A"], cwd=SCRIPT_DIR)
subprocess.run([
    "git", "commit", "-m",
    f"data: remplacer données estimées Val Gardena par Open-Meteo archive 2014-2023"
], cwd=SCRIPT_DIR)
subprocess.run(["git", "push"], cwd=SCRIPT_DIR)

print(f"\n{'='*55}")
print(f"  ✓ Val Gardena mis à jour — données Open-Meteo réelles")
print(f"{'='*55}\n")
