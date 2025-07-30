"""Users API controllers."""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.shared.infrastructure.database import get_db_session
from src.users.application import CustomerService, SellerService, UserService
from src.users.infrastructure.sql_repositories import (
    SQLCustomerRepository,
    SQLSellerRepository,
    SQLUserRepository,
)

# Pydantic models for API
class CreateUserRequest(BaseModel):
    """Request model for creating a user."""
    email: str
    password: str
    first_name: str
    last_name: str
    phone_number: Optional[str] = None

class UserResponse(BaseModel):
    """Response model for user data."""
    id: str
    email: str
    first_name: str
    last_name: str
    phone_number: Optional[str] = None
    is_active: bool
    created_at: str
    updated_at: str

class UpdateUserRequest(BaseModel):
    """Request model for updating a user."""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None

class CreateCustomerRequest(BaseModel):
    """Request model for creating a customer."""
    user_id: str
    shipping_address: str
    billing_address: str

class CustomerResponse(BaseModel):
    """Response model for customer data."""
    id: str
    user_id: str
    shipping_address: str
    billing_address: str
    created_at: str
    updated_at: str

class CreateSellerRequest(BaseModel):
    """Request model for creating a seller."""
    user_id: str
    company_name: str
    company_description: Optional[str] = None
    website: Optional[str] = None

class SellerResponse(BaseModel):
    """Response model for seller data."""
    id: str
    user_id: str
    company_name: str
    company_description: Optional[str] = None
    website: Optional[str] = None
    is_verified: bool
    created_at: str
    updated_at: str

# Dependency injection
def get_user_service(session: AsyncSession = Depends(get_db_session)) -> UserService:
    """Get user service instance."""
    user_repo = SQLUserRepository(session)
    return UserService(user_repo)

def get_customer_service(session: AsyncSession = Depends(get_db_session)) -> CustomerService:
    """Get customer service instance."""
    customer_repo = SQLCustomerRepository(session)
    return CustomerService(customer_repo)

def get_seller_service(session: AsyncSession = Depends(get_db_session)) -> SellerService:
    """Get seller service instance."""
    seller_repo = SQLSellerRepository(session)
    return SellerService(seller_repo)

# Router
router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    request: CreateUserRequest,
    service: UserService = Depends(get_user_service)
) -> UserResponse:
    """Create a new user."""
    try:
        # In a real application, you would hash the password here
        user = await service.create_user(
            email=request.email,
            password_hash=request.password,  # This should be hashed
            first_name=request.first_name,
            last_name=request.last_name,
            phone_number=request.phone_number,
        )
        
        return UserResponse(
            id=user.id.value,
            email=user.email.value,
            first_name=user.first_name,
            last_name=user.last_name,
            phone_number=user.phone_number.value if user.phone_number else None,
            is_active=user.is_active,
            created_at=user.created_at.isoformat(),
            updated_at=user.updated_at.isoformat(),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    service: UserService = Depends(get_user_service)
) -> UserResponse:
    """Get user by ID."""
    try:
        user = await service.get_user(user_id)
        return UserResponse(
            id=user.id.value,
            email=user.email.value,
            first_name=user.first_name,
            last_name=user.last_name,
            phone_number=user.phone_number.value if user.phone_number else None,
            is_active=user.is_active,
            created_at=user.created_at.isoformat(),
            updated_at=user.updated_at.isoformat(),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.get("/", response_model=List[UserResponse])
async def get_all_users(
    service: UserService = Depends(get_user_service)
) -> List[UserResponse]:
    """Get all users."""
    try:
        users = await service.get_all_users()
        return [
            UserResponse(
                id=user.id.value,
                email=user.email.value,
                first_name=user.first_name,
                last_name=user.last_name,
                phone_number=user.phone_number.value if user.phone_number else None,
                is_active=user.is_active,
                created_at=user.created_at.isoformat(),
                updated_at=user.updated_at.isoformat(),
            )
            for user in users
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    request: UpdateUserRequest,
    service: UserService = Depends(get_user_service)
) -> UserResponse:
    """Update user information."""
    try:
        user = await service.update_user(
            user_id=user_id,
            first_name=request.first_name,
            last_name=request.last_name,
            phone_number=request.phone_number,
        )
        
        return UserResponse(
            id=user.id.value,
            email=user.email.value,
            first_name=user.first_name,
            last_name=user.last_name,
            phone_number=user.phone_number.value if user.phone_number else None,
            is_active=user.is_active,
            created_at=user.created_at.isoformat(),
            updated_at=user.updated_at.isoformat(),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.delete("/{user_id}")
async def delete_user(
    user_id: str,
    service: UserService = Depends(get_user_service)
):
    """Delete user."""
    try:
        success = await service.delete_user(user_id)
        if success:
            return {"message": "User deleted successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

# Customer endpoints
@router.post("/customers", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
async def create_customer(
    request: CreateCustomerRequest,
    service: CustomerService = Depends(get_customer_service)
) -> CustomerResponse:
    """Create a new customer."""
    try:
        customer = await service.create_customer(
            user_id=request.user_id,
            shipping_address=request.shipping_address,
            billing_address=request.billing_address,
        )
        
        return CustomerResponse(
            id=customer.id.value,
            user_id=customer.user_id.value,
            shipping_address=customer.shipping_address,
            billing_address=customer.billing_address,
            created_at=customer.created_at.isoformat(),
            updated_at=customer.updated_at.isoformat(),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/customers/{customer_id}", response_model=CustomerResponse)
async def get_customer(
    customer_id: str,
    service: CustomerService = Depends(get_customer_service)
) -> CustomerResponse:
    """Get customer by ID."""
    try:
        customer = await service.get_customer(customer_id)
        return CustomerResponse(
            id=customer.id.value,
            user_id=customer.user_id.value,
            shipping_address=customer.shipping_address,
            billing_address=customer.billing_address,
            created_at=customer.created_at.isoformat(),
            updated_at=customer.updated_at.isoformat(),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.get("/customers", response_model=List[CustomerResponse])
async def get_all_customers(
    service: CustomerService = Depends(get_customer_service)
) -> List[CustomerResponse]:
    """Get all customers."""
    try:
        customers = await service.get_all_customers()
        return [
            CustomerResponse(
                id=customer.id.value,
                user_id=customer.user_id.value,
                shipping_address=customer.shipping_address,
                billing_address=customer.billing_address,
                created_at=customer.created_at.isoformat(),
                updated_at=customer.updated_at.isoformat(),
            )
            for customer in customers
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

# Seller endpoints
@router.post("/sellers", response_model=SellerResponse, status_code=status.HTTP_201_CREATED)
async def create_seller(
    request: CreateSellerRequest,
    service: SellerService = Depends(get_seller_service)
) -> SellerResponse:
    """Create a new seller."""
    try:
        seller = await service.create_seller(
            user_id=request.user_id,
            company_name=request.company_name,
            company_description=request.company_description,
            website=request.website,
        )
        
        return SellerResponse(
            id=seller.id.value,
            user_id=seller.user_id.value,
            company_name=seller.company_name,
            company_description=seller.company_description,
            website=seller.website,
            is_verified=seller.is_verified,
            created_at=seller.created_at.isoformat(),
            updated_at=seller.updated_at.isoformat(),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/sellers/{seller_id}", response_model=SellerResponse)
async def get_seller(
    seller_id: str,
    service: SellerService = Depends(get_seller_service)
) -> SellerResponse:
    """Get seller by ID."""
    try:
        seller = await service.get_seller(seller_id)
        return SellerResponse(
            id=seller.id.value,
            user_id=seller.user_id.value,
            company_name=seller.company_name,
            company_description=seller.company_description,
            website=seller.website,
            is_verified=seller.is_verified,
            created_at=seller.created_at.isoformat(),
            updated_at=seller.updated_at.isoformat(),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.get("/sellers", response_model=List[SellerResponse])
async def get_all_sellers(
    service: SellerService = Depends(get_seller_service)
) -> List[SellerResponse]:
    """Get all sellers."""
    try:
        sellers = await service.get_all_sellers()
        return [
            SellerResponse(
                id=seller.id.value,
                user_id=seller.user_id.value,
                company_name=seller.company_name,
                company_description=seller.company_description,
                website=seller.website,
                is_verified=seller.is_verified,
                created_at=seller.created_at.isoformat(),
                updated_at=seller.updated_at.isoformat(),
            )
            for seller in sellers
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/sellers/verified", response_model=List[SellerResponse])
async def get_verified_sellers(
    service: SellerService = Depends(get_seller_service)
) -> List[SellerResponse]:
    """Get all verified sellers."""
    try:
        sellers = await service.get_verified_sellers()
        return [
            SellerResponse(
                id=seller.id.value,
                user_id=seller.user_id.value,
                company_name=seller.company_name,
                company_description=seller.company_description,
                website=seller.website,
                is_verified=seller.is_verified,
                created_at=seller.created_at.isoformat(),
                updated_at=seller.updated_at.isoformat(),
            )
            for seller in sellers
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/sellers/{seller_id}/verify", response_model=SellerResponse)
async def verify_seller(
    seller_id: str,
    service: SellerService = Depends(get_seller_service)
) -> SellerResponse:
    """Verify a seller."""
    try:
        seller = await service.verify_seller(seller_id)
        return SellerResponse(
            id=seller.id.value,
            user_id=seller.user_id.value,
            company_name=seller.company_name,
            company_description=seller.company_description,
            website=seller.website,
            is_verified=seller.is_verified,
            created_at=seller.created_at.isoformat(),
            updated_at=seller.updated_at.isoformat(),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
