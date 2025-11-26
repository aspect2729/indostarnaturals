"""Owner User Management API endpoints"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.core.database import get_db
from app.services.user_service import user_service
from app.services.dependencies import require_owner
from app.models.user import User
from app.models.enums import UserRole, DistributorStatus


router = APIRouter(prefix="/api/v1/owner/users", tags=["owner-users"])


class UserRoleUpdate(BaseModel):
    """Schema for updating user role"""
    role: UserRole


class UserResponse(BaseModel):
    """Schema for user response"""
    id: int
    email: Optional[str]
    phone: str
    name: str
    role: UserRole
    distributor_status: Optional[DistributorStatus]
    is_email_verified: bool
    is_phone_verified: bool
    is_active: bool
    
    class Config:
        from_attributes = True


@router.get("", response_model=list[UserResponse])
async def get_all_users(
    role_filter: Optional[UserRole] = Query(None, description="Filter by user role"),
    status_filter: Optional[bool] = Query(None, description="Filter by active status"),
    distributor_status_filter: Optional[DistributorStatus] = Query(None, description="Filter by distributor status"),
    current_user: User = Depends(require_owner),
    db: Session = Depends(get_db)
):
    """
    Get all users with filtering (owner only).
    
    Returns a list of all users in the system with filtering options.
    Only accessible by users with owner role.
    
    Filters:
    - role_filter: Filter by user role (consumer, distributor, owner)
    - status_filter: Filter by active status (true/false)
    - distributor_status_filter: Filter by distributor status (pending, approved, rejected)
    
    Requirements: 10.4
    """
    users = user_service.get_all_users(
        db=db,
        role_filter=role_filter,
        status_filter=status_filter,
        distributor_status_filter=distributor_status_filter
    )
    
    return users


@router.put("/{user_id}/role", response_model=UserResponse)
async def update_user_role(
    user_id: int,
    role_update: UserRoleUpdate,
    current_user: User = Depends(require_owner),
    db: Session = Depends(get_db)
):
    """
    Update user role (owner only).
    
    Updates the role of a user and creates an audit log entry.
    Only accessible by users with owner role.
    
    Requirements: 10.5, 15.3
    """
    # Update user role
    updated_user = user_service.update_user_role(
        user_id=user_id,
        new_role=role_update.role,
        actor_id=current_user.id,
        db=db
    )
    
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return updated_user
