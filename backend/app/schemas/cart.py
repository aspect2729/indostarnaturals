"""Cart schemas for request/response validation"""
from typing import List, Optional
from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel, Field, field_validator
from app.core.validators import (
    validate_quantity,
    sanitize_string_input,
    validate_safe_input
)


class CartItemBase(BaseModel):
    """Base cart item schema"""
    product_id: int = Field(..., gt=0, description="Product ID must be positive")
    quantity: int = Field(..., gt=0, description="Quantity must be positive")
    
    @field_validator('quantity')
    @classmethod
    def validate_quantity_field(cls, v):
        """Validate quantity is within acceptable range"""
        return validate_quantity(v, min_value=1, max_value=1000)


class CartItemCreate(CartItemBase):
    """Schema for adding item to cart"""
    pass


class CartItemUpdate(BaseModel):
    """Schema for updating cart item"""
    quantity: int = Field(..., gt=0, description="Quantity must be positive")
    
    @field_validator('quantity')
    @classmethod
    def validate_quantity_field(cls, v):
        """Validate quantity is within acceptable range"""
        return validate_quantity(v, min_value=1, max_value=1000)


class CartItemResponse(BaseModel):
    """Cart item response schema"""
    id: int
    cart_id: int
    product_id: int
    quantity: int
    unit_price: Decimal
    product_title: str
    product_sku: str
    product_image_url: Optional[str] = None
    subtotal: Decimal
    
    class Config:
        from_attributes = True


class CouponApply(BaseModel):
    """Schema for applying coupon"""
    coupon_code: str = Field(..., min_length=1, max_length=100)
    
    @field_validator('coupon_code')
    @classmethod
    def validate_coupon(cls, v):
        """Validate and sanitize coupon code"""
        sanitized = sanitize_string_input(v, max_length=100)
        validate_safe_input(sanitized)
        return sanitized.upper()  # Normalize to uppercase


class CartResponse(BaseModel):
    """Cart response schema"""
    id: int
    user_id: int
    items: List[CartItemResponse]
    coupon_code: Optional[str] = None
    discount_amount: Decimal
    subtotal: Decimal
    total: Decimal
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class CartValidation(BaseModel):
    """Cart validation result"""
    is_valid: bool
    errors: List[str] = []
    warnings: List[str] = []

