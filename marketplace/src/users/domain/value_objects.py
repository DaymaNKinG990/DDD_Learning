"""Value objects for the users domain."""

# Python imports
from dataclasses import dataclass

# Local imports
from src.shared.domain.value_object import ValueObject


@dataclass(frozen=True)
class UserId(ValueObject):
    """
    User identifier value object.
    
    Attributes:
        value: The value of the user ID.
    """

    value: str

    def __hash__(self) -> int:
        """
        Hash the user ID.
        
        Returns:
            int: The hash of the user ID.
        """
        return hash(self.value)

    def __str__(self) -> str:
        """
        Get the string representation of the user ID.
        
        Returns:
            str: The string representation of the user ID.
        """
        return self.value


@dataclass(frozen=True)
class CustomerId(ValueObject):
    """
    Customer identifier value object.
    
    Attributes:
        value: The value of the customer ID.
    """

    value: str

    def __hash__(self) -> int:
        """
        Hash the customer ID.
        
        Returns:
            int: The hash of the customer ID.
        """
        return hash(self.value)

    def __str__(self) -> str:
        """
        Get the string representation of the customer ID.
        
        Returns:
            str: The string representation of the customer ID.
        """
        return self.value


@dataclass(frozen=True)
class SellerId(ValueObject):
    """
    Seller identifier value object.
    
    Attributes:
        value: The value of the seller ID.
    """

    value: str

    def __hash__(self) -> int:
        """
        Hash the seller ID.
        
        Returns:
            int: The hash of the seller ID.
        """
        return hash(self.value)

    def __str__(self) -> str:
        """
        Get the string representation of the seller ID.
        
        Returns:
            str: The string representation of the seller ID.
        """
        return self.value


@dataclass(frozen=True)
class Email(ValueObject):
    """
    Email value object.
    
    Attributes:
        value: The value of the email.
    """

    value: str

    def __post_init__(self) -> None:
        """
        Validate email format after initialization.
        
        Raises:
            ValueError: If the email is empty or invalid.
        """
        if not self.value or not self.value.strip():
            raise ValueError("Email cannot be empty")
        if "@" not in self.value or "." not in self.value:
            raise ValueError("Invalid email format")
        # Normalize email to lowercase
        object.__setattr__(self, "value", self.value.lower().strip())

    def __hash__(self) -> int:
        """
        Hash the email.
        
        Returns:
            int: The hash of the email.
        """
        return hash(self.value)

    def __str__(self) -> str:
        """
        Get the string representation of the email.
        
        Returns:
            str: The string representation of the email.
        """
        return self.value


@dataclass(frozen=True)
class PhoneNumber(ValueObject):
    """
    Phone number value object.
    
    Attributes:
        value: The value of the phone number.
    """

    value: str

    def __post_init__(self) -> None:
        """
        Validate phone number format after initialization.
        
        Raises:
            ValueError: If the phone number is empty or too short.
        """
        if not self.value or not self.value.strip():
            raise ValueError("Phone number cannot be empty")
        # Remove all non-digit characters
        digits_only = "".join(filter(str.isdigit, self.value))
        if len(digits_only) < 10:
            raise ValueError("Phone number too short")
        # Store normalized phone number
        object.__setattr__(self, "value", digits_only)

    def __hash__(self) -> int:
        """
        Hash the phone number.
        
        Returns:
            int: The hash of the phone number.
        """
        return hash(self.value)

    def __str__(self) -> str:
        """
        Get the string representation of the phone number.
        
        Returns:
            str: The string representation of the phone number.
        """
        return self.value
