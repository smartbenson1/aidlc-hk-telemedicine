"""
Symptom Description model class for the Appointment Matching Service.
"""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from ..utils.helpers import (
    generate_uuid, get_current_utc_datetime, validate_string_length,
    validate_decimal_range
)
from ..utils.exceptions import ValidationError


@dataclass
class SymptomDescription:
    """Symptom description component."""
    
    # Identity
    id: str = field(default_factory=generate_uuid)
    patient_id: str = ""
    
    # Symptom Information
    symptoms_text: str = ""
    parsed_keywords: List[str] = field(default_factory=list)
    confidence_score: Decimal = field(default_factory=lambda: Decimal('0.0'))
    
    # Analysis Results
    matched_specialties: List[str] = field(default_factory=list)  # List of specialty UUIDs
    analysis_timestamp: Optional[datetime] = None
    
    # System Fields
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
    
    def __post_init__(self):
        """Initialize timestamps if not provided."""
        if self.created_at is None:
            self.created_at = get_current_utc_datetime()
        if self.updated_at is None:
            self.updated_at = get_current_utc_datetime()
    
    def validate(self) -> bool:
        """Validate the symptom description data."""
        errors = []
        
        # Validate required fields
        if not self.patient_id:
            errors.append("Patient ID is required")
        
        if not self.symptoms_text:
            errors.append("Symptoms text is required")
        elif not validate_string_length(self.symptoms_text, 2000, 1):
            errors.append("Symptoms text must be between 1 and 2000 characters")
        
        # Validate confidence score
        if not validate_decimal_range(self.confidence_score, Decimal('0.0'), Decimal('1.0')):
            errors.append("Confidence score must be between 0.0 and 1.0")
        
        if errors:
            raise ValidationError(f"Symptom description validation failed: {'; '.join(errors)}")
        
        return True
    
    def validate_symptoms_text(self, text: str) -> bool:
        """Validate symptoms text."""
        return validate_string_length(text, 2000, 1)
    
    def validate_confidence_score(self, score: Decimal) -> bool:
        """Validate confidence score."""
        return validate_decimal_range(score, Decimal('0.0'), Decimal('1.0'))
    
    def validate_specialties(self, specialties: List[str]) -> bool:
        """Validate specialties list."""
        if not isinstance(specialties, list):
            return False
        
        # Check that all specialties are valid UUIDs (basic check)
        for specialty_id in specialties:
            if not isinstance(specialty_id, str) or len(specialty_id) != 36:
                return False
        
        return True
    
    def update_symptoms_text(self, symptoms_text: str) -> None:
        """Update the symptoms text."""
        if not self.validate_symptoms_text(symptoms_text):
            raise ValidationError("Invalid symptoms text")
        
        self.symptoms_text = symptoms_text
        self.updated_at = get_current_utc_datetime()
        
        # Clear analysis results when symptoms change
        self.parsed_keywords = []
        self.confidence_score = Decimal('0.0')
        self.matched_specialties = []
        self.analysis_timestamp = None
    
    def update_analysis_results(self, keywords: List[str], specialties: List[str], 
                              confidence: Decimal) -> None:
        """Update analysis results."""
        if not isinstance(keywords, list):
            raise ValidationError("Keywords must be a list")
        
        if not self.validate_specialties(specialties):
            raise ValidationError("Invalid specialties list")
        
        if not self.validate_confidence_score(confidence):
            raise ValidationError("Invalid confidence score")
        
        self.parsed_keywords = keywords
        self.matched_specialties = specialties
        self.confidence_score = confidence
        self.analysis_timestamp = get_current_utc_datetime()
        self.updated_at = get_current_utc_datetime()
    
    def add_keyword(self, keyword: str) -> None:
        """Add a keyword to the parsed keywords."""
        if keyword and keyword not in self.parsed_keywords:
            self.parsed_keywords.append(keyword)
            self.updated_at = get_current_utc_datetime()
    
    def remove_keyword(self, keyword: str) -> bool:
        """Remove a keyword from the parsed keywords."""
        if keyword in self.parsed_keywords:
            self.parsed_keywords.remove(keyword)
            self.updated_at = get_current_utc_datetime()
            return True
        return False
    
    def add_specialty(self, specialty_id: str) -> None:
        """Add a specialty to the matched specialties."""
        if (specialty_id and 
            isinstance(specialty_id, str) and 
            len(specialty_id) == 36 and 
            specialty_id not in self.matched_specialties):
            self.matched_specialties.append(specialty_id)
            self.updated_at = get_current_utc_datetime()
    
    def remove_specialty(self, specialty_id: str) -> bool:
        """Remove a specialty from the matched specialties."""
        if specialty_id in self.matched_specialties:
            self.matched_specialties.remove(specialty_id)
            self.updated_at = get_current_utc_datetime()
            return True
        return False
    
    def is_analyzed(self) -> bool:
        """Check if symptoms have been analyzed."""
        return (self.analysis_timestamp is not None and 
                len(self.parsed_keywords) > 0)
    
    def has_high_confidence(self, threshold: Decimal = Decimal('0.7')) -> bool:
        """Check if analysis has high confidence."""
        return self.confidence_score >= threshold
    
    def get_top_keywords(self, limit: int = 10) -> List[str]:
        """Get top keywords (limited by count)."""
        return self.parsed_keywords[:limit]
    
    def __str__(self) -> str:
        """String representation of the symptom description."""
        return f"Symptoms for {self.patient_id}: {self.symptoms_text[:50]}..."
    
    def __repr__(self) -> str:
        """Detailed representation of the symptom description."""
        return (f"SymptomDescription(id='{self.id}', patient_id='{self.patient_id}', "
                f"confidence={self.confidence_score}, keywords_count={len(self.parsed_keywords)})")