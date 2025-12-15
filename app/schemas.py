from datetime import datetime

from pydantic import BaseModel


class ItemCreate(BaseModel):
    name: str


class ItemResponse(BaseModel):
    id: int
    name: str
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
