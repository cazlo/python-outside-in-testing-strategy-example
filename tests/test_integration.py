"""
Integration tests following the Diamond Testing Strategy.

These tests verify the entire flow from API request through database to Celery tasks.
They are "integration-biased" meaning they test multiple components working together.
"""
import asyncio
from unittest.mock import patch, MagicMock

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    """Test the health check endpoint."""
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


@pytest.mark.asyncio
async def test_create_item_triggers_background_task(client: AsyncClient):
    """
    Integration test: Create an item and verify it triggers a background task.
    This mocks the Celery task to verify integration without needing RabbitMQ.
    """
    with patch("app.main.process_item") as mock_task:
        mock_task.delay = MagicMock()
        
        response = await client.post("/items", json={"name": "Test Item"})
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Item"
        assert data["status"] == "pending"
        assert "id" in data
        
        # Verify the background task was triggered
        mock_task.delay.assert_called_once_with(data["id"])


@pytest.mark.asyncio
async def test_get_item(client: AsyncClient):
    """Test getting an item by ID."""
    # First create an item
    create_response = await client.post("/items", json={"name": "Get Test Item"})
    assert create_response.status_code == 201
    item_id = create_response.json()["id"]
    
    # Then retrieve it
    response = await client.get(f"/items/{item_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == item_id
    assert data["name"] == "Get Test Item"
    assert data["status"] == "pending"


@pytest.mark.asyncio
async def test_get_nonexistent_item(client: AsyncClient):
    """Test getting an item that doesn't exist."""
    response = await client.get("/items/999999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_list_items(client: AsyncClient):
    """Test listing all items."""
    # Create multiple items
    await client.post("/items", json={"name": "Item 1"})
    await client.post("/items", json={"name": "Item 2"})
    await client.post("/items", json={"name": "Item 3"})
    
    # List all items
    response = await client.get("/items")
    assert response.status_code == 200
    items = response.json()
    assert len(items) == 3
    assert all("name" in item for item in items)
    assert all("status" in item for item in items)


@pytest.mark.asyncio
async def test_full_workflow_with_task_processing(client: AsyncClient):
    """
    Full integration test: Create item, process it, and verify state change.
    This test simulates the complete workflow including the Celery task execution.
    """
    # Create an item
    create_response = await client.post("/items", json={"name": "Workflow Item"})
    assert create_response.status_code == 201
    item_id = create_response.json()["id"]
    
    # Verify initial state
    get_response = await client.get(f"/items/{item_id}")
    assert get_response.json()["status"] == "pending"
    
    # Simulate task processing (in a real integration test with docker-compose,
    # this would happen automatically via Celery worker)
    from app.tasks import process_item
    result = process_item(item_id)
    
    assert result["status"] == "processed"
    
    # Verify updated state
    final_response = await client.get(f"/items/{item_id}")
    assert final_response.json()["status"] == "processed"
