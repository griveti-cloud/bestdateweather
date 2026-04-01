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

// ── Travel advisories cache (in-memory, per worker instance) ──
let _advisoryCache = null;
let _advisoryCacheAt = 0;
const ADVISORY_TTL = 6 * 3600 * 1000; // 6h

// Map ISO2 → risk level 1-4 from Auswärtiges Amt
function parseAdvisories(data) {
  const resp = data.response || {};
  const result = { _updated: new Date().toISOString().slice(0,10), _source: 'Auswärtiges Amt (DE)' };
  for (const k of Object.keys(resp)) {
    if (k === 'lastModified') continue;
    const v = resp[k];
    if (!v || typeof v !== 'object' || !v.countryCode) continue;
    const w = v.warning, pw = v.partialWarning, sw = v.situationWarning, spw = v.situationPartWarning;
    result[v.countryCode] = w ? 4 : sw ? 3 : (pw || spw) ? 2 : 1;
  }
  return result;
}

async function handleAdvisories(request) {
  const headers = {
    'Access-Control-Allow-Origin': '*',
    'Content-Type': 'application/json',
    'Cache-Control': 'public, max-age=21600',
  };
  const now = Date.now();
  if (_advisoryCache && (now - _advisoryCacheAt) < ADVISORY_TTL) {
    return new Response(JSON.stringify(_advisoryCache), { headers });
  }
  try {
    const r = await fetch('https://www.auswaertiges-amt.de/opendata/travelwarning', {
      headers: { 'User-Agent': 'BestDateWeather/1.0' },
      cf: { cacheTtl: 21600, cacheEverything: true },
    });
    if (!r.ok) throw new Error('upstream ' + r.status);
    const data = await r.json();
    _advisoryCache = parseAdvisories(data);
    _advisoryCacheAt = now;
    return new Response(JSON.stringify(_advisoryCache), { headers });
  } catch(e) {
    // Return stale cache if available, otherwise error
    if (_advisoryCache) return new Response(JSON.stringify(_advisoryCache), { headers });
    return new Response(JSON.stringify({ error: e.message }), { status: 502, headers });
  }
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const path = url.pathname;

    // ── Servir notre robots.txt (override CF managed) ──
    if (path === '/robots.txt') {
      const body = `User-agent: *
Allow: /
Disallow: /en/app.html?
Disallow: /es/app.html?
Disallow: /us/app.html?
Disallow: /de/app.html?
Disallow: /app.html?
Disallow: /index.html?
Disallow: /data/
Disallow: /widget/

Sitemap: https://bestdateweather.com/sitemap-index.xml`;
      return new Response(body, { headers: { 'Content-Type': 'text/plain', 'Cache-Control': 'public, max-age=86400' } });
    }

    // ── Travel advisories endpoint ──
    if (path === '/api/advisories') return handleAdvisories(request);

    // ── Subscribe endpoint ──
    if (path === '/subscribe') return handleSubscribe(request, env);

    // ── Regex redirects ──
    const mFR = path.match(PATTERN_FR);
    if (mFR) return Response.redirect(`${url.origin}/${mFR[1]}-meteo-${mFR[2]}.html`, 301);

    const mEN = path.match(PATTERN_EN);
    if (mEN) return Response.redirect(`${url.origin}/en/${mEN[1]}-weather-${mEN[2]}.html`, 301);

    // ── Proxy /data/suggestions.json depuis GitHub (hors limite 20k assets CF) ──
    if (path === '/data/suggestions.json') {
      const r = await fetch('https://raw.githubusercontent.com/griveti-cloud/bestdateweather/main/data/suggestions.json', {
        cf: { cacheTtl: 86400, cacheEverything: true }
      });
      if (!r.ok) return new Response('{}', { status: 200, headers: { 'Content-Type': 'application/json', 'Cache-Control': 'public, max-age=86400' } });
      const body = await r.text();
      return new Response(body, { status: 200, headers: { 'Content-Type': 'application/json', 'Cache-Control': 'public, max-age=86400', 'Access-Control-Allow-Origin': '*' } });
    }

    // ── Static assets ──
    return env.ASSETS.fetch(request);
  }
};
