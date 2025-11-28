"""OAuth Service

Handles Google OAuth 2.0 authentication.
"""
from typing import Optional, Dict, Any
from google.oauth2 import id_token
from google.auth.transport import requests
from app.core.config import settings


class GoogleOAuthService:
    """Service for Google OAuth operations"""
    
    @staticmethod
    def verify_google_token(token: str) -> Optional[Dict[str, Any]]:
        """
        Verify Google OAuth token and extract user information.
        
        Args:
            token: Google OAuth ID token
            
        Returns:
            User information dict if valid, None otherwise
        """
        try:
            import logging
            logger = logging.getLogger(__name__)
            
            # Verify the token
            logger.info(f"Verifying Google token with client ID: {settings.GOOGLE_OAUTH_CLIENT_ID[:20]}...")
            idinfo = id_token.verify_oauth2_token(
                token,
                requests.Request(),
                settings.GOOGLE_OAUTH_CLIENT_ID
            )
            
            logger.info(f"Token verified successfully. Issuer: {idinfo.get('iss')}")
            
            # Verify the issuer
            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                logger.warning(f"Invalid issuer: {idinfo['iss']}")
                return None
            
            # Extract user information
            user_info = {
                'google_id': idinfo['sub'],
                'email': idinfo.get('email'),
                'name': idinfo.get('name'),
                'picture': idinfo.get('picture'),
                'email_verified': idinfo.get('email_verified', False)
            }
            logger.info(f"Extracted user info for email: {user_info.get('email')}")
            return user_info
            
        except ValueError as e:
            # Invalid token
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error verifying Google token: {e}", exc_info=True)
            return None
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Unexpected error verifying Google token: {e}", exc_info=True)
            return None
    
    @staticmethod
    def get_or_create_user_from_google(google_info: Dict[str, Any], db) -> Optional[Any]:
        """
        Get existing user or create new user from Google OAuth info.
        
        Args:
            google_info: User information from Google
            db: Database session
            
        Returns:
            User object if successful, None otherwise
        """
        from app.models.user import User
        from app.models.enums import UserRole
        
        # Check if user exists by google_id
        user = db.query(User).filter(User.google_id == google_info['google_id']).first()
        
        if user:
            # Update user information if needed
            if google_info.get('email') and not user.email:
                user.email = google_info['email']
            if google_info.get('name') and not user.name:
                user.name = google_info['name']
            if google_info.get('email_verified'):
                user.is_email_verified = True
            db.commit()
            db.refresh(user)
            return user
        
        # Check if user exists by email
        if google_info.get('email'):
            user = db.query(User).filter(User.email == google_info['email']).first()
            if user:
                # Link Google account to existing user
                user.google_id = google_info['google_id']
                if google_info.get('email_verified'):
                    user.is_email_verified = True
                db.commit()
                db.refresh(user)
                return user
        
        # Create new user
        new_user = User(
            email=google_info.get('email'),
            phone='',  # Will need to be added later
            name=google_info.get('name', 'Google User'),
            google_id=google_info['google_id'],
            role=UserRole.CONSUMER,
            is_email_verified=google_info.get('email_verified', False),
            is_active=True
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        return new_user


# Create singleton instance
google_oauth_service = GoogleOAuthService()
