"""Repository interfaces for notifications domain."""

# Python imports
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional

# Local imports
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
    """
    Repository interface for Notification entity.
    
    This interface defines the methods for saving, retrieving, and deleting notifications.
    """

    @abstractmethod
    async def save(self, notification: Notification) -> Notification:
        """
        Save a notification.
        
        Args:
            notification (Notification): The notification to save.

        Returns:
            Notification: The saved notification.
        """
        pass

    @abstractmethod
    async def get_by_id(self, notification_id: NotificationId) -> Optional[Notification]:
        """
        Get notification by ID.
        
        Args:
            notification_id (NotificationId): The ID of the notification to retrieve.

        Returns:
            Optional[Notification]: The notification if found, None otherwise.
        """
        pass

    @abstractmethod
    async def get_by_status(self, status: NotificationStatus) -> List[Notification]:
        """
        Get notifications by status.
        
        Args:
            status (NotificationStatus): The status of the notifications to retrieve.

        Returns:
            List[Notification]: The notifications with the specified status.
        """
        pass

    @abstractmethod
    async def get_by_recipient(self, user_id: str) -> List[Notification]:
        """
        Get notifications by recipient user ID.
        
        Args:
            user_id (str): The ID of the user to retrieve notifications for.

        Returns:
            List[Notification]: The notifications for the specified user.
        """
        pass

    @abstractmethod
    async def get_by_type(self, notification_type: NotificationType) -> List[Notification]:
        """
        Get notifications by type.
        
        Args:
            notification_type (NotificationType): The type of the notifications to retrieve.

        Returns:
            List[Notification]: The notifications with the specified type.
        """
        pass

    @abstractmethod
    async def get_pending_notifications(self) -> List[Notification]:
        """
        Get all pending notifications.
        
        Returns:
            List[Notification]: All pending notifications.
        """
        pass

    @abstractmethod
    async def get_failed_notifications(self) -> List[Notification]:
        """
        Get all failed notifications.
        
        Returns:
            List[Notification]: All failed notifications.
        """
        pass

    @abstractmethod
    async def get_scheduled_notifications(self, before: datetime) -> List[Notification]:
        """
        Get notifications scheduled before a specific time.
        
        Args:
            before (datetime): The time before which the notifications were scheduled.

        Returns:
            List[Notification]: The notifications scheduled before the specified time.
        """
        pass

    @abstractmethod
    async def delete(self, notification_id: NotificationId) -> None:
        """
        Delete a notification.
        
        Args:
            notification_id (NotificationId): The ID of the notification to delete.
        """
        pass


class NotificationBatchRepository(ABC):
    """
    Repository interface for NotificationBatch entity.
    
    This interface defines the methods for saving, retrieving, and deleting notification batches.
    """

    @abstractmethod
    async def save(self, batch: NotificationBatch) -> NotificationBatch:
        """
        Save a notification batch.
        
        Args:
            batch (NotificationBatch): The notification batch to save.

        Returns:
            NotificationBatch: The saved notification batch.
        """
        pass

    @abstractmethod
    async def get_by_id(self, batch_id: NotificationId) -> Optional[NotificationBatch]:
        """
        Get batch by ID.
        
        Args:
            batch_id (NotificationId): The ID of the notification batch to retrieve.

        Returns:
            Optional[NotificationBatch]: The notification batch if found, None otherwise.
        """
        pass

    @abstractmethod
    async def get_by_status(self, status: str) -> List[NotificationBatch]:
        """
        Get batches by status.
        
        Args:
            status (str): The status of the notification batches to retrieve.

        Returns:
            List[NotificationBatch]: The notification batches with the specified status.
        """
        pass

    @abstractmethod
    async def get_pending_batches(self) -> List[NotificationBatch]:
        """
        Get all pending batches.
        
        Returns:
            List[NotificationBatch]: All pending notification batches.
        """
        pass

    @abstractmethod
    async def get_processing_batches(self) -> List[NotificationBatch]:
        """
        Get all processing batches.
        
        Returns:
            List[NotificationBatch]: All processing notification batches.
        """
        pass

    @abstractmethod
    async def delete(self, batch_id: NotificationId) -> None:
        """
        Delete a notification batch.
        
        Args:
            batch_id (NotificationId): The ID of the notification batch to delete.
        """
        pass


class NotificationSubscriptionRepository(ABC):
    """
    Repository interface for NotificationSubscription entity.
    
    This interface defines the methods for saving, retrieving, and deleting notification subscriptions.
    """

    @abstractmethod
    async def save(self, subscription: NotificationSubscription) -> NotificationSubscription:
        """
        Save a notification subscription.
        
        Args:
            subscription (NotificationSubscription): The notification subscription to save.

        Returns:
            NotificationSubscription: The saved notification subscription.
        """
        pass

    @abstractmethod
    async def get_by_id(self, subscription_id: NotificationId) -> Optional[NotificationSubscription]:
        """
        Get subscription by ID.
        
        Args:
            subscription_id (NotificationId): The ID of the notification subscription to retrieve.

        Returns:
            Optional[NotificationSubscription]: The notification subscription if found, None otherwise.
        """
        pass

    @abstractmethod
    async def get_by_user_id(self, user_id: str) -> List[NotificationSubscription]:
        """
        Get subscriptions by user ID.
        
        Args:
            user_id (str): The ID of the user to retrieve subscriptions for.

        Returns:
            List[NotificationSubscription]: The subscriptions for the specified user.
        """
        pass

    @abstractmethod
    async def get_by_event_type(self, event_type: str) -> List[NotificationSubscription]:
        """
        Get subscriptions by event type.
        
        Args:
            event_type (str): The type of the event to retrieve subscriptions for.

        Returns:
            List[NotificationSubscription]: The subscriptions for the specified event type.
        """
        pass

    @abstractmethod
    async def get_active_subscriptions(self) -> List[NotificationSubscription]:
        """
        Get all active subscriptions.
        
        Returns:
            List[NotificationSubscription]: All active notification subscriptions.
        """
        pass

    @abstractmethod
    async def get_by_user_and_event(
        self,
        user_id: str,
        event_type: str
    ) -> Optional[NotificationSubscription]:
        """
        Get subscription by user ID and event type.
        
        Args:
            user_id (str): The ID of the user to retrieve the subscription for.
            event_type (str): The type of the event to retrieve the subscription for.

        Returns:
            Optional[NotificationSubscription]: The subscription if found, None otherwise.
        """
        pass

    @abstractmethod
    async def delete(self, subscription_id: NotificationId) -> None:
        """
        Delete a notification subscription.
        
        Args:
            subscription_id (NotificationId): The ID of the notification subscription to delete.
        """
        pass 