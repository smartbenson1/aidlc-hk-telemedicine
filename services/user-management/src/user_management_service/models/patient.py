"""
Patient model for the User Management Service.
"""

from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from ..utils.base_models import BaseEntity
from ..utils.enums import UserStatus


@dataclass
class Patient(BaseEntity):
    """Patient entity model."""
    
    # Basic Information
    name: str = ""
    email: str = ""
    phone: str = ""
    
    # Medical Information
    medical_history: str = ""
    emergency_contact_name: str = ""
    emergency_contact_phone: str = ""
    emergency_contact_relationship: str = ""
    
    # System Fields
    status: UserStatus = UserStatus.ACTIVE
    
    def __str__(self) -> str:
        """String representation of the patient."""
        return f"{self.name} ({self.email})"
    
    def __repr__(self) -> str:
        """Detailed string representation of the patient."""
        return (f"Patient(id={self.id}, name='{self.name}', email='{self.email}', "
                f"status={self.status.value})")
    
    def is_active(self) -> bool:
        """Check if the patient is active."""
        return self.status == UserStatus.ACTIVE
    
    def has_medical_history(self) -> bool:
        """Check if the patient has medical history recorded."""
        return bool(self.medical_history and self.medical_history.strip())
    
    def update_medical_history(self, medical_history: str, updated_by: Optional[UUID] = None) -> None:
        """Update the patient's medical history."""
        self.medical_history = medical_history
        self.update_timestamp(updated_by)
    
    def update_emergency_contact(self, name: str, phone: str, relationship: str, 
                               updated_by: Optional[UUID] = None) -> None:
        """Update the patient's emergency contact information."""
        self.emergency_contact_name = name
        self.emergency_contact_phone = phone
        self.emergency_contact_relationship = relationship
        self.update_timestamp(updated_by)
    
    def activate(self, updated_by: Optional[UUID] = None) -> None:
        """Activate the patient."""
        self.status = UserStatus.ACTIVE
        self.update_timestamp(updated_by)
    
    def deactivate(self, updated_by: Optional[UUID] = None) -> None:
        """Deactivate the patient."""
        self.status = UserStatus.INACTIVE
        self.update_timestamp(updated_by)
    
    def suspend(self, updated_by: Optional[UUID] = None) -> None:
        """Suspend the patient."""
        self.status = UserStatus.SUSPENDED
        self.update_timestamp(updated_by)
    
    def get_emergency_contact_info(self) -> dict:
        """Get emergency contact information as a dictionary."""
        return {
            'name': self.emergency_contact_name,
            'phone': self.emergency_contact_phone,
            'relationship': self.emergency_contact_relationship
        }
    
    def to_dict(self) -> dict:
        """Convert patient to dictionary representation."""
        return {
            'id': str(self.id),
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'medical_history': self.medical_history,
            'emergency_contact_name': self.emergency_contact_name,
            'emergency_contact_phone': self.emergency_contact_phone,
            'emergency_contact_relationship': self.emergency_contact_relationship,
            'status': self.status.value,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'created_by': str(self.created_by) if self.created_by else None,
            'updated_by': str(self.updated_by) if self.updated_by else None
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Patient':
        """Create patient from dictionary representation."""
        from uuid import UUID
        from datetime import datetime
        
        patient = cls()
        patient.id = UUID(data['id'])
        patient.name = data['name']
        patient.email = data['email']
        patient.phone = data['phone']
        patient.medical_history = data['medical_history']
        patient.emergency_contact_name = data['emergency_contact_name']
        patient.emergency_contact_phone = data['emergency_contact_phone']
        patient.emergency_contact_relationship = data['emergency_contact_relationship']
        patient.status = UserStatus(data['status'])
        patient.created_at = datetime.fromisoformat(data['created_at'])
        patient.updated_at = datetime.fromisoformat(data['updated_at'])
        patient.created_by = UUID(data['created_by']) if data['created_by'] else None
        patient.updated_by = UUID(data['updated_by']) if data['updated_by'] else None
        
        return patient