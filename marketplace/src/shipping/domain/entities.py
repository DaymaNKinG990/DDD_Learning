"""Entities for shipping domain."""

# Python imports
from dataclasses import dataclass, field
from datetime import UTC, datetime
from decimal import Decimal
from typing import List, Optional

# Local imports
from src.orders.domain.value_objects import OrderId
from src.shared.domain.entity import Entity
from src.shipping.domain.value_objects import (
    DeliveryAddress,
    ShippingCost,
    ShippingMethod,
    ShippingStatus,
    TrackingNumber,
)


@dataclass
class Shipment(Entity):
    """
    Shipment entity.
    
    Attributes:
        order_id: The order ID.
        method: The shipping method.
        cost: The shipping cost.
        delivery_address: The delivery address.
        tracking_number: The tracking number.
        status: The status of the shipment.
        estimated_delivery_date: The estimated delivery date.
        actual_delivery_date: The actual delivery date.
        carrier: The carrier.
        notes: The notes.
    """

    order_id: OrderId
    method: ShippingMethod
    cost: ShippingCost
    delivery_address: DeliveryAddress
    tracking_number: Optional[TrackingNumber] = None
    status: ShippingStatus = ShippingStatus.PENDING
    estimated_delivery_date: Optional[datetime] = None
    actual_delivery_date: Optional[datetime] = None
    carrier: str = ""
    notes: Optional[str] = None

    def assign_tracking_number(self, tracking_number: str) -> None:
        """
        Assign tracking number to shipment.
        
        Args:
            tracking_number: The tracking number to assign.
        """
        self.tracking_number = TrackingNumber(value=tracking_number)

    def update_status(self, status: ShippingStatus) -> None:
        """
        Update shipment status.
        
        Args:
            status: The new status.
        """
        self.status = status
        if status == ShippingStatus.DELIVERED:
            self.actual_delivery_date = datetime.now(UTC)

    def set_estimated_delivery_date(self, date: datetime) -> None:
        """
        Set estimated delivery date.
        
        Args:
            date: The estimated delivery date.
        """
        self.estimated_delivery_date = date

    def add_note(self, note: str) -> None:
        """
        Add note to shipment.
        
        Args:
            note: The note to add.
        """
        if self.notes:
            self.notes += f"\n{note}"
        else:
            self.notes = note

    def is_delivered(self) -> bool:
        """
        Check if shipment is delivered.
        
        Returns:
            bool: True if the shipment is delivered, False otherwise.
        """
        return self.status == ShippingStatus.DELIVERED

    def is_in_transit(self) -> bool:
        """
        Check if shipment is in transit.
        
        Returns:
            bool: True if the shipment is in transit, False otherwise.
        """
        return self.status == ShippingStatus.IN_TRANSIT


@dataclass
class ShippingProvider(Entity):
    """
    Shipping provider entity.
    
    Attributes:
        name: The name of the shipping provider.
        code: The code of the shipping provider.
        base_cost: The base cost of the shipping provider.
        delivery_time_days: The delivery time in days.
        supported_methods: The supported methods.
        is_active: Whether the shipping provider is active.
        express_delivery_time_days: The express delivery time in days.
        premium_delivery_time_days: The premium delivery time in days.
        same_day_delivery_available: Whether same day delivery is available.
        api_endpoint: The API endpoint.
        api_key: The API key.
    """

    name: str
    code: str
    base_cost: ShippingCost
    delivery_time_days: int = 0
    supported_methods: List[ShippingMethod] = field(default_factory=list)
    is_active: bool = True
    express_delivery_time_days: Optional[int] = None
    premium_delivery_time_days: Optional[int] = None
    same_day_delivery_available: bool = False
    api_endpoint: Optional[str] = None
    api_key: Optional[str] = None

    def activate(self) -> None:
        """Activate shipping provider."""
        self.is_active = True

    def deactivate(self) -> None:
        """Deactivate shipping provider."""
        self.is_active = False

    def supports_method(self, method: ShippingMethod) -> bool:
        """
        Check if provider supports specific shipping method.
        
        Args:
            method: The shipping method.

        Returns:
            bool: True if the shipping provider supports the method, False otherwise.
        """
        return method in self.supported_methods

    def get_delivery_time(self, method: ShippingMethod) -> Optional[int]:
        """
        Get delivery time for specific method.
        
        Args:
            method: The shipping method.

        Returns:
            Optional[int]: The delivery time in days.
        """
        if method == ShippingMethod.STANDARD:
            return self.delivery_time_days
        elif method == ShippingMethod.EXPRESS:
            return self.express_delivery_time_days
        elif method == ShippingMethod.PREMIUM:
            return self.premium_delivery_time_days
        elif method == ShippingMethod.SAME_DAY:
            return 1 if self.same_day_delivery_available else None

    def calculate_cost(self, method: ShippingMethod, weight: float = 1.0) -> ShippingCost:
        """
        Calculate shipping cost for specific method and weight.
        
        Args:
            method: The shipping method.
            weight: The weight of the shipment.

        Returns:
            ShippingCost: The calculated shipping cost.
        """
        # Simple calculation - in real implementation would be more complex
        base_cost = self.base_cost.value
        if method == ShippingMethod.EXPRESS:
            base_cost *= 1.5
        elif method == ShippingMethod.PREMIUM:
            base_cost *= 2.0

        # Apply weight multiplier
        total_cost = base_cost * weight
        return ShippingCost(
            value=Decimal(str(total_cost)), currency=self.base_cost.currency
        )
