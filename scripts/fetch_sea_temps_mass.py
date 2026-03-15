import urllib.request, json, csv, time
from collections import defaultdict
from scoring import raw_beach_score

dests = {r['slug_fr']: r for r in csv.DictReader(open('data/destinations.csv'))}
with open('data/climate.csv', newline='') as f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames
    rows = list(reader)
idx = {(r['slug'], r['mois_num']): i for i, r in enumerate(rows)}

missing = [slug for slug, d in dests.items()
           if d.get('coastal') == 'True'
           and any(r['slug']==slug and r['mois_num']=='7' and not r.get('sea_temp') for r in rows)]

print(f'{len(missing)} destinations a fetcher')

def fetch_sst(lat, lon):
    url = (f'https://marine-api.open-meteo.com/v1/marine?latitude={lat}&longitude={lon}'
           f'&hourly=sea_surface_temperature&start_date=2018-01-01&end_date=2023-12-31')
    with urllib.request.urlopen(url, timeout=30) as r:
        data = json.loads(r.read())
    monthly = defaultdict(list)
    for t, v in zip(data['hourly']['time'], data['hourly']['sea_surface_temperature']):
        if v is not None:
            monthly[int(t[5:7])].append(v)
    return {m: round(sum(vs)/len(vs), 1) for m, vs in monthly.items() if vs}

updated, errors = 0, []
for i, slug in enumerate(missing):
    try:
        d = dests[slug]
        monthly = fetch_sst(float(d['lat']), float(d['lon']))
        if not monthly:
            errors.append(slug)
            continue
        for m, sst in monthly.items():
            j = idx.get((slug, str(m)))
            if j is None:
                continue
            rows[j]['sea_temp'] = str(sst)
            try:
                r = rows[j]
                bs = round(raw_beach_score(float(r['tmax']), float(r['rain_pct']), float(r['sun_h']), sst) * 10, 1)
                rows[j]['beach_score'] = str(bs)
                updated += 1
            except Exception:
                pass
        if (i+1) % 30 == 0:
            print(f'  [{i+1}/{len(missing)}] {slug} juil={monthly.get(7)}C')
        time.sleep(0.25)
    except Exception as e:
        errors.append(f'{slug}:{str(e)[:60]}')
        time.sleep(1)

with open('data/climate.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=fieldnames)
    w.writeheader()
    w.writerows(rows)

print(f'OK: {updated} lignes mises a jour | Erreurs: {len(errors)}')
if errors:
    print('Premiers erreurs:', errors[:5])
