"""Application services for shipping domain."""

# Python imports
from datetime import datetime
from typing import List, Optional

# Local imports
from src.orders.domain.value_objects import OrderId
from src.shared.application.event_bus import EventBus
from src.shared.domain.exceptions import EntityNotFoundError
from src.shipping.domain.entities import Shipment, ShippingProvider
from src.shipping.domain.repositories import ShipmentRepository, ShippingProviderRepository
from src.shipping.domain.value_objects import (
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
    ) -> None:
        """
        Initialize the shipment service.
        
        Args:
            shipment_repository: The shipment repository.
            event_bus: The event bus.
        """
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
        """
        Create a new shipment.
        
        Args:
            order_id: The order ID.
            method: The shipping method.
            cost: The shipping cost.
            delivery_address: The delivery address.
            carrier: The carrier.
            notes: The notes.

        Returns:
            Shipment: The created shipment.
        """
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
        """
        Get shipment by ID.
        
        Args:
            shipment_id: The shipment ID.

        Returns:
            Shipment: The shipment.
        """
        shipment = await self.shipment_repository.get_by_id(
            ShippingId(value=shipment_id)
        )
        if not shipment:
            raise EntityNotFoundError(f"Shipment with ID {shipment_id} not found")
        return shipment

    async def get_shipments_by_order(self, order_id: str) -> List[Shipment]:
        """
        Get shipments by order ID.
        
        Args:
            order_id: The order ID.

        Returns:
            List[Shipment]: The shipments.
        """
        return await self.shipment_repository.get_by_order_id(OrderId(value=order_id))

    async def get_shipments_by_status(self, status: ShippingStatus) -> List[Shipment]:
        """
        Get shipments by status.
        
        Args:
            status: The status.

        Returns:
            List[Shipment]: The shipments.
        """
        return await self.shipment_repository.get_by_status(status)

    async def assign_tracking_number(self, shipment_id: str, tracking_number: str) -> Shipment:
        """
        Assign tracking number to shipment.
        
        Args:
            shipment_id: The shipment ID.
            tracking_number: The tracking number.

        Returns:
            Shipment: The shipment.
        """
        shipment = await self.get_shipment(shipment_id)
        shipment.assign_tracking_number(tracking_number)
        return await self.shipment_repository.save(shipment)

    async def update_shipment_status(self, shipment_id: str, status: ShippingStatus) -> Shipment:
        """
        Update shipment status.
        
        Args:
            shipment_id: The shipment ID.
            status: The status.

        Returns:
            Shipment: The shipment.
        """
        shipment = await self.get_shipment(shipment_id)
        shipment.update_status(status)
        return await self.shipment_repository.save(shipment)

    async def set_estimated_delivery_date(self, shipment_id: str, delivery_date: datetime) -> Shipment:
        """
        Set estimated delivery date.
        
        Args:
            shipment_id: The shipment ID.
            delivery_date: The delivery date.

        Returns:
            Shipment: The shipment.
        """

        shipment = await self.get_shipment(shipment_id)
        shipment.set_estimated_delivery_date(delivery_date)
        return await self.shipment_repository.save(shipment)

    async def add_shipment_note(self, shipment_id: str, note: str) -> Shipment:
        """
        Add note to shipment.
        
        Args:
            shipment_id: The shipment ID.
            note: The note.

        Returns:
            Shipment: The shipment.
        """
        shipment = await self.get_shipment(shipment_id)
        shipment.add_note(note)
        return await self.shipment_repository.save(shipment)

    async def delete_shipment(self, shipment_id: str) -> bool:
        """
        Delete shipment.
        
        Args:
            shipment_id: The shipment ID.

        Returns:
            bool: True if the shipment was deleted, False otherwise.
        """
        return await self.shipment_repository.delete(ShippingId(value=shipment_id))


class ShippingProviderService:
    """Application service for shipping provider operations."""

    def __init__(
        self,
        shipping_provider_repository: ShippingProviderRepository,
        event_bus: EventBus,
    ) -> None:
        """
        Initialize the shipping provider service.
        
        Args:
            shipping_provider_repository: The shipping provider repository.
            event_bus: The event bus.
        """
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
        """
        Create a new shipping provider.
        
        Args:
            name: The name of the shipping provider.
            code: The code of the shipping provider.
            base_cost: The base cost of the shipping provider.
            delivery_time_days: The delivery time in days.
            supported_methods: The supported methods.
            express_delivery_time_days: The express delivery time in days.
            premium_delivery_time_days: The premium delivery time in days.
            same_day_delivery_available: Whether same day delivery is available.
            api_endpoint: The API endpoint.
            api_key: The API key.

        Returns:
            ShippingProvider: The created shipping provider.
        """
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
        """
        Get shipping provider by ID.
        
        Args:
            provider_id: The ID of the shipping provider.

        Returns:
            ShippingProvider: The shipping provider.
        """
        provider = await self.shipping_provider_repository.get_by_id(
            ShippingProviderId(value=provider_id)
        )
        if not provider:
            raise EntityNotFoundError(
                f"Shipping provider with ID {provider_id} not found"
            )
        return provider

    async def get_all_providers(self) -> List[ShippingProvider]:
        """
        Get all shipping providers.
        
        Returns:
            List[ShippingProvider]: The shipping providers.
        """
        return await self.shipping_provider_repository.get_all()

    async def get_active_providers(self) -> List[ShippingProvider]:
        """
        Get active shipping providers.
        
        Returns:
            List[ShippingProvider]: The active shipping providers.
        """
        return await self.shipping_provider_repository.get_active()

    async def get_providers_by_method(self, method: ShippingMethod) -> List[ShippingProvider]:
        """
        Get providers that support specific shipping method.
        
        Args:
            method: The shipping method.

        Returns:
            List[ShippingProvider]: The providers that support the shipping method.
        """
        return await self.shipping_provider_repository.get_providers_by_method(method)

    async def activate_provider(self, provider_id: str) -> ShippingProvider:
        """
        Activate shipping provider.
        
        Args:
            provider_id: The ID of the shipping provider.

        Returns:
            ShippingProvider: The activated shipping provider.
        """
        provider = await self.get_shipping_provider(provider_id)
        provider.activate()
        return await self.shipping_provider_repository.save(provider)

    async def deactivate_provider(self, provider_id: str) -> ShippingProvider:
        """
        Deactivate shipping provider.
        
        Args:
            provider_id: The ID of the shipping provider.

        Returns:
            ShippingProvider: The deactivated shipping provider.
        """
        provider = await self.get_shipping_provider(provider_id)
        provider.deactivate()
        return await self.shipping_provider_repository.save(provider)

    async def calculate_shipping_cost(self, provider_id: str, method: ShippingMethod, weight: float = 1.0) -> ShippingCost:
        """
        Calculate shipping cost for specific provider and method.
        
        Args:
            provider_id: The ID of the shipping provider.
            method: The shipping method.
            weight: The weight of the shipment.

        Returns:
            ShippingCost: The calculated shipping cost.
        """
        provider = await self.get_shipping_provider(provider_id)
        return provider.calculate_cost(method, weight)

    async def get_delivery_time(self, provider_id: str, method: ShippingMethod) -> Optional[int]:
        """
        Get delivery time for specific provider and method.
        
        Args:
            provider_id: The ID of the shipping provider.
            method: The shipping method.

        Returns:
            Optional[int]: The delivery time in days.
        """
        provider = await self.get_shipping_provider(provider_id)
        return provider.get_delivery_time(method)

    async def delete_provider(self, provider_id: str) -> bool:
        """
        Delete shipping provider.
        
        Args:
            provider_id: The ID of the shipping provider.

        Returns:
            bool: True if the shipping provider was deleted, False otherwise.
        """
        return await self.shipping_provider_repository.delete(
            ShippingProviderId(value=provider_id)
        )
