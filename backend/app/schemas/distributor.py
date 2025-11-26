"""Distributor Pydantic schemas"""
from pydantic import BaseModel, EmailStr, Field, field_validator
import re


class DistributorRegistrationRequest(BaseModel):
    """Request schema for distributor registration"""
    phone: str = Field(..., description="Phone number with country code")
    email: EmailStr = Field(..., description="Email address")
    name: str = Field(..., min_length=2, max_length=255, description="Full name")
    business_name: str = Field(..., min_length=2, max_length=255, description="Business name")
    
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: str) -> str:
        """Validate phone number format"""
        phone = v.replace(' ', '').replace('-', '')
        if not re.match(r'^\+91[6-9]\d{9}$', phone):
            raise ValueError('Phone number must be in format +91XXXXXXXXXX')
        return phone


class DistributorRegistrationResponse(BaseModel):
    """Response schema for distributor registration"""
    success: bool
    message: str
    user_id: int


class ApproveDistributorRequest(BaseModel):
    """Request schema for approving distributor"""
    user_id: int = Field(..., description="User ID to approve as distributor")
    approved: bool = Field(..., description="True to approve, False to reject")


class ApproveDistributorResponse(BaseModel):
    """Response schema for distributor approval"""
    success: bool
    message: str
    user_id: int
    status: str
