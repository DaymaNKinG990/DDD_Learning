"""Repository interfaces for shipping domain."""

from abc import ABC, abstractmethod
from typing import List, Optional

from src.shipping.domain.entities import Shipment, ShippingProvider
from src.shipping.domain.value_objects import (
    ShippingId,
    ShippingMethod,
    ShippingStatus,
    TrackingNumber,
)


class ShipmentRepository(ABC):
    """Repository interface for Shipment entity."""

    @abstractmethod
    async def save(self, shipment: Shipment) -> Shipment:
        """Save shipment."""
        pass

    @abstractmethod
    async def get_by_id(self, shipment_id: ShippingId) -> Optional[Shipment]:
        """Get shipment by ID."""
        pass

    @abstractmethod
    async def get_by_tracking_number(
        self, tracking_number: TrackingNumber
    ) -> Optional[Shipment]:
        """Get shipment by tracking number."""
        pass

    @abstractmethod
    async def get_by_order_id(self, order_id: str) -> Optional[Shipment]:
        """Get shipment by order ID."""
        pass

    @abstractmethod
    async def get_by_status(self, status: ShippingStatus) -> List[Shipment]:
        """Get shipments by status."""
        pass

    @abstractmethod
    async def get_all(self) -> List[Shipment]:
        """Get all shipments."""
        pass

    @abstractmethod
    async def delete(self, shipment_id: ShippingId) -> bool:
        """Delete shipment by ID."""
        pass


class ShippingProviderRepository(ABC):
    """Repository interface for ShippingProvider entity."""

    @abstractmethod
    async def save(self, provider: ShippingProvider) -> ShippingProvider:
        """Save shipping provider."""
        pass

    @abstractmethod
    async def get_by_id(self, provider_id: str) -> Optional[ShippingProvider]:
        """Get shipping provider by ID."""
        pass

    @abstractmethod
    async def get_by_code(self, code: str) -> Optional[ShippingProvider]:
        """Get shipping provider by code."""
        pass

    @abstractmethod
    async def get_active_providers(self) -> List[ShippingProvider]:
        """Get all active shipping providers."""
        pass

    @abstractmethod
    async def get_providers_by_method(
        self, method: ShippingMethod
    ) -> List[ShippingProvider]:
        """Get providers that support specific shipping method."""
        pass

    @abstractmethod
    async def get_all(self) -> List[ShippingProvider]:
        """Get all shipping providers."""
        pass

    @abstractmethod
    async def delete(self, provider_id: str) -> bool:
        """Delete shipping provider by ID."""
        pass
