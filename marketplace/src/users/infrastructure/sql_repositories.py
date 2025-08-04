"""SQLAlchemy repository implementations for users domain."""

# Python imports
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# Local imports
from src.shared.infrastructure.sql_repositories import SQLRepository
from src.users.domain.entities import Customer, Seller, User
from src.users.domain.repositories import CustomerRepository, SellerRepository, UserRepository
from src.users.domain.value_objects import CustomerId, Email, SellerId, UserId, Username, PhoneNumber
from src.users.infrastructure.models import CustomerModel, SellerModel, UserModel


class SQLUserRepository(SQLRepository[UserModel], UserRepository):
    """
    SQLAlchemy implementation of UserRepository.
    
    Attributes:
        session: The SQLAlchemy session.
    """
    
    def __init__(self, session: AsyncSession) -> None:
        """Initialize the SQLAlchemy user repository."""
        super().__init__(session, UserModel)
    
    async def save(self, user: User) -> User:
        """
        Save user to database.
        
        Args:
            user: The user to save.

        Returns:
            User: The saved user.
        """
        # Convert domain entity to SQLAlchemy model
        user_model = UserModel(
            id=user.id.value,
            email=user.email.value,
            username=user.username.value,
            password_hash="",  # This should be handled separately in auth service
            first_name=user.first_name,
            last_name=user.last_name,
            phone_number=user.phone_number.value if user.phone_number else None,
            is_active=user.is_active,
        )
        
        saved_model = await super().save(user_model)
        
        # Convert back to domain entity
        return User(
            id=UserId(value=saved_model.id),
            email=Email(value=saved_model.email),
            username=Username(value=saved_model.username),
            first_name=saved_model.first_name,
            last_name=saved_model.last_name,
            phone_number=PhoneNumber(value=saved_model.phone_number) if saved_model.phone_number else None,
            is_active=saved_model.is_active,
        )
    
    async def get_by_id(self, user_id: UserId) -> Optional[User]:
        """
        Get user by ID.
        
        Args:
            user_id: The ID of the user.

        Returns:
            Optional[User]: The user.
        """
        user_model = await super().get_by_id(user_id.value)
        if not user_model:
            return None
        
        return User(
            id=UserId(value=user_model.id),
            email=Email(value=user_model.email),
            username=Username(value=user_model.username),
            first_name=user_model.first_name,
            last_name=user_model.last_name,
            phone_number=PhoneNumber(value=user_model.phone_number) if user_model.phone_number else None,
            is_active=user_model.is_active,
        )
    
    async def get_by_email(self, email: Email) -> Optional[User]:
        """
        Get user by email.
        
        Args:
            email: The email of the user.

        Returns:
            Optional[User]: The user.
        """
        stmt = select(UserModel).where(UserModel.email == email.value)
        result = await self.session.execute(stmt)
        user_model = result.scalar_one_or_none()
        
        if not user_model:
            return None
        
        return User(
            id=UserId(value=user_model.id),
            email=Email(value=user_model.email),
            username=Username(value=user_model.username),
            first_name=user_model.first_name,
            last_name=user_model.last_name,
            phone_number=PhoneNumber(value=user_model.phone_number) if user_model.phone_number else None,
            is_active=user_model.is_active,
        )
    
    async def get_by_username(self, username: Username) -> Optional[User]:
        """
        Get user by username.
        
        Args:
            username: The username of the user.

        Returns:
            Optional[User]: The user.
        """
        stmt = select(UserModel).where(UserModel.username == username.value)
        result = await self.session.execute(stmt)
        user_model = result.scalar_one_or_none()
        
        if not user_model:
            return None
        
        return User(
            id=UserId(value=user_model.id),
            email=Email(value=user_model.email),
            username=Username(value=user_model.username),
            first_name=user_model.first_name,
            last_name=user_model.last_name,
            phone_number=PhoneNumber(value=user_model.phone_number) if user_model.phone_number else None,
            is_active=user_model.is_active,
        )
    
    async def get_active_users(self) -> List[User]:
        """
        Get all active users.
        
        Returns:
            List[User]: The active users.
        """
        stmt = select(UserModel).where(UserModel.is_active == True)
        result = await self.session.execute(stmt)
        user_models = result.scalars().all()
        
        return [
            User(
                id=UserId(value=user_model.id),
                email=Email(value=user_model.email),
                username=Username(value=user_model.username),
                first_name=user_model.first_name,
                last_name=user_model.last_name,
                phone_number=PhoneNumber(value=user_model.phone_number) if user_model.phone_number else None,
                is_active=user_model.is_active,
            )
            for user_model in user_models
        ]
    
    async def get_all(self) -> List[User]:
        """
        Get all users.
        
        Returns:
            List[User]: The users.
        """
        user_models = await super().get_all()
        
        return [
            User(
                id=UserId(value=model.id),
                email=Email(value=model.email),
                username=Username(value=model.username),
                first_name=model.first_name,
                last_name=model.last_name,
                phone_number=PhoneNumber(value=model.phone_number) if model.phone_number else None,
                is_active=model.is_active,
            )
            for model in user_models
        ]
    
    async def delete(self, user_id: UserId) -> bool:
        """
        Delete user by ID.
        
        Args:
            user_id: The ID of the user.

        Returns:
            bool: True if the user was deleted, False otherwise.
        """
        return await super().delete(user_id.value)


class SQLCustomerRepository(SQLRepository[CustomerModel], CustomerRepository):
    """
    SQLAlchemy implementation of CustomerRepository.
    
    Attributes:
        session: The SQLAlchemy session.
    """
    
    def __init__(self, session: AsyncSession) -> None:
        """
        Initialize the SQLAlchemy customer repository.
        
        Args:
            session: The SQLAlchemy session.
        """
        super().__init__(session, CustomerModel)
    
    async def save(self, customer: Customer) -> Customer:
        """
        Save customer to database.
        
        Args:
            customer: The customer to save.

        Returns:
            Customer: The saved customer.
        """
        customer_model = CustomerModel(
            id=customer.id.value,
            user_id=customer.user_id.value,
            shipping_address=",".join(customer.shipping_addresses),
            billing_address=",".join(customer.billing_addresses),
        )
        
        saved_model = await super().save(customer_model)
        
        return Customer(
            id=CustomerId(value=saved_model.id),
            user_id=UserId(value=saved_model.user_id),
            shipping_addresses=saved_model.shipping_address.split(",") if saved_model.shipping_address else [],
            billing_addresses=saved_model.billing_address.split(",") if saved_model.billing_address else [],
        )
    
    async def get_by_id(self, customer_id: CustomerId) -> Optional[Customer]:
        """
        Get customer by ID.
        
        Args:
            customer_id: The ID of the customer.

        Returns:
            Optional[Customer]: The customer.
        """
        customer_model = await super().get_by_id(customer_id.value)
        if not customer_model:
            return None
        
        return Customer(
            id=CustomerId(value=customer_model.id),
            user_id=UserId(value=customer_model.user_id),
            shipping_addresses=customer_model.shipping_address.split(",") if customer_model.shipping_address else [],
            billing_addresses=customer_model.billing_address.split(",") if customer_model.billing_address else [],
        )
    
    async def get_by_user_id(self, user_id: UserId) -> Optional[Customer]:
        """
        Get customer by user ID.
        
        Args:
            user_id: The ID of the user.

        Returns:
            Optional[Customer]: The customer.
        """
        stmt = select(CustomerModel).where(CustomerModel.user_id == user_id.value)
        result = await self.session.execute(stmt)
        customer_model = result.scalar_one_or_none()
        
        if not customer_model:
            return None
        
        return Customer(
            id=CustomerId(value=customer_model.id),
            user_id=UserId(value=customer_model.user_id),
            shipping_addresses=customer_model.shipping_address.split(",") if customer_model.shipping_address else [],
            billing_addresses=customer_model.billing_address.split(",") if customer_model.billing_address else [],
        )
    
    async def get_all(self) -> List[Customer]:
        """
        Get all customers.
        
        Returns:
            List[Customer]: The customers.
        """
        customer_models = await super().get_all()
        
        return [
            Customer(
                id=CustomerId(value=model.id),
                user_id=UserId(value=model.user_id),
                shipping_addresses=model.shipping_address.split(",") if model.shipping_address else [],
                billing_addresses=model.billing_address.split(",") if model.billing_address else [],
            )
            for model in customer_models
        ]
    
    async def delete(self, customer_id: CustomerId) -> bool:
        """
        Delete customer by ID.
        
        Args:
            customer_id: The ID of the customer.

        Returns:
            bool: True if the customer was deleted, False otherwise.
        """
        return await super().delete(customer_id.value)


class SQLSellerRepository(SQLRepository[SellerModel], SellerRepository):
    """
    SQLAlchemy implementation of SellerRepository.
    
    Attributes:
        session: The SQLAlchemy session.
    """
    
    def __init__(self, session: AsyncSession) -> None:
        """
        Initialize the SQLAlchemy seller repository.
        
        Args:
            session: The SQLAlchemy session.
        """
        super().__init__(session, SellerModel)
    
    async def save(self, seller: Seller) -> Seller:
        """
        Save seller to database.
        
        Args:
            seller: The seller to save.

        Returns:
            Seller: The saved seller.
        """
        seller_model = SellerModel(
            id=seller.id.value,
            user_id=seller.user_id.value,
            company_name=seller.company_name,
            business_address=seller.business_address,
            company_description=seller.company_description,
            tax_id=seller.tax_id,
            is_verified=seller.is_verified,
        )
        
        saved_model = await super().save(seller_model)
        
        return Seller(
            id=SellerId(value=saved_model.id),
            user_id=UserId(value=saved_model.user_id),
            company_name=saved_model.company_name,
            business_address=saved_model.business_address,
            company_description=saved_model.company_description,
            tax_id=saved_model.tax_id,
            is_verified=saved_model.is_verified,
        )
    
    async def get_by_id(self, seller_id: SellerId) -> Optional[Seller]:
        """
        Get seller by ID.
        
        Args:
            seller_id: The ID of the seller.

        Returns:
            Optional[Seller]: The seller.
        """
        seller_model = await super().get_by_id(seller_id.value)
        if not seller_model:
            return None
        
        return Seller(
            id=SellerId(value=seller_model.id),
            user_id=UserId(value=seller_model.user_id),
            company_name=seller_model.company_name,
            business_address=seller_model.business_address,
            company_description=seller_model.company_description,
            tax_id=seller_model.tax_id,
            is_verified=seller_model.is_verified,
        )
    
    async def get_by_user_id(self, user_id: UserId) -> Optional[Seller]:
        """
        Get seller by user ID.
        
        Args:
            user_id: The ID of the user.

        Returns:
            Optional[Seller]: The seller.
        """
        stmt = select(SellerModel).where(SellerModel.user_id == user_id.value)
        result = await self.session.execute(stmt)
        seller_model = result.scalar_one_or_none()
        
        if not seller_model:
            return None
        
        return Seller(
            id=SellerId(value=seller_model.id),
            user_id=UserId(value=seller_model.user_id),
            company_name=seller_model.company_name,
            business_address=seller_model.business_address,
            company_description=seller_model.company_description,
            tax_id=seller_model.tax_id,
            is_verified=seller_model.is_verified,
        )
    
    async def get_all(self) -> List[Seller]:
        """
        Get all sellers.
        
        Returns:
            List[Seller]: The sellers.
        """
        seller_models = await super().get_all()
        
        return [
            Seller(
                id=SellerId(value=model.id),
                user_id=UserId(value=model.user_id),
                company_name=model.company_name,
                business_address=model.business_address,
                company_description=model.company_description,
                tax_id=model.tax_id,
                is_verified=model.is_verified,
            )
            for model in seller_models
        ]
    
    async def get_verified(self) -> List[Seller]:
        """
        Get all verified sellers.
        
        Returns:
            List[Seller]: The verified sellers.
        """
        stmt = select(SellerModel).where(SellerModel.is_verified == True)
        result = await self.session.execute(stmt)
        seller_models = result.scalars().all()
        
        return [
            Seller(
                id=SellerId(value=model.id),
                user_id=UserId(value=model.user_id),
                company_name=model.company_name,
                business_address=model.business_address,
                company_description=model.company_description,
                tax_id=model.tax_id,
                is_verified=model.is_verified,
            )
            for model in seller_models
        ]
    
    async def delete(self, seller_id: SellerId) -> bool:
        """
        Delete seller by ID.
        
        Args:
            seller_id: The ID of the seller.

        Returns:
            bool: True if the seller was deleted, False otherwise.
        """
        return await super().delete(seller_id.value) 