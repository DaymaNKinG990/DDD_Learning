"""Orders microservice main application."""

from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.orders.application.services import OrderService
from src.orders.infrastructure.repositories import InMemoryOrderRepository
from src.interfaces.api.controllers import router as orders_router
from src.shared.infrastructure.database import close_db, init_db
from src.shared.infrastructure.middleware import (
    CacheMiddleware,
    LoggingMiddleware,
    RateLimitMiddleware,
    SecurityMiddleware,
)
from src.shared.infrastructure.error_handlers import ErrorHandler


# Create FastAPI app
app = FastAPI(
    title="Orders Service",
    description="Orders microservice for marketplace",
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

# Include routers
app.include_router(orders_router, prefix="/orders", tags=["orders"])

# Database events
@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    await init_db()


@app.on_event("shutdown")
async def shutdown_event():
    """Close database on shutdown."""
    await close_db()


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Orders Service",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "orders": "/orders",
            "order_items": "/orders/items",
        },
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "orders",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002) 