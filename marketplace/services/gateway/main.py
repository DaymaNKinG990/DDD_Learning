"""API Gateway for marketplace microservices."""

# Python imports
from datetime import UTC, datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
from typing import Dict, Any

# Local imports
from src.shared.infrastructure.middleware import (
    LoggingMiddleware,
    SecurityMiddleware,
)
from src.shared.infrastructure.error_handlers import ErrorHandler


# Service URLs
SERVICES = {
    "catalog": "http://catalog:8001",
    "orders": "http://orders:8002", 
    "users": "http://users:8003",
    "auth": "http://auth:8004",
    "reviews": "http://reviews:8005",
    "notifications": "http://notifications:8006",
}

# Create FastAPI app
app = FastAPI(
    title="Marketplace API Gateway",
    description="API Gateway for marketplace microservices",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add error handlers
error_handler = ErrorHandler(app)

# Add middleware
app.add_middleware(SecurityMiddleware)
app.add_middleware(LoggingMiddleware)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Marketplace API Gateway",
        "version": "1.0.0",
        "docs": "/docs",
        "services": {
            "catalog": "/catalog",
            "orders": "/orders", 
            "users": "/users",
            "auth": "/auth",
            "reviews": "/reviews",
            "notifications": "/notifications",
        },
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for all services."""
    health_status = {
        "gateway": {
            "status": "healthy",
            "timestamp": datetime.now(UTC).isoformat(),
        },
        "services": {}
    }
    
    async with httpx.AsyncClient() as client:
        for service_name, service_url in SERVICES.items():
            try:
                response = await client.get(f"{service_url}/health", timeout=5.0)
                if response.status_code == 200:
                    health_status["services"][service_name] = {
                        "status": "healthy",
                        "url": service_url,
                    }
                else:
                    health_status["services"][service_name] = {
                        "status": "unhealthy",
                        "url": service_url,
                        "error": f"HTTP {response.status_code}"
                    }
            except Exception as e:
                health_status["services"][service_name] = {
                    "status": "unhealthy",
                    "url": service_url,
                    "error": str(e)
                }
    
    return health_status


@app.get("/catalog/{path:path}")
async def catalog_proxy(path: str) -> Dict[str, Any]:
    """
    Proxy requests to catalog service.
    
    Args:
        path: The path to proxy the request to.

    Returns:
        Dict[str, Any]: The response from the catalog service.
    """
    return await proxy_request("catalog", path)


@app.post("/catalog/{path:path}")
async def catalog_proxy_post(path: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Proxy POST requests to catalog service.
    
    Args:
        path: The path to proxy the request to.
        data: The data to send in the POST request.

    Returns:
        Dict[str, Any]: The response from the catalog service.
    """
    return await proxy_request("catalog", path, method="POST", data=data)


@app.get("/orders/{path:path}")
async def orders_proxy(path: str) -> Dict[str, Any]:
    """
    Proxy requests to orders service.
    
    Args:
        path: The path to proxy the request to.

    Returns:
        Dict[str, Any]: The response from the orders service.
    """
    return await proxy_request("orders", path)


@app.post("/orders/{path:path}")
async def orders_proxy_post(path: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Proxy POST requests to orders service.
    
    Args:
        path: The path to proxy the request to.
        data: The data to send in the POST request.

    Returns:
        Dict[str, Any]: The response from the orders service.
    """
    return await proxy_request("orders", path, method="POST", data=data)


@app.get("/users/{path:path}")
async def users_proxy(path: str) -> Dict[str, Any]:
    """
    Proxy requests to users service.
    
    Args:
        path: The path to proxy the request to.

    Returns:
        Dict[str, Any]: The response from the users service.
    """
    return await proxy_request("users", path)


@app.post("/users/{path:path}")
async def users_proxy_post(path: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Proxy POST requests to users service.
    
    Args:
        path: The path to proxy the request to.
        data: The data to send in the POST request.

    Returns:
        Dict[str, Any]: The response from the users service.
    """
    return await proxy_request("users", path, method="POST", data=data)


@app.get("/auth/{path:path}")
async def auth_proxy(path: str) -> Dict[str, Any]:
    """
    Proxy requests to auth service.
    
    Args:
        path: The path to proxy the request to.

    Returns:
        Dict[str, Any]: The response from the auth service.
    """
    return await proxy_request("auth", path)


@app.post("/auth/{path:path}")
async def auth_proxy_post(path: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Proxy POST requests to auth service.
    
    Args:
        path: The path to proxy the request to.
        data: The data to send in the POST request.

    Returns:
        Dict[str, Any]: The response from the auth service.
    """
    return await proxy_request("auth", path, method="POST", data=data)


@app.get("/reviews/{path:path}")
async def reviews_proxy(path: str) -> Dict[str, Any]:
    """
    Proxy requests to reviews service.
    
    Args:
        path: The path to proxy the request to.

    Returns:
        Dict[str, Any]: The response from the reviews service.
    """
    return await proxy_request("reviews", path)


@app.post("/reviews/{path:path}")
async def reviews_proxy_post(path: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Proxy POST requests to reviews service.
    
    Args:
        path: The path to proxy the request to.
        data: The data to send in the POST request.

    Returns:
        Dict[str, Any]: The response from the reviews service.
    """
    return await proxy_request("reviews", path, method="POST", data=data)


@app.get("/notifications/{path:path}")
async def notifications_proxy(path: str) -> Dict[str, Any]:
    """
    Proxy requests to notifications service.
    
    Args:
        path: The path to proxy the request to.

    Returns:
        Dict[str, Any]: The response from the notifications service.
    """
    return await proxy_request("notifications", path)


@app.post("/notifications/{path:path}")
async def notifications_proxy_post(path: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Proxy POST requests to notifications service.
    
    Args:
        path: The path to proxy the request to.
        data: The data to send in the POST request.

    Returns:
        Dict[str, Any]: The response from the notifications service.
    """
    return await proxy_request("notifications", path, method="POST", data=data)


async def proxy_request(service_name: str, path: str, method: str = "GET", data: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Proxy request to microservice.
    
    Args:
        service_name: The name of the service to proxy the request to.
        path: The path to proxy the request to.
        method: The HTTP method to use for the request.
        data: The data to send in the request.

    Returns:
        Dict[str, Any]: The response from the microservice.
    """
    if service_name not in SERVICES:
        raise HTTPException(status_code=404, detail=f"Service {service_name} not found")
    
    service_url = SERVICES[service_name]
    full_url = f"{service_url}/{path}"
    
    try:
        async with httpx.AsyncClient() as client:
            if method == "GET":
                response = await client.get(full_url, timeout=30.0)
            elif method == "POST":
                response = await client.post(full_url, json=data, timeout=30.0)
            else:
                raise HTTPException(status_code=405, detail=f"Method {method} not supported")
            
            return response.json()
            
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail=f"Service {service_name} timeout")
    except httpx.RequestError as e:
        raise HTTPException(status_code=502, detail=f"Service {service_name} error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gateway error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 