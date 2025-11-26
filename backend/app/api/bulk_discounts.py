"""Bulk Discount API endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.schemas.bulk_discount import (
    BulkDiscountRuleCreate,
    BulkDiscountRuleUpdate,
    BulkDiscountRuleResponse,
    BulkDiscountRuleListResponse
)
from app.models.bulk_discount_rule import BulkDiscountRule
from app.models.product import Product
from app.models.category import Category
from app.services.dependencies import require_owner
from app.models.user import User


router = APIRouter(prefix="/api/v1/owner/bulk-discounts", tags=["bulk-discounts"])


@router.post("", response_model=BulkDiscountRuleResponse)
async def create_bulk_discount_rule(
    rule_data: BulkDiscountRuleCreate,
    current_user: User = Depends(require_owner),
    db: Session = Depends(get_db)
):
    """
    Create a new bulk discount rule.
    
    Owner only endpoint.
    """
    # Validate product_id if provided
    if rule_data.product_id:
        product = db.query(Product).filter(Product.id == rule_data.product_id).first()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with ID {rule_data.product_id} not found"
            )
    
    # Validate category_id if provided
    if rule_data.category_id:
        category = db.query(Category).filter(Category.id == rule_data.category_id).first()
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category with ID {rule_data.category_id} not found"
            )
    
    # Create bulk discount rule
    rule = BulkDiscountRule(
        product_id=rule_data.product_id,
        category_id=rule_data.category_id,
        min_quantity=rule_data.min_quantity,
        discount_percentage=rule_data.discount_percentage,
        is_active=True
    )
    
    db.add(rule)
    db.commit()
    db.refresh(rule)
    
    return rule


@router.get("", response_model=BulkDiscountRuleListResponse)
async def list_bulk_discount_rules(
    product_id: Optional[int] = None,
    category_id: Optional[int] = None,
    is_active: Optional[bool] = None,
    current_user: User = Depends(require_owner),
    db: Session = Depends(get_db)
):
    """
    List all bulk discount rules with optional filtering.
    
    Owner only endpoint.
    """
    query = db.query(BulkDiscountRule)
    
    # Apply filters
    if product_id is not None:
        query = query.filter(BulkDiscountRule.product_id == product_id)
    
    if category_id is not None:
        query = query.filter(BulkDiscountRule.category_id == category_id)
    
    if is_active is not None:
        query = query.filter(BulkDiscountRule.is_active == is_active)
    
    rules = query.all()
    
    return BulkDiscountRuleListResponse(
        rules=rules,
        total=len(rules)
    )


@router.get("/{rule_id}", response_model=BulkDiscountRuleResponse)
async def get_bulk_discount_rule(
    rule_id: int,
    current_user: User = Depends(require_owner),
    db: Session = Depends(get_db)
):
    """
    Get a specific bulk discount rule by ID.
    
    Owner only endpoint.
    """
    rule = db.query(BulkDiscountRule).filter(BulkDiscountRule.id == rule_id).first()
    
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bulk discount rule with ID {rule_id} not found"
        )
    
    return rule


@router.put("/{rule_id}", response_model=BulkDiscountRuleResponse)
async def update_bulk_discount_rule(
    rule_id: int,
    rule_data: BulkDiscountRuleUpdate,
    current_user: User = Depends(require_owner),
    db: Session = Depends(get_db)
):
    """
    Update a bulk discount rule.
    
    Owner only endpoint.
    """
    rule = db.query(BulkDiscountRule).filter(BulkDiscountRule.id == rule_id).first()
    
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bulk discount rule with ID {rule_id} not found"
        )
    
    # Update fields if provided
    if rule_data.min_quantity is not None:
        rule.min_quantity = rule_data.min_quantity
    
    if rule_data.discount_percentage is not None:
        rule.discount_percentage = rule_data.discount_percentage
    
    if rule_data.is_active is not None:
        rule.is_active = rule_data.is_active
    
    db.commit()
    db.refresh(rule)
    
    return rule


@router.delete("/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_bulk_discount_rule(
    rule_id: int,
    current_user: User = Depends(require_owner),
    db: Session = Depends(get_db)
):
    """
    Delete a bulk discount rule.
    
    Owner only endpoint.
    """
    rule = db.query(BulkDiscountRule).filter(BulkDiscountRule.id == rule_id).first()
    
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bulk discount rule with ID {rule_id} not found"
        )
    
    db.delete(rule)
    db.commit()
    
    return None
