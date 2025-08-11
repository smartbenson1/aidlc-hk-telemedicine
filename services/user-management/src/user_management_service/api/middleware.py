#!/usr/bin/env python3
"""
API Middleware

Provides middleware functions for the User Management Service API.
"""

from fastapi import Request, Response
from fastapi.responses import JSONResponse
import time
import uuid
from datetime import datetime
from typing import Callable

from ..utils.logging_utils import get_logger

logger = get_logger(__name__)


async def logging_middleware(request: Request, call_next: Callable) -> Response:
    """Middleware for request/response logging."""
    
    # Generate request ID
    request_id = str(uuid.uuid4())
    
    # Add request ID to request state
    request.state.request_id = request_id
    
    # Log request
    start_time = time.time()
    logger.info(
        f"Request started",
        extra={
            "request_id": request_id,
            "method": request.method,
            "url": str(request.url),
            "client_ip": request.client.host if request.client else "unknown",
            "user_agent": request.headers.get("user-agent", "unknown"),
            "timestamp": datetime.utcnow().isoformat()
        }
    )
    
    try:
        # Process request
        response = await call_next(request)
        
        # Calculate processing time
        process_time = time.time() - start_time
        
        # Log response
        logger.info(
            f"Request completed",
            extra={
                "request_id": request_id,
                "method": request.method,
                "url": str(request.url),
                "status_code": response.status_code,
                "process_time": f"{process_time:.4f}s",
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        
        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id
        
        return response
        
    except Exception as e:
        # Calculate processing time
        process_time = time.time() - start_time
        
        # Log error
        logger.error(
            f"Request failed",
            extra={
                "request_id": request_id,
                "method": request.method,
                "url": str(request.url),
                "error": str(e),
                "process_time": f"{process_time:.4f}s",
                "timestamp": datetime.utcnow().isoformat()
            },
            exc_info=True
        )
        
        # Return error response
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": 500,
                    "message": "Internal server error",
                    "type": "INTERNAL_ERROR",
                    "request_id": request_id
                },
                "success": False,
                "timestamp": datetime.utcnow().isoformat()
            },
            headers={"X-Request-ID": request_id}
        )


async def error_handling_middleware(request: Request, call_next: Callable) -> Response:
    """Middleware for global error handling."""
    
    try:
        response = await call_next(request)
        return response
        
    except Exception as e:
        request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
        
        logger.error(
            f"Unhandled exception in middleware",
            extra={
                "request_id": request_id,
                "method": request.method,
                "url": str(request.url),
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            },
            exc_info=True
        )
        
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": 500,
                    "message": "Internal server error",
                    "type": "MIDDLEWARE_ERROR",
                    "request_id": request_id
                },
                "success": False,
                "timestamp": datetime.utcnow().isoformat()
            },
            headers={"X-Request-ID": request_id}
        )


async def cors_middleware(request: Request, call_next: Callable) -> Response:
    """Custom CORS middleware for additional control."""
    
    response = await call_next(request)
    
    # Add additional CORS headers if needed
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    
    return response


async def rate_limiting_middleware(request: Request, call_next: Callable) -> Response:
    """Basic rate limiting middleware (placeholder for future implementation)."""
    
    # TODO: Implement rate limiting logic
    # This could use Redis or in-memory storage to track request counts
    # For now, just pass through
    
    response = await call_next(request)
    return response