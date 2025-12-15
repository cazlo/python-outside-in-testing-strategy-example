import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from asgi_lifespan import LifespanManager

from app.main import app


@pytest_asyncio.fixture
async def app_lifecycle_managed():
    async with LifespanManager(app) as manager:
        # see also https://fastapi.tiangolo.com/advanced/async-tests/#in-detail
        # caching requires lifecycle features
        print("We're in!")
        yield manager.app


@pytest_asyncio.fixture
async def test_client(app_lifecycle_managed):
    async with AsyncClient(
        transport=ASGITransport(app=app_lifecycle_managed), base_url="http://test:1080/api/v1"
    ) as client:
        print("Client is ready")
        yield client


@pytest.mark.asyncio
async def test_cached(test_client):
    endpoint = "cache/cached"
    response = await test_client.get(endpoint)
    assert response.status_code == 200
    original_etag = response.headers["etag"]
    original_call_time = response.json()["data"]

    cached_response = await test_client.get(endpoint)
    assert cached_response.status_code == 200
    cached_call_time = cached_response.json()["data"]
    cached_call_etag = cached_response.headers["etag"]
    assert original_call_time == cached_call_time
    assert original_etag == cached_call_etag

    cached_response = await test_client.get(endpoint, headers={"If-None-Match": original_etag} )
    assert cached_response.status_code == 304


@pytest.mark.asyncio
async def test_no_cached(test_client):
    endpoint = "cache/no_cache"
    response = await test_client.get(endpoint)
    assert response.status_code == 200
    original_call_time = response.json()["data"]
    cached_response = await test_client.get(endpoint)
    assert cached_response.status_code == 200
    cached_call_time = cached_response.json()["data"]
    assert original_call_time != cached_call_time
