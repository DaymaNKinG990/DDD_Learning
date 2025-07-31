"""Event bus for domain events."""

from typing import Dict, List, Callable, Any
from src.shared.domain.events import DomainEvent


class EventBus:
    """Simple event bus for domain events."""
    
    def __init__(self):
        self._handlers: Dict[str, List[Callable]] = {}
    
    def subscribe(self, event_type: str, handler: Callable[[DomainEvent], None]) -> None:
        """Subscribe to an event type."""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)
    
    async def publish(self, event: DomainEvent) -> None:
        """Publish an event to all subscribers."""
        event_type = type(event).__name__
        if event_type in self._handlers:
            for handler in self._handlers[event_type]:
                await handler(event)
    
    def unsubscribe(self, event_type: str, handler: Callable[[DomainEvent], None]) -> None:
        """Unsubscribe from an event type."""
        if event_type in self._handlers:
            self._handlers[event_type] = [
                h for h in self._handlers[event_type] if h != handler
            ] 