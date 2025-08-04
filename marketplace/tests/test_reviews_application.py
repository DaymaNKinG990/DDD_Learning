"""Tests for reviews application services."""

import pytest
from unittest.mock import AsyncMock, Mock

from src.reviews.application.services import ReviewService
from src.reviews.domain.entities import Review, ReviewResponse, ReviewModeration
from src.reviews.domain.value_objects import (
    ReviewId, ReviewStatus, ReviewType, ReviewTitle, ReviewContent, Rating
)
from src.catalog.domain.value_objects import ProductId
from src.users.domain.value_objects import UserId


class TestReviewService:
    """Test ReviewService."""

    @pytest.fixture
    def review_repository(self):
        """Create mock review repository."""
        return AsyncMock()

    @pytest.fixture
    def review_response_repository(self):
        """Create mock review response repository."""
        return AsyncMock()

    @pytest.fixture
    def review_moderation_repository(self):
        """Create mock review moderation repository."""
        return AsyncMock()

    @pytest.fixture
    def event_handler(self):
        """Create mock event handler."""
        mock_handler = AsyncMock()
        # Mock the handle method to avoid domain event instantiation issues
        mock_handler.handle = AsyncMock(side_effect=lambda event: None)
        return mock_handler

    @pytest.fixture
    def service(self, review_repository, review_response_repository, review_moderation_repository, event_handler):
        """Create review service."""
        return ReviewService(
            review_repository,
            review_response_repository,
            review_moderation_repository,
            event_handler
        )

    @pytest.fixture
    def sample_review(self):
        """Create sample review."""
        return Review(
            id=ReviewId(value="review_123"),
            user_id=UserId(value="user_123"),
            review_type=ReviewType.PRODUCT,
            title=ReviewTitle(value="Great Product"),
            content=ReviewContent(value="This product is amazing!"),
            rating=Rating(value=5),
            product_id=ProductId(value="product_123"),
        )



    @pytest.mark.asyncio
    async def test_create_review_without_event_handler(self, review_repository, review_response_repository, review_moderation_repository):
        """Test creating a review without event handler."""
        # Arrange
        service = ReviewService(
            review_repository,
            review_response_repository,
            review_moderation_repository,
            None
        )
        
        user_id = "user_123"
        review_type = "product"
        title = "Great Product"
        content = "This product is amazing!"
        rating = 5
        product_id = "product_123"
        
        expected_review = Review(
            id=ReviewId(value="review_123"),
            user_id=UserId(value=user_id),
            review_type=ReviewType(review_type),
            title=ReviewTitle(value=title),
            content=ReviewContent(value=content),
            rating=Rating(value=rating),
            product_id=ProductId(value=product_id),
        )
        review_repository.save.return_value = expected_review

        # Act
        result = await service.create_review(user_id, review_type, title, content, rating, product_id)

        # Assert
        assert result == expected_review
        review_repository.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_approve_review_without_event_handler(self, review_repository, review_response_repository, review_moderation_repository, sample_review):
        """Test approving a review without event handler."""
        # Arrange
        service = ReviewService(
            review_repository,
            review_response_repository,
            review_moderation_repository,
            None
        )
        
        review_id = "review_123"
        moderator_id = "moderator_123"
        notes = "Approved after review"
        
        review_repository.get_by_id.return_value = sample_review
        review_repository.save.return_value = sample_review
        review_moderation_repository.save.return_value = None

        # Act
        result = await service.approve_review(review_id, moderator_id, notes)

        # Assert
        assert result == sample_review
        assert sample_review.status == ReviewStatus.APPROVED
        review_repository.save.assert_called_once()
        review_moderation_repository.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_reject_review_without_event_handler(self, review_repository, review_response_repository, review_moderation_repository, sample_review):
        """Test rejecting a review without event handler."""
        # Arrange
        service = ReviewService(
            review_repository,
            review_response_repository,
            review_moderation_repository,
            None
        )
        
        review_id = "review_123"
        moderator_id = "moderator_123"
        reason = "Inappropriate content"
        notes = "Contains offensive language"
        
        review_repository.get_by_id.return_value = sample_review
        review_repository.save.return_value = sample_review
        review_moderation_repository.save.return_value = None

        # Act
        result = await service.reject_review(review_id, moderator_id, reason, notes)

        # Assert
        assert result == sample_review
        assert sample_review.status == ReviewStatus.REJECTED
        review_repository.save.assert_called_once()
        review_moderation_repository.save.assert_called_once()



    @pytest.mark.asyncio
    async def test_approve_review_not_found(self, service, review_repository):
        """Test approving a review that doesn't exist."""
        # Arrange
        review_id = "review_999"
        moderator_id = "moderator_123"
        review_repository.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(ValueError, match=f"Review with ID {review_id} not found"):
            await service.approve_review(review_id, moderator_id)



    @pytest.mark.asyncio
    async def test_reject_review_not_found(self, service, review_repository):
        """Test rejecting a review that doesn't exist."""
        # Arrange
        review_id = "review_999"
        moderator_id = "moderator_123"
        reason = "Inappropriate content"
        review_repository.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(ValueError, match=f"Review with ID {review_id} not found"):
            await service.reject_review(review_id, moderator_id, reason)

    @pytest.mark.asyncio
    async def test_add_response(self, service, review_repository, review_response_repository, sample_review):
        """Test adding a response to a review."""
        # Arrange
        review_id = "review_123"
        responder_id = "seller_123"
        content = "Thank you for your feedback!"
        is_public = True
        
        expected_response = ReviewResponse(
            id=ReviewId(value="response_123"),
            review_id=sample_review.id,
            responder_id=UserId(value=responder_id),
            content=ReviewContent(value=content),
            is_public=is_public,
        )
        
        review_repository.get_by_id.return_value = sample_review
        review_response_repository.save.return_value = expected_response

        # Act
        result = await service.add_response(review_id, responder_id, content, is_public)

        # Assert
        assert result == expected_response
        review_response_repository.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_add_response_review_not_found(self, service, review_repository):
        """Test adding a response to a review that doesn't exist."""
        # Arrange
        review_id = "review_999"
        responder_id = "seller_123"
        content = "Thank you for your feedback!"
        review_repository.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(ValueError, match=f"Review with ID {review_id} not found"):
            await service.add_response(review_id, responder_id, content)

    @pytest.mark.asyncio
    async def test_mark_review_helpful(self, service, review_repository, sample_review):
        """Test marking a review as helpful."""
        # Arrange
        review_id = "review_123"
        review_repository.get_by_id.return_value = sample_review
        review_repository.save.return_value = sample_review

        # Act
        result = await service.mark_review_helpful(review_id)

        # Assert
        assert result == sample_review
        assert sample_review.helpful_votes.value == 1
        review_repository.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_mark_review_helpful_not_found(self, service, review_repository):
        """Test marking a review as helpful that doesn't exist."""
        # Arrange
        review_id = "review_999"
        review_repository.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(ValueError, match=f"Review with ID {review_id} not found"):
            await service.mark_review_helpful(review_id)

    @pytest.mark.asyncio
    async def test_update_review(self, service, review_repository, sample_review):
        """Test updating a review."""
        # Arrange
        review_id = "review_123"
        new_title = "Updated Title"
        new_content = "Updated content"
        new_rating = 4
        
        review_repository.get_by_id.return_value = sample_review
        review_repository.save.return_value = sample_review

        # Act
        result = await service.update_review(review_id, new_title, new_content, new_rating)

        # Assert
        assert result == sample_review
        assert sample_review.title.value == new_title
        assert sample_review.content.value == new_content
        assert sample_review.rating.value == new_rating
        review_repository.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_review_not_found(self, service, review_repository):
        """Test updating a review that doesn't exist."""
        # Arrange
        review_id = "review_999"
        new_title = "Updated Title"
        new_content = "Updated content"
        new_rating = 4
        review_repository.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(ValueError, match=f"Review with ID {review_id} not found"):
            await service.update_review(review_id, new_title, new_content, new_rating) 