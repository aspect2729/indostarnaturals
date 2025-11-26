"""Unit tests for PaymentService"""
import pytest
from unittest.mock import Mock, patch
from app.services.payment_service import PaymentService
from app.models.enums import PaymentStatus
from decimal import Decimal


@pytest.mark.unit
class TestPaymentService:
    """Unit tests for PaymentService methods"""

    @pytest.fixture
    def payment_service(self, db_session):
        return PaymentService(db_session)

    @pytest.mark.asyncio
    @patch('razorpay.Client')
    async def test_create_razorpay_order(self, mock_client, payment_service, test_order):
        """Test creating Razorpay order"""
        mock_client.return_value.order.create.return_value = {
            'id': 'order_test123',
            'amount': 10000,
            'currency': 'INR'
        }
        
        razorpay_order = await payment_service.create_razorpay_order(
            order_id=test_order.id,
            amount=Decimal('100.00')
        )
        
        assert razorpay_order['id'] == 'order_test123'

    @pytest.mark.asyncio
    async def test_verify_payment_signature(self, payment_service):
        """Test verifying payment signature"""
        payload = {
            'razorpay_order_id': 'order_test',
            'razorpay_payment_id': 'pay_test',
            'razorpay_signature': 'valid_signature'
        }
        
        with patch.object(payment_service, '_verify_signature', return_value=True):
            is_valid = await payment_service.verify_payment_signature(payload)
            assert is_valid is True

    @pytest.mark.asyncio
    async def test_handle_payment_success(self, payment_service, test_order, db_session):
        """Test handling successful payment"""
        payment = await payment_service.handle_payment_success(
            razorpay_payment_id='pay_test123',
            order_id=test_order.id
        )
        
        assert payment.status == PaymentStatus.PAID
        db_session.refresh(test_order)
        assert test_order.payment_status == PaymentStatus.PAID

    @pytest.mark.asyncio
    async def test_handle_payment_failure(self, payment_service, test_order, db_session):
        """Test handling failed payment"""
        payment = await payment_service.handle_payment_failure(
            razorpay_payment_id='pay_test123',
            order_id=test_order.id
        )
        
        assert payment.status == PaymentStatus.FAILED
        db_session.refresh(test_order)
        assert test_order.payment_status == PaymentStatus.FAILED
