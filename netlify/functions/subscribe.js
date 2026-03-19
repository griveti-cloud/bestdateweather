// Netlify Function : capture email → Brevo
// Clé API stockée dans variable d'environnement Netlify (jamais en front)

exports.handler = async (event) => {
  const headers = {
    'Access-Control-Allow-Origin': 'https://bestdateweather.com',
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Content-Type': 'application/json'
  };

  if (event.httpMethod === 'OPTIONS') {
    return { statusCode: 200, headers, body: '' };
  }

  if (event.httpMethod !== 'POST') {
    return { statusCode: 405, headers, body: JSON.stringify({ error: 'Method not allowed' }) };
  }

  let email, source;
  try {
    const body = JSON.parse(event.body || '{}');
    email = body.email;
    source = body.source || 'favori';
  } catch(e) {
    return { statusCode: 400, headers, body: JSON.stringify({ error: 'Invalid JSON' }) };
  }

  // Validation email basique
  if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    return { statusCode: 400, headers, body: JSON.stringify({ error: 'Email invalide' }) };
  }

  const BREVO_API_KEY = process.env.BREVO_API_KEY;
  if (!BREVO_API_KEY) {
    return { statusCode: 500, headers, body: JSON.stringify({ error: 'Config manquante' }) };
  }

  try {
    const resp = await fetch('https://api.brevo.com/v3/contacts', {
      method: 'POST',
      headers: {
        'api-key': BREVO_API_KEY,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        email,
        attributes: { SOURCE: source },
        listIds: [2], // liste par défaut Brevo
        updateEnabled: true
      })
    });

    if (resp.status === 201 || resp.status === 204) {
      return { statusCode: 200, headers, body: JSON.stringify({ success: true }) };
    }

    // Contact déjà existant = OK
    if (resp.status === 400) {
      const data = await resp.json();
      if (data.code === 'duplicate_parameter') {
        return { statusCode: 200, headers, body: JSON.stringify({ success: true, existing: true }) };
      }
    }

    return { statusCode: 502, headers, body: JSON.stringify({ error: 'Brevo error' }) };

  } catch(e) {
    return { statusCode: 500, headers, body: JSON.stringify({ error: 'Network error' }) };
  }
};
