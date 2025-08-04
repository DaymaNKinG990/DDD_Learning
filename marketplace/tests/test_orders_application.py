"""Tests for orders application services."""

import pytest
from unittest.mock import Mock, AsyncMock
from decimal import Decimal
from datetime import datetime, UTC

from src.orders.application.services import OrderService
from src.orders.domain.entities import Order, OrderItem
from src.orders.domain.value_objects import (
    OrderId, OrderStatus, OrderItemId
)
from src.orders.domain.repositories import OrderRepository
from src.catalog.domain.value_objects import ProductId, Price
from src.orders.domain.value_objects import OrderTotal
from src.shared.domain.exceptions import EntityNotFoundError, InvalidOperationError


class TestOrderService:
    """Test OrderService application service."""

    @pytest.fixture
    def mock_order_repository(self):
        """Create mock order repository."""
        return Mock(spec=OrderRepository)

    @pytest.fixture
    def mock_order_item_repository(self):
        """Create mock order item repository."""
        return Mock()

    @pytest.fixture
    def order_service(self, mock_order_repository, mock_order_item_repository):
        """Create order service with mocked dependencies."""
        return OrderService(
            order_repository=mock_order_repository,
            order_item_repository=mock_order_item_repository
        )

    @pytest.fixture
    def sample_order(self):
        """Create sample order for testing."""
        order = Order(
            id=OrderId(value="order-123"),
            customer_id="customer-123",
            items=[
                OrderItem(
                    id=OrderItemId(value="item-1"),
                    product_id="prod-123",
                    product_name="Test Product",
                    quantity=2,
                    unit_price=Decimal("100.00"),
                    total_price=Decimal("200.00")
                )
            ],
            status=OrderStatus.PENDING,
            total=OrderTotal.calculate(Decimal("200.00")),
            shipping_address="ул. Ленина, 1, Москва",
            billing_address="ул. Ленина, 1, Москва"
        )
        return order

    @pytest.fixture
    def confirmed_order(self):
        """Create confirmed order for testing."""
        order = Order(
            id=OrderId(value="order-123"),
            customer_id="customer-123",
            items=[
                OrderItem(
                    id=OrderItemId(value="item-1"),
                    product_id="prod-123",
                    product_name="Test Product",
                    quantity=2,
                    unit_price=Decimal("100.00"),
                    total_price=Decimal("200.00")
                )
            ],
            status=OrderStatus.CONFIRMED,
            total=OrderTotal.calculate(Decimal("200.00")),
            shipping_address="ул. Ленина, 1, Москва",
            billing_address="ул. Ленина, 1, Москва"
        )
        return order

    @pytest.fixture
    def shipped_order(self):
        """Create shipped order for testing."""
        order = Order(
            id=OrderId(value="order-123"),
            customer_id="customer-123",
            items=[
                OrderItem(
                    id=OrderItemId(value="item-1"),
                    product_id="prod-123",
                    product_name="Test Product",
                    quantity=2,
                    unit_price=Decimal("100.00"),
                    total_price=Decimal("200.00")
                )
            ],
            status=OrderStatus.SHIPPED,
            total=OrderTotal.calculate(Decimal("200.00")),
            shipping_address="ул. Ленина, 1, Москва",
            billing_address="ул. Ленина, 1, Москва"
        )
        return order

    @pytest.mark.asyncio
    async def test_create_order(self, order_service, mock_order_repository, sample_order):
        """Test creating an order."""
        # Arrange
        mock_order_repository.save = AsyncMock()
        mock_order_repository.save.return_value = sample_order

        # Act
        result = await order_service.create_order(
            customer_id="customer-123",
            shipping_address="ул. Ленина, 1, Москва",
            billing_address="ул. Ленина, 1, Москва"
        )

        # Assert
        assert result.customer_id == "customer-123"
        assert result.status == OrderStatus.PENDING
        mock_order_repository.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_order_by_id(self, order_service, mock_order_repository, sample_order):
        """Test getting order by ID."""
        # Arrange
        mock_order_repository.get_by_id = AsyncMock()
        mock_order_repository.get_by_id.return_value = sample_order

        # Act
        result = await order_service.get_order_by_id(OrderId(value="order-123"))

        # Assert
        assert result == sample_order
        mock_order_repository.get_by_id.assert_called_once_with(OrderId(value="order-123"))

    @pytest.mark.asyncio
    async def test_get_order_by_id_not_found(self, order_service, mock_order_repository):
        """Test getting order by ID when not found."""
        # Arrange
        mock_order_repository.get_by_id = AsyncMock()
        mock_order_repository.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(EntityNotFoundError, match="Order with id order-123 not found"):
            await order_service.get_order_by_id(OrderId(value="order-123"))

    @pytest.mark.asyncio
    async def test_confirm_order(self, order_service, mock_order_repository, sample_order):
        """Test confirming an order."""
        # Arrange
        mock_order_repository.get_by_id = AsyncMock()
        mock_order_repository.get_by_id.return_value = sample_order
        mock_order_repository.save = AsyncMock()
        mock_order_repository.save.return_value = sample_order

        # Act
        result = await order_service.confirm_order(OrderId(value="order-123"))

        # Assert
        assert result.status == OrderStatus.CONFIRMED
        mock_order_repository.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_ship_order(self, order_service, mock_order_repository, confirmed_order):
        """Test shipping an order."""
        # Arrange
        mock_order_repository.get_by_id = AsyncMock()
        mock_order_repository.get_by_id.return_value = confirmed_order
        mock_order_repository.save = AsyncMock()
        mock_order_repository.save.return_value = confirmed_order

        # Act
        result = await order_service.ship_order(OrderId(value="order-123"))

        # Assert
        assert result.status == OrderStatus.SHIPPED
        mock_order_repository.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_deliver_order(self, order_service, mock_order_repository, shipped_order):
        """Test delivering an order."""
        # Arrange
        mock_order_repository.get_by_id = AsyncMock()
        mock_order_repository.get_by_id.return_value = shipped_order
        mock_order_repository.save = AsyncMock()
        mock_order_repository.save.return_value = shipped_order

        # Act
        result = await order_service.deliver_order(OrderId(value="order-123"))

        # Assert
        assert result.status == OrderStatus.DELIVERED
        mock_order_repository.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_cancel_order(self, order_service, mock_order_repository, sample_order):
        """Test canceling an order."""
        # Arrange
        mock_order_repository.get_by_id = AsyncMock()
        mock_order_repository.get_by_id.return_value = sample_order
        mock_order_repository.save = AsyncMock()
        mock_order_repository.save.return_value = sample_order

        # Act
        result = await order_service.cancel_order(OrderId(value="order-123"))

        # Assert
        assert result.status == OrderStatus.CANCELLED
        mock_order_repository.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_refund_order(self, order_service, mock_order_repository, shipped_order):
        """Test refunding an order."""
        # Arrange
        mock_order_repository.get_by_id = AsyncMock()
        mock_order_repository.get_by_id.return_value = shipped_order
        mock_order_repository.save = AsyncMock()
        mock_order_repository.save.return_value = shipped_order

        # Act
        result = await order_service.refund_order(OrderId(value="order-123"))

        # Assert
        assert result.status == OrderStatus.REFUNDED
        mock_order_repository.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_customer_orders(self, order_service, mock_order_repository, sample_order):
        """Test getting orders by customer ID using get_customer_orders method."""
        # Arrange
        mock_order_repository.get_by_customer = AsyncMock()
        mock_order_repository.get_by_customer.return_value = [sample_order]

        # Act
        result = await order_service.get_customer_orders("customer-123")

        # Assert
        assert len(result) == 1
        assert result[0] == sample_order
        mock_order_repository.get_by_customer.assert_called_once_with("customer-123")

    @pytest.mark.asyncio
    async def test_get_orders_by_customer(self, order_service, mock_order_repository, sample_order):
        """Test getting orders by customer ID."""
        # Arrange
        mock_order_repository.get_by_customer = AsyncMock()
        mock_order_repository.get_by_customer.return_value = [sample_order]

        # Act
        result = await order_service.get_orders_by_customer("customer-123")

        # Assert
        assert len(result) == 1
        assert result[0] == sample_order
        mock_order_repository.get_by_customer.assert_called_once_with("customer-123")

    @pytest.mark.asyncio
    async def test_add_item_to_order(self, order_service, mock_order_repository, sample_order):
        """Test adding item to order."""
        # Arrange
        mock_order_repository.get_by_id = AsyncMock()
        mock_order_repository.get_by_id.return_value = sample_order
        mock_order_repository.save = AsyncMock()
        mock_order_repository.save.return_value = sample_order

        # Act
        result = await order_service.add_item_to_order(
            order_id=OrderId(value="order-123"),
            product_id="prod-456",
            product_name="New Product",
            quantity=3,
            unit_price=Decimal("150.00")
        )

        # Assert
        assert len(result.items) == 2
        mock_order_repository.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_add_item_to_order_invalid_status(self, order_service, mock_order_repository, confirmed_order):
        """Test adding item to order with invalid status."""
        # Arrange
        mock_order_repository.get_by_id = AsyncMock()
        mock_order_repository.get_by_id.return_value = confirmed_order

        # Act & Assert
        with pytest.raises(InvalidOperationError, match="Can only add items to pending orders"):
            await order_service.add_item_to_order(
                order_id=OrderId(value="order-123"),
                product_id="prod-456",
                product_name="New Product",
                quantity=3,
                unit_price=Decimal("150.00")
            )

    @pytest.mark.asyncio
    async def test_remove_item_from_order(self, order_service, mock_order_repository, sample_order):
        """Test removing item from order."""
        # Arrange
        mock_order_repository.get_by_id = AsyncMock()
        mock_order_repository.get_by_id.return_value = sample_order
        mock_order_repository.save = AsyncMock()
        mock_order_repository.save.return_value = sample_order

        # Act
        result = await order_service.remove_item_from_order(
            order_id=OrderId(value="order-123"),
            product_id="prod-123"
        )

        # Assert
        assert len(result.items) == 0
        mock_order_repository.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_remove_item_from_order_invalid_status(self, order_service, mock_order_repository, confirmed_order):
        """Test removing item from order with invalid status."""
        # Arrange
        mock_order_repository.get_by_id = AsyncMock()
        mock_order_repository.get_by_id.return_value = confirmed_order

        # Act & Assert
        with pytest.raises(InvalidOperationError, match="Can only remove items from pending orders"):
            await order_service.remove_item_from_order(
                order_id=OrderId(value="order-123"),
                product_id="prod-123"
            )

    @pytest.mark.asyncio
    async def test_get_pending_orders(self, order_service, mock_order_repository, sample_order):
        """Test getting pending orders."""
        # Arrange
        mock_order_repository.get_pending_orders = AsyncMock()
        mock_order_repository.get_pending_orders.return_value = [sample_order]

        # Act
        result = await order_service.get_pending_orders()

        # Assert
        assert len(result) == 1
        assert result[0] == sample_order
        mock_order_repository.get_pending_orders.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_orders_by_status(self, order_service, mock_order_repository, sample_order):
        """Test getting orders by status."""
        # Arrange
        mock_order_repository.get_orders_by_status = AsyncMock()
        mock_order_repository.get_orders_by_status.return_value = [sample_order]

        # Act
        result = await order_service.get_orders_by_status("pending")

        # Assert
        assert len(result) == 1
        assert result[0] == sample_order
        mock_order_repository.get_orders_by_status.assert_called_once_with("pending") 