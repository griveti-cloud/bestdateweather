#!/usr/bin/env python3
"""
generate_editorial_rules.py — Génération éditoriale par règles ERA5.
Couvre toutes les destinations manquantes sans appel API.
Skip les entrées déjà présentes dans editorial.json.
Usage: python3 generate_editorial_rules.py
"""
import csv, json, os

OUTPUT_FILE  = 'data/editorial.json'
CLIMATE_FILE = 'data/climate.csv'
DESTS_FILE   = 'data/destinations.csv'

MONTHS = {
    'fr': ['Janvier','Février','Mars','Avril','Mai','Juin',
           'Juillet','Août','Septembre','Octobre','Novembre','Décembre'],
    'en': ['January','February','March','April','May','June',
           'July','August','September','October','November','December'],
    'es': ['Enero','Febrero','Marzo','Abril','Mayo','Junio',
           'Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre'],
    'de': ['Januar','Februar','März','April','Mai','Juni',
           'Juli','August','September','Oktober','November','Dezember'],
}

def gen(slug, nom, pays, month_name, month_lc, tmin, tmax,
        rain_pct, precip_mm, sun_h, score, sea_temp, beach_score,
        best_month, best_month_lc, best_score, lang):

    is_very_hot  = tmax >= 37
    is_hot       = tmax >= 32
    is_warm      = 24 <= tmax < 32
    is_mild      = 15 <= tmax < 24
    is_cool      = 7  <= tmax < 15
    is_cold      = tmax < 7
    is_dry       = rain_pct <= 15
    is_little_r  = 15 < rain_pct <= 35
    is_moderate  = 35 < rain_pct <= 55
    is_rainy     = rain_pct > 55
    is_very_sun  = sun_h >= 11
    is_sunny     = sun_h >= 8
    is_cloudy    = sun_h < 5
    has_sea      = sea_temp is not None and sea_temp > 0
    is_warm_sea  = has_sea and sea_temp >= 25
    is_swim      = has_sea and sea_temp >= 21
    is_cool_sea  = has_sea and sea_temp < 18
    is_peak      = score >= 8.5
    is_good      = 7.0 <= score < 8.5
    is_fair      = 5.5 <= score < 7.0
    is_poor      = score < 5.5
    diff         = best_score - score
    is_near_peak = diff <= 0.4

    def rain_desc(l):
        if precip_mm < 15:
            return {'fr':'quelques averses isolées','en':'only occasional showers',
                    'es':'algún chubasco aislado','de':'vereinzelte Schauer'}[l]
        elif precip_mm < 60:
            return {'fr':'des pluies modérées','en':'moderate rainfall',
                    'es':'lluvias moderadas','de':'mäßiger Regen'}[l]
        elif precip_mm < 150:
            return {'fr':'des pluies régulières','en':'regular rainfall',
                    'es':'lluvias regulares','de':'regelmäßiger Regen'}[l]
        else:
            return {'fr':'de fortes pluies tropicales','en':'heavy tropical rains',
                    'es':'fuertes lluvias tropicales','de':'starke tropische Regenfälle'}[l]

    s = []

    # ── Phrase 1 : conditions principales ──────────────────────────────────
    if lang == 'fr':
        if is_very_hot and is_dry:
            s.append(f"Chaleur intense ({tmax:.0f}°C) et ciel bleu quasi permanent — {nom} en {month_lc} convient aux amateurs de soleil pur, moins aux personnes sensibles à la canicule.")
        elif is_very_hot and is_rainy:
            s.append(f"{nom} en {month_lc} combine chaleur étouffante ({tmax:.0f}°C) et {rain_desc(lang)} ({rain_pct:.0f}% des jours) — prévoyez des activités couvertes en journée.")
        elif is_hot and is_dry and is_very_sun:
            s.append(f"Avec {tmax:.0f}°C, {sun_h:.1f}h de soleil et seulement {rain_pct:.0f}% de jours avec pluie, {nom} en {month_lc} offre des conditions estivales très favorables.")
        elif is_hot and (is_moderate or is_rainy):
            s.append(f"La chaleur ({tmax:.0f}°C) se conjugue à {rain_desc(lang)} — {rain_pct:.0f}% des journées sont affectées, ce qui exige un programme adaptable.")
        elif is_warm and is_dry and is_sunny:
            s.append(f"Températures agréables ({tmax:.0f}°C), {sun_h:.1f}h de soleil quotidien et {rain_pct:.0f}% de jours secs : {nom} en {month_lc} coche les cases du séjour réussi.")
        elif is_warm and (is_moderate or is_rainy):
            s.append(f"{nom} en {month_lc} est doux ({tmax:.0f}°C) mais {rain_desc(lang)} touchent {rain_pct:.0f}% des journées — un imperméable léger est recommandé.")
        elif is_mild and is_dry:
            s.append(f"Températures douces ({tmax:.0f}°C) et seulement {rain_pct:.0f}% de jours pluvieux : {nom} en {month_lc} est une bonne fenêtre hors-saison, souvent moins fréquentée.")
        elif is_mild and (is_moderate or is_rainy):
            s.append(f"{month_name} apporte à {nom} un temps doux mais humide ({tmax:.0f}°C, {rain_pct:.0f}% de jours avec pluie) — idéal pour les musées et la gastronomie locale.")
        elif is_cool and is_dry:
            s.append(f"Ciel dégagé mais températures fraîches ({tmax:.0f}°C) — {nom} en {month_lc} convient aux voyageurs qui préfèrent marcher sans transpirer.")
        elif is_cool:
            s.append(f"{nom} en {month_lc} est frais ({tmax:.0f}°C) avec {sun_h:.1f}h de lumière par jour — la saison basse offre une authenticité que l'été ne permet pas.")
        elif is_cold:
            s.append(f"Conditions hivernales à {nom} en {month_lc} ({tmax:.0f}°C) — habillement chaud indispensable, mais l'ambiance locale hors-saison a son caractère propre.")
        else:
            s.append(f"{nom} en {month_lc} : {tmax:.0f}°C, {sun_h:.1f}h de soleil et {rain_pct:.0f}% de jours avec pluie.")

        # ── Phrase 2 : mer ou soleil ────────────────────────────────────────
        if is_warm_sea:
            s.append(f"La mer à {sea_temp:.0f}°C rend la baignade très agréable.")
        elif is_swim:
            s.append(f"Avec une mer à {sea_temp:.0f}°C, la baignade est confortable pour la plupart des baigneurs.")
        elif is_cool_sea:
            s.append(f"La mer reste fraîche ({sea_temp:.0f}°C) — les sports nautiques sont envisageables mais la baignade prolongée est déconseillée.")
        elif is_very_sun and not has_sea and (is_cool or is_cold or is_rainy or is_moderate):
            s.append(f"L'ensoleillement généreux ({sun_h:.1f}h/j) reste l'atout principal de cette période.")
        elif is_cloudy:
            s.append(f"La lumière reste limitée ({sun_h:.1f}h/j) — privilégiez les activités couvertes et la découverte culturelle.")

        # ── Phrase 3 : verdict score ────────────────────────────────────────
        if is_near_peak and is_peak:
            s.append(f"Score {score:.1f}/10 — c'est l'un des meilleurs créneaux de l'année pour {nom}.")
        elif is_near_peak and diff < 0.05:
            s.append(f"Score {score:.1f}/10 — c'est le pic annuel pour {nom}.")
        elif is_near_peak:
            s.append(f"Score {score:.1f}/10 — très proche du pic annuel ({best_month}, {best_score:.1f}/10), souvent avec moins de monde.")
        elif is_peak or is_good:
            s.append(f"Score {score:.1f}/10 : en dessous du meilleur mois ({best_month}, {best_score:.1f}/10) mais pleinement recommandable si vos dates sont fixées.")
        elif is_fair:
            s.append(f"Score {score:.1f}/10 — si vous avez de la flexibilité, {best_month} ({best_score:.1f}/10) offre une météo nettement supérieure.")
        else:
            s.append(f"Score {score:.1f}/10 — l'une des périodes les moins favorables de l'année ; {best_month} ({best_score:.1f}/10) est fortement préférable.")

    elif lang == 'en':
        if is_very_hot and is_dry:
            s.append(f"Intense heat ({tmax:.0f}°C) and near-constant sunshine define {nom} in {month_name} — ideal for sun seekers, demanding for those sensitive to extreme heat.")
        elif is_very_hot and is_rainy:
            s.append(f"{month_name} in {nom} combines stifling heat ({tmax:.0f}°C) with {rain_desc(lang)}, affecting {rain_pct:.0f}% of days — midday indoor activities are advisable.")
        elif is_hot and is_dry and is_very_sun:
            s.append(f"With {tmax:.0f}°C, {sun_h:.1f} daily sun hours and just {rain_pct:.0f}% rainy days, {nom} in {month_name} delivers highly favourable summer conditions.")
        elif is_hot and (is_moderate or is_rainy):
            s.append(f"The heat ({tmax:.0f}°C) is paired with {rain_desc(lang)} — {rain_pct:.0f}% of days are affected, requiring a flexible itinerary.")
        elif is_warm and is_dry and is_sunny:
            s.append(f"Pleasant temperatures ({tmax:.0f}°C), {sun_h:.1f} sun hours daily and only {rain_pct:.0f}% rainy days make {month_name} one of {nom}'s most reliable months.")
        elif is_warm and (is_moderate or is_rainy):
            s.append(f"{nom} in {month_name} is warm ({tmax:.0f}°C) but {rain_desc(lang)} affect {rain_pct:.0f}% of days — pack a light rain jacket.")
        elif is_mild and is_dry:
            s.append(f"Mild temperatures ({tmax:.0f}°C) and only {rain_pct:.0f}% rainy days make {month_name} a good off-peak window for {nom}, typically less crowded.")
        elif is_mild and (is_moderate or is_rainy):
            s.append(f"{month_name} brings mild but damp conditions to {nom} ({tmax:.0f}°C, {rain_pct:.0f}% rainy days) — excellent for museums and local gastronomy.")
        elif is_cool and is_dry:
            s.append(f"Clear skies but cool temperatures ({tmax:.0f}°C) — {nom} in {month_name} suits travellers who prefer exploring without the heat.")
        elif is_cool:
            s.append(f"{nom} in {month_name} is cool ({tmax:.0f}°C) with {sun_h:.1f} daylight hours — low season with authentic local atmosphere.")
        elif is_cold:
            s.append(f"Winter conditions in {nom} in {month_name} ({tmax:.0f}°C) — warm clothing essential, but the off-season character has its own appeal.")
        else:
            s.append(f"{nom} in {month_name}: {tmax:.0f}°C, {sun_h:.1f}h of sun, {rain_pct:.0f}% rainy days.")

        if is_warm_sea:
            s.append(f"The sea reaches {sea_temp:.0f}°C — excellent for swimming and water activities.")
        elif is_swim:
            s.append(f"Sea temperature of {sea_temp:.0f}°C makes swimming comfortable for most visitors.")
        elif is_cool_sea:
            s.append(f"The sea is cool at {sea_temp:.0f}°C — watersports are possible but extended swimming is not recommended.")
        elif is_very_sun and not has_sea and (is_cool or is_cold or is_rainy or is_moderate):
            s.append(f"Generous sunshine ({sun_h:.1f}h/day) stands out as this period's main asset.")
        elif is_cloudy:
            s.append(f"Limited daylight ({sun_h:.1f}h/day) — focus on indoor activities and cultural discovery.")

        if is_near_peak and is_peak:
            s.append(f"Score {score:.1f}/10 — one of the year's best windows for {nom}.")
        elif is_near_peak and diff < 0.05:
            s.append(f"Score {score:.1f}/10 — this is the annual peak for {nom}.")
        elif is_near_peak:
            s.append(f"Score {score:.1f}/10 — nearly as good as the annual peak ({best_month}, {best_score:.1f}/10), often with fewer tourists.")
        elif is_peak or is_good:
            s.append(f"Score {score:.1f}/10: below the best month ({best_month}, {best_score:.1f}/10) but fully worthwhile if your dates are set.")
        elif is_fair:
            s.append(f"Score {score:.1f}/10 — if you have flexibility, {best_month} ({best_score:.1f}/10) offers significantly better conditions.")
        elif diff > 0.1:
            s.append(f"Score {score:.1f}/10 — one of the year's least favourable periods; {best_month} ({best_score:.1f}/10) is strongly preferred.")
        else:
            s.append(f"Score {score:.1f}/10 — conditions at {nom} are fairly consistent year-round.")

    elif lang == 'es':
        if is_very_hot and is_dry:
            s.append(f"Calor intenso ({tmax:.0f}°C) y sol casi constante definen {nom} en {month_lc} — ideal para quienes disfrutan del calor extremo.")
        elif is_hot and is_dry and is_very_sun:
            s.append(f"Con {tmax:.0f}°C, {sun_h:.1f}h de sol diarias y solo {rain_pct:.0f}% de días lluviosos, {nom} en {month_lc} ofrece condiciones estivales muy favorables.")
        elif is_warm and is_dry and is_sunny:
            s.append(f"Temperaturas agradables ({tmax:.0f}°C), {sun_h:.1f}h de sol diarias y {rain_pct:.0f}% de días secos convierten {month_name.lower()} en uno de los meses más fiables en {nom}.")
        elif is_warm and is_rainy:
            s.append(f"{nom} en {month_lc} es cálido ({tmax:.0f}°C) pero {rain_desc(lang)} afectan al {rain_pct:.0f}% de los días — conviene llevar chubasquero ligero.")
        elif is_mild and is_dry:
            s.append(f"Temperaturas suaves ({tmax:.0f}°C) y {rain_pct:.0f}% de días secos hacen de {month_name.lower()} una buena ventana fuera de temporada en {nom}.")
        elif is_cool or is_cold:
            s.append(f"{nom} en {month_lc} es {'frío' if is_cold else 'fresco'} ({tmax:.0f}°C) con {sun_h:.1f}h de luz — temporada baja con ambiente local auténtico.")
        else:
            s.append(f"{nom} en {month_lc}: {tmax:.0f}°C, {sun_h:.1f}h de sol y {rain_pct:.0f}% de días con lluvia.")

        if is_warm_sea:
            s.append(f"El mar a {sea_temp:.0f}°C invita al baño sin reservas.")
        elif is_swim:
            s.append(f"Mar a {sea_temp:.0f}°C — el baño es cómodo para la mayoría de bañistas.")
        elif is_cool_sea:
            s.append(f"El mar está fresco ({sea_temp:.0f}°C) — deportes acuáticos posibles pero baño prolongado no recomendado.")

        if is_near_peak and is_peak:
            s.append(f"Puntuación {score:.1f}/10 — una de las mejores épocas del año en {nom}.")
        elif is_near_peak and diff < 0.05:
            s.append(f"Puntuación {score:.1f}/10 — este es el mejor momento del año en {nom}.")
        elif is_near_peak:
            s.append(f"Puntuación {score:.1f}/10 — muy cercana al pico anual ({best_month}, {best_score:.1f}/10), a menudo con menos turistas.")
        elif is_peak or is_good:
            s.append(f"Puntuación {score:.1f}/10 — por debajo del pico ({best_month}, {best_score:.1f}/10) pero plenamente recomendable con fechas fijas.")
        elif is_fair:
            s.append(f"Puntuación {score:.1f}/10 — con flexibilidad, {best_month} ({best_score:.1f}/10) ofrece condiciones notablemente mejores.")
        else:
            s.append(f"Puntuación {score:.1f}/10 — uno de los peores momentos del año; {best_month} ({best_score:.1f}/10) es muy preferible.")

    elif lang == 'de':
        if is_very_hot and is_dry:
            s.append(f"Intensive Hitze ({tmax:.0f}°C) und fast ununterbrochener Sonnenschein prägen {nom} im {month_name} — ideal für Hitzeliebhaber, anspruchsvoll für andere.")
        elif is_hot and is_dry and is_very_sun:
            s.append(f"Mit {tmax:.0f}°C, {sun_h:.1f}h Sonne täglich und nur {rain_pct:.0f}% Regentagen bietet {nom} im {month_name} sehr günstige Sommerbedingungen.")
        elif is_warm and is_dry and is_sunny:
            s.append(f"Angenehme Temperaturen ({tmax:.0f}°C), {sun_h:.1f}h Sonne täglich und {rain_pct:.0f}% trockene Tage machen {month_name} zu einem der zuverlässigsten Monate in {nom}.")
        elif is_warm and (is_moderate or is_rainy):
            s.append(f"{nom} im {month_name} ist warm ({tmax:.0f}°C), aber {rain_desc(lang)} betreffen {rain_pct:.0f}% der Tage — leichte Regenjacke einpacken.")
        elif is_mild and is_dry:
            s.append(f"Milde Temperaturen ({tmax:.0f}°C) und {rain_pct:.0f}% trockene Tage machen {month_name} zu einem guten Nebensaison-Fenster für {nom}.")
        elif is_cool or is_cold:
            s.append(f"{nom} im {month_name} ist {'kalt' if is_cold else 'kühl'} ({tmax:.0f}°C) mit {sun_h:.1f}h Tageslicht — Nebensaison mit authentischer Atmosphäre.")
        else:
            s.append(f"{nom} im {month_name}: {tmax:.0f}°C, {sun_h:.1f}h Sonne und {rain_pct:.0f}% Regentage.")

        if is_warm_sea:
            s.append(f"Das Meer erreicht {sea_temp:.0f}°C — ausgezeichnet zum Schwimmen und für Wassersport.")
        elif is_swim:
            s.append(f"Wassertemperatur {sea_temp:.0f}°C — angenehm für die meisten Schwimmer.")
        elif is_cool_sea:
            s.append(f"Das Meer ist kühl ({sea_temp:.0f}°C) — Wassersport möglich, aber längeres Schwimmen nicht empfohlen.")

        if is_near_peak and is_peak:
            s.append(f"Bewertung {score:.1f}/10 — eines der besten Zeitfenster des Jahres für {nom}.")
        elif is_near_peak and diff < 0.05:
            s.append(f"Bewertung {score:.1f}/10 — das ist der beste Reisezeitpunkt für {nom}.")
        elif is_near_peak:
            s.append(f"Bewertung {score:.1f}/10 — fast so gut wie der Jahreshöhepunkt ({best_month}, {best_score:.1f}/10), oft mit weniger Touristen.")
        elif is_peak or is_good:
            s.append(f"Bewertung {score:.1f}/10 — unter dem Jahreshöhepunkt ({best_month}, {best_score:.1f}/10), aber bei festen Terminen durchaus empfehlenswert.")
        elif is_fair:
            s.append(f"Bewertung {score:.1f}/10 — bei Flexibilität ist {best_month} ({best_score:.1f}/10) deutlich vorzuziehen.")
        else:
            s.append(f"Bewertung {score:.1f}/10 — eine der ungünstigsten Perioden des Jahres; {best_month} ({best_score:.1f}/10) ist klar vorzuziehen.")

    return ' '.join(s[:3])


def main():
    # Charger données
    climate_rows = []
    with open(CLIMATE_FILE, encoding='utf-8-sig') as f:
        climate_rows = list(csv.DictReader(f))

    dests_rows = []
    with open(DESTS_FILE, encoding='utf-8-sig') as f:
        dests_rows = list(csv.DictReader(f))

    dests_map = {r['slug_fr']: r for r in dests_rows}

    # Grouper climate par slug
    climate_by_slug = {}
    for r in climate_rows:
        slug = r['slug']
        if slug not in climate_by_slug:
            climate_by_slug[slug] = []
        climate_by_slug[slug].append(r)

    # Charger editorial existant
    editorial = {}
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, encoding='utf-8') as f:
            editorial = json.load(f)

    already = len(editorial)
    added = 0
    skipped = 0

    for slug, months in sorted(climate_by_slug.items()):
        dest = dests_map.get(slug)
        if not dest:
            continue

        # Trouver le meilleur mois
        best_row = max(months, key=lambda r: float(r['score']))
        
        for row in sorted(months, key=lambda r: int(r['mois_num'])):
            mi = int(row['mois_num'])
            tmin = float(row['tmin'])
            tmax = float(row['tmax'])
            rain = float(row['rain_pct'])
            precip = float(row['precip_mm'])
            sun = float(row['sun_h'])
            score = float(row['score'])
            sea = float(row['sea_temp']) if row.get('sea_temp','').strip() and row['sea_temp'] != 'nan' else None
            beach = float(row['beach_score']) if row.get('beach_score','').strip() and row['beach_score'] != 'nan' else None
            best_score = float(best_row['score'])

            for lang in ['fr', 'en', 'es', 'de']:
                key = f"{slug}:{mi}:{lang}"
                if key in editorial:
                    skipped += 1
                    continue

                MONTHS_L = MONTHS[lang]
                month_name = MONTHS_L[mi - 1]
                month_lc = month_name.lower()
                best_mi = int(best_row['mois_num'])
                best_month = MONTHS_L[best_mi - 1]
                best_month_lc = best_month.lower()

                nom_col  = {'fr':'nom_fr','en':'nom_en','es':'nom_es','de':'nom_de'}[lang]
                pays_col = {'fr':'pays','en':'country_en','es':'country_es','de':'country_de'}[lang]
                nom  = dest.get(nom_col, dest.get('nom_bare', slug))
                pays = dest.get(pays_col, dest.get('pays', ''))
                if not nom or nom == 'nan': nom = dest.get('nom_bare', slug)
                if not pays or pays == 'nan': pays = dest.get('pays', '')

                text = gen(slug, nom, pays, month_name, month_lc,
                           tmin, tmax, rain, precip, sun, score, sea, beach,
                           best_month, best_month_lc, best_score, lang)

                editorial[key] = text
                added += 1

    # Sauvegarder
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(editorial, f, ensure_ascii=False, indent=2)

    print(f"✅ editorial.json : {already} existants + {added} ajoutés = {len(editorial)} total")
    print(f"   ({skipped} skippés car déjà présents)")

if __name__ == '__main__':
    main()
