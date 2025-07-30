"""Repository interfaces for the catalog domain."""

# Python imports
from abc import ABC, abstractmethod
from typing import List, Optional

# Local imports
from .entities import Brand, Category, Product
from .value_objects import BrandId, CategoryId, ProductId


class ProductRepository(ABC):
    """Product repository interface.
    
    This interface defines the methods for managing products.
    """

    @abstractmethod
    async def save(self, product: Product) -> Product:
        """
        Save product.
        
        Args:
            product: The product to save.
            
        Returns:
            Product: The saved product.
        """
        pass

    @abstractmethod
    async def get_by_id(self, product_id: ProductId) -> Optional[Product]:
        """
        Get product by ID.
        
        Args:
            product_id: The ID of the product to get.
            
        Returns:
            Optional[Product]: The product if found, None otherwise.
        """
        pass

    @abstractmethod
    async def get_by_sku(self, sku: str) -> Optional[Product]:
        """
        Get product by SKU.
        
        Args:
            sku: The SKU of the product to get.
            
        Returns:
            Optional[Product]: The product if found, None otherwise.
        """
        pass

    @abstractmethod
    async def get_by_category(self, category_id: CategoryId) -> List[Product]:
        """
        Get products by category.
        
        Args:
            category_id: The ID of the category to get products for.
            
        Returns:
            List[Product]: The list of products in the category.
        """
        pass

    @abstractmethod
    async def get_by_brand(self, brand_id: BrandId) -> List[Product]:
        """
        Get products by brand.
        
        Args:
            brand_id: The ID of the brand to get products for.
            
        Returns:
            List[Product]: The list of products in the brand.
        """
        pass

    @abstractmethod
    async def get_active_products(self) -> List[Product]:
        """
        Get all active products.
        
        Returns:
            List[Product]: The list of active products.
        """
        pass

    @abstractmethod
    async def delete(self, product_id: ProductId) -> None:
        """
        Delete product.
        
        Args:
            product_id: The ID of the product to delete.
        """
        pass


class CategoryRepository(ABC):
    """Category repository interface.
    
    This interface defines the methods for managing categories.
    """

    @abstractmethod
    async def save(self, category: Category) -> Category:
        """
        Save category.
        
        Args:
            category: The category to save.
            
        Returns:
            Category: The saved category.
        """
        pass

    @abstractmethod
    async def get_by_id(self, category_id: CategoryId) -> Optional[Category]:
        """
        Get category by ID.
        
        Args:
            category_id: The ID of the category to get.
            
        Returns:
            Optional[Category]: The category if found, None otherwise.
        """
        pass

    @abstractmethod
    async def get_root_categories(self) -> List[Category]:
        """
        Get root categories.
        
        Returns:
            List[Category]: The list of root categories.
        """
        pass

    @abstractmethod
    async def get_subcategories(self, parent_id: CategoryId) -> List[Category]:
        """
        Get subcategories.
        
        Args:
            parent_id: The ID of the parent category to get subcategories for.
            
        Returns:
            List[Category]: The list of subcategories.
        """
        pass

    @abstractmethod
    async def get_active_categories(self) -> List[Category]:
        """
        Get all active categories.
        
        Returns:
            List[Category]: The list of active categories.
        """
        pass

    @abstractmethod
    async def delete(self, category_id: CategoryId) -> None:
        """
        Delete category.
        
        Args:
            category_id: The ID of the category to delete.
        """
        pass


class BrandRepository(ABC):
    """Brand repository interface.
    
    This interface defines the methods for managing brands.
    """

    @abstractmethod
    async def save(self, brand: Brand) -> Brand:
        """
        Save brand.
        
        Args:
            brand: The brand to save.
            
        Returns:
            Brand: The saved brand.
        """
        pass

    @abstractmethod
    async def get_by_id(self, brand_id: BrandId) -> Optional[Brand]:
        """
        Get brand by ID.
        
        Args:
            brand_id: The ID of the brand to get.
            
        Returns:
            Optional[Brand]: The brand if found, None otherwise.
        """
        pass

    @abstractmethod
    async def get_by_name(self, name: str) -> Optional[Brand]:
        """
        Get brand by name.
        
        Args:
            name: The name of the brand to get.
            
        Returns:
            Optional[Brand]: The brand if found, None otherwise.
        """
        pass

    @abstractmethod
    async def get_active_brands(self) -> List[Brand]:
        """
        Get all active brands.
        
        Returns:
            List[Brand]: The list of active brands.
        """
        pass

    @abstractmethod
    async def delete(self, brand_id: BrandId) -> None:
        """
        Delete brand.
        
        Args:
            brand_id: The ID of the brand to delete.
        """
        pass
