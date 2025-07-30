"""Tests for reviews domain."""


import pytest
from src.reviews.domain.entities import Review, ReviewModeration, ReviewResponse
from src.reviews.domain.value_objects import (
    HelpfulVotes,
    Rating,
    ReviewContent,
    ReviewId,
    ReviewStatus,
    ReviewTitle,
    ReviewType,
)
from src.users.domain.value_objects import UserId


class TestReview:
    """Test Review entity."""

    def test_create_review(self):
        """Test creating a review."""
        from src.catalog.domain.value_objects import ProductId

        review = Review(
            id=ReviewId(value="review-123"),
            user_id=UserId(value="user-123"),
            product_id=ProductId(value="product-456"),
            review_type=ReviewType.PRODUCT,
            title=ReviewTitle(value="Отличный товар!"),
            content=ReviewContent(value="Очень качественный продукт, рекомендую всем."),
            rating=Rating(value=5)
        )

        assert review.user_id.value == "user-123"
        assert review.product_id.value == "product-456"
        assert review.review_type == ReviewType.PRODUCT
        assert review.title.value == "Отличный товар!"
        assert review.content.value == "Очень качественный продукт, рекомендую всем."
        assert review.rating.value == 5
        assert review.status == ReviewStatus.PENDING
        assert review.helpful_votes.value == 0
        assert review.is_verified_purchase is False

    def test_approve_review(self):
        """Test approving a review."""
        from src.catalog.domain.value_objects import ProductId

        review = Review(
            id=ReviewId(value="review-456"),
            user_id=UserId(value="user-123"),
            product_id=ProductId(value="product-456"),
            review_type=ReviewType.PRODUCT,
            title=ReviewTitle(value="Хороший товар"),
            content=ReviewContent(value="Качество на высоте, доставка быстрая."),
            rating=Rating(value=4)
        )

        review.approve()
        assert review.status == ReviewStatus.APPROVED
        assert review.updated_at is not None

    def test_reject_review(self):
        """Test rejecting a review."""
        from src.catalog.domain.value_objects import ProductId

        review = Review(
            id=ReviewId(value="review-789"),
            user_id=UserId(value="user-123"),
            product_id=ProductId(value="product-456"),
            review_type=ReviewType.PRODUCT,
            title=ReviewTitle(value="Плохой товар"),
            content=ReviewContent(value="Не рекомендую."),
            rating=Rating(value=1)
        )

        reason = "Нарушение правил сообщества"
        review.reject(reason)
        assert review.status == ReviewStatus.REJECTED
        assert review.moderator_notes == reason
        assert review.updated_at is not None

    def test_hide_review(self):
        """Test hiding a review."""
        from src.catalog.domain.value_objects import ProductId

        review = Review(
            id=ReviewId(value="review-101"),
            user_id=UserId(value="user-123"),
            product_id=ProductId(value="product-456"),
            review_type=ReviewType.PRODUCT,
            title=ReviewTitle(value="Средний товар"),
            content=ReviewContent(value="Нормальное качество."),
            rating=Rating(value=3)
        )

        review.hide()
        assert review.status == ReviewStatus.HIDDEN
        assert review.updated_at is not None

    def test_mark_as_helpful(self):
        """Test marking review as helpful."""
        from src.catalog.domain.value_objects import ProductId

        review = Review(
            id=ReviewId(value="review-202"),
            user_id=UserId(value="user-123"),
            product_id=ProductId(value="product-456"),
            review_type=ReviewType.PRODUCT,
            title=ReviewTitle(value="Полезный отзыв"),
            content=ReviewContent(value="Много полезной информации."),
            rating=Rating(value=5)
        )

        assert review.helpful_votes.value == 0
        review.mark_as_helpful()
        assert review.helpful_votes.value == 1
        review.mark_as_helpful()
        assert review.helpful_votes.value == 2

    def test_unmark_as_helpful(self):
        """Test unmarking review as helpful."""
        from src.catalog.domain.value_objects import ProductId

        review = Review(
            id=ReviewId(value="review-303"),
            user_id=UserId(value="user-123"),
            product_id=ProductId(value="product-456"),
            review_type=ReviewType.PRODUCT,
            title=ReviewTitle(value="Полезный отзыв"),
            content=ReviewContent(value="Много полезной информации."),
            rating=Rating(value=5)
        )

        review.mark_as_helpful()
        review.mark_as_helpful()
        assert review.helpful_votes.value == 2

        review.unmark_as_helpful()
        assert review.helpful_votes.value == 1

        # Should not go below 0
        review.unmark_as_helpful()
        review.unmark_as_helpful()
        assert review.helpful_votes.value == 0

    def test_update_content(self):
        """Test updating review content."""
        from src.catalog.domain.value_objects import ProductId

        review = Review(
            id=ReviewId(value="review-404"),
            user_id=UserId(value="user-123"),
            product_id=ProductId(value="product-456"),
            review_type=ReviewType.PRODUCT,
            title=ReviewTitle(value="Старый заголовок"),
            content=ReviewContent(value="Старое содержание."),
            rating=Rating(value=3)
        )

        review.update_content(
            title="Новый заголовок",
            content="Новое содержание с дополнительной информацией.",
            rating=4
        )

        assert review.title.value == "Новый заголовок"
        assert review.content.value == "Новое содержание с дополнительной информацией."
        assert review.rating.value == 4
        assert review.updated_at is not None

    def test_status_checks(self):
        """Test status check methods."""
        from src.catalog.domain.value_objects import ProductId

        review = Review(
            id=ReviewId(value="review-505"),
            user_id=UserId(value="user-123"),
            product_id=ProductId(value="product-456"),
            review_type=ReviewType.PRODUCT,
            title=ReviewTitle(value="Тестовый отзыв"),
            content=ReviewContent(value="Тестовое содержание."),
            rating=Rating(value=4)
        )

        assert review.is_pending() is True
        assert review.is_approved() is False
        assert review.is_rejected() is False

        review.approve()
        assert review.is_pending() is False
        assert review.is_approved() is True
        assert review.is_rejected() is False

        review.reject("Test reason")
        assert review.is_pending() is False
        assert review.is_approved() is False
        assert review.is_rejected() is True


class TestReviewResponse:
    """Test ReviewResponse entity."""

    def test_create_review_response(self):
        """Test creating a review response."""
        from src.users.domain.value_objects import UserId

        response = ReviewResponse(
            id="response-123",
            review_id=ReviewId(value="review-123"),
            responder_id=UserId(value="seller-456"),
            content=ReviewContent(
                value="Спасибо за отзыв! Мы рады, что вам понравился наш товар."
            )
        )

        assert response.review_id.value == "review-123"
        assert response.responder_id.value == "seller-456"
        assert (
            response.content.value 
            == "Спасибо за отзыв! Мы рады, что вам понравился наш товар."
        )
        assert response.is_public is True

    def test_update_content(self):
        """Test updating response content."""
        from src.users.domain.value_objects import UserId

        response = ReviewResponse(
            id="response-456",
            review_id=ReviewId(value="review-123"),
            responder_id=UserId(value="seller-456"),
            content=ReviewContent(value="Первоначальный ответ.")
        )

        response.update_content("Обновленный ответ с дополнительной информацией.")
        assert (
            response.content.value 
            == "Обновленный ответ с дополнительной информацией."
        )
        assert response.updated_at is not None

    def test_make_private_public(self):
        """Test making response private and public."""
        from src.users.domain.value_objects import UserId

        response = ReviewResponse(
            id="response-789",
            review_id=ReviewId(value="review-123"),
            responder_id=UserId(value="seller-456"),
            content=ReviewContent(value="Тестовый ответ.")
        )

        assert response.is_public is True

        response.make_private()
        assert response.is_public is False

        response.make_public()
        assert response.is_public is True


class TestReviewModeration:
    """Test ReviewModeration entity."""

    def test_create_review_moderation(self):
        """Test creating a review moderation."""
        moderation = ReviewModeration(
            id=ReviewId(value="mod-123"),
            review_id=ReviewId(value="review-123"),
            moderator_id=UserId(value="moderator-456"),
            action="approve",
            reason="Соответствует правилам"
        )

        assert moderation.review_id.value == "review-123"
        assert moderation.moderator_id.value == "moderator-456"
        assert moderation.action == "approve"
        assert moderation.reason == "Соответствует правилам"

    def test_add_note(self):
        """Test adding notes to moderation."""
        moderation = ReviewModeration(
            id=ReviewId(value="mod-123"),
            review_id=ReviewId(value="review-123"),
            moderator_id=UserId(value="moderator-456"),
            action="reject",
            reason="Нарушение правил"
        )

        moderation.add_note("Дополнительная информация о нарушении")
        assert "Дополнительная информация о нарушении" in moderation.notes

        moderation.add_note("Еще одна заметка")
        assert "Дополнительная информация о нарушении" in moderation.notes
        assert "Еще одна заметка" in moderation.notes


class TestValueObjects:
    """Test reviews value objects."""

    def test_rating_validation(self):
        """Test rating validation."""
        # Valid ratings
        for rating in [1, 2, 3, 4, 5]:
            rating_obj = Rating(value=rating)
            assert rating_obj.value == rating

        # Invalid ratings
        with pytest.raises(ValueError, match="between 1 and 5"):
            Rating(value=0)

        with pytest.raises(ValueError, match="between 1 and 5"):
            Rating(value=6)

    def test_review_title_validation(self):
        """Test review title validation."""
        # Valid title
        title = ReviewTitle(value="Отличный товар!")
        assert title.value == "Отличный товар!"

        # Invalid title (too short)
        with pytest.raises(ValueError, match="at least 3 characters"):
            ReviewTitle(value="А")

        # Invalid title (too long)
        with pytest.raises(ValueError, match="cannot exceed 100 characters"):
            ReviewTitle(value="A" * 101)

    def test_review_content_validation(self):
        """Test review content validation."""
        # Valid content
        content = ReviewContent(
            value="Очень подробный отзыв с множеством деталей о товаре."
        )
        assert (
            content.value 
            == "Очень подробный отзыв с множеством деталей о товаре."
        )

        # Invalid content (too short)
        with pytest.raises(ValueError, match="at least 10 characters"):
            ReviewContent(value="Короткий")

        # Invalid content (too long)
        with pytest.raises(ValueError, match="cannot exceed 2000 characters"):
            ReviewContent(value="A" * 2001)

    def test_helpful_votes(self):
        """Test helpful votes functionality."""
        votes = HelpfulVotes(value=0)
        assert votes.value == 0

        votes = votes.increment()
        assert votes.value == 1

        votes = votes.increment()
        assert votes.value == 2

        votes = votes.decrement()
        assert votes.value == 1

        votes = votes.decrement()
        assert votes.value == 0

        # Should not go below 0
        votes = votes.decrement()
        assert votes.value == 0
