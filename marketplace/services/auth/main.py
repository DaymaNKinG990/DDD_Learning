"""Authentication microservice main application."""

# Python imports
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from typing import Any, Generator
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Local imports
from src.auth.application.services import AuthenticationService
from src.auth.infrastructure.sql_repositories import SQLTokenRepository, SQLSessionRepository
from src.interfaces.api.auth_controllers import router as auth_router
from src.shared.infrastructure.database import close_db, init_db
from src.shared.infrastructure.middleware import (
    CacheMiddleware,
    LoggingMiddleware,
    RateLimitMiddleware,
    SecurityMiddleware,
)
from src.shared.infrastructure.error_handlers import ErrorHandler


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
    yield
    # Shutdown
    await close_db()


# Create FastAPI app
app = FastAPI(
    title="Authentication Service",
    description="Authentication microservice for marketplace",
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
app.include_router(auth_router, prefix="/auth", tags=["auth"])





@app.get("/")
async def root() -> dict[str, Any]:
    """
    Root endpoint.
    
    Returns:
        dict[str, Any]: The root endpoint response.
    """
    return {
        "message": "Authentication Service",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "login": "/auth/login",
            "register": "/auth/register",
            "refresh": "/auth/refresh",
            "logout": "/auth/logout",
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
        "service": "auth",
        "timestamp": datetime.now(UTC).isoformat(),
        "version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004) 