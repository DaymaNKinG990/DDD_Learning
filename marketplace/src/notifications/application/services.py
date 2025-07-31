"""Application services for notifications domain."""

# Python imports
from datetime import UTC, datetime
from typing import Any, Dict, List, Optional

# Local imports
from src.notifications.domain.entities import (
    Notification,
    NotificationBatch,
    NotificationSubscription,
)
from src.notifications.domain.events import (
    NotificationCreated,
    NotificationSent,
    NotificationDelivered,
    NotificationFailed,
    BatchProcessingStarted,
    BatchProcessingCompleted,
)
from src.notifications.domain.repositories import (
    NotificationRepository,
    NotificationBatchRepository,
    NotificationSubscriptionRepository,
)
from src.notifications.domain.value_objects import (
    NotificationId,
    NotificationPriority,
    NotificationRecipient,
    NotificationStatus,
    NotificationTemplate,
    NotificationType,
)
from src.shared.application.event_handlers import EventHandler


class NotificationService:
    """
    Service for managing notifications.
    
    This class provides methods for creating, sending, and managing notifications.
    """

    def __init__(
        self,
        notification_repository: NotificationRepository,
        batch_repository: NotificationBatchRepository,
        subscription_repository: NotificationSubscriptionRepository,
        event_handler: Optional[EventHandler] = None,
    ) -> None:
        """
        Initialize the notification service.
        
        Args:
            notification_repository (NotificationRepository): The repository for notifications.
            batch_repository (NotificationBatchRepository): The repository for notification batches.
            subscription_repository (NotificationSubscriptionRepository): The repository for notification subscriptions.
            event_handler (EventHandler): The event handler for the notification service.
        """
        self.notification_repository = notification_repository
        self.batch_repository = batch_repository
        self.subscription_repository = subscription_repository
        self.event_handler = event_handler

    async def send_notification(
        self,
        recipient: NotificationRecipient,
        template: NotificationTemplate,
        notification_type: NotificationType,
        data: Dict[str, Any],
        priority: NotificationPriority = NotificationPriority.NORMAL,
        scheduled_at: Optional[datetime] = None,
    ) -> Notification:
        """
        Send a single notification.
        
        Args:
            recipient (NotificationRecipient): The recipient of the notification.
            template (NotificationTemplate): The template for the notification.
            notification_type (NotificationType): The type of the notification.
            data (Dict[str, Any]): The data for the notification.
            priority (NotificationPriority): The priority of the notification.
            scheduled_at (Optional[datetime]): The scheduled time of the notification.

        Returns:
            Notification: The notification that was sent.
        """
        notification = Notification(
            id=NotificationId.generate(),
            recipient=recipient,
            template=template,
            type=notification_type,
            priority=priority,
            data=data,
            scheduled_at=scheduled_at,
        )

        saved_notification = await self.notification_repository.save(notification)
        
        if self.event_handler:
            await self.event_handler.handle(NotificationCreated(notification_id=notification.id))
        
        return saved_notification

    async def create_batch(
        self,
        name: str,
        template: NotificationTemplate,
        notification_type: NotificationType,
        recipients: List[NotificationRecipient],
        data: Dict[str, Any],
        description: Optional[str] = None,
        priority: NotificationPriority = NotificationPriority.NORMAL,
        scheduled_at: Optional[datetime] = None,
    ) -> NotificationBatch:
        """
        Create a notification batch.
        
        Args:
            name (str): The name of the batch.
            template (NotificationTemplate): The template for the batch.
            notification_type (NotificationType): The type of the batch.
            recipients (List[NotificationRecipient]): The recipients of the batch.
            data (Dict[str, Any]): The data for the batch.
            description (Optional[str]): The description of the batch.
            priority (NotificationPriority): The priority of the batch.
            scheduled_at (Optional[datetime]): The scheduled time of the batch.

        Returns:
            NotificationBatch: The created notification batch.
        """
        batch = NotificationBatch(
            id=NotificationId.generate(),
            name=name,
            template=template,
            type=notification_type,
            recipients=recipients,
            total_count=len(recipients),
            description=description,
            priority=priority,
            data=data,
            scheduled_at=scheduled_at,
        )

        return await self.batch_repository.save(batch)

    async def start_batch_processing(self, batch_id: str) -> NotificationBatch:
        """
        Start processing a notification batch.
        
        Args:
            batch_id (str): The ID of the batch to start processing.

        Returns:
            NotificationBatch: The batch that was started processing.
        """
        batch = await self.batch_repository.get_by_id(NotificationId(value=batch_id))
        if not batch:
            raise ValueError(f"Batch with ID {batch_id} not found")

        batch.start_processing()
        saved_batch = await self.batch_repository.save(batch)
        
        if self.event_handler:
            await self.event_handler.handle(BatchProcessingStarted(batch_id=batch.id))
        
        return saved_batch

    async def complete_batch(self, batch_id: str) -> NotificationBatch:
        """
        Mark a batch as completed.
        
        Args:
            batch_id (str): The ID of the batch to mark as completed.

        Returns:
            NotificationBatch: The batch that was marked as completed.
        """
        batch = await self.batch_repository.get_by_id(NotificationId(value=batch_id))
        if not batch:
            raise ValueError(f"Batch with ID {batch_id} not found")

        batch.complete()
        saved_batch = await self.batch_repository.save(batch)
        
        if self.event_handler:
            await self.event_handler.handle(BatchProcessingCompleted(batch_id=batch.id))
        
        return saved_batch

    async def mark_notification_sent(self, notification_id: str) -> Notification:
        """
        Mark a notification as sent.
        
        Args:
            notification_id (str): The ID of the notification to mark as sent.

        Returns:
            Notification: The notification that was marked as sent.
        """
        notification = await self.notification_repository.get_by_id(
            NotificationId(value=notification_id)
        )
        if not notification:
            raise ValueError(f"Notification with ID {notification_id} not found")

        notification.send()
        saved_notification = await self.notification_repository.save(notification)
        
        if self.event_handler:
            await self.event_handler.handle(NotificationSent(notification_id=notification.id))
        
        return saved_notification

    async def mark_notification_delivered(self, notification_id: str) -> Notification:
        """
        Mark a notification as delivered.
        
        Args:
            notification_id (str): The ID of the notification to mark as delivered.

        Returns:
            Notification: The notification that was marked as delivered.
        """
        notification = await self.notification_repository.get_by_id(
            NotificationId(value=notification_id)
        )
        if not notification:
            raise ValueError(f"Notification with ID {notification_id} not found")

        notification.deliver()
        saved_notification = await self.notification_repository.save(notification)
        
        if self.event_handler:
            await self.event_handler.handle(NotificationDelivered(notification_id=notification.id))
        
        return saved_notification

    async def mark_notification_failed(self, notification_id: str, error_message: str) -> Notification:
        """
        Mark a notification as failed.
        
        Args:
            notification_id (str): The ID of the notification to mark as failed.
            error_message (str): The error message of the notification.

        Returns:
            Notification: The notification that was marked as failed.
        """
        notification = await self.notification_repository.get_by_id(
            NotificationId(value=notification_id)
        )
        if not notification:
            raise ValueError(f"Notification with ID {notification_id} not found")

        notification.fail(error_message)
        saved_notification = await self.notification_repository.save(notification)
        
        if self.event_handler:
            await self.event_handler.handle(NotificationFailed(notification_id=notification.id))
        
        return saved_notification

    async def retry_notification(self, notification_id: str) -> Optional[Notification]:
        """
        Retry sending a failed notification.
        
        Args:
            notification_id (str): The ID of the notification to retry.

        Returns:
            Optional[Notification]: The notification that was retried, None if it was not found.
        """
        notification = await self.notification_repository.get_by_id(
            NotificationId(value=notification_id)
        )
        if not notification:
            raise ValueError(f"Notification with ID {notification_id} not found")

        if notification.retry():
            return await self.notification_repository.save(notification)
        return None

    async def create_subscription(
        self,
        user_id: str,
        event_type: str,
        channels: List[NotificationType],
    ) -> NotificationSubscription:
        """
        Create a notification subscription.
        
        Args:
            user_id (str): The ID of the user.
            event_type (str): The type of the event.
            channels (List[NotificationType]): The channels to send the notification on.

        Returns:
            NotificationSubscription: The created notification subscription.
        """
        subscription = NotificationSubscription(
            id=NotificationId.generate(),
            user_id=user_id,
            event_type=event_type,
            channels=channels,
        )

        return await self.subscription_repository.save(subscription)

    async def update_subscription(
        self,
        subscription_id: str,
        channels: List[NotificationType],
        is_active: bool = True,
    ) -> NotificationSubscription:
        """
        Update a notification subscription.
        
        Args:
            subscription_id (str): The ID of the subscription to update.
            channels (List[NotificationType]): The channels to send the notification on.
            is_active (bool): Whether the subscription is active.

        Returns:
            NotificationSubscription: The updated notification subscription.
        """
        subscription = await self.subscription_repository.get_by_id(
            NotificationId(value=subscription_id)
        )
        if not subscription:
            raise ValueError(f"Subscription with ID {subscription_id} not found")

        subscription.channels = channels
        subscription.is_active = is_active
        subscription.updated_at = datetime.now(UTC)

        return await self.subscription_repository.save(subscription)

    async def get_user_subscriptions(self, user_id: str) -> List[NotificationSubscription]:
        """
        Get all subscriptions for a user.
        
        Args:
            user_id (str): The ID of the user.

        Returns:
            List[NotificationSubscription]: The subscriptions for the user.
        """
        return await self.subscription_repository.get_by_user_id(user_id)

    async def get_pending_notifications(self) -> List[Notification]:
        """
        Get all pending notifications.
        
        Returns:
            List[Notification]: The pending notifications.
        """
        return await self.notification_repository.get_by_status(NotificationStatus.PENDING)

    async def get_failed_notifications(self) -> List[Notification]:
        """
        Get all failed notifications.
        
        Returns:
            List[Notification]: The failed notifications.
        """
        return await self.notification_repository.get_by_status(NotificationStatus.FAILED) 