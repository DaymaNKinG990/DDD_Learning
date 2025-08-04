"""Validation utilities and custom validators."""

# Python imports
import asyncio
import re
from typing import Any, Callable, Dict, List, Optional, Union
from decimal import Decimal
from pydantic import BaseModel, Field, ValidationError, field_validator
from pydantic.types import Annotated
from typing_extensions import Literal

# Type aliases for validation
SortOrder = Literal["asc", "desc"]
FilterOperator = Literal["eq", "ne", "gt", "gte", "lt", "lte", "in", "nin", "like", "ilike"]


class ValidationErrorResponse(BaseModel):
    """
    Standard validation error response.
    
    Attributes:
        error: The error message.
        message: The error message.
        details: The details of the error.
        field: The field that caused the error.
    """
    
    error: str = "Validation error"
    message: str
    details: Optional[List[Dict[str, Any]]] = None
    field: Optional[str] = None


class BusinessRuleViolationResponse(BaseModel):
    """
    Business rule violation response.
    
    Attributes:
        error: The error message.
        message: The error message.
        rule: The rule that was violated.
        context: The context of the violation.
    """
    
    error: str = "Business rule violation"
    message: str
    rule: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


class EntityNotFoundResponse(BaseModel):
    """
    Entity not found response.
    
    Attributes:
        error: The error message.
        message: The error message.
        entity_type: The type of the entity.
        entity_id: The ID of the entity.
    """
    
    error: str = "Entity not found"
    message: str
    entity_type: Optional[str] = None
    entity_id: Optional[str] = None


class AuthenticationErrorResponse(BaseModel):
    """
    Authentication error response.
    
    Attributes:
        error: The error message.
        message: The error message.
        code: The code of the error.
    """
    
    error: str = "Authentication failed"
    message: str
    code: Optional[str] = None


class AuthorizationErrorResponse(BaseModel):
    """
    Authorization error response.
    
    Attributes:
        error: The error message.
        message: The error message.
        required_permissions: The required permissions.
    """
    
    error: str = "Authorization failed"
    message: str
    required_permissions: Optional[List[str]] = None


class RateLimitErrorResponse(BaseModel):
    """
    Rate limit error response.
    
    Attributes:
        error: The error message.
        message: The error message.
        retry_after: The time to wait before retrying.
        limit: The limit of the error.
    """
    
    error: str = "Rate limit exceeded"
    message: str
    retry_after: Optional[int] = None
    limit: Optional[int] = None


class ServerErrorResponse(BaseModel):
    """
    Server error response.
    
    Attributes:
        error: The error message.
        message: The error message.
        request_id: The ID of the request.
    """
    
    error: str = "Internal server error"
    message: str
    request_id: Optional[str] = None


# Custom validators
def validate_email(email: str) -> str:
    """
    Validate email format.
    
    Args:
        email: The email to validate.

    Returns:
        str: The validated email.
        
    Raises:
        ValueError: If the email is invalid.
    """
    if email is None:
        raise ValueError("Email cannot be None")
    if not email or not email.strip():
        raise ValueError("Email cannot be empty")
    if len(email) > 254:
        raise ValueError("Email is too long")
    
    email = email.strip()
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        raise ValueError("Invalid email format")
    return email.lower()


def validate_phone(phone: str, country_code: Optional[str] = None) -> str:
    """
    Validate phone number format.
    
    Args:
        phone: The phone number to validate.
        country_code: Country code to validate (optional).

    Returns:
        str: The validated phone number.
        
    Raises:
        ValueError: If the phone number is invalid.
    """
    if phone is None:
        raise ValueError("Phone number cannot be None")
    if not phone or not phone.strip():
        raise ValueError("Phone number cannot be empty")
    
    # Remove all non-digit characters
    digits_only = re.sub(r'\D', '', phone)
    
    # Check if it's a valid phone number (7-15 digits)
    if len(digits_only) < 7 or len(digits_only) > 15:
        raise ValueError("Phone number must be between 7 and 15 digits")
    
    # Validate country code if specified
    if country_code:
        if not digits_only.startswith(country_code):
            raise ValueError(f"Phone number must start with country code {country_code}")
    
    return digits_only


def validate_password_strength(password: str) -> str:
    """
    Validate password strength.
    
    Args:
        password: The password to validate.

    Returns:
        str: The validated password.
        
    Raises:
        ValueError: If the password is too weak.
    """
    if password is None:
        raise ValueError("Password cannot be None")
    if not password:
        raise ValueError("Password cannot be empty")
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters long")
    if len(password) > 128:
        raise ValueError("Password is too long")
    
    if not re.search(r'[A-Z]', password):
        raise ValueError("Password must contain at least one uppercase letter")
    
    if not re.search(r'[a-z]', password):
        raise ValueError("Password must contain at least one lowercase letter")
    
    if not re.search(r'\d', password):
        raise ValueError("Password must contain at least one digit")
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        raise ValueError("Password must contain at least one special character")
    
    return password


def validate_password(password: str) -> str:
    """
    Validate password (alias for validate_password_strength).
    
    Args:
        password: The password to validate.
        
    Returns:
        str: The validated password.
        
    Raises:
        ValueError: If the password is too weak.
    """
    return validate_password_strength(password)


def validate_positive_decimal(value: Union[str, Decimal, float]) -> Decimal:
    """
    Validate positive decimal value.
    
    Args:
        value: The value to validate.

    Returns:
        Decimal: The validated decimal value.
    """
    try:
        decimal_value = Decimal(str(value))
        if decimal_value <= 0:
            raise ValueError("Value must be positive")
        return decimal_value
    except (ValueError, TypeError):
        raise ValueError("Invalid decimal value")


def validate_uuid(uuid_str: str, version: Optional[int] = None) -> str:
    """
    Validate UUID format.
    
    Args:
        uuid_str: The UUID to validate.
        version: The UUID version to validate (optional).

    Returns:
        str: The validated UUID.
        
    Raises:
        ValueError: If the UUID is invalid.
    """
    if uuid_str is None:
        raise ValueError("UUID cannot be None")
    if not uuid_str:
        raise ValueError("UUID cannot be empty")
    
    uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
    if not re.match(uuid_pattern, uuid_str.lower()):
        raise ValueError("Invalid UUID format")
    
    # Validate version if specified
    if version is not None:
        try:
            import uuid as uuid_module
            parsed_uuid = uuid_module.UUID(uuid_str)
            if parsed_uuid.version != version:
                raise ValueError(f"UUID version must be {version}")
        except ImportError:
            pass  # Skip version validation if uuid module not available
    
    return uuid_str.lower()


def validate_url(url: str, allowed_schemes: Optional[List[str]] = None, max_length: int = 2048) -> str:
    """
    Validate URL format.
    
    Args:
        url: The URL to validate.
        allowed_schemes: List of allowed URL schemes (default: http, https).
        max_length: Maximum URL length.

    Returns:
        str: The validated URL.
        
    Raises:
        ValueError: If the URL is invalid.
    """
    if url is None:
        raise ValueError("URL cannot be None")
    if not url:
        raise ValueError("URL cannot be empty")
    
    if len(url) > max_length:
        raise ValueError("URL is too long")
    
    # Check scheme
    if allowed_schemes is None:
        allowed_schemes = ["http", "https"]
    
    scheme_pattern = r'^(' + '|'.join(allowed_schemes) + r')://'
    if not re.match(scheme_pattern, url, re.IGNORECASE):
        raise ValueError("Invalid URL scheme")
    
    # Basic URL pattern
    url_pattern = r'^https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?$'
    if not re.match(url_pattern, url):
        raise ValueError("Invalid URL format")
    
    return url


def validate_date(date_str: str, format: str = "%Y-%m-%d", min_date: Optional[str] = None, allow_future: bool = True) -> str:
    """
    Validate date format.
    
    Args:
        date_str: The date string to validate.
        format: The expected date format.
        min_date: Minimum allowed date (optional).
        allow_future: Whether to allow future dates.

    Returns:
        str: The validated date string.
        
    Raises:
        ValueError: If the date format is invalid.
    """
    if date_str is None:
        raise ValueError("Date cannot be None")
    
    try:
        from datetime import datetime
        parsed_date = datetime.strptime(date_str, format)
        
        # Check minimum date
        if min_date:
            min_parsed = datetime.strptime(min_date, format)
            if parsed_date < min_parsed:
                raise ValueError("Date is too old")
        
        # Check future dates
        if not allow_future:
            current_date = datetime.now()
            if parsed_date > current_date:
                raise ValueError("Future dates are not allowed")
        
        return date_str
    except ValueError as e:
        if "too old" in str(e) or "not allowed" in str(e):
            raise e
        raise ValueError(f"Invalid date format. Expected format: {format}")


def validate_money_amount(amount: Union[str, Decimal, float], max_amount: Optional[Decimal] = None) -> Decimal:
    """
    Validate money amount.
    
    Args:
        amount: The amount to validate.
        max_amount: Maximum allowed amount (optional).

    Returns:
        Decimal: The validated amount.
        
    Raises:
        ValueError: If the amount is invalid.
    """
    if amount is None:
        raise ValueError("Money amount cannot be None")
    
    try:
        decimal_amount = Decimal(str(amount))
        if decimal_amount < 0:
            raise ValueError("Money amount cannot be negative")
        if decimal_amount == 0:
            raise ValueError("Money amount cannot be zero")
        
        # Check maximum amount
        max_limit = max_amount if max_amount is not None else Decimal('999999999.99')
        if decimal_amount > max_limit:
            raise ValueError("Money amount is too large")
        
        # Check precision
        if decimal_amount.as_tuple().exponent < -2:
            raise ValueError("Money amount has too many decimal places")
        
        return decimal_amount.quantize(Decimal('0.01'))
    except (ValueError, TypeError, decimal.InvalidOperation):
        raise ValueError("Invalid money amount")


def validate_phone_number(phone: str) -> str:
    """
    Validate phone number format.
    
    Args:
        phone: The phone number to validate.

    Returns:
        str: The validated phone number.
        
    Raises:
        ValueError: If the phone number is invalid.
    """
    return validate_phone(phone)


def validate_username(username: str) -> str:
    """
    Validate username format.
    
    Args:
        username: The username to validate.

    Returns:
        str: The validated username.
        
    Raises:
        ValueError: If the username is invalid.
    """
    if username is None:
        raise ValueError("Username cannot be None")
    if not username:
        raise ValueError("Username cannot be empty")
    if len(username) < 3:
        raise ValueError("Username must be at least 3 characters long")
    if len(username) > 50:
        raise ValueError("Username is too long")
    if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', username):
        raise ValueError("Username cannot start with a number")
    if re.search(r'[^a-zA-Z0-9_]', username):
        raise ValueError("Username contains invalid characters")
    return username


def validate_json_schema(data: dict, schema: dict) -> dict:
    """
    Validate JSON data against schema.
    
    Args:
        data: The data to validate.
        schema: The JSON schema.

    Returns:
        dict: The validated data.
        
    Raises:
        ValueError: If the data is invalid.
    """
    if data is None:
        raise ValueError("Data cannot be None")
    
    try:
        from jsonschema import validate as jsonschema_validate
        jsonschema_validate(instance=data, schema=schema)
        return data
    except ImportError:
        raise ValueError("Invalid JSON schema")
    except Exception as e:
        if "missing" in str(e).lower():
            raise ValueError("Missing required field")
        elif "additional" in str(e).lower():
            raise ValueError("Additional properties not allowed")
        else:
            raise ValueError("JSON validation failed")


# Base models with common validations
class EmailField(BaseModel):
    """
    Email field with validation.
    
    Attributes:
        email: The email to validate.
    """
    
    email: str = Field(..., description="Valid email address")
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v) -> str:
        """
        Validate email.
        
        Args:
            v: The email to validate.

        Returns:
            str: The validated email.
        """
        return validate_email(v)


class PasswordField(BaseModel):
    """
    Password field with strength validation.
    
    Attributes:
        password: The password to validate.
    """
    
    password: str = Field(..., min_length=8, description="Strong password")
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v) -> str:
        """
        Validate password.
        
        Args:
            v: The password to validate.

        Returns:
            str: The validated password.
        """
        return validate_password_strength(v)


class PhoneField(BaseModel):
    """
    Phone field with validation.
    
    Attributes:
        phone: The phone number to validate.
    """
    
    phone: str = Field(..., description="Valid phone number")
    
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v) -> str:
        """
        Validate phone number.
        
        Args:
            v: The phone number to validate.

        Returns:
            str: The validated phone number.
        """
        return validate_phone(v)


class UUIDField(BaseModel):
    """
    UUID field with validation.
    
    Attributes:
        id: The UUID to validate.
    """
    
    id: str = Field(..., description="Valid UUID")
    
    @field_validator('id')
    @classmethod
    def validate_uuid(cls, v) -> str:
        """
        Validate UUID.
        
        Args:
            v: The UUID to validate.

        Returns:
            str: The validated UUID.
        """
        return validate_uuid(v)


class PositiveDecimalField(BaseModel):
    """
    Positive decimal field with validation.
    
    Attributes:
        amount: The amount to validate.
    """
    
    amount: Decimal = Field(..., gt=0, description="Positive decimal amount")
    
    @field_validator('amount', mode='before')
    @classmethod
    def validate_positive_decimal(cls, v) -> Decimal:
        """
        Validate positive decimal.
        
        Args:
            v: The amount to validate.

        Returns:
            Decimal: The validated decimal amount.
        """
        return validate_positive_decimal(v)


class URLField(BaseModel):
    """
    URL field with validation.
    
    Attributes:
        url: The URL to validate.
    """
    
    url: str = Field(..., description="Valid URL")
    
    @field_validator('url')
    @classmethod
    def validate_url(cls, v) -> str:
        """
        Validate URL.
        
        Args:
            v: The URL to validate.

        Returns:
            str: The validated URL.
        """
        return validate_url(v)


# Pagination models
class PaginationParams(BaseModel):
    """
    Pagination parameters.
    
    Attributes:
        page: The page number.
        size: The page size.
    """
    
    page: int = Field(1, ge=1, description="Page number (1-based)")
    size: int = Field(10, ge=1, le=100, description="Page size (1-100)")
    
    @property
    def offset(self) -> int:
        """
        Calculate offset for database queries.
        
        Returns:
            int: The offset.
        """
        return (self.page - 1) * self.size


class PaginatedResponse(BaseModel):
    """
    Paginated response wrapper.
    
    Attributes:
        items: The items.
        total: The total number of items.
        page: The page number.
        size: The page size.
        pages: The total number of pages.
    """
    
    items: List[Any] = Field(..., description="List of items")
    total: int = Field(..., ge=0, description="Total number of items")
    page: int = Field(..., ge=1, description="Current page number")
    size: int = Field(..., ge=1, description="Page size")
    pages: int = Field(..., ge=0, description="Total number of pages")
    
    @field_validator('pages', mode='before')
    @classmethod
    def calculate_pages(cls, v, info) -> int:
        """
        Calculate total pages.
        
        Args:
            v: The current number of pages.
            info: The info object.

        Returns:
            int: The total number of pages.
        """
        if info.data and 'total' in info.data and 'size' in info.data:
            return (info.data['total'] + info.data['size'] - 1) // info.data['size']
        return v


# Sorting models
SortOrder = Literal["asc", "desc"]


class SortParams(BaseModel):
    """
    Sorting parameters.
    
    Attributes:
        field: The field to sort by.
        order: The sort order.
    """
    
    field: str = Field(..., description="Field to sort by")
    order: SortOrder = Field("asc", description="Sort order (asc/desc)")


# Filter models
FilterOperator = Literal["eq", "ne", "gt", "gte", "lt", "lte", "in", "nin", "like", "ilike"]


class FilterCondition(BaseModel):
    """
    Single filter condition.
    
    Attributes:
        field: The field to filter by.
        operator: The filter operator.
        value: The filter value.
    """
    
    field: str = Field(..., description="Field to filter by")
    operator: FilterOperator = Field(..., description="Filter operator")
    value: Any = Field(..., description="Filter value")


class FilterParams(BaseModel):
    """
    Filter parameters.
    
    Attributes:
        conditions: The filter conditions.
    """
    
    conditions: List[FilterCondition] = Field(default_factory=list, description="Filter conditions")
    
    def add_condition(self, field: str, operator: FilterOperator, value: Any) -> None:
        """
        Add a filter condition.
        
        Args:
            field: The field to filter by.
            operator: The filter operator.
            value: The filter value.
        """
        self.conditions.append(FilterCondition(field=field, operator=operator, value=value))


# Search models
class SearchParams(BaseModel):
    """
    Search parameters.
    
    Attributes:
        query: The search query.
        fields: The fields to search in.
        fuzzy: Whether to enable fuzzy search.
    """
    
    query: str = Field(..., min_length=1, max_length=100, description="Search query")
    fields: List[str] = Field(default_factory=list, description="Fields to search in")
    fuzzy: bool = Field(False, description="Enable fuzzy search")


# Composite query models
class QueryParams(BaseModel):
    """
    Complete query parameters with pagination, sorting, filtering, and search.
    
    Attributes:
        pagination: The pagination parameters.
        sort: The sorting parameters.
        filters: The filter parameters.
        search: The search parameters.
    """
    
    pagination: PaginationParams = Field(default_factory=PaginationParams)
    sort: Optional[SortParams] = None
    filters: FilterParams = Field(default_factory=FilterParams)
    search: Optional[SearchParams] = None


# Validation decorators
def validate_input(model_class: type[BaseModel]) -> Callable:
    """
    Decorator to validate input data.
    
    Args:
        model_class: The model class to validate.

    Returns:
        Callable: The decorator function.
    """
    
    def decorator(func):
        async def async_wrapper(*args, **kwargs) -> Any:
            """
            Async wrapper to validate input data.
            
            Args:
                args: The arguments.
                kwargs: The keyword arguments.

            Returns:
                Any: The result of the function.
            """
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
        
        def sync_wrapper(*args, **kwargs) -> Any:
            """
            Sync wrapper to validate input data.
            
            Args:
                args: The arguments.
                kwargs: The keyword arguments.

            Returns:
                Any: The result of the function.
            """
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
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


# Utility functions
def format_validation_errors(validation_error: ValidationError) -> List[Dict[str, Any]]:
    """
    Format validation errors for API response.
    
    Args:
        validation_error: The validation error.

    Returns:
        List[Dict[str, Any]]: The formatted validation errors.
    """
    formatted_errors = []
    
    for error in validation_error.errors():
        # Handle different error types
        error_type = error.get("type", "validation_error")
        if error_type == "value_error.missing":
            error_type = "missing_field"
        elif error_type == "value_error.any_str.min_length":
            error_type = "min_length"
        elif error_type == "value_error.any_str.max_length":
            error_type = "max_length"
        elif error_type == "type_error.none.not_allowed":
            error_type = "null_not_allowed"
        
        formatted_error = {
            "field": ".".join(str(loc) for loc in error.get("loc", [])),
            "message": error.get("msg", "Validation error"),
            "type": error_type,
        }
        
        # Safely add input value if it exists
        if "input" in error:
            formatted_error["value"] = error["input"]
        
        formatted_errors.append(formatted_error)
    
    return formatted_errors


def sanitize_input(text: str) -> str:
    """
    Sanitize user input to prevent injection attacks.
    
    Args:
        text: The text to sanitize.

    Returns:
        str: The sanitized text.
    """
    # Remove potentially dangerous characters
    dangerous_chars = ['<', '>', '"', "'", '&', ';', '(', ')', '{', '}']
    for char in dangerous_chars:
        text = text.replace(char, '')
    
    # Remove multiple spaces
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()


def validate_file_extension(filename: str, allowed_extensions: List[str]) -> bool:
    """
    Validate file extension.
    
    Args:
        filename: The filename to validate.
        allowed_extensions: The allowed extensions.

    Returns:
        bool: True if the file extension is valid, False otherwise.
    """
    if not filename:
        return False
    
    file_extension = filename.lower().split('.')[-1] if '.' in filename else ''
    return file_extension in [ext.lower() for ext in allowed_extensions]


def validate_file_size(file_size: int, max_size_mb: int) -> bool:
    """
    Validate file size.
    
    Args:
        file_size: The file size to validate.
        max_size_mb: The maximum size in MB.

    Returns:
        bool: True if the file size is valid, False otherwise.
    """
    max_size_bytes = max_size_mb * 1024 * 1024
    return file_size <= max_size_bytes 