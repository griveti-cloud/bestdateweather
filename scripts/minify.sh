#!/bin/sh
# Regenerate minified JS files from sources
# Run after editing js/core.js, js/i18n-fr.js, or js/i18n-en.js

set -e
cd "$(dirname "$0")/.."

echo "Minifying JS files..."
npx terser js/core.js -c -m -o js/core.min.js
npx terser js/i18n-fr.js -c -m -o js/i18n-fr.min.js
npx terser js/i18n-en.js -c -m -o js/i18n-en.min.js

echo "Done:"
ls -lh js/core.js js/core.min.js js/i18n-fr.js js/i18n-fr.min.js js/i18n-en.js js/i18n-en.min.js | awk '{print $5, $NF}'
