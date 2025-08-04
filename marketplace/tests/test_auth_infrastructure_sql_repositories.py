"""Tests for auth infrastructure SQL repositories."""

# Python imports
import pytest
from unittest.mock import AsyncMock, Mock, patch
from datetime import datetime, timezone, timedelta
from typing import List

# Local imports
from src.auth.infrastructure.sql_repositories import SQLTokenRepository, SQLSessionRepository
from src.auth.domain.entities import TokenPair, UserSession
from src.auth.domain.value_objects import TokenId, TokenType, AccessToken, RefreshToken
from src.users.domain.value_objects import UserId
from src.auth.infrastructure.models import TokenPairModel, UserSessionModel


class TestSQLTokenRepository:
    """Test cases for SQLTokenRepository."""

    @pytest.fixture
    def mock_session(self):
        """Create mock SQLAlchemy session."""
        return AsyncMock()

    @pytest.fixture
    def repository(self, mock_session):
        """Create SQLTokenRepository instance."""
        return SQLTokenRepository(mock_session)

    @pytest.fixture
    def token_pair(self):
        """Create test token pair."""
        return TokenPair(
            id=TokenId("token-123"),
            user_id=UserId("user-123"),
            access_token=AccessToken.create("access-token-123", 30),
            refresh_token=RefreshToken.create("refresh-token-123", 7),
            token_type=TokenType.ACCESS,
            is_revoked=False
        )

    @pytest.fixture
    def token_pair_model(self):
        """Create test token pair model."""
        return TokenPairModel(
            id="token-123",
            user_id="user-123",
            access_token="access-token-123",
            refresh_token="refresh-token-123",
            token_type=TokenType.ACCESS.value,
            is_revoked=False,
            access_token_expires_at=datetime.now(timezone.utc) + timedelta(minutes=30),
            refresh_token_expires_at=datetime.now(timezone.utc) + timedelta(days=7),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

    @pytest.mark.asyncio
    async def test_save_token_pair(self, repository, token_pair, token_pair_model):
        """Test saving token pair."""
        expected_entity = TokenPair(
            id=TokenId("token-123"),
            user_id=UserId("user-123"),
            access_token=AccessToken.create("access-token-123", 30),
            refresh_token=RefreshToken.create("refresh-token-123", 7),
            token_type=TokenType.ACCESS,
            is_revoked=False
        )
        
        with patch.object(repository, 'save', return_value=expected_entity):
            result = await repository.save(token_pair)
            
            assert result.id.value == "token-123"
            assert result.user_id.value == "user-123"
            assert result.access_token.value == "access-token-123"
            assert result.refresh_token.value == "refresh-token-123"
            assert result.token_type == TokenType.ACCESS
            assert result.is_revoked is False

    @pytest.mark.asyncio
    async def test_get_by_id_found(self, repository, token_pair_model):
        """Test getting token pair by ID when found."""
        expected_entity = TokenPair(
            id=TokenId("token-123"),
            user_id=UserId("user-123"),
            access_token=AccessToken.create("access-token-123", 30),
            refresh_token=RefreshToken.create("refresh-token-123", 7),
            token_type=TokenType.ACCESS,
            is_revoked=False
        )
        
        with patch.object(repository, 'get_by_id', return_value=expected_entity):
            result = await repository.get_by_id(TokenId("token-123"))
            
            assert result is not None
            assert result.id.value == "token-123"
            assert result.user_id.value == "user-123"

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, repository):
        """Test getting token pair by ID when not found."""
        with patch.object(repository, 'get_by_id', return_value=None):
            result = await repository.get_by_id(TokenId("token-123"))
            
            assert result is None

    @pytest.mark.asyncio
    async def test_get_by_user_id(self, repository, token_pair_model):
        """Test getting token pairs by user ID."""
        expected_entity = TokenPair(
            id=TokenId("token-123"),
            user_id=UserId("user-123"),
            access_token=AccessToken.create("access-token-123", 30),
            refresh_token=RefreshToken.create("refresh-token-123", 7),
            token_type=TokenType.ACCESS,
            is_revoked=False
        )
        
        with patch.object(repository, '_model_to_entity', return_value=expected_entity):
            with patch.object(repository.session, 'execute') as mock_execute:
                mock_result = Mock()
                mock_result.scalars.return_value.all.return_value = [token_pair_model]
                mock_execute.return_value = mock_result
                
                result = await repository.get_by_user_id(UserId("user-123"))
                
                assert len(result) == 1
                assert result[0].user_id.value == "user-123"

    @pytest.mark.asyncio
    async def test_get_by_access_token_found(self, repository, token_pair_model):
        """Test getting token pair by access token when found."""
        with patch.object(repository.session, 'execute') as mock_execute:
            mock_result = Mock()
            mock_result.scalar_one_or_none.return_value = token_pair_model
            mock_execute.return_value = mock_result
            
            result = await repository.get_by_access_token("access-token-123")
            
            assert result is not None
            assert result.access_token.value == "access-token-123"

    @pytest.mark.asyncio
    async def test_get_by_access_token_not_found(self, repository):
        """Test getting token pair by access token when not found."""
        with patch.object(repository.session, 'execute') as mock_execute:
            mock_result = Mock()
            mock_result.scalar_one_or_none.return_value = None
            mock_execute.return_value = mock_result
            
            result = await repository.get_by_access_token("access-token-123")
            
            assert result is None

    @pytest.mark.asyncio
    async def test_get_by_refresh_token_found(self, repository, token_pair_model):
        """Test getting token pair by refresh token when found."""
        with patch.object(repository.session, 'execute') as mock_execute:
            mock_result = Mock()
            mock_result.scalar_one_or_none.return_value = token_pair_model
            mock_execute.return_value = mock_result
            
            result = await repository.get_by_refresh_token("refresh-token-123")
            
            assert result is not None
            assert result.refresh_token.value == "refresh-token-123"

    @pytest.mark.asyncio
    async def test_get_by_refresh_token_not_found(self, repository):
        """Test getting token pair by refresh token when not found."""
        with patch.object(repository.session, 'execute') as mock_execute:
            mock_result = Mock()
            mock_result.scalar_one_or_none.return_value = None
            mock_execute.return_value = mock_result
            
            result = await repository.get_by_refresh_token("refresh-token-123")
            
            assert result is None

    @pytest.mark.asyncio
    async def test_revoke_token_success(self, repository):
        """Test revoking token successfully."""
        with patch.object(repository.session, 'execute') as mock_execute:
            mock_result = Mock()
            mock_result.rowcount = 1
            mock_execute.return_value = mock_result
            
            result = await repository.revoke_token(TokenId("token-123"))
            
            assert result is True

    @pytest.mark.asyncio
    async def test_revoke_token_not_found(self, repository):
        """Test revoking token when not found."""
        with patch.object(repository.session, 'execute') as mock_execute:
            mock_result = Mock()
            mock_result.rowcount = 0
            mock_execute.return_value = mock_result
            
            result = await repository.revoke_token(TokenId("token-123"))
            
            assert result is False

    @pytest.mark.asyncio
    async def test_revoke_all_user_tokens_success(self, repository):
        """Test revoking all user tokens successfully."""
        with patch.object(repository.session, 'execute') as mock_execute:
            mock_result = Mock()
            mock_result.rowcount = 3
            mock_execute.return_value = mock_result
            
            result = await repository.revoke_all_user_tokens(UserId("user-123"))
            
            assert result is True

    @pytest.mark.asyncio
    async def test_delete_expired_tokens(self, repository):
        """Test deleting expired tokens."""
        with patch.object(repository.session, 'execute') as mock_execute:
            mock_result = Mock()
            mock_scalars = Mock()
            mock_scalars.all.return_value = [Mock(), Mock(), Mock(), Mock(), Mock()]  # 5 expired tokens
            mock_result.scalars.return_value = mock_scalars
            mock_execute.return_value = mock_result
            
            result = await repository.delete_expired_tokens()
            
            assert result == 5

    def test_model_to_entity(self, repository, token_pair_model):
        """Test converting model to entity."""
        result = repository._model_to_entity(token_pair_model)
        
        assert result.id.value == "token-123"
        assert result.user_id.value == "user-123"
        assert result.access_token.value == "access-token-123"
        assert result.refresh_token.value == "refresh-token-123"
        assert result.token_type == TokenType.ACCESS
        assert result.is_revoked is False


class TestSQLSessionRepository:
    """Test cases for SQLSessionRepository."""

    @pytest.fixture
    def mock_session(self):
        """Create mock SQLAlchemy session."""
        return AsyncMock()

    @pytest.fixture
    def repository(self, mock_session):
        """Create SQLSessionRepository instance."""
        return SQLSessionRepository(mock_session)

    @pytest.fixture
    def user_session(self):
        """Create test user session."""
        return UserSession(
            id=TokenId("session-123"),
            user_id=UserId("user-123"),
            refresh_token=RefreshToken.create("refresh-token-123", 7),
            ip_address="127.0.0.1",
            user_agent="test-agent",
            is_active=True
        )

    @pytest.fixture
    def user_session_model(self):
        """Create test user session model."""
        return UserSessionModel(
            id="session-123",
            user_id="user-123",
            refresh_token="refresh-token-123",
            ip_address="127.0.0.1",
            user_agent="test-agent",
            is_active=True,
            last_activity=datetime.now(timezone.utc),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )

    @pytest.mark.asyncio
    async def test_save_user_session(self, repository, user_session, user_session_model):
        """Test saving user session."""
        expected_entity = UserSession(
            id=TokenId("session-123"),
            user_id=UserId("user-123"),
            refresh_token=RefreshToken.create("refresh-token-123", 7),
            ip_address="127.0.0.1",
            user_agent="test-agent",
            is_active=True
        )
        
        with patch.object(repository, 'save', return_value=expected_entity):
            result = await repository.save(user_session)
            
            assert result.id.value == "session-123"
            assert result.user_id.value == "user-123"
            assert result.refresh_token.value == "refresh-token-123"
            assert result.ip_address == "127.0.0.1"
            assert result.user_agent == "test-agent"
            assert result.is_active is True

    @pytest.mark.asyncio
    async def test_get_by_id_found(self, repository, user_session_model):
        """Test getting user session by ID when found."""
        expected_entity = UserSession(
            id=TokenId("session-123"),
            user_id=UserId("user-123"),
            refresh_token=RefreshToken.create("refresh-token-123", 7),
            ip_address="127.0.0.1",
            user_agent="test-agent",
            is_active=True
        )
        
        with patch.object(repository, 'get_by_id', return_value=expected_entity):
            result = await repository.get_by_id(TokenId("session-123"))
            
            assert result is not None
            assert result.id.value == "session-123"
            assert result.user_id.value == "user-123"

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, repository):
        """Test getting user session by ID when not found."""
        with patch.object(repository, 'get_by_id', return_value=None):
            result = await repository.get_by_id(TokenId("session-123"))
            
            assert result is None

    @pytest.mark.asyncio
    async def test_get_by_user_id(self, repository, user_session_model):
        """Test getting user sessions by user ID."""
        expected_entity = UserSession(
            id=TokenId("session-123"),
            user_id=UserId("user-123"),
            refresh_token=RefreshToken.create("refresh-token-123", 7),
            ip_address="127.0.0.1",
            user_agent="test-agent",
            is_active=True
        )
        
        with patch.object(repository, '_model_to_entity', return_value=expected_entity):
            with patch.object(repository.session, 'execute') as mock_execute:
                mock_result = Mock()
                mock_result.scalars.return_value.all.return_value = [user_session_model]
                mock_execute.return_value = mock_result
                
                result = await repository.get_by_user_id(UserId("user-123"))
                
                assert len(result) == 1
                assert result[0].user_id.value == "user-123"

    @pytest.mark.asyncio
    async def test_get_by_refresh_token_found(self, repository, user_session_model):
        """Test getting user session by refresh token when found."""
        with patch.object(repository.session, 'execute') as mock_execute:
            mock_result = Mock()
            mock_result.scalar_one_or_none.return_value = user_session_model
            mock_execute.return_value = mock_result
            
            result = await repository.get_by_refresh_token("refresh-token-123")
            
            assert result is not None
            assert result.refresh_token.value == "refresh-token-123"

    @pytest.mark.asyncio
    async def test_get_by_refresh_token_not_found(self, repository):
        """Test getting user session by refresh token when not found."""
        with patch.object(repository.session, 'execute') as mock_execute:
            mock_result = Mock()
            mock_result.scalar_one_or_none.return_value = None
            mock_execute.return_value = mock_result
            
            result = await repository.get_by_refresh_token("refresh-token-123")
            
            assert result is None

    @pytest.mark.asyncio
    async def test_deactivate_session_success(self, repository):
        """Test deactivating session successfully."""
        with patch.object(repository.session, 'execute') as mock_execute:
            mock_result = Mock()
            mock_result.rowcount = 1
            mock_execute.return_value = mock_result
            
            result = await repository.deactivate_session(TokenId("session-123"))
            
            assert result is True

    @pytest.mark.asyncio
    async def test_deactivate_session_not_found(self, repository):
        """Test deactivating session when not found."""
        with patch.object(repository.session, 'execute') as mock_execute:
            mock_result = Mock()
            mock_result.rowcount = 0
            mock_execute.return_value = mock_result
            
            result = await repository.deactivate_session(TokenId("session-123"))
            
            assert result is False

    @pytest.mark.asyncio
    async def test_deactivate_all_user_sessions_success(self, repository):
        """Test deactivating all user sessions successfully."""
        with patch.object(repository.session, 'execute') as mock_execute:
            mock_result = Mock()
            mock_result.rowcount = 3
            mock_execute.return_value = mock_result
            
            result = await repository.deactivate_all_user_sessions(UserId("user-123"))
            
            assert result is True

    @pytest.mark.asyncio
    async def test_update_session_activity_success(self, repository):
        """Test updating session activity successfully."""
        with patch.object(repository.session, 'execute') as mock_execute:
            mock_result = Mock()
            mock_result.rowcount = 1
            mock_execute.return_value = mock_result
            
            result = await repository.update_session_activity(TokenId("session-123"))
            
            assert result is True

    @pytest.mark.asyncio
    async def test_update_session_activity_not_found(self, repository):
        """Test updating session activity when not found."""
        with patch.object(repository.session, 'execute') as mock_execute:
            mock_result = Mock()
            mock_result.rowcount = 0
            mock_execute.return_value = mock_result
            
            result = await repository.update_session_activity(TokenId("session-123"))
            
            assert result is False

    @pytest.mark.asyncio
    async def test_delete_expired_sessions(self, repository):
        """Test deleting expired sessions."""
        with patch.object(repository.session, 'execute') as mock_execute:
            mock_result = Mock()
            mock_scalars = Mock()
            mock_scalars.all.return_value = [Mock(), Mock(), Mock()]  # 3 expired sessions
            mock_result.scalars.return_value = mock_scalars
            mock_execute.return_value = mock_result
            
            result = await repository.delete_expired_sessions()
            
            assert result == 3

    def test_model_to_entity(self, repository, user_session_model):
        """Test converting model to entity."""
        result = repository._model_to_entity(user_session_model)
        
        assert result.id.value == "session-123"
        assert result.user_id.value == "user-123"
        assert result.refresh_token.value == "refresh-token-123"
        assert result.ip_address == "127.0.0.1"
        assert result.user_agent == "test-agent"
        assert result.is_active is True 