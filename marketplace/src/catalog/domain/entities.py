"""Entities for the catalog domain."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Optional

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
    """Product entity."""

    name: ProductName
    description: ProductDescription
    price: Price
    category_id: CategoryId
    brand_id: Optional[BrandId] = None
    sku: str = ""
    is_active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __hash__(self) -> int:
        return hash(self.id)

    def update_price(self, new_price: Price) -> None:
        """Update product price."""
        self.price = new_price
        self.updated_at = datetime.now(UTC)

    def deactivate(self) -> None:
        """Deactivate product."""
        self.is_active = False
        self.updated_at = datetime.now(UTC)

    def activate(self) -> None:
        """Activate product."""
        self.is_active = True
        self.updated_at = datetime.now(UTC)


@dataclass
class Category(Entity[CategoryId]):
    """Category entity."""

    name: str
    description: Optional[str] = None
    parent_id: Optional[CategoryId] = None
    is_active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __hash__(self) -> int:
        return hash(self.id)

    def add_subcategory(self, subcategory: "Category") -> None:
        """Add subcategory to this category."""
        if subcategory.parent_id != self.id:
            raise ValueError("Subcategory must have this category as parent")

    def deactivate(self) -> None:
        """Deactivate category."""
        self.is_active = False
        self.updated_at = datetime.now(UTC)


@dataclass
class Brand(Entity[BrandId]):
    """Brand entity."""

    name: str
    description: Optional[str] = None
    logo_url: Optional[str] = None
    is_active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __hash__(self) -> int:
        return hash(self.id)

    def deactivate(self) -> None:
        """Deactivate brand."""
        self.is_active = False
        self.updated_at = datetime.now(UTC)
