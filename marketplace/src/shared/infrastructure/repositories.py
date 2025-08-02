"""Base repository implementations for the infrastructure layer."""

# Python imports
from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, List, Optional, TypeVar


T = TypeVar("T")


class BaseRepository(ABC, Generic[T]):
    """
    Base repository interface.
    
    Attributes:
        _storage: The storage for the repository.
    """

    def __init__(self) -> None:
        """Initialize repository."""
        self._storage: Dict[str, T] = {}

    @abstractmethod
    async def save(self, entity: T) -> T:
        """
        Save entity.
        
        Args:
            entity: The entity to save.
        """
        pass

    @abstractmethod
    async def get_by_id(self, entity_id: Any) -> Optional[T]:
        """
        Get entity by ID.
        
        Args:
            entity_id: The ID of the entity.
        """
        pass

    @abstractmethod
    async def delete(self, entity_id: Any) -> None:
        """
        Delete entity.
        
        Args:
            entity_id: The ID of the entity.
        """
        pass

    @abstractmethod
    async def list_all(self) -> List[T]:
        """
        List all entities.
        
        Returns:
            List[T]: The list of entities.
        """
        pass


class InMemoryRepository(BaseRepository[T]):
    """
    In-memory repository implementation for testing.
    
    Attributes:
        _storage: The storage for the repository.
    """

    def __init__(self) -> None:
        """Initialize in-memory repository."""
        super().__init__()
        self._counter = 0

    async def save(self, entity: T) -> T:
        """
        Save entity to memory.
        
        Args:
            entity: The entity to save.
        """
        entity_id = getattr(entity, "id", None)
        if entity_id:
            self._storage[str(entity_id)] = entity
        else:
            self._counter += 1
            # This is a simplified approach - in real implementation
            # you'd generate proper ID
            self._storage[str(self._counter)] = entity
        return entity

    async def get_by_id(self, entity_id: Any) -> Optional[T]:
        """
        Get entity by ID from memory.
        
        Args:
            entity_id: The ID of the entity.
        """
        return self._storage.get(str(entity_id))

    async def delete(self, entity_id: Any) -> None:
        """
        Delete entity from memory.
        
        Args:
            entity_id: The ID of the entity.
        """
        self._storage.pop(str(entity_id), None)

    async def list_all(self) -> List[T]:
        """
        List all entities from memory.
        
        Returns:
            List[T]: The list of entities.
        """
        return list(self._storage.values())

    def clear(self) -> None:
        """Clear all data (for testing)."""
        self._storage.clear()
        self._counter = 0
