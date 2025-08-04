"""Domain events for authentication."""

# Python imports
from datetime import datetime
from typing import Any

# Local imports
from src.shared.domain.events import DomainEvent


class UserLoggedIn(DomainEvent):
    """
    Event raised when user logs in.
    
    Attributes:
        user_id: The user ID.
        ip_address: The IP address of the session.
        user_agent: The user agent of the session.
        timestamp: The timestamp of the event.
    """

    user_id: str
    ip_address: str
    user_agent: str
    timestamp: datetime

    def __init__(self, **data: dict[str, Any]):
        """Initialize UserLoggedIn event."""
        super().__init__(
            event_type="UserLoggedIn",
            aggregate_id=data.get("user_id", ""),
            **data
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert event to dictionary representation."""
        return {
            "event_id": str(self.event_id),
            "event_type": self.event_type,
            "aggregate_id": self.aggregate_id,
            "occurred_on": self.occurred_on.isoformat(),
            "version": self.version,
            "user_id": self.user_id,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "timestamp": self.timestamp.isoformat(),
        }


class UserLoggedOut(DomainEvent):
    """
    Event raised when user logs out.
    
    Attributes:
        user_id: The user ID.
        session_id: The session ID.
        timestamp: The timestamp of the event.
    """

    user_id: str
    session_id: str
    timestamp: datetime

    def __init__(self, **data: dict[str, Any]):
        """Initialize UserLoggedOut event."""
        super().__init__(
            event_type="UserLoggedOut",
            aggregate_id=data.get("user_id", ""),
            **data
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert event to dictionary representation."""
        return {
            "event_id": str(self.event_id),
            "event_type": self.event_type,
            "aggregate_id": self.aggregate_id,
            "occurred_on": self.occurred_on.isoformat(),
            "version": self.version,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "timestamp": self.timestamp.isoformat(),
        }


class TokenRevoked(DomainEvent):
    """Event raised when token is revoked.
    
    Attributes:
        user_id: The user ID.
        token_id: The token ID.
        reason: The reason for revoking the token.
        timestamp: The timestamp of the event.
    """

    user_id: str
    token_id: str
    reason: str
    timestamp: datetime

    def __init__(self, **data: dict[str, Any]):
        """Initialize TokenRevoked event."""
        super().__init__(
            event_type="TokenRevoked",
            aggregate_id=data.get("user_id", ""),
            **data
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert event to dictionary representation."""
        return {
            "event_id": str(self.event_id),
            "event_type": self.event_type,
            "aggregate_id": self.aggregate_id,
            "occurred_on": self.occurred_on.isoformat(),
            "version": self.version,
            "user_id": self.user_id,
            "token_id": self.token_id,
            "reason": self.reason,
            "timestamp": self.timestamp.isoformat(),
        }


class SessionExpired(DomainEvent):
    """Event raised when session expires.
    
    Attributes:
        user_id: The user ID.
        session_id: The session ID.
        timestamp: The timestamp of the event.
    """

    user_id: str
    session_id: str
    timestamp: datetime

    def __init__(self, **data: dict[str, Any]):
        """Initialize SessionExpired event."""
        super().__init__(
            event_type="SessionExpired",
            aggregate_id=data.get("user_id", ""),
            **data
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert event to dictionary representation."""
        return {
            "event_id": str(self.event_id),
            "event_type": self.event_type,
            "aggregate_id": self.aggregate_id,
            "occurred_on": self.occurred_on.isoformat(),
            "version": self.version,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "timestamp": self.timestamp.isoformat(),
        }


class FailedLoginAttempt(DomainEvent):
    """Event raised when login attempt fails.
    
    Attributes:
        email: The email of the user.
        ip_address: The IP address of the session.
        user_agent: The user agent of the session.
        reason: The reason for the failed login attempt.
        timestamp: The timestamp of the event.
    """

    email: str
    ip_address: str
    user_agent: str
    reason: str
    timestamp: datetime

    def __init__(self, **data: dict[str, Any]):
        """Initialize FailedLoginAttempt event."""
        super().__init__(
            event_type="FailedLoginAttempt",
            aggregate_id=data.get("email", ""),
            **data
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert event to dictionary representation."""
        return {
            "event_id": str(self.event_id),
            "event_type": self.event_type,
            "aggregate_id": self.aggregate_id,
            "occurred_on": self.occurred_on.isoformat(),
            "version": self.version,
            "email": self.email,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "reason": self.reason,
            "timestamp": self.timestamp.isoformat(),
        }


class PasswordChanged(DomainEvent):
    """Event raised when password is changed.
    
    Attributes:
        user_id: The user ID.
        timestamp: The timestamp of the event.
    """

    user_id: str
    timestamp: datetime

    def __init__(self, **data: dict[str, Any]):
        """Initialize PasswordChanged event."""
        super().__init__(
            event_type="PasswordChanged",
            aggregate_id=data.get("user_id", ""),
            **data
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert event to dictionary representation."""
        return {
            "event_id": str(self.event_id),
            "event_type": self.event_type,
            "aggregate_id": self.aggregate_id,
            "occurred_on": self.occurred_on.isoformat(),
            "version": self.version,
            "user_id": self.user_id,
            "timestamp": self.timestamp.isoformat(),
        }


class AccountLocked(DomainEvent):
    """Event raised when account is locked.
    
    Attributes:
        user_id: The user ID.
        reason: The reason for locking the account.
        timestamp: The timestamp of the event.
    """

    user_id: str
    reason: str
    timestamp: datetime

    def __init__(self, **data: dict[str, Any]):
        """Initialize AccountLocked event."""
        super().__init__(
            event_type="AccountLocked",
            aggregate_id=data.get("user_id", ""),
            **data
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert event to dictionary representation."""
        return {
            "event_id": str(self.event_id),
            "event_type": self.event_type,
            "aggregate_id": self.aggregate_id,
            "occurred_on": self.occurred_on.isoformat(),
            "version": self.version,
            "user_id": self.user_id,
            "reason": self.reason,
            "timestamp": self.timestamp.isoformat(),
        }


class AccountUnlocked(DomainEvent):
    """Event raised when account is unlocked.
    
    Attributes:
        user_id: The user ID.
        timestamp: The timestamp of the event.
    """

    user_id: str
    timestamp: datetime

    def __init__(self, **data: dict[str, Any]):
        """Initialize AccountUnlocked event."""
        super().__init__(
            event_type="AccountUnlocked",
            aggregate_id=data.get("user_id", ""),
            **data
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert event to dictionary representation."""
        return {
            "event_id": str(self.event_id),
            "event_type": self.event_type,
            "aggregate_id": self.aggregate_id,
            "occurred_on": self.occurred_on.isoformat(),
            "version": self.version,
            "user_id": self.user_id,
            "timestamp": self.timestamp.isoformat(),
        } 