.PHONY: help run test lint format migrate seed clean setup

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-18s\033[0m %s\n", $$1, $$2}'

# ── Development ──────────────────────────────────────────────

setup: ## First-time project setup (venv, deps, db)
	python -m venv venv
	. venv/bin/activate && pip install -r requirements.txt -r requirements-dev.txt
	. venv/bin/activate && pre-commit install
	$(MAKE) migrate
	@echo "\n✓ Setup complete. Activate with: source venv/bin/activate"

run: ## Run development server
	FLASK_CONFIG=development python run.py

test: ## Run test suite with pytest
	FLASK_CONFIG=testing python -m pytest tests/ -v --tb=short

test-cov: ## Run tests with coverage report
	FLASK_CONFIG=testing python -m pytest tests/ -v --tb=short --cov=app --cov-report=term-missing

# ── Code Quality ─────────────────────────────────────────────

lint: ## Run linters (flake8, isort --check, black --check)
	python -m flake8 app/ tests/ run.py config.py
	python -m isort --check-only app/ tests/ run.py config.py
	python -m black --check app/ tests/ run.py config.py

format: ## Auto-format code (black + isort)
	python -m isort app/ tests/ run.py config.py
	python -m black app/ tests/ run.py config.py

# ── Database ─────────────────────────────────────────────────

migrate: ## Run database migrations (upgrade to latest)
	flask db upgrade

migration: ## Generate a new migration from model changes
	flask db migrate -m "$(msg)"

seed: ## Seed the database with glossary data
	python scripts/seed_db.py

db-reset: ## Drop all tables and re-run migrations + seed
	flask db downgrade base
	flask db upgrade
	$(MAKE) seed

# ── Production ───────────────────────────────────────────────

prod: ## Run production server (gunicorn)
	gunicorn run:app --bind 0.0.0.0:$${PORT:-10000}

# ── Cleanup ──────────────────────────────────────────────────

clean: ## Remove caches, bytecode, and build artifacts
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name '*.pyc' -delete 2>/dev/null || true
	rm -rf .pytest_cache htmlcov .coverage
