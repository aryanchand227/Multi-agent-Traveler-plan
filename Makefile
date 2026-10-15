.PHONY: help install backend frontend db migrate test docker-up docker-down clean

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# --- Installation ---

install: ## Install all dependencies
	@$(MAKE) install-backend
	@$(MAKE) install-frontend

install-backend: ## Install backend dependencies
	cd backend && pip install -e ".[dev]"

install-frontend: ## Install frontend dependencies
	cd frontend && npm install

# --- Development ---

backend: ## Run backend dev server
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

frontend: ## Run frontend dev server
	cd frontend && npm run dev

# --- Database ---

db-migrate: ## Run database migrations
	cd backend && alembic upgrade head

db-revision: ## Create new migration (usage: make db-revision MSG="description")
	cd backend && alembic revision --autogenerate -m "$(MSG)"

db-downgrade: ## Downgrade database by one revision
	cd backend && alembic downgrade -1

# --- Testing ---

test: ## Run all tests
	cd backend && python -m pytest tests/ -v

test-cov: ## Run tests with coverage
	cd backend && python -m pytest tests/ -v --cov=app --cov-report=html

# --- Docker ---

docker-up: ## Start all services with Docker
	docker compose up -d --build

docker-down: ## Stop all Docker services
	docker compose down

docker-logs: ## View Docker logs
	docker compose logs -f

# --- Cleanup ---

clean: ## Clean generated files
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	rm -rf backend/htmlcov backend/.coverage
	rm -rf frontend/.next frontend/node_modules
