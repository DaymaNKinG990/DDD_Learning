"""Value objects for authentication domain."""

# Python imports
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum


class TokenType(Enum):
    """
    Token types.
    
    Attributes:
        ACCESS: The access token type.
        REFRESH: The refresh token type.
    """

    ACCESS = "access"
    REFRESH = "refresh"


@dataclass(frozen=True)
class TokenId:
    """
    Token ID value object.
    
    Attributes:
        value: The token ID.
    """

    value: str


@dataclass(frozen=True)
class AccessToken:
    """
    Access token value object.
    
    Attributes:
        value: The token value.
        expires_at: The token expiration date.
    """

    value: str
    expires_at: datetime
    
    @property
    def is_expired(self) -> bool:
        """
        Check if token is expired.
        
        Returns:
            bool: True if token is expired, False otherwise.
        """
        return datetime.now(timezone.utc) > self.expires_at
    
    @classmethod
    def create(cls, value: str, expires_in_minutes: int = 30) -> "AccessToken":
        """
        Create a new access token.
        
        Args:
            value: The token value.
            expires_in_minutes: The number of minutes the token is valid for.
            
        Returns:
            AccessToken: The new access token.
        """
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=expires_in_minutes)
        return cls(value=value, expires_at=expires_at)


@dataclass(frozen=True)
class RefreshToken:
    """
    Refresh token value object.
    
    Attributes:
        value: The token value.
        expires_at: The token expiration date.
    """

    value: str
    expires_at: datetime
    
    @property
    def is_expired(self) -> bool:
        """
        Check if token is expired.
        
        Returns:
            bool: True if token is expired, False otherwise.
        """
        return datetime.now(timezone.utc) > self.expires_at
    
    @classmethod
    def create(cls, value: str, expires_in_days: int = 7) -> "RefreshToken":
        """
        Create a new refresh token.
        
        Args:
            value: The token value.
            expires_in_days: The number of days the token is valid for.
            
        Returns:
            RefreshToken: The new refresh token.
        """
        expires_at = datetime.now(timezone.utc) + timedelta(days=expires_in_days)
        return cls(value=value, expires_at=expires_at)


@dataclass(frozen=True)
class Password:
    """
    Password value object.
    
    Attributes:
        value: The password.
    """

    value: str
    
    def __post_init__(self) -> None:
        """
        Validate password.
        
        Raises:
            ValueError: If password is not valid.
        """
        if len(self.value) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not any(map(str.isupper, self.value)):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(map(str.islower, self.value)):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(map(str.isdigit, self.value)):
            raise ValueError("Password must contain at least one digit")


@dataclass(frozen=True)
class Username:
    """
    Username value object.
    
    Attributes:
        value: The username.
    """

    value: str
    
    def __post_init__(self) -> None:
        """
        Validate username.
        
        Raises:
            ValueError: If username is not valid.
        """
        if len(self.value) < 3:
            raise ValueError("Username must be at least 3 characters long")
        if len(self.value) > 50:
            raise ValueError("Username must be at most 50 characters long")
        if not self.value.isalnum():
            raise ValueError("Username must contain only alphanumeric characters") 