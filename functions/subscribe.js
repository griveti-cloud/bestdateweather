/**
 * Cloudflare Pages Function — capture email → Brevo
 * Equivalent de netlify/functions/subscribe.js
 * Route: /subscribe (POST)
 */

export async function onRequestPost(context) {
  const { request, env } = context;

  const headers = {
    'Access-Control-Allow-Origin': 'https://bestdateweather.com',
    'Content-Type': 'application/json'
  };

  let email, source;
  try {
    const body = await request.json();
    email = body.email;
    source = body.source || 'favori';
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
      body: JSON.stringify({
        email,
        attributes: { SOURCE: source },
        listIds: [2],
        updateEnabled: true
      })
    });

    if (resp.status === 201 || resp.status === 204) {
      return new Response(JSON.stringify({ success: true }), { status: 200, headers });
    }
    if (resp.status === 400) {
      const data = await resp.json();
      if (data.code === 'duplicate_parameter') {
        return new Response(JSON.stringify({ success: true, existing: true }), { status: 200, headers });
      }
    }
    return new Response(JSON.stringify({ error: 'Brevo error' }), { status: 502, headers });
  } catch(e) {
    return new Response(JSON.stringify({ error: 'Network error' }), { status: 500, headers });
  }
}

export async function onRequestOptions() {
  return new Response(null, {
    status: 200,
    headers: {
      'Access-Control-Allow-Origin': 'https://bestdateweather.com',
      'Access-Control-Allow-Methods': 'POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type'
    }
  });
}
