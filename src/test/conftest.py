import pytest

from app.core.config import settings


@pytest.fixture(scope='session')
def celery_config():
    rabbitmq_user = getattr(settings, "RABBITMQ_USER", "guest")
    rabbitmq_password = getattr(settings, "RABBITMQ_PASSWORD", "guest")
    rabbitmq_host = getattr(settings, "RABBITMQ_HOST", "rabbitmq")
    rabbitmq_port = getattr(settings, "RABBITMQ_PORT", 5672)
    return {
        #     broker=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
        #     backend=str(settings.SYNC_CELERY_DATABASE_URI),
        #     include="app.api.celery_task",  # route where tasks are defined
        'broker_url': f"amqp://{rabbitmq_user}:{rabbitmq_password}@{rabbitmq_host}:{rabbitmq_port}//",
        'result_backend': str(settings.SYNC_CELERY_DATABASE_URI),
        'include':  "app.api.celery_task" # required for test coverage
    }

pytest_plugins = ("celery.contrib.pytest", )