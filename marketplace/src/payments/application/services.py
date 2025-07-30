"""Application services for payments domain."""

from typing import List, Optional

from src.orders.domain.value_objects import OrderId
from src.shared.application.event_bus import EventBus
from src.shared.domain.exceptions import EntityNotFoundError
from src.users.domain.value_objects import UserId

from ..domain.entities import Payment, PaymentMethod
from ..domain.repositories import PaymentMethodRepository, PaymentRepository
from ..domain.value_objects import (
    Amount,
    PaymentId,
    PaymentMethodId,
    PaymentStatus,
)


class PaymentService:
    """Application service for payment operations."""

    def __init__(
        self,
        payment_repository: PaymentRepository,
        event_bus: EventBus,
    ):
        self.payment_repository = payment_repository
        self.event_bus = event_bus

    async def create_payment(
        self,
        order_id: str,
        amount: Amount,
        payment_method_id: str,
        description: Optional[str] = None,
    ) -> Payment:
        """Create a new payment."""
        payment = Payment(
            id=PaymentId(value=f"payment_{order_id}_{amount.value}"),
            order_id=OrderId(value=order_id),
            amount=amount,
            payment_method_id=PaymentMethodId(value=payment_method_id),
            description=description,
        )
        return await self.payment_repository.save(payment)

    async def get_payment(self, payment_id: str) -> Payment:
        """Get payment by ID."""
        payment = await self.payment_repository.get_by_id(PaymentId(value=payment_id))
        if not payment:
            raise EntityNotFoundError(f"Payment with ID {payment_id} not found")
        return payment

    async def get_payments_by_order(self, order_id: str) -> List[Payment]:
        """Get payments by order ID."""
        return await self.payment_repository.get_by_order_id(OrderId(value=order_id))

    async def get_payments_by_status(self, status: PaymentStatus) -> List[Payment]:
        """Get payments by status."""
        return await self.payment_repository.get_by_status(status)

    async def process_payment(self, payment_id: str) -> Payment:
        """Process payment."""
        payment = await self.get_payment(payment_id)
        payment.process()
        return await self.payment_repository.save(payment)

    async def complete_payment(
        self, payment_id: str, external_payment_id: Optional[str] = None
    ) -> Payment:
        """Complete payment."""
        payment = await self.get_payment(payment_id)
        payment.complete(external_payment_id)
        return await self.payment_repository.save(payment)

    async def fail_payment(self, payment_id: str, reason: str) -> Payment:
        """Fail payment."""
        payment = await self.get_payment(payment_id)
        payment.fail(reason)
        return await self.payment_repository.save(payment)

    async def cancel_payment(self, payment_id: str) -> Payment:
        """Cancel payment."""
        payment = await self.get_payment(payment_id)
        payment.cancel()
        return await self.payment_repository.save(payment)

    async def refund_payment(
        self, payment_id: str, refund_amount: Optional[Amount] = None
    ) -> Payment:
        """Refund payment."""
        payment = await self.get_payment(payment_id)
        payment.refund(refund_amount)
        return await self.payment_repository.save(payment)

    async def delete_payment(self, payment_id: str) -> bool:
        """Delete payment."""
        return await self.payment_repository.delete(PaymentId(value=payment_id))


class PaymentMethodService:
    """Application service for payment method operations."""

    def __init__(
        self,
        payment_method_repository: PaymentMethodRepository,
        event_bus: EventBus,
    ):
        self.payment_method_repository = payment_method_repository
        self.event_bus = event_bus

    async def create_payment_method(
        self,
        user_id: str,
        type: str,
        name: str,
        metadata: Optional[dict] = None,
        is_default: bool = False,
    ) -> PaymentMethod:
        """Create a new payment method."""
        if is_default:
            # Remove default status from other payment methods
            existing_methods = await self.payment_method_repository.get_by_user_id(
                UserId(value=user_id)
            )
            for method in existing_methods:
                if method.is_default:
                    method.remove_default()
                    await self.payment_method_repository.save(method)

        payment_method = PaymentMethod(
            id=PaymentMethodId(value=f"pm_{user_id}_{type}"),
            user_id=UserId(value=user_id),
            type=type,
            name=name,
            metadata=metadata or {},
            is_default=is_default,
        )
        return await self.payment_method_repository.save(payment_method)

    async def get_payment_method(self, payment_method_id: str) -> PaymentMethod:
        """Get payment method by ID."""
        payment_method = await self.payment_method_repository.get_by_id(
            PaymentMethodId(value=payment_method_id)
        )
        if not payment_method:
            raise EntityNotFoundError(
                f"Payment method with ID {payment_method_id} not found"
            )
        return payment_method

    async def get_payment_methods_by_user(self, user_id: str) -> List[PaymentMethod]:
        """Get payment methods by user ID."""
        return await self.payment_method_repository.get_by_user_id(
            UserId(value=user_id)
        )

    async def get_active_payment_methods_by_user(
        self, user_id: str
    ) -> List[PaymentMethod]:
        """Get active payment methods by user ID."""
        return await self.payment_method_repository.get_active_by_user_id(
            UserId(value=user_id)
        )

    async def get_default_payment_method(self, user_id: str) -> Optional[PaymentMethod]:
        """Get default payment method by user ID."""
        return await self.payment_method_repository.get_default_by_user_id(
            UserId(value=user_id)
        )

    async def activate_payment_method(self, payment_method_id: str) -> PaymentMethod:
        """Activate payment method."""
        payment_method = await self.get_payment_method(payment_method_id)
        payment_method.activate()
        return await self.payment_method_repository.save(payment_method)

    async def deactivate_payment_method(self, payment_method_id: str) -> PaymentMethod:
        """Deactivate payment method."""
        payment_method = await self.get_payment_method(payment_method_id)
        payment_method.deactivate()
        return await self.payment_method_repository.save(payment_method)

    async def set_as_default(self, payment_method_id: str) -> PaymentMethod:
        """Set payment method as default."""
        payment_method = await self.get_payment_method(payment_method_id)

        # Remove default status from other payment methods
        existing_methods = await self.payment_method_repository.get_by_user_id(
            payment_method.user_id
        )
        for method in existing_methods:
            if method.is_default and method.id != payment_method.id:
                method.remove_default()
                await self.payment_method_repository.save(method)

        payment_method.set_as_default()
        return await self.payment_method_repository.save(payment_method)

    async def update_metadata(
        self, payment_method_id: str, metadata: dict
    ) -> PaymentMethod:
        """Update payment method metadata."""
        payment_method = await self.get_payment_method(payment_method_id)
        payment_method.update_metadata(metadata)
        return await self.payment_method_repository.save(payment_method)

    async def delete_payment_method(self, payment_method_id: str) -> bool:
        """Delete payment method."""
        return await self.payment_method_repository.delete(
            PaymentMethodId(value=payment_method_id)
        )
