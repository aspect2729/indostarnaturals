"""Cart Service

Handles shopping cart operations including item management, pricing, and validation.
"""
from typing import Optional, List
from decimal import Decimal
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_
from app.models.cart import Cart
from app.models.cart_item import CartItem
from app.models.product import Product
from app.models.user import User
from app.models.enums import UserRole
from app.schemas.cart import (
    CartItemCreate,
    CartItemUpdate,
    CartResponse,
    CartItemResponse,
    CartValidation
)


class CartService:
    """Service for shopping cart operations"""
    
    @staticmethod
    def get_cart(
        user_id: int,
        db: Session
    ) -> CartResponse:
        """
        Get user's cart with role-based pricing.
        
        Args:
            user_id: User ID
            db: Database session
            
        Returns:
            CartResponse with cart details and role-appropriate pricing
        """
        # Get user to determine role
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError(f"User with ID {user_id} does not exist")
        
        # Get or create cart
        cart = db.query(Cart).options(
            joinedload(Cart.items).joinedload(CartItem.product)
        ).filter(Cart.user_id == user_id).first()
        
        if not cart:
            # Create new cart for user
            cart = Cart(user_id=user_id)
            db.add(cart)
            db.commit()
            db.refresh(cart)
        
        # Build cart response with role-based pricing
        return CartService._build_cart_response(cart, user.role, db)
    
    @staticmethod
    def add_item(
        user_id: int,
        item_data: CartItemCreate,
        db: Session
    ) -> CartResponse:
        """
        Add item to cart with stock validation.
        
        Args:
            user_id: User ID
            item_data: Item to add
            db: Database session
            
        Returns:
            Updated CartResponse
            
        Raises:
            ValueError: If product doesn't exist, is inactive, or insufficient stock
        """
        # Get user to determine role
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError(f"User with ID {user_id} does not exist")
        
        # Verify product exists and is active
        product = db.query(Product).filter(Product.id == item_data.product_id).first()
        if not product:
            raise ValueError(f"Product with ID {item_data.product_id} does not exist")
        
        if not product.is_active:
            raise ValueError(f"Product '{product.title}' is not available")
        
        # Check stock availability
        if product.stock_quantity < item_data.quantity:
            raise ValueError(
                f"Insufficient stock for '{product.title}'. "
                f"Available: {product.stock_quantity}, Requested: {item_data.quantity}"
            )
        
        # Get or create cart
        cart = db.query(Cart).filter(Cart.user_id == user_id).first()
        if not cart:
            cart = Cart(user_id=user_id)
            db.add(cart)
            db.flush()
        
        # Check if item already exists in cart
        existing_item = db.query(CartItem).filter(
            and_(
                CartItem.cart_id == cart.id,
                CartItem.product_id == item_data.product_id
            )
        ).first()
        
        # Determine price based on user role
        unit_price = (
            product.distributor_price 
            if user.role == UserRole.DISTRIBUTOR 
            else product.consumer_price
        )
        
        if existing_item:
            # Update quantity of existing item
            new_quantity = existing_item.quantity + item_data.quantity
            
            # Check stock for new total quantity
            if product.stock_quantity < new_quantity:
                raise ValueError(
                    f"Insufficient stock for '{product.title}'. "
                    f"Available: {product.stock_quantity}, Requested: {new_quantity}"
                )
            
            existing_item.quantity = new_quantity
            existing_item.unit_price = unit_price  # Update price in case it changed
        else:
            # Create new cart item
            cart_item = CartItem(
                cart_id=cart.id,
                product_id=item_data.product_id,
                quantity=item_data.quantity,
                unit_price=unit_price
            )
            db.add(cart_item)
        
        db.commit()
        db.refresh(cart)
        
        # Return updated cart
        return CartService.get_cart(user_id, db)
    
    @staticmethod
    def update_item_quantity(
        user_id: int,
        item_id: int,
        quantity_data: CartItemUpdate,
        db: Session
    ) -> CartResponse:
        """
        Update cart item quantity with total recalculation.
        
        Args:
            user_id: User ID
            item_id: Cart item ID
            quantity_data: New quantity
            db: Database session
            
        Returns:
            Updated CartResponse
            
        Raises:
            ValueError: If item doesn't exist or insufficient stock
        """
        # Get cart
        cart = db.query(Cart).filter(Cart.user_id == user_id).first()
        if not cart:
            raise ValueError("Cart not found")
        
        # Get cart item
        cart_item = db.query(CartItem).options(
            joinedload(CartItem.product)
        ).filter(
            and_(
                CartItem.id == item_id,
                CartItem.cart_id == cart.id
            )
        ).first()
        
        if not cart_item:
            raise ValueError(f"Cart item with ID {item_id} not found in your cart")
        
        # Check stock availability
        product = cart_item.product
        if product.stock_quantity < quantity_data.quantity:
            raise ValueError(
                f"Insufficient stock for '{product.title}'. "
                f"Available: {product.stock_quantity}, Requested: {quantity_data.quantity}"
            )
        
        # Update quantity
        cart_item.quantity = quantity_data.quantity
        
        db.commit()
        db.refresh(cart)
        
        # Return updated cart with recalculated total
        return CartService.get_cart(user_id, db)
    
    @staticmethod
    def remove_item(
        user_id: int,
        item_id: int,
        db: Session
    ) -> CartResponse:
        """
        Remove item from cart with total recalculation.
        
        Args:
            user_id: User ID
            item_id: Cart item ID
            db: Database session
            
        Returns:
            Updated CartResponse
            
        Raises:
            ValueError: If item doesn't exist
        """
        # Get cart
        cart = db.query(Cart).filter(Cart.user_id == user_id).first()
        if not cart:
            raise ValueError("Cart not found")
        
        # Get cart item
        cart_item = db.query(CartItem).filter(
            and_(
                CartItem.id == item_id,
                CartItem.cart_id == cart.id
            )
        ).first()
        
        if not cart_item:
            raise ValueError(f"Cart item with ID {item_id} not found in your cart")
        
        # Remove item
        db.delete(cart_item)
        db.commit()
        db.refresh(cart)
        
        # Return updated cart with recalculated total
        return CartService.get_cart(user_id, db)
    
    @staticmethod
    def apply_coupon(
        user_id: int,
        coupon_code: str,
        db: Session
    ) -> CartResponse:
        """
        Apply coupon code to cart with validation.
        
        Args:
            user_id: User ID
            coupon_code: Coupon code to apply
            db: Database session
            
        Returns:
            Updated CartResponse
            
        Raises:
            ValueError: If coupon is invalid
            
        Note:
            This is a simplified implementation. In production, you would:
            - Check coupon validity (expiration, usage limits, etc.)
            - Calculate discount based on coupon rules
            - Store coupon details in a separate Coupon model
        """
        # Get cart
        cart = db.query(Cart).filter(Cart.user_id == user_id).first()
        if not cart:
            raise ValueError("Cart not found")
        
        # Validate coupon code (simplified - in production, check against Coupon model)
        # For now, we'll accept any non-empty coupon and apply a 10% discount
        if not coupon_code or len(coupon_code.strip()) == 0:
            raise ValueError("Invalid coupon code")
        
        # Calculate discount (10% of subtotal for demo purposes)
        cart_items = db.query(CartItem).filter(CartItem.cart_id == cart.id).all()
        subtotal = sum(item.quantity * item.unit_price for item in cart_items)
        # Round discount to 2 decimal places to ensure consistency
        discount = (subtotal * Decimal('0.10')).quantize(Decimal('0.01'))
        
        # Apply coupon
        cart.coupon_code = coupon_code.strip().upper()
        cart.discount_amount = discount
        
        db.commit()
        db.refresh(cart)
        
        # Return updated cart
        return CartService.get_cart(user_id, db)
    
    @staticmethod
    def remove_coupon(
        user_id: int,
        db: Session
    ) -> CartResponse:
        """
        Remove coupon from cart.
        
        Args:
            user_id: User ID
            db: Database session
            
        Returns:
            Updated CartResponse
        """
        # Get cart
        cart = db.query(Cart).filter(Cart.user_id == user_id).first()
        if not cart:
            raise ValueError("Cart not found")
        
        # Remove coupon
        cart.coupon_code = None
        cart.discount_amount = Decimal('0.00')
        
        db.commit()
        db.refresh(cart)
        
        # Return updated cart
        return CartService.get_cart(user_id, db)
    
    @staticmethod
    def validate_cart(
        user_id: int,
        db: Session
    ) -> CartValidation:
        """
        Validate cart for stock availability check.
        
        Args:
            user_id: User ID
            db: Database session
            
        Returns:
            CartValidation with validation results
        """
        errors = []
        warnings = []
        
        # Get cart
        cart = db.query(Cart).options(
            joinedload(Cart.items).joinedload(CartItem.product)
        ).filter(Cart.user_id == user_id).first()
        
        if not cart:
            errors.append("Cart not found")
            return CartValidation(is_valid=False, errors=errors)
        
        if not cart.items:
            errors.append("Cart is empty")
            return CartValidation(is_valid=False, errors=errors)
        
        # Check each item
        for item in cart.items:
            product = item.product
            
            # Check if product is still active
            if not product.is_active:
                errors.append(
                    f"Product '{product.title}' is no longer available"
                )
            
            # Check stock availability
            if product.stock_quantity < item.quantity:
                errors.append(
                    f"Insufficient stock for '{product.title}'. "
                    f"Available: {product.stock_quantity}, In cart: {item.quantity}"
                )
            elif product.stock_quantity < item.quantity * 2:
                # Warning if stock is low but sufficient
                warnings.append(
                    f"Low stock for '{product.title}'. Only {product.stock_quantity} remaining."
                )
        
        is_valid = len(errors) == 0
        
        return CartValidation(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings
        )
    
    @staticmethod
    def _build_cart_response(
        cart: Cart,
        user_role: UserRole,
        db: Session
    ) -> CartResponse:
        """
        Build cart response with calculated totals.
        
        Args:
            cart: Cart object
            user_role: User's role for pricing
            db: Database session
            
        Returns:
            CartResponse with all calculated fields
        """
        # Get cart items with products
        cart_items = db.query(CartItem).options(
            joinedload(CartItem.product).joinedload(Product.images)
        ).filter(CartItem.cart_id == cart.id).all()
        
        # Build item responses
        item_responses = []
        subtotal = Decimal('0.00')
        
        for item in cart_items:
            product = item.product
            item_subtotal = item.quantity * item.unit_price
            subtotal += item_subtotal
            
            # Get first product image if available
            image_url = None
            if product.images:
                image_url = product.images[0].url
            
            item_response = CartItemResponse(
                id=item.id,
                cart_id=item.cart_id,
                product_id=item.product_id,
                quantity=item.quantity,
                unit_price=item.unit_price,
                product_title=product.title,
                product_sku=product.sku,
                product_image_url=image_url,
                subtotal=item_subtotal
            )
            item_responses.append(item_response)
        
        # Calculate total
        total = subtotal - cart.discount_amount
        
        return CartResponse(
            id=cart.id,
            user_id=cart.user_id,
            items=item_responses,
            coupon_code=cart.coupon_code,
            discount_amount=cart.discount_amount,
            subtotal=subtotal,
            total=total,
            created_at=cart.created_at,
            updated_at=cart.updated_at
        )


# Create singleton instance
cart_service = CartService()

