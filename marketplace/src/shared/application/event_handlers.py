"""Shared event handlers for cross-cutting concerns."""

import logging
from typing import Any, Dict

from src.shared.domain.events import DomainEvent, EventHandler

logger = logging.getLogger(__name__)


class NotificationEventHandler(EventHandler):
    """Handler for sending notifications based on domain events."""

    def __init__(self):
        self.notification_service = None  # Would be injected in real implementation

    async def handle(self, event: DomainEvent) -> None:
        """Handle domain event and send appropriate notifications."""
        try:
            notification_data = self._create_notification_data(event)
            await self._send_notification(notification_data)
            logger.info(f"Notification sent for event {event.event_type}")
        except Exception as e:
            logger.error(
                f"Failed to send notification for event {event.event_type}: {e}"
            )

    def _create_notification_data(self, event: DomainEvent) -> Dict[str, Any]:
        """Create notification data based on event type."""
        event_data = event.to_dict()

        # Map event types to notification templates
        notification_mapping = {
            "OrderCreated": {
                "type": "order_confirmation",
                "subject": "Order Confirmation",
                "template": "order_created.html",
                "recipient_field": "customer_id"
            },
            "OrderConfirmed": {
                "type": "order_status_update",
                "subject": "Order Confirmed",
                "template": "order_confirmed.html",
                "recipient_field": "customer_id"
            },
            "OrderShipped": {
                "type": "order_status_update",
                "subject": "Order Shipped",
                "template": "order_shipped.html",
                "recipient_field": "customer_id"
            },
            "UserCreated": {
                "type": "welcome",
                "subject": "Welcome to Marketplace",
                "template": "welcome_user.html",
                "recipient_field": "user_id"
            },
            "SellerVerified": {
                "type": "seller_status",
                "subject": "Seller Account Verified",
                "template": "seller_verified.html",
                "recipient_field": "seller_id"
            }
        }

        event_config = notification_mapping.get(event.event_type, {})

        return {
            "notification_type": event_config.get("type", "general"),
            "subject": event_config.get("subject", f"Event: {event.event_type}"),
            "template": event_config.get("template", "default.html"),
            "recipient": event_data.get(
                event_config.get("recipient_field", "aggregate_id")
            ),
            "event_data": event_data
        }

    async def _send_notification(self, notification_data: Dict[str, Any]) -> None:
        """Send notification (placeholder for real implementation)."""
        # In real implementation, this would integrate with email/SMS service
        logger.info(f"Would send notification: {notification_data}")


class AuditEventHandler(EventHandler):
    """Handler for audit logging of domain events."""

    def __init__(self):
        self.audit_repository = None  # Would be injected in real implementation

    async def handle(self, event: DomainEvent) -> None:
        """Handle domain event and log audit information."""
        try:
            audit_record = self._create_audit_record(event)
            await self._save_audit_record(audit_record)
            logger.info(f"Audit record created for event {event.event_type}")
        except Exception as e:
            logger.error(
                f"Failed to create audit record for event {event.event_type}: {e}"
            )

    def _create_audit_record(self, event: DomainEvent) -> Dict[str, Any]:
        """Create audit record from domain event."""
        event_data = event.to_dict()

        return {
            "event_id": str(event.event_id),
            "event_type": event.event_type,
            "aggregate_id": event.aggregate_id,
            "occurred_on": event.occurred_on.isoformat(),
            "version": event.version,
            "event_data": event_data,
            "user_id": self._extract_user_id(event_data),
            "action": self._determine_action(event.event_type)
        }

    def _extract_user_id(self, event_data: Dict[str, Any]) -> str:
        """Extract user ID from event data."""
        # Try to find user-related fields in event data
        user_fields = ["user_id", "customer_id", "seller_id"]
        for field in user_fields:
            if field in event_data:
                return event_data[field]
        return "system"

    def _determine_action(self, event_type: str) -> str:
        """Determine action type from event type."""
        action_mapping = {
            "Created": "CREATE",
            "Updated": "UPDATE",
            "Deleted": "DELETE",
            "Confirmed": "CONFIRM",
            "Cancelled": "CANCEL",
            "Shipped": "SHIP",
            "Delivered": "DELIVER",
            "Verified": "VERIFY",
            "Deactivated": "DEACTIVATE"
        }

        for suffix, action in action_mapping.items():
            if event_type.endswith(suffix):
                return action

        return "OTHER"

    async def _save_audit_record(self, audit_record: Dict[str, Any]) -> None:
        """Save audit record (placeholder for real implementation)."""
        # In real implementation, this would save to audit database
        logger.info(f"Would save audit record: {audit_record}")


class EventSourcingHandler(EventHandler):
    """Handler for event sourcing - storing events for aggregate reconstruction."""

    def __init__(self):
        self.event_store = None  # Would be injected in real implementation

    async def handle(self, event: DomainEvent) -> None:
        """Handle domain event and store for event sourcing."""
        try:
            await self._store_event(event)
            logger.info(f"Event stored for event sourcing: {event.event_type}")
        except Exception as e:
            logger.error(f"Failed to store event for event sourcing: {e}")

    async def _store_event(self, event: DomainEvent) -> None:
        """Store event in event store (placeholder for real implementation)."""
        # In real implementation, this would save to event store
        event_data = event.to_dict()
        logger.info(f"Would store event in event store: {event_data}")
