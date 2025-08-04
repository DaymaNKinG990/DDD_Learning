"""Tests for orders application queries."""

import pytest
from datetime import datetime, UTC
from unittest.mock import AsyncMock

from src.orders.application.queries import (
    OrderReadModel,
    OrderItemReadModel,
    OrderSummaryReadModel,
    GetOrderQuery,
    GetOrdersByCustomerQuery,
    GetOrdersByStatusQuery,
    GetOrdersByDateRangeQuery,
    GetOrderSummaryQuery,
    GetCustomerOrderHistoryQuery,
    InMemoryOrderQueryHandler,
)


class TestOrderReadModel:
    """Test OrderReadModel."""

    def test_order_read_model_creation(self):
        """Test creating an OrderReadModel."""
        order = OrderReadModel(
            id="order-123",
            customer_id="customer-123",
            customer_name="John Doe",
            status="pending",
            total="200.00",
            shipping_address="ул. Ленина, 1, Москва",
            billing_address="ул. Ленина, 1, Москва",
            notes="Test order",
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
            items=[]
        )

        assert order.id == "order-123"
        assert order.customer_id == "customer-123"
        assert order.customer_name == "John Doe"
        assert order.status == "pending"
        assert order.total == "200.00"
        assert order.shipping_address == "ул. Ленина, 1, Москва"
        assert order.billing_address == "ул. Ленина, 1, Москва"
        assert order.notes == "Test order"
        assert isinstance(order.created_at, datetime)
        assert isinstance(order.updated_at, datetime)
        assert order.items == []

    def test_order_read_model_minimal(self):
        """Test creating an OrderReadModel with minimal fields."""
        order = OrderReadModel(
            id="order-123",
            customer_id="customer-123",
            status="pending",
            total="200.00",
            shipping_address="ул. Ленина, 1, Москва",
            billing_address="ул. Ленина, 1, Москва",
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC)
        )

        assert order.id == "order-123"
        assert order.customer_name is None
        assert order.notes is None
        assert order.items == []


class TestOrderItemReadModel:
    """Test OrderItemReadModel."""

    def test_order_item_read_model_creation(self):
        """Test creating an OrderItemReadModel."""
        item = OrderItemReadModel(
            id="item-123",
            order_id="order-123",
            product_id="prod-123",
            product_name="Test Product",
            quantity=2,
            unit_price="100.00",
            total="200.00"
        )

        assert item.id == "item-123"
        assert item.order_id == "order-123"
        assert item.product_id == "prod-123"
        assert item.product_name == "Test Product"
        assert item.quantity == 2
        assert item.unit_price == "100.00"
        assert item.total == "200.00"


class TestOrderSummaryReadModel:
    """Test OrderSummaryReadModel."""

    def test_order_summary_read_model_creation(self):
        """Test creating an OrderSummaryReadModel."""
        summary = OrderSummaryReadModel(
            id="order-123",
            customer_id="customer-123",
            status="pending",
            total="200.00",
            item_count=2,
            created_at=datetime.now(UTC)
        )

        assert summary.id == "order-123"
        assert summary.customer_id == "customer-123"
        assert summary.status == "pending"
        assert summary.total == "200.00"
        assert summary.item_count == 2
        assert isinstance(summary.created_at, datetime)


class TestQueryObjects:
    """Test query objects."""

    def test_get_order_query(self):
        """Test GetOrderQuery."""
        query = GetOrderQuery(order_id="order-123")
        assert query.order_id == "order-123"

    def test_get_orders_by_customer_query(self):
        """Test GetOrdersByCustomerQuery."""
        query = GetOrdersByCustomerQuery(
            customer_id="customer-123",
            limit=20,
            offset=10,
            status="pending"
        )
        assert query.customer_id == "customer-123"
        assert query.limit == 20
        assert query.offset == 10
        assert query.status == "pending"

    def test_get_orders_by_customer_query_defaults(self):
        """Test GetOrdersByCustomerQuery with defaults."""
        query = GetOrdersByCustomerQuery(customer_id="customer-123")
        assert query.customer_id == "customer-123"
        assert query.limit == 50
        assert query.offset == 0
        assert query.status is None

    def test_get_orders_by_status_query(self):
        """Test GetOrdersByStatusQuery."""
        query = GetOrdersByStatusQuery(
            status="pending",
            limit=15,
            offset=5
        )
        assert query.status == "pending"
        assert query.limit == 15
        assert query.offset == 5

    def test_get_orders_by_status_query_defaults(self):
        """Test GetOrdersByStatusQuery with defaults."""
        query = GetOrdersByStatusQuery(status="pending")
        assert query.status == "pending"
        assert query.limit == 50
        assert query.offset == 0

    def test_get_orders_by_date_range_query(self):
        """Test GetOrdersByDateRangeQuery."""
        start_date = datetime.now(UTC)
        end_date = datetime.now(UTC)
        query = GetOrdersByDateRangeQuery(
            start_date=start_date,
            end_date=end_date,
            limit=25,
            offset=5
        )
        assert query.start_date == start_date
        assert query.end_date == end_date
        assert query.limit == 25
        assert query.offset == 5

    def test_get_orders_by_date_range_query_defaults(self):
        """Test GetOrdersByDateRangeQuery with defaults."""
        start_date = datetime.now(UTC)
        end_date = datetime.now(UTC)
        query = GetOrdersByDateRangeQuery(
            start_date=start_date,
            end_date=end_date
        )
        assert query.start_date == start_date
        assert query.end_date == end_date
        assert query.limit == 50
        assert query.offset == 0

    def test_get_order_summary_query(self):
        """Test GetOrderSummaryQuery."""
        query = GetOrderSummaryQuery(order_id="order-123")
        assert query.order_id == "order-123"

    def test_get_customer_order_history_query(self):
        """Test GetCustomerOrderHistoryQuery."""
        query = GetCustomerOrderHistoryQuery(
            customer_id="customer-123",
            limit=30,
            offset=10
        )
        assert query.customer_id == "customer-123"
        assert query.limit == 30
        assert query.offset == 10

    def test_get_customer_order_history_query_defaults(self):
        """Test GetCustomerOrderHistoryQuery with defaults."""
        query = GetCustomerOrderHistoryQuery(customer_id="customer-123")
        assert query.customer_id == "customer-123"
        assert query.limit == 50
        assert query.offset == 0


class TestInMemoryOrderQueryHandler:
    """Test InMemoryOrderQueryHandler."""

    @pytest.fixture
    def handler(self):
        """Create InMemoryOrderQueryHandler."""
        return InMemoryOrderQueryHandler()

    @pytest.fixture
    def sample_order(self):
        """Create sample order read model."""
        return OrderReadModel(
            id="order-123",
            customer_id="customer-123",
            customer_name="John Doe",
            status="pending",
            total="200.00",
            shipping_address="ул. Ленина, 1, Москва",
            billing_address="ул. Ленина, 1, Москва",
            notes="Test order",
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
            items=[]
        )

    @pytest.fixture
    def sample_order_summary(self):
        """Create sample order summary read model."""
        return OrderSummaryReadModel(
            id="order-123",
            customer_id="customer-123",
            status="pending",
            total="200.00",
            item_count=2,
            created_at=datetime.now(UTC)
        )

    @pytest.mark.asyncio
    async def test_get_order_found(self, handler, sample_order):
        """Test getting an order that exists."""
        # Arrange
        handler.add_order(sample_order)

        # Act
        result = await handler.get_order(GetOrderQuery(order_id="order-123"))

        # Assert
        assert result is not None
        assert result.id == "order-123"
        assert result.customer_id == "customer-123"

    @pytest.mark.asyncio
    async def test_get_order_not_found(self, handler):
        """Test getting an order that doesn't exist."""
        # Act
        result = await handler.get_order(GetOrderQuery(order_id="order-999"))

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_get_orders_by_customer(self, handler, sample_order):
        """Test getting orders by customer."""
        # Arrange
        handler.add_order(sample_order)

        # Act
        result = await handler.get_orders_by_customer(
            GetOrdersByCustomerQuery(customer_id="customer-123")
        )

        # Assert
        assert len(result) == 1
        assert result[0].id == "order-123"
        assert result[0].customer_id == "customer-123"

    @pytest.mark.asyncio
    async def test_get_orders_by_customer_with_status_filter(self, handler, sample_order):
        """Test getting orders by customer with status filter."""
        # Arrange
        handler.add_order(sample_order)

        # Act
        result = await handler.get_orders_by_customer(
            GetOrdersByCustomerQuery(
                customer_id="customer-123",
                status="pending"
            )
        )

        # Assert
        assert len(result) == 1
        assert result[0].status == "pending"

    @pytest.mark.asyncio
    async def test_get_orders_by_customer_with_status_filter_no_match(self, handler, sample_order):
        """Test getting orders by customer with status filter that doesn't match."""
        # Arrange
        handler.add_order(sample_order)

        # Act
        result = await handler.get_orders_by_customer(
            GetOrdersByCustomerQuery(
                customer_id="customer-123",
                status="completed"
            )
        )

        # Assert
        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_get_orders_by_customer_empty(self, handler):
        """Test getting orders by customer when none exist."""
        # Act
        result = await handler.get_orders_by_customer(
            GetOrdersByCustomerQuery(customer_id="customer-999")
        )

        # Assert
        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_get_orders_by_status(self, handler, sample_order):
        """Test getting orders by status."""
        # Arrange
        handler.add_order(sample_order)

        # Act
        result = await handler.get_orders_by_status(
            GetOrdersByStatusQuery(status="pending")
        )

        # Assert
        assert len(result) == 1
        assert result[0].status == "pending"

    @pytest.mark.asyncio
    async def test_get_orders_by_status_empty(self, handler):
        """Test getting orders by status when none exist."""
        # Act
        result = await handler.get_orders_by_status(
            GetOrdersByStatusQuery(status="completed")
        )

        # Assert
        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_get_orders_by_date_range(self, handler, sample_order):
        """Test getting orders by date range."""
        # Arrange
        now = datetime.now(UTC)
        # Update sample_order with the same datetime
        sample_order.created_at = now
        handler.add_order(sample_order)
        start_date = now
        end_date = now

        # Act
        result = await handler.get_orders_by_date_range(
            GetOrdersByDateRangeQuery(
                start_date=start_date,
                end_date=end_date
            )
        )

        # Assert
        assert len(result) == 1
        assert result[0].id == "order-123"

    @pytest.mark.asyncio
    async def test_get_orders_by_date_range_empty(self, handler):
        """Test getting orders by date range when none exist."""
        # Arrange
        start_date = datetime(2020, 1, 1, tzinfo=UTC)
        end_date = datetime(2020, 1, 31, tzinfo=UTC)

        # Act
        result = await handler.get_orders_by_date_range(
            GetOrdersByDateRangeQuery(
                start_date=start_date,
                end_date=end_date
            )
        )

        # Assert
        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_get_order_summary_found(self, handler, sample_order_summary):
        """Test getting an order summary that exists."""
        # Arrange
        handler.add_order_summary(sample_order_summary)

        # Act
        result = await handler.get_order_summary(
            GetOrderSummaryQuery(order_id="order-123")
        )

        # Assert
        assert result is not None
        assert result.id == "order-123"
        assert result.customer_id == "customer-123"

    @pytest.mark.asyncio
    async def test_get_order_summary_not_found(self, handler):
        """Test getting an order summary that doesn't exist."""
        # Act
        result = await handler.get_order_summary(
            GetOrderSummaryQuery(order_id="order-999")
        )

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_get_customer_order_history(self, handler, sample_order_summary):
        """Test getting customer order history."""
        # Arrange
        handler.add_order_summary(sample_order_summary)

        # Act
        result = await handler.get_customer_order_history(
            GetCustomerOrderHistoryQuery(customer_id="customer-123")
        )

        # Assert
        assert len(result) == 1
        assert result[0].id == "order-123"
        assert result[0].customer_id == "customer-123"

    @pytest.mark.asyncio
    async def test_get_customer_order_history_empty(self, handler):
        """Test getting customer order history when none exist."""
        # Act
        result = await handler.get_customer_order_history(
            GetCustomerOrderHistoryQuery(customer_id="customer-999")
        )

        # Assert
        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_get_orders_by_customer_with_limit_and_offset(self, handler):
        """Test getting orders by customer with limit and offset."""
        # Arrange
        for i in range(10):
            order = OrderReadModel(
                id=f"order-{i}",
                customer_id="customer-123",
                status="pending",
                total="200.00",
                shipping_address="ул. Ленина, 1, Москва",
                billing_address="ул. Ленина, 1, Москва",
                created_at=datetime(2024, 1, 1 + i, tzinfo=UTC),  # Different dates for consistent ordering
                updated_at=datetime(2024, 1, 1 + i, tzinfo=UTC)
            )
            handler.add_order(order)

        # Act
        result = await handler.get_orders_by_customer(
            GetOrdersByCustomerQuery(
                customer_id="customer-123",
                limit=3,
                offset=2
            )
        )

        # Assert
        assert len(result) == 3
        # Since sorted by created_at desc (newest first), order-9, order-8, order-7, order-6, order-5, order-4, order-3, order-2, order-1, order-0
        # With offset=2, limit=3: order-7, order-6, order-5
        assert result[0].id == "order-7"
        assert result[1].id == "order-6"
        assert result[2].id == "order-5"

    @pytest.mark.asyncio
    async def test_get_orders_by_status_with_limit_and_offset(self, handler):
        """Test getting orders by status with limit and offset."""
        # Arrange
        for i in range(10):
            order = OrderReadModel(
                id=f"order-{i}",
                customer_id=f"customer-{i}",
                status="pending",
                total="200.00",
                shipping_address="ул. Ленина, 1, Москва",
                billing_address="ул. Ленина, 1, Москва",
                created_at=datetime(2024, 1, 1 + i, tzinfo=UTC),  # Different dates for consistent ordering
                updated_at=datetime(2024, 1, 1 + i, tzinfo=UTC)
            )
            handler.add_order(order)

        # Act
        result = await handler.get_orders_by_status(
            GetOrdersByStatusQuery(
                status="pending",
                limit=3,
                offset=2
            )
        )

        # Assert
        assert len(result) == 3
        # Since sorted by created_at desc (newest first), order-9, order-8, order-7, order-6, order-5, order-4, order-3, order-2, order-1, order-0
        # With offset=2, limit=3: order-7, order-6, order-5
        assert result[0].id == "order-7"
        assert result[1].id == "order-6"
        assert result[2].id == "order-5"

    @pytest.mark.asyncio
    async def test_get_customer_order_history_with_limit_and_offset(self, handler):
        """Test getting customer order history with limit and offset."""
        # Arrange
        for i in range(10):
            summary = OrderSummaryReadModel(
                id=f"order-{i}",
                customer_id="customer-123",
                status="pending",
                total="200.00",
                item_count=2,
                created_at=datetime(2024, 1, 1 + i, tzinfo=UTC)  # Different dates
            )
            handler.add_order_summary(summary)

        # Act
        result = await handler.get_customer_order_history(
            GetCustomerOrderHistoryQuery(
                customer_id="customer-123",
                limit=3,
                offset=2
            )
        )

        # Assert
        assert len(result) == 3
        # Since sorted by created_at desc (newest first), order-9, order-8, order-7, order-6, order-5, order-4, order-3, order-2, order-1, order-0
        # With offset=2, limit=3: order-7, order-6, order-5
        assert result[0].id == "order-7"
        assert result[1].id == "order-6"
        assert result[2].id == "order-5"

    def test_update_order(self, handler, sample_order):
        """Test updating an order."""
        # Arrange
        handler.add_order(sample_order)
        updated_order = OrderReadModel(
            id="order-123",
            customer_id="customer-123",
            customer_name="John Doe",
            status="completed",  # Changed status
            total="200.00",
            shipping_address="ул. Ленина, 1, Москва",
            billing_address="ул. Ленина, 1, Москва",
            notes="Updated order",
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
            items=[]
        )

        # Act
        handler.update_order(updated_order)

        # Assert
        # Verify the order was updated by querying it
        import asyncio
        result = asyncio.run(handler.get_order(GetOrderQuery(order_id="order-123")))
        assert result is not None
        assert result.status == "completed"
        assert result.notes == "Updated order" 