"""Property-based tests for distributor features

Feature: indostar-naturals-ecommerce
"""
import pytest
from app.models.user import User
from app.models.enums import UserRole, DistributorStatus, PaymentStatus, OrderStatus
from app.services.user_service import user_service


# Feature: indostar-naturals-ecommerce, Property 8: Distributor requires approval
def test_property_distributor_requires_approval(db_session):
    """
    **Property 8: Distributor requires approval**
    **Validates: Requirements 2.4**
    
    For any distributor registration, the user's role should remain 
    pending or inactive until an owner explicitly approves the account.
    """
    # Register distributor
    user = user_service.register_distributor(
        phone="+919876543210",
        email="distributor@test.com",
        name="Test Distributor",
        business_name="Test Business",
        db=db_session
    )
    
    # Verify user was created
    assert user is not None
    assert user.id is not None
    
    # Verify user has pending distributor status
    assert user.distributor_status == DistributorStatus.PENDING
    
    # Verify user does NOT have distributor role yet (should be consumer)
    assert user.role == UserRole.CONSUMER
    
    # Verify user is active but not yet a distributor
    assert user.is_active is True
    
    # Verify email and phone are set
    assert user.email == "distributor@test.com"
    assert user.phone == "+919876543210"


# Feature: indostar-naturals-ecommerce, Property 53: Distributor approval updates role and notifies
def test_property_distributor_approval_updates_role_and_notifies(db_session):
    """
    **Property 53: Distributor approval updates role and notifies**
    **Validates: Requirements 10.5**
    
    For any distributor approval action, the system should update 
    the user's role to distributor and send a confirmation email.
    """
    # Create an owner user for approval
    owner = User(
        phone="+919999999999",
        email="owner@test.com",
        name="Test Owner",
        role=UserRole.OWNER,
        is_active=True,
        is_phone_verified=True,
        is_email_verified=True
    )
    db_session.add(owner)
    db_session.commit()
    db_session.refresh(owner)
    
    # Register distributor
    user = user_service.register_distributor(
        phone="+919876543211",
        email="distributor2@test.com",
        name="Test Distributor 2",
        business_name="Test Business 2",
        db=db_session
    )
    
    # Verify initial state
    assert user.distributor_status == DistributorStatus.PENDING
    assert user.role == UserRole.CONSUMER
    
    # Approve distributor
    approved_user = user_service.approve_distributor(
        user_id=user.id,
        approved=True,
        actor_id=owner.id,
        db=db_session
    )
    
    # Verify approval updated the user
    assert approved_user is not None
    assert approved_user.id == user.id
    
    # Verify distributor status changed to approved
    assert approved_user.distributor_status == DistributorStatus.APPROVED
    
    # Verify role changed to distributor
    assert approved_user.role == UserRole.DISTRIBUTOR
    
    # Verify audit log was created
    from app.models.audit_log import AuditLog
    audit_logs = db_session.query(AuditLog).filter(
        AuditLog.object_type == "USER",
        AuditLog.object_id == user.id,
        AuditLog.action_type == "DISTRIBUTOR_APPROVAL"
    ).all()
    
    assert len(audit_logs) > 0
    audit_log = audit_logs[0]
    assert audit_log.actor_id == owner.id
    assert audit_log.details["approved"] is True
    assert audit_log.details["new_role"] == UserRole.DISTRIBUTOR.value
    assert audit_log.details["new_status"] == DistributorStatus.APPROVED.value


# Test rejection flow
def test_property_distributor_rejection_maintains_consumer_role(db_session):
    """
    Test that rejecting a distributor application keeps the user as a consumer
    and updates the status to rejected.
    """
    # Create an owner user for rejection
    owner = User(
        phone="+919999999998",
        email="owner2@test.com",
        name="Test Owner 2",
        role=UserRole.OWNER,
        is_active=True,
        is_phone_verified=True,
        is_email_verified=True
    )
    db_session.add(owner)
    db_session.commit()
    db_session.refresh(owner)
    
    # Register distributor
    user = user_service.register_distributor(
        phone="+919876543212",
        email="distributor3@test.com",
        name="Test Distributor 3",
        business_name="Test Business 3",
        db=db_session
    )
    
    # Verify initial state
    assert user.distributor_status == DistributorStatus.PENDING
    assert user.role == UserRole.CONSUMER
    
    # Reject distributor
    rejected_user = user_service.approve_distributor(
        user_id=user.id,
        approved=False,
        actor_id=owner.id,
        db=db_session
    )
    
    # Verify rejection updated the user
    assert rejected_user is not None
    assert rejected_user.id == user.id
    
    # Verify distributor status changed to rejected
    assert rejected_user.distributor_status == DistributorStatus.REJECTED
    
    # Verify role remains consumer
    assert rejected_user.role == UserRole.CONSUMER
    
    # Verify audit log was created
    from app.models.audit_log import AuditLog
    audit_logs = db_session.query(AuditLog).filter(
        AuditLog.object_type == "USER",
        AuditLog.object_id == user.id,
        AuditLog.action_type == "DISTRIBUTOR_REJECTION"
    ).all()
    
    assert len(audit_logs) > 0
    audit_log = audit_logs[0]
    assert audit_log.actor_id == owner.id
    assert audit_log.details["approved"] is False
    assert audit_log.details["new_role"] == UserRole.CONSUMER.value
    assert audit_log.details["new_status"] == DistributorStatus.REJECTED.value



# Feature: indostar-naturals-ecommerce, Property 47: Bulk discounts apply to qualifying orders
def test_property_bulk_discounts_apply_to_qualifying_orders(db_session):
    """
    **Property 47: Bulk discounts apply to qualifying orders**
    **Validates: Requirements 9.4**
    
    For any distributor order meeting bulk discount quantity thresholds, 
    the system should apply the additional discount to the order total.
    """
    from app.models.bulk_discount_rule import BulkDiscountRule
    from decimal import Decimal
    
    # Create a distributor user
    distributor = User(
        phone="+919876543220",
        email="distributor_bulk@test.com",
        name="Bulk Distributor",
        role=UserRole.DISTRIBUTOR,
        distributor_status=DistributorStatus.APPROVED,
        is_active=True,
        is_phone_verified=True,
        is_email_verified=True
    )
    db_session.add(distributor)
    db_session.commit()
    db_session.refresh(distributor)
    
    # Create a category
    from app.models.category import Category
    category = Category(
        name="Bulk Test Category",
        slug="bulk-test-category",
        display_order=1
    )
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)
    
    # Create a product
    from app.models.product import Product
    product = Product(
        owner_id=distributor.id,
        title="Bulk Test Product",
        description="Test product for bulk discounts",
        category_id=category.id,
        sku="BULK-001",
        unit_size="1 kg",
        consumer_price=Decimal("100.00"),
        distributor_price=Decimal("80.00"),
        stock_quantity=1000,
        is_active=True
    )
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)
    
    # Create a bulk discount rule: 10% off for orders of 50+ units
    bulk_rule = BulkDiscountRule(
        product_id=product.id,
        category_id=None,
        min_quantity=50,
        discount_percentage=Decimal("10.00"),
        is_active=True
    )
    db_session.add(bulk_rule)
    db_session.commit()
    db_session.refresh(bulk_rule)
    
    # Create an order with 60 units (qualifies for bulk discount)
    from app.models.order import Order
    from app.models.order_item import OrderItem
    from app.models.address import Address
    
    address = Address(
        user_id=distributor.id,
        name="Test Address",
        phone="+919876543220",
        address_line1="123 Test St",
        city="Test City",
        state="Test State",
        postal_code="123456",
        country="India",
        is_default=True
    )
    db_session.add(address)
    db_session.commit()
    db_session.refresh(address)
    
    order = Order(
        user_id=distributor.id,
        order_number="ORD-BULK-001",
        total_amount=Decimal("4800.00"),  # 60 * 80
        discount_amount=Decimal("0.00"),
        final_amount=Decimal("4800.00"),
        payment_status=PaymentStatus.PENDING,
        order_status=OrderStatus.PENDING,
        delivery_address_id=address.id
    )
    db_session.add(order)
    db_session.flush()
    
    order_item = OrderItem(
        order_id=order.id,
        product_id=product.id,
        quantity=60,
        unit_price=Decimal("80.00"),
        total_price=Decimal("4800.00")
    )
    db_session.add(order_item)
    db_session.commit()
    db_session.refresh(order)
    
    # Apply bulk discounts
    from app.services.order_service import order_service
    bulk_discount = order_service.apply_bulk_discounts(order, db_session)
    
    # Verify bulk discount was applied
    # 10% of 4800 = 480
    assert bulk_discount == Decimal("480.00")
    assert bulk_discount > Decimal("0.00")


# Feature: indostar-naturals-ecommerce, Property 45: Distributor cart uses distributor pricing
def test_property_distributor_cart_uses_distributor_pricing(db_session):
    """
    **Property 45: Distributor cart uses distributor pricing**
    **Validates: Requirements 9.2**
    
    For any distributor's cart, the cart total should be calculated 
    using distributor_price for all items.
    """
    from app.models.category import Category
    from app.models.product import Product
    from app.models.cart import Cart
    from app.models.cart_item import CartItem
    from decimal import Decimal
    
    # Create a distributor user
    distributor = User(
        phone="+919876543221",
        email="distributor_cart@test.com",
        name="Cart Distributor",
        role=UserRole.DISTRIBUTOR,
        distributor_status=DistributorStatus.APPROVED,
        is_active=True,
        is_phone_verified=True,
        is_email_verified=True
    )
    db_session.add(distributor)
    db_session.commit()
    db_session.refresh(distributor)
    
    # Create a category
    category = Category(
        name="Cart Test Category",
        slug="cart-test-category",
        display_order=1
    )
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)
    
    # Create a product with different consumer and distributor prices
    product = Product(
        owner_id=distributor.id,
        title="Cart Test Product",
        description="Test product for cart pricing",
        category_id=category.id,
        sku="CART-001",
        unit_size="1 kg",
        consumer_price=Decimal("100.00"),
        distributor_price=Decimal("75.00"),
        stock_quantity=100,
        is_active=True
    )
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)
    
    # Create a cart for the distributor
    cart = Cart(
        user_id=distributor.id,
        coupon_code=None,
        discount_amount=Decimal("0.00")
    )
    db_session.add(cart)
    db_session.commit()
    db_session.refresh(cart)
    
    # Add item to cart with distributor price
    cart_item = CartItem(
        cart_id=cart.id,
        product_id=product.id,
        quantity=10,
        unit_price=product.distributor_price  # Should use distributor price
    )
    db_session.add(cart_item)
    db_session.commit()
    db_session.refresh(cart_item)
    
    # Verify cart item uses distributor pricing
    assert cart_item.unit_price == product.distributor_price
    assert cart_item.unit_price == Decimal("75.00")
    assert cart_item.unit_price != product.consumer_price
    
    # Verify cart total uses distributor pricing
    cart_total = cart_item.quantity * cart_item.unit_price
    assert cart_total == Decimal("750.00")  # 10 * 75
    assert cart_total != Decimal("1000.00")  # Would be 10 * 100 with consumer price


# Feature: indostar-naturals-ecommerce, Property 46: Distributor checkout uses distributor pricing
def test_property_distributor_checkout_uses_distributor_pricing(db_session):
    """
    **Property 46: Distributor checkout uses distributor pricing**
    **Validates: Requirements 9.3**
    
    For any distributor order, the final_amount should be calculated 
    using distributor_price for all items.
    """
    from app.models.category import Category
    from app.models.product import Product
    from app.models.order import Order
    from app.models.order_item import OrderItem
    from app.models.address import Address
    from decimal import Decimal
    
    # Create a distributor user
    distributor = User(
        phone="+919876543222",
        email="distributor_checkout@test.com",
        name="Checkout Distributor",
        role=UserRole.DISTRIBUTOR,
        distributor_status=DistributorStatus.APPROVED,
        is_active=True,
        is_phone_verified=True,
        is_email_verified=True
    )
    db_session.add(distributor)
    db_session.commit()
    db_session.refresh(distributor)
    
    # Create a category
    category = Category(
        name="Checkout Test Category",
        slug="checkout-test-category",
        display_order=1
    )
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)
    
    # Create a product
    product = Product(
        owner_id=distributor.id,
        title="Checkout Test Product",
        description="Test product for checkout pricing",
        category_id=category.id,
        sku="CHECKOUT-001",
        unit_size="1 kg",
        consumer_price=Decimal("120.00"),
        distributor_price=Decimal("90.00"),
        stock_quantity=100,
        is_active=True
    )
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)
    
    # Create an address
    address = Address(
        user_id=distributor.id,
        name="Test Address",
        phone="+919876543222",
        address_line1="123 Test St",
        city="Test City",
        state="Test State",
        postal_code="123456",
        country="India",
        is_default=True
    )
    db_session.add(address)
    db_session.commit()
    db_session.refresh(address)
    
    # Create an order with distributor pricing
    order = Order(
        user_id=distributor.id,
        order_number="ORD-CHECKOUT-001",
        total_amount=Decimal("900.00"),  # 10 * 90 (distributor price)
        discount_amount=Decimal("0.00"),
        final_amount=Decimal("900.00"),
        payment_status=PaymentStatus.PENDING,
        order_status=OrderStatus.PENDING,
        delivery_address_id=address.id
    )
    db_session.add(order)
    db_session.flush()
    
    order_item = OrderItem(
        order_id=order.id,
        product_id=product.id,
        quantity=10,
        unit_price=product.distributor_price,  # Should use distributor price
        total_price=Decimal("900.00")
    )
    db_session.add(order_item)
    db_session.commit()
    db_session.refresh(order)
    
    # Verify order uses distributor pricing
    assert order_item.unit_price == product.distributor_price
    assert order_item.unit_price == Decimal("90.00")
    assert order_item.unit_price != product.consumer_price
    
    # Verify order total uses distributor pricing
    assert order.final_amount == Decimal("900.00")  # 10 * 90
    assert order.final_amount != Decimal("1200.00")  # Would be 10 * 120 with consumer price


# Feature: indostar-naturals-ecommerce, Property 48: Distributor order history shows distributor pricing
def test_property_distributor_order_history_shows_distributor_pricing(db_session):
    """
    **Property 48: Distributor order history shows distributor pricing**
    **Validates: Requirements 9.5**
    
    For any distributor viewing order history, all orders should display 
    distributor prices and any applied bulk discounts.
    """
    from app.models.category import Category
    from app.models.product import Product
    from app.models.order import Order
    from app.models.order_item import OrderItem
    from app.models.address import Address
    from decimal import Decimal
    
    # Create a distributor user
    distributor = User(
        phone="+919876543223",
        email="distributor_history@test.com",
        name="History Distributor",
        role=UserRole.DISTRIBUTOR,
        distributor_status=DistributorStatus.APPROVED,
        is_active=True,
        is_phone_verified=True,
        is_email_verified=True
    )
    db_session.add(distributor)
    db_session.commit()
    db_session.refresh(distributor)
    
    # Create a category
    category = Category(
        name="History Test Category",
        slug="history-test-category",
        display_order=1
    )
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)
    
    # Create a product
    product = Product(
        owner_id=distributor.id,
        title="History Test Product",
        description="Test product for order history",
        category_id=category.id,
        sku="HISTORY-001",
        unit_size="1 kg",
        consumer_price=Decimal("150.00"),
        distributor_price=Decimal("110.00"),
        stock_quantity=100,
        is_active=True
    )
    db_session.add(product)
    db_session.commit()
    db_session.refresh(product)
    
    # Create an address
    address = Address(
        user_id=distributor.id,
        name="Test Address",
        phone="+919876543223",
        address_line1="123 Test St",
        city="Test City",
        state="Test State",
        postal_code="123456",
        country="India",
        is_default=True
    )
    db_session.add(address)
    db_session.commit()
    db_session.refresh(address)
    
    # Create an order
    order = Order(
        user_id=distributor.id,
        order_number="ORD-HISTORY-001",
        total_amount=Decimal("1100.00"),  # 10 * 110
        discount_amount=Decimal("50.00"),  # Some bulk discount
        final_amount=Decimal("1050.00"),
        payment_status=PaymentStatus.PAID,
        order_status=OrderStatus.DELIVERED,
        delivery_address_id=address.id
    )
    db_session.add(order)
    db_session.flush()
    
    order_item = OrderItem(
        order_id=order.id,
        product_id=product.id,
        quantity=10,
        unit_price=product.distributor_price,
        total_price=Decimal("1100.00")
    )
    db_session.add(order_item)
    db_session.commit()
    db_session.refresh(order)
    
    # Retrieve order history for distributor
    from app.services.order_service import order_service
    orders, total = order_service.get_user_orders(
        user_id=distributor.id,
        page=1,
        page_size=20,
        db=db_session
    )
    
    # Verify order history contains the order
    assert len(orders) > 0
    assert orders[0].id == order.id
    
    # Verify order shows distributor pricing
    retrieved_order = orders[0]
    assert retrieved_order.items[0].unit_price == product.distributor_price
    assert retrieved_order.items[0].unit_price == Decimal("110.00")
    assert retrieved_order.items[0].unit_price != product.consumer_price
    
    # Verify bulk discount is shown
    assert retrieved_order.discount_amount == Decimal("50.00")
    assert retrieved_order.final_amount == Decimal("1050.00")
