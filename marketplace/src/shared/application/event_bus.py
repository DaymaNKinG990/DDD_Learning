"""Event bus for domain events."""
# Python imports
from typing import Dict, List, Callable

# Local imports
from src.shared.domain.events import DomainEvent


class EventBus:
    """Simple event bus for domain events."""
    
    def __init__(self) -> None:
        """Initialize the event bus."""
        self._handlers: Dict[str, List[Callable]] = {}
    
    def subscribe(self, event_type: str, handler: Callable[[DomainEvent], None]) -> None:
        """
        Subscribe to an event type.

        Args:
            event_type: The type of event to subscribe to.
            handler: The handler to call when the event is published.
        """
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)
    
    async def publish(self, event: DomainEvent) -> None:
        """
        Publish an event to all subscribers.

        Args:
            event: The event to publish.
        """
        event_type = type(event).__name__
        if event_type in self._handlers:
            for handler in self._handlers[event_type]:
                await handler(event)
    
    def unsubscribe(self, event_type: str, handler: Callable[[DomainEvent], None]) -> None:
        """
        Unsubscribe from an event type.

        Args:
            event_type: The type of event to unsubscribe from.
            handler: The handler to unsubscribe.
        """
        if event_type in self._handlers:
            self._handlers[event_type] = [
                h for h in self._handlers[event_type] if h != handler
            ] 