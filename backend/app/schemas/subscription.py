"""Subscription schemas for request/response validation"""
from typing import List, Optional
from decimal import Decimal
from datetime import date, datetime
from pydantic import BaseModel, Field, field_validator
from app.models.enums import SubscriptionFrequency, SubscriptionStatus


class SubscriptionCreate(BaseModel):
    """Schema for creating a subscription"""
    product_id: int = Field(..., gt=0, description="Product ID for subscription")
    plan_frequency: SubscriptionFrequency = Field(..., description="Subscription frequency")
    start_date: date = Field(..., description="Subscription start date")
    delivery_address_id: int = Field(..., gt=0, description="Delivery address ID")
    
    @field_validator('start_date')
    @classmethod
    def validate_start_date(cls, v):
        """Validate start date is not in the past"""
        from datetime import date as date_type
        today = date_type.today()
        if v < today:
            raise ValueError('Start date cannot be in the past')
        return v


class ProductResponse(BaseModel):
    """Product response schema for subscription"""
    id: int
    title: str
    sku: str
    unit_size: str
    consumer_price: Decimal
    distributor_price: Decimal
    is_subscription_available: bool
    
    class Config:
        from_attributes = True


class AddressResponse(BaseModel):
    """Address response schema for subscription"""
    id: int
    name: str
    phone: str
    address_line1: str
    address_line2: Optional[str] = None
    city: str
    state: str
    postal_code: str
    country: str
    
    class Config:
        from_attributes = True


class SubscriptionResponse(BaseModel):
    """Subscription response schema"""
    id: int
    user_id: int
    product_id: int
    razorpay_subscription_id: str
    plan_frequency: SubscriptionFrequency
    start_date: date
    next_delivery_date: date
    delivery_address_id: int
    status: SubscriptionStatus
    product: ProductResponse
    delivery_address: AddressResponse
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class SubscriptionListResponse(BaseModel):
    """Subscription list response"""
    subscriptions: List[SubscriptionResponse]
    total: int


class RazorpaySubscriptionResponse(BaseModel):
    """Razorpay subscription creation response"""
    razorpay_subscription_id: str
    status: str
    subscription_id: int
    key_id: str


class SubscriptionPaymentVerification(BaseModel):
    """Schema for verifying subscription payment"""
    razorpay_payment_id: str
    razorpay_subscription_id: str
    razorpay_signature: str
