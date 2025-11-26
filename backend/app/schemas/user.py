"""User and Address Pydantic schemas"""
from pydantic import BaseModel, EmailStr, Field, field_validator
import re
from app.core.validators import (
    validate_phone_with_country_code,
    validate_postal_code_india,
    sanitize_string_input,
    validate_safe_input
)


class UserUpdateRequest(BaseModel):
    """Request schema for updating user profile"""
    name: str | None = Field(None, min_length=1, max_length=255)
    email: EmailStr | None = None
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str | None) -> str | None:
        """Validate and sanitize name"""
        if v is None:
            return v
        sanitized = sanitize_string_input(v, max_length=255)
        validate_safe_input(sanitized)
        return sanitized


class AddressBase(BaseModel):
    """Base schema for address"""
    name: str = Field(..., min_length=1, max_length=255, description="Recipient name")
    phone: str = Field(..., description="Phone number with country code")
    address_line1: str = Field(..., min_length=1, max_length=500, description="Address line 1")
    address_line2: str | None = Field(None, max_length=500, description="Address line 2 (optional)")
    city: str = Field(..., min_length=1, max_length=100, description="City")
    state: str = Field(..., min_length=1, max_length=100, description="State")
    postal_code: str = Field(..., min_length=1, max_length=20, description="Postal code")
    country: str = Field(default="India", max_length=100, description="Country")
    is_default: bool = Field(default=False, description="Set as default address")
    
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: str) -> str:
        """Validate phone number format with country code"""
        return validate_phone_with_country_code(v)
    
    @field_validator('postal_code')
    @classmethod
    def validate_postal_code(cls, v: str) -> str:
        """Validate postal code format"""
        return validate_postal_code_india(v)
    
    @field_validator('name', 'address_line1', 'address_line2', 'city', 'state')
    @classmethod
    def validate_text_fields(cls, v: str | None) -> str | None:
        """Validate and sanitize text fields"""
        if v is None:
            return v
        sanitized = sanitize_string_input(v)
        validate_safe_input(sanitized)
        return sanitized


class AddressCreateRequest(AddressBase):
    """Request schema for creating address"""
    pass


class AddressUpdateRequest(BaseModel):
    """Request schema for updating address"""
    name: str | None = Field(None, min_length=1, max_length=255)
    phone: str | None = None
    address_line1: str | None = Field(None, min_length=1, max_length=500)
    address_line2: str | None = Field(None, max_length=500)
    city: str | None = Field(None, min_length=1, max_length=100)
    state: str | None = Field(None, min_length=1, max_length=100)
    postal_code: str | None = Field(None, min_length=1, max_length=20)
    country: str | None = Field(None, max_length=100)
    is_default: bool | None = None
    
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: str | None) -> str | None:
        """Validate phone number format with country code"""
        if v is None:
            return v
        return validate_phone_with_country_code(v)
    
    @field_validator('postal_code')
    @classmethod
    def validate_postal_code(cls, v: str | None) -> str | None:
        """Validate postal code format"""
        if v is None:
            return v
        return validate_postal_code_india(v)
    
    @field_validator('name', 'address_line1', 'address_line2', 'city', 'state')
    @classmethod
    def validate_text_fields(cls, v: str | None) -> str | None:
        """Validate and sanitize text fields"""
        if v is None:
            return v
        sanitized = sanitize_string_input(v)
        validate_safe_input(sanitized)
        return sanitized


class AddressResponse(BaseModel):
    """Response schema for address"""
    id: int
    user_id: int
    name: str
    phone: str
    address_line1: str
    address_line2: str | None
    city: str
    state: str
    postal_code: str
    country: str
    is_default: bool
    
    class Config:
        from_attributes = True


class UserProfileResponse(BaseModel):
    """Response schema for user profile"""
    id: int
    email: str | None
    phone: str
    name: str
    role: str
    is_email_verified: bool
    is_phone_verified: bool
    is_active: bool
    
    class Config:
        from_attributes = True
