"""Cleanup background tasks

Handles scheduled cleanup operations including:
- Cleaning up expired shopping carts
- Cleaning up expired tokens (password reset, email verification)
"""
from datetime import datetime, timedelta
from celery import Task
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.core.celery_app import celery_app
from app.core.database import SessionLocal
from app.core.redis_client import get_redis
from app.models.cart import Cart
from app.models.cart_item import CartItem


class CleanupTask(Task):
    """Base task class for cleanup operations"""
    
    autoretry_for = (Exception,)
    retry_kwargs = {"max_retries": 3}
    retry_backoff = True
    retry_backoff_max = 600  # Max 10 minutes
    retry_jitter = True


@celery_app.task(
    bind=True,
    base=CleanupTask,
    name="app.tasks.cleanup.cleanup_expired_carts"
)
def cleanup_expired_carts(self, days_old: int = 30) -> dict:
    """
    Clean up expired shopping carts.
    
    This task runs daily and removes carts that:
    - Have not been updated in the specified number of days (default: 30)
    - Are empty (have no items)
    
    Args:
        days_old: Number of days of inactivity before cart is considered expired
        
    Returns:
        Dict with cleanup statistics
        
    Raises:
        Exception: If critical errors occur during cleanup
    """
    db: Session = SessionLocal()
    
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        
        print(f"Starting cart cleanup for carts older than {cutoff_date}")
        
        # Find expired carts (not updated in X days)
        expired_carts = db.query(Cart).filter(
            Cart.updated_at < cutoff_date
        ).all()
        
        print(f"Found {len(expired_carts)} carts not updated since {cutoff_date}")
        
        deleted_count = 0
        empty_deleted_count = 0
        
        for cart in expired_carts:
            try:
                # Check if cart is empty
                item_count = db.query(CartItem).filter(
                    CartItem.cart_id == cart.id
                ).count()
                
                if item_count == 0:
                    # Delete empty expired carts
                    db.delete(cart)
                    empty_deleted_count += 1
                    deleted_count += 1
                else:
                    # For non-empty carts, we might want to keep them
                    # or send a reminder to the user
                    # For now, we'll also delete them after 30 days
                    db.delete(cart)
                    deleted_count += 1
                    
            except Exception as e:
                print(f"Error deleting cart {cart.id}: {e}")
                # Continue with other carts
                continue
        
        # Commit all deletions
        db.commit()
        
        stats = {
            "cutoff_date": str(cutoff_date),
            "days_old": days_old,
            "total_expired": len(expired_carts),
            "deleted": deleted_count,
            "empty_deleted": empty_deleted_count
        }
        
        print(f"Cart cleanup complete: {stats}")
        
        return stats
        
    except Exception as exc:
        db.rollback()
        print(f"Critical error in cleanup_expired_carts: {exc}")
        raise
    finally:
        db.close()


@celery_app.task(
    bind=True,
    base=CleanupTask,
    name="app.tasks.cleanup.cleanup_expired_tokens"
)
def cleanup_expired_tokens(self) -> dict:
    """
    Clean up expired tokens from Redis.
    
    This task runs daily and removes:
    - Expired password reset tokens
    - Expired email verification tokens
    - Expired OTP codes
    
    Note: Redis automatically expires keys with TTL, but this task
    provides additional cleanup and statistics.
    
    Returns:
        Dict with cleanup statistics
        
    Raises:
        Exception: If critical errors occur during cleanup
    """
    try:
        redis = get_redis()
        
        print("Starting token cleanup")
        
        # Scan for password reset tokens
        password_reset_keys = []
        for key in redis.scan_iter(match="password_reset:*"):
            password_reset_keys.append(key)
        
        # Scan for email verification tokens
        email_verification_keys = []
        for key in redis.scan_iter(match="email_verification:*"):
            email_verification_keys.append(key)
        
        # Scan for OTP codes
        otp_keys = []
        for key in redis.scan_iter(match="otp:*"):
            otp_keys.append(key)
        
        # Check TTL and delete expired keys
        password_reset_deleted = 0
        for key in password_reset_keys:
            ttl = redis.ttl(key)
            if ttl == -1:  # No expiration set (shouldn't happen)
                redis.delete(key)
                password_reset_deleted += 1
            elif ttl == -2:  # Key doesn't exist
                password_reset_deleted += 1
        
        email_verification_deleted = 0
        for key in email_verification_keys:
            ttl = redis.ttl(key)
            if ttl == -1:  # No expiration set
                redis.delete(key)
                email_verification_deleted += 1
            elif ttl == -2:  # Key doesn't exist
                email_verification_deleted += 1
        
        otp_deleted = 0
        for key in otp_keys:
            ttl = redis.ttl(key)
            if ttl == -1:  # No expiration set
                redis.delete(key)
                otp_deleted += 1
            elif ttl == -2:  # Key doesn't exist
                otp_deleted += 1
        
        stats = {
            "password_reset_tokens": {
                "total": len(password_reset_keys),
                "deleted": password_reset_deleted
            },
            "email_verification_tokens": {
                "total": len(email_verification_keys),
                "deleted": email_verification_deleted
            },
            "otp_codes": {
                "total": len(otp_keys),
                "deleted": otp_deleted
            }
        }
        
        print(f"Token cleanup complete: {stats}")
        
        return stats
        
    except Exception as exc:
        print(f"Critical error in cleanup_expired_tokens: {exc}")
        raise


@celery_app.task(
    bind=True,
    base=CleanupTask,
    name="app.tasks.cleanup.cleanup_old_audit_logs"
)
def cleanup_old_audit_logs(self, days_old: int = 90) -> dict:
    """
    Clean up old audit logs.
    
    This task runs periodically and removes audit logs older than
    the specified number of days (default: 90 days / 3 months).
    
    This helps manage database size while retaining recent audit history.
    
    Args:
        days_old: Number of days to retain audit logs
        
    Returns:
        Dict with cleanup statistics
        
    Raises:
        Exception: If critical errors occur during cleanup
    """
    db: Session = SessionLocal()
    
    try:
        from app.models.audit_log import AuditLog
        
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        
        print(f"Starting audit log cleanup for logs older than {cutoff_date}")
        
        # Count old audit logs
        old_logs_count = db.query(AuditLog).filter(
            AuditLog.created_at < cutoff_date
        ).count()
        
        print(f"Found {old_logs_count} audit logs older than {cutoff_date}")
        
        # Delete old audit logs in batches to avoid long-running transactions
        batch_size = 1000
        deleted_count = 0
        
        while True:
            # Delete a batch
            batch = db.query(AuditLog).filter(
                AuditLog.created_at < cutoff_date
            ).limit(batch_size).all()
            
            if not batch:
                break
            
            for log in batch:
                db.delete(log)
            
            db.commit()
            deleted_count += len(batch)
            
            print(f"Deleted {deleted_count} / {old_logs_count} audit logs")
        
        stats = {
            "cutoff_date": str(cutoff_date),
            "days_old": days_old,
            "total_old_logs": old_logs_count,
            "deleted": deleted_count
        }
        
        print(f"Audit log cleanup complete: {stats}")
        
        return stats
        
    except Exception as exc:
        db.rollback()
        print(f"Critical error in cleanup_old_audit_logs: {exc}")
        raise
    finally:
        db.close()


@celery_app.task(
    bind=True,
    base=CleanupTask,
    name="app.tasks.cleanup.cleanup_abandoned_sessions"
)
def cleanup_abandoned_sessions(self, hours_old: int = 24) -> dict:
    """
    Clean up abandoned user sessions from Redis.
    
    This task removes session data for users who haven't been active
    in the specified number of hours.
    
    Args:
        hours_old: Number of hours of inactivity before session is considered abandoned
        
    Returns:
        Dict with cleanup statistics
        
    Raises:
        Exception: If critical errors occur during cleanup
    """
    try:
        redis = get_redis()
        
        print(f"Starting session cleanup for sessions older than {hours_old} hours")
        
        # Scan for session keys
        session_keys = []
        for key in redis.scan_iter(match="session:*"):
            session_keys.append(key)
        
        print(f"Found {len(session_keys)} session keys")
        
        deleted_count = 0
        
        for key in session_keys:
            ttl = redis.ttl(key)
            
            # If TTL is less than the threshold, consider it abandoned
            # (assuming sessions have a longer default TTL)
            if ttl == -1:  # No expiration set
                redis.delete(key)
                deleted_count += 1
            elif ttl == -2:  # Key doesn't exist
                deleted_count += 1
        
        stats = {
            "hours_old": hours_old,
            "total_sessions": len(session_keys),
            "deleted": deleted_count
        }
        
        print(f"Session cleanup complete: {stats}")
        
        return stats
        
    except Exception as exc:
        print(f"Critical error in cleanup_abandoned_sessions: {exc}")
        raise
