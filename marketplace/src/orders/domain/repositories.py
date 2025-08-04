"""Repository interfaces for the orders domain."""

# Python imports
from abc import ABC, abstractmethod
from typing import List, Optional

# Local imports
from .entities import Order, OrderItem
from .value_objects import OrderId, OrderItemId


class OrderRepository(ABC):
    """
    Order repository interface.
    
    This interface defines the methods for managing orders in the domain.
    """

    @abstractmethod
    async def save(self, order: Order) -> Order:
        """
        Save an order.
        
        Args:
            order (Order): The order to save.

        Returns:
            Order: The saved order.
        """
        pass

    @abstractmethod
    async def get_by_id(self, order_id: OrderId) -> Optional[Order]:
        """
        Get an order by its ID.
        
        Args:
            order_id (OrderId): The ID of the order to get.

        Returns:
            Optional[Order]: The order if found, None otherwise.
        """
        pass

    @abstractmethod
    async def get_by_customer(self, customer_id: str) -> List[Order]:
        """
        Get all orders for a customer.
        
        Args:
            customer_id (str): The ID of the customer.

        Returns:
            List[Order]: The orders for the customer.
        """
        pass

    @abstractmethod
    async def get_by_customer_id(self, customer_id: str) -> List[Order]:
        """
        Get all orders for a customer by customer ID.
        
        Args:
            customer_id (str): The ID of the customer.

        Returns:
            List[Order]: The orders for the customer.
        """
        pass

    @abstractmethod
    async def get_pending_orders(self) -> List[Order]:
        """
        Get all pending orders.
        
        Returns:
            List[Order]: The pending orders.
        """
        pass

    @abstractmethod
    async def get_orders_by_status(self, status: str) -> List[Order]:
        """
        Get all orders by status.
        
        Args:
            status (str): The status of the orders to get.

        Returns:
            List[Order]: The orders with the given status.
        """
        pass

    @abstractmethod
    async def get_orders_by_date_range(self, start_date, end_date) -> List[Order]:
        """
        Get all orders within a date range.
        
        Args:
            start_date: The start date for the range.
            end_date: The end date for the range.

        Returns:
            List[Order]: The orders within the date range.
        """
        pass

    @abstractmethod
    async def delete(self, order_id: OrderId) -> None:
        """
        Delete an order.
        
        Args:
            order_id (OrderId): The ID of the order to delete.
        """
        pass


class OrderItemRepository(ABC):
    """
    Order item repository interface.
    
    This interface defines the methods for managing order items in the domain.
    """

    @abstractmethod
    async def save(self, order_item: OrderItem) -> OrderItem:
        """
        Save an order item.
        
        Args:
            order_item (OrderItem): The order item to save.

        Returns:
            OrderItem: The saved order item.
        """
        pass

    @abstractmethod
    async def get_by_id(self, order_item_id: OrderItemId) -> Optional[OrderItem]:
        """
        Get an order item by its ID.
        
        Args:
            order_item_id (OrderItemId): The ID of the order item to get.

        Returns:
            Optional[OrderItem]: The order item if found, None otherwise.
        """
        pass

    @abstractmethod
    async def get_by_order(self, order_id: OrderId) -> List[OrderItem]:
        """
        Get all items for an order.
        
        Args:
            order_id (OrderId): The ID of the order.

        Returns:
            List[OrderItem]: The items for the order.
        """
        pass

    @abstractmethod
    async def delete(self, order_item_id: OrderItemId) -> None:
        """
        Delete an order item.
        
        Args:
            order_item_id (OrderItemId): The ID of the order item to delete.
        """
        pass
