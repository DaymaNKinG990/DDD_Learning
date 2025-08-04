"""Tests for domain events across all domains."""

import pytest
from datetime import datetime, UTC
from decimal import Decimal

from src.catalog.domain.events import (
    ProductCreated, ProductPriceUpdated, ProductDeactivated, CategoryCreated
)
from src.orders.domain.events import (
    OrderCreated, OrderConfirmed, OrderCancelled, OrderItemAdded
)
from src.users.domain.events import (
    UserCreated, UserUpdated, UserDeactivated
)


from src.shared.domain.events import DomainEvent


class TestCatalogEvents:
    """Test catalog domain events."""

    def test_product_created_event(self):
        """Test ProductCreated event."""
        event = ProductCreated(
            event_type="ProductCreated",
            aggregate_id="prod-123",
            product_id="prod-123",
            name="Test Product",
            description="Test description",
            price="100.00",
            category_id="cat-123",
            sku="test-sku"
        )

        assert event.event_type == "ProductCreated"
        assert event.aggregate_id == "prod-123"
        assert event.product_id == "prod-123"
        assert event.name == "Test Product"
        assert event.description == "Test description"
        assert event.price == "100.00"
        assert event.category_id == "cat-123"
        assert event.sku == "test-sku"
        assert isinstance(event.occurred_on, datetime)

    def test_product_price_updated_event(self):
        """Test ProductPriceUpdated event."""
        event = ProductPriceUpdated(
            event_type="ProductPriceUpdated",
            aggregate_id="prod-123",
            product_id="prod-123",
            old_price="100.00",
            new_price="150.00"
        )

        assert event.event_type == "ProductPriceUpdated"
        assert event.aggregate_id == "prod-123"
        assert event.product_id == "prod-123"
        assert event.old_price == "100.00"
        assert event.new_price == "150.00"

    def test_product_deactivated_event(self):
        """Test ProductDeactivated event."""
        event = ProductDeactivated(
            event_type="ProductDeactivated",
            aggregate_id="prod-123",
            product_id="prod-123",
            reason="Out of stock"
        )

        assert event.event_type == "ProductDeactivated"
        assert event.aggregate_id == "prod-123"
        assert event.product_id == "prod-123"
        assert event.reason == "Out of stock"

    def test_category_created_event(self):
        """Test CategoryCreated event."""
        event = CategoryCreated(
            event_type="CategoryCreated",
            aggregate_id="cat-123",
            category_id="cat-123",
            name="Electronics",
            parent_id=None
        )

        assert event.event_type == "CategoryCreated"
        assert event.aggregate_id == "cat-123"
        assert event.category_id == "cat-123"
        assert event.name == "Electronics"
        assert event.parent_id is None


class TestOrdersEvents:
    """Test orders domain events."""

    def test_order_created_event(self):
        """Test OrderCreated event."""
        event = OrderCreated(
            event_type="OrderCreated",
            aggregate_id="order-123",
            order_id="order-123",
            customer_id="customer-123",
            total="200.00",
            shipping_address="Test address",
            billing_address="Test address"
        )

        assert event.event_type == "OrderCreated"
        assert event.aggregate_id == "order-123"
        assert event.order_id == "order-123"
        assert event.customer_id == "customer-123"
        assert event.total == "200.00"
        assert event.shipping_address == "Test address"
        assert event.billing_address == "Test address"
        assert isinstance(event.occurred_on, datetime)

    def test_order_confirmed_event(self):
        """Test OrderConfirmed event."""
        event = OrderConfirmed(
            event_type="OrderConfirmed",
            aggregate_id="order-123",
            order_id="order-123",
            customer_id="customer-123",
            total="200.00"
        )

        assert event.event_type == "OrderConfirmed"
        assert event.aggregate_id == "order-123"
        assert event.order_id == "order-123"
        assert event.customer_id == "customer-123"
        assert event.total == "200.00"
        assert isinstance(event.occurred_on, datetime)

    def test_order_cancelled_event(self):
        """Test OrderCancelled event."""
        event = OrderCancelled(
            event_type="OrderCancelled",
            aggregate_id="order-123",
            order_id="order-123",
            reason="Customer request"
        )

        assert event.event_type == "OrderCancelled"
        assert event.aggregate_id == "order-123"
        assert event.order_id == "order-123"
        assert event.reason == "Customer request"
        assert isinstance(event.occurred_on, datetime)

    def test_order_item_added_event(self):
        """Test OrderItemAdded event."""
        event = OrderItemAdded(
            event_type="OrderItemAdded",
            aggregate_id="order-123",
            order_id="order-123",
            product_id="prod-123",
            product_name="Test Product",
            quantity=2,
            unit_price="100.00",
            total="200.00"
        )

        assert event.event_type == "OrderItemAdded"
        assert event.aggregate_id == "order-123"
        assert event.order_id == "order-123"
        assert event.product_id == "prod-123"
        assert event.product_name == "Test Product"
        assert event.quantity == 2
        assert event.unit_price == "100.00"
        assert event.total == "200.00"
        assert isinstance(event.occurred_on, datetime)


class TestUsersEvents:
    """Test users domain events."""

    def test_user_created_event(self):
        """Test UserCreated event."""
        event = UserCreated(
            event_type="UserCreated",
            aggregate_id="user-123",
            user_id="user-123",
            email="test@example.com",
            first_name="John",
            last_name="Doe"
        )

        assert event.event_type == "UserCreated"
        assert event.aggregate_id == "user-123"
        assert event.user_id == "user-123"
        assert event.email == "test@example.com"
        assert event.first_name == "John"
        assert event.last_name == "Doe"
        assert isinstance(event.occurred_on, datetime)

    def test_user_updated_event(self):
        """Test UserUpdated event."""
        event = UserUpdated(
            event_type="UserUpdated",
            aggregate_id="user-123",
            user_id="user-123",
            first_name="Jane",
            last_name="Smith",
            phone_number="+1234567890"
        )

        assert event.event_type == "UserUpdated"
        assert event.aggregate_id == "user-123"
        assert event.user_id == "user-123"
        assert event.first_name == "Jane"
        assert event.last_name == "Smith"
        assert event.phone_number == "+1234567890"
        assert isinstance(event.occurred_on, datetime)

    def test_user_deactivated_event(self):
        """Test UserDeactivated event."""
        event = UserDeactivated(
            event_type="UserDeactivated",
            aggregate_id="user-123",
            user_id="user-123",
            reason="Violation of terms"
        )

        assert event.event_type == "UserDeactivated"
        assert event.aggregate_id == "user-123"
        assert event.user_id == "user-123"
        assert event.reason == "Violation of terms"
        assert isinstance(event.occurred_on, datetime)











class TestDomainEventBase:
    """Test base DomainEvent functionality."""

    def test_domain_event_inheritance(self):
        """Test that all events inherit from DomainEvent."""
        events = [
            ProductCreated(event_type="ProductCreated", aggregate_id="test", product_id="test", name="test", description="test", price="100", category_id="test", sku="test"),
            OrderCreated(event_type="OrderCreated", aggregate_id="test", order_id="test", customer_id="test", total="100", shipping_address="test", billing_address="test"),
            UserCreated(event_type="UserCreated", aggregate_id="test", user_id="test", email="test@test.com", first_name="test", last_name="test")
        ]

        for event in events:
            assert isinstance(event, DomainEvent)
            assert hasattr(event, 'event_id')
            assert hasattr(event, 'event_type')
            assert hasattr(event, 'aggregate_id')
            assert hasattr(event, 'occurred_on')
            assert hasattr(event, 'version')

    def test_domain_event_occurred_on(self):
        """Test that all events have occurred_on timestamp."""
        event = ProductCreated(
            event_type="ProductCreated",
            aggregate_id="test",
            product_id="test",
            name="test",
            description="test",
            price="100",
            category_id="test",
            sku="test"
        )

        assert isinstance(event.occurred_on, datetime)
        assert event.occurred_on.tzinfo is not None 