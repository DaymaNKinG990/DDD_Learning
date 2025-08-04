"""Tests for error handling in catalog application services."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from decimal import Decimal

from src.catalog.application.services import CatalogService
from src.catalog.domain.entities import Product, Category
from src.catalog.domain.value_objects import ProductId, CategoryId, Price, ProductName
from src.catalog.domain.exceptions import (
    ProductNotFoundError,
    CategoryNotFoundError,
    ProductAlreadyExistsError,
    InvalidProductDataError,
    InvalidCategoryDataError,
)
from src.shared.domain.exceptions import EntityNotFoundError, InvalidOperationError


class TestCatalogServiceErrorHandling:
    """Test error handling scenarios in catalog service."""

    @pytest.fixture
    def mock_product_repository(self):
        """Create a mock product repository."""
        return AsyncMock()

    @pytest.fixture
    def mock_category_repository(self):
        """Create a mock category repository."""
        return AsyncMock()

    @pytest.fixture
    def catalog_service(self, mock_product_repository, mock_category_repository):
        """Create catalog service instance."""
        return CatalogService(mock_product_repository, mock_category_repository)

    @pytest.fixture
    def sample_product(self):
        """Create a sample product for testing."""
        return Product(
            id=ProductId("test-product-id"),
            name=ProductName("Test Product"),
            description="Test product description",
            price=Price(Decimal("99.99")),
            category_id=CategoryId("test-category-id"),
            stock_quantity=10
        )

    @pytest.fixture
    def sample_category(self):
        """Create a sample category for testing."""
        return Category(
            id=CategoryId("test-category-id"),
            name="Test Category",
            description="Test category description"
        )

    async def test_create_product_invalid_data(self, catalog_service, mock_product_repository):
        """Test creating product with invalid data."""
        # Arrange
        mock_product_repository.save.side_effect = ValueError("Invalid product data")
        
        # Act & Assert
        with pytest.raises(ValueError, match="Invalid product data"):
            await catalog_service.create_product(
                name="",
                description="",
                price=Decimal("-10.00"),
                category_id="invalid_category",
                stock_quantity=-5
            )

    async def test_create_product_duplicate_name(self, catalog_service, mock_product_repository):
        """Test creating product with duplicate name."""
        # Arrange
        mock_product_repository.save.side_effect = ProductAlreadyExistsError("Product with this name already exists")
        
        # Act & Assert
        with pytest.raises(ProductAlreadyExistsError, match="Product with this name already exists"):
            await catalog_service.create_product(
                name="Existing Product",
                description="Test description",
                price=Decimal("99.99"),
                category_id="test-category-id",
                stock_quantity=10
            )

    async def test_create_product_category_not_found(self, catalog_service, mock_category_repository):
        """Test creating product with non-existent category."""
        # Arrange
        mock_category_repository.get_by_id.return_value = None
        
        # Act & Assert
        with pytest.raises(CategoryNotFoundError, match="Category not found"):
            await catalog_service.create_product(
                name="Test Product",
                description="Test description",
                price=Decimal("99.99"),
                category_id="non_existent_category",
                stock_quantity=10
            )

    async def test_get_product_not_found(self, catalog_service, mock_product_repository):
        """Test getting non-existent product."""
        # Arrange
        mock_product_repository.get_by_id.return_value = None
        
        # Act & Assert
        with pytest.raises(ProductNotFoundError, match="Product not found"):
            await catalog_service.get_product("non_existent_product")

    async def test_get_product_invalid_id(self, catalog_service, mock_product_repository):
        """Test getting product with invalid ID."""
        # Arrange
        mock_product_repository.get_by_id.side_effect = ValueError("Invalid product ID format")
        
        # Act & Assert
        with pytest.raises(ValueError, match="Invalid product ID format"):
            await catalog_service.get_product("invalid_id_format")

    async def test_update_product_not_found(self, catalog_service, mock_product_repository):
        """Test updating non-existent product."""
        # Arrange
        mock_product_repository.get_by_id.return_value = None
        
        # Act & Assert
        with pytest.raises(ProductNotFoundError, match="Product not found"):
            await catalog_service.update_product(
                "non_existent_product",
                name="Updated Product",
                description="Updated description",
                price=Decimal("149.99"),
                stock_quantity=20
            )

    async def test_update_product_invalid_data(self, catalog_service, mock_product_repository, sample_product):
        """Test updating product with invalid data."""
        # Arrange
        mock_product_repository.get_by_id.return_value = sample_product
        mock_product_repository.save.side_effect = ValueError("Invalid product data")
        
        # Act & Assert
        with pytest.raises(ValueError, match="Invalid product data"):
            await catalog_service.update_product(
                "test-product-id",
                name="",
                description="",
                price=Decimal("-10.00"),
                stock_quantity=-5
            )

    async def test_update_product_category_not_found(self, catalog_service, mock_product_repository, mock_category_repository, sample_product):
        """Test updating product with non-existent category."""
        # Arrange
        mock_product_repository.get_by_id.return_value = sample_product
        mock_category_repository.get_by_id.return_value = None
        
        # Act & Assert
        with pytest.raises(CategoryNotFoundError, match="Category not found"):
            await catalog_service.update_product(
                "test-product-id",
                category_id="non_existent_category"
            )

    async def test_delete_product_not_found(self, catalog_service, mock_product_repository):
        """Test deleting non-existent product."""
        # Arrange
        mock_product_repository.get_by_id.return_value = None
        
        # Act & Assert
        with pytest.raises(ProductNotFoundError, match="Product not found"):
            await catalog_service.delete_product("non_existent_product")

    async def test_delete_product_with_active_orders(self, catalog_service, mock_product_repository, sample_product):
        """Test deleting product with active orders."""
        # Arrange
        mock_product_repository.get_by_id.return_value = sample_product
        mock_product_repository.delete.side_effect = InvalidOperationError("Cannot delete product with active orders")
        
        # Act & Assert
        with pytest.raises(InvalidOperationError, match="Cannot delete product with active orders"):
            await catalog_service.delete_product("test-product-id")

    async def test_get_products_by_category_not_found(self, catalog_service, mock_category_repository):
        """Test getting products for non-existent category."""
        # Arrange
        mock_category_repository.get_by_id.return_value = None
        
        # Act & Assert
        with pytest.raises(CategoryNotFoundError, match="Category not found"):
            await catalog_service.get_products_by_category("non_existent_category")

    async def test_get_products_by_category_empty_result(self, catalog_service, mock_category_repository, sample_category):
        """Test getting products for category with no products."""
        # Arrange
        mock_category_repository.get_by_id.return_value = sample_category
        mock_product_repository.get_by_category.return_value = []
        
        # Act
        result = await catalog_service.get_products_by_category("test-category-id")
        
        # Assert
        assert result == []

    async def test_search_products_invalid_query(self, catalog_service, mock_product_repository):
        """Test searching products with invalid query."""
        # Arrange
        mock_product_repository.search.side_effect = ValueError("Search query is too short")
        
        # Act & Assert
        with pytest.raises(ValueError, match="Search query is too short"):
            await catalog_service.search_products("a")

    async def test_search_products_empty_result(self, catalog_service, mock_product_repository):
        """Test searching products with no results."""
        # Arrange
        mock_product_repository.search.return_value = []
        
        # Act
        result = await catalog_service.search_products("nonexistent")
        
        # Assert
        assert result == []

    async def test_get_products_paginated_invalid_pagination(self, catalog_service, mock_product_repository):
        """Test getting paginated products with invalid pagination."""
        # Arrange
        mock_product_repository.get_paginated.side_effect = ValueError("Invalid pagination parameters")
        
        # Act & Assert
        with pytest.raises(ValueError, match="Invalid pagination parameters"):
            await catalog_service.get_products_paginated(page=-1, size=0)

    async def test_get_products_paginated_empty_result(self, catalog_service, mock_product_repository):
        """Test getting paginated products with no results."""
        # Arrange
        mock_product_repository.get_paginated.return_value = []
        
        # Act
        result = await catalog_service.get_products_paginated(page=1, size=10)
        
        # Assert
        assert result == []

    async def test_create_category_invalid_data(self, catalog_service, mock_category_repository):
        """Test creating category with invalid data."""
        # Arrange
        mock_category_repository.save.side_effect = ValueError("Invalid category data")
        
        # Act & Assert
        with pytest.raises(ValueError, match="Invalid category data"):
            await catalog_service.create_category(
                name="",
                description=""
            )

    async def test_create_category_duplicate_name(self, catalog_service, mock_category_repository):
        """Test creating category with duplicate name."""
        # Arrange
        mock_category_repository.save.side_effect = InvalidOperationError("Category with this name already exists")
        
        # Act & Assert
        with pytest.raises(InvalidOperationError, match="Category with this name already exists"):
            await catalog_service.create_category(
                name="Existing Category",
                description="Test description"
            )

    async def test_get_category_not_found(self, catalog_service, mock_category_repository):
        """Test getting non-existent category."""
        # Arrange
        mock_category_repository.get_by_id.return_value = None
        
        # Act & Assert
        with pytest.raises(CategoryNotFoundError, match="Category not found"):
            await catalog_service.get_category("non_existent_category")

    async def test_get_category_invalid_id(self, catalog_service, mock_category_repository):
        """Test getting category with invalid ID."""
        # Arrange
        mock_category_repository.get_by_id.side_effect = ValueError("Invalid category ID format")
        
        # Act & Assert
        with pytest.raises(ValueError, match="Invalid category ID format"):
            await catalog_service.get_category("invalid_id_format")

    async def test_update_category_not_found(self, catalog_service, mock_category_repository):
        """Test updating non-existent category."""
        # Arrange
        mock_category_repository.get_by_id.return_value = None
        
        # Act & Assert
        with pytest.raises(CategoryNotFoundError, match="Category not found"):
            await catalog_service.update_category(
                "non_existent_category",
                name="Updated Category",
                description="Updated description"
            )

    async def test_update_category_invalid_data(self, catalog_service, mock_category_repository, sample_category):
        """Test updating category with invalid data."""
        # Arrange
        mock_category_repository.get_by_id.return_value = sample_category
        mock_category_repository.save.side_effect = ValueError("Invalid category data")
        
        # Act & Assert
        with pytest.raises(ValueError, match="Invalid category data"):
            await catalog_service.update_category(
                "test-category-id",
                name="",
                description=""
            )

    async def test_delete_category_not_found(self, catalog_service, mock_category_repository):
        """Test deleting non-existent category."""
        # Arrange
        mock_category_repository.get_by_id.return_value = None
        
        # Act & Assert
        with pytest.raises(CategoryNotFoundError, match="Category not found"):
            await catalog_service.delete_category("non_existent_category")

    async def test_delete_category_with_products(self, catalog_service, mock_category_repository, sample_category):
        """Test deleting category with products."""
        # Arrange
        mock_category_repository.get_by_id.return_value = sample_category
        mock_category_repository.delete.side_effect = InvalidOperationError("Cannot delete category with products")
        
        # Act & Assert
        with pytest.raises(InvalidOperationError, match="Cannot delete category with products"):
            await catalog_service.delete_category("test-category-id")

    async def test_get_all_categories_empty_result(self, catalog_service, mock_category_repository):
        """Test getting all categories when none exist."""
        # Arrange
        mock_category_repository.get_all.return_value = []
        
        # Act
        result = await catalog_service.get_all_categories()
        
        # Assert
        assert result == []

    async def test_get_products_by_price_range_invalid_range(self, catalog_service, mock_product_repository):
        """Test getting products by price range with invalid range."""
        # Arrange
        mock_product_repository.get_by_price_range.side_effect = ValueError("Invalid price range")
        
        # Act & Assert
        with pytest.raises(ValueError, match="Invalid price range"):
            await catalog_service.get_products_by_price_range(
                min_price=Decimal("100.00"),
                max_price=Decimal("50.00")
            )

    async def test_get_products_by_price_range_empty_result(self, catalog_service, mock_product_repository):
        """Test getting products by price range with no results."""
        # Arrange
        mock_product_repository.get_by_price_range.return_value = []
        
        # Act
        result = await catalog_service.get_products_by_price_range(
            min_price=Decimal("1000.00"),
            max_price=Decimal("2000.00")
        )
        
        # Assert
        assert result == []

    async def test_update_product_stock_invalid_quantity(self, catalog_service, mock_product_repository, sample_product):
        """Test updating product stock with invalid quantity."""
        # Arrange
        mock_product_repository.get_by_id.return_value = sample_product
        
        # Act & Assert
        with pytest.raises(ValueError, match="Stock quantity cannot be negative"):
            await catalog_service.update_product_stock("test-product-id", -5)

    async def test_update_product_stock_not_found(self, catalog_service, mock_product_repository):
        """Test updating stock for non-existent product."""
        # Arrange
        mock_product_repository.get_by_id.return_value = None
        
        # Act & Assert
        with pytest.raises(ProductNotFoundError, match="Product not found"):
            await catalog_service.update_product_stock("non_existent_product", 10) 