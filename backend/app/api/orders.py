"""Order API endpoints"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.order import (
    OrderCreate,
    OrderResponse,
    OrderListResponse,
    RazorpayOrderResponse,
    OrderItemResponse,
    AddressResponse
)
from app.services.order_service import order_service
from app.services.payment_service import payment_service
from app.services.cart_service import cart_service
from app.services.dependencies import get_current_active_user
from app.models.user import User
from app.models.enums import OrderStatus
from math import ceil


router = APIRouter(prefix="/api/v1/orders", tags=["orders"])


@router.post("", response_model=RazorpayOrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_data: OrderCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create order (initiate checkout).
    
    This endpoint:
    1. Validates cart items against current stock
    2. Creates order and order items
    3. Reduces product stock quantities
    4. Clears the cart
    5. Creates Razorpay order for payment
    
    Requires authentication.
    
    Requirements: 6.1, 8.4
    """
    try:
        # Validate cart before order creation
        validation = cart_service.validate_cart(
            user_id=current_user.id,
            db=db
        )
        
        if not validation.is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "Cart validation failed",
                    "errors": validation.errors
                }
            )
        
        # Create order
        order = order_service.create_order(
            user_id=current_user.id,
            address_id=order_data.address_id,
            db=db
        )
        
        # Create Razorpay order for payment
        razorpay_order = await payment_service.create_razorpay_order(
            db=db,
            order_id=order.id,
            amount=order.final_amount
        )
        
        # Return Razorpay order details for frontend payment integration
        return RazorpayOrderResponse(
            razorpay_order_id=razorpay_order["razorpay_order_id"],
            amount=razorpay_order["amount"],
            currency=razorpay_order["currency"],
            key_id=razorpay_order["key_id"],
            order_id=order.id,
            order_number=order.order_number
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        # Log the error for debugging
        print(f"Error creating order: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create order"
        )


@router.get("", response_model=OrderListResponse)
async def get_user_orders(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    status_filter: Optional[OrderStatus] = Query(None, description="Filter by order status"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get user's orders with pagination.
    
    Returns a paginated list of orders for the authenticated user.
    Optionally filter by order status.
    
    Requires authentication.
    
    Requirements: 8.4
    """
    try:
        # Get user's orders
        orders, total_count = order_service.get_user_orders(
            user_id=current_user.id,
            page=page,
            page_size=page_size,
            status_filter=status_filter,
            db=db
        )
        
        # Convert orders to response format
        order_responses = []
        for order in orders:
            # Build order items
            items = [
                OrderItemResponse(
                    id=item.id,
                    order_id=item.order_id,
                    product_id=item.product_id,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                    total_price=item.total_price,
                    product_title=item.product.title,
                    product_sku=item.product.sku
                )
                for item in order.items
            ]
            
            # Build address
            address = AddressResponse(
                id=order.delivery_address.id,
                name=order.delivery_address.name,
                phone=order.delivery_address.phone,
                address_line1=order.delivery_address.address_line1,
                address_line2=order.delivery_address.address_line2,
                city=order.delivery_address.city,
                state=order.delivery_address.state,
                postal_code=order.delivery_address.postal_code,
                country=order.delivery_address.country
            )
            
            # Build order response
            order_response = OrderResponse(
                id=order.id,
                user_id=order.user_id,
                order_number=order.order_number,
                total_amount=order.total_amount,
                discount_amount=order.discount_amount,
                final_amount=order.final_amount,
                payment_status=order.payment_status,
                order_status=order.order_status,
                delivery_address=address,
                items=items,
                notes=order.notes,
                created_at=order.created_at,
                updated_at=order.updated_at
            )
            order_responses.append(order_response)
        
        # Calculate total pages
        total_pages = ceil(total_count / page_size)
        
        return OrderListResponse(
            orders=order_responses,
            total=total_count,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
        
    except Exception as e:
        # Log the error for debugging
        print(f"Error retrieving orders: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve orders"
        )


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order_details(
    order_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get order details by ID.
    
    Returns detailed information about a specific order.
    Users can only access their own orders.
    
    Requires authentication.
    
    Requirements: 8.4
    """
    try:
        # Get order with ownership validation
        order = order_service.get_order_by_id(
            order_id=order_id,
            user_id=current_user.id,
            db=db
        )
        
        # Build order items
        items = [
            OrderItemResponse(
                id=item.id,
                order_id=item.order_id,
                product_id=item.product_id,
                quantity=item.quantity,
                unit_price=item.unit_price,
                total_price=item.total_price,
                product_title=item.product.title,
                product_sku=item.product.sku
            )
            for item in order.items
        ]
        
        # Build address
        address = AddressResponse(
            id=order.delivery_address.id,
            name=order.delivery_address.name,
            phone=order.delivery_address.phone,
            address_line1=order.delivery_address.address_line1,
            address_line2=order.delivery_address.address_line2,
            city=order.delivery_address.city,
            state=order.delivery_address.state,
            postal_code=order.delivery_address.postal_code,
            country=order.delivery_address.country
        )
        
        # Build order response
        return OrderResponse(
            id=order.id,
            user_id=order.user_id,
            order_number=order.order_number,
            total_amount=order.total_amount,
            discount_amount=order.discount_amount,
            final_amount=order.final_amount,
            payment_status=order.payment_status,
            order_status=order.order_status,
            delivery_address=address,
            items=items,
            notes=order.notes,
            created_at=order.created_at,
            updated_at=order.updated_at
        )
        
    except ValueError as e:
        # Order not found or doesn't belong to user
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        # Log the error for debugging
        print(f"Error retrieving order: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve order"
        )

