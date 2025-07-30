"""Tests for orders domain models."""

from decimal import Decimal

import pytest
from src.orders.domain.entities import Order, OrderItem
from src.orders.domain.value_objects import (
    OrderId,
    OrderStatus,
    OrderTotal,
)


class TestOrderId:
    """Test OrderId value object."""

    def test_create_order_id(self):
        """Test creating an order ID."""
        order_id = OrderId(value="order_123")
        assert order_id.value == "order_123"
        assert str(order_id) == "order_123"

    def test_order_id_hash(self):
        """Test order ID hash."""
        order_id1 = OrderId(value="order_123")
        order_id2 = OrderId(value="order_123")
        order_id3 = OrderId(value="order_456")

        assert hash(order_id1) == hash(order_id2)
        assert hash(order_id1) != hash(order_id3)


class TestOrderTotal:
    """Test OrderTotal value object."""

    def test_create_order_total(self):
        """Test creating an order total."""
        total = OrderTotal(
            subtotal=Decimal("100"),
            tax=Decimal("20"),
            shipping=Decimal("10"),
            discount=Decimal("5"),
            total=Decimal("125"),
            currency="RUB",
        )

        assert total.subtotal == Decimal("100")
        assert total.tax == Decimal("20")
        assert total.shipping == Decimal("10")
        assert total.discount == Decimal("5")
        assert total.total == Decimal("125")
        assert total.currency == "RUB"

    def test_calculate_order_total(self):
        """Test calculating order total."""
        total = OrderTotal.calculate(
            subtotal=Decimal("100"),
            tax_rate=Decimal("0.20"),
            shipping_cost=Decimal("10"),
            discount=Decimal("5"),
            currency="RUB",
        )

        assert total.subtotal == Decimal("100")
        assert total.tax == Decimal("20")  # 100 * 0.20
        assert total.shipping == Decimal("10")
        assert total.discount == Decimal("5")
        assert total.total == Decimal("125")  # 100 + 20 + 10 - 5
        assert total.currency == "RUB"

    def test_order_total_validation_negative_amount(self):
        """Test order total validation with negative amount."""
        with pytest.raises(ValueError, match="Subtotal cannot be negative"):
            OrderTotal(
                subtotal=Decimal("-10"),
                tax=Decimal("0"),
                shipping=Decimal("0"),
                total=Decimal("-10"),
            )


class TestOrderItem:
    """Test OrderItem entity."""

    def test_create_order_item(self):
        """Test creating an order item."""
        item = OrderItem.create(
            product_id="prod_123",
            product_name="Test Product",
            quantity=2,
            unit_price=Decimal("50"),
        )

        assert item.product_id == "prod_123"
        assert item.product_name == "Test Product"
        assert item.quantity == 2
        assert item.unit_price == Decimal("50")
        assert item.total_price == Decimal("100")  # 2 * 50

    def test_create_order_item_invalid_quantity(self):
        """Test creating order item with invalid quantity."""
        with pytest.raises(ValueError, match="Quantity must be positive"):
            OrderItem.create(
                product_id="prod_123",
                product_name="Test Product",
                quantity=0,
                unit_price=Decimal("50"),
            )

    def test_create_order_item_invalid_price(self):
        """Test creating order item with invalid price."""
        with pytest.raises(ValueError, match="Unit price must be positive"):
            OrderItem.create(
                product_id="prod_123",
                product_name="Test Product",
                quantity=2,
                unit_price=Decimal("-50"),
            )

    def test_update_order_item_quantity(self):
        """Test updating order item quantity."""
        item = OrderItem.create(
            product_id="prod_123",
            product_name="Test Product",
            quantity=2,
            unit_price=Decimal("50"),
        )

        item.update_quantity(3)

        assert item.quantity == 3
        assert item.total_price == Decimal("150")  # 3 * 50
        assert item.id == item.id


class TestOrder:
    """Test Order entity."""

    def test_create_order(self):
        """Test creating an order."""
        order = Order.create(
            customer_id="customer_123",
            shipping_address="123 Main St",
            billing_address="123 Main St",
            notes="Test order",
        )

        assert order.customer_id == "customer_123"
        assert order.shipping_address == "123 Main St"
        assert order.billing_address == "123 Main St"
        assert order.notes == "Test order"
        assert order.status == OrderStatus.PENDING
        assert len(order.items) == 0
        assert order.total.total == Decimal("0")

    def test_add_item_to_order(self):
        """Test adding item to order."""
        order = Order.create(
            customer_id="customer_123",
            shipping_address="123 Main St",
            billing_address="123 Main St",
        )

        item = OrderItem.create(
            product_id="prod_123",
            product_name="Test Product",
            quantity=2,
            unit_price=Decimal("50"),
        )

        order.add_item(item)

        assert len(order.items) == 1
        assert order.items[0].product_id == "prod_123"
        assert order.total.subtotal == Decimal("100")
        assert order.total.total > Decimal("0")

    def test_add_duplicate_item_to_order(self):
        """Test adding duplicate item to order."""
        order = Order.create(
            customer_id="customer_123",
            shipping_address="123 Main St",
            billing_address="123 Main St",
        )

        item1 = OrderItem.create(
            product_id="prod_123",
            product_name="Test Product",
            quantity=2,
            unit_price=Decimal("50"),
        )

        item2 = OrderItem.create(
            product_id="prod_123",
            product_name="Test Product",
            quantity=1,
            unit_price=Decimal("50"),
        )

        order.add_item(item1)
        order.add_item(item2)

        assert len(order.items) == 1
        assert order.items[0].quantity == 3  # 2 + 1
        assert order.items[0].total_price == Decimal("150")  # 3 * 50

    def test_remove_item_from_order(self):
        """Test removing item from order."""
        order = Order.create(
            customer_id="customer_123",
            shipping_address="123 Main St",
            billing_address="123 Main St",
        )

        item = OrderItem.create(
            product_id="prod_123",
            product_name="Test Product",
            quantity=2,
            unit_price=Decimal("50"),
        )

        order.add_item(item)
        order.remove_item("prod_123")

        assert len(order.items) == 0
        assert order.total.total == Decimal("0")

    def test_confirm_order(self):
        """Test confirming an order."""
        order = Order.create(
            customer_id="customer_123",
            shipping_address="123 Main St",
            billing_address="123 Main St",
        )

        order.confirm()

        assert order.status == OrderStatus.CONFIRMED
        assert order.id == order.id

    def test_confirm_already_confirmed_order(self):
        """Test confirming an already confirmed order."""
        order = Order.create(
            customer_id="customer_123",
            shipping_address="123 Main St",
            billing_address="123 Main St",
        )

        order.confirm()

        with pytest.raises(ValueError, match="Only pending orders can be confirmed"):
            order.confirm()

    def test_ship_order(self):
        """Test shipping an order."""
        order = Order.create(
            customer_id="customer_123",
            shipping_address="123 Main St",
            billing_address="123 Main St",
        )

        order.confirm()
        order.ship()

        assert order.status == OrderStatus.SHIPPED
        assert order.id == order.id

    def test_ship_pending_order(self):
        """Test shipping a pending order."""
        order = Order.create(
            customer_id="customer_123",
            shipping_address="123 Main St",
            billing_address="123 Main St",
        )

        with pytest.raises(
            ValueError, match="Only confirmed or processing orders can be shipped"
        ):
            order.ship()

    def test_deliver_order(self):
        """Test delivering an order."""
        order = Order.create(
            customer_id="customer_123",
            shipping_address="123 Main St",
            billing_address="123 Main St",
        )

        order.confirm()
        order.ship()
        order.deliver()

        assert order.status == OrderStatus.DELIVERED
        assert order.id == order.id

    def test_deliver_unshipped_order(self):
        """Test delivering an unshipped order."""
        order = Order.create(
            customer_id="customer_123",
            shipping_address="123 Main St",
            billing_address="123 Main St",
        )

        order.confirm()

        with pytest.raises(ValueError, match="Only shipped orders can be delivered"):
            order.deliver()

    def test_cancel_order(self):
        """Test cancelling an order."""
        order = Order.create(
            customer_id="customer_123",
            shipping_address="123 Main St",
            billing_address="123 Main St",
        )

        order.cancel()

        assert order.status == OrderStatus.CANCELLED
        assert order.id == order.id

    def test_cancel_delivered_order(self):
        """Test cancelling a delivered order."""
        order = Order.create(
            customer_id="customer_123",
            shipping_address="123 Main St",
            billing_address="123 Main St",
        )

        order.confirm()
        order.ship()
        order.deliver()

        with pytest.raises(
            ValueError, match="Cannot cancel delivered or refunded order"
        ):
            order.cancel()

    def test_refund_order(self):
        """Test refunding an order."""
        order = Order.create(
            customer_id="customer_123",
            shipping_address="123 Main St",
            billing_address="123 Main St",
        )

        order.confirm()
        order.refund()

        assert order.status == OrderStatus.REFUNDED
        assert order.id == order.id
