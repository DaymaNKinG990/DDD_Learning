"""Tests for notifications queries."""

import pytest
from datetime import datetime, UTC
from unittest.mock import AsyncMock

from src.notifications.application.queries import (
    NotificationQueryHandler, NotificationBatchQueryHandler, NotificationSubscriptionQueryHandler,
    GetNotificationQuery, GetNotificationsByUserQuery, GetNotificationsByStatusQuery,
    GetNotificationsByTypeQuery, GetScheduledNotificationsQuery, GetBatchQuery,
    GetBatchesByStatusQuery, GetSubscriptionQuery, GetSubscriptionsByUserQuery,
    GetSubscriptionsByEventTypeQuery, NotificationReadModel, NotificationBatchReadModel,
    NotificationSubscriptionReadModel
)
from src.notifications.domain.value_objects import NotificationStatus, NotificationType


class InMemoryNotificationQueryHandler(NotificationQueryHandler):
    """In-memory implementation of NotificationQueryHandler for testing."""

    def __init__(self):
        """Initialize the in-memory query handler."""
        self._notifications = {}

    def add_notification(self, notification: NotificationReadModel):
        """Add a notification to the in-memory storage."""
        self._notifications[notification.id] = notification

    async def get_notification(self, query: GetNotificationQuery) -> NotificationReadModel | None:
        """Get notification by ID."""
        return self._notifications.get(query.notification_id)

    async def get_notifications_by_user(self, query: GetNotificationsByUserQuery) -> list[NotificationReadModel]:
        """Get notifications by user ID."""
        notifications = [
            n for n in self._notifications.values()
            if n.recipient_user_id == query.user_id
        ]
        
        if query.status:
            notifications = [n for n in notifications if n.status == query.status.value]
        if query.notification_type:
            notifications = [n for n in notifications if n.notification_type == query.notification_type.value]
        
        # Sort by created_at desc (newest first)
        notifications.sort(key=lambda x: x.created_at, reverse=True)
        
        start = query.offset
        end = start + query.limit
        return notifications[start:end]

    async def get_notifications_by_status(self, query: GetNotificationsByStatusQuery) -> list[NotificationReadModel]:
        """Get notifications by status."""
        notifications = [
            n for n in self._notifications.values()
            if n.status == query.status.value
        ]
        
        # Sort by created_at desc (newest first)
        notifications.sort(key=lambda x: x.created_at, reverse=True)
        
        start = query.offset
        end = start + query.limit
        return notifications[start:end]

    async def get_notifications_by_type(self, query: GetNotificationsByTypeQuery) -> list[NotificationReadModel]:
        """Get notifications by type."""
        notifications = [
            n for n in self._notifications.values()
            if n.notification_type == query.notification_type.value
        ]
        
        if query.status:
            notifications = [n for n in notifications if n.status == query.status.value]
        
        # Sort by created_at desc (newest first)
        notifications.sort(key=lambda x: x.created_at, reverse=True)
        
        start = query.offset
        end = start + query.limit
        return notifications[start:end]

    async def get_scheduled_notifications(self, query: GetScheduledNotificationsQuery) -> list[NotificationReadModel]:
        """Get scheduled notifications."""
        notifications = [
            n for n in self._notifications.values()
            if n.scheduled_at and n.scheduled_at <= query.before
        ]
        
        # Sort by scheduled_at asc (earliest first)
        notifications.sort(key=lambda x: x.scheduled_at)
        
        start = query.offset
        end = start + query.limit
        return notifications[start:end]


class InMemoryNotificationBatchQueryHandler(NotificationBatchQueryHandler):
    """In-memory implementation of NotificationBatchQueryHandler for testing."""

    def __init__(self):
        """Initialize the in-memory query handler."""
        self._batches = {}

    def add_batch(self, batch: NotificationBatchReadModel):
        """Add a batch to the in-memory storage."""
        self._batches[batch.id] = batch

    async def get_batch(self, query: GetBatchQuery) -> NotificationBatchReadModel | None:
        """Get batch by ID."""
        return self._batches.get(query.batch_id)

    async def get_batches_by_status(self, query: GetBatchesByStatusQuery) -> list[NotificationBatchReadModel]:
        """Get batches by status."""
        batches = [
            b for b in self._batches.values()
            if b.status == query.status
        ]
        
        # Sort by created_at desc (newest first)
        batches.sort(key=lambda x: x.created_at, reverse=True)
        
        start = query.offset
        end = start + query.limit
        return batches[start:end]


class InMemoryNotificationSubscriptionQueryHandler(NotificationSubscriptionQueryHandler):
    """In-memory implementation of NotificationSubscriptionQueryHandler for testing."""

    def __init__(self):
        """Initialize the in-memory query handler."""
        self._subscriptions = {}

    def add_subscription(self, subscription: NotificationSubscriptionReadModel):
        """Add a subscription to the in-memory storage."""
        self._subscriptions[subscription.id] = subscription

    async def get_subscription(self, query: GetSubscriptionQuery) -> NotificationSubscriptionReadModel | None:
        """Get subscription by ID."""
        return self._subscriptions.get(query.subscription_id)

    async def get_subscriptions_by_user(self, query: GetSubscriptionsByUserQuery) -> list[NotificationSubscriptionReadModel]:
        """Get subscriptions by user ID."""
        subscriptions = [
            s for s in self._subscriptions.values()
            if s.user_id == query.user_id
        ]
        
        if query.is_active is not None:
            subscriptions = [s for s in subscriptions if s.is_active == query.is_active]
        
        # Sort by created_at desc (newest first)
        subscriptions.sort(key=lambda x: x.created_at, reverse=True)
        
        start = query.offset
        end = start + query.limit
        return subscriptions[start:end]

    async def get_subscriptions_by_event_type(self, query: GetSubscriptionsByEventTypeQuery) -> list[NotificationSubscriptionReadModel]:
        """Get subscriptions by event type."""
        subscriptions = [
            s for s in self._subscriptions.values()
            if s.event_type == query.event_type
        ]
        
        if query.is_active is not None:
            subscriptions = [s for s in subscriptions if s.is_active == query.is_active]
        
        # Sort by created_at desc (newest first)
        subscriptions.sort(key=lambda x: x.created_at, reverse=True)
        
        start = query.offset
        end = start + query.limit
        return subscriptions[start:end]


class TestNotificationQueryHandler:
    """Test NotificationQueryHandler."""

    @pytest.fixture
    def handler(self):
        """Create notification query handler."""
        return InMemoryNotificationQueryHandler()

    @pytest.fixture
    def sample_notification(self):
        """Create sample notification read model."""
        return NotificationReadModel(
            id="notification_123",
            recipient_user_id="user_123",
            recipient_email="test@example.com",
            template_name="welcome_email",
            template_content="Welcome {{name}}!",
            notification_type="EMAIL",
            priority="NORMAL",
            status="PENDING",
            data={"name": "John Doe"},
            scheduled_at=None,
            sent_at=None,
            delivered_at=None,
            retry_count=0,
            max_retries=3,
            error_message=None,
            metadata={},
            created_at=datetime.now(UTC)
        )

    @pytest.mark.asyncio
    async def test_get_notification_found(self, handler, sample_notification):
        """Test getting notification that exists."""
        # Arrange
        handler.add_notification(sample_notification)
        query = GetNotificationQuery(notification_id="notification_123")

        # Act
        result = await handler.get_notification(query)

        # Assert
        assert result == sample_notification

    @pytest.mark.asyncio
    async def test_get_notification_not_found(self, handler):
        """Test getting notification that doesn't exist."""
        # Arrange
        query = GetNotificationQuery(notification_id="nonexistent")

        # Act
        result = await handler.get_notification(query)

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_get_notifications_by_user(self, handler):
        """Test getting notifications by user."""
        # Arrange
        notifications = [
            NotificationReadModel(
                id=f"notification_{i}",
                recipient_user_id="user_123",
                recipient_email="test@example.com",
                template_name="welcome_email",
                template_content="Welcome {{name}}!",
                notification_type="EMAIL",
                priority="NORMAL",
                status="PENDING",
                data={"name": "John Doe"},
                scheduled_at=None,
                sent_at=None,
                delivered_at=None,
                retry_count=0,
                max_retries=3,
                error_message=None,
                metadata={},
                created_at=datetime(2024, 1, 1 + i, tzinfo=UTC)
            )
            for i in range(5)
        ]
        for notification in notifications:
            handler.add_notification(notification)

        query = GetNotificationsByUserQuery(user_id="user_123", limit=3, offset=1)

        # Act
        result = await handler.get_notifications_by_user(query)

        # Assert
        assert len(result) == 3
        # Since sorted by created_at desc, with offset=1, limit=3: notification_3, notification_2, notification_1
        assert result[0].id == "notification_3"
        assert result[1].id == "notification_2"
        assert result[2].id == "notification_1"

    @pytest.mark.asyncio
    async def test_get_notifications_by_status(self, handler):
        """Test getting notifications by status."""
        # Arrange
        notifications = [
            NotificationReadModel(
                id=f"notification_{i}",
                recipient_user_id="user_123",
                recipient_email="test@example.com",
                template_name="welcome_email",
                template_content="Welcome {{name}}!",
                notification_type="EMAIL",
                priority="NORMAL",
                status=NotificationStatus.PENDING.value if i % 2 == 0 else NotificationStatus.SENT.value,
                data={"name": "John Doe"},
                scheduled_at=None,
                sent_at=None,
                delivered_at=None,
                retry_count=0,
                max_retries=3,
                error_message=None,
                metadata={},
                created_at=datetime(2024, 1, 1 + i, tzinfo=UTC)
            )
            for i in range(6)
        ]
        for notification in notifications:
            handler.add_notification(notification)

        query = GetNotificationsByStatusQuery(status=NotificationStatus.PENDING, limit=2, offset=1)

        # Act
        result = await handler.get_notifications_by_status(query)

        # Assert
        assert len(result) == 2
        # PENDING notifications: notification_0, notification_2, notification_4
        # With offset=1, limit=2: notification_2, notification_0
        assert result[0].id == "notification_2"
        assert result[1].id == "notification_0"

    @pytest.mark.asyncio
    async def test_get_notifications_by_type(self, handler):
        """Test getting notifications by type."""
        # Arrange
        notifications = [
            NotificationReadModel(
                id=f"notification_{i}",
                recipient_user_id="user_123",
                recipient_email="test@example.com",
                template_name="welcome_email",
                template_content="Welcome {{name}}!",
                notification_type=NotificationType.EMAIL.value if i % 2 == 0 else NotificationType.SMS.value,
                priority="NORMAL",
                status="PENDING",
                data={"name": "John Doe"},
                scheduled_at=None,
                sent_at=None,
                delivered_at=None,
                retry_count=0,
                max_retries=3,
                error_message=None,
                metadata={},
                created_at=datetime(2024, 1, 1 + i, tzinfo=UTC)
            )
            for i in range(6)
        ]
        for notification in notifications:
            handler.add_notification(notification)

        query = GetNotificationsByTypeQuery(notification_type=NotificationType.EMAIL, limit=2, offset=1)

        # Act
        result = await handler.get_notifications_by_type(query)

        # Assert
        assert len(result) == 2
        # EMAIL notifications: notification_0, notification_2, notification_4
        # With offset=1, limit=2: notification_2, notification_0
        assert result[0].id == "notification_2"
        assert result[1].id == "notification_0"

    @pytest.mark.asyncio
    async def test_get_scheduled_notifications(self, handler):
        """Test getting scheduled notifications."""
        # Arrange
        base_time = datetime(2024, 1, 1, 12, 0, 0, tzinfo=UTC)
        notifications = [
            NotificationReadModel(
                id=f"notification_{i}",
                recipient_user_id="user_123",
                recipient_email="test@example.com",
                template_name="welcome_email",
                template_content="Welcome {{name}}!",
                notification_type="EMAIL",
                priority="NORMAL",
                status="PENDING",
                data={"name": "John Doe"},
                scheduled_at=base_time.replace(hour=10 + i),  # 10:00, 11:00, 12:00, 13:00, 14:00
                sent_at=None,
                delivered_at=None,
                retry_count=0,
                max_retries=3,
                error_message=None,
                metadata={},
                created_at=datetime.now(UTC)
            )
            for i in range(5)
        ]
        for notification in notifications:
            handler.add_notification(notification)

        query = GetScheduledNotificationsQuery(before=base_time.replace(hour=13), limit=2, offset=1)

        # Act
        result = await handler.get_scheduled_notifications(query)

        # Assert
        assert len(result) == 2
        # Scheduled before 13:00: notification_0 (10:00), notification_1 (11:00), notification_2 (12:00)
        # Sorted by scheduled_at asc, with offset=1, limit=2: notification_1 (11:00), notification_2 (12:00)
        assert result[0].id == "notification_1"
        assert result[1].id == "notification_2"


class TestNotificationBatchQueryHandler:
    """Test NotificationBatchQueryHandler."""

    @pytest.fixture
    def handler(self):
        """Create batch query handler."""
        return InMemoryNotificationBatchQueryHandler()

    @pytest.fixture
    def sample_batch(self):
        """Create sample batch read model."""
        return NotificationBatchReadModel(
            id="batch_123",
            name="Welcome Batch",
            template_name="welcome_email",
            template_content="Welcome {{name}}!",
            notification_type="EMAIL",
            total_count=10,
            sent_count=5,
            failed_count=1,
            description="Welcome emails for new users",
            priority="NORMAL",
            data={"welcome_message": "Welcome!"},
            scheduled_at=None,
            status="PROCESSING",
            created_at=datetime.now(UTC),
            completed_at=None
        )

    @pytest.mark.asyncio
    async def test_get_batch_found(self, handler, sample_batch):
        """Test getting batch that exists."""
        # Arrange
        handler.add_batch(sample_batch)
        query = GetBatchQuery(batch_id="batch_123")

        # Act
        result = await handler.get_batch(query)

        # Assert
        assert result == sample_batch

    @pytest.mark.asyncio
    async def test_get_batch_not_found(self, handler):
        """Test getting batch that doesn't exist."""
        # Arrange
        query = GetBatchQuery(batch_id="nonexistent")

        # Act
        result = await handler.get_batch(query)

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_get_batches_by_status(self, handler):
        """Test getting batches by status."""
        # Arrange
        batches = [
            NotificationBatchReadModel(
                id=f"batch_{i}",
                name=f"Batch {i}",
                template_name="welcome_email",
                template_content="Welcome {{name}}!",
                notification_type="EMAIL",
                total_count=10,
                sent_count=5,
                failed_count=1,
                description="Test batch",
                priority="NORMAL",
                data={},
                scheduled_at=None,
                status="PROCESSING" if i % 2 == 0 else "COMPLETED",
                created_at=datetime(2024, 1, 1 + i, tzinfo=UTC),
                completed_at=None
            )
            for i in range(6)
        ]
        for batch in batches:
            handler.add_batch(batch)

        query = GetBatchesByStatusQuery(status="PROCESSING", limit=2, offset=1)

        # Act
        result = await handler.get_batches_by_status(query)

        # Assert
        assert len(result) == 2
        # PROCESSING batches: batch_0, batch_2, batch_4
        # With offset=1, limit=2: batch_2, batch_0
        assert result[0].id == "batch_2"
        assert result[1].id == "batch_0"


class TestNotificationSubscriptionQueryHandler:
    """Test NotificationSubscriptionQueryHandler."""

    @pytest.fixture
    def handler(self):
        """Create subscription query handler."""
        return InMemoryNotificationSubscriptionQueryHandler()

    @pytest.fixture
    def sample_subscription(self):
        """Create sample subscription read model."""
        return NotificationSubscriptionReadModel(
            id="subscription_123",
            user_id="user_123",
            event_type="order_created",
            channels=["EMAIL", "SMS"],
            is_active=True,
            created_at=datetime.now(UTC),
            updated_at=None
        )

    @pytest.mark.asyncio
    async def test_get_subscription_found(self, handler, sample_subscription):
        """Test getting subscription that exists."""
        # Arrange
        handler.add_subscription(sample_subscription)
        query = GetSubscriptionQuery(subscription_id="subscription_123")

        # Act
        result = await handler.get_subscription(query)

        # Assert
        assert result == sample_subscription

    @pytest.mark.asyncio
    async def test_get_subscription_not_found(self, handler):
        """Test getting subscription that doesn't exist."""
        # Arrange
        query = GetSubscriptionQuery(subscription_id="nonexistent")

        # Act
        result = await handler.get_subscription(query)

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_get_subscriptions_by_user(self, handler):
        """Test getting subscriptions by user."""
        # Arrange
        subscriptions = [
            NotificationSubscriptionReadModel(
                id=f"subscription_{i}",
                user_id="user_123" if i % 2 == 0 else "user_456",
                event_type="order_created",
                channels=["EMAIL"],
                is_active=True if i % 3 == 0 else False,
                created_at=datetime(2024, 1, 1 + i, tzinfo=UTC),
                updated_at=None
            )
            for i in range(6)
        ]
        for subscription in subscriptions:
            handler.add_subscription(subscription)

        query = GetSubscriptionsByUserQuery(user_id="user_123", is_active=True, limit=2, offset=0)

        # Act
        result = await handler.get_subscriptions_by_user(query)

        # Assert
        assert len(result) == 1  # Only subscription_0 matches both user_123 and is_active=True
        assert result[0].id == "subscription_0"

    @pytest.mark.asyncio
    async def test_get_subscriptions_by_event_type(self, handler):
        """Test getting subscriptions by event type."""
        # Arrange
        subscriptions = [
            NotificationSubscriptionReadModel(
                id=f"subscription_{i}",
                user_id="user_123",
                event_type="order_created" if i % 2 == 0 else "payment_received",
                channels=["EMAIL"],
                is_active=True,
                created_at=datetime(2024, 1, 1 + i, tzinfo=UTC),
                updated_at=None
            )
            for i in range(6)
        ]
        for subscription in subscriptions:
            handler.add_subscription(subscription)

        query = GetSubscriptionsByEventTypeQuery(event_type="order_created", limit=2, offset=1)

        # Act
        result = await handler.get_subscriptions_by_event_type(query)

        # Assert
        assert len(result) == 2
        # order_created subscriptions: subscription_0, subscription_2, subscription_4
        # With offset=1, limit=2: subscription_2, subscription_0
        assert result[0].id == "subscription_2"
        assert result[1].id == "subscription_0" 