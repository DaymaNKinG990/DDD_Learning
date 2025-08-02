"""Infrastructure layer for users domain."""

# Local imports
from .models import CustomerModel, SellerModel, UserModel
from .repositories import (
    InMemoryCustomerRepository,
    InMemorySellerRepository,
    InMemoryUserRepository,
)
from .sql_repositories import (
    SQLCustomerRepository,
    SQLSellerRepository,
    SQLUserRepository,
)

__all__ = [
    # Models
    "UserModel",
    "CustomerModel",
    "SellerModel",
    # In-Memory repositories
    "InMemoryUserRepository",
    "InMemoryCustomerRepository",
    "InMemorySellerRepository",
    # SQL repositories
    "SQLUserRepository",
    "SQLCustomerRepository",
    "SQLSellerRepository",
]
