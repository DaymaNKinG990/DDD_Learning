"""SQLAlchemy models for users domain."""

from sqlalchemy import Boolean, Column, DateTime, String, Text
from sqlalchemy.orm import relationship

from src.shared.infrastructure.models import Base, TimestampMixin


class UserModel(Base, TimestampMixin):
    """SQLAlchemy model for User entity."""
    
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    phone_number = Column(String(20), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    customer = relationship("CustomerModel", back_populates="user", uselist=False)
    seller = relationship("SellerModel", back_populates="user", uselist=False)


class CustomerModel(Base, TimestampMixin):
    """SQLAlchemy model for Customer entity."""
    
    __tablename__ = "customers"
    
    id = Column(String(36), primary_key=True, index=True)
    user_id = Column(String(36), nullable=False, index=True)
    shipping_address = Column(Text, nullable=False)
    billing_address = Column(Text, nullable=False)
    
    # Relationships
    user = relationship("UserModel", back_populates="customer")


class SellerModel(Base, TimestampMixin):
    """SQLAlchemy model for Seller entity."""
    
    __tablename__ = "sellers"
    
    id = Column(String(36), primary_key=True, index=True)
    user_id = Column(String(36), nullable=False, index=True)
    company_name = Column(String(255), nullable=False)
    company_description = Column(Text, nullable=True)
    website = Column(String(255), nullable=True)
    is_verified = Column(Boolean, default=False, nullable=False)
    
    # Relationships
    user = relationship("UserModel", back_populates="seller") 