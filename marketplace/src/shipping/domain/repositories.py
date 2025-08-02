"""Repository interfaces for shipping domain."""

# Python imports
from abc import ABC, abstractmethod
from typing import List, Optional

# Local imports
from src.shipping.domain.entities import Shipment, ShippingProvider
from src.shipping.domain.value_objects import (
    ShippingId,
    ShippingMethod,
    ShippingStatus,
    TrackingNumber,
)


class ShipmentRepository(ABC):
    """
    Repository interface for Shipment entity.
    
    Attributes:
        save: Save shipment.
        get_by_id: Get shipment by ID.
        get_by_tracking_number: Get shipment by tracking number.
        get_by_order_id: Get shipment by order ID.
        get_by_status: Get shipments by status.
        get_all: Get all shipments.
        delete: Delete shipment by ID.
    """

    @abstractmethod
    async def save(self, shipment: Shipment) -> Shipment:
        """
        Save shipment.
        
        Args:
            shipment: The shipment to save.

        Returns:
            Shipment: The saved shipment.
        """
        pass

    @abstractmethod
    async def get_by_id(self, shipment_id: ShippingId) -> Optional[Shipment]:
        """
        Get shipment by ID.
        
        Args:
            shipment_id: The ID of the shipment.

        Returns:
            Optional[Shipment]: The shipment.
        """
        pass

    @abstractmethod
    async def get_by_tracking_number(self, tracking_number: TrackingNumber) -> Optional[Shipment]:
        """
        Get shipment by tracking number.
        
        Args:
            tracking_number: The tracking number.

        Returns:
            Optional[Shipment]: The shipment.
        """
        pass

    @abstractmethod
    async def get_by_order_id(self, order_id: str) -> Optional[Shipment]:
        """
        Get shipment by order ID.
        
        Args:
            order_id: The ID of the order.

        Returns:
            Optional[Shipment]: The shipment.
        """
        pass

    @abstractmethod
    async def get_by_status(self, status: ShippingStatus) -> List[Shipment]:
        """
        Get shipments by status.
        
        Args:
            status: The status.

        Returns:
            List[Shipment]: The shipments.
        """
        pass

    @abstractmethod
    async def get_all(self) -> List[Shipment]:
        """
        Get all shipments.
        
        Returns:
            List[Shipment]: The shipments.
        """
        pass

    @abstractmethod
    async def delete(self, shipment_id: ShippingId) -> bool:
        """
        Delete shipment by ID.
        
        Args:
            shipment_id: The ID of the shipment.

        Returns:
            bool: True if the shipment was deleted, False otherwise.
        """
        pass


class ShippingProviderRepository(ABC):
    """
    Repository interface for ShippingProvider entity.
    
    Attributes:
        save: Save shipping provider.
        get_by_id: Get shipping provider by ID.
        get_by_code: Get shipping provider by code.
        get_active_providers: Get all active shipping providers.
        get_providers_by_method: Get providers that support specific shipping method.
        get_all: Get all shipping providers.
        delete: Delete shipping provider by ID.
    """

    @abstractmethod
    async def save(self, provider: ShippingProvider) -> ShippingProvider:
        """
        Save shipping provider.
        
        Args:
            provider: The shipping provider to save.

        Returns:
            ShippingProvider: The saved shipping provider.
        """
        pass

    @abstractmethod
    async def get_by_id(self, provider_id: str) -> Optional[ShippingProvider]:
        """
        Get shipping provider by ID.
        
        Args:
            provider_id: The ID of the shipping provider.

        Returns:
            Optional[ShippingProvider]: The shipping provider.
        """
        pass

    @abstractmethod
    async def get_by_code(self, code: str) -> Optional[ShippingProvider]:
        """
        Get shipping provider by code.
        
        Args:
            code: The code of the shipping provider.

        Returns:
            Optional[ShippingProvider]: The shipping provider.
        """
        pass

    @abstractmethod
    async def get_active_providers(self) -> List[ShippingProvider]:
        """
        Get all active shipping providers.
        
        Returns:
            List[ShippingProvider]: The active shipping providers.
        """
        pass

    @abstractmethod
    async def get_providers_by_method(self, method: ShippingMethod) -> List[ShippingProvider]:
        """
        Get providers that support specific shipping method.
        
        Args:
            method: The shipping method.

        Returns:
            List[ShippingProvider]: The providers that support the shipping method.
        """
        pass

    @abstractmethod
    async def get_all(self) -> List[ShippingProvider]:
        """
        Get all shipping providers.
        
        Returns:
            List[ShippingProvider]: The shipping providers.
        """
        pass

    @abstractmethod
    async def delete(self, provider_id: str) -> bool:
        """
        Delete shipping provider by ID.
        
        Args:
            provider_id: The ID of the shipping provider.

        Returns:
            bool: True if the shipping provider was deleted, False otherwise.
        """
        pass
