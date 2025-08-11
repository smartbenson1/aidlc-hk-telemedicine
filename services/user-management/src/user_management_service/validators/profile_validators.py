"""
Profile update validators for the User Management Service.
"""

from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from ..requests.profile_update_requests import DoctorProfileUpdateRequest, PatientProfileUpdateRequest
from ..repositories.doctor_repository import DoctorRepository
from ..repositories.patient_repository import PatientRepository
from ..repositories.specialty_repository import MedicalSpecialtyRepository
from ..models.doctor import Doctor
from ..models.patient import Patient
from ..utils.validation_utils import ValidationResult, combine_validation_results
from ..utils.exceptions import ValidationError, BusinessRuleError, PermissionError


class DoctorProfileUpdateValidator:
    """Validator for doctor profile update requests."""
    
    def __init__(self, doctor_repository: DoctorRepository,
                 specialty_repository: MedicalSpecialtyRepository):
        """Initialize the validator with required repositories."""
        self.doctor_repository = doctor_repository
        self.specialty_repository = specialty_repository
    
    def validate_profile_update_request(self, request: DoctorProfileUpdateRequest,
                                      current_doctor: Doctor) -> ValidationResult:
        """Validate a complete doctor profile update request."""
        # Basic field validation (already done in request model)
        basic_validation = request.validate()
        if not basic_validation.is_valid:
            return basic_validation
        
        # Business rule validations
        validations = [basic_validation]
        
        # Email uniqueness validation
        if request.email is not None:
            email_validation = self._validate_email_update(request.email, current_doctor)
            validations.append(email_validation)
        
        # Specialty validation
        if request.specialties is not None:
            specialty_validation = self._validate_specialty_update(request.specialties)
            validations.append(specialty_validation)
        
        # Update frequency validation
        frequency_validation = self._validate_update_frequency(current_doctor.id)
        validations.append(frequency_validation)
        
        return combine_validation_results(*validations)
    
    def _validate_email_update(self, new_email: str, current_doctor: Doctor) -> ValidationResult:
        """Validate email update for uniqueness."""
        result = ValidationResult(is_valid=True, errors=[])
        
        # Check if new email is different from current
        if new_email == current_doctor.email:
            return result  # No change, no validation needed
        
        # Check if new email exists in doctors (excluding current doctor)
        if self.doctor_repository.email_exists(new_email, exclude_id=current_doctor.id):
            result.add_error("Email address is already in use by another doctor", "email")
        
        return result
    
    def _validate_specialty_update(self, new_specialties: list) -> ValidationResult:
        """Validate specialty update."""
        result = ValidationResult(is_valid=True, errors=[])
        
        validation_result = self.specialty_repository.validate_specialties_exist(new_specialties)
        
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
    
    def _validate_update_frequency(self, doctor_id: UUID) -> ValidationResult:
        """Validate update frequency limits (simplified)."""
        result = ValidationResult(is_valid=True, errors=[])
        
        # In a real implementation, you'd track update frequency
        # For demo purposes, we'll use a simplified check
        
        # Simplified: assume max 5 updates per day
        # This would require tracking update history in a real implementation
        
        return result
    
    def validate_update_permissions(self, doctor_id: UUID, requester_id: UUID,
                                  is_admin: bool = False) -> ValidationResult:
        """Validate permissions for profile update."""
        result = ValidationResult(is_valid=True, errors=[])
        
        # Users can only update their own profiles, unless they're admin
        if not is_admin and doctor_id != requester_id:
            result.add_error("You can only update your own profile", "permissions")
        
        return result
    
    def validate_critical_field_changes(self, request: DoctorProfileUpdateRequest,
                                      current_doctor: Doctor) -> ValidationResult:
        """Validate critical field changes that might require additional verification."""
        result = ValidationResult(is_valid=True, errors=[])
        
        # Email changes might require verification
        if request.email is not None and request.email != current_doctor.email:
            # In a real implementation, you might require email verification
            pass
        
        # Phone changes might require confirmation
        if request.phone is not None and request.phone != current_doctor.phone:
            # In a real implementation, you might require phone verification
            pass
        
        return result
    
    def validate_and_throw(self, request: DoctorProfileUpdateRequest,
                          current_doctor: Doctor) -> None:
        """Validate and throw exception if validation fails."""
        validation_result = self.validate_profile_update_request(request, current_doctor)
        if not validation_result.is_valid:
            raise ValidationError(
                f"Doctor profile update validation failed: {'; '.join(validation_result.errors)}",
                validation_result.field
            )


class PatientProfileUpdateValidator:
    """Validator for patient profile update requests."""
    
    def __init__(self, patient_repository: PatientRepository):
        """Initialize the validator with required repositories."""
        self.patient_repository = patient_repository
    
    def validate_profile_update_request(self, request: PatientProfileUpdateRequest,
                                      current_patient: Patient) -> ValidationResult:
        """Validate a complete patient profile update request."""
        # Basic field validation (already done in request model)
        basic_validation = request.validate(current_patient.phone)
        if not basic_validation.is_valid:
            return basic_validation
        
        # Business rule validations
        validations = [basic_validation]
        
        # Email uniqueness validation
        if request.email is not None:
            email_validation = self._validate_email_update(request.email, current_patient)
            validations.append(email_validation)
        
        # Phone uniqueness validation
        if request.phone is not None:
            phone_validation = self._validate_phone_update(request.phone, current_patient)
            validations.append(phone_validation)
        
        # Emergency contact validation
        if request.has_emergency_contact_updates():
            emergency_validation = self._validate_emergency_contact_update(request, current_patient)
            validations.append(emergency_validation)
        
        # Update frequency validation
        frequency_validation = self._validate_update_frequency(current_patient.id)
        validations.append(frequency_validation)
        
        return combine_validation_results(*validations)
    
    def _validate_email_update(self, new_email: str, current_patient: Patient) -> ValidationResult:
        """Validate email update for uniqueness."""
        result = ValidationResult(is_valid=True, errors=[])
        
        # Check if new email is different from current
        if new_email == current_patient.email:
            return result  # No change, no validation needed
        
        # Check if new email exists in patients (excluding current patient)
        if self.patient_repository.email_exists(new_email, exclude_id=current_patient.id):
            result.add_error("Email address is already in use by another patient", "email")
        
        return result
    
    def _validate_phone_update(self, new_phone: str, current_patient: Patient) -> ValidationResult:
        """Validate phone update for uniqueness."""
        result = ValidationResult(is_valid=True, errors=[])
        
        # Check if new phone is different from current
        if new_phone == current_patient.phone:
            return result  # No change, no validation needed
        
        # Check if new phone exists in patients (excluding current patient)
        if self.patient_repository.phone_exists(new_phone, exclude_id=current_patient.id):
            result.add_error("Phone number is already in use by another patient", "phone")
        
        return result
    
    def _validate_emergency_contact_update(self, request: PatientProfileUpdateRequest,
                                         current_patient: Patient) -> ValidationResult:
        """Validate emergency contact update."""
        result = ValidationResult(is_valid=True, errors=[])
        
        # If any emergency contact field is being updated, validate all fields
        if request.has_emergency_contact_updates():
            # Get the phone to check against (either new or current)
            patient_phone = request.phone if request.phone is not None else current_patient.phone
            emergency_phone = (request.emergency_contact_phone 
                             if request.emergency_contact_phone is not None 
                             else current_patient.emergency_contact_phone)
            
            # Ensure emergency contact phone is different from patient phone
            if patient_phone and emergency_phone and patient_phone == emergency_phone:
                result.add_error(
                    "Emergency contact phone must be different from patient phone", 
                    "emergency_contact_phone"
                )
        
        return result
    
    def _validate_update_frequency(self, patient_id: UUID) -> ValidationResult:
        """Validate update frequency limits (simplified)."""
        result = ValidationResult(is_valid=True, errors=[])
        
        # In a real implementation, you'd track update frequency
        # For demo purposes, we'll use a simplified check
        
        return result
    
    def validate_update_permissions(self, patient_id: UUID, requester_id: UUID,
                                  is_admin: bool = False) -> ValidationResult:
        """Validate permissions for profile update."""
        result = ValidationResult(is_valid=True, errors=[])
        
        # Users can only update their own profiles, unless they're admin
        if not is_admin and patient_id != requester_id:
            result.add_error("You can only update your own profile", "permissions")
        
        return result
    
    def validate_critical_field_changes(self, request: PatientProfileUpdateRequest,
                                      current_patient: Patient) -> ValidationResult:
        """Validate critical field changes that might require additional verification."""
        result = ValidationResult(is_valid=True, errors=[])
        
        # Email changes might require verification
        if request.email is not None and request.email != current_patient.email:
            # In a real implementation, you might require email verification
            pass
        
        # Phone changes might require confirmation
        if request.phone is not None and request.phone != current_patient.phone:
            # In a real implementation, you might require phone verification
            pass
        
        return result
    
    def validate_and_throw(self, request: PatientProfileUpdateRequest,
                          current_patient: Patient) -> None:
        """Validate and throw exception if validation fails."""
        validation_result = self.validate_profile_update_request(request, current_patient)
        if not validation_result.is_valid:
            raise ValidationError(
                f"Patient profile update validation failed: {'; '.join(validation_result.errors)}",
                validation_result.field
            )


class ProfileUpdateBusinessRules:
    """Business rules validator for profile update operations."""
    
    def __init__(self, doctor_repository: DoctorRepository,
                 patient_repository: PatientRepository):
        """Initialize with required repositories."""
        self.doctor_repository = doctor_repository
        self.patient_repository = patient_repository
    
    def validate_cross_user_email_uniqueness(self, email: str, user_type: str,
                                           exclude_user_id: UUID) -> ValidationResult:
        """Validate email uniqueness across both doctors and patients."""
        result = ValidationResult(is_valid=True, errors=[])
        
        if user_type == "doctor":
            # Check if email exists in patients
            if self.patient_repository.email_exists(email):
                result.add_error("Email address is already registered by a patient", "email")
            # Check if email exists in other doctors
            if self.doctor_repository.email_exists(email, exclude_id=exclude_user_id):
                result.add_error("Email address is already registered by another doctor", "email")
        
        elif user_type == "patient":
            # Check if email exists in doctors
            if self.doctor_repository.email_exists(email):
                result.add_error("Email address is already registered by a doctor", "email")
            # Check if email exists in other patients
            if self.patient_repository.email_exists(email, exclude_id=exclude_user_id):
                result.add_error("Email address is already registered by another patient", "email")
        
        return result
    
    def validate_update_rate_limiting(self, user_id: UUID, user_type: str) -> ValidationResult:
        """Validate update rate limiting (simplified)."""
        result = ValidationResult(is_valid=True, errors=[])
        
        # In a real implementation, you'd track update history
        # For demo purposes, we'll use a simplified check
        
        # Simplified: assume max 5 updates per day per user
        # This would require an update history table in a real implementation
        
        return result
    
    def validate_concurrent_updates(self, user_id: UUID, user_type: str,
                                  last_updated: datetime) -> ValidationResult:
        """Validate against concurrent updates (optimistic locking)."""
        result = ValidationResult(is_valid=True, errors=[])
        
        # Get current user data
        if user_type == "doctor":
            current_user = self.doctor_repository.find_by_id(user_id)
        else:
            current_user = self.patient_repository.find_by_id(user_id)
        
        if current_user and current_user.updated_at > last_updated:
            result.add_error(
                "Profile has been modified by another session. Please refresh and try again.",
                "concurrent_update"
            )
        
        return result


class ProfileValidatorFactory:
    """Factory for creating profile validators."""
    
    @staticmethod
    def create_doctor_validator(doctor_repository: DoctorRepository,
                              specialty_repository: MedicalSpecialtyRepository) -> DoctorProfileUpdateValidator:
        """Create a doctor profile update validator."""
        return DoctorProfileUpdateValidator(doctor_repository, specialty_repository)
    
    @staticmethod
    def create_patient_validator(patient_repository: PatientRepository) -> PatientProfileUpdateValidator:
        """Create a patient profile update validator."""
        return PatientProfileUpdateValidator(patient_repository)
    
    @staticmethod
    def create_business_rules_validator(doctor_repository: DoctorRepository,
                                      patient_repository: PatientRepository) -> ProfileUpdateBusinessRules:
        """Create a business rules validator."""
        return ProfileUpdateBusinessRules(doctor_repository, patient_repository)