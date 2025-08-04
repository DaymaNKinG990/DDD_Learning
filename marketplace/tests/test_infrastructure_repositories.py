"""Tests for infrastructure repositories."""

import pytest
from unittest.mock import Mock, AsyncMock
from decimal import Decimal

# Mock redis to avoid import errors
import sys
from unittest.mock import MagicMock
sys.modules['redis'] = MagicMock()
sys.modules['redis.asyncio'] = MagicMock()

from src.shared.infrastructure.repositories import InMemoryRepository
from src.catalog.domain.entities import Product, Category
from src.catalog.domain.value_objects import (
    ProductId, CategoryId, Price, ProductName, ProductDescription
)
from src.catalog.infrastructure.repositories import (
    InMemoryProductRepository, InMemoryCategoryRepository
)
from src.orders.domain.entities import Order
from src.orders.domain.value_objects import OrderId, OrderStatus, OrderTotal
from src.orders.infrastructure.repositories import InMemoryOrderRepository
from src.users.domain.entities import User
from src.users.domain.value_objects import UserId, Email, Username
from src.users.infrastructure.repositories import InMemoryUserRepository


class TestInMemoryRepository:
    """Test base InMemoryRepository functionality."""

    @pytest.fixture
    def repository(self):
        """Create base repository for testing."""
        return InMemoryRepository[object]()

    @pytest.fixture
    def sample_entity(self):
        """Create sample entity for testing."""
        class TestEntity:
            def __init__(self, id: str, name: str):
                self.id = id
                self.name = name

        return TestEntity("test-123", "Test Entity")

    @pytest.mark.asyncio
    async def test_save_and_get_by_id(self, repository, sample_entity):
        """Test saving and retrieving entity by ID."""
        # Act
        await repository.save(sample_entity)
        result = await repository.get_by_id("test-123")

        # Assert
        assert result == sample_entity
        assert result.id == "test-123"
        assert result.name == "Test Entity"

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, repository):
        """Test getting entity by ID when not found."""
        # Act
        result = await repository.get_by_id("non-existent")

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_get_all(self, repository, sample_entity):
        """Test getting all entities."""
        # Arrange
        entity2 = type(sample_entity)("test-456", "Test Entity 2")
        await repository.save(sample_entity)
        await repository.save(entity2)

        # Act
        result = await repository.list_all()

        # Assert
        assert len(result) == 2
        assert sample_entity in result
        assert entity2 in result

    @pytest.mark.asyncio
    async def test_delete(self, repository, sample_entity):
        """Test deleting entity."""
        # Arrange
        await repository.save(sample_entity)

        # Act
        await repository.delete("test-123")
        result = await repository.get_by_id("test-123")

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_update(self, repository, sample_entity):
        """Test updating entity."""
        # Arrange
        await repository.save(sample_entity)
        sample_entity.name = "Updated Entity"

        # Act
        await repository.save(sample_entity)
        result = await repository.get_by_id("test-123")

        # Assert
        assert result.name == "Updated Entity"


class TestInMemoryProductRepository:
    """Test InMemoryProductRepository."""

    @pytest.fixture
    def repository(self):
        """Create product repository for testing."""
        return InMemoryProductRepository()

    @pytest.fixture
    def sample_product(self):
        """Create sample product for testing."""
        return Product(
            id=ProductId(value="prod-123"),
            name=ProductName(value="Test Product"),
            description=ProductDescription(value="Test description"),
            price=Price(amount=Decimal("100.00"), currency="RUB"),
            category_id=CategoryId(value="cat-123"),
            stock_quantity=10,
            is_active=True
        )

    @pytest.mark.asyncio
    async def test_save_and_get_by_id(self, repository, sample_product):
        """Test saving and retrieving product by ID."""
        # Act
        await repository.save(sample_product)
        result = await repository.get_by_id(ProductId(value="prod-123"))

        # Assert
        assert result == sample_product
        assert result.id.value == "prod-123"

    @pytest.mark.asyncio
    async def test_get_by_seller_id(self, repository, sample_product):
        """Test getting products by seller ID."""
        # Arrange
        product2 = Product(
            id=ProductId(value="prod-456"),
            name=ProductName(value="Test Product 2"),
            description=ProductDescription(value="Test description 2"),
            price=Price(amount=Decimal("200.00"), currency="RUB"),
            category_id=CategoryId(value="cat-123"),
            stock_quantity=5,
            is_active=True
        )
        await repository.save(sample_product)
        await repository.save(product2)

        # Act
        result = await repository.get_by_seller_id("seller-123")

        # Assert
        assert len(result) == 2
        assert sample_product in result
        assert product2 in result

    @pytest.mark.asyncio
    async def test_get_by_category_id(self, repository, sample_product):
        """Test getting products by category ID."""
        # Arrange
        await repository.save(sample_product)

        # Act
        result = await repository.get_by_category(CategoryId(value="cat-123"))

        # Assert
        assert len(result) == 1
        assert sample_product in result

    @pytest.mark.asyncio
    async def test_search_products(self, repository, sample_product):
        """Test searching products."""
        # Arrange
        await repository.save(sample_product)

        # Act
        result = await repository.search_products("Test")

        # Assert
        assert len(result) == 1
        assert sample_product in result

    @pytest.mark.asyncio
    async def test_get_active_products(self, repository, sample_product):
        """Test getting active products."""
        # Arrange
        inactive_product = Product(
            id=ProductId(value="prod-456"),
            name=ProductName(value="Inactive Product"),
            description=ProductDescription(value="Inactive description"),
            price=Price(amount=Decimal("200.00"), currency="RUB"),
            category_id=CategoryId(value="cat-123"),
            stock_quantity=5,
            is_active=False
        )
        await repository.save(sample_product)
        await repository.save(inactive_product)

        # Act
        result = await repository.get_active_products()

        # Assert
        assert len(result) == 1
        assert sample_product in result
        assert inactive_product not in result


class TestInMemoryCategoryRepository:
    """Test InMemoryCategoryRepository."""

    @pytest.fixture
    def repository(self):
        """Create category repository for testing."""
        return InMemoryCategoryRepository()

    @pytest.fixture
    def sample_category(self):
        """Create sample category for testing."""
        return Category(
            id=CategoryId(value="cat-123"),
            name="Electronics",
            description="Electronic devices",
            parent_id=None,
            is_active=True
        )

    @pytest.mark.asyncio
    async def test_save_and_get_by_id(self, repository, sample_category):
        """Test saving and retrieving category by ID."""
        # Act
        await repository.save(sample_category)
        result = await repository.get_by_id(CategoryId(value="cat-123"))

        # Assert
        assert result == sample_category
        assert result.id.value == "cat-123"

    @pytest.mark.asyncio
    async def test_get_by_name(self, repository, sample_category):
        """Test getting category by name."""
        # Arrange
        await repository.save(sample_category)

        # Act
        result = await repository.get_by_name("Electronics")

        # Assert
        assert result == sample_category

    @pytest.mark.asyncio
    async def test_get_children(self, repository, sample_category):
        """Test getting child categories."""
        # Arrange
        child_category = Category(
            id=CategoryId(value="cat-456"),
            name="Smartphones",
            description="Smartphone devices",
            parent_id=CategoryId(value="cat-123"),
            is_active=True
        )
        await repository.save(sample_category)
        await repository.save(child_category)

        # Act
        result = await repository.get_children(CategoryId(value="cat-123"))

        # Assert
        assert len(result) == 1
        assert child_category in result

    @pytest.mark.asyncio
    async def test_get_active_categories(self, repository, sample_category):
        """Test getting active categories."""
        # Arrange
        inactive_category = Category(
            id=CategoryId(value="cat-456"),
            name="Inactive Category",
            description="Inactive category description",
            parent_id=None,
            is_active=False
        )
        await repository.save(sample_category)
        await repository.save(inactive_category)

        # Act
        result = await repository.get_active_categories()

        # Assert
        assert len(result) == 1
        assert sample_category in result
        assert inactive_category not in result


class TestInMemoryOrderRepository:
    """Test InMemoryOrderRepository."""

    @pytest.fixture
    def repository(self):
        """Create order repository for testing."""
        return InMemoryOrderRepository()

    @pytest.fixture
    def sample_order(self):
        """Create sample order for testing."""
        return Order(
            id=OrderId(value="order-123"),
            customer_id="customer-123",
            items=[],
            status=OrderStatus.PENDING,
            total=OrderTotal.calculate(Decimal("200.00")),
            shipping_address="ул. Ленина, 1, Москва",
            billing_address="ул. Ленина, 1, Москва"
        )

    @pytest.mark.asyncio
    async def test_save_and_get_by_id(self, repository, sample_order):
        """Test saving and retrieving order by ID."""
        # Act
        await repository.save(sample_order)
        result = await repository.get_by_id(OrderId(value="order-123"))

        # Assert
        assert result == sample_order
        assert result.id.value == "order-123"

    @pytest.mark.asyncio
    async def test_get_by_customer_id(self, repository, sample_order):
        """Test getting orders by customer ID."""
        # Arrange
        order2 = Order(
            id=OrderId(value="order-456"),
            customer_id="customer-123",
            items=[],
            status=OrderStatus.CONFIRMED,
            total=OrderTotal.calculate(Decimal("300.00")),
            shipping_address="ул. Пушкина, 10, Москва",
            billing_address="ул. Пушкина, 10, Москва"
        )
        await repository.save(sample_order)
        await repository.save(order2)

        # Act
        result = await repository.get_by_customer_id("customer-123")

        # Assert
        assert len(result) == 2
        assert sample_order in result
        assert order2 in result

    @pytest.mark.asyncio
    async def test_get_by_status(self, repository, sample_order):
        """Test getting orders by status."""
        # Arrange
        await repository.save(sample_order)

        # Act
        result = await repository.get_orders_by_status("pending")

        # Assert
        assert len(result) == 1
        assert sample_order in result

    @pytest.mark.asyncio
    async def test_get_orders_by_date_range(self, repository, sample_order):
        """Test getting orders by date range."""
        # Arrange
        await repository.save(sample_order)

        # Act
        result = await repository.get_orders_by_date_range(
            start_date=sample_order.created_at,
            end_date=sample_order.created_at
        )

        # Assert
        assert len(result) == 1
        assert sample_order in result


class TestInMemoryUserRepository:
    """Test InMemoryUserRepository."""

    @pytest.fixture
    def repository(self):
        """Create user repository for testing."""
        return InMemoryUserRepository()

    @pytest.fixture
    def sample_user(self):
        """Create sample user for testing."""
        return User(
            id=UserId(value="user-123"),
            email=Email(value="test@example.com"),
            username=Username(value="testuser"),
            first_name="Test",
            last_name="User",
            is_active=True
        )

    @pytest.mark.asyncio
    async def test_save_and_get_by_id(self, repository, sample_user):
        """Test saving and retrieving user by ID."""
        # Act
        await repository.save(sample_user)
        result = await repository.get_by_id(UserId(value="user-123"))

        # Assert
        assert result == sample_user
        assert result.id.value == "user-123"

    @pytest.mark.asyncio
    async def test_get_by_email(self, repository, sample_user):
        """Test getting user by email."""
        # Arrange
        await repository.save(sample_user)

        # Act
        result = await repository.get_by_email(Email(value="test@example.com"))

        # Assert
        assert result == sample_user

    @pytest.mark.asyncio
    async def test_get_by_username(self, repository, sample_user):
        """Test getting user by username."""
        # Arrange
        await repository.save(sample_user)

        # Act
        result = await repository.get_by_username(Username(value="testuser"))

        # Assert
        assert result == sample_user

    @pytest.mark.asyncio
    async def test_get_active_users(self, repository, sample_user):
        """Test getting active users."""
        # Arrange
        inactive_user = User(
            id=UserId(value="user-456"),
            email=Email(value="inactive@example.com"),
            username=Username(value="inactiveuser"),
            first_name="Inactive",
            last_name="User",
            is_active=False
        )
        await repository.save(sample_user)
        await repository.save(inactive_user)

        # Act
        result = await repository.get_active_users()

        # Assert
        assert len(result) == 1
        assert sample_user in result
        assert inactive_user not in result 