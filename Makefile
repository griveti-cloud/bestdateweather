# ═══════════════════════════════════════════════════
# BestDateWeather — Build Pipeline
# ═══════════════════════════════════════════════════
#
# Usage:
#   make all         — Full rebuild toutes langues
#   make pages       — Pages destinations (FR+EN+ES+DE+US, annual+monthly)
#   make pillar      — Pages piliers
#   make comparisons — Pages comparatifs
#   make rankings    — Pages classements
#   make sitemap     — Sitemaps 5 langues
#   make test        — Tests scoring
#   make check-loc   — Validation cohérence locales
#   make deploy      — Commit + push (Netlify auto-deploy on push)
#
# Prerequisites: Python 3.8+, node (terser, eslint)

.PHONY: all pages pillar comparisons rankings sitemap slugs test check-loc deploy climate scores

# ── Full rebuild ──────────────────────────────────────
all: pages pillar comparisons rankings sitemap
	@echo ""
	@echo "✅ Full build complete"
	@echo "   Run 'make test' to validate scoring consistency"
	@echo "   Run 'make deploy' to push to production"

# ── Destination pages (toutes langues) ───────────────
pages:
	@echo "🌍 Generating destination pages (×5 langues)..."
	python3 generate_pages.py --lang fr
	python3 generate_pages.py --lang en
	python3 generate_pages.py --lang en-us
	python3 generate_pages.py --lang es
	python3 generate_pages.py --lang de

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

# ── Sitemaps ──────────────────────────────────────────
sitemap:
	@echo "🗺️  Generating sitemaps..."
	python3 generate_sitemaps.py

# ── Autocomplete slugs ────────────────────────────────
slugs:
	@echo "🔤 Regenerating fiche-slugs.js..."
	python3 generate_fiche_slugs.py

# ── Données ───────────────────────────────────────────
climate:
	@echo "🌡️  Fetching fresh climate data..."
	python3 scripts/fetch_climate.py

# ── Testing ───────────────────────────────────────────
test:
	@echo "🧪 Running scoring consistency tests..."
	python3 tests/test_scoring.py

check-loc:
	@echo "🌐 Checking locale consistency..."
	python3 scripts/check_locale.py

# ── Deploy ────────────────────────────────────────────
deploy: check-loc
	git add -A
	git status --short
	@echo ""
	@read -p "Commit message: " msg; git commit -m "$$msg"
	git push

# ── Utilities ─────────────────────────────────────────
minify:
	@echo "📦 Minifying all JS sources..."
	sh scripts/minify.sh

scores:
	@echo "⚠️  regenerate_scores.py est dans scripts/archive/ — usage rare"
	python3 scripts/archive/regenerate_scores.py
