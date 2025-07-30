"""Authentication domain module."""

from .entities import TokenPair, UserSession
from .events import (
    AccountLocked,
    AccountUnlocked,
    FailedLoginAttempt,
    PasswordChanged,
    SessionExpired,
    TokenRevoked,
    UserLoggedIn,
    UserLoggedOut,
)
from .repositories import SessionRepository, TokenRepository
from .value_objects import (
    AccessToken,
    Password,
    RefreshToken,
    TokenId,
    TokenType,
    Username,
)

__all__ = [
    # Entities
    "TokenPair",
    "UserSession",
    # Events
    "UserLoggedIn",
    "UserLoggedOut",
    "TokenRevoked",
    "SessionExpired",
    "FailedLoginAttempt",
    "PasswordChanged",
    "AccountLocked",
    "AccountUnlocked",
    # Repositories
    "TokenRepository",
    "SessionRepository",
    # Value Objects
    "TokenId",
    "AccessToken",
    "RefreshToken",
    "TokenType",
    "Password",
    "Username",
] 