"""Entities for shipping domain."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from decimal import Decimal
from typing import List, Optional

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
    """Shipment entity."""

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
        """Assign tracking number to shipment."""
        self.tracking_number = TrackingNumber(value=tracking_number)

    def update_status(self, status: ShippingStatus) -> None:
        """Update shipment status."""
        self.status = status
        if status == ShippingStatus.DELIVERED:
            self.actual_delivery_date = datetime.now(UTC)

    def set_estimated_delivery_date(self, date: datetime) -> None:
        """Set estimated delivery date."""
        self.estimated_delivery_date = date

    def add_note(self, note: str) -> None:
        """Add note to shipment."""
        if self.notes:
            self.notes += f"\n{note}"
        else:
            self.notes = note

    def is_delivered(self) -> bool:
        """Check if shipment is delivered."""
        return self.status == ShippingStatus.DELIVERED

    def is_in_transit(self) -> bool:
        """Check if shipment is in transit."""
        return self.status == ShippingStatus.IN_TRANSIT


@dataclass
class ShippingProvider(Entity):
    """Shipping provider entity."""

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
        """Check if provider supports specific shipping method."""
        return method in self.supported_methods

    def get_delivery_time(self, method: ShippingMethod) -> Optional[int]:
        """Get delivery time for specific method."""
        if method == ShippingMethod.STANDARD:
            return self.delivery_time_days
        elif method == ShippingMethod.EXPRESS:
            return self.express_delivery_time_days
        elif method == ShippingMethod.PREMIUM:
            return self.premium_delivery_time_days
        elif method == ShippingMethod.SAME_DAY:
            return 1 if self.same_day_delivery_available else None
        return None

    def calculate_cost(
        self, method: ShippingMethod, weight: float = 1.0
    ) -> ShippingCost:
        """Calculate shipping cost for specific method and weight."""
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
