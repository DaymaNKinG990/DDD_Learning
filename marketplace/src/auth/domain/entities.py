"""Domain entities for authentication."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from src.auth.domain.value_objects import AccessToken, RefreshToken, TokenId, TokenType
from src.shared.domain.entity import Entity
from src.users.domain.value_objects import UserId


@dataclass
class TokenPair(Entity[TokenId]):
    """Token pair entity (access + refresh tokens)."""
    
    id: TokenId
    user_id: UserId
    access_token: AccessToken
    refresh_token: RefreshToken
    token_type: TokenType
    is_revoked: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def revoke(self) -> None:
        """Revoke the token pair."""
        self.is_revoked = True
        self.updated_at = datetime.utcnow()
    
    @property
    def is_expired(self) -> bool:
        """Check if token pair is expired."""
        return self.access_token.is_expired or self.refresh_token.is_expired
    
    @property
    def is_valid(self) -> bool:
        """Check if token pair is valid."""
        return not self.is_revoked and not self.is_expired


@dataclass
class UserSession(Entity[TokenId]):
    """User session entity."""
    
    id: TokenId
    user_id: UserId
    refresh_token: RefreshToken
    ip_address: str
    user_agent: str
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_activity: datetime = field(default_factory=datetime.utcnow)
    
    def deactivate(self) -> None:
        """Deactivate the session."""
        self.is_active = False
        self.last_activity = datetime.utcnow()
    
    def update_activity(self) -> None:
        """Update last activity timestamp."""
        self.last_activity = datetime.utcnow()
    
    @property
    def is_expired(self) -> bool:
        """Check if session is expired."""
        return self.refresh_token.is_expired
    
    @property
    def is_valid(self) -> bool:
        """Check if session is valid."""
        return self.is_active and not self.is_expired 