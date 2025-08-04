"""Tests for reviews.infrastructure.repositories module."""

import pytest
from unittest.mock import Mock
from src.reviews.infrastructure.repositories import (
    InMemoryReviewRepository,
    InMemoryReviewResponseRepository,
    InMemoryReviewModerationRepository
)
from src.reviews.domain.value_objects import ReviewId, ReviewStatus
from src.users.domain.value_objects import UserId


@pytest.mark.asyncio
class TestInMemoryReviewRepository:
    """Test InMemoryReviewRepository."""

    @pytest.fixture
    def repository(self):
        """Create repository instance."""
        return InMemoryReviewRepository()

    @pytest.fixture
    def sample_review(self):
        """Create sample review."""
        review = Mock()
        review.id = ReviewId("review-123")
        review.user_id = UserId("user-123")
        review.product_id = "product-123"
        review.status = ReviewStatus.PENDING
        return review

    async def test_save_review(self, repository, sample_review):
        """Test saving a review."""
        result = await repository.save(sample_review)
        assert result == sample_review
        assert str(sample_review.id) in repository._reviews

    async def test_get_by_id_existing(self, repository, sample_review):
        """Test getting review by ID when it exists."""
        await repository.save(sample_review)
        result = await repository.get_by_id(sample_review.id)
        assert result == sample_review

    async def test_get_by_id_not_found(self, repository):
        """Test getting review by ID when it doesn't exist."""
        result = await repository.get_by_id(ReviewId("nonexistent"))
        assert result is None

    async def test_get_by_user_id(self, repository, sample_review):
        """Test getting reviews by user ID."""
        await repository.save(sample_review)
        result = await repository.get_by_user_id(sample_review.user_id)
        assert len(result) == 1
        assert result[0] == sample_review

    async def test_get_by_user_id_empty(self, repository):
        """Test getting reviews by user ID when none exist."""
        result = await repository.get_by_user_id(UserId("user-123"))
        assert result == []

    async def test_get_by_product_id(self, repository, sample_review):
        """Test getting reviews by product ID."""
        await repository.save(sample_review)
        result = await repository.get_by_product_id(sample_review.product_id)
        assert len(result) == 1
        assert result[0] == sample_review

    async def test_get_by_product_id_empty(self, repository):
        """Test getting reviews by product ID when none exist."""
        result = await repository.get_by_product_id("product-123")
        assert result == []

    async def test_get_by_status(self, repository, sample_review):
        """Test getting reviews by status."""
        await repository.save(sample_review)
        result = await repository.get_by_status(sample_review.status)
        assert len(result) == 1
        assert result[0] == sample_review

    async def test_get_by_status_empty(self, repository):
        """Test getting reviews by status when none exist."""
        result = await repository.get_by_status(ReviewStatus.APPROVED)
        assert result == []

    async def test_get_pending_reviews(self, repository, sample_review):
        """Test getting pending reviews."""
        await repository.save(sample_review)
        result = await repository.get_pending_reviews()
        assert len(result) == 1
        assert result[0] == sample_review

    async def test_delete_review(self, repository, sample_review):
        """Test deleting a review."""
        await repository.save(sample_review)
        await repository.delete(sample_review.id)
        result = await repository.get_by_id(sample_review.id)
        assert result is None

    async def test_delete_review_not_found(self, repository):
        """Test deleting a review that doesn't exist."""
        # Should not raise an exception
        await repository.delete(ReviewId("nonexistent"))

    async def test_multiple_reviews_same_user(self, repository):
        """Test handling multiple reviews from the same user."""
        review1 = Mock()
        review1.id = ReviewId("review-1")
        review1.user_id = UserId("user-123")
        review1.product_id = "product-123"
        review1.status = ReviewStatus.PENDING

        review2 = Mock()
        review2.id = ReviewId("review-2")
        review2.user_id = UserId("user-123")
        review2.product_id = "product-456"
        review2.status = ReviewStatus.APPROVED

        await repository.save(review1)
        await repository.save(review2)

        user_reviews = await repository.get_by_user_id(UserId("user-123"))
        assert len(user_reviews) == 2

        pending_reviews = await repository.get_by_status(ReviewStatus.PENDING)
        assert len(pending_reviews) == 1
        assert pending_reviews[0] == review1


@pytest.mark.asyncio
class TestInMemoryReviewResponseRepository:
    """Test InMemoryReviewResponseRepository."""

    @pytest.fixture
    def repository(self):
        """Create repository instance."""
        return InMemoryReviewResponseRepository()

    @pytest.fixture
    def sample_response(self):
        """Create sample review response."""
        response = Mock()
        response.id = ReviewId("response-123")
        response.review_id = ReviewId("review-123")
        response.responder_id = UserId("user-456")
        return response

    async def test_save_response(self, repository, sample_response):
        """Test saving a review response."""
        result = await repository.save(sample_response)
        assert result == sample_response
        assert str(sample_response.id) in repository._responses

    async def test_get_by_id_existing(self, repository, sample_response):
        """Test getting response by ID when it exists."""
        await repository.save(sample_response)
        result = await repository.get_by_id(sample_response.id)
        assert result == sample_response

    async def test_get_by_id_not_found(self, repository):
        """Test getting response by ID when it doesn't exist."""
        result = await repository.get_by_id(ReviewId("nonexistent"))
        assert result is None

    async def test_get_by_review_id(self, repository, sample_response):
        """Test getting responses by review ID."""
        await repository.save(sample_response)
        result = await repository.get_by_review_id(sample_response.review_id)
        assert len(result) == 1
        assert result[0] == sample_response

    async def test_get_by_review_id_empty(self, repository):
        """Test getting responses by review ID when none exist."""
        result = await repository.get_by_review_id(ReviewId("review-123"))
        assert result == []

    async def test_get_by_responder_id(self, repository, sample_response):
        """Test getting responses by responder ID."""
        await repository.save(sample_response)
        result = await repository.get_by_responder_id(sample_response.responder_id)
        assert len(result) == 1
        assert result[0] == sample_response

    async def test_get_by_responder_id_empty(self, repository):
        """Test getting responses by responder ID when none exist."""
        result = await repository.get_by_responder_id(UserId("user-123"))
        assert result == []

    async def test_delete_response(self, repository, sample_response):
        """Test deleting a review response."""
        await repository.save(sample_response)
        await repository.delete(sample_response.id)
        result = await repository.get_by_id(sample_response.id)
        assert result is None

    async def test_delete_response_not_found(self, repository):
        """Test deleting a response that doesn't exist."""
        # Should not raise an exception
        await repository.delete(ReviewId("nonexistent"))

    async def test_multiple_responses_same_review(self, repository):
        """Test handling multiple responses for the same review."""
        response1 = Mock()
        response1.id = ReviewId("response-1")
        response1.review_id = ReviewId("review-123")
        response1.responder_id = UserId("user-456")

        response2 = Mock()
        response2.id = ReviewId("response-2")
        response2.review_id = ReviewId("review-123")
        response2.responder_id = UserId("user-789")

        await repository.save(response1)
        await repository.save(response2)

        review_responses = await repository.get_by_review_id(ReviewId("review-123"))
        assert len(review_responses) == 2


@pytest.mark.asyncio
class TestInMemoryReviewModerationRepository:
    """Test InMemoryReviewModerationRepository."""

    @pytest.fixture
    def repository(self):
        """Create repository instance."""
        return InMemoryReviewModerationRepository()

    @pytest.fixture
    def sample_moderation(self):
        """Create sample review moderation."""
        moderation = Mock()
        moderation.id = ReviewId("moderation-123")
        moderation.review_id = ReviewId("review-123")
        moderation.moderator_id = UserId("moderator-456")
        return moderation

    async def test_save_moderation(self, repository, sample_moderation):
        """Test saving a review moderation."""
        result = await repository.save(sample_moderation)
        assert result == sample_moderation
        assert str(sample_moderation.id) in repository._moderations

    async def test_get_by_id_existing(self, repository, sample_moderation):
        """Test getting moderation by ID when it exists."""
        await repository.save(sample_moderation)
        result = await repository.get_by_id(sample_moderation.id)
        assert result == sample_moderation

    async def test_get_by_id_not_found(self, repository):
        """Test getting moderation by ID when it doesn't exist."""
        result = await repository.get_by_id(ReviewId("nonexistent"))
        assert result is None

    async def test_get_by_review_id(self, repository, sample_moderation):
        """Test getting moderations by review ID."""
        await repository.save(sample_moderation)
        result = await repository.get_by_review_id(sample_moderation.review_id)
        assert len(result) == 1
        assert result[0] == sample_moderation

    async def test_get_by_review_id_empty(self, repository):
        """Test getting moderations by review ID when none exist."""
        result = await repository.get_by_review_id(ReviewId("review-123"))
        assert result == []

    async def test_get_by_moderator_id(self, repository, sample_moderation):
        """Test getting moderations by moderator ID."""
        await repository.save(sample_moderation)
        result = await repository.get_by_moderator_id(sample_moderation.moderator_id)
        assert len(result) == 1
        assert result[0] == sample_moderation

    async def test_get_by_moderator_id_empty(self, repository):
        """Test getting moderations by moderator ID when none exist."""
        result = await repository.get_by_moderator_id(UserId("moderator-123"))
        assert result == []

    async def test_delete_moderation(self, repository, sample_moderation):
        """Test deleting a review moderation."""
        await repository.save(sample_moderation)
        await repository.delete(sample_moderation.id)
        result = await repository.get_by_id(sample_moderation.id)
        assert result is None

    async def test_delete_moderation_not_found(self, repository):
        """Test deleting a moderation that doesn't exist."""
        # Should not raise an exception
        await repository.delete(ReviewId("nonexistent"))

    async def test_multiple_moderations_same_review(self, repository):
        """Test handling multiple moderations for the same review."""
        moderation1 = Mock()
        moderation1.id = ReviewId("moderation-1")
        moderation1.review_id = ReviewId("review-123")
        moderation1.moderator_id = UserId("moderator-456")

        moderation2 = Mock()
        moderation2.id = ReviewId("moderation-2")
        moderation2.review_id = ReviewId("review-123")
        moderation2.moderator_id = UserId("moderator-789")

        await repository.save(moderation1)
        await repository.save(moderation2)

        review_moderations = await repository.get_by_review_id(ReviewId("review-123"))
        assert len(review_moderations) == 2 