"""Subscription API endpoints

Handles subscription creation, management, and user subscription operations.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.models.product import Product
from app.services.dependencies import get_current_user
from app.services.subscription_service import subscription_service
from app.schemas.subscription import (
    SubscriptionCreate,
    SubscriptionResponse,
    SubscriptionListResponse,
    RazorpaySubscriptionResponse,
    SubscriptionPaymentVerification
)

router = APIRouter(prefix="/api/v1/subscriptions", tags=["subscriptions"])


@router.post("", response_model=RazorpaySubscriptionResponse, status_code=status.HTTP_201_CREATED)
def create_subscription(
    subscription_data: SubscriptionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new subscription for a product.
    
    Validates:
    - Product is subscription-available
    - Delivery address belongs to user
    - Creates Razorpay subscription
    
    Requirements: 7.1, 7.2
    """
    try:
        # Verify product is subscription-available
        product = db.query(Product).filter(Product.id == subscription_data.product_id).first()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with ID {subscription_data.product_id} not found"
            )
        
        if not product.is_subscription_available:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Product '{product.title}' is not available for subscription"
            )
        
        # Create subscription
        subscription = subscription_service.create_subscription(
            user_id=current_user.id,
            product_id=subscription_data.product_id,
            plan_frequency=subscription_data.plan_frequency,
            start_date=subscription_data.start_date,
            delivery_address_id=subscription_data.delivery_address_id,
            db=db
        )
        
        # Return Razorpay subscription details for frontend
        from app.core.config import settings
        return RazorpaySubscriptionResponse(
            razorpay_subscription_id=subscription.razorpay_subscription_id,
            status="active",
            subscription_id=subscription.id,
            key_id=settings.RAZORPAY_KEY_ID
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        # Log the full error for debugging
        import traceback
        print(f"Error creating subscription: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create subscription: {str(e)}"
        )


@router.get("", response_model=SubscriptionListResponse)
def get_user_subscriptions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all subscriptions for the current user.
    
    Returns list of subscriptions with product and address details.
    
    Requirements: 7.1
    """
    try:
        subscriptions = subscription_service.get_user_subscriptions(
            user_id=current_user.id,
            db=db
        )
        
        return SubscriptionListResponse(
            subscriptions=subscriptions,
            total=len(subscriptions)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve subscriptions: {str(e)}"
        )


@router.get("/{subscription_id}", response_model=SubscriptionResponse)
def get_subscription_details(
    subscription_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get details of a specific subscription.
    
    Validates that subscription belongs to current user.
    
    Requirements: 7.1
    """
    try:
        subscriptions = subscription_service.get_user_subscriptions(
            user_id=current_user.id,
            db=db
        )
        
        # Find the requested subscription
        subscription = next(
            (sub for sub in subscriptions if sub.id == subscription_id),
            None
        )
        
        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Subscription with ID {subscription_id} not found or does not belong to user"
            )
        
        return subscription
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve subscription: {str(e)}"
        )


@router.put("/{subscription_id}/pause", response_model=SubscriptionResponse)
def pause_subscription(
    subscription_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Pause a subscription.
    
    Suspends billing and deliveries until resumed.
    
    Requirements: 7.5
    """
    try:
        subscription = subscription_service.pause_subscription(
            subscription_id=subscription_id,
            user_id=current_user.id,
            db=db
        )
        
        return subscription
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to pause subscription: {str(e)}"
        )


@router.put("/{subscription_id}/resume", response_model=SubscriptionResponse)
def resume_subscription(
    subscription_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Resume a paused subscription.
    
    Restores billing and deliveries.
    
    Requirements: 7.5
    """
    try:
        subscription = subscription_service.resume_subscription(
            subscription_id=subscription_id,
            user_id=current_user.id,
            db=db
        )
        
        return subscription
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to resume subscription: {str(e)}"
        )


@router.delete("/{subscription_id}", response_model=SubscriptionResponse)
def cancel_subscription(
    subscription_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cancel a subscription permanently.
    
    Cancels Razorpay subscription and prevents future charges.
    
    Requirements: 7.6
    """
    try:
        subscription = subscription_service.cancel_subscription(
            subscription_id=subscription_id,
            user_id=current_user.id,
            db=db
        )
        
        return subscription
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel subscription: {str(e)}"
        )


@router.post("/{subscription_id}/verify-payment", response_model=SubscriptionResponse)
def verify_subscription_payment(
    subscription_id: int,
    payment_data: SubscriptionPaymentVerification,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Verify subscription payment after Razorpay checkout.
    
    Validates the payment signature from Razorpay to ensure payment authenticity.
    
    Requirements: 7.2
    """
    try:
        subscription = subscription_service.verify_subscription_payment(
            subscription_id=subscription_id,
            user_id=current_user.id,
            razorpay_payment_id=payment_data.razorpay_payment_id,
            razorpay_subscription_id=payment_data.razorpay_subscription_id,
            razorpay_signature=payment_data.razorpay_signature,
            db=db
        )
        
        return subscription
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to verify subscription payment: {str(e)}"
        )
