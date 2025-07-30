"""In-memory repositories for reviews domain."""

from typing import Dict, List, Optional

from src.reviews.domain.entities import Review, ReviewResponse, ReviewModeration
from src.reviews.domain.repositories import (
    ReviewRepository,
    ReviewResponseRepository,
    ReviewModerationRepository,
)
from src.reviews.domain.value_objects import ReviewId, ReviewStatus
from src.users.domain.value_objects import UserId


class InMemoryReviewRepository(ReviewRepository):
    """In-memory implementation of ReviewRepository."""

    def __init__(self):
        self._reviews: Dict[str, Review] = {}
        self._reviews_by_user_id: Dict[str, List[Review]] = {}
        self._reviews_by_product_id: Dict[str, List[Review]] = {}
        self._reviews_by_status: Dict[ReviewStatus, List[Review]] = {}

    async def save(self, review: Review) -> Review:
        """Save a review."""
        review_id_str = str(review.id)
        self._reviews[review_id_str] = review

        # Update indexes
        user_id_str = str(review.user_id)
        if user_id_str not in self._reviews_by_user_id:
            self._reviews_by_user_id[user_id_str] = []
        self._reviews_by_user_id[user_id_str].append(review)

        if review.product_id:
            product_id_str = str(review.product_id)
            if product_id_str not in self._reviews_by_product_id:
                self._reviews_by_product_id[product_id_str] = []
            self._reviews_by_product_id[product_id_str].append(review)

        if review.status not in self._reviews_by_status:
            self._reviews_by_status[review.status] = []
        self._reviews_by_status[review.status].append(review)

        return review

    async def get_by_id(self, review_id: ReviewId) -> Optional[Review]:
        """Get review by ID."""
        return self._reviews.get(str(review_id))

    async def get_by_user_id(self, user_id: UserId) -> List[Review]:
        """Get reviews by user ID."""
        return self._reviews_by_user_id.get(str(user_id), [])

    async def get_by_product_id(self, product_id: str) -> List[Review]:
        """Get reviews by product ID."""
        return self._reviews_by_product_id.get(product_id, [])

    async def get_by_status(self, status: ReviewStatus) -> List[Review]:
        """Get reviews by status."""
        return self._reviews_by_status.get(status, [])

    async def get_pending_reviews(self) -> List[Review]:
        """Get all pending reviews."""
        return self._reviews_by_status.get(ReviewStatus.PENDING, [])

    async def delete(self, review_id: ReviewId) -> None:
        """Delete a review."""
        review_id_str = str(review_id)
        if review_id_str in self._reviews:
            review = self._reviews[review_id_str]
            del self._reviews[review_id_str]

            # Remove from indexes
            user_id_str = str(review.user_id)
            if user_id_str in self._reviews_by_user_id:
                self._reviews_by_user_id[user_id_str] = [
                    r for r in self._reviews_by_user_id[user_id_str] if r.id != review_id
                ]

            if review.product_id:
                product_id_str = str(review.product_id)
                if product_id_str in self._reviews_by_product_id:
                    self._reviews_by_product_id[product_id_str] = [
                        r for r in self._reviews_by_product_id[product_id_str] 
                        if r.id != review_id
                    ]

            if review.status in self._reviews_by_status:
                self._reviews_by_status[review.status] = [
                    r for r in self._reviews_by_status[review.status] if r.id != review_id
                ]


class InMemoryReviewResponseRepository(ReviewResponseRepository):
    """In-memory implementation of ReviewResponseRepository."""

    def __init__(self):
        self._responses: Dict[str, ReviewResponse] = {}
        self._responses_by_review_id: Dict[str, List[ReviewResponse]] = {}
        self._responses_by_responder_id: Dict[str, List[ReviewResponse]] = {}

    async def save(self, response: ReviewResponse) -> ReviewResponse:
        """Save a review response."""
        response_id_str = str(response.id)
        self._responses[response_id_str] = response

        # Update indexes
        review_id_str = str(response.review_id)
        if review_id_str not in self._responses_by_review_id:
            self._responses_by_review_id[review_id_str] = []
        self._responses_by_review_id[review_id_str].append(response)

        responder_id_str = str(response.responder_id)
        if responder_id_str not in self._responses_by_responder_id:
            self._responses_by_responder_id[responder_id_str] = []
        self._responses_by_responder_id[responder_id_str].append(response)

        return response

    async def get_by_id(self, response_id: ReviewId) -> Optional[ReviewResponse]:
        """Get response by ID."""
        return self._responses.get(str(response_id))

    async def get_by_review_id(self, review_id: ReviewId) -> List[ReviewResponse]:
        """Get responses by review ID."""
        return self._responses_by_review_id.get(str(review_id), [])

    async def get_by_responder_id(self, responder_id: UserId) -> List[ReviewResponse]:
        """Get responses by responder ID."""
        return self._responses_by_responder_id.get(str(responder_id), [])

    async def delete(self, response_id: ReviewId) -> None:
        """Delete a response."""
        response_id_str = str(response_id)
        if response_id_str in self._responses:
            response = self._responses[response_id_str]
            del self._responses[response_id_str]

            # Remove from indexes
            review_id_str = str(response.review_id)
            if review_id_str in self._responses_by_review_id:
                self._responses_by_review_id[review_id_str] = [
                    r for r in self._responses_by_review_id[review_id_str] 
                    if r.id != response_id
                ]

            responder_id_str = str(response.responder_id)
            if responder_id_str in self._responses_by_responder_id:
                self._responses_by_responder_id[responder_id_str] = [
                    r for r in self._responses_by_responder_id[responder_id_str] 
                    if r.id != response_id
                ]


class InMemoryReviewModerationRepository(ReviewModerationRepository):
    """In-memory implementation of ReviewModerationRepository."""

    def __init__(self):
        self._moderations: Dict[str, ReviewModeration] = {}
        self._moderations_by_review_id: Dict[str, List[ReviewModeration]] = {}
        self._moderations_by_moderator_id: Dict[str, List[ReviewModeration]] = {}

    async def save(self, moderation: ReviewModeration) -> ReviewModeration:
        """Save a moderation record."""
        moderation_id_str = str(moderation.id)
        self._moderations[moderation_id_str] = moderation

        # Update indexes
        review_id_str = str(moderation.review_id)
        if review_id_str not in self._moderations_by_review_id:
            self._moderations_by_review_id[review_id_str] = []
        self._moderations_by_review_id[review_id_str].append(moderation)

        moderator_id_str = str(moderation.moderator_id)
        if moderator_id_str not in self._moderations_by_moderator_id:
            self._moderations_by_moderator_id[moderator_id_str] = []
        self._moderations_by_moderator_id[moderator_id_str].append(moderation)

        return moderation

    async def get_by_id(self, moderation_id: ReviewId) -> Optional[ReviewModeration]:
        """Get moderation by ID."""
        return self._moderations.get(str(moderation_id))

    async def get_by_review_id(self, review_id: ReviewId) -> List[ReviewModeration]:
        """Get moderation records by review ID."""
        return self._moderations_by_review_id.get(str(review_id), [])

    async def get_by_moderator_id(self, moderator_id: UserId) -> List[ReviewModeration]:
        """Get moderation records by moderator ID."""
        return self._moderations_by_moderator_id.get(str(moderator_id), [])

    async def delete(self, moderation_id: ReviewId) -> None:
        """Delete a moderation record."""
        moderation_id_str = str(moderation_id)
        if moderation_id_str in self._moderations:
            moderation = self._moderations[moderation_id_str]
            del self._moderations[moderation_id_str]

            # Remove from indexes
            review_id_str = str(moderation.review_id)
            if review_id_str in self._moderations_by_review_id:
                self._moderations_by_review_id[review_id_str] = [
                    m for m in self._moderations_by_review_id[review_id_str] 
                    if m.id != moderation_id
                ]

            moderator_id_str = str(moderation.moderator_id)
            if moderator_id_str in self._moderations_by_moderator_id:
                self._moderations_by_moderator_id[moderator_id_str] = [
                    m for m in self._moderations_by_moderator_id[moderator_id_str] 
                    if m.id != moderation_id
                ] 