"""Authentication Service

Handles JWT token generation, verification, refresh logic, and password hashing.
"""
from datetime import datetime, timedelta
from typing import Dict, Any
from jose import JWTError, jwt
import bcrypt
from app.core.config import settings


class TokenService:
    """Service for JWT token operations"""
    
    @staticmethod
    def create_access_token(data: Dict[str, Any]) -> str:
        """
        Create a JWT access token with 1 hour expiration.
        
        Args:
            data: Dictionary containing user data to encode in token
            
        Returns:
            Encoded JWT token string
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire, "type": "access"})
        
        encoded_jwt = jwt.encode(
            to_encode,
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM
        )
        return encoded_jwt
    
    @staticmethod
    def create_refresh_token(data: Dict[str, Any]) -> str:
        """
        Create a JWT refresh token with 7 day expiration.
        
        Args:
            data: Dictionary containing user data to encode in token
            
        Returns:
            Encoded JWT refresh token string
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire, "type": "refresh"})
        
        encoded_jwt = jwt.encode(
            to_encode,
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM
        )
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str, token_type: str = "access") -> Dict[str, Any] | None:
        """
        Verify and decode a JWT token.
        
        Args:
            token: JWT token string to verify
            token_type: Expected token type ("access" or "refresh")
            
        Returns:
            Decoded token payload if valid, None otherwise
        """
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM]
            )
            
            # Verify token type matches expected type
            if payload.get("type") != token_type:
                return None
            
            # Check if token is expired (jose handles this automatically)
            return payload
            
        except JWTError:
            return None
    
    @staticmethod
    def refresh_access_token(refresh_token: str) -> str | None:
        """
        Generate a new access token from a valid refresh token.
        
        Args:
            refresh_token: Valid refresh token string
            
        Returns:
            New access token if refresh token is valid, None otherwise
        """
        payload = TokenService.verify_token(refresh_token, token_type="refresh")
        
        if payload is None:
            return None
        
        # Extract user data (excluding exp and type)
        user_data = {k: v for k, v in payload.items() if k not in ["exp", "type"]}
        
        # Create new access token
        return TokenService.create_access_token(user_data)
    
    @staticmethod
    def create_token_pair(user_id: int, email: str | None, phone: str, role: str) -> Dict[str, str]:
        """
        Create both access and refresh tokens for a user.
        
        Args:
            user_id: User's database ID
            email: User's email address (optional)
            phone: User's phone number
            role: User's role (consumer, distributor, owner)
            
        Returns:
            Dictionary with access_token and refresh_token
        """
        user_data = {
            "sub": str(user_id),
            "email": email,
            "phone": phone,
            "role": role
        }
        
        return {
            "access_token": TokenService.create_access_token(user_data),
            "refresh_token": TokenService.create_refresh_token(user_data)
        }


class PasswordService:
    """Service for password hashing and verification"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a password using bcrypt with cost factor 12.
        
        Args:
            password: Plain text password to hash
            
        Returns:
            Bcrypt hashed password string
        """
        # Convert password to bytes
        password_bytes = password.encode('utf-8')
        # Generate salt with cost factor 12
        salt = bcrypt.gensalt(rounds=12)
        # Hash the password
        hashed = bcrypt.hashpw(password_bytes, salt)
        # Return as string
        return hashed.decode('utf-8')
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Verify a plain text password against a hashed password.
        
        Args:
            plain_password: Plain text password to verify
            hashed_password: Bcrypt hashed password to compare against
            
        Returns:
            True if password matches, False otherwise
        """
        # Convert to bytes
        password_bytes = plain_password.encode('utf-8')
        hashed_bytes = hashed_password.encode('utf-8')
        # Verify
        return bcrypt.checkpw(password_bytes, hashed_bytes)


# Create singleton instances
token_service = TokenService()
password_service = PasswordService()
