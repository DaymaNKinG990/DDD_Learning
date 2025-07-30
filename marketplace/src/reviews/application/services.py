"""Application services for reviews domain."""

from datetime import UTC, datetime
from typing import List, Optional

from src.reviews.domain.entities import Review, ReviewResponse, ReviewModeration
from src.reviews.domain.events import ReviewCreated, ReviewApproved, ReviewRejected
from src.reviews.domain.repositories import (
    ReviewRepository,
    ReviewResponseRepository,
    ReviewModerationRepository,
)
from src.reviews.domain.value_objects import (
    ReviewContent,
    ReviewId,
    ReviewStatus,
    ReviewTitle,
    Rating,
    ReviewType,
)
from src.catalog.domain.value_objects import ProductId
from src.shared.application.event_handlers import EventHandler
from src.shared.domain.events import DomainEvent
from src.users.domain.value_objects import UserId


class ReviewService:
    """Service for managing reviews."""

    def __init__(
        self,
        review_repository: ReviewRepository,
        review_response_repository: ReviewResponseRepository,
        review_moderation_repository: ReviewModerationRepository,
        event_handler: Optional[EventHandler] = None,
    ):
        self.review_repository = review_repository
        self.review_response_repository = review_response_repository
        self.review_moderation_repository = review_moderation_repository
        self.event_handler = event_handler

    async def create_review(
        self,
        user_id: str,
        review_type: str,
        title: str,
        content: str,
        rating: int,
        product_id: Optional[str] = None,
        seller_id: Optional[str] = None,
        order_id: Optional[str] = None,
    ) -> Review:
        """Create a new review."""
        review = Review(
            id=ReviewId.generate(),
            user_id=UserId(value=user_id),
            review_type=ReviewType(review_type),
            title=ReviewTitle(value=title),
            content=ReviewContent(value=content),
            rating=Rating(value=rating),
            product_id=ProductId(value=product_id) if product_id else None,
            seller_id=seller_id,
            order_id=order_id,
        )

        saved_review = await self.review_repository.save(review)
        
        if self.event_handler:
            await self.event_handler.handle(ReviewCreated(review_id=review.id))
        
        return saved_review

    async def approve_review(
        self, review_id: str, moderator_id: str, notes: Optional[str] = None
    ) -> Review:
        """Approve a review."""
        review = await self.review_repository.get_by_id(ReviewId(value=review_id))
        if not review:
            raise ValueError(f"Review with ID {review_id} not found")

        review.approve()
        saved_review = await self.review_repository.save(review)

        # Create moderation record
        moderation = ReviewModeration(
            id=ReviewId.generate(),
            review_id=review.id,
            moderator_id=UserId(value=moderator_id),
            action="approve",
            notes=notes,
        )
        await self.review_moderation_repository.save(moderation)

        if self.event_handler:
            await self.event_handler.handle(ReviewApproved(review_id=review.id))
        
        return saved_review

    async def reject_review(
        self, review_id: str, moderator_id: str, reason: str, notes: Optional[str] = None
    ) -> Review:
        """Reject a review."""
        review = await self.review_repository.get_by_id(ReviewId(value=review_id))
        if not review:
            raise ValueError(f"Review with ID {review_id} not found")

        review.reject(reason)
        saved_review = await self.review_repository.save(review)

        # Create moderation record
        moderation = ReviewModeration(
            id=ReviewId.generate(),
            review_id=review.id,
            moderator_id=UserId(value=moderator_id),
            action="reject",
            reason=reason,
            notes=notes,
        )
        await self.review_moderation_repository.save(moderation)

        if self.event_handler:
            await self.event_handler.handle(ReviewRejected(review_id=review.id))
        
        return saved_review

    async def add_response(
        self, review_id: str, responder_id: str, content: str, is_public: bool = True
    ) -> ReviewResponse:
        """Add response to a review."""
        review = await self.review_repository.get_by_id(ReviewId(value=review_id))
        if not review:
            raise ValueError(f"Review with ID {review_id} not found")

        response = ReviewResponse(
            id=ReviewId.generate(),
            review_id=review.id,
            responder_id=UserId(value=responder_id),
            content=ReviewContent(value=content),
            is_public=is_public,
        )

        return await self.review_response_repository.save(response)

    async def mark_review_helpful(self, review_id: str) -> Review:
        """Mark review as helpful."""
        review = await self.review_repository.get_by_id(ReviewId(value=review_id))
        if not review:
            raise ValueError(f"Review with ID {review_id} not found")

        review.mark_as_helpful()
        return await self.review_repository.save(review)

    async def update_review(
        self, review_id: str, title: str, content: str, rating: int
    ) -> Review:
        """Update review content."""
        review = await self.review_repository.get_by_id(ReviewId(value=review_id))
        if not review:
            raise ValueError(f"Review with ID {review_id} not found")

        review.update_content(title, content, rating)
        return await self.review_repository.save(review) 