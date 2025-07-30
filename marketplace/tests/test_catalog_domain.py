"""Tests for catalog domain models."""

from decimal import Decimal

import pytest
from src.catalog.domain.entities import Brand, Category, Product
from src.catalog.domain.value_objects import (
    BrandId,
    CategoryId,
    Price,
    ProductDescription,
    ProductId,
    ProductName,
)


class TestProductId:
    """Test ProductId value object."""

    def test_create_product_id(self):
        """Test creating a product ID."""
        product_id = ProductId(value="prod_123")
        assert product_id.value == "prod_123"
        assert str(product_id) == "prod_123"

    def test_product_id_hash(self):
        """Test product ID hash."""
        product_id1 = ProductId(value="prod_123")
        product_id2 = ProductId(value="prod_123")
        product_id3 = ProductId(value="prod_456")

        assert hash(product_id1) == hash(product_id2)
        assert hash(product_id1) != hash(product_id3)


class TestPrice:
    """Test Price value object."""

    def test_create_price(self):
        """Test creating a price."""
        price = Price(amount=Decimal("100.50"), currency="RUB")
        assert price.amount == Decimal("100.50")
        assert price.currency == "RUB"

    def test_price_validation_negative_amount(self):
        """Test price validation with negative amount."""
        with pytest.raises(ValueError, match="Price cannot be negative"):
            Price(amount=Decimal("-10"), currency="RUB")

    def test_price_validation_invalid_currency(self):
        """Test price validation with invalid currency."""
        with pytest.raises(ValueError, match="Currency must be a 3-letter code"):
            Price(amount=Decimal("100"), currency="RU")

    def test_price_addition(self):
        """Test adding two prices."""
        price1 = Price(amount=Decimal("100"), currency="RUB")
        price2 = Price(amount=Decimal("50"), currency="RUB")
        result = price1 + price2

        assert result.amount == Decimal("150")
        assert result.currency == "RUB"

    def test_price_addition_different_currencies(self):
        """Test adding prices with different currencies."""
        price1 = Price(amount=Decimal("100"), currency="RUB")
        price2 = Price(amount=Decimal("50"), currency="USD")

        with pytest.raises(
            ValueError, match="Cannot add prices with different currencies"
        ):
            price1 + price2


class TestProduct:
    """Test Product entity."""

    def test_create_product(self):
        """Test creating a product."""
        product_id = ProductId(value="prod_123")
        name = ProductName(value="Test Product")
        description = ProductDescription(value="Test description")
        price = Price(amount=Decimal("100"), currency="RUB")
        category_id = CategoryId(value="cat_1")

        product = Product(
            id=product_id,
            name=name,
            description=description,
            price=price,
            category_id=category_id,
            sku="SKU123",
        )

        assert product.id == product_id
        assert product.name == name
        assert product.description == description
        assert product.price == price
        assert product.category_id == category_id
        assert product.sku == "SKU123"
        assert product.is_active is True

    def test_update_product_price(self):
        """Test updating product price."""
        product = Product(
            id=ProductId(value="prod_123"),
            name=ProductName(value="Test Product"),
            description=ProductDescription(value="Test description"),
            price=Price(amount=Decimal("100"), currency="RUB"),
            category_id=CategoryId(value="cat_1"),
            sku="SKU123",
        )

        new_price = Price(amount=Decimal("150"), currency="RUB")
        product.update_price(new_price)

        assert product.price == new_price
        assert product.id == ProductId(value="prod_123")
        assert product.name == ProductName(value="Test Product")

    def test_deactivate_product(self):
        """Test deactivating a product."""
        product = Product(
            id=ProductId(value="prod_123"),
            name=ProductName(value="Test Product"),
            description=ProductDescription(value="Test description"),
            price=Price(amount=Decimal("100"), currency="RUB"),
            category_id=CategoryId(value="cat_1"),
            sku="SKU123",
        )

        product.deactivate()

        assert product.is_active is False
        assert product.id == ProductId(value="prod_123")


class TestCategory:
    """Test Category entity."""

    def test_create_category(self):
        """Test creating a category."""
        category_id = CategoryId(value="cat_1")

        category = Category(
            id=category_id,
            name="Electronics",
            description="Electronic devices",
        )

        assert category.id == category_id
        assert category.name == "Electronics"
        assert category.description == "Electronic devices"
        assert category.is_active is True

    def test_deactivate_category(self):
        """Test deactivating a category."""
        category = Category(
            id=CategoryId(value="cat_1"),
            name="Electronics",
            description="Electronic devices",
        )

        category.deactivate()

        assert category.is_active is False
        assert category.id == CategoryId(value="cat_1")


class TestBrand:
    """Test Brand entity."""

    def test_create_brand(self):
        """Test creating a brand."""
        brand_id = BrandId(value="brand_1")

        brand = Brand(
            id=brand_id,
            name="Apple",
            description="Apple Inc.",
            logo_url="https://example.com/apple.png",
        )

        assert brand.id == brand_id
        assert brand.name == "Apple"
        assert brand.description == "Apple Inc."
        assert brand.logo_url == "https://example.com/apple.png"
        assert brand.is_active is True

    def test_deactivate_brand(self):
        """Test deactivating a brand."""
        brand = Brand(
            id=BrandId(value="brand_1"),
            name="Apple",
            description="Apple Inc.",
        )

        brand.deactivate()

        assert brand.is_active is False
        assert brand.id == BrandId(value="brand_1")
