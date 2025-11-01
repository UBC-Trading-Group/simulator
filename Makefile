# Trading Simulator Backend - Docker Commands

.PHONY: help build up down logs shell test clean dev format

# Default target
help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Build commands
build: ## Build the Docker image
	docker-compose build

build-no-cache: ## Build the Docker image without cache
	docker-compose build --no-cache

# Development commands
up: ## Start all services
	docker-compose up -d

up-build: ## Build and start all services
	docker-compose up --build -d

down: ## Stop all services
	docker-compose down

logs: ## Show logs for all services
	docker-compose logs -f

logs-api: ## Show logs for API service only
	docker-compose logs -f api

logs-db: ## Show logs for database service only
	docker-compose logs -f db

# Database commands
db-shell: ## Connect to PostgreSQL database shell
	docker-compose exec db psql -U sim -d simdb

init-db: ## Initialize database with admin user
	docker-compose exec api uv run python scripts/init_db.py

db-reset: ## Reset the database (WARNING: This will delete all data)
	docker-compose down -v
	docker-compose up -d db
	@timeout 5 || true
	docker-compose exec api uv run alembic upgrade head

# Application commands
shell: ## Open a shell in the API container
	docker-compose exec api bash

migrate: ## Run database migrations
	docker-compose exec api uv run alembic upgrade head

migrate-create: ## Create a new migration (usage: make migrate-create MESSAGE="description")
	docker-compose exec api uv run alembic revision --autogenerate -m "$(MESSAGE)"

# Testing commands
test: ## Run tests
	docker-compose exec api uv run pytest

test-cov: ## Run tests with coverage
	docker-compose exec api uv run pytest --cov=app

# Formatting commands
format: ## Format code with isort and black
	cd backend && uv run isort .
	cd backend && uv run black .

# Utility commands
clean: ## Clean up Docker resources
	docker-compose down -v
	docker system prune -f

dev: ## Start development environment
	@echo "Starting development environment..."
	@echo "1. Building and starting services..."
	docker-compose up --build -d
	@echo "2. Waiting for services to be ready..."
	@timeout 10 || true
	@echo "3. Running database migrations..."
	docker-compose exec api uv run alembic upgrade head
	@echo "4. Development environment ready!"
	@echo "API available at: http://localhost:8000"
	@echo "API docs at: http://localhost:8000/api/docs"
	@echo "Database available at: localhost:5432"

# Status commands
status: ## Show status of all services
	docker-compose ps

# Restart commands
restart: ## Restart all services
	docker-compose restart

restart-api: ## Restart API service only
	docker-compose restart api
