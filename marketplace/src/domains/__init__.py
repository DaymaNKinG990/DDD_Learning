"""Domain modules for modular monolith architecture."""

from .catalog import catalog_app
from .orders import orders_app
from .users import users_app
from .auth import auth_app
from .reviews import reviews_app
from .notifications import notifications_app

__all__ = [
    "catalog_app",
    "orders_app", 
    "users_app",
    "auth_app",
    "reviews_app",
    "notifications_app"
] 