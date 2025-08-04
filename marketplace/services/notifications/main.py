"""Notifications microservice main application."""

# Python imports
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from typing import Any
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Local imports
from src.notifications.application.services import NotificationService
from src.notifications.infrastructure.repositories import InMemoryNotificationRepository, InMemoryNotificationBatchRepository, InMemoryNotificationSubscriptionRepository
from src.interfaces.api.notifications_controllers import router as notifications_router
from src.shared.infrastructure.database import close_db, init_db
from src.shared.infrastructure.middleware import (
    CacheMiddleware,
    LoggingMiddleware,
    RateLimitMiddleware,
    SecurityMiddleware,
)
from src.shared.infrastructure.error_handlers import ErrorHandler


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for database initialization and cleanup."""
    # Startup
    await init_db()
    yield
    # Shutdown
    await close_db()


# Create FastAPI app
app = FastAPI(
    title="Notifications Service",
    description="Notifications microservice for marketplace",
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

# Include routers
app.include_router(notifications_router, prefix="/notifications", tags=["notifications"])


@app.get("/")
async def root() -> dict[str, Any]:
    """
    Root endpoint.
    
    Returns:
        dict[str, Any]: The root endpoint response.
    """
    return {
        "message": "Notifications Service",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "notifications": "/notifications",
            "subscriptions": "/notifications/subscriptions",
        },
    }


@app.get("/health")
async def health_check() -> dict[str, Any]:
    """
    Health check endpoint.
    
    Returns:
        dict[str, Any]: The health check endpoint response.
    """
    return {
        "status": "healthy",
        "service": "notifications",
        "timestamp": datetime.now(UTC).isoformat(),
        "version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8006) 