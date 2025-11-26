"""FastAPI Exception Handlers for Standardized Error Responses"""
import uuid
import logging
import traceback
from typing import Any, Dict
from datetime import datetime
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError

from app.core.exceptions import (
    AppException,
    ValidationException,
    AuthenticationException,
    AuthorizationException,
    NotFoundException,
    ConflictException,
    RateLimitException,
    ServerException,
)

logger = logging.getLogger(__name__)


def create_error_response(
    code: str,
    message: str,
    status_code: int,
    details: list = None,
    request_id: str = None
) -> Dict[str, Any]:
    """Create standardized error response"""
    return {
        "error": {
            "code": code,
            "message": message,
            "details": details or [],
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "request_id": request_id or str(uuid.uuid4())
        }
    }


def add_exception_handlers(app: FastAPI):
    """Add all exception handlers to FastAPI app"""
    
    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        """Handle custom application exceptions"""
        request_id = request.state.request_id if hasattr(request.state, "request_id") else str(uuid.uuid4())
        
        # Log the error
        logger.error(
            f"Application error: {exc.code} - {exc.message}",
            extra={
                "request_id": request_id,
                "path": request.url.path,
                "method": request.method,
                "status_code": exc.status_code,
                "details": exc.details
            }
        )
        
        return JSONResponse(
            status_code=exc.status_code,
            content=create_error_response(
                code=exc.code,
                message=exc.message,
                status_code=exc.status_code,
                details=exc.details,
                request_id=request_id
            )
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """Handle Pydantic validation errors (400)"""
        request_id = request.state.request_id if hasattr(request.state, "request_id") else str(uuid.uuid4())
        
        # Extract field-level validation errors
        details = []
        for error in exc.errors():
            field = ".".join(str(loc) for loc in error["loc"] if loc != "body")
            details.append({
                "field": field,
                "message": error["msg"],
                "type": error["type"]
            })
        
        logger.warning(
            f"Validation error on {request.method} {request.url.path}",
            extra={
                "request_id": request_id,
                "details": details
            }
        )
        
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=create_error_response(
                code="VALIDATION_ERROR",
                message="Validation failed",
                status_code=400,
                details=details,
                request_id=request_id
            )
        )
    
    @app.exception_handler(ValidationError)
    async def pydantic_validation_exception_handler(request: Request, exc: ValidationError):
        """Handle Pydantic validation errors from models (400)"""
        request_id = request.state.request_id if hasattr(request.state, "request_id") else str(uuid.uuid4())
        
        # Extract field-level validation errors
        details = []
        for error in exc.errors():
            field = ".".join(str(loc) for loc in error["loc"])
            details.append({
                "field": field,
                "message": error["msg"],
                "type": error["type"]
            })
        
        logger.warning(
            f"Pydantic validation error on {request.method} {request.url.path}",
            extra={
                "request_id": request_id,
                "details": details
            }
        )
        
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=create_error_response(
                code="VALIDATION_ERROR",
                message="Validation failed",
                status_code=400,
                details=details,
                request_id=request_id
            )
        )
    
    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
        """Handle database errors (500)"""
        request_id = request.state.request_id if hasattr(request.state, "request_id") else str(uuid.uuid4())
        
        # Log full error details
        logger.error(
            f"Database error: {str(exc)}",
            extra={
                "request_id": request_id,
                "path": request.url.path,
                "method": request.method,
                "traceback": traceback.format_exc()
            }
        )
        
        # Return sanitized error message
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=create_error_response(
                code="DATABASE_ERROR",
                message="A database error occurred",
                status_code=500,
                request_id=request_id
            )
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle all unhandled exceptions (500)"""
        request_id = request.state.request_id if hasattr(request.state, "request_id") else str(uuid.uuid4())
        
        # Log full error details with stack trace
        logger.error(
            f"Unhandled exception: {type(exc).__name__} - {str(exc)}",
            extra={
                "request_id": request_id,
                "path": request.url.path,
                "method": request.method,
                "traceback": traceback.format_exc()
            },
            exc_info=True
        )
        
        # Return sanitized error message (don't expose internal details)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=create_error_response(
                code="SERVER_ERROR",
                message="An unexpected error occurred",
                status_code=500,
                request_id=request_id
            )
        )
