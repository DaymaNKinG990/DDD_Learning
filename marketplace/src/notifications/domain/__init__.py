"""Notifications domain module."""

from .entities import Notification, NotificationBatch, NotificationSubscription
from .events import (
    NotificationCreated,
    NotificationSent,
    NotificationDelivered,
    NotificationFailed,
    BatchProcessingStarted,
    BatchProcessingCompleted,
    NotificationSubscriptionCreated,
    NotificationSubscriptionUpdated,
)
from .repositories import (
    NotificationRepository,
    NotificationBatchRepository,
    NotificationSubscriptionRepository,
)
from .value_objects import (
    NotificationId,
    NotificationStatus,
    NotificationType,
    NotificationPriority,
    NotificationRecipient,
    NotificationTemplate,
)

__all__ = [
    "Notification",
    "NotificationBatch",
    "NotificationSubscription",
    "NotificationCreated",
    "NotificationSent",
    "NotificationDelivered",
    "NotificationFailed",
    "BatchProcessingStarted",
    "BatchProcessingCompleted",
    "NotificationSubscriptionCreated",
    "NotificationSubscriptionUpdated",
    "NotificationRepository",
    "NotificationBatchRepository",
    "NotificationSubscriptionRepository",
    "NotificationId",
    "NotificationStatus",
    "NotificationType",
    "NotificationPriority",
    "NotificationRecipient",
    "NotificationTemplate",
]
