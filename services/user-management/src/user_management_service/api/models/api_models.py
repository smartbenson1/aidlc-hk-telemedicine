"""
FastAPI request/response models.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID


class BaseResponse(BaseModel):
    """Base response model for all API responses."""
    success: bool
    message: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    request_id: str


class ErrorResponse(BaseResponse):
    """Error response model."""
    error_code: str
    details: Optional[Dict[str, Any]] = None


class RegistrationResponse(BaseResponse):
    """Registration response model."""
    data: Dict[str, Any]


class EmailAvailabilityResponse(BaseResponse):
    """Email availability response model."""
    data: Dict[str, Any]


class StatisticsResponse(BaseResponse):
    """Statistics response model."""
    data: Dict[str, Any]


class SessionResponse(BaseResponse):
    """Session response model."""
    data: Dict[str, Any]


class ProfileResponse(BaseResponse):
    """Profile response model."""
    data: Dict[str, Any]


class AvailabilityResponse(BaseResponse):
    """Availability response model."""
    data: Dict[str, Any]


class SpecialtyResponse(BaseResponse):
    """Specialty response model."""
    data: Dict[str, Any]


class HealthResponse(BaseResponse):
    """Health check response model."""
    data: Dict[str, Any]


# Request Models
class SessionCreateRequest(BaseModel):
    """Session creation request model."""
    user_id: UUID
    user_type: str = Field(..., regex="^(doctor|patient)$")
    ip_address: str
    user_agent: str


class AvailabilityQueryRequest(BaseModel):
    """Availability query request model."""
    doctor_id: Optional[UUID] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    appointment_type: Optional[str] = None
    specialty_id: Optional[UUID] = None


# Health Check Models
class HealthStatus(BaseModel):
    """Health status model."""
    status: str
    version: str
    timestamp: datetime
    checks: Dict[str, Any]


class CheckResult(BaseModel):
    """Individual health check result."""
    status: str
    message: str
    duration_ms: float


# Pagination Models
class PaginationInfo(BaseModel):
    """Pagination information."""
    page: int
    page_size: int
    total_items: int
    total_pages: int


class PaginatedResponse(BaseResponse):
    """Paginated response model."""
    data: List[Any]
    pagination: PaginationInfo