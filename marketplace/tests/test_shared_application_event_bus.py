"""Tests for shared application event bus."""

# Python imports
import pytest
from unittest.mock import AsyncMock, Mock

# Local imports
from src.shared.application.event_bus import EventBus
from src.shared.domain.events import DomainEvent


class MockEvent(DomainEvent):
    """Mock event for testing."""
    
    def __init__(self, **data):
        """Initialize MockEvent."""
        super().__init__(
            event_type="MockEvent",
            aggregate_id=data.get("aggregate_id", "test-aggregate"),
            **data
        )
    
    def to_dict(self):
        return {"test": "data"}


class TestEventBus:
    """Test cases for EventBus."""

    @pytest.fixture
    def event_bus(self):
        """Create event bus instance."""
        return EventBus()

    @pytest.fixture
    def test_event(self):
        """Create test event."""
        return MockEvent()

    @pytest.fixture
    def mock_handler(self):
        """Create mock handler."""
        return AsyncMock()

    def test_event_bus_initialization(self, event_bus):
        """Test event bus initialization."""
        assert event_bus._handlers == {}

    def test_subscribe_new_event_type(self, event_bus, mock_handler):
        """Test subscribing to new event type."""
        event_bus.subscribe("MockEvent", mock_handler)
        
        assert "MockEvent" in event_bus._handlers
        assert len(event_bus._handlers["MockEvent"]) == 1
        assert event_bus._handlers["MockEvent"][0] == mock_handler

    def test_subscribe_multiple_handlers(self, event_bus):
        """Test subscribing multiple handlers to same event type."""
        handler1 = AsyncMock()
        handler2 = AsyncMock()
        
        event_bus.subscribe("MockEvent", handler1)
        event_bus.subscribe("MockEvent", handler2)
        
        assert len(event_bus._handlers["MockEvent"]) == 2
        assert handler1 in event_bus._handlers["MockEvent"]
        assert handler2 in event_bus._handlers["MockEvent"]

    @pytest.mark.asyncio
    async def test_publish_event_with_handlers(self, event_bus, test_event, mock_handler):
        """Test publishing event with registered handlers."""
        event_bus.subscribe("MockEvent", mock_handler)
        
        await event_bus.publish(test_event)
        
        mock_handler.assert_called_once_with(test_event)

    @pytest.mark.asyncio
    async def test_publish_event_without_handlers(self, event_bus, test_event):
        """Test publishing event without registered handlers."""
        # Should not raise any exception
        await event_bus.publish(test_event)

    @pytest.mark.asyncio
    async def test_publish_event_multiple_handlers(self, event_bus, test_event):
        """Test publishing event with multiple handlers."""
        handler1 = AsyncMock()
        handler2 = AsyncMock()
        
        event_bus.subscribe("MockEvent", handler1)
        event_bus.subscribe("MockEvent", handler2)
        
        await event_bus.publish(test_event)
        
        handler1.assert_called_once_with(test_event)
        handler2.assert_called_once_with(test_event)

    @pytest.mark.asyncio
    async def test_publish_different_event_types(self, event_bus):
        """Test publishing different event types."""
        event1 = MockEvent()
        event2 = MockEvent()
        
        handler1 = AsyncMock()
        handler2 = AsyncMock()
        
        event_bus.subscribe("MockEvent", handler1)
        event_bus.subscribe("AnotherEvent", handler2)
        
        await event_bus.publish(event1)
        
        handler1.assert_called_once_with(event1)
        handler2.assert_not_called()

    def test_unsubscribe_handler(self, event_bus, mock_handler):
        """Test unsubscribing handler."""
        event_bus.subscribe("MockEvent", mock_handler)
        event_bus.unsubscribe("MockEvent", mock_handler)
        
        assert "MockEvent" not in event_bus._handlers

    def test_unsubscribe_handler_multiple_handlers(self, event_bus):
        """Test unsubscribing specific handler when multiple exist."""
        handler1 = AsyncMock()
        handler2 = AsyncMock()
        
        event_bus.subscribe("MockEvent", handler1)
        event_bus.subscribe("MockEvent", handler2)
        event_bus.unsubscribe("MockEvent", handler1)
        
        assert len(event_bus._handlers["MockEvent"]) == 1
        assert event_bus._handlers["MockEvent"][0] == handler2

    def test_unsubscribe_nonexistent_event_type(self, event_bus, mock_handler):
        """Test unsubscribing from nonexistent event type."""
        # Should not raise any exception
        event_bus.unsubscribe("NonexistentEvent", mock_handler)

    def test_unsubscribe_nonexistent_handler(self, event_bus):
        """Test unsubscribing nonexistent handler."""
        handler1 = AsyncMock()
        handler2 = AsyncMock()
        
        event_bus.subscribe("MockEvent", handler1)
        event_bus.unsubscribe("MockEvent", handler2)
        
        assert len(event_bus._handlers["MockEvent"]) == 1
        assert event_bus._handlers["MockEvent"][0] == handler1

    @pytest.mark.asyncio
    async def test_handler_exception_handling(self, event_bus, test_event):
        """Test that handler exceptions don't affect other handlers."""
        handler1 = AsyncMock(side_effect=Exception("Handler error"))
        handler2 = AsyncMock()
        
        event_bus.subscribe("MockEvent", handler1)
        event_bus.subscribe("MockEvent", handler2)
        
        # Should not raise exception, handler2 should still be called
        await event_bus.publish(test_event)
        
        handler1.assert_called_once_with(test_event)
        handler2.assert_called_once_with(test_event)

    @pytest.mark.asyncio
    async def test_event_type_detection(self, event_bus):
        """Test that event type is correctly detected from event instance."""
        test_event = MockEvent()
        mock_handler = AsyncMock()
        
        event_bus.subscribe("MockEvent", mock_handler)
        await event_bus.publish(test_event)
        
        mock_handler.assert_called_once_with(test_event) 