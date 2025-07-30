"""Error handling and exception handlers for FastAPI."""

import traceback
from typing import Any, Dict, Optional

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

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
    """Centralized error handler for the application."""
    
    def __init__(self, app: FastAPI):
        self.app = app
        self.logger = get_logger("marketplace.error_handler")
        self._register_handlers()
    
    def _register_handlers(self):
        """Register all error handlers."""
        
        @self.app.exception_handler(ValidationError)
        async def validation_error_handler(request: Request, exc: ValidationError):
            """Handle Pydantic validation errors."""
            return await self._handle_validation_error(request, exc)
        
        @self.app.exception_handler(RequestValidationError)
        async def request_validation_error_handler(request: Request, exc: RequestValidationError):
            """Handle FastAPI request validation errors."""
            return await self._handle_validation_error(request, exc)
        
        @self.app.exception_handler(BusinessRuleViolationError)
        async def business_rule_violation_handler(request: Request, exc: BusinessRuleViolationError):
            """Handle business rule violations."""
            return await self._handle_business_rule_violation(request, exc)
        
        @self.app.exception_handler(EntityNotFoundError)
        async def entity_not_found_handler(request: Request, exc: EntityNotFoundError):
            """Handle entity not found errors."""
            return await self._handle_entity_not_found(request, exc)
        
        @self.app.exception_handler(StarletteHTTPException)
        async def http_exception_handler(request: Request, exc: StarletteHTTPException):
            """Handle HTTP exceptions."""
            return await self._handle_http_exception(request, exc)
        
        @self.app.exception_handler(Exception)
        async def general_exception_handler(request: Request, exc: Exception):
            """Handle all other exceptions."""
            return await self._handle_general_exception(request, exc)
    
    async def _handle_validation_error(
        self, 
        request: Request, 
        exc: ValidationError
    ) -> JSONResponse:
        """Handle validation errors."""
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
    
    async def _handle_business_rule_violation(
        self, 
        request: Request, 
        exc: BusinessRuleViolationError
    ) -> JSONResponse:
        """Handle business rule violations."""
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
    
    async def _handle_entity_not_found(
        self, 
        request: Request, 
        exc: EntityNotFoundError
    ) -> JSONResponse:
        """Handle entity not found errors."""
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
    
    async def _handle_http_exception(
        self, 
        request: Request, 
        exc: StarletteHTTPException
    ) -> JSONResponse:
        """Handle HTTP exceptions."""
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
        elif exc.status_code == status.HTTP_403_FORBIDDEN:
            error_response = AuthorizationErrorResponse(
                message=exc.detail
            )
        elif exc.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
            error_response = RateLimitErrorResponse(
                message=exc.detail
            )
        else:
            # Generic error response
            error_response = {
                "error": "HTTP error",
                "message": exc.detail,
                "status_code": exc.status_code
            }
        
        return JSONResponse(
            status_code=exc.status_code,
            content=error_response.model_dump() if hasattr(error_response, 'model_dump') else error_response
        )
    
    async def _handle_general_exception(
        self, 
        request: Request, 
        exc: Exception
    ) -> JSONResponse:
        """Handle general exceptions."""
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
            message="An unexpected error occurred",
            request_id=request_id
        )
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response.model_dump()
        )


class ErrorMiddleware:
    """Middleware for error handling and logging."""
    
    def __init__(self, app: FastAPI):
        self.app = app
        self.logger = get_logger("marketplace.error_middleware")
    
    async def __call__(self, scope, receive, send):
        """Process request and handle errors."""
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
    """Authentication error."""
    
    def __init__(self, message: str, code: Optional[str] = None):
        self.message = message
        self.code = code
        super().__init__(self.message)


class AuthorizationError(Exception):
    """Authorization error."""
    
    def __init__(self, message: str, required_permissions: Optional[list] = None):
        self.message = message
        self.required_permissions = required_permissions or []
        super().__init__(self.message)


class RateLimitError(Exception):
    """Rate limit error."""
    
    def __init__(self, message: str, retry_after: Optional[int] = None, limit: Optional[int] = None):
        self.message = message
        self.retry_after = retry_after
        self.limit = limit
        super().__init__(self.message)


class DatabaseError(Exception):
    """Database error."""
    
    def __init__(self, message: str, operation: Optional[str] = None, table: Optional[str] = None):
        self.message = message
        self.operation = operation
        self.table = table
        super().__init__(self.message)


class CacheError(Exception):
    """Cache error."""
    
    def __init__(self, message: str, operation: Optional[str] = None, key: Optional[str] = None):
        self.message = message
        self.operation = operation
        self.key = key
        super().__init__(self.message)


class ExternalServiceError(Exception):
    """External service error."""
    
    def __init__(self, message: str, service: Optional[str] = None, status_code: Optional[int] = None):
        self.message = message
        self.service = service
        self.status_code = status_code
        super().__init__(self.message)


# Error context manager
class ErrorContext:
    """Context manager for error handling."""
    
    def __init__(self, logger_name: str = "marketplace.error_context"):
        self.logger = get_logger(logger_name)
        self.context: Dict[str, Any] = {}
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
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
    
    def add_context(self, **kwargs):
        """Add context information."""
        self.context.update(kwargs)
        return self


# Error decorators
def handle_errors(logger_name: str = "marketplace.error_handler"):
    """Decorator to handle errors in functions."""
    def decorator(func):
        logger = get_logger(logger_name)
        
        async def async_wrapper(*args, **kwargs):
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
        
        def sync_wrapper(*args, **kwargs):
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
        
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def retry_on_error(max_retries: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """Decorator to retry functions on error."""
    import asyncio
    import time
    
    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        await asyncio.sleep(delay * (backoff ** attempt))
            
            raise last_exception
        
        def sync_wrapper(*args, **kwargs):
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