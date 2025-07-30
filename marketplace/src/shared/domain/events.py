"""Base domain events for shared domain."""

from abc import ABC, abstractmethod
from datetime import UTC, datetime
from typing import Any, Dict
from uuid import UUID

from pydantic import BaseModel, Field


class DomainEvent(BaseModel, ABC):
    """Base class for all domain events."""

    event_id: UUID = Field(default_factory=lambda: UUID.uuid4())
    event_type: str = Field(description="Type of the event")
    aggregate_id: str = Field(description="ID of the aggregate that raised the event")
    occurred_on: datetime = Field(default_factory=lambda: datetime.now(UTC))
    version: int = Field(default=1, description="Event version for event sourcing")

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, **data):
        super().__init__(**data)
        if not self.event_type:
            self.event_type = self.__class__.__name__

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary representation."""
        pass


class EventHandler(ABC):
    """Base interface for event handlers."""

    @abstractmethod
    async def handle(self, event: DomainEvent) -> None:
        """Handle a domain event."""
        pass


class EventBus(ABC):
    """Abstract event bus for publishing domain events."""

    @abstractmethod
    async def publish(self, event: DomainEvent) -> None:
        """Publish a domain event."""
        pass

    @abstractmethod
    async def subscribe(self, event_type: str, handler: EventHandler) -> None:
        """Subscribe to events of a specific type."""
        pass


class InMemoryEventBus(EventBus):
    """In-memory implementation of event bus."""

    def __init__(self):
        self._handlers: Dict[str, list[EventHandler]] = {}
        self._published_events: list[DomainEvent] = []

    async def publish(self, event: DomainEvent) -> None:
        """Publish a domain event."""
        self._published_events.append(event)

        # Notify all handlers for this event type
        handlers = self._handlers.get(event.event_type, [])
        for handler in handlers:
            await handler.handle(event)

    async def subscribe(self, event_type: str, handler: EventHandler) -> None:
        """Subscribe to events of a specific type."""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)

    def get_published_events(self) -> list[DomainEvent]:
        """Get all published events (for testing)."""
        return self._published_events.copy()

    def clear_events(self) -> None:
        """Clear all published events (for testing)."""
        self._published_events.clear()
