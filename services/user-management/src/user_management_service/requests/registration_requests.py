"""
Registration request models for the User Management Service.
"""

from dataclasses import dataclass
from typing import List, Optional
from uuid import UUID

from ..utils.validation_utils import ValidationResult, combine_validation_results
from ..utils.validation_utils import (
    validate_email, validate_phone, validate_name, validate_text_length,
    validate_uuid_list, validate_emergency_contact_relationship,
    validate_phone_uniqueness, validate_required_fields
)
from ..utils.enums import (
    MAX_LOCATION_LENGTH, MAX_EXPERIENCE_LENGTH, MIN_EXPERIENCE_LENGTH,
    MAX_MEDICAL_HISTORY_LENGTH, MIN_SPECIALTIES_PER_DOCTOR, MAX_SPECIALTIES_PER_DOCTOR
)


@dataclass
class DoctorRegistrationRequest:
    """Request model for doctor registration."""
    
    name: str
    email: str
    phone: str
    location: str
    specialties: List[UUID]
    experience: str
    
    def __str__(self) -> str:
        """String representation of the registration request."""
        return f"DoctorRegistrationRequest(email={self.email}, name={self.name})"
    
    def validate(self) -> ValidationResult:
        """Validate the doctor registration request."""
        # Check required fields
        required_validation = validate_required_fields(
            self.__dict__, 
            ['name', 'email', 'phone', 'location', 'specialties', 'experience']
        )
        
        if not required_validation.is_valid:
            return required_validation
        
        # Individual field validations
        name_validation = validate_name(self.name, "name")
        email_validation = validate_email(self.email)
        phone_validation = validate_phone(self.phone)
        location_validation = validate_text_length(
            self.location, "location", min_length=5, max_length=MAX_LOCATION_LENGTH
        )
        specialties_validation = validate_uuid_list(
            self.specialties, "specialties", 
            min_count=MIN_SPECIALTIES_PER_DOCTOR, max_count=MAX_SPECIALTIES_PER_DOCTOR
        )
        experience_validation = validate_text_length(
            self.experience, "experience", 
            min_length=MIN_EXPERIENCE_LENGTH, max_length=MAX_EXPERIENCE_LENGTH
        )
        
        return combine_validation_results(
            name_validation, email_validation, phone_validation,
            location_validation, specialties_validation, experience_validation
        )
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'location': self.location,
            'specialties': [str(s) for s in self.specialties],
            'experience': self.experience
        }


@dataclass
class PatientRegistrationRequest:
    """Request model for patient registration."""
    
    name: str
    email: str
    phone: str
    medical_history: Optional[str] = ""
    emergency_contact_name: str = ""
    emergency_contact_phone: str = ""
    emergency_contact_relationship: str = ""
    
    def __str__(self) -> str:
        """String representation of the registration request."""
        return f"PatientRegistrationRequest(email={self.email}, name={self.name})"
    
    def validate(self) -> ValidationResult:
        """Validate the patient registration request."""
        # Check required fields
        required_validation = validate_required_fields(
            self.__dict__, 
            ['name', 'email', 'phone', 'emergency_contact_name', 
             'emergency_contact_phone', 'emergency_contact_relationship']
        )
        
        if not required_validation.is_valid:
            return required_validation
        
        # Individual field validations
        name_validation = validate_name(self.name, "name")
        email_validation = validate_email(self.email)
        phone_validation = validate_phone(self.phone)
        
        # Medical history is optional
        medical_history_validation = ValidationResult(is_valid=True, errors=[])
        if self.medical_history:
            medical_history_validation = validate_text_length(
                self.medical_history, "medical_history", 
                min_length=0, max_length=MAX_MEDICAL_HISTORY_LENGTH, required=False
            )
        
        # Emergency contact validations
        emergency_name_validation = validate_name(self.emergency_contact_name, "emergency_contact_name")
        emergency_phone_validation = validate_phone(self.emergency_contact_phone)
        emergency_relationship_validation = validate_emergency_contact_relationship(
            self.emergency_contact_relationship
        )
        
        # Phone uniqueness validation
        phone_uniqueness_validation = validate_phone_uniqueness(
            self.phone, self.emergency_contact_phone,
            "phone", "emergency_contact_phone"
        )
        
        return combine_validation_results(
            name_validation, email_validation, phone_validation,
            medical_history_validation, emergency_name_validation,
            emergency_phone_validation, emergency_relationship_validation,
            phone_uniqueness_validation
        )
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'medical_history': self.medical_history or "",
            'emergency_contact_name': self.emergency_contact_name,
            'emergency_contact_phone': self.emergency_contact_phone,
            'emergency_contact_relationship': self.emergency_contact_relationship
        }


@dataclass
class RegistrationResult:
    """Result of a registration operation."""
    
    success: bool
    user_id: Optional[UUID] = None
    email: str = ""
    user_type: str = ""
    message: str = ""
    errors: List[str] = None
    
    def __post_init__(self):
        """Initialize errors list if None."""
        if self.errors is None:
            self.errors = []
    
    @classmethod
    def success_result(cls, user_id: UUID, email: str, user_type: str, 
                      message: str = "Registration successful") -> 'RegistrationResult':
        """Create a successful registration result."""
        return cls(
            success=True,
            user_id=user_id,
            email=email,
            user_type=user_type,
            message=message
        )
    
    @classmethod
    def error_result(cls, email: str, user_type: str, message: str, 
                    errors: List[str] = None) -> 'RegistrationResult':
        """Create an error registration result."""
        return cls(
            success=False,
            email=email,
            user_type=user_type,
            message=message,
            errors=errors or []
        )
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            'success': self.success,
            'user_id': str(self.user_id) if self.user_id else None,
            'email': self.email,
            'user_type': self.user_type,
            'message': self.message,
            'errors': self.errors
        }