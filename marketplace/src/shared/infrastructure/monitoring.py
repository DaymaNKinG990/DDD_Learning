"""Monitoring and metrics for marketplace services."""

import time
from typing import Callable, Any
from functools import wraps

from prometheus_client import (
    Counter,
    Histogram,
    Gauge,
    Summary,
    generate_latest,
    CONTENT_TYPE_LATEST,
    CollectorRegistry,
    multiprocess,
)
from fastapi import Request, Response
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
    """Decorator to track request metrics."""
    @wraps(func)
    async def wrapper(*args, **kwargs):
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


def track_business_metrics(metric_name: str, labels: dict = None):
    """Decorator to track business metrics."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
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


def track_performance(service: str, operation: str):
    """Decorator to track performance metrics."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
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
    """Prometheus metrics endpoint."""
    return PlainTextResponse(
        generate_latest(registry),
        media_type=CONTENT_TYPE_LATEST
    )


def update_health_status(service: str, is_healthy: bool):
    """Update health check status."""
    health_check_status.labels(service=service).set(1 if is_healthy else 0)


def update_database_connections(count: int):
    """Update database connections metric."""
    database_connections_active.set(count)


def update_redis_connections(count: int):
    """Update Redis connections metric."""
    redis_connections_active.set(count)


def update_cache_hit_ratio(ratio: float):
    """Update cache hit ratio metric."""
    cache_hit_ratio.set(ratio)


class MetricsMiddleware:
    """FastAPI middleware for collecting metrics."""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        start_time = time.time()
        method = scope["method"]
        path = scope["path"]
        
        # Track request start
        http_requests_total.labels(method=method, endpoint=path, status="started").inc()
        
        async def send_wrapper(message):
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