"""Domain events for orders bounded context."""

from typing import Any, Dict, Optional

from src.shared.domain.events import DomainEvent


class OrderCreated(DomainEvent):
    """Event raised when an order is created."""

    order_id: str
    customer_id: str
    total: str
    shipping_address: str
    billing_address: str
    notes: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": str(self.event_id),
            "event_type": self.event_type,
            "aggregate_id": self.aggregate_id,
            "occurred_on": self.occurred_on.isoformat(),
            "version": self.version,
            "order_id": self.order_id,
            "customer_id": self.customer_id,
            "total": self.total,
            "shipping_address": self.shipping_address,
            "billing_address": self.billing_address,
            "notes": self.notes,
        }


class OrderItemAdded(DomainEvent):
    """Event raised when an item is added to an order."""

    order_id: str
    product_id: str
    product_name: str
    quantity: int
    unit_price: str
    total: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": str(self.event_id),
            "event_type": self.event_type,
            "aggregate_id": self.aggregate_id,
            "occurred_on": self.occurred_on.isoformat(),
            "version": self.version,
            "order_id": self.order_id,
            "product_id": self.product_id,
            "product_name": self.product_name,
            "quantity": self.quantity,
            "unit_price": self.unit_price,
            "total": self.total,
        }


class OrderItemRemoved(DomainEvent):
    """Event raised when an item is removed from an order."""

    order_id: str
    product_id: str
    quantity: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": str(self.event_id),
            "event_type": self.event_type,
            "aggregate_id": self.aggregate_id,
            "occurred_on": self.occurred_on.isoformat(),
            "version": self.version,
            "order_id": self.order_id,
            "product_id": self.product_id,
            "quantity": self.quantity,
        }


class OrderConfirmed(DomainEvent):
    """Event raised when an order is confirmed."""

    order_id: str
    customer_id: str
    total: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": str(self.event_id),
            "event_type": self.event_type,
            "aggregate_id": self.aggregate_id,
            "occurred_on": self.occurred_on.isoformat(),
            "version": self.version,
            "order_id": self.order_id,
            "customer_id": self.customer_id,
            "total": self.total,
        }


class OrderShipped(DomainEvent):
    """Event raised when an order is shipped."""

    order_id: str
    tracking_number: Optional[str] = None
    shipping_method: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": str(self.event_id),
            "event_type": self.event_type,
            "aggregate_id": self.aggregate_id,
            "occurred_on": self.occurred_on.isoformat(),
            "version": self.version,
            "order_id": self.order_id,
            "tracking_number": self.tracking_number,
            "shipping_method": self.shipping_method,
        }


class OrderDelivered(DomainEvent):
    """Event raised when an order is delivered."""

    order_id: str
    delivered_at: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": str(self.event_id),
            "event_type": self.event_type,
            "aggregate_id": self.aggregate_id,
            "occurred_on": self.occurred_on.isoformat(),
            "version": self.version,
            "order_id": self.order_id,
            "delivered_at": self.delivered_at,
        }


class OrderCancelled(DomainEvent):
    """Event raised when an order is cancelled."""

    order_id: str
    reason: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": str(self.event_id),
            "event_type": self.event_type,
            "aggregate_id": self.aggregate_id,
            "occurred_on": self.occurred_on.isoformat(),
            "version": self.version,
            "order_id": self.order_id,
            "reason": self.reason,
        }


class OrderRefunded(DomainEvent):
    """Event raised when an order is refunded."""

    order_id: str
    refund_amount: str
    reason: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": str(self.event_id),
            "event_type": self.event_type,
            "aggregate_id": self.aggregate_id,
            "occurred_on": self.occurred_on.isoformat(),
            "version": self.version,
            "order_id": self.order_id,
            "refund_amount": self.refund_amount,
            "reason": self.reason,
        }
