"""In-memory repository implementations for orders domain."""

# Python imports
from typing import Dict, List, Optional

# Local imports
from src.shared.infrastructure.repositories import InMemoryRepository
from src.orders.domain.entities import Order, OrderItem
from src.orders.domain.repositories import OrderItemRepository, OrderRepository
from src.orders.domain.value_objects import OrderId, OrderItemId


class InMemoryOrderRepository(InMemoryRepository[Order], OrderRepository):
    """In-memory implementation of OrderRepository.
    
    This class provides an in-memory implementation of the OrderRepository interface.
    """

    def __init__(self) -> None:
        """Initialize the in-memory order repository."""
        super().__init__()
        self._orders: Dict[str, Order] = {}

    async def save(self, order: Order) -> Order:
        """
        Save order to in-memory storage.
        
        Args:
            order (Order): The order to save.

        Returns:
            Order: The saved order.
        """
        self._orders[str(order.id)] = order
        return order

    async def get_by_id(self, order_id: OrderId) -> Optional[Order]:
        """
        Get order by ID.
        
        Args:
            order_id (OrderId): The ID of the order to get.

        Returns:
            Optional[Order]: The order if found, None otherwise.
        """
        return self._orders.get(str(order_id))

    async def get_all(self) -> List[Order]:
        """
        Get all orders.
        
        Returns:
            List[Order]: The orders.
        """
        return list(self._orders.values())

    async def get_by_customer(self, customer_id: str) -> List[Order]:
        """
        Get orders by customer ID.
        
        Args:
            customer_id (str): The ID of the customer.

        Returns:
            List[Order]: The orders for the customer.
        """
        return [
            order for order in self._orders.values()
            if order.customer_id == customer_id
        ]

    async def delete(self, order_id: OrderId) -> bool:
        """
        Delete order by ID.
        
        Args:
            order_id (OrderId): The ID of the order to delete.

        Returns:
            bool: True if the order was deleted, False otherwise.
        """
        if str(order_id) in self._orders:
            del self._orders[str(order_id)]
            return True
        return False


class InMemoryOrderItemRepository(InMemoryRepository[OrderItem], OrderItemRepository):
    """
    In-memory implementation of OrderItemRepository.
    
    This class provides an in-memory implementation of the OrderItemRepository interface.
    """

    def __init__(self) -> None:
        """Initialize the in-memory order item repository."""
        super().__init__()
        self._order_items: Dict[str, OrderItem] = {}

    async def save(self, order_item: OrderItem) -> OrderItem:
        """
        Save order item to in-memory storage.
        
        Args:
            order_item (OrderItem): The order item to save.

        Returns:
            OrderItem: The saved order item.
        """
        self._order_items[str(order_item.id)] = order_item
        return order_item

    async def get_by_id(self, order_item_id: OrderItemId) -> Optional[OrderItem]:
        """
        Get order item by ID.
        
        Args:
            order_item_id (OrderItemId): The ID of the order item to get.

        Returns:
            Optional[OrderItem]: The order item if found, None otherwise.
        """
        return self._order_items.get(str(order_item_id))

    async def get_all(self) -> List[OrderItem]:
        """
        Get all order items.
        
        Returns:
            List[OrderItem]: The order items.
        """
        return list(self._order_items.values())

    async def get_by_order(self, order_id: OrderId) -> List[OrderItem]:
        """
        Get order items by order ID.
        
        Args:
            order_id (OrderId): The ID of the order.

        Returns:
            List[OrderItem]: The items for the order.
        """
        return [
            item for item in self._order_items.values()
            if item.order_id == order_id
        ]

    async def delete(self, order_item_id: OrderItemId) -> bool:
        """
        Delete order item by ID.
        
        Args:
            order_item_id (OrderItemId): The ID of the order item to delete.

        Returns:
            bool: True if the order item was deleted, False otherwise.
        """
        if str(order_item_id) in self._order_items:
            del self._order_items[str(order_item_id)]
            return True
        return False
