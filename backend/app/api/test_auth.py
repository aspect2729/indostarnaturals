"""Test authentication endpoint - FOR DEVELOPMENT ONLY"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.models.enums import UserRole
from app.services.auth_service import token_service
from pydantic import BaseModel


router = APIRouter(prefix="/api/v1/test", tags=["test-auth"])


class TestLoginRequest(BaseModel):
    phone: str
    role: str = "consumer"  # consumer, distributor, or owner


class TestLoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    user: dict


@router.post("/login", response_model=TestLoginResponse)
async def test_login(
    request: TestLoginRequest,
    db: Session = Depends(get_db)
):
    """
    TEST ONLY: Create or get user and return tokens without OTP.
    DO NOT USE IN PRODUCTION!
    """
    # Get or create user
    user = db.query(User).filter(User.phone == request.phone).first()
    
    if not user:
        # Create new user
        user = User(
            phone=request.phone,
            email=f"test_{request.phone}@example.com",
            full_name=f"Test User {request.phone}",
            role=UserRole[request.role.upper()],
            is_active=True,
            is_verified=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    
    # Generate tokens
    access_token = token_service.create_access_token({"sub": str(user.id)})
    refresh_token = token_service.create_refresh_token({"sub": str(user.id)})
    
    return TestLoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        user={
            "id": user.id,
            "phone": user.phone,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role.value,
            "is_active": user.is_active,
            "is_verified": user.is_verified
        }
    )
