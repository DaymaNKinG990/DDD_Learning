"""In-memory repositories for reviews domain."""

# Python imports
from typing import Dict, List, Optional

# Local imports
from src.reviews.domain.entities import Review, ReviewResponse, ReviewModeration
from src.reviews.domain.repositories import (
    ReviewRepository,
    ReviewResponseRepository,
    ReviewModerationRepository,
)
from src.reviews.domain.value_objects import ReviewId, ReviewStatus
from src.users.domain.value_objects import UserId


class InMemoryReviewRepository(ReviewRepository):
    """
    In-memory implementation of ReviewRepository.
    
    This repository provides an in-memory implementation of the ReviewRepository interface.
    """

    def __init__(self) -> None:
        """Initialize the repository."""
        self._reviews: Dict[str, Review] = {}
        self._reviews_by_user_id: Dict[str, List[Review]] = {}
        self._reviews_by_product_id: Dict[str, List[Review]] = {}
        self._reviews_by_status: Dict[ReviewStatus, List[Review]] = {}

    async def save(self, review: Review) -> Review:
        """
        Save a review.
        
        Args:
            review (Review): The review to save.

        Returns:
            Review: The saved review.
        """
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
        """
        Get review by ID.
        
        Args:
            review_id (ReviewId): The ID of the review to get.

        Returns:
            Optional[Review]: The review if found, None otherwise.
        """
        return self._reviews.get(str(review_id))

    async def get_by_user_id(self, user_id: UserId) -> List[Review]:
        """
        Get reviews by user ID.
        
        Args:
            user_id (UserId): The ID of the user to get reviews for.

        Returns:
            List[Review]: The reviews for the user.
        """
        return self._reviews_by_user_id.get(str(user_id), [])

    async def get_by_product_id(self, product_id: str) -> List[Review]:
        """
        Get reviews by product ID.
        
        Args:
            product_id (str): The ID of the product to get reviews for.

        Returns:
            List[Review]: The reviews for the product.
        """
        return self._reviews_by_product_id.get(product_id, [])

    async def get_by_status(self, status: ReviewStatus) -> List[Review]:
        """
        Get reviews by status.
        
        Args:
            status (ReviewStatus): The status of the reviews to get.

        Returns:
            List[Review]: The reviews with the given status.
        """
        return self._reviews_by_status.get(status, [])

    async def get_pending_reviews(self) -> List[Review]:
        """
        Get all pending reviews.
        
        Returns:
            List[Review]: All pending reviews.
        """
        return self._reviews_by_status.get(ReviewStatus.PENDING, [])

    async def delete(self, review_id: ReviewId) -> None:
        """
        Delete a review.
        
        Args:
            review_id (ReviewId): The ID of the review to delete.
        """
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
    """
    In-memory implementation of ReviewResponseRepository.
    
    This repository provides an in-memory implementation of the ReviewResponseRepository interface.
    """

    def __init__(self) -> None:
        """Initialize the repository."""
        self._responses: Dict[str, ReviewResponse] = {}
        self._responses_by_review_id: Dict[str, List[ReviewResponse]] = {}
        self._responses_by_responder_id: Dict[str, List[ReviewResponse]] = {}

    async def save(self, response: ReviewResponse) -> ReviewResponse:
        """
        Save a review response.
        
        Args:
            response (ReviewResponse): The review response to save.

        Returns:
            ReviewResponse: The saved review response.
        """
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
        """
        Get response by ID.
        
        Args:
            response_id (ReviewId): The ID of the response to get.

        Returns:
            Optional[ReviewResponse]: The response if found, None otherwise.
        """
        return self._responses.get(str(response_id))

    async def get_by_review_id(self, review_id: ReviewId) -> List[ReviewResponse]:
        """
        Get responses by review ID.
        
        Args:
            review_id (ReviewId): The ID of the review to get responses for.

        Returns:
            List[ReviewResponse]: The responses for the review.
        """
        return self._responses_by_review_id.get(str(review_id), [])

    async def get_by_responder_id(self, responder_id: UserId) -> List[ReviewResponse]:
        """
        Get responses by responder ID.
        
        Args:
            responder_id (UserId): The ID of the responder to get responses for.

        Returns:
            List[ReviewResponse]: The responses for the responder.
        """
        return self._responses_by_responder_id.get(str(responder_id), [])

    async def delete(self, response_id: ReviewId) -> None:
        """
        Delete a response.
        
        Args:
            response_id (ReviewId): The ID of the response to delete.
        """
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
    """
    In-memory implementation of ReviewModerationRepository.
    
    This repository provides an in-memory implementation of the ReviewModerationRepository interface.
    """

    def __init__(self) -> None:
        """Initialize the repository."""
        self._moderations: Dict[str, ReviewModeration] = {}
        self._moderations_by_review_id: Dict[str, List[ReviewModeration]] = {}
        self._moderations_by_moderator_id: Dict[str, List[ReviewModeration]] = {}

    async def save(self, moderation: ReviewModeration) -> ReviewModeration:
        """
        Save a moderation record.
        
        Args:
            moderation (ReviewModeration): The moderation record to save.

        Returns:
            ReviewModeration: The saved moderation record.
        """
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
        """
        Get moderation by ID.
        
        Args:
            moderation_id (ReviewId): The ID of the moderation to get.

        Returns:
            Optional[ReviewModeration]: The moderation if found, None otherwise.
        """
        return self._moderations.get(str(moderation_id))

    async def get_by_review_id(self, review_id: ReviewId) -> List[ReviewModeration]:
        """
        Get moderation records by review ID.
        
        Args:
            review_id (ReviewId): The ID of the review to get moderation records for.

        Returns:
            List[ReviewModeration]: The moderation records for the review.
        """
        return self._moderations_by_review_id.get(str(review_id), [])

    async def get_by_moderator_id(self, moderator_id: UserId) -> List[ReviewModeration]:
        """
        Get moderation records by moderator ID.
        
        Args:
            moderator_id (UserId): The ID of the moderator to get moderation records for.

        Returns:
            List[ReviewModeration]: The moderation records for the moderator.
        """
        return self._moderations_by_moderator_id.get(str(moderator_id), [])

    async def delete(self, moderation_id: ReviewId) -> None:
        """
        Delete a moderation record.
        
        Args:
            moderation_id (ReviewId): The ID of the moderation to delete.
        """
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