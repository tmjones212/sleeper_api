# Makefile for Fantasy Football Website
# Provides easy commands for building and updating the site

.PHONY: help build clean update-trades update-network update-matchups update-all dev deploy

# Default league ID (can be overridden with LEAGUE=xxx)
LEAGUE ?= 1181025001438806016

help:
	@echo "Fantasy Football Website Build System"
	@echo "===================================="
	@echo "Available commands:"
	@echo "  make build          - Build complete website from components"
	@echo "  make clean          - Remove generated files"
	@echo "  make update-trades  - Update only trade data (preserves grades)"
	@echo "  make update-network - Update network visualization"
	@echo "  make update-matchups- Update matchup data"
	@echo "  make update-all     - Update all dynamic data"
	@echo "  make dev            - Start development server"
	@echo "  make deploy         - Deploy to production"
	@echo ""
	@echo "Options:"
	@echo "  LEAGUE=xxx         - Specify league ID (default: $(LEAGUE))"
	@echo ""
	@echo "Examples:"
	@echo "  make build"
	@echo "  make update-trades LEAGUE=123456789"

build:
	@echo "Building website..."
	@python3 build/site_generator.py --build
	@echo "✓ Build complete! Open dist/index.html to view."

clean:
	@echo "Cleaning generated files..."
	@rm -f dist/index.html
	@rm -f dist/matchup_breakdowns.js
	@echo "✓ Clean complete"

update-trades:
	@echo "Updating trade data for league $(LEAGUE)..."
	@python3 update_scripts/update_trades.py --league $(LEAGUE)

update-network:
	@echo "Updating network data for league $(LEAGUE)..."
	@python3 update_scripts/update_network.py --league $(LEAGUE)

update-matchups:
	@echo "Updating matchup data for league $(LEAGUE)..."
	@python3 update_scripts/update_matchups.py --league $(LEAGUE)

update-all: update-trades update-network update-matchups
	@echo "✓ All updates complete"

dev:
	@echo "Starting development server..."
	@cd dist && python3 -m http.server 8000

deploy:
	@echo "Deploying to production..."
	@cp dist/index.html ../index.html
	@cp dist/matchup_breakdowns.js ../matchup_breakdowns.js 2>/dev/null || true
	@echo "✓ Deployed to parent directory"

# Quick commands
trades: update-trades
network: update-network
matchups: update-matchups