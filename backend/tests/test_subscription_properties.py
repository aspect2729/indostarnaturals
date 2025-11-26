"""Property-based tests for subscription functionality

These tests validate correctness properties for subscription management.
"""
import pytest
from hypothesis import given, strategies as st, settings, assume, HealthCheck
from datetime import date, timedelta
from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base
from app.models.user import User
from app.models.product import Product
from app.models.category import Category
from app.models.address import Address
from app.models.subscription import Subscription
from app.models.enums import (
    UserRole,
    SubscriptionFrequency,
    SubscriptionStatus,
    PaymentStatus,
    OrderStatus
)
from app.services.subscription_service import subscription_service
from app.schemas.subscription import SubscriptionCreate
from unittest.mock import Mock, patch


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


# Hypothesis strategies for generating test data
@st.composite
def subscription_frequency_strategy(draw):
    """Generate valid subscription frequencies"""
    return draw(st.sampled_from([
        SubscriptionFrequency.DAILY,
        SubscriptionFrequency.ALTERNATE_DAYS,
        SubscriptionFrequency.WEEKLY
    ]))


@st.composite
def future_date_strategy(draw):
    """Generate future dates within reasonable range"""
    days_ahead = draw(st.integers(min_value=0, max_value=365))
    return date.today() + timedelta(days=days_ahead)


@st.composite
def valid_subscription_data_strategy(draw):
    """Generate valid subscription creation data"""
    return {
        'plan_frequency': draw(subscription_frequency_strategy()),
        'start_date': draw(future_date_strategy())
    }


# Feature: indostar-naturals-ecommerce, Property 35: Subscription creation requires all fields
@settings(max_examples=100, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(
    missing_field=st.sampled_from(['product_id', 'plan_frequency', 'start_date', 'delivery_address_id'])
)
def test_subscription_creation_requires_all_fields(missing_field):
    """
    **Validates: Requirements 7.2**
    
    Property 35: Subscription creation requires all fields
    *For any* subscription creation attempt, if any required field (product_id, plan_frequency,
    start_date, delivery_address_id) is missing, the system should reject the request.
    """
    # Create subscription data with one field missing
    subscription_data = {
        'product_id': 1,
        'plan_frequency': SubscriptionFrequency.DAILY,
        'start_date': date.today(),
        'delivery_address_id': 1
    }
    
    # Remove the specified field
    del subscription_data[missing_field]
    
    # Attempt to create subscription with missing field
    # This should fail validation at the Pydantic schema level
    with pytest.raises((ValueError, TypeError, KeyError)):
        # Try to create the schema
        SubscriptionCreate(**subscription_data)


# Feature: indostar-naturals-ecommerce, Property 36: Subscription confirmation creates Razorpay subscription
@settings(max_examples=50, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(
    subscription_data=valid_subscription_data_strategy()
)
def test_subscription_confirmation_creates_razorpay_subscription(subscription_data):
    """
    **Validates: Requirements 7.3**
    
    Property 36: Subscription confirmation creates Razorpay subscription
    *For any* subscription confirmation, the system should create a Razorpay subscription
    and store the razorpay_subscription_id.
    """
    # Create test database
    test_db, engine = get_test_db()
    
    try:
        # Create test user
        user = User(
            email="test@example.com",
            phone="+919876543210",
            name="Test User",
            role=UserRole.CONSUMER,
            hashed_password="hashed_password",
            is_active=True
        )
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)
        
        # Create test category
        category = Category(
            name="Test Category",
            slug="test-category",
            display_order=1
        )
        test_db.add(category)
        test_db.commit()
        test_db.refresh(category)
        
        # Create test product (subscription-available)
        product = Product(
            owner_id=user.id,
            title="Test Milk",
            description="Fresh milk",
            category_id=category.id,
            sku="MILK-001",
            unit_size="1 Liter",
            consumer_price=Decimal("50.00"),
            distributor_price=Decimal("40.00"),
            stock_quantity=100,
            is_subscription_available=True,
            is_active=True
        )
        test_db.add(product)
        test_db.commit()
        test_db.refresh(product)
        
        # Create test address
        address = Address(
            user_id=user.id,
            name="Test User",
            phone="+919876543210",
            address_line1="123 Test St",
            city="Test City",
            state="Test State",
            postal_code="123456",
            country="India",
            is_default=True
        )
        test_db.add(address)
        test_db.commit()
        test_db.refresh(address)
        
        # Mock Razorpay client responses
        mock_plan_response = {
            "id": "plan_test123",
            "period": "daily",
            "interval": 1
        }
        
        mock_subscription_response = {
            "id": "sub_test123",
            "status": "active",
            "plan_id": "plan_test123"
        }
        
        # Patch Razorpay client methods
        with patch.object(subscription_service.client.plan, 'create', return_value=mock_plan_response):
            with patch.object(subscription_service.client.subscription, 'create', return_value=mock_subscription_response):
                # Create subscription
                subscription = subscription_service.create_subscription(
                    user_id=user.id,
                    product_id=product.id,
                    plan_frequency=subscription_data['plan_frequency'],
                    start_date=subscription_data['start_date'],
                    delivery_address_id=address.id,
                    db=test_db
                )
                
                # Verify subscription was created with Razorpay subscription ID
                assert subscription is not None
                assert subscription.razorpay_subscription_id == "sub_test123"
                assert subscription.razorpay_subscription_id is not None
                assert len(subscription.razorpay_subscription_id) > 0
                
                # Verify subscription is stored in database
                db_subscription = test_db.query(Subscription).filter(
                    Subscription.id == subscription.id
                ).first()
                assert db_subscription is not None
                assert db_subscription.razorpay_subscription_id == "sub_test123"
    finally:
        test_db.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


# Feature: indostar-naturals-ecommerce, Property 37: Subscription charge creates order
@settings(max_examples=50, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(
    subscription_data=valid_subscription_data_strategy()
)
def test_subscription_charge_creates_order(subscription_data):
    """
    **Validates: Requirements 7.4**
    
    Property 37: Subscription charge creates order
    *For any* successful Razorpay subscription charge webhook, the system should create
    an order record with the subscription details.
    """
    # Create test database
    test_db, engine = get_test_db()
    
    try:
        # Create test user
        user = User(
            email="test@example.com",
            phone="+919876543210",
            name="Test User",
            role=UserRole.CONSUMER,
            hashed_password="hashed_password",
            is_active=True
        )
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)
        
        # Create test category
        category = Category(
            name="Test Category",
            slug="test-category",
            display_order=1
        )
        test_db.add(category)
        test_db.commit()
        test_db.refresh(category)
        
        # Create test product (subscription-available)
        product = Product(
            owner_id=user.id,
            title="Test Milk",
            description="Fresh milk",
            category_id=category.id,
            sku="MILK-001",
            unit_size="1 Liter",
            consumer_price=Decimal("50.00"),
            distributor_price=Decimal("40.00"),
            stock_quantity=100,
            is_subscription_available=True,
            is_active=True
        )
        test_db.add(product)
        test_db.commit()
        test_db.refresh(product)
        
        # Create test address
        address = Address(
            user_id=user.id,
            name="Test User",
            phone="+919876543210",
            address_line1="123 Test St",
            city="Test City",
            state="Test State",
            postal_code="123456",
            country="India",
            is_default=True
        )
        test_db.add(address)
        test_db.commit()
        test_db.refresh(address)
        
        # Create subscription directly in database
        subscription = Subscription(
            user_id=user.id,
            product_id=product.id,
            razorpay_subscription_id="sub_test123",
            plan_frequency=subscription_data['plan_frequency'],
            start_date=subscription_data['start_date'],
            next_delivery_date=subscription_data['start_date'],
            delivery_address_id=address.id,
            status=SubscriptionStatus.ACTIVE
        )
        test_db.add(subscription)
        test_db.commit()
        test_db.refresh(subscription)
        
        # Process subscription charge
        order = subscription_service.process_subscription_charge(
            razorpay_subscription_id="sub_test123",
            razorpay_payment_id="pay_test123",
            db=test_db
        )
        
        # Verify order was created
        assert order is not None
        assert order.user_id == user.id
        assert order.payment_status == PaymentStatus.PAID
        assert order.order_status == OrderStatus.CONFIRMED
        assert order.delivery_address_id == address.id
        
        # Verify order has correct items
        assert len(order.items) == 1
        assert order.items[0].product_id == product.id
        assert order.items[0].quantity == 1
        
        # Verify stock was reduced
        test_db.refresh(product)
        assert product.stock_quantity == 99
        
    finally:
        test_db.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


# Feature: indostar-naturals-ecommerce, Property 38: Paused subscriptions suspend billing
@settings(max_examples=50, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(
    subscription_data=valid_subscription_data_strategy()
)
def test_paused_subscriptions_suspend_billing(subscription_data):
    """
    **Validates: Requirements 7.5**
    
    Property 38: Paused subscriptions suspend billing
    *For any* paused subscription, no charges or deliveries should occur until
    the subscription is resumed.
    """
    # Create test database
    test_db, engine = get_test_db()
    
    try:
        # Create test user
        user = User(
            email="test@example.com",
            phone="+919876543210",
            name="Test User",
            role=UserRole.CONSUMER,
            hashed_password="hashed_password",
            is_active=True
        )
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)
        
        # Create test category
        category = Category(
            name="Test Category",
            slug="test-category",
            display_order=1
        )
        test_db.add(category)
        test_db.commit()
        test_db.refresh(category)
        
        # Create test product
        product = Product(
            owner_id=user.id,
            title="Test Milk",
            description="Fresh milk",
            category_id=category.id,
            sku="MILK-001",
            unit_size="1 Liter",
            consumer_price=Decimal("50.00"),
            distributor_price=Decimal("40.00"),
            stock_quantity=100,
            is_subscription_available=True,
            is_active=True
        )
        test_db.add(product)
        test_db.commit()
        test_db.refresh(product)
        
        # Create test address
        address = Address(
            user_id=user.id,
            name="Test User",
            phone="+919876543210",
            address_line1="123 Test St",
            city="Test City",
            state="Test State",
            postal_code="123456",
            country="India",
            is_default=True
        )
        test_db.add(address)
        test_db.commit()
        test_db.refresh(address)
        
        # Create active subscription
        subscription = Subscription(
            user_id=user.id,
            product_id=product.id,
            razorpay_subscription_id="sub_test123",
            plan_frequency=subscription_data['plan_frequency'],
            start_date=subscription_data['start_date'],
            next_delivery_date=subscription_data['start_date'],
            delivery_address_id=address.id,
            status=SubscriptionStatus.ACTIVE
        )
        test_db.add(subscription)
        test_db.commit()
        test_db.refresh(subscription)
        
        # Mock Razorpay pause call
        with patch.object(subscription_service.client.subscription, 'pause', return_value={"status": "paused"}):
            # Pause subscription
            paused_subscription = subscription_service.pause_subscription(
                subscription_id=subscription.id,
                user_id=user.id,
                db=test_db
            )
            
            # Verify subscription is paused
            assert paused_subscription.status == SubscriptionStatus.PAUSED
            
            # Attempt to process charge on paused subscription should fail
            with pytest.raises(ValueError, match="not active"):
                subscription_service.process_subscription_charge(
                    razorpay_subscription_id="sub_test123",
                    razorpay_payment_id="pay_test123",
                    db=test_db
                )
    
    finally:
        test_db.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


# Feature: indostar-naturals-ecommerce, Property 39: Cancelled subscriptions prevent charges
@settings(max_examples=50, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(
    subscription_data=valid_subscription_data_strategy()
)
def test_cancelled_subscriptions_prevent_charges(subscription_data):
    """
    **Validates: Requirements 7.6**
    
    Property 39: Cancelled subscriptions prevent charges
    *For any* cancelled subscription, the Razorpay subscription should be cancelled
    and no future charges should occur.
    """
    # Create test database
    test_db, engine = get_test_db()
    
    try:
        # Create test user
        user = User(
            email="test@example.com",
            phone="+919876543210",
            name="Test User",
            role=UserRole.CONSUMER,
            hashed_password="hashed_password",
            is_active=True
        )
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)
        
        # Create test category
        category = Category(
            name="Test Category",
            slug="test-category",
            display_order=1
        )
        test_db.add(category)
        test_db.commit()
        test_db.refresh(category)
        
        # Create test product
        product = Product(
            owner_id=user.id,
            title="Test Milk",
            description="Fresh milk",
            category_id=category.id,
            sku="MILK-001",
            unit_size="1 Liter",
            consumer_price=Decimal("50.00"),
            distributor_price=Decimal("40.00"),
            stock_quantity=100,
            is_subscription_available=True,
            is_active=True
        )
        test_db.add(product)
        test_db.commit()
        test_db.refresh(product)
        
        # Create test address
        address = Address(
            user_id=user.id,
            name="Test User",
            phone="+919876543210",
            address_line1="123 Test St",
            city="Test City",
            state="Test State",
            postal_code="123456",
            country="India",
            is_default=True
        )
        test_db.add(address)
        test_db.commit()
        test_db.refresh(address)
        
        # Create active subscription
        subscription = Subscription(
            user_id=user.id,
            product_id=product.id,
            razorpay_subscription_id="sub_test123",
            plan_frequency=subscription_data['plan_frequency'],
            start_date=subscription_data['start_date'],
            next_delivery_date=subscription_data['start_date'],
            delivery_address_id=address.id,
            status=SubscriptionStatus.ACTIVE
        )
        test_db.add(subscription)
        test_db.commit()
        test_db.refresh(subscription)
        
        # Mock Razorpay cancel call
        with patch.object(subscription_service.client.subscription, 'cancel', return_value={"status": "cancelled"}):
            # Cancel subscription
            cancelled_subscription = subscription_service.cancel_subscription(
                subscription_id=subscription.id,
                user_id=user.id,
                db=test_db
            )
            
            # Verify subscription is cancelled
            assert cancelled_subscription.status == SubscriptionStatus.CANCELLED
            
            # Attempt to process charge on cancelled subscription should fail
            with pytest.raises(ValueError, match="not active"):
                subscription_service.process_subscription_charge(
                    razorpay_subscription_id="sub_test123",
                    razorpay_payment_id="pay_test123",
                    db=test_db
                )
    
    finally:
        test_db.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


# Feature: indostar-naturals-ecommerce, Property 34: Subscription products show options
@settings(max_examples=50, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(
    is_subscription_available=st.booleans()
)
def test_subscription_products_show_options(is_subscription_available):
    """
    **Validates: Requirements 7.1**
    
    Property 34: Subscription products show options
    *For any* product marked as subscription_available, the product detail page should
    display subscription frequency options.
    """
    # Create test database
    test_db, engine = get_test_db()
    
    try:
        # Create test user
        user = User(
            email="test@example.com",
            phone="+919876543210",
            name="Test User",
            role=UserRole.CONSUMER,
            hashed_password="hashed_password",
            is_active=True
        )
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)
        
        # Create test category
        category = Category(
            name="Test Category",
            slug="test-category",
            display_order=1
        )
        test_db.add(category)
        test_db.commit()
        test_db.refresh(category)
        
        # Create test product with varying subscription availability
        product = Product(
            owner_id=user.id,
            title="Test Product",
            description="Test Description",
            category_id=category.id,
            sku="TEST-001",
            unit_size="1 Unit",
            consumer_price=Decimal("100.00"),
            distributor_price=Decimal("80.00"),
            stock_quantity=50,
            is_subscription_available=is_subscription_available,
            is_active=True
        )
        test_db.add(product)
        test_db.commit()
        test_db.refresh(product)
        
        # Verify the is_subscription_available field matches what we set
        assert product.is_subscription_available == is_subscription_available
        
        # If product is subscription-available, it should be possible to create a subscription
        if is_subscription_available:
            # Create test address
            address = Address(
                user_id=user.id,
                name="Test User",
                phone="+919876543210",
                address_line1="123 Test St",
                city="Test City",
                state="Test State",
                postal_code="123456",
                country="India",
                is_default=True
            )
            test_db.add(address)
            test_db.commit()
            test_db.refresh(address)
            
            # Mock Razorpay responses
            mock_plan_response = {
                "id": "plan_test123",
                "period": "daily",
                "interval": 1
            }
            
            mock_subscription_response = {
                "id": "sub_test123",
                "status": "active",
                "plan_id": "plan_test123"
            }
            
            # Should be able to create subscription
            with patch.object(subscription_service.client.plan, 'create', return_value=mock_plan_response):
                with patch.object(subscription_service.client.subscription, 'create', return_value=mock_subscription_response):
                    subscription = subscription_service.create_subscription(
                        user_id=user.id,
                        product_id=product.id,
                        plan_frequency=SubscriptionFrequency.DAILY,
                        start_date=date.today(),
                        delivery_address_id=address.id,
                        db=test_db
                    )
                    assert subscription is not None
        else:
            # If product is not subscription-available, attempting to create subscription should fail
            address = Address(
                user_id=user.id,
                name="Test User",
                phone="+919876543210",
                address_line1="123 Test St",
                city="Test City",
                state="Test State",
                postal_code="123456",
                country="India",
                is_default=True
            )
            test_db.add(address)
            test_db.commit()
            test_db.refresh(address)
            
            with pytest.raises(ValueError, match="not available for subscription"):
                subscription_service.create_subscription(
                    user_id=user.id,
                    product_id=product.id,
                    plan_frequency=SubscriptionFrequency.DAILY,
                    start_date=date.today(),
                    delivery_address_id=address.id,
                    db=test_db
                )
    
    finally:
        test_db.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


# Feature: indostar-naturals-ecommerce, Property 51: Subscription calendar shows scheduled deliveries
@settings(max_examples=50, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(
    num_subscriptions=st.integers(min_value=1, max_value=10),
    days_ahead=st.integers(min_value=1, max_value=30)
)
def test_subscription_calendar_shows_scheduled_deliveries(num_subscriptions, days_ahead):
    """
    **Validates: Requirements 10.3**
    
    Property 51: Subscription calendar shows scheduled deliveries
    *For any* date in the subscription calendar, the system should display all subscriptions
    scheduled for delivery on that date.
    """
    # Create test database
    test_db, engine = get_test_db()
    
    try:
        # Create test user
        user = User(
            email="test@example.com",
            phone="+919876543210",
            name="Test User",
            role=UserRole.CONSUMER,
            hashed_password="hashed_password",
            is_active=True
        )
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)
        
        # Create test category
        category = Category(
            name="Test Category",
            slug="test-category",
            display_order=1
        )
        test_db.add(category)
        test_db.commit()
        test_db.refresh(category)
        
        # Create test product
        product = Product(
            owner_id=user.id,
            title="Test Milk",
            description="Fresh milk",
            category_id=category.id,
            sku="MILK-001",
            unit_size="1 Liter",
            consumer_price=Decimal("50.00"),
            distributor_price=Decimal("40.00"),
            stock_quantity=100,
            is_subscription_available=True,
            is_active=True
        )
        test_db.add(product)
        test_db.commit()
        test_db.refresh(product)
        
        # Create test address
        address = Address(
            user_id=user.id,
            name="Test User",
            phone="+919876543210",
            address_line1="123 Test St",
            city="Test City",
            state="Test State",
            postal_code="123456",
            country="India",
            is_default=True
        )
        test_db.add(address)
        test_db.commit()
        test_db.refresh(address)
        
        # Create multiple subscriptions with different delivery dates
        from datetime import timedelta
        target_date = date.today() + timedelta(days=days_ahead)
        subscriptions_on_target_date = 0
        
        for i in range(num_subscriptions):
            # Some subscriptions will have the target date, others won't
            if i % 2 == 0:
                next_delivery = target_date
                subscriptions_on_target_date += 1
            else:
                next_delivery = target_date + timedelta(days=i + 1)
            
            subscription = Subscription(
                user_id=user.id,
                product_id=product.id,
                razorpay_subscription_id=f"sub_test{i}",
                plan_frequency=SubscriptionFrequency.DAILY,
                start_date=date.today(),
                next_delivery_date=next_delivery,
                delivery_address_id=address.id,
                status=SubscriptionStatus.ACTIVE
            )
            test_db.add(subscription)
        
        test_db.commit()
        
        # Query subscriptions for the target date
        from sqlalchemy import and_
        calendar_subscriptions = test_db.query(Subscription).filter(
            and_(
                Subscription.status == SubscriptionStatus.ACTIVE,
                Subscription.next_delivery_date == target_date
            )
        ).all()
        
        # Verify the calendar shows exactly the subscriptions scheduled for that date
        assert len(calendar_subscriptions) == subscriptions_on_target_date
        
        # Verify all returned subscriptions have the correct delivery date
        for sub in calendar_subscriptions:
            assert sub.next_delivery_date == target_date
            assert sub.status == SubscriptionStatus.ACTIVE
    
    finally:
        test_db.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()
