from celery import Celery

from app.config import settings
from app.database import Item, SessionLocal

celery_app = Celery(
    "worker",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

celery_app.conf.task_routes = {
    "app.tasks.process_item": "main-queue",
}


@celery_app.task(name="app.tasks.process_item")
def process_item(item_id: int) -> dict:
    """
    Process an item by updating its status to 'processed'.
    This simulates background work that modifies database state.
    """
    db = SessionLocal()
    try:
        item = db.query(Item).filter(Item.id == item_id).first()
        if item:
            item.status = "processed"
            db.commit()
            db.refresh(item)
            return {
                "id": item.id,
                "name": item.name,
                "status": item.status,
            }
        return {"error": f"Item {item_id} not found"}
    finally:
        db.close()
