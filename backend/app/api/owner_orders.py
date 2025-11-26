"""Owner Order Management API endpoints"""
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.order import (
    OrderStatusUpdate,
    OrderResponseWithUser,
    OwnerOrderListResponse,
    OrderItemResponse,
    AddressResponse
)
from app.services.order_service import order_service
from app.services.dependencies import require_owner
from app.models.user import User
from app.models.enums import OrderStatus, UserRole
from math import ceil


router = APIRouter(prefix="/api/v1/owner/orders", tags=["owner-orders"])


@router.get("", response_model=OwnerOrderListResponse)
async def list_all_orders(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    status_filter: Optional[OrderStatus] = Query(None, description="Filter by order status"),
    user_role_filter: Optional[UserRole] = Query(None, description="Filter by user role"),
    start_date: Optional[datetime] = Query(None, description="Filter by start date"),
    end_date: Optional[datetime] = Query(None, description="Filter by end date"),
    current_user: User = Depends(require_owner),
    db: Session = Depends(get_db)
):
    """
    List all orders with filtering (owner only).
    
    Returns a paginated list of all orders in the system with filtering options.
    Only accessible by users with owner role.
    
    Filters:
    - status_filter: Filter by order status
    - user_role_filter: Filter by user role (consumer, distributor)
    - start_date: Filter orders created on or after this date
    - end_date: Filter orders created on or before this date
    
    Requirements: 8.2, 8.5
    """
    try:
        # Get all orders with filters
        orders, total_count = order_service.get_all_orders(
            page=page,
            page_size=page_size,
            status_filter=status_filter,
            user_role_filter=user_role_filter,
            start_date=start_date,
            end_date=end_date,
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
            
            # Build order response with user information
            order_response = OrderResponseWithUser(
                id=order.id,
                user_id=order.user_id,
                user_name=order.user.name,
                user_email=order.user.email,
                user_phone=order.user.phone,
                user_role=order.user.role.value,
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
        
        return OwnerOrderListResponse(
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


@router.put("/{order_id}/status", response_model=OrderResponseWithUser)
async def update_order_status(
    order_id: int,
    status_update: OrderStatusUpdate,
    current_user: User = Depends(require_owner),
    db: Session = Depends(get_db)
):
    """
    Update order status (owner only).
    
    Updates the status of an order and creates an audit log entry.
    Sends notifications to the customer based on the new status.
    
    Valid status transitions:
    - PENDING -> CONFIRMED, CANCELLED
    - CONFIRMED -> PACKED, CANCELLED
    - PACKED -> OUT_FOR_DELIVERY, CANCELLED
    - OUT_FOR_DELIVERY -> DELIVERED, CANCELLED
    - Any status -> REFUNDED (via refund endpoint)
    
    Requirements: 8.2
    """
    try:
        # Update order status
        order = order_service.update_order_status(
            order_id=order_id,
            new_status=status_update.status,
            actor_id=current_user.id,
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
        
        # Build order response with user information
        return OrderResponseWithUser(
            id=order.id,
            user_id=order.user_id,
            user_name=order.user.name,
            user_email=order.user.email,
            user_phone=order.user.phone,
            user_role=order.user.role.value,
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
        # Order not found or invalid status
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        # Log the error for debugging
        print(f"Error updating order status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update order status"
        )


@router.post("/{order_id}/refund", response_model=OrderResponseWithUser)
async def process_refund(
    order_id: int,
    current_user: User = Depends(require_owner),
    db: Session = Depends(get_db)
):
    """
    Process refund for an order (owner only).
    
    This endpoint:
    1. Updates order status to REFUNDED
    2. Updates payment status to REFUNDED
    3. Restores product stock quantities
    4. Creates audit log entry
    
    Can only refund orders that have been paid.
    
    Requirements: 8.5
    """
    try:
        # Process refund
        order = order_service.process_refund(
            order_id=order_id,
            actor_id=current_user.id,
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
        
        # Build order response with user information
        return OrderResponseWithUser(
            id=order.id,
            user_id=order.user_id,
            user_name=order.user.name,
            user_email=order.user.email,
            user_phone=order.user.phone,
            user_role=order.user.role.value,
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
        # Order not found or cannot be refunded
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        # Log the error for debugging
        print(f"Error processing refund: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process refund"
        )
