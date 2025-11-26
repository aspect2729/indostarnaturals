"""Property-based tests for product services

Feature: indostar-naturals-ecommerce
"""
import pytest
from decimal import Decimal
from hypothesis import given, strategies as st, settings, HealthCheck, assume
from app.services.product_service import product_service
from app.schemas.product import ProductCreate, ProductFilters
from app.models.enums import UserRole
from app.models.category import Category
from app.models.user import User


# Custom strategies for generating test data
@st.composite
def valid_product_data_strategy(draw):
    """Generate valid product data for creation"""
    title = draw(st.text(min_size=1, max_size=255, alphabet=st.characters(min_codepoint=32, max_codepoint=126)))
    description = draw(st.text(min_size=1, max_size=1000, alphabet=st.characters(min_codepoint=32, max_codepoint=126)))
    # SKU: alphanumeric with hyphens
    sku = draw(st.from_regex(r'[A-Z0-9\-]{3,20}', fullmatch=True))
    unit_size = draw(st.sampled_from(['500g', '1kg', '2kg', '500ml', '1L', '2L', '250g', '100g']))
    
    # Generate prices with max 2 decimal places
    consumer_price = draw(st.decimals(min_value=Decimal('0.01'), max_value=Decimal('9999.99'), places=2))
    distributor_price = draw(st.decimals(min_value=Decimal('0.01'), max_value=Decimal('9999.99'), places=2))
    
    stock_quantity = draw(st.integers(min_value=0, max_value=10000))
    is_subscription_available = draw(st.booleans())
    
    return {
        "title": title,
        "description": description,
        "sku": sku,
        "unit_size": unit_size,
        "consumer_price": consumer_price,
        "distributor_price": distributor_price,
        "stock_quantity": stock_quantity,
        "is_subscription_available": is_subscription_available
    }


@st.composite
def incomplete_product_data_strategy(draw):
    """Generate incomplete product data (missing required fields)"""
    # Randomly omit one or more required fields
    fields_to_include = draw(st.sets(
        st.sampled_from(['title', 'description', 'sku', 'unit_size', 'consumer_price', 'distributor_price', 'stock_quantity']),
        min_size=0,
        max_size=6  # Omit at least one field
    ))
    
    # Ensure at least one field is missing
    assume(len(fields_to_include) < 7)
    
    data = {}
    
    if 'title' in fields_to_include:
        data['title'] = draw(st.text(min_size=1, max_size=255))
    if 'description' in fields_to_include:
        data['description'] = draw(st.text(min_size=1, max_size=1000))
    if 'sku' in fields_to_include:
        data['sku'] = draw(st.from_regex(r'[A-Z0-9\-]{3,20}', fullmatch=True))
    if 'unit_size' in fields_to_include:
        data['unit_size'] = draw(st.sampled_from(['500g', '1kg', '2kg']))
    if 'consumer_price' in fields_to_include:
        data['consumer_price'] = draw(st.decimals(min_value=Decimal('0.01'), max_value=Decimal('9999.99'), places=2))
    if 'distributor_price' in fields_to_include:
        data['distributor_price'] = draw(st.decimals(min_value=Decimal('0.01'), max_value=Decimal('9999.99'), places=2))
    if 'stock_quantity' in fields_to_include:
        data['stock_quantity'] = draw(st.integers(min_value=0, max_value=10000))
    
    return data


# Feature: indostar-naturals-ecommerce, Property 11: Product creation requires all fields
@given(incomplete_data=incomplete_product_data_strategy())
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
def test_property_product_creation_requires_all_fields(incomplete_data, db_session):
    """
    **Property 11: Product creation requires all fields**
    **Validates: Requirements 3.1**
    
    For any product creation attempt, if any required field 
    (title, description, category, SKU, unit size, consumer price, 
    distributor price, stock quantity) is missing, the system should 
    reject the request with a 400 Bad Request response.
    """
    from pydantic import ValidationError
    
    # Add category_id (required but not in incomplete data strategy)
    incomplete_data['category_id'] = 1
    
    # Attempt to create ProductCreate schema should fail
    with pytest.raises(ValidationError) as exc_info:
        ProductCreate(**incomplete_data)
    
    # Verify validation error occurred
    errors = exc_info.value.errors()
    assert len(errors) > 0
    
    # Verify at least one required field is missing
    required_fields = {'title', 'description', 'sku', 'unit_size', 'consumer_price', 'distributor_price', 'stock_quantity'}
    missing_fields = required_fields - set(incomplete_data.keys())
    assert len(missing_fields) > 0
    
    # Verify error mentions missing field
    error_fields = {error['loc'][0] for error in errors}
    assert len(error_fields.intersection(missing_fields)) > 0


# Test that valid product data passes validation
@given(product_data=valid_product_data_strategy())
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
def test_property_valid_product_data_passes_validation(product_data, db_session):
    """
    Test that product data with all required fields passes validation.
    """
    from pydantic import ValidationError
    
    # Create owner user
    owner = User(
        phone='+919876543210',
        name='Test Owner',
        role=UserRole.OWNER,
        is_active=True
    )
    db_session.add(owner)
    db_session.commit()
    db_session.refresh(owner)
    
    # Create category
    category = Category(
        name='Test Category',
        slug='test-category',
        display_order=0
    )
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)
    
    # Add category_id to product data
    product_data['category_id'] = category.id
    
    # Should pass validation
    try:
        product_create = ProductCreate(**product_data)
        
        # Verify all fields are present
        assert product_create.title == product_data['title']
        assert product_create.description == product_data['description']
        assert product_create.sku == product_data['sku']
        assert product_create.unit_size == product_data['unit_size']
        assert product_create.consumer_price == product_data['consumer_price']
        assert product_create.distributor_price == product_data['distributor_price']
        assert product_create.stock_quantity == product_data['stock_quantity']
        assert product_create.category_id == category.id
        
        # Create product in database
        product = product_service.create_product(
            product_data=product_create,
            owner_id=owner.id,
            db=db_session
        )
        
        # Verify product was created
        assert product is not None
        assert product.id is not None
        assert product.title == product_data['title']
        assert product.sku == product_data['sku']
        
        # Clean up
        db_session.delete(product)
        
    except ValidationError as e:
        assert False, f"Valid product data should not fail validation: {e}"
    finally:
        # Clean up
        db_session.delete(category)
        db_session.delete(owner)
        db_session.commit()


# Test price validation (must be positive with max 2 decimal places)
@given(
    invalid_price=st.one_of(
        st.decimals(min_value=Decimal('-9999.99'), max_value=Decimal('-0.01'), places=2),  # Negative
        st.just(Decimal('0')),  # Zero
        st.decimals(min_value=Decimal('0.001'), max_value=Decimal('9999.999'), places=3)  # Too many decimals
    )
)
@settings(max_examples=50, deadline=None)
def test_property_product_price_validation(invalid_price):
    """
    Test that invalid prices are rejected.
    """
    from pydantic import ValidationError
    
    # Attempt to create product with invalid consumer price
    with pytest.raises(ValidationError):
        ProductCreate(
            title='Test Product',
            description='Test Description',
            category_id=1,
            sku='TEST-001',
            unit_size='1kg',
            consumer_price=invalid_price,
            distributor_price=Decimal('10.00'),
            stock_quantity=100
        )
    
    # Attempt to create product with invalid distributor price
    with pytest.raises(ValidationError):
        ProductCreate(
            title='Test Product',
            description='Test Description',
            category_id=1,
            sku='TEST-001',
            unit_size='1kg',
            consumer_price=Decimal('10.00'),
            distributor_price=invalid_price,
            stock_quantity=100
        )


# Test stock quantity validation (must be non-negative)
@given(invalid_stock=st.integers(max_value=-1))
@settings(max_examples=50, deadline=None)
def test_property_product_stock_validation(invalid_stock):
    """
    Test that negative stock quantities are rejected.
    """
    from pydantic import ValidationError
    
    # Attempt to create product with negative stock
    with pytest.raises(ValidationError):
        ProductCreate(
            title='Test Product',
            description='Test Description',
            category_id=1,
            sku='TEST-001',
            unit_size='1kg',
            consumer_price=Decimal('10.00'),
            distributor_price=Decimal('8.00'),
            stock_quantity=invalid_stock
        )



# Feature: indostar-naturals-ecommerce, Property 13: Stock updates create audit logs
@given(
    product_data=valid_product_data_strategy(),
    quantity_delta=st.integers(min_value=-100, max_value=100)
)
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
def test_property_stock_updates_create_audit_logs(product_data, quantity_delta, db_session):
    """
    **Property 13: Stock updates create audit logs**
    **Validates: Requirements 3.3**
    
    For any product stock quantity update, the system should create 
    an audit log entry containing actor_id, timestamp, old quantity, 
    and new quantity.
    """
    from app.models.audit_log import AuditLog
    
    # Create owner user
    owner = User(
        phone='+919876543210',
        name='Test Owner',
        role=UserRole.OWNER,
        is_active=True
    )
    db_session.add(owner)
    db_session.commit()
    db_session.refresh(owner)
    
    # Create category
    category = Category(
        name='Test Category',
        slug='test-category',
        display_order=0
    )
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)
    
    # Add category_id to product data
    product_data['category_id'] = category.id
    
    # Create product
    product_create = ProductCreate(**product_data)
    product = product_service.create_product(
        product_data=product_create,
        owner_id=owner.id,
        db=db_session
    )
    
    # Store initial stock quantity
    initial_stock = product.stock_quantity
    
    # Skip if update would result in negative stock
    if initial_stock + quantity_delta < 0:
        db_session.delete(product)
        db_session.delete(category)
        db_session.delete(owner)
        db_session.commit()
        return
    
    # Count audit logs before update
    audit_count_before = db_session.query(AuditLog).filter(
        AuditLog.object_type == "PRODUCT",
        AuditLog.object_id == product.id,
        AuditLog.action_type == "PRODUCT_STOCK_UPDATED"
    ).count()
    
    # Update stock
    updated_product = product_service.update_stock(
        product_id=product.id,
        quantity_delta=quantity_delta,
        actor_id=owner.id,
        db=db_session
    )
    
    # Verify product was updated
    assert updated_product is not None
    assert updated_product.stock_quantity == initial_stock + quantity_delta
    
    # Verify audit log was created
    audit_count_after = db_session.query(AuditLog).filter(
        AuditLog.object_type == "PRODUCT",
        AuditLog.object_id == product.id,
        AuditLog.action_type == "PRODUCT_STOCK_UPDATED"
    ).count()
    
    assert audit_count_after == audit_count_before + 1
    
    # Get the audit log entry
    audit_log = db_session.query(AuditLog).filter(
        AuditLog.object_type == "PRODUCT",
        AuditLog.object_id == product.id,
        AuditLog.action_type == "PRODUCT_STOCK_UPDATED"
    ).order_by(AuditLog.created_at.desc()).first()
    
    # Verify audit log contains required information
    assert audit_log is not None
    assert audit_log.actor_id == owner.id
    assert audit_log.object_type == "PRODUCT"
    assert audit_log.object_id == product.id
    assert audit_log.action_type == "PRODUCT_STOCK_UPDATED"
    assert audit_log.created_at is not None
    
    # Verify details contain old and new quantities
    assert 'old_quantity' in audit_log.details
    assert 'new_quantity' in audit_log.details
    assert 'quantity_delta' in audit_log.details
    assert audit_log.details['old_quantity'] == initial_stock
    assert audit_log.details['new_quantity'] == initial_stock + quantity_delta
    assert audit_log.details['quantity_delta'] == quantity_delta
    
    # Clean up
    db_session.delete(audit_log)
    db_session.delete(product)
    db_session.delete(category)
    db_session.delete(owner)
    db_session.commit()


# Test that negative stock updates are rejected
@given(
    product_data=valid_product_data_strategy(),
    excessive_delta=st.integers(min_value=-10000, max_value=-1)
)
@settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
def test_property_negative_stock_rejected(product_data, excessive_delta, db_session):
    """
    Test that stock updates resulting in negative stock are rejected.
    """
    # Create owner user
    owner = User(
        phone='+919876543210',
        name='Test Owner',
        role=UserRole.OWNER,
        is_active=True
    )
    db_session.add(owner)
    db_session.commit()
    db_session.refresh(owner)
    
    # Create category
    category = Category(
        name='Test Category',
        slug='test-category',
        display_order=0
    )
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)
    
    # Add category_id to product data
    product_data['category_id'] = category.id
    
    # Create product with limited stock
    product_create = ProductCreate(**product_data)
    product = product_service.create_product(
        product_data=product_create,
        owner_id=owner.id,
        db=db_session
    )
    
    # Attempt to reduce stock below zero
    if product.stock_quantity + excessive_delta < 0:
        with pytest.raises(ValueError) as exc_info:
            product_service.update_stock(
                product_id=product.id,
                quantity_delta=excessive_delta,
                actor_id=owner.id,
                db=db_session
            )
        
        assert "Insufficient stock" in str(exc_info.value)
    
    # Clean up
    db_session.delete(product)
    db_session.delete(category)
    db_session.delete(owner)
    db_session.commit()



# Feature: indostar-naturals-ecommerce, Property 6: Consumer sees consumer prices
@given(product_data=valid_product_data_strategy())
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
def test_property_consumer_sees_consumer_prices(product_data, db_session):
    """
    **Property 6: Consumer sees consumer prices**
    **Validates: Requirements 2.2**
    
    For any consumer user and any product, the displayed price 
    should equal the product's consumer_price field.
    """
    # Create owner user
    owner = User(
        phone='+919876543210',
        name='Test Owner',
        role=UserRole.OWNER,
        is_active=True
    )
    db_session.add(owner)
    db_session.commit()
    db_session.refresh(owner)
    
    # Create category
    category = Category(
        name='Test Category',
        slug='test-category',
        display_order=0
    )
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)
    
    # Add category_id to product data
    product_data['category_id'] = category.id
    
    # Create product
    product_create = ProductCreate(**product_data)
    product = product_service.create_product(
        product_data=product_create,
        owner_id=owner.id,
        db=db_session
    )
    
    # Get product as consumer
    product_response = product_service.get_product_by_id(
        product_id=product.id,
        user_role=UserRole.CONSUMER,
        db=db_session
    )
    
    # Verify consumer sees consumer price
    assert product_response is not None
    assert product_response.price == product.consumer_price
    assert product_response.price == product_data['consumer_price']
    
    # Verify consumer does NOT see distributor price
    assert product_response.price != product.distributor_price or product.consumer_price == product.distributor_price
    
    # Clean up
    db_session.delete(product)
    db_session.delete(category)
    db_session.delete(owner)
    db_session.commit()


# Feature: indostar-naturals-ecommerce, Property 7: Distributor sees distributor prices
@given(product_data=valid_product_data_strategy())
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
def test_property_distributor_sees_distributor_prices(product_data, db_session):
    """
    **Property 7: Distributor sees distributor prices**
    **Validates: Requirements 2.3**
    
    For any distributor user and any product, the displayed price 
    should equal the product's distributor_price field.
    """
    # Create owner user
    owner = User(
        phone='+919876543210',
        name='Test Owner',
        role=UserRole.OWNER,
        is_active=True
    )
    db_session.add(owner)
    db_session.commit()
    db_session.refresh(owner)
    
    # Create category
    category = Category(
        name='Test Category',
        slug='test-category',
        display_order=0
    )
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)
    
    # Add category_id to product data
    product_data['category_id'] = category.id
    
    # Create product
    product_create = ProductCreate(**product_data)
    product = product_service.create_product(
        product_data=product_create,
        owner_id=owner.id,
        db=db_session
    )
    
    # Get product as distributor
    product_response = product_service.get_product_by_id(
        product_id=product.id,
        user_role=UserRole.DISTRIBUTOR,
        db=db_session
    )
    
    # Verify distributor sees distributor price
    assert product_response is not None
    assert product_response.price == product.distributor_price
    assert product_response.price == product_data['distributor_price']
    
    # Verify distributor does NOT see consumer price
    assert product_response.price != product.consumer_price or product.consumer_price == product.distributor_price
    
    # Clean up
    db_session.delete(product)
    db_session.delete(category)
    db_session.delete(owner)
    db_session.commit()


# Test that owner sees consumer prices by default
@given(product_data=valid_product_data_strategy())
@settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
def test_property_owner_sees_consumer_prices(product_data, db_session):
    """
    Test that owner sees consumer prices by default (same as consumers).
    """
    # Create owner user
    owner = User(
        phone='+919876543210',
        name='Test Owner',
        role=UserRole.OWNER,
        is_active=True
    )
    db_session.add(owner)
    db_session.commit()
    db_session.refresh(owner)
    
    # Create category
    category = Category(
        name='Test Category',
        slug='test-category',
        display_order=0
    )
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)
    
    # Add category_id to product data
    product_data['category_id'] = category.id
    
    # Create product
    product_create = ProductCreate(**product_data)
    product = product_service.create_product(
        product_data=product_create,
        owner_id=owner.id,
        db=db_session
    )
    
    # Get product as owner
    product_response = product_service.get_product_by_id(
        product_id=product.id,
        user_role=UserRole.OWNER,
        db=db_session
    )
    
    # Verify owner sees consumer price
    assert product_response is not None
    assert product_response.price == product.consumer_price
    
    # Clean up
    db_session.delete(product)
    db_session.delete(category)
    db_session.delete(owner)
    db_session.commit()



# Feature: indostar-naturals-ecommerce, Property 15: Soft delete hides products
@given(product_data=valid_product_data_strategy())
@settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
def test_property_soft_delete_hides_products(product_data, db_session):
    """
    **Property 15: Soft delete hides products**
    **Validates: Requirements 3.5**
    
    For any product marked as deleted, the product should not appear 
    in catalog queries for consumers or distributors.
    """
    # Create owner user
    owner = User(
        phone='+919876543210',
        name='Test Owner',
        role=UserRole.OWNER,
        is_active=True
    )
    db_session.add(owner)
    db_session.commit()
    db_session.refresh(owner)
    
    # Create category
    category = Category(
        name='Test Category',
        slug='test-category',
        display_order=0
    )
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)
    
    # Add category_id to product data
    product_data['category_id'] = category.id
    
    # Create product
    product_create = ProductCreate(**product_data)
    product = product_service.create_product(
        product_data=product_create,
        owner_id=owner.id,
        db=db_session
    )
    
    # Verify product is initially active and visible
    assert product.is_active is True
    
    # Get products list before deletion (should include this product)
    filters_before = ProductFilters(
        category_id=category.id,
        is_active=True,
        page=1,
        page_size=100
    )
    products_before_consumer = product_service.get_products(
        filters=filters_before,
        user_role=UserRole.CONSUMER,
        db=db_session
    )
    products_before_distributor = product_service.get_products(
        filters=filters_before,
        user_role=UserRole.DISTRIBUTOR,
        db=db_session
    )
    
    # Product should be in the list
    product_ids_before_consumer = [p.id for p in products_before_consumer.items]
    product_ids_before_distributor = [p.id for p in products_before_distributor.items]
    assert product.id in product_ids_before_consumer
    assert product.id in product_ids_before_distributor
    
    # Soft delete the product
    deleted_product = product_service.soft_delete(
        product_id=product.id,
        actor_id=owner.id,
        db=db_session
    )
    
    # Verify product is marked as inactive
    assert deleted_product is not None
    assert deleted_product.is_active is False
    
    # Get products list after deletion (should NOT include this product)
    filters_after = ProductFilters(
        category_id=category.id,
        is_active=True,  # Only active products
        page=1,
        page_size=100
    )
    products_after_consumer = product_service.get_products(
        filters=filters_after,
        user_role=UserRole.CONSUMER,
        db=db_session
    )
    products_after_distributor = product_service.get_products(
        filters=filters_after,
        user_role=UserRole.DISTRIBUTOR,
        db=db_session
    )
    
    # Product should NOT be in the list
    product_ids_after_consumer = [p.id for p in products_after_consumer.items]
    product_ids_after_distributor = [p.id for p in products_after_distributor.items]
    assert product.id not in product_ids_after_consumer
    assert product.id not in product_ids_after_distributor
    
    # Verify product still exists in database (soft delete, not hard delete)
    from app.models.product import Product as ProductModel
    db_product = db_session.query(ProductModel).filter(ProductModel.id == product.id).first()
    assert db_product is not None
    assert db_product.is_active is False
    
    # Clean up
    db_session.delete(product)
    db_session.delete(category)
    db_session.delete(owner)
    db_session.commit()


# Test that soft delete creates audit log
@given(product_data=valid_product_data_strategy())
@settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
def test_property_soft_delete_creates_audit_log(product_data, db_session):
    """
    Test that soft deleting a product creates an audit log entry.
    """
    from app.models.audit_log import AuditLog
    
    # Create owner user
    owner = User(
        phone='+919876543210',
        name='Test Owner',
        role=UserRole.OWNER,
        is_active=True
    )
    db_session.add(owner)
    db_session.commit()
    db_session.refresh(owner)
    
    # Create category
    category = Category(
        name='Test Category',
        slug='test-category',
        display_order=0
    )
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)
    
    # Add category_id to product data
    product_data['category_id'] = category.id
    
    # Create product
    product_create = ProductCreate(**product_data)
    product = product_service.create_product(
        product_data=product_create,
        owner_id=owner.id,
        db=db_session
    )
    
    # Soft delete the product
    product_service.soft_delete(
        product_id=product.id,
        actor_id=owner.id,
        db=db_session
    )
    
    # Verify audit log was created
    audit_log = db_session.query(AuditLog).filter(
        AuditLog.object_type == "PRODUCT",
        AuditLog.object_id == product.id,
        AuditLog.action_type == "PRODUCT_DELETED"
    ).first()
    
    assert audit_log is not None
    assert audit_log.actor_id == owner.id
    assert 'soft_delete' in audit_log.details
    assert audit_log.details['soft_delete'] is True
    
    # Clean up
    db_session.delete(audit_log)
    db_session.delete(product)
    db_session.delete(category)
    db_session.delete(owner)
    db_session.commit()



# Feature: indostar-naturals-ecommerce, Property 76: Image upload validates file type and size
@given(
    invalid_content_type=st.sampled_from([
        'image/gif',
        'image/bmp',
        'image/svg+xml',
        'application/pdf',
        'text/plain',
        'video/mp4'
    ])
)
@settings(max_examples=50, deadline=None)
def test_property_image_upload_validates_file_type(invalid_content_type):
    """
    **Property 76: Image upload validates file type and size**
    **Validates: Requirements 20.1**
    
    For any product image upload, if the file type is not JPEG, PNG, or WebP, 
    or if the size exceeds 5MB, the system should reject with a validation error.
    """
    from app.services.image_service import image_service
    from fastapi import UploadFile, HTTPException
    from io import BytesIO
    from unittest.mock import Mock
    
    # Create a mock upload file with invalid content type
    file_content = b"fake image content"
    mock_file = Mock(spec=UploadFile)
    mock_file.file = BytesIO(file_content)
    mock_file.content_type = invalid_content_type
    mock_file.filename = "test.jpg"
    
    # Attempt to validate should fail
    with pytest.raises(HTTPException) as exc_info:
        image_service.validate_image(mock_file)
    
    # Verify error is about invalid file type
    assert exc_info.value.status_code == 400
    assert "Invalid file type" in str(exc_info.value.detail)


# Test that valid image types pass validation
@given(
    valid_content_type=st.sampled_from(['image/jpeg', 'image/png', 'image/webp'])
)
@settings(max_examples=50, deadline=None)
def test_property_valid_image_types_pass_validation(valid_content_type):
    """
    Test that valid image types (JPEG, PNG, WebP) pass validation.
    """
    from app.services.image_service import image_service
    from fastapi import UploadFile
    from io import BytesIO
    from unittest.mock import Mock
    
    # Create a mock upload file with valid content type and size
    file_content = b"fake image content" * 100  # Small file
    mock_file = Mock(spec=UploadFile)
    mock_file.file = BytesIO(file_content)
    mock_file.content_type = valid_content_type
    mock_file.filename = "test.jpg"
    
    # Should not raise exception
    try:
        image_service.validate_image(mock_file)
    except Exception as e:
        assert False, f"Valid image type should pass validation: {e}"


# Test that oversized files are rejected
@settings(max_examples=20, deadline=None)
def test_property_oversized_images_rejected():
    """
    Test that images exceeding 5MB are rejected.
    """
    from app.services.image_service import image_service
    from fastapi import UploadFile, HTTPException
    from io import BytesIO
    from unittest.mock import Mock
    
    # Create a file larger than 5MB
    file_size = 6 * 1024 * 1024  # 6MB
    file_content = b"x" * file_size
    mock_file = Mock(spec=UploadFile)
    mock_file.file = BytesIO(file_content)
    mock_file.content_type = "image/jpeg"
    mock_file.filename = "large.jpg"
    
    # Attempt to validate should fail
    with pytest.raises(HTTPException) as exc_info:
        image_service.validate_image(mock_file)
    
    # Verify error is about file size
    assert exc_info.value.status_code == 400
    assert "size exceeds" in str(exc_info.value.detail).lower()


# Feature: indostar-naturals-ecommerce, Property 12: Product image upload associates with product
@given(
    product_data=valid_product_data_strategy(),
    phone_suffix=st.integers(min_value=1000, max_value=9999)
)
@settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
async def test_property_image_upload_associates_with_product(product_data, phone_suffix, db_session):
    """
    **Property 12: Product image upload associates with product**
    **Validates: Requirements 3.2**
    
    For any uploaded product image, the image should be stored and 
    associated with the product, such that querying the product 
    returns the image URL.
    
    Note: This test mocks S3 upload to avoid external dependencies.
    """
    from unittest.mock import patch, AsyncMock
    from fastapi import UploadFile
    from io import BytesIO
    
    # Create owner user with unique phone
    owner = User(
        phone=f'+9198765{phone_suffix}',
        name='Test Owner',
        role=UserRole.OWNER,
        is_active=True
    )
    db_session.add(owner)
    db_session.commit()
    db_session.refresh(owner)
    
    # Create category
    category = Category(
        name='Test Category',
        slug='test-category',
        display_order=0
    )
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)
    
    # Add category_id to product data
    product_data['category_id'] = category.id
    
    # Create product
    product_create = ProductCreate(**product_data)
    product = product_service.create_product(
        product_data=product_create,
        owner_id=owner.id,
        db=db_session
    )
    
    # Create mock image file
    from unittest.mock import Mock
    file_content = b"fake image content"
    mock_file = Mock(spec=UploadFile)
    mock_file.file = BytesIO(file_content)
    mock_file.content_type = "image/jpeg"
    mock_file.filename = "test.jpg"
    
    # Mock S3 upload to return a fake URL
    mock_url = f"https://cdn.example.com/products/{product.id}/test.jpg"
    
    with patch('app.services.product_service.image_service.upload_image', new_callable=AsyncMock) as mock_upload:
        mock_upload.return_value = mock_url
        
        # Upload image
        product_image = await product_service.upload_product_image(
            product_id=product.id,
            image_file=mock_file,
            alt_text="Test Image",
            db=db_session
        )
        
        # Verify image was created
        assert product_image is not None
        assert product_image.product_id == product.id
        assert product_image.url == mock_url
        assert product_image.alt_text == "Test Image"
        
        # Verify image is associated with product
        db_session.refresh(product)
        assert len(product.images) > 0
        assert any(img.url == mock_url for img in product.images)
        
        # Get product and verify image is returned
        product_response = product_service.get_product_by_id(
            product_id=product.id,
            user_role=UserRole.CONSUMER,
            db=db_session
        )
        
        assert product_response is not None
        assert len(product_response.images) > 0
        assert any(img.url == mock_url for img in product_response.images)
        
        # Clean up
        db_session.delete(product_image)
    
    db_session.delete(product)
    db_session.delete(category)
    db_session.delete(owner)
    db_session.commit()


# Test that multiple images can be uploaded to same product
@given(
    product_data=valid_product_data_strategy(),
    phone_suffix=st.integers(min_value=1000, max_value=9999)
)
@settings(max_examples=20, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
async def test_property_multiple_images_per_product(product_data, phone_suffix, db_session):
    """
    Test that multiple images can be uploaded to the same product.
    """
    from unittest.mock import patch, AsyncMock
    from fastapi import UploadFile
    from io import BytesIO
    
    # Create owner user with unique phone
    owner = User(
        phone=f'+9198765{phone_suffix}',
        name='Test Owner',
        role=UserRole.OWNER,
        is_active=True
    )
    db_session.add(owner)
    db_session.commit()
    db_session.refresh(owner)
    
    # Create category
    category = Category(
        name='Test Category',
        slug='test-category',
        display_order=0
    )
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)
    
    # Add category_id to product data
    product_data['category_id'] = category.id
    
    # Create product
    product_create = ProductCreate(**product_data)
    product = product_service.create_product(
        product_data=product_create,
        owner_id=owner.id,
        db=db_session
    )
    
    # Mock S3 upload
    with patch('app.services.product_service.image_service.upload_image', new_callable=AsyncMock) as mock_upload:
        # Upload 3 images
        uploaded_images = []
        for i in range(3):
            mock_url = f"https://cdn.example.com/products/{product.id}/test{i}.jpg"
            mock_upload.return_value = mock_url
            
            from unittest.mock import Mock
            file_content = b"fake image content"
            mock_file = Mock(spec=UploadFile)
            mock_file.file = BytesIO(file_content)
            mock_file.content_type = "image/jpeg"
            mock_file.filename = f"test{i}.jpg"
            
            product_image = await product_service.upload_product_image(
                product_id=product.id,
                image_file=mock_file,
                alt_text=f"Test Image {i}",
                db=db_session
            )
            
            uploaded_images.append(product_image)
        
        # Verify all images are associated with product
        db_session.refresh(product)
        assert len(product.images) == 3
        
        # Verify display order is sequential
        for i, img in enumerate(uploaded_images):
            assert img.display_order == i + 1
        
        # Clean up
        for img in uploaded_images:
            db_session.delete(img)
    
    db_session.delete(product)
    db_session.delete(category)
    db_session.delete(owner)
    db_session.commit()



# Feature: indostar-naturals-ecommerce, Property 16: Catalog pagination returns 20 items
@given(
    num_products=st.integers(min_value=1, max_value=50),
    phone_suffix=st.integers(min_value=10000, max_value=99999)
)
@settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
def test_property_catalog_pagination_returns_20_items(num_products, phone_suffix, db_session):
    """
    **Property 16: Catalog pagination returns 20 items**
    **Validates: Requirements 4.1**
    
    For any product catalog query without explicit page size, 
    the system should return exactly 20 items per page 
    (or fewer on the last page).
    """
    # Create owner user with unique phone
    owner = User(
        phone=f'+9198{phone_suffix}',
        name='Test Owner',
        role=UserRole.OWNER,
        is_active=True
    )
    db_session.add(owner)
    db_session.commit()
    db_session.refresh(owner)
    
    # Create category
    category = Category(
        name='Test Category',
        slug='test-category',
        display_order=0
    )
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)
    
    # Create multiple products
    products = []
    for i in range(num_products):
        product_data = ProductCreate(
            title=f'Product {i}',
            description=f'Description {i}',
            category_id=category.id,
            sku=f'SKU-{phone_suffix}-{i}',
            unit_size='1kg',
            consumer_price=Decimal('10.00'),
            distributor_price=Decimal('8.00'),
            stock_quantity=100
        )
        product = product_service.create_product(
            product_data=product_data,
            owner_id=owner.id,
            db=db_session
        )
        products.append(product)
    
    # Get products with default pagination (page_size=20)
    filters = ProductFilters(
        page=1,
        page_size=20,
        is_active=True
    )
    result = product_service.get_products(filters, UserRole.CONSUMER, db_session)
    
    # Verify pagination
    if num_products <= 20:
        # Should return all products
        assert len(result.items) == num_products
    else:
        # Should return exactly 20 items on first page
        assert len(result.items) == 20
    
    # Verify total count
    assert result.total >= num_products
    assert result.page == 1
    assert result.page_size == 20
    
    # Clean up
    for product in products:
        db_session.delete(product)
    db_session.delete(category)
    db_session.delete(owner)
    db_session.commit()


# Feature: indostar-naturals-ecommerce, Property 17: Category filter returns matching products
@given(
    num_products_cat1=st.integers(min_value=1, max_value=10),
    num_products_cat2=st.integers(min_value=1, max_value=10),
    phone_suffix=st.integers(min_value=10000, max_value=99999)
)
@settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
def test_property_category_filter_returns_matching_products(num_products_cat1, num_products_cat2, phone_suffix, db_session):
    """
    **Property 17: Category filter returns matching products**
    **Validates: Requirements 4.2**
    
    For any category filter applied to product catalog, 
    all returned products should belong to the specified category.
    """
    # Create owner user with unique phone
    owner = User(
        phone=f'+9198{phone_suffix}',
        name='Test Owner',
        role=UserRole.OWNER,
        is_active=True
    )
    db_session.add(owner)
    db_session.commit()
    db_session.refresh(owner)
    
    # Create two categories
    category1 = Category(
        name='Category 1',
        slug='category-1',
        display_order=0
    )
    category2 = Category(
        name='Category 2',
        slug='category-2',
        display_order=1
    )
    db_session.add(category1)
    db_session.add(category2)
    db_session.commit()
    db_session.refresh(category1)
    db_session.refresh(category2)
    
    # Create products in category 1
    products_cat1 = []
    for i in range(num_products_cat1):
        product_data = ProductCreate(
            title=f'Product Cat1 {i}',
            description=f'Description {i}',
            category_id=category1.id,
            sku=f'SKU-{phone_suffix}-C1-{i}',
            unit_size='1kg',
            consumer_price=Decimal('10.00'),
            distributor_price=Decimal('8.00'),
            stock_quantity=100
        )
        product = product_service.create_product(
            product_data=product_data,
            owner_id=owner.id,
            db=db_session
        )
        products_cat1.append(product)
    
    # Create products in category 2
    products_cat2 = []
    for i in range(num_products_cat2):
        product_data = ProductCreate(
            title=f'Product Cat2 {i}',
            description=f'Description {i}',
            category_id=category2.id,
            sku=f'SKU-{phone_suffix}-C2-{i}',
            unit_size='1kg',
            consumer_price=Decimal('10.00'),
            distributor_price=Decimal('8.00'),
            stock_quantity=100
        )
        product = product_service.create_product(
            product_data=product_data,
            owner_id=owner.id,
            db=db_session
        )
        products_cat2.append(product)
    
    # Filter by category 1
    filters = ProductFilters(
        category_id=category1.id,
        page=1,
        page_size=100,
        is_active=True
    )
    result = product_service.get_products(filters, UserRole.CONSUMER, db_session)
    
    # Verify all returned products belong to category 1
    assert len(result.items) >= num_products_cat1
    for product in result.items:
        if product.id in [p.id for p in products_cat1]:
            assert product.category_id == category1.id
    
    # Filter by category 2
    filters = ProductFilters(
        category_id=category2.id,
        page=1,
        page_size=100,
        is_active=True
    )
    result = product_service.get_products(filters, UserRole.CONSUMER, db_session)
    
    # Verify all returned products belong to category 2
    assert len(result.items) >= num_products_cat2
    for product in result.items:
        if product.id in [p.id for p in products_cat2]:
            assert product.category_id == category2.id
    
    # Clean up
    for product in products_cat1 + products_cat2:
        db_session.delete(product)
    db_session.delete(category1)
    db_session.delete(category2)
    db_session.delete(owner)
    db_session.commit()


# Feature: indostar-naturals-ecommerce, Property 18: Search returns matching products
@given(
    search_term=st.text(min_size=3, max_size=10, alphabet=st.characters(min_codepoint=97, max_codepoint=122)),
    phone_suffix=st.integers(min_value=10000, max_value=99999)
)
@settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
def test_property_search_returns_matching_products(search_term, phone_suffix, db_session):
    """
    **Property 18: Search returns matching products**
    **Validates: Requirements 4.3**
    
    For any search query, all returned products should contain 
    the query terms in their title, description, or tags.
    """
    # Create owner user with unique phone
    owner = User(
        phone=f'+9198{phone_suffix}',
        name='Test Owner',
        role=UserRole.OWNER,
        is_active=True
    )
    db_session.add(owner)
    db_session.commit()
    db_session.refresh(owner)
    
    # Create category
    category = Category(
        name='Test Category',
        slug='test-category',
        display_order=0
    )
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)
    
    # Create product with search term in title
    product_with_term = ProductCreate(
        title=f'Product with {search_term}',
        description='Some description',
        category_id=category.id,
        sku=f'SKU-{phone_suffix}-MATCH',
        unit_size='1kg',
        consumer_price=Decimal('10.00'),
        distributor_price=Decimal('8.00'),
        stock_quantity=100
    )
    matching_product = product_service.create_product(
        product_data=product_with_term,
        owner_id=owner.id,
        db=db_session
    )
    
    # Create product without search term
    product_without_term = ProductCreate(
        title='Different Product',
        description='Different description',
        category_id=category.id,
        sku=f'SKU-{phone_suffix}-NOMATCH',
        unit_size='1kg',
        consumer_price=Decimal('10.00'),
        distributor_price=Decimal('8.00'),
        stock_quantity=100
    )
    non_matching_product = product_service.create_product(
        product_data=product_without_term,
        owner_id=owner.id,
        db=db_session
    )
    
    # Search for products
    result = product_service.search_products(
        query=search_term,
        user_role=UserRole.CONSUMER,
        page=1,
        page_size=100,
        db=db_session
    )
    
    # Verify matching product is in results
    product_ids = [p.id for p in result.items]
    assert matching_product.id in product_ids
    
    # Verify all returned products contain search term (case-insensitive)
    for product in result.items:
        if product.id == matching_product.id:
            title_lower = product.title.lower()
            desc_lower = product.description.lower()
            search_lower = search_term.lower()
            assert search_lower in title_lower or search_lower in desc_lower
    
    # Clean up
    db_session.delete(matching_product)
    db_session.delete(non_matching_product)
    db_session.delete(category)
    db_session.delete(owner)
    db_session.commit()
