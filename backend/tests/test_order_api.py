"""Tests for Order API endpoints"""
import pytest
from decimal import Decimal
from app.models.user import User
from app.models.product import Product
from app.models.category import Category
from app.models.cart import Cart
from app.models.cart_item import CartItem
from app.models.address import Address
from app.models.enums import UserRole, OrderStatus, PaymentStatus
from app.services.order_service import order_service


@pytest.fixture
def test_address(db_session, test_user):
    """Create a test address"""
    address = Address(
        user_id=test_user.id,
        name="Test User",
        phone="+919876543210",
        address_line1="123 Test Street",
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
def test_cart_with_items(db_session, test_user, test_product):
    """Create a test cart with items"""
    # Create cart
    cart = Cart(user_id=test_user.id)
    db_session.add(cart)
    db_session.commit()
    db_session.refresh(cart)
    
    # Add item to cart
    cart_item = CartItem(
        cart_id=cart.id,
        product_id=test_product.id,
        quantity=2,
        unit_price=test_product.consumer_price
    )
    db_session.add(cart_item)
    db_session.commit()
    
    return cart


def test_create_order_validates_cart(db_session, test_user, test_address):
    """Test that order creation validates cart before proceeding"""
    # Try to create order with empty cart
    with pytest.raises(ValueError, match="Cart is empty"):
        order_service.create_order(
            user_id=test_user.id,
            address_id=test_address.id,
            db=db_session
        )


def test_create_order_success(db_session, test_user, test_address, test_cart_with_items, test_product):
    """Test successful order creation"""
    initial_stock = test_product.stock_quantity
    
    # Create order
    order = order_service.create_order(
        user_id=test_user.id,
        address_id=test_address.id,
        db=db_session
    )
    
    # Verify order was created
    assert order.id is not None
    assert order.user_id == test_user.id
    assert order.order_status == OrderStatus.PENDING
    assert order.payment_status == PaymentStatus.PENDING
    assert order.delivery_address_id == test_address.id
    
    # Verify order items
    assert len(order.items) == 1
    assert order.items[0].product_id == test_product.id
    assert order.items[0].quantity == 2
    
    # Verify stock was reduced
    db_session.refresh(test_product)
    assert test_product.stock_quantity == initial_stock - 2
    
    # Verify cart was cleared
    cart = db_session.query(Cart).filter(Cart.user_id == test_user.id).first()
    assert len(cart.items) == 0


def test_get_user_orders(db_session, test_user, test_address, test_cart_with_items):
    """Test retrieving user's orders"""
    # Create an order
    order = order_service.create_order(
        user_id=test_user.id,
        address_id=test_address.id,
        db=db_session
    )
    
    # Get user's orders
    orders, total = order_service.get_user_orders(
        user_id=test_user.id,
        page=1,
        page_size=20,
        db=db_session
    )
    
    # Verify results
    assert total == 1
    assert len(orders) == 1
    assert orders[0].id == order.id


def test_get_order_by_id_with_ownership_validation(db_session, test_user, test_address, test_cart_with_items):
    """Test getting order by ID with ownership validation"""
    # Create an order
    order = order_service.create_order(
        user_id=test_user.id,
        address_id=test_address.id,
        db=db_session
    )
    
    # Get order with correct user
    retrieved_order = order_service.get_order_by_id(
        order_id=order.id,
        user_id=test_user.id,
        db=db_session
    )
    assert retrieved_order.id == order.id
    
    # Try to get order with wrong user
    with pytest.raises(ValueError, match="does not belong to user"):
        order_service.get_order_by_id(
            order_id=order.id,
            user_id=999,  # Non-existent user
            db=db_session
        )


def test_create_order_validates_stock(db_session, test_user, test_address, test_product):
    """Test that order creation validates stock availability"""
    # Create cart with more items than available stock
    cart = Cart(user_id=test_user.id)
    db_session.add(cart)
    db_session.commit()
    
    cart_item = CartItem(
        cart_id=cart.id,
        product_id=test_product.id,
        quantity=test_product.stock_quantity + 10,  # More than available
        unit_price=test_product.consumer_price
    )
    db_session.add(cart_item)
    db_session.commit()
    
    # Try to create order
    with pytest.raises(ValueError, match="Insufficient stock"):
        order_service.create_order(
            user_id=test_user.id,
            address_id=test_address.id,
            db=db_session
        )


def test_create_order_validates_address_ownership(db_session, test_user, test_cart_with_items):
    """Test that order creation validates address belongs to user"""
    # Create address for different user
    other_user = User(
        email="other@example.com",
        phone="+919876543211",
        name="Other User",
        role=UserRole.CONSUMER,
        hashed_password="hashed",
        is_active=True
    )
    db_session.add(other_user)
    db_session.commit()
    
    other_address = Address(
        user_id=other_user.id,
        name="Other User",
        phone="+919876543211",
        address_line1="456 Other Street",
        city="Other City",
        state="Other State",
        postal_code="654321",
        country="India",
        is_default=True
    )
    db_session.add(other_address)
    db_session.commit()
    
    # Try to create order with other user's address
    with pytest.raises(ValueError, match="does not belong to user"):
        order_service.create_order(
            user_id=test_user.id,
            address_id=other_address.id,
            db=db_session
        )

