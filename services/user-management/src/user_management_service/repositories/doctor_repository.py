"""
Doctor repository implementation for the User Management Service.
"""

from typing import List, Optional, Dict, Any
from uuid import UUID

from .base_repository import InMemoryRepository
from ..models.doctor import Doctor
from ..utils.enums import UserStatus
from ..utils.exceptions import DuplicateError


class DoctorRepository(InMemoryRepository[Doctor]):
    """Repository for Doctor entities."""
    
    def __init__(self):
        """Initialize the doctor repository."""
        super().__init__("Doctor", "doctors.json")
    
    def _deserialize_entity(self, data: Dict[str, Any]) -> Doctor:
        """Deserialize doctor from dictionary data."""
        return Doctor.from_dict(data)
    
    def find_by_email(self, email: str) -> Optional[Doctor]:
        """Find doctor by email address."""
        doctors = self.find_by_field("email", email)
        return doctors[0] if doctors else None
    
    def find_by_specialty(self, specialty_id: UUID) -> List[Doctor]:
        """Find doctors by specialty."""
        results = []
        for doctor in self.find_all():
            if doctor.has_specialty(specialty_id):
                results.append(doctor)
        return results
    
    def find_by_specialties(self, specialty_ids: List[UUID]) -> List[Doctor]:
        """Find doctors who have any of the specified specialties."""
        results = []
        for doctor in self.find_all():
            for specialty_id in specialty_ids:
                if doctor.has_specialty(specialty_id):
                    results.append(doctor)
                    break
        return results
    
    def find_by_status(self, status: UserStatus) -> List[Doctor]:
        """Find doctors by status."""
        return self.find_by_field("status", status)
    
    def find_active_doctors(self) -> List[Doctor]:
        """Find all active doctors."""
        return self.find_by_status(UserStatus.ACTIVE)
    
    def find_by_location(self, location: str) -> List[Doctor]:
        """Find doctors by location (partial match)."""
        results = []
        location_lower = location.lower()
        for doctor in self.find_all():
            if location_lower in doctor.location.lower():
                results.append(doctor)
        return results
    
    def find_by_rating_range(self, min_rating: float, max_rating: float) -> List[Doctor]:
        """Find doctors within a rating range."""
        results = []
        for doctor in self.find_all():
            if min_rating <= doctor.rating <= max_rating:
                results.append(doctor)
        return results
    
    def find_top_rated(self, limit: int = 10) -> List[Doctor]:
        """Find top-rated doctors."""
        doctors = self.find_active_doctors()
        doctors.sort(key=lambda d: d.rating, reverse=True)
        return doctors[:limit]
    
    def search_doctors(self, criteria: Dict[str, Any]) -> List[Doctor]:
        """Search doctors by multiple criteria."""
        results = self.find_all()
        
        # Filter by status (default to active if not specified)
        status = criteria.get('status', UserStatus.ACTIVE)
        if status:
            results = [d for d in results if d.status == status]
        
        # Filter by specialty
        specialty_id = criteria.get('specialty_id')
        if specialty_id:
            results = [d for d in results if d.has_specialty(specialty_id)]
        
        # Filter by location (partial match)
        location = criteria.get('location')
        if location:
            location_lower = location.lower()
            results = [d for d in results if location_lower in d.location.lower()]
        
        # Filter by minimum rating
        min_rating = criteria.get('min_rating')
        if min_rating is not None:
            results = [d for d in results if d.rating >= min_rating]
        
        # Filter by name (partial match)
        name = criteria.get('name')
        if name:
            name_lower = name.lower()
            results = [d for d in results if name_lower in d.name.lower()]
        
        return results
    
    def email_exists(self, email: str, exclude_id: Optional[UUID] = None) -> bool:
        """Check if email exists, optionally excluding a specific doctor ID."""
        doctor = self.find_by_email(email)
        if not doctor:
            return False
        if exclude_id and doctor.id == exclude_id:
            return False
        return True
    
    def create_with_email_check(self, doctor: Doctor) -> Doctor:
        """Create doctor with email uniqueness check."""
        if self.email_exists(doctor.email):
            raise DuplicateError(
                f"Doctor with email {doctor.email} already exists",
                "Doctor",
                "email",
                doctor.email
            )
        return self.create(doctor)
    
    def update_with_email_check(self, doctor: Doctor) -> Doctor:
        """Update doctor with email uniqueness check."""
        if self.email_exists(doctor.email, exclude_id=doctor.id):
            raise DuplicateError(
                f"Doctor with email {doctor.email} already exists",
                "Doctor",
                "email",
                doctor.email
            )
        return self.update(doctor)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get repository statistics."""
        doctors = self.find_all()
        active_doctors = self.find_active_doctors()
        
        # Calculate average rating
        total_rating = sum(d.rating for d in active_doctors)
        avg_rating = total_rating / len(active_doctors) if active_doctors else 0.0
        
        # Count by status
        status_counts = {}
        for status in UserStatus:
            status_counts[status.value] = len(self.find_by_status(status))
        
        # Count specialties
        specialty_counts = {}
        for doctor in active_doctors:
            for specialty_id in doctor.specialties:
                specialty_id_str = str(specialty_id)
                specialty_counts[specialty_id_str] = specialty_counts.get(specialty_id_str, 0) + 1
        
        return {
            'total_doctors': len(doctors),
            'active_doctors': len(active_doctors),
            'average_rating': round(avg_rating, 2),
            'status_distribution': status_counts,
            'specialty_distribution': specialty_counts
        }
    
    def bulk_update_status(self, doctor_ids: List[UUID], status: UserStatus, 
                          updated_by: Optional[UUID] = None) -> List[Doctor]:
        """Bulk update status for multiple doctors."""
        updated_doctors = []
        for doctor_id in doctor_ids:
            doctor = self.find_by_id(doctor_id)
            if doctor:
                doctor.status = status
                doctor.update_timestamp(updated_by)
                updated_doctor = self.update(doctor)
                updated_doctors.append(updated_doctor)
        return updated_doctors