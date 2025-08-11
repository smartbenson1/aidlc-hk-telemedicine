"""
Symptom Analyzer service with NLP capabilities for the Appointment Matching Service.
"""

import re
import random
from decimal import Decimal
from typing import List, Dict, Set
from datetime import datetime

from ..models.analysis_results import AnalysisResult
from ..utils.helpers import generate_uuid, get_current_utc_datetime, setup_logging, extract_keywords
from ..utils.exceptions import AnalysisError, ValidationError


class SymptomAnalyzer:
    """Service for analyzing symptoms using NLP techniques."""
    
    def __init__(self):
        self.id = generate_uuid()
        self.model_name = "basic_nlp_analyzer"
        self.model_version = "1.0"
        self.confidence_threshold = Decimal('0.7')
        self.max_keywords = 20
        self.min_keyword_length = 3
        self.logger = setup_logging("SymptomAnalyzer")
        
        # Medical terms dictionary (simplified for demo)
        self.medical_terms = {
            'pain', 'ache', 'fever', 'headache', 'nausea', 'vomiting', 'diarrhea',
            'constipation', 'fatigue', 'weakness', 'dizziness', 'shortness', 'breath',
            'cough', 'sore', 'throat', 'runny', 'nose', 'congestion', 'rash', 'itching',
            'swelling', 'inflammation', 'infection', 'bleeding', 'bruising', 'numbness',
            'tingling', 'stiffness', 'cramps', 'spasms', 'chest', 'abdominal', 'back',
            'joint', 'muscle', 'bone', 'skin', 'eye', 'ear', 'dental', 'heart',
            'stomach', 'kidney', 'liver', 'lung', 'brain', 'nerve', 'blood'
        }
        
        # Specialty keywords mapping (simplified)
        self.specialty_keywords = {
            'cardiology': ['heart', 'chest', 'cardiac', 'blood', 'pressure', 'pulse'],
            'dermatology': ['skin', 'rash', 'itching', 'acne', 'mole', 'eczema'],
            'neurology': ['headache', 'dizziness', 'numbness', 'tingling', 'seizure'],
            'gastroenterology': ['stomach', 'nausea', 'vomiting', 'diarrhea', 'constipation'],
            'orthopedics': ['bone', 'joint', 'muscle', 'back', 'knee', 'shoulder'],
            'pulmonology': ['lung', 'cough', 'breath', 'shortness', 'chest'],
            'general': ['fever', 'fatigue', 'weakness', 'pain', 'ache']
        }
        
        self.created_at = get_current_utc_datetime()
        self.updated_at = get_current_utc_datetime()
    
    def analyze_symptoms(self, symptoms_text: str) -> AnalysisResult:
        """Analyze symptoms text using NLP techniques."""
        try:
            self.logger.info(f"Starting symptom analysis for text: {symptoms_text[:50]}...")
            
            if not symptoms_text or not symptoms_text.strip():
                raise AnalysisError("Symptoms text cannot be empty")
            
            # Clean and preprocess text
            processed_text = self._preprocess_text(symptoms_text)
            
            # Extract keywords
            keywords = self.extract_keywords(processed_text)
            
            # Identify medical terms
            medical_terms = self.identify_medical_terms(keywords)
            
            # Calculate confidence score
            confidence = self.calculate_confidence(keywords, processed_text)
            
            # Create analysis result
            result = AnalysisResult(
                keywords=keywords,
                confidence_score=confidence,
                medical_terms=medical_terms,
                processed_text=processed_text,
                analysis_metadata={
                    'model_name': self.model_name,
                    'model_version': self.model_version,
                    'analysis_timestamp': get_current_utc_datetime().isoformat(),
                    'total_keywords': str(len(keywords)),
                    'medical_terms_count': str(len(medical_terms))
                }
            )
            
            self.logger.info(f"Analysis completed with confidence: {confidence}")
            return result
            
        except Exception as e:
            self.logger.error(f"Symptom analysis failed: {e}")
            raise AnalysisError(f"Failed to analyze symptoms: {e}")
    
    def extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text using NLP techniques."""
        if not text:
            return []
        
        # Use the helper function for basic keyword extraction
        keywords = extract_keywords(text, self.min_keyword_length, self.max_keywords)
        
        # Enhanced processing for medical context
        enhanced_keywords = []
        
        # Look for compound medical terms
        text_lower = text.lower()
        compound_terms = [
            'shortness of breath', 'sore throat', 'runny nose', 'chest pain',
            'back pain', 'joint pain', 'muscle pain', 'stomach ache', 'head ache'
        ]
        
        for term in compound_terms:
            if term in text_lower:
                enhanced_keywords.extend(term.split())
        
        # Combine and deduplicate
        all_keywords = list(set(keywords + enhanced_keywords))
        
        # Filter by medical relevance
        medical_keywords = [kw for kw in all_keywords if self._is_medically_relevant(kw)]
        
        return medical_keywords[:self.max_keywords]
    
    def calculate_confidence(self, keywords: List[str], text: str) -> Decimal:
        """Calculate confidence score for the analysis."""
        if not keywords:
            return Decimal('0.0')
        
        # Base confidence from keyword count
        keyword_score = min(len(keywords) / 10.0, 1.0)
        
        # Medical terms bonus
        medical_terms_count = len(self.identify_medical_terms(keywords))
        medical_bonus = min(medical_terms_count / 5.0, 0.3)
        
        # Text length factor
        text_length_factor = min(len(text) / 100.0, 0.2)
        
        # Combine scores
        total_confidence = keyword_score + medical_bonus + text_length_factor
        
        # Add some realistic variation
        variation = random.uniform(-0.1, 0.1)
        total_confidence = max(0.0, min(1.0, total_confidence + variation))
        
        return Decimal(str(round(total_confidence, 2)))
    
    def identify_medical_terms(self, keywords: List[str]) -> List[str]:
        """Identify medical terms from keywords."""
        medical_terms = []
        
        for keyword in keywords:
            if keyword.lower() in self.medical_terms:
                medical_terms.append(keyword)
        
        return medical_terms
    
    def update_model(self, model_name: str, version: str) -> None:
        """Update the NLP model configuration."""
        if not model_name or not version:
            raise ValidationError("Model name and version are required")
        
        self.model_name = model_name
        self.model_version = version
        self.updated_at = get_current_utc_datetime()
        self.logger.info(f"Updated model to {model_name} v{version}")
    
    def update_threshold(self, threshold: Decimal) -> None:
        """Update confidence threshold."""
        if not self.validate_confidence_threshold(threshold):
            raise ValidationError("Confidence threshold must be between 0.0 and 1.0")
        
        self.confidence_threshold = threshold
        self.updated_at = get_current_utc_datetime()
        self.logger.info(f"Updated confidence threshold to {threshold}")
    
    def add_medical_terms(self, terms: List[str]) -> None:
        """Add medical terms to the dictionary."""
        if not terms:
            return
        
        for term in terms:
            if term and isinstance(term, str):
                self.medical_terms.add(term.lower())
        
        self.updated_at = get_current_utc_datetime()
        self.logger.info(f"Added {len(terms)} medical terms")
    
    def update_specialty_keywords(self, specialty_name: str, keywords: List[str]) -> None:
        """Update keywords for a specialty."""
        if not specialty_name or not keywords:
            raise ValidationError("Specialty name and keywords are required")
        
        self.specialty_keywords[specialty_name.lower()] = [kw.lower() for kw in keywords]
        self.updated_at = get_current_utc_datetime()
        self.logger.info(f"Updated keywords for specialty: {specialty_name}")
    
    def validate_confidence_threshold(self, threshold: Decimal) -> bool:
        """Validate confidence threshold."""
        return Decimal('0.0') <= threshold <= Decimal('1.0')
    
    def validate_model_configuration(self, model_name: str, version: str) -> bool:
        """Validate model configuration."""
        return bool(model_name and version and isinstance(model_name, str) and isinstance(version, str))
    
    def validate_keyword_settings(self, max_keywords: int, min_length: int) -> bool:
        """Validate keyword extraction settings."""
        return max_keywords > 0 and min_length > 0 and max_keywords <= 50
    
    def _preprocess_text(self, text: str) -> str:
        """Preprocess text for analysis."""
        # Convert to lowercase
        text = text.lower()
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Remove special characters but keep medical punctuation
        text = re.sub(r'[^\w\s\-\.]', ' ', text)
        
        return text
    
    def _is_medically_relevant(self, keyword: str) -> bool:
        """Check if a keyword is medically relevant."""
        # Check against medical terms
        if keyword.lower() in self.medical_terms:
            return True
        
        # Check against specialty keywords
        for specialty_keywords in self.specialty_keywords.values():
            if keyword.lower() in specialty_keywords:
                return True
        
        # Check for medical-sounding patterns
        medical_patterns = [
            r'.*ache$', r'.*pain$', r'.*itis$', r'.*osis$', r'.*emia$'
        ]
        
        for pattern in medical_patterns:
            if re.match(pattern, keyword.lower()):
                return True
        
        return False