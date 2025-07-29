"""Entities for the orders domain."""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import Field

from src.shared.domain.entity import Entity

from .value_objects import OrderId, OrderItemId, OrderStatus, OrderTotal


class OrderItem(Entity[OrderItemId]):
    """Order item entity."""
    
    product_id: str = Field(description="Product identifier")
    product_name: str = Field(description="Product name")
    quantity: int = Field(description="Item quantity")
    unit_price: Decimal = Field(description="Unit price")
    total_price: Decimal = Field(description="Total price for this item")
    
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
    
    def update_quantity(self, new_quantity: int) -> "OrderItem":
        """Update item quantity."""
        if new_quantity <= 0:
            raise ValueError("Quantity must be positive")
        
        return OrderItem(
            id=self.id,
            product_id=self.product_id,
            product_name=self.product_name,
            quantity=new_quantity,
            unit_price=self.unit_price,
            total_price=self.unit_price * new_quantity,
        )


class Order(Entity[OrderId]):
    """Order entity."""
    
    customer_id: str = Field(description="Customer identifier")
    items: List[OrderItem] = Field(default_factory=list, description="Order items")
    status: OrderStatus = Field(default=OrderStatus.PENDING, description="Order status")
    total: OrderTotal = Field(description="Order total")
    shipping_address: str = Field(description="Shipping address")
    billing_address: str = Field(description="Billing address")
    notes: Optional[str] = Field(default=None, description="Order notes")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    
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
            id=OrderId(value=f"order_{customer_id}_{datetime.utcnow().timestamp()}"),
            customer_id=customer_id,
            items=[],
            total=OrderTotal.calculate(Decimal("0")),
            shipping_address=shipping_address,
            billing_address=billing_address,
            notes=notes,
        )
    
    def add_item(self, item: OrderItem) -> "Order":
        """Add item to order."""
        # Check if item already exists
        for existing_item in self.items:
            if existing_item.product_id == item.product_id:
                # Update quantity of existing item
                updated_item = existing_item.update_quantity(existing_item.quantity + item.quantity)
                new_items = [updated_item if i.product_id == item.product_id else i for i in self.items]
                break
        else:
            # Add new item
            new_items = self.items + [item]
        
        # Recalculate total
        subtotal = sum(item.total_price for item in new_items)
        new_total = OrderTotal.calculate(subtotal)
        
        return Order(
            id=self.id,
            customer_id=self.customer_id,
            items=new_items,
            status=self.status,
            total=new_total,
            shipping_address=self.shipping_address,
            billing_address=self.billing_address,
            notes=self.notes,
            created_at=self.created_at,
            updated_at=datetime.utcnow(),
        )
    
    def remove_item(self, product_id: str) -> "Order":
        """Remove item from order."""
        new_items = [item for item in self.items if item.product_id != product_id]
        
        # Recalculate total
        subtotal = sum(item.total_price for item in new_items)
        new_total = OrderTotal.calculate(subtotal)
        
        return Order(
            id=self.id,
            customer_id=self.customer_id,
            items=new_items,
            status=self.status,
            total=new_total,
            shipping_address=self.shipping_address,
            billing_address=self.billing_address,
            notes=self.notes,
            created_at=self.created_at,
            updated_at=datetime.utcnow(),
        )
    
    def update_status(self, new_status: OrderStatus) -> "Order":
        """Update order status."""
        return Order(
            id=self.id,
            customer_id=self.customer_id,
            items=self.items,
            status=new_status,
            total=self.total,
            shipping_address=self.shipping_address,
            billing_address=self.billing_address,
            notes=self.notes,
            created_at=self.created_at,
            updated_at=datetime.utcnow(),
        )
    
    def cancel(self) -> "Order":
        """Cancel order."""
        if self.status in [OrderStatus.DELIVERED, OrderStatus.REFUNDED]:
            raise ValueError("Cannot cancel delivered or refunded order")
        
        return self.update_status(OrderStatus.CANCELLED)
    
    def confirm(self) -> "Order":
        """Confirm order."""
        if self.status != OrderStatus.PENDING:
            raise ValueError("Only pending orders can be confirmed")
        
        return self.update_status(OrderStatus.CONFIRMED)
    
    def ship(self) -> "Order":
        """Ship order."""
        if self.status not in [OrderStatus.CONFIRMED, OrderStatus.PROCESSING]:
            raise ValueError("Only confirmed or processing orders can be shipped")
        
        return self.update_status(OrderStatus.SHIPPED)
    
    def deliver(self) -> "Order":
        """Mark order as delivered."""
        if self.status != OrderStatus.SHIPPED:
            raise ValueError("Only shipped orders can be delivered")
        
        return self.update_status(OrderStatus.DELIVERED)
    
    def refund(self) -> "Order":
        """Refund order."""
        if self.status not in [OrderStatus.CONFIRMED, OrderStatus.PROCESSING, OrderStatus.SHIPPED, OrderStatus.DELIVERED]:
            raise ValueError("Cannot refund order in current status")
        
        return self.update_status(OrderStatus.REFUNDED)