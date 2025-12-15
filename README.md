# Python Outside-In Testing Strategy Example

An example of how to implement a diamond (integration test biased) testing strategy in Python with FastAPI, Celery, RabbitMQ, and Postgres.

## Overview

This repository demonstrates a complete Python microservice architecture with:

- **FastAPI**: Async HTTP API server
- **Celery**: Distributed task queue for background processing
- **RabbitMQ**: Message broker for Celery
- **Redis**: Result backend for Celery
- **PostgreSQL**: Database for persistence
- **pytest**: Testing framework with integration-first approach

## Diamond Testing Strategy

The "diamond" or "integration-biased" testing strategy focuses primarily on integration tests that verify the entire system working together, with fewer unit tests for critical business logic. This approach:

1. **Integration Tests** (tests/test_integration.py): Test the full workflow from API → Database → Background Tasks
2. **Unit Tests** (tests/test_tasks.py): Test isolated components like Celery tasks
3. **Minimal Mocking**: Only mock external dependencies when necessary

## Architecture

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   FastAPI   │─────▶│  PostgreSQL  │      │  RabbitMQ   │
│   Server    │      │   Database   │      │   Broker    │
└─────────────┘      └──────────────┘      └─────────────┘
       │                     ▲                      │
       │                     │                      │
       │                     │                      ▼
       └────────────────────────────────────▶┌─────────────┐
                  Triggers Task               │   Celery    │
                                             │   Worker    │
                                             └─────────────┘
```

### Workflow

1. Client sends POST request to create an item
2. FastAPI creates item in Postgres with status "pending"
3. FastAPI triggers Celery task to process the item
4. Celery worker picks up task from RabbitMQ
5. Worker updates item status to "processed" in Postgres

## Project Structure

```
.
├── app/
│   ├── __init__.py
│   ├── config.py          # Configuration management
│   ├── database.py        # SQLAlchemy models and database setup
│   ├── main.py           # FastAPI application
│   ├── schemas.py        # Pydantic models
│   └── tasks.py          # Celery tasks
├── tests/
│   ├── __init__.py
│   ├── conftest.py       # pytest fixtures
│   ├── test_integration.py  # Integration tests (diamond strategy)
│   └── test_tasks.py     # Unit tests for Celery tasks
├── docker-compose.yml    # Docker orchestration
├── Dockerfile           # Container image
├── Makefile            # Build and test automation
├── pyproject.toml      # Project configuration
├── requirements.txt    # Production dependencies
└── requirements-dev.txt # Development dependencies
```

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.12+ (for local development)
- Make (optional, for convenience)

### Running with Docker Compose

1. Start all services:
   ```bash
   make docker-up
   # or
   docker-compose up -d
   ```

2. The API will be available at http://localhost:8000
3. RabbitMQ management UI at http://localhost:15672 (guest/guest)

### API Usage

Create an item:
```bash
curl -X POST http://localhost:8000/items \
  -H "Content-Type: application/json" \
  -d '{"name": "My Item"}'
```

Get an item:
```bash
curl http://localhost:8000/items/1
```

List all items:
```bash
curl http://localhost:8000/items
```

Health check:
```bash
curl http://localhost:8000/health
```

### Local Development

1. Install dependencies:
   ```bash
   make dev-install
   # or
   pip install -r requirements-dev.txt
   ```

2. Start infrastructure services:
   ```bash
   docker-compose up -d postgres rabbitmq redis
   ```

3. Run the API server:
   ```bash
   make run-api
   # or
   uvicorn app.main:app --reload
   ```

4. Run the Celery worker (in another terminal):
   ```bash
   make run-worker
   # or
   celery -A app.tasks worker --loglevel=info
   ```

## Testing

### Run All Tests
```bash
make test
```

This will:
- Start Docker services (postgres, rabbitmq, redis)
- Run all tests
- Stop Docker services

### Run Unit Tests Only
```bash
make test-unit
```

Unit tests don't require Docker services.

### Run Integration Tests
```bash
make test-integration
```

### Test with Coverage
```bash
make test-cov
```

### Manual Testing
```bash
# Start services
make docker-up

# Run tests
pytest tests/ -v

# Stop services
make docker-down
```

## Code Quality

### Linting
```bash
make lint
```

### Formatting
```bash
make format
```

## Makefile Targets

- `make help` - Show available targets
- `make install` - Install production dependencies
- `make dev-install` - Install development dependencies
- `make clean` - Clean cache files
- `make lint` - Run linting
- `make format` - Format code
- `make test` - Run all tests
- `make test-unit` - Run unit tests
- `make test-integration` - Run integration tests
- `make test-cov` - Run tests with coverage
- `make docker-up` - Start Docker services
- `make docker-down` - Stop Docker services
- `make docker-logs` - Show Docker logs
- `make docker-clean` - Remove Docker volumes
- `make run-api` - Run API locally
- `make run-worker` - Run Celery worker locally

## Testing Philosophy

This project follows the **Diamond Testing Strategy**:

1. **Heavy on Integration Tests**: Most tests verify the full system behavior
2. **Light on Unit Tests**: Only critical business logic gets isolated unit tests
3. **Real Dependencies**: Use actual databases and services in tests when possible
4. **Fast Feedback**: Integration tests run quickly thanks to Docker Compose

### Benefits

- ✅ Catches integration issues early
- ✅ Tests represent real-world usage
- ✅ Less brittle than heavily mocked tests
- ✅ Faster to write and maintain
- ✅ Better confidence in deployments

### Trade-offs

- ❌ Slower than pure unit tests (mitigated by Docker)
- ❌ Requires infrastructure setup
- ❌ May miss some edge cases in business logic

## Environment Variables

See `.env.example` for available configuration options:

- `DATABASE_URL`: Async PostgreSQL connection string
- `DATABASE_URL_SYNC`: Sync PostgreSQL connection string (for Celery)
- `CELERY_BROKER_URL`: RabbitMQ broker URL
- `CELERY_RESULT_BACKEND`: Redis backend URL
- `API_HOST`: API server host
- `API_PORT`: API server port

## License

MIT License - see LICENSE file for details
