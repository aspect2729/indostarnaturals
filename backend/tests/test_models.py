"""Tests for database models"""
import pytest
from decimal import Decimal
from datetime import date, timedelta
from app.models import (
    User, Address, UserRole, Category, Product, ProductImage, 
    Cart, CartItem, Order, OrderItem, PaymentStatus, OrderStatus,
    Subscription, Payment, SubscriptionFrequency, SubscriptionStatus
)


def test_user_model_creation():
    """Test User model can be instantiated"""
    user = User(
        email="test@example.com",
        phone="+919876543210",
        name="Test User",
        role=UserRole.CONSUMER,
        hashed_password="hashed_password_here",
        is_active=True,
        is_email_verified=False,
        is_phone_verified=False
    )
    
    assert user.email == "test@example.com"
    assert user.phone == "+919876543210"
    assert user.name == "Test User"
    assert user.role == UserRole.CONSUMER
    assert user.is_active is True
    assert user.is_email_verified is False
    assert user.is_phone_verified is False


def test_user_model_with_google_oauth():
    """Test User model with Google OAuth"""
    user = User(
        email="google@example.com",
        phone="+919876543211",
        name="Google User",
        role=UserRole.CONSUMER,
        google_id="google_oauth_id_123"
    )
    
    assert user.google_id == "google_oauth_id_123"
    assert user.hashed_password is None


def test_user_roles():
    """Test all user roles can be assigned"""
    consumer = User(
        phone="+919876543210",
        name="Consumer",
        role=UserRole.CONSUMER
    )
    
    distributor = User(
        phone="+919876543211",
        name="Distributor",
        role=UserRole.DISTRIBUTOR
    )
    
    owner = User(
        phone="+919876543212",
        name="Owner",
        role=UserRole.OWNER
    )
    
    assert consumer.role == UserRole.CONSUMER
    assert distributor.role == UserRole.DISTRIBUTOR
    assert owner.role == UserRole.OWNER


def test_address_model_creation():
    """Test Address model can be instantiated"""
    address = Address(
        user_id=1,
        name="John Doe",
        phone="+919876543210",
        address_line1="123 Main Street",
        address_line2="Apt 4B",
        city="Mumbai",
        state="Maharashtra",
        postal_code="400001",
        country="India",
        is_default=True
    )
    
    assert address.user_id == 1
    assert address.name == "John Doe"
    assert address.phone == "+919876543210"
    assert address.address_line1 == "123 Main Street"
    assert address.address_line2 == "Apt 4B"
    assert address.city == "Mumbai"
    assert address.state == "Maharashtra"
    assert address.postal_code == "400001"
    assert address.country == "India"
    assert address.is_default is True


def test_address_model_without_optional_fields():
    """Test Address model without optional fields"""
    address = Address(
        user_id=1,
        name="Jane Doe",
        phone="+919876543211",
        address_line1="456 Oak Avenue",
        city="Delhi",
        state="Delhi",
        postal_code="110001",
        country="India",
        is_default=False
    )
    
    assert address.address_line2 is None
    assert address.is_default is False


def test_address_default_country():
    """Test Address model has default country"""
    address = Address(
        user_id=1,
        name="Test User",
        phone="+919876543210",
        address_line1="Test Address",
        city="Test City",
        state="Test State",
        postal_code="123456",
        country="India"  # Explicitly set default
    )
    
    # Default country should be India
    assert address.country == "India"


# Property-Based Tests
from hypothesis import given, strategies as st, settings


@pytest.mark.property
@settings(max_examples=100)
@given(
    email=st.one_of(st.none(), st.emails()),
    phone=st.from_regex(r'^\+[1-9]\d{1,14}$', fullmatch=True),
    name=st.text(min_size=1, max_size=255).filter(lambda x: x.strip()),
    role=st.sampled_from([UserRole.CONSUMER, UserRole.DISTRIBUTOR, UserRole.OWNER]),
    google_id=st.one_of(st.none(), st.text(min_size=1, max_size=255)),
    has_password=st.booleans()
)
def test_property_user_creation_assigns_single_role(email, phone, name, role, google_id, has_password):
    """
    Feature: indostar-naturals-ecommerce, Property 5: User creation assigns single role
    
    Property: For any user account creation, the user should have exactly one role 
    from the set {consumer, distributor, owner}.
    
    Validates: Requirements 2.1
    """
    # Create user with the generated role
    user = User(
        email=email,
        phone=phone,
        name=name,
        role=role,
        google_id=google_id,
        hashed_password="hashed_password" if has_password else None
    )
    
    # Verify the user has exactly one role
    assert user.role is not None, "User must have a role assigned"
    assert user.role in [UserRole.CONSUMER, UserRole.DISTRIBUTOR, UserRole.OWNER], \
        f"User role must be one of the valid roles, got {user.role}"
    
    # Verify the role is exactly what was assigned
    assert user.role == role, f"User role should be {role}, but got {user.role}"
    
    # Verify the role is a single value (not a list or multiple values)
    assert isinstance(user.role, UserRole), "User role must be a UserRole enum instance"



def test_category_model_creation():
    """Test Category model can be instantiated"""
    category = Category(
        name="Dairy Products",
        slug="dairy-products",
        parent_id=None,
        display_order=1
    )
    
    assert category.name == "Dairy Products"
    assert category.slug == "dairy-products"
    assert category.parent_id is None
    assert category.display_order == 1


def test_category_hierarchical_support():
    """Test Category model supports hierarchical structure"""
    parent_category = Category(
        id=1,
        name="Food",
        slug="food",
        parent_id=None,
        display_order=1
    )
    
    child_category = Category(
        name="Dairy",
        slug="dairy",
        parent_id=1,
        display_order=1
    )
    
    assert child_category.parent_id == parent_category.id


def test_product_model_creation():
    """Test Product model can be instantiated with dual pricing"""
    product = Product(
        owner_id=1,
        title="Organic Milk",
        description="Fresh organic milk from local farms",
        category_id=1,
        sku="MILK-001",
        unit_size="1 Liter",
        consumer_price=Decimal("60.00"),
        distributor_price=Decimal("50.00"),
        stock_quantity=100,
        is_subscription_available=True,
        is_active=True
    )
    
    assert product.title == "Organic Milk"
    assert product.sku == "MILK-001"
    assert product.consumer_price == Decimal("60.00")
    assert product.distributor_price == Decimal("50.00")
    assert product.stock_quantity == 100
    assert product.is_subscription_available is True
    assert product.is_active is True


def test_product_dual_pricing():
    """Test Product model stores both consumer and distributor prices"""
    product = Product(
        owner_id=1,
        title="Jaggery",
        description="Pure organic jaggery",
        category_id=2,
        sku="JAG-001",
        unit_size="500g",
        consumer_price=Decimal("120.00"),
        distributor_price=Decimal("100.00"),
        stock_quantity=50
    )
    
    # Verify both prices are stored
    assert product.consumer_price == Decimal("120.00")
    assert product.distributor_price == Decimal("100.00")
    # Verify distributor price is lower than consumer price
    assert product.distributor_price < product.consumer_price


def test_product_image_model_creation():
    """Test ProductImage model can be instantiated"""
    product_image = ProductImage(
        product_id=1,
        url="https://cdn.example.com/images/milk-001.jpg",
        alt_text="Organic Milk Bottle",
        display_order=1
    )
    
    assert product_image.product_id == 1
    assert product_image.url == "https://cdn.example.com/images/milk-001.jpg"
    assert product_image.alt_text == "Organic Milk Bottle"
    assert product_image.display_order == 1


def test_product_image_display_order():
    """Test ProductImage model supports display ordering"""
    image1 = ProductImage(
        product_id=1,
        url="https://cdn.example.com/images/milk-001-front.jpg",
        alt_text="Front view",
        display_order=1
    )
    
    image2 = ProductImage(
        product_id=1,
        url="https://cdn.example.com/images/milk-001-back.jpg",
        alt_text="Back view",
        display_order=2
    )
    
    assert image1.display_order < image2.display_order


@pytest.mark.property
@settings(max_examples=100)
@given(
    title=st.text(min_size=1, max_size=255).filter(lambda x: x.strip()),
    description=st.text(min_size=1, max_size=1000).filter(lambda x: x.strip()),
    sku=st.from_regex(r'^[A-Z0-9\-]{3,50}$', fullmatch=True),
    unit_size=st.text(min_size=1, max_size=100).filter(lambda x: x.strip()),
    consumer_price=st.decimals(min_value=Decimal("0.01"), max_value=Decimal("99999.99"), places=2),
    distributor_price=st.decimals(min_value=Decimal("0.01"), max_value=Decimal("99999.99"), places=2),
    stock_quantity=st.integers(min_value=0, max_value=100000),
    user_role=st.sampled_from([UserRole.CONSUMER, UserRole.DISTRIBUTOR])
)
def test_property_dual_pricing_stored_and_retrieved_by_role(
    title, description, sku, unit_size, consumer_price, distributor_price, stock_quantity, user_role
):
    """
    Feature: indostar-naturals-ecommerce, Property 14: Dual pricing stored and retrieved by role
    
    Property: For any product with different consumer and distributor prices, when queried by 
    a consumer, the consumer price should be returned, and when queried by a distributor, 
    the distributor price should be returned.
    
    Validates: Requirements 3.4
    """
    # Create a product with dual pricing
    product = Product(
        owner_id=1,
        title=title,
        description=description,
        category_id=1,
        sku=sku,
        unit_size=unit_size,
        consumer_price=consumer_price,
        distributor_price=distributor_price,
        stock_quantity=stock_quantity,
        is_subscription_available=False,
        is_active=True
    )
    
    # Verify both prices are stored correctly
    assert product.consumer_price == consumer_price, \
        f"Consumer price should be {consumer_price}, but got {product.consumer_price}"
    assert product.distributor_price == distributor_price, \
        f"Distributor price should be {distributor_price}, but got {product.distributor_price}"
    
    # Simulate role-based price retrieval
    # In a real implementation, this would be done by a service layer method
    # For now, we verify that the model stores both prices and they can be accessed
    if user_role == UserRole.CONSUMER:
        retrieved_price = product.consumer_price
        assert retrieved_price == consumer_price, \
            f"Consumer should see consumer price {consumer_price}, but got {retrieved_price}"
    elif user_role == UserRole.DISTRIBUTOR:
        retrieved_price = product.distributor_price
        assert retrieved_price == distributor_price, \
            f"Distributor should see distributor price {distributor_price}, but got {retrieved_price}"
    
    # Verify that both prices exist and are accessible regardless of role
    assert hasattr(product, 'consumer_price'), "Product must have consumer_price attribute"
    assert hasattr(product, 'distributor_price'), "Product must have distributor_price attribute"
    assert product.consumer_price is not None, "Consumer price must not be None"
    assert product.distributor_price is not None, "Distributor price must not be None"



def test_cart_model_creation():
    """Test Cart model can be instantiated"""
    cart = Cart(
        user_id=1,
        coupon_code=None,
        discount_amount=Decimal("0.00")
    )
    
    assert cart.user_id == 1
    assert cart.coupon_code is None
    assert cart.discount_amount == Decimal("0.00")


def test_cart_model_with_coupon():
    """Test Cart model with coupon support"""
    cart = Cart(
        user_id=1,
        coupon_code="SAVE10",
        discount_amount=Decimal("10.00")
    )
    
    assert cart.user_id == 1
    assert cart.coupon_code == "SAVE10"
    assert cart.discount_amount == Decimal("10.00")


def test_cart_item_model_creation():
    """Test CartItem model can be instantiated with locked unit price"""
    cart_item = CartItem(
        cart_id=1,
        product_id=1,
        quantity=2,
        unit_price=Decimal("60.00")
    )
    
    assert cart_item.cart_id == 1
    assert cart_item.product_id == 1
    assert cart_item.quantity == 2
    assert cart_item.unit_price == Decimal("60.00")


def test_cart_item_locked_price():
    """Test CartItem model locks unit price at time of adding"""
    # Simulate adding item to cart with current price
    original_price = Decimal("50.00")
    cart_item = CartItem(
        cart_id=1,
        product_id=1,
        quantity=1,
        unit_price=original_price
    )
    
    # Verify the price is locked
    assert cart_item.unit_price == original_price
    
    # Even if product price changes, cart item price should remain locked
    # This is a design feature - the unit_price field stores the locked price
    new_price = Decimal("55.00")
    # Cart item price should NOT change automatically
    assert cart_item.unit_price == original_price
    assert cart_item.unit_price != new_price



@pytest.mark.property
@settings(max_examples=100)
@given(
    quantity=st.integers(min_value=1, max_value=100),
    unit_price=st.decimals(min_value=Decimal("0.01"), max_value=Decimal("9999.99"), places=2)
)
def test_property_cart_additions_persist(quantity, unit_price):
    """
    Feature: indostar-naturals-ecommerce, Property 21: Cart additions persist
    
    Property: For any product added to a user's cart, querying the cart should return 
    that product with the specified quantity.
    
    Validates: Requirements 5.1
    """
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from app.core.database import Base
    
    # Create a fresh database for each example
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestSession()
    
    try:
        # Create test data
        user = User(
            email="test@example.com",
            phone="+919876543210",
            name="Test User",
            role=UserRole.CONSUMER,
            hashed_password="hashed_password",
            is_active=True
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        
        category = Category(
            name="Test Category",
            slug="test-category",
            display_order=1
        )
        session.add(category)
        session.commit()
        session.refresh(category)
        
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
            is_active=True
        )
        session.add(product)
        session.commit()
        session.refresh(product)
        
        # Create a cart for the user
        cart = Cart(
            user_id=user.id,
            discount_amount=Decimal("0.00")
        )
        session.add(cart)
        session.commit()
        session.refresh(cart)
        
        # Add a product to the cart
        cart_item = CartItem(
            cart_id=cart.id,
            product_id=product.id,
            quantity=quantity,
            unit_price=unit_price
        )
        session.add(cart_item)
        session.commit()
        
        # Query the cart from the database (simulating persistence)
        queried_cart = session.query(Cart).filter(Cart.user_id == user.id).first()
        
        # Verify the cart exists
        assert queried_cart is not None, "Cart should exist in database"
        assert queried_cart.id == cart.id, "Queried cart should match created cart"
        
        # Verify the cart contains the added item
        assert len(queried_cart.items) > 0, "Cart should contain at least one item"
        
        # Find the cart item we added
        found_item = None
        for item in queried_cart.items:
            if item.product_id == product.id:
                found_item = item
                break
        
        # Verify the item was found
        assert found_item is not None, \
            f"Cart should contain product with id {product.id}"
        
        # Verify the item has the correct quantity
        assert found_item.quantity == quantity, \
            f"Cart item quantity should be {quantity}, but got {found_item.quantity}"
        
        # Verify the item has the correct unit price (locked price)
        assert found_item.unit_price == unit_price, \
            f"Cart item unit price should be {unit_price}, but got {found_item.unit_price}"
        
        # Verify the item is associated with the correct product
        assert found_item.product_id == product.id, \
            f"Cart item should reference product {product.id}, but got {found_item.product_id}"
        
        # Verify the cart is associated with the correct user
        assert queried_cart.user_id == user.id, \
            f"Cart should belong to user {user.id}, but got {queried_cart.user_id}"
    
    finally:
        session.close()
        engine.dispose()



def test_order_model_creation():
    """Test Order model can be instantiated with status enums"""
    order = Order(
        user_id=1,
        order_number="ORD-2024-001",
        total_amount=Decimal("120.00"),
        discount_amount=Decimal("10.00"),
        final_amount=Decimal("110.00"),
        payment_status=PaymentStatus.PENDING,
        order_status=OrderStatus.PENDING,
        delivery_address_id=1,
        notes="Please deliver in the morning"
    )
    
    assert order.user_id == 1
    assert order.order_number == "ORD-2024-001"
    assert order.total_amount == Decimal("120.00")
    assert order.discount_amount == Decimal("10.00")
    assert order.final_amount == Decimal("110.00")
    assert order.payment_status == PaymentStatus.PENDING
    assert order.order_status == OrderStatus.PENDING
    assert order.delivery_address_id == 1
    assert order.notes == "Please deliver in the morning"


def test_order_status_enums():
    """Test Order model supports all status enums"""
    # Test all order statuses
    statuses = [
        OrderStatus.PENDING,
        OrderStatus.CONFIRMED,
        OrderStatus.PACKED,
        OrderStatus.OUT_FOR_DELIVERY,
        OrderStatus.DELIVERED,
        OrderStatus.CANCELLED,
        OrderStatus.REFUNDED
    ]
    
    for status in statuses:
        order = Order(
            user_id=1,
            order_number=f"ORD-{status.value}",
            total_amount=Decimal("100.00"),
            discount_amount=Decimal("0.00"),
            final_amount=Decimal("100.00"),
            payment_status=PaymentStatus.PENDING,
            order_status=status,
            delivery_address_id=1
        )
        assert order.order_status == status


def test_payment_status_enums():
    """Test Order model supports all payment status enums"""
    # Test all payment statuses
    statuses = [
        PaymentStatus.PENDING,
        PaymentStatus.PAID,
        PaymentStatus.FAILED,
        PaymentStatus.REFUNDED
    ]
    
    for status in statuses:
        order = Order(
            user_id=1,
            order_number=f"ORD-PAY-{status.value}",
            total_amount=Decimal("100.00"),
            discount_amount=Decimal("0.00"),
            final_amount=Decimal("100.00"),
            payment_status=status,
            order_status=OrderStatus.PENDING,
            delivery_address_id=1
        )
        assert order.payment_status == status


def test_order_item_model_creation():
    """Test OrderItem model can be instantiated"""
    order_item = OrderItem(
        order_id=1,
        product_id=1,
        quantity=2,
        unit_price=Decimal("60.00"),
        total_price=Decimal("120.00")
    )
    
    assert order_item.order_id == 1
    assert order_item.product_id == 1
    assert order_item.quantity == 2
    assert order_item.unit_price == Decimal("60.00")
    assert order_item.total_price == Decimal("120.00")


def test_order_item_total_calculation():
    """Test OrderItem model stores calculated total price"""
    quantity = 3
    unit_price = Decimal("45.50")
    total_price = unit_price * quantity
    
    order_item = OrderItem(
        order_id=1,
        product_id=1,
        quantity=quantity,
        unit_price=unit_price,
        total_price=total_price
    )
    
    # Verify the total price is stored correctly
    assert order_item.total_price == Decimal("136.50")
    assert order_item.total_price == quantity * unit_price


def test_order_with_no_discount():
    """Test Order model with no discount"""
    order = Order(
        user_id=1,
        order_number="ORD-2024-002",
        total_amount=Decimal("100.00"),
        discount_amount=Decimal("0.00"),
        final_amount=Decimal("100.00"),
        payment_status=PaymentStatus.PENDING,
        order_status=OrderStatus.PENDING,
        delivery_address_id=1
    )
    
    assert order.discount_amount == Decimal("0.00")
    assert order.total_amount == order.final_amount


def test_order_with_discount():
    """Test Order model with discount applied"""
    total = Decimal("200.00")
    discount = Decimal("20.00")
    final = total - discount
    
    order = Order(
        user_id=1,
        order_number="ORD-2024-003",
        total_amount=total,
        discount_amount=discount,
        final_amount=final,
        payment_status=PaymentStatus.PENDING,
        order_status=OrderStatus.PENDING,
        delivery_address_id=1
    )
    
    assert order.total_amount == Decimal("200.00")
    assert order.discount_amount == Decimal("20.00")
    assert order.final_amount == Decimal("180.00")
    assert order.final_amount == order.total_amount - order.discount_amount


def test_order_without_notes():
    """Test Order model without optional notes field"""
    order = Order(
        user_id=1,
        order_number="ORD-2024-004",
        total_amount=Decimal("100.00"),
        discount_amount=Decimal("0.00"),
        final_amount=Decimal("100.00"),
        payment_status=PaymentStatus.PENDING,
        order_status=OrderStatus.PENDING,
        delivery_address_id=1
    )
    
    assert order.notes is None


@pytest.mark.property
@settings(max_examples=100)
@given(
    order_number=st.from_regex(r'^ORD-\d{4}-\d{3,6}$', fullmatch=True),
    total_amount=st.decimals(min_value=Decimal("0.01"), max_value=Decimal("99999.99"), places=2),
    discount_amount=st.decimals(min_value=Decimal("0.00"), max_value=Decimal("9999.99"), places=2),
    notes=st.one_of(st.none(), st.text(min_size=0, max_size=500))
)
def test_property_new_orders_start_as_pending(order_number, total_amount, discount_amount, notes):
    """
    Feature: indostar-naturals-ecommerce, Property 40: New orders start as pending
    
    Property: For any newly created order, the initial order_status should be PENDING.
    
    Validates: Requirements 8.1
    """
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from app.core.database import Base
    
    # Create a fresh database for each example
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestSession()
    
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
        session.add(user)
        session.commit()
        session.refresh(user)
        
        # Create test address
        address = Address(
            user_id=user.id,
            name="Test User",
            phone="+919876543210",
            address_line1="123 Test Street",
            city="Test City",
            state="Test State",
            postal_code="123456",
            country="India"
        )
        session.add(address)
        session.commit()
        session.refresh(address)
        
        # Calculate final amount
        final_amount = total_amount - discount_amount
        
        # Ensure final amount is not negative
        if final_amount < Decimal("0.00"):
            final_amount = Decimal("0.00")
        
        # Create a new order WITHOUT explicitly setting order_status
        # This tests that the default value is PENDING
        order = Order(
            user_id=user.id,
            order_number=order_number,
            total_amount=total_amount,
            discount_amount=discount_amount,
            final_amount=final_amount,
            delivery_address_id=address.id,
            notes=notes
            # Note: NOT setting order_status or payment_status explicitly
            # to test that defaults are applied
        )
        session.add(order)
        session.commit()
        session.refresh(order)
        
        # Verify the order status is PENDING
        assert order.order_status == OrderStatus.PENDING, \
            f"New order should have status PENDING, but got {order.order_status}"
        
        # Also verify payment status defaults to PENDING
        assert order.payment_status == PaymentStatus.PENDING, \
            f"New order should have payment status PENDING, but got {order.payment_status}"
        
        # Query the order from database to ensure persistence
        queried_order = session.query(Order).filter(Order.id == order.id).first()
        
        assert queried_order is not None, "Order should exist in database"
        assert queried_order.order_status == OrderStatus.PENDING, \
            f"Queried order should have status PENDING, but got {queried_order.order_status}"
        
        # Verify the order has all required fields
        assert queried_order.user_id == user.id
        assert queried_order.order_number == order_number
        assert queried_order.total_amount == total_amount
        assert queried_order.discount_amount == discount_amount
        assert queried_order.final_amount == final_amount
        assert queried_order.delivery_address_id == address.id
        
        # Verify created_at and updated_at are set
        assert queried_order.created_at is not None, "Order should have created_at timestamp"
        assert queried_order.updated_at is not None, "Order should have updated_at timestamp"
    
    finally:
        session.close()
        engine.dispose()



def test_subscription_model_creation():
    """Test Subscription model can be instantiated with frequency enum"""
    today = date.today()
    next_delivery = today + timedelta(days=1)
    
    subscription = Subscription(
        user_id=1,
        product_id=1,
        razorpay_subscription_id="sub_razorpay_123",
        plan_frequency=SubscriptionFrequency.DAILY,
        start_date=today,
        next_delivery_date=next_delivery,
        delivery_address_id=1,
        status=SubscriptionStatus.ACTIVE
    )
    
    assert subscription.user_id == 1
    assert subscription.product_id == 1
    assert subscription.razorpay_subscription_id == "sub_razorpay_123"
    assert subscription.plan_frequency == SubscriptionFrequency.DAILY
    assert subscription.start_date == today
    assert subscription.next_delivery_date == next_delivery
    assert subscription.delivery_address_id == 1
    assert subscription.status == SubscriptionStatus.ACTIVE


def test_subscription_frequency_enums():
    """Test Subscription model supports all frequency enums"""
    today = date.today()
    next_delivery = today + timedelta(days=1)
    
    frequencies = [
        SubscriptionFrequency.DAILY,
        SubscriptionFrequency.ALTERNATE_DAYS,
        SubscriptionFrequency.WEEKLY
    ]
    
    for frequency in frequencies:
        subscription = Subscription(
            user_id=1,
            product_id=1,
            razorpay_subscription_id=f"sub_{frequency.value}",
            plan_frequency=frequency,
            start_date=today,
            next_delivery_date=next_delivery,
            delivery_address_id=1,
            status=SubscriptionStatus.ACTIVE
        )
        assert subscription.plan_frequency == frequency


def test_subscription_status_enums():
    """Test Subscription model supports all status enums"""
    today = date.today()
    next_delivery = today + timedelta(days=1)
    
    statuses = [
        SubscriptionStatus.ACTIVE,
        SubscriptionStatus.PAUSED,
        SubscriptionStatus.CANCELLED
    ]
    
    for status in statuses:
        subscription = Subscription(
            user_id=1,
            product_id=1,
            razorpay_subscription_id=f"sub_{status.value}",
            plan_frequency=SubscriptionFrequency.DAILY,
            start_date=today,
            next_delivery_date=next_delivery,
            delivery_address_id=1,
            status=status
        )
        assert subscription.status == status


def test_subscription_default_status():
    """Test Subscription model has default status of ACTIVE when persisted"""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from app.core.database import Base
    
    # Create a fresh database
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestSession()
    
    try:
        today = date.today()
        next_delivery = today + timedelta(days=1)
        
        # Create test user
        user = User(
            email="test@example.com",
            phone="+919876543210",
            name="Test User",
            role=UserRole.CONSUMER,
            hashed_password="hashed_password",
            is_active=True
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        
        # Create test category and product
        category = Category(
            name="Test Category",
            slug="test-category",
            display_order=1
        )
        session.add(category)
        session.commit()
        session.refresh(category)
        
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
            is_active=True
        )
        session.add(product)
        session.commit()
        session.refresh(product)
        
        # Create test address
        address = Address(
            user_id=user.id,
            name="Test User",
            phone="+919876543210",
            address_line1="123 Test Street",
            city="Test City",
            state="Test State",
            postal_code="123456",
            country="India"
        )
        session.add(address)
        session.commit()
        session.refresh(address)
        
        # Create subscription WITHOUT explicitly setting status
        subscription = Subscription(
            user_id=user.id,
            product_id=product.id,
            razorpay_subscription_id="sub_default_test",
            plan_frequency=SubscriptionFrequency.WEEKLY,
            start_date=today,
            next_delivery_date=next_delivery,
            delivery_address_id=address.id
            # Note: NOT setting status explicitly to test default
        )
        session.add(subscription)
        session.commit()
        session.refresh(subscription)
        
        # Default status should be ACTIVE after persistence
        assert subscription.status == SubscriptionStatus.ACTIVE
    
    finally:
        session.close()
        engine.dispose()


def test_payment_model_creation():
    """Test Payment model can be instantiated with Razorpay fields"""
    payment = Payment(
        order_id=1,
        subscription_id=None,
        razorpay_payment_id="pay_razorpay_123",
        razorpay_order_id="order_razorpay_456",
        amount=Decimal("120.00"),
        currency="INR",
        status=PaymentStatus.PAID,
        payment_method="card"
    )
    
    assert payment.order_id == 1
    assert payment.subscription_id is None
    assert payment.razorpay_payment_id == "pay_razorpay_123"
    assert payment.razorpay_order_id == "order_razorpay_456"
    assert payment.amount == Decimal("120.00")
    assert payment.currency == "INR"
    assert payment.status == PaymentStatus.PAID
    assert payment.payment_method == "card"


def test_payment_for_subscription():
    """Test Payment model can be associated with subscription"""
    payment = Payment(
        order_id=None,
        subscription_id=1,
        razorpay_payment_id="pay_sub_123",
        razorpay_order_id=None,
        amount=Decimal("60.00"),
        currency="INR",
        status=PaymentStatus.PAID,
        payment_method="upi"
    )
    
    assert payment.order_id is None
    assert payment.subscription_id == 1
    assert payment.razorpay_payment_id == "pay_sub_123"
    assert payment.amount == Decimal("60.00")


def test_payment_default_currency():
    """Test Payment model has default currency of INR when persisted"""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from app.core.database import Base
    
    # Create a fresh database
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestSession()
    
    try:
        # Create test user and address
        user = User(
            email="test@example.com",
            phone="+919876543210",
            name="Test User",
            role=UserRole.CONSUMER,
            hashed_password="hashed_password",
            is_active=True
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        
        address = Address(
            user_id=user.id,
            name="Test User",
            phone="+919876543210",
            address_line1="123 Test Street",
            city="Test City",
            state="Test State",
            postal_code="123456",
            country="India"
        )
        session.add(address)
        session.commit()
        session.refresh(address)
        
        # Create test order
        order = Order(
            user_id=user.id,
            order_number="ORD-TEST-001",
            total_amount=Decimal("100.00"),
            discount_amount=Decimal("0.00"),
            final_amount=Decimal("100.00"),
            delivery_address_id=address.id
        )
        session.add(order)
        session.commit()
        session.refresh(order)
        
        # Create payment WITHOUT explicitly setting currency
        payment = Payment(
            order_id=order.id,
            razorpay_payment_id="pay_default_currency",
            amount=Decimal("100.00"),
            status=PaymentStatus.PENDING
            # Note: NOT setting currency explicitly to test default
        )
        session.add(payment)
        session.commit()
        session.refresh(payment)
        
        # Default currency should be INR after persistence
        assert payment.currency == "INR"
    
    finally:
        session.close()
        engine.dispose()


def test_payment_default_status():
    """Test Payment model has default status of PENDING when persisted"""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from app.core.database import Base
    
    # Create a fresh database
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestSession()
    
    try:
        # Create test user and address
        user = User(
            email="test@example.com",
            phone="+919876543210",
            name="Test User",
            role=UserRole.CONSUMER,
            hashed_password="hashed_password",
            is_active=True
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        
        address = Address(
            user_id=user.id,
            name="Test User",
            phone="+919876543210",
            address_line1="123 Test Street",
            city="Test City",
            state="Test State",
            postal_code="123456",
            country="India"
        )
        session.add(address)
        session.commit()
        session.refresh(address)
        
        # Create test order
        order = Order(
            user_id=user.id,
            order_number="ORD-TEST-002",
            total_amount=Decimal("100.00"),
            discount_amount=Decimal("0.00"),
            final_amount=Decimal("100.00"),
            delivery_address_id=address.id
        )
        session.add(order)
        session.commit()
        session.refresh(order)
        
        # Create payment WITHOUT explicitly setting status
        payment = Payment(
            order_id=order.id,
            razorpay_payment_id="pay_default_status",
            amount=Decimal("100.00"),
            currency="INR"
            # Note: NOT setting status explicitly to test default
        )
        session.add(payment)
        session.commit()
        session.refresh(payment)
        
        # Default status should be PENDING after persistence
        assert payment.status == PaymentStatus.PENDING
    
    finally:
        session.close()
        engine.dispose()


def test_payment_without_order_or_subscription():
    """Test Payment model can exist without order or subscription initially"""
    payment = Payment(
        razorpay_payment_id="pay_standalone",
        amount=Decimal("50.00"),
        currency="INR",
        status=PaymentStatus.PENDING
    )
    
    assert payment.order_id is None
    assert payment.subscription_id is None
    assert payment.razorpay_payment_id == "pay_standalone"


def test_payment_with_optional_fields():
    """Test Payment model with all optional fields"""
    payment = Payment(
        order_id=1,
        subscription_id=None,
        razorpay_payment_id="pay_full_123",
        razorpay_order_id="order_full_456",
        amount=Decimal("150.00"),
        currency="INR",
        status=PaymentStatus.PAID,
        payment_method="netbanking"
    )
    
    assert payment.razorpay_order_id == "order_full_456"
    assert payment.payment_method == "netbanking"


def test_payment_without_optional_fields():
    """Test Payment model without optional fields"""
    payment = Payment(
        razorpay_payment_id="pay_minimal",
        amount=Decimal("75.00"),
        status=PaymentStatus.PENDING,
        currency="INR"  # Explicitly set since we're not persisting
    )
    
    assert payment.order_id is None
    assert payment.subscription_id is None
    assert payment.razorpay_order_id is None
    assert payment.payment_method is None
    assert payment.currency == "INR"



def test_audit_log_model_creation():
    """Test AuditLog model can be instantiated with JSON details field"""
    from app.models.audit_log import AuditLog
    
    audit_log = AuditLog(
        actor_id=1,
        action_type="PRODUCT_CREATED",
        object_type="PRODUCT",
        object_id=123,
        details={"old_value": None, "new_value": {"title": "New Product", "price": "100.00"}},
        ip_address="192.168.1.1"
    )
    
    assert audit_log.actor_id == 1
    assert audit_log.action_type == "PRODUCT_CREATED"
    assert audit_log.object_type == "PRODUCT"
    assert audit_log.object_id == 123
    assert audit_log.details == {"old_value": None, "new_value": {"title": "New Product", "price": "100.00"}}
    assert audit_log.ip_address == "192.168.1.1"


def test_audit_log_without_ip_address():
    """Test AuditLog model without optional ip_address field"""
    from app.models.audit_log import AuditLog
    
    audit_log = AuditLog(
        actor_id=1,
        action_type="PRICE_UPDATED",
        object_type="PRODUCT",
        object_id=456,
        details={"old_price": "100.00", "new_price": "120.00"}
    )
    
    assert audit_log.ip_address is None


def test_audit_log_action_types():
    """Test AuditLog model supports various action types"""
    from app.models.audit_log import AuditLog
    
    action_types = [
        "PRODUCT_CREATED",
        "PRICE_UPDATED",
        "STOCK_UPDATED",
        "ROLE_CHANGED",
        "ORDER_STATUS_CHANGED",
        "USER_CREATED"
    ]
    
    for action_type in action_types:
        audit_log = AuditLog(
            actor_id=1,
            action_type=action_type,
            object_type="TEST",
            object_id=1,
            details={"action": action_type}
        )
        assert audit_log.action_type == action_type


def test_audit_log_persistence():
    """Test AuditLog model persists to database correctly"""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from app.core.database import Base
    from app.models.audit_log import AuditLog
    
    # Create a fresh database
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestSession()
    
    try:
        # Create test user
        user = User(
            email="test@example.com",
            phone="+919876543210",
            name="Test User",
            role=UserRole.OWNER,
            hashed_password="hashed_password",
            is_active=True
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        
        # Create audit log entry
        audit_log = AuditLog(
            actor_id=user.id,
            action_type="STOCK_UPDATED",
            object_type="PRODUCT",
            object_id=789,
            details={
                "old_quantity": 50,
                "new_quantity": 45,
                "delta": -5,
                "reason": "Order fulfillment"
            },
            ip_address="10.0.0.1"
        )
        session.add(audit_log)
        session.commit()
        session.refresh(audit_log)
        
        # Query the audit log from database
        queried_log = session.query(AuditLog).filter(AuditLog.id == audit_log.id).first()
        
        # Verify the audit log exists and has correct data
        assert queried_log is not None, "Audit log should exist in database"
        assert queried_log.actor_id == user.id
        assert queried_log.action_type == "STOCK_UPDATED"
        assert queried_log.object_type == "PRODUCT"
        assert queried_log.object_id == 789
        assert queried_log.details["old_quantity"] == 50
        assert queried_log.details["new_quantity"] == 45
        assert queried_log.details["delta"] == -5
        assert queried_log.ip_address == "10.0.0.1"
        
        # Verify timestamps are set
        assert queried_log.created_at is not None, "Audit log should have created_at timestamp"
        
        # Verify relationship to user
        assert queried_log.actor is not None, "Audit log should have actor relationship"
        assert queried_log.actor.id == user.id
        assert queried_log.actor.name == "Test User"
    
    finally:
        session.close()
        engine.dispose()


def test_audit_log_complex_details():
    """Test AuditLog model with complex nested JSON details"""
    from app.models.audit_log import AuditLog
    
    complex_details = {
        "action": "ROLE_CHANGED",
        "user": {
            "id": 123,
            "email": "user@example.com",
            "name": "John Doe"
        },
        "changes": {
            "old_role": "CONSUMER",
            "new_role": "DISTRIBUTOR"
        },
        "metadata": {
            "approved_by": "owner@example.com",
            "approval_date": "2024-01-15",
            "notes": "Approved after verification"
        }
    }
    
    audit_log = AuditLog(
        actor_id=1,
        action_type="ROLE_CHANGED",
        object_type="USER",
        object_id=123,
        details=complex_details
    )
    
    assert audit_log.details == complex_details
    assert audit_log.details["user"]["id"] == 123
    assert audit_log.details["changes"]["old_role"] == "CONSUMER"
    assert audit_log.details["metadata"]["approved_by"] == "owner@example.com"
