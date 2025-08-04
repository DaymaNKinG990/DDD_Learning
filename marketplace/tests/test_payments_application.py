"""Tests for payments application services."""

import pytest
from decimal import Decimal
from unittest.mock import AsyncMock, Mock

from src.payments.application.services import PaymentService, PaymentMethodService
from src.payments.domain.entities import Payment, PaymentMethod
from src.payments.domain.value_objects import (
    PaymentId, PaymentMethodId, PaymentStatus, PaymentType, PaymentCurrency, PaymentAmount
)
from src.orders.domain.value_objects import OrderId
from src.users.domain.value_objects import UserId
from src.shared.domain.exceptions import EntityNotFoundError


class TestPaymentService:
    """Test PaymentService."""

    @pytest.fixture
    def payment_repository(self):
        """Create mock payment repository."""
        return AsyncMock()

    @pytest.fixture
    def event_bus(self):
        """Create mock event bus."""
        return AsyncMock()

    @pytest.fixture
    def service(self, payment_repository, event_bus):
        """Create payment service."""
        return PaymentService(payment_repository, event_bus)

    @pytest.fixture
    def sample_payment(self):
        """Create sample payment."""
        return Payment(
            id=PaymentId(value="payment_123"),
            order_id=OrderId(value="order_123"),
            user_id=UserId(value="user_123"),
            amount=PaymentAmount(amount=Decimal("100.00"), currency=PaymentCurrency.RUB),
            payment_type=PaymentType.CREDIT_CARD,
        )

    @pytest.mark.asyncio
    async def test_get_payment_found(self, service, payment_repository, sample_payment):
        """Test getting payment that exists."""
        # Arrange
        payment_id = "payment_123"
        payment_repository.get_by_id.return_value = sample_payment

        # Act
        result = await service.get_payment(payment_id)

        # Assert
        assert result == sample_payment
        payment_repository.get_by_id.assert_called_once_with(PaymentId(value=payment_id))

    @pytest.mark.asyncio
    async def test_get_payment_not_found(self, service, payment_repository):
        """Test getting payment that doesn't exist."""
        # Arrange
        payment_id = "payment_999"
        payment_repository.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(EntityNotFoundError, match=f"Payment with ID {payment_id} not found"):
            await service.get_payment(payment_id)

    @pytest.mark.asyncio
    async def test_get_payments_by_order(self, service, payment_repository, sample_payment):
        """Test getting payments by order."""
        # Arrange
        order_id = "order_123"
        expected_payments = [sample_payment]
        payment_repository.get_by_order_id.return_value = expected_payments

        # Act
        result = await service.get_payments_by_order(order_id)

        # Assert
        assert result == expected_payments
        payment_repository.get_by_order_id.assert_called_once_with(OrderId(value=order_id))

    @pytest.mark.asyncio
    async def test_get_payments_by_status(self, service, payment_repository, sample_payment):
        """Test getting payments by status."""
        # Arrange
        status = PaymentStatus.PENDING
        expected_payments = [sample_payment]
        payment_repository.get_by_status.return_value = expected_payments

        # Act
        result = await service.get_payments_by_status(status)

        # Assert
        assert result == expected_payments
        payment_repository.get_by_status.assert_called_once_with(status)

    @pytest.mark.asyncio
    async def test_process_payment(self, service, payment_repository, sample_payment):
        """Test processing payment."""
        # Arrange
        payment_id = "payment_123"
        payment_repository.get_by_id.return_value = sample_payment
        payment_repository.save.return_value = sample_payment

        # Act
        result = await service.process_payment(payment_id)

        # Assert
        assert result == sample_payment
        assert sample_payment.status == PaymentStatus.PROCESSING
        payment_repository.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_complete_payment(self, service, payment_repository, sample_payment):
        """Test completing payment."""
        # Arrange
        payment_id = "payment_123"
        external_payment_id = "ext_123"
        payment_repository.get_by_id.return_value = sample_payment
        payment_repository.save.return_value = sample_payment

        # Act
        result = await service.complete_payment(payment_id, external_payment_id)

        # Assert
        assert result == sample_payment
        assert sample_payment.status == PaymentStatus.COMPLETED
        assert sample_payment.external_payment_id == external_payment_id
        payment_repository.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_fail_payment(self, service, payment_repository, sample_payment):
        """Test failing payment."""
        # Arrange
        payment_id = "payment_123"
        reason = "Insufficient funds"
        payment_repository.get_by_id.return_value = sample_payment
        payment_repository.save.return_value = sample_payment

        # Act
        result = await service.fail_payment(payment_id, reason)

        # Assert
        assert result == sample_payment
        assert sample_payment.status == PaymentStatus.FAILED
        payment_repository.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_cancel_payment(self, service, payment_repository, sample_payment):
        """Test cancelling payment."""
        # Arrange
        payment_id = "payment_123"
        payment_repository.get_by_id.return_value = sample_payment
        payment_repository.save.return_value = sample_payment

        # Act
        result = await service.cancel_payment(payment_id)

        # Assert
        assert result == sample_payment
        assert sample_payment.status == PaymentStatus.CANCELLED
        payment_repository.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_refund_payment(self, service, payment_repository, sample_payment):
        """Test refunding payment."""
        # Arrange
        payment_id = "payment_123"
        refund_amount = PaymentAmount(amount=Decimal("50.00"), currency=PaymentCurrency.RUB)
        sample_payment.status = PaymentStatus.COMPLETED  # Payment must be completed to be refunded
        payment_repository.get_by_id.return_value = sample_payment
        payment_repository.save.return_value = sample_payment

        # Act
        result = await service.refund_payment(payment_id, refund_amount)

        # Assert
        assert result == sample_payment
        assert sample_payment.status == PaymentStatus.REFUNDED
        payment_repository.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_payment(self, service, payment_repository):
        """Test deleting payment."""
        # Arrange
        payment_id = "payment_123"
        payment_repository.delete.return_value = True

        # Act
        result = await service.delete_payment(payment_id)

        # Assert
        assert result is True
        payment_repository.delete.assert_called_once_with(PaymentId(value=payment_id))


class TestPaymentMethodService:
    """Test PaymentMethodService."""

    @pytest.fixture
    def payment_method_repository(self):
        """Create mock payment method repository."""
        return AsyncMock()

    @pytest.fixture
    def event_bus(self):
        """Create mock event bus."""
        return AsyncMock()

    @pytest.fixture
    def service(self, payment_method_repository, event_bus):
        """Create payment method service."""
        return PaymentMethodService(payment_method_repository, event_bus)

    @pytest.fixture
    def sample_payment_method(self):
        """Create sample payment method."""
        return PaymentMethod(
            id=PaymentMethodId(value="pm_123"),
            user_id=UserId(value="user_123"),
            payment_type=PaymentType.CREDIT_CARD,
            card_last_four="1234",
            card_brand="Visa",
        )

    @pytest.mark.asyncio
    async def test_get_payment_method_found(self, service, payment_method_repository, sample_payment_method):
        """Test getting payment method that exists."""
        # Arrange
        payment_method_id = "pm_123"
        payment_method_repository.get_by_id.return_value = sample_payment_method

        # Act
        result = await service.get_payment_method(payment_method_id)

        # Assert
        assert result == sample_payment_method
        payment_method_repository.get_by_id.assert_called_once_with(PaymentMethodId(value=payment_method_id))

    @pytest.mark.asyncio
    async def test_get_payment_method_not_found(self, service, payment_method_repository):
        """Test getting payment method that doesn't exist."""
        # Arrange
        payment_method_id = "pm_999"
        payment_method_repository.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(EntityNotFoundError, match=f"Payment method with ID {payment_method_id} not found"):
            await service.get_payment_method(payment_method_id)

    @pytest.mark.asyncio
    async def test_get_payment_methods_by_user(self, service, payment_method_repository, sample_payment_method):
        """Test getting payment methods by user."""
        # Arrange
        user_id = "user_123"
        expected_methods = [sample_payment_method]
        payment_method_repository.get_by_user_id.return_value = expected_methods

        # Act
        result = await service.get_payment_methods_by_user(user_id)

        # Assert
        assert result == expected_methods
        payment_method_repository.get_by_user_id.assert_called_once_with(UserId(value=user_id))

    @pytest.mark.asyncio
    async def test_get_active_payment_methods_by_user(self, service, payment_method_repository, sample_payment_method):
        """Test getting active payment methods by user."""
        # Arrange
        user_id = "user_123"
        expected_methods = [sample_payment_method]
        payment_method_repository.get_active_by_user_id.return_value = expected_methods

        # Act
        result = await service.get_active_payment_methods_by_user(user_id)

        # Assert
        assert result == expected_methods
        payment_method_repository.get_active_by_user_id.assert_called_once_with(UserId(value=user_id))

    @pytest.mark.asyncio
    async def test_get_default_payment_method(self, service, payment_method_repository, sample_payment_method):
        """Test getting default payment method."""
        # Arrange
        user_id = "user_123"
        payment_method_repository.get_default_by_user_id.return_value = sample_payment_method

        # Act
        result = await service.get_default_payment_method(user_id)

        # Assert
        assert result == sample_payment_method
        payment_method_repository.get_default_by_user_id.assert_called_once_with(UserId(value=user_id))

    @pytest.mark.asyncio
    async def test_activate_payment_method(self, service, payment_method_repository, sample_payment_method):
        """Test activating payment method."""
        # Arrange
        payment_method_id = "pm_123"
        sample_payment_method.is_active = False
        payment_method_repository.get_by_id.return_value = sample_payment_method
        payment_method_repository.save.return_value = sample_payment_method

        # Act
        result = await service.activate_payment_method(payment_method_id)

        # Assert
        assert result == sample_payment_method
        assert sample_payment_method.is_active is True
        payment_method_repository.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_deactivate_payment_method(self, service, payment_method_repository, sample_payment_method):
        """Test deactivating payment method."""
        # Arrange
        payment_method_id = "pm_123"
        sample_payment_method.is_active = True
        payment_method_repository.get_by_id.return_value = sample_payment_method
        payment_method_repository.save.return_value = sample_payment_method

        # Act
        result = await service.deactivate_payment_method(payment_method_id)

        # Assert
        assert result == sample_payment_method
        assert sample_payment_method.is_active is False
        payment_method_repository.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_set_as_default(self, service, payment_method_repository, sample_payment_method):
        """Test setting payment method as default."""
        # Arrange
        payment_method_id = "pm_123"
        existing_method = PaymentMethod(
            id=PaymentMethodId(value="pm_existing"),
            user_id=UserId(value="user_123"),
            payment_type=PaymentType.CREDIT_CARD,
            card_last_four="5678",
            card_brand="Mastercard",
            is_default=True,
        )
        
        payment_method_repository.get_by_id.return_value = sample_payment_method
        payment_method_repository.get_by_user_id.return_value = [existing_method, sample_payment_method]
        payment_method_repository.save.return_value = sample_payment_method

        # Act
        result = await service.set_as_default(payment_method_id)

        # Assert
        assert result == sample_payment_method
        assert sample_payment_method.is_default is True
        assert existing_method.is_default is False
        assert payment_method_repository.save.call_count == 2

    @pytest.mark.asyncio
    async def test_delete_payment_method(self, service, payment_method_repository):
        """Test deleting payment method."""
        # Arrange
        payment_method_id = "pm_123"
        payment_method_repository.delete.return_value = True

        # Act
        result = await service.delete_payment_method(payment_method_id)

        # Assert
        assert result is True
        payment_method_repository.delete.assert_called_once_with(PaymentMethodId(value=payment_method_id)) 