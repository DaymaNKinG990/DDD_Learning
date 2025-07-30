"""Domain events for authentication."""

from dataclasses import dataclass
from datetime import datetime

from src.shared.domain.events import DomainEvent


@dataclass
class UserLoggedIn(DomainEvent):
    """Event raised when user logs in."""
    user_id: str
    ip_address: str
    user_agent: str
    timestamp: datetime


@dataclass
class UserLoggedOut(DomainEvent):
    """Event raised when user logs out."""
    user_id: str
    session_id: str
    timestamp: datetime


@dataclass
class TokenRevoked(DomainEvent):
    """Event raised when token is revoked."""
    user_id: str
    token_id: str
    reason: str
    timestamp: datetime


@dataclass
class SessionExpired(DomainEvent):
    """Event raised when session expires."""
    user_id: str
    session_id: str
    timestamp: datetime


@dataclass
class FailedLoginAttempt(DomainEvent):
    """Event raised when login attempt fails."""
    email: str
    ip_address: str
    user_agent: str
    reason: str
    timestamp: datetime


@dataclass
class PasswordChanged(DomainEvent):
    """Event raised when password is changed."""
    user_id: str
    timestamp: datetime


@dataclass
class AccountLocked(DomainEvent):
    """Event raised when account is locked."""
    user_id: str
    reason: str
    timestamp: datetime


@dataclass
class AccountUnlocked(DomainEvent):
    """Event raised when account is unlocked."""
    user_id: str
    timestamp: datetime 