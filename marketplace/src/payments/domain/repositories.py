"""Repository interfaces for payments domain."""

from abc import ABC, abstractmethod
from typing import List, Optional

from src.orders.domain.value_objects import OrderId
from src.users.domain.value_objects import UserId

from .entities import Payment, PaymentMethod
from .value_objects import PaymentId, PaymentMethodId, PaymentStatus


class PaymentRepository(ABC):
    """Repository interface for Payment entity."""

    @abstractmethod
    async def save(self, payment: Payment) -> Payment:
        """Save payment."""
        pass

    @abstractmethod
    async def get_by_id(self, payment_id: PaymentId) -> Optional[Payment]:
        """Get payment by ID."""
        pass

    @abstractmethod
    async def get_by_order_id(self, order_id: OrderId) -> List[Payment]:
        """Get payments by order ID."""
        pass

    @abstractmethod
    async def get_by_status(self, status: PaymentStatus) -> List[Payment]:
        """Get payments by status."""
        pass

    @abstractmethod
    async def get_by_external_id(self, external_payment_id: str) -> Optional[Payment]:
        """Get payment by external payment ID."""
        pass

    @abstractmethod
    async def delete(self, payment_id: PaymentId) -> bool:
        """Delete payment by ID."""
        pass


class PaymentMethodRepository(ABC):
    """Repository interface for PaymentMethod entity."""

    @abstractmethod
    async def save(self, payment_method: PaymentMethod) -> PaymentMethod:
        """Save payment method."""
        pass

    @abstractmethod
    async def get_by_id(
        self, payment_method_id: PaymentMethodId
    ) -> Optional[PaymentMethod]:
        """Get payment method by ID."""
        pass

    @abstractmethod
    async def get_by_user_id(self, user_id: UserId) -> List[PaymentMethod]:
        """Get payment methods by user ID."""
        pass

    @abstractmethod
    async def get_default_by_user_id(self, user_id: UserId) -> Optional[PaymentMethod]:
        """Get default payment method by user ID."""
        pass

    @abstractmethod
    async def get_active_by_user_id(self, user_id: UserId) -> List[PaymentMethod]:
        """Get active payment methods by user ID."""
        pass

    @abstractmethod
    async def delete(self, payment_method_id: PaymentMethodId) -> bool:
        """Delete payment method by ID."""
        pass
