const FR_MONTHS = 'janvier|fevrier|mars|avril|mai|juin|juillet|aout|septembre|octobre|novembre|decembre';
const EN_MONTHS = 'january|february|march|april|may|june|july|august|september|october|november|december';
const PATTERN_FR = new RegExp(`^/meilleure-periode-(.+)-en-(${FR_MONTHS})\\.html$`);
const PATTERN_EN = new RegExp(`^/en/best-time-to-visit-(.+)-in-(${EN_MONTHS})\\.html$`);
// Old annual pages at root → /en/
const PATTERN_ANNUAL_ROOT = /^\/best-time-to-visit-(.+)\.html$/;
// Old monthly pages with English months in FR slugs
const EN_TO_FR_MONTH = {january:'janvier',february:'fevrier',march:'mars',april:'avril',may:'mai',june:'juin',july:'juillet',august:'aout',september:'septembre',october:'octobre',november:'novembre',december:'decembre'};
const PATTERN_FR_EN_MONTH = new RegExp(`^/([a-z0-9-]+)-meteo-(january|february|march|april|may|june|july|august|september|october|november|december)\.html$`);
// Old /us/best-time-to-visit-X-in-MONTH.html (without subdirectory check already handled for en)
const PATTERN_US = new RegExp(`^/us/best-time-to-visit-(.+)-in-(${EN_MONTHS})\\.html$`);

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


    // ── Geo IP endpoint — retourne ville+coords depuis Cloudflare sans permission ──
    if (path === '/api/geo') {
      const cf = request.cf || {};
      const city    = cf.city || '';
      const lat     = cf.latitude  ? parseFloat(cf.latitude)  : null;
      const lon     = cf.longitude ? parseFloat(cf.longitude) : null;
      const country = cf.country   || '';
      const tz      = cf.timezone  || '';
      const data    = { city, lat, lon, country, tz, approx: true };
      return new Response(JSON.stringify(data), {
        headers: {
          'Content-Type': 'application/json',
          'Access-Control-Allow-Origin': '*',
          'Cache-Control': 'no-store',
        }
      });
    }

    // ── Subscribe endpoint ──
    if (path === '/subscribe') return handleSubscribe(request, env);

    // ── URLs sans extension → ajouter .html (301) ──
    // Couvre ~600 URLs GSC sans .html : /us/X-weather-MONTH, /de/X-wetter-MONTH, /meilleure-periode-X, etc.
    if (!path.includes('.') && path !== '/' && !path.startsWith('/api/') && path !== '/subscribe') {
      return Response.redirect(`${url.origin}${path}.html`, 301);
    }

    // ── Regex redirects ──
    const mFR = path.match(PATTERN_FR);
    if (mFR) return Response.redirect(`${url.origin}/${mFR[1]}-meteo-${mFR[2]}.html`, 301);

    const mEN = path.match(PATTERN_EN);
    if (mEN) return Response.redirect(`${url.origin}/en/${mEN[1]}-weather-${mEN[2]}.html`, 301);

    // Old annual root pages → /en/
    const mAnnRoot = path.match(PATTERN_ANNUAL_ROOT);
    if (mAnnRoot) return Response.redirect(`${url.origin}/en/best-time-to-visit-${mAnnRoot[1]}.html`, 301);

    // FR slug with English month → correct FR month
    const mFREnMonth = path.match(PATTERN_FR_EN_MONTH);
    if (mFREnMonth) return Response.redirect(`${url.origin}/${mFREnMonth[1]}-meteo-${EN_TO_FR_MONTH[mFREnMonth[2]]}.html`, 301);

    // /us/best-time-to-visit-X-in-MONTH → /us/X-weather-MONTH
    const mUS = path.match(PATTERN_US);
    if (mUS) return Response.redirect(`${url.origin}/us/${mUS[1]}-weather-${mUS[2]}.html`, 301);

    // Double subdirectory /us/us/ → /us/
    if (path.startsWith('/us/us/')) return Response.redirect(`${url.origin}${path.replace('/us/us/', '/us/')}`, 301);

    // Mariage/wedding pages → homepage
    if (path.includes('mariage') || path.includes('wedding')) return Response.redirect(`${url.origin}/`, 301);

    // /en/index.html → /en/app.html
    if (path === '/en/index.html') return Response.redirect(`${url.origin}/en/app.html`, 301);

    // Old pages renamed
    if (path === '/methodology.html') return Response.redirect(`${url.origin}/methodologie.html`, 301);
    if (path === '/privacy.html') return Response.redirect(`${url.origin}/confidentialite.html`, 301);
    if (path === '/legal.html') return Response.redirect(`${url.origin}/mentions-legales.html`, 301);
    if (path === '/destinations.html') return Response.redirect(`${url.origin}/`, 301);
    if (path === '/methodik.html') return Response.redirect(`${url.origin}/de/app.html`, 301);

    // amalfi-coast slugs → amalfi-coast EN page (not in FR)
    if (path.startsWith('/amalfi-coast-meteo-')) {
      const m = path.match(/^\/amalfi-coast-meteo-([a-z]+)\.html$/);
      if (m) { const fr = EN_TO_FR_MONTH[m[1]] || m[1]; return Response.redirect(`${url.origin}/amalfi-meteo-${fr}.html`, 301); }
    }

    // ── Proxy /data/monthly.json depuis GitHub (hors limite 20k assets CF) ──
    if (path === '/data/monthly.json') {
      const r = await fetch('https://raw.githubusercontent.com/griveti-cloud/bestdateweather/main/data/monthly.json', {
        cf: { cacheTtl: 86400, cacheEverything: true }
      });
      if (!r.ok) return new Response('{}', { status: 200, headers: { 'Content-Type': 'application/json', 'Cache-Control': 'public, max-age=86400' } });
      const body = await r.text();
      return new Response(body, { status: 200, headers: { 'Content-Type': 'application/json', 'Cache-Control': 'public, max-age=86400', 'Access-Control-Allow-Origin': '*' } });
    }

    // ── Proxy /data/suggestions.json depuis GitHub (hors limite 20k assets CF) ──
    if (path === '/data/suggestions.json') {
      const r = await fetch('https://raw.githubusercontent.com/griveti-cloud/bestdateweather/main/data/suggestions.json', {
        cf: { cacheTtl: 86400, cacheEverything: true }
      });
      if (!r.ok) return new Response('{}', { status: 200, headers: { 'Content-Type': 'application/json', 'Cache-Control': 'public, max-age=86400' } });
      const body = await r.text();
      return new Response(body, { status: 200, headers: { 'Content-Type': 'application/json', 'Cache-Control': 'public, max-age=86400', 'Access-Control-Allow-Origin': '*' } });
    }


    // ── Geo-redirect sur la racine ──
    // Uniquement sur "/" — respecte le choix manuel via cookie bdw_lang
    if (path === '/' || path === '/index.html') {
      // Respecter le choix manuel de l'utilisateur
      const cookie = request.headers.get('Cookie') || '';
      const langCookie = cookie.match(/bdw_lang=([a-z-]+)/);
      if (langCookie) {
        const chosen = langCookie[1];
        if (chosen === 'en')    return Response.redirect(url.origin + '/en/app.html', 302);
        if (chosen === 'en-us') return Response.redirect(url.origin + '/us/app.html', 302);
        if (chosen === 'es')    return Response.redirect(url.origin + '/es/app.html', 302);
        if (chosen === 'de')    return Response.redirect(url.origin + '/de/app.html', 302);
        // chosen === 'fr' → laisser passer (index.html)
      } else {
        // Détection par IP (Cloudflare header) en priorité
        const country = (request.cf && request.cf.country) || '';
        // Accept-Language en fallback
        const acceptLang = (request.headers.get('Accept-Language') || '').toLowerCase();

        // Pays US → version US (°F)
        if (country === 'US') {
          return Response.redirect(url.origin + '/us/app.html', 302);
        }
        // Pays hispanophones
        const ES_COUNTRIES = ['ES','MX','AR','CO','CL','PE','VE','EC','BO','PY','UY','CR','PA','HN','SV','GT','NI','DO','CU','PR'];
        if (ES_COUNTRIES.includes(country)) {
          return Response.redirect(url.origin + '/es/app.html', 302);
        }
        // Pays germanophones
        if (['DE','AT','CH','LI','LU'].includes(country)) {
          return Response.redirect(url.origin + '/de/app.html', 302);
        }
        // Pays francophones → index.html (par défaut, pas de redirect)
        const FR_COUNTRIES = ['FR','BE','CA','CH','LU','MC','SN','CI','CM','MG','ML','BF','NE','TD','GN','BJ','TG','RW','BI','CD','CG','GA','CF','KM','DJ','MR','MU','SC','VU','WF','PF','NC','PM','GP','MQ','RE','YT','GF','BL','MF'];
        if (FR_COUNTRIES.includes(country)) {
          // Reste sur index.html, pas de redirect
        } else {
          // Tout le reste du monde → EN (fallback universel)
          // Sauf si Accept-Language suggère FR
          if (!acceptLang.startsWith('fr')) {
            return Response.redirect(url.origin + '/en/app.html', 302);
          }
        }
      }
    }

    // ── Force no-cache on SW cleanup script (override CF Workers Assets immutable) ──
    if (path === '/js/sw-register.js') {
      const r = await env.ASSETS.fetch(request);
      const h = new Headers(r.headers);
      h.set('Cache-Control', 'no-cache, no-store, must-revalidate');
      h.delete('ETag');
      return new Response(r.body, { status: r.status, headers: h });
    }

    // ── Static assets ──
    // Wrap the response: on 404 HTML, inject Clear-Site-Data header to purge
    // any orphaned Service Worker + cache on the client (fixes ghost pages
    // like old /en/best-time-to-visit-pogo.html served from stale SW cache).
    const resp = await env.ASSETS.fetch(request);
    if (resp.status === 404 && path.endsWith('.html')) {
      const h = new Headers(resp.headers);
      h.set('Clear-Site-Data', '"cache", "storage"');
      h.set('Cache-Control', 'no-cache, no-store, must-revalidate');
      return new Response(resp.body, { status: 404, headers: h });
    }
    return resp;
  }
};
