"""Order schemas for request/response validation"""
from typing import List, Optional
from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel, Field, field_validator
from app.models.enums import OrderStatus, PaymentStatus
from app.core.validators import sanitize_string_input, validate_safe_input


class OrderItemResponse(BaseModel):
    """Order item response schema"""
    id: int
    order_id: int
    product_id: int
    quantity: int
    unit_price: Decimal
    total_price: Decimal
    product_title: str
    product_sku: str
    
    class Config:
        from_attributes = True


class AddressResponse(BaseModel):
    """Address response schema for order"""
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


class OrderCreate(BaseModel):
    """Schema for creating an order"""
    address_id: int = Field(..., gt=0, description="Delivery address ID")
    notes: Optional[str] = Field(None, max_length=1000, description="Optional order notes")
    
    @field_validator('notes')
    @classmethod
    def validate_notes(cls, v):
        """Validate and sanitize notes"""
        if v is not None:
            sanitized = sanitize_string_input(v, max_length=1000)
            validate_safe_input(sanitized)
            return sanitized
        return v


class OrderResponse(BaseModel):
    """Order response schema"""
    id: int
    user_id: int
    order_number: str
    total_amount: Decimal
    discount_amount: Decimal
    final_amount: Decimal
    payment_status: PaymentStatus
    order_status: OrderStatus
    delivery_address: AddressResponse
    items: List[OrderItemResponse]
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class OrderListResponse(BaseModel):
    """Order list response with pagination"""
    orders: List[OrderResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class RazorpayOrderResponse(BaseModel):
    """Razorpay order creation response"""
    razorpay_order_id: str
    amount: int
    currency: str
    key_id: str
    order_id: int
    order_number: str


class OrderStatusUpdate(BaseModel):
    """Schema for updating order status"""
    status: OrderStatus = Field(description="New order status")


class OrderResponseWithUser(BaseModel):
    """Order response schema with user information (for owner)"""
    id: int
    user_id: int
    user_name: str
    user_email: Optional[str] = None
    user_phone: str
    user_role: str
    order_number: str
    total_amount: Decimal
    discount_amount: Decimal
    final_amount: Decimal
    payment_status: PaymentStatus
    order_status: OrderStatus
    delivery_address: AddressResponse
    items: List[OrderItemResponse]
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class OwnerOrderListResponse(BaseModel):
    """Order list response for owner with pagination"""
    orders: List[OrderResponseWithUser]
    total: int
    page: int
    page_size: int
    total_pages: int

