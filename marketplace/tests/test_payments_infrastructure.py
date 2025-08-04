"""Tests for payments infrastructure repositories."""

import pytest
from datetime import datetime, UTC
from decimal import Decimal
from unittest.mock import AsyncMock

from src.payments.infrastructure.repositories import (
    InMemoryPaymentRepository,
    InMemoryPaymentMethodRepository,
)
from src.payments.domain.entities import (
    Payment,
    PaymentMethod,
)
from src.payments.domain.value_objects import (
    PaymentId,
    PaymentMethodId,
    PaymentStatus,
    PaymentAmount,
    PaymentCurrency,
    PaymentType,
)
from src.orders.domain.value_objects import OrderId
from src.users.domain.value_objects import UserId


class TestInMemoryPaymentRepository:
    """Test InMemoryPaymentRepository."""

    @pytest.fixture
    def repository(self):
        """Create InMemoryPaymentRepository."""
        return InMemoryPaymentRepository()

    @pytest.fixture
    def sample_payment(self):
        """Create sample payment."""
        return Payment(
            id=PaymentId(value="payment-123"),
            order_id=OrderId(value="order-123"),
            user_id=UserId(value="user-123"),
            amount=PaymentAmount(
                amount=Decimal("100.00"),
                currency=PaymentCurrency.USD
            ),
            payment_type=PaymentType.CREDIT_CARD,
            status=PaymentStatus.PENDING,
            external_payment_id="ext-123",
            created_at=datetime.now(UTC)
        )

    @pytest.mark.asyncio
    async def test_save_payment(self, repository, sample_payment):
        """Test saving a payment."""
        # Act
        result = await repository.save(sample_payment)

        # Assert
        assert result == sample_payment
        saved_payment = await repository.get_by_id(sample_payment.id)
        assert saved_payment == sample_payment

    @pytest.mark.asyncio
    async def test_get_by_id_found(self, repository, sample_payment):
        """Test getting payment by ID when it exists."""
        # Arrange
        await repository.save(sample_payment)

        # Act
        result = await repository.get_by_id(sample_payment.id)

        # Assert
        assert result == sample_payment

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, repository):
        """Test getting payment by ID when it doesn't exist."""
        # Act
        result = await repository.get_by_id(PaymentId(value="payment-999"))

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_get_by_order_id(self, repository, sample_payment):
        """Test getting payments by order ID."""
        # Arrange
        await repository.save(sample_payment)

        # Act
        result = await repository.get_by_order_id(OrderId(value="order-123"))

        # Assert
        assert len(result) == 1
        assert result[0] == sample_payment

    @pytest.mark.asyncio
    async def test_get_by_order_id_empty(self, repository):
        """Test getting payments by order ID when none exist."""
        # Act
        result = await repository.get_by_order_id(OrderId(value="order-999"))

        # Assert
        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_get_by_status(self, repository, sample_payment):
        """Test getting payments by status."""
        # Arrange
        await repository.save(sample_payment)

        # Act
        result = await repository.get_by_status(PaymentStatus.PENDING)

        # Assert
        assert len(result) == 1
        assert result[0] == sample_payment

    @pytest.mark.asyncio
    async def test_get_by_status_empty(self, repository):
        """Test getting payments by status when none exist."""
        # Act
        result = await repository.get_by_status(PaymentStatus.COMPLETED)

        # Assert
        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_get_by_external_id_found(self, repository, sample_payment):
        """Test getting payment by external ID when it exists."""
        # Arrange
        await repository.save(sample_payment)

        # Act
        result = await repository.get_by_external_id("ext-123")

        # Assert
        assert result == sample_payment

    @pytest.mark.asyncio
    async def test_get_by_external_id_not_found(self, repository):
        """Test getting payment by external ID when it doesn't exist."""
        # Act
        result = await repository.get_by_external_id("ext-999")

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_get_by_external_id_none(self, repository):
        """Test getting payment by external ID when payment has no external ID."""
        # Arrange
        payment_without_external = Payment(
            id=PaymentId(value="payment-no-ext"),
            order_id=OrderId(value="order-123"),
            user_id=UserId(value="user-123"),
            amount=PaymentAmount(
                amount=Decimal("100.00"),
                currency=PaymentCurrency.USD
            ),
            payment_type=PaymentType.CREDIT_CARD,
            status=PaymentStatus.PENDING,
            external_payment_id=None,
            created_at=datetime.now(UTC)
        )
        await repository.save(payment_without_external)

        # Act
        result = await repository.get_by_external_id("ext-123")

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_delete_payment(self, repository, sample_payment):
        """Test deleting a payment."""
        # Arrange
        await repository.save(sample_payment)

        # Act
        result = await repository.delete(sample_payment.id)

        # Assert
        assert result is True
        deleted_payment = await repository.get_by_id(sample_payment.id)
        assert deleted_payment is None

    @pytest.mark.asyncio
    async def test_delete_payment_not_found(self, repository):
        """Test deleting a payment that doesn't exist."""
        # Act
        result = await repository.delete(PaymentId(value="payment-999"))

        # Assert
        assert result is False

    @pytest.mark.asyncio
    async def test_list_all_payments(self, repository, sample_payment):
        """Test listing all payments."""
        # Arrange
        await repository.save(sample_payment)

        # Act
        result = await repository.list_all()

        # Assert
        assert len(result) == 1
        assert result[0] == sample_payment

    @pytest.mark.asyncio
    async def test_list_all_payments_empty(self, repository):
        """Test listing all payments when none exist."""
        # Act
        result = await repository.list_all()

        # Assert
        assert len(result) == 0


class TestInMemoryPaymentMethodRepository:
    """Test InMemoryPaymentMethodRepository."""

    @pytest.fixture
    def repository(self):
        """Create InMemoryPaymentMethodRepository."""
        return InMemoryPaymentMethodRepository()

    @pytest.fixture
    def sample_payment_method(self):
        """Create sample payment method."""
        return PaymentMethod(
            id=PaymentMethodId(value="pm-123"),
            user_id=UserId(value="user-123"),
            payment_type=PaymentType.CREDIT_CARD,
            card_last_four="1234",
            card_brand="Visa",
            is_default=True,
            is_active=True,
            created_at=datetime.now(UTC)
        )

    @pytest.mark.asyncio
    async def test_save_payment_method(self, repository, sample_payment_method):
        """Test saving a payment method."""
        # Act
        result = await repository.save(sample_payment_method)

        # Assert
        assert result == sample_payment_method
        saved_payment_method = await repository.get_by_id(sample_payment_method.id)
        assert saved_payment_method == sample_payment_method

    @pytest.mark.asyncio
    async def test_get_by_id_found(self, repository, sample_payment_method):
        """Test getting payment method by ID when it exists."""
        # Arrange
        await repository.save(sample_payment_method)

        # Act
        result = await repository.get_by_id(sample_payment_method.id)

        # Assert
        assert result == sample_payment_method

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, repository):
        """Test getting payment method by ID when it doesn't exist."""
        # Act
        result = await repository.get_by_id(PaymentMethodId(value="pm-999"))

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_get_by_user_id(self, repository, sample_payment_method):
        """Test getting payment methods by user ID."""
        # Arrange
        await repository.save(sample_payment_method)

        # Act
        result = await repository.get_by_user_id(UserId(value="user-123"))

        # Assert
        assert len(result) == 1
        assert result[0] == sample_payment_method

    @pytest.mark.asyncio
    async def test_get_by_user_id_empty(self, repository):
        """Test getting payment methods by user ID when none exist."""
        # Act
        result = await repository.get_by_user_id(UserId(value="user-999"))

        # Assert
        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_get_default_by_user_id_found(self, repository, sample_payment_method):
        """Test getting default payment method by user ID when it exists."""
        # Arrange
        await repository.save(sample_payment_method)

        # Act
        result = await repository.get_default_by_user_id(UserId(value="user-123"))

        # Assert
        assert result == sample_payment_method

    @pytest.mark.asyncio
    async def test_get_default_by_user_id_not_found(self, repository):
        """Test getting default payment method by user ID when it doesn't exist."""
        # Act
        result = await repository.get_default_by_user_id(UserId(value="user-999"))

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_get_default_by_user_id_not_default(self, repository):
        """Test getting default payment method when user has no default method."""
        # Arrange
        non_default_method = PaymentMethod(
            id=PaymentMethodId(value="pm-non-default"),
            user_id=UserId(value="user-123"),
            payment_type=PaymentType.CREDIT_CARD,
            card_last_four="5678",
            card_brand="Mastercard",
            is_default=False,
            is_active=True,
            created_at=datetime.now(UTC)
        )
        await repository.save(non_default_method)

        # Act
        result = await repository.get_default_by_user_id(UserId(value="user-123"))

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_get_active_by_user_id(self, repository, sample_payment_method):
        """Test getting active payment methods by user ID."""
        # Arrange
        await repository.save(sample_payment_method)

        # Act
        result = await repository.get_active_by_user_id(UserId(value="user-123"))

        # Assert
        assert len(result) == 1
        assert result[0] == sample_payment_method

    @pytest.mark.asyncio
    async def test_get_active_by_user_id_inactive(self, repository):
        """Test getting active payment methods when user has inactive methods."""
        # Arrange
        inactive_method = PaymentMethod(
            id=PaymentMethodId(value="pm-inactive"),
            user_id=UserId(value="user-123"),
            payment_type=PaymentType.CREDIT_CARD,
            card_last_four="5678",
            card_brand="Mastercard",
            is_default=True,
            is_active=False,
            created_at=datetime.now(UTC)
        )
        await repository.save(inactive_method)

        # Act
        result = await repository.get_active_by_user_id(UserId(value="user-123"))

        # Assert
        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_get_active_by_user_id_empty(self, repository):
        """Test getting active payment methods by user ID when none exist."""
        # Act
        result = await repository.get_active_by_user_id(UserId(value="user-999"))

        # Assert
        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_delete_payment_method(self, repository, sample_payment_method):
        """Test deleting a payment method."""
        # Arrange
        await repository.save(sample_payment_method)

        # Act
        result = await repository.delete(sample_payment_method.id)

        # Assert
        assert result is True
        deleted_payment_method = await repository.get_by_id(sample_payment_method.id)
        assert deleted_payment_method is None

    @pytest.mark.asyncio
    async def test_delete_payment_method_not_found(self, repository):
        """Test deleting a payment method that doesn't exist."""
        # Act
        result = await repository.delete(PaymentMethodId(value="pm-999"))

        # Assert
        assert result is False

    @pytest.mark.asyncio
    async def test_list_all_payment_methods(self, repository, sample_payment_method):
        """Test listing all payment methods."""
        # Arrange
        await repository.save(sample_payment_method)

        # Act
        result = await repository.list_all()

        # Assert
        assert len(result) == 1
        assert result[0] == sample_payment_method

    @pytest.mark.asyncio
    async def test_list_all_payment_methods_empty(self, repository):
        """Test listing all payment methods when none exist."""
        # Act
        result = await repository.list_all()

        # Assert
        assert len(result) == 0 