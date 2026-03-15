#!/bin/sh
# Regenerate minified JS files from sources
# Run after editing any JS source file

set -e
cd "$(dirname "$0")/.."

echo "Minifying JS files..."

npx terser js/core.js              -c -m -o js/core.min.js
npx terser js/weather-banner-2.js  -c -m -o js/weather-banner-2.min.js
npx terser js/fiche-slugs.js       -c -m -o js/fiche-slugs.min.js
npx terser js/i18n-fr.js           -c -m -o js/i18n-fr.min.js
npx terser js/i18n-en.js           -c -m -o js/i18n-en.min.js
npx terser js/i18n-en-us.js        -c -m -o js/i18n-en-us.min.js
npx terser js/i18n-es.js           -c -m -o js/i18n-es.min.js
npx terser js/i18n-de.js           -c -m -o js/i18n-de.min.js

echo "Done:"
for f in core weather-banner-2 fiche-slugs; do
    src="js/${f}.js"
    min="js/${f}.min.js"
    [ -f "$src" ] && [ -f "$min" ] && printf "  %-28s → %s\n" "$src" "$min"
done
