"""Domain exceptions for the marketplace project."""


class DomainException(Exception):
    """Base exception for domain errors."""
    pass


class EntityNotFoundError(DomainException):
    """Raised when an entity is not found."""
    pass


class InvalidOperationError(DomainException):
    """Raised when an operation is invalid for the current state."""
    pass


class BusinessRuleViolationError(DomainException):
    """Raised when a business rule is violated."""
    pass


class AuthenticationError(DomainException):
    """Raised when authentication fails."""
    pass


class ConcurrencyError(DomainException):
    """Raised when there's a concurrency conflict."""
    pass


class ValidationError(DomainException):
    """Raised when validation fails."""
    pass
