#!/usr/bin/env python3
"""
generate_hero_subs.py — génère des hero_sub météo factuels pour destinations.csv
depuis climate.csv. Écrase uniquement les entrées jugées génériques.
"""
import csv, re, unicodedata

MONTHS_FR = ['janvier','février','mars','avril','mai','juin',
             'juillet','août','septembre','octobre','novembre','décembre']
MONTHS_EN = ['January','February','March','April','May','June',
             'July','August','September','October','November','December']

def month_name(num, lang='fr'):
    return (MONTHS_FR if lang=='fr' else MONTHS_EN)[num - 1]

def months_range(nums, lang='fr'):
    """[4,5,6] → 'avril–juin'"""
    mns = MONTHS_FR if lang == 'fr' else MONTHS_EN
    if not nums: return ''
    if len(nums) == 1: return mns[nums[0]-1]
    # Try to find contiguous runs
    runs, cur = [], [nums[0]]
    for n in nums[1:]:
        if n == cur[-1] + 1: cur.append(n)
        else: runs.append(cur); cur = [n]
    runs.append(cur)
    parts = []
    for r in runs:
        if len(r) == 1: parts.append(mns[r[0]-1])
        else: parts.append(mns[r[0]-1] + '–' + mns[r[-1]-1])
    return ', '.join(parts)

def load_climate():
    climate = {}
    with open('data/climate.csv', encoding='utf-8-sig') as f:
        for r in csv.DictReader(f):
            slug = r['slug']
            if slug not in climate: climate[slug] = []
            climate[slug].append({
                'mois': r['mois'], 'mois_num': int(r['mois_num']),
                'tmin': int(r['tmin']), 'tmax': int(r['tmax']),
                'rain_pct': int(r['rain_pct']), 'sun_h': float(r['sun_h']),
                'score': float(r['score']), 'classe': r['classe']
            })
    return {k: sorted(v, key=lambda x: x['mois_num']) for k, v in climate.items()}

def is_generic(text):
    """Retourne True si hero_sub actuel est trop court / sans info météo."""
    if len(text) < 130: return True
    keywords = ['données', '10 ans', 'mousson', 'saison', 'fenêtre', 'pluie',
                'score', 'juillet', 'juin', 'décembre', 'novembre', 'invivable',
                'garantis', 'impossible', 'orage', 'cyclone', 'neige', 'chaleur',
                'risque', 'période', 'winter','summer','avoid','forecast']
    if not any(k.lower() in text.lower() for k in keywords): return True
    return False

def generate_fr(slug, dest, months, tropical, mountain):
    nom = dest['nom_bare']
    prep = dest.get('prep','à')

    rec = [m for m in months if m['classe'] == 'rec']
    mid = [m for m in months if m['classe'] == 'mid']
    avoid = [m for m in months if m['classe'] == 'avoid']
    best = max(months, key=lambda x: x['score'])
    worst = min(months, key=lambda x: x['score'])

    tmax_max = max(m['tmax'] for m in months)
    tmax_min = min(m['tmax'] for m in months)
    rain_min = min(m['rain_pct'] for m in months)
    rain_max = max(m['rain_pct'] for m in months)
    tmax_range = tmax_max - tmax_min
    best_sun = max(m['sun_h'] for m in months)
    n_rec = len(rec)

    rec_nums = [m['mois_num'] for m in rec]
    avoid_nums = [m['mois_num'] for m in avoid]
    best_mn = month_name(best['mois_num'])
    worst_mn = month_name(worst['mois_num'])

    parts = []

    # ── Fenêtre favorable ──────────────────────────────────────────
    if n_rec == 12:
        if rain_max - rain_min <= 15:
            parts.append(f"{nom} est visitable toute l'année avec une météo remarquablement stable ({rain_min}–{rain_max}% de jours pluvieux)")
        else:
            parts.append(f"{nom} est visitable toute l'année, bien que {best_mn} offre les meilleures conditions (score {best['score']:.1f}/10)")
    elif n_rec >= 8:
        window = months_range(rec_nums)
        parts.append(f"La fenêtre favorable {prep} {nom} couvre {n_rec} mois ({window}), ce qui laisse une large flexibilité")
    elif n_rec >= 4:
        window = months_range(rec_nums)
        parts.append(f"{nom} offre {n_rec} mois favorables ({window}) — {best_mn} est le meilleur mois avec {best['rain_pct']}% de jours pluvieux et {best['sun_h']:.0f}h de soleil")
    elif n_rec >= 1:
        window = months_range(rec_nums)
        parts.append(f"La fenêtre météo {prep} {nom} est étroite : {window} seulement ({n_rec} mois recommandé{'s' if n_rec>1 else ''})")
    else:
        parts.append(f"{nom} ne présente aucun mois idéal — même {best_mn} (le meilleur) atteint seulement {best['score']:.1f}/10")

    # ── Amplitude thermique ou contexte tropical ───────────────────
    if mountain:
        parts.append(f"l'altitude joue un rôle déterminant : {tmax_min}°C en hiver contre {tmax_max}°C en été")
    elif tropical:
        if rain_max >= 80:
            parts.append(f"la saison des pluies (pic à {rain_max}% en {worst_mn}) reste souvent tolérable grâce aux averses courtes et au soleil entre les ondées")
        else:
            parts.append(f"les pluies tropicales restent modérées (pic à {rain_max}%) et n'empêchent pas de profiter du séjour")
    elif tmax_range >= 18:
        parts.append(f"l'amplitude thermique est forte ({tmax_min}°C en {worst_mn} contre {tmax_max}°C en {best_mn}) — évitez {months_range(avoid_nums) if avoid_nums else worst_mn}")
    elif tmax_max >= 36:
        parts.append(f"la chaleur estivale dépasse {tmax_max}°C en {worst_mn if worst['tmax']==tmax_max else best_mn} — à éviter si vous êtes sensible à la canicule")
    elif tmax_max <= 15:
        parts.append(f"les températures restent fraîches toute l'année (max {tmax_max}°C) — habillez-vous en conséquence même en été")
    else:
        parts.append(f"les précipitations varient de {rain_min}% à {rain_max}% selon le mois")

    # ── Ensoleillement ou stat clé ─────────────────────────────────
    if best_sun >= 11:
        parts.append(f"jusqu'à {best_sun:.0f}h de soleil par jour en pic de saison")
    elif best_sun <= 5:
        parts.append(f"l'ensoleillement reste limité ({best_sun:.0f}h/j au meilleur mois) — facteur à anticiper")

    # ── Point de précision final ───────────────────────────────────
    parts.append(f"10 ans de données ERA5 pour choisir la date idéale")

    # Assembler
    text = '. '.join(p[0].upper() + p[1:] for p in parts if p) + '.'
    # Nettoyer doubles majuscules / points
    text = re.sub(r'\.\.+', '.', text)
    return text

def generate_en(slug, dest, months, tropical, mountain):
    nom = dest.get('nom_en', dest['nom_bare'])
    prep = 'in' if dest.get('prep','à') in ('à','en','aux') else 'in'

    rec = [m for m in months if m['classe'] == 'rec']
    best = max(months, key=lambda x: x['score'])
    worst = min(months, key=lambda x: x['score'])

    tmax_max = max(m['tmax'] for m in months)
    tmax_min = min(m['tmax'] for m in months)
    rain_min = min(m['rain_pct'] for m in months)
    rain_max = max(m['rain_pct'] for m in months)
    tmax_range = tmax_max - tmax_min
    best_sun = max(m['sun_h'] for m in months)
    n_rec = len(rec)

    rec_nums = [m['mois_num'] for m in rec]
    avoid_nums = [m['mois_num'] for m in [m for m in months if m['classe']=='avoid']]
    best_mn = month_name(best['mois_num'], 'en')
    worst_mn = month_name(worst['mois_num'], 'en')

    parts = []

    if n_rec == 12:
        if rain_max - rain_min <= 15:
            parts.append(f"{nom} is a year-round destination with consistently stable weather ({rain_min}–{rain_max}% rainy days)")
        else:
            parts.append(f"{nom} is visitable year-round, though {best_mn} offers the best conditions (score {best['score']:.1f}/10)")
    elif n_rec >= 8:
        window = months_range(rec_nums, 'en')
        parts.append(f"The good-weather window {prep} {nom} spans {n_rec} months ({window}), offering broad flexibility")
    elif n_rec >= 4:
        window = months_range(rec_nums, 'en')
        parts.append(f"{nom} has {n_rec} recommended months ({window}) — {best_mn} is the best with {best['rain_pct']}% rain probability and {best['sun_h']:.0f}h of sunshine")
    elif n_rec >= 1:
        window = months_range(rec_nums, 'en')
        parts.append(f"The weather window {prep} {nom} is narrow: only {window} ({n_rec} recommended month{'s' if n_rec>1 else ''})")
    else:
        parts.append(f"{nom} has no ideal month — even {best_mn} (the best) scores only {best['score']:.1f}/10")

    if mountain:
        parts.append(f"altitude plays a key role: {tmax_min}°C in winter vs {tmax_max}°C in summer")
    elif tropical:
        if rain_max >= 80:
            parts.append(f"the rainy season (peak {rain_max}% in {worst_mn}) is often tolerable thanks to short showers and sunshine between them")
        else:
            parts.append(f"tropical rains stay moderate (peak {rain_max}%) and rarely disrupt a stay")
    elif tmax_range >= 18:
        parts.append(f"the temperature swing is significant ({tmax_min}°C in {worst_mn} vs {tmax_max}°C in {best_mn})")
    elif tmax_max >= 36:
        parts.append(f"summer heat exceeds {tmax_max}°C — avoid if heat-sensitive")
    elif tmax_max <= 15:
        parts.append(f"temperatures stay cool year-round (max {tmax_max}°C) — dress accordingly even in summer")
    else:
        parts.append(f"rainfall ranges from {rain_min}% to {rain_max}% depending on the month")

    if best_sun >= 11:
        parts.append(f"up to {best_sun:.0f}h of sunshine per day at peak season")
    elif best_sun <= 5:
        parts.append(f"sunshine stays limited ({best_sun:.0f}h/day at best) — a factor to plan around")

    parts.append(f"10 years of ERA5 data to pick the ideal date")

    text = '. '.join(p[0].upper() + p[1:] for p in parts if p) + '.'
    text = re.sub(r'\.\.+', '.', text)
    return text


def main():
    climate = load_climate()
    dests = []
    with open('data/destinations.csv', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        for r in reader:
            dests.append(r)

    updated_fr = 0
    updated_en = 0
    skipped = 0

    for dest in dests:
        slug = dest['slug_fr']
        if slug not in climate:
            continue

        months = climate[slug]
        tropical = dest.get('tropical', 'False') == 'True'
        mountain = dest.get('mountain', 'False') == 'True'

        # FR
        if is_generic(dest['hero_sub']):
            dest['hero_sub'] = generate_fr(slug, dest, months, tropical, mountain)
            updated_fr += 1
        else:
            skipped += 1

        # EN
        if is_generic(dest.get('hero_sub_en', '')):
            dest['hero_sub_en'] = generate_en(slug, dest, months, tropical, mountain)
            updated_en += 1

    # Write back
    with open('data/destinations.csv', 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(dests)

    print(f"Updated FR: {updated_fr}, EN: {updated_en}, kept as-is: {skipped}")

if __name__ == '__main__':
    main()
