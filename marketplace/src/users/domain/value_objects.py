"""Value objects for the users domain."""

from typing import Any

from pydantic import Field, field_validator

from src.shared.domain.value_object import ValueObject


class UserId(ValueObject):
    """User identifier value object."""
    
    value: str = Field(description="User identifier")
    
    def __hash__(self) -> int:
        return hash(self.value)
    
    def __str__(self) -> str:
        return self.value


class CustomerId(ValueObject):
    """Customer identifier value object."""
    
    value: str = Field(description="Customer identifier")
    
    def __hash__(self) -> int:
        return hash(self.value)
    
    def __str__(self) -> str:
        return self.value


class SellerId(ValueObject):
    """Seller identifier value object."""
    
    value: str = Field(description="Seller identifier")
    
    def __hash__(self) -> int:
        return hash(self.value)
    
    def __str__(self) -> str:
        return self.value


class Email(ValueObject):
    """Email value object."""
    
    value: str = Field(description="Email address")
    
    @field_validator("value")
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Validate email format."""
        if not v or not v.strip():
            raise ValueError("Email cannot be empty")
        if "@" not in v or "." not in v:
            raise ValueError("Invalid email format")
        return v.lower().strip()
    
    def __hash__(self) -> int:
        return hash(self.value)
    
    def __str__(self) -> str:
        return self.value


class PhoneNumber(ValueObject):
    """Phone number value object."""
    
    value: str = Field(description="Phone number")
    
    @field_validator("value")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        """Validate phone number format."""
        if not v or not v.strip():
            raise ValueError("Phone number cannot be empty")
        # Remove all non-digit characters
        digits_only = "".join(filter(str.isdigit, v))
        if len(digits_only) < 10:
            raise ValueError("Phone number too short")
        return digits_only
    
    def __hash__(self) -> int:
        return hash(self.value)
    
    def __str__(self) -> str:
        return self.value