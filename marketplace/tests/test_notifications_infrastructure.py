"""Tests for notifications infrastructure repositories."""

import pytest
from datetime import datetime, UTC
from unittest.mock import AsyncMock

from src.notifications.infrastructure.repositories import (
    InMemoryNotificationRepository,
    InMemoryNotificationBatchRepository,
    InMemoryNotificationSubscriptionRepository,
)
from src.notifications.domain.entities import (
    Notification,
    NotificationBatch,
    NotificationSubscription,
)
from src.notifications.domain.value_objects import (
    NotificationId,
    NotificationStatus,
    NotificationType,
    NotificationRecipient,
    NotificationTemplate,
    NotificationPriority,
)


class TestInMemoryNotificationRepository:
    """Test InMemoryNotificationRepository."""

    @pytest.fixture
    def repository(self):
        """Create InMemoryNotificationRepository."""
        return InMemoryNotificationRepository()

    @pytest.fixture
    def sample_notification(self):
        """Create sample notification."""
        return Notification(
            id=NotificationId(value="notif-123"),
            recipient=NotificationRecipient(
                user_id="user-123",
                email="test@example.com",
                phone="+1234567890",
                push_token="push-token-123",
                preferences={
                    "email_enabled": True,
                    "sms_enabled": True,
                    "push_enabled": True
                }
            ),
            template=NotificationTemplate(
                name="test_template",
                content="This is a test notification",
                subject="Test Subject",
                variables={"key": "value"}
            ),
            type=NotificationType.EMAIL,
            priority=NotificationPriority.NORMAL,
            status=NotificationStatus.PENDING,
            data={"key": "value"},
            scheduled_at=datetime.now(UTC)
        )

    @pytest.mark.asyncio
    async def test_save_notification(self, repository, sample_notification):
        """Test saving a notification."""
        # Act
        result = await repository.save(sample_notification)

        # Assert
        assert result == sample_notification
        saved_notification = await repository.get_by_id(sample_notification.id)
        assert saved_notification == sample_notification

    @pytest.mark.asyncio
    async def test_get_by_id_found(self, repository, sample_notification):
        """Test getting notification by ID when it exists."""
        # Arrange
        await repository.save(sample_notification)

        # Act
        result = await repository.get_by_id(sample_notification.id)

        # Assert
        assert result == sample_notification

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, repository):
        """Test getting notification by ID when it doesn't exist."""
        # Act
        result = await repository.get_by_id(NotificationId(value="notif-999"))

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_get_by_status(self, repository, sample_notification):
        """Test getting notifications by status."""
        # Arrange
        await repository.save(sample_notification)

        # Act
        result = await repository.get_by_status(NotificationStatus.PENDING)

        # Assert
        assert len(result) == 1
        assert result[0] == sample_notification

    @pytest.mark.asyncio
    async def test_get_by_status_empty(self, repository):
        """Test getting notifications by status when none exist."""
        # Act
        result = await repository.get_by_status(NotificationStatus.SENT)

        # Assert
        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_get_by_recipient(self, repository, sample_notification):
        """Test getting notifications by recipient."""
        # Arrange
        await repository.save(sample_notification)

        # Act
        result = await repository.get_by_recipient("user-123")

        # Assert
        assert len(result) == 1
        assert result[0] == sample_notification

    @pytest.mark.asyncio
    async def test_get_by_recipient_empty(self, repository):
        """Test getting notifications by recipient when none exist."""
        # Act
        result = await repository.get_by_recipient("user-999")

        # Assert
        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_get_by_type(self, repository, sample_notification):
        """Test getting notifications by type."""
        # Arrange
        await repository.save(sample_notification)

        # Act
        result = await repository.get_by_type(NotificationType.EMAIL)

        # Assert
        assert len(result) == 1
        assert result[0] == sample_notification

    @pytest.mark.asyncio
    async def test_get_by_type_empty(self, repository):
        """Test getting notifications by type when none exist."""
        # Act
        result = await repository.get_by_type(NotificationType.SMS)

        # Assert
        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_get_pending_notifications(self, repository, sample_notification):
        """Test getting pending notifications."""
        # Arrange
        await repository.save(sample_notification)

        # Act
        result = await repository.get_pending_notifications()

        # Assert
        assert len(result) == 1
        assert result[0] == sample_notification

    @pytest.mark.asyncio
    async def test_get_failed_notifications(self, repository):
        """Test getting failed notifications."""
        # Arrange
        failed_notification = Notification(
            id=NotificationId(value="notif-failed"),
            recipient=NotificationRecipient(
                user_id="user-123",
                email="test@example.com",
                preferences={}
            ),
            template=NotificationTemplate(
                name="failed_template",
                content="This notification failed"
            ),
            type=NotificationType.EMAIL,
            status=NotificationStatus.FAILED,
            scheduled_at=datetime.now(UTC)
        )
        await repository.save(failed_notification)

        # Act
        result = await repository.get_failed_notifications()

        # Assert
        assert len(result) == 1
        assert result[0] == failed_notification

    @pytest.mark.asyncio
    async def test_get_scheduled_notifications(self, repository, sample_notification):
        """Test getting scheduled notifications."""
        # Arrange
        await repository.save(sample_notification)
        before_time = datetime.now(UTC)

        # Act
        result = await repository.get_scheduled_notifications(before_time)

        # Assert
        assert len(result) == 1
        assert result[0] == sample_notification

    @pytest.mark.asyncio
    async def test_delete_notification(self, repository, sample_notification):
        """Test deleting a notification."""
        # Arrange
        await repository.save(sample_notification)

        # Act
        await repository.delete(sample_notification.id)

        # Assert
        result = await repository.get_by_id(sample_notification.id)
        assert result is None


class TestInMemoryNotificationBatchRepository:
    """Test InMemoryNotificationBatchRepository."""

    @pytest.fixture
    def repository(self):
        """Create InMemoryNotificationBatchRepository."""
        return InMemoryNotificationBatchRepository()

    @pytest.fixture
    def sample_batch(self):
        """Create sample notification batch."""
        return NotificationBatch(
            id=NotificationId(value="batch-123"),
            name="Test Batch",
            template=NotificationTemplate(
                name="batch_template",
                content="Batch notification content"
            ),
            type=NotificationType.EMAIL,
            recipients=[
                NotificationRecipient(
                    user_id="user-1",
                    email="user1@example.com",
                    preferences={}
                ),
                NotificationRecipient(
                    user_id="user-2",
                    email="user2@example.com",
                    preferences={}
                )
            ],
            total_count=2,
            status="pending",
            created_at=datetime.now(UTC)
        )

    @pytest.mark.asyncio
    async def test_save_batch(self, repository, sample_batch):
        """Test saving a notification batch."""
        # Act
        result = await repository.save(sample_batch)

        # Assert
        assert result == sample_batch
        saved_batch = await repository.get_by_id(sample_batch.id)
        assert saved_batch == sample_batch

    @pytest.mark.asyncio
    async def test_get_by_id_found(self, repository, sample_batch):
        """Test getting batch by ID when it exists."""
        # Arrange
        await repository.save(sample_batch)

        # Act
        result = await repository.get_by_id(sample_batch.id)

        # Assert
        assert result == sample_batch

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, repository):
        """Test getting batch by ID when it doesn't exist."""
        # Act
        result = await repository.get_by_id(NotificationId(value="batch-999"))

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_get_by_status(self, repository, sample_batch):
        """Test getting batches by status."""
        # Arrange
        await repository.save(sample_batch)

        # Act
        result = await repository.get_by_status("pending")

        # Assert
        assert len(result) == 1
        assert result[0] == sample_batch

    @pytest.mark.asyncio
    async def test_get_by_status_empty(self, repository):
        """Test getting batches by status when none exist."""
        # Act
        result = await repository.get_by_status("completed")

        # Assert
        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_get_pending_batches(self, repository, sample_batch):
        """Test getting pending batches."""
        # Arrange
        await repository.save(sample_batch)

        # Act
        result = await repository.get_pending_batches()

        # Assert
        assert len(result) == 1
        assert result[0] == sample_batch

    @pytest.mark.asyncio
    async def test_get_processing_batches(self, repository):
        """Test getting processing batches."""
        # Arrange
        processing_batch = NotificationBatch(
            id=NotificationId(value="batch-processing"),
            name="Processing Batch",
            template=NotificationTemplate(
                name="processing_template",
                content="Processing batch content"
            ),
            type=NotificationType.EMAIL,
            recipients=[],
            status="processing",
            created_at=datetime.now(UTC)
        )
        await repository.save(processing_batch)

        # Act
        result = await repository.get_processing_batches()

        # Assert
        assert len(result) == 1
        assert result[0] == processing_batch

    @pytest.mark.asyncio
    async def test_delete_batch(self, repository, sample_batch):
        """Test deleting a batch."""
        # Arrange
        await repository.save(sample_batch)

        # Act
        await repository.delete(sample_batch.id)

        # Assert
        result = await repository.get_by_id(sample_batch.id)
        assert result is None


class TestInMemoryNotificationSubscriptionRepository:
    """Test InMemoryNotificationSubscriptionRepository."""

    @pytest.fixture
    def repository(self):
        """Create InMemoryNotificationSubscriptionRepository."""
        return InMemoryNotificationSubscriptionRepository()

    @pytest.fixture
    def sample_subscription(self):
        """Create sample notification subscription."""
        return NotificationSubscription(
            id=NotificationId(value="sub-123"),
            user_id="user-123",
            event_type="order.confirmed",
            channels=[NotificationType.EMAIL, NotificationType.SMS],
            is_active=True,
            created_at=datetime.now(UTC)
        )

    @pytest.mark.asyncio
    async def test_save_subscription(self, repository, sample_subscription):
        """Test saving a notification subscription."""
        # Act
        result = await repository.save(sample_subscription)

        # Assert
        assert result == sample_subscription
        saved_subscription = await repository.get_by_id(sample_subscription.id)
        assert saved_subscription == sample_subscription

    @pytest.mark.asyncio
    async def test_get_by_id_found(self, repository, sample_subscription):
        """Test getting subscription by ID when it exists."""
        # Arrange
        await repository.save(sample_subscription)

        # Act
        result = await repository.get_by_id(sample_subscription.id)

        # Assert
        assert result == sample_subscription

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, repository):
        """Test getting subscription by ID when it doesn't exist."""
        # Act
        result = await repository.get_by_id(NotificationId(value="sub-999"))

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_get_by_user_id(self, repository, sample_subscription):
        """Test getting subscriptions by user ID."""
        # Arrange
        await repository.save(sample_subscription)

        # Act
        result = await repository.get_by_user_id("user-123")

        # Assert
        assert len(result) == 1
        assert result[0] == sample_subscription

    @pytest.mark.asyncio
    async def test_get_by_user_id_empty(self, repository):
        """Test getting subscriptions by user ID when none exist."""
        # Act
        result = await repository.get_by_user_id("user-999")

        # Assert
        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_get_by_event_type(self, repository, sample_subscription):
        """Test getting subscriptions by event type."""
        # Arrange
        await repository.save(sample_subscription)

        # Act
        result = await repository.get_by_event_type("order.confirmed")

        # Assert
        assert len(result) == 1
        assert result[0] == sample_subscription

    @pytest.mark.asyncio
    async def test_get_by_event_type_empty(self, repository):
        """Test getting subscriptions by event type when none exist."""
        # Act
        result = await repository.get_by_event_type("order.cancelled")

        # Assert
        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_get_active_subscriptions(self, repository, sample_subscription):
        """Test getting active subscriptions."""
        # Arrange
        await repository.save(sample_subscription)

        # Act
        result = await repository.get_active_subscriptions()

        # Assert
        assert len(result) == 1
        assert result[0] == sample_subscription

    @pytest.mark.asyncio
    async def test_get_active_subscriptions_inactive(self, repository):
        """Test getting active subscriptions when subscription is inactive."""
        # Arrange
        inactive_subscription = NotificationSubscription(
            id=NotificationId(value="sub-inactive"),
            user_id="user-123",
            event_type="order.confirmed",
            channels=[NotificationType.EMAIL],
            is_active=False,
            created_at=datetime.now(UTC)
        )
        await repository.save(inactive_subscription)

        # Act
        result = await repository.get_active_subscriptions()

        # Assert
        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_get_by_user_and_event_found(self, repository, sample_subscription):
        """Test getting subscription by user and event when it exists."""
        # Arrange
        await repository.save(sample_subscription)

        # Act
        result = await repository.get_by_user_and_event("user-123", "order.confirmed")

        # Assert
        assert result == sample_subscription

    @pytest.mark.asyncio
    async def test_get_by_user_and_event_not_found(self, repository):
        """Test getting subscription by user and event when it doesn't exist."""
        # Act
        result = await repository.get_by_user_and_event("user-999", "order.confirmed")

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_delete_subscription(self, repository, sample_subscription):
        """Test deleting a subscription."""
        # Arrange
        await repository.save(sample_subscription)

        # Act
        await repository.delete(sample_subscription.id)

        # Assert
        result = await repository.get_by_id(sample_subscription.id)
        assert result is None 