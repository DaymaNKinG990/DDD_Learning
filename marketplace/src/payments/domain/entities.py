"""Entities for the payments domain."""

# Python imports
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Optional

# Local imports
from src.orders.domain.value_objects import OrderId
from src.shared.domain.entity import Entity
from src.users.domain.value_objects import UserId
from .value_objects import (
    Amount,
    PaymentId,
    PaymentMethodId,
    PaymentStatus,
    PaymentType,
    PaymentCurrency,
    PaymentAmount,
)


@dataclass
class PaymentMethod(Entity[PaymentMethodId]):
    """
    Payment method entity.
    
    This entity represents a payment method used for payments.
    
    Attributes:
        user_id (UserId): The ID of the user.
        payment_type (PaymentType): The type of the payment method.
        card_last_four (str): The last four digits of the card.
        card_brand (str): The brand of the card.
        is_active (bool): Whether the payment method is active.
        is_default (bool): Whether the payment method is the default.
        created_at (datetime): The date and time the payment method was created.
    """

    user_id: UserId
    payment_type: PaymentType
    card_last_four: str
    card_brand: str
    is_active: bool = True
    is_default: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __hash__(self) -> int:
        """Hash the payment method."""
        return hash(self.id)

    def deactivate(self) -> None:
        """Deactivate payment method."""
        self.is_active = False

    def activate(self) -> None:
        """Activate payment method."""
        self.is_active = True

    def set_as_default(self) -> None:
        """Set payment method as default."""
        self.is_default = True

    def remove_default(self) -> None:
        """Remove default status from payment method."""
        self.is_default = False


@dataclass
class Payment(Entity[PaymentId]):
    """
    Payment entity.
    
    This entity represents a payment made for an order.
    
    Attributes:
        order_id (OrderId): The ID of the order.
        user_id (UserId): The ID of the user.
        amount (PaymentAmount): The amount of the payment.
        payment_type (PaymentType): The type of the payment.
        status (PaymentStatus): The status of the payment.
        external_payment_id (Optional[str]): The ID of the external payment.
        created_at (datetime): The date and time the payment was created.
    """

    order_id: OrderId
    user_id: UserId
    amount: PaymentAmount
    payment_type: PaymentType
    status: PaymentStatus = PaymentStatus.PENDING
    external_payment_id: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __hash__(self) -> int:
        """Hash the payment."""
        return hash(self.id)

    def process(self) -> None:
        """Mark payment as processing."""
        if self.status != PaymentStatus.PENDING:
            raise ValueError("Only pending payments can be processed")
        self.status = PaymentStatus.PROCESSING

    def complete(self, external_payment_id: Optional[str] = None) -> None:
        """
        Mark payment as completed.
        
        Args:
            external_payment_id (Optional[str]): The ID of the external payment.
        """
        if self.status not in [PaymentStatus.PENDING, PaymentStatus.PROCESSING]:
            raise ValueError("Only pending or processing payments can be completed")
        self.status = PaymentStatus.COMPLETED
        self.external_payment_id = external_payment_id

    def fail(self, reason: str) -> None:
        """
        Mark payment as failed.
        
        Args:
            reason (str): The reason for the failure.
        """
        if self.status not in [PaymentStatus.PENDING, PaymentStatus.PROCESSING]:
            raise ValueError("Only pending or processing payments can be failed")
        self.status = PaymentStatus.FAILED

    def cancel(self) -> None:
        """Cancel payment."""
        if self.status not in [PaymentStatus.PENDING, PaymentStatus.PROCESSING]:
            raise ValueError("Only pending or processing payments can be cancelled")
        self.status = PaymentStatus.CANCELLED

    def refund(self, refund_amount: Optional[PaymentAmount] = None) -> None:
        """
        Refund payment.
        
        Args:
            refund_amount (Optional[PaymentAmount]): The amount to refund.
        """
        if self.status != PaymentStatus.COMPLETED:
            raise ValueError("Only completed payments can be refunded")
        self.status = PaymentStatus.REFUNDED

    def is_completed(self) -> bool:
        """
        Check if payment is completed.
        
        Returns:
            bool: True if the payment is completed, False otherwise.
        """
        return self.status == PaymentStatus.COMPLETED

    def is_failed(self) -> bool:
        """
        Check if payment is failed.
        
        Returns:
            bool: True if the payment is failed, False otherwise.
        """
        return self.status == PaymentStatus.FAILED

    def is_cancelled(self) -> bool:
        """
        Check if payment is cancelled.
        
        Returns:
            bool: True if the payment is cancelled, False otherwise.
        """
        return self.status == PaymentStatus.CANCELLED

    def is_refunded(self) -> bool:
        """
        Check if payment is refunded.
        
        Returns:
            bool: True if the payment is refunded, False otherwise.
        """
        return self.status == PaymentStatus.REFUNDED
