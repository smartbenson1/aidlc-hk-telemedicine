"""
User Registration Service for the User Management Service.
"""

import logging
from typing import Optional
from uuid import UUID

from ..models.doctor import Doctor
from ..models.patient import Patient
from ..repositories.doctor_repository import DoctorRepository
from ..repositories.patient_repository import PatientRepository
from ..repositories.specialty_repository import MedicalSpecialtyRepository
from ..requests.registration_requests import (
    DoctorRegistrationRequest, PatientRegistrationRequest, RegistrationResult
)
from ..validators.registration_validators import (
    DoctorRegistrationValidator, PatientRegistrationValidator, RegistrationBusinessRules
)
from ..integrations.email_service import EmailServiceIntegration
from ..events.event_publisher import get_event_publisher
from ..utils.base_models import ServiceResult
from ..utils.exceptions import (
    RegistrationError, ValidationError, BusinessRuleError, IntegrationError
)

logger = logging.getLogger(__name__)


class UserRegistrationService:
    """Service for handling user registration operations."""
    
    def __init__(self, doctor_repository: DoctorRepository,
                 patient_repository: PatientRepository,
                 specialty_repository: MedicalSpecialtyRepository,
                 email_service: EmailServiceIntegration):
        """Initialize the registration service."""
        self.doctor_repository = doctor_repository
        self.patient_repository = patient_repository
        self.specialty_repository = specialty_repository
        self.email_service = email_service
        self.event_publisher = get_event_publisher()
        
        # Initialize validators
        self.doctor_validator = DoctorRegistrationValidator(
            doctor_repository, specialty_repository
        )
        self.patient_validator = PatientRegistrationValidator(patient_repository)
        self.business_rules = RegistrationBusinessRules(
            doctor_repository, patient_repository
        )
    
    def register_doctor(self, request: DoctorRegistrationRequest) -> ServiceResult:
        """Register a new doctor."""
        try:
            logger.info(f"Starting doctor registration for email: {request.email}")
            
            # Validate the registration request
            self._validate_doctor_registration(request)
            
            # Create doctor entity
            doctor = self._create_doctor_from_request(request)
            
            # Save to repository
            created_doctor = self.doctor_repository.create_with_email_check(doctor)
            logger.info(f"Doctor created with ID: {created_doctor.id}")
            
            # Send confirmation email
            self._send_doctor_confirmation_email(created_doctor)
            
            # Publish registration event
            self._publish_doctor_registration_event(created_doctor)
            
            # Return success result
            return ServiceResult.success_result(
                RegistrationResult.success_result(
                    created_doctor.id,
                    created_doctor.email,
                    "doctor",
                    "Doctor registration completed successfully"
                )
            )
            
        except ValidationError as e:
            logger.warning(f"Doctor registration validation failed: {e.message}")
            return ServiceResult.error_result(
                f"Registration validation failed: {e.message}",
                "VALIDATION_ERROR",
                {"field": e.field, "value": e.value}
            )
        
        except BusinessRuleError as e:
            logger.warning(f"Doctor registration business rule violation: {e.message}")
            return ServiceResult.error_result(
                f"Registration failed: {e.message}",
                "BUSINESS_RULE_ERROR",
                {"rule": e.rule}
            )
        
        except Exception as e:
            logger.error(f"Doctor registration failed: {str(e)}")
            return ServiceResult.error_result(
                "Registration failed due to an internal error",
                "INTERNAL_ERROR"
            )
    
    def register_patient(self, request: PatientRegistrationRequest) -> ServiceResult:
        """Register a new patient."""
        try:
            logger.info(f"Starting patient registration for email: {request.email}")
            
            # Validate the registration request
            self._validate_patient_registration(request)
            
            # Create patient entity
            patient = self._create_patient_from_request(request)
            
            # Save to repository
            created_patient = self.patient_repository.create_with_uniqueness_check(patient)
            logger.info(f"Patient created with ID: {created_patient.id}")
            
            # Send confirmation email
            self._send_patient_confirmation_email(created_patient)
            
            # Publish registration event
            self._publish_patient_registration_event(created_patient)
            
            # Return success result
            return ServiceResult.success_result(
                RegistrationResult.success_result(
                    created_patient.id,
                    created_patient.email,
                    "patient",
                    "Patient registration completed successfully"
                )
            )
            
        except ValidationError as e:
            logger.warning(f"Patient registration validation failed: {e.message}")
            return ServiceResult.error_result(
                f"Registration validation failed: {e.message}",
                "VALIDATION_ERROR",
                {"field": e.field, "value": e.value}
            )
        
        except BusinessRuleError as e:
            logger.warning(f"Patient registration business rule violation: {e.message}")
            return ServiceResult.error_result(
                f"Registration failed: {e.message}",
                "BUSINESS_RULE_ERROR",
                {"rule": e.rule}
            )
        
        except Exception as e:
            logger.error(f"Patient registration failed: {str(e)}")
            return ServiceResult.error_result(
                "Registration failed due to an internal error",
                "INTERNAL_ERROR"
            )
    
    def check_email_availability(self, email: str, user_type: str) -> ServiceResult:
        """Check if an email is available for registration."""
        try:
            # Check cross-user email uniqueness
            validation_result = self.business_rules.validate_cross_user_email_uniqueness(
                email, user_type, None
            )
            
            is_available = validation_result.is_valid
            message = "Email is available" if is_available else "Email is already registered"
            
            return ServiceResult.success_result({
                "email": email,
                "is_available": is_available,
                "message": message,
                "errors": validation_result.errors if not is_available else []
            })
            
        except Exception as e:
            logger.error(f"Email availability check failed: {str(e)}")
            return ServiceResult.error_result(
                "Failed to check email availability",
                "INTERNAL_ERROR"
            )
    
    def _validate_doctor_registration(self, request: DoctorRegistrationRequest) -> None:
        """Validate doctor registration request."""
        # Basic validation
        self.doctor_validator.validate_and_throw(request)
        
        # Cross-user email uniqueness
        email_validation = self.business_rules.validate_cross_user_email_uniqueness(
            request.email, "doctor"
        )
        if not email_validation.is_valid:
            raise ValidationError(
                f"Email validation failed: {'; '.join(email_validation.errors)}",
                "email"
            )
        
        # Daily registration limits
        limits_validation = self.business_rules.validate_daily_registration_limits("doctor")
        if not limits_validation.is_valid:
            raise BusinessRuleError(
                f"Registration limits exceeded: {'; '.join(limits_validation.errors)}",
                "daily_limit"
            )
        
        # System capacity
        capacity_validation = self.business_rules.validate_system_capacity()
        if not capacity_validation.is_valid:
            raise BusinessRuleError(
                f"System capacity exceeded: {'; '.join(capacity_validation.errors)}",
                "system_capacity"
            )
    
    def _validate_patient_registration(self, request: PatientRegistrationRequest) -> None:
        """Validate patient registration request."""
        # Basic validation
        self.patient_validator.validate_and_throw(request)
        
        # Cross-user email uniqueness
        email_validation = self.business_rules.validate_cross_user_email_uniqueness(
            request.email, "patient"
        )
        if not email_validation.is_valid:
            raise ValidationError(
                f"Email validation failed: {'; '.join(email_validation.errors)}",
                "email"
            )
        
        # Daily registration limits
        limits_validation = self.business_rules.validate_daily_registration_limits("patient")
        if not limits_validation.is_valid:
            raise BusinessRuleError(
                f"Registration limits exceeded: {'; '.join(limits_validation.errors)}",
                "daily_limit"
            )
        
        # System capacity
        capacity_validation = self.business_rules.validate_system_capacity()
        if not capacity_validation.is_valid:
            raise BusinessRuleError(
                f"System capacity exceeded: {'; '.join(capacity_validation.errors)}",
                "system_capacity"
            )
    
    def _create_doctor_from_request(self, request: DoctorRegistrationRequest) -> Doctor:
        """Create a doctor entity from registration request."""
        doctor = Doctor(
            name=request.name,
            email=request.email,
            phone=request.phone,
            location=request.location,
            specialties=request.specialties,
            experience=request.experience,
            rating=0.0  # Initial rating
        )
        return doctor
    
    def _create_patient_from_request(self, request: PatientRegistrationRequest) -> Patient:
        """Create a patient entity from registration request."""
        patient = Patient(
            name=request.name,
            email=request.email,
            phone=request.phone,
            medical_history=request.medical_history or "",
            emergency_contact_name=request.emergency_contact_name,
            emergency_contact_phone=request.emergency_contact_phone,
            emergency_contact_relationship=request.emergency_contact_relationship
        )
        return patient
    
    def _send_doctor_confirmation_email(self, doctor: Doctor) -> None:
        """Send confirmation email to registered doctor."""
        try:
            email_result = self.email_service.send_registration_confirmation(doctor, "doctor")
            if not email_result.success:
                logger.warning(f"Failed to send confirmation email to doctor {doctor.email}: {email_result.error_message}")
        except Exception as e:
            logger.error(f"Error sending confirmation email to doctor {doctor.email}: {str(e)}")
    
    def _send_patient_confirmation_email(self, patient: Patient) -> None:
        """Send confirmation email to registered patient."""
        try:
            email_result = self.email_service.send_registration_confirmation(patient, "patient")
            if not email_result.success:
                logger.warning(f"Failed to send confirmation email to patient {patient.email}: {email_result.error_message}")
        except Exception as e:
            logger.error(f"Error sending confirmation email to patient {patient.email}: {str(e)}")
    
    def _publish_doctor_registration_event(self, doctor: Doctor) -> None:
        """Publish doctor registration event."""
        try:
            # Publish to existing event system
            self.event_publisher.publish_user_registration_event(
                doctor.id, "doctor", doctor.email, doctor.name
            )
            
            # Sync to appointment matching service via HTTP
            from ..integrations.appointment_matching_sync import AppointmentMatchingSyncClient
            sync_client = AppointmentMatchingSyncClient()
            sync_success = sync_client.sync_doctor_registration(doctor)
            
            if sync_success:
                logger.info(f"Successfully synced doctor {doctor.id} to appointment matching service")
            else:
                logger.warning(f"Failed to sync doctor {doctor.id} to appointment matching service")
            
        except Exception as e:
            logger.error(f"Failed to publish doctor registration event: {str(e)}")
    
    def _publish_patient_registration_event(self, patient: Patient) -> None:
        """Publish patient registration event."""
        try:
            self.event_publisher.publish_user_registration_event(
                patient.id, "patient", patient.email, patient.name
            )
        except Exception as e:
            logger.error(f"Failed to publish patient registration event: {str(e)}")
    
    def get_registration_statistics(self) -> ServiceResult:
        """Get registration statistics."""
        try:
            doctor_stats = self.doctor_repository.get_statistics()
            patient_stats = self.patient_repository.get_statistics()
            
            stats = {
                "doctors": doctor_stats,
                "patients": patient_stats,
                "total_users": doctor_stats["total_doctors"] + patient_stats["total_patients"],
                "active_users": doctor_stats["active_doctors"] + patient_stats["active_patients"]
            }
            
            return ServiceResult.success_result(stats)
            
        except Exception as e:
            logger.error(f"Failed to get registration statistics: {str(e)}")
            return ServiceResult.error_result(
                "Failed to retrieve registration statistics",
                "INTERNAL_ERROR"
            )