from fastapi import APIRouter
from app.api.v1.endpoints import async_job

api_router = APIRouter()
api_router.include_router(async_job.router, prefix="/async_job", tags=["async_job"])
