"""Value objects for the catalog domain."""

# Python imports
from dataclasses import dataclass
from decimal import Decimal
from typing import Union

# Local imports
from src.shared.domain.value_object import ValueObject


@dataclass(frozen=True)
class ProductId(ValueObject):
    """
    Product identifier value object.
    
    Attributes:
        value: The product ID.
    """

    value: str

    def __hash__(self) -> int:
        """Hash the product ID."""
        return hash(self.value)

    def __str__(self) -> str:
        """String representation of the product ID."""
        return self.value


@dataclass(frozen=True)
class CategoryId(ValueObject):
    """
    Category identifier value object.
    
    Attributes:
        value: The category ID.
    """

    value: str

    def __hash__(self) -> int:
        """Hash the category ID."""
        return hash(self.value)

    def __str__(self) -> str:
        """String representation of the category ID."""
        return self.value


@dataclass(frozen=True)
class BrandId(ValueObject):
    """
    Brand identifier value object.
    
    Attributes:
        value: The brand ID.
    """

    value: str

    def __hash__(self) -> int:
        """Hash the brand ID."""
        return hash(self.value)

    def __str__(self) -> str:
        """String representation of the brand ID."""
        return self.value


@dataclass(frozen=True)
class Price(ValueObject):
    """
    Price value object.
    
    Attributes:
        amount: The price amount.
        currency: The price currency.
    """

    amount: Decimal
    currency: str

    def __post_init__(self) -> None:
        """
        Validate price after initialization.
        
        Raises:
            ValueError: If the price is negative or the currency is not a 3-letter code.
        """
        if self.amount < 0:
            raise ValueError("Price cannot be negative")
        if not self.currency or len(self.currency) != 3:
            raise ValueError("Currency must be a 3-letter code")
        # Normalize currency to uppercase
        object.__setattr__(self, "currency", self.currency.upper())

    def __hash__(self) -> int:
        """Hash the price."""
        return hash((self.amount, self.currency))

    def __str__(self) -> str:
        """String representation of the price."""
        return f"{self.amount} {self.currency}"

    def __add__(self, other: "Price") -> "Price":
        """
        Add two prices.
        
        Args:
            other: The other price to add.
            
        Returns:
            Price: The sum of the two prices.
        """
        if self.currency != other.currency:
            raise ValueError("Cannot add prices with different currencies")
        return Price(amount=self.amount + other.amount, currency=self.currency)

    def __sub__(self, other: "Price") -> "Price":
        """
        Subtract two prices.
        
        Args:
            other: The other price to subtract.
            
        Returns:
            Price: The difference of the two prices.

        Raises:
            ValueError: If the prices have different currencies.
        """
        if self.currency != other.currency:
            raise ValueError("Cannot subtract prices with different currencies")
        return Price(amount=self.amount - other.amount, currency=self.currency)

    @classmethod
    def create(
        cls,
        amount: Union[Decimal, float, str],
        currency: str = "RUB"
    ) -> "Price":
        """
        Create a price from amount and currency.
        
        Args:
            amount: The amount of the price.
            currency: The currency of the price.

        Returns:
            Price: The created price.
        """
        amount_decimal = Decimal(str(amount))
        return cls(value=amount_decimal, currency=currency)


@dataclass(frozen=True)
class ProductName(ValueObject):
    """Product name value object.
    
    Attributes:
        value: The product name.
    """

    value: str

    def __post_init__(self) -> None:
        """
        Validate product name after initialization.
        
        Raises:
            ValueError: If the product name is empty or too long.
        """
        if not self.value or not self.value.strip():
            raise ValueError("Product name cannot be empty")
        if len(self.value) > 200:
            raise ValueError("Product name too long")
        # Normalize product name
        object.__setattr__(self, "value", self.value.strip())

    def __hash__(self) -> int:
        """Hash the product name."""
        return hash(self.value)

    def __str__(self) -> str:
        """String representation of the product name."""
        return self.value


@dataclass(frozen=True)
class ProductDescription(ValueObject):
    """Product description value object.
    
    Attributes:
        value: The product description.
    """

    value: str

    def __post_init__(self) -> None:
        """
        Validate product description after initialization.
        
        Raises:
            ValueError: If the product description is empty or too long.
        """
        if not self.value or not self.value.strip():
            raise ValueError("Product description cannot be empty")
        if len(self.value) > 2000:
            raise ValueError("Product description too long")
        # Normalize product description
        object.__setattr__(self, "value", self.value.strip())

    def __hash__(self) -> int:
        """Hash the product description."""
        return hash(self.value)

    def __str__(self) -> str:
        """String representation of the product description."""
        return self.value
