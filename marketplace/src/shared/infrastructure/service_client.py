"""Service client for inter-service communication."""

# Python imports
import asyncio
from types import TracebackType
from typing import Any, Dict, Optional, Type
import httpx

# Local imports
from src.shared.infrastructure.logging import get_logger
from src.shared.infrastructure.error_handlers import ExternalServiceError


class ServiceClient:
    """
    HTTP client for inter-service communication.
    
    Attributes:
        base_url: The base URL of the service.
        timeout: The timeout for the client.
        logger: The logger for the client.
        _client: The HTTP client.
    """
    
    def __init__(self, base_url: str, timeout: float = 30.0) -> None:
        """
        Initialize the service client.
        
        Args:
            base_url: The base URL of the service.
            timeout: The timeout for the client.
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.logger = get_logger(f"marketplace.service_client.{base_url}")
        self._client: Optional[httpx.AsyncClient] = None
    
    async def __aenter__(self) -> "ServiceClient":
        """
        Async context manager entry.
        
        Returns:
            ServiceClient: The service client.
        """
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout,
            headers={"Content-Type": "application/json"}
        )
        return self
    
    async def __aexit__(self, exc_type: Optional[Type[BaseException]], exc_val: Optional[BaseException], exc_tb: Optional[TracebackType]) -> None:
        """
        Async context manager exit.
        
        Args:
            exc_type: The type of the exception.
            exc_val: The value of the exception.
            exc_tb: The traceback of the exception.
        """
        if self._client:
            await self._client.aclose()
    
    async def get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Make GET request.
        
        Args:
            path: The path of the request.
            params: The parameters of the request.

        Returns:
            Dict[str, Any]: The response from the request.
        """
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
        """
        Make POST request.
        
        Args:
            path: The path of the request.
            data: The data of the request.

        Returns:
            Dict[str, Any]: The response from the request.
        """

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
        """
        Make PUT request.
        
        Args:
            path: The path of the request.
            data: The data of the request.

        Returns:
            Dict[str, Any]: The response from the request.
        """

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
        """
        Make DELETE request.
        
        Args:
            path: The path of the request.

        Returns:
            Dict[str, Any]: The response from the request.
        """

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
    """
    Registry for service URLs.
    
    Attributes:
        services: The services.
    """
    
    def __init__(self) -> None:
        """Initialize the service registry."""
        self.services = {
            "catalog": "http://catalog:8001",
            "orders": "http://orders:8002",
            "users": "http://users:8003",
            "auth": "http://auth:8004",
            "reviews": "http://reviews:8005",
            "notifications": "http://notifications:8006",
        }
    
    def get_service_url(self, service_name: str) -> str:
        """
        Get service URL by name.
        
        Args:
            service_name: The name of the service.

        Returns:
            str: The URL of the service.
        """
        if service_name not in self.services:
            raise ValueError(f"Unknown service: {service_name}")
        return self.services[service_name]
    
    def get_client(self, service_name: str) -> ServiceClient:
        """
        Get service client by name.
        
        Args:
            service_name: The name of the service.

        Returns:
            ServiceClient: The service client.
        """
        url = self.get_service_url(service_name)
        return ServiceClient(url)


# Global service registry
service_registry = ServiceRegistry()


# Convenience functions
async def call_service(service_name: str, method: str, path: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Call service with retry logic.
    
    Args:
        service_name: The name of the service.
        method: The method of the request.
        path: The path of the request.
        data: The data of the request.

    Returns:
        Dict[str, Any]: The response from the request.
    """
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
    """
    Call service with retry logic.
    
    Args:
        service_name: The name of the service.
        method: The method of the request.
        path: The path of the request.
        data: The data of the request.
        max_retries: The maximum number of retries.
        delay: The delay between retries.

    Returns:
        Dict[str, Any]: The response from the request.
    """
    last_exception = None
    
    for attempt in range(max_retries):
        try:
            return await call_service(service_name, method, path, data)
        except ExternalServiceError as e:
            last_exception = e
            if attempt < max_retries - 1:
                await asyncio.sleep(delay * (2 ** attempt))  # Exponential backoff
    
    raise last_exception 