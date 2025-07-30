"""Entities for the orders domain."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from decimal import Decimal
from typing import List, Optional

from src.shared.domain.entity import Entity

from .value_objects import OrderId, OrderItemId, OrderStatus, OrderTotal


@dataclass
class OrderItem(Entity[OrderItemId]):
    """Order item entity."""

    product_id: str
    product_name: str
    quantity: int
    unit_price: Decimal
    total_price: Decimal

    def __hash__(self) -> int:
        return hash(self.id)

    @classmethod
    def create(
        cls,
        product_id: str,
        product_name: str,
        quantity: int,
        unit_price: Decimal,
    ) -> "OrderItem":
        """Create a new order item."""
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
        """Update item quantity."""
        if new_quantity <= 0:
            raise ValueError("Quantity must be positive")

        self.quantity = new_quantity
        self.total_price = self.unit_price * new_quantity


@dataclass
class Order(Entity[OrderId]):
    """Order entity."""

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
        return hash(self.id)

    @classmethod
    def create(
        cls,
        customer_id: str,
        shipping_address: str,
        billing_address: str,
        notes: Optional[str] = None,
    ) -> "Order":
        """Create a new order."""
        return cls(
            id=OrderId(value=f"order_{customer_id}_{datetime.now(UTC).timestamp()}"),
            customer_id=customer_id,
            total=OrderTotal.calculate(Decimal("0")),
            shipping_address=shipping_address,
            billing_address=billing_address,
            notes=notes,
        )

    def add_item(self, item: OrderItem) -> None:
        """Add item to order."""
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
        """Remove item from order."""
        self.items = [item for item in self.items if item.product_id != product_id]

        # Recalculate total
        self._recalculate_total()
        self.updated_at = datetime.now(UTC)

    def update_status(self, new_status: OrderStatus) -> None:
        """Update order status."""
        self.status = new_status
        self.updated_at = datetime.now(UTC)

    def cancel(self) -> None:
        """Cancel order."""
        if self.status in [OrderStatus.DELIVERED, OrderStatus.REFUNDED]:
            raise ValueError("Cannot cancel delivered or refunded order")

        self.update_status(OrderStatus.CANCELLED)

    def confirm(self) -> None:
        """Confirm order."""
        if self.status != OrderStatus.PENDING:
            raise ValueError("Only pending orders can be confirmed")

        self.update_status(OrderStatus.CONFIRMED)

    def ship(self) -> None:
        """Ship order."""
        if self.status not in [OrderStatus.CONFIRMED, OrderStatus.PROCESSING]:
            raise ValueError("Only confirmed or processing orders can be shipped")

        self.update_status(OrderStatus.SHIPPED)

    def deliver(self) -> None:
        """Mark order as delivered."""
        if self.status != OrderStatus.SHIPPED:
            raise ValueError("Only shipped orders can be delivered")

        self.update_status(OrderStatus.DELIVERED)

    def refund(self) -> None:
        """Refund order."""
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
        """Recalculate order total."""
        subtotal = sum(item.total_price for item in self.items)
        self.total = OrderTotal.calculate(subtotal)
