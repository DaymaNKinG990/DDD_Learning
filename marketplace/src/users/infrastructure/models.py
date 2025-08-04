"""SQLAlchemy models for users domain."""

# Python imports
from sqlalchemy import Boolean, Column, DateTime, String, Text, ForeignKey
from sqlalchemy.orm import relationship

# Local imports
from src.shared.infrastructure.models import Base, TimestampMixin


class UserModel(Base, TimestampMixin):
    """
    SQLAlchemy model for User entity.
    
    Attributes:
        id: The ID of the user.
        email: The email of the user.
        password_hash: The hash of the user's password.
        first_name: The first name of the user.
        last_name: The last name of the user.
        phone_number: The phone number of the user.
        is_active: Whether the user is active.
    """
    
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    phone_number = Column(String(20), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    customer = relationship("CustomerModel", back_populates="user", uselist=False)
    seller = relationship("SellerModel", back_populates="user", uselist=False)


class CustomerModel(Base, TimestampMixin):
    """
    SQLAlchemy model for Customer entity.
    
    Attributes:
        id: The ID of the customer.
        user_id: The ID of the user.
        shipping_address: The shipping address of the customer.
        billing_address: The billing address of the customer.
    """
    
    __tablename__ = "customers"
    
    id = Column(String(36), primary_key=True, index=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    shipping_address = Column(Text, nullable=False)
    billing_address = Column(Text, nullable=False)
    
    # Relationships
    user = relationship("UserModel", back_populates="customer")


class SellerModel(Base, TimestampMixin):
    """
    SQLAlchemy model for Seller entity.
    
    Attributes:
        id: The ID of the seller.
        user_id: The ID of the user.
        company_name: The name of the company.
        company_description: The description of the company.
        website: The website of the company.
        is_verified: Whether the seller is verified.
    """
    
    __tablename__ = "sellers"
    
    id = Column(String(36), primary_key=True, index=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    company_name = Column(String(255), nullable=False)
    business_address = Column(Text, nullable=False)
    company_description = Column(Text, nullable=True)
    tax_id = Column(String(100), nullable=True)
    is_verified = Column(Boolean, default=False, nullable=False)
    
    # Relationships
    user = relationship("UserModel", back_populates="seller") 