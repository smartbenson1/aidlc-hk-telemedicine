"""
Appointment Booking Event model class for the Appointment Matching Service.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from ..utils.enums import EventStatus
from ..utils.helpers import (
    generate_uuid, get_current_utc_datetime, validate_string_length
)
from ..utils.exceptions import ValidationError


@dataclass
class AppointmentBookingEvent:
    """Appointment booking event component."""
    
    # Event Identity
    event_id: str = field(default_factory=generate_uuid)
    event_type: str = "appointment_booked"
    
    # Appointment Information
    appointment_id: str = ""
    patient_id: str = ""
    doctor_id: str = ""
    datetime: Optional[datetime] = None
    symptoms: str = ""
    
    # Event Metadata
    timestamp: Optional[datetime] = None
    source_service: str = "appointment_matching_service"
    correlation_id: str = field(default_factory=generate_uuid)
    
    # Processing Status
    status: EventStatus = EventStatus.PENDING
    processed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    
    # System Fields
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Initialize timestamps if not provided."""
        if self.timestamp is None:
            self.timestamp = get_current_utc_datetime()
        if self.created_at is None:
            self.created_at = get_current_utc_datetime()
        if self.updated_at is None:
            self.updated_at = get_current_utc_datetime()
    
    def validate(self) -> bool:
        """Validate the event data."""
        errors = []
        
        # Validate required fields
        if not self.appointment_id:
            errors.append("Appointment ID is required")
        
        if not self.patient_id:
            errors.append("Patient ID is required")
        
        if not self.doctor_id:
            errors.append("Doctor ID is required")
        
        if not self.datetime:
            errors.append("DateTime is required")
        
        if not self.symptoms:
            errors.append("Symptoms are required")
        elif not validate_string_length(self.symptoms, 2000, 1):
            errors.append("Symptoms must be between 1 and 2000 characters")
        
        if not self.source_service:
            errors.append("Source service is required")
        
        # Validate error message if provided
        if self.error_message and not validate_string_length(self.error_message, 1000):
            errors.append("Error message must be at most 1000 characters")
        
        if errors:
            raise ValidationError(f"Appointment booking event validation failed: {'; '.join(errors)}")
        
        return True
    
    def is_pending(self) -> bool:
        """Check if event is pending."""
        return self.status == EventStatus.PENDING
    
    def is_processed(self) -> bool:
        """Check if event is processed."""
        return self.status == EventStatus.PROCESSED
    
    def is_failed(self) -> bool:
        """Check if event processing failed."""
        return self.status == EventStatus.FAILED
    
    def mark_processed(self) -> None:
        """Mark event as processed."""
        self.status = EventStatus.PROCESSED
        self.processed_at = get_current_utc_datetime()
        self.updated_at = get_current_utc_datetime()
        self.error_message = None
    
    def mark_failed(self, error_message: str) -> None:
        """Mark event as failed."""
        if not validate_string_length(error_message, 1000, 1):
            raise ValidationError("Error message is required and must be at most 1000 characters")
        
        self.status = EventStatus.FAILED
        self.error_message = error_message
        self.updated_at = get_current_utc_datetime()
    
    def retry(self) -> None:
        """Reset event for retry."""
        if not self.is_failed():
            raise ValidationError("Only failed events can be retried")
        
        self.status = EventStatus.PENDING
        self.processed_at = None
        self.error_message = None
        self.updated_at = get_current_utc_datetime()
    
    def update_appointment_info(self, appointment_id: str, patient_id: str, 
                              doctor_id: str, datetime: datetime, symptoms: str) -> None:
        """Update appointment information in the event."""
        if not appointment_id or not patient_id or not doctor_id or not datetime or not symptoms:
            raise ValidationError("All appointment information is required")
        
        if not validate_string_length(symptoms, 2000, 1):
            raise ValidationError("Invalid symptoms")
        
        self.appointment_id = appointment_id
        self.patient_id = patient_id
        self.doctor_id = doctor_id
        self.datetime = datetime
        self.symptoms = symptoms
        self.updated_at = get_current_utc_datetime()
    
    def __str__(self) -> str:
        """String representation of the event."""
        return f"BookingEvent {self.event_id} - {self.appointment_id} ({self.status.value})"
    
    def __repr__(self) -> str:
        """Detailed representation of the event."""
        return (f"AppointmentBookingEvent(event_id='{self.event_id}', "
                f"appointment_id='{self.appointment_id}', status={self.status.value})")