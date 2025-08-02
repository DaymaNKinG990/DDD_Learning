"""Base domain events for shared domain."""

# Python imports
from abc import ABC, abstractmethod
from datetime import UTC, datetime
from typing import Any
from uuid import UUID
from pydantic import BaseModel, Field


class DomainEvent(BaseModel, ABC):
    """
    Base class for all domain events.
    
    Attributes:
        event_id: The unique identifier of the event.
        event_type: The type of the event.
        aggregate_id: The ID of the aggregate that raised the event.
        occurred_on: The date and time the event occurred.
        version: The version of the event.
    """

    event_id: UUID = Field(default_factory=lambda: UUID.uuid4())
    event_type: str = Field(description="Type of the event")
    aggregate_id: str = Field(description="ID of the aggregate that raised the event")
    occurred_on: datetime = Field(default_factory=lambda: datetime.now(UTC))
    version: int = Field(default=1, description="Event version for event sourcing")

    class Config:
        """
        Configuration for the domain event.
        
        Attributes:
            arbitrary_types_allowed: Whether to allow arbitrary types.
        """

        arbitrary_types_allowed = True

    def __init__(self, **data: dict[str, Any]):
        """
        Initialize the domain event.
        
        Args:
            **data[str, Any]: The data to initialize the event with.
        """
        super().__init__(**data)
        if not self.event_type:
            self.event_type = self.__class__.__name__

    @abstractmethod
    def to_dict(self) -> dict[str, Any]:
        """
        Convert event to dictionary representation.

        Returns:
            dict[str, Any]: The dictionary representation of the event.
        """
        pass


class EventHandler(ABC):
    """
    Base interface for event handlers.
    
    Attributes:
        event_type: The type of the event to handle.
    """

    @abstractmethod
    async def handle(self, event: DomainEvent) -> None:
        """
        Handle a domain event.

        Args:
            event: The domain event to handle.
        """
        pass


class EventBus(ABC):
    """
    Abstract event bus for publishing domain events.
    
    Attributes:
        event_type: The type of the event to publish.
    """

    @abstractmethod
    async def publish(self, event: DomainEvent) -> None:
        """
        Publish a domain event.

        Args:
            event: The domain event to publish.
        """
        pass

    @abstractmethod
    async def subscribe(self, event_type: str, handler: EventHandler) -> None:
        """
        Subscribe to events of a specific type.

        Args:
            event_type: The type of the event to subscribe to.
            handler: The handler to subscribe to.
        """
        pass


class InMemoryEventBus(EventBus):
    """
    In-memory implementation of event bus.
    
    Attributes:
        _handlers: The handlers for the event bus.
        _published_events: The published events.
    """

    def __init__(self) -> None:
        """Initialize the in-memory event bus."""
        self._handlers: dict[str, list[EventHandler]] = {}
        self._published_events: list[DomainEvent] = []

    async def publish(self, event: DomainEvent) -> None:
        """
        Publish a domain event.

        Args:
            event: The domain event to publish.
        """
        self._published_events.append(event)

        # Notify all handlers for this event type
        handlers = self._handlers.get(event.event_type, [])
        for handler in handlers:
            await handler.handle(event)

    async def subscribe(self, event_type: str, handler: EventHandler) -> None:
        """
        Subscribe to events of a specific type.

        Args:
            event_type: The type of the event to subscribe to.
            handler: The handler to subscribe to.
        """
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)

    def get_published_events(self) -> list[DomainEvent]:
        """
        Get all published events (for testing).

        Returns:
            list[DomainEvent]: The published events.
        """
        return self._published_events.copy()

    def clear_events(self) -> None:
        """Clear all published events (for testing)."""
        self._published_events.clear()
