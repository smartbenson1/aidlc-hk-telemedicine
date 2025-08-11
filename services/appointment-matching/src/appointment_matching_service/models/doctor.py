"""
Doctor model class for the Appointment Matching Service.
"""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from ..utils.enums import UserStatus
from ..utils.helpers import (
    generate_uuid, get_current_utc_datetime, validate_email, 
    validate_phone, validate_string_length, validate_decimal_range
)
from ..utils.exceptions import ValidationError


@dataclass
class Doctor:
    """Doctor profile component."""
    
    # Identity
    id: str = field(default_factory=generate_uuid)
    
    # Basic Information
    name: str = ""
    email: str = ""
    phone: str = ""
    location: str = ""
    
    # Professional Information
    specialties: List[str] = field(default_factory=list)  # List of specialty UUIDs
    experience: str = ""
    rating: Decimal = field(default_factory=lambda: Decimal('0.0'))
    
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
        """Validate the doctor data."""
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
        
        if not self.location:
            errors.append("Location is required")
        elif not validate_string_length(self.location, 200, 1):
            errors.append("Location must be between 1 and 200 characters")
        
        if not self.specialties:
            errors.append("At least one specialty is required")
        
        if not self.experience:
            errors.append("Experience is required")
        elif not validate_string_length(self.experience, 1000, 1):
            errors.append("Experience must be between 1 and 1000 characters")
        
        # Validate rating
        if not validate_decimal_range(self.rating, Decimal('0.0'), Decimal('5.0')):
            errors.append("Rating must be between 0.0 and 5.0")
        
        if errors:
            raise ValidationError(f"Doctor validation failed: {'; '.join(errors)}")
        
        return True
    
    def validate_email(self, email: str) -> bool:
        """Validate email format."""
        return validate_email(email)
    
    def validate_phone(self, phone: str) -> bool:
        """Validate phone format."""
        return validate_phone(phone)
    
    def validate_specialties(self, specialties: List[str]) -> bool:
        """Validate specialties list."""
        if not specialties:
            return False
        
        # Check that all specialties are valid UUIDs (basic check)
        for specialty_id in specialties:
            if not isinstance(specialty_id, str) or len(specialty_id) != 36:
                return False
        
        return True
    
    def add_specialty(self, specialty_id: str) -> None:
        """Add a specialty to the doctor."""
        if specialty_id not in self.specialties:
            self.specialties.append(specialty_id)
            self.updated_at = get_current_utc_datetime()
    
    def remove_specialty(self, specialty_id: str) -> bool:
        """Remove a specialty from the doctor."""
        if specialty_id in self.specialties:
            self.specialties.remove(specialty_id)
            self.updated_at = get_current_utc_datetime()
            return True
        return False
    
    def update_rating(self, new_rating: Decimal) -> None:
        """Update the doctor's rating."""
        if validate_decimal_range(new_rating, Decimal('0.0'), Decimal('5.0')):
            self.rating = new_rating
            self.updated_at = get_current_utc_datetime()
        else:
            raise ValidationError("Rating must be between 0.0 and 5.0")
    
    def is_active(self) -> bool:
        """Check if the doctor is active."""
        return self.status == UserStatus.ACTIVE
    
    def activate(self) -> None:
        """Activate the doctor."""
        self.status = UserStatus.ACTIVE
        self.updated_at = get_current_utc_datetime()
    
    def deactivate(self) -> None:
        """Deactivate the doctor."""
        self.status = UserStatus.INACTIVE
        self.updated_at = get_current_utc_datetime()
    
    def suspend(self) -> None:
        """Suspend the doctor."""
        self.status = UserStatus.SUSPENDED
        self.updated_at = get_current_utc_datetime()
    
    def __str__(self) -> str:
        """String representation of the doctor."""
        return f"Dr. {self.name} ({self.email}) - Rating: {self.rating}"
    
    def __repr__(self) -> str:
        """Detailed representation of the doctor."""
        return (f"Doctor(id='{self.id}', name='{self.name}', email='{self.email}', "
                f"rating={self.rating}, status={self.status.value})")