"""Value objects for the orders domain."""

from decimal import Decimal
from enum import Enum
from typing import Any

from pydantic import Field, field_validator

from src.shared.domain.value_object import ValueObject


class OrderId(ValueObject):
    """Order identifier value object."""
    
    value: str = Field(description="Order identifier")
    
    def __hash__(self) -> int:
        return hash(self.value)
    
    def __str__(self) -> str:
        return self.value


class OrderItemId(ValueObject):
    """Order item identifier value object."""
    
    value: str = Field(description="Order item identifier")
    
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


class OrderTotal(ValueObject):
    """Order total value object."""
    
    subtotal: Decimal = Field(description="Subtotal amount")
    tax: Decimal = Field(description="Tax amount")
    shipping: Decimal = Field(description="Shipping cost")
    discount: Decimal = Field(default=Decimal("0"), description="Discount amount")
    total: Decimal = Field(description="Total amount")
    currency: str = Field(default="RUB", description="Currency code")
    
    @field_validator("subtotal", "tax", "shipping", "discount", "total")
    @classmethod
    def validate_amounts(cls, v: Any) -> Decimal:
        """Validate monetary amounts."""
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
        return hash((self.subtotal, self.tax, self.shipping, self.discount, self.total, self.currency))
    
    def __str__(self) -> str:
        return f"{self.total} {self.currency}"
    
    @classmethod
    def calculate(
        cls,
        subtotal: Decimal,
        tax_rate: Decimal = Decimal("0.20"),  # 20% VAT
        shipping_cost: Decimal = Decimal("0"),
        discount: Decimal = Decimal("0"),
        currency: str = "RUB",
    ) -> "OrderTotal":
        """Calculate order total from components."""
        tax = subtotal * tax_rate
        total = subtotal + tax + shipping_cost - discount
        
        return cls(
            subtotal=subtotal,
            tax=tax,
            shipping=shipping_cost,
            discount=discount,
            total=total,
            currency=currency,
        )