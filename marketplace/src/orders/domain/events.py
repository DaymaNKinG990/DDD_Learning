"""Domain events for orders bounded context."""

# Python imports
from typing import Any, Dict, Optional

# Local imports
from src.shared.domain.events import DomainEvent


class OrderCreated(DomainEvent):
    """
    Event raised when an order is created.
    
    This event is raised when an order is created.
    
    Attributes:
        order_id (str): The ID of the order.
        customer_id (str): The ID of the customer.
        total (str): The total amount of the order.
        shipping_address (str): The shipping address of the order.
        billing_address (str): The billing address of the order.
        notes (Optional[str]): The notes of the order.
    """

    order_id: str
    customer_id: str
    total: str
    shipping_address: str
    billing_address: str
    notes: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the event to a dictionary.
        
        Returns:
            Dict[str, Any]: The dictionary representation of the event.
        """
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
    """
    Event raised when an item is added to an order.
    
    This event is raised when an item is added to an order.
    
    Attributes:
        order_id (str): The ID of the order.
        product_id (str): The ID of the product.
        product_name (str): The name of the product.
        quantity (int): The quantity of the product.
        unit_price (str): The price of the product per unit.
        total (str): The total price of the product.
    """

    order_id: str
    product_id: str
    product_name: str
    quantity: int
    unit_price: str
    total: str

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the event to a dictionary.
        
        Returns:
            Dict[str, Any]: The dictionary representation of the event.
        """
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
    """
    Event raised when an item is removed from an order.
    
    This event is raised when an item is removed from an order.
    
    Attributes:
        order_id (str): The ID of the order.
        product_id (str): The ID of the product.
        quantity (int): The quantity of the product.
    """

    order_id: str
    product_id: str
    quantity: int

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the event to a dictionary.
        
        Returns:
            Dict[str, Any]: The dictionary representation of the event.
        """
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
    """
    Event raised when an order is confirmed.
    
    This event is raised when an order is confirmed.
    
    Attributes:
        order_id (str): The ID of the order.
        customer_id (str): The ID of the customer.
        total (str): The total amount of the order.
    """

    order_id: str
    customer_id: str
    total: str

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the event to a dictionary.
        
        Returns:
            Dict[str, Any]: The dictionary representation of the event.
        """
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
    """
    Event raised when an order is shipped.
    
    This event is raised when an order is shipped.
    
    Attributes:
        order_id (str): The ID of the order.
        tracking_number (Optional[str]): The tracking number of the order.
        shipping_method (str): The shipping method of the order.
    """

    order_id: str
    tracking_number: Optional[str] = None
    shipping_method: str

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the event to a dictionary.
        
        Returns:
            Dict[str, Any]: The dictionary representation of the event.
        """
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
    """
    Event raised when an order is delivered.
    
    This event is raised when an order is delivered.
    
    Attributes:
        order_id (str): The ID of the order.
        delivered_at (str): The date and time the order was delivered.
    """

    order_id: str
    delivered_at: str

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the event to a dictionary.
        
        Returns:
            Dict[str, Any]: The dictionary representation of the event.
        """
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
    """
    Event raised when an order is cancelled.
    
    This event is raised when an order is cancelled.
    
    Attributes:
        order_id (str): The ID of the order.
        reason (Optional[str]): The reason for the cancellation.
    """

    order_id: str
    reason: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the event to a dictionary.
        
        Returns:
            Dict[str, Any]: The dictionary representation of the event.
        """
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
    """
    Event raised when an order is refunded.
    
    This event is raised when an order is refunded.
    
    Attributes:
        order_id (str): The ID of the order.
        refund_amount (str): The amount refunded.
        reason (str): The reason for the refund.
    """

    order_id: str
    refund_amount: str
    reason: str

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the event to a dictionary.
        
        Returns:
            Dict[str, Any]: The dictionary representation of the event.
        """
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
