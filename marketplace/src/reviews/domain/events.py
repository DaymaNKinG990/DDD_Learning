"""Domain events for reviews."""

# Python imports
from dataclasses import dataclass
from datetime import UTC, datetime

# Local imports
from src.reviews.domain.value_objects import ReviewId
from src.shared.domain.events import DomainEvent


@dataclass
class ReviewCreated(DomainEvent):
    """Event raised when a review is created.
    
    This event is raised when a review is created.
    
    Attributes:
        review_id (ReviewId): The ID of the review.
        occurred_on (datetime): The date and time the event occurred.
    """

    review_id: ReviewId
    occurred_on: datetime = None

    def __post_init__(self) -> None:
        """
        Initialize the event.
        
        This method initializes the event and sets the occurred_on timestamp.
        """
        if self.occurred_on is None:
            self.occurred_on = datetime.now(UTC)


@dataclass
class ReviewApproved(DomainEvent):
    """Event raised when a review is approved.
    
    This event is raised when a review is approved.
    
    Attributes:
        review_id (ReviewId): The ID of the review.
        occurred_on (datetime): The date and time the event occurred.
    """
    
    review_id: ReviewId
    occurred_on: datetime = None

    def __post_init__(self) -> None:
        """
        Initialize the event.
        
        This method initializes the event and sets the occurred_on timestamp.
        """
        if self.occurred_on is None:
            self.occurred_on = datetime.now(UTC)


@dataclass
class ReviewRejected(DomainEvent):
    """Event raised when a review is rejected.
    
    This event is raised when a review is rejected.
    
    Attributes:
        review_id (ReviewId): The ID of the review.
        reason (str): The reason for rejecting the review.
        occurred_on (datetime): The date and time the event occurred.
    """
    
    review_id: ReviewId
    reason: str
    occurred_on: datetime = None

    def __post_init__(self) -> None:
        """
        Initialize the event.
        
        This method initializes the event and sets the occurred_on timestamp.
        """
        if self.occurred_on is None:
            self.occurred_on = datetime.now(UTC)


@dataclass
class ReviewResponseAdded(DomainEvent):
    """Event raised when a response is added to a review.
    
    This event is raised when a response is added to a review.
    
    Attributes:
        review_id (ReviewId): The ID of the review.
        response_id (ReviewId): The ID of the response.
        occurred_on (datetime): The date and time the event occurred.
    """
    
    review_id: ReviewId
    response_id: ReviewId
    occurred_on: datetime = None

    def __post_init__(self) -> None:
        """
        Initialize the event.
        
        This method initializes the event and sets the occurred_on timestamp.
        """
        if self.occurred_on is None:
            self.occurred_on = datetime.now(UTC)


@dataclass
class ReviewMarkedHelpful(DomainEvent):
    """Event raised when a review is marked as helpful.
    
    This event is raised when a review is marked as helpful.
    
    Attributes:
        review_id (ReviewId): The ID of the review.
        occurred_on (datetime): The date and time the event occurred.
    """
    
    review_id: ReviewId
    occurred_on: datetime = None

    def __post_init__(self) -> None:
        """
        Initialize the event.
        
        This method initializes the event and sets the occurred_on timestamp.
        """
        if self.occurred_on is None:
            self.occurred_on = datetime.now(UTC) 