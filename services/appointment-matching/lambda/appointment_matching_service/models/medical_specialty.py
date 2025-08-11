"""
Medical Specialty model class for the Appointment Matching Service.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from ..utils.enums import SpecialtyStatus
from ..utils.helpers import (
    generate_uuid, get_current_utc_datetime, validate_string_length
)
from ..utils.exceptions import ValidationError


@dataclass
class MedicalSpecialty:
    """Medical specialty component."""
    
    # Identity
    id: str = field(default_factory=generate_uuid)
    
    # Basic Information
    name: str = ""
    description: str = ""
    
    # System Fields
    status: SpecialtyStatus = SpecialtyStatus.ACTIVE
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
        """Validate the medical specialty data."""
        errors = []
        
        # Validate required fields
        if not self.name:
            errors.append("Name is required")
        elif not validate_string_length(self.name, 100, 1):
            errors.append("Name must be between 1 and 100 characters")
        
        # Validate optional description
        if self.description and not validate_string_length(self.description, 500):
            errors.append("Description must be at most 500 characters")
        
        if errors:
            raise ValidationError(f"Medical specialty validation failed: {'; '.join(errors)}")
        
        return True
    
    def validate_name(self, name: str) -> bool:
        """Validate specialty name."""
        return validate_string_length(name, 100, 1)
    
    def validate_description(self, description: str) -> bool:
        """Validate specialty description."""
        return not description or validate_string_length(description, 500)
    
    def update_name(self, name: str) -> None:
        """Update the specialty name."""
        if not self.validate_name(name):
            raise ValidationError("Invalid specialty name")
        
        self.name = name
        self.updated_at = get_current_utc_datetime()
    
    def update_description(self, description: str) -> None:
        """Update the specialty description."""
        if not self.validate_description(description):
            raise ValidationError("Invalid specialty description")
        
        self.description = description
        self.updated_at = get_current_utc_datetime()
    
    def is_active(self) -> bool:
        """Check if the specialty is active."""
        return self.status == SpecialtyStatus.ACTIVE
    
    def activate(self) -> None:
        """Activate the specialty."""
        self.status = SpecialtyStatus.ACTIVE
        self.updated_at = get_current_utc_datetime()
    
    def deactivate(self) -> None:
        """Deactivate the specialty."""
        self.status = SpecialtyStatus.INACTIVE
        self.updated_at = get_current_utc_datetime()
    
    def __str__(self) -> str:
        """String representation of the specialty."""
        return f"{self.name}"
    
    def __repr__(self) -> str:
        """Detailed representation of the specialty."""
        return (f"MedicalSpecialty(id='{self.id}', name='{self.name}', "
                f"status={self.status.value})")