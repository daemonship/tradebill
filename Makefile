.PHONY: help install-backend install-frontend install dev dev-backend dev-frontend test lint format

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: install-backend install-frontend ## Install all dependencies

install-backend: ## Install backend Python dependencies
	python -m pip install --upgrade pip
	pip install -e .[dev]

install-frontend: ## Install frontend Node dependencies
	cd frontend && npm ci

dev: ## Start all development services
	docker-compose up

dev-backend: ## Start backend only
	uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend: ## Start frontend only
	cd frontend && npm run dev

test: test-backend test-frontend ## Run all tests

test-backend: ## Run backend tests
	cd backend && python -m pytest -v

test-frontend: ## Run frontend tests
	cd frontend && npm test

lint: lint-backend lint-frontend ## Run all linters

lint-backend: ## Lint backend code
	ruff check backend/
	black --check backend/
	mypy backend/

lint-frontend: ## Lint frontend code
	cd frontend && npm run lint

format: ## Format backend code
	black backend/
	ruff check --fix backend/

db-upgrade: ## Run database migrations
	cd backend && alembic upgrade head

db-downgrade: ## Downgrade database migrations
	cd backend && alembic downgrade -1

db-migration: ## Create a new migration (use NAME=name)
	cd backend && alembic revision --autogenerate -m $(NAME)
