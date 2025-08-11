"""
Profile management API endpoints.
"""

from fastapi import APIRouter, HTTPException, Request, Path, Header
from uuid import UUID
from typing import Optional
import logging

from ...services.profile_service import ProfileManagementService
from ...repositories.doctor_repository import DoctorRepository
from ...repositories.patient_repository import PatientRepository
from ...repositories.specialty_repository import MedicalSpecialtyRepository
from ...repositories.session_repository import UserSessionRepository
from ...requests.profile_update_requests import DoctorProfileUpdateRequest, PatientProfileUpdateRequest
from ...utils.logging_utils import get_logger
from ..models.api_models import BaseResponse, ProfileResponse

logger = get_logger(__name__)
router = APIRouter()

# Initialize service dependencies
# TODO: Replace with dependency injection
doctor_repository = DoctorRepository()
patient_repository = PatientRepository()
specialty_repository = MedicalSpecialtyRepository()
session_repository = UserSessionRepository()

profile_service = ProfileManagementService(
    doctor_repository,
    patient_repository,
    specialty_repository,
    session_repository
)


@router.get("/doctors/{doctor_id}/profile", response_model=ProfileResponse)
async def get_doctor_profile(
    request: Request,
    doctor_id: UUID = Path(..., description="Doctor ID"),
    x_session_id: Optional[str] = Header(None, alias="X-Session-ID")
):
    """Get doctor profile."""
    request_id = getattr(request.state, 'request_id', 'unknown')
    
    logger.info(f"Get doctor profile request", extra={"request_id": request_id})
    
    try:
        # For now, we'll skip session validation since authentication is disabled
        # In the future, validate x_session_id here
        
        result = profile_service.get_doctor_profile(doctor_id, x_session_id)
        
        if result.success:
            profile_data = result.data
            return ProfileResponse(
                success=True,
                message="Doctor profile retrieved",
                data={
                    "id": str(profile_data.id),
                    "name": profile_data.name,
                    "email": profile_data.email,
                    "phone": profile_data.phone,
                    "location": profile_data.location,
                    "specialties": [str(s) for s in profile_data.specialties],
                    "experience": profile_data.experience,
                    "rating": profile_data.rating,
                    "status": profile_data.status.value if hasattr(profile_data.status, 'value') else str(profile_data.status)
                },
                request_id=request_id
            )
        else:
            status_code = 404 if "not found" in result.error_message.lower() else 401
            raise HTTPException(status_code=status_code, detail=result.error_message)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get doctor profile failed: {str(e)}", extra={"request_id": request_id})
        raise HTTPException(status_code=500, detail="Failed to get doctor profile")


@router.put("/doctors/{doctor_id}/profile", response_model=ProfileResponse)
async def update_doctor_profile(
    request: Request,
    profile_data: DoctorProfileUpdateRequest,
    doctor_id: UUID = Path(..., description="Doctor ID"),
    x_session_id: Optional[str] = Header(None, alias="X-Session-ID")
):
    """Update doctor profile."""
    request_id = getattr(request.state, 'request_id', 'unknown')
    
    logger.info(f"Update doctor profile request", extra={"request_id": request_id})
    
    try:
        # For now, we'll skip session validation since authentication is disabled
        # In the future, validate x_session_id here
        
        result = profile_service.update_doctor_profile(doctor_id, profile_data, x_session_id)
        
        if result.success:
            return ProfileResponse(
                success=True,
                message="Doctor profile updated successfully",
                data={
                    "user_id": str(result.data.user_id),
                    "updated_fields": result.data.updated_fields,
                    "message": result.data.message
                },
                request_id=request_id
            )
        else:
            status_code = 404 if "not found" in result.error_message.lower() else 400
            raise HTTPException(status_code=status_code, detail=result.error_message)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update doctor profile failed: {str(e)}", extra={"request_id": request_id})
        raise HTTPException(status_code=500, detail="Failed to update doctor profile")


@router.get("/patients/{patient_id}/profile", response_model=ProfileResponse)
async def get_patient_profile(
    request: Request,
    patient_id: UUID = Path(..., description="Patient ID"),
    x_session_id: Optional[str] = Header(None, alias="X-Session-ID")
):
    """Get patient profile."""
    request_id = getattr(request.state, 'request_id', 'unknown')
    
    logger.info(f"Get patient profile request", extra={"request_id": request_id})
    
    try:
        # For now, we'll skip session validation since authentication is disabled
        # In the future, validate x_session_id here
        
        result = profile_service.get_patient_profile(patient_id, x_session_id)
        
        if result.success:
            profile_data = result.data
            return ProfileResponse(
                success=True,
                message="Patient profile retrieved",
                data={
                    "id": str(profile_data.id),
                    "name": profile_data.name,
                    "email": profile_data.email,
                    "phone": profile_data.phone,
                    "medical_history": profile_data.medical_history,
                    "emergency_contact": profile_data.emergency_contact,
                    "status": profile_data.status.value if hasattr(profile_data.status, 'value') else str(profile_data.status)
                },
                request_id=request_id
            )
        else:
            status_code = 404 if "not found" in result.error_message.lower() else 401
            raise HTTPException(status_code=status_code, detail=result.error_message)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get patient profile failed: {str(e)}", extra={"request_id": request_id})
        raise HTTPException(status_code=500, detail="Failed to get patient profile")


@router.put("/patients/{patient_id}/profile", response_model=ProfileResponse)
async def update_patient_profile(
    request: Request,
    profile_data: PatientProfileUpdateRequest,
    patient_id: UUID = Path(..., description="Patient ID"),
    x_session_id: Optional[str] = Header(None, alias="X-Session-ID")
):
    """Update patient profile."""
    request_id = getattr(request.state, 'request_id', 'unknown')
    
    logger.info(f"Update patient profile request", extra={"request_id": request_id})
    
    try:
        # For now, we'll skip session validation since authentication is disabled
        # In the future, validate x_session_id here
        
        result = profile_service.update_patient_profile(patient_id, profile_data, x_session_id)
        
        if result.success:
            return ProfileResponse(
                success=True,
                message="Patient profile updated successfully",
                data={
                    "user_id": str(result.data.user_id),
                    "updated_fields": result.data.updated_fields,
                    "message": result.data.message
                },
                request_id=request_id
            )
        else:
            status_code = 404 if "not found" in result.error_message.lower() else 400
            raise HTTPException(status_code=status_code, detail=result.error_message)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update patient profile failed: {str(e)}", extra={"request_id": request_id})
        raise HTTPException(status_code=500, detail="Failed to update patient profile")