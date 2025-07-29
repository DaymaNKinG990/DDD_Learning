"""Base Entity class for all domain entities."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, TypeVar
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class EntityId(BaseModel):
    """Base class for entity identifiers."""
    
    model_config = ConfigDict(frozen=True)
    
    value: UUID = Field(default_factory=uuid4)
    
    def __str__(self) -> str:
        return str(self.value)
    
    def __hash__(self) -> int:
        return hash(self.value)
    
    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, EntityId):
            return False
        return self.value == other.value


class Entity(BaseModel, ABC, Generic[T]):
    """Base class for all domain entities."""
    
    model_config = ConfigDict(frozen=True)
    
    id: T = Field(description="Entity identifier")
    
    @abstractmethod
    def __hash__(self) -> int:
        """Return hash of the entity."""
        pass
    
    def __eq__(self, other: Any) -> bool:
        """Check if entities are equal."""
        if not isinstance(other, self.__class__):
            return False
        return self.id == other.id
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert entity to dictionary."""
        return self.model_dump()