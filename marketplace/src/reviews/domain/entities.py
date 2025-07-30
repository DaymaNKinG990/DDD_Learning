"""Entities for reviews domain."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Optional

from src.catalog.domain.value_objects import ProductId
from src.reviews.domain.value_objects import (
    HelpfulVotes,
    Rating,
    ReviewContent,
    ReviewId,
    ReviewStatus,
    ReviewTitle,
    ReviewType,
)
from src.shared.domain.entity import Entity
from src.users.domain.value_objects import UserId


@dataclass
class Review(Entity[ReviewId]):
    """Review entity."""

    id: ReviewId
    user_id: UserId
    review_type: ReviewType
    title: ReviewTitle
    content: ReviewContent
    rating: Rating
    product_id: Optional[ProductId] = None
    seller_id: Optional[str] = None
    order_id: Optional[str] = None
    status: ReviewStatus = ReviewStatus.PENDING
    helpful_votes: HelpfulVotes = field(default_factory=lambda: HelpfulVotes(value=0))
    is_verified_purchase: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: Optional[datetime] = None
    moderator_notes: Optional[str] = None

    def approve(self) -> None:
        """Approve review."""
        self.status = ReviewStatus.APPROVED
        self.updated_at = datetime.now(UTC)

    def reject(self, reason: str) -> None:
        """Reject review."""
        self.status = ReviewStatus.REJECTED
        self.moderator_notes = reason
        self.updated_at = datetime.now(UTC)

    def hide(self) -> None:
        """Hide review."""
        self.status = ReviewStatus.HIDDEN
        self.updated_at = datetime.now(UTC)

    def mark_as_helpful(self) -> None:
        """Mark review as helpful."""
        self.helpful_votes = self.helpful_votes.increment()

    def unmark_as_helpful(self) -> None:
        """Unmark review as helpful."""
        self.helpful_votes = self.helpful_votes.decrement()

    def update_content(self, title: str, content: str, rating: int) -> None:
        """Update review content."""
        self.title = ReviewTitle(value=title)
        self.content = ReviewContent(value=content)
        self.rating = Rating(value=rating)
        self.updated_at = datetime.now(UTC)

    def is_approved(self) -> bool:
        """Check if review is approved."""
        return self.status == ReviewStatus.APPROVED

    def is_pending(self) -> bool:
        """Check if review is pending."""
        return self.status == ReviewStatus.PENDING

    def is_rejected(self) -> bool:
        """Check if review is rejected."""
        return self.status == ReviewStatus.REJECTED


@dataclass
class ReviewResponse(Entity[ReviewId]):
    """Review response entity (seller/company response to review)."""

    id: ReviewId
    review_id: ReviewId
    responder_id: UserId
    content: ReviewContent
    is_public: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: Optional[datetime] = None

    def update_content(self, content: str) -> None:
        """Update response content."""
        self.content = ReviewContent(value=content)
        self.updated_at = datetime.now(UTC)

    def make_private(self) -> None:
        """Make response private."""
        self.is_public = False

    def make_public(self) -> None:
        """Make response public."""
        self.is_public = True


@dataclass
class ReviewModeration(Entity[ReviewId]):
    """Review moderation entity."""

    id: ReviewId
    review_id: ReviewId
    moderator_id: UserId
    action: str
    reason: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    notes: Optional[str] = None

    def add_note(self, note: str) -> None:
        """Add moderation note."""
        if self.notes:
            self.notes += f"\n{note}"
        else:
            self.notes = note
