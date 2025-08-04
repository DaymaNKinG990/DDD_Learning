"""Tests for notifications.application.services module."""

import pytest
from unittest.mock import Mock, AsyncMock
from datetime import datetime, timezone

from src.notifications.application.services import NotificationService
from src.notifications.domain.entities import Notification, NotificationBatch, NotificationSubscription
from src.notifications.domain.events import NotificationSent, NotificationCreated
from src.notifications.domain.repositories import NotificationRepository
from src.notifications.domain.value_objects import (
    NotificationId,
    NotificationStatus,
    NotificationType,
    NotificationPriority,
    NotificationRecipient,
    NotificationTemplate,
)
from src.shared.application.event_handlers import EventHandler
from src.shared.domain.exceptions import EntityNotFoundError
from src.users.domain.value_objects import UserId


@pytest.mark.asyncio
class TestNotificationService:
    """Test NotificationService."""

    @pytest.fixture
    def notification_repository(self):
        """Create notification repository mock."""
        return Mock()

    @pytest.fixture
    def batch_repository(self):
        """Create batch repository mock."""
        return Mock()

    @pytest.fixture
    def subscription_repository(self):
        """Create subscription repository mock."""
        return Mock()

    @pytest.fixture
    def event_handler(self):
        """Create event handler mock."""
        return Mock(spec=EventHandler)

    @pytest.fixture
    def service(self, notification_repository, batch_repository, subscription_repository, event_handler):
        """Create notification service instance."""
        return NotificationService(
            notification_repository=notification_repository,
            batch_repository=batch_repository,
            subscription_repository=subscription_repository,
            event_handler=event_handler,
        )

    @pytest.fixture
    def sample_recipient(self):
        """Create sample notification recipient."""
        return NotificationRecipient(
            user_id="user-123",
            email="test@example.com",
        )

    @pytest.fixture
    def sample_template(self):
        """Create sample notification template."""
        return NotificationTemplate(
            name="test_template",
            content="Hello {{name}}, this is a test notification.",
            subject="Test Notification",
        )

    @pytest.fixture
    def sample_notification(self):
        """Create sample notification."""
        notification = Mock(spec=Notification)
        notification.id = NotificationId("notification-123")
        notification.status = NotificationStatus.PENDING
        notification.type = NotificationType.EMAIL
        notification.priority = NotificationPriority.NORMAL
        notification.created_at = datetime.now(timezone.utc)
        return notification

    async def test_send_notification_successful(self, service, notification_repository, event_handler, sample_recipient, sample_template, sample_notification):
        """Test successful notification sending."""
        notification_repository.save = AsyncMock(return_value=sample_notification)
        event_handler.handle = AsyncMock()
        
        result = await service.send_notification(
            recipient=sample_recipient,
            template=sample_template,
            notification_type=NotificationType.EMAIL,
            data={"name": "John"},
            priority=NotificationPriority.NORMAL,
        )
        
        assert result == sample_notification
        notification_repository.save.assert_called_once()
        event_handler.handle.assert_called_once()
        
        # Verify event was called with NotificationCreated
        call_args = event_handler.handle.call_args[0][0]
        assert isinstance(call_args, NotificationCreated)

    async def test_mark_notification_sent(self, service, notification_repository, event_handler, sample_notification):
        """Test marking notification as sent."""
        sample_notification.send = Mock()
        notification_repository.get_by_id = AsyncMock(return_value=sample_notification)
        notification_repository.save = AsyncMock(return_value=sample_notification)
        event_handler.handle = AsyncMock()
        
        result = await service.mark_notification_sent("notification-123")
        
        assert result == sample_notification
        sample_notification.send.assert_called_once()
        notification_repository.save.assert_called_once()
        event_handler.handle.assert_called_once()
        
        # Verify event was called with NotificationSent
        call_args = event_handler.handle.call_args[0][0]
        assert isinstance(call_args, NotificationSent)

    async def test_mark_notification_sent_not_found(self, service, notification_repository):
        """Test marking notification as sent when not found."""
        notification_repository.get_by_id = AsyncMock(return_value=None)
        
        with pytest.raises(ValueError, match="Notification with ID notification-123 not found"):
            await service.mark_notification_sent("notification-123")

    async def test_mark_notification_delivered(self, service, notification_repository, event_handler, sample_notification):
        """Test marking notification as delivered."""
        sample_notification.deliver = Mock()
        notification_repository.get_by_id = AsyncMock(return_value=sample_notification)
        notification_repository.save = AsyncMock(return_value=sample_notification)
        event_handler.handle = AsyncMock()
        
        result = await service.mark_notification_delivered("notification-123")
        
        assert result == sample_notification
        sample_notification.deliver.assert_called_once()
        notification_repository.save.assert_called_once()
        event_handler.handle.assert_called_once()

    async def test_mark_notification_failed(self, service, notification_repository, event_handler, sample_notification):
        """Test marking notification as failed."""
        sample_notification.fail = Mock()
        notification_repository.get_by_id = AsyncMock(return_value=sample_notification)
        notification_repository.save = AsyncMock(return_value=sample_notification)
        event_handler.handle = AsyncMock()
        
        result = await service.mark_notification_failed("notification-123", "Connection timeout")
        
        assert result == sample_notification
        sample_notification.fail.assert_called_once_with("Connection timeout")
        notification_repository.save.assert_called_once()
        event_handler.handle.assert_called_once()

    async def test_retry_notification(self, service, notification_repository, sample_notification):
        """Test retrying notification."""
        notification_repository.get_by_id = AsyncMock(return_value=sample_notification)
        notification_repository.save = AsyncMock(return_value=sample_notification)
        
        result = await service.retry_notification("notification-123")
        
        assert result == sample_notification
        assert sample_notification.status == NotificationStatus.PENDING
        notification_repository.save.assert_called_once()

    async def test_retry_notification_not_found(self, service, notification_repository):
        """Test retrying notification when not found."""
        notification_repository.get_by_id = AsyncMock(return_value=None)
        
        with pytest.raises(ValueError, match="Notification with ID notification-123 not found"):
            await service.retry_notification("notification-123")

    async def test_create_subscription(self, service, subscription_repository, event_handler):
        """Test creating notification subscription."""
        subscription = Mock(spec=NotificationSubscription)
        subscription_repository.save = AsyncMock(return_value=subscription)
        event_handler.handle = AsyncMock()
        
        result = await service.create_subscription(
            user_id="user-123",
            event_type="order_created",
            channels=[NotificationType.EMAIL, NotificationType.PUSH],
        )
        
        assert result == subscription
        subscription_repository.save.assert_called_once()

    async def test_get_user_subscriptions(self, service, subscription_repository):
        """Test getting user subscriptions."""
        subscriptions = [Mock(spec=NotificationSubscription), Mock(spec=NotificationSubscription)]
        subscription_repository.get_by_user_id = AsyncMock(return_value=subscriptions)
        
        result = await service.get_user_subscriptions("user-123")
        
        assert result == subscriptions
        subscription_repository.get_by_user_id.assert_called_once_with("user-123")

    async def test_get_pending_notifications(self, service, notification_repository, sample_notification):
        """Test getting pending notifications."""
        notifications = [sample_notification, Mock(spec=Notification)]
        notification_repository.get_by_status = AsyncMock(return_value=notifications)
        
        result = await service.get_pending_notifications()
        
        assert result == notifications
        notification_repository.get_by_status.assert_called_once_with(NotificationStatus.PENDING)

    async def test_get_failed_notifications(self, service, notification_repository, sample_notification):
        """Test getting failed notifications."""
        notifications = [sample_notification, Mock(spec=Notification)]
        notification_repository.get_by_status = AsyncMock(return_value=notifications)
        
        result = await service.get_failed_notifications()
        
        assert result == notifications
        notification_repository.get_by_status.assert_called_once_with(NotificationStatus.FAILED)

    async def test_create_batch(self, service, batch_repository, event_handler, sample_template):
        """Test creating notification batch."""
        batch = Mock(spec=NotificationBatch)
        batch_repository.save = AsyncMock(return_value=batch)
        event_handler.handle = AsyncMock()
        
        recipients = [
            NotificationRecipient(user_id="user-123", email="user1@example.com"),
            NotificationRecipient(user_id="user-456", email="user2@example.com"),
        ]
        
        result = await service.create_batch(
            name="test_batch",
            template=sample_template,
            notification_type=NotificationType.EMAIL,
            recipients=recipients,
            data={"event": "test"},
            description="Test batch",
            priority=NotificationPriority.NORMAL,
        )
        
        assert result == batch
        batch_repository.save.assert_called_once()
        # Note: create_batch doesn't call event_handler.handle, so we don't check it 