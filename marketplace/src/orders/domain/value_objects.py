"""Value objects for the orders domain."""

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from typing import Union

from src.shared.domain.value_object import ValueObject


@dataclass(frozen=True)
class OrderId(ValueObject):
    """Order identifier value object."""

    value: str

    def __hash__(self) -> int:
        return hash(self.value)

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class OrderItemId(ValueObject):
    """Order item identifier value object."""

    value: str

    def __hash__(self) -> int:
        return hash(self.value)

    def __str__(self) -> str:
        return self.value


class OrderStatus(str, Enum):
    """Order status enumeration."""

    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


@dataclass(frozen=True)
class OrderTotal(ValueObject):
    """Order total value object."""

    subtotal: Decimal
    tax: Decimal
    shipping: Decimal
    discount: Decimal = Decimal("0")
    total: Decimal = Decimal("0")
    currency: str = "RUB"

    def __post_init__(self) -> None:
        """Validate monetary amounts after initialization."""
        if self.subtotal < 0:
            raise ValueError("Subtotal cannot be negative")
        if self.tax < 0:
            raise ValueError("Tax cannot be negative")
        if self.shipping < 0:
            raise ValueError("Shipping cannot be negative")
        if self.discount < 0:
            raise ValueError("Discount cannot be negative")
        if self.total < 0:
            raise ValueError("Total cannot be negative")
        if not self.currency or len(self.currency) != 3:
            raise ValueError("Currency must be a 3-letter code")

    def __hash__(self) -> int:
        return hash((
            self.subtotal,
            self.tax,
            self.shipping,
            self.discount,
            self.total,
            self.currency
        ))

    def __str__(self) -> str:
        return f"{self.total} {self.currency}"

    @classmethod
    def calculate(
        cls,
        subtotal: Union[Decimal, float, str],
        tax_rate: Union[Decimal, float, str] = Decimal("0.20"),  # 20% VAT
        shipping_cost: Union[Decimal, float, str] = Decimal("0"),
        discount: Union[Decimal, float, str] = Decimal("0"),
        currency: str = "RUB",
    ) -> "OrderTotal":
        """Calculate order total from components."""
        # Convert all inputs to Decimal
        subtotal_decimal = Decimal(str(subtotal))
        tax_rate_decimal = Decimal(str(tax_rate))
        shipping_decimal = Decimal(str(shipping_cost))
        discount_decimal = Decimal(str(discount))

        tax = subtotal_decimal * tax_rate_decimal
        total = subtotal_decimal + tax + shipping_decimal - discount_decimal

        return cls(
            subtotal=subtotal_decimal,
            tax=tax,
            shipping=shipping_decimal,
            discount=discount_decimal,
            total=total,
            currency=currency.upper(),
        )
