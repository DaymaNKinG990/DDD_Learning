"""Value objects for reviews domain."""

# Python imports
from dataclasses import dataclass
from enum import Enum
import uuid

# Local imports
from src.shared.domain.value_object import ValueObject


@dataclass(frozen=True)
class ReviewId(ValueObject):
    """
    Review ID value object.
    
    This value object represents the identifier for a review.
    
    Attributes:
        value (str): The value of the review identifier.
    """

    value: str

    @classmethod
    def generate(cls) -> "ReviewId":
        """
        Generate a new review ID.
        
        Returns:
            ReviewId: The generated review ID.
        """
        return cls(value=f"review_{uuid.uuid4().hex}")


@dataclass(frozen=True)
class Rating(ValueObject):
    """
    Rating value object.
    
    This value object represents the rating of a review.
    
    Attributes:
        value (int): The value of the rating.
    """

    value: int

    def __post_init__(self) -> None:
        """Validate rating value after initialization."""
        if not 1 <= self.value <= 5:
            raise ValueError("Rating must be between 1 and 5")


class ReviewStatus(Enum):
    """
    Review status enumeration.
    
    This enumeration represents the status of a review.
    
    Attributes:
        PENDING (str): The review is pending.
        APPROVED (str): The review is approved.
        REJECTED (str): The review is rejected.
        HIDDEN (str): The review is hidden.
    """

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    HIDDEN = "hidden"


class ReviewType(Enum):
    """
    Review type enumeration.
    
    This enumeration represents the type of a review.
    
    Attributes:
        PRODUCT (str): The review is for a product.
        SELLER (str): The review is for a seller.
        DELIVERY (str): The review is for a delivery.
    """

    PRODUCT = "product"
    SELLER = "seller"
    DELIVERY = "delivery"


@dataclass(frozen=True)
class ReviewTitle(ValueObject):
    """
    Review title value object.
    
    This value object represents the title of a review.
    
    Attributes:
        value (str): The value of the review title.
    """

    value: str

    def __post_init__(self) -> None:
        """
        Validate review title after initialization.
        
        Raises:
            ValueError: If the review title is not at least 3 characters long or exceeds 100 characters.
        """
        if not self.value or len(self.value.strip()) < 3:
            raise ValueError("Review title must be at least 3 characters long")
        if len(self.value.strip()) > 100:
            raise ValueError("Review title cannot exceed 100 characters")
        # Normalize review title
        object.__setattr__(self, "value", self.value.strip())


@dataclass(frozen=True)
class ReviewContent(ValueObject):
    """
    Review content value object.
    
    This value object represents the content of a review.
    
    Attributes:
        value (str): The value of the review content.
    """

    value: str

    def __post_init__(self) -> None:
        """
        Validate review content after initialization.
        
        Raises:
            ValueError: If the review content is not at least 10 characters long or exceeds 2000 characters.
        """
        if not self.value or len(self.value.strip()) < 10:
            raise ValueError("Review content must be at least 10 characters long")
        if len(self.value.strip()) > 2000:
            raise ValueError("Review content cannot exceed 2000 characters")
        # Normalize review content
        object.__setattr__(self, "value", self.value.strip())


@dataclass(frozen=True)
class HelpfulVotes(ValueObject):
    """
    Helpful votes value object.
    
    This value object represents the number of helpful votes for a review.
    
    Attributes:
        value (int): The value of the helpful votes.
    """

    value: int

    def __post_init__(self) -> None:
        """
        Validate helpful votes after initialization.
        
        Raises:
            ValueError: If the helpful votes are negative.
        """
        if self.value < 0:
            raise ValueError("Helpful votes cannot be negative")

    def increment(self) -> "HelpfulVotes":
        """
        Increment helpful votes and return new instance.
        
        Returns:
            HelpfulVotes: The new instance with the incremented helpful votes.
        """
        return self.__class__(value=self.value + 1)

    def decrement(self) -> "HelpfulVotes":
        """
        Decrement helpful votes and return new instance.
        
        Returns:
            HelpfulVotes: The new instance with the decremented helpful votes.
        """
        if self.value > 0:
            return self.__class__(value=self.value - 1)
        return self
