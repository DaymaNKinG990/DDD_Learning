"""Repository interfaces for the catalog domain."""

from abc import ABC, abstractmethod
from typing import List, Optional

from .entities import Brand, Category, Product
from .value_objects import BrandId, CategoryId, ProductId


class ProductRepository(ABC):
    """Product repository interface."""
    
    @abstractmethod
    async def save(self, product: Product) -> Product:
        """Save product."""
        pass
    
    @abstractmethod
    async def get_by_id(self, product_id: ProductId) -> Optional[Product]:
        """Get product by ID."""
        pass
    
    @abstractmethod
    async def get_by_sku(self, sku: str) -> Optional[Product]:
        """Get product by SKU."""
        pass
    
    @abstractmethod
    async def get_by_category(self, category_id: CategoryId) -> List[Product]:
        """Get products by category."""
        pass
    
    @abstractmethod
    async def get_by_brand(self, brand_id: BrandId) -> List[Product]:
        """Get products by brand."""
        pass
    
    @abstractmethod
    async def get_active_products(self) -> List[Product]:
        """Get all active products."""
        pass
    
    @abstractmethod
    async def delete(self, product_id: ProductId) -> None:
        """Delete product."""
        pass


class CategoryRepository(ABC):
    """Category repository interface."""
    
    @abstractmethod
    async def save(self, category: Category) -> Category:
        """Save category."""
        pass
    
    @abstractmethod
    async def get_by_id(self, category_id: CategoryId) -> Optional[Category]:
        """Get category by ID."""
        pass
    
    @abstractmethod
    async def get_root_categories(self) -> List[Category]:
        """Get root categories."""
        pass
    
    @abstractmethod
    async def get_subcategories(self, parent_id: CategoryId) -> List[Category]:
        """Get subcategories."""
        pass
    
    @abstractmethod
    async def get_active_categories(self) -> List[Category]:
        """Get all active categories."""
        pass
    
    @abstractmethod
    async def delete(self, category_id: CategoryId) -> None:
        """Delete category."""
        pass


class BrandRepository(ABC):
    """Brand repository interface."""
    
    @abstractmethod
    async def save(self, brand: Brand) -> Brand:
        """Save brand."""
        pass
    
    @abstractmethod
    async def get_by_id(self, brand_id: BrandId) -> Optional[Brand]:
        """Get brand by ID."""
        pass
    
    @abstractmethod
    async def get_by_name(self, name: str) -> Optional[Brand]:
        """Get brand by name."""
        pass
    
    @abstractmethod
    async def get_active_brands(self) -> List[Brand]:
        """Get all active brands."""
        pass
    
    @abstractmethod
    async def delete(self, brand_id: BrandId) -> None:
        """Delete brand."""
        pass