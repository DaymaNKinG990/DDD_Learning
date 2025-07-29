"""Base repository implementations for the infrastructure layer."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, List, Optional, TypeVar

T = TypeVar("T")


class BaseRepository(ABC, Generic[T]):
    """Base repository interface."""
    
    def __init__(self):
        """Initialize repository."""
        self._storage: Dict[str, T] = {}
    
    @abstractmethod
    async def save(self, entity: T) -> T:
        """Save entity."""
        pass
    
    @abstractmethod
    async def get_by_id(self, entity_id: Any) -> Optional[T]:
        """Get entity by ID."""
        pass
    
    @abstractmethod
    async def delete(self, entity_id: Any) -> None:
        """Delete entity."""
        pass
    
    @abstractmethod
    async def list_all(self) -> List[T]:
        """List all entities."""
        pass


class InMemoryRepository(BaseRepository[T]):
    """In-memory repository implementation for testing."""
    
    def __init__(self):
        """Initialize in-memory repository."""
        super().__init__()
        self._counter = 0
    
    async def save(self, entity: T) -> T:
        """Save entity to memory."""
        entity_id = getattr(entity, 'id', None)
        if entity_id:
            self._storage[str(entity_id)] = entity
        else:
            self._counter += 1
            # This is a simplified approach - in real implementation you'd generate proper ID
            self._storage[str(self._counter)] = entity
        return entity
    
    async def get_by_id(self, entity_id: Any) -> Optional[T]:
        """Get entity by ID from memory."""
        return self._storage.get(str(entity_id))
    
    async def delete(self, entity_id: Any) -> None:
        """Delete entity from memory."""
        self._storage.pop(str(entity_id), None)
    
    async def list_all(self) -> List[T]:
        """List all entities from memory."""
        return list(self._storage.values())
    
    def clear(self) -> None:
        """Clear all data (for testing)."""
        self._storage.clear()
        self._counter = 0