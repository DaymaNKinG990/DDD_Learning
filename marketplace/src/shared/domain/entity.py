"""Base Entity class for all domain entities."""

# Python imports
from dataclasses import asdict, dataclass
from typing import Any, Dict, Generic, TypeVar
from uuid import UUID, uuid4


T = TypeVar("T")


@dataclass(frozen=True)
class EntityId:
    """
    Base class for entity identifiers.
    
    Attributes:
        value: The UUID value of the entity identifier.
    """

    value: UUID = uuid4()

    def __str__(self) -> str:
        """
        Return the string representation of the entity identifier.

        Returns:
            str: The string representation of the entity identifier.
        """
        return str(self.value)

    def __hash__(self) -> int:
        """
        Return the hash of the entity identifier.

        Returns:
            int: The hash of the entity identifier.
        """
        return hash(self.value)

    def __eq__(self, other: Any) -> bool:
        """
        Check if the entity identifier is equal to another object.

        Args:
            other: The other object to compare with.

        Returns:
            bool: True if the entity identifier is equal to the other object, False otherwise.
        """
        if not isinstance(other, EntityId):
            return False
        return self.value == other.value


@dataclass
class Entity(Generic[T]):
    """
    Base class for all domain entities.
    
    Attributes:
        id: The identifier of the entity.
    """

    id: T

    def __hash__(self) -> int:
        """
        Return the hash of the entity.

        Returns:
            int: The hash of the entity.
        """
        return hash(self.id)

    def __eq__(self, other: Any) -> bool:
        """
        Check if entities are equal.

        Args:
            other: The other entity to compare with.

        Returns:
            bool: True if the entities are equal, False otherwise.
        """
        if not isinstance(other, self.__class__):
            return False
        return self.id == other.id

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert entity to dictionary.

        Returns:
            Dict[str, Any]: The dictionary representation of the entity.
        """
        return asdict(self)
