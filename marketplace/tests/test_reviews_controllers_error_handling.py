"""Tests for error handling in reviews controllers."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import HTTPException
from fastapi.testclient import TestClient

from src.interfaces.api.reviews_controllers import (
    router,
    get_review_service,
    CreateReviewRequest,
    UpdateReviewRequest,
)
from src.reviews.application.services import ReviewService
from src.reviews.domain.exceptions import (
    ReviewNotFoundError,
    ReviewAlreadyExistsError,
    InvalidReviewDataError,
    UnauthorizedReviewError,
)
from src.shared.domain.exceptions import EntityNotFoundError, InvalidOperationError


class TestReviewsControllersErrorHandling:
    """Test error handling scenarios in reviews controllers."""

    @pytest.fixture
    def mock_review_service(self):
        """Create a mock review service."""
        service = AsyncMock(spec=ReviewService)
        return service

    @pytest.fixture
    def client(self, mock_review_service):
        """Create test client with mocked service."""
        from fastapi import FastAPI
        app = FastAPI()
        app.include_router(router)
        
        # Override dependency
        app.dependency_overrides[get_review_service] = lambda: mock_review_service
        
        return TestClient(app)

    async def test_create_review_invalid_data(self, client, mock_review_service):
        """Test creating review with invalid data."""
        # Arrange
        mock_review_service.create_review.side_effect = ValueError("Invalid review data")
        
        request_data = {
            "product_id": "",
            "user_id": "",
            "rating": 0,
            "comment": ""
        }
        
        # Act & Assert
        response = client.post("/reviews", json=request_data)
        assert response.status_code == 400
        assert "Invalid review data" in response.json()["detail"]

    async def test_create_review_duplicate_review(self, client, mock_review_service):
        """Test creating duplicate review."""
        # Arrange
        mock_review_service.create_review.side_effect = ReviewAlreadyExistsError("User has already reviewed this product")
        
        request_data = {
            "product_id": "test_product",
            "user_id": "test_user",
            "rating": 5,
            "comment": "Great product!"
        }
        
        # Act & Assert
        response = client.post("/reviews", json=request_data)
        assert response.status_code == 409
        assert "User has already reviewed this product" in response.json()["detail"]

    async def test_create_review_invalid_rating(self, client, mock_review_service):
        """Test creating review with invalid rating."""
        # Arrange
        mock_review_service.create_review.side_effect = ValueError("Rating must be between 1 and 5")
        
        request_data = {
            "product_id": "test_product",
            "user_id": "test_user",
            "rating": 6,
            "comment": "Great product!"
        }
        
        # Act & Assert
        response = client.post("/reviews", json=request_data)
        assert response.status_code == 400
        assert "Rating must be between 1 and 5" in response.json()["detail"]

    async def test_get_review_not_found(self, client, mock_review_service):
        """Test getting non-existent review."""
        # Arrange
        mock_review_service.get_review_by_id.side_effect = ReviewNotFoundError("Review not found")
        
        # Act & Assert
        response = client.get("/reviews/non_existent_review")
        assert response.status_code == 404
        assert "Review not found" in response.json()["detail"]

    async def test_get_review_invalid_id(self, client, mock_review_service):
        """Test getting review with invalid ID."""
        # Arrange
        mock_review_service.get_review_by_id.side_effect = ValueError("Invalid review ID format")
        
        # Act & Assert
        response = client.get("/reviews/invalid_id")
        assert response.status_code == 400
        assert "Invalid review ID format" in response.json()["detail"]

    async def test_update_review_not_found(self, client, mock_review_service):
        """Test updating non-existent review."""
        # Arrange
        mock_review_service.update_review.side_effect = ReviewNotFoundError("Review not found")
        
        request_data = {
            "rating": 4,
            "comment": "Updated comment"
        }
        
        # Act & Assert
        response = client.put("/reviews/non_existent_review", json=request_data)
        assert response.status_code == 404
        assert "Review not found" in response.json()["detail"]

    async def test_update_review_unauthorized(self, client, mock_review_service):
        """Test updating review by unauthorized user."""
        # Arrange
        mock_review_service.update_review.side_effect = UnauthorizedReviewError("You can only update your own reviews")
        
        request_data = {
            "rating": 4,
            "comment": "Updated comment"
        }
        
        # Act & Assert
        response = client.put("/reviews/test_review", json=request_data)
        assert response.status_code == 403
        assert "You can only update your own reviews" in response.json()["detail"]

    async def test_update_review_invalid_data(self, client, mock_review_service):
        """Test updating review with invalid data."""
        # Arrange
        mock_review_service.update_review.side_effect = ValueError("Invalid review data")
        
        request_data = {
            "rating": 0,
            "comment": ""
        }
        
        # Act & Assert
        response = client.put("/reviews/test_review", json=request_data)
        assert response.status_code == 400
        assert "Invalid review data" in response.json()["detail"]

    async def test_delete_review_not_found(self, client, mock_review_service):
        """Test deleting non-existent review."""
        # Arrange
        mock_review_service.delete_review.side_effect = ReviewNotFoundError("Review not found")
        
        # Act & Assert
        response = client.delete("/reviews/non_existent_review")
        assert response.status_code == 404
        assert "Review not found" in response.json()["detail"]

    async def test_delete_review_unauthorized(self, client, mock_review_service):
        """Test deleting review by unauthorized user."""
        # Arrange
        mock_review_service.delete_review.side_effect = UnauthorizedReviewError("You can only delete your own reviews")
        
        # Act & Assert
        response = client.delete("/reviews/test_review")
        assert response.status_code == 403
        assert "You can only delete your own reviews" in response.json()["detail"]

    async def test_get_product_reviews_not_found(self, client, mock_review_service):
        """Test getting reviews for non-existent product."""
        # Arrange
        mock_review_service.get_reviews_by_product.return_value = []
        
        # Act & Assert
        response = client.get("/reviews/product/non_existent_product")
        assert response.status_code == 200
        assert response.json() == []

    async def test_get_product_reviews_invalid_product_id(self, client, mock_review_service):
        """Test getting reviews with invalid product ID."""
        # Arrange
        mock_review_service.get_reviews_by_product.side_effect = ValueError("Invalid product ID")
        
        # Act & Assert
        response = client.get("/reviews/product/invalid_product_id")
        assert response.status_code == 400
        assert "Invalid product ID" in response.json()["detail"]

    async def test_get_user_reviews_not_found(self, client, mock_review_service):
        """Test getting reviews for non-existent user."""
        # Arrange
        mock_review_service.get_reviews_by_user.return_value = []
        
        # Act & Assert
        response = client.get("/reviews/user/non_existent_user")
        assert response.status_code == 200
        assert response.json() == []

    async def test_get_user_reviews_invalid_user_id(self, client, mock_review_service):
        """Test getting reviews with invalid user ID."""
        # Arrange
        mock_review_service.get_reviews_by_user.side_effect = ValueError("Invalid user ID")
        
        # Act & Assert
        response = client.get("/reviews/user/invalid_user_id")
        assert response.status_code == 400
        assert "Invalid user ID" in response.json()["detail"]

    async def test_get_reviews_by_rating_invalid_rating(self, client, mock_review_service):
        """Test getting reviews with invalid rating."""
        # Arrange
        mock_review_service.get_reviews_by_rating.side_effect = ValueError("Invalid rating value")
        
        # Act & Assert
        response = client.get("/reviews/rating/6")
        assert response.status_code == 400
        assert "Invalid rating value" in response.json()["detail"]

    async def test_get_reviews_by_rating_empty_result(self, client, mock_review_service):
        """Test getting reviews by rating with no results."""
        # Arrange
        mock_review_service.get_reviews_by_rating.return_value = []
        
        # Act & Assert
        response = client.get("/reviews/rating/5")
        assert response.status_code == 200
        assert response.json() == []

    async def test_get_reviews_paginated_invalid_pagination(self, client, mock_review_service):
        """Test getting paginated reviews with invalid pagination."""
        # Arrange
        mock_review_service.get_reviews_paginated.side_effect = ValueError("Invalid pagination parameters")
        
        # Act & Assert
        response = client.get("/reviews?page=-1&size=0")
        assert response.status_code == 400
        assert "Invalid pagination parameters" in response.json()["detail"]

    async def test_get_reviews_paginated_empty_result(self, client, mock_review_service):
        """Test getting paginated reviews with no results."""
        # Arrange
        mock_review_service.get_reviews_paginated.return_value = []
        
        # Act & Assert
        response = client.get("/reviews?page=1&size=10")
        assert response.status_code == 200
        assert response.json() == []

    async def test_search_reviews_invalid_query(self, client, mock_review_service):
        """Test searching reviews with invalid query."""
        # Arrange
        mock_review_service.search_reviews.side_effect = ValueError("Search query is too short")
        
        # Act & Assert
        response = client.get("/reviews/search?q=a")
        assert response.status_code == 400
        assert "Search query is too short" in response.json()["detail"]

    async def test_search_reviews_empty_result(self, client, mock_review_service):
        """Test searching reviews with no results."""
        # Arrange
        mock_review_service.search_reviews.return_value = []
        
        # Act & Assert
        response = client.get("/reviews/search?q=nonexistent")
        assert response.status_code == 200
        assert response.json() == []

    async def test_get_review_statistics_not_found(self, client, mock_review_service):
        """Test getting review statistics for non-existent product."""
        # Arrange
        mock_review_service.get_review_statistics.side_effect = EntityNotFoundError("Product not found")
        
        # Act & Assert
        response = client.get("/reviews/statistics/non_existent_product")
        assert response.status_code == 404
        assert "Product not found" in response.json()["detail"]

    async def test_get_review_statistics_invalid_product_id(self, client, mock_review_service):
        """Test getting review statistics with invalid product ID."""
        # Arrange
        mock_review_service.get_review_statistics.side_effect = ValueError("Invalid product ID")
        
        # Act & Assert
        response = client.get("/reviews/statistics/invalid_product_id")
        assert response.status_code == 400
        assert "Invalid product ID" in response.json()["detail"]

    async def test_like_review_not_found(self, client, mock_review_service):
        """Test liking non-existent review."""
        # Arrange
        mock_review_service.like_review.side_effect = ReviewNotFoundError("Review not found")
        
        # Act & Assert
        response = client.post("/reviews/non_existent_review/like")
        assert response.status_code == 404
        assert "Review not found" in response.json()["detail"]

    async def test_like_review_already_liked(self, client, mock_review_service):
        """Test liking already liked review."""
        # Arrange
        mock_review_service.like_review.side_effect = InvalidOperationError("Review already liked")
        
        # Act & Assert
        response = client.post("/reviews/test_review/like")
        assert response.status_code == 400
        assert "Review already liked" in response.json()["detail"]

    async def test_unlike_review_not_found(self, client, mock_review_service):
        """Test unliking non-existent review."""
        # Arrange
        mock_review_service.unlike_review.side_effect = ReviewNotFoundError("Review not found")
        
        # Act & Assert
        response = client.delete("/reviews/non_existent_review/like")
        assert response.status_code == 404
        assert "Review not found" in response.json()["detail"]

    async def test_unlike_review_not_liked(self, client, mock_review_service):
        """Test unliking review that was not liked."""
        # Arrange
        mock_review_service.unlike_review.side_effect = InvalidOperationError("Review not liked")
        
        # Act & Assert
        response = client.delete("/reviews/test_review/like")
        assert response.status_code == 400
        assert "Review not liked" in response.json()["detail"]

    async def test_report_review_not_found(self, client, mock_review_service):
        """Test reporting non-existent review."""
        # Arrange
        mock_review_service.report_review.side_effect = ReviewNotFoundError("Review not found")
        
        request_data = {
            "reason": "Inappropriate content"
        }
        
        # Act & Assert
        response = client.post("/reviews/non_existent_review/report", json=request_data)
        assert response.status_code == 404
        assert "Review not found" in response.json()["detail"]

    async def test_report_review_invalid_reason(self, client, mock_review_service):
        """Test reporting review with invalid reason."""
        # Arrange
        mock_review_service.report_review.side_effect = ValueError("Invalid report reason")
        
        request_data = {
            "reason": ""
        }
        
        # Act & Assert
        response = client.post("/reviews/test_review/report", json=request_data)
        assert response.status_code == 400
        assert "Invalid report reason" in response.json()["detail"]

    async def test_report_review_already_reported(self, client, mock_review_service):
        """Test reporting already reported review."""
        # Arrange
        mock_review_service.report_review.side_effect = InvalidOperationError("Review already reported")
        
        request_data = {
            "reason": "Inappropriate content"
        }
        
        # Act & Assert
        response = client.post("/reviews/test_review/report", json=request_data)
        assert response.status_code == 400
        assert "Review already reported" in response.json()["detail"] 