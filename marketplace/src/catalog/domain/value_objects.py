"""Value objects for the catalog domain."""

from decimal import Decimal
from typing import Any

from pydantic import Field, field_validator

from src.shared.domain.value_object import ValueObject


class ProductId(ValueObject):
    """Product identifier value object."""
    
    value: str = Field(description="Product identifier")
    
    def __hash__(self) -> int:
        return hash(self.value)
    
    def __str__(self) -> str:
        return self.value


class CategoryId(ValueObject):
    """Category identifier value object."""
    
    value: str = Field(description="Category identifier")
    
    def __hash__(self) -> int:
        return hash(self.value)
    
    def __str__(self) -> str:
        return self.value


class BrandId(ValueObject):
    """Brand identifier value object."""
    
    value: str = Field(description="Brand identifier")
    
    def __hash__(self) -> int:
        return hash(self.value)
    
    def __str__(self) -> str:
        return self.value


class Price(ValueObject):
    """Price value object."""
    
    amount: Decimal = Field(description="Price amount")
    currency: str = Field(default="RUB", description="Currency code")
    
    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v: Any) -> Decimal:
        """Validate price amount."""
        if not isinstance(v, Decimal):
            v = Decimal(str(v))
        if v < 0:
            raise ValueError("Price cannot be negative")
        return v
    
    @field_validator("currency")
    @classmethod
    def validate_currency(cls, v: str) -> str:
        """Validate currency code."""
        if not v or len(v) != 3:
            raise ValueError("Currency must be a 3-letter code")
        return v.upper()
    
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


class ProductName(ValueObject):
    """Product name value object."""
    
    value: str = Field(description="Product name")
    
    @field_validator("value")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate product name."""
        if not v or not v.strip():
            raise ValueError("Product name cannot be empty")
        if len(v) > 200:
            raise ValueError("Product name too long")
        return v.strip()
    
    def __hash__(self) -> int:
        return hash(self.value)
    
    def __str__(self) -> str:
        return self.value


class ProductDescription(ValueObject):
    """Product description value object."""
    
    value: str = Field(description="Product description")
    
    @field_validator("value")
    @classmethod
    def validate_description(cls, v: str) -> str:
        """Validate product description."""
        if not v or not v.strip():
            raise ValueError("Product description cannot be empty")
        if len(v) > 2000:
            raise ValueError("Product description too long")
        return v.strip()
    
    def __hash__(self) -> int:
        return hash(self.value)
    
    def __str__(self) -> str:
        return self.value