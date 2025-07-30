"""In-memory repository implementations for orders domain."""

from typing import Dict, List, Optional

from src.shared.infrastructure.repositories import InMemoryRepository
from src.orders.domain.entities import Order, OrderItem
from src.orders.domain.repositories import OrderItemRepository, OrderRepository
from src.orders.domain.value_objects import OrderId, OrderItemId


class InMemoryOrderRepository(InMemoryRepository[Order], OrderRepository):
    """In-memory implementation of OrderRepository."""

    def __init__(self):
        super().__init__()
        self._orders: Dict[str, Order] = {}

    async def save(self, order: Order) -> Order:
        """Save order to in-memory storage."""
        self._orders[str(order.id)] = order
        return order

    async def get_by_id(self, order_id: OrderId) -> Optional[Order]:
        """Get order by ID."""
        return self._orders.get(str(order_id))

    async def get_all(self) -> List[Order]:
        """Get all orders."""
        return list(self._orders.values())

    async def get_by_customer(self, customer_id: str) -> List[Order]:
        """Get orders by customer ID."""
        return [
            order for order in self._orders.values()
            if order.customer_id == customer_id
        ]

    async def delete(self, order_id: OrderId) -> bool:
        """Delete order by ID."""
        if str(order_id) in self._orders:
            del self._orders[str(order_id)]
            return True
        return False


class InMemoryOrderItemRepository(
    InMemoryRepository[OrderItem], OrderItemRepository
):
    """In-memory implementation of OrderItemRepository."""

    def __init__(self):
        super().__init__()
        self._order_items: Dict[str, OrderItem] = {}

    async def save(self, order_item: OrderItem) -> OrderItem:
        """Save order item to in-memory storage."""
        self._order_items[str(order_item.id)] = order_item
        return order_item

    async def get_by_id(self, order_item_id: OrderItemId) -> Optional[OrderItem]:
        """Get order item by ID."""
        return self._order_items.get(str(order_item_id))

    async def get_all(self) -> List[OrderItem]:
        """Get all order items."""
        return list(self._order_items.values())

    async def get_by_order(self, order_id: OrderId) -> List[OrderItem]:
        """Get order items by order ID."""
        return [
            item for item in self._order_items.values()
            if item.order_id == order_id
        ]

    async def delete(self, order_item_id: OrderItemId) -> bool:
        """Delete order item by ID."""
        if str(order_item_id) in self._order_items:
            del self._order_items[str(order_item_id)]
            return True
        return False
