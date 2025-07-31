"""Entities for reviews domain."""

# Python imports
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Optional

# Local imports
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
    """Review entity.
    
    This entity represents a review of a product or seller.
    
    Attributes:
        id (ReviewId): The ID of the review.
        user_id (UserId): The ID of the user who wrote the review.
        review_type (ReviewType): The type of review (product or seller).
        title (ReviewTitle): The title of the review.
        content (ReviewContent): The content of the review.
        rating (Rating): The rating of the review.
        product_id (Optional[ProductId]): The ID of the product being reviewed.
        seller_id (Optional[str]): The ID of the seller being reviewed.
        order_id (Optional[str]): The ID of the order being reviewed.
        status (ReviewStatus): The status of the review.
        helpful_votes (HelpfulVotes): The number of helpful votes for the review.
        is_verified_purchase (bool): Whether the purchase was verified.
        created_at (datetime): The date and time the review was created.
        updated_at (Optional[datetime]): The date and time the review was last updated.
        moderator_notes (Optional[str]): The notes from the moderator.
    """

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
        """
        Reject review.
        
        Args:
            reason (str): The reason for rejecting the review.
        """
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
        """
        Update review content.
        
        Args:
            title (str): The new title of the review.
            content (str): The new content of the review.
            rating (int): The new rating of the review.
        """
        self.title = ReviewTitle(value=title)
        self.content = ReviewContent(value=content)
        self.rating = Rating(value=rating)
        self.updated_at = datetime.now(UTC)

    def is_approved(self) -> bool:
        """
        Check if review is approved.
        
        Returns:
            bool: True if the review is approved, False otherwise.
        """
        return self.status == ReviewStatus.APPROVED

    def is_pending(self) -> bool:
        """
        Check if review is pending.
        
        Returns:
            bool: True if the review is pending, False otherwise.
        """
        return self.status == ReviewStatus.PENDING

    def is_rejected(self) -> bool:
        """
        Check if review is rejected.
        
        Returns:
            bool: True if the review is rejected, False otherwise.
        """
        return self.status == ReviewStatus.REJECTED


@dataclass
class ReviewResponse(Entity[ReviewId]):
    """
    Review response entity (seller/company response to review).
    
    This entity represents a response to a review.
    
    Attributes:
        id (ReviewId): The ID of the review response.
        review_id (ReviewId): The ID of the review being responded to.
        responder_id (UserId): The ID of the user who responded to the review.
        content (ReviewContent): The content of the response.
        is_public (bool): Whether the response is public.
        created_at (datetime): The date and time the response was created.
        updated_at (Optional[datetime]): The date and time the response was last updated.
    """

    id: ReviewId
    review_id: ReviewId
    responder_id: UserId
    content: ReviewContent
    is_public: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: Optional[datetime] = None

    def update_content(self, content: str) -> None:
        """
        Update response content.
        
        Args:
            content (str): The new content of the response.
        """
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
    """Review moderation entity.
    
    This entity represents a moderation action on a review.
    
    Attributes:
        id (ReviewId): The ID of the moderation.
        review_id (ReviewId): The ID of the review being moderated.
        moderator_id (UserId): The ID of the user who moderated the review.
        action (str): The action taken on the review.
        reason (Optional[str]): The reason for the moderation action.
        created_at (datetime): The date and time the moderation action was taken.
        notes (Optional[str]): Additional notes from the moderator.
    """

    id: ReviewId
    review_id: ReviewId
    moderator_id: UserId
    action: str
    reason: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    notes: Optional[str] = None

    def add_note(self, note: str) -> None:
        """Add moderation note.
        
        Args:
            note (str): The note to add to the moderation.
        """
        if self.notes:
            self.notes += f"\n{note}"
        else:
            self.notes = note
