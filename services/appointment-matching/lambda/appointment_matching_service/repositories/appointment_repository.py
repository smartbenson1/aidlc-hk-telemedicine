"""
Appointment repository implementation for the Appointment Matching Service.
"""

from datetime import datetime
from typing import List, Optional

from .base_repository import InMemoryRepository
from ..models.appointment import Appointment
from ..utils.enums import AppointmentStatus


class AppointmentRepository(InMemoryRepository[Appointment]):
    """Repository for managing appointments."""
    
    def __init__(self):
        super().__init__("Appointment")
    
    def find_by_patient(self, patient_id: str) -> List[Appointment]:
        """Find appointments by patient ID."""
        return self.find_by_field("patient_id", patient_id)
    
    def find_by_doctor(self, doctor_id: str) -> List[Appointment]:
        """Find appointments by doctor ID."""
        return self.find_by_field("doctor_id", doctor_id)
    
    def find_by_date_range(self, start: datetime, end: datetime) -> List[Appointment]:
        """Find appointments within date range."""
        return self.find_by_predicate(
            lambda appointment: (appointment.datetime and 
                               start <= appointment.datetime <= end)
        )
    
    def find_upcoming(self) -> List[Appointment]:
        """Find upcoming appointments."""
        current_time = datetime.utcnow()
        return self.find_by_predicate(
            lambda appointment: (appointment.datetime and 
                               appointment.datetime > current_time and
                               appointment.status == AppointmentStatus.SCHEDULED)
        )
    
    def find_by_status(self, status: AppointmentStatus) -> List[Appointment]:
        """Find appointments by status."""
        return self.find_by_field("status", status)
    
    def find_scheduled_for_doctor(self, doctor_id: str) -> List[Appointment]:
        """Find scheduled appointments for a doctor."""
        return self.find_by_predicate(
            lambda appointment: (appointment.doctor_id == doctor_id and 
                               appointment.status == AppointmentStatus.SCHEDULED)
        )