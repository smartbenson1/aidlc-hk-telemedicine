"""
Session management API endpoints.
"""

from fastapi import APIRouter, HTTPException, Request, Path
from uuid import UUID
import logging

from ...services.session_service import UserSessionManager
from ...repositories.session_repository import UserSessionRepository
from ...repositories.doctor_repository import DoctorRepository
from ...repositories.patient_repository import PatientRepository
from ...utils.logging_utils import get_logger
from ..models.api_models import (
    BaseResponse,
    SessionResponse,
    SessionCreateRequest,
    StatisticsResponse
)

logger = get_logger(__name__)
router = APIRouter()

# Initialize service dependencies
# TODO: Replace with dependency injection
session_repository = UserSessionRepository()
doctor_repository = DoctorRepository()
patient_repository = PatientRepository()

session_manager = UserSessionManager(
    session_repository,
    doctor_repository,
    patient_repository
)


@router.post("/sessions", response_model=SessionResponse, status_code=201)
async def create_session(request: Request, session_data: SessionCreateRequest):
    """Create a new user session."""
    request_id = getattr(request.state, 'request_id', 'unknown')
    
    logger.info(f"Session creation request", extra={"request_id": request_id})
    
    try:
        result = session_manager.create_session(
            session_data.user_id,
            session_data.user_type,
            session_data.ip_address,
            session_data.user_agent
        )
        
        if result.success:
            return SessionResponse(
                success=True,
                message="Session created successfully",
                data={
                    "session_id": str(result.data.session_id),
                    "user_id": str(result.data.user_id),
                    "user_type": result.data.user_type,
                    "expires_at": result.data.expires_at.isoformat()
                },
                request_id=request_id
            )
        else:
            raise HTTPException(
                status_code=400 if result.error_code == "VALIDATION_ERROR" else 404,
                detail=result.error_message
            )
            
    except Exception as e:
        logger.error(f"Session creation failed: {str(e)}", extra={"request_id": request_id})
        raise HTTPException(status_code=500, detail="Session creation failed")


@router.get("/sessions/{session_id}", response_model=SessionResponse)
async def validate_session(
    request: Request,
    session_id: UUID = Path(..., description="Session ID to validate")
):
    """Validate a session."""
    request_id = getattr(request.state, 'request_id', 'unknown')
    
    logger.info(f"Session validation request", extra={"request_id": request_id})
    
    try:
        result = session_manager.validate_session(session_id)
        
        if result.success:
            return SessionResponse(
                success=True,
                message="Session is valid",
                data={
                    "session_id": str(session_id),
                    "is_valid": result.data.is_valid,
                    "user_id": str(result.data.user_id) if result.data.user_id else None,
                    "user_type": result.data.user_type,
                    "expires_at": result.data.expires_at.isoformat() if result.data.expires_at else None
                },
                request_id=request_id
            )
        else:
            raise HTTPException(status_code=404, detail="Session not found")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Session validation failed: {str(e)}", extra={"request_id": request_id})
        raise HTTPException(status_code=500, detail="Session validation failed")


@router.put("/sessions/{session_id}/refresh", response_model=SessionResponse)
async def refresh_session(
    request: Request,
    session_id: UUID = Path(..., description="Session ID to refresh")
):
    """Refresh a session."""
    request_id = getattr(request.state, 'request_id', 'unknown')
    
    logger.info(f"Session refresh request", extra={"request_id": request_id})
    
    try:
        result = session_manager.refresh_session(session_id)
        
        if result.success:
            return SessionResponse(
                success=True,
                message="Session refreshed successfully",
                data={
                    "session_id": str(result.data.session_id),
                    "user_id": str(result.data.user_id),
                    "user_type": result.data.user_type,
                    "expires_at": result.data.expires_at.isoformat()
                },
                request_id=request_id
            )
        else:
            raise HTTPException(status_code=404, detail="Session not found")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Session refresh failed: {str(e)}", extra={"request_id": request_id})
        raise HTTPException(status_code=500, detail="Session refresh failed")


@router.delete("/sessions/{session_id}", response_model=BaseResponse)
async def terminate_session(
    request: Request,
    session_id: UUID = Path(..., description="Session ID to terminate")
):
    """Terminate a session."""
    request_id = getattr(request.state, 'request_id', 'unknown')
    
    logger.info(f"Session termination request", extra={"request_id": request_id})
    
    try:
        result = session_manager.terminate_session(session_id)
        
        if result.success:
            return BaseResponse(
                success=True,
                message="Session terminated successfully",
                request_id=request_id
            )
        else:
            raise HTTPException(status_code=404, detail="Session not found")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Session termination failed: {str(e)}", extra={"request_id": request_id})
        raise HTTPException(status_code=500, detail="Session termination failed")


@router.get("/sessions/{session_id}/context", response_model=SessionResponse)
async def get_user_context(
    request: Request,
    session_id: UUID = Path(..., description="Session ID to get context for")
):
    """Get user context from session."""
    request_id = getattr(request.state, 'request_id', 'unknown')
    
    logger.info(f"User context request", extra={"request_id": request_id})
    
    try:
        result = session_manager.get_user_context(session_id)
        
        if result.success:
            return SessionResponse(
                success=True,
                message="User context retrieved",
                data={
                    "session_id": str(session_id),
                    "user_id": str(result.data.user_id),
                    "user_type": result.data.user_type.value if hasattr(result.data.user_type, 'value') else str(result.data.user_type),
                    "is_active": result.data.is_active
                },
                request_id=request_id
            )
        else:
            raise HTTPException(status_code=404, detail="Session not found")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"User context retrieval failed: {str(e)}", extra={"request_id": request_id})
        raise HTTPException(status_code=500, detail="User context retrieval failed")


@router.get("/sessions/statistics", response_model=StatisticsResponse)
async def get_session_statistics(request: Request):
    """Get session statistics."""
    request_id = getattr(request.state, 'request_id', 'unknown')
    
    logger.info(f"Session statistics request", extra={"request_id": request_id})
    
    try:
        result = session_manager.get_session_statistics()
        
        if result.success:
            return StatisticsResponse(
                success=True,
                message="Session statistics retrieved",
                data=result.data,
                request_id=request_id
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to get statistics")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Session statistics failed: {str(e)}", extra={"request_id": request_id})
        raise HTTPException(status_code=500, detail="Failed to get session statistics")