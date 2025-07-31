"""Queries for reviews domain."""

# Python imports
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

# Local imports
from src.reviews.domain.value_objects import ReviewId, ReviewStatus, ReviewType
from src.users.domain.value_objects import UserId


# Read Models
class ReviewReadModel(BaseModel):
    """
    Read model for Review.
    
    This model represents a review of a product.
    
    Attributes:
        id (str): The ID of the review.
        user_id (str): The ID of the user who wrote the review.
        review_type (str): The type of the review.
        title (str): The title of the review.
        content (str): The content of the review.
        rating (int): The rating of the review.
        product_id (Optional[str]): The ID of the product being reviewed.
        seller_id (Optional[str]): The ID of the seller being reviewed.
        order_id (Optional[str]): The ID of the order being reviewed.
        status (str): The status of the review.
        helpful_votes (int): The number of helpful votes for the review.
        is_verified_purchase (bool): Whether the purchase was verified.
        created_at (datetime): The date and time the review was created.
        updated_at (Optional[datetime]): The date and time the review was last updated.
        moderator_notes (Optional[str]): The notes from the moderator.
    """
    
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
    """
    Read model for ReviewResponse.
    
    This model represents a response to a review.
    
    Attributes:
        id (str): The ID of the response.
        review_id (str): The ID of the review being responded to.
        responder_id (str): The ID of the user who responded to the review.
        content (str): The content of the response.
        is_public (bool): Whether the response is public.
        created_at (datetime): The date and time the response was created.
        updated_at (Optional[datetime]): The date and time the response was last updated.
    """
    
    id: str
    review_id: str
    responder_id: str
    content: str
    is_public: bool
    created_at: datetime
    updated_at: Optional[datetime] = None


class ReviewModerationReadModel(BaseModel):
    """
    Read model for ReviewModeration.
    
    This model represents a moderation action on a review.
    
    Attributes:
        id (str): The ID of the moderation.
        review_id (str): The ID of the review being moderated.
        moderator_id (str): The ID of the user who moderated the review.
        action (str): The action taken on the review.
        reason (Optional[str]): The reason for the moderation action.
        created_at (datetime): The date and time the moderation action was taken.
        notes (Optional[str]): Additional notes from the moderator.
    """
    
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
    """
    Query to get a review by ID.
    
    This query retrieves a review by its ID.
    
    Attributes:
        review_id (str): The ID of the review to retrieve.
    """

    review_id: str


@dataclass
class GetReviewsByUserQuery:
    """
    Query to get reviews by user ID.
    
    This query retrieves reviews by a specific user.
    
    Attributes:
        user_id (str): The ID of the user to retrieve reviews for.
        status (Optional[ReviewStatus]): The status of the reviews to retrieve.
        limit (int): The maximum number of reviews to retrieve.
        offset (int): The number of reviews to skip.
    """

    user_id: str
    status: Optional[ReviewStatus] = None
    limit: int = 50
    offset: int = 0


@dataclass
class GetReviewsByProductQuery:
    """
    Query to get reviews by product ID.
    
    This query retrieves reviews by a specific product.
    
    Attributes:
        product_id (str): The ID of the product to retrieve reviews for.
        status (ReviewStatus): The status of the reviews to retrieve.
        limit (int): The maximum number of reviews to retrieve.
        offset (int): The number of reviews to skip.
    """

    product_id: str
    status: ReviewStatus = ReviewStatus.APPROVED
    limit: int = 50
    offset: int = 0


@dataclass
class GetReviewsByStatusQuery:
    """
    Query to get reviews by status.
    
    This query retrieves reviews by a specific status.
    
    Attributes:
        status (ReviewStatus): The status of the reviews to retrieve.
        limit (int): The maximum number of reviews to retrieve.
        offset (int): The number of reviews to skip.
    """

    status: ReviewStatus
    limit: int = 50
    offset: int = 0


@dataclass
class SearchReviewsQuery:
    """
    Query to search reviews.
    
    This query searches for reviews based on various criteria.
    
    Attributes:
        query (str): The search query.
        review_type (Optional[ReviewType]): The type of review to search for.
        status (ReviewStatus): The status of the reviews to search for.
        min_rating (Optional[int]): The minimum rating to search for.
        max_rating (Optional[int]): The maximum rating to search for.
        limit (int): The maximum number of reviews to retrieve.
        offset (int): The number of reviews to skip.
    """
    query: str
    review_type: Optional[ReviewType] = None
    status: ReviewStatus = ReviewStatus.APPROVED
    min_rating: Optional[int] = None
    max_rating: Optional[int] = None
    limit: int = 50
    offset: int = 0


@dataclass
class GetReviewResponsesQuery:
    """Query to get responses for a review.
    
    This query retrieves responses for a specific review.
    
    Attributes:
        review_id (str): The ID of the review to retrieve responses for.
        limit (int): The maximum number of responses to retrieve.
        offset (int): The number of responses to skip.
    """

    review_id: str
    limit: int = 50
    offset: int = 0


@dataclass
class GetReviewModerationHistoryQuery:
    """Query to get moderation history for a review.
    
    This query retrieves the moderation history for a specific review.
    
    Attributes:
        review_id (str): The ID of the review to retrieve moderation history for.
        limit (int): The maximum number of moderations to retrieve.
        offset (int): The number of moderations to skip.
    """

    review_id: str
    limit: int = 50
    offset: int = 0


# Query Handlers
class ReviewQueryHandler(ABC):
    """
    Abstract query handler for reviews.
    
    This handler provides methods for retrieving reviews and related information.
    """

    @abstractmethod
    async def get_review(self, query: GetReviewQuery) -> Optional[ReviewReadModel]:
        """
        Get review by ID.
        
        Args:
            query (GetReviewQuery): The query to get a review by ID.

        Returns:
            Optional[ReviewReadModel]: The review if found, None otherwise.
        """
        pass

    @abstractmethod
    async def get_reviews_by_user(self, query: GetReviewsByUserQuery) -> List[ReviewReadModel]:
        """
        Get reviews by user ID.
        
        Args:
            query (GetReviewsByUserQuery): The query to get reviews by user ID.

        Returns:
            List[ReviewReadModel]: The reviews for the user.
        """
        pass

    @abstractmethod
    async def get_reviews_by_product(self, query: GetReviewsByProductQuery) -> List[ReviewReadModel]:
        """
        Get reviews by product ID.
        
        Args:
            query (GetReviewsByProductQuery): The query to get reviews by product ID.

        Returns:
            List[ReviewReadModel]: The reviews for the product.
        """
        pass

    @abstractmethod
    async def get_reviews_by_status(self, query: GetReviewsByStatusQuery) -> List[ReviewReadModel]:
        """
        Get reviews by status.
        
        Args:
            query (GetReviewsByStatusQuery): The query to get reviews by status.

        Returns:
            List[ReviewReadModel]: The reviews with the given status.
        """
        pass

    @abstractmethod
    async def search_reviews(self, query: SearchReviewsQuery) -> List[ReviewReadModel]:
        """
        Search reviews.
        
        Args:
            query (SearchReviewsQuery): The query to search reviews.

        Returns:
            List[ReviewReadModel]: The reviews matching the search criteria.
        """
        pass

    @abstractmethod
    async def get_review_responses(self, query: GetReviewResponsesQuery) -> List[ReviewResponseReadModel]:
        """
        Get responses for a review.
        
        Args:
            query (GetReviewResponsesQuery): The query to get responses for a review.

        Returns:
            List[ReviewResponseReadModel]: The responses for the review.
        """
        pass

    @abstractmethod
    async def get_review_moderation_history(self, query: GetReviewModerationHistoryQuery) -> List[ReviewModerationReadModel]:
        """
        Get moderation history for a review.
        
        Args:
            query (GetReviewModerationHistoryQuery): The query to get moderation history for a review.

        Returns:
            List[ReviewModerationReadModel]: The moderation history for the review.
        """
        pass


class ReviewResponseQueryHandler(ABC):
    """
    Abstract query handler for review responses.
    
    This handler provides methods for retrieving review responses.
    """

    @abstractmethod
    async def get_response_by_id(self, response_id: str) -> Optional[ReviewResponseReadModel]:
        """Get response by ID.
        
        Args:
            response_id (str): The ID of the response to retrieve.

        Returns:
            Optional[ReviewResponseReadModel]: The response if found, None otherwise.
        """
        pass

    @abstractmethod
    async def get_responses_by_responder(self, responder_id: str, limit: int = 50, offset: int = 0) -> List[ReviewResponseReadModel]:
        """
        Get responses by responder ID.
        
        Args:
            responder_id (str): The ID of the responder.
            limit (int): The maximum number of responses to retrieve.
            offset (int): The number of responses to skip.

        Returns:
            List[ReviewResponseReadModel]: The responses for the responder.
        """
        pass


class ReviewModerationQueryHandler(ABC):
    """
    Abstract query handler for review moderation.
    
    This handler provides methods for retrieving review moderation information.
    """

    @abstractmethod
    async def get_moderation_by_id(self, moderation_id: str) -> Optional[ReviewModerationReadModel]:
        """Get moderation by ID.
        
        Args:
            moderation_id (str): The ID of the moderation to retrieve.

        Returns:
            Optional[ReviewModerationReadModel]: The moderation if found, None otherwise.
        """
        pass

    @abstractmethod
    async def get_moderations_by_moderator(self, moderator_id: str, limit: int = 50, offset: int = 0) -> List[ReviewModerationReadModel]:
        """
        Get moderations by moderator ID.
        
        Args:
            moderator_id (str): The ID of the moderator.
            limit (int): The maximum number of moderations to retrieve.
            offset (int): The number of moderations to skip.

        Returns:
            List[ReviewModerationReadModel]: The moderations for the moderator.
        """
        pass 