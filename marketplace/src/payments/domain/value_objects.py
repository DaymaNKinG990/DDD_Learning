"""Value objects for the payments domain."""

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from typing import Union

from src.shared.domain.value_object import ValueObject


@dataclass(frozen=True)
class PaymentId(ValueObject):
    """Payment identifier value object."""

    value: str

    def __hash__(self) -> int:
        return hash(self.value)

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class PaymentMethodId(ValueObject):
    """Payment method identifier value object."""

    value: str

    def __hash__(self) -> int:
        return hash(self.value)

    def __str__(self) -> str:
        return self.value


class PaymentStatus(str, Enum):
    """Payment status enumeration."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


@dataclass(frozen=True)
class Amount(ValueObject):
    """Amount value object."""

    value: Decimal
    currency: str

    def __post_init__(self) -> None:
        """Validate amount after initialization."""
        if self.value < 0:
            raise ValueError("Amount cannot be negative")
        if not self.currency or len(self.currency) != 3:
            raise ValueError("Currency must be a 3-letter code")
        # Normalize currency to uppercase
        object.__setattr__(self, "currency", self.currency.upper())

    def __hash__(self) -> int:
        return hash((self.value, self.currency))

    def __str__(self) -> str:
        return f"{self.value} {self.currency}"

    def __add__(self, other: "Amount") -> "Amount":
        """Add two amounts."""
        if self.currency != other.currency:
            raise ValueError("Cannot add amounts with different currencies")
        return Amount(value=self.value + other.value, currency=self.currency)

    def __sub__(self, other: "Amount") -> "Amount":
        """Subtract two amounts."""
        if self.currency != other.currency:
            raise ValueError("Cannot subtract amounts with different currencies")
        return Amount(value=self.value - other.value, currency=self.currency)

    @classmethod
    def create(
        cls, value: Union[Decimal, float, str], currency: str = "RUB"
    ) -> "Amount":
        """Create an amount from value and currency."""
        value_decimal = Decimal(str(value))
        return cls(value=value_decimal, currency=currency)
