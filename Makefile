.PHONY: help install dev-install clean lint format test test-unit test-integration docker-up docker-down docker-logs

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install production dependencies
	pip install -r requirements.txt

dev-install: ## Install development dependencies
	pip install -r requirements-dev.txt

clean: ## Clean up cache files and artifacts
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete

lint: ## Run linting checks
	ruff check app/ tests/

format: ## Format code with ruff
	ruff format app/ tests/

test: docker-up ## Run all tests (requires Docker services)
	pytest tests/ -v --tb=short
	$(MAKE) docker-down

test-unit: ## Run unit tests only (no Docker required)
	pytest tests/test_tasks.py -v --tb=short

test-integration: docker-up ## Run integration tests (requires Docker services)
	pytest tests/test_integration.py -v --tb=short
	$(MAKE) docker-down

test-cov: docker-up ## Run tests with coverage
	pytest tests/ -v --cov=app --cov-report=term-missing --cov-report=html
	$(MAKE) docker-down

docker-up: ## Start all Docker services
	docker-compose up -d
	@echo "Waiting for services to be ready..."
	@sleep 10

docker-down: ## Stop all Docker services
	docker-compose down

docker-logs: ## Show logs from Docker services
	docker-compose logs -f

docker-clean: ## Remove Docker volumes and containers
	docker-compose down -v

run-api: ## Run the API locally (requires services from docker-compose)
	uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

run-worker: ## Run the Celery worker locally (requires services from docker-compose)
	celery -A app.tasks worker --loglevel=info
