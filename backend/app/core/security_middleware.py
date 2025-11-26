"""Security middleware for input sanitization and security headers"""
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import logging

logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add security headers to all responses.
    
    Implements security best practices including:
    - Content Security Policy (CSP)
    - X-Frame-Options
    - X-Content-Type-Options
    - X-XSS-Protection
    - Strict-Transport-Security (HSTS)
    """
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next):
        """Add security headers to response"""
        response = await call_next(request)
        
        # Content Security Policy
        # Restricts sources of content to prevent XSS attacks
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://checkout.razorpay.com; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self' https://api.razorpay.com; "
            "frame-src https://api.razorpay.com; "
            "object-src 'none'; "
            "base-uri 'self'; "
            "form-action 'self';"
        )
        
        # Prevent clickjacking attacks
        response.headers["X-Frame-Options"] = "DENY"
        
        # Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        # Enable XSS protection in older browsers
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # Enforce HTTPS (only in production)
        # Note: max-age is set to 1 year (31536000 seconds)
        if request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains"
            )
        
        # Referrer policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Permissions policy (formerly Feature-Policy)
        response.headers["Permissions-Policy"] = (
            "geolocation=(), "
            "microphone=(), "
            "camera=(), "
            "payment=(self)"
        )
        
        return response


class InputSanitizationMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log and detect potentially malicious input.
    
    Note: Primary validation happens in Pydantic schemas.
    This middleware provides an additional layer of defense.
    """
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next):
        """Check for suspicious patterns in request"""
        
        # Check query parameters
        if request.query_params:
            for key, value in request.query_params.items():
                if self._is_suspicious(value):
                    logger.warning(
                        f"Suspicious query parameter detected: {key}={value[:100]} "
                        f"from IP: {request.client.host}"
                    )
        
        # Check path parameters
        if self._is_suspicious(str(request.url.path)):
            logger.warning(
                f"Suspicious path detected: {request.url.path} "
                f"from IP: {request.client.host}"
            )
        
        response = await call_next(request)
        return response
    
    def _is_suspicious(self, value: str) -> bool:
        """
        Check if value contains suspicious patterns.
        
        Args:
            value: String to check
            
        Returns:
            True if suspicious patterns detected
        """
        if not value:
            return False
        
        value_upper = value.upper()
        
        # SQL injection patterns
        sql_keywords = [
            "UNION SELECT", "DROP TABLE", "DELETE FROM",
            "INSERT INTO", "UPDATE SET", "'; DROP",
            "' OR '1'='1", "' OR 1=1", "-- ", "/*", "*/"
        ]
        
        for keyword in sql_keywords:
            if keyword in value_upper:
                return True
        
        # XSS patterns
        xss_patterns = [
            "<script", "javascript:", "onerror=", "onload=",
            "<iframe", "<object", "<embed"
        ]
        
        value_lower = value.lower()
        for pattern in xss_patterns:
            if pattern in value_lower:
                return True
        
        # Path traversal
        if "../" in value or "..%2F" in value or "..%5C" in value:
            return True
        
        return False


def add_security_middleware(app):
    """
    Add security middleware to FastAPI application.
    
    Args:
        app: FastAPI application instance
    """
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(InputSanitizationMiddleware)
