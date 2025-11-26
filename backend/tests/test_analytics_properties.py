"""Property-based tests for analytics functionality

These tests use Hypothesis to verify correctness properties across many random inputs.
"""
import os

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
from datetime import datetime, date, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base
from app.models.user import User
from app.models.product import Product
from app.models.category import Category
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.subscription import Subscription
from app.models.address import Address
from app.models.audit_log import AuditLog
from app.models.enums import UserRole, OrderStatus, PaymentStatus, SubscriptionStatus, SubscriptionFrequency
from app.services.analytics_service import AnalyticsService


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

def create_test_user(session, role=UserRole.CONSUMER, suffix=""):
    """Create a test user"""
    user_data = {
        'email': f'user{suffix}@example.com',
        'phone': f'+9198765432{suffix.zfill(2)}' if suffix else '+919876543210',
        'name': f'Test User {suffix}',
        'role': role,
        'hashed_password': 'hashed_password',
        'is_active': True
    }
    user = User(**user_data)
    session.add(user)
    session.commit()
    return user


def create_test_category(session, suffix=""):
    """Create a test category"""
    category = Category(
        name=f'Test Category {suffix}',
        slug=f'test-category-{suffix}' if suffix else 'test-category'
    )
    session.add(category)
    session.commit()
    return category


def create_test_product(session, category_id, stock_quantity=100, suffix=""):
    """Create a test product"""
    product = Product(
        owner_id=1,
        title=f'Test Product {suffix}',
        description=f'Test Description {suffix}',
        category_id=category_id,
        sku=f'TEST-SKU-{suffix}' if suffix else 'TEST-SKU',
        unit_size='1kg',
        consumer_price=Decimal('100.00'),
        distributor_price=Decimal('80.00'),
        stock_quantity=stock_quantity,
        is_active=True
    )
    session.add(product)
    session.commit()
    return product


def create_test_address(session, user_id):
    """Create a test address"""
    address = Address(
        user_id=user_id,
        name='Test Name',
        phone='+919876543210',
        address_line1='123 Test St',
        city='Test City',
        state='Test State',
        postal_code='123456',
        country='India',
        is_default=True
    )
    session.add(address)
    session.commit()
    return address


def create_test_order(session, user_id, address_id, final_amount, payment_status=PaymentStatus.PAID):
    """Create a test order"""
    order = Order(
        user_id=user_id,
        order_number=f'ORD-{datetime.utcnow().timestamp()}',
        total_amount=final_amount,
        discount_amount=Decimal('0.00'),
        final_amount=final_amount,
        payment_status=payment_status,
        order_status=OrderStatus.PENDING,
        delivery_address_id=address_id
    )
    session.add(order)
    session.commit()
    return order


def create_test_subscription(session, user_id, product_id, address_id, status=SubscriptionStatus.ACTIVE):
    """Create a test subscription"""
    subscription = Subscription(
        user_id=user_id,
        product_id=product_id,
        razorpay_subscription_id=f'sub_{datetime.utcnow().timestamp()}',
        plan_frequency=SubscriptionFrequency.DAILY,
        start_date=date.today(),
        next_delivery_date=date.today() + timedelta(days=1),
        delivery_address_id=address_id,
        status=status
    )
    session.add(subscription)
    session.commit()
    return subscription


# Property-based tests

# Feature: indostar-naturals-ecommerce, Property 49: Dashboard displays all metrics
@pytest.mark.asyncio
@given(
    num_orders=st.integers(min_value=0, max_value=10),
    num_subscriptions=st.integers(min_value=0, max_value=10),
    num_low_stock=st.integers(min_value=0, max_value=5)
)
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
async def test_dashboard_displays_all_metrics(num_orders, num_subscriptions, num_low_stock):
    """
    Property 49: Dashboard displays all metrics
    For any dashboard query, the response should include total revenue, order count,
    active subscriptions count, and low stock alerts.
    """
    session, engine = get_test_db()
    
    try:
        # Create test data
        owner = create_test_user(session, UserRole.OWNER, "owner")
        consumer = create_test_user(session, UserRole.CONSUMER, "consumer")
        category = create_test_category(session)
        address = create_test_address(session, consumer.id)
        
        # Create orders with varying amounts
        total_expected_revenue = Decimal('0.00')
        for i in range(num_orders):
            amount = Decimal(str((i + 1) * 100))
            create_test_order(session, consumer.id, address.id, amount, PaymentStatus.PAID)
            total_expected_revenue += amount
        
        # Create subscriptions
        for i in range(num_subscriptions):
            product = create_test_product(session, category.id, 100, f"sub{i}")
            create_test_subscription(session, consumer.id, product.id, address.id, SubscriptionStatus.ACTIVE)
        
        # Create low stock products
        for i in range(num_low_stock):
            create_test_product(session, category.id, i, f"low{i}")  # Stock < 10
        
        # Get dashboard metrics
        metrics = await AnalyticsService.get_dashboard_metrics(session)
        
        # Verify all required fields are present
        assert 'total_revenue' in metrics
        assert 'order_count' in metrics
        assert 'active_subscriptions' in metrics
        assert 'low_stock_alerts' in metrics
        
        # Verify values are correct
        assert metrics['order_count'] == num_orders
        assert metrics['active_subscriptions'] == num_subscriptions
        assert abs(metrics['total_revenue'] - float(total_expected_revenue)) < 0.01
        assert len(metrics['low_stock_alerts']) == num_low_stock
        
        # Verify low stock alerts have required fields
        for alert in metrics['low_stock_alerts']:
            assert 'product_id' in alert
            assert 'title' in alert
            assert 'sku' in alert
            assert 'stock_quantity' in alert
            assert alert['stock_quantity'] < 10
        
    finally:
        cleanup_test_db(session, engine)


# Feature: indostar-naturals-ecommerce, Property 50: Inventory reports show accurate stock
@pytest.mark.asyncio
@given(
    num_products=st.integers(min_value=1, max_value=10),
    stock_quantities=st.lists(st.integers(min_value=0, max_value=100), min_size=1, max_size=10)
)
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
async def test_inventory_reports_show_accurate_stock(num_products, stock_quantities):
    """
    Property 50: Inventory reports show accurate stock
    For any inventory report query, the system should return current stock levels
    for all products with support for category filtering.
    """
    session, engine = get_test_db()
    
    try:
        # Ensure we have enough stock quantities
        while len(stock_quantities) < num_products:
            stock_quantities.append(50)
        stock_quantities = stock_quantities[:num_products]
        
        # Create test data
        owner = create_test_user(session, UserRole.OWNER, "owner")
        category1 = create_test_category(session, "cat1")
        category2 = create_test_category(session, "cat2")
        
        # Create products in different categories
        products_cat1 = []
        products_cat2 = []
        
        for i in range(num_products):
            if i % 2 == 0:
                product = create_test_product(session, category1.id, stock_quantities[i], f"prod{i}")
                products_cat1.append(product)
            else:
                product = create_test_product(session, category2.id, stock_quantities[i], f"prod{i}")
                products_cat2.append(product)
        
        # Test 1: Get all inventory (no filter)
        inventory = await AnalyticsService.get_inventory_status(session)
        assert len(inventory) == num_products
        
        # Verify stock quantities match
        for item in inventory:
            assert 'product_id' in item
            assert 'stock_quantity' in item
            assert 'is_low_stock' in item
            # Find the corresponding product
            product_id = item['product_id']
            product = session.query(Product).filter(Product.id == product_id).first()
            assert item['stock_quantity'] == product.stock_quantity
            assert item['is_low_stock'] == (product.stock_quantity < 10)
        
        # Test 2: Filter by category 1
        inventory_cat1 = await AnalyticsService.get_inventory_status(session, category_id=category1.id)
        assert len(inventory_cat1) == len(products_cat1)
        for item in inventory_cat1:
            assert item['category_id'] == category1.id
        
        # Test 3: Filter by category 2
        inventory_cat2 = await AnalyticsService.get_inventory_status(session, category_id=category2.id)
        assert len(inventory_cat2) == len(products_cat2)
        for item in inventory_cat2:
            assert item['category_id'] == category2.id
        
    finally:
        cleanup_test_db(session, engine)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


# Feature: indostar-naturals-ecommerce, Property 52: User management supports filtering
@pytest.mark.asyncio
@given(
    num_consumers=st.integers(min_value=0, max_value=5),
    num_distributors=st.integers(min_value=0, max_value=5),
    num_owners=st.integers(min_value=0, max_value=2)
)
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
async def test_user_management_supports_filtering(num_consumers, num_distributors, num_owners):
    """
    Property 52: User management supports filtering
    For any user management query, the system should return users with support
    for filtering by role and account status.
    """
    session, engine = get_test_db()
    
    try:
        from app.services.user_service import user_service
        
        # Create users with different roles
        consumers = []
        for i in range(num_consumers):
            user = create_test_user(session, UserRole.CONSUMER, f"consumer{i}")
            consumers.append(user)
        
        distributors = []
        for i in range(num_distributors):
            user = create_test_user(session, UserRole.DISTRIBUTOR, f"distributor{i}")
            distributors.append(user)
        
        owners = []
        for i in range(num_owners):
            user = create_test_user(session, UserRole.OWNER, f"owner{i}")
            owners.append(user)
        
        total_users = num_consumers + num_distributors + num_owners
        
        # Test 1: Get all users (no filter)
        all_users = user_service.get_all_users(session)
        assert len(all_users) == total_users
        
        # Test 2: Filter by consumer role
        consumer_users = user_service.get_all_users(session, role_filter=UserRole.CONSUMER)
        assert len(consumer_users) == num_consumers
        for user in consumer_users:
            assert user.role == UserRole.CONSUMER
        
        # Test 3: Filter by distributor role
        distributor_users = user_service.get_all_users(session, role_filter=UserRole.DISTRIBUTOR)
        assert len(distributor_users) == num_distributors
        for user in distributor_users:
            assert user.role == UserRole.DISTRIBUTOR
        
        # Test 4: Filter by owner role
        owner_users = user_service.get_all_users(session, role_filter=UserRole.OWNER)
        assert len(owner_users) == num_owners
        for user in owner_users:
            assert user.role == UserRole.OWNER
        
        # Test 5: Filter by active status (all should be active)
        active_users = user_service.get_all_users(session, status_filter=True)
        assert len(active_users) == total_users
        
        # Test 6: Deactivate one user and test filtering
        if total_users > 0:
            all_users[0].is_active = False
            session.commit()
            
            active_users = user_service.get_all_users(session, status_filter=True)
            assert len(active_users) == total_users - 1
            
            inactive_users = user_service.get_all_users(session, status_filter=False)
            assert len(inactive_users) == 1
        
    finally:
        cleanup_test_db(session, engine)


# Feature: indostar-naturals-ecommerce, Property 62: Role changes create audit logs
@pytest.mark.asyncio
@given(
    initial_role=st.sampled_from([UserRole.CONSUMER, UserRole.DISTRIBUTOR]),
    new_role=st.sampled_from([UserRole.CONSUMER, UserRole.DISTRIBUTOR, UserRole.OWNER])
)
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
async def test_role_changes_create_audit_logs(initial_role, new_role):
    """
    Property 62: Role changes create audit logs
    For any user role update, the system should create an audit log entry containing
    actor_id, timestamp, affected user_id, old role, and new role.
    """
    session, engine = get_test_db()
    
    try:
        from app.services.user_service import user_service
        
        # Create an owner to perform the action
        owner = create_test_user(session, UserRole.OWNER, "owner")
        
        # Create a user with initial role
        user = create_test_user(session, initial_role, "user")
        
        # Count audit logs before
        audit_logs_before = session.query(AuditLog).count()
        
        # Update user role
        updated_user = user_service.update_user_role(
            user_id=user.id,
            new_role=new_role,
            actor_id=owner.id,
            db=session
        )
        
        # Verify user role was updated
        assert updated_user is not None
        assert updated_user.role == new_role
        
        # Count audit logs after
        audit_logs_after = session.query(AuditLog).count()
        
        # Verify audit log was created
        assert audit_logs_after == audit_logs_before + 1
        
        # Get the audit log entry
        audit_log = session.query(AuditLog).filter(
            AuditLog.object_type == "USER",
            AuditLog.object_id == user.id,
            AuditLog.action_type == "USER_ROLE_UPDATED"
        ).first()
        
        # Verify audit log contains required fields
        assert audit_log is not None
        assert audit_log.actor_id == owner.id
        assert audit_log.created_at is not None
        assert 'old_role' in audit_log.details
        assert 'new_role' in audit_log.details
        assert audit_log.details['old_role'] == initial_role.value
        assert audit_log.details['new_role'] == new_role.value
        assert 'user_email' in audit_log.details
        assert 'user_phone' in audit_log.details
        
    finally:
        cleanup_test_db(session, engine)



# Feature: indostar-naturals-ecommerce, Property 63: Audit logs support filtering
@pytest.mark.asyncio
@given(
    num_logs=st.integers(min_value=1, max_value=10),
    action_types=st.lists(
        st.sampled_from(["PRODUCT_CREATED", "PRICE_UPDATED", "STOCK_UPDATED", "USER_ROLE_UPDATED"]),
        min_size=1,
        max_size=4
    )
)
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
async def test_audit_logs_support_filtering(num_logs, action_types):
    """
    Property 63: Audit logs support filtering
    For any audit log query, the system should support filtering by action type,
    date range, and actor.
    """
    session, engine = get_test_db()
    
    try:
        # Create test users
        owner1 = create_test_user(session, UserRole.OWNER, "owner1")
        owner2 = create_test_user(session, UserRole.OWNER, "owner2")
        category = create_test_category(session)
        
        # Create audit logs with different action types and actors
        logs_by_action = {}
        logs_by_actor = {owner1.id: [], owner2.id: []}
        
        for i in range(num_logs):
            action_type = action_types[i % len(action_types)]
            actor_id = owner1.id if i % 2 == 0 else owner2.id
            
            # Create a product for the audit log
            product = create_test_product(session, category.id, 100, f"prod{i}")
            
            audit_log = AuditLog(
                actor_id=actor_id,
                action_type=action_type,
                object_type="PRODUCT",
                object_id=product.id,
                details={"test": f"log_{i}"}
            )
            session.add(audit_log)
            session.commit()
            
            # Track logs by action type
            if action_type not in logs_by_action:
                logs_by_action[action_type] = []
            logs_by_action[action_type].append(audit_log)
            
            # Track logs by actor
            logs_by_actor[actor_id].append(audit_log)
        
        # Test 1: Get all logs (no filter)
        all_logs = await AnalyticsService.get_audit_logs(session)
        assert len(all_logs) >= num_logs  # May have more from previous tests
        
        # Test 2: Filter by action type
        for action_type in set(action_types):
            filtered_logs = await AnalyticsService.get_audit_logs(
                session,
                action_type_filter=action_type
            )
            # Verify all returned logs have the correct action type
            for log in filtered_logs:
                assert log['action_type'] == action_type
        
        # Test 3: Filter by actor
        logs_actor1 = await AnalyticsService.get_audit_logs(
            session,
            actor_id_filter=owner1.id
        )
        for log in logs_actor1:
            assert log['actor_id'] == owner1.id
        
        logs_actor2 = await AnalyticsService.get_audit_logs(
            session,
            actor_id_filter=owner2.id
        )
        for log in logs_actor2:
            assert log['actor_id'] == owner2.id
        
        # Test 4: Filter by date range
        now = datetime.utcnow()
        yesterday = now - timedelta(days=1)
        tomorrow = now + timedelta(days=1)
        
        logs_in_range = await AnalyticsService.get_audit_logs(
            session,
            start_date=yesterday,
            end_date=tomorrow
        )
        # All logs should be in this range
        assert len(logs_in_range) >= num_logs
        
        # Test 5: Verify required fields are present
        if all_logs:
            log = all_logs[0]
            assert 'id' in log
            assert 'actor_id' in log
            assert 'action_type' in log
            assert 'object_type' in log
            assert 'object_id' in log
            assert 'details' in log
            assert 'created_at' in log
        
    finally:
        cleanup_test_db(session, engine)



# Feature: indostar-naturals-ecommerce, Property 61: Price changes create audit logs
@pytest.mark.asyncio
@given(
    old_consumer_price=st.decimals(min_value=10, max_value=1000, places=2),
    new_consumer_price=st.decimals(min_value=10, max_value=1000, places=2),
    old_distributor_price=st.decimals(min_value=10, max_value=1000, places=2),
    new_distributor_price=st.decimals(min_value=10, max_value=1000, places=2)
)
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
async def test_price_changes_create_audit_logs(
    old_consumer_price,
    new_consumer_price,
    old_distributor_price,
    new_distributor_price
):
    """
    Property 61: Price changes create audit logs
    For any product price update, the system should create an audit log entry containing
    actor_id, timestamp, old price, and new price.
    """
    session, engine = get_test_db()
    
    try:
        from app.services.product_service import product_service
        from app.schemas.product import ProductUpdate
        
        # Assume prices are different to trigger audit log
        assume(old_consumer_price != new_consumer_price or old_distributor_price != new_distributor_price)
        
        # Create test data
        owner = create_test_user(session, UserRole.OWNER, "owner")
        category = create_test_category(session)
        
        # Create a product with old prices
        product = Product(
            owner_id=owner.id,
            title='Test Product',
            description='Test Description',
            category_id=category.id,
            sku='TEST-SKU',
            unit_size='1kg',
            consumer_price=old_consumer_price,
            distributor_price=old_distributor_price,
            stock_quantity=100,
            is_active=True
        )
        session.add(product)
        session.commit()
        session.refresh(product)
        
        # Count audit logs before
        audit_logs_before = session.query(AuditLog).filter(
            AuditLog.action_type == "PRODUCT_PRICE_UPDATED"
        ).count()
        
        # Update product prices
        update_data = ProductUpdate(
            consumer_price=new_consumer_price,
            distributor_price=new_distributor_price
        )
        
        updated_product = product_service.update_product(
            product_id=product.id,
            product_data=update_data,
            actor_id=owner.id,
            db=session
        )
        
        # Verify product was updated
        assert updated_product is not None
        assert updated_product.consumer_price == new_consumer_price
        assert updated_product.distributor_price == new_distributor_price
        
        # Count audit logs after
        audit_logs_after = session.query(AuditLog).filter(
            AuditLog.action_type == "PRODUCT_PRICE_UPDATED"
        ).count()
        
        # Verify audit log was created
        assert audit_logs_after == audit_logs_before + 1
        
        # Get the audit log entry
        audit_log = session.query(AuditLog).filter(
            AuditLog.object_type == "PRODUCT",
            AuditLog.object_id == product.id,
            AuditLog.action_type == "PRODUCT_PRICE_UPDATED"
        ).first()
        
        # Verify audit log contains required fields
        assert audit_log is not None
        assert audit_log.actor_id == owner.id
        assert audit_log.created_at is not None
        assert 'price_changes' in audit_log.details
        
        price_changes = audit_log.details['price_changes']
        
        # Verify consumer price change is logged
        if old_consumer_price != new_consumer_price:
            assert 'consumer_price' in price_changes
            assert abs(price_changes['consumer_price']['old'] - float(old_consumer_price)) < 0.01
            assert abs(price_changes['consumer_price']['new'] - float(new_consumer_price)) < 0.01
        
        # Verify distributor price change is logged
        if old_distributor_price != new_distributor_price:
            assert 'distributor_price' in price_changes
            assert abs(price_changes['distributor_price']['old'] - float(old_distributor_price)) < 0.01
            assert abs(price_changes['distributor_price']['new'] - float(new_distributor_price)) < 0.01
        
    finally:
        cleanup_test_db(session, engine)
