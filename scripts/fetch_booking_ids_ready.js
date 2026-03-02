/**
 * fetch_booking_ids.js
 * ====================
 * Script à coller dans la console navigateur sur https://www.booking.com
 *
 * USAGE:
 * 1. Ouvrir https://www.booking.com dans Chrome/Firefox
 * 2. Ouvrir la console (F12 → Console)
 * 3. Coller ce script et appuyer Entrée
 * 4. Attendre ~5-10 min (351 destinations, 1 requête/sec)
 * 5. Le résultat CSV est copié dans le presse-papier et affiché
 *
 * Le script utilise l'endpoint autocomplete interne de Booking.com
 * qui nécessite d'être sur le domaine booking.com (cookies de session).
 */

(async function fetchBookingIds() {
  const DESTINATIONS = [{"s": "bordeaux", "q": "Bordeaux, France"}, {"s": "bretagne", "q": "Brittany, France"}, {"s": "corse", "q": "Corsica, France"}, {"s": "costa-rica", "q": "Costa Rica, Costa Rica"}, {"s": "fuerteventura", "q": "Fuerteventura, Spain"}, {"s": "goa", "q": "Goa, India"}, {"s": "hawaii", "q": "Hawaii / Maui, United States"}, {"s": "jamaique", "q": "Jamaica, Jamaica"}, {"s": "le-cap", "q": "Cape Town, South Africa"}, {"s": "los-angeles", "q": "Los Angeles, United States"}, {"s": "lyon", "q": "Lyon, France"}, {"s": "marseille", "q": "Marseille, France"}, {"s": "miami", "q": "Miami, United States"}, {"s": "minorque", "q": "Menorca, Spain"}, {"s": "nice", "q": "Nice, France"}, {"s": "paris", "q": "Paris, France"}, {"s": "provence", "q": "Provence, France"}, {"s": "seville", "q": "Seville, Spain"}, {"s": "tulum", "q": "Tulum, Mexico"}, {"s": "zakynthos", "q": "Zakynthos, Greece"}, {"s": "barbade", "q": "Barbados, Barbados"}, {"s": "athenes", "q": "Athens, Greece"}, {"s": "milan", "q": "Milan, Italy"}, {"s": "naples", "q": "Naples, Italy"}, {"s": "lac-come", "q": "Lake Como, Italy"}, {"s": "cinque-terre", "q": "Cinque Terre, Italy"}, {"s": "madrid", "q": "Madrid, Spain"}, {"s": "grenade", "q": "Granada, Spain"}, {"s": "acores", "q": "Azores, Portugal"}, {"s": "antalya", "q": "Antalya, Turkey"}, {"s": "cappadoce", "q": "Cappadocia, Turkey"}, {"s": "copenhague", "q": "Copenhagen, Denmark"}, {"s": "budapest", "q": "Budapest, Hungary"}, {"s": "cracovie", "q": "Krakow, Poland"}, {"s": "montenegro", "q": "Montenegro, Montenegro"}, {"s": "chypre", "q": "Cyprus, Cyprus"}, {"s": "fes", "q": "Fes, Morocco"}, {"s": "djerba", "q": "Djerba, Tunisia"}, {"s": "le-caire", "q": "Cairo, Egypt"}, {"s": "hurghada", "q": "Hurghada, Egypt"}, {"s": "jordanie", "q": "Jordan, Jordan"}, {"s": "kenya", "q": "Kenya, Kenya"}, {"s": "madagascar", "q": "Madagascar, Madagascar"}, {"s": "chiang-mai", "q": "Chiang Mai, Thailand"}, {"s": "koh-samui", "q": "Koh Samui, Thailand"}, {"s": "hanoi", "q": "Hanoi, Vietnam"}, {"s": "ho-chi-minh", "q": "Ho Chi Minh City, Vietnam"}, {"s": "kyoto", "q": "Kyoto, Japan"}, {"s": "hong-kong", "q": "Hong Kong, China"}, {"s": "seoul", "q": "Seoul, South Korea"}, {"s": "philippines", "q": "Philippines, Philippines"}, {"s": "kuala-lumpur", "q": "Kuala Lumpur, Malaysia"}, {"s": "rajasthan", "q": "Rajasthan, India"}, {"s": "sri-lanka", "q": "Sri Lanka, Sri Lanka"}, {"s": "san-francisco", "q": "San Francisco, USA"}, {"s": "las-vegas", "q": "Las Vegas, USA"}, {"s": "guadeloupe", "q": "Guadeloupe, Guadeloupe"}, {"s": "martinique", "q": "Martinique, Martinique"}, {"s": "republique-dominicaine", "q": "Dominican Republic, Dominican Republic"}, {"s": "punta-cana", "q": "Punta Cana, Dominican Republic"}, {"s": "perou", "q": "Peru, Peru"}, {"s": "machu-picchu", "q": "Machu Picchu, Peru"}, {"s": "colombie", "q": "Colombia, Colombia"}, {"s": "sydney", "q": "Sydney, Australia"}, {"s": "nouvelle-zelande", "q": "New Zealand, New Zealand"}, {"s": "polynesie", "q": "French Polynesia, French Polynesia"}, {"s": "bora-bora", "q": "Bora Bora, French Polynesia"}, {"s": "dublin", "q": "Dublin, Ireland"}, {"s": "thessalonique", "q": "Thessaloniki, Greece"}, {"s": "naxos", "q": "Naxos, Greece"}, {"s": "paros", "q": "Paros, Greece"}, {"s": "kefalonia", "q": "Kefalonia, Greece"}, {"s": "pouilles", "q": "Puglia, Italy"}, {"s": "lac-garde", "q": "Lake Garda, Italy"}, {"s": "palerme", "q": "Palermo, Italy"}, {"s": "dolomites", "q": "Dolomites, Italy"}, {"s": "cadix", "q": "Cadiz, Spain"}, {"s": "saint-sebastien", "q": "San Sebastián, Spain"}, {"s": "formentera", "q": "Formentera, Spain"}, {"s": "costa-brava", "q": "Costa Brava, Spain"}, {"s": "cordoue", "q": "Córdoba, Spain"}, {"s": "faro", "q": "Faro, Portugal"}, {"s": "normandie", "q": "Normandy, France"}, {"s": "pays-basque", "q": "French Basque Country, France"}, {"s": "biarritz", "q": "Biarritz, France"}, {"s": "zadar", "q": "Zadar, Croatia"}, {"s": "hvar", "q": "Hvar, Croatia"}, {"s": "bodrum", "q": "Bodrum, Turkey"}, {"s": "munich", "q": "Munich, Germany"}, {"s": "stockholm", "q": "Stockholm, Sweden"}, {"s": "oslo", "q": "Oslo, Norway"}, {"s": "lofoten", "q": "Lofoten Islands, Norway"}, {"s": "laponie", "q": "Lapland, Finland"}, {"s": "kotor", "q": "Kotor, Montenegro"}, {"s": "albanie", "q": "Albania, Albania"}, {"s": "bruxelles", "q": "Brussels, Belgium"}, {"s": "essaouira", "q": "Essaouira, Morocco"}, {"s": "tunis", "q": "Tunis, Tunisia"}, {"s": "sharm-el-sheikh", "q": "Sharm el-Sheikh, Egypt"}, {"s": "louxor", "q": "Luxor, Egypt"}, {"s": "oman", "q": "Oman, Oman"}, {"s": "abu-dhabi", "q": "Abu Dhabi, UAE"}, {"s": "tel-aviv", "q": "Tel Aviv, Israel"}, {"s": "senegal", "q": "Senegal, Senegal"}, {"s": "cap-vert", "q": "Cape Verde, Cape Verde"}, {"s": "namibie", "q": "Namibia, Namibia"}, {"s": "tanzanie", "q": "Tanzania, Tanzania"}, {"s": "krabi", "q": "Krabi, Thailand"}, {"s": "koh-lanta", "q": "Koh Lanta, Thailand"}, {"s": "baie-halong", "q": "Halong Bay, Vietnam"}, {"s": "da-nang", "q": "Da Nang, Vietnam"}, {"s": "phu-quoc", "q": "Phu Quoc, Vietnam"}, {"s": "lombok", "q": "Lombok, Indonesia"}, {"s": "java", "q": "Java, Indonesia"}, {"s": "ubud", "q": "Ubud, Indonesia"}, {"s": "osaka", "q": "Osaka, Japan"}, {"s": "pekin", "q": "Beijing, China"}, {"s": "shanghai", "q": "Shanghai, China"}, {"s": "palawan", "q": "Palawan, Philippines"}, {"s": "laos", "q": "Laos, Laos"}, {"s": "kerala", "q": "Kerala, India"}, {"s": "delhi", "q": "Delhi, India"}, {"s": "georgie", "q": "Georgia, Georgia"}, {"s": "chicago", "q": "Chicago, USA"}, {"s": "washington", "q": "Washington DC, USA"}, {"s": "orlando", "q": "Orlando, USA"}, {"s": "nouvelle-orleans", "q": "New Orleans, USA"}, {"s": "montreal", "q": "Montreal, Canada"}, {"s": "vancouver", "q": "Vancouver, Canada"}, {"s": "bahamas", "q": "Bahamas, Bahamas"}, {"s": "saint-lucie", "q": "Saint Lucia, Saint Lucia"}, {"s": "saint-martin", "q": "Saint Martin, Saint Martin"}, {"s": "mexico", "q": "Mexico City, Mexico"}, {"s": "playa-del-carmen", "q": "Playa del Carmen, Mexico"}, {"s": "puerto-vallarta", "q": "Puerto Vallarta, Mexico"}, {"s": "cabo-san-lucas", "q": "Cabo San Lucas, Mexico"}, {"s": "panama", "q": "Panama, Panama"}, {"s": "medellin", "q": "Medellín, Colombia"}, {"s": "chili", "q": "Chile, Chile"}, {"s": "patagonie", "q": "Patagonia, Argentina"}, {"s": "galapagos", "q": "Galápagos, Ecuador"}, {"s": "melbourne", "q": "Melbourne, Australia"}, {"s": "fidji", "q": "Fiji, Fiji"}, {"s": "nouvelle-caledonie", "q": "New Caledonia, New Caledonia"}, {"s": "mayotte", "q": "Mayotte, Mayotte"}, {"s": "taipei", "q": "Taipei, Taiwan"}, {"s": "saint-barthelemy", "q": "Saint Barthélemy, Saint Barthélemy"}, {"s": "el-nido", "q": "El Nido, Philippines"}, {"s": "cambodge", "q": "Cambodia, Cambodia"}, {"s": "nepal", "q": "Nepal, Nepal"}, {"s": "lefkada", "q": "Lefkada, Greece"}, {"s": "kos", "q": "Kos, Greece"}, {"s": "milos", "q": "Milos, Greece"}, {"s": "hydra", "q": "Hydra, Greece"}, {"s": "turin", "q": "Turin, Italy"}, {"s": "bologne", "q": "Bologna, Italy"}, {"s": "verone", "q": "Verona, Italy"}, {"s": "bilbao", "q": "Bilbao, Spain"}, {"s": "la-palma", "q": "La Palma, Spain"}, {"s": "la-gomera", "q": "La Gomera, Spain"}, {"s": "sintra", "q": "Sintra, Portugal"}, {"s": "dordogne", "q": "Dordogne, France"}, {"s": "strasbourg", "q": "Strasbourg, France"}, {"s": "chamonix", "q": "Chamonix, France"}, {"s": "montpellier", "q": "Montpellier, France"}, {"s": "plitvice", "q": "Plitvice, Croatia"}, {"s": "zagreb", "q": "Zagreb, Croatia"}, {"s": "izmir", "q": "Izmir, Turkey"}, {"s": "fethiye", "q": "Fethiye, Turkey"}, {"s": "hambourg", "q": "Hamburg, Germany"}, {"s": "francfort", "q": "Frankfurt, Germany"}, {"s": "helsinki", "q": "Helsinki, Finland"}, {"s": "tromso", "q": "Tromsø, Norway"}, {"s": "bergen", "q": "Bergen, Norway"}, {"s": "varsovie", "q": "Warsaw, Poland"}, {"s": "bucarest", "q": "Bucharest, Romania"}, {"s": "sofia", "q": "Sofia, Bulgaria"}, {"s": "tallinn", "q": "Tallinn, Estonia"}, {"s": "riga", "q": "Riga, Latvia"}, {"s": "vilnius", "q": "Vilnius, Lithuania"}, {"s": "bratislava", "q": "Bratislava, Slovakia"}, {"s": "ljubljana", "q": "Ljubljana, Slovenia"}, {"s": "paphos", "q": "Paphos, Cyprus"}, {"s": "zurich", "q": "Zurich, Switzerland"}, {"s": "geneve", "q": "Geneva, Switzerland"}, {"s": "bruges", "q": "Bruges, Belgium"}, {"s": "gozo", "q": "Gozo, Malta"}, {"s": "chefchaouen", "q": "Chefchaouen, Morocco"}, {"s": "ouarzazate", "q": "Ouarzazate, Morocco"}, {"s": "hammamet", "q": "Hammamet, Tunisia"}, {"s": "marsa-alam", "q": "Marsa Alam, Egypt"}, {"s": "doha", "q": "Doha, Qatar"}, {"s": "koh-phi-phi", "q": "Koh Phi Phi, Thailand"}, {"s": "koh-tao", "q": "Koh Tao, Thailand"}, {"s": "pattaya", "q": "Pattaya, Thailand"}, {"s": "gili", "q": "Gili Islands, Indonesia"}, {"s": "nusa-penida", "q": "Nusa Penida, Indonesia"}, {"s": "komodo", "q": "Komodo, Indonesia"}, {"s": "okinawa", "q": "Okinawa, Japan"}, {"s": "hiroshima", "q": "Hiroshima, Japan"}, {"s": "busan", "q": "Busan, South Korea"}, {"s": "jeju", "q": "Jeju, South Korea"}, {"s": "cebu", "q": "Cebu, Philippines"}, {"s": "boracay", "q": "Boracay, Philippines"}, {"s": "langkawi", "q": "Langkawi, Malaysia"}, {"s": "penang", "q": "Penang, Malaysia"}, {"s": "myanmar", "q": "Myanmar, Myanmar"}, {"s": "luang-prabang", "q": "Luang Prabang, Laos"}, {"s": "ouzbekistan", "q": "Uzbekistan, Uzbekistan"}, {"s": "boston", "q": "Boston, USA"}, {"s": "seattle", "q": "Seattle, USA"}, {"s": "key-west", "q": "Key West, USA"}, {"s": "yellowstone", "q": "Yellowstone, USA"}, {"s": "toronto", "q": "Toronto, Canada"}, {"s": "quebec-ville", "q": "Quebec City, Canada"}, {"s": "curacao", "q": "Curaçao, Curaçao"}, {"s": "aruba", "q": "Aruba, Aruba"}, {"s": "porto-rico", "q": "Puerto Rico, Puerto Rico"}, {"s": "trinite-et-tobago", "q": "Trinidad and Tobago, Trinidad and Tobago"}, {"s": "antigua", "q": "Antigua, Antigua and Barbuda"}, {"s": "oaxaca", "q": "Oaxaca, Mexico"}, {"s": "guatemala", "q": "Guatemala, Guatemala"}, {"s": "belize", "q": "Belize, Belize"}, {"s": "nicaragua", "q": "Nicaragua, Nicaragua"}, {"s": "santiago", "q": "Santiago, Chile"}, {"s": "equateur", "q": "Ecuador, Ecuador"}, {"s": "bolivie", "q": "Bolivia, Bolivia"}, {"s": "uruguay", "q": "Uruguay, Uruguay"}, {"s": "gold-coast", "q": "Gold Coast, Australia"}, {"s": "cairns", "q": "Cairns, Australia"}, {"s": "perth", "q": "Perth, Australia"}, {"s": "rodrigues", "q": "Rodrigues, Mauritius"}, {"s": "nosybe", "q": "Nosy Be, Madagascar"}, {"s": "wild-atlantic-way", "q": "Wild Atlantic Way, Ireland"}, {"s": "gdansk", "q": "Gdańsk, Poland"}, {"s": "transylvanie", "q": "Transylvania, Romania"}, {"s": "da-lat", "q": "Da Lat, Vietnam"}, {"s": "tbilissi", "q": "Tbilisi, Georgia"}, {"s": "canggu", "q": "Canggu, Indonesia"}, {"s": "el-hierro", "q": "El Hierro, Spain"}, {"s": "guyane", "q": "French Guiana, French Guiana"}, {"s": "saint-pierre-et-miquelon", "q": "Saint-Pierre and Miquelon, Saint-Pierre and Miquelon"}, {"s": "diani", "q": "Diani Beach, Kenya"}, {"s": "dakar", "q": "Dakar, Senegal"}, {"s": "sapa", "q": "Sa Pa, Vietnam"}, {"s": "nha-trang", "q": "Nha Trang, Vietnam"}, {"s": "siargao", "q": "Siargao, Philippines"}, {"s": "borneo", "q": "Borneo, Malaysia"}, {"s": "macao", "q": "Macau, China"}, {"s": "phnom-penh", "q": "Phnom Penh, Cambodia"}, {"s": "bermudes", "q": "Bermuda, Bermuda"}, {"s": "bogota", "q": "Bogota, Colombia"}, {"s": "isla-holbox", "q": "Isla Holbox, Mexico"}, {"s": "valparaiso", "q": "Valparaíso, Chile"}, {"s": "annecy", "q": "Annecy, France"}, {"s": "toulouse", "q": "Toulouse, France"}, {"s": "alsace", "q": "Alsace, France"}, {"s": "palma-de-majorque", "q": "Palma de Mallorca, Spain"}, {"s": "bari", "q": "Bari, Italy"}, {"s": "lecce", "q": "Lecce, Italy"}, {"s": "genes", "q": "Genoa, Italy"}, {"s": "catane", "q": "Catania, Italy"}, {"s": "sarajevo", "q": "Sarajevo, Bosnia and Herzegovina"}, {"s": "belgrade", "q": "Belgrade, Serbia"}, {"s": "skopje", "q": "Skopje, North Macedonia"}, {"s": "tirana", "q": "Tirana, Albania"}, {"s": "riyad", "q": "Riyadh, Saudi Arabia"}, {"s": "djeddah", "q": "Jeddah, Saudi Arabia"}, {"s": "bahrein", "q": "Bahrain, Bahrain"}, {"s": "koweït", "q": "Kuwait City, Kuwait"}, {"s": "beyrouth", "q": "Beirut, Lebanon"}, {"s": "muscat", "q": "Muscat, Oman"}, {"s": "casablanca", "q": "Casablanca, Morocco"}, {"s": "nairobi", "q": "Nairobi, Kenya"}, {"s": "mombasa", "q": "Mombasa, Kenya"}, {"s": "johannesburg", "q": "Johannesburg, South Africa"}, {"s": "durban", "q": "Durban, South Africa"}, {"s": "accra", "q": "Accra, Ghana"}, {"s": "abidjan", "q": "Abidjan, Ivory Coast"}, {"s": "kigali", "q": "Kigali, Rwanda"}, {"s": "addis-abeba", "q": "Addis Ababa, Ethiopia"}, {"s": "stone-town", "q": "Stone Town, Tanzania"}, {"s": "victoria-falls", "q": "Victoria Falls, Zimbabwe"}, {"s": "kampala", "q": "Kampala, Uganda"}, {"s": "lagos", "q": "Lagos, Nigeria"}, {"s": "dar-es-salaam", "q": "Dar es Salaam, Tanzania"}, {"s": "mumbai", "q": "Mumbai, India"}, {"s": "jaipur", "q": "Jaipur, India"}, {"s": "varanasi", "q": "Varanasi, India"}, {"s": "udaipur", "q": "Udaipur, India"}, {"s": "colombo", "q": "Colombo, Sri Lanka"}, {"s": "kandy", "q": "Kandy, Sri Lanka"}, {"s": "yangon", "q": "Yangon, Myanmar"}, {"s": "mandalay", "q": "Mandalay, Myanmar"}, {"s": "manille", "q": "Manila, Philippines"}, {"s": "xian", "q": "Xi'an, China"}, {"s": "chengdu", "q": "Chengdu, China"}, {"s": "guilin", "q": "Guilin, China"}, {"s": "sapporo", "q": "Sapporo, Japan"}, {"s": "samarcande", "q": "Samarkand, Uzbekistan"}, {"s": "almaty", "q": "Almaty, Kazakhstan"}, {"s": "sao-paulo", "q": "São Paulo, Brazil"}, {"s": "salvador-de-bahia", "q": "Salvador, Brazil"}, {"s": "cusco", "q": "Cusco, Peru"}, {"s": "lima", "q": "Lima, Peru"}, {"s": "cartagena", "q": "Cartagena, Colombia"}, {"s": "montevideo", "q": "Montevideo, Uruguay"}, {"s": "quito", "q": "Quito, Ecuador"}, {"s": "la-paz", "q": "La Paz, Bolivia"}, {"s": "asuncion", "q": "Asunción, Paraguay"}, {"s": "bariloche", "q": "Bariloche, Argentina"}, {"s": "san-jose", "q": "San José, Costa Rica"}, {"s": "antigua-guatemala", "q": "Antigua Guatemala, Guatemala"}, {"s": "san-juan", "q": "San Juan, Puerto Rico"}, {"s": "nassau", "q": "Nassau, Bahamas"}, {"s": "turks-et-caicos", "q": "Turks and Caicos, Turks and Caicos"}, {"s": "denver", "q": "Denver, United States"}, {"s": "nashville", "q": "Nashville, United States"}, {"s": "savannah", "q": "Savannah, United States"}, {"s": "auckland", "q": "Auckland, New Zealand"}, {"s": "queenstown", "q": "Queenstown, New Zealand"}, {"s": "rotorua", "q": "Rotorua, New Zealand"}, {"s": "darwin", "q": "Darwin, Australia"}, {"s": "hobart", "q": "Hobart, Australia"}, {"s": "adelaide", "q": "Adelaide, Australia"}, {"s": "samoa", "q": "Samoa, Samoa"}, {"s": "vanuatu", "q": "Vanuatu, Vanuatu"}, {"s": "tonga", "q": "Tonga, Tonga"}, {"s": "teheran", "q": "Tehran, Iran"}, {"s": "ispahan", "q": "Isfahan, Iran"}, {"s": "hue", "q": "Hue, Vietnam"}, {"s": "ronda", "q": "Ronda, Spain"}, {"s": "maputo", "q": "Maputo, Mozambique"}, {"s": "windhoek", "q": "Windhoek, Namibia"}, {"s": "charleston", "q": "Charleston, United States"}, {"s": "bichkek", "q": "Bishkek, Kyrgyzstan"}, {"s": "agra", "q": "Agra, India"}, {"s": "pondicherry", "q": "Pondicherry, India"}, {"s": "honolulu", "q": "Honolulu, United States"}, {"s": "austin", "q": "Austin, United States"}, {"s": "san-diego", "q": "San Diego, United States"}, {"s": "portland", "q": "Portland, United States"}, {"s": "florianopolis", "q": "Florianópolis, Brazil"}, {"s": "rarotonga", "q": "Rarotonga, Cook Islands"}, {"s": "phoenix", "q": "Phoenix, United States"}, {"s": "iguazu", "q": "Iguazú, Argentina"}, {"s": "noumea", "q": "Nouméa, New Caledonia"}, {"s": "tahiti", "q": "Tahiti, French Polynesia"}, {"s": "petra", "q": "Petra, Jordan"}, {"s": "monteverde", "q": "Monteverde, Costa Rica"}, {"s": "trieste", "q": "Trieste, Italy"}];

  const DELAY_MS = 1200; // 1.2s entre chaque requête pour éviter le rate-limit
  const results = [];
  const errors = [];

  console.log(`🔍 Démarrage: ${DESTINATIONS.length} destinations à résoudre...`);

  for (let i = 0; i < DESTINATIONS.length; i++) {
    const dest = DESTINATIONS[i];
    const query = dest.q;

    try {
      // Endpoint autocomplete utilisé par le frontend Booking.com
      const resp = await fetch(
        `/autocomplete?lang=en-us&sb=1&src=index&src_elem=sb&ss=${encodeURIComponent(query)}&selected_currency=EUR`,
        {
          headers: {
            'Accept': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
          },
          credentials: 'same-origin',
        }
      );

      if (!resp.ok) {
        // Fallback: try the accommodations endpoint
        const resp2 = await fetch(
          `https://accommodations.booking.com/autocomplete.json?lang=en-us&text=${encodeURIComponent(query)}`,
          { credentials: 'include' }
        );
        if (resp2.ok) {
          const data2 = await resp2.json();
          if (data2.results && data2.results.length > 0) {
            const r = data2.results[0];
            results.push({ slug: dest.s, dest_id: r.dest_id, dest_type: r.dest_type, label: r.label });
            console.log(`  ✅ [${i+1}/${DESTINATIONS.length}] ${dest.s} → ${r.dest_id} (${r.dest_type})`);
          } else {
            errors.push({ slug: dest.s, query, reason: 'no results (fallback)' });
            console.warn(`  ⚠️ [${i+1}/${DESTINATIONS.length}] ${dest.s} → aucun résultat`);
          }
        } else {
          errors.push({ slug: dest.s, query, reason: `HTTP ${resp.status} + fallback ${resp2.status}` });
          console.error(`  ❌ [${i+1}/${DESTINATIONS.length}] ${dest.s} → erreurs HTTP`);
        }
      } else {
        // Parse response - could be HTML or JSON depending on endpoint
        const text = await resp.text();
        try {
          const data = JSON.parse(text);
          // Try to extract dest_id from JSON response
          const city = (data.results || data || []).find(r =>
            r.dest_type === 'city' || r.dest_type === 'region'
          ) || (data.results || data || [])[0];

          if (city && city.dest_id) {
            results.push({ slug: dest.s, dest_id: city.dest_id, dest_type: city.dest_type, label: city.label || city.name });
            console.log(`  ✅ [${i+1}/${DESTINATIONS.length}] ${dest.s} → ${city.dest_id} (${city.dest_type})`);
          } else {
            errors.push({ slug: dest.s, query, reason: 'no dest_id in response' });
            console.warn(`  ⚠️ [${i+1}/${DESTINATIONS.length}] ${dest.s} → pas de dest_id`);
          }
        } catch {
          // Try to extract from HTML
          const match = text.match(/dest_id[=:]\s*["']?(-?\d+)/);
          if (match) {
            results.push({ slug: dest.s, dest_id: match[1], dest_type: 'city', label: query });
            console.log(`  ✅ [${i+1}/${DESTINATIONS.length}] ${dest.s} → ${match[1]} (HTML)`);
          } else {
            errors.push({ slug: dest.s, query, reason: 'unparseable response' });
            console.warn(`  ⚠️ [${i+1}/${DESTINATIONS.length}] ${dest.s} → réponse non parsable`);
          }
        }
      }
    } catch (err) {
      errors.push({ slug: dest.s, query, reason: err.message });
      console.error(`  ❌ [${i+1}/${DESTINATIONS.length}] ${dest.s} → ${err.message}`);
    }

    // Rate-limit
    await new Promise(r => setTimeout(r, DELAY_MS));
  }

  // Output CSV
  const csv = 'slug_fr,booking_dest_id,dest_type,label\n' +
    results.map(r => `${r.slug},${r.dest_id},${r.dest_type},"${(r.label||'').replace(/"/g, '""')}"`).join('\n');

  console.log('\n' + '='.repeat(60));
  console.log(`✅ Résultats: ${results.length}/${DESTINATIONS.length} trouvés`);
  console.log(`❌ Erreurs: ${errors.length}`);
  console.log('='.repeat(60));
  console.log('\n📋 CSV (aussi copié dans le presse-papier):');
  console.log(csv);

  if (errors.length > 0) {
    console.log('\n⚠️ Destinations non résolues:');
    errors.forEach(e => console.log(`  ${e.slug}: ${e.reason}`));
  }

  try {
    await navigator.clipboard.writeText(csv);
    console.log('\n✅ CSV copié dans le presse-papier !');
  } catch {
    console.log('\n⚠️ Impossible de copier — sélectionnez le CSV ci-dessus manuellement');
  }

  // Also store in window for easy access
  window.__bookingResults = { results, errors, csv };
  console.log('\nAccès aux données: window.__bookingResults');

  return { results, errors };
})();


// 351 destinations to resolve
