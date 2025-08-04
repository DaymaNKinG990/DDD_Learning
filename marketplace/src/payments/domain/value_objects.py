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


class PaymentType(str, Enum):
    """
    Payment type enumeration.
    
    This enumeration represents the type of a payment.
    
    Attributes:
        CREDIT_CARD (str): Credit card payment.
        DEBIT_CARD (str): Debit card payment.
        BANK_TRANSFER (str): Bank transfer payment.
        DIGITAL_WALLET (str): Digital wallet payment.
        CASH (str): Cash payment.
    """

    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    BANK_TRANSFER = "bank_transfer"
    DIGITAL_WALLET = "digital_wallet"
    CASH = "cash"


class PaymentCurrency(str, Enum):
    """
    Payment currency enumeration.
    
    This enumeration represents the currency of a payment.
    
    Attributes:
        USD (str): US Dollar.
        EUR (str): Euro.
        RUB (str): Russian Ruble.
    """

    USD = "USD"
    EUR = "EUR"
    RUB = "RUB"


@dataclass(frozen=True)
class PaymentAmount(ValueObject):
    """
    Payment amount value object.
    
    This value object represents the amount of a payment.
    
    Attributes:
        amount (Decimal): The amount value.
        currency (PaymentCurrency): The currency of the amount.
    """

    amount: Decimal
    currency: PaymentCurrency

    def __post_init__(self) -> None:
        """Validate amount after initialization."""
        if self.amount < 0:
            raise ValueError("Amount cannot be negative")

    def __hash__(self) -> int:
        """Hash the payment amount."""
        return hash((self.amount, self.currency))

    def __str__(self) -> str:
        """String representation of the payment amount."""
        return f"{self.amount} {self.currency.value}"

    def __add__(self, other: "PaymentAmount") -> "PaymentAmount":
        """
        Add two payment amounts.
        
        Args:
            other (PaymentAmount): The amount to add.

        Returns:
            PaymentAmount: The sum of the two amounts.
        """
        if self.currency != other.currency:
            raise ValueError("Cannot add amounts with different currencies")
        return PaymentAmount(amount=self.amount + other.amount, currency=self.currency)

    def __sub__(self, other: "PaymentAmount") -> "PaymentAmount":
        """
        Subtract two payment amounts.
        
        Args:
            other (PaymentAmount): The amount to subtract.

        Returns:
            PaymentAmount: The difference of the two amounts.
        """
        if self.currency != other.currency:
            raise ValueError("Cannot subtract amounts with different currencies")
        return PaymentAmount(amount=self.amount - other.amount, currency=self.currency)


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
