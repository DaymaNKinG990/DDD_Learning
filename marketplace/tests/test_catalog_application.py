"""Tests for catalog application services."""

import pytest
from unittest.mock import Mock, AsyncMock
from decimal import Decimal

from src.catalog.application.services import CatalogService
from src.catalog.domain.entities import Product, Category
from src.catalog.domain.value_objects import (
    ProductId, CategoryId, Price, ProductName, ProductDescription
)
from src.catalog.domain.repositories import ProductRepository, CategoryRepository
from src.shared.domain.exceptions import EntityNotFoundError


class TestCatalogService:
    """Test CatalogService application service."""

    @pytest.fixture
    def mock_product_repository(self):
        """Create mock product repository."""
        return Mock(spec=ProductRepository)

    @pytest.fixture
    def mock_category_repository(self):
        """Create mock category repository."""
        return Mock(spec=CategoryRepository)

    @pytest.fixture
    def mock_brand_repository(self):
        """Create mock brand repository."""
        return Mock()

    @pytest.fixture
    def catalog_service(self, mock_product_repository, mock_category_repository, mock_brand_repository):
        """Create catalog service with mocked dependencies."""
        return CatalogService(
            product_repository=mock_product_repository,
            category_repository=mock_category_repository,
            brand_repository=mock_brand_repository
        )

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
    async def test_create_product(self, catalog_service, mock_product_repository, sample_product):
        """Test creating a product."""
        # Arrange
        mock_product_repository.save = AsyncMock()
        mock_product_repository.save.return_value = sample_product

        # Act
        result = await catalog_service.create_product(
            name="Test Product",
            description="Test description",
            price=Price(amount=Decimal("100.00"), currency="RUB"),
            category_id=CategoryId(value="cat-123"),
            sku="test-sku"
        )

        # Assert
        assert result.name.value == "Test Product"
        assert result.description.value == "Test description"
        assert result.price.amount == Decimal("100.00")
        mock_product_repository.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_product_by_id(self, catalog_service, mock_product_repository, sample_product):
        """Test getting product by ID."""
        # Arrange
        mock_product_repository.get_by_id = AsyncMock()
        mock_product_repository.get_by_id.return_value = sample_product

        # Act
        result = await catalog_service.get_product("prod-123")

        # Assert
        assert result == sample_product
        mock_product_repository.get_by_id.assert_called_once_with(ProductId(value="prod-123"))

    @pytest.mark.asyncio
    async def test_get_product_by_id_not_found(self, catalog_service, mock_product_repository):
        """Test getting product by ID when not found."""
        # Arrange
        mock_product_repository.get_by_id = AsyncMock()
        mock_product_repository.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(EntityNotFoundError, match="Product with ID prod-123 not found"):
            await catalog_service.get_product("prod-123")

    @pytest.mark.asyncio
    async def test_update_product_price(self, catalog_service, mock_product_repository, sample_product):
        """Test updating product price."""
        # Arrange
        mock_product_repository.get_by_id = AsyncMock()
        mock_product_repository.get_by_id.return_value = sample_product
        mock_product_repository.save = AsyncMock()
        mock_product_repository.save.return_value = sample_product

        # Act
        result = await catalog_service.update_product_price(
            product_id="prod-123",
            new_price=Price(amount=Decimal("150.00"), currency="RUB")
        )

        # Assert
        assert result.price.amount == Decimal("150.00")
        mock_product_repository.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_deactivate_product(self, catalog_service, mock_product_repository, sample_product):
        """Test deactivating a product."""
        # Arrange
        mock_product_repository.get_by_id = AsyncMock()
        mock_product_repository.get_by_id.return_value = sample_product
        mock_product_repository.save = AsyncMock()
        mock_product_repository.save.return_value = sample_product

        # Act
        result = await catalog_service.deactivate_product("prod-123", "Out of stock")

        # Assert
        assert not result.is_active
        mock_product_repository.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_category(self, catalog_service, mock_category_repository, sample_category):
        """Test creating a category."""
        # Arrange
        mock_category_repository.save = AsyncMock()
        mock_category_repository.save.return_value = sample_category

        # Act
        result = await catalog_service.create_category(
            name="Electronics",
            description="Electronic devices",
            parent_id=None
        )

        # Assert
        assert result.name == "Electronics"
        assert result.description == "Electronic devices"
        mock_category_repository.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_category_by_id(self, catalog_service, mock_category_repository, sample_category):
        """Test getting category by ID."""
        # Arrange
        mock_category_repository.get_by_id = AsyncMock()
        mock_category_repository.get_by_id.return_value = sample_category

        # Act
        result = await catalog_service.get_category("cat-123")

        # Assert
        assert result == sample_category
        mock_category_repository.get_by_id.assert_called_once_with(CategoryId(value="cat-123"))

    @pytest.mark.asyncio
    async def test_get_products_by_category(self, catalog_service, mock_product_repository, sample_product):
        """Test getting products by category."""
        # Arrange
        mock_product_repository.get_by_category = AsyncMock()
        mock_product_repository.get_by_category.return_value = [sample_product]

        # Act
        result = await catalog_service.get_products_by_category("cat-123")

        # Assert
        assert len(result) == 1
        assert result[0] == sample_product
        mock_product_repository.get_by_category.assert_called_once_with(CategoryId(value="cat-123")) 