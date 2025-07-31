"""Value objects for the orders domain."""

# Python imports
from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from typing import Union

# Local imports
from src.shared.domain.value_object import ValueObject


@dataclass(frozen=True)
class OrderId(ValueObject):
    """
    Order identifier value object.
    
    This value object represents the unique identifier for an order.

    Attributes:
        value (str): The unique identifier for the order.
    """

    value: str

    def __hash__(self) -> int:
        """
        Hash the order ID.
        
        Returns:
            int: The hash of the order ID.
        """
        return hash(self.value)

    def __str__(self) -> str:
        """
        Return the string representation of the order ID.
        
        Returns:
            str: The string representation of the order ID.
        """
        return self.value


@dataclass(frozen=True)
class OrderItemId(ValueObject):
    """
    Order item identifier value object.
    
    This value object represents the unique identifier for an order item.
    
    Attributes:
        value (str): The unique identifier for the order item.
    """

    value: str

    def __hash__(self) -> int:
        """
        Hash the order item ID.
        
        Returns:
            int: The hash of the order item ID.
        """
        return hash(self.value)

    def __str__(self) -> str:
        """
        Return the string representation of the order item ID.
        
        Returns:
            str: The string representation of the order item ID.
        """
        return self.value


class OrderStatus(str, Enum):
    """
    Order status enumeration.
    
    This enumeration represents the possible statuses of an order.
    
    Attributes:
        PENDING (str): The order is pending.
        CONFIRMED (str): The order is confirmed.
        PROCESSING (str): The order is being processed.
        SHIPPED (str): The order has been shipped.
        DELIVERED (str): The order has been delivered.
        CANCELLED (str): The order has been cancelled.
        REFUNDED (str): The order has been refunded.
    """

    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


@dataclass(frozen=True)
class OrderTotal(ValueObject):
    """
    Order total value object.
    
    This value object represents the total amount of an order.
    
    Attributes:
        subtotal (Decimal): The subtotal of the order.
        tax (Decimal): The tax of the order.
        shipping (Decimal): The shipping cost of the order.
        discount (Decimal): The discount of the order.
        total (Decimal): The total amount of the order.
        currency (str): The currency of the order.
    """

    subtotal: Decimal
    tax: Decimal
    shipping: Decimal
    discount: Decimal = Decimal("0")
    total: Decimal = Decimal("0")
    currency: str = "RUB"

    def __post_init__(self) -> None:
        """
        Validate monetary amounts after initialization.
        
        Raises:
            ValueError: If any of the monetary amounts are negative or the currency is not a 3-letter code.
        """
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
        """
        Hash the order total.
        
        Returns:
            int: The hash of the order total.
        """
        return hash((
            self.subtotal,
            self.tax,
            self.shipping,
            self.discount,
            self.total,
            self.currency
        ))

    def __str__(self) -> str:
        """
        Return the string representation of the order total.
        
        Returns:
            str: The string representation of the order total.
        """
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
        """
        Calculate order total from components.
        
        Args:
            subtotal (Union[Decimal, float, str]): The subtotal of the order.
            tax_rate (Union[Decimal, float, str]): The tax rate of the order.
            shipping_cost (Union[Decimal, float, str]): The shipping cost of the order.
            discount (Union[Decimal, float, str]): The discount of the order.
            currency (str): The currency of the order.

        Returns:
            OrderTotal: The calculated order total.
        """
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
