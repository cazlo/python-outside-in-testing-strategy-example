import os
import pytest
import requests

# CRITICAL: Set test environment variables BEFORE any app imports
# This ensures settings are instantiated with the correct values
if not os.getenv("BASE_URL"):  # Unit test context
    # Override DATABASE_HOST for local unit tests
    if not os.getenv("DATABASE_HOST_OVERRIDE_DISABLED"):
        os.environ["DATABASE_HOST"] = os.getenv("DATABASE_HOST_TEST", "localhost")
        os.environ["DATABASE_PORT"] = os.getenv("DATABASE_PORT_TEST", "5454")
        os.environ["RABBITMQ_HOST"] = os.getenv("RABBITMQ_HOST_TEST", "localhost")
        os.environ["RABBITMQ_PORT"] = os.getenv("RABBITMQ_PORT_TEST", "5672")

from fastapi.testclient import TestClient
from app.core.config import settings
from app.main import app


def is_integration_context() -> bool:
    """
    Detect if we're running in integration test context.
    Integration context: BASE_URL is set (pointing to a real server)
    Unit test context: BASE_URL is not set (use TestClient)
    """
    return bool(os.getenv("BASE_URL"))


@pytest.fixture(scope='session')
def celery_config():
    """
    Celery configuration fixture for unit tests.
    Configures Celery to run in eager mode (synchronous execution).
    In integration tests, this is skipped and a real worker is used.
    """
    if is_integration_context():
        pytest.skip("Celery config not needed for integration tests - using real worker")
    
    rabbitmq_user = getattr(settings, "RABBITMQ_USER", "guest")
    rabbitmq_password = getattr(settings, "RABBITMQ_PASSWORD", "guest")
    rabbitmq_host = getattr(settings, "RABBITMQ_HOST", "localhost")  # Use localhost for unit tests
    rabbitmq_port = getattr(settings, "RABBITMQ_PORT", 5672)
    return {
        'broker_url': f"amqp://{rabbitmq_user}:{rabbitmq_password}@{rabbitmq_host}:{rabbitmq_port}//",
        'result_backend': str(settings.SYNC_CELERY_DATABASE_URI),
        'include':  "app.api.celery_task",  # required for test coverage
        # 'task_always_eager': True,  # Execute tasks synchronously
        # 'task_eager_propagates': True,  # Propagate exceptions in eager mode
        'broker_connection_retry_on_startup': True,  # Don't fail if broker is unreachable
    }


@pytest.fixture(scope='function')
def celery_worker(celery_app):
    """
    Custom celery_worker fixture that handles both unit and integration contexts.
    - Unit tests: Returns None (eager mode handles execution inline)
    - Integration tests: Would skip this fixture (real worker runs externally)
    
    This fixture ensures unit tests don't try to spin up a real worker thread.
    """
    if is_integration_context():
        pytest.skip("Real celery worker is running externally in integration context")
    
    # In eager mode, tasks execute inline, so we don't need to start a worker
    # Just ensure the app is configured with eager mode
    if celery_app.conf.task_always_eager:
        # Return a mock object so tests that reference celery_worker don't fail
        yield None
        return
    
    # If not in eager mode (shouldn't happen for unit tests), fall back to pytest-celery worker
    from celery.contrib.testing import worker
    with worker.start_worker(celery_app, perform_ping_check=False):
        yield


@pytest.fixture(scope='session')
def client():
    """
    Universal client fixture that returns the appropriate client based on test context.
    - Unit tests: Returns FastAPI TestClient
    - Integration tests: Returns real HTTP client
    """
    if is_integration_context():
        # Integration test context: use real HTTP client
        base_url = os.getenv("BASE_URL", "http://localhost:8000")
        
        class HTTPClient:
            """Wrapper around requests with a base_url for easier testing."""
            
            def __init__(self, base_url: str):
                self.base_url = base_url.rstrip('/')
                self.session = requests.Session()
            
            def get(self, path: str, **kwargs):
                url = f"{self.base_url}/{path.lstrip('/')}"
                return self.session.get(url, **kwargs)
            
            def post(self, path: str, **kwargs):
                url = f"{self.base_url}/{path.lstrip('/')}"
                return self.session.post(url, **kwargs)
            
            def put(self, path: str, **kwargs):
                url = f"{self.base_url}/{path.lstrip('/')}"
                return self.session.put(url, **kwargs)
            
            def delete(self, path: str, **kwargs):
                url = f"{self.base_url}/{path.lstrip('/')}"
                return self.session.delete(url, **kwargs)
            
            def patch(self, path: str, **kwargs):
                url = f"{self.base_url}/{path.lstrip('/')}"
                return self.session.patch(url, **kwargs)
        
        return HTTPClient(base_url)
    else:
        # Unit test context: use FastAPI TestClient
        return TestClient(app, base_url="http://testserver")


# Only register celery pytest plugin for unit tests
# In integration tests, we use a real celery worker
if not is_integration_context():
    pytest_plugins = ("celery.contrib.pytest", )


