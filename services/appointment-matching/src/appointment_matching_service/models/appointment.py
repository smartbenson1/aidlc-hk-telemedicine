"""
Appointment model class for the Appointment Matching Service.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from ..utils.enums import AppointmentStatus, AppointmentType
from ..utils.helpers import (
    generate_uuid, get_current_utc_datetime, validate_booking_window, 
    validate_string_length
)
from ..utils.exceptions import ValidationError


@dataclass
class Appointment:
    """Appointment component."""
    
    # Identity
    id: str = field(default_factory=generate_uuid)
    patient_id: str = ""
    doctor_id: str = ""
    availability_id: str = ""
    
    # Appointment Details
    datetime: Optional[datetime] = None
    appointment_type: AppointmentType = AppointmentType.IN_PERSON
    symptoms: str = ""
    
    # Status Management
    status: AppointmentStatus = AppointmentStatus.SCHEDULED
    reschedule_reason: Optional[str] = None
    reschedule_count: int = 0
    
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
        """Validate the appointment data."""
        errors = []
        
        # Validate required fields
        if not self.patient_id:
            errors.append("Patient ID is required")
        
        if not self.doctor_id:
            errors.append("Doctor ID is required")
        
        if not self.availability_id:
            errors.append("Availability ID is required")
        
        if not self.datetime:
            errors.append("DateTime is required")
        elif not validate_booking_window(self.datetime):
            errors.append("DateTime must be within the booking window")
        
        if not self.symptoms:
            errors.append("Symptoms are required")
        elif not validate_string_length(self.symptoms, 2000, 1):
            errors.append("Symptoms must be between 1 and 2000 characters")
        
        # Validate reschedule reason if provided
        if self.reschedule_reason and not validate_string_length(self.reschedule_reason, 500):
            errors.append("Reschedule reason must be at most 500 characters")
        
        # Validate reschedule count
        if self.reschedule_count < 0 or self.reschedule_count > 2:
            errors.append("Reschedule count must be between 0 and 2")
        
        if errors:
            raise ValidationError(f"Appointment validation failed: {'; '.join(errors)}")
        
        return True
    
    def validate_booking_window(self, dt: datetime) -> bool:
        """Validate datetime is within booking window."""
        return validate_booking_window(dt)
    
    def validate_reschedule_limit(self, reschedule_count: int) -> bool:
        """Validate reschedule count is within limit."""
        return 0 <= reschedule_count <= 2
    
    def validate_symptoms(self, symptoms: str) -> bool:
        """Validate symptoms text."""
        return validate_string_length(symptoms, 2000, 1)
    
    def is_scheduled(self) -> bool:
        """Check if appointment is scheduled."""
        return self.status == AppointmentStatus.SCHEDULED
    
    def is_completed(self) -> bool:
        """Check if appointment is completed."""
        return self.status == AppointmentStatus.COMPLETED
    
    def is_cancelled(self) -> bool:
        """Check if appointment is cancelled."""
        return self.status == AppointmentStatus.CANCELLED
    
    def is_rescheduled(self) -> bool:
        """Check if appointment is rescheduled."""
        return self.status == AppointmentStatus.RESCHEDULED
    
    def is_no_show(self) -> bool:
        """Check if appointment is marked as no show."""
        return self.status == AppointmentStatus.NO_SHOW
    
    def can_reschedule(self) -> bool:
        """Check if appointment can be rescheduled."""
        return (self.is_scheduled() and 
                self.reschedule_count < 2 and 
                self.datetime and 
                self.datetime > get_current_utc_datetime())
    
    def complete(self) -> None:
        """Mark appointment as completed."""
        if not self.is_scheduled():
            raise ValidationError("Only scheduled appointments can be completed")
        
        self.status = AppointmentStatus.COMPLETED
        self.updated_at = get_current_utc_datetime()
    
    def cancel(self, reason: Optional[str] = None) -> None:
        """Cancel the appointment."""
        if self.is_completed():
            raise ValidationError("Cannot cancel a completed appointment")
        
        self.status = AppointmentStatus.CANCELLED
        if reason:
            self.reschedule_reason = reason
        self.updated_at = get_current_utc_datetime()
    
    def reschedule(self, new_datetime: datetime, reason: str) -> None:
        """Reschedule the appointment."""
        if not self.can_reschedule():
            raise ValidationError("Appointment cannot be rescheduled")
        
        if not validate_booking_window(new_datetime):
            raise ValidationError("New datetime must be within booking window")
        
        if not validate_string_length(reason, 500, 1):
            raise ValidationError("Reschedule reason is required and must be at most 500 characters")
        
        self.datetime = new_datetime
        self.reschedule_reason = reason
        self.reschedule_count += 1
        self.status = AppointmentStatus.RESCHEDULED
        self.updated_at = get_current_utc_datetime()
    
    def mark_no_show(self) -> None:
        """Mark appointment as no show."""
        if not self.is_scheduled():
            raise ValidationError("Only scheduled appointments can be marked as no show")
        
        self.status = AppointmentStatus.NO_SHOW
        self.updated_at = get_current_utc_datetime()
    
    def update_symptoms(self, symptoms: str) -> None:
        """Update appointment symptoms."""
        if not self.validate_symptoms(symptoms):
            raise ValidationError("Invalid symptoms")
        
        self.symptoms = symptoms
        self.updated_at = get_current_utc_datetime()
    
    def __str__(self) -> str:
        """String representation of the appointment."""
        return f"Appointment {self.id} - {self.datetime} ({self.status.value})"
    
    def __repr__(self) -> str:
        """Detailed representation of the appointment."""
        return (f"Appointment(id='{self.id}', patient_id='{self.patient_id}', "
                f"doctor_id='{self.doctor_id}', datetime={self.datetime}, "
                f"status={self.status.value})")