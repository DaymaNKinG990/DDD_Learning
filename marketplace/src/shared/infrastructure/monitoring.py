"""Monitoring and metrics for marketplace services."""

# Python imports
import time
from typing import Any, Callable
from functools import wraps
from prometheus_client import (
    Counter,
    Histogram,
    Gauge,
    Summary,
    generate_latest,
    CONTENT_TYPE_LATEST,
    CollectorRegistry
)
from fastapi import Response
from fastapi.responses import PlainTextResponse


# Create a registry for metrics
registry = CollectorRegistry()

# HTTP metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total number of HTTP requests',
    ['method', 'endpoint', 'status'],
    registry=registry
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint'],
    registry=registry
)

http_request_size_bytes = Histogram(
    'http_request_size_bytes',
    'HTTP request size in bytes',
    ['method', 'endpoint'],
    registry=registry
)

http_response_size_bytes = Histogram(
    'http_response_size_bytes',
    'HTTP response size in bytes',
    ['method', 'endpoint'],
    registry=registry
)

# Business metrics
orders_created_total = Counter(
    'orders_created_total',
    'Total number of orders created',
    ['status'],
    registry=registry
)

products_viewed_total = Counter(
    'products_viewed_total',
    'Total number of product views',
    ['product_id'],
    registry=registry
)

users_registered_total = Counter(
    'users_registered_total',
    'Total number of user registrations',
    registry=registry
)

reviews_created_total = Counter(
    'reviews_created_total',
    'Total number of reviews created',
    ['rating'],
    registry=registry
)

# System metrics
database_connections_active = Gauge(
    'database_connections_active',
    'Number of active database connections',
    registry=registry
)

redis_connections_active = Gauge(
    'redis_connections_active',
    'Number of active Redis connections',
    registry=registry
)

cache_hit_ratio = Gauge(
    'cache_hit_ratio',
    'Cache hit ratio',
    registry=registry
)

# Error metrics
errors_total = Counter(
    'errors_total',
    'Total number of errors',
    ['service', 'error_type'],
    registry=registry
)

# Performance metrics
service_response_time = Summary(
    'service_response_time_seconds',
    'Service response time in seconds',
    ['service', 'operation'],
    registry=registry
)

# Health check metric
health_check_status = Gauge(
    'health_check_status',
    'Health check status (1 = healthy, 0 = unhealthy)',
    ['service'],
    registry=registry
)


def track_request_metrics(func: Callable) -> Callable:
    """
    Decorator to track request metrics.

    Args:
        func: The function to track.

    Returns:
        Callable: The decorated function.
    """
    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        """
        Wrapper to track request metrics.

        Args:
            *args: The arguments.
            **kwargs: The keyword arguments.

        Returns:
            Any: The result of the function.
        """
        start_time = time.time()
        
        try:
            result = await func(*args, **kwargs)
            status = 200
            return result
        except Exception as e:
            status = 500
            errors_total.labels(service=func.__module__, error_type=type(e).__name__).inc()
            raise
        finally:
            duration = time.time() - start_time
            http_request_duration_seconds.labels(
                method="POST",  # Default, should be extracted from request
                endpoint=func.__name__
            ).observe(duration)
    
    return wrapper


def track_business_metrics(metric_name: str, labels: dict = None) -> Callable:
    """
    Decorator to track business metrics.

    Args:
        metric_name: The name of the metric.
        labels: The labels for the metric.

    Returns:
        Callable: The decorated function.
    """
    def decorator(func: Callable) -> Callable:
        """
        Decorator to track business metrics.

        Args:
            func: The function to track.

        Returns:
            Callable: The decorated function.
        """
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            """
            Wrapper to track business metrics.

            Args:
                *args: The arguments.
                **kwargs: The keyword arguments.
            """
            try:
                result = await func(*args, **kwargs)
                
                # Increment appropriate metric based on metric_name
                if metric_name == "orders_created":
                    orders_created_total.labels(status="success").inc()
                elif metric_name == "products_viewed":
                    product_id = kwargs.get('product_id', 'unknown')
                    products_viewed_total.labels(product_id=product_id).inc()
                elif metric_name == "users_registered":
                    users_registered_total.inc()
                elif metric_name == "reviews_created":
                    rating = kwargs.get('rating', 'unknown')
                    reviews_created_total.labels(rating=str(rating)).inc()
                
                return result
            except Exception as e:
                errors_total.labels(service=func.__module__, error_type=type(e).__name__).inc()
                raise
        
        return wrapper
    return decorator


def track_performance(service: str, operation: str) -> Callable:
    """
    Decorator to track performance metrics.

    Args:
        service: The name of the service.
        operation: The name of the operation.

    Returns:
        Callable: The decorated function.
    """
    def decorator(func: Callable) -> Callable:
        """
        Decorator to track performance metrics.

        Args:
            func: The function to track.

        Returns:
            Callable: The decorated function.
        """
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            """
            Wrapper to track performance metrics.

            Args:
                *args: The arguments.
                **kwargs: The keyword arguments.
            """
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                service_response_time.labels(service=service, operation=operation).observe(duration)
        
        return wrapper
    return decorator


async def metrics_endpoint() -> Response:
    """
    Prometheus metrics endpoint.

    Returns:
        Response: The response.
    """
    return PlainTextResponse(
        generate_latest(registry),
        media_type=CONTENT_TYPE_LATEST
    )


def update_health_status(service: str, is_healthy: bool) -> None:
    """
    Update health check status.

    Args:
        service: The name of the service.
        is_healthy: The health status.
    """
    health_check_status.labels(service=service).set(1 if is_healthy else 0)


def update_database_connections(count: int) -> None:
    """
    Update database connections metric.

    Args:
        count: The number of database connections.
    """
    database_connections_active.set(count)


def update_redis_connections(count: int) -> None:
    """
    Update Redis connections metric.

    Args:
        count: The number of Redis connections.
    """
    redis_connections_active.set(count)


def update_cache_hit_ratio(ratio: float) -> None:
    """
    Update cache hit ratio metric.

    Args:
        ratio: The cache hit ratio.
    """
    cache_hit_ratio.set(ratio)


class MetricsMiddleware:
    """
    FastAPI middleware for collecting metrics.

    Attributes:
        app: The FastAPI app.
    """
    
    def __init__(self, app) -> None:
        """
        Initialize the metrics middleware.

        Args:
            app: The FastAPI app.
        """
        self.app = app
    
    async def __call__(self, scope: dict, receive: Callable, send: Callable) -> None:
        """
        Call the middleware.

        Args:
            scope: The scope.
            receive: The receive function.
            send: The send function.
        """
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        start_time = time.time()
        method = scope["method"]
        path = scope["path"]
        
        # Track request start
        http_requests_total.labels(method=method, endpoint=path, status="started").inc()
        
        async def send_wrapper(message: dict) -> None:
            """
            Wrapper to send the response.

            Args:
                message: The message.
            """
            if message["type"] == "http.response.start":
                status = message["status"]
                http_requests_total.labels(method=method, endpoint=path, status=status).inc()
            
            await send(message)
        
        try:
            await self.app(scope, receive, send_wrapper)
        except Exception as e:
            errors_total.labels(service="fastapi", error_type=type(e).__name__).inc()
            raise
        finally:
            duration = time.time() - start_time
            http_request_duration_seconds.labels(method=method, endpoint=path).observe(duration) 