"""Queries for notifications domain."""

# Python imports
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel

# Local imports
from src.notifications.domain.value_objects import (
    NotificationStatus,
    NotificationType,
)


# Read Models
class NotificationReadModel(BaseModel):
    """
    Read model for Notification.
    
    This model represents the data structure for a notification.

    Attributes:
        id (str): The ID of the notification.
        recipient_user_id (str): The ID of the recipient user.
        recipient_email (str): The email of the recipient.
        template_name (str): The name of the template.
        template_content (str): The content of the template.
        notification_type (str): The type of the notification.
        priority (str): The priority of the notification.
        status (str): The status of the notification.
        data (Dict[str, Any]): The data of the notification.
        scheduled_at (Optional[datetime]): The scheduled time of the notification.
        sent_at (Optional[datetime]): The time the notification was sent.
        delivered_at (Optional[datetime]): The time the notification was delivered.
        retry_count (int): The number of times the notification has been retried.
        max_retries (int): The maximum number of retries for the notification.
        error_message (Optional[str]): The error message of the notification.
        metadata (Dict[str, Any]): The metadata of the notification.
        created_at (datetime): The date and time the notification was created.
    """
    
    id: str
    recipient_user_id: str
    recipient_email: str
    template_name: str
    template_content: str
    notification_type: str
    priority: str
    status: str
    data: Dict[str, Any]
    scheduled_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    retry_count: int
    max_retries: int
    error_message: Optional[str] = None
    metadata: Dict[str, Any]
    created_at: datetime


class NotificationBatchReadModel(BaseModel):
    """
    Read model for NotificationBatch.
    
    This model represents the data structure for a notification batch.

    Attributes:
        id (str): The ID of the notification batch.
        name (str): The name of the notification batch.
        template_name (str): The name of the template.
        template_content (str): The content of the template.
        notification_type (str): The type of the notification.
        total_count (int): The total number of notifications in the batch.
        sent_count (int): The number of notifications that have been sent.
        failed_count (int): The number of notifications that have failed.
        description (Optional[str]): The description of the notification batch.
        priority (str): The priority of the notification batch.
        data (Dict[str, Any]): The data of the notification batch.
        scheduled_at (Optional[datetime]): The scheduled time of the notification batch.
        status (str): The status of the notification batch.
        created_at (datetime): The date and time the notification batch was created.
        completed_at (Optional[datetime]): The date and time the notification batch was completed.
    """
    
    id: str
    name: str
    template_name: str
    template_content: str
    notification_type: str
    total_count: int
    sent_count: int
    failed_count: int
    description: Optional[str] = None
    priority: str
    data: Dict[str, Any]
    scheduled_at: Optional[datetime] = None
    status: str
    created_at: datetime
    completed_at: Optional[datetime] = None


class NotificationSubscriptionReadModel(BaseModel):
    """
    Read model for NotificationSubscription.
    
    This model represents the data structure for a notification subscription.

    Attributes:
        id (str): The ID of the notification subscription.
        user_id (str): The ID of the user.
        event_type (str): The type of the event.
        channels (List[str]): The channels of the notification subscription.
        is_active (bool): Whether the notification subscription is active.
        created_at (datetime): The date and time the notification subscription was created.
        updated_at (Optional[datetime]): The date and time the notification subscription was updated.
    """

    id: str
    user_id: str
    event_type: str
    channels: List[str]
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None


# Query Commands
@dataclass
class GetNotificationQuery:
    """
    Query to get a notification by ID.
    
    This query is used to retrieve a notification by its ID.
    """
    
    notification_id: str


@dataclass
class GetNotificationsByUserQuery:
    """
    Query to get notifications by user ID.
    
    This query is used to retrieve notifications by user ID.

    Attributes:
        user_id (str): The ID of the user.
        status (Optional[NotificationStatus]): The status of the notifications.
        notification_type (Optional[NotificationType]): The type of the notifications.
        limit (int): The maximum number of notifications to retrieve.
        offset (int): The number of notifications to skip.
    """
    
    user_id: str
    status: Optional[NotificationStatus] = None
    notification_type: Optional[NotificationType] = None
    limit: int = 50
    offset: int = 0


@dataclass
class GetNotificationsByStatusQuery:
    """
    Query to get notifications by status.
    
    This query is used to retrieve notifications by status.

    Attributes:
        status (NotificationStatus): The status of the notifications.
        limit (int): The maximum number of notifications to retrieve.
        offset (int): The number of notifications to skip.
    """
    
    status: NotificationStatus
    limit: int = 50
    offset: int = 0


@dataclass
class GetNotificationsByTypeQuery:
    """
    Query to get notifications by type.
    
    This query is used to retrieve notifications by type.

    Attributes:
        notification_type (NotificationType): The type of the notifications.
        status (Optional[NotificationStatus]): The status of the notifications.
        limit (int): The maximum number of notifications to retrieve.
        offset (int): The number of notifications to skip.
    """
    
    notification_type: NotificationType
    status: Optional[NotificationStatus] = None
    limit: int = 50
    offset: int = 0


@dataclass
class GetScheduledNotificationsQuery:
    """
    Query to get scheduled notifications.
    
    This query is used to retrieve scheduled notifications.

    Attributes:
        before (datetime): The time before which the notifications were scheduled.
        limit (int): The maximum number of notifications to retrieve.
        offset (int): The number of notifications to skip.
    """
    
    before: datetime
    limit: int = 50
    offset: int = 0


@dataclass
class GetBatchQuery:
    """
    Query to get a batch by ID.
    
    This query is used to retrieve a batch by its ID.

    Attributes:
        batch_id (str): The ID of the batch.
    """
    
    batch_id: str


@dataclass
class GetBatchesByStatusQuery:
    """
    Query to get batches by status.
    
    This query is used to retrieve batches by status.

    Attributes:
        status (str): The status of the batches.
        limit (int): The maximum number of batches to retrieve.
        offset (int): The number of batches to skip.
    """
    
    status: str
    limit: int = 50
    offset: int = 0


@dataclass
class GetSubscriptionQuery:
    """
    Query to get a subscription by ID.
    
    This query is used to retrieve a subscription by its ID.

    Attributes:
        subscription_id (str): The ID of the subscription.
    """
    
    subscription_id: str


@dataclass
class GetSubscriptionsByUserQuery:
    """
    Query to get subscriptions by user ID.
    
    This query is used to retrieve subscriptions by user ID.

    Attributes:
        user_id (str): The ID of the user.
        is_active (Optional[bool]): Whether the subscription is active.
        limit (int): The maximum number of subscriptions to retrieve.
        offset (int): The number of subscriptions to skip.
    """
    
    user_id: str
    is_active: Optional[bool] = None
    limit: int = 50
    offset: int = 0


@dataclass
class GetSubscriptionsByEventTypeQuery:
    """
    Query to get subscriptions by event type.
    
    This query is used to retrieve subscriptions by event type.

    Attributes:
        event_type (str): The type of the event.
        is_active (Optional[bool]): Whether the subscription is active.
        limit (int): The maximum number of subscriptions to retrieve.
        offset (int): The number of subscriptions to skip.
    """
    
    event_type: str
    is_active: Optional[bool] = None
    limit: int = 50
    offset: int = 0


# Query Handlers
class NotificationQueryHandler(ABC):
    """
    Abstract query handler for notifications.
    
    This class defines the abstract methods for handling notification queries.
    """

    @abstractmethod
    async def get_notification(self, query: GetNotificationQuery) -> Optional[NotificationReadModel]:
        """
        Get notification by ID.
        
        Args:
            query (GetNotificationQuery): The query to get the notification.

        Returns:
            Optional[NotificationReadModel]: The notification if found, None otherwise.
        """
        pass

    @abstractmethod
    async def get_notifications_by_user(self, query: GetNotificationsByUserQuery) -> List[NotificationReadModel]:
        """
        Get notifications by user ID.
        
        Args:
            query (GetNotificationsByUserQuery): The query to get the notifications.

        Returns:
            List[NotificationReadModel]: The notifications.
        """
        pass

    @abstractmethod
    async def get_notifications_by_status(self, query: GetNotificationsByStatusQuery) -> List[NotificationReadModel]:
        """
        Get notifications by status.
        
        Args:
            query (GetNotificationsByStatusQuery): The query to get the notifications.

        Returns:
            List[NotificationReadModel]: The notifications.
        """
        pass

    @abstractmethod
    async def get_notifications_by_type(self, query: GetNotificationsByTypeQuery) -> List[NotificationReadModel]:
        """
        Get notifications by type.
        
        Args:
            query (GetNotificationsByTypeQuery): The query to get the notifications.

        Returns:
            List[NotificationReadModel]: The notifications.
        """
        pass

    @abstractmethod
    async def get_scheduled_notifications(self, query: GetScheduledNotificationsQuery) -> List[NotificationReadModel]:
        """
        Get scheduled notifications.
        
        Args:
            query (GetScheduledNotificationsQuery): The query to get the scheduled notifications.

        Returns:
            List[NotificationReadModel]: The scheduled notifications.
        """
        pass


class NotificationBatchQueryHandler(ABC):
    """
    Abstract query handler for notification batches.
    
    This class defines the abstract methods for handling notification batch queries.
    """

    @abstractmethod
    async def get_batch(self, query: GetBatchQuery) -> Optional[NotificationBatchReadModel]:
        """
        Get batch by ID.
        
        Args:
            query (GetBatchQuery): The query to get the batch.

        Returns:
            Optional[NotificationBatchReadModel]: The batch if found, None otherwise.
        """
        pass

    @abstractmethod
    async def get_batches_by_status(self, query: GetBatchesByStatusQuery) -> List[NotificationBatchReadModel]:
        """
        Get batches by status.
        
        Args:
            query (GetBatchesByStatusQuery): The query to get the batches.

        Returns:
            List[NotificationBatchReadModel]: The batches.
        """
        pass


class NotificationSubscriptionQueryHandler(ABC):
    """
    Abstract query handler for notification subscriptions.
    
    This class defines the abstract methods for handling notification subscription queries.
    """

    @abstractmethod
    async def get_subscription(self, query: GetSubscriptionQuery) -> Optional[NotificationSubscriptionReadModel]:
        """
        Get subscription by ID.
        
        Args:
            query (GetSubscriptionQuery): The query to get the subscription.

        Returns:
            Optional[NotificationSubscriptionReadModel]: The subscription if found, None otherwise.
        """
        pass

    @abstractmethod
    async def get_subscriptions_by_user(self, query: GetSubscriptionsByUserQuery) -> List[NotificationSubscriptionReadModel]:
        """
        Get subscriptions by user ID.
        
        Args:
            query (GetSubscriptionsByUserQuery): The query to get the subscriptions.

        Returns:
            List[NotificationSubscriptionReadModel]: The subscriptions.
        """
        pass

    @abstractmethod
    async def get_subscriptions_by_event_type(self, query: GetSubscriptionsByEventTypeQuery) -> List[NotificationSubscriptionReadModel]:
        """
        Get subscriptions by event type.
        
        Args:
            query (GetSubscriptionsByEventTypeQuery): The query to get the subscriptions.

        Returns:
            List[NotificationSubscriptionReadModel]: The subscriptions.
        """
        pass 