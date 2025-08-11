"""
Simplified registration router without Pydantic dependencies
"""

import json
from datetime import datetime
from decimal import Decimal
from typing import Dict, Any

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse

from ...models.simple_models import (
    DoctorRegistrationData, 
    create_success_response, 
    create_error_response
)
from ...database.dynamodb_doctor_repository import DynamoDBDoctorRepository
from ...models.doctor import Doctor
from ...utils.enums import UserStatus
from ...utils.logging_utils import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.post("/doctors/register")
async def register_doctor_simple(request: Request):
    """Register a new doctor without Pydantic validation."""
    request_id = getattr(request.state, 'request_id', 'unknown')
    
    try:
        # Parse request body manually
        body = await request.body()
        try:
            data = json.loads(body.decode('utf-8'))
        except json.JSONDecodeError:
            response = create_error_response(
                "Invalid JSON in request body",
                "INVALID_JSON"
            )
            return JSONResponse(
                status_code=400,
                content=response.to_dict()
            )
        
        # Create and validate registration data
        reg_data = DoctorRegistrationData.from_dict(data)
        validation_errors = reg_data.validate()
        
        if validation_errors:
            response = create_error_response(
                f"Validation failed: {'; '.join(validation_errors)}",
                "VALIDATION_ERROR"
            )
            return JSONResponse(
                status_code=400,
                content=response.to_dict()
            )
        
        logger.info(f"Doctor registration request", extra={
            "request_id": request_id,
            "email": reg_data.email,
            "name": reg_data.name
        })
        
        # Create doctor repository
        doctor_repository = DynamoDBDoctorRepository()
        
        # Generate doctor ID
        doctor_id = f"doctor_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Create doctor object
        doctor = Doctor(
            id=doctor_id,
            name=reg_data.name,
            email=reg_data.email,
            phone=reg_data.phone,
            location=reg_data.location,
            specialties=reg_data.specialties,
            experience=reg_data.experience,
            rating=Decimal('4.5'),  # Default rating
            status=UserStatus.ACTIVE,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Save to DynamoDB
        try:
            created_doctor = doctor_repository.create_with_email_check(doctor)
            
            logger.info(f"Doctor registered successfully", extra={
                "request_id": request_id,
                "doctor_id": created_doctor.id,
                "email": created_doctor.email
            })
            
            response = create_success_response(
                data={
                    "user_id": created_doctor.id,
                    "user_type": "doctor",
                    "email": created_doctor.email,
                    "name": created_doctor.name,
                    "message": "Doctor registered successfully"
                }
            )
            
            return JSONResponse(
                status_code=200,
                content=response.to_dict()
            )
            
        except Exception as db_error:
            logger.error(f"Database error during registration", extra={
                "request_id": request_id,
                "error": str(db_error)
            })
            
            # Check if it's a duplicate email error
            if "email already exists" in str(db_error).lower():
                response = create_error_response(
                    "Email address is already registered",
                    "DUPLICATE_EMAIL"
                )
                return JSONResponse(
                    status_code=409,
                    content=response.to_dict()
                )
            
            response = create_error_response(
                "Failed to register doctor",
                "DATABASE_ERROR"
            )
            return JSONResponse(
                status_code=500,
                content=response.to_dict()
            )
    
    except Exception as e:
        logger.error(f"Unexpected error during registration", extra={
            "request_id": request_id,
            "error": str(e)
        }, exc_info=True)
        
        response = create_error_response(
            "Internal server error",
            "INTERNAL_ERROR"
        )
        return JSONResponse(
            status_code=500,
            content=response.to_dict()
        )


@router.get("/doctors/register/health")
async def registration_health():
    """Health check for registration endpoint."""
    response = create_success_response(
        data={
            "status": "healthy",
            "endpoint": "doctor_registration",
            "timestamp": datetime.utcnow().isoformat()
        }
    )
    return JSONResponse(content=response.to_dict())