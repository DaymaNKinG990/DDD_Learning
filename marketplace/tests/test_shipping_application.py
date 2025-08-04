"""Tests for shipping application services."""

import pytest
from decimal import Decimal
from datetime import datetime, UTC
from unittest.mock import AsyncMock, Mock

from src.shipping.application.services import ShipmentService, ShippingProviderService
from src.shipping.domain.entities import Shipment, ShippingProvider
from src.shipping.domain.value_objects import (
    ShippingId, ShippingProviderId, ShippingStatus, ShippingMethod, ShippingCost, DeliveryAddress
)
from src.orders.domain.value_objects import OrderId
from src.shared.domain.exceptions import EntityNotFoundError


class TestShipmentService:
    """Test ShipmentService."""

    @pytest.fixture
    def shipment_repository(self):
        """Create mock shipment repository."""
        return AsyncMock()

    @pytest.fixture
    def event_bus(self):
        """Create mock event bus."""
        return AsyncMock()

    @pytest.fixture
    def service(self, shipment_repository, event_bus):
        """Create shipment service."""
        return ShipmentService(shipment_repository, event_bus)

    @pytest.fixture
    def sample_shipment(self):
        """Create sample shipment."""
        return Shipment(
            id=ShippingId(value="shipment_123"),
            order_id=OrderId(value="order_123"),
            method=ShippingMethod.STANDARD,
            cost=ShippingCost(amount=Decimal("10.00"), currency="RUB"),
            delivery_address=DeliveryAddress(
                street="ул. Ленина, 1",
                city="Москва",
                state="Москва",
                postal_code="123456",
                country="Россия"
            ),
            carrier="Почта России",
        )

    @pytest.mark.asyncio
    async def test_create_shipment(self, service, shipment_repository):
        """Test creating a shipment."""
        # Arrange
        order_id = "order_123"
        method = ShippingMethod.STANDARD
        cost = ShippingCost(amount=Decimal("10.00"), currency="RUB")
        delivery_address = DeliveryAddress(
            street="ул. Ленина, 1",
            city="Москва",
            state="Москва",
            postal_code="123456",
            country="Россия"
        )
        carrier = "Почта России"
        notes = "Handle with care"
        
        expected_shipment = Shipment(
            id=ShippingId(value="shipment_order_123_STANDARD"),
            order_id=OrderId(value=order_id),
            method=method,
            cost=cost,
            delivery_address=delivery_address,
            carrier=carrier,
            notes=notes,
        )
        shipment_repository.save.return_value = expected_shipment

        # Act
        result = await service.create_shipment(order_id, method, cost, delivery_address, carrier, notes)

        # Assert
        assert result == expected_shipment
        shipment_repository.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_shipment_found(self, service, shipment_repository, sample_shipment):
        """Test getting shipment that exists."""
        # Arrange
        shipment_id = "shipment_123"
        shipment_repository.get_by_id.return_value = sample_shipment

        # Act
        result = await service.get_shipment(shipment_id)

        # Assert
        assert result == sample_shipment
        shipment_repository.get_by_id.assert_called_once_with(ShippingId(value=shipment_id))

    @pytest.mark.asyncio
    async def test_get_shipment_not_found(self, service, shipment_repository):
        """Test getting shipment that doesn't exist."""
        # Arrange
        shipment_id = "shipment_999"
        shipment_repository.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(EntityNotFoundError, match=f"Shipment with ID {shipment_id} not found"):
            await service.get_shipment(shipment_id)

    @pytest.mark.asyncio
    async def test_get_shipments_by_order(self, service, shipment_repository, sample_shipment):
        """Test getting shipments by order."""
        # Arrange
        order_id = "order_123"
        expected_shipments = [sample_shipment]
        shipment_repository.get_by_order_id.return_value = expected_shipments

        # Act
        result = await service.get_shipments_by_order(order_id)

        # Assert
        assert result == expected_shipments
        shipment_repository.get_by_order_id.assert_called_once_with(OrderId(value=order_id))

    @pytest.mark.asyncio
    async def test_get_shipments_by_status(self, service, shipment_repository, sample_shipment):
        """Test getting shipments by status."""
        # Arrange
        status = ShippingStatus.PENDING
        expected_shipments = [sample_shipment]
        shipment_repository.get_by_status.return_value = expected_shipments

        # Act
        result = await service.get_shipments_by_status(status)

        # Assert
        assert result == expected_shipments
        shipment_repository.get_by_status.assert_called_once_with(status)

    @pytest.mark.asyncio
    async def test_assign_tracking_number(self, service, shipment_repository, sample_shipment):
        """Test assigning tracking number to shipment."""
        # Arrange
        shipment_id = "shipment_123"
        tracking_number = "TRK123456789"
        shipment_repository.get_by_id.return_value = sample_shipment
        shipment_repository.save.return_value = sample_shipment

        # Act
        result = await service.assign_tracking_number(shipment_id, tracking_number)

        # Assert
        assert result == sample_shipment
        assert sample_shipment.tracking_number.value == tracking_number
        shipment_repository.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_shipment_status(self, service, shipment_repository, sample_shipment):
        """Test updating shipment status."""
        # Arrange
        shipment_id = "shipment_123"
        status = ShippingStatus.IN_TRANSIT
        shipment_repository.get_by_id.return_value = sample_shipment
        shipment_repository.save.return_value = sample_shipment

        # Act
        result = await service.update_shipment_status(shipment_id, status)

        # Assert
        assert result == sample_shipment
        assert sample_shipment.status == status
        shipment_repository.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_set_estimated_delivery_date(self, service, shipment_repository, sample_shipment):
        """Test setting estimated delivery date."""
        # Arrange
        shipment_id = "shipment_123"
        delivery_date = datetime(2024, 12, 25, tzinfo=UTC)
        shipment_repository.get_by_id.return_value = sample_shipment
        shipment_repository.save.return_value = sample_shipment

        # Act
        result = await service.set_estimated_delivery_date(shipment_id, delivery_date)

        # Assert
        assert result == sample_shipment
        assert sample_shipment.estimated_delivery_date == delivery_date
        shipment_repository.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_add_shipment_note(self, service, shipment_repository, sample_shipment):
        """Test adding note to shipment."""
        # Arrange
        shipment_id = "shipment_123"
        note = "Package delivered to neighbor"
        shipment_repository.get_by_id.return_value = sample_shipment
        shipment_repository.save.return_value = sample_shipment

        # Act
        result = await service.add_shipment_note(shipment_id, note)

        # Assert
        assert result == sample_shipment
        assert note in sample_shipment.notes
        shipment_repository.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_shipment(self, service, shipment_repository):
        """Test deleting shipment."""
        # Arrange
        shipment_id = "shipment_123"
        shipment_repository.delete.return_value = True

        # Act
        result = await service.delete_shipment(shipment_id)

        # Assert
        assert result is True
        shipment_repository.delete.assert_called_once_with(ShippingId(value=shipment_id))


class TestShippingProviderService:
    """Test ShippingProviderService."""

    @pytest.fixture
    def shipping_provider_repository(self):
        """Create mock shipping provider repository."""
        return AsyncMock()

    @pytest.fixture
    def event_bus(self):
        """Create mock event bus."""
        return AsyncMock()

    @pytest.fixture
    def service(self, shipping_provider_repository, event_bus):
        """Create shipping provider service."""
        return ShippingProviderService(shipping_provider_repository, event_bus)

    @pytest.fixture
    def sample_provider(self):
        """Create sample shipping provider."""
        return ShippingProvider(
            id=ShippingProviderId(value="provider_123"),
            name="Почта России",
            code="russian_post",
            base_cost=ShippingCost(amount=Decimal("10.00"), currency="RUB"),
            delivery_time_days=5,
            supported_methods=[ShippingMethod.STANDARD, ShippingMethod.EXPRESS],
        )

    @pytest.mark.asyncio
    async def test_create_shipping_provider(self, service, shipping_provider_repository):
        """Test creating a shipping provider."""
        # Arrange
        name = "Почта России"
        code = "russian_post"
        base_cost = ShippingCost(amount=Decimal("10.00"), currency="RUB")
        delivery_time_days = 5
        supported_methods = [ShippingMethod.STANDARD, ShippingMethod.EXPRESS]
        
        expected_provider = ShippingProvider(
            id=ShippingProviderId(value="provider_russian_post"),
            name=name,
            code=code,
            base_cost=base_cost,
            delivery_time_days=delivery_time_days,
            supported_methods=supported_methods,
        )
        shipping_provider_repository.save.return_value = expected_provider

        # Act
        result = await service.create_shipping_provider(
            name, code, base_cost, delivery_time_days, supported_methods
        )

        # Assert
        assert result == expected_provider
        shipping_provider_repository.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_shipping_provider_found(self, service, shipping_provider_repository, sample_provider):
        """Test getting shipping provider that exists."""
        # Arrange
        provider_id = "provider_123"
        shipping_provider_repository.get_by_id.return_value = sample_provider

        # Act
        result = await service.get_shipping_provider(provider_id)

        # Assert
        assert result == sample_provider
        shipping_provider_repository.get_by_id.assert_called_once_with(ShippingProviderId(value=provider_id))

    @pytest.mark.asyncio
    async def test_get_shipping_provider_not_found(self, service, shipping_provider_repository):
        """Test getting shipping provider that doesn't exist."""
        # Arrange
        provider_id = "provider_999"
        shipping_provider_repository.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(EntityNotFoundError, match=f"Shipping provider with ID {provider_id} not found"):
            await service.get_shipping_provider(provider_id)

    @pytest.mark.asyncio
    async def test_get_all_providers(self, service, shipping_provider_repository, sample_provider):
        """Test getting all shipping providers."""
        # Arrange
        expected_providers = [sample_provider]
        shipping_provider_repository.get_all.return_value = expected_providers

        # Act
        result = await service.get_all_providers()

        # Assert
        assert result == expected_providers
        shipping_provider_repository.get_all.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_active_providers(self, service, shipping_provider_repository, sample_provider):
        """Test getting active shipping providers."""
        # Arrange
        expected_providers = [sample_provider]
        shipping_provider_repository.get_active.return_value = expected_providers

        # Act
        result = await service.get_active_providers()

        # Assert
        assert result == expected_providers
        shipping_provider_repository.get_active.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_providers_by_method(self, service, shipping_provider_repository, sample_provider):
        """Test getting providers by method."""
        # Arrange
        method = ShippingMethod.STANDARD
        expected_providers = [sample_provider]
        shipping_provider_repository.get_providers_by_method.return_value = expected_providers

        # Act
        result = await service.get_providers_by_method(method)

        # Assert
        assert result == expected_providers
        shipping_provider_repository.get_providers_by_method.assert_called_once_with(method)

    @pytest.mark.asyncio
    async def test_activate_provider(self, service, shipping_provider_repository, sample_provider):
        """Test activating shipping provider."""
        # Arrange
        provider_id = "provider_123"
        sample_provider.is_active = False
        shipping_provider_repository.get_by_id.return_value = sample_provider
        shipping_provider_repository.save.return_value = sample_provider

        # Act
        result = await service.activate_provider(provider_id)

        # Assert
        assert result == sample_provider
        assert sample_provider.is_active is True
        shipping_provider_repository.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_deactivate_provider(self, service, shipping_provider_repository, sample_provider):
        """Test deactivating shipping provider."""
        # Arrange
        provider_id = "provider_123"
        sample_provider.is_active = True
        shipping_provider_repository.get_by_id.return_value = sample_provider
        shipping_provider_repository.save.return_value = sample_provider

        # Act
        result = await service.deactivate_provider(provider_id)

        # Assert
        assert result == sample_provider
        assert sample_provider.is_active is False
        shipping_provider_repository.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_calculate_shipping_cost(self, service, shipping_provider_repository):
        """Test calculating shipping cost."""
        # Arrange
        provider_id = "provider_123"
        method = ShippingMethod.STANDARD
        weight = 2.5
        expected_cost = ShippingCost(amount=Decimal("25.00"), currency="RUB")
        
        # Create a mock provider
        mock_provider = Mock()
        mock_provider.calculate_cost.return_value = expected_cost
        
        shipping_provider_repository.get_by_id.return_value = mock_provider

        # Act
        result = await service.calculate_shipping_cost(provider_id, method, weight)

        # Assert
        assert result == expected_cost
        mock_provider.calculate_cost.assert_called_once_with(method, weight)

    @pytest.mark.asyncio
    async def test_get_delivery_time(self, service, shipping_provider_repository):
        """Test getting delivery time."""
        # Arrange
        provider_id = "provider_123"
        method = ShippingMethod.STANDARD
        expected_delivery_time = 5
        
        # Create a mock provider
        mock_provider = Mock()
        mock_provider.get_delivery_time.return_value = expected_delivery_time
        
        shipping_provider_repository.get_by_id.return_value = mock_provider

        # Act
        result = await service.get_delivery_time(provider_id, method)

        # Assert
        assert result == expected_delivery_time
        mock_provider.get_delivery_time.assert_called_once_with(method)

    @pytest.mark.asyncio
    async def test_delete_provider(self, service, shipping_provider_repository):
        """Test deleting shipping provider."""
        # Arrange
        provider_id = "provider_123"
        shipping_provider_repository.delete.return_value = True

        # Act
        result = await service.delete_provider(provider_id)

        # Assert
        assert result is True
        shipping_provider_repository.delete.assert_called_once_with(ShippingProviderId(value=provider_id)) 