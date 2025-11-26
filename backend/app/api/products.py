"""Product API Endpoints

Public endpoints for browsing products, categories, and search.
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.product_service import product_service
from app.services.dependencies import get_optional_user
from app.schemas.product import ProductResponse, ProductListResponse, ProductFilters
from app.models.user import User
from app.models.enums import UserRole
from app.models.category import Category

router = APIRouter(prefix="/api/v1", tags=["products"])


@router.get("/products", response_model=ProductListResponse)
def list_products(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price"),
    is_subscription_available: Optional[bool] = Query(None, description="Filter by subscription availability"),
    search_query: Optional[str] = Query(None, description="Search query"),
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """
    List products with pagination, filtering, and role-based pricing.
    
    - **page**: Page number (default: 1)
    - **page_size**: Items per page (default: 20, max: 100)
    - **category_id**: Filter by category
    - **min_price**: Minimum price filter
    - **max_price**: Maximum price filter
    - **is_subscription_available**: Filter subscription products
    - **search_query**: Search in title and description
    
    Returns products with pricing based on user role (consumer/distributor).
    """
    # Determine user role for pricing
    user_role = current_user.role if current_user else UserRole.CONSUMER
    
    # Create filters
    filters = ProductFilters(
        page=page,
        page_size=page_size,
        category_id=category_id,
        min_price=min_price,
        max_price=max_price,
        is_subscription_available=is_subscription_available,
        search_query=search_query,
        is_active=True
    )
    
    # Get products
    return product_service.get_products(filters, user_role, db)


@router.get("/products/{product_id}", response_model=ProductResponse)
def get_product(
    product_id: int,
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """
    Get product details by ID with role-based pricing.
    
    Returns product with pricing based on user role (consumer/distributor).
    """
    # Determine user role for pricing
    user_role = current_user.role if current_user else UserRole.CONSUMER
    
    # Get product
    product = product_service.get_product_by_id(product_id, user_role, db)
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Check if product is active
    if not product.is_active:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return product


@router.get("/categories", response_model=list)
def list_categories(
    db: Session = Depends(get_db)
):
    """
    List all categories.
    
    Returns all categories ordered by display_order.
    """
    categories = db.query(Category).order_by(Category.display_order).all()
    
    return [
        {
            "id": cat.id,
            "name": cat.name,
            "slug": cat.slug,
            "parent_id": cat.parent_id,
            "display_order": cat.display_order
        }
        for cat in categories
    ]


@router.get("/products/search", response_model=ProductListResponse)
def search_products(
    q: str = Query(..., min_length=1, description="Search query"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """
    Search products by title and description.
    
    - **q**: Search query (required)
    - **page**: Page number (default: 1)
    - **page_size**: Items per page (default: 20, max: 100)
    
    Returns products matching the search query with role-based pricing.
    """
    # Determine user role for pricing
    user_role = current_user.role if current_user else UserRole.CONSUMER
    
    # Search products
    return product_service.search_products(q, user_role, page, page_size, db)
