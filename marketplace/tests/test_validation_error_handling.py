"""Tests for error handling in validation module."""

import pytest
from datetime import datetime, date
from decimal import Decimal
import uuid

from src.shared.infrastructure.validation import (
    validate_email,
    validate_password,
    validate_uuid,
    validate_date,
    validate_money_amount,
    validate_phone_number,
    validate_username,
    validate_url,
    validate_json_schema,
)


class TestValidationErrorHandling:
    """Test error handling scenarios in validation functions."""

    def test_validate_email_empty_string(self):
        """Test email validation with empty string."""
        # Act & Assert
        with pytest.raises(ValueError, match="Email cannot be empty"):
            validate_email("")

    def test_validate_email_none_value(self):
        """Test email validation with None value."""
        # Act & Assert
        with pytest.raises(ValueError, match="Email cannot be None"):
            validate_email(None)

    def test_validate_email_invalid_format(self):
        """Test email validation with invalid format."""
        invalid_emails = [
            "invalid_email",
            "@example.com",
            "test@",
            "test@.com",
            "test..test@example.com",
            "test@example..com",
            "test@example.com.",
            ".test@example.com",
        ]
        
        for email in invalid_emails:
            with pytest.raises(ValueError, match="Invalid email format"):
                validate_email(email)

    def test_validate_email_too_long(self):
        """Test email validation with email longer than maximum length."""
        # Arrange
        long_email = "a" * 300 + "@example.com"
        
        # Act & Assert
        with pytest.raises(ValueError, match="Email is too long"):
            validate_email(long_email)

    def test_validate_email_whitespace(self):
        """Test email validation with whitespace."""
        # Act & Assert
        with pytest.raises(ValueError, match="Email cannot contain whitespace"):
            validate_email("test @example.com")

    def test_validate_password_empty_string(self):
        """Test password validation with empty string."""
        # Act & Assert
        with pytest.raises(ValueError, match="Password cannot be empty"):
            validate_password("")

    def test_validate_password_none_value(self):
        """Test password validation with None value."""
        # Act & Assert
        with pytest.raises(ValueError, match="Password cannot be None"):
            validate_password(None)

    def test_validate_password_too_short(self):
        """Test password validation with password shorter than minimum length."""
        # Act & Assert
        with pytest.raises(ValueError, match="Password must be at least 8 characters long"):
            validate_password("short")

    def test_validate_password_no_digits(self):
        """Test password validation with password without digits."""
        # Act & Assert
        with pytest.raises(ValueError, match="Password must contain at least one digit"):
            validate_password("NoDigits!")

    def test_validate_password_no_uppercase(self):
        """Test password validation with password without uppercase letters."""
        # Act & Assert
        with pytest.raises(ValueError, match="Password must contain at least one uppercase letter"):
            validate_password("nouppercase123!")

    def test_validate_password_no_lowercase(self):
        """Test password validation with password without lowercase letters."""
        # Act & Assert
        with pytest.raises(ValueError, match="Password must contain at least one lowercase letter"):
            validate_password("NOLOWERCASE123!")

    def test_validate_password_no_special_characters(self):
        """Test password validation with password without special characters."""
        # Act & Assert
        with pytest.raises(ValueError, match="Password must contain at least one special character"):
            validate_password("NoSpecialChars123")

    def test_validate_password_too_long(self):
        """Test password validation with password longer than maximum length."""
        # Arrange
        long_password = "A" * 129 + "1!"
        
        # Act & Assert
        with pytest.raises(ValueError, match="Password is too long"):
            validate_password(long_password)

    def test_validate_uuid_empty_string(self):
        """Test UUID validation with empty string."""
        # Act & Assert
        with pytest.raises(ValueError, match="UUID cannot be empty"):
            validate_uuid("")

    def test_validate_uuid_none_value(self):
        """Test UUID validation with None value."""
        # Act & Assert
        with pytest.raises(ValueError, match="UUID cannot be None"):
            validate_uuid(None)

    def test_validate_uuid_invalid_format(self):
        """Test UUID validation with invalid format."""
        invalid_uuids = [
            "invalid-uuid",
            "12345678-1234-1234-1234-123456789012",
            "12345678-1234-1234-1234-12345678901",
            "12345678-1234-1234-1234-1234567890123",
            "12345678-1234-1234-1234-12345678901g",
        ]
        
        for uuid_str in invalid_uuids:
            with pytest.raises(ValueError, match="Invalid UUID format"):
                validate_uuid(uuid_str)

    def test_validate_uuid_wrong_version(self):
        """Test UUID validation with wrong version."""
        # Arrange
        wrong_version_uuid = "12345678-1234-1234-1234-123456789012"
        
        # Act & Assert
        with pytest.raises(ValueError, match="Invalid UUID version"):
            validate_uuid(wrong_version_uuid, version=4)

    def test_validate_date_none_value(self):
        """Test date validation with None value."""
        # Act & Assert
        with pytest.raises(ValueError, match="Date cannot be None"):
            validate_date(None)

    def test_validate_date_invalid_format(self):
        """Test date validation with invalid format."""
        invalid_dates = [
            "invalid-date",
            "2023-13-01",  # Invalid month
            "2023-12-32",  # Invalid day
            "2023-02-30",  # Invalid day for February
            "2023-04-31",  # Invalid day for April
        ]
        
        for date_str in invalid_dates:
            with pytest.raises(ValueError, match="Invalid date format"):
                validate_date(date_str)

    def test_validate_date_future_date(self):
        """Test date validation with future date."""
        # Arrange
        future_date = "2025-12-31"
        
        # Act & Assert
        with pytest.raises(ValueError, match="Date cannot be in the future"):
            validate_date(future_date, allow_future=False)

    def test_validate_date_too_old(self):
        """Test date validation with date too old."""
        # Arrange
        old_date = "1900-01-01"
        
        # Act & Assert
        with pytest.raises(ValueError, match="Date is too old"):
            validate_date(old_date, min_date=date(1950, 1, 1))

    def test_validate_money_amount_none_value(self):
        """Test money amount validation with None value."""
        # Act & Assert
        with pytest.raises(ValueError, match="Amount cannot be None"):
            validate_money_amount(None)

    def test_validate_money_amount_negative(self):
        """Test money amount validation with negative amount."""
        # Act & Assert
        with pytest.raises(ValueError, match="Amount cannot be negative"):
            validate_money_amount(Decimal("-10.50"))

    def test_validate_money_amount_zero(self):
        """Test money amount validation with zero amount."""
        # Act & Assert
        with pytest.raises(ValueError, match="Amount cannot be zero"):
            validate_money_amount(Decimal("0"))

    def test_validate_money_amount_too_large(self):
        """Test money amount validation with amount too large."""
        # Arrange
        large_amount = Decimal("999999999.99")
        
        # Act & Assert
        with pytest.raises(ValueError, match="Amount is too large"):
            validate_money_amount(large_amount, max_amount=Decimal("1000000.00"))

    def test_validate_money_amount_invalid_precision(self):
        """Test money amount validation with invalid precision."""
        # Arrange
        invalid_amount = Decimal("10.123")  # More than 2 decimal places
        
        # Act & Assert
        with pytest.raises(ValueError, match="Amount has too many decimal places"):
            validate_money_amount(invalid_amount)

    def test_validate_phone_number_empty_string(self):
        """Test phone number validation with empty string."""
        # Act & Assert
        with pytest.raises(ValueError, match="Phone number cannot be empty"):
            validate_phone_number("")

    def test_validate_phone_number_none_value(self):
        """Test phone number validation with None value."""
        # Act & Assert
        with pytest.raises(ValueError, match="Phone number cannot be None"):
            validate_phone_number(None)

    def test_validate_phone_number_invalid_format(self):
        """Test phone number validation with invalid format."""
        invalid_phones = [
            "invalid-phone",
            "123",
            "12345678901234567890",  # Too long
            "+1-234-567-8900-123",   # Too many parts
            "abc-def-ghij",          # Contains letters
        ]
        
        for phone in invalid_phones:
            with pytest.raises(ValueError, match="Invalid phone number format"):
                validate_phone_number(phone)

    def test_validate_phone_number_invalid_country_code(self):
        """Test phone number validation with invalid country code."""
        # Act & Assert
        with pytest.raises(ValueError, match="Invalid country code"):
            validate_phone_number("+999-123-456-7890")

    def test_validate_username_empty_string(self):
        """Test username validation with empty string."""
        # Act & Assert
        with pytest.raises(ValueError, match="Username cannot be empty"):
            validate_username("")

    def test_validate_username_none_value(self):
        """Test username validation with None value."""
        # Act & Assert
        with pytest.raises(ValueError, match="Username cannot be None"):
            validate_username(None)

    def test_validate_username_too_short(self):
        """Test username validation with username shorter than minimum length."""
        # Act & Assert
        with pytest.raises(ValueError, match="Username must be at least 3 characters long"):
            validate_username("ab")

    def test_validate_username_too_long(self):
        """Test username validation with username longer than maximum length."""
        # Arrange
        long_username = "a" * 51
        
        # Act & Assert
        with pytest.raises(ValueError, match="Username is too long"):
            validate_username(long_username)

    def test_validate_username_invalid_characters(self):
        """Test username validation with invalid characters."""
        invalid_usernames = [
            "user@name",
            "user name",
            "user.name",
            "user/name",
            "user\\name",
            "user<name",
            "user>name",
        ]
        
        for username in invalid_usernames:
            with pytest.raises(ValueError, match="Username contains invalid characters"):
                validate_username(username)

    def test_validate_username_starts_with_number(self):
        """Test username validation with username starting with number."""
        # Act & Assert
        with pytest.raises(ValueError, match="Username cannot start with a number"):
            validate_username("1username")

    def test_validate_url_empty_string(self):
        """Test URL validation with empty string."""
        # Act & Assert
        with pytest.raises(ValueError, match="URL cannot be empty"):
            validate_url("")

    def test_validate_url_none_value(self):
        """Test URL validation with None value."""
        # Act & Assert
        with pytest.raises(ValueError, match="URL cannot be None"):
            validate_url(None)

    def test_validate_url_invalid_format(self):
        """Test URL validation with invalid format."""
        invalid_urls = [
            "invalid-url",
            "http://",
            "https://",
            "ftp://example.com",
            "http://example",
            "http://.com",
            "http://example..com",
        ]
        
        for url in invalid_urls:
            with pytest.raises(ValueError, match="Invalid URL format"):
                validate_url(url)

    def test_validate_url_invalid_scheme(self):
        """Test URL validation with invalid scheme."""
        # Act & Assert
        with pytest.raises(ValueError, match="Invalid URL scheme"):
            validate_url("ftp://example.com", allowed_schemes=["http", "https"])

    def test_validate_url_too_long(self):
        """Test URL validation with URL longer than maximum length."""
        # Arrange
        long_url = "http://example.com/" + "a" * 2000
        
        # Act & Assert
        with pytest.raises(ValueError, match="URL is too long"):
            validate_url(long_url)

    def test_validate_json_schema_none_value(self):
        """Test JSON schema validation with None value."""
        # Act & Assert
        with pytest.raises(ValueError, match="Data cannot be None"):
            validate_json_schema(None, {})

    def test_validate_json_schema_invalid_schema(self):
        """Test JSON schema validation with invalid schema."""
        # Arrange
        invalid_schema = {"type": "invalid_type"}
        
        # Act & Assert
        with pytest.raises(ValueError, match="Invalid JSON schema"):
            validate_json_schema({"test": "data"}, invalid_schema)

    def test_validate_json_schema_validation_error(self):
        """Test JSON schema validation with validation error."""
        # Arrange
        schema = {"type": "object", "properties": {"name": {"type": "string"}}}
        invalid_data = {"name": 123}
        
        # Act & Assert
        with pytest.raises(ValueError, match="Data validation failed"):
            validate_json_schema(invalid_data, schema)

    def test_validate_json_schema_missing_required_field(self):
        """Test JSON schema validation with missing required field."""
        # Arrange
        schema = {
            "type": "object",
            "properties": {"name": {"type": "string"}},
            "required": ["name"]
        }
        invalid_data = {}
        
        # Act & Assert
        with pytest.raises(ValueError, match="Data validation failed"):
            validate_json_schema(invalid_data, schema)

    def test_validate_json_schema_additional_properties(self):
        """Test JSON schema validation with additional properties."""
        # Arrange
        schema = {
            "type": "object",
            "properties": {"name": {"type": "string"}},
            "additionalProperties": False
        }
        invalid_data = {"name": "test", "extra": "field"}
        
        # Act & Assert
        with pytest.raises(ValueError, match="Data validation failed"):
            validate_json_schema(invalid_data, schema) 