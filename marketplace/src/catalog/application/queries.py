"""CQRS queries for catalog bounded context."""

from abc import ABC, abstractmethod
from typing import List, Optional

from pydantic import BaseModel


# Query Models (Read Models)
class ProductReadModel(BaseModel):
    """Read model for product queries."""

    id: str
    name: str
    description: str
    price: str
    category_id: str
    category_name: Optional[str] = None
    brand_id: Optional[str] = None
    brand_name: Optional[str] = None
    sku: str
    is_active: bool


class CategoryReadModel(BaseModel):
    """Read model for category queries."""

    id: str
    name: str
    description: Optional[str] = None
    parent_id: Optional[str] = None
    parent_name: Optional[str] = None
    product_count: int = 0


class BrandReadModel(BaseModel):
    """Read model for brand queries."""

    id: str
    name: str
    description: Optional[str] = None
    logo_url: Optional[str] = None
    product_count: int = 0


# Query Objects
class GetProductQuery(BaseModel):
    """Query to get a product by ID."""

    product_id: str


class GetProductsByCategoryQuery(BaseModel):
    """Query to get products by category."""

    category_id: str
    limit: Optional[int] = 50
    offset: Optional[int] = 0


class GetProductsByBrandQuery(BaseModel):
    """Query to get products by brand."""

    brand_id: str
    limit: Optional[int] = 50
    offset: Optional[int] = 0


class SearchProductsQuery(BaseModel):
    """Query to search products."""

    search_term: str
    category_id: Optional[str] = None
    brand_id: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    limit: Optional[int] = 50
    offset: Optional[int] = 0


class GetCategoryQuery(BaseModel):
    """Query to get a category by ID."""

    category_id: str


class GetCategoriesQuery(BaseModel):
    """Query to get all categories."""

    parent_id: Optional[str] = None
    include_inactive: bool = False


class GetBrandQuery(BaseModel):
    """Query to get a brand by ID."""

    brand_id: str


class GetBrandsQuery(BaseModel):
    """Query to get all brands."""

    include_inactive: bool = False


# Query Handlers
class ProductQueryHandler(ABC):
    """Abstract query handler for product queries."""

    @abstractmethod
    async def get_product(self, query: GetProductQuery) -> Optional[ProductReadModel]:
        """Get product by ID."""
        pass

    @abstractmethod
    async def get_products_by_category(
        self, query: GetProductsByCategoryQuery
    ) -> List[ProductReadModel]:
        """Get products by category."""
        pass

    @abstractmethod
    async def get_products_by_brand(
        self, query: GetProductsByBrandQuery
    ) -> List[ProductReadModel]:
        """Get products by brand."""
        pass

    @abstractmethod
    async def search_products(
        self, query: SearchProductsQuery
    ) -> List[ProductReadModel]:
        """Search products."""
        pass


class CategoryQueryHandler(ABC):
    """Abstract query handler for category queries."""

    @abstractmethod
    async def get_category(
        self, query: GetCategoryQuery
    ) -> Optional[CategoryReadModel]:
        """Get category by ID."""
        pass

    @abstractmethod
    async def get_categories(
        self, query: GetCategoriesQuery
    ) -> List[CategoryReadModel]:
        """Get categories."""
        pass


class BrandQueryHandler(ABC):
    """Abstract query handler for brand queries."""

    @abstractmethod
    async def get_brand(self, query: GetBrandQuery) -> Optional[BrandReadModel]:
        """Get brand by ID."""
        pass

    @abstractmethod
    async def get_brands(self, query: GetBrandsQuery) -> List[BrandReadModel]:
        """Get brands."""
        pass


# In-Memory Query Handlers (for testing/demo)
class InMemoryProductQueryHandler(ProductQueryHandler):
    """In-memory implementation of product query handler."""

    def __init__(self):
        self._products: dict[str, ProductReadModel] = {}
        self._categories: dict[str, CategoryReadModel] = {}
        self._brands: dict[str, BrandReadModel] = {}

    async def get_product(self, query: GetProductQuery) -> Optional[ProductReadModel]:
        """Get product by ID."""
        return self._products.get(query.product_id)

    async def get_products_by_category(
        self, query: GetProductsByCategoryQuery
    ) -> List[ProductReadModel]:
        """Get products by category."""
        products = [
            product for product in self._products.values()
            if product.category_id == query.category_id and product.is_active
        ]

        # Apply pagination
        start = query.offset or 0
        end = start + (query.limit or 50)
        return products[start:end]

    async def get_products_by_brand(
        self, query: GetProductsByBrandQuery
    ) -> List[ProductReadModel]:
        """Get products by brand."""
        products = [
            product for product in self._products.values()
            if product.brand_id == query.brand_id and product.is_active
        ]

        # Apply pagination
        start = query.offset or 0
        end = start + (query.limit or 50)
        return products[start:end]

    async def search_products(
        self, query: SearchProductsQuery
    ) -> List[ProductReadModel]:
        """Search products."""
        products = [
            product for product in self._products.values()
            if product.is_active and self._matches_search_criteria(product, query)
        ]

        # Apply pagination
        start = query.offset or 0
        end = start + (query.limit or 50)
        return products[start:end]

    def _matches_search_criteria(
        self, product: ProductReadModel, query: SearchProductsQuery
    ) -> bool:
        """Check if product matches search criteria."""
        # Search term matching
        if query.search_term:
            search_lower = query.search_term.lower()
            if (search_lower not in product.name.lower() and
                search_lower not in product.description.lower()):
                return False

        # Category filter
        if query.category_id and product.category_id != query.category_id:
            return False

        # Brand filter
        if query.brand_id and product.brand_id != query.brand_id:
            return False

        # Price range filter
        try:
            price = float(product.price.replace("RUB", "").strip())
            if query.min_price and price < query.min_price:
                return False
            if query.max_price and price > query.max_price:
                return False
        except ValueError:
            pass

        return True

    def add_product(self, product: ProductReadModel) -> None:
        """Add product to in-memory storage."""
        self._products[product.id] = product

    def add_category(self, category: CategoryReadModel) -> None:
        """Add category to in-memory storage."""
        self._categories[category.id] = category

    def add_brand(self, brand: BrandReadModel) -> None:
        """Add brand to in-memory storage."""
        self._brands[brand.id] = brand


class InMemoryCategoryQueryHandler(CategoryQueryHandler):
    """In-memory implementation of category query handler."""

    def __init__(self):
        self._categories: dict[str, CategoryReadModel] = {}

    async def get_category(
        self, query: GetCategoryQuery
    ) -> Optional[CategoryReadModel]:
        """Get category by ID."""
        return self._categories.get(query.category_id)

    async def get_categories(
        self, query: GetCategoriesQuery
    ) -> List[CategoryReadModel]:
        """Get categories."""
        categories = list(self._categories.values())

        if query.parent_id is not None:
            categories = [cat for cat in categories if cat.parent_id == query.parent_id]

        return categories

    def add_category(self, category: CategoryReadModel) -> None:
        """Add category to in-memory storage."""
        self._categories[category.id] = category


class InMemoryBrandQueryHandler(BrandQueryHandler):
    """In-memory implementation of brand query handler."""

    def __init__(self):
        self._brands: dict[str, BrandReadModel] = {}

    async def get_brand(self, query: GetBrandQuery) -> Optional[BrandReadModel]:
        """Get brand by ID."""
        return self._brands.get(query.brand_id)

    async def get_brands(self, query: GetBrandsQuery) -> List[BrandReadModel]:
        """Get brands."""
        return list(self._brands.values())

    def add_brand(self, brand: BrandReadModel) -> None:
        """Add brand to in-memory storage."""
        self._brands[brand.id] = brand
