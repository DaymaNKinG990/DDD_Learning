"""Domain exceptions for users module."""

from src.shared.domain.exceptions import DomainException


class UserNotFoundError(DomainException):
    """Raised when a user is not found."""
    pass


class InvalidUserDataError(DomainException):
    """Raised when user data is invalid."""
    pass


class UserAlreadyExistsError(DomainException):
    """Raised when trying to create a user that already exists."""
    pass


class InvalidEmailError(DomainException):
    """Raised when email is invalid."""
    pass


class InvalidPasswordError(DomainException):
    """Raised when password is invalid."""
    pass


class UserInactiveError(DomainException):
    """Raised when user is inactive."""
    pass


class InvalidUserRoleError(DomainException):
    """Raised when user role is invalid."""
    pass 