"""Base SQLAlchemy models for domain entities."""

from datetime import datetime
from typing import Any, Dict

from sqlalchemy import Column, DateTime, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }


class TimestampMixin:
    """Mixin for adding timestamp fields."""
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class SoftDeleteMixin:
    """Mixin for soft delete functionality."""
    
    deleted_at = Column(DateTime, nullable=True)


# Base for all domain models
DomainBase = declarative_base(cls=Base) 