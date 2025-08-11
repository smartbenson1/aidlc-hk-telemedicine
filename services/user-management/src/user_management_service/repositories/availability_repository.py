"""
Doctor Availability repository implementation for the User Management Service.
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from uuid import UUID

from .base_repository import InMemoryRepository
from ..models.doctor_availability import DoctorAvailability
from ..utils.enums import AvailabilityStatus, AppointmentType
from ..utils.exceptions import DuplicateError, BusinessRuleError


class DoctorAvailabilityRepository(InMemoryRepository[DoctorAvailability]):
    """Repository for Doctor Availability entities."""
    
    def __init__(self):
        """Initialize the doctor availability repository."""
        super().__init__("DoctorAvailability", "doctor_availability.json")
    
    def _deserialize_entity(self, data: Dict[str, Any]) -> DoctorAvailability:
        """Deserialize doctor availability from dictionary data."""
        return DoctorAvailability.from_dict(data)
    
    def find_by_doctor(self, doctor_id: UUID) -> List[DoctorAvailability]:
        """Find all availability slots for a doctor."""
        return self.find_by_field("doctor_id", doctor_id)
    
    def find_by_doctor_and_date_range(self, doctor_id: UUID, start_date: datetime, 
                                     end_date: datetime) -> List[DoctorAvailability]:
        """Find availability slots for a doctor within a date range."""
        results = []
        for availability in self.find_by_doctor(doctor_id):
            if start_date <= availability.datetime <= end_date:
                results.append(availability)
        return sorted(results, key=lambda a: a.datetime)
    
    def find_available_slots(self, doctor_id: UUID, start_date: datetime, 
                           end_date: datetime) -> List[DoctorAvailability]:
        """Find available (unbooked) slots for a doctor within a date range."""
        results = []
        for availability in self.find_by_doctor_and_date_range(doctor_id, start_date, end_date):
            if availability.is_available() and availability.is_in_future():
                results.append(availability)
        return results
    
    def find_by_status(self, status: AvailabilityStatus) -> List[DoctorAvailability]:
        """Find availability slots by status."""
        return self.find_by_field("status", status)
    
    def find_by_appointment_type(self, appointment_type: AppointmentType) -> List[DoctorAvailability]:
        """Find availability slots by appointment type."""
        return self.find_by_field("appointment_type", appointment_type)
    
    def find_by_specialty(self, specialty_id: UUID) -> List[DoctorAvailability]:
        """Find availability slots by specialty."""
        return self.find_by_field("specialty_id", specialty_id)
    
    def find_conflicting_slot(self, doctor_id: UUID, datetime_slot: datetime) -> Optional[DoctorAvailability]:
        """Find if there's a conflicting slot at the same time for the same doctor."""
        for availability in self.find_by_doctor(doctor_id):
            if availability.datetime == datetime_slot:
                return availability
        return None
    
    def has_conflict(self, doctor_id: UUID, datetime_slot: datetime, 
                    exclude_id: Optional[UUID] = None) -> bool:
        """Check if there's a scheduling conflict."""
        conflicting_slot = self.find_conflicting_slot(doctor_id, datetime_slot)
        if not conflicting_slot:
            return False
        if exclude_id and conflicting_slot.id == exclude_id:
            return False
        return True
    
    def create_with_conflict_check(self, availability: DoctorAvailability) -> DoctorAvailability:
        """Create availability slot with conflict check."""
        if self.has_conflict(availability.doctor_id, availability.datetime):
            raise DuplicateError(
                f"Doctor already has a slot at {availability.datetime}",
                "DoctorAvailability",
                "datetime",
                availability.datetime.isoformat()
            )
        return self.create(availability)
    
    def get_doctor_schedule(self, doctor_id: UUID, date: datetime) -> List[DoctorAvailability]:
        """Get doctor's schedule for a specific date."""
        start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)
        return self.find_by_doctor_and_date_range(doctor_id, start_of_day, end_of_day)
    
    def get_weekly_schedule(self, doctor_id: UUID, week_start: datetime) -> List[DoctorAvailability]:
        """Get doctor's schedule for a week."""
        week_end = week_start + timedelta(days=7)
        return self.find_by_doctor_and_date_range(doctor_id, week_start, week_end)
    
    def count_daily_slots(self, doctor_id: UUID, date: datetime) -> int:
        """Count slots for a doctor on a specific date."""
        return len(self.get_doctor_schedule(doctor_id, date))
    
    def count_weekly_slots(self, doctor_id: UUID, week_start: datetime) -> int:
        """Count slots for a doctor in a week."""
        return len(self.get_weekly_schedule(doctor_id, week_start))
    
    def validate_daily_limit(self, doctor_id: UUID, date: datetime, max_daily_slots: int = 12) -> bool:
        """Validate that doctor hasn't exceeded daily slot limit."""
        current_count = self.count_daily_slots(doctor_id, date)
        return current_count < max_daily_slots
    
    def validate_weekly_limit(self, doctor_id: UUID, week_start: datetime, max_weekly_slots: int = 60) -> bool:
        """Validate that doctor hasn't exceeded weekly slot limit."""
        current_count = self.count_weekly_slots(doctor_id, week_start)
        return current_count < max_weekly_slots
    
    def create_with_business_rules(self, availability: DoctorAvailability) -> DoctorAvailability:
        """Create availability slot with business rule validation."""
        # Check for conflicts
        if self.has_conflict(availability.doctor_id, availability.datetime):
            raise BusinessRuleError(
                f"Doctor already has a slot at {availability.datetime}",
                "slot_conflict"
            )
        
        # Check daily limit
        if not self.validate_daily_limit(availability.doctor_id, availability.datetime):
            raise BusinessRuleError(
                "Doctor has reached the daily limit of 12 slots",
                "daily_limit_exceeded"
            )
        
        # Check weekly limit
        week_start = availability.datetime.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = week_start - timedelta(days=week_start.weekday())
        if not self.validate_weekly_limit(availability.doctor_id, week_start):
            raise BusinessRuleError(
                "Doctor has reached the weekly limit of 60 slots",
                "weekly_limit_exceeded"
            )
        
        return self.create(availability)
    
    def find_upcoming_slots(self, doctor_id: Optional[UUID] = None, 
                           hours_ahead: int = 24) -> List[DoctorAvailability]:
        """Find upcoming slots within specified hours."""
        now = datetime.utcnow()
        future_time = now + timedelta(hours=hours_ahead)
        
        results = []
        slots = self.find_by_doctor(doctor_id) if doctor_id else self.find_all()
        
        for slot in slots:
            if now <= slot.datetime <= future_time:
                results.append(slot)
        
        return sorted(results, key=lambda s: s.datetime)
    
    def find_expired_slots(self) -> List[DoctorAvailability]:
        """Find slots that are in the past and still marked as available."""
        now = datetime.utcnow()
        results = []
        
        for slot in self.find_by_status(AvailabilityStatus.AVAILABLE):
            if slot.datetime < now:
                results.append(slot)
        
        return results
    
    def cleanup_expired_slots(self) -> int:
        """Remove or block expired available slots."""
        expired_slots = self.find_expired_slots()
        cleaned_count = 0
        
        for slot in expired_slots:
            slot.block()  # Block instead of delete to maintain history
            self.update(slot)
            cleaned_count += 1
        
        return cleaned_count
    
    def search_available_slots(self, criteria: Dict[str, Any]) -> List[DoctorAvailability]:
        """Search available slots by multiple criteria."""
        results = self.find_by_status(AvailabilityStatus.AVAILABLE)
        
        # Filter by doctor
        doctor_id = criteria.get('doctor_id')
        if doctor_id:
            results = [s for s in results if s.doctor_id == doctor_id]
        
        # Filter by date range
        start_date = criteria.get('start_date')
        end_date = criteria.get('end_date')
        if start_date and end_date:
            results = [s for s in results if start_date <= s.datetime <= end_date]
        
        # Filter by appointment type
        appointment_type = criteria.get('appointment_type')
        if appointment_type:
            results = [s for s in results if s.appointment_type == appointment_type]
        
        # Filter by specialty
        specialty_id = criteria.get('specialty_id')
        if specialty_id:
            results = [s for s in results if s.specialty_id == specialty_id]
        
        # Filter future slots only
        if criteria.get('future_only', True):
            now = datetime.utcnow()
            results = [s for s in results if s.datetime > now]
        
        return sorted(results, key=lambda s: s.datetime)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get repository statistics."""
        all_slots = self.find_all()
        available_slots = self.find_by_status(AvailabilityStatus.AVAILABLE)
        booked_slots = self.find_by_status(AvailabilityStatus.BOOKED)
        blocked_slots = self.find_by_status(AvailabilityStatus.BLOCKED)
        
        # Count by status
        status_counts = {
            'available': len(available_slots),
            'booked': len(booked_slots),
            'blocked': len(blocked_slots)
        }
        
        # Count by appointment type
        type_counts = {}
        for appointment_type in AppointmentType:
            type_counts[appointment_type.value] = len(self.find_by_appointment_type(appointment_type))
        
        # Calculate utilization rate
        total_bookable = len(available_slots) + len(booked_slots)
        utilization_rate = (len(booked_slots) / total_bookable * 100) if total_bookable > 0 else 0
        
        return {
            'total_slots': len(all_slots),
            'status_distribution': status_counts,
            'appointment_type_distribution': type_counts,
            'utilization_rate': round(utilization_rate, 1),
            'expired_available_slots': len(self.find_expired_slots())
        }
    
    def bulk_update_status(self, slot_ids: List[UUID], status: AvailabilityStatus, 
                          updated_by: Optional[UUID] = None) -> List[DoctorAvailability]:
        """Bulk update status for multiple slots."""
        updated_slots = []
        for slot_id in slot_ids:
            slot = self.find_by_id(slot_id)
            if slot:
                slot.status = status
                slot.update_timestamp(updated_by)
                updated_slot = self.update(slot)
                updated_slots.append(updated_slot)
        return updated_slots
    
    def get_doctor_availability_summary(self, doctor_id: UUID, 
                                       days_ahead: int = 30) -> Dict[str, Any]:
        """Get availability summary for a doctor."""
        start_date = datetime.utcnow()
        end_date = start_date + timedelta(days=days_ahead)
        
        all_slots = self.find_by_doctor_and_date_range(doctor_id, start_date, end_date)
        available_slots = [s for s in all_slots if s.is_available()]
        booked_slots = [s for s in all_slots if s.is_booked()]
        
        # Group by date
        dates_with_availability = {}
        for slot in available_slots:
            date_key = slot.datetime.date().isoformat()
            if date_key not in dates_with_availability:
                dates_with_availability[date_key] = []
            dates_with_availability[date_key].append(slot)
        
        return {
            'doctor_id': str(doctor_id),
            'period': f"{start_date.date()} to {end_date.date()}",
            'total_slots': len(all_slots),
            'available_slots': len(available_slots),
            'booked_slots': len(booked_slots),
            'dates_with_availability': len(dates_with_availability),
            'next_available_slot': min(available_slots, key=lambda s: s.datetime).datetime.isoformat() if available_slots else None
        }