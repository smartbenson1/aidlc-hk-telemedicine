"""
Response models and result classes for the User Management Service.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID

from ..utils.enums import UserStatus, UserType, AppointmentType, AvailabilityStatus


@dataclass
class DoctorProfileView:
    """View model for doctor profile information."""
    
    id: UUID
    name: str
    email: str
    phone: str
    location: str
    specialties: List[Dict[str, str]]  # [{"id": "uuid", "name": "Cardiology"}]
    experience: str
    rating: float
    status: UserStatus
    created_at: datetime
    updated_at: datetime
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            'id': str(self.id),
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'location': self.location,
            'specialties': self.specialties,
            'experience': self.experience,
            'rating': self.rating,
            'status': self.status.value,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


@dataclass
class PatientProfileView:
    """View model for patient profile information."""
    
    id: UUID
    name: str
    email: str
    phone: str
    medical_history: str
    emergency_contact: Dict[str, str]  # {"name": "", "phone": "", "relationship": ""}
    status: UserStatus
    created_at: datetime
    updated_at: datetime
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            'id': str(self.id),
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'medical_history': self.medical_history,
            'emergency_contact': self.emergency_contact,
            'status': self.status.value,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


@dataclass
class AvailableSlotResponse:
    """Response model for available appointment slots."""
    
    id: UUID
    doctor_id: UUID
    datetime: datetime
    appointment_type: AppointmentType
    specialty: Dict[str, str]  # {"id": "uuid", "name": "Cardiology"}
    duration_hours: int = 1
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            'id': str(self.id),
            'doctor_id': str(self.doctor_id),
            'datetime': self.datetime.isoformat(),
            'appointment_type': self.appointment_type.value,
            'specialty': self.specialty,
            'duration_hours': self.duration_hours
        }


@dataclass
class DoctorAvailabilityResponse:
    """Response model for doctor availability information."""
    
    id: UUID
    doctor_id: UUID
    datetime: datetime
    appointment_type: AppointmentType
    specialty: Dict[str, str]
    status: AvailabilityStatus
    created_at: datetime
    updated_at: datetime
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            'id': str(self.id),
            'doctor_id': str(self.doctor_id),
            'datetime': self.datetime.isoformat(),
            'appointment_type': self.appointment_type.value,
            'specialty': self.specialty,
            'status': self.status.value,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


@dataclass
class DoctorSearchResult:
    """Response model for doctor search results."""
    
    id: UUID
    name: str
    location: str
    specialties: List[Dict[str, str]]
    rating: float
    available_slots_count: int = 0
    next_available_slot: Optional[datetime] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            'id': str(self.id),
            'name': self.name,
            'location': self.location,
            'specialties': self.specialties,
            'rating': self.rating,
            'available_slots_count': self.available_slots_count,
            'next_available_slot': self.next_available_slot.isoformat() if self.next_available_slot else None
        }


@dataclass
class PatientBasicInfoResponse:
    """Response model for basic patient information."""
    
    id: UUID
    name: str
    email: str
    phone: str
    status: UserStatus
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            'id': str(self.id),
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'status': self.status.value
        }


@dataclass
class UserVerificationResponse:
    """Response model for user verification."""
    
    exists: bool
    user_id: Optional[UUID] = None
    user_type: Optional[UserType] = None
    name: Optional[str] = None
    email: Optional[str] = None
    status: Optional[UserStatus] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            'exists': self.exists,
            'user_id': str(self.user_id) if self.user_id else None,
            'user_type': self.user_type.value if self.user_type else None,
            'name': self.name,
            'email': self.email,
            'status': self.status.value if self.status else None
        }


@dataclass
class SessionResponse:
    """Response model for session operations."""
    
    session_id: UUID
    user_id: UUID
    user_type: UserType
    expires_at: datetime
    created_at: datetime
    last_accessed: datetime
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            'session_id': str(self.session_id),
            'user_id': str(self.user_id),
            'user_type': self.user_type.value,
            'expires_at': self.expires_at.isoformat(),
            'created_at': self.created_at.isoformat(),
            'last_accessed': self.last_accessed.isoformat()
        }


@dataclass
class UserContextResponse:
    """Response model for user context from session."""
    
    user_id: UUID
    user_type: UserType
    name: str
    email: str
    permissions: List[str]
    preferences: Dict[str, str]
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            'user_id': str(self.user_id),
            'user_type': self.user_type.value,
            'name': self.name,
            'email': self.email,
            'permissions': self.permissions,
            'preferences': self.preferences
        }


@dataclass
class EmailValidationResponse:
    """Response model for email validation."""
    
    email: str
    is_available: bool
    message: str
    suggestions: List[str] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            'email': self.email,
            'is_available': self.is_available,
            'message': self.message,
            'suggestions': self.suggestions
        }


@dataclass
class SuccessResponse:
    """Generic success response."""
    
    success: bool = True
    message: str = "Operation completed successfully"
    data: Optional[Dict[str, Any]] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            'success': self.success,
            'message': self.message,
            'data': self.data,
            'timestamp': self.timestamp.isoformat()
        }


@dataclass
class ErrorResponse:
    """Generic error response."""
    
    success: bool = False
    error_code: str = "UNKNOWN_ERROR"
    message: str = "An error occurred"
    details: Optional[Dict[str, Any]] = None
    errors: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            'success': self.success,
            'error_code': self.error_code,
            'message': self.message,
            'details': self.details,
            'errors': self.errors,
            'timestamp': self.timestamp.isoformat()
        }


@dataclass
class PaginatedResponse:
    """Generic paginated response."""
    
    items: List[Dict[str, Any]]
    total_count: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_previous: bool
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            'items': self.items,
            'total_count': self.total_count,
            'page': self.page,
            'page_size': self.page_size,
            'total_pages': self.total_pages,
            'has_next': self.has_next,
            'has_previous': self.has_previous
        }
    
    @classmethod
    def create(cls, items: List[Any], total_count: int, page: int, page_size: int) -> 'PaginatedResponse':
        """Create a paginated response."""
        total_pages = (total_count + page_size - 1) // page_size
        has_next = page < total_pages
        has_previous = page > 1
        
        # Convert items to dict if they have to_dict method
        dict_items = []
        for item in items:
            if hasattr(item, 'to_dict'):
                dict_items.append(item.to_dict())
            else:
                dict_items.append(item)
        
        return cls(
            items=dict_items,
            total_count=total_count,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            has_next=has_next,
            has_previous=has_previous
        )