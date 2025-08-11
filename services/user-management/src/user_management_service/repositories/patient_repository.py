"""
Patient repository implementation for the User Management Service.
"""

from typing import List, Optional, Dict, Any
from uuid import UUID

from .base_repository import InMemoryRepository
from ..models.patient import Patient
from ..utils.enums import UserStatus
from ..utils.exceptions import DuplicateError


class PatientRepository(InMemoryRepository[Patient]):
    """Repository for Patient entities."""
    
    def __init__(self):
        """Initialize the patient repository."""
        super().__init__("Patient", "patients.json")
    
    def _deserialize_entity(self, data: Dict[str, Any]) -> Patient:
        """Deserialize patient from dictionary data."""
        return Patient.from_dict(data)
    
    def find_by_email(self, email: str) -> Optional[Patient]:
        """Find patient by email address."""
        patients = self.find_by_field("email", email)
        return patients[0] if patients else None
    
    def find_by_phone(self, phone: str) -> Optional[Patient]:
        """Find patient by phone number."""
        patients = self.find_by_field("phone", phone)
        return patients[0] if patients else None
    
    def find_by_status(self, status: UserStatus) -> List[Patient]:
        """Find patients by status."""
        return self.find_by_field("status", status)
    
    def find_active_patients(self) -> List[Patient]:
        """Find all active patients."""
        return self.find_by_status(UserStatus.ACTIVE)
    
    def find_by_name(self, name: str, exact_match: bool = False) -> List[Patient]:
        """Find patients by name (partial or exact match)."""
        results = []
        search_name = name if exact_match else name.lower()
        
        for patient in self.find_all():
            patient_name = patient.name if exact_match else patient.name.lower()
            if exact_match:
                if patient_name == search_name:
                    results.append(patient)
            else:
                if search_name in patient_name:
                    results.append(patient)
        
        return results
    
    def find_by_emergency_contact_phone(self, phone: str) -> List[Patient]:
        """Find patients by emergency contact phone number."""
        return self.find_by_field("emergency_contact_phone", phone)
    
    def find_by_emergency_contact_relationship(self, relationship: str) -> List[Patient]:
        """Find patients by emergency contact relationship."""
        return self.find_by_field("emergency_contact_relationship", relationship)
    
    def find_with_medical_history(self) -> List[Patient]:
        """Find patients who have medical history recorded."""
        results = []
        for patient in self.find_all():
            if patient.has_medical_history():
                results.append(patient)
        return results
    
    def search_patients(self, criteria: Dict[str, Any]) -> List[Patient]:
        """Search patients by multiple criteria."""
        results = self.find_all()
        
        # Filter by status (default to active if not specified)
        status = criteria.get('status', UserStatus.ACTIVE)
        if status:
            results = [p for p in results if p.status == status]
        
        # Filter by name (partial match)
        name = criteria.get('name')
        if name:
            name_lower = name.lower()
            results = [p for p in results if name_lower in p.name.lower()]
        
        # Filter by email (partial match)
        email = criteria.get('email')
        if email:
            email_lower = email.lower()
            results = [p for p in results if email_lower in p.email.lower()]
        
        # Filter by phone (exact match)
        phone = criteria.get('phone')
        if phone:
            results = [p for p in results if p.phone == phone]
        
        # Filter by emergency contact relationship
        emergency_relationship = criteria.get('emergency_contact_relationship')
        if emergency_relationship:
            results = [p for p in results if p.emergency_contact_relationship == emergency_relationship]
        
        # Filter by medical history presence
        has_medical_history = criteria.get('has_medical_history')
        if has_medical_history is not None:
            if has_medical_history:
                results = [p for p in results if p.has_medical_history()]
            else:
                results = [p for p in results if not p.has_medical_history()]
        
        return results
    
    def email_exists(self, email: str, exclude_id: Optional[UUID] = None) -> bool:
        """Check if email exists, optionally excluding a specific patient ID."""
        patient = self.find_by_email(email)
        if not patient:
            return False
        if exclude_id and patient.id == exclude_id:
            return False
        return True
    
    def phone_exists(self, phone: str, exclude_id: Optional[UUID] = None) -> bool:
        """Check if phone exists, optionally excluding a specific patient ID."""
        patient = self.find_by_phone(phone)
        if not patient:
            return False
        if exclude_id and patient.id == exclude_id:
            return False
        return True
    
    def create_with_uniqueness_check(self, patient: Patient) -> Patient:
        """Create patient with email and phone uniqueness check."""
        if self.email_exists(patient.email):
            raise DuplicateError(
                f"Patient with email {patient.email} already exists",
                "Patient",
                "email",
                patient.email
            )
        
        if self.phone_exists(patient.phone):
            raise DuplicateError(
                f"Patient with phone {patient.phone} already exists",
                "Patient",
                "phone",
                patient.phone
            )
        
        return self.create(patient)
    
    def update_with_uniqueness_check(self, patient: Patient) -> Patient:
        """Update patient with email and phone uniqueness check."""
        if self.email_exists(patient.email, exclude_id=patient.id):
            raise DuplicateError(
                f"Patient with email {patient.email} already exists",
                "Patient",
                "email",
                patient.email
            )
        
        if self.phone_exists(patient.phone, exclude_id=patient.id):
            raise DuplicateError(
                f"Patient with phone {patient.phone} already exists",
                "Patient",
                "phone",
                patient.phone
            )
        
        return self.update(patient)
    
    def get_basic_info(self, patient_id: UUID) -> Optional[Dict[str, Any]]:
        """Get basic patient information."""
        patient = self.find_by_id(patient_id)
        if not patient:
            return None
        
        return {
            'id': str(patient.id),
            'name': patient.name,
            'email': patient.email,
            'phone': patient.phone,
            'status': patient.status.value
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get repository statistics."""
        patients = self.find_all()
        active_patients = self.find_active_patients()
        patients_with_history = self.find_with_medical_history()
        
        # Count by status
        status_counts = {}
        for status in UserStatus:
            status_counts[status.value] = len(self.find_by_status(status))
        
        # Count by emergency contact relationship
        relationship_counts = {}
        for patient in active_patients:
            relationship = patient.emergency_contact_relationship
            relationship_counts[relationship] = relationship_counts.get(relationship, 0) + 1
        
        return {
            'total_patients': len(patients),
            'active_patients': len(active_patients),
            'patients_with_medical_history': len(patients_with_history),
            'medical_history_percentage': round(
                (len(patients_with_history) / len(active_patients) * 100) if active_patients else 0, 1
            ),
            'status_distribution': status_counts,
            'emergency_contact_relationships': relationship_counts
        }
    
    def bulk_update_status(self, patient_ids: List[UUID], status: UserStatus, 
                          updated_by: Optional[UUID] = None) -> List[Patient]:
        """Bulk update status for multiple patients."""
        updated_patients = []
        for patient_id in patient_ids:
            patient = self.find_by_id(patient_id)
            if patient:
                patient.status = status
                patient.update_timestamp(updated_by)
                updated_patient = self.update(patient)
                updated_patients.append(updated_patient)
        return updated_patients
    
    def find_patients_by_emergency_contact_criteria(self, name: Optional[str] = None, 
                                                   phone: Optional[str] = None,
                                                   relationship: Optional[str] = None) -> List[Patient]:
        """Find patients by emergency contact criteria."""
        results = []
        for patient in self.find_all():
            match = True
            
            if name and name.lower() not in patient.emergency_contact_name.lower():
                match = False
            
            if phone and patient.emergency_contact_phone != phone:
                match = False
            
            if relationship and patient.emergency_contact_relationship != relationship:
                match = False
            
            if match:
                results.append(patient)
        
        return results