"""
Registration API endpoints.
"""

from fastapi import APIRouter, HTTPException, Request, Query
from typing import Optional
import logging

from ...services.registration_service import UserRegistrationService
from ...repositories.doctor_repository import DoctorRepository
from ...repositories.patient_repository import PatientRepository
from ...repositories.specialty_repository import MedicalSpecialtyRepository
from ...integrations.email_service import EmailServiceIntegration
from ...requests.registration_requests import DoctorRegistrationRequest, PatientRegistrationRequest
from ...utils.logging_utils import get_logger
from ..models.api_models import (
    BaseResponse,
    RegistrationResponse,
    EmailAvailabilityResponse,
    StatisticsResponse
)

logger = get_logger(__name__)
router = APIRouter()

# Initialize service dependencies
# TODO: Replace with dependency injection
from ...database.dynamodb_doctor_repository import DynamoDBDoctorRepository
from ...database.dynamodb_client import get_dynamodb_client

# Use DynamoDB repositories instead of in-memory ones
dynamodb_client = get_dynamodb_client()
doctor_repository = DynamoDBDoctorRepository()
patient_repository = PatientRepository()  # TODO: Replace with DynamoDB version
specialty_repository = MedicalSpecialtyRepository()  # TODO: Replace with DynamoDB version
email_service = EmailServiceIntegration()

registration_service = UserRegistrationService(
    doctor_repository,
    patient_repository,
    specialty_repository,
    email_service
)


@router.post("/doctors/register", response_model=RegistrationResponse, status_code=201)
async def register_doctor(request: Request, doctor_data: DoctorRegistrationRequest):
    """Register a new doctor."""
    request_id = getattr(request.state, 'request_id', 'unknown')
    
    logger.info(f"Doctor registration request", extra={"request_id": request_id})
    
    try:
        result = registration_service.register_doctor(doctor_data)
        
        if result.success:
            return RegistrationResponse(
                success=True,
                message="Doctor registered successfully",
                data={
                    "user_id": str(result.data.user_id),
                    "email": result.data.email,
                    "user_type": result.data.user_type
                },
                request_id=request_id
            )
        else:
            raise HTTPException(
                status_code=400 if result.error_code == "VALIDATION_ERROR" else 409,
                detail=result.error_message
            )
            
    except Exception as e:
        logger.error(f"Doctor registration failed: {str(e)}", extra={"request_id": request_id})
        raise HTTPException(status_code=500, detail="Registration failed")


@router.post("/patients/register", response_model=RegistrationResponse, status_code=201)
async def register_patient(request: Request, patient_data: PatientRegistrationRequest):
    """Register a new patient."""
    request_id = getattr(request.state, 'request_id', 'unknown')
    
    logger.info(f"Patient registration request", extra={"request_id": request_id})
    
    try:
        result = registration_service.register_patient(patient_data)
        
        if result.success:
            return RegistrationResponse(
                success=True,
                message="Patient registered successfully",
                data={
                    "user_id": str(result.data.user_id),
                    "email": result.data.email,
                    "user_type": result.data.user_type
                },
                request_id=request_id
            )
        else:
            raise HTTPException(
                status_code=400 if result.error_code == "VALIDATION_ERROR" else 409,
                detail=result.error_message
            )
            
    except Exception as e:
        logger.error(f"Patient registration failed: {str(e)}", extra={"request_id": request_id})
        raise HTTPException(status_code=500, detail="Registration failed")


@router.get("/registration/email-availability", response_model=EmailAvailabilityResponse)
async def check_email_availability(
    request: Request,
    email: str = Query(..., description="Email address to check"),
    user_type: str = Query(..., description="User type: doctor or patient")
):
    """Check if email address is available for registration."""
    request_id = getattr(request.state, 'request_id', 'unknown')
    
    logger.info(f"Email availability check", extra={"request_id": request_id, "email": email})
    
    try:
        if user_type not in ["doctor", "patient"]:
            raise HTTPException(status_code=400, detail="user_type must be 'doctor' or 'patient'")
        
        result = registration_service.check_email_availability(email, user_type)
        
        return EmailAvailabilityResponse(
            success=True,
            message="Email availability checked",
            data={
                "email": email,
                "is_available": result.data,
                "user_type": user_type
            },
            request_id=request_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Email availability check failed: {str(e)}", extra={"request_id": request_id})
        raise HTTPException(status_code=500, detail="Email availability check failed")


@router.get("/registration/statistics", response_model=StatisticsResponse)
async def get_registration_statistics(request: Request):
    """Get registration statistics."""
    request_id = getattr(request.state, 'request_id', 'unknown')
    
    logger.info(f"Registration statistics request", extra={"request_id": request_id})
    
    try:
        result = registration_service.get_registration_statistics()
        
        if result.success:
            return StatisticsResponse(
                success=True,
                message="Registration statistics retrieved",
                data=result.data,
                request_id=request_id
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to get statistics")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration statistics failed: {str(e)}", extra={"request_id": request_id})
        raise HTTPException(status_code=500, detail="Failed to get registration statistics")