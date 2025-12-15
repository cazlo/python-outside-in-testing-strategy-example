from fastapi import APIRouter
from app.api.v1.endpoints import (
    user,
    auth,
    cache,
    report,
    async_job,
)

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(user.router, prefix="/user", tags=["user"])
api_router.include_router(cache.router, prefix="/cache", tags=["cache"])
api_router.include_router(report.router, prefix="/report", tags=["report"])
api_router.include_router(async_job.router, prefix="/async_job", tags=["async_job"])
