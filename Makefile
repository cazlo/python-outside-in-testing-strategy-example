.PHONY: help
help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

##@ Development

.PHONY: install
install: ## Install Python dependencies using uv
	uv sync

.PHONY: run
run: deps-up ## Run the FastAPI server locally
	uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

.PHONY: run-debug
run-debug: deps-up ## Run the FastAPI server in debug mode
	uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --log-level debug

##@ Testing

# Three distinct test runtime contexts:
# 1. test-unit: Local unit tests with coverage (uv pytest + local dependencies)
# 2. test-integration: Full integration in Docker Compose (all services containerized, no coverage)
# 3. test-local-integration: Dependencies in Docker, API/worker local for debugging

.PHONY: test-unit
test-unit: deps-up ## Run unit tests locally with coverage (pytest on host, deps in Docker)
	@echo "Running unit tests with line and branch coverage..."
	cd src && uv run pytest -v \
	    -m "unit" \
		--cov=app \
		--cov-branch \
		--cov-report=html \
		--cov-report=term-missing \
		--cov-report=term:skip-covered

.PHONY: test-integration
test-integration: ## Run integration tests in Docker Compose (all services containerized, no coverage)
	@echo "Running integration tests in Docker Compose..."
	docker compose -f docker-compose.test.yml up --build --abort-on-container-exit --exit-code-from tests
	docker compose -f docker-compose.test.yml down

.PHONY: test-local-integration
test-local-integration: deps-up wait-for-health ## Run integration tests against locally running API (for debugging)
	@echo "Dependencies are running. Start your API/worker locally in debug mode, then run:"
	@echo "  cd src && BASE_URL=http://localhost:8000 uv run pytest test/ -v -m integration"
	@echo ""
	@echo "Or use this target to run tests automatically:"
	$(MAKE) _run-local-integration-tests

.PHONY: _run-local-integration-tests
_run-local-integration-tests: ## Internal: Run integration tests against local API
	@echo "Waiting for API to be healthy at http://localhost:8000..."
	@timeout 30s sh -c 'until curl -sf http://localhost:8000/health > /dev/null; do sleep 1; done' || \
		(echo "ERROR: API not healthy after 30s. Start the API with 'make run' in another terminal." && exit 1)
	cd src && BASE_URL=http://localhost:8000 uv run pytest test/ -v -m integration

.PHONY: wait-for-health
wait-for-health: ## Wait for local dependencies to be healthy
	@echo "Waiting for PostgreSQL..."
	@timeout 30s sh -c 'until docker compose exec -T database pg_isready -U $${DATABASE_USER:-user} > /dev/null 2>&1; do sleep 1; done' || \
		(echo "ERROR: PostgreSQL not ready" && exit 1)
	@echo "Waiting for RabbitMQ..."
	@timeout 30s sh -c 'until docker compose exec -T rabbitmq rabbitmq-diagnostics check_port_connectivity > /dev/null 2>&1; do sleep 1; done' || \
		(echo "ERROR: RabbitMQ not ready" && exit 1)
	@echo "✓ All dependencies healthy"

.PHONY: test
test: test-unit ## Default: Run unit tests (alias for test-unit)

.PHONY: ci-test
ci-test: fmt lint test-unit test-integration ## Run all checks and tests (CI-compatible)

##@ Docker Compose Workflows

.PHONY: deps-up
deps-up: ## Start dependency services (database, redis, rabbitmq) in Docker Compose
	docker compose up -d database rabbitmq

.PHONY: deps-down
deps-down: ## Stop dependency services
	docker compose down

.PHONY: compose-up-dev
compose-up-dev: ## Start all services in Docker Compose (dev profile)
	docker compose --profile dev up --build

.PHONY: compose-up-prod
compose-up-prod: ## Start all services in Docker Compose (prod profile)
	docker compose --profile prod up --build

.PHONY: compose-down
compose-down: ## Stop all Docker Compose services
	docker compose down

##@ Docker Image Management

.PHONY: docker-build-dev
docker-build-dev: ## Build the dev/test Docker image
	docker build --target test -t python-outside-in:dev .

.PHONY: docker-build-prod
docker-build-prod: ## Build the production Docker image
	docker build --target runtime -t python-outside-in:prod .

.PHONY: docker-build-all
docker-build-all: docker-build-dev docker-build-prod ## Build all Docker images

##@ Code Quality

.PHONY: fmt
fmt: ## Format Python code with ruff
	uv run ruff format .

.PHONY: lint
lint: ## Run ruff and mypy linters
	uv run ruff check .
	cd src && uv run mypy app/

.PHONY: lint-fix
lint-fix: ## Run ruff with autofix mode
	uv run ruff check --fix .

##@ Database Management

.PHONY: db-migrate
db-migrate: deps-up ## Run database migrations
	cd src && uv run alembic upgrade head

.PHONY: db-revision
db-revision: ## Create a new database migration (requires MESSAGE="migration message")
	cd src && uv run alembic revision --autogenerate -m "$(MESSAGE)"

.PHONY: db-downgrade
db-downgrade: ## Downgrade database by one revision
	cd src && uv run alembic downgrade -1

##@ CI-Compatible Workflows

.PHONY: ci-build
ci-build: docker-build-all ## Build all artifacts (CI-compatible)

.PHONY: ci-full
ci-full: ci-test ci-build ## Run complete CI pipeline locally

##@ Cleanup

.PHONY: clean
clean: ## Clean build artifacts and containers
	rm -rf .pytest_cache/ htmlcov/ .coverage .mypy_cache/ .ruff_cache/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	docker compose down -v

.PHONY: clean-all
clean-all: clean ## Clean everything including Docker images
	docker rmi python-outside-in:dev python-outside-in:prod 2>/dev/null || true

##@ Common Workflows

.PHONY: local-dev
local-dev: deps-up run ## Start local dev environment (dependencies + local server)

