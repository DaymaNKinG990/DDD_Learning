"""Tests for auth.application.services module."""

import pytest
from unittest.mock import Mock, AsyncMock
from datetime import datetime, timedelta, timezone
from jose import jwt

from src.auth.application.services import AuthenticationService
from src.auth.domain.entities import TokenPair, UserSession
from src.auth.domain.events import (
    FailedLoginAttempt,
    PasswordChanged,
    UserLoggedIn,
    UserLoggedOut,
)
from src.auth.domain.value_objects import (
    AccessToken,
    RefreshToken,
    TokenId,
    TokenType,
)
from src.shared.application.event_handlers import EventHandler
from src.shared.domain.exceptions import BusinessRuleViolationError, EntityNotFoundError
from src.users.domain.entities import User
from src.users.domain.value_objects import Email, UserId


class TestAuthenticationService:
    """Test AuthenticationService."""

    @pytest.fixture
    def user_repository(self):
        """Create user repository mock."""
        return Mock()

    @pytest.fixture
    def token_repository(self):
        """Create token repository mock."""
        return Mock()

    @pytest.fixture
    def session_repository(self):
        """Create session repository mock."""
        return Mock()

    @pytest.fixture
    def event_handler(self):
        """Create event handler mock."""
        return Mock(spec=EventHandler)

    @pytest.fixture
    def service(self, user_repository, token_repository, session_repository, event_handler):
        """Create authentication service instance."""
        return AuthenticationService(
            user_repository=user_repository,
            token_repository=token_repository,
            session_repository=session_repository,
            secret_key="test-secret-key",
            algorithm="HS256",
            access_token_expire_minutes=30,
            refresh_token_expire_days=7,
            event_handler=event_handler,
        )

    @pytest.fixture
    def sample_user(self):
        """Create sample user."""
        user = Mock(spec=User)
        user.id = UserId("user-123")
        user.email = Email("test@example.com")
        # Create a proper password hash for "password"
        service = AuthenticationService(
            user_repository=Mock(),
            token_repository=Mock(),
            session_repository=Mock(),
            secret_key="test-secret-key",
        )
        user.password_hash = service.get_password_hash("password")
        user.is_active = True
        return user

    def test_verify_password_valid(self, service):
        """Test password verification with valid password."""
        hash_result = service.get_password_hash("password")
        result = service.verify_password("password", hash_result)
        assert result is True

    def test_verify_password_invalid(self, service):
        """Test password verification with invalid password."""
        hash_result = service.get_password_hash("password")
        result = service.verify_password("wrong_password", hash_result)
        assert result is False

    def test_get_password_hash(self, service):
        """Test password hashing."""
        hash_result = service.get_password_hash("test_password")
        assert hash_result.startswith("$2b$")
        assert service.verify_password("test_password", hash_result) is True

    def test_create_access_token(self, service):
        """Test access token creation."""
        data = {"sub": "user-123", "email": "test@example.com"}
        token = service.create_access_token(data)
        
        # Verify token can be decoded
        decoded = jwt.decode(token, service.secret_key, algorithms=[service.algorithm])
        assert decoded["sub"] == "user-123"
        assert decoded["email"] == "test@example.com"

    def test_create_access_token_with_expires_delta(self, service):
        """Test access token creation with custom expiration."""
        data = {"sub": "user-123"}
        expires_delta = timedelta(minutes=60)
        token = service.create_access_token(data, expires_delta)
        
        decoded = jwt.decode(token, service.secret_key, algorithms=[service.algorithm])
        exp_timestamp = decoded["exp"]
        # Check that expiration is approximately 60 minutes from now
        current_time = datetime.now(timezone.utc).timestamp()
        # Allow some tolerance for test execution time
        assert exp_timestamp - current_time >= 3500  # 58+ minutes in seconds

    def test_create_refresh_token(self, service):
        """Test refresh token creation."""
        data = {"sub": "user-123", "type": "refresh"}
        token = service.create_refresh_token(data)
        
        decoded = jwt.decode(token, service.secret_key, algorithms=[service.algorithm])
        assert decoded["sub"] == "user-123"
        assert decoded["type"] == "refresh"

    def test_verify_token_valid(self, service):
        """Test token verification with valid token."""
        data = {"sub": "user-123", "email": "test@example.com"}
        token = service.create_access_token(data)
        
        result = service.verify_token(token)
        assert result is not None
        assert result["sub"] == "user-123"
        assert result["email"] == "test@example.com"

    def test_verify_token_invalid(self, service):
        """Test token verification with invalid token."""
        result = service.verify_token("invalid_token")
        assert result is None

    @pytest.mark.asyncio
    async def test_authenticate_user_valid(self, service, user_repository, sample_user):
        """Test user authentication with valid credentials."""
        user_repository.get_by_email = AsyncMock(return_value=sample_user)
        
        result = await service.authenticate_user("test@example.com", "password")
        assert result == sample_user
        user_repository.get_by_email.assert_called_once_with(Email("test@example.com"))

    @pytest.mark.asyncio
    async def test_authenticate_user_invalid_password(self, service, user_repository, sample_user):
        """Test user authentication with invalid password."""
        user_repository.get_by_email = AsyncMock(return_value=sample_user)
        
        result = await service.authenticate_user("test@example.com", "wrong_password")
        assert result is None

    @pytest.mark.asyncio
    async def test_authenticate_user_user_not_found(self, service, user_repository):
        """Test user authentication when user not found."""
        user_repository.get_by_email = AsyncMock(return_value=None)
        
        result = await service.authenticate_user("nonexistent@example.com", "password")
        assert result is None

    @pytest.mark.asyncio
    async def test_authenticate_user_inactive_user(self, service, user_repository, sample_user):
        """Test user authentication with inactive user."""
        sample_user.is_active = False
        user_repository.get_by_email = AsyncMock(return_value=sample_user)
        
        result = await service.authenticate_user("test@example.com", "password")
        assert result is None

    @pytest.mark.asyncio
    async def test_login_successful(self, service, user_repository, token_repository, session_repository, event_handler, sample_user):
        """Test successful login."""
        user_repository.get_by_email = AsyncMock(return_value=sample_user)
        
        # Create a proper TokenPair mock
        token_pair_mock = Mock(spec=TokenPair)
        token_pair_mock.access_token = Mock(spec=AccessToken)
        token_pair_mock.refresh_token = Mock(spec=RefreshToken)
        token_repository.save = AsyncMock(return_value=token_pair_mock)
        
        session_repository.save = AsyncMock()
        event_handler.handle = AsyncMock()
        
        result = await service.login("test@example.com", "password", "192.168.1.1", "Mozilla/5.0")
        
        assert isinstance(result, TokenPair)
        assert result.access_token is not None
        assert result.refresh_token is not None
        token_repository.save.assert_called()
        session_repository.save.assert_called()
        event_handler.handle.assert_called_once()
        
        # Verify event was called with UserLoggedIn
        call_args = event_handler.handle.call_args[0][0]
        assert isinstance(call_args, UserLoggedIn)
        assert call_args.user_id == str(sample_user.id)
        assert call_args.ip_address == "192.168.1.1"
        assert call_args.user_agent == "Mozilla/5.0"

    @pytest.mark.asyncio
    async def test_login_failed_authentication(self, service, user_repository, event_handler):
        """Test login with failed authentication."""
        user_repository.get_by_email = AsyncMock(return_value=None)
        event_handler.handle = AsyncMock()
        
        with pytest.raises(BusinessRuleViolationError, match="Invalid email or password"):
            await service.login("test@example.com", "wrong_password", "192.168.1.1", "Mozilla/5.0")
        
        event_handler.handle.assert_called_once()
        
        # Verify event was called with FailedLoginAttempt
        call_args = event_handler.handle.call_args[0][0]
        assert isinstance(call_args, FailedLoginAttempt)
        assert call_args.email == "test@example.com"
        assert call_args.ip_address == "192.168.1.1"
        assert call_args.user_agent == "Mozilla/5.0"
        assert call_args.reason == "Invalid credentials"

    @pytest.mark.asyncio
    async def test_refresh_token_successful(self, service, token_repository, user_repository, event_handler, sample_user):
        """Test successful token refresh."""
        # Create a valid refresh token
        token_data = {"sub": str(sample_user.id), "type": "refresh"}
        refresh_token = service.create_refresh_token(token_data)
        
        # Create a proper TokenPair mock
        token_pair_mock = Mock(spec=TokenPair)
        token_pair_mock.access_token = Mock(spec=AccessToken)
        token_pair_mock.refresh_token = Mock(spec=RefreshToken)
        
        token_repository.get_by_refresh_token = AsyncMock(return_value=token_pair_mock)
        token_repository.delete = AsyncMock()
        token_repository.save = AsyncMock(return_value=token_pair_mock)
        user_repository.get_by_id = AsyncMock(return_value=sample_user)
        event_handler.handle = AsyncMock()
        
        result = await service.refresh_token(refresh_token)
        
        assert isinstance(result, TokenPair)
        assert result.access_token is not None
        assert result.refresh_token is not None
        token_repository.save.assert_called()

    @pytest.mark.asyncio
    async def test_refresh_token_invalid_token(self, service):
        """Test token refresh with invalid token."""
        with pytest.raises(BusinessRuleViolationError, match="Invalid refresh token"):
            await service.refresh_token("invalid_token")

    @pytest.mark.asyncio
    async def test_logout_successful(self, service, token_repository, session_repository, event_handler):
        """Test successful logout."""
        token_data = {"sub": "user-123", "jti": "token-123"}
        access_token = service.create_access_token(token_data)
        
        # Create a proper TokenPair mock
        token_pair_mock = Mock(spec=TokenPair)
        token_pair_mock.revoke = Mock()
        token_pair_mock.user_id = UserId("user-123")
        token_pair_mock.id = TokenId("token-123")
        refresh_token_mock = Mock(spec=RefreshToken)
        refresh_token_mock.value = "refresh_token_value"
        token_pair_mock.refresh_token = refresh_token_mock
        
        token_repository.get_by_access_token = AsyncMock(return_value=token_pair_mock)
        token_repository.save = AsyncMock()
        session_repository.get_by_refresh_token = AsyncMock(return_value=Mock(spec=UserSession))
        session_repository.save = AsyncMock()
        event_handler.handle = AsyncMock()
        
        result = await service.logout(access_token)
        
        assert result is True
        token_repository.save.assert_called()
        event_handler.handle.assert_called_once()
        
        # Verify event was called with UserLoggedOut
        call_args = event_handler.handle.call_args[0][0]
        assert isinstance(call_args, UserLoggedOut)

    @pytest.mark.asyncio
    async def test_logout_token_not_found(self, service, token_repository):
        """Test logout with token not found."""
        token_data = {"sub": "user-123", "jti": "token-123"}
        access_token = service.create_access_token(token_data)
        
        token_repository.get_by_access_token = AsyncMock(return_value=None)
        
        result = await service.logout(access_token)
        assert result is False

    @pytest.mark.asyncio
    async def test_logout_all_sessions_successful(self, service, session_repository, event_handler):
        """Test successful logout from all sessions."""
        user_repository = Mock()
        user_mock = Mock(spec=User)
        user_mock.id = UserId("user-123")
        user_repository.get_by_id = AsyncMock(return_value=user_mock)
        service.user_repository = user_repository
        
        token_repository = Mock()
        token_repository.revoke_all_user_tokens = AsyncMock()
        service.token_repository = token_repository
        
        session_repository.get_by_user_id = AsyncMock(return_value=[Mock(), Mock()])
        session_repository.delete = AsyncMock(return_value=True)
        session_repository.deactivate_all_user_sessions = AsyncMock()
        event_handler.handle = AsyncMock()
        
        result = await service.logout_all_sessions("user-123")
        
        assert result is True
        session_repository.deactivate_all_user_sessions.assert_called()

    @pytest.mark.asyncio
    async def test_change_password_successful(self, service, user_repository, event_handler, sample_user):
        """Test successful password change."""
        user_repository.get_by_id = AsyncMock(return_value=sample_user)
        user_repository.save = AsyncMock()
        
        token_repository = Mock()
        token_repository.revoke_all_user_tokens = AsyncMock()
        service.token_repository = token_repository
        
        session_repository = Mock()
        session_repository.deactivate_all_user_sessions = AsyncMock()
        service.session_repository = session_repository
        
        event_handler.handle = AsyncMock()
        
        result = await service.change_password("user-123", "password", "new_password")
        
        assert result is True
        user_repository.save.assert_called()
        event_handler.handle.assert_called_once()
        
        # Verify event was called with PasswordChanged
        call_args = event_handler.handle.call_args[0][0]
        assert isinstance(call_args, PasswordChanged)
        assert call_args.user_id == str(sample_user.id)

    @pytest.mark.asyncio
    async def test_change_password_user_not_found(self, service, user_repository):
        """Test password change with user not found."""
        user_repository.get_by_id = AsyncMock(return_value=None)
        
        with pytest.raises(EntityNotFoundError, match="User with ID user-123 not found"):
            await service.change_password("user-123", "password", "new_password")

    @pytest.mark.asyncio
    async def test_change_password_invalid_old_password(self, service, user_repository, sample_user):
        """Test password change with invalid old password."""
        user_repository.get_by_id = AsyncMock(return_value=sample_user)
        
        with pytest.raises(BusinessRuleViolationError, match="Invalid old password"):
            await service.change_password("user-123", "wrong_password", "new_password")

    @pytest.mark.asyncio
    async def test_get_current_user_successful(self, service, user_repository, sample_user):
        """Test getting current user successfully."""
        token_data = {"sub": str(sample_user.id), "type": "access"}
        access_token = service.create_access_token(token_data)
        
        user_repository.get_by_id = AsyncMock(return_value=sample_user)
        
        # Mock token repository to return valid token pair
        token_repository = Mock()
        token_pair_mock = Mock(spec=TokenPair)
        token_pair_mock.is_valid = True
        token_repository.get_by_access_token = AsyncMock(return_value=token_pair_mock)
        service.token_repository = token_repository
        
        result = await service.get_current_user(access_token)
        
        assert result == sample_user
        user_repository.get_by_id.assert_called_once_with(UserId("user-123"))

    @pytest.mark.asyncio
    async def test_get_current_user_invalid_token(self, service):
        """Test getting current user with invalid token."""
        result = await service.get_current_user("invalid_token")
        assert result is None

    @pytest.mark.asyncio
    async def test_get_current_user_user_not_found(self, service, user_repository):
        """Test getting current user when user not found."""
        token_data = {"sub": "user-123"}
        access_token = service.create_access_token(token_data)
        
        user_repository.get_by_id = AsyncMock(return_value=None)
        
        result = await service.get_current_user(access_token)
        assert result is None

    @pytest.mark.asyncio
    async def test_cleanup_expired_tokens(self, service, token_repository):
        """Test cleanup of expired tokens."""
        token_repository.delete_expired_tokens = AsyncMock(return_value=2)
        session_repository = Mock()
        session_repository.delete_expired_sessions = AsyncMock(return_value=1)
        service.session_repository = session_repository
        
        result = await service.cleanup_expired_tokens()
        
        assert result == 3  # 2 tokens + 1 session
        token_repository.delete_expired_tokens.assert_called_once()
        session_repository.delete_expired_sessions.assert_called_once() 