"""In-memory repository implementations for users domain."""

from typing import Dict, List, Optional

from src.shared.infrastructure.repositories import InMemoryRepository
from src.users.domain.entities import Customer, Seller, User
from src.users.domain.repositories import (
    CustomerRepository,
    SellerRepository,
    UserRepository,
)
from src.users.domain.value_objects import CustomerId, Email, SellerId, UserId


class InMemoryUserRepository(InMemoryRepository[User], UserRepository):
    """In-memory implementation of UserRepository."""

    def __init__(self):
        super().__init__()
        self._users: Dict[str, User] = {}
        self._users_by_email: Dict[str, User] = {}

    async def save(self, user: User) -> User:
        """Save user to in-memory storage."""
        self._users[str(user.id)] = user
        self._users_by_email[user.email.value] = user
        return user

    async def get_by_id(self, user_id: UserId) -> Optional[User]:
        """Get user by ID."""
        return self._users.get(str(user_id))

    async def get_by_email(self, email: Email) -> Optional[User]:
        """Get user by email."""
        return self._users_by_email.get(email.value)

    async def get_all(self) -> List[User]:
        """Get all users."""
        return list(self._users.values())

    async def delete(self, user_id: UserId) -> bool:
        """Delete user by ID."""
        user = self._users.get(str(user_id))
        if user:
            del self._users[str(user_id)]
            del self._users_by_email[user.email.value]
            return True
        return False


class InMemoryCustomerRepository(
    InMemoryRepository[Customer], CustomerRepository
):
    """In-memory implementation of CustomerRepository."""

    def __init__(self):
        super().__init__()
        self._customers: Dict[str, Customer] = {}
        self._customers_by_user_id: Dict[str, Customer] = {}

    async def save(self, customer: Customer) -> Customer:
        """Save customer to in-memory storage."""
        self._customers[str(customer.id)] = customer
        self._customers_by_user_id[str(customer.user_id)] = customer
        return customer

    async def get_by_id(self, customer_id: CustomerId) -> Optional[Customer]:
        """Get customer by ID."""
        return self._customers.get(str(customer_id))

    async def get_by_user_id(self, user_id: UserId) -> Optional[Customer]:
        """Get customer by user ID."""
        return self._customers_by_user_id.get(str(user_id))

    async def get_all(self) -> List[Customer]:
        """Get all customers."""
        return list(self._customers.values())

    async def delete(self, customer_id: CustomerId) -> bool:
        """Delete customer by ID."""
        customer = self._customers.get(str(customer_id))
        if customer:
            del self._customers[str(customer_id)]
            del self._customers_by_user_id[str(customer.user_id)]
            return True
        return False


class InMemorySellerRepository(InMemoryRepository[Seller], SellerRepository):
    """In-memory implementation of SellerRepository."""

    def __init__(self):
        super().__init__()
        self._sellers: Dict[str, Seller] = {}
        self._sellers_by_user_id: Dict[str, Seller] = {}

    async def save(self, seller: Seller) -> Seller:
        """Save seller to in-memory storage."""
        self._sellers[str(seller.id)] = seller
        self._sellers_by_user_id[str(seller.user_id)] = seller
        return seller

    async def get_by_id(self, seller_id: SellerId) -> Optional[Seller]:
        """Get seller by ID."""
        return self._sellers.get(str(seller_id))

    async def get_by_user_id(self, user_id: UserId) -> Optional[Seller]:
        """Get seller by user ID."""
        return self._sellers_by_user_id.get(str(user_id))

    async def get_all(self) -> List[Seller]:
        """Get all sellers."""
        return list(self._sellers.values())

    async def get_verified(self) -> List[Seller]:
        """Get all verified sellers."""
        return [seller for seller in self._sellers.values() if seller.is_verified]

    async def delete(self, seller_id: SellerId) -> bool:
        """Delete seller by ID."""
        seller = self._sellers.get(str(seller_id))
        if seller:
            del self._sellers[str(seller_id)]
            del self._sellers_by_user_id[str(seller.user_id)]
            return True
        return False
