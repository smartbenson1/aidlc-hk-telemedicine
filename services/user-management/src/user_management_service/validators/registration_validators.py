"""
Registration validators for the User Management Service.
"""

from typing import List, Optional
from uuid import UUID

from ..requests.registration_requests import DoctorRegistrationRequest, PatientRegistrationRequest
from ..repositories.doctor_repository import DoctorRepository
from ..repositories.patient_repository import PatientRepository
from ..repositories.specialty_repository import MedicalSpecialtyRepository
from ..utils.validation_utils import ValidationResult, combine_validation_results
from ..utils.exceptions import ValidationError, BusinessRuleError


class DoctorRegistrationValidator:
    """Validator for doctor registration requests."""
    
    def __init__(self, doctor_repository: DoctorRepository, 
                 specialty_repository: MedicalSpecialtyRepository):
        """Initialize the validator with required repositories."""
        self.doctor_repository = doctor_repository
        self.specialty_repository = specialty_repository
    
    def validate_registration_request(self, request: DoctorRegistrationRequest) -> ValidationResult:
        """Validate a complete doctor registration request."""
        # Basic field validation (already done in request model)
        basic_validation = request.validate()
        if not basic_validation.is_valid:
            return basic_validation
        
        # Business rule validations
        email_validation = self._validate_email_uniqueness(request.email)
        specialty_validation = self._validate_specialty_availability(request.specialties)
        registration_limits_validation = self._validate_registration_limits()
        
        return combine_validation_results(
            basic_validation, email_validation, specialty_validation, registration_limits_validation
        )
    
    def _validate_email_uniqueness(self, email: str) -> ValidationResult:
        """Validate that email is unique across all users."""
        result = ValidationResult(is_valid=True, errors=[])
        
        # Check if email exists in doctors
        if self.doctor_repository.email_exists(email):
            result.add_error("Email address is already registered as a doctor", "email")
        
        # Note: In a real implementation, you'd also check patients repository
        # For now, we'll assume cross-repository checking is handled at service level
        
        return result
    
    def _validate_specialty_availability(self, specialty_ids: List[UUID]) -> ValidationResult:
        """Validate that all specialties exist and are active."""
        result = ValidationResult(is_valid=True, errors=[])
        
        validation_result = self.specialty_repository.validate_specialties_exist(specialty_ids)
        
        if not validation_result['all_valid']:
            if validation_result['invalid_ids']:
                result.add_error(
                    f"Invalid specialty IDs: {', '.join(validation_result['invalid_ids'])}", 
                    "specialties"
                )
            
            if validation_result['inactive_ids']:
                result.add_error(
                    f"Inactive specialty IDs: {', '.join(validation_result['inactive_ids'])}", 
                    "specialties"
                )
        
        return result
    
    def _validate_registration_limits(self) -> ValidationResult:
        """Validate registration limits (simplified version)."""
        result = ValidationResult(is_valid=True, errors=[])
        
        # Simplified: Check if we have too many doctors (business rule)
        total_doctors = self.doctor_repository.count()
        if total_doctors >= 10000:  # Arbitrary limit for demo
            result.add_error("Registration temporarily unavailable due to capacity limits")
        
        return result
    
    def validate_and_throw(self, request: DoctorRegistrationRequest) -> None:
        """Validate and throw exception if validation fails."""
        validation_result = self.validate_registration_request(request)
        if not validation_result.is_valid:
            raise ValidationError(
                f"Doctor registration validation failed: {'; '.join(validation_result.errors)}",
                validation_result.field
            )


class PatientRegistrationValidator:
    """Validator for patient registration requests."""
    
    def __init__(self, patient_repository: PatientRepository):
        """Initialize the validator with required repositories."""
        self.patient_repository = patient_repository
    
    def validate_registration_request(self, request: PatientRegistrationRequest) -> ValidationResult:
        """Validate a complete patient registration request."""
        # Basic field validation (already done in request model)
        basic_validation = request.validate()
        if not basic_validation.is_valid:
            return basic_validation
        
        # Business rule validations
        email_validation = self._validate_email_uniqueness(request.email)
        phone_validation = self._validate_phone_uniqueness(request.phone)
        registration_limits_validation = self._validate_registration_limits()
        
        return combine_validation_results(
            basic_validation, email_validation, phone_validation, registration_limits_validation
        )
    
    def _validate_email_uniqueness(self, email: str) -> ValidationResult:
        """Validate that email is unique across all users."""
        result = ValidationResult(is_valid=True, errors=[])
        
        # Check if email exists in patients
        if self.patient_repository.email_exists(email):
            result.add_error("Email address is already registered as a patient", "email")
        
        return result
    
    def _validate_phone_uniqueness(self, phone: str) -> ValidationResult:
        """Validate that phone is unique."""
        result = ValidationResult(is_valid=True, errors=[])
        
        # Check if phone exists in patients
        if self.patient_repository.phone_exists(phone):
            result.add_error("Phone number is already registered", "phone")
        
        return result
    
    def _validate_registration_limits(self) -> ValidationResult:
        """Validate registration limits (simplified version)."""
        result = ValidationResult(is_valid=True, errors=[])
        
        # Simplified: Check if we have too many patients (business rule)
        total_patients = self.patient_repository.count()
        if total_patients >= 50000:  # Arbitrary limit for demo
            result.add_error("Registration temporarily unavailable due to capacity limits")
        
        return result
    
    def validate_and_throw(self, request: PatientRegistrationRequest) -> None:
        """Validate and throw exception if validation fails."""
        validation_result = self.validate_registration_request(request)
        if not validation_result.is_valid:
            raise ValidationError(
                f"Patient registration validation failed: {'; '.join(validation_result.errors)}",
                validation_result.field
            )


class RegistrationBusinessRules:
    """Business rules validator for registration operations."""
    
    def __init__(self, doctor_repository: DoctorRepository, 
                 patient_repository: PatientRepository):
        """Initialize with required repositories."""
        self.doctor_repository = doctor_repository
        self.patient_repository = patient_repository
    
    def validate_cross_user_email_uniqueness(self, email: str, 
                                           exclude_doctor_id: Optional[UUID] = None,
                                           exclude_patient_id: Optional[UUID] = None) -> ValidationResult:
        """Validate email uniqueness across both doctors and patients."""
        result = ValidationResult(is_valid=True, errors=[])
        
        # Check doctors
        if self.doctor_repository.email_exists(email, exclude_doctor_id):
            result.add_error("Email address is already registered by another user", "email")
        
        # Check patients
        if self.patient_repository.email_exists(email, exclude_patient_id):
            result.add_error("Email address is already registered by another user", "email")
        
        return result
    
    def validate_daily_registration_limits(self, user_type: str) -> ValidationResult:
        """Validate daily registration limits (simplified)."""
        result = ValidationResult(is_valid=True, errors=[])
        
        # In a real implementation, you'd track registrations by date
        # For demo purposes, we'll use a simple count check
        
        if user_type == "doctor":
            # Simplified: assume max 10 doctor registrations per day
            recent_doctors = len(self.doctor_repository.find_active_doctors())
            if recent_doctors >= 100:  # Simplified check
                result.add_error("Daily doctor registration limit reached")
        
        elif user_type == "patient":
            # Simplified: assume max 100 patient registrations per day
            recent_patients = len(self.patient_repository.find_active_patients())
            if recent_patients >= 1000:  # Simplified check
                result.add_error("Daily patient registration limit reached")
        
        return result
    
    def validate_system_capacity(self) -> ValidationResult:
        """Validate overall system capacity."""
        result = ValidationResult(is_valid=True, errors=[])
        
        total_users = self.doctor_repository.count() + self.patient_repository.count()
        
        if total_users >= 60000:  # Arbitrary system limit
            result.add_error("System capacity limit reached. Registration temporarily unavailable.")
        
        return result
    
    def validate_registration_window(self) -> ValidationResult:
        """Validate if registration is currently allowed (simplified)."""
        result = ValidationResult(is_valid=True, errors=[])
        
        # In a real implementation, you might have maintenance windows
        # or specific registration hours. For demo, always allow.
        
        return result


class RegistrationValidatorFactory:
    """Factory for creating registration validators."""
    
    @staticmethod
    def create_doctor_validator(doctor_repository: DoctorRepository,
                              specialty_repository: MedicalSpecialtyRepository) -> DoctorRegistrationValidator:
        """Create a doctor registration validator."""
        return DoctorRegistrationValidator(doctor_repository, specialty_repository)
    
    @staticmethod
    def create_patient_validator(patient_repository: PatientRepository) -> PatientRegistrationValidator:
        """Create a patient registration validator."""
        return PatientRegistrationValidator(patient_repository)
    
    @staticmethod
    def create_business_rules_validator(doctor_repository: DoctorRepository,
                                      patient_repository: PatientRepository) -> RegistrationBusinessRules:
        """Create a business rules validator."""
        return RegistrationBusinessRules(doctor_repository, patient_repository)