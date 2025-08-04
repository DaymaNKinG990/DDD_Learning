"""In-memory repository implementations for catalog domain."""

# Python imports
from typing import Dict, List, Optional

# Local imports
from src.catalog.domain.entities import Brand, Category, Product
from src.catalog.domain.repositories import (
    BrandRepository,
    CategoryRepository,
    ProductRepository,
)
from src.catalog.domain.value_objects import BrandId, CategoryId, ProductId
from src.shared.infrastructure.repositories import InMemoryRepository


class InMemoryProductRepository(InMemoryRepository[Product], ProductRepository):
    """
    In-memory implementation of ProductRepository.
    
    This class provides an in-memory implementation of the product repository.
    """

    def __init__(self) -> None:
        """Initialize the in-memory product repository."""
        super().__init__()
        self._products: Dict[str, Product] = {}

    async def save(self, product: Product) -> Product:
        """
        Save product to in-memory storage.
        
        Args:
            product: The product to save.
            
        Returns:
            Product: The saved product.
        """
        self._products[str(product.id)] = product
        return product

    async def get_by_id(self, product_id: ProductId) -> Optional[Product]:
        """
        Get product by ID.
        
        Args:
            product_id: The ID of the product to get.
            
        Returns:
            Optional[Product]: The product if found, None otherwise.
        """
        return self._products.get(str(product_id))

    async def get_by_sku(self, sku: str) -> Optional[Product]:
        """
        Get product by SKU.
        
        Args:
            sku: The SKU of the product to get.
            
        Returns:
            Optional[Product]: The product if found, None otherwise.
        """
        for product in self._products.values():
            if product.sku == sku:
                return product
        return None

    async def get_active_products(self) -> List[Product]:
        """
        Get all active products.
        
        Returns:
            List[Product]: The list of active products.
        """
        return [product for product in self._products.values() if product.is_active]

    async def get_all(self) -> List[Product]:
        """
        Get all products.
        
        Returns:
            List[Product]: The list of products.
        """
        return list(self._products.values())

    async def get_by_category(self, category_id: CategoryId) -> List[Product]:
        """
        Get products by category.
        
        Args:
            category_id: The ID of the category to get products for.
            
        Returns:
            List[Product]: The list of products in the category.
        """
        return [
            product for product in self._products.values()
            if product.category_id == category_id
        ]

    async def get_by_brand(self, brand_id: BrandId) -> List[Product]:
        """
        Get products by brand.
        
        Args:
            brand_id: The ID of the brand to get products for.
            
        Returns:
            List[Product]: The list of products in the brand.
        """
        return [
            product for product in self._products.values()
            if product.brand_id == brand_id
        ]

    async def get_by_seller_id(self, seller_id: str) -> List[Product]:
        """
        Get products by seller ID.
        
        Args:
            seller_id: The ID of the seller to get products for.
            
        Returns:
            List[Product]: The list of products for the seller.
        """
        # For now, return all products since we don't have seller_id in Product entity
        # In a real implementation, Product would have a seller_id field
        return list(self._products.values())

    async def search_products(self, query: str) -> List[Product]:
        """
        Search products by query.
        
        Args:
            query: The search query.
            
        Returns:
            List[Product]: The list of products matching the query.
        """
        query_lower = query.lower()
        return [
            product for product in self._products.values()
            if query_lower in product.name.value.lower() or 
               query_lower in product.description.value.lower()
        ]

    async def delete(self, product_id: ProductId) -> bool:
        """
        Delete product by ID.
        
        Args:
            product_id: The ID of the product to delete.
            
        Returns:
            bool: True if the product was deleted, False otherwise.
        """
        if str(product_id) in self._products:
            del self._products[str(product_id)]
            return True
        return False


class InMemoryCategoryRepository(InMemoryRepository[Category], CategoryRepository):
    """
    In-memory implementation of CategoryRepository.
    
    This class provides an in-memory implementation of the category repository.
    """

    def __init__(self) -> None:
        """Initialize the in-memory category repository."""
        super().__init__()
        self._categories: Dict[str, Category] = {}

    async def save(self, category: Category) -> Category:
        """
        Save category to in-memory storage.
        
        Args:
            category: The category to save.
            
        Returns:
            Category: The saved category.
        """
        self._categories[str(category.id)] = category
        return category

    async def get_by_id(self, category_id: CategoryId) -> Optional[Category]:
        """
        Get category by ID.
        
        Args:
            category_id: The ID of the category to get.
            
        Returns:
            Optional[Category]: The category if found, None otherwise.
        """
        return self._categories.get(str(category_id))

    async def get_by_name(self, name: str) -> Optional[Category]:
        """
        Get category by name.
        
        Args:
            name: The name of the category to get.
            
        Returns:
            Optional[Category]: The category if found, None otherwise.
        """
        for category in self._categories.values():
            if category.name == name:
                return category
        return None

    async def get_root_categories(self) -> List[Category]:
        """
        Get root categories.
        
        Returns:
            List[Category]: The list of root categories.
        """
        return [category for category in self._categories.values() if category.parent_id is None]

    async def get_subcategories(self, parent_id: CategoryId) -> List[Category]:
        """
        Get subcategories.
        
        Args:
            parent_id: The ID of the parent category to get subcategories for.
            
        Returns:
            List[Category]: The list of subcategories.
        """
        return [category for category in self._categories.values() if category.parent_id == parent_id]

    async def get_children(self, parent_id: CategoryId) -> List[Category]:
        """
        Get child categories.
        
        Args:
            parent_id: The ID of the parent category to get children for.
            
        Returns:
            List[Category]: The list of child categories.
        """
        return [category for category in self._categories.values() if category.parent_id == parent_id]

    async def get_active_categories(self) -> List[Category]:
        """
        Get all active categories.
        
        Returns:
            List[Category]: The list of active categories.
        """
        return [category for category in self._categories.values() if category.is_active]

    async def get_all(self) -> List[Category]:
        """
        Get all categories.
        
        Returns:
            List[Category]: The list of categories.
        """
        return list(self._categories.values())

    async def get_by_parent(self, parent_id: CategoryId) -> List[Category]:
        """
        Get categories by parent.
        
        Args:
            parent_id: The ID of the parent category to get subcategories for.
            
        Returns:
            List[Category]: The list of subcategories.
        """
        return [
            category for category in self._categories.values()
            if category.parent_id == parent_id
        ]

    async def delete(self, category_id: CategoryId) -> bool:
        """
        Delete category by ID.
        
        Args:
            category_id: The ID of the category to delete.
            
        Returns:
            bool: True if the category was deleted, False otherwise.
        """
        if str(category_id) in self._categories:
            del self._categories[str(category_id)]
            return True
        return False


class InMemoryBrandRepository(InMemoryRepository[Brand], BrandRepository):
    """
    In-memory implementation of BrandRepository.
    
    This class provides an in-memory implementation of the brand repository.
    """

    def __init__(self) -> None:
        """Initialize the in-memory brand repository."""
        super().__init__()
        self._brands: Dict[str, Brand] = {}

    async def save(self, brand: Brand) -> Brand:
        """
        Save brand to in-memory storage.
        
        Args:
            brand: The brand to save.
            
        Returns:
            Brand: The saved brand.
        """
        self._brands[str(brand.id)] = brand
        return brand

    async def get_by_id(self, brand_id: BrandId) -> Optional[Brand]:
        """
        Get brand by ID.
        
        Args:
            brand_id: The ID of the brand to get.
            
        Returns:
            Optional[Brand]: The brand if found, None otherwise.
        """
        return self._brands.get(str(brand_id))

    async def get_by_name(self, name: str) -> Optional[Brand]:
        """
        Get brand by name.
        
        Args:
            name: The name of the brand to get.
            
        Returns:
            Optional[Brand]: The brand if found, None otherwise.
        """
        for brand in self._brands.values():
            if brand.name == name:
                return brand
        return None

    async def get_active_brands(self) -> List[Brand]:
        """
        Get all active brands.
        
        Returns:
            List[Brand]: The list of active brands.
        """
        return [brand for brand in self._brands.values() if brand.is_active]

    async def get_all(self) -> List[Brand]:
        """
        Get all brands.
        
        Returns:
            List[Brand]: The list of brands.
        """
        return list(self._brands.values())

    async def delete(self, brand_id: BrandId) -> bool:
        """
        Delete brand by ID.
        
        Args:
            brand_id: The ID of the brand to delete.
            
        Returns:
            bool: True if the brand was deleted, False otherwise.
        """
        if str(brand_id) in self._brands:
            del self._brands[str(brand_id)]
            return True
        return False
