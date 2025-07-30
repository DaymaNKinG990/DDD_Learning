"""Value objects for reviews domain."""

from dataclasses import dataclass
from enum import Enum

from src.shared.domain.value_object import ValueObject


@dataclass(frozen=True)
class ReviewId(ValueObject):
    """Review ID value object."""

    value: str

    @classmethod
    def generate(cls) -> "ReviewId":
        """Generate a new review ID."""
        import uuid
        return cls(value=f"review_{uuid.uuid4().hex}")


@dataclass(frozen=True)
class Rating(ValueObject):
    """Rating value object."""

    value: int

    def __post_init__(self) -> None:
        """Validate rating value after initialization."""
        if not 1 <= self.value <= 5:
            raise ValueError("Rating must be between 1 and 5")


class ReviewStatus(Enum):
    """Review status enumeration."""

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    HIDDEN = "hidden"


class ReviewType(Enum):
    """Review type enumeration."""

    PRODUCT = "product"
    SELLER = "seller"
    DELIVERY = "delivery"


@dataclass(frozen=True)
class ReviewTitle(ValueObject):
    """Review title value object."""

    value: str

    def __post_init__(self) -> None:
        """Validate review title after initialization."""
        if not self.value or len(self.value.strip()) < 3:
            raise ValueError("Review title must be at least 3 characters long")
        if len(self.value.strip()) > 100:
            raise ValueError("Review title cannot exceed 100 characters")
        # Normalize review title
        object.__setattr__(self, "value", self.value.strip())


@dataclass(frozen=True)
class ReviewContent(ValueObject):
    """Review content value object."""

    value: str

    def __post_init__(self) -> None:
        """Validate review content after initialization."""
        if not self.value or len(self.value.strip()) < 10:
            raise ValueError("Review content must be at least 10 characters long")
        if len(self.value.strip()) > 2000:
            raise ValueError("Review content cannot exceed 2000 characters")
        # Normalize review content
        object.__setattr__(self, "value", self.value.strip())


@dataclass(frozen=True)
class HelpfulVotes(ValueObject):
    """Helpful votes value object."""

    value: int

    def __post_init__(self) -> None:
        """Validate helpful votes after initialization."""
        if self.value < 0:
            raise ValueError("Helpful votes cannot be negative")

    def increment(self) -> "HelpfulVotes":
        """Increment helpful votes and return new instance."""
        return self.__class__(value=self.value + 1)

    def decrement(self) -> "HelpfulVotes":
        """Decrement helpful votes and return new instance."""
        if self.value > 0:
            return self.__class__(value=self.value - 1)
        return self
