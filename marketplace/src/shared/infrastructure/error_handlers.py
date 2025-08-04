"""Error handling and exception handlers for FastAPI."""

# Python imports
import asyncio
import time
import traceback
from types import TracebackType
from typing import Any, Callable, Dict, Optional, Type
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

# Local imports
from src.shared.domain.exceptions import (
    BusinessRuleViolationError,
    EntityNotFoundError,
)
from src.shared.infrastructure.logging import get_logger
from src.shared.infrastructure.validation import (
    AuthenticationErrorResponse,
    AuthorizationErrorResponse,
    BusinessRuleViolationResponse,
    EntityNotFoundResponse,
    RateLimitErrorResponse,
    ServerErrorResponse,
    ValidationErrorResponse,
    format_validation_errors,
)


class ErrorHandler:
    """
    Centralized error handler for the application.
    
    Attributes:
        app: The FastAPI application.
        logger: The logger for the error handler.
    """
    
    def __init__(self, app: FastAPI) -> None:
        """Initialize the error handler."""
        self.app = app
        self.logger = get_logger("marketplace.error_handler")
        self._register_handlers()
    
    def _register_handlers(self) -> None:
        """Register all error handlers."""
        
        @self.app.exception_handler(ValidationError)
        async def validation_error_handler(request: Request, exc: ValidationError) -> JSONResponse:  # noqa: F841
            """
            Handle Pydantic validation errors.

            Args:
                request: The request object.
                exc: The validation error.

            Returns:
                JSONResponse: The response object.
            """
            return await self._handle_validation_error(request, exc)
        
        @self.app.exception_handler(RequestValidationError)
        async def request_validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:  # noqa: F841
            """
            Handle FastAPI request validation errors.

            Args:
                request: The request object.
                exc: The request validation error.

            Returns:
                JSONResponse: The response object.
            """
            return await self._handle_validation_error(request, exc)
        
        @self.app.exception_handler(BusinessRuleViolationError)
        async def business_rule_violation_handler(request: Request, exc: BusinessRuleViolationError) -> JSONResponse:  # noqa: F841
            """
            Handle business rule violations.

            Args:
                request: The request object.
                exc: The business rule violation error.

            Returns:
                JSONResponse: The response object.
            """
            return await self._handle_business_rule_violation(request, exc)
        
        @self.app.exception_handler(EntityNotFoundError)
        async def entity_not_found_handler(request: Request, exc: EntityNotFoundError) -> JSONResponse:  # noqa: F841
            """
            Handle entity not found errors.

            Args:
                request: The request object.
                exc: The entity not found error.

            Returns:
                JSONResponse: The response object.
            """
            return await self._handle_entity_not_found(request, exc)
        
        @self.app.exception_handler(StarletteHTTPException)
        async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:  # noqa: F841
            """
            Handle HTTP exceptions.

            Args:
                request: The request object.
                exc: The HTTP exception.

            Returns:
                JSONResponse: The response object.
            """
            return await self._handle_http_exception(request, exc)
        
        @self.app.exception_handler(Exception)
        async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:  # noqa: F841
            """
            Handle all other exceptions.

            Args:
                request: The request object.
                exc: The exception.

            Returns:
                JSONResponse: The response object.
            """
            return await self._handle_general_exception(request, exc)
    
    async def _handle_validation_error(self, request: Request, exc: ValidationError) -> JSONResponse:
        """
        Handle validation errors.

        Args:
            request: The request object.
            exc: The validation error.

        Returns:
            JSONResponse: The response object.
        """
        # Log the error
        self.logger.error(
            f"Validation error: {exc}",
            extra={
                "request_path": request.url.path,
                "request_method": request.method,
                "error_type": "validation_error",
                "details": format_validation_errors(exc)
            }
        )
        
        # Create response
        error_response = ValidationErrorResponse(
            message="Input validation failed",
            details=format_validation_errors(exc)
        )
        
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=error_response.model_dump()
        )
    
    async def _handle_business_rule_violation(self, request: Request, exc: BusinessRuleViolationError) -> JSONResponse:
        """
        Handle business rule violations.

        Args:
            request: The request object.
            exc: The business rule violation error.

        Returns:
            JSONResponse: The response object.
        """
        # Log the error
        self.logger.warning(
            f"Business rule violation: {exc}",
            extra={
                "request_path": request.url.path,
                "request_method": request.method,
                "error_type": "business_rule_violation",
                "rule": getattr(exc, 'rule', None),
                "context": getattr(exc, 'context', None)
            }
        )
        
        # Create response
        error_response = BusinessRuleViolationResponse(
            message=str(exc),
            rule=getattr(exc, 'rule', None),
            context=getattr(exc, 'context', None)
        )
        
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=error_response.model_dump()
        )
    
    async def _handle_entity_not_found(self, request: Request, exc: EntityNotFoundError) -> JSONResponse:
        """
        Handle entity not found errors.

        Args:
            request: The request object.
            exc: The entity not found error.

        Returns:
            JSONResponse: The response object.
        """
        # Log the error
        self.logger.info(
            f"Entity not found: {exc}",
            extra={
                "request_path": request.url.path,
                "request_method": request.method,
                "error_type": "entity_not_found",
                "entity_type": getattr(exc, 'entity_type', None),
                "entity_id": getattr(exc, 'entity_id', None)
            }
        )
        
        # Create response
        error_response = EntityNotFoundResponse(
            message=str(exc),
            entity_type=getattr(exc, 'entity_type', None),
            entity_id=getattr(exc, 'entity_id', None)
        )
        
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=error_response.model_dump()
        )
    
    async def _handle_http_exception(self, request: Request, exc: StarletteHTTPException) -> JSONResponse:
        """
        Handle HTTP exceptions.

        Args:
            request: The request object.
            exc: The HTTP exception.

        Returns:
            JSONResponse: The response object.
        """
        # Log the error
        self.logger.warning(
            f"HTTP exception: {exc.status_code} - {exc.detail}",
            extra={
                "request_path": request.url.path,
                "request_method": request.method,
                "error_type": "http_exception",
                "status_code": exc.status_code
            }
        )
        
        # Handle specific HTTP status codes
        if exc.status_code == status.HTTP_401_UNAUTHORIZED:
            error_response = AuthenticationErrorResponse(
                message=exc.detail,
                code="UNAUTHORIZED"
            )
            content = error_response.model_dump()
        elif exc.status_code == status.HTTP_403_FORBIDDEN:
            error_response = AuthorizationErrorResponse(
                message=exc.detail
            )
            content = error_response.model_dump()
        elif exc.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
            error_response = RateLimitErrorResponse(
                message=exc.detail
            )
            content = error_response.model_dump()
        else:
            # Generic error response
            content = {
                "error": "HTTP error",
                "message": exc.detail,
                "status_code": exc.status_code
            }
        
        return JSONResponse(
            status_code=exc.status_code,
            content=content
        )
    
    async def _handle_general_exception(self, request: Request, exc: Exception) -> JSONResponse:
        """
        Handle general exceptions.

        Args:
            request: The request object.
            exc: The exception.

        Returns:
            JSONResponse: The response object.
        """
        # Get request ID if available
        request_id = getattr(request.state, 'request_id', None)
        
        # Log the error with full traceback
        self.logger.error(
            f"Unhandled exception: {exc}",
            extra={
                "request_path": request.url.path,
                "request_method": request.method,
                "error_type": "unhandled_exception",
                "request_id": request_id,
                "traceback": traceback.format_exc()
            }
        )
        
        # Create response
        error_response = ServerErrorResponse(
            message=str(exc),
            request_id=request_id
        )
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response.model_dump()
        )


class ErrorMiddleware:
    """
    Middleware for error handling and logging.
    
    Attributes:
        app: The FastAPI application.
        logger: The logger for the error middleware.
    """
    
    def __init__(self, app: FastAPI) -> None:
        """
        Initialize the error middleware.

        Args:
            app: The FastAPI application.
        """
        self.app = app
        self.logger = get_logger("marketplace.error_middleware")
    
    async def __call__(self, scope: dict, receive: Any, send: Any) -> None:
        """
        Process request and handle errors.

        Args:
            scope: The scope of the request.
            receive: The receive function.
            send: The send function.
        """
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        try:
            await self.app(scope, receive, send)
        except Exception as exc:
            # Log the error
            self.logger.error(
                f"Middleware caught exception: {exc}",
                extra={
                    "path": scope.get("path", "unknown"),
                    "method": scope.get("method", "unknown"),
                    "error_type": "middleware_exception",
                    "traceback": traceback.format_exc()
                }
            )
            
            # Re-raise to let FastAPI handle it
            raise


# Custom exception classes
class AuthenticationError(Exception):
    """
    Authentication error.
    
    Attributes:
        message: The error message.
        code: The error code.
    """
    
    def __init__(self, message: str, code: Optional[str] = None) -> None:
        """
        Initialize the authentication error.

        Args:
            message: The error message.
            code: The error code.
        """
        self.message = message
        self.code = code
        super().__init__(self.message)


class AuthorizationError(Exception):
    """
    Authorization error.
    
    Attributes:
        message: The error message.
        required_permissions: The required permissions.
    """
    
    def __init__(self, message: str, required_permissions: Optional[list] = None) -> None:
        """
        Initialize the authorization error.

        Args:
            message: The error message.
            required_permissions: The required permissions.
        """
        self.message = message
        self.required_permissions = required_permissions or []
        super().__init__(self.message)


class RateLimitError(Exception):
    """
    Rate limit error.
    
    Attributes:
        message: The error message.
        retry_after: The time to wait before retrying.
        limit: The rate limit.
    """

    def __init__(self, message: str, retry_after: Optional[int] = None, limit: Optional[int] = None) -> None:
        """
        Initialize the rate limit error.

        Args:
            message: The error message.
            retry_after: The time to wait before retrying.
            limit: The rate limit.
        """
        self.message = message
        self.retry_after = retry_after
        self.limit = limit
        super().__init__(self.message)


class DatabaseError(Exception):
    """
    Database error.
    
    Attributes:
        message: The error message.
        operation: The operation that caused the error.
        table: The table that caused the error.
    """

    def __init__(self, message: str, operation: Optional[str] = None, table: Optional[str] = None) -> None:
        """
        Initialize the database error.

        Args:
            message: The error message.
            operation: The operation that caused the error.
            table: The table that caused the error.
        """
        self.message = message
        self.operation = operation
        self.table = table
        super().__init__(self.message)


class CacheError(Exception):
    """
    Cache error.
    
    Attributes:
        message: The error message.
        operation: The operation that caused the error.
        key: The key that caused the error.
    """

    def __init__(self, message: str, operation: Optional[str] = None, key: Optional[str] = None) -> None:
        """
        Initialize the cache error.

        Args:
            message: The error message.
            operation: The operation that caused the error.
            key: The key that caused the error.
        """
        self.message = message
        self.operation = operation
        self.key = key
        super().__init__(self.message)


class ExternalServiceError(Exception):
    """
    External service error.
    
    Attributes:
        message: The error message.
        service: The service that caused the error.
        status_code: The status code of the error.
    """

    def __init__(self, message: str, service: Optional[str] = None, status_code: Optional[int] = None) -> None:
        """
        Initialize the external service error.

        Args:
            message: The error message.
            service: The service that caused the error.
            status_code: The status code of the error.
        """
        self.message = message
        self.service = service
        self.status_code = status_code
        super().__init__(self.message)


# Error context manager
class ErrorContext:
    """
    Context manager for error handling.
    
    Attributes:
        logger: The logger for the error context.
        logger_name: The name of the logger.
        context: The context of the error.
    """
    
    def __init__(self, logger_name: str = "marketplace.error_context") -> None:
        """
        Initialize the error context.

        Args:
            logger_name: The name of the logger.
        """
        self.logger = get_logger(logger_name)
        self.logger_name = logger_name
        self.context: Dict[str, Any] = {}
    
    def __enter__(self) -> "ErrorContext":
        """
        Enter the error context.

        Returns:
            ErrorContext: The error context.
        """
        return self
    
    def __exit__(self, exc_type: Optional[Type[BaseException]], exc_val: Optional[BaseException], exc_tb: Optional[TracebackType]) -> None:
        """
        Exit the error context.

        Args:
            exc_type: The type of the exception.
            exc_val: The value of the exception.
            exc_tb: The traceback of the exception.

        Returns:
            bool: False to re-raise the exception.
        """
        if exc_type is not None:
            self.logger.error(
                f"Error in context: {exc_val}",
                extra={
                    "error_type": exc_type.__name__,
                    "error_message": str(exc_val),
                    "context": self.context,
                    "traceback": traceback.format_exc()
                }
            )
        return False  # Re-raise the exception
    
    def add_context(self, **kwargs: Any) -> "ErrorContext":
        """
        Add context information.

        Args:
            **kwargs: The context information.

        Returns:
            ErrorContext: The error context.
        """
        self.context.update(kwargs)
        return self


# Error decorators
def handle_errors(logger_name: str = "marketplace.error_handler") -> Callable:
    """
    Decorator to handle errors in functions.

    Args:
        logger_name: The name of the logger.

    Returns:
        Callable: The decorator.
    """

    def decorator(func: Callable) -> Callable:
        """
        Decorator to handle errors in functions.

        Args:
            func: The function to handle errors.

        Returns:
            Callable: The decorated function.
        """
        logger = get_logger(logger_name)
        
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            """
            Async wrapper to handle errors.

            Args:
                *args: The arguments.
                **kwargs: The keyword arguments.

            Returns:
                Any: The result of the function.
            """
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                logger.error(
                    f"Error in {func.__name__}: {e}",
                    extra={
                        "function": func.__name__,
                        "error_type": type(e).__name__,
                        "error_message": str(e),
                        "traceback": traceback.format_exc()
                    }
                )
                raise
        
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            """
            Sync wrapper to handle errors.

            Args:
                *args: The arguments.
                **kwargs: The keyword arguments.

            Returns:
                Any: The result of the function.
            """
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(
                    f"Error in {func.__name__}: {e}",
                    extra={
                        "function": func.__name__,
                        "error_type": type(e).__name__,
                        "error_message": str(e),
                        "traceback": traceback.format_exc()
                    }
                )
                raise
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def retry_on_error(max_retries: int = 3, delay: float = 1.0, backoff: float = 2.0) -> Callable:
    """
    Decorator to retry functions on error.

    Args:
        max_retries: The maximum number of retries.
        delay: The delay between retries.
        backoff: The backoff factor.

    Returns:
        Callable: The decorator.
    """
    
    def decorator(func: Callable) -> Callable:
        """
        Decorator to retry functions on error.

        Args:
            func: The function to retry.

        Returns:
            Callable: The decorated function.
        """
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            """
            Async wrapper to retry functions on error.

            Args:
                *args: The arguments.
                **kwargs: The keyword arguments.

            Returns:
                Any: The result of the function.
            """
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        await asyncio.sleep(delay * (backoff ** attempt))
            
            raise last_exception
        
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            """
            Sync wrapper to retry functions on error.

            Args:
                *args: The arguments.
                **kwargs: The keyword arguments.

            Returns:
                Any: The result of the function.
            """
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        time.sleep(delay * (backoff ** attempt))
            
            raise last_exception
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def handle_validation_error(exc: ValidationError) -> Dict[str, Any]:
    """
    Handle validation errors and return formatted error response.
    
    Args:
        exc: The validation error.
        
    Returns:
        Dict containing formatted validation error response.
    """
    errors = format_validation_errors(exc.errors())
    
    return {
        "error": "Validation Error",
        "message": "The provided data is invalid",
        "details": errors,
        "status_code": 422
    }


def handle_not_found_error(exc: EntityNotFoundError) -> Dict[str, Any]:
    """
    Handle not found errors and return formatted error response.
    
    Args:
        exc: The entity not found error.
        
    Returns:
        Dict containing formatted not found error response.
    """
    return {
        "error": "Not Found",
        "message": str(exc),
        "entity_type": getattr(exc, 'entity_type', None),
        "entity_id": getattr(exc, 'entity_id', None),
        "status_code": 404
    }


def handle_database_error(exc: DatabaseError) -> Dict[str, Any]:
    """
    Handle database errors and return formatted error response.
    
    Args:
        exc: The database error.
        
    Returns:
        Dict containing formatted database error response.
    """
    return {
        "error": "Database Error",
        "message": str(exc),
        "operation": getattr(exc, 'operation', None),
        "table": getattr(exc, 'table', None),
        "status_code": 500
    }


def handle_external_service_error(exc: ExternalServiceError) -> Dict[str, Any]:
    """
    Handle external service errors and return formatted error response.
    
    Args:
        exc: The external service error.
        
    Returns:
        Dict containing formatted external service error response.
    """
    return {
        "error": "External Service Error",
        "message": str(exc),
        "service": getattr(exc, 'service', None),
        "status_code": getattr(exc, 'status_code', 500)
    }