"""Tests for shipping domain."""

from decimal import Decimal

import pytest
from src.shipping.domain.entities import Shipment, ShippingProvider
from src.shipping.domain.value_objects import (
    DeliveryAddress,
    ShippingCost,
    ShippingId,
    ShippingMethod,
    ShippingStatus,
    TrackingNumber,
)


class TestShipment:
    """Test Shipment entity."""

    def test_create_shipment(self):
        """Test creating a shipment."""
        from src.orders.domain.value_objects import OrderId

        order_id = OrderId(value="order-123")
        method = ShippingMethod.STANDARD
        cost = ShippingCost(amount=Decimal("500"), currency="RUB")
        address = DeliveryAddress(
            street="ул. Ленина, 1",
            city="Москва",
            postal_code="123456",
            country="Russia"
        )

        shipment = Shipment(
            id=ShippingId(value="shipment-123"),
            order_id=order_id,
            method=method,
            cost=cost,
            delivery_address=address,
            carrier="Почта России"
        )

        assert shipment.order_id == order_id
        assert shipment.method == method
        assert shipment.cost == cost
        assert shipment.status == ShippingStatus.PENDING
        assert shipment.tracking_number is None

    def test_assign_tracking_number(self):
        """Test assigning tracking number."""
        from src.orders.domain.value_objects import OrderId

        shipment = Shipment(
            id=ShippingId(value="shipment-456"),
            order_id=OrderId(value="order-123"),
            method=ShippingMethod.EXPRESS,
            cost=ShippingCost(amount=Decimal("1000"), currency="RUB"),
            delivery_address=DeliveryAddress(
                street="ул. Ленина, 1",
                city="Москва",
                postal_code="123456"
            ),
            carrier="DHL"
        )

        tracking_number = "TRK123456789"
        shipment.assign_tracking_number(tracking_number)

        assert shipment.tracking_number.value == tracking_number

    def test_update_status(self):
        """Test updating shipment status."""
        from src.orders.domain.value_objects import OrderId

        shipment = Shipment(
            id=ShippingId(value="shipment-789"),
            order_id=OrderId(value="order-123"),
            method=ShippingMethod.STANDARD,
            cost=ShippingCost(amount=Decimal("500"), currency="RUB"),
            delivery_address=DeliveryAddress(
                street="ул. Ленина, 1",
                city="Москва",
                postal_code="123456"
            ),
            carrier="Почта России"
        )

        shipment.update_status(ShippingStatus.IN_TRANSIT)
        assert shipment.status == ShippingStatus.IN_TRANSIT

        shipment.update_status(ShippingStatus.DELIVERED)
        assert shipment.status == ShippingStatus.DELIVERED
        assert shipment.actual_delivery_date is not None

    def test_add_note(self):
        """Test adding notes to shipment."""
        from src.orders.domain.value_objects import OrderId

        shipment = Shipment(
            id=ShippingId(value="shipment-101"),
            order_id=OrderId(value="order-123"),
            method=ShippingMethod.STANDARD,
            cost=ShippingCost(amount=Decimal("500"), currency="RUB"),
            delivery_address=DeliveryAddress(
                street="ул. Ленина, 1",
                city="Москва",
                postal_code="123456"
            ),
            carrier="Почта России"
        )

        shipment.add_note("Package picked up")
        assert shipment.notes == "Package picked up"

        shipment.add_note("In transit")
        assert "Package picked up" in shipment.notes
        assert "In transit" in shipment.notes


class TestShippingProvider:
    """Test ShippingProvider entity."""

    def test_create_shipping_provider(self):
        """Test creating a shipping provider."""
        provider = ShippingProvider(
            id="provider-123",
            name="Почта России",
            code="RUSSIAN_POST",
            supported_methods=[ShippingMethod.STANDARD, ShippingMethod.EXPRESS],
            base_cost=ShippingCost(amount=Decimal("300"), currency="RUB"),
            delivery_time_days=5,
            express_delivery_time_days=2
        )

        assert provider.name == "Почта России"
        assert provider.code == "RUSSIAN_POST"
        assert provider.is_active is True
        assert len(provider.supported_methods) == 2

    def test_supports_method(self):
        """Test checking if provider supports method."""
        provider = ShippingProvider(
            id="provider-456",
            name="DHL",
            code="DHL",
            supported_methods=[ShippingMethod.EXPRESS, ShippingMethod.PREMIUM],
            base_cost=ShippingCost(amount=Decimal("1000"), currency="RUB"),
            delivery_time_days=3
        )

        assert provider.supports_method(ShippingMethod.EXPRESS) is True
        assert provider.supports_method(ShippingMethod.STANDARD) is False

    def test_get_delivery_time(self):
        """Test getting delivery time for method."""
        provider = ShippingProvider(
            id="provider-789",
            name="FedEx",
            code="FEDEX",
            supported_methods=[
                ShippingMethod.STANDARD, 
                ShippingMethod.EXPRESS, 
                ShippingMethod.SAME_DAY
            ],
            base_cost=ShippingCost(amount=Decimal("800"), currency="RUB"),
            delivery_time_days=4,
            express_delivery_time_days=1,
            same_day_delivery_available=True
        )

        assert provider.get_delivery_time(ShippingMethod.STANDARD) == 4
        assert provider.get_delivery_time(ShippingMethod.EXPRESS) == 1
        assert provider.get_delivery_time(ShippingMethod.SAME_DAY) == 1

    def test_calculate_cost(self):
        """Test calculating shipping cost."""
        provider = ShippingProvider(
            id="provider-test",
            name="Test Provider",
            code="TEST",
            supported_methods=[ShippingMethod.STANDARD, ShippingMethod.EXPRESS],
            base_cost=ShippingCost(amount=Decimal("100"), currency="RUB"),
            delivery_time_days=3,
            express_delivery_time_days=1
        )

        standard_cost = provider.calculate_cost(ShippingMethod.STANDARD, weight=2.0)
        assert standard_cost.amount == Decimal("200")  # 100 * 1.0 * 2.0

        express_cost = provider.calculate_cost(ShippingMethod.EXPRESS, weight=1.5)
        assert express_cost.amount == Decimal("300")  # 100 * 2.0 * 1.5

    def test_activate_deactivate(self):
        """Test activating and deactivating provider."""
        provider = ShippingProvider(
            id="provider-activate",
            name="Test Provider",
            code="TEST",
            supported_methods=[ShippingMethod.STANDARD],
            base_cost=ShippingCost(amount=Decimal("100"), currency="RUB"),
            delivery_time_days=3
        )

        assert provider.is_active is True

        provider.deactivate()
        assert provider.is_active is False

        provider.activate()
        assert provider.is_active is True


class TestValueObjects:
    """Test shipping value objects."""

    def test_tracking_number_validation(self):
        """Test tracking number validation."""
        # Valid tracking number
        tracking = TrackingNumber(value="TRK123456789")
        assert tracking.value == "TRK123456789"

        # Invalid tracking number (too short)
        with pytest.raises(ValueError, match="at least 5 characters"):
            TrackingNumber(value="123")

    def test_shipping_cost_validation(self):
        """Test shipping cost validation."""
        # Valid cost
        cost = ShippingCost(amount=Decimal("500"), currency="RUB")
        assert cost.amount == Decimal("500")
        assert cost.currency == "RUB"

        # Invalid cost (negative)
        with pytest.raises(ValueError, match="cannot be negative"):
            ShippingCost(amount=Decimal("-100"), currency="RUB")

    def test_delivery_address_validation(self):
        """Test delivery address validation."""
        # Valid address
        address = DeliveryAddress(
            street="ул. Ленина, 1",
            city="Москва",
            postal_code="123456"
        )
        assert str(address) == "ул. Ленина, 1, Москва, 123456, Russia"

        # Invalid address (empty street)
        with pytest.raises(ValueError, match="cannot be empty"):
            DeliveryAddress(
                street="",
                city="Москва",
                postal_code="123456"
            )
