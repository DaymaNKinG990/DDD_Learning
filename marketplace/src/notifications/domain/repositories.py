"""Repository interfaces for notifications domain."""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional

from src.notifications.domain.entities import (
    Notification,
    NotificationBatch,
    NotificationSubscription,
)
from src.notifications.domain.value_objects import (
    NotificationId,
    NotificationStatus,
    NotificationType,
)


class NotificationRepository(ABC):
    """Repository interface for Notification entity."""

    @abstractmethod
    async def save(self, notification: Notification) -> Notification:
        """Save a notification."""
        pass

    @abstractmethod
    async def get_by_id(self, notification_id: NotificationId) -> Optional[Notification]:
        """Get notification by ID."""
        pass

    @abstractmethod
    async def get_by_status(self, status: NotificationStatus) -> List[Notification]:
        """Get notifications by status."""
        pass

    @abstractmethod
    async def get_by_recipient(self, user_id: str) -> List[Notification]:
        """Get notifications by recipient user ID."""
        pass

    @abstractmethod
    async def get_by_type(self, notification_type: NotificationType) -> List[Notification]:
        """Get notifications by type."""
        pass

    @abstractmethod
    async def get_pending_notifications(self) -> List[Notification]:
        """Get all pending notifications."""
        pass

    @abstractmethod
    async def get_failed_notifications(self) -> List[Notification]:
        """Get all failed notifications."""
        pass

    @abstractmethod
    async def get_scheduled_notifications(self, before: datetime) -> List[Notification]:
        """Get notifications scheduled before a specific time."""
        pass

    @abstractmethod
    async def delete(self, notification_id: NotificationId) -> None:
        """Delete a notification."""
        pass


class NotificationBatchRepository(ABC):
    """Repository interface for NotificationBatch entity."""

    @abstractmethod
    async def save(self, batch: NotificationBatch) -> NotificationBatch:
        """Save a notification batch."""
        pass

    @abstractmethod
    async def get_by_id(self, batch_id: NotificationId) -> Optional[NotificationBatch]:
        """Get batch by ID."""
        pass

    @abstractmethod
    async def get_by_status(self, status: str) -> List[NotificationBatch]:
        """Get batches by status."""
        pass

    @abstractmethod
    async def get_pending_batches(self) -> List[NotificationBatch]:
        """Get all pending batches."""
        pass

    @abstractmethod
    async def get_processing_batches(self) -> List[NotificationBatch]:
        """Get all processing batches."""
        pass

    @abstractmethod
    async def delete(self, batch_id: NotificationId) -> None:
        """Delete a batch."""
        pass


class NotificationSubscriptionRepository(ABC):
    """Repository interface for NotificationSubscription entity."""

    @abstractmethod
    async def save(self, subscription: NotificationSubscription) -> NotificationSubscription:
        """Save a notification subscription."""
        pass

    @abstractmethod
    async def get_by_id(self, subscription_id: NotificationId) -> Optional[NotificationSubscription]:
        """Get subscription by ID."""
        pass

    @abstractmethod
    async def get_by_user_id(self, user_id: str) -> List[NotificationSubscription]:
        """Get subscriptions by user ID."""
        pass

    @abstractmethod
    async def get_by_event_type(self, event_type: str) -> List[NotificationSubscription]:
        """Get subscriptions by event type."""
        pass

    @abstractmethod
    async def get_active_subscriptions(self) -> List[NotificationSubscription]:
        """Get all active subscriptions."""
        pass

    @abstractmethod
    async def get_by_user_and_event(
        self, user_id: str, event_type: str
    ) -> Optional[NotificationSubscription]:
        """Get subscription by user ID and event type."""
        pass

    @abstractmethod
    async def delete(self, subscription_id: NotificationId) -> None:
        """Delete a subscription."""
        pass 