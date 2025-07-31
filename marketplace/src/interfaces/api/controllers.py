"""API controllers for catalog and orders."""

# Python imports
from decimal import Decimal
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

# Local imports
from src.catalog.application import CatalogService
from src.catalog.domain.value_objects import BrandId, CategoryId, Price
from src.catalog.infrastructure import (
    InMemoryBrandRepository,
    InMemoryCategoryRepository,
    InMemoryProductRepository,
)
from src.orders.application import OrderService
from src.orders.infrastructure import (
    InMemoryOrderItemRepository,
    InMemoryOrderRepository,
)


# Pydantic models for API requests/responses
class CreateProductRequest(BaseModel):
    """
    Request model for creating a new product.

    Attributes:
        name (str): The name of the product.
        description (str): The description of the product.
        price (Decimal): The price of the product.  
        category_id (str): The ID of the category.
        sku (str): The stock keeping unit of the product.
        brand_id (Optional[str]): The ID of the brand.
    """

    name: str
    description: str
    price: Decimal
    category_id: str
    sku: str
    brand_id: Optional[str] = None

class CreateCategoryRequest(BaseModel):
    """
    Request model for creating a new category.

    Attributes:
        name (str): The name of the category.
        description (Optional[str]): The description of the category.
        parent_id (Optional[str]): The ID of the parent category.   
    """

    name: str
    description: Optional[str] = None
    parent_id: Optional[str] = None

class CreateBrandRequest(BaseModel):
    """
    Request model for creating a new brand.

    Attributes:
        name (str): The name of the brand.
        description (Optional[str]): The description of the brand.
        logo_url (Optional[str]): The URL of the brand's logo.
    """

    name: str
    description: Optional[str] = None
    logo_url: Optional[str] = None

class CreateOrderRequest(BaseModel):
    """
    Request model for creating a new order.

    Attributes:
        customer_id (str): The ID of the customer.
        shipping_address (str): The shipping address of the order.
        billing_address (str): The billing address of the order.
        notes (Optional[str]): The notes of the order.
    """

    customer_id: str
    shipping_address: str
    billing_address: str
    notes: Optional[str] = None

class AddOrderItemRequest(BaseModel):
    """
    Request model for adding an item to an order.

    Attributes:
        product_id (str): The ID of the product.
        product_name (str): The name of the product.
        quantity (int): The quantity of the product.
        unit_price (Decimal): The unit price of the product.
    """

    product_id: str
    product_name: str
    quantity: int
    unit_price: Decimal


# API Routers
catalog_router = APIRouter(prefix="/catalog", tags=["catalog"])
orders_router = APIRouter(prefix="/orders", tags=["orders"])


# Dependency injection
def get_catalog_service() -> CatalogService:
    """
    Get catalog service instance.

    Returns:
        CatalogService: The catalog service instance.
    """

    return CatalogService(
        product_repository=InMemoryProductRepository(),
        category_repository=InMemoryCategoryRepository(),
        brand_repository=InMemoryBrandRepository(),
    )


def get_order_service() -> OrderService:
    """
    Get order service instance.

    Returns:
        OrderService: The order service instance.
    """

    return OrderService(
        order_repository=InMemoryOrderRepository(),
        order_item_repository=InMemoryOrderItemRepository(),
    )


# Catalog endpoints
@catalog_router.post("/products", response_model=dict)
async def create_product(
    request: CreateProductRequest,
    catalog_service: CatalogService = Depends(get_catalog_service),
) -> dict[str, str | bool]:
    """Create a new product.

    Args:
        request (CreateProductRequest): The request object containing product details.
        catalog_service (CatalogService): The catalog service instance.

    Returns:
        dict[str, str | bool]: The response containing product details.
    """

    try:
        price = Price(amount=request.price, currency="RUB")
        category_id = CategoryId(value=request.category_id)
        brand_id = BrandId(value=request.brand_id) if request.brand_id else None

        product = await catalog_service.create_product(
            name=request.name,
            description=request.description,
            price=price,
            category_id=category_id,
            sku=request.sku,
            brand_id=brand_id,
        )

        return {
            "id": str(product.id),
            "name": product.name.value,
            "description": product.description.value,
            "price": str(product.price),
            "category_id": str(product.category_id),
            "brand_id": str(product.brand_id) if product.brand_id else None,
            "sku": product.sku,
            "is_active": product.is_active,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@catalog_router.get("/products/{product_id}", response_model=dict)
async def get_product(
    product_id: str,
    catalog_service: CatalogService = Depends(get_catalog_service),
) -> dict[str, str | bool]:
    """
    Get product by ID.

    Args:
        product_id (str): The ID of the product.
        catalog_service (CatalogService): The catalog service instance.

    Returns:
        dict[str, str | bool]: The response containing product details.
    """

    try:
        product = await catalog_service.get_product(product_id)
        return {
            "id": str(product.id),
            "name": product.name.value,
            "description": product.description.value,
            "price": str(product.price),
            "category_id": str(product.category_id),
            "brand_id": str(product.brand_id) if product.brand_id else None,
            "sku": product.sku,
            "is_active": product.is_active,
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@catalog_router.post("/categories", response_model=dict)
async def create_category(
    request: CreateCategoryRequest,
    catalog_service: CatalogService = Depends(get_catalog_service),
) -> dict[str, str | bool]:
    """Create a new category.

    Args:
        request (CreateCategoryRequest): The request object containing category details.
        catalog_service (CatalogService): The catalog service instance.

    Returns:
        dict[str, str | bool]: The response containing category details.
    """

    try:
        parent_id = CategoryId(value=request.parent_id) if request.parent_id else None

        category = await catalog_service.create_category(
            name=request.name,
            description=request.description,
            parent_id=parent_id,
        )

        return {
            "id": str(category.id),
            "name": category.name.value,
            "description": category.description.value if category.description else None,
            "parent_id": str(category.parent_id) if category.parent_id else None,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@catalog_router.post("/brands", response_model=dict)
async def create_brand(
    request: CreateBrandRequest,
    catalog_service: CatalogService = Depends(get_catalog_service),
) -> dict[str, str | bool]:
    """Create a new brand.

    Args:
        request (CreateBrandRequest): The request object containing brand details.
        catalog_service (CatalogService): The catalog service instance.

    Returns:
        dict[str, str | bool]: The response containing brand details.
    """

    try:
        brand = await catalog_service.create_brand(
            name=request.name,
            description=request.description,
            logo_url=request.logo_url,
        )

        return {
            "id": str(brand.id),
            "name": brand.name.value,
            "description": brand.description.value if brand.description else None,
            "logo_url": brand.logo_url,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Orders endpoints
@orders_router.post("/", response_model=dict)
async def create_order(
    request: CreateOrderRequest,
    order_service: OrderService = Depends(get_order_service),
) -> dict[str, str | bool]:
    """
    Create a new order.

    Args:
        request (CreateOrderRequest): The request object containing order details.
        order_service (OrderService): The order service instance.

    Returns:
        dict[str, str | bool]: The response containing order details.
    """

    try:
        order = await order_service.create_order(
            customer_id=request.customer_id,
            shipping_address=request.shipping_address,
            billing_address=request.billing_address,
            notes=request.notes,
        )

        return {
            "id": str(order.id),
            "customer_id": order.customer_id,
            "status": order.status.value,
            "total": str(order.total),
            "shipping_address": order.shipping_address,
            "billing_address": order.billing_address,
            "notes": order.notes,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@orders_router.get("/{order_id}", response_model=dict)
async def get_order(
    order_id: str,
    order_service: OrderService = Depends(get_order_service),
) -> dict[str, str | bool]:
    """
    Get order by ID.

    Args:
        order_id (str): The ID of the order.
        order_service (OrderService): The order service instance.

    Returns:
        dict[str, str | bool]: The response containing order details.
    """

    try:
        order = await order_service.get_order(order_id)
        return {
            "id": str(order.id),
            "customer_id": order.customer_id,
            "status": order.status.value,
            "total": str(order.total),
            "shipping_address": order.shipping_address,
            "billing_address": order.billing_address,
            "notes": order.notes,
            "items": [
                {
                    "id": str(item.id),
                    "product_id": str(item.product_id),
                    "product_name": item.product_name,
                    "quantity": item.quantity,
                    "unit_price": str(item.unit_price),
                    "total": str(item.total),
                }
                for item in order.items
            ],
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@orders_router.post("/{order_id}/items", response_model=dict)
async def add_item_to_order(
    order_id: str,
    request: AddOrderItemRequest,
    order_service: OrderService = Depends(get_order_service),
) -> dict[str, str | bool]:
    """
    Add item to order.

    Args:
        order_id (str): The ID of the order.
        request (AddOrderItemRequest): The request object containing item details.
        order_service (OrderService): The order service instance.

    Returns:
        dict[str, str | bool]: The response containing order details.
    """

    try:
        order = await order_service.add_item_to_order(
            order_id=order_id,
            product_id=request.product_id,
            product_name=request.product_name,
            quantity=request.quantity,
            unit_price=request.unit_price,
        )

        return {
            "id": str(order.id),
            "customer_id": order.customer_id,
            "status": order.status.value,
            "total": str(order.total),
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@orders_router.post("/{order_id}/confirm", response_model=dict)
async def confirm_order(
    order_id: str,
    order_service: OrderService = Depends(get_order_service),
) -> dict[str, str | bool]:
    """
    Confirm order.

    Args:
        order_id (str): The ID of the order.
        order_service (OrderService): The order service instance.

    Returns:
        dict[str, str | bool]: The response containing order details.
    """

    try:
        order = await order_service.confirm_order(order_id)
        return {
            "id": str(order.id),
            "status": order.status.value,
            "message": "Order confirmed successfully",
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@orders_router.post("/{order_id}/cancel", response_model=dict)
async def cancel_order(
    order_id: str,
    order_service: OrderService = Depends(get_order_service),
) -> dict[str, str | bool]:
    """
    Cancel order.

    Args:
        order_id (str): The ID of the order.
        order_service (OrderService): The order service instance.

    Returns:
        dict[str, str | bool]: The response containing order details.
    """

    try:
        order = await order_service.cancel_order(order_id)
        return {
            "id": str(order.id),
            "status": order.status.value,
            "message": "Order cancelled successfully",
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
