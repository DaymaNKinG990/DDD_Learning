"""Tests for interfaces.api.notifications_controllers module."""

import pytest
from src.interfaces.api.notifications_controllers import router


class TestRouterConfiguration:
    """Test router configuration."""

    def test_notifications_router_prefix(self):
        """Test notifications router prefix."""
        assert router.prefix == "/notifications"
        assert "notifications" in router.tags

    def test_notifications_router_routes(self):
        """Test notifications router has expected routes."""
        routes = [route.path for route in router.routes]
        # Check that router has some routes (exact paths may vary)
        assert len(routes) > 0
        # All routes should start with /notifications
        for route in routes:
            assert route.startswith("/notifications") 