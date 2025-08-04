"""Tests for users application services."""

import pytest
from unittest.mock import AsyncMock

from src.users.application.services import UserService, CustomerService, SellerService
from src.users.domain.entities import User, Customer, Seller
from src.users.domain.value_objects import (
    UserId, CustomerId, SellerId, Email, PhoneNumber, Username
)
from src.shared.domain.exceptions import EntityNotFoundError, BusinessRuleViolationError


class TestUserService:
    """Test UserService."""

    @pytest.fixture
    def user_repository(self):
        """Create mock user repository."""
        return AsyncMock()

    @pytest.fixture
    def service(self, user_repository):
        """Create user service."""
        return UserService(user_repository)

    @pytest.fixture
    def sample_user(self):
        """Create sample user."""
        return User(
            id=UserId(value="user_123"),
            email=Email(value="test@example.com"),
            username=Username(value="johndoe"),
            first_name="John",
            last_name="Doe",
            phone_number=PhoneNumber(value="+1234567890"),
        )

    @pytest.mark.asyncio
    async def test_create_user(self, service, user_repository):
        """Test creating a user."""
        # Arrange
        email = "test@example.com"
        password_hash = "hashed_password"
        first_name = "John"
        last_name = "Doe"
        phone_number = "+1234567890"
        
        expected_user = User(
            id=UserId(value="user_123"),
            email=Email(value=email),
            username=Username(value="johndoe"),
            first_name=first_name,
            last_name=last_name,
            phone_number=PhoneNumber(value=phone_number),
        )
        user_repository.get_by_email.return_value = None
        user_repository.save.return_value = expected_user

        # Act
        result = await service.create_user(email, password_hash, first_name, last_name, phone_number)

        # Assert
        assert result == expected_user
        user_repository.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_user_email_already_exists(self, service, user_repository, sample_user):
        """Test creating a user with existing email."""
        # Arrange
        email = "test@example.com"
        password_hash = "hashed_password"
        first_name = "John"
        last_name = "Doe"
        
        user_repository.get_by_email.return_value = sample_user

        # Act & Assert
        with pytest.raises(BusinessRuleViolationError, match="User with this email already exists"):
            await service.create_user(email, password_hash, first_name, last_name)

    @pytest.mark.asyncio
    async def test_get_user_found(self, service, user_repository, sample_user):
        """Test getting user that exists."""
        # Arrange
        user_id = "user_123"
        user_repository.get_by_id.return_value = sample_user

        # Act
        result = await service.get_user(user_id)

        # Assert
        assert result == sample_user
        user_repository.get_by_id.assert_called_once_with(UserId(value=user_id))

    @pytest.mark.asyncio
    async def test_get_user_not_found(self, service, user_repository):
        """Test getting user that doesn't exist."""
        # Arrange
        user_id = "user_999"
        user_repository.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(EntityNotFoundError, match=f"User with ID {user_id} not found"):
            await service.get_user(user_id)

    @pytest.mark.asyncio
    async def test_get_user_by_email_found(self, service, user_repository, sample_user):
        """Test getting user by email that exists."""
        # Arrange
        email = "test@example.com"
        user_repository.get_by_email.return_value = sample_user

        # Act
        result = await service.get_user_by_email(email)

        # Assert
        assert result == sample_user
        user_repository.get_by_email.assert_called_once_with(Email(value=email))

    @pytest.mark.asyncio
    async def test_get_user_by_email_not_found(self, service, user_repository):
        """Test getting user by email that doesn't exist."""
        # Arrange
        email = "nonexistent@example.com"
        user_repository.get_by_email.return_value = None

        # Act
        result = await service.get_user_by_email(email)

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_get_all_users(self, service, user_repository, sample_user):
        """Test getting all users."""
        # Arrange
        expected_users = [sample_user]
        user_repository.get_all.return_value = expected_users

        # Act
        result = await service.get_all_users()

        # Assert
        assert result == expected_users
        user_repository.get_all.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_user(self, service, user_repository, sample_user):
        """Test updating user."""
        # Arrange
        user_id = "user_123"
        new_first_name = "Jane"
        new_last_name = "Smith"
        new_phone_number = "+0987654321"
        
        user_repository.get_by_id.return_value = sample_user
        user_repository.save.return_value = sample_user

        # Act
        result = await service.update_user(user_id, new_first_name, new_last_name, new_phone_number)

        # Assert
        assert result == sample_user
        assert sample_user.first_name == new_first_name
        assert sample_user.last_name == new_last_name
        assert sample_user.phone_number.value == "0987654321"  # PhoneNumber normalizes to digits only
        user_repository.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_deactivate_user(self, service, user_repository, sample_user):
        """Test deactivating user."""
        # Arrange
        user_id = "user_123"
        sample_user.is_active = True
        user_repository.get_by_id.return_value = sample_user
        user_repository.save.return_value = sample_user

        # Act
        result = await service.deactivate_user(user_id)

        # Assert
        assert result == sample_user
        assert sample_user.is_active is False
        user_repository.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_user(self, service, user_repository):
        """Test deleting user."""
        # Arrange
        user_id = "user_123"
        user_repository.delete.return_value = True

        # Act
        result = await service.delete_user(user_id)

        # Assert
        assert result is True
        user_repository.delete.assert_called_once_with(UserId(value=user_id))


class TestCustomerService:
    """Test CustomerService."""

    @pytest.fixture
    def customer_repository(self):
        """Create mock customer repository."""
        return AsyncMock()

    @pytest.fixture
    def service(self, customer_repository):
        """Create customer service."""
        return CustomerService(customer_repository)

    @pytest.fixture
    def sample_customer(self):
        """Create sample customer."""
        return Customer(
            id=CustomerId(value="customer_123"),
            user_id=UserId(value="user_123"),
            shipping_addresses=["ул. Ленина, 1, Москва"],
            billing_addresses=["ул. Ленина, 1, Москва"],
        )

    @pytest.mark.asyncio
    async def test_create_customer(self, service, customer_repository):
        """Test creating a customer."""
        # Arrange
        user_id = "user_123"
        shipping_address = "ул. Ленина, 1, Москва"
        billing_address = "ул. Ленина, 1, Москва"
        
        expected_customer = Customer(
            id=CustomerId(value="customer_123"),
            user_id=UserId(value=user_id),
            shipping_addresses=[shipping_address],
            billing_addresses=[billing_address],
        )
        customer_repository.save.return_value = expected_customer

        # Act
        result = await service.create_customer(user_id, shipping_address, billing_address)

        # Assert
        assert result == expected_customer
        customer_repository.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_customer_found(self, service, customer_repository, sample_customer):
        """Test getting customer that exists."""
        # Arrange
        customer_id = "customer_123"
        customer_repository.get_by_id.return_value = sample_customer

        # Act
        result = await service.get_customer(customer_id)

        # Assert
        assert result == sample_customer
        customer_repository.get_by_id.assert_called_once_with(CustomerId(value=customer_id))

    @pytest.mark.asyncio
    async def test_get_customer_not_found(self, service, customer_repository):
        """Test getting customer that doesn't exist."""
        # Arrange
        customer_id = "customer_999"
        customer_repository.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(EntityNotFoundError, match=f"Customer with ID {customer_id} not found"):
            await service.get_customer(customer_id)

    @pytest.mark.asyncio
    async def test_get_customer_by_user_id_found(self, service, customer_repository, sample_customer):
        """Test getting customer by user ID that exists."""
        # Arrange
        user_id = "user_123"
        customer_repository.get_by_user_id.return_value = sample_customer

        # Act
        result = await service.get_customer_by_user_id(user_id)

        # Assert
        assert result == sample_customer
        customer_repository.get_by_user_id.assert_called_once_with(UserId(value=user_id))

    @pytest.mark.asyncio
    async def test_get_customer_by_user_id_not_found(self, service, customer_repository):
        """Test getting customer by user ID that doesn't exist."""
        # Arrange
        user_id = "user_999"
        customer_repository.get_by_user_id.return_value = None

        # Act
        result = await service.get_customer_by_user_id(user_id)

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_get_all_customers(self, service, customer_repository, sample_customer):
        """Test getting all customers."""
        # Arrange
        expected_customers = [sample_customer]
        customer_repository.get_all.return_value = expected_customers

        # Act
        result = await service.get_all_customers()

        # Assert
        assert result == expected_customers
        customer_repository.get_all.assert_called_once()

    @pytest.mark.asyncio
    async def test_add_shipping_address(self, service, customer_repository, sample_customer):
        """Test adding shipping address to customer."""
        # Arrange
        customer_id = "customer_123"
        new_address = "ул. Пушкина, 10, Санкт-Петербург"
        customer_repository.get_by_id.return_value = sample_customer
        customer_repository.save.return_value = sample_customer

        # Act
        result = await service.add_shipping_address(customer_id, new_address)

        # Assert
        assert result == sample_customer
        assert new_address in sample_customer.shipping_addresses
        customer_repository.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_add_billing_address(self, service, customer_repository, sample_customer):
        """Test adding billing address to customer."""
        # Arrange
        customer_id = "customer_123"
        new_address = "ул. Пушкина, 10, Санкт-Петербург"
        customer_repository.get_by_id.return_value = sample_customer
        customer_repository.save.return_value = sample_customer

        # Act
        result = await service.add_billing_address(customer_id, new_address)

        # Assert
        assert result == sample_customer
        assert new_address in sample_customer.billing_addresses
        customer_repository.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_customer(self, service, customer_repository):
        """Test deleting customer."""
        # Arrange
        customer_id = "customer_123"
        customer_repository.delete.return_value = True

        # Act
        result = await service.delete_customer(customer_id)

        # Assert
        assert result is True
        customer_repository.delete.assert_called_once_with(CustomerId(value=customer_id))


class TestSellerService:
    """Test SellerService."""

    @pytest.fixture
    def seller_repository(self):
        """Create mock seller repository."""
        return AsyncMock()

    @pytest.fixture
    def service(self, seller_repository):
        """Create seller service."""
        return SellerService(seller_repository)

    @pytest.fixture
    def sample_seller(self):
        """Create sample seller."""
        return Seller(
            id=SellerId(value="seller_123"),
            user_id=UserId(value="user_123"),
            company_name="ООО Тест",
            business_address="ул. Ленина, 1, Москва",
            company_description="Тестовая компания",
        )

    @pytest.mark.asyncio
    async def test_create_seller(self, service, seller_repository):
        """Test creating a seller."""
        # Arrange
        user_id = "user_123"
        company_name = "ООО Тест"
        company_description = "Тестовая компания"
        website = "https://test.com"
        
        expected_seller = Seller(
            id=SellerId(value="seller_123"),
            user_id=UserId(value=user_id),
            company_name=company_name,
            business_address="ул. Ленина, 1, Москва",
            company_description=company_description,
        )
        seller_repository.save.return_value = expected_seller

        # Act
        result = await service.create_seller(user_id, company_name, company_description, website)

        # Assert
        assert result == expected_seller
        seller_repository.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_seller_found(self, service, seller_repository, sample_seller):
        """Test getting seller that exists."""
        # Arrange
        seller_id = "seller_123"
        seller_repository.get_by_id.return_value = sample_seller

        # Act
        result = await service.get_seller(seller_id)

        # Assert
        assert result == sample_seller
        seller_repository.get_by_id.assert_called_once_with(SellerId(value=seller_id))

    @pytest.mark.asyncio
    async def test_get_seller_not_found(self, service, seller_repository):
        """Test getting seller that doesn't exist."""
        # Arrange
        seller_id = "seller_999"
        seller_repository.get_by_id.return_value = None

        # Act & Assert
        with pytest.raises(EntityNotFoundError, match=f"Seller with ID {seller_id} not found"):
            await service.get_seller(seller_id)

    @pytest.mark.asyncio
    async def test_get_seller_by_user_id_found(self, service, seller_repository, sample_seller):
        """Test getting seller by user ID that exists."""
        # Arrange
        user_id = "user_123"
        seller_repository.get_by_user_id.return_value = sample_seller

        # Act
        result = await service.get_seller_by_user_id(user_id)

        # Assert
        assert result == sample_seller
        seller_repository.get_by_user_id.assert_called_once_with(UserId(value=user_id))

    @pytest.mark.asyncio
    async def test_get_seller_by_user_id_not_found(self, service, seller_repository):
        """Test getting seller by user ID that doesn't exist."""
        # Arrange
        user_id = "user_999"
        seller_repository.get_by_user_id.return_value = None

        # Act
        result = await service.get_seller_by_user_id(user_id)

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_get_all_sellers(self, service, seller_repository, sample_seller):
        """Test getting all sellers."""
        # Arrange
        expected_sellers = [sample_seller]
        seller_repository.get_all.return_value = expected_sellers

        # Act
        result = await service.get_all_sellers()

        # Assert
        assert result == expected_sellers
        seller_repository.get_all.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_verified_sellers(self, service, seller_repository, sample_seller):
        """Test getting verified sellers."""
        # Arrange
        expected_sellers = [sample_seller]
        seller_repository.get_verified.return_value = expected_sellers

        # Act
        result = await service.get_verified_sellers()

        # Assert
        assert result == expected_sellers
        seller_repository.get_verified.assert_called_once()

    @pytest.mark.asyncio
    async def test_verify_seller(self, service, seller_repository, sample_seller):
        """Test verifying seller."""
        # Arrange
        seller_id = "seller_123"
        sample_seller.is_verified = False
        seller_repository.get_by_id.return_value = sample_seller
        seller_repository.save.return_value = sample_seller

        # Act
        result = await service.verify_seller(seller_id)

        # Assert
        assert result == sample_seller
        assert sample_seller.is_verified is True
        seller_repository.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_unverify_seller(self, service, seller_repository, sample_seller):
        """Test unverifying seller."""
        # Arrange
        seller_id = "seller_123"
        sample_seller.is_verified = True
        seller_repository.get_by_id.return_value = sample_seller
        seller_repository.save.return_value = sample_seller

        # Act
        result = await service.unverify_seller(seller_id)

        # Assert
        assert result == sample_seller
        assert sample_seller.is_verified is False
        seller_repository.save.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_seller(self, service, seller_repository):
        """Test deleting seller."""
        # Arrange
        seller_id = "seller_123"
        seller_repository.delete.return_value = True

        # Act
        result = await service.delete_seller(seller_id)

        # Assert
        assert result is True
        seller_repository.delete.assert_called_once_with(SellerId(value=seller_id)) 