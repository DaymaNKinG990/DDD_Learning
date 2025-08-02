"""Application services for users domain."""

# Python imports
from typing import List, Optional

# Local imports
from src.shared.domain.exceptions import EntityNotFoundError, BusinessRuleViolationError
from src.users.domain.entities import Customer, Seller, User
from src.users.domain.repositories import (
    CustomerRepository,
    SellerRepository,
    UserRepository,
)
from src.users.domain.value_objects import (
    CustomerId,
    Email,
    PhoneNumber,
    SellerId,
    UserId,
)


class UserService:
    """
    Application service for User entity.
    
    Attributes:
        user_repository: The repository for User entity.
    """

    def __init__(self, user_repository: UserRepository) -> None:
        """Initialize the UserService."""
        self.user_repository = user_repository

    async def create_user(
        self,
        email: str,
        password_hash: str,
        first_name: str,
        last_name: str,
        phone_number: Optional[str] = None,
    ) -> User:
        """
        Create a new user.
        
        Args:
            email: The email of the user.
            password_hash: The hash of the user's password.
            first_name: The first name of the user.
            last_name: The last name of the user.
            phone_number: The phone number of the user.

        Returns:
            User: The created user.
        """
        email_vo = Email(value=email)
        phone_vo = PhoneNumber(value=phone_number) if phone_number else None

        # Check if user with this email already exists
        existing_user = await self.user_repository.get_by_email(email_vo)
        if existing_user:
            raise BusinessRuleViolationError("User with this email already exists")

        user = User(
            email=email_vo,
            password_hash=password_hash,
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_vo,
        )

        return await self.user_repository.save(user)

    async def get_user(self, user_id: str) -> User:
        """
        Get user by ID.
        
        Args:
            user_id: The ID of the user.

        Returns:
            User: The user.
        """
        user = await self.user_repository.get_by_id(UserId(value=user_id))
        if not user:
            raise EntityNotFoundError(f"User with ID {user_id} not found")
        return user

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email.
        
        Args:
            email: The email of the user.

        Returns:
            Optional[User]: The user.
        """
        return await self.user_repository.get_by_email(Email(value=email))

    async def get_all_users(self) -> List[User]:
        """
        Get all users.
        
        Returns:
            List[User]: The users.
        """
        return await self.user_repository.get_all()

    async def update_user(
        self,
        user_id: str,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        phone_number: Optional[str] = None,
    ) -> User:
        """
        Update user information.
        
        Args:
            user_id: The ID of the user.
            first_name: The first name of the user.
            last_name: The last name of the user.
            phone_number: The phone number of the user.

        Returns:
            User: The updated user.
        """
        user = await self.get_user(user_id)

        if first_name:
            user.first_name = first_name
        if last_name:
            user.last_name = last_name
        if phone_number:
            user.phone_number = PhoneNumber(value=phone_number)

        return await self.user_repository.save(user)

    async def deactivate_user(self, user_id: str) -> User:
        """
        Deactivate user.
        
        Args:
            user_id: The ID of the user.

        Returns:
            User: The deactivated user.
        """
        user = await self.get_user(user_id)
        user.deactivate()
        return await self.user_repository.save(user)

    async def delete_user(self, user_id: str) -> bool:
        """
        Delete user.
        
        Args:
            user_id: The ID of the user.

        Returns:
            bool: True if the user was deleted, False otherwise.
        """
        return await self.user_repository.delete(UserId(value=user_id))


class CustomerService:
    """
    Application service for Customer entity.
    
    Attributes:
        customer_repository: The repository for Customer entity.
    """

    def __init__(self, customer_repository: CustomerRepository) -> None:
        """Initialize the CustomerService."""
        self.customer_repository = customer_repository

    async def create_customer(
        self,
        user_id: str,
        shipping_address: str,
        billing_address: str,
    ) -> Customer:
        """
        Create a new customer.
        
        Args:
            user_id: The ID of the user.
            shipping_address: The shipping address of the customer.
            billing_address: The billing address of the customer.

        Returns:
            Customer: The created customer.
        """
        customer = Customer(
            user_id=UserId(value=user_id),
            shipping_address=shipping_address,
            billing_address=billing_address,
        )

        return await self.customer_repository.save(customer)

    async def get_customer(self, customer_id: str) -> Customer:
        """
        Get customer by ID.
        
        Args:
            customer_id: The ID of the customer.

        Returns:
            Customer: The customer.
        """
        customer = await self.customer_repository.get_by_id(
            CustomerId(value=customer_id)
        )
        if not customer:
            raise EntityNotFoundError(f"Customer with ID {customer_id} not found")
        return customer

    async def get_customer_by_user_id(self, user_id: str) -> Optional[Customer]:
        """
        Get customer by user ID.
        
        Args:
            user_id: The ID of the user.

        Returns:
            Optional[Customer]: The customer.
        """
        return await self.customer_repository.get_by_user_id(UserId(value=user_id))

    async def get_all_customers(self) -> List[Customer]:
        """
        Get all customers.
        
        Returns:
            List[Customer]: The customers.
        """
        return await self.customer_repository.get_all()

    async def add_shipping_address(self, customer_id: str, address: str) -> Customer:
        """
        Add shipping address to customer.
        
        Args:
            customer_id: The ID of the customer.
            address: The shipping address.

        Returns:
            Customer: The customer with the added shipping address.
        """
        customer = await self.get_customer(customer_id)
        customer.add_shipping_address(address)
        return await self.customer_repository.save(customer)

    async def add_billing_address(self, customer_id: str, address: str) -> Customer:
        """
        Add billing address to customer.
        
        Args:
            customer_id: The ID of the customer.
            address: The billing address.

        Returns:
            Customer: The customer with the added billing address.
        """
        customer = await self.get_customer(customer_id)
        customer.add_billing_address(address)
        return await self.customer_repository.save(customer)

    async def delete_customer(self, customer_id: str) -> bool:
        """
        Delete customer.
        
        Args:
            customer_id: The ID of the customer.
        """
        return await self.customer_repository.delete(CustomerId(value=customer_id))


class SellerService:
    """
    Application service for Seller entity.
    
    Attributes:
        seller_repository: The repository for Seller entity.
    """

    def __init__(self, seller_repository: SellerRepository) -> None:
        """Initialize the SellerService."""
        self.seller_repository = seller_repository

    async def create_seller(
        self,
        user_id: str,
        company_name: str,
        company_description: Optional[str] = None,
        website: Optional[str] = None,
    ) -> Seller:
        """
        Create a new seller.
        
        Args:
            user_id: The ID of the user.
            company_name: The name of the company.
            company_description: The description of the company.
            website: The website of the company.

        Returns:
            Seller: The created seller.
        """
        seller = Seller(
            user_id=UserId(value=user_id),
            company_name=company_name,
            company_description=company_description,
            website=website,
        )

        return await self.seller_repository.save(seller)

    async def get_seller(self, seller_id: str) -> Seller:
        """
        Get seller by ID.
        
        Args:
            seller_id: The ID of the seller.

        Returns:
            Seller: The seller.
        """
        seller = await self.seller_repository.get_by_id(SellerId(value=seller_id))
        if not seller:
            raise EntityNotFoundError(f"Seller with ID {seller_id} not found")
        return seller

    async def get_seller_by_user_id(self, user_id: str) -> Optional[Seller]:
        """
        Get seller by user ID.
        
        Args:
            user_id: The ID of the user.

        Returns:
            Optional[Seller]: The seller.
        """
        return await self.seller_repository.get_by_user_id(UserId(value=user_id))

    async def get_all_sellers(self) -> List[Seller]:
        """
        Get all sellers.
        
        Returns:
            List[Seller]: The sellers.
        """
        return await self.seller_repository.get_all()

    async def get_verified_sellers(self) -> List[Seller]:
        """
        Get all verified sellers.
        
        Returns:
            List[Seller]: The verified sellers.
        """
        return await self.seller_repository.get_verified()

    async def verify_seller(self, seller_id: str) -> Seller:
        """
        Verify seller.
        
        Args:
            seller_id: The ID of the seller.

        Returns:
            Seller: The verified seller.
        """
        seller = await self.get_seller(seller_id)
        seller.verify()
        return await self.seller_repository.save(seller)

    async def unverify_seller(self, seller_id: str) -> Seller:
        """
        Unverify seller.
        
        Args:
            seller_id: The ID of the seller.

        Returns:
            Seller: The unverified seller.
        """
        seller = await self.get_seller(seller_id)
        seller.unverify()
        return await self.seller_repository.save(seller)

    async def delete_seller(self, seller_id: str) -> bool:
        """
        Delete seller.
        
        Args:
            seller_id: The ID of the seller.

        Returns:
            bool: True if the seller was deleted, False otherwise.
        """
        return await self.seller_repository.delete(SellerId(value=seller_id))
