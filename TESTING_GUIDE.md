# Diamond Testing Strategy Guide

## What is the Diamond Testing Strategy?

The Diamond (or Integration-Biased) Testing Strategy is an approach to testing that prioritizes integration tests over unit tests. Instead of the traditional testing pyramid (many unit tests, fewer integration tests, very few end-to-end tests), the diamond strategy uses:

```
        /\
       /  \        <- Few E2E tests
      /    \
     /------\      <- Many Integration tests (the "diamond")
    /        \
   /----------\    <- Fewer Unit tests (only for critical logic)
  
```

## Why Use This Strategy?

### Benefits

1. **Real-world confidence**: Tests verify the system works as a whole, not just in isolation
2. **Less brittleness**: Fewer mocks mean less coupling to implementation details
3. **Faster refactoring**: Change internals without breaking tests
4. **Better bug detection**: Integration issues are caught early
5. **Simpler test maintenance**: Fewer tests to maintain overall

### Trade-offs

1. **Slower execution**: Integration tests are slower than unit tests (mitigated by Docker)
2. **More complex setup**: Requires infrastructure (databases, message queues)
3. **Harder to debug**: Failures may involve multiple components

## Our Implementation

### Test Layers

#### 1. Integration Tests (Primary Layer)
**Location**: `tests/test_integration.py`

These tests verify the entire workflow:
- HTTP request → FastAPI endpoint
- Database operations via SQLAlchemy
- Background task triggering via Celery
- End-to-end state verification

**Example**:
```python
async def test_create_item_triggers_background_task(client: AsyncClient):
    response = await client.post("/items", json={"name": "Test Item"})
    assert response.status_code == 201
    # Verifies: API, Database, Task triggering
```

**When to use**:
- Testing API endpoints
- Verifying database persistence
- Checking workflow orchestration
- Validating business processes

#### 2. Unit Tests (Secondary Layer)
**Location**: `tests/test_tasks.py`

These tests verify isolated components with critical business logic:
- Celery task execution
- Complex business rules
- Edge case handling

**Example**:
```python
def test_process_item_success():
    result = process_item(1)
    assert result["status"] == "processed"
    # Verifies: Task logic in isolation
```

**When to use**:
- Complex business logic that's hard to test via integration
- Edge cases that are difficult to reproduce end-to-end
- Performance-critical code that needs fast test feedback

### Test Infrastructure

#### Fixtures (tests/conftest.py)

1. **test_db**: Provides a clean database for each test
   - Creates schema before test
   - Drops schema after test
   - Ensures test isolation

2. **client**: Provides an HTTP client with database dependency override
   - Injects test database
   - Allows async API testing
   - Cleans up after each test

#### Test Database Strategy

We use a real PostgreSQL database in tests (not SQLite or in-memory):
- Same database engine as production
- Catches SQL compatibility issues
- Tests real connection pooling behavior
- Validates actual query performance

This is made fast through Docker Compose and parallel test execution.

## Running Tests

### All Tests
```bash
make test
```
Starts Docker services, runs all tests, then stops services.

### Unit Tests Only (Fast)
```bash
make test-unit
```
No Docker required, runs in milliseconds.

### Integration Tests (Slower)
```bash
make test-integration
```
Requires Docker services, runs in seconds.

### With Coverage
```bash
make test-cov
```
Generates HTML coverage report in `htmlcov/`.

## Writing New Tests

### Guidelines

1. **Start with integration**: Write an integration test first
2. **Add unit tests only when needed**: For complex logic or edge cases
3. **Use real services**: Prefer actual databases over mocks
4. **Test behavior, not implementation**: Focus on what happens, not how
5. **Keep tests independent**: Each test should work in isolation

### Integration Test Template

```python
@pytest.mark.asyncio
async def test_my_feature(client: AsyncClient):
    # Arrange: Set up initial state
    setup_response = await client.post("/items", json={"name": "Setup"})
    item_id = setup_response.json()["id"]
    
    # Act: Perform the action
    response = await client.get(f"/items/{item_id}")
    
    # Assert: Verify the outcome
    assert response.status_code == 200
    assert response.json()["name"] == "Setup"
```

### Unit Test Template

```python
def test_my_function():
    # Arrange
    mock_dependency = MagicMock()
    
    # Act
    with patch("app.tasks.dependency", mock_dependency):
        result = my_function(input_data)
    
    # Assert
    assert result == expected_output
```

## Best Practices

### DO

- ✅ Write integration tests for happy paths
- ✅ Write integration tests for common error cases
- ✅ Use real databases and services when possible
- ✅ Test the public API, not private methods
- ✅ Use descriptive test names that explain the scenario

### DON'T

- ❌ Mock everything (defeats the purpose)
- ❌ Test private methods directly
- ❌ Write unit tests for simple CRUD operations
- ❌ Skip integration tests because they're "too slow"
- ❌ Share state between tests

## Debugging Failed Tests

### Integration Test Failures

1. **Check the logs**: `make docker-logs`
2. **Verify services are running**: `docker ps`
3. **Connect to the database**: `docker exec -it <container> psql -U user -d testdb`
4. **Check API responses**: Add `print(response.json())` to see details
5. **Run single test**: `pytest tests/test_integration.py::test_name -v`

### Unit Test Failures

1. **Add debug prints**: Show intermediate values
2. **Use pytest debugger**: `pytest --pdb`
3. **Check mock setup**: Verify mock return values
4. **Isolate the test**: Run only the failing test

## Common Patterns

### Pattern 1: Create-Verify
```python
# Create something
create_resp = await client.post("/items", json={"name": "Test"})
item_id = create_resp.json()["id"]

# Verify it exists
get_resp = await client.get(f"/items/{item_id}")
assert get_resp.status_code == 200
```

### Pattern 2: Workflow Testing
```python
# Step 1: Initial state
initial = await client.get("/items")
assert len(initial.json()) == 0

# Step 2: Action
await client.post("/items", json={"name": "New"})

# Step 3: Verify state change
final = await client.get("/items")
assert len(final.json()) == 1
```

### Pattern 3: Error Handling
```python
# Trigger error condition
response = await client.get("/items/99999")

# Verify proper error response
assert response.status_code == 404
assert "not found" in response.json()["detail"].lower()
```

## Continuous Integration

When running in CI (GitHub Actions, etc.):

1. Use Docker Compose to spin up services
2. Run tests against real services
3. Collect coverage reports
4. Clean up services after tests

Example CI configuration:
```yaml
- name: Start services
  run: docker compose up -d
  
- name: Run tests
  run: pytest tests/ --cov=app --cov-report=xml
  
- name: Stop services
  run: docker compose down
```

## Measuring Success

Good test suite metrics:
- **Coverage**: Aim for 80%+ line coverage
- **Speed**: Integration tests should run in < 30 seconds
- **Reliability**: Tests should be deterministic (no flaky tests)
- **Clarity**: Test failures should clearly indicate what's broken

## Further Reading

- [Testing Strategies in a Microservice Architecture](https://martinfowler.com/articles/microservice-testing/)
- [The Testing Trophy](https://kentcdodds.com/blog/the-testing-trophy-and-testing-classifications)
- [Integration Testing with FastAPI](https://fastapi.tiangolo.com/tutorial/testing/)
- [pytest Documentation](https://docs.pytest.org/)
