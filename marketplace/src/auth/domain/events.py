"""Domain events for authentication."""

# Python imports
from dataclasses import dataclass
from datetime import datetime

# Local imports
from src.shared.domain.events import DomainEvent


@dataclass
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


@dataclass
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


@dataclass
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


@dataclass
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


@dataclass
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


@dataclass
class PasswordChanged(DomainEvent):
    """Event raised when password is changed.
    
    Attributes:
        user_id: The user ID.
        timestamp: The timestamp of the event.
    """

    user_id: str
    timestamp: datetime


@dataclass
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


@dataclass
class AccountUnlocked(DomainEvent):
    """Event raised when account is unlocked.
    
    Attributes:
        user_id: The user ID.
        timestamp: The timestamp of the event.
    """

    user_id: str
    timestamp: datetime 