"""Product schemas for request/response validation"""
from typing import Optional, List
from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel, Field, field_validator
from app.core.validators import (
    validate_price,
    validate_stock_quantity,
    validate_sku,
    sanitize_string_input,
    validate_safe_input
)


class ProductImageSchema(BaseModel):
    """Schema for product image"""
    id: int
    product_id: int
    url: str
    alt_text: Optional[str] = None
    display_order: int
    created_at: datetime

    class Config:
        from_attributes = True


class CategorySchema(BaseModel):
    """Schema for category"""
    id: int
    name: str
    slug: str
    parent_id: Optional[int] = None
    display_order: int

    class Config:
        from_attributes = True


class ProductBase(BaseModel):
    """Base product schema"""
    title: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1)
    category_id: int = Field(..., gt=0)
    sku: str = Field(..., min_length=1, max_length=100)
    unit_size: str = Field(..., min_length=1, max_length=100)
    consumer_price: Decimal = Field(..., gt=0)
    distributor_price: Decimal = Field(..., gt=0)
    stock_quantity: int = Field(..., ge=0)
    is_subscription_available: bool = False

    @field_validator('consumer_price', 'distributor_price')
    @classmethod
    def validate_price_field(cls, v):
        """Validate price has max 2 decimal places and is positive"""
        return validate_price(v)
    
    @field_validator('stock_quantity')
    @classmethod
    def validate_stock(cls, v):
        """Validate stock quantity is non-negative"""
        return validate_stock_quantity(v)
    
    @field_validator('sku')
    @classmethod
    def validate_sku_field(cls, v):
        """Validate SKU format"""
        return validate_sku(v)
    
    @field_validator('title', 'description', 'unit_size')
    @classmethod
    def validate_text_fields(cls, v):
        """Validate and sanitize text fields"""
        sanitized = sanitize_string_input(v)
        validate_safe_input(sanitized)
        return sanitized


class ProductCreate(ProductBase):
    """Schema for creating a product"""
    pass


class ProductUpdate(BaseModel):
    """Schema for updating a product"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, min_length=1)
    category_id: Optional[int] = Field(None, gt=0)
    sku: Optional[str] = Field(None, min_length=1, max_length=100)
    unit_size: Optional[str] = Field(None, min_length=1, max_length=100)
    consumer_price: Optional[Decimal] = Field(None, gt=0)
    distributor_price: Optional[Decimal] = Field(None, gt=0)
    stock_quantity: Optional[int] = Field(None, ge=0)
    is_subscription_available: Optional[bool] = None
    is_active: Optional[bool] = None

    @field_validator('consumer_price', 'distributor_price')
    @classmethod
    def validate_price_field(cls, v):
        """Validate price has max 2 decimal places and is positive"""
        if v is not None:
            return validate_price(v)
        return v
    
    @field_validator('stock_quantity')
    @classmethod
    def validate_stock(cls, v):
        """Validate stock quantity is non-negative"""
        if v is not None:
            return validate_stock_quantity(v)
        return v
    
    @field_validator('sku')
    @classmethod
    def validate_sku_field(cls, v):
        """Validate SKU format"""
        if v is not None:
            return validate_sku(v)
        return v
    
    @field_validator('title', 'description', 'unit_size')
    @classmethod
    def validate_text_fields(cls, v):
        """Validate and sanitize text fields"""
        if v is not None:
            sanitized = sanitize_string_input(v)
            validate_safe_input(sanitized)
            return sanitized
        return v


class ProductResponse(ProductBase):
    """Schema for product response"""
    id: int
    owner_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    images: List[ProductImageSchema] = []
    category: Optional[CategorySchema] = None
    # Price will be set based on user role
    price: Optional[Decimal] = None

    class Config:
        from_attributes = True


class ProductListResponse(BaseModel):
    """Schema for paginated product list"""
    items: List[ProductResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class ProductFilters(BaseModel):
    """Schema for product filtering"""
    category_id: Optional[int] = None
    min_price: Optional[Decimal] = None
    max_price: Optional[Decimal] = None
    is_subscription_available: Optional[bool] = None
    search_query: Optional[str] = None
    is_active: bool = True
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)


class StockUpdate(BaseModel):
    """Schema for stock quantity update"""
    quantity_delta: int = Field(..., description="Change in stock quantity (positive or negative)")
