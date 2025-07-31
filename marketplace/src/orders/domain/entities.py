"""Entities for the orders domain."""

# Python imports
from dataclasses import dataclass, field
from datetime import UTC, datetime
from decimal import Decimal
from typing import List, Optional

# Local imports
from src.shared.domain.entity import Entity
from .value_objects import OrderId, OrderItemId, OrderStatus, OrderTotal


@dataclass
class OrderItem(Entity[OrderItemId]):
    """
    Order item entity.
    
    This entity represents an item in an order.
    
    Attributes:
        product_id (str): The ID of the product.
        product_name (str): The name of the product.
        quantity (int): The quantity of the product.
        unit_price (Decimal): The price of the product per unit.
        total_price (Decimal): The total price of the product.
    """

    product_id: str
    product_name: str
    quantity: int
    unit_price: Decimal
    total_price: Decimal

    def __hash__(self) -> int:
        """
        Hash the order item.
        
        Returns:
            int: The hash of the order item.
        """
        return hash(self.id)

    @classmethod
    def create(
        cls,
        product_id: str,
        product_name: str,
        quantity: int,
        unit_price: Decimal,
    ) -> "OrderItem":
        """
        Create a new order item.
        
        Args:
            product_id (str): The ID of the product.
            product_name (str): The name of the product.
            quantity (int): The quantity of the product.
            unit_price (Decimal): The price of the product per unit.

        Returns:
            OrderItem: The created order item.
        """
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
        if unit_price <= 0:
            raise ValueError("Unit price must be positive")

        total_price = unit_price * quantity

        return cls(
            id=OrderItemId(value=f"item_{product_id}_{quantity}"),
            product_id=product_id,
            product_name=product_name,
            quantity=quantity,
            unit_price=unit_price,
            total_price=total_price,
        )

    def update_quantity(self, new_quantity: int) -> None:
        """
        Update item quantity.
        
        Args:
            new_quantity (int): The new quantity of the product.
        """
        if new_quantity <= 0:
            raise ValueError("Quantity must be positive")

        self.quantity = new_quantity
        self.total_price = self.unit_price * new_quantity


@dataclass
class Order(Entity[OrderId]):
    """
    Order entity.
    
    This entity represents an order.
    
    Attributes:
        customer_id (str): The ID of the customer.
        total (OrderTotal): The total amount of the order.
        shipping_address (str): The shipping address of the order.
        billing_address (str): The billing address of the order.
        items (List[OrderItem]): The items in the order.
        status (OrderStatus): The status of the order.
        notes (Optional[str]): The notes of the order.
        created_at (datetime): The date and time the order was created.
        updated_at (datetime): The date and time the order was last updated.
    """

    customer_id: str
    total: OrderTotal
    shipping_address: str
    billing_address: str
    items: List[OrderItem] = field(default_factory=list)
    status: OrderStatus = OrderStatus.PENDING
    notes: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __hash__(self) -> int:
        """
        Hash the order.
        
        Returns:
            int: The hash of the order.
        """
        return hash(self.id)

    @classmethod
    def create(
        cls,
        customer_id: str,
        shipping_address: str,
        billing_address: str,
        notes: Optional[str] = None,
    ) -> "Order":
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
        return cls(
            id=OrderId(value=f"order_{customer_id}_{datetime.now(UTC).timestamp()}"),
            customer_id=customer_id,
            total=OrderTotal.calculate(Decimal("0")),
            shipping_address=shipping_address,
            billing_address=billing_address,
            notes=notes,
        )

    def add_item(self, item: OrderItem) -> None:
        """
        Add item to order.
        
        Args:
            item (OrderItem): The item to add to the order.
        """
        # Check if item already exists
        for existing_item in self.items:
            if existing_item.product_id == item.product_id:
                # Update quantity of existing item
                existing_item.update_quantity(existing_item.quantity + item.quantity)
                break
        else:
            # Add new item
            self.items.append(item)

        # Recalculate total
        self._recalculate_total()
        self.updated_at = datetime.now(UTC)

    def remove_item(self, product_id: str) -> None:
        """
        Remove item from order.
        
        Args:
            product_id (str): The ID of the product to remove from the order.
        """
        self.items = [item for item in self.items if item.product_id != product_id]

        # Recalculate total
        self._recalculate_total()
        self.updated_at = datetime.now(UTC)

    def update_status(self, new_status: OrderStatus) -> None:
        """
        Update order status.
        
        Args:
            new_status (OrderStatus): The new status of the order.
        """
        self.status = new_status
        self.updated_at = datetime.now(UTC)

    def cancel(self) -> None:
        """
        Cancel order.
        
        Raises:
            ValueError: If the order is already delivered or refunded.
        """
        if self.status in [OrderStatus.DELIVERED, OrderStatus.REFUNDED]:
            raise ValueError("Cannot cancel delivered or refunded order")

        self.update_status(OrderStatus.CANCELLED)

    def confirm(self) -> None:
        """
        Confirm order.
        
        Raises:
            ValueError: If the order is not pending.
        """
        if self.status != OrderStatus.PENDING:
            raise ValueError("Only pending orders can be confirmed")

        self.update_status(OrderStatus.CONFIRMED)

    def ship(self) -> None:
        """
        Ship order.
        
        Raises:
            ValueError: If the order is not confirmed or processing.
        """
        if self.status not in [OrderStatus.CONFIRMED, OrderStatus.PROCESSING]:
            raise ValueError("Only confirmed or processing orders can be shipped")

        self.update_status(OrderStatus.SHIPPED)

    def deliver(self) -> None:
        """
        Mark order as delivered.
        
        Raises:
            ValueError: If the order is not shipped.
        """
        if self.status != OrderStatus.SHIPPED:
            raise ValueError("Only shipped orders can be delivered")

        self.update_status(OrderStatus.DELIVERED)

    def refund(self) -> None:
        """
        Refund order.
        
        Raises:
            ValueError: If the order is not confirmed, processing, shipped, or delivered.
        """
        if self.status not in [
            OrderStatus.CONFIRMED,
            OrderStatus.PROCESSING,
            OrderStatus.SHIPPED,
            OrderStatus.DELIVERED
        ]:
            raise ValueError("Cannot refund order in current status")
        self.status = OrderStatus.REFUNDED
        self.updated_at = datetime.now(UTC)

    def _recalculate_total(self) -> None:
        """
        Recalculate order total.
        
        This method recalculates the total amount of the order based on the items in the order.
        """
        subtotal = sum(item.total_price for item in self.items)
        self.total = OrderTotal.calculate(subtotal)
