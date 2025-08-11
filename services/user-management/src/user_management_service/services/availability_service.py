"""
Availability Management Service for the User Management Service.
"""

import logging
from datetime import datetime
from typing import Optional, List
from uuid import UUID

from ..models.doctor_availability import DoctorAvailability
from ..repositories.doctor_repository import DoctorRepository
from ..repositories.availability_repository import DoctorAvailabilityRepository
from ..repositories.specialty_repository import MedicalSpecialtyRepository
from ..repositories.session_repository import UserSessionRepository
from ..requests.availability_requests import (
    TimeSlotRequest, TimeSlotUpdateRequest, AvailabilityQueryRequest, 
    AvailabilityResult, BulkAvailabilityRequest
)
from ..requests.response_models import DoctorAvailabilityResponse, AvailableSlotResponse
from ..validators.availability_validators import (
    TimeSlotCreationValidator, TimeSlotModificationValidator, BulkAvailabilityValidator
)
from ..integrations.appointment_service import AppointmentServiceIntegration
from ..events.event_publisher import get_event_publisher
from ..utils.base_models import ServiceResult
from ..utils.exceptions import (
    AvailabilityError, ValidationError, NotFoundError, PermissionError, BusinessRuleError
)
from ..utils.enums import ChangeType

logger = logging.getLogger(__name__)


class AvailabilityManagementService:
    """Service for handling doctor availability management operations."""
    
    def __init__(self, doctor_repository: DoctorRepository,
                 availability_repository: DoctorAvailabilityRepository,
                 specialty_repository: MedicalSpecialtyRepository,
                 session_repository: UserSessionRepository,
                 appointment_service: AppointmentServiceIntegration):
        """Initialize the availability management service."""
        self.doctor_repository = doctor_repository
        self.availability_repository = availability_repository
        self.specialty_repository = specialty_repository
        self.session_repository = session_repository
        self.appointment_service = appointment_service
        self.event_publisher = get_event_publisher()
        
        # Initialize validators
        self.creation_validator = TimeSlotCreationValidator(
            doctor_repository, availability_repository, specialty_repository
        )
        self.modification_validator = TimeSlotModificationValidator(
            doctor_repository, availability_repository, specialty_repository
        )
        self.bulk_validator = BulkAvailabilityValidator(
            doctor_repository, availability_repository, specialty_repository
        )
    
    def add_time_slot(self, doctor_id: UUID, request: TimeSlotRequest,
                     session_id: Optional[UUID] = None) -> ServiceResult:
        """Add a new time slot for a doctor."""
        try:
            logger.info(f"Adding time slot for doctor {doctor_id} at {request.datetime}")
            
            # Validate session and permissions
            if session_id:
                self._validate_session_access(session_id, doctor_id)
            
            # Validate the time slot request
            self._validate_time_slot_creation(request, doctor_id)
            
            # Check for appointment conflicts
            self._validate_no_appointment_conflicts(doctor_id, request.datetime)
            
            # Create availability entity
            availability = self._create_availability_from_request(doctor_id, request)
            
            # Save to repository with business rules
            created_availability = self.availability_repository.create_with_business_rules(availability)
            logger.info(f"Time slot created with ID: {created_availability.id}")
            
            # Publish availability update event
            self._publish_availability_update_event(
                doctor_id, created_availability.id, ChangeType.ADDED,
                None, created_availability.to_dict(), doctor_id
            )
            
            # Return success result
            return ServiceResult.success_result(
                AvailabilityResult.success_result(
                    doctor_id,
                    "create",
                    created_availability.id,
                    "Time slot added successfully"
                )
            )
            
        except ValidationError as e:
            logger.warning(f"Time slot creation validation failed: {e.message}")
            return ServiceResult.error_result(
                f"Time slot validation failed: {e.message}",
                "VALIDATION_ERROR",
                {"field": e.field}
            )
        
        except BusinessRuleError as e:
            logger.warning(f"Time slot creation business rule violation: {e.message}")
            return ServiceResult.error_result(
                f"Time slot creation failed: {e.message}",
                "BUSINESS_RULE_ERROR",
                {"rule": e.rule}
            )
        
        except Exception as e:
            logger.error(f"Time slot creation failed: {str(e)}")
            return ServiceResult.error_result(
                "Time slot creation failed due to an internal error",
                "INTERNAL_ERROR"
            )
    
    def modify_time_slot(self, doctor_id: UUID, slot_id: UUID, request: TimeSlotUpdateRequest,
                        session_id: Optional[UUID] = None) -> ServiceResult:
        """Modify an existing time slot."""
        try:
            logger.info(f"Modifying time slot {slot_id} for doctor {doctor_id}")
            
            # Validate session and permissions
            if session_id:
                self._validate_session_access(session_id, doctor_id)
            
            # Get current slot
            current_slot = self.availability_repository.find_by_id(slot_id)
            if not current_slot:
                return ServiceResult.error_result(
                    "Time slot not found",
                    "NOT_FOUND_ERROR"
                )
            
            # Validate the modification request
            self._validate_time_slot_modification(slot_id, request, doctor_id)
            
            # Store previous state for event
            previous_data = current_slot.to_dict()
            
            # Apply updates
            updated_slot = self._apply_time_slot_updates(current_slot, request)
            
            # Save to repository
            saved_slot = self.availability_repository.update(updated_slot)
            logger.info(f"Time slot modified: {saved_slot.id}")
            
            # Publish availability update event
            self._publish_availability_update_event(
                doctor_id, saved_slot.id, ChangeType.MODIFIED,
                previous_data, saved_slot.to_dict(), doctor_id
            )
            
            # Return success result
            return ServiceResult.success_result(
                AvailabilityResult.success_result(
                    doctor_id,
                    "update",
                    saved_slot.id,
                    "Time slot modified successfully"
                )
            )
            
        except ValidationError as e:
            logger.warning(f"Time slot modification validation failed: {e.message}")
            return ServiceResult.error_result(
                f"Time slot modification validation failed: {e.message}",
                "VALIDATION_ERROR",
                {"field": e.field}
            )
        
        except Exception as e:
            logger.error(f"Time slot modification failed: {str(e)}")
            return ServiceResult.error_result(
                "Time slot modification failed due to an internal error",
                "INTERNAL_ERROR"
            )
    
    def remove_time_slot(self, doctor_id: UUID, slot_id: UUID,
                        session_id: Optional[UUID] = None) -> ServiceResult:
        """Remove a time slot."""
        try:
            logger.info(f"Removing time slot {slot_id} for doctor {doctor_id}")
            
            # Validate session and permissions
            if session_id:
                self._validate_session_access(session_id, doctor_id)
            
            # Get current slot
            current_slot = self.availability_repository.find_by_id(slot_id)
            if not current_slot:
                return ServiceResult.error_result(
                    "Time slot not found",
                    "NOT_FOUND_ERROR"
                )
            
            # Validate deletion permissions
            self._validate_time_slot_deletion(slot_id, doctor_id)
            
            # Store previous state for event
            previous_data = current_slot.to_dict()
            
            # Remove from repository
            deleted = self.availability_repository.delete(slot_id)
            if not deleted:
                return ServiceResult.error_result(
                    "Failed to remove time slot",
                    "INTERNAL_ERROR"
                )
            
            logger.info(f"Time slot removed: {slot_id}")
            
            # Publish availability update event
            self._publish_availability_update_event(
                doctor_id, slot_id, ChangeType.REMOVED,
                previous_data, None, doctor_id
            )
            
            # Return success result
            return ServiceResult.success_result(
                AvailabilityResult.success_result(
                    doctor_id,
                    "delete",
                    slot_id,
                    "Time slot removed successfully"
                )
            )
            
        except ValidationError as e:
            logger.warning(f"Time slot deletion validation failed: {e.message}")
            return ServiceResult.error_result(
                f"Time slot deletion validation failed: {e.message}",
                "VALIDATION_ERROR"
            )
        
        except Exception as e:
            logger.error(f"Time slot deletion failed: {str(e)}")
            return ServiceResult.error_result(
                "Time slot deletion failed due to an internal error",
                "INTERNAL_ERROR"
            )
    
    def get_doctor_availability(self, query: AvailabilityQueryRequest) -> ServiceResult:
        """Get doctor availability based on query parameters."""
        try:
            # Validate query
            validation_result = query.validate()
            if not validation_result.is_valid:
                return ServiceResult.error_result(
                    f"Query validation failed: {'; '.join(validation_result.errors)}",
                    "VALIDATION_ERROR"
                )
            
            # Get availability slots
            if query.available_only:
                slots = self.availability_repository.search_available_slots({
                    'doctor_id': query.doctor_id,
                    'start_date': query.start_date,
                    'end_date': query.end_date,
                    'appointment_type': query.appointment_type,
                    'specialty_id': query.specialty_id,
                    'future_only': True
                })
            else:
                slots = self.availability_repository.find_by_doctor_and_date_range(
                    query.doctor_id, query.start_date, query.end_date
                )
            
            # Convert to response models
            response_slots = []
            for slot in slots:
                specialty_details = self.specialty_repository.get_specialty_details([slot.specialty_id])
                specialty = specialty_details[0] if specialty_details else {"id": str(slot.specialty_id), "name": "Unknown"}
                
                if query.available_only:
                    response_slot = AvailableSlotResponse(
                        id=slot.id,
                        doctor_id=slot.doctor_id,
                        datetime=slot.datetime,
                        appointment_type=slot.appointment_type,
                        specialty=specialty
                    )
                else:
                    response_slot = DoctorAvailabilityResponse(
                        id=slot.id,
                        doctor_id=slot.doctor_id,
                        datetime=slot.datetime,
                        appointment_type=slot.appointment_type,
                        specialty=specialty,
                        status=slot.status,
                        created_at=slot.created_at,
                        updated_at=slot.updated_at
                    )
                
                response_slots.append(response_slot)
            
            return ServiceResult.success_result(response_slots)
            
        except Exception as e:
            logger.error(f"Failed to get doctor availability: {str(e)}")
            return ServiceResult.error_result(
                "Failed to retrieve doctor availability",
                "INTERNAL_ERROR"
            )
    
    def bulk_add_time_slots(self, request: BulkAvailabilityRequest,
                           session_id: Optional[UUID] = None) -> ServiceResult:
        """Add multiple time slots at once."""
        try:
            logger.info(f"Bulk adding {len(request.time_slots)} time slots for doctor {request.doctor_id}")
            
            # Validate session and permissions
            if session_id:
                self._validate_session_access(session_id, request.doctor_id)
            
            # Validate the bulk request
            self._validate_bulk_availability_request(request)
            
            # Create availability entities
            created_slots = []
            for slot_request in request.time_slots:
                # Check for appointment conflicts
                self._validate_no_appointment_conflicts(request.doctor_id, slot_request.datetime)
                
                # Create availability entity
                availability = self._create_availability_from_request(request.doctor_id, slot_request)
                
                # Save to repository
                created_availability = self.availability_repository.create_with_business_rules(availability)
                created_slots.append(created_availability)
                
                # Publish availability update event for each slot
                self._publish_availability_update_event(
                    request.doctor_id, created_availability.id, ChangeType.ADDED,
                    None, created_availability.to_dict(), request.doctor_id
                )
            
            logger.info(f"Bulk created {len(created_slots)} time slots")
            
            # Return success result
            return ServiceResult.success_result({
                "doctor_id": str(request.doctor_id),
                "created_slots": len(created_slots),
                "slot_ids": [str(slot.id) for slot in created_slots],
                "message": f"Successfully created {len(created_slots)} time slots"
            })
            
        except ValidationError as e:
            logger.warning(f"Bulk time slot creation validation failed: {e.message}")
            return ServiceResult.error_result(
                f"Bulk time slot validation failed: {e.message}",
                "VALIDATION_ERROR"
            )
        
        except BusinessRuleError as e:
            logger.warning(f"Bulk time slot creation business rule violation: {e.message}")
            return ServiceResult.error_result(
                f"Bulk time slot creation failed: {e.message}",
                "BUSINESS_RULE_ERROR"
            )
        
        except Exception as e:
            logger.error(f"Bulk time slot creation failed: {str(e)}")
            return ServiceResult.error_result(
                "Bulk time slot creation failed due to an internal error",
                "INTERNAL_ERROR"
            )
    
    def _validate_session_access(self, session_id: UUID, doctor_id: UUID) -> UUID:
        """Validate session access for doctor operations."""
        session_validation = self.session_repository.validate_session(session_id)
        
        if not session_validation['is_valid']:
            raise PermissionError(
                session_validation['error'] or "Invalid session",
                session_id
            )
        
        # Ensure the session belongs to the doctor
        session_user_id = session_validation['user_id']
        if session_user_id != doctor_id:
            raise PermissionError(
                "You can only manage your own availability",
                session_user_id
            )
        
        return session_user_id
    
    def _validate_time_slot_creation(self, request: TimeSlotRequest, doctor_id: UUID) -> None:
        """Validate time slot creation request."""
        self.creation_validator.validate_and_throw(request, doctor_id)
    
    def _validate_time_slot_modification(self, slot_id: UUID, request: TimeSlotUpdateRequest,
                                       doctor_id: UUID) -> None:
        """Validate time slot modification request."""
        self.modification_validator.validate_and_throw(slot_id, request, doctor_id)
    
    def _validate_time_slot_deletion(self, slot_id: UUID, doctor_id: UUID) -> None:
        """Validate time slot deletion request."""
        validation_result = self.modification_validator.validate_slot_deletion(slot_id, doctor_id)
        if not validation_result.is_valid:
            raise ValidationError(
                f"Time slot deletion validation failed: {'; '.join(validation_result.errors)}"
            )
    
    def _validate_bulk_availability_request(self, request: BulkAvailabilityRequest) -> None:
        """Validate bulk availability request."""
        self.bulk_validator.validate_and_throw(request)
    
    def _validate_no_appointment_conflicts(self, doctor_id: UUID, datetime_slot: datetime) -> None:
        """Validate that there are no appointment conflicts."""
        try:
            conflict_result = self.appointment_service.check_appointment_conflicts(doctor_id, datetime_slot)
            if conflict_result.has_conflict:
                raise BusinessRuleError(
                    f"Time slot conflicts with existing appointment: {conflict_result.message}",
                    "appointment_conflict"
                )
        except Exception as e:
            logger.warning(f"Could not check appointment conflicts: {str(e)}")
            # In a real implementation, you might want to fail safe or retry
    
    def _create_availability_from_request(self, doctor_id: UUID, request: TimeSlotRequest) -> DoctorAvailability:
        """Create availability entity from request."""
        availability = DoctorAvailability(
            doctor_id=doctor_id,
            datetime=request.datetime,
            appointment_type=request.appointment_type,
            specialty_id=request.specialty_id
        )
        return availability
    
    def _apply_time_slot_updates(self, slot: DoctorAvailability,
                               request: TimeSlotUpdateRequest) -> DoctorAvailability:
        """Apply updates to time slot."""
        if request.appointment_type is not None:
            slot.update_appointment_type(request.appointment_type)
        
        if request.specialty_id is not None:
            slot.update_specialty(request.specialty_id)
        
        return slot
    
    def _publish_availability_update_event(self, doctor_id: UUID, availability_id: UUID,
                                         change_type: ChangeType, previous_data: dict,
                                         new_data: dict, updated_by: UUID) -> None:
        """Publish availability update event."""
        try:
            self.event_publisher.publish_availability_update_event(
                doctor_id, availability_id, change_type.value,
                previous_data, new_data, updated_by
            )
        except Exception as e:
            logger.error(f"Failed to publish availability update event: {str(e)}")
    
    def get_availability_statistics(self, doctor_id: Optional[UUID] = None) -> ServiceResult:
        """Get availability statistics."""
        try:
            if doctor_id:
                # Get statistics for specific doctor
                stats = self.availability_repository.get_doctor_availability_summary(doctor_id)
            else:
                # Get overall statistics
                stats = self.availability_repository.get_statistics()
            
            return ServiceResult.success_result(stats)
            
        except Exception as e:
            logger.error(f"Failed to get availability statistics: {str(e)}")
            return ServiceResult.error_result(
                "Failed to retrieve availability statistics",
                "INTERNAL_ERROR"
            )