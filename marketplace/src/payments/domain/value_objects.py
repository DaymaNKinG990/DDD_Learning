"""Value objects for the payments domain."""

# Python imports
from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from typing import Union

# Local imports
from src.shared.domain.value_object import ValueObject


@dataclass(frozen=True)
class PaymentId(ValueObject):
    """
    Payment identifier value object.
    
    This value object represents the identifier for a payment.
    
    Attributes:
        value (str): The value of the payment identifier.
    """

    value: str

    def __hash__(self) -> int:
        """Hash the payment identifier."""
        return hash(self.value)

    def __str__(self) -> str:
        """String representation of the payment identifier."""
        return self.value


@dataclass(frozen=True)
class PaymentMethodId(ValueObject):
    """
    Payment method identifier value object.
    
    This value object represents the identifier for a payment method.
    
    Attributes:
        value (str): The value of the payment method identifier.
    """

    value: str

    def __hash__(self) -> int:
        """Hash the payment method identifier."""
        return hash(self.value)

    def __str__(self) -> str:
        """String representation of the payment method identifier."""
        return self.value


class PaymentStatus(str, Enum):
    """
    Payment status enumeration.
    
    This enumeration represents the status of a payment.
    
    Attributes:
        PENDING (str): The payment is pending.
        PROCESSING (str): The payment is processing.
        COMPLETED (str): The payment is completed.
        FAILED (str): The payment is failed.
        CANCELLED (str): The payment is cancelled.
        REFUNDED (str): The payment is refunded.
    """

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


@dataclass(frozen=True)
class Amount(ValueObject):
    """
    Amount value object.
    
    This value object represents the amount of a payment.
    
    Attributes:
        value (Decimal): The value of the amount.
        currency (str): The currency of the amount.
    """

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
        """Hash the amount."""
        return hash((self.value, self.currency))

    def __str__(self) -> str:
        """String representation of the amount."""
        return f"{self.value} {self.currency}"

    def __add__(self, other: "Amount") -> "Amount":
        """
        Add two amounts.
        
        Args:
            other (Amount): The amount to add.

        Returns:
            Amount: The sum of the two amounts.
        """
        if self.currency != other.currency:
            raise ValueError("Cannot add amounts with different currencies")
        return Amount(value=self.value + other.value, currency=self.currency)

    def __sub__(self, other: "Amount") -> "Amount":
        """
        Subtract two amounts.
        
        Args:
            other (Amount): The amount to subtract.

        Returns:
            Amount: The difference of the two amounts.
        """
        if self.currency != other.currency:
            raise ValueError("Cannot subtract amounts with different currencies")
        return Amount(value=self.value - other.value, currency=self.currency)

    @classmethod
    def create(cls, value: Union[Decimal, float, str], currency: str = "RUB") -> "Amount":
        """
        Create an amount from value and currency.
        
        Args:
            value (Union[Decimal, float, str]): The value of the amount.
            currency (str): The currency of the amount.

        Returns:
            Amount: The created amount.
        """
        value_decimal = Decimal(str(value))
        return cls(value=value_decimal, currency=currency)
