"""Authentication API endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.auth import (
    SendOTPRequest,
    SendOTPResponse,
    VerifyOTPRequest,
    TokenResponse,
    GoogleAuthRequest,
    RefreshTokenRequest,
    RefreshTokenResponse,
    RequestPasswordResetRequest,
    RequestPasswordResetResponse,
    CompletePasswordResetRequest,
    CompletePasswordResetResponse,
    UserResponse
)
from app.services.user_service import user_service
from app.services.auth_service import token_service
from app.services.email_service import password_reset_service
from app.services.rate_limiter import RateLimiter
from fastapi import Request


router = APIRouter(prefix="/api/v1/auth", tags=["authentication"])


@router.post("/send-otp", response_model=SendOTPResponse)
async def send_otp(
    request_data: SendOTPRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Send OTP to phone number for authentication.
    
    Rate limited to 5 attempts per 15 minutes per IP address.
    """
    try:
        # Get client IP for rate limiting
        client_ip = request.client.host if request.client else "unknown"
        
        # Check rate limit
        if not RateLimiter.check_rate_limit(
            identifier=f"otp:{client_ip}",
            max_attempts=5,
            window_minutes=15
        ):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many OTP requests. Please try again later."
            )
        
        # Send OTP
        success = user_service.send_otp(request_data.phone)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send OTP. Please try again."
            )
        
        return SendOTPResponse(
            success=True,
            message="OTP sent successfully"
        )
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except ConnectionError as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Redis connection error in send_otp: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service is temporarily unavailable. Redis server is not running."
        )
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Unexpected error in send_otp: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )


@router.post("/verify-otp", response_model=TokenResponse)
async def verify_otp(
    request_data: VerifyOTPRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Verify OTP and return JWT tokens.
    
    Rate limited to 5 attempts per 15 minutes per IP address.
    """
    # Get client IP for rate limiting
    client_ip = request.client.host if request.client else "unknown"
    
    # Check rate limit
    if not RateLimiter.check_rate_limit(
        identifier=f"verify:{client_ip}",
        max_attempts=5,
        window_minutes=15
    ):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many verification attempts. Please try again later."
        )
    
    # Authenticate with OTP
    result = user_service.authenticate_with_otp(
        phone=request_data.phone,
        otp=request_data.otp,
        db=db
    )
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid OTP code"
        )
    
    user, access_token, refresh_token = result
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserResponse.model_validate(user)
    )


@router.post("/google", response_model=TokenResponse)
async def google_auth(
    request_data: GoogleAuthRequest,
    db: Session = Depends(get_db)
):
    """
    Authenticate with Google OAuth and return JWT tokens.
    """
    try:
        # Authenticate with Google
        result = user_service.authenticate_with_google(
            google_token=request_data.token,
            db=db
        )
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Google token"
            )
        
        user, access_token, refresh_token = result
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            user=UserResponse.model_validate(user)
        )
    except HTTPException:
        raise
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Google authentication error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Google authentication failed: {str(e)}"
        )


@router.post("/refresh", response_model=RefreshTokenResponse)
async def refresh_token(request_data: RefreshTokenRequest):
    """
    Refresh access token using refresh token.
    """
    # Generate new access token
    new_access_token = token_service.refresh_access_token(request_data.refresh_token)
    
    if not new_access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )
    
    return RefreshTokenResponse(
        access_token=new_access_token
    )


@router.post("/reset-password", response_model=RequestPasswordResetResponse)
async def request_password_reset(
    request_data: RequestPasswordResetRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Request password reset email.
    
    Rate limited to 5 attempts per 15 minutes per IP address.
    """
    # Get client IP for rate limiting
    client_ip = request.client.host if request.client else "unknown"
    
    # Check rate limit
    if not RateLimiter.check_rate_limit(
        identifier=f"reset:{client_ip}",
        max_attempts=5,
        window_minutes=15
    ):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many password reset requests. Please try again later."
        )
    
    # Check if user exists
    user = user_service.get_user_by_email(request_data.email, db)
    
    if not user:
        # Don't reveal if email exists or not for security
        return RequestPasswordResetResponse(
            success=True,
            message="If the email exists, a password reset link has been sent."
        )
    
    # Create reset token and send email
    token = password_reset_service.create_reset_token(request_data.email)
    success = password_reset_service.send_reset_email(request_data.email, token)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send password reset email. Please try again."
        )
    
    return RequestPasswordResetResponse(
        success=True,
        message="If the email exists, a password reset link has been sent."
    )


@router.put("/reset-password", response_model=CompletePasswordResetResponse)
async def complete_password_reset(
    request_data: CompletePasswordResetRequest,
    db: Session = Depends(get_db)
):
    """
    Complete password reset with token and new password.
    """
    # Process password reset
    success = password_reset_service.process_password_reset(
        token=request_data.token,
        new_password=request_data.new_password,
        db=db
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    return CompletePasswordResetResponse(
        success=True,
        message="Password reset successfully"
    )
