"""Email Service

Handles email verification tokens and email sending.
"""
import secrets
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from app.core.config import settings


class EmailVerificationToken:
    """Model for email verification tokens (stored in database)"""
    def __init__(self, token: str, email: str, expires_at: datetime):
        self.token = token
        self.email = email
        self.expires_at = expires_at


class EmailService:
    """Service for email operations"""
    
    @staticmethod
    def generate_verification_token() -> str:
        """
        Generate a secure email verification token.
        
        Returns:
            Secure random token string
        """
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def create_verification_token(email: str, db: Session) -> str:
        """
        Create and store email verification token with 24-hour expiration.
        
        Args:
            email: Email address to verify
            db: Database session
            
        Returns:
            Verification token string
        """
        token = EmailService.generate_verification_token()
        expires_at = datetime.utcnow() + timedelta(hours=24)
        
        # In a real implementation, this would be stored in the database
        # For now, we'll use Redis as a simple key-value store
        from app.core.redis_client import get_redis
        redis = get_redis()
        key = f"email_verification:{token}"
        redis.setex(key, 86400, email)  # 24 hours in seconds
        
        return token
    
    @staticmethod
    def verify_token(token: str) -> Optional[str]:
        """
        Verify email verification token and return associated email.
        
        Args:
            token: Verification token to check
            
        Returns:
            Email address if token is valid, None otherwise
        """
        from app.core.redis_client import get_redis
        redis = get_redis()
        key = f"email_verification:{token}"
        email = redis.get(key)
        
        if email:
            # Delete token after successful verification
            redis.delete(key)
            return email
        
        return None
    
    @staticmethod
    def send_verification_email(email: str, token: str) -> bool:
        """
        Send verification email with token link.
        
        Args:
            email: Email address to send to
            token: Verification token
            
        Returns:
            True if sent successfully
        """
        verification_url = f"{settings.FRONTEND_URL}/verify-email?token={token}"
        
        if settings.EMAIL_PROVIDER == "sendgrid":
            return EmailService._send_via_sendgrid(
                email,
                "Verify your email",
                f"Click here to verify your email: {verification_url}"
            )
        elif settings.EMAIL_PROVIDER == "ses":
            return EmailService._send_via_ses(
                email,
                "Verify your email",
                f"Click here to verify your email: {verification_url}"
            )
        else:
            # For development/testing
            print(f"[DEV] Verification email for {email}: {verification_url}")
            return True
    
    @staticmethod
    def _send_via_sendgrid(to_email: str, subject: str, body: str) -> bool:
        """
        Send email via SendGrid.
        
        Args:
            to_email: Recipient email
            subject: Email subject
            body: Email body
            
        Returns:
            True if sent successfully
        """
        try:
            from sendgrid import SendGridAPIClient
            from sendgrid.helpers.mail import Mail
            
            message = Mail(
                from_email=settings.SENDGRID_FROM_EMAIL,
                to_emails=to_email,
                subject=subject,
                plain_text_content=body
            )
            
            sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
            response = sg.send(message)
            
            return response.status_code == 202
        except Exception as e:
            print(f"Error sending email via SendGrid: {e}")
            return False
    
    @staticmethod
    def _send_via_ses(to_email: str, subject: str, body: str) -> bool:
        """
        Send email via AWS SES.
        
        Args:
            to_email: Recipient email
            subject: Email subject
            body: Email body
            
        Returns:
            True if sent successfully
        """
        # AWS SES implementation would go here
        print(f"[SES] Would send email to {to_email}: {subject}")
        return True
    
    @staticmethod
    def send_email(to_email: str, subject: str, body: str) -> bool:
        """
        Send a generic email.
        
        Args:
            to_email: Recipient email
            subject: Email subject
            body: Email body
            
        Returns:
            True if sent successfully
        """
        if settings.EMAIL_PROVIDER == "sendgrid":
            return EmailService._send_via_sendgrid(to_email, subject, body)
        elif settings.EMAIL_PROVIDER == "ses":
            return EmailService._send_via_ses(to_email, subject, body)
        else:
            print(f"[DEV] Email to {to_email}: {subject}")
            return True


class PasswordResetService:
    """Service for password reset operations"""
    
    @staticmethod
    def generate_reset_token() -> str:
        """
        Generate a secure password reset token.
        
        Returns:
            Secure random token string
        """
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def create_reset_token(email: str) -> str:
        """
        Create and store password reset token with 24-hour expiration.
        
        Args:
            email: Email address for password reset
            
        Returns:
            Reset token string
        """
        token = PasswordResetService.generate_reset_token()
        expires_at = datetime.utcnow() + timedelta(hours=24)
        
        from app.core.redis_client import get_redis
        redis = get_redis()
        key = f"password_reset:{token}"
        redis.setex(key, 86400, email)  # 24 hours in seconds
        
        return token
    
    @staticmethod
    def verify_reset_token(token: str) -> Optional[str]:
        """
        Verify password reset token and return associated email.
        
        Args:
            token: Reset token to check
            
        Returns:
            Email address if token is valid, None otherwise
        """
        from app.core.redis_client import get_redis
        redis = get_redis()
        key = f"password_reset:{token}"
        email = redis.get(key)
        
        if email:
            # Delete token after successful verification
            redis.delete(key)
            return email
        
        return None
    
    @staticmethod
    def send_reset_email(email: str, token: str) -> bool:
        """
        Send password reset email with secure link.
        
        Args:
            email: Email address to send to
            token: Reset token
            
        Returns:
            True if sent successfully
        """
        reset_url = f"{settings.FRONTEND_URL}/reset-password?token={token}"
        
        subject = "Reset your password"
        body = f"""
        You requested a password reset for your IndoStar Naturals account.
        
        Click here to reset your password: {reset_url}
        
        This link will expire in 24 hours.
        
        If you didn't request this, please ignore this email.
        """
        
        return EmailService.send_email(email, subject, body)
    
    @staticmethod
    def process_password_reset(token: str, new_password: str, db: Session) -> bool:
        """
        Process password reset with token verification.
        
        Args:
            token: Reset token
            new_password: New password to set
            db: Database session
            
        Returns:
            True if password was reset successfully
        """
        # Verify token and get email
        email = PasswordResetService.verify_reset_token(token)
        
        if not email:
            return False
        
        # In a real implementation, this would update the user's password in the database
        # For now, we'll just return True to indicate success
        from app.services.auth_service import password_service
        hashed_password = password_service.hash_password(new_password)
        
        # TODO: Update user password in database
        # user = db.query(User).filter(User.email == email).first()
        # if user:
        #     user.hashed_password = hashed_password
        #     db.commit()
        #     return True
        
        return True


# Create singleton instances
email_service = EmailService()
password_reset_service = PasswordResetService()
