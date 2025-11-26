"""Bulk Discount Pydantic schemas"""
from pydantic import BaseModel, Field, field_validator
from decimal import Decimal
from typing import Optional
from app.core.validators import validate_discount_percentage


class BulkDiscountRuleCreate(BaseModel):
    """Request schema for creating bulk discount rule"""
    product_id: Optional[int] = Field(None, description="Product ID (null for all products)")
    category_id: Optional[int] = Field(None, description="Category ID (null for all categories)")
    min_quantity: int = Field(..., gt=0, description="Minimum quantity to qualify for discount")
    discount_percentage: Decimal = Field(..., gt=0, le=100, description="Discount percentage (0-100)")
    
    @field_validator('discount_percentage')
    @classmethod
    def validate_discount_percentage_field(cls, v: Decimal) -> Decimal:
        """Validate discount percentage"""
        return validate_discount_percentage(v)


class BulkDiscountRuleUpdate(BaseModel):
    """Request schema for updating bulk discount rule"""
    min_quantity: Optional[int] = Field(None, gt=0, description="Minimum quantity")
    discount_percentage: Optional[Decimal] = Field(None, gt=0, le=100, description="Discount percentage")
    is_active: Optional[bool] = Field(None, description="Active status")
    
    @field_validator('discount_percentage')
    @classmethod
    def validate_discount_percentage_field(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        """Validate discount percentage"""
        if v is not None:
            return validate_discount_percentage(v)
        return v


class BulkDiscountRuleResponse(BaseModel):
    """Response schema for bulk discount rule"""
    id: int
    product_id: Optional[int]
    category_id: Optional[int]
    min_quantity: int
    discount_percentage: Decimal
    is_active: bool
    
    class Config:
        from_attributes = True


class BulkDiscountRuleListResponse(BaseModel):
    """Response schema for list of bulk discount rules"""
    rules: list[BulkDiscountRuleResponse]
    total: int
