"""Test fixtures and configuration"""
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
os.environ.setdefault('SMS_PROVIDER_API_KEY', 'test-sms-key')
os.environ.setdefault('EMAIL_PROVIDER_API_KEY', 'test-email-key')
os.environ.setdefault('GOOGLE_OAUTH_CLIENT_ID', 'test-google-client-id')
os.environ.setdefault('GOOGLE_OAUTH_CLIENT_SECRET', 'test-google-secret')

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from unittest.mock import Mock, AsyncMock
from app.core.database import Base, get_db
from app.main import app
from app.models import (
    User, Product, Category, Cart, CartItem, AuditLog,
    Order, OrderItem, Address, Subscription, Payment
)
from app.models.enums import UserRole, OrderStatus, PaymentStatus, SubscriptionStatus
from decimal import Decimal
from datetime import datetime, date


# Use in-memory SQLite for tests
TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="function")
def db_engine():
    """Create a test database engine"""
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(db_engine):
    """Create a test database session"""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture
def client(db_session):
    """Create a test client with database override"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db_session):
    """Create a test consumer user"""
    user = User(
        email="test@example.com",
        phone="+919876543210",
        name="Test User",
        role=UserRole.CONSUMER,
        hashed_password="hashed_password",
        is_active=True,
        is_email_verified=True,
        is_phone_verified=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_distributor(db_session):
    """Create a test distributor user"""
    user = User(
        email="distributor@example.com",
        phone="+919876543211",
        name="Test Distributor",
        role=UserRole.DISTRIBUTOR,
        hashed_password="hashed_password",
        is_active=True,
        is_email_verified=True,
        is_phone_verified=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_owner(db_session):
    """Create a test owner user"""
    user = User(
        email="owner@example.com",
        phone="+919876543212",
        name="Test Owner",
        role=UserRole.OWNER,
        hashed_password="hashed_password",
        is_active=True,
        is_email_verified=True,
        is_phone_verified=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_category(db_session):
    """Create a test category"""
    category = Category(
        name="Test Category",
        slug="test-category",
        display_order=1
    )
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)
    return category


@pytest.fixture
def test_product(db_session, test_owner, test_category):
    """Create a test product"""
    product = Product(
        owner_id=test_owner.id,
        title="Test Product",
        description="Test Description",
        category_id=test_category.id,
        sku="TEST-001",
        unit_size="1 Unit",
        consumer_price=Decimal("100.00"),
        distributor_price=Decimal("80.00"),
        stock_quantity=50,
        is_active=True,
        is_subscription_available=False
    )
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)
    return product


@pytest.fixture
def test_address(db_session, test_user):
    """Create a test address"""
    address = Address(
        user_id=test_user.id,
        name="Test User",
        phone="+919876543210",
        address_line1="123 Test Street",
        address_line2="Apt 4B",
        city="Test City",
        state="Test State",
        postal_code="123456",
        country="India",
        is_default=True
    )
    db_session.add(address)
    db_session.commit()
    db_session.refresh(address)
    return address


@pytest.fixture
def test_cart(db_session, test_user):
    """Create a test cart"""
    cart = Cart(
        user_id=test_user.id,
        discount_amount=Decimal("0.00")
    )
    db_session.add(cart)
    db_session.commit()
    db_session.refresh(cart)
    return cart


@pytest.fixture
def test_order(db_session, test_user, test_address):
    """Create a test order"""
    order = Order(
        user_id=test_user.id,
        order_number=f"ORD-{datetime.now().strftime('%Y%m%d')}-001",
        total_amount=Decimal("100.00"),
        discount_amount=Decimal("0.00"),
        final_amount=Decimal("100.00"),
        payment_status=PaymentStatus.PENDING,
        order_status=OrderStatus.PENDING,
        delivery_address_id=test_address.id
    )
    db_session.add(order)
    db_session.commit()
    db_session.refresh(order)
    return order


# Mock fixtures for external services
@pytest.fixture
def mock_razorpay_client():
    """Mock Razorpay client"""
    mock = Mock()
    mock.order.create = Mock(return_value={
        'id': 'order_test123',
        'amount': 10000,
        'currency': 'INR',
        'status': 'created'
    })
    mock.subscription.create = Mock(return_value={
        'id': 'sub_test123',
        'status': 'created'
    })
    mock.utility.verify_payment_signature = Mock(return_value=True)
    return mock


@pytest.fixture
def mock_sms_service():
    """Mock SMS service"""
    mock = AsyncMock()
    mock.send_sms = AsyncMock(return_value=True)
    return mock


@pytest.fixture
def mock_email_service():
    """Mock email service"""
    mock = AsyncMock()
    mock.send_email = AsyncMock(return_value=True)
    return mock


@pytest.fixture
def mock_s3_client():
    """Mock S3 client"""
    mock = Mock()
    mock.upload_fileobj = Mock(return_value=None)
    mock.delete_object = Mock(return_value=None)
    mock.generate_presigned_url = Mock(return_value='https://cdn.example.com/test.jpg')
    return mock


@pytest.fixture
def mock_redis_client():
    """Mock Redis client"""
    mock = AsyncMock()
    mock.get = AsyncMock(return_value=None)
    mock.set = AsyncMock(return_value=True)
    mock.delete = AsyncMock(return_value=True)
    mock.incr = AsyncMock(return_value=1)
    mock.expire = AsyncMock(return_value=True)
    return mock
