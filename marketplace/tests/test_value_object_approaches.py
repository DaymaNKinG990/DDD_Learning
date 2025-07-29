"""Tests comparing different Value Object approaches."""

import pytest
from decimal import Decimal

from src.shared.domain.value_object_hybrid import (
    DataclassPrice, PydanticPrice, HybridPrice, ValidationError
)


class TestDataclassApproach:
    """Test dataclass-based value objects."""
    
    def test_valid_price_creation(self):
        """Test creating valid price with dataclass approach."""
        price = DataclassPrice(amount=100.0, currency="RUB")
        assert price.amount == 100.0
        assert price.currency == "RUB"
    
    def test_invalid_negative_price(self):
        """Test that negative price raises validation error."""
        with pytest.raises(ValidationError, match="Price cannot be negative"):
            DataclassPrice(amount=-10.0)
    
    def test_invalid_currency_length(self):
        """Test that invalid currency length raises validation error."""
        with pytest.raises(ValidationError, match="Currency must be 3 letters"):
            DataclassPrice(amount=100.0, currency="RU")
    
    def test_equality(self):
        """Test value object equality."""
        price1 = DataclassPrice(amount=100.0, currency="RUB")
        price2 = DataclassPrice(amount=100.0, currency="RUB")
        price3 = DataclassPrice(amount=200.0, currency="RUB")
        
        assert price1 == price2
        assert price1 != price3
    
    def test_hash(self):
        """Test value object hashing."""
        price1 = DataclassPrice(amount=100.0, currency="RUB")
        price2 = DataclassPrice(amount=100.0, currency="RUB")
        
        assert hash(price1) == hash(price2)
    
    def test_to_dict(self):
        """Test conversion to dictionary."""
        price = DataclassPrice(amount=100.0, currency="RUB")
        expected = {"amount": 100.0, "currency": "RUB"}
        assert price.to_dict() == expected


class TestPydanticApproach:
    """Test Pydantic-based value objects."""
    
    def test_valid_price_creation(self):
        """Test creating valid price with Pydantic approach."""
        price = PydanticPrice(amount=100.0, currency="RUB")
        assert price.amount == 100.0
        assert price.currency == "RUB"
    
    def test_invalid_negative_price(self):
        """Test that negative price raises validation error."""
        with pytest.raises(ValueError):
            PydanticPrice(amount=-10.0)
    
    def test_invalid_currency_length(self):
        """Test that invalid currency length raises validation error."""
        with pytest.raises(ValueError):
            PydanticPrice(amount=100.0, currency="RU")
    
    def test_currency_uppercase_conversion(self):
        """Test that currency is converted to uppercase."""
        price = PydanticPrice(amount=100.0, currency="rub")
        assert price.currency == "RUB"
    
    def test_equality(self):
        """Test value object equality."""
        price1 = PydanticPrice(amount=100.0, currency="RUB")
        price2 = PydanticPrice(amount=100.0, currency="RUB")
        price3 = PydanticPrice(amount=200.0, currency="RUB")
        
        assert price1 == price2
        assert price1 != price3
    
    def test_hash(self):
        """Test value object hashing."""
        price1 = PydanticPrice(amount=100.0, currency="RUB")
        price2 = PydanticPrice(amount=100.0, currency="RUB")
        
        assert hash(price1) == hash(price2)
    
    def test_to_dict(self):
        """Test conversion to dictionary."""
        price = PydanticPrice(amount=100.0, currency="RUB")
        expected = {"amount": 100.0, "currency": "RUB"}
        assert price.to_dict() == expected


class TestHybridApproach:
    """Test hybrid approach value objects."""
    
    def test_valid_price_creation(self):
        """Test creating valid price with hybrid approach."""
        price = HybridPrice(amount=100.0, currency="RUB")
        assert price.amount == 100.0
        assert price.currency == "RUB"
    
    def test_invalid_negative_price(self):
        """Test that negative price raises validation error."""
        with pytest.raises(ValueError):
            HybridPrice(amount=-10.0)
    
    def test_unsupported_currency(self):
        """Test that unsupported currency raises business rule error."""
        with pytest.raises(ValidationError, match="Unsupported currency"):
            HybridPrice(amount=100.0, currency="GBP")
    
    def test_currency_uppercase_conversion(self):
        """Test that currency is converted to uppercase."""
        price = HybridPrice(amount=100.0, currency="rub")
        assert price.currency == "RUB"
    
    def test_price_addition_same_currency(self):
        """Test adding prices with same currency."""
        price1 = HybridPrice(amount=100.0, currency="RUB")
        price2 = HybridPrice(amount=50.0, currency="RUB")
        result = price1 + price2
        
        assert result.amount == 150.0
        assert result.currency == "RUB"
    
    def test_price_addition_different_currencies(self):
        """Test that adding prices with different currencies raises error."""
        price1 = HybridPrice(amount=100.0, currency="RUB")
        price2 = HybridPrice(amount=50.0, currency="USD")
        
        with pytest.raises(ValidationError, match="Cannot add prices with different currencies"):
            price1 + price2
    
    def test_equality(self):
        """Test value object equality."""
        price1 = HybridPrice(amount=100.0, currency="RUB")
        price2 = HybridPrice(amount=100.0, currency="RUB")
        price3 = HybridPrice(amount=200.0, currency="RUB")
        
        assert price1 == price2
        assert price1 != price3
    
    def test_hash(self):
        """Test value object hashing."""
        price1 = HybridPrice(amount=100.0, currency="RUB")
        price2 = HybridPrice(amount=100.0, currency="RUB")
        
        assert hash(price1) == hash(price2)
    
    def test_to_dict(self):
        """Test conversion to dictionary."""
        price = HybridPrice(amount=100.0, currency="RUB")
        expected = {"amount": 100.0, "currency": "RUB"}
        assert price.to_dict() == expected


class TestApproachComparison:
    """Compare different approaches."""
    
    def test_immutability(self):
        """Test that all approaches ensure immutability."""
        dataclass_price = DataclassPrice(amount=100.0, currency="RUB")
        pydantic_price = PydanticPrice(amount=100.0, currency="RUB")
        hybrid_price = HybridPrice(amount=100.0, currency="RUB")
        
        # All should be frozen
        assert dataclass_price.__class__.__dataclass_params__.frozen
        assert pydantic_price.model_config.get("frozen")
        assert hybrid_price.model_config.get("frozen")
    
    def test_validation_timing(self):
        """Test when validation occurs in each approach."""
        # Dataclass: validation in __post_init__
        # Pydantic: validation during __init__
        # Hybrid: validation during __init__ + business rules
        
        # All should validate immediately
        with pytest.raises((ValidationError, ValueError)):
            DataclassPrice(amount=-10.0)
        
        with pytest.raises(ValueError):
            PydanticPrice(amount=-10.0)
        
        with pytest.raises(ValueError):
            HybridPrice(amount=-10.0)
    
    def test_serialization(self):
        """Test serialization capabilities."""
        dataclass_price = DataclassPrice(amount=100.0, currency="RUB")
        pydantic_price = PydanticPrice(amount=100.0, currency="RUB")
        hybrid_price = HybridPrice(amount=100.0, currency="RUB")
        
        expected = {"amount": 100.0, "currency": "RUB"}
        
        assert dataclass_price.to_dict() == expected
        assert pydantic_price.to_dict() == expected
        assert hybrid_price.to_dict() == expected
        
        # Pydantic approaches also support model_dump_json()
        assert pydantic_price.model_dump_json() == '{"amount":100.0,"currency":"RUB"}'
        assert hybrid_price.model_dump_json() == '{"amount":100.0,"currency":"RUB"}'