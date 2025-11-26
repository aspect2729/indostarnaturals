"""Custom Exception Classes for IndoStar Naturals API"""
from typing import Any, Dict, List, Optional
from datetime import datetime


class AppException(Exception):
    """Base exception class for all application exceptions"""
    
    def __init__(
        self,
        message: str,
        code: str,
        status_code: int = 500,
        details: Optional[List[Dict[str, Any]]] = None
    ):
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or []
        super().__init__(self.message)


class ValidationException(AppException):
    """Exception for validation errors (400)"""
    
    def __init__(
        self,
        message: str = "Validation failed",
        details: Optional[List[Dict[str, Any]]] = None
    ):
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            status_code=400,
            details=details
        )


class AuthenticationException(AppException):
    """Exception for authentication errors (401)"""
    
    def __init__(
        self,
        message: str = "Authentication failed",
        details: Optional[List[Dict[str, Any]]] = None
    ):
        super().__init__(
            message=message,
            code="AUTHENTICATION_ERROR",
            status_code=401,
            details=details
        )


class AuthorizationException(AppException):
    """Exception for authorization errors (403)"""
    
    def __init__(
        self,
        message: str = "Access forbidden",
        details: Optional[List[Dict[str, Any]]] = None
    ):
        super().__init__(
            message=message,
            code="AUTHORIZATION_ERROR",
            status_code=403,
            details=details
        )


class NotFoundException(AppException):
    """Exception for resource not found errors (404)"""
    
    def __init__(
        self,
        message: str = "Resource not found",
        details: Optional[List[Dict[str, Any]]] = None
    ):
        super().__init__(
            message=message,
            code="NOT_FOUND",
            status_code=404,
            details=details
        )


class ConflictException(AppException):
    """Exception for conflict errors (409)"""
    
    def __init__(
        self,
        message: str = "Resource conflict",
        details: Optional[List[Dict[str, Any]]] = None
    ):
        super().__init__(
            message=message,
            code="CONFLICT_ERROR",
            status_code=409,
            details=details
        )


class RateLimitException(AppException):
    """Exception for rate limit errors (429)"""
    
    def __init__(
        self,
        message: str = "Too many requests",
        details: Optional[List[Dict[str, Any]]] = None
    ):
        super().__init__(
            message=message,
            code="RATE_LIMIT_EXCEEDED",
            status_code=429,
            details=details
        )


class ServerException(AppException):
    """Exception for server errors (500)"""
    
    def __init__(
        self,
        message: str = "Internal server error",
        details: Optional[List[Dict[str, Any]]] = None
    ):
        super().__init__(
            message=message,
            code="SERVER_ERROR",
            status_code=500,
            details=details
        )


class ExternalServiceException(AppException):
    """Exception for external service failures (502)"""
    
    def __init__(
        self,
        message: str = "External service unavailable",
        details: Optional[List[Dict[str, Any]]] = None
    ):
        super().__init__(
            message=message,
            code="EXTERNAL_SERVICE_ERROR",
            status_code=502,
            details=details
        )
