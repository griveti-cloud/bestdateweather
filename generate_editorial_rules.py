#!/usr/bin/env python3
"""
generate_editorial_rules.py — Génération éditoriale enrichie sans API.
Textes naturels et variés basés sur les données ERA5.
Skip les entrées déjà présentes (Claude ou rules).
"""
import csv, json, os, random

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

def pick(lst, seed):
    """Sélectionne un élément de façon déterministe selon un seed."""
    return lst[seed % len(lst)]

def gen(slug, nom, pays, month_name, month_lc, month_num,
        tmin, tmax, rain_pct, precip_mm, sun_h, score, sea_temp,
        best_month, best_month_lc, best_score, lang, coastal, tropical, mountain):

    # Seed déterministe par destination+mois pour cohérence entre régénérations
    seed = hash(f"{slug}{month_num}{lang}") % 1000

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
    is_best_month = diff < 0.05

    s = []

    if lang == 'fr':
        # ── Phrase 1 ──
        if is_very_hot and is_dry:
            opts = [
                f"{nom} en {month_lc}, c'est la chaleur à l'état pur : {tmax:.0f}°C et un soleil implacable. Parfait pour les adeptes du bronzage intense, moins adapté aux randonneurs ou aux personnes sensibles à la canicule.",
                f"Chaleur extrême ({tmax:.0f}°C) et ciel bleu permanent définissent {nom} en {month_lc}. Réservez les sorties aux heures fraîches et profitez des soirées douces.",
                f"{month_name} est le mois le plus chaud à {nom} ({tmax:.0f}°C) — idéal si vous recherchez le soleil sans compromis, exigeant pour tout le reste.",
            ]
        elif is_very_hot and is_rainy:
            opts = [
                f"{nom} en {month_lc} combine chaleur accablante ({tmax:.0f}°C) et {precip_mm:.0f}mm de pluie — {rain_pct:.0f}% des jours sont touchés. Les activités de plein air nécessitent une organisation matinale.",
                f"Chaud et humide : {nom} en {month_lc} affiche {tmax:.0f}°C avec des averses fréquentes ({rain_pct:.0f}% des jours). Prévoyez des alternatives couvertes pour les après-midis.",
                f"La mousson frappe {nom} en {month_lc} — {tmax:.0f}°C et {rain_pct:.0f}% de jours pluvieux. L'ambiance reste vivante mais le programme doit s'adapter aux pluies tropicales.",
            ]
        elif is_hot and is_dry and is_very_sun:
            opts = [
                f"Le soleil règne sur {nom} en {month_lc} : {tmax:.0f}°C, {sun_h:.1f}h de lumière et seulement {rain_pct:.0f}% de jours avec pluie. Les conditions estivales sont au rendez-vous.",
                f"Avec {tmax:.0f}°C et {sun_h:.1f}h de soleil par jour, {nom} en {month_lc} offre des conditions balnéaires proches de l'idéal. La pluie ne s'invite que {rain_pct:.0f}% du temps.",
                f"{month_name} à {nom}, c'est le plein été : {tmax:.0f}°C, ciel dégagé et {sun_h:.1f}h de clarté quotidienne. Le séjour parfait pour qui veut maximiser les heures de plage.",
            ]
        elif is_hot and is_rainy:
            opts = [
                f"{nom} en {month_lc} est chaud ({tmax:.0f}°C) mais les pluies sont présentes {rain_pct:.0f}% du temps. Un programme flexible avec alternatives couvertes s'impose.",
                f"La chaleur ({tmax:.0f}°C) et les averses ({rain_pct:.0f}% des jours) cohabitent à {nom} en {month_lc}. Pensez à alterner plage le matin et visites culturelles l'après-midi.",
                f"Conditions tropicales à {nom} en {month_lc} : {tmax:.0f}°C et {rain_pct:.0f}% de jours pluvieux. Les pluies sont souvent brèves — ne les laissez pas dicter votre programme.",
            ]
        elif is_warm and is_dry and is_sunny:
            opts = [
                f"{nom} en {month_lc} atteint l'équilibre : {tmax:.0f}°C, {sun_h:.1f}h de soleil et {rain_pct:.0f}% de jours avec pluie seulement. Une valeur sûre pour un séjour réussi.",
                f"Douceur et soleil au programme à {nom} en {month_lc} — {tmax:.0f}°C, {sun_h:.1f}h de clarté, rares averses ({rain_pct:.0f}%). Le temps idéal pour conjuguer plein air et découvertes.",
                f"{nom} en {month_lc} mérite sa réputation : {tmax:.0f}°C, {sun_h:.1f}h de soleil et seulement {rain_pct:.0f}% de jours pluvieux — un mois qui coche toutes les cases.",
            ]
        elif is_warm and is_moderate:
            opts = [
                f"À {nom} en {month_lc}, les {tmax:.0f}°C et les {sun_h:.1f}h de soleil sont tempérés par des pluies modérées ({rain_pct:.0f}% des jours). Un bon séjour si vous acceptez quelques averses.",
                f"{month_name} à {nom} alterne soleil ({sun_h:.1f}h/j) et averses ({rain_pct:.0f}% des jours) avec des températures douces ({tmax:.0f}°C). Glissez un imperméable dans le sac.",
                f"Chaud ({tmax:.0f}°C) mais variable : {nom} en {month_lc} propose {sun_h:.1f}h de soleil et {rain_pct:.0f}% de jours pluvieux. La météo est clémente, pas parfaite.",
            ]
        elif is_warm and is_rainy:
            opts = [
                f"{nom} en {month_lc} est doux ({tmax:.0f}°C) mais les pluies touchent {rain_pct:.0f}% des journées — un imperméable de qualité est indispensable.",
                f"Douceur ({tmax:.0f}°C) et pluies fréquentes ({rain_pct:.0f}% des jours) caractérisent {nom} en {month_lc}. Les {sun_h:.1f}h de soleil journalier restent appréciables entre les averses.",
                f"Saison humide à {nom} en {month_lc} : {tmax:.0f}°C mais {rain_pct:.0f}% de jours touchés par la pluie. Les paysages sont souvent magnifiques — chaque saison a ses atouts.",
            ]
        elif is_mild and is_dry:
            opts = [
                f"{nom} en {month_lc} offre une météo douce ({tmax:.0f}°C) et peu pluvieuse ({rain_pct:.0f}%) — idéal pour explorer sans transpirer, avec moins de monde qu'en haute saison.",
                f"Fraîcheur agréable ({tmax:.0f}°C) et ciel clément ({rain_pct:.0f}% de jours pluvieux) : {nom} en {month_lc} convient aux voyageurs qui préfèrent le confort thermique à la chaleur estivale.",
                f"{month_name} à {nom}, c'est la saison idéale pour marcher, visiter et explorer : {tmax:.0f}°C, {sun_h:.1f}h de lumière et seulement {rain_pct:.0f}% de jours humides.",
            ]
        elif is_mild and is_moderate:
            opts = [
                f"Doux ({tmax:.0f}°C) mais arrosé ({rain_pct:.0f}% des jours), {nom} en {month_lc} séduira les voyageurs qui apprécient l'ambiance locale hors-saison et les musées sans files d'attente.",
                f"{month_name} à {nom} : températures agréables ({tmax:.0f}°C), {sun_h:.1f}h de soleil, mais {rain_pct:.0f}% de jours pluvieux. Les activités couvertes complètent bien un séjour.",
                f"Ni trop chaud ni trop froid ({tmax:.0f}°C), mais les pluies sont présentes ({rain_pct:.0f}% des jours) à {nom} en {month_lc}. Une destination qui révèle un visage authentique en cette saison.",
            ]
        elif is_mild and is_rainy:
            opts = [
                f"{nom} en {month_lc} est doux ({tmax:.0f}°C) mais franchement humide — {rain_pct:.0f}% des jours voient de la pluie. La ville ou la région se vit différemment, avec ses charmes propres.",
                f"Saison creuse à {nom} : {tmax:.0f}°C et {rain_pct:.0f}% de jours pluvieux, mais aussi moins de touristes et des prix attractifs. Le bon choix si la météo n'est pas la priorité.",
                f"{month_name} apporte à {nom} fraîcheur ({tmax:.0f}°C) et pluies fréquentes ({rain_pct:.0f}%). L'atmosphère locale, les restaurants et la culture restent pleinement accessibles.",
            ]
        elif is_cool and is_dry:
            opts = [
                f"Frais et sec à {nom} en {month_lc} : {tmax:.0f}°C et seulement {rain_pct:.0f}% de jours pluvieux. Le temps idéal pour marcher et visiter sans transpirer.",
                f"{nom} en {month_lc} offre {tmax:.0f}°C et un ciel souvent clément ({rain_pct:.0f}% de pluie) — les conditions parfaites pour explorer à pied sans les foules estivales.",
                f"Températures fraîches ({tmax:.0f}°C) et faible pluviométrie ({rain_pct:.0f}%) : {nom} en {month_lc} convient aux randonneurs et aux amateurs de visites sans chaleur.",
            ]
        elif is_cool:
            opts = [
                f"{nom} en {month_lc} est frais ({tmax:.0f}°C) avec {sun_h:.1f}h de lumière par jour. La saison creuse révèle une destination plus authentique, moins touristique.",
                f"Fraîcheur et authenticité à {nom} en {month_lc} : {tmax:.0f}°C, {rain_pct:.0f}% de jours pluvieux, et une atmosphère locale que la haute saison ne permet pas de saisir.",
                f"{month_name} à {nom}, c'est la ville pour les locaux : {tmax:.0f}°C, {sun_h:.1f}h de soleil, et des expériences culturelles sans l'affluence touristique.",
            ]
        elif is_cold:
            opts = [
                f"L'hiver s'installe à {nom} en {month_lc} ({tmax:.0f}°C) — habillement chaud indispensable. L'ambiance hivernale a son charme propre, souvent apprécié des voyageurs qui fuient les clichés.",
                f"{nom} en {month_lc} : {tmax:.0f}°C et {sun_h:.1f}h de lumière. Les conditions hivernales n'empêchent pas de profiter de la culture, de la gastronomie et de l'architecture locale.",
                f"Hiver à {nom} en {month_lc} ({tmax:.0f}°C, {rain_pct:.0f}% de jours pluvieux). La destination se découvre différemment — souvent plus sincèrement qu'en haute saison.",
            ]
        else:
            opts = [
                f"{nom} en {month_lc} : {tmax:.0f}°C, {sun_h:.1f}h de soleil et {rain_pct:.0f}% de jours avec pluie. Des conditions {'favorables' if is_good else 'correctes'} pour un séjour.",
                f"Météo {'agréable' if is_good else 'variable'} à {nom} en {month_lc} : {tmax:.0f}°C, {sun_h:.1f}h de clarté, {rain_pct:.0f}% de jours pluvieux.",
            ]
        s.append(pick(opts, seed))

        # ── Phrase 2 : mer ou ensoleillement contextuel ──
        if is_warm_sea:
            sea_opts = [
                f"La mer à {sea_temp:.0f}°C se prête à une baignade sans hésitation.",
                f"Eau à {sea_temp:.0f}°C — les conditions pour la natation et les sports nautiques sont excellentes.",
                f"La mer atteint {sea_temp:.0f}°C, parfaite pour les nageurs et les adeptes de plongée.",
            ]
            s.append(pick(sea_opts, seed+1))
        elif is_swim:
            sea_opts = [
                f"La mer à {sea_temp:.0f}°C reste agréable pour la baignade, même si les amateurs d'eau chaude préféreront d'autres mois.",
                f"Avec {sea_temp:.0f}°C en mer, la baignade est confortable pour la majorité des baigneurs.",
                f"Eau à {sea_temp:.0f}°C — accessible pour nager, idéale pour les sports de glisse.",
            ]
            s.append(pick(sea_opts, seed+1))
        elif is_cool_sea:
            sea_opts = [
                f"La mer reste fraîche ({sea_temp:.0f}°C) — parfaite pour le snorkeling et les activités nautiques, moins pour la baignade prolongée.",
                f"Eau fraîche ({sea_temp:.0f}°C) : les sports nautiques sont envisageables, la baignade longue déconseillée.",
            ]
            s.append(pick(sea_opts, seed+1))
        elif is_very_sun and (is_cool or is_cold or is_rainy or is_moderate):
            sun_opts = [
                f"L'ensoleillement ({sun_h:.1f}h/j) reste le principal atout de cette période.",
                f"Malgré les conditions fraîches, la lumière est au rendez-vous ({sun_h:.1f}h de soleil par jour).",
                f"{sun_h:.1f}h de soleil quotidiennes compensent les températures modestes.",
            ]
            s.append(pick(sun_opts, seed+1))
        elif is_cloudy:
            cloud_opts = [
                f"La lumière reste rare ({sun_h:.1f}h/j) — les musées, la gastronomie et la culture locale prennent alors toute leur valeur.",
                f"Avec seulement {sun_h:.1f}h de soleil par jour, les activités en intérieur s'imposent naturellement.",
            ]
            s.append(pick(cloud_opts, seed+1))

        # ── Phrase 3 : verdict score ──
        if is_best_month and is_peak:
            v3_opts = [
                f"Score {score:.1f}/10 — le meilleur créneau de l'année pour {nom}.",
                f"Score {score:.1f}/10 : difficile de faire mieux pour visiter {nom}.",
                f"Avec {score:.1f}/10, c'est clairement la meilleure période pour {nom}.",
            ]
        elif is_best_month:
            v3_opts = [
                f"Score {score:.1f}/10 — le pic annuel à {nom}, souvent avec plus de monde qu'en épaule.",
                f"Score {score:.1f}/10 : le sommet de l'année pour la météo à {nom}.",
            ]
        elif is_near_peak:
            v3_opts = [
                f"Score {score:.1f}/10 — très proche du pic annuel ({best_month}, {best_score:.1f}/10), souvent avec moins d'affluence.",
                f"Score {score:.1f}/10 : quasi équivalent à {best_month} ({best_score:.1f}/10) avec l'avantage d'une fréquentation réduite.",
                f"À {score:.1f}/10, ce mois rivalise presque avec {best_month} ({best_score:.1f}/10) — et les hôtels y sont souvent moins chers.",
            ]
        elif is_peak or is_good:
            v3_opts = [
                f"Score {score:.1f}/10 : un peu en dessous de {best_month} ({best_score:.1f}/10) mais pleinement recommandable si vos dates sont fixées.",
                f"Score {score:.1f}/10 — inférieur au pic ({best_month}, {best_score:.1f}/10) sans être décevant pour autant.",
                f"À {score:.1f}/10, le séjour reste très satisfaisant, même si {best_month} ({best_score:.1f}/10) offre théoriquement mieux.",
            ]
        elif is_fair:
            v3_opts = [
                f"Score {score:.1f}/10 — si vos dates sont flexibles, {best_month} ({best_score:.1f}/10) offre une météo nettement supérieure.",
                f"Score {score:.1f}/10 : la météo est correcte mais {best_month} ({best_score:.1f}/10) reste la référence pour {nom}.",
                f"À {score:.1f}/10, ce mois convient aux voyageurs sans contraintes de calendrier... mais {best_month} ({best_score:.1f}/10) est clairement préférable.",
            ]
        else:
            v3_opts = [
                f"Score {score:.1f}/10 — l'une des périodes les moins favorables de l'année ; {best_month} ({best_score:.1f}/10) est fortement recommandé à la place.",
                f"Score {score:.1f}/10 : si possible, décalez votre séjour à {best_month} ({best_score:.1f}/10) pour une expérience météo bien meilleure.",
                f"À {score:.1f}/10, ce n'est pas la saison idéale pour {nom} — {best_month} ({best_score:.1f}/10) mérite d'être privilégié.",
            ]
        s.append(pick(v3_opts, seed+2))

    elif lang == 'en':
        if is_very_hot and is_dry:
            opts = [
                f"{nom} in {month_name} is pure heat: {tmax:.0f}°C and relentless sunshine. A dream for sun worshippers, a challenge for everyone else.",
                f"Expect intense heat ({tmax:.0f}°C) and near-constant sun in {nom} in {month_name}. Plan outdoor activities for early morning and enjoy the warm evenings.",
                f"{month_name} is {nom}'s hottest month at {tmax:.0f}°C — ideal for those who want sun without compromise, demanding for sightseers.",
            ]
        elif is_very_hot and is_rainy:
            opts = [
                f"{nom} in {month_name} pairs stifling heat ({tmax:.0f}°C) with frequent rain ({rain_pct:.0f}% of days). Morning activities are your best bet.",
                f"Hot and wet: {nom} in {month_name} delivers {tmax:.0f}°C alongside rain on {rain_pct:.0f}% of days. A flexible itinerary is essential.",
                f"Monsoon season hits {nom} in {month_name} — {tmax:.0f}°C and rain {rain_pct:.0f}% of the time. The destination stays vibrant; your plans need to adapt.",
            ]
        elif is_hot and is_dry and is_very_sun:
            opts = [
                f"{nom} in {month_name} delivers prime summer conditions: {tmax:.0f}°C, {sun_h:.1f} daily sun hours, and just {rain_pct:.0f}% rainy days.",
                f"Classic summer at {nom}: {tmax:.0f}°C, {sun_h:.1f}h of sunshine daily, and barely a cloud in sight ({rain_pct:.0f}% rainy days).",
                f"{month_name} is peak season for a reason in {nom} — {tmax:.0f}°C and {sun_h:.1f}h of sun make for near-perfect conditions.",
            ]
        elif is_warm and is_dry and is_sunny:
            opts = [
                f"{nom} in {month_name} hits the sweet spot: pleasant {tmax:.0f}°C, {sun_h:.1f}h of sun, and only {rain_pct:.0f}% rainy days.",
                f"Reliable and welcoming: {tmax:.0f}°C, {sun_h:.1f}h sunshine and {rain_pct:.0f}% dry days make {month_name} one of {nom}'s most dependable months.",
                f"With {tmax:.0f}°C, {sun_h:.1f} sun hours daily, and rain on just {rain_pct:.0f}% of days, {nom} in {month_name} rarely disappoints.",
            ]
        elif is_warm and (is_moderate or is_rainy):
            opts = [
                f"Warm at {tmax:.0f}°C but variable: {nom} in {month_name} sees rain on {rain_pct:.0f}% of days. A light rain jacket goes a long way.",
                f"{nom} in {month_name} offers pleasant {tmax:.0f}°C with {sun_h:.1f}h of sun, but showers affect {rain_pct:.0f}% of days — pack accordingly.",
                f"The warmth ({tmax:.0f}°C) and sunshine ({sun_h:.1f}h/day) at {nom} in {month_name} are real, but so is the rain on {rain_pct:.0f}% of days.",
            ]
        elif is_mild and is_dry:
            opts = [
                f"Mild ({tmax:.0f}°C) and mostly dry ({rain_pct:.0f}% rainy days): {nom} in {month_name} is great for active exploration without peak heat or crowds.",
                f"{nom} in {month_name} offers {tmax:.0f}°C and {sun_h:.1f}h of daylight with just {rain_pct:.0f}% rainy days — ideal for walkers and sightseers.",
                f"Cool, clear and uncrowded: {tmax:.0f}°C and {rain_pct:.0f}% rainy days make {month_name} an underrated time to visit {nom}.",
            ]
        elif is_mild and (is_moderate or is_rainy):
            opts = [
                f"Mild ({tmax:.0f}°C) but damp ({rain_pct:.0f}% rainy days), {nom} in {month_name} suits travellers who prioritise culture and authenticity over sunshine.",
                f"{nom} in {month_name}: comfortable {tmax:.0f}°C, {sun_h:.1f}h of light, and rain on {rain_pct:.0f}% of days. Museums, restaurants and local life are all fully on.",
                f"The low season mood at {nom} in {month_name} — {tmax:.0f}°C, {rain_pct:.0f}% rainy days, and a genuine local atmosphere that peak season rarely offers.",
            ]
        elif is_cool or is_cold:
            opts = [
                f"{'Cold' if is_cold else 'Cool'} at {tmax:.0f}°C with {sun_h:.1f}h of daylight, {nom} in {month_name} is low season territory — with all the authenticity that brings.",
                f"{nom} in {month_name} runs {'cold' if is_cold else 'cool'} ({tmax:.0f}°C) but {'the snow-covered streets have their own appeal' if is_cold else 'the mild grey days suit unhurried exploration'}.",
                f"{tmax:.0f}°C and {sun_h:.1f}h of light: {nom} in {month_name} is for travellers who don't need sunshine to have a great trip.",
            ]
        else:
            opts = [
                f"{nom} in {month_name}: {tmax:.0f}°C, {sun_h:.1f}h of sun, {rain_pct:.0f}% rainy days — {'solid' if is_good else 'mixed'} conditions overall.",
                f"Expect {tmax:.0f}°C and {sun_h:.1f}h sunshine in {nom} in {month_name}, with rain affecting {rain_pct:.0f}% of days.",
            ]
        s.append(pick(opts, seed))

        if is_warm_sea:
            opts = [f"The sea hits {sea_temp:.0f}°C — swimming and water sports are excellent.",
                    f"Sea at {sea_temp:.0f}°C: perfect for extended swimming and snorkelling.",
                    f"With {sea_temp:.0f}°C water, every beach day is a proper beach day."]
            s.append(pick(opts, seed+1))
        elif is_swim:
            opts = [f"Sea temperature of {sea_temp:.0f}°C makes swimming comfortable for most.",
                    f"The {sea_temp:.0f}°C sea is inviting for a swim, though not tropical-warm.",
                    f"At {sea_temp:.0f}°C, the water is perfectly swimmable."]
            s.append(pick(opts, seed+1))
        elif is_cool_sea:
            opts = [f"The sea is cool at {sea_temp:.0f}°C — good for watersports, less so for long swims.",
                    f"At {sea_temp:.0f}°C the water suits wetsuits more than bikinis."]
            s.append(pick(opts, seed+1))
        elif is_very_sun and (is_cool or is_cold or is_rainy or is_moderate):
            opts = [f"The generous sunshine ({sun_h:.1f}h/day) is the standout feature of this period.",
                    f"{sun_h:.1f} daily sun hours add a silver lining to the cooler conditions."]
            s.append(pick(opts, seed+1))
        elif is_cloudy:
            opts = [f"With only {sun_h:.1f}h of sun daily, indoor experiences take centre stage.",
                    f"Limited light ({sun_h:.1f}h/day) — lean into museums, food and local life."]
            s.append(pick(opts, seed+1))

        if is_best_month and is_peak:
            opts = [f"Score {score:.1f}/10 — the best time of year to visit {nom}.",
                    f"Score {score:.1f}/10: as good as it gets for {nom}.",
                    f"At {score:.1f}/10, this is {nom} at its finest."]
        elif is_best_month:
            opts = [f"Score {score:.1f}/10 — the annual peak for {nom}.",
                    f"Score {score:.1f}/10: the top of the year for weather in {nom}."]
        elif is_near_peak:
            opts = [f"Score {score:.1f}/10 — nearly as good as {best_month} ({best_score:.1f}/10), often with fewer tourists.",
                    f"Score {score:.1f}/10: close to the peak ({best_month}, {best_score:.1f}/10), usually with better availability.",
                    f"At {score:.1f}/10, this rivals {best_month} ({best_score:.1f}/10) — sometimes at a lower price."]
        elif is_peak or is_good:
            opts = [f"Score {score:.1f}/10: below the peak ({best_month}, {best_score:.1f}/10) but fully worthwhile if your dates are set.",
                    f"Score {score:.1f}/10 — not the top month but a genuinely good time to be in {nom}.",
                    f"At {score:.1f}/10, you won't be disappointed — {best_month} ({best_score:.1f}/10) is simply better."]
        elif is_fair:
            opts = [f"Score {score:.1f}/10 — if flexible, {best_month} ({best_score:.1f}/10) offers noticeably better weather.",
                    f"Score {score:.1f}/10: decent but {best_month} ({best_score:.1f}/10) is worth waiting for if possible.",
                    f"At {score:.1f}/10, the weather is passable — {best_month} ({best_score:.1f}/10) would be a clear upgrade."]
        else:
            opts = [f"Score {score:.1f}/10 — one of the tougher months in {nom}; {best_month} ({best_score:.1f}/10) is strongly recommended instead.",
                    f"Score {score:.1f}/10: the weather is genuinely difficult. {best_month} ({best_score:.1f}/10) is the obvious alternative.",
                    f"At {score:.1f}/10, this is off-peak for a reason — {best_month} ({best_score:.1f}/10) transforms the experience."]
        s.append(pick(opts, seed+2))

    elif lang == 'es':
        if is_very_hot and is_dry:
            opts = [
                f"{nom} en {month_lc} es puro calor: {tmax:.0f}°C y sol implacable. El sueño de los amantes del bronceado, un desafío para los demás.",
                f"Calor extremo ({tmax:.0f}°C) y cielo despejado definen {nom} en {month_lc}. Planifica las salidas en las horas frescas.",
            ]
        elif is_hot and is_dry and is_very_sun:
            opts = [
                f"{nom} en {month_lc} ofrece condiciones estivales de primer nivel: {tmax:.0f}°C, {sun_h:.1f}h de sol y solo {rain_pct:.0f}% de días lluviosos.",
                f"Clásico verano en {nom}: {tmax:.0f}°C, {sun_h:.1f}h de sol diarias y apenas lluvia ({rain_pct:.0f}% de días).",
            ]
        elif is_warm and is_dry and is_sunny:
            opts = [
                f"{nom} en {month_lc} da en el clavo: {tmax:.0f}°C agradables, {sun_h:.1f}h de sol y solo {rain_pct:.0f}% de días con lluvia.",
                f"Fiable y acogedor: {tmax:.0f}°C, {sun_h:.1f}h de sol y {rain_pct:.0f}% de días secos hacen de {month_name.lower()} uno de los mejores meses en {nom}.",
            ]
        elif is_warm and (is_moderate or is_rainy):
            opts = [
                f"Cálido ({tmax:.0f}°C) pero variable: {nom} en {month_lc} registra lluvia en el {rain_pct:.0f}% de los días. Un chubasquero ligero es imprescindible.",
                f"{nom} en {month_lc} ofrece {tmax:.0f}°C con {sun_h:.1f}h de sol, pero la lluvia afecta al {rain_pct:.0f}% de los días.",
            ]
        elif is_mild and is_dry:
            opts = [
                f"Suave ({tmax:.0f}°C) y seco ({rain_pct:.0f}% de días lluviosos): {nom} en {month_lc} es ideal para explorar sin calor ni multitudes.",
                f"{nom} en {month_lc} brinda {tmax:.0f}°C y solo {rain_pct:.0f}% de días con lluvia — perfecto para los viajeros activos.",
            ]
        elif is_cool or is_cold:
            opts = [
                f"{'Frío' if is_cold else 'Fresco'} ({tmax:.0f}°C) con {sun_h:.1f}h de luz: {nom} en {month_lc} es temporada baja con toda su autenticidad.",
                f"{nom} en {month_lc} ({tmax:.0f}°C) ofrece una experiencia más genuina, lejos del turismo masivo.",
            ]
        else:
            opts = [
                f"{nom} en {month_lc}: {tmax:.0f}°C, {sun_h:.1f}h de sol y {rain_pct:.0f}% de días con lluvia — condiciones {'favorables' if is_good else 'aceptables'}.",
            ]
        s.append(pick(opts, seed))

        if is_warm_sea:
            s.append(pick([f"El mar a {sea_temp:.0f}°C invita al baño sin reservas.",
                           f"Mar a {sea_temp:.0f}°C — ideal para nadar y hacer deportes acuáticos."], seed+1))
        elif is_swim:
            s.append(pick([f"Mar a {sea_temp:.0f}°C: el baño es cómodo para la mayoría.",
                           f"El agua a {sea_temp:.0f}°C está lista para disfrutarla."], seed+1))
        elif is_cool_sea:
            s.append(f"El mar está fresco ({sea_temp:.0f}°C) — deportes acuáticos posibles, baño prolongado no recomendado.")

        if is_best_month and is_peak:
            s.append(pick([f"Puntuación {score:.1f}/10 — la mejor época del año para visitar {nom}.",
                           f"Con {score:.1f}/10, este es el momento álgido en {nom}."], seed+2))
        elif is_near_peak:
            s.append(pick([f"Puntuación {score:.1f}/10 — casi tan bueno como {best_month} ({best_score:.1f}/10), a menudo con menos turistas.",
                           f"Puntuación {score:.1f}/10: rivaliza con el pico ({best_month}, {best_score:.1f}/10), normalmente con mejor disponibilidad."], seed+2))
        elif is_peak or is_good:
            s.append(pick([f"Puntuación {score:.1f}/10: por debajo del pico ({best_month}, {best_score:.1f}/10) pero plenamente recomendable.",
                           f"Con {score:.1f}/10, no te decepcionará — {best_month} ({best_score:.1f}/10) sencillamente es mejor."], seed+2))
        elif is_fair:
            s.append(f"Puntuación {score:.1f}/10 — con flexibilidad, {best_month} ({best_score:.1f}/10) ofrece condiciones notablemente mejores.")
        else:
            s.append(f"Puntuación {score:.1f}/10 — uno de los peores meses en {nom}; {best_month} ({best_score:.1f}/10) es muy preferible.")

    elif lang == 'de':
        if is_very_hot and is_dry:
            opts = [
                f"{nom} im {month_name}: intensive Hitze ({tmax:.0f}°C) und fast ununterbrochener Sonnenschein. Ideal für Sonnenanbeter, anspruchsvoll für alle anderen.",
                f"Extrem heiß ({tmax:.0f}°C) und strahlend sonnig — {nom} im {month_name} ist die perfekte Wahl für absolute Sonnenliebhaber.",
            ]
        elif is_hot and is_dry and is_very_sun:
            opts = [
                f"{nom} im {month_name} bietet besten Sommer: {tmax:.0f}°C, {sun_h:.1f}h Sonne täglich, nur {rain_pct:.0f}% Regentage.",
                f"Klassischer Hochsommer in {nom}: {tmax:.0f}°C, {sun_h:.1f}h Sonnenschein und kaum Regen ({rain_pct:.0f}% der Tage).",
            ]
        elif is_warm and is_dry and is_sunny:
            opts = [
                f"{nom} im {month_name} trifft den Sweet Spot: angenehme {tmax:.0f}°C, {sun_h:.1f}h Sonne und nur {rain_pct:.0f}% Regentage.",
                f"Zuverlässig und einladend: {tmax:.0f}°C, {sun_h:.1f}h Sonne und {rain_pct:.0f}% trockene Tage machen {month_name} zu einem der besten Monate in {nom}.",
            ]
        elif is_warm and (is_moderate or is_rainy):
            opts = [
                f"Warm ({tmax:.0f}°C) aber wechselhaft: {nom} im {month_name} sieht Regen an {rain_pct:.0f}% der Tage. Eine leichte Regenjacke gehört ins Gepäck.",
                f"{nom} im {month_name} bietet {tmax:.0f}°C und {sun_h:.1f}h Sonne, aber Regen betrifft {rain_pct:.0f}% der Tage.",
            ]
        elif is_mild and is_dry:
            opts = [
                f"Mild ({tmax:.0f}°C) und meist trocken ({rain_pct:.0f}% Regentage): {nom} im {month_name} lädt zur aktiven Entdeckungsreise ohne Hitze und Menschenmassen ein.",
                f"{nom} im {month_name}: {tmax:.0f}°C und {sun_h:.1f}h Tageslicht bei nur {rain_pct:.0f}% Regentagen — ideal für Wanderer und Kulturinteressierte.",
            ]
        elif is_cool or is_cold:
            opts = [
                f"{'Kalt' if is_cold else 'Kühl'} ({tmax:.0f}°C) mit {sun_h:.1f}h Tageslicht: {nom} im {month_name} ist Nebensaison — mit all der Authentizität, die das mit sich bringt.",
                f"{nom} im {month_name} ({tmax:.0f}°C) zeigt sich von seiner ruhigeren, einheimischen Seite.",
            ]
        else:
            opts = [
                f"{nom} im {month_name}: {tmax:.0f}°C, {sun_h:.1f}h Sonne und {rain_pct:.0f}% Regentage — {'gute' if is_good else 'akzeptable'} Bedingungen.",
            ]
        s.append(pick(opts, seed))

        if is_warm_sea:
            s.append(pick([f"Das Meer erreicht {sea_temp:.0f}°C — ausgezeichnet zum Schwimmen und für Wassersport.",
                           f"Wassertemperatur {sea_temp:.0f}°C: jeder Strandtag ist ein echter Badetag."], seed+1))
        elif is_swim:
            s.append(pick([f"Das Meer ist mit {sea_temp:.0f}°C angenehm zum Baden.",
                           f"Bei {sea_temp:.0f}°C Wassertemperatur ist Schwimmen für die meisten Besucher komfortabel."], seed+1))
        elif is_cool_sea:
            s.append(f"Das Meer ist kühl ({sea_temp:.0f}°C) — Wassersport möglich, längeres Schwimmen nicht empfohlen.")
        elif is_very_sun and (is_cool or is_cold or is_rainy or is_moderate):
            s.append(f"{sun_h:.1f}h Sonnenschein täglich sind das Hauptargument für diesen Monat.")
        elif is_cloudy:
            s.append(f"Wenig Licht ({sun_h:.1f}h/Tag) — Museums- und Kulturprogramm steht im Vordergrund.")

        if is_best_month and is_peak:
            s.append(pick([f"Bewertung {score:.1f}/10 — die beste Reisezeit des Jahres für {nom}.",
                           f"Mit {score:.1f}/10 ist dies die Hochsaison für Wetter in {nom}."], seed+2))
        elif is_near_peak:
            s.append(pick([f"Bewertung {score:.1f}/10 — fast so gut wie {best_month} ({best_score:.1f}/10), oft mit weniger Touristen.",
                           f"Bewertung {score:.1f}/10: knapp unter dem Jahreshöhepunkt ({best_month}, {best_score:.1f}/10), meist mit besserer Verfügbarkeit."], seed+2))
        elif is_peak or is_good:
            s.append(pick([f"Bewertung {score:.1f}/10: unter dem Spitzenmonat ({best_month}, {best_score:.1f}/10), aber bei festen Terminen durchaus empfehlenswert.",
                           f"Mit {score:.1f}/10 lohnt sich der Besuch — {best_month} ({best_score:.1f}/10) ist schlicht besser."], seed+2))
        elif is_fair:
            s.append(f"Bewertung {score:.1f}/10 — bei Flexibilität ist {best_month} ({best_score:.1f}/10) deutlich vorzuziehen.")
        else:
            s.append(f"Bewertung {score:.1f}/10 — einer der schwierigeren Monate; {best_month} ({best_score:.1f}/10) ist klar zu bevorzugen.")

    return ' '.join(s[:3])


def main():
    climate_rows = []
    with open(CLIMATE_FILE, encoding='utf-8-sig') as f:
        climate_rows = list(csv.DictReader(f))

    dests_rows = []
    with open(DESTS_FILE, encoding='utf-8-sig') as f:
        dests_rows = list(csv.DictReader(f))

    dests_map = {r['slug_fr']: r for r in dests_rows}

    climate_by_slug = {}
    for r in climate_rows:
        slug = r['slug']
        if slug not in climate_by_slug:
            climate_by_slug[slug] = []
        climate_by_slug[slug].append(r)

    editorial = {}
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, encoding='utf-8') as f:
            editorial = json.load(f)

    already = len(editorial)
    added = 0

    for slug, months in sorted(climate_by_slug.items()):
        dest = dests_map.get(slug)
        if not dest:
            continue

        best_row = max(months, key=lambda r: float(r['score']))

        coastal = dest.get('coastal','False').strip().lower() == 'true'
        tropical = dest.get('tropical','False').strip().lower() == 'true'
        mountain = dest.get('mountain','False').strip().lower() == 'true'

        for row in sorted(months, key=lambda r: int(r['mois_num'])):
            mi = int(row['mois_num'])
            tmin = float(row['tmin'])
            tmax = float(row['tmax'])
            rain = float(row['rain_pct'])
            precip = float(row['precip_mm'])
            sun = float(row['sun_h'])
            score = float(row['score'])
            sea = float(row['sea_temp']) if row.get('sea_temp','').strip() and row['sea_temp'] not in ('nan','') else None
            best_score = float(best_row['score'])

            for lang in ['fr', 'en', 'es', 'de']:
                key = f"{slug}:{mi}:{lang}"
                if key in editorial:
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

                text = gen(slug, nom, pays, month_name, month_lc, mi,
                           tmin, tmax, rain, precip, sun, score, sea,
                           best_month, best_month_lc, best_score, lang,
                           coastal, tropical, mountain)

                editorial[key] = text
                added += 1

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(editorial, f, ensure_ascii=False, indent=2)

    print(f"✅ editorial.json : {already} existants + {added} ajoutés = {len(editorial)} total")

if __name__ == '__main__':
    main()
