"""Domain events for notifications."""

from dataclasses import dataclass
from datetime import datetime

from src.notifications.domain.value_objects import NotificationId
from src.shared.domain.events import DomainEvent


@dataclass
class NotificationCreated(DomainEvent):
    """Event raised when a notification is created."""
    
    notification_id: NotificationId
    occurred_on: datetime = None

    def __post_init__(self):
        if self.occurred_on is None:
            from datetime import UTC
            self.occurred_on = datetime.now(UTC)


@dataclass
class NotificationSent(DomainEvent):
    """Event raised when a notification is sent."""
    
    notification_id: NotificationId
    occurred_on: datetime = None

    def __post_init__(self):
        if self.occurred_on is None:
            from datetime import UTC
            self.occurred_on = datetime.now(UTC)


@dataclass
class NotificationDelivered(DomainEvent):
    """Event raised when a notification is delivered."""
    
    notification_id: NotificationId
    occurred_on: datetime = None

    def __post_init__(self):
        if self.occurred_on is None:
            from datetime import UTC
            self.occurred_on = datetime.now(UTC)


@dataclass
class NotificationFailed(DomainEvent):
    """Event raised when a notification fails to send."""
    
    notification_id: NotificationId
    error_message: str
    occurred_on: datetime = None

    def __post_init__(self):
        if self.occurred_on is None:
            from datetime import UTC
            self.occurred_on = datetime.now(UTC)


@dataclass
class BatchProcessingStarted(DomainEvent):
    """Event raised when batch processing starts."""
    
    batch_id: NotificationId
    occurred_on: datetime = None

    def __post_init__(self):
        if self.occurred_on is None:
            from datetime import UTC
            self.occurred_on = datetime.now(UTC)


@dataclass
class BatchProcessingCompleted(DomainEvent):
    """Event raised when batch processing completes."""
    
    batch_id: NotificationId
    occurred_on: datetime = None

    def __post_init__(self):
        if self.occurred_on is None:
            from datetime import UTC
            self.occurred_on = datetime.now(UTC)


@dataclass
class NotificationSubscriptionCreated(DomainEvent):
    """Event raised when a notification subscription is created."""
    
    subscription_id: NotificationId
    user_id: str
    event_type: str
    occurred_on: datetime = None

    def __post_init__(self):
        if self.occurred_on is None:
            from datetime import UTC
            self.occurred_on = datetime.now(UTC)


@dataclass
class NotificationSubscriptionUpdated(DomainEvent):
    """Event raised when a notification subscription is updated."""
    
    subscription_id: NotificationId
    user_id: str
    event_type: str
    occurred_on: datetime = None

    def __post_init__(self):
        if self.occurred_on is None:
            from datetime import UTC
            self.occurred_on = datetime.now(UTC) 