"""
Availability validators for the User Management Service.
"""

from datetime import datetime, timedelta
from typing import List, Optional
from uuid import UUID

from ..requests.availability_requests import TimeSlotRequest, TimeSlotUpdateRequest, BulkAvailabilityRequest
from ..repositories.doctor_repository import DoctorRepository
from ..repositories.availability_repository import DoctorAvailabilityRepository
from ..repositories.specialty_repository import MedicalSpecialtyRepository
from ..models.doctor import Doctor
from ..models.doctor_availability import DoctorAvailability
from ..utils.validation_utils import ValidationResult, combine_validation_results
from ..utils.exceptions import ValidationError, BusinessRuleError
from ..utils.enums import MAX_BOOKING_WINDOW_DAYS, MAX_DAILY_SLOTS, MAX_WEEKLY_SLOTS


class TimeSlotCreationValidator:
    """Validator for time slot creation requests."""
    
    def __init__(self, doctor_repository: DoctorRepository,
                 availability_repository: DoctorAvailabilityRepository,
                 specialty_repository: MedicalSpecialtyRepository):
        """Initialize the validator with required repositories."""
        self.doctor_repository = doctor_repository
        self.availability_repository = availability_repository
        self.specialty_repository = specialty_repository
    
    def validate_time_slot_request(self, request: TimeSlotRequest, doctor_id: UUID) -> ValidationResult:
        """Validate a complete time slot creation request."""
        # Basic field validation (already done in request model)
        basic_validation = request.validate()
        if not basic_validation.is_valid:
            return basic_validation
        
        # Get doctor for validation
        doctor = self.doctor_repository.find_by_id(doctor_id)
        if not doctor:
            return ValidationResult(is_valid=False, errors=["Doctor not found"])
        
        # Business rule validations
        validations = [basic_validation]
        
        # Doctor-specific validations
        doctor_validation = self._validate_doctor_requirements(doctor, request)
        validations.append(doctor_validation)
        
        # Specialty validation
        specialty_validation = self._validate_specialty_assignment(request.specialty_id, doctor)
        validations.append(specialty_validation)
        
        # Conflict validation
        conflict_validation = self._validate_time_slot_conflicts(doctor_id, request.datetime)
        validations.append(conflict_validation)
        
        # Business hours validation
        business_hours_validation = self._validate_business_hours(request.datetime)
        validations.append(business_hours_validation)
        
        # Daily and weekly limits validation
        limits_validation = self._validate_slot_limits(doctor_id, request.datetime)
        validations.append(limits_validation)
        
        return combine_validation_results(*validations)
    
    def _validate_doctor_requirements(self, doctor: Doctor, request: TimeSlotRequest) -> ValidationResult:
        """Validate doctor-specific requirements."""
        result = ValidationResult(is_valid=True, errors=[])
        
        # Doctor must be active
        if not doctor.is_active():
            result.add_error("Only active doctors can create availability slots", "doctor_status")
        
        return result
    
    def _validate_specialty_assignment(self, specialty_id: UUID, doctor: Doctor) -> ValidationResult:
        """Validate specialty assignment."""
        result = ValidationResult(is_valid=True, errors=[])
        
        # Specialty must be one of doctor's specialties
        if not doctor.has_specialty(specialty_id):
            result.add_error("Specialty must be one of doctor's registered specialties", "specialty_id")
        
        # Specialty must be active
        if not self.specialty_repository.validate_specialty_exists(specialty_id):
            result.add_error("Specialty is not active or does not exist", "specialty_id")
        
        return result
    
    def _validate_time_slot_conflicts(self, doctor_id: UUID, datetime_slot: datetime) -> ValidationResult:
        """Validate time slot conflicts."""
        result = ValidationResult(is_valid=True, errors=[])
        
        # Check for existing slots at the same time
        if self.availability_repository.has_conflict(doctor_id, datetime_slot):
            result.add_error("Doctor already has a slot at this time", "datetime")
        
        return result
    
    def _validate_business_hours(self, datetime_slot: datetime) -> ValidationResult:
        """Validate business hours (6 AM - 11 PM)."""
        result = ValidationResult(is_valid=True, errors=[])
        
        hour = datetime_slot.hour
        if hour < 6 or hour > 23:
            result.add_error("Time slots must be between 6 AM and 11 PM", "datetime")
        
        return result
    
    def _validate_slot_limits(self, doctor_id: UUID, datetime_slot: datetime) -> ValidationResult:
        """Validate daily and weekly slot limits."""
        result = ValidationResult(is_valid=True, errors=[])
        
        # Daily limit validation
        if not self.availability_repository.validate_daily_limit(doctor_id, datetime_slot, MAX_DAILY_SLOTS):
            result.add_error(f"Doctor has reached the daily limit of {MAX_DAILY_SLOTS} slots", "daily_limit")
        
        # Weekly limit validation
        week_start = datetime_slot.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = week_start - timedelta(days=week_start.weekday())
        if not self.availability_repository.validate_weekly_limit(doctor_id, week_start, MAX_WEEKLY_SLOTS):
            result.add_error(f"Doctor has reached the weekly limit of {MAX_WEEKLY_SLOTS} slots", "weekly_limit")
        
        return result
    
    def validate_and_throw(self, request: TimeSlotRequest, doctor_id: UUID) -> None:
        """Validate and throw exception if validation fails."""
        validation_result = self.validate_time_slot_request(request, doctor_id)
        if not validation_result.is_valid:
            raise ValidationError(
                f"Time slot creation validation failed: {'; '.join(validation_result.errors)}",
                validation_result.field
            )


class TimeSlotModificationValidator:
    """Validator for time slot modification requests."""
    
    def __init__(self, doctor_repository: DoctorRepository,
                 availability_repository: DoctorAvailabilityRepository,
                 specialty_repository: MedicalSpecialtyRepository):
        """Initialize the validator with required repositories."""
        self.doctor_repository = doctor_repository
        self.availability_repository = availability_repository
        self.specialty_repository = specialty_repository
    
    def validate_slot_modification(self, slot_id: UUID, updates: TimeSlotUpdateRequest,
                                 doctor_id: UUID) -> ValidationResult:
        """Validate time slot modification request."""
        # Basic field validation
        basic_validation = updates.validate()
        if not basic_validation.is_valid:
            return basic_validation
        
        # Get slot and doctor
        slot = self.availability_repository.find_by_id(slot_id)
        if not slot:
            return ValidationResult(is_valid=False, errors=["Time slot not found"])
        
        doctor = self.doctor_repository.find_by_id(doctor_id)
        if not doctor:
            return ValidationResult(is_valid=False, errors=["Doctor not found"])
        
        # Business rule validations
        validations = [basic_validation]
        
        # Ownership validation
        ownership_validation = self._validate_slot_ownership(slot, doctor_id)
        validations.append(ownership_validation)
        
        # Modification permission validation
        modification_validation = self._validate_modification_permissions(slot)
        validations.append(modification_validation)
        
        # Specialty validation (if specialty is being updated)
        if updates.specialty_id is not None:
            specialty_validation = self._validate_specialty_assignment(updates.specialty_id, doctor)
            validations.append(specialty_validation)
        
        return combine_validation_results(*validations)
    
    def validate_slot_deletion(self, slot_id: UUID, doctor_id: UUID) -> ValidationResult:
        """Validate time slot deletion request."""
        result = ValidationResult(is_valid=True, errors=[])
        
        # Get slot
        slot = self.availability_repository.find_by_id(slot_id)
        if not slot:
            result.add_error("Time slot not found", "slot_id")
            return result
        
        # Ownership validation
        ownership_validation = self._validate_slot_ownership(slot, doctor_id)
        if not ownership_validation.is_valid:
            return ownership_validation
        
        # Deletion permission validation
        if not slot.can_be_deleted():
            if slot.is_booked():
                result.add_error("Cannot delete booked time slots", "slot_status")
            elif not slot.is_in_future():
                result.add_error("Cannot delete past time slots", "datetime")
        
        # 24-hour advance notice validation (simplified)
        if slot.datetime <= datetime.utcnow() + timedelta(hours=24):
            result.add_error("Cannot delete slots less than 24 hours in advance", "datetime")
        
        return result
    
    def _validate_slot_ownership(self, slot: DoctorAvailability, doctor_id: UUID) -> ValidationResult:
        """Validate that the slot belongs to the doctor."""
        result = ValidationResult(is_valid=True, errors=[])
        
        if slot.doctor_id != doctor_id:
            result.add_error("You can only modify your own time slots", "permissions")
        
        return result
    
    def _validate_modification_permissions(self, slot: DoctorAvailability) -> ValidationResult:
        """Validate modification permissions."""
        result = ValidationResult(is_valid=True, errors=[])
        
        if not slot.can_be_modified():
            if slot.is_booked():
                result.add_error("Cannot modify booked time slots", "slot_status")
            elif not slot.is_in_future():
                result.add_error("Cannot modify past time slots", "datetime")
        
        return result
    
    def _validate_specialty_assignment(self, specialty_id: UUID, doctor: Doctor) -> ValidationResult:
        """Validate specialty assignment."""
        result = ValidationResult(is_valid=True, errors=[])
        
        # Specialty must be one of doctor's specialties
        if not doctor.has_specialty(specialty_id):
            result.add_error("Specialty must be one of doctor's registered specialties", "specialty_id")
        
        # Specialty must be active
        if not self.specialty_repository.validate_specialty_exists(specialty_id):
            result.add_error("Specialty is not active or does not exist", "specialty_id")
        
        return result
    
    def validate_and_throw(self, slot_id: UUID, updates: TimeSlotUpdateRequest,
                          doctor_id: UUID) -> None:
        """Validate and throw exception if validation fails."""
        validation_result = self.validate_slot_modification(slot_id, updates, doctor_id)
        if not validation_result.is_valid:
            raise ValidationError(
                f"Time slot modification validation failed: {'; '.join(validation_result.errors)}",
                validation_result.field
            )


class BulkAvailabilityValidator:
    """Validator for bulk availability operations."""
    
    def __init__(self, doctor_repository: DoctorRepository,
                 availability_repository: DoctorAvailabilityRepository,
                 specialty_repository: MedicalSpecialtyRepository):
        """Initialize the validator with required repositories."""
        self.doctor_repository = doctor_repository
        self.availability_repository = availability_repository
        self.specialty_repository = specialty_repository
        self.slot_validator = TimeSlotCreationValidator(
            doctor_repository, availability_repository, specialty_repository
        )
    
    def validate_bulk_availability_request(self, request: BulkAvailabilityRequest) -> ValidationResult:
        """Validate bulk availability creation request."""
        # Basic validation
        basic_validation = request.validate()
        if not basic_validation.is_valid:
            return basic_validation
        
        # Get doctor
        doctor = self.doctor_repository.find_by_id(request.doctor_id)
        if not doctor:
            return ValidationResult(is_valid=False, errors=["Doctor not found"])
        
        # Validate each time slot
        validations = [basic_validation]
        
        for i, slot_request in enumerate(request.time_slots):
            slot_validation = self.slot_validator.validate_time_slot_request(slot_request, request.doctor_id)
            if not slot_validation.is_valid:
                # Add slot index to error messages
                indexed_errors = [f"Slot {i+1}: {error}" for error in slot_validation.errors]
                slot_validation.errors = indexed_errors
            validations.append(slot_validation)
        
        # Validate overall limits
        limits_validation = self._validate_bulk_limits(request)
        validations.append(limits_validation)
        
        return combine_validation_results(*validations)
    
    def _validate_bulk_limits(self, request: BulkAvailabilityRequest) -> ValidationResult:
        """Validate bulk operation limits."""
        result = ValidationResult(is_valid=True, errors=[])
        
        # Check if bulk operation would exceed daily/weekly limits
        dates_affected = set()
        weeks_affected = set()
        
        for slot_request in request.time_slots:
            date = slot_request.datetime.date()
            dates_affected.add(date)
            
            week_start = slot_request.datetime.replace(hour=0, minute=0, second=0, microsecond=0)
            week_start = week_start - timedelta(days=week_start.weekday())
            weeks_affected.add(week_start.date())
        
        # Check daily limits for each affected date
        for date in dates_affected:
            slots_for_date = len([s for s in request.time_slots if s.datetime.date() == date])
            current_slots = self.availability_repository.count_daily_slots(
                request.doctor_id, datetime.combine(date, datetime.min.time())
            )
            
            if current_slots + slots_for_date > MAX_DAILY_SLOTS:
                result.add_error(
                    f"Bulk operation would exceed daily limit for {date} "
                    f"(current: {current_slots}, adding: {slots_for_date}, limit: {MAX_DAILY_SLOTS})",
                    "daily_limit"
                )
        
        # Check weekly limits for each affected week
        for week_start_date in weeks_affected:
            week_start = datetime.combine(week_start_date, datetime.min.time())
            slots_for_week = len([s for s in request.time_slots 
                                if (s.datetime.replace(hour=0, minute=0, second=0, microsecond=0) - 
                                   timedelta(days=s.datetime.weekday())).date() == week_start_date])
            current_slots = self.availability_repository.count_weekly_slots(request.doctor_id, week_start)
            
            if current_slots + slots_for_week > MAX_WEEKLY_SLOTS:
                result.add_error(
                    f"Bulk operation would exceed weekly limit for week of {week_start_date} "
                    f"(current: {current_slots}, adding: {slots_for_week}, limit: {MAX_WEEKLY_SLOTS})",
                    "weekly_limit"
                )
        
        return result
    
    def validate_and_throw(self, request: BulkAvailabilityRequest) -> None:
        """Validate and throw exception if validation fails."""
        validation_result = self.validate_bulk_availability_request(request)
        if not validation_result.is_valid:
            raise ValidationError(
                f"Bulk availability validation failed: {'; '.join(validation_result.errors)}",
                validation_result.field
            )


class AvailabilityValidatorFactory:
    """Factory for creating availability validators."""
    
    @staticmethod
    def create_slot_creation_validator(doctor_repository: DoctorRepository,
                                     availability_repository: DoctorAvailabilityRepository,
                                     specialty_repository: MedicalSpecialtyRepository) -> TimeSlotCreationValidator:
        """Create a time slot creation validator."""
        return TimeSlotCreationValidator(doctor_repository, availability_repository, specialty_repository)
    
    @staticmethod
    def create_slot_modification_validator(doctor_repository: DoctorRepository,
                                         availability_repository: DoctorAvailabilityRepository,
                                         specialty_repository: MedicalSpecialtyRepository) -> TimeSlotModificationValidator:
        """Create a time slot modification validator."""
        return TimeSlotModificationValidator(doctor_repository, availability_repository, specialty_repository)
    
    @staticmethod
    def create_bulk_validator(doctor_repository: DoctorRepository,
                            availability_repository: DoctorAvailabilityRepository,
                            specialty_repository: MedicalSpecialtyRepository) -> BulkAvailabilityValidator:
        """Create a bulk availability validator."""
        return BulkAvailabilityValidator(doctor_repository, availability_repository, specialty_repository)