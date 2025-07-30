"""Domain entities for authentication."""

# Python imports
from dataclasses import dataclass, field
from datetime import datetime, timezone

# Local imports
from src.auth.domain.value_objects import AccessToken, RefreshToken, TokenId, TokenType
from src.shared.domain.entity import Entity
from src.users.domain.value_objects import UserId


@dataclass
class TokenPair(Entity[TokenId]):
    """
    Token pair entity (access + refresh tokens).
    
    Attributes:
        id: The token pair ID.
        user_id: The user ID.
        access_token: The access token.
        refresh_token: The refresh token.
        token_type: The token type.
        is_revoked: Whether the token pair is revoked.
        created_at: The creation timestamp.
        updated_at: The last update timestamp.
    """
    
    id: TokenId
    user_id: UserId
    access_token: AccessToken
    refresh_token: RefreshToken
    token_type: TokenType
    is_revoked: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def revoke(self) -> None:
        """Revoke the token pair."""
        self.is_revoked = True
        self.updated_at = datetime.now(timezone.utc)
    
    @property
    def is_expired(self) -> bool:
        """
        Check if token pair is expired.
        
        Returns:
            bool: True if token pair is expired, False otherwise.
        """
        return self.access_token.is_expired or self.refresh_token.is_expired
    
    @property
    def is_valid(self) -> bool:
        """
        Check if token pair is valid.
        
        Returns:
            bool: True if token pair is valid, False otherwise.
        """
        return not self.is_revoked and not self.is_expired


@dataclass
class UserSession(Entity[TokenId]):
    """
    User session entity.
    
    Attributes:
        id: The session ID.
        user_id: The user ID.
        refresh_token: The refresh token.
        ip_address: The IP address of the session.
        user_agent: The user agent of the session.
        is_active: Whether the session is active.
        created_at: The creation timestamp.
        last_activity: The last activity timestamp.
    """
    
    id: TokenId
    user_id: UserId
    refresh_token: RefreshToken
    ip_address: str
    user_agent: str
    is_active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_activity: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    
    def deactivate(self) -> None:
        """Deactivate the session."""
        self.is_active = False
        self.last_activity = datetime.now(timezone.utc)
    
    def update_activity(self) -> None:
        """Update last activity timestamp."""
        self.last_activity = datetime.now(timezone.utc)
    
    @property
    def is_expired(self) -> bool:
        """
        Check if session is expired.
        
        Returns:
            bool: True if session is expired, False otherwise.
        """
        return self.refresh_token.is_expired
    
    @property
    def is_valid(self) -> bool:
        """
        Check if session is valid.
        
        Returns:
            bool: True if session is valid, False otherwise.
        """
        return self.is_active and not self.is_expired 