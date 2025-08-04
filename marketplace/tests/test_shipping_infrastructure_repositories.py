"""Tests for shipping.infrastructure.repositories module."""

import pytest
from unittest.mock import Mock
from src.shipping.infrastructure.repositories import (
    InMemoryShipmentRepository,
    InMemoryShippingProviderRepository
)
from src.shipping.domain.value_objects import (
    ShippingId, ShippingProviderId, ShippingStatus, ShippingMethod
)
from src.orders.domain.value_objects import OrderId


@pytest.mark.asyncio
class TestInMemoryShipmentRepository:
    """Test InMemoryShipmentRepository."""

    @pytest.fixture
    def repository(self):
        """Create repository instance."""
        return InMemoryShipmentRepository()

    @pytest.fixture
    def sample_shipment(self):
        """Create sample shipment."""
        shipment = Mock()
        shipment.id = ShippingId("shipment-123")
        shipment.order_id = OrderId("order-123")
        shipment.status = ShippingStatus.PENDING
        shipment.tracking_number = "TRK123456789"
        return shipment

    async def test_save_shipment(self, repository, sample_shipment):
        """Test saving a shipment."""
        result = await repository.save(sample_shipment)
        assert result == sample_shipment
        assert str(sample_shipment.id) in repository._storage

    async def test_get_by_id_existing(self, repository, sample_shipment):
        """Test getting shipment by ID when it exists."""
        await repository.save(sample_shipment)
        result = await repository.get_by_id(sample_shipment.id)
        assert result == sample_shipment

    async def test_get_by_id_not_found(self, repository):
        """Test getting shipment by ID when it doesn't exist."""
        result = await repository.get_by_id(ShippingId("nonexistent"))
        assert result is None

    async def test_get_by_order_id(self, repository, sample_shipment):
        """Test getting shipments by order ID."""
        await repository.save(sample_shipment)
        result = await repository.get_by_order_id(sample_shipment.order_id)
        assert len(result) == 1
        assert result[0] == sample_shipment

    async def test_get_by_order_id_empty(self, repository):
        """Test getting shipments by order ID when none exist."""
        result = await repository.get_by_order_id(OrderId("order-123"))
        assert result == []

    async def test_get_by_status(self, repository, sample_shipment):
        """Test getting shipments by status."""
        await repository.save(sample_shipment)
        result = await repository.get_by_status(sample_shipment.status)
        assert len(result) == 1
        assert result[0] == sample_shipment

    async def test_get_by_status_empty(self, repository):
        """Test getting shipments by status when none exist."""
        result = await repository.get_by_status(ShippingStatus.DELIVERED)
        assert result == []

    async def test_get_by_tracking_number(self, repository, sample_shipment):
        """Test getting shipment by tracking number."""
        await repository.save(sample_shipment)
        result = await repository.get_by_tracking_number(sample_shipment.tracking_number)
        assert result == sample_shipment

    async def test_get_by_tracking_number_not_found(self, repository):
        """Test getting shipment by tracking number when it doesn't exist."""
        result = await repository.get_by_tracking_number("nonexistent")
        assert result is None

    async def test_delete_shipment(self, repository, sample_shipment):
        """Test deleting a shipment."""
        await repository.save(sample_shipment)
        result = await repository.delete(sample_shipment.id)
        assert result is True
        retrieved = await repository.get_by_id(sample_shipment.id)
        assert retrieved is None

    async def test_delete_shipment_not_found(self, repository):
        """Test deleting a shipment that doesn't exist."""
        result = await repository.delete(ShippingId("nonexistent"))
        assert result is False

    async def test_multiple_shipments_same_order(self, repository):
        """Test handling multiple shipments for the same order."""
        shipment1 = Mock()
        shipment1.id = ShippingId("shipment-1")
        shipment1.order_id = OrderId("order-123")
        shipment1.status = ShippingStatus.PENDING
        shipment1.tracking_number = "TRK123456789"

        shipment2 = Mock()
        shipment2.id = ShippingId("shipment-2")
        shipment2.order_id = OrderId("order-123")
        shipment2.status = ShippingStatus.IN_TRANSIT
        shipment2.tracking_number = "TRK987654321"

        await repository.save(shipment1)
        await repository.save(shipment2)

        order_shipments = await repository.get_by_order_id(OrderId("order-123"))
        assert len(order_shipments) == 2

        pending_shipments = await repository.get_by_status(ShippingStatus.PENDING)
        assert len(pending_shipments) == 1
        assert pending_shipments[0] == shipment1

    async def test_shipment_without_tracking_number(self, repository):
        """Test handling shipment without tracking number."""
        shipment = Mock()
        shipment.id = ShippingId("shipment-123")
        shipment.order_id = OrderId("order-123")
        shipment.status = ShippingStatus.PENDING
        shipment.tracking_number = None

        await repository.save(shipment)
        result = await repository.get_by_tracking_number("nonexistent")
        assert result is None


@pytest.mark.asyncio
class TestInMemoryShippingProviderRepository:
    """Test InMemoryShippingProviderRepository."""

    @pytest.fixture
    def repository(self):
        """Create repository instance."""
        return InMemoryShippingProviderRepository()

    @pytest.fixture
    def sample_provider(self):
        """Create sample shipping provider."""
        provider = Mock()
        provider.id = ShippingProviderId("provider-123")
        provider.name = "Test Provider"
        provider.is_active = True
        provider.supported_methods = [ShippingMethod.STANDARD, ShippingMethod.EXPRESS]
        return provider

    async def test_save_provider(self, repository, sample_provider):
        """Test saving a shipping provider."""
        result = await repository.save(sample_provider)
        assert result == sample_provider
        assert str(sample_provider.id) in repository._storage

    async def test_get_by_id_existing(self, repository, sample_provider):
        """Test getting provider by ID when it exists."""
        await repository.save(sample_provider)
        result = await repository.get_by_id(sample_provider.id)
        assert result == sample_provider

    async def test_get_by_id_not_found(self, repository):
        """Test getting provider by ID when it doesn't exist."""
        result = await repository.get_by_id(ShippingProviderId("nonexistent"))
        assert result is None

    async def test_get_all(self, repository, sample_provider):
        """Test getting all providers."""
        await repository.save(sample_provider)
        result = await repository.get_all()
        assert len(result) == 1
        assert result[0] == sample_provider

    async def test_get_all_empty(self, repository):
        """Test getting all providers when none exist."""
        result = await repository.get_all()
        assert result == []

    async def test_get_active(self, repository, sample_provider):
        """Test getting active providers."""
        await repository.save(sample_provider)
        result = await repository.get_active()
        assert len(result) == 1
        assert result[0] == sample_provider

    async def test_get_active_empty(self, repository):
        """Test getting active providers when none exist."""
        result = await repository.get_active()
        assert result == []

    async def test_get_providers_by_method(self, repository, sample_provider):
        """Test getting providers by shipping method."""
        await repository.save(sample_provider)
        result = await repository.get_providers_by_method(ShippingMethod.STANDARD)
        assert len(result) == 1
        assert result[0] == sample_provider

    async def test_get_providers_by_method_empty(self, repository):
        """Test getting providers by shipping method when none exist."""
        result = await repository.get_providers_by_method(ShippingMethod.STANDARD)
        assert result == []

    async def test_delete_provider(self, repository, sample_provider):
        """Test deleting a provider."""
        await repository.save(sample_provider)
        result = await repository.delete(sample_provider.id)
        assert result is True
        retrieved = await repository.get_by_id(sample_provider.id)
        assert retrieved is None

    async def test_delete_provider_not_found(self, repository):
        """Test deleting a provider that doesn't exist."""
        result = await repository.delete(ShippingProviderId("nonexistent"))
        assert result is False

    async def test_inactive_provider(self, repository):
        """Test handling inactive provider."""
        provider = Mock()
        provider.id = ShippingProviderId("provider-123")
        provider.name = "Inactive Provider"
        provider.is_active = False
        provider.supported_methods = [ShippingMethod.STANDARD]

        await repository.save(provider)
        active_providers = await repository.get_active()
        assert len(active_providers) == 0

    async def test_provider_multiple_methods(self, repository):
        """Test provider supporting multiple shipping methods."""
        provider = Mock()
        provider.id = ShippingProviderId("provider-123")
        provider.name = "Multi-Method Provider"
        provider.is_active = True
        provider.supported_methods = [ShippingMethod.STANDARD, ShippingMethod.EXPRESS, ShippingMethod.PRIORITY]

        await repository.save(provider)

        standard_providers = await repository.get_providers_by_method(ShippingMethod.STANDARD)
        assert len(standard_providers) == 1
        assert standard_providers[0] == provider

        express_providers = await repository.get_providers_by_method(ShippingMethod.EXPRESS)
        assert len(express_providers) == 1
        assert express_providers[0] == provider

        priority_providers = await repository.get_providers_by_method(ShippingMethod.PRIORITY)
        assert len(priority_providers) == 1
        assert priority_providers[0] == provider

    async def test_multiple_providers_same_method(self, repository):
        """Test multiple providers supporting the same method."""
        provider1 = Mock()
        provider1.id = ShippingProviderId("provider-1")
        provider1.name = "Provider 1"
        provider1.is_active = True
        provider1.supported_methods = [ShippingMethod.STANDARD]

        provider2 = Mock()
        provider2.id = ShippingProviderId("provider-2")
        provider2.name = "Provider 2"
        provider2.is_active = True
        provider2.supported_methods = [ShippingMethod.STANDARD, ShippingMethod.EXPRESS]

        await repository.save(provider1)
        await repository.save(provider2)

        standard_providers = await repository.get_providers_by_method(ShippingMethod.STANDARD)
        assert len(standard_providers) == 2

        express_providers = await repository.get_providers_by_method(ShippingMethod.EXPRESS)
        assert len(express_providers) == 1
        assert express_providers[0] == provider2 