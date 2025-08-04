"""Tests for shared.infrastructure.service_client module."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import httpx
from src.shared.infrastructure.service_client import (
    ServiceClient, ServiceRegistry, call_service, call_service_with_retry
)
from src.shared.infrastructure.error_handlers import ExternalServiceError


@pytest.mark.asyncio
class TestServiceClient:
    @pytest.fixture
    def client(self):
        return ServiceClient("http://test.com")

    @pytest.fixture
    def mock_response(self):
        response = AsyncMock()
        response.json = AsyncMock(return_value={"status": "ok"})
        response.raise_for_status = AsyncMock(return_value=None)
        return response

    async def test_context_manager(self, client):
        async with client as c:
            assert c._client is not None
            assert isinstance(c._client, httpx.AsyncClient)
        # After context manager exit, _client should be None
        assert client._client is None

    async def test_get_success(self, client, mock_response):
        with patch.object(httpx.AsyncClient, 'get', return_value=mock_response):
            async with client:
                result = await client.get("/test")
                assert result == {"status": "ok"}

    async def test_post_success(self, client, mock_response):
        with patch.object(httpx.AsyncClient, 'post', return_value=mock_response):
            async with client:
                result = await client.post("/test", {"data": "test"})
                assert result == {"status": "ok"}

    async def test_put_success(self, client, mock_response):
        with patch.object(httpx.AsyncClient, 'put', return_value=mock_response):
            async with client:
                result = await client.put("/test", {"data": "test"})
                assert result == {"status": "ok"}

    async def test_delete_success(self, client, mock_response):
        with patch.object(httpx.AsyncClient, 'delete', return_value=mock_response):
            async with client:
                result = await client.delete("/test")
                assert result == {"status": "ok"}

    async def test_get_without_context_manager(self, client):
        with pytest.raises(RuntimeError, match="ServiceClient must be used as async context manager"):
            await client.get("/test")

    async def test_http_status_error(self, client):
        error_response = AsyncMock()
        error_response.status_code = 404
        http_error = httpx.HTTPStatusError("Not Found", request=AsyncMock(), response=error_response)
        
        with patch.object(httpx.AsyncClient, 'get', side_effect=http_error):
            async with client:
                with pytest.raises(ExternalServiceError) as exc_info:
                    await client.get("/test")
                assert exc_info.value.status_code == 404
                assert exc_info.value.service == "http://test.com"

    async def test_request_error(self, client):
        request_error = httpx.RequestError("Connection failed", request=AsyncMock())
        
        with patch.object(httpx.AsyncClient, 'get', side_effect=request_error):
            async with client:
                with pytest.raises(ExternalServiceError) as exc_info:
                    await client.get("/test")
                assert "Request failed" in str(exc_info.value.message)
                assert exc_info.value.service == "http://test.com"


class TestServiceRegistry:
    @pytest.fixture
    def registry(self):
        return ServiceRegistry()

    def test_get_service_url_success(self, registry):
        assert registry.get_service_url("catalog") == "http://catalog:8001"
        assert registry.get_service_url("orders") == "http://orders:8002"

    def test_get_service_url_unknown_service(self, registry):
        with pytest.raises(ValueError, match="Unknown service: unknown"):
            registry.get_service_url("unknown")

    def test_get_client(self, registry):
        client = registry.get_client("catalog")
        assert isinstance(client, ServiceClient)
        assert client.base_url == "http://catalog:8001"


@pytest.mark.asyncio
class TestCallService:
    @pytest.fixture
    def mock_response(self):
        response = AsyncMock()
        response.json = AsyncMock(return_value={"status": "ok"})
        response.raise_for_status = AsyncMock(return_value=None)
        return response

    async def test_call_service_get(self, mock_response):
        with patch.object(httpx.AsyncClient, 'get', return_value=mock_response):
            result = await call_service("catalog", "GET", "/products")
            assert result == {"status": "ok"}

    async def test_call_service_post(self, mock_response):
        with patch.object(httpx.AsyncClient, 'post', return_value=mock_response):
            result = await call_service("orders", "POST", "/orders", {"data": "test"})
            assert result == {"status": "ok"}

    async def test_call_service_put(self, mock_response):
        with patch.object(httpx.AsyncClient, 'put', return_value=mock_response):
            result = await call_service("users", "PUT", "/users/1", {"data": "test"})
            assert result == {"status": "ok"}

    async def test_call_service_delete(self, mock_response):
        with patch.object(httpx.AsyncClient, 'delete', return_value=mock_response):
            result = await call_service("reviews", "DELETE", "/reviews/1")
            assert result == {"status": "ok"}

    async def test_call_service_unsupported_method(self):
        with pytest.raises(ValueError, match="Unsupported method: PATCH"):
            await call_service("catalog", "PATCH", "/test")

    async def test_call_service_unknown_service(self):
        with pytest.raises(ValueError, match="Unknown service: unknown"):
            await call_service("unknown", "GET", "/test")


@pytest.mark.asyncio
class TestCallServiceWithRetry:
    @pytest.fixture
    def mock_response(self):
        response = AsyncMock()
        response.json = AsyncMock(return_value={"status": "ok"})
        response.raise_for_status = AsyncMock(return_value=None)
        return response

    async def test_call_service_with_retry_success_first_attempt(self, mock_response):
        with patch.object(httpx.AsyncClient, 'get', return_value=mock_response):
            result = await call_service_with_retry("catalog", "GET", "/products")
            assert result == {"status": "ok"}

    async def test_call_service_with_retry_success_after_failure(self, mock_response):
        error_response = AsyncMock()
        error_response.status_code = 500
        http_error = httpx.HTTPStatusError("Internal Server Error", request=AsyncMock(), response=error_response)
        
        with patch.object(httpx.AsyncClient, 'get', side_effect=[http_error, mock_response]):
            result = await call_service_with_retry("catalog", "GET", "/products", max_retries=2, delay=0.01)
            assert result == {"status": "ok"}

    async def test_call_service_with_retry_all_attempts_fail(self):
        error_response = AsyncMock()
        error_response.status_code = 500
        http_error = httpx.HTTPStatusError("Internal Server Error", request=AsyncMock(), response=error_response)
        
        with patch.object(httpx.AsyncClient, 'get', side_effect=http_error):
            with pytest.raises(ExternalServiceError) as exc_info:
                await call_service_with_retry("catalog", "GET", "/products", max_retries=2, delay=0.01)
            assert exc_info.value.status_code == 500 