#!/usr/bin/env python3
"""Regenerate SEO destination hub: search + 6 accordions + sub-accordions."""
import csv, re, os
import html as html_mod

# ── slug → (mega_region, sub_region) overrides ──
# Priorité sur MAPPING[pays] pour les territoires géographiquement hors-métropole
SLUG_OVERRIDE = {
    # DOM-TOM français → régions géographiques
    'guadeloupe':     ('ameriques', 'Caraïbes'),
    'martinique':     ('ameriques', 'Caraïbes'),
    'saint-martin':   ('ameriques', 'Caraïbes'),
    'saint-barthelemy': ('ameriques', 'Caraïbes'),
    'guyane':         ('ameriques', 'Amérique du Sud'),
    'reunion':        ('afrique-mo', 'Océan Indien'),
    'mayotte':        ('afrique-mo', 'Océan Indien'),
    'polynesie':      ('oceanie', 'Pacifique & Outre-mer'),
    'bora-bora':      ('oceanie', 'Pacifique & Outre-mer'),
    'nouvelle-caledonie': ('oceanie', 'Pacifique & Outre-mer'),
    'saint-pierre-et-miquelon': ('ameriques', 'Amérique du Nord'),
    # Bermudes (Royaume-Uni) → Caraïbes
    'bermudes':       ('ameriques', 'Caraïbes'),
    # Canaries (Espagne) → Macaronésie
    'canaries':       ('afrique-mo', 'Macaronésie'),
    'tenerife':       ('afrique-mo', 'Macaronésie'),
    'gran-canaria':   ('afrique-mo', 'Macaronésie'),
    'fuerteventura':  ('afrique-mo', 'Macaronésie'),
    'lanzarote':      ('afrique-mo', 'Macaronésie'),
    'la-palma':       ('afrique-mo', 'Macaronésie'),
    'la-gomera':      ('afrique-mo', 'Macaronésie'),
    'el-hierro':      ('afrique-mo', 'Macaronésie'),
}

# ── pays → (mega_region, sub_region) ──
MAPPING = {
    'France': ('france', 'France'),
    # EUROPE
    'Albanie': ('europe', 'Europe du Sud & Méditerranée'),
    'Bosnie-Herzégovine': ('europe', 'Europe du Sud & Méditerranée'),
    'Chypre': ('europe', 'Europe du Sud & Méditerranée'),
    'Croatie': ('europe', 'Europe du Sud & Méditerranée'),
    'Espagne': ('europe', 'Europe du Sud & Méditerranée'),
    'Grèce': ('europe', 'Europe du Sud & Méditerranée'),
    'Italie': ('europe', 'Europe du Sud & Méditerranée'),
    'Macédoine du Nord': ('europe', 'Europe du Sud & Méditerranée'),
    'Malte': ('europe', 'Europe du Sud & Méditerranée'),
    'Monaco': ('europe', 'Europe du Sud & Méditerranée'),
    'Monténégro': ('europe', 'Europe du Sud & Méditerranée'),
    'Portugal': ('europe', 'Europe du Sud & Méditerranée'),
    'Serbie': ('europe', 'Europe du Sud & Méditerranée'),
    'Slovénie': ('europe', 'Europe du Sud & Méditerranée'),
    'Turquie': ('europe', 'Europe du Sud & Méditerranée'),
    'Allemagne': ('europe', 'Europe du Nord & Centrale'),
    'Autriche': ('europe', 'Europe du Nord & Centrale'),
    'Belgique': ('europe', 'Europe du Nord & Centrale'),
    'Bulgarie': ('europe', 'Europe du Nord & Centrale'),
    'Hongrie': ('europe', 'Europe du Nord & Centrale'),
    'Irlande': ('europe', 'Europe du Nord & Centrale'),
    'Islande': ('europe', 'Europe du Nord & Centrale'),
    'Pays-Bas': ('europe', 'Europe du Nord & Centrale'),
    'Pologne': ('europe', 'Europe du Nord & Centrale'),
    'Roumanie': ('europe', 'Europe du Nord & Centrale'),
    'Royaume-Uni': ('europe', 'Europe du Nord & Centrale'),
    'Slovaquie': ('europe', 'Europe du Nord & Centrale'),
    'Suisse': ('europe', 'Europe du Nord & Centrale'),
    'Tchéquie': ('europe', 'Europe du Nord & Centrale'),
    'Écosse': ('europe', 'Europe du Nord & Centrale'),
    'Danemark': ('europe', 'Scandinavie & Baltique'),
    'Estonie': ('europe', 'Scandinavie & Baltique'),
    'Finlande': ('europe', 'Scandinavie & Baltique'),
    'Lettonie': ('europe', 'Scandinavie & Baltique'),
    'Lituanie': ('europe', 'Scandinavie & Baltique'),
    'Norvège': ('europe', 'Scandinavie & Baltique'),
    'Suède': ('europe', 'Scandinavie & Baltique'),
    'Géorgie': ('europe', 'Caucase & Asie Centrale'),
    'Kazakhstan': ('europe', 'Caucase & Asie Centrale'),
    'Kirghizistan': ('europe', 'Caucase & Asie Centrale'),
    'Ouzbékistan': ('europe', 'Caucase & Asie Centrale'),
    'Ukraine': ('europe', 'Europe du Nord & Centrale'),
    # AFRIQUE & MOYEN-ORIENT
    'Maroc': ('afrique-mo', 'Afrique du Nord'),
    'Tunisie': ('afrique-mo', 'Afrique du Nord'),
    'Égypte': ('afrique-mo', 'Afrique du Nord'),
    'Cap-Vert': ('afrique-mo', "Afrique de l'Ouest"),
    "Côte d'Ivoire": ('afrique-mo', "Afrique de l'Ouest"),
    'Ghana': ('afrique-mo', "Afrique de l'Ouest"),
    'Nigeria': ('afrique-mo', "Afrique de l'Ouest"),
    'Sénégal': ('afrique-mo', "Afrique de l'Ouest"),
    'Burkina Faso': ('afrique-mo', "Afrique de l'Ouest"),
    'Bénin': ('afrique-mo', "Afrique de l'Ouest"),
    'Cameroun': ('afrique-mo', "Afrique de l'Ouest"),
    'Sierra Leone': ('afrique-mo', "Afrique de l'Ouest"),
    'Togo': ('afrique-mo', "Afrique de l'Ouest"),
    'Kenya': ('afrique-mo', "Afrique de l'Est"),
    'Ouganda': ('afrique-mo', "Afrique de l'Est"),
    'Rwanda': ('afrique-mo', "Afrique de l'Est"),
    'Tanzanie': ('afrique-mo', "Afrique de l'Est"),
    'Éthiopie': ('afrique-mo', "Afrique de l'Est"),
    'Afrique du Sud': ('afrique-mo', 'Afrique australe'),
    'Mozambique': ('afrique-mo', 'Afrique australe'),
    'Namibie': ('afrique-mo', 'Afrique australe'),
    'Zimbabwe': ('afrique-mo', 'Afrique australe'),
    'Botswana': ('afrique-mo', 'Afrique australe'),
    'Zambie': ('afrique-mo', 'Afrique australe'),
    'Madagascar': ('afrique-mo', 'Océan Indien'),
    'Maurice': ('afrique-mo', 'Océan Indien'),
    'Seychelles': ('afrique-mo', 'Océan Indien'),
    'Arabie Saoudite': ('afrique-mo', 'Moyen-Orient'),
    'Bahreïn': ('afrique-mo', 'Moyen-Orient'),
    'Iran': ('afrique-mo', 'Moyen-Orient'),
    'Israël': ('afrique-mo', 'Moyen-Orient'),
    'Jordanie': ('afrique-mo', 'Moyen-Orient'),
    'Koweït': ('afrique-mo', 'Moyen-Orient'),
    'Liban': ('afrique-mo', 'Moyen-Orient'),
    'Oman': ('afrique-mo', 'Moyen-Orient'),
    'Qatar': ('afrique-mo', 'Moyen-Orient'),
    'Émirats Arabes Unis': ('afrique-mo', 'Moyen-Orient'),
    'Yémen': ('afrique-mo', 'Moyen-Orient'),
    # ASIE
    'Cambodge': ('asie', 'Asie du Sud-Est'),
    'Indonésie': ('asie', 'Asie du Sud-Est'),
    'Laos': ('asie', 'Asie du Sud-Est'),
    'Malaisie': ('asie', 'Asie du Sud-Est'),
    'Myanmar': ('asie', 'Asie du Sud-Est'),
    'Philippines': ('asie', 'Asie du Sud-Est'),
    'Singapour': ('asie', 'Asie du Sud-Est'),
    'Thaïlande': ('asie', 'Asie du Sud-Est'),
    'Viêt Nam': ('asie', 'Asie du Sud-Est'),
    'Chine': ('asie', "Asie de l'Est"),
    'Corée du Sud': ('asie', "Asie de l'Est"),
    'Hong Kong': ('asie', "Asie de l'Est"),
    'Japon': ('asie', "Asie de l'Est"),
    'Macao': ('asie', "Asie de l'Est"),
    'Taïwan': ('asie', "Asie de l'Est"),
    'Mongolie': ('asie', "Asie de l'Est"),
    'Inde': ('asie', 'Asie du Sud'),
    'Bhoutan': ('asie', 'Asie du Sud'),
    'Maldives': ('asie', 'Asie du Sud'),
    'Népal': ('asie', 'Asie du Sud'),
    'Sri Lanka': ('asie', 'Asie du Sud'),
    # AMÉRIQUES
    'Canada': ('ameriques', 'Amérique du Nord'),
    'États-Unis': ('ameriques', 'Amérique du Nord'),
    'Antigua-et-Barbuda': ('ameriques', 'Caraïbes'),
    'Aruba': ('ameriques', 'Caraïbes'),
    'Bahamas': ('ameriques', 'Caraïbes'),
    'Barbade': ('ameriques', 'Caraïbes'),
    'Cuba': ('ameriques', 'Caraïbes'),
    'Curaçao': ('ameriques', 'Caraïbes'),
    'Jamaïque': ('ameriques', 'Caraïbes'),
    'Porto Rico': ('ameriques', 'Caraïbes'),
    'République Dominicaine': ('ameriques', 'Caraïbes'),
    'Sainte-Lucie': ('ameriques', 'Caraïbes'),
    'Trinité-et-Tobago': ('ameriques', 'Caraïbes'),
    'Turks-et-Caïcos': ('ameriques', 'Caraïbes'),
    'Dominique': ('ameriques', 'Caraïbes'),
    'Pays-Bas caribéens': ('ameriques', 'Caraïbes'),
    'Saint-Vincent-et-les-Grenadines': ('ameriques', 'Caraïbes'),
    'Belize': ('ameriques', 'Mexique & Amérique Centrale'),
    'Costa Rica': ('ameriques', 'Mexique & Amérique Centrale'),
    'Guatemala': ('ameriques', 'Mexique & Amérique Centrale'),
    'Honduras': ('ameriques', 'Mexique & Amérique Centrale'),
    'Mexique': ('ameriques', 'Mexique & Amérique Centrale'),
    'Nicaragua': ('ameriques', 'Mexique & Amérique Centrale'),
    'Panama': ('ameriques', 'Mexique & Amérique Centrale'),
    'Argentine': ('ameriques', 'Amérique du Sud'),
    'Bolivie': ('ameriques', 'Amérique du Sud'),
    'Brésil': ('ameriques', 'Amérique du Sud'),
    'Chili': ('ameriques', 'Amérique du Sud'),
    'Colombie': ('ameriques', 'Amérique du Sud'),
    'Paraguay': ('ameriques', 'Amérique du Sud'),
    'Pérou': ('ameriques', 'Amérique du Sud'),
    'Uruguay': ('ameriques', 'Amérique du Sud'),
    'Équateur': ('ameriques', 'Amérique du Sud'),
    # OCÉANIE & OUTRE-MER
    'Australie': ('oceanie', 'Australie & Nouvelle-Zélande'),
    'Nouvelle-Zélande': ('oceanie', 'Australie & Nouvelle-Zélande'),
    'Fidji': ('oceanie', 'Pacifique & Outre-mer'),
    'Îles Cook': ('oceanie', 'Pacifique & Outre-mer'),
    'Nouvelle-Calédonie': ('oceanie', 'Pacifique & Outre-mer'),
    'Polynésie française': ('oceanie', 'Pacifique & Outre-mer'),
    'Samoa': ('oceanie', 'Pacifique & Outre-mer'),
    'Tonga': ('oceanie', 'Pacifique & Outre-mer'),
    'Vanuatu': ('oceanie', 'Pacifique & Outre-mer'),
    'Papouasie-Nouvelle-Guinée': ('oceanie', 'Pacifique & Outre-mer'),
}

# 6 mega-regions in order
MEGAS = [
    ('france',     1, {'fr': '<img src="flags/fr.png" width="20" height="15" alt="" style="vertical-align:middle;border-radius:2px"> France',
                       'en': '<img src="../flags/fr.png" width="20" height="15" alt="" style="vertical-align:middle;border-radius:2px"> France'}),
    ('europe',     2, {'fr': '🌊 Europe',                         'en': '🌊 Europe'}),
    ('afrique-mo', 3, {'fr': '🌍 Afrique & Moyen-Orient',        'en': '🌍 Africa & Middle East'}),
    ('asie',       4, {'fr': '🌏 Asie',                           'en': '🌏 Asia'}),
    ('ameriques',  5, {'fr': '🌎 Amériques',                      'en': '🌎 Americas'}),
    ('oceanie',    6, {'fr': '🦘 Océanie & Outre-mer',            'en': '🦘 Oceania & Overseas'}),
]

# Sub-region sort order within each mega
SUB_ORDER = {
    'France': 1,
    'Europe du Sud & Méditerranée': 1,
    'Europe du Nord & Centrale': 2,
    'Scandinavie & Baltique': 3,
    'Caucase & Asie Centrale': 4,
    'Afrique du Nord': 1,
    "Afrique de l'Ouest": 2,
    "Afrique de l'Est": 3,
    'Afrique australe': 4,
    'Océan Indien': 5,
    'Moyen-Orient': 6,
    'Macaronésie': 7,
    'Asie du Sud-Est': 1,
    "Asie de l'Est": 2,
    'Asie du Sud': 3,
    'Amérique du Nord': 1,
    'Caraïbes': 2,
    'Mexique & Amérique Centrale': 3,
    'Amérique du Sud': 4,
    'Australie & Nouvelle-Zélande': 1,
    'Pacifique & Outre-mer': 2,
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

.dh-acc{border:1.5px solid #e8e0d0;border-radius:14px;margin-bottom:10px;overflow:hidden;background:#fff}
.dh-acc-head{width:100%;display:flex;align-items:center;justify-content:space-between;padding:16px 18px;background:#fff;border:none;cursor:pointer;font-family:inherit;text-align:left;gap:12px}
.dh-acc-head:hover{background:#faf8f3}
.dh-acc-label{font-size:16px;font-weight:700;color:#1a1f2e}
.dh-acc-meta{display:flex;align-items:center;gap:10px;flex-shrink:0}
.dh-acc-count{font-size:12px;color:#7a8fa8;background:#f0ebe0;border-radius:20px;padding:2px 10px;font-weight:600}
.dh-acc-chev{font-size:14px;color:#9ca3af;transition:transform .25s}
.dh-acc.open>.dh-acc-head .dh-acc-chev{transform:rotate(180deg)}
.dh-acc-body{display:none;padding:0 18px 14px}
.dh-acc.open>.dh-acc-body{display:block}

.dh-sub{border:1px solid #f0ebe0;border-radius:10px;margin-bottom:8px;overflow:hidden;background:#faf8f3}
.dh-sub-head{width:100%;display:flex;align-items:center;justify-content:space-between;padding:12px 14px;background:#faf8f3;border:none;cursor:pointer;font-family:inherit;text-align:left;gap:10px}
.dh-sub-head:hover{background:#f5f0e5}
.dh-sub-label{font-size:13px;font-weight:700;color:#4a5568}
.dh-sub-count{font-size:11px;color:#9ca3af;font-weight:600}
.dh-sub-chev{font-size:12px;color:#bbb;transition:transform .25s}
.dh-sub.open>.dh-sub-head .dh-sub-chev{transform:rotate(180deg)}
.dh-sub-body{display:none;padding:6px 14px 12px}
.dh-sub.open>.dh-sub-body{display:block}

.dh-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(155px,1fr));gap:8px}
.dh-card{background:#fff;border-radius:10px;padding:10px 12px;text-decoration:none;border:1px solid #e8e0d0;display:flex;align-items:center;gap:9px;transition:border-color .15s,box-shadow .15s}
.dh-card:hover{border-color:#e8940a;box-shadow:0 2px 8px rgba(232,148,10,.12)}
.dh-card img{flex-shrink:0}
.dh-card-name{font-size:12px;font-weight:700;color:#1a1f2e;display:block;line-height:1.3}
.dh-card-sub{font-size:10px;color:#7a8fa8}
.dh-card.dh-hidden{display:none}
.dh-no-results{display:none;text-align:center;padding:32px 16px;color:#7a8fa8;font-size:14px}
.dh-no-results.show{display:block}

@media(max-width:640px){
 .dh-grid{grid-template-columns:repeat(2,1fr);gap:6px}
 .dh-card{padding:9px 10px}
 .dh-acc-head{padding:14px 14px}
 .dh-acc-label{font-size:15px}
 .dh-sub-head{padding:10px 12px}
 .dh-sub-body{padding:6px 6px 10px}
 .dh-acc-body{padding:10px 6px 14px}
}
"""

# ── JS ──
JS_FR = """
(function(){
 var inp=document.getElementById('dh-input'),
     clear=document.getElementById('dh-clear'),
     count=document.getElementById('dh-count'),
     cards=document.querySelectorAll('.dh-card'),
     accs=document.querySelectorAll('.dh-acc'),
     subs=document.querySelectorAll('.dh-sub'),
     noRes=document.getElementById('dh-no-results');

 function norm(s){return s.normalize('NFD').replace(/[\\u0300-\\u036f]/g,'').toLowerCase()}
 var searching=false;

 function doSearch(){
  var q=norm(inp.value.trim());
  clear.className='dh-search-clear'+(q?' show':'');
  if(!q){
   searching=false;
   cards.forEach(function(c){c.classList.remove('dh-hidden')});
   accs.forEach(function(a){a.classList.remove('open','dh-sm');a.style.display=''});
   subs.forEach(function(s){s.classList.remove('open','dh-sm');s.style.display=''});
   count.className='dh-count';noRes.className='dh-no-results';
   return;
  }
  searching=true;
  var n=0;
  cards.forEach(function(c){
   var t=norm(c.getAttribute('data-name')||'');
   var p=norm(c.getAttribute('data-country')||'');
   if(t.indexOf(q)>-1||p.indexOf(q)>-1){c.classList.remove('dh-hidden');n++}
   else{c.classList.add('dh-hidden')}
  });
  subs.forEach(function(s){
   var vis=s.querySelectorAll('.dh-card:not(.dh-hidden)');
   if(vis.length){s.classList.add('open','dh-sm');s.style.display=''}
   else{s.style.display='none'}
  });
  accs.forEach(function(a){
   var vis=a.querySelectorAll('.dh-card:not(.dh-hidden)');
   if(vis.length){a.classList.add('open','dh-sm');a.style.display=''}
   else{a.style.display='none'}
  });
  count.textContent=n+' '+(n>1?'destinations trouvées':'destination trouvée');
  count.className='dh-count show';
  noRes.className='dh-no-results'+(n===0?' show':'');
 }

 inp.addEventListener('input',doSearch);
 clear.addEventListener('click',function(){inp.value='';doSearch();inp.focus()});

 function toggleAcc(el,cls){
  el.addEventListener('click',function(){
   if(searching)return;
   var acc=el.parentElement;
   var wasOpen=acc.classList.contains('open');
   acc.classList.toggle('open');
   if(!wasOpen)setTimeout(function(){acc.scrollIntoView({behavior:'smooth',block:'start'})},80);
  });
 }
 document.querySelectorAll('.dh-acc-head').forEach(function(h){toggleAcc(h)});
 document.querySelectorAll('.dh-sub-head').forEach(function(h){toggleAcc(h)});
})();
"""

JS_EN = JS_FR.replace("'destinations trouvées':'destination trouvée'",
                       "'destinations found':'destination found'")


def make_card(slug, name, bare, flag, country, asset_prefix, page_prefix, is_fr):
    href = f'{page_prefix}meilleure-periode-{slug}.html' if is_fr else f'{page_prefix}best-time-to-visit-{slug}.html'
    sub = 'Quand partir' if is_fr else 'When to visit'
    return (
        f'<a href="{href}" target="_top" class="dh-card" '
        f'data-name="{html_mod.escape(bare)}" data-country="{html_mod.escape(country)}">'
        f'<img src="{asset_prefix}flags/{flag}.png" width="20" height="15" alt="{flag.upper()}" style="border-radius:2px">'
        f'<span><span class="dh-card-name">{html_mod.escape(name)}</span>'
        f'<span class="dh-card-sub">{sub}</span></span></a>')


def build_hub(destinations, is_fr=True):
    asset_prefix = '' if is_fr else '../'
    page_prefix = ''  # pages are always in same dir as hub
    lang = 'fr' if is_fr else 'en'

    # Group: mega → sub → [dests]
    megas = {}
    for d in destinations:
        slug = d['slug_fr']
        pays = d['pays']
        # Slug override takes priority (DOM-TOM, Canaries, Bermuda…)
        if slug in SLUG_OVERRIDE:
            mega_id, sub_name = SLUG_OVERRIDE[slug]
        elif pays not in MAPPING:
            print(f"  ⚠️  Pays sans mapping: {pays} ({d['nom_fr']})")
            continue
        else:
            mega_id, sub_name = MAPPING[pays]
        if mega_id not in megas:
            megas[mega_id] = {}
        if sub_name not in megas[mega_id]:
            megas[mega_id][sub_name] = []
        megas[mega_id][sub_name].append(d)

    L = []

    # Search bar
    ph = 'Rechercher une destination…' if is_fr else 'Search a destination…'
    L.append(f'<div class="dh-search"><span class="dh-search-icon">🔍</span>')
    L.append(f'<input type="text" id="dh-input" placeholder="{ph}" autocomplete="off">')
    L.append(f'<button id="dh-clear" class="dh-search-clear" aria-label="Clear">✕</button></div>')
    L.append(f'<div id="dh-count" class="dh-count"></div>')

    # 6 mega-accordions
    for mega_id, sort, labels in MEGAS:
        if mega_id not in megas:
            continue
        label = labels[lang]
        subs_data = megas[mega_id]
        cnt = sum(len(v) for v in subs_data.values())
        has_subs = len(subs_data) > 1

        L.append(f'<div class="dh-acc">')
        L.append(f'<button class="dh-acc-head" aria-expanded="false">')
        L.append(f'<span class="dh-acc-label">{label}</span>')
        L.append(f'<span class="dh-acc-meta"><span class="dh-acc-count">{cnt}</span>')
        L.append(f'<span class="dh-acc-chev">▾</span></span></button>')
        L.append(f'<div class="dh-acc-body">')

        sorted_subs = sorted(subs_data.items(), key=lambda x: SUB_ORDER.get(x[0], 99))

        if has_subs:
            for sub_name, dests in sorted_subs:
                sub_cnt = len(dests)
                L.append(f'<div class="dh-sub">')
                L.append(f'<button class="dh-sub-head">')
                L.append(f'<span class="dh-sub-label">{html_mod.escape(sub_name)}</span>')
                L.append(f'<span class="dh-acc-meta"><span class="dh-sub-count">{sub_cnt}</span>')
                L.append(f'<span class="dh-sub-chev">▾</span></span></button>')
                L.append(f'<div class="dh-sub-body"><div class="dh-grid">')
                for d in sorted(dests, key=lambda x: x['nom_bare']):
                    slug = d['slug_fr'] if is_fr else d['slug_en']
                    name = d['nom_fr'] if is_fr else d['nom_en']
                    L.append(make_card(slug, name, d['nom_bare'], d['flag'], d['pays'], asset_prefix, page_prefix, is_fr))
                L.append(f'</div></div></div>')
        else:
            # Single sub-region: no sub-accordion, just grid
            dests = list(subs_data.values())[0]
            L.append(f'<div class="dh-grid">')
            for d in sorted(dests, key=lambda x: x['nom_bare']):
                slug = d['slug_fr'] if is_fr else d['slug_en']
                name = d['nom_fr'] if is_fr else d['nom_en']
                L.append(make_card(slug, name, d['nom_bare'], d['flag'], d['pays'], asset_prefix, page_prefix, is_fr))
            L.append(f'</div>')

        L.append(f'</div></div>')

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
    content = re.sub(r'View destination guides \(\d+ destinations\)',
                     f'View destination guides ({total} destinations)', content)
    content = re.sub(r'Tableaux climatiques mensuels · \d+ destinations',
                     f'Tableaux climatiques mensuels · {total} destinations', content)
    content = re.sub(r'Monthly climate tables · \d+ destinations',
                     f'Monthly climate tables · {total} destinations', content)
    # Update guides shortcut counts
    content = re.sub(r'Guides destinations · \d+ fiches',
                     f'Guides destinations · {total} fiches', content)
    content = re.sub(r'Destination guides · \d+ cities',
                     f'Destination guides · {total} cities', content)

    # CSS is now in style.css — no injection needed

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

    start_marker = '<!-- SILO 1 : MEILLEURE PERIODE - dominant -->'
    end_marker = '\n <!-- SILO 2'
    start_idx = content.find(start_marker)
    end_idx = content.find(end_marker, start_idx)

    if start_idx == -1 or end_idx == -1:
        print(f"  ⚠️  SILO markers not found in {filepath}")
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
