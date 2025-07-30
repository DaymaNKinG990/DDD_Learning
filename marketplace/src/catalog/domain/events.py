"""Domain events for catalog bounded context."""

# Python imports
from typing import Any, Dict, Optional

# Local imports
from src.shared.domain.events import DomainEvent


class ProductCreated(DomainEvent):
    """Event raised when a product is created.
    
    Attributes:
        product_id: The product ID.
        name: The product name.
        description: The product description.
        price: The product price.
        category_id: The category ID.
        brand_id: The brand ID.
        sku: The product SKU.
    """

    product_id: str
    name: str
    description: str
    price: str
    category_id: str
    brand_id: Optional[str] = None
    sku: str

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the event to a dictionary.
        
        Returns:
            Dict[str, Any]: The event data as a dictionary.
        """
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
    """Event raised when a product price is updated.
    
    Attributes:
        product_id: The product ID.
        old_price: The old price.
        new_price: The new price.
    """

    product_id: str
    old_price: str
    new_price: str

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the event to a dictionary.
        
        Returns:
            Dict[str, Any]: The event data as a dictionary.
        """
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
    """Event raised when a product is deactivated.
    
    Attributes:
        product_id: The product ID.
        reason: The reason for deactivation.
    """

    product_id: str
    reason: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the event to a dictionary.
        
        Returns:
            Dict[str, Any]: The event data as a dictionary.
        """
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
    """Event raised when a category is created.
    
    Attributes:
        category_id: The category ID.
        name: The category name.
        description: The category description.
        parent_id: The parent category ID.
    """

    category_id: str
    name: str
    description: Optional[str] = None
    parent_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the event to a dictionary.
        
        Returns:
            Dict[str, Any]: The event data as a dictionary.
        """
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
    """Event raised when a brand is created.
    
    Attributes:
        brand_id: The brand ID.
        name: The brand name.
        description: The brand description.
        logo_url: The brand logo URL.
    """

    brand_id: str
    name: str
    description: Optional[str] = None
    logo_url: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the event to a dictionary.
        
        Returns:
            Dict[str, Any]: The event data as a dictionary.
        """
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
