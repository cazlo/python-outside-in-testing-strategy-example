# Outside-In Testing Strategy

This repository prioritizes **outside-in tests**:
- Tests exercise the service **via its public HTTP interface**
- Dependencies are treated as **black boxes**
- Tests interact with the service the same way real clients do

This strategy aligns with the **Testing Diamond** philosophy (as opposed to the traditional Testing Pyramid).
We prioritize integration and outside-in tests over granular unit tests to maximize confidence in the system's behavior.

| Layer | Emphasis | Role |
|-----|---------|---|
| **Outside-in / Black-box** | **High** | Validates contracts and critical paths (The "Top") |
| **Integration** | **High** | Validates component interactions (The "Fat Middle") |
| **Unit** | Targeted | Validates specific algorithms and logic (The "Base") |

By focusing on the "fat middle" of integration and outside-in tests, we ensure that tests act as **living documentation** of the system's behavior, rather than just verifying implementation details.

The goal is to **validate stable interfaces first**, not internal
implementation details.

---

## Test Reuse Across Environments

The same outside-in tests can run against:

- An in-process server (`httptest`)
- A locally running binary (ideal for debugging)
- Docker Compose (mocked dependencies)
- Kubernetes (real dependencies)

This is achieved by:
- Driving tests purely via HTTP
- Using environment variables (e.g. `BASE_URL`) to switch targets
- Avoiding direct imports of application internals in integration tests

---

## Outside-In Testing Philosophy

### Why Outside-In?

Outside-in tests:
- Validate the **most stable contracts** (HTTP APIs, schemas, auth behavior)
- Fail when user-visible behavior changes
- Continue to work as internal implementations evolve

As features are added, these tests tend to **break less often** than
implementation-level tests.

---

### Unit Tests Still Matter (But Differently)

This approach does **not** eliminate unit testing.

Instead:
- Unit tests are used **surgically**
- Primarily to:
    - Reach coverage targets
    - Exercise edge cases that are difficult to trigger via HTTP
    - Validate complex logic in isolation

Outside-in tests remain the primary correctness signal.

---

### DTO and Model Handling in Integration Tests

Integration and outside-in tests intentionally:
- **Do not import application DTOs or model classes**
- Parse JSON and validate responses manually

This is intentional.

Benefits:
- Detects drift between models and actual API contracts
- Catches serialization, tagging, and schema mismatches
- Prevents false confidence caused by shared types

---

## Benefits of This Approach

- High confidence in user-visible behavior
- Excellent test reuse across environments
- Strong alignment with production behavior
- Debug-friendly local workflows
- Resistant to internal refactors

---

## Trade-Offs and Risks

- Test setup can become complex
- Slower feedback than pure unit tests
- Requires discipline around environment configuration
- Poorly designed outside-in tests can become overly broad

This approach works best when:
- Service boundaries are well defined
- Configuration is explicit
- Teams value contract stability

---

## Extensibility Beyond HTTP

While this repository demonstrates the pattern using an HTTP service, the **outside-in** strategy is equally applicable to:
- **Queue Workers**: Treat the message broker as the interface. Publish a message and assert on the side effects (DB changes, downstream messages).
- **gRPC Services**: Use a gRPC client to drive the tests.
- **Event-Driven Microservices**: Validate the consumption and production of events.

The core principle remains: **Test the interface, not the implementation.**

---

## Mitigating Complexity and Cost

Moving away from unit tests introduces trade-offs, but modern development practices mitigate these risks:

### 1. Setup Complexity vs. Agentic AI
Writing comprehensive integration tests requires more boilerplate (setup, teardown, seeding).
- **Mitigation**: **Agentic models** and **Spec-Driven Development** excel here. By maintaining clear agent instructions and specifications, AI assistants can generate and maintain the complex test scaffolding that humans find tedious.

### 2. Execution Time vs. Sharding
Integration tests run slower than unit tests.
- **Mitigation**: **Test Sharding**. Distribute tests across multiple parallel workers.
- **Trade-off**: This lowers wall-clock time (keeping feedback loops fast) but increases total compute costs. This is an acceptable trade-off for the increased confidence and reduced maintenance burden of stable, behavioral tests.

### 3. Feedback Loop Speed vs. Selective Execution
Running the full suite for every small change can be slow.
- **Mitigation**: **Selective Test Execution**. In a monorepo or modular design, use dependency analysis tools to run only the tests affected by the changed code.
- **Mitigation**: **Fail Fast**. Configure CI pipelines to abort immediately upon the first failure, saving resources and alerting developers quicker.

### 4. Flakiness vs. Deterministic Data
Shared state is the enemy of reliable integration tests.
- **Mitigation**: **Unique Namespacing**. Ensure every test generates unique identifiers (UUIDs) for its data. Avoid hardcoded IDs (e.g., `ID=1`).
- **Mitigation**: **Robust Wait Strategies**. Instead of `time.Sleep()`, use polling mechanisms to wait for asynchronous side effects (e.g., "wait until message appears in queue").

---

## Celery Task Testing

Testing asynchronous Celery tasks presents unique challenges:
- Background workers run in separate processes, making coverage collection difficult
- Async behavior can introduce timing issues and test flakiness
- Need to validate both task logic AND integration with broker/backend

### Real Workers in All Contexts

This repository uses **real Celery workers** in all test contexts:
- Unit tests: Worker runs locally on host (via pytest-celery)
- Integration tests: Worker runs in Docker container
- Local integration tests: Worker runs locally for debugging

### Benefits

- **Realistic Testing**: Validates actual message passing and task execution
- **Production Parity**: Tests behave like production
- **Coverage Support**: pytest-celery workers support coverage instrumentation in unit tests
- **Debuggable**: Workers can be debugged with breakpoints in local contexts

### Example Test

```python
def test_async_job(client):
    # Submit job via HTTP API
    response = client.post("/api/v1/async_job/submit", json={"data": "test"})
    assert response.status_code == 200
    job_id = response.json()["job_id"]
    
    # Wait for task to complete
    import time
    time.sleep(2)
    
    # Check result
    result_response = client.get(f"/api/v1/async_job/result/{job_id}")
    assert result_response.status_code == 200
    assert result_response.json()["status"] == "completed"
```

### Production Testing

For testing the production Docker image (via `docker-compose.test.yml`):
- Celery workers run in separate containers
- Tests validate the full deployment topology
- Coverage is NOT collected (production image has no test tooling)
- Focus shifts to **behavioral validation** rather than code coverage

This approach ensures:
- Realistic task execution in all environments
- Production parity across all test contexts

---

## Test Runtime Contexts

This repository defines **three distinct test runtime contexts**, each optimized for different purposes:

### 1. Local Unit Tests (`make test-unit`)

**Purpose**: Fast feedback with comprehensive coverage during development

**Characteristics**:
- Runs on host using `uv run pytest`
- Dependencies (PostgreSQL, RabbitMQ) run in Docker containers
- Celery worker runs locally on host (via pytest-celery)
- **Coverage enabled** (line and branch coverage)
- Moderate execution speed (~seconds to minutes)

**When to use**:
- Primary development workflow
- Pre-commit validation
- Coverage analysis
- TDD/refactoring cycles

**Command**: `make test-unit`

**Trade-offs**:
- ✅ Full coverage metrics
- ✅ Debuggable (local worker)
- ✅ Realistic task execution
- ⚠️ Doesn't validate containerized deployment
- ⚠️ Slower than mocked/eager approaches

---

### 2. Integration Tests (`make test-integration`)

**Purpose**: Validate production Docker image and deployment topology

**Characteristics**:
- All services run in Docker Compose
- API server, Celery worker, and dependencies all containerized
- Tests run inside a test container
- **No coverage** (production image has no test tooling)
- Validates actual production artifacts
- Slower execution (~30-60 seconds including build)

**When to use**:
- CI pipeline validation
- Pre-release testing
- Validating Docker image changes
- Testing deployment configurations

**Command**: `make test-integration`

**Trade-offs**:
- ✅ Validates production-like environment
- ✅ Tests actual Docker images
- ✅ Catches deployment/configuration issues
- ⚠️ Slower (requires image builds)
- ⚠️ No coverage metrics
- ⚠️ Harder to debug (everything containerized)

---

### 3. Local Integration Tests (`make test-local-integration`)

**Purpose**: Debug integration tests with IDE breakpoints and step-through debugging

**Characteristics**:
- Dependencies run in Docker containers
- API server and Celery worker run **locally on host**
- Tests run on host with `BASE_URL=http://localhost:8000`
- Developer manually starts API/worker in debug mode
- **No coverage** (focus is on debugging, not metrics)

**When to use**:
- Debugging failing integration tests
- Step-through debugging of API handlers
- Investigating timing/async issues
- Understanding complex request flows

**Command**: 
```bash
# Terminal 1: Start dependencies
make deps-up

# Terminal 2: Start API in debug mode (with IDE debugger attached)
make run  # or run via IDE debugger

# Terminal 3: Run integration tests
make test-local-integration
```

**Trade-offs**:
- ✅ Full IDE debugging support
- ✅ Set breakpoints in API/worker code
- ✅ Fast iteration (no container rebuilds)
- ⚠️ Manual workflow (multiple terminals)
- ⚠️ Requires local Python environment
- ⚠️ Doesn't validate containerized deployment

---

### Choosing the Right Context

| Need | Use |
|------|-----|
| Fast TDD cycle | `make test-unit` |
| Coverage reports | `make test-unit` |
| Debug test failure | `make test-local-integration` |
| Pre-commit check | `make test-unit` |
| CI validation | `make test-integration` |
| Validate Docker image | `make test-integration` |
| Step through API handler | `make test-local-integration` |

### Context Switching via Environment Variables

The test suite automatically adapts based on `BASE_URL`:
- **`BASE_URL` not set**: Unit test context (TestClient, local Celery worker)
- **`BASE_URL` set**: Integration test context (real HTTP client, containerized workers)

This design enables **test reuse**: the same test code works in all three contexts.

---
