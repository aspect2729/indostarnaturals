"""Property-based tests for order functionality

These tests use Hypothesis to verify correctness properties across many random inputs.
"""
import os
import sys

# Set test environment variables before any imports
os.environ.setdefault('DATABASE_URL', 'sqlite:///:memory:')
os.environ.setdefault('REDIS_URL', 'redis://localhost:6379/0')
os.environ.setdefault('JWT_SECRET_KEY', 'test_secret_key')
os.environ.setdefault('RAZORPAY_KEY_ID', 'test_key')
os.environ.setdefault('RAZORPAY_KEY_SECRET', 'test_secret')
os.environ.setdefault('RAZORPAY_WEBHOOK_SECRET', 'test_webhook')
os.environ.setdefault('S3_BUCKET_NAME', 'test-bucket')
os.environ.setdefault('S3_ACCESS_KEY', 'test-access')
os.environ.setdefault('S3_SECRET_KEY', 'test-secret')

import pytest
from hypothesis import given, strategies as st, settings, assume, HealthCheck
from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base
from app.models.user import User
from app.models.product import Product
from app.models.category import Category
from app.models.cart import Cart
from app.models.cart_item import CartItem
from app.models.address import Address
from app.models.order import Order
from app.models.enums import UserRole, OrderStatus, PaymentStatus
from app.services.order_service import order_service
from app.services.cart_service import cart_service
from app.schemas.cart import CartItemCreate


# Test database setup
TEST_DATABASE_URL = "sqlite:///:memory:"


def get_test_db():
    """Create a test database session"""
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    return session, engine


def cleanup_test_db(session, engine):
    """Clean up test database"""
    session.close()
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


# Helper functions for creating test data

def create_test_owner(session, suffix=""):
    """Create a test owner user"""
    owner_data = {
        'email': f'owner{suffix}@example.com',
        'phone': f'+919999999{suffix.zfill(3)}' if suffix else '+919999999999',
        'name': f'Test Owner {suffix}',
        'role': UserRole.OWNER,
        'hashed_password': 'hashed_password',
        'is_active': True
    }
    owner = User(**owner_data)
    session.add(owner)
    session.commit()
    return owner


def create_test_consumer(session, suffix=""):
    """Create a test consumer user"""
    consumer_data = {
        'email': f'consumer{suffix}@example.com',
        'phone': f'+919876543{suffix.zfill(3)}' if suffix else '+919876543210',
        'name': f'Test Consumer {suffix}',
        'role': UserRole.CONSUMER,
        'hashed_password': 'hashed_password',
        'is_active': True
    }
    consumer = User(**consumer_data)
    session.add(consumer)
    session.commit()
    return consumer


def create_test_category(session, suffix=""):
    """Create a test category"""
    category = Category(
        name=f'Test Category {suffix}',
        slug=f'test-category-{suffix}' if suffix else 'test-category'
    )
    session.add(category)
    session.commit()
    return category


def create_test_product(session, owner_id, category_id, stock_quantity=100, suffix=""):
    """Create a test product"""
    import uuid
    sku_suffix = str(uuid.uuid4())[:8]
    product_data = {
        'owner_id': owner_id,
        'title': f'Test Product {suffix}',
        'description': 'Test Description',
        'category_id': category_id,
        'sku': f'TEST-{suffix}-{sku_suffix}' if suffix else f'TEST-{sku_suffix}',
        'unit_size': '1 kg',
        'consumer_price': Decimal('100.00'),
        'distributor_price': Decimal('80.00'),
        'stock_quantity': stock_quantity,
        'is_active': True
    }
    product = Product(**product_data)
    session.add(product)
    session.commit()
    return product


def create_test_address(session, user_id, suffix=""):
    """Create a test address"""
    address_data = {
        'user_id': user_id,
        'name': f'Test User {suffix}',
        'phone': f'+919876543{suffix.zfill(3)}' if suffix else '+919876543210',
        'address_line1': f'123 Test Street {suffix}',
        'address_line2': None,
        'city': 'Test City',
        'state': 'Test State',
        'postal_code': '123456',
        'country': 'India',
        'is_default': True
    }
    address = Address(**address_data)
    session.add(address)
    session.commit()
    return address


# Property Tests

# Feature: indostar-naturals-ecommerce, Property 27: Checkout validates stock
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
@given(
    quantity_multiplier=st.floats(min_value=1.1, max_value=5.0)
)
def test_checkout_validates_stock(quantity_multiplier):
    """
    Property 27: Checkout validates stock
    
    For any checkout initiation, the system should verify that all cart items
    have sufficient stock before creating an order.
    
    Validates: Requirements 6.1
    """
    session, engine = get_test_db()
    
    try:
        # Create test data
        owner = create_test_owner(session)
        category = create_test_category(session)
        consumer = create_test_consumer(session)
        address = create_test_address(session, consumer.id)
        
        # Create product with limited stock
        product = create_test_product(session, owner.id, category.id, stock_quantity=10)
        
        # Add item to cart with quantity that exceeds stock
        requested_quantity = int(product.stock_quantity * quantity_multiplier)
        assume(requested_quantity > product.stock_quantity)  # Ensure we're testing insufficient stock
        
        # Create cart manually
        cart = Cart(user_id=consumer.id)
        session.add(cart)
        session.commit()
        
        # Add cart item with excessive quantity
        cart_item = CartItem(
            cart_id=cart.id,
            product_id=product.id,
            quantity=requested_quantity,
            unit_price=product.consumer_price
        )
        session.add(cart_item)
        session.commit()
        
        # Attempt to create order - should fail due to insufficient stock
        with pytest.raises(ValueError) as exc_info:
            order_service.create_order(
                user_id=consumer.id,
                address_id=address.id,
                db=session
            )
        
        # Verify error message mentions insufficient stock
        assert "Insufficient stock" in str(exc_info.value)
        
        # Verify no order was created
        orders = session.query(Order).filter(Order.user_id == consumer.id).all()
        assert len(orders) == 0, "No order should be created when stock is insufficient"
        
    finally:
        cleanup_test_db(session, engine)


# Feature: indostar-naturals-ecommerce, Property 32: Order creation reduces stock
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
@given(
    quantity=st.integers(min_value=1, max_value=10)
)
def test_order_creation_reduces_stock(quantity):
    """
    Property 32: Order creation reduces stock
    
    For any order created, the stock quantity for each ordered product
    should be reduced by the ordered quantity.
    
    Validates: Requirements 6.6
    """
    session, engine = get_test_db()
    
    try:
        # Create test data
        owner = create_test_owner(session)
        category = create_test_category(session)
        consumer = create_test_consumer(session)
        address = create_test_address(session, consumer.id)
        product = create_test_product(session, owner.id, category.id, stock_quantity=100)
        
        # Record initial stock
        initial_stock = product.stock_quantity
        
        # Add item to cart
        cart_item_data = CartItemCreate(product_id=product.id, quantity=quantity)
        cart_service.add_item(consumer.id, cart_item_data, session)
        
        # Create order
        order = order_service.create_order(
            user_id=consumer.id,
            address_id=address.id,
            db=session
        )
        
        # Refresh product to get updated stock
        session.refresh(product)
        
        # Verify stock was reduced by the ordered quantity
        expected_stock = initial_stock - quantity
        assert product.stock_quantity == expected_stock, \
            f"Stock should be reduced from {initial_stock} to {expected_stock}, but is {product.stock_quantity}"
        
    finally:
        cleanup_test_db(session, engine)


# Feature: indostar-naturals-ecommerce, Property 40: New orders start as pending
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
@given(
    quantity=st.integers(min_value=1, max_value=10)
)
def test_new_orders_start_as_pending(quantity):
    """
    Property 40: New orders start as pending
    
    For any newly created order, the initial order_status should be PENDING.
    
    Validates: Requirements 8.1
    """
    session, engine = get_test_db()
    
    try:
        # Create test data
        owner = create_test_owner(session)
        category = create_test_category(session)
        consumer = create_test_consumer(session)
        address = create_test_address(session, consumer.id)
        product = create_test_product(session, owner.id, category.id)
        
        # Add item to cart
        cart_item_data = CartItemCreate(product_id=product.id, quantity=quantity)
        cart_service.add_item(consumer.id, cart_item_data, session)
        
        # Create order
        order = order_service.create_order(
            user_id=consumer.id,
            address_id=address.id,
            db=session
        )
        
        # Verify order status is PENDING
        assert order.order_status == OrderStatus.PENDING, \
            f"New order should have status PENDING, but has {order.order_status}"
        
        # Verify payment status is also PENDING
        assert order.payment_status == PaymentStatus.PENDING, \
            f"New order should have payment status PENDING, but has {order.payment_status}"
        
    finally:
        cleanup_test_db(session, engine)


# Feature: indostar-naturals-ecommerce, Property 41: Order status transitions are valid
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
@given(
    new_status=st.sampled_from([
        OrderStatus.PENDING,
        OrderStatus.CONFIRMED,
        OrderStatus.PACKED,
        OrderStatus.OUT_FOR_DELIVERY,
        OrderStatus.DELIVERED,
        OrderStatus.CANCELLED,
        OrderStatus.REFUNDED
    ])
)
def test_order_status_transitions_are_valid(new_status):
    """
    Property 41: Order status transitions are valid
    
    For any order status update, the new status should be one of the valid states:
    pending, confirmed, packed, out-for-delivery, delivered, cancelled, or refunded.
    
    Validates: Requirements 8.2
    """
    session, engine = get_test_db()
    
    try:
        # Create test data
        owner = create_test_owner(session)
        category = create_test_category(session)
        consumer = create_test_consumer(session)
        address = create_test_address(session, consumer.id)
        product = create_test_product(session, owner.id, category.id)
        
        # Add item to cart and create order
        cart_item_data = CartItemCreate(product_id=product.id, quantity=1)
        cart_service.add_item(consumer.id, cart_item_data, session)
        
        order = order_service.create_order(
            user_id=consumer.id,
            address_id=address.id,
            db=session
        )
        
        # Update order status
        updated_order = order_service.update_order_status(
            order_id=order.id,
            new_status=new_status,
            actor_id=owner.id,
            db=session
        )
        
        # Verify status was updated to the requested valid status
        assert updated_order.order_status == new_status, \
            f"Order status should be {new_status}, but is {updated_order.order_status}"
        
    finally:
        cleanup_test_db(session, engine)


# Feature: indostar-naturals-ecommerce, Property 43: Consumer sees own orders
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
@given(
    quantity=st.integers(min_value=1, max_value=10)
)
def test_consumer_sees_own_orders(quantity):
    """
    Property 43: Consumer sees own orders
    
    For any consumer viewing order history, the system should return
    only orders belonging to that consumer.
    
    Validates: Requirements 8.4
    """
    session, engine = get_test_db()
    
    try:
        # Create test data
        owner = create_test_owner(session)
        category = create_test_category(session)
        
        # Create two consumers
        consumer1 = create_test_consumer(session, suffix="1")
        consumer2 = create_test_consumer(session, suffix="2")
        
        # Create addresses
        address1 = create_test_address(session, consumer1.id, suffix="1")
        address2 = create_test_address(session, consumer2.id, suffix="2")
        
        # Create product
        product = create_test_product(session, owner.id, category.id)
        
        # Create order for consumer1
        cart_item_data = CartItemCreate(product_id=product.id, quantity=quantity)
        cart_service.add_item(consumer1.id, cart_item_data, session)
        order1 = order_service.create_order(
            user_id=consumer1.id,
            address_id=address1.id,
            db=session
        )
        
        # Create order for consumer2
        cart_service.add_item(consumer2.id, cart_item_data, session)
        order2 = order_service.create_order(
            user_id=consumer2.id,
            address_id=address2.id,
            db=session
        )
        
        # Get orders for consumer1
        orders1, count1 = order_service.get_user_orders(
            user_id=consumer1.id,
            db=session
        )
        
        # Verify consumer1 only sees their own order
        assert len(orders1) == 1, f"Consumer1 should see 1 order, but sees {len(orders1)}"
        assert orders1[0].id == order1.id, "Consumer1 should see their own order"
        assert orders1[0].user_id == consumer1.id, "Order should belong to consumer1"
        
        # Verify consumer1 doesn't see consumer2's order
        order_ids = [o.id for o in orders1]
        assert order2.id not in order_ids, "Consumer1 should not see consumer2's order"
        
    finally:
        cleanup_test_db(session, engine)


# Feature: indostar-naturals-ecommerce, Property 44: Owner sees all orders
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
@given(
    num_consumers=st.integers(min_value=2, max_value=5)
)
def test_owner_sees_all_orders(num_consumers):
    """
    Property 44: Owner sees all orders
    
    For any owner viewing orders, the system should return orders from all users
    with support for filtering by status, date range, and user role.
    
    Validates: Requirements 8.5
    """
    session, engine = get_test_db()
    
    try:
        # Create test data
        owner = create_test_owner(session)
        category = create_test_category(session)
        product = create_test_product(session, owner.id, category.id, stock_quantity=1000)
        
        # Create multiple consumers and orders
        order_ids = []
        for i in range(num_consumers):
            consumer = create_test_consumer(session, suffix=str(i))
            address = create_test_address(session, consumer.id, suffix=str(i))
            
            cart_item_data = CartItemCreate(product_id=product.id, quantity=1)
            cart_service.add_item(consumer.id, cart_item_data, session)
            
            order = order_service.create_order(
                user_id=consumer.id,
                address_id=address.id,
                db=session
            )
            order_ids.append(order.id)
        
        # Owner gets all orders
        all_orders, total_count = order_service.get_all_orders(
            page=1,
            page_size=100,
            db=session
        )
        
        # Verify owner sees all orders
        assert len(all_orders) == num_consumers, \
            f"Owner should see {num_consumers} orders, but sees {len(all_orders)}"
        
        # Verify all created orders are in the result
        retrieved_order_ids = [o.id for o in all_orders]
        for order_id in order_ids:
            assert order_id in retrieved_order_ids, \
                f"Owner should see order {order_id}"
        
    finally:
        cleanup_test_db(session, engine)


# Feature: indostar-naturals-ecommerce, Property 42: Status changes trigger notifications
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
@given(
    new_status=st.sampled_from([
        OrderStatus.CONFIRMED,
        OrderStatus.OUT_FOR_DELIVERY
    ])
)
def test_status_changes_trigger_notifications(new_status, monkeypatch):
    """
    Property 42: Status changes trigger notifications
    
    For any order status change, the system should send an email notification
    to the customer.
    
    Validates: Requirements 8.3
    """
    session, engine = get_test_db()
    
    # Track notification calls
    notification_calls = []
    
    def mock_send_order_confirmation(*args, **kwargs):
        notification_calls.append(('order_confirmation', args, kwargs))
        return (True, True)  # email_sent, sms_sent
    
    def mock_send_order_shipped(*args, **kwargs):
        notification_calls.append(('order_shipped', args, kwargs))
        return (True, True)  # email_sent, sms_sent
    
    # Patch notification methods
    monkeypatch.setattr(
        'app.services.order_service.notification_service.send_order_confirmation',
        mock_send_order_confirmation
    )
    monkeypatch.setattr(
        'app.services.order_service.notification_service.send_order_shipped',
        mock_send_order_shipped
    )
    
    try:
        # Create test data
        owner = create_test_owner(session)
        category = create_test_category(session)
        consumer = create_test_consumer(session)
        address = create_test_address(session, consumer.id)
        product = create_test_product(session, owner.id, category.id)
        
        # Add item to cart and create order
        cart_item_data = CartItemCreate(product_id=product.id, quantity=1)
        cart_service.add_item(consumer.id, cart_item_data, session)
        
        order = order_service.create_order(
            user_id=consumer.id,
            address_id=address.id,
            db=session
        )
        
        # Clear notification calls from order creation
        notification_calls.clear()
        
        # Update order status
        updated_order = order_service.update_order_status(
            order_id=order.id,
            new_status=new_status,
            actor_id=owner.id,
            db=session
        )
        
        # Verify notification was sent
        assert len(notification_calls) > 0, \
            f"Status change to {new_status} should trigger a notification"
        
        # Verify correct notification type was sent
        notification_type, args, kwargs = notification_calls[0]
        
        if new_status == OrderStatus.CONFIRMED:
            assert notification_type == 'order_confirmation', \
                "CONFIRMED status should trigger order confirmation notification"
            # Verify notification contains order details
            assert order.order_number in str(args) or order.order_number in str(kwargs), \
                "Notification should contain order number"
        elif new_status == OrderStatus.OUT_FOR_DELIVERY:
            assert notification_type == 'order_shipped', \
                "OUT_FOR_DELIVERY status should trigger order shipped notification"
            # Verify notification contains order details
            assert order.order_number in str(args) or order.order_number in str(kwargs), \
                "Notification should contain order number"
        
        # Verify customer email/phone was used
        assert consumer.email in str(args) or consumer.email in str(kwargs) or \
               consumer.phone in str(args) or consumer.phone in str(kwargs), \
            "Notification should be sent to customer's email or phone"
        
    finally:
        cleanup_test_db(session, engine)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
