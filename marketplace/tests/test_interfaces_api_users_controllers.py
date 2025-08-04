"""Tests for interfaces.api.users_controllers module."""

import pytest
from src.interfaces.api.users_controllers import router


class TestRouterConfiguration:
    """Test router configuration."""

    def test_users_router_prefix(self):
        """Test users router prefix."""
        assert router.prefix == "/users"
        assert "users" in router.tags

    def test_users_router_routes(self):
        """Test users router has expected routes."""
        routes = [route.path for route in router.routes]
        # Check that router has some routes (exact paths may vary)
        assert len(routes) > 0
        # All routes should start with /users
        for route in routes:
            assert route.startswith("/users") 