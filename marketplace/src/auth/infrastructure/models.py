"""SQLAlchemy models for authentication domain."""

from sqlalchemy import Boolean, Column, DateTime, String, Text
from sqlalchemy.orm import relationship

from src.shared.infrastructure.models import Base, TimestampMixin


class TokenPairModel(Base, TimestampMixin):
    """SQLAlchemy model for TokenPair entity."""
    
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
    """SQLAlchemy model for UserSession entity."""
    
    __tablename__ = "user_sessions"
    
    id = Column(String(36), primary_key=True, index=True)
    user_id = Column(String(36), nullable=False, index=True)
    refresh_token = Column(Text, nullable=False)
    ip_address = Column(String(45), nullable=False)  # IPv6 compatible
    user_agent = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    last_activity = Column(DateTime, nullable=False)
    refresh_token_expires_at = Column(DateTime, nullable=False) 