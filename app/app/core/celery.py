# Celery is good for data-intensive application or some long-running tasks in other simple cases use Fastapi background tasks
# Reference https://towardsdatascience.com/deploying-ml-models-in-production-with-fastapi-and-celery-7063e539a5db
from celery import Celery
from app.core.config import settings

# Get RabbitMQ credentials from settings or use defaults
rabbitmq_user = getattr(settings, "RABBITMQ_USER", "guest")
rabbitmq_password = getattr(settings, "RABBITMQ_PASSWORD", "guest")
rabbitmq_host = getattr(settings, "RABBITMQ_HOST", "rabbitmq")
rabbitmq_port = getattr(settings, "RABBITMQ_PORT", 5672)

celery = Celery(
    "async_task",
    broker=f"amqp://{rabbitmq_user}:{rabbitmq_password}@{rabbitmq_host}:{rabbitmq_port}//",
    backend=str(settings.SYNC_CELERY_DATABASE_URI),
    include="app.api.celery_task",  # route where tasks are defined
)

celery.conf.update({"beat_dburi": str(settings.SYNC_CELERY_BEAT_DATABASE_URI)})
celery.autodiscover_tasks()
