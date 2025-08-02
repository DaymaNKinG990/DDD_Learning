"""In-memory repository implementations for users domain."""

# Python imports
from typing import Dict, List, Optional

# Local imports
from src.shared.infrastructure.repositories import InMemoryRepository
from src.users.domain.entities import Customer, Seller, User
from src.users.domain.repositories import (
    CustomerRepository,
    SellerRepository,
    UserRepository,
)
from src.users.domain.value_objects import CustomerId, Email, SellerId, UserId


class InMemoryUserRepository(InMemoryRepository[User], UserRepository):
    """
    In-memory implementation of UserRepository.
    
    Attributes:
        _users: A dictionary of users.
        _users_by_email: A dictionary of users by email.
    """

    def __init__(self) -> None:
        """Initialize the in-memory user repository."""
        super().__init__()
        self._users: Dict[str, User] = {}
        self._users_by_email: Dict[str, User] = {}

    async def save(self, user: User) -> User:
        """
        Save user to in-memory storage.
        
        Args:
            user: The user to save.

        Returns:
            User: The saved user.
        """
        self._users[str(user.id)] = user
        self._users_by_email[user.email.value] = user
        return user

    async def get_by_id(self, user_id: UserId) -> Optional[User]:
        """
        Get user by ID.
        
        Args:
            user_id: The ID of the user.

        Returns:
            Optional[User]: The user.
        """
        return self._users.get(str(user_id))

    async def get_by_email(self, email: Email) -> Optional[User]:
        """
        Get user by email.
        
        Args:
            email: The email of the user.

        Returns:
            Optional[User]: The user.
        """
        return self._users_by_email.get(email.value)

    async def get_all(self) -> List[User]:
        """
        Get all users.
        
        Returns:
            List[User]: The users.
        """
        return list(self._users.values())

    async def delete(self, user_id: UserId) -> bool:
        """
        Delete user by ID.
        
        Args:
            user_id: The ID of the user.

        Returns:
            bool: True if the user was deleted, False otherwise.
        """
        user = self._users.get(str(user_id))
        if user:
            del self._users[str(user_id)]
            del self._users_by_email[user.email.value]
            return True
        return False


class InMemoryCustomerRepository(InMemoryRepository[Customer], CustomerRepository):
    """
    In-memory implementation of CustomerRepository.
    
    Attributes:
        _customers: A dictionary of customers.
        _customers_by_user_id: A dictionary of customers by user ID.
    """

    def __init__(self) -> None:
        """Initialize the in-memory customer repository."""
        super().__init__()
        self._customers: Dict[str, Customer] = {}
        self._customers_by_user_id: Dict[str, Customer] = {}

    async def save(self, customer: Customer) -> Customer:
        """
        Save customer to in-memory storage.
        
        Args:
            customer: The customer to save.

        Returns:
            Customer: The saved customer.
        """
        self._customers[str(customer.id)] = customer
        self._customers_by_user_id[str(customer.user_id)] = customer
        return customer

    async def get_by_id(self, customer_id: CustomerId) -> Optional[Customer]:
        """
        Get customer by ID.
        
        Args:
            customer_id: The ID of the customer.

        Returns:
            Optional[Customer]: The customer.
        """
        return self._customers.get(str(customer_id))

    async def get_by_user_id(self, user_id: UserId) -> Optional[Customer]:
        """
        Get customer by user ID.
        
        Args:
            user_id: The ID of the user.

        Returns:
            Optional[Customer]: The customer.
        """
        return self._customers_by_user_id.get(str(user_id))

    async def get_all(self) -> List[Customer]:
        """
        Get all customers.
        
        Returns:
            List[Customer]: The customers.
        """
        return list(self._customers.values())

    async def delete(self, customer_id: CustomerId) -> bool:
        """
        Delete customer by ID.
        
        Args:
            customer_id: The ID of the customer.

        Returns:
            bool: True if the customer was deleted, False otherwise.
        """
        customer = self._customers.get(str(customer_id))
        if customer:
            del self._customers[str(customer_id)]
            del self._customers_by_user_id[str(customer.user_id)]
            return True
        return False


class InMemorySellerRepository(InMemoryRepository[Seller], SellerRepository):
    """
    In-memory implementation of SellerRepository.
    
    Attributes:
        _sellers: A dictionary of sellers.
        _sellers_by_user_id: A dictionary of sellers by user ID.
    """

    def __init__(self) -> None:
        """Initialize the in-memory seller repository."""
        super().__init__()
        self._sellers: Dict[str, Seller] = {}
        self._sellers_by_user_id: Dict[str, Seller] = {}

    async def save(self, seller: Seller) -> Seller:
        """
        Save seller to in-memory storage.
        
        Args:
            seller: The seller to save.

        Returns:
            Seller: The saved seller.
        """
        self._sellers[str(seller.id)] = seller
        self._sellers_by_user_id[str(seller.user_id)] = seller
        return seller

    async def get_by_id(self, seller_id: SellerId) -> Optional[Seller]:
        """
        Get seller by ID.
        
        Args:
            seller_id: The ID of the seller.

        Returns:
            Optional[Seller]: The seller.
        """
        return self._sellers.get(str(seller_id))

    async def get_by_user_id(self, user_id: UserId) -> Optional[Seller]:
        """
        Get seller by user ID.
        
        Args:
            user_id: The ID of the user.

        Returns:
            Optional[Seller]: The seller.
        """
        return self._sellers_by_user_id.get(str(user_id))

    async def get_all(self) -> List[Seller]:
        """
        Get all sellers.
        
        Returns:
            List[Seller]: The sellers.
        """
        return list(self._sellers.values())

    async def get_verified(self) -> List[Seller]:
        """
        Get all verified sellers.
        
        Returns:
            List[Seller]: The verified sellers.
        """
        return [seller for seller in self._sellers.values() if seller.is_verified]

    async def delete(self, seller_id: SellerId) -> bool:
        """
        Delete seller by ID.
        
        Args:
            seller_id: The ID of the seller.

        Returns:
            bool: True if the seller was deleted, False otherwise.
        """
        seller = self._sellers.get(str(seller_id))
        if seller:
            del self._sellers[str(seller_id)]
            del self._sellers_by_user_id[str(seller.user_id)]
            return True
        return False
