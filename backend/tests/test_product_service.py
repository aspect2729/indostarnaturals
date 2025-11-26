"""Unit tests for ProductService"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from app.services.product_service import ProductService
from app.models import Product, Category, ProductImage
from app.models.enums import UserRole
from app.core.exceptions import ValidationException, NotFoundException
from decimal import Decimal


@pytest.mark.unit
class TestProductService:
    """Unit tests for ProductService methods"""

    @pytest.fixture
    def product_service(self, db_session):
        """Create ProductService instance"""
        return ProductService(db_session)

    @pytest.mark.asyncio
    async def test_create_product_success(self, product_service, test_owner, test_category):
        """Test successful product creation"""
        product_data = {
            'title': 'New Product',
            'description': 'New Description',
            'category_id': test_category.id,
            'sku': 'NEW-001',
            'unit_size': '1 Unit',
            'consumer_price': Decimal('150.00'),
            'distributor_price': Decimal('120.00'),
            'stock_quantity': 100
        }
        
        product = await product_service.create_product(test_owner.id, **product_data)
        
        assert product.title == product_data['title']
        assert product.sku == product_data['sku']
        assert product.consumer_price == product_data['consumer_price']
        assert product.distributor_price == product_data['distributor_price']

    @pytest.mark.asyncio
    async def test_create_product_duplicate_sku(self, product_service, test_owner, test_product, test_category):
        """Test product creation with duplicate SKU fails"""
        product_data = {
            'title': 'Duplicate SKU Product',
            'description': 'Description',
            'category_id': test_category.id,
            'sku': test_product.sku,  # Duplicate SKU
            'unit_size': '1 Unit',
            'consumer_price': Decimal('150.00'),
            'distributor_price': Decimal('120.00'),
            'stock_quantity': 100
        }
        
        with pytest.raises(ValidationError):
            await product_service.create_product(test_owner.id, **product_data)

    @pytest.mark.asyncio
    async def test_get_product_by_id_consumer_pricing(self, product_service, test_product):
        """Test getting product with consumer pricing"""
        product = await product_service.get_product_by_id(test_product.id, UserRole.CONSUMER)
        
        assert product.id == test_product.id
        # Should return consumer price
        assert hasattr(product, 'price')
        assert product.price == test_product.consumer_price

    @pytest.mark.asyncio
    async def test_get_product_by_id_distributor_pricing(self, product_service, test_product):
        """Test getting product with distributor pricing"""
        product = await product_service.get_product_by_id(test_product.id, UserRole.DISTRIBUTOR)
        
        assert product.id == test_product.id
        # Should return distributor price
        assert hasattr(product, 'price')
        assert product.price == test_product.distributor_price

    @pytest.mark.asyncio
    async def test_get_products_with_pagination(self, product_service, test_product):
        """Test getting products with pagination"""
        result = await product_service.get_products(
            page=1,
            size=20,
            user_role=UserRole.CONSUMER
        )
        
        assert 'items' in result
        assert 'total' in result
        assert 'page' in result
        assert 'pages' in result
        assert len(result['items']) <= 20

    @pytest.mark.asyncio
    async def test_get_products_with_category_filter(self, product_service, test_product, test_category):
        """Test getting products filtered by category"""
        result = await product_service.get_products(
            category_id=test_category.id,
            user_role=UserRole.CONSUMER
        )
        
        assert all(item.category_id == test_category.id for item in result['items'])

    @pytest.mark.asyncio
    async def test_search_products(self, product_service, test_product):
        """Test searching products"""
        results = await product_service.search_products(
            query='Test',
            user_role=UserRole.CONSUMER
        )
        
        assert len(results) > 0
        assert any('Test' in product.title for product in results)

    @pytest.mark.asyncio
    async def test_update_product_success(self, product_service, test_product):
        """Test updating product"""
        update_data = {
            'title': 'Updated Product',
            'consumer_price': Decimal('200.00')
        }
        
        updated_product = await product_service.update_product(
            test_product.id,
            **update_data
        )
        
        assert updated_product.title == update_data['title']
        assert updated_product.consumer_price == update_data['consumer_price']

    @pytest.mark.asyncio
    async def test_update_stock_with_audit(self, product_service, test_product, test_owner, db_session):
        """Test updating stock creates audit log"""
        quantity_delta = 10
        old_quantity = test_product.stock_quantity
        
        updated_product = await product_service.update_stock(
            product_id=test_product.id,
            quantity_delta=quantity_delta,
            actor_id=test_owner.id
        )
        
        assert updated_product.stock_quantity == old_quantity + quantity_delta
        
        # Check audit log was created
        from app.models import AuditLog
        audit_log = db_session.query(AuditLog).filter(
            AuditLog.actor_id == test_owner.id,
            AuditLog.object_id == test_product.id,
            AuditLog.action_type == 'STOCK_UPDATED'
        ).first()
        
        assert audit_log is not None
        assert audit_log.details['old_quantity'] == old_quantity
        assert audit_log.details['new_quantity'] == old_quantity + quantity_delta

    @pytest.mark.asyncio
    async def test_update_stock_negative_not_allowed(self, product_service, test_product, test_owner):
        """Test updating stock to negative value fails"""
        quantity_delta = -(test_product.stock_quantity + 10)
        
        with pytest.raises(ValidationError):
            await product_service.update_stock(
                product_id=test_product.id,
                quantity_delta=quantity_delta,
                actor_id=test_owner.id
            )

    @pytest.mark.asyncio
    async def test_soft_delete_product(self, product_service, test_product):
        """Test soft deleting product"""
        deleted_product = await product_service.delete_product(test_product.id)
        
        assert deleted_product.is_active is False
        
        # Product should not appear in active product queries
        result = await product_service.get_products(user_role=UserRole.CONSUMER)
        assert not any(p.id == test_product.id for p in result['items'])

    @pytest.mark.asyncio
    @patch('app.services.image_service.ImageService.upload_image')
    async def test_upload_product_image(self, mock_upload, product_service, test_product):
        """Test uploading product image"""
        mock_upload.return_value = 'https://cdn.example.com/test.jpg'
        
        mock_file = Mock()
        mock_file.filename = 'test.jpg'
        mock_file.content_type = 'image/jpeg'
        
        image = await product_service.upload_image(
            product_id=test_product.id,
            image_file=mock_file
        )
        
        assert image.product_id == test_product.id
        assert image.url == 'https://cdn.example.com/test.jpg'

    @pytest.mark.asyncio
    async def test_get_low_stock_products(self, product_service, test_product, db_session):
        """Test getting low stock products"""
        # Set product to low stock
        test_product.stock_quantity = 5
        db_session.commit()
        
        low_stock_products = await product_service.get_low_stock_products(threshold=10)
        
        assert len(low_stock_products) > 0
        assert all(p.stock_quantity <= 10 for p in low_stock_products)
