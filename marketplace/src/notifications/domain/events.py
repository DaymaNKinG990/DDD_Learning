"""Domain events for notifications."""

# Python imports
from dataclasses import dataclass
from datetime import UTC, datetime

# Local imports
from src.notifications.domain.value_objects import NotificationId
from src.shared.domain.events import DomainEvent


@dataclass
class NotificationCreated(DomainEvent):
    """
    Event raised when a notification is created.
    
    Attributes:
        notification_id (NotificationId): The ID of the notification.
        occurred_on (datetime): The date and time the event occurred.
    """

    notification_id: NotificationId
    occurred_on: datetime = None

    def __post_init__(self) -> None:
        """
        Initialize the event.
        
        Raises:
            ValueError: If the occurred_on is not provided.
        """
        if self.occurred_on is None:
            self.occurred_on = datetime.now(UTC)


@dataclass
class NotificationSent(DomainEvent):
    """
    Event raised when a notification is sent.
    
    Attributes:
        notification_id (NotificationId): The ID of the notification.
        occurred_on (datetime): The date and time the event occurred.
    """
    
    notification_id: NotificationId
    occurred_on: datetime = None

    def __post_init__(self) -> None:
        """
        Initialize the event.
        
        Raises:
            ValueError: If the occurred_on is not provided.
        """
        if self.occurred_on is None:
            self.occurred_on = datetime.now(UTC)


@dataclass
class NotificationDelivered(DomainEvent):
    """
    Event raised when a notification is delivered.
    
    Attributes:
        notification_id (NotificationId): The ID of the notification.
        occurred_on (datetime): The date and time the event occurred.
    """
    
    notification_id: NotificationId
    occurred_on: datetime = None

    def __post_init__(self) -> None:
        """
        Initialize the event.
        
        Raises:
            ValueError: If the occurred_on is not provided.
        """
        if self.occurred_on is None:
            self.occurred_on = datetime.now(UTC)


@dataclass
class NotificationFailed(DomainEvent):
    """
    Event raised when a notification fails to send.
    
    Attributes:
        notification_id (NotificationId): The ID of the notification.
        error_message (str): The error message of the notification.
        occurred_on (datetime): The date and time the event occurred.
    """
    
    notification_id: NotificationId
    error_message: str
    occurred_on: datetime = None

    def __post_init__(self) -> None:
        """
        Initialize the event.
        
        Raises:
            ValueError: If the occurred_on is not provided.
        """
        if self.occurred_on is None:
            self.occurred_on = datetime.now(UTC)


@dataclass
class BatchProcessingStarted(DomainEvent):
    """
    Event raised when batch processing starts.
    
    Attributes:
        batch_id (NotificationId): The ID of the batch.
        occurred_on (datetime): The date and time the event occurred.
    """
    
    batch_id: NotificationId
    occurred_on: datetime = None

    def __post_init__(self) -> None:
        """
        Initialize the event.
        
        Raises:
            ValueError: If the occurred_on is not provided.
        """
        if self.occurred_on is None:
            self.occurred_on = datetime.now(UTC)


@dataclass
class BatchProcessingCompleted(DomainEvent):
    """
    Event raised when batch processing completes.
    
    Attributes:
        batch_id (NotificationId): The ID of the batch.
        occurred_on (datetime): The date and time the event occurred.
    """
    
    batch_id: NotificationId
    occurred_on: datetime = None

    def __post_init__(self) -> None:
        """
        Initialize the event.
        
        Raises:
            ValueError: If the occurred_on is not provided.
        """
        if self.occurred_on is None:
            self.occurred_on = datetime.now(UTC)


@dataclass
class NotificationSubscriptionCreated(DomainEvent):
    """
    Event raised when a notification subscription is created.
    
    Attributes:
        subscription_id (NotificationId): The ID of the subscription.
        user_id (str): The ID of the user.
        event_type (str): The type of the event.
        occurred_on (datetime): The date and time the event occurred.
    """
    
    subscription_id: NotificationId
    user_id: str
    event_type: str
    occurred_on: datetime = None

    def __post_init__(self) -> None:
        """
        Initialize the event.
        
        Raises:
            ValueError: If the occurred_on is not provided.
        """
        if self.occurred_on is None:
            self.occurred_on = datetime.now(UTC)


@dataclass
class NotificationSubscriptionUpdated(DomainEvent):
    """
    Event raised when a notification subscription is updated.
    
    Attributes:
        subscription_id (NotificationId): The ID of the subscription.
        user_id (str): The ID of the user.
        event_type (str): The type of the event.
        occurred_on (datetime): The date and time the event occurred.
    """
    
    subscription_id: NotificationId
    user_id: str
    event_type: str
    occurred_on: datetime = None

    def __post_init__(self) -> None:
        """
        Initialize the event.
        
        Raises:
            ValueError: If the occurred_on is not provided.
        """
        if self.occurred_on is None:
            self.occurred_on = datetime.now(UTC) 