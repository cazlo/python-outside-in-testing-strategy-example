"""
Unit tests for Celery tasks.

These are more focused tests that verify individual task behavior.
"""
from unittest.mock import MagicMock, patch

from app.tasks import process_item


def test_process_item_success():
    """Test that process_item correctly updates an item's status."""
    # Create mock objects
    mock_session = MagicMock()
    mock_item = MagicMock()
    mock_item.id = 1
    mock_item.name = "Test Item"
    mock_item.status = "pending"

    # Setup the query chain
    mock_query = MagicMock()
    mock_filter = MagicMock()
    mock_query.filter.return_value = mock_filter
    mock_filter.first.return_value = mock_item
    mock_session.query.return_value = mock_query

    with patch("app.tasks.SessionLocal", return_value=mock_session):
        result = process_item(1)

        # Verify the item status was updated
        assert mock_item.status == "processed"
        # Verify commit was called
        mock_session.commit.assert_called_once()
        # Verify result
        assert result["status"] == "processed"
        assert result["id"] == 1


def test_process_item_not_found():
    """Test that process_item handles missing items gracefully."""
    mock_session = MagicMock()

    # Setup the query chain to return None
    mock_query = MagicMock()
    mock_filter = MagicMock()
    mock_query.filter.return_value = mock_filter
    mock_filter.first.return_value = None
    mock_session.query.return_value = mock_query

    with patch("app.tasks.SessionLocal", return_value=mock_session):
        result = process_item(999)

        # Verify error message
        assert "error" in result
        assert "not found" in result["error"].lower()
        # Verify commit was not called since nothing to update
        mock_session.commit.assert_not_called()
