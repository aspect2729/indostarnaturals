"""Webhook API Endpoints

Handles Razorpay webhook events for payment and subscription processing.
"""
import json
import logging
from typing import Dict, Any
from fastapi import APIRouter, Request, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.services.payment_service import payment_service
from app.models.order import Order
from app.models.subscription import Subscription
from app.models.audit_log import AuditLog
from app.models.enums import PaymentStatus, OrderStatus

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/webhooks",
    tags=["webhooks"]
)


# Store processed webhook IDs to prevent duplicate processing (idempotency)
processed_webhooks = set()


@router.post("/razorpay")
async def razorpay_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Handle Razorpay webhook events.
    
    Processes the following events:
    - payment.captured: Payment successful
    - payment.failed: Payment failed
    - subscription.charged: Subscription payment successful
    - subscription.cancelled: Subscription cancelled
    
    Implements idempotency to prevent duplicate processing.
    Verifies webhook signature before processing.
    Logs all webhook events.
    """
    # Get raw body for signature verification
    body = await request.body()
    body_str = body.decode('utf-8')
    
    # Get signature from headers
    signature = request.headers.get('X-Razorpay-Signature')
    
    if not signature:
        logger.warning("Webhook received without signature")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing webhook signature"
        )
    
    # Verify webhook signature
    is_valid = payment_service.verify_webhook_signature(body_str, signature)
    
    if not is_valid:
        logger.warning("Invalid webhook signature")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid webhook signature"
        )
    
    # Parse webhook payload
    try:
        payload = json.loads(body_str)
    except json.JSONDecodeError:
        logger.error("Invalid JSON in webhook payload")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JSON payload"
        )
    
    event = payload.get('event')
    webhook_id = payload.get('id')
    
    # Implement idempotency - check if webhook already processed
    if webhook_id in processed_webhooks:
        logger.info(f"Webhook {webhook_id} already processed, skipping")
        return {"status": "already_processed"}
    
    # Log webhook event
    logger.info(f"Processing webhook: {event} (ID: {webhook_id})")
    
    try:
        # Handle different event types
        if event == "payment.captured":
            await handle_payment_captured(db, payload)
        elif event == "payment.failed":
            await handle_payment_failed(db, payload)
        elif event == "subscription.charged":
            await handle_subscription_charged(db, payload)
        elif event == "subscription.cancelled":
            await handle_subscription_cancelled(db, payload)
        else:
            logger.info(f"Unhandled webhook event: {event}")
        
        # Mark webhook as processed
        processed_webhooks.add(webhook_id)
        
        # Log to audit log
        audit_log = AuditLog(
            actor_id=None,  # System action
            action_type="WEBHOOK_PROCESSED",
            object_type="WEBHOOK",
            object_id=0,
            details={
                "event": event,
                "webhook_id": webhook_id
            }
        )
        db.add(audit_log)
        await db.commit()
        
        return {"status": "success", "event": event}
        
    except Exception as e:
        logger.error(f"Error processing webhook {webhook_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing webhook"
        )


async def handle_payment_captured(db: AsyncSession, payload: Dict[str, Any]):
    """
    Handle payment.captured event.
    
    Updates order status to confirmed and creates payment record.
    """
    payment_entity = payload.get('payload', {}).get('payment', {}).get('entity', {})
    
    razorpay_payment_id = payment_entity.get('id')
    razorpay_order_id = payment_entity.get('order_id')
    
    if not razorpay_payment_id or not razorpay_order_id:
        logger.error("Missing payment or order ID in webhook payload")
        return
    
    # Extract order ID from notes
    notes = payment_entity.get('notes', {})
    order_id = notes.get('order_id')
    
    if not order_id:
        logger.error(f"Order ID not found in payment notes for {razorpay_payment_id}")
        return
    
    try:
        order_id = int(order_id)
    except (ValueError, TypeError):
        logger.error(f"Invalid order ID in payment notes: {order_id}")
        return
    
    # Handle payment success
    try:
        payment = await payment_service.handle_payment_success(
            db=db,
            razorpay_payment_id=razorpay_payment_id,
            razorpay_order_id=razorpay_order_id,
            order_id=order_id
        )
        
        logger.info(f"Payment captured for order {order_id}: {razorpay_payment_id}")
        
        # Log payment success to audit log
        audit_log = AuditLog(
            actor_id=None,  # System action
            action_type="PAYMENT_SUCCESS",
            object_type="PAYMENT",
            object_id=payment.id,
            details={
                "razorpay_payment_id": razorpay_payment_id,
                "razorpay_order_id": razorpay_order_id,
                "order_id": order_id,
                "amount": str(payment.amount)
            }
        )
        db.add(audit_log)
        await db.commit()
        
    except Exception as e:
        logger.error(f"Error handling payment success for order {order_id}: {str(e)}")
        raise


async def handle_payment_failed(db: AsyncSession, payload: Dict[str, Any]):
    """
    Handle payment.failed event.
    
    Updates order payment status to failed.
    """
    payment_entity = payload.get('payload', {}).get('payment', {}).get('entity', {})
    
    razorpay_payment_id = payment_entity.get('id')
    razorpay_order_id = payment_entity.get('order_id')
    error_description = payment_entity.get('error_description')
    
    if not razorpay_payment_id or not razorpay_order_id:
        logger.error("Missing payment or order ID in webhook payload")
        return
    
    # Extract order ID from notes
    notes = payment_entity.get('notes', {})
    order_id = notes.get('order_id')
    
    if not order_id:
        logger.error(f"Order ID not found in payment notes for {razorpay_payment_id}")
        return
    
    try:
        order_id = int(order_id)
    except (ValueError, TypeError):
        logger.error(f"Invalid order ID in payment notes: {order_id}")
        return
    
    # Handle payment failure
    try:
        payment = await payment_service.handle_payment_failure(
            db=db,
            razorpay_payment_id=razorpay_payment_id,
            razorpay_order_id=razorpay_order_id,
            order_id=order_id,
            error_description=error_description
        )
        
        logger.info(f"Payment failed for order {order_id}: {razorpay_payment_id}")
        
        # Log payment failure to audit log
        audit_log = AuditLog(
            actor_id=None,  # System action
            action_type="PAYMENT_FAILED",
            object_type="PAYMENT",
            object_id=payment.id,
            details={
                "razorpay_payment_id": razorpay_payment_id,
                "razorpay_order_id": razorpay_order_id,
                "order_id": order_id,
                "amount": str(payment.amount),
                "error_description": error_description
            }
        )
        db.add(audit_log)
        await db.commit()
        
    except Exception as e:
        logger.error(f"Error handling payment failure for order {order_id}: {str(e)}")
        raise


async def handle_subscription_charged(db: AsyncSession, payload: Dict[str, Any]):
    """
    Handle subscription.charged event.
    
    Creates payment record for subscription charge.
    """
    subscription_entity = payload.get('payload', {}).get('subscription', {}).get('entity', {})
    payment_entity = payload.get('payload', {}).get('payment', {}).get('entity', {})
    
    razorpay_subscription_id = subscription_entity.get('id')
    razorpay_payment_id = payment_entity.get('id')
    amount_paise = payment_entity.get('amount', 0)
    
    if not razorpay_subscription_id or not razorpay_payment_id:
        logger.error("Missing subscription or payment ID in webhook payload")
        return
    
    # Convert amount from paise to rupees
    from decimal import Decimal
    amount = Decimal(amount_paise) / 100
    
    # Handle subscription charge
    try:
        payment = await payment_service.handle_subscription_charged(
            db=db,
            razorpay_subscription_id=razorpay_subscription_id,
            razorpay_payment_id=razorpay_payment_id,
            amount=amount
        )
        
        logger.info(f"Subscription charged: {razorpay_subscription_id}, payment: {razorpay_payment_id}")
        
        # Log subscription charge to audit log
        audit_log = AuditLog(
            actor_id=None,  # System action
            action_type="SUBSCRIPTION_CHARGED",
            object_type="PAYMENT",
            object_id=payment.id,
            details={
                "razorpay_subscription_id": razorpay_subscription_id,
                "razorpay_payment_id": razorpay_payment_id,
                "subscription_id": payment.subscription_id,
                "amount": str(payment.amount)
            }
        )
        db.add(audit_log)
        await db.commit()
        
    except Exception as e:
        logger.error(f"Error handling subscription charge for {razorpay_subscription_id}: {str(e)}")
        raise


async def handle_subscription_cancelled(db: AsyncSession, payload: Dict[str, Any]):
    """
    Handle subscription.cancelled event.
    
    Updates subscription status to cancelled.
    """
    subscription_entity = payload.get('payload', {}).get('subscription', {}).get('entity', {})
    
    razorpay_subscription_id = subscription_entity.get('id')
    
    if not razorpay_subscription_id:
        logger.error("Missing subscription ID in webhook payload")
        return
    
    # Get subscription from database
    result = await db.execute(
        select(Subscription).where(Subscription.razorpay_subscription_id == razorpay_subscription_id)
    )
    subscription = result.scalar_one_or_none()
    
    if not subscription:
        logger.error(f"Subscription not found: {razorpay_subscription_id}")
        return
    
    # Update subscription status
    from app.models.enums import SubscriptionStatus
    subscription.status = SubscriptionStatus.CANCELLED
    
    await db.commit()
    
    logger.info(f"Subscription cancelled: {razorpay_subscription_id}")
    
    # Log subscription cancellation to audit log
    audit_log = AuditLog(
        actor_id=None,  # System action
        action_type="SUBSCRIPTION_CANCELLED",
        object_type="SUBSCRIPTION",
        object_id=subscription.id,
        details={
            "razorpay_subscription_id": razorpay_subscription_id,
            "user_id": subscription.user_id
        }
    )
    db.add(audit_log)
    await db.commit()
