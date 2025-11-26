"""Comprehensive validation utilities for input validation"""
import re
from decimal import Decimal
from typing import Any
from pydantic import field_validator


def validate_email_rfc5322(email: str) -> str:
    """
    Validate email format according to RFC 5322 standards.
    
    Args:
        email: Email address to validate
        
    Returns:
        Validated email address
        
    Raises:
        ValueError: If email format is invalid
    """
    # RFC 5322 compliant email regex (simplified but comprehensive)
    # This pattern covers most valid email formats
    pattern = r'^[a-zA-Z0-9.!#$%&\'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$'
    
    if not re.match(pattern, email):
        raise ValueError('Invalid email format according to RFC 5322 standards')
    
    # Additional checks
    if len(email) > 254:  # RFC 5321
        raise ValueError('Email address too long (max 254 characters)')
    
    if '@' not in email:
        raise ValueError('Email must contain @ symbol')
    
    local_part, domain = email.rsplit('@', 1)
    if len(local_part) > 64:  # RFC 5321
        raise ValueError('Email local part too long (max 64 characters)')
    
    # Ensure domain has at least one dot (TLD required)
    if '.' not in domain:
        raise ValueError('Email domain must contain a TLD (e.g., .com, .org)')
    
    return email


def validate_phone_with_country_code(phone: str) -> str:
    """
    Validate phone number format with country code.
    Currently supports Indian phone numbers (+91).
    
    Args:
        phone: Phone number to validate
        
    Returns:
        Validated phone number
        
    Raises:
        ValueError: If phone format is invalid
    """
    # Remove spaces and dashes
    phone_cleaned = phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
    
    # Check if it matches Indian phone number format: +91XXXXXXXXXX
    # Indian mobile numbers start with 6, 7, 8, or 9
    if not re.match(r'^\+91[6-9]\d{9}$', phone_cleaned):
        raise ValueError('Phone number must be in format +91XXXXXXXXXX (Indian mobile number)')
    
    return phone_cleaned


def validate_price(price: Decimal) -> Decimal:
    """
    Validate price value.
    
    Args:
        price: Price to validate
        
    Returns:
        Validated price
        
    Raises:
        ValueError: If price is invalid
    """
    if price <= 0:
        raise ValueError('Price must be positive')
    
    # Check decimal places (max 2)
    if price.as_tuple().exponent < -2:
        raise ValueError('Price must have maximum 2 decimal places')
    
    # Check reasonable upper limit (prevent overflow)
    if price > Decimal('999999.99'):
        raise ValueError('Price exceeds maximum allowed value (999999.99)')
    
    return price


def validate_stock_quantity(quantity: int) -> int:
    """
    Validate stock quantity.
    
    Args:
        quantity: Stock quantity to validate
        
    Returns:
        Validated quantity
        
    Raises:
        ValueError: If quantity is invalid
    """
    if quantity < 0:
        raise ValueError('Stock quantity cannot be negative')
    
    if quantity > 1000000:
        raise ValueError('Stock quantity exceeds maximum allowed value (1000000)')
    
    return quantity


def validate_required_fields(data: dict, required_fields: list[str]) -> None:
    """
    Validate that all required fields are present and not empty.
    
    Args:
        data: Dictionary of data to validate
        required_fields: List of required field names
        
    Raises:
        ValueError: If any required field is missing or empty
    """
    missing_fields = []
    empty_fields = []
    
    for field in required_fields:
        if field not in data:
            missing_fields.append(field)
        elif data[field] is None or (isinstance(data[field], str) and not data[field].strip()):
            empty_fields.append(field)
    
    if missing_fields:
        raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")
    
    if empty_fields:
        raise ValueError(f"Required fields cannot be empty: {', '.join(empty_fields)}")


def sanitize_string_input(value: str, max_length: int = None) -> str:
    """
    Sanitize string input to prevent XSS and other injection attacks.
    
    Args:
        value: String to sanitize
        max_length: Maximum allowed length
        
    Returns:
        Sanitized string
        
    Raises:
        ValueError: If string exceeds max length
    """
    if not isinstance(value, str):
        raise ValueError('Value must be a string')
    
    # Strip leading/trailing whitespace
    sanitized = value.strip()
    
    # Check length
    if max_length and len(sanitized) > max_length:
        raise ValueError(f'String exceeds maximum length of {max_length} characters')
    
    # Check for null bytes
    if '\x00' in sanitized:
        raise ValueError('String contains invalid null bytes')
    
    return sanitized


def validate_postal_code_india(postal_code: str) -> str:
    """
    Validate Indian postal code (PIN code).
    
    Args:
        postal_code: Postal code to validate
        
    Returns:
        Validated postal code
        
    Raises:
        ValueError: If postal code is invalid
    """
    # Remove spaces
    postal_code_cleaned = postal_code.replace(' ', '')
    
    # Check if it's a valid Indian PIN code (6 digits)
    if not re.match(r'^\d{6}$', postal_code_cleaned):
        raise ValueError('Postal code must be 6 digits')
    
    return postal_code_cleaned


def validate_sku(sku: str) -> str:
    """
    Validate SKU format.
    
    Args:
        sku: SKU to validate
        
    Returns:
        Validated SKU
        
    Raises:
        ValueError: If SKU is invalid
    """
    # SKU should be alphanumeric with optional hyphens and underscores
    if not re.match(r'^[A-Za-z0-9_-]+$', sku):
        raise ValueError('SKU must contain only alphanumeric characters, hyphens, and underscores')
    
    if len(sku) < 1 or len(sku) > 100:
        raise ValueError('SKU must be between 1 and 100 characters')
    
    return sku.upper()  # Normalize to uppercase


def validate_quantity(quantity: int, min_value: int = 1, max_value: int = 1000) -> int:
    """
    Validate quantity value.
    
    Args:
        quantity: Quantity to validate
        min_value: Minimum allowed value
        max_value: Maximum allowed value
        
    Returns:
        Validated quantity
        
    Raises:
        ValueError: If quantity is invalid
    """
    if quantity < min_value:
        raise ValueError(f'Quantity must be at least {min_value}')
    
    if quantity > max_value:
        raise ValueError(f'Quantity cannot exceed {max_value}')
    
    return quantity


def validate_discount_percentage(percentage: Decimal) -> Decimal:
    """
    Validate discount percentage.
    
    Args:
        percentage: Discount percentage to validate
        
    Returns:
        Validated percentage
        
    Raises:
        ValueError: If percentage is invalid
    """
    if percentage < 0:
        raise ValueError('Discount percentage cannot be negative')
    
    if percentage > 100:
        raise ValueError('Discount percentage cannot exceed 100')
    
    # Check decimal places (max 2)
    if percentage.as_tuple().exponent < -2:
        raise ValueError('Discount percentage must have maximum 2 decimal places')
    
    return percentage


def detect_sql_injection(value: str) -> bool:
    """
    Detect potential SQL injection patterns.
    
    Args:
        value: String to check
        
    Returns:
        True if potential SQL injection detected, False otherwise
    """
    # Common SQL injection patterns
    sql_patterns = [
        r"(\bUNION\b.*\bSELECT\b)",
        r"(\bSELECT\b.*\bFROM\b)",
        r"(\bINSERT\b.*\bINTO\b)",
        r"(\bUPDATE\b.*\bSET\b)",
        r"(\bDELETE\b.*\bFROM\b)",
        r"(\bDROP\b.*\bTABLE\b)",
        r"(--|\#|\/\*|\*\/)",  # SQL comments
        r"(\bOR\b.*=.*)",
        r"(\bAND\b.*=.*)",
        r"(';|\";\s*--)",
    ]
    
    value_upper = value.upper()
    for pattern in sql_patterns:
        if re.search(pattern, value_upper, re.IGNORECASE):
            return True
    
    return False


def detect_xss(value: str) -> bool:
    """
    Detect potential XSS patterns.
    
    Args:
        value: String to check
        
    Returns:
        True if potential XSS detected, False otherwise
    """
    # Common XSS patterns
    xss_patterns = [
        r"<script[^>]*>.*?</script>",
        r"javascript:",
        r"on\w+\s*=",  # Event handlers like onclick, onload, etc.
        r"<iframe",
        r"<object",
        r"<embed",
        r"<img[^>]+src",
    ]
    
    value_lower = value.lower()
    for pattern in xss_patterns:
        if re.search(pattern, value_lower, re.IGNORECASE):
            return True
    
    return False


def validate_safe_input(value: str) -> str:
    """
    Validate that input doesn't contain malicious patterns.
    
    Args:
        value: String to validate
        
    Returns:
        Validated string
        
    Raises:
        ValueError: If malicious patterns detected
    """
    if detect_sql_injection(value):
        raise ValueError('Input contains potential SQL injection patterns')
    
    if detect_xss(value):
        raise ValueError('Input contains potential XSS patterns')
    
    return value
