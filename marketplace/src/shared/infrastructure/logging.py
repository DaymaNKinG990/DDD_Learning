"""Logging configuration and utilities."""

import asyncio
import logging
import logging.config
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from pydantic import BaseModel

from src.shared.infrastructure.config import settings


class LogConfig(BaseModel):
    """Logging configuration model."""
    
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
    """Structured logger with context support."""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.context: Dict[str, Any] = {}
    
    def bind(self, **kwargs) -> "StructuredLogger":
        """Bind context to logger."""
        new_logger = StructuredLogger(self.logger.name)
        new_logger.context = {**self.context, **kwargs}
        return new_logger
    
    def _format_message(self, message: str) -> str:
        """Format message with context."""
        if self.context:
            context_str = " | ".join(f"{k}={v}" for k, v in self.context.items())
            return f"{message} | {context_str}"
        return message
    
    def debug(self, message: str, **kwargs):
        """Log debug message."""
        self.logger.debug(self._format_message(message), extra=kwargs)
    
    def info(self, message: str, **kwargs):
        """Log info message."""
        self.logger.info(self._format_message(message), extra=kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message."""
        self.logger.warning(self._format_message(message), extra=kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message."""
        self.logger.error(self._format_message(message), extra=kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log critical message."""
        self.logger.critical(self._format_message(message), extra=kwargs)
    
    def exception(self, message: str, **kwargs):
        """Log exception message."""
        self.logger.exception(self._format_message(message), extra=kwargs)


class RequestLogger:
    """Request-specific logger."""
    
    def __init__(self, request_id: str, user_id: Optional[str] = None):
        self.request_id = request_id
        self.user_id = user_id
        self.logger = StructuredLogger("marketplace.api").bind(
            request_id=request_id,
            user_id=user_id
        )
    
    def log_request(self, method: str, path: str, status_code: int, duration: float):
        """Log HTTP request."""
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
    
    def log_error(self, error: Exception, context: Optional[Dict[str, Any]] = None):
        """Log error with context."""
        self.logger.error(
            f"Error: {str(error)}",
            extra={
                "error_type": type(error).__name__,
                "error_message": str(error),
                "context": context or {},
                "event_type": "error"
            }
        )


def setup_logging():
    """Setup logging configuration."""
    # Create logs directory
    Path("logs").mkdir(exist_ok=True)
    
    # Configure logging
    log_config = LogConfig()
    logging.config.dictConfig(log_config.model_dump())


def get_logger(name: str) -> StructuredLogger:
    """Get structured logger by name."""
    return StructuredLogger(name)


def get_request_logger(request_id: str, user_id: Optional[str] = None) -> RequestLogger:
    """Get request-specific logger."""
    return RequestLogger(request_id, user_id)


# Performance logging decorator
def log_performance(logger_name: str = "marketplace"):
    """Decorator to log function performance."""
    def decorator(func):
        logger = get_logger(logger_name)
        
        async def async_wrapper(*args, **kwargs):
            start_time = datetime.utcnow()
            try:
                result = await func(*args, **kwargs)
                duration = (datetime.utcnow() - start_time).total_seconds()
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
                duration = (datetime.utcnow() - start_time).total_seconds()
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
        
        def sync_wrapper(*args, **kwargs):
            start_time = datetime.utcnow()
            try:
                result = func(*args, **kwargs)
                duration = (datetime.utcnow() - start_time).total_seconds()
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
                duration = (datetime.utcnow() - start_time).total_seconds()
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