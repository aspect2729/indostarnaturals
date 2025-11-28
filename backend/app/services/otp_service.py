"""OTP Service

Handles OTP generation, storage, verification, and SMS sending.
"""
import random
import string
from typing import Optional
from app.core.redis_client import get_redis
from app.core.config import settings

# OTP expiration time in seconds (10 minutes)
OTP_EXPIRATION = 600


class OTPService:
    """Service for OTP operations"""
    
    @staticmethod
    def generate_otp() -> str:
        """
        Generate a 6-digit OTP code.
        
        Returns:
            6-digit OTP string
        """
        return ''.join(random.choices(string.digits, k=6))
    
    @staticmethod
    def store_otp(phone: str, otp: str) -> bool:
        """
        Store OTP in Redis with 10-minute expiration.
        
        Args:
            phone: Phone number to associate with OTP
            otp: OTP code to store
            
        Returns:
            True if stored successfully
            
        Raises:
            ConnectionError: If Redis is not available
        """
        try:
            redis = get_redis()
            key = f"otp:{phone}"
            redis.setex(key, OTP_EXPIRATION, otp)
            return True
        except ConnectionError as e:
            raise ConnectionError("Redis is not available. Please ensure Redis server is running. See REDIS_SETUP_GUIDE.md for instructions.") from e
    
    @staticmethod
    def verify_otp(phone: str, otp: str) -> bool:
        """
        Verify OTP against stored value.
        
        Args:
            phone: Phone number to verify
            otp: OTP code to verify
            
        Returns:
            True if OTP is valid, False otherwise
            
        Raises:
            ConnectionError: If Redis is not available
        """
        try:
            redis = get_redis()
            key = f"otp:{phone}"
            stored_otp = redis.get(key)
            
            if stored_otp is None:
                return False
            
            # Verify OTP matches
            if stored_otp == otp:
                # Delete OTP after successful verification
                redis.delete(key)
                return True
            
            return False
        except ConnectionError as e:
            raise ConnectionError("Redis is not available. Please ensure Redis server is running. See REDIS_SETUP_GUIDE.md for instructions.") from e
    
    @staticmethod
    def send_otp_sms(phone: str, otp: str) -> bool:
        """
        Send OTP via SMS using configured provider.
        
        Args:
            phone: Phone number to send OTP to
            otp: OTP code to send
            
        Returns:
            True if sent successfully, False otherwise
        """
        # Check which SMS provider is configured
        if settings.SMS_PROVIDER == "twilio":
            return OTPService._send_via_twilio(phone, otp)
        elif settings.SMS_PROVIDER == "msg91":
            return OTPService._send_via_msg91(phone, otp)
        else:
            # For development/testing, just log the OTP
            print(f"[DEV] OTP for {phone}: {otp}")
            return True
    
    @staticmethod
    def _send_via_twilio(phone: str, otp: str) -> bool:
        """
        Send OTP via Twilio.
        
        Args:
            phone: Phone number
            otp: OTP code
            
        Returns:
            True if sent successfully
        """
        try:
            from twilio.rest import Client
            
            client = Client(
                settings.TWILIO_ACCOUNT_SID,
                settings.TWILIO_AUTH_TOKEN
            )
            
            message = client.messages.create(
                body=f"Your IndoStar Naturals verification code is: {otp}. Valid for 10 minutes.",
                from_=settings.TWILIO_PHONE_NUMBER,
                to=phone
            )
            
            return message.sid is not None
        except Exception as e:
            print(f"Error sending OTP via Twilio: {e}")
            return False
    
    @staticmethod
    def _send_via_msg91(phone: str, otp: str) -> bool:
        """
        Send OTP via MSG91.
        
        Args:
            phone: Phone number
            otp: OTP code
            
        Returns:
            True if sent successfully
        """
        # MSG91 implementation would go here
        # For now, return True for development
        print(f"[MSG91] Would send OTP {otp} to {phone}")
        return True
    
    @staticmethod
    def create_and_send_otp(phone: str) -> bool:
        """
        Generate, store, and send OTP in one operation.
        
        Args:
            phone: Phone number to send OTP to
            
        Returns:
            True if OTP was created and sent successfully
        """
        otp = OTPService.generate_otp()
        OTPService.store_otp(phone, otp)
        return OTPService.send_otp_sms(phone, otp)


# Create singleton instance
otp_service = OTPService()
