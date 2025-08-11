"""
Profile update request models for the User Management Service.
"""

from dataclasses import dataclass
from typing import List, Optional
from uuid import UUID

from ..utils.validation_utils import ValidationResult, combine_validation_results
from ..utils.validation_utils import (
    validate_email, validate_phone, validate_name, validate_text_length,
    validate_uuid_list, validate_emergency_contact_relationship,
    validate_phone_uniqueness
)
from ..utils.enums import (
    MAX_LOCATION_LENGTH, MAX_EXPERIENCE_LENGTH, MIN_EXPERIENCE_LENGTH,
    MAX_MEDICAL_HISTORY_LENGTH, MIN_SPECIALTIES_PER_DOCTOR, MAX_SPECIALTIES_PER_DOCTOR
)


@dataclass
class DoctorProfileUpdateRequest:
    """Request model for doctor profile updates."""
    
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    specialties: Optional[List[UUID]] = None
    experience: Optional[str] = None
    
    def __str__(self) -> str:
        """String representation of the update request."""
        updated_fields = [field for field, value in self.__dict__.items() if value is not None]
        return f"DoctorProfileUpdateRequest(updating: {', '.join(updated_fields)})"
    
    def has_updates(self) -> bool:
        """Check if the request contains any updates."""
        return any(value is not None for value in self.__dict__.values())
    
    def get_updated_fields(self) -> List[str]:
        """Get list of fields being updated."""
        return [field for field, value in self.__dict__.items() if value is not None]
    
    def validate(self) -> ValidationResult:
        """Validate the doctor profile update request."""
        if not self.has_updates():
            return ValidationResult(
                is_valid=False, 
                errors=["At least one field must be provided for update"]
            )
        
        validations = []
        
        # Validate each field that is being updated
        if self.name is not None:
            validations.append(validate_name(self.name, "name"))
        
        if self.email is not None:
            validations.append(validate_email(self.email))
        
        if self.phone is not None:
            validations.append(validate_phone(self.phone))
        
        if self.location is not None:
            validations.append(validate_text_length(
                self.location, "location", min_length=5, max_length=MAX_LOCATION_LENGTH
            ))
        
        if self.specialties is not None:
            validations.append(validate_uuid_list(
                self.specialties, "specialties",
                min_count=MIN_SPECIALTIES_PER_DOCTOR, max_count=MAX_SPECIALTIES_PER_DOCTOR
            ))
        
        if self.experience is not None:
            validations.append(validate_text_length(
                self.experience, "experience",
                min_length=MIN_EXPERIENCE_LENGTH, max_length=MAX_EXPERIENCE_LENGTH
            ))
        
        return combine_validation_results(*validations) if validations else ValidationResult(is_valid=True, errors=[])
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        result = {}
        if self.name is not None:
            result['name'] = self.name
        if self.email is not None:
            result['email'] = self.email
        if self.phone is not None:
            result['phone'] = self.phone
        if self.location is not None:
            result['location'] = self.location
        if self.specialties is not None:
            result['specialties'] = [str(s) for s in self.specialties]
        if self.experience is not None:
            result['experience'] = self.experience
        return result


@dataclass
class PatientProfileUpdateRequest:
    """Request model for patient profile updates."""
    
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    medical_history: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    emergency_contact_relationship: Optional[str] = None
    
    def __str__(self) -> str:
        """String representation of the update request."""
        updated_fields = [field for field, value in self.__dict__.items() if value is not None]
        return f"PatientProfileUpdateRequest(updating: {', '.join(updated_fields)})"
    
    def has_updates(self) -> bool:
        """Check if the request contains any updates."""
        return any(value is not None for value in self.__dict__.values())
    
    def get_updated_fields(self) -> List[str]:
        """Get list of fields being updated."""
        return [field for field, value in self.__dict__.items() if value is not None]
    
    def has_emergency_contact_updates(self) -> bool:
        """Check if any emergency contact fields are being updated."""
        emergency_fields = [
            self.emergency_contact_name,
            self.emergency_contact_phone,
            self.emergency_contact_relationship
        ]
        return any(field is not None for field in emergency_fields)
    
    def validate(self, current_phone: Optional[str] = None) -> ValidationResult:
        """Validate the patient profile update request."""
        if not self.has_updates():
            return ValidationResult(
                is_valid=False,
                errors=["At least one field must be provided for update"]
            )
        
        validations = []
        
        # Validate each field that is being updated
        if self.name is not None:
            validations.append(validate_name(self.name, "name"))
        
        if self.email is not None:
            validations.append(validate_email(self.email))
        
        if self.phone is not None:
            validations.append(validate_phone(self.phone))
        
        if self.medical_history is not None:
            validations.append(validate_text_length(
                self.medical_history, "medical_history",
                min_length=0, max_length=MAX_MEDICAL_HISTORY_LENGTH, required=False
            ))
        
        if self.emergency_contact_name is not None:
            validations.append(validate_name(self.emergency_contact_name, "emergency_contact_name"))
        
        if self.emergency_contact_phone is not None:
            validations.append(validate_phone(self.emergency_contact_phone))
        
        if self.emergency_contact_relationship is not None:
            validations.append(validate_emergency_contact_relationship(
                self.emergency_contact_relationship
            ))
        
        # Validate phone uniqueness if both phones are being updated or provided
        phone_to_check = self.phone if self.phone is not None else current_phone
        if (phone_to_check and self.emergency_contact_phone is not None):
            validations.append(validate_phone_uniqueness(
                phone_to_check, self.emergency_contact_phone,
                "phone", "emergency_contact_phone"
            ))
        
        return combine_validation_results(*validations) if validations else ValidationResult(is_valid=True, errors=[])
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        result = {}
        if self.name is not None:
            result['name'] = self.name
        if self.email is not None:
            result['email'] = self.email
        if self.phone is not None:
            result['phone'] = self.phone
        if self.medical_history is not None:
            result['medical_history'] = self.medical_history
        if self.emergency_contact_name is not None:
            result['emergency_contact_name'] = self.emergency_contact_name
        if self.emergency_contact_phone is not None:
            result['emergency_contact_phone'] = self.emergency_contact_phone
        if self.emergency_contact_relationship is not None:
            result['emergency_contact_relationship'] = self.emergency_contact_relationship
        return result


@dataclass
class ProfileUpdateResult:
    """Result of a profile update operation."""
    
    success: bool
    user_id: UUID
    updated_fields: List[str]
    message: str = ""
    errors: List[str] = None
    
    def __post_init__(self):
        """Initialize errors list if None."""
        if self.errors is None:
            self.errors = []
    
    @classmethod
    def success_result(cls, user_id: UUID, updated_fields: List[str], 
                      message: str = "Profile updated successfully") -> 'ProfileUpdateResult':
        """Create a successful profile update result."""
        return cls(
            success=True,
            user_id=user_id,
            updated_fields=updated_fields,
            message=message
        )
    
    @classmethod
    def error_result(cls, user_id: UUID, message: str, 
                    errors: List[str] = None) -> 'ProfileUpdateResult':
        """Create an error profile update result."""
        return cls(
            success=False,
            user_id=user_id,
            updated_fields=[],
            message=message,
            errors=errors or []
        )
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            'success': self.success,
            'user_id': str(self.user_id),
            'updated_fields': self.updated_fields,
            'message': self.message,
            'errors': self.errors
        }