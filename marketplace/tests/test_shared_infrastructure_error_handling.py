"""Tests for error handling in shared infrastructure modules."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import asyncio
import aiohttp
from sqlalchemy.exc import SQLAlchemyError

from src.shared.infrastructure.cache import CacheManager
from src.shared.infrastructure.service_client import ServiceClient
from src.shared.infrastructure.middleware import (
    ErrorHandlingMiddleware,
    LoggingMiddleware,
    AuthenticationMiddleware,
)
from src.shared.infrastructure.monitoring import MetricsCollector
from src.shared.infrastructure.error_handlers import (
    handle_validation_error,
    handle_not_found_error,
    handle_database_error,
    handle_external_service_error,
)
from src.shared.domain.exceptions import (
    EntityNotFoundError,
    ValidationError,
    DatabaseError,
    ExternalServiceError,
)


class TestCacheManagerErrorHandling:
    """Test error handling scenarios in cache manager."""

    @pytest.fixture
    def cache_manager(self):
        """Create cache manager instance."""
        return CacheManager()

    async def test_get_cache_connection_error(self, cache_manager):
        """Test getting value with cache connection error."""
        # Arrange
        with patch('redis.asyncio.Redis') as mock_redis:
            mock_redis.return_value.get.side_effect = ConnectionError("Redis connection failed")
            
            # Act & Assert
            with pytest.raises(ConnectionError):
                await cache_manager.get("test_key")

    async def test_set_cache_connection_error(self, cache_manager):
        """Test setting value with cache connection error."""
        # Arrange
        with patch('redis.asyncio.Redis') as mock_redis:
            mock_redis.return_value.set.side_effect = ConnectionError("Redis connection failed")
            
            # Act & Assert
            with pytest.raises(ConnectionError):
                await cache_manager.set("test_key", "test_value")

    async def test_delete_cache_connection_error(self, cache_manager):
        """Test deleting value with cache connection error."""
        # Arrange
        with patch('redis.asyncio.Redis') as mock_redis:
            mock_redis.return_value.delete.side_effect = ConnectionError("Redis connection failed")
            
            # Act & Assert
            with pytest.raises(ConnectionError):
                await cache_manager.delete("test_key")

    async def test_get_cache_memory_error(self, cache_manager):
        """Test getting value with memory error."""
        # Arrange
        with patch('redis.asyncio.Redis') as mock_redis:
            mock_redis.return_value.get.side_effect = MemoryError("Out of memory")
            
            # Act & Assert
            with pytest.raises(MemoryError):
                await cache_manager.get("test_key")

    async def test_set_cache_memory_error(self, cache_manager):
        """Test setting value with memory error."""
        # Arrange
        with patch('redis.asyncio.Redis') as mock_redis:
            mock_redis.return_value.set.side_effect = MemoryError("Out of memory")
            
            # Act & Assert
            with pytest.raises(MemoryError):
                await cache_manager.set("test_key", "test_value")

    async def test_get_cache_timeout_error(self, cache_manager):
        """Test getting value with timeout error."""
        # Arrange
        with patch('redis.asyncio.Redis') as mock_redis:
            mock_redis.return_value.get.side_effect = asyncio.TimeoutError("Operation timed out")
            
            # Act & Assert
            with pytest.raises(asyncio.TimeoutError):
                await cache_manager.get("test_key")


class TestServiceClientErrorHandling:
    """Test error handling scenarios in service client."""

    @pytest.fixture
    def service_client(self):
        """Create service client instance."""
        return ServiceClient("http://test-service.com")

    async def test_get_request_connection_error(self, service_client):
        """Test GET request with connection error."""
        # Arrange
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_get.side_effect = aiohttp.ClientConnectionError("Connection failed")
            
            # Act & Assert
            with pytest.raises(aiohttp.ClientConnectionError):
                await service_client.get("/test")

    async def test_post_request_connection_error(self, service_client):
        """Test POST request with connection error."""
        # Arrange
        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_post.side_effect = aiohttp.ClientConnectionError("Connection failed")
            
            # Act & Assert
            with pytest.raises(aiohttp.ClientConnectionError):
                await service_client.post("/test", {"data": "test"})

    async def test_get_request_timeout_error(self, service_client):
        """Test GET request with timeout error."""
        # Arrange
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_get.side_effect = asyncio.TimeoutError("Request timed out")
            
            # Act & Assert
            with pytest.raises(asyncio.TimeoutError):
                await service_client.get("/test")

    async def test_post_request_timeout_error(self, service_client):
        """Test POST request with timeout error."""
        # Arrange
        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_post.side_effect = asyncio.TimeoutError("Request timed out")
            
            # Act & Assert
            with pytest.raises(asyncio.TimeoutError):
                await service_client.post("/test", {"data": "test"})

    async def test_get_request_http_error(self, service_client):
        """Test GET request with HTTP error."""
        # Arrange
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status = 500
            mock_response.text.return_value = "Internal Server Error"
            mock_get.return_value.__aenter__.return_value = mock_response
            
            # Act & Assert
            with pytest.raises(aiohttp.ClientResponseError):
                await service_client.get("/test")

    async def test_post_request_http_error(self, service_client):
        """Test POST request with HTTP error."""
        # Arrange
        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_response = MagicMock()
            mock_response.status = 400
            mock_response.text.return_value = "Bad Request"
            mock_post.return_value.__aenter__.return_value = mock_response
            
            # Act & Assert
            with pytest.raises(aiohttp.ClientResponseError):
                await service_client.post("/test", {"data": "test"})

    async def test_get_request_ssl_error(self, service_client):
        """Test GET request with SSL error."""
        # Arrange
        with patch('aiohttp.ClientSession.get') as mock_get:
            mock_get.side_effect = aiohttp.ClientSSLError("SSL certificate error")
            
            # Act & Assert
            with pytest.raises(aiohttp.ClientSSLError):
                await service_client.get("/test")

    async def test_post_request_ssl_error(self, service_client):
        """Test POST request with SSL error."""
        # Arrange
        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_post.side_effect = aiohttp.ClientSSLError("SSL certificate error")
            
            # Act & Assert
            with pytest.raises(aiohttp.ClientSSLError):
                await service_client.post("/test", {"data": "test"})


class TestMiddlewareErrorHandling:
    """Test error handling scenarios in middleware."""

    @pytest.fixture
    def error_handling_middleware(self):
        """Create error handling middleware instance."""
        return ErrorHandlingMiddleware()

    @pytest.fixture
    def logging_middleware(self):
        """Create logging middleware instance."""
        return LoggingMiddleware()

    @pytest.fixture
    def auth_middleware(self):
        """Create authentication middleware instance."""
        return AuthenticationMiddleware()

    async def test_error_handling_middleware_validation_error(self, error_handling_middleware):
        """Test error handling middleware with validation error."""
        # Arrange
        request = MagicMock()
        validation_error = ValidationError("Invalid data")
        
        # Act & Assert
        with pytest.raises(ValidationError):
            await error_handling_middleware.handle_error(request, validation_error)

    async def test_error_handling_middleware_database_error(self, error_handling_middleware):
        """Test error handling middleware with database error."""
        # Arrange
        request = MagicMock()
        database_error = DatabaseError("Database connection failed")
        
        # Act & Assert
        with pytest.raises(DatabaseError):
            await error_handling_middleware.handle_error(request, database_error)

    async def test_logging_middleware_logging_error(self, logging_middleware):
        """Test logging middleware with logging error."""
        # Arrange
        request = MagicMock()
        with patch('logging.getLogger') as mock_logger:
            mock_logger.return_value.error.side_effect = OSError("Logging failed")
            
            # Act & Assert
            with pytest.raises(OSError):
                await logging_middleware.log_request(request)

    async def test_auth_middleware_invalid_token(self, auth_middleware):
        """Test authentication middleware with invalid token."""
        # Arrange
        request = MagicMock()
        request.headers = {"Authorization": "Bearer invalid_token"}
        
        # Act & Assert
        with pytest.raises(ValueError, match="Invalid token"):
            await auth_middleware.authenticate(request)

    async def test_auth_middleware_missing_token(self, auth_middleware):
        """Test authentication middleware with missing token."""
        # Arrange
        request = MagicMock()
        request.headers = {}
        
        # Act & Assert
        with pytest.raises(ValueError, match="Missing authorization header"):
            await auth_middleware.authenticate(request)

    async def test_auth_middleware_expired_token(self, auth_middleware):
        """Test authentication middleware with expired token."""
        # Arrange
        request = MagicMock()
        request.headers = {"Authorization": "Bearer expired_token"}
        
        with patch('jwt.decode') as mock_jwt:
            mock_jwt.side_effect = Exception("Token expired")
            
            # Act & Assert
            with pytest.raises(Exception, match="Token expired"):
                await auth_middleware.authenticate(request)


class TestMetricsCollectorErrorHandling:
    """Test error handling scenarios in metrics collector."""

    @pytest.fixture
    def metrics_collector(self):
        """Create metrics collector instance."""
        return MetricsCollector()

    async def test_increment_counter_connection_error(self, metrics_collector):
        """Test incrementing counter with connection error."""
        # Arrange
        with patch('prometheus_client.Counter.labels') as mock_counter:
            mock_counter.return_value.inc.side_effect = ConnectionError("Prometheus connection failed")
            
            # Act & Assert
            with pytest.raises(ConnectionError):
                await metrics_collector.increment_counter("test_counter", {"label": "value"})

    async def test_set_gauge_connection_error(self, metrics_collector):
        """Test setting gauge with connection error."""
        # Arrange
        with patch('prometheus_client.Gauge.labels') as mock_gauge:
            mock_gauge.return_value.set.side_effect = ConnectionError("Prometheus connection failed")
            
            # Act & Assert
            with pytest.raises(ConnectionError):
                await metrics_collector.set_gauge("test_gauge", 10, {"label": "value"})

    async def test_observe_histogram_connection_error(self, metrics_collector):
        """Test observing histogram with connection error."""
        # Arrange
        with patch('prometheus_client.Histogram.labels') as mock_histogram:
            mock_histogram.return_value.observe.side_effect = ConnectionError("Prometheus connection failed")
            
            # Act & Assert
            with pytest.raises(ConnectionError):
                await metrics_collector.observe_histogram("test_histogram", 1.5, {"label": "value"})

    async def test_increment_counter_invalid_metric_name(self, metrics_collector):
        """Test incrementing counter with invalid metric name."""
        # Arrange
        invalid_name = "invalid-metric-name-with-special-chars!"
        
        # Act & Assert
        with pytest.raises(ValueError, match="Invalid metric name"):
            await metrics_collector.increment_counter(invalid_name, {"label": "value"})

    async def test_set_gauge_invalid_value(self, metrics_collector):
        """Test setting gauge with invalid value."""
        # Arrange
        invalid_value = "not_a_number"
        
        # Act & Assert
        with pytest.raises(ValueError, match="Invalid gauge value"):
            await metrics_collector.set_gauge("test_gauge", invalid_value, {"label": "value"})


class TestErrorHandlers:
    """Test error handler functions."""

    def test_handle_validation_error(self):
        """Test handling validation error."""
        # Arrange
        validation_error = ValidationError("Invalid data")
        
        # Act
        response = handle_validation_error(validation_error)
        
        # Assert
        assert response.status_code == 400
        assert "Invalid data" in response.body.decode()

    def test_handle_not_found_error(self):
        """Test handling not found error."""
        # Arrange
        not_found_error = EntityNotFoundError("Entity not found")
        
        # Act
        response = handle_not_found_error(not_found_error)
        
        # Assert
        assert response.status_code == 404
        assert "Entity not found" in response.body.decode()

    def test_handle_database_error(self):
        """Test handling database error."""
        # Arrange
        database_error = DatabaseError("Database connection failed")
        
        # Act
        response = handle_database_error(database_error)
        
        # Assert
        assert response.status_code == 500
        assert "Database connection failed" in response.body.decode()

    def test_handle_external_service_error(self):
        """Test handling external service error."""
        # Arrange
        external_service_error = ExternalServiceError("External service unavailable")
        
        # Act
        response = handle_external_service_error(external_service_error)
        
        # Assert
        assert response.status_code == 503
        assert "External service unavailable" in response.body.decode()

    def test_handle_validation_error_with_details(self):
        """Test handling validation error with details."""
        # Arrange
        validation_error = ValidationError("Invalid data", details={"field": "email", "error": "Invalid format"})
        
        # Act
        response = handle_validation_error(validation_error)
        
        # Assert
        assert response.status_code == 400
        response_data = response.body.decode()
        assert "Invalid data" in response_data
        assert "email" in response_data

    def test_handle_database_error_with_retry(self):
        """Test handling database error with retry information."""
        # Arrange
        database_error = DatabaseError("Database connection failed", retry_after=30)
        
        # Act
        response = handle_database_error(database_error)
        
        # Assert
        assert response.status_code == 500
        assert "Database connection failed" in response.body.decode()
        assert "30" in response.headers.get("Retry-After", "")

    def test_handle_external_service_error_with_timeout(self):
        """Test handling external service error with timeout."""
        # Arrange
        external_service_error = ExternalServiceError("External service timeout", timeout=60)
        
        # Act
        response = handle_external_service_error(external_service_error)
        
        # Assert
        assert response.status_code == 503
        assert "External service timeout" in response.body.decode()
        assert "60" in response.headers.get("Retry-After", "") 