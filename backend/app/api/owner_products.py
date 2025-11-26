"""Owner Product Management API Endpoints

Owner-only endpoints for managing products, images, and inventory.
"""
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Form
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.services.product_service import product_service
from app.services.dependencies import require_owner
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse, StockUpdate
from app.models.user import User

router = APIRouter(prefix="/api/v1/owner", tags=["owner-products"])


@router.post("/products", response_model=ProductResponse, status_code=201)
def create_product(
    product_data: ProductCreate,
    current_user: User = Depends(require_owner),
    db: Session = Depends(get_db)
):
    """
    Create a new product (owner only).
    
    Requires all fields: title, description, category, SKU, unit size,
    consumer price, distributor price, and stock quantity.
    """
    try:
        product = product_service.create_product(
            product_data=product_data,
            owner_id=current_user.id,
            db=db
        )
        
        # Return with consumer pricing by default
        from app.models.enums import UserRole
        return product_service.get_product_by_id(product.id, UserRole.CONSUMER, db)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/products/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    product_data: ProductUpdate,
    current_user: User = Depends(require_owner),
    db: Session = Depends(get_db)
):
    """
    Update an existing product (owner only).
    
    All fields are optional. Only provided fields will be updated.
    """
    try:
        product = product_service.update_product(
            product_id=product_id,
            product_data=product_data,
            actor_id=current_user.id,
            db=db
        )
        
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Return with consumer pricing by default
        from app.models.enums import UserRole
        return product_service.get_product_by_id(product.id, UserRole.CONSUMER, db)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/products/{product_id}", status_code=204)
def delete_product(
    product_id: int,
    current_user: User = Depends(require_owner),
    db: Session = Depends(get_db)
):
    """
    Soft delete a product (owner only).
    
    Product will be marked as inactive and hidden from catalogs.
    """
    product = product_service.soft_delete(
        product_id=product_id,
        actor_id=current_user.id,
        db=db
    )
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return None


@router.post("/products/{product_id}/images", status_code=201)
async def upload_product_image(
    product_id: int,
    image: UploadFile = File(..., description="Product image (JPEG, PNG, or WebP, max 5MB)"),
    alt_text: Optional[str] = Form(None, description="Alt text for image"),
    current_user: User = Depends(require_owner),
    db: Session = Depends(get_db)
):
    """
    Upload a product image (owner only).
    
    - **image**: Image file (JPEG, PNG, or WebP, max 5MB)
    - **alt_text**: Optional alt text for accessibility
    
    Returns the created image record with URL.
    """
    try:
        product_image = await product_service.upload_product_image(
            product_id=product_id,
            image_file=image,
            alt_text=alt_text,
            db=db
        )
        
        if not product_image:
            raise HTTPException(status_code=404, detail="Product not found")
        
        return {
            "id": product_image.id,
            "product_id": product_image.product_id,
            "url": product_image.url,
            "alt_text": product_image.alt_text,
            "display_order": product_image.display_order,
            "created_at": product_image.created_at
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload image: {str(e)}")


@router.delete("/products/{product_id}/images/{image_id}", status_code=204)
def delete_product_image(
    product_id: int,
    image_id: int,
    current_user: User = Depends(require_owner),
    db: Session = Depends(get_db)
):
    """
    Delete a product image (owner only).
    
    Removes image from S3 storage and database.
    """
    success = product_service.delete_product_image(
        product_id=product_id,
        image_id=image_id,
        db=db
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="Image not found")
    
    return None


@router.put("/products/{product_id}/stock", response_model=ProductResponse)
def update_product_stock(
    product_id: int,
    stock_update: StockUpdate,
    current_user: User = Depends(require_owner),
    db: Session = Depends(get_db)
):
    """
    Update product stock quantity (owner only).
    
    - **quantity_delta**: Change in stock (positive to add, negative to reduce)
    
    Creates audit log entry for the stock change.
    """
    try:
        product = product_service.update_stock(
            product_id=product_id,
            quantity_delta=stock_update.quantity_delta,
            actor_id=current_user.id,
            db=db
        )
        
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Return with consumer pricing by default
        from app.models.enums import UserRole
        return product_service.get_product_by_id(product.id, UserRole.CONSUMER, db)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
