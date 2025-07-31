"""Application services for the orders domain."""

# Python imports
from decimal import Decimal
from typing import List, Optional

# Local imports
from src.shared.domain.exceptions import EntityNotFoundError, InvalidOperationError
from ..domain.entities import Order, OrderItem
from ..domain.repositories import OrderItemRepository, OrderRepository
from ..domain.value_objects import OrderId, OrderStatus


class OrderService:
    """
    Order application service.
    
    This service provides the application layer for the orders domain.
    """

    def __init__(
        self,
        order_repository: OrderRepository,
        order_item_repository: OrderItemRepository,
    ) -> None:
        """
        Initialize order service.
        
        Args:
            order_repository (OrderRepository): The repository for orders.
            order_item_repository (OrderItemRepository): The repository for order items.
        """
        self._order_repository = order_repository
        self._order_item_repository = order_item_repository

    async def create_order(
        self,
        customer_id: str,
        shipping_address: str,
        billing_address: str,
        notes: Optional[str] = None,
    ) -> Order:
        """
        Create a new order.
        
        Args:
            customer_id (str): The ID of the customer.
            shipping_address (str): The shipping address of the order.
            billing_address (str): The billing address of the order.
            notes (Optional[str]): The notes of the order.

        Returns:
            Order: The created order.
        """
        order = Order.create(
            customer_id=customer_id,
            shipping_address=shipping_address,
            billing_address=billing_address,
            notes=notes,
        )

        return await self._order_repository.save(order)

    async def get_order(self, order_id: OrderId) -> Order:
        """
        Get order by ID.
        
        Args:
            order_id (OrderId): The ID of the order to get.

        Returns:
            Order: The order.
        """
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
        """
        Add item to order.
        
        Args:
            order_id (OrderId): The ID of the order.
            product_id (str): The ID of the product.
            product_name (str): The name of the product.
            quantity (int): The quantity of the product.
            unit_price (Decimal): The price of the product per unit.
        """
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
        """
        Remove item from order.
        
        Args:
            order_id (OrderId): The ID of the order.
            product_id (str): The ID of the product.

        Returns:
            Order: The updated order.
        """
        order = await self.get_order(order_id)

        if order.status != OrderStatus.PENDING:
            raise InvalidOperationError("Can only remove items from pending orders")

        updated_order = order.remove_item(product_id)
        return await self._order_repository.save(updated_order)

    async def confirm_order(self, order_id: OrderId) -> Order:
        """
        Confirm order.
        
        Args:
            order_id (OrderId): The ID of the order to confirm.

        Returns:
            Order: The confirmed order.
        """
        order = await self.get_order(order_id)
        confirmed_order = order.confirm()
        return await self._order_repository.save(confirmed_order)

    async def ship_order(self, order_id: OrderId) -> Order:
        """
        Ship order.
        
        Args:
            order_id (OrderId): The ID of the order to ship.

        Returns:
            Order: The shipped order.
        """
        order = await self.get_order(order_id)
        shipped_order = order.ship()
        return await self._order_repository.save(shipped_order)

    async def deliver_order(self, order_id: OrderId) -> Order:
        """
        Mark order as delivered.
        
        Args:
            order_id (OrderId): The ID of the order to deliver.

        Returns:
            Order: The delivered order.
        """
        order = await self.get_order(order_id)
        delivered_order = order.deliver()
        return await self._order_repository.save(delivered_order)

    async def cancel_order(self, order_id: OrderId) -> Order:
        """
        Cancel order.
        
        Args:
            order_id (OrderId): The ID of the order to cancel.

        Returns:
            Order: The cancelled order.
        """
        order = await self.get_order(order_id)
        cancelled_order = order.cancel()
        return await self._order_repository.save(cancelled_order)

    async def refund_order(self, order_id: OrderId) -> Order:
        """
        Refund order.
        
        Args:
            order_id (OrderId): The ID of the order to refund.

        Returns:
            Order: The refunded order.
        """
        order = await self.get_order(order_id)
        refunded_order = order.refund()
        return await self._order_repository.save(refunded_order)

    async def get_customer_orders(self, customer_id: str) -> List[Order]:
        """
        Get all orders for a customer.
        
        Args:
            customer_id (str): The ID of the customer.

        Returns:
            List[Order]: The orders for the customer.
        """
        return await self._order_repository.get_by_customer(customer_id)

    async def get_pending_orders(self) -> List[Order]:
        """
        Get all pending orders.
        
        Returns:
            List[Order]: The pending orders.
        """
        return await self._order_repository.get_pending_orders()

    async def get_orders_by_status(self, status: str) -> List[Order]:
        """
        Get orders by status.
        
        Args:
            status (str): The status of the orders to get.

        Returns:
            List[Order]: The orders with the given status.
        """
        return await self._order_repository.get_orders_by_status(status)
