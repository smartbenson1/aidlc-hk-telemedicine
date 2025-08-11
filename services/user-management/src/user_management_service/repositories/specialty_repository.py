"""
Medical Specialty repository implementation for the User Management Service.
"""

from typing import List, Optional, Dict, Any
from uuid import UUID

from .base_repository import InMemoryRepository
from ..models.medical_specialty import MedicalSpecialty
from ..utils.enums import UserStatus
from ..utils.exceptions import DuplicateError


class MedicalSpecialtyRepository(InMemoryRepository[MedicalSpecialty]):
    """Repository for Medical Specialty entities."""
    
    def __init__(self):
        """Initialize the medical specialty repository."""
        super().__init__("MedicalSpecialty", "medical_specialties.json")
    
    def _deserialize_entity(self, data: Dict[str, Any]) -> MedicalSpecialty:
        """Deserialize medical specialty from dictionary data."""
        return MedicalSpecialty.from_dict(data)
    
    def find_by_name(self, name: str, exact_match: bool = True) -> Optional[MedicalSpecialty]:
        """Find medical specialty by name."""
        if exact_match:
            specialties = self.find_by_field("name", name)
            return specialties[0] if specialties else None
        else:
            # Partial match
            name_lower = name.lower()
            for specialty in self.find_all():
                if name_lower in specialty.name.lower():
                    return specialty
            return None
    
    def find_by_status(self, status: UserStatus) -> List[MedicalSpecialty]:
        """Find medical specialties by status."""
        return self.find_by_field("status", status)
    
    def find_active_specialties(self) -> List[MedicalSpecialty]:
        """Find all active medical specialties."""
        return self.find_by_status(UserStatus.ACTIVE)
    
    def find_inactive_specialties(self) -> List[MedicalSpecialty]:
        """Find all inactive medical specialties."""
        return self.find_by_status(UserStatus.INACTIVE)
    
    def search_by_name(self, search_term: str) -> List[MedicalSpecialty]:
        """Search specialties by name (partial match)."""
        results = []
        search_term_lower = search_term.lower()
        
        for specialty in self.find_all():
            if (search_term_lower in specialty.name.lower() or 
                search_term_lower in specialty.description.lower()):
                results.append(specialty)
        
        return results
    
    def search_specialties(self, criteria: Dict[str, Any]) -> List[MedicalSpecialty]:
        """Search specialties by multiple criteria."""
        results = self.find_all()
        
        # Filter by status (default to active if not specified)
        status = criteria.get('status', UserStatus.ACTIVE)
        if status:
            results = [s for s in results if s.status == status]
        
        # Filter by name (partial match)
        name = criteria.get('name')
        if name:
            name_lower = name.lower()
            results = [s for s in results if name_lower in s.name.lower()]
        
        # Filter by description (partial match)
        description = criteria.get('description')
        if description:
            description_lower = description.lower()
            results = [s for s in results if description_lower in s.description.lower()]
        
        return results
    
    def name_exists(self, name: str, exclude_id: Optional[UUID] = None) -> bool:
        """Check if specialty name exists, optionally excluding a specific specialty ID."""
        specialty = self.find_by_name(name, exact_match=True)
        if not specialty:
            return False
        if exclude_id and specialty.id == exclude_id:
            return False
        return True
    
    def create_with_name_check(self, specialty: MedicalSpecialty) -> MedicalSpecialty:
        """Create specialty with name uniqueness check."""
        if self.name_exists(specialty.name):
            raise DuplicateError(
                f"Medical specialty with name '{specialty.name}' already exists",
                "MedicalSpecialty",
                "name",
                specialty.name
            )
        return self.create(specialty)
    
    def update_with_name_check(self, specialty: MedicalSpecialty) -> MedicalSpecialty:
        """Update specialty with name uniqueness check."""
        if self.name_exists(specialty.name, exclude_id=specialty.id):
            raise DuplicateError(
                f"Medical specialty with name '{specialty.name}' already exists",
                "MedicalSpecialty",
                "name",
                specialty.name
            )
        return self.update(specialty)
    
    def get_specialty_details(self, specialty_ids: List[UUID]) -> List[Dict[str, str]]:
        """Get specialty details for a list of specialty IDs."""
        details = []
        for specialty_id in specialty_ids:
            specialty = self.find_by_id(specialty_id)
            if specialty:
                details.append({
                    'id': str(specialty.id),
                    'name': specialty.name,
                    'description': specialty.description
                })
        return details
    
    def validate_specialty_exists(self, specialty_id: UUID) -> bool:
        """Validate that a specialty exists and is active."""
        specialty = self.find_by_id(specialty_id)
        return specialty is not None and specialty.is_active()
    
    def validate_specialties_exist(self, specialty_ids: List[UUID]) -> Dict[str, Any]:
        """Validate that all specialties exist and are active."""
        result = {
            'all_valid': True,
            'valid_ids': [],
            'invalid_ids': [],
            'inactive_ids': []
        }
        
        for specialty_id in specialty_ids:
            specialty = self.find_by_id(specialty_id)
            if not specialty:
                result['invalid_ids'].append(str(specialty_id))
                result['all_valid'] = False
            elif not specialty.is_active():
                result['inactive_ids'].append(str(specialty_id))
                result['all_valid'] = False
            else:
                result['valid_ids'].append(str(specialty_id))
        
        return result
    
    def get_popular_specialties(self, doctor_repository, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most popular specialties based on doctor count."""
        specialty_counts = {}
        
        # Count doctors for each specialty
        for doctor in doctor_repository.find_active_doctors():
            for specialty_id in doctor.specialties:
                specialty_id_str = str(specialty_id)
                if specialty_id_str not in specialty_counts:
                    specialty_counts[specialty_id_str] = {
                        'specialty_id': specialty_id,
                        'count': 0,
                        'specialty': None
                    }
                specialty_counts[specialty_id_str]['count'] += 1
        
        # Get specialty details
        for specialty_data in specialty_counts.values():
            specialty = self.find_by_id(specialty_data['specialty_id'])
            if specialty:
                specialty_data['specialty'] = {
                    'id': str(specialty.id),
                    'name': specialty.name,
                    'description': specialty.description
                }
        
        # Sort by count and return top specialties
        sorted_specialties = sorted(
            specialty_counts.values(),
            key=lambda x: x['count'],
            reverse=True
        )
        
        return sorted_specialties[:limit]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get repository statistics."""
        specialties = self.find_all()
        active_specialties = self.find_active_specialties()
        inactive_specialties = self.find_inactive_specialties()
        
        # Count by status
        status_counts = {}
        for status in UserStatus:
            if status in [UserStatus.ACTIVE, UserStatus.INACTIVE]:  # Only relevant statuses
                status_counts[status.value] = len(self.find_by_status(status))
        
        # Calculate average description length
        descriptions = [s.description for s in active_specialties if s.description]
        avg_description_length = (
            sum(len(desc) for desc in descriptions) / len(descriptions)
            if descriptions else 0
        )
        
        return {
            'total_specialties': len(specialties),
            'active_specialties': len(active_specialties),
            'inactive_specialties': len(inactive_specialties),
            'status_distribution': status_counts,
            'specialties_with_description': len(descriptions),
            'average_description_length': round(avg_description_length, 1)
        }
    
    def bulk_update_status(self, specialty_ids: List[UUID], status: UserStatus, 
                          updated_by: Optional[UUID] = None) -> List[MedicalSpecialty]:
        """Bulk update status for multiple specialties."""
        updated_specialties = []
        for specialty_id in specialty_ids:
            specialty = self.find_by_id(specialty_id)
            if specialty:
                if status == UserStatus.ACTIVE:
                    specialty.activate(updated_by)
                elif status == UserStatus.INACTIVE:
                    specialty.deactivate(updated_by)
                updated_specialty = self.update(specialty)
                updated_specialties.append(updated_specialty)
        return updated_specialties
    
    def get_alphabetical_list(self, active_only: bool = True) -> List[MedicalSpecialty]:
        """Get specialties in alphabetical order."""
        specialties = self.find_active_specialties() if active_only else self.find_all()
        return sorted(specialties, key=lambda s: s.name.lower())
    
    def import_specialties_from_admin_service(self, specialties_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Import specialties from administration service data."""
        result = {
            'imported': 0,
            'updated': 0,
            'skipped': 0,
            'errors': []
        }
        
        for specialty_data in specialties_data:
            try:
                # Check if specialty already exists by name
                existing = self.find_by_name(specialty_data['name'])
                
                if existing:
                    # Update existing specialty
                    existing.description = specialty_data.get('description', existing.description)
                    existing.status = UserStatus(specialty_data.get('status', 'active'))
                    self.update(existing)
                    result['updated'] += 1
                else:
                    # Create new specialty
                    specialty = MedicalSpecialty(
                        name=specialty_data['name'],
                        description=specialty_data.get('description', ''),
                        status=UserStatus(specialty_data.get('status', 'active'))
                    )
                    self.create(specialty)
                    result['imported'] += 1
                    
            except Exception as e:
                result['errors'].append(f"Failed to import {specialty_data.get('name', 'unknown')}: {str(e)}")
                result['skipped'] += 1
        
        return result