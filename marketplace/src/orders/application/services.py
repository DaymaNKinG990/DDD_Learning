"""Application services for the orders domain."""

from decimal import Decimal
from typing import List, Optional

from src.shared.domain.exceptions import EntityNotFoundError, InvalidOperationError

from ..domain.entities import Order, OrderItem
from ..domain.repositories import OrderItemRepository, OrderRepository
from ..domain.value_objects import OrderId, OrderStatus


class OrderService:
    """Order application service."""

    def __init__(
        self,
        order_repository: OrderRepository,
        order_item_repository: OrderItemRepository,
    ) -> None:
        """Initialize order service."""
        self._order_repository = order_repository
        self._order_item_repository = order_item_repository

    async def create_order(
        self,
        customer_id: str,
        shipping_address: str,
        billing_address: str,
        notes: Optional[str] = None,
    ) -> Order:
        """Create a new order."""
        order = Order.create(
            customer_id=customer_id,
            shipping_address=shipping_address,
            billing_address=billing_address,
            notes=notes,
        )

        return await self._order_repository.save(order)

    async def get_order(self, order_id: OrderId) -> Order:
        """Get order by ID."""
        order = await self._order_repository.get_by_id(order_id)
        if not order:
            raise EntityNotFoundError(f"Order with id {order_id} not found")
        return order

    async def add_item_to_order(
        self,
        order_id: OrderId,
        product_id: str,
        product_name: str,
        quantity: int,
        unit_price: Decimal,
    ) -> Order:
        """Add item to order."""
        order = await self.get_order(order_id)

        if order.status != OrderStatus.PENDING:
            raise InvalidOperationError("Can only add items to pending orders")

        item = OrderItem.create(
            product_id=product_id,
            product_name=product_name,
            quantity=quantity,
            unit_price=unit_price,
        )

        updated_order = order.add_item(item)
        return await self._order_repository.save(updated_order)

    async def remove_item_from_order(self, order_id: OrderId, product_id: str) -> Order:
        """Remove item from order."""
        order = await self.get_order(order_id)

        if order.status != OrderStatus.PENDING:
            raise InvalidOperationError("Can only remove items from pending orders")

        updated_order = order.remove_item(product_id)
        return await self._order_repository.save(updated_order)

    async def confirm_order(self, order_id: OrderId) -> Order:
        """Confirm order."""
        order = await self.get_order(order_id)
        confirmed_order = order.confirm()
        return await self._order_repository.save(confirmed_order)

    async def ship_order(self, order_id: OrderId) -> Order:
        """Ship order."""
        order = await self.get_order(order_id)
        shipped_order = order.ship()
        return await self._order_repository.save(shipped_order)

    async def deliver_order(self, order_id: OrderId) -> Order:
        """Mark order as delivered."""
        order = await self.get_order(order_id)
        delivered_order = order.deliver()
        return await self._order_repository.save(delivered_order)

    async def cancel_order(self, order_id: OrderId) -> Order:
        """Cancel order."""
        order = await self.get_order(order_id)
        cancelled_order = order.cancel()
        return await self._order_repository.save(cancelled_order)

    async def refund_order(self, order_id: OrderId) -> Order:
        """Refund order."""
        order = await self.get_order(order_id)
        refunded_order = order.refund()
        return await self._order_repository.save(refunded_order)

    async def get_customer_orders(self, customer_id: str) -> List[Order]:
        """Get all orders for a customer."""
        return await self._order_repository.get_by_customer(customer_id)

    async def get_pending_orders(self) -> List[Order]:
        """Get all pending orders."""
        return await self._order_repository.get_pending_orders()

    async def get_orders_by_status(self, status: str) -> List[Order]:
        """Get orders by status."""
        return await self._order_repository.get_orders_by_status(status)
