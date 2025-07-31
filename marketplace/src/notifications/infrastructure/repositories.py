"""In-memory repositories for notifications domain."""

# Python imports
from datetime import datetime
from typing import Dict, List, Optional

# Local imports
from src.notifications.domain.entities import (
    Notification,
    NotificationBatch,
    NotificationSubscription,
)
from src.notifications.domain.repositories import (
    NotificationRepository,
    NotificationBatchRepository,
    NotificationSubscriptionRepository,
)
from src.notifications.domain.value_objects import (
    NotificationId,
    NotificationStatus,
    NotificationType,
)


class InMemoryNotificationRepository(NotificationRepository):
    """
    In-memory implementation of NotificationRepository.
    
    This class provides an in-memory implementation of the NotificationRepository interface.
    """

    def __init__(self) -> None:
        """Initialize the in-memory notification repository."""
        self._notifications: Dict[str, Notification] = {}
        self._notifications_by_status: Dict[NotificationStatus, List[Notification]] = {}
        self._notifications_by_recipient: Dict[str, List[Notification]] = {}
        self._notifications_by_type: Dict[NotificationType, List[Notification]] = {}

    async def save(self, notification: Notification) -> Notification:
        """
        Save a notification.
        
        Args:
            notification (Notification): The notification to save.

        Returns:
            Notification: The saved notification.
        """
        notification_id_str = str(notification.id)
        self._notifications[notification_id_str] = notification

        # Update indexes
        if notification.status not in self._notifications_by_status:
            self._notifications_by_status[notification.status] = []
        self._notifications_by_status[notification.status].append(notification)

        recipient_user_id = notification.recipient.user_id
        if recipient_user_id not in self._notifications_by_recipient:
            self._notifications_by_recipient[recipient_user_id] = []
        self._notifications_by_recipient[recipient_user_id].append(notification)

        if notification.type not in self._notifications_by_type:
            self._notifications_by_type[notification.type] = []
        self._notifications_by_type[notification.type].append(notification)

        return notification

    async def get_by_id(self, notification_id: NotificationId) -> Optional[Notification]:
        """
        Get notification by ID.
        
        Args:
            notification_id (NotificationId): The ID of the notification to get.

        Returns:
            Optional[Notification]: The notification if found, None otherwise.
        """
        return self._notifications.get(str(notification_id))

    async def get_by_status(self, status: NotificationStatus) -> List[Notification]:
        """
        Get notifications by status.
        
        Args:
            status (NotificationStatus): The status of the notifications to get.

        Returns:
            List[Notification]: The notifications with the given status.
        """
        return self._notifications_by_status.get(status, [])

    async def get_by_recipient(self, user_id: str) -> List[Notification]:
        """
        Get notifications by recipient user ID.
        
        Args:
            user_id (str): The ID of the recipient user.

        Returns:
            List[Notification]: The notifications for the given recipient user ID.
        """
        return self._notifications_by_recipient.get(user_id, [])

    async def get_by_type(self, notification_type: NotificationType) -> List[Notification]:
        """
        Get notifications by type.
        
        Args:
            notification_type (NotificationType): The type of the notifications to get.

        Returns:
            List[Notification]: The notifications with the given type.
        """
        return self._notifications_by_type.get(notification_type, [])

    async def get_pending_notifications(self) -> List[Notification]:
        """
        Get all pending notifications.
        
        Returns:
            List[Notification]: The pending notifications.
        """
        return self._notifications_by_status.get(NotificationStatus.PENDING, [])

    async def get_failed_notifications(self) -> List[Notification]:
        """
        Get all failed notifications.
        
        Returns:
            List[Notification]: The failed notifications.
        """
        return self._notifications_by_status.get(NotificationStatus.FAILED, [])

    async def get_scheduled_notifications(self, before: datetime) -> List[Notification]:
        """
        Get notifications scheduled before a specific time.
        
        Args:
            before (datetime): The time before which the notifications were scheduled.

        Returns:
            List[Notification]: The scheduled notifications.
        """
        scheduled_notifications = []
        for notification in self._notifications.values():
            if (
                notification.scheduled_at 
                and notification.scheduled_at <= before
                and notification.status == NotificationStatus.PENDING
            ):
                scheduled_notifications.append(notification)
        return scheduled_notifications

    async def delete(self, notification_id: NotificationId) -> None:
        """
        Delete a notification.
        
        Args:
            notification_id (NotificationId): The ID of the notification to delete.
        """
        notification_id_str = str(notification_id)
        if notification_id_str in self._notifications:
            notification = self._notifications[notification_id_str]
            del self._notifications[notification_id_str]

            # Remove from indexes
            if notification.status in self._notifications_by_status:
                self._notifications_by_status[notification.status] = [
                    n for n in self._notifications_by_status[notification.status] 
                    if n.id != notification_id
                ]

            recipient_user_id = notification.recipient.user_id
            if recipient_user_id in self._notifications_by_recipient:
                self._notifications_by_recipient[recipient_user_id] = [
                    n for n in self._notifications_by_recipient[recipient_user_id] 
                    if n.id != notification_id
                ]

            if notification.type in self._notifications_by_type:
                self._notifications_by_type[notification.type] = [
                    n for n in self._notifications_by_type[notification.type] 
                    if n.id != notification_id
                ]


class InMemoryNotificationBatchRepository(NotificationBatchRepository):
    """
    In-memory implementation of NotificationBatchRepository.
    
    This class provides an in-memory implementation of the NotificationBatchRepository interface.
    """

    def __init__(self) -> None:
        """Initialize the in-memory notification batch repository."""
        self._batches: Dict[str, NotificationBatch] = {}
        self._batches_by_status: Dict[str, List[NotificationBatch]] = {}

    async def save(self, batch: NotificationBatch) -> NotificationBatch:
        """
        Save a notification batch.
        
        Args:
            batch (NotificationBatch): The notification batch to save.

        Returns:
            NotificationBatch: The saved notification batch.
        """
        batch_id_str = str(batch.id)
        self._batches[batch_id_str] = batch

        # Update indexes
        if batch.status not in self._batches_by_status:
            self._batches_by_status[batch.status] = []
        self._batches_by_status[batch.status].append(batch)

        return batch

    async def get_by_id(self, batch_id: NotificationId) -> Optional[NotificationBatch]:
        """
        Get batch by ID.
        
        Args:
            batch_id (NotificationId): The ID of the batch to get.

        Returns:
            Optional[NotificationBatch]: The batch if found, None otherwise.
        """
        return self._batches.get(str(batch_id))

    async def get_by_status(self, status: str) -> List[NotificationBatch]:
        """
        Get batches by status.
        
        Args:
            status (str): The status of the batches to get.

        Returns:
            List[NotificationBatch]: The batches with the given status.
        """
        return self._batches_by_status.get(status, [])

    async def get_pending_batches(self) -> List[NotificationBatch]:
        """
        Get all pending batches.
        
        Returns:
            List[NotificationBatch]: The pending batches.
        """
        return self._batches_by_status.get("pending", [])

    async def get_processing_batches(self) -> List[NotificationBatch]:
        """
        Get all processing batches.
        
        Returns:
            List[NotificationBatch]: The processing batches.
        """
        return self._batches_by_status.get("processing", [])

    async def delete(self, batch_id: NotificationId) -> None:
        """
        Delete a batch.
        
        Args:
            batch_id (NotificationId): The ID of the batch to delete.
        """
        batch_id_str = str(batch_id)
        if batch_id_str in self._batches:
            batch = self._batches[batch_id_str]
            del self._batches[batch_id_str]

            # Remove from indexes
            if batch.status in self._batches_by_status:
                self._batches_by_status[batch.status] = [
                    b for b in self._batches_by_status[batch.status] 
                    if b.id != batch_id
                ]


class InMemoryNotificationSubscriptionRepository(NotificationSubscriptionRepository):
    """
    In-memory implementation of NotificationSubscriptionRepository.
    
    This class provides an in-memory implementation of the NotificationSubscriptionRepository interface.
    """

    def __init__(self) -> None:
        """Initialize the in-memory notification subscription repository."""
        self._subscriptions: Dict[str, NotificationSubscription] = {}
        self._subscriptions_by_user_id: Dict[str, List[NotificationSubscription]] = {}
        self._subscriptions_by_event_type: Dict[str, List[NotificationSubscription]] = {}

    async def save(self, subscription: NotificationSubscription) -> NotificationSubscription:
        """
        Save a notification subscription.
        
        Args:
            subscription (NotificationSubscription): The notification subscription to save.

        Returns:
            NotificationSubscription: The saved notification subscription.
        """
        subscription_id_str = str(subscription.id)
        self._subscriptions[subscription_id_str] = subscription

        # Update indexes
        if subscription.user_id not in self._subscriptions_by_user_id:
            self._subscriptions_by_user_id[subscription.user_id] = []
        self._subscriptions_by_user_id[subscription.user_id].append(subscription)

        if subscription.event_type not in self._subscriptions_by_event_type:
            self._subscriptions_by_event_type[subscription.event_type] = []
        self._subscriptions_by_event_type[subscription.event_type].append(subscription)

        return subscription

    async def get_by_id(self, subscription_id: NotificationId) -> Optional[NotificationSubscription]:
        """
        Get subscription by ID.
        
        Args:
            subscription_id (NotificationId): The ID of the subscription to get.

        Returns:
            Optional[NotificationSubscription]: The subscription if found, None otherwise.
        """
        return self._subscriptions.get(str(subscription_id))

    async def get_by_user_id(self, user_id: str) -> List[NotificationSubscription]:
        """
        Get subscriptions by user ID.
        
        Args:
            user_id (str): The ID of the user.

        Returns:
            List[NotificationSubscription]: The subscriptions for the given user ID.
        """
        return self._subscriptions_by_user_id.get(user_id, [])

    async def get_by_event_type(self, event_type: str) -> List[NotificationSubscription]:
        """
        Get subscriptions by event type.
        
        Args:
            event_type (str): The type of the event.

        Returns:
            List[NotificationSubscription]: The subscriptions for the given event type.
        """
        return self._subscriptions_by_event_type.get(event_type, [])

    async def get_active_subscriptions(self) -> List[NotificationSubscription]:
        """
        Get all active subscriptions.
        
        Returns:
            List[NotificationSubscription]: The active subscriptions.
        """
        active_subscriptions = []
        for subscription in self._subscriptions.values():
            if subscription.is_active:
                active_subscriptions.append(subscription)
        return active_subscriptions

    async def get_by_user_and_event(self, user_id: str, event_type: str) -> Optional[NotificationSubscription]:
        """
        Get subscription by user ID and event type.
        
        Args:
            user_id (str): The ID of the user.
            event_type (str): The type of the event.

        Returns:
            Optional[NotificationSubscription]: The subscription if found, None otherwise.
        """
        user_subscriptions = self._subscriptions_by_user_id.get(user_id, [])
        for subscription in user_subscriptions:
            if subscription.event_type == event_type:
                return subscription
        return None

    async def delete(self, subscription_id: NotificationId) -> None:
        """
        Delete a subscription.
        
        Args:
            subscription_id (NotificationId): The ID of the subscription to delete.
        """
        subscription_id_str = str(subscription_id)
        if subscription_id_str in self._subscriptions:
            subscription = self._subscriptions[subscription_id_str]
            del self._subscriptions[subscription_id_str]

            # Remove from indexes
            if subscription.user_id in self._subscriptions_by_user_id:
                self._subscriptions_by_user_id[subscription.user_id] = [
                    s for s in self._subscriptions_by_user_id[subscription.user_id] 
                    if s.id != subscription_id
                ]

            if subscription.event_type in self._subscriptions_by_event_type:
                self._subscriptions_by_event_type[subscription.event_type] = [
                    s for s in self._subscriptions_by_event_type[subscription.event_type] 
                    if s.id != subscription_id
                ] 