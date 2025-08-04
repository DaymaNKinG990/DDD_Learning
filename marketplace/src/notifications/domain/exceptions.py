"""Domain exceptions for notifications module."""

from src.shared.domain.exceptions import DomainException


class NotificationNotFoundError(DomainException):
    """Raised when a notification is not found."""
    pass


class InvalidNotificationDataError(DomainException):
    """Raised when notification data is invalid."""
    pass


class NotificationAlreadyExistsError(DomainException):
    """Raised when trying to create a notification that already exists."""
    pass


class InvalidNotificationTypeError(DomainException):
    """Raised when notification type is invalid."""
    pass


class NotificationDeliveryError(DomainException):
    """Raised when notification delivery fails."""
    pass


class InvalidRecipientError(DomainException):
    """Raised when notification recipient is invalid."""
    pass


class BatchNotFoundError(DomainException):
    """Raised when a notification batch is not found."""
    pass 


class SubscriptionNotFoundError(DomainException):
    """Raised when a subscription is not found."""
    pass 


class InvalidBatchDataError(DomainException):
    """Raised when batch data is invalid."""
    pass 