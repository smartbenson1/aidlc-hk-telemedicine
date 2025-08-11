"""
Patient model class for the Appointment Matching Service.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from ..utils.enums import UserStatus
from ..utils.helpers import (
    generate_uuid, get_current_utc_datetime, validate_email, 
    validate_phone, validate_string_length
)
from ..utils.exceptions import ValidationError


@dataclass
class Patient:
    """Patient profile component."""
    
    # Identity
    id: str = field(default_factory=generate_uuid)
    
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
        """Validate the patient data."""
        errors = []
        
        # Validate required fields
        if not self.name:
            errors.append("Name is required")
        elif not validate_string_length(self.name, 100, 1):
            errors.append("Name must be between 1 and 100 characters")
        
        if not self.email:
            errors.append("Email is required")
        elif not validate_email(self.email):
            errors.append("Invalid email format")
        
        if not self.phone:
            errors.append("Phone is required")
        elif not validate_phone(self.phone):
            errors.append("Invalid phone format")
        
        # Validate emergency contact information
        if not self.emergency_contact_name:
            errors.append("Emergency contact name is required")
        elif not validate_string_length(self.emergency_contact_name, 100, 1):
            errors.append("Emergency contact name must be between 1 and 100 characters")
        
        if not self.emergency_contact_phone:
            errors.append("Emergency contact phone is required")
        elif not validate_phone(self.emergency_contact_phone):
            errors.append("Invalid emergency contact phone format")
        
        if not self.emergency_contact_relationship:
            errors.append("Emergency contact relationship is required")
        elif not validate_string_length(self.emergency_contact_relationship, 50, 1):
            errors.append("Emergency contact relationship must be between 1 and 50 characters")
        
        # Validate optional medical history
        if self.medical_history and not validate_string_length(self.medical_history, 2000):
            errors.append("Medical history must be at most 2000 characters")
        
        if errors:
            raise ValidationError(f"Patient validation failed: {'; '.join(errors)}")
        
        return True
    
    def validate_email(self, email: str) -> bool:
        """Validate email format."""
        return validate_email(email)
    
    def validate_phone(self, phone: str) -> bool:
        """Validate phone format."""
        return validate_phone(phone)
    
    def validate_emergency_contact(self, name: str, phone: str, relationship: str) -> bool:
        """Validate emergency contact information."""
        return (
            validate_string_length(name, 100, 1) and
            validate_phone(phone) and
            validate_string_length(relationship, 50, 1)
        )
    
    def update_emergency_contact(self, name: str, phone: str, relationship: str) -> None:
        """Update emergency contact information."""
        if not self.validate_emergency_contact(name, phone, relationship):
            raise ValidationError("Invalid emergency contact information")
        
        self.emergency_contact_name = name
        self.emergency_contact_phone = phone
        self.emergency_contact_relationship = relationship
        self.updated_at = get_current_utc_datetime()
    
    def update_medical_history(self, medical_history: str) -> None:
        """Update medical history."""
        if medical_history and not validate_string_length(medical_history, 2000):
            raise ValidationError("Medical history must be at most 2000 characters")
        
        self.medical_history = medical_history
        self.updated_at = get_current_utc_datetime()
    
    def is_active(self) -> bool:
        """Check if the patient is active."""
        return self.status == UserStatus.ACTIVE
    
    def activate(self) -> None:
        """Activate the patient."""
        self.status = UserStatus.ACTIVE
        self.updated_at = get_current_utc_datetime()
    
    def deactivate(self) -> None:
        """Deactivate the patient."""
        self.status = UserStatus.INACTIVE
        self.updated_at = get_current_utc_datetime()
    
    def suspend(self) -> None:
        """Suspend the patient."""
        self.status = UserStatus.SUSPENDED
        self.updated_at = get_current_utc_datetime()
    
    def __str__(self) -> str:
        """String representation of the patient."""
        return f"{self.name} ({self.email})"
    
    def __repr__(self) -> str:
        """Detailed representation of the patient."""
        return (f"Patient(id='{self.id}', name='{self.name}', email='{self.email}', "
                f"status={self.status.value})")