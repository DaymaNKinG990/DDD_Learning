"""Base SQLAlchemy models for domain entities."""

# Python imports
from datetime import UTC, datetime
from typing import Any, Dict
from sqlalchemy import Column, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy models.

    Attributes:
        to_dict: Convert model to dictionary.
    """
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert model to dictionary.

        Returns:
            Dict[str, Any]: The model as a dictionary.
        """
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }


class TimestampMixin:
    """
    Mixin for adding timestamp fields.

    Attributes:
        created_at: The creation timestamp.
        updated_at: The update timestamp.
    """
    
    created_at = Column(DateTime, default=lambda: datetime.now(UTC), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC), nullable=False)


class SoftDeleteMixin:
    """
    Mixin for soft delete functionality.

    Attributes:
        deleted_at: The deletion timestamp.
    """
    
    deleted_at = Column(DateTime, nullable=True)


# Base for all domain models
DomainBase = declarative_base(cls=Base) 