"""Catalog microservice main application."""

from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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

# Create FastAPI app
app = FastAPI(
    title="Catalog Service",
    description="Catalog microservice for marketplace",
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
app.add_middleware(RateLimitMiddleware)
app.add_middleware(CacheMiddleware)
app.add_middleware(MetricsMiddleware)

# Include routers
app.include_router(catalog_router, prefix="/catalog", tags=["catalog"])

# Add metrics endpoint
app.add_api_route("/metrics", metrics_endpoint, methods=["GET"])

# Database events
@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    await init_db()
    update_health_status("catalog", True)

@app.on_event("shutdown")
async def shutdown_event():
    """Close database on shutdown."""
    await close_db()
    update_health_status("catalog", False)

@app.get("/")
async def root():
    """Root endpoint."""
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
async def health_check():
    """Health check endpoint."""
    update_health_status("catalog", True)
    return {
        "status": "healthy",
        "service": "catalog",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001) 