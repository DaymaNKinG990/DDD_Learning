"""Base Entity class for all domain entities."""

from dataclasses import asdict, dataclass
from typing import Any, Dict, Generic, TypeVar
from uuid import UUID, uuid4

T = TypeVar("T")


@dataclass(frozen=True)
class EntityId:
    """Base class for entity identifiers."""

    value: UUID = uuid4()

    def __str__(self) -> str:
        return str(self.value)

    def __hash__(self) -> int:
        return hash(self.value)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, EntityId):
            return False
        return self.value == other.value


@dataclass
class Entity(Generic[T]):
    """Base class for all domain entities."""

    id: T

    def __hash__(self) -> int:
        """Return hash of the entity."""
        return hash(self.id)

    def __eq__(self, other: Any) -> bool:
        """Check if entities are equal."""
        if not isinstance(other, self.__class__):
            return False
        return self.id == other.id

    def to_dict(self) -> Dict[str, Any]:
        """Convert entity to dictionary."""
        return asdict(self)
