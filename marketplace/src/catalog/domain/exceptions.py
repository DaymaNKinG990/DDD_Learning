"""Domain exceptions for catalog module."""

from src.shared.domain.exceptions import DomainException


class ProductNotFoundError(DomainException):
    """Raised when a product is not found."""
    pass


class CategoryNotFoundError(DomainException):
    """Raised when a category is not found."""
    pass


class InvalidProductDataError(DomainException):
    """Raised when product data is invalid."""
    pass


class ProductAlreadyExistsError(DomainException):
    """Raised when trying to create a product that already exists."""
    pass


class CategoryAlreadyExistsError(DomainException):
    """Raised when trying to create a category that already exists."""
    pass


class InvalidPriceError(DomainException):
    """Raised when product price is invalid."""
    pass


class InvalidStockError(DomainException):
    """Raised when product stock is invalid."""
    pass


class InvalidCategoryDataError(DomainException):
    """Raised when category data is invalid."""
    pass 