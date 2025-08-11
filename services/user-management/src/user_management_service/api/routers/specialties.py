"""
Medical specialties API endpoints.
"""

from fastapi import APIRouter, HTTPException, Request, Path
from uuid import UUID
import logging

from ...repositories.specialty_repository import MedicalSpecialtyRepository
from ...utils.logging_utils import get_logger
from ..models.api_models import BaseResponse, SpecialtyResponse

logger = get_logger(__name__)
router = APIRouter()

# Initialize service dependencies
# TODO: Replace with dependency injection
specialty_repository = MedicalSpecialtyRepository()


@router.get("/specialties", response_model=SpecialtyResponse)
async def get_all_specialties(request: Request):
    """Get all medical specialties."""
    request_id = getattr(request.state, 'request_id', 'unknown')
    
    logger.info(f"Get all specialties request", extra={"request_id": request_id})
    
    try:
        specialties = specialty_repository.find_all()
        
        specialties_data = []
        for specialty in specialties:
            specialties_data.append({
                "id": str(specialty.id),
                "name": specialty.name,
                "description": specialty.description,
                "status": specialty.status.value if hasattr(specialty.status, 'value') else str(specialty.status),
                "created_at": specialty.created_at.isoformat(),
                "updated_at": specialty.updated_at.isoformat()
            })
        
        return SpecialtyResponse(
            success=True,
            message="Medical specialties retrieved successfully",
            data={
                "specialties": specialties_data,
                "total_count": len(specialties_data)
            },
            request_id=request_id
        )
        
    except Exception as e:
        logger.error(f"Get all specialties failed: {str(e)}", extra={"request_id": request_id})
        raise HTTPException(status_code=500, detail="Failed to get medical specialties")


@router.get("/specialties/{specialty_id}", response_model=SpecialtyResponse)
async def get_specialty(
    request: Request,
    specialty_id: UUID = Path(..., description="Specialty ID")
):
    """Get a specific medical specialty."""
    request_id = getattr(request.state, 'request_id', 'unknown')
    
    logger.info(f"Get specialty request", extra={"request_id": request_id})
    
    try:
        specialty = specialty_repository.find_by_id(specialty_id)
        
        if specialty:
            return SpecialtyResponse(
                success=True,
                message="Medical specialty retrieved successfully",
                data={
                    "id": str(specialty.id),
                    "name": specialty.name,
                    "description": specialty.description,
                    "status": specialty.status.value if hasattr(specialty.status, 'value') else str(specialty.status),
                    "created_at": specialty.created_at.isoformat(),
                    "updated_at": specialty.updated_at.isoformat()
                },
                request_id=request_id
            )
        else:
            raise HTTPException(status_code=404, detail="Medical specialty not found")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get specialty failed: {str(e)}", extra={"request_id": request_id})
        raise HTTPException(status_code=500, detail="Failed to get medical specialty")