"""Repository interfaces for reviews domain."""

# Python imports
from abc import ABC, abstractmethod
from typing import List, Optional

# Local imports
from src.reviews.domain.entities import Review, ReviewResponse, ReviewModeration
from src.reviews.domain.value_objects import ReviewId, ReviewStatus
from src.users.domain.value_objects import UserId


class ReviewRepository(ABC):
    """
    Repository interface for Review entity.
    
    This repository provides methods for managing reviews.
    """

    @abstractmethod
    async def save(self, review: Review) -> Review:
        """
        Save a review.
        
        Args:
            review (Review): The review to save.

        Returns:
            Review: The saved review.
        """
        pass

    @abstractmethod
    async def get_by_id(self, review_id: ReviewId) -> Optional[Review]:
        """
        Get review by ID.
        
        Args:
            review_id (ReviewId): The ID of the review to get.

        Returns:
            Optional[Review]: The review if found, None otherwise.
        """
        pass

    @abstractmethod
    async def get_by_user_id(self, user_id: UserId) -> List[Review]:
        """
        Get reviews by user ID.
        
        Args:
            user_id (UserId): The ID of the user to get reviews for.

        Returns:
            List[Review]: The reviews for the user.
        """
        pass

    @abstractmethod
    async def get_by_product_id(self, product_id: str) -> List[Review]:
        """
        Get reviews by product ID.
        
        Args:
            product_id (str): The ID of the product to get reviews for.

        Returns:
            List[Review]: The reviews for the product.
        """
        pass

    @abstractmethod
    async def get_by_status(self, status: ReviewStatus) -> List[Review]:
        """
        Get reviews by status.
        
        Args:
            status (ReviewStatus): The status of the reviews to get.

        Returns:
            List[Review]: The reviews with the given status.
        """
        pass

    @abstractmethod
    async def get_pending_reviews(self) -> List[Review]:
        """
        Get all pending reviews.
        
        Returns:
            List[Review]: All pending reviews.
        """
        pass

    @abstractmethod
    async def delete(self, review_id: ReviewId) -> None:
        """
        Delete a review.
        
        Args:
            review_id (ReviewId): The ID of the review to delete.
        """
        pass


class ReviewResponseRepository(ABC):
    """
    Repository interface for ReviewResponse entity.
    
    This repository provides methods for managing review responses.
    """

    @abstractmethod
    async def save(self, response: ReviewResponse) -> ReviewResponse:
        """
        Save a review response.
        
        Args:
            response (ReviewResponse): The review response to save.

        Returns:
            ReviewResponse: The saved review response.
        """
        pass

    @abstractmethod
    async def get_by_id(self, response_id: ReviewId) -> Optional[ReviewResponse]:
        """
        Get response by ID.
        
        Args:
            response_id (ReviewId): The ID of the response to get.

        Returns:
            Optional[ReviewResponse]: The response if found, None otherwise.
        """
        pass

    @abstractmethod
    async def get_by_review_id(self, review_id: ReviewId) -> List[ReviewResponse]:
        """
        Get responses by review ID.
        
        Args:
            review_id (ReviewId): The ID of the review to get responses for.

        Returns:
            List[ReviewResponse]: The responses for the review.
        """
        pass

    @abstractmethod
    async def get_by_responder_id(self, responder_id: UserId) -> List[ReviewResponse]:
        """
        Get responses by responder ID.
        
        Args:
            responder_id (UserId): The ID of the responder to get responses for.

        Returns:
            List[ReviewResponse]: The responses for the responder.
        """
        pass

    @abstractmethod
    async def delete(self, response_id: ReviewId) -> None:
        """
        Delete a response.
        
        Args:
            response_id (ReviewId): The ID of the response to delete.
        """
        pass


class ReviewModerationRepository(ABC):
    """
    Repository interface for ReviewModeration entity.
    
    This repository provides methods for managing review moderation.
    """

    @abstractmethod
    async def save(self, moderation: ReviewModeration) -> ReviewModeration:
        """
        Save a moderation record.
        
        Args:
            moderation (ReviewModeration): The moderation record to save.

        Returns:
            ReviewModeration: The saved moderation record.
        """
        pass

    @abstractmethod
    async def get_by_id(self, moderation_id: ReviewId) -> Optional[ReviewModeration]:
        """
        Get moderation by ID.
        
        Args:
            moderation_id (ReviewId): The ID of the moderation to get.

        Returns:
            Optional[ReviewModeration]: The moderation if found, None otherwise.
        """
        pass

    @abstractmethod
    async def get_by_review_id(self, review_id: ReviewId) -> List[ReviewModeration]:
        """
        Get moderation records by review ID.
        
        Args:
            review_id (ReviewId): The ID of the review to get moderation records for.

        Returns:
            List[ReviewModeration]: The moderation records for the review.
        """
        pass

    @abstractmethod
    async def get_by_moderator_id(self, moderator_id: UserId) -> List[ReviewModeration]:
        """
        Get moderation records by moderator ID.
        
        Args:
            moderator_id (UserId): The ID of the moderator to get moderation records for.

        Returns:
            List[ReviewModeration]: The moderation records for the moderator.
        """
        pass

    @abstractmethod
    async def delete(self, moderation_id: ReviewId) -> None:
        """
        Delete a moderation record.
        
        Args:
            moderation_id (ReviewId): The ID of the moderation to delete.
        """
        pass 