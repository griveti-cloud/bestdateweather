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
  const DESTINATIONS = PLACEHOLDER_DESTINATIONS;

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
