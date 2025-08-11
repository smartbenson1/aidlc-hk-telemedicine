"""
Doctor Recommendation model class for the Appointment Matching Service.
"""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import List, Optional
import json

from ..utils.helpers import (
    generate_uuid, get_current_utc_datetime, validate_decimal_range
)
from ..utils.exceptions import ValidationError


@dataclass
class DoctorRecommendation:
    """Doctor recommendation component."""
    
    # Identity
    id: str = field(default_factory=generate_uuid)
    symptom_description_id: str = ""
    patient_id: str = ""
    
    # Recommendation Details
    recommended_doctors: List[str] = field(default_factory=list)  # List of doctor UUIDs (max 3)
    match_scores: List[Decimal] = field(default_factory=list)  # Matching confidence per doctor
    available_slots: List[datetime] = field(default_factory=list)  # Earliest available slots
    
    # Algorithm Metadata
    algorithm_version: str = "1.0"
    ranking_factors: str = ""  # JSON string of factors used in ranking
    
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
        """Validate the doctor recommendation data."""
        errors = []
        
        # Validate required fields
        if not self.symptom_description_id:
            errors.append("Symptom description ID is required")
        
        if not self.patient_id:
            errors.append("Patient ID is required")
        
        # Validate recommendation lists consistency
        if len(self.recommended_doctors) != len(self.match_scores):
            errors.append("Recommended doctors and match scores must have same length")
        
        if len(self.recommended_doctors) != len(self.available_slots):
            errors.append("Recommended doctors and available slots must have same length")
        
        # Validate maximum recommendations
        if len(self.recommended_doctors) > 3:
            errors.append("Maximum 3 doctors can be recommended")
        
        # Validate match scores
        for score in self.match_scores:
            if not validate_decimal_range(score, Decimal('0.0'), Decimal('1.0')):
                errors.append("All match scores must be between 0.0 and 1.0")
                break
        
        # Validate doctor IDs format
        for doctor_id in self.recommended_doctors:
            if not isinstance(doctor_id, str) or len(doctor_id) < 1:
                errors.append("Invalid doctor ID format")
                break
        
        if errors:
            raise ValidationError(f"Doctor recommendation validation failed: {'; '.join(errors)}")
        
        return True
    
    def validate_doctor_count(self, doctors: List[str]) -> bool:
        """Validate doctor count is within limit."""
        return len(doctors) <= 3
    
    def validate_match_scores(self, scores: List[Decimal]) -> bool:
        """Validate match scores are within valid range."""
        return all(validate_decimal_range(score, Decimal('0.0'), Decimal('1.0')) 
                  for score in scores)
    
    def validate_available_slots(self, slots: List[datetime]) -> bool:
        """Validate available slots are in the future."""
        current_time = get_current_utc_datetime()
        return all(slot > current_time for slot in slots)
    
    def update_recommendations(self, doctors: List[str], scores: List[Decimal], 
                             slots: List[datetime]) -> None:
        """Update the recommendations."""
        if not self.validate_doctor_count(doctors):
            raise ValidationError("Maximum 3 doctors can be recommended")
        
        if len(doctors) != len(scores) or len(doctors) != len(slots):
            raise ValidationError("Doctors, scores, and slots lists must have same length")
        
        if not self.validate_match_scores(scores):
            raise ValidationError("Invalid match scores")
        
        if not self.validate_available_slots(slots):
            raise ValidationError("All available slots must be in the future")
        
        self.recommended_doctors = doctors
        self.match_scores = scores
        self.available_slots = slots
        self.updated_at = get_current_utc_datetime()
    
    def add_recommendation(self, doctor_id: str, match_score: Decimal, 
                          available_slot: datetime) -> None:
        """Add a single recommendation."""
        if len(self.recommended_doctors) >= 3:
            raise ValidationError("Maximum 3 doctors can be recommended")
        
        if not isinstance(doctor_id, str) or len(doctor_id) != 36:
            raise ValidationError("Invalid doctor ID format")
        
        if not validate_decimal_range(match_score, Decimal('0.0'), Decimal('1.0')):
            raise ValidationError("Match score must be between 0.0 and 1.0")
        
        if available_slot <= get_current_utc_datetime():
            raise ValidationError("Available slot must be in the future")
        
        self.recommended_doctors.append(doctor_id)
        self.match_scores.append(match_score)
        self.available_slots.append(available_slot)
        self.updated_at = get_current_utc_datetime()
    
    def remove_recommendation(self, doctor_id: str) -> bool:
        """Remove a recommendation by doctor ID."""
        try:
            index = self.recommended_doctors.index(doctor_id)
            self.recommended_doctors.pop(index)
            self.match_scores.pop(index)
            self.available_slots.pop(index)
            self.updated_at = get_current_utc_datetime()
            return True
        except ValueError:
            return False
    
    def get_top_recommendation(self) -> Optional[tuple]:
        """Get the top recommendation (doctor_id, score, slot)."""
        if not self.recommended_doctors:
            return None
        
        # Find the index of the highest score
        max_index = 0
        max_score = self.match_scores[0]
        
        for i, score in enumerate(self.match_scores[1:], 1):
            if score > max_score:
                max_score = score
                max_index = i
        
        return (
            self.recommended_doctors[max_index],
            self.match_scores[max_index],
            self.available_slots[max_index]
        )
    
    def get_recommendations_sorted(self) -> List[tuple]:
        """Get all recommendations sorted by match score (highest first)."""
        if not self.recommended_doctors:
            return []
        
        # Create list of tuples and sort by score (descending)
        recommendations = list(zip(
            self.recommended_doctors, 
            self.match_scores, 
            self.available_slots
        ))
        
        return sorted(recommendations, key=lambda x: x[1], reverse=True)
    
    def set_ranking_factors(self, factors: dict) -> None:
        """Set the ranking factors as JSON."""
        try:
            self.ranking_factors = json.dumps(factors)
            self.updated_at = get_current_utc_datetime()
        except (TypeError, ValueError) as e:
            raise ValidationError(f"Invalid ranking factors: {e}")
    
    def get_ranking_factors(self) -> dict:
        """Get the ranking factors as dictionary."""
        if not self.ranking_factors:
            return {}
        
        try:
            return json.loads(self.ranking_factors)
        except (json.JSONDecodeError, TypeError):
            return {}
    
    def has_recommendations(self) -> bool:
        """Check if there are any recommendations."""
        return len(self.recommended_doctors) > 0
    
    def get_recommendation_count(self) -> int:
        """Get the number of recommendations."""
        return len(self.recommended_doctors)
    
    def __str__(self) -> str:
        """String representation of the recommendation."""
        return f"Recommendation for {self.patient_id}: {len(self.recommended_doctors)} doctors"
    
    def __repr__(self) -> str:
        """Detailed representation of the recommendation."""
        return (f"DoctorRecommendation(id='{self.id}', patient_id='{self.patient_id}', "
                f"doctors_count={len(self.recommended_doctors)})")