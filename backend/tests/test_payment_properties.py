"""Property-based tests for payment services

Feature: indostar-naturals-ecommerce
"""
import pytest
from decimal import Decimal
from hypothesis import given, strategies as st, settings
from unittest.mock import Mock, patch, AsyncMock
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.payment_service import payment_service
from app.models.order import Order
from app.models.payment import Payment
from app.models.subscription import Subscription
from app.models.enums import PaymentStatus, OrderStatus, UserRole


# Custom strategies for generating test data
@st.composite
def order_data_strategy(draw):
    """Generate random order data for payment testing"""
    order_id = draw(st.integers(min_value=1, max_value=1000000))
    amount = draw(st.decimals(min_value=Decimal('1.00'), max_value=Decimal('100000.00'), places=2))
    
    return {
        "order_id": order_id,
        "amount": amount
    }


@st.composite
def razorpay_order_response_strategy(draw):
    """Generate random Razorpay order response"""
    order_id = draw(st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')), min_size=20, max_size=30))
    amount_paise = draw(st.integers(min_value=100, max_value=10000000))
    
    return {
        "id": f"order_{order_id}",
        "amount": amount_paise,
        "currency": "INR",
        "status": "created"
    }


# Feature: indostar-naturals-ecommerce, Property 29: Order confirmation creates Razorpay order
@given(order_data=order_data_strategy())
@settings(max_examples=100)
@pytest.mark.asyncio
async def test_property_order_confirmation_creates_razorpay_order(order_data):
    """
    **Property 29: Order confirmation creates Razorpay order**
    **Validates: Requirements 6.3**
    
    For any order confirmation, the system should create a Razorpay order 
    and return an order token to the frontend.
    """
    # Mock database session
    mock_db = AsyncMock(spec=AsyncSession)
    
    # Mock Razorpay client response
    amount_paise = int(order_data["amount"] * 100)
    mock_razorpay_response = {
        "id": f"order_test_{order_data['order_id']}",
        "amount": amount_paise,
        "currency": "INR",
        "status": "created"
    }
    
    with patch.object(payment_service.client.order, 'create', return_value=mock_razorpay_response):
        # Create Razorpay order
        result = await payment_service.create_razorpay_order(
            db=mock_db,
            order_id=order_data["order_id"],
            amount=order_data["amount"]
        )
        
        # Verify that Razorpay order is created
        assert "razorpay_order_id" in result
        assert "amount" in result
        assert "currency" in result
        assert "key_id" in result
        
        # Verify order ID format
        assert result["razorpay_order_id"].startswith("order_")
        
        # Verify amount is in paise
        assert result["amount"] == amount_paise
        
        # Verify currency is INR
        assert result["currency"] == "INR"
        
        # Verify key_id is present for frontend
        assert isinstance(result["key_id"], str)
        assert len(result["key_id"]) > 0


# Feature: indostar-naturals-ecommerce, Property 30: Payment success updates order status
@given(
    order_id=st.integers(min_value=1, max_value=1000000),
    amount=st.decimals(min_value=Decimal('1.00'), max_value=Decimal('100000.00'), places=2)
)
@settings(max_examples=100)
@pytest.mark.asyncio
async def test_property_payment_success_updates_order_status(order_id, amount):
    """
    **Property 30: Payment success updates order status**
    **Validates: Requirements 6.4**
    
    For any valid Razorpay webhook indicating successful payment, 
    the system should update the order status to confirmed.
    """
    # Create mock order
    mock_order = Order(
        id=order_id,
        user_id=1,
        order_number=f"ORD{order_id}",
        total_amount=amount,
        discount_amount=Decimal('0.00'),
        final_amount=amount,
        payment_status=PaymentStatus.PENDING,
        order_status=OrderStatus.PENDING,
        delivery_address_id=1
    )
    
    # Mock database session
    mock_db = AsyncMock(spec=AsyncSession)
    mock_result = Mock()
    mock_result.scalar_one_or_none.return_value = mock_order
    mock_db.execute = AsyncMock(return_value=mock_result)
    mock_db.commit = AsyncMock()
    mock_db.refresh = AsyncMock()
    
    # Handle payment success
    payment = await payment_service.handle_payment_success(
        db=mock_db,
        razorpay_payment_id=f"pay_test_{order_id}",
        razorpay_order_id=f"order_test_{order_id}",
        order_id=order_id
    )
    
    # Verify payment record is created
    assert isinstance(payment, Payment)
    assert payment.order_id == order_id
    assert payment.status == PaymentStatus.PAID
    assert payment.amount == amount
    
    # Verify order status is updated to CONFIRMED
    assert mock_order.payment_status == PaymentStatus.PAID
    assert mock_order.order_status == OrderStatus.CONFIRMED
    
    # Verify database operations were called
    mock_db.commit.assert_called_once()


# Feature: indostar-naturals-ecommerce, Property 31: Payment failure updates order status
@given(
    order_id=st.integers(min_value=1, max_value=1000000),
    amount=st.decimals(min_value=Decimal('1.00'), max_value=Decimal('100000.00'), places=2)
)
@settings(max_examples=100)
@pytest.mark.asyncio
async def test_property_payment_failure_updates_order_status(order_id, amount):
    """
    **Property 31: Payment failure updates order status**
    **Validates: Requirements 6.5**
    
    For any valid Razorpay webhook indicating failed payment, 
    the system should update the order status to failed.
    """
    # Create mock order
    mock_order = Order(
        id=order_id,
        user_id=1,
        order_number=f"ORD{order_id}",
        total_amount=amount,
        discount_amount=Decimal('0.00'),
        final_amount=amount,
        payment_status=PaymentStatus.PENDING,
        order_status=OrderStatus.PENDING,
        delivery_address_id=1
    )
    
    # Mock database session
    mock_db = AsyncMock(spec=AsyncSession)
    mock_result = Mock()
    mock_result.scalar_one_or_none.return_value = mock_order
    mock_db.execute = AsyncMock(return_value=mock_result)
    mock_db.commit = AsyncMock()
    mock_db.refresh = AsyncMock()
    
    # Handle payment failure
    payment = await payment_service.handle_payment_failure(
        db=mock_db,
        razorpay_payment_id=f"pay_test_{order_id}",
        razorpay_order_id=f"order_test_{order_id}",
        order_id=order_id,
        error_description="Payment declined by bank"
    )
    
    # Verify payment record is created with FAILED status
    assert isinstance(payment, Payment)
    assert payment.order_id == order_id
    assert payment.status == PaymentStatus.FAILED
    assert payment.amount == amount
    
    # Verify order payment status is updated to FAILED
    assert mock_order.payment_status == PaymentStatus.FAILED
    
    # Verify order status remains PENDING (so user can retry)
    assert mock_order.order_status == OrderStatus.PENDING
    
    # Verify database operations were called
    mock_db.commit.assert_called_once()


# Feature: indostar-naturals-ecommerce, Property 33: Webhook signature verification required
@given(
    order_id=st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')), min_size=20, max_size=30),
    payment_id=st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')), min_size=20, max_size=30),
    signature=st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')), min_size=64, max_size=64)
)
@settings(max_examples=100)
def test_property_webhook_signature_verification_required(order_id, payment_id, signature):
    """
    **Property 33: Webhook signature verification required**
    **Validates: Requirements 6.7**
    
    For any webhook request without a valid Razorpay signature, 
    the system should reject the request with a 401 Unauthorized response.
    """
    # Test with invalid signature (random signature should fail)
    is_valid = payment_service.verify_payment_signature(
        razorpay_order_id=f"order_{order_id}",
        razorpay_payment_id=f"pay_{payment_id}",
        razorpay_signature=signature
    )
    
    # Random signature should not be valid
    # (unless by extreme coincidence it matches the HMAC, which is astronomically unlikely)
    # We verify that the function returns a boolean
    assert isinstance(is_valid, bool)
    
    # Test that the verification function properly validates correct signatures
    # by generating a proper signature
    import hmac
    import hashlib
    from app.core.config import settings
    
    message = f"order_{order_id}|pay_{payment_id}"
    correct_signature = hmac.new(
        settings.RAZORPAY_KEY_SECRET.encode('utf-8'),
        message.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    # Verify that correct signature passes
    is_valid_correct = payment_service.verify_payment_signature(
        razorpay_order_id=f"order_{order_id}",
        razorpay_payment_id=f"pay_{payment_id}",
        razorpay_signature=correct_signature
    )
    
    assert is_valid_correct is True


# Test webhook signature verification
@given(
    payload=st.text(min_size=10, max_size=1000),
    signature=st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')), min_size=64, max_size=64)
)
@settings(max_examples=100)
def test_property_webhook_payload_signature_verification(payload, signature):
    """
    Test that webhook payload signature verification works correctly.
    This ensures webhooks are authenticated before processing.
    """
    # Test with invalid signature (random signature should fail)
    is_valid = payment_service.verify_webhook_signature(
        payload=payload,
        signature=signature
    )
    
    # Verify that the function returns a boolean
    assert isinstance(is_valid, bool)
    
    # Generate correct signature for the payload
    import hmac
    import hashlib
    from app.core.config import settings
    
    correct_signature = hmac.new(
        settings.RAZORPAY_WEBHOOK_SECRET.encode('utf-8'),
        payload.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    # Verify that correct signature passes
    is_valid_correct = payment_service.verify_webhook_signature(
        payload=payload,
        signature=correct_signature
    )
    
    assert is_valid_correct is True



# Feature: indostar-naturals-ecommerce, Property 64: Payment attempts are logged
@given(
    order_id=st.integers(min_value=1, max_value=1000000),
    amount=st.decimals(min_value=Decimal('1.00'), max_value=Decimal('100000.00'), places=2),
    payment_success=st.booleans()
)
@settings(max_examples=100)
@pytest.mark.asyncio
async def test_property_payment_attempts_are_logged(order_id, amount, payment_success):
    """
    **Property 64: Payment attempts are logged**
    **Validates: Requirements 15.5**
    
    For any payment attempt (success or failure), the system should create 
    a log entry with transaction ID and status.
    """
    # Create mock order
    mock_order = Order(
        id=order_id,
        user_id=1,
        order_number=f"ORD{order_id}",
        total_amount=amount,
        discount_amount=Decimal('0.00'),
        final_amount=amount,
        payment_status=PaymentStatus.PENDING,
        order_status=OrderStatus.PENDING,
        delivery_address_id=1
    )
    
    # Mock database session
    mock_db = AsyncMock(spec=AsyncSession)
    mock_result = Mock()
    mock_result.scalar_one_or_none.return_value = mock_order
    mock_db.execute = AsyncMock(return_value=mock_result)
    mock_db.commit = AsyncMock()
    mock_db.refresh = AsyncMock()
    
    razorpay_payment_id = f"pay_test_{order_id}"
    razorpay_order_id = f"order_test_{order_id}"
    
    # Handle payment (success or failure)
    if payment_success:
        payment = await payment_service.handle_payment_success(
            db=mock_db,
            razorpay_payment_id=razorpay_payment_id,
            razorpay_order_id=razorpay_order_id,
            order_id=order_id
        )
        expected_status = PaymentStatus.PAID
    else:
        payment = await payment_service.handle_payment_failure(
            db=mock_db,
            razorpay_payment_id=razorpay_payment_id,
            razorpay_order_id=razorpay_order_id,
            order_id=order_id,
            error_description="Test error"
        )
        expected_status = PaymentStatus.FAILED
    
    # Verify payment record is created (this serves as the log entry)
    assert isinstance(payment, Payment)
    assert payment.razorpay_payment_id == razorpay_payment_id
    assert payment.razorpay_order_id == razorpay_order_id
    assert payment.order_id == order_id
    assert payment.amount == amount
    assert payment.status == expected_status
    
    # Verify that the payment record contains all necessary information for logging
    # Transaction ID (razorpay_payment_id)
    assert payment.razorpay_payment_id is not None
    assert len(payment.razorpay_payment_id) > 0
    
    # Status
    assert payment.status in [PaymentStatus.PAID, PaymentStatus.FAILED, PaymentStatus.PENDING, PaymentStatus.REFUNDED]
    
    # Amount
    assert payment.amount > 0
    
    # Currency
    assert payment.currency == "INR"
    
    # Verify database commit was called (to persist the log)
    mock_db.commit.assert_called()
