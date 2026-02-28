#!/usr/bin/env python3
"""Regenerate the SEO destination hub in index.html and en/app.html
with search bar + accordion regions + sub-region grouping."""
import csv, re, os
import html as html_mod

# ── Region hierarchy: pays → (continent_id, sub_region, sort) ──
MAPPING = {
    'France': ('france', 'France', 1),
    'Italie': ('europe-sud', 'Italie', 2),
    'Grèce': ('europe-sud', 'Grèce', 2),
    'Espagne': ('europe-sud', 'Espagne', 2),
    'Portugal': ('europe-sud', 'Portugal', 2),
    'Croatie': ('europe-sud', 'Croatie', 2),
    'Malte': ('europe-sud', 'Malte', 2),
    'Monaco': ('europe-sud', 'Monaco', 2),
    'Monténégro': ('europe-sud', 'Monténégro', 2),
    'Albanie': ('europe-sud', 'Albanie', 2),
    'Chypre': ('europe-sud', 'Chypre', 2),
    'Turquie': ('europe-sud', 'Turquie', 2),
    'Slovénie': ('europe-sud', 'Slovénie', 2),
    'Pays-Bas': ('europe-nord', 'Pays-Bas', 3),
    'Allemagne': ('europe-nord', 'Allemagne', 3),
    'Royaume-Uni': ('europe-nord', 'Royaume-Uni', 3),
    'Écosse': ('europe-nord', 'Royaume-Uni', 3),
    'Tchéquie': ('europe-nord', 'Tchéquie', 3),
    'Autriche': ('europe-nord', 'Autriche', 3),
    'Belgique': ('europe-nord', 'Belgique', 3),
    'Hongrie': ('europe-nord', 'Hongrie', 3),
    'Pologne': ('europe-nord', 'Pologne', 3),
    'Roumanie': ('europe-nord', 'Roumanie', 3),
    'Irlande': ('europe-nord', 'Irlande', 3),
    'Islande': ('europe-nord', 'Islande', 3),
    'Suisse': ('europe-nord', 'Suisse', 3),
    'Bulgarie': ('europe-nord', 'Bulgarie', 3),
    'Slovaquie': ('europe-nord', 'Slovaquie', 3),
    'Danemark': ('scandinavie', 'Danemark', 4),
    'Suède': ('scandinavie', 'Suède', 4),
    'Norvège': ('scandinavie', 'Norvège', 4),
    'Finlande': ('scandinavie', 'Finlande', 4),
    'Estonie': ('scandinavie', 'Estonie', 4),
    'Lettonie': ('scandinavie', 'Lettonie', 4),
    'Lituanie': ('scandinavie', 'Lituanie', 4),
    'Géorgie': ('caucase', 'Géorgie', 5),
    'Ouzbékistan': ('caucase', 'Ouzbékistan', 5),
    'Maroc': ('afrique', 'Maroc', 6),
    'Tunisie': ('afrique', 'Tunisie', 6),
    'Égypte': ('afrique', 'Égypte', 6),
    'Kenya': ('afrique', "Afrique de l'Est", 6),
    'Tanzanie': ('afrique', "Afrique de l'Est", 6),
    'Madagascar': ('afrique', 'Océan Indien', 6),
    'Maurice': ('afrique', 'Océan Indien', 6),
    'Seychelles': ('afrique', 'Océan Indien', 6),
    'Réunion': ('afrique', 'Océan Indien', 6),
    'Mayotte': ('afrique', 'Océan Indien', 6),
    'Namibie': ('afrique', 'Afrique australe', 6),
    'Afrique du Sud': ('afrique', 'Afrique australe', 6),
    'Sénégal': ('afrique', "Afrique de l'Ouest", 6),
    'Cap-Vert': ('afrique', "Afrique de l'Ouest", 6),
    'Émirats Arabes Unis': ('moyen-orient', 'Émirats', 7),
    'Jordanie': ('moyen-orient', 'Jordanie', 7),
    'Oman': ('moyen-orient', 'Oman', 7),
    'Israël': ('moyen-orient', 'Israël', 7),
    'Qatar': ('moyen-orient', 'Qatar', 7),
    'Thaïlande': ('asie-se', 'Thaïlande', 8),
    'Viêt Nam': ('asie-se', 'Viêt Nam', 8),
    'Indonésie': ('asie-se', 'Indonésie', 8),
    'Philippines': ('asie-se', 'Philippines', 8),
    'Malaisie': ('asie-se', 'Malaisie', 8),
    'Cambodge': ('asie-se', 'Cambodge', 8),
    'Laos': ('asie-se', 'Laos', 8),
    'Singapour': ('asie-se', 'Singapour', 8),
    'Myanmar': ('asie-se', 'Myanmar', 8),
    'Japon': ('asie-est', 'Japon', 9),
    'Chine': ('asie-est', 'Chine', 9),
    'Corée du Sud': ('asie-est', 'Corée du Sud', 9),
    'Taïwan': ('asie-est', 'Taïwan', 9),
    'Macao': ('asie-est', 'Macao', 9),
    'Hong Kong': ('asie-est', 'Hong Kong', 9),
    'Inde': ('asie-sud', 'Inde', 10),
    'Sri Lanka': ('asie-sud', 'Sri Lanka', 10),
    'Népal': ('asie-sud', 'Népal', 10),
    'Maldives': ('asie-sud', 'Maldives', 10),
    'États-Unis': ('amerique-nord', 'États-Unis', 11),
    'Canada': ('amerique-nord', 'Canada', 11),
    'Guadeloupe': ('caraibes', 'Antilles françaises', 12),
    'Martinique': ('caraibes', 'Antilles françaises', 12),
    'Saint-Barthélemy': ('caraibes', 'Antilles françaises', 12),
    'Saint-Martin': ('caraibes', 'Antilles françaises', 12),
    'République Dominicaine': ('caraibes', 'Grandes Antilles', 12),
    'Cuba': ('caraibes', 'Grandes Antilles', 12),
    'Jamaïque': ('caraibes', 'Grandes Antilles', 12),
    'Porto Rico': ('caraibes', 'Grandes Antilles', 12),
    'Bahamas': ('caraibes', 'Bahamas', 12),
    'Bermudes': ('caraibes', 'Bermudes', 12),
    'Sainte-Lucie': ('caraibes', 'Petites Antilles', 12),
    'Barbade': ('caraibes', 'Petites Antilles', 12),
    'Antigua-et-Barbuda': ('caraibes', 'Petites Antilles', 12),
    'Trinité-et-Tobago': ('caraibes', 'Petites Antilles', 12),
    'Curaçao': ('caraibes', 'ABC & autres', 12),
    'Aruba': ('caraibes', 'ABC & autres', 12),
    'Mexique': ('mex-centram', 'Mexique', 13),
    'Costa Rica': ('mex-centram', 'Amérique Centrale', 13),
    'Panama': ('mex-centram', 'Amérique Centrale', 13),
    'Guatemala': ('mex-centram', 'Amérique Centrale', 13),
    'Belize': ('mex-centram', 'Amérique Centrale', 13),
    'Nicaragua': ('mex-centram', 'Amérique Centrale', 13),
    'Colombie': ('amerique-sud', 'Colombie', 14),
    'Pérou': ('amerique-sud', 'Pérou', 14),
    'Brésil': ('amerique-sud', 'Brésil', 14),
    'Chili': ('amerique-sud', 'Chili', 14),
    'Argentine': ('amerique-sud', 'Argentine', 14),
    'Équateur': ('amerique-sud', 'Équateur', 14),
    'Bolivie': ('amerique-sud', 'Bolivie', 14),
    'Uruguay': ('amerique-sud', 'Uruguay', 14),
    'Australie': ('oceanie', 'Australie', 15),
    'Nouvelle-Zélande': ('oceanie', 'Nouvelle-Zélande', 15),
    'Polynésie française': ('oceanie', 'Pacifique', 15),
    'Fidji': ('oceanie', 'Pacifique', 15),
    'Nouvelle-Calédonie': ('oceanie', 'Pacifique', 15),
    'Guyane': ('outre-mer', 'Guyane', 16),
    'Saint-Pierre-et-Miquelon': ('outre-mer', 'Saint-Pierre-et-Miquelon', 16),
}

CONTINENTS = {
    'france':       {'fr': '🇫🇷 France',                    'en': '🇫🇷 France'},
    'europe-sud':   {'fr': '🌊 Europe du Sud & Méditerranée','en': '🌊 Southern Europe & Mediterranean'},
    'europe-nord':  {'fr': '🏰 Europe du Nord & Centrale',  'en': '🏰 Northern & Central Europe'},
    'scandinavie':  {'fr': '❄️ Scandinavie & Baltique',     'en': '❄️ Scandinavia & Baltics'},
    'caucase':      {'fr': '🏔️ Caucase & Asie Centrale',   'en': '🏔️ Caucasus & Central Asia'},
    'afrique':      {'fr': '🌴 Afrique & Océan Indien',     'en': '🌴 Africa & Indian Ocean'},
    'moyen-orient': {'fr': '🕌 Moyen-Orient',               'en': '🕌 Middle East'},
    'asie-se':      {'fr': '🌏 Asie du Sud-Est',            'en': '🌏 Southeast Asia'},
    'asie-est':     {'fr': "🏯 Asie de l'Est",              'en': '🏯 East Asia'},
    'asie-sud':     {'fr': '🕉️ Asie du Sud',               'en': '🕉️ South Asia'},
    'amerique-nord':{'fr': '🗽 Amérique du Nord',           'en': '🗽 North America'},
    'caraibes':     {'fr': '🏝️ Caraïbes',                  'en': '🏝️ Caribbean'},
    'mex-centram':  {'fr': '🌮 Mexique & Amérique Centrale','en': '🌮 Mexico & Central America'},
    'amerique-sud': {'fr': '🌎 Amérique du Sud',            'en': '🌎 South America'},
    'oceanie':      {'fr': '🦘 Océanie & Pacifique',        'en': '🦘 Oceania & Pacific'},
    'outre-mer':    {'fr': "🇫🇷 France d'outre-mer",       'en': '🇫🇷 French Overseas'},
}

# ── CSS ──
CSS = """
/* ── Destination Hub ── */
.dh-search{position:relative;margin-bottom:24px}
.dh-search input{width:100%;padding:14px 16px 14px 44px;border:1.5px solid #e8e0d0;border-radius:12px;font-size:15px;font-family:inherit;background:#fff;color:#1a1f2e;outline:none;transition:border-color .2s;box-sizing:border-box}
.dh-search input:focus{border-color:#e8940a}
.dh-search input::placeholder{color:#9ca3af}
.dh-search-icon{position:absolute;left:14px;top:50%;transform:translateY(-50%);color:#9ca3af;pointer-events:none;font-size:18px}
.dh-search-clear{position:absolute;right:12px;top:50%;transform:translateY(-50%);background:none;border:none;font-size:18px;color:#9ca3af;cursor:pointer;padding:4px;display:none}
.dh-search-clear.show{display:block}
.dh-count{font-size:12px;color:#7a8fa8;margin:-16px 0 20px 4px;display:none}
.dh-count.show{display:block}
.dh-accordion{border:1.5px solid #e8e0d0;border-radius:12px;margin-bottom:10px;overflow:hidden;background:#fff}
.dh-accordion-head{width:100%;display:flex;align-items:center;justify-content:space-between;padding:16px 18px;background:#fff;border:none;cursor:pointer;font-family:inherit;text-align:left;gap:12px}
.dh-accordion-head:hover{background:#faf8f3}
.dh-accordion-label{font-size:15px;font-weight:700;color:#1a1f2e}
.dh-accordion-meta{display:flex;align-items:center;gap:10px;flex-shrink:0}
.dh-accordion-count{font-size:12px;color:#7a8fa8;background:#f0ebe0;border-radius:20px;padding:2px 10px;font-weight:600}
.dh-accordion-chevron{font-size:14px;color:#9ca3af;transition:transform .25s}
.dh-accordion.open .dh-accordion-chevron{transform:rotate(180deg)}
.dh-accordion-body{display:none;padding:0 18px 18px}
.dh-accordion.open .dh-accordion-body{display:block}
.dh-subregion{font-size:11px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:#7a5205;margin:18px 0 10px;padding-bottom:6px;border-bottom:1px solid #f0ebe0}
.dh-subregion:first-child{margin-top:4px}
.dh-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(155px,1fr));gap:8px;margin-bottom:4px}
.dh-card{background:#faf8f3;border-radius:10px;padding:10px 12px;text-decoration:none;border:1px solid #e8e0d0;display:flex;align-items:center;gap:9px;transition:border-color .15s,box-shadow .15s}
.dh-card:hover{border-color:#e8940a;box-shadow:0 2px 8px rgba(232,148,10,.12)}
.dh-card img{flex-shrink:0}
.dh-card-name{font-size:12px;font-weight:700;color:#1a1f2e;display:block;line-height:1.3}
.dh-card-sub{font-size:10px;color:#7a8fa8}
.dh-card.dh-hidden{display:none}
.dh-no-results{display:none;text-align:center;padding:32px 16px;color:#7a8fa8;font-size:14px}
.dh-no-results.show{display:block}
@media(max-width:640px){
 .dh-grid{grid-template-columns:repeat(auto-fill,minmax(140px,1fr));gap:6px}
 .dh-card{padding:9px 10px}
 .dh-accordion-head{padding:14px 14px}
 .dh-accordion-label{font-size:14px}
}
"""

# ── JS ──
JS_CORE = """
(function(){
 var inp=document.getElementById('dh-input'),
     clear=document.getElementById('dh-clear'),
     count=document.getElementById('dh-count'),
     cards=document.querySelectorAll('.dh-card'),
     accs=document.querySelectorAll('.dh-accordion'),
     noRes=document.getElementById('dh-no-results');

 function norm(s){return s.normalize('NFD').replace(/[\\u0300-\\u036f]/g,'').toLowerCase()}

 function doSearch(){
  var q=norm(inp.value.trim());
  clear.className='dh-search-clear'+(q?' show':'');
  if(!q){
   cards.forEach(function(c){c.classList.remove('dh-hidden')});
   accs.forEach(function(a){a.classList.remove('open','dh-search-mode');a.style.display=''});
   count.className='dh-count';noRes.className='dh-no-results';
   return;
  }
  var n=0;
  cards.forEach(function(c){
   var t=norm(c.getAttribute('data-name')||'');
   var p=norm(c.getAttribute('data-country')||'');
   if(t.indexOf(q)>-1||p.indexOf(q)>-1){c.classList.remove('dh-hidden');n++}
   else{c.classList.add('dh-hidden')}
  });
  accs.forEach(function(a){
   var vis=a.querySelectorAll('.dh-card:not(.dh-hidden)');
   if(vis.length){a.classList.add('open','dh-search-mode');a.style.display=''}
   else{a.style.display='none'}
  });
  count.textContent=n+' '+__FOUND_FN__(n);
  count.className='dh-count show';
  noRes.className='dh-no-results'+(n===0?' show':'');
 }

 inp.addEventListener('input',doSearch);
 clear.addEventListener('click',function(){inp.value='';doSearch();inp.focus()});

 document.querySelectorAll('.dh-accordion-head').forEach(function(h){
  h.addEventListener('click',function(){
   var acc=h.parentElement;
   if(acc.classList.contains('dh-search-mode'))return;
   acc.classList.toggle('open');
  });
 });
})();
"""

JS_FR = JS_CORE.replace('__FOUND_FN__(n)', "(n>1?'destinations trouvées':'destination trouvée')")
JS_EN = JS_CORE.replace('__FOUND_FN__(n)', "(n>1?'destinations found':'destination found')")


def make_card(slug, name, bare, flag, country, prefix, is_fr):
    href = f'{prefix}meilleure-periode-{slug}.html' if is_fr else f'{prefix}best-time-to-visit-{slug}.html'
    sub = 'Quand partir' if is_fr else 'When to visit'
    return (
        f'<a href="{href}" target="_top" class="dh-card" '
        f'data-name="{html_mod.escape(bare)}" data-country="{html_mod.escape(country)}">'
        f'<img src="{prefix}flags/{flag}.png" width="20" height="15" alt="{flag.upper()}" style="border-radius:2px">'
        f'<span><span class="dh-card-name">{html_mod.escape(name)}</span>'
        f'<span class="dh-card-sub">{sub}</span></span></a>'
    )


def build_hub(destinations, is_fr=True):
    prefix = '' if is_fr else '../'
    lang = 'fr' if is_fr else 'en'

    # Group by continent → sub_region
    continents = {}
    for d in destinations:
        pays = d['pays']
        if pays in MAPPING:
            cid, sub, sort = MAPPING[pays]
        else:
            cid, sub, sort = 'autres', pays, 99
            print(f"  ⚠️  Pays sans mapping: {pays} ({d['nom_fr']})")
        if cid not in continents:
            continents[cid] = {'order': sort, 'subs': {}}
        if sub not in continents[cid]['subs']:
            continents[cid]['subs'][sub] = []
        continents[cid]['subs'][sub].append(d)

    L = []

    # Search
    ph = 'Rechercher une destination…' if is_fr else 'Search a destination…'
    L.append(f'<div class="dh-search"><span class="dh-search-icon">🔍</span>')
    L.append(f'<input type="text" id="dh-input" placeholder="{ph}" autocomplete="off">')
    L.append(f'<button id="dh-clear" class="dh-search-clear" aria-label="Clear">✕</button></div>')
    L.append(f'<div id="dh-count" class="dh-count"></div>')

    # Accordions
    for cid, data in sorted(continents.items(), key=lambda x: x[1]['order']):
        info = CONTINENTS.get(cid, {'fr': cid, 'en': cid})
        label = info[lang]
        cnt = sum(len(v) for v in data['subs'].values())
        show_subs = len(data['subs']) > 1

        L.append(f'<div class="dh-accordion">')
        L.append(f'<button class="dh-accordion-head" aria-expanded="false">')
        L.append(f'<span class="dh-accordion-label">{label}</span>')
        L.append(f'<span class="dh-accordion-meta"><span class="dh-accordion-count">{cnt}</span>')
        L.append(f'<span class="dh-accordion-chevron">▾</span></span></button>')
        L.append(f'<div class="dh-accordion-body">')

        for sub_name, dests in sorted(data['subs'].items()):
            if show_subs:
                L.append(f'<div class="dh-subregion">{html_mod.escape(sub_name)}</div>')
            L.append('<div class="dh-grid">')
            for d in sorted(dests, key=lambda x: x['nom_bare']):
                slug = d['slug_fr'] if is_fr else d['slug_en']
                name = d['nom_fr'] if is_fr else d['nom_en']
                L.append(make_card(slug, name, d['nom_bare'], d['flag'], d['pays'], prefix, is_fr))
            L.append('</div>')

        L.append('</div></div>')

    no_msg = 'Aucune destination trouvée.' if is_fr else 'No destinations found.'
    L.append(f'<div id="dh-no-results" class="dh-no-results">{no_msg}</div>')

    return '\n'.join(L)


def inject(filepath, destinations, is_fr=True):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    total = len(destinations)

    # Update counts
    content = re.sub(r'Voir les guides destinations \(\d+ destinations\)',
                     f'Voir les guides destinations ({total} destinations)', content)
    content = re.sub(r'Tableaux climatiques mensuels · \d+ destinations',
                     f'Tableaux climatiques mensuels · {total} destinations', content)

    # Inject CSS
    if '/* ── Destination Hub ── */' not in content:
        content = content.replace(
            '#inp-date.has-val{color:var(--navy)}',
            '#inp-date.has-val{color:var(--navy)}\n' + CSS, 1)
    else:
        content = re.sub(
            r'/\* ── Destination Hub ── \*/.*?(?=#inp-date|</style>)',
            CSS, content, flags=re.DOTALL)

    # Build new SILO 1
    hub = build_hub(destinations, is_fr)
    js = JS_FR if is_fr else JS_EN
    title = 'Meilleure p&eacute;riode par destination' if is_fr else 'Best time to visit by destination'

    new_silo = f"""<!-- SILO 1 : MEILLEURE PERIODE - dominant -->
 <div style="margin-bottom:52px">
  <div style="display:flex;align-items:center;gap:14px;margin-bottom:22px">
   <p style="font-size:13px;font-weight:800;letter-spacing:.5px;text-transform:uppercase;color:#1a1f2e;margin:0">&#127758; {title}</p>
   <div style="flex:1;height:2px;background:linear-gradient(90deg,#e8940a,#e8e0d0)"></div>
  </div>
{hub}
 </div>
<script>
{js}
</script>"""

    # Use string find instead of re.sub to avoid JS escape issues
    start_marker = '<!-- SILO 1 : MEILLEURE PERIODE - dominant -->'
    end_marker = '\n <!-- SILO 2'
    start_idx = content.find(start_marker)
    end_idx = content.find(end_marker, start_idx)

    if start_idx == -1 or end_idx == -1:
        print(f"  ⚠️  SILO 1 markers not found in {filepath}")
        return False

    new_content = content[:start_idx] + new_silo + content[end_idx:]

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    return True


# ── Main ──
dests = []
with open('data/destinations.csv', encoding='utf-8-sig') as f:
    for r in csv.DictReader(f):
        dests.append(r)
print(f"📦 {len(dests)} destinations")

print("\n🇫🇷 index.html...")
if inject('index.html', dests, True):
    c = len(re.findall(r'meilleure-periode-', open('index.html').read()))
    print(f"  ✅ {c} liens")

if os.path.exists('en/app.html'):
    print("\n🇬🇧 en/app.html...")
    if 'SILO 1' in open('en/app.html').read():
        if inject('en/app.html', dests, False):
            c = len(re.findall(r'best-time-to-visit-', open('en/app.html').read()))
            print(f"  ✅ {c} liens")

print("\n✅ Done")
