"""Repository interfaces for the orders domain."""

from abc import ABC, abstractmethod
from typing import List, Optional

from .entities import Order, OrderItem
from .value_objects import OrderId, OrderItemId


class OrderRepository(ABC):
    """Order repository interface."""
    
    @abstractmethod
    async def save(self, order: Order) -> Order:
        """Save order."""
        pass
    
    @abstractmethod
    async def get_by_id(self, order_id: OrderId) -> Optional[Order]:
        """Get order by ID."""
        pass
    
    @abstractmethod
    async def get_by_customer(self, customer_id: str) -> List[Order]:
        """Get orders by customer."""
        pass
    
    @abstractmethod
    async def get_pending_orders(self) -> List[Order]:
        """Get all pending orders."""
        pass
    
    @abstractmethod
    async def get_orders_by_status(self, status: str) -> List[Order]:
        """Get orders by status."""
        pass
    
    @abstractmethod
    async def delete(self, order_id: OrderId) -> None:
        """Delete order."""
        pass


class OrderItemRepository(ABC):
    """Order item repository interface."""
    
    @abstractmethod
    async def save(self, order_item: OrderItem) -> OrderItem:
        """Save order item."""
        pass
    
    @abstractmethod
    async def get_by_id(self, order_item_id: OrderItemId) -> Optional[OrderItem]:
        """Get order item by ID."""
        pass
    
    @abstractmethod
    async def get_by_order(self, order_id: OrderId) -> List[OrderItem]:
        """Get items by order."""
        pass
    
    @abstractmethod
    async def delete(self, order_item_id: OrderItemId) -> None:
        """Delete order item."""
        pass