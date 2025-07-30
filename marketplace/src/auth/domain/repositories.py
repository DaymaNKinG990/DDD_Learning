"""Repository interfaces for authentication domain."""

# Python imports
from abc import ABC, abstractmethod
from typing import List, Optional

# Local imports
from src.auth.domain.entities import TokenPair, UserSession
from src.auth.domain.value_objects import TokenId
from src.users.domain.value_objects import UserId


class TokenRepository(ABC):
    """Repository interface for token management.
    
    This interface defines the methods for managing token pairs.
    """
    
    @abstractmethod
    async def save(self, token_pair: TokenPair) -> TokenPair:
        """
        Save token pair.
        
        Args:
            token_pair: The token pair to save.
            
        Returns:
            TokenPair: The saved token pair.
        """
        pass
    
    @abstractmethod
    async def get_by_id(self, token_id: TokenId) -> Optional[TokenPair]:
        """
        Get token pair by ID.
        
        Args:
            token_id: The ID of the token pair to get.
            
        Returns:
            Optional[TokenPair]: The token pair if found, None otherwise.
        """
        pass
    
    @abstractmethod
    async def get_by_user_id(self, user_id: UserId) -> List[TokenPair]:
        """
        Get all token pairs for a user.
        
        Args:
            user_id: The ID of the user to get token pairs for.
            
        Returns:
            List[TokenPair]: The list of token pairs for the user.
        """
        pass
    
    @abstractmethod
    async def get_by_access_token(self, access_token: str) -> Optional[TokenPair]:
        """
        Get token pair by access token.
        
        Args:
            access_token: The access token to get the token pair for.
            
        Returns:
            Optional[TokenPair]: The token pair if found, None otherwise.
        """
        pass
    
    @abstractmethod
    async def get_by_refresh_token(self, refresh_token: str) -> Optional[TokenPair]:
        """
        Get token pair by refresh token.
        
        Args:
            refresh_token: The refresh token to get the token pair for.
            
        Returns:
            Optional[TokenPair]: The token pair if found, None otherwise.
        """
        pass
    
    @abstractmethod
    async def revoke_token(self, token_id: TokenId) -> bool:
        """
        Revoke a token pair.
        
        Args:
            token_id: The ID of the token pair to revoke.
            
        Returns:
            bool: True if the token pair was revoked, False otherwise.
        """
        pass
    
    @abstractmethod
    async def revoke_all_user_tokens(self, user_id: UserId) -> bool:
        """
        Revoke all tokens for a user.
        
        Args:
            user_id: The ID of the user to revoke tokens for.
            
        Returns:
            bool: True if all tokens were revoked, False otherwise.
        """
        pass
    
    @abstractmethod
    async def delete_expired_tokens(self) -> int:
        """
        Delete expired tokens and return count of deleted tokens.
        
        Returns:
            int: The number of deleted tokens.
        """
        pass


class SessionRepository(ABC):
    """Repository interface for session management.
    
    This interface defines the methods for managing user sessions.
    """
    
    @abstractmethod
    async def save(self, session: UserSession) -> UserSession:
        """
        Save user session.
        
        Args:
            session: The user session to save.
            
        Returns:
            UserSession: The saved user session.
        """
        pass
    
    @abstractmethod
    async def get_by_id(self, session_id: TokenId) -> Optional[UserSession]:
        """
        Get session by ID.
        
        Args:
            session_id: The ID of the session to get.
            
        Returns:
            Optional[UserSession]: The session if found, None otherwise.
        """
        pass
    
    @abstractmethod
    async def get_by_user_id(self, user_id: UserId) -> List[UserSession]:
        """
        Get all sessions for a user.
        
        Args:
            user_id: The ID of the user to get sessions for.
            
        Returns:
            List[UserSession]: The list of sessions for the user.
        """
        pass
    
    @abstractmethod
    async def get_by_refresh_token(self, refresh_token: str) -> Optional[UserSession]:
        """
        Get session by refresh token.
        
        Args:
            refresh_token: The refresh token to get the session for.
            
        Returns:
            Optional[UserSession]: The session if found, None otherwise.
        """
        pass
    
    @abstractmethod
    async def deactivate_session(self, session_id: TokenId) -> bool:
        """
        Deactivate a session.
        
        Args:
            session_id: The ID of the session to deactivate.
            
        Returns:
            bool: True if the session was deactivated, False otherwise.
        """
        pass
    
    @abstractmethod
    async def deactivate_all_user_sessions(self, user_id: UserId) -> bool:
        """
        Deactivate all sessions for a user.
        
        Args:
            user_id: The ID of the user to deactivate sessions for.
            
        Returns:
            bool: True if all sessions were deactivated, False otherwise.
        """
        pass
    
    @abstractmethod
    async def update_session_activity(self, session_id: TokenId) -> bool:
        """
        Update session last activity.
        
        Args:
            session_id: The ID of the session to update.
            
        Returns:
            bool: True if the session activity was updated, False otherwise.
        """
        pass
    
    @abstractmethod
    async def delete_expired_sessions(self) -> int:
        """
        Delete expired sessions and return count of deleted sessions.
        
        Returns:
            int: The number of deleted sessions.
        """
        pass 