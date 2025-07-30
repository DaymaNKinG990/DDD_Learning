"""Entities for notifications domain."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Dict, List, Optional

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
    """Notification entity."""

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
        """Mark notification as failed."""
        self.status = NotificationStatus.FAILED
        self.error_message = error_message

    def retry(self) -> bool:
        """Retry sending notification."""
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
        """Check if notification is sent."""
        return self.status in [NotificationStatus.SENT, NotificationStatus.DELIVERED]

    def is_delivered(self) -> bool:
        """Check if notification is delivered."""
        return self.status == NotificationStatus.DELIVERED

    def is_failed(self) -> bool:
        """Check if notification is failed."""
        return self.status == NotificationStatus.FAILED

    def can_retry(self) -> bool:
        """Check if notification can be retried."""
        return (
            self.retry_count < self.max_retries and
            self.status == NotificationStatus.FAILED
        )

    def render_content(self) -> str:
        """Render notification content with template data."""
        return self.template.render(self.data)


@dataclass
class NotificationBatch(Entity[NotificationId]):
    """Notification batch entity for bulk notifications."""

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
        """Get batch progress percentage."""
        if self.total_count == 0:
            return 0.0
        return (self.sent_count + self.failed_count) / self.total_count * 100

    def is_completed(self) -> bool:
        """Check if batch is completed."""
        return self.status == "completed"

    def is_failed(self) -> bool:
        """Check if batch is failed."""
        return self.status == "failed"


@dataclass
class NotificationSubscription(Entity[NotificationId]):
    """Notification subscription entity."""

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
        """Add notification channel."""
        if channel not in self.channels:
            self.channels.append(channel)
            self.updated_at = datetime.now(UTC)

    def remove_channel(self, channel: NotificationType) -> None:
        """Remove notification channel."""
        if channel in self.channels:
            self.channels.remove(channel)
            self.updated_at = datetime.now(UTC)

    def supports_channel(self, channel: NotificationType) -> bool:
        """Check if subscription supports specific channel."""
        return channel in self.channels
