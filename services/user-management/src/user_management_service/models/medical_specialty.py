"""
Medical Specialty model for the User Management Service.
"""

from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from ..utils.base_models import BaseEntity
from ..utils.enums import UserStatus


@dataclass
class MedicalSpecialty(BaseEntity):
    """Medical Specialty entity model."""
    
    # Basic Information
    name: str = ""
    description: str = ""
    
    # System Fields
    status: UserStatus = UserStatus.ACTIVE
    
    def __str__(self) -> str:
        """String representation of the medical specialty."""
        return self.name
    
    def __repr__(self) -> str:
        """Detailed string representation of the medical specialty."""
        return f"MedicalSpecialty(id={self.id}, name='{self.name}', status={self.status.value})"
    
    def is_active(self) -> bool:
        """Check if the medical specialty is active."""
        return self.status == UserStatus.ACTIVE
    
    def activate(self, updated_by: Optional[UUID] = None) -> None:
        """Activate the medical specialty."""
        self.status = UserStatus.ACTIVE
        self.update_timestamp(updated_by)
    
    def deactivate(self, updated_by: Optional[UUID] = None) -> None:
        """Deactivate the medical specialty."""
        self.status = UserStatus.INACTIVE
        self.update_timestamp(updated_by)
    
    def update_description(self, description: str, updated_by: Optional[UUID] = None) -> None:
        """Update the specialty description."""
        self.description = description
        self.update_timestamp(updated_by)
    
    def to_dict(self) -> dict:
        """Convert medical specialty to dictionary representation."""
        return {
            'id': str(self.id),
            'name': self.name,
            'description': self.description,
            'status': self.status.value,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'created_by': str(self.created_by) if self.created_by else None,
            'updated_by': str(self.updated_by) if self.updated_by else None
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'MedicalSpecialty':
        """Create medical specialty from dictionary representation."""
        from uuid import UUID
        from datetime import datetime
        
        specialty = cls()
        specialty.id = UUID(data['id'])
        specialty.name = data['name']
        specialty.description = data['description']
        specialty.status = UserStatus(data['status'])
        specialty.created_at = datetime.fromisoformat(data['created_at'])
        specialty.updated_at = datetime.fromisoformat(data['updated_at'])
        specialty.created_by = UUID(data['created_by']) if data['created_by'] else None
        specialty.updated_by = UUID(data['updated_by']) if data['updated_by'] else None
        
        return specialty