# ═══════════════════════════════════════════════════
# BestDateWeather — Build Pipeline
# ═══════════════════════════════════════════════════
#
# Usage:
#   make all         — Full rebuild (destinations + pillar + comparison + ranking pages)
#   make destinations — Destination pages only (FR + EN, annual + monthly)
#   make pillar      — Pillar pages only
#   make comparisons — Comparison pages only
#   make rankings    — Ranking pages only
#   make test        — Run scoring consistency tests
#   make deploy      — Commit and push to Vercel
#   make check       — Dry-run validation (no file writes)
#
# Prerequisites: Python 3.8+, node (for JS syntax check)

.PHONY: all destinations fr en pillar comparisons rankings test deploy check clean

# ── Full rebuild ──────────────────────────────────────
all: destinations pillar comparisons rankings
	@echo ""
	@echo "✅ Full build complete"
	@echo "   Run 'make test' to validate scoring consistency"
	@echo "   Run 'make deploy' to push to production"

# ── Destination pages ─────────────────────────────────
destinations: fr en

fr:
	@echo "🇫🇷 Generating FR destination pages..."
	python3 generate_all.py

en:
	@echo "🇬🇧 Generating EN destination pages..."
	python3 generate_all_en.py

# ── Content pages ─────────────────────────────────────
pillar:
	@echo "📄 Generating pillar pages..."
	python3 generate_piliers.py

comparisons:
	@echo "🔀 Generating comparison pages..."
	python3 generate_comparatifs.py

rankings:
	@echo "🏆 Generating ranking pages..."
	python3 generate_classements.py

# ── Testing ───────────────────────────────────────────
test:
	@echo "🧪 Running scoring consistency tests..."
	python3 tests/test_scoring.py

check:
	@echo "🔍 Dry-run validation (no writes)..."
	python3 generate_all.py --dry-run
	python3 generate_all_en.py --dry-run

# ── Deploy ────────────────────────────────────────────
deploy:
	git add -A
	git status --short
	@echo ""
	@read -p "Commit message: " msg; git commit -m "$$msg"
	git push

# ── Utilities ─────────────────────────────────────────
fiche-scores:
	@echo "📊 Regenerating FICHE_SCORES in core.js..."
	python3 scripts/build_fiche_scores.py

climate:
	@echo "🌡️  Fetching fresh climate data..."
	python3 fetch_climate.py

scores:
	@echo "🔢 Regenerating scores in existing pages..."
	python3 regenerate_scores.py
