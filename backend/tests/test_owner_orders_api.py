"""Tests for owner order management API endpoints"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.models.user import User
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.product import Product
from app.models.category import Category
from app.models.address import Address
from app.models.enums import UserRole, OrderStatus, PaymentStatus
from app.services.auth_service import token_service
from decimal import Decimal
from datetime import datetime


client = TestClient(app)


def create_test_user(db: Session, role: UserRole, email_suffix: str) -> User:
    """Helper to create a test user"""
    user = User(
        email=f"test_{email_suffix}@example.com",
        phone=f"+1234567{email_suffix}",
        name=f"Test User {email_suffix}",
        role=role,
        is_active=True,
        is_email_verified=True,
        is_phone_verified=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def create_test_product(db: Session, owner_id: int, sku_suffix: str) -> Product:
    """Helper to create a test product"""
    # Create category first
    category = db.query(Category).first()
    if not category:
        category = Category(
            name="Test Category",
            slug="test-category",
            display_order=1
        )
        db.add(category)
        db.commit()
        db.refresh(category)
    
    product = Product(
        owner_id=owner_id,
        title=f"Test Product {sku_suffix}",
        description="Test description",
        category_id=category.id,
        sku=f"TEST-{sku_suffix}",
        unit_size="1kg",
        consumer_price=Decimal("100.00"),
        distributor_price=Decimal("80.00"),
        stock_quantity=100,
        is_active=True,
        is_subscription_available=False
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


def create_test_address(db: Session, user_id: int) -> Address:
    """Helper to create a test address"""
    address = Address(
        user_id=user_id,
        name="Test User",
        phone="+1234567890",
        address_line1="123 Test St",
        address_line2="Apt 4",
        city="Test City",
        state="Test State",
        postal_code="12345",
        country="Test Country",
        is_default=True
    )
    db.add(address)
    db.commit()
    db.refresh(address)
    return address


def create_test_order(
    db: Session,
    user: User,
    product: Product,
    address: Address,
    status: OrderStatus = OrderStatus.PENDING
) -> Order:
    """Helper to create a test order"""
    order = Order(
        user_id=user.id,
        order_number=f"ORD-TEST-{datetime.utcnow().timestamp()}",
        total_amount=Decimal("100.00"),
        discount_amount=Decimal("0.00"),
        final_amount=Decimal("100.00"),
        payment_status=PaymentStatus.PENDING,
        order_status=status,
        delivery_address_id=address.id
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    
    # Create order item
    order_item = OrderItem(
        order_id=order.id,
        product_id=product.id,
        quantity=1,
        unit_price=Decimal("100.00"),
        total_price=Decimal("100.00")
    )
    db.add(order_item)
    db.commit()
    
    return order


def test_list_all_orders_as_owner(db_session: Session):
    """Test listing all orders as owner"""
    # Create owner user
    owner = create_test_user(db_session, UserRole.OWNER, "owner1")
    
    # Create consumer user
    consumer = create_test_user(db_session, UserRole.CONSUMER, "consumer1")
    
    # Create product
    product = create_test_product(db_session, owner.id, "001")
    
    # Create address
    address = create_test_address(db_session, consumer.id)
    
    # Create orders
    order1 = create_test_order(db_session, consumer, product, address, OrderStatus.PENDING)
    order2 = create_test_order(db_session, consumer, product, address, OrderStatus.CONFIRMED)
    
    # Generate token for owner
    token = token_service.create_access_token({"sub": str(owner.id), "role": owner.role.value})
    
    # Make request
    response = client.get(
        "/api/v1/owner/orders",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "orders" in data
    assert "total" in data
    assert data["total"] >= 2
    assert len(data["orders"]) >= 2


def test_list_all_orders_with_status_filter(db_session: Session):
    """Test listing orders with status filter"""
    # Create owner user
    owner = create_test_user(db_session, UserRole.OWNER, "owner2")
    
    # Create consumer user
    consumer = create_test_user(db_session, UserRole.CONSUMER, "consumer2")
    
    # Create product
    product = create_test_product(db_session, owner.id, "002")
    
    # Create address
    address = create_test_address(db_session, consumer.id)
    
    # Create orders with different statuses
    order1 = create_test_order(db_session, consumer, product, address, OrderStatus.PENDING)
    order2 = create_test_order(db_session, consumer, product, address, OrderStatus.CONFIRMED)
    
    # Generate token for owner
    token = token_service.create_access_token({"sub": str(owner.id), "role": owner.role.value})
    
    # Make request with status filter
    response = client.get(
        "/api/v1/owner/orders?status_filter=CONFIRMED",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "orders" in data
    # All returned orders should have CONFIRMED status
    for order in data["orders"]:
        assert order["order_status"] == "CONFIRMED"


def test_list_all_orders_as_non_owner_forbidden(db_session: Session):
    """Test that non-owner users cannot list all orders"""
    # Create consumer user
    consumer = create_test_user(db_session, UserRole.CONSUMER, "consumer3")
    
    # Generate token for consumer
    token = token_service.create_access_token({"sub": str(consumer.id), "role": consumer.role.value})
    
    # Make request
    response = client.get(
        "/api/v1/owner/orders",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 403
    assert "forbidden" in response.json()["detail"].lower()


def test_update_order_status_as_owner(db_session: Session):
    """Test updating order status as owner"""
    # Create owner user
    owner = create_test_user(db_session, UserRole.OWNER, "owner3")
    
    # Create consumer user
    consumer = create_test_user(db_session, UserRole.CONSUMER, "consumer4")
    
    # Create product
    product = create_test_product(db_session, owner.id, "003")
    
    # Create address
    address = create_test_address(db_session, consumer.id)
    
    # Create order
    order = create_test_order(db_session, consumer, product, address, OrderStatus.PENDING)
    
    # Generate token for owner
    token = token_service.create_access_token({"sub": str(owner.id), "role": owner.role.value})
    
    # Make request to update status
    response = client.put(
        f"/api/v1/owner/orders/{order.id}/status",
        json={"status": "CONFIRMED"},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["order_status"] == "CONFIRMED"
    assert data["id"] == order.id


def test_update_order_status_as_non_owner_forbidden(db_session: Session):
    """Test that non-owner users cannot update order status"""
    # Create owner user
    owner = create_test_user(db_session, UserRole.OWNER, "owner4")
    
    # Create consumer user
    consumer = create_test_user(db_session, UserRole.CONSUMER, "consumer5")
    
    # Create product
    product = create_test_product(db_session, owner.id, "004")
    
    # Create address
    address = create_test_address(db_session, consumer.id)
    
    # Create order
    order = create_test_order(db_session, consumer, product, address, OrderStatus.PENDING)
    
    # Generate token for consumer
    token = token_service.create_access_token({"sub": str(consumer.id), "role": consumer.role.value})
    
    # Make request to update status
    response = client.put(
        f"/api/v1/owner/orders/{order.id}/status",
        json={"status": "CONFIRMED"},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 403
    assert "forbidden" in response.json()["detail"].lower()


def test_process_refund_as_owner(db_session: Session):
    """Test processing refund as owner"""
    # Create owner user
    owner = create_test_user(db_session, UserRole.OWNER, "owner5")
    
    # Create consumer user
    consumer = create_test_user(db_session, UserRole.CONSUMER, "consumer6")
    
    # Create product
    product = create_test_product(db_session, owner.id, "005")
    
    # Create address
    address = create_test_address(db_session, consumer.id)
    
    # Create order with PAID status
    order = create_test_order(db_session, consumer, product, address, OrderStatus.CONFIRMED)
    order.payment_status = PaymentStatus.PAID
    db_session.commit()
    
    # Store initial stock
    initial_stock = product.stock_quantity
    
    # Generate token for owner
    token = token_service.create_access_token({"sub": str(owner.id), "role": owner.role.value})
    
    # Make request to process refund
    response = client.post(
        f"/api/v1/owner/orders/{order.id}/refund",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["order_status"] == "REFUNDED"
    assert data["payment_status"] == "REFUNDED"
    assert data["id"] == order.id
    
    # Verify stock was restored
    db_session.refresh(product)
    assert product.stock_quantity == initial_stock + 1


def test_process_refund_as_non_owner_forbidden(db_session: Session):
    """Test that non-owner users cannot process refunds"""
    # Create owner user
    owner = create_test_user(db_session, UserRole.OWNER, "owner6")
    
    # Create consumer user
    consumer = create_test_user(db_session, UserRole.CONSUMER, "consumer7")
    
    # Create product
    product = create_test_product(db_session, owner.id, "006")
    
    # Create address
    address = create_test_address(db_session, consumer.id)
    
    # Create order with PAID status
    order = create_test_order(db_session, consumer, product, address, OrderStatus.CONFIRMED)
    order.payment_status = PaymentStatus.PAID
    db_session.commit()
    
    # Generate token for consumer
    token = token_service.create_access_token({"sub": str(consumer.id), "role": consumer.role.value})
    
    # Make request to process refund
    response = client.post(
        f"/api/v1/owner/orders/{order.id}/refund",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 403
    assert "forbidden" in response.json()["detail"].lower()


def test_process_refund_on_unpaid_order_fails(db_session: Session):
    """Test that refund fails on unpaid orders"""
    # Create owner user
    owner = create_test_user(db_session, UserRole.OWNER, "owner7")
    
    # Create consumer user
    consumer = create_test_user(db_session, UserRole.CONSUMER, "consumer8")
    
    # Create product
    product = create_test_product(db_session, owner.id, "007")
    
    # Create address
    address = create_test_address(db_session, consumer.id)
    
    # Create order with PENDING payment status
    order = create_test_order(db_session, consumer, product, address, OrderStatus.PENDING)
    
    # Generate token for owner
    token = token_service.create_access_token({"sub": str(owner.id), "role": owner.role.value})
    
    # Make request to process refund
    response = client.post(
        f"/api/v1/owner/orders/{order.id}/refund",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 400
    assert "paid" in response.json()["detail"].lower()
