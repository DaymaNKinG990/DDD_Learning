"""Repository interfaces for payments domain."""

# Python imports
from abc import ABC, abstractmethod
from typing import List, Optional

# Local imports
from src.orders.domain.value_objects import OrderId
from src.users.domain.value_objects import UserId
from .entities import Payment, PaymentMethod
from .value_objects import PaymentId, PaymentMethodId, PaymentStatus


class PaymentRepository(ABC):
    """
    Repository interface for Payment entity.
    
    This interface defines the methods for interacting with the Payment entity.
    """

    @abstractmethod
    async def save(self, payment: Payment) -> Payment:
        """
        Save payment.
        
        Args:
            payment (Payment): The payment to save.

        Returns:
            Payment: The saved payment.
        """
        pass

    @abstractmethod
    async def get_by_id(self, payment_id: PaymentId) -> Optional[Payment]:
        """
        Get payment by ID.
        
        Args:
            payment_id (PaymentId): The ID of the payment to get.

        Returns:
            Optional[Payment]: The payment if found, None otherwise.
        """
        pass

    @abstractmethod
    async def get_by_order_id(self, order_id: OrderId) -> List[Payment]:
        """
        Get payments by order ID.
        
        Args:
            order_id (OrderId): The ID of the order.

        Returns:
            List[Payment]: The payments for the order.
        """
        pass

    @abstractmethod
    async def get_by_status(self, status: PaymentStatus) -> List[Payment]:
        """
        Get payments by status.
        
        Args:
            status (PaymentStatus): The status of the payments to get.

        Returns:
            List[Payment]: The payments with the given status.
        """
        pass

    @abstractmethod
    async def get_by_external_id(self, external_payment_id: str) -> Optional[Payment]:
        """
        Get payment by external payment ID.
        
        Args:
            external_payment_id (str): The ID of the external payment.

        Returns:
            Optional[Payment]: The payment if found, None otherwise.
        """
        pass

    @abstractmethod
    async def delete(self, payment_id: PaymentId) -> bool:
        """
        Delete payment by ID.
        
        Args:
            payment_id (PaymentId): The ID of the payment to delete.

        Returns:
            bool: True if the payment was deleted, False otherwise.
        """
        pass


class PaymentMethodRepository(ABC):
    """
    Repository interface for PaymentMethod entity.
    
    This interface defines the methods for interacting with the PaymentMethod entity.
    """

    @abstractmethod
    async def save(self, payment_method: PaymentMethod) -> PaymentMethod:
        """
        Save payment method.
        
        Args:
            payment_method (PaymentMethod): The payment method to save.

        Returns:
            PaymentMethod: The saved payment method.
        """
        pass

    @abstractmethod
    async def get_by_id(self, payment_method_id: PaymentMethodId) -> Optional[PaymentMethod]:
        """
        Get payment method by ID.
        
        Args:
            payment_method_id (PaymentMethodId): The ID of the payment method to get.

        Returns:
            Optional[PaymentMethod]: The payment method if found, None otherwise.
        """
        pass

    @abstractmethod
    async def get_by_user_id(self, user_id: UserId) -> List[PaymentMethod]:
        """
        Get payment methods by user ID.
        
        Args:
            user_id (UserId): The ID of the user.

        Returns:
            List[PaymentMethod]: The payment methods for the user.
        """
        pass

    @abstractmethod
    async def get_default_by_user_id(self, user_id: UserId) -> Optional[PaymentMethod]:
        """
        Get default payment method by user ID.
        
        Args:
            user_id (UserId): The ID of the user.

        Returns:
            Optional[PaymentMethod]: The default payment method for the user.
        """
        pass

    @abstractmethod
    async def get_active_by_user_id(self, user_id: UserId) -> List[PaymentMethod]:
        """
        Get active payment methods by user ID.
        
        Args:
            user_id (UserId): The ID of the user.

        Returns:
            List[PaymentMethod]: The active payment methods for the user.
        """
        pass

    @abstractmethod
    async def delete(self, payment_method_id: PaymentMethodId) -> bool:
        """
        Delete payment method by ID.
        
        Args:
            payment_method_id (PaymentMethodId): The ID of the payment method to delete.

        Returns:
            bool: True if the payment method was deleted, False otherwise.
        """
        pass
