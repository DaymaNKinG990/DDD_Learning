"""Logging configuration and utilities."""

# Python imports
import asyncio
import logging
import logging.config
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Callable, Dict, Optional
from pydantic import BaseModel

# Local imports
from src.shared.infrastructure.config import settings


class LogConfig(BaseModel):
    """
    Logging configuration model.

    Attributes:
        LOGGER_NAME: The name of the logger.
        LOG_FORMAT: The format of the log messages.
        LOG_LEVEL: The level of the log messages.
    """
    
    LOGGER_NAME: str = "marketplace"
    LOG_FORMAT: str = "%(levelprefix)s | %(asctime)s | %(message)s"
    LOG_LEVEL: str = "INFO"
    
    # Logging config
    version: int = 1
    disable_existing_loggers: bool = False
    formatters: Dict[str, Dict[str, str]] = {
        "default": {
            "format": LOG_FORMAT,
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "detailed": {
            "format": "%(levelprefix)s | %(asctime)s | %(name)s | %(funcName)s:%(lineno)d | %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "json": {
            "format": '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": "%(message)s"}',
            "datefmt": "%Y-%m-%d %H:%M:%S",
        }
    }
    handlers: Dict[str, Dict[str, Any]] = {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        },
        "file": {
            "formatter": "detailed",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "logs/marketplace.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
        },
        "error_file": {
            "formatter": "detailed",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "logs/errors.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
            "level": "ERROR",
        },
        "json_file": {
            "formatter": "json",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "logs/marketplace.json",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
        }
    }
    loggers: Dict[str, Dict[str, Any]] = {
        "marketplace": {
            "handlers": ["default", "file", "error_file"],
            "level": LOG_LEVEL,
            "propagate": False,
        },
        "marketplace.api": {
            "handlers": ["default", "file", "json_file"],
            "level": LOG_LEVEL,
            "propagate": False,
        },
        "marketplace.auth": {
            "handlers": ["default", "file", "error_file"],
            "level": LOG_LEVEL,
            "propagate": False,
        },
        "marketplace.db": {
            "handlers": ["default", "file"],
            "level": "DEBUG" if settings.debug else "INFO",
            "propagate": False,
        },
        "marketplace.cache": {
            "handlers": ["default", "file"],
            "level": "DEBUG" if settings.debug else "INFO",
            "propagate": False,
        },
        "uvicorn": {
            "handlers": ["default", "file"],
            "level": "INFO",
            "propagate": False,
        },
        "uvicorn.error": {
            "level": "INFO",
        },
        "uvicorn.access": {
            "handlers": ["default", "file"],
            "level": "INFO",
            "propagate": False,
        },
    }


class StructuredLogger:
    """
    Structured logger with context support.

    Attributes:
        logger: The logger instance.
        context: The context of the logger.
    """
    
    def __init__(self, name: str) -> None:
        """
        Initialize the structured logger.

        Args:
            name: The name of the logger.
        """
        self.logger = logging.getLogger(name)
        self.context: Dict[str, Any] = {}
    
    def bind(self, **kwargs) -> "StructuredLogger":
        """
        Bind context to logger.

        Args:
            **kwargs: The context to bind.

        Returns:
            StructuredLogger: The new logger instance.
        """
        new_logger = StructuredLogger(self.logger.name)
        new_logger.context = {**self.context, **kwargs}
        return new_logger
    
    def _format_message(self, message: str) -> str:
        """
        Format message with context.

        Args:
            message: The message to format.

        Returns:
            str: The formatted message.
        """
        if self.context:
            context_str = " | ".join(f"{k}={v}" for k, v in self.context.items())
            return f"{message} | {context_str}"
        return message
    
    def debug(self, message: str, **kwargs) -> None:
        """
        Log debug message.

        Args:
            message: The message to log.
            **kwargs: The keyword arguments.
        """
        self.logger.debug(self._format_message(message), extra=kwargs)
    
    def info(self, message: str, **kwargs) -> None:
        """
        Log info message.

        Args:
            message: The message to log.
            **kwargs: The keyword arguments.
        """
        self.logger.info(self._format_message(message), extra=kwargs)
    
    def warning(self, message: str, **kwargs) -> None:
        """
        Log warning message.

        Args:
            message: The message to log.
            **kwargs: The keyword arguments.
        """
        self.logger.warning(self._format_message(message), extra=kwargs)
    
    def error(self, message: str, **kwargs) -> None:
        """
        Log error message.

        Args:
            message: The message to log.
            **kwargs: The keyword arguments.
        """
        self.logger.error(self._format_message(message), extra=kwargs)
    
    def critical(self, message: str, **kwargs) -> None:
        """
        Log critical message.

        Args:
            message: The message to log.
            **kwargs: The keyword arguments.
        """
        self.logger.critical(self._format_message(message), extra=kwargs)
    
    def exception(self, message: str, **kwargs) -> None:
        """
        Log exception message.

        Args:
            message: The message to log.
            **kwargs: The keyword arguments.
        """
        self.logger.exception(self._format_message(message), extra=kwargs)


class RequestLogger:
    """
    Request-specific logger.

    Attributes:
        request_id: The request ID.
        user_id: The user ID.
        logger: The logger instance.
    """
    
    def __init__(self, request_id: str, user_id: Optional[str] = None) -> None:
        """
        Initialize the request logger.

        Args:
            request_id: The request ID.
            user_id: The user ID.
        """
        self.request_id = request_id
        self.user_id = user_id
        self.logger = StructuredLogger("marketplace.api").bind(
            request_id=request_id,
            user_id=user_id
        )
    
    def log_request(self, method: str, path: str, status_code: int, duration: float) -> None:
        """
        Log HTTP request.

        Args:
            method: The HTTP method.
            path: The path of the request.
            status_code: The status code of the request.
            duration: The duration of the request.
        """
        self.logger.info(
            f"HTTP {method} {path} {status_code}",
            extra={
                "method": method,
                "path": path,
                "status_code": status_code,
                "duration": duration,
                "event_type": "http_request"
            }
        )
    
    def log_error(self, error: Exception, context: Optional[Dict[str, Any]] = None) -> None:
        """
        Log error with context.

        Args:
            error: The error to log.
            context: The context of the error.
        """
        self.logger.error(
            f"Error: {str(error)}",
            extra={
                "error_type": type(error).__name__,
                "error_message": str(error),
                "context": context or {},
                "event_type": "error"
            }
        )


def setup_logging() -> None:
    """Setup logging configuration."""
    # Create logs directory
    Path("logs").mkdir(exist_ok=True)
    
    # Configure logging
    log_config = LogConfig()
    logging.config.dictConfig(log_config.model_dump())


def get_logger(name: str) -> StructuredLogger:
    """
    Get structured logger by name.

    Args:
        name: The name of the logger.

    Returns:
        StructuredLogger: The structured logger.
    """
    return StructuredLogger(name)


def get_request_logger(request_id: str, user_id: Optional[str] = None) -> RequestLogger:
    """
    Get request-specific logger.

    Args:
        request_id: The request ID.
        user_id: The user ID.

    Returns:
        RequestLogger: The request-specific logger.
    """
    return RequestLogger(request_id, user_id)


# Performance logging decorator
def log_performance(logger_name: str = "marketplace") -> Callable:
    """
    Decorator to log function performance.

    Args:
        logger_name: The name of the logger.

    Returns:
        Callable: The decorator.
    """
    def decorator(func: Callable) -> Callable:
        """
        Decorator to log function performance.

        Args:
            func: The function to log.

        Returns:
            Callable: The decorated function.
        """
        logger = get_logger(logger_name)
        
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            """
            Async wrapper to log function performance.

            Args:
                *args: The arguments.
                **kwargs: The keyword arguments.

            Returns:
                Any: The result of the function.
            """
            start_time = datetime.now(UTC)
            try:
                result = await func(*args, **kwargs)
                duration = (datetime.now(UTC) - start_time).total_seconds()
                logger.info(
                    f"Function {func.__name__} completed",
                    extra={
                        "function": func.__name__,
                        "duration": duration,
                        "event_type": "performance"
                    }
                )
                return result
            except Exception as e:
                duration = (datetime.now(UTC) - start_time).total_seconds()
                logger.error(
                    f"Function {func.__name__} failed",
                    extra={
                        "function": func.__name__,
                        "duration": duration,
                        "error": str(e),
                        "event_type": "performance_error"
                    }
                )
                raise
        
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            """
            Sync wrapper to log function performance.

            Args:
                *args: The arguments.
                **kwargs: The keyword arguments.

            Returns:
                Any: The result of the function.
            """
            start_time = datetime.now(UTC)
            try:
                result = func(*args, **kwargs)
                duration = (datetime.now(UTC) - start_time).total_seconds()
                logger.info(
                    f"Function {func.__name__} completed",
                    extra={
                        "function": func.__name__,
                        "duration": duration,
                        "event_type": "performance"
                    }
                )
                return result
            except Exception as e:
                duration = (datetime.now(UTC) - start_time).total_seconds()
                logger.error(
                    f"Function {func.__name__} failed",
                    extra={
                        "function": func.__name__,
                        "duration": duration,
                        "error": str(e),
                        "event_type": "performance_error"
                    }
                )
                raise
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


# Initialize logging on module import
setup_logging() 