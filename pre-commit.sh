#!/bin/sh
# Pre-commit hook: JS syntax check
# Install: cp pre-commit.sh .git/hooks/pre-commit && chmod +x .git/hooks/pre-commit

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
exit 0
