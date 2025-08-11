"""
Availability request models for the User Management Service.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Optional
from uuid import UUID

from ..utils.validation_utils import ValidationResult, combine_validation_results
from ..utils.enums import AppointmentType, MAX_BOOKING_WINDOW_DAYS


@dataclass
class TimeSlotRequest:
    """Request model for creating a new time slot."""
    
    datetime: datetime
    appointment_type: AppointmentType
    specialty_id: UUID
    
    def __str__(self) -> str:
        """String representation of the time slot request."""
        return f"TimeSlotRequest({self.datetime}, {self.appointment_type.value})"
    
    def validate(self) -> ValidationResult:
        """Validate the time slot request."""
        result = ValidationResult(is_valid=True, errors=[])
        
        # Check if datetime is in the future
        if self.datetime <= datetime.utcnow():
            result.add_error("Time slot must be in the future", "datetime")
        
        # Check if datetime is within booking window
        max_future_date = datetime.utcnow() + timedelta(days=MAX_BOOKING_WINDOW_DAYS)
        if self.datetime > max_future_date:
            result.add_error(f"Time slot must be within {MAX_BOOKING_WINDOW_DAYS} days", "datetime")
        
        # Check if datetime is on the hour (no minutes/seconds)
        if self.datetime.minute != 0 or self.datetime.second != 0:
            result.add_error("Time slot must be on the hour (e.g., 2:00 PM, not 2:30 PM)", "datetime")
        
        # Check if appointment type is valid
        if not isinstance(self.appointment_type, AppointmentType):
            result.add_error("Invalid appointment type", "appointment_type")
        
        # Check if specialty_id is provided
        if not self.specialty_id:
            result.add_error("Specialty ID is required", "specialty_id")
        
        return result
    
    def is_within_business_hours(self) -> bool:
        """Check if the time slot is within business hours (6 AM - 11 PM)."""
        hour = self.datetime.hour
        return 6 <= hour <= 23
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            'datetime': self.datetime.isoformat(),
            'appointment_type': self.appointment_type.value,
            'specialty_id': str(self.specialty_id)
        }


@dataclass
class TimeSlotUpdateRequest:
    """Request model for updating an existing time slot."""
    
    appointment_type: Optional[AppointmentType] = None
    specialty_id: Optional[UUID] = None
    
    def __str__(self) -> str:
        """String representation of the time slot update request."""
        updates = []
        if self.appointment_type is not None:
            updates.append(f"type={self.appointment_type.value}")
        if self.specialty_id is not None:
            updates.append(f"specialty={self.specialty_id}")
        return f"TimeSlotUpdateRequest({', '.join(updates)})"
    
    def has_updates(self) -> bool:
        """Check if the request contains any updates."""
        return self.appointment_type is not None or self.specialty_id is not None
    
    def get_updated_fields(self) -> List[str]:
        """Get list of fields being updated."""
        fields = []
        if self.appointment_type is not None:
            fields.append("appointment_type")
        if self.specialty_id is not None:
            fields.append("specialty_id")
        return fields
    
    def validate(self) -> ValidationResult:
        """Validate the time slot update request."""
        result = ValidationResult(is_valid=True, errors=[])
        
        if not self.has_updates():
            result.add_error("At least one field must be provided for update")
            return result
        
        # Validate appointment type if provided
        if self.appointment_type is not None and not isinstance(self.appointment_type, AppointmentType):
            result.add_error("Invalid appointment type", "appointment_type")
        
        # Validate specialty_id if provided
        if self.specialty_id is not None and not self.specialty_id:
            result.add_error("Specialty ID cannot be empty", "specialty_id")
        
        return result
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        result = {}
        if self.appointment_type is not None:
            result['appointment_type'] = self.appointment_type.value
        if self.specialty_id is not None:
            result['specialty_id'] = str(self.specialty_id)
        return result


@dataclass
class AvailabilityQueryRequest:
    """Request model for querying doctor availability."""
    
    doctor_id: UUID
    start_date: datetime
    end_date: datetime
    specialty_id: Optional[UUID] = None
    appointment_type: Optional[AppointmentType] = None
    available_only: bool = True
    
    def __str__(self) -> str:
        """String representation of the availability query request."""
        return f"AvailabilityQueryRequest(doctor={self.doctor_id}, {self.start_date} to {self.end_date})"
    
    def validate(self) -> ValidationResult:
        """Validate the availability query request."""
        result = ValidationResult(is_valid=True, errors=[])
        
        # Check if doctor_id is provided
        if not self.doctor_id:
            result.add_error("Doctor ID is required", "doctor_id")
        
        # Check if start_date is provided
        if not self.start_date:
            result.add_error("Start date is required", "start_date")
        
        # Check if end_date is provided
        if not self.end_date:
            result.add_error("End date is required", "end_date")
        
        # Check if end_date is after start_date
        if self.start_date and self.end_date and self.end_date <= self.start_date:
            result.add_error("End date must be after start date", "end_date")
        
        # Check if date range is reasonable (not more than 3 months)
        if self.start_date and self.end_date:
            max_range = timedelta(days=90)
            if self.end_date - self.start_date > max_range:
                result.add_error("Date range cannot exceed 90 days", "end_date")
        
        return result
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            'doctor_id': str(self.doctor_id),
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat(),
            'specialty_id': str(self.specialty_id) if self.specialty_id else None,
            'appointment_type': self.appointment_type.value if self.appointment_type else None,
            'available_only': self.available_only
        }


@dataclass
class AvailabilityResult:
    """Result of an availability operation."""
    
    success: bool
    doctor_id: UUID
    operation: str  # "create", "update", "delete", "query"
    message: str = ""
    availability_id: Optional[UUID] = None
    errors: List[str] = None
    
    def __post_init__(self):
        """Initialize errors list if None."""
        if self.errors is None:
            self.errors = []
    
    @classmethod
    def success_result(cls, doctor_id: UUID, operation: str, 
                      availability_id: Optional[UUID] = None,
                      message: str = "Operation successful") -> 'AvailabilityResult':
        """Create a successful availability result."""
        return cls(
            success=True,
            doctor_id=doctor_id,
            operation=operation,
            availability_id=availability_id,
            message=message
        )
    
    @classmethod
    def error_result(cls, doctor_id: UUID, operation: str, message: str,
                    errors: List[str] = None) -> 'AvailabilityResult':
        """Create an error availability result."""
        return cls(
            success=False,
            doctor_id=doctor_id,
            operation=operation,
            message=message,
            errors=errors or []
        )
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            'success': self.success,
            'doctor_id': str(self.doctor_id),
            'operation': self.operation,
            'message': self.message,
            'availability_id': str(self.availability_id) if self.availability_id else None,
            'errors': self.errors
        }


@dataclass
class BulkAvailabilityRequest:
    """Request model for creating multiple time slots at once."""
    
    doctor_id: UUID
    time_slots: List[TimeSlotRequest]
    
    def __str__(self) -> str:
        """String representation of the bulk availability request."""
        return f"BulkAvailabilityRequest(doctor={self.doctor_id}, slots={len(self.time_slots)})"
    
    def validate(self) -> ValidationResult:
        """Validate the bulk availability request."""
        result = ValidationResult(is_valid=True, errors=[])
        
        # Check if doctor_id is provided
        if not self.doctor_id:
            result.add_error("Doctor ID is required", "doctor_id")
        
        # Check if time_slots is provided and not empty
        if not self.time_slots:
            result.add_error("At least one time slot is required", "time_slots")
            return result
        
        # Check if there are too many slots (business rule)
        if len(self.time_slots) > 50:
            result.add_error("Cannot create more than 50 slots at once", "time_slots")
        
        # Validate each time slot
        for i, slot in enumerate(self.time_slots):
            slot_validation = slot.validate()
            if not slot_validation.is_valid:
                for error in slot_validation.errors:
                    result.add_error(f"Slot {i+1}: {error}", "time_slots")
        
        # Check for duplicate time slots
        datetimes = [slot.datetime for slot in self.time_slots]
        if len(datetimes) != len(set(datetimes)):
            result.add_error("Duplicate time slots are not allowed", "time_slots")
        
        return result
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            'doctor_id': str(self.doctor_id),
            'time_slots': [slot.to_dict() for slot in self.time_slots]
        }