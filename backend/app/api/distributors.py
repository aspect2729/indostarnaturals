"""Distributor API endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.distributor import (
    DistributorRegistrationRequest,
    DistributorRegistrationResponse,
    ApproveDistributorRequest,
    ApproveDistributorResponse
)
from app.services.user_service import user_service
from app.services.dependencies import get_current_user, require_owner
from app.models.user import User


router = APIRouter(prefix="/api/v1", tags=["distributors"])


@router.post("/distributors/register", response_model=DistributorRegistrationResponse)
async def register_distributor(
    request_data: DistributorRegistrationRequest,
    db: Session = Depends(get_db)
):
    """
    Register as a distributor with pending status.
    
    Requires owner approval before gaining distributor access.
    """
    try:
        user = user_service.register_distributor(
            phone=request_data.phone,
            email=request_data.email,
            name=request_data.name,
            business_name=request_data.business_name,
            db=db
        )
        
        return DistributorRegistrationResponse(
            success=True,
            message="Distributor application submitted successfully. Pending owner approval.",
            user_id=user.id
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to register distributor. Please try again."
        )


@router.post("/owner/distributors/approve", response_model=ApproveDistributorResponse)
async def approve_distributor(
    request_data: ApproveDistributorRequest,
    current_user: User = Depends(require_owner),
    db: Session = Depends(get_db)
):
    """
    Approve or reject a distributor application.
    
    Owner only endpoint.
    """
    try:
        user = user_service.approve_distributor(
            user_id=request_data.user_id,
            approved=request_data.approved,
            actor_id=current_user.id,
            db=db
        )
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        status_text = "approved" if request_data.approved else "rejected"
        
        return ApproveDistributorResponse(
            success=True,
            message=f"Distributor application {status_text} successfully",
            user_id=user.id,
            status=user.distributor_status.value
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process distributor approval. Please try again."
        )
