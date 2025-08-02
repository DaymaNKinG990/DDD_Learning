"""Repository interfaces for users domain."""

# Python imports
from abc import ABC, abstractmethod
from typing import List, Optional

# Local imports
from src.users.domain.entities import Customer, Seller, User
from src.users.domain.value_objects import CustomerId, Email, SellerId, UserId


class UserRepository(ABC):
    """
    Repository interface for User entity.
    
    Attributes:
        user: The user to save.
    """

    @abstractmethod
    async def save(self, user: User) -> User:
        """
        Save user.
        
        Args:
            user: The user to save.

        Returns:
            User: The saved user.
        """
        pass

    @abstractmethod
    async def get_by_id(self, user_id: UserId) -> Optional[User]:
        """
        Get user by ID.
        
        Args:
            user_id: The ID of the user.

        Returns:
            Optional[User]: The user.
        """
        pass

    @abstractmethod
    async def get_by_email(self, email: Email) -> Optional[User]:
        """
        Get user by email.
        
        Args:
            email: The email of the user.

        Returns:
            Optional[User]: The user.
        """
        pass

    @abstractmethod
    async def get_all(self) -> List[User]:
        """
        Get all users.
        
        Returns:
            List[User]: The users.
        """
        pass

    @abstractmethod
    async def delete(self, user_id: UserId) -> bool:
        """
        Delete user by ID.
        
        Args:
            user_id: The ID of the user.

        Returns:
            bool: True if the user was deleted, False otherwise.
        """
        pass


class CustomerRepository(ABC):
    """
    Repository interface for Customer entity.
    
    Attributes:
        customer: The customer to save.
    """

    @abstractmethod
    async def save(self, customer: Customer) -> Customer:
        """
        Save customer.
        
        Args:
            customer: The customer to save.

        Returns:
            Customer: The saved customer.
        """
        pass

    @abstractmethod
    async def get_by_id(self, customer_id: CustomerId) -> Optional[Customer]:
        """
        Get customer by ID.
        
        Args:
            customer_id: The ID of the customer.

        Returns:
            Optional[Customer]: The customer.
        """
        pass

    @abstractmethod
    async def get_by_user_id(self, user_id: UserId) -> Optional[Customer]:
        """
        Get customer by user ID.
        
        Args:
            user_id: The ID of the user.

        Returns:
            Optional[Customer]: The customer.
        """
        pass

    @abstractmethod
    async def get_all(self) -> List[Customer]:
        """
        Get all customers.
        
        Returns:
            List[Customer]: The customers.
        """
        pass

    @abstractmethod
    async def delete(self, customer_id: CustomerId) -> bool:
        """
        Delete customer by ID.
        
        Args:
            customer_id: The ID of the customer.

        Returns:
            bool: True if the customer was deleted, False otherwise.
        """
        pass


class SellerRepository(ABC):
    """
    Repository interface for Seller entity.
    
    Attributes:
        seller: The seller to save.
    """

    @abstractmethod
    async def save(self, seller: Seller) -> Seller:
        """
        Save seller.
        
        Args:
            seller: The seller to save.

        Returns:
            Seller: The saved seller.
        """
        pass

    @abstractmethod
    async def get_by_id(self, seller_id: SellerId) -> Optional[Seller]:
        """
        Get seller by ID.
        
        Args:
            seller_id: The ID of the seller.

        Returns:
            Optional[Seller]: The seller.
        """
        pass

    @abstractmethod
    async def get_by_user_id(self, user_id: UserId) -> Optional[Seller]:
        """
        Get seller by user ID.
        
        Args:
            user_id: The ID of the user.

        Returns:
            Optional[Seller]: The seller.
        """
        pass

    @abstractmethod
    async def get_all(self) -> List[Seller]:
        """
        Get all sellers.
        
        Returns:
            List[Seller]: The sellers.
        """
        pass

    @abstractmethod
    async def get_verified(self) -> List[Seller]:
        """
        Get all verified sellers.
        
        Returns:
            List[Seller]: The verified sellers.
        """
        pass

    @abstractmethod
    async def delete(self, seller_id: SellerId) -> bool:
        """
        Delete seller by ID.
        
        Args:
            seller_id: The ID of the seller.

        Returns:
            bool: True if the seller was deleted, False otherwise.
        """
        pass
