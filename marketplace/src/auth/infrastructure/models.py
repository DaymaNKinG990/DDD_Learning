"""SQLAlchemy models for authentication domain."""

# Python imports
from sqlalchemy import Boolean, Column, DateTime, String, Text

# Local imports
from src.shared.infrastructure.models import Base, TimestampMixin


class TokenPairModel(Base, TimestampMixin):
    """
    SQLAlchemy model for TokenPair entity.
    
    Attributes:
        id: The token pair ID.
        user_id: The user ID.
        access_token: The access token.
        refresh_token: The refresh token.
        token_type: The token type.
        is_revoked: Whether the token pair is revoked.
        access_token_expires_at: The access token expiration date.
        refresh_token_expires_at: The refresh token expiration date.
    """
    
    __tablename__ = "token_pairs"
    
    id = Column(String(36), primary_key=True, index=True)
    user_id = Column(String(36), nullable=False, index=True)
    access_token = Column(Text, nullable=False)
    refresh_token = Column(Text, nullable=False)
    token_type = Column(String(20), nullable=False)
    is_revoked = Column(Boolean, default=False, nullable=False)
    access_token_expires_at = Column(DateTime, nullable=False)
    refresh_token_expires_at = Column(DateTime, nullable=False)


class UserSessionModel(Base, TimestampMixin):
    """
    SQLAlchemy model for UserSession entity.
    
    Attributes:
        id: The session ID.
        user_id: The user ID.
        refresh_token: The refresh token.
        ip_address: The IP address of the session.
        user_agent: The user agent of the session.
        is_active: Whether the session is active.
        last_activity: The last activity timestamp.
        refresh_token_expires_at: The refresh token expiration date.
    """
    
    __tablename__ = "user_sessions"
    
    id = Column(String(36), primary_key=True, index=True)
    user_id = Column(String(36), nullable=False, index=True)
    refresh_token = Column(Text, nullable=False)
    ip_address = Column(String(45), nullable=False)  # IPv6 compatible
    user_agent = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    last_activity = Column(DateTime, nullable=False)
    refresh_token_expires_at = Column(DateTime, nullable=False) 