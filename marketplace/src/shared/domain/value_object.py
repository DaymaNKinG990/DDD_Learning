"""Base ValueObject class for all domain value objects."""

from dataclasses import asdict, dataclass
from typing import Any, Dict


@dataclass(frozen=True)
class ValueObject:
    """Base class for all domain value objects."""

    def __hash__(self) -> int:
        """Return hash of the value object."""
        return hash(tuple(sorted(asdict(self).items())))

    def __eq__(self, other: Any) -> bool:
        """Check if value objects are equal."""
        if not isinstance(other, self.__class__):
            return False
        return asdict(self) == asdict(other)

    def to_dict(self) -> Dict[str, Any]:
        """Convert value object to dictionary."""
        return asdict(self)
