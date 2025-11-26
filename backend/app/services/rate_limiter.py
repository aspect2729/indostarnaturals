"""Rate Limiting Service

Handles rate limiting for authentication endpoints using Redis.
"""
from typing import Optional
from fastapi import Request, HTTPException, status
from app.core.redis_client import get_redis
from app.core.config import settings


class RateLimiter:
    """Service for rate limiting operations"""
    
    @staticmethod
    def get_client_ip(request: Request) -> str:
        """
        Extract client IP address from request.
        
        Args:
            request: FastAPI request object
            
        Returns:
            Client IP address
        """
        # Check for forwarded IP first (for proxy/load balancer scenarios)
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        
        # Fall back to direct client IP
        return request.client.host if request.client else "unknown"
    
    @staticmethod
    def check_rate_limit(
        identifier: str,
        max_attempts: int = None,
        window_minutes: int = None
    ) -> bool:
        """
        Check if rate limit has been exceeded.
        
        Args:
            identifier: Unique identifier (e.g., IP address, user ID)
            max_attempts: Maximum number of attempts allowed
            window_minutes: Time window in minutes
            
        Returns:
            True if within rate limit, False if exceeded
        """
        if max_attempts is None:
            max_attempts = settings.RATE_LIMIT_AUTH_ATTEMPTS
        if window_minutes is None:
            window_minutes = settings.RATE_LIMIT_AUTH_WINDOW_MINUTES
        
        redis = get_redis()
        key = f"rate_limit:{identifier}"
        
        # Get current count
        current = redis.get(key)
        
        if current is None:
            # First attempt, set counter with expiration
            redis.setex(key, window_minutes * 60, 1)
            return True
        
        current_count = int(current)
        
        if current_count >= max_attempts:
            # Rate limit exceeded
            return False
        
        # Increment counter
        redis.incr(key)
        return True
    
    @staticmethod
    def get_remaining_attempts(
        identifier: str,
        max_attempts: int = None
    ) -> int:
        """
        Get remaining attempts before rate limit.
        
        Args:
            identifier: Unique identifier
            max_attempts: Maximum number of attempts allowed
            
        Returns:
            Number of remaining attempts
        """
        if max_attempts is None:
            max_attempts = settings.RATE_LIMIT_AUTH_ATTEMPTS
        
        redis = get_redis()
        key = f"rate_limit:{identifier}"
        
        current = redis.get(key)
        if current is None:
            return max_attempts
        
        current_count = int(current)
        remaining = max_attempts - current_count
        return max(0, remaining)
    
    @staticmethod
    def get_retry_after(identifier: str) -> Optional[int]:
        """
        Get seconds until rate limit resets.
        
        Args:
            identifier: Unique identifier
            
        Returns:
            Seconds until reset, or None if not rate limited
        """
        redis = get_redis()
        key = f"rate_limit:{identifier}"
        
        ttl = redis.ttl(key)
        if ttl > 0:
            return ttl
        
        return None
    
    @staticmethod
    def reset_rate_limit(identifier: str) -> None:
        """
        Reset rate limit for an identifier.
        
        Args:
            identifier: Unique identifier to reset
        """
        redis = get_redis()
        key = f"rate_limit:{identifier}"
        redis.delete(key)


def rate_limit_auth(request: Request) -> None:
    """
    Rate limiting dependency for authentication endpoints.
    
    Applies 5 attempts per 15 minutes limit.
    Returns 429 Too Many Requests when limit exceeded.
    
    Args:
        request: FastAPI request object
        
    Raises:
        HTTPException: 429 if rate limit exceeded
    """
    ip_address = RateLimiter.get_client_ip(request)
    
    if not RateLimiter.check_rate_limit(ip_address):
        retry_after = RateLimiter.get_retry_after(ip_address)
        
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many authentication attempts. Please try again later.",
            headers={"Retry-After": str(retry_after)} if retry_after else {}
        )


# Create singleton instance
rate_limiter = RateLimiter()
