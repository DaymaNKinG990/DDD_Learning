"""Entities for the users domain."""

# Python imports
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Optional

# Local imports
from src.shared.domain.entity import Entity
from .value_objects import CustomerId, Email, PhoneNumber, SellerId, UserId, Username


@dataclass
class User(Entity[UserId]):
    """
    Base user entity.
    
    Attributes:
        email: The email of the user.
        username: The username of the user.
        first_name: The first name of the user.
        last_name: The last name of the user.
        phone_number: The phone number of the user.
        is_active: Whether the user is active.
        created_at: The date and time the user was created.
        updated_at: The date and time the user was last updated.
    """

    email: Email
    username: Username
    first_name: str
    last_name: str
    phone_number: Optional[PhoneNumber] = None
    is_active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __hash__(self) -> int:
        """
        Hash the user.
        
        Returns:
            int: The hash of the user.
        """
        return hash(self.id)

    @property
    def full_name(self) -> str:
        """
        Get the full name of the user.
        
        Returns:
            str: The full name of the user.
        """
        return f"{self.first_name} {self.last_name}"

    def deactivate(self) -> None:
        """Deactivate user."""
        self.is_active = False
        self.updated_at = datetime.now(UTC)

    def activate(self) -> None:
        """Activate user."""
        self.is_active = True
        self.updated_at = datetime.now(UTC)


@dataclass
class Customer(Entity[CustomerId]):
    """
    Customer entity.
    
    Attributes:
        user_id: The ID of the user.
        shipping_addresses: The shipping addresses of the customer.
        billing_addresses: The billing addresses of the customer.
        preferences: The preferences of the customer.
        created_at: The date and time the customer was created.
        updated_at: The date and time the customer was last updated.
    """

    user_id: UserId
    shipping_addresses: list[str] = field(default_factory=list)
    billing_addresses: list[str] = field(default_factory=list)
    preferences: dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __hash__(self) -> int:
        """
        Hash the customer.
        
        Returns:
            int: The hash of the customer.
        """
        return hash(self.id)

    def add_shipping_address(self, address: str) -> None:
        """
        Add a shipping address to the customer.
        
        Args:
            address: The shipping address to add.
        """
        self.shipping_addresses.append(address)
        self.updated_at = datetime.now(UTC)

    def add_billing_address(self, address: str) -> None:
        """
        Add a billing address to the customer.
        
        Args:
            address: The billing address to add.
        """
        self.billing_addresses.append(address)
        self.updated_at = datetime.now(UTC)


@dataclass
class Seller(Entity[SellerId]):
    """
    Seller entity.
    
    Attributes:
        user_id: The ID of the user.
        company_name: The name of the company.
        business_address: The business address of the seller.
        company_description: The description of the company.
        tax_id: The tax ID of the seller.
        is_verified: Whether the seller is verified.
        created_at: The date and time the seller was created.
        updated_at: The date and time the seller was last updated.
    """

    user_id: UserId
    company_name: str
    business_address: str
    company_description: Optional[str] = None
    tax_id: Optional[str] = None
    is_verified: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __hash__(self) -> int:
        """
        Hash the seller.
        
        Returns:
            int: The hash of the seller.
        """
        return hash(self.id)

    def verify(self) -> None:
        """Verify seller."""
        self.is_verified = True
        self.updated_at = datetime.now(UTC)

    def unverify(self) -> None:
        """Unverify seller."""
        self.is_verified = False
        self.updated_at = datetime.now(UTC)
