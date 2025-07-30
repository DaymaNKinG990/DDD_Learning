"""Tests for notifications domain."""


import pytest
from src.notifications.domain.entities import (
    Notification,
    NotificationBatch,
    NotificationSubscription,
)
from src.notifications.domain.value_objects import (
    NotificationId,
    NotificationRecipient,
    NotificationStatus,
    NotificationTemplate,
    NotificationType,
)


class TestNotification:
    """Test Notification entity."""

    def test_create_notification(self):
        """Test creating a notification."""
        recipient = NotificationRecipient(user_id="user-123", email="test@example.com")
        template = NotificationTemplate(
            name="order_confirmation",
            content="Ваш заказ {{order_id}} подтвержден и будет отправлен "
            "{{delivery_date}}."
        )

        notification = Notification(
            id=NotificationId(value="notif-123"),
            recipient=recipient,
            template=template,
            type=NotificationType.EMAIL,
            data={"order_id": "ORD-123", "delivery_date": "2024-01-15"}
        )

        assert notification.recipient.user_id == "user-123"
        assert notification.template.name == "order_confirmation"
        assert notification.type == NotificationType.EMAIL
        assert notification.status == NotificationStatus.PENDING
        assert notification.retry_count == 0

    def test_send_notification(self):
        """Test sending a notification."""
        recipient = NotificationRecipient(user_id="user-123", email="test@example.com")
        template = NotificationTemplate(
            name="test",
            content="Test content"
        )

        notification = Notification(
            id=NotificationId(value="notif-123"),
            recipient=recipient,
            template=template,
            type=NotificationType.EMAIL
        )

        notification.send()
        assert notification.status == NotificationStatus.SENT
        assert notification.sent_at is not None

    def test_deliver_notification(self):
        """Test delivering a notification."""
        recipient = NotificationRecipient(user_id="user-123", email="test@example.com")
        template = NotificationTemplate(
            name="test",
            content="Test content"
        )

        notification = Notification(
            id=NotificationId(value="notif-123"),
            recipient=recipient,
            template=template,
            type=NotificationType.EMAIL
        )

        notification.send()
        notification.deliver()
        assert notification.status == NotificationStatus.DELIVERED
        assert notification.delivered_at is not None

    def test_fail_notification(self):
        """Test failing a notification."""
        recipient = NotificationRecipient(user_id="user-123", email="test@example.com")
        template = NotificationTemplate(
            name="test",
            content="Test content"
        )

        notification = Notification(
            id=NotificationId(value="notif-123"),
            recipient=recipient,
            template=template,
            type=NotificationType.EMAIL
        )

        error_message = "SMTP connection failed"
        notification.fail(error_message)
        assert notification.status == NotificationStatus.FAILED
        assert notification.error_message == error_message

    def test_retry_notification(self):
        """Test retrying a notification."""
        recipient = NotificationRecipient(user_id="user-123", email="test@example.com")
        template = NotificationTemplate(
            name="test",
            content="Test content"
        )

        notification = Notification(
            id=NotificationId(value="notif-123"),
            recipient=recipient,
            template=template,
            type=NotificationType.EMAIL
        )

        notification.fail("Test error")
        assert notification.retry_count == 0

        # First retry
        assert notification.retry() is True
        assert notification.retry_count == 1
        assert notification.status == NotificationStatus.PENDING
        assert notification.error_message is None

        # Second retry
        notification.fail("Test error 2")
        assert notification.retry() is True
        assert notification.retry_count == 2

        # Third retry
        notification.fail("Test error 3")
        assert notification.retry() is True
        assert notification.retry_count == 3

        # Fourth retry should fail (max retries reached)
        notification.fail("Test error 4")
        assert notification.retry() is False
        assert notification.retry_count == 3

    def test_cancel_notification(self):
        """Test canceling a notification."""
        recipient = NotificationRecipient(user_id="user-123", email="test@example.com")
        template = NotificationTemplate(
            name="test",
            content="Test content"
        )

        notification = Notification(
            id=NotificationId(value="notif-123"),
            recipient=recipient,
            template=template,
            type=NotificationType.EMAIL
        )

        notification.cancel()
        assert notification.status == NotificationStatus.CANCELLED

    def test_status_checks(self):
        """Test status check methods."""
        recipient = NotificationRecipient(user_id="user-123", email="test@example.com")
        template = NotificationTemplate(
            name="test",
            content="Test content"
        )

        notification = Notification(
            id=NotificationId(value="notif-123"),
            recipient=recipient,
            template=template,
            type=NotificationType.EMAIL
        )

        assert notification.is_sent() is False
        assert notification.is_delivered() is False
        assert notification.is_failed() is False

        notification.send()
        assert notification.is_sent() is True
        assert notification.is_delivered() is False

        notification.deliver()
        assert notification.is_sent() is True  # DELIVERED implies SENT
        assert notification.is_delivered() is True

    def test_can_retry(self):
        """Test can_retry method."""
        recipient = NotificationRecipient(user_id="user-123", email="test@example.com")
        template = NotificationTemplate(
            name="test",
            content="Test content"
        )

        notification = Notification(
            id=NotificationId(value="notif-123"),
            recipient=recipient,
            template=template,
            type=NotificationType.EMAIL
        )

        # Not failed yet
        assert notification.can_retry() is False

        notification.fail("Test error")
        assert notification.can_retry() is True

        # Exhaust retries
        for _ in range(3):
            notification.retry()
            notification.fail("Test error")

        assert notification.can_retry() is False

    def test_render_content(self):
        """Test rendering notification content."""
        recipient = NotificationRecipient(user_id="user-123", email="test@example.com")
        template = NotificationTemplate(
            name="order_confirmation",
            content="Заказ {{order_id}} на сумму {{amount}} {{currency}} подтвержден."
        )

        notification = Notification(
            id=NotificationId(value="notif-123"),
            recipient=recipient,
            template=template,
            type=NotificationType.EMAIL,
            data={
                "order_id": "ORD-123",
                "amount": "1500",
                "currency": "RUB"
            }
        )

        rendered_content = notification.render_content()
        assert rendered_content == "Заказ ORD-123 на сумму 1500 RUB подтвержден."


class TestNotificationBatch:
    """Test NotificationBatch entity."""

    def test_create_notification_batch(self):
        """Test creating a notification batch."""
        recipients = [
            NotificationRecipient(user_id="user-1", email="user1@example.com"),
            NotificationRecipient(user_id="user-2", email="user2@example.com"),
        ]

        template = NotificationTemplate(
            name="newsletter",
            content="Новости недели: {{news}}"
        )

        batch = NotificationBatch(
            id=NotificationId(value="batch-123"),
            name="Weekly Newsletter",
            description="Еженедельная рассылка новостей",
            template=template,
            type=NotificationType.EMAIL,
            recipients=recipients,
            data={"news": "Новые поступления товаров"},
            total_count=2
        )

        assert batch.name == "Weekly Newsletter"
        assert batch.total_count == 2
        assert batch.sent_count == 0
        assert batch.failed_count == 0
        assert batch.status == "pending"

    def test_start_processing(self):
        """Test starting batch processing."""
        recipients = [
            NotificationRecipient(user_id="user-1", email="user1@example.com")
        ]
        template = NotificationTemplate(name="test", content="Test content")

        batch = NotificationBatch(
            id=NotificationId(value="batch-123"),
            name="Test Batch",
            template=template,
            type=NotificationType.EMAIL,
            recipients=recipients,
            total_count=1
        )

        batch.start_processing()
        assert batch.status == "processing"

    def test_complete_batch(self):
        """Test completing a batch."""
        recipients = [
            NotificationRecipient(user_id="user-1", email="user1@example.com")
        ]
        template = NotificationTemplate(name="test", content="Test content")

        batch = NotificationBatch(
            id=NotificationId(value="batch-123"),
            name="Test Batch",
            template=template,
            type=NotificationType.EMAIL,
            recipients=recipients,
            total_count=1
        )

        batch.complete()
        assert batch.status == "completed"
        assert batch.completed_at is not None

    def test_fail_batch(self):
        """Test failing a batch."""
        recipients = [
            NotificationRecipient(user_id="user-1", email="user1@example.com")
        ]
        template = NotificationTemplate(name="test", content="Test content")

        batch = NotificationBatch(
            id=NotificationId(value="batch-123"),
            name="Test Batch",
            template=template,
            type=NotificationType.EMAIL,
            recipients=recipients,
            total_count=1
        )

        batch.fail()
        assert batch.status == "failed"
        assert batch.completed_at is not None

    def test_increment_counts(self):
        """Test incrementing sent and failed counts."""
        recipients = [
            NotificationRecipient(user_id="user-1", email="user1@example.com")
        ]
        template = NotificationTemplate(name="test", content="Test content")

        batch = NotificationBatch(
            id=NotificationId(value="batch-123"),
            name="Test Batch",
            template=template,
            type=NotificationType.EMAIL,
            recipients=recipients,
            total_count=1
        )

        batch.increment_sent()
        assert batch.sent_count == 1

        batch.increment_failed()
        assert batch.failed_count == 1

    def test_get_progress(self):
        """Test getting batch progress."""
        recipients = [
            NotificationRecipient(user_id="user-1", email="user1@example.com")
        ]
        template = NotificationTemplate(name="test", content="Test content")

        batch = NotificationBatch(
            id=NotificationId(value="batch-123"),
            name="Test Batch",
            template=template,
            type=NotificationType.EMAIL,
            recipients=recipients,
            total_count=4
        )

        # 0% progress
        assert batch.get_progress() == 0.0

        # 25% progress
        batch.increment_sent()
        assert batch.get_progress() == 25.0

        # 50% progress
        batch.increment_sent()
        assert batch.get_progress() == 50.0

        # 75% progress
        batch.increment_failed()
        assert batch.get_progress() == 75.0

        # 100% progress
        batch.increment_sent()
        assert batch.get_progress() == 100.0

    def test_status_checks(self):
        """Test batch status checks."""
        recipients = [
            NotificationRecipient(user_id="user-1", email="user1@example.com")
        ]
        template = NotificationTemplate(name="test", content="Test content")

        batch = NotificationBatch(
            id=NotificationId(value="batch-123"),
            name="Test Batch",
            template=template,
            type=NotificationType.EMAIL,
            recipients=recipients,
            total_count=1
        )

        assert batch.is_completed() is False
        assert batch.is_failed() is False

        batch.complete()
        assert batch.is_completed() is True
        assert batch.is_failed() is False

        batch.fail()
        assert batch.is_completed() is False
        assert batch.is_failed() is True


class TestNotificationSubscription:
    """Test NotificationSubscription entity."""

    def test_create_subscription(self):
        """Test creating a notification subscription."""
        subscription = NotificationSubscription(
            id=NotificationId(value="sub-123"),
            user_id="user-123",
            event_type="order_status_changed",
            channels=[NotificationType.EMAIL, NotificationType.PUSH]
        )

        assert subscription.user_id == "user-123"
        assert subscription.event_type == "order_status_changed"
        assert len(subscription.channels) == 2
        assert subscription.is_active is True

    def test_activate_deactivate(self):
        """Test activating and deactivating subscription."""
        subscription = NotificationSubscription(
            id=NotificationId(value="sub-123"),
            user_id="user-123",
            event_type="order_status_changed",
            channels=[NotificationType.EMAIL]
        )

        assert subscription.is_active is True

        subscription.deactivate()
        assert subscription.is_active is False

        subscription.activate()
        assert subscription.is_active is True

    def test_add_remove_channel(self):
        """Test adding and removing channels."""
        subscription = NotificationSubscription(
            id=NotificationId(value="sub-123"),
            user_id="user-123",
            event_type="order_status_changed",
            channels=[NotificationType.EMAIL]
        )

        assert len(subscription.channels) == 1
        assert NotificationType.EMAIL in subscription.channels

        subscription.add_channel(NotificationType.PUSH)
        assert len(subscription.channels) == 2
        assert NotificationType.PUSH in subscription.channels

        subscription.remove_channel(NotificationType.EMAIL)
        assert len(subscription.channels) == 1
        assert NotificationType.EMAIL not in subscription.channels
        assert NotificationType.PUSH in subscription.channels

    def test_supports_channel(self):
        """Test checking if subscription supports channel."""
        subscription = NotificationSubscription(
            id=NotificationId(value="sub-123"),
            user_id="user-123",
            event_type="order_status_changed",
            channels=[NotificationType.EMAIL, NotificationType.SMS]
        )

        assert subscription.supports_channel(NotificationType.EMAIL) is True
        assert subscription.supports_channel(NotificationType.SMS) is True
        assert subscription.supports_channel(NotificationType.PUSH) is False


class TestValueObjects:
    """Test notifications value objects."""

    def test_notification_template_validation(self):
        """Test notification template validation."""
        # Valid template
        template = NotificationTemplate(
            name="order_confirmation",
            content="Ваш заказ {{order_id}} подтвержден."
        )
        assert template.name == "order_confirmation"
        assert template.content == "Ваш заказ {{order_id}} подтвержден."

        # Invalid name (too short)
        with pytest.raises(ValueError, match="at least 3 characters"):
            NotificationTemplate(
                name="ab",
                content="Test content"
            )

        # Invalid content (too short)
        with pytest.raises(ValueError, match="at least 10 characters"):
            NotificationTemplate(
                name="test",
                content="Short"
            )

    def test_notification_template_render(self):
        """Test notification template rendering."""
        template = NotificationTemplate(
            name="welcome",
            content="Добро пожаловать, {{name}}! Ваш аккаунт создан {{date}}."
        )

        data = {
            "name": "Иван",
            "date": "2024-01-15"
        }

        rendered = template.render(data)
        assert rendered == "Добро пожаловать, Иван! Ваш аккаунт создан 2024-01-15."

    def test_notification_recipient_validation(self):
        """Test notification recipient validation."""
        # Valid recipient
        recipient = NotificationRecipient(
            user_id="user-123",
            email="test@example.com"
        )
        assert recipient.user_id == "user-123"
        assert recipient.email == "test@example.com"

        # Invalid email
        with pytest.raises(ValueError, match="Invalid email format"):
            NotificationRecipient(
                user_id="user-123",
                email="invalid-email"
            )

    def test_notification_recipient_preferences(self):
        """Test notification recipient preferences."""
        recipient = NotificationRecipient(
            user_id="user-123",
            email="test@example.com"
        )

        # Default preferences
        assert recipient.can_receive(NotificationType.EMAIL) is True
        assert recipient.can_receive(NotificationType.SMS) is True

        # Update preferences
        recipient = recipient.update_preference(NotificationType.EMAIL, False)
        assert recipient.can_receive(NotificationType.EMAIL) is False
        assert recipient.can_receive(NotificationType.SMS) is True

        recipient = recipient.update_preference(NotificationType.SMS, False)
        assert recipient.can_receive(NotificationType.SMS) is False
