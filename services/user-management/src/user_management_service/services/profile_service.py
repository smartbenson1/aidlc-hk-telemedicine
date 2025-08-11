"""
Profile Management Service for the User Management Service.
"""

import logging
from typing import Optional, Dict, Any
from uuid import UUID

from ..models.doctor import Doctor
from ..models.patient import Patient
from ..repositories.doctor_repository import DoctorRepository
from ..repositories.patient_repository import PatientRepository
from ..repositories.specialty_repository import MedicalSpecialtyRepository
from ..repositories.session_repository import UserSessionRepository
from ..requests.profile_update_requests import (
    DoctorProfileUpdateRequest, PatientProfileUpdateRequest, ProfileUpdateResult
)
from ..requests.response_models import DoctorProfileView, PatientProfileView
from ..validators.profile_validators import (
    DoctorProfileUpdateValidator, PatientProfileUpdateValidator, ProfileUpdateBusinessRules
)
from ..events.event_publisher import get_event_publisher
from ..utils.base_models import ServiceResult, ProfileChanges
from ..utils.exceptions import (
    ProfileUpdateError, ValidationError, NotFoundError, PermissionError
)

logger = logging.getLogger(__name__)


class ProfileManagementService:
    """Service for handling profile management operations."""
    
    def __init__(self, doctor_repository: DoctorRepository,
                 patient_repository: PatientRepository,
                 specialty_repository: MedicalSpecialtyRepository,
                 session_repository: UserSessionRepository):
        """Initialize the profile management service."""
        self.doctor_repository = doctor_repository
        self.patient_repository = patient_repository
        self.specialty_repository = specialty_repository
        self.session_repository = session_repository
        self.event_publisher = get_event_publisher()
        
        # Initialize validators
        self.doctor_validator = DoctorProfileUpdateValidator(
            doctor_repository, specialty_repository
        )
        self.patient_validator = PatientProfileUpdateValidator(patient_repository)
        self.business_rules = ProfileUpdateBusinessRules(
            doctor_repository, patient_repository
        )
    
    def get_doctor_profile(self, doctor_id: UUID, session_id: Optional[UUID] = None) -> ServiceResult:
        """Get doctor profile information."""
        try:
            # Validate session if provided
            if session_id:
                self._validate_session_access(session_id, doctor_id, "doctor")
            
            # Get doctor
            doctor = self.doctor_repository.find_by_id(doctor_id)
            if not doctor:
                return ServiceResult.error_result(
                    "Doctor not found",
                    "NOT_FOUND_ERROR"
                )
            
            # Get specialty details
            specialty_details = self.specialty_repository.get_specialty_details(doctor.specialties)
            
            # Create profile view
            profile_view = DoctorProfileView(
                id=doctor.id,
                name=doctor.name,
                email=doctor.email,
                phone=doctor.phone,
                location=doctor.location,
                specialties=specialty_details,
                experience=doctor.experience,
                rating=doctor.rating,
                status=doctor.status,
                created_at=doctor.created_at,
                updated_at=doctor.updated_at
            )
            
            return ServiceResult.success_result(profile_view)
            
        except PermissionError as e:
            return ServiceResult.error_result(
                f"Access denied: {e.message}",
                "PERMISSION_ERROR"
            )
        except Exception as e:
            logger.error(f"Failed to get doctor profile: {str(e)}")
            return ServiceResult.error_result(
                "Failed to retrieve doctor profile",
                "INTERNAL_ERROR"
            )
    
    def get_patient_profile(self, patient_id: UUID, session_id: Optional[UUID] = None) -> ServiceResult:
        """Get patient profile information."""
        try:
            # Validate session if provided
            if session_id:
                self._validate_session_access(session_id, patient_id, "patient")
            
            # Get patient
            patient = self.patient_repository.find_by_id(patient_id)
            if not patient:
                return ServiceResult.error_result(
                    "Patient not found",
                    "NOT_FOUND_ERROR"
                )
            
            # Create profile view
            profile_view = PatientProfileView(
                id=patient.id,
                name=patient.name,
                email=patient.email,
                phone=patient.phone,
                medical_history=patient.medical_history,
                emergency_contact=patient.get_emergency_contact_info(),
                status=patient.status,
                created_at=patient.created_at,
                updated_at=patient.updated_at
            )
            
            return ServiceResult.success_result(profile_view)
            
        except PermissionError as e:
            return ServiceResult.error_result(
                f"Access denied: {e.message}",
                "PERMISSION_ERROR"
            )
        except Exception as e:
            logger.error(f"Failed to get patient profile: {str(e)}")
            return ServiceResult.error_result(
                "Failed to retrieve patient profile",
                "INTERNAL_ERROR"
            )
    
    def update_doctor_profile(self, doctor_id: UUID, request: DoctorProfileUpdateRequest,
                            session_id: Optional[UUID] = None) -> ServiceResult:
        """Update doctor profile."""
        try:
            logger.info(f"Starting doctor profile update for ID: {doctor_id}")
            
            # Validate session and permissions
            requester_id = doctor_id
            if session_id:
                requester_id = self._validate_session_access(session_id, doctor_id, "doctor")
            
            # Get current doctor
            current_doctor = self.doctor_repository.find_by_id(doctor_id)
            if not current_doctor:
                return ServiceResult.error_result(
                    "Doctor not found",
                    "NOT_FOUND_ERROR"
                )
            
            # Validate the update request
            self._validate_doctor_profile_update(request, current_doctor, requester_id)
            
            # Track changes
            changes = self._track_doctor_profile_changes(current_doctor, request)
            
            # Apply updates
            updated_doctor = self._apply_doctor_profile_updates(current_doctor, request)
            
            # Save to repository
            saved_doctor = self.doctor_repository.update_with_email_check(updated_doctor)
            logger.info(f"Doctor profile updated: {saved_doctor.id}")
            
            # Publish profile update event
            if changes.changed_fields:
                self._publish_doctor_profile_update_event(saved_doctor, changes, requester_id)
            
            # Return success result
            return ServiceResult.success_result(
                ProfileUpdateResult.success_result(
                    saved_doctor.id,
                    changes.changed_fields,
                    "Doctor profile updated successfully"
                )
            )
            
        except ValidationError as e:
            logger.warning(f"Doctor profile update validation failed: {e.message}")
            return ServiceResult.error_result(
                f"Profile update validation failed: {e.message}",
                "VALIDATION_ERROR",
                {"field": e.field}
            )
        
        except PermissionError as e:
            return ServiceResult.error_result(
                f"Access denied: {e.message}",
                "PERMISSION_ERROR"
            )
        
        except Exception as e:
            logger.error(f"Doctor profile update failed: {str(e)}")
            return ServiceResult.error_result(
                "Profile update failed due to an internal error",
                "INTERNAL_ERROR"
            )
    
    def update_patient_profile(self, patient_id: UUID, request: PatientProfileUpdateRequest,
                             session_id: Optional[UUID] = None) -> ServiceResult:
        """Update patient profile."""
        try:
            logger.info(f"Starting patient profile update for ID: {patient_id}")
            
            # Validate session and permissions
            requester_id = patient_id
            if session_id:
                requester_id = self._validate_session_access(session_id, patient_id, "patient")
            
            # Get current patient
            current_patient = self.patient_repository.find_by_id(patient_id)
            if not current_patient:
                return ServiceResult.error_result(
                    "Patient not found",
                    "NOT_FOUND_ERROR"
                )
            
            # Validate the update request
            self._validate_patient_profile_update(request, current_patient, requester_id)
            
            # Track changes
            changes = self._track_patient_profile_changes(current_patient, request)
            
            # Apply updates
            updated_patient = self._apply_patient_profile_updates(current_patient, request)
            
            # Save to repository
            saved_patient = self.patient_repository.update_with_uniqueness_check(updated_patient)
            logger.info(f"Patient profile updated: {saved_patient.id}")
            
            # Publish profile update event
            if changes.changed_fields:
                self._publish_patient_profile_update_event(saved_patient, changes, requester_id)
            
            # Return success result
            return ServiceResult.success_result(
                ProfileUpdateResult.success_result(
                    saved_patient.id,
                    changes.changed_fields,
                    "Patient profile updated successfully"
                )
            )
            
        except ValidationError as e:
            logger.warning(f"Patient profile update validation failed: {e.message}")
            return ServiceResult.error_result(
                f"Profile update validation failed: {e.message}",
                "VALIDATION_ERROR",
                {"field": e.field}
            )
        
        except PermissionError as e:
            return ServiceResult.error_result(
                f"Access denied: {e.message}",
                "PERMISSION_ERROR"
            )
        
        except Exception as e:
            logger.error(f"Patient profile update failed: {str(e)}")
            return ServiceResult.error_result(
                "Profile update failed due to an internal error",
                "INTERNAL_ERROR"
            )
    
    def _validate_session_access(self, session_id: UUID, user_id: UUID, user_type: str) -> UUID:
        """Validate session access and return requester ID."""
        session_validation = self.session_repository.validate_session(session_id)
        
        if not session_validation['is_valid']:
            raise PermissionError(
                session_validation['error'] or "Invalid session",
                session_id
            )
        
        # For now, assume users can only access their own profiles
        # In a real implementation, you might have admin users who can access any profile
        session_user_id = session_validation['user_id']
        if session_user_id != user_id:
            raise PermissionError(
                "You can only access your own profile",
                session_user_id
            )
        
        return session_user_id
    
    def _validate_doctor_profile_update(self, request: DoctorProfileUpdateRequest,
                                      current_doctor: Doctor, requester_id: UUID) -> None:
        """Validate doctor profile update request."""
        # Basic validation
        self.doctor_validator.validate_and_throw(request, current_doctor)
        
        # Permission validation
        permission_validation = self.doctor_validator.validate_update_permissions(
            current_doctor.id, requester_id
        )
        if not permission_validation.is_valid:
            raise PermissionError(
                f"Permission denied: {'; '.join(permission_validation.errors)}",
                requester_id
            )
        
        # Cross-user email uniqueness (if email is being updated)
        if request.email is not None:
            email_validation = self.business_rules.validate_cross_user_email_uniqueness(
                request.email, "doctor", current_doctor.id
            )
            if not email_validation.is_valid:
                raise ValidationError(
                    f"Email validation failed: {'; '.join(email_validation.errors)}",
                    "email"
                )
    
    def _validate_patient_profile_update(self, request: PatientProfileUpdateRequest,
                                       current_patient: Patient, requester_id: UUID) -> None:
        """Validate patient profile update request."""
        # Basic validation
        self.patient_validator.validate_and_throw(request, current_patient)
        
        # Permission validation
        permission_validation = self.patient_validator.validate_update_permissions(
            current_patient.id, requester_id
        )
        if not permission_validation.is_valid:
            raise PermissionError(
                f"Permission denied: {'; '.join(permission_validation.errors)}",
                requester_id
            )
        
        # Cross-user email uniqueness (if email is being updated)
        if request.email is not None:
            email_validation = self.business_rules.validate_cross_user_email_uniqueness(
                request.email, "patient", current_patient.id
            )
            if not email_validation.is_valid:
                raise ValidationError(
                    f"Email validation failed: {'; '.join(email_validation.errors)}",
                    "email"
                )
    
    def _track_doctor_profile_changes(self, current_doctor: Doctor,
                                    request: DoctorProfileUpdateRequest) -> ProfileChanges:
        """Track changes being made to doctor profile."""
        changes = ProfileChanges()
        
        if request.name is not None and request.name != current_doctor.name:
            changes.add_change("name", current_doctor.name, request.name)
        
        if request.email is not None and request.email != current_doctor.email:
            changes.add_change("email", current_doctor.email, request.email)
        
        if request.phone is not None and request.phone != current_doctor.phone:
            changes.add_change("phone", current_doctor.phone, request.phone)
        
        if request.location is not None and request.location != current_doctor.location:
            changes.add_change("location", current_doctor.location, request.location)
        
        if request.specialties is not None and request.specialties != current_doctor.specialties:
            changes.add_change("specialties", current_doctor.specialties, request.specialties)
        
        if request.experience is not None and request.experience != current_doctor.experience:
            changes.add_change("experience", current_doctor.experience, request.experience)
        
        return changes
    
    def _track_patient_profile_changes(self, current_patient: Patient,
                                     request: PatientProfileUpdateRequest) -> ProfileChanges:
        """Track changes being made to patient profile."""
        changes = ProfileChanges()
        
        if request.name is not None and request.name != current_patient.name:
            changes.add_change("name", current_patient.name, request.name)
        
        if request.email is not None and request.email != current_patient.email:
            changes.add_change("email", current_patient.email, request.email)
        
        if request.phone is not None and request.phone != current_patient.phone:
            changes.add_change("phone", current_patient.phone, request.phone)
        
        if request.medical_history is not None and request.medical_history != current_patient.medical_history:
            changes.add_change("medical_history", current_patient.medical_history, request.medical_history)
        
        if request.emergency_contact_name is not None and request.emergency_contact_name != current_patient.emergency_contact_name:
            changes.add_change("emergency_contact_name", current_patient.emergency_contact_name, request.emergency_contact_name)
        
        if request.emergency_contact_phone is not None and request.emergency_contact_phone != current_patient.emergency_contact_phone:
            changes.add_change("emergency_contact_phone", current_patient.emergency_contact_phone, request.emergency_contact_phone)
        
        if request.emergency_contact_relationship is not None and request.emergency_contact_relationship != current_patient.emergency_contact_relationship:
            changes.add_change("emergency_contact_relationship", current_patient.emergency_contact_relationship, request.emergency_contact_relationship)
        
        return changes
    
    def _apply_doctor_profile_updates(self, doctor: Doctor,
                                    request: DoctorProfileUpdateRequest) -> Doctor:
        """Apply updates to doctor profile."""
        if request.name is not None:
            doctor.name = request.name
        
        if request.email is not None:
            doctor.email = request.email
        
        if request.phone is not None:
            doctor.phone = request.phone
        
        if request.location is not None:
            doctor.location = request.location
        
        if request.specialties is not None:
            doctor.specialties = request.specialties
        
        if request.experience is not None:
            doctor.experience = request.experience
        
        doctor.update_timestamp()
        return doctor
    
    def _apply_patient_profile_updates(self, patient: Patient,
                                     request: PatientProfileUpdateRequest) -> Patient:
        """Apply updates to patient profile."""
        if request.name is not None:
            patient.name = request.name
        
        if request.email is not None:
            patient.email = request.email
        
        if request.phone is not None:
            patient.phone = request.phone
        
        if request.medical_history is not None:
            patient.medical_history = request.medical_history
        
        if request.emergency_contact_name is not None:
            patient.emergency_contact_name = request.emergency_contact_name
        
        if request.emergency_contact_phone is not None:
            patient.emergency_contact_phone = request.emergency_contact_phone
        
        if request.emergency_contact_relationship is not None:
            patient.emergency_contact_relationship = request.emergency_contact_relationship
        
        patient.update_timestamp()
        return patient
    
    def _publish_doctor_profile_update_event(self, doctor: Doctor, changes: ProfileChanges,
                                           updated_by: UUID) -> None:
        """Publish doctor profile update event."""
        try:
            self.event_publisher.publish_profile_update_event(
                doctor.id, "doctor", changes.previous_values, changes.new_values, updated_by
            )
        except Exception as e:
            logger.error(f"Failed to publish doctor profile update event: {str(e)}")
    
    def _publish_patient_profile_update_event(self, patient: Patient, changes: ProfileChanges,
                                            updated_by: UUID) -> None:
        """Publish patient profile update event."""
        try:
            self.event_publisher.publish_profile_update_event(
                patient.id, "patient", changes.previous_values, changes.new_values, updated_by
            )
        except Exception as e:
            logger.error(f"Failed to publish patient profile update event: {str(e)}")