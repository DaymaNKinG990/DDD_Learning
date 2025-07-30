"""Application services for catalog domain."""

from typing import List, Optional

from src.catalog.domain.entities import Brand, Category, Product
from src.catalog.domain.events import (
    BrandCreated,
    CategoryCreated,
    ProductCreated,
    ProductDeactivated,
    ProductPriceUpdated,
)
from src.catalog.domain.repositories import (
    BrandRepository,
    CategoryRepository,
    ProductRepository,
)
from src.catalog.domain.value_objects import (
    BrandId,
    CategoryId,
    Price,
    ProductDescription,
    ProductId,
    ProductName,
)
from src.shared.domain.events import EventBus
from src.shared.domain.exceptions import EntityNotFoundError, BusinessRuleViolationError


class CatalogService:
    """Application service for catalog domain."""

    def __init__(
        self,
        product_repository: ProductRepository,
        category_repository: CategoryRepository,
        brand_repository: BrandRepository,
        event_bus: Optional[EventBus] = None,
    ):
        self.product_repository = product_repository
        self.category_repository = category_repository
        self.brand_repository = brand_repository
        self.event_bus = event_bus

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
        # Validate that category exists
        category = await self.category_repository.get_by_id(category_id)
        if not category:
            raise BusinessRuleViolationError(f"Category with ID {category_id} not found")

        # Validate that brand exists if provided
        if brand_id:
            brand = await self.brand_repository.get_by_id(brand_id)
            if not brand:
                raise BusinessRuleViolationError(f"Brand with ID {brand_id} not found")

        product = Product(
            name=ProductName(value=name),
            description=ProductDescription(value=description),
            price=price,
            category_id=category_id,
            sku=sku,
            brand_id=brand_id,
        )

        saved_product = await self.product_repository.save(product)

        # Publish domain event
        if self.event_bus:
            event = ProductCreated(
                aggregate_id=str(saved_product.id),
                product_id=str(saved_product.id),
                name=saved_product.name.value,
                description=saved_product.description.value,
                price=str(saved_product.price),
                category_id=str(saved_product.category_id),
                brand_id=(
                    str(saved_product.brand_id) if saved_product.brand_id else None
                ),
                sku=saved_product.sku,
            )
            await self.event_bus.publish(event)

        return saved_product

    async def get_product(self, product_id: str) -> Product:
        """Get product by ID."""
        product = await self.product_repository.get_by_id(ProductId(value=product_id))
        if not product:
            raise EntityNotFoundError(f"Product with ID {product_id} not found")
        return product

    async def update_product_price(self, product_id: str, new_price: Price) -> Product:
        """Update product price."""
        product = await self.get_product(product_id)
        old_price = product.price
        product.update_price(new_price)

        saved_product = await self.product_repository.save(product)

        # Publish domain event
        if self.event_bus:
            event = ProductPriceUpdated(
                aggregate_id=str(saved_product.id),
                product_id=str(saved_product.id),
                old_price=str(old_price),
                new_price=str(new_price),
            )
            await self.event_bus.publish(event)

        return saved_product

    async def deactivate_product(
        self, product_id: str, reason: Optional[str] = None
    ) -> Product:
        """Deactivate product."""
        product = await self.get_product(product_id)
        product.deactivate()

        saved_product = await self.product_repository.save(product)

        # Publish domain event
        if self.event_bus:
            event = ProductDeactivated(
                aggregate_id=str(saved_product.id),
                product_id=str(saved_product.id),
                reason=reason,
            )
            await self.event_bus.publish(event)

        return saved_product

    async def create_category(
        self,
        name: str,
        description: Optional[str] = None,
        parent_id: Optional[CategoryId] = None,
    ) -> Category:
        """Create a new category."""
        # Validate that parent category exists if provided
        if parent_id:
            parent_category = await self.category_repository.get_by_id(parent_id)
            if not parent_category:
                raise ValidationError(f"Parent category with ID {parent_id} not found")

        category = Category(
            name=name,
            description=description,
            parent_id=parent_id,
        )

        saved_category = await self.category_repository.save(category)

        # Publish domain event
        if self.event_bus:
            event = CategoryCreated(
                aggregate_id=str(saved_category.id),
                category_id=str(saved_category.id),
                name=saved_category.name.value,
                description=(
                    saved_category.description.value 
                    if saved_category.description else None
                ),
                parent_id=(
                    str(saved_category.parent_id) if saved_category.parent_id else None
                ),
            )
            await self.event_bus.publish(event)

        return saved_category

    async def get_category(self, category_id: str) -> Category:
        """Get category by ID."""
        category = await self.category_repository.get_by_id(
            CategoryId(value=category_id)
        )
        if not category:
            raise EntityNotFoundError(f"Category with ID {category_id} not found")
        return category

    async def create_brand(
        self,
        name: str,
        description: Optional[str] = None,
        logo_url: Optional[str] = None,
    ) -> Brand:
        """Create a new brand."""
        brand = Brand(
            name=name,
            description=description,
            logo_url=logo_url,
        )

        saved_brand = await self.brand_repository.save(brand)

        # Publish domain event
        if self.event_bus:
            event = BrandCreated(
                aggregate_id=str(saved_brand.id),
                brand_id=str(saved_brand.id),
                name=saved_brand.name.value,
                description=(
                    saved_brand.description.value if saved_brand.description else None
                ),
                logo_url=saved_brand.logo_url,
            )
            await self.event_bus.publish(event)

        return saved_brand

    async def get_brand(self, brand_id: str) -> Brand:
        """Get brand by ID."""
        brand = await self.brand_repository.get_by_id(BrandId(value=brand_id))
        if not brand:
            raise EntityNotFoundError(f"Brand with ID {brand_id} not found")
        return brand

    async def get_products_by_category(self, category_id: str) -> List[Product]:
        """Get products by category."""
        return await self.product_repository.get_by_category(
            CategoryId(value=category_id)
        )

    async def get_products_by_brand(self, brand_id: str) -> List[Product]:
        """Get products by brand."""
        return await self.product_repository.get_by_brand(BrandId(value=brand_id))
