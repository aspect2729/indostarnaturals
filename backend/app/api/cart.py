"""Cart API endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.cart import (
    CartResponse,
    CartItemCreate,
    CartItemUpdate,
    CouponApply
)
from app.services.cart_service import cart_service
from app.services.dependencies import get_current_active_user
from app.models.user import User


router = APIRouter(prefix="/api/v1/cart", tags=["cart"])


@router.get("", response_model=CartResponse)
async def get_cart(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get user's cart with role-based pricing.
    
    Requires authentication.
    """
    try:
        cart = cart_service.get_cart(
            user_id=current_user.id,
            db=db
        )
        return cart
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve cart"
        )


@router.post("/items", response_model=CartResponse)
async def add_item_to_cart(
    item_data: CartItemCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Add item to cart with stock validation.
    
    Requires authentication.
    """
    try:
        cart = cart_service.add_item(
            user_id=current_user.id,
            item_data=item_data,
            db=db
        )
        return cart
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add item to cart"
        )


@router.put("/items/{item_id}", response_model=CartResponse)
async def update_cart_item(
    item_id: int,
    quantity_data: CartItemUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update cart item quantity with total recalculation.
    
    Requires authentication.
    """
    try:
        cart = cart_service.update_item_quantity(
            user_id=current_user.id,
            item_id=item_id,
            quantity_data=quantity_data,
            db=db
        )
        return cart
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update cart item"
        )


@router.delete("/items/{item_id}", response_model=CartResponse)
async def remove_cart_item(
    item_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Remove item from cart with total recalculation.
    
    Requires authentication.
    """
    try:
        cart = cart_service.remove_item(
            user_id=current_user.id,
            item_id=item_id,
            db=db
        )
        return cart
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to remove cart item"
        )


@router.post("/coupon", response_model=CartResponse)
async def apply_coupon_to_cart(
    coupon_data: CouponApply,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Apply coupon code to cart with validation.
    
    Requires authentication.
    """
    try:
        cart = cart_service.apply_coupon(
            user_id=current_user.id,
            coupon_code=coupon_data.coupon_code,
            db=db
        )
        return cart
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to apply coupon"
        )


@router.delete("/coupon", response_model=CartResponse)
async def remove_coupon_from_cart(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Remove coupon from cart.
    
    Requires authentication.
    """
    try:
        cart = cart_service.remove_coupon(
            user_id=current_user.id,
            db=db
        )
        return cart
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to remove coupon"
        )
