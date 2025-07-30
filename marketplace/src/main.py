"""Main FastAPI application for the marketplace."""

from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.interfaces.api.controllers import catalog_router, orders_router
from src.interfaces.api.users_controllers import router as users_router
from src.interfaces.api.reviews_controllers import router as reviews_router
from src.interfaces.api.notifications_controllers import router as notifications_router
from src.interfaces.api.auth_controllers import router as auth_router
from src.shared.infrastructure.database import close_db, init_db
from src.shared.infrastructure.middleware import (
    CacheMiddleware,
    LoggingMiddleware,
    RateLimitMiddleware,
    SecurityMiddleware,
)
from src.shared.infrastructure.error_handlers import ErrorHandler

app = FastAPI(
    title="Marketplace DDD API",
    description="API for the marketplace built with DDD principles",
    version="0.1.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(catalog_router)
app.include_router(orders_router)
app.include_router(users_router)
# Add error handlers
error_handler = ErrorHandler(app)

# Add middleware
app.add_middleware(SecurityMiddleware)
app.add_middleware(LoggingMiddleware)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(CacheMiddleware)

app.include_router(reviews_router)
app.include_router(notifications_router)
app.include_router(auth_router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to Marketplace DDD API",
        "version": "0.1.0",
        "docs": "/docs",
        "endpoints": {
            "catalog": "/catalog",
            "orders": "/orders",
            "users": "/users",
            "reviews": "/reviews",
            "notifications": "/notifications",
            "auth": "/auth",
        },
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    await init_db()


@app.on_event("shutdown")
async def shutdown_event():
    """Close database connections on shutdown."""
    await close_db()
