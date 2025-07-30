"""Repository interfaces for authentication domain."""

from abc import ABC, abstractmethod
from typing import List, Optional

from src.auth.domain.entities import TokenPair, UserSession
from src.auth.domain.value_objects import TokenId
from src.users.domain.value_objects import UserId


class TokenRepository(ABC):
    """Repository interface for token management."""
    
    @abstractmethod
    async def save(self, token_pair: TokenPair) -> TokenPair:
        """Save token pair."""
        pass
    
    @abstractmethod
    async def get_by_id(self, token_id: TokenId) -> Optional[TokenPair]:
        """Get token pair by ID."""
        pass
    
    @abstractmethod
    async def get_by_user_id(self, user_id: UserId) -> List[TokenPair]:
        """Get all token pairs for a user."""
        pass
    
    @abstractmethod
    async def get_by_access_token(self, access_token: str) -> Optional[TokenPair]:
        """Get token pair by access token."""
        pass
    
    @abstractmethod
    async def get_by_refresh_token(self, refresh_token: str) -> Optional[TokenPair]:
        """Get token pair by refresh token."""
        pass
    
    @abstractmethod
    async def revoke_token(self, token_id: TokenId) -> bool:
        """Revoke a token pair."""
        pass
    
    @abstractmethod
    async def revoke_all_user_tokens(self, user_id: UserId) -> bool:
        """Revoke all tokens for a user."""
        pass
    
    @abstractmethod
    async def delete_expired_tokens(self) -> int:
        """Delete expired tokens and return count of deleted tokens."""
        pass


class SessionRepository(ABC):
    """Repository interface for session management."""
    
    @abstractmethod
    async def save(self, session: UserSession) -> UserSession:
        """Save user session."""
        pass
    
    @abstractmethod
    async def get_by_id(self, session_id: TokenId) -> Optional[UserSession]:
        """Get session by ID."""
        pass
    
    @abstractmethod
    async def get_by_user_id(self, user_id: UserId) -> List[UserSession]:
        """Get all sessions for a user."""
        pass
    
    @abstractmethod
    async def get_by_refresh_token(self, refresh_token: str) -> Optional[UserSession]:
        """Get session by refresh token."""
        pass
    
    @abstractmethod
    async def deactivate_session(self, session_id: TokenId) -> bool:
        """Deactivate a session."""
        pass
    
    @abstractmethod
    async def deactivate_all_user_sessions(self, user_id: UserId) -> bool:
        """Deactivate all sessions for a user."""
        pass
    
    @abstractmethod
    async def update_session_activity(self, session_id: TokenId) -> bool:
        """Update session last activity."""
        pass
    
    @abstractmethod
    async def delete_expired_sessions(self) -> int:
        """Delete expired sessions and return count of deleted sessions."""
        pass 