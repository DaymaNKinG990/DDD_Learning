"""Catalog microservice main application."""

# Python imports
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from typing import Any, Generator
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Local imports
from src.catalog.application.services import CatalogService
from src.catalog.infrastructure.repositories import InMemoryProductRepository, InMemoryCategoryRepository, InMemoryBrandRepository
from src.interfaces.api.controllers import catalog_router
from src.shared.infrastructure.database import close_db, init_db
from src.shared.infrastructure.middleware import (
    CacheMiddleware,
    LoggingMiddleware,
    RateLimitMiddleware,
    SecurityMiddleware,
)
from src.shared.infrastructure.error_handlers import ErrorHandler
from src.shared.infrastructure.monitoring import metrics_endpoint, update_health_status, MetricsMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI) -> Generator[None, None, None]:
    """
    Lifespan event handler for database initialization and cleanup.
    
    Args:
        app: The FastAPI app.

    Returns:
        Generator[None, None, None]: A generator that yields None.
    """
    # Startup
    await init_db()
    update_health_status("catalog", True)
    yield
    # Shutdown
    await close_db()
    update_health_status("catalog", False)


# Create FastAPI app
app = FastAPI(
    title="Catalog Service",
    description="Catalog microservice for marketplace",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
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
app.add_middleware(RateLimitMiddleware)
app.add_middleware(CacheMiddleware)
app.add_middleware(MetricsMiddleware)

# Include routers
app.include_router(catalog_router, prefix="/catalog", tags=["catalog"])

# Add metrics endpoint
app.add_api_route("/metrics", metrics_endpoint, methods=["GET"])



@app.get("/")
async def root() -> dict[str, Any]:
    """
    Root endpoint.
    
    Returns:
        dict[str, Any]: The root endpoint response.
    """
    return {
        "message": "Catalog Service",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "products": "/catalog/products",
            "categories": "/catalog/categories",
            "brands": "/catalog/brands"
        }
    }

@app.get("/health")
async def health_check() -> dict[str, Any]:
    """
    Health check endpoint.
    
    Returns:
        dict[str, Any]: The health check endpoint response.
    """
    update_health_status("catalog", True)
    return {
        "status": "healthy",
        "service": "catalog",
        "timestamp": datetime.now(UTC).isoformat(),
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001) 