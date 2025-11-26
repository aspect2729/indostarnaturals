"""Unit tests for SubscriptionService"""
import pytest
from unittest.mock import Mock, patch
from app.services.subscription_service import SubscriptionService
from app.models.enums import SubscriptionStatus, SubscriptionFrequency
from decimal import Decimal
from datetime import date


@pytest.mark.unit
class TestSubscriptionService:
    """Unit tests for SubscriptionService methods"""

    @pytest.fixture
    def subscription_service(self, db_session):
        return SubscriptionService(db_session)

    @pytest.mark.asyncio
    @patch('app.services.payment_service.PaymentService.create_razorpay_subscription')
    async def test_create_subscription(self, mock_razorpay, subscription_service, test_user, test_product, test_address):
        """Test creating subscription"""
        mock_razorpay.return_value = {'id': 'sub_test123'}
        
        subscription = await subscription_service.create_subscription(
            user_id=test_user.id,
            product_id=test_product.id,
            plan_frequency=SubscriptionFrequency.DAILY,
            start_date=date.today(),
            delivery_address_id=test_address.id
        )
        
        assert subscription.user_id == test_user.id
        assert subscription.status == SubscriptionStatus.ACTIVE

    @pytest.mark.asyncio
    async def test_pause_subscription(self, subscription_service, db_session, test_user, test_product, test_address):
        """Test pausing subscription"""
        from app.models import Subscription
        subscription = Subscription(
            user_id=test_user.id,
            product_id=test_product.id,
            razorpay_subscription_id='sub_test',
            plan_frequency=SubscriptionFrequency.DAILY,
            start_date=date.today(),
            next_delivery_date=date.today(),
            delivery_address_id=test_address.id,
            status=SubscriptionStatus.ACTIVE
        )
        db_session.add(subscription)
        db_session.commit()
        
        paused = await subscription_service.pause_subscription(subscription.id, test_user.id)
        
        assert paused.status == SubscriptionStatus.PAUSED

    @pytest.mark.asyncio
    async def test_cancel_subscription(self, subscription_service, db_session, test_user, test_product, test_address):
        """Test cancelling subscription"""
        from app.models import Subscription
        subscription = Subscription(
            user_id=test_user.id,
            product_id=test_product.id,
            razorpay_subscription_id='sub_test',
            plan_frequency=SubscriptionFrequency.DAILY,
            start_date=date.today(),
            next_delivery_date=date.today(),
            delivery_address_id=test_address.id,
            status=SubscriptionStatus.ACTIVE
        )
        db_session.add(subscription)
        db_session.commit()
        
        cancelled = await subscription_service.cancel_subscription(subscription.id, test_user.id)
        
        assert cancelled.status == SubscriptionStatus.CANCELLED
