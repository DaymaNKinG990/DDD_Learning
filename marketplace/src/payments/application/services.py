"""Application services for payments domain."""

# Python imports
from typing import List, Optional
from typing_extensions import Any

# Local imports
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
    """
    Application service for payment operations.
    
    This service provides the application layer for the payments domain.
    """

    def __init__(
        self,
        payment_repository: PaymentRepository,
        event_bus: EventBus,
    ) -> None:
        """
        Initialize the payment service.
        
        Args:
            payment_repository (PaymentRepository): The repository for payments.
            event_bus (EventBus): The event bus for publishing events.
        """
        self.payment_repository = payment_repository
        self.event_bus = event_bus

    async def create_payment(
        self,
        order_id: str,
        amount: Amount,
        payment_method_id: str,
        description: Optional[str] = None,
    ) -> Payment:
        """
        Create a new payment.
        
        Args:
            order_id (str): The ID of the order.
            amount (Amount): The amount of the payment.
            payment_method_id (str): The ID of the payment method.
            description (Optional[str]): The description of the payment.

        Returns:
            Payment: The created payment.
        """
        payment = Payment(
            id=PaymentId(value=f"payment_{order_id}_{amount.value}"),
            order_id=OrderId(value=order_id),
            amount=amount,
            payment_method_id=PaymentMethodId(value=payment_method_id),
            description=description,
        )
        return await self.payment_repository.save(payment)

    async def get_payment(self, payment_id: str) -> Payment:
        """
        Get payment by ID.
        
        Args:
            payment_id (str): The ID of the payment to get.

        Returns:
            Payment: The payment.
        """
        payment = await self.payment_repository.get_by_id(PaymentId(value=payment_id))
        if not payment:
            raise EntityNotFoundError(f"Payment with ID {payment_id} not found")
        return payment

    async def get_payments_by_order(self, order_id: str) -> List[Payment]:
        """
        Get payments by order ID.
        
        Args:
            order_id (str): The ID of the order.

        Returns:
            List[Payment]: The payments for the order.
        """
        return await self.payment_repository.get_by_order_id(OrderId(value=order_id))

    async def get_payments_by_status(self, status: PaymentStatus) -> List[Payment]:
        """
        Get payments by status.
        
        Args:
            status (PaymentStatus): The status of the payments to get.

        Returns:
            List[Payment]: The payments with the given status.
        """
        return await self.payment_repository.get_by_status(status)

    async def process_payment(self, payment_id: str) -> Payment:
        """
        Process payment.
        
        Args:
            payment_id (str): The ID of the payment to process.

        Returns:
            Payment: The processed payment.
        """
        payment = await self.get_payment(payment_id)
        payment.process()
        return await self.payment_repository.save(payment)

    async def complete_payment(self, payment_id: str, external_payment_id: Optional[str] = None) -> Payment:
        """
        Complete payment.
        
        Args:
            payment_id (str): The ID of the payment to complete.
            external_payment_id (Optional[str]): The ID of the external payment.

        Returns:
            Payment: The completed payment.
        """
        payment = await self.get_payment(payment_id)
        payment.complete(external_payment_id)
        return await self.payment_repository.save(payment)

    async def fail_payment(self, payment_id: str, reason: str) -> Payment:
        """
        Fail payment.
        
        Args:
            payment_id (str): The ID of the payment to fail.
            reason (str): The reason for the failure.

        Returns:
            Payment: The failed payment.
        """
        payment = await self.get_payment(payment_id)
        payment.fail(reason)
        return await self.payment_repository.save(payment)

    async def cancel_payment(self, payment_id: str) -> Payment:
        """
        Cancel payment.
        
        Args:
            payment_id (str): The ID of the payment to cancel.

        Returns:
            Payment: The cancelled payment.
        """
        payment = await self.get_payment(payment_id)
        payment.cancel()
        return await self.payment_repository.save(payment)

    async def refund_payment(self, payment_id: str, refund_amount: Optional[Amount] = None) -> Payment:
        """
        Refund payment.
        
        Args:
            payment_id (str): The ID of the payment to refund.
            refund_amount (Optional[Amount]): The amount to refund.

        Returns:
            Payment: The refunded payment.
        """
        payment = await self.get_payment(payment_id)
        payment.refund(refund_amount)
        return await self.payment_repository.save(payment)

    async def delete_payment(self, payment_id: str) -> bool:
        """
        Delete payment.
        
        Args:
            payment_id (str): The ID of the payment to delete.

        Returns:
            bool: True if the payment was deleted, False otherwise.
        """
        return await self.payment_repository.delete(PaymentId(value=payment_id))


class PaymentMethodService:
    """
    Application service for payment method operations.
    
    This service provides the application layer for the payment methods domain.
    """

    def __init__(
        self,
        payment_method_repository: PaymentMethodRepository,
        event_bus: EventBus,
    ) -> None:
        """Initialize the payment method service.
        
        Args:
            payment_method_repository (PaymentMethodRepository): The repository for payment methods.
            event_bus (EventBus): The event bus for publishing events.
        """
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
        """
        Create a new payment method.
        
        Args:
            user_id (str): The ID of the user.
            type (str): The type of the payment method.
            name (str): The name of the payment method.
            metadata (Optional[dict]): The metadata of the payment method.
            is_default (bool): Whether the payment method is the default.

        Returns:
            PaymentMethod: The created payment method.
        """
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
        """
        Get payment method by ID.
        
        Args:
            payment_method_id (str): The ID of the payment method to get.

        Returns:
            PaymentMethod: The payment method.
        """
        payment_method = await self.payment_method_repository.get_by_id(
            PaymentMethodId(value=payment_method_id)
        )
        if not payment_method:
            raise EntityNotFoundError(
                f"Payment method with ID {payment_method_id} not found"
            )
        return payment_method

    async def get_payment_methods_by_user(self, user_id: str) -> List[PaymentMethod]:
        """
        Get payment methods by user ID.
        
        Args:
            user_id (str): The ID of the user.

        Returns:
            List[PaymentMethod]: The payment methods for the user.
        """
        return await self.payment_method_repository.get_by_user_id(
            UserId(value=user_id)
        )

    async def get_active_payment_methods_by_user(self, user_id: str) -> List[PaymentMethod]:
        """
        Get active payment methods by user ID.
        
        Args:
            user_id (str): The ID of the user.

        Returns:
            List[PaymentMethod]: The active payment methods for the user.
        """
        return await self.payment_method_repository.get_active_by_user_id(
            UserId(value=user_id)
        )

    async def get_default_payment_method(self, user_id: str) -> Optional[PaymentMethod]:
        """
        Get default payment method by user ID.
        
        Args:
            user_id (str): The ID of the user.

        Returns:
            Optional[PaymentMethod]: The default payment method for the user.
        """
        return await self.payment_method_repository.get_default_by_user_id(
            UserId(value=user_id)
        )

    async def activate_payment_method(self, payment_method_id: str) -> PaymentMethod:
        """
        Activate payment method.
        
        Args:
            payment_method_id (str): The ID of the payment method to activate.

        Returns:
            PaymentMethod: The activated payment method.
        """
        payment_method = await self.get_payment_method(payment_method_id)
        payment_method.activate()
        return await self.payment_method_repository.save(payment_method)

    async def deactivate_payment_method(self, payment_method_id: str) -> PaymentMethod:
        """
        Deactivate payment method.
        
        Args:
            payment_method_id (str): The ID of the payment method to deactivate.

        Returns:
            PaymentMethod: The deactivated payment method.
        """
        payment_method = await self.get_payment_method(payment_method_id)
        payment_method.deactivate()
        return await self.payment_method_repository.save(payment_method)

    async def set_as_default(self, payment_method_id: str) -> PaymentMethod:
        """
        Set payment method as default.
        
        Args:
            payment_method_id (str): The ID of the payment method to set as default.

        Returns:
            PaymentMethod: The payment method set as default.
        """
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

    async def update_metadata(self, payment_method_id: str, metadata: dict[str, Any]) -> PaymentMethod:
        """
        Update payment method metadata.
        
        Args:
            payment_method_id (str): The ID of the payment method to update.
            metadata (dict[str, Any]): The metadata to update.

        Returns:
            PaymentMethod: The updated payment method.
        """
        payment_method = await self.get_payment_method(payment_method_id)
        payment_method.update_metadata(metadata)
        return await self.payment_method_repository.save(payment_method)

    async def delete_payment_method(self, payment_method_id: str) -> bool:
        """
        Delete payment method.
        
        Args:
            payment_method_id (str): The ID of the payment method to delete.

        Returns:
            bool: True if the payment method was deleted, False otherwise.
        """
        return await self.payment_method_repository.delete(
            PaymentMethodId(value=payment_method_id)
        )
