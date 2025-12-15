from app.schemas.response_schema import IGetResponseBase, create_response
from datetime import datetime
from fastapi import APIRouter
from fastapi_cache.decorator import cache

router = APIRouter()

# this is a basic demo of using the fastapi cache, with caching distributed and
#  backed by redis


@router.get("/cached")
@cache(expire=10)
async def get_a_cached_response() -> IGetResponseBase[str]:
    """
    Gets a cached datetime
    """
    return create_response(data=datetime.now().isoformat())


@router.get("/no_cache")
async def get_a_normal_response() -> IGetResponseBase[str]:
    """
    Gets a real-time datetime
    """
    return create_response(data=datetime.now().isoformat())
