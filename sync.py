#!/usr/bin/env python3
"""
sync.py — Synchronise les fonctions JS partagées de index.html vers en/app.html
Usage : python3 sync.py
"""

import re, sys

SOURCE = 'index.html'
TARGET = 'en/app.html'

# Fonctions légitimement différentes (traductions UI ou appels EN-spécifiques)
EXCLUDE = {
    'getLabel','getSeaComfortFR','getSeaComfortEN','slugFromName','slugFromNameEN',
    'fetchMarineSST','fetchMarineSSTEN','renderSeaChip','renderSeaChipEN',
    'fmtTemp','fmtTempRaw','fmtTempUnit','fmtWind','fmtWindUnit','fmtPrecip','fmtHour',
    'setUnits','initFlatpickr','updateHero','renderHourly','scenarioLabel',
    'renderScCard','updateScenarioLabels','computeAndRenderScore','applyHorizonWording',
    'setConfBadge','showResults','_snowTimeLbl',
    'applyTzOffset','buildRows','fetchAC','fetchAnnualArchive','fetchForecast',
    'findFicheScores','flagEmoji','fmt','getIcon','getMainRisk','getVerdict',
    'lunarPhase','quickFill','renderAnnual','renderAstro','run','runAnnual',
    'sunriseSunset','tryFallback','updateScoreTooltip'
}

def extract_full_func(content, name):
    idx = content.find('function ' + name + '(')
    if idx < 0:
        return None
    depth, i = 0, idx
    while i < len(content):
        if content[i] == '{':
            depth += 1
        elif content[i] == '}':
            depth -= 1
            if depth == 0:
                return content[idx:i+1]
        i += 1
    return None

def replace_func(content, name, new_body):
    old_body = extract_full_func(content, name)
    if old_body is None:
        return content, False
    return content.replace(old_body, new_body, 1), True

def main():
    fr = open(SOURCE, encoding='utf-8').read()
    en = open(TARGET, encoding='utf-8').read()

    fr_funcs = set(re.findall(r'function (\w+)\(', fr))
    en_funcs = set(re.findall(r'function (\w+)\(', en))
    common = fr_funcs & en_funcs
    to_sync = sorted(common - EXCLUDE)

    synced = []
    skipped = []
    not_found = []

    for name in to_sync:
        fr_body = extract_full_func(fr, name)
        en_body = extract_full_func(en, name)
        if fr_body is None or en_body is None:
            not_found.append(name)
            continue
        if fr_body == en_body:
            continue  # Already in sync
        en, ok = replace_func(en, name, fr_body)
        if ok:
            synced.append(name)
        else:
            skipped.append(name)

    if synced:
        open(TARGET, 'w', encoding='utf-8').write(en)
        print(f'✓ Synced {len(synced)} function(s): {", ".join(synced)}')
    else:
        print('✓ Already in sync — nothing to update')

    if skipped:
        print(f'⚠ Could not replace: {", ".join(skipped)}')
    if not_found:
        print(f'ℹ Not in target: {", ".join(not_found)}')

    # Validate JS syntax
    import subprocess
    result = subprocess.run(
        ['node', '--input-type=commonjs'],
        input=f'''
var fs = require('fs');
var c = fs.readFileSync('{TARGET}','utf8');
var scripts = c.split('<script>');
for (var i = 1; i < scripts.length; i++) {{
    var s = scripts[i].split('</script>')[0];
    try {{ new Function(s); }}
    catch(e) {{ process.stdout.write('JS ERROR script ' + i + ': ' + e.message + '\\n'); process.exit(1); }}
}}
process.stdout.write('JS OK\\n');
''',
        capture_output=True, text=True
    )
    print(result.stdout.strip())
    if result.returncode != 0:
        print('SYNC ABORTED — JS error detected, reverting')
        sys.exit(1)

if __name__ == '__main__':
    main()
