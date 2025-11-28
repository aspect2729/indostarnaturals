"""Unit tests for analytics API endpoints"""
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
from fastapi.testclient import TestClient
from datetime import date, timedelta
from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.core.database import Base, get_db
from app.models.user import User
from app.models.product import Product
from app.models.category import Category
from app.models.order import Order
from app.models.address import Address
from app.models.subscription import Subscription
from app.models.enums import UserRole, OrderStatus, PaymentStatus, SubscriptionStatus, SubscriptionFrequency
from app.services.auth_service import TokenService


# Test database setup
TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(scope="function", autouse=True)
def setup_database():
    """Create tables before each test and drop after"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session():
    """Get a database session for tests"""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def owner_user(db_session):
    """Create an owner user for testing"""
    user = User(
        email='owner@example.com',
        phone='+919876543210',
        name='Test Owner',
        role=UserRole.OWNER,
        hashed_password='hashed_password',
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def consumer_user(db_session):
    """Create a consumer user for testing"""
    user = User(
        email='consumer@example.com',
        phone='+919876543211',
        name='Test Consumer',
        role=UserRole.CONSUMER,
        hashed_password='hashed_password',
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def owner_token(owner_user):
    """Create JWT token for owner user"""
    return TokenService.create_access_token(data={"sub": str(owner_user.id)})


@pytest.fixture
def consumer_token(consumer_user):
    """Create JWT token for consumer user"""
    return TokenService.create_access_token(data={"sub": str(consumer_user.id)})


@pytest.fixture
def test_category(db_session):
    """Create a test category"""
    category = Category(
        name='Test Category',
        slug='test-category'
    )
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)
    return category


@pytest.fixture
def test_product(db_session, owner_user, test_category):
    """Create a test product"""
    product = Product(
        owner_id=owner_user.id,
        title='Test Product',
        description='Test Description',
        category_id=test_category.id,
        sku='TEST-SKU',
        unit_size='1kg',
        consumer_price=Decimal('100.00'),
        distributor_price=Decimal('80.00'),
        stock_quantity=5,  # Low stock
        is_active=True
    )
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)
    return product


@pytest.fixture
def test_address(db_session, consumer_user):
    """Create a test address"""
    address = Address(
        user_id=consumer_user.id,
        name='Test Name',
        phone='+919876543210',
        address_line1='123 Test St',
        city='Test City',
        state='Test State',
        postal_code='123456',
        country='India',
        is_default=True
    )
    db_session.add(address)
    db_session.commit()
    db_session.refresh(address)
    return address


def test_get_dashboard_metrics_success(owner_token, db_session, consumer_user, test_address, test_product):
    """Test getting dashboard metrics successfully"""
    # Create some test data
    # Create a paid order
    order = Order(
        user_id=consumer_user.id,
        order_number='ORD-001',
        total_amount=Decimal('100.00'),
        discount_amount=Decimal('0.00'),
        final_amount=Decimal('100.00'),
        payment_status=PaymentStatus.PAID,
        order_status=OrderStatus.CONFIRMED,
        delivery_address_id=test_address.id
    )
    db_session.add(order)
    
    # Create an active subscription
    subscription = Subscription(
        user_id=consumer_user.id,
        product_id=test_product.id,
        razorpay_subscription_id='sub_test123',
        plan_frequency=SubscriptionFrequency.DAILY,
        start_date=date.today(),
        next_delivery_date=date.today() + timedelta(days=1),
        delivery_address_id=test_address.id,
        status=SubscriptionStatus.ACTIVE
    )
    db_session.add(subscription)
    db_session.commit()
    
    # Make request
    response = client.get(
        "/api/v1/owner/analytics/dashboard",
        headers={"Authorization": f"Bearer {owner_token}"}
    )
    
    # Verify response
    assert response.status_code == 200
    data = response.json()
    
    # Verify all required fields are present
    assert 'total_revenue' in data
    assert 'order_count' in data
    assert 'active_subscriptions' in data
    assert 'low_stock_alerts' in data
    
    # Verify values
    assert data['order_count'] == 1
    assert data['active_subscriptions'] == 1
    assert data['total_revenue'] == 100.00
    assert len(data['low_stock_alerts']) == 1
    assert data['low_stock_alerts'][0]['product_id'] == test_product.id


def test_get_dashboard_metrics_unauthorized(consumer_token):
    """Test that non-owner users cannot access dashboard metrics"""
    response = client.get(
        "/api/v1/owner/analytics/dashboard",
        headers={"Authorization": f"Bearer {consumer_token}"}
    )
    
    assert response.status_code == 403


def test_get_dashboard_metrics_no_auth():
    """Test that unauthenticated users cannot access dashboard metrics"""
    response = client.get("/api/v1/owner/analytics/dashboard")
    
    assert response.status_code == 401


def test_get_revenue_report_success(owner_token, db_session, consumer_user, test_address):
    """Test getting revenue report successfully"""
    # Create orders with different dates
    today = date.today()
    yesterday = today - timedelta(days=1)
    
    # Order from yesterday
    order1 = Order(
        user_id=consumer_user.id,
        order_number='ORD-001',
        total_amount=Decimal('100.00'),
        discount_amount=Decimal('0.00'),
        final_amount=Decimal('100.00'),
        payment_status=PaymentStatus.PAID,
        order_status=OrderStatus.CONFIRMED,
        delivery_address_id=test_address.id,
        created_at=yesterday
    )
    db_session.add(order1)
    
    # Order from today
    order2 = Order(
        user_id=consumer_user.id,
        order_number='ORD-002',
        total_amount=Decimal('200.00'),
        discount_amount=Decimal('0.00'),
        final_amount=Decimal('200.00'),
        payment_status=PaymentStatus.PAID,
        order_status=OrderStatus.CONFIRMED,
        delivery_address_id=test_address.id
    )
    db_session.add(order2)
    db_session.commit()
    
    # Make request without date filters
    response = client.get(
        "/api/v1/owner/analytics/revenue",
        headers={"Authorization": f"Bearer {owner_token}"}
    )
    
    # Verify response
    assert response.status_code == 200
    data = response.json()
    
    assert 'total_revenue' in data
    assert 'total_orders' in data
    assert 'daily_data' in data
    assert data['total_revenue'] == 300.00
    assert data['total_orders'] == 2


def test_get_revenue_report_with_date_filter(owner_token, db_session, consumer_user, test_address):
    """Test getting revenue report with date range filtering"""
    # Create orders with different dates
    today = date.today()
    yesterday = today - timedelta(days=1)
    
    # Order from yesterday
    order1 = Order(
        user_id=consumer_user.id,
        order_number='ORD-001',
        total_amount=Decimal('100.00'),
        discount_amount=Decimal('0.00'),
        final_amount=Decimal('100.00'),
        payment_status=PaymentStatus.PAID,
        order_status=OrderStatus.CONFIRMED,
        delivery_address_id=test_address.id,
        created_at=yesterday
    )
    db_session.add(order1)
    
    # Order from today
    order2 = Order(
        user_id=consumer_user.id,
        order_number='ORD-002',
        total_amount=Decimal('200.00'),
        discount_amount=Decimal('0.00'),
        final_amount=Decimal('200.00'),
        payment_status=PaymentStatus.PAID,
        order_status=OrderStatus.CONFIRMED,
        delivery_address_id=test_address.id
    )
    db_session.add(order2)
    db_session.commit()
    
    # Make request with date filter for today only
    response = client.get(
        f"/api/v1/owner/analytics/revenue?start_date={today}&end_date={today}",
        headers={"Authorization": f"Bearer {owner_token}"}
    )
    
    # Verify response
    assert response.status_code == 200
    data = response.json()
    
    # Should only include today's order
    assert data['total_revenue'] == 200.00
    assert data['total_orders'] == 1


def test_get_revenue_report_unauthorized(consumer_token):
    """Test that non-owner users cannot access revenue report"""
    response = client.get(
        "/api/v1/owner/analytics/revenue",
        headers={"Authorization": f"Bearer {consumer_token}"}
    )
    
    assert response.status_code == 403


def test_get_inventory_status_success(owner_token, db_session, owner_user, test_category):
    """Test getting inventory status successfully"""
    # Create products with different stock levels
    product1 = Product(
        owner_id=owner_user.id,
        title='Product 1',
        description='Description 1',
        category_id=test_category.id,
        sku='SKU-001',
        unit_size='1kg',
        consumer_price=Decimal('100.00'),
        distributor_price=Decimal('80.00'),
        stock_quantity=5,  # Low stock
        is_active=True
    )
    db_session.add(product1)
    
    product2 = Product(
        owner_id=owner_user.id,
        title='Product 2',
        description='Description 2',
        category_id=test_category.id,
        sku='SKU-002',
        unit_size='1kg',
        consumer_price=Decimal('150.00'),
        distributor_price=Decimal('120.00'),
        stock_quantity=50,  # Normal stock
        is_active=True
    )
    db_session.add(product2)
    db_session.commit()
    
    # Make request
    response = client.get(
        "/api/v1/owner/inventory",
        headers={"Authorization": f"Bearer {owner_token}"}
    )
    
    # Verify response
    assert response.status_code == 200
    data = response.json()
    
    assert 'products' in data
    assert len(data['products']) == 2
    
    # Verify product data
    for product in data['products']:
        assert 'product_id' in product
        assert 'title' in product
        assert 'sku' in product
        assert 'stock_quantity' in product
        assert 'is_low_stock' in product


def test_get_inventory_status_with_category_filter(owner_token, db_session, owner_user, test_category):
    """Test getting inventory status with category filtering"""
    # Create another category
    category2 = Category(
        name='Category 2',
        slug='category-2'
    )
    db_session.add(category2)
    db_session.commit()
    db_session.refresh(category2)
    
    # Create products in different categories
    product1 = Product(
        owner_id=owner_user.id,
        title='Product 1',
        description='Description 1',
        category_id=test_category.id,
        sku='SKU-001',
        unit_size='1kg',
        consumer_price=Decimal('100.00'),
        distributor_price=Decimal('80.00'),
        stock_quantity=50,
        is_active=True
    )
    db_session.add(product1)
    
    product2 = Product(
        owner_id=owner_user.id,
        title='Product 2',
        description='Description 2',
        category_id=category2.id,
        sku='SKU-002',
        unit_size='1kg',
        consumer_price=Decimal('150.00'),
        distributor_price=Decimal('120.00'),
        stock_quantity=50,
        is_active=True
    )
    db_session.add(product2)
    db_session.commit()
    
    # Make request with category filter
    response = client.get(
        f"/api/v1/owner/inventory?category_id={test_category.id}",
        headers={"Authorization": f"Bearer {owner_token}"}
    )
    
    # Verify response
    assert response.status_code == 200
    data = response.json()
    
    assert 'products' in data
    assert len(data['products']) == 1
    assert data['products'][0]['category_id'] == test_category.id


def test_get_inventory_status_unauthorized(consumer_token):
    """Test that non-owner users cannot access inventory status"""
    response = client.get(
        "/api/v1/owner/inventory",
        headers={"Authorization": f"Bearer {consumer_token}"}
    )
    
    assert response.status_code == 403


def test_get_inventory_status_no_auth():
    """Test that unauthenticated users cannot access inventory status"""
    response = client.get("/api/v1/owner/inventory")
    
    assert response.status_code == 401


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
