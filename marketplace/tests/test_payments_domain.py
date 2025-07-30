"""Tests for payments domain."""

from decimal import Decimal

import pytest
from src.orders.domain.value_objects import OrderId
from src.payments.domain.entities import Payment, PaymentMethod
from src.payments.domain.value_objects import (
    Amount,
    PaymentId,
    PaymentMethodId,
    PaymentStatus,
)
from src.users.domain.value_objects import UserId


class TestPaymentId:
    """Test PaymentId value object."""

    def test_create_payment_id(self):
        """Test creating payment ID."""
        payment_id = PaymentId(value="payment_123")
        assert payment_id.value == "payment_123"

    def test_payment_id_hash(self):
        """Test payment ID hash."""
        payment_id1 = PaymentId(value="payment_123")
        payment_id2 = PaymentId(value="payment_123")
        payment_id3 = PaymentId(value="payment_456")

        assert hash(payment_id1) == hash(payment_id2)
        assert hash(payment_id1) != hash(payment_id3)


class TestPaymentMethodId:
    """Test PaymentMethodId value object."""

    def test_create_payment_method_id(self):
        """Test creating payment method ID."""
        payment_method_id = PaymentMethodId(value="pm_123")
        assert payment_method_id.value == "pm_123"

    def test_payment_method_id_hash(self):
        """Test payment method ID hash."""
        pm_id1 = PaymentMethodId(value="pm_123")
        pm_id2 = PaymentMethodId(value="pm_123")
        pm_id3 = PaymentMethodId(value="pm_456")

        assert hash(pm_id1) == hash(pm_id2)
        assert hash(pm_id1) != hash(pm_id3)


class TestAmount:
    """Test Amount value object."""

    def test_create_amount(self):
        """Test creating amount."""
        amount = Amount.create(100.50, "RUB")
        assert amount.value == Decimal("100.50")
        assert amount.currency == "RUB"

    def test_amount_validation_negative_value(self):
        """Test amount validation with negative value."""
        with pytest.raises(ValueError, match="Amount cannot be negative"):
            Amount.create(-100, "RUB")

    def test_amount_validation_invalid_currency(self):
        """Test amount validation with invalid currency."""
        with pytest.raises(ValueError, match="Currency must be a 3-letter code"):
            Amount.create(100, "RU")

    def test_amount_addition(self):
        """Test amount addition."""
        amount1 = Amount.create(100, "RUB")
        amount2 = Amount.create(50, "RUB")
        result = amount1 + amount2
        assert result.value == Decimal("150")
        assert result.currency == "RUB"

    def test_amount_addition_different_currencies(self):
        """Test amount addition with different currencies."""
        amount1 = Amount.create(100, "RUB")
        amount2 = Amount.create(50, "USD")
        with pytest.raises(
            ValueError, match="Cannot add amounts with different currencies"
        ):
            amount1 + amount2

    def test_amount_subtraction(self):
        """Test amount subtraction."""
        amount1 = Amount.create(100, "RUB")
        amount2 = Amount.create(30, "RUB")
        result = amount1 - amount2
        assert result.value == Decimal("70")
        assert result.currency == "RUB"


class TestPaymentMethod:
    """Test PaymentMethod entity."""

    def test_create_payment_method(self):
        """Test creating payment method."""
        payment_method = PaymentMethod(
            id=PaymentMethodId(value="pm_123"),
            user_id=UserId(value="user_123"),
            type="card",
            name="Visa ****1234",
        )
        assert payment_method.type == "card"
        assert payment_method.name == "Visa ****1234"
        assert payment_method.is_active is True
        assert payment_method.is_default is False

    def test_activate_payment_method(self):
        """Test activating payment method."""
        payment_method = PaymentMethod(
            id=PaymentMethodId(value="pm_123"),
            user_id=UserId(value="user_123"),
            type="card",
            name="Visa ****1234",
            is_active=False,
        )
        payment_method.activate()
        assert payment_method.is_active is True

    def test_deactivate_payment_method(self):
        """Test deactivating payment method."""
        payment_method = PaymentMethod(
            id=PaymentMethodId(value="pm_123"),
            user_id=UserId(value="user_123"),
            type="card",
            name="Visa ****1234",
        )
        payment_method.deactivate()
        assert payment_method.is_active is False

    def test_set_as_default(self):
        """Test setting payment method as default."""
        payment_method = PaymentMethod(
            id=PaymentMethodId(value="pm_123"),
            user_id=UserId(value="user_123"),
            type="card",
            name="Visa ****1234",
        )
        payment_method.set_as_default()
        assert payment_method.is_default is True

    def test_remove_default(self):
        """Test removing default status."""
        payment_method = PaymentMethod(
            id=PaymentMethodId(value="pm_123"),
            user_id=UserId(value="user_123"),
            type="card",
            name="Visa ****1234",
            is_default=True,
        )
        payment_method.remove_default()
        assert payment_method.is_default is False

    def test_update_metadata(self):
        """Test updating metadata."""
        payment_method = PaymentMethod(
            id=PaymentMethodId(value="pm_123"),
            user_id=UserId(value="user_123"),
            type="card",
            name="Visa ****1234",
        )
        payment_method.update_metadata({"last4": "1234", "brand": "visa"})
        assert payment_method.metadata["last4"] == "1234"
        assert payment_method.metadata["brand"] == "visa"


class TestPayment:
    """Test Payment entity."""

    def test_create_payment(self):
        """Test creating payment."""
        payment = Payment(
            id=PaymentId(value="payment_123"),
            order_id=OrderId(value="order_123"),
            amount=Amount.create(1000, "RUB"),
            payment_method_id=PaymentMethodId(value="pm_123"),
        )
        assert payment.status == PaymentStatus.PENDING
        assert payment.amount.value == Decimal("1000")
        assert payment.amount.currency == "RUB"

    def test_process_payment(self):
        """Test processing payment."""
        payment = Payment(
            id=PaymentId(value="payment_123"),
            order_id=OrderId(value="order_123"),
            amount=Amount.create(1000, "RUB"),
            payment_method_id=PaymentMethodId(value="pm_123"),
        )
        payment.process()
        assert payment.status == PaymentStatus.PROCESSING

    def test_process_payment_wrong_status(self):
        """Test processing payment with wrong status."""
        payment = Payment(
            id=PaymentId(value="payment_123"),
            order_id=OrderId(value="order_123"),
            amount=Amount.create(1000, "RUB"),
            payment_method_id=PaymentMethodId(value="pm_123"),
        )
        payment.process()
        with pytest.raises(ValueError, match="Only pending payments can be processed"):
            payment.process()

    def test_complete_payment(self):
        """Test completing payment."""
        payment = Payment(
            id=PaymentId(value="payment_123"),
            order_id=OrderId(value="order_123"),
            amount=Amount.create(1000, "RUB"),
            payment_method_id=PaymentMethodId(value="pm_123"),
        )
        payment.complete("ext_123")
        assert payment.status == PaymentStatus.COMPLETED
        assert payment.external_payment_id == "ext_123"
        assert payment.processed_at is not None

    def test_fail_payment(self):
        """Test failing payment."""
        payment = Payment(
            id=PaymentId(value="payment_123"),
            order_id=OrderId(value="order_123"),
            amount=Amount.create(1000, "RUB"),
            payment_method_id=PaymentMethodId(value="pm_123"),
        )
        payment.fail("Insufficient funds")
        assert payment.status == PaymentStatus.FAILED
        assert payment.failure_reason == "Insufficient funds"

    def test_cancel_payment(self):
        """Test cancelling payment."""
        payment = Payment(
            id=PaymentId(value="payment_123"),
            order_id=OrderId(value="order_123"),
            amount=Amount.create(1000, "RUB"),
            payment_method_id=PaymentMethodId(value="pm_123"),
        )
        payment.cancel()
        assert payment.status == PaymentStatus.CANCELLED

    def test_refund_payment(self):
        """Test refunding payment."""
        payment = Payment(
            id=PaymentId(value="payment_123"),
            order_id=OrderId(value="order_123"),
            amount=Amount.create(1000, "RUB"),
            payment_method_id=PaymentMethodId(value="pm_123"),
        )
        payment.complete("ext_123")
        payment.refund()
        assert payment.status == PaymentStatus.REFUNDED

    def test_refund_payment_not_completed(self):
        """Test refunding payment that is not completed."""
        payment = Payment(
            id=PaymentId(value="payment_123"),
            order_id=OrderId(value="order_123"),
            amount=Amount.create(1000, "RUB"),
            payment_method_id=PaymentMethodId(value="pm_123"),
        )
        with pytest.raises(ValueError, match="Only completed payments can be refunded"):
            payment.refund()

    def test_status_checks(self):
        """Test payment status checks."""
        payment = Payment(
            id=PaymentId(value="payment_123"),
            order_id=OrderId(value="order_123"),
            amount=Amount.create(1000, "RUB"),
            payment_method_id=PaymentMethodId(value="pm_123"),
        )

        assert payment.is_completed() is False
        assert payment.is_failed() is False
        assert payment.is_cancelled() is False
        assert payment.is_refunded() is False

        payment.complete("ext_123")
        assert payment.is_completed() is True

        payment = Payment(
            id=PaymentId(value="payment_124"),
            order_id=OrderId(value="order_124"),
            amount=Amount.create(1000, "RUB"),
            payment_method_id=PaymentMethodId(value="pm_124"),
        )
        payment.fail("Error")
        assert payment.is_failed() is True

        payment = Payment(
            id=PaymentId(value="payment_125"),
            order_id=OrderId(value="order_125"),
            amount=Amount.create(1000, "RUB"),
            payment_method_id=PaymentMethodId(value="pm_125"),
        )
        payment.cancel()
        assert payment.is_cancelled() is True

        payment = Payment(
            id=PaymentId(value="payment_126"),
            order_id=OrderId(value="order_126"),
            amount=Amount.create(1000, "RUB"),
            payment_method_id=PaymentMethodId(value="pm_126"),
        )
        payment.complete("ext_126")
        payment.refund()
        assert payment.is_refunded() is True
