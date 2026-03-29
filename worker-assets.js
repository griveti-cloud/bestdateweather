const FR_MONTHS = 'janvier|fevrier|mars|avril|mai|juin|juillet|aout|septembre|octobre|novembre|decembre';
const EN_MONTHS = 'january|february|march|april|may|june|july|august|september|october|november|december';
const PATTERN_FR = new RegExp(`^/meilleure-periode-(.+)-en-(${FR_MONTHS})\\.html$`);
const PATTERN_EN = new RegExp(`^/en/best-time-to-visit-(.+)-in-(${EN_MONTHS})\\.html$`);

async function handleSubscribe(request, env) {
  const headers = {
    'Access-Control-Allow-Origin': 'https://bestdateweather.com',
    'Content-Type': 'application/json'
  };
  if (request.method === 'OPTIONS') {
    return new Response(null, { status: 200, headers: {
      'Access-Control-Allow-Origin': 'https://bestdateweather.com',
      'Access-Control-Allow-Methods': 'POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type'
    }});
  }
  if (request.method !== 'POST') return new Response('Method Not Allowed', { status: 405 });
  let email, source;
  try {
    const body = await request.json();
    email = body.email; source = body.source || 'favori';
  } catch(e) {
    return new Response(JSON.stringify({ error: 'Invalid JSON' }), { status: 400, headers });
  }
  if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    return new Response(JSON.stringify({ error: 'Email invalide' }), { status: 400, headers });
  }
  const BREVO_API_KEY = env.BREVO_API_KEY;
  if (!BREVO_API_KEY) {
    return new Response(JSON.stringify({ error: 'Config manquante' }), { status: 500, headers });
  }
  try {
    const resp = await fetch('https://api.brevo.com/v3/contacts', {
      method: 'POST',
      headers: { 'api-key': BREVO_API_KEY, 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, attributes: { SOURCE: source }, listIds: [2], updateEnabled: false })
    });
    const data = await resp.json();
    if (resp.ok) return new Response(JSON.stringify({ success: true }), { status: 200, headers });
    if (data.code === 'duplicate_parameter') return new Response(JSON.stringify({ success: true, existing: true }), { status: 200, headers });
    return new Response(JSON.stringify({ error: 'Brevo error' }), { status: 502, headers });
  } catch(e) {
    return new Response(JSON.stringify({ error: 'Network error' }), { status: 500, headers });
  }
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const path = url.pathname;

    // ── Subscribe endpoint ──
    if (path === '/subscribe') return handleSubscribe(request, env);

    // ── Regex redirects ──
    const mFR = path.match(PATTERN_FR);
    if (mFR) return Response.redirect(`${url.origin}/${mFR[1]}-meteo-${mFR[2]}.html`, 301);

    const mEN = path.match(PATTERN_EN);
    if (mEN) return Response.redirect(`${url.origin}/en/${mEN[1]}-weather-${mEN[2]}.html`, 301);

    // ── Static assets ──
    return env.ASSETS.fetch(request);
  }
};
