"""FastAPI middleware for logging and caching."""

import time
import uuid
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from src.shared.infrastructure.cache import cache
from src.shared.infrastructure.logging import get_request_logger


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging HTTP requests."""
    
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        # Generate request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Get user ID from auth if available
        user_id = None
        if hasattr(request.state, "user"):
            user_id = getattr(request.state.user, "id", None)
        
        # Create request logger
        logger = get_request_logger(request_id, user_id)
        
        # Log request start
        start_time = time.time()
        logger.info(
            f"Request started: {request.method} {request.url.path}",
            extra={
                "method": request.method,
                "path": request.url.path,
                "query_params": str(request.query_params),
                "client_ip": request.client.host if request.client else "unknown",
                "user_agent": request.headers.get("user-agent", "unknown"),
                "event_type": "request_start"
            }
        )
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate duration
            duration = time.time() - start_time
            
            # Log request completion
            logger.log_request(
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                duration=duration
            )
            
            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id
            
            return response
            
        except Exception as e:
            # Calculate duration
            duration = time.time() - start_time
            
            # Log error
            logger.log_error(e, {
                "method": request.method,
                "path": request.url.path,
                "duration": duration
            })
            
            # Re-raise exception
            raise


class CacheMiddleware(BaseHTTPMiddleware):
    """Middleware for caching responses."""
    
    def __init__(
        self, 
        app, 
        cache_prefix: str = "api",
        default_ttl: int = 300,  # 5 minutes
        cacheable_methods: set = None,
        cacheable_paths: set = None
    ):
        super().__init__(app)
        self.cache_prefix = cache_prefix
        self.default_ttl = default_ttl
        self.cacheable_methods = cacheable_methods or {"GET"}
        self.cacheable_paths = cacheable_paths or {"/products", "/categories", "/brands"}
    
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        # Check if request is cacheable
        if not self._is_cacheable(request):
            return await call_next(request)
        
        # Generate cache key
        cache_key = self._generate_cache_key(request)
        
        # Try to get from cache
        cached_response = await cache.get_json(cache_key)
        if cached_response:
            # Return cached response
            response = Response(
                content=cached_response["content"],
                status_code=cached_response["status_code"],
                headers=cached_response["headers"],
                media_type=cached_response["media_type"]
            )
            response.headers["X-Cache"] = "HIT"
            return response
        
        # Process request
        response = await call_next(request)
        
        # Cache response if successful
        if response.status_code == 200:
            await self._cache_response(cache_key, response)
            response.headers["X-Cache"] = "MISS"
        
        return response
    
    def _is_cacheable(self, request: Request) -> bool:
        """Check if request is cacheable."""
        return (
            request.method in self.cacheable_methods and
            any(request.url.path.startswith(path) for path in self.cacheable_paths)
        )
    
    def _generate_cache_key(self, request: Request) -> str:
        """Generate cache key for request."""
        # Include method, path, and query parameters
        key_parts = [
            self.cache_prefix,
            request.method,
            request.url.path,
            str(sorted(request.query_params.items()))
        ]
        return ":".join(key_parts)
    
    async def _cache_response(self, cache_key: str, response: Response):
        """Cache response."""
        try:
            # Get response content
            content = b""
            async for chunk in response.body_iterator:
                content += chunk
            
            # Create cache entry
            cache_entry = {
                "content": content.decode(),
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "media_type": response.media_type
            }
            
            # Cache for default TTL
            await cache.set_json(cache_key, cache_entry, expire=self.default_ttl)
            
            # Create new response with cached content
            response = Response(
                content=content,
                status_code=response.status_code,
                headers=response.headers,
                media_type=response.media_type
            )
            
        except Exception:
            # If caching fails, just return original response
            pass


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware for rate limiting."""
    
    def __init__(
        self, 
        app, 
        requests_per_minute: int = 60,
        requests_per_hour: int = 1000
    ):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
    
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        # Get client identifier (IP or user ID)
        client_id = self._get_client_id(request)
        
        # Check rate limits
        if await self._is_rate_limited(client_id):
            return Response(
                content='{"error": "Rate limit exceeded"}',
                status_code=429,
                media_type="application/json"
            )
        
        # Increment request count
        await self._increment_request_count(client_id)
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(
            await self._get_remaining_requests(client_id)
        )
        
        return response
    
    def _get_client_id(self, request: Request) -> str:
        """Get client identifier."""
        # Use user ID if authenticated, otherwise use IP
        if hasattr(request.state, "user") and request.state.user:
            return f"user:{request.state.user.id}"
        return f"ip:{request.client.host if request.client else 'unknown'}"
    
    async def _is_rate_limited(self, client_id: str) -> bool:
        """Check if client is rate limited."""
        # Check minute limit
        minute_key = f"rate_limit:minute:{client_id}"
        minute_count = await cache.get(minute_key)
        if minute_count and int(minute_count) >= self.requests_per_minute:
            return True
        
        # Check hour limit
        hour_key = f"rate_limit:hour:{client_id}"
        hour_count = await cache.get(hour_key)
        if hour_count and int(hour_count) >= self.requests_per_hour:
            return True
        
        return False
    
    async def _increment_request_count(self, client_id: str):
        """Increment request count for client."""
        # Increment minute count
        minute_key = f"rate_limit:minute:{client_id}"
        await cache.incr(minute_key)
        await cache.expire(minute_key, 60)  # Expire in 1 minute
        
        # Increment hour count
        hour_key = f"rate_limit:hour:{client_id}"
        await cache.incr(hour_key)
        await cache.expire(hour_key, 3600)  # Expire in 1 hour
    
    async def _get_remaining_requests(self, client_id: str) -> int:
        """Get remaining requests for client."""
        minute_key = f"rate_limit:minute:{client_id}"
        minute_count = await cache.get(minute_key)
        current_count = int(minute_count) if minute_count else 0
        return max(0, self.requests_per_minute - current_count)


class SecurityMiddleware(BaseHTTPMiddleware):
    """Middleware for security headers."""
    
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        return response 