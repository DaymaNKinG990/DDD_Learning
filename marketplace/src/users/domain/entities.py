"""Entities for the users domain."""

from datetime import datetime
from typing import Optional

from pydantic import Field

from src.shared.domain.entity import Entity

from .value_objects import CustomerId, Email, PhoneNumber, SellerId, UserId


class User(Entity[UserId]):
    """Base user entity."""
    
    email: Email = Field(description="User email")
    first_name: str = Field(description="First name")
    last_name: str = Field(description="Last name")
    phone_number: Optional[PhoneNumber] = Field(default=None, description="Phone number")
    is_active: bool = Field(default=True, description="User status")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    
    def __hash__(self) -> int:
        return hash(self.id)
    
    @property
    def full_name(self) -> str:
        """Get user's full name."""
        return f"{self.first_name} {self.last_name}"
    
    def deactivate(self) -> "User":
        """Deactivate user."""
        return User(
            id=self.id,
            email=self.email,
            first_name=self.first_name,
            last_name=self.last_name,
            phone_number=self.phone_number,
            is_active=False,
            created_at=self.created_at,
            updated_at=datetime.utcnow(),
        )
    
    def activate(self) -> "User":
        """Activate user."""
        return User(
            id=self.id,
            email=self.email,
            first_name=self.first_name,
            last_name=self.last_name,
            phone_number=self.phone_number,
            is_active=True,
            created_at=self.created_at,
            updated_at=datetime.utcnow(),
        )


class Customer(Entity[CustomerId]):
    """Customer entity."""
    
    user_id: UserId = Field(description="Associated user")
    shipping_addresses: list[str] = Field(default_factory=list, description="Shipping addresses")
    billing_addresses: list[str] = Field(default_factory=list, description="Billing addresses")
    preferences: dict = Field(default_factory=dict, description="Customer preferences")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    
    def __hash__(self) -> int:
        return hash(self.id)
    
    def add_shipping_address(self, address: str) -> "Customer":
        """Add shipping address."""
        new_addresses = self.shipping_addresses + [address]
        return Customer(
            id=self.id,
            user_id=self.user_id,
            shipping_addresses=new_addresses,
            billing_addresses=self.billing_addresses,
            preferences=self.preferences,
            created_at=self.created_at,
            updated_at=datetime.utcnow(),
        )
    
    def add_billing_address(self, address: str) -> "Customer":
        """Add billing address."""
        new_addresses = self.billing_addresses + [address]
        return Customer(
            id=self.id,
            user_id=self.user_id,
            shipping_addresses=self.shipping_addresses,
            billing_addresses=new_addresses,
            preferences=self.preferences,
            created_at=self.created_at,
            updated_at=datetime.utcnow(),
        )


class Seller(Entity[SellerId]):
    """Seller entity."""
    
    user_id: UserId = Field(description="Associated user")
    company_name: str = Field(description="Company name")
    company_description: Optional[str] = Field(default=None, description="Company description")
    business_address: str = Field(description="Business address")
    tax_id: Optional[str] = Field(default=None, description="Tax identification number")
    is_verified: bool = Field(default=False, description="Verification status")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    
    def __hash__(self) -> int:
        return hash(self.id)
    
    def verify(self) -> "Seller":
        """Verify seller."""
        return Seller(
            id=self.id,
            user_id=self.user_id,
            company_name=self.company_name,
            company_description=self.company_description,
            business_address=self.business_address,
            tax_id=self.tax_id,
            is_verified=True,
            created_at=self.created_at,
            updated_at=datetime.utcnow(),
        )
    
    def unverify(self) -> "Seller":
        """Unverify seller."""
        return Seller(
            id=self.id,
            user_id=self.user_id,
            company_name=self.company_name,
            company_description=self.company_description,
            business_address=self.business_address,
            tax_id=self.tax_id,
            is_verified=False,
            created_at=self.created_at,
            updated_at=datetime.utcnow(),
        )