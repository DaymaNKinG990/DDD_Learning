"""Tests for catalog application queries."""

import pytest
from unittest.mock import AsyncMock
from decimal import Decimal

from src.catalog.application.queries import (
    ProductReadModel,
    CategoryReadModel,
    BrandReadModel,
    GetProductQuery,
    GetProductsByCategoryQuery,
    GetProductsByBrandQuery,
    SearchProductsQuery,
    GetCategoryQuery,
    GetCategoriesQuery,
    GetBrandQuery,
    GetBrandsQuery,
    InMemoryProductQueryHandler,
    InMemoryCategoryQueryHandler,
    InMemoryBrandQueryHandler,
)


class TestProductReadModel:
    """Test ProductReadModel."""

    def test_product_read_model_creation(self):
        """Test creating a ProductReadModel."""
        product = ProductReadModel(
            id="prod-123",
            name="Test Product",
            description="Test description",
            price="100.00",
            category_id="cat-123",
            category_name="Electronics",
            brand_id="brand-123",
            brand_name="Test Brand",
            sku="TEST-123",
            is_active=True
        )

        assert product.id == "prod-123"
        assert product.name == "Test Product"
        assert product.description == "Test description"
        assert product.price == "100.00"
        assert product.category_id == "cat-123"
        assert product.category_name == "Electronics"
        assert product.brand_id == "brand-123"
        assert product.brand_name == "Test Brand"
        assert product.sku == "TEST-123"
        assert product.is_active is True

    def test_product_read_model_minimal(self):
        """Test creating a ProductReadModel with minimal fields."""
        product = ProductReadModel(
            id="prod-123",
            name="Test Product",
            description="Test description",
            price="100.00",
            category_id="cat-123",
            sku="TEST-123",
            is_active=True
        )

        assert product.id == "prod-123"
        assert product.category_name is None
        assert product.brand_id is None
        assert product.brand_name is None


class TestCategoryReadModel:
    """Test CategoryReadModel."""

    def test_category_read_model_creation(self):
        """Test creating a CategoryReadModel."""
        category = CategoryReadModel(
            id="cat-123",
            name="Electronics",
            description="Electronic devices",
            parent_id="cat-parent",
            parent_name="Technology",
            product_count=10
        )

        assert category.id == "cat-123"
        assert category.name == "Electronics"
        assert category.description == "Electronic devices"
        assert category.parent_id == "cat-parent"
        assert category.parent_name == "Technology"
        assert category.product_count == 10

    def test_category_read_model_minimal(self):
        """Test creating a CategoryReadModel with minimal fields."""
        category = CategoryReadModel(
            id="cat-123",
            name="Electronics"
        )

        assert category.id == "cat-123"
        assert category.name == "Electronics"
        assert category.description is None
        assert category.parent_id is None
        assert category.parent_name is None
        assert category.product_count == 0


class TestBrandReadModel:
    """Test BrandReadModel."""

    def test_brand_read_model_creation(self):
        """Test creating a BrandReadModel."""
        brand = BrandReadModel(
            id="brand-123",
            name="Test Brand",
            description="Test brand description",
            logo_url="https://example.com/logo.png",
            product_count=5
        )

        assert brand.id == "brand-123"
        assert brand.name == "Test Brand"
        assert brand.description == "Test brand description"
        assert brand.logo_url == "https://example.com/logo.png"
        assert brand.product_count == 5

    def test_brand_read_model_minimal(self):
        """Test creating a BrandReadModel with minimal fields."""
        brand = BrandReadModel(
            id="brand-123",
            name="Test Brand"
        )

        assert brand.id == "brand-123"
        assert brand.name == "Test Brand"
        assert brand.description is None
        assert brand.logo_url is None
        assert brand.product_count == 0


class TestQueryObjects:
    """Test query objects."""

    def test_get_product_query(self):
        """Test GetProductQuery."""
        query = GetProductQuery(product_id="prod-123")
        assert query.product_id == "prod-123"

    def test_get_products_by_category_query(self):
        """Test GetProductsByCategoryQuery."""
        query = GetProductsByCategoryQuery(
            category_id="cat-123",
            limit=20,
            offset=10
        )
        assert query.category_id == "cat-123"
        assert query.limit == 20
        assert query.offset == 10

    def test_get_products_by_category_query_defaults(self):
        """Test GetProductsByCategoryQuery with defaults."""
        query = GetProductsByCategoryQuery(category_id="cat-123")
        assert query.category_id == "cat-123"
        assert query.limit == 50
        assert query.offset == 0

    def test_get_products_by_brand_query(self):
        """Test GetProductsByBrandQuery."""
        query = GetProductsByBrandQuery(
            brand_id="brand-123",
            limit=15,
            offset=5
        )
        assert query.brand_id == "brand-123"
        assert query.limit == 15
        assert query.offset == 5

    def test_search_products_query(self):
        """Test SearchProductsQuery."""
        query = SearchProductsQuery(
            search_term="laptop",
            category_id="cat-123",
            brand_id="brand-123",
            min_price=100.0,
            max_price=1000.0,
            limit=25,
            offset=5
        )
        assert query.search_term == "laptop"
        assert query.category_id == "cat-123"
        assert query.brand_id == "brand-123"
        assert query.min_price == 100.0
        assert query.max_price == 1000.0
        assert query.limit == 25
        assert query.offset == 5

    def test_search_products_query_minimal(self):
        """Test SearchProductsQuery with minimal fields."""
        query = SearchProductsQuery(search_term="laptop")
        assert query.search_term == "laptop"
        assert query.category_id is None
        assert query.brand_id is None
        assert query.min_price is None
        assert query.max_price is None
        assert query.limit == 50
        assert query.offset == 0

    def test_get_category_query(self):
        """Test GetCategoryQuery."""
        query = GetCategoryQuery(category_id="cat-123")
        assert query.category_id == "cat-123"

    def test_get_categories_query(self):
        """Test GetCategoriesQuery."""
        query = GetCategoriesQuery(
            parent_id="cat-parent",
            include_inactive=True
        )
        assert query.parent_id == "cat-parent"
        assert query.include_inactive is True

    def test_get_categories_query_defaults(self):
        """Test GetCategoriesQuery with defaults."""
        query = GetCategoriesQuery()
        assert query.parent_id is None
        assert query.include_inactive is False

    def test_get_brand_query(self):
        """Test GetBrandQuery."""
        query = GetBrandQuery(brand_id="brand-123")
        assert query.brand_id == "brand-123"

    def test_get_brands_query(self):
        """Test GetBrandsQuery."""
        query = GetBrandsQuery(include_inactive=True)
        assert query.include_inactive is True

    def test_get_brands_query_defaults(self):
        """Test GetBrandsQuery with defaults."""
        query = GetBrandsQuery()
        assert query.include_inactive is False


class TestInMemoryProductQueryHandler:
    """Test InMemoryProductQueryHandler."""

    @pytest.fixture
    def handler(self):
        """Create InMemoryProductQueryHandler."""
        return InMemoryProductQueryHandler()

    @pytest.fixture
    def sample_product(self):
        """Create sample product read model."""
        return ProductReadModel(
            id="prod-123",
            name="Test Product",
            description="Test description",
            price="100.00",
            category_id="cat-123",
            category_name="Electronics",
            brand_id="brand-123",
            brand_name="Test Brand",
            sku="TEST-123",
            is_active=True
        )

    @pytest.fixture
    def sample_category(self):
        """Create sample category read model."""
        return CategoryReadModel(
            id="cat-123",
            name="Electronics",
            description="Electronic devices",
            product_count=1
        )

    @pytest.fixture
    def sample_brand(self):
        """Create sample brand read model."""
        return BrandReadModel(
            id="brand-123",
            name="Test Brand",
            description="Test brand",
            product_count=1
        )

    @pytest.mark.asyncio
    async def test_get_product_found(self, handler, sample_product):
        """Test getting a product that exists."""
        # Arrange
        handler.add_product(sample_product)

        # Act
        result = await handler.get_product(GetProductQuery(product_id="prod-123"))

        # Assert
        assert result is not None
        assert result.id == "prod-123"
        assert result.name == "Test Product"

    @pytest.mark.asyncio
    async def test_get_product_not_found(self, handler):
        """Test getting a product that doesn't exist."""
        # Act
        result = await handler.get_product(GetProductQuery(product_id="prod-999"))

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_get_products_by_category(self, handler, sample_product, sample_category):
        """Test getting products by category."""
        # Arrange
        handler.add_product(sample_product)
        handler.add_category(sample_category)

        # Act
        result = await handler.get_products_by_category(
            GetProductsByCategoryQuery(category_id="cat-123")
        )

        # Assert
        assert len(result) == 1
        assert result[0].id == "prod-123"
        assert result[0].category_id == "cat-123"

    @pytest.mark.asyncio
    async def test_get_products_by_category_empty(self, handler):
        """Test getting products by category when none exist."""
        # Act
        result = await handler.get_products_by_category(
            GetProductsByCategoryQuery(category_id="cat-999")
        )

        # Assert
        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_get_products_by_brand(self, handler, sample_product, sample_brand):
        """Test getting products by brand."""
        # Arrange
        handler.add_product(sample_product)
        handler.add_brand(sample_brand)

        # Act
        result = await handler.get_products_by_brand(
            GetProductsByBrandQuery(brand_id="brand-123")
        )

        # Assert
        assert len(result) == 1
        assert result[0].id == "prod-123"
        assert result[0].brand_id == "brand-123"

    @pytest.mark.asyncio
    async def test_get_products_by_brand_empty(self, handler):
        """Test getting products by brand when none exist."""
        # Act
        result = await handler.get_products_by_brand(
            GetProductsByBrandQuery(brand_id="brand-999")
        )

        # Assert
        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_search_products_by_name(self, handler, sample_product):
        """Test searching products by name."""
        # Arrange
        handler.add_product(sample_product)

        # Act
        result = await handler.search_products(
            SearchProductsQuery(search_term="Test")
        )

        # Assert
        assert len(result) == 1
        assert result[0].id == "prod-123"

    @pytest.mark.asyncio
    async def test_search_products_by_description(self, handler, sample_product):
        """Test searching products by description."""
        # Arrange
        handler.add_product(sample_product)

        # Act
        result = await handler.search_products(
            SearchProductsQuery(search_term="description")
        )

        # Assert
        assert len(result) == 1
        assert result[0].id == "prod-123"

    @pytest.mark.asyncio
    async def test_search_products_by_category(self, handler, sample_product):
        """Test searching products by category filter."""
        # Arrange
        handler.add_product(sample_product)

        # Act
        result = await handler.search_products(
            SearchProductsQuery(
                search_term="Test",
                category_id="cat-123"
            )
        )

        # Assert
        assert len(result) == 1
        assert result[0].id == "prod-123"

    @pytest.mark.asyncio
    async def test_search_products_by_brand(self, handler, sample_product):
        """Test searching products by brand filter."""
        # Arrange
        handler.add_product(sample_product)

        # Act
        result = await handler.search_products(
            SearchProductsQuery(
                search_term="Test",
                brand_id="brand-123"
            )
        )

        # Assert
        assert len(result) == 1
        assert result[0].id == "prod-123"

    @pytest.mark.asyncio
    async def test_search_products_by_price_range(self, handler, sample_product):
        """Test searching products by price range."""
        # Arrange
        handler.add_product(sample_product)

        # Act
        result = await handler.search_products(
            SearchProductsQuery(
                search_term="Test",
                min_price=50.0,
                max_price=150.0
            )
        )

        # Assert
        assert len(result) == 1
        assert result[0].id == "prod-123"

    @pytest.mark.asyncio
    async def test_search_products_no_matches(self, handler, sample_product):
        """Test searching products with no matches."""
        # Arrange
        handler.add_product(sample_product)

        # Act
        result = await handler.search_products(
            SearchProductsQuery(search_term="nonexistent")
        )

        # Assert
        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_search_products_with_limit_and_offset(self, handler):
        """Test searching products with limit and offset."""
        # Arrange
        for i in range(10):
            product = ProductReadModel(
                id=f"prod-{i}",
                name=f"Product {i}",
                description=f"Description {i}",
                price="100.00",
                category_id="cat-123",
                sku=f"SKU-{i}",
                is_active=True
            )
            handler.add_product(product)

        # Act
        result = await handler.search_products(
            SearchProductsQuery(
                search_term="Product",
                limit=3,
                offset=2
            )
        )

        # Assert
        assert len(result) == 3
        assert result[0].id == "prod-2"
        assert result[1].id == "prod-3"
        assert result[2].id == "prod-4"


class TestInMemoryCategoryQueryHandler:
    """Test InMemoryCategoryQueryHandler."""

    @pytest.fixture
    def handler(self):
        """Create InMemoryCategoryQueryHandler."""
        return InMemoryCategoryQueryHandler()

    @pytest.fixture
    def sample_category(self):
        """Create sample category read model."""
        return CategoryReadModel(
            id="cat-123",
            name="Electronics",
            description="Electronic devices",
            product_count=5
        )

    @pytest.mark.asyncio
    async def test_get_category_found(self, handler, sample_category):
        """Test getting a category that exists."""
        # Arrange
        handler.add_category(sample_category)

        # Act
        result = await handler.get_category(GetCategoryQuery(category_id="cat-123"))

        # Assert
        assert result is not None
        assert result.id == "cat-123"
        assert result.name == "Electronics"

    @pytest.mark.asyncio
    async def test_get_category_not_found(self, handler):
        """Test getting a category that doesn't exist."""
        # Act
        result = await handler.get_category(GetCategoryQuery(category_id="cat-999"))

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_get_categories_root(self, handler, sample_category):
        """Test getting root categories."""
        # Arrange
        handler.add_category(sample_category)

        # Act
        result = await handler.get_categories(GetCategoriesQuery())

        # Assert
        assert len(result) == 1
        assert result[0].id == "cat-123"

    @pytest.mark.asyncio
    async def test_get_categories_with_parent(self, handler):
        """Test getting categories with parent filter."""
        # Arrange
        parent_category = CategoryReadModel(
            id="cat-parent",
            name="Technology",
            product_count=0
        )
        child_category = CategoryReadModel(
            id="cat-child",
            name="Electronics",
            parent_id="cat-parent",
            product_count=0
        )
        handler.add_category(parent_category)
        handler.add_category(child_category)

        # Act
        result = await handler.get_categories(
            GetCategoriesQuery(parent_id="cat-parent")
        )

        # Assert
        assert len(result) == 1
        assert result[0].id == "cat-child"
        assert result[0].parent_id == "cat-parent"


class TestInMemoryBrandQueryHandler:
    """Test InMemoryBrandQueryHandler."""

    @pytest.fixture
    def handler(self):
        """Create InMemoryBrandQueryHandler."""
        return InMemoryBrandQueryHandler()

    @pytest.fixture
    def sample_brand(self):
        """Create sample brand read model."""
        return BrandReadModel(
            id="brand-123",
            name="Test Brand",
            description="Test brand description",
            logo_url="https://example.com/logo.png",
            product_count=3
        )

    @pytest.mark.asyncio
    async def test_get_brand_found(self, handler, sample_brand):
        """Test getting a brand that exists."""
        # Arrange
        handler.add_brand(sample_brand)

        # Act
        result = await handler.get_brand(GetBrandQuery(brand_id="brand-123"))

        # Assert
        assert result is not None
        assert result.id == "brand-123"
        assert result.name == "Test Brand"

    @pytest.mark.asyncio
    async def test_get_brand_not_found(self, handler):
        """Test getting a brand that doesn't exist."""
        # Act
        result = await handler.get_brand(GetBrandQuery(brand_id="brand-999"))

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_get_brands(self, handler, sample_brand):
        """Test getting all brands."""
        # Arrange
        handler.add_brand(sample_brand)

        # Act
        result = await handler.get_brands(GetBrandsQuery())

        # Assert
        assert len(result) == 1
        assert result[0].id == "brand-123"
        assert result[0].name == "Test Brand"

    @pytest.mark.asyncio
    async def test_get_brands_empty(self, handler):
        """Test getting brands when none exist."""
        # Act
        result = await handler.get_brands(GetBrandsQuery())

        # Assert
        assert len(result) == 0 