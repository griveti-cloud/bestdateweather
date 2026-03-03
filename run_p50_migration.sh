#!/bin/bash
set -e
echo "=== STEP 1/3: Re-fetch climate.csv (P50) ==="
python3 fetch_climate.py --all
echo ""
echo "=== STEP 2/3: Regenerate fiche scores ==="
python3 regenerate_scores.py
echo ""
echo "=== STEP 3/3: Regenerate classements ==="
python3 generate_classements.py
echo ""
echo "=== DONE - commit ==="
git add -A
git commit -m "data: re-fetch all climate with P50 median + regenerate scores/classements"
echo "Run: git push origin main"
