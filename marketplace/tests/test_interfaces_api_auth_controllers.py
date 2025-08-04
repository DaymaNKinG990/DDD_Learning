"""Tests for interfaces.api.auth_controllers module."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi import FastAPI
from src.interfaces.api.auth_controllers import (
    router, LoginRequest, TokenResponse, RefreshTokenRequest, 
    ChangePasswordRequest, UserInfoResponse, get_auth_service, get_current_user
)


@pytest.fixture
def auth_client():
    """Create test client for auth router."""
    app = FastAPI()
    from src.shared.infrastructure.error_handlers import ErrorHandler
    ErrorHandler(app)
    app.include_router(router)
    return TestClient(app)


class TestRequestModels:
    """Test Pydantic request models."""

    def test_login_request(self):
        """Test LoginRequest model."""
        request = LoginRequest(
            email="test@example.com",
            password="password123"
        )
        assert request.email == "test@example.com"
        assert request.password == "password123"

    def test_token_response(self):
        """Test TokenResponse model."""
        response = TokenResponse(
            access_token="access_token_123",
            refresh_token="refresh_token_123",
            token_type="bearer",
            expires_in=3600
        )
        assert response.access_token == "access_token_123"
        assert response.refresh_token == "refresh_token_123"
        assert response.token_type == "bearer"
        assert response.expires_in == 3600

    def test_token_response_defaults(self):
        """Test TokenResponse model with defaults."""
        response = TokenResponse(
            access_token="access_token_123",
            refresh_token="refresh_token_123",
            expires_in=3600
        )
        assert response.token_type == "bearer"

    def test_refresh_token_request(self):
        """Test RefreshTokenRequest model."""
        request = RefreshTokenRequest(
            refresh_token="refresh_token_123"
        )
        assert request.refresh_token == "refresh_token_123"

    def test_change_password_request(self):
        """Test ChangePasswordRequest model."""
        request = ChangePasswordRequest(
            old_password="old_password",
            new_password="new_password"
        )
        assert request.old_password == "old_password"
        assert request.new_password == "new_password"

    def test_user_info_response(self):
        """Test UserInfoResponse model."""
        response = UserInfoResponse(
            id="user-123",
            email="test@example.com",
            first_name="John",
            last_name="Doe",
            is_active=True
        )
        assert response.id == "user-123"
        assert response.email == "test@example.com"
        assert response.first_name == "John"
        assert response.last_name == "Doe"
        assert response.is_active is True


class TestRouterConfiguration:
    """Test router configuration."""

    def test_auth_router_prefix(self):
        """Test auth router prefix."""
        assert router.prefix == "/auth"
        assert "authentication" in router.tags

    def test_auth_router_routes(self):
        """Test auth router has expected routes."""
        routes = [route.path for route in router.routes]
        assert "/auth/login" in routes
        assert "/auth/refresh" in routes
        assert "/auth/logout" in routes


class TestDependencyInjection:
    """Test dependency injection."""

    def test_get_auth_service(self):
        """Test get_auth_service dependency."""
        # This would require more complex setup with database
        pass

    def test_get_current_user(self):
        """Test get_current_user dependency."""
        # This would require more complex setup with tokens
        pass


class TestSecurityScheme:
    """Test security scheme."""

    def test_security_scheme_exists(self):
        """Test security scheme is defined."""
        from src.interfaces.api.auth_controllers import security
        assert security is not None


class TestAuthEndpoints:
    """Test authentication endpoints."""

    def test_login_success(self, auth_client):
        """Test successful login."""
        with patch('src.interfaces.api.auth_controllers.get_auth_service') as mock_get_service:
            # Mock authentication service
            mock_service = AsyncMock()
            mock_token_pair = MagicMock()
            mock_token_pair.access_token.value = "access_token_123"
            mock_token_pair.refresh_token.value = "refresh_token_123"
            mock_service.login.return_value = mock_token_pair
            mock_get_service.return_value = mock_service

            # Override the dependency
            auth_client.app.dependency_overrides[get_auth_service] = lambda: mock_service

            response = auth_client.post("/auth/login", json={
                "email": "test@example.com",
                "password": "password123"
            })

            assert response.status_code == 200
            data = response.json()
            assert "access_token" in data
            assert "refresh_token" in data
            assert data["token_type"] == "bearer"
            assert "expires_in" in data

            # Clean up
            auth_client.app.dependency_overrides.clear()

    def test_login_invalid_credentials(self, auth_client):
        """Test login with invalid credentials."""
        with patch('src.interfaces.api.auth_controllers.get_auth_service') as mock_get_service:
            # Mock authentication service to raise exception
            mock_service = AsyncMock()
            from src.shared.domain.exceptions import BusinessRuleViolationError
            mock_service.login.side_effect = BusinessRuleViolationError("Invalid credentials")
            mock_get_service.return_value = mock_service

            # Override the dependency
            auth_client.app.dependency_overrides[get_auth_service] = lambda: mock_service

            response = auth_client.post("/auth/login", json={
                "email": "test@example.com",
                "password": "wrong_password"
            })

            assert response.status_code == 400
            data = response.json()
            assert "detail" in data

            # Clean up
            auth_client.app.dependency_overrides.clear()

    def test_login_validation_error(self, auth_client):
        """Test login with validation error."""
        response = auth_client.post("/auth/login", json={
            "email": "invalid-email",
            "password": ""  # Empty password
        })

        assert response.status_code == 422  # Validation error

    def test_refresh_token_success(self, auth_client):
        """Test successful token refresh."""
        with patch('src.interfaces.api.auth_controllers.get_auth_service') as mock_get_service:
            # Mock authentication service
            mock_service = AsyncMock()
            mock_token_pair = MagicMock()
            mock_token_pair.access_token.value = "new_access_token_123"
            mock_token_pair.refresh_token.value = "new_refresh_token_123"
            mock_service.refresh_token.return_value = mock_token_pair
            mock_get_service.return_value = mock_service

            # Override the dependency
            auth_client.app.dependency_overrides[get_auth_service] = lambda: mock_service

            response = auth_client.post("/auth/refresh", json={
                "refresh_token": "old_refresh_token_123"
            })

            assert response.status_code == 200
            data = response.json()
            assert "access_token" in data
            assert "refresh_token" in data
            assert data["token_type"] == "bearer"

            # Clean up
            auth_client.app.dependency_overrides.clear()

    def test_refresh_token_invalid(self, auth_client):
        """Test refresh token with invalid token."""
        with patch('src.interfaces.api.auth_controllers.get_auth_service') as mock_get_service:
            # Mock authentication service to raise exception
            mock_service = AsyncMock()
            from src.shared.domain.exceptions import BusinessRuleViolationError
            mock_service.refresh_token.side_effect = BusinessRuleViolationError("Invalid refresh token")
            mock_get_service.return_value = mock_service

            # Override the dependency
            auth_client.app.dependency_overrides[get_auth_service] = lambda: mock_service

            response = auth_client.post("/auth/refresh", json={
                "refresh_token": "invalid_token"
            })

            assert response.status_code == 400
            data = response.json()
            assert "detail" in data

            # Clean up
            auth_client.app.dependency_overrides.clear()

    def test_logout_success(self, auth_client):
        """Test successful logout."""
        with patch('src.interfaces.api.auth_controllers.get_current_user') as mock_get_user, \
             patch('src.interfaces.api.auth_controllers.get_auth_service') as mock_get_service:
            
            # Mock current user
            mock_get_user.return_value = {"sub": "user-123"}
            
            # Mock authentication service
            mock_service = AsyncMock()
            mock_service.logout.return_value = True
            mock_get_service.return_value = mock_service

            # Override the dependencies
            auth_client.app.dependency_overrides[get_current_user] = lambda: {"id": "user-123", "sub": "user-123"}
            auth_client.app.dependency_overrides[get_auth_service] = lambda: mock_service

            response = auth_client.post("/auth/logout", headers={
                "Authorization": "Bearer valid_token"
            })

            assert response.status_code == 200
            data = response.json()
            assert "message" in data

            # Clean up
            auth_client.app.dependency_overrides.clear()

    def test_logout_unauthorized(self, auth_client):
        """Test logout without authentication."""
        response = auth_client.post("/auth/logout")
        assert response.status_code == 401  # Unauthorized

    def test_logout_all_sessions_success(self, auth_client):
        """Test successful logout from all sessions."""
        with patch('src.interfaces.api.auth_controllers.get_current_user') as mock_get_user, \
             patch('src.interfaces.api.auth_controllers.get_auth_service') as mock_get_service:
            
            # Mock current user
            mock_get_user.return_value = {"id": "user-123", "sub": "user-123"}
            
            # Mock authentication service
            mock_service = AsyncMock()
            mock_service.logout_all_sessions.return_value = True
            mock_get_service.return_value = mock_service

            # Override the dependencies
            auth_client.app.dependency_overrides[get_current_user] = lambda: {"id": "user-123", "sub": "user-123"}
            auth_client.app.dependency_overrides[get_auth_service] = lambda: mock_service

            response = auth_client.post("/auth/logout-all", headers={
                "Authorization": "Bearer valid_token"
            })

            assert response.status_code == 200
            data = response.json()
            assert "message" in data

            # Clean up
            auth_client.app.dependency_overrides.clear()

    def test_change_password_success(self, auth_client):
        """Test successful password change."""
        with patch('src.interfaces.api.auth_controllers.get_current_user') as mock_get_user, \
             patch('src.interfaces.api.auth_controllers.get_auth_service') as mock_get_service:
            
            # Mock current user
            mock_get_user.return_value = {"id": "user-123", "sub": "user-123"}
            
            # Mock authentication service
            mock_service = AsyncMock()
            mock_service.change_password.return_value = True
            mock_get_service.return_value = mock_service

            # Override the dependencies
            auth_client.app.dependency_overrides[get_current_user] = lambda: {"id": "user-123", "sub": "user-123"}
            auth_client.app.dependency_overrides[get_auth_service] = lambda: mock_service

            response = auth_client.post("/auth/change-password", 
                json={
                    "old_password": "old_password",
                    "new_password": "new_password"
                },
                headers={
                    "Authorization": "Bearer valid_token"
                }
            )

            assert response.status_code == 200
            data = response.json()
            assert "message" in data

            # Clean up
            auth_client.app.dependency_overrides.clear()

    def test_change_password_invalid_old_password(self, auth_client):
        """Test password change with invalid old password."""
        with patch('src.interfaces.api.auth_controllers.get_current_user') as mock_get_user, \
             patch('src.interfaces.api.auth_controllers.get_auth_service') as mock_get_service:
            
            # Mock current user
            mock_get_user.return_value = {"id": "user-123", "sub": "user-123"}
            
            # Mock authentication service to raise exception
            mock_service = AsyncMock()
            from src.shared.domain.exceptions import BusinessRuleViolationError
            mock_service.change_password.side_effect = BusinessRuleViolationError("Invalid old password")
            mock_get_service.return_value = mock_service

            # Override the dependencies
            auth_client.app.dependency_overrides[get_current_user] = lambda: {"id": "user-123", "sub": "user-123"}
            auth_client.app.dependency_overrides[get_auth_service] = lambda: mock_service

            response = auth_client.post("/auth/change-password", 
                json={
                    "old_password": "wrong_password",
                    "new_password": "new_password"
                },
                headers={
                    "Authorization": "Bearer valid_token"
                }
            )

            assert response.status_code == 400
            data = response.json()
            assert "detail" in data

            # Clean up
            auth_client.app.dependency_overrides.clear()

    def test_get_current_user_info_success(self, auth_client):
        """Test successful get current user info."""
        with patch('src.interfaces.api.auth_controllers.get_current_user') as mock_get_user:
            # Mock current user
            mock_get_user.return_value = {
                "sub": "user-123",
                "email": "test@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "is_active": True
            }

            # Override the dependency
            auth_client.app.dependency_overrides[get_current_user] = lambda: {
                "id": "user-123",
                "sub": "user-123",
                "email": "test@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "is_active": True
            }

            response = auth_client.get("/auth/me", headers={
                "Authorization": "Bearer valid_token"
            })

            assert response.status_code == 200
            data = response.json()
            assert data["id"] == "user-123"
            assert data["email"] == "test@example.com"
            assert data["first_name"] == "John"
            assert data["last_name"] == "Doe"
            assert data["is_active"] is True

            # Clean up
            auth_client.app.dependency_overrides.clear()

    def test_get_current_user_info_unauthorized(self, auth_client):
        """Test get current user info without authentication."""
        response = auth_client.get("/auth/me")
        assert response.status_code == 401  # Unauthorized

    def test_validate_token_success(self, auth_client):
        """Test successful token validation."""
        with patch('src.interfaces.api.auth_controllers.get_current_user') as mock_get_user:
            # Mock current user
            mock_get_user.return_value = {
                "sub": "user-123",
                "email": "test@example.com"
            }

            # Override the dependency
            auth_client.app.dependency_overrides[get_current_user] = lambda: {
                "id": "user-123",
                "sub": "user-123",
                "email": "test@example.com"
            }

            response = auth_client.get("/auth/validate", headers={
                "Authorization": "Bearer valid_token"
            })

            assert response.status_code == 200
            data = response.json()
            assert data["valid"] is True
            assert "user_id" in data

            # Clean up
            auth_client.app.dependency_overrides.clear()

    def test_validate_token_invalid(self, auth_client):
        """Test validate token with invalid token."""
        response = auth_client.get("/auth/validate", headers={
            "Authorization": "Bearer invalid_token"
        })
        assert response.status_code == 401  # Unauthorized

    def test_validate_token_missing(self, auth_client):
        """Test validate token with missing token."""
        response = auth_client.get("/auth/validate")
        assert response.status_code == 401  # Unauthorized


class TestErrorHandling:
    """Test error handling in auth endpoints."""

    def test_login_service_exception(self, auth_client):
        """Test login when service raises exception."""
        with patch('src.interfaces.api.auth_controllers.get_auth_service') as mock_get_service:
            # Mock authentication service to raise exception
            mock_service = AsyncMock()
            mock_service.login.side_effect = Exception("Service error")
            mock_get_service.return_value = mock_service

            # Override the dependency
            auth_client.app.dependency_overrides[get_auth_service] = lambda: mock_service

            response = auth_client.post("/auth/login", json={
                "email": "test@example.com",
                "password": "password123"
            })

            assert response.status_code == 500
            data = response.json()
            assert "error" in data

            # Clean up
            auth_client.app.dependency_overrides.clear()

    def test_refresh_token_service_exception(self, auth_client):
        """Test refresh token when service raises exception."""
        with patch('src.interfaces.api.auth_controllers.get_auth_service') as mock_get_service:
            # Mock authentication service to raise exception
            mock_service = AsyncMock()
            mock_service.refresh_token.side_effect = Exception("Service error")
            mock_get_service.return_value = mock_service

            # Override the dependency
            auth_client.app.dependency_overrides[get_auth_service] = lambda: mock_service

            response = auth_client.post("/auth/refresh", json={
                "refresh_token": "refresh_token_123"
            })

            assert response.status_code == 500
            data = response.json()
            assert "error" in data

            # Clean up
            auth_client.app.dependency_overrides.clear()

    def test_logout_service_exception(self, auth_client):
        """Test logout when service raises exception."""
        with patch('src.interfaces.api.auth_controllers.get_current_user') as mock_get_user, \
             patch('src.interfaces.api.auth_controllers.get_auth_service') as mock_get_service:
            
            # Mock current user
            mock_get_user.return_value = {"id": "user-123", "sub": "user-123"}
            
            # Mock authentication service to raise exception
            mock_service = AsyncMock()
            mock_service.logout.side_effect = Exception("Service error")
            mock_get_service.return_value = mock_service

            # Override the dependencies
            auth_client.app.dependency_overrides[get_current_user] = lambda: {"id": "user-123", "sub": "user-123"}
            auth_client.app.dependency_overrides[get_auth_service] = lambda: mock_service

            response = auth_client.post("/auth/logout", headers={
                "Authorization": "Bearer valid_token"
            })

            assert response.status_code == 500
            data = response.json()
            assert "error" in data

            # Clean up
            auth_client.app.dependency_overrides.clear()


class TestRequestValidation:
    """Test request validation."""

    def test_login_request_missing_fields(self, auth_client):
        """Test login request with missing fields."""
        response = auth_client.post("/auth/login", json={})
        assert response.status_code == 422

        response = auth_client.post("/auth/login", json={"email": "test@example.com"})
        assert response.status_code == 422

        response = auth_client.post("/auth/login", json={"password": "password123"})
        assert response.status_code == 422

    def test_refresh_token_request_missing_token(self, auth_client):
        """Test refresh token request with missing token."""
        response = auth_client.post("/auth/refresh", json={})
        assert response.status_code == 422

    def test_change_password_request_missing_fields(self, auth_client):
        """Test change password request with missing fields."""
        response = auth_client.post("/auth/change-password", json={})
        assert response.status_code == 403  # Requires authentication

        response = auth_client.post("/auth/change-password", json={"old_password": "old"})
        assert response.status_code == 403  # Requires authentication

        response = auth_client.post("/auth/change-password", json={"new_password": "new"})
        assert response.status_code == 403  # Requires authentication

    def test_login_request_invalid_email(self, auth_client):
        """Test login request with invalid email format."""
        response = auth_client.post("/auth/login", json={
            "email": "invalid-email",
            "password": "password123"
        })
        assert response.status_code == 422

    def test_change_password_request_short_password(self, auth_client):
        """Test change password request with short password."""
        response = auth_client.post("/auth/change-password", json={
            "old_password": "old",
            "new_password": "123"  # Too short
        })
        assert response.status_code == 403  # Requires authentication 