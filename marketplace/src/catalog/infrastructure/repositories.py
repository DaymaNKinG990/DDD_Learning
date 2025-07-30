"""In-memory repository implementations for catalog domain."""

from typing import Dict, List, Optional

from src.catalog.domain.entities import Brand, Category, Product
from src.catalog.domain.repositories import (
    BrandRepository,
    CategoryRepository,
    ProductRepository,
)
from src.catalog.domain.value_objects import BrandId, CategoryId, ProductId
from src.shared.infrastructure.repositories import InMemoryRepository


class InMemoryProductRepository(
    InMemoryRepository[Product], ProductRepository
):
    """In-memory implementation of ProductRepository."""

    def __init__(self):
        super().__init__()
        self._products: Dict[str, Product] = {}

    async def save(self, product: Product) -> Product:
        """Save product to in-memory storage."""
        self._products[str(product.id)] = product
        return product

    async def get_by_id(self, product_id: ProductId) -> Optional[Product]:
        """Get product by ID."""
        return self._products.get(str(product_id))

    async def get_all(self) -> List[Product]:
        """Get all products."""
        return list(self._products.values())

    async def get_by_category(self, category_id: CategoryId) -> List[Product]:
        """Get products by category."""
        return [
            product for product in self._products.values()
            if product.category_id == category_id
        ]

    async def get_by_brand(self, brand_id: BrandId) -> List[Product]:
        """Get products by brand."""
        return [
            product for product in self._products.values()
            if product.brand_id == brand_id
        ]

    async def delete(self, product_id: ProductId) -> bool:
        """Delete product by ID."""
        if str(product_id) in self._products:
            del self._products[str(product_id)]
            return True
        return False


class InMemoryCategoryRepository(
    InMemoryRepository[Category], CategoryRepository
):
    """In-memory implementation of CategoryRepository."""

    def __init__(self):
        super().__init__()
        self._categories: Dict[str, Category] = {}

    async def save(self, category: Category) -> Category:
        """Save category to in-memory storage."""
        self._categories[str(category.id)] = category
        return category

    async def get_by_id(self, category_id: CategoryId) -> Optional[Category]:
        """Get category by ID."""
        return self._categories.get(str(category_id))

    async def get_all(self) -> List[Category]:
        """Get all categories."""
        return list(self._categories.values())

    async def get_by_parent(self, parent_id: CategoryId) -> List[Category]:
        """Get categories by parent."""
        return [
            category for category in self._categories.values()
            if category.parent_id == parent_id
        ]

    async def delete(self, category_id: CategoryId) -> bool:
        """Delete category by ID."""
        if str(category_id) in self._categories:
            del self._categories[str(category_id)]
            return True
        return False


class InMemoryBrandRepository(InMemoryRepository[Brand], BrandRepository):
    """In-memory implementation of BrandRepository."""

    def __init__(self):
        super().__init__()
        self._brands: Dict[str, Brand] = {}

    async def save(self, brand: Brand) -> Brand:
        """Save brand to in-memory storage."""
        self._brands[str(brand.id)] = brand
        return brand

    async def get_by_id(self, brand_id: BrandId) -> Optional[Brand]:
        """Get brand by ID."""
        return self._brands.get(str(brand_id))

    async def get_all(self) -> List[Brand]:
        """Get all brands."""
        return list(self._brands.values())

    async def delete(self, brand_id: BrandId) -> bool:
        """Delete brand by ID."""
        if str(brand_id) in self._brands:
            del self._brands[str(brand_id)]
            return True
        return False
