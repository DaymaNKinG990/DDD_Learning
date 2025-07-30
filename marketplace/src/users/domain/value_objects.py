"""Value objects for the users domain."""

from dataclasses import dataclass

from src.shared.domain.value_object import ValueObject


@dataclass(frozen=True)
class UserId(ValueObject):
    """User identifier value object."""

    value: str

    def __hash__(self) -> int:
        return hash(self.value)

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class CustomerId(ValueObject):
    """Customer identifier value object."""

    value: str

    def __hash__(self) -> int:
        return hash(self.value)

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class SellerId(ValueObject):
    """Seller identifier value object."""

    value: str

    def __hash__(self) -> int:
        return hash(self.value)

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class Email(ValueObject):
    """Email value object."""

    value: str

    def __post_init__(self) -> None:
        """Validate email format after initialization."""
        if not self.value or not self.value.strip():
            raise ValueError("Email cannot be empty")
        if "@" not in self.value or "." not in self.value:
            raise ValueError("Invalid email format")
        # Normalize email to lowercase
        object.__setattr__(self, "value", self.value.lower().strip())

    def __hash__(self) -> int:
        return hash(self.value)

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class PhoneNumber(ValueObject):
    """Phone number value object."""

    value: str

    def __post_init__(self) -> None:
        """Validate phone number format after initialization."""
        if not self.value or not self.value.strip():
            raise ValueError("Phone number cannot be empty")
        # Remove all non-digit characters
        digits_only = "".join(filter(str.isdigit, self.value))
        if len(digits_only) < 10:
            raise ValueError("Phone number too short")
        # Store normalized phone number
        object.__setattr__(self, "value", digits_only)

    def __hash__(self) -> int:
        return hash(self.value)

    def __str__(self) -> str:
        return self.value
