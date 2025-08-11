"""
Doctor model for the User Management Service.
"""

from dataclasses import dataclass, field
from typing import List, Optional
from uuid import UUID

from ..utils.base_models import BaseEntity
from ..utils.enums import UserStatus


@dataclass
class Doctor(BaseEntity):
    """Doctor entity model."""
    
    # Basic Information
    name: str = ""
    email: str = ""
    phone: str = ""
    location: str = ""
    
    # Professional Information
    specialties: List[UUID] = field(default_factory=list)
    experience: str = ""
    rating: float = 0.0
    
    # System Fields
    status: UserStatus = UserStatus.ACTIVE
    
    def __str__(self) -> str:
        """String representation of the doctor."""
        return f"Dr. {self.name} ({self.email})"
    
    def __repr__(self) -> str:
        """Detailed string representation of the doctor."""
        return (f"Doctor(id={self.id}, name='{self.name}', email='{self.email}', "
                f"specialties={len(self.specialties)}, status={self.status.value})")
    
    def is_active(self) -> bool:
        """Check if the doctor is active."""
        return self.status == UserStatus.ACTIVE
    
    def has_specialty(self, specialty_id: UUID) -> bool:
        """Check if the doctor has a specific specialty."""
        return specialty_id in self.specialties
    
    def add_specialty(self, specialty_id: UUID) -> None:
        """Add a specialty to the doctor."""
        if specialty_id not in self.specialties:
            self.specialties.append(specialty_id)
            self.update_timestamp()
    
    def remove_specialty(self, specialty_id: UUID) -> None:
        """Remove a specialty from the doctor."""
        if specialty_id in self.specialties:
            self.specialties.remove(specialty_id)
            self.update_timestamp()
    
    def update_rating(self, new_rating: float) -> None:
        """Update the doctor's rating."""
        if 0.0 <= new_rating <= 5.0:
            self.rating = new_rating
            self.update_timestamp()
    
    def activate(self, updated_by: Optional[UUID] = None) -> None:
        """Activate the doctor."""
        self.status = UserStatus.ACTIVE
        self.update_timestamp(updated_by)
    
    def deactivate(self, updated_by: Optional[UUID] = None) -> None:
        """Deactivate the doctor."""
        self.status = UserStatus.INACTIVE
        self.update_timestamp(updated_by)
    
    def suspend(self, updated_by: Optional[UUID] = None) -> None:
        """Suspend the doctor."""
        self.status = UserStatus.SUSPENDED
        self.update_timestamp(updated_by)
    
    def to_dict(self) -> dict:
        """Convert doctor to dictionary representation."""
        return {
            'id': str(self.id),
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'location': self.location,
            'specialties': [str(s) for s in self.specialties],
            'experience': self.experience,
            'rating': self.rating,
            'status': self.status.value,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'created_by': str(self.created_by) if self.created_by else None,
            'updated_by': str(self.updated_by) if self.updated_by else None
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Doctor':
        """Create doctor from dictionary representation."""
        from uuid import UUID
        from datetime import datetime
        
        doctor = cls()
        doctor.id = UUID(data['id'])
        doctor.name = data['name']
        doctor.email = data['email']
        doctor.phone = data['phone']
        doctor.location = data['location']
        doctor.specialties = [UUID(s) for s in data['specialties']]
        doctor.experience = data['experience']
        doctor.rating = data['rating']
        doctor.status = UserStatus(data['status'])
        doctor.created_at = datetime.fromisoformat(data['created_at'])
        doctor.updated_at = datetime.fromisoformat(data['updated_at'])
        doctor.created_by = UUID(data['created_by']) if data['created_by'] else None
        doctor.updated_by = UUID(data['updated_by']) if data['updated_by'] else None
        
        return doctor