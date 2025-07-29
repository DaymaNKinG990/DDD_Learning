"""Application services for the catalog domain."""

from typing import List, Optional

from src.shared.domain.exceptions import EntityNotFoundError

from ..domain.entities import Brand, Category, Product
from ..domain.repositories import BrandRepository, CategoryRepository, ProductRepository
from ..domain.value_objects import (
    BrandId,
    CategoryId,
    Price,
    ProductDescription,
    ProductId,
    ProductName,
)


class CatalogService:
    """Catalog application service."""
    
    def __init__(
        self,
        product_repository: ProductRepository,
        category_repository: CategoryRepository,
        brand_repository: BrandRepository,
    ) -> None:
        """Initialize catalog service."""
        self._product_repository = product_repository
        self._category_repository = category_repository
        self._brand_repository = brand_repository
    
    # Product operations
    async def create_product(
        self,
        name: str,
        description: str,
        price: Price,
        category_id: CategoryId,
        sku: str,
        brand_id: Optional[BrandId] = None,
    ) -> Product:
        """Create a new product."""
        # Validate category exists
        category = await self._category_repository.get_by_id(category_id)
        if not category:
            raise EntityNotFoundError(f"Category with id {category_id} not found")
        
        # Validate brand exists if provided
        if brand_id:
            brand = await self._brand_repository.get_by_id(brand_id)
            if not brand:
                raise EntityNotFoundError(f"Brand with id {brand_id} not found")
        
        # Check if SKU already exists
        existing_product = await self._product_repository.get_by_sku(sku)
        if existing_product:
            raise ValueError(f"Product with SKU {sku} already exists")
        
        product = Product(
            id=ProductId(value=f"prod_{sku}"),
            name=ProductName(value=name),
            description=ProductDescription(value=description),
            price=price,
            category_id=category_id,
            brand_id=brand_id,
            sku=sku,
        )
        
        return await self._product_repository.save(product)
    
    async def get_product(self, product_id: ProductId) -> Product:
        """Get product by ID."""
        product = await self._product_repository.get_by_id(product_id)
        if not product:
            raise EntityNotFoundError(f"Product with id {product_id} not found")
        return product
    
    async def update_product_price(self, product_id: ProductId, new_price: Price) -> Product:
        """Update product price."""
        product = await self.get_product(product_id)
        updated_product = product.update_price(new_price)
        return await self._product_repository.save(updated_product)
    
    async def deactivate_product(self, product_id: ProductId) -> Product:
        """Deactivate product."""
        product = await self.get_product(product_id)
        deactivated_product = product.deactivate()
        return await self._product_repository.save(deactivated_product)
    
    async def get_products_by_category(self, category_id: CategoryId) -> List[Product]:
        """Get products by category."""
        return await self._product_repository.get_by_category(category_id)
    
    async def get_products_by_brand(self, brand_id: BrandId) -> List[Product]:
        """Get products by brand."""
        return await self._product_repository.get_by_brand(brand_id)
    
    async def get_active_products(self) -> List[Product]:
        """Get all active products."""
        return await self._product_repository.get_active_products()
    
    # Category operations
    async def create_category(
        self,
        name: str,
        description: Optional[str] = None,
        parent_id: Optional[CategoryId] = None,
    ) -> Category:
        """Create a new category."""
        if parent_id:
            parent = await self._category_repository.get_by_id(parent_id)
            if not parent:
                raise EntityNotFoundError(f"Parent category with id {parent_id} not found")
        
        category = Category(
            id=CategoryId(value=f"cat_{name.lower().replace(' ', '_')}"),
            name=name,
            description=description,
            parent_id=parent_id,
        )
        
        return await self._category_repository.save(category)
    
    async def get_category(self, category_id: CategoryId) -> Category:
        """Get category by ID."""
        category = await self._category_repository.get_by_id(category_id)
        if not category:
            raise EntityNotFoundError(f"Category with id {category_id} not found")
        return category
    
    async def get_root_categories(self) -> List[Category]:
        """Get root categories."""
        return await self._category_repository.get_root_categories()
    
    async def get_subcategories(self, parent_id: CategoryId) -> List[Category]:
        """Get subcategories."""
        return await self._category_repository.get_subcategories(parent_id)
    
    # Brand operations
    async def create_brand(
        self,
        name: str,
        description: Optional[str] = None,
        logo_url: Optional[str] = None,
    ) -> Brand:
        """Create a new brand."""
        # Check if brand with same name already exists
        existing_brand = await self._brand_repository.get_by_name(name)
        if existing_brand:
            raise ValueError(f"Brand with name {name} already exists")
        
        brand = Brand(
            id=BrandId(value=f"brand_{name.lower().replace(' ', '_')}"),
            name=name,
            description=description,
            logo_url=logo_url,
        )
        
        return await self._brand_repository.save(brand)
    
    async def get_brand(self, brand_id: BrandId) -> Brand:
        """Get brand by ID."""
        brand = await self._brand_repository.get_by_id(brand_id)
        if not brand:
            raise EntityNotFoundError(f"Brand with id {brand_id} not found")
        return brand
    
    async def get_active_brands(self) -> List[Brand]:
        """Get all active brands."""
        return await self._brand_repository.get_active_brands()