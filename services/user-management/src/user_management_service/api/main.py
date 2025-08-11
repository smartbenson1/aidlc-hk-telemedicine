"""
FastAPI application for User Management Service.
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import logging
import time
import uuid
from datetime import datetime
from typing import Dict, Any

from .routers import (
    registration,
    sessions,
    profiles,
    availability,
    specialties,
    health
)
from ..utils.exceptions import (
    UserManagementException,
    ValidationError,
    BusinessRuleError,
    NotFoundError,
    AuthenticationError
)
from ..utils.logging_utils import setup_logging, get_logger

# Setup logging
setup_logging()
logger = get_logger(__name__)

# Create FastAPI application
app = FastAPI(
    title="User Management Service API",
    description="REST API for user registration, profile management, session management, and doctor availability",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all domains as specified
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Add trusted host middleware for security
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # Allow all hosts for now
)


@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    """Log all requests and add request ID."""
    request_id = str(uuid.uuid4())
    start_time = time.time()
    
    # Add request ID to request state
    request.state.request_id = request_id
    
    # Log request
    logger.info(
        f"Request started",
        extra={
            "request_id": request_id,
            "method": request.method,
            "url": str(request.url),
            "client_ip": request.client.host if request.client else "unknown"
        }
    )
    
    try:
        response = await call_next(request)
        
        # Log response
        process_time = time.time() - start_time
        logger.info(
            f"Request completed",
            extra={
                "request_id": request_id,
                "status_code": response.status_code,
                "process_time": process_time
            }
        )
        
        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id
        return response
        
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(
            f"Request failed",
            extra={
                "request_id": request_id,
                "error": str(e),
                "process_time": process_time
            }
        )
        raise


@app.exception_handler(UserManagementException)
async def user_management_exception_handler(request: Request, exc: UserManagementException):
    """Handle custom user management exceptions."""
    request_id = getattr(request.state, 'request_id', str(uuid.uuid4()))
    
    status_code = 500
    error_code = "INTERNAL_ERROR"
    
    if isinstance(exc, ValidationError):
        status_code = 400
        error_code = "VALIDATION_ERROR"
    elif isinstance(exc, BusinessRuleError):
        status_code = 422
        error_code = "BUSINESS_RULE_ERROR"
    elif isinstance(exc, NotFoundError):
        status_code = 404
        error_code = "NOT_FOUND"
    elif isinstance(exc, AuthenticationError):
        status_code = 401
        error_code = "AUTHENTICATION_ERROR"
    
    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "message": str(exc),
            "error_code": error_code,
            "timestamp": datetime.utcnow().isoformat(),
            "request_id": request_id
        }
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions."""
    request_id = getattr(request.state, 'request_id', str(uuid.uuid4()))
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.detail,
            "error_code": f"HTTP_{exc.status_code}",
            "timestamp": datetime.utcnow().isoformat(),
            "request_id": request_id
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions."""
    request_id = getattr(request.state, 'request_id', str(uuid.uuid4()))
    
    logger.error(
        f"Unexpected error: {str(exc)}",
        extra={"request_id": request_id},
        exc_info=True
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Internal server error",
            "error_code": "INTERNAL_ERROR",
            "timestamp": datetime.utcnow().isoformat(),
            "request_id": request_id
        }
    )


# Include routers
app.include_router(registration.router, prefix="/api", tags=["Registration"])
app.include_router(sessions.router, prefix="/api", tags=["Sessions"])
app.include_router(profiles.router, prefix="/api", tags=["Profiles"])
app.include_router(availability.router, prefix="/api", tags=["Availability"])
app.include_router(specialties.router, prefix="/api", tags=["Specialties"])
app.include_router(health.router, prefix="/api", tags=["Health"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "User Management Service API",
        "version": "1.0.0",
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/api")
async def api_info():
    """API information endpoint."""
    return {
        "service": "User Management Service API",
        "version": "1.0.0",
        "description": "REST API for user registration, profile management, session management, and doctor availability",
        "docs_url": "/api/docs",
        "redoc_url": "/api/redoc",
        "openapi_url": "/api/openapi.json",
        "timestamp": datetime.utcnow().isoformat()
    }


# Health check for load balancers
@app.get("/health")
async def health_check():
    """Simple health check endpoint."""
    return {"status": "healthy"}