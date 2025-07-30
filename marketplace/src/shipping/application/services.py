"""Application services for shipping domain."""

from datetime import datetime
from typing import List, Optional

from src.orders.domain.value_objects import OrderId
from src.shared.application.event_bus import EventBus
from src.shared.domain.exceptions import EntityNotFoundError

from ..domain.entities import Shipment, ShippingProvider
from ..domain.repositories import ShipmentRepository, ShippingProviderRepository
from ..domain.value_objects import (
    DeliveryAddress,
    ShippingCost,
    ShippingId,
    ShippingMethod,
    ShippingProviderId,
    ShippingStatus,
)


class ShipmentService:
    """Application service for shipment operations."""

    def __init__(
        self,
        shipment_repository: ShipmentRepository,
        event_bus: EventBus,
    ):
        self.shipment_repository = shipment_repository
        self.event_bus = event_bus

    async def create_shipment(
        self,
        order_id: str,
        method: ShippingMethod,
        cost: ShippingCost,
        delivery_address: DeliveryAddress,
        carrier: str = "",
        notes: Optional[str] = None,
    ) -> Shipment:
        """Create a new shipment."""
        shipment = Shipment(
            id=ShippingId(value=f"shipment_{order_id}_{method.value}"),
            order_id=OrderId(value=order_id),
            method=method,
            cost=cost,
            delivery_address=delivery_address,
            carrier=carrier,
            notes=notes,
        )
        return await self.shipment_repository.save(shipment)

    async def get_shipment(self, shipment_id: str) -> Shipment:
        """Get shipment by ID."""
        shipment = await self.shipment_repository.get_by_id(
            ShippingId(value=shipment_id)
        )
        if not shipment:
            raise EntityNotFoundError(f"Shipment with ID {shipment_id} not found")
        return shipment

    async def get_shipments_by_order(self, order_id: str) -> List[Shipment]:
        """Get shipments by order ID."""
        return await self.shipment_repository.get_by_order_id(OrderId(value=order_id))

    async def get_shipments_by_status(self, status: ShippingStatus) -> List[Shipment]:
        """Get shipments by status."""
        return await self.shipment_repository.get_by_status(status)

    async def assign_tracking_number(
        self, shipment_id: str, tracking_number: str
    ) -> Shipment:
        """Assign tracking number to shipment."""
        shipment = await self.get_shipment(shipment_id)
        shipment.assign_tracking_number(tracking_number)
        return await self.shipment_repository.save(shipment)

    async def update_shipment_status(
        self, shipment_id: str, status: ShippingStatus
    ) -> Shipment:
        """Update shipment status."""
        shipment = await self.get_shipment(shipment_id)
        shipment.update_status(status)
        return await self.shipment_repository.save(shipment)

    async def set_estimated_delivery_date(
        self, shipment_id: str, delivery_date: datetime
    ) -> Shipment:
        """Set estimated delivery date."""
        shipment = await self.get_shipment(shipment_id)
        shipment.set_estimated_delivery_date(delivery_date)
        return await self.shipment_repository.save(shipment)

    async def add_shipment_note(self, shipment_id: str, note: str) -> Shipment:
        """Add note to shipment."""
        shipment = await self.get_shipment(shipment_id)
        shipment.add_note(note)
        return await self.shipment_repository.save(shipment)

    async def delete_shipment(self, shipment_id: str) -> bool:
        """Delete shipment."""
        return await self.shipment_repository.delete(ShippingId(value=shipment_id))


class ShippingProviderService:
    """Application service for shipping provider operations."""

    def __init__(
        self,
        shipping_provider_repository: ShippingProviderRepository,
        event_bus: EventBus,
    ):
        self.shipping_provider_repository = shipping_provider_repository
        self.event_bus = event_bus

    async def create_shipping_provider(
        self,
        name: str,
        code: str,
        base_cost: ShippingCost,
        delivery_time_days: int = 0,
        supported_methods: Optional[List[ShippingMethod]] = None,
        express_delivery_time_days: Optional[int] = None,
        premium_delivery_time_days: Optional[int] = None,
        same_day_delivery_available: bool = False,
        api_endpoint: Optional[str] = None,
        api_key: Optional[str] = None,
    ) -> ShippingProvider:
        """Create a new shipping provider."""
        provider = ShippingProvider(
            id=ShippingProviderId(value=f"provider_{code}"),
            name=name,
            code=code,
            base_cost=base_cost,
            delivery_time_days=delivery_time_days,
            supported_methods=supported_methods or [],
            express_delivery_time_days=express_delivery_time_days,
            premium_delivery_time_days=premium_delivery_time_days,
            same_day_delivery_available=same_day_delivery_available,
            api_endpoint=api_endpoint,
            api_key=api_key,
        )
        return await self.shipping_provider_repository.save(provider)

    async def get_shipping_provider(self, provider_id: str) -> ShippingProvider:
        """Get shipping provider by ID."""
        provider = await self.shipping_provider_repository.get_by_id(
            ShippingProviderId(value=provider_id)
        )
        if not provider:
            raise EntityNotFoundError(
                f"Shipping provider with ID {provider_id} not found"
            )
        return provider

    async def get_all_providers(self) -> List[ShippingProvider]:
        """Get all shipping providers."""
        return await self.shipping_provider_repository.get_all()

    async def get_active_providers(self) -> List[ShippingProvider]:
        """Get active shipping providers."""
        return await self.shipping_provider_repository.get_active()

    async def get_providers_by_method(
        self, method: ShippingMethod
    ) -> List[ShippingProvider]:
        """Get providers that support specific shipping method."""
        return await self.shipping_provider_repository.get_providers_by_method(method)

    async def activate_provider(self, provider_id: str) -> ShippingProvider:
        """Activate shipping provider."""
        provider = await self.get_shipping_provider(provider_id)
        provider.activate()
        return await self.shipping_provider_repository.save(provider)

    async def deactivate_provider(self, provider_id: str) -> ShippingProvider:
        """Deactivate shipping provider."""
        provider = await self.get_shipping_provider(provider_id)
        provider.deactivate()
        return await self.shipping_provider_repository.save(provider)

    async def calculate_shipping_cost(
        self, provider_id: str, method: ShippingMethod, weight: float = 1.0
    ) -> ShippingCost:
        """Calculate shipping cost for specific provider and method."""
        provider = await self.get_shipping_provider(provider_id)
        return provider.calculate_cost(method, weight)

    async def get_delivery_time(
        self, provider_id: str, method: ShippingMethod
    ) -> Optional[int]:
        """Get delivery time for specific provider and method."""
        provider = await self.get_shipping_provider(provider_id)
        return provider.get_delivery_time(method)

    async def delete_provider(self, provider_id: str) -> bool:
        """Delete shipping provider."""
        return await self.shipping_provider_repository.delete(
            ShippingProviderId(value=provider_id)
        )
