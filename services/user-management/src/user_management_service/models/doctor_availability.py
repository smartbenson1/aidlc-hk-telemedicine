"""
Doctor Availability model for the User Management Service.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID

from ..utils.base_models import BaseEntity
from ..utils.enums import AppointmentType, AvailabilityStatus


@dataclass
class DoctorAvailability(BaseEntity):
    """Doctor Availability entity model."""
    
    # Identity
    doctor_id: UUID = None
    
    # Scheduling Information
    datetime: datetime = None
    appointment_type: AppointmentType = AppointmentType.IN_PERSON
    specialty_id: UUID = None
    
    # Status Management
    status: AvailabilityStatus = AvailabilityStatus.AVAILABLE
    
    def __str__(self) -> str:
        """String representation of the doctor availability."""
        return f"Availability for {self.doctor_id} on {self.datetime} ({self.status.value})"
    
    def __repr__(self) -> str:
        """Detailed string representation of the doctor availability."""
        return (f"DoctorAvailability(id={self.id}, doctor_id={self.doctor_id}, "
                f"datetime={self.datetime}, status={self.status.value})")
    
    def is_available(self) -> bool:
        """Check if the slot is available for booking."""
        return self.status == AvailabilityStatus.AVAILABLE
    
    def is_booked(self) -> bool:
        """Check if the slot is booked."""
        return self.status == AvailabilityStatus.BOOKED
    
    def is_blocked(self) -> bool:
        """Check if the slot is blocked."""
        return self.status == AvailabilityStatus.BLOCKED
    
    def is_in_future(self) -> bool:
        """Check if the availability slot is in the future."""
        return self.datetime > datetime.utcnow()
    
    def book(self, updated_by: Optional[UUID] = None) -> None:
        """Mark the slot as booked."""
        if self.is_available():
            self.status = AvailabilityStatus.BOOKED
            self.update_timestamp(updated_by)
    
    def unbook(self, updated_by: Optional[UUID] = None) -> None:
        """Mark the slot as available (unbook)."""
        if self.is_booked():
            self.status = AvailabilityStatus.AVAILABLE
            self.update_timestamp(updated_by)
    
    def block(self, updated_by: Optional[UUID] = None) -> None:
        """Block the slot."""
        self.status = AvailabilityStatus.BLOCKED
        self.update_timestamp(updated_by)
    
    def unblock(self, updated_by: Optional[UUID] = None) -> None:
        """Unblock the slot (make available)."""
        if self.is_blocked():
            self.status = AvailabilityStatus.AVAILABLE
            self.update_timestamp(updated_by)
    
    def update_appointment_type(self, appointment_type: AppointmentType, 
                              updated_by: Optional[UUID] = None) -> None:
        """Update the appointment type."""
        if self.is_available():  # Only allow changes for available slots
            self.appointment_type = appointment_type
            self.update_timestamp(updated_by)
    
    def update_specialty(self, specialty_id: UUID, updated_by: Optional[UUID] = None) -> None:
        """Update the specialty for this slot."""
        if self.is_available():  # Only allow changes for available slots
            self.specialty_id = specialty_id
            self.update_timestamp(updated_by)
    
    def can_be_modified(self) -> bool:
        """Check if the slot can be modified."""
        return self.is_available() and self.is_in_future()
    
    def can_be_deleted(self) -> bool:
        """Check if the slot can be deleted."""
        return self.is_available() and self.is_in_future()
    
    def get_duration_hours(self) -> int:
        """Get the duration of the slot in hours."""
        return 1  # All slots are 1 hour as per business rules
    
    def to_dict(self) -> dict:
        """Convert doctor availability to dictionary representation."""
        return {
            'id': str(self.id),
            'doctor_id': str(self.doctor_id),
            'datetime': self.datetime.isoformat(),
            'appointment_type': self.appointment_type.value,
            'specialty_id': str(self.specialty_id) if self.specialty_id else None,
            'status': self.status.value,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'created_by': str(self.created_by) if self.created_by else None,
            'updated_by': str(self.updated_by) if self.updated_by else None
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'DoctorAvailability':
        """Create doctor availability from dictionary representation."""
        from uuid import UUID
        from datetime import datetime
        
        availability = cls()
        availability.id = UUID(data['id'])
        availability.doctor_id = UUID(data['doctor_id'])
        availability.datetime = datetime.fromisoformat(data['datetime'])
        availability.appointment_type = AppointmentType(data['appointment_type'])
        availability.specialty_id = UUID(data['specialty_id']) if data['specialty_id'] else None
        availability.status = AvailabilityStatus(data['status'])
        availability.created_at = datetime.fromisoformat(data['created_at'])
        availability.updated_at = datetime.fromisoformat(data['updated_at'])
        availability.created_by = UUID(data['created_by']) if data['created_by'] else None
        availability.updated_by = UUID(data['updated_by']) if data['updated_by'] else None
        
        return availability