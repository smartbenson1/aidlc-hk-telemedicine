"""
Doctor Availability model class for the Appointment Matching Service.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from ..utils.enums import AvailabilityStatus, AppointmentType
from ..utils.helpers import (
    generate_uuid, get_current_utc_datetime, validate_future_datetime, 
    validate_booking_window
)
from ..utils.exceptions import ValidationError


@dataclass
class DoctorAvailability:
    """Doctor availability component."""
    
    # Identity
    id: str = field(default_factory=generate_uuid)
    doctor_id: str = ""
    
    # Scheduling Information
    datetime: Optional[datetime] = None
    appointment_type: AppointmentType = AppointmentType.IN_PERSON
    specialty_id: Optional[str] = None
    
    # Status Management
    status: AvailabilityStatus = AvailabilityStatus.AVAILABLE
    
    # System Fields
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    
    def __post_init__(self):
        """Initialize timestamps if not provided."""
        if self.created_at is None:
            self.created_at = get_current_utc_datetime()
        if self.updated_at is None:
            self.updated_at = get_current_utc_datetime()
    
    def validate(self) -> bool:
        """Validate the doctor availability data."""
        errors = []
        
        # Validate required fields
        if not self.doctor_id:
            errors.append("Doctor ID is required")
        
        if not self.datetime:
            errors.append("DateTime is required")
        elif not validate_future_datetime(self.datetime):
            errors.append("DateTime must be in the future")
        elif not validate_booking_window(self.datetime):
            errors.append("DateTime must be within the booking window (30 days)")
        
        if errors:
            raise ValidationError(f"Doctor availability validation failed: {'; '.join(errors)}")
        
        return True
    
    def validate_datetime(self, dt: datetime) -> bool:
        """Validate datetime is in future and within booking window."""
        return validate_future_datetime(dt) and validate_booking_window(dt)
    
    def validate_specialty(self, specialty_id: str) -> bool:
        """Validate specialty ID format."""
        return isinstance(specialty_id, str) and len(specialty_id) == 36
    
    def validate_booking_window(self, dt: datetime) -> bool:
        """Validate datetime is within booking window."""
        return validate_booking_window(dt)
    
    def is_available(self) -> bool:
        """Check if the slot is available."""
        return self.status == AvailabilityStatus.AVAILABLE
    
    def is_booked(self) -> bool:
        """Check if the slot is booked."""
        return self.status == AvailabilityStatus.BOOKED
    
    def is_blocked(self) -> bool:
        """Check if the slot is blocked."""
        return self.status == AvailabilityStatus.BLOCKED
    
    def book(self) -> None:
        """Mark the slot as booked."""
        if not self.is_available():
            raise ValidationError("Cannot book a slot that is not available")
        
        self.status = AvailabilityStatus.BOOKED
        self.updated_at = get_current_utc_datetime()
    
    def unbook(self) -> None:
        """Mark the slot as available again."""
        if not self.is_booked():
            raise ValidationError("Cannot unbook a slot that is not booked")
        
        self.status = AvailabilityStatus.AVAILABLE
        self.updated_at = get_current_utc_datetime()
    
    def block(self) -> None:
        """Block the slot."""
        self.status = AvailabilityStatus.BLOCKED
        self.updated_at = get_current_utc_datetime()
    
    def unblock(self) -> None:
        """Unblock the slot."""
        if self.is_blocked():
            self.status = AvailabilityStatus.AVAILABLE
            self.updated_at = get_current_utc_datetime()
    
    def update_datetime(self, new_datetime: datetime) -> None:
        """Update the availability datetime."""
        if not self.validate_datetime(new_datetime):
            raise ValidationError("Invalid datetime for availability")
        
        self.datetime = new_datetime
        self.updated_at = get_current_utc_datetime()
    
    def update_appointment_type(self, appointment_type: AppointmentType) -> None:
        """Update the appointment type."""
        self.appointment_type = appointment_type
        self.updated_at = get_current_utc_datetime()
    
    def update_specialty(self, specialty_id: str) -> None:
        """Update the specialty for this availability."""
        if not self.validate_specialty(specialty_id):
            raise ValidationError("Invalid specialty ID")
        
        self.specialty_id = specialty_id
        self.updated_at = get_current_utc_datetime()
    
    def __str__(self) -> str:
        """String representation of the availability."""
        return f"Availability for {self.doctor_id} on {self.datetime} ({self.status.value})"
    
    def __repr__(self) -> str:
        """Detailed representation of the availability."""
        return (f"DoctorAvailability(id='{self.id}', doctor_id='{self.doctor_id}', "
                f"datetime={self.datetime}, status={self.status.value})")