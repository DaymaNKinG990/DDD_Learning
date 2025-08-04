"""Tests for interfaces.api.reviews_controllers module."""

import pytest
from src.interfaces.api.reviews_controllers import router


class TestRouterConfiguration:
    """Test router configuration."""

    def test_reviews_router_prefix(self):
        """Test reviews router prefix."""
        assert router.prefix == "/reviews"
        assert "reviews" in router.tags

    def test_reviews_router_routes(self):
        """Test reviews router has expected routes."""
        routes = [route.path for route in router.routes]
        # Check that router has some routes (exact paths may vary)
        assert len(routes) > 0
        # All routes should start with /reviews
        for route in routes:
            assert route.startswith("/reviews") 