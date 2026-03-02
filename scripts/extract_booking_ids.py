#!/usr/bin/env python3
"""
extract_booking_ids.py
======================
Fetches Booking.com city pages and extracts dest_id from internal links.

The city pages (e.g. booking.com/city/fr/paris.html) contain internal links 
with &city={dest_id} parameters that we can extract.

Usage:
    python3 scripts/extract_booking_ids.py

Output: data/booking_ids_extracted.csv
Then run: python3 scripts/merge_booking_ids.py data/booking_ids_extracted.csv
"""
import csv, re, os, sys, time, json
from urllib.request import urlopen, Request
from urllib.parse import unquote

DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(DIR, 'data', 'destinations.csv')
OUTPUT = os.path.join(DIR, 'data', 'booking_ids_extracted.csv')

COUNTRY_CODES = {
    'France': 'fr', 'Spain': 'es', 'Italy': 'it', 'Greece': 'gr', 'Turkey': 'tr',
    'Portugal': 'pt', 'Germany': 'de', 'United Kingdom': 'gb', 'Ireland': 'ie',
    'Croatia': 'hr', 'Morocco': 'ma', 'Tunisia': 'tn', 'Egypt': 'eg', 'Japan': 'jp',
    'Thailand': 'th', 'Vietnam': 'vn', 'Indonesia': 'id', 'India': 'in', 'China': 'cn',
    'South Korea': 'kr', 'Philippines': 'ph', 'Malaysia': 'my', 'Myanmar': 'mm',
    'Cambodia': 'kh', 'Laos': 'la', 'Sri Lanka': 'lk', 'Nepal': 'np',
    'United States': 'us', 'USA': 'us', 'Canada': 'ca', 'Mexico': 'mx',
    'Brazil': 'br', 'Argentina': 'ar', 'Colombia': 'co', 'Peru': 'pe', 'Chile': 'cl',
    'Ecuador': 'ec', 'Bolivia': 'bo', 'Uruguay': 'uy', 'Paraguay': 'py',
    'Costa Rica': 'cr', 'Panama': 'pa', 'Guatemala': 'gt', 'Belize': 'bz',
    'Nicaragua': 'ni', 'Dominican Republic': 'do', 'Jamaica': 'jm', 'Cuba': 'cu',
    'Australia': 'au', 'New Zealand': 'nz', 'Fiji': 'fj',
    'UAE': 'ae', 'Qatar': 'qa', 'Oman': 'om', 'Jordan': 'jo', 'Israel': 'il',
    'Saudi Arabia': 'sa', 'Lebanon': 'lb', 'Kuwait': 'kw', 'Bahrain': 'bh', 'Iran': 'ir',
    'South Africa': 'za', 'Kenya': 'ke', 'Tanzania': 'tz', 'Namibia': 'na',
    'Madagascar': 'mg', 'Mauritius': 'mu', 'Senegal': 'sn', 'Cape Verde': 'cv',
    'Rwanda': 'rw', 'Ethiopia': 'et', 'Uganda': 'ug', 'Zimbabwe': 'zw',
    'Ghana': 'gh', 'Nigeria': 'ng', 'Ivory Coast': 'ci', 'Mozambique': 'mz',
    'Denmark': 'dk', 'Sweden': 'se', 'Norway': 'no', 'Finland': 'fi',
    'Poland': 'pl', 'Hungary': 'hu', 'Czech Republic': 'cz', 'Romania': 'ro',
    'Bulgaria': 'bg', 'Serbia': 'rs', 'Albania': 'al', 'Montenegro': 'me',
    'North Macedonia': 'mk', 'Bosnia and Herzegovina': 'ba', 'Slovenia': 'si',
    'Slovakia': 'sk', 'Estonia': 'ee', 'Latvia': 'lv', 'Lithuania': 'lt',
    'Belgium': 'be', 'Netherlands': 'nl', 'Switzerland': 'ch', 'Austria': 'at',
    'Malta': 'mt', 'Cyprus': 'cy', 'Georgia': 'ge', 'Armenia': 'am',
    'Uzbekistan': 'uz', 'Kazakhstan': 'kz', 'Kyrgyzstan': 'kg',
    'Taiwan': 'tw', 'Barbados': 'bb', 'Puerto Rico': 'pr',
    'French Polynesia': 'pf', 'New Caledonia': 'nc',
    'Guadeloupe': 'gp', 'Martinique': 'mq', 'Mayotte': 'yt',
    'French Guiana': 'gf', 'Curaçao': 'cw', 'Aruba': 'aw',
    'Bermuda': 'bm', 'Bahamas': 'bs', 'Saint Lucia': 'lc',
    'Antigua and Barbuda': 'ag', 'Trinidad and Tobago': 'tt',
    'Turks and Caicos': 'tc', 'Cook Islands': 'ck',
    'Samoa': 'ws', 'Vanuatu': 'vu', 'Tonga': 'to',
    'Saint Martin': 'mf', 'Saint Barthélemy': 'bl',
    'Saint-Pierre and Miquelon': 'pm',
}

# Override booking.com city slugs where they differ from nom_en
SLUG_OVERRIDES = {
    'chamonix': 'chamonix-mont-blanc',
    'le-cap': 'cape-town',
    'athenes': 'athens',
    'copenhague': 'copenhagen',
    'cracovie': 'krakow',
    'pekin': 'beijing',
    'varsovie': 'warsaw',
    'bucarest': 'bucharest',
    'bruxelles': 'brussels',
    'geneve': 'geneva',
    'thessalonique': 'thessaloniki',
    'pouilles': 'puglia',
    'lac-garde': 'lake-garda',
    'lac-come': 'lake-como',
    'palerme': 'palermo',
    'cadix': 'cadiz',
    'saint-sebastien': 'san-sebastian',
    'cordoue': 'cordoba',
    'munich': 'munich',
    'hambourg': 'hamburg',
    'francfort': 'frankfurt',
    'tromso': 'tromso',
    'bergen': 'bergen',
    'le-caire': 'cairo',
    'louxor': 'luxor',
    'abu-dhabi': 'abu-dhabi',
    'tel-aviv': 'tel-aviv',
    'chiang-mai': 'chiang-mai',
    'koh-samui': 'ko-samui',
    'hanoi': 'hanoi',
    'ho-chi-minh': 'ho-chi-minh-city',
    'hong-kong': 'hong-kong',
    'kuala-lumpur': 'kuala-lumpur',
    'quebec-ville': 'quebec',
    'nouvelle-orleans': 'new-orleans',
    'punta-cana': 'punta-cana',
    'playa-del-carmen': 'playa-del-carmen',
    'cabo-san-lucas': 'cabo-san-lucas',
    'puerto-vallarta': 'puerto-vallarta',
    'mexico': 'mexico-city',
    'medellin': 'medellin',
    'machu-picchu': 'machu-picchu',
    'san-francisco': 'san-francisco',
    'las-vegas': 'las-vegas',
    'los-angeles': 'los-angeles',
    'key-west': 'key-west',
    'san-diego': 'san-diego',
    'nouvelle-zelande': 'new-zealand',
    'gold-coast': 'gold-coast',
    'ile-maurice': 'mauritius',
    'nosybe': 'nosy-be',
    'koh-phi-phi': 'ko-phi-phi',
    'koh-tao': 'ko-tao',
    'koh-lanta': 'ko-lanta',
    'gili': 'gili-islands',
    'nusa-penida': 'nusa-penida',
    'da-nang': 'da-nang',
    'baie-halong': 'halong',
    'da-lat': 'da-lat',
    'sapa': 'sapa',
    'nha-trang': 'nha-trang',
    'phu-quoc': 'phu-quoc',
    'phnom-penh': 'phnom-penh',
    'luang-prabang': 'luang-prabang',
    'el-nido': 'el-nido',
    'palma-de-majorque': 'palma-de-mallorca',
    'tbilissi': 'tbilisi',
    'bichkek': 'bishkek',
    'samarcande': 'samarkand',
    'djeddah': 'jeddah',
    'riyad': 'riyadh',
    'koweït': 'kuwait-city',
    'beyrouth': 'beirut',
    'dar-es-salaam': 'dar-es-salaam',
    'addis-abeba': 'addis-ababa',
    'victoria-falls': 'victoria-falls',
    'stone-town': 'stone-town',
    'salvador-de-bahia': 'salvador',
    'sao-paulo': 'sao-paulo',
    'florianopolis': 'florianopolis',
    'san-jose': 'san-jose',
    'antigua-guatemala': 'antigua-guatemala',
    'san-juan': 'san-juan',
    'isla-holbox': 'holbox',
    'valparaiso': 'valparaiso',
    'wild-atlantic-way': 'wild-atlantic-way',
    'trinite-et-tobago': 'trinidad',
    'turks-et-caicos': 'providenciales',
    'porto-rico': 'san-juan',
    'saint-barthelemy': 'saint-barthelemy',
    'saint-martin': 'saint-martin',
    'saint-lucie': 'saint-lucia',
    'saint-pierre-et-miquelon': 'saint-pierre',
    'teheran': 'tehran',
    'ispahan': 'isfahan',
    'xian': 'xian',
    'guilin': 'guilin',
    'muscat': 'muscat',
    'manille': 'manila',
    'yangon': 'yangon',
    'genes': 'genoa',
    'catane': 'catania',
    'bologne': 'bologna',
    'verone': 'verona',
    'lecce': 'lecce',
    'bari': 'bari',
    'patagonie': 'patagonia',
    'galapagos': 'galapagos',
    'polynesie': 'french-polynesia',
    'bora-bora': 'bora-bora',
    'tahiti': 'tahiti',
    'nouvelle-caledonie': 'new-caledonia',
    'noumea': 'noumea',
    'rarotonga': 'rarotonga',
    'rodrigues': 'rodrigues',
    'mayotte': 'mamoudzou',
    'guyane': 'cayenne',
    'pondicherry': 'puducherry',
    'varanasi': 'varanasi',
    'udaipur': 'udaipur',
    'jaipur': 'jaipur',
    'agra': 'agra',
    'mumbai': 'mumbai',
    'delhi': 'new-delhi',
    'colombo': 'colombo',
    'kandy': 'kandy',
    'mandalay': 'mandalay',
    'iguazu': 'puerto-iguazu',
}


def get_booking_slug(dest):
    """Get the booking.com city URL slug for a destination."""
    slug = dest['slug_fr']
    if slug in SLUG_OVERRIDES:
        return SLUG_OVERRIDES[slug]
    # Default: use English name, lowercased, with dashes
    name = dest.get('nom_en', dest.get('nom_bare', slug))
    return name.lower().replace(' ', '-').replace("'", '').replace('/', '-')


def fetch_dest_id(url):
    """Fetch a Booking.com city page and extract dest_id from links."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept': 'text/html,application/xhtml+xml',
    }
    try:
        req = Request(url, headers=headers)
        resp = urlopen(req, timeout=15)
        html = resp.read().decode('utf-8', errors='ignore')
        
        # Extract city= parameter from internal links
        matches = re.findall(r'[&?]city=(-?\d+)', html)
        if matches:
            from collections import Counter
            most_common = Counter(matches).most_common(1)[0][0]
            return most_common
        
        # Fallback: try dest_id= parameter
        matches = re.findall(r'dest_id=(-?\d+)', html)
        if matches:
            from collections import Counter
            return Counter(matches).most_common(1)[0][0]
            
    except Exception as e:
        return None
    return None


def main():
    # Load destinations
    with open(CSV_PATH, encoding='utf-8-sig') as f:
        dests = list(csv.DictReader(f))
    
    missing = [d for d in dests if not d.get('booking_dest_id', '').strip()]
    print(f"📊 {len(missing)} destinations without booking_dest_id")
    
    results = []
    errors = []
    
    for i, d in enumerate(missing):
        slug = d['slug_fr']
        country = d.get('country_en', '')
        cc = COUNTRY_CODES.get(country, '')
        
        if not cc:
            errors.append((slug, f"Unknown country code for '{country}'"))
            print(f"  ⚠️  [{i+1}/{len(missing)}] {slug} — unknown country '{country}'")
            continue
        
        bk_slug = get_booking_slug(d)
        url = f"https://www.booking.com/city/{cc}/{bk_slug}.html"
        
        print(f"  [{i+1}/{len(missing)}] {slug:25s} → {url}", end='', flush=True)
        
        dest_id = fetch_dest_id(url)
        
        if dest_id:
            results.append({'slug_fr': slug, 'booking_dest_id': dest_id, 'dest_type': 'city', 'url': url})
            print(f" ✅ {dest_id}")
        else:
            # Try alternative slug: just the city name
            alt_slug = d.get('nom_en', '').lower().replace(' ', '-')
            if alt_slug != bk_slug:
                alt_url = f"https://www.booking.com/city/{cc}/{alt_slug}.html"
                print(f" ❌ trying {alt_slug}...", end='', flush=True)
                dest_id = fetch_dest_id(alt_url)
                if dest_id:
                    results.append({'slug_fr': slug, 'booking_dest_id': dest_id, 'dest_type': 'city', 'url': alt_url})
                    print(f" ✅ {dest_id}")
                else:
                    errors.append((slug, f"Not found at {url}"))
                    print(f" ❌")
            else:
                errors.append((slug, f"Not found at {url}"))
                print(f" ❌")
        
        time.sleep(0.8)  # Rate limit
    
    # Write results
    with open(OUTPUT, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['slug_fr', 'booking_dest_id', 'dest_type', 'url'])
        writer.writeheader()
        writer.writerows(results)
    
    print(f"\n{'='*60}")
    print(f"✅ Found: {len(results)}/{len(missing)}")
    print(f"❌ Errors: {len(errors)}")
    print(f"📄 Output: {OUTPUT}")
    
    if errors:
        print(f"\nNot found ({len(errors)}):")
        for slug, reason in errors:
            print(f"  {slug}: {reason}")
    
    print(f"\nNext step:")
    print(f"  python3 scripts/merge_booking_ids.py {OUTPUT}")


if __name__ == '__main__':
    main()
