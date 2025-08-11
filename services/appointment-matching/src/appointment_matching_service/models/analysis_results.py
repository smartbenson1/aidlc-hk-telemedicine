"""
Analysis result and specialty match data classes for the Appointment Matching Service.
"""

from dataclasses import dataclass, field
from decimal import Decimal
from typing import List, Dict, Optional


@dataclass
class AnalysisResult:
    """Result of symptom analysis."""
    
    keywords: List[str] = field(default_factory=list)
    confidence_score: Decimal = field(default_factory=lambda: Decimal('0.0'))
    medical_terms: List[str] = field(default_factory=list)
    processed_text: str = ""
    analysis_metadata: Dict[str, str] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate the analysis result."""
        if self.confidence_score < Decimal('0.0') or self.confidence_score > Decimal('1.0'):
            raise ValueError("Confidence score must be between 0.0 and 1.0")
    
    def has_high_confidence(self, threshold: Decimal = Decimal('0.7')) -> bool:
        """Check if analysis has high confidence."""
        return self.confidence_score >= threshold
    
    def get_top_keywords(self, limit: int = 10) -> List[str]:
        """Get top keywords limited by count."""
        return self.keywords[:limit]
    
    def get_medical_terms_count(self) -> int:
        """Get count of identified medical terms."""
        return len(self.medical_terms)


@dataclass
class SpecialtyMatch:
    """Result of specialty matching."""
    
    specialty_id: str = ""
    specialty_name: str = ""
    match_score: Decimal = field(default_factory=lambda: Decimal('0.0'))
    exact_matches: int = 0
    fuzzy_matches: int = 0
    matched_keywords: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Validate the specialty match."""
        if self.match_score < Decimal('0.0') or self.match_score > Decimal('1.0'):
            raise ValueError("Match score must be between 0.0 and 1.0")
        
        if self.exact_matches < 0 or self.fuzzy_matches < 0:
            raise ValueError("Match counts cannot be negative")
    
    def get_total_matches(self) -> int:
        """Get total number of matches."""
        return self.exact_matches + self.fuzzy_matches
    
    def has_exact_matches(self) -> bool:
        """Check if there are exact matches."""
        return self.exact_matches > 0
    
    def has_fuzzy_matches(self) -> bool:
        """Check if there are fuzzy matches."""
        return self.fuzzy_matches > 0
    
    def is_strong_match(self, threshold: Decimal = Decimal('0.8')) -> bool:
        """Check if this is a strong match."""
        return self.match_score >= threshold


@dataclass
class DoctorRank:
    """Result of doctor ranking."""
    
    doctor_id: str = ""
    doctor_name: str = ""
    overall_score: Decimal = field(default_factory=lambda: Decimal('0.0'))
    rating_score: Decimal = field(default_factory=lambda: Decimal('0.0'))
    availability_score: Decimal = field(default_factory=lambda: Decimal('0.0'))
    specialty_match_score: Decimal = field(default_factory=lambda: Decimal('0.0'))
    earliest_slot: Optional[str] = None  # ISO datetime string
    
    def __post_init__(self):
        """Validate the doctor rank."""
        scores = [self.overall_score, self.rating_score, self.availability_score, self.specialty_match_score]
        for score in scores:
            if score < Decimal('0.0') or score > Decimal('1.0'):
                raise ValueError("All scores must be between 0.0 and 1.0")
    
    def is_highly_ranked(self, threshold: Decimal = Decimal('0.8')) -> bool:
        """Check if doctor is highly ranked."""
        return self.overall_score >= threshold
    
    def has_early_availability(self) -> bool:
        """Check if doctor has early availability."""
        return self.availability_score >= Decimal('0.7')


@dataclass
class ValidationResult:
    """Result of validation operations."""
    
    is_valid: bool = False
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    validated_data: Optional[Dict] = None
    
    def add_error(self, error: str) -> None:
        """Add an error message."""
        self.errors.append(error)
        self.is_valid = False
    
    def add_warning(self, warning: str) -> None:
        """Add a warning message."""
        self.warnings.append(warning)
    
    def has_errors(self) -> bool:
        """Check if there are validation errors."""
        return len(self.errors) > 0
    
    def has_warnings(self) -> bool:
        """Check if there are validation warnings."""
        return len(self.warnings) > 0
    
    def get_error_summary(self) -> str:
        """Get a summary of all errors."""
        return "; ".join(self.errors)
    
    def get_warning_summary(self) -> str:
        """Get a summary of all warnings."""
        return "; ".join(self.warnings)


@dataclass
class BatchResult:
    """Result of batch operations."""
    
    total_items: int = 0
    successful_items: int = 0
    failed_items: int = 0
    errors: List[str] = field(default_factory=list)
    processing_time_seconds: float = 0.0
    
    def __post_init__(self):
        """Validate batch result."""
        if self.successful_items + self.failed_items != self.total_items:
            raise ValueError("Successful + failed items must equal total items")
    
    def get_success_rate(self) -> Decimal:
        """Get success rate as decimal."""
        if self.total_items == 0:
            return Decimal('0.0')
        return Decimal(str(self.successful_items)) / Decimal(str(self.total_items))
    
    def is_fully_successful(self) -> bool:
        """Check if all items were processed successfully."""
        return self.failed_items == 0 and self.total_items > 0
    
    def has_failures(self) -> bool:
        """Check if there were any failures."""
        return self.failed_items > 0


@dataclass
class CircuitBreakerStatus:
    """Status of circuit breaker."""
    
    state: str = "closed"  # closed, open, half_open
    failure_count: int = 0
    last_failure_time: Optional[str] = None  # ISO datetime string
    next_attempt_time: Optional[str] = None  # ISO datetime string
    
    def is_open(self) -> bool:
        """Check if circuit breaker is open."""
        return self.state == "open"
    
    def is_closed(self) -> bool:
        """Check if circuit breaker is closed."""
        return self.state == "closed"
    
    def is_half_open(self) -> bool:
        """Check if circuit breaker is half open."""
        return self.state == "half_open"