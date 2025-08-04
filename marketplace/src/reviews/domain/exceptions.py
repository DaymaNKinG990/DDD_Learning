"""Domain exceptions for reviews module."""

from src.shared.domain.exceptions import DomainException

class ReviewNotFoundError(DomainException): pass
class InvalidReviewDataError(DomainException): pass
class ReviewAlreadyExistsError(DomainException): pass
class InvalidRatingError(DomainException): pass
class ReviewNotAuthorizedError(DomainException): pass
class InvalidReviewContentError(DomainException): pass


class UnauthorizedReviewError(DomainException): pass 