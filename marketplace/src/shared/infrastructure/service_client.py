"""Service client for inter-service communication."""

import asyncio
from typing import Any, Dict, Optional
import httpx
from pydantic import BaseModel

from src.shared.infrastructure.logging import get_logger
from src.shared.infrastructure.error_handlers import ExternalServiceError


class ServiceClient:
    """HTTP client for inter-service communication."""
    
    def __init__(self, base_url: str, timeout: float = 30.0):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.logger = get_logger(f"marketplace.service_client.{base_url}")
        self._client: Optional[httpx.AsyncClient] = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout,
            headers={"Content-Type": "application/json"}
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self._client:
            await self._client.aclose()
    
    async def get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make GET request."""
        if not self._client:
            raise RuntimeError("ServiceClient must be used as async context manager")
        
        try:
            self.logger.info(f"GET {path}", extra={"path": path, "params": params})
            response = await self._client.get(path, params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            self.logger.error(f"HTTP error: {e.response.status_code}", extra={"status_code": e.response.status_code})
            raise ExternalServiceError(
                message=f"Service returned {e.response.status_code}",
                service=self.base_url,
                status_code=e.response.status_code
            )
        except httpx.RequestError as e:
            self.logger.error(f"Request error: {e}", extra={"error": str(e)})
            raise ExternalServiceError(
                message=f"Request failed: {str(e)}",
                service=self.base_url
            )
    
    async def post(self, path: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make POST request."""
        if not self._client:
            raise RuntimeError("ServiceClient must be used as async context manager")
        
        try:
            self.logger.info(f"POST {path}", extra={"path": path, "data": data})
            response = await self._client.post(path, json=data)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            self.logger.error(f"HTTP error: {e.response.status_code}", extra={"status_code": e.response.status_code})
            raise ExternalServiceError(
                message=f"Service returned {e.response.status_code}",
                service=self.base_url,
                status_code=e.response.status_code
            )
        except httpx.RequestError as e:
            self.logger.error(f"Request error: {e}", extra={"error": str(e)})
            raise ExternalServiceError(
                message=f"Request failed: {str(e)}",
                service=self.base_url
            )
    
    async def put(self, path: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make PUT request."""
        if not self._client:
            raise RuntimeError("ServiceClient must be used as async context manager")
        
        try:
            self.logger.info(f"PUT {path}", extra={"path": path, "data": data})
            response = await self._client.put(path, json=data)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            self.logger.error(f"HTTP error: {e.response.status_code}", extra={"status_code": e.response.status_code})
            raise ExternalServiceError(
                message=f"Service returned {e.response.status_code}",
                service=self.base_url,
                status_code=e.response.status_code
            )
        except httpx.RequestError as e:
            self.logger.error(f"Request error: {e}", extra={"error": str(e)})
            raise ExternalServiceError(
                message=f"Request failed: {str(e)}",
                service=self.base_url
            )
    
    async def delete(self, path: str) -> Dict[str, Any]:
        """Make DELETE request."""
        if not self._client:
            raise RuntimeError("ServiceClient must be used as async context manager")
        
        try:
            self.logger.info(f"DELETE {path}", extra={"path": path})
            response = await self._client.delete(path)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            self.logger.error(f"HTTP error: {e.response.status_code}", extra={"status_code": e.response.status_code})
            raise ExternalServiceError(
                message=f"Service returned {e.response.status_code}",
                service=self.base_url,
                status_code=e.response.status_code
            )
        except httpx.RequestError as e:
            self.logger.error(f"Request error: {e}", extra={"error": str(e)})
            raise ExternalServiceError(
                message=f"Request failed: {str(e)}",
                service=self.base_url
            )


class ServiceRegistry:
    """Registry for service URLs."""
    
    def __init__(self):
        self.services = {
            "catalog": "http://catalog:8001",
            "orders": "http://orders:8002",
            "users": "http://users:8003",
            "auth": "http://auth:8004",
            "reviews": "http://reviews:8005",
            "notifications": "http://notifications:8006",
        }
    
    def get_service_url(self, service_name: str) -> str:
        """Get service URL by name."""
        if service_name not in self.services:
            raise ValueError(f"Unknown service: {service_name}")
        return self.services[service_name]
    
    def get_client(self, service_name: str) -> ServiceClient:
        """Get service client by name."""
        url = self.get_service_url(service_name)
        return ServiceClient(url)


# Global service registry
service_registry = ServiceRegistry()


# Convenience functions
async def call_service(service_name: str, method: str, path: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Call service with retry logic."""
    client = service_registry.get_client(service_name)
    
    async with client:
        if method.upper() == "GET":
            return await client.get(path)
        elif method.upper() == "POST":
            return await client.post(path, data)
        elif method.upper() == "PUT":
            return await client.put(path, data)
        elif method.upper() == "DELETE":
            return await client.delete(path)
        else:
            raise ValueError(f"Unsupported method: {method}")


async def call_service_with_retry(
    service_name: str, 
    method: str, 
    path: str, 
    data: Optional[Dict[str, Any]] = None,
    max_retries: int = 3,
    delay: float = 1.0
) -> Dict[str, Any]:
    """Call service with retry logic."""
    last_exception = None
    
    for attempt in range(max_retries):
        try:
            return await call_service(service_name, method, path, data)
        except ExternalServiceError as e:
            last_exception = e
            if attempt < max_retries - 1:
                await asyncio.sleep(delay * (2 ** attempt))  # Exponential backoff
    
    raise last_exception 