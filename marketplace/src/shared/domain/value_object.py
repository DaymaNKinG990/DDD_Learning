"""Base ValueObject class for all domain value objects."""

from abc import ABC, abstractmethod
from typing import Any, Dict

from pydantic import BaseModel, ConfigDict


class ValueObject(BaseModel, ABC):
    """Base class for all domain value objects."""
    
    model_config = ConfigDict(frozen=True)
    
    @abstractmethod
    def __hash__(self) -> int:
        """Return hash of the value object."""
        pass
    
    def __eq__(self, other: Any) -> bool:
        """Check if value objects are equal."""
        if not isinstance(other, self.__class__):
            return False
        return self.model_dump() == other.model_dump()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert value object to dictionary."""
        return self.model_dump()