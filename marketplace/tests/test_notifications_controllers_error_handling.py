"""Tests for error handling in notifications controllers."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import HTTPException
from fastapi.testclient import TestClient

from src.interfaces.api.notifications_controllers import (
    router,
    get_notification_service,
    SendNotificationRequest,
    CreateBatchRequest,
    RetryNotificationRequest,
    CreateSubscriptionRequest,
)
from src.notifications.application.services import NotificationService
from src.notifications.domain.exceptions import (
    NotificationNotFoundError,
    BatchNotFoundError,
    SubscriptionNotFoundError,
    InvalidNotificationDataError,
    InvalidBatchDataError,
)
from src.shared.domain.exceptions import EntityNotFoundError, InvalidOperationError


class TestNotificationsControllersErrorHandling:
    """Test error handling scenarios in notifications controllers."""

    @pytest.fixture
    def mock_notification_service(self):
        """Create a mock notification service."""
        service = AsyncMock(spec=NotificationService)
        return service

    @pytest.fixture
    def client(self, mock_notification_service):
        """Create test client with mocked service."""
        from fastapi import FastAPI
        app = FastAPI()
        app.include_router(router)
        
        # Override dependency
        app.dependency_overrides[get_notification_service] = lambda: mock_notification_service
        
        return TestClient(app)

    async def test_send_notification_invalid_data(self, client, mock_notification_service):
        """Test sending notification with invalid data."""
        # Arrange
        mock_notification_service.send_notification.side_effect = ValueError("Invalid notification data")
        
        request_data = {
            "recipient_id": "",
            "notification_type": "invalid_type",
            "title": "",
            "content": "",
            "priority": "invalid_priority"
        }
        
        # Act & Assert
        response = client.post("/notifications/send", json=request_data)
        assert response.status_code == 400
        assert "Invalid notification data" in response.json()["detail"]

    async def test_send_notification_entity_not_found(self, client, mock_notification_service):
        """Test sending notification when recipient not found."""
        # Arrange
        mock_notification_service.send_notification.side_effect = EntityNotFoundError("Recipient not found")
        
        request_data = {
            "recipient_id": "non_existent_user",
            "notification_type": "email",
            "title": "Test",
            "content": "Test content"
        }
        
        # Act & Assert
        response = client.post("/notifications/send", json=request_data)
        assert response.status_code == 404
        assert "Recipient not found" in response.json()["detail"]

    async def test_create_batch_empty_notifications(self, client, mock_notification_service):
        """Test creating batch with empty notifications list."""
        # Arrange
        mock_notification_service.create_batch.side_effect = InvalidBatchDataError("Batch cannot be empty")
        
        request_data = {
            "batch_name": "test_batch",
            "notifications": []
        }
        
        # Act & Assert
        response = client.post("/notifications/batch", json=request_data)
        assert response.status_code == 400
        assert "Batch cannot be empty" in response.json()["detail"]

    async def test_create_batch_invalid_data(self, client, mock_notification_service):
        """Test creating batch with invalid notification data."""
        # Arrange
        mock_notification_service.create_batch.side_effect = InvalidNotificationDataError("Invalid notification data")
        
        request_data = {
            "batch_name": "test_batch",
            "notifications": [
                {
                    "recipient_id": "",
                    "notification_type": "invalid",
                    "title": "",
                    "content": ""
                }
            ]
        }
        
        # Act & Assert
        response = client.post("/notifications/batch", json=request_data)
        assert response.status_code == 400
        assert "Invalid notification data" in response.json()["detail"]

    async def test_start_batch_processing_not_found(self, client, mock_notification_service):
        """Test starting batch processing with non-existent batch."""
        # Arrange
        mock_notification_service.start_batch_processing.side_effect = BatchNotFoundError("Batch not found")
        
        # Act & Assert
        response = client.post("/notifications/batch/non_existent_batch/start")
        assert response.status_code == 404
        assert "Batch not found" in response.json()["detail"]

    async def test_start_batch_processing_already_started(self, client, mock_notification_service):
        """Test starting already started batch."""
        # Arrange
        mock_notification_service.start_batch_processing.side_effect = InvalidOperationError("Batch already started")
        
        # Act & Assert
        response = client.post("/notifications/batch/test_batch/start")
        assert response.status_code == 400
        assert "Batch already started" in response.json()["detail"]

    async def test_complete_batch_not_found(self, client, mock_notification_service):
        """Test completing non-existent batch."""
        # Arrange
        mock_notification_service.complete_batch.side_effect = BatchNotFoundError("Batch not found")
        
        # Act & Assert
        response = client.post("/notifications/batch/non_existent_batch/complete")
        assert response.status_code == 404
        assert "Batch not found" in response.json()["detail"]

    async def test_complete_batch_invalid_status(self, client, mock_notification_service):
        """Test completing batch in invalid status."""
        # Arrange
        mock_notification_service.complete_batch.side_effect = InvalidOperationError("Cannot complete batch in current status")
        
        # Act & Assert
        response = client.post("/notifications/batch/test_batch/complete")
        assert response.status_code == 400
        assert "Cannot complete batch in current status" in response.json()["detail"]

    async def test_get_notification_not_found(self, client, mock_notification_service):
        """Test getting non-existent notification."""
        # Arrange
        mock_notification_service.get_notification_by_id.side_effect = NotificationNotFoundError("Notification not found")
        
        # Act & Assert
        response = client.get("/notifications/non_existent_notification")
        assert response.status_code == 404
        assert "Notification not found" in response.json()["detail"]

    async def test_mark_notification_sent_not_found(self, client, mock_notification_service):
        """Test marking non-existent notification as sent."""
        # Arrange
        mock_notification_service.mark_notification_sent.side_effect = NotificationNotFoundError("Notification not found")
        
        # Act & Assert
        response = client.post("/notifications/non_existent_notification/mark-sent")
        assert response.status_code == 404
        assert "Notification not found" in response.json()["detail"]

    async def test_mark_notification_sent_invalid_status(self, client, mock_notification_service):
        """Test marking notification as sent in invalid status."""
        # Arrange
        mock_notification_service.mark_notification_sent.side_effect = InvalidOperationError("Cannot mark as sent in current status")
        
        # Act & Assert
        response = client.post("/notifications/test_notification/mark-sent")
        assert response.status_code == 400
        assert "Cannot mark as sent in current status" in response.json()["detail"]

    async def test_mark_notification_delivered_not_found(self, client, mock_notification_service):
        """Test marking non-existent notification as delivered."""
        # Arrange
        mock_notification_service.mark_notification_delivered.side_effect = NotificationNotFoundError("Notification not found")
        
        # Act & Assert
        response = client.post("/notifications/non_existent_notification/mark-delivered")
        assert response.status_code == 404
        assert "Notification not found" in response.json()["detail"]

    async def test_mark_notification_failed_not_found(self, client, mock_notification_service):
        """Test marking non-existent notification as failed."""
        # Arrange
        mock_notification_service.mark_notification_failed.side_effect = NotificationNotFoundError("Notification not found")
        
        # Act & Assert
        response = client.post("/notifications/non_existent_notification/mark-failed")
        assert response.status_code == 404
        assert "Notification not found" in response.json()["detail"]

    async def test_retry_notification_not_found(self, client, mock_notification_service):
        """Test retrying non-existent notification."""
        # Arrange
        mock_notification_service.retry_notification.side_effect = NotificationNotFoundError("Notification not found")
        
        request_data = {"reason": "Test retry"}
        
        # Act & Assert
        response = client.post("/notifications/non_existent_notification/retry", json=request_data)
        assert response.status_code == 404
        assert "Notification not found" in response.json()["detail"]

    async def test_retry_notification_invalid_status(self, client, mock_notification_service):
        """Test retrying notification not in failed status."""
        # Arrange
        mock_notification_service.retry_notification.side_effect = InvalidOperationError("Can only retry failed notifications")
        
        request_data = {"reason": "Test retry"}
        
        # Act & Assert
        response = client.post("/notifications/test_notification/retry", json=request_data)
        assert response.status_code == 400
        assert "Can only retry failed notifications" in response.json()["detail"]

    async def test_create_subscription_invalid_data(self, client, mock_notification_service):
        """Test creating subscription with invalid data."""
        # Arrange
        mock_notification_service.create_subscription.side_effect = ValueError("Invalid subscription data")
        
        request_data = {
            "user_id": "",
            "notification_types": [],
            "channels": []
        }
        
        # Act & Assert
        response = client.post("/notifications/subscriptions", json=request_data)
        assert response.status_code == 400
        assert "Invalid subscription data" in response.json()["detail"]

    async def test_create_subscription_duplicate(self, client, mock_notification_service):
        """Test creating duplicate subscription."""
        # Arrange
        mock_notification_service.create_subscription.side_effect = InvalidOperationError("Subscription already exists")
        
        request_data = {
            "user_id": "test_user",
            "notification_types": ["email"],
            "channels": ["email"]
        }
        
        # Act & Assert
        response = client.post("/notifications/subscriptions", json=request_data)
        assert response.status_code == 400
        assert "Subscription already exists" in response.json()["detail"]

    async def test_get_user_subscriptions_not_found(self, client, mock_notification_service):
        """Test getting subscriptions for non-existent user."""
        # Arrange
        mock_notification_service.get_user_subscriptions.return_value = []
        
        # Act & Assert
        response = client.get("/notifications/subscriptions/user/non_existent_user")
        assert response.status_code == 200
        assert response.json() == []

    async def test_get_pending_notifications_empty(self, client, mock_notification_service):
        """Test getting pending notifications when none exist."""
        # Arrange
        mock_notification_service.get_pending_notifications.return_value = []
        
        # Act & Assert
        response = client.get("/notifications/pending")
        assert response.status_code == 200
        assert response.json() == []

    async def test_get_failed_notifications_empty(self, client, mock_notification_service):
        """Test getting failed notifications when none exist."""
        # Arrange
        mock_notification_service.get_failed_notifications.return_value = []
        
        # Act & Assert
        response = client.get("/notifications/failed")
        assert response.status_code == 200
        assert response.json() == [] 