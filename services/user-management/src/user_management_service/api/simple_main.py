"""
Simplified FastAPI application without Pydantic dependencies
"""

import json
import time
import uuid
from datetime import datetime
from typing import Dict, Any

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from .routers import simple_registration
from ..models.simple_models import create_success_response, create_error_response
from ..utils.logging_utils import get_logger

logger = get_logger(__name__)

# Create FastAPI app
app = FastAPI(
    title="User Management Service API (Simplified)",
    description="Simplified REST API for doctor registration without Pydantic dependencies",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_request_id_middleware(request: Request, call_next):
    """Add request ID to all requests."""
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    
    start_time = time.time()
    
    try:
        response = await call_next(request)
        
        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id
        
        # Log request completion
        process_time = time.time() - start_time
        logger.info(
            f"Request completed",
            extra={
                "request_id": request_id,
                "method": request.method,
                "url": str(request.url),
                "status_code": response.status_code,
                "process_time": round(process_time, 3)
            }
        )
        
        return response
        
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(
            f"Request failed",
            extra={
                "request_id": request_id,
                "method": request.method,
                "url": str(request.url),
                "error": str(e),
                "process_time": round(process_time, 3)
            },
            exc_info=True
        )
        
        # Return error response
        response = create_error_response(
            "Internal server error",
            "REQUEST_ERROR"
        )
        return JSONResponse(
            status_code=500,
            content=response.to_dict(),
            headers={"X-Request-ID": request_id}
        )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions."""
    request_id = getattr(request.state, 'request_id', 'unknown')
    
    logger.warning(
        f"HTTP exception",
        extra={
            "request_id": request_id,
            "status_code": exc.status_code,
            "detail": exc.detail
        }
    )
    
    response = create_error_response(
        exc.detail,
        "HTTP_ERROR"
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content=response.to_dict(),
        headers={"X-Request-ID": request_id}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions."""
    request_id = getattr(request.state, 'request_id', 'unknown')
    
    logger.error(
        f"Unhandled exception",
        extra={
            "request_id": request_id,
            "error": str(exc),
            "error_type": type(exc).__name__
        },
        exc_info=True
    )
    
    response = create_error_response(
        "Internal server error",
        "UNHANDLED_ERROR"
    )
    
    return JSONResponse(
        status_code=500,
        content=response.to_dict(),
        headers={"X-Request-ID": request_id}
    )


# Include routers
app.include_router(simple_registration.router, prefix="/api", tags=["Registration"])


@app.get("/")
async def root():
    """Root endpoint."""
    response = create_success_response(
        data={
            "service": "User Management Service API (Simplified)",
            "version": "1.0.0",
            "description": "Simplified REST API for doctor registration",
            "docs_url": "/api/docs",
            "redoc_url": "/api/redoc",
            "health_url": "/api/health"
        }
    )
    return JSONResponse(content=response.to_dict())


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    response = create_success_response(
        data={
            "status": "healthy",
            "service": "user-management-service",
            "version": "1.0.0",
            "timestamp": datetime.utcnow().isoformat(),
            "uptime": "running"
        }
    )
    return JSONResponse(content=response.to_dict())


@app.get("/api/info")
async def service_info():
    """Service information endpoint."""
    response = create_success_response(
        data={
            "service": "User Management Service API (Simplified)",
            "version": "1.0.0",
            "description": "Simplified REST API for doctor registration without Pydantic dependencies",
            "endpoints": {
                "doctor_registration": "/api/doctors/register",
                "health": "/api/health",
                "docs": "/api/docs"
            },
            "features": [
                "Doctor registration",
                "DynamoDB integration",
                "No Pydantic dependencies",
                "ARM Lambda compatible"
            ]
        }
    )
    return JSONResponse(content=response.to_dict())