"""Tests for users infrastructure SQL repositories."""

# Python imports
import pytest
from unittest.mock import AsyncMock, Mock, patch
from datetime import datetime, timezone
from typing import List

# Local imports
from src.users.infrastructure.sql_repositories import (
    SQLUserRepository,
    SQLCustomerRepository,
    SQLSellerRepository
)
from src.users.domain.entities import User, Customer, Seller
from src.users.domain.value_objects import UserId, Email, CustomerId, SellerId, PhoneNumber, Username
from src.users.infrastructure.models import UserModel, CustomerModel, SellerModel
from src.shared.infrastructure.sql_repositories import SQLRepository


class TestSQLUserRepository:
    """Test cases for SQLUserRepository."""

    @pytest.fixture
    def mock_session(self):
        """Create mock SQLAlchemy session."""
        return AsyncMock()

    @pytest.fixture
    def repository(self, mock_session):
        """Create SQLUserRepository instance."""
        return SQLUserRepository(mock_session)

    @pytest.fixture
    def user(self):
        """Create test user."""
        return User(
            id=UserId("user-123"),
            email=Email("test@example.com"),
            username=Username("testuser"),
            first_name="John",
            last_name="Doe",
            phone_number=PhoneNumber("+1234567890"),
            is_active=True
        )

    @pytest.fixture
    def user_model(self):
        """Create test user model."""
        return UserModel(
            id="user-123",
            email="test@example.com",
            username="testuser",
            password_hash="hashed_password",
            first_name="John",
            last_name="Doe",
            phone_number="+1234567890",
            is_active=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

    @pytest.mark.asyncio
    async def test_save_user(self, repository, user):
        """Test saving user."""
        # Create a mock UserModel that will be returned by the base class save method
        mock_user_model = UserModel(
            id="user-123",
            email="test@example.com",
            username="testuser",
            password_hash="",
            first_name="John",
            last_name="Doe",
            phone_number="+1234567890",
            is_active=True
        )
        
        with patch.object(SQLRepository, 'save', return_value=mock_user_model):
            result = await repository.save(user)
            
            assert result.id.value == "user-123"
            assert result.email.value == "test@example.com"
            assert result.username.value == "testuser"
            assert result.first_name == "John"
            assert result.last_name == "Doe"
            assert result.phone_number.value == "1234567890"
            assert result.is_active is True

    @pytest.mark.asyncio
    async def test_get_by_id_found(self, repository):
        """Test getting user by ID when found."""
        mock_user_model = UserModel(
            id="user-123",
            email="test@example.com",
            username="testuser",
            password_hash="",
            first_name="John",
            last_name="Doe",
            phone_number="+1234567890",
            is_active=True
        )
        
        with patch.object(SQLRepository, 'get_by_id', return_value=mock_user_model):
            result = await repository.get_by_id(UserId("user-123"))
            
            assert result is not None
            assert result.id.value == "user-123"
            assert result.email.value == "test@example.com"

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, repository):
        """Test getting user by ID when not found."""
        with patch.object(repository, 'get_by_id', return_value=None):
            result = await repository.get_by_id(UserId("user-123"))
            
            assert result is None

    @pytest.mark.asyncio
    async def test_get_by_email_found(self, repository, user_model):
        """Test getting user by email when found."""
        with patch.object(repository.session, 'execute') as mock_execute:
            mock_result = Mock()
            mock_result.scalar_one_or_none.return_value = user_model
            mock_execute.return_value = mock_result
            
            result = await repository.get_by_email(Email("test@example.com"))
            
            assert result is not None
            assert result.email.value == "test@example.com"

    @pytest.mark.asyncio
    async def test_get_by_email_not_found(self, repository):
        """Test getting user by email when not found."""
        with patch.object(repository.session, 'execute') as mock_execute:
            mock_result = Mock()
            mock_result.scalar_one_or_none.return_value = None
            mock_execute.return_value = mock_result
            
            result = await repository.get_by_email(Email("test@example.com"))
            
            assert result is None

    @pytest.mark.asyncio
    async def test_get_all(self, repository, user_model):
        """Test getting all users."""
        with patch.object(repository.session, 'execute') as mock_execute:
            mock_result = Mock()
            mock_result.scalars.return_value.all.return_value = [user_model]
            mock_execute.return_value = mock_result
            
            result = await repository.get_all()
            
            assert len(result) == 1
            assert result[0].id.value == "user-123"

    @pytest.mark.asyncio
    async def test_delete_success(self, repository):
        """Test deleting user successfully."""
        with patch.object(repository, 'delete', return_value=True):
            result = await repository.delete(UserId("user-123"))
            
            assert result is True

    @pytest.mark.asyncio
    async def test_delete_not_found(self, repository):
        """Test deleting user when not found."""
        with patch.object(repository, 'delete', return_value=False):
            result = await repository.delete(UserId("user-123"))
            
            assert result is False


class TestSQLCustomerRepository:
    """Test cases for SQLCustomerRepository."""

    @pytest.fixture
    def mock_session(self):
        """Create mock SQLAlchemy session."""
        return AsyncMock()

    @pytest.fixture
    def repository(self, mock_session):
        """Create SQLCustomerRepository instance."""
        return SQLCustomerRepository(mock_session)

    @pytest.fixture
    def customer(self):
        """Create test customer."""
        return Customer(
            id=CustomerId("customer-123"),
            user_id=UserId("user-123"),
            shipping_addresses=["123 Main St"],
            billing_addresses=["123 Main St"],
            preferences={"newsletter": True}
        )

    @pytest.fixture
    def customer_model(self):
        """Create test customer model."""
        return CustomerModel(
            id="customer-123",
            user_id="user-123",
            shipping_address="123 Main St",
            billing_address="123 Main St",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

    @pytest.mark.asyncio
    async def test_save_customer(self, repository, customer):
        """Test saving customer."""
        mock_customer_model = CustomerModel(
            id="customer-123",
            user_id="user-123",
            shipping_address="123 Main St",
            billing_address="123 Main St"
        )
        
        with patch.object(SQLRepository, 'save', return_value=mock_customer_model):
            result = await repository.save(customer)
            
            assert result.id.value == "customer-123"
            assert result.user_id.value == "user-123"
            assert result.shipping_addresses == ["123 Main St"]
            assert result.billing_addresses == ["123 Main St"]

    @pytest.mark.asyncio
    async def test_get_by_id_found(self, repository):
        """Test getting customer by ID when found."""
        mock_customer_model = CustomerModel(
            id="customer-123",
            user_id="user-123",
            shipping_address="123 Main St",
            billing_address="123 Main St"
        )
        
        with patch.object(SQLRepository, 'get_by_id', return_value=mock_customer_model):
            result = await repository.get_by_id(CustomerId("customer-123"))
            
            assert result is not None
            assert result.id.value == "customer-123"
            assert result.user_id.value == "user-123"

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, repository):
        """Test getting customer by ID when not found."""
        with patch.object(repository, 'get_by_id', return_value=None):
            result = await repository.get_by_id(CustomerId("customer-123"))
            
            assert result is None

    @pytest.mark.asyncio
    async def test_get_by_user_id_found(self, repository, customer_model):
        """Test getting customer by user ID when found."""
        with patch.object(repository.session, 'execute') as mock_execute:
            mock_result = Mock()
            mock_result.scalar_one_or_none.return_value = customer_model
            mock_execute.return_value = mock_result
            
            result = await repository.get_by_user_id(UserId("user-123"))
            
            assert result is not None
            assert result.user_id.value == "user-123"

    @pytest.mark.asyncio
    async def test_get_by_user_id_not_found(self, repository):
        """Test getting customer by user ID when not found."""
        with patch.object(repository.session, 'execute') as mock_execute:
            mock_result = Mock()
            mock_result.scalar_one_or_none.return_value = None
            mock_execute.return_value = mock_result
            
            result = await repository.get_by_user_id(UserId("user-123"))
            
            assert result is None

    @pytest.mark.asyncio
    async def test_get_all(self, repository, customer_model):
        """Test getting all customers."""
        with patch.object(repository.session, 'execute') as mock_execute:
            mock_result = Mock()
            mock_result.scalars.return_value.all.return_value = [customer_model]
            mock_execute.return_value = mock_result
            
            result = await repository.get_all()
            
            assert len(result) == 1
            assert result[0].id.value == "customer-123"

    @pytest.mark.asyncio
    async def test_delete_success(self, repository):
        """Test deleting customer successfully."""
        with patch.object(repository, 'delete', return_value=True):
            result = await repository.delete(CustomerId("customer-123"))
            
            assert result is True

    @pytest.mark.asyncio
    async def test_delete_not_found(self, repository):
        """Test deleting customer when not found."""
        with patch.object(repository, 'delete', return_value=False):
            result = await repository.delete(CustomerId("customer-123"))
            
            assert result is False


class TestSQLSellerRepository:
    """Test cases for SQLSellerRepository."""

    @pytest.fixture
    def mock_session(self):
        """Create mock SQLAlchemy session."""
        return AsyncMock()

    @pytest.fixture
    def repository(self, mock_session):
        """Create SQLSellerRepository instance."""
        return SQLSellerRepository(mock_session)

    @pytest.fixture
    def seller(self):
        """Create test seller."""
        return Seller(
            id=SellerId("seller-123"),
            user_id=UserId("user-123"),
            company_name="Test Business",
            business_address="456 Business St",
            company_description="Test business description",
            tax_id="TAX123456",
            is_verified=True
        )

    @pytest.fixture
    def seller_model(self):
        """Create test seller model."""
        return SellerModel(
            id="seller-123",
            user_id="user-123",
            company_name="Test Business",
            business_address="456 Business St",
            company_description="Test business description",
            tax_id="TAX123456",
            is_verified=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

    @pytest.mark.asyncio
    async def test_save_seller(self, repository, seller):
        """Test saving seller."""
        mock_seller_model = SellerModel(
            id="seller-123",
            user_id="user-123",
            company_name="Test Business",
            business_address="456 Business St",
            company_description="Test business description",
            tax_id="TAX123456",
            is_verified=True
        )
        
        with patch.object(SQLRepository, 'save', return_value=mock_seller_model):
            result = await repository.save(seller)
            
            assert result.id.value == "seller-123"
            assert result.user_id.value == "user-123"
            assert result.company_name == "Test Business"
            assert result.business_address == "456 Business St"
            assert result.company_description == "Test business description"
            assert result.tax_id == "TAX123456"
            assert result.is_verified is True

    @pytest.mark.asyncio
    async def test_get_by_id_found(self, repository):
        """Test getting seller by ID when found."""
        mock_seller_model = SellerModel(
            id="seller-123",
            user_id="user-123",
            company_name="Test Business",
            business_address="456 Business St",
            company_description="Test business description",
            tax_id="TAX123456",
            is_verified=True
        )
        
        with patch.object(SQLRepository, 'get_by_id', return_value=mock_seller_model):
            result = await repository.get_by_id(SellerId("seller-123"))
            
            assert result is not None
            assert result.id.value == "seller-123"
            assert result.user_id.value == "user-123"

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, repository):
        """Test getting seller by ID when not found."""
        with patch.object(repository, 'get_by_id', return_value=None):
            result = await repository.get_by_id(SellerId("seller-123"))
            
            assert result is None

    @pytest.mark.asyncio
    async def test_get_by_user_id_found(self, repository, seller_model):
        """Test getting seller by user ID when found."""
        with patch.object(repository.session, 'execute') as mock_execute:
            mock_result = Mock()
            mock_result.scalar_one_or_none.return_value = seller_model
            mock_execute.return_value = mock_result
            
            result = await repository.get_by_user_id(UserId("user-123"))
            
            assert result is not None
            assert result.user_id.value == "user-123"

    @pytest.mark.asyncio
    async def test_get_by_user_id_not_found(self, repository):
        """Test getting seller by user ID when not found."""
        with patch.object(repository.session, 'execute') as mock_execute:
            mock_result = Mock()
            mock_result.scalar_one_or_none.return_value = None
            mock_execute.return_value = mock_result
            
            result = await repository.get_by_user_id(UserId("user-123"))
            
            assert result is None

    @pytest.mark.asyncio
    async def test_get_all(self, repository, seller_model):
        """Test getting all sellers."""
        with patch.object(repository.session, 'execute') as mock_execute:
            mock_result = Mock()
            mock_result.scalars.return_value.all.return_value = [seller_model]
            mock_execute.return_value = mock_result
            
            result = await repository.get_all()
            
            assert len(result) == 1
            assert result[0].id.value == "seller-123"

    @pytest.mark.asyncio
    async def test_get_verified(self, repository, seller_model):
        """Test getting verified sellers."""
        with patch.object(repository.session, 'execute') as mock_execute:
            mock_result = Mock()
            mock_result.scalars.return_value.all.return_value = [seller_model]
            mock_execute.return_value = mock_result
            
            result = await repository.get_verified()
            
            assert len(result) == 1
            assert result[0].id.value == "seller-123"
            assert result[0].is_verified is True

    @pytest.mark.asyncio
    async def test_delete_success(self, repository):
        """Test deleting seller successfully."""
        with patch.object(repository, 'delete', return_value=True):
            result = await repository.delete(SellerId("seller-123"))
            
            assert result is True

    @pytest.mark.asyncio
    async def test_delete_not_found(self, repository):
        """Test deleting seller when not found."""
        with patch.object(repository, 'delete', return_value=False):
            result = await repository.delete(SellerId("seller-123"))
            
            assert result is False


class TestRepositoryEdgeCases:
    """Test cases for edge cases in repositories."""

    @pytest.fixture
    def mock_session(self):
        """Create mock SQLAlchemy session."""
        return AsyncMock()

    @pytest.fixture
    def user_repository(self, mock_session):
        """Create SQLUserRepository instance."""
        return SQLUserRepository(mock_session)

    @pytest.fixture
    def customer_repository(self, mock_session):
        """Create SQLCustomerRepository instance."""
        return SQLCustomerRepository(mock_session)

    @pytest.fixture
    def seller_repository(self, mock_session):
        """Create SQLSellerRepository instance."""
        return SQLSellerRepository(mock_session)

    @pytest.mark.asyncio
    async def test_save_user_without_phone(self, user_repository):
        """Test saving user without phone number."""
        user = User(
            id=UserId("user-123"),
            email=Email("test@example.com"),
            username=Username("testuser"),
            first_name="John",
            last_name="Doe",
            phone_number=None,
            is_active=True
        )
        
        user_model = UserModel(
            id="user-123",
            email="test@example.com",
            username="testuser",
            password_hash="",
            first_name="John",
            last_name="Doe",
            phone_number=None,
            is_active=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        with patch.object(SQLRepository, 'save', return_value=user_model):
            result = await user_repository.save(user)
            
            assert result.phone_number is None

    @pytest.mark.asyncio
    async def test_get_all_empty(self, user_repository):
        """Test getting all users when empty."""
        with patch.object(user_repository.session, 'execute') as mock_execute:
            mock_result = Mock()
            mock_result.scalars.return_value.all.return_value = []
            mock_execute.return_value = mock_result
            
            result = await user_repository.get_all()
            
            assert len(result) == 0

    @pytest.mark.asyncio
    async def test_get_verified_empty(self, seller_repository):
        """Test getting verified sellers when empty."""
        with patch.object(seller_repository.session, 'execute') as mock_execute:
            mock_result = Mock()
            mock_result.scalars.return_value.all.return_value = []
            mock_execute.return_value = mock_result
            
            result = await seller_repository.get_verified()
            
            assert len(result) == 0 