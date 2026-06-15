#!/usr/bin/env python3
"""
smoke_test_prod.py — Vérification du site EN PRODUCTION après déploiement.

Complément de check_deploy.py (qui teste les fichiers locaux avant deploy).
Ce script teste les URLs réelles servies par Cloudflare : il attrape les
problèmes qui n'apparaissent qu'en prod (config worker, redirections,
propagation cache, headers).

Tourne dans le job smoke-test de la CI (après deploy), ou à la main :
    python3 smoke_test_prod.py

Exit 0 si tout OK, exit 1 si au moins une erreur (alerte CI).
"""
import sys
import re
import urllib.request
import urllib.error

BASE = 'https://bestdateweather.com'

ERRORS = []
WARNINGS = []
OKS = 0

def err(msg):  ERRORS.append(f"❌ {msg}")
def warn(msg): WARNINGS.append(f"⚠️  {msg}")
def ok(msg):
    global OKS
    OKS += 1
    print(f"  ✅ {msg}")

def fetch(url, follow=True, timeout=15):
    """Retourne (status_code, final_url, body) ; suit ou non les redirects."""
    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, *a, **k):
            return None
    opener = urllib.request.build_opener() if follow else \
             urllib.request.build_opener(NoRedirect)
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (smoke-test bestdateweather CI)',
        'Accept-Encoding': 'identity',
    })
    try:
        r = opener.open(req, timeout=timeout)
        body = r.read().decode('utf-8', errors='replace')
        return r.status, r.geturl(), body
    except urllib.error.HTTPError as e:
        return e.code, url, ''
    except Exception as e:
        return None, url, str(e)

def internal_html_links(html):
    return [m for m in re.findall(r'href="([^"]+)"', html)
            if m.endswith('.html') and '://' not in m]

print("\n=== smoke_test_prod.py — Vérification production ===\n")

# ── 1. Pages clés répondent 200 (servies directement, pas de redirect) ───────
print("1. URLs clés servies en 200")
DIRECT_200 = [
    f'{BASE}/',
    f'{BASE}/meilleure-periode-paris',
    f'{BASE}/paris-meteo-juillet',
    f'{BASE}/en/best-time-to-visit-paris',
    f'{BASE}/de/beste-reisezeit-bali',
    f'{BASE}/es/mejor-epoca-paris',
    f'{BASE}/ou-partir-en-mai',
    f'{BASE}/meilleures-destinations-meteo',
    f'{BASE}/a-propos',
    f'{BASE}/methodologie',
]
for url in DIRECT_200:
    status, final, _ = fetch(url, follow=False)
    if status == 200:
        ok(f"200: {url.replace(BASE,'') or '/'}")
    elif status in (301, 302, 307, 308):
        err(f"{url.replace(BASE,'')}: redirige {status} → {final} "
            f"(devrait servir 200 directement)")
    else:
        err(f"{url.replace(BASE,'')}: HTTP {status}")

# ── 2. Canonical == URL servie (sans .html, pas de redirect) ─────────────────
print("\n2. Canonical cohérent (sans .html)")
CANON_CHECK = [
    (f'{BASE}/meilleure-periode-paris', f'{BASE}/meilleure-periode-paris'),
    (f'{BASE}/paris-meteo-juillet', f'{BASE}/paris-meteo-juillet'),
    (f'{BASE}/ou-partir-en-mai', f'{BASE}/ou-partir-en-mai'),
    (f'{BASE}/a-propos', f'{BASE}/a-propos'),
]
for url, expected in CANON_CHECK:
    status, _, body = fetch(url)
    if status != 200:
        err(f"{url.replace(BASE,'')}: HTTP {status} (canonical non vérifiable)")
        continue
    m = re.search(r'rel="canonical" href="([^"]+)"', body)
    if not m:
        err(f"{url.replace(BASE,'')}: canonical absent")
    elif '.html' in m.group(1):
        err(f"{url.replace(BASE,'')}: canonical .html ({m.group(1)})")
    elif m.group(1) != expected:
        warn(f"{url.replace(BASE,'')}: canonical {m.group(1)} (attendu {expected})")
    else:
        ok(f"canonical OK: {url.replace(BASE,'')}")

# ── 3. Format V6 présent sur les fiches annuelles ────────────────────────────
print("\n3. Format V6 en prod (anti-régression)")
V6_MARKERS = ['decider-grid', 'verdict-note', 'method-mini']
V6_URLS = [
    f'{BASE}/meilleure-periode-paris',
    f'{BASE}/en/best-time-to-visit-paris',
    f'{BASE}/de/beste-reisezeit-bali',
]
for url in V6_URLS:
    status, _, body = fetch(url)
    if status != 200:
        err(f"{url.replace(BASE,'')}: HTTP {status}")
        continue
    missing = [m for m in V6_MARKERS if m not in body]
    if missing:
        err(f"{url.replace(BASE,'')}: RÉGRESSION V6 — markers absents {missing}")
    else:
        ok(f"V6 OK: {url.replace(BASE,'')}")

# ── 4. Liens .html internes = 0 (anti redirect en masse) ─────────────────────
print("\n4. Liens .html internes = 0")
LINK_URLS = [
    f'{BASE}/meilleure-periode-paris',
    f'{BASE}/ou-partir-en-mai',
    f'{BASE}/',
]
for url in LINK_URLS:
    status, _, body = fetch(url)
    if status != 200:
        continue
    links = internal_html_links(body)
    if links:
        err(f"{url.replace(BASE,'')}: {len(links)} liens .html internes "
            f"(ex: {links[0]}) → 307")
    else:
        ok(f"0 lien .html: {url.replace(BASE,'')}")

# ── 5. Sitemaps : index OK, pas de vieux sitemap-{lang}.xml ──────────────────
print("\n5. Sitemaps")
status, _, body = fetch(f'{BASE}/sitemap-index.xml')
if status == 200 and '<sitemapindex' in body:
    n = body.count('<sitemap>')
    ok(f"sitemap-index.xml: {n} sitemaps")
else:
    err(f"sitemap-index.xml: HTTP {status}")
# Vieux sitemap doit être 404
status, _, _ = fetch(f'{BASE}/sitemap-fr.xml', follow=False)
if status == 404:
    ok("sitemap-fr.xml → 404 (vieux sitemap supprimé)")
else:
    warn(f"sitemap-fr.xml → HTTP {status} (devrait être 404 : doublon résiduel)")

# ── 6. robots.txt autorise Googlebot ─────────────────────────────────────────
print("\n6. robots.txt")
status, _, body = fetch(f'{BASE}/robots.txt')
if status == 200:
    # Googlebot ne doit PAS être bloqué globalement
    if re.search(r'User-agent:\s*Googlebot\s*\nDisallow:\s*/\s*$', body, re.MULTILINE):
        err("robots.txt: Googlebot bloqué (Disallow: /) !")
    elif 'Sitemap:' in body:
        ok("robots.txt: Googlebot autorisé + Sitemap déclaré")
    else:
        warn("robots.txt: pas de directive Sitemap")
else:
    err(f"robots.txt: HTTP {status}")

# ── 7. Sécurité : badge cohérent (Jordanie rl=4 → pas vert) ──────────────────
print("\n7. Cohérence sécurité (classement)")
status, _, body = fetch(f'{BASE}/ou-partir-en-mai')
if status == 200:
    if 'Math.max(POOL' in body:
        ok("classement: Math.max sur advisories (FR/DE combinés)")
    else:
        err("classement: pas de Math.max → risque badge sécu erroné")
else:
    warn(f"ou-partir-en-mai: HTTP {status}")

# ── Résumé ────────────────────────────────────────────────────────────────────
print(f"\n{'='*55}")
print(f"{OKS} checks OK")
if WARNINGS:
    for w in WARNINGS:
        print(w)
if ERRORS:
    for e in ERRORS:
        print(e)
    print(f"\n❌ {len(ERRORS)} erreur(s) en production !")
    sys.exit(1)
elif WARNINGS:
    print(f"\n⚠️  {len(WARNINGS)} avertissement(s) — site fonctionnel")
    sys.exit(0)
else:
    print("\n✅ Production saine — tous les checks passent")
    sys.exit(0)
