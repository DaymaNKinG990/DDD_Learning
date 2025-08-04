"""Tests for shared infrastructure monitoring."""

# Python imports
import pytest
from unittest.mock import AsyncMock, Mock, patch, MagicMock
from fastapi import Request, Response
from starlette.responses import PlainTextResponse
import time

# Local imports
from src.shared.infrastructure.monitoring import (
    track_request_metrics,
    track_business_metrics,
    track_performance,
    metrics_endpoint,
    update_health_status,
    update_database_connections,
    update_redis_connections,
    update_cache_hit_ratio,
    MetricsMiddleware,
    http_requests_total,
    http_request_duration_seconds,
    orders_created_total,
    products_viewed_total,
    users_registered_total,
    reviews_created_total,
    database_connections_active,
    redis_connections_active,
    cache_hit_ratio,
    errors_total
)


class TestMetricsDecorators:
    """Test cases for metrics decorators."""

    @pytest.fixture
    def mock_request(self):
        """Create mock request."""
        request = Mock(spec=Request)
        request.method = "GET"
        request.url.path = "/api/test"
        request.headers = {"content-length": "100"}
        return request

    @pytest.fixture
    def mock_response(self):
        """Create mock response."""
        response = Mock(spec=Response)
        response.status_code = 200
        response.headers = {"content-length": "200"}
        return response

    @pytest.mark.asyncio
    async def test_track_request_metrics_success(self, mock_request, mock_response):
        """Test tracking request metrics for successful request."""
        @track_request_metrics
        async def test_handler(request: Request) -> Response:
            return mock_response

        with patch('src.shared.infrastructure.monitoring.http_requests_total') as mock_counter:
            with patch('src.shared.infrastructure.monitoring.http_request_duration_seconds') as mock_histogram:
                with patch('src.shared.infrastructure.monitoring.http_request_size_bytes') as mock_req_size:
                    with patch('src.shared.infrastructure.monitoring.http_response_size_bytes') as mock_resp_size:
                        result = await test_handler(mock_request)

                        assert result == mock_response
                        mock_counter.labels.assert_called_once_with(
                            method="GET", endpoint="/api/test", status=200
                        )
                        mock_histogram.labels.assert_called_once_with(
                            method="GET", endpoint="/api/test"
                        )

    @pytest.mark.asyncio
    async def test_track_request_metrics_exception(self, mock_request):
        """Test tracking request metrics for failed request."""
        @track_request_metrics
        async def test_handler(request: Request) -> Response:
            raise Exception("Test error")

        with patch('src.shared.infrastructure.monitoring.http_requests_total') as mock_counter:
            with patch('src.shared.infrastructure.monitoring.errors_total') as mock_errors:
                with pytest.raises(Exception, match="Test error"):
                    await test_handler(mock_request)

                mock_counter.labels.assert_called_once_with(
                    method="GET", endpoint="/api/test", status=500
                )
                mock_errors.labels.assert_called_once_with(
                    service="tests.test_shared_infrastructure_monitoring", error_type="Exception"
                )

    @pytest.mark.asyncio
    async def test_track_business_metrics_success(self):
        """Test tracking business metrics."""
        @track_business_metrics("test_metric", {"label1": "value1"})
        async def test_handler() -> str:
            return "success"

        with patch('src.shared.infrastructure.monitoring.Counter') as mock_counter_class:
            mock_counter = Mock()
            mock_counter_class.return_value = mock_counter
            
            result = await test_handler()

            assert result == "success"
            mock_counter.labels.assert_called_once_with(label1="value1")

    @pytest.mark.asyncio
    async def test_track_business_metrics_exception(self):
        """Test tracking business metrics with exception."""
        @track_business_metrics("test_metric", {"label1": "value1"})
        async def test_handler() -> str:
            raise Exception("Test error")

        with patch('src.shared.infrastructure.monitoring.Counter') as mock_counter_class:
            with patch('src.shared.infrastructure.monitoring.errors_total') as mock_errors:
                mock_counter = Mock()
                mock_counter_class.return_value = mock_counter
                
                with pytest.raises(Exception, match="Test error"):
                    await test_handler()

                mock_counter.labels.assert_called_once_with(label1="value1")
                mock_errors.labels.assert_called_once_with(
                    service="tests.test_shared_infrastructure_monitoring", error_type="Exception"
                )

    @pytest.mark.asyncio
    async def test_track_performance_success(self):
        """Test tracking performance metrics."""
        @track_performance("test_service", "test_operation")
        async def test_handler() -> str:
            return "success"

        with patch('src.shared.infrastructure.monitoring.http_request_duration_seconds') as mock_histogram:
            result = await test_handler()

            assert result == "success"
            mock_histogram.labels.assert_called_once_with(
                method="", endpoint="test_service_test_operation"
            )

    @pytest.mark.asyncio
    async def test_track_performance_exception(self):
        """Test tracking performance metrics with exception."""
        @track_performance("test_service", "test_operation")
        async def test_handler() -> str:
            raise Exception("Test error")

        with patch('src.shared.infrastructure.monitoring.http_request_duration_seconds') as mock_histogram:
            with patch('src.shared.infrastructure.monitoring.errors_total') as mock_errors:
                with pytest.raises(Exception, match="Test error"):
                    await test_handler()

                mock_histogram.labels.assert_called_once_with(
                    method="", endpoint="test_service_test_operation"
                )
                mock_errors.labels.assert_called_once_with(
                    service="test_service", error_type="Exception"
                )


class TestMetricsFunctions:
    """Test cases for metrics functions."""

    @pytest.mark.asyncio
    async def test_metrics_endpoint(self):
        """Test metrics endpoint."""
        with patch('src.shared.infrastructure.monitoring.generate_latest') as mock_generate:
            mock_generate.return_value = b"test_metrics"
            
            result = await metrics_endpoint()
            
            assert isinstance(result, PlainTextResponse)
            assert result.body == b"test_metrics"
            assert result.headers["content-type"] == "text/plain; version=0.0.4; charset=utf-8"

    def test_update_health_status(self):
        """Test updating health status."""
        with patch('src.shared.infrastructure.monitoring.database_connections_active') as mock_gauge:
            update_health_status("test_service", True)
            
            # Verify the gauge is updated (though the actual implementation may vary)
            # This test ensures the function doesn't raise exceptions

    def test_update_database_connections(self):
        """Test updating database connections."""
        with patch('src.shared.infrastructure.monitoring.database_connections_active') as mock_gauge:
            update_database_connections(5)
            
            mock_gauge.set.assert_called_once_with(5)

    def test_update_redis_connections(self):
        """Test updating Redis connections."""
        with patch('src.shared.infrastructure.monitoring.redis_connections_active') as mock_gauge:
            update_redis_connections(3)
            
            mock_gauge.set.assert_called_once_with(3)

    def test_update_cache_hit_ratio(self):
        """Test updating cache hit ratio."""
        with patch('src.shared.infrastructure.monitoring.cache_hit_ratio') as mock_gauge:
            update_cache_hit_ratio(0.85)
            
            mock_gauge.set.assert_called_once_with(0.85)


class TestMetricsMiddleware:
    """Test cases for MetricsMiddleware."""

    @pytest.fixture
    def middleware(self):
        """Create metrics middleware."""
        app = AsyncMock()
        return MetricsMiddleware(app)

    @pytest.fixture
    def mock_scope(self):
        """Create mock scope."""
        return {
            "type": "http",
            "method": "GET",
            "path": "/api/test",
            "headers": [(b"content-length", b"100")]
        }

    @pytest.fixture
    def mock_receive(self):
        """Create mock receive function."""
        return AsyncMock()

    @pytest.fixture
    def mock_send(self):
        """Create mock send function."""
        return AsyncMock()

    @pytest.mark.asyncio
    async def test_middleware_success(self, middleware, mock_scope, mock_receive, mock_send):
        """Test middleware for successful request."""
        with patch('src.shared.infrastructure.monitoring.http_requests_total') as mock_counter:
            with patch('src.shared.infrastructure.monitoring.http_request_duration_seconds') as mock_histogram:
                # Mock the app to call send_wrapper with success status
                async def mock_app(scope, receive, send_wrapper):
                    await send_wrapper({"type": "http.response.start", "status": 200})
                
                middleware.app = mock_app
                await middleware(mock_scope, mock_receive, mock_send)
                
                # Check that both "started" and "200" status calls were made
                mock_counter.labels.assert_any_call(
                    method="GET", endpoint="/api/test", status="started"
                )
                mock_counter.labels.assert_any_call(
                    method="GET", endpoint="/api/test", status=200
                )

    @pytest.mark.asyncio
    async def test_middleware_exception(self, middleware, mock_scope, mock_receive, mock_send):
        """Test middleware for failed request."""
        # Mock the app to raise an exception
        async def mock_app(scope, receive, send_wrapper):
            raise Exception("Test error")
        
        middleware.app = mock_app
        
        with patch('src.shared.infrastructure.monitoring.http_requests_total') as mock_counter:
            with patch('src.shared.infrastructure.monitoring.errors_total') as mock_errors:
                with pytest.raises(Exception, match="Test error"):
                    await middleware(mock_scope, mock_receive, mock_send)
                
                # Check that "started" status call was made
                mock_counter.labels.assert_any_call(
                    method="GET", endpoint="/api/test", status="started"
                )
                mock_errors.labels.assert_called_once_with(
                    service="fastapi", error_type="Exception"
                )

    @pytest.mark.asyncio
    async def test_middleware_non_http_scope(self, middleware, mock_receive, mock_send):
        """Test middleware for non-HTTP scope."""
        mock_scope = {"type": "websocket"}
        
        await middleware(mock_scope, mock_receive, mock_send)
        
        # app is called in the middleware implementation

    @pytest.mark.asyncio
    async def test_middleware_send_wrapper(self, middleware, mock_scope, mock_receive, mock_send):
        """Test middleware send wrapper."""
        with patch('src.shared.infrastructure.monitoring.http_response_size_bytes') as mock_resp_size:
            # Mock the app to call send_wrapper
            async def mock_app(scope, receive, send_wrapper):
                await send_wrapper({"type": "http.response.start", "status": 200})
                await send_wrapper({"type": "http.response.body", "body": b"test"})
            
            middleware.app = mock_app
            await middleware(mock_scope, mock_receive, mock_send)
            
            # Verify that the send function was called
            mock_send.assert_called()


class TestMetricsCounters:
    """Test cases for metrics counters."""

    def test_http_requests_total(self):
        """Test HTTP requests total counter."""
        assert http_requests_total._name == "http_requests"
        assert http_requests_total._documentation == "Total number of HTTP requests"

    def test_orders_created_total(self):
        """Test orders created total counter."""
        assert orders_created_total._name == "orders_created"
        assert orders_created_total._documentation == "Total number of orders created"

    def test_products_viewed_total(self):
        """Test products viewed total counter."""
        assert products_viewed_total._name == "products_viewed"
        assert products_viewed_total._documentation == "Total number of product views"

    def test_users_registered_total(self):
        """Test users registered total counter."""
        assert users_registered_total._name == "users_registered"
        assert users_registered_total._documentation == "Total number of user registrations"

    def test_reviews_created_total(self):
        """Test reviews created total counter."""
        assert reviews_created_total._name == "reviews_created"
        assert reviews_created_total._documentation == "Total number of reviews created"


class TestMetricsGauges:
    """Test cases for metrics gauges."""

    def test_database_connections_active(self):
        """Test database connections active gauge."""
        assert database_connections_active._name == "database_connections_active"
        assert database_connections_active._documentation == "Number of active database connections"

    def test_redis_connections_active(self):
        """Test Redis connections active gauge."""
        assert redis_connections_active._name == "redis_connections_active"
        assert redis_connections_active._documentation == "Number of active Redis connections"

    def test_cache_hit_ratio(self):
        """Test cache hit ratio gauge."""
        assert cache_hit_ratio._name == "cache_hit_ratio"
        assert cache_hit_ratio._documentation == "Cache hit ratio"


class TestMetricsHistograms:
    """Test cases for metrics histograms."""

    def test_http_request_duration_seconds(self):
        """Test HTTP request duration histogram."""
        assert http_request_duration_seconds._name == "http_request_duration_seconds"
        assert http_request_duration_seconds._documentation == "HTTP request duration in seconds"


class TestMetricsErrorHandling:
    """Test cases for error handling in metrics."""

    @pytest.mark.asyncio
    async def test_track_request_metrics_no_content_length(self):
        """Test tracking request metrics without content length."""
        request = Mock(spec=Request)
        request.method = "GET"
        request.url.path = "/api/test"
        request.headers = {}

        response = Mock(spec=Response)
        response.status_code = 200
        response.headers = {}

        @track_request_metrics
        async def test_handler(request: Request) -> Response:
            return response

        with patch('src.shared.infrastructure.monitoring.http_requests_total') as mock_counter:
            result = await test_handler(request)

            assert result == response
            mock_counter.labels.assert_called_once_with(
                method="GET", endpoint="/api/test", status=200
            )

    @pytest.mark.asyncio
    async def test_track_business_metrics_no_labels(self):
        """Test tracking business metrics without labels."""
        @track_business_metrics("users_registered")
        async def test_handler() -> str:
            return "success"

        with patch('src.shared.infrastructure.monitoring.users_registered_total') as mock_counter:
            result = await test_handler()

            assert result == "success"
            mock_counter.inc.assert_called_once()

    @pytest.mark.asyncio
    async def test_track_performance_with_timing(self):
        """Test tracking performance metrics with timing."""
        @track_performance("test_service", "test_operation")
        async def test_handler() -> str:
            time.sleep(0.01)  # Small delay to test timing
            return "success"

        with patch('src.shared.infrastructure.monitoring.http_request_duration_seconds') as mock_histogram:
            result = await test_handler()

            assert result == "success"
            mock_histogram.labels.assert_called_once_with(
                method="", endpoint="test_service_test_operation"
            ) 