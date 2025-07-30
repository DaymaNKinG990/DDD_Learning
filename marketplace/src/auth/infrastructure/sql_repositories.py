"""SQLAlchemy repository implementations for authentication domain."""

from typing import List, Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.domain.entities import TokenPair, UserSession
from src.auth.domain.repositories import SessionRepository, TokenRepository
from src.auth.domain.value_objects import TokenId, TokenType
from src.auth.infrastructure.models import TokenPairModel, UserSessionModel
from src.shared.infrastructure.sql_repositories import SQLRepository
from src.users.domain.value_objects import UserId


class SQLTokenRepository(SQLRepository[TokenPairModel], TokenRepository):
    """SQLAlchemy implementation of TokenRepository."""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, TokenPairModel)
    
    async def save(self, token_pair: TokenPair) -> TokenPair:
        """Save token pair to database."""
        token_model = TokenPairModel(
            id=token_pair.id.value,
            user_id=token_pair.user_id.value,
            access_token=token_pair.access_token.value,
            refresh_token=token_pair.refresh_token.value,
            token_type=token_pair.token_type.value,
            is_revoked=token_pair.is_revoked,
            access_token_expires_at=token_pair.access_token.expires_at,
            refresh_token_expires_at=token_pair.refresh_token.expires_at,
        )
        
        saved_model = await super().save(token_model)
        
        return TokenPair(
            id=TokenId(value=saved_model.id),
            user_id=UserId(value=saved_model.user_id),
            access_token=saved_model.access_token,
            refresh_token=saved_model.refresh_token,
            token_type=TokenType(saved_model.token_type),
            is_revoked=saved_model.is_revoked,
            created_at=saved_model.created_at,
            updated_at=saved_model.updated_at,
        )
    
    async def get_by_id(self, token_id: TokenId) -> Optional[TokenPair]:
        """Get token pair by ID."""
        token_model = await super().get_by_id(token_id.value)
        if not token_model:
            return None
        
        return self._model_to_entity(token_model)
    
    async def get_by_user_id(self, user_id: UserId) -> List[TokenPair]:
        """Get all token pairs for a user."""
        stmt = select(TokenPairModel).where(TokenPairModel.user_id == user_id.value)
        result = await self.session.execute(stmt)
        token_models = result.scalars().all()
        
        return [self._model_to_entity(model) for model in token_models]
    
    async def get_by_access_token(self, access_token: str) -> Optional[TokenPair]:
        """Get token pair by access token."""
        stmt = select(TokenPairModel).where(TokenPairModel.access_token == access_token)
        result = await self.session.execute(stmt)
        token_model = result.scalar_one_or_none()
        
        if not token_model:
            return None
        
        return self._model_to_entity(token_model)
    
    async def get_by_refresh_token(self, refresh_token: str) -> Optional[TokenPair]:
        """Get token pair by refresh token."""
        stmt = select(TokenPairModel).where(TokenPairModel.refresh_token == refresh_token)
        result = await self.session.execute(stmt)
        token_model = result.scalar_one_or_none()
        
        if not token_model:
            return None
        
        return self._model_to_entity(token_model)
    
    async def revoke_token(self, token_id: TokenId) -> bool:
        """Revoke a token pair."""
        stmt = (
            update(TokenPairModel)
            .where(TokenPairModel.id == token_id.value)
            .values(is_revoked=True)
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount > 0
    
    async def revoke_all_user_tokens(self, user_id: UserId) -> bool:
        """Revoke all tokens for a user."""
        stmt = (
            update(TokenPairModel)
            .where(TokenPairModel.user_id == user_id.value)
            .values(is_revoked=True)
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount > 0
    
    async def delete_expired_tokens(self) -> int:
        """Delete expired tokens and return count of deleted tokens."""
        from datetime import datetime
        
        stmt = select(TokenPairModel).where(
            (TokenPairModel.access_token_expires_at < datetime.utcnow()) |
            (TokenPairModel.refresh_token_expires_at < datetime.utcnow())
        )
        result = await self.session.execute(stmt)
        expired_tokens = result.scalars().all()
        
        for token in expired_tokens:
            await self.session.delete(token)
        
        await self.session.commit()
        return len(expired_tokens)
    
    def _model_to_entity(self, model: TokenPairModel) -> TokenPair:
        """Convert SQLAlchemy model to domain entity."""
        from src.auth.domain.value_objects import AccessToken, RefreshToken
        
        return TokenPair(
            id=TokenId(value=model.id),
            user_id=UserId(value=model.user_id),
            access_token=AccessToken(value=model.access_token, expires_at=model.access_token_expires_at),
            refresh_token=RefreshToken(value=model.refresh_token, expires_at=model.refresh_token_expires_at),
            token_type=TokenType(model.token_type),
            is_revoked=model.is_revoked,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )


class SQLSessionRepository(SQLRepository[UserSessionModel], SessionRepository):
    """SQLAlchemy implementation of SessionRepository."""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, UserSessionModel)
    
    async def save(self, session: UserSession) -> UserSession:
        """Save user session to database."""
        session_model = UserSessionModel(
            id=session.id.value,
            user_id=session.user_id.value,
            refresh_token=session.refresh_token.value,
            ip_address=session.ip_address,
            user_agent=session.user_agent,
            is_active=session.is_active,
            last_activity=session.last_activity,
            refresh_token_expires_at=session.refresh_token.expires_at,
        )
        
        saved_model = await super().save(session_model)
        
        return self._model_to_entity(saved_model)
    
    async def get_by_id(self, session_id: TokenId) -> Optional[UserSession]:
        """Get session by ID."""
        session_model = await super().get_by_id(session_id.value)
        if not session_model:
            return None
        
        return self._model_to_entity(session_model)
    
    async def get_by_user_id(self, user_id: UserId) -> List[UserSession]:
        """Get all sessions for a user."""
        stmt = select(UserSessionModel).where(UserSessionModel.user_id == user_id.value)
        result = await self.session.execute(stmt)
        session_models = result.scalars().all()
        
        return [self._model_to_entity(model) for model in session_models]
    
    async def get_by_refresh_token(self, refresh_token: str) -> Optional[UserSession]:
        """Get session by refresh token."""
        stmt = select(UserSessionModel).where(UserSessionModel.refresh_token == refresh_token)
        result = await self.session.execute(stmt)
        session_model = result.scalar_one_or_none()
        
        if not session_model:
            return None
        
        return self._model_to_entity(session_model)
    
    async def deactivate_session(self, session_id: TokenId) -> bool:
        """Deactivate a session."""
        stmt = (
            update(UserSessionModel)
            .where(UserSessionModel.id == session_id.value)
            .values(is_active=False)
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount > 0
    
    async def deactivate_all_user_sessions(self, user_id: UserId) -> bool:
        """Deactivate all sessions for a user."""
        stmt = (
            update(UserSessionModel)
            .where(UserSessionModel.user_id == user_id.value)
            .values(is_active=False)
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount > 0
    
    async def update_session_activity(self, session_id: TokenId) -> bool:
        """Update session last activity."""
        from datetime import datetime
        
        stmt = (
            update(UserSessionModel)
            .where(UserSessionModel.id == session_id.value)
            .values(last_activity=datetime.utcnow())
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount > 0
    
    async def delete_expired_sessions(self) -> int:
        """Delete expired sessions and return count of deleted sessions."""
        from datetime import datetime
        
        stmt = select(UserSessionModel).where(
            UserSessionModel.refresh_token_expires_at < datetime.utcnow()
        )
        result = await self.session.execute(stmt)
        expired_sessions = result.scalars().all()
        
        for session in expired_sessions:
            await self.session.delete(session)
        
        await self.session.commit()
        return len(expired_sessions)
    
    def _model_to_entity(self, model: UserSessionModel) -> UserSession:
        """Convert SQLAlchemy model to domain entity."""
        from src.auth.domain.value_objects import RefreshToken
        
        return UserSession(
            id=TokenId(value=model.id),
            user_id=UserId(value=model.user_id),
            refresh_token=RefreshToken(value=model.refresh_token, expires_at=model.refresh_token_expires_at),
            ip_address=model.ip_address,
            user_agent=model.user_agent,
            is_active=model.is_active,
            created_at=model.created_at,
            last_activity=model.last_activity,
        ) 