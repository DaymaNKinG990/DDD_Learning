"""Tests for shared application event handlers."""

# Python imports
import pytest
from unittest.mock import AsyncMock, Mock, patch
from datetime import datetime, timezone

# Local imports
from src.shared.application.event_handlers import (
    NotificationEventHandler,
    AuditEventHandler,
    EventSourcingHandler
)
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
        return {
            "event_id": str(self.event_id),
            "event_type": self.event_type,
            "aggregate_id": self.aggregate_id,
            "occurred_on": self.occurred_on.isoformat(),
            "version": self.version,
            "user_id": "test-user-123",
            "customer_id": "test-customer-456"
        }


class OrderCreatedEvent(DomainEvent):
    """Test order created event."""
    
    def __init__(self, **data):
        """Initialize OrderCreatedEvent."""
        super().__init__(
            event_type="OrderCreatedEvent",
            aggregate_id=data.get("aggregate_id", "test-order-123"),
            **data
        )
    
    def to_dict(self):
        return {
            "event_id": str(self.event_id),
            "event_type": self.event_type,
            "aggregate_id": self.aggregate_id,
            "occurred_on": self.occurred_on.isoformat(),
            "version": self.version,
            "customer_id": "test-customer-456"
        }


class UserCreatedEvent(DomainEvent):
    """Test user created event."""
    
    def __init__(self, **data):
        """Initialize UserCreatedEvent."""
        super().__init__(
            event_type="UserCreatedEvent",
            aggregate_id=data.get("aggregate_id", "test-user-123"),
            **data
        )
    
    def to_dict(self):
        return {
            "event_id": str(self.event_id),
            "event_type": self.event_type,
            "aggregate_id": self.aggregate_id,
            "occurred_on": self.occurred_on.isoformat(),
            "version": self.version,
            "user_id": "test-user-123"
        }


class TestNotificationEventHandler:
    """Test cases for NotificationEventHandler."""

    @pytest.fixture
    def handler(self):
        """Create notification event handler."""
        return NotificationEventHandler()

    @pytest.fixture
    def test_event(self):
        """Create test event."""
        return MockEvent()

    @pytest.fixture
    def order_created_event(self):
        """Create order created event."""
        return OrderCreatedEvent()

    @pytest.fixture
    def user_created_event(self):
        """Create user created event."""
        return UserCreatedEvent()

    def test_handler_initialization(self, handler):
        """Test handler initialization."""
        assert handler.notification_service is None

    @pytest.mark.asyncio
    async def test_handle_general_event(self, handler, test_event):
        """Test handling general event."""
        with patch.object(handler, '_send_notification') as mock_send:
            await handler.handle(test_event)
            
            mock_send.assert_called_once()
            call_args = mock_send.call_args[0][0]
            assert call_args["notification_type"] == "general"
            assert call_args["subject"] == "Event: MockEvent"
            assert call_args["template"] == "default.html"

    @pytest.mark.asyncio
    async def test_handle_order_created_event(self, handler, order_created_event):
        """Test handling order created event."""
        with patch.object(handler, '_send_notification') as mock_send:
            await handler.handle(order_created_event)
            
            mock_send.assert_called_once()
            call_args = mock_send.call_args[0][0]
            assert call_args["notification_type"] == "order_confirmation"
            assert call_args["subject"] == "Order Confirmation"
            assert call_args["template"] == "order_created.html"
            assert call_args["recipient"] == "test-customer-456"

    @pytest.mark.asyncio
    async def test_handle_user_created_event(self, handler, user_created_event):
        """Test handling user created event."""
        with patch.object(handler, '_send_notification') as mock_send:
            await handler.handle(user_created_event)
            
            mock_send.assert_called_once()
            call_args = mock_send.call_args[0][0]
            assert call_args["notification_type"] == "welcome"
            assert call_args["subject"] == "Welcome to Marketplace"
            assert call_args["template"] == "welcome_user.html"
            assert call_args["recipient"] == "test-user-123"

    @pytest.mark.asyncio
    async def test_handle_exception(self, handler, test_event):
        """Test handling exception during notification sending."""
        with patch.object(handler, '_send_notification', side_effect=Exception("Send failed")):
            # Should not raise exception, should log error
            await handler.handle(test_event)

    def test_create_notification_data_general_event(self, handler, test_event):
        """Test creating notification data for general event."""
        data = handler._create_notification_data(test_event)
        
        assert data["notification_type"] == "general"
        assert data["subject"] == "Event: MockEvent"
        assert data["template"] == "default.html"
        assert data["recipient"] == "test-user-123"  # Uses user_id from event data

    def test_create_notification_data_order_event(self, handler, order_created_event):
        """Test creating notification data for order event."""
        data = handler._create_notification_data(order_created_event)
        
        assert data["notification_type"] == "order_confirmation"
        assert data["subject"] == "Order Confirmation"
        assert data["template"] == "order_created.html"
        assert data["recipient"] == "test-customer-456"

    @pytest.mark.asyncio
    async def test_send_notification_placeholder(self, handler):
        """Test send notification placeholder method."""
        notification_data = {"test": "data"}
        # Should not raise exception
        await handler._send_notification(notification_data)


class TestAuditEventHandler:
    """Test cases for AuditEventHandler."""

    @pytest.fixture
    def handler(self):
        """Create audit event handler."""
        return AuditEventHandler()

    @pytest.fixture
    def test_event(self):
        """Create test event."""
        return MockEvent()

    def test_handler_initialization(self, handler):
        """Test handler initialization."""
        assert handler.audit_repository is None

    @pytest.mark.asyncio
    async def test_handle_event(self, handler, test_event):
        """Test handling event for audit."""
        with patch.object(handler, '_save_audit_record') as mock_save:
            await handler.handle(test_event)
            
            mock_save.assert_called_once()
            call_args = mock_save.call_args[0][0]
            assert call_args["event_id"] == str(test_event.event_id)
            assert call_args["event_type"] == test_event.event_type
            assert call_args["aggregate_id"] == test_event.aggregate_id
            assert call_args["user_id"] == "test-user-123"
            assert call_args["action"] == "OTHER"

    @pytest.mark.asyncio
    async def test_handle_exception(self, handler, test_event):
        """Test handling exception during audit."""
        with patch.object(handler, '_save_audit_record', side_effect=Exception("Save failed")):
            # Should not raise exception, should log error
            await handler.handle(test_event)

    def test_create_audit_record(self, handler, test_event):
        """Test creating audit record."""
        record = handler._create_audit_record(test_event)
        
        assert record["event_id"] == str(test_event.event_id)
        assert record["event_type"] == test_event.event_type
        assert record["aggregate_id"] == test_event.aggregate_id
        assert record["user_id"] == "test-user-123"
        assert record["action"] == "OTHER"

    def test_extract_user_id_from_user_id(self, handler):
        """Test extracting user ID from user_id field."""
        event_data = {"user_id": "user-123", "other_field": "value"}
        user_id = handler._extract_user_id(event_data)
        assert user_id == "user-123"

    def test_extract_user_id_from_customer_id(self, handler):
        """Test extracting user ID from customer_id field."""
        event_data = {"customer_id": "customer-456", "other_field": "value"}
        user_id = handler._extract_user_id(event_data)
        assert user_id == "customer-456"

    def test_extract_user_id_from_seller_id(self, handler):
        """Test extracting user ID from seller_id field."""
        event_data = {"seller_id": "seller-789", "other_field": "value"}
        user_id = handler._extract_user_id(event_data)
        assert user_id == "seller-789"

    def test_extract_user_id_fallback(self, handler):
        """Test extracting user ID fallback to system."""
        event_data = {"other_field": "value"}
        user_id = handler._extract_user_id(event_data)
        assert user_id == "system"

    def test_determine_action_created(self, handler):
        """Test determining action for Created event."""
        action = handler._determine_action("OrderCreated")
        assert action == "CREATE"

    def test_determine_action_updated(self, handler):
        """Test determining action for Updated event."""
        action = handler._determine_action("UserUpdated")
        assert action == "UPDATE"

    def test_determine_action_deleted(self, handler):
        """Test determining action for Deleted event."""
        action = handler._determine_action("ProductDeleted")
        assert action == "DELETE"

    def test_determine_action_confirmed(self, handler):
        """Test determining action for Confirmed event."""
        action = handler._determine_action("OrderConfirmed")
        assert action == "CONFIRM"

    def test_determine_action_cancelled(self, handler):
        """Test determining action for Cancelled event."""
        action = handler._determine_action("OrderCancelled")
        assert action == "CANCEL"

    def test_determine_action_shipped(self, handler):
        """Test determining action for Shipped event."""
        action = handler._determine_action("OrderShipped")
        assert action == "SHIP"

    def test_determine_action_delivered(self, handler):
        """Test determining action for Delivered event."""
        action = handler._determine_action("OrderDelivered")
        assert action == "DELIVER"

    def test_determine_action_verified(self, handler):
        """Test determining action for Verified event."""
        action = handler._determine_action("SellerVerified")
        assert action == "VERIFY"

    def test_determine_action_deactivated(self, handler):
        """Test determining action for Deactivated event."""
        action = handler._determine_action("UserDeactivated")
        assert action == "DEACTIVATE"

    def test_determine_action_unknown(self, handler):
        """Test determining action for unknown event."""
        action = handler._determine_action("UnknownEvent")
        assert action == "OTHER"

    @pytest.mark.asyncio
    async def test_save_audit_record_placeholder(self, handler):
        """Test save audit record placeholder method."""
        audit_record = {"test": "data"}
        # Should not raise exception
        await handler._save_audit_record(audit_record)


class TestEventSourcingHandler:
    """Test cases for EventSourcingHandler."""

    @pytest.fixture
    def handler(self):
        """Create event sourcing handler."""
        return EventSourcingHandler()

    @pytest.fixture
    def test_event(self):
        """Create test event."""
        return MockEvent()

    def test_handler_initialization(self, handler):
        """Test handler initialization."""
        assert handler.event_store is None

    @pytest.mark.asyncio
    async def test_handle_event(self, handler, test_event):
        """Test handling event for event sourcing."""
        with patch.object(handler, '_store_event') as mock_store:
            await handler.handle(test_event)
            
            mock_store.assert_called_once_with(test_event)

    @pytest.mark.asyncio
    async def test_handle_exception(self, handler, test_event):
        """Test handling exception during event sourcing."""
        with patch.object(handler, '_store_event', side_effect=Exception("Store failed")):
            # Should not raise exception, should log error
            await handler.handle(test_event)

    @pytest.mark.asyncio
    async def test_store_event_placeholder(self, handler, test_event):
        """Test store event placeholder method."""
        # Should not raise exception
        await handler._store_event(test_event) 