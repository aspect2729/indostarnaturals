"""Property-based tests for cart functionality

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
from app.models.enums import UserRole
from app.services.cart_service import cart_service
from app.schemas.cart import CartItemCreate, CartItemUpdate


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


# Hypothesis strategies for generating test data

@st.composite
def user_strategy(draw, role=None):
    """Generate a random user"""
    if role is None:
        role = draw(st.sampled_from([UserRole.CONSUMER, UserRole.DISTRIBUTOR]))
    
    phone_number = draw(st.integers(min_value=1000000000, max_value=9999999999))
    
    return {
        'email': f'user{phone_number}@example.com',
        'phone': f'+91{phone_number}',
        'name': draw(st.text(min_size=3, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Zs')))),
        'role': role,
        'hashed_password': 'hashed_password',
        'is_active': True
    }


@st.composite
def product_strategy(draw, owner_id, category_id):
    """Generate a random product with unique SKU"""
    # Use random UUID to ensure unique SKUs across test runs
    import uuid
    sku_suffix = str(uuid.uuid4())[:8]
    sku_num = draw(st.integers(min_value=1, max_value=999999))
    
    consumer_price = draw(st.decimals(min_value=Decimal('1.00'), max_value=Decimal('10000.00'), places=2))
    distributor_price = draw(st.decimals(min_value=Decimal('1.00'), max_value=consumer_price, places=2))
    
    return {
        'owner_id': owner_id,
        'title': f'Product {sku_num}',
        'description': draw(st.text(min_size=10, max_size=200)),
        'category_id': category_id,
        'sku': f'SKU-{sku_num}-{sku_suffix}',
        'unit_size': draw(st.sampled_from(['1 kg', '500 g', '1 L', '500 ml', '1 Unit'])),
        'consumer_price': consumer_price,
        'distributor_price': distributor_price,
        'stock_quantity': draw(st.integers(min_value=10, max_value=1000)),
        'is_active': True
    }


@st.composite
def cart_item_quantity_strategy(draw):
    """Generate a valid cart item quantity"""
    return draw(st.integers(min_value=1, max_value=50))


# Feature: indostar-naturals-ecommerce, Property 22: Quantity updates recalculate total
@settings(max_examples=100, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(
    user_data=user_strategy(),
    product_data_list=st.lists(
        st.data(),
        min_size=1,
        max_size=5
    ),
    new_quantity=cart_item_quantity_strategy()
)
def test_cart_quantity_update_recalculates_total(
    user_data,
    product_data_list,
    new_quantity
):
    """
    Property 22: Quantity updates recalculate total
    
    For any cart and cart item, when the quantity is updated,
    the cart total should equal the sum of (quantity × unit_price) for all items.
    
    Validates: Requirements 5.2
    """
    # Create test database
    db_session, engine = get_test_db()
    
    try:
        # Create category
        test_category = Category(
            name="Test Category",
            slug="test-category",
            display_order=1
        )
        db_session.add(test_category)
        db_session.commit()
        db_session.refresh(test_category)
        
        # Create user
        user = User(**user_data)
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        # Create products
        products = []
        for data_strategy in product_data_list:
            product_data = data_strategy.draw(product_strategy(owner_id=user.id, category_id=test_category.id))
            product = Product(**product_data)
            db_session.add(product)
            db_session.commit()
            db_session.refresh(product)
            products.append(product)
        
        # Add items to cart
        for product in products:
            initial_quantity = min(5, product.stock_quantity)
            item_data = CartItemCreate(
                product_id=product.id,
                quantity=initial_quantity
            )
            cart_service.add_item(user.id, item_data, db_session)
        
        # Get cart and select first item to update
        cart_response = cart_service.get_cart(user.id, db_session)
        assume(len(cart_response.items) > 0)
        
        first_item = cart_response.items[0]
        
        # Ensure new quantity doesn't exceed stock
        product = db_session.query(Product).filter(Product.id == first_item.product_id).first()
        new_quantity = min(new_quantity, product.stock_quantity)
        
        # Update quantity
        quantity_data = CartItemUpdate(quantity=new_quantity)
        updated_cart = cart_service.update_item_quantity(
            user.id,
            first_item.id,
            quantity_data,
            db_session
        )
        
        # Verify total equals sum of (quantity × unit_price)
        expected_subtotal = sum(
            item.quantity * item.unit_price 
            for item in updated_cart.items
        )
        expected_total = expected_subtotal - updated_cart.discount_amount
        
        assert updated_cart.subtotal == expected_subtotal, \
            f"Subtotal mismatch: expected {expected_subtotal}, got {updated_cart.subtotal}"
        assert updated_cart.total == expected_total, \
            f"Total mismatch: expected {expected_total}, got {updated_cart.total}"
    
    finally:
        cleanup_test_db(db_session, engine)


# Feature: indostar-naturals-ecommerce, Property 23: Valid coupon reduces cart total
@settings(max_examples=100, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(
    user_data=user_strategy(),
    product_data_list=st.lists(
        st.data(),
        min_size=1,
        max_size=3
    ),
    coupon_code=st.text(min_size=5, max_size=20, alphabet=st.characters(whitelist_categories=('Lu', 'Nd')))
)
def test_valid_coupon_reduces_cart_total(
    user_data,
    product_data_list,
    coupon_code
):
    """
    Property 23: Valid coupon reduces cart total
    
    For any cart with items, when a valid coupon is applied,
    the cart total should be less than the subtotal.
    
    Validates: Requirements 5.3
    """
    # Create test database
    db_session, engine = get_test_db()
    
    try:
        # Create category
        test_category = Category(
            name="Test Category",
            slug="test-category",
            display_order=1
        )
        db_session.add(test_category)
        db_session.commit()
        db_session.refresh(test_category)
        
        # Create user
        user = User(**user_data)
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        # Create products and add to cart
        for data_strategy in product_data_list:
            product_data = data_strategy.draw(product_strategy(owner_id=user.id, category_id=test_category.id))
            product = Product(**product_data)
            db_session.add(product)
            db_session.commit()
            db_session.refresh(product)
            
            # Add to cart
            quantity = min(3, product.stock_quantity)
            item_data = CartItemCreate(product_id=product.id, quantity=quantity)
            cart_service.add_item(user.id, item_data, db_session)
        
        # Get cart before coupon
        cart_before = cart_service.get_cart(user.id, db_session)
        subtotal_before = cart_before.subtotal
        
        # Apply coupon
        cart_after = cart_service.apply_coupon(user.id, coupon_code, db_session)
        
        # Verify coupon reduces total
        assert cart_after.discount_amount > Decimal('0.00'), \
            "Discount amount should be positive"
        assert cart_after.total < subtotal_before, \
            f"Total after coupon ({cart_after.total}) should be less than subtotal ({subtotal_before})"
        assert cart_after.total == cart_after.subtotal - cart_after.discount_amount, \
            "Total should equal subtotal minus discount"
    
    finally:
        cleanup_test_db(db_session, engine)


# Feature: indostar-naturals-ecommerce, Property 24: Cart displays role-appropriate prices
@settings(max_examples=100, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(
    consumer_phone=st.integers(min_value=1000000000, max_value=9999999999),
    distributor_phone=st.integers(min_value=1000000000, max_value=9999999999),
    product_data=st.data()
)
def test_cart_displays_role_appropriate_prices(
    consumer_phone,
    distributor_phone,
    product_data
):
    """
    Property 24: Cart displays role-appropriate prices
    
    For any product, when added to a consumer's cart, the unit price should be consumer_price,
    and when added to a distributor's cart, the unit price should be distributor_price.
    
    Validates: Requirements 5.4
    """
    # Ensure different phone numbers
    assume(consumer_phone != distributor_phone)
    
    # Create test database
    db_session, engine = get_test_db()
    
    try:
        # Create category
        test_category = Category(
            name="Test Category",
            slug="test-category",
            display_order=1
        )
        db_session.add(test_category)
        db_session.commit()
        db_session.refresh(test_category)
        
        # Create consumer
        consumer_data = {
            'email': f'consumer{consumer_phone}@example.com',
            'phone': f'+91{consumer_phone}',
            'name': f'Consumer {consumer_phone}',
            'role': UserRole.CONSUMER,
            'hashed_password': 'hashed_password',
            'is_active': True
        }
        consumer = User(**consumer_data)
        db_session.add(consumer)
        db_session.commit()
        db_session.refresh(consumer)
        
        # Create distributor
        distributor_data = {
            'email': f'distributor{distributor_phone}@example.com',
            'phone': f'+91{distributor_phone}',
            'name': f'Distributor {distributor_phone}',
            'role': UserRole.DISTRIBUTOR,
            'hashed_password': 'hashed_password',
            'is_active': True
        }
        distributor = User(**distributor_data)
        db_session.add(distributor)
        db_session.commit()
        db_session.refresh(distributor)
        
        # Create product
        product_dict = product_data.draw(product_strategy(owner_id=consumer.id, category_id=test_category.id))
        product = Product(**product_dict)
        db_session.add(product)
        db_session.commit()
        db_session.refresh(product)
        
        # Add to consumer cart
        consumer_item_data = CartItemCreate(product_id=product.id, quantity=2)
        consumer_cart = cart_service.add_item(consumer.id, consumer_item_data, db_session)
        
        # Add to distributor cart
        distributor_item_data = CartItemCreate(product_id=product.id, quantity=2)
        distributor_cart = cart_service.add_item(distributor.id, distributor_item_data, db_session)
        
        # Verify consumer sees consumer price
        consumer_cart_item = consumer_cart.items[0]
        assert consumer_cart_item.unit_price == product.consumer_price, \
            f"Consumer should see consumer price {product.consumer_price}, got {consumer_cart_item.unit_price}"
        
        # Verify distributor sees distributor price
        distributor_cart_item = distributor_cart.items[0]
        assert distributor_cart_item.unit_price == product.distributor_price, \
            f"Distributor should see distributor price {product.distributor_price}, got {distributor_cart_item.unit_price}"
    
    finally:
        cleanup_test_db(db_session, engine)


# Feature: indostar-naturals-ecommerce, Property 25: Item removal updates cart
@settings(max_examples=100, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(
    user_data=user_strategy(),
    product_data_list=st.lists(
        st.data(),
        min_size=2,
        max_size=5
    )
)
def test_item_removal_updates_cart(
    user_data,
    product_data_list
):
    """
    Property 25: Item removal updates cart
    
    For any cart item, when removed, the item should not appear in subsequent cart queries
    and the cart total should be recalculated.
    
    Validates: Requirements 5.5
    """
    # Create test database
    db_session, engine = get_test_db()
    
    try:
        # Create category
        test_category = Category(
            name="Test Category",
            slug="test-category",
            display_order=1
        )
        db_session.add(test_category)
        db_session.commit()
        db_session.refresh(test_category)
        
        # Create user
        user = User(**user_data)
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        # Create products and add to cart
        for data_strategy in product_data_list:
            product_data = data_strategy.draw(product_strategy(owner_id=user.id, category_id=test_category.id))
            product = Product(**product_data)
            db_session.add(product)
            db_session.commit()
            db_session.refresh(product)
            
            # Add to cart
            quantity = min(3, product.stock_quantity)
            item_data = CartItemCreate(product_id=product.id, quantity=quantity)
            cart_service.add_item(user.id, item_data, db_session)
        
        # Get cart before removal
        cart_before = cart_service.get_cart(user.id, db_session)
        item_count_before = len(cart_before.items)
        assume(item_count_before >= 2)
        
        # Select item to remove
        item_to_remove = cart_before.items[0]
        item_id_to_remove = item_to_remove.id
        product_id_to_remove = item_to_remove.product_id
        
        # Calculate expected total after removal
        expected_subtotal = sum(
            item.quantity * item.unit_price 
            for item in cart_before.items 
            if item.id != item_id_to_remove
        )
        
        # Remove item
        cart_after = cart_service.remove_item(user.id, item_id_to_remove, db_session)
        
        # Verify item is removed
        assert len(cart_after.items) == item_count_before - 1, \
            f"Cart should have {item_count_before - 1} items, got {len(cart_after.items)}"
        
        # Verify removed item is not in cart
        remaining_product_ids = [item.product_id for item in cart_after.items]
        assert product_id_to_remove not in remaining_product_ids, \
            f"Product {product_id_to_remove} should not be in cart after removal"
        
        # Verify total is recalculated
        assert cart_after.subtotal == expected_subtotal, \
            f"Subtotal should be {expected_subtotal}, got {cart_after.subtotal}"
    
    finally:
        cleanup_test_db(db_session, engine)


# Feature: indostar-naturals-ecommerce, Property 26: Insufficient stock blocks checkout
@settings(max_examples=100, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(
    user_data=user_strategy(),
    product_data=st.data(),
    cart_quantity=st.integers(min_value=10, max_value=50)
)
def test_insufficient_stock_blocks_checkout(
    user_data,
    product_data,
    cart_quantity
):
    """
    Property 26: Insufficient stock blocks checkout
    
    For any cart containing items where quantity exceeds available stock,
    the validation should fail and return stock availability errors.
    
    Validates: Requirements 5.6
    """
    # Create test database
    db_session, engine = get_test_db()
    
    try:
        # Create category
        test_category = Category(
            name="Test Category",
            slug="test-category",
            display_order=1
        )
        db_session.add(test_category)
        db_session.commit()
        db_session.refresh(test_category)
        
        # Create user
        user = User(**user_data)
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        # Create product with limited stock
        product_dict = product_data.draw(product_strategy(owner_id=user.id, category_id=test_category.id))
        # Override stock to be less than cart quantity
        product_dict['stock_quantity'] = max(1, cart_quantity - 5)
        product = Product(**product_dict)
        db_session.add(product)
        db_session.commit()
        db_session.refresh(product)
        
        # Add item to cart with quantity less than stock
        initial_quantity = min(2, product.stock_quantity)
        item_data = CartItemCreate(product_id=product.id, quantity=initial_quantity)
        cart_service.add_item(user.id, item_data, db_session)
        
        # Reduce product stock to create insufficient stock situation
        product.stock_quantity = max(0, initial_quantity - 1)
        db_session.commit()
        
        # Validate cart
        validation = cart_service.validate_cart(user.id, db_session)
        
        # Verify validation fails
        assert not validation.is_valid, \
            "Cart validation should fail when stock is insufficient"
        assert len(validation.errors) > 0, \
            "Validation should return errors for insufficient stock"
        
        # Verify error message mentions stock
        error_text = ' '.join(validation.errors).lower()
        assert 'stock' in error_text or 'available' in error_text, \
            f"Error should mention stock availability: {validation.errors}"
    
    finally:
        cleanup_test_db(db_session, engine)

