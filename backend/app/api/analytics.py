"""Owner Analytics API endpoints"""
from typing import Optional
from datetime import date, datetime
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.analytics_service import AnalyticsService
from app.services.dependencies import require_owner
from app.models.user import User


router = APIRouter(prefix="/api/v1/owner", tags=["owner-analytics"])


@router.get("/analytics/dashboard")
async def get_dashboard_metrics(
    current_user: User = Depends(require_owner),
    db: Session = Depends(get_db)
):
    """
    Get dashboard metrics including revenue, order count, active subscriptions, and low stock alerts.
    
    Returns:
    - total_revenue: Total revenue from paid orders
    - order_count: Total number of orders
    - active_subscriptions: Number of active subscriptions
    - low_stock_alerts: List of products with stock < 10
    
    Requirements: 10.1
    """
    try:
        metrics = await AnalyticsService.get_dashboard_metrics(db)
        return metrics
    except Exception as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=f"Failed to fetch dashboard metrics: {str(e)}")


@router.get("/analytics/revenue")
async def get_revenue_report(
    start_date: Optional[date] = Query(None, description="Start date for filtering"),
    end_date: Optional[date] = Query(None, description="End date for filtering"),
    current_user: User = Depends(require_owner),
    db: Session = Depends(get_db)
):
    """
    Get revenue report with date range filtering.
    
    Query Parameters:
    - start_date: Start date for filtering (optional)
    - end_date: End date for filtering (optional)
    
    Returns:
    - start_date: Start date of the report
    - end_date: End date of the report
    - total_revenue: Total revenue in the date range
    - total_orders: Total number of orders in the date range
    - daily_data: Array of daily revenue and order count
    
    Requirements: 10.1
    """
    try:
        report = await AnalyticsService.get_revenue_report(db, start_date, end_date)
        return report
    except Exception as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=f"Failed to fetch revenue report: {str(e)}")


@router.get("/inventory")
async def get_inventory_status(
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    current_user: User = Depends(require_owner),
    db: Session = Depends(get_db)
):
    """
    Get inventory status with category filtering.
    
    Query Parameters:
    - category_id: Category ID for filtering (optional)
    
    Returns:
    List of products with inventory information including:
    - product_id
    - title
    - sku
    - category_id
    - stock_quantity
    - consumer_price
    - distributor_price
    - is_low_stock
    
    Requirements: 10.2
    """
    inventory = await AnalyticsService.get_inventory_status(db, category_id)
    return {"products": inventory}



@router.get("/audit-logs")
async def get_audit_logs(
    action_type: Optional[str] = Query(None, description="Filter by action type"),
    start_date: Optional[datetime] = Query(None, description="Start date for filtering"),
    end_date: Optional[datetime] = Query(None, description="End date for filtering"),
    actor_id: Optional[int] = Query(None, description="Filter by actor ID"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of logs to return"),
    current_user: User = Depends(require_owner),
    db: Session = Depends(get_db)
):
    """
    Get audit logs with filtering (owner only).
    
    Query Parameters:
    - action_type: Filter by action type (optional)
    - start_date: Start date for filtering (optional)
    - end_date: End date for filtering (optional)
    - actor_id: Filter by actor ID (optional)
    - limit: Maximum number of logs to return (default: 100, max: 1000)
    
    Returns:
    List of audit log entries with:
    - id
    - actor_id
    - action_type
    - object_type
    - object_id
    - details
    - ip_address
    - created_at
    
    Requirements: 15.4
    """
    logs = await AnalyticsService.get_audit_logs(
        db=db,
        action_type_filter=action_type,
        start_date=start_date,
        end_date=end_date,
        actor_id_filter=actor_id,
        limit=limit
    )
    return {"logs": logs}
