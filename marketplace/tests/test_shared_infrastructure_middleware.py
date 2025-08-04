"""Tests for shared infrastructure middleware."""

# Python imports
import pytest
from unittest.mock import AsyncMock, Mock, patch, MagicMock
from fastapi import Request, Response
from starlette.middleware.base import RequestResponseEndpoint
from starlette.responses import JSONResponse
import time

# Local imports
from src.shared.infrastructure.middleware import (
    LoggingMiddleware,
    CacheMiddleware,
    RateLimitMiddleware,
    SecurityMiddleware
)


class TestLoggingMiddleware:
    """Test cases for LoggingMiddleware."""

    @pytest.fixture
    def middleware(self):
        """Create logging middleware."""
        return LoggingMiddleware(Mock())

    @pytest.fixture
    def mock_request(self):
        """Create mock request."""
        request = Mock(spec=Request)
        request.method = "GET"
        request.url.path = "/api/test"
        request.query_params = {}
        request.client.host = "127.0.0.1"
        request.headers = {"user-agent": "test-agent"}
        request.state = Mock()
        return request

    @pytest.fixture
    def mock_response(self):
        """Create mock response."""
        response = Mock(spec=Response)
        response.status_code = 200
        response.headers = {}
        return response

    @pytest.fixture
    def mock_call_next(self):
        """Create mock call_next function."""
        return AsyncMock()

    @pytest.mark.asyncio
    async def test_dispatch_success(self, middleware, mock_request, mock_response, mock_call_next):
        """Test successful request dispatch."""
        mock_call_next.return_value = mock_response
        
        with patch('uuid.uuid4', return_value="test-uuid-123"):
            with patch('src.shared.infrastructure.middleware.get_request_logger') as mock_logger:
                mock_logger_instance = Mock()
                mock_logger.return_value = mock_logger_instance
                
                result = await middleware.dispatch(mock_request, mock_call_next)
                
                assert result == mock_response
                assert mock_request.state.request_id == "test-uuid-123"
                assert result.headers["X-Request-ID"] == "test-uuid-123"
                mock_call_next.assert_called_once_with(mock_request)

    @pytest.mark.asyncio
    async def test_dispatch_with_user(self, middleware, mock_request, mock_response, mock_call_next):
        """Test dispatch with authenticated user."""
        mock_call_next.return_value = mock_response
        mock_user = Mock()
        mock_user.id = "user-123"
        mock_request.state.user = mock_user
        
        with patch('uuid.uuid4', return_value="test-uuid-123"):
            with patch('src.shared.infrastructure.middleware.get_request_logger') as mock_logger:
                mock_logger_instance = Mock()
                mock_logger.return_value = mock_logger_instance
                
                await middleware.dispatch(mock_request, mock_call_next)
                
                mock_logger.assert_called_once_with("test-uuid-123", "user-123")

    @pytest.mark.asyncio
    async def test_dispatch_exception(self, middleware, mock_request, mock_call_next):
        """Test dispatch with exception."""
        mock_call_next.side_effect = Exception("Test error")
        
        with patch('uuid.uuid4', return_value="test-uuid-123"):
            with patch('src.shared.infrastructure.middleware.get_request_logger') as mock_logger:
                mock_logger_instance = Mock()
                mock_logger.return_value = mock_logger_instance
                
                with pytest.raises(Exception, match="Test error"):
                    await middleware.dispatch(mock_request, mock_call_next)

    @pytest.mark.asyncio
    async def test_dispatch_logging_calls(self, middleware, mock_request, mock_response, mock_call_next):
        """Test that logging methods are called correctly."""
        mock_call_next.return_value = mock_response
        
        with patch('uuid.uuid4', return_value="test-uuid-123"):
            with patch('src.shared.infrastructure.middleware.get_request_logger') as mock_logger:
                mock_logger_instance = Mock()
                mock_logger.return_value = mock_logger_instance
                
                await middleware.dispatch(mock_request, mock_call_next)
                
                # Check that logger.info was called for request start
                mock_logger_instance.info.assert_called_once()
                # Check that log_request was called for completion
                mock_logger_instance.log_request.assert_called_once()


class TestCacheMiddleware:
    """Test cases for CacheMiddleware."""

    @pytest.fixture
    def middleware(self):
        """Create cache middleware."""
        return CacheMiddleware(
            Mock(),
            cache_prefix="test",
            default_ttl=300,
            cacheable_methods={"GET"},
            cacheable_paths={"/api/test"}
        )

    @pytest.fixture
    def mock_request(self):
        """Create mock request."""
        request = Mock(spec=Request)
        request.method = "GET"
        request.url.path = "/api/test"
        request.url.query = ""
        request.headers = {}
        # Mock query_params to be iterable
        request.query_params = Mock()
        request.query_params.items.return_value = [("param1", "value1"), ("param2", "value2")]
        return request

    @pytest.fixture
    def mock_response(self):
        """Create mock response."""
        response = Mock(spec=Response)
        response.status_code = 200
        response.body = b'{"test": "data"}'
        response.headers = {"content-type": "application/json"}
        return response

    @pytest.fixture
    def mock_call_next(self):
        """Create mock call_next function."""
        return AsyncMock()

    @pytest.mark.asyncio
    async def test_dispatch_cacheable_request(self, middleware, mock_request, mock_response, mock_call_next):
        """Test dispatch for cacheable request."""
        mock_call_next.return_value = mock_response
        
        with patch('src.shared.infrastructure.middleware.cache') as mock_cache:
            mock_cache.get_json = AsyncMock(return_value=None)
            mock_cache.set_json = AsyncMock(return_value=True)
            
            result = await middleware.dispatch(mock_request, mock_call_next)
            
            assert result == mock_response
            mock_call_next.assert_called_once_with(mock_request)
            mock_cache.get_json.assert_called_once()
            # set_json is called in _cache_response method, not directly in dispatch

    @pytest.mark.asyncio
    async def test_dispatch_cached_response(self, middleware, mock_request, mock_response, mock_call_next):
        """Test dispatch with cached response."""
        cached_response_data = {
            "content": '{"cached": "data"}',
            "status_code": 200,
            "headers": {"content-type": "application/json"},
            "media_type": "application/json"
        }
        
        with patch('src.shared.infrastructure.middleware.cache') as mock_cache:
            mock_cache.get_json = AsyncMock(return_value=cached_response_data)
            
            result = await middleware.dispatch(mock_request, mock_call_next)
            
            assert result.status_code == 200
            assert result.body == b'{"cached": "data"}'
            mock_call_next.assert_not_called()

    @pytest.mark.asyncio
    async def test_dispatch_non_cacheable_method(self, middleware, mock_request, mock_response, mock_call_next):
        """Test dispatch for non-cacheable method."""
        mock_request.method = "POST"
        mock_call_next.return_value = mock_response
        
        with patch('src.shared.infrastructure.middleware.cache') as mock_cache:
            result = await middleware.dispatch(mock_request, mock_call_next)
            
            assert result == mock_response
            mock_call_next.assert_called_once_with(mock_request)
            mock_cache.get.assert_not_called()

    @pytest.mark.asyncio
    async def test_dispatch_non_cacheable_path(self, middleware, mock_request, mock_response, mock_call_next):
        """Test dispatch for non-cacheable path."""
        mock_request.url.path = "/api/other"
        mock_call_next.return_value = mock_response
        
        with patch('src.shared.infrastructure.middleware.cache') as mock_cache:
            result = await middleware.dispatch(mock_request, mock_call_next)
            
            assert result == mock_response
            mock_call_next.assert_called_once_with(mock_request)
            mock_cache.get.assert_not_called()

    def test_is_cacheable_true(self, middleware, mock_request):
        """Test is_cacheable returns True for cacheable request."""
        result = middleware._is_cacheable(mock_request)
        assert result is True

    def test_is_cacheable_false_method(self, middleware, mock_request):
        """Test is_cacheable returns False for non-cacheable method."""
        mock_request.method = "POST"
        result = middleware._is_cacheable(mock_request)
        assert result is False

    def test_is_cacheable_false_path(self, middleware, mock_request):
        """Test is_cacheable returns False for non-cacheable path."""
        mock_request.url.path = "/api/other"
        result = middleware._is_cacheable(mock_request)
        assert result is False

    def test_generate_cache_key(self, middleware, mock_request):
        """Test cache key generation."""
        result = middleware._generate_cache_key(mock_request)
        assert "test" in result
        assert "GET" in result
        assert "/api/test" in result

    @pytest.mark.asyncio
    async def test_cache_response(self, middleware, mock_response):
        """Test caching response."""
        with patch('src.shared.infrastructure.middleware.cache') as mock_cache:
            mock_cache.set_json = AsyncMock(return_value=True)
            # Mock response body_iterator to be async iterable
            mock_response.body_iterator = AsyncMock()
            mock_response.body_iterator.__aiter__.return_value = [b'{"test": "data"}']
            
            await middleware._cache_response("test_key", mock_response)
            
            mock_cache.set_json.assert_called_once()
            call_args = mock_cache.set_json.call_args
            assert call_args[0][0] == "test_key"


class TestRateLimitMiddleware:
    """Test cases for RateLimitMiddleware."""

    @pytest.fixture
    def middleware(self):
        """Create rate limit middleware."""
        return RateLimitMiddleware(Mock(), requests_per_minute=60, requests_per_hour=1000)

    @pytest.fixture
    def mock_request(self):
        """Create mock request."""
        request = Mock(spec=Request)
        request.client.host = "127.0.0.1"
        request.headers = {"user-agent": "test-agent"}
        # Ensure no user state is set
        request.state = Mock()
        request.state.user = None
        return request

    @pytest.fixture
    def mock_response(self):
        """Create mock response."""
        response = Mock(spec=Response)
        response.status_code = 200
        response.headers = {}
        return response

    @pytest.fixture
    def mock_call_next(self):
        """Create mock call_next function."""
        return AsyncMock()

    @pytest.mark.asyncio
    async def test_dispatch_success(self, middleware, mock_request, mock_response, mock_call_next):
        """Test successful request dispatch."""
        mock_call_next.return_value = mock_response
        
        with patch.object(middleware, '_is_rate_limited', return_value=False):
            with patch.object(middleware, '_increment_request_count'):
                result = await middleware.dispatch(mock_request, mock_call_next)
                
                assert result == mock_response
                mock_call_next.assert_called_once_with(mock_request)

    @pytest.mark.asyncio
    async def test_dispatch_rate_limited(self, middleware, mock_request, mock_call_next):
        """Test dispatch when rate limited."""
        with patch.object(middleware, '_is_rate_limited', return_value=True):
            with patch.object(middleware, '_get_remaining_requests', return_value=0):
                result = await middleware.dispatch(mock_request, mock_call_next)
                
                assert result.status_code == 429
                mock_call_next.assert_not_called()

    def test_get_client_id_ip(self, middleware, mock_request):
        """Test getting client ID from IP."""
        result = middleware._get_client_id(mock_request)
        assert result == "ip:127.0.0.1"

    def test_get_client_id_user_agent(self, middleware, mock_request):
        """Test getting client ID with user agent."""
        mock_request.client.host = None
        result = middleware._get_client_id(mock_request)
        assert result == "ip:None"

    @pytest.mark.asyncio
    async def test_is_rate_limited_true(self, middleware):
        """Test is_rate_limited returns True."""
        with patch('src.shared.infrastructure.middleware.cache') as mock_cache:
            mock_cache.get = AsyncMock(return_value="65")  # Over limit
            
            result = await middleware._is_rate_limited("test-client")
            
            assert result is True

    @pytest.mark.asyncio
    async def test_is_rate_limited_false(self, middleware):
        """Test is_rate_limited returns False."""
        with patch('src.shared.infrastructure.middleware.cache') as mock_cache:
            mock_cache.get = AsyncMock(return_value="30")  # Under limit
            
            result = await middleware._is_rate_limited("test-client")
            
            assert result is False

    @pytest.mark.asyncio
    async def test_increment_request_count(self, middleware):
        """Test incrementing request count."""
        with patch('src.shared.infrastructure.middleware.cache') as mock_cache:
            mock_cache.incr = AsyncMock(return_value=1)
            mock_cache.expire = AsyncMock(return_value=True)
            
            await middleware._increment_request_count("test-client")
            
            assert mock_cache.incr.call_count == 2  # Called for both minute and hour
            assert mock_cache.expire.call_count == 2

    @pytest.mark.asyncio
    async def test_get_remaining_requests(self, middleware):
        """Test getting remaining requests."""
        with patch('src.shared.infrastructure.middleware.cache') as mock_cache:
            mock_cache.get = AsyncMock(return_value="30")
            
            result = await middleware._get_remaining_requests("test-client")
            
            assert result == 30


class TestSecurityMiddleware:
    """Test cases for SecurityMiddleware."""

    @pytest.fixture
    def middleware(self):
        """Create security middleware."""
        return SecurityMiddleware(Mock())

    @pytest.fixture
    def mock_request(self):
        """Create mock request."""
        request = Mock(spec=Request)
        request.headers = {
            "user-agent": "test-agent",
            "x-forwarded-for": "192.168.1.1"
        }
        return request

    @pytest.fixture
    def mock_response(self):
        """Create mock response."""
        response = Mock(spec=Response)
        response.status_code = 200
        response.headers = {}
        return response

    @pytest.fixture
    def mock_call_next(self):
        """Create mock call_next function."""
        return AsyncMock()

    @pytest.mark.asyncio
    async def test_dispatch_success(self, middleware, mock_request, mock_response, mock_call_next):
        """Test successful request dispatch."""
        mock_call_next.return_value = mock_response
        
        result = await middleware.dispatch(mock_request, mock_call_next)
        
        assert result == mock_response
        mock_call_next.assert_called_once_with(mock_request)

    @pytest.mark.asyncio
    async def test_dispatch_adds_security_headers(self, middleware, mock_request, mock_response, mock_call_next):
        """Test that security headers are added to response."""
        mock_call_next.return_value = mock_response
        
        result = await middleware.dispatch(mock_request, mock_call_next)
        
        # Check that security headers are added
        assert "X-Content-Type-Options" in result.headers
        assert "X-Frame-Options" in result.headers
        assert "X-XSS-Protection" in result.headers
        assert "Strict-Transport-Security" in result.headers
        assert "Content-Security-Policy" in result.headers

    @pytest.mark.asyncio
    async def test_dispatch_exception(self, middleware, mock_request, mock_call_next):
        """Test dispatch with exception."""
        mock_call_next.side_effect = Exception("Test error")
        
        with pytest.raises(Exception, match="Test error"):
            await middleware.dispatch(mock_request, mock_call_next) 