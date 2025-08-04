"""Tests for shared.infrastructure.error_handlers module."""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from src.shared.infrastructure.error_handlers import (
    AuthenticationError, AuthorizationError, RateLimitError, DatabaseError, CacheError, ExternalServiceError,
    ErrorContext, handle_errors, retry_on_error, ErrorHandler
)
from src.shared.domain.exceptions import BusinessRuleViolationError, EntityNotFoundError
import asyncio


def test_authentication_error():
    err = AuthenticationError("msg", code="401")
    assert str(err) == "msg"
    assert err.code == "401"

def test_authorization_error():
    err = AuthorizationError("msg", required_permissions=["admin"])
    assert str(err) == "msg"
    assert err.required_permissions == ["admin"]

def test_rate_limit_error():
    err = RateLimitError("msg", retry_after=5, limit=10)
    assert str(err) == "msg"
    assert err.retry_after == 5
    assert err.limit == 10

def test_database_error():
    err = DatabaseError("db fail", operation="insert", table="users")
    assert str(err) == "db fail"
    assert err.operation == "insert"
    assert err.table == "users"

def test_cache_error():
    err = CacheError("cache fail", operation="get", key="foo")
    assert str(err) == "cache fail"
    assert err.operation == "get"
    assert err.key == "foo"

def test_external_service_error():
    err = ExternalServiceError("fail", service="mail", status_code=500)
    assert str(err) == "fail"
    assert err.service == "mail"
    assert err.status_code == 500


def test_error_context_add_and_exit():
    ctx = ErrorContext("test_logger")
    with ctx.add_context(user="u1", action="test") as c:
        assert c.context["user"] == "u1"
        assert c.context["action"] == "test"
    # __exit__ should not raise


def test_handle_errors_decorator_sync():
    @handle_errors("test_logger")
    def f(x):
        if x == 0:
            raise ValueError("fail")
        return x
    assert f(1) == 1
    with pytest.raises(ValueError):
        f(0)

def test_handle_errors_decorator_async():
    @handle_errors("test_logger")
    async def f(x):
        if x == 0:
            raise ValueError("fail")
        return x
    assert asyncio.run(f(1)) == 1
    with pytest.raises(ValueError):
        asyncio.run(f(0))


def test_retry_on_error_sync():
    calls = {"n": 0}
    @retry_on_error(max_retries=2, delay=0.01)
    def f():
        calls["n"] += 1
        if calls["n"] < 2:
            raise ValueError("fail")
        return 42
    assert f() == 42
    assert calls["n"] == 2

def test_retry_on_error_async():
    calls = {"n": 0}
    @retry_on_error(max_retries=2, delay=0.01)
    async def f():
        calls["n"] += 1
        if calls["n"] < 2:
            raise ValueError("fail")
        return 42
    assert asyncio.run(f()) == 42
    assert calls["n"] == 2


class TestErrorHandler:
    """Test ErrorHandler class."""

    @pytest.fixture
    def app(self):
        """Create FastAPI app for testing."""
        return FastAPI()

    @pytest.fixture
    def error_handler(self, app):
        """Create ErrorHandler instance."""
        return ErrorHandler(app)

    @pytest.fixture
    def mock_request(self):
        """Create mock request."""
        request = Mock(spec=Request)
        request.url.path = "/test"
        request.method = "GET"
        request.headers = {"user-agent": "test-agent"}
        request.client.host = "127.0.0.1"
        return request

    @pytest.mark.asyncio
    async def test_handle_validation_error(self, error_handler, mock_request):
        """Test handling validation error."""
        # Create a validation error
        validation_error = ValidationError.from_exception_data(
            "ValidationError",
            [{"loc": ("body", "email"), "msg": "field required", "type": "value_error.missing"}]
        )

        response = await error_handler._handle_validation_error(mock_request, validation_error)

        assert response.status_code == 422
        data = response.body.decode()
        assert "Validation error" in data
        assert "field required" in data

    @pytest.mark.asyncio
    async def test_handle_request_validation_error(self, error_handler, mock_request):
        """Test handling request validation error."""
        # Create a request validation error
        validation_error = RequestValidationError(
            errors=[{"loc": ("body", "email"), "msg": "field required", "type": "value_error.missing"}]
        )

        response = await error_handler._handle_validation_error(mock_request, validation_error)

        assert response.status_code == 422
        data = response.body.decode()
        assert "Validation error" in data
        assert "field required" in data

    @pytest.mark.asyncio
    async def test_handle_business_rule_violation(self, error_handler, mock_request):
        """Test handling business rule violation."""
        business_error = BusinessRuleViolationError("Invalid business rule")

        response = await error_handler._handle_business_rule_violation(mock_request, business_error)

        assert response.status_code == 400
        data = response.body.decode()
        assert "Business rule violation" in data
        assert "Invalid business rule" in data

    @pytest.mark.asyncio
    async def test_handle_entity_not_found(self, error_handler, mock_request):
        """Test handling entity not found error."""
        entity_error = EntityNotFoundError("User with ID 123 not found")

        response = await error_handler._handle_entity_not_found(mock_request, entity_error)

        assert response.status_code == 404
        data = response.body.decode()
        assert "Entity not found" in data
        assert "User with ID 123 not found" in data

    @pytest.mark.asyncio
    async def test_handle_http_exception(self, error_handler, mock_request):
        """Test handling HTTP exception."""
        http_error = StarletteHTTPException(status_code=403, detail="Forbidden")

        response = await error_handler._handle_http_exception(mock_request, http_error)

        assert response.status_code == 403
        data = response.body.decode()
        assert "Forbidden" in data

    @pytest.mark.asyncio
    async def test_handle_general_exception(self, error_handler, mock_request):
        """Test handling general exception."""
        general_error = ValueError("Something went wrong")

        response = await error_handler._handle_general_exception(mock_request, general_error)

        assert response.status_code == 500
        data = response.body.decode()
        assert "Internal server error" in data

    @pytest.mark.asyncio
    async def test_handle_general_exception_with_traceback(self, error_handler, mock_request):
        """Test handling general exception with traceback."""
        general_error = ValueError("Something went wrong")

        with patch.object(error_handler.logger, 'error') as mock_logger:
            response = await error_handler._handle_general_exception(mock_request, general_error)

            assert response.status_code == 500
            mock_logger.assert_called_once()

    @pytest.mark.asyncio
    async def test_register_handlers(self, app):
        """Test that handlers are registered."""
        error_handler = ErrorHandler(app)
        
        # Check that exception handlers are registered
        assert hasattr(app, 'exception_handlers')
        assert len(app.exception_handlers) > 0

    @pytest.mark.asyncio
    async def test_validation_error_handler_integration(self, app):
        """Test validation error handler integration."""
        error_handler = ErrorHandler(app)
        
        @app.get("/test")
        async def test_endpoint():
            raise ValidationError.from_exception_data(
                "ValidationError",
                [{"loc": ("body", "email"), "msg": "field required", "type": "value_error.missing"}]
            )

        from fastapi.testclient import TestClient
        client = TestClient(app)
        
        response = client.get("/test")
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_business_rule_violation_handler_integration(self, app):
        """Test business rule violation handler integration."""
        error_handler = ErrorHandler(app)
        
        @app.get("/test")
        async def test_endpoint():
            raise BusinessRuleViolationError("Invalid business rule")

        from fastapi.testclient import TestClient
        client = TestClient(app)
        
        response = client.get("/test")
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_entity_not_found_handler_integration(self, app):
        """Test entity not found handler integration."""
        error_handler = ErrorHandler(app)
        
        @app.get("/test")
        async def test_endpoint():
            raise EntityNotFoundError("User not found")

        from fastapi.testclient import TestClient
        client = TestClient(app)
        
        response = client.get("/test")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_http_exception_handler_integration(self, app):
        """Test HTTP exception handler integration."""
        error_handler = ErrorHandler(app)
        
        @app.get("/test")
        async def test_endpoint():
            raise StarletteHTTPException(status_code=403, detail="Forbidden")

        from fastapi.testclient import TestClient
        client = TestClient(app)
        
        response = client.get("/test")
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_general_exception_handler_integration(self, app):
        """Test general exception handler integration."""
        error_handler = ErrorHandler(app)
        
        @app.get("/test")
        async def test_endpoint():
            raise ValueError("Something went wrong")

        from fastapi.testclient import TestClient
        client = TestClient(app)
        
        response = client.get("/test")
        assert response.status_code == 500


class TestErrorMiddleware:
    """Test ErrorMiddleware class."""

    @pytest.fixture
    def app(self):
        """Create FastAPI app for testing."""
        return FastAPI()

    @pytest.fixture
    def middleware(self, app):
        """Create ErrorMiddleware instance."""
        from src.shared.infrastructure.error_handlers import ErrorMiddleware
        return ErrorMiddleware(app)

    @pytest.mark.asyncio
    async def test_middleware_call_success(self, middleware):
        """Test middleware call with success."""
        scope = {"type": "http", "method": "GET", "path": "/test"}
        receive = AsyncMock()
        send = AsyncMock()

        await middleware(scope, receive, send)

        # Should call the app
        assert middleware.app.called

    @pytest.mark.asyncio
    async def test_middleware_call_with_exception(self, middleware):
        """Test middleware call with exception."""
        scope = {"type": "http", "method": "GET", "path": "/test"}
        receive = AsyncMock()
        send = AsyncMock()

        # Mock app to raise exception
        middleware.app = AsyncMock(side_effect=ValueError("Test error"))

        await middleware(scope, receive, send)

        # Should handle the exception
        send.assert_called()


class TestErrorContext:
    """Test ErrorContext class."""

    def test_error_context_initialization(self):
        """Test ErrorContext initialization."""
        ctx = ErrorContext("test_logger")
        assert ctx.logger_name == "test_logger"
        assert ctx.context == {}

    def test_error_context_add_context(self):
        """Test adding context to ErrorContext."""
        ctx = ErrorContext("test_logger")
        ctx.add_context(user_id="123", action="test")
        
        assert ctx.context["user_id"] == "123"
        assert ctx.context["action"] == "test"

    def test_error_context_multiple_add_context(self):
        """Test adding multiple contexts to ErrorContext."""
        ctx = ErrorContext("test_logger")
        ctx.add_context(user_id="123")
        ctx.add_context(action="test")
        
        assert ctx.context["user_id"] == "123"
        assert ctx.context["action"] == "test"

    def test_error_context_context_manager(self):
        """Test ErrorContext as context manager."""
        ctx = ErrorContext("test_logger")
        
        with ctx.add_context(user_id="123", action="test") as context:
            assert context.context["user_id"] == "123"
            assert context.context["action"] == "test"

    def test_error_context_exit_with_exception(self):
        """Test ErrorContext exit with exception."""
        ctx = ErrorContext("test_logger")
        
        with ctx.add_context(user_id="123"):
            pass  # Normal exit
        
        # Should not raise any exception


class TestHandleErrorsDecorator:
    """Test handle_errors decorator."""

    def test_handle_errors_sync_function_success(self):
        """Test handle_errors decorator with successful sync function."""
        @handle_errors("test_logger")
        def test_func(x):
            return x * 2

        result = test_func(5)
        assert result == 10

    def test_handle_errors_sync_function_exception(self):
        """Test handle_errors decorator with sync function that raises exception."""
        @handle_errors("test_logger")
        def test_func(x):
            if x == 0:
                raise ValueError("Division by zero")
            return 10 / x

        with pytest.raises(ValueError, match="Division by zero"):
            test_func(0)

    @pytest.mark.asyncio
    async def test_handle_errors_async_function_success(self):
        """Test handle_errors decorator with successful async function."""
        @handle_errors("test_logger")
        async def test_func(x):
            return x * 2

        result = await test_func(5)
        assert result == 10

    @pytest.mark.asyncio
    async def test_handle_errors_async_function_exception(self):
        """Test handle_errors decorator with async function that raises exception."""
        @handle_errors("test_logger")
        async def test_func(x):
            if x == 0:
                raise ValueError("Division by zero")
            return 10 / x

        with pytest.raises(ValueError, match="Division by zero"):
            await test_func(0)


class TestRetryOnErrorDecorator:
    """Test retry_on_error decorator."""

    def test_retry_on_error_sync_function_success(self):
        """Test retry_on_error decorator with successful sync function."""
        @retry_on_error(max_retries=3, delay=0.01)
        def test_func(x):
            return x * 2

        result = test_func(5)
        assert result == 10

    def test_retry_on_error_sync_function_retry_success(self):
        """Test retry_on_error decorator with sync function that succeeds after retries."""
        call_count = 0
        
        @retry_on_error(max_retries=3, delay=0.01)
        def test_func():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("Temporary error")
            return "success"

        result = test_func()
        assert result == "success"
        assert call_count == 3

    def test_retry_on_error_sync_function_max_retries_exceeded(self):
        """Test retry_on_error decorator with sync function that exceeds max retries."""
        @retry_on_error(max_retries=2, delay=0.01)
        def test_func():
            raise ValueError("Persistent error")

        with pytest.raises(ValueError, match="Persistent error"):
            test_func()

    @pytest.mark.asyncio
    async def test_retry_on_error_async_function_success(self):
        """Test retry_on_error decorator with successful async function."""
        @retry_on_error(max_retries=3, delay=0.01)
        async def test_func(x):
            return x * 2

        result = await test_func(5)
        assert result == 10

    @pytest.mark.asyncio
    async def test_retry_on_error_async_function_retry_success(self):
        """Test retry_on_error decorator with async function that succeeds after retries."""
        call_count = 0
        
        @retry_on_error(max_retries=3, delay=0.01)
        async def test_func():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("Temporary error")
            return "success"

        result = await test_func()
        assert result == "success"
        assert call_count == 3

    @pytest.mark.asyncio
    async def test_retry_on_error_async_function_max_retries_exceeded(self):
        """Test retry_on_error decorator with async function that exceeds max retries."""
        @retry_on_error(max_retries=2, delay=0.01)
        async def test_func():
            raise ValueError("Persistent error")

        with pytest.raises(ValueError, match="Persistent error"):
            await test_func()