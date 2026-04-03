#!/usr/bin/env python3
"""
fetch_photos_v2.py — Fetch Unsplash hero photos, magnifiques et idiomatiques.

Améliorations vs v1 :
  - Requêtes spécialisées par type de destination (+ overrides manuels)
  - Scoring : localisation > likes (on préfère pertinence à popularité)
  - Double passe : requête précise d'abord, fallback large ensuite
  - Seuil de score plus bas : accept dès que la photo est locale

Usage:
  UNSPLASH_KEY=xxx python3 scripts/fetch_photos_v2.py
"""

import csv, json, os, sys, time, urllib.request, urllib.parse

UNSPLASH_KEY = os.environ.get("UNSPLASH_KEY", "")
DEST_CSV     = "data/destinations.csv"
PHOTOS_CSV   = "data/destination_photos.csv"
SLEEP_SEC    = 80  # 50 req/h demo key → 72s min, 80s safe

# Tags à éviter absolument
SKIP_TAGS = {'portrait','person','people','food','dish','restaurant',
             'interior','indoor','bedroom','cooking','meal','drink','cafe'}

# Overrides manuels : requêtes spécifiques pour destinations rares
QUERY_OVERRIDES = {
    'lalibela':        'Lalibela rock churches Ethiopia',
    'jinja':           'Jinja source Nile Uganda',
    'lamu':            'Lamu island Kenya old town',
    'livingstone':     'Victoria Falls Zimbabwe Zambia',
    'maun':            'Okavango Delta Botswana',
    'tofo':            'Tofo beach Mozambique ocean',
    'etosha':          'Etosha National Park Namibia wildlife',
    'wadi-rum':        'Wadi Rum desert Jordan red rock',
    'al-ula':          'AlUla Hegra Saudi Arabia desert rock',
    'aqaba':           'Aqaba Red Sea Jordan coral reef',
    'salalah':         'Salalah Oman green mountains monsoon',
    'ras-al-khaimah':  'Ras Al Khaimah mountain UAE',
    'raja-ampat':      'Raja Ampat Papua Indonesia turquoise bay',
    'labuan-bajo':     'Labuan Bajo Komodo Indonesia sunset',
    'chiang-rai':      'Chiang Rai White Temple Thailand',
    'ninh-binh':       'Ninh Binh Tam Coc limestone Vietnam',
    'coron':           'Coron Palawan Philippines lagoon',
    'battambang':      'Battambang Cambodia temple',
    'luzon':           'Batad rice terraces Banaue Philippines',
    'nara':            'Nara deer Japan pagoda',
    'zhangjiajie':     'Zhangjiajie Avatar mountains China',
    'nagasaki':        'Nagasaki Japan harbor colorful',
    'lijiang':         'Lijiang old town Yunnan China',
    'hampi':           'Hampi ruins Karnataka India',
    'kochi':           'Kochi Kerala backwaters India',
    'bhutan':          'Bhutan Tiger Nest monastery mountain',
    'ella':            'Ella Nine Arch Bridge Sri Lanka',
    'pokhara':         'Pokhara Phewa Lake Annapurna Nepal',
    'boukhara':        'Bukhara old city Uzbekistan mosque',
    'khiva':           'Khiva Itchan Kala Uzbekistan',
    'sedona':          'Sedona red rock formation Arizona',
    'napa-valley':     'Napa Valley vineyard California wine',
    'jackson-hole':    'Jackson Hole Grand Teton Wyoming',
    'anchorage':       'Anchorage Alaska mountains wilderness',
    'san-antonio':     'San Antonio River Walk Texas',
    'memphis':         'Memphis Tennessee Mississippi river',
    'maui':            'Maui Hawaii Road to Hana waterfall',
    'dominique':       'Dominica Caribbean rainforest waterfall',
    'tobago':          'Tobago Caribbean beach coral reef',
    'saint-kitts':     'Saint Kitts Caribbean volcanic island',
    'antigua':         'Antigua Caribbean sailing harbor',
    'montserrat':      'Montserrat Caribbean volcano island',
    'iles-turques':    'Turks Caicos turquoise beach',
    'cap-vert':        'Cape Verde islands beach dunes',
    'sao-tome':        'Sao Tome island tropical forest',
    'comores':         'Comoros island Indian Ocean beach',
    'mayotte':         'Mayotte lagoon Indian Ocean',
    'reunion-island':  'Reunion island volcano Piton de la Fournaise',
    'rodrigues':       'Rodrigues island Mauritius beach',
    'socotra':         'Socotra island Dragon Blood tree Yemen',
    'palolem':         'Palolem beach Goa India crescent',
    'coorg':           'Coorg coffee plantation Karnataka India',
    'munnar':          'Munnar tea plantation Kerala India',
    'darjeeling':      'Darjeeling tea garden Himalayas India',
    'shimla':          'Shimla Himalayas colonial India',
    'amritsar':        'Golden Temple Amritsar Punjab India',
    'varanasi':        'Varanasi ghats Ganges India sunrise',
    'khajuraho':       'Khajuraho temple UNESCO India',
    'orchha':          'Orchha fort Madhya Pradesh India',
    'udaipur':         'Udaipur lake palace Rajasthan India',
    'jaisalmer':       'Jaisalmer golden fort desert Rajasthan',
    'pushkar':         'Pushkar lake camel Rajasthan India',
    'mcleod-ganj':     'McLeod Ganj Dharamsala Tibet India',
    'kaziranga':       'Kaziranga one-horned rhino Assam India',
    'andaman':         'Andaman islands beach tropical India',
    'yosemite':        'Yosemite Valley El Capitan waterfall',
    'zion':            'Zion National Park canyon Utah',
    'bryce':           'Bryce Canyon hoodoos Utah',
    'moab':            'Arches National Park Utah desert arch',
    'yellowstone':     'Yellowstone geyser bison thermal',
    'glacier':         'Glacier National Park Montana mountain lake',
    'death-valley':    'Death Valley sand dunes California',
    'grand-canyon':    'Grand Canyon Colorado River Arizona',
    'banff':           'Banff Lake Louise Alberta Canada mountain',
    'jasper':          'Jasper Alberta Canada wilderness',
    'whistler':        'Whistler mountain British Columbia ski',
    'tofino':          'Tofino Pacific coast British Columbia waves',
    'charlottetown':   'Prince Edward Island Canada lighthouse',
    'gros-morne':      'Gros Morne Newfoundland fjord Canada',
    'niagara':         'Niagara Falls Canada mist',
    'wengen':          'Wengen Jungfrau Alps Switzerland',
    'grindelwald':     'Grindelwald Eiger Alps Switzerland',
    'zermatt':         'Zermatt Matterhorn Alps Switzerland',
    'verbier':         'Verbier Alps Switzerland ski',
    'saas-fee':        'Saas-Fee Alps Switzerland glacier',
    'davos':           'Davos Alps Switzerland winter',
    'st-moritz':       'St Moritz Alps Switzerland lake winter',
    'chamonix':        'Chamonix Mont Blanc Alps France',
    'val-disere':      'Val d\'Isere French Alps ski',
    'courchevel':      'Courchevel Alps France ski luxury',
    'megeve':          'Megève Alps France winter village',
    'annecy':          'Annecy lake Alps France medieval',
    'les-gets':        'Les Gets Alps France mountain village',
    'morzine':         'Morzine Alps France ski',
    'alpe-dhuez':      'Alpe d\'Huez Alps France ski',
    'serre-chevalier': 'Serre Chevalier Alps France mountain',
    'les-deux-alpes':  'Les Deux Alpes France glacier ski',
    'ischgl':          'Ischgl Tyrol Austria Alps ski',
    'lech':            'Lech Vorarlberg Austria Alps winter',
    'kitzbuhel':       'Kitzbühel Austria Alps ski',
    'innsbruck':       'Innsbruck Alps Austria old town',
    'hallstatt':       'Hallstatt lake Austria alpine village',
    'salzburg':        'Salzburg baroque Mozart Austria',
    'cortina':         'Cortina d\'Ampezzo Dolomites Italy',
    'courmayeur':      'Courmayeur Mont Blanc Italy Alps',
    'cervinia':        'Cervinia Matterhorn Italy ski',
    'livigno':         'Livigno Alps Italy ski',
    'madonna':         'Madonna di Campiglio Dolomites Italy',
    'sestriere':       'Sestriere Alps Italy ski',
    'bormio':          'Bormio Lombardy Alps Italy',
    'val-gardena':     'Val Gardena Dolomites Italy summer',
    'alta-badia':      'Alta Badia Dolomites Italy mountain',
    'lago-di-garda':   'Lake Garda Italy mountains',
    'positano':        'Positano Amalfi coast Italy colorful',
    'procida':         'Procida island Italy colorful harbor',
    'matera':          'Matera Sassi cave dwellings Italy',
    'tropea':          'Tropea Calabria Italy cliff sea',
    'alghero':         'Alghero Sardinia Italy old town sea',
    'san-gimignano':   'San Gimignano Tuscany Italy towers',
    'siena':           'Siena Piazza del Campo Tuscany Italy',
    'lucca':           'Lucca walls Tuscany Italy',
    'assisi':          'Assisi Umbria Italy basilica',
    'padova':          'Padova Piazza dei Signori Italy',
    'verona':          'Verona Arena Romeo Juliet Italy',
    'trieste':         'Trieste Miramare castle Adriatic Italy',
    'taormina':        'Taormina Sicily Etna ancient theater',
    'agrigento':       'Agrigento Valley of Temples Sicily',
    'palermo':         'Palermo Sicily street market cathedral',
    'ragusa':          'Ragusa Ibla baroque Sicily',
    'noto':            'Noto baroque architecture Sicily',
    'pitigliano':      'Pitigliano tufa cliff Tuscany Italy',
    'civita':          'Civita di Bagnoregio dying city Italy',
    'norcia':          'Norcia Sibillini mountains Umbria Italy',
    'abruzzo':         'Abruzzo mountains national park Italy',
}

def score_photo(photo, nom_en, country_en, query):
    score = 0
    tags = [t.get('title','').lower() for t in photo.get('tags', [])]
    desc = (photo.get('description') or photo.get('alt_description') or '').lower()
    nom_lower = nom_en.lower()
    country_lower = (country_en or '').lower()

    # 1. Localisation — signal le plus fort
    nom_words = [w for w in nom_lower.split() if len(w) > 3]
    if any(any(w in t for w in nom_words) for t in tags):
        score += 50
    if any(w in t for t in tags for w in country_lower.split() if len(w) > 3):
        score += 15
    if any(w in desc for w in nom_words):
        score += 25
    if country_lower in desc:
        score += 8

    # 2. Mots du query dans les tags/desc
    query_words = [w for w in query.lower().split() if len(w) > 4]
    desc_and_tags = desc + ' ' + ' '.join(tags)
    matches = sum(1 for w in query_words if w in desc_and_tags)
    score += matches * 5

    # 3. Likes — signal qualité, moins important que localisation
    likes = photo.get('likes', 0)
    if likes > 1000: score += 15
    elif likes > 300: score += 10
    elif likes > 100: score += 6
    elif likes > 30:  score += 3

    # 4. Pénalités
    if any(t in SKIP_TAGS for t in tags): score -= 40
    if 'map' in tags or 'icon' in tags:   score -= 20

    # 5. Orientation paysage
    w, h = photo.get('width', 1), photo.get('height', 1)
    if w > h * 1.3: score += 5

    return score


def search_unsplash(query, nom_en, country_en, access_key, per_page=10):
    params = urllib.parse.urlencode({
        "query": query, "per_page": per_page,
        "orientation": "landscape", "order_by": "relevant",
    })
    url = f"https://api.unsplash.com/search/photos?{params}"
    req = urllib.request.Request(url, headers={
        "Authorization": f"Client-ID {access_key}",
        "Accept-Version": "v1",
    })
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            remaining = r.headers.get("X-Ratelimit-Remaining", "?")
            data = json.loads(r.read())
        results = data.get("results", [])
        if not results:
            return None, remaining

        scored = sorted(
            [(score_photo(p, nom_en, country_en, query), p) for p in results],
            key=lambda x: -x[0]
        )
        best_score, photo = scored[0]

        if best_score < 3:
            return None, remaining

        photo_id = photo["id"]
        url_cdn  = photo["urls"]["raw"] + "&w=1400&q=85&fm=jpg&fit=crop&crop=entropy"
        username = photo["user"]["username"]
        utm = "utm_source=bestdateweather&utm_medium=referral"
        return {
            "url":          url_cdn,
            "credit_name":  photo["user"]["name"],
            "credit_url":   f"https://unsplash.com/@{username}?{utm}",
            "photo_url":    f"https://unsplash.com/photos/{photo_id}?{utm}",
            "_score":       best_score,
            "_likes":       photo.get("likes", 0),
            "_desc":        (photo.get("description") or photo.get("alt_description") or "")[:60],
        }, remaining
    except Exception as e:
        print(f"  [ERROR] {e}")
        return None, "?"


def build_queries(dest):
    slug    = dest.get("slug_fr", "")
    nom     = dest.get("nom_en") or dest.get("nom_bare") or dest.get("nom_fr", "")
    country = dest.get("country_en") or dest.get("pays", "")
    is_mountain = dest.get("mountain", "False").strip() == "True"
    is_coastal  = dest.get("coastal",  "False").strip() == "True"
    is_tropical = dest.get("tropical", "False").strip() == "True"

    # Override manuel en priorité
    if slug in QUERY_OVERRIDES:
        return [QUERY_OVERRIDES[slug], f"{nom} {country}"], nom, country

    # Requête contextuelle
    if is_mountain:
        q1 = f"{nom} {country} mountain alpine"
        q2 = f"{nom} {country} landscape"
    elif is_coastal and is_tropical:
        q1 = f"{nom} {country} beach turquoise"
        q2 = f"{nom} {country} island"
    elif is_coastal:
        q1 = f"{nom} {country} coast sea"
        q2 = f"{nom} {country} harbor"
    else:
        q1 = f"{nom} {country} landmark"
        q2 = f"{nom} {country} city"

    return [q1, q2, f"{nom} {country}"], nom, country


def main():
    if not UNSPLASH_KEY:
        print("UNSPLASH_KEY not set")
        sys.exit(1)

    dests = list(csv.DictReader(open(DEST_CSV, encoding="utf-8-sig")))
    existing = {}
    if os.path.exists(PHOTOS_CSV):
        for row in csv.DictReader(open(PHOTOS_CSV, encoding="utf-8")):
            if row.get("photo_url", "").strip():
                existing[row["slug_fr"]] = row

    to_process = [d for d in dests if d["slug_fr"] not in existing]
    print(f"Total: {len(dests)} | Done: {len(existing)} | Remaining: {len(to_process)}")

    with open(PHOTOS_CSV, "a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "slug_fr","photo_url","photo_credit_name","photo_credit_url","photo_page_url"
        ])

        for i, dest in enumerate(to_process, 1):
            slug = dest["slug_fr"]
            queries, nom_en, country_en = build_queries(dest)
            print(f"[{i:3}/{len(to_process)}] {slug:30}", end=" ", flush=True)

            photo, remaining = None, "?"
            for q in queries:
                photo, remaining = search_unsplash(q, nom_en, country_en, UNSPLASH_KEY)
                if photo:
                    break

            if photo:
                writer.writerow({
                    "slug_fr":           slug,
                    "photo_url":         photo["url"],
                    "photo_credit_name": photo["credit_name"],
                    "photo_credit_url":  photo["credit_url"],
                    "photo_page_url":    photo["photo_url"],
                })
                f.flush()
                print(f"✓ score={photo['_score']:3} likes={photo['_likes']:5} | {photo['_desc'][:50]}")
            else:
                writer.writerow({
                    "slug_fr": slug, "photo_url": "",
                    "photo_credit_name": "", "photo_credit_url": "", "photo_page_url": ""
                })
                f.flush()
                print(f"✗ no result")

            try:
                rem = int(remaining)
                if rem <= 3:
                    print(f"⏳ Rate limit, sleeping 3600s...")
                    time.sleep(3600)
                else:
                    time.sleep(SLEEP_SEC)
            except (ValueError, TypeError):
                time.sleep(SLEEP_SEC)

    print(f"\n✅ Done.")

if __name__ == "__main__":
    main()
