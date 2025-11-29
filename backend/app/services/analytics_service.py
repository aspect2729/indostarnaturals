"""Analytics service for owner dashboard metrics and reports"""
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, Dict, Any, List
from sqlalchemy import func, and_, or_, desc
from sqlalchemy.orm import Session
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.product import Product
from app.models.subscription import Subscription
from app.models.enums import OrderStatus, PaymentStatus, SubscriptionStatus


class AnalyticsService:
    """Service for analytics and reporting"""

    @staticmethod
    async def get_dashboard_metrics(db: Session) -> Dict[str, Any]:
        """
        Get dashboard metrics including revenue, order count, active subscriptions, and low stock alerts.
        
        Args:
            db: Database session
            
        Returns:
            Dictionary containing dashboard metrics
        """
        # Calculate total revenue from paid orders
        total_revenue = db.query(
            func.coalesce(func.sum(Order.final_amount), 0)
        ).filter(
            Order.payment_status == "paid"
        ).scalar()

        # Count total orders
        order_count = db.query(func.count(Order.id)).scalar()

        # Count active subscriptions
        active_subscriptions = db.query(
            func.count(Subscription.id)
        ).filter(
            Subscription.status == "active"
        ).scalar()

        # Get low stock alerts (products with stock < 10)
        low_stock_products = db.query(Product).filter(
            and_(
                Product.is_active == True,
                Product.stock_quantity < 10
            )
        ).all()

        low_stock_alerts = [
            {
                "id": product.id,
                "product_id": product.id,
                "title": product.title,
                "sku": product.sku,
                "stock_quantity": product.stock_quantity
            }
            for product in low_stock_products
        ]

        return {
            "total_revenue": float(total_revenue) if total_revenue else 0.0,
            "order_count": order_count or 0,
            "active_subscriptions": active_subscriptions or 0,
            "low_stock_alerts": low_stock_alerts
        }

    @staticmethod
    async def get_revenue_report(
        db: Session,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Get revenue report with date range filtering.
        
        Args:
            db: Database session
            start_date: Start date for filtering (optional)
            end_date: End date for filtering (optional)
            
        Returns:
            Dictionary containing revenue report data
        """
        query = db.query(
            func.date(Order.created_at).label('date'),
            func.sum(Order.final_amount).label('revenue'),
            func.count(Order.id).label('order_count')
        ).filter(
            Order.payment_status == "paid"
        )

        # Apply date filters if provided
        if start_date:
            query = query.filter(func.date(Order.created_at) >= start_date)
        if end_date:
            query = query.filter(func.date(Order.created_at) <= end_date)

        # Group by date and order by date descending
        query = query.group_by(func.date(Order.created_at)).order_by(desc('date'))

        results = query.all()

        # Calculate totals with proper null handling
        total_revenue = Decimal(0)
        total_orders = 0
        
        if results:
            for row in results:
                if row.revenue:
                    total_revenue += row.revenue
                if row.order_count:
                    total_orders += row.order_count

        return {
            "start_date": start_date.isoformat() if start_date else None,
            "end_date": end_date.isoformat() if end_date else None,
            "total_revenue": float(total_revenue),
            "total_orders": total_orders,
            "daily_data": [
                {
                    "date": row.date.isoformat() if row.date else None,
                    "revenue": float(row.revenue) if row.revenue else 0.0,
                    "order_count": row.order_count if row.order_count else 0
                }
                for row in results
            ]
        }

    @staticmethod
    async def get_inventory_status(
        db: Session,
        category_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get inventory status with category filtering.
        
        Args:
            db: Database session
            category_id: Category ID for filtering (optional)
            
        Returns:
            List of products with inventory information
        """
        query = db.query(Product).filter(Product.is_active == True)

        # Apply category filter if provided
        if category_id:
            query = query.filter(Product.category_id == category_id)

        products = query.order_by(Product.stock_quantity.asc()).all()

        return [
            {
                "product_id": product.id,
                "title": product.title,
                "sku": product.sku,
                "category_id": product.category_id,
                "stock_quantity": product.stock_quantity,
                "consumer_price": float(product.consumer_price),
                "distributor_price": float(product.distributor_price),
                "is_low_stock": product.stock_quantity < 10
            }
            for product in products
        ]

    @staticmethod
    async def get_low_stock_alerts(
        db: Session,
        threshold: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get low stock alerts for products below threshold.
        
        Args:
            db: Database session
            threshold: Stock quantity threshold (default: 10)
            
        Returns:
            List of products with low stock
        """
        products = db.query(Product).filter(
            and_(
                Product.is_active == True,
                Product.stock_quantity < threshold
            )
        ).order_by(Product.stock_quantity.asc()).all()

        return [
            {
                "product_id": product.id,
                "title": product.title,
                "sku": product.sku,
                "category_id": product.category_id,
                "stock_quantity": product.stock_quantity,
                "threshold": threshold
            }
            for product in products
        ]


    @staticmethod
    async def get_audit_logs(
        db: Session,
        action_type_filter: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        actor_id_filter: Optional[int] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get audit logs with filtering by action type, date range, and actor.
        
        Args:
            db: Database session
            action_type_filter: Filter by action type (optional)
            start_date: Start date for filtering (optional)
            end_date: End date for filtering (optional)
            actor_id_filter: Filter by actor ID (optional)
            limit: Maximum number of logs to return (default: 100)
            
        Returns:
            List of audit log entries
        """
        from app.models.audit_log import AuditLog
        
        query = db.query(AuditLog)
        
        # Apply action type filter
        if action_type_filter:
            query = query.filter(AuditLog.action_type == action_type_filter)
        
        # Apply date filters
        if start_date:
            query = query.filter(AuditLog.created_at >= start_date)
        if end_date:
            query = query.filter(AuditLog.created_at <= end_date)
        
        # Apply actor filter
        if actor_id_filter:
            query = query.filter(AuditLog.actor_id == actor_id_filter)
        
        # Order by created_at descending and limit results
        logs = query.order_by(AuditLog.created_at.desc()).limit(limit).all()
        
        return [
            {
                "id": log.id,
                "actor_id": log.actor_id,
                "action_type": log.action_type,
                "object_type": log.object_type,
                "object_id": log.object_id,
                "details": log.details,
                "ip_address": log.ip_address,
                "created_at": log.created_at.isoformat()
            }
            for log in logs
        ]
