"""Value objects for the catalog domain."""

from dataclasses import dataclass
from decimal import Decimal
from typing import Union

from src.shared.domain.value_object import ValueObject


@dataclass(frozen=True)
class ProductId(ValueObject):
    """Product identifier value object."""

    value: str

    def __hash__(self) -> int:
        return hash(self.value)

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class CategoryId(ValueObject):
    """Category identifier value object."""

    value: str

    def __hash__(self) -> int:
        return hash(self.value)

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class BrandId(ValueObject):
    """Brand identifier value object."""

    value: str

    def __hash__(self) -> int:
        return hash(self.value)

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class Price(ValueObject):
    """Price value object."""

    amount: Decimal
    currency: str

    def __post_init__(self) -> None:
        """Validate price after initialization."""
        if self.amount < 0:
            raise ValueError("Price cannot be negative")
        if not self.currency or len(self.currency) != 3:
            raise ValueError("Currency must be a 3-letter code")
        # Normalize currency to uppercase
        object.__setattr__(self, "currency", self.currency.upper())

    def __hash__(self) -> int:
        return hash((self.amount, self.currency))

    def __str__(self) -> str:
        return f"{self.amount} {self.currency}"

    def __add__(self, other: "Price") -> "Price":
        """Add two prices."""
        if self.currency != other.currency:
            raise ValueError("Cannot add prices with different currencies")
        return Price(amount=self.amount + other.amount, currency=self.currency)

    def __sub__(self, other: "Price") -> "Price":
        """Subtract two prices."""
        if self.currency != other.currency:
            raise ValueError("Cannot subtract prices with different currencies")
        return Price(amount=self.amount - other.amount, currency=self.currency)

    @classmethod
    def create(
        cls, amount: Union[Decimal, float, str], currency: str = "RUB"
    ) -> "Price":
        """Create a price from amount and currency."""
        amount_decimal = Decimal(str(amount))
        return cls(value=amount_decimal, currency=currency)


@dataclass(frozen=True)
class ProductName(ValueObject):
    """Product name value object."""

    value: str

    def __post_init__(self) -> None:
        """Validate product name after initialization."""
        if not self.value or not self.value.strip():
            raise ValueError("Product name cannot be empty")
        if len(self.value) > 200:
            raise ValueError("Product name too long")
        # Normalize product name
        object.__setattr__(self, "value", self.value.strip())

    def __hash__(self) -> int:
        return hash(self.value)

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class ProductDescription(ValueObject):
    """Product description value object."""

    value: str

    def __post_init__(self) -> None:
        """Validate product description after initialization."""
        if not self.value or not self.value.strip():
            raise ValueError("Product description cannot be empty")
        if len(self.value) > 2000:
            raise ValueError("Product description too long")
        # Normalize product description
        object.__setattr__(self, "value", self.value.strip())

    def __hash__(self) -> int:
        return hash(self.value)

    def __str__(self) -> str:
        return self.value
