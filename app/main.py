from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import Item, get_db, init_db
from app.schemas import ItemCreate, ItemResponse
from app.tasks import process_item


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup."""
    await init_db()
    yield


app = FastAPI(
    title="Python Outside-In Testing Example",
    description="A FastAPI service demonstrating diamond testing strategy",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post("/items", response_model=ItemResponse, status_code=201)
async def create_item(item: ItemCreate, db: AsyncSession = Depends(get_db)):
    """
    Create a new item and trigger background processing.
    """
    new_item = Item(name=item.name, status="pending")
    db.add(new_item)
    await db.commit()
    await db.refresh(new_item)

    # Trigger async task to process the item
    process_item.delay(new_item.id)

    return new_item


@app.get("/items/{item_id}", response_model=ItemResponse)
async def get_item(item_id: int, db: AsyncSession = Depends(get_db)):
    """
    Get an item by ID.
    """
    result = await db.execute(select(Item).where(Item.id == item_id))
    item = result.scalar_one_or_none()

    if not item:
        raise HTTPException(status_code=404, detail=f"Item {item_id} not found")

    return item


@app.get("/items", response_model=list[ItemResponse])
async def list_items(db: AsyncSession = Depends(get_db)):
    """
    List all items.
    """
    result = await db.execute(select(Item))
    items = result.scalars().all()
    return items
