"""Unit tests for OrderService"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from app.services.order_service import OrderService
from app.models import Order, OrderItem
from app.models.enums import OrderStatus, PaymentStatus
from app.core.exceptions import ValidationException
from decimal import Decimal


@pytest.mark.unit
class TestOrderService:
    """Unit tests for OrderService methods"""

    @pytest.fixture
    def order_service(self, db_session):
        return OrderService(db_session)

    @pytest.mark.asyncio
    async def test_create_order_success(self, order_service, test_user, test_product, test_address):
        """Test successful order creation"""
        # Create cart with items
        from app.services.cart_service import CartService
        cart_service = CartService(order_service.db)
        await cart_service.add_item(test_user.id, test_product.id, 2, test_user.role)
        
        order = await order_service.create_order(
            user_id=test_user.id,
            address_id=test_address.id
        )
        
        assert order.user_id == test_user.id
        assert order.order_status == OrderStatus.PENDING
        assert order.payment_status == PaymentStatus.PENDING
        assert len(order.items) > 0

    @pytest.mark.asyncio
    async def test_create_order_reduces_stock(self, order_service, test_user, test_product, test_address, db_session):
        """Test order creation reduces product stock"""
        initial_stock = test_product.stock_quantity
        quantity = 2
        
        from app.services.cart_service import CartService
        cart_service = CartService(order_service.db)
        await cart_service.add_item(test_user.id, test_product.id, quantity, test_user.role)
        
        await order_service.create_order(test_user.id, test_address.id)
        
        db_session.refresh(test_product)
        assert test_product.stock_quantity == initial_stock - quantity

    @pytest.mark.asyncio
    async def test_get_user_orders(self, order_service, test_order):
        """Test getting user orders"""
        result = await order_service.get_user_orders(test_order.user_id)
        
        assert 'items' in result
        assert len(result['items']) > 0

    @pytest.mark.asyncio
    async def test_update_order_status(self, order_service, test_order, test_owner):
        """Test updating order status"""
        new_status = OrderStatus.CONFIRMED
        
        updated_order = await order_service.update_order_status(
            order_id=test_order.id,
            status=new_status,
            actor_id=test_owner.id
        )
        
        assert updated_order.order_status == new_status

    @pytest.mark.asyncio
    @patch('app.services.notification_service.NotificationService.send_email')
    async def test_status_change_sends_notification(self, mock_send_email, order_service, test_order, test_owner):
        """Test status change triggers notification"""
        mock_send_email.return_value = True
        
        await order_service.update_order_status(
            order_id=test_order.id,
            status=OrderStatus.CONFIRMED,
            actor_id=test_owner.id
        )
        
        mock_send_email.assert_called_once()
