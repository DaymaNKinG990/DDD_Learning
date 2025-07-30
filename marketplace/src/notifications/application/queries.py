"""Queries for notifications domain."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from src.notifications.domain.value_objects import (
    NotificationId,
    NotificationStatus,
    NotificationType,
)


# Read Models
class NotificationReadModel(BaseModel):
    """Read model for Notification."""
    
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
    """Read model for NotificationBatch."""
    
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
    """Read model for NotificationSubscription."""
    
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
    """Query to get a notification by ID."""
    notification_id: str


@dataclass
class GetNotificationsByUserQuery:
    """Query to get notifications by user ID."""
    user_id: str
    status: Optional[NotificationStatus] = None
    notification_type: Optional[NotificationType] = None
    limit: int = 50
    offset: int = 0


@dataclass
class GetNotificationsByStatusQuery:
    """Query to get notifications by status."""
    status: NotificationStatus
    limit: int = 50
    offset: int = 0


@dataclass
class GetNotificationsByTypeQuery:
    """Query to get notifications by type."""
    notification_type: NotificationType
    status: Optional[NotificationStatus] = None
    limit: int = 50
    offset: int = 0


@dataclass
class GetScheduledNotificationsQuery:
    """Query to get scheduled notifications."""
    before: datetime
    limit: int = 50
    offset: int = 0


@dataclass
class GetBatchQuery:
    """Query to get a batch by ID."""
    batch_id: str


@dataclass
class GetBatchesByStatusQuery:
    """Query to get batches by status."""
    status: str
    limit: int = 50
    offset: int = 0


@dataclass
class GetSubscriptionQuery:
    """Query to get a subscription by ID."""
    subscription_id: str


@dataclass
class GetSubscriptionsByUserQuery:
    """Query to get subscriptions by user ID."""
    user_id: str
    is_active: Optional[bool] = None
    limit: int = 50
    offset: int = 0


@dataclass
class GetSubscriptionsByEventTypeQuery:
    """Query to get subscriptions by event type."""
    event_type: str
    is_active: Optional[bool] = None
    limit: int = 50
    offset: int = 0


# Query Handlers
class NotificationQueryHandler(ABC):
    """Abstract query handler for notifications."""

    @abstractmethod
    async def get_notification(self, query: GetNotificationQuery) -> Optional[NotificationReadModel]:
        """Get notification by ID."""
        pass

    @abstractmethod
    async def get_notifications_by_user(
        self, query: GetNotificationsByUserQuery
    ) -> List[NotificationReadModel]:
        """Get notifications by user ID."""
        pass

    @abstractmethod
    async def get_notifications_by_status(
        self, query: GetNotificationsByStatusQuery
    ) -> List[NotificationReadModel]:
        """Get notifications by status."""
        pass

    @abstractmethod
    async def get_notifications_by_type(
        self, query: GetNotificationsByTypeQuery
    ) -> List[NotificationReadModel]:
        """Get notifications by type."""
        pass

    @abstractmethod
    async def get_scheduled_notifications(
        self, query: GetScheduledNotificationsQuery
    ) -> List[NotificationReadModel]:
        """Get scheduled notifications."""
        pass


class NotificationBatchQueryHandler(ABC):
    """Abstract query handler for notification batches."""

    @abstractmethod
    async def get_batch(self, query: GetBatchQuery) -> Optional[NotificationBatchReadModel]:
        """Get batch by ID."""
        pass

    @abstractmethod
    async def get_batches_by_status(
        self, query: GetBatchesByStatusQuery
    ) -> List[NotificationBatchReadModel]:
        """Get batches by status."""
        pass


class NotificationSubscriptionQueryHandler(ABC):
    """Abstract query handler for notification subscriptions."""

    @abstractmethod
    async def get_subscription(
        self, query: GetSubscriptionQuery
    ) -> Optional[NotificationSubscriptionReadModel]:
        """Get subscription by ID."""
        pass

    @abstractmethod
    async def get_subscriptions_by_user(
        self, query: GetSubscriptionsByUserQuery
    ) -> List[NotificationSubscriptionReadModel]:
        """Get subscriptions by user ID."""
        pass

    @abstractmethod
    async def get_subscriptions_by_event_type(
        self, query: GetSubscriptionsByEventTypeQuery
    ) -> List[NotificationSubscriptionReadModel]:
        """Get subscriptions by event type."""
        pass 