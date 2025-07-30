"""Validation utilities and custom validators."""

import re
from typing import Any, Dict, List, Optional, Union
from decimal import Decimal

from pydantic import BaseModel, Field, ValidationError, validator
from pydantic.types import Annotated
from typing_extensions import Literal


class ValidationErrorResponse(BaseModel):
    """Standard validation error response."""
    
    error: str = "Validation error"
    message: str
    details: Optional[List[Dict[str, Any]]] = None
    field: Optional[str] = None


class BusinessRuleViolationResponse(BaseModel):
    """Business rule violation response."""
    
    error: str = "Business rule violation"
    message: str
    rule: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


class EntityNotFoundResponse(BaseModel):
    """Entity not found response."""
    
    error: str = "Entity not found"
    message: str
    entity_type: Optional[str] = None
    entity_id: Optional[str] = None


class AuthenticationErrorResponse(BaseModel):
    """Authentication error response."""
    
    error: str = "Authentication failed"
    message: str
    code: Optional[str] = None


class AuthorizationErrorResponse(BaseModel):
    """Authorization error response."""
    
    error: str = "Authorization failed"
    message: str
    required_permissions: Optional[List[str]] = None


class RateLimitErrorResponse(BaseModel):
    """Rate limit error response."""
    
    error: str = "Rate limit exceeded"
    message: str
    retry_after: Optional[int] = None
    limit: Optional[int] = None


class ServerErrorResponse(BaseModel):
    """Server error response."""
    
    error: str = "Internal server error"
    message: str = "An unexpected error occurred"
    request_id: Optional[str] = None


# Custom validators
def validate_email(email: str) -> str:
    """Validate email format."""
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        raise ValueError("Invalid email format")
    return email.lower()


def validate_phone(phone: str) -> str:
    """Validate phone number format."""
    # Remove all non-digit characters
    digits_only = re.sub(r'\D', '', phone)
    
    # Check if it's a valid phone number (7-15 digits)
    if len(digits_only) < 7 or len(digits_only) > 15:
        raise ValueError("Phone number must be between 7 and 15 digits")
    
    return digits_only


def validate_password_strength(password: str) -> str:
    """Validate password strength."""
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters long")
    
    if not re.search(r'[A-Z]', password):
        raise ValueError("Password must contain at least one uppercase letter")
    
    if not re.search(r'[a-z]', password):
        raise ValueError("Password must contain at least one lowercase letter")
    
    if not re.search(r'\d', password):
        raise ValueError("Password must contain at least one digit")
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        raise ValueError("Password must contain at least one special character")
    
    return password


def validate_positive_decimal(value: Union[str, Decimal, float]) -> Decimal:
    """Validate positive decimal value."""
    try:
        decimal_value = Decimal(str(value))
        if decimal_value <= 0:
            raise ValueError("Value must be positive")
        return decimal_value
    except (ValueError, TypeError):
        raise ValueError("Invalid decimal value")


def validate_uuid(uuid_str: str) -> str:
    """Validate UUID format."""
    uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
    if not re.match(uuid_pattern, uuid_str.lower()):
        raise ValueError("Invalid UUID format")
    return uuid_str.lower()


def validate_url(url: str) -> str:
    """Validate URL format."""
    url_pattern = r'^https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?$'
    if not re.match(url_pattern, url):
        raise ValueError("Invalid URL format")
    return url


# Base models with common validations
class EmailField(BaseModel):
    """Email field with validation."""
    
    email: str = Field(..., description="Valid email address")
    
    @validator('email')
    def validate_email(cls, v):
        return validate_email(v)


class PasswordField(BaseModel):
    """Password field with strength validation."""
    
    password: str = Field(..., min_length=8, description="Strong password")
    
    @validator('password')
    def validate_password(cls, v):
        return validate_password_strength(v)


class PhoneField(BaseModel):
    """Phone field with validation."""
    
    phone: str = Field(..., description="Valid phone number")
    
    @validator('phone')
    def validate_phone(cls, v):
        return validate_phone(v)


class UUIDField(BaseModel):
    """UUID field with validation."""
    
    id: str = Field(..., description="Valid UUID")
    
    @validator('id')
    def validate_uuid(cls, v):
        return validate_uuid(v)


class PositiveDecimalField(BaseModel):
    """Positive decimal field with validation."""
    
    amount: Decimal = Field(..., gt=0, description="Positive decimal amount")
    
    @validator('amount', pre=True)
    def validate_positive_decimal(cls, v):
        return validate_positive_decimal(v)


class URLField(BaseModel):
    """URL field with validation."""
    
    url: str = Field(..., description="Valid URL")
    
    @validator('url')
    def validate_url(cls, v):
        return validate_url(v)


# Pagination models
class PaginationParams(BaseModel):
    """Pagination parameters."""
    
    page: int = Field(1, ge=1, description="Page number (1-based)")
    size: int = Field(10, ge=1, le=100, description="Page size (1-100)")
    
    @property
    def offset(self) -> int:
        """Calculate offset for database queries."""
        return (self.page - 1) * self.size


class PaginatedResponse(BaseModel):
    """Paginated response wrapper."""
    
    items: List[Any] = Field(..., description="List of items")
    total: int = Field(..., ge=0, description="Total number of items")
    page: int = Field(..., ge=1, description="Current page number")
    size: int = Field(..., ge=1, description="Page size")
    pages: int = Field(..., ge=0, description="Total number of pages")
    
    @validator('pages', pre=True, always=True)
    def calculate_pages(cls, v, values):
        """Calculate total pages."""
        if 'total' in values and 'size' in values:
            return (values['total'] + values['size'] - 1) // values['size']
        return v


# Sorting models
SortOrder = Literal["asc", "desc"]


class SortParams(BaseModel):
    """Sorting parameters."""
    
    field: str = Field(..., description="Field to sort by")
    order: SortOrder = Field("asc", description="Sort order (asc/desc)")


# Filter models
FilterOperator = Literal["eq", "ne", "gt", "gte", "lt", "lte", "in", "nin", "like", "ilike"]


class FilterCondition(BaseModel):
    """Single filter condition."""
    
    field: str = Field(..., description="Field to filter by")
    operator: FilterOperator = Field(..., description="Filter operator")
    value: Any = Field(..., description="Filter value")


class FilterParams(BaseModel):
    """Filter parameters."""
    
    conditions: List[FilterCondition] = Field(default_factory=list, description="Filter conditions")
    
    def add_condition(self, field: str, operator: FilterOperator, value: Any):
        """Add a filter condition."""
        self.conditions.append(FilterCondition(field=field, operator=operator, value=value))


# Search models
class SearchParams(BaseModel):
    """Search parameters."""
    
    query: str = Field(..., min_length=1, max_length=100, description="Search query")
    fields: List[str] = Field(default_factory=list, description="Fields to search in")
    fuzzy: bool = Field(False, description="Enable fuzzy search")


# Composite query models
class QueryParams(BaseModel):
    """Complete query parameters with pagination, sorting, filtering, and search."""
    
    pagination: PaginationParams = Field(default_factory=PaginationParams)
    sort: Optional[SortParams] = None
    filters: FilterParams = Field(default_factory=FilterParams)
    search: Optional[SearchParams] = None


# Validation decorators
def validate_input(model_class: type[BaseModel]):
    """Decorator to validate input data."""
    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            try:
                # Extract data from kwargs or first argument
                data = kwargs.get('data') or (args[0] if args else {})
                
                # Validate data
                validated_data = model_class(**data)
                
                # Replace data with validated data
                if 'data' in kwargs:
                    kwargs['data'] = validated_data
                elif args:
                    args = (validated_data,) + args[1:]
                
                return await func(*args, **kwargs)
            except ValidationError as e:
                raise ValidationErrorResponse(
                    message="Input validation failed",
                    details=[{"field": error["loc"][0], "message": error["msg"]} for error in e.errors()]
                )
        
        def sync_wrapper(*args, **kwargs):
            try:
                # Extract data from kwargs or first argument
                data = kwargs.get('data') or (args[0] if args else {})
                
                # Validate data
                validated_data = model_class(**data)
                
                # Replace data with validated data
                if 'data' in kwargs:
                    kwargs['data'] = validated_data
                elif args:
                    args = (validated_data,) + args[1:]
                
                return func(*args, **kwargs)
            except ValidationError as e:
                raise ValidationErrorResponse(
                    message="Input validation failed",
                    details=[{"field": error["loc"][0], "message": error["msg"]} for error in e.errors()]
                )
        
        # Return appropriate wrapper based on function type
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


# Utility functions
def format_validation_errors(validation_error: ValidationError) -> List[Dict[str, Any]]:
    """Format validation errors for API response."""
    return [
        {
            "field": ".".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"],
            "value": error.get("input")
        }
        for error in validation_error.errors()
    ]


def sanitize_input(text: str) -> str:
    """Sanitize user input to prevent injection attacks."""
    # Remove potentially dangerous characters
    dangerous_chars = ['<', '>', '"', "'", '&', ';', '(', ')', '{', '}']
    for char in dangerous_chars:
        text = text.replace(char, '')
    
    # Remove multiple spaces
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()


def validate_file_extension(filename: str, allowed_extensions: List[str]) -> bool:
    """Validate file extension."""
    if not filename:
        return False
    
    file_extension = filename.lower().split('.')[-1] if '.' in filename else ''
    return file_extension in [ext.lower() for ext in allowed_extensions]


def validate_file_size(file_size: int, max_size_mb: int) -> bool:
    """Validate file size."""
    max_size_bytes = max_size_mb * 1024 * 1024
    return file_size <= max_size_bytes 