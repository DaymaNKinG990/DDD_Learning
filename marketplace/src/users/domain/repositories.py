"""Repository interfaces for users domain."""

from abc import ABC, abstractmethod
from typing import List, Optional

from src.users.domain.entities import Customer, Seller, User
from src.users.domain.value_objects import CustomerId, Email, SellerId, UserId


class UserRepository(ABC):
    """Repository interface for User entity."""

    @abstractmethod
    async def save(self, user: User) -> User:
        """Save user."""
        pass

    @abstractmethod
    async def get_by_id(self, user_id: UserId) -> Optional[User]:
        """Get user by ID."""
        pass

    @abstractmethod
    async def get_by_email(self, email: Email) -> Optional[User]:
        """Get user by email."""
        pass

    @abstractmethod
    async def get_all(self) -> List[User]:
        """Get all users."""
        pass

    @abstractmethod
    async def delete(self, user_id: UserId) -> bool:
        """Delete user by ID."""
        pass


class CustomerRepository(ABC):
    """Repository interface for Customer entity."""

    @abstractmethod
    async def save(self, customer: Customer) -> Customer:
        """Save customer."""
        pass

    @abstractmethod
    async def get_by_id(self, customer_id: CustomerId) -> Optional[Customer]:
        """Get customer by ID."""
        pass

    @abstractmethod
    async def get_by_user_id(self, user_id: UserId) -> Optional[Customer]:
        """Get customer by user ID."""
        pass

    @abstractmethod
    async def get_all(self) -> List[Customer]:
        """Get all customers."""
        pass

    @abstractmethod
    async def delete(self, customer_id: CustomerId) -> bool:
        """Delete customer by ID."""
        pass


class SellerRepository(ABC):
    """Repository interface for Seller entity."""

    @abstractmethod
    async def save(self, seller: Seller) -> Seller:
        """Save seller."""
        pass

    @abstractmethod
    async def get_by_id(self, seller_id: SellerId) -> Optional[Seller]:
        """Get seller by ID."""
        pass

    @abstractmethod
    async def get_by_user_id(self, user_id: UserId) -> Optional[Seller]:
        """Get seller by user ID."""
        pass

    @abstractmethod
    async def get_all(self) -> List[Seller]:
        """Get all sellers."""
        pass

    @abstractmethod
    async def get_verified(self) -> List[Seller]:
        """Get all verified sellers."""
        pass

    @abstractmethod
    async def delete(self, seller_id: SellerId) -> bool:
        """Delete seller by ID."""
        pass
