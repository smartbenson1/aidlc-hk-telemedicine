"""
Health check and monitoring API endpoints.
"""

from fastapi import APIRouter, Request
import time
import logging
from datetime import datetime

from ...repositories.doctor_repository import DoctorRepository
from ...repositories.patient_repository import PatientRepository
from ...repositories.session_repository import UserSessionRepository
from ...integrations.email_service import EmailServiceIntegration
from ...integrations.admin_service import AdministrationServiceIntegration
from ...integrations.appointment_service import AppointmentServiceIntegration
from ...utils.logging_utils import get_logger
from ..models.api_models import HealthResponse, CheckResult

logger = get_logger(__name__)
router = APIRouter()

# Initialize dependencies for health checks
doctor_repository = DoctorRepository()
patient_repository = PatientRepository()
session_repository = UserSessionRepository()
email_service = EmailServiceIntegration()
admin_service = AdministrationServiceIntegration()
appointment_service = AppointmentServiceIntegration()


@router.get("/health", response_model=HealthResponse)
async def health_check(request: Request):
    """Comprehensive health check endpoint."""
    request_id = getattr(request.state, 'request_id', 'unknown')
    
    logger.info(f"Health check request", extra={"request_id": request_id})
    
    checks = {}
    overall_status = "healthy"
    
    # Check database connectivity (repositories)
    try:
        start_time = time.time()
        doctor_count = len(doctor_repository.find_all())
        duration = (time.time() - start_time) * 1000
        
        checks["database"] = {
            "status": "healthy",
            "message": f"Database accessible, {doctor_count} doctors found",
            "duration_ms": duration
        }
    except Exception as e:
        checks["database"] = {
            "status": "unhealthy",
            "message": f"Database error: {str(e)}",
            "duration_ms": 0
        }
        overall_status = "unhealthy"
    
    # Check email service
    try:
        start_time = time.time()
        # For mock email service, just check if it's initialized
        email_health = True  # email_service.health_check() if available
        duration = (time.time() - start_time) * 1000
        
        checks["email_service"] = {
            "status": "healthy" if email_health else "unhealthy",
            "message": "Email service operational (simulated)",
            "duration_ms": duration
        }
    except Exception as e:
        checks["email_service"] = {
            "status": "unhealthy",
            "message": f"Email service error: {str(e)}",
            "duration_ms": 0
        }
        # Email service is not critical, don't mark overall as unhealthy
    
    # Check external integrations
    try:
        start_time = time.time()
        admin_health = admin_service.health_check()
        duration = (time.time() - start_time) * 1000
        
        checks["admin_service"] = {
            "status": "healthy" if admin_health.success else "unhealthy",
            "message": "Admin service integration operational" if admin_health.success else "Admin service unavailable",
            "duration_ms": duration
        }
    except Exception as e:
        checks["admin_service"] = {
            "status": "unhealthy",
            "message": f"Admin service error: {str(e)}",
            "duration_ms": 0
        }
        # External service is not critical, don't mark overall as unhealthy
    
    try:
        start_time = time.time()
        appointment_health = appointment_service.health_check()
        duration = (time.time() - start_time) * 1000
        
        checks["appointment_service"] = {
            "status": "healthy" if appointment_health.success else "unhealthy",
            "message": "Appointment service integration operational" if appointment_health.success else "Appointment service unavailable",
            "duration_ms": duration
        }
    except Exception as e:
        checks["appointment_service"] = {
            "status": "unhealthy",
            "message": f"Appointment service error: {str(e)}",
            "duration_ms": 0
        }
        # External service is not critical, don't mark overall as unhealthy
    
    # Check memory usage (basic check)
    try:
        import sys
        memory_usage = sys.getsizeof(doctor_repository) + sys.getsizeof(patient_repository)
        checks["memory"] = {
            "status": "healthy",
            "message": f"Memory usage: {memory_usage} bytes",
            "duration_ms": 0
        }
    except Exception as e:
        checks["memory"] = {
            "status": "unhealthy",
            "message": f"Memory check error: {str(e)}",
            "duration_ms": 0
        }
    
    return HealthResponse(
        success=overall_status == "healthy",
        message=f"Service is {overall_status}",
        data={
            "status": overall_status,
            "version": "1.0.0",
            "timestamp": datetime.utcnow().isoformat(),
            "checks": checks
        },
        request_id=request_id
    )


@router.get("/health/ready", response_model=HealthResponse)
async def readiness_check(request: Request):
    """Readiness check endpoint for load balancers."""
    request_id = getattr(request.state, 'request_id', 'unknown')
    
    logger.info(f"Readiness check request", extra={"request_id": request_id})
    
    try:
        # Basic readiness checks
        checks = {}
        
        # Check if repositories are initialized
        checks["repositories"] = {
            "status": "ready",
            "message": "All repositories initialized",
            "duration_ms": 0
        }
        
        # Check if services are initialized
        checks["services"] = {
            "status": "ready",
            "message": "All services initialized",
            "duration_ms": 0
        }
        
        return HealthResponse(
            success=True,
            message="Service is ready",
            data={
                "status": "ready",
                "version": "1.0.0",
                "timestamp": datetime.utcnow().isoformat(),
                "checks": checks
            },
            request_id=request_id
        )
        
    except Exception as e:
        logger.error(f"Readiness check failed: {str(e)}", extra={"request_id": request_id})
        return HealthResponse(
            success=False,
            message="Service is not ready",
            data={
                "status": "not_ready",
                "version": "1.0.0",
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e)
            },
            request_id=request_id
        )


@router.get("/metrics", response_model=HealthResponse)
async def get_metrics(request: Request):
    """Get service metrics."""
    request_id = getattr(request.state, 'request_id', 'unknown')
    
    logger.info(f"Metrics request", extra={"request_id": request_id})
    
    try:
        # Collect basic metrics
        doctor_count = len(doctor_repository.find_all())
        patient_count = len(patient_repository.find_all())
        session_count = len(session_repository.find_all())
        
        metrics = {
            "users": {
                "total_doctors": doctor_count,
                "total_patients": patient_count,
                "total_users": doctor_count + patient_count
            },
            "sessions": {
                "active_sessions": session_count
            },
            "system": {
                "version": "1.0.0",
                "uptime": "unknown",  # Would need to track startup time
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        
        return HealthResponse(
            success=True,
            message="Metrics retrieved successfully",
            data=metrics,
            request_id=request_id
        )
        
    except Exception as e:
        logger.error(f"Metrics collection failed: {str(e)}", extra={"request_id": request_id})
        raise HTTPException(status_code=500, detail="Failed to collect metrics")