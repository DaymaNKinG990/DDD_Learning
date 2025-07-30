"""Domain events for catalog bounded context."""

from typing import Any, Dict, Optional

from src.shared.domain.events import DomainEvent


class ProductCreated(DomainEvent):
    """Event raised when a product is created."""

    product_id: str
    name: str
    description: str
    price: str
    category_id: str
    brand_id: Optional[str] = None
    sku: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": str(self.event_id),
            "event_type": self.event_type,
            "aggregate_id": self.aggregate_id,
            "occurred_on": self.occurred_on.isoformat(),
            "version": self.version,
            "product_id": self.product_id,
            "name": self.name,
            "description": self.description,
            "price": self.price,
            "category_id": self.category_id,
            "brand_id": self.brand_id,
            "sku": self.sku,
        }


class ProductPriceUpdated(DomainEvent):
    """Event raised when a product price is updated."""

    product_id: str
    old_price: str
    new_price: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": str(self.event_id),
            "event_type": self.event_type,
            "aggregate_id": self.aggregate_id,
            "occurred_on": self.occurred_on.isoformat(),
            "version": self.version,
            "product_id": self.product_id,
            "old_price": self.old_price,
            "new_price": self.new_price,
        }


class ProductDeactivated(DomainEvent):
    """Event raised when a product is deactivated."""

    product_id: str
    reason: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": str(self.event_id),
            "event_type": self.event_type,
            "aggregate_id": self.aggregate_id,
            "occurred_on": self.occurred_on.isoformat(),
            "version": self.version,
            "product_id": self.product_id,
            "reason": self.reason,
        }


class CategoryCreated(DomainEvent):
    """Event raised when a category is created."""

    category_id: str
    name: str
    description: Optional[str] = None
    parent_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": str(self.event_id),
            "event_type": self.event_type,
            "aggregate_id": self.aggregate_id,
            "occurred_on": self.occurred_on.isoformat(),
            "version": self.version,
            "category_id": self.category_id,
            "name": self.name,
            "description": self.description,
            "parent_id": self.parent_id,
        }


class BrandCreated(DomainEvent):
    """Event raised when a brand is created."""

    brand_id: str
    name: str
    description: Optional[str] = None
    logo_url: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": str(self.event_id),
            "event_type": self.event_type,
            "aggregate_id": self.aggregate_id,
            "occurred_on": self.occurred_on.isoformat(),
            "version": self.version,
            "brand_id": self.brand_id,
            "name": self.name,
            "description": self.description,
            "logo_url": self.logo_url,
        }
