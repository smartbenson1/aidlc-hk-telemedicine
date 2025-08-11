"""
Symptom Description repository implementation for the Appointment Matching Service.
"""

from typing import List

from .base_repository import InMemoryRepository
from ..models.symptom_description import SymptomDescription


class SymptomDescriptionRepository(InMemoryRepository[SymptomDescription]):
    """Repository for managing symptom descriptions."""
    
    def __init__(self):
        super().__init__("SymptomDescription")
    
    def find_by_patient(self, patient_id: str) -> List[SymptomDescription]:
        """Find symptom descriptions by patient ID."""
        return self.find_by_field("patient_id", patient_id)
    
    def find_by_keywords(self, keywords: List[str]) -> List[SymptomDescription]:
        """Find symptom descriptions containing any of the keywords."""
        return self.find_by_predicate(
            lambda desc: any(keyword in desc.parsed_keywords for keyword in keywords)
        )
    
    def find_analyzed(self) -> List[SymptomDescription]:
        """Find symptom descriptions that have been analyzed."""
        return self.find_by_predicate(lambda desc: desc.is_analyzed())
    
    def find_high_confidence(self, threshold: float = 0.7) -> List[SymptomDescription]:
        """Find symptom descriptions with high confidence scores."""
        from decimal import Decimal
        return self.find_by_predicate(
            lambda desc: desc.has_high_confidence(Decimal(str(threshold)))
        )