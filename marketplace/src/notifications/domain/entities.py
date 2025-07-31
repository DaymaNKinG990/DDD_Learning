"""Entities for notifications domain."""

# Python imports
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Dict, List, Optional

# Local imports
from src.notifications.domain.value_objects import (
    NotificationId,
    NotificationPriority,
    NotificationRecipient,
    NotificationStatus,
    NotificationTemplate,
    NotificationType,
)
from src.shared.domain.entity import Entity


@dataclass
class Notification(Entity[NotificationId]):
    """
    Notification entity.
    
    Attributes:
        id (NotificationId): The ID of the notification.
        recipient (NotificationRecipient): The recipient of the notification.
        template (NotificationTemplate): The template of the notification.
        type (NotificationType): The type of the notification.
        priority (NotificationPriority): The priority of the notification.
        status (NotificationStatus): The status of the notification.
        data (Dict[str, Any]): The data of the notification.
        scheduled_at (Optional[datetime]): The scheduled date and time of the notification.
        sent_at (Optional[datetime]): The date and time the notification was sent.
        delivered_at (Optional[datetime]): The date and time the notification was delivered.
        retry_count (int): The number of times the notification has been retried.
        max_retries (int): The maximum number of retries for the notification.
        error_message (Optional[str]): The error message of the notification.
        metadata (Dict[str, Any]): The metadata of the notification.
    """

    id: NotificationId
    recipient: NotificationRecipient
    template: NotificationTemplate
    type: NotificationType
    priority: NotificationPriority = NotificationPriority.NORMAL
    status: NotificationStatus = NotificationStatus.PENDING
    data: Dict[str, Any] = field(default_factory=dict)
    scheduled_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    retry_count: int = 0
    max_retries: int = 3
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def send(self) -> None:
        """Mark notification as sent."""
        self.status = NotificationStatus.SENT
        self.sent_at = datetime.now(UTC)

    def deliver(self) -> None:
        """Mark notification as delivered."""
        self.status = NotificationStatus.DELIVERED
        self.delivered_at = datetime.now(UTC)

    def fail(self, error_message: str) -> None:
        """Mark notification as failed.
        
        Args:
            error_message (str): The error message of the notification.
        """
        self.status = NotificationStatus.FAILED
        self.error_message = error_message

    def retry(self) -> bool:
        """
        Retry sending notification.
        
        Returns:
            bool: True if the notification was retried, False otherwise.
        """
        if self.retry_count < self.max_retries:
            self.retry_count += 1
            self.status = NotificationStatus.PENDING
            self.error_message = None
            return True
        return False

    def cancel(self) -> None:
        """Cancel notification."""
        self.status = NotificationStatus.CANCELLED

    def is_sent(self) -> bool:
        """
        Check if notification is sent.
        
        Returns:
            bool: True if the notification is sent, False otherwise.
        """
        return self.status in [NotificationStatus.SENT, NotificationStatus.DELIVERED]

    def is_delivered(self) -> bool:
        """
        Check if notification is delivered.
        
        Returns:
            bool: True if the notification is delivered, False otherwise.
        """
        return self.status == NotificationStatus.DELIVERED

    def is_failed(self) -> bool:
        """
        Check if notification is failed.
        
        Returns:
            bool: True if the notification is failed, False otherwise.
        """
        return self.status == NotificationStatus.FAILED

    def can_retry(self) -> bool:
        """
        Check if notification can be retried.
        
        Returns:
            bool: True if the notification can be retried, False otherwise.
        """
        return (
            self.retry_count < self.max_retries and
            self.status == NotificationStatus.FAILED
        )

    def render_content(self) -> str:
        """
        Render notification content with template data.
        
        Returns:
            str: The rendered notification content.
        """
        return self.template.render(self.data)


@dataclass
class NotificationBatch(Entity[NotificationId]):
    """
    Notification batch entity for bulk notifications.
    
    Attributes:
        id (NotificationId): The ID of the notification batch.
        name (str): The name of the notification batch.
        template (NotificationTemplate): The template of the notification batch.
        type (NotificationType): The type of the notification batch.
        recipients (List[NotificationRecipient]): The recipients of the notification batch.
        total_count (int): The total number of notifications in the batch.
        description (Optional[str]): The description of the notification batch.
        priority (NotificationPriority): The priority of the notification batch.
        data (Dict[str, Any]): The data of the notification batch.
        scheduled_at (Optional[datetime]): The scheduled date and time of the notification batch.
        status (str): The status of the notification batch.
        sent_count (int): The number of notifications sent.
        failed_count (int): The number of notifications failed.
        created_at (datetime): The date and time the notification batch was created.
        completed_at (Optional[datetime]): The date and time the notification batch was completed.
    """

    id: NotificationId
    name: str
    template: NotificationTemplate
    type: NotificationType
    recipients: List[NotificationRecipient] = field(default_factory=list)
    total_count: int = 0
    description: Optional[str] = None
    priority: NotificationPriority = NotificationPriority.NORMAL
    data: Dict[str, Any] = field(default_factory=dict)
    scheduled_at: Optional[datetime] = None
    status: str = "pending"
    sent_count: int = 0
    failed_count: int = 0
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    completed_at: Optional[datetime] = None

    def start_processing(self) -> None:
        """Start batch processing."""
        self.status = "processing"

    def complete(self) -> None:
        """Mark batch as completed."""
        self.status = "completed"
        self.completed_at = datetime.now(UTC)

    def fail(self) -> None:
        """Mark batch as failed."""
        self.status = "failed"
        self.completed_at = datetime.now(UTC)

    def increment_sent(self) -> None:
        """Increment sent count."""
        self.sent_count += 1

    def increment_failed(self) -> None:
        """Increment failed count."""
        self.failed_count += 1

    def get_progress(self) -> float:
        """
        Get batch progress percentage.
        
        Returns:
            float: The progress percentage of the notification batch.
        """
        if self.total_count == 0:
            return 0.0
        return (self.sent_count + self.failed_count) / self.total_count * 100

    def is_completed(self) -> bool:
        """
        Check if batch is completed.
        
        Returns:
            bool: True if the notification batch is completed, False otherwise.
        """
        return self.status == "completed"

    def is_failed(self) -> bool:
        """
        Check if batch is failed.
        
        Returns:
            bool: True if the notification batch is failed, False otherwise.
        """
        return self.status == "failed"


@dataclass
class NotificationSubscription(Entity[NotificationId]):
    """
    Notification subscription entity.
    
    Attributes:
        id (NotificationId): The ID of the notification subscription.
        user_id (str): The ID of the user.
        event_type (str): The type of the event.
        channels (List[NotificationType]): The channels of the notification subscription.
        is_active (bool): Whether the notification subscription is active.
        created_at (datetime): The date and time the notification subscription was created.
        updated_at (Optional[datetime]): The date and time the notification subscription was updated.
    """

    id: NotificationId
    user_id: str
    event_type: str
    channels: List[NotificationType] = field(default_factory=list)
    is_active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: Optional[datetime] = None

    def activate(self) -> None:
        """Activate subscription."""
        self.is_active = True
        self.updated_at = datetime.now(UTC)

    def deactivate(self) -> None:
        """Deactivate subscription."""
        self.is_active = False
        self.updated_at = datetime.now(UTC)

    def add_channel(self, channel: NotificationType) -> None:
        """Add notification channel.
        
        Args:
            channel (NotificationType): The channel to add.
        """
        if channel not in self.channels:
            self.channels.append(channel)
            self.updated_at = datetime.now(UTC)

    def remove_channel(self, channel: NotificationType) -> None:
        """Remove notification channel.
        
        Args:
            channel (NotificationType): The channel to remove.
        """
        if channel in self.channels:
            self.channels.remove(channel)
            self.updated_at = datetime.now(UTC)

    def supports_channel(self, channel: NotificationType) -> bool:
        """Check if subscription supports specific channel.
        
        Args:
            channel (NotificationType): The channel to check.

        Returns:
            bool: True if the notification subscription supports the channel, False otherwise.
        """
        return channel in self.channels
