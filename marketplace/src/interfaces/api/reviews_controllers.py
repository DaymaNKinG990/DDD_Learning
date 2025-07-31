"""Reviews API controllers."""

# Python imports
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

# Local imports
from src.reviews.application.services import ReviewService
from src.reviews.infrastructure.repositories import (
    InMemoryReviewRepository,
    InMemoryReviewResponseRepository,
    InMemoryReviewModerationRepository,
)


# Pydantic models for API
class CreateReviewRequest(BaseModel):
    """
    Request model for creating a review.

    Attributes:
        user_id (str): The ID of the user.
        review_type (str): The type of review.
        title (str): The title of the review.
        content (str): The content of the review.
        rating (int): The rating of the review.
        product_id (Optional[str]): The ID of the product.
        seller_id (Optional[str]): The ID of the seller.
        order_id (Optional[str]): The ID of the order.
    """

    user_id: str
    review_type: str  # "product" or "seller"
    title: str
    content: str
    rating: int
    product_id: Optional[str] = None
    seller_id: Optional[str] = None
    order_id: Optional[str] = None


class ReviewResponse(BaseModel):
    """
    Response model for review data.

    Attributes:
        id (str): The ID of the review.
        user_id (str): The ID of the user.
        review_type (str): The type of review.
        title (str): The title of the review.
        content (str): The content of the review.
        rating (int): The rating of the review.
        product_id (Optional[str]): The ID of the product.
        seller_id (Optional[str]): The ID of the seller.
        order_id (Optional[str]): The ID of the order.
        status (str): The status of the review.
        helpful_count (int): The number of helpful reviews.
        created_at (str): The creation date and time of the review.
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
    helpful_count: int
    created_at: str


class ApproveReviewRequest(BaseModel):
    """
    Request model for approving a review.

    Attributes:
        moderator_id (str): The ID of the moderator.
        reason (Optional[str]): The reason for approving the review.
    """

    moderator_id: str
    reason: Optional[str] = None


class RejectReviewRequest(BaseModel):
    """
    Request model for rejecting a review.

    Attributes:
        moderator_id (str): The ID of the moderator.
        reason (str): The reason for rejecting the review.
    """

    moderator_id: str
    reason: str


class AddResponseRequest(BaseModel):
    """
    Request model for adding a response to a review.

    Attributes:
        responder_id (str): The ID of the responder.
        content (str): The content of the response.
    """

    responder_id: str
    content: str


class MarkHelpfulRequest(BaseModel):
    """
    Request model for marking a review as helpful.

    Attributes:
        user_id (str): The ID of the user.
    """

    user_id: str


# Dependency injection
def get_review_service() -> ReviewService:
    """
    Get review service instance.

    Returns:
        ReviewService: The review service instance.
    """

    review_repo = InMemoryReviewRepository()
    response_repo = InMemoryReviewResponseRepository()
    moderation_repo = InMemoryReviewModerationRepository()
    return ReviewService(review_repo, response_repo, moderation_repo)


# Router
router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.post("/", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
async def create_review(
    request: CreateReviewRequest,
    service: ReviewService = Depends(get_review_service)
) -> ReviewResponse:
    """
    Create a new review.

    Args:
        request (CreateReviewRequest): The request object containing review details.
        service (ReviewService): The review service instance.

    Returns:
        ReviewResponse: The response object containing review details.
    """

    try:
        review = await service.create_review(
            user_id=request.user_id,
            review_type=request.review_type,
            title=request.title,
            content=request.content,
            rating=request.rating,
            product_id=request.product_id,
            seller_id=request.seller_id,
            order_id=request.order_id,
        )
        
        return ReviewResponse(
            id=review.id.value,
            user_id=review.user_id.value,
            review_type=review.review_type.value,
            title=review.title.value,
            content=review.content.value,
            rating=review.rating.value,
            product_id=review.product_id.value if review.product_id else None,
            seller_id=review.seller_id,
            order_id=review.order_id,
            status=review.status.value,
            helpful_count=review.helpful_count,
            created_at=review.created_at.isoformat(),
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{review_id}", response_model=ReviewResponse)
async def get_review(
    review_id: str,
    service: ReviewService = Depends(get_review_service)
) -> ReviewResponse:
    """
    Get a review by ID.

    Args:
        review_id (str): The ID of the review.
        service (ReviewService): The review service instance.

    Returns:
        ReviewResponse: The response object containing review details.
    """

    try:
        review = await service.get_review(review_id)
        return ReviewResponse(
            id=review.id.value,
            user_id=review.user_id.value,
            review_type=review.review_type.value,
            title=review.title.value,
            content=review.content.value,
            rating=review.rating.value,
            product_id=review.product_id.value if review.product_id else None,
            seller_id=review.seller_id,
            order_id=review.order_id,
            status=review.status.value,
            helpful_count=review.helpful_count,
            created_at=review.created_at.isoformat(),
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.post("/{review_id}/approve", response_model=ReviewResponse)
async def approve_review(
    review_id: str,
    request: ApproveReviewRequest,
    service: ReviewService = Depends(get_review_service)
) -> ReviewResponse:
    """
    Approve a review.

    Args:
        review_id (str): The ID of the review.
        request (ApproveReviewRequest): The request object containing approval details.
        service (ReviewService): The review service instance.

    Returns:
        ReviewResponse: The response object containing review details.
    """
    try:
        review = await service.approve_review(
            review_id=review_id,
            moderator_id=request.moderator_id,
            reason=request.reason,
        )
        return ReviewResponse(
            id=review.id.value,
            user_id=review.user_id.value,
            review_type=review.review_type.value,
            title=review.title.value,
            content=review.content.value,
            rating=review.rating.value,
            product_id=review.product_id.value if review.product_id else None,
            seller_id=review.seller_id,
            order_id=review.order_id,
            status=review.status.value,
            helpful_count=review.helpful_count,
            created_at=review.created_at.isoformat(),
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{review_id}/reject", response_model=ReviewResponse)
async def reject_review(
    review_id: str,
    request: RejectReviewRequest,
    service: ReviewService = Depends(get_review_service)
) -> ReviewResponse:
    """
    Reject a review.

    Args:
        review_id (str): The ID of the review.
        request (RejectReviewRequest): The request object containing rejection details.
        service (ReviewService): The review service instance.

    Returns:
        ReviewResponse: The response object containing review details.
    """
    try:
        review = await service.reject_review(
            review_id=review_id,
            moderator_id=request.moderator_id,
            reason=request.reason,
        )
        return ReviewResponse(
            id=review.id.value,
            user_id=review.user_id.value,
            review_type=review.review_type.value,
            title=review.title.value,
            content=review.content.value,
            rating=review.rating.value,
            product_id=review.product_id.value if review.product_id else None,
            seller_id=review.seller_id,
            order_id=review.order_id,
            status=review.status.value,
            helpful_count=review.helpful_count,
            created_at=review.created_at.isoformat(),
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{review_id}/response")
async def add_response(
    review_id: str,
    request: AddResponseRequest,
    service: ReviewService = Depends(get_review_service)
) -> dict[str, str]:
    """
    Add a response to a review.

    Args:
        review_id (str): The ID of the review.
        request (AddResponseRequest): The request object containing response details.
        service (ReviewService): The review service instance.

    Returns:
        dict[str, str]: The response object containing response details.
    """
    try:
        response = await service.add_response(
            review_id=review_id,
            responder_id=request.responder_id,
            content=request.content,
        )
        return {
            "id": response.id.value,
            "review_id": response.review_id.value,
            "responder_id": response.responder_id,
            "content": response.content.value,
            "created_at": response.created_at.isoformat(),
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{review_id}/helpful")
async def mark_review_helpful(
    review_id: str,
    request: MarkHelpfulRequest,
    service: ReviewService = Depends(get_review_service)
) -> dict[str, str]:
    """
    Mark a review as helpful.

    Args:
        review_id (str): The ID of the review.
        request (MarkHelpfulRequest): The request object containing helpful details.
        service (ReviewService): The review service instance.

    Returns:
        dict[str, str]: The response object containing helpful details.
    """
    try:
        review = await service.mark_review_helpful(
            review_id=review_id,
            user_id=request.user_id,
        )
        return {
            "review_id": review.id.value,
            "helpful_count": review.helpful_count,
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/product/{product_id}", response_model=List[ReviewResponse])
async def get_product_reviews(
    product_id: str,
    service: ReviewService = Depends(get_review_service)
) -> List[ReviewResponse]:
    """
    Get all reviews for a product.

    Args:
        product_id (str): The ID of the product.
        service (ReviewService): The review service instance.

    Returns:
        List[ReviewResponse]: The response object containing review details.
    """

    try:
        reviews = await service.get_product_reviews(product_id)
        return [
            ReviewResponse(
                id=review.id.value,
                user_id=review.user_id.value,
                review_type=review.review_type.value,
                title=review.title.value,
                content=review.content.value,
                rating=review.rating.value,
                product_id=review.product_id.value if review.product_id else None,
                seller_id=review.seller_id,
                order_id=review.order_id,
                status=review.status.value,
                helpful_count=review.helpful_count,
                created_at=review.created_at.isoformat(),
            )
            for review in reviews
        ]
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/seller/{seller_id}", response_model=List[ReviewResponse])
async def get_seller_reviews(
    seller_id: str,
    service: ReviewService = Depends(get_review_service)
) -> List[ReviewResponse]:
    """
    Get all reviews for a seller.

    Args:
        seller_id (str): The ID of the seller.
        service (ReviewService): The review service instance.

    Returns:
        List[ReviewResponse]: The response object containing review details.
    """

    try:
        reviews = await service.get_seller_reviews(seller_id)
        return [
            ReviewResponse(
                id=review.id.value,
                user_id=review.user_id.value,
                review_type=review.review_type.value,
                title=review.title.value,
                content=review.content.value,
                rating=review.rating.value,
                product_id=review.product_id.value if review.product_id else None,
                seller_id=review.seller_id,
                order_id=review.order_id,
                status=review.status.value,
                helpful_count=review.helpful_count,
                created_at=review.created_at.isoformat(),
            )
            for review in reviews
        ]
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        ) 