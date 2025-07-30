"""Value objects for notifications domain."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional

from src.shared.domain.value_object import ValueObject


@dataclass(frozen=True)
class NotificationId(ValueObject):
    """Notification ID value object."""

    value: str

    @classmethod
    def generate(cls) -> "NotificationId":
        """Generate a new notification ID."""
        import uuid
        return cls(value=f"notification_{uuid.uuid4().hex}")


class NotificationType(Enum):
    """Notification type enumeration."""

    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    IN_APP = "in_app"
    WEBHOOK = "webhook"


class NotificationStatus(Enum):
    """Notification status enumeration."""

    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    CANCELLED = "cancelled"


class NotificationPriority(Enum):
    """Notification priority enumeration."""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


@dataclass(frozen=True)
class NotificationTemplate(ValueObject):
    """Notification template value object."""

    name: str
    content: str
    subject: Optional[str] = None
    variables: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate notification template after initialization."""
        if not self.name or len(self.name.strip()) < 3:
            raise ValueError("Template name must be at least 3 characters long")
        if not self.content or len(self.content.strip()) < 10:
            raise ValueError("Template content must be at least 10 characters long")

        # Normalize template fields
        object.__setattr__(self, "name", self.name.strip())
        object.__setattr__(self, "content", self.content.strip())
        if self.subject:
            object.__setattr__(self, "subject", self.subject.strip())

    def render(self, data: Dict[str, Any]) -> str:
        """Render template with provided data."""
        content = self.content
        for key, value in data.items():
            placeholder = f"{{{{{key}}}}}"
            content = content.replace(placeholder, str(value))
        return content


@dataclass(frozen=True)
class NotificationChannel(ValueObject):
    """Notification channel value object."""

    type: NotificationType
    config: Dict[str, Any] = field(default_factory=dict)
    is_active: bool = True

    def __post_init__(self) -> None:
        """Initialize with default values if needed."""
        if self.config is None:
            object.__setattr__(self, "config", {})

    def activate(self) -> "NotificationChannel":
        """Activate notification channel and return new instance."""
        return self.__class__(
            type=self.type,
            config=self.config,
            is_active=True
        )

    def deactivate(self) -> "NotificationChannel":
        """Deactivate notification channel and return new instance."""
        return self.__class__(
            type=self.type,
            config=self.config,
            is_active=False
        )

    def update_config(self, config: Dict[str, Any]) -> "NotificationChannel":
        """Update channel configuration and return new instance."""
        new_config = self.config.copy()
        new_config.update(config)
        return self.__class__(
            type=self.type,
            config=new_config,
            is_active=self.is_active
        )


@dataclass(frozen=True)
class NotificationRecipient(ValueObject):
    """Notification recipient value object."""

    user_id: str
    email: Optional[str] = None
    phone: Optional[str] = None
    push_token: Optional[str] = None
    preferences: Dict[str, bool] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate notification recipient after initialization."""
        if not self.user_id or not self.user_id.strip():
            raise ValueError("User ID cannot be empty")
        if self.email and "@" not in self.email:
            raise ValueError("Invalid email format")

        # Normalize user ID
        object.__setattr__(self, "user_id", self.user_id.strip())

        # Initialize preferences if None
        if self.preferences is None:
            object.__setattr__(self, "preferences", {})

    def can_receive(self, notification_type: NotificationType) -> bool:
        """Check if recipient can receive specific notification type."""
        preference_key = f"enable_{notification_type.value}"
        return self.preferences.get(preference_key, True)

    def update_preference(
        self, notification_type: NotificationType, enabled: bool
    ) -> "NotificationRecipient":
        """Update notification preference and return new instance."""
        preference_key = f"enable_{notification_type.value}"
        new_preferences = self.preferences.copy()
        new_preferences[preference_key] = enabled
        return NotificationRecipient(
            email=self.email,
            phone=self.phone,
            push_token=self.push_token,
            preferences=new_preferences
        )
