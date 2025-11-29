"""Subscription Service

Handles subscription creation, management, and recurring billing integration with Razorpay.
"""
from typing import List, Dict, Any
from decimal import Decimal
from datetime import date, timedelta
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, select
from app.models.subscription import Subscription
from app.models.product import Product
from app.models.user import User
from app.models.address import Address
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.enums import (
    SubscriptionFrequency,
    SubscriptionStatus,
    UserRole,
    OrderStatus,
    PaymentStatus
)
from app.core.config import settings
import razorpay


class SubscriptionService:
    """Service for subscription management operations"""
    
    def __init__(self):
        """Initialize Razorpay client with API credentials"""
        # Check if Razorpay is configured (not using placeholder values)
        self.razorpay_enabled = (
            settings.RAZORPAY_KEY_ID and 
            settings.RAZORPAY_KEY_SECRET and
            not settings.RAZORPAY_KEY_ID.startswith('your-') and
            not settings.RAZORPAY_KEY_SECRET.startswith('your-')
        )
        
        if self.razorpay_enabled:
            self.client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        else:
            self.client = None
    
    def create_subscription(
        self,
        user_id: int,
        product_id: int,
        plan_frequency: SubscriptionFrequency,
        start_date: date,
        delivery_address_id: int,
        db: Session
    ) -> Subscription:
        """
        Create a subscription with Razorpay integration.
        
        This function:
        1. Validates the product is subscription-available
        2. Validates the delivery address belongs to the user
        3. Creates a Razorpay subscription
        4. Creates the subscription record in the database
        
        Args:
            user_id: User ID
            product_id: Product ID
            plan_frequency: Subscription frequency (daily, alternate_days, weekly)
            start_date: Subscription start date
            delivery_address_id: Delivery address ID
            db: Database session
            
        Returns:
            Created Subscription object
            
        Raises:
            ValueError: If validation fails
        """
        # Get user
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError(f"User with ID {user_id} does not exist")
        
        # Get product and validate it's subscription-available
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise ValueError(f"Product with ID {product_id} does not exist")
        
        if not product.is_subscription_available:
            raise ValueError(f"Product '{product.title}' is not available for subscription")
        
        if not product.is_active:
            raise ValueError(f"Product '{product.title}' is not active")
        
        # Verify address belongs to user
        address = db.query(Address).filter(
            and_(
                Address.id == delivery_address_id,
                Address.user_id == user_id
            )
        ).first()
        
        if not address:
            raise ValueError(f"Address with ID {delivery_address_id} not found or does not belong to user")
        
        # Determine price based on user role
        if user.role == UserRole.DISTRIBUTOR:
            price = product.distributor_price
        else:
            price = product.consumer_price
        
        # Create Razorpay subscription if enabled, otherwise use mock ID
        if self.razorpay_enabled:
            # Create Razorpay plan based on frequency
            plan_period = self._get_plan_period(plan_frequency)
            plan_interval = self._get_plan_interval(plan_frequency)
            
            # Create Razorpay plan
            razorpay_plan = self.client.plan.create({
                "period": plan_period,
                "interval": plan_interval,
                "item": {
                    "name": f"{product.title} - {plan_frequency.value}",
                    "amount": int(price * 100),  # Convert to paise
                    "currency": "INR",
                    "description": f"Subscription for {product.title}"
                },
                "notes": {
                    "product_id": str(product_id),
                    "user_id": str(user_id)
                }
            })
            
            # Create Razorpay subscription
            # Convert start_date to Unix timestamp if it's in the future
            start_at_timestamp = None
            if start_date > date.today():
                from datetime import datetime
                start_datetime = datetime.combine(start_date, datetime.min.time())
                start_at_timestamp = int(start_datetime.timestamp())
            
            razorpay_subscription = self.client.subscription.create({
                "plan_id": razorpay_plan["id"],
                "customer_notify": 1,
                "total_count": 0,  # Unlimited billing cycles
                "start_at": start_at_timestamp,
                "notes": {
                    "product_id": str(product_id),
                    "user_id": str(user_id),
                    "address_id": str(delivery_address_id)
                }
            })
            razorpay_subscription_id = razorpay_subscription["id"]
        else:
            # Development mode: use mock subscription ID
            import uuid
            razorpay_subscription_id = f"sub_dev_{uuid.uuid4().hex[:16]}"
        
        # Calculate next delivery date
        next_delivery_date = self._calculate_next_delivery_date(start_date, plan_frequency)
        
        # Create subscription record
        subscription = Subscription(
            user_id=user_id,
            product_id=product_id,
            razorpay_subscription_id=razorpay_subscription_id,
            plan_frequency=plan_frequency,
            start_date=start_date,
            next_delivery_date=next_delivery_date,
            delivery_address_id=delivery_address_id,
            status=SubscriptionStatus.ACTIVE
        )
        
        db.add(subscription)
        db.commit()
        db.refresh(subscription)
        
        return subscription
    
    def get_user_subscriptions(
        self,
        user_id: int,
        db: Session
    ) -> List[Subscription]:
        """
        Get all subscriptions for a user.
        
        Args:
            user_id: User ID
            db: Database session
            
        Returns:
            List of Subscription objects with related product and address
        """
        subscriptions = db.query(Subscription).options(
            joinedload(Subscription.product),
            joinedload(Subscription.delivery_address)
        ).filter(Subscription.user_id == user_id).order_by(
            Subscription.created_at.desc()
        ).all()
        
        return subscriptions
    
    def pause_subscription(
        self,
        subscription_id: int,
        user_id: int,
        db: Session
    ) -> Subscription:
        """
        Pause a subscription with Razorpay API call.
        
        Args:
            subscription_id: Subscription ID
            user_id: User ID (for ownership validation)
            db: Database session
            
        Returns:
            Updated Subscription object
            
        Raises:
            ValueError: If subscription not found or doesn't belong to user
        """
        # Get subscription
        subscription = db.query(Subscription).filter(
            and_(
                Subscription.id == subscription_id,
                Subscription.user_id == user_id
            )
        ).first()
        
        if not subscription:
            raise ValueError(f"Subscription with ID {subscription_id} not found or does not belong to user")
        
        if subscription.status == SubscriptionStatus.CANCELLED:
            raise ValueError("Cannot pause a cancelled subscription")
        
        if subscription.status == SubscriptionStatus.PAUSED:
            raise ValueError("Subscription is already paused")
        
        # Pause Razorpay subscription if enabled
        if self.razorpay_enabled:
            try:
                self.client.subscription.pause(subscription.razorpay_subscription_id)
            except Exception as e:
                raise ValueError(f"Failed to pause subscription with Razorpay: {str(e)}")
        
        # Update subscription status
        subscription.status = SubscriptionStatus.PAUSED
        
        db.commit()
        db.refresh(subscription)
        
        return subscription
    
    def resume_subscription(
        self,
        subscription_id: int,
        user_id: int,
        db: Session
    ) -> Subscription:
        """
        Resume a paused subscription with Razorpay API call.
        
        Args:
            subscription_id: Subscription ID
            user_id: User ID (for ownership validation)
            db: Database session
            
        Returns:
            Updated Subscription object
            
        Raises:
            ValueError: If subscription not found or doesn't belong to user
        """
        # Get subscription
        subscription = db.query(Subscription).filter(
            and_(
                Subscription.id == subscription_id,
                Subscription.user_id == user_id
            )
        ).first()
        
        if not subscription:
            raise ValueError(f"Subscription with ID {subscription_id} not found or does not belong to user")
        
        if subscription.status == SubscriptionStatus.CANCELLED:
            raise ValueError("Cannot resume a cancelled subscription")
        
        if subscription.status == SubscriptionStatus.ACTIVE:
            raise ValueError("Subscription is already active")
        
        # Resume Razorpay subscription if enabled
        if self.razorpay_enabled:
            try:
                self.client.subscription.resume(subscription.razorpay_subscription_id)
            except Exception as e:
                raise ValueError(f"Failed to resume subscription with Razorpay: {str(e)}")
        
        # Update subscription status and recalculate next delivery date
        subscription.status = SubscriptionStatus.ACTIVE
        subscription.next_delivery_date = self._calculate_next_delivery_date(
            date.today(),
            subscription.plan_frequency
        )
        
        db.commit()
        db.refresh(subscription)
        
        return subscription
    
    def cancel_subscription(
        self,
        subscription_id: int,
        user_id: int,
        db: Session
    ) -> Subscription:
        """
        Cancel a subscription with Razorpay API call.
        
        Args:
            subscription_id: Subscription ID
            user_id: User ID (for ownership validation)
            db: Database session
            
        Returns:
            Updated Subscription object
            
        Raises:
            ValueError: If subscription not found or doesn't belong to user
        """
        # Get subscription
        subscription = db.query(Subscription).filter(
            and_(
                Subscription.id == subscription_id,
                Subscription.user_id == user_id
            )
        ).first()
        
        if not subscription:
            raise ValueError(f"Subscription with ID {subscription_id} not found or does not belong to user")
        
        if subscription.status == SubscriptionStatus.CANCELLED:
            raise ValueError("Subscription is already cancelled")
        
        # Cancel Razorpay subscription if enabled
        if self.razorpay_enabled:
            try:
                self.client.subscription.cancel(subscription.razorpay_subscription_id)
            except Exception as e:
                raise ValueError(f"Failed to cancel subscription with Razorpay: {str(e)}")
        
        # Update subscription status
        subscription.status = SubscriptionStatus.CANCELLED
        
        db.commit()
        db.refresh(subscription)
        
        return subscription
    
    def verify_subscription_payment(
        self,
        subscription_id: int,
        user_id: int,
        razorpay_payment_id: str,
        razorpay_subscription_id: str,
        razorpay_signature: str,
        db: Session
    ) -> Subscription:
        """
        Verify subscription payment signature from Razorpay.
        
        Args:
            subscription_id: Subscription ID
            user_id: User ID (for ownership validation)
            razorpay_payment_id: Razorpay payment ID
            razorpay_subscription_id: Razorpay subscription ID
            razorpay_signature: Razorpay signature for verification
            db: Database session
            
        Returns:
            Updated Subscription object
            
        Raises:
            ValueError: If verification fails or subscription not found
        """
        # Get subscription
        subscription = db.query(Subscription).filter(
            and_(
                Subscription.id == subscription_id,
                Subscription.user_id == user_id
            )
        ).first()
        
        if not subscription:
            raise ValueError(f"Subscription with ID {subscription_id} not found or does not belong to user")
        
        # Verify signature if Razorpay is enabled
        if self.razorpay_enabled:
            try:
                # Verify payment signature
                params_dict = {
                    'razorpay_payment_id': razorpay_payment_id,
                    'razorpay_subscription_id': razorpay_subscription_id,
                    'razorpay_signature': razorpay_signature
                }
                self.client.utility.verify_payment_signature(params_dict)
            except Exception as e:
                raise ValueError(f"Payment signature verification failed: {str(e)}")
        
        # Payment verified successfully - subscription is already active from creation
        # Just return the subscription
        db.refresh(subscription)
        return subscription
    
    def process_subscription_charge(
        self,
        razorpay_subscription_id: str,
        razorpay_payment_id: str,
        db: Session
    ) -> Order:
        """
        Process a subscription charge by creating an order.
        
        This function is called from the webhook handler when a subscription is charged.
        It creates an order for the subscription delivery.
        
        Args:
            razorpay_subscription_id: Razorpay subscription ID
            razorpay_payment_id: Razorpay payment ID
            db: Database session
            
        Returns:
            Created Order object
            
        Raises:
            ValueError: If subscription not found
        """
        # Get subscription with related data
        subscription = db.query(Subscription).options(
            joinedload(Subscription.product),
            joinedload(Subscription.user),
            joinedload(Subscription.delivery_address)
        ).filter(
            Subscription.razorpay_subscription_id == razorpay_subscription_id
        ).first()
        
        if not subscription:
            raise ValueError(f"Subscription with Razorpay ID {razorpay_subscription_id} not found")
        
        # Check if subscription is active
        if subscription.status != SubscriptionStatus.ACTIVE:
            raise ValueError(f"Subscription {subscription.id} is not active")
        
        # Get product and user
        product = subscription.product
        user = subscription.user
        
        # Determine price based on user role
        if user.role == UserRole.DISTRIBUTOR:
            unit_price = product.distributor_price
        else:
            unit_price = product.consumer_price
        
        # Check stock availability
        if product.stock_quantity < 1:
            raise ValueError(f"Insufficient stock for product '{product.title}'")
        
        # Generate unique order number
        from datetime import datetime
        order_number = f"SUB-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{subscription.id}"
        
        # Create order
        order = Order(
            user_id=subscription.user_id,
            order_number=order_number,
            total_amount=unit_price,
            discount_amount=Decimal('0.00'),
            final_amount=unit_price,
            payment_status=PaymentStatus.PAID,  # Already paid via subscription
            order_status=OrderStatus.CONFIRMED,
            delivery_address_id=subscription.delivery_address_id,
            notes=f"Subscription order for {product.title}"
        )
        db.add(order)
        db.flush()  # Get order ID
        
        # Create order item
        order_item = OrderItem(
            order_id=order.id,
            product_id=product.id,
            quantity=1,
            unit_price=unit_price,
            total_price=unit_price
        )
        db.add(order_item)
        
        # Reduce stock quantity
        product.stock_quantity -= 1
        
        # Update next delivery date
        subscription.next_delivery_date = self._calculate_next_delivery_date(
            subscription.next_delivery_date,
            subscription.plan_frequency
        )
        
        db.commit()
        db.refresh(order)
        
        return order
    
    def _get_plan_period(self, frequency: SubscriptionFrequency) -> str:
        """Get Razorpay plan period based on subscription frequency"""
        if frequency == SubscriptionFrequency.DAILY:
            return "daily"
        elif frequency == SubscriptionFrequency.ALTERNATE_DAYS:
            return "daily"
        elif frequency == SubscriptionFrequency.WEEKLY:
            return "weekly"
        else:
            raise ValueError(f"Invalid subscription frequency: {frequency}")
    
    def _get_plan_interval(self, frequency: SubscriptionFrequency) -> int:
        """Get Razorpay plan interval based on subscription frequency"""
        if frequency == SubscriptionFrequency.DAILY:
            return 1
        elif frequency == SubscriptionFrequency.ALTERNATE_DAYS:
            return 2
        elif frequency == SubscriptionFrequency.WEEKLY:
            return 1
        else:
            raise ValueError(f"Invalid subscription frequency: {frequency}")
    
    def _calculate_next_delivery_date(
        self,
        current_date: date,
        frequency: SubscriptionFrequency
    ) -> date:
        """Calculate next delivery date based on frequency"""
        if frequency == SubscriptionFrequency.DAILY:
            return current_date + timedelta(days=1)
        elif frequency == SubscriptionFrequency.ALTERNATE_DAYS:
            return current_date + timedelta(days=2)
        elif frequency == SubscriptionFrequency.WEEKLY:
            return current_date + timedelta(days=7)
        else:
            raise ValueError(f"Invalid subscription frequency: {frequency}")


# Create singleton instance
subscription_service = SubscriptionService()
