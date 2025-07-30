"""Repository interfaces for reviews domain."""

from abc import ABC, abstractmethod
from typing import List, Optional

from src.reviews.domain.entities import Review, ReviewResponse, ReviewModeration
from src.reviews.domain.value_objects import ReviewId, ReviewStatus
from src.users.domain.value_objects import UserId


class ReviewRepository(ABC):
    """Repository interface for Review entity."""

    @abstractmethod
    async def save(self, review: Review) -> Review:
        """Save a review."""
        pass

    @abstractmethod
    async def get_by_id(self, review_id: ReviewId) -> Optional[Review]:
        """Get review by ID."""
        pass

    @abstractmethod
    async def get_by_user_id(self, user_id: UserId) -> List[Review]:
        """Get reviews by user ID."""
        pass

    @abstractmethod
    async def get_by_product_id(self, product_id: str) -> List[Review]:
        """Get reviews by product ID."""
        pass

    @abstractmethod
    async def get_by_status(self, status: ReviewStatus) -> List[Review]:
        """Get reviews by status."""
        pass

    @abstractmethod
    async def get_pending_reviews(self) -> List[Review]:
        """Get all pending reviews."""
        pass

    @abstractmethod
    async def delete(self, review_id: ReviewId) -> None:
        """Delete a review."""
        pass


class ReviewResponseRepository(ABC):
    """Repository interface for ReviewResponse entity."""

    @abstractmethod
    async def save(self, response: ReviewResponse) -> ReviewResponse:
        """Save a review response."""
        pass

    @abstractmethod
    async def get_by_id(self, response_id: ReviewId) -> Optional[ReviewResponse]:
        """Get response by ID."""
        pass

    @abstractmethod
    async def get_by_review_id(self, review_id: ReviewId) -> List[ReviewResponse]:
        """Get responses by review ID."""
        pass

    @abstractmethod
    async def get_by_responder_id(self, responder_id: UserId) -> List[ReviewResponse]:
        """Get responses by responder ID."""
        pass

    @abstractmethod
    async def delete(self, response_id: ReviewId) -> None:
        """Delete a response."""
        pass


class ReviewModerationRepository(ABC):
    """Repository interface for ReviewModeration entity."""

    @abstractmethod
    async def save(self, moderation: ReviewModeration) -> ReviewModeration:
        """Save a moderation record."""
        pass

    @abstractmethod
    async def get_by_id(self, moderation_id: ReviewId) -> Optional[ReviewModeration]:
        """Get moderation by ID."""
        pass

    @abstractmethod
    async def get_by_review_id(self, review_id: ReviewId) -> List[ReviewModeration]:
        """Get moderation records by review ID."""
        pass

    @abstractmethod
    async def get_by_moderator_id(self, moderator_id: UserId) -> List[ReviewModeration]:
        """Get moderation records by moderator ID."""
        pass

    @abstractmethod
    async def delete(self, moderation_id: ReviewId) -> None:
        """Delete a moderation record."""
        pass 