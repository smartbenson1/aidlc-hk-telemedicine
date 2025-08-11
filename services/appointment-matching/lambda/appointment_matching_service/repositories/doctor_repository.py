"""
Doctor repository implementation for the Appointment Matching Service.
"""

from typing import List, Optional

from .base_repository import InMemoryRepository
from ..models.doctor import Doctor
from ..utils.enums import UserStatus


class DoctorRepository(InMemoryRepository[Doctor]):
    """Repository for managing doctors."""
    
    def __init__(self):
        super().__init__("Doctor")
    
    def find_by_email(self, email: str) -> Optional[Doctor]:
        """Find doctor by email."""
        doctors = self.find_by_field("email", email)
        return doctors[0] if doctors else None
    
    def find_by_specialty(self, specialty_id: str) -> List[Doctor]:
        """Find doctors by specialty."""
        return self.find_by_predicate(
            lambda doctor: specialty_id in doctor.specialties
        )
    
    def find_active(self) -> List[Doctor]:
        """Find all active doctors."""
        return self.find_by_field("status", UserStatus.ACTIVE)
    
    def find_by_rating_range(self, min_rating: float, max_rating: float) -> List[Doctor]:
        """Find doctors within rating range."""
        return self.find_by_predicate(
            lambda doctor: min_rating <= float(doctor.rating) <= max_rating
        )
    
    def find_by_location(self, location: str) -> List[Doctor]:
        """Find doctors by location."""
        return self.find_by_field("location", location)
    
    def find_active_by_specialty(self, specialty_id: str) -> List[Doctor]:
        """Find active doctors by specialty."""
        return self.find_by_predicate(
            lambda doctor: (doctor.status == UserStatus.ACTIVE and 
                          specialty_id in doctor.specialties)
        )
    
    def get_top_rated(self, limit: int = 10) -> List[Doctor]:
        """Get top rated doctors."""
        all_doctors = self.find_all()
        sorted_doctors = sorted(all_doctors, key=lambda d: d.rating, reverse=True)
        return sorted_doctors[:limit]