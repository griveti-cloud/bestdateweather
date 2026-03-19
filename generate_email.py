#!/usr/bin/env python3
"""
generate_email.py — Génère et envoie l'email mensuel BestDateWeather
Usage : python3 generate_email.py [--month 4] [--dry-run] [--preview]

--month N   : forcer le mois (1-12), par défaut mois suivant
--dry-run   : générer le HTML sans envoyer
--preview   : ouvrir le HTML dans le navigateur
"""

import csv, json, os, sys, argparse
from datetime import date
from urllib.request import urlopen, Request
from urllib.parse import urlencode

# ── Config ───────────────────────────────────────────────────────────────────
BREVO_API_KEY = os.environ.get('BREVO_API_KEY', '')
SITE_URL      = 'https://bestdateweather.com'
FROM_EMAIL    = 'contact@bestdateweather.com'
FROM_NAME     = 'BestDateWeather'
LIST_ID       = 2  # liste Brevo par défaut

MOIS_FR = ['','janvier','février','mars','avril','mai','juin',
           'juillet','août','septembre','octobre','novembre','décembre']

MOIS_CAP = ['','Janvier','Février','Mars','Avril','Mai','Juin',
            'Juillet','Août','Septembre','Octobre','Novembre','Décembre']

# ── Données ──────────────────────────────────────────────────────────────────
def load_data():
    with open('data/climate.csv', encoding='utf-8-sig') as f:
        climate = list(csv.DictReader(f))
    with open('data/destinations.csv', encoding='utf-8-sig') as f:
        dests = {r['slug_fr']: r for r in csv.DictReader(f)}
    with open('data/editorial.json') as f:
        editorial = json.load(f)
    return climate, dests, editorial

def get_top5(climate, dests, editorial, month):
    rows = [r for r in climate if int(r['mois_num']) == month]
    top = sorted(rows, key=lambda x: float(x['score']), reverse=True)[:5]
    result = []
    for r in top:
        slug = r['slug']
        dest = dests.get(slug, {})
        ed_key = f"{slug}:{month}:fr"
        blurb = editorial.get(ed_key, '')[:160]
        # Couper proprement à la dernière phrase complète
        if len(blurb) == 160 and '.' in blurb:
            blurb = blurb[:blurb.rfind('.')+1]
        result.append({
            'slug':    slug,
            'nom':     dest.get('nom_fr', slug),
            'pays':    dest.get('pays', ''),
            'flag':    dest.get('flag', ''),
            'score':   float(r['score']),
            'tmax':    r['tmax'],
            'sun_h':   r['sun_h'],
            'rain':    r['rain_pct'],
            'blurb':   blurb,
            'url':     f"{SITE_URL}/meilleure-periode-{slug}.html",
        })
    return result

# ── Génération HTML ───────────────────────────────────────────────────────────
def score_color(s):
    if s >= 9: return '#16a34a'
    if s >= 7: return '#d97706'
    return '#dc2626'

def build_html(month, destinations):
    mois_nom  = MOIS_FR[month]
    mois_cap  = MOIS_CAP[month]
    year      = date.today().year

    cards = ''
    for i, d in enumerate(destinations):
        color = score_color(d['score'])
        flag_url = f"{SITE_URL}/flags/{d['flag']}.png" if d['flag'] else ''
        cards += f'''
    <tr>
      <td style="padding:0 0 20px 0">
        <table width="100%" cellpadding="0" cellspacing="0" border="0"
               style="background:#ffffff;border-radius:12px;border:1px solid #e8e0d0;overflow:hidden">
          <tr>
            <td style="padding:20px 24px">
              <!-- Rang + nom -->
              <table width="100%" cellpadding="0" cellspacing="0" border="0">
                <tr>
                  <td>
                    <span style="font-size:11px;font-weight:700;color:#94a3b8;text-transform:uppercase;letter-spacing:.5px">#{i+1}</span>
                    {'<img src="' + flag_url + '" width="20" height="15" alt="" style="vertical-align:middle;margin:0 6px 2px;border-radius:2px">' if flag_url else ''}
                    <span style="font-family:Georgia,serif;font-size:18px;font-weight:700;color:#1a1f2e">{d['nom']}</span>
                    <span style="font-size:13px;color:#64748b;margin-left:6px">{d['pays']}</span>
                  </td>
                  <td align="right">
                    <span style="font-size:22px;font-weight:800;color:{color}">{d['score']:.1f}</span>
                    <span style="font-size:11px;color:#94a3b8">/10</span>
                  </td>
                </tr>
              </table>
              <!-- Stats -->
              <table cellpadding="0" cellspacing="0" border="0" style="margin:10px 0 12px">
                <tr>
                  <td style="padding-right:16px;font-size:12px;color:#475569">🌡 <strong>{d['tmax']}°C</strong></td>
                  <td style="padding-right:16px;font-size:12px;color:#475569">☀️ <strong>{d['sun_h']}h</strong> soleil</td>
                  <td style="font-size:12px;color:#475569">🌧 <strong>{d['rain']}%</strong> pluie</td>
                </tr>
              </table>
              <!-- Blurb -->
              <p style="font-size:14px;color:#374151;line-height:1.6;margin:0 0 14px">{d['blurb']}</p>
              <!-- CTA -->
              <a href="{d['url']}" style="display:inline-block;background:#d97706;color:#ffffff;font-weight:700;font-size:13px;padding:9px 18px;border-radius:8px;text-decoration:none">
                Voir la météo de {mois_cap} →
              </a>
            </td>
          </tr>
        </table>
      </td>
    </tr>'''

    return f'''<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1.0"/>
<title>Top 5 destinations — {mois_cap} {year}</title>
</head>
<body style="margin:0;padding:0;background:#f1f5f9;font-family:DM Sans,Arial,sans-serif">
<table width="100%" cellpadding="0" cellspacing="0" border="0" style="background:#f1f5f9;padding:32px 16px">
  <tr><td align="center">
    <table width="600" cellpadding="0" cellspacing="0" border="0" style="max-width:600px;width:100%">

      <!-- Header -->
      <tr><td style="padding-bottom:24px;text-align:center">
        <a href="{SITE_URL}" style="font-family:Georgia,serif;font-size:22px;font-weight:700;color:#1a1f2e;text-decoration:none">
          Best<em style="color:#d97706">Date</em>Weather
        </a>
      </td></tr>

      <!-- Hero -->
      <tr><td style="background:linear-gradient(135deg,#0d1a3a,#1a2a6a);border-radius:16px;padding:32px 28px;text-align:center;margin-bottom:24px">
        <p style="margin:0 0 8px;font-size:13px;font-weight:700;color:#93c5fd;text-transform:uppercase;letter-spacing:.8px">Météo voyage</p>
        <h1 style="margin:0 0 12px;font-family:Georgia,serif;font-size:28px;font-weight:700;color:#ffffff;line-height:1.2">
          Top 5 destinations<br>pour <em style="color:#d97706">{mois_cap} {year}</em>
        </h1>
        <p style="margin:0;font-size:14px;color:rgba(255,255,255,.7)">
          Sélection basée sur 10 ans de données ERA5/ECMWF · 696 destinations analysées
        </p>
      </td></tr>

      <tr><td style="padding:24px 0 0">
        <table width="100%" cellpadding="0" cellspacing="0" border="0">
          {cards}
        </table>
      </td></tr>

      <!-- Footer -->
      <tr><td style="padding:24px 0;text-align:center;border-top:1px solid #e2e8f0">
        <p style="margin:0 0 8px;font-size:12px;color:#94a3b8">
          Vous recevez cet email car vous êtes inscrit à BestDateWeather.
        </p>
        <p style="margin:0;font-size:12px;color:#94a3b8">
          <a href="{SITE_URL}" style="color:#d97706">bestdateweather.com</a> ·
          <a href="{{{{ unsubscribe }}}}" style="color:#94a3b8">Se désabonner</a>
        </p>
      </td></tr>

    </table>
  </td></tr>
</table>
</body>
</html>'''

# ── Envoi Brevo ───────────────────────────────────────────────────────────────
def send_campaign(html, month, year, dry_run=False):
    if not BREVO_API_KEY:
        print("❌ BREVO_API_KEY manquante")
        return False

    mois_cap = MOIS_CAP[month]
    subject  = f"🌍 Top 5 destinations météo pour {mois_cap} {year}"

    import json as _json
    from urllib.request import urlopen, Request
    from urllib.error import HTTPError

    headers = {
        'api-key': BREVO_API_KEY,
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    payload = {
        "name": f"BDW Top 5 {mois_cap} {year}",
        "subject": subject,
        "sender": {"name": FROM_NAME, "email": FROM_EMAIL},
        "type": "classic",
        "htmlContent": html,
        "recipients": {"listIds": [LIST_ID]},
        "header": f"Meilleure période pour voyager en {mois_cap}"
    }

    if dry_run:
        print(f"[DRY-RUN] Campagne : {subject}")
        print(f"[DRY-RUN] Taille HTML : {len(html):,} caractères")
        print("[DRY-RUN] Pas d'envoi")
        return True

    try:
        req = Request(
            'https://api.brevo.com/v3/emailCampaigns',
            data=_json.dumps(payload).encode(),
            headers=headers,
            method='POST'
        )
        with urlopen(req) as resp:
            data = _json.loads(resp.read())
            campaign_id = data.get('id')
            print(f"✅ Campagne créée (id={campaign_id})")

        # Envoyer maintenant
        req2 = Request(
            f'https://api.brevo.com/v3/emailCampaigns/{campaign_id}/sendNow',
            data=b'{}',
            headers=headers,
            method='POST'
        )
        with urlopen(req2) as resp2:
            print(f"✅ Campagne envoyée !")
            return True

    except HTTPError as e:
        print(f"❌ Erreur Brevo {e.code}: {e.read().decode()}")
        return False

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--month', type=int, default=None)
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--preview', action='store_true')
    args = parser.parse_args()

    today = date.today()
    month = args.month or (today.month % 12 + 1)
    year  = today.year if month > today.month else today.year

    print(f"=== Email BestDateWeather — {MOIS_CAP[month]} {year} ===")

    climate, dests, editorial = load_data()
    top5 = get_top5(climate, dests, editorial, month)

    print(f"Top 5 destinations :")
    for d in top5:
        print(f"  {d['flag']} {d['nom']:25} {d['score']:.1f}/10")

    html = build_html(month, top5)

    # Sauvegarder pour preview
    out = f"email_preview_{MOIS_FR[month]}.html"
    with open(out, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"\n📄 HTML sauvegardé : {out} ({len(html):,} chars)")

    if args.preview:
        import webbrowser
        webbrowser.open(out)
        return

    if args.dry_run:
        send_campaign(html, month, year, dry_run=True)
    else:
        confirm = input(f"\nEnvoyer à la liste Brevo #{LIST_ID} ? (oui/non) : ")
        if confirm.lower() == 'oui':
            send_campaign(html, month, year, dry_run=False)
        else:
            print("Annulé.")

if __name__ == '__main__':
    main()
