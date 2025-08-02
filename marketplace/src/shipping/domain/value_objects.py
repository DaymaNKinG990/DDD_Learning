"""Value objects for shipping domain."""

# Python imports
from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from typing import Optional, Union

# Local imports
from src.shared.domain.value_object import ValueObject


@dataclass(frozen=True)
class ShippingId(ValueObject):
    """
    Shipping ID value object.
    
    Attributes:
        value: The shipping ID.
    """

    value: str


@dataclass(frozen=True)
class ShippingProviderId(ValueObject):
    """
    Shipping provider ID value object.
    
    Attributes:
        value: The shipping provider ID.
    """

    value: str


@dataclass(frozen=True)
class TrackingNumber(ValueObject):
    """
    Tracking number value object.
    
    Attributes:
        value: The tracking number.
    """

    value: str

    def __post_init__(self) -> None:
        """
        Validate tracking number format after initialization.
        
        Raises:
            ValueError: If the tracking number is not at least 5 characters long.
        """
        if not self.value or len(self.value.strip()) < 5:
            raise ValueError("Tracking number must be at least 5 characters long")
        # Normalize tracking number
        object.__setattr__(self, "value", self.value.strip())


class ShippingStatus(Enum):
    """
    Shipping status enumeration.
    
    Attributes:
        PENDING: The shipment is pending.
        IN_TRANSIT: The shipment is in transit.
        DELIVERED: The shipment is delivered.
        FAILED: The shipment failed.
        RETURNED: The shipment was returned.
    """

    PENDING = "pending"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    FAILED = "failed"
    RETURNED = "returned"


class ShippingMethod(Enum):
    """
    Shipping method enumeration.
    
    Attributes:
        STANDARD: The standard shipping method.
        EXPRESS: The express shipping method.
        PREMIUM: The premium shipping method.
        SAME_DAY: The same day shipping method.
    """

    STANDARD = "standard"
    EXPRESS = "express"
    PREMIUM = "premium"
    SAME_DAY = "same_day"


@dataclass(frozen=True)
class ShippingCost(ValueObject):
    """
    Shipping cost value object.
    
    Attributes:
        amount: The amount of the shipping cost.
        currency: The currency of the shipping cost.
    """

    amount: Decimal
    currency: str

    def __post_init__(self) -> None:
        """Validate shipping cost after initialization.
        
        Raises:
            ValueError: If the shipping cost is negative or the currency is not a 3-letter code.
        """
        if self.amount < 0:
            raise ValueError("Shipping cost cannot be negative")
        if not self.currency or len(self.currency) != 3:
            raise ValueError("Currency must be a 3-letter code")
        # Normalize currency to uppercase
        object.__setattr__(self, "currency", self.currency.upper())

    def __str__(self) -> str:
        """String representation.
        
        Returns:
            str: The string representation of the shipping cost.
        """
        return f"{self.amount} {self.currency}"

    @classmethod
    def create(cls, amount: Union[Decimal, float, str], currency: str = "RUB") -> "ShippingCost":
        """
        Create a shipping cost from amount and currency.
        
        Args:
            amount: The amount of the shipping cost.
            currency: The currency of the shipping cost.

        Returns:
            ShippingCost: The created shipping cost.
        """
        amount_decimal = Decimal(str(amount))
        return cls(value=amount_decimal, currency=currency)


@dataclass(frozen=True)
class DeliveryAddress(ValueObject):
    """
    Delivery address value object.
    
    Attributes:
        street: The street address.
        city: The city.
        postal_code: The postal code.
        state: The state.
        country: The country.
    """

    street: str
    city: str
    postal_code: str
    state: Optional[str] = None
    country: str = "Russia"

    def __post_init__(self) -> None:
        """
        Validate delivery address after initialization.
        
        Raises:
            ValueError: If the street address, city, or postal code is empty.
        """
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
        """
        String representation.
        
        Returns:
            str: The string representation of the delivery address.
        """
        parts = [self.street, self.city]
        if self.state:
            parts.append(self.state)
        parts.extend([self.postal_code, self.country])
        return ", ".join(parts)
