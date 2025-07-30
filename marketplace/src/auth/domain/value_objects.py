"""Value objects for authentication domain."""

from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional


class TokenType(Enum):
    """Token types."""
    ACCESS = "access"
    REFRESH = "refresh"


@dataclass(frozen=True)
class TokenId:
    """Token ID value object."""
    value: str


@dataclass(frozen=True)
class AccessToken:
    """Access token value object."""
    value: str
    expires_at: datetime
    
    @property
    def is_expired(self) -> bool:
        """Check if token is expired."""
        return datetime.utcnow() > self.expires_at
    
    @classmethod
    def create(cls, value: str, expires_in_minutes: int = 30) -> "AccessToken":
        """Create a new access token."""
        expires_at = datetime.utcnow() + timedelta(minutes=expires_in_minutes)
        return cls(value=value, expires_at=expires_at)


@dataclass(frozen=True)
class RefreshToken:
    """Refresh token value object."""
    value: str
    expires_at: datetime
    
    @property
    def is_expired(self) -> bool:
        """Check if token is expired."""
        return datetime.utcnow() > self.expires_at
    
    @classmethod
    def create(cls, value: str, expires_in_days: int = 7) -> "RefreshToken":
        """Create a new refresh token."""
        expires_at = datetime.utcnow() + timedelta(days=expires_in_days)
        return cls(value=value, expires_at=expires_at)


@dataclass(frozen=True)
class Password:
    """Password value object."""
    value: str
    
    def __post_init__(self):
        """Validate password."""
        if len(self.value) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not any(c.isupper() for c in self.value):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in self.value):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in self.value):
            raise ValueError("Password must contain at least one digit")


@dataclass(frozen=True)
class Username:
    """Username value object."""
    value: str
    
    def __post_init__(self):
        """Validate username."""
        if len(self.value) < 3:
            raise ValueError("Username must be at least 3 characters long")
        if len(self.value) > 50:
            raise ValueError("Username must be at most 50 characters long")
        if not self.value.isalnum():
            raise ValueError("Username must contain only alphanumeric characters") 