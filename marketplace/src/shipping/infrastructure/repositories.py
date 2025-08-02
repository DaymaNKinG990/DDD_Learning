"""In-memory repository implementations for shipping domain."""

# Python imports
from typing import Dict, List, Optional

# Local imports
from src.shared.infrastructure.repositories import InMemoryRepository
from src.orders.domain.value_objects import OrderId

from ..domain.entities import Shipment, ShippingProvider
from ..domain.repositories import ShipmentRepository, ShippingProviderRepository
from ..domain.value_objects import (
    ShippingId,
    ShippingMethod,
    ShippingProviderId,
    ShippingStatus,
)


class InMemoryShipmentRepository(InMemoryRepository[Shipment, ShippingId], ShipmentRepository):
    """
    In-memory implementation of ShipmentRepository.
    
    Attributes:
        _shipments_by_order_id: A dictionary mapping order IDs to shipments.
        _shipments_by_status: A dictionary mapping statuses to shipments.
        _shipments_by_tracking_number: A dictionary mapping tracking numbers to shipments.
    """

    def __init__(self) -> None:
        """Initialize the in-memory shipment repository."""
        super().__init__()
        self._shipments_by_order_id: Dict[str, List[Shipment]] = {}
        self._shipments_by_status: Dict[ShippingStatus, List[Shipment]] = {}
        self._shipments_by_tracking_number: Dict[str, Shipment] = {}

    async def save(self, shipment: Shipment) -> Shipment:
        """
        Save shipment.
        
        Args:
            shipment: The shipment to save.

        Returns:
            Shipment: The saved shipment.
        """

        saved_shipment = await super().save(shipment)

        # Update indexes
        order_id_str = str(shipment.order_id)
        if order_id_str not in self._shipments_by_order_id:
            self._shipments_by_order_id[order_id_str] = []
        if shipment not in self._shipments_by_order_id[order_id_str]:
            self._shipments_by_order_id[order_id_str].append(shipment)

        if shipment.status not in self._shipments_by_status:
            self._shipments_by_status[shipment.status] = []
        if shipment not in self._shipments_by_status[shipment.status]:
            self._shipments_by_status[shipment.status].append(shipment)

        if shipment.tracking_number:
            self._shipments_by_tracking_number[str(shipment.tracking_number)] = shipment

        return saved_shipment

    async def get_by_order_id(self, order_id: OrderId) -> List[Shipment]:
        """
        Get shipments by order ID.
        
        Args:
            order_id: The order ID.

        Returns:
            List[Shipment]: The shipments.
        """
        return self._shipments_by_order_id.get(str(order_id), [])

    async def get_by_status(self, status: ShippingStatus) -> List[Shipment]:
        """
        Get shipments by status.
        
        Args:
            status: The status.

        Returns:
            List[Shipment]: The shipments.
        """
        return self._shipments_by_status.get(status, [])

    async def get_by_tracking_number(self, tracking_number: str) -> Optional[Shipment]:
        """
        Get shipment by tracking number.
        
        Args:
            tracking_number: The tracking number.

        Returns:
            Optional[Shipment]: The shipment.
        """
        return self._shipments_by_tracking_number.get(tracking_number)

    async def delete(self, shipment_id: ShippingId) -> bool:
        """
        Delete shipment by ID.
        
        Args:
            shipment_id: The ID of the shipment.

        Returns:
            bool: True if the shipment was deleted, False otherwise.
        """
        shipment = await self.get_by_id(shipment_id)
        if shipment:
            # Remove from indexes
            order_id_str = str(shipment.order_id)
            if order_id_str in self._shipments_by_order_id:
                self._shipments_by_order_id[order_id_str] = [
                    s for s in self._shipments_by_order_id[order_id_str] 
                    if s.id != shipment_id
                ]

            if shipment.status in self._shipments_by_status:
                self._shipments_by_status[shipment.status] = [
                    s for s in self._shipments_by_status[shipment.status] 
                    if s.id != shipment_id
                ]

            if shipment.tracking_number:
                self._shipments_by_tracking_number.pop(
                    str(shipment.tracking_number), None
                )

            return await super().delete(shipment_id)
        return False


class InMemoryShippingProviderRepository(InMemoryRepository[ShippingProvider, ShippingProviderId], ShippingProviderRepository):
    """
    In-memory implementation of ShippingProviderRepository.
    
    Attributes:
        _providers_by_method: A dictionary mapping shipping methods to shipping providers.
        _active_providers: A list of active shipping providers.
    """

    def __init__(self) -> None:
        """Initialize the in-memory shipping provider repository."""
        super().__init__()
        self._providers_by_method: Dict[ShippingMethod, List[ShippingProvider]] = {}
        self._active_providers: List[ShippingProvider] = []

    async def save(self, provider: ShippingProvider) -> ShippingProvider:
        """
        Save shipping provider.
        
        Args:
            provider: The shipping provider to save.

        Returns:
            ShippingProvider: The saved shipping provider.
        """
        saved_provider = await super().save(provider)

        # Update indexes
        for method in provider.supported_methods:
            if method not in self._providers_by_method:
                self._providers_by_method[method] = []
            if provider not in self._providers_by_method[method]:
                self._providers_by_method[method].append(provider)

        if provider.is_active and provider not in self._active_providers:
            self._active_providers.append(provider)
        elif not provider.is_active and provider in self._active_providers:
            self._active_providers.remove(provider)

        return saved_provider

    async def get_all(self) -> List[ShippingProvider]:
        """
        Get all shipping providers.
        
        Returns:
            List[ShippingProvider]: The shipping providers.
        """
        return list(self._storage.values())

    async def get_active(self) -> List[ShippingProvider]:
        """
        Get active shipping providers.
        
        Returns:
            List[ShippingProvider]: The active shipping providers.
        """
        return self._active_providers.copy()

    async def get_providers_by_method(self, method: ShippingMethod) -> List[ShippingProvider]:
        """
        Get providers that support specific shipping method.
        
        Args:
            method: The shipping method.

        Returns:
            List[ShippingProvider]: The providers that support the shipping method.
        """
        return self._providers_by_method.get(method, [])

    async def delete(self, provider_id: ShippingProviderId) -> bool:
        """
        Delete shipping provider by ID.
        
        Args:
            provider_id: The ID of the shipping provider.

        Returns:
            bool: True if the shipping provider was deleted, False otherwise.
        """
        provider = await self.get_by_id(provider_id)
        if provider:
            # Remove from indexes
            for method in provider.supported_methods:
                if method in self._providers_by_method:
                    self._providers_by_method[method] = [
                        p for p in self._providers_by_method[method] 
                        if p.id != provider_id
                    ]

            if provider in self._active_providers:
                self._active_providers.remove(provider)

            return await super().delete(provider_id)
        return False
