"""Domain events for reviews."""

from dataclasses import dataclass
from datetime import datetime

from src.reviews.domain.value_objects import ReviewId
from src.shared.domain.events import DomainEvent


@dataclass
class ReviewCreated(DomainEvent):
    """Event raised when a review is created."""
    
    review_id: ReviewId
    occurred_on: datetime = None

    def __post_init__(self):
        if self.occurred_on is None:
            from datetime import UTC
            self.occurred_on = datetime.now(UTC)


@dataclass
class ReviewApproved(DomainEvent):
    """Event raised when a review is approved."""
    
    review_id: ReviewId
    occurred_on: datetime = None

    def __post_init__(self):
        if self.occurred_on is None:
            from datetime import UTC
            self.occurred_on = datetime.now(UTC)


@dataclass
class ReviewRejected(DomainEvent):
    """Event raised when a review is rejected."""
    
    review_id: ReviewId
    reason: str
    occurred_on: datetime = None

    def __post_init__(self):
        if self.occurred_on is None:
            from datetime import UTC
            self.occurred_on = datetime.now(UTC)


@dataclass
class ReviewResponseAdded(DomainEvent):
    """Event raised when a response is added to a review."""
    
    review_id: ReviewId
    response_id: ReviewId
    occurred_on: datetime = None

    def __post_init__(self):
        if self.occurred_on is None:
            from datetime import UTC
            self.occurred_on = datetime.now(UTC)


@dataclass
class ReviewMarkedHelpful(DomainEvent):
    """Event raised when a review is marked as helpful."""
    
    review_id: ReviewId
    occurred_on: datetime = None

    def __post_init__(self):
        if self.occurred_on is None:
            from datetime import UTC
            self.occurred_on = datetime.now(UTC) 