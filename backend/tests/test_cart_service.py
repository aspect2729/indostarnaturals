"""Unit tests for CartService"""
import pytest
from unittest.mock import Mock, AsyncMock
from app.services.cart_service import CartService
from app.models import Cart, CartItem
from app.models.enums import UserRole
from app.core.exceptions import ValidationException, NotFoundException
from decimal import Decimal


@pytest.mark.unit
class TestCartService:
    """Unit tests for CartService methods"""

    @pytest.fixture
    def cart_service(self, db_session):
        """Create CartService instance"""
        return CartService(db_session)

    @pytest.mark.asyncio
    async def test_get_or_create_cart(self, cart_service, test_user):
        """Test getting or creating cart for user"""
        cart = await cart_service.get_or_create_cart(test_user.id)
        
        assert cart.user_id == test_user.id
        assert cart.discount_amount == Decimal('0.00')

    @pytest.mark.asyncio
    async def test_add_item_to_cart(self, cart_service, test_user, test_product):
        """Test adding item to cart"""
        cart = await cart_service.add_item(
            user_id=test_user.id,
            product_id=test_product.id,
            quantity=2,
            user_role=UserRole.CONSUMER
        )
        
        assert len(cart.items) > 0
        cart_item = cart.items[0]
        assert cart_item.product_id == test_product.id
        assert cart_item.quantity == 2
        assert cart_item.unit_price == test_product.consumer_price

    @pytest.mark.asyncio
    async def test_add_item_distributor_pricing(self, cart_service, test_distributor, test_product):
        """Test adding item with distributor pricing"""
        cart = await cart_service.add_item(
            user_id=test_distributor.id,
            product_id=test_product.id,
            quantity=2,
            user_role=UserRole.DISTRIBUTOR
        )
        
        cart_item = cart.items[0]
        assert cart_item.unit_price == test_product.distributor_price

    @pytest.mark.asyncio
    async def test_add_item_insufficient_stock(self, cart_service, test_user, test_product, db_session):
        """Test adding item with insufficient stock fails"""
        # Set low stock
        test_product.stock_quantity = 1
        db_session.commit()
        
        with pytest.raises(ValidationException, match="Insufficient stock"):
            await cart_service.add_item(
                user_id=test_user.id,
                product_id=test_product.id,
                quantity=10,
                user_role=UserRole.CONSUMER
            )

    @pytest.mark.asyncio
    async def test_update_item_quantity(self, cart_service, test_user, test_product):
        """Test updating cart item quantity"""
        # First add item
        cart = await cart_service.add_item(
            user_id=test_user.id,
            product_id=test_product.id,
            quantity=2,
            user_role=UserRole.CONSUMER
        )
        
        cart_item_id = cart.items[0].id
        
        # Update quantity
        updated_cart = await cart_service.update_item_quantity(
            user_id=test_user.id,
            item_id=cart_item_id,
            quantity=5
        )
        
        updated_item = next(item for item in updated_cart.items if item.id == cart_item_id)
        assert updated_item.quantity == 5

    @pytest.mark.asyncio
    async def test_cart_total_recalculation(self, cart_service, test_user, test_product):
        """Test cart total is recalculated correctly"""
        cart = await cart_service.add_item(
            user_id=test_user.id,
            product_id=test_product.id,
            quantity=3,
            user_role=UserRole.CONSUMER
        )
        
        expected_total = test_product.consumer_price * 3
        assert cart.total_amount == expected_total

    @pytest.mark.asyncio
    async def test_remove_item_from_cart(self, cart_service, test_user, test_product):
        """Test removing item from cart"""
        # First add item
        cart = await cart_service.add_item(
            user_id=test_user.id,
            product_id=test_product.id,
            quantity=2,
            user_role=UserRole.CONSUMER
        )
        
        cart_item_id = cart.items[0].id
        
        # Remove item
        updated_cart = await cart_service.remove_item(
            user_id=test_user.id,
            item_id=cart_item_id
        )
        
        assert not any(item.id == cart_item_id for item in updated_cart.items)

    @pytest.mark.asyncio
    async def test_apply_coupon_success(self, cart_service, test_user, test_product, db_session):
        """Test applying valid coupon"""
        # Add item to cart
        cart = await cart_service.add_item(
            user_id=test_user.id,
            product_id=test_product.id,
            quantity=2,
            user_role=UserRole.CONSUMER
        )
        
        # Mock coupon validation
        with patch.object(cart_service, 'validate_coupon', return_value=Decimal('10.00')):
            updated_cart = await cart_service.apply_coupon(
                user_id=test_user.id,
                coupon_code='TEST10'
            )
            
            assert updated_cart.coupon_code == 'TEST10'
            assert updated_cart.discount_amount == Decimal('10.00')

    @pytest.mark.asyncio
    async def test_remove_coupon(self, cart_service, test_user, test_product):
        """Test removing coupon from cart"""
        # Add item and coupon
        cart = await cart_service.add_item(
            user_id=test_user.id,
            product_id=test_product.id,
            quantity=2,
            user_role=UserRole.CONSUMER
        )
        
        with patch.object(cart_service, 'validate_coupon', return_value=Decimal('10.00')):
            cart = await cart_service.apply_coupon(
                user_id=test_user.id,
                coupon_code='TEST10'
            )
        
        # Remove coupon
        updated_cart = await cart_service.remove_coupon(test_user.id)
        
        assert updated_cart.coupon_code is None
        assert updated_cart.discount_amount == Decimal('0.00')

    @pytest.mark.asyncio
    async def test_validate_cart_success(self, cart_service, test_user, test_product):
        """Test validating cart with sufficient stock"""
        cart = await cart_service.add_item(
            user_id=test_user.id,
            product_id=test_product.id,
            quantity=2,
            user_role=UserRole.CONSUMER
        )
        
        validation_result = await cart_service.validate_cart(test_user.id)
        
        assert validation_result['is_valid'] is True
        assert len(validation_result['errors']) == 0

    @pytest.mark.asyncio
    async def test_validate_cart_insufficient_stock(self, cart_service, test_user, test_product, db_session):
        """Test validating cart with insufficient stock"""
        # Add item
        cart = await cart_service.add_item(
            user_id=test_user.id,
            product_id=test_product.id,
            quantity=10,
            user_role=UserRole.CONSUMER
        )
        
        # Reduce stock
        test_product.stock_quantity = 5
        db_session.commit()
        
        validation_result = await cart_service.validate_cart(test_user.id)
        
        assert validation_result['is_valid'] is False
        assert len(validation_result['errors']) > 0

    @pytest.mark.asyncio
    async def test_clear_cart(self, cart_service, test_user, test_product):
        """Test clearing all items from cart"""
        # Add items
        await cart_service.add_item(
            user_id=test_user.id,
            product_id=test_product.id,
            quantity=2,
            user_role=UserRole.CONSUMER
        )
        
        # Clear cart
        cleared_cart = await cart_service.clear_cart(test_user.id)
        
        assert len(cleared_cart.items) == 0
        assert cleared_cart.total_amount == Decimal('0.00')
