"""Value objects for notifications domain."""

# Python imports
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional
import uuid

# Local imports
from src.shared.domain.value_object import ValueObject


@dataclass(frozen=True)
class NotificationId(ValueObject):
    """
    Notification ID value object.
    
    Attributes:
        value (str): The value of the notification ID.
    """

    value: str

    @classmethod
    def generate(cls) -> "NotificationId":
        """
        Generate a new notification ID.

        Returns:
            NotificationId: The generated notification ID.
        """
        return cls(value=f"notification_{uuid.uuid4().hex}")


class NotificationType(Enum):
    """
    Notification type enumeration.
    
    Attributes:
        EMAIL (str): The email notification type.
        SMS (str): The SMS notification type.
        PUSH (str): The push notification type.
        IN_APP (str): The in-app notification type.
        WEBHOOK (str): The webhook notification type.
    """

    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    IN_APP = "in_app"
    WEBHOOK = "webhook"


class NotificationStatus(Enum):
    """
    Notification status enumeration.
    
    Attributes:
        PENDING (str): The pending notification status.
        SENT (str): The sent notification status.
        DELIVERED (str): The delivered notification status.
        FAILED (str): The failed notification status.
        CANCELLED (str): The cancelled notification status.
    """

    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    CANCELLED = "cancelled"


class NotificationPriority(Enum):
    """
    Notification priority enumeration.
    
    Attributes:
        LOW (str): The low priority.
        NORMAL (str): The normal priority.
        HIGH (str): The high priority.
        URGENT (str): The urgent priority.
    """

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


@dataclass(frozen=True)
class NotificationTemplate(ValueObject):
    """
    Notification template value object.
    
    Attributes:
        name (str): The name of the template.
        content (str): The content of the template.
        subject (Optional[str]): The subject of the template.
        variables (Dict[str, str]): The variables of the template.
    """

    name: str
    content: str
    subject: Optional[str] = None
    variables: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """
        Validate notification template after initialization.
        
        Raises:
            ValueError: If the template name is not at least 3 characters long or the content is not at least 10 characters long.
        """
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
        """
        Render template with provided data.
        
        Args:
            data (Dict[str, Any]): The data to render the template with.

        Returns:
            str: The rendered template.
        """
        content = self.content
        for key, value in data.items():
            placeholder = f"{{{{{key}}}}}"
            content = content.replace(placeholder, str(value))
        return content


@dataclass(frozen=True)
class NotificationChannel(ValueObject):
    """
    Notification channel value object.
    
    Attributes:
        type (NotificationType): The type of the channel.
        config (Dict[str, Any]): The configuration of the channel.
        is_active (bool): Whether the channel is active.
    """

    type: NotificationType
    config: Dict[str, Any] = field(default_factory=dict)
    is_active: bool = True

    def __post_init__(self) -> None:
        """
        Initialize with default values if needed.
        
        Raises:
            ValueError: If the configuration is not a dictionary.
        """
        if self.config is None:
            object.__setattr__(self, "config", {})

    def activate(self) -> "NotificationChannel":
        """
        Activate notification channel and return new instance.
        
        Returns:
            NotificationChannel: The activated notification channel.
        """
        return self.__class__(
            type=self.type,
            config=self.config,
            is_active=True
        )

    def deactivate(self) -> "NotificationChannel":
        """
        Deactivate notification channel and return new instance.
        
        Returns:
            NotificationChannel: The deactivated notification channel.
        """
        return self.__class__(
            type=self.type,
            config=self.config,
            is_active=False
        )

    def update_config(self, config: Dict[str, Any]) -> "NotificationChannel":
        """
        Update channel configuration and return new instance.
        
        Args:
            config (Dict[str, Any]): The configuration to update.

        Returns:
            NotificationChannel: The updated notification channel.
        """
        new_config = self.config.copy()
        new_config.update(config)
        return self.__class__(
            type=self.type,
            config=new_config,
            is_active=self.is_active
        )


@dataclass(frozen=True)
class NotificationRecipient(ValueObject):
    """
    Notification recipient value object.
    
    Attributes:
        user_id (str): The ID of the user.
        email (Optional[str]): The email of the recipient.
        phone (Optional[str]): The phone number of the recipient.
        push_token (Optional[str]): The push token of the recipient.
        preferences (Dict[str, bool]): The preferences of the recipient.
    """

    user_id: str
    email: Optional[str] = None
    phone: Optional[str] = None
    push_token: Optional[str] = None
    preferences: Dict[str, bool] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """
        Validate notification recipient after initialization.
        
        Raises:
            ValueError: If the user ID is empty or the email is not valid.
        """
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
        """
        Check if recipient can receive specific notification type.
        
        Args:
            notification_type (NotificationType): The notification type to check.

        Returns:
            bool: True if the recipient can receive the notification type, False otherwise.
        """
        preference_key = f"enable_{notification_type.value}"
        return self.preferences.get(preference_key, True)

    def update_preference(
        self, notification_type: NotificationType, enabled: bool
    ) -> "NotificationRecipient":
        """Update notification preference and return new instance.
        
        Args:
            notification_type (NotificationType): The notification type to update.
            enabled (bool): Whether the notification type is enabled.

        Returns:
            NotificationRecipient: The updated notification recipient.
        """
        preference_key = f"enable_{notification_type.value}"
        new_preferences = self.preferences.copy()
        new_preferences[preference_key] = enabled
        return NotificationRecipient(
            email=self.email,
            phone=self.phone,
            push_token=self.push_token,
            preferences=new_preferences
        )
