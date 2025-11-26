"""Monitoring and Metrics Collection

Provides custom metrics for business KPIs and system health monitoring.
Integrates with Sentry for error tracking and alerting.
"""
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from app.models.order import Order
from app.models.subscription import Subscription
from app.models.product import Product
from app.models.enums import OrderStatus, SubscriptionStatus, PaymentStatus

logger = logging.getLogger(__name__)


class MetricsCollector:
    """Collects and reports custom business metrics"""
    
    @staticmethod
    def collect_order_metrics(db: Session, time_window_hours: int = 24) -> Dict[str, Any]:
        """
        Collect order-related metrics for monitoring.
        
        Args:
            db: Database session
            time_window_hours: Time window for metrics collection (default 24 hours)
            
        Returns:
            Dictionary containing order metrics
        """
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=time_window_hours)
            
            # Total orders in time window
            total_orders = db.query(func.count(Order.id)).filter(
                Order.created_at >= cutoff_time
            ).scalar() or 0
            
            # Confirmed orders
            confirmed_orders = db.query(func.count(Order.id)).filter(
                and_(
                    Order.created_at >= cutoff_time,
                    Order.order_status == OrderStatus.CONFIRMED
                )
            ).scalar() or 0
            
            # Failed orders
            failed_orders = db.query(func.count(Order.id)).filter(
                and_(
                    Order.created_at >= cutoff_time,
                    Order.payment_status == PaymentStatus.FAILED
                )
            ).scalar() or 0
            
            # Total revenue
            revenue = db.query(func.sum(Order.final_amount)).filter(
                and_(
                    Order.created_at >= cutoff_time,
                    Order.payment_status == PaymentStatus.PAID
                )
            ).scalar() or Decimal('0')
            
            # Calculate failure rate
            failure_rate = (failed_orders / total_orders * 100) if total_orders > 0 else 0
            
            metrics = {
                'time_window_hours': time_window_hours,
                'total_orders': total_orders,
                'confirmed_orders': confirmed_orders,
                'failed_orders': failed_orders,
                'failure_rate_percent': round(failure_rate, 2),
                'revenue': float(revenue),
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }
            
            logger.info("Order metrics collected", extra=metrics)
            
            # Alert if failure rate is high
            if failure_rate > 5.0:
                logger.warning(
                    f"High order failure rate detected: {failure_rate:.2f}%",
                    extra={
                        'alert_type': 'high_failure_rate',
                        'failure_rate': failure_rate,
                        'failed_orders': failed_orders,
                        'total_orders': total_orders
                    }
                )
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to collect order metrics: {str(e)}", exc_info=True)
            return {}
    
    @staticmethod
    def collect_subscription_metrics(db: Session) -> Dict[str, Any]:
        """
        Collect subscription-related metrics.
        
        Args:
            db: Database session
            
        Returns:
            Dictionary containing subscription metrics
        """
        try:
            # Active subscriptions
            active_subscriptions = db.query(func.count(Subscription.id)).filter(
                Subscription.status == SubscriptionStatus.ACTIVE
            ).scalar() or 0
            
            # Paused subscriptions
            paused_subscriptions = db.query(func.count(Subscription.id)).filter(
                Subscription.status == SubscriptionStatus.PAUSED
            ).scalar() or 0
            
            # Cancelled subscriptions (last 24 hours)
            cutoff_time = datetime.utcnow() - timedelta(hours=24)
            recent_cancellations = db.query(func.count(Subscription.id)).filter(
                and_(
                    Subscription.status == SubscriptionStatus.CANCELLED,
                    Subscription.updated_at >= cutoff_time
                )
            ).scalar() or 0
            
            metrics = {
                'active_subscriptions': active_subscriptions,
                'paused_subscriptions': paused_subscriptions,
                'recent_cancellations_24h': recent_cancellations,
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }
            
            logger.info("Subscription metrics collected", extra=metrics)
            
            # Alert if many recent cancellations
            if recent_cancellations > 10:
                logger.warning(
                    f"High subscription cancellation rate: {recent_cancellations} in last 24h",
                    extra={
                        'alert_type': 'high_cancellation_rate',
                        'cancellations': recent_cancellations
                    }
                )
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to collect subscription metrics: {str(e)}", exc_info=True)
            return {}
    
    @staticmethod
    def collect_inventory_metrics(db: Session, low_stock_threshold: int = 10) -> Dict[str, Any]:
        """
        Collect inventory-related metrics.
        
        Args:
            db: Database session
            low_stock_threshold: Threshold for low stock alerts
            
        Returns:
            Dictionary containing inventory metrics
        """
        try:
            # Total products
            total_products = db.query(func.count(Product.id)).filter(
                Product.is_active == True
            ).scalar() or 0
            
            # Low stock products
            low_stock_products = db.query(func.count(Product.id)).filter(
                and_(
                    Product.is_active == True,
                    Product.stock_quantity <= low_stock_threshold,
                    Product.stock_quantity > 0
                )
            ).scalar() or 0
            
            # Out of stock products
            out_of_stock_products = db.query(func.count(Product.id)).filter(
                and_(
                    Product.is_active == True,
                    Product.stock_quantity == 0
                )
            ).scalar() or 0
            
            # Get list of low stock product SKUs for alerting
            low_stock_skus = []
            if low_stock_products > 0:
                low_stock_items = db.query(Product.sku, Product.title, Product.stock_quantity).filter(
                    and_(
                        Product.is_active == True,
                        Product.stock_quantity <= low_stock_threshold,
                        Product.stock_quantity > 0
                    )
                ).limit(10).all()
                
                low_stock_skus = [
                    {
                        'sku': item.sku,
                        'title': item.title,
                        'stock': item.stock_quantity
                    }
                    for item in low_stock_items
                ]
            
            metrics = {
                'total_products': total_products,
                'low_stock_products': low_stock_products,
                'out_of_stock_products': out_of_stock_products,
                'low_stock_threshold': low_stock_threshold,
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }
            
            logger.info("Inventory metrics collected", extra=metrics)
            
            # Alert if many products are low on stock
            if low_stock_products > 5:
                logger.warning(
                    f"Multiple products low on stock: {low_stock_products} products",
                    extra={
                        'alert_type': 'low_stock_alert',
                        'low_stock_count': low_stock_products,
                        'low_stock_items': low_stock_skus
                    }
                )
            
            # Alert if products are out of stock
            if out_of_stock_products > 0:
                logger.warning(
                    f"Products out of stock: {out_of_stock_products} products",
                    extra={
                        'alert_type': 'out_of_stock_alert',
                        'out_of_stock_count': out_of_stock_products
                    }
                )
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to collect inventory metrics: {str(e)}", exc_info=True)
            return {}
    
    @staticmethod
    def collect_all_metrics(db: Session) -> Dict[str, Any]:
        """
        Collect all business metrics.
        
        Args:
            db: Database session
            
        Returns:
            Dictionary containing all metrics
        """
        return {
            'orders': MetricsCollector.collect_order_metrics(db),
            'subscriptions': MetricsCollector.collect_subscription_metrics(db),
            'inventory': MetricsCollector.collect_inventory_metrics(db)
        }


class PerformanceMonitor:
    """Monitor API performance and response times"""
    
    # Thresholds for alerting (in seconds)
    SLOW_RESPONSE_THRESHOLD = 2.0
    VERY_SLOW_RESPONSE_THRESHOLD = 5.0
    
    @staticmethod
    def check_response_time(endpoint: str, duration: float, method: str = "GET"):
        """
        Check if response time exceeds thresholds and log/alert accordingly.
        
        Args:
            endpoint: API endpoint path
            duration: Response time in seconds
            method: HTTP method
        """
        if duration > PerformanceMonitor.VERY_SLOW_RESPONSE_THRESHOLD:
            logger.error(
                f"Very slow response: {method} {endpoint} took {duration:.3f}s",
                extra={
                    'alert_type': 'very_slow_response',
                    'endpoint': endpoint,
                    'method': method,
                    'duration': duration,
                    'threshold': PerformanceMonitor.VERY_SLOW_RESPONSE_THRESHOLD
                }
            )
        elif duration > PerformanceMonitor.SLOW_RESPONSE_THRESHOLD:
            logger.warning(
                f"Slow response: {method} {endpoint} took {duration:.3f}s",
                extra={
                    'alert_type': 'slow_response',
                    'endpoint': endpoint,
                    'method': method,
                    'duration': duration,
                    'threshold': PerformanceMonitor.SLOW_RESPONSE_THRESHOLD
                }
            )


class ExternalServiceMonitor:
    """Monitor external service health and failures"""
    
    @staticmethod
    def log_external_service_failure(
        service_name: str,
        operation: str,
        error: str,
        retry_count: int = 0
    ):
        """
        Log external service failures for monitoring and alerting.
        
        Args:
            service_name: Name of the external service (e.g., 'razorpay', 'twilio')
            operation: Operation that failed (e.g., 'create_order', 'send_sms')
            error: Error message
            retry_count: Number of retries attempted
        """
        logger.error(
            f"External service failure: {service_name}.{operation}",
            extra={
                'alert_type': 'external_service_failure',
                'service': service_name,
                'operation': operation,
                'error': error,
                'retry_count': retry_count
            }
        )
    
    @staticmethod
    def log_external_service_success(
        service_name: str,
        operation: str,
        duration: float,
        retry_count: int = 0
    ):
        """
        Log successful external service calls for monitoring.
        
        Args:
            service_name: Name of the external service
            operation: Operation that succeeded
            duration: Time taken in seconds
            retry_count: Number of retries before success
        """
        logger.info(
            f"External service success: {service_name}.{operation}",
            extra={
                'service': service_name,
                'operation': operation,
                'duration': duration,
                'retry_count': retry_count
            }
        )


def setup_sentry_custom_metrics():
    """
    Set up custom metrics and tags for Sentry monitoring.
    This should be called during application startup.
    """
    try:
        import sentry_sdk
        
        # Set custom tags
        sentry_sdk.set_tag("application", "indostar-naturals")
        sentry_sdk.set_tag("component", "backend-api")
        
        logger.info("Sentry custom metrics configured")
        
    except ImportError:
        logger.warning("Sentry SDK not available for custom metrics")
    except Exception as e:
        logger.error(f"Failed to setup Sentry custom metrics: {str(e)}")
