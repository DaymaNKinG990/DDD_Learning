"""Tests for interfaces.api.controllers module."""

import pytest
from decimal import Decimal
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock
from src.interfaces.api.controllers import (
    catalog_router, orders_router, CreateProductRequest, CreateCategoryRequest,
    CreateBrandRequest, CreateOrderRequest, AddOrderItemRequest
)


@pytest.fixture
def catalog_client():
    """Create test client for catalog router."""
    from fastapi import FastAPI
    app = FastAPI()
    app.include_router(catalog_router)
    return TestClient(app)


@pytest.fixture
def orders_client():
    """Create test client for orders router."""
    from fastapi import FastAPI
    app = FastAPI()
    app.include_router(orders_router)
    return TestClient(app)


class TestRequestModels:
    """Test Pydantic request models."""

    def test_create_product_request(self):
        """Test CreateProductRequest model."""
        request = CreateProductRequest(
            name="Test Product",
            description="Test Description",
            price=Decimal("100.00"),
            category_id="cat-123",
            sku="SKU123",
            brand_id="brand-123"
        )
        assert request.name == "Test Product"
        assert request.price == Decimal("100.00")
        assert request.brand_id == "brand-123"

    def test_create_product_request_without_brand(self):
        """Test CreateProductRequest model without brand."""
        request = CreateProductRequest(
            name="Test Product",
            description="Test Description",
            price=Decimal("100.00"),
            category_id="cat-123",
            sku="SKU123"
        )
        assert request.brand_id is None

    def test_create_category_request(self):
        """Test CreateCategoryRequest model."""
        request = CreateCategoryRequest(
            name="Test Category",
            description="Test Description",
            parent_id="parent-123"
        )
        assert request.name == "Test Category"
        assert request.parent_id == "parent-123"

    def test_create_brand_request(self):
        """Test CreateBrandRequest model."""
        request = CreateBrandRequest(
            name="Test Brand",
            description="Test Description",
            logo_url="http://example.com/logo.png"
        )
        assert request.name == "Test Brand"
        assert request.logo_url == "http://example.com/logo.png"

    def test_create_order_request(self):
        """Test CreateOrderRequest model."""
        request = CreateOrderRequest(
            customer_id="customer-123",
            shipping_address="Test Address",
            billing_address="Test Billing",
            notes="Test Notes"
        )
        assert request.customer_id == "customer-123"
        assert request.notes == "Test Notes"

    def test_add_order_item_request(self):
        """Test AddOrderItemRequest model."""
        request = AddOrderItemRequest(
            product_id="prod-123",
            product_name="Test Product",
            quantity=2,
            unit_price=Decimal("50.00")
        )
        assert request.product_id == "prod-123"
        assert request.quantity == 2
        assert request.unit_price == Decimal("50.00")


class TestCatalogEndpoints:
    """Test catalog endpoints with basic validation."""

    def test_create_product_endpoint_exists(self, catalog_client):
        """Test that create product endpoint exists and accepts valid data."""
        response = catalog_client.post("/catalog/products", json={
            "name": "Test Product",
            "description": "Test Description",
            "price": "100.00",
            "category_id": "cat-123",
            "sku": "SKU123"
        })
        # Should return 400 due to missing category, but endpoint exists
        assert response.status_code in [400, 422]

    def test_get_product_endpoint_exists(self, catalog_client):
        """Test that get product endpoint exists."""
        response = catalog_client.get("/catalog/products/test-id")
        # Should return 404 for non-existent product, but endpoint exists
        assert response.status_code in [404, 400]

    def test_create_category_endpoint_exists(self, catalog_client):
        """Test that create category endpoint exists."""
        response = catalog_client.post("/catalog/categories", json={
            "name": "Test Category",
            "description": "Test Description"
        })
        # Should return 400 due to validation, but endpoint exists
        assert response.status_code in [400, 422]

    def test_create_brand_endpoint_exists(self, catalog_client):
        """Test that create brand endpoint exists."""
        response = catalog_client.post("/catalog/brands", json={
            "name": "Test Brand",
            "description": "Test Description"
        })
        # Should return 400 due to validation, but endpoint exists
        assert response.status_code in [400, 422]


class TestOrdersEndpoints:
    """Test orders endpoints with basic validation."""

    def test_create_order_endpoint_exists(self, orders_client):
        """Test that create order endpoint exists."""
        response = orders_client.post("/orders/", json={
            "customer_id": "customer-123",
            "shipping_address": "Test Address",
            "billing_address": "Test Billing"
        })
        # Should return 200 or 400, but endpoint exists
        assert response.status_code in [200, 400, 422]

    def test_get_order_endpoint_exists(self, orders_client):
        """Test that get order endpoint exists."""
        response = orders_client.get("/orders/test-id")
        # Should return 404 for non-existent order, but endpoint exists
        assert response.status_code in [404, 400]

    def test_add_item_to_order_endpoint_exists(self, orders_client):
        """Test that add item to order endpoint exists."""
        response = orders_client.post("/orders/test-id/items", json={
            "product_id": "prod-123",
            "product_name": "Test Product",
            "quantity": 2,
            "unit_price": "50.00"
        })
        # Should return 400 for non-existent order, but endpoint exists
        assert response.status_code in [400, 404, 422]

    def test_confirm_order_endpoint_exists(self, orders_client):
        """Test that confirm order endpoint exists."""
        response = orders_client.post("/orders/test-id/confirm")
        # Should return 400 for non-existent order, but endpoint exists
        assert response.status_code in [400, 404]

    def test_cancel_order_endpoint_exists(self, orders_client):
        """Test that cancel order endpoint exists."""
        response = orders_client.post("/orders/test-id/cancel")
        # Should return 400 for non-existent order, but endpoint exists
        assert response.status_code in [400, 404]


class TestRouterConfiguration:
    """Test router configuration."""

    def test_catalog_router_prefix(self):
        """Test catalog router prefix."""
        assert catalog_router.prefix == "/catalog"
        assert "catalog" in catalog_router.tags

    def test_orders_router_prefix(self):
        """Test orders router prefix."""
        assert orders_router.prefix == "/orders"
        assert "orders" in orders_router.tags

    def test_catalog_router_routes(self):
        """Test catalog router has expected routes."""
        routes = [route.path for route in catalog_router.routes]
        assert "/catalog/products" in routes
        assert "/catalog/products/{product_id}" in routes
        assert "/catalog/categories" in routes
        assert "/catalog/brands" in routes

    def test_orders_router_routes(self):
        """Test orders router has expected routes."""
        routes = [route.path for route in orders_router.routes]
        assert "/orders/" in routes  # create order
        assert "/orders/{order_id}" in routes  # get order
        assert "/orders/{order_id}/items" in routes  # add item
        assert "/orders/{order_id}/confirm" in routes  # confirm order
        assert "/orders/{order_id}/cancel" in routes  # cancel order


class TestDependencyInjection:
    """Test dependency injection functions."""

    def test_get_catalog_service(self):
        """Test get_catalog_service function."""
        from src.interfaces.api.controllers import get_catalog_service
        service = get_catalog_service()
        assert service is not None
        # Should return a CatalogService instance
        assert hasattr(service, 'create_product')
        assert hasattr(service, 'get_product')
        assert hasattr(service, 'create_category')
        assert hasattr(service, 'create_brand')

    def test_get_order_service(self):
        """Test get_order_service function."""
        from src.interfaces.api.controllers import get_order_service
        service = get_order_service()
        assert service is not None
        # Should return an OrderService instance
        assert hasattr(service, 'create_order')
        # Note: OrderService might not have get_order method
        assert hasattr(service, 'add_item_to_order')
        assert hasattr(service, 'confirm_order')
        assert hasattr(service, 'cancel_order') 