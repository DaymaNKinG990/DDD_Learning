"""In-memory repository implementations for payments domain."""

from typing import Dict, List, Optional

from src.infrastructure.repositories import InMemoryRepository
from src.orders.domain.value_objects import OrderId
from src.users.domain.value_objects import UserId

from ..domain.entities import Payment, PaymentMethod
from ..domain.repositories import PaymentMethodRepository, PaymentRepository
from ..domain.value_objects import PaymentId, PaymentMethodId, PaymentStatus


class InMemoryPaymentRepository(
    InMemoryRepository[Payment, PaymentId], PaymentRepository
):
    """In-memory implementation of PaymentRepository."""

    def __init__(self):
        super().__init__()
        self._payments_by_order_id: Dict[str, List[Payment]] = {}
        self._payments_by_status: Dict[PaymentStatus, List[Payment]] = {}
        self._payments_by_external_id: Dict[str, Payment] = {}

    async def save(self, payment: Payment) -> Payment:
        """Save payment."""
        saved_payment = await super().save(payment)

        # Update indexes
        order_id_str = str(payment.order_id)
        if order_id_str not in self._payments_by_order_id:
            self._payments_by_order_id[order_id_str] = []
        if payment not in self._payments_by_order_id[order_id_str]:
            self._payments_by_order_id[order_id_str].append(payment)

        if payment.status not in self._payments_by_status:
            self._payments_by_status[payment.status] = []
        if payment not in self._payments_by_status[payment.status]:
            self._payments_by_status[payment.status].append(payment)

        if payment.external_payment_id:
            self._payments_by_external_id[payment.external_payment_id] = payment

        return saved_payment

    async def get_by_order_id(self, order_id: OrderId) -> List[Payment]:
        """Get payments by order ID."""
        return self._payments_by_order_id.get(str(order_id), [])

    async def get_by_status(self, status: PaymentStatus) -> List[Payment]:
        """Get payments by status."""
        return self._payments_by_status.get(status, [])

    async def get_by_external_id(self, external_payment_id: str) -> Optional[Payment]:
        """Get payment by external payment ID."""
        return self._payments_by_external_id.get(external_payment_id)

    async def delete(self, payment_id: PaymentId) -> bool:
        """Delete payment by ID."""
        payment = await self.get_by_id(payment_id)
        if payment:
            # Remove from indexes
            order_id_str = str(payment.order_id)
            if order_id_str in self._payments_by_order_id:
                self._payments_by_order_id[order_id_str] = [
                    p for p in self._payments_by_order_id[order_id_str]
                    if p.id != payment_id
                ]

            if payment.status in self._payments_by_status:
                self._payments_by_status[payment.status] = [
                    p for p in self._payments_by_status[payment.status]
                    if p.id != payment_id
                ]

            if payment.external_payment_id:
                self._payments_by_external_id.pop(payment.external_payment_id, None)

            return await super().delete(payment_id)
        return False


class InMemoryPaymentMethodRepository(
    InMemoryRepository[PaymentMethod, PaymentMethodId], PaymentMethodRepository
):
    """In-memory implementation of PaymentMethodRepository."""

    def __init__(self):
        super().__init__()
        self._payment_methods_by_user_id: Dict[str, List[PaymentMethod]] = {}
        self._default_payment_methods_by_user_id: Dict[str, PaymentMethod] = {}

    async def save(self, payment_method: PaymentMethod) -> PaymentMethod:
        """Save payment method."""
        saved_payment_method = await super().save(payment_method)

        # Update indexes
        user_id_str = str(payment_method.user_id)
        if user_id_str not in self._payment_methods_by_user_id:
            self._payment_methods_by_user_id[user_id_str] = []
        if payment_method not in self._payment_methods_by_user_id[user_id_str]:
            self._payment_methods_by_user_id[user_id_str].append(payment_method)

        if payment_method.is_default:
            self._default_payment_methods_by_user_id[user_id_str] = payment_method

        return saved_payment_method

    async def get_by_user_id(self, user_id: UserId) -> List[PaymentMethod]:
        """Get payment methods by user ID."""
        return self._payment_methods_by_user_id.get(str(user_id), [])

    async def get_default_by_user_id(self, user_id: UserId) -> Optional[PaymentMethod]:
        """Get default payment method by user ID."""
        return self._default_payment_methods_by_user_id.get(str(user_id))

    async def get_active_by_user_id(self, user_id: UserId) -> List[PaymentMethod]:
        """Get active payment methods by user ID."""
        user_methods = self._payment_methods_by_user_id.get(str(user_id), [])
        return [method for method in user_methods if method.is_active]

    async def delete(self, payment_method_id: PaymentMethodId) -> bool:
        """Delete payment method by ID."""
        payment_method = await self.get_by_id(payment_method_id)
        if payment_method:
            # Remove from indexes
            user_id_str = str(payment_method.user_id)
            if user_id_str in self._payment_methods_by_user_id:
                self._payment_methods_by_user_id[user_id_str] = [
                    pm for pm in self._payment_methods_by_user_id[user_id_str]
                    if pm.id != payment_method_id
                ]

            if user_id_str in self._default_payment_methods_by_user_id:
                default_method = self._default_payment_methods_by_user_id[user_id_str]
                if default_method.id == payment_method_id:
                    del self._default_payment_methods_by_user_id[user_id_str]

            return await super().delete(payment_method_id)
        return False
