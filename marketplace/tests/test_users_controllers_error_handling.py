"""Tests for error handling in users controllers."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import HTTPException
from fastapi.testclient import TestClient

from src.interfaces.api.users_controllers import (
    router,
    get_user_service,
    CreateUserRequest,
    UpdateUserRequest,
    AuthenticateUserRequest,
)
from src.users.application.services import UserService
from src.users.domain.exceptions import (
    UserNotFoundError,
    UserAlreadyExistsError,
    InvalidUserDataError,
)
from src.shared.domain.exceptions import EntityNotFoundError, InvalidOperationError, AuthenticationError


class TestUsersControllersErrorHandling:
    """Test error handling scenarios in users controllers."""

    @pytest.fixture
    def mock_user_service(self):
        """Create a mock user service."""
        service = AsyncMock(spec=UserService)
        return service

    @pytest.fixture
    def client(self, mock_user_service):
        """Create test client with mocked service."""
        from fastapi import FastAPI
        app = FastAPI()
        app.include_router(router)
        
        # Override dependency
        app.dependency_overrides[get_user_service] = lambda: mock_user_service
        
        return TestClient(app)

    async def test_create_user_invalid_email(self, client, mock_user_service):
        """Test creating user with invalid email format."""
        # Arrange
        mock_user_service.create_user.side_effect = ValueError("Invalid email format")
        
        request_data = {
            "username": "testuser",
            "email": "invalid_email",
            "password": "TestPassword123!",
            "first_name": "Test",
            "last_name": "User"
        }
        
        # Act & Assert
        response = client.post("/users", json=request_data)
        assert response.status_code == 400
        assert "Invalid email format" in response.json()["detail"]

    async def test_create_user_empty_username(self, client, mock_user_service):
        """Test creating user with empty username."""
        # Arrange
        mock_user_service.create_user.side_effect = ValueError("Username cannot be empty")
        
        request_data = {
            "username": "",
            "email": "test@example.com",
            "password": "TestPassword123!",
            "first_name": "Test",
            "last_name": "User"
        }
        
        # Act & Assert
        response = client.post("/users", json=request_data)
        assert response.status_code == 400
        assert "Username cannot be empty" in response.json()["detail"]

    async def test_create_user_weak_password(self, client, mock_user_service):
        """Test creating user with weak password."""
        # Arrange
        mock_user_service.create_user.side_effect = ValueError("Password does not meet security requirements")
        
        request_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "weak",
            "first_name": "Test",
            "last_name": "User"
        }
        
        # Act & Assert
        response = client.post("/users", json=request_data)
        assert response.status_code == 400
        assert "Password does not meet security requirements" in response.json()["detail"]

    async def test_create_user_existing_email(self, client, mock_user_service):
        """Test creating user with existing email."""
        # Arrange
        mock_user_service.create_user.side_effect = UserAlreadyExistsError("User with this email already exists")
        
        request_data = {
            "username": "testuser",
            "email": "existing@example.com",
            "password": "TestPassword123!",
            "first_name": "Test",
            "last_name": "User"
        }
        
        # Act & Assert
        response = client.post("/users", json=request_data)
        assert response.status_code == 409
        assert "User with this email already exists" in response.json()["detail"]

    async def test_create_user_existing_username(self, client, mock_user_service):
        """Test creating user with existing username."""
        # Arrange
        mock_user_service.create_user.side_effect = UserAlreadyExistsError("Username already taken")
        
        request_data = {
            "username": "existinguser",
            "email": "test@example.com",
            "password": "TestPassword123!",
            "first_name": "Test",
            "last_name": "User"
        }
        
        # Act & Assert
        response = client.post("/users", json=request_data)
        assert response.status_code == 409
        assert "Username already taken" in response.json()["detail"]

    async def test_update_user_not_found(self, client, mock_user_service):
        """Test updating non-existent user."""
        # Arrange
        mock_user_service.update_user.side_effect = UserNotFoundError("User not found")
        
        request_data = {
            "first_name": "Updated",
            "last_name": "Name"
        }
        
        # Act & Assert
        response = client.put("/users/non_existent_user", json=request_data)
        assert response.status_code == 404
        assert "User not found" in response.json()["detail"]

    async def test_update_user_invalid_data(self, client, mock_user_service):
        """Test updating user with invalid data."""
        # Arrange
        mock_user_service.update_user.side_effect = ValueError("Invalid user data")
        
        request_data = {
            "email": "invalid_email",
            "first_name": ""
        }
        
        # Act & Assert
        response = client.put("/users/test_user", json=request_data)
        assert response.status_code == 400
        assert "Invalid user data" in response.json()["detail"]

    async def test_update_user_email_conflict(self, client, mock_user_service):
        """Test updating user with email that already exists."""
        # Arrange
        mock_user_service.update_user.side_effect = UserAlreadyExistsError("Email already in use")
        
        request_data = {
            "email": "existing@example.com"
        }
        
        # Act & Assert
        response = client.put("/users/test_user", json=request_data)
        assert response.status_code == 409
        assert "Email already in use" in response.json()["detail"]

    async def test_delete_user_not_found(self, client, mock_user_service):
        """Test deleting non-existent user."""
        # Arrange
        mock_user_service.delete_user.side_effect = UserNotFoundError("User not found")
        
        # Act & Assert
        response = client.delete("/users/non_existent_user")
        assert response.status_code == 404
        assert "User not found" in response.json()["detail"]

    async def test_delete_user_with_active_orders(self, client, mock_user_service):
        """Test deleting user with active orders."""
        # Arrange
        mock_user_service.delete_user.side_effect = InvalidOperationError("Cannot delete user with active orders")
        
        # Act & Assert
        response = client.delete("/users/test_user")
        assert response.status_code == 400
        assert "Cannot delete user with active orders" in response.json()["detail"]

    async def test_get_user_by_id_not_found(self, client, mock_user_service):
        """Test getting non-existent user by ID."""
        # Arrange
        mock_user_service.get_user_by_id.side_effect = UserNotFoundError("User not found")
        
        # Act & Assert
        response = client.get("/users/non_existent_user")
        assert response.status_code == 404
        assert "User not found" in response.json()["detail"]

    async def test_get_user_by_id_invalid_format(self, client, mock_user_service):
        """Test getting user with invalid ID format."""
        # Arrange
        mock_user_service.get_user_by_id.side_effect = ValueError("Invalid user ID format")
        
        # Act & Assert
        response = client.get("/users/invalid_id_format")
        assert response.status_code == 400
        assert "Invalid user ID format" in response.json()["detail"]

    async def test_get_user_by_email_not_found(self, client, mock_user_service):
        """Test getting non-existent user by email."""
        # Arrange
        mock_user_service.get_user_by_email.side_effect = UserNotFoundError("User not found")
        
        # Act & Assert
        response = client.get("/users/email/non_existent@example.com")
        assert response.status_code == 404
        assert "User not found" in response.json()["detail"]

    async def test_get_user_by_email_invalid_format(self, client, mock_user_service):
        """Test getting user with invalid email format."""
        # Arrange
        mock_user_service.get_user_by_email.side_effect = ValueError("Invalid email format")
        
        # Act & Assert
        response = client.get("/users/email/invalid_email")
        assert response.status_code == 400
        assert "Invalid email format" in response.json()["detail"]

    async def test_authenticate_user_invalid_credentials(self, client, mock_user_service):
        """Test authentication with invalid credentials."""
        # Arrange
        mock_user_service.authenticate_user.side_effect = AuthenticationError("Invalid credentials")
        
        request_data = {
            "username": "testuser",
            "password": "wrongpassword"
        }
        
        # Act & Assert
        response = client.post("/users/authenticate", json=request_data)
        assert response.status_code == 401
        assert "Invalid credentials" in response.json()["detail"]

    async def test_authenticate_user_blocked(self, client, mock_user_service):
        """Test authentication with blocked user."""
        # Arrange
        mock_user_service.authenticate_user.side_effect = AuthenticationError("User account is blocked")
        
        request_data = {
            "username": "blockeduser",
            "password": "correctpassword"
        }
        
        # Act & Assert
        response = client.post("/users/authenticate", json=request_data)
        assert response.status_code == 401
        assert "User account is blocked" in response.json()["detail"]

    async def test_authenticate_user_inactive(self, client, mock_user_service):
        """Test authentication with inactive user."""
        # Arrange
        mock_user_service.authenticate_user.side_effect = AuthenticationError("User account is not activated")
        
        request_data = {
            "username": "inactiveuser",
            "password": "correctpassword"
        }
        
        # Act & Assert
        response = client.post("/users/authenticate", json=request_data)
        assert response.status_code == 401
        assert "User account is not activated" in response.json()["detail"]

    async def test_authenticate_user_empty_credentials(self, client, mock_user_service):
        """Test authentication with empty credentials."""
        # Arrange
        mock_user_service.authenticate_user.side_effect = ValueError("Username and password are required")
        
        request_data = {
            "username": "",
            "password": ""
        }
        
        # Act & Assert
        response = client.post("/users/authenticate", json=request_data)
        assert response.status_code == 400
        assert "Username and password are required" in response.json()["detail"]

    async def test_get_users_empty_list(self, client, mock_user_service):
        """Test getting users when none exist."""
        # Arrange
        mock_user_service.get_users.return_value = []
        
        # Act & Assert
        response = client.get("/users")
        assert response.status_code == 200
        assert response.json() == []

    async def test_get_users_invalid_pagination(self, client, mock_user_service):
        """Test getting users with invalid pagination parameters."""
        # Arrange
        mock_user_service.get_users.side_effect = ValueError("Invalid pagination parameters")
        
        # Act & Assert
        response = client.get("/users?page=-1&size=0")
        assert response.status_code == 400
        assert "Invalid pagination parameters" in response.json()["detail"]

    async def test_search_users_not_found(self, client, mock_user_service):
        """Test searching users with no results."""
        # Arrange
        mock_user_service.search_users.return_value = []
        
        # Act & Assert
        response = client.get("/users/search?q=nonexistent")
        assert response.status_code == 200
        assert response.json() == []

    async def test_search_users_invalid_query(self, client, mock_user_service):
        """Test searching users with invalid query."""
        # Arrange
        mock_user_service.search_users.side_effect = ValueError("Search query is too short")
        
        # Act & Assert
        response = client.get("/users/search?q=a")
        assert response.status_code == 400
        assert "Search query is too short" in response.json()["detail"] 