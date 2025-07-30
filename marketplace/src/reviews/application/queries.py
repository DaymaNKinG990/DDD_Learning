"""Queries for reviews domain."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from src.reviews.domain.value_objects import ReviewId, ReviewStatus, ReviewType
from src.users.domain.value_objects import UserId


# Read Models
class ReviewReadModel(BaseModel):
    """Read model for Review."""
    
    id: str
    user_id: str
    review_type: str
    title: str
    content: str
    rating: int
    product_id: Optional[str] = None
    seller_id: Optional[str] = None
    order_id: Optional[str] = None
    status: str
    helpful_votes: int
    is_verified_purchase: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    moderator_notes: Optional[str] = None


class ReviewResponseReadModel(BaseModel):
    """Read model for ReviewResponse."""
    
    id: str
    review_id: str
    responder_id: str
    content: str
    is_public: bool
    created_at: datetime
    updated_at: Optional[datetime] = None


class ReviewModerationReadModel(BaseModel):
    """Read model for ReviewModeration."""
    
    id: str
    review_id: str
    moderator_id: str
    action: str
    reason: Optional[str] = None
    created_at: datetime
    notes: Optional[str] = None


# Query Commands
@dataclass
class GetReviewQuery:
    """Query to get a review by ID."""
    review_id: str


@dataclass
class GetReviewsByUserQuery:
    """Query to get reviews by user ID."""
    user_id: str
    status: Optional[ReviewStatus] = None
    limit: int = 50
    offset: int = 0


@dataclass
class GetReviewsByProductQuery:
    """Query to get reviews by product ID."""
    product_id: str
    status: ReviewStatus = ReviewStatus.APPROVED
    limit: int = 50
    offset: int = 0


@dataclass
class GetReviewsByStatusQuery:
    """Query to get reviews by status."""
    status: ReviewStatus
    limit: int = 50
    offset: int = 0


@dataclass
class SearchReviewsQuery:
    """Query to search reviews."""
    query: str
    review_type: Optional[ReviewType] = None
    status: ReviewStatus = ReviewStatus.APPROVED
    min_rating: Optional[int] = None
    max_rating: Optional[int] = None
    limit: int = 50
    offset: int = 0


@dataclass
class GetReviewResponsesQuery:
    """Query to get responses for a review."""
    review_id: str
    limit: int = 50
    offset: int = 0


@dataclass
class GetReviewModerationHistoryQuery:
    """Query to get moderation history for a review."""
    review_id: str
    limit: int = 50
    offset: int = 0


# Query Handlers
class ReviewQueryHandler(ABC):
    """Abstract query handler for reviews."""

    @abstractmethod
    async def get_review(self, query: GetReviewQuery) -> Optional[ReviewReadModel]:
        """Get review by ID."""
        pass

    @abstractmethod
    async def get_reviews_by_user(
        self, query: GetReviewsByUserQuery
    ) -> List[ReviewReadModel]:
        """Get reviews by user ID."""
        pass

    @abstractmethod
    async def get_reviews_by_product(
        self, query: GetReviewsByProductQuery
    ) -> List[ReviewReadModel]:
        """Get reviews by product ID."""
        pass

    @abstractmethod
    async def get_reviews_by_status(
        self, query: GetReviewsByStatusQuery
    ) -> List[ReviewReadModel]:
        """Get reviews by status."""
        pass

    @abstractmethod
    async def search_reviews(
        self, query: SearchReviewsQuery
    ) -> List[ReviewReadModel]:
        """Search reviews."""
        pass

    @abstractmethod
    async def get_review_responses(
        self, query: GetReviewResponsesQuery
    ) -> List[ReviewResponseReadModel]:
        """Get responses for a review."""
        pass

    @abstractmethod
    async def get_review_moderation_history(
        self, query: GetReviewModerationHistoryQuery
    ) -> List[ReviewModerationReadModel]:
        """Get moderation history for a review."""
        pass


class ReviewResponseQueryHandler(ABC):
    """Abstract query handler for review responses."""

    @abstractmethod
    async def get_response_by_id(
        self, response_id: str
    ) -> Optional[ReviewResponseReadModel]:
        """Get response by ID."""
        pass

    @abstractmethod
    async def get_responses_by_responder(
        self, responder_id: str, limit: int = 50, offset: int = 0
    ) -> List[ReviewResponseReadModel]:
        """Get responses by responder ID."""
        pass


class ReviewModerationQueryHandler(ABC):
    """Abstract query handler for review moderation."""

    @abstractmethod
    async def get_moderation_by_id(
        self, moderation_id: str
    ) -> Optional[ReviewModerationReadModel]:
        """Get moderation by ID."""
        pass

    @abstractmethod
    async def get_moderations_by_moderator(
        self, moderator_id: str, limit: int = 50, offset: int = 0
    ) -> List[ReviewModerationReadModel]:
        """Get moderations by moderator ID."""
        pass 