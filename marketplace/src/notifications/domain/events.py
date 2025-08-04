"""Domain events for notifications."""

# Python imports
from datetime import UTC, datetime
from typing import Any

# Local imports
from src.notifications.domain.value_objects import NotificationId
from src.shared.domain.events import DomainEvent


class NotificationCreated(DomainEvent):
    """
    Event raised when a notification is created.
    
    Attributes:
        notification_id (NotificationId): The ID of the notification.
    """

    notification_id: NotificationId

    def __init__(self, **data: dict[str, Any]):
        """Initialize NotificationCreated event."""
        super().__init__(
            event_type="NotificationCreated",
            aggregate_id=str(data.get("notification_id", "")),
            **data
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert event to dictionary representation."""
        return {
            "event_id": str(self.event_id),
            "event_type": self.event_type,
            "aggregate_id": str(self.notification_id.value),
            "occurred_on": self.occurred_on.isoformat(),
            "version": self.version,
            "notification_id": str(self.notification_id.value)
        }


class NotificationSent(DomainEvent):
    """
    Event raised when a notification is sent.
    
    Attributes:
        notification_id (NotificationId): The ID of the notification.
    """
    
    notification_id: NotificationId

    def __init__(self, **data: dict[str, Any]):
        """Initialize NotificationSent event."""
        super().__init__(
            event_type="NotificationSent",
            aggregate_id=str(data.get("notification_id", "")),
            **data
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert event to dictionary representation."""
        return {
            "event_id": str(self.event_id),
            "event_type": self.event_type,
            "aggregate_id": str(self.notification_id.value),
            "occurred_on": self.occurred_on.isoformat(),
            "version": self.version,
            "notification_id": str(self.notification_id.value)
        }


class NotificationDelivered(DomainEvent):
    """
    Event raised when a notification is delivered.
    
    Attributes:
        notification_id (NotificationId): The ID of the notification.
    """
    
    notification_id: NotificationId

    def __init__(self, **data: dict[str, Any]):
        """Initialize NotificationDelivered event."""
        super().__init__(
            event_type="NotificationDelivered",
            aggregate_id=str(data.get("notification_id", "")),
            **data
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert event to dictionary representation."""
        return {
            "event_id": str(self.event_id),
            "event_type": self.event_type,
            "aggregate_id": str(self.notification_id.value),
            "occurred_on": self.occurred_on.isoformat(),
            "version": self.version,
            "notification_id": str(self.notification_id.value)
        }


class NotificationFailed(DomainEvent):
    """
    Event raised when a notification fails to send.
    
    Attributes:
        notification_id (NotificationId): The ID of the notification.
        error_message (str): The error message of the notification.
    """
    
    notification_id: NotificationId
    error_message: str

    def __init__(self, **data: dict[str, Any]):
        """Initialize NotificationFailed event."""
        super().__init__(
            event_type="NotificationFailed",
            aggregate_id=str(data.get("notification_id", "")),
            **data
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert event to dictionary representation."""
        return {
            "event_id": str(self.event_id),
            "event_type": self.event_type,
            "aggregate_id": str(self.notification_id.value),
            "occurred_on": self.occurred_on.isoformat(),
            "version": self.version,
            "notification_id": str(self.notification_id.value),
            "error_message": self.error_message
        }


class BatchProcessingStarted(DomainEvent):
    """
    Event raised when batch processing starts.
    
    Attributes:
        batch_id (NotificationId): The ID of the batch.
    """
    
    batch_id: NotificationId

    def __init__(self, **data: dict[str, Any]):
        """Initialize BatchProcessingStarted event."""
        super().__init__(
            event_type="BatchProcessingStarted",
            aggregate_id=str(data.get("batch_id", "")),
            **data
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert event to dictionary representation."""
        return {
            "event_id": str(self.event_id),
            "event_type": self.event_type,
            "aggregate_id": str(self.batch_id.value),
            "occurred_on": self.occurred_on.isoformat(),
            "version": self.version,
            "batch_id": str(self.batch_id.value)
        }


class BatchProcessingCompleted(DomainEvent):
    """
    Event raised when batch processing completes.
    
    Attributes:
        batch_id (NotificationId): The ID of the batch.
    """
    
    batch_id: NotificationId

    def __init__(self, **data: dict[str, Any]):
        """Initialize BatchProcessingCompleted event."""
        super().__init__(
            event_type="BatchProcessingCompleted",
            aggregate_id=str(data.get("batch_id", "")),
            **data
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert event to dictionary representation."""
        return {
            "event_id": str(self.event_id),
            "event_type": self.event_type,
            "aggregate_id": str(self.batch_id.value),
            "occurred_on": self.occurred_on.isoformat(),
            "version": self.version,
            "batch_id": str(self.batch_id.value)
        }


class NotificationSubscriptionCreated(DomainEvent):
    """
    Event raised when a notification subscription is created.
    
    Attributes:
        subscription_id (NotificationId): The ID of the subscription.
        user_id (str): The ID of the user.
        event_type (str): The type of the event.
    """
    
    subscription_id: NotificationId
    user_id: str
    event_type: str

    def __init__(self, **data: dict[str, Any]):
        """Initialize NotificationSubscriptionCreated event."""
        super().__init__(
            event_type="NotificationSubscriptionCreated",
            aggregate_id=str(data.get("subscription_id", "")),
            **data
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert event to dictionary representation."""
        return {
            "event_id": str(self.event_id),
            "event_type": self.event_type,
            "aggregate_id": str(self.subscription_id.value),
            "occurred_on": self.occurred_on.isoformat(),
            "version": self.version,
            "subscription_id": str(self.subscription_id.value),
            "user_id": self.user_id,
            "event_type": self.event_type
        }


class NotificationSubscriptionUpdated(DomainEvent):
    """
    Event raised when a notification subscription is updated.
    
    Attributes:
        subscription_id (NotificationId): The ID of the subscription.
        user_id (str): The ID of the user.
        event_type (str): The type of the event.
    """
    
    subscription_id: NotificationId
    user_id: str
    event_type: str

    def __init__(self, **data: dict[str, Any]):
        """Initialize NotificationSubscriptionUpdated event."""
        super().__init__(
            event_type="NotificationSubscriptionUpdated",
            aggregate_id=str(data.get("subscription_id", "")),
            **data
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert event to dictionary representation."""
        return {
            "event_id": str(self.event_id),
            "event_type": self.event_type,
            "aggregate_id": str(self.subscription_id.value),
            "occurred_on": self.occurred_on.isoformat(),
            "version": self.version,
            "subscription_id": str(self.subscription_id.value),
            "user_id": self.user_id,
            "event_type": self.event_type
        } 