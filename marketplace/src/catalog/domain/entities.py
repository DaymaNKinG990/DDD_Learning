"""Entities for the catalog domain."""

# Python imports
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Optional

# Local imports
from src.shared.domain.entity import Entity

from .value_objects import (
    BrandId,
    CategoryId,
    Price,
    ProductDescription,
    ProductId,
    ProductName,
)


@dataclass
class Product(Entity[ProductId]):
    """Product entity.
    
    Attributes:
        name: The product name.
        description: The product description.
        price: The product price.
        category_id: The category ID.
        brand_id: The brand ID.
        sku: The product SKU.
        stock_quantity: The stock quantity.
        is_active: Whether the product is active.
        created_at: The creation timestamp.
        updated_at: The last update timestamp.
    """

    name: ProductName
    description: ProductDescription
    price: Price
    category_id: CategoryId
    brand_id: Optional[BrandId] = None
    sku: str = ""
    stock_quantity: int = 0
    is_active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __hash__(self) -> int:
        """Hash the product."""
        return hash(self.id)

    def update_price(self, new_price: Price) -> None:
        """Update product price.
        
        Args:
            new_price: The new price to set.
        """
        self.price = new_price
        self.updated_at = datetime.now(UTC)

    def deactivate(self) -> None:
        """Deactivate product.
        
        This method deactivates the product by setting the is_active flag to False
        and updating the updated_at timestamp.
        """
        self.is_active = False
        self.updated_at = datetime.now(UTC)

    def activate(self) -> None:
        """Activate product.
        
        This method activates the product by setting the is_active flag to True
        and updating the updated_at timestamp.
        """
        self.is_active = True
        self.updated_at = datetime.now(UTC)


@dataclass
class Category(Entity[CategoryId]):
    """Category entity.
    
    Attributes:
        name: The category name.
        description: The category description.
        parent_id: The parent category ID.
        is_active: Whether the category is active.
        created_at: The creation timestamp.
        updated_at: The last update timestamp.
    """

    name: str
    description: Optional[str] = None
    parent_id: Optional[CategoryId] = None
    is_active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __hash__(self) -> int:
        """Hash the category."""
        return hash(self.id)

    def add_subcategory(self, subcategory: "Category") -> None:
        """Add subcategory to this category.
        
        Args:
            subcategory: The subcategory to add.
            
        Raises:
            ValueError: If the subcategory does not have this category as parent.
        """
        if subcategory.parent_id != self.id:
            raise ValueError("Subcategory must have this category as parent")

    def deactivate(self) -> None:
        """Deactivate category.
        
        This method deactivates the category by setting the is_active flag to False
        and updating the updated_at timestamp.
        """
        self.is_active = False
        self.updated_at = datetime.now(UTC)


@dataclass
class Brand(Entity[BrandId]):
    """Brand entity.
    
    Attributes:
        name: The brand name.
        description: The brand description.
        logo_url: The brand logo URL.
        is_active: Whether the brand is active.
        created_at: The creation timestamp.
        updated_at: The last update timestamp.
    """

    name: str
    description: Optional[str] = None
    logo_url: Optional[str] = None
    is_active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __hash__(self) -> int:
        """Hash the brand."""
        return hash(self.id)

    def deactivate(self) -> None:
        """Deactivate brand.
        
        This method deactivates the brand by setting the is_active flag to False
        and updating the updated_at timestamp.
        """
        self.is_active = False
        self.updated_at = datetime.now(UTC)
