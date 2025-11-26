"""Authentication Pydantic schemas"""
from pydantic import BaseModel, EmailStr, Field, field_validator
import re
from app.core.validators import (
    validate_phone_with_country_code,
    validate_email_rfc5322
)


class SendOTPRequest(BaseModel):
    """Request schema for sending OTP"""
    phone: str = Field(..., description="Phone number with country code")
    
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: str) -> str:
        """Validate phone number format with country code"""
        return validate_phone_with_country_code(v)


class SendOTPResponse(BaseModel):
    """Response schema for sending OTP"""
    success: bool
    message: str


class VerifyOTPRequest(BaseModel):
    """Request schema for verifying OTP"""
    phone: str = Field(..., description="Phone number with country code")
    otp: str = Field(..., min_length=6, max_length=6, description="6-digit OTP code")
    
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: str) -> str:
        """Validate phone number format with country code"""
        return validate_phone_with_country_code(v)
    
    @field_validator('otp')
    @classmethod
    def validate_otp(cls, v: str) -> str:
        """Validate OTP is numeric"""
        if not v.isdigit():
            raise ValueError('OTP must be numeric')
        return v


class TokenResponse(BaseModel):
    """Response schema for authentication with tokens"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: 'UserResponse'


class GoogleAuthRequest(BaseModel):
    """Request schema for Google OAuth"""
    token: str = Field(..., description="Google OAuth ID token")


class RefreshTokenRequest(BaseModel):
    """Request schema for refreshing access token"""
    refresh_token: str = Field(..., description="Refresh token")


class RefreshTokenResponse(BaseModel):
    """Response schema for refresh token"""
    access_token: str
    token_type: str = "bearer"


class RequestPasswordResetRequest(BaseModel):
    """Request schema for requesting password reset"""
    email: EmailStr = Field(..., description="Email address")
    
    @field_validator('email')
    @classmethod
    def validate_email_format(cls, v: str) -> str:
        """Validate email format according to RFC 5322"""
        return validate_email_rfc5322(v)


class RequestPasswordResetResponse(BaseModel):
    """Response schema for password reset request"""
    success: bool
    message: str


class CompletePasswordResetRequest(BaseModel):
    """Request schema for completing password reset"""
    token: str = Field(..., description="Password reset token")
    new_password: str = Field(..., min_length=8, description="New password")
    
    @field_validator('new_password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        
        # Check for at least one uppercase, one lowercase, and one digit
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        
        return v


class CompletePasswordResetResponse(BaseModel):
    """Response schema for password reset completion"""
    success: bool
    message: str


class UserResponse(BaseModel):
    """Response schema for user information"""
    id: int
    email: str | None
    phone: str
    name: str
    role: str
    is_email_verified: bool
    is_phone_verified: bool
    is_active: bool
    distributor_status: str | None = None
    
    class Config:
        from_attributes = True


# Rebuild TokenResponse model to resolve forward reference
TokenResponse.model_rebuild()
