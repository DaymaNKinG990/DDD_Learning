"""Entities for the users domain."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Optional

from src.shared.domain.entity import Entity

from .value_objects import CustomerId, Email, PhoneNumber, SellerId, UserId


@dataclass
class User(Entity[UserId]):
    """Base user entity."""

    email: Email
    first_name: str
    last_name: str
    phone_number: Optional[PhoneNumber] = None
    is_active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __hash__(self) -> int:
        return hash(self.id)

    @property
    def full_name(self) -> str:
        """Get user's full name."""
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
    """Customer entity."""

    user_id: UserId
    shipping_addresses: list[str] = field(default_factory=list)
    billing_addresses: list[str] = field(default_factory=list)
    preferences: dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __hash__(self) -> int:
        return hash(self.id)

    def add_shipping_address(self, address: str) -> None:
        """Add shipping address."""
        self.shipping_addresses.append(address)
        self.updated_at = datetime.now(UTC)

    def add_billing_address(self, address: str) -> None:
        """Add billing address."""
        self.billing_addresses.append(address)
        self.updated_at = datetime.now(UTC)


@dataclass
class Seller(Entity[SellerId]):
    """Seller entity."""

    user_id: UserId
    company_name: str
    business_address: str
    company_description: Optional[str] = None
    tax_id: Optional[str] = None
    is_verified: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __hash__(self) -> int:
        return hash(self.id)

    def verify(self) -> None:
        """Verify seller."""
        self.is_verified = True
        self.updated_at = datetime.now(UTC)

    def unverify(self) -> None:
        """Unverify seller."""
        self.is_verified = False
        self.updated_at = datetime.now(UTC)
