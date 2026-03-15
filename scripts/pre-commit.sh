#!/bin/sh
# Pre-commit hook: JS syntax check + auto-minification
# Install: cp scripts/pre-commit.sh .git/hooks/pre-commit && chmod +x .git/hooks/pre-commit

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

echo "🔍 Pre-commit: checking JS syntax..."

ERRORS=0
for f in js/core.js js/weather-banner-2.js js/fiche-slugs.js js/i18n-fr.js js/i18n-en.js js/i18n-en-us.js js/i18n-es.js js/i18n-de.js; do
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
JS_CHANGED=$(git diff --cached --name-only -- \
    js/core.js \
    js/weather-banner-2.js \
    js/fiche-slugs.js \
    js/i18n-fr.js js/i18n-en.js js/i18n-en-us.js js/i18n-es.js js/i18n-de.js)

if [ -n "$JS_CHANGED" ]; then
    echo "📦 Auto-minifying changed JS files..."
    echo "$JS_CHANGED" | while read f; do
        src="$f"
        min="${f%.js}.min.js"
        if [ -f "$src" ] && [ "$src" != "$min" ]; then
            npx terser "$src" -c -m -o "$min" 2>/dev/null && \
                git add "$min" && \
                echo "  ✓ $src → $min"
        fi
    done
    echo "${GREEN}✅ Minified JS added to commit${NC}"
fi

# Validate locale consistency
echo "🌐 Checking locale consistency..."
python3 scripts/check_locale.py > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "${RED}❌ Locale inconsistency detected — run: python3 scripts/check_locale.py${NC}"
    exit 1
fi
echo "${GREEN}✅ Locales OK${NC}"

exit 0
