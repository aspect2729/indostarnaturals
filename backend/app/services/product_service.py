"""Product Service

Handles product management operations including CRUD, search, and inventory management.
"""
from typing import Optional, List, Tuple
from decimal import Decimal
from fastapi import UploadFile
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, func, desc
from app.models.product import Product
from app.models.category import Category
from app.models.product_image import ProductImage
from app.models.audit_log import AuditLog
from app.models.enums import UserRole
from app.schemas.product import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    ProductFilters,
    ProductListResponse
)
from app.services.image_service import image_service


class ProductService:
    """Service for product management operations"""
    
    @staticmethod
    def create_product(
        product_data: ProductCreate,
        owner_id: int,
        db: Session
    ) -> Product:
        """
        Create a new product with validation.
        
        Args:
            product_data: Product creation data
            owner_id: ID of the owner creating the product
            db: Database session
            
        Returns:
            Created Product object
            
        Raises:
            ValueError: If SKU already exists or category doesn't exist
        """
        # Check if SKU already exists
        existing_product = db.query(Product).filter(Product.sku == product_data.sku).first()
        if existing_product:
            raise ValueError(f"Product with SKU '{product_data.sku}' already exists")
        
        # Verify category exists
        category = db.query(Category).filter(Category.id == product_data.category_id).first()
        if not category:
            raise ValueError(f"Category with ID {product_data.category_id} does not exist")
        
        # Create product
        product = Product(
            owner_id=owner_id,
            title=product_data.title,
            description=product_data.description,
            category_id=product_data.category_id,
            sku=product_data.sku,
            unit_size=product_data.unit_size,
            consumer_price=product_data.consumer_price,
            distributor_price=product_data.distributor_price,
            stock_quantity=product_data.stock_quantity,
            is_subscription_available=product_data.is_subscription_available,
            is_active=True
        )
        
        db.add(product)
        db.commit()
        db.refresh(product)
        
        return product
    
    @staticmethod
    def update_product(
        product_id: int,
        product_data: ProductUpdate,
        actor_id: int,
        db: Session
    ) -> Optional[Product]:
        """
        Update an existing product.
        
        Args:
            product_id: ID of product to update
            product_data: Product update data
            actor_id: ID of user performing the update
            db: Database session
            
        Returns:
            Updated Product object if successful, None otherwise
            
        Raises:
            ValueError: If SKU already exists for another product
        """
        # Find product
        product = db.query(Product).filter(Product.id == product_id).first()
        
        if not product:
            return None
        
        # Check if SKU is being updated and already exists
        if product_data.sku and product_data.sku != product.sku:
            existing_product = db.query(Product).filter(
                Product.sku == product_data.sku,
                Product.id != product_id
            ).first()
            if existing_product:
                raise ValueError(f"Product with SKU '{product_data.sku}' already exists")
        
        # Verify category exists if being updated
        if product_data.category_id:
            category = db.query(Category).filter(Category.id == product_data.category_id).first()
            if not category:
                raise ValueError(f"Category with ID {product_data.category_id} does not exist")
        
        # Track price changes for audit logging
        price_changes = {}
        if product_data.consumer_price is not None and product_data.consumer_price != product.consumer_price:
            price_changes['consumer_price'] = {
                'old': float(product.consumer_price),
                'new': float(product_data.consumer_price)
            }
        if product_data.distributor_price is not None and product_data.distributor_price != product.distributor_price:
            price_changes['distributor_price'] = {
                'old': float(product.distributor_price),
                'new': float(product_data.distributor_price)
            }
        
        # Update product fields
        update_data = product_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(product, field, value)
        
        # Create audit log for price changes
        if price_changes:
            audit_log = AuditLog(
                actor_id=actor_id,
                action_type="PRODUCT_PRICE_UPDATED",
                object_type="PRODUCT",
                object_id=product_id,
                details={
                    "product_sku": product.sku,
                    "product_title": product.title,
                    "price_changes": price_changes
                }
            )
            db.add(audit_log)
        
        db.commit()
        db.refresh(product)
        
        return product
    
    @staticmethod
    def get_products(
        filters: ProductFilters,
        user_role: UserRole,
        db: Session
    ) -> ProductListResponse:
        """
        Get products with pagination, filtering, and role-based pricing.
        
        Args:
            filters: Product filters and pagination parameters
            user_role: User's role for pricing
            db: Database session
            
        Returns:
            ProductListResponse with paginated products
        """
        # Base query with eager loading
        query = db.query(Product).options(
            joinedload(Product.images),
            joinedload(Product.category)
        )
        
        # Apply filters
        if filters.is_active is not None:
            query = query.filter(Product.is_active == filters.is_active)
        
        if filters.category_id:
            query = query.filter(Product.category_id == filters.category_id)
        
        if filters.is_subscription_available is not None:
            query = query.filter(Product.is_subscription_available == filters.is_subscription_available)
        
        # Price filtering based on user role
        if filters.min_price is not None:
            if user_role == UserRole.DISTRIBUTOR:
                query = query.filter(Product.distributor_price >= filters.min_price)
            else:
                query = query.filter(Product.consumer_price >= filters.min_price)
        
        if filters.max_price is not None:
            if user_role == UserRole.DISTRIBUTOR:
                query = query.filter(Product.distributor_price <= filters.max_price)
            else:
                query = query.filter(Product.consumer_price <= filters.max_price)
        
        # Search query (full-text search on title and description)
        if filters.search_query:
            search_term = f"%{filters.search_query}%"
            query = query.filter(
                or_(
                    Product.title.ilike(search_term),
                    Product.description.ilike(search_term)
                )
            )
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        offset = (filters.page - 1) * filters.page_size
        products = query.offset(offset).limit(filters.page_size).all()
        
        # Convert to response schema with role-based pricing
        product_responses = []
        for product in products:
            product_dict = ProductResponse.from_orm(product).dict()
            # Set price based on user role
            if user_role == UserRole.DISTRIBUTOR:
                product_dict['price'] = product.distributor_price
            else:
                product_dict['price'] = product.consumer_price
            product_responses.append(ProductResponse(**product_dict))
        
        # Calculate total pages
        total_pages = (total + filters.page_size - 1) // filters.page_size
        
        return ProductListResponse(
            items=product_responses,
            total=total,
            page=filters.page,
            page_size=filters.page_size,
            total_pages=total_pages
        )
    
    @staticmethod
    def get_product_by_id(
        product_id: int,
        user_role: UserRole,
        db: Session
    ) -> Optional[ProductResponse]:
        """
        Get product by ID with role-based pricing.
        
        Args:
            product_id: Product ID
            user_role: User's role for pricing
            db: Database session
            
        Returns:
            ProductResponse if found, None otherwise
        """
        product = db.query(Product).options(
            joinedload(Product.images),
            joinedload(Product.category)
        ).filter(Product.id == product_id).first()
        
        if not product:
            return None
        
        # Convert to response schema with role-based pricing
        product_dict = ProductResponse.from_orm(product).dict()
        # Set price based on user role
        if user_role == UserRole.DISTRIBUTOR:
            product_dict['price'] = product.distributor_price
        else:
            product_dict['price'] = product.consumer_price
        
        return ProductResponse(**product_dict)
    
    @staticmethod
    def update_stock(
        product_id: int,
        quantity_delta: int,
        actor_id: int,
        db: Session
    ) -> Optional[Product]:
        """
        Update product stock quantity with audit logging.
        
        Args:
            product_id: Product ID
            quantity_delta: Change in stock quantity (positive or negative)
            actor_id: ID of user performing the update
            db: Database session
            
        Returns:
            Updated Product object if successful, None otherwise
            
        Raises:
            ValueError: If resulting stock would be negative
        """
        # Find product
        product = db.query(Product).filter(Product.id == product_id).first()
        
        if not product:
            return None
        
        # Calculate new stock quantity
        old_quantity = product.stock_quantity
        new_quantity = old_quantity + quantity_delta
        
        # Validate stock cannot be negative
        if new_quantity < 0:
            raise ValueError(f"Insufficient stock. Current: {old_quantity}, Requested change: {quantity_delta}")
        
        # Update stock
        product.stock_quantity = new_quantity
        
        # Create audit log
        audit_log = AuditLog(
            actor_id=actor_id,
            action_type="PRODUCT_STOCK_UPDATED",
            object_type="PRODUCT",
            object_id=product_id,
            details={
                "product_sku": product.sku,
                "product_title": product.title,
                "old_quantity": old_quantity,
                "new_quantity": new_quantity,
                "quantity_delta": quantity_delta
            }
        )
        
        db.add(audit_log)
        db.commit()
        db.refresh(product)
        
        return product
    
    @staticmethod
    def search_products(
        query: str,
        user_role: UserRole,
        page: int = 1,
        page_size: int = 20,
        db: Session = None
    ) -> ProductListResponse:
        """
        Search products with full-text search.
        
        Args:
            query: Search query string
            user_role: User's role for pricing
            page: Page number (1-indexed)
            page_size: Number of items per page
            db: Database session
            
        Returns:
            ProductListResponse with matching products
        """
        filters = ProductFilters(
            search_query=query,
            page=page,
            page_size=page_size,
            is_active=True
        )
        
        return ProductService.get_products(filters, user_role, db)
    
    @staticmethod
    def soft_delete(
        product_id: int,
        actor_id: int,
        db: Session
    ) -> Optional[Product]:
        """
        Soft delete a product (mark as inactive).
        
        Args:
            product_id: Product ID
            actor_id: ID of user performing the deletion
            db: Database session
            
        Returns:
            Updated Product object if successful, None otherwise
        """
        # Find product
        product = db.query(Product).filter(Product.id == product_id).first()
        
        if not product:
            return None
        
        # Mark as inactive
        product.is_active = False
        
        # Create audit log
        audit_log = AuditLog(
            actor_id=actor_id,
            action_type="PRODUCT_DELETED",
            object_type="PRODUCT",
            object_id=product_id,
            details={
                "product_sku": product.sku,
                "product_title": product.title,
                "soft_delete": True
            }
        )
        
        db.add(audit_log)
        db.commit()
        db.refresh(product)
        
        return product
    
    @staticmethod
    def get_product_by_sku(
        sku: str,
        db: Session
    ) -> Optional[Product]:
        """
        Get product by SKU.
        
        Args:
            sku: Product SKU
            db: Database session
            
        Returns:
            Product object if found, None otherwise
        """
        return db.query(Product).filter(Product.sku == sku).first()
    
    @staticmethod
    async def upload_product_image(
        product_id: int,
        image_file: UploadFile,
        alt_text: Optional[str],
        db: Session
    ) -> Optional[ProductImage]:
        """
        Upload product image to S3 and associate with product.
        
        Args:
            product_id: Product ID
            image_file: Image file to upload
            alt_text: Alt text for image
            db: Database session
            
        Returns:
            ProductImage object if successful, None otherwise
            
        Raises:
            ValueError: If product doesn't exist
            HTTPException: If image validation or upload fails
        """
        # Verify product exists
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise ValueError(f"Product with ID {product_id} does not exist")
        
        # Upload image to S3
        image_url = await image_service.upload_image(image_file, folder="products")
        
        # Get current max display order
        max_order = db.query(func.max(ProductImage.display_order)).filter(
            ProductImage.product_id == product_id
        ).scalar() or 0
        
        # Create product image record
        product_image = ProductImage(
            product_id=product_id,
            url=image_url,
            alt_text=alt_text or product.title,
            display_order=max_order + 1
        )
        
        db.add(product_image)
        db.commit()
        db.refresh(product_image)
        
        return product_image
    
    @staticmethod
    def delete_product_image(
        product_id: int,
        image_id: int,
        db: Session
    ) -> bool:
        """
        Delete product image from S3 and database.
        
        Args:
            product_id: Product ID
            image_id: Image ID
            db: Database session
            
        Returns:
            True if deletion successful, False otherwise
        """
        # Find image
        image = db.query(ProductImage).filter(
            ProductImage.id == image_id,
            ProductImage.product_id == product_id
        ).first()
        
        if not image:
            return False
        
        # Delete from S3
        image_service.delete_image(image.url)
        
        # Delete from database
        db.delete(image)
        db.commit()
        
        return True


# Create singleton instance
product_service = ProductService()
