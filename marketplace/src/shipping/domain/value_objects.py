"""Value objects for shipping domain."""

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from typing import Optional, Union

from src.shared.domain.value_object import ValueObject


@dataclass(frozen=True)
class ShippingId(ValueObject):
    """Shipping ID value object."""

    value: str


@dataclass(frozen=True)
class TrackingNumber(ValueObject):
    """Tracking number value object."""

    value: str

    def __post_init__(self) -> None:
        """Validate tracking number format after initialization."""
        if not self.value or len(self.value.strip()) < 5:
            raise ValueError("Tracking number must be at least 5 characters long")
        # Normalize tracking number
        object.__setattr__(self, "value", self.value.strip())


class ShippingStatus(Enum):
    """Shipping status enumeration."""

    PENDING = "pending"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    FAILED = "failed"
    RETURNED = "returned"


class ShippingMethod(Enum):
    """Shipping method enumeration."""

    STANDARD = "standard"
    EXPRESS = "express"
    PREMIUM = "premium"
    SAME_DAY = "same_day"


@dataclass(frozen=True)
class ShippingCost(ValueObject):
    """Shipping cost value object."""

    amount: Decimal
    currency: str

    def __post_init__(self) -> None:
        """Validate shipping cost after initialization."""
        if self.amount < 0:
            raise ValueError("Shipping cost cannot be negative")
        if not self.currency or len(self.currency) != 3:
            raise ValueError("Currency must be a 3-letter code")
        # Normalize currency to uppercase
        object.__setattr__(self, "currency", self.currency.upper())

    def __str__(self) -> str:
        """String representation."""
        return f"{self.amount} {self.currency}"

    @classmethod
    def create(
        cls, amount: Union[Decimal, float, str], currency: str = "RUB"
    ) -> "ShippingCost":
        """Create a shipping cost from amount and currency."""
        amount_decimal = Decimal(str(amount))
        return cls(value=amount_decimal, currency=currency)


@dataclass(frozen=True)
class DeliveryAddress(ValueObject):
    """Delivery address value object."""

    street: str
    city: str
    postal_code: str
    state: Optional[str] = None
    country: str = "Russia"

    def __post_init__(self) -> None:
        """Validate delivery address after initialization."""
        if not self.street or not self.street.strip():
            raise ValueError("Street address cannot be empty")
        if not self.city or not self.city.strip():
            raise ValueError("City cannot be empty")
        if not self.postal_code or not self.postal_code.strip():
            raise ValueError("Postal code cannot be empty")

        # Normalize address fields
        object.__setattr__(self, "street", self.street.strip())
        object.__setattr__(self, "city", self.city.strip())
        object.__setattr__(self, "postal_code", self.postal_code.strip())
        if self.state:
            object.__setattr__(self, "state", self.state.strip())

    def __str__(self) -> str:
        """String representation."""
        parts = [self.street, self.city]
        if self.state:
            parts.append(self.state)
        parts.extend([self.postal_code, self.country])
        return ", ".join(parts)
