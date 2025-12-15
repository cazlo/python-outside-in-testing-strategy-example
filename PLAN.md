# Refactor Plan: Simple Async Job API

This plan outlines the steps to refactor the current complex application into a simple Async Job API, adhering to the "Outside-In Testing Strategy".

## Objective
Reduce the codebase to a minimal example demonstrating the testing strategy using Python, FastAPI, and Celery. Remove authentication, authorization, pagination, and unrelated domains (Users, Roles, Media).

## Phase 1: Documentation & Configuration

- [x] **Update Copilot Instructions**
    - Edit `.github/copilot-instructions.md`.
    - Replace Go-specific references (`go test`, `Makefile` targets) with Python equivalents (`pytest`, `uv`).
    - Maintain the core philosophy (Outside-In, HTTP-first testing).
- [ ] **Rewrite Makefile**
    - Replace Go targets with Python targets.
    - `make test` -> `uv run pytest`.
    - `make run` -> `uv run fastapi run`.
    - `make deps-up` -> `docker compose up -d`.
- [x] **Clean Dependencies**
    - Edit `app/pyproject.toml`.
    - Remove: `bcrypt`, `fastapi-pagination`, `minio`, `Pillow`, `pandas`, `openpyxl`, `pyjwt`, `fastapi-limiter`.
    - Keep: `fastapi`, `celery`, `sqlmodel`, `alembic`, `asyncpg`

## Phase 2: Code Removal (The Great Purge)

- [x] **Remove Authentication & Authorization**
    - Delete `app/core/security.py`, `app/core/authz.py`.
    - Remove `app/api/v1/endpoints/auth.py`.
    - Remove `app/api/deps.py` (or strip it down to DB deps only).
    - Remove `app/utils/token.py`.
- [x] **Remove User & Role Domain**
    - Delete `app/models/user_model.py`, `app/models/role_model.py`.
    - Delete `app/schemas/user_schema.py`, `app/schemas/role_schema.py`, `app/schemas/token_schema.py`.
    - Delete `app/crud/user_crud.py`, `app/crud/role_crud.py`.
- [x] **Remove Media & Files Domain**
    - Delete `app/models/image_media_model.py`, `app/models/media_model.py`.
    - Delete `app/schemas/image_media_schema.py`, `app/schemas/media_schema.py`.
    - Delete `app/crud/image_media_crud.py`.
    - Delete `app/utils/file_repository/`.
    - Delete `app/utils/resize_image.py`.
- [x] **Simplify Core & Utils**
    - Clean up `app/main.py` (remove auth middleware, pagination add-ons).
    - Clean up `app/initial_data.py` (remove user seeding).

## Phase 3: Database Reset

- [x] **Reset Migrations**
    - Delete all files in `app/alembic/versions/`.
    - Ensure `app/models/__init__.py` only imports `AsyncJob` (and maybe `Base`).
- [x] **Create New Migration**
    - Run `alembic revision --autogenerate -m "init_async_job"` to create a clean slate migration.
    - Note: Since we have no database models (async jobs use Celery without DB persistence), no migration is needed.

## Phase 4: Test Refactoring

- [x] **Clean Test Suite**
    - Delete `test/api/test_login.py`, `test/api/test_user.py`.
    - Delete `test/api/test_cache.py` (if not needed).
- [x] **Update Fixtures**
    - Edit `test/conftest.py`.
    - Remove `client_authenticated`, `user_token_headers`, etc.
    - Ensure `client` fixture works without auth.
- [x] **Update Async Job Tests**
    - Edit `test/api/test_async_job.py`.
    - Remove any auth headers from requests.
    - Ensure tests pass with the simplified API.
- [x] **Remove unneeded dependencies** in the docker-compose yaml (minio, etc.)
- [x] **Setup 2 different docker-compose yamls**
    - Created `docker-compose.dev.yml` for unit tests with coverage
    - Created `docker-compose.test.yml` for prod image testing
    - Tests auto-adapt to these contexts via environment variables

## Phase 5: Verification

- [x] **Run Tests**
    - Execute `make test` (or `pytest`).
    - Verify all tests pass.
- [x] **Manual Check**
    - Added `/health` endpoint for container orchestration
    - OpenAPI docs accessible at `/docs` (only Job endpoints exist)

## Phase 6: Final Polish & CI

- [ ] **Update Copilot Instructions (Again)**
    - Added Celery testing strategy section
    - Reflected learnings about dual docker-compose approach
- [ ] **Document Celery Integration Testing**
    - Added comprehensive Celery testing section to `docs/testing-strategy.md`
    - Explained `celery_config` fixture pattern
    - Documented eager mode vs real workers trade-offs
- [ ] **Update GitHub CI**
    - Updated `.github/workflows/ci.yml` to use `uv`, Python 3.13, and new Makefile targets
    - Updated `.github/workflows/deploy.yml` to use Python-based deployment
    - Removed Go-specific steps and replaced with Python equivalents
