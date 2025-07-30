"""SQLAlchemy repository implementations for users domain."""

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.shared.infrastructure.sql_repositories import SQLRepository
from src.users.domain.entities import Customer, Seller, User
from src.users.domain.repositories import CustomerRepository, SellerRepository, UserRepository
from src.users.domain.value_objects import CustomerId, Email, SellerId, UserId
from src.users.infrastructure.models import CustomerModel, SellerModel, UserModel


class SQLUserRepository(SQLRepository[UserModel], UserRepository):
    """SQLAlchemy implementation of UserRepository."""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, UserModel)
    
    async def save(self, user: User) -> User:
        """Save user to database."""
        # Convert domain entity to SQLAlchemy model
        user_model = UserModel(
            id=user.id.value,
            email=user.email.value,
            password_hash=user.password_hash,
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
            password_hash=saved_model.password_hash,
            first_name=saved_model.first_name,
            last_name=saved_model.last_name,
            phone_number=saved_model.phone_number,
            is_active=saved_model.is_active,
        )
    
    async def get_by_id(self, user_id: UserId) -> Optional[User]:
        """Get user by ID."""
        user_model = await super().get_by_id(user_id.value)
        if not user_model:
            return None
        
        return User(
            id=UserId(value=user_model.id),
            email=Email(value=user_model.email),
            password_hash=user_model.password_hash,
            first_name=user_model.first_name,
            last_name=user_model.last_name,
            phone_number=user_model.phone_number,
            is_active=user_model.is_active,
        )
    
    async def get_by_email(self, email: Email) -> Optional[User]:
        """Get user by email."""
        stmt = select(UserModel).where(UserModel.email == email.value)
        result = await self.session.execute(stmt)
        user_model = result.scalar_one_or_none()
        
        if not user_model:
            return None
        
        return User(
            id=UserId(value=user_model.id),
            email=Email(value=user_model.email),
            password_hash=user_model.password_hash,
            first_name=user_model.first_name,
            last_name=user_model.last_name,
            phone_number=user_model.phone_number,
            is_active=user_model.is_active,
        )
    
    async def get_all(self) -> List[User]:
        """Get all users."""
        user_models = await super().get_all()
        
        return [
            User(
                id=UserId(value=model.id),
                email=Email(value=model.email),
                password_hash=model.password_hash,
                first_name=model.first_name,
                last_name=model.last_name,
                phone_number=model.phone_number,
                is_active=model.is_active,
            )
            for model in user_models
        ]
    
    async def delete(self, user_id: UserId) -> bool:
        """Delete user by ID."""
        return await super().delete(user_id.value)


class SQLCustomerRepository(SQLRepository[CustomerModel], CustomerRepository):
    """SQLAlchemy implementation of CustomerRepository."""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, CustomerModel)
    
    async def save(self, customer: Customer) -> Customer:
        """Save customer to database."""
        customer_model = CustomerModel(
            id=customer.id.value,
            user_id=customer.user_id.value,
            shipping_address=customer.shipping_address,
            billing_address=customer.billing_address,
        )
        
        saved_model = await super().save(customer_model)
        
        return Customer(
            id=CustomerId(value=saved_model.id),
            user_id=UserId(value=saved_model.user_id),
            shipping_address=saved_model.shipping_address,
            billing_address=saved_model.billing_address,
        )
    
    async def get_by_id(self, customer_id: CustomerId) -> Optional[Customer]:
        """Get customer by ID."""
        customer_model = await super().get_by_id(customer_id.value)
        if not customer_model:
            return None
        
        return Customer(
            id=CustomerId(value=customer_model.id),
            user_id=UserId(value=customer_model.user_id),
            shipping_address=customer_model.shipping_address,
            billing_address=customer_model.billing_address,
        )
    
    async def get_by_user_id(self, user_id: UserId) -> Optional[Customer]:
        """Get customer by user ID."""
        stmt = select(CustomerModel).where(CustomerModel.user_id == user_id.value)
        result = await self.session.execute(stmt)
        customer_model = result.scalar_one_or_none()
        
        if not customer_model:
            return None
        
        return Customer(
            id=CustomerId(value=customer_model.id),
            user_id=UserId(value=customer_model.user_id),
            shipping_address=customer_model.shipping_address,
            billing_address=customer_model.billing_address,
        )
    
    async def get_all(self) -> List[Customer]:
        """Get all customers."""
        customer_models = await super().get_all()
        
        return [
            Customer(
                id=CustomerId(value=model.id),
                user_id=UserId(value=model.user_id),
                shipping_address=model.shipping_address,
                billing_address=model.billing_address,
            )
            for model in customer_models
        ]
    
    async def delete(self, customer_id: CustomerId) -> bool:
        """Delete customer by ID."""
        return await super().delete(customer_id.value)


class SQLSellerRepository(SQLRepository[SellerModel], SellerRepository):
    """SQLAlchemy implementation of SellerRepository."""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, SellerModel)
    
    async def save(self, seller: Seller) -> Seller:
        """Save seller to database."""
        seller_model = SellerModel(
            id=seller.id.value,
            user_id=seller.user_id.value,
            company_name=seller.company_name,
            company_description=seller.company_description,
            website=seller.website,
            is_verified=seller.is_verified,
        )
        
        saved_model = await super().save(seller_model)
        
        return Seller(
            id=SellerId(value=saved_model.id),
            user_id=UserId(value=saved_model.user_id),
            company_name=saved_model.company_name,
            company_description=saved_model.company_description,
            website=saved_model.website,
            is_verified=saved_model.is_verified,
        )
    
    async def get_by_id(self, seller_id: SellerId) -> Optional[Seller]:
        """Get seller by ID."""
        seller_model = await super().get_by_id(seller_id.value)
        if not seller_model:
            return None
        
        return Seller(
            id=SellerId(value=seller_model.id),
            user_id=UserId(value=seller_model.user_id),
            company_name=seller_model.company_name,
            company_description=seller_model.company_description,
            website=seller_model.website,
            is_verified=seller_model.is_verified,
        )
    
    async def get_by_user_id(self, user_id: UserId) -> Optional[Seller]:
        """Get seller by user ID."""
        stmt = select(SellerModel).where(SellerModel.user_id == user_id.value)
        result = await self.session.execute(stmt)
        seller_model = result.scalar_one_or_none()
        
        if not seller_model:
            return None
        
        return Seller(
            id=SellerId(value=seller_model.id),
            user_id=UserId(value=seller_model.user_id),
            company_name=seller_model.company_name,
            company_description=seller_model.company_description,
            website=seller_model.website,
            is_verified=seller_model.is_verified,
        )
    
    async def get_all(self) -> List[Seller]:
        """Get all sellers."""
        seller_models = await super().get_all()
        
        return [
            Seller(
                id=SellerId(value=model.id),
                user_id=UserId(value=model.user_id),
                company_name=model.company_name,
                company_description=model.company_description,
                website=model.website,
                is_verified=model.is_verified,
            )
            for model in seller_models
        ]
    
    async def get_verified(self) -> List[Seller]:
        """Get all verified sellers."""
        stmt = select(SellerModel).where(SellerModel.is_verified == True)
        result = await self.session.execute(stmt)
        seller_models = result.scalars().all()
        
        return [
            Seller(
                id=SellerId(value=model.id),
                user_id=UserId(value=model.user_id),
                company_name=model.company_name,
                company_description=model.company_description,
                website=model.website,
                is_verified=model.is_verified,
            )
            for model in seller_models
        ]
    
    async def delete(self, seller_id: SellerId) -> bool:
        """Delete seller by ID."""
        return await super().delete(seller_id.value) 