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
)


@dataclass
class PaymentMethod(Entity[PaymentMethodId]):
    """
    Payment method entity.
    
    This entity represents a payment method used for payments.
    
    Attributes:
        user_id (UserId): The ID of the user.
        type (str): The type of the payment method.
        name (str): The name of the payment method.
        is_active (bool): Whether the payment method is active.
        is_default (bool): Whether the payment method is the default.
        metadata (dict): The metadata of the payment method.
        created_at (datetime): The date and time the payment method was created.
        updated_at (datetime): The date and time the payment method was last updated.
    """

    user_id: UserId
    type: str  # "card", "bank_transfer", "digital_wallet", etc.
    name: str  # "Visa ****1234", "Sberbank", etc.
    is_active: bool = True
    is_default: bool = False
    metadata: dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __hash__(self) -> int:
        """Hash the payment method."""
        return hash(self.id)

    def deactivate(self) -> None:
        """Deactivate payment method."""
        self.is_active = False
        self.updated_at = datetime.now(UTC)

    def activate(self) -> None:
        """Activate payment method."""
        self.is_active = True
        self.updated_at = datetime.now(UTC)

    def set_as_default(self) -> None:
        """Set payment method as default."""
        self.is_default = True
        self.updated_at = datetime.now(UTC)

    def remove_default(self) -> None:
        """Remove default status from payment method."""
        self.is_default = False
        self.updated_at = datetime.now(UTC)

    def update_metadata(self, metadata: dict) -> None:
        """
        Update payment method metadata.
        
        Args:
            metadata (dict): The metadata to update.
        """
        self.metadata.update(metadata)
        self.updated_at = datetime.now(UTC)


@dataclass
class Payment(Entity[PaymentId]):
    """
    Payment entity.
    
    This entity represents a payment made for an order.
    
    Attributes:
        order_id (OrderId): The ID of the order.
        amount (Amount): The amount of the payment.
        payment_method_id (PaymentMethodId): The ID of the payment method.
        status (PaymentStatus): The status of the payment.
        description (Optional[str]): The description of the payment.
        external_payment_id (Optional[str]): The ID of the external payment.
        failure_reason (Optional[str]): The reason for the failure.
        processed_at (Optional[datetime]): The date and time the payment was processed.
        created_at (datetime): The date and time the payment was created.
        updated_at (datetime): The date and time the payment was last updated.
    """

    order_id: OrderId
    amount: Amount
    payment_method_id: PaymentMethodId
    status: PaymentStatus = PaymentStatus.PENDING
    description: Optional[str] = None
    external_payment_id: Optional[str] = None
    failure_reason: Optional[str] = None
    processed_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __hash__(self) -> int:
        """Hash the payment."""
        return hash(self.id)

    def process(self) -> None:
        """Mark payment as processing."""
        if self.status != PaymentStatus.PENDING:
            raise ValueError("Only pending payments can be processed")
        self.status = PaymentStatus.PROCESSING
        self.updated_at = datetime.now(UTC)

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
        self.processed_at = datetime.now(UTC)
        self.updated_at = datetime.now(UTC)

    def fail(self, reason: str) -> None:
        """
        Mark payment as failed.
        
        Args:
            reason (str): The reason for the failure.
        """
        if self.status not in [PaymentStatus.PENDING, PaymentStatus.PROCESSING]:
            raise ValueError("Only pending or processing payments can be failed")
        self.status = PaymentStatus.FAILED
        self.failure_reason = reason
        self.updated_at = datetime.now(UTC)

    def cancel(self) -> None:
        """Cancel payment."""
        if self.status not in [PaymentStatus.PENDING, PaymentStatus.PROCESSING]:
            raise ValueError("Only pending or processing payments can be cancelled")
        self.status = PaymentStatus.CANCELLED
        self.updated_at = datetime.now(UTC)

    def refund(self, refund_amount: Optional[Amount] = None) -> None:
        """
        Refund payment.
        
        Args:
            refund_amount (Optional[Amount]): The amount to refund.
        """
        if self.status != PaymentStatus.COMPLETED:
            raise ValueError("Only completed payments can be refunded")
        self.status = PaymentStatus.REFUNDED
        if refund_amount:
            # Store refund amount for audit purposes
            self.metadata = getattr(self, 'metadata', {})
            self.metadata['refund_amount'] = refund_amount.value
        self.updated_at = datetime.now(UTC)

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
