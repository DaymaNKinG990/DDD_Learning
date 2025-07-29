"""Entities for the catalog domain."""

from datetime import datetime
from typing import List, Optional

from pydantic import Field

from src.shared.domain.entity import Entity, EntityId

from .value_objects import (
    BrandId,
    CategoryId,
    Price,
    ProductDescription,
    ProductId,
    ProductName,
)


class Product(Entity[ProductId]):
    """Product entity."""
    
    name: ProductName = Field(description="Product name")
    description: ProductDescription = Field(description="Product description")
    price: Price = Field(description="Product price")
    category_id: CategoryId = Field(description="Product category")
    brand_id: Optional[BrandId] = Field(default=None, description="Product brand")
    sku: str = Field(description="Stock keeping unit")
    is_active: bool = Field(default=True, description="Product availability")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    
    def __hash__(self) -> int:
        return hash(self.id)
    
    def update_price(self, new_price: Price) -> "Product":
        """Update product price."""
        return Product(
            id=self.id,
            name=self.name,
            description=self.description,
            price=new_price,
            category_id=self.category_id,
            brand_id=self.brand_id,
            sku=self.sku,
            is_active=self.is_active,
            created_at=self.created_at,
            updated_at=datetime.utcnow(),
        )
    
    def deactivate(self) -> "Product":
        """Deactivate product."""
        return Product(
            id=self.id,
            name=self.name,
            description=self.description,
            price=self.price,
            category_id=self.category_id,
            brand_id=self.brand_id,
            sku=self.sku,
            is_active=False,
            created_at=self.created_at,
            updated_at=datetime.utcnow(),
        )
    
    def activate(self) -> "Product":
        """Activate product."""
        return Product(
            id=self.id,
            name=self.name,
            description=self.description,
            price=self.price,
            category_id=self.category_id,
            brand_id=self.brand_id,
            sku=self.sku,
            is_active=True,
            created_at=self.created_at,
            updated_at=datetime.utcnow(),
        )


class Category(Entity[CategoryId]):
    """Category entity."""
    
    name: str = Field(description="Category name")
    description: Optional[str] = Field(default=None, description="Category description")
    parent_id: Optional[CategoryId] = Field(default=None, description="Parent category")
    is_active: bool = Field(default=True, description="Category availability")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    
    def __hash__(self) -> int:
        return hash(self.id)
    
    def add_subcategory(self, subcategory: "Category") -> None:
        """Add subcategory to this category."""
        if subcategory.parent_id != self.id:
            raise ValueError("Subcategory must have this category as parent")
    
    def deactivate(self) -> "Category":
        """Deactivate category."""
        return Category(
            id=self.id,
            name=self.name,
            description=self.description,
            parent_id=self.parent_id,
            is_active=False,
            created_at=self.created_at,
            updated_at=datetime.utcnow(),
        )


class Brand(Entity[BrandId]):
    """Brand entity."""
    
    name: str = Field(description="Brand name")
    description: Optional[str] = Field(default=None, description="Brand description")
    logo_url: Optional[str] = Field(default=None, description="Brand logo URL")
    is_active: bool = Field(default=True, description="Brand availability")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    
    def __hash__(self) -> int:
        return hash(self.id)
    
    def deactivate(self) -> "Brand":
        """Deactivate brand."""
        return Brand(
            id=self.id,
            name=self.name,
            description=self.description,
            logo_url=self.logo_url,
            is_active=False,
            created_at=self.created_at,
            updated_at=datetime.utcnow(),
        )