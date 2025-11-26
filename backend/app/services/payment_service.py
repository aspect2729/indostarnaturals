"""Payment Service

Handles Razorpay payment and subscription operations, webhook signature verification,
and payment status updates.
"""
from decimal import Decimal
from typing import Dict, Any
import hmac
import hashlib
import razorpay
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.config import settings
from app.models.payment import Payment
from app.models.order import Order
from app.models.subscription import Subscription
from app.models.user import User
from app.models.enums import PaymentStatus, OrderStatus
from app.services.notification_service import notification_service


class PaymentService:
    """Service for Razorpay payment operations"""
    
    def __init__(self):
        """Initialize Razorpay client with API credentials"""
        self.client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    
    async def create_razorpay_order(
        self,
        db: AsyncSession,
        order_id: int,
        amount: Decimal
    ) -> Dict[str, Any]:
        """
        Create a Razorpay order for payment processing.
        
        Args:
            db: Database session
            order_id: Internal order ID
            amount: Order amount in rupees
            
        Returns:
            Dictionary containing Razorpay order details including order_id and amount
        """
        # Convert amount to paise (Razorpay uses smallest currency unit)
        amount_paise = int(amount * 100)
        
        # Create Razorpay order
        razorpay_order = self.client.order.create({
            "amount": amount_paise,
            "currency": "INR",
            "receipt": f"order_{order_id}",
            "notes": {
                "order_id": str(order_id)
            }
        })
        
        return {
            "razorpay_order_id": razorpay_order["id"],
            "amount": razorpay_order["amount"],
            "currency": razorpay_order["currency"],
            "key_id": settings.RAZORPAY_KEY_ID
        }
    
    async def create_razorpay_subscription(
        self,
        db: AsyncSession,
        subscription_id: int,
        plan_id: str
    ) -> Dict[str, Any]:
        """
        Create a Razorpay subscription for recurring billing.
        
        Args:
            db: Database session
            subscription_id: Internal subscription ID
            plan_id: Razorpay plan ID for the subscription
            
        Returns:
            Dictionary containing Razorpay subscription details
        """
        # Create Razorpay subscription
        razorpay_subscription = self.client.subscription.create({
            "plan_id": plan_id,
            "customer_notify": 1,
            "total_count": 0,  # Unlimited billing cycles
            "notes": {
                "subscription_id": str(subscription_id)
            }
        })
        
        return {
            "razorpay_subscription_id": razorpay_subscription["id"],
            "status": razorpay_subscription["status"],
            "plan_id": razorpay_subscription["plan_id"]
        }
    
    def verify_payment_signature(
        self,
        razorpay_order_id: str,
        razorpay_payment_id: str,
        razorpay_signature: str
    ) -> bool:
        """
        Verify Razorpay payment signature for security.
        
        Args:
            razorpay_order_id: Razorpay order ID
            razorpay_payment_id: Razorpay payment ID
            razorpay_signature: Signature to verify
            
        Returns:
            True if signature is valid, False otherwise
        """
        try:
            # Create message to verify
            message = f"{razorpay_order_id}|{razorpay_payment_id}"
            
            # Generate expected signature
            expected_signature = hmac.new(
                settings.RAZORPAY_KEY_SECRET.encode('utf-8'),
                message.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            # Compare signatures
            return hmac.compare_digest(expected_signature, razorpay_signature)
        except Exception:
            return False
    
    def verify_webhook_signature(
        self,
        payload: str,
        signature: str
    ) -> bool:
        """
        Verify Razorpay webhook signature for security.
        
        Args:
            payload: Raw webhook payload string
            signature: X-Razorpay-Signature header value
            
        Returns:
            True if signature is valid, False otherwise
        """
        try:
            # Generate expected signature
            expected_signature = hmac.new(
                settings.RAZORPAY_WEBHOOK_SECRET.encode('utf-8'),
                payload.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            # Compare signatures
            return hmac.compare_digest(expected_signature, signature)
        except Exception:
            return False
    
    async def handle_payment_success(
        self,
        db: AsyncSession,
        razorpay_payment_id: str,
        razorpay_order_id: str,
        order_id: int
    ) -> Payment:
        """
        Handle successful payment by creating payment record and updating order status.
        
        Args:
            db: Database session
            razorpay_payment_id: Razorpay payment ID
            razorpay_order_id: Razorpay order ID
            order_id: Internal order ID
            
        Returns:
            Created Payment object
        """
        # Get order
        result = await db.execute(select(Order).where(Order.id == order_id))
        order = result.scalar_one_or_none()
        
        if not order:
            raise ValueError(f"Order {order_id} not found")
        
        # Create payment record
        payment = Payment(
            order_id=order_id,
            razorpay_payment_id=razorpay_payment_id,
            razorpay_order_id=razorpay_order_id,
            amount=order.final_amount,
            currency="INR",
            status=PaymentStatus.PAID
        )
        db.add(payment)
        
        # Update order status
        order.payment_status = PaymentStatus.PAID
        order.order_status = OrderStatus.CONFIRMED
        
        await db.commit()
        await db.refresh(payment)
        
        return payment
    
    async def handle_payment_failure(
        self,
        db: AsyncSession,
        razorpay_payment_id: str,
        razorpay_order_id: str,
        order_id: int,
        error_description: str | None = None
    ) -> Payment:
        """
        Handle failed payment by creating payment record and updating order status.
        
        Args:
            db: Database session
            razorpay_payment_id: Razorpay payment ID
            razorpay_order_id: Razorpay order ID
            order_id: Internal order ID
            error_description: Optional error description
            
        Returns:
            Created Payment object
        """
        # Get order
        result = await db.execute(select(Order).where(Order.id == order_id))
        order = result.scalar_one_or_none()
        
        if not order:
            raise ValueError(f"Order {order_id} not found")
        
        # Create payment record
        payment = Payment(
            order_id=order_id,
            razorpay_payment_id=razorpay_payment_id,
            razorpay_order_id=razorpay_order_id,
            amount=order.final_amount,
            currency="INR",
            status=PaymentStatus.FAILED
        )
        db.add(payment)
        
        # Update order status
        order.payment_status = PaymentStatus.FAILED
        # Keep order status as PENDING so user can retry
        
        await db.commit()
        await db.refresh(payment)
        
        # Send payment failure notification (non-blocking)
        try:
            user_result = await db.execute(select(User).where(User.id == order.user_id))
            user = user_result.scalar_one_or_none()
            
            if user and user.email:
                notification_service.send_payment_failed(
                    email=user.email,
                    order_number=order.order_number,
                    customer_name=user.name,
                    order_total=str(order.final_amount),
                    failure_reason=error_description or "Payment processing failed"
                )
        except Exception as e:
            # Log error but don't fail the payment processing
            print(f"Failed to send payment failure notification: {e}")
        
        return payment
    
    async def handle_subscription_charged(
        self,
        db: AsyncSession,
        razorpay_subscription_id: str,
        razorpay_payment_id: str,
        amount: Decimal
    ) -> Payment:
        """
        Handle successful subscription charge by creating payment record.
        
        Args:
            db: Database session
            razorpay_subscription_id: Razorpay subscription ID
            razorpay_payment_id: Razorpay payment ID
            amount: Charged amount in rupees
            
        Returns:
            Created Payment object
        """
        # Get subscription
        result = await db.execute(
            select(Subscription).where(Subscription.razorpay_subscription_id == razorpay_subscription_id)
        )
        subscription = result.scalar_one_or_none()
        
        if not subscription:
            raise ValueError(f"Subscription with Razorpay ID {razorpay_subscription_id} not found")
        
        # Create payment record
        payment = Payment(
            subscription_id=subscription.id,
            razorpay_payment_id=razorpay_payment_id,
            amount=amount,
            currency="INR",
            status=PaymentStatus.PAID
        )
        db.add(payment)
        
        await db.commit()
        await db.refresh(payment)
        
        return payment


# Create singleton instance
payment_service = PaymentService()
