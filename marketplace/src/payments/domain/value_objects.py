"""Value objects for the payments domain."""

from decimal import Decimal
from enum import Enum
from typing import Any

from pydantic import Field, field_validator

from src.shared.domain.value_object import ValueObject


class PaymentId(ValueObject):
    """Payment identifier value object."""
    
    value: str = Field(description="Payment identifier")
    
    def __hash__(self) -> int:
        return hash(self.value)
    
    def __str__(self) -> str:
        return self.value


class PaymentMethodId(ValueObject):
    """Payment method identifier value object."""
    
    value: str = Field(description="Payment method identifier")
    
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


class Amount(ValueObject):
    """Amount value object."""
    
    value: Decimal = Field(description="Amount value")
    currency: str = Field(default="RUB", description="Currency code")
    
    @field_validator("value")
    @classmethod
    def validate_amount(cls, v: Any) -> Decimal:
        """Validate amount."""
        if not isinstance(v, Decimal):
            v = Decimal(str(v))
        if v < 0:
            raise ValueError("Amount cannot be negative")
        return v
    
    @field_validator("currency")
    @classmethod
    def validate_currency(cls, v: str) -> str:
        """Validate currency code."""
        if not v or len(v) != 3:
            raise ValueError("Currency must be a 3-letter code")
        return v.upper()
    
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