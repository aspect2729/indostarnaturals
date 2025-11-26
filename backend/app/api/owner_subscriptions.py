"""Owner Subscription Management API endpoints

Handles owner-only subscription management operations including viewing all subscriptions
and delivery calendar.
"""
from typing import List, Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from app.core.database import get_db
from app.models.user import User
from app.models.subscription import Subscription
from app.models.enums import UserRole, SubscriptionStatus
from app.services.dependencies import get_current_user
from app.schemas.subscription import SubscriptionResponse, SubscriptionListResponse
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/owner/subscriptions", tags=["owner-subscriptions"])


def require_owner(current_user: User = Depends(get_current_user)) -> User:
    """Dependency to ensure user is an owner"""
    if current_user.role != UserRole.OWNER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only owners can access this endpoint"
        )
    return current_user


class DeliveryCalendarItem(BaseModel):
    """Delivery calendar item schema"""
    subscription_id: int
    user_id: int
    user_name: str
    product_id: int
    product_title: str
    delivery_date: date
    delivery_address: str
    status: SubscriptionStatus
    
    class Config:
        orm_mode = True


class DeliveryCalendarResponse(BaseModel):
    """Delivery calendar response schema"""
    deliveries: List[DeliveryCalendarItem]
    total: int
    date_range: str


@router.get("", response_model=SubscriptionListResponse)
def list_all_subscriptions(
    status_filter: Optional[SubscriptionStatus] = Query(None, description="Filter by subscription status"),
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    current_user: User = Depends(require_owner),
    db: Session = Depends(get_db)
):
    """
    List all subscriptions in the system (owner only).
    
    Supports filtering by status and user ID.
    
    Requirements: 10.3
    """
    try:
        # Build query
        query = db.query(Subscription)
        
        # Apply filters
        if status_filter:
            query = query.filter(Subscription.status == status_filter)
        
        if user_id:
            query = query.filter(Subscription.user_id == user_id)
        
        # Get total count
        total = query.count()
        
        # Apply pagination and fetch
        subscriptions = query.order_by(
            Subscription.created_at.desc()
        ).offset(skip).limit(limit).all()
        
        return SubscriptionListResponse(
            subscriptions=subscriptions,
            total=total
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve subscriptions: {str(e)}"
        )


@router.get("/calendar", response_model=DeliveryCalendarResponse)
def get_delivery_calendar(
    start_date: Optional[date] = Query(None, description="Start date for calendar view"),
    end_date: Optional[date] = Query(None, description="End date for calendar view"),
    current_user: User = Depends(require_owner),
    db: Session = Depends(get_db)
):
    """
    Get delivery calendar showing scheduled deliveries organized by date (owner only).
    
    Returns all active subscriptions with their next delivery dates within the specified range.
    If no date range is provided, returns deliveries for the next 30 days.
    
    Requirements: 10.3
    """
    try:
        from datetime import timedelta
        from sqlalchemy.orm import joinedload
        
        # Set default date range if not provided
        if not start_date:
            start_date = date.today()
        if not end_date:
            end_date = start_date + timedelta(days=30)
        
        # Query active subscriptions with deliveries in the date range
        subscriptions = db.query(Subscription).options(
            joinedload(Subscription.user),
            joinedload(Subscription.product),
            joinedload(Subscription.delivery_address)
        ).filter(
            and_(
                Subscription.status == SubscriptionStatus.ACTIVE,
                Subscription.next_delivery_date >= start_date,
                Subscription.next_delivery_date <= end_date
            )
        ).order_by(Subscription.next_delivery_date).all()
        
        # Build delivery calendar items
        deliveries = []
        for sub in subscriptions:
            # Format address
            addr = sub.delivery_address
            address_str = f"{addr.address_line1}, {addr.city}, {addr.state} {addr.postal_code}"
            
            deliveries.append(DeliveryCalendarItem(
                subscription_id=sub.id,
                user_id=sub.user_id,
                user_name=sub.user.name,
                product_id=sub.product_id,
                product_title=sub.product.title,
                delivery_date=sub.next_delivery_date,
                delivery_address=address_str,
                status=sub.status
            ))
        
        date_range = f"{start_date.isoformat()} to {end_date.isoformat()}"
        
        return DeliveryCalendarResponse(
            deliveries=deliveries,
            total=len(deliveries),
            date_range=date_range
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve delivery calendar: {str(e)}"
        )
