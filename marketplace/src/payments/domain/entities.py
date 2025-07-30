"""Entities for the payments domain."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Optional

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
    """Payment method entity."""

    user_id: UserId
    type: str  # "card", "bank_transfer", "digital_wallet", etc.
    name: str  # "Visa ****1234", "Sberbank", etc.
    is_active: bool = True
    is_default: bool = False
    metadata: dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __hash__(self) -> int:
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
        """Update payment method metadata."""
        self.metadata.update(metadata)
        self.updated_at = datetime.now(UTC)


@dataclass
class Payment(Entity[PaymentId]):
    """Payment entity."""

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
        return hash(self.id)

    def process(self) -> None:
        """Mark payment as processing."""
        if self.status != PaymentStatus.PENDING:
            raise ValueError("Only pending payments can be processed")
        self.status = PaymentStatus.PROCESSING
        self.updated_at = datetime.now(UTC)

    def complete(self, external_payment_id: Optional[str] = None) -> None:
        """Mark payment as completed."""
        if self.status not in [PaymentStatus.PENDING, PaymentStatus.PROCESSING]:
            raise ValueError("Only pending or processing payments can be completed")
        self.status = PaymentStatus.COMPLETED
        self.external_payment_id = external_payment_id
        self.processed_at = datetime.now(UTC)
        self.updated_at = datetime.now(UTC)

    def fail(self, reason: str) -> None:
        """Mark payment as failed."""
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
        """Refund payment."""
        if self.status != PaymentStatus.COMPLETED:
            raise ValueError("Only completed payments can be refunded")
        self.status = PaymentStatus.REFUNDED
        self.updated_at = datetime.now(UTC)

    def is_completed(self) -> bool:
        """Check if payment is completed."""
        return self.status == PaymentStatus.COMPLETED

    def is_failed(self) -> bool:
        """Check if payment is failed."""
        return self.status == PaymentStatus.FAILED

    def is_cancelled(self) -> bool:
        """Check if payment is cancelled."""
        return self.status == PaymentStatus.CANCELLED

    def is_refunded(self) -> bool:
        """Check if payment is refunded."""
        return self.status == PaymentStatus.REFUNDED
