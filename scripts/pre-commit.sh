#!/bin/sh
# Pre-commit hook: JS syntax check + auto-minification

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

echo "🔍 Pre-commit: checking JS syntax..."

ERRORS=0
for f in js/core.js js/i18n-fr.js js/i18n-en.js; do
    if [ -f "$f" ]; then
        node --check "$f" 2>/dev/null
        if [ $? -ne 0 ]; then
            echo "${RED}❌ SyntaxError in $f${NC}"
            ERRORS=1
        fi
    fi
done

if [ $ERRORS -eq 1 ]; then
    echo "${RED}❌ Commit blocked: fix JS syntax errors first${NC}"
    exit 1
fi

echo "${GREEN}✅ JS syntax OK${NC}"

# Auto-minify if any JS source changed
JS_CHANGED=$(git diff --cached --name-only -- js/core.js js/i18n-fr.js js/i18n-en.js)
if [ -n "$JS_CHANGED" ]; then
    echo "📦 Auto-minifying JS..."
    npx terser js/core.js -c -m -o js/core.min.js 2>/dev/null
    npx terser js/i18n-fr.js -c -m -o js/i18n-fr.min.js 2>/dev/null
    npx terser js/i18n-en.js -c -m -o js/i18n-en.min.js 2>/dev/null
    git add js/core.min.js js/i18n-fr.min.js js/i18n-en.min.js
    echo "${GREEN}✅ Minified JS added to commit${NC}"
fi

exit 0
