"""Order Service

Handles order creation, retrieval, status updates, and refund processing.
"""
from typing import Optional, List, Tuple
from decimal import Decimal
from datetime import datetime
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, desc
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.cart import Cart
from app.models.cart_item import CartItem
from app.models.product import Product
from app.models.user import User
from app.models.address import Address
from app.models.audit_log import AuditLog
from app.models.enums import OrderStatus, PaymentStatus, UserRole
from app.models.bulk_discount_rule import BulkDiscountRule
from app.schemas.cart import CartValidation
from app.services.notification_service import notification_service


class OrderService:
    """Service for order management operations"""
    
    @staticmethod
    def create_order(
        user_id: int,
        address_id: int,
        db: Session
    ) -> Order:
        """
        Create order with stock validation and reduction.
        
        This function:
        1. Validates cart items against current stock
        2. Creates order and order items
        3. Reduces product stock quantities
        4. Clears the cart
        
        All operations are performed within a database transaction.
        
        Args:
            user_id: User ID
            address_id: Delivery address ID
            db: Database session
            
        Returns:
            Created Order object
            
        Raises:
            ValueError: If validation fails or insufficient stock
        """
        # Get user
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError(f"User with ID {user_id} does not exist")
        
        # Verify address belongs to user
        address = db.query(Address).filter(
            and_(
                Address.id == address_id,
                Address.user_id == user_id
            )
        ).first()
        
        if not address:
            raise ValueError(f"Address with ID {address_id} not found or does not belong to user")
        
        # Get cart with items
        cart = db.query(Cart).options(
            joinedload(Cart.items).joinedload(CartItem.product)
        ).filter(Cart.user_id == user_id).first()
        
        if not cart or not cart.items:
            raise ValueError("Cart is empty")
        
        # Validate cart and check stock availability
        errors = []
        for item in cart.items:
            product = item.product
            
            # Check if product is still active
            if not product.is_active:
                errors.append(f"Product '{product.title}' is no longer available")
            
            # Check stock availability (atomic check within transaction)
            if product.stock_quantity < item.quantity:
                errors.append(
                    f"Insufficient stock for '{product.title}'. "
                    f"Available: {product.stock_quantity}, Requested: {item.quantity}"
                )
        
        if errors:
            raise ValueError("; ".join(errors))
        
        # Calculate order totals
        subtotal = sum(item.quantity * item.unit_price for item in cart.items)
        discount = cart.discount_amount or Decimal('0.00')
        final_amount = subtotal - discount
        
        # Generate unique order number
        order_number = f"ORD-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{user_id}"
        
        # Create order
        order = Order(
            user_id=user_id,
            order_number=order_number,
            total_amount=subtotal,
            discount_amount=discount,
            final_amount=final_amount,
            payment_status=PaymentStatus.PENDING,
            order_status=OrderStatus.PENDING,
            delivery_address_id=address_id,
            notes=None
        )
        db.add(order)
        db.flush()  # Get order ID
        
        # Create order items and reduce stock
        for cart_item in cart.items:
            product = cart_item.product
            
            # Create order item
            order_item = OrderItem(
                order_id=order.id,
                product_id=cart_item.product_id,
                quantity=cart_item.quantity,
                unit_price=cart_item.unit_price,
                total_price=cart_item.quantity * cart_item.unit_price
            )
            db.add(order_item)
            
            # Reduce stock quantity
            product.stock_quantity -= cart_item.quantity
        
        # Clear cart items
        for cart_item in cart.items:
            db.delete(cart_item)
        
        # Reset cart discount
        cart.coupon_code = None
        cart.discount_amount = Decimal('0.00')
        
        db.commit()
        db.refresh(order)
        
        return order
    
    @staticmethod
    def get_user_orders(
        user_id: int,
        page: int = 1,
        page_size: int = 20,
        status_filter: Optional[OrderStatus] = None,
        db: Session = None
    ) -> Tuple[List[Order], int]:
        """
        Get user's orders with pagination.
        
        Args:
            user_id: User ID
            page: Page number (1-indexed)
            page_size: Number of items per page
            status_filter: Optional status filter
            db: Database session
            
        Returns:
            Tuple of (list of orders, total count)
        """
        # Build query
        query = db.query(Order).options(
            joinedload(Order.items).joinedload(OrderItem.product),
            joinedload(Order.delivery_address)
        ).filter(Order.user_id == user_id)
        
        # Apply status filter if provided
        if status_filter:
            query = query.filter(Order.order_status == status_filter)
        
        # Get total count
        total_count = query.count()
        
        # Apply pagination and ordering
        orders = query.order_by(desc(Order.created_at)).offset(
            (page - 1) * page_size
        ).limit(page_size).all()
        
        return orders, total_count
    
    @staticmethod
    def get_order_by_id(
        order_id: int,
        user_id: Optional[int] = None,
        db: Session = None
    ) -> Order:
        """
        Get order by ID with ownership validation.
        
        Args:
            order_id: Order ID
            user_id: Optional user ID for ownership validation
            db: Database session
            
        Returns:
            Order object
            
        Raises:
            ValueError: If order not found or doesn't belong to user
        """
        # Build query
        query = db.query(Order).options(
            joinedload(Order.items).joinedload(OrderItem.product),
            joinedload(Order.delivery_address),
            joinedload(Order.user)
        ).filter(Order.id == order_id)
        
        order = query.first()
        
        if not order:
            raise ValueError(f"Order with ID {order_id} not found")
        
        # Validate ownership if user_id provided
        if user_id is not None and order.user_id != user_id:
            raise ValueError(f"Order with ID {order_id} does not belong to user")
        
        return order
    
    @staticmethod
    def update_order_status(
        order_id: int,
        new_status: OrderStatus,
        actor_id: int,
        db: Session
    ) -> Order:
        """
        Update order status with state validation and audit logging.
        
        Args:
            order_id: Order ID
            new_status: New order status
            actor_id: ID of user performing the update
            db: Database session
            
        Returns:
            Updated Order object
            
        Raises:
            ValueError: If order not found or invalid status transition
        """
        # Get order
        order = db.query(Order).filter(Order.id == order_id).first()
        
        if not order:
            raise ValueError(f"Order with ID {order_id} not found")
        
        # Validate status transition
        valid_statuses = [
            OrderStatus.PENDING,
            OrderStatus.CONFIRMED,
            OrderStatus.PACKED,
            OrderStatus.OUT_FOR_DELIVERY,
            OrderStatus.DELIVERED,
            OrderStatus.CANCELLED,
            OrderStatus.REFUNDED
        ]
        
        if new_status not in valid_statuses:
            raise ValueError(f"Invalid order status: {new_status}")
        
        # Store old status for audit log
        old_status = order.order_status
        
        # Update status
        order.order_status = new_status
        order.updated_at = datetime.utcnow()
        
        # Create audit log
        audit_log = AuditLog(
            actor_id=actor_id,
            action_type="ORDER_STATUS_UPDATED",
            object_type="ORDER",
            object_id=order_id,
            details={
                "old_status": old_status.value,
                "new_status": new_status.value,
                "order_number": order.order_number
            }
        )
        db.add(audit_log)
        
        db.commit()
        db.refresh(order)
        
        # Send notifications based on status change
        # Load user and address for notification context
        user = db.query(User).filter(User.id == order.user_id).first()
        address = db.query(Address).filter(Address.id == order.delivery_address_id).first()
        
        if user and new_status == OrderStatus.CONFIRMED:
            # Send order confirmation notification
            notification_service.send_order_confirmation(
                email=user.email or "",
                phone=user.phone,
                order_number=order.order_number,
                customer_name=user.name,
                order_total=str(order.final_amount),
                delivery_address=f"{address.address_line1}, {address.city}" if address else "N/A"
            )
        elif user and new_status == OrderStatus.OUT_FOR_DELIVERY:
            # Send order shipped notification
            notification_service.send_order_shipped(
                email=user.email or "",
                phone=user.phone,
                order_number=order.order_number,
                customer_name=user.name,
                tracking_info="TBD",  # Would come from shipping provider
                expected_delivery="2-3 business days"
            )
        
        return order
    
    @staticmethod
    def process_refund(
        order_id: int,
        actor_id: int,
        db: Session
    ) -> Order:
        """
        Process refund for an order.
        
        This function:
        1. Updates order status to REFUNDED
        2. Updates payment status to REFUNDED
        3. Restores product stock quantities
        4. Creates audit log
        
        Args:
            order_id: Order ID
            actor_id: ID of user performing the refund
            db: Database session
            
        Returns:
            Updated Order object
            
        Raises:
            ValueError: If order not found or cannot be refunded
        """
        # Get order with items
        order = db.query(Order).options(
            joinedload(Order.items).joinedload(OrderItem.product)
        ).filter(Order.id == order_id).first()
        
        if not order:
            raise ValueError(f"Order with ID {order_id} not found")
        
        # Validate order can be refunded
        if order.order_status == OrderStatus.REFUNDED:
            raise ValueError("Order has already been refunded")
        
        if order.payment_status != PaymentStatus.PAID:
            raise ValueError("Can only refund paid orders")
        
        # Update order status
        old_status = order.order_status
        order.order_status = OrderStatus.REFUNDED
        order.payment_status = PaymentStatus.REFUNDED
        order.updated_at = datetime.utcnow()
        
        # Restore stock quantities
        for order_item in order.items:
            product = order_item.product
            product.stock_quantity += order_item.quantity
        
        # Create audit log
        audit_log = AuditLog(
            actor_id=actor_id,
            action_type="ORDER_REFUNDED",
            object_type="ORDER",
            object_id=order_id,
            details={
                "old_status": old_status.value,
                "new_status": OrderStatus.REFUNDED.value,
                "order_number": order.order_number,
                "refund_amount": str(order.final_amount)
            }
        )
        db.add(audit_log)
        
        db.commit()
        db.refresh(order)
        
        return order
    
    @staticmethod
    def get_all_orders(
        page: int = 1,
        page_size: int = 20,
        status_filter: Optional[OrderStatus] = None,
        user_role_filter: Optional[UserRole] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        db: Session = None
    ) -> Tuple[List[Order], int]:
        """
        Get all orders with filtering (owner only).
        
        Args:
            page: Page number (1-indexed)
            page_size: Number of items per page
            status_filter: Optional status filter
            user_role_filter: Optional user role filter
            start_date: Optional start date filter
            end_date: Optional end date filter
            db: Database session
            
        Returns:
            Tuple of (list of orders, total count)
        """
        # Build query
        query = db.query(Order).options(
            joinedload(Order.items).joinedload(OrderItem.product),
            joinedload(Order.delivery_address),
            joinedload(Order.user)
        )
        
        # Apply filters
        if status_filter:
            query = query.filter(Order.order_status == status_filter)
        
        if user_role_filter:
            query = query.join(User).filter(User.role == user_role_filter)
        
        if start_date:
            query = query.filter(Order.created_at >= start_date)
        
        if end_date:
            query = query.filter(Order.created_at <= end_date)
        
        # Get total count
        total_count = query.count()
        
        # Apply pagination and ordering
        orders = query.order_by(desc(Order.created_at)).offset(
            (page - 1) * page_size
        ).limit(page_size).all()
        
        return orders, total_count
    
    @staticmethod
    def apply_bulk_discounts(
        order: Order,
        db: Session
    ) -> Decimal:
        """
        Apply bulk discount rules to an order for distributor users.
        
        This function calculates additional discounts based on quantity thresholds
        for distributor orders. Discounts can be product-specific, category-specific,
        or apply to all products.
        
        Args:
            order: Order object with loaded items
            db: Database session
            
        Returns:
            Total bulk discount amount
        """
        # Only apply bulk discounts to distributor orders
        user = db.query(User).filter(User.id == order.user_id).first()
        if not user or user.role != UserRole.DISTRIBUTOR:
            return Decimal('0.00')
        
        total_discount = Decimal('0.00')
        
        # Get all active bulk discount rules
        bulk_rules = db.query(BulkDiscountRule).filter(
            BulkDiscountRule.is_active == True
        ).all()
        
        # Group order items by product and category for efficient processing
        for order_item in order.items:
            product = order_item.product
            applicable_discount = Decimal('0.00')
            
            # Find the best applicable discount rule
            # Priority: Product-specific > Category-specific > Global
            
            # Check product-specific rules
            product_rules = [
                rule for rule in bulk_rules
                if rule.product_id == product.id and order_item.quantity >= rule.min_quantity
            ]
            
            if product_rules:
                # Get the rule with highest discount percentage
                best_rule = max(product_rules, key=lambda r: r.discount_percentage)
                applicable_discount = (order_item.total_price * best_rule.discount_percentage) / Decimal('100')
            else:
                # Check category-specific rules
                category_rules = [
                    rule for rule in bulk_rules
                    if rule.category_id == product.category_id and rule.product_id is None
                    and order_item.quantity >= rule.min_quantity
                ]
                
                if category_rules:
                    best_rule = max(category_rules, key=lambda r: r.discount_percentage)
                    applicable_discount = (order_item.total_price * best_rule.discount_percentage) / Decimal('100')
                else:
                    # Check global rules (no product_id and no category_id)
                    global_rules = [
                        rule for rule in bulk_rules
                        if rule.product_id is None and rule.category_id is None
                        and order_item.quantity >= rule.min_quantity
                    ]
                    
                    if global_rules:
                        best_rule = max(global_rules, key=lambda r: r.discount_percentage)
                        applicable_discount = (order_item.total_price * best_rule.discount_percentage) / Decimal('100')
            
            total_discount += applicable_discount
        
        return total_discount


# Create singleton instance
order_service = OrderService()
