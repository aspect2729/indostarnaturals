"""User Profile API endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.user import (
    UserProfileResponse,
    UserUpdateRequest,
    AddressCreateRequest,
    AddressUpdateRequest,
    AddressResponse
)
from app.services.dependencies import get_current_active_user
from app.models.user import User
from app.models.address import Address


router = APIRouter(prefix="/api/v1/users", tags=["users"])


@router.get("/me", response_model=UserProfileResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current user profile.
    """
    return UserProfileResponse.model_validate(current_user)


@router.put("/me", response_model=UserProfileResponse)
async def update_current_user_profile(
    update_data: UserUpdateRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update current user profile.
    """
    # Update fields if provided
    if update_data.name is not None:
        current_user.name = update_data.name
    
    if update_data.email is not None:
        # Check if email is already taken by another user
        existing_user = db.query(User).filter(
            User.email == update_data.email,
            User.id != current_user.id
        ).first()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        current_user.email = update_data.email
        # Reset email verification if email changed
        current_user.is_email_verified = False
    
    db.commit()
    db.refresh(current_user)
    
    return UserProfileResponse.model_validate(current_user)


@router.get("/me/addresses", response_model=list[AddressResponse])
async def get_user_addresses(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get all addresses for current user.
    """
    addresses = db.query(Address).filter(
        Address.user_id == current_user.id
    ).order_by(Address.is_default.desc(), Address.created_at.desc()).all()
    
    return [AddressResponse.model_validate(addr) for addr in addresses]


@router.post("/me/addresses", response_model=AddressResponse, status_code=status.HTTP_201_CREATED)
async def create_address(
    address_data: AddressCreateRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Add new address for current user.
    """
    # If this is set as default, unset other default addresses
    if address_data.is_default:
        db.query(Address).filter(
            Address.user_id == current_user.id,
            Address.is_default == True
        ).update({"is_default": False})
    
    # Create new address
    new_address = Address(
        user_id=current_user.id,
        name=address_data.name,
        phone=address_data.phone,
        address_line1=address_data.address_line1,
        address_line2=address_data.address_line2,
        city=address_data.city,
        state=address_data.state,
        postal_code=address_data.postal_code,
        country=address_data.country,
        is_default=address_data.is_default
    )
    
    db.add(new_address)
    db.commit()
    db.refresh(new_address)
    
    return AddressResponse.model_validate(new_address)


@router.put("/me/addresses/{address_id}", response_model=AddressResponse)
async def update_address(
    address_id: int,
    address_data: AddressUpdateRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update address for current user.
    """
    # Get address
    address = db.query(Address).filter(
        Address.id == address_id,
        Address.user_id == current_user.id
    ).first()
    
    if not address:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Address not found"
        )
    
    # If setting as default, unset other default addresses
    if address_data.is_default is True and not address.is_default:
        db.query(Address).filter(
            Address.user_id == current_user.id,
            Address.is_default == True,
            Address.id != address_id
        ).update({"is_default": False})
    
    # Update fields if provided
    if address_data.name is not None:
        address.name = address_data.name
    if address_data.phone is not None:
        address.phone = address_data.phone
    if address_data.address_line1 is not None:
        address.address_line1 = address_data.address_line1
    if address_data.address_line2 is not None:
        address.address_line2 = address_data.address_line2
    if address_data.city is not None:
        address.city = address_data.city
    if address_data.state is not None:
        address.state = address_data.state
    if address_data.postal_code is not None:
        address.postal_code = address_data.postal_code
    if address_data.country is not None:
        address.country = address_data.country
    if address_data.is_default is not None:
        address.is_default = address_data.is_default
    
    db.commit()
    db.refresh(address)
    
    return AddressResponse.model_validate(address)


@router.delete("/me/addresses/{address_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_address(
    address_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete address for current user.
    """
    # Get address
    address = db.query(Address).filter(
        Address.id == address_id,
        Address.user_id == current_user.id
    ).first()
    
    if not address:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Address not found"
        )
    
    db.delete(address)
    db.commit()
    
    return None
